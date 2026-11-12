# Frozen sky130A models in Cadence Virtuoso / Spectre

Goal: Spectre simulates **exactly the same model data** as xschem/ngspice (open_pdks 1689ac3f), so a number
never depends on which tool produced it. Keep the Virtuoso kit (sky130_release_0.0.4) for schematic entry and
layout drawing; replace only its **models**.

## What differed in the LF cell (12 Nov 2026)

| Device | xschem shows | Virtuoso shows | Simulated (ngspice, frozen PDK) | Why the labels differ |
|---|---|---|---|---|
| R1 xhigh 0.35 x 1.36 um | 7.771 k | 9.70657 k | 8.387 kOhm at 1 V (8.358 k at 0.05 V) | Both are label formulas, not simulations. xschem: 2000 Ohm/sq x 1.36/0.35 (body only, no contact heads). Virtuoso: the kit's own CDF formula, passed as `r=` |
| C2 MIM 20 x 20, x2 | 1.63 p | 813.182 f, m=2 | 1626.4 fF total | **No difference**: xschem prints the total, Virtuoso the value of one instance. 2 x 813.18 = 1626.4 |

Lesson: compare **simulated** currents, never instance labels.

## Why not convert the whole kit
A Virtuoso kit has models, symbols/CDF, pcells, a tech file and DRC/LVS decks. Only the **models** decide
simulated numbers, and only they can be checked automatically against ngspice. Sign-off DRC/LVS for the
challenge is Magic + Netgen (Rules 13-14), so the kit's pcells and decks only need to draw the same layers -
Magic DRC and Netgen LVS on the final GDS are the authority. Converting pcells and decks cannot be validated
here and would add risk without changing any result.

## Steps (on your PC)

1. Make sure your open-source PDK is the frozen one: `cat $PDK_ROOT/sky130A/.config/nodeinfo.json` must show
   commit `1689ac3f2dc763876eaf967227c7dfe831b031ae` (run `tools/collect_versions.sh`).
2. Build the Spectre-ready copy (syntax and naming only - verified identical in ngspice):
   ```sh
   python3 tools/cadence/make_spectre_models.py $PDK_ROOT $HOME/sky130A_frozen_spectre
   ```
3. Run the bench from a terminal: edit `OUT` in `tools/cadence/corr_kit.scs`, then `spectre corr_kit.scs`.
   Compare every current with the `expect` comment (target within 0.5%; the models are the same, so only
   numerical differences remain).
4. If it passes, in ADE > Setup > Model Libraries **remove** the kit's `.../models/sky130.lib.spice` and add:
   - `$HOME/sky130A_frozen_spectre/sky130A/libs.tech/ngspice/sky130.lib.spice`, section `tt` (or ss, ff, sf, fs)
   - `$HOME/sky130A_frozen_spectre/sspll_kit_wrap.spice`, no section
5. Re-run your LF cell: Spectre must now give 8.359 kOhm (0 V model; ngspice full model 8.387 kOhm at 1 V) and 1626.4 fF.

## Changes needed for MMSIM 15.1 (Spectre 15.1, 2015) - all made by the generator

| Change | Why | Effect on results (ngspice, original vs converted) |
|---|---|---|
| .param defaults moved onto the .subckt line (246 subcircuits) | Spectre treats body .param as constants | none (identical) |
| Monte Carlo terms `MC_*_SWITCH*AGAUSS(..)` removed (23,170) | AGAUSS rejected in model cards | none in tt/ss/ff/sf/fs (the switches are 0); Monte Carlo only in ngspice |
| `{expr}` written as `'expr'` | braces rejected on header lines | none |
| Voltage-dependent poly resistors evaluated at 0 V across the resistor | `r = {.. v(a,b) ..}` not accepted | within 0.07% for small signals; at 1 V across: xhigh 0.35x1.36 -0.33%, xhigh 5.73x0.65 -1.43%, high 0.35x20 +0.99% |

MIM caps and all MOS devices: identical at tt, ss, ff, sf, fs. For DC bias points with large voltages across
short resistors (CCO degeneration, Rsm) use the ngspice value; for AC, noise and the loop filter Spectre is equivalent.

## If step 3 fails

| Symptom | Cause | Fix |
|---|---|---|
| MOS currents wrong by ~1e6 or "out of bin range" | Spectre ignores the models' `.option scale=1u` | In `sspll_kit_wrap.spice` set `.param mos_u=1` |
| R6 = R3 current, or C3 = C2, or N7 = N1 | `m` not applied through the wrapper | Send me the log; the fix is a per-device `m` pass-through |
| Parse errors (`pwr`, `agauss`, `v(r1,r2)` in a resistor) | ngspice-specific syntax Spectre's SPICE reader rejects | Send me the first error lines; the generator gets a rule for it |
| Everything off by a few % | wrong section, or `temp`/`tnom` not 27 | Section `tt`, `temp=27 tnom=27` |

Notes: ngspice cannot test `m` through two subcircuit levels (it only warns), which is why the bench checks
`m` in Spectre. Never edit the generated files by hand; change the generator and rebuild.

## Correlation result - 12 Nov 2026, Spectre MMSIM 15.1 (IC617 VM), models v4, tt 27 C

| Source | Device | Spectre | ngspice (converted) | Diff |
|---|---|---|---|---|
| V1 | xhigh 0.35 x 20 um | 8.7052 uA | 8.7052 uA | 0.00% |
| V2 | xhigh 0.35 x 1.36 um | 119.628 uA | 119.628 uA | 0.00% |
| V3 | xhigh 5.73 x 5.41 um | 508.81 uA | 508.81 uA | 0.00% |
| V4 | xhigh 5.73 x 0.65 um | 3.2903 mA | 3.2903 mA | 0.00% |
| V5 | high 0.35 x 20 um | 43.720 uA | 43.604 uA | +0.27% |
| V6 | xhigh 5.73 x 5.41, m=8 | 4.0705 mA | 4.0705 mA | 0.00% |
| VDN | nfet 4/0.15 | 188.524 uA | 188.524 uA | 0.00% |
| VDN7 | nfet 4/0.15, m=7 | 1.31967 mA | 1.31967 mA | 0.00% |
| VDP | pfet 8/0.15 | 74.863 uA | 74.863 uA | 0.00% |
| VC1 | MIM 5x5 | 53.28 fF | 53.28 fF | 0.00% |
| VC2 | MIM 20x20 | 813.18 fF | 813.18 fF | 0.00% |
| VC3 | MIM 20x20, m=2 | 1626.4 fF | 1626.4 fF | 0.00% |

PASS. `mos_u = 1e6` is correct for MMSIM 15.1; `m=` passes through the wrapper. Open item: high_po +0.27% (not used in
the design). Bench fix: MMSIM 15.1 rejects an AC sweep with start = stop, so `corr_kit.scs` uses `ac freq=1M`.
