# xschem/ngspice vs Cadence Virtuoso/Spectre - device correlation

Why the same "PDK component" gives different values in the two tools, how to find which cause applies,
and the reference numbers the Cadence kit must reproduce before any Cadence phase-noise result is trusted.

**Reference (sign-off) = open_pdks 1689ac3f + ngspice.** Rules 13-14 require open-source verifiability, so Cadence
is the cross-check, correlated to this reference - not the other way round.

## 1. Why the values differ

| # | Cause | What happens | How to see it |
|---|---|---|---|
| 1 | Different model data | The Cadence kit's Spectre models are a separate conversion of SkyWater data, of some version. Even two open_pdks versions differ: the old design's README (ngspice, open_pdks 4d5af10b) has Rsm = 261 Ohm, the pinned PDK gives 308 Ohm for the same drawing | Compare the R, C, MOS tables below |
| 2 | Wrong or missing R/C corner section | In open_pdks `.lib sky130.lib.spice tt` loads MOS tt **and** `r+c/res_typical__cap_typical.spice`; MIM area/perimeter constants (camimc 2.0 fF/um2, cpmimc 0.19 fF/um, m3_dw -0.025 um, tol_m3) and resistor parameters live there. Kits often have separate MOS and R/C sections; a missing or different R/C section moves R by up to +/-15% | ADE: Setup > Model Libraries - list every file and section |
| 3 | Multiplier semantics | In these models `mult` (resistor) and `mf` (MIM) only enter the mismatch formula; the copies are made by the instance `m`. Tested in ngspice: MIM 20x20 with MF = 2 alone = 813 fF, with m = 2 = 1626 fF; `m=` on res_xhigh_po is ignored in ngspice-42 | Read the netlist ADE writes: which of m / mf / mult it passes |
| 4 | Meaning of W and L | open_pdks MIM W/L = top plate (capm), minus 0.025 um. A Virtuoso pcell may take the met3 bottom plate (0.14 um larger each side) or snap to grid: 20x20 then gives ~791 fF instead of 813, 5x5 ~48 instead of 53 fF. xschem xhigh resistors have W fixed by the device name and L = body length between the heads; a generic Cadence poly resistor may treat W and L differently | Compare the W/L in the ADE netlist with the drawn values |
| 5 | Bias and temperature | The resistor model is voltage- and temperature-dependent: xhigh 5.73 x 0.65 um = 303.9 Ohm at 0.05 V and 308.3 Ohm at 1 V; xhigh R is -10% at 110 C and +11% at -40 C. The R shown on the Virtuoso instance (CDF) is a zero-bias formula, not a simulation | Compare simulated with simulated, same V and T |
| 6 | Editing the kit | m3_1 (met3-met4) and m3_2 (met4-met5) are separate subcircuits; commenting out m3_2 cannot change m3_1 | Revert the edit; never modify PDK files (reproducibility) |

## 2. Reference values (ngspice-42, open_pdks 1689ac3f, tt, 27 C)

Resistors (R = V/I, substrate terminal at 0 V), `corr_rc.sp`:

| Device | L (um) | R at 0.05 V | R at 1.0 V | R at 1.0 V, 110 C | R at 1.0 V, -40 C |
|---|---|---|---|---|---|
| res_xhigh_po_0p35 | 20 | 114.87 kOhm | 114.79 kOhm | 102.99 kOhm | 127.42 kOhm |
| res_xhigh_po_0p35 | 1.36 | 8.358 kOhm | 8.387 kOhm | - | - |
| res_xhigh_po_5p73 | 5.41 | 1965.2 Ohm | 1968.1 Ohm | 1773.1 Ohm | 2176.8 Ohm |
| res_xhigh_po_5p73 | 0.65 | 303.9 Ohm | 308.3 Ohm | - | - |
| res_high_po_0p35 | 20 | 22.92 kOhm | 22.71 kOhm | - | - |

