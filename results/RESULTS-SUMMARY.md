# Results summary

Run date 2026-10-13. Every number below was computed today from raw files and is in the named CSV under `results/tables/`. Returns are one-minute bid-to-bid log returns in basis points (bp). "t" is mean / (sd / sqrt(n)) with one observation per trading day. Sharpe ratios are annualised with sqrt(252) and assume zero cost unless stated. Nothing here is a trading recommendation or a claim of a tradable edge.

## 1. The rollover bar (histdata M1, ten FX pairs)

- In 2015-2026 the bar stamped 16:59 New York is the most negative of all 1,440 minutes of the day for **all ten pairs** (T1b).
- Size and strength, 2015-2026 (T2):

| Pair | Days | Mean of 16:59 bar (bp) | t | Share of days negative | Sum 16:55-17:04 (bp) | t |
|---|---|---|---|---|---|---|
| EURUSD | 2,964 | -0.77 | -27.7 | 72% | -0.99 | -20.2 |
| USDJPY | 2,964 | -1.17 | -32.3 | 77% | -2.22 | -34.5 |
| GBPUSD | 2,959 | -1.24 | -30.1 | 76% | -2.09 | -16.8 |
| AUDUSD | 2,958 | -1.55 | -35.9 | 77% | -3.27 | -34.4 |
| USDCHF | 2,962 | -2.07 | -37.1 | 82% | -3.72 | -39.0 |
| USDCAD | 2,965 | -1.05 | -28.7 | 72% | -2.01 | -29.9 |
| NZDUSD | 2,962 | -2.58 | -36.3 | 82% | -4.56 | -28.4 |
| EURGBP | 2,945 | -1.72 | -37.7 | 80% | -3.66 | -28.2 |
| EURJPY | 2,932 | -1.36 | -36.2 | 78% | -2.30 | -32.2 |
| GBPJPY | 2,935 | -1.68 | -35.3 | 78% | -3.36 | -25.6 |

- The five-minute window 16:55-16:59 (the bar the earlier project flagged) sums to -0.9 to -3.2 bp with t from -22.6 to -39.0. The earlier report's "about -2 bp, t near -35" is consistent with this for the mid-range pairs.
- For comparison, the median |t| of the other 1,439 minutes is about 0.8-1.1 (T1b).
- **It is absent before 2015.** 2009-2014 means of the 16:59 bar are between -0.32 and 0.00 bp; nine of ten pairs have |t| below 2.1 (AUDUSD -4.8). Median return 0.00 and 8-18% of days exactly zero (T2).
- **It is present in every year 2015-2026 for every pair.** Weakest single pair-year t is -3.95 (2015); from 2016 the weakest is -4.4 (T2, fig3).
- Partial rebounds: the 17:05 bar and the 18:00 bar are strongly positive (18:00: +0.28 to +1.24 bp, t up to +20.0). Net over 16:55-18:04 the bid is back to about zero for EURUSD (+0.03 bp) but still down 0.4-1.5 bp for the others (T2).
- **Weekday** (T3): Wednesday, the triple-swap day, is no different from other days (for example EURUSD -0.85 bp on Wednesday against -0.62 to -1.00 on other days). Friday shows it too.
- **Bar range** (T2): the 16:59 bar's high-low range is 1.9-4.4 bp against 0.7-1.2 bp for the 16:30-16:54 average in 2015-2026.
- Gold and silver show the same pattern (16:59 bar -0.81 bp, t -16.6 and -3.65 bp, t -20.5 in 2015-2026; nothing in 2009-2014). They have a one-hour daily break after 17:00 and were not analysed further.
- Other minutes with large negative t in 2015-2026 include 08:29 and 09:59 New York - the minute before scheduled US releases - which fits the same bid-only mechanism (T7). Not analysed further.

## 2. Mechanism

Second source, FXCM candles with bid and ask, stamped in UTC (F2, F2b, fig5):

| Pair, 2015-2023 | Bid return at 16:59 (bp) | Ask return | Mid return | Spread 10:00-15:59 (bp) | Spread at 16:59 | Spread 17:00-17:04 | Spread 18:00-18:59 |
|---|---|---|---|---|---|---|---|
| EURUSD | -0.88 | +0.76 | -0.06 | 0.18 | 2.63 | 2.44 | 0.34 |
| USDJPY | -1.10 | +0.82 | -0.14 | 0.23 | 3.09 | 2.95 | 0.44 |
| AUDUSD | -1.37 | +1.15 | -0.11 | 0.40 | 4.55 | 4.55 | 0.66 |

(Averages of yearly values.) The bid falls and the ask rises by nearly the same amount; the spread is roughly ten to fifteen times its daytime level at 16:59.

