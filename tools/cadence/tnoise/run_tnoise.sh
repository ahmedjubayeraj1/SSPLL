#!/bin/bash
# run_tnoise.sh - transient-noise period jitter of the ring. Use: cd ~/sky130A_frozen_spectre ; bash tnoise/run_tnoise.sh
source ~/cadence_env.sh 2>/dev/null
cd "$(dirname "$0")/.." || exit 1
rm -rf tnoise/out tnoise/tnoise.log
echo "running (several minutes) ..."
spectre tnoise/ring5_tnoise.scs -format psfascii -raw ./tnoise/out +log tnoise/tnoise.log > /dev/null 2>&1
{ echo "=== A) noiseless ===";  awk -f tnoise/periods.awk tnoise/out/trq.tran.tran
  echo "=== B) with noise ==="; awk -f tnoise/periods.awk tnoise/out/trn.tran.tran
  echo "=== errors ===";        grep -m10 "ERROR" tnoise/tnoise.log
  echo "=== warnings about noise ==="; grep -i -m5 "noise" tnoise/tnoise.log | grep -i -E "warn|ignor|not a valid"
  echo "=== log tail ===";      tail -3 tnoise/tnoise.log; } | tee tnoise/tnoise_results.txt
cp tnoise/tnoise_results.txt ~/Desktop/
