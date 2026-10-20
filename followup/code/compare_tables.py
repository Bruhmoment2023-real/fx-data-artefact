"""Compare regenerated CSV tables with the pack's tables. Usage: compare_tables.py packdir rerundir"""
import sys, glob, os
import pandas as pd, numpy as np
a, b = sys.argv[1], sys.argv[2]
allok = True
for f in sorted(glob.glob(os.path.join(a, "*.csv"))):
    g = os.path.join(b, os.path.basename(f))
    if not os.path.exists(g): print(f"{os.path.basename(f):45s} NOT REGENERATED"); allok = False; continue
    x, y = pd.read_csv(f), pd.read_csv(g)
    if x.shape != y.shape or list(x.columns) != list(y.columns):
        print(f"{os.path.basename(f):45s} SHAPE/COLUMNS DIFFER pack {x.shape} rerun {y.shape}"); allok = False; continue
    num = x.select_dtypes("number").columns
    mx = float(np.nanmax(np.abs(x[num].to_numpy(float) - y[num].to_numpy(float)))) if len(num) else 0.0
    nn = [c for c in x.columns if c not in num]
    eq = all((x[c].fillna("").astype(str).to_numpy() == y[c].fillna("").astype(str).to_numpy()).all() for c in nn)
    nan_same = bool((x[num].isna().to_numpy() == y[num].isna().to_numpy()).all()) if len(num) else True
    ok = mx < 1e-6 and eq and nan_same
    allok &= ok
    print(f"{os.path.basename(f):45s} rows {len(x):6d}  max|diff| {mx:.2g}  text_equal {eq}  nan_same {nan_same}  {'OK' if ok else 'DIFF'}")
print("ALL TABLES MATCH" if allok else "SOME TABLES DIFFER OR MISSING")
