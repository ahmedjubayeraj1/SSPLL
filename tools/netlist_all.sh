#!/usr/bin/env bash
# netlist_all.sh - netlist every schematic in xschem/ with xschem in batch mode.
#   cells       -> netlist/schematic/<cell>.spice   (as a .subckt, for LVS and checks)
#   testbenches -> netlist/tb/<tb>.spice            (top level, ready for ngspice)
# Logs go to netlist/netlist.log. Run from anywhere:  ./tools/netlist_all.sh
set -u
source "$(dirname "$0")/env.sh"
cd "$SSPLL_ROOT/xschem" || { echo "no xschem/ directory"; exit 1; }
mkdir -p ../netlist/schematic ../netlist/tb
log=../netlist/netlist.log; : > "$log"
n=0; fail=0
for s in *.sch tb/*.sch; do
  [ -f "$s" ] || continue
  case "$s" in
    tb/*) out=../netlist/tb; extra=() ;;
    *)    out=../netlist/schematic; extra=(--tcl "set top_subckt 1") ;;
  esac
  echo "== $s" >> "$log"
  if timeout 120 xschem -n -s -q -x -r "${extra[@]}" --netlist_path "$out" "$s" >> "$log" 2>&1; then n=$((n+1)); else fail=$((fail+1)); echo "FAILED: $s" | tee -a "$log"; fi
done
echo "netlisted $n schematics, $fail failed (log: netlist/netlist.log)"
