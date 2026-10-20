"""Step 2: per-day tables on three clocks, streamed one pair-year at a time.

Usage:  python build_daily.py EURUSD USDJPY ...

Return definition (used everywhere downstream):
    r_t = 1e4 * ln(close_t / close_{t-1})   bid-to-bid, in basis points,
    assigned to bar t, defined only when bar t-1 is at most 30 minutes earlier in label time
    (so weekend and holiday gaps never produce a return; a missing minute or the short
    post-rollover pause does).

Clocks:
    two_era    measured convention (fxclock.label_to_utc default)          -> "true" clock
    fixed_est  the vendor's documented convention (label + 5 h = UTC)       -> "documented" clock
    new_york   New York wall clock for all years (the earlier project fix)

Outputs (results/daily/):
    <PAIR>_<clock>.parquet  one row per New York calendar date: h00..h23 = sum of r_t in each
                            New York hour, n16 = bars in hour 16, mA/mB/mC = sum of r_t in
                            16:55-16:59, 17:00-17:04, 17:05-18:04 New York (the mask windows)
    <PAIR>_win.parquet      true clock only: one row per (date, minute) for 16:30-18:29 New York
                            with r, bar range (bp) and weekday
    <PAIR>_nyprofile.parquet true clock only: per (year, weekday, New York minute) n, sum, sum of
                            squares, sum |r|, sum of range, bar count
"""
import sys, time
from pathlib import Path
import numpy as np, pandas as pd
import fxio, fxclock

OUT = Path(__file__).resolve().parents[1] / "results" / "daily"
OUT.mkdir(parents=True, exist_ok=True)
CLOCKS = ("two_era", "fixed_est", "new_york")
MAXGAP_MIN = 30


def prep(df):
    lc = np.log(df["c"].to_numpy())
    gap = np.r_[np.inf, np.diff(df["t"].to_numpy()).astype("timedelta64[m]").astype(float)]
    r = np.r_[np.nan, np.diff(lc)] * 1e4
    r[gap > MAXGAP_MIN] = np.nan
    df["r"] = r
    df["rng"] = (df["h"] - df["l"]) / df["c"] * 1e4
    return df


def daily_for_clock(df, clock):
    ny = fxclock.utc_to_ny(fxclock.label_to_utc(df["t"], clock))
    d = pd.DataFrame({"date": ny.tz_localize(None).normalize(), "hour": ny.hour, "minute": ny.hour * 60 + ny.minute,
                      "r": df["r"].to_numpy()})
    d = d[np.isfinite(d.r)]
    hh = d.pivot_table(index="date", columns="hour", values="r", aggfunc="sum").reindex(columns=range(24))
    hh.columns = [f"h{h:02d}" for h in range(24)]
    hh["n16"] = d[d.hour == 16].groupby("date").size().reindex(hh.index).fillna(0).astype(int)
    for name, lo, hi in (("mA", 1015, 1019), ("mB", 1020, 1024), ("mC", 1025, 1084)):
        hh[name] = d[(d.minute >= lo) & (d.minute <= hi)].groupby("date").r.sum().reindex(hh.index).fillna(0.0)
    return hh.reset_index()


def true_clock_extras(df, year):
    ny = fxclock.utc_to_ny(fxclock.label_to_utc(df["t"], "two_era"))
    d = pd.DataFrame({"date": ny.tz_localize(None).normalize(), "dow": ny.dayofweek.astype("int8"),
                      "minute": (ny.hour * 60 + ny.minute).astype("int16"), "r": df["r"].to_numpy(), "rng": df["rng"].to_numpy()})
    win = d[(d.minute >= 990) & (d.minute < 1110)].copy()
    d["r2"] = d.r ** 2; d["ra"] = d.r.abs()
    prof = d.groupby(["dow", "minute"]).agg(n_bars=("rng", "size"), n=("r", "count"), s=("r", "sum"), ss=("r2", "sum"),
                                              sabs=("ra", "sum"), s_rng=("rng", "sum")).reset_index()
    prof.insert(0, "year", year)
    return win, prof


if __name__ == "__main__":
    for pair in sys.argv[1:]:
        t0 = time.time()
        daily = {c: [] for c in CLOCKS}; wins = []; profs = []
        for y in sorted({y for y, _ in fxio.zips_for(pair)}):
            df = prep(fxio.read_pair_year(pair, y))
            for c in CLOCKS:
                daily[c].append(daily_for_clock(df, c))
            w, p = true_clock_extras(df, y); wins.append(w); profs.append(p)
        for c in CLOCKS:
            x = pd.concat(daily[c], ignore_index=True)
            num = [k for k in x.columns if k != "date"]
            x = x.groupby("date", as_index=False)[num].sum(min_count=1)      # a NY date can straddle two year files
            x.to_parquet(OUT / f"{pair}_{c}.parquet", index=False)
        pd.concat(wins, ignore_index=True).to_parquet(OUT / f"{pair}_win.parquet", index=False)
        pd.concat(profs, ignore_index=True).to_parquet(OUT / f"{pair}_nyprofile.parquet", index=False)
        print(pair, f"{time.time()-t0:.0f}s", flush=True)
