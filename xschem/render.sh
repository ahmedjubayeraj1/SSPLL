#!/bin/bash
# render.sh file.sch out.png [WxH] - PNG of a schematic (needs xvfb-run), whole drawing zoomed to fit
f=$1; o=$2; s=${3:-2400x1600}
cd "$(dirname "$0")"; export PDK_ROOT=${PDK_ROOT:-/home/claude/pdk} PDK=${PDK:-sky130A}
xvfb-run -a -s "-screen 0 ${s}x24" xschem -q --rcfile xschemrc \
  --tcl "set enable_layer(15) 0; set enable_layer(17) 0" \
  --command "xschem zoom_full; xschem print png $o ${s%x*} ${s#*x}; xschem exit closewindow" "$f" >/dev/null 2>&1