- The mid is not perfectly flat: yearly t-statistics for the mid at 16:59 range from +0.6 to -3.6, and are below -2 in 11 of 36 pair-years. The mid move is about a tenth of the bid move.
- FXCM shows the bid drop in 2012-2014 as well (EURUSD -0.38 bp, AUDUSD -1.13 bp), when histdata shows none. So the market did not change in 2015; **histdata's feed did**.
- The vendor's own tick files (tick_summary): in 2012-07 and 2013-01 the spread is a constant (EURUSD 1.38 and 1.28 bp at every time of day; bid and ask returns identical). In 2017 and 2024 the spread varies and the 16:59 pattern is bid about -0.4 to -2.8 bp, ask +0.1 to +2.6 bp. Seven sample months per pair, three pairs; about 22 days per month, so single-month numbers are noisy.

## 3. The clock

What the vendor documents: fixed EST, no daylight saving (UTC-5 all year). What the files show:

| Files | Regime | Friday last-bar label (share of 80-100 pair-years) | Label of the morning volatility spike | Best offset against the UTC source |
|---|---|---|---|---|
| 2009-2018 | 0: US and EU winter | 16:59 (100%) | 08:30 | +5 h (21 of 21 pair-years) |
| 2009-2018 | 1: US summer, EU winter | 16:59 (99%) | 08:30 | +4 h (21 of 21) |
| 2009-2018 | 2: both summer | 16:59 (100%) | 08:30 | +4 h (21 of 21) |
| 2019-2026 | 0 | 16:59 (100%) | 08:30 | +5 h (15 of 15) |
| 2019-2026 | 1 | **15:59 (97.5%)** | **07:30** | **+5 h (15 of 15)** |
| 2019-2026 | 2 | 16:59 (100%) | 08:30 | +4 h (15 of 15) |

(T5b for the first two columns, ten FX pairs; F1 for the last, three pairs, 2012-2023.)