MIM cap_mim_m3_1 at 1 MHz: 5x5 um = 53.28 fF, 20x20 um = 813.2 fF.

MOS (`corr_mos.sp`, nf = 1, ad/as = 0.29 W):

| Device | Bias | Id | gm | gds | Cgg | Drain noise at 1 MHz / 1 GHz |
|---|---|---|---|---|---|---|
| nfet_01v8 W=4 L=0.15 | Vgs = Vds = 0.9 V | 188.5 uA | 1.417 mS | 82.0 uS | 3.13 fF | 66.8 / 6.80 pA/rtHz |
| pfet_01v8 W=8 L=0.15 | Vsg = Vsd = 0.9 V | 74.9 uA | 0.596 mS | 75.6 uS | 7.47 fF | 5.41 / 3.53 pA/rtHz |

Note the nMOS 1/f noise: its corner is tens to hundreds of MHz in these models; the pMOS corner is ~1-2 MHz.

Ring (integrated check), `ring5_x1p5_ref.sp`: 5-stage pseudo-differential, cell x1.5, ideal 1.08 mA feed,
5 fF per node, vtune 0.9 V -> **f0 = 1.602 GHz**. Phase noise at 1 MHz offset (ISF, `vco_study/isf2.py`):
thermal -97.5, flicker -97.1, **total -94.2 dBc/Hz**, 1/f^3 corner ~1.1 MHz (thermal-only with gamma = 1: -98.1).

## 3. Procedure in Virtuoso

1. Revert any edit to the kit. Write down the kit name, version and model file paths in `versions.txt` ([cadence]).
2. Build three test cells with the kit's devices at the same drawn sizes: resistors (DC source 0.05 V and 1 V, measure
   current), MIM caps (AC 1 V at 1 MHz, C = Im(I)/(2 pi f)), the two MOS biases above (DC op + noise analysis
   with the drain current as output).
3. Run at tt, 27 C, then 110 C and -40 C for the resistors. Fill the same tables.
4. Acceptance: R and C within 2%, Id and gm within 3%, noise within 1 dB, ring frequency within 3%.
5. If a row fails, open the netlist ADE wrote (Simulation > Netlist > Display) and check, in this order:
   model sections (cause 2), multiplier parameters (3), W/L values (4), temperature (5).
6. If the model data themselves differ (cause 1), do not "fix" by scaling. Keep ngspice as the reference and record
   the Cadence offsets in a correlation table; or load the open_pdks SPICE models into Spectre
   (`simulator lang=spice` include of `sky130.lib.spice` section tt) and re-run these benches to see whether Spectre
   accepts them - the ngspice-specific syntax in the files may need small edits.

Over corners and temperature: `tools/cadence/pvt/run_corr_pvt.sh` runs this same bench at 9 model sections x 3
temperatures and compares automatically (frozen mode: PASS/FAIL; kit mode: measures the kit's own models).
Status and the R/C-corner finding: `STEP7.md`.

## 4. Phase-noise cross-check in Spectre (after step 3 passes)

Ring alone, same bench as `ring5_x1p5_ref.sp` (ideal current feed, 5 fF per node, tt, 27 C):
- PSS: oscillator mode, fundamental ~1.6 GHz, oscillator nodes vop / vom, about 10 harmonics, stabilisation 20-30 ns.
- Pnoise: relative sweep around harmonic 1, 10 kHz to 100 MHz, output vop - vom, noise type time-average,
  then plot phase noise.
- Compare L(1 MHz) with -94.2 dBc/Hz (total) and use the noise summary at 1 MHz to split flicker and thermal
  (-97.1 / -97.5 here). A difference of a few dB is expected from the method (ISF with a bias-table noise model vs
  Spectre's linear periodic noise); a difference above ~3 dB points to a model mismatch - go back to section 3.
- Loop level: keep the block-level approach (VCO, SSPD + CP, reference, delay line) and combine in the phase-domain
  model (`proposal/jitter_budget.py`); a closed-loop PSS/pnoise of the full PLL is optional.
