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
 (74, "VCO redesign", "done", "docs/design/step74_vco.md",
  "5-stage x1.5 ring, S and TG nMOS at L 0.3 um: 1.437 mA for 1.6 GHz, L(1 MHz) -98.7 dBc/Hz, f_c3 0.57 MHz, "
  "K_VCO -300 MHz/V; hierarchical schematics LVS-clean"),
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
 ("VCO dcell", "XS1/XS2", "nfet_01v8", 4.5, 1, 0.3, "fine-tune switch (step 74: L 0.3 for flicker)"),
 ("VCO dcell", "XC1/XC2", "nfet_01v8", 4.5, 1, 0.5, "fine-tune MOS cap"),
 ("VCO dcell", "XT1N/XT2N", "nfet_01v8", 0.84, 1, 0.3, "coupling TG nMOS (step 74: L 0.3 for flicker)"),
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
  "S at 4.5/0.3 um, TG nMOS at 0.84/0.3 um: corner 0.57 MHz for +9 % current (L = 0.5 um cost 21 % speed)", "solved"),
 (74, "schematic", "Hand-drawn schematics hard to read and drifting from simulation",
  "overlapping wires/text, flat drawings", "no checks", "tools/xsch.py: generated hierarchical schematics with "
  "drawing checks + netgen LVS against the simulated netlist", "solved"),
 (74, "VCO", "4-stage pseudo-differential ring latches at power-up", "startup sims (proposal/sim/startup_results.md)",
  "even stage count: each half is a non-inverting loop", "5 stages (odd): both halves invert", "solved"),
 (74, "VCO", "pfet_01v8_lvt minimum L is 0.35 um", "model bins", "PDK", "no LVT pMOS in the ring; nfet_01v8_lvt considered", "decided"),
 (74, "VCO", "Tuning flattens below vtune 0.7 V (switch turns off)", "K_VCO -216 MHz/V in 0.6-0.75 V vs -330 above",
  "switch S gate overdrive vanishes", "lock window V_cont 0.7-1.2 V (centre 0.95 V); MOS loop cap still >= 6.9 fF/um2", "requirement"),
 (74, "VCO", "Ring node near 1.8 V at the top of the range at ss/110 C", "1.78 V at 1.76 GHz with 15 fF/node",
  "slow corner + wiring capacitance", "layout target <= 10 fF per node (1.71 V); CCO clamp; nfet_01v8_lvt fallback", "requirement"),
 (74, "simulation", "Symmetric netlist does not start oscillating from all-zero nodes", "f ~ 100 GHz noise, no swing",
  "perfect symmetry: metastable common-mode point", "start-up test with 1 % mismatch (real silicon always has it)", "solved"),
 (74, "simulation", "PDK poly resistor makes transients ~5x slower", "behavioural R model",
  "voltage-dependent resistor expression", "characterisation with ideal R/C of the same values incl. 3 fF end parasitics "
  "(matches the PDK buffer to 0.001 %); ISF and LVS with PDK devices", "solved"),
 (74, "power", "Ring needs 9 % more current after the flicker fix", "typ power 9.55 mW vs 'about 9'",
  "larger switch / TG capacitance", "accept (FoM unchanged -227.8 dB) or recover 0.5 mW from LDO reserve, dummy buffers, NCB", "watch"),
 (74, "power (guaranteed)", "Worst-case power may exceed the 15 / 13 mW maxima after layout",
  "margin tracker: 15.23 / 13.15 mW post-layout estimate", "ring needs 2.0-2.3 mA at ss/110 C for 1.76 GHz, fed from 3.63 V "
  "through a 1:8 mirror (1/8 extra current in the reference branch)",
  "step 75: 1:16 CCO mirror (-0.5 mW worst); layout rule <= 10 fF per ring node (-1.0 mW); replace the x1.3 worst-case "
  "factor on the other blocks with simulated values", "open - fix in step 75"),
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
 ("VCO base cell: 1/f^3 corner", 1.02, 0.6, "MHz", "max", 74, "fails -> step-74 cell"),
 ("VCO step-74 cell: current for 1.6 GHz (tt)", 1.437, 1.45, "mA", "max", 74, "+9 % vs base"),
 ("VCO step-74 cell: L(1 MHz) thermal (ISF)", -98.71, -98.35, "dBc/Hz", "max", 74, ""),
 ("VCO step-74 cell: 1/f^3 corner", 0.57, 0.6, "MHz", "max", 74, ""),
 ("VCO K_VCO magnitude, 0.6-1.2 V avg (tt)", 300, 300, "MHz/V", "min", 74, "matches the step-73 assumption"),
 ("VCO ring node at 1.76 GHz, ss/110 C, 10 fF", 1.71, 1.8, "V", "max", 74, "15 fF: 1.78 V"),
 ("VCO start-up time (ss/110 C, 1 % mismatch)", 8.5, 20, "ns", "max", 74, "10th cycle"),
 ("Jitter FFNC on, typ, with step-74 VCO", 1.318, 1.4, "ps", "max", 74, ""),
 ("Jitter FFNC off, typ, with step-74 VCO", 2.040, 2.3, "ps", "max", 74, ""),
 ("Power FFNC on, typ, with step-74 VCO", 9.55, 9.0, "mW", "max", 74, "about 9 mW in the proposal"),
]

# Margin tracker: every proposal spec vs the best pre-layout number so far and the expected post-layout change.
# kind: "max" (value must be <= limit) or "min" (>=); target: "guaranteed" (min/max column of the proposal, must hold
# post-layout over PVT) or "typ" (design target at tt).  pre = None -> not simulated yet.
# change = expected post-layout shift in the spec's own unit (worsening direction), an engineering estimate:
#   jitter +10 % (parasitics recovered by more current and re-trimmed codes), power +0.97 mW worst (ring wiring
#   15 fF instead of 10 fF at ss/110 C) / +8 % typ, phase noise +1 dB, ring node +70 mV (15 fF), area +25 % (routing).
# guard = margin wanted *after* that change before calling a spec safe.
MARGIN = [  # spec, condition, target, kind, limit, unit, pre, change, guard, source, verify in
 ("RMS jitter, FFNC on", "typ, 10 kHz-40 MHz", "typ", "max", 1.4, "ps", 1.318, 0.132, 0.05, "step-72 model + step-74 ring", "121"),
 ("RMS jitter, FFNC on", "max over PVT", "guaranteed", "max", 3.2, "ps", 1.73, 0.17, 0.5, "step-72 model, pessimistic set", "121"),
 ("RMS jitter, FFNC off", "typ", "typ", "max", 2.3, "ps", 2.04, 0.20, 0.05, "step-72 model + step-74 ring", "121"),
 ("RMS jitter, FFNC off", "max over PVT", "guaranteed", "max", 4.7, "ps", 2.71, 0.27, 0.5, "step-72 model, pessimistic set", "121"),
 ("Jitter reduction by FFNC", "min, after calibration", "guaranteed", "min", 20, "%", 36, 5, 5, "step-72 model, pessimistic set", "121"),
 ("Phase noise 300 kHz, FFNC off", "typ", "typ", "max", -110, "dBc/Hz", -110.6, 1.0, 0.5, "step-72 model + step-74 ring", "121"),
 ("Phase noise 300 kHz, FFNC off", "max", "guaranteed", "max", -102, "dBc/Hz", -106.7, 1.0, 2.0, "step-72 model, pessimistic set", "121"),
 ("Phase noise 300 kHz, FFNC on", "typ", "typ", "max", -120, "dBc/Hz", -120.0, 1.0, 0.5, "step-72 model + step-74 ring", "121"),
 ("Phase noise 300 kHz, FFNC on", "max", "guaranteed", "max", -110, "dBc/Hz", -114.5, 1.0, 2.0, "step-72 model, pessimistic set", "121"),
 ("Power, FFNC on", "typ", "typ", "max", 9.0, "mW", 9.55, 0.76, 0.3, "step-72 table + step-74 ring 1.437 mA", "120"),
 ("Power, FFNC on", "max over PVT", "guaranteed", "max", 15, "mW", 14.26, 0.97, 0.75, "ring 2.02 mA at ss/110 C, 3.63 V; others typ x1.3", "120"),
 ("Power, FFNC off", "typ", "typ", "max", 7.5, "mW", 8.10, 0.65, 0.3, "as above minus NCB", "120"),
 ("Power, FFNC off", "max over PVT", "guaranteed", "max", 13, "mW", 12.18, 0.97, 0.65, "as above minus NCB", "120"),
 ("Area", "standalone, excl. pads", "guaranteed", "max", 0.12, "mm2", 0.0575, 0.0144, 0.01, "step-72 area table incl. LDO", "115"),
 ("Area", "typ", "typ", "max", 0.08, "mm2", 0.0575, 0.0144, 0.005, "step-72 area table incl. LDO", "115"),
 ("Ring supply node", "absolute limit, any code/corner", "guaranteed", "max", 1.80, "V", 1.71, 0.07, 0.05, "step 74, 1.76 GHz ss/110 C, 10 fF/node", "118"),
 ("Output frequency range", "1.44-1.76 GHz reachable", "guaranteed", "min", 1.76, "GHz", 1.98, 0.08, 0.05, "step 74: ss/110 C at 2.4 mA, 10 fF", "118"),
 ("Jitter FoM", "typ", "typ", "max", -227.5, "dB", -227.8, 0.8, 0.2, "1.318 ps, 9.55 mW", "121"),
 ("Lock time", "max", "guaranteed", "max", 20, "us", None, None, 5, "phase loop 0.34 us (step 73); FLL not designed", "104"),
 ("Reference spur, FFNC off", "max", "guaranteed", "max", -45, "dBc", None, None, 5, "not simulated", "105"),
 ("Reference spur, FFNC on", "max", "guaranteed", "max", -42, "dBc", None, None, 5, "not simulated", "105"),
 ("Regulated analog rail", "1.71-1.89 V", "guaranteed", "max", 1.89, "V", None, None, 0.03, "LDO not designed", "LDO step"),
 ("Power, output dividers", "max", "guaranteed", "max", 1.0, "mW", None, None, 0.2, "dividers not designed", "85"),
]


