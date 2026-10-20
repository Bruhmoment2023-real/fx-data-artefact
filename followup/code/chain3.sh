#!/bin/bash
# waits for chain2, then fetches FXCM public candles for two more pairs (README 'ready to run' item) and analyses them. Output isolated in fxcm_extra/.
cd /d/Research-Publishing/03-fx-data-artefact/followup
while [ ! -f logs/chain2_done.txt ]; do sleep 20; done
V=D:/Research-Publishing/03-fx-data-artefact/.venv/Scripts/python
$V code/runlog.py logs/30_fxcm_fetch.log fxcm_extra/code $V ../../code/runstat.py fetch_fxcm.py GBPUSD:2012-2023 USDCHF:2012-2023
$V code/runlog.py logs/31_fxcm_analyze.log fxcm_extra/code $V ../../code/runstat.py analyze_fxcm.py GBPUSD USDCHF
echo CHAIN3 DONE > logs/chain3_done.txt
