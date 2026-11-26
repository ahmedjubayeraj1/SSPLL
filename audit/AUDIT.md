# Step 6 - audit of the previous schematics (11 Nov 2026)

Source: the 28 block schematics of the previous design (project copy of `sspll/xschem/*.sch`, open_pdks 4d5af10b,
5-stage ring at 2.36 GHz, N = 48). Checked against `docs/sky130_cheatsheet.md` and the proposal architecture
(5-stage x1.5 ring, 1.6 GHz, N = 32, FFNC, output dividers, 3.3 V REF_IN). Values re-simulated with the pinned
PDK (open_pdks 1689ac3f, ngspice-42) in `audit/rcheck.sp` and `correlation/corr_rc.sp`.

Severity: **M** = must fix before layout (illegal, wrong, or missing for the proposal),
**S** = should fix (layout friendliness, robustness), **N** = note.

## 1. Findings by block

| # | Block | Finding | Sev | Action |
|---|---|---|---|---|
| 1 | ldo | MIM caps 80x80 (XCM), 50x50 x4 (XCF), 50x50 x2 (XCFF) exceed the 30 um maximum side - illegal | M | Block is not used for the ring (CCO replaced it). Move to `archive/`, do not lay out. A **new, small** LDO is still required for the SSPD/CP/buffer/NCB rail (step 8, docs/architecture_decision.md) |
| 2 | cco | Rsm = res_xhigh_po_5p73, L = 0.65 um is legal but only 0.11 squares: 27% of its 308 Ohm is end (contact) resistance. Rsr : Rsm = 1968 : 308 = 6.4, not the 8 the 1:8 mirror needs; ends do not match like bodies | M | Rsm = 8 copies of the Rsr unit (L = 5.41) in parallel, drawn as 8 instances, common-centroid with Rsr |
| 3 | cco | Rf = 0.35 x 271 um (1.55 MOhm with the pinned PDK; the old README says 2 MOhm) | S | Draw as 8 series segments of ~34 um so schematic = layout; re-check the filter corner |
| 4 | cco | XCF is a 1.8 V pfet MOS cap whose n-well, source and drain sit on vdda = 3.3 V; gate = mirror gate (vdda - 1.0..1.3 V) | S | Verify gate-oxide voltage over power-up/down and that Magic DRC accepts a thin-oxide device in a 3.3 V well; fallback pfet_g5v0d10v5 cap (2.6x area) |
| 5 | cco | Mirror devices XPD (8x) and XPM (64x) are single 40 um fingers (nf = 1) | S | nf = 8 (5 um fingers), 8:64 as a common-centroid array with dummies |
| 6 | cco | DAC range 1.02-1.6 mA was set for 2.36 GHz with the 1x ring | M | Re-centre for the x1.5 ring at 1.44-1.76 GHz (tt 1.31 mA, ss/110 C up to 1.66 mA, ff/-40 C low end) |
| 7 | lf | C1 = nfet_01v8 MOS cap 20x20 x7 (~21 pF) on vctrl: capacitance drops 3.4x below ~0.6 V | S | Check the vctrl range in the lock bench over PVT; if it goes below 0.6 V use MIM stacked above the MOS cap |
| 8 | lf | R1, C1, C2 were sized for N = 48, 2.36 GHz and the old K_VCO | M | Recompute for 1.6 GHz, N = 32, x1.5 ring |
| 9 | sscp | Degeneration resistors (xhigh, 22 / 13.6 / 32.5 um) set Gm: +/-15% process, -10% at 110 C, +11% at -40 C | N | Include the CP-gain spread in the loop PVT analysis |
| 10 | clkgen | RC pulser: R = 50.6 kOhm xhigh, C = 31 fF MIM 3.8x3.8; pulse width ~0.7 RC moves with R (+/-15%, temperature) | S | Option: time the Gm pulse from the divided VCO clock (width = k x T_VCO, PVT-independent once locked) |
| 11 | refin | 1.8 V AC-coupled inverter. The proposal's REF_IN is self-biased at VDDA/2 on the 3.3 V pad with overvoltage protection (Rule 10) | M | New 3.3 V input stage (thick oxide) + level shift to 1.8 V |
| 12 | div48 | /2 /2 /2 /3 /2 = 48 | M | N = 32: /2 x5 (TSPC first stages, static logic after); FLL /32 |
| 13 | top | No FFNC path (delay line, gain DAC), no output dividers /2-/16, no CLK_OUT /16/32/64 mux and pad driver, no VTEST mux, no control mapping to the Rule 7.4 digital pins | M | New blocks |
| 14 | vco, dcell | 1x cell, nf = 1 with 8 um pMOS fingers | M/S | Scale to 1.5x; fold 8x1.5 = 12 um pMOS into nf = 3 (shared diffusion lowers node capacitance, helps the 23% speed margin) |
| 15 | sspd | MIM 5x5 sampling caps, perimeter is ~7% of C; dummies present (good) | N | Sampling node on the top plate (capm), identical surroundings for p/m |
| 16 | acbuf | MIM 4x4 coupling cap on every ring node | N | Top plate on the ring node to keep bottom-plate parasitic off it |
| 17 | logic | Custom nand2, nor2, inv_1..16, dffr, pfd | S | Use sky130_fd_sc_hd standard cells (ready layout, LVS-clean); keep only the TSPC /2 and ring-speed paths custom |

## 2. Rules that apply to every block

- **Resistor multiplier.** With these models `m=` is ignored on `res_xhigh_po_*` in ngspice-42 (tested: m = 8 gives the
  single-resistor value), while it works on `res_high_po_*` and MOS. `mult` only enters the mismatch formula.
  Never use mult/m on xhigh resistors - draw parallel copies. Re-test on ngspice-47 with `correlation/mtest3.sp`.
- **MIM multiplier.** `MF` alone does not multiply in ngspice (MF = 2 gives 813 fF for 20x20, MF = 2 with m = 2 gives 1626 fF).
  The xschem symbol writes both (`MF=@MF m=@MF`), so xschem is right; other netlisters may not be.
- **Model drift.** The old README (ngspice, open_pdks 4d5af10b) gives Rsm = 261 Ohm; the pinned PDK gives 308 Ohm for
  the same drawing. Every old sizing must be re-simulated with the pinned PDK; no number is carried over.
- **Fingers and units.** nf = 1 everywhere today. Use one unit device per matched group, fingers of 2-5 um, dummies,
  common-centroid for mirrors and the CP.
- **Layout effects.** Schematics use sa = sb = sd = 0 (no stress effects); post-layout extraction will shift currents.
- **Wiring.** The VCO study budgets 10 fF per ring node; keep ring wires short and symmetric, crossover included.

## 3. Correction to the cheat sheet
`docs/sky130_cheatsheet.md` section 5 said the RSM resistor was 0.65 um wide. It is 5.73 um wide and 0.65 um long
(legal); the problem is the short length (finding 2), not the width. Fixed in the same commit.
