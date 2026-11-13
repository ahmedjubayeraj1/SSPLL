# SKY130 sub-sampling PLL with feedforward noise cancellation

Chipalooza Challenge #4 (Chip Foundry Sky130) entry. A ring-oscillator sub-sampling PLL after
Nagam and Kinget (IEEE JSSC 2018): 50 MHz reference x 32 = 1.6 GHz, with feedforward noise
cancellation. Target 1.6 ps rms jitter (10 kHz-40 MHz) at about 7.4 mW. Status: proposal stage.

| Folder / file | Content |
|---|---|
| `proposal/` | submitted proposal (PDF), frozen architecture (`DECISION.md`), jitter and power budgets, feasibility simulations |
| `docs/chipalooza4-constraints.md` | challenge rules, schedule and what they force on this design |
| `docs/sky130_cheatsheet.md` | legal device sizes, resistor and capacitor densities, voltage limits, from the pinned PDK |
| `versions.txt` | the frozen toolchain (IIC-OSIC-TOOLS 2026.10, open_pdks 1689ac3f) |
| `tools/` | `env.sh`, `collect_versions.sh`, `netlist_all.sh`, `check_netlists.py` |
| `pdk_char/` | ngspice benches that produced the cheat-sheet numbers |
| `audit/` | step 6: audit of the previous schematics |
| `correlation/` | step 7: ngspice vs Cadence/Spectre device correlation (`STEP7.md`) |
| `tools/cadence/` | frozen models for Spectre, correlation benches (`pvt/` over corners), phase-noise checks |
| `xschem/` | schematics and testbenches (baseline import in step 4) |

## Reproduce
    source tools/env.sh                 # PDK_ROOT, PDK
    ./tools/collect_versions.sh         # compare with versions.txt
    ./tools/netlist_all.sh              # netlist every schematic
    python3 tools/check_netlists.py     # connectivity checks
    python3 proposal/final_budget.py    # jitter and power budget behind the spec

Everything here can be rebuilt and verified with open-source tools (Chipalooza Rules 13-14).
License: Apache-2.0.
