import polars as pl

def _cum_cat_cnt_by_ts_with_delta(df:pl.DataFrame, val_col, ts_col, delta, min_ts=None, max_ts=None, cold_start=True):
    if min_ts is None:
        min_ts = df[ts_col].min()
    else:
        min_ts = pl.max_horizontal(min_ts, df[ts_col].min())
    if max_ts is None:
        max_ts = df[ts_col].max()
    else:
        max_ts = pl.min_horizontal(max_ts, df[ts_col].max())

    obs_range = pl.DataFrame(pl.date_range(min_ts, max_ts, delta, eager=True, closed="both").alias("__ts_bucket__"))

    if not cold_start:
        df_filtered = df.with_columns(pl.col(ts_col).fill_null(min_ts))
    else:
        df_filtered = df.filter(pl.col(ts_col) >= min_ts)
        
    df_filtered = df_filtered.select([ts_col, val_col]).filter(pl.col(ts_col) <= max_ts)

    dense_count_before_buckets = df_filtered.group_by([val_col, ts_col]).agg(pl.len().alias("__instance_cnt__")).sort(ts_col)
    

    bucketized_count = dense_count_before_buckets.join_asof(
            obs_range,
            left_on=ts_col,
            right_on="__ts_bucket__",
            strategy="forward",
            tolerance=None
        ).drop(ts_col)

    grid = obs_range.join(df.select(val_col).unique(subset=val_col), how="cross")

    sparse_count_bucketized = grid.join(bucketized_count, on=["__ts_bucket__", val_col], how="left").with_columns(pl.col("__instance_cnt__").fill_null(0))
    
    sparse_cum_count_bucketized = sparse_count_bucketized.with_columns(
        pl.col("__instance_cnt__")
        .cum_sum()
        .over(val_col, order_by="__ts_bucket__")
        .alias("__cum_cnt__")
    ).drop("__instance_cnt__")
    
    return sparse_cum_count_bucketized.pivot(
        on = val_col,
        index="__ts_bucket__",
        values="__cum_cnt__",
        aggregate_function="sum"
    )