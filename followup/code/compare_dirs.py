"""Compare parquet files in two folders (pack vs rerun) for equal content. Usage: compare_dirs.py packdir rerundir [glob]"""
import sys, glob, os
import pandas as pd, numpy as np
a, b = sys.argv[1], sys.argv[2]; pat = sys.argv[3] if len(sys.argv) > 3 else "*.parquet"
ok = True
for f in sorted(glob.glob(os.path.join(b, pat))):
    g = os.path.join(a, os.path.basename(f))
    if not os.path.exists(g): print("MISSING in pack:", os.path.basename(f)); continue
    x, y = pd.read_parquet(g), pd.read_parquet(f)
    same_shape = x.shape == y.shape
    if same_shape:
        num = x.select_dtypes("number").columns
        mx = float(np.nanmax(np.abs(x[num].to_numpy(float) - y[num].to_numpy(float)))) if len(num) else 0.0
        nonnum = [c for c in x.columns if c not in num]
        eq_non = all((x[c].astype(str).to_numpy() == y[c].astype(str).to_numpy()).all() for c in nonnum)
        # NaN pattern
        nan_same = bool((x[num].isna().to_numpy() == y[num].isna().to_numpy()).all())
        res = f"shape {x.shape} maxabsdiff {mx:.3g} nonnum_equal {eq_non} nan_pattern_same {nan_same}"
        ok &= (mx < 1e-9 and eq_non and nan_same)
    else:
        res = f"SHAPE DIFFERS pack {x.shape} rerun {y.shape}"; ok = False
    print(os.path.basename(f), res)
print("ALL IDENTICAL" if ok else "DIFFERENCES FOUND")
