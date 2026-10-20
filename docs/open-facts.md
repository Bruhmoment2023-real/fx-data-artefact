# Open facts - (a) when the clock convention switched, (b) why the artefact starts around 2015

Pre-specifications are in `ADDENDUM-2026-10-13.md` (A1, A1b, A2), written before these results were computed. All of this is SECONDARY; the pack's pre-specified headline (demonstration rule, `code\PRESPEC.txt`) is unchanged. Scripts: `code\switch_date.py`, `code\switch_summary.py`, `code\break_2015.py`. Tables: `tables\switch\`, `tables\switch_weeks_window.csv`, `tables\switch_gridchange.csv`, `tables\break_*.csv`. Logs: `logs\40_switch_summary.txt`, `logs\2*.log`.

## (a) The switch of the timestamp convention

### Answer in one paragraph

The labels cannot give a single day. They show the New York convention on Friday 2 Nov 2018 and the Sunday 28 Oct 2018 open, and the European convention from the Sunday 10 Mar 2019 open. In between the two conventions give identical output because New York and Europe are both on winter time, so no label-based test can see the switch. The narrowest interval the labels support is therefore: after the Friday 2 Nov 2018 close and no later than the Sunday 10 Mar 2019 open (about 128 days; this is 5 days narrower at the upper end than the pack's "15 Mar"). A separate, much sharper feed-change signature in seven non-FX series dates a data-source change to the weekend of Fri 14 Dec - Sun 16 Dec 2018, which lies inside that interval. Whether the clock rule changed at exactly that weekend is an inference, not a measurement.

### Evidence (measured here from the raw files)

Informative days are those on which the two conventions predict different labels (US on daylight time, Europe not): the weeks of 29 Oct - 2 Nov 2018 and 11 - 29 Mar 2019 in this window. For the 18 weeks between them both conventions predict the same labels, so they carry no information.

1. Weekly close label, last bar of the Friday (`tables\switch_weeks_window.csv`):
   - Fri 2 Nov 2018 (informative): 16:59 in all 19 series (10 FX pairs, gold, silver, 5 indices, oil, dollar index) - New York convention.
   - Fri 15, 22, 29 Mar 2019 (informative): 15:59 in all 10 FX pairs; 15:58/15:57 gold and silver; SPXUSD, NSXUSD, UDXUSD and WTIUSD close 15:14, 15:14, 14:59 and 15:14-15:45, each one hour earlier than their winter-weeks value (16:14, 16:14, 15:59, 16:14-16:45) - European convention. GRXEUR and UKXGBP follow different session rules and are not used here.
   - Every other Friday in the window: 16:59 in 100% of the ten FX pairs; 95% for gold and silver (the exceptions are the US Thanksgiving day-after, 23 Nov, with an early close).
2. Weekly open label, the Sunday evening (same table, column `next_open_label`):
   - Sun 28 Oct 2018 (informative): 17:00 or 17:01 for all ten FX pairs; gold and silver 18:01 - New York convention.
   - Sun 10 Mar 2019 (informative): 16:00 or 16:01 for AUDUSD, EURGBP, EURJPY, EURUSD, GBPUSD; 17:00 for GBPJPY, NZDUSD, USDCAD, USDCHF, USDJPY (these five are consistent with either convention, if their first quote was an hour after the market opened); gold and silver 17:00 against 18:00 in winter - European convention. A bar stamped 16:00 before the market opens at 17:00 New York is impossible under the New York convention, so five FX pairs, two metals and the S&P and Nasdaq series prove the European convention by this Sunday.
3. Daily gap position (metals and indices only; the ten FX pairs have no daily break): gold's one-hour break starts at label 16:59 on 29 Oct - 1 Nov 2018 and throughout December 2018; from Mon 11 Mar 2019 it starts at 15:58, one hour earlier. The S&P series' break starts at 16:59 to 14 Dec 2018, at 16:14 from Mon 17 Dec, and at 15:14 from Mon 11 Mar 2019 (so the index also shows the hour shift in March 2019).
4. Second source (FXCM, UTC-stamped; EURUSD, USDJPY, AUDUSD; `tables\switch\*_weeks.csv`, column `best_offset_h`): the week of 28 Oct - 2 Nov 2018 correlates best at +4 h (New York convention) for all three pairs; every week from 9 Nov 2018 to 29 Mar 2019 correlates best at +5 h. In the informative weeks of March 2019 +5 h is the European convention (a New York-convention label would need +4 h).
5. Feed-change signature on the weekend 14-16 Dec 2018 (from `tables\switch_gridchange.csv`; first day after the largest 10-day-before versus 10-day-after jump is **Sun 16 Dec 2018** in each case): share of one-minute closes lying on a coarse price grid falls from 100% to 0% (GRXEUR 0.25 grid, JPXJPY 1.0 grid), 98% to 0% (SPXUSD 0.25 grid), 100% to 0.9% (UKXGBP 0.25), 78% to 0% (NSXUSD 0.25), 100% to 8.6% (UDXUSD 0.01), 100% to 12% (WTIUSD 0.01), 19% to 0.2% (XAUUSD 0.05). The S&P series' last bar on Fri 14 Dec 2018 is 16:59, and from Mon 17 Dec the daily break starts at 16:14. No FX pair shows a price-grid signature: the largest jump for any FX pair at any tested grid is 0.048 (noise level), and for the pairs it falls on dates scattered from September 2018 to April 2019. Gold shows the grid change but silver's grid test does not (jump 0.054 on 23 Sep 2018). This is an independent confirmation, on one-minute files, of what a public write-up reports from tick data.
6. Vendor's own text: its FAQ sentence ("Eastern Standard Time (EST) time-zone WITHOUT Day Light Savings adjustments") is word-for-word unchanged in all 16 archived snapshots between 14 Mar 2012 and 14 Mar 2019 (`raw\wayback_faq_*.txt`). The vendor's blog posted "Fix of Free Forex Historical Data Update for December 2018" on 4 Jan 2019: "We've found an error in the previously deployed files. It's fixed now." (`raw\wayback_post_fix_dec2018_*.html`). It does not say what the error was.

### Separate: what is conjecture

- That the clock rule changed at the same moment as the feed (weekend of 16 Dec 2018): consistent with the evidence above and with the public write-up (radiusred/tradedesk-marketdata issue #93 comment, archived in `archive\`), but cannot be tested from labels because winter hides it.
- That the new feed comes from a Swiss/European provider (the write-up says "Europe/Zurich local time minus a fixed 6 h" and matches a Dukascopy cache; Dukascopy could not be reached from here, so this was not re-checked).
- Practical consequence stays as in the pack: any switch date between 3 Nov 2018 and 10 Mar 2019 produces identical conversions, so `fxclock.ERA_SWITCH = 2019-01-01` is a safe convention. If a user wants the "measured" date, 16 Dec 2018 is the best-supported feed-change date, with the caveat above.

## (b) Why the rollover artefact begins around 2015

### Answer

In this data the artefact does not begin on a clean date, and "2015" is a rounding. The 16:59 bar is indistinguishable from zero in most months of 2014 up to September, turns negative in all ten pairs in November 2014 (-0.26 to -1.64 bp), and is negative in all ten pairs in July and August 2015 (monthly t -1.9 to -5.8); some later single months are not (for example USDCAD September 2015, +0.90 bp). At the same time (September 2014 to January 2015) the mean bar range of 16:30-16:54 rises about two- to four-fold and the share of flat bars (high = low) falls by half or more. These look like a change in what the feed is, not in the market. The cause - a change of upstream quote source or of how the vendor builds the bid series - is not documented anywhere I could reach, so it is a hypothesis.

### Evidence

Monthly series built from the raw files for ten pairs, 2013-2016 (`tables\break_monthly.csv`; daily features in `tables\break\`):

1. Mean return of the 16:59 New York bar, bp (selected months; all ten pairs in the CSV):

| Month | EURUSD | USDJPY | GBPUSD | AUDUSD | USDCHF | NZDUSD |
|---|---|---|---|---|---|---|
| 2014-06 | 0.01 | -0.22 | 0.10 | -0.18 | 0.20 | -0.25 |
| 2014-09 | -0.17 | 0.24 | -0.31 | -1.00 | 0.00 | 0.04 |
| 2014-10 | -0.15 | -0.46 | -0.08 | -1.32 | -0.09 | -0.51 |
| 2014-11 | -0.26 | -0.80 | -0.90 | -1.46 | -1.64 | -1.44 |
| 2014-12 | -0.98 | -0.63 | -0.94 | -1.52 | -0.63 | -1.84 |
| 2015-01 | -0.20 | -0.55 | -0.27 | -1.48 | -1.28 | -2.28 |
| 2015-07 | -1.44 | -0.63 | -1.03 | -1.53 | -2.22 | -3.80 |

2. Single-break search (pre-specified: Welch |t| of 12 months before versus 6 months after, candidates 2014-07 to 2015-12), month of the maximum, by pair: EURUSD 2015-07, USDJPY 2014-11, GBPUSD 2014-07 (the edge of the candidate range), AUDUSD 2014-09, USDCHF 2014-11, USDCAD 2015-03, NZDUSD 2014-11, EURGBP 2015-06, EURJPY 2015-03, GBPJPY 2015-04. The estimates are scattered over a year, so no single month is supported; the effect builds up and is noisy in single months.
3. Co-movement with other series (`tables\break_tests.csv`), month of maximum by pair:
   - Mean range of bars 16:30-16:54: 2014-11 to 2015-01 for all ten pairs (seven at 2015-01), |t| 5.3 to 8.7; EURUSD mean 0.49 bp before, 1.19 bp after; AUDUSD 0.94 to 1.69; USDCHF 0.53 to 1.51.
   - Share of bars with high = low: break 2014-10 to 2015-03 for seven pairs (the others scatter from 2014-07 to 2015-09); falls from about 2% of bars to about 0.5-1% (EURUSD 3.9% in June 2014 to 0.8% in November 2014).
   - Range of the 16:59 bar itself: 2015-01 for five pairs, 2014-11 for two, 2015-02 to 2015-08 for the rest.
   - Not changing: decimals used in prices (about 4.9 of 5 digits, 2.9 of 3 for yen pairs; essentially flat, with a dip for AUDUSD to 4.78 in September 2015), bars per day (about 1,325 to 1,355, break t below 2.6), bars in the 16:55-17:04 window (about 8.7 to 9.0), and days with no bar at 17:00-17:04 (identical across pairs, so a calendar/holiday effect of the vendor, not pair-specific).
4. The pre-specified coincidence criterion (at least 8 of 10 pairs with a break within one month of the 16:59 break month) is **not met** by any series, because the 16:59 break month is itself widely scattered; so this analysis does not claim a statistically established common date. The closeness of the range break (2014-11 to 2015-01) and the monthly pattern of the 16:59 mean (onset November 2014) is a post-hoc description.
5. From the pack (not recomputed here beyond the tables): the vendor's own tick files for 2012-07 and 2013-01 carry a constant spread (EURUSD 1.38 and 1.28 bp at every time of day, bid and ask returns identical), whereas 2017 and 2024 files have varying spreads; FXCM bid/ask candles show the bid drop already in 2012-2014 (confirmed here for GBPUSD and USDCHF: `rerun-report.md`). So the market behaviour existed before; the histdata series did not carry it until the feed changed.

### Public record of a source change

Opened: 16 archived snapshots of the vendor's FAQ (Wayback Machine, 2012-03-14 to 2019-03-14) and the 4 Jan 2019 fix post. None of them names a quote provider, a change of provider, or a change in spread handling. The FAQ lists "Recent Posts" titles only; the October 2015 post "Host Provider Change: Concluded!" concerns the web host. The Wayback Machine then refused further connections, so the vendor's monthly update posts for September 2014 to February 2015 were **not read**: they are the best remaining place to look and are listed as the next step (below). No other public statement was found by the literature searches (`novelty-final.md`).

### Conjecture (labelled)

- A change of upstream quote provider or of the bid-construction method in autumn 2014 (consistent with the range and flat-bar changes, and with the 2012-2013 constant-spread tick files).
- The SNB shock of 15 Jan 2015 may add noise to January 2015 values but cannot explain a November 2014 onset.

### Ready to run, not run

- Wayback fetch of the vendor's update posts for Sep 2014 - Feb 2015 (about 12 pages, after the rate-limit cools off).
- Vendor tick files for one month per quarter from 2014-01 to 2015-06 to see when the constant spread ends (`code\fetch_ticks.py` uses the vendor's download form; the rules treat form submissions as not allowed, so this needs a decision).
- Email to the vendor (suggested in `00-STATUS.md`) asking whether the quote source changed.
