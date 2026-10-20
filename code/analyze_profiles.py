"""Step 5: tables on the rollover artefact and the clock, from the small intermediate files.

Inputs : results/daily/<PAIR>_nyprofile.parquet, <PAIR>_win.parquet  (true clock, build_daily.py)
         results/minute_stats/<PAIR>.parquet                         (label clock, build_minute_stats.py)
Outputs: results/tables/*.csv  (listed at the end of the run)

All returns are one-minute bid-to-bid log returns in basis points. t = mean / (sd / sqrt(n)),
one observation per trading day, no autocorrelation correction (one bar per day).
"""
from pathlib import Path
import numpy as np, pandas as pd
import fxio

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "results" / "daily"; MS = ROOT / "results" / "minute_stats"; OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)
FX = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCHF", "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"]
METALS = ["XAUUSD", "XAGUSD"]
hm = lambda m: f"{int(m) // 60:02d}:{int(m) % 60:02d}"


def tstat(n, s, ss):
    mean = s / n; var = (ss - n * mean ** 2) / (n - 1)
    return mean, np.sqrt(var), mean / np.sqrt(var / n)


def st(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 10: return n, np.nan, np.nan
    return n, x.mean(), x.mean() / (x.std(ddof=1) / np.sqrt(n))


def have(pairs, suffix):
    return [p for p in pairs if (D / f"{p}{suffix}").exists()]


# ---------- T1: minute-of-day profile on the true New York clock -------------------------------
def t1():
    out, rank = [], []
    for p in have(FX + METALS, "_nyprofile.parquet"):
        d = pd.read_parquet(D / f"{p}_nyprofile.parquet"); d = d[d.dow < 5]
        for sname, sel in (("2009-2026", d.year >= 2009), ("2009-2014", d.year <= 2014), ("2015-2026", d.year >= 2015)):
            g = d[sel].groupby("minute")[["n", "s", "ss", "sabs", "s_rng", "n_bars"]].sum()
            g = g[g.n > 30]
            m, sd, t = tstat(g.n, g.s, g.ss)
            x = pd.DataFrame({"pair": p, "sample": sname, "ny_minute": g.index, "hhmm_ny": [hm(i) for i in g.index], "n": g.n.astype(int),
                              "mean_bp": m, "sd_bp": sd, "t": t, "mean_abs_bp": g.sabs / g.n, "mean_range_bp": g.s_rng / g.n_bars})
            out.append(x)
            xs = x.sort_values("t")
            r1659 = x[x.ny_minute == 1019]
            rank.append(dict(pair=p, sample=sname, minutes=len(x), most_negative_minute=xs.hhmm_ny.iloc[0], most_negative_t=xs.t.iloc[0],
                             second_most_negative=xs.hhmm_ny.iloc[1], second_t=xs.t.iloc[1],
                             most_positive_minute=xs.hhmm_ny.iloc[-1], most_positive_t=xs.t.iloc[-1],
                             t_1659=float(r1659.t.iloc[0]) if len(r1659) else np.nan, mean_1659_bp=float(r1659.mean_bp.iloc[0]) if len(r1659) else np.nan,
                             n_abs_t_gt4=int((x.t.abs() > 4).sum()), n_abs_t_gt3=int((x.t.abs() > 3).sum()),
                             median_abs_t_other=float(x[x.ny_minute != 1019].t.abs().median())))
    pd.concat(out).round(4).to_csv(OUT / "T1_minute_profile_ny.csv", index=False)
    r = pd.DataFrame(rank).round(3); r.to_csv(OUT / "T1b_minute_profile_summary.csv", index=False)
    top = pd.concat(out, ignore_index=True); top = top[top["sample"] == "2015-2026"]
    top = top.assign(abs_t=top.t.abs()).sort_values(["pair", "abs_t"], ascending=[True, False]).groupby("pair").head(15)
    top.round(4).to_csv(OUT / "T7_top15_minutes_2015_2026.csv", index=False)
    return r


# ---------- T2/T3/T4: rollover window from per-day data ----------------------------------------
def window_table(w, lo, hi):
    return w[(w.minute >= lo) & (w.minute <= hi)].groupby("date").r.sum()


def t2():
    rows, wrows, rrows = [], [], []
    for p in have(FX + METALS, "_win.parquet"):
        w = pd.read_parquet(D / f"{p}_win.parquet"); w = w[w.dow < 5]
        w["year"] = w.date.dt.year
        dts = w.groupby("date").agg(year=("year", "first"), dow=("dow", "first"))
        dts["r1659"] = w[w.minute == 1019].set_index("date").r
        dts["r1700"] = w[w.minute == 1020].set_index("date").r
        dts["r1705"] = w[w.minute == 1025].set_index("date").r
        dts["r1800"] = w[w.minute == 1080].set_index("date").r
        dts["s1655_1659"] = window_table(w, 1015, 1019)
        dts["s1655_1704"] = window_table(w, 1015, 1024)
        dts["s1655_1804"] = window_table(w, 1015, 1084)
        dts["s1630_1654"] = window_table(w, 990, 1014)
        dts["rng1659"] = w[w.minute == 1019].set_index("date").rng
        dts["rng_base"] = w[(w.minute >= 990) & (w.minute <= 1014)].groupby("date").rng.mean()
        def block(g, **key):
            d = dict(pair=p, **key)
            for c in ("r1659", "r1700", "r1705", "r1800", "s1655_1659", "s1655_1704", "s1655_1804", "s1630_1654"):
                n, m, t = st(g[c]); d[f"{c}_mean"] = m; d[f"{c}_t"] = t
                if c == "r1659": d["n_days"] = n
            d["share_days_negative_1659"] = float((g.r1659.dropna() < 0).mean()) if g.r1659.notna().sum() else np.nan
            d["share_days_zero_1659"] = float((g.r1659.dropna() == 0).mean()) if g.r1659.notna().sum() else np.nan
            d["median_1659"] = float(g.r1659.median())
            d["range_1659_bp"] = float(g.rng1659.mean()); d["range_1630_1654_bp"] = float(g.rng_base.mean())
            return d
        for y, g in dts.groupby("year"):
            rows.append(block(g, year=int(y)))
        for sname, sel in (("2009-2014", dts.year <= 2014), ("2015-2026", dts.year >= 2015), ("2009-2026", dts.year >= 2009)):
            rows.append(block(dts[sel], year=sname))
            for dw, g in dts[sel].groupby("dow"):
                wrows.append(block(g, sample=sname, weekday=["Mon", "Tue", "Wed", "Thu", "Fri"][int(dw)]))
            x = w[w.year.between(*((2009, 2014) if sname == "2009-2014" else (2015, 2026) if sname == "2015-2026" else (2009, 2026)))]
            g = x.groupby("minute").agg(n=("r", "count"), mean_bp=("r", "mean"), sd=("r", "std"), mean_abs_bp=("r", lambda s: s.abs().mean()),
                                        mean_range_bp=("rng", "mean"), bars=("rng", "size")).reset_index()
            g["t"] = g.mean_bp / (g.sd / np.sqrt(g.n)); g["cum_mean_bp"] = g.mean_bp.cumsum()
            g.insert(0, "sample", sname); g.insert(0, "pair", p); g["hhmm_ny"] = g.minute.map(hm)
            rrows.append(g)
    a = pd.DataFrame(rows).round(4); a.to_csv(OUT / "T2_rollover_by_pair_year.csv", index=False)
    b = pd.DataFrame(wrows).round(4); b.to_csv(OUT / "T3_rollover_by_weekday.csv", index=False)
    pd.concat(rrows).round(4).to_csv(OUT / "T4_window_1630_1829_by_minute.csv", index=False)
    return a, b


# ---------- T5: clock evidence from label-clock statistics --------------------------------------
def t5():
    rows = []
    for p in [q for q in FX + METALS if (MS / f"{q}.parquet").exists()]:
        d = pd.read_parquet(MS / f"{p}.parquet")
        for (y, s), g in d.groupby(["year", "dst"]):
            if s > 2: continue
            fr = g[g.dow == 4].groupby("minute").n_bars.sum(); su = g[g.dow == 6].groupby("minute").n_bars.sum()
            last_fri = fr[fr >= 0.5 * fr.max()].index.max() if len(fr) else np.nan
            first_sun = su[su >= 0.5 * su.max()].index.min() if len(su) else np.nan
            a = g[g.dow < 5].groupby("minute")[["n", "sabs"]].sum(); a["ma"] = a.sabs / a.n
            base = a.ma.median()
            def rel(m): return float(a.ma.get(m, np.nan) / base)
            am = a.loc[6 * 60:10 * 60 + 30, "ma"]
            rows.append(dict(pair=p, year=int(y), regime=int(s), fridays=int(fr.max()) if len(fr) else 0,
                             friday_last_bar_label=hm(last_fri) if last_fri == last_fri else "", sunday_first_bar_label=hm(first_sun) if first_sun == first_sun else "",
                             morning_peak_label=hm(am.idxmax()), absret_0730_rel=rel(450), absret_0830_rel=rel(510), absret_0930_rel=rel(570),
                             absret_1955_rel=rel(1195), absret_2055_rel=rel(1255)))
    x = pd.DataFrame(rows).round(3); x.to_csv(OUT / "T5_clock_evidence_by_year_regime.csv", index=False)
    # compact summary: share of pair-years whose Friday close label is 16:59, by era and regime
    x["era"] = np.where(x.year <= 2018, "2009-2018", "2019-2026")
    fxo = x[x.pair.isin(FX)]
    s = fxo.groupby(["era", "regime"]).agg(pair_years=("pair", "size"),
                                           close_1659=("friday_last_bar_label", lambda v: (v == "16:59").mean()),
                                           close_1559=("friday_last_bar_label", lambda v: (v == "15:59").mean()),
                                           peak_0830=("morning_peak_label", lambda v: (v == "08:30").mean()),
                                           peak_0730=("morning_peak_label", lambda v: (v == "07:30").mean()),
                                           absret_0730_rel=("absret_0730_rel", "median"), absret_0830_rel=("absret_0830_rel", "median"),
                                           absret_1955_rel=("absret_1955_rel", "median"), absret_2055_rel=("absret_2055_rel", "median")).reset_index().round(3)
    s.to_csv(OUT / "T5b_clock_evidence_summary.csv", index=False)
    return s


# ---------- T6: every Friday close label for one pair, straight from the raw files ---------------
def t6(pair="EURUSD"):
    import fxclock
    rows = []
    for y in sorted({y for y, _ in fxio.zips_for(pair)}):
        df = fxio.read_pair_year(pair, y)
        gap = df.t.diff().shift(-1); nxt = df.t.shift(-1)
        sel = (gap > pd.Timedelta(hours=30)) & (gap < pd.Timedelta(hours=100))
        for t_last, t_next in zip(df.t[sel], nxt[sel]):
            rows.append(dict(pair=pair, last_bar_label=t_last, next_bar_label=t_next))
    x = pd.DataFrame(rows)
    x["regime"] = fxclock.dst_regime(x.last_bar_label)
    x["last_hhmm"] = x.last_bar_label.dt.strftime("%a %H:%M"); x["next_hhmm"] = x.next_bar_label.dt.strftime("%a %H:%M")
    x.to_csv(OUT / f"T6_weekly_close_open_labels_{pair}.csv", index=False)
    r1 = x[(x.regime == 1) & (x.last_bar_label.dt.dayofweek == 4)]
    return r1[["last_bar_label", "next_bar_label"]]


if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
    r = t1(); print("T1b summary (2015-2026)"); print(r[r["sample"] == "2015-2026"].to_string(index=False))
    a, b = t2()
    cols = ["pair", "year", "n_days", "r1659_mean", "r1659_t", "r1700_mean", "r1700_t", "s1655_1704_mean", "s1655_1704_t", "r1705_mean", "r1800_mean", "r1800_t", "s1655_1804_mean", "s1655_1804_t", "share_days_negative_1659", "range_1659_bp", "range_1630_1654_bp"]
    print("\nT2 pooled rows"); print(a[a.year.isin(["2009-2014", "2015-2026"])][cols].to_string(index=False))
    print("\nT2 EURUSD by year"); print(a[(a.pair == "EURUSD")][cols].to_string(index=False))
    print("\nT3 weekday, 2015-2026"); print(b[b["sample"] == "2015-2026"][["pair", "weekday", "n_days", "r1659_mean", "r1659_t", "s1655_1704_mean", "s1655_1704_t", "r1800_mean"]].to_string(index=False))
    print("\nT5b"); print(t5().to_string(index=False))
    print("\nT6 regime-1 Fridays (EURUSD)"); print(t6().to_string(index=False))
