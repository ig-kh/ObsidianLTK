import polars as pl
from typing import List, Union


def cat_groups_resolver(
    df: pl.DataFrame, src_col: str, dst_col: str, groups: List[Union[str, List[str]]]
) -> pl.DataFrame:
    mapping = dict()

    for member in groups:
        if type(member) == list:
            new_val = " & ".join(member)
            for submem in member:
                mapping[submem] = new_val
        else:
            mapping[member] = member

    return (
        df.filter(pl.col(src_col).is_in(mapping.keys()))
        .with_columns(pl.col(src_col).replace(mapping).alias(dst_col))
        .drop(src_col)
    )
