"""Interview questions for roadmap step 73 (loop parameters). Shared by the notebook and docs/design/step73_loop.md."""
QA73 = [
("Why is the loop bandwidth chosen from the out2 (FFNC-on) jitter model and not from out1?",
 "out2 is the output the specification is written for (1.4 ps typ). But out2 is almost flat in f_c (1.34–1.36 ps from 1.5 to "
 "5 MHz) because FFNC cancels the VCO noise the loop would otherwise have to suppress. So out2 says 'anything in 1.5–5 MHz "
 "works', and the *other* specs pick the point inside that range."),
("Then what actually pins f_c = 2.5 MHz?",
 "Two specs pull in opposite directions. The FFNC-off phase noise at 300 kHz (−110 typ) needs f_c ≥ 2.5 MHz, because a wider "
 "loop suppresses more ring noise. The FFNC jitter reduction (35 % typ, 20 % min) needs f_c ≤ 2.5 MHz, because a wider loop "
 "leaves less VCO noise for FFNC to remove. 2.5 MHz is the only point that meets both typ values."),
("Why does a wider loop reduce the benefit of FFNC?",
 "FFNC removes VCO noise between f_c and about f_REF/8. If the loop already suppresses the VCO up to a higher f_c, the band "
 "where FFNC helps shrinks: at 4 MHz the reduction is 18 % (below the 20 % minimum), at 5 MHz only 9 %."),
("Why 50° of phase margin and not 60°?",
 "In the jitter model a higher PM lowers peaking and jitter slightly (1.36 → 1.30 ps at 60°), but the zero moves lower (the "
 "zero–pole spread b grows), which weakens low-frequency VCO suppression: L(300 kHz) FFNC-off goes from −110.2 to −108. 50° "
 "is the highest PM that still meets −110, and it keeps the overshoot (27 %) and peaking (2.5 dB) moderate."),
("What is the 'sampled-data' loop and why is it needed here?",
 "The SSPD looks at the phase only once per reference period and the pulsed Gm delivers one charge packet per period, a delay "
 "t_p after the sampling edge. A continuous-time model ignores both. The exact model propagates the filter + VCO state over one "
 "period with the matrix exponential, x[k+1] = e^{AT}x[k] + e^{A(T−t_p)}B·q[k], and evaluates L(e^{jωT}). It shows the "
 "continuous design would land at 48.7° (t_p = 0.5 ns) or 40.6° (t_p = 11 ns) instead of 50°."),
("How large is the phase lag of the packet delay, and how do you compensate it?",
 "A delay t_p adds 360°·f_c·t_p of lag at crossover: 2.3° at 2.5 ns, 9.9° at 11 ns. It is compensated by designing the "
 "filter for a larger lead (52.7° instead of 50° at t_p = 2.5 ns), i.e. a wider zero–pole spread, then iterating on the "
 "exact sampled model until f_c and PM land exactly."),
("Why does t_p become a requirement on the clock generator?",
 "With the filter fixed, PM falls from 51.3° (t_p = 0.5 ns) to 48.3° (5 ns) and 43.4° (11 ns). Firing the Gm pulse right after "
 "the hold transfer instead of half a period later is free in power and area, so step 77 must deliver t_p ≤ 5 ns (2.5 ns "
 "nominal)."),
("Write β for the pulsed-Gm charge pump and explain each term.",
 "β = 2A·g_m·d (A per rad of VCO phase). 2A is the differential SSPD slope (V/rad) for a sampled amplitude A, g_m converts the "
 "held voltage into current, and d = τ/T is the fraction of the period the Gm conducts. The average current into the filter "
 "is β·θ_e. Here A = 0.5 V, d = 0.01 (200 ps / 20 ns), g_m = 84.8 µS → β = 0.848 µA/rad."),
("Why can K_VCO still be unknown when the filter is frozen?",
 "The loop depends only on the product β·K_VCO (C_tot = b·β·K_VCO/ω_c², R = b/(ω_c C1)). If step 74 lands a different "
 "K_VCO, g_m is rescaled (g_m ∝ 1/K_VCO) and the filter is unchanged. The large-area parts (C1, C2) are frozen now; the "
 "small-area part (Gm unit size) absorbs the uncertainty. That is a layout-driven decision."),
("How were C1 and β picked together?",
 "C1 was snapped to whole layout tiles first (2 tiles of 8.56 pF), then β was scaled by the same factor (×0.848) so β·K_VCO/C "
 "stays the same, and R (×1/0.848) and C2 (×0.848) followed. The loop is identical; the layout gets an integer number of "
 "identical tiles."),
("What is in one C1 tile and why?",
 "9 nfet_01v8 MOS-capacitor units (W = L = 10 µm, 3×3) with one 30×30 µm cap_mim_m3_1 above them: 6.73 pF + 1.82 pF = "
 "8.56 pF at V_cont = 0.9 V in about 34×34 µm. The MOS cap gives density (7.5 fF/µm²), the MIM on top is free extra "
 "capacitance in the same footprint and shields the gate from routing above."),
("What is the catch with a MOS capacitor in the loop filter?",
 "Its capacitance depends on the gate voltage: 7.48 fF/µm² at 0.9 V, 6.5 at 0.6 V, only 2.2 at 0 V (measured C-V, tt). If "
 "V_cont drops below ~0.6 V, C1 collapses, the zero moves up and the PM drops. So the VCO fine-tune range must be centred so "
 "V_cont stays in 0.6–1.2 V — a requirement handed to steps 74/75."),
("Why is C1 allowed to be a MOS cap but C2 is a MIM cap?",
 "C1 is the large zero capacitor; a ±19 % variation of it moves the zero and changes PM by only a few degrees. C2 sets the "
 "pole and directly takes the charge packet each cycle; its linearity and its absolute value matter more, and it is small "
 "(2.2 pF), so a linear MIM costs little area."),
("How is R1 realised and why that resistor type?",
 "res_xhigh_po_2p85 (2.85 µm wide, 701 Ω/µm, 139 Ω heads), L = 15.5 µm → 11.0 kΩ. In the ngspice R/C corners it moves −12 % "
 "/ +13 % (mostly temperature: tc ≈ −2.5e-3/°C), against −17 % / +20 % for res_high_po. It is compact, and wide enough for "
 "low mismatch and flicker. 2.85 µm is one of the five legal widths."),
("How much does R1 add to the jitter, and what is the trade-off with β?",
 "0.31 ps FFNC-off / 0.165 ps FFNC-on (total 2.12 / 1.36 ps). Doubling β halves R (−30 % R noise) but doubles C1 and C2 area; "
 "halving β halves area but R-jitter rises to 0.40 ps. Between β = 0.5 and 2 µA/rad the total changes by only 0.03 ps, so "
 "β is chosen for area and for a Gm small enough to keep its own noise and offset low."),
("Why are the zero and pole at 0.84 MHz and 7.4 MHz?",
 "They are placed about geometrically around f_c with spread b = tan(45° + lead/2) ≈ 2.9: f_z = f_c/b, f_p = f_c·b (here "
 "slightly asymmetric because the sampled-loop correction adds lead). The zero gives the phase lead at f_c; the pole "
 "filters the per-cycle charge-packet ripple and the reference spur."),
("What is the closed-loop peaking and the 3 dB bandwidth?",
 "2.5 dB peaking, f_3dB = 4.3 MHz. Peaking amplifies in-band (reference, SSPD, CP) noise near f_c; 2.5 dB is acceptable "
 "because those sources are ≥ 10 dB below the VCO contribution in the budget."),
("How do you check the loop's lock behaviour at this stage?",
 "With the same sampled model, cycle by cycle: after a 1 rad reference phase step the error overshoots 27 % and settles "
 "inside ±10 ps in 0.34 µs. The 5 µs lock-time spec is therefore set by FLL acquisition (step 81), not by the phase loop."),
("Which parameters make up the loop-gain spread m?",
 "m = (A·g_m·τ·K_VCO)/nominal. A (SSPD amplitude, buffer swing), g_m (bias, mobility), τ (pulser RC) and K_VCO (ring) "
 "all vary over PVT; their product can span about ×0.3 to ×2.4 before any trim."),
("How robust is the loop to m and to the R/C corners?",
 "At nominal R/C, PM ≥ 45° for m = 0.46–1.75. At the worst R/C combinations (R −12/+13 %, MIM −12/+13 %, MOS cap −19/+8 % "
 "over V_cont 0.6–1.2 V, ss/ff, −40/110 °C) the range narrows to m = 0.78–1.23. With a residual m of 0.75–1.3, PM stays "
 "45.5–50° and f_c 1.8–3.3 MHz at every corner."),
("What does icp_trim do and how is it built?",
 "It changes the number of identical Gm unit cells: 00 → 3 units (nominal), 01 → 4, 10 → 2, 11 → 5, i.e. β ×1, ×1.33, ×0.67, "
 "×1.67. It recentres the process part of m (≈ ×0.55 to ×2.0) to within about ±17 %, leaving room for voltage and "
 "temperature drift. Unit cells (rather than a trimmed resistor or pulse width) keep the layout regular and the Gm noise "
 "proportional to β."),
("Why should code 00 be the nominal setting?",
 "All controls power up at 0. With 00 = nominal the PLL locks with a sensible bandwidth before any calibration, which makes "
 "bring-up and the first measurements safe. The offset-binary decode costs three gates on VDDD."),
("What happens if PM drops to 40°?",
 "The loop is still stable, but peaking rises to about 4 dB, the overshoot grows, and in-band noise is amplified near f_c. "
 "The jitter model at PM 40° gives out2 pess 1.84 ps — still inside the 3.2 ps max — so 40° is the floor, 45° the target."),
("Why is the continuous approximation good below f_c but wrong near f_REF/2?",
 "Below f_c the loop sees many samples per cycle of any disturbance, so sampling is invisible. Near f_REF/2 the sampled gain "
 "folds and its phase falls faster (delay e^{−jωt_p} plus the hold): the sampled |L| flattens at −25 dB while the continuous "
 "one keeps falling. Gardner's rule (f_c < f_REF/10) keeps the difference small; here f_c/f_REF = 1/20."),
("What is Gardner's stability limit and how far are we from it?",
 "For a CP-PLL the sampled loop becomes unstable when the loop gain is so high that the per-cycle correction overshoots; "
 "roughly ω_c²·T² limits apply when f_c approaches f_REF/π. At f_c = f_REF/20 we are far below; m = 3 (f_c ≈ 6 MHz) still "
 "keeps PM above 30°."),
("How does the FLL interact with this loop filter?",
 "The FLL charge pump injects into the same filter while out of lock. With C_tot ≈ 19 pF a 10 µA FLL current slews V_cont at "
 "0.5 V/µs; once the phase error is inside the dead zone the FLL CP is off and only the pulsed Gm acts. Step 81 sizes the FLL "
 "current against this C_tot."),
("Why does the filter not use a third pole (4th-order loop)?",
 "The reference spur from a pulsed-Gm SSPLL is small (no PFD/CP mismatch pulses; in lock the packets are near zero), and "
 "C2 with the 7.4 MHz pole already filters the packet ripple at 50 MHz by about 17 dB. An extra RC pole would cost phase "
 "margin and area for a spur that is not the limiting spec."),
("What leakage matters in this filter?",
 "Gate leakage of the thin-oxide MOS cap and junction leakage at V_cont. A leakage I_L is supplied by the loop as a static "
 "phase offset θ = I_L/β and a small per-cycle ripple I_L·T/C2. For nA-level leakage the offset is mrad and the ripple µV, "
 "but it is checked in the loop-filter testbench (step 100) at 110 °C."),
("How does temperature move f_c?",
 "R (xhigh_po) falls about 19 % from −40 to 110 °C (+11 % / −10 % around 27 °C); K_VCO and g_m change too. Since f_c ≈ β·K_VCO·R/2π above the zero, f_c moves "
 "with the product; the robustness plot covers this with the R and m axes."),
("Why freeze the loop filter now, before the VCO and CP exist?",
 "C1 and C2 are the largest analog blocks after the CCO and the decap; their area and shape set the floorplan of the "
 "CP + LF region. Freezing them (and absorbing K_VCO uncertainty in g_m) lets the floorplan and layout start early."),
("What is in the design sheet that the block designers need?",
 "β·K_VCO product, g_m per unit, τ and t_p limits, R1/C1/C2 with device names and sizes, V_cont window 0.6–1.2 V, icp_trim "
 "mapping, and the spread budget for m (process ×0.55–2.0, residual ×0.75–1.3)."),
("How would you verify the loop parameters in simulation?",
 "Step 100: AC of the filter impedance at R/C corners (zero, pole). Step 103: open-loop gain from extracted block gains. "
 "Step 104: transient lock with a phase/frequency step, compared with the cycle model's 0.34 µs and 27 % overshoot."),
("Why does the jitter barely depend on β at fixed f_c and PM?",
 "Because the only β-dependent noise is R1's, and R1's contribution is small (0.2–0.4 ps against 2.1 ps total). The detector "
 "and CP noise referred to VCO phase do not depend on how β is split between g_m and τ, only on A, g_m and d through the "
 "budget formulas of step 72."),
("Explain the open-loop gain shape in the Bode plot.",
 "Below the zero: two integrators (VCO and C_tot) → −40 dB/dec and −180°. Between zero and pole: −20 dB/dec, phase rises to a "
 "maximum near f_c (the lead). Above the pole: −40 dB/dec again. The sampled version adds extra phase lag from the delay "
 "and sampling and flattens near f_REF/2."),
("What would change if the reference were 45 or 55 MHz?",
 "T changes, so the per-cycle charge changes but the average gain β = 2A·g_m·τ/T changes with 1/T: β rises 11 % at 55 MHz "
 "and falls 10 % at 45 MHz (m = 1.11 / 0.90) — inside the residual band. f_c/f_REF stays near 1/20."),
("Why is the loop parameterised by β and not by an equivalent charge-pump current I_p?",
 "In a PFD/CP loop the CP current per radian of reference phase is I_p/2π and the divider adds 1/N. In the SSPLL there is no "
 "divider and the detector gain is per radian of VCO phase, so β (A/rad of VCO phase) is the natural unit; I_p/(2πN) of a "
 "CP-PLL corresponds to β."),
]

