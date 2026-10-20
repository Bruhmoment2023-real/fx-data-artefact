"""Step 1: minute-of-day sufficient statistics from the raw histdata M1 zips.

Usage:  python build_minute_stats.py EURUSD USDJPY ...
Output: results/minute_stats/<PAIR>.parquet with one row per
        (year, dst_state, weekday, label minute) holding n, sum and sum of squares
        of the one-minute bid-to-bid log return (bp), sum |return|, and sum of bar range (bp).
Streaming: one pair-year in memory at a time.
"""
import sys, time
from pathlib import Path
import numpy as np, pandas as pd
import fxio

OUT = Path(__file__).resolve().parents[1] / "results" / "minute_stats"
OUT.mkdir(parents=True, exist_ok=True)

def agg_year(df):
    df = fxio.add_features(df)
    df["r2"] = df["ret_cc"] ** 2
    df["ra"] = df["ret_cc"].abs()
    df["oc2"] = df["ret_oc"] ** 2
    g = df.groupby(["dst", "dow", "minute"], sort=True)
    a = g.agg(n_bars=("c", "size"), n=("ret_cc", "count"), s=("ret_cc", "sum"), ss=("r2", "sum"),
              sabs=("ra", "sum"), s_oc=("ret_oc", "sum"), ss_oc=("oc2", "sum"), s_rng=("range_bp", "sum"))
    return a.reset_index()

if __name__ == "__main__":
    for pair in sys.argv[1:]:
        t0 = time.time(); parts = []
        years = sorted({y for y, _ in fxio.zips_for(pair)})
        for y in years:
            df = fxio.read_pair_year(pair, y)
            a = agg_year(df); a.insert(0, "year", y); parts.append(a)
        res = pd.concat(parts, ignore_index=True); res.insert(0, "pair", pair)
        res.to_parquet(OUT / f"{pair}.parquet", index=False)
        print(pair, "years", years[0], years[-1], "rows", len(res), "bars", int(res.n_bars.sum()), f"{time.time()-t0:.0f}s", flush=True)