# ------------------------------------------------------------------------------------------------ step 75 (CCO)
STEPS.append((75, "CCO (current-fed VCO supply)", "done", "docs/design/step75_cco.md",
              "IBIAS -> 5-bit DAC (13 + code units of 2.5 uA) -> 1:25 mirror with 10 Mohm / 7.3 pF filter: 0.84-2.79 mA (tt), "
              "range kept over +/-20 % IBIAS and 5 corners; active clamp keeps ring node <= 1.793 V; 8.9 pA/rtHz at 1 MHz; "
              "level shifters 1.8 -> 3.3 V; schematics LVS-clean"))
METHODS += [
 ("M10", "DC operating point and compliance sweep", "75",
  "Output current of a current source for each code / corner / supply / bias, and its dependence on the output voltage",
  "A current source is a DC circuit: its job is a current at a voltage. An operating point per condition is exact (no "
  "approximation) and cheap, so all 90 corner combinations plus a full code sweep fit in minutes.",
  "The ring node is replaced by an ideal voltage source at the typical ring voltage (1.45 V); its current (vr#branch) "
  "is the CCO output. For compliance, the source is swept 0-2.4 V (.dc) at the least-headroom corner (VDDA 2.97 V, "
  "ss/110 C, max code): the current must stay flat over the ring's range (1.38-1.8 V).",
  "design/cco/step75_sim.py (sections A, B); xschem: tb_cco_dc",
  "Ignores the ring's own I-V (load line); M12 closes that gap. Exact for the models used."),
 ("M11", "Output-current noise (.noise) and supply rejection (.ac)", "75",
  "Output current noise spectrum (A/rtHz) of the complete circuit incl. PDK resistors and MIM caps; |dI/dVDDA| vs frequency",
  "Noise of a biased analog block is small-signal: .noise linearises every device at its operating point and adds "
  "their noise (thermal, flicker, resistor) through the exact transfer functions - faster and more accurate than a "
  "transient noise run. The same linearisation with an ac 1 V source on VDDA gives supply rejection.",
  "The ring node is an ideal source at 1.45 V through a 0 V ammeter; a CCVS (h1, 1 V/A) converts its current into a "
  "voltage 'o' so .noise reports A/rtHz. option sparse is needed (KLU fails on .noise). The spectrum feeds the "
  "budget (M9): S_f = K_I^2 S_i, shaped by |(1-Gc)(1-H)|^2, gives the CCO jitter and L(300 kHz).",
  "design/cco/step75_noise.py, step75_sim.py (section D); xschem: tb_cco_ac",
  "Linear around the operating point; tt only (corners shift g_m by +/-15 %)."),
 ("M12", "Clamp check with the ring's measured I-V (load-line method)", "75",
  "The ring-node voltage reached for each code when the CCO drives the real ring at the worst corner",
  "The ring node is set by where the CCO output (a current source) meets the ring's I-V curve and the clamp. "
  "Simulating the whole ring for every code would take hours; a behavioural model of its I-V gives the same DC "
  "intersection in seconds.",
  "The ring's average I-V at ss/110 C, 10 fF/node (from step-74 transients, M1) is a pwl B-source current "
  "I_ring(V). The CCO plus clamp drive it at VDDA 3.63 V with IBIAS 4 and 6 uA; the .op solution is the ring node.",
  "design/cco/clamp_ring.py",
  "The ring's average current replaces its switching current; good for DC, not for ripple."),
 ("M13", "Level-shifter transient at the hardest supply corners", "75",
  "Whether the 1.8 -> 3.3 V shifter switches, its output levels and edge times",
  "A cross-coupled level shifter is a ratioed latch: it only flips if the nMOS pull-downs (driven from the low "
  "supply) win against the pMOS loads (on the high supply). The worst case is lowest VDDD with highest VDDA, slow "
  "and fast corners - a transient shows directly whether it flips.",
  "Pulse on 'in' (0-1.71 V), VDDA 3.63 V, 20 fF loads; .meas rise/fall at VDDA/2 and the high/low levels; ss/110 C and ff/-40 C.",
  "design/cco/step75_sim.py (section E)",
  "Static control bits: speed hardly matters, only correct switching."),
]
DEVICES += [
 ("CCO DAC", "XNB", "nfet_g5v0d10v5", 1, 1, 4.0, "IBIAS input diode, m=2"),
 ("CCO DAC", "XU0..XU5", "nfet_g5v0d10v5", 1, 1, 4.0, "unit sinks, m = 13,1,2,4,8,16"),
 ("CCO DAC", "XS0..XS5", "nfet_g5v0d10v5", 1, 1, 0.5, "unit switches"),
 ("CCO", "XMREF", "pfet_g5v0d10v5", 20, 2, 2.0, "reference diode, 1 unit"),
 ("CCO", "XMOUT", "pfet_g5v0d10v5", 20, 2, 2.0, "output mirror, m=25"),
 ("CCO", "xrf1..20", "res_xhigh_po_0p35", 0.35, 1, 87.48, "R_F = 10 Mohm (20 segments)"),
 ("CCO", "XCF", "cap_mim_m3_1", 30, 1, 30, "C_F = 7.3 pF, m=4, over MOUT"),
 ("CCO", "XPEN / XNEN", "pfet / nfet_g5v0d10v5", 2, 1, 0.5, "enable pull-up / IBIAS pull-down"),
 ("CCO clamp", "XPREP", "pfet_01v8", 1, 1, 0.15, "replica diode from VDDL"),
 ("CCO clamp", "XUREP", "nfet_g5v0d10v5", 1, 1, 4.0, "replica bias (1 DAC unit)"),
 ("CCO clamp", "XPSEN", "pfet_01v8", 1, 1, 0.15, "sense device"),
 ("CCO clamp", "XRS", "res_xhigh_po_0p35", 0.35, 1, 56.0, "sense resistor 320 kOhm"),
 ("CCO clamp", "XNSH", "nfet_01v8", 5, 4, 0.15, "shunt"),
 ("CCO", "XTGN / XTGP", "n/pfet_g5v0d10v5", 2, 1, 0.5, "VTEST transmission gate"),
 ("CCO", "XRINJ", "res_xhigh_po_0p35", 0.35, 1, 3.39, "VTEST injection 20 kOhm"),
 ("Level shifter", "XP1/XP2, XN1/XN2", "p/nfet_g5v0d10v5", 1, 1, 0.5, "latch pMOS W 1, pull-down nMOS W 3"),
]
PROBLEMS = [p if not (p[0] == 74 and p[1] == "power (guaranteed)") else
            p[:5] + ("step 75: 1:25 CCO mirror (reference branch 4 % instead of 12.5 %): -0.62 mW worst, -0.40 mW typ; "
                     "ring-node capacitance rule <= 10 fF still to be met in layout", "fixed in step 75 (power) - layout rule open")
            for p in PROBLEMS]
