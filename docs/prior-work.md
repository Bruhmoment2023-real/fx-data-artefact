# 01 - Prior work and novelty check

Date: 2026-10-13. Every source below is marked with how far it was read:
**[FULL]** full text opened, **[ABS]** abstract or landing page only, **[META]** bibliographic metadata only (Crossref), **[SNIPPET]** seen only as a search-result summary; the page itself could not be opened.

Search coverage and its limits: Crossref (13 + 18 queries), Semantic Scholar batch lookup, GitHub issue and repository search, StackExchange API, direct fetches of vendor pages, one web search. **OpenAlex was unavailable** (shared daily quota exhausted) and the arXiv API returned nothing for "histdata" (it does not search full text). So "no paper found" below means "not found by these searches", not "does not exist".

## 1. Verdict in four lines

1. **The clock problem is already publicly documented by practitioners** - two GitHub write-ups from August and October 2026 - including the fact that it has two eras. It is not in any paper found. The note cannot claim discovery; it can claim independent verification, a longer sample, and tested code.
2. **Bid-only quotes are documented by the vendor itself.** That is not a finding.
3. **Spread widening at the 17:00 New York rollover is common knowledge among FX practitioners and brokers.** That is not a finding either.
4. **What was not found anywhere:** a measurement of how large the resulting bias is in this specific, very widely used free dataset; the fact that it switches on in 2015; a demonstration that it manufactures Sharpe ratios of 2 to 8 for a trivial rule; and the interaction with the clock error. That quantified, reproducible package is the contribution. Novelty of that package: **provisional but plausible**.

## 2. The vendor's own documentation (exact quotes)

Source A - histdata.com FAQ, https://www.histdata.com/f-a-q/ **[FULL]**, fetched 2026-10-13:

> "What is the timeZone of the dates in the .csv files? The timezone of all data is: Eastern Standard Time (EST) time-zone WITHOUT Day Light Savings adjustments."

> "About the price data? All timeframes that are bar based, like M1 (1 Minute Bar) Data and Tick (1 Second Bar) Data, the bar prices: Open, High, Low, Close in the data files are based on the tick Bid price."

> "And, the spread information? The Ask price is only included in the Tick data of the Generic ASCII format. With both Bid and Ask you'll have the spread value for each specific tick."

> "Is the data reliable? Since it's free data, you'll not get from us any kind of warranty or certification. Use the data at your own will and risk."

> "No volume information? Why? Trading Volumes, in forex, are not aggregated and the only volume that you can find is the Broker Specific Volumes. So, therefore, we decided to remove the volume information from the delivered data."

Source B - histdata.com "Data Files - Detailed Specification", https://www.histdata.com/f-a-q/data-files-detailed-specification/ **[FULL]**:

> Generic ASCII M1 row fields: "DateTime Stamp;Bar OPEN Bid Quote;Bar HIGH Bid Quote;Bar LOW Bid Quote;Bar CLOSE Bid Quote;Volume"

> "TimeZone: Eastern Standard Time (EST) time-zone WITHOUT Day Light Savings adjustments"

> Generic ASCII tick row fields: "DateTime Stamp,Bid Quote,Ask Quote,Volume"

