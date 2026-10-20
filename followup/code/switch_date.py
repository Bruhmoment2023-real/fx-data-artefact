"""Task 2a - when did the histdata timestamp convention switch? (specified in ADDENDUM-2026-10-13.md, A1 and A1b)

Usage: python switch_date.py EURUSD USDJPY ...       (one instrument at a time is read; raw zips are read-only)
Writes one small CSV set per instrument to followup/tables/switch/ :
   <INST>_days.csv    one row per calendar day 2018-09-01..2019-04-30: first/last label, bars, grid shares, last-bar label
   <INST>_weeks.csv   one row per Sunday-start week: Friday last-bar label, Sunday first-bar label, DST regime of that Friday,
                      informative flag, FXCM best offset (3 pairs only) and the three correlations
Reads the pack's data_fxcm read-only for the three pairs that have it.
"""
import sys, gzip
from pathlib import Path
import numpy as np, pandas as pd

PACK = Path(r"D:/Research-Publishing/03-fx-data-artefact")
sys.path.insert(0, str(PACK / "code"))
import fxio, fxclock

OUT = Path(__file__).resolve().parents[1] / "tables" / "switch"; OUT.mkdir(parents=True, exist_ok=True)
LO, HI = pd.Timestamp("2018-09-01"), pd.Timestamp("2019-05-01")
FXCM_PAIRS = {"EURUSD", "USDJPY", "AUDUSD"}
GRIDS = {  # candidate grids, fixed in advance (see addendum)
    "FX": [1e-4, 5e-5], "JPY": [1e-2, 5e-3], "XAUUSD": [1, 0.5, 0.25, 0.1, 0.05], "XAGUSD": [0.1, 0.05, 0.01, 0.005],
    "IDX": [1, 0.5, 0.25, 0.1, 0.05], "WTIUSD": [0.1, 0.05, 0.01], "UDXUSD": [0.01, 0.005, 0.001],
}


def grid_kind(inst):
    if inst in ("XAUUSD", "XAGUSD", "WTIUSD", "UDXUSD"): return inst
    if inst in ("SPXUSD", "NSXUSD", "UKXGBP", "GRXEUR", "JPXJPY"): return "IDX"
    return "JPY" if "JPY" in inst and inst[:3] != "JPX" else "FX"


def on_grid(x, g):
    k = x / g
    return np.abs(k - np.round(k)) < 1e-6


def load_window(inst):
    parts = []
    for y in (2018, 2019):
        d = fxio.read_pair_year(inst, y)
        if d is not None: parts.append(d[(d.t >= LO) & (d.t < HI)])
    return pd.concat(parts, ignore_index=True).drop_duplicates("t").sort_values("t").reset_index(drop=True)


def fxcm_year(pair, y):
    fs = sorted((PACK / "data_fxcm").glob(f"{pair}_m1_{y}_w*.csv.gz"))
    d = pd.concat([pd.read_csv(f, compression="gzip", usecols=["DateTime", "BidClose"]) for f in fs], ignore_index=True)
    d["utc"] = pd.to_datetime(d["DateTime"], format="%m/%d/%Y %H:%M:%S.%f", errors="coerce")
    d["b"] = pd.to_numeric(d["BidClose"], errors="coerce")
    d = d.dropna(subset=["utc", "b"]).drop_duplicates("utc").sort_values("utc").reset_index(drop=True)
    gap = d.utc.diff() / pd.Timedelta(minutes=1)
    r = np.log(d.b).diff() * 1e4; r[gap != 1] = np.nan
    return d.assign(r=r)


def main(inst):
    df = load_window(inst)
    t = df["t"]; day = t.dt.normalize()
    # ---- daily table with grid shares
    kind = grid_kind(inst); cols = {}
    for g in GRIDS[kind]:
        cols[f"grid_{g:g}"] = pd.Series(on_grid(df.c.to_numpy(), g)).groupby(day.to_numpy()).mean()
    dd = pd.DataFrame(cols)
    g = df.groupby(day)
    dd["bars"] = g.size(); dd["first"] = g.t.first().dt.strftime("%H:%M"); dd["last"] = g.t.last().dt.strftime("%H:%M")
    gap = t.diff().shift(-1)
    dd["regime"] = fxclock.dst_regime(dd.index)
    # largest within-day gap starting 15:00-19:00 label time (daily break marker; metals/indices)
    sel = (gap >= pd.Timedelta(minutes=30)) & (t.dt.hour >= 15) & (t.dt.hour < 19) & (gap < pd.Timedelta(hours=20))
    br = pd.DataFrame({"day": day[sel], "start": t[sel].dt.strftime("%H:%M"), "mins": (gap[sel] / pd.Timedelta(minutes=1)).astype(int)})
    br = br.sort_values("mins").groupby("day").last()
    dd["break_start"] = br.start; dd["break_mins"] = br.mins
    dd.index.name = "date"; dd.to_csv(OUT / f"{inst}_days.csv")
    # ---- weekly close / open labels
    s = t; gp = s.diff().shift(-1)
    last = s[(gp > pd.Timedelta(hours=30)) & (gp < pd.Timedelta(hours=80)) & (s.dt.dayofweek == 4)]
    first_after = s[(s.diff() > pd.Timedelta(hours=30)) & (s.diff() < pd.Timedelta(hours=80)) & (s.dt.dayofweek == 6)]
    rows = []
    for l in last:
        wk = (l.normalize() - pd.Timedelta(days=5))               # Sunday that starts this week
        f = first_after[(first_after > l) & (first_after < l + pd.Timedelta(days=4))]
        rows.append(dict(week_start=wk.date(), friday=l.date(), last_label=l.strftime("%H:%M"),
                         next_open_label=(f.iloc[0].strftime("%a %H:%M") if len(f) else ""),
                         regime=int(fxclock.dst_regime([l.normalize()])[0])))
    wk = pd.DataFrame(rows)
    # ---- FXCM weekly offset correlations
    if inst in FXCM_PAIRS and len(wk):
        f18, f19 = fxcm_year(inst, 2018), fxcm_year(inst, 2019)
        fser = pd.concat([f18, f19]).drop_duplicates("utc").set_index("utc").r
        cons = np.r_[False, np.diff(t.to_numpy()).astype("timedelta64[m]").astype(int) == 1]
        r = np.r_[np.nan, np.diff(np.log(df.c.to_numpy()))] * 1e4; r[~cons] = np.nan
        h = pd.DataFrame({"label": t, "rh": r}).dropna()
        h["wk"] = h.label.dt.to_period("W-SAT").dt.start_time
        for k in (4, 5, 6):
            h[f"f{k}"] = fser.reindex(h.label + pd.Timedelta(hours=k)).to_numpy()
        cr = []
        for w, gg in h.groupby("wk"):
            row = dict(week_start=w.date())
            for k in (4, 5, 6):
                x = gg[["rh", f"f{k}"]].dropna(); row[f"corr_p{k}"] = x.rh.corr(x[f"f{k}"]) if len(x) > 300 else np.nan
                row["n"] = len(x)
            ks = [k for k in (4, 5, 6) if np.isfinite(row[f"corr_p{k}"])]
            row["best_offset_h"] = max(ks, key=lambda k: row[f"corr_p{k}"]) if ks else np.nan
            cr.append(row)
        wk = wk.merge(pd.DataFrame(cr), on="week_start", how="outer")
    wk.insert(0, "inst", inst); wk.to_csv(OUT / f"{inst}_weeks.csv", index=False)
    print(inst, "days", len(dd), "weeks", len(wk), flush=True)


if __name__ == "__main__":
    for inst in sys.argv[1:]:
        main(inst)