PROBLEMS += [
 (75, "clamp", "Single-pMOS clamp too soft", "at 1.7 V it already stole 0.47-0.85 mA of the ring's current",
  "a pMOS conducts by its Vsg: one device cannot be both off at 1.7 V and sink 1 mA at 1.8 V",
  "two-stage active clamp: replica-biased sense pMOS (weak inversion, exponential) -> 320 kOhm -> nMOS shunt; RS 48.9 -> 56 um, shunt nf 2 -> 4", "fixed"),
 (75, "range", "IBIAS +/-20 % broke the frequency range", "1:20 mirror / 19 base units: code 31 at 4 uA below 2.02 mA, code 0 at 6 uA above 0.97 mA",
  "the DAC current scales with IBIAS; a 1.7:1 code range cannot absorb a 1.5:1 bias spread plus the corners",
  "1:25 mirror, 13 base units (3.4:1 code range); residual 50 uA excess at ff/-40 C/6 uA/code 0 is covered by fine tuning (60 of 75 MHz)", "fixed (fine-tune margin used at one corner)"),
 (75, "noise", "Filter resistor too noisy", "300 kOhm: 21 pA/rtHz at 1 MHz, L(300 kHz) FFNC off -104 dBc/Hz",
  "above the RC corner the resistor's noise at the gate falls as 1/(sqrt(R) C): a small R is noisier, not quieter",
  "R_F 10 Mohm (20 x 87.48 um xhigh_po_0p35) with 7.3 pF MIM over the output array: 8.9 pA/rtHz", "fixed"),
 (75, "schematic", "Wires drawn through pins shorted devices", "LVS: level shifter x and y nodes merged; last filter segment shorted",
  "a straight wire passing over a pin connects it in xschem; a crossing drawn with a vertex on both wires is a junction",
  "drawing checker (tools/xsch.py) now flags 4-way junctions and wires touching two pins of one device; all CCO cells LVS-clean", "fixed"),
 (75, "lock time", "Slow CCO filter (tau = 70 us) after pll_en", "current ramps for ~0.2 ms after enable",
  "10 Mohm x 7.3 pF is chosen for noise", "set cco_code before pll_en; the FLL waits for the CCO to settle (step 81)", "open - handle in step 81"),
]
RESULTS += [
 ("CCO current code 31, tt", 2.79, 2.02, "mA", "min", 75, "tt, IBIAS 5 uA (code 0: 0.84 mA)"),
 ("CCO current code 31, worst (ss/110 C, IBIAS 4 uA)", 2.20, 2.02, "mA", "min", 75, "ring needs 2.02 mA for 1.76 GHz at 10 fF/node"),
 ("CCO current code 0, worst (ff/-40 C, IBIAS 6 uA)", 1.02, 0.97, "mA", "max", 75, "excess 50 uA = 60 MHz, inside the +/-75 MHz fine tune"),
 ("Ring node, worst (code 31, IBIAS 6 uA, ss/110 C, VDDA 3.63 V)", 1.793, 1.8, "V", "max", 75, "active clamp"),
 ("CCO output noise at 1 MHz", 8.92, 10.3, "pA/rtHz", "max", 75, ".noise, complete circuit"),
 ("Jitter FFNC off, typ, with step-75 CCO", 1.958, 2.3, "ps", "max", 75, "step-72 model with the simulated CCO spectrum"),
 ("Jitter FFNC on, typ, with step-75 CCO", 1.270, 1.4, "ps", "max", 75, "step-72 model with the simulated CCO spectrum"),
 ("Supply -> current", 0.25, None, "uA/mV", "info", 75, "1 kHz-10 MHz, tt"),
 ("Power FFNC on, typ, with 1:25 CCO", 9.15, 9.0, "mW", "max", 75, "-0.40 mW vs step 74"),
]
_m = {(r[0], r[1]): r for r in MARGIN}
def _set(spec, cond, pre, change=None, source=None):
    r = list(_m[(spec, cond)]); r[6] = pre
    if change is not None: r[7] = change
    if source: r[9] = source
    _m[(spec, cond)] = tuple(r)
_set("RMS jitter, FFNC on", "typ, 10 kHz-40 MHz", 1.270, source="step-72 model + step-74 ring + step-75 CCO")
_set("RMS jitter, FFNC off", "typ", 1.958, source="step-72 model + step-74 ring + step-75 CCO")
_set("Phase noise 300 kHz, FFNC off", "typ", -110.9, source="step-72 model + step-74 ring + step-75 CCO")
_set("Phase noise 300 kHz, FFNC on", "typ", -120.0, source="step-72 model + step-74 ring + step-75 CCO")
_set("Power, FFNC on", "typ", 9.15, source="step-72 table, ring 1.437 mA, 1:25 CCO (step 75)")
_set("Power, FFNC on", "max over PVT", 13.64, source="ring 2.02 mA at ss/110 C, 3.63 V, 1:25 CCO; others typ x1.3")
_set("Power, FFNC off", "typ", 7.70, source="as above minus NCB")
_set("Power, FFNC off", "max over PVT", 11.56, source="as above minus NCB")
_set("Jitter FoM", "typ", -228.1, source="1.270 ps, 9.15 mW")
MARGIN = list(_m.values()) + [
 ("Ring supply node", "abuse: code 31, IBIAS +20 %, ss/110 C", "guaranteed", "max", 1.8, "V", 1.793, 0.005, 0.01,
  "step 75 active clamp (referenced to VDDL)", "118"),
]


# ------------------------------------------------------------------------------------------------ step 76 (REF buffer)
STEPS.append((76, "REF_IN receiver (reference buffer)", "done", "docs/design/step76_refbuf.md",
              "AC-coupled (3.6 pF) self-biased (5 Mohm) current-reuse stage, 60 uA header + C_H, 3.3 -> 1.8 V, NOR enable: "
              "per-edge jitter 0.23 / 0.61 / 1.15 ps at 3.3 / 1.0 / 0.4 V pp; system 1.95 / 1.26 ps at full swing; "
              "0.25 mW typ, 0.39 mW worst; schematics LVS-clean"))
