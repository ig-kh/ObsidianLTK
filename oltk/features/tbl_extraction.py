import polars as pl


def cum_cat_cnt_bucketized(
    df: pl.DataFrame, val_col, ts_col, delta, min_ts=None, max_ts=None, cold_start=True
) -> pl.DataFrame:
    if min_ts is None:
        min_ts = df[ts_col].min()
    else:
        min_ts = pl.max_horizontal(min_ts, df[ts_col].min())
    if max_ts is None:
        max_ts = df[ts_col].dt.offset_by(delta).max()
    else:
        max_ts = pl.min_horizontal(max_ts, df[ts_col].max())

    buckets = pl.DataFrame(
        pl.date_range(min_ts, max_ts, delta, eager=True, closed="both").alias(
            f"__ts_bucket__({ts_col})"
        )
    )

    if not cold_start:
        df_filtered = df.with_columns(pl.col(ts_col).fill_null(min_ts))
    else:
        df_filtered = df.filter(pl.col(ts_col) >= min_ts)

    df_filtered = (
        df_filtered.select([ts_col, val_col])
        .filter(pl.col(ts_col) <= max_ts)
        .sort(ts_col)
    )

    sparse_bucketized_instances = df_filtered.join_asof(
        buckets,
        left_on=ts_col,
        right_on=f"__ts_bucket__({ts_col})",
        strategy="forward",
        tolerance=None,
    ).select([f"__ts_bucket__({ts_col})", val_col])

    sparce_bucketized_cnt = (
        sparse_bucketized_instances.group_by([val_col, f"__ts_bucket__({ts_col})"])
        .agg(pl.len().alias(f"__instance_cnt__({val_col})"))
        .sort(f"__ts_bucket__({ts_col})")
    )

    dense_grid = buckets.join(df.select(val_col).unique(subset=val_col), how="cross")

    dense_bucketized_cnt = dense_grid.join(
        sparce_bucketized_cnt, on=[f"__ts_bucket__({ts_col})", val_col], how="left"
    ).with_columns(pl.col(f"__instance_cnt__({val_col})").fill_null(0))

    dense_bucketized_cum_cnt = dense_bucketized_cnt.with_columns(
        pl.col(f"__instance_cnt__({val_col})")
        .cum_sum()
        .over(val_col, order_by=f"__ts_bucket__({ts_col})")
        .alias(f"__cum_cnt__({val_col})")
    )

    return dense_bucketized_cum_cnt.pivot(
        on=val_col,
        index=f"__ts_bucket__({ts_col})",
        values=f"__cum_cnt__({val_col})",
        aggregate_function="sum",
    )
