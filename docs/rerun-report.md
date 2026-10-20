# Rerun report - pack pipeline regenerated from the raw files

Run dates 2026-10-13 (first agent for step 1, this agent for the rest) and 2026-10-17 (checks). Everything ran on a copy of the pack's code in `followup\rerun\code\` (SHA-256 of all code files identical to the pack: `rerun\logs\code_sha256_pack.txt` equals `code_sha256_copy.txt`). Outputs went to `followup\rerun\results\`; nothing in the pack or in `D:\Malaysian-SNR` was written. Raw histdata zips were read from `D:\Malaysian-SNR\phase3\data\histdata_zips` (read-only), one pair-year at a time.

## Verdict

- 26 of 26 tests pass (4 of them run against the real archive and were not skipped). `rerun\logs\01_pytest.log`, and a verbose rerun `01b_pytest_verbose.log`: "26 passed in 17.92s".
- All 19 tables regenerated and compared with `results\tables\`: identical (max absolute difference 0, same text columns, same NaN pattern). `rerun\logs\11_compare_tables.log` ("ALL TABLES MATCH").
- Intermediates identical too: 12 minute-statistics parquet files (`04_compare_step1.log`) and 60 daily parquet files (`05_compare_step2.log`), "ALL IDENTICAL".
- All 7 figures are byte-identical to the pack's (SHA-256 compared).
- Nothing was found to be wrong in the pack's pipeline.

## Previous agent's leftovers

The first follow-up agent had started step 1 for 12 symbols. It had finished (exit 0, 956 s wall, 12 parquet files) before this agent resumed; I reused it after verifying it against the pack (identical). No process from that agent or from mine was running when work resumed on 2026-10-17 (checked by command line for python and bash processes touching this folder).

## Versions (`rerun\logs\00_versions.log`)

Python 3.12.10 (pack venv `..\.venv`); numpy 2.5.4, pandas 3.0.6, pyarrow 26.0.0, matplotlib 3.11.2, pytest 9.1.1, tzdata 2026.5, requests 2.34.2, pypdf 6.20.1. Windows 11; machine shared with other agents' jobs throughout, so wall times are inflated compared with the README's figures.

## Steps, one at a time (logs in `rerun\logs\`)

| Step | What ran | Wall | CPU | Peak memory | Result |
|---|---|---|---|---|---|
| tests | `pytest test_fxclock.py` | 18 s | n/a | n/a | 26 passed |
| 1 | `build_minute_stats.py` 12 symbols (10 FX pairs, XAUUSD, XAGUSD) | 956 s (54-114 s per symbol) | not recorded (the first agent's wrapper measured the Windows launcher, not Python) | not recorded | identical to pack |
| 2 | `build_daily.py` in two batches of 6 symbols | 442 s and 674 s | 408 s and 549 s | 237 MB, 229 MB | identical to pack |
| 3 | `analyze_ticks.py` on the pack's 21 tick zips (analysis only, see below) | 245 s | 208 s | 970 MB | `tick_*.csv` identical |
| 4 | `demo_rule.py` | 18 s | 6 s | 144 MB | identical |
| 5 | `analyze_profiles.py` | 135 s | 90 s | 333 MB | identical |
| 6 | `analyze_fxcm.py EURUSD USDJPY AUDUSD` on the pack's FXCM files (analysis only) | 362 s | 305 s | 413 MB | `F1`-`F3` identical |
| 7 | `make_figures.py` | 29 s | 24 s | 344 MB | figures byte-identical |

Each job stayed under 10 minutes of CPU and 1 GB of memory. Step 2 batch B took 11 minutes of wall time but 9 minutes of CPU, because the disk was shared.

What was not repeated, and why: the downloads in steps 3 and 6 (`fetch_ticks.py` uses the vendor's public download form, which the follow-up rules treat as a form submission; `fetch_fxcm.py` was reused only through new pairs below). Steps 3 and 6 were therefore re-analysed from the pack's existing raw tick and candle files, read through directory junctions `rerun\data_ticks` and `rerun\data_fxcm` (read-only use). So the "regenerate from raw" test covers the analysis code from the raw tick and candle files onward, and the whole chain from the zip files for steps 1, 2, 4, 5, 7.

## README "ready to run" list

| Job | Status |
|---|---|
| All 66 histdata instruments, 2000-2026 | Not run: needs about 1,700 downloads through the vendor's form (rule) and 1.5-2 h. What fits was done instead: every series already on disk. 19 series are on disk (10 FX pairs, XAUUSD, XAGUSD, SPXUSD, NSXUSD, UKXGBP, GRXEUR, JPXJPY, UDXUSD, WTIUSD); `build_daily.py` was run for the 7 non-FX series (275 s and 185 s wall; 243 s and 167 s CPU; 218-225 MB). Used in `robustness.md`. |
| Tick-level mechanism for whole years | Not run: the fetch goes through the vendor's download form. Script is ready (`code\fetch_ticks.py`); needs Sean's or the hub's decision on whether that counts as a form submission. |
| FXCM check for the other pairs | Run for GBPUSD and USDCHF, 2012-2023 (isolated in `followup\fxcm_extra\`, so the three-pair tables above are untouched). Fetch 707 s wall, analysis 170 s wall (149 s CPU, 407 MB). Results below. Not run: USDCAD, NZDUSD, EURGBP, EURJPY, GBPJPY, AUDUSD already covered, so five pairs remain, about 12 minutes of download each. |
| Clean rerun of the earlier masked strategy search | Not run: lives in `D:\Malaysian-SNR`, 2-4 h and over 4 GB. See `malaysian-snr-clock-impact.md` for what was re-derived lightly instead. |

### New secondary result: FXCM for GBPUSD and USDCHF (files `fxcm_extra\results\tables\F1-F3`)

Label this SECONDARY; it extends, and does not replace, the pack's three-pair check.

- Clock: at the correct offset the one-minute return correlation with the UTC-stamped FXCM bid is 0.95 to 0.99 and at the other two offsets it is between -0.02 and +0.03, in all 72 pair-year-regime cells (2 pairs x 12 years x 3 regimes). Regime 1 (US on daylight time, Europe not) shows both +4 and +5 hours as the best offset across years, as the two-era picture predicts (+4 h to 2018, +5 h from 2019).
- Mechanism, 2015-2023 yearly values of the 16:59 New York bar: GBPUSD bid -0.75 to -1.75 bp, ask +0.53 to +1.67 bp, mid -0.28 to +0.08 bp; USDCHF bid -0.71 to -3.22 bp, ask +0.58 to +2.95 bp, mid -0.18 to +0.09 bp. Quoted spread at 16:59 is roughly 6 to 22 times its 10:00-15:59 level (for example USDCHF 2022: 8.6 bp against 0.52 bp; GBPUSD 2023: 2.5 bp against 0.43 bp).
- Pre-2015: FXCM also shows the bid drop and ask rise in 2012-2014 for both pairs (GBPUSD bid -0.19 to -0.69 bp; USDCHF -0.69 to -1.56 bp), consistent with the pack's EURUSD/AUDUSD finding that the market did not change in 2015 and the histdata feed did.
- The demonstration rule priced on FXCM, 2015-2023 (Sharpe, annualised): GBPUSD bid-to-bid 4.80, mid-to-mid -0.15, executable -6.16; USDCHF 4.57, 0.37, -5.08. Same ordering as the pack's three pairs (bid-only large and positive, mid near zero, executable strongly negative). The one mid-to-mid cell that reaches |t| above 2 is USDCHF 2012-2014 (Sharpe 1.51, t 2.63; full sample 2012-2023 Sharpe 0.56, t 1.95), small beside the bid-to-bid 6.31 and reported as it came out.
- Caveat inherited from the pack: FXCM and histdata one-minute bid returns correlate at about 0.99, so these are not independent price sources; only the timestamps and the ask side are independent. FXCM years have day holes (167-254 days with a 16:59 bar per year).