METHODS += [
 ("M14", "Crossing-point noise analysis (.noise at the self-bias point)", "76",
  "Gate-referred noise spectrum of a threshold circuit at the instant of its crossing, incl. flicker and bias-resistor noise",
  "A self-biased inverter rests exactly at its trip point, i.e. at the operating point it passes through at every "
  "crossing. A small-signal .noise there is exact for the slow (quasi-static) noise that shifts the crossing, and it "
  "shows which device or resistor dominates. It is fast enough to be used for sizing.",
  "Output noise of S1 (.noise, source = the pad generator through 50 ohm) divided by the gain |v(s1)/v(vin)| gives the "
  "gate-referred PSD. Jitter PSD = S_gate/s_gate^2 with s_gate = pi f V_pp |v(vin)/v(pad)| at 50 MHz; "
  "L(f) = (2 pi f_ref)^2 S_t(f)/2 for f << f_ref.",
  "design/refbuf/refbuf.py: input_noise(); step76_noise.py",
  "Valid for slow noise only; the white, fast noise of a switching comparator needs M15."),
 ("M15", "Transient-noise jitter (trnoise injection, edge-time statistics)", "76",
  "Per-edge jitter and its spectrum for the real, non-linear switching of the receiver",
  "In a high-gain comparator the small-signal gain at DC (~190) is not the gain that applies while the input sweeps "
  "through the threshold (~30), so 'integrated output noise / output slope' is wrong by about 2x. Simulating the "
  "switching with noise present measures the jitter directly.",
  "The white plateau of the M14 noise, referred to the pad, is injected as a trnoise voltage (time step 10 ps, i.e. "
  "50 GHz bandwidth) in series with the 50 ohm source of a noiseless circuit. 300 refclk rising-edge times are "
  "interpolated; a 4th-order polynomial removes the deterministic settling of the AC-coupling bias; the rms "
  "deviation is the per-edge jitter (period jitter / sqrt 2 agrees, so the jitter is white). L_floor = (2 pi f sigma)^2 / f.",
  "design/refbuf/tn_run.py (refbuf.tnoise, edge_stats)",
  "Noise sources stationary at their crossing-point level; 300 edges give sigma to about +/-4 %; ~10 min per run."),
 ("M16", "Large-signal transient: delay, duty, edge rate, supply current, supply sensitivity, start-up", "76",
  "Delay pad->out, duty, 10-90 % rise time, average supply currents over corners, amplitudes, frequencies and supplies; "
  "edge-time sensitivity to VDDA / VDDL; start-up after enable; the disabled state",
  "These are large-signal properties of a switching circuit; only a transient shows them. A finite difference of "
  "two transients (supply +10 mV) gives the supply sensitivity of the edge time directly in ps/mV.",
  "Sine (or square) source at the pad through 50 ohm; 14 cycles, the last 5 evaluated in numpy from the waveforms "
  "(interpolated crossings). Start-up: pll_en steps at 0.5 us, 25 us run, first edge after which all periods are "
  "within 2 % of 1/f.",
  "design/refbuf/step76_sim.py; xschem: tb_refin (to be drawn in phase 8)",
  "Drawn netlist with PDK resistors and MIM capacitors; no layout parasitics yet."),
]
DEVICES += [
 ("REF receiver", "XRPU / XRPD", "res_xhigh_po_0p35", 0.35, 1, 87.48, "pad divider, 500 kOhm each"),
 ("REF receiver", "XCAC", "cap_mim_m3_1", 30, 1, 30, "C_AC 3.6 pF, m=2, bottom plate on the pad"),
 ("REF receiver", "xrb0..9", "res_xhigh_po_0p35", 0.35, 1, 87.48, "R_B = 5 Mohm (10 segments)"),
 ("REF receiver S1", "XPD / XPH", "pfet_g5v0d10v5", 2, 1, 4.0, "bias diode / header m=24 (60 uA)"),
 ("REF receiver S1", "XCH", "cap_mim_m3_1", 30, 1, 30, "C_H 1.8 pF"),
 ("REF receiver S1", "XP1", "pfet_g5v0d10v5", 10, 12, 1.0, "input pMOS, body = source"),
 ("REF receiver S1", "XN1", "nfet_g5v0d10v5", 10, 12, 1.0, "input nMOS"),
 ("REF receiver S1", "XPEN / XNS1", "p/nfet_g5v0d10v5", 2, 1, 0.5, "enable"),
 ("REF receiver", "XP2 / XN2", "p/nfet_g5v0d10v5", 2, 1, 0.5, "S2 on VDDA (W 2 / 1)"),
 ("REF receiver", "XPL / XNL", "p/nfet_g5v0d10v5", 2, 1, 0.5, "3.3 -> 1.8 V inverter on VDDL (W 2 / 1)"),
 ("REF receiver", "XPB,XPB2 / XNB,XNB2", "p/nfet_01v8", 4, 1, 0.15, "output NOR (pMOS W 4, nMOS W 1)"),
]
PROBLEMS += [
 (76, "noise", "First stage too noisy: 0.84 ps per edge at 1 V pp", "transient-noise run (M15) of the first sizing",
  "the header current source degenerated the pMOS (no current reuse) and had as much g_m as the input nMOS, so its "
  "noise counted fully", "C_H = 1.8 pF from the header node to VDDA, header L 2 -> 4 um, input devices 120 um / 1 um in "
  "moderate inversion, 40 -> 60 uA: 0.61 ps", "fixed"),
 (76, "method", "Output noise / output slope overestimated the jitter",
  "integrated .noise at s1 / slope gave 1.2 ps where the transient-noise run gave 0.6 ps",
  "the comparator's DC small-signal gain is ~6x the gain that applies during a crossing",
  "use M15 (transient noise) for the white per-edge jitter and M14 only for slow noise", "fixed (method)"),
 (76, "method", "Pad-referred low-frequency noise blew up below the AC-coupling corner",
  "the first phase-noise estimate showed -150 dBc/Hz at 300 kHz from the 'pad-referred' spectrum",
  "slow noise must be referred to the gate and divided by the gate slope at 50 MHz, not by the pad-to-gate gain at "
  "the noise frequency", "refer slow noise at the gate with the 50 MHz divider: no low-frequency excess remains", "fixed"),
 (76, "spec", "Typical noise targets need a full-swing reference",
  "1 V pp sine: FFNC-on L(300 kHz) -118.2 dBc/Hz (typ -120); 0.4 V pp: FFNC-off -109.7 (typ -110)",
  "jitter per edge = noise / input slope: a 1 V pp sine is 3.3x less steep than 3.3 V pp, and on-chip noise costs current",
  "state the typical specs for a full-swing (>= 2 V pp, e.g. 3.3 V CMOS) XO; guaranteed limits are met down to 0.4 V pp",
  "open - proposal wording / test-plan reference source"),
 (76, "duty", "Duty up to 65 % at VDDA 3.63 V with 0.4 V pp", "M16 corner runs (fs, ss at 3.63 V)",
  "S2's threshold follows VDDA while s1's edges are slow at small inputs",
  "accepted: >= 45 % is met (47-65 %) and the SSPD uses only the rising edge; a replica-biased S2 would centre it", "accepted"),
 (76, "start-up", "Input bias settles slowly after pll_en", "periods within 2 % after 3.8 us, bias drifts for ~30 us",
  "the AC-coupling bias is charged through R_B", "R_B 20 -> 5 Mohm (4x faster, also less in-band noise); FLL waits for the CCO (0.3 ms) anyway", "fixed"),
]
RESULTS += [
 ("REF receiver per-edge jitter, 1 V pp sine", 0.609, 0.4, "ps", "max", 76, "M15; target from the step-72 allocation"),
 ("REF receiver per-edge jitter, 3.3 V pp sine", 0.227, 0.4, "ps", "max", 76, "M15"),
 ("REF receiver power, tt, 1 V pp", 0.254, 0.2, "mW", "max", 76, "allocation 0.2 mW"),
 ("REF receiver duty, worst", 47.0, 45, "%", "min", 76, "min over corners and amplitudes (max 65 %)"),
 ("Jitter FFNC on, typ, full-swing REF, step-76 receiver", 1.256, 1.4, "ps", "max", 76, "3.3 V pp; 1.329 ps at 1 V pp"),
 ("L(300 kHz) FFNC on, typ, full-swing REF", -120.7, -120, "dBc/Hz", "max", 76, "3.3 V pp; -118.2 at 1 V pp"),
]
_m = {(r[0], r[1]): r for r in MARGIN}
_set("RMS jitter, FFNC on", "typ, 10 kHz-40 MHz", 1.256, source="steps 74-76 simulated (REF 3.3 V pp); 1.33 ps at 1 V pp")
_set("RMS jitter, FFNC off", "typ", 1.954, source="steps 74-76 simulated (REF 3.3 V pp)")
_set("Phase noise 300 kHz, FFNC off", "typ", -111.0, source="steps 74-76 simulated (REF 3.3 V pp)")
_set("Phase noise 300 kHz, FFNC on", "typ", -120.7, source="steps 74-76 simulated (REF 3.3 V pp); -118.2 at 1 V pp")
_set("Power, FFNC on", "typ", 9.20, source="step-72 table with steps 74-76 (receiver 0.254 mW)")
_set("Power, FFNC on", "max over PVT", 13.74, source="ring 2.02 mA ss/110 C, 1:25 CCO, receiver 0.39 mW; others typ x1.3")
_set("Power, FFNC off", "typ", 7.75, source="as above minus NCB")
_set("Power, FFNC off", "max over PVT", 11.66, source="as above minus NCB")
_set("Jitter FoM", "typ", -228.3, source="1.256 ps, 9.20 mW")
MARGIN = list(_m.values())


