# learn/ — Phases 1–6: theory notebooks with interactive figures and interview questions

| Notebook | Roadmap steps | Interview questions |
|---|---|---|
| `phase1_fundamentals.ipynb` | 11–24 PLL fundamentals | 164 |
| `phase2_type1.ipynb` | 25–32 Type-I PLL, limits, fixes | 78 |
| `phase3_type2_cppll.ipynb` | 33–45 Type-II charge-pump PLL (incl. the 50 MHz × 32 baseline design) | 118 |
| `phase4_sspll.ipynb` | 46–58 sub-sampling PLL (incl. FLL acquisition simulation) | 112 |
| `phase5_vcdl.ipynb` | 59–64 voltage-controlled delay line / NCB (SKY130 ngspice lab) | 50 |
| `phase6_ffnc.ipynb` | 65–71 feedforward noise cancellation and calibration | 58 |

Every step: what happens → how (equations, Razavi notation) → why → interactive figure (slider inside the plot) → try it →
interview questions (click to open the answer). Design numbers follow the submitted proposal (50 MHz × 32 = 1.6 GHz, f_c ≈ 2.5 MHz).

**Use in Jupyter:** `./tools/setup_python.sh`, then `source .venv/bin/activate && cd learn && jupyter lab` and *Run All*.
**Web version:** `python3 learn/build/export.py` writes `learn/html/` (open `index.html`; works offline).

| Folder / file | Content |
|---|---|
| `build/phase*.py` | the notebook sources (edit here, not in the .ipynb) — `build/nb.py` is the builder |
| `build/export.py` | build + execute + export to HTML |
| `sspll_learn.py` | slider-plot helper, Bode helper, cycle-by-cycle CP-PLL simulator, closed-form loop-filter design |
| `spice/pll_phase_domain.cir` | ngspice phase-domain PLL (checks H(s) against Python to 1e-4 dB) |
| `spice/inv_delay_vdd.sp`, `spice/vcdl_starved.sp`, `spice/run_sky130.sh` | SKY130 delay labs of Phase 5 (`PDK_ROOT=... ./run_sky130.sh`) |
| `data/*.csv` | results of the ngspice runs that the notebooks plot |

Assumptions to be replaced in Phase 7: K_VCO = 2π·300 MHz/V (fine tuning), sampled amplitude A = 0.5 V, I_p = 100 µA (Type-II baseline).
