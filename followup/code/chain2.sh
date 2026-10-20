#!/bin/bash
cd /d/Research-Publishing/03-fx-data-artefact/followup
V=D:/Research-Publishing/03-fx-data-artefact/.venv/Scripts/python
mkdir -p logs
runR() { log=$1; shift; $V code/runlog.py rerun/logs/$log rerun/code $V ../../code/runstat.py "$@"; }
runF() { log=$1; shift; $V code/runlog.py logs/$log code $V runstat.py "$@"; }
runR 12_step2_build_daily_idx_A.log build_daily.py GRXEUR JPXJPY NSXUSD SPXUSD
runR 13_step2_build_daily_idx_B.log build_daily.py UDXUSD UKXGBP WTIUSD
runF 20_switch_date_A.log switch_date.py EURUSD USDJPY AUDUSD GBPUSD USDCHF USDCAD
runF 21_switch_date_B.log switch_date.py NZDUSD EURGBP EURJPY GBPJPY XAUUSD XAGUSD
runF 22_switch_date_C.log switch_date.py SPXUSD NSXUSD UKXGBP GRXEUR JPXJPY UDXUSD WTIUSD
runF 23_break_2015_A.log break_2015.py build EURUSD USDJPY GBPUSD AUDUSD USDCHF
runF 24_break_2015_B.log break_2015.py build USDCAD NZDUSD EURGBP EURJPY GBPJPY
runF 25_break_2015_test.log break_2015.py test
runF 26_robustness.log robustness.py
echo CHAIN2 DONE > logs/chain2_done.txt
