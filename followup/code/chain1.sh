#!/bin/bash
# sequential, one job at a time: pack steps 4, 5, 3(analysis only), 6(analysis only), 7 on the rerun copy
cd /d/Research-Publishing/03-fx-data-artefact/followup
V=D:/Research-Publishing/03-fx-data-artefact/.venv/Scripts/python
run() { log=$1; shift; $V code/runlog.py rerun/logs/$log rerun/code $V ../../code/runstat.py "$@"; }
run 06_step4_demo_rule.log demo_rule.py
run 07_step5_analyze_profiles.log analyze_profiles.py
run 08_step3_analyze_ticks.log analyze_ticks.py
run 09_step6_analyze_fxcm.log analyze_fxcm.py EURUSD USDJPY AUDUSD
run 10_step7_make_figures.log make_figures.py
echo CHAIN1 DONE > rerun/logs/chain1_done.txt
