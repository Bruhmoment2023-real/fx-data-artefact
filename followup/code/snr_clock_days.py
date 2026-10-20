"""Task 5 - how many trading days does the Malaysian-SNR clock helper get wrong, and what does it do to the 16:55 mask?
READ-ONLY on D:\\Malaysian-SNR (parquet read; nothing written there). Outputs go to followup/tables/ and followup/malaysian-snr-copy/.

Part A (calendar, no market data): weekdays whose label->UTC conversion differs between
   cf_clock   = "labels are New York wall clock + 5 h, every year"   (fxclock convention 'new_york' applied to label - 5 h)
   the measured two-era rule (fxclock 'two_era')
   and the phase-4/5 original assumption ('fixed_est' / label == UTC)
Part B (light re-derivation on in-memory copies): the pack's rule "short NY 16:00-17:00" on the SNR project's own 5-minute bars,
   clock = cf_clock vs two_era, mask = none vs the 16:55 New York 5-minute bar (what phase4cf_pm masked).
Usage: python snr_clock_days.py
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

PACK = Path(r"D:/Research-Publishing/03-fx-data-artefact"); sys.path.insert(0, str(PACK / "code"))
import fxclock

TAB = Path(__file__).resolve().parents[1] / "tables"; TAB.mkdir(exist_ok=True)
D4 = Path(r"D:/Malaysian-SNR/phase4/data")


def part_a(end):
    days = pd.bdate_range("2009-01-01", end)
    lab = pd.DatetimeIndex(days + pd.Timedelta(hours=12))                      # a label at 12:00 on each weekday
    two = fxclock.label_to_utc(lab, "two_era"); ny = fxclock.label_to_utc(lab, "new_york"); fx = fxclock.label_to_utc(lab, "fixed_est")
    reg = fxclock.dst_regime(days)
    df = pd.DataFrame({"date": days, "year": days.year, "regime": reg, "cf_wrong": (two != ny), "fixed_est_wrong": (two != fx)})
    rows = []
    for name, sel in (("2009-2018", df.year <= 2018), ("2019-2026", df.year >= 2019), ("2010-2026 (phase 4/5 span)", df.year >= 2010), ("all 2009-2026", df.year >= 2009)):
        g = df[sel]
        rows.append(dict(span=name, weekdays=len(g), cf_clock_wrong_days=int(g.cf_wrong.sum()), cf_wrong_share=round(g.cf_wrong.mean(), 4),
                         original_label_is_utc_wrong_days=int(g.fixed_est_wrong.sum()), original_wrong_share=round(g.fixed_est_wrong.mean(), 4)))
    pd.DataFrame(rows).to_csv(TAB / "SNR_A1_days_summary.csv", index=False)
    y = df.groupby("year").agg(weekdays=("date", "size"), cf_wrong=("cf_wrong", "sum"), fixed_est_wrong=("fixed_est_wrong", "sum")).reset_index()
    y.to_csv(TAB / "SNR_A2_days_by_year.csv", index=False)
    # list the wrong weeks
    w = df[df.cf_wrong]; blocks = []
    start = prev = None
    for d in w.date:
        if start is None: start = prev = d
        elif (d - prev).days <= 3: prev = d
        else: blocks.append((start, prev)); start = prev = d
    if start is not None: blocks.append((start, prev))
    pd.DataFrame([(a.date(), b.date(), len(pd.bdate_range(a, b))) for a, b in blocks], columns=["first_weekday", "last_weekday", "weekdays"]).to_csv(TAB / "SNR_A3_wrong_weeks.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False)); print(y.to_string(index=False))


def returns5(close_index_raw, c):
    lc = np.log(c); gap = np.r_[np.inf, np.diff(close_index_raw.to_numpy()).astype("timedelta64[m]").astype(float)]
    r = np.r_[np.nan, np.diff(lc)] * 1e4; r[gap > 5] = np.nan
    return r


def stats(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    m, s = x.mean(), x.std(ddof=1)
    return dict(n=n, mean_bp=round(m, 4), t=round(m / (s / np.sqrt(n)), 2), sharpe=round(m / s * np.sqrt(252), 2))


def part_b(pairs):
    rows = []
    for p in pairs:
        d = pd.read_parquet(D4 / f"{p}_5m.parquet", columns=["close"])
        lab = d.index.tz_localize(None) if d.index.tz is not None else d.index
        raw = pd.DatetimeIndex(lab - pd.Timedelta(hours=5))                 # the vendor's own label (SNR added 5 h)
        r = returns5(raw, d["close"].to_numpy())
        for clock in ("cf_clock (NY wall clock all years)", "two_era (measured)"):
            utc = fxclock.label_to_utc(raw, "new_york" if clock.startswith("cf") else "two_era")
            ny = fxclock.utc_to_ny(utc)
            x = pd.DataFrame({"date": ny.tz_localize(None).normalize(), "m": (ny.hour * 60 + ny.minute).to_numpy(), "r": r, "dow": ny.dayofweek.to_numpy()})
            x = x[(x.dow < 5) & np.isfinite(x.r)]
            h = x[(x.m >= 960) & (x.m < 1020)]
            cnt = h.groupby("date").size(); ok = cnt[cnt >= 10].index
            none = -h[h.date.isin(ok)].groupby("date").r.sum()
            masked = -h[h.date.isin(ok) & (h.m != 1015)].groupby("date").r.sum()   # drop the 16:55 New York 5-minute bar
            for sname, lo in (("2015-2026", 2015), ("2019-2026", 2019), ("2009-2018 (cf right)", None)):
                if lo is None: sel = lambda s: s[(s.index.year >= 2009) & (s.index.year <= 2018)]
                else: sel = (lambda lo: (lambda s: s[s.index.year >= lo]))(lo)
                for mname, s in (("none", none), ("16:55 bar masked", masked)):
                    rows.append(dict(pair=p, clock=clock, sample=sname, mask=mname, **stats(sel(s))))
        print(p, "done", flush=True)
    out = pd.DataFrame(rows); out.to_csv(TAB / "SNR_B_rule_cf_vs_true.csv", index=False)
    print(out.query("sample=='2019-2026'").to_string(index=False))


if __name__ == "__main__":
    last = pd.read_parquet(D4 / "EURUSD_5m.parquet", columns=["close"]).index.max()
    print("last bar in SNR 5m EURUSD:", last)
    part_a(pd.Timestamp(last).tz_localize(None).normalize())
    if len(sys.argv) > 1 and sys.argv[1] == "b":
        part_b(["EURUSD", "NZDUSD", "EURGBP", "USDCHF", "AUDUSD"])
