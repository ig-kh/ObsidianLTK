import os
import polars as pl
from pathlib import Path
from argparse import ArgumentParser

from utils.obsidian_parsing import extract_backlinks, extract_header_props
from utils.fs import list_shallow_dir, read_md

def parse_md_file(path):
    print(f"Processing file: {path}")

    content = read_md(path)
    title = Path(path).stem

    raw_text = content
    backlinks = extract_backlinks(content)
    props = extract_header_props(content)

    meta_create_date = None  # TODO
    meta_update_date = os.path.getmtime(path)

    return title, raw_text, backlinks, props, meta_create_date, meta_update_date


def get_ve_datasets(data):
    md_df = pl.DataFrame(
        {
            "title": [item[0] for item in data],
            "text": [item[1] for item in data],
            "backlinks": [item[2] for item in data],
            "tags": [item[3].get("tags", None) for item in data],
            "explicit_date": [item[3].get("date", None) for item in data],
            # "created_at": [item[4] for item in data], # TODO
            "meta_date": [item[5] for item in data],
        }
    ).with_row_index("node_id")

    nodes_maping = md_df.select(["node_id", "title", "backlinks"]).explode("backlinks")
    nodes_maping = nodes_maping.with_columns(
        pl.col("backlinks").list.get(0).alias("to_node"),
        pl.col("backlinks").list.get(1).alias("alias"),
    ).drop(["backlinks"])

    nodes_mapping_left = nodes_maping.select(
        pl.col("node_id").alias("from_node_id"),
        pl.col("to_node").alias("title"),
        pl.col("alias"),
    )
    nodes_mapping_right = nodes_maping.select(
        pl.col("node_id").alias("to_node_id"), pl.col("title")
    )

    edges_df = (
        nodes_mapping_left.join(nodes_mapping_right, how="inner", on="title")
        .drop("title")
        .with_row_index("edge_id")
    )

    nodes_df = md_df.select(
        [
            "node_id",
            "title",
            "text",
            "tags",
            pl.coalesce(["explicit_date", pl.from_epoch("meta_date").dt.date()]).alias(
                "date"
            ),
        ]
    )

    return nodes_df, edges_df

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--notes_src_dir")
    parser.add_argument("--notes_df_dst")
    parser.add_argument("--links_df_dst")
    args = parser.parse_args()

    directory = Path(args.notes_src_dir)
    md_files = list_shallow_dir(directory)

    md_data = []
    for filepath in md_files:
        note_data = parse_md_file(filepath)
        if note_data:
            md_data.append(note_data)
    
    v_df, e_df = get_ve_datasets(md_data)

    if args.notes_df_dst:
        v_df.write_parquet(args.notes_df_dst)

    if args.links_df_dst:
        e_df.write_parquet(args.links_df_dst)