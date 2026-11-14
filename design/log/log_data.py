"""log_data.py - single source of the project log. build_log.py turns it into design/SSPLL_design_log.xlsx and
docs/methods.md. Add a row here whenever a step adds a method, a device, a problem or a result."""

STEPS = [  # step, title, status, deliverable (file), key result
 (7, "Cadence correlation (Spectre vs ngspice) over PVT", "scripts ready, VM runs pending", "correlation/STEP7.md",
  "Spectre = ngspice at tt on the frozen models; kit models put the LF branch +41 % off"),
 (8, "Architecture decision", "done", "docs/architecture_decision.md", "SSPLL + FFNC on silicon, Type-II simulation-only, CCO + new LDO"),
 (9, "Python environment + PLL phase-domain model", "done", "models/pllmodel", "TYP 2.29/1.40 ps, PESS 3.71/2.25 ps (FFNC off/on)"),
 (10, "Documentation skeleton", "done", "docs/book", "20 chapter outlines, mkdocs"),
 ("11-71", "Theory notebooks, phases 1-6", "done", "learn/*.ipynb", "580 interview questions, What/How/Why for 61 steps"),
 (72, "Noise, power, area budget per block", "done", "docs/design/step72_budget.md",
  "1.36 ps typ / 1.73 pess (FFNC on); 9.08 mW; 0.058 mm2; ring f_c3 <= 0.6 MHz, CCO flicker corner <= 0.3 MHz"),
 (73, "Loop parameters (design sheet)", "done", "docs/design/step73_loop.md",
  "f_c 2.5 MHz, PM 50 deg (sampled); R1 11.01 k, C1 17.11 p, C2 2.205 p; beta 0.848 uA/rad"),
 (74, "VCO redesign", "in progress", "docs/design/step74_vco.md", "see Results"),
]

