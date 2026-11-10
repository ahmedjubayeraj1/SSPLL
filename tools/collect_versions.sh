#!/usr/bin/env bash
# collect_versions.sh - record the exact tool and PDK versions on this machine.
#
# Run it inside the Linux machine (or VMware VM) where you design:
#     chmod +x tools/collect_versions.sh
#     ./tools/collect_versions.sh > versions_pc.txt
# Then compare versions_pc.txt with the [reference] block in versions.txt.
# Missing tools are reported as "not found"; the script never changes anything.

v() { command -v "$1" >/dev/null 2>&1; }
line() { printf '%-18s = %s\n' "$1" "$2"; }
first() { head -n 1 | tr -d '\r'; }

echo "# versions_pc.txt  generated $(date -u +%Y-%m-%dT%H:%MZ) on $(hostname)"
echo "[machine]"
line os "$( (. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME") || uname -sr)"
line kernel "$(uname -r)"
if [ -d /foss ]; then
  line container "IIC-OSIC-TOOLS (found /foss); tag: ${IIC_OSIC_TOOLS_VERSION:-unknown - check 'docker ps' on the host}"
else
  line container "none (native install)"
fi

echo "[open_source_tools]"
if v xschem;  then line xschem  "$(xschem --version 2>&1 | first)"; else line xschem "not found"; fi
if v ngspice; then line ngspice "$(ngspice --version 2>&1 | grep -o 'ngspice-[0-9.]*' | first)"; else line ngspice "not found"; fi
if v magic;   then line magic   "$(magic --version 2>&1 | first)"; else line magic "not found"; fi
NG=$(command -v netgen || command -v netgen-lvs)
if [ -n "$NG" ]; then line netgen "$("$NG" -noconsole </dev/null 2>&1 | grep -io 'netgen[^0-9]*[0-9][0-9.]*' | first) ($NG)"; else line netgen "not found"; fi
if v klayout; then line klayout "$(klayout -v 2>&1 | first)"; else line klayout "not found (or Python module only)"; fi
if v Xyce;    then line xyce    "$(Xyce -v 2>&1 | first)"; else line xyce "not found"; fi
if v python3; then
  line python "$(python3 --version 2>&1)"
  line cace   "$(python3 -c 'import importlib.metadata as m; print(m.version("cace"))' 2>/dev/null || echo 'not installed')"
  line numpy_scipy_mpl "$(python3 -c 'import numpy,scipy,matplotlib;print(numpy.__version__,scipy.__version__,matplotlib.__version__)' 2>/dev/null || echo 'missing')"
fi

echo "[pdk]"
line PDK_ROOT "${PDK_ROOT:-not set}"
line PDK "${PDK:-not set}"
if [ -n "$PDK_ROOT" ] && [ -n "$PDK" ] && [ -f "$PDK_ROOT/$PDK/.config/nodeinfo.json" ]; then
  python3 - "$PDK_ROOT/$PDK/.config/nodeinfo.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print(f"{'open_pdks_commit':18s} = {d.get('commit', {}).get('open_pdks', 'unknown')}")
print(f"{'open_pdks_version':18s} = {d.get('build', {}).get('open_pdks', 'unknown')}")
print(f"{'sky130_fd_pr':18s} = {d.get('reference', {}).get('sky130_fd_pr', 'unknown')}")
print(f"{'xschem_sky130':18s} = {d.get('reference', {}).get('xschem_sky130', 'unknown')}")
PY
else
  line open_pdks "unknown (no \$PDK_ROOT/\$PDK/.config/nodeinfo.json)"
fi

echo "[cadence]"
if v virtuoso; then line virtuoso "$( (virtuoso -W || virtuoso -version) 2>&1 | first)"; else line virtuoso "not found in PATH"; fi
if v spectre;  then line spectre  "$( (spectre -W || spectre -version) 2>&1 | first)"; else line spectre "not found in PATH"; fi
# Look for a Cadence-compatible SKY130 kit in the usual places and in cds.lib
kits=$(find "$HOME" /opt /tools /cad 2>/dev/null -maxdepth 4 -type d -iname '*sky130*' 2>/dev/null | head -n 5 | tr '\n' ' ')
line sky130_kit_dirs "${kits:-none found - write the kit name and version by hand}"
for f in "$HOME/cds.lib" ./cds.lib; do
  [ -f "$f" ] && line "cds.lib($f)" "$(grep -i sky130 "$f" | tr '\n' ';' | cut -c1-200)"
done
echo "# end"
