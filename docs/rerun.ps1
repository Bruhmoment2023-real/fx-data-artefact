<#
Rebuild the main results of paper 03 (bid-only rollover artefact / timestamp error in histdata.com M1 FX data) from raw data, in order.
Usage:  powershell -File rerun.ps1 [-Quick] [-Part analysis|literature|all]
  -Quick   run only the cheap checks: copy code to a work folder, run the 26 unit tests, import-check every script (default for first use).
  analysis    the data analysis (steps 1-7 of code\README.md), run in a WORK COPY so the pack's results\ are never overwritten.
  literature  the literature map (bibliometrics\) and depth layers 2-3.
Nothing here writes to the pack's code\, results\ or to followup\. D: must be present; raw histdata zips are read from D:\Malaysian-SNR\phase3\data\histdata_zips (read-only).
Heavy steps (1, 2, 3, 5, 6) take 1-3 minutes per pair; the literature part takes about 1.5 hours of mostly network wait (OpenAlex is rate-limited).
#>
param([switch]$Quick, [ValidateSet('analysis','literature','all')][string]$Part = 'analysis')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path 'D:\')) { throw 'D: is missing - stopping.' }
$P    = 'D:\Research-Publishing\03-fx-data-artefact'
$Work = "$P\depth\appendix\rerun-work"
$py   = "$P\.venv\Scripts\python.exe"
$bpy  = 'D:\Research-Publishing\_tools\biblio-venv\Scripts\python.exe'
$env:PYTHONIOENCODING = 'utf-8'

if ($Part -in 'analysis','all') {
  New-Item -ItemType Directory -Force $Work | Out-Null
  Copy-Item "$P\code" "$Work\" -Recurse -Force -Exclude '__pycache__'
  Push-Location "$Work\code"
  Write-Host '== tests (26 expected; 4 use the real archive)'
  & $py -m pytest -q test_fxclock.py
  Write-Host '== import check of every analysis script'
  foreach ($f in 'fxio','fxclock','build_minute_stats','build_daily','demo_rule','analyze_ticks','analyze_profiles','analyze_fxcm','make_figures') { & $py -c "import ast,sys; ast.parse(open('$f.py',encoding='utf-8').read()); print('syntax ok: $f')" }
  if (-not $Quick) {
    # outputs go to $Work\results (code resolves results\ relative to its own folder's parent)
    $pairs = 'EURUSD','USDJPY','GBPUSD','AUDUSD'
    & $py build_minute_stats.py @pairs        # step 1
    & $py build_daily.py @pairs               # step 2
    & $py demo_rule.py                         # step 4 (reads results\daily)
    & $py analyze_profiles.py                  # step 5
    & $py make_figures.py                      # step 7
    Write-Host 'Steps 3 and 6 (downloads of tick and FXCM files) are not run here; see code\README.md. Compare $Work\results\tables with $P\results\tables.'
  }
  Pop-Location
}
if ($Part -in 'literature','all') {
  $b = "$P\bibliometrics"
  if ($Quick) { Write-Host 'Quick: literature part skipped (needs the network and ~1.5 h).' }
  else {
    & $bpy 'D:\Research-Publishing\_tools\biblio-kit\pipeline.py' $b search enrich snowball refs master
    if (Test-Path "$b\data\clean\handscreen_exclusions.json") { & $bpy 'D:\Research-Publishing\_tools\biblio-kit\handscreen.py' $b apply; & $bpy 'D:\Research-Publishing\_tools\biblio-kit\pipeline.py' $b master }
    & powershell -NoProfile -File 'D:\Research-Publishing\_tools\biblio-kit\finish.ps1' '03-fx-data-artefact'   # R, figures, evidence table, PDFs, docs
    & $bpy 'D:\Research-Publishing\_tools\depth-kit\burst_mainpath.py' $b                                   # depth layer 3
    & $bpy 'D:\Research-Publishing\_tools\depth-kit\citations.py' $P "$P\depth\citations\extra_nodoi.json"   # depth layer 2
    & $bpy 'D:\Research-Publishing\_tools\depth-kit\appendix.py' $P "$P\depth\appendix\_extra_dictionary.md" # data dictionary
  }
}
