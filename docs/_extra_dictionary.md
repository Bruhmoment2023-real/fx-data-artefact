# Paper-specific data (outside `bibliometrics\`)

Meanings below are taken from column names and from `code\README.md`; units are stated only where the name carries them (`_bp` = basis points, `t` = t-statistic of the mean, `n` = count of observations). Check `code\` before relying on a definition not spelled out in the README.

## Raw inputs (third-party; do not redistribute)

| Path | Source and access date | Size / rows | Content and problems |
|---|---|---|---|
| `D:\Malaysian-SNR\phase3\data\histdata_zips\*.zip` (read-only, outside this folder) | HistData.com free M1 files, downloaded for the earlier Malaysian-SNR project; read by `code\fxio.py` | 499 zips (pair-year files, 2009-2026) | Generic ASCII M1 bars `DateTime;Open;High;Low;Close;Volume`, all prices on the **bid** side; documented as EST without DST, but timestamps follow DST (see `01-prior-work.md`); volume is zero. |
| `data_ticks\*.zip` | HistData.com tick files (generic ASCII), fetched 2026-10-13 with `code\fetch_ticks.py` | 21 zips (EURUSD, USDJPY, AUDUSD; 2012-07, 2013-01, 2017-01, 2017-07, 2024-01, 2024-03, 2024-07), about 188 MB | Tick rows `DateTime,Bid,Ask,Volume`; the only HistData product with ask quotes. |
| `data_fxcm\<PAIR>_m1_<year>_wNN.csv.gz` | FXCM public candle archive (https://github.com/fxcm/MarketData), fetched 2026-10-13 with `code\fetch_fxcm.py`, about 245 MB | 1,888 weekly files | Columns `DateTime, BidOpen, BidHigh, BidLow, BidClose, AskOpen, AskHigh, AskLow, AskClose`; README says timestamps are UTC; free for personal use under FXCM's EULA (not read). |

## Derived results

| Path | Rows x columns (checked 2026-10-17) | Variables |
|---|---|---|
| `results\minute_stats\<PAIR>.parquet` (12 files) | EURUSD 388,784 x 13 | One row per (pair, year, dst state, weekday, label minute): n_bars (bars), n (returns), s (sum of the one-minute bid-to-bid log return, bp), ss (sum of squares), sabs (sum of absolute returns), s_oc and ss_oc (open-to-close return sums), s_rng (sum of bar range, bp); sufficient statistics for means and t-statistics (`codeuild_minute_stats.py`) |
| `results\daily\<PAIR>_{fixed_est,new_york,two_era}.parquet` (3 x 12 pairs) | EURUSD two_era 5,542 x 29 | One row per New York calendar date: h00..h23 = sum of one-minute bid-to-bid returns r (bp) in each New York hour; n16 = bars in hour 16; mA, mB, mC = summed r in 16:55-16:59, 17:00-17:04 and 17:05-18:04 New York (the mask windows). The three files differ only in the clock used to place bars: two_era (measured, "true"), fixed_est (vendor-documented), new_york (New York wall clock, all years). r = 1e4 ln(close_t / close_t-1), left empty across gaps over 30 minutes (`codeuild_daily.py`) |
| `results\daily\<PAIR>_win.parquet` | EURUSD 517,592 x 5 | One row per (date, New York minute) for 16:30-18:29 on the true clock: dow, minute, r (minute return, bp), rng (bar range, bp) |
| `results\daily\<PAIR>_nyprofile.parquet` | EURUSD 129,603 x 9 | Per (year, weekday, New York minute) on the true clock: n_bars, n, s, ss, sabs, s_rng (counts and sums as above) |
| `results\tables\T1_minute_profile_ny.csv` | 51,564 x 10 | pair, sample, ny_minute, hhmm_ny, n, mean_bp, sd_bp, t, mean_abs_bp, mean_range_bp |
| `results\tables\T1b`, `T2`, `T3`, `T4`, `T5`, `T5b`, `T6`, `T7` | 36 x 14, 252 x 24, 180 x 25, 4,202 x 12, 648 x 12, 6 x 11, 918 x 6, 180 x 11 | rollover-bar statistics by pair, year, weekday and minute (`r1659_mean`, `r1659_t`, ...), clock-convention evidence (`friday_last_bar_label`, `sunday_first_bar_label`, `morning_peak_label`), weekly close/open labels |
| `results\tables\F1`, `F1b`, `F2`, `F2b`, `F3` | 108 x 8, 123 x 6, 36 x 30, 720 x 9, 27 x 8 | FXCM cross-check: correlation of HistData returns with FXCM at +4/+5/+6 h offsets; bid/ask/mid return at 16:59 and 17:00 by year; the rule on bid, mid and ask pricing (`pricing`, `sharpe`, `mean_exit_spread_bp`) |
| `results\tables\demo_rule_2x2.csv`, `demo_rule_by_year.csv`, `hour_scan.csv` | 180 x 10, 720 x 9, 1,680 x 9 | the pre-specified demonstration rule by clock (`clock`) and rollover mask (`mask`): n, mean_bp, sd_bp, t, sharpe |
| `results\tables\tick_summary.csv`, `tick_minute_rollover.csv` | 21 x 19, 2,520 x 10 | tick-level bid/ask/mid returns and spread around 16:59-17:00 New York per pair-month |
| `results\figures\fig1..fig7*.png` | 7 PNG | figures made by `code\make_figures.py` |
| `results\RESULTS-SUMMARY.md` | text | verified key numbers (2026-10-13) |

## Known problems

- HistData bars are bid-only and their clock follows DST in two eras; every result that is not marked "true clock" is on the label clock and says so in its `clock` column.
- The study uses ten FX pairs plus gold and silver from one free vendor, and a second source (FXCM) only for 2012-2023 weekly samples.
- Raw zips live outside this folder (in `D:\Malaysian-SNR`), so a rerun needs that drive present and read-only.
- `followup\` holds a separate full rerun (identical tables, 17 Oct 2026) written by another agent; not touched here.
