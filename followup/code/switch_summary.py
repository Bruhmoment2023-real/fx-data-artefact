import glob, os
import numpy as np, pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.max_rows", 200)
T = "tables/switch/"
insts = sorted(os.path.basename(f).split("_")[0] for f in glob.glob(T + "*_weeks.csv"))
print("instruments", insts)
W = pd.concat([pd.read_csv(T + f"{i}_weeks.csv") for i in insts]); W["friday"] = pd.to_datetime(W.friday)
W = W[(W.friday >= "2018-10-15") & (W.friday <= "2019-03-29")]
# 1. Friday last-bar label in informative weeks (regime 1), per instrument
inf = W[W.regime == 1]
print("\nINFORMATIVE Fridays (US on DST, Europe not): last-bar label")
print(inf.pivot_table(index="friday", columns="inst", values="last_label", aggfunc="first").to_string())
print("\nNon-informative Fridays: share with last label 16:59 by instrument")
print(W[W.regime != 1].groupby("inst").last_label.apply(lambda s: round((s == "16:59").mean(), 3)).to_string())
print("\nAll Fridays in window with a last label other than 16:59:")
print(W[W.last_label != "16:59"][["inst", "friday", "last_label", "regime"]].to_string(index=False))
# 2. FXCM offset
F = W[W.best_offset_h.notna()]
if len(F):
    print("\nFXCM weekly best offset (hours), informative weeks and neighbours")
    print(F.pivot_table(index="friday", columns="inst", values="best_offset_h", aggfunc="first").to_string())
# 3. grid change points
rows = []
for i in insts:
    d = pd.read_csv(T + f"{i}_days.csv", parse_dates=["date"]).set_index("date")
    for g in [c for c in d.columns if c.startswith("grid_")]:
        s = d[g].dropna(); best = (0, None)
        for k in range(10, len(s) - 10):
            a, b = s.iloc[k - 10:k].mean(), s.iloc[k:k + 10].mean()
            if abs(a - b) > best[0]: best = (abs(a - b), s.index[k], a, b)
        rows.append(dict(inst=i, grid=g, jump=round(best[0], 3), first_day_after=str(best[1])[:10] if best[1] is not None else None,
                         before=round(best[2], 3) if best[1] is not None else None, after=round(best[3], 3) if best[1] is not None else None))
G = pd.DataFrame(rows); G.to_csv("tables/switch_gridchange.csv", index=False)
print("\nGRID CHANGE POINTS (largest 10-day-before vs 10-day-after jump)"); print(G.sort_values(["inst", "jump"], ascending=[True, False]).groupby("inst").head(2).to_string(index=False))
W.to_csv("tables/switch_weeks_window.csv", index=False)
