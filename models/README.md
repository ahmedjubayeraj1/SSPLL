# models/ - phase-domain models (roadmap step 9)

| File | What it is |
|---|---|
| `pllmodel/` | the model: loop transfer, noise sources, FFNC path, jitter, bandwidth optimum; design points `TYP`, `PESS` (proposal basis), `TYPE2_*` (Type-II baseline) |
| `template.ipynb` | template notebook: loop, phase noise, jitter, bandwidth sweep, FFNC gain error, plugging in simulated curves. Copy it for each study |
| `make_template.py` | writes `template.ipynb` (edit cells there) |
| `step8_variants.py` | Type-II vs SSPLL vs SSPLL + FFNC table and figure (step 8) |
| `selftest.py` | checks the install and that the model reproduces the proposal (2.29 / 1.40 ps) |
| `requirements.txt` | numpy, scipy, matplotlib, JupyterLab |

Setup (once): `./tools/setup_python.sh` (creates `.venv`, installs, registers the "Python (sspll)" kernel, runs the self-test).
Then `source .venv/bin/activate && jupyter lab models/template.ipynb`.
Figures go to `models/out/` (not committed). Commit notebooks with cleared outputs.

The equations are written out in `pllmodel/__init__.py` and derived in the documentation (docs/book, chapters 2-6).