METHODS = [  # id, name, step, what it gives, why this method, how it works, how to run it, limits / accuracy
 ("M1", "Transient frequency and ring-node measurement", "74",
  "Oscillation frequency f, ring supply-node voltage, differential swing for a given feed current, vtune, corner",
  "A ring oscillator has no small-signal operating point to analyse (it is a large-signal limit cycle); only a "
  "transient shows the real frequency. It is the direct equivalent of measuring with a frequency counter.",
  "The ring is started with a small differential kick (initial condition) and fed by an ideal current source. After "
  "start-up settles (12 cycles), the time of 20 rising zero crossings of v(vop)-v(vom) is measured with .meas; "
  "f = 20 / (t32 - t12). The average and maximum of the supply node over the same window give the ring voltage.",
  "design/vco/vco.py: vco.run(vco.netlist(p, I=..., corner=..., temp=..., vtune=...)); xschem: tb_vco_tran",
  "Time step 2 ps; f accurate to ~0.1 %. Needs a start-up kick; a symmetric netlist can stay in a metastable state."),
 ("M2", "ISF phase-noise extraction with the models' own noise", "72, 74",
  "Free-running phase noise L(1 MHz), thermal and flicker parts, the 1/f^3 corner, and each device's share",
  "ngspice has no PSS/PNOISE (Spectre's periodic noise). The impulse sensitivity function (Hajimiri-Lee) converts any "
  "noise current at a node into phase noise and shows *which device* causes it - the information needed to fix it.",
  "1) reference run: period T and the bias (Vgs, Vds) of every device on node p1 over one cycle; 2) inject +q and -q "
  "(2 fC, 1 ps) at 12 points of the cycle and measure the permanent shift of a zero crossing 30 cycles later: "
  "h(t) = dphi/dq; 3) each device's thermal S_th and flicker B (A^2) from .noise tables of a W = 1 um device over a "
  "Vgs x Vds grid, scaled by W; 4) thermal L = 2N<h^2 S_th>/(2 dw^2); flicker up-conversion uses the dc part of h: "
  "L_fl = 2N <h sqrt(B)>^2/f/(2 dw^2); corner f_c3 where they are equal.",
  "design/vco/step74_point.py NAME (variant), uses vco.isf_noise(); tables cached in design/vco/data/noisegrid_*.npz",
  "About 6 dB pessimistic in absolute level against transient noise (step 7); the corner and the device ranking are "
  "reliable. Spectre PNOISE in the Cadence VM is the cross-check."),
 ("M3", "Device noise tables (.noise)", "72, 74",
  "Channel thermal noise density and the 1/f coefficient of one device type and length vs bias",
  "Gives the models' own noise (gamma, flicker parameters of the PDK) instead of textbook gamma = 2/3 or 1.",
  "For each (Vgs, Vds) point: .noise of the drain current (through a CCVS) from 1 kHz to 1 GHz; B = S(1 kHz) x 1 kHz; "
  "S_th = S(1 GHz) - B/1 GHz.", "vco.noise_table(model, L)", "One table per (model, L); 100 bias points; tt, 27 C."),
 ("M4", "Schematic-vs-simulation LVS (netgen)", "74",
  "Proof that the drawn xschem schematic is exactly the circuit that was simulated (devices, sizes, connections)",
  "Schematics drawn by hand (or generated) and netlists used in simulation can drift apart; netgen compares them "
  "topologically, like the layout LVS later.",
  "xschem netlists the schematic in LVS format (top level as .subckt); netgen compares it with the hierarchical "
  "reference written from the simulated netlist (vco.lvs_reference) using the PDK's netgen setup file.",
  "xschem/lvs.sh xschem/vco/<cell>.sch xschem/netlist/ref_vco.spice <cell>", "Exact; result 'Circuits match uniquely'."),
 ("M5", "Schematic drawing checks", "74",
  "No overlapping wires of different nets, no wire through a pin, no floating pin, no text over text or wires",
  "Readable schematics are a project rule; an automatic check stops a messy drawing before it is committed.",
  "tools/xsch.py builds the schematic geometrically, then checks segment overlaps, pin-on-wire, unwired pins and text "
  "boxes; xschem/render.sh draws a PNG for a visual check.", "python3 design/vco/schematics.py", "Text boxes approximate."),
 ("M6", "Small-signal C-V (AC)", "73",
  "Capacitance of the MOS capacitor and MIM tiles vs bias, corner and temperature",
  "A MOS capacitor's value depends on its gate voltage; only an AC analysis at each DC bias shows it.",
  "DC bias on the gate plus an AC source; C = Im(I)/(2 pi f) at 1 MHz; swept over 0-1.8 V, tt/ss/ff, -40/27/110 C.",
  "design/loop/spice/run_cv.sh", "Exact for the model; layout parasitics come later."),
 ("M7", "R/C corner and temperature runs", "73",
  "Resistor and MIM values over the ll/hh/hl/lh sections and temperature",
  "In SKY130 the tt/ss/ff corners do not move R or C; their spread is in separate sections.",
  "AC current of a 1 V source across the device -> R = 1/Re(I), C = Im(I)/(2 pi f).", "design/loop/spice/run_rc.sh", ""),
 ("M8", "Exact sampled-data loop analysis", "73",
  "Phase margin, crossover, closed-loop peaking and step response of the SSPLL including sampling and packet delay",
  "The SSPD samples once per period and the Gm acts after a delay; a continuous model overestimates the phase margin.",
  "Filter + VCO state propagated over one period with the matrix exponential; L(z) on the unit circle gives margins.",
  "design/loop/sampled_loop.py; step73_loop.py", "Linear (small phase errors)."),
 ("M9", "Phase-domain jitter budget", "72, 73",
  "Output phase-noise spectrum and rms jitter per block, FFNC on and off",
  "Combines every block's noise through its own transfer function; shows which allocation matters.",
  "S_out = sum S_i |T_i|^2 with H, 1-H, the cancellation path G_c and aliasing; jitter = sqrt(int S df)/(2 pi f0).",
  "design/budget/step72_budget.py", "Uses allocations until block results replace them."),
]

