#!/bin/bash
# setup_python.sh - roadmap step 9: Python environment for the phase-domain models (models/).
#   ./tools/setup_python.sh          creates .venv in the repo, installs models/requirements.txt,
#                                    registers the Jupyter kernel "sspll" and runs the self-test.
# Inside IIC-OSIC-TOOLS numpy/scipy/matplotlib are already present; the venv still keeps versions reproducible.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PY=${PYTHON:-python3}
$PY -c 'import sys; assert sys.version_info >= (3, 10), "need Python >= 3.10"' || exit 1
[ -d .venv ] || $PY -m venv .venv
. .venv/bin/activate
python -m pip install -q --upgrade pip
python -m pip install -q -r models/requirements.txt
python -m ipykernel install --user --name sspll --display-name "Python (sspll)" > /dev/null
python models/selftest.py
echo
echo "Done. Use it with:   source .venv/bin/activate"
echo "                     jupyter lab models/template.ipynb      (kernel: Python (sspll))"
echo "                     python models/step8_variants.py"
