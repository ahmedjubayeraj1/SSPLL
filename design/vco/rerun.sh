#!/bin/bash
# step-74 characterisation re-run with the PDK .spiceinit (15 Nov 2026)
cd "$(dirname "$0")"
python3 step74_point.py q3 1.3e-3 > data/log_rerun.txt 2>&1
python3 step74_point.py base 1.2e-3 >> data/log_rerun.txt 2>&1
python3 step74_char.py q3 >> data/log_rerun.txt 2>&1
python3 step74_extra.py >> data/log_rerun.txt 2>&1
echo ALLDONE >> data/log_rerun.txt