# Step 73 redo for the device-rule migration: 800 MHz, 5 V analog devices (docs/design/step73_hv_loop.md)
QA73HV = [
("Why does the 5 V MOS capacitor give 2.6× less capacitance per area, and why is its flat region higher?",
 "In inversion a MOS capacitor is the gate oxide: C_ox = ε_ox/t_ox. The 5 V devices have a gate oxide roughly 2.5–3× "
 "thicker than the 1.8 V devices, so C_ox falls to 2.87 fF/µm² against 7.48. The thicker oxide also raises the threshold "
 "voltage, so the channel forms later: the 5 V cap is flat (within 3 %) only above 1.0 V, while the 1.8 V cap was flat "
 "above 0.6 V. Below that the capacitance collapses towards the depletion value (1.3 fF/µm² at 0 V)."),
("C1 has to be smaller now. Why does lowering β keep the loop identical, and what does it cost?",
 "f_c and PM depend only on β·K_VCO/C and on R·C: C_tot = b·β·K_VCO/ω_c² and R1 = b/(ω_c·C1). Scale C1 and C2 by k and β "
 "by k, and R1 by 1/k: the zero (1/R1C1) and the pole stay put and the gain curve is unchanged. The cost is R1's thermal "
 "noise, 4kTR1, which grows as 1/k. Here 2 tiles (8.81 pF, R1 = 20.6 kΩ) cost 0.013 ps more than 3 tiles and save "
 "1 500 µm²."),
("Why does f_c come out at 2.5 MHz again at 800 MHz?",
 "The same two specs pull in opposite directions: L(300 kHz) with FFNC off (now −114 dBc/Hz) needs a wide loop, "
 "f_c ≥ about 2.25 MHz; the FFNC jitter reduction (35 % typ) needs a narrow one, f_c ≤ about 2.55 MHz. The jitter in "
 "seconds did not change with the carrier (same ring power and FoM), so the crossing point did not move either."),
("Why does the phase-step settling to ±10 ps take longer at 800 MHz although the loop is identical?",
 "The loop dynamics in radians are the same (27.6 % overshoot, same time constants), but the window is in seconds. At "
 "800 MHz, 10 ps is 2π·0.8 GHz·10 ps = 0.050 rad against 0.10 rad at 1.6 GHz, so the error has to decay twice as far: "
 "0.40 µs instead of 0.34 µs."),
("Why is the level shifter in the Gm pulse path not timing-critical for the loop, while the one on the sampling edge is?",
 "A delay in the Gm pulse only delays the charge packet: it adds 360°·f_c·t_p of phase lag — 0.9° for 1 ns at 2.5 MHz. "
 "Its jitter does not matter either, because the packet's charge, not its timing, carries the phase information. The "
 "sampling edge is the phase measurement itself: any jitter on it is reference jitter, multiplied by N² at the output."),
("Why centre the V_cont window at VDDA/2 (1.0–2.3 V)?",
 "The lower edge is set by the MOS capacitor (flat above 1.0 V). The upper edge leaves headroom for the Gm output "
 "cascodes and the FLL charge pump on the 3.3 V supply. Centring the window gives the Gm the most symmetric compliance and "
 "makes the VCO fine range symmetric around the lock point after the coarse code is set."),
("When would you stack MIM2 on MIM1 in the C1 tile, and what must you check first?",
 "cap_mim_m3_2 (met4/capm2, top plate on met5) has the same 2.0 fF/µm² and fits above MIM1, raising a tile from 4.4 to "
 "6.2 pF. Use it when area is tight. First check that the slot lets you use met5 (the harness may reserve it for power) "
 "and that the MIM2 rules (enclosure, spacing to MIM1 vias) fit the 35 µm tile."),
("Why does the flatter thick-oxide C-V improve the phase-margin spread at the C-min corner?",
 "C1 sets the zero. At the 1.8 V design the MOS share of C1 varied ×0.81–1.08 over its window and corners; the thick-oxide "
 "cap varies only ×0.93–1.06 over 1.0–2.3 V. A smaller C1 drop moves the zero up less, so the lead at f_c and the PM drop "
 "less: the residual band m = 0.75–1.3 keeps PM ≥ 46.5° at every R/C corner (45.5° before)."),
]
