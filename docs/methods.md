# Measurement and analysis methods

Generated from `design/log/log_data.py` (also in `design/SSPLL_design_log.xlsx`, sheet Methods). For every method: what it gives, why this method was chosen, how it works, how to run it yourself, and its limits.

## M1. Transient frequency and ring-node measurement (step 74)

**What it gives.** Oscillation frequency f, ring supply-node voltage, differential swing for a given feed current, vtune, corner

**Why this method.** A ring oscillator has no small-signal operating point to analyse (it is a large-signal limit cycle); only a transient shows the real frequency. It is the direct equivalent of measuring with a frequency counter.

**How it works.** The ring is started with a small differential kick (initial condition) and fed by an ideal current source. After start-up settles (12 cycles), the time of 20 rising zero crossings of v(vop)-v(vom) is measured with .meas; f = 20 / (t32 - t12). The average and maximum of the supply node over the same window give the ring voltage.

**How to run it.** `design/vco/vco.py: vco.run(vco.netlist(p, I=..., corner=..., temp=..., vtune=...)); xschem: tb_vco_tran`

**Limits.** Time step 2 ps; f accurate to ~0.1 %. Needs a start-up kick; a symmetric netlist can stay in a metastable state.

## M2. ISF phase-noise extraction with the models' own noise (step 72, 74)

**What it gives.** Free-running phase noise L(1 MHz), thermal and flicker parts, the 1/f^3 corner, and each device's share

**Why this method.** ngspice has no PSS/PNOISE (Spectre's periodic noise). The impulse sensitivity function (Hajimiri-Lee) converts any noise current at a node into phase noise and shows *which device* causes it - the information needed to fix it.

**How it works.** 1) reference run: period T and the bias (Vgs, Vds) of every device on node p1 over one cycle; 2) inject +q and -q (2 fC, 1 ps) at 12 points of the cycle and measure the permanent shift of a zero crossing 30 cycles later: h(t) = dphi/dq; 3) each device's thermal S_th and flicker B (A^2) from .noise tables of a W = 1 um device over a Vgs x Vds grid, scaled by W; 4) thermal L = 2N<h^2 S_th>/(2 dw^2); flicker up-conversion uses the dc part of h: L_fl = 2N <h sqrt(B)>^2/f/(2 dw^2); corner f_c3 where they are equal.

**How to run it.** `design/vco/step74_point.py NAME (variant), uses vco.isf_noise(); tables cached in design/vco/data/noisegrid_*.npz`

**Limits.** About 6 dB pessimistic in absolute level against transient noise (step 7); the corner and the device ranking are reliable. Spectre PNOISE in the Cadence VM is the cross-check.

## M3. Device noise tables (.noise) (step 72, 74)

**What it gives.** Channel thermal noise density and the 1/f coefficient of one device type and length vs bias

**Why this method.** Gives the models' own noise (gamma, flicker parameters of the PDK) instead of textbook gamma = 2/3 or 1.

**How it works.** For each (Vgs, Vds) point: .noise of the drain current (through a CCVS) from 1 kHz to 1 GHz; B = S(1 kHz) x 1 kHz; S_th = S(1 GHz) - B/1 GHz.

**How to run it.** `vco.noise_table(model, L)`

**Limits.** One table per (model, L); 100 bias points; tt, 27 C.

## M4. Schematic-vs-simulation LVS (netgen) (step 74)

**What it gives.** Proof that the drawn xschem schematic is exactly the circuit that was simulated (devices, sizes, connections)

**Why this method.** Schematics drawn by hand (or generated) and netlists used in simulation can drift apart; netgen compares them topologically, like the layout LVS later.

**How it works.** xschem netlists the schematic in LVS format (top level as .subckt); netgen compares it with the hierarchical reference written from the simulated netlist (vco.lvs_reference) using the PDK's netgen setup file.

**How to run it.** `xschem/lvs.sh xschem/vco/<cell>.sch xschem/netlist/ref_vco.spice <cell>`

**Limits.** Exact; result 'Circuits match uniquely'.

## M5. Schematic drawing checks (step 74)

**What it gives.** No overlapping wires of different nets, no wire through a pin, no floating pin, no text over text or wires

**Why this method.** Readable schematics are a project rule; an automatic check stops a messy drawing before it is committed.

