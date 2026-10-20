# 02 - Design

## 1. Claims (each tied to the table that tests it)

| # | Claim | Test | Table / figure |
|---|---|---|---|
| C1 | In histdata.com M1 bars, the one-minute bar ending at 17:00 New York (stamped 16:59) has a large negative mean return, far outside the other 1,439 minutes. | Mean and t per New York minute, pooled and by year. | T1, T1b, fig1 |
| C2 | The effect begins in 2015 and is present in every year since. | Same bar by pair and year. | T2, fig3 |
| C3 | It is a quote-side effect, not a price move: the bid falls, the ask rises, the mid barely moves. | (a) histdata's own tick files (bid and ask); (b) FXCM bid/ask candles. | tick_summary, F2, F2b, fig5 |
| C4 | It is not the swap: Wednesdays (triple-swap day) are no different. | Same bar by weekday. | T3 |
| C5 | The timestamps are not the fixed UTC-5 clock the vendor documents. Files to 2018 follow New York wall time; files from 2019 follow UTC-5 / UTC-4 on the European calendar. | (a) label time of the weekly close and reopen; (b) label time of the 08:30 New York volatility spike; (c) minute-by-minute return correlation with a UTC-stamped second source at +4 h, +5 h, +6 h. | T5, T5b, T6, F1, F1b, fig4 |
| C6 | Together these fake a time-of-day edge: a one-line rule shows Sharpe 2 to 8 at zero cost on bid-only bars; it disappears on mid quotes and is strongly negative at executable prices. | Pre-specified rule, 2 x 2 (clock x mask), plus the same rule on FXCM mid and executable prices. | demo_rule_2x2, demo_rule_by_year, F3, fig6 |
| C7 | The clock error and the artefact interact: on the documented clock the artefact is diluted, so fixing the clock makes the fake edge look **stronger**. | Documented-clock versus true-clock columns of the 2 x 2. | demo_rule_2x2, fig6 |

A correction to the starting brief: it described the data as a fixed-offset clock that users wrongly treat as UTC. The raw files show the opposite. The vendor **documents** a fixed offset; the data **follows daylight saving**. A user who obeys the documentation is the one who is an hour out.

## 2. Data

| Item | Detail |
|---|---|
| Primary | histdata.com "Generic ASCII" M1 bars, bid OHLC, raw zips already on disk at `D:\Malaysian-SNR\phase3\data\histdata_zips` (read-only). Years 2009 to 2026-10. |
| Pairs | Headline: EURUSD, USDJPY, GBPUSD, AUDUSD. Extension: USDCHF, USDCAD, NZDUSD, EURGBP, EURJPY, GBPJPY. Clock evidence also uses XAUUSD and XAGUSD. Stock-index and oil series were not analysed (different trading hours). |
| Size | About 6.4 million one-minute bars per pair; about 4,500 trading days. |
| Mechanism check 1 | histdata.com tick files (bid and ask), downloaded today through the public form: EURUSD, USDJPY, AUDUSD for 2012-07, 2013-01, 2017-01, 2017-07, 2024-01, 2024-03, 2024-07. Same vendor. |
| Mechanism and clock check 2 | FXCM public M1 candles with bid and ask OHLC, stamped in UTC, 2012-2023, weekly files. A different publisher. |
| Not obtained | Dukascopy (HTTP 503 from this network). TrueFX and others need an account, which the rules for this work forbid. |

## 3. Method

- **Return.** r_t = 10,000 x ln(close_t / close_(t-1)), bid to bid, assigned to bar t, defined only if bar t-1 is at most 30 minutes earlier. Weekend and holiday gaps never produce a return.
- **Minute-of-day statistic.** For each New York minute, the mean of r_t across trading days and t = mean / (sd / sqrt(n)). One observation per day per minute, so no overlap; no autocorrelation correction is applied.
- **Clock.** Label time is converted to UTC with `fxclock.label_to_utc` (two-era rule), then to New York time with the IANA database. Daylight-saving regime of a date: 0 = US and EU on winter time, 1 = US on daylight time and EU not, 2 = both on summer time.
- **Clock evidence without any second source.** (a) The FX week ends at 17:00 New York; the label time of the last bar on Friday shows which clock the vendor uses. (b) US data releases at 08:30 New York produce a volatility spike; its label time shows the same thing on ordinary days. (c) The Tokyo fixing (09:55 Tokyo, no daylight saving) must move by an hour in a clock that observes daylight saving.
- **Clock evidence with a second source.** Correlate histdata and FXCM one-minute bid returns matched at label + 4 h, + 5 h and + 6 h, by year and regime, and by week inside regime 1.
- **Mask.** Narrow: bars 16:55 to 17:04 New York set to zero. Wide: 16:55 to 18:04.
- **Streaming.** One pair-year in memory at a time (about 400,000 rows). Measured run time about 60 s per pair per pass; peak memory well under 1 GB.

