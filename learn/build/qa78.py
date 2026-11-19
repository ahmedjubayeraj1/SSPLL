"""Interview questions for roadmap step 78 (sub-sampling phase detector with hold)."""
QA78 = [
("What does the SSPD do, in one sentence?",
 "At every reference edge it takes a sample of the VCO waveform; near lock the sampled voltage is proportional to the "
 "time (phase) error between the VCO zero crossing and the reference edge, with gain dv/dt of the waveform, and no "
 "divider is needed because sampling a 1.6 GHz wave with 50 MHz folds it down by itself."),
("Why is the SSPD gain not divided by N like a PFD's?",
 "A PFD compares the reference with the VCO divided by N, so a VCO phase error φ appears as φ/N at its input. The SSPD "
 "looks at the VCO itself: an error of φ radians of VCO phase moves the sampled voltage by A·φ. The gain is set by the "
 "VCO waveform slope, not by N, so the PD and charge-pump noise are not multiplied by N² at the output."),
("What is A and how did you get it?",
 "A is the slope of the sampled waveform at the lock point per side, in volts per radian of VCO phase: dv/dφ = (dv/dt)/ω0. "
 "The differential sample v1p − v1m changes by 2A per radian. It is measured with a beat run: the VCO runs at "
 "(32 + 1/32)·f_ref, so each reference period samples 1/32 of a VCO cycle further along; a line fit within ±0.35 rad "
 "of the zero crossing gives 2A. Result 0.514 V at tt (target 0.5 V)."),
("Why put a series resistor in front of the sampling capacitor?",
 "The isolation buffer makes a sharp square wave, whose slope at the crossing would be very large, badly defined (it "
 "depends on the inverter edge) and linear over only a few picoseconds. R_s and C1 round it into a near-sine. For an "
 "RC-filtered square of amplitude VDD/2 the slope at the crossing is exactly (VDD/2)/τ_s, so A = VDD/(2ω0 R C): set by "
 "a resistor and a capacitor, with a linear range of about ±1 rad. kT/C noise does not change: it depends only on C."),
("Derive the slope of an RC-filtered square wave at its zero crossing.",
 "After an edge, v(t) = a(1 − 2e^{−t/τ}/(1 + e^{−T/2τ})) for a square of ±a. It crosses zero where e^{−t_c/τ} = "
 "(1 + e^{−T/2τ})/2. The slope is dv/dt = (2a/τ)e^{−t/τ}/(1 + e^{−T/2τ}), which at t_c is exactly a/τ, independent of "
 "the period. With a = 0.9 V and A = 0.5 V at 1.6 GHz: τ = a/(Aω0) = 179 ps."),
("Why a transmission gate with a low-Vt nMOS as the sampling switch?",
 "The sample is taken near mid-rail (the common mode of the filtered wave, ≈ 0.72 V). A standard nfet_01v8 with its "
 "source at 0.9 V has a body-affected threshold near 1 V and gives 5.4 kΩ at W = 2 µm; the pfet_01v8 is worse (35 kΩ). "
 "nfet_01v8_lvt gives 1.8 kΩ at the same size. The pMOS in parallel helps when the waveform is high and cancels part of "
 "the nMOS channel charge at turn-off."),
("What is the dummy sampler and why is it there?",
 "A second switch and capacitor (CD = C1 + the Gm input) on the same node f, driven by the opposite clock. When the "
 "sampler opens, the dummy closes, so the isolation buffer always drives one capacitor. Its delay and its supply "
 "current then do not change at f_ref. Without the dummy the SSPD current has a 42 µA component at f_ref; with it, "
 "0.76 µA (−35 dB). That current would ripple the LDO rail that also feeds the VCO buffers and the NCB: a reference spur."),
("What are the isolation buffers for?",
 "Two inverters between the VCO output (clkp/clkm, shared with the NCB and the divider) and the sampler. The first is "
 "small (0.42/0.84 µm), so clkp sees ~2 fF; the second drives R_s and C1. The sampler's switching charge then reaches "
 "clkp only through the gate-drain capacitance of the small inverter: the clkp edges move by at most 1.2 fs, a spur "
 "estimate of −147 dBc."),
("Why does the Gm read C1 and not C2?",
 "Sharing C1 with C2 makes C2 a memory: v2[k] = (1 − α)v1[k] + αv2[k−1], α = C2/(C1 + C2) ≈ 0.47. A pole at z = α inside "
 "the PLL loop would cost about 16° of phase margin at f_c = f_ref/20. So the Gm reads C1 during the 200 ps pulse right "
 "after the sample, and only then is C1 shared onto C2. Step 77's clock order was changed for this (t_p also fell from "
 "2.63 to 0.28 ns)."),
("What is C2 for, then?",
 "The NCB needs the measured phase error for a whole reference period, while C1 is busy tracking the VCO again. C2 "
 "holds it. The charge-sharing pole on that path is the one the FFNC model already contains (−60° at f_ref/7.8 "
 "together with the hold and the half-period delay)."),
("How did you measure α?",
 "From the same beat run: every period gives a pair (v1[k], v2[k]). A least-squares fit of v2[k] = a·v1[k] + b·v2[k−1] "
 "gives b = α = 0.473 and a + b = 1.000 (the hold has unity DC gain). The capacitor ratio predicts "
 "(34.7 + 4)/(34.7 + 6 + 3 + 34.7 + 4) ≈ 0.47."),
("Why C1 = C2 = 35 fF and not the 100 fF of the roadmap?",
 "Power. The buffer must swing C at 1.6 GHz: about C·ΔV·f per side. 100 fF cost 0.70 mW, 35 fF 0.47 mW. The kT/C noise "
 "goes up by 4.6 dB but it is far below the reference: the system model gives L(300 kHz) −121.00 vs −121.01 dBc/Hz and "
 "the same jitter. The step-72 budget already allowed ≥ 50 fF; going lower was checked with the full model."),
("How large is the kT/C noise of the sampler in phase terms?",
 "Each side gets kT/C; the differential sample has 2kT/C. Divided by (2A)² it is a phase variance kT/(2CA²) per sample, a "
 "white floor L = kT/(2 C A² f_ref) = −144.7 dBc/Hz with C ≈ 46 fF and A = 0.514 V. It is not multiplied by N² — about "
 "15 dB under the reference contribution at the output."),
("Which noise of the SSPD does count like reference noise?",
 "Timing noise of the isolation buffers. The loop sees the VCO through them, so a random delay there is "
 "indistinguishable from reference jitter: it is multiplied by N² inside the bandwidth. The clkp node itself is common "
 "with the output path, so its noise is VCO-like. Method M17 on XB1/XB2 gives the jitter of the filtered crossing."),
("How does A vary over PVT and why is that acceptable?",
 "0.35 V (ss_hh) to 0.77 V (ff_ll); over temperature only ±3 % at a fixed corner, over VDDL ±10 % per ±5 %. A follows "
 "1/(R_s C1), so the R/C process corner moves it most. The loop needs β·K_VCO; A·τ·K_VCO at the extreme corners is "
 "×0.69–1.41, inside the icp_trim range (process ×0.55–2.0). What the trim cannot remove is drift, and the drift is small."),
("Why does A depend on VDDL?",
 "The filtered square has amplitude VDD/2 and the slope at the crossing is (VDD/2)/τ_s, so A ∝ VDDL. The LDO keeps "
 "VDDL fixed; its tolerance is part of the residual spread handed to step 79."),
("What is the common mode of the sample and why is it not 0.9 V?",
 "0.72 V at tt (0.60–0.82 V over corners). The TG conducts better at low voltage (lvt nMOS) than at high voltage (a "
 "standard pMOS), so the falling half of the wave is driven harder: the average and the crossing level sink below "
 "VDD/2. Only the differential sample matters for the loop; the Gm input stage (step 79) must accept 0.6–0.85 V."),
("What sets the linear range of the SSPD?",
 "The shape of the sampled waveform. The near-sine has a linear region of about ±0.7 rad around the crossing and peaks "
 "at ±1.1 V differential near ±π/2. Outside, the gain falls and reverses: the SSPD has no frequency information, so the "
 "FLL must bring the VCO within the capture range first."),
("Is the SSPD characteristic symmetric?",
 "Per side, no: the TG makes rise and fall slightly different. Differentially, yes: the m side is the p side shifted "
 "by π, so v1p − v1m is odd-symmetric and both zero crossings have the same slope (0.514 V/rad at tt, checked). The "
 "loop polarity (step 79) picks the stable one."),
("What is the kick-back problem and how big is it here?",
 "When the sampling switch opens or closes, its channel charge and the capacitor's sudden connection disturb the node "
 "that drives it, and through it the VCO: a periodic disturbance at f_ref, i.e. a reference spur. Here the "
 "disturbance reaches clkp through two isolation stages: at most 0.28 mV and 1.2 fs of edge shift; the ring itself is one "
 "more buffer away."),
("How did you measure the kick-back?",
 "Two otherwise identical runs at f = 32·f_ref: one with the clock generator running, one with refclk held low (the "
 "sampler tracks, nothing switches). The difference of the clkp edge times is the kick-back; its Fourier component at "
 "f_ref, as a phase deviation 2π f0 Δt, gives the spur estimate 20 log(a1/2)."),
("Why must the hold pulse be long (≥ 1.5 ns)?",
 "sw2 shares C1 and C2 through its on-resistance (~3 kΩ with 1 µm devices): τ ≈ 3 kΩ × 20 fF (C1 and C2 in series) "
 "= 60 ps. 2.16 ns is many time constants; the length mainly keeps the end of the transfer far from the next tracking "
 "phase and lets the switch's own injection settle."),
("What does the Gm input capacitance do to the SSPD?",
 "It is part of the C1 node: it slows τ_s (lower A) and is copied in the dummy capacitor (CD = C1 + 6 fF) so that the "
 "load stays constant. Step 79 must keep its input capacitance near 6 fF per side, or the dummy is resized."),
("Why does the hold switch use smaller devices than the sampling switch?",
 "Its speed is not critical (2 ns to settle 60 ps), and a smaller switch injects less charge onto C2 and loads ckh less."),
("How would you verify the SSPD in Cadence?",
 "Same beat testbench with analogLib vpulse sources and the clock generator. For the characteristic use the "
 "Calculator to sample v1p − v1m at the Gm pulse (value at a time list) and plot against phase; or run pss with the "
 "reference as the beat frequency and the VCO at 32 + 1/32 times it. Kick-back: two transients and the difference "
 "of the cross() times."),
("What would you do if a later step needs a larger A?",
 "Shorten R_s (A ∝ 1/R): R_s = 0.69 × 0.5 µm gives A ≈ 0.55 V. Below that the transistors dominate τ_s and A follows "
 "the MOS corners more. Alternatively a smaller C1, at the cost of the Gm input mattering more."),
("What layout precautions does the SSPD need?",
 "Mirror symmetry between the p and m sides; C1, CD and C2 as matched MIM tiles with the bottom plate on VSS; R_s next "
 "to the switch; the clock lines cks/cksb routed with equal length to both sides and away from v1; v1 and v2 shielded "
 "(they are high-impedance during hold); clkp/clkm entering symmetrically from the VCO buffers."),
]

