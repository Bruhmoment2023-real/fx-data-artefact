"""Step 6: independent second source. FXCM public one-minute candles carry bid AND ask and are
stamped in UTC (per FXCM's own README), so they can check both findings without trusting histdata.

A. Clock: for each year and daylight-saving regime, correlate histdata one-minute bid returns with
   FXCM one-minute bid returns under three hypotheses: UTC = histdata label + 4 h, + 5 h, + 6 h.
   The right offset gives a high correlation; the others give roughly zero.
B. Mechanism: FXCM bid, ask and mid one-minute returns and the quoted spread by New York minute.
C. The demonstration rule on FXCM prices: bid-to-bid (what a bid-only backtest sees), mid-to-mid,
   and executable (sell at the bid at 16:00, buy back at the ask at 17:00).
   NOTE: part C was added after the pre-specified demo had been run; it is a robustness check.

Usage: python analyze_fxcm.py EURUSD USDJPY AUDUSD
Outputs: results/tables/F1_clock_offset_vs_fxcm.csv, F1b_clock_offset_by_week_regime1.csv,
         F2_fxcm_rollover_by_year.csv, F2b_fxcm_window_by_minute.csv, F3_rule_on_fxcm.csv
"""
import sys, gzip
from pathlib import Path
import numpy as np, pandas as pd
import fxio, fxclock

ROOT = Path(__file__).resolve().parents[1]
FX = ROOT / "data_fxcm"; OUT = ROOT / "results" / "tables"; OUT.mkdir(parents=True, exist_ok=True)


def load_fxcm_year(pair, y):
    fs = sorted(FX.glob(f"{pair}_m1_{y}_w*.csv.gz"))
    if not fs: return None
    parts = []
    for f in fs:
        try:
            parts.append(pd.read_csv(f, compression="gzip"))
        except Exception as e:
            print("  skip", f.name, repr(e)[:60])
    d = pd.concat(parts, ignore_index=True)
    d["utc"] = pd.to_datetime(d["DateTime"], format="%m/%d/%Y %H:%M:%S.%f", errors="coerce")
    for col in ("BidOpen", "BidClose", "AskOpen", "AskClose"):
        d[col] = pd.to_numeric(d[col], errors="coerce")
    bad = d.utc.isna() | d[["BidOpen", "BidClose", "AskOpen", "AskClose"]].isna().any(axis=1) | (d.BidClose <= 0) | (d.AskClose <= 0)
    if bad.any(): print(f"  {pair} {y}: dropped {int(bad.sum())} unparseable rows of {len(d)}")
    d = d[~bad]
    d = d.drop_duplicates("utc").sort_values("utc").reset_index(drop=True)
    gap = d.utc.diff() / pd.Timedelta(minutes=1)
    for k, col in (("bid", "BidClose"), ("ask", "AskClose")):
        r = np.log(d[col]).diff() * 1e4; r[gap > 30] = np.nan; d["r_" + k] = r
    mid = (d.BidClose + d.AskClose) / 2
    r = np.log(mid).diff() * 1e4; r[gap > 30] = np.nan; d["r_mid"] = r
    d["spr"] = (d.AskClose - d.BidClose) / mid * 1e4
    d["gap1"] = gap == 1
    return d


