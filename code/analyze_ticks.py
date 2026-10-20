"""Step 3: mechanism check with the vendor's own tick files, which carry BOTH bid and ask.

For every tick zip in data_ticks/ (fetched by fetch_ticks.py) build one-minute bars of the last
bid, last ask and mean quoted spread on the true New York clock, then report by New York minute:
    bid return, ask return, mid return (bp) and quoted spread (bp of mid).
If the 16:59 bid drop is a spread effect, the ask must RISE in the same minute and the mid must
barely move.

Outputs: results/tables/tick_minute_rollover.csv   (per pair-month, minutes 16:30-18:29)
         results/tables/tick_summary.csv           (per pair-month: key numbers)
"""
import zipfile
from pathlib import Path
import numpy as np, pandas as pd
import fxclock

ROOT = Path(__file__).resolve().parents[1]
TICKS = ROOT / "data_ticks"; OUT = ROOT / "results" / "tables"; OUT.mkdir(parents=True, exist_ok=True)


def minute_bars(f):
    z = zipfile.ZipFile(f)
    name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    df = pd.read_csv(z.open(name), header=None, names=["dt", "bid", "ask", "v"], usecols=[0, 1, 2],
                     dtype={"dt": str, "bid": "float64", "ask": "float64"})
    t = pd.to_datetime(df["dt"].str.slice(0, 15), format="%Y%m%d %H%M%S")
    df["lab_min"] = t.dt.floor("min")
    df["spr"] = (df.ask - df.bid) / ((df.ask + df.bid) / 2) * 1e4
    g = df.groupby("lab_min", sort=True)
    b = g.agg(bid=("bid", "last"), ask=("ask", "last"), spr_mean=("spr", "mean"), spr_last=("spr", "last"), nt=("bid", "size")).reset_index()
    ny = fxclock.utc_to_ny(fxclock.label_to_utc(b.lab_min))
    b["date"] = ny.tz_localize(None).normalize(); b["minute"] = ny.hour * 60 + ny.minute; b["dow"] = ny.dayofweek
    gap = b.lab_min.diff() / pd.Timedelta(minutes=1)
    for k in ("bid", "ask"):
        r = np.log(b[k]).diff() * 1e4
        r[gap > 30] = np.nan
        b["r_" + k] = r
    b["r_mid"] = (np.log((b.bid + b.ask) / 2)).diff() * 1e4
    b.loc[gap > 30, "r_mid"] = np.nan
    return b


if __name__ == "__main__":
    rows = []; summ = []
    hm = lambda m: f"{m // 60:02d}:{m % 60:02d}"
    for f in sorted(TICKS.glob("*_T_*.zip")):
        pair, _, ym = f.stem.split("_")
        b = minute_bars(f)
        b = b[b.dow < 5]
        day_med = b.spr_mean.median()
        w = b[(b.minute >= 990) & (b.minute < 1110)]
        a = w.groupby("minute").agg(n=("r_bid", "count"), bid_ret=("r_bid", "mean"), ask_ret=("r_ask", "mean"), mid_ret=("r_mid", "mean"),
                                    spread_mean=("spr_mean", "mean"), spread_last=("spr_last", "mean")).reset_index()
        a.insert(0, "month", ym); a.insert(0, "pair", pair); a["hhmm_ny"] = a.minute.map(hm)
        rows.append(a)
        def one(m, col, fn="mean"):
            x = b.loc[b.minute == m, col].dropna()
            return (x.mean() if fn == "mean" else x.std(ddof=1) / np.sqrt(len(x))) if len(x) else np.nan
        def spr(lo, hi):
            return b.loc[(b.minute >= lo) & (b.minute <= hi), "spr_mean"].mean()
        n = int(b.loc[b.minute == 1019, "r_bid"].notna().sum())
        summ.append(dict(pair=pair, month=ym, days_1659=n,
                         bid_ret_1659=one(1019, "r_bid"), ask_ret_1659=one(1019, "r_ask"), mid_ret_1659=one(1019, "r_mid"),
                         se_bid_1659=one(1019, "r_bid", "se"), se_mid_1659=one(1019, "r_mid", "se"),
                         bid_ret_1700=one(1020, "r_bid"), ask_ret_1700=one(1020, "r_ask"), mid_ret_1700=one(1020, "r_mid"),
                         spread_day_median=day_med, spread_1600_1654=spr(960, 1014), spread_1655_1658=spr(1015, 1018),
                         spread_1659=spr(1019, 1019), spread_1700_1704=spr(1020, 1024), spread_1705_1759=spr(1025, 1079),
                         spread_1800_1859=spr(1080, 1139), spread_1900_1959=spr(1140, 1199)))
        print(pair, ym, "minutes", len(b), flush=True)
    pd.concat(rows, ignore_index=True).round(4).to_csv(OUT / "tick_minute_rollover.csv", index=False)
    s = pd.DataFrame(summ).round(4); s.to_csv(OUT / "tick_summary.csv", index=False)
    pd.set_option("display.width", 250); print(s.to_string(index=False))
