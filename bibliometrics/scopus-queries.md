# Scopus and Web of Science queries - paper 03 (bid-only rollover artefact and timestamp error in free minute FX data)

Status: **not run.** There is no Scopus or Web of Science login on this machine. `scopus-drop\` was empty on 2026-10-13.
The strings mirror the three sub-literatures in `search-protocol.md`. Note: the practitioner write-ups (GitHub issues, vendor FAQs) that are the nearest prior art for the clock error are not in any bibliographic database.

How to use
- Scopus: Advanced document search -> paste -> Search -> Export -> **CSV**; tick *Citation information, Bibliographical information, Abstract & keywords, Include references* (with references the cap is 2,000 records per file: export in year slices).
- Web of Science: Advanced Search (Core Collection) -> paste -> Export -> **BibTeX** or *Plain text file*, Record Content = **Full Record and Cited References** (500 per file).
- Save each export into `bibliometrics\scopus-drop\`; the R script merges whatever is there with `bibliometrix::convert2df()` + `mergeDbSources()`.
- Record the date, database and number of hits under each query.

## A. Intraday FX seasonality and time-of-day effects

Scopus
```
TITLE-ABS-KEY ( ( intraday OR "intra-day" OR "time of day" OR "time-of-day" OR diurnal OR "around the clock" OR "trading hours" OR "intraday seasonalit*" OR "intraday pattern*" OR "intraday periodicity"
    OR fixing* OR "day-of-the-week" OR "day of the week" OR "overnight return*" OR "daylight saving" )
  AND ( "foreign exchange" OR "exchange rate*" OR currenc* OR forex OR "FX market" ) )
AND NOT TITLE ( "deep learning" OR "neural network*" OR lstm OR tourism OR remittance OR "purchasing power" OR "pass-through" OR carbon )
AND PUBYEAR > 1969 AND LANGUAGE ( english )
AND ( LIMIT-TO ( SUBJAREA , "ECON" ) OR LIMIT-TO ( SUBJAREA , "BUSI" ) OR LIMIT-TO ( SUBJAREA , "MATH" ) OR LIMIT-TO ( SUBJAREA , "PHYS" ) )
```
Web of Science
```
TS=((intraday OR "intra-day" OR "time of day" OR "time-of-day" OR diurnal OR "around the clock" OR "trading hours" OR "intraday seasonalit*" OR "intraday pattern*" OR "intraday periodicity"
    OR fixing* OR "day-of-the-week" OR "day of the week" OR "overnight return*" OR "daylight saving")
  AND ("foreign exchange" OR "exchange rate*" OR currenc* OR forex OR "FX market"))
NOT TI=("deep learning" OR "neural network*" OR lstm OR tourism OR remittance OR "purchasing power" OR "pass-through" OR carbon)
AND PY=(1970-2026) AND LA=(English)
```
Refine by Web of Science Categories: Business, Finance; Economics; Mathematics, Interdisciplinary Applications; Physics, Multidisciplinary.

## B. FX microstructure around the daily rollover, spreads and liquidity

Scopus
```
TITLE-ABS-KEY ( ( "bid-ask spread*" OR "bid ask spread*" OR spread* OR rollover OR "roll-over" OR microstructure OR "order flow" OR liquidity OR "tick data" OR "market maker*" OR dealer* OR interbank
    OR "limit order*" OR "electronic broking" OR "flash crash" OR "flash event" OR "price impact" )
  AND ( "foreign exchange" OR "exchange rate*" OR currenc* OR forex OR "FX market" OR "FX spot" )
  AND ( intraday OR "time of day" OR hours OR "high-frequency" OR "trading day" OR quote* OR "daily close" OR "end of day" ) )
AND NOT TITLE ( "deep learning" OR "neural network*" OR lstm OR blockchain OR carbon OR "monetary policy shock*" OR "bank lending" )
AND PUBYEAR > 1969 AND LANGUAGE ( english )
```
Web of Science
```
TS=(("bid-ask spread*" OR "bid ask spread*" OR spread* OR rollover OR "roll-over" OR microstructure OR "order flow" OR liquidity OR "tick data" OR "market maker*" OR dealer* OR interbank
    OR "limit order*" OR "electronic broking" OR "flash crash" OR "flash event" OR "price impact")
  AND ("foreign exchange" OR "exchange rate*" OR currenc* OR forex OR "FX market" OR "FX spot")
  AND (intraday OR "time of day" OR hours OR "high-frequency" OR "trading day" OR quote* OR "daily close" OR "end of day"))
NOT TI=("deep learning" OR "neural network*" OR lstm OR blockchain OR carbon OR "monetary policy shock*" OR "bank lending")
AND PY=(1970-2026) AND LA=(English)
```

## C. Data quality, data errors and spurious results in financial research

Scopus
```
TITLE-ABS-KEY ( ( "data quality" OR "data error*" OR "data cleaning" OR "data handling" OR "errors in data" OR "database error*" OR timestamp* OR "time stamp*" OR "time zone*" OR "daylight saving"
    OR "survivorship bias" OR "look-ahead bias" OR "lookahead bias" OR spurious OR "measurement error*" OR "bid-only" OR outlier* OR "handle with care" OR replicat* OR reproducib* OR "data vendor*" )
  AND ( "financial data" OR "high-frequency" OR "tick data" OR "market data" OR "asset price*" OR "stock return*" OR "exchange rate*" OR currenc* OR "trading strateg*" OR backtest* OR "financial research" OR "empirical finance" ) )
AND NOT TITLE ( "deep learning" OR "neural network*" OR lstm OR genom* OR clinical OR satellite )
AND PUBYEAR > 1969 AND LANGUAGE ( english )
AND ( LIMIT-TO ( SUBJAREA , "ECON" ) OR LIMIT-TO ( SUBJAREA , "BUSI" ) OR LIMIT-TO ( SUBJAREA , "MATH" ) OR LIMIT-TO ( SUBJAREA , "COMP" ) )
```
Web of Science
```
TS=(("data quality" OR "data error*" OR "data cleaning" OR "data handling" OR "errors in data" OR "database error*" OR timestamp* OR "time stamp*" OR "time zone*" OR "daylight saving"
    OR "survivorship bias" OR "look-ahead bias" OR "lookahead bias" OR spurious OR "measurement error*" OR "bid-only" OR outlier* OR "handle with care" OR replicat* OR reproducib* OR "data vendor*")
  AND ("financial data" OR "high-frequency" OR "tick data" OR "market data" OR "asset price*" OR "stock return*" OR "exchange rate*" OR currenc* OR "trading strateg*" OR backtest* OR "financial research" OR "empirical finance"))
NOT TI=("deep learning" OR "neural network*" OR lstm OR genom* OR clinical OR satellite)
AND PY=(1970-2026) AND LA=(English)
```

## D. Seed check (should all be returned by the combined searches)
Breedon and Ranaldo (2013); Huang and Masulis (1999); Bollerslev and Domowitz (1993); Ito and Hashimoto (2006); Ranaldo (2009); Krohn, Mueller, Whelan (2024); Andersen and Bollerslev (1997); Ince and Porter (2006); Rosenberg and Houglet (1974); Brownlees and Gallo (2006); Karnaukh, Ranaldo, Soderlind (2015).
