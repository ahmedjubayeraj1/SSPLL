# Phase 0, step 7 - Cadence vs ngspice device correlation (closure report)

Status 13 Nov 2026: **closed on the open-source side; two runs left in the Cadence VM** (section 5).

## 1. What step 7 is, and why it exists

The same schematic gave different R and C values in Virtuoso (Cadence kit `sky130_release_0.0.4`) and in
xschem/ngspice (open_pdks). That was one of the reasons the previous SSPLL could not be verified in Cadence.
A PLL is a chain of gains (K_VCO, CP gain, R1, C1, C2); if one tool's resistor is 15% off, the loop
bandwidth, phase margin and jitter all move, and no number can be trusted until we know which tool is right
and by how much they differ.

Step 7 answers three questions:

1. **Which is the reference?** ngspice + open_pdks 1689ac3f. Chipalooza Rules 13-14 require open-source
   verifiability, so Cadence is a cross-check that must agree with ngspice, not the other way round.
2. **Can Spectre simulate exactly the same model data?** Yes: `tools/cadence/make_spectre_models.py` converts
   the frozen open_pdks models to Spectre syntax (no value changed), and `sspll_kit_wrap.spice` maps the kit's cell
   names and SI units onto them. Virtuoso is still used to draw schematics and layouts with the kit's symbols.
3. **How far off are the kit's own models?** Measured on the loop-filter cell: +41% current in the resistor branch.
   The full device-by-device table over corners is the kit-mode run in section 5.

How each value is measured (identical in both tools, so the comparison is fair):
- Resistor: 1 V DC across it, R = V / I.
- MIM capacitor: 1 V AC at 1 MHz, C = |I| / (2 pi f V).
- MOS: drain current at a fixed bias (nfet 4/0.15 at Vgs = Vds = 0.9 V; pfet 8/0.15 at Vsg = Vsd = 0.9 V).

Never compare the values printed on instances (CDF labels in Virtuoso, `value` text in xschem): those are
zero-bias formulas, not simulations (`tools/cadence/README.md`, LF example: 7.771 k vs 9.707 k labels, 8.387 k simulated).

## 2. Results so far

| Check | Date | Result |
|---|---|---|
| Spectre (MMSIM 15.1) on converted frozen models vs ngspice, tt 27 C: 6 resistors, 3 MIM, 3 MOS incl. `m=` | 12 Nov | **PASS**, all 0.00% except high_po +0.27% (not used in the design) |
| ADE (IC617) loop-filter testbench with frozen models vs ngspice, 1 MHz | 12 Nov | **PASS**, 96.1368 uA both; kit's own models give 135.64 uA (+41%) |
| Single-device drain noise, Spectre vs ngspice (nfet, pfet at 1 MHz and 1 GHz) | 12 Nov | **PASS**, 0.0 dB |
| Ring VCO frequency, Spectre PSS vs ngspice | 12 Nov | **PASS**, 1.6021 vs 1.6022 GHz (0.006%) |
| Ring phase noise, Spectre pnoise vs ngspice ISF | 12 Nov | Resolved with transient noise: pnoise 3.0 dB optimistic (sideband convention), ISF 6.4 dB pessimistic. Best estimate L(1 MHz) ~ -99 dBc/Hz (`tools/cadence/pnoise/RESULT.md`) |
| Expected values for 9 model sections x 3 temperatures (27 points, 12 values each), ngspice-42 on converted models | 13 Nov | Done: `tools/cadence/pvt/expected_pvt.csv`. tt 27 C row reproduces the 12 Nov Spectre numbers exactly |
| Spectre over the same 27 points, frozen and kit models | - | **To run in the VM** (section 5) |

## 3. New finding: process corners do not move R and C

In `sky130.lib.spice` the sections `tt, ss, ff, sf, fs` change **only the MOS devices**; all five load
`r+c/res_typical__cap_typical.spice`. Resistor and capacitor spread lives in separate sections:
`ll` (low R, low C), `hh`, `hl` (high R, low C), `lh`, and combined ones such as `ss_hh`, `ff_ll`, `sf_hl`.

Spread relative to tt 27 C (`expected_pvt.csv`; R computed from current, + means larger):

| Section, T | R xhigh 0.35 x 20 | R xhigh 5.73 x 0.65 | R high_po 0.35 x 20 | C MIM 20 x 20 |
|---|---|---|---|---|
| tt/ss/ff/sf/fs, 27 C | 0 | 0 | 0 | 0 |
| any MOS corner, -40 C | +11.0% | +8.3% | -2.6% | 0 |
| any MOS corner, 110 C | -10.3% | -7.7% | +4.7% | 0 |
| ll, 27 C | -7.8% | -12.4% | -15.5% | -12.1% |
| hh, 27 C | +7.8% | +12.4% | +15.5% | +12.4% |
| hh, -40 C | +19.7% | +20.7% | +12.6% | +12.4% |
| ll, 110 C | -17.3% | -20.1% | -11.3% | -12.1% |