# ------------------------------------------------------------------------------------------------ testbench guide (15 Nov)
PROBLEMS += [
 (74, "simulation setup", "VCO simulated without the PDK .spiceinit (ngbehavior=hsa)",
  "stand-alone deck tb_vco_tran: 1.676 GHz at 1.437 mA instead of 1.602 GHz; ring node 1.40 V instead of 1.45 V",
  "design/vco/vco.py ran ngspice without copying the PDK spinit; the CCO, REF buffer and tb/ decks load it",
  "always run through tb/run.sh or copy spinit to .spiceinit; re-run the step-74 characterisation (f(I), K_VCO, ISF "
  "phase noise, corners) and update the CCO clamp model and the budget. Corrected: tt 1.6 GHz at ~1.35 mA, ss/110 C "
  "1.76 GHz at ~1.93 mA (ring 1.70 V), K_VCO ~ -366 MHz/V", "open - re-run step 74"),
 (76, "testbench", "Wrong trnoise amplitude in the stand-alone deck", "deck gave 1.8 ps instead of 0.6 ps",
  "NA = sqrt(S/(2 NT)) mis-computed by hand (2.64 instead of 0.836 mV)",
  "corrected; habit: noiseless baseline run + comparison with the ideal circuit before trusting a noise result", "fixed"),
]


# ------------------------------------------------------------------------------------------------ step-74 re-run (15 Nov)
PROBLEMS = [p if not (p[0] == 74 and p[1] == "simulation setup") else
            p[:6] + ("fixed - step 74 re-run with .spiceinit; CCO NBASE 13 -> 11; loop Gm unit 28.3 -> 26.0 uS",) for p in PROBLEMS]
PROBLEMS += [
 (75, "range", "Code 0 too high at ff/-40 C with IBIAS +20 % after the corrected ring data",
  "ring needs 0.89 mA for 1.44 GHz (was 0.97); code 0 gave up to 1.02 mA (13 base units) = ~160 MHz too fast",
  "the corrected ring is faster per mA", "NBASE 13 -> 11: code 0 <= 0.865 mA, code 31 >= 2.104 mA (needs 1.93)", "fixed"),
 (73, "loop gain", "K_VCO is -326 MHz/V instead of the assumed -300", "corrected step-74 f(vtune)",
  "only beta x K_VCO sets f_c and PM", "Gm unit g_m 28.3 -> 26.0 uS (3 units = 78.1 uS) - requirement on step 79; R1, C1, C2 unchanged", "fixed (requirement)"),
]
RESULTS += [
 ("VCO current for 1.6 GHz, tt (corrected)", 1.352, None, "mA", "info", 74, "was 1.437 mA without .spiceinit"),
 ("VCO 1/f3 corner (corrected)", 0.60, 0.6, "MHz", "max", 74, "at the requirement, no margin"),
 ("VCO L(1 MHz) thermal (corrected)", -98.66, -98.35, "dBc/Hz", "max", 74, ""),
 ("K_VCO average 0.6-1.2 V, tt (corrected)", -326, None, "MHz/V", "info", 74, "ss -223, ff -484"),
 ("Ring node at 1.76 GHz, ss/110 C, 10 fF (corrected)", 1.649, 1.8, "V", "max", 74, "1.93 mA"),
 ("CCO code 0, ff/-40 C, IBIAS 6 uA (NBASE 11)", 0.865, 0.89, "mA", "max", 75, ""),
 ("CCO code 31, ss/110 C, IBIAS 4 uA (NBASE 11)", 2.104, 1.93, "mA", "min", 75, ""),
 ("Ring node abuse case (NBASE 11, corrected ring)", 1.785, 1.8, "V", "max", 75, "active clamp"),
]
_set("RMS jitter, FFNC on", "typ, 10 kHz-40 MHz", 1.261, source="steps 74-76, corrected ring, NBASE 11 (REF 3.3 V pp)")
_set("RMS jitter, FFNC off", "typ", 1.965, source="steps 74-76, corrected ring, NBASE 11 (REF 3.3 V pp)")
_set("Phase noise 300 kHz, FFNC off", "typ", -110.8, source="steps 74-76, corrected (REF 3.3 V pp)")
_set("Phase noise 300 kHz, FFNC on", "typ", -120.7, source="steps 74-76, corrected (REF 3.3 V pp); -118.2 at 1 V pp")
_set("Power, FFNC on", "typ", 8.91, source="ring 1.352 mA (corrected) via 1:25 CCO, receiver 0.254 mW")
_set("Power, FFNC on", "max over PVT", 13.40, source="ring 1.93 mA at ss/110 C (corrected), 1:25 CCO, receiver 0.39 mW; others typ x1.3")
_set("Power, FFNC off", "typ", 7.46, source="as above minus NCB")
_set("Power, FFNC off", "max over PVT", 11.32, source="as above minus NCB")
_set("Jitter FoM", "typ", -228.5, source="1.261 ps, 8.91 mW")
_set("Ring supply node", "absolute limit, any code/corner", 1.649, source="step 74 corrected: 1.76 GHz at ss/110 C, 10 fF/node")
_set("Ring supply node", "abuse: code 31, IBIAS +20 %, ss/110 C", 1.785, source="step 75 clamp, NBASE 11, corrected ring I-V")
_set("Output frequency range", "1.44-1.76 GHz reachable", 2.02, source="step 74 corrected: ss/110 C at 2.4 mA, 10 fF")
MARGIN = list(_m.values())


# ------------------------------------------------------------------------------------------------ step 77 (clock generator)
STEPS.append((77, "Clock generator: sampling clocks, hold pulse, Gm pulse", "done", "docs/design/step77_clkgen.md",
              "t_s 226 ps, gaps 186/182 ps (>= 115), W_H 2.15 ns (>= 1.51), tau 202 ps (106-408, tau*K_VCO x0.86-1.21), "
              "t_p 2.63 ns (<= 4.30), jitter 0.15 ps (-163.4 dBc/Hz), 78 uW; 4 cells LVS-clean"))
