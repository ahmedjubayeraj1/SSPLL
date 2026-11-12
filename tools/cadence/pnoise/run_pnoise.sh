#!/bin/bash
# run_pnoise.sh - run the ring phase-noise bench and pack everything needed for the comparison.
# Use:  cd ~/sky130A_frozen_spectre ; bash pnoise/run_pnoise.sh
source ~/cadence_env.sh 2>/dev/null
cd "$(dirname "$0")/.." || exit 1
rm -rf pnoise/out pnoise/pnoise.log
spectre pnoise/ring5_pnoise.scs -format psfascii -raw ./pnoise/out +log pnoise/pnoise.log > /dev/null 2>&1
echo "=== errors ===";            grep -m10 "ERROR" pnoise/pnoise.log
echo "=== PSS frequency ===";     grep -i -m5 -E "fundamental|frequency.*=|oscillat" pnoise/pnoise.log
echo "=== log tail ===";          tail -4 pnoise/pnoise.log
tar czf ~/Desktop/pnoise_results.tar.gz pnoise/pnoise.log pnoise/out 2>/dev/null
ls -lh ~/Desktop/pnoise_results.tar.gz
