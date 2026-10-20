"""Task 2b - why does the rollover artefact begin in 2015? (specified in ADDENDUM-2026-10-13.md, A2)

Step 1:  python break_2015.py build EURUSD USDJPY ...   -> followup/tables/break/daily_<PAIR>.csv   (raw zips 2013-2016, read-only)
Step 2:  python break_2015.py test                      -> followup/tables/break_tests.csv, break_monthly.csv
Daily features use the true (two-era) clock; before 2019 that equals New York wall clock.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
PACK = Path(r"D:/Research-Publishing/03-fx-data-artefact"); sys.path.insert(0, str(PACK / "code"))
import fxio, fxclock

TAB = Path(__file__).resolve().parents[1] / "tables"; OUT = TAB / "break"; OUT.mkdir(parents=True, exist_ok=True)
PAIRS = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCHF", "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"]
YEARS = (2013, 2014, 2015, 2016)


def decimals_used(c, dp):
    v = np.round(c * 10 ** dp).astype(np.int64); tz = np.zeros(len(v), int)
    for k in range(1, dp + 1):
        tz += (v % 10 ** k == 0)
    return dp - np.minimum(tz, dp)


def build(pair):
    dp = 3 if "JPY" in pair else 5
    parts = []
    for y in YEARS:
        df = fxio.read_pair_year(pair, y)
        gap = np.r_[np.inf, np.diff(df.t.to_numpy()).astype("timedelta64[m]").astype(float)]
        r = np.r_[np.nan, np.diff(np.log(df.c.to_numpy()))] * 1e4; r[gap > 30] = np.nan
        ny = fxclock.utc_to_ny(fxclock.label_to_utc(df.t, "two_era"))
        d = pd.DataFrame({"date": ny.tz_localize(None).normalize(), "min": (ny.hour * 60 + ny.minute).to_numpy(), "r": r,
                          "rng": ((df.h - df.l) / df.c * 1e4).to_numpy(), "hl_eq": (df.h == df.l).to_numpy(),
                          "dec": decimals_used(df.c.to_numpy(), dp)})
        d = d[d.date.dt.dayofweek < 5]
        g = d.groupby("date")
        out = pd.DataFrame({"bars": g.size(), "hl_eq_share": g.hl_eq.mean(), "dec_mean": g.dec.mean()})
        b = d[d["min"] == 1019].set_index("date")           # 16:59 bar
        out["r1659"] = b.r; out["rng1659"] = b.rng
        pre = d[(d["min"] >= 990) & (d["min"] <= 1014)]       # 16:30-16:54
        out["rng_pre"] = pre.groupby("date").rng.mean(); out["bars_pre"] = pre.groupby("date").size()
        w = d[(d["min"] >= 1015) & (d["min"] <= 1024)]        # 16:55-17:04
        out["bars_win"] = w.groupby("date").size()
        out["no_bar_1700_1704"] = (d[(d["min"] >= 1020) & (d["min"] <= 1024)].groupby("date").size().reindex(out.index).fillna(0) == 0).astype(int)
        parts.append(out.reset_index())
        print(pair, y, len(out), flush=True)
    x = pd.concat(parts).groupby("date", as_index=False).agg({"bars": "sum", "hl_eq_share": "mean", "dec_mean": "mean", "r1659": "first",
                                                              "rng1659": "first", "rng_pre": "mean", "bars_pre": "sum", "bars_win": "sum", "no_bar_1700_1704": "max"})
    x.insert(0, "pair", pair); x.to_csv(OUT / f"daily_{pair}.csv", index=False)


def welch_abs_t(a, b):
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if len(a) < 20 or len(b) < 20: return np.nan
    return abs(a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))


def test():
    series = ["r1659", "rng1659", "rng_pre", "bars", "bars_win", "hl_eq_share", "dec_mean", "no_bar_1700_1704"]
    rows, mrows = [], []
    for p in PAIRS:
        f = OUT / f"daily_{p}.csv"
        if not f.exists(): continue
        d = pd.read_csv(f, parse_dates=["date"]); d["ym"] = d.date.dt.to_period("M")
        m = d.groupby("ym").agg(days=("date", "size"), r1659_mean=("r1659", "mean"), r1659_sd=("r1659", "std"), r1659_n=("r1659", "count"),
                                  zero1659=("r1659", lambda s: (s.dropna() == 0).mean()), rng1659=("rng1659", "mean"), rng_pre=("rng_pre", "mean"),
                                  bars=("bars", "mean"), bars_win=("bars_win", "mean"), hl_eq_share=("hl_eq_share", "mean"),
                                  dec_mean=("dec_mean", "mean"), no_bar_1700_1704=("no_bar_1700_1704", "mean")).reset_index()
        m["r1659_t"] = m.r1659_mean / (m.r1659_sd / np.sqrt(m.r1659_n)); m.insert(0, "pair", p); mrows.append(m)
        for s in series:
            best = (np.nan, None)
            for b in pd.period_range("2014-07", "2015-12", freq="M"):
                pre = d[(d.ym >= b - 12) & (d.ym < b)][s].to_numpy(float); post = d[(d.ym >= b) & (d.ym < b + 6)][s].to_numpy(float)
                t = welch_abs_t(post, pre)
                if np.isfinite(t) and (best[1] is None or t > best[0]): best = (t, b)
            pre = d[(d.ym >= best[1] - 12) & (d.ym < best[1])][s].mean() if best[1] is not None else np.nan
            post = d[(d.ym >= best[1]) & (d.ym < best[1] + 6)][s].mean() if best[1] is not None else np.nan
            rows.append(dict(pair=p, series=s, break_month=str(best[1]), abs_welch_t=best[0], mean_before_12m=pre, mean_after_6m=post))
    pd.DataFrame(rows).to_csv(TAB / "break_tests.csv", index=False)
    pd.concat(mrows).to_csv(TAB / "break_monthly.csv", index=False)
    r = pd.DataFrame(rows); r["bm"] = pd.PeriodIndex(r.break_month, freq="M")
    ref = r[r.series == "r1659"].set_index("pair").bm
    for s in series:
        x = r[r.series == s].set_index("pair")
        within1 = int(sum(abs((x.bm[p] - ref[p]).n) <= 1 for p in x.index if p in ref.index))
        print(f"{s:18s} break month by pair: " + " ".join(f"{p}:{x.bm[p]}" for p in x.index) + f" | within 1 month of r1659 break: {within1}/{len(x)}")


if __name__ == "__main__":
    if sys.argv[1] == "build":
        for p in sys.argv[2:]: build(p)
    else:
        test()