METHODS += [
 ("M17", "Transient-noise jitter of a logic path with per-node noise currents", "77",
  "rms jitter added by a chain of CMOS gates to an edge (the sampling edge cks), and its phase-noise floor at f_ref",
  "ngspice has no device noise in transient; a gate is noisy only while it switches (around its trip point), so a "
  "white current of the trip-point density at every node gives a simple, slightly pessimistic estimate",
  ".noise on each inverter size at V_M -> S_i; flat netlist with trnoise(NA 1p 0 0) at every node, NA = sqrt(S_i/(2 NT)); "
  "noiseless 500 MHz input, 120+ edges, edges paired within 0.6 ns, 4th-order detrend; baseline with NA x 1e-6",
  "ONLY_JITTER=1 design/clkgen/step77_sim.py; tb/clkgen/tb_clkgen_jitter.spice + tb/edges.py --fall --col 3",
  "white only; trip-point density during the whole run is pessimistic; 120 edges -> +-7 %; cross-check: Spectre "
  "transient noise or pss + pnoise"),
]
DEVICES += [
 ("Clock generator", "INVS n / p", "nfet_01v8 / pfet_01v8", "0.42 / 0.84", 1, 0.15, "gap and pulser inverters"),
 ("Clock generator", "INVM n / p", "nfet_01v8 / pfet_01v8", "1 / 2", 1, 0.15, "refclk buffer, driver middle stage"),
 ("Clock generator", "INVL n / p", "nfet_01v8 / pfet_01v8", "2 / 4", 2, 0.15, "driver outputs (4 / 8 um)"),
 ("Clock generator", "NOR2 n / p", "nfet_01v8 / pfet_01v8", "0.84 / 1.68", 1, 0.15, "pulser gate"),
 ("Clock generator", "R_H", "res_xhigh_po_0p35", 0.35, 1, 6.0, "34.9 kOhm, hold pulse"),
 ("Clock generator", "C_H", "cap_mim_m3_1", 6, 1, 6, "76 fF, hold pulse"),
 ("Clock generator", "R_G", "res_xhigh_po_0p35", 0.35, 1, 0.5, "3.48 kOhm (minimum length), Gm pulse"),
 ("Clock generator", "C_G", "cap_mim_m3_1", 3.5, 1, 3.5, "27 fF, Gm pulse"),
]
PROBLEMS += [
 (77, "timing", "Gm pulse width tau far outside +-25 % over PVT", "first RC-dominated pulser: xhigh_po TC -19 % over "
  "-40..110 C plus R/C corners; final tau 106 (ff_ll 110 C) - 408 ps (ss_hh -40 C)",
  "tau = ln2 RC + gate delays; both depend on process and temperature",
  "R at minimum length so gates set most of tau; gate delay tracks the ring VCO, so tau*K_VCO stays x0.86-1.21; "
  "requirement re-allocated to beta*K_VCO, final check in step 79", "accepted (requirement moved to step 79)"),
 (77, "corners", "Plain ss/ff corners miss the RC extremes", "tau worst cases appeared only in ss_hh / ff_ll / hl / lh",
  "the ss/ff library sections keep R and C typical", "use the combined MOS + R/C corners for every RC-timed block "
  "(also to revisit for the REF buffer and CCO passives)", "fixed (method)"),
 (77, "method", "Jitter first came out 1.17 ps", "transient-noise run of the sampling path",
  "edge mis-pairing plus a slow numerical drift of the edge times (~1.2 ps, also with noise x 1e-6)",
  "pair each output edge with its input edge within 0.6 ns, 4th-order detrend, noiseless baseline: 0.152 ps", "fixed"),
 (77, "timing", "Hold-pulse width depends on refclk duty", "W_H 2.22 ns at 35 %, 1.95 ns at 65 % duty",
  "the RC node is not fully reset during a short low phase", "accepted (>= 1.5 ns); a reset nMOS on the RC node would remove it",
  "accepted"),
 (77, "testbench", "Jitter deck stops with 'timestep too small' near 251 ns (seed 1)", "tb_clkgen_jitter.spice",
  "random 1 ps noise steps on the source branch", "run 248 ns (122 edges) or change the seed", "fixed"),
]
RESULTS += [
 ("Clock gen t_p (sample -> Gm pulse centre), worst", 4.30, 5.0, "ns", "max", 77, "ss_hh -40 C 1.71 V; tt 2.63 ns"),
 ("Clock gen hold pulse W_H, worst", 1.51, 1.5, "ns", "min", 77, "ff_ll 110 C; tt 2.15 ns"),
 ("Clock gen non-overlap gap, worst", 115, 100, "ps", "min", 77, "ff -40 C; tt 186 / 182 ps"),
 ("Clock gen Gm pulse tau, tt", 202, 200, "ps", "info", 77, "106-408 ps over PVT; tau*K_VCO x0.86-1.21"),
 ("Clock gen sampling-edge jitter", 0.152, None, "ps", "info", 77, "M17; floor -163.4 dBc/Hz"),
 ("Clock gen phase-noise floor at 50 MHz", -163.4, -160, "dBc/Hz", "max", 77, "allocation -160"),
 ("Clock gen power, worst", 0.108, 0.216, "mW", "max", 77, "tt 78 uW; allocation SSPD + clock gen 0.12 mA x 1.8 V"),
]
_set("RMS jitter, FFNC on", "typ, 10 kHz-40 MHz", 1.254, source="steps 74-77 simulated (REF 3.3 V pp); 1.327 ps at 1 V pp")
_set("RMS jitter, FFNC off", "typ", 1.963, source="steps 74-77 simulated (REF 3.3 V pp)")
_set("Phase noise 300 kHz, FFNC off", "typ", -110.9, source="steps 74-77 simulated (REF 3.3 V pp)")
_set("Phase noise 300 kHz, FFNC on", "typ", -121.0, source="steps 74-77 simulated (REF 3.3 V pp); -118.4 at 1 V pp")
_set("Jitter FoM", "typ", -228.5, source="1.254 ps, 8.91 mW")
MARGIN = list(_m.values())


# ------------------------------------------------------------------------------------------------ step 78 (SSPD) + step-77 revision
STEPS = [s if s[0] != 77 else (77, s[1], "done (revised in step 78)", s[3],
         "order sample -> Gm -> hold (hold-trigger latch); t_s 228 ps, gaps 171/318 ps (>= 110), tau 200 ps (106-405), "
         "W_H 2.16 ns (>= 1.51), t_p 0.28 ns (<= 0.50), jitter 0.15 ps (-163.4 dBc/Hz), 82 uW; 5 cells LVS-clean") for s in STEPS]
STEPS.append((78, "SSPD with hold: sampler, dummy sampler, isolation buffers", "done", "docs/design/step78_sspd.md",
              "A 0.514 V/rad (0.35-0.77 over MOS+R/C corners, +-1.5 % over temperature), alpha 0.473, kick <= 2.3 fs "
              "(spur <= -134 dBc), dummy: f_ref supply current 0.76 vs 42 uA, buffer jitter 0.080 ps, 0.47 mW; LVS-clean"))
