"""Step 4: the pre-specified demonstration rule (see PRESPEC.txt) and the 24-hour scan.

Reads results/daily/<PAIR>_<clock>.parquet (built by build_daily.py). No raw data is touched.

Outputs (results/tables/):
    demo_rule_2x2.csv        pair x sample x clock x mask: n, mean bp/day, sd, t, Sharpe
    demo_rule_by_year.csv    pair x year, the four headline cells
    hour_scan.csv            pair x clock x mask x New York hour: long-the-hour mean, t, Sharpe
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "results" / "daily"; OUT = ROOT / "results" / "tables"; OUT.mkdir(parents=True, exist_ok=True)
HEAD = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD"]
EXT = ["USDCHF", "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"]
CLOCK_NAMES = {"fixed_est": "documented", "two_era": "true", "new_york": "new_york_all_years"}
MIN_BARS = 30


def stats(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    n = len(x)
    if n < 20:
        return dict(n=n, mean_bp=np.nan, sd_bp=np.nan, t=np.nan, sharpe=np.nan)
    m, s = x.mean(), x.std(ddof=1)
    return dict(n=n, mean_bp=m, sd_bp=s, t=m / (s / np.sqrt(n)), sharpe=m / s * np.sqrt(252))


def load(pair, clock):
    d = pd.read_parquet(D / f"{pair}_{clock}.parquet")
    d = d[d.date.dt.dayofweek < 5].copy()
    return d


def hour_ret(d, h, mask):
    """Sum of bid-to-bid returns in New York hour h, with the chosen mask applied on this clock.
    narrow = bars 16:55-17:04 removed; wide = bars 16:55-18:04 removed (wide needs columns c17, c18,
    which are only available on the true clock; for the 16:00-17:00 rule narrow and wide are identical)."""
    x = d[f"h{h:02d}"].copy()
    if mask in ("narrow", "wide"):
        if h == 16: x = x - d.mA
        if h == 17: x = x - d.mB
    if mask == "wide":
        if h == 17: x = x - d.c17
        if h == 18: x = x - d.c18
    return x


def add_wide_parts(d, pair):
    w = pd.read_parquet(D / f"{pair}_win.parquet", columns=["date", "minute", "r"])
    c17 = w[(w.minute >= 1025) & (w.minute <= 1079)].groupby("date").r.sum()
    c18 = w[(w.minute >= 1080) & (w.minute <= 1084)].groupby("date").r.sum()
    d["c17"] = d.date.map(c17).fillna(0.0); d["c18"] = d.date.map(c18).fillna(0.0)
    return d


if __name__ == "__main__":
    pairs = [p for p in HEAD + EXT if (D / f"{p}_two_era.parquet").exists()]
    rows, yrows, srows = [], [], []
    for p in pairs:
        for clock, cname in CLOCK_NAMES.items():
            d = load(p, clock); ok = d.n16 >= MIN_BARS
            for mask in ("none", "narrow"):
                pnl = -hour_ret(d, 16, mask)[ok]
                dates = d.date[ok]
                for sname, sel in (("2009-2026", dates.dt.year >= 2009), ("2015-2026", dates.dt.year >= 2015), ("2009-2014", dates.dt.year <= 2014)):
                    rows.append(dict(pair=p, group="headline" if p in HEAD else "extension", sample=sname, clock=cname, mask=mask, **stats(pnl[sel])))
                if clock in ("fixed_est", "two_era"):
                    for y, g in pnl.groupby(dates.dt.year):
                        yrows.append(dict(pair=p, year=y, clock=cname, mask=mask, **stats(g)))
                for h in range(24):
                    x = hour_ret(d, h, mask)
                    x = x[d[f"h{h:02d}"].notna()]
                    srows.append(dict(pair=p, clock=cname, mask=mask, ny_hour=h, **stats(x)))
            if clock == "two_era":
                d = add_wide_parts(d, p)
                for h in range(24):
                    x = hour_ret(d, h, "wide")
                    x = x[d[f"h{h:02d}"].notna()]
                    srows.append(dict(pair=p, clock=cname, mask="wide", ny_hour=h, **stats(x)))
    r = pd.DataFrame(rows).round(4); r.to_csv(OUT / "demo_rule_2x2.csv", index=False)
    pd.DataFrame(yrows).round(4).to_csv(OUT / "demo_rule_by_year.csv", index=False)
    s = pd.DataFrame(srows).round(4); s.to_csv(OUT / "hour_scan.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
    for sname in ("2009-2026", "2015-2026"):
        x = r[(r["sample"] == sname) & (r.clock != "new_york_all_years")]
        print("\nSAMPLE", sname, "- Sharpe (mean bp/day) [t]")
        x = x.assign(cell=x.clock + "/" + x["mask"], val=x.sharpe.round(2).astype(str) + " (" + x.mean_bp.round(3).astype(str) + ") [" + x.t.round(1).astype(str) + "]")
        print(x.pivot(index="pair", columns="cell", values="val").reindex(pairs).to_string())
    x = s[(s.clock == "true") & (s["mask"] == "none")].pivot(index="ny_hour", columns="pair", values="t").reindex(columns=pairs).round(1)
    print("\nHOUR SCAN, true clock, no mask: t-statistic of long-the-hour"); print(x.to_string())