# devices: block, instance, model, W per finger (um), nf, L (um), role
DEVICES = [
 ("loop filter", "R1", "res_xhigh_po_2p85", 2.85, 1, 15.51, "zero resistor 11.01 kOhm"),
 ("loop filter", "C1 MOS unit", "nfet_01v8", 10, 1, 10, "18 units (2 tiles), gate = filter node"),
 ("loop filter", "C1 MIM tile", "cap_mim_m3_1", 30, 1, 30, "2 tiles over the MOS units"),
 ("loop filter", "C2", "cap_mim_m3_1", 30, 1, 18.11, "2 rectangles, pole capacitor"),
 ("VCO dcell", "XP1/XP2", "pfet_01v8", 3.0, 4, 0.15, "main inverter pMOS"),
 ("VCO dcell", "XN1/XN2", "nfet_01v8", 3.0, 2, 0.15, "main inverter nMOS"),
 ("VCO dcell", "XS1/XS2", "nfet_01v8", 2.25, 1, 0.15, "fine-tune switch (base cell)"),
 ("VCO dcell", "XC1/XC2", "nfet_01v8", 4.5, 1, 0.5, "fine-tune MOS cap"),
 ("VCO dcell", "XT1N/XT2N", "nfet_01v8", 0.63, 1, 0.15, "coupling TG nMOS (base cell)"),
 ("VCO dcell", "XT1P/XT2P", "pfet_01v8", 0.63, 1, 0.15, "coupling TG pMOS"),
 ("VCO acbuf", "XCC", "cap_mim_m3_1", 4.2, 1, 4.2, "AC coupling 38 fF"),
 ("VCO acbuf", "XRF", "res_xhigh_po_0p35", 0.35, 1, 39.8, "self-bias 227 kOhm"),
 ("VCO acbuf", "XP1", "pfet_01v8", 2, 1, 0.15, "inverter 1"), ("VCO acbuf", "XN1", "nfet_01v8", 1, 1, 0.15, "inverter 1"),
 ("VCO acbuf", "XP2", "pfet_01v8", 4, 1, 0.15, "inverter 2"), ("VCO acbuf", "XN2", "nfet_01v8", 2, 1, 0.15, "inverter 2"),
]

LIMITS = [  # model, Lmin, Lmax, Wmin (per finger), Wmax, note
 ("nfet_01v8", 0.15, 100, 0.36, 100, "model bins"), ("pfet_01v8", 0.15, 100, 0.42, 100, "model bins"),
 ("nfet_01v8_lvt", 0.15, 100, 0.42, 100, "model bins"), ("pfet_01v8_lvt", 0.35, 100, 0.42, 100, "model bins"),
 ("nfet_g5v0d10v5", 0.5, 100, 0.42, 100, "model bins"), ("pfet_g5v0d10v5", 0.5, 100, 0.42, 100, "model bins"),
 ("cap_mim_m3_1", 2, 30, 2, 30, "side 2-30 um (pcell)"),
 ("res_xhigh_po_0p35", 0.5, 1000, 0.35, 0.35, "W fixed; fold above 100 um"),
 ("res_xhigh_po_2p85", 0.5, 1000, 2.85, 2.85, "W fixed; fold above 100 um"),
]