Why it matters for this PLL:
- Loop filter: R1 C1 (the loop-filter zero) moves from -27% (ll, 110 C) to +35% (hh, -40 C),
  so phase margin and bandwidth must be checked at `ss_hh`/`ff_ll`-type sections, not only at ss/ff.
- Pulsed-Gm charge pump: Gm is set by degeneration resistors, so CP gain follows R (+/-20% over R corner x temperature).
- RC pulse generator (clkgen): pulse width ~ RC moves with both.
- MIM capacitors have no temperature coefficient in these models; xhigh poly R has about -0.13%/C.

**Rule for every later PVT run:** the corner list is MOS corner x R/C corner x temperature, e.g.
`tt, ss_hh, ss_ll, ff_hh, ff_ll, sf_hl, fs_lh` (plus others where a block depends on R/C ratio) at -40/27/110 C.
A sweep over only tt/ss/ff/sf/fs silently assumes perfect resistors and capacitors.

(Side note: the pfet test bias Vsg = 0.9 V is close to its threshold, so its current moves -79%...+330% over
corners and temperature. That is expected for a near-threshold test point and is only used to compare tools.)

## 4. What the files do

| File | Purpose |
|---|---|
| `tools/cadence/make_spectre_models.py` | frozen open_pdks models -> Spectre-readable copy + kit-name wrapper |
| `tools/cadence/corr_kit.scs` | the single-point (tt 27 C) Spectre bench of 12 Nov |
| `tools/cadence/pvt/ngspice_expected.py` | ngspice twin of the bench over 9 sections x 3 temperatures -> `expected_pvt.csv` |
| `tools/cadence/pvt/corr_pvt.scs.tmpl` | the Spectre bench, with the model include and temperature filled per point |
| `tools/cadence/pvt/run_corr_pvt.sh` | runs all 27 points in Spectre (`frozen` or `kit` mode) and compares |
| `tools/cadence/pvt/compare_pvt.py` | reads the psfascii results, prints the table, PASS/FAIL (frozen) or the difference (kit) |

## 5. What you run in the Cadence VM (about 5 minutes)

Copy `tools/cadence/pvt/` into the VM next to your `~/sky130A_frozen_spectre`, then in a terminal where `spectre` runs:

```sh
cd pvt
bash run_corr_pvt.sh frozen ~/sky130A_frozen_spectre
#   must end with: PASS - worst |diff| ... (limit 0.5%) over 324 values
bash run_corr_pvt.sh kit /path/to/sky130_release_0.0.4/models/sky130.lib.spice
#   measures the kit's own models against the reference; no pass/fail
```

- If the kit names its sections differently (for example `tt_mm`), give a map as the third argument:
  `bash run_corr_pvt.sh kit KIT_LIB "tt=tt_mm ss=ss_mm ..."`. Sections the kit does not have are listed as missing.
- If the frozen run fails only at the `ll/hh/hl/lh` sections, the converted R/C corner files are not being read -
  send `out_frozen/hh_27/spectre.log`.
- If the VM has no python3, the script packs `corr_pvt_<mode>.tar.gz` on the Desktop; send it and I compare it.
- Send `result_frozen.md` and `result_kit.md` (copied to the Desktop). The kit table becomes the documented
  "Cadence kit vs open PDK" difference in the final report.

Then fill the `[cadence]` section of `versions.txt` (`tools/collect_versions.sh` prints most of it).

## 6. Acceptance and closure

| Item | Criterion | Status |
|---|---|---|
| Reference defined | ngspice + open_pdks 1689ac3f, frozen in `versions.txt` | done |
| Same models in Spectre | converted, every value within 0.5% at tt 27 C | done (12 Nov) |
| Same models over PVT | within 0.5% at 27 points | VM run pending |
| ADE uses the frozen models | LF cell 96.1368 uA in ADE = ngspice | done (12 Nov); keep the `frozen_tt` ADE state |
| Kit difference documented | per-device table over corners | VM run pending (+41% LF branch already measured) |
| Noise and oscillator | device noise 0.0 dB; ring f0 0.006%; pnoise vs ISF explained | done (12 Nov) |
| Tool versions recorded | `[cadence]` in `versions.txt` | partly (from the 12 Nov runs); confirm in the VM |

Step 7 is closed when the two VM runs are in. Nothing in later steps waits for them: every design number
comes from ngspice, and Spectre is now known to give the same answer at tt.

## 7. Carried forward (not part of step 7)

- **Monte Carlo runs only in ngspice.** The converter removes the AGAUSS mismatch terms (MMSIM 15.1 rejects them);
  corner results are unaffected.
- **Large DC voltage across short poly resistors.** The converted resistor model is evaluated at 0 V across the
  resistor: up to -1.4% at 1 V for xhigh 5.73 x 0.65. For DC operating points of the CCO degeneration use ngspice.
- **ISF phase-noise model is 6.4 dB pessimistic** against transient noise (`vco_study/isf2.py`): fix before
  sizing the redesigned VCO (VCO step).
- **PVT matrix must include R/C sections** (section 3) in every block bench and in CACE datasheets.
