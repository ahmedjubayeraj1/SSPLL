#!/bin/bash
# run.sh deck.spice [corner] [temp]
#   Runs one testbench deck with ngspice in batch mode.
#   * copies the PDK's spinit to .spiceinit in a scratch folder (sets the HSPICE-compatibility mode the sky130
#     models need, and the KLU solver)
#   * replaces the placeholders __PDK__ (path of sky130A), __CORNER__ (tt/ss/ff/sf/fs) and __TEMP__ in the deck
#   * runs "ngspice -b" and leaves the raw output, logs and data files in tb/out/<deck name>/
# Environment: PDK_ROOT (default /home/claude/pdk on this server; on your PC e.g. ~/.volare or /usr/local/share/pdk)
set -e
deck=$(realpath "$1"); corner=${2:-tt}; temp=${3:-27}
PDK_ROOT=${PDK_ROOT:-/home/claude/pdk}; PDK=${PDK:-sky130A}
here=$(dirname "$(realpath "$0")")
out="$here/out/$(basename "${deck%.spice}")"; mkdir -p "$out"
cp "$PDK_ROOT/$PDK/libs.tech/ngspice/spinit" "$out/.spiceinit"
sed -e "s|__PDK__|$PDK_ROOT/$PDK|g" -e "s|__CORNER__|$corner|g" -e "s|__TEMP__|$temp|g" \
    -e "s|__DUT__|$here/dut|g" "$deck" > "$out/run.spice"
cd "$out" && ngspice -b run.spice > ngspice.log 2>&1 || { tail -30 ngspice.log; exit 1; }
grep -E "^[a-zA-Z_0-9]+ *= |^RESULT" ngspice.log | grep -v -E "^(Reference value|No\. of Data)" || true
echo "(full log: $out/ngspice.log)"