METHODS += [
 ("M18", "Beat-frequency characteristic of a sampling phase detector", "78",
  "the sampled characteristic v1(phi) over a whole VCO cycle, the detector gain A at the lock point, the hold memory "
  "alpha, the sample common mode and the power, in one transient",
  "a phase sweep would need one run per phase; with the VCO at (32 + 1/nb) f_ref the sampling phase slides by 2 pi/nb "
  "each reference period, so nb + 2 periods cover the characteristic with the real clock generator and switches",
  "VCO = ideal squares behind an acbuf-like inverter, starting at t = 0; each cks falling edge is a sample with phase "
  "2 pi f_vco t mod 2 pi; v1 read mid-Gm-pulse, v2 after the hold; line fit within +-0.35 rad of the rising zero "
  "crossing (taken modulo 2 pi) gives 2A; least squares v2[k] = a v1[k] + b v2[k-1] gives alpha = b",
  "design/sspd/sspd.py characteristic(), step78_sim.py; tb/sspd/tb_sspd_char.spice + tb/sspd_char.py",
  "32 points per cycle (+-0.1 rad resolution); the ideal VCO has no noise; the Gm and NCB inputs are capacitor "
  "placeholders until steps 79/82"),
 ("M19", "Kick-back by differential transient (switching vs not switching)", "78",
  "the disturbance the sampler puts on the VCO output: clkp edge shift, a reference-spur estimate, the voltage "
  "glitch, and the supply-current component at f_ref (with and without the dummy sampler)",
  "the effect is femtoseconds, far below any absolute accuracy of a transient; the difference of two runs on the same "
  "time grid that differ only in the switching cancels everything else",
  "locked frequency 32 f_ref, VCO phase near the lock point; run a: clock generator on; run b: refclk = 0 (sampler "
  "tracks); clkp edge times a - b -> phase 2 pi f0 dt -> Fourier component at f_ref -> 20 log(a1/2) dBc",
  "design/sspd/sspd.py kick(), step78_extra.py; tb/sspd/tb_sspd_kick.spice + tb/sspd_kick.py",
  "VCO output modelled by an ideal source behind a driver (the ring and acbuf would attenuate it further); one "
  "operating point"),
]
DEVICES += [
 ("SSPD side", "XB1 n / p", "nfet_01v8 / pfet_01v8", "0.42 / 0.84", 1, 0.15, "isolation buffer input"),
 ("SSPD side", "XB2 n / p", "nfet_01v8 / pfet_01v8", "2 / 4", 1, 0.15, "drives R_s + C"),
 ("SSPD side", "XRS", "res_xhigh_po_0p69", 0.69, 1, 0.6, "R_s 2.16 kOhm"),
 ("SSPD tg", "XN / XP", "nfet_01v8_lvt / pfet_01v8", "3 / 1.5", 1, 0.15, "sampling and dummy TG"),
 ("SSPD tgh", "XN / XP", "nfet_01v8_lvt / pfet_01v8", "1 / 1", 1, 0.15, "hold TG"),
 ("SSPD side", "XC1, XC2", "cap_mim_m3_1", 4, 1, 4, "34.7 fF each"),
 ("SSPD side", "XCD", "cap_mim_m3_1", 4.35, 1, 4.35, "40.7 fF dummy = C1 + Gm input"),
 ("Clock generator", "hlatch NOR x3", "nfet_01v8 / pfet_01v8", "0.84 / 1.68", 1, 0.15, "hold trigger latch (step 78)"),
]
PROBLEMS += [
 (78, "loop", "Charge-sharing pole inside the loop", "the Gm read C2 (after the hold transfer) in the step-77 order",
  "v2[k] = (1 - alpha) v1[k] + alpha v2[k-1], alpha ~ 0.5: pole z = 0.5, 16 deg lag at f_c = f_ref/20; not in step 73",
  "clock order changed to sample -> Gm (reads C1) -> hold; t_p 2.63 -> 0.28 ns (+~1.5 deg PM)", "fixed (step 77 revised)"),
 (77, "timing", "Hold pulser did not fire after the reorder", "no ckh pulse when triggered by the end of the 200 ps Gm pulse",
  "the 2.6 ns RC node is reset only while the pulser input is low: 200 ps is not enough",
  "NOR latch set by ckg, reset while cks = 1: its output stays high until refclk falls, RC reset ~10 ns", "fixed"),
 (77, "simulation", "ngspice aborted (timestep too small) with tr = 410 ps", "refclk source breakpoint at exactly 15 ns",
  "PWL/pulse corner coinciding with the KLU solver step control", "retry with tran 2p when the run ends early", "fixed"),
 (78, "power", "SSPD power above the step-72 allocation", "0.47 mW (0.26 mA) vs 0.12 mA for SSPD + clock generator",
  "the buffer must swing ~46 fF per side at 1.6 GHz (C dV f) plus its own capacitance; dummy keeps it constant",
  "C1 100 -> 35 fF (0.70 -> 0.47 mW, kT/C still negligible); further options: 20 fF, re-balance with measured acbuf "
  "currents, NCB current", "open - power review after step 82"),
 (78, "method", "Negative A at the ss corners", "fit gave A = -0.34 at ss/110 C",
  "the rising zero crossing straddled 2 pi in the sorted phases", "phase difference taken modulo 2 pi", "fixed"),
 (78, "budget", "Renamed budget key double-counted the reference", "jitter 1.254 -> 1.293 ps after adding the SSPD term",
  "system() overwrites the step-72 allocation by its key; a new name kept the placeholder too",
  "keep the allocation key; SSPD buffer term added inside it", "fixed"),
 (78, "spread", "A follows the R/C corner", "0.352 (ss_hh) to 0.771 V (ff_ll)", "A = VDD/(2 w0 R_s C1)",
  "within icp_trim (A tau K_VCO x0.69-1.41); temperature drift only +-1.5 %", "accepted (trim)"),
]
RESULTS = [r for r in RESULTS if not r[0].startswith("Clock gen t_p")]
RESULTS += [
 ("Clock gen t_p (sample -> Gm pulse centre), worst (revised order)", 0.50, 5.0, "ns", "max", 77, "tt 0.28 ns"),
 ("SSPD gain A, tt", 0.514, 0.5, "V/rad", "info", 78, "target 0.5"),
 ("SSPD gain A, worst (ss_hh -40 C)", 0.352, 0.35, "V/rad", "min", 78, "ff_ll 110 C: 0.771"),
 ("SSPD hold memory alpha", 0.473, None, "-", "info", 78, "C2/(C1 + C2)"),
 ("SSPD kick-back, clkp edge shift", 2.3, None, "fs", "info", 78, "spur estimate <= -134 dBc"),
 ("SSPD supply current at f_ref (with dummy)", 0.76, None, "uA", "info", 78, "42 uA without"),
 ("SSPD isolation-buffer jitter (differential)", 0.080, None, "ps", "info", 78, "-169.0 dBc/Hz at 50 MHz"),
 ("SSPD power, tt", 0.47, 0.216, "mW", "max", 78, "allocation (SSPD + clkgen 0.12 mA x 1.8 V); over - see power review"),
]
_set("RMS jitter, FFNC on", "typ, 10 kHz-40 MHz", 1.256, source="steps 74-78 simulated (REF 3.3 V pp); 1.329 ps at 1 V pp")
_set("RMS jitter, FFNC off", "typ", 1.964, source="steps 74-78 simulated (REF 3.3 V pp)")
_set("Phase noise 300 kHz, FFNC off", "typ", -110.9, source="steps 74-78 simulated (REF 3.3 V pp)")
_set("Phase noise 300 kHz, FFNC on", "typ", -120.9, source="steps 74-78 simulated (REF 3.3 V pp); -118.4 at 1 V pp")
_set("Power, FFNC on", "typ", 9.53, source="as before + SSPD 0.26 mA and clock gen 0.05 mA instead of 0.12 mA allocated (x 3.3 V)")
_set("Power, FFNC on", "max over PVT", 14.23, source="as before + SSPD 0.32 mA (ff_ll 110 C) and clock gen 0.06 mA (x 3.63 V)")
_set("Power, FFNC off", "typ", 8.08, source="as above minus NCB")
_set("Power, FFNC off", "max over PVT", 12.15, source="as above minus NCB")
_set("Jitter FoM", "typ", -228.2, source="1.256 ps, 9.53 mW")
MARGIN = list(_m.values())


# ------------------------------------------------------------------------------------------------ device-rule migration (18 Nov 2026)
STEPS.append(("M0", "Device-rule migration: 5 V analog devices, 1.8 V logic; VCO feasibility; 800 MHz decision", "done",
              "docs/design/hv_vco_feasibility.md, hv_devices.md, hv_output_divider.md",
              "ring in g5v0d10v5 reaches 1.07-1.10 GHz at ss 110 C (ring 2.6 V): 1.6 GHz infeasible; 800 MHz = 50 MHz x 16, "
              "3-stage pseudo-differential ring, no LDO, output divider /1/2/4/8/16; proposal and roadmap updated"))
