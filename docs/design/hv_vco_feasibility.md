# Device-rule migration — VCO feasibility in 5 V devices (18 Nov 2026)

New rule: all analog blocks in `nfet_g5v0d10v5` / `pfet_g5v0d10v5` (L ≥ 0.5 µm) on VDDA 3.3 V; digital in 1.8 V
devices. The ring VCO is analog, so its speed in thick-oxide devices sets the output frequency.

**Method.** `design/feas/hv_vco.py`, transient (ngspice, PDK `.spiceinit`). Every ring node carries a 5 V output
buffer (n 1 / p 2.5 µm driving 10 fF) and 8 fF of wiring. Rings A/B are fed from an ideal voltage V_ring that stands
for the CCO node; the worst case allows V_ring ≤ 2.6 V (VDDA 3.0 V minus 0.4 V for the CCO mirror). Corners: tt 27 °C
3.3 V, ss 110 °C 3.0 V, ff −40 °C 3.6 V. Data: `design/feas/hv_vco.json`, log `hv_vco.log`. (f = 0 in the log means
below ~0.9 GHz, too slow for the 40 ns measurement window — not a failure to oscillate.)

| Candidate | tt, V_ring 2.6 V | **ss 110 °C, V_ring 2.6 V** | ss 110 °C, 3.0 V | ff −40 °C, 2.6 V | ring current at ss limit |
|---|---|---|---|---|---|
| A: 3-stage inverter ring, single-ended | 1.53 GHz | **1.07 GHz** | 1.29 GHz | 2.12 GHz | 0.41 mA |
| B: 3-stage pseudo-differential (step-74 cell style) | 1.59 GHz | **1.10 GHz** | 1.37 GHz | 2.25 GHz | 0.87 mA |
| C3: Maneatis differential, 3 stages | unreliable (swing 0.3–0.4 V, near the edge of oscillation) | — | — | — | — |
| C4: Maneatis differential, 4 stages | 0.85–1.31 GHz at 3–13 mW | 0.87 GHz only at 6.8 mW | — | 1.6 GHz at 15 mW | 2.25 mA |

**Reading.**
- Worst-case ceiling of a full-swing 3-stage ring in 5 V devices ≈ **1.1 GHz**. Safe target = worst case ÷ 1.10
  (f_ref up to 55 MHz) ÷ 1.15 (layout parasitics) ≈ **0.85 GHz**.
- **1.6 GHz is not feasible** across PVT: even the full 3.0 V on the ring gives only 1.37 GHz at ss 110 °C.
- The reduced-swing Maneatis ring did not help: thick-oxide devices have low g_m/C and need large overdrive; it was
  slower and used 2–5× the power. (Quick sizing — but no sign it could reach 1.6 GHz at sane power.)
- A and B have the same speed; B costs about 2× the current but gives true complementary outputs (needed by the
  SSPD and the NCB) and keeps the step-74 cell, its theory and its ISF noise tools.

**Decision proposed: 800 MHz = 50 MHz × 16 with ring B** (3-stage pseudo-differential, 5 V devices, CCO-fed).
Margin at the worst corner: 1.10 GHz vs 0.88 GHz needed (55 MHz × 16) = 25 % for layout. The ring current is set
later by the phase-noise budget (ring jitter ∝ 1/√P, independent of f), not by speed.