# step 78 redo: 5 V SSPD at 800 MHz (19 Nov 2026)
QA78HV = [
("Why does A need a longer τ_s at 800 MHz on 3.3 V than at 1.6 GHz on 1.8 V?",
 "A = VDDA/(2ω0τ_s). Halving ω0 doubles A for the same τ_s, and the 3.3 V swing almost doubles it again. To land on "
 "the same kind of target (0.8 V/rad from step 72 HV) the RC must therefore be about 2.3× slower: τ_s = 3.3/(2·2π·0.8 GHz·0.8) "
 "= 0.41 ns instead of 0.18 ns. With C1 unchanged that means a larger R_s (≈ 3.4 kΩ, xhigh-poly 0.35 × 0.6 µm)."),
("Why is there no low-V_T sampling switch any more, and what replaces it?",
 "The device rule allows only g5v0d10v5 devices in analog blocks, and there is no low-V_T 5 V nMOS. At the sampled "
 "level (≈ 1.66 V) the nMOS has V_GS ≈ 1.65 V on a 3.3 V clock, which is enough, but its on-resistance is higher per "
 "micron. So the TG is wider (n 3 µm, p 6 µm) and the pMOS, which is well on at mid-rail with a 3.3 V clock, carries "
 "about half the conductance. A wider TG (4/8 µm) was tried: more junction capacitance lowered A to 0.788 V/rad and "
 "cost 4 % more power."),
("Why does A now change with VDDA, and why is that acceptable without an LDO?",
 "The filtered square swings VDDA/2 around its mid-level, so the slope at the crossing, and A, are proportional to VDDA: "
 "0.693 / 0.811 / 0.950 V/rad at 2.97 / 3.3 / 3.63 V. The static part (the chip's VDDA) is a fixed loop-gain error, "
 "covered by the icp_trim like a process corner. The fast part (supply noise) only scales the tiny locked phase error "
 "and so produces a second-order effect; the supply noise that matters is what moves edges, measured separately (M21)."),
("Why is the kick-back 30× larger than in the 1.8 V design, and does it matter?",
 "The sampling clock now swings 3.3 V instead of 1.8 V, and 0.5 µm-long thick-oxide devices have larger overlap "
 "capacitances, so more charge reaches XB2's output and, through XB1's gate–drain capacitance, clkp. The edge right "
 "after the sampling instant moves by 69 fs, a spur estimate of −99 dBc at the ring buffer output. The proposal allows "
 "−45 dBc maximum (−55 typical), so it is 54 dB inside, and the ring itself is one more buffer away."),
("Why does the SSPD use twice its power allocation?",
 "Each side swings its sampling capacitance (≈ 46 fF with the Gm input and junctions) through 3.3 V at 800 MHz: "
 "2 × 46 fF × 3.3² × 0.8 GHz ≈ 0.80 mW, plus the buffers' own gates: 1.03 mW measured. The step-72 allocation (0.49 mW) "
 "scaled the 1.8 V design by current; the right scaling is C·V²·f, which is (3.3/1.8)² × ½ = 1.68× higher per farad."),
("Why is the MIM capacitor C1 only 16.2 fF?",
 "Because the Gm's input is part of the sampled node. Step 79 measured it: 26.5 fF per side at tt (24–29 fF over "
 "corners and trim codes), not the 8 fF placeholder used at first. The node that sets A, α and kT/C is C1 + C_Gm + junctions, so "
 "C1 was cut from 4 × 4 to 2.69 × 2.69 µm to keep that node at 45.7 fF (step 72 requires ≥ 35 fF); the dummy CD "
 "(= C1 + C_Gm) stayed the same. A rerun of all 18 conditions confirmed A = 0.811 V/rad at tt. Making the node "
 "smaller would save power, but the Gm's non-linear gate capacitance (up to +25 % over ±0.8 V) would dominate it."),
("Why is a DC supply step enough for the isolation buffers but not for the receiver?",
 "Method M21 exists because a self-biased, AC-coupled stage changes its operating point with a time constant, so its "
 "sensitivity depends on the ripple frequency. The isolation buffers are plain inverters driven rail to rail: no bias "
 "node, no coupling capacitor, nothing with memory. Their delay sensitivity is the same at DC and at MHz, so a +10 mV "
 "step (22 ps/V) is the whole answer."),
("How was R_s chosen?",
 "By full beat runs with the real clock generator at three lengths of the xhigh-poly resistor (0.35 µm wide): 0.8 µm "
 "gave A = 0.701, 0.6 µm 0.812 and 0.5 µm 0.880 V/rad. 0.6 µm is closest to the 0.8 V/rad target and keeps the "
 "minimum over corners (0.536 at ss_hh, 2.97 V, in the final design) above the 0.5 V/rad floor."),
("Why does the dummy sampler matter more without an LDO?",
 "Without it, the isolation buffer charges C1 only while the sampler tracks, so the SSPD current has a component at "
 "f_ref (27.9 µA). That current flows in the VDDA wiring shared with the ring's CCO, the NCB and the buffers: an f_ref "
 "ripple there is a reference spur source. With the dummy the buffer always drives one capacitor: 0.80 µA (−31 dB)."),
("Which SSPD noise is multiplied by N², and which is not?",
 "kT/C of the sampling capacitor is detector noise: divided by the detector gain it is a phase error already in ring "
 "radians, so it reaches the output without ×N² (−148.6 dBc/Hz floor, 40 fs). Timing noise of the isolation buffers and "
 "their supply sensitivity shift the moment the ring is looked at, exactly like reference jitter: those are multiplied "
 "by N² in band (−171.6 and −186 dBc/Hz at 50 MHz)."),
]
