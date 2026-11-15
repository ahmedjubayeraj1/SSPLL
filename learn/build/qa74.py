"""Interview questions for roadmap step 74 (VCO redesign)."""
QA74 = [
("Why a ring oscillator and not an LC oscillator for this PLL?",
 "Area and tuning range. An LC tank at 1.6 GHz needs a nH inductor (hundreds of µm on a side in SKY130's thick metal) and "
 "gives a narrow range; a ring is a few hundred µm², tunes over more than ±30 % and is easy to lay out. Its phase noise is "
 "~20 dB worse, which is exactly why this design uses a sub-sampling detector and FFNC: they suppress and cancel ring noise."),
("Why 5 stages and not 4?",
 "A pseudo-differential ring of N stages is two single-ended rings of N inverters coupled by the cross connection. With N = 4 "
 "each half is a 4-inverter ring - a non-inverting loop that can latch (two stable states). The proposal's start-up "
 "simulations latched at tt, ss and ff. With N = 5 each half is an odd ring and cannot latch; the crossing at the end keeps "
 "the differential loop inverting."),
("Why not 3 stages?",
 "The step-6 study: 3 stages run at 2.4 GHz for N = 48 with similar efficiency (VCO FoM within 1 dB) but more absolute "
 "jitter at equal power, push the SSPD, NCB and first divider to 2.4–2.6 GHz, and would have changed the submitted "
 "proposal. 5 stages at 1.6 GHz were kept."),
("What does the always-on transmission gate between the two halves do?",
 "It ties inp to outp (and inm to outm) so the two single-ended rings run in anti-phase: a weak in-phase coupling that "
 "enforces the differential mode. Without it the halves could drift into the common mode. It also adds load and, as the "
 "ISF showed, noise - which is why its nMOS was redesigned."),
("How is the frequency tuned?",
 "Coarse: the CCO current into the ring's supply node (5-bit DAC, step 75) - more current, faster edges. Fine: vtune turns "
 "on switch S, which hangs a MOS capacitor on each output; more vtune means more capacitance and a lower frequency, so "
 "K_VCO is negative (−326 MHz/V average over 0.6–1.2 V). The loop's charge-pump polarity is chosen to match."),
("Why is K_VCO negative and does it matter?",
 "Raising vtune connects more capacitance, slowing the ring. A negative gain is fine as long as the sign of the detector or "
 "the charge pump is flipped so the loop has negative feedback. It must be documented, because a wrong sign makes the "
 "loop run away to a rail instead of locking."),
("What did the ISF reveal about the original cell?",
 "Thermal noise was dominated by the main pMOS (68 %), but 86 % of the flicker up-conversion came from two small devices: "
 "the fine-tune switch (42 %) and the coupling TG nMOS (44 %) - both minimum length (0.15 µm). The main inverter nMOS, "
 "normally blamed for flicker, contributed only 4 %."),
("Why does a tiny switch dominate the flicker?",
 "Flicker noise density scales roughly with 1/(W·L): a 0.15 µm device has a tiny gate area, so its 1/f current is large. "
 "The switch's on-resistance sets how much of the tuning capacitor the output sees; slow fluctuations of that resistance "
 "change the load - that is directly a frequency modulation, i.e. up-converted flicker (the dc part of the ISF)."),
("How was the 1/f³ corner reduced and what did it cost?",
 "The switch and the TG nMOS were drawn at L = 0.3 µm (switch W 2.25 → 4.5 µm to keep W/L; TG nMOS 0.63 → 0.84 µm). "
 "Corner 1.06 → 0.60 MHz (spec ≤ 0.6). The bigger devices add capacitance: 10 % more current for 1.6 GHz (1.225 → 1.352 mA, "
 "corrected values with the PDK .spiceinit). L = 0.5 µm was tried first and cost 21 % of speed - rejected."),
("Why must ngspice load the PDK .spiceinit, and what happened when it did not?",
 "The sky130 model files are written for HSPICE; the PDK's spinit sets ngbehavior=hsa so ngspice reads them the HSPICE "
 "way. The first step-74 runs did not load it: multi-finger devices were read wrongly and the ring ran 4.6 % slow "
 "(1.437 instead of 1.352 mA for 1.6 GHz). Single-finger devices were unaffected, which is why the device noise tables did "
 "not change. Found when the stand-alone testbench decks disagreed with the design scripts; everything was re-run."),
("Why not simply make the main inverters bigger to lower the noise?",
 "Scaling the whole ring by k lowers all noise by 10·log k but costs k× power - the FoM does not change. The ISF showed the "
 "flicker came from two small devices; fixing those costs 9 % power for 2.6 dB lower close-in noise, far better than scaling."),
("What is the 1/f³ corner and why does it matter here?",
 "The offset where up-converted flicker equals thermal phase noise; below it L(f) falls at −30 dB/dec. With the loop at "
 "2.5 MHz, a corner near 1 MHz puts flicker noise right where the loop and FFNC have the least suppression, raising "
 "L(300 kHz) FFNC-off above the −110 dBc/Hz spec."),
("What does h_dc/h_rms (0.67) tell you?",
 "How asymmetric the ISF is: the dc part converts slow (flicker) noise into phase drift. A perfectly symmetric waveform would "
 "have h_dc = 0 and no flicker up-conversion. 0.67 is high - the rising and falling edges and the load of the tuning branch "
 "are not symmetric - so the remaining handle is device area of the noisy devices."),
("Why use LVT devices or not?",
 "pfet_01v8_lvt has a minimum length of 0.35 µm - far too slow for a 1.6 GHz ring. nfet_01v8_lvt would lower the ring-node "
 "voltage for a given frequency (more headroom for the CCO), but the standard-Vt ring already runs at 1.45 V at tt and "
 "within the limit at ss/110 °C; LVT would add leakage and spread. Kept as a fallback, not used."),
("Why is the ring fed by a current and not by a voltage?",
 "A current-fed ring (CCO) has low supply sensitivity - the high output impedance of the current source isolates it from "
 "VDDA noise - and the current directly sets the frequency (K_I ≈ 1.2 GHz/mA). The ring-node voltage settles wherever the "
 "ring needs it to draw that current."),
("Why must the ring-node voltage stay below 1.8 V?",
 "The ring uses 1.8 V core devices (absolute maximum 1.95 V) and the CCO output transistor needs headroom from VDDA "
 "(2.97 V minimum): every 100 mV more on the ring node costs CCO headroom and raises its noise (step 72)."),
("Why does every ring node get a buffer, even unused ones?",
 "Equal loading: each node then has the same capacitance, so all stages have the same delay and the ISF is the same at "
 "every node (the 2N-node assumption of the noise calculation holds). It also makes the layout regular - 10 identical "
 "buffer cells - and any tap can be used later."),
("Why AC-coupled buffers?",
 "The ring's DC level moves with the CCO current (1.1–1.7 V); a buffer biased by the ring's DC would change its trip point "
 "and duty cycle with frequency. The coupling cap removes the DC and the feedback resistor biases the first inverter at its "
 "own trip point, so the buffer output is centred at any ring voltage."),
("How is the frequency measured in simulation and why that way?",
 "Transient with an ideal current feed, a differential kick at t = 0, and .meas of 16–20 zero crossings of vop − vom after "
 "start-up has settled. A ring has no DC operating point that oscillates, so a small-signal analysis cannot give the "
 "frequency; the transient is the simulation equivalent of a frequency counter."),
("How was phase noise computed without Spectre PNOISE?",
 "With the ISF: the charge-injection response h(t) of one node at 12 phases, the bias of every device over a cycle and the "
 "PDK's own thermal and flicker noise tables for each device type and length. L = 2N·⟨h²S_th⟩/(2Δω²) for thermal; "
 "the flicker part uses ⟨h·√B⟩². It tells not only the total but which device causes it."),
("How accurate is the ISF estimate?",
 "The level is about 6 dB pessimistic against ngspice transient noise (step 7), because the ISF with cyclostationary "
 "white noise treats every injection as uncorrelated and the tables use the device's small-signal noise at each instant. "
 "The ranking of devices and the 1/f³ corner are reliable. Spectre PNOISE in the Cadence VM is the cross-check (step 95)."),
("Why use ideal R and C in the buffer for the long characterisation runs?",
 "The PDK poly resistor is a behavioural (voltage-dependent) model and makes the transient about 5× slower. The ideal "
 "replacement uses the PDK values including the resistor's 3 fF end parasitics, and reproduces the PDK-buffer frequency "
 "to 0.001 %; the ISF runs and the LVS use the real PDK devices."),
("What is K_I and how is it used?",
 "df/dI of the current-fed ring (Hz/A). It converts the CCO's output current noise into frequency noise (step 72: "
 "i_n ≤ 7.2 pA/√Hz) and sets the DAC step size in Hz (step 75)."),
("How do you check the schematic is the simulated circuit?",
 "xschem netlists the schematic (LVS format) and netgen compares it with the netlist generated for simulation: all four "
 "levels (cell, buffer, core, VCO) match uniquely. The same flow is used for layout-versus-schematic later."),
("What layout decisions are already in the schematic?",
 "Integer finger counts (pMOS 4 × 3 µm, nMOS 2 × 3 µm) so each cell is one abutting row; the two halves are mirror images; "
 "the 5 cells are identical; the TGs, switches and caps are drawn per half; 10 identical buffers; MIM bottom plate on the "
 "driven ring node, top plate on the high-impedance buffer gate."),
("Why is the MIM bottom plate on the ring node?",
 "The bottom plate (met3) has parasitic capacitance to the substrate. On the strongly driven ring node it only adds a "
 "little load; on the high-impedance buffer gate it would form a divider with the coupling cap and attenuate the signal."),
("Why is the ring supply node decoupled with only 0.5 pF in simulation?",
 "The ring is current-fed: a large decap on its supply node would just be charged by the CCO current (it sets the start-up "
 "time) and filters the ring's own current ripple. Its value is a layout choice (step 109); 0.5 pF keeps start-up fast."),
("How does the frequency change from tt to ss/110 °C, and how is it handled?",
 "Slower devices and higher temperature lower the frequency at a given current; the CCO DAC supplies more current. The "
 "check is that 1.76 GHz is reachable at ss/110 °C with the ring node below the limit, and 1.44 GHz at ff/−40 °C with "
 "the DAC's minimum current."),
("What sets the start-up time?",
 "The CCO charging the supply node and decap, then the growth of the differential mode from noise or mismatch. With 5 "
 "stages the differential mode is the only unstable mode, so it starts in a few ns at all corners."),
("Why 10 fF extra capacitance per node in the simulations?",
 "A pre-layout allowance for wiring; corners use 5 fF (ff/−40 °C, fast case) and 15 fF (ss/110 °C, slow case). Step 118 "
 "replaces it with the extracted values."),
("What is the VCO's contribution to the total jitter after this step?",
 "With the step-74 ring numbers in the step-72 model: 2.04 ps FFNC off, 1.32 ps FFNC on (typ), L(300 kHz) −110.6 / −120.0 "
 "dBc/Hz - all inside the typ specs. Power rises to 9.55 mW typ (spec 'about 9'), FoM −227.8 dB unchanged."),
("If power had to come back to 9.0 mW, where would you take it?",
 "The LDO load reserve (0.33 mW), the dummy-buffer size (8 of 10 buffers only provide equal loading - they can be smaller "
 "inverters with the same input capacitance), and the NCB bias. Not from the ring: its current buys the noise margin."),
]
