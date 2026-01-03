from ..utils.fs import read_md, get_all_by_extension
from ..features import extract_backlinks
import polars as pl
import os
from copy import deepcopy
from networkx import DiGraph

class VaultDataset:
    def __init__(self, root):
        self.root = root

    def construct(self):
        note_paths = get_all_by_extension(self.root, "md")

        self._note_index = pl.DataFrame({"note_rel_path": note_paths}).with_row_index(
            name="note_id"
        )

        self._note_index = self._note_index.with_columns(
            pl.col("note_rel_path")
            .str.replace_all(".md", "", literal=True)
            .alias("note_ref")
        )

        self._note_index = self._note_index.with_columns(
            pl.col("note_rel_path")
            .map_elements(lambda x: os.path.join(self.root, x))
            .alias("note_path")
        ).drop("note_rel_path")

        self._note_index = self._note_index.with_columns(
            pl.col("note_ref")
            .map_elements(lambda x: x.split("/")[-1])
            .alias("note_name")
        )

        _edges_left = (
            self._note_index.select(
                pl.col("note_id").alias("from_id"), pl.col("note_path")
            )
            .with_columns(
                pl.col("note_path")
                .map_elements(
                    lambda x: extract_backlinks(read_md(x)),
                    return_dtype=pl.List(pl.List(str)),
                )
                .alias("links")
            )
            .drop("note_path")
            .explode("links")
        )

        _edges_left = _edges_left.with_columns(
            pl.col("links").list.get(0).alias("link_handler")
        )

        _edges_right_byname = self._note_index.select(
            pl.col("note_id").alias("to_id_from_name"),
            pl.col("note_name").alias("link_handler"),
        )
        _edges_right_byref = self._note_index.select(
            pl.col("note_id").alias("to_id_from_ref"),
            pl.col("note_ref").alias("link_handler"),
        )

        self._edges = _edges_left.join(_edges_right_byname, "link_handler", "left")
        self._edges = self._edges.join(_edges_right_byref, "link_handler", "left")
        self._edges = self._edges.with_columns(
            pl.coalesce(pl.col("to_id_from_name"), pl.col("to_id_from_ref")).alias(
                "to_id"
            )
        )
        self._edges = self._edges.select(
            "from_id",
            "to_id",
            pl.col("links").list.get(1).alias("heading"),
            pl.col("links").list.get(2).alias("alias"),
        )
        self._edges = self._edges.drop_nulls("to_id").drop_nulls("from_id")

        self._vertixes = None

    def get_e(self):
        return deepcopy(self._edges)

    def get_v_index(self):
        return deepcopy(self._note_index)

    def get_v(self):
        if self._vertixes is None:
            self._vertixes = self._note_index.select(
                pl.col("note_id").alias("id"),
                pl.col("note_name").alias("title"),
                pl.col("note_path"),
            )
            self._vertixes = self._vertixes.with_columns(
                pl.col("note_path").map_elements(read_md).alias("text")
            ).drop("note_path")
        return deepcopy(self._vertixes)
    
    # def to_nx(self):
        