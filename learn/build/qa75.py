"""Interview questions for roadmap step 75 (CCO: current-fed supply of the ring VCO)."""
QA75 = [
("What is the CCO in this design and why is the ring fed by a current?",
 "A programmable current source from VDDA (3.3 V) into the ring's supply node. A current-fed ring settles at the voltage "
 "where it draws exactly that current, so the current sets the frequency (K_I ≈ 0.85 GHz/mA). The current source's high "
 "output impedance isolates the ring from VDDA noise, and the DAC gives the coarse tuning."),
("Draw the CCO from IBIAS to the ring node.",
 "IBIAS (5 µA) → 2-unit nMOS diode → unit sinks of 2.5 µA (13 base + binary 1, 2, 4, 8, 16, switched by cco_code) → "
 "pMOS diode MREF (1 unit) → 10 MΩ / 7.3 pF RC filter → MOUT (25 units) → ring node. I_out = 25 × 2.5 µA × (13 + code) = "
 "62.5 µA × (13 + code): 0.81–2.75 mA."),
("Why a 1:25 output mirror and not 1:8?",
 "The reference branch also draws its current from VDDA: with 1:8 that is +12.5 % of the ring current, with 1:25 only +4 %. "
 "At the worst corner (2.0–2.3 mA at 3.63 V) that saves 0.6–0.7 mW, which brings the worst-case power back under 15 mW. "
 "The price: reference-side noise is multiplied by 25 — which the RC filter removes."),
("Why is the DAC range 0.81–2.75 mA when the ring only needs 0.97–2.26 mA?",
 "IBIAS from the harness may be 4.0–6.0 µA (±20 %), and the DAC current scales with it. At IBIAS = 6 µA, code 0 must still "
 "be low enough for 1.44 GHz at ff/−40 °C (0.97 mA); at 4 µA, code 31 must still reach 1.76 GHz at ss/110 °C (2.02 mA at "
 "10 fF/node). The ±20 % costs a 3.4:1 code range."),
("How fine is the coarse tuning and why is it fine enough?",
 "One LSB is 62.5 µA, i.e. about 53 MHz at tt (K_I 0.85 GHz/mA). The fine-tune range over the 0.75–1.2 V lock window is "
 "about 150 MHz, roughly 3 LSBs, so after the coarse code is chosen the loop can always reach lock with margin for "
 "temperature drift."),
("Why the RC filter between the two mirror gates?",
 "Without it, the noise of the reference side (MREF, the DAC units, the IBIAS input) appears at the output multiplied by "
 "the mirror ratio (×25 in current, ×625 in power). The RC low-pass with a ~2 kHz corner removes it everywhere in the "
 "10 kHz–40 MHz band, so only MOUT's own noise and the filter resistor's noise remain."),
("Why is the filter resistor 10 MΩ and not 300 kΩ?",
 "Above the RC corner the resistor's own noise at the gate falls as √(4kT/R)/(2πCf): a larger R with the same C gives "
 "LESS noise in band. With 300 kΩ the output noise was 21 pA/√Hz at 1 MHz and L(300 kHz) FFNC-off −104.4 dBc/Hz; with "
 "10 MΩ it is 8.9 pA/√Hz and −110.9 dBc/Hz."),
("How is a 10 MΩ resistor made legal and layout-friendly?",
 "20 series segments of res_xhigh_po_0p35 (the highest sheet resistance, 0.35 µm is a legal width), each 87.48 µm long "
 "(≈ 500 kΩ including heads), drawn as a serpentine. Every segment is inside the PDK limits and the array folds into a "
 "compact block."),
("Where does the 7.3 pF filter capacitor go?",
 "Four 30 × 30 µm MIM tiles, placed over the output-transistor array (the MIM layers are above the active devices), so "
 "they cost no extra area. Top plate on the high-impedance gate node, bottom plate on VDDA. MOUT's own gate capacitance "
 "(several pF) adds to it."),
("Why is the filter capacitor tied to VDDA and not to ground?",
 "The output pMOS current depends on its source-gate voltage. With the capacitor to VDDA, a VDDA step moves the gate with "
 "the source, so Vsg — and the current — stays constant: supply rejection. A capacitor to ground would hold the gate "
 "still and turn every VDDA ripple into a current ripple."),
("What sets the CCO output noise floor?",
 "MOUT's channel noise, i_n² = 4kTγ·g_m. With 25 units of 40/2 µm and ~1.45 mA, g_m is a few mS; the result is "
 "8.9 pA/√Hz at 1 MHz (requirement ≤ 10.3). Lower g_m (larger overdrive) would help but costs headroom: VDDA_min − "
 "V_ring_max = 2.97 − 1.8 = 1.17 V."),
("Why thick-oxide (g5v0d10v5) devices in the CCO?",
 "Every device connected to VDDA can see up to 3.63 V (3.96 V absolute) between terminals; thin-oxide devices are "
 "rated for 1.8 V. The project rule: 3.3 V devices wherever a node touches VDDA or a pad."),
("Why L = 2 µm for the mirror and 4 µm for the DAC units?",
 "Long channels lower flicker noise (area), raise output impedance (better DAC accuracy and supply rejection) and improve "
 "matching. The output still saturates: Vov ≈ 0.5–0.7 V against 1.17 V of headroom."),
("What does the clamp do and why is it needed?",
 "At ss/110 °C with IBIAS +20 % and a high code, the CCO could push the ring node to ~2.0 V — above the 1.8 V rating of "
 "the ring's core devices and above the proposal's absolute limit. The clamp sinks the excess current once the node reaches "
 "the 1.8 V rail (VDDL)."),
("Why did a simple one-transistor clamp not work?",
 "A pMOS from the ring node to ground, biased by a replica, conducts by Vsg: to sink ~1 mA at 1.8 V it already steals "
 "0.4–0.85 mA at 1.7 V, which is exactly where the ring must run at the top of its range. Its I-V is not sharp enough."),
("How does the two-stage active clamp get a sharp knee?",
 "A small sense pMOS (gate at the replica voltage) conducts exponentially (weak inversion) as the ring node approaches VDDL; "
 "its current into 320 kΩ drives the gate of an nMOS shunt. The shunt only turns on when that voltage reaches its "
 "threshold, adding gain: < 10 µA at 1.725 V, 0.2–1.5 mA at 1.8 V. With the ring's I-V at ss/110 °C, code 31 and IBIAS "
 "6 µA the node stays at 1.793 V."),
("Why is the clamp referenced to VDDL and a replica pMOS?",
 "The replica diode from the 1.8 V rail sets the sense gate one |Vgs| below VDDL, so the sense device turns on when the ring "
 "node reaches VDDL regardless of the pMOS threshold at that corner (it tracks process and temperature). VDDL is the "
 "regulated rail whose voltage is, by definition, safe for 1.8 V devices."),
("How is the CCO disabled (pll_en = 0)?",
 "A thick-oxide pMOS pulls the output gate to VDDA (MOUT off) and a thick-oxide nMOS shorts the IBIAS input to ground (all "
 "DAC units and the clamp replica off). The base units' switch is also driven by pll_en. All controls default to 0, so the "
 "block powers up off."),
("What is VTEST for and how is it injected?",
 "The test plan uses a tone on ANA0 (VTEST) to calibrate the cancellation gain (50 kHz) and to measure supply sensitivity "
 "(1 mV pp at 100 kHz). A thick-oxide transmission gate (vtest_en) and a 20 kΩ poly resistor inject (V_test − V_ring)/20 kΩ "
 "into the ring node: 1 mV → 50 nA → ~42 kHz frequency deviation, a clearly measurable spur."),
("Why level shifters, and how does yours work?",
 "cco_code, pll_en and vtest_en come from the 1.8 V digital domain but drive 3.3 V switches. A thin-oxide inverter on VDDD "
 "makes in/inb; thick-oxide nMOS pull-downs flip a cross-coupled thick-oxide pMOS latch on VDDA; output inverters give "
 "full 3.3 V out/outb. Pull-downs (W 3 µm) are sized to win against the pMOS loads (W 1 µm) even at VDDD 1.71 V."),
("How was the CCO verified?",
 "DC operating points (current vs code over 5 corners × VDDA × IBIAS), a compliance sweep, the clamp with the ring's "
 "measured I-V, an AC supply-rejection analysis, .noise of the complete circuit with PDK resistors and capacitors "
 "(converted to jitter through the loop model), and a level-shifter transient at the hardest supplies. Methods M10–M13."),
("How do you convert CCO current noise to phase noise?",
 "Frequency noise S_f = K_I²·S_i (Hz²/Hz); phase noise S_φ = S_f/f²; L = S_φ/2. In the PLL it is shaped like VCO noise: "
 "|(1 − G_c)(1 − H)|², so low-frequency CCO noise is suppressed by the loop and FFNC."),
("Why did the CCO beat its step-72 allocation?",
 "The allocation assumed 7.2 pA/√Hz with a 0.3 MHz flicker corner; the measured K_I (0.85 instead of 1.22 GHz/mA) relaxes "
 "the current-noise requirement by 1.44×, and the long-channel devices plus the filter keep the spectrum low. Result: "
 "0.70 ps (FFNC off) / 0.44 ps (on) instead of 0.90 / 0.56 ps."),
("What would you check in layout for this block?",
 "Common-centroid placement of MREF among the 25 MOUT units, dummies at the array ends, the MIM tiles over the array, the "
 "serpentine resistor away from the ring and shielded, the gate node (vgo) kept short and guarded (it is a 10 MΩ "
 "high-impedance node: leakage and coupling matter), thick-oxide devices in their own well/guard ring."),
("What leakage could upset a 10 MΩ / 7 pF filter node?",
 "The gate node draws no DC current, but junction leakage of the enable pMOS drain and the resistor body leakage flow "
 "through 10 MΩ: 1 nA gives 10 mV of offset between vgr and vgo, i.e. a few % current error — a static offset the loop "
 "absorbs, but it is verified at 110 °C (leakage doubles every ~10 °C)."),
("How does VDDA noise reach the ring?",
 "Through the finite output impedance of MOUT and through the gate coupling. The AC analysis gives ΔI/ΔVDDA of about "
 "0.25 mA/V up to 1 MHz, i.e. 1 mV of VDDA ripple → 0.25 µA → ~0.2 MHz deviation — further reduced by the loop and FFNC "
 "below 2.5–6 MHz."),
("What is the start-up behaviour?",
 "pll_en rises, the level shifter releases the enable devices, IBIAS flows into the DAC and the reference diode, the filter "
 "charges the output gate with τ = RC ≈ 70 µs — the current ramps up over ~0.2 ms. The FLL waits for it (step 81)."),
("Could the 70 µs RC time constant be a problem for lock time?",
 "Only at power-up: once the CCO current has settled, the coarse code is static. The 5 µs lock-time spec is measured "
 "'from pll_en with coarse code set' — but the code must be set before the CCO is enabled, and the slow filter is "
 "precisely why the test plan sets cco_code first."),
]
