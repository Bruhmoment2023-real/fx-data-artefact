# Code

Python 3.12, packages: numpy, pandas, pyarrow, matplotlib, pytest, tzdata, requests. Install with `pip install -r ..equirements.txt`.
All scripts are run from this folder. Raw data is read-only and processed one pair-year at a time.

## Release-ready (the part other people can reuse)

| File | Purpose |
|---|---|
| `fxclock.py` | `label_to_utc` (clock conversion, four conventions), `utc_to_ny`, `rollover_mask`, `mask_returns`, `dst_regime`, `diagnose_clock` (detect the convention from timestamps alone). No I/O, no global state. |
| `test_fxclock.py` | 26 tests: both eras, both daylight-saving transitions, the US-only weeks, the mask, and four tests against real files (skipped if the archive is absent). Run: `python -m pytest -q test_fxclock.py`. Result on 2026-10-13: 26 passed. |

Minimal use:

```python
import pandas as pd, fxclock
utc = fxclock.label_to_utc(df["label"])          # df["label"]: naive histdata timestamps
keep = ~fxclock.rollover_mask(utc, before=5, after=65)   # drop 16:55-18:04 New York
print(fxclock.diagnose_clock(df["label"]))       # which clock is this file on?
```

## Analysis pipeline (run in this order)

| Step | Command | Reads | Writes | Measured time |
|---|---|---|---|---|
| 1 | `python build_minute_stats.py EURUSD USDJPY GBPUSD AUDUSD` | raw zips | `results/minute_stats/` (label clock) | about 60-95 s per pair |
| 2 | `python build_daily.py EURUSD USDJPY GBPUSD AUDUSD` | raw zips | `results/daily/` (three clocks, rollover window, New York profile) | about 60 s per pair |
| 3 | `python fetch_ticks.py EURUSD:2017:1 ...` then `python analyze_ticks.py` | histdata public form | `data_ticks/`, `results/tables/tick_*.csv` | download about 10 s per file; analysis about 3 min for 21 files |
| 4 | `python demo_rule.py` | `results/daily/` | `demo_rule_2x2.csv`, `demo_rule_by_year.csv`, `hour_scan.csv` | seconds |
| 5 | `python analyze_profiles.py` | intermediates + raw EURUSD for T6 | `T1` to `T7` tables | about 2 min |
| 6 | `python fetch_fxcm.py EURUSD:2012-2023 ...` then `python analyze_fxcm.py EURUSD USDJPY AUDUSD` | FXCM public candles | `data_fxcm/`, `F1` to `F3` tables | download about 1.5 min per pair-year; analysis about 2 min per pair |
| 7 | `python make_figures.py` | tables | `results/figures/fig1` to `fig7` | seconds |

`fxio.py` is the streaming reader. `PRESPEC.txt` is the frozen rule definition.

## Ready to run, not run (heavier)

| Job | Command | Expected | Why not run |
|---|---|---|---|
| All 66 histdata instruments, 2000-2026 | First download the missing zips with the earlier project's fetcher, then steps 1, 2, 4, 5 with all symbols | Download about 3 s per file, roughly 1,700 files, about 1.5-2 h; analysis about 2 min per symbol | Download volume; ten pairs already make the point |
| Tick-level mechanism for whole years | `python fetch_ticks.py EURUSD:2016:1 ... EURUSD:2016:12` then `analyze_ticks.py` | 10-25 MB per pair-month; analysis about 10 s per file | Seven sample months per pair were enough to see the mechanism |
| FXCM check for all ten pairs | `python fetch_fxcm.py USDCHF:2012-2023 ...` then `analyze_fxcm.py` | About 18 min download and 2 min analysis per pair | Time |

## Data folders

- `data_ticks/` (188 MB) and `data_fxcm/` (245 MB) are third-party downloads. Do not redistribute them. They can be deleted and re-fetched with the scripts.
