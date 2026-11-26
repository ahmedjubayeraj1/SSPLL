# SKY130 sub-sampling PLL with feedforward noise cancellation

Chipalooza Challenge #4 (Chip Foundry Sky130) entry. A ring-oscillator sub-sampling PLL after Nagam and Kinget (IEEE JSSC 2018), with feedforward noise cancellation.

- **Frequency plan:** 50 MHz reference × 16 = 800 MHz, divided into 400, 200, 100 and 50 MHz outputs.
- **Devices:** every analog circuit uses only the 5 V-rated `g5v0d10v5` devices on VDDA 3.3 V (ground VSSA). The digital logic uses the 1.8 V devices on VDDD (ground VSSD).
- **Target:** 1.6 ps rms jitter (10 kHz–40 MHz) at about 10 mW.
- **Status:** block design, steps 72–79 done (pre-layout).

| Folder / file | Content |
|---|---|
| `docs/chipalooza4-constraints.md` | Challenge rules, schedule and what they force on this design |
| `docs/sky130_cheatsheet.md`, `pdk_char/` | Legal device sizes, resistor and capacitor densities, voltage limits from the pinned PDK, and the ngspice benches behind them |
| `versions.txt` | The frozen toolchain (IIC-OSIC-TOOLS 2026.10, open_pdks 1689ac3f) |
| `docs/design/proposal_final_spec.md` | How each proposal value was set from the pre-layout results |
| `docs/design/hv_*.md` | 5 V device characterisation, ring feasibility, output divider |
| `docs/design/budget_hv.md`, `design/budget/` | Step 72: phase-noise, jitter, power and area budget |
| `docs/design/loop_hv.md`, `design/loop/` | Step 73: loop design (f_c, PM, β, R, C) and the exact sampled-loop model |
| `docs/design/vco_hv.md`, `design/vco/`, `xschem/vco_hv/` | Step 74: 3-stage pseudo-differential ring VCO |
| `docs/design/cco_hv.md`, `design/cco/`, `xschem/cco_hv/` | Step 75: 5-bit current DAC and level shifter |
| `docs/design/refbuf_hv.md`, `design/refbuf/`, `xschem/refbuf_hv/` | Step 76: reference receiver |
| `docs/design/clkgen_hv.md`, `design/clkgen/`, `xschem/clkgen_hv/` | Step 77: clock generator (sample, Gm and hold pulses) |
| `docs/design/sspd_hv.md`, `design/sspd/`, `xschem/sspd_hv/` | Step 78: sub-sampling phase detector with hold |
| `docs/design/sscp_hv.md`, `design/sscp/`, `xschem/sscp_hv/` | Step 79: pulsed-Gm charge pump |
| `docs/design/lf_hv.md`, `design/loop/`, `xschem/lf_hv/` | Step 80: loop filter in real devices |
| `docs/design/ground_split.md` | VSSA / VSSD assignment, and the proof that it changed nothing simulated |
| `docs/testbench_guide.md` | Every testbench: what it measures, why, how it is set up and run |
| `tools/xsch.py`, `xschem/lvs.sh`, `xschem/render.sh`, `tools/lvs_hv_all.py` | Schematic builder with drawing checks, schematic-vs-simulation LVS of every cell, PNG rendering |
| `tools/ground_split_check.py`, `tools/pdk_limits.py` | Netlist equivalence and node-count check; PDK size limits |
| `models/` | Phase-domain PLL model (`pllmodel`) and self-test |

## Reproduce

    source tools/env.sh                                   # PDK_ROOT, PDK
    ./tools/collect_versions.sh                           # compare with versions.txt
    for b in cco clkgen refbuf sspd sscp vco; do (cd design/$b && python3 schematics_hv.py); done
    python3 tools/lvs_hv_all.py                           # LVS of every 5 V cell
    python3 design/sscp/sscp_hv_sim.py                   # each step's simulations: design/<block>/<block>_hv_*.py

Each step's note in `docs/design/` lists its scripts, run times and results, and `docs/testbench_guide.md` explains every bench.

Everything here can be rebuilt and verified with open-source tools (Chipalooza Rules 13–14). License: Apache-2.0.
