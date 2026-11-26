"""Interview questions for roadmap step 76 (REF_IN receiver / reference buffer)."""
QA76 = [
("What does the reference buffer do in this PLL?",
 "It turns whatever the crystal oscillator delivers on the REF_IN pad (a 0.4 V pp sine up to a 0–3.3 V square wave) "
 "into a clean 1.8 V CMOS edge, refclk, for the clock generator that fires the sub-sampling phase detector. Its own "
 "noise is added to the reference, so it is multiplied by N² = 1024 (+30 dB) inside the loop bandwidth."),
("Why is reference-buffer noise so important in a sub-sampling PLL?",
 "The SSPD removes the divider and makes PD/CP noise small, so inside the loop bandwidth the output phase noise is "
 "set by the reference path: XO + buffer, times N². In this design FFNC-on L(300 kHz) is reference-limited: a perfect "
 "buffer gives −121.3 dBc/Hz, a −155 dBc/Hz buffer −119.7 (with a −160 dBc/Hz clock-generator placeholder)."),
("How do you convert voltage noise at a threshold crossing into jitter?",
 "σ_t = σ_v / slope at the crossing. For a sine of V_pp at f the slope at the zero crossing is π f V_pp: 1 V pp at "
 "50 MHz gives 0.157 V/ns, so 63 µV rms of noise is 0.4 ps rms. A square wave with 0.5 ns edges has a 20× steeper "
 "slope, so the same noise gives 20× less jitter."),
("How do you convert per-edge white jitter into a phase-noise floor?",
 "Independent jitter σ on every edge at f_ref is sampled white noise: S_φ (single-sided) = 2(2π f_ref σ)²/f_ref, so "
 "L = (2π f_ref σ)²/f_ref. 0.4 ps at 50 MHz is −155 dBc/Hz; 0.61 ps is −151.4 dBc/Hz."),
("Why AC coupling at the input?",
 "The external oscillator may have any DC level (0–1.8 V CMOS, 0–3.3 V CMOS, a clipped sine around ground or an "
 "AC-coupled sine). The coupling capacitor removes the DC, and the receiver biases its own input at its switching "
 "point, so the crossing is always at the middle of the input waveform and the duty cycle stays near 50 %."),
("How is the receiver input biased?",
 "Through R_B = 5 MΩ from the output of the first stage to its input. At DC this is a short, so the inverter sits at "
 "its trip point: v_in = v_s1 ≈ 0.86 V. At 50 MHz R_B is an open circuit, so the full signal reaches the gate."),
("What is the pad divider for?",
 "Two 500 kΩ poly resistors hold the pad at VDDA/2 when the oscillator is AC-coupled externally or not connected, so "
 "the pad never floats. They load the oscillator with 250 kΩ, negligible next to C_AC's 0.9 kΩ at 50 MHz, and cost "
 "3.3 µA."),
("Why is the first stage a current-limited inverter and not a plain self-biased inverter?",
 "A plain inverter at VDDA/2 runs both devices in strong inversion with a current that changes 4–6× over VDDA and "
 "process. The header current source fixes the current (60 µA) and lets the wide input devices run in moderate "
 "inversion, where g_m/I is high (~13 V⁻¹): more g_m — less noise — per µA."),
("What is C_H for?",
 "The header is a current source, so the pMOS input device's source sees a high impedance and is degenerated: it would "
 "add almost no g_m. C_H (1.8 pF MIM) ties that node to VDDA at high frequency, so XP1 adds its g_m (current reuse) and "
 "the header's own noise current is shunted into the capacitor instead of the output. It lowered the white input noise "
 "by about 30 %."),
("Why is XP1's body tied to its source?",
 "Its source sits about 0.9 V below VDDA. With the body at VDDA its threshold rose to 1.24 V (body effect), costing "
 "headroom at VDDA = 2.97 V. In its own n-well with body = source, V_th is about 1.0 V."),
("Why thick-oxide devices in S1 and S2?",
 "They connect to VDDA (3.3 V) and S1's gate connects to the pad through C_AC: with a 3.3 V pp input the gate swings "
 "from about −0.8 V to 2.5 V. Thin-oxide devices are rated for 1.8 V. The project rule: 3.3 V devices wherever a node "
 "touches VDDA or a pad."),
("How is the signal brought from 3.3 V down to 1.8 V?",
 "A thick-oxide inverter powered from VDDL (1.8 V): its gate tolerates the 0–3.3 V swing of S2, its output swings "
 "0–1.8 V. A down-shift needs no latch (unlike the up-shift of step 75) because a 3.3 V input fully turns the 1.8 V "
 "inverter on and off."),
("Why is the output a NOR gate?",
 "NOR(s3, not pll_en): when enabled it is an inverter, when disabled it forces refclk low, so the clock generator and "
 "SSPD see a defined, quiet state. All controls default to 0."),
("What happens when pll_en = 0?",
 "XPEN pulls the header gate to VDDA (S1 current off), XNS1 pulls s1 low (and through R_B the input), so no device "
 "carries static current; the output NOR holds refclk at 0. Only the pad divider (3.3 µA) remains."),
("Why is there a start-up time after pll_en?",
 "When enabled, the input sits at 0 V and must charge to the trip point through R_B into C_AC + C_in "
 "before the crossing is centred; simulated, the periods are within 2 % about 4 µs after pll_en and the bias keeps settling for some 30 µs. The CCO filter needs "
 "about 0.3 ms, so the FLL (step 81) waits for that anyway."),
("How did you choose R_B?",
 "Its noise current flows into the input node. Inside the bias loop the low-frequency level at the gate is "
 "4kT·R_B/(1 + A)², flat up to the corner (1 + A)/(2π R_B C), which lies above 300 kHz because A ≈ 190. So a smaller "
 "R_B gives LESS noise in the 10 kHz–1 MHz band: 20 MΩ gave 3.3 nV/√Hz at the gate, 5 MΩ 1.7 nV/√Hz. 5 MΩ is also four "
 "times smaller (10 segments) and starts up faster. The lower limit: the input high-pass corner, about 1.5 MHz, must "
 "stay far below 45 MHz."),
("How was the noise verified?",
 "Two methods. M14: .noise at the self-bias point (which is the crossing point of S1) gives the input-referred "
 "spectrum, including flicker and R_B; its low-frequency part converts to phase noise through the input slope. M15: "
 "a transient with the white part of that spectrum injected at the pad (trnoise) gives the per-edge jitter directly "
 "from 300 edge times, including the stage's non-linear switching."),
("Why not just divide the integrated .noise output by the output slope?",
 "S1 is a high-gain comparator: its small-signal low-frequency gain (≈ 190) is much larger than the gain that applies "
 "to the fast-moving input during a crossing (≈ 30), so output-referred noise over output slope overestimated the "
 "jitter 2×. The transient-noise run measures what really happens; the small-signal analysis is used only for the "
 "slow (quasi-static) noise, where it is exact."),
("What is the effective noise bandwidth of the receiver and why does it matter?",
 "σ_v = σ_t × slope; with the white input noise S_w this defines B_eff = σ_v²/S_w ≈ 650 MHz, close to S1's "
 "gain-bandwidth. The per-edge jitter is √(S_w·B_eff)/slope: lower noise density (more g_m) or less bandwidth reduce it, "
 "at the price of power or delay."),
("What does the receiver achieve?",
 "Per-edge jitter 0.23 ps with a 3.3 V pp input (−159.9 dBc/Hz), 0.61 ps at 1 V pp (−151.4), 1.15 ps at 0.4 V pp "
 "(−145.8). With the ring, CCO and loop: 1.95 / 1.26 ps and L(300 kHz) −111.0 / −120.7 dBc/Hz at 3.3 V pp; at 1 V pp "
 "1.97 / 1.33 ps and −110.6 / −118.2."),
("Does the design meet the specification?",
 "All guaranteed (max) limits are met over the whole 0.4–3.3 V pp input range. The typical targets need a full-swing "
 "input (≥ about 2 V pp, e.g. a 3.3 V CMOS crystal oscillator): with a 1 V pp sine the FFNC-on L(300 kHz) is 1.8 dB "
 "above its typical target. So the typical specification is stated for a full-swing reference."),
("Why not simply burn more current to fix the 1 V pp case?",
 "Doubling S1's current (+0.2 mW) lowers the white jitter only by √2: L(300 kHz) FFNC-on would still be about "
 "−119.5 dBc/Hz at 1 V pp, while the worst-case power margin (0.4 mW) would be almost used up. A full-swing XO costs "
 "nothing on chip."),
("How sensitive is the edge time to supply noise?",
 "Measured by stepping VDDA and VDDL by 10 mV and comparing the delays (finite difference). Supply ripple at the "
 "reference rate moves every edge the same way and appears as a spur; random supply noise inside the loop bandwidth "
 "is multiplied by N² like any reference noise."),
("What sets the duty cycle and does it matter?",
 "The input is centred by the self-bias, and later stages switch near mid-supply, so the duty stays 47–53 % at typical supplies; at VDDA = 3.63 V with the smallest (0.4 V pp) input it rises to about 65 % because S2's threshold moves with VDDA while s1's edges are slow. The SSPD "
 "only uses the rising edge (the clock generator makes its own pulses from it), but the proposal guarantees ≥ 45 %."),
("Which layout precautions does this block need?",
 "REF_IN routed short and shielded from the pad, the high-impedance vin node (5 MΩ) guarded and away from digital "
 "lines, C_AC with its bottom plate on the pad side (bottom-plate parasitic driven by the low-impedance source), XN1 and "
 "XP1 with dummies, XP1 in its own n-well, C_H next to the header, R_B as a serpentine over a quiet area."),
("Why the bottom plate of C_AC on the pad side?",
 "The MIM bottom plate has a larger parasitic capacitance to the substrate. On the pad side it is driven by the 50 Ω "
 "source and does not matter; on vin it would attenuate the signal and couple substrate noise into a 20 MΩ node."),
("What ESD considerations apply?",
 "The pad cell provides primary ESD protection. Behind it the only connections are poly resistors and the MIM "
 "capacitor's bottom plate — no gate is connected directly to the pad. The MIM dielectric must withstand the pad's ESD "
 "voltage; this is checked with the pad cell in the top-level ESD review."),
]
