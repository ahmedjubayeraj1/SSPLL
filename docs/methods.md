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
