import plotly.graph_objects as go
from ..features import cat_groups_resolver, cum_cat_cnt_bucketized
import polars as pl


def generate_purple_lin_scale(n_points):
    colors = []
    for i in range(n_points):
        t = i / (n_points - 1)

        r1, g1, b1 = int("E8", 16), int("D9", 16), int("FF", 16)
        r2, g2, b2 = int("4B", 16), int("00", 16), int("82", 16)

        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        colors.append(hex_color)

    return colors


def progress_web(
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

    colors = generate_purple_lin_scale(len(stats_vec))

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
        closed_rad = (
            row[f"__cum_cnt_vec__({cat_col})"] + row[f"__cum_cnt_vec__({cat_col})"][:1]
        )
        fig.add_trace(
            go.Scatterpolar(
                mode="lines",
                fill="tonext",
                r=closed_rad,
                fillcolor=colors[idx],
                theta=categories,
                line=dict(color=colors[idx], width=3),
                name=str(row[f"__ts_bucket__({ts_col})"]),
            )
        )

    return fig
