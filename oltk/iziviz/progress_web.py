import plotly.graph_objects as go
from ..features import cat_groups_resolver, cum_cat_cnt_bucketized
import polars as pl

def progress_web(df, cat_col, ts_col, ts_delta, groups, min_ts=None, max_ts=None, cold_start=True):
    grouped_data = cat_groups_resolver(df, cat_col, f"__grouped({cat_col})__", groups)
    stat = cum_cat_cnt_bucketized(grouped_data, f"__grouped({cat_col})__", ts_col, ts_delta, min_ts, max_ts, cold_start)
    categories = stat.columns[1:]

    stats_vec = stat.select(pl.col("__ts_bucket__"), pl.concat_list(categories).alias("__cum_cnt_vec__"))

    fig = go.Figure()

    for row in stats_vec.iter_rows(named=True):
        fig.add_trace(go.Scatterpolar(
            r=row["__cum_cnt_vec__"],
            theta=categories,
            name=str(row["__ts_bucket__"])
        ))
        
    return fig
