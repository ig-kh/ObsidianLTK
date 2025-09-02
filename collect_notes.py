import os
import re
import polars as pl
from pathlib import Path

# import statx
import yaml


def parse_md_file(path):
    print(f"Processing file: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"UTF-8 failed, trying utf-8-sig for {path}")
        with open(path, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

    title = Path(path).stem

    raw_text = content

    backlinks = []
    backlink_matches = re.findall(
        r"(?<!\!)(\[\[([^\]\|]+?)(?:\|([^\]]+?))?\]\])", content, re.UNICODE
    )
    for match in backlink_matches:
        node = match[1].strip().split("#")[0]
        alias = match[2].strip() if match[2] else None
        backlinks.append((node, alias))

    md_yaml_props = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if md_yaml_props:
        props = yaml.safe_load(md_yaml_props.group(1))
    else:
        props = dict()

    meta_create_date = None  # TODO

    meta_update_date = os.path.getmtime(path)

    return title, raw_text, backlinks, props, meta_create_date, meta_update_date


if __name__ == "__main__":

    NOTES_PATH = "/mnt/i/obs_vaults/techStackGraph/Nodes"

    directory = Path(NOTES_PATH)
    if not directory.exists():
        print(f"Directory {directory} does not exist.")

    data = []
    md_files = list(directory.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {directory}")

    for filepath in md_files:
        note_data = parse_md_file(filepath)
        if note_data:
            data.append(note_data)

    if not data:
        print("No data parsed from files.")

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

    print(edges_df, nodes_df)
