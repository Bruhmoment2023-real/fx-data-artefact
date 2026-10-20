# Data dictionary: 03-fx-data-artefact - bibliometrics files

Generated 2026-10-17 by `_tools/depth-kit/appendix.py`. All files below were built from free databases (OpenAlex, Crossref, Semantic Scholar, ERIC, arXiv, OpenCitations) on the dates in `data/raw/query_log.csv`; access date = pull date unless a row says otherwise.

## Files

| Path (under `bibliometrics\`) | What it is | Rows | Columns | Known problems |
|---|---|---|---|---|
| `config.json` | every setting of the run: queries, inclusion/exclusion rules, seeds, manual_exclude (hand-screen exclusions with reasons), evidence relation text | 18 | JSON |  |
| `evidence-table.csv` | the 30-60 most relevant papers with study type, data, method, one-line finding, read status, relation to the paper | 57 | 19 | Findings from abstracts unless read_status says full text; hand-screened and patched after the automatic selection. |
| `data/api_log.json` | log of API calls, cache hits and errors | 282 | JSON | Contains no personal identifier. |
| `data/clean/bibliometrix_M.rds` | bibliometrix data frame (M) as saved R object |  | R data frame |  |
| `data/clean/bibliometrix_input.csv` | master table reshaped to Web of Science field tags for bibliometrix | 945 | 29 | CR (cited references) built from OpenAlex referenced_works labels; only references resolved within the cap are labelled. |
| `data/clean/citation_edges.csv` | direct citation links between corpus records (citing, cited: OpenAlex ids) | 2956 | 2 | Only links where OpenAlex has the reference list. |
| `data/clean/cited_references.csv` | works cited by corpus records, with how often and how many are in the corpus | 4786 | 10 | Capped number of references resolved to metadata (see refs_stats.json). |
| `data/clean/corpus_final.jsonl.gz` | corpus after one snowball round, raw OpenAlex JSON per line | 1041 | JSON per line | Written BEFORE hand-screen exclusions: master.csv has fewer rows (the exclusions in config.json manual_exclude are applied in the master stage). |
| `data/clean/corpus_stage1.jsonl.gz` | OpenAlex records that passed the title pre-screen and the topical screen (before snowballing) | 829 | JSON per line | Raw OpenAlex JSON per line. |
| `data/clean/evidence-table.autogen.csv` | the automatic evidence table before hand-screening (kept for comparison) | 61 | 18 |  |
| `data/clean/evidence_candidates.json` | ranked candidates for the evidence table | 70 | JSON |  |
| `data/clean/evidence_notes.json` | per-paper evidence-table fields (study type, method, finding from abstract, relation) | 61 | JSON | Findings come from abstracts only. |
| `data/clean/handscreen_exclusions.json` | OpenAlex ids excluded by hand-screen, with reason | 96 | JSON |  |
| `data/clean/master.csv` | one row per corpus record: the cleaned master table | 945 | 49 | Abstracts missing for part of the records; keywords are OpenAlex machine-assigned. |
| `data/clean/master.rds` | master.csv as an R data frame |  | R data frame |  |
| `data/clean/prisma_search.json` | PRISMA-style counts for the search stage | 10 | JSON |  |
| `data/clean/prisma_snowball.json` | PRISMA-style counts for the snowball stage | 11 | JSON |  |
| `data/clean/refs_stats.json` | counts of cited references and how many were resolved | 6 | JSON |  |
| `data/clean/screening_log_search.csv` | decision and reason for every candidate screened in the search stage | 2950 | 8 |  |
| `data/clean/screening_log_snowball.csv` | decision and reason for every candidate screened in the snowball stage | 2322 | 7 |  |
| `data/clean/snowball_central_papers.csv` | the most central corpus papers whose references and citations were snowballed | 25 | 6 |  |
| `data/clean/unresolved_candidates.csv` | search hits with no OpenAlex match (no DOI or not indexed) | 115 | 7 | These are lost to the map; check by hand if important. |
| `data/raw/all_hits.csv` | every hit returned by the discovery queries (Crossref, Semantic Scholar, ERIC, arXiv, seeds), before de-duplication | 13199 | 16 | Hits include off-topic records; duplicates across databases. |
| `data/raw/prior_work_ids.json` | OpenAlex ids/titles of papers named in the pack's prior-work notes, used as seeds | 3 | JSON | Titles that could not be matched are listed in run_search.log. |
| `data/raw/query_log.csv` | one row per query: database, search string, hits retrieved, date | 68 | 8 | Totals reported by Crossref are for the whole index, not for the topic. |
| `data/raw/arxiv/` | raw API responses, 10 files, 0.2 MB (one file per query page; cached in `_tools/biblio-cache`) | | | Response formats differ by database; OpenAlex rate-limits. |
| `data/raw/crossref/` | raw API responses, 35 files, 6.9 MB (one file per query page; cached in `_tools/biblio-cache`) | | | Response formats differ by database; OpenAlex rate-limits. |
| `data/raw/openalex/` | raw API responses, 3 files, 11.8 MB (one file per query page; cached in `_tools/biblio-cache`) | | | Response formats differ by database; OpenAlex rate-limits. |
| `data/raw/s2/` | raw API responses, 9 files, 8.2 MB (one file per query page; cached in `_tools/biblio-cache`) | | | Response formats differ by database; OpenAlex rate-limits. |
| `tables/` | 63 CSV tables: the numbers behind every figure (`R_*` from bibliometrix, `py_*` from Python) | | | see `figures/captions.md` for each caution |

## Variables

### master.csv

| Variable | Meaning and units |
|---|---|
| oa_id | OpenAlex work id (W...) |
| doi | DOI without URL prefix |
| title / year / date / type / language | bibliographic basics (OpenAlex) |
| source / source_type / publisher / issn | journal or venue and its type |
| authors / n_authors / first_author | author names, ';'-separated |
| institutions / countries / first_author_country / corresponding_country / international_collab | affiliations and ISO-2 country codes; international_collab = more than one country |
| cited_by_count / fwci / local_citations / n_refs | OpenAlex citations at pull date; field-weighted citation impact; citations from other corpus records; length of reference list |
| is_oa / oa_status / oa_url / best_pdf_url / all_pdf_urls / best_oa_landing | open-access status and links (OpenAlex) |
| sublit / sublits_all / origin / found_in / relevance | which sub-literature the record was found for; how it entered (search, snowball, seed); databases that returned it; relevance score used to rank evidence |
| primary_topic / subfield / field / domain / keywords / topics / concepts | OpenAlex classification (machine-assigned) |
| abstract / has_abstract | abstract text rebuilt from OpenAlex inverted index; flag |
| is_retracted | OpenAlex retraction flag |
| sr | short reference label used in bibliometrix |
| crossref_cited_by / crossref_n_refs / s2_citation_count / s2_pdf_url | cross-checks from Crossref and Semantic Scholar |

### evidence-table.csv

| Variable | Meaning and units |
|---|---|
| rank, citation, year, doi_or_link, open_access_link, oa_status, pdf_in_folder | identification and access |
| sub_literature, study_type, country_or_setting, data, method | coding by the agent from title and abstract |
| main_finding_from_abstract, read_status | one line from the abstract; 'abstract read' or 'metadata only' (no record was read in full unless marked) |
| relation_to_seans_paper | agent's judgement |
| local_citations, global_citations_openalex, openalex_id | citation counts at pull date |

### citation_edges.csv

| Variable | Meaning and units |
|---|---|
| citing, cited | OpenAlex ids; edge = citing record lists cited record in its references |

### tables/R_*.csv, tables/py_*.csv

| Variable | Meaning and units |
|---|---|
| (varies) | each table holds the numbers behind the figure of the same name; see figures/captions.md |

Counts (citations, records) have no unit beyond 'number of'; years are calendar years; `fwci` is a ratio (1 = world average for field, year and type).


---

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