## 4. The demonstration rule (pre-specified)

The exact text is frozen in `code/PRESPEC.txt`. In short:

- **Rule:** every trading day, sell at 16:00 New York and buy back at 17:00 New York. Profit = minus the sum of bid-to-bid one-minute returns in that hour. No cost. No fitted parameter.
- **2 x 2:** clock (vendor-documented fixed EST versus measured two-era) x mask (none versus narrow, applied on the same clock the rule uses).
- **Reported for every pair and every cell:** n, mean, sd, t, annualised Sharpe.
- **Stated in advance as evidence against the claim:** masked not clearly weaker than unmasked; documented clock as strong as true clock.

How "pre" this is, honestly: the rule was written **after** the minute-of-day profile had been seen (so the direction and the hour were chosen knowing where the artefact sits) and **before** any rule profit was computed. That is the right order for a demonstration of an artefact; it would be the wrong order for a claim of a trading edge, and the note should say so.

Deviations from the pre-specification:

- The "wide mask" was listed as an extra. For this rule it is identical to the narrow mask (the extra minutes are after 17:00), so it only appears in the hour scan.
- The same rule on FXCM bid, mid and executable prices was added afterwards as a robustness check and is labelled as such.
- The sample split 2009-2014 / 2015-2026 was added after seeing that the artefact starts in 2015.

## 5. Threats to validity

| Threat | Why it matters | What the design does | What remains |
|---|---|---|---|
| One vendor | The artefact could be a quirk of one feed. | FXCM bid/ask candles show the same bid drop, ask rise and flat mid, 2012-2023, three pairs. | histdata and FXCM one-minute bid returns correlate at about 0.99, so they are not independent price sources; they may share upstream liquidity. Only the time stamps and the ask side are independent. |
| No ask side in the M1 bars | The mechanism would be inferred. | Two ask-side sources (vendor ticks, FXCM). | The vendor's 2012-2013 tick files have a **constant** spread (ask = bid + a fixed amount), so they say nothing about spreads in that era. |
| "Known microstructure" | A referee may say nothing is new. | The note claims the measurement and the consequence, not the mechanism; prior art is cited. | Depends on the reading list in `01-prior-work.md` being completed. |
| The 2015 break is unexplained | It looks like a change of upstream provider or of spread model, but the vendor documents nothing. | Reported as a dated fact, with the constant-spread tick evidence. | Cause is a hypothesis. |
| Era switch date | The second-era clock rule needs a start date. | Bracketed from the data: last New-York-style week ends 2 Nov 2018, first European-style week ends 15 Mar 2019. Any date in between gives identical conversions. | The exact day (a GitHub write-up says 16 Dec 2018) was not verified. |
| Rule chosen after seeing the profile | Selection. | Stated openly; all pairs and cells reported; the claim is that the profit is fake, which selection cannot help. | None for the artefact claim. |
| Residual after masking | With the narrow mask some pairs still show significant hour-16 or hour-17/18 returns (for example EURGBP Sharpe 1.69, USDJPY -1.14 in 2015-2026). | Reported. Spreads start widening before 16:55 and are not back to normal until about 19:00, so a ten-minute mask is not a full cure. | Whether the residual is more spread drift or genuine seasonality cannot be settled without mid quotes for all pairs. |
| t-statistics | Fat tails; days are not perfectly independent. | With t between -28 and -38 no reasonable correction changes the conclusion; share of days negative (72-82%) and medians are reported alongside. | Minutes with |t| of 3 to 6 elsewhere in the day should not be over-read. |
| Data holes | 2023 has months with many missing hours (198 trading days with a 16:59 bar for EURUSD against about 257 in other years). | Returns never span gaps over 30 minutes; day counts are reported per year. | 2023 numbers rest on fewer days. |
| Other bid-only artefacts | Negative bars at 08:29 and 09:59 New York (the minute before scheduled releases) suggest the same mechanism elsewhere. | Listed in T7; not analysed further. | Out of scope for a short note; say so. |
| Sample start | Zips on disk start in 2009; histdata offers data from 2000. | Stated. | Nothing is claimed about 2000-2008. |
| Earlier project numbers | The "Sharpe above 2, vanishes when masked" result from the strategy search came from a run that later crashed. | The note does not need them; the small demonstration here replaces them. | If Sean wants to cite the large search, only configuration-level numbers are valid. |