What the documentation does **not** say: who the upstream quote provider is, that the provider changed, or that the spread behaviour changed. The About page (https://www.histdata.com/about-us/ **[FULL]**) says only "We're a group of traders and strategy developers".

**The key point for the note:** the documented time zone is a fixed UTC-5 clock. The files do not behave that way (section 4 of `results/RESULTS-SUMMARY.md`). So the "clock error" is not a user who ignored the documentation; it is a user who **followed** it.

### Terms of use

- No terms-of-use, licence or disclaimer page exists on the site. `/terms-of-use/`, `/terms/`, `/terms-and-conditions/` and `/disclaimer/` all return HTTP 404; the home page links only to the FAQ, About, a cookies page and a privacy policy. The footer reads "(c) 2026 HistData.com"; each status file inside a zip reads "HistData.com (c) 2012".
- The only statement about use is the FAQ line quoted above ("Use the data at your own will and risk"). `robots.txt` disallows only `/wp-admin/`.
- **What this allows:** nothing on the site restricts publishing statistics derived from the data. Nothing grants a redistribution licence either. Safe practice for the paper: publish derived statistics, tables, figures and the download-and-analysis code; **do not** redistribute the raw files; cite the site and the download date. This is a reading of the site, not legal advice; Sean could email the site for an explicit OK if a journal asks.
- Second source (FXCM candles): FXCM's README says the sample data is free, "Timestamps are in UTC", and "This is for personal use and abides by our EULA" (https://github.com/fxcm/MarketData **[FULL]** README). Same rule: statistics yes, files no. The EULA itself was not read.

## 3. Practitioner write-ups on the histdata clock

| Source | Read | What it says | Relation to this note |
|---|---|---|---|
| radiusred/tradedesk-marketdata issue #82, "HistData timestamps are one hour late in summer: 'EST' is not a fixed UTC-5", 9 Oct 2026, https://github.com/radiusred/tradedesk-marketdata/issues/82 | **[FULL]** | Compared histdata with a Dukascopy cache, 25 instruments, 2020-01 to 2026-02. Winter days match at zero shift, summer days only at minus 60 minutes. States two eras: New York local time with DST for the provider used "until 2018-12-16", then "Europe/Zurich local time minus a fixed 6 h". Says "HistData's own description is wrong". | **Direct prior art for the clock finding, four days before this analysis.** Must be cited. This note reproduces it independently (no Dukascopy; internal evidence 2009-2026 plus FXCM 2012-2023). The 2018-12-16 date is theirs and was not verified here; this analysis only brackets the switch between 2 Nov 2018 and 15 Mar 2019. |
| Same repository, issue #93, 9 Oct 2026, https://github.com/radiusred/tradedesk-marketdata/issues/93 | **[FULL]** | Implementation plan for the per-era decode with `zoneinfo`. | Same. |
| jay79-boop/pwb-toolbox pull request #87, 22 Aug 2026, https://github.com/jay79-boop/pwb-toolbox/pull/87 | **[FULL]** | "histdata's ASCII M1 exports are stamped New York local time *with DST*, not the fixed EST they are usually read as." Reports a strategy measuring +39 points on the flat offset and +7 on the right one. | Earlier prior art for the clock finding (one era only). Must be cited. Also an independent example of the consequence. |
| dmidlo/histdata.com-tools issues #46 (2022) and #127 (21 Jun 2026), https://github.com/dmidlo/histdata.com-tools/issues/127 | **[FULL]** | A maintained downloader that deliberately enforces "fixed UTC-05:00" and adds tests "to avoid accidental America/New_York localization". | Evidence that the documented convention is being hard-coded into tools today - i.e. the error is live. |
| philipperemy/FX-1-Minute-Data README (691 GitHub stars), https://github.com/philipperemy/FX-1-Minute-Data | **[FULL]** (README) | Repeats "TimeZone: Eastern Standard Time (EST) time-zone *WITHOUT* Day Light Savings adjustments" and the bid-quote field list. | Evidence of how widely the dataset and its documented convention are used. |

Honest reading: the clock fact is "known to a handful of practitioners since mid-2026, unknown to the main tools, absent from the literature found". None of these write-ups mentions the rollover artefact or bid-only bias.

Both GitHub write-ups appear to be AI-assisted project notes (one says so). They are still dated, public, and specific, and a referee can find them in one search - cite them.

## 4. The 17:00 New York rollover and spread widening

| Source | Read | Relevance |
|---|---|---|
| Breedon, F. and Ranaldo, A. (2013), "Intraday patterns in FX returns and order flow", *Journal of Money, Credit and Banking* 45(5). DOI 10.1111/jmcb.12032. Working-paper version: Queen Mary WP 694 (2012), https://www.econstor.eu/bitstream/10419/97343/1/690223323.pdf | **[FULL]** (working paper) | Calls New York time "the universally accepted reference time zone for OTC FX transactions (i.e. the end of the trading day is defined as 5pm New York time...)". Uses EBS firm bid and offer, defines returns "using the prevailing midquote price", and notes that daylight saving "does not begin/end on the same date as New York; we allow for this in our calculations". | The careful benchmark: mid quotes and explicit DST handling. Shows what the note's naive user fails to do. Does not discuss rollover spread widening. |
| BIS Markets Committee (2017), "The sterling 'flash event' of 7 October 2016", Markets Committee Papers 9, https://www.bis.org/publ/mktc09.htm | **[ABS]** (PDF download blocked) | Official report that puts "significant weight on the time of day" (early Asian hours, just after the New York close) as a cause of thin liquidity. | Authoritative support that liquidity is thinnest right after 17:00 New York. Read the PDF before citing specifics. |
| Noss, Pedace, Tobek, Linton and Crowley-Reidy (2017), "The October 2016 sterling flash episode", Bank of England SWP. DOI 10.2139/ssrn.3066841 | **[META]** | Same event, academic treatment. | Optional. |
| Huang, R. and Masulis, R. (1999), "FX spreads and dealer competition across the 24-hour trading day", *Review of Financial Studies* 12(1). DOI 10.1093/rfs/12.1.61 | **[META]** | Classic paper on spreads by time of day. | Likely the right citation for "spreads vary with dealer competition over the day". **Must be read before citing.** |
| Bollerslev, T. and Domowitz, I. (1993), "Trading patterns and prices in the interbank foreign exchange market", *Journal of Finance* 48(4). DOI 10.1111/j.1540-6261.1993.tb04760.x | **[META]** | Intraday quote and spread patterns. | Same caveat. |
| Ito, T. and Hashimoto, Y. (2006), "Intraday seasonality in activities of the foreign exchange markets: evidence from the electronic broking system", *J. Japanese and International Economies* 20(4). DOI 10.1016/j.jjie.2006.06.005; NBER WP 12413 | **[ABS]** | "A negative correlation is observed between the number of deals and the width of bid-ask spread during business hours." | Supports: spreads are widest when activity is lowest. |
| Karnaukh, Ranaldo and Soderlind (2015), "Understanding FX liquidity", *RFS* 28(11). DOI 10.1093/rfs/hhv029; Mancini, Ranaldo and Wrampelmeyer (2013), *J. Finance* 68(5). DOI 10.1111/jofi.12053 | **[META]** | FX liquidity measurement. | Background only. |
| Broker help pages: FOREX.com "Rollover FAQs" (https://forex.com/en-us/help-and-support/rollover); BlackBull "Understanding roll over and widening spreads" | **[SNIPPET]** (HTTP 403 / 404 on fetch) | Rollover is processed at 5pm New York; spreads widen around it. | Shows it is common knowledge. **Open in a browser and quote exactly, or do not cite.** |

No source found reports the size of the widening as it appears in a bid-only retail history, or dates when a free dataset started to show it.

## 5. Intraday FX seasonality (the "real" effects a referee will compare against)

| Source | Read | Finding | Use |
|---|---|---|---|
| Cornett, Schwarz and Szakmary (1995), "Seasonalities and intraday return patterns in the foreign currency futures market", *J. Banking and Finance* 19(5). DOI 10.1016/0378-4266(95)00084-T | **[META]** | Per Breedon and Ranaldo's summary: local currencies depreciate in their own trading hours. | Cite via own reading only. |
| Ranaldo, A. (2009), "Segmentation and time-of-day patterns in foreign exchange markets", *J. Banking and Finance* 33(12). DOI 10.1016/j.jbankfin.2009.05.019 | **[ABS]** | "domestic currencies appreciate (depreciate) systematically during foreign (domestic) working hours". | The genuine time-of-day effect. It is spread over whole sessions and is small; the artefact is one minute and large. |
| Breedon and Ranaldo (2013), above | **[FULL]** | Confirms the pattern with EBS mid quotes; trading-strategy returns "inc. costs" are far smaller. | Same contrast. The hour scan here shows EURUSD hours 06-07 New York with t about -5, which may be this real effect. |
| Krohn, Mueller and Whelan (2024), "Foreign exchange fixings and returns around the clock", *Journal of Finance*. DOI 10.1111/jofi.13306 | **[META]** | Intraday return pattern around the fixings. | Probably the most relevant recent paper. **Read before submission**; a referee in this area will expect it. |
| Andersen and Bollerslev (1997), "Intraday periodicity and volatility persistence in financial markets", *J. Empirical Finance* 4. DOI 10.1016/S0927-5398(97)00004-2 | **[META]** | Intraday volatility seasonality and announcement spikes. | Background for the 08:30 release test. |
| Dacorogna, Gencay, Muller, Olsen and Pictet (2001), *An Introduction to High-Frequency Finance*, Academic Press | **[META]** | Standard reference on FX tick data cleaning, bid-ask bounce, time-zone and "business time" issues. | Likely already describes generic versions of both problems. **Check the data-cleaning chapters before claiming anything is new in general.** |
| Nower (2024), "Losing sleep at the international market: daylight saving time and exchange rates", *Economics Letters*. DOI 10.1016/j.econlet.2024.111813 | **[META]** | DST and exchange rates (behavioural angle, judging by the title). | Different question; cite only if read. |

## 6. Data artefacts and spurious backtest results

| Source | Read | Use |
|---|---|---|
| Bailey, Borwein, Lopez de Prado and Zhu (2014), "Pseudo-mathematics and financial charlatanism", *Notices of the AMS* 61(5). DOI 10.1090/noti1105 | **[META]** | Backtest overfitting; the general frame. Open access. |
| Bailey and Lopez de Prado (2014), "The deflated Sharpe ratio", *J. Portfolio Management* 40(5). DOI 10.3905/jpm.2014.40.5.094 | **[META]** | Point to make: multiple-testing corrections do **not** remove this artefact, because it is a real feature of the data, not luck. (In the earlier project the artefact passed a Benjamini-Hochberg screen with q = 0.000.) |
| Harvey, Liu and Zhu (2016), "...and the cross-section of expected returns", *RFS* 29(1). DOI 10.1093/rfs/hhv059 | **[META]** | t > 3 hurdle; here t is -28 to -38 and still not tradable. |
| Sullivan, Timmermann and White (1999), "Data-snooping, technical trading rule performance, and the bootstrap", *J. Finance* 54(5). DOI 10.1111/0022-1082.00163 | **[META]** | Data snooping in trading rules. |
| Ince and Porter (2006), "Individual equity return data from Thomson Datastream: handle with care!", *J. Financial Research* 29(4). DOI 10.1111/j.1475-6803.2006.00189.x | **[META]** | The closest **genre** precedent: a short note documenting errors in one widely used database and showing they change published inferences. Good model for structure. |
| Rosenberg and Houglet (1974), "Error rates in CRSP and Compustat data bases and their implications", *J. Finance* 29(4). DOI 10.1111/j.1540-6261.1974.tb03107.x | **[META]** | Same genre, classic. |
| Brownlees and Gallo (2006), "Financial econometric analysis at ultra-high frequency: data handling concerns", *Computational Statistics and Data Analysis* 51(4). DOI 10.1016/j.csda.2006.09.030 | **[META]** | High-frequency data cleaning. |

## 7. How much is "already known", stated plainly

| Claim in the note | Status |
|---|---|
| histdata M1 bars are bid-only | Documented by the vendor. Known. |
| FX spreads widen around 17:00 New York | Common practitioner knowledge; supported indirectly by central-bank reports. Known. |
| A bid-only series therefore dips at the rollover | Follows logically; **no written source found that states or measures it**. |
| Size: -0.8 to -2.6 bp in one minute, t -28 to -38, ten pairs | **Not found anywhere.** New measurement. |
| It is absent before 2015 and present every year since | **Not found anywhere.** New. |
| It yields Sharpe 2 to 8 for a one-line rule at zero cost, about 0.5 on mid quotes and about -3.8 after the spread | **Not found anywhere.** New. |
| histdata timestamps are not fixed EST | **Known to a few practitioners (Aug and Oct 2026 GitHub).** Not in any paper found. Verified independently here. |
| Two eras, the second following the European calendar | Stated in the Oct 2026 GitHub issue. Verified independently here with a longer sample and a different reference. |
| The clock error and the rollover artefact interact (the wrong clock hides the artefact for about 60% of days) | **Not found anywhere.** New. |

## 8. What a documented, quantified note adds

- A citable reference with numbers, for a dataset that hundreds of public projects use.
- A second-source check (FXCM) that does not depend on trusting the vendor.
- A regime date (2015) that explains why older tutorials never saw the problem.
- A warning that standard multiple-testing controls do not catch it.
- Tested, small code that fixes both problems.

## 9. Reading list for Sean before writing (in order)

1. Breedon and Ranaldo (2013) - working paper is free; sections 2.1-2.2.
2. The two GitHub write-ups (issues #82 and #87 above).
3. Huang and Masulis (1999) and Krohn, Mueller and Whelan (2024) - needed before the literature paragraph can be written honestly.
4. Ince and Porter (2006) - as a model of the genre.
5. Dacorogna et al. (2001), data-cleaning chapter - to make sure the general point is attributed.
