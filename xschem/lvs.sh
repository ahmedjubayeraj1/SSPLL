#!/bin/bash
# lvs.sh cell.sch reference.spice cellname - netlist a schematic with xschem (LVS format, top level as .subckt) and
# compare it with a reference SPICE netlist using netgen: proves the drawing is the circuit that was simulated.
cd "$(dirname "$0")"; export PDK_ROOT=${PDK_ROOT:-/home/claude/pdk} PDK=${PDK:-sky130A}
sch=$1; ref=$2; cell=$3
NETGEN=$(command -v netgen || command -v netgen-lvs)
mkdir -p netlist
xvfb-run -a xschem -q -x --rcfile xschemrc --tcl "set lvs_netlist 1" \
  --command "xschem set format lvs_format; xschem netlist; xschem exit closewindow" -o netlist "$sch" >/dev/null 2>&1
net=netlist/$(basename "${sch%.sch}").spice
$NETGEN -batch lvs "$net $cell" "$ref $cell" "$PDK_ROOT/$PDK/libs.tech/netgen/${PDK}_setup.tcl" \
  netlist/${cell}_lvs.out > netlist/${cell}_lvs.log 2>&1
grep -E "Circuits match uniquely|Netlists do not match|Netlists match" netlist/${cell}_lvs.out | tail -1
