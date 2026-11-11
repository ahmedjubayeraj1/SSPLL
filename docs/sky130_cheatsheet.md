# SKY130 design cheat sheet (sky130A, open_pdks 1.0.608 / 1689ac3f)

Every number below was read from, or simulated with, the pinned PDK on 2026-11-11.
Source of each value is given so it can be re-checked. Benches: `pdk_char/`.

## 1. Transistors

| Device | Use | L min (um) | W min (um) | Vds, Vgs max | Oxide (nm) |
|---|---|---|---|---|---|
| nfet_01v8 / pfet_01v8 | 1.8 V core logic and analog | 0.15 | 0.42 | 1.95 V | 4.15 / 4.23 |
| nfet_01v8_lvt | faster nMOS, lower Vt | 0.15 | 0.42 | 1.95 V | 4.15 |
| **pfet_01v8_lvt** | faster pMOS | **0.35** (not 0.15) | 0.42 | 1.95 V | 4.23 |
| pfet_01v8_hvt | low-leakage pMOS | 0.15 | 0.42 | 1.95 V | 4.23 |
| nfet_g5v0d10v5 / pfet_g5v0d10v5 | 3.3 V and 5 V circuits (CCO mirror, pads) | 0.50 | 0.42 | Vgs 5.5 V, Vds 11 V | 11.6 / 11.75 |
| nfet_03v3_nvt | native 3.3 V nMOS | 0.50 (max 0.9) | 0.42 | 3.3 V | 11.6 |
| nfet_05v0_nvt | native 5 V nMOS | 0.90 | 0.42 | 5.5 V | 11.6 |

Sources: L/W limits = union of the model bins in `libs.tech/combined/continuous/models_fet/*.spice`;
voltage limits = SkyWater device-details page (SPICE validity range); oxide = model `toxe`.
**Design rule for this project: no 1.8 V device may see more than 1.8 V in normal operation (1.95 V absolute).**

## 2. Poly resistors (legal widths are fixed)

Precision poly resistors exist only in five widths: **0.35, 0.69, 1.41, 2.85, 5.73 um** (rules rpm.1b-f).
Minimum length 0.50 um (Magic pcell). Any other width fails DRC.

| Resistor | Width (um) | Body (Ohm/um) | Both heads (Ohm) | L for 10 kOhm (um) | L for 100 kOhm (um) |
|---|---|---|---|---|---|
| res_xhigh_po_0p35 | 0.35 | 5708.6 | 623 | 1.6 | 17.4 |
| res_xhigh_po_0p69 | 0.69 | 2895.7 | 428 | 3.3 | 34.4 |
| res_xhigh_po_1p41 | 1.41 | 1417.0 | 246 | 6.9 | 70.4 |
| res_xhigh_po_2p85 | 2.85 | 701.1 | 139 | 14.1 | 142.4 |
| res_xhigh_po_5p73 | 5.73 | 348.7 | 82 | 28.4 | 286.6 |
| res_high_po_0p35 | 0.35 | 1104.6 | 616 | 8.5 | 90.0 |
| res_high_po_0p69 | 0.69 | 491.5 | 395 | 19.5 | 202.7 |
| res_high_po_1p41 | 1.41 | 230.0 | 257 | 42.4 | 433.6 |
| res_high_po_2p85 | 2.85 | 113.6 | 132 | 86.9 | 879.5 |
| res_high_po_5p73 | 5.73 | 56.5 | 68 | 175.9 | 1770.1 |

R = body x L + heads. Simulated in ngspice (tt, 27 C) at L = 10 and 20 um (`pdk_char/res.sp`).

| Property | res_xhigh_po | res_high_po | Source |
|---|---|---|---|
| Sheet resistance, nominal | 2000 Ohm/sq | 325 Ohm/sq | parameters_res_nom.spice |
| Process corners | 1700 to 2300 Ohm/sq (+/-15%) | 277 to 370 Ohm/sq | parameters_res_low/high |
| Temperature coefficient tc1 | about -2.5e-3 /C | - | models_resistors.spice |
| Mismatch (sigma) | 4.64% / sqrt(W*L) | 2.06% / sqrt(W*L) | models_global.spice |
| Current limit | 100 uA/um of width preferred, 500 uA/um max | same | SkyWater device page |

Other resistive layers (sheet, nominal): generic poly 48.2, n+ diff 120, p+ diff 197, n-well 1700,
p-well 3816, li1 12.3, met1/met2 0.124, met3/met4 0.046, met5 0.0275 Ohm/sq;
via 4.5, via2-via4 3.41 Ohm each.

## 3. Capacitors

| Capacitor | Density | Size limits | Source |
|---|---|---|---|
| cap_mim_m3_1 (met3-met4) | **2.00 fF/um2** + 0.164 fF/um perimeter (model); pcell uses 0.19 | sides **2 to 30 um**, rectangular only, spacing 0.84 um, met3 overlap 0.14 um | pdk_char/cap.sp; Magic pcell; sky130A.tech capm.* |
| cap_mim_m3_2 (met4-met5) | same as m3_1 | same | same |
| nfet_01v8 gate as capacitor | **7.48 fF/um2 at Vg = 0.9 V**, 7.88 at 1.8 V, only 2.2 at 0 V | L, W as transistor | pdk_char/cap.sp |
| nfet_g5v0d10v5 gate as capacitor | 2.87 fF/um2 at 1.65 V, 2.92 at 3.3 V, 1.31 at 0 V | as transistor | pdk_char/cap.sp |

Area for 20 pF: MIM 10,000 um2 (needs several 30x30 um tiles); 1.8 V MOS cap about 2,700 um2,
**but only when biased well above threshold** - at 0 V it is 3.4x smaller.

## 4. Minimum layout dimensions (most used)

| Layer | Min width (um) | Min spacing (um) | Rule |
|---|---|---|---|
| poly | 0.15 | - | poly.1a |
| licon | 0.17 x 0.17 (fixed) | - | licon.1 |
| li1 | 0.17 | 0.17 | li.1, li.3 |
| met1 | 0.14 | 0.14 | m1.1, m1.2 |
| rpm (resistor implant) | 1.27 | 0.84 | rpm.1a, rpm.2 |
| MIM cap | 1.0 (DRC) / 2.0 (pcell) | 0.84 | capm.1, capm.2a |

## 5. What this means for the previous SSPLL design (input to step 6)

- Any resistor whose width is not one of the five values above is illegal. (The old RSM is 5.73 um wide and
  0.65 um long - legal, but so short that 27% of its value is end resistance; see audit/AUDIT.md.)
- `m=` is ignored on res_xhigh_po in ngspice-42 with these models; draw parallel resistors explicitly.
- A resistor shorter than 0.5 um is illegal; a resistor hundreds of um long (RF at 271 um) is legal but should be folded.
- MIM caps above 30 x 30 um must be tiled; large LDO MIMs need re-planning.
- A MOS capacitor must stay biased above about 0.6 V or most of its capacitance disappears.
- The Cadence-compatible SKY130 kit may use slightly different R and C values; step 7 measures the difference.