- A true fixed UTC-5 clock would show the close at 15:59 and the spike at 07:30 in **both** regimes 1 and 2. It never does in regime 2.
- Against the UTC-stamped source, one-minute return correlation is 0.965-0.994 at the right offset and between -0.02 and +0.03 at the wrong ones, in every one of the 108 pair-year-regime cells (F1).
- Week by week (F1b, T6): the last New-York-style week ends Friday 2 Nov 2018; the first European-style week ends Friday 15 Mar 2019. The switch lies between those dates; any date in that window gives identical conversions.
- Share of trading days on which "label + 5 h = UTC" is an hour out: about 65% in 2009-2018 and about 59% in 2019-2026.
- Treating all years as New York wall clock (what the earlier project's fix did) is wrong on about 7% of trading days from 2019: the three or four weeks a year when the US has changed clocks and Europe has not.
- Gold and silver follow the same two-era pattern.

## 4. The demonstration rule (pre-specified in `code/PRESPEC.txt`)

Rule: sell at 16:00 New York, buy back at 17:00, every trading day, zero cost, bid-to-bid.

2015-2026, annualised Sharpe (mean bp per day) [t] (demo_rule_2x2):

| Pair | Documented clock, no mask | Documented clock, masked | True clock, no mask | True clock, masked |
|---|---|---|---|---|
| EURUSD | 0.63 (0.28) [2.2] | -0.01 (-0.01) [-0.0] | **3.09** (1.02) [10.6] | 0.35 (0.11) [1.2] |
| USDJPY | 0.15 (0.07) [0.5] | -1.05 (-0.47) [-3.6] | **2.05** (0.96) [7.1] | -1.14 (-0.52) [-3.9] |
| GBPUSD | 0.92 (0.43) [3.2] | -0.32 (-0.14) [-1.1] | **4.07** (1.61) [14.0] | 0.29 (0.11) [1.0] |
| AUDUSD | 1.72 (1.06) [5.9] | 0.26 (0.15) [0.9] | **5.34** (2.49) [18.4] | 0.89 (0.40) [3.0] |
| USDCHF | 2.35 | 0.55 | **5.38** | 0.92 |
| USDCAD | 1.43 | 0.41 | **3.71** | 0.83 |
| NZDUSD | 1.93 | 0.16 | **5.54** | 0.86 |
| EURGBP | 3.08 | 1.02 | **7.72** | 1.69 |
| EURJPY | 0.25 | -0.93 | **2.60** | -0.75 |
| GBPJPY | 0.39 | -1.09 | **3.19** | -0.81 |

- Both outcomes that would have counted against the claim did not occur: masking removes most of the result, and the documented clock is much weaker than the true clock.
- **Not everything vanishes.** With the mask, EURGBP is still 1.69 (t 5.8), AUDUSD 0.89 (t 3.0), and the yen pairs are significantly negative. A ten-minute mask is not a complete cure (spreads begin widening before 16:55).
- Whole sample 2009-2026, true clock, no mask: Sharpe 0.56 to 4.66. In 2009-2014 alone the rule is mostly negative (-2.40 to +1.84), because the artefact is not in the data yet.
- Year by year (demo_rule_by_year), for example AUDUSD true clock no mask: 2.6 to 10.3 in every year 2015-2026; masked: -0.9 to +3.2.
- Hour scan (hour_scan, fig7), true clock, 2009-2026, t of "long the hour": hour 16 is -2.4 to -19.7 for all ten pairs; hour 18 is +2.4 to +12.1. With the wide mask (16:55-18:04) hour 18 falls to 0.5-4.1.

The same rule priced on the second source (F3) - added after the pre-specified run:

| Pair, 2015-2023 | Bid-to-bid Sharpe | Mid-to-mid Sharpe | Executable (sell at bid, buy back at ask) | Mean spread paid at exit (bp) |
|---|---|---|---|---|
| EURUSD | 4.39 (t 13.3) | 0.54 (t 1.6) | -3.76 (t -11.4) | 2.7 |
| USDJPY | 1.78 (t 5.4) | -2.09 (t -6.3) | -6.58 (t -20.0) | 3.2 |
| AUDUSD | 5.22 (t 15.8) | 0.66 (t 2.0) | -4.95 (t -15.0) | 4.9 |

The profit a bid-only backtest reports is about half the spread widening; a real trade pays the whole widened spread.

## 5. How the two problems interact

- On the documented clock, a rule keyed to "the last New York hour" trades the wrong hour on about 60% of days, so it meets the artefact only in winter. The fake edge is diluted (Sharpe 0.15-3.08) but not removed.
- Fixing the clock concentrates the artefact in one hour and the fake edge **grows** (2.05-7.72). This matches what the earlier project saw: the result appeared after the clock was corrected.
- A mask applied on the wrong clock masks the wrong minutes for most of the year.

## 6. Things that did not work or were not done

- Dukascopy as a second source: HTTP 503.
- OpenAlex: quota exhausted; literature search relied on Crossref and direct fetches.
- BIS flash-event PDF, two broker help pages and one RBA page could not be opened.
- Only three pairs were checked against FXCM; only seven months of vendor ticks per pair.
- Stock-index and oil series in the archive were not analysed.
- The cause of the 2015 change and the exact day of the 2018-19 clock change are not established.
- 2023 has large data holes (for EURUSD, 198 days with a 16:59 bar against about 257 in other years).

## 7. How to detect and fix it - checklist for any user of this data

1. **Find the weekly close in your file.** Take the last bar before each weekend. FX closes at 17:00 New York. If that bar is stamped 16:59 in January **and** in July, your labels follow daylight saving, whatever the documentation says. `fxclock.diagnose_clock(labels)` does this.
2. **Check the US-only weeks.** In the two or three weeks of March and the one week of late October / early November when the US has changed clocks and Europe has not: if the last Friday bar is 16:59 you are on New York time; if it is 15:59 you are on the European calendar.
3. **Confirm with a second anchor.** The minute with the largest average absolute return between 07:00 and 10:00 should be 08:30 New York. If it moves to 07:30 in some weeks, your clock is off in those weeks.
4. **Convert once, with a time-zone database, not a fixed offset.** `fxclock.label_to_utc(labels)`; never "+5 hours". Re-run the weekly-close check on the converted data: it should be 16:59 New York in every week.
5. **Look at every minute of the day before testing any rule.** Compute the mean one-minute return and its t for each of the 1,440 minutes. Any minute with |t| above about 6 is a data property, not an opportunity. Check 16:59, 17:00, 17:05, 18:00, 08:29 and 09:59 New York first.
6. **Know which side of the quote you have.** Bid-only bars move when the spread moves. If the vendor has tick files with the ask, sample a month and plot the spread by minute of day.
7. **Mask as a diagnostic.** Re-run any result with bars 16:55-18:04 New York removed (`fxclock.rollover_mask(utc, before=5, after=65)`). If the result depends on those bars, it is the artefact. If it survives, that is still not proof: the mask does not remove all of the spread drift.
8. **Price at least one test at executable prices.** Sell at the bid, buy at the ask, using a source that has both. A result that needs mid or bid-only prices to be positive is not a result.
9. **Do not rely on multiple-testing corrections to catch this.** They guard against luck. This effect is real in the data and passes them easily.
10. **Check for regime changes in the feed.** Split by year. An effect that switches on in one calendar year across every pair is more likely a change in the data than in the market.
