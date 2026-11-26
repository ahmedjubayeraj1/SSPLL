#!/bin/bash
# run_rc.sh - loop-filter R and MIM C over tt/ll/hh/hl/lh and -40/27/110 C (loop design).
#   PDK_ROOT=/path/to/pdk ./run_rc.sh      writes ../data/rc_corners.csv
set -e
cd "$(dirname "$0")"
: "${PDK_ROOT:?set PDK_ROOT (directory that contains sky130A)}"
cp "$PDK_ROOT/sky130A/libs.tech/ngspice/spinit" .spiceinit
mkdir -p ../data
echo "corner,temp,r_high_po_ohm,r_xhigh_po_ohm,c_mim_fF" > ../data/rc_corners.csv
for c in tt ll hh hl lh; do for t in -40 27 110; do
  sed -e "s#PDK_ROOT#$PDK_ROOT#" -e "s#CORNER#$c#" -e "s#TEMP#$t#" rc_corners.sp > /tmp/_rc.sp
  ngspice -b /tmp/_rc.sp > /tmp/_rc.log 2>&1
  awk -v c=$c -v t=$t '{printf "%s,%s,%s,%s,%s\n", c, t, $1, $2, $3}' rc_out.txt >> ../data/rc_corners.csv
done; done
rm -f rc_out.txt
echo "-> ../data/rc_corners.csv"