**How it works.** tools/xsch.py builds the schematic geometrically, then checks segment overlaps, pin-on-wire, unwired pins and text boxes; xschem/render.sh draws a PNG for a visual check.

**How to run it.** `python3 design/vco/schematics.py`

**Limits.** Text boxes approximate.

## M6. Small-signal C-V (AC) (step 73)

**What it gives.** Capacitance of the MOS capacitor and MIM tiles vs bias, corner and temperature

**Why this method.** A MOS capacitor's value depends on its gate voltage; only an AC analysis at each DC bias shows it.

**How it works.** DC bias on the gate plus an AC source; C = Im(I)/(2 pi f) at 1 MHz; swept over 0-1.8 V, tt/ss/ff, -40/27/110 C.

**How to run it.** `design/loop/spice/run_cv.sh`

**Limits.** Exact for the model; layout parasitics come later.

## M7. R/C corner and temperature runs (step 73)

**What it gives.** Resistor and MIM values over the ll/hh/hl/lh sections and temperature

**Why this method.** In SKY130 the tt/ss/ff corners do not move R or C; their spread is in separate sections.

**How it works.** AC current of a 1 V source across the device -> R = 1/Re(I), C = Im(I)/(2 pi f).

**How to run it.** `design/loop/spice/run_rc.sh`

**Limits.** -

## M8. Exact sampled-data loop analysis (step 73)

**What it gives.** Phase margin, crossover, closed-loop peaking and step response of the SSPLL including sampling and packet delay

**Why this method.** The SSPD samples once per period and the Gm acts after a delay; a continuous model overestimates the phase margin.

**How it works.** Filter + VCO state propagated over one period with the matrix exponential; L(z) on the unit circle gives margins.

**How to run it.** `design/loop/sampled_loop.py; step73_loop.py`

**Limits.** Linear (small phase errors).

## M9. Phase-domain jitter budget (step 72, 73)

**What it gives.** Output phase-noise spectrum and rms jitter per block, FFNC on and off

**Why this method.** Combines every block's noise through its own transfer function; shows which allocation matters.

**How it works.** S_out = sum S_i |T_i|^2 with H, 1-H, the cancellation path G_c and aliasing; jitter = sqrt(int S df)/(2 pi f0).

**How to run it.** `design/budget/step72_budget.py`

**Limits.** Uses allocations until block results replace them.

## M10. DC operating point and compliance sweep (step 75)

**What it gives.** Output current of a current source for each code / corner / supply / bias, and its dependence on the output voltage

**Why this method.** A current source is a DC circuit: its job is a current at a voltage. An operating point per condition is exact (no approximation) and cheap, so all 90 corner combinations plus a full code sweep fit in minutes.

