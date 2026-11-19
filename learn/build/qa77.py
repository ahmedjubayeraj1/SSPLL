"""Interview questions for roadmap step 77 (clock generator: sampling clocks, hold pulse, Gm pulse)."""
QA77 = [
("What does the clock generator do in this sub-sampling PLL?",
 "From one reference edge (refclk) it makes three complementary control pairs, in a fixed order: cks/cksb for the "
 "sampling switch (it tracks the VCO and opens at the reference edge), ckg/ckgb for the short current pulse of the "
 "pulsed-Gm charge pump, which reads C1 right after the sample, and ckh/ckhb for the hold switch that then shares C1 "
 "onto C2 for the NCB. It is the timing skeleton of the SSPD + charge pump (order revised in step 78)."),
("Why does the sampling happen on the falling edge of cks and not on a rising edge?",
 "While cks = 1 the switch conducts and the sampling capacitor follows the VCO (track). The sample is the voltage at "
 "the moment the switch opens, i.e. when cks falls. The reference's rising edge is the timing reference, so cks must "
 "fall in response to refclk rising: the driver gives cks from the inverted path."),
("Why are there gaps between the three phases?",
 "Two switches must never conduct at the same time, and the Gm must read a settled sample. If the Gm current flowed "
 "while sw1 still tracked the VCO, it would see the VCO instead of the sample; if sw2 shared C1 with C2 while the Gm "
 "current flowed, the current would follow the sharing transient. Gap 1 (cks fall → ckg rise) and gap 2 (ckg fall → "
 "ckh rise) are the non-overlap times: 171 / 318 ps typical, at least 110 ps over all corners (requirement ≥ 100 ps)."),
("How does an RC pulser make a pulse from an edge?",
 "The input and a delayed, inverted copy of it go into a gate (here a NOR of the inverted input and the inverted "
 "delayed input, which is input AND NOT delayed). After a rising edge both conditions are true until the delayed copy "
 "has also switched, so the output is high for one delay: the pulse width is the delay of the R-C stage plus the "
 "gates. A falling edge produces no pulse."),
("What sets the width of the RC pulse?",
 "The RC node charges exponentially and the next inverter switches when it crosses its trip point (about half the "
 "supply), so the RC part is ≈ ln2 · R·C. To it add the delays of the inverters and the NOR. For the hold pulse "
 "RC dominates (R_H ≈ 34 kΩ, C_H ≈ 75 fF → ≈ 1.8 ns of the 2.15 ns); for the 200 ps Gm pulse the gates dominate "
 "(minimum-length resistor)."),
("Why does the Gm pulse width τ matter so much?",
 "The charge pump delivers a charge g_m · v_sample · τ per reference period, so the phase-detector gain is "
 "β = 2A·g_m·τ/T. The loop bandwidth and phase margin depend on β·K_VCO. A τ that varies ±50 % over PVT moves the "
 "bandwidth by ±50 % unless something else compensates."),
("τ varies from 106 to 408 ps over corners. Why is that acceptable?",
 "Because the loop needs β·K_VCO, not τ alone. τ is long when transistors are slow (ss, cold, high R) and the VCO "
 "gain is then small; τ is short in ff where K_VCO is large. The product τ·K_VCO stays within ×0.86–1.21 of nominal "
 "in the worst conditions found. The final check of β·K_VCO with g_m and A is done in step 79."),
("Why not use a high-precision resistor for τ?",
 "A poly resistor's temperature coefficient (xhigh_po −19 % over −40…110 °C) and its process corner (±20 % or more) "
 "add to the gate-delay variation. Making R small and letting the gates set most of τ lets the τ variation track "
 "the ring VCO's transistors, which is the compensation we want. Absolute accuracy would need a trimmed or "
 "locked delay (a DLL), which costs power and area for no system benefit here."),
("What are the SKY130 'combined' corners and why did you use them here?",
 "The PDK has MOS corners (tt, ss, ff, sf, fs) and resistor/capacitor corners. The combined library sections such "
 "as ss_hh (slow MOS, high R, high C) and ff_ll move both together, and hl / lh move R and C the opposite way. A "
 "circuit whose timing is R·C plus gate delay has its extremes there, not at plain ss/ff: τ's worst cases came "
 "from ss_hh (408 ps) and ff_ll (106 ps)."),
("What is t_p and why must it be ≤ 5 ns?",
 "t_p is the delay from the sampling instant to the centre of the Gm current pulse: the loop's transport delay. In "
 "the loop gain it appears as e^{−s·t_p}, i.e. a phase lag ω_c·t_p at the crossover. Step 73 allowed up to 5 ns for "
 "≤ 3° of phase-margin loss. With the Gm right after the sample t_p = 0.28 ns typical and 0.50 ns worst (it was "
 "2.63 ns when the Gm came after the hold pulse)."),
("Why must W_H be at least 1.5 ns?",
 "During the hold pulse the charge on C1 is shared with C2 through sw2. The transfer must settle (several R_on·C time "
 "constants) so that C2, which the NCB reads for the whole next period, holds the final shared value, and some "
 "time is reserved for the switch's own charge injection to die away. 1.5 ns is the requirement; the minimum over "
 "corners is 1.51 ns (ff_ll, 110 °C)."),
("Why does the hold pulse width depend on the reference duty cycle?",
 "The RC node of the hold pulser is reset while its trigger is low, i.e. while refclk is low. With a short low "
 "time (duty 65 %) the node is not fully discharged at the next edge, so it reaches the trip point earlier and the "
 "pulse shrinks (1.98 ns at 65 % vs 2.22 ns at 35 %). It stays above 1.5 ns; a reset nMOS on the RC node would remove "
 "the dependence if needed."),
("How is the clock generator disabled when the PLL is off?",
 "It has no enable pin. When pll_en = 0 the reference buffer holds refclk at 0: cks stays 1 (the sampling switch "
 "tracks), and no hold or Gm pulses are produced, so the charge pump injects no charge and the circuit draws only "
 "leakage."),
("How much power does it use and why so little?",
 "78 µW typical (69–108 µW over corners). It is CMOS logic switching once per reference period: P ≈ C_total·V²·f "
 "with tens of fF per node at 50 MHz. It fits inside the 0.12 mA allocation for the SSPD and clock generator."),
("Why does the jitter of the clock generator matter?",
 "The sampling edge is the PLL's time reference. Any random delay added between refclk and the moment the switch "
 "opens is reference jitter and is multiplied by N = 32 (+30 dB) inside the loop bandwidth, exactly like the "
 "crystal's own noise. The Gm and hold edges do not matter for noise: they act after the sample has been taken."),
("How did you estimate the jitter of an inverter chain in ngspice?",
 "Method M17: .noise on each inverter size biased at its trip point gives the noise current it makes while switching "
 "(2.4–7.2 pA/√Hz). In a transient, every node of the sampling path gets a white trnoise current of that size, with "
 "NA = √(S/(2NT)). 123 edges of a noiseless 500 MHz input give the spread of the output edge times: 0.15 ps rms."),
("Why inject at the trip-point noise level?",
 "A CMOS inverter is quiet when it rests at a rail (one device off, the other in deep triode with no gain). It "
 "contributes to timing only while it passes through the threshold, where both devices conduct with maximum g_m and "
 "the node is high-impedance. Using the trip-point density during the whole run is pessimistic, which is fine for "
 "a budget check."),
("Your first jitter result was 1.17 ps. What was wrong?",
 "Two things. Some output edges were paired with the wrong input edge, and the simulator's time grid made the edge "
 "times drift slowly by about 1.2 ps over the run. A run with all noise scaled by 10⁻⁶ showed the same 1.2 ps, so it "
 "was numerical. Pairing each output edge within 0.6 ns of its input edge and removing a 4th-order trend gave "
 "0.15 ps, with a noiseless baseline of 0.0002 ps."),
("How do you turn 0.15 ps of per-edge jitter into phase noise?",
 "Independent jitter on each 50 MHz edge is a white phase-noise floor L = (2π·f_ref·σ)²/f_ref = (2π·5×10⁷·1.5×10⁻¹³)² "
 "/ 5×10⁷ = 4.4×10⁻¹⁷ → −163.4 dBc/Hz. The step-72 allocation was −160 dBc/Hz, so there is 3.4 dB of margin."),
("Why are the output drivers bigger than the rest of the logic?",
 "They drive the switch gates (30 / 20 fF) with sharp edges. A slow edge on the sampling switch makes the sampling "
 "instant depend on the signal level (the switch turns off when V_GS crosses V_T, which depends on the sampled "
 "voltage) and makes the edge more sensitive to noise. 4 / 8 µm output stages give 76 ps rise times."),
("Why are cks and cksb generated by paths of 2 and 3 inverters, and is the skew a problem?",
 "One output needs the inverted signal, so its path has one more stage. The extra stage gives about 12 ps skew. For "
 "a complementary transmission gate, a small skew only changes which device turns off last; the sampling instant is "
 "set by the last one to turn off, and it is the same every period, so it adds no jitter and only a fixed delay."),
("Which requirements does step 77 hand on to later steps?",
 "Loads ≤ 30 fF on cks/cksb and ≤ 20 fF on the others (switch sizes in steps 78/79); the Gm switch must handle pulses "
 "as short as 106 ps; β·K_VCO must be checked over corners with the real g_m and A (step 79); the layout must keep "
 "the sampling path short and symmetric (parasitic delay adds to t_p and to jitter)."),
("Why was the order of the Gm and hold pulses changed in step 78?",
 "Charge sharing makes C2 a memory: v2[k] = (C1 v1[k] + C2 v2[k−1])/(C1 + C2), a first-order low-pass with a pole at "
 "z = C2/(C1 + C2) = 0.5. If the Gm read C2 (or C1 after the sharing), that pole would sit inside the PLL loop and cost "
 "about 16° of phase margin at f_c = f_ref/20; step 73 did not include it. Reading C1 before the sharing gives the Gm "
 "the fresh sample; the NCB, which reads C2, keeps the pole that the FFNC model already contains."),
("Why does the hold pulser need a latch as its trigger?",
 "The hold pulser's RC node (R_H·C_H ≈ 2.6 ns) is reset only while its input is low. Triggered directly by the end of "
 "the 200 ps Gm pulse, its input would be low for only 200 ps and the pulser would never fire. The latch is set by ckg "
 "and reset while refclk is low (cks = 1); its output q·NOT(ckg) rises when the Gm pulse ends and stays high until "
 "refclk falls, so the RC node gets ~10 ns to reset every period."),
("How would you check this block in Cadence?",
 "Same testbench: an ideal 50 MHz pulse on refclk, capacitive loads, tran with the Calculator's cross() and delay() "
 "for the edges, Corners setup with the combined MOS+R/C sections. Jitter by Spectre transient noise (noisefmax "
 "≈ 500 GHz) or, better, pss + pnoise with sampled (jitter) output at the cks crossing."),
("What would you change if τ had to be accurate to ±10 %?",
 "Replace the RC pulser by a delay that is locked to the reference: e.g. a current-starved delay biased from a "
 "replica delay line in a DLL, or trim the R with a few switched segments after measurement. Both cost area and "
 "power; with this loop the natural τ·K_VCO compensation makes them unnecessary."),
("Why are all the devices thin-oxide 1.8 V transistors at minimum length?",
 "The block runs from VDDL = 1.8 V and has to be fast: minimum L gives the smallest gate capacitance and delay, and "
 "the power is dominated by switching, not leakage. Matching is not important here because the absolute delays are "
 "re-referenced every period and only their noise matters."),
]

