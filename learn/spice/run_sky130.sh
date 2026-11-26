#!/bin/bash
# run_sky130.sh - run the SKY130 lab netlists of Phase 5 (inv_delay_vdd.sp, vcdl_starved.sp) with your PDK.
#   PDK_ROOT=/path/to/pdk ./run_sky130.sh            (PDK_ROOT must contain sky130A; e.g. from tools/env.sh)
# Writes ../data/inv_delay_vdd.csv and ../data/vcdl_starved.csv, which the Phase 5 notebook plots.
set -e
cd "$(dirname "$0")"
: "${PDK_ROOT:?set PDK_ROOT (directory that contains sky130A)}"
cp "$PDK_ROOT/sky130A/libs.tech/ngspice/spinit" .spiceinit
for f in inv_delay_vdd.sp vcdl_starved.sp; do
  sed "s#PDK_ROOT#$PDK_ROOT#" "$f" > "/tmp/_$f"
  (cd "$(pwd)" && ngspice -b "/tmp/_$f" > "/tmp/_$f.log" 2>&1) && echo "$f done"
done