**How it works.** The ring node is replaced by an ideal voltage source at the typical ring voltage (1.45 V); its current (vr#branch) is the CCO output. For compliance, the source is swept 0-2.4 V (.dc) at the least-headroom corner (VDDA 2.97 V, ss/110 C, max code): the current must stay flat over the ring's range (1.38-1.8 V).

**How to run it.** `design/cco/step75_sim.py (sections A, B); xschem: tb_cco_dc`

**Limits.** Ignores the ring's own I-V (load line); M12 closes that gap. Exact for the models used.

## M11. Output-current noise (.noise) and supply rejection (.ac) (step 75)

**What it gives.** Output current noise spectrum (A/rtHz) of the complete circuit incl. PDK resistors and MIM caps; |dI/dVDDA| vs frequency

**Why this method.** Noise of a biased analog block is small-signal: .noise linearises every device at its operating point and adds their noise (thermal, flicker, resistor) through the exact transfer functions - faster and more accurate than a transient noise run. The same linearisation with an ac 1 V source on VDDA gives supply rejection.

**How it works.** The ring node is an ideal source at 1.45 V through a 0 V ammeter; a CCVS (h1, 1 V/A) converts its current into a voltage 'o' so .noise reports A/rtHz. option sparse is needed (KLU fails on .noise). The spectrum feeds the budget (M9): S_f = K_I^2 S_i, shaped by |(1-Gc)(1-H)|^2, gives the CCO jitter and L(300 kHz).

**How to run it.** `design/cco/step75_noise.py, step75_sim.py (section D); xschem: tb_cco_ac`

**Limits.** Linear around the operating point; tt only (corners shift g_m by +/-15 %).

## M12. Clamp check with the ring's measured I-V (load-line method) (step 75)

**What it gives.** The ring-node voltage reached for each code when the CCO drives the real ring at the worst corner

**Why this method.** The ring node is set by where the CCO output (a current source) meets the ring's I-V curve and the clamp. Simulating the whole ring for every code would take hours; a behavioural model of its I-V gives the same DC intersection in seconds.

**How it works.** The ring's average I-V at ss/110 C, 10 fF/node (from step-74 transients, M1) is a pwl B-source current I_ring(V). The CCO plus clamp drive it at VDDA 3.63 V with IBIAS 4 and 6 uA; the .op solution is the ring node.

**How to run it.** `design/cco/clamp_ring.py`

**Limits.** The ring's average current replaces its switching current; good for DC, not for ripple.

## M13. Level-shifter transient at the hardest supply corners (step 75)

**What it gives.** Whether the 1.8 -> 3.3 V shifter switches, its output levels and edge times

**Why this method.** A cross-coupled level shifter is a ratioed latch: it only flips if the nMOS pull-downs (driven from the low supply) win against the pMOS loads (on the high supply). The worst case is lowest VDDD with highest VDDA, slow and fast corners - a transient shows directly whether it flips.

**How it works.** Pulse on 'in' (0-1.71 V), VDDA 3.63 V, 20 fF loads; .meas rise/fall at VDDA/2 and the high/low levels; ss/110 C and ff/-40 C.

**How to run it.** `design/cco/step75_sim.py (section E)`

**Limits.** Static control bits: speed hardly matters, only correct switching.

## M14. Crossing-point noise analysis (.noise at the self-bias point) (step 76)

**What it gives.** Gate-referred noise spectrum of a threshold circuit at the instant of its crossing, incl. flicker and bias-resistor noise

**Why this method.** A self-biased inverter rests exactly at its trip point, i.e. at the operating point it passes through at every crossing. A small-signal .noise there is exact for the slow (quasi-static) noise that shifts the crossing, and it shows which device or resistor dominates. It is fast enough to be used for sizing.

**How it works.** Output noise of S1 (.noise, source = the pad generator through 50 ohm) divided by the gain |v(s1)/v(vin)| gives the gate-referred PSD. Jitter PSD = S_gate/s_gate^2 with s_gate = pi f V_pp |v(vin)/v(pad)| at 50 MHz; L(f) = (2 pi f_ref)^2 S_t(f)/2 for f << f_ref.

**How to run it.** `design/refbuf/refbuf.py: input_noise(); step76_noise.py`

**Limits.** Valid for slow noise only; the white, fast noise of a switching comparator needs M15.

## M15. Transient-noise jitter (trnoise injection, edge-time statistics) (step 76)

**What it gives.** Per-edge jitter and its spectrum for the real, non-linear switching of the receiver

**Why this method.** In a high-gain comparator the small-signal gain at DC (~190) is not the gain that applies while the input sweeps through the threshold (~30), so 'integrated output noise / output slope' is wrong by about 2x. Simulating the switching with noise present measures the jitter directly.

**How it works.** The white plateau of the M14 noise, referred to the pad, is injected as a trnoise voltage (time step 10 ps, i.e. 50 GHz bandwidth) in series with the 50 ohm source of a noiseless circuit. 300 refclk rising-edge times are interpolated; a 4th-order polynomial removes the deterministic settling of the AC-coupling bias; the rms deviation is the per-edge jitter (period jitter / sqrt 2 agrees, so the jitter is white). L_floor = (2 pi f sigma)^2 / f.

**How to run it.** `design/refbuf/tn_run.py (refbuf.tnoise, edge_stats)`

**Limits.** Noise sources stationary at their crossing-point level; 300 edges give sigma to about +/-4 %; ~10 min per run.

## M16. Large-signal transient: delay, duty, edge rate, supply current, supply sensitivity, start-up (step 76)

**What it gives.** Delay pad->out, duty, 10-90 % rise time, average supply currents over corners, amplitudes, frequencies and supplies; edge-time sensitivity to VDDA / VDDL; start-up after enable; the disabled state

**Why this method.** These are large-signal properties of a switching circuit; only a transient shows them. A finite difference of two transients (supply +10 mV) gives the supply sensitivity of the edge time directly in ps/mV.

**How it works.** Sine (or square) source at the pad through 50 ohm; 14 cycles, the last 5 evaluated in numpy from the waveforms (interpolated crossings). Start-up: pll_en steps at 0.5 us, 25 us run, first edge after which all periods are within 2 % of 1/f.

**How to run it.** `design/refbuf/step76_sim.py; xschem: tb_refin (to be drawn in phase 8)`

**Limits.** Drawn netlist with PDK resistors and MIM capacitors; no layout parasitics yet.

## M17. Transient-noise jitter of a logic path with per-node noise currents (step 77)

**What it gives.** rms jitter added by a chain of CMOS gates to an edge (the sampling edge cks), and its phase-noise floor at f_ref

**Why this method.** ngspice has no device noise in transient; a gate is noisy only while it switches (around its trip point), so a white current of the trip-point density at every node gives a simple, slightly pessimistic estimate

**How it works.** .noise on each inverter size at V_M -> S_i; flat netlist with trnoise(NA 1p 0 0) at every node, NA = sqrt(S_i/(2 NT)); noiseless 500 MHz input, 120+ edges, edges paired within 0.6 ns, 4th-order detrend; baseline with NA x 1e-6

**How to run it.** `ONLY_JITTER=1 design/clkgen/step77_sim.py; tb/clkgen/tb_clkgen_jitter.spice + tb/edges.py --fall --col 3`

**Limits.** white only; trip-point density during the whole run is pessimistic; 120 edges -> +-7 %; cross-check: Spectre transient noise or pss + pnoise

## M18. Beat-frequency characteristic of a sampling phase detector (step 78)

**What it gives.** the sampled characteristic v1(phi) over a whole VCO cycle, the detector gain A at the lock point, the hold memory alpha, the sample common mode and the power, in one transient

**Why this method.** a phase sweep would need one run per phase; with the VCO at (32 + 1/nb) f_ref the sampling phase slides by 2 pi/nb each reference period, so nb + 2 periods cover the characteristic with the real clock generator and switches

**How it works.** VCO = ideal squares behind an acbuf-like inverter, starting at t = 0; each cks falling edge is a sample with phase 2 pi f_vco t mod 2 pi; v1 read mid-Gm-pulse, v2 after the hold; line fit within +-0.35 rad of the rising zero crossing (taken modulo 2 pi) gives 2A; least squares v2[k] = a v1[k] + b v2[k-1] gives alpha = b

**How to run it.** `design/sspd/sspd.py characteristic(), step78_sim.py; tb/sspd/tb_sspd_char.spice + tb/sspd_char.py`

**Limits.** 32 points per cycle (+-0.1 rad resolution); the ideal VCO has no noise; the Gm and NCB inputs are capacitor placeholders until steps 79/82

## M19. Kick-back by differential transient (switching vs not switching) (step 78)

**What it gives.** the disturbance the sampler puts on the VCO output: clkp edge shift, a reference-spur estimate, the voltage glitch, and the supply-current component at f_ref (with and without the dummy sampler)

**Why this method.** the effect is femtoseconds, far below any absolute accuracy of a transient; the difference of two runs on the same time grid that differ only in the switching cancels everything else

**How it works.** locked frequency 32 f_ref, VCO phase near the lock point; run a: clock generator on; run b: refclk = 0 (sampler tracks); clkp edge times a - b -> phase 2 pi f0 dt -> Fourier component at f_ref -> 20 log(a1/2) dBc

**How to run it.** `design/sspd/sspd.py kick(), step78_extra.py; tb/sspd/tb_sspd_kick.spice + tb/sspd_kick.py`

**Limits.** VCO output modelled by an ideal source behind a driver (the ring and acbuf would attenuate it further); one operating point

## M20. Device noise at fixed g_m/I_D (ngspice .noise on one transistor) (step 72-HV)

**What it gives.** thermal-noise factor gamma = S_id/(4kT g_m), the 1/f corner frequency and the gate-referred flicker voltage of each device type and length, at the same operating point

**Why this method.** a fair comparison of device families must hold g_m/I_D and the current fixed - then the width follows from the current density, and every difference left is the device's own noise

**How it works.** one dc sweep of V_GS on a 10 um device -> g_m/I_D = d ln I_D / dV_GS; pick V_GS where it equals 10 (searching past the leakage region); scale W to 100 uA (split into fingers <= 40 um); .noise from 100 Hz to 1 GHz with the drain current read through a CCVS; gamma from the 1 GHz value, corner where the PSD is twice the thermal floor

**How to run it.** `python3 design/feas/hv_noise.py -> design/feas/hv_noise.json`

**Limits.** tt, 27 C, one V_DS; SKY130 flicker parameters are binned by length, so the corner must be measured per L used

## M21. Supply-to-edge sensitivity by differential sinusoidal supply modulation (step 76-HV)

**What it gives.** |dt_edge/dV_supply| (s/V) of a clock path as a function of the ripple frequency, for each supply separately; with the supply noise density it gives the path's supply-induced phase noise L(f) = (2 pi f_ref)^2 K(f)^2 S_v(f)/2

**Why this method.** without an LDO every supply ripple that moves an edge is reference noise (x N^2 in band); a DC step misses the frequency dependence of AC-coupled / self-biased circuits and of decoupled bias nodes, and a single run with a fit confuses the start-up drift of slow bias loops with the ripple

**How it works.** two transients from the same operating point: rail = V0 + 10 mV sin(2 pi f_m (t - t_set)) and rail = V0; the edge times are read where the output crosses the receiving gate's threshold (VDDD/2 for a VDDD gate, fixed for VDDA); the edge-by-edge difference is fitted to offset + sinusoid at f_m (least squares); f_m = 0.3, 1, 5, 20 MHz < f_ref/2; a +10 mV DC step at settled bias gives the low-frequency point

**How to run it.** `python3 design/refbuf/step76hv_supply.py --diff -> design/refbuf/data/step76hv_supply.json`

**Limits.** small-signal (10 mV), tt only; 2-3 ripple periods per point (+-5 %); edges sample the ripple at f_ref, so f_m must stay below f_ref/2

## M22. Whole-detector beat run: SSPD + pulsed Gm + clock generator, charge per period vs phase (step 79)

**What it gives.** effective detector gain beta_eff (A/rad) at the lock point, the lock point itself and the charge-phase characteristic

**Why this method.** a pulsed block tested with DC inputs hides any internal node that needs time to settle: with the real SSPD, v1 tracks the 800 MHz ring for half of every period, and the Gm must recover before it is read

**How it works.** ring at (16 + 1/32) f_ref (beat), real clock generator, real Gm on v1, vctl an ideal source; per period the integral of i(vvc) and the ring phase at the sample; cubic fit of charge vs phase within +-0.6 rad of the v1 zero crossing; slope at the charge's zero / T = beta_eff, the zero = lock point

**How to run it.** `python3 design/sscp/step79hv_det.py -> design/sscp/data/step79hv_det.json`

**Limits.** 32 points per ring cycle: the local slope comes from a fit; one run per corner (about 25 min)

## M23. Merged-ground netlist comparison (proof that a net split changed nothing that was simulated) (step 79b)

**What it gives.** IDENTICAL / DIFFERENT per netlist, the instance node counts and a domain audit (which device sits on which ground)

**Why this method.** every pre-layout bench ties both grounds to 0 V, so the split circuit is the simulated circuit exactly when merging the two nets gives back the old netlist; a text proof is exact and takes seconds, a re-simulation proves nothing more

**How it works.** snapshot the old netlists; build the new ones; rename VSSA, VSSD -> VSS, merge the adjacent 'VSSA VSSD' port pair of each mixed cell and the matching node pair of every instance, replace port names by positions, drop comments; compare line by line. Then count the nodes of every sspll_ instance in the design scripts against the port count

**How to run it.** `python3 tools/ground_split_check.py snap DIR (before) / check DIR (after); python3 tools/lvs_hv_all.py`

**Limits.** covers netlists built without running ngspice (references and the cco / refbuf / sspd / sscp benches); inline benches in step scripts are covered by the node-count check and by their VSSA / VSSD sources being 0 V
