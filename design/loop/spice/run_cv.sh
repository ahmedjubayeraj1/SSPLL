#!/bin/bash
# run_cv.sh - C-V of the loop-filter MOS cap and MIM tile over corners and temperature (loop design).
#   PDK_ROOT=/path/to/pdk ./run_cv.sh      writes ../data/moscap_cv.csv
set -e
cd "$(dirname "$0")"
: "${PDK_ROOT:?set PDK_ROOT (directory that contains sky130A)}"
cp "$PDK_ROOT/sky130A/libs.tech/ngspice/spinit" .spiceinit
mkdir -p ../data
echo "corner,temp,vg,c_mos_fF,c_mim_fF" > ../data/moscap_cv.csv
for c in tt ss ff; do for t in -40 27 110; do
  sed -e "s#PDK_ROOT#$PDK_ROOT#" -e "s#CORNER#$c#" -e "s#TEMP#$t#" moscap_cv.sp > /tmp/_cv.sp
  ngspice -b /tmp/_cv.sp > /tmp/_cv.log 2>&1
  tail -n +2 cv_out.txt | awk -v c=$c -v t=$t '{printf "%s,%s,%s,%s,%s\n", c, t, $1, $2, $3}' >> ../data/moscap_cv.csv
done; done
rm -f cv_out.txt
echo "-> ../data/moscap_cv.csv"