PROBLEMS += [
 ("M0", "rule", "New rule: analog blocks only in nfet/pfet_g5v0d10v5; digital in 1.8 V devices",
  "organisers' guidance (Chipalooza chat): 3v3_nvt are native devices, the 5 V devices are the ones to use",
  "thick oxide (L >= 0.5 um): f_T ~11 GHz (n) / 3.8 GHz (p) at gm/Id = 10, vs 58 GHz for nfet_01v8",
  "VCO feasibility over 3 ring types; frequency lowered to 800 MHz; LDO dropped; level shifters at every domain "
  "crossing; steps 72-76 and 78 to be redone, 77 kept", "decided - migration in progress"),
 ("M0", "frequency", "1.6 GHz not reachable in 5 V devices", "loaded 3-stage ring: 1.07-1.10 GHz at ss 110 C, 1.37 GHz even at 3.0 V",
  "low g_m/C of thick-oxide devices; CCO headroom leaves 2.6 V for the ring at VDDA 3.0 V",
  "800 MHz with ring B (25 % margin at the worst corner); reduced-swing Maneatis ring tried and rejected (slower, 2-5x power)",
  "decided"),
]

# ------------------------------------------------------------------ step 72 redo: 800 MHz, 5 V analog devices (18 Nov 2026)
STEPS.append(("72-HV", "Budget redo for 800 MHz, N = 16, 5 V analog devices, no LDO", "done",
              "docs/design/step72_hv_budget.md, design/budget/step72_hv_budget.py, design/feas/hv_noise.py",
              "2.12 / 1.37 ps typ, 3.44 / 2.20 ps pess (FFNC off / on); L(300k) -116.2 / -125.8 typ; 9.13 mW, "
              "FoM -227.7 dB; 0.060 mm2; new targets K_vdd <= 5 MHz/V, K_s <= 104 ps/V, VDDA <= 100 nV/rtHz; "
              "proposal targets 1.6 / 2.6 ps typ, 3.2 / 5.0 ps max"))
METHODS += [
 ("M20", "Device noise at fixed g_m/I_D (ngspice .noise on one transistor)", "72-HV",
  "thermal-noise factor gamma = S_id/(4kT g_m), the 1/f corner frequency and the gate-referred flicker voltage of "
  "each device type and length, at the same operating point",
  "a fair comparison of device families must hold g_m/I_D and the current fixed - then the width follows from the "
  "current density, and every difference left is the device's own noise",
  "one dc sweep of V_GS on a 10 um device -> g_m/I_D = d ln I_D / dV_GS; pick V_GS where it equals 10 (searching past "
  "the leakage region); scale W to 100 uA (split into fingers <= 40 um); .noise from 100 Hz to 1 GHz with the drain "
  "current read through a CCVS; gamma from the 1 GHz value, corner where the PSD is twice the thermal floor",
  "python3 design/feas/hv_noise.py -> design/feas/hv_noise.json",
  "tt, 27 C, one V_DS; SKY130 flicker parameters are binned by length, so the corner must be measured per L used"),
]
PROBLEMS += [
 ("72-HV", "simulation setup", "device-noise sweep took > 10 min and was killed", "timeout after 600 s",
  "one ngspice launch (with the full PDK load) per V_GS point: 75 x 8 runs",
  "one dc sweep per device instead of one .op per point: 2 runs per device, 1 min in total", "fixed"),
 ("72-HV", "simulation setup", "wrong operating point for the 5 V pMOS at L = 1 um (g_m/I_D = 2 instead of 10)",
  "g_m 0.21 mS at 100 uA; then an empty noise output",
  "the search took the first V_GS with g_m/I_D < 10, which for a high-V_T device is inside the leakage region at "
  "V_GS = 0.3 V; after fixing that, W = 115 um is beyond the model bins",
  "search only above the g_m/I_D peak; sweep V_GS to 3.0 V for 5 V devices; split W into m fingers <= 40 um", "fixed"),
 ("72-HV", "supply", "no LDO: VDDA noise reaches the ring and the NCB", "budget term up to 1.17 ps (pess, FFNC off)",
  "the ring is current-fed, but the CCO output impedance is finite (K_vdd); the NCB delay depends on VDDA (K_s)",
  "targets K_vdd <= 5 MHz/V (cascoded CCO, L >= 1 um) and K_s <= 104 ps/V; low-noise VDDA regulator in the test plan",
  "open - verified in steps 74/75/80"),
]
RESULTS += [
 ("Jitter FFNC on, typ (budget, 800 MHz)", 1.37, 1.6, "ps", "max", "72-HV", "5 V devices, no LDO"),
 ("Jitter FFNC off, typ (budget, 800 MHz)", 2.12, 2.6, "ps", "max", "72-HV", ""),
 ("Jitter FFNC on, pess (budget, 800 MHz)", 2.20, 3.2, "ps", "max", "72-HV", ""),
 ("Jitter FFNC off, pess (budget, 800 MHz)", 3.44, 5.0, "ps", "max", "72-HV", ""),
 ("L(300 kHz) FFNC on, typ (800 MHz)", -125.8, -124, "dBc/Hz", "max", "72-HV", ""),
 ("L(300 kHz) FFNC off, typ (800 MHz)", -116.2, -114, "dBc/Hz", "max", "72-HV", ""),
 ("Power FFNC on, typ (800 MHz)", 9.13, 9.15, "mW", "max", "72-HV", "spec typ 9.1 is this value rounded"),
 ("Power FFNC on, worst (800 MHz)", 13.53, 15, "mW", "max", "72-HV", ""),
 ("Area (800 MHz, 5 V)", 0.060, 0.10, "mm2", "max", "72-HV", ""),
]

# ------------------------------------------------------------------ step 73 redo: loop for 800 MHz, 5 V devices (18 Nov 2026)
STEPS.append(("73-HV", "Loop parameters for 800 MHz with 5 V devices (thick-oxide C1)", "done",
              "docs/design/step73_hv_loop.md, design/loop/step73_hv_loop.py, design/loop/spice/run_cv_hv.sh",
              "f_c 2.50 MHz, PM 50.0 (t_p 0.5 ns); beta 0.911 uA/rad, g_m 3 x 19.0 uS; R1 20.6 kOhm, C1 8.81 pF (2 tiles of "
              "9 x nfet_g5v0d10v5 + MIM), C2 1.236 pF; V_cont 1.0-2.3 V; ~3800 um2; jitter 2.14 / 1.37 ps typ, 3.45 / 2.20 "
              "pess; residual m 0.75-1.3: PM 46.5-50.6 deg; proposal unchanged"))
PROBLEMS += [
 ("73-HV", "device rule", "loop-filter MOS cap must be thick-oxide: 2.6x less capacitance per area",
  "nfet_g5v0d10v5 C-V: 2.87 fF/um2 at 1.65 V vs 7.48 for nfet_01v8; flat only above 1.0 V",
  "C_ox = eps/t_ox with a 2.5-3x thicker gate oxide; higher V_T",
  "keep the loop, scale beta and C by the same factor (2 tiles of 4.41 pF, beta 0.911 uA/rad, R1 20.6 kOhm: +0.013 ps); "
  "V_cont window moved to 1.0-2.3 V; MIM2 stacking kept as an option if met5 is allowed", "decided"),
]
RESULTS += [
 ("Loop f_c (800 MHz design)", 2.50, 2.5, "MHz", "max", "73-HV", "sampled loop, t_p 0.5 ns"),
 ("Loop PM (800 MHz, sampled)", 50.0, 45, "deg", "min", "73-HV", ""),
 ("Loop PM, residual m 0.75-1.3, all R/C corners", 46.5, 45, "deg", "min", "73-HV", ""),
 ("Loop-filter area (800 MHz, 5 V)", 3789, 5000, "um2", "max", "73-HV", "CP + LF budget 5000 um2"),
 ("Phase-step settling to +-10 ps (800 MHz)", 0.40, 5, "us", "max", "73-HV", "lock-time typ 5 us"),
]
