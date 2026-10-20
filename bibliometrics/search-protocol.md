# Search protocol - 03-fx-data-artefact

- Paper question: A bid-only rollover artefact and a timestamp error in free minute-level FX data (histdata.com)
- Date of search and data pull: **2026-10-17**
- Years covered: 1970-2026; language: English (OpenAlex language field `en` or missing)
- Built by an AI agent (Claude) with the scripts in `python\` and `R\`; all numbers below are read from the run logs.

## 1. Databases

| Role | Database | Access | Note |
|---|---|---|---|
| Discovery | Crossref REST API | free, no key, `mailto` polite pool | relevance-ranked keyword search; top N per query |
| Discovery | Semantic Scholar Graph API (bulk search) | free, no key | boolean search on title/abstract; top N by citations per query |
| Discovery | ERIC API | free, no key | education topics only |
| Discovery | arXiv API | free, no key | preprints |
| Enrichment (authors, institutions, countries, topics, keywords, abstracts, references, citation counts, OA links) | **OpenAlex** single-record lookups (`/works/doi:...`, `/works/mag:...`, `/works/W...`) | free, no key | see limit 1 below |
| Forward citations for snowballing | OpenCitations Index API v2 | free, no key | DOI-to-DOI citations only |
| Cross-check | Crossref (per-DOI), Semantic Scholar (batch) | free, no key | citation counts and reference-list coverage compared in `tables\coverage_crosscheck.csv` |
| Not used | Scopus, Web of Science, Lens, Dimensions | need accounts | equivalent strings are in `scopus-queries.md` |
| Not usable | RePEc/IDEAS | its API needs a registered access code; the public search page returned no parseable result list to a script | economics working papers still enter via Crossref, Semantic Scholar and snowballing |

**Why OpenAlex was not the search engine.** Since 2026 OpenAlex charges keyless list/search calls against a small daily budget shared by everyone on the same IP address ($0.10/day). On the day of the pull that budget was already exhausted by other work on this network, and an API key needs an account (ruled out). Single-record lookups remain free and unlimited, so records were *discovered* in Crossref / Semantic Scholar / ERIC / arXiv and then *enriched* one by one from OpenAlex. Consequence: a work that is in OpenAlex but not found by any of the four discovery databases is missed, except where snowballing caught it.

## 2. Exact search strings

### a_intraday_seasonality: Intraday FX seasonality and time-of-day effects

| database | query | hits in database | records retrieved | status |
|---|---|---|---|---|
| crossref | intraday patterns foreign exchange returns order flow | 2565718.0 | 250 | ok |
| crossref | seasonalities intraday return patterns foreign currency futures | 1020096.0 | 250 | ok |
| crossref | intraday seasonality foreign exchange activity electronic broking | 2923679.0 | 250 | ok |
| crossref | segmentation time-of-day patterns foreign exchange markets | 3373203.0 | 250 | ok |
| crossref | foreign exchange fixings and returns around the clock | 877223.0 | 250 | ok |
| crossref | intraday periodicity volatility persistence financial markets | 804453.0 | 250 | ok |
| crossref | time of day effects exchange rate volatility | 5289360.0 | 250 | ok |
| crossref | day of the week effect foreign exchange | 3859877.0 | 250 | ok |
| crossref | intraday volatility pattern currency market trading hours | 990182.0 | 250 | ok |
| crossref | macroeconomic announcements intraday exchange rate | 932030.0 | 250 | ok |
| crossref | overnight versus intraday currency returns | 631527.0 | 250 | ok |
| s2 | (intraday \| "time of day" \| "time-of-day" \| diurnal \| "around the clock") + ("foreign exchange" \| currency \| "exchange rate" \| forex) | 1021.0 | 800 | ok |
| s2 | ("intraday seasonality" \| "intraday patterns" \| "intraday periodicity") + (FX \| currency \| "exchange rate" \| "foreign exchange") | 52.0 | 52 | ok |
| s2 | (fixing \| fixings \| "daylight saving") + ("foreign exchange" \| currency \| "exchange rate") | 1277.0 | 800 | ok |
| arxiv | all:"intraday" AND all:"foreign exchange" | 11.0 | 11 | ok |
| arxiv | all:"intraday seasonality" AND cat:q-fin.* | 9.0 | 9 | ok |
| arxiv | all:forex AND all:"time of day" | 0.0 | 0 | ok |

### b_fx_microstructure: FX microstructure around the daily rollover, spreads and liquidity

| database | query | hits in database | records retrieved | status |
|---|---|---|---|---|
| crossref | fx spreads dealer competition 24-hour trading day | 2817714.0 | 250 | ok |
| crossref | trading patterns and prices in the interbank foreign exchange market | 1667851.0 | 250 | ok |
| crossref | bid-ask spread foreign exchange intraday | 742495.0 | 250 | ok |
| crossref | understanding FX liquidity | 538385.0 | 250 | ok |
| crossref | liquidity risk and arbitrage pricing foreign exchange | 2382558.0 | 250 | ok |
| crossref | foreign exchange market microstructure order flow | 2652860.0 | 250 | ok |
| crossref | rollover foreign exchange spread widening | 725126.0 | 250 | ok |
| crossref | sterling flash event October 2016 liquidity | 5732991.0 | 250 | ok |
| crossref | electronic broking system FX market microstructure | 4871296.0 | 250 | ok |
| crossref | FX market liquidity time of day thin trading | 2859754.0 | 250 | ok |
| crossref | retail forex broker spreads execution quality | 1541587.0 | 250 | ok |
| crossref | high-frequency foreign exchange quotes bid ask midquote | 4064341.0 | 250 | ok |
| s2 | ("bid-ask spread" \| spreads \| liquidity \| microstructure \| "order flow") + ("foreign exchange" \| "FX market" \| currency \| forex) + (intraday \| "time of day" \| hours) | 268.0 | 268 | ok |
| s2 | (rollover \| "roll-over" \| "daily close" \| "5 pm") + (FX \| "foreign exchange" \| forex) + (spread \| liquidity) | 16.0 | 16 | ok |
| s2 | ("flash crash" \| "flash event") + (sterling \| currency \| "foreign exchange") | 19.0 | 19 | ok |
| arxiv | all:"foreign exchange" AND all:"bid-ask spread" | 3.0 | 3 | ok |
| arxiv | all:"FX" AND all:microstructure | 26.0 | 26 | ok |
| arxiv | all:forex AND all:spread AND cat:q-fin.* | 1.0 | 1 | ok |

### c_data_quality: Data quality, data errors and spurious results in financial research

| database | query | hits in database | records retrieved | status |
|---|---|---|---|---|
| crossref | individual equity return data Thomson Datastream handle with care | 4880344.0 | 250 | ok |
| crossref | error rates in CRSP and Compustat data bases | 2939432.0 | 250 | ok |
| crossref | financial econometric analysis at ultra-high frequency data handling | 12071388.0 | 250 | ok |
| crossref | data errors high-frequency financial data cleaning | 6430253.0 | 250 | ok |
| crossref | spurious results data errors empirical finance | 3883905.0 | 250 | ok |
| crossref | survivorship bias look-ahead bias backtest data | 2724558.0 | 250 | ok |
| crossref | time zone daylight saving time errors financial data | 4900873.0 | 250 | ok |
| crossref | tick data filtering outliers high-frequency | 5893185.0 | 250 | ok |
| crossref | replication financial research data errors | 12047035.0 | 250 | ok |
| crossref | data snooping backtest overfitting pseudo-mathematics | 3530884.0 | 250 | ok |
| crossref | bid ask bounce quote data errors | 2584811.0 | 250 | ok |
| crossref | problems with free financial data vendors | 4510095.0 | 250 | ok |
| s2 | ("data errors" \| "data quality" \| "data cleaning" \| "data handling") + (financial \| "high-frequency" \| tick \| "asset prices" \| returns) | 4810.0 | 800 | ok |
| s2 | (timestamp \| timestamps \| "time zone" \| "daylight saving") + (financial \| trading \| "high-frequency" \| "tick data" \| market data) | 785.0 | 785 | ok |
| s2 | (spurious \| "look-ahead bias" \| "survivorship bias") + (backtest \| "trading strategy" \| "trading strategies" \| returns) | 1028.0 | 800 | ok |
| arxiv | all:"data quality" AND all:"high-frequency" AND cat:q-fin.* | 0.0 | 0 | ok |
| arxiv | all:"tick data" AND all:cleaning | 1.0 | 1 | ok |
| arxiv | all:timestamp AND all:"market data" | 3.0 | 3 | ok |
| arxiv | all:"look-ahead bias" AND cat:q-fin.* | 22.0 | 22 | ok |

Per-query retrieval caps: crossref = 250, s2 = 800, arxiv = 100. Crossref totals are large because its search is an OR-type relevance ranking; only the top-ranked records were taken. Raw responses for every query are in `data\raw\<database>\`.

### Seed papers (known key works, each verified to exist by a Crossref title match; they bypass the keyword rules)

| seed title | result |
|---|---|
| Intraday patterns in FX returns and order flow | matched 10.2139/ssrn.2099321 |
| FX Spreads and Dealer Competition across the 24-Hour Trading Day | matched 10.1093/rfs/12.1.61 |
| Trading Patterns and Prices in the Interbank Foreign Exchange Market | matched 10.1111/j.1540-6261.1993.tb04760.x |
| Intraday seasonality in activities of the foreign exchange markets: evidence from the electronic broking system | matched 10.1016/j.jjie.2006.06.005 |
| Understanding FX Liquidity | matched 10.2139/ssrn.2329738 |
| Segmentation and time-of-day patterns in foreign exchange markets | matched 10.1016/j.jbankfin.2009.05.019 |
| Foreign Exchange Fixings and Returns around the Clock | matched 10.1111/jofi.13306 |
| Intraday Periodicity and Volatility Persistence in Financial Markets | matched 10.1016/s0927-5398(97)00004-2 |
| Individual Equity Return Data From Thomson Datastream: Handle With Care! | matched 10.1111/j.1475-6803.2006.00189.x |
| Error Rates in CRSP and Compustat Data Bases and Their Implications | matched 10.1111/j.1540-6261.1974.tb03107.x |
| Financial econometric analysis at ultra-high frequency: Data handling concerns | matched 10.1016/j.csda.2006.09.030 |
| Seasonalities and intraday return patterns in the foreign currency futures market | matched 10.1016/0378-4266(95)00084-t |
| Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance | matched 10.1090/noti1105 |
| The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality | matched 10.3905/jpm.2014.40.5.094 |

## 3. Inclusion and exclusion rules (applied identically to search hits and snowballed records)

A record is **included** if all of the following hold:
1. It resolves to an OpenAlex work record (by DOI, MAG id, or a Crossref title match of at least 93% similarity).
2. OpenAlex type is article, review, preprint, book chapter, book, dissertation, report or other (editorials, errata, paratext, datasets, peer reviews are dropped).
3. Publication year 1970-2026; language English or unrecorded.
4. It satisfies at least one sub-literature rule below: every `include` pattern must match in title + abstract, and every `title_must` pattern must match in the title.
5. Its title does not match the exclusion pattern.
6. Citation floor: records older than 3 years need at least 1 citation(s).

Book-series and proceedings trap: a record whose abstract is a series/proceedings blurb (detected by wording such as 'this volume constitutes the refereed proceedings', or the same abstract shared by 3+ records) is screened on its title alone; whole-volume records (titles starting 'Proceedings of', 'Front matter', etc.) are dropped.

The patterns are case-insensitive regular expressions (`\b` = word boundary, `\w*` = any word ending, `.{0,80}` = within 80 characters).

**a_intraday_seasonality - Intraday FX seasonality and time-of-day effects**

- include (title+abstract): `(intraday|intra-day|time[- ]of[- ]day|diurnal|seasonal\w*|trading hours?|hour[- ]of[- ]the[- ]day|session|around the clock|day[- ]of[- ]the[- ]week|weekend|periodicity|time[- ]zone|fixings?|24[- ]hour)`
- include (title+abstract): `\b(foreign exchange|exchange rates?|currenc\w*|forex|\bfx\b|\beuro\b|yen|sterling|dollar|eur/usd|usd/jpy)\b`
- title_must (title): `(intraday|intra-day|time[- ]of[- ]day|diurnal|seasonal|hours?|session|around the clock|day|weekend|periodic|pattern|fixing|returns?|volatility|activity|trading)`

**b_fx_microstructure - FX microstructure around the daily rollover, spreads and liquidity**

- include (title+abstract): `(bid[- ]ask|spreads?|rollover|roll-over|market microstructure|microstructure|liquidity|order flow|quotes?|quoting|tick data|market makers?|dealers?|interbank|limit order|electronic broking|ebs\b|reuters)`
- include (title+abstract): `\b(foreign exchange|exchange rates?|currenc\w*|forex|\bfx\b|\beuro\b|yen|sterling|dollar|eur/usd|usd/jpy)\b`
- title_must (title): `(spread|bid|ask|rollover|roll-over|microstructure|liquidity|order flow|quot|tick|dealer|interbank|trading|market|intraday|volume|depth|electronic|high[- ]frequency)`

**c_data_quality - Data quality, data errors and spurious results in financial research**

- include (title+abstract): `(data (quality|errors?|cleaning|mining|vendors?|problems?|mistakes?|revisions?|filtering)|errors? in (data|databases?|prices?)|time ?stamps?|time[- ]zone|daylight saving|survivorship bias|look-?ahead bias|spurious|measurement errors?|database errors?|bid[- ]only|reproducib\w+|replicat\w+|outliers?|data handling|filtering (of )?high[- ]frequency|handle with care|backtest\w*|data snooping)`
- include (title+abstract): `(financ\w+|market|price|prices|returns?|tick|trading|asset|stock|currenc\w*|exchange rates?|econom\w+|high[- ]frequency|database)`
- title_must (title): `(data|error|quality|timestamp|time stamp|time zone|daylight|bias|spurious|clean|filter|replicat|reproduc|anomal|outlier|mistake|handle with care|snooping|backtest|mining|database|care)`

**Exclusion pattern (title):** `(deep learning|neural network|\blstm\b|transformer|reinforcement learning|random forest|support vector|genetic algorithm|blockchain|covid|tourism|remittance|inflation targeting|purchasing power|pass-through|trade balance|carbon|climate|electricity|bank lending|monetary policy shocks?)`

A record matching several rules is assigned to the first one in the order listed (its other matches are kept in `sublits_all`).

## 4. Snowballing (one round)

- Central papers: the 25 corpus records ranked highest on local citations + topical relevance + log(global citations) - listed in `data\clean\snowball_central_papers.csv`.
- Backward: every OpenAlex `referenced_works` entry of those papers not already in the corpus (694 candidates).
- Forward: citing DOIs from OpenCitations, up to 150 per central paper (1628 candidates). OpenCitations only knows DOI-to-DOI links, so citing preprints and books without DOIs are missed.
- All candidates were looked up in OpenAlex and screened with the rules in section 3: 71 backward and 141 forward records were added.

## 5. PRISMA-style counts

| stage | n |
|---|---|
| Records identified through database searching (all query hits) | 13199 |
|    of which from arxiv | 76 |
|    of which from crossref | 8750 |
|    of which from s2 | 4340 |
|    of which from seed | 33 |
| Duplicates removed (same DOI / id / title across queries and databases) | 4409 |
| Unique records screened on title (+ abstract where the database supplied one) | 8790 |
| Removed at title pre-screen (off-topic) | 5840 |
| Records looked up in OpenAlex | 2950 |
| Duplicates removed after OpenAlex matching (same work / same title) | 13 |
| Excluded at full screen: offtopic_fails_inclusion_rule | 1765 |
| Excluded at full screen: type_excluded | 153 |
| Excluded at full screen: no_openalex_record (no DOI / not indexed) | 115 |
| Excluded at full screen: uncited_older_record (citation floor) | 60 |
| Excluded at full screen: language_not_english | 13 |
| Excluded at full screen: paratext_or_container_record | 2 |
| Included after search screening | 829 |
| Snowball: central papers used | 25 |
| Snowball: backward-reference candidates | 694 |
| Snowball: forward-citation candidates (OpenCitations) | 1628 |
| Snowball: duplicates of corpus records | 40 |
| Snowball excluded: offtopic_fails_inclusion_rule | 1694 |
| Snowball excluded: no_openalex_record | 175 |
| Snowball excluded: offtopic_exclusion_term_in_title | 79 |
| Snowball excluded: type_excluded | 49 |
| Snowball excluded: language_not_english | 27 |
| Snowball excluded: year_out_of_range | 17 |
| Snowball excluded: uncited_older_record (citation floor) | 17 |
| Snowball excluded: paratext_or_container_record | 12 |
| Snowball: included (backward) | 71 |
| Snowball: included (forward) | 141 |
| Corpus before hand-screening | 1041 |
| Removed at hand-screening (see tables/hand_screen_removed.csv) | 96 |
| FINAL CORPUS | 945 |
|    with abstract | 687 |
|    with DOI | 847 |
|    with a reference list in OpenAlex | 803 |
| Distinct cited references / resolved to metadata | 21364 / 4641 |

Figure: `figures\py_01_prisma_flow.png`.

## 6. Hand-screening

After rule screening and snowballing, the agent read the titles (with source and year) of the whole corpus and removed 96 records as off-topic or mis-matched; every removal and its reason is in `tables\hand_screen_removed.csv`. This is a single-screener pass by an AI agent on titles, not a two-person human screen; borderline records were kept.

Removal reasons:
- Off-topic: not a finance/FX data-quality study (non-financial domain such as hydrology, medicine, radar, surveys); hand-screened by title, 17 Oct 2026: 96

## 7. Coverage and cross-checks

| item | value |
|---|---|
| corpus records | 945.0 |
| records with DOI | 847.0 |
| found in Crossref (DOI lookup) | 811.0 |
| found in Semantic Scholar (batch DOI lookup) | 767.0 |
| Spearman corr. OpenAlex vs Crossref cited-by | 0.919 |
| Spearman corr. OpenAlex vs Semantic Scholar cited-by | 0.935 |
| median cited-by: OpenAlex | 14.0 |
| median cited-by: Crossref | 11.0 |
| median cited-by: Semantic Scholar | 16.0 |
| records with no reference list in OpenAlex | 142.0 |
|   of which Crossref holds a reference list | 4.0 |
| records with no institution/country data | 157.0 |
| records without abstract | 258.0 |
| open-access records (OpenAlex) | 498.0 |
| origin: search | 714.0 |
| origin: snowball_forward | 141.0 |
| origin: snowball_backward | 71.0 |
| origin: seed | 19.0 |
| retrieved by: s2 | 709.0 |
| retrieved by: openalex_snowball | 212.0 |
| retrieved by: arxiv | 22.0 |
| retrieved by: seed | 19.0 |
| retrieved by: crossref | 4.0 |


- 115 title-screened candidates could not be matched to any OpenAlex record (no DOI or MAG id, or not indexed) and are **not** in the corpus. They are listed in `data\clean\unresolved_candidates.csv` (s2: 113, seed: 2). ERIC reports and theses and Indian or legal journal articles without DOIs dominate this list.

- Cited references: 21364 distinct works are cited by the corpus (35314 links); 4641 of the 5000 outside the corpus were resolved to metadata for the co-citation and RPYS analyses.


### Named prior work (seed list / the substance agent's saved papers) - is it in the corpus?

| id | kind | in_corpus |
|---|---|---|
| 10.1016/0378-4266(95 | doi | 0 |
| 10.1016/j.csda.2006.09.030 | doi | 1 |
| 10.1016/j.econlet.2024.111813 | doi | 1 |
| 10.1016/j.jbankfin.2009.05.019 | doi | 1 |
| 10.1016/j.jjie.2006.06.005 | doi | 1 |
| 10.1016/s0927-5398(97 | doi | 0 |
| 10.1090/noti1105 | doi | 1 |
| 10.1093/rfs/12.1.61 | doi | 1 |
| 10.1093/rfs/hhv029 | doi | 1 |
| 10.1093/rfs/hhv059 | doi | 1 |
| 10.1111/0022-1082.00163 | doi | 1 |
| 10.1111/j.1475-6803.2006.00189.x | doi | 1 |
| 10.1111/j.1540-6261.1974.tb03107.x | doi | 1 |
| 10.1111/j.1540-6261.1993.tb04760.x | doi | 1 |
| 10.1111/jmcb.12032 | doi | 1 |
| 10.1111/jofi.12053 | doi | 1 |
| 10.1111/jofi.13306 | doi | 1 |
| 10.2139/ssrn.3066841 | doi | 1 |
| 10.3905/jpm.2014.40.5.094 | doi | 1 |

## 8. API failures during the run

- api.openalex.org: failed after retries: {"error":"Rate limit exceeded","message":"Rate l (x280)
- api.crossref.org: failed after retries:  (x2)


## 9. Scopus / Web of Science exports
- `scopus-drop\`: EMPTY - no Scopus/WoS export to merge; corpus is OpenAlex-only.
- Ready-to-paste strings: `scopus-queries.md`.
