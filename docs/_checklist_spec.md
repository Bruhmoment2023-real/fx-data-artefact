## Data availability
- Raw price data: HistData.com free M1 bars and ticks (no licence page found; FAQ says "use at your own risk"); FXCM public candle archive (README: personal use, EULA not read). **Not redistributable**: publish derived tables, figures and code only, cite the sites and download dates (13 Oct 2026). Raw zips live in `D:\Malaysian-SNR\phase3\data\histdata_zips` (read-only, not copied into this pack).
- Derived tables (`results\tables\*.csv`) and the 7 figures are in the pack and can be shared.
- Literature data: public metadata (see below); `bibliometrics\data\`.

## Code availability
- `code\` (analysis; 26 tests, 26 passed on 2026-10-13 and again on 2026-10-17 in `depth\appendix\rerun.ps1 -Quick`); `followup\rerun\` holds a separate full rerun by another agent in which all 19 tables, 12 and 60 intermediates and 7 figures were identical (`followup\rerun-report.md`).
- `depth\appendix\rerun.ps1` rebuilds in a work copy; no random numbers in the analysis code (grep for seed/random/bootstrap found nothing), so reruns on the same raw files are deterministic.
- Analysis software: Python 3.12.10, numpy 2.5.4, pandas 3.0.6, pyarrow 26.0.0, matplotlib 3.11.2, pytest 9.1.1, tzdata 2026.5, requests 2.34.2 (from `followup\rerun\logs\00_versions.log`).
