import plotly.graph_objects as go
from ..features import cat_groups_resolver, cum_cat_cnt_bucketized
import polars as pl
from ..utils.plotting import generate_purple_with_fade_lin_scale
import numpy as np


def focus_chladni(
    df, cat_col, ts_col, ts_delta, groups, min_ts=None, max_ts=None, cold_start=True
):
    grouped_data = cat_groups_resolver(df, cat_col, f"__grouped({cat_col})__", groups)
    stat = cum_cat_cnt_bucketized(
        grouped_data,
        f"__grouped({cat_col})__",
        ts_col,
        ts_delta,
        min_ts,
        max_ts,
        cold_start,
    )
    categories = stat.columns[1:] + stat.columns[1:2]
    stats_vec = stat.select(
        pl.col(f"__ts_bucket__({ts_col})"),
        pl.concat_list(categories).alias(f"__cum_cnt_vec__({cat_col})"),
    )

    colors = generate_purple_with_fade_lin_scale(len(stats_vec))

    fig = go.Figure()

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                showticklabels=False,
                tick0=0,
            ),
            angularaxis=dict(
                layer="below traces",
            ),
        )
    )

    for idx, row in enumerate(stats_vec.iter_rows(named=True)):
        blob_stats = np.array(row[f"__cum_cnt_vec__({cat_col})"])
        blob_stats = blob_stats / np.linalg.norm(blob_stats)
        closed_rad = blob_stats + blob_stats[:1]
        fig.add_trace(
            go.Scatterpolar(
                mode="lines",
                fill=None,
                r=closed_rad,
                theta=categories,
                line=dict(color=colors[idx], width=3, shape="spline"),
                name=str(row[f"__ts_bucket__({ts_col})"]),
            )
        )

    return fig
