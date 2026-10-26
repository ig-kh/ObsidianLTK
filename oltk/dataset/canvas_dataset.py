import json

import polars as pl

from .vault_dataset import VaultDataset
from ..utils.fs import abs_under_root, norm_ref, to_ref, read_md
from ..features import extract_backlinks

class CanvasDataset:
    def __init__(
        self,
        path,
        root="auto",
        allow_implicit_spatial_inclusions: bool = True,
        allow_note_content_references: bool = True,
    ):
        self.root = root

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw_v = data.get("nodes", []) or []
        raw_e = data.get("edges", []) or []

        self.graph = VaultDataset(root)
        self.graph.construct()
        v_index = self.graph.get_v_index()
        reachable_refs = set(v_index["note_ref"].to_list())

        normalized = [self._normalize_node(n) for n in raw_v]
        _nodes_df = pl.DataFrame(
            normalized,
            schema_overrides={
                "type": pl.String,
                "content": pl.String,
                "coords": pl.List(pl.List(pl.Int64)),
                "src_id": pl.String,
                "ref": pl.String,
            },
            strict=False,
        )
        for col, dtype in (
            ("type", pl.String),
            ("content", pl.String),
            ("coords", pl.List(pl.List(pl.Int64))),
            ("src_id", pl.String),
            ("ref", pl.String),
        ):
            if col not in _nodes_df.columns:
                _nodes_df = _nodes_df.with_columns(
                    pl.lit(None).cast(dtype).alias(col)
                )

        _nodes_df_clamped = self._clamp_nodes(_nodes_df)
        self.src_mapping = (
            _nodes_df_clamped.select("src_id", "id")
            .explode("src_id")
            .drop_nulls("src_id")
        )

        self.nodes = self._build_nodes(_nodes_df, _nodes_df_clamped, v_index)

        edge_parts: list[pl.DataFrame] = []

        if allow_note_content_references:
            part = self._edges_text_references(_nodes_df, self.src_mapping)
            if part is not None:
                edge_parts.append(part)

        if raw_e:
            part = self._edges_explicit(raw_e, self.src_mapping)
            if part is not None:
                edge_parts.append(part)

        if allow_note_content_references:
            part = self._edges_graph_refs(
                _nodes_df_clamped, self.src_mapping, v_index
            )
            if part is not None:
                edge_parts.append(part)

        if allow_implicit_spatial_inclusions:
            part = self._edges_containment(_nodes_df_clamped)
            if part is not None:
                edge_parts.append(part)

        self.edges = self._assemble_edges(edge_parts)

    def _clamp_nodes(self, _nodes_df: pl.DataFrame) -> pl.DataFrame:
        """Merge attachment nodes that point to the same vault note."""
        attachments = _nodes_df.filter(pl.col("type") == "attachment")
        if attachments.height:
            unique_attaches = attachments.group_by("ref").agg(
                pl.col("content").first().alias("content"),
                pl.lit("attachment").alias("type"),
                pl.col("coords").alias("loc"),
                pl.col("src_id").alias("src_id"),
            )
        else:
            unique_attaches = pl.DataFrame(
                schema={
                    "ref": pl.String,
                    "content": pl.String,
                    "type": pl.String,
                    "loc": pl.List(pl.List(pl.List(pl.Int64))),
                    "src_id": pl.List(pl.String),
                }
            )

        others_df = _nodes_df.filter(pl.col("type") != "attachment")
        if others_df.height:
            other_nodes = others_df.select(
                pl.lit(None).cast(pl.String).alias("ref"),
                "content",
                "type",
                pl.col("coords")
                .map_elements(
                    lambda x: [x],
                    return_dtype=pl.List(pl.List(pl.List(pl.Int64))),
                )
                .alias("loc"),
                pl.concat_list(pl.col("src_id")).alias("src_id"),
            )
        else:
            other_nodes = pl.DataFrame(
                schema={
                    "ref": pl.String,
                    "content": pl.String,
                    "type": pl.String,
                    "loc": pl.List(pl.List(pl.List(pl.Int64))),
                    "src_id": pl.List(pl.String),
                }
            )

        return pl.concat(
            [
                unique_attaches.select("ref", "content", "type", "loc", "src_id"),
                other_nodes.select("ref", "content", "type", "loc", "src_id"),
            ],
            how="vertical_relaxed",
        ).with_row_index("id")

    def _build_nodes(
        self,
        _nodes_df: pl.DataFrame,
        _nodes_df_clamped: pl.DataFrame,
        v_index: pl.DataFrame,
    ) -> pl.DataFrame:
        clamped_ref = (
            _nodes_df.select("src_id", "ref")
            .join(self.src_mapping, on="src_id", how="inner")
            .group_by("id")
            .agg(pl.col("ref").first())
        )
        readable_ids = clamped_ref.filter(
            pl.col("ref").is_in(list(set(v_index["note_ref"].to_list())))
        ).select("id")
        readable_mask = (pl.col("type") == "attachment") & pl.col("id").is_in(
            readable_ids["id"]
        )

        # ref -> (note_name, absolute note_path) straight from the vault index
        ref_to_meta = v_index.select(
            pl.col("note_ref").alias("ref"),
            pl.col("note_name").alias("note_name"),
            pl.col("note_path").alias("note_path"),
        )

        readables_df = (
            _nodes_df_clamped.join(clamped_ref, on="id", how="left")
            .join(ref_to_meta, on="ref", how="left")
            .filter(readable_mask)
            .select(
                "id",
                pl.lit("note").alias("type"),
                # content = "<filename>\n\n<full text>"
                (
                    pl.col("note_name").cast(pl.String)
                    + pl.lit("\n\n")
                    + pl.col("note_path")
                    .map_elements(
                        lambda p: read_md(p) if p else "",
                        return_dtype=pl.String,
                    )
                ).alias("content"),
                "loc",
            )
        )
        other_df = _nodes_df_clamped.filter(~readable_mask).select(
            "id", "type", "content", "loc"
        )

        return (
            pl.concat(
                [
                    readables_df.select("id", "type", "content", "loc"),
                    other_df.select("id", "type", "content", "loc"),
                ],
                how="vertical_relaxed",
            )
            .sort("id")
            .select(
                "id",
                "type",
                "content",
                pl.col("loc").cast(pl.List(pl.Array(pl.Int128, shape=(2, 2)))),
            )
        )

    def _edges_text_references(
        self, _nodes_df: pl.DataFrame, src_mapping: pl.DataFrame
    ) -> pl.DataFrame | None:
        """Wikilinks inside canvas `text` nodes → attachment nodes."""
        if not _nodes_df.height:
            return None

        notes_with_src = _nodes_df.filter(pl.col("type") == "note").join(
            src_mapping, on="src_id", how="left"
        )
        if not notes_with_src.height:
            return None

        lhs = (
            notes_with_src.with_columns(
                pl.col("content")
                .map_elements(
                    lambda c: extract_backlinks(c) if c else [],
                    return_dtype=pl.List(pl.List(pl.String)),
                )
                .alias("link")
            )
            .explode("link")
            .drop_nulls("link")
            .select(
                pl.col("id").alias("from_id"),
                pl.lit(None).cast(pl.String).alias("from_side"),
                pl.col("link").list.get(0).alias("link_target"),
                pl.col("link").list.get(2).alias("label"),
                pl.lit("references").alias("type"),
                pl.lit(None).cast(pl.String).alias("to_side"),
            )
            .drop_nulls("link_target")
            .with_columns(
                pl.col("link_target")
                .map_elements(norm_ref, return_dtype=pl.String)
                .alias("link_target")
            )
        )
        rhs = (
            _nodes_df.filter(pl.col("type") == "attachment")
            .join(src_mapping, on="src_id", how="left")
            .select(
                pl.col("ref").alias("link_target"),
                pl.col("id").alias("to_id"),
            )
            .drop_nulls(["link_target", "to_id"])
            .unique()
        )
        if not lhs.height or not rhs.height:
            return None
        return lhs.join(rhs, on="link_target", how="inner").select(
            "from_id", "from_side", "to_id", "to_side", "type", "label"
        )

    def _edges_explicit(
        self, raw_e: list[dict], src_mapping: pl.DataFrame
    ) -> pl.DataFrame | None:
        """Edges declared in the .canvas `edges` array."""
        raw_e_df = pl.DataFrame(
            [
                {
                    "id": e.get("id"),
                    "fromNode": e.get("fromNode"),
                    "toNode": e.get("toNode"),
                    "fromSide": e.get("fromSide"),
                    "toSide": e.get("toSide"),
                    "label": e.get("label", ""),
                }
                for e in raw_e
            ],
            schema_overrides={
                "id": pl.String,
                "fromNode": pl.String,
                "toNode": pl.String,
                "fromSide": pl.String,
                "toSide": pl.String,
                "label": pl.String,
            },
            strict=False,
        )
        result = (
            raw_e_df.join(
                src_mapping.select(
                    pl.col("src_id").alias("fromNode"),
                    pl.col("id").alias("from_id"),
                ),
                on="fromNode",
                how="inner",
            )
            .join(
                src_mapping.select(
                    pl.col("src_id").alias("toNode"),
                    pl.col("id").alias("to_id"),
                ),
                on="toNode",
                how="inner",
            )
            .select(
                "from_id",
                pl.col("fromSide").alias("from_side"),
                "to_id",
                pl.col("toSide").alias("to_side"),
                pl.lit("is_connected_to").alias("type"),
                pl.col("label").fill_null(""),
            )
        )
        return result if result.height else None

    def _edges_graph_refs(
        self,
        _nodes_df_clamped: pl.DataFrame,
        src_mapping: pl.DataFrame,
        v_index: pl.DataFrame,
    ) -> pl.DataFrame | None:
        """References resolved through the vault graph between canvas notes."""
        if not _nodes_df_clamped.height or not v_index.height:
            return None

        attachments = _nodes_df_clamped.filter(pl.col("type") == "attachment")
        if not attachments.height:
            return None

        graph2canvas = (
            attachments.explode("src_id")
            .drop_nulls(["src_id", "ref"])
            .join(src_mapping, on="src_id", how="inner")
            .select(
                pl.col("ref").alias("note_ref"),
                pl.col("id").alias("canvas_node_id"),
            )
            .join(v_index.select("note_id", "note_ref"), on="note_ref", how="inner")
            .select(
                pl.col("note_id").alias("graph_node_id"),
                "canvas_node_id",
            )
        )
        if not graph2canvas.height:
            return None

        result = (
            self.graph.get_e()
            .join(
                graph2canvas.select(
                    pl.col("graph_node_id").alias("from_id"),
                    pl.col("canvas_node_id").alias("from_canvas_id"),
                ),
                on="from_id",
                how="inner",
            )
            .join(
                graph2canvas.select(
                    pl.col("graph_node_id").alias("to_id"),
                    pl.col("canvas_node_id").alias("to_canvas_id"),
                ),
                on="to_id",
                how="inner",
            )
            .select(
                pl.col("from_canvas_id").alias("from_id"),
                pl.lit(None).cast(pl.String).alias("from_side"),
                pl.col("to_canvas_id").alias("to_id"),
                pl.lit(None).cast(pl.String).alias("to_side"),
                pl.lit("references").alias("type"),
                pl.col("alias").cast(pl.String).alias("label"),
            )
        )
        return result if result.height else None

    def _edges_containment(
        self, _nodes_df_clamped: pl.DataFrame
    ) -> pl.DataFrame | None:
        """Implicit spatial inclusions: groups fully containing other nodes."""
        if not _nodes_df_clamped.height:
            return None

        boxes = (
            _nodes_df_clamped.with_columns(
                pl.col("loc")
                .list.eval(pl.element().list.get(0).list.get(0))
                .list.min()
                .alias("x0"),
                pl.col("loc")
                .list.eval(pl.element().list.get(0).list.get(1))
                .list.max()
                .alias("x1"),
                pl.col("loc")
                .list.eval(pl.element().list.get(1).list.get(0))
                .list.min()
                .alias("y0"),
                pl.col("loc")
                .list.eval(pl.element().list.get(1).list.get(1))
                .list.max()
                .alias("y1"),
            )
            .drop_nulls(["x0", "x1", "y0", "y1"])
            .select("id", "type", "x0", "x1", "y0", "y1")
        )

        g = boxes.filter(pl.col("type") == "group").rename(
            {"id": "gid", "x0": "gx0", "x1": "gx1", "y0": "gy0", "y1": "gy1"}
        )
        n = boxes.filter(pl.col("type") != "group").rename(
            {"id": "nid", "x0": "nx0", "x1": "nx1", "y0": "ny0", "y1": "ny1"}
        )
        if not g.height or not n.height:
            return None

        result = (
            g.join(n, how="cross")
            .filter(
                (pl.col("nx0") >= pl.col("gx0"))
                & (pl.col("nx1") <= pl.col("gx1"))
                & (pl.col("ny0") >= pl.col("gy0"))
                & (pl.col("ny1") <= pl.col("gy1"))
            )
            .select(
                pl.col("nid").alias("from_id"),
                pl.lit(None).cast(pl.String).alias("from_side"),
                pl.col("gid").alias("to_id"),
                pl.lit(None).cast(pl.String).alias("to_side"),
                pl.lit("is_contained_in").alias("type"),
                pl.lit("").alias("label"),
            )
        )
        return result if result.height else None

    @staticmethod
    def _assemble_edges(parts: list[pl.DataFrame]) -> pl.DataFrame:
        schema = {
            "from_id": pl.UInt32,
            "from_side": pl.String,
            "to_id": pl.UInt32,
            "to_side": pl.String,
            "type": pl.String,
            "label": pl.String,
        }
        if not parts:
            return pl.DataFrame(schema={"id": pl.UInt32, **schema})

        return (
            pl.concat(
                [p.select(list(schema.keys())).cast(schema) for p in parts],
                how="vertical_relaxed",
            )
            .unique()
            .with_row_index("id")
        )

    def _normalize_node(self, node_dict):
        typ = node_dict.get("type")
        x = node_dict.get("x", 0)
        y = node_dict.get("y", 0)

        default_w = 250 if typ == "text" else 0
        default_h = 60 if typ == "text" else 0
        w = node_dict.get("width", default_w)
        h = node_dict.get("height", default_h)

        coords = [[int(x), int(x + w)], [int(y), int(y + h)]]

        content = ""
        intermediate_type = None
        ref = None

        if typ == "text":
            content = node_dict.get("text", "") or ""
            intermediate_type = "note"
        elif typ == "file":
            file_rel = node_dict.get("file", "")
            abs_file = abs_under_root(self.root, file_rel)
            content = abs_file
            intermediate_type = "attachment"
            if abs_file.lower().endswith(".md"):
                ref = to_ref(self.root, abs_file)
        elif typ == "group":
            content = node_dict.get("label", "") or ""
            intermediate_type = "group"
        else:
            intermediate_type = "unknown"

        return {
            "type": intermediate_type,
            "content": content,
            "coords": coords,
            "src_id": node_dict.get("id"),
            "ref": ref,
        }