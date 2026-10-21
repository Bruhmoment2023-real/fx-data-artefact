# A rollover artefact and a clock error in free forex minute data: how histdata.com bars manufacture a time-of-day edge

Archived on Zenodo: https://doi.org/10.5281/zenodo.23537746 (this DOI always points to the latest version).

Sean Solano Paul, Independent researcher, Bengaluru, India. Funding: none. Competing interests: none.

## Summary

Free one-minute forex bars from histdata.com are widely used for retail backtesting. This repository supports a study of two
problems with them and how they combine. First, from late 2014 the bar stamped 16:59 New York, the last minute before the daily 17:00
rollover, has a large negative mean return in all ten currency pairs examined (-0.77 to -2.58 basis points in 2015-2026, t-statistics -28 to -38),
and it is the most negative of the 1,440 minutes of the day in every pair. The bars are built from bid prices; at the rollover the spread widens
to ten to fifteen times its daytime level, so the bid falls while the ask rises by about as much and the mid barely moves. Second, the timestamps
are not the fixed UTC-5 clock the vendor documents: files up to 2018 follow New York wall time with daylight saving, and files from 2019 follow the
European daylight-saving calendar, so a user who follows the documentation is an hour out on 59% to 65% of trading days. Together these let a one-line
rule ("sell at 16:00 New York, buy back at 17:00") show annualised Sharpe ratios of 2.1 to 7.7 at zero cost; masking ten minutes around the rollover
removes most of this, and the same rule priced at executable bid and ask prices loses heavily. The repository contains the analysis code, a tested
clock-conversion and rollover-mask module, the results tables and figures, and a ten-step check.

## Repository layout

| Path | Contents |
|---|---|
| `code/` | Analysis pipeline and the reusable `fxclock.py` module with `test_fxclock.py`; `code/README.md` documents each script; `PRESPEC.txt` is the frozen rule definition |
| `results/` | `RESULTS-SUMMARY.md`, tables `T1`-`T7`, `F1`-`F3` and the demonstration-rule tables (`results/tables/`), figures 1-7 (`results/figures/`) |
| `followup/` | Follow-up analyses: clock-switch dating, the 2015 break, robustness checks (`followup/code/`, `followup/tables/`, `followup/logs/`), the clean re-run tables, figures and logs (`followup/rerun/`) and literature search logs (`followup/lit/`) |
| `docs/` | Design and pre-specification (`design.md`, `ADDENDUM-2026-10-13.md`), prior-work notes, data dictionary, open facts, robustness and re-run reports |
| `literature/` | Reference list (`references.bib`, `references.ris`) |
| `bibliometrics/` | A literature map (OpenAlex-based): scripts, tables, figures, search protocol and the cleaned corpus metadata |

## How to reproduce

Python 3.12. Install: `pip install -r requirements.txt`. Run scripts from `code/`.

1. Obtain the raw data (below) and put the histdata.com Generic-ASCII M1 zips, named `<PAIR>_<YEAR>[...].zip`, in `data/raw/histdata_zips/`
   (or set the environment variable `HISTDATA_ZIPDIR` to the folder).
2. `python build_minute_stats.py EURUSD USDJPY GBPUSD AUDUSD` (and the other pairs)
3. `python build_daily.py EURUSD USDJPY GBPUSD AUDUSD`
4. `python fetch_ticks.py EURUSD:2017:1 ...` then `python analyze_ticks.py`
5. `python demo_rule.py`
6. `python analyze_profiles.py`
7. `python fetch_fxcm.py EURUSD:2012-2023 ...` then `python analyze_fxcm.py EURUSD USDJPY AUDUSD`
8. `python make_figures.py`
9. Tests: `python -m pytest -q test_fxclock.py` (26 tests; the 4 that read real vendor files skip if the archive is absent; 22 passed, 4 skipped when checked without the archive).

Minimal use of the clock module:

```python
import pandas as pd, fxclock
utc = fxclock.label_to_utc(df["label"])
keep = ~fxclock.rollover_mask(utc, before=5, after=65)
print(fxclock.diagnose_clock(df["label"]))
```

`code/README.md` gives measured run times. Follow-up scripts are in `followup/code/` (each logs to `followup/logs/`).

## Data sources and licences

| Source | Used for | Licence / terms |
|---|---|---|
| histdata.com free M1 bar files (Generic ASCII) and tick files | Primary data | Vendor terms; no redistribution licence granted. Not included. Download from https://www.histdata.com/download-free-forex-data/ (one zip per pair and year; tick files via the site's public download form, which `code/fetch_ticks.py` automates). |
| FXCM public one-minute candle files (bid and ask OHLC, UTC) | Independent second source for the clock and bid/ask checks | Vendor terms. Not included. `code/fetch_fxcm.py` downloads them from the public URL pattern `https://candledata.fxcorporate.com/m1/<PAIR>/<YEAR>/<WEEK>.csv.gz`. |
| OpenAlex, Crossref, Semantic Scholar, ERIC, arXiv, OpenCitations metadata | Literature map in `bibliometrics/` | OpenAlex is CC0; other services' terms apply to raw responses (not included). |
| Author's derived tables, figures, results | Everything under `results/`, `followup/` tables | CC BY 4.0 (`LICENSE-DATA.md`) |
| Code | All scripts | MIT (`LICENSE`) |

## Not included and why

- Abstract text of third-party papers (the `abstract`/`AB` columns and abstract-derived quote columns of the bibliographic tables, and abstract fields in the OpenAlex JSON). Identifiers, titles, years, venues, keywords and citation data are kept; re-fetch abstracts with the bibliometrics pipeline if needed.
- Per-paper reading notes on the literature (they contain quotations from copyrighted papers) and the literature gap-analysis note (scoping). The scripts that built the notes are kept; run them on your own copies of the papers.
- Raw vendor data: histdata.com zips and tick files, FXCM weekly candle files (`data_fxcm/`, `data_ticks/`, `followup/fxcm_extra/`) - third-party terms, and large (about 450 MB). Re-download with the scripts above.
- Large derived intermediates: `results/daily/` and `results/minute_stats/` parquet files (about 430 MB), and identical copies under `followup/rerun/results/`. They are per-minute and per-day aggregates computed directly from the vendor bars; regenerate with steps 2-3 (about 60-95 s per pair).
- Full-text PDFs of papers (`bibliometrics/pdfs/`, `followup/lit/papers/`), the extracted text of those papers, and archived copies of web pages and GitHub issue captures (`followup/archive/`, `followup/raw/`) - copyrighted or third-party material. The citations are in `literature/citations/`.
- Raw API responses for the literature search (`bibliometrics/data/raw/`) and `.rds` caches - regenerate with `bibliometrics/python/pipeline.py`; interactive HTML figures and their JavaScript libraries (PNG/SVG versions are kept).
- Virtual environment, caches and scratch working files.

## Citation

Solano Paul, S. (2026). *A rollover artefact and a clock error in free forex minute data: how histdata.com bars manufacture a time-of-day edge* (software and data repository). See `CITATION.cff`. A Zenodo DOI will be added when the repository is made public.
