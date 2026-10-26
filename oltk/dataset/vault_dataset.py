import os
from copy import deepcopy

import polars as pl

from ..features import extract_backlinks
from ..utils.fs import get_all_by_extension, read_md, norm_ref, strip_md_suffix


class VaultDataset:
    def __init__(self, root):
        self.root = root
        self._note_index = None
        self._edges = None
        self._vertixes = None

    @staticmethod
    def from_index(vault_index, custom_root=""):
        instance = VaultDataset(custom_root)
        instance._note_index = vault_index
        return instance

    def __add__(self, other):
        if not isinstance(other, VaultDataset):
            return NotImplemented

        cols = ["note_ref", "note_path", "note_name"]
        joint_index = pl.concat(
            [self.get_v_index().select(cols), other.get_v_index().select(cols)]
        ).with_row_index(name="note_id")

        dataset_sum = VaultDataset.from_index(
            joint_index, f"{self.root}+{other.root}"
        )
        dataset_sum.construct()
        return dataset_sum

    def _build_note_index(self, note_paths):
        return (
            pl.DataFrame({"note_rel_path": note_paths})
            .with_row_index(name="note_id")
            .with_columns(
                pl.col("note_rel_path")
                .str.replace_all("\\", "/", literal=True)
                .map_elements(strip_md_suffix, return_dtype=pl.String)
                .alias("note_ref"),
                pl.col("note_rel_path")
                .map_elements(
                    lambda x: os.path.join(self.root, x),
                    return_dtype=pl.String,
                )
                .alias("note_path"),
            )
            .with_columns(
                pl.col("note_ref")
                .str.split("/")
                .list.last()
                .alias("note_name"),
            )
            .with_columns(
                pl.col("note_name").str.to_lowercase().alias("note_name_lc"),
                pl.col("note_ref").str.to_lowercase().alias("note_ref_lc"),
            )
        )

    def _ensure_index_columns(self):
        """Add derived columns to an externally supplied `_note_index`."""
        if "note_name_lc" in self._note_index.columns:
            return
        self._note_index = (
            self._note_index.with_columns(
                pl.col("note_ref")
                .str.replace_all("\\", "/", literal=True)
                .map_elements(strip_md_suffix, return_dtype=pl.String)
                .alias("note_ref"),
            )
            .with_columns(
                pl.col("note_ref")
                .str.split("/")
                .list.last()
                .alias("note_name"),
            )
            .with_columns(
                pl.col("note_name").str.to_lowercase().alias("note_name_lc"),
                pl.col("note_ref").str.to_lowercase().alias("note_ref_lc"),
            )
        )

    def construct(self):

        if self._note_index is None:
            self._note_index = self._build_note_index(
                get_all_by_extension(self.root, "md")
            )
        else:
            self._ensure_index_columns()


        def _read_and_extract(path: str):
            content = read_md(path)
            try:
                with open(path, "rb") as f:
                    f.read(0)
            except Exception as e:
                print(f"Error reading {path}: {f}")
            return extract_backlinks(content) if content else []

        _edges_left = (
            self._note_index.select(
                pl.col("note_id").alias("from_id"), pl.col("note_path")
            )
            .with_columns(
                pl.col("note_path")
                .map_elements(
                    _read_and_extract,
                    return_dtype=pl.List(pl.List(pl.String)),
                )
                .alias("links")
            )
            .drop("note_path")
            .explode("links")
            .with_columns(
                pl.col("links").list.get(0).alias("link_handler"),
                pl.col("links").list.get(1).alias("heading"),
                pl.col("links").list.get(2).alias("alias"),
            )
            .drop("links")
            .with_columns(
                pl.col("link_handler").fill_null("").alias("link_handler_raw"),
                pl.col("link_handler")
                .fill_null("")
                .map_elements(norm_ref, return_dtype=pl.String)
                .str.to_lowercase()
                .alias("link_handler_lc"),
            )
            .with_columns(
                pl.when(pl.col("link_handler_raw") == "")
                .then(pl.col("from_id"))
                .otherwise(None)
                .cast(pl.Int64)
                .alias("to_id_self")
            )
        )

        unique_names = (
            self._note_index.group_by("note_name_lc")
            .agg(pl.len().alias("cnt"))
            .filter(pl.col("cnt") == 1)
            .select("note_name_lc")
        )
        _edges_right_byname = (
            self._note_index.join(unique_names, on="note_name_lc").select(
                pl.col("note_id").alias("to_id_from_name"),
                pl.col("note_name_lc").alias("link_handler_lc"),
            )
        )

        _edges_right_byref = self._note_index.select(
            pl.col("note_id").alias("to_id_from_ref"),
            pl.col("note_ref_lc").alias("link_handler_lc"),
        )

        self._edges = (
            _edges_left.join(_edges_right_byname, on="link_handler_lc", how="left")
            .join(_edges_right_byref, on="link_handler_lc", how="left")
            .with_columns(
                pl.coalesce(
                    pl.col("to_id_self"),
                    pl.col("to_id_from_name"),
                    pl.col("to_id_from_ref"),
                ).alias("to_id")
            )
            .select("from_id", "to_id", "heading", "alias")
            .drop_nulls(["to_id", "from_id"])
            .unique()
        )

        self._vertixes = None

    def get_e(self):
        return deepcopy(self._edges)

    def get_v_index(self):
        return deepcopy(self._note_index)

    def get_v(self):
        if self._vertixes is None:
            self._vertixes = (
                self._note_index.select(
                    pl.col("note_id").alias("id"),
                    pl.col("note_name").alias("title"),
                    pl.col("note_path"),
                )
                .with_columns(
                    pl.col("note_path")
                    .map_elements(read_md, return_dtype=pl.String)
                    .alias("text")
                )
                .drop("note_path")
            )
        return deepcopy(self._vertixes)