def st(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 10: return dict(n=n, mean=np.nan, t=np.nan, sharpe=np.nan)
    m, s = x.mean(), x.std(ddof=1)
    return dict(n=n, mean=m, t=m / (s / np.sqrt(n)), sharpe=m / s * np.sqrt(252))


if __name__ == "__main__":
    pairs = sys.argv[1:] or ["EURUSD"]
    crow, wrow, mrow, minrow, rrow = [], [], [], [], []
    for pair in pairs:
        daily = []
        for y in range(2012, 2024):
            f = load_fxcm_year(pair, y)
            h = fxio.read_pair_year(pair, y)
            if f is None or h is None: continue
            # ---------- A. clock ----------
            lc = np.log(h.c.to_numpy()); cons = np.r_[False, np.diff(h.t.to_numpy()).astype("timedelta64[m]").astype(int) == 1]
            rh = np.r_[np.nan, np.diff(lc)] * 1e4; rh[~cons] = np.nan
            hs = pd.DataFrame({"label": h.t, "rh": rh, "regime": fxclock.dst_regime(h.t)}).dropna()
            hs["week"] = hs.label.dt.to_period("W-SAT").dt.start_time
            fser = f.loc[f.gap1, ["utc", "r_bid"]].dropna().set_index("utc").r_bid
            for k in (4, 5, 6):
                hs[f"f{k}"] = fser.reindex(hs.label + pd.Timedelta(hours=k)).to_numpy()
            for reg, g in hs.groupby("regime"):
                d = dict(pair=pair, year=y, regime=int(reg), minutes=len(g))
                for k in (4, 5, 6):
                    x = g[["rh", f"f{k}"]].dropna(); d[f"corr_plus{k}h"] = x.rh.corr(x[f"f{k}"]) if len(x) > 200 else np.nan
                d["best_offset_h"] = max((4, 5, 6), key=lambda k: -9 if np.isnan(d[f"corr_plus{k}h"]) else d[f"corr_plus{k}h"])
                crow.append(d)
            for wk, g in hs[hs.regime == 1].groupby("week"):
                d = dict(pair=pair, week_start=wk.date(), minutes=len(g))
                for k in (4, 5, 6):
                    x = g[["rh", f"f{k}"]].dropna(); d[f"corr_plus{k}h"] = x.rh.corr(x[f"f{k}"]) if len(x) > 200 else np.nan
                wrow.append(d)
            # ---------- B. mechanism ----------
            ny = f.utc.dt.tz_localize("UTC").dt.tz_convert("America/New_York")
            f["date"] = ny.dt.tz_localize(None).dt.normalize(); f["minute"] = ny.dt.hour * 60 + ny.dt.minute; f["dow"] = ny.dt.dayofweek
            f = f[f.dow < 5]
            def one(m, col): return st(f.loc[f.minute == m, col])
            d = dict(pair=pair, year=y)
            for m, nm in ((1019, "1659"), (1020, "1700"), (1080, "1800")):
                for col in ("r_bid", "r_ask", "r_mid"):
                    s = one(m, col); d[f"{col[2:]}_{nm}_mean"] = s["mean"]; d[f"{col[2:]}_{nm}_t"] = s["t"]
            d["days"] = one(1019, "r_bid")["n"]
            day_med = f.spr.median()
            for lo, hi, nm in ((600, 959, "1000_1559"), (960, 1014, "1600_1654"), (1015, 1018, "1655_1658"), (1019, 1019, "1659"),
                               (1020, 1024, "1700_1704"), (1025, 1079, "1705_1759"), (1080, 1139, "1800_1859"), (1140, 1199, "1900_1959")):
                d[f"spread_{nm}"] = f.loc[(f.minute >= lo) & (f.minute <= hi), "spr"].mean()
            d["spread_all_day_median"] = day_med
            mrow.append(d)
            w = f[(f.minute >= 990) & (f.minute < 1110)]
            minrow.append(w.groupby("minute").agg(n=("r_bid", "count"), s_bid=("r_bid", "sum"), s_ask=("r_ask", "sum"), s_mid=("r_mid", "sum"),
                                                  s_spr=("spr", "sum"), n_spr=("spr", "count")).reset_index().assign(pair=pair, year=y))
            # ---------- C. rule on FXCM prices ----------
            h16 = f[(f.minute >= 960) & (f.minute <= 1019)]
            g = h16.groupby("date")
            dd = pd.DataFrame({"n": g.size(), "bid_open": g.BidOpen.first(), "bid_close": g.BidClose.last(), "ask_open": g.AskOpen.first(), "ask_close": g.AskClose.last()})
            dd = dd[dd.n >= 30]
            dd["pnl_bid"] = -np.log(dd.bid_close / dd.bid_open) * 1e4
            dd["pnl_mid"] = -np.log((dd.bid_close + dd.ask_close) / (dd.bid_open + dd.ask_open)) * 1e4
            dd["pnl_exec"] = np.log(dd.bid_open / dd.ask_close) * 1e4          # sell at bid, buy back at ask
            dd["spread_exit"] = (dd.ask_close - dd.bid_close) / dd.bid_close * 1e4
            dd["year"] = y; daily.append(dd)
        if daily:
            dd = pd.concat(daily)
            for sname, sel in (("2012-2014", dd.year <= 2014), ("2015-2023", dd.year >= 2015), ("2012-2023", dd.year >= 2012)):
                for col, nm in (("pnl_bid", "bid-to-bid (what a bid-only backtest sees)"), ("pnl_mid", "mid-to-mid"), ("pnl_exec", "executable: sell bid 16:00, buy ask 17:00")):
                    rrow.append(dict(pair=pair, sample=sname, pricing=nm, **st(dd.loc[sel, col]), mean_exit_spread_bp=dd.loc[sel, "spread_exit"].mean()))
        print(pair, "done", flush=True)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
    c = pd.DataFrame(crow).round(4); c.to_csv(OUT / "F1_clock_offset_vs_fxcm.csv", index=False)
    pd.DataFrame(wrow).round(4).to_csv(OUT / "F1b_clock_offset_by_week_regime1.csv", index=False)
    m = pd.DataFrame(mrow).round(4); m.to_csv(OUT / "F2_fxcm_rollover_by_year.csv", index=False)
    if minrow:
        x = pd.concat(minrow)
        x["era"] = np.where(x.year <= 2014, "2012-2014", "2015-2023")
        x = x.groupby(["pair", "era", "minute"])[["n", "s_bid", "s_ask", "s_mid", "s_spr", "n_spr"]].sum().reset_index()
        for k in ("bid", "ask", "mid"): x[f"{k}_ret_bp"] = x[f"s_{k}"] / x.n
        x["spread_bp"] = x.s_spr / x.n_spr; x["hhmm_ny"] = x.minute.map(lambda v: f"{v // 60:02d}:{v % 60:02d}")
        x.drop(columns=["s_bid", "s_ask", "s_mid", "s_spr", "n_spr"]).round(4).to_csv(OUT / "F2b_fxcm_window_by_minute.csv", index=False)
    r = pd.DataFrame(rrow).round(4); r.to_csv(OUT / "F3_rule_on_fxcm.csv", index=False)
    print(c.to_string(index=False)); print(pd.DataFrame(wrow).round(3).to_string(index=False))
    print(m[["pair", "year", "days", "bid_1659_mean", "bid_1659_t", "ask_1659_mean", "ask_1659_t", "mid_1659_mean", "mid_1659_t", "spread_1000_1559", "spread_1600_1654", "spread_1659", "spread_1700_1704", "spread_1705_1759", "spread_1800_1859"]].to_string(index=False))
    print(r.to_string(index=False))
