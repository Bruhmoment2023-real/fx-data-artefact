# Robustness - every instrument on disk, size by year, wider and asymmetric masks

SECONDARY analysis (pack headline unchanged). Specification: `ADDENDUM-2026-10-13.md` section A3, written before the results. Script `code\robustness.py`; log `logs\26_robustness.log`; tables `tables\R1`-`R4`, `R3b`. Inputs: `rerun\results\daily\` (true two-era clock; built from the raw zips, identical to the pack's for the 12 original series). Constraints modelled: histdata one-minute bid-to-bid log returns in bp, one observation per trading day, t = mean/(sd/sqrt n) with no autocorrelation correction, zero cost, Monday-Friday, days with at least 30 bars in the 16:00 hour for the rule.

## 1. Minute-of-day profile for every series on disk (`tables\R1_profile_all_instruments.csv`)

Instruments on disk: 10 FX pairs, XAUUSD, XAGUSD, and index/commodity series SPXUSD, NSXUSD, UKXGBP, GRXEUR, JPXJPY, UDXUSD, WTIUSD (19 in all; the vendor has more instruments, which would need downloads).

- Ten FX pairs: the 16:59 New York bar is the most negative of ~1,440 minutes in 2015-2026 for all ten (rank 1; t -27.7 to -37.7). In 2009-2014 it is not: AUDUSD ranks 5 (t -4.8), USDCAD 43 (t -2.1), the other eight pairs rank 183 to 688 (|t| below 1.3).
- Gold and silver: also rank 1 in 2015-2026 (XAUUSD -0.81 bp, t -16.6; XAGUSD -3.65 bp, t -20.5); nothing in 2009-2014 (t +1.6 and -0.5). Caveat: for metals 16:59 is the bar before a one-hour daily break, so a bar-before-the-break effect cannot be separated from the rollover effect with bid-only bars.
- Japan index series (JPXJPY, file ends 2018): rank 1 at 16:59 in 2015-2018 (-1.56 bp, t -11.7), none in 2009-2014 (t +0.5) - same timing as FX.
- Index, oil and dollar-index series: SPXUSD, NSXUSD, UDXUSD and WTIUSD have no 16:59 effect of the FX kind (16:59 ranks 720, 9, 5 and 763; t +0.1, -3.6, -5.3, +0.2); their most negative minute in 2015-2026 is instead label 17:00 (t -10.4, -18.2, -8.3, -8.8). UKXGBP's is 16:00 (t -11.2) and GRXEUR's 03:25 (t -8.3). I did not analyse why these sit at other minutes (their sessions and breaks differ and changed on 16 Dec 2018, see `open-facts.md`); the clock for them is assumed to follow the two-era rule (supported by their weekly close/open labels). Descriptive only.
- A caution for any reader scanning these profiles: other minutes also reach |t| of 5-19 in some series (for example EURUSD 08:15 and 06:59 in 2009-2014, t +6.3 and -9.8). In 2015-2026, FX pairs have 16-36 minutes with |t| above 4 against a median |t| of 0.8-1.1.

## 2. Size by year (`tables\R2_size_by_year.csv`; ten FX pairs, mean of the 16:59 bar, bp)

| Year | Weakest pair | Median pair | Strongest pair | Pairs with t < -2 | Median share of days negative |
|---|---|---|---|---|---|
| 2009-2013 | -0.48 to -0.18 | -0.11 to +0.08 | up to +0.61 | 0 of 10 each year | 0.36-0.50 |
| 2014 | -0.11 | -0.24 | -0.65 | 7 of 10 | 0.53 |
| 2015 | -0.48 | -1.29 | -2.18 | 10 of 10 | 0.72 |
| 2016 | -0.83 | -1.90 | -3.36 | 10 | 0.81 |
| 2017 | -0.84 | -2.14 | -3.50 | 10 | 0.87 |
| 2018 | -0.73 | -1.99 | -4.04 | 10 | 0.81 |
| 2019 | -0.42 | -1.23 | -2.52 | 10 | 0.78 |
| 2020 | -0.54 | -0.90 | -2.42 | 10 | 0.66 |
| 2021 | -0.93 | -1.57 | -2.91 | 10 | 0.78 |
| 2022 | -1.27 | -1.73 | -3.76 | 10 | 0.76 |
| 2023 | -0.87 | -1.17 | -2.05 | 10 | 0.80 |
| 2024 | -0.49 | -0.88 | -1.44 | 10 | 0.75 |
| 2025 | -0.71 | -1.17 | -2.84 | 10 | 0.71 |
| 2026 (to Oct) | -0.59 | -1.25 | -2.74 | 10 | 0.82 |

- Size is not constant: the median pair peaks at about -2 bp in 2016-2018, falls to about -0.9 bp in 2020 and 2024, and recovers in 2021-2022 and 2025-2026. The t-statistics stay between -3.95 (2015, weakest) and -21.7 for every pair-year from 2015.
- 2014 already shows t < -2 in seven pairs: see `open-facts.md` (onset in autumn 2014; the pack's "absent before 2015" is a good approximation for the pooled 2009-2014 sample but the last months of 2014 carry it).
- Gold: -1.5 bp in 2015, near zero or positive in 2017-2018 (+0.1, +0.4), -0.4 to -1.4 bp from 2019. Silver: negative in all years except 2018 (+2.3 bp, t +5.7, unexplained and not investigated). The metals' 2017-2018 gap is a reminder that the artefact is not constant across instruments.
- 2023 has data holes (fewer days), as the pack notes.

## 3. Masks on the pre-specified rule: does a wider mask remove the residual? (`tables\R3_mask_grid_rule.csv`, `R3b_mask_verdict.csv`)

Rule: short the New York hour 16:00-17:00 (true clock). Mask: bars from 17:00 minus b minutes to 16:59 set to zero (b = 0 is the unmasked rule; b = 5 is the pack's narrow mask). The stored minute window starts at 16:30, so b cannot exceed 30. Because the rule ends at 17:00, minutes after 17:00 do not enter it. Pre-specified criterion: a mask removes the residual for a pair if |t| < 2 in 2015-2026; a mask is called effective only if at least 8 of 10 pairs meet this at that b and every wider b.

Sharpe (t) in 2015-2026:

| Pair | none | b=5 | b=10 | b=15 | b=20 | b=25 | b=30 |
|---|---|---|---|---|---|---|---|
| EURUSD | 3.09 (10.6) | 0.35 (1.2) | 0.21 (0.7) | 0.24 (0.8) | 0.31 (1.1) | 0.19 (0.6) | 0.03 (0.1) |
| USDJPY | 2.05 (7.1) | -1.14 (-3.9) | -0.98 (-3.4) | -1.17 (-4.0) | -1.14 (-3.9) | -1.26 (-4.3) | -0.89 (-3.1) |
| GBPUSD | 4.07 (14.0) | 0.29 (1.0) | 0.31 (1.1) | 0.47 (1.6) | 0.64 (2.2) | 0.44 (1.5) | 0.16 (0.6) |
| AUDUSD | 5.34 (18.4) | 0.89 (3.0) | 0.88 (3.0) | 0.86 (3.0) | 0.86 (3.0) | 1.01 (3.5) | 0.41 (1.4) |
| USDCHF | 5.38 (18.5) | 0.92 (3.2) | 1.01 (3.5) | 0.80 (2.7) | 0.62 (2.1) | 0.55 (1.9) | 0.33 (1.1) |
| USDCAD | 3.71 (12.8) | 0.83 (2.9) | 0.80 (2.7) | 0.75 (2.6) | 0.75 (2.6) | 0.83 (2.9) | 0.72 (2.5) |
| NZDUSD | 5.54 (19.1) | 0.86 (3.0) | 0.68 (2.3) | 0.69 (2.4) | 0.64 (2.2) | 0.68 (2.3) | 0.29 (1.0) |
| EURGBP | 7.72 (26.5) | 1.69 (5.8) | 1.15 (3.9) | 0.59 (2.0) | 0.40 (1.4) | 0.42 (1.5) | 0.10 (0.3) |
| EURJPY | 2.60 (8.9) | -0.75 (-2.6) | -0.80 (-2.8) | -1.02 (-3.5) | -0.92 (-3.2) | -1.12 (-3.9) | -0.90 (-3.1) |
| GBPJPY | 3.19 (11.0) | -0.81 (-2.8) | -0.76 (-2.6) | -0.79 (-2.7) | -0.70 (-2.4) | -0.93 (-3.2) | -0.71 (-2.4) |

Verdict by mask (ten pairs; `R3b_mask_verdict.csv`):

| b (minutes before 17:00) | Pairs with abs t < 2 | Mean Sharpe | Range of Sharpe | Effective by the pre-specified criterion |
|---|---|---|---|---|
| 0 | 0 | 4.27 | 2.05 to 7.72 | no |
| 5 | 2 | 0.31 | -1.14 to 1.69 | no |
| 10 | 2 | 0.25 | -0.98 to 1.15 | no |
| 15 | 2 | 0.14 | -1.17 to 0.86 | no |
| 20 | 2 | 0.15 | -1.14 to 0.86 | no |
| 25 | 4 | 0.08 | -1.26 to 1.01 | no |
| 30 | 6 | -0.05 | -0.90 to 0.72 | no |

Reading:

1. **No tested mask meets the pre-specified criterion.** Widening from 5 to 30 minutes removes the residual for EURGBP (t 5.8 to 0.3), GBPUSD, NZDUSD, USDCHF and AUDUSD (t 3.0 to 1.4), but not for the three yen pairs (t -3.1, -3.1, -2.4 at b = 30) and not for USDCAD (t 2.5). 6 of 10 pairs are inside |t| < 2 at b = 30. The yen pairs' residual does not shrink as the mask widens (t between -2.4 and -4.3 at every b), so it is not concentrated in the last 30 minutes.
2. **The yen-pair residual is not part of the 2015 artefact.** For 2009-2014, when the 16:59 artefact is absent, the same rule with a 30-minute mask has t = -3.2 (EURJPY), -2.5 (GBPJPY), -1.4 (USDJPY, -3.5 unmasked), and USDCHF has t +2.4 (+4.6 unmasked). So some residual drift in the hour before the rollover predates the artefact and has the same sign. Whether that is real seasonality (the pack's references suggest time-of-day patterns exist) or another data property cannot be settled with bid-only bars. It is a reason not to claim that a ten-minute mask is a cure; the pack already says this.
3. Mean Sharpe falls from 4.27 (none) to about 0.3 (b = 5) and about 0 (b = 30). Most of the unmasked Sharpe is in the last five minutes.
4. Multiplicity: 10 pairs x 7 masks; the criterion asks for 8 of 10 pairs, so a lucky pair does not decide it. No pair is selected.

## 4. Asymmetric masks: the after-side of the rollover (`tables\R4_after_side_residual.csv`)

Residual = sum of one-minute returns from 17:00 + a minutes to 18:29, left unmasked, for a = 5, 35, 60, 65, 89 (the stored window ends 18:29), mean (bp) and t, 2015-2026:

| a (window left) | Mean range over ten FX pairs | t range |
|---|---|---|
| 5 (17:05-18:29) | +0.9 to +4.6 bp | +5.5 to +29.3 |
| 35 (17:35-18:29) | +0.3 to +2.3 bp | +2.1 to +16.6 |
| 60 (18:00-18:29) | +0.3 to +2.5 bp | +2.2 to +16.5 |
| 65 (18:05-18:29) | -0.0 to +0.7 bp | -0.1 to +5.3 |
| 89 (18:29 only) | -0.0 to +0.0 bp | -0.8 to +1.2 |

The bid rebounds after 17:00 (17:05 and 18:00 bars) and the rebound is not complete by 18:05 for most pairs (t above 2.5 for seven pairs at a = 65, USDJPY about zero, USDCAD and EURJPY below 2). A symmetric 16:55-17:04 mask leaves a large positive after-window; a mask covering 17:00 to about 18:29 would be needed to remove it, and no tested window reaches the point where it is clearly empty except the single last minute. For a long-the-hour-18 rule the artefact therefore spans at least 18:00-18:29. Indices and gold: gold shows the same shape (t +5.3 at a = 5, +4.2 at a = 65), SPXUSD, NSXUSD and UDXUSD show nothing after 17:00 (|t| below 2).

## 5. What this does and does not establish

- Size by year, instrument coverage and mask grid are reported in full; nothing was dropped. All numbers regenerate with `python code\robustness.py`.
- Not established: the cause of the residual in the yen pairs and USDCAD; the behaviour for b above 30 (needs the 16:00-16:30 minutes in the daily stage; ready to run by extending `build_daily.py`'s window); anything on instruments the vendor has but which are not on disk.
- Index and oil series are on a different session clock; their rows are descriptive.