# Step 77 redo for the device-rule migration: 1.8 V clock generator on VDDD + level shifters + 5 V outputs
# (docs/design/step77_hv_clkgen.md)
QA77HV = [
("Why does the clock generator stay in 1.8 V logic when its outputs must swing 0–3.3 V?",
 "The timing core — buffers, gap inverters, RC edge generators and the hold latch — is fastest, smallest and least "
 "power-hungry in thin-oxide 1.8 V devices, and the reference receiver already delivers a 1.8 V edge on VDDD. Only "
 "the switch gates of the SSPD and the Gm (5 V devices on VDDA) need 3.3 V. So the logic stays at 1.8 V and level "
 "shifters plus 5 V drivers sit only at the outputs."),
("Why can't a short pulse simply be passed through one level shifter?",
 "A cross-coupled level shifter is asymmetric: its output rises when the input nMOS pulls one latch node down (fast), "
 "but falls only after the latch flips back through the weak pMOS (slow). The difference — a few hundred ps at the "
 "slow corner — is subtracted from the pulse width, and a few-hundred-ps pulse shrinks or disappears."),
("What is edge-pair level shifting?",
 "Each pulse is sent across as two rising steps, start and stop, through two identical level shifters and two "
 "identical step drivers; both edges see the same (fast) delay. The pulse is formed only at the 5 V output gates: "
 "ckg = NOR(NOT start, stop), ckgb = NAND(start, NOT stop). The steps fall when refclk falls, where nothing is timed."),
("Why does a narrow pulse not survive a 5 V buffer chain, and how was that found?",
 "Thick-oxide gates have 100–200 ps edges with realistic loads. A pulse not much longer than rise + fall never reaches "
 "full swing at the next stage and is filtered away. It showed as an output that never crossed 90 % of VDDA in the "
 "timing bench; at ff_ll / 110 °C even the final 210 ps pulse reached only 84 % of the rail."),
("Why was the Gm pulse lengthened from 200 ps to about 530 ps, and what does it cost?",
 "So that it reaches full swing at every corner with 5 V output gates (≥ 322 ps at ff_ll / 110 °C). The loop only sees "
 "β = 2A·g_m·τ/T, so step 79 lowers g_m by the same factor; the pulsed-Gm noise, which goes as 1/(g_m·τ), is "
 "unchanged. The loop delay t_p (sample → middle of the Gm pulse) grows to about 0.9 ns, still far below the 5 ns limit; "
 "at f_c = 2.5 MHz the extra 0.38 ns costs 0.34° of phase margin (0.85° at the slowest corner)."),
("Why is τ allowed to vary 3× over the corners?",
 "Because the loop gain is β·K_VCO and τ is set mainly by gate delays: slow devices make τ longer exactly where the "
 "thick-oxide ring has a lower K_VCO. The product τ·K_VCO stays within ×0.89–1.14 of nominal (ff_ll −40 °C to ss_hh 110 °C)."),
("How are cks and cksb made to switch together?",
 "The driver's inverted output goes through three inverters, the in-phase output through two plus an always-on "
 "transmission gate whose RC delay replaces the missing inverter. Its width sets the skew: 1.5 µm gives −11 ps at tt."),
("Why does the sampling edge no longer pass through refclk and a level shifter?",
 "Measured with M21, the edge that went REF_IN → receiver → refclk (VDDD) → two VDDD inverters → level shifter → 5 V "
 "driver moved by 376 ps per volt of VDDD: the receiver's VDDD gates gave 157 ps/V and the level shifter, whose input "
 "nMOS is driven with VDDD's level, most of the rest. VDDD would have had to be quieter than about 70 nV/√Hz. The "
 "receiver already has the edge at 3.3 V (S2's output on VDDA), so it is brought out as refhv and drives the 5 V "
 "sampling driver directly: no VDDD gate is left in the sampling path. The Gm and hold pulses still come from refclk; "
 "their timing acts on a sample that is already held, so their jitter does not matter. Result: 2.1 ps/V of VDDD (was 376); VDDA gives 148–175 ps/V, a −169.7 dBc/Hz term at 100 nV/√Hz."),
("Why does the clock generator now cost about 0.7 mW instead of 0.08 mW?",
 "Its outputs and their drivers switch 3.3 V instead of 1.8 V (3.4× the energy per unit capacitance), the thick-oxide "
 "gates are larger for the same speed, and four level shifters add contention current. Most of it is the two pulse "
 "outputs (≈ 0.15 mW each), the sampling driver (≈ 0.16 mW) and the level shifters (≈ 33 µW each). It is 0.31 mW over its 0.41 mW allocation; with the receiver (+0.03) and the CCO (−0.18) the total is 9.29 mW, inside the proposal's 'about 9 mW' (maximum 15 mW)."),
("Why must gap 2 be at least 100 ps, and what fixed it?",
 "Gap 2 separates the end of the Gm pulse from the start of the hold transfer: the Gm must have finished reading C1 "
 "before C1 shares its charge with C2. With two gap inverters it fell to 79 ps at the fs corner; four inverters give "
 "≥ 100 ps everywhere."),
]
