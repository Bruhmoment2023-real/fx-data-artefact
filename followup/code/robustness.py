"""Task 3 - robustness (specified in ADDENDUM-2026-10-13.md, A3). SECONDARY analysis.

Inputs : followup/rerun/results/daily/<INST>_{two_era,win,nyprofile}.parquet   (made by build_daily.py on the true clock)
Outputs: followup/tables/R1_profile_all_instruments.csv   minute-of-day summary per instrument and sample
         followup/tables/R2_size_by_year.csv              16:59 bar and 16:55-17:04 sum by instrument and year
         followup/tables/R3_mask_grid_rule.csv            rule "short 16:00-17:00", mask start b minutes before 17:00
         followup/tables/R4_after_side_residual.csv       sums of returns after 17:00 left unmasked, by after-mask length a
         followup/tables/R3b_mask_verdict.csv             |t| < 2 criterion per mask over the ten FX pairs
Usage: python robustness.py [DAILY_DIR]
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "rerun" / "results" / "daily"
OUT = ROOT / "tables"; OUT.mkdir(exist_ok=True)
FX = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCHF", "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"]
OTHER = ["XAUUSD", "XAGUSD", "SPXUSD", "NSXUSD", "UKXGBP", "GRXEUR", "JPXJPY", "UDXUSD", "WTIUSD"]
ALL = [i for i in FX + OTHER if (D / f"{i}_two_era.parquet").exists()]
SAMPLES = {"2009-2014": (2009, 2014), "2015-2026": (2015, 2026)}
hm = lambda m: f"{int(m) // 60:02d}:{int(m) % 60:02d}"


def st(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 20: return dict(n=n, mean_bp=np.nan, t=np.nan, sharpe=np.nan)
    m, s = x.mean(), x.std(ddof=1)
    return dict(n=n, mean_bp=m, t=m / (s / np.sqrt(n)), sharpe=m / s * np.sqrt(252))


def r1():
    rows = []
    for i in ALL:
        d = pd.read_parquet(D / f"{i}_nyprofile.parquet"); d = d[d.dow < 5]
        for sn, (a, b) in SAMPLES.items():
            g = d[d.year.between(a, b)].groupby("minute")[["n", "s", "ss"]].sum(); g = g[g.n > 30]
            if not len(g): continue
            mean = g.s / g.n; sd = np.sqrt((g.ss - g.n * mean ** 2) / (g.n - 1)); t = mean / (sd / np.sqrt(g.n))
            order = t.sort_values()
            m59 = 1019
            rows.append(dict(inst=i, sample=sn, minutes=len(g), mean_1659_bp=mean.get(m59, np.nan), t_1659=t.get(m59, np.nan),
                             rank_1659_from_most_negative=int(list(order.index).index(m59) + 1) if m59 in order.index else np.nan,
                             most_negative_minute=hm(order.index[0]), most_negative_t=order.iloc[0],
                             most_positive_minute=hm(order.index[-1]), most_positive_t=order.iloc[-1],
                             n_abs_t_gt4=int((t.abs() > 4).sum()), median_abs_t=float(t.abs().median())))
    pd.DataFrame(rows).round(3).to_csv(OUT / "R1_profile_all_instruments.csv", index=False)


def load_win(i):
    w = pd.read_parquet(D / f"{i}_win.parquet", columns=["date", "minute", "r", "dow"])
    return w[w.dow < 5]


def r2():
    rows = []
    for i in ALL:
        w = load_win(i); w = w.assign(year=w.date.dt.year)
        p = w.pivot_table(index="date", columns="minute", values="r", aggfunc="sum")
        r59 = p.get(1019); s5504 = p[[c for c in p.columns if 1015 <= c <= 1024]].sum(axis=1, min_count=1)
        df = pd.DataFrame({"year": p.index.year, "r1659": r59, "s": s5504})
        for y, g in df.groupby("year"):
            a, b = st(g.r1659), st(g.s)
            rows.append(dict(inst=i, year=int(y), n_days=a["n"], mean_1659_bp=a["mean_bp"], t_1659=a["t"],
                             share_negative_1659=float((g.r1659.dropna() < 0).mean()), share_zero_1659=float((g.r1659.dropna() == 0).mean()),
                             mean_sum_1655_1704_bp=b["mean_bp"], t_sum_1655_1704=b["t"]))
    pd.DataFrame(rows).round(3).to_csv(OUT / "R2_size_by_year.csv", index=False)


def r3_r4():
    r3, r4 = [], []
    for i in ALL:
        d = pd.read_parquet(D / f"{i}_two_era.parquet"); d = d[d.date.dt.dayofweek < 5].set_index("date")
        w = load_win(i)
        p = w.pivot_table(index="date", columns="minute", values="r", aggfunc="sum")
        d = d[d.n16 >= 30]
        for b in (0, 5, 10, 15, 20, 25, 30):
            cols = [c for c in p.columns if 1020 - b <= c <= 1019]
            masked = p.reindex(d.index)[cols].sum(axis=1, min_count=1).fillna(0.0) if b else 0.0
            pnl = -(d.h16 - masked)                       # short the hour with bars 17:00-b ... 16:59 set to zero
            for sn, (a, bb) in SAMPLES.items():
                s = pnl[(pnl.index.year >= a) & (pnl.index.year <= bb)]
                r3.append(dict(inst=i, mask_start_minutes_before_1700=b, sample=sn, **st(s)))
        # early-hour residual (16:00-16:29) is the b = 30 row. After-side residuals:
        for a in (5, 35, 60, 65, 89):
            cols = [c for c in p.columns if 1020 + a <= c <= 1109]
            x = p.reindex(d.index)[cols].sum(axis=1, min_count=1)
            for sn, (lo, hi) in SAMPLES.items():
                s = x[(x.index.year >= lo) & (x.index.year <= hi)]
                r4.append(dict(inst=i, after_mask_minutes=a, residual_window=f"{hm(1020 + a)}-18:29", sample=sn, **st(s)))
    r3 = pd.DataFrame(r3); r4 = pd.DataFrame(r4)
    r3.round(4).to_csv(OUT / "R3_mask_grid_rule.csv", index=False); r4.round(4).to_csv(OUT / "R4_after_side_residual.csv", index=False)
    # verdict: |t| < 2 for the ten FX pairs, 2015-2026; "effective" if >= 8 of 10 pairs at this and every wider b
    v = r3[(r3["sample"] == "2015-2026") & r3.inst.isin(FX)].copy()
    v["abs_t_lt2"] = v.t.abs() < 2
    s = v.groupby("mask_start_minutes_before_1700").agg(pairs=("inst", "size"), n_abs_t_lt2=("abs_t_lt2", "sum"), mean_sharpe=("sharpe", "mean"),
                                                        min_sharpe=("sharpe", "min"), max_sharpe=("sharpe", "max"), n_positive_t_gt2=("t", lambda x: int((x > 2).sum())),
                                                        n_negative_t_lt_m2=("t", lambda x: int((x < -2).sum())))
    ok = (s.n_abs_t_lt2 >= 8)[::-1].cumprod()[::-1].astype(bool)      # this and every wider mask
    s["effective_by_prespecified_criterion"] = ok
    s.round(3).to_csv(OUT / "R3b_mask_verdict.csv")
    print(s.round(2).to_string())


if __name__ == "__main__":
    print("instruments:", ALL)
    r1(); r2(); r3_r4(); print("done")
