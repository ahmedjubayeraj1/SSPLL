#!/bin/bash
# run_corr_pvt.sh - step 7: Spectre vs ngspice device correlation over corners and temperature.
#
#   bash run_corr_pvt.sh frozen [FROZEN_DIR]
#       Spectre on the converted frozen models (make_spectre_models.py output, default ~/sky130A_frozen_spectre).
#       Must PASS: every value within 0.5% of expected_pvt.csv.
#   bash run_corr_pvt.sh kit KIT_LIB [SECTION_MAP]
#       Spectre on the Virtuoso kit's OWN models (e.g. .../sky130_release_0.0.4/models/sky130.lib.spice).
#       No pass/fail: measures how far the kit is from the frozen reference (the "difference" step 7 asks for).
#       SECTION_MAP renames corners if the kit uses other section names, e.g. "tt=tt ss=ss ff=ff sf=sf fs=fs".
#       Corners the kit does not have are reported as missing.
# Results: out_<mode>/<corner>_<temp>/ (psfascii), summary in result_<mode>.md (copied to ~/Desktop if it exists).
source ~/cadence_env.sh 2>/dev/null
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE" || exit 1
MODE=${1:-frozen}
CORNERS="tt ss ff sf fs ll hh hl lh"; TEMPS="-40 27 110"
if [ "$MODE" = frozen ]; then
  FZ=${2:-$HOME/sky130A_frozen_spectre}
  [ -f "$FZ/sspll_kit_wrap.spice" ] || { echo "no $FZ/sspll_kit_wrap.spice - run make_spectre_models.py first"; exit 1; }
elif [ "$MODE" = kit ]; then
  KIT=$2; [ -f "$KIT" ] || { echo "usage: $0 kit /path/to/kit/models/sky130.lib.spice ['tt=tt ss=ss ...']"; exit 1; }
  declare -A MAP; for kv in $3; do MAP[${kv%%=*}]=${kv#*=}; done
else echo "mode must be frozen or kit"; exit 1; fi
which spectre >/dev/null || { echo "spectre not in PATH (source your Cadence setup first)"; exit 1; }
rm -rf "out_$MODE"; mkdir -p "out_$MODE"
for c in $CORNERS; do for t in $TEMPS; do
  d="out_$MODE/${c}_${t}"; mkdir -p "$d"
  if [ "$MODE" = frozen ]; then
    M="include \"$FZ/sky130A/libs.tech/ngspice/sky130.lib.spice\" section=$c\ninclude \"$FZ/sspll_kit_wrap.spice\""
  else
    s=${MAP[$c]:-$c}
    if ! grep -qiE "^\s*\.?(lib|section)\s+$s\b" "$KIT"; then echo "kit has no section '$s' ($c) - skipped"; echo missing > "$d/MISSING"; continue; fi
    M="include \"$KIT\" section=$s"
  fi
  sed -e "s#%MODELS%#$M#" -e "s#%TEMP%#$t#" corr_pvt.scs.tmpl > "$d/corr.scs"
  ( cd "$d" && spectre corr.scs -format psfascii -raw ./psf +log spectre.log > /dev/null 2>&1 )
  if grep -q "ERROR" "$d/spectre.log"; then echo "$c $t: ERROR (first lines below)"; grep -m3 -A2 ERROR "$d/spectre.log"; else echo "$c $t: done"; fi
done; done
tar czf "corr_pvt_$MODE.tar.gz" "out_$MODE"
if ! command -v python3 >/dev/null; then
  # old Cadence VMs (CentOS 6/7) may have no python3: send corr_pvt_$MODE.tar.gz and it is compared outside the VM
  [ -d ~/Desktop ] && cp "corr_pvt_$MODE.tar.gz" ~/Desktop/
  echo "python3 not found: results packed in corr_pvt_$MODE.tar.gz (also on ~/Desktop); compare with"
  echo "  python3 compare_pvt.py out_$MODE expected_pvt.csv $MODE      (on any machine with python3)"; exit 0
fi
python3 compare_pvt.py "out_$MODE" expected_pvt.csv "$MODE" | tee "result_$MODE.md"; rc=${PIPESTATUS[0]}
if [ -d ~/Desktop ]; then cp "result_$MODE.md" ~/Desktop/ && echo "copied result_$MODE.md to ~/Desktop"; fi
exit $rc