PROBLEMS = [  # step, area, problem, how it shows up, cause, solution, status
 ("old", "PDK legality", "Resistor and capacitor sizes outside the PDK limits in the old design",
  "DRC failures, Cadence kit refuses values", "sizes chosen from calculation only",
  "tools/pdk_limits.py checks every device; values snapped to legal widths and tiles", "solved"),
 (7, "Cadence correlation", "Kit models give different R/C than the open PDK",
  "LF branch +41 % in Spectre with kit models", "different model decks", "run Spectre with the frozen models; "
  "repeat R/C corner runs with the kit before freezing a value in Virtuoso", "open (VM runs)"),
 (72, "phase noise", "FFNC-off L(300 kHz) misses -110 dBc/Hz typ with the simulated ring",
  "-108.1 dBc/Hz in the budget", "ring 1/f^3 corner 1.1 MHz (flicker up-conversion)",
  "allocate f_c3 <= 0.6 MHz (step 74) and CCO flicker corner <= 0.3 MHz (step 75); fallback icp_trim -> f_c 2.8 MHz", "open"),
 (72, "phase noise", "FFNC-on L(300 kHz) has no margin (-119.9 vs -120)", "budget", "reference x N^2 floor",
  "quieter REF receiver (-157 dBc/Hz) for +0.1 mW if needed", "watch"),
 (73, "loop", "Continuous loop design overestimates phase margin", "48.7 deg (t_p 0.5 ns), 40.6 deg (11 ns) instead of 50",
  "sampling and charge-packet delay", "design on the exact sampled model; t_p <= 5 ns required from the clock generator", "solved"),
 (73, "loop filter", "MOS-cap C1 collapses at low V_cont", "C-V: 7.5 fF/um2 at 0.9 V, 2.2 at 0 V",
  "MOS cap leaves inversion", "keep V_cont in 0.6-1.2 V (VCO fine-tune range requirement)", "requirement"),
 (73, "loop", "Loop gain spread (A, g_m, tau, K_VCO) up to x0.3-2.4", "PM < 45 deg at extremes",
  "PVT", "icp_trim (Gm unit count 2-5) recentres process; residual spread must stay x0.75-1.3", "requirement"),
 (74, "VCO noise", "1/f^3 corner 1.03 MHz in the base cell", "ISF: flicker share 43 % tuning switch, 44 % TG nMOS",
  "minimum-length (0.15 um) switch and TG nMOS carry flicker straight into the ISF dc part",
  "draw the switch and TG nMOS at L = 0.5 um with the same W/L (variant 'quiet')", "in progress"),
 (74, "schematic", "Hand-drawn schematics hard to read and drifting from simulation",
  "overlapping wires/text, flat drawings", "no checks", "tools/xsch.py: generated hierarchical schematics with "
  "drawing checks + netgen LVS against the simulated netlist", "solved"),
 (74, "VCO", "4-stage pseudo-differential ring latches at power-up", "startup sims (proposal/sim/startup_results.md)",
  "even stage count: each half is a non-inverting loop", "5 stages (odd): both halves invert", "solved"),
 (74, "VCO", "pfet_01v8_lvt minimum L is 0.35 um", "model bins", "PDK", "no LVT pMOS in the ring; nfet_01v8_lvt considered", "decided"),
]

RESULTS = [  # parameter, value, spec / target, unit, kind ("max" = value must be <= target, "min" = >=), step, note
 ("Jitter FFNC on, typ (budget)", 1.36, 1.4, "ps", "max", 72, ""),
 ("Jitter FFNC off, typ (budget)", 2.11, 2.3, "ps", "max", 72, ""),
 ("Jitter FFNC on, pess (budget)", 1.73, 3.2, "ps", "max", 72, ""),
 ("L(300 kHz) FFNC off, typ", -110.2, -110, "dBc/Hz", "max", 72, "needs ring f_c3 <= 0.6 MHz"),
 ("Power FFNC on, typ", 9.08, 9.0, "mW", "max", 72, "0.9 % over 'about 9'"),
 ("Power FFNC on, worst", 13.47, 15, "mW", "max", 72, ""),
 ("Area", 0.0575, 0.08, "mm2", "max", 72, ""),
 ("Loop phase margin (sampled)", 50.0, 45, "deg", "min", 73, ""),
 ("Loop settling to +-10 ps", 0.34, 5, "us", "max", 73, "phase loop only; FLL adds"),
 ("VCO base cell: current for 1.6 GHz (tt)", 1.244, 1.31, "mA", "max", 74, "ideal-RC buffers"),
 ("VCO base cell: L(1 MHz) thermal (ISF)", -98.01, -98.35, "dBc/Hz", "max", 74, "0.3 dB short, ideal-RC buffers"),
 ("VCO base cell: 1/f^3 corner", 1.03, 0.6, "MHz", "max", 74, "fails -> quiet variant"),
]
