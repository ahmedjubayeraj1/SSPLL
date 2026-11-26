"""www.py - explicit What / How / Why blocks for the steps whose main text is organised differently
(lab steps, tables, procedures). nb.Book.step() inserts them right after the step title."""

WWW = {
33: ("Two edges arrive at the PFD; one output (UP or DN) goes high at the first edge and both reset shortly after the second, "
     "so the pulse width equals the time difference.",
     "Two D flip-flops with D = 1 are clocked by REF and DIV; an AND gate detects UP·DN = 1 and resets both after $t_{rst}$. "
     "$t_{UP} = \\frac{\\Delta\\phi}{2\\pi}T_{REF}$ (linear over ±2π). With unequal frequencies extra edges of the faster input find "
     "the PFD already set, so one output stays high most of the time.",
     "Because the PFD stores *which edge came first*, its average output keeps the sign of a frequency error — that is why a CP-PLL "
     "pulls in over the whole VCO range. The dead zone appears because the charge-pump switches need a minimum pulse to turn on; "
     "the reset delay is the cure."),
35: ("With a series R1 the CP-PLL becomes a stable second-order loop whose closed-loop response has a zero, so it peaks "
     "(|H| > 1) near ω_n and overshoots in the step response even when ζ ≥ 1.",
     "Write $G = \\frac{I_pK_{VCO}}{2\\pi NC_1}\\frac{1+sR_1C_1}{s^2}$, close the loop $H/N = G/(1+G)$ and match the denominator to "
     "$s^2+2\\zeta\\omega_ns+\\omega_n^2$: $\\omega_n^2 = I_pK_{VCO}/(2\\pi NC_1)$, $2\\zeta\\omega_n = I_pK_{VCO}R_1/(2\\pi N)$. The numerator "
     "$2\\zeta\\omega_ns+\\omega_n^2$ is the closed-loop zero.",
     "The zero comes from R1's proportional path: it adds phase (stability) but also lets the input pass with gain above 1 near "
     "ω_n. Both ω_n and ζ grow with √(I_p K_VCO), so PVT spread of K_VCO moves bandwidth and damping together."),
38: ("We turn the theory of steps 34–37 into real component values for the simulated Type-II baseline: f_REF = 50 MHz, N = 32, "
     "f_c = 2.5 MHz, PM = 60°.",
     "Pick f_c and PM → b = tan(45° + PM/2) → C_1/C_2 = b² − 1 → crossover condition gives C_tot = b·I_p·K_VCO/(2πNω_c²) → "
     "C_2 = C_tot/b², C_1 = C_tot − C_2, R_1 = b/(ω_cC_1) → convert to SKY130 geometry (xhigh-poly length, MIM/MOS-cap area).",
     "A design is only real when every element is legal in the PDK and survives the R/C corners; doing the arithmetic once by "
     "hand shows which knob (I_p) trades area against noise, and that the ripple step I_pR_1 is fixed by the loop itself."),
41: ("Changing the loop bandwidth moves four things at once: VCO-noise suppression, ×N² in-band noise, reference spurs, and "
     "filter area (plus the dead zone handled by the reset delay).",
     "Wider f_c: the high-pass 1/(1+G) suppresses more VCO noise, the low-pass NG/(1+G) passes more in-band noise, smaller "
     "capacitors (C_tot ∝ 1/f_c²) raise |Z(jω_REF)| and therefore the spur, and the sampling delay costs 180°·f_c/f_REF of PM.",
     "Every term pulls the optimum in a different direction, so there is no free lunch: a ring-VCO CP-PLL ends up limited by its "
     "in-band floor and spurs, which is the case for the SSPLL."),
42: ("Three circuit fixes remove the CP-PLL's own error sources: the PFD dead zone, UP/DN current mismatch over V_cont, and "
     "charge sharing when switches close.",
     "Reset delay keeps both outputs on for $t_{rst} > t_{on}$; a replica branch with an op-amp forces the replica drain to $V_{cont}$ "
     "and servo-matches UP and DN (mismatch ÷ (1 + A)); current steering into a dump node held at $V_{cont}$ by a unity-gain buffer "
     "keeps internal nodes from drifting to the rails.",
     "Each error is periodic at f_REF, so each one becomes a reference spur or a static phase offset; fixing them at the source is "
     "cheaper than filtering them later with a narrower loop."),
43: ("Further fixes act on the filter (sampled loop filter), on the calibration (trim the CP), or on the detector itself "
     "(a detector whose gain does not shrink with N).",
     "A sampled filter updates $V_{cont}$ only after the CP pulse has settled, so the VCO never sees the $I_pR_1$ spike; calibration "
     "measures the static offset and trims a current source; a sub-sampling detector measures VCO phase directly with gain A per "
     "VCO radian instead of $I_p/(2\\pi N)$.",
     "The last idea removes the root cause (the N² penalty on detector noise) instead of treating symptoms — the bridge to Phase 4."),
44: ("For a ring VCO the jitter-optimal bandwidth slides to wider values and lower jitter as the in-band noise floor drops.",
     "The total jitter is the integral of in-band noise × |NG/(1+G)|² plus VCO noise × |1/(1+G)|²; lowering the in-band term lets "
     "the crossover move up until the stability/spur limit (~f_REF/20 for an SSPLL) is reached.",
     "A CP-PLL can only lower its floor with more current or a higher f_REF; the SSPLL removes ~20 dB at once, and beyond the "
     "bandwidth wall only feedforward cancellation can help."),
45: ("A behavioural CP-PLL is hit with a 200 MHz output-frequency step: a wide loop tracks it linearly, a narrow loop saturates "
     "the PFD and slews.",
     "The cycle-by-cycle simulator computes the PFD error each reference period; when |Δφ| ≥ 2π the PFD stays in one state and the "
     "CP delivers its maximum average current, so $V_{cont}$ ramps at ≈ $I_p/C_{tot}$ until the error is back inside the linear range.",
     "Lock time and acquisition behaviour depend on loop bandwidth and frequency error, not only on the linear step response — "
     "why the lock-time spec starts with the coarse code already set."),
50: ("The held SSPD voltage drives a transconductor that is connected to the loop filter only for a short pulse τ per "
     "reference period.",
     "Average current $= g_m\\cdot2A\\sin\\Delta\\phi\\cdot\\tau/T_{REF}$, so $\\beta = 2Ag_m\\tau/T_{REF}$; the filter scales as "
     "$C_{tot} = b\\beta K_{VCO}/\\omega_c^2$; outside the pulse the current is steered to a dump node at $V_{cont}$.",
     "The SSPD gain is so large that a continuous Gm would need nanofarads of filter capacitance; pulsing is the cheapest way to "
     "reduce β — but gated noise power scales with duty while signal scales with duty², so noise grows as T/τ."),
51: ("The SSPD output changes only once per reference period and is passed through a second (hold) capacitor, so the loop sees "
     "extra phase lag.",
     "Zero-order hold: $(1-e^{-sT})/(sT)$ = sinc magnitude and a T/2 delay. Charge sharing: "
     "$H(z) = (1-\\alpha)/(1-\\alpha z^{-1})$, $\\alpha = C_h/(C_s+C_h)$. Their phase adds to the loop's at the crossover.",
     "That lag eats phase margin (9° from the hold alone at f_REF/20, 25° with equal caps) and limits the FFNC bandwidth later; "
     "the loop filter must be designed with it included."),
52: ("Started off-frequency, the SSPD loop locks to whichever harmonic k·f_REF is nearest; with a dead-zone FLL it always "
     "ends at 32·f_REF.",
     "The SSPD samples the VCO phase mod 2π at each REF edge, so every k·f_REF gives a constant sample. The FLL's PFD compares REF with "
     "VCO/32, saturates while the frequency is wrong (pulls it in), and goes silent once its phase error is inside the dead zone.",
     "The SSPD trades frequency detection for low noise; a separate acquisition loop that switches itself off restores robustness "
     "without bringing back its noise."),
53: ("Compared with the Type-II CP-PLL at the same bandwidth, the SSPLL lowers in-band noise, removes the divider from the loop, "
     "and makes FFNC possible.",
     "The SSPD measures VCO phase directly (gain A per VCO radian), so detector noise is not ×N²; at lock the sample is ~0, so the "
     "pulsed Gm injects almost no current (no mismatch spurs); the held sample is a voltage proportional to each edge's timing error.",
     "With a ring VCO the jitter gain from the SSPLL alone is modest (2.52 → 2.29 ps) because the ring dominates; the decisive "
     "benefit is that it enables FFNC (→ 1.40 ps)."),
54: ("After a disturbance larger than its capture range, an SSPLL either relocks to a wrong harmonic (no FLL) or relocks "
     "slowly (FLL), and a too-narrow FLL dead zone makes the two loops fight.",
     "The FLL acts only after its divided phase error leaves the dead zone; it then pulls the frequency back and hands over again. "
     "If the SSPD's lock point lies just outside the dead zone, the FLL keeps pushing and the SSPD keeps slipping — a limit cycle.",
     "Low noise comes from a detector without frequency information; robustness must be added back carefully (dead-zone width, "
     "FLL strength) or with smarter detectors (Hsu's PFD + auxiliary SSPD, Geng's quadrature SSPD)."),
55: ("The sampler disturbs the VCO once per reference period, creating spurs; meanwhile reference noise is still ×N² and ring "
     "noise beyond f_c is untouched.",
     "Load modulation: ΔC on a ring node for a fraction d of the period changes f by f_0·ΔC/ΣC → phase modulation "
     "β = 2δf·sin(πd)/(πf_REF) → spur 20 log(β/2). Kickback and charge sharing add charge to the node each period.",
     "Because β scales with f_0/f_REF = 32, femtofarads matter: isolation buffers and dummy samplers are mandatory, and FFNC is the "
     "only tool left for the ring noise beyond the loop bandwidth."),
56: ("The SSPD's gain is not constant: it falls with phase error, becomes negative beyond ±π/2, and depends on the VCO amplitude "
     "(supply, corner, temperature).",
     "The sample is $A\\sin\\Delta\\phi$, so the local gain is $A\\cos\\Delta\\phi$; for a ring the slope is the slew rate at the crossing, "
     "which follows the ring's swing and therefore its supply.",
     "Large transients get weak correction (slow recovery, possible slips), and a changing amplitude shifts both loop bandwidth and "
     "the required NCB gain — one reason FFNC needs calibration."),
57: ("Each SSPLL limitation has a known remedy; the table maps them to the blocks and controls of our proposal.",
     "Acquisition → FLL (or PFD+aux SSPD / QSSPD); spurs → isolation buffers, dummies, short tracking window, two-switch sampler; "
     "filter area → pulsed Gm; amplitude dependence → CCO supply and calibration; REF noise → low-noise receiver; ring noise → FFNC.",
     "Knowing which fix belongs to which problem is how you defend an architecture in a review: every block in the proposal exists "
     "because of one row of this table."),
58: ("The full behavioural SSPLL locks from several coarse errors; every waveform (frequency, SSPD sample, FLL activity, V_cont) "
     "tells a part of the lock story.",
     "FLL ramps the frequency while saturated, the SSPD sample beats until the frequency is close, the FLL goes silent in its dead "
     "zone, and V_cont settles at −offset·f_REF/K_VCO.",
     "Reading these waveforms is exactly what you will do on the transistor-level lock benches of Phase 8; the behavioural run gives "
     "the expected shapes and numbers to compare against."),
63: ("We turn the cancellation condition into numbers for our 1.6 GHz NCB: gain, range, trim span, noise, supply and power.",
     "$G_{t,NCB} = 1/K_{t,SSPD} = 1/(A\\cdot2\\pi f_0)$: 117 fs/mV for A = 0.85 V, 199 fs/mV for A = 0.5 V; range ±10 ps ≈ ±4σ of the "
     "residual jitter; trim 0.6–1.5× in 16 codes; noise floor ≤ −150 dBc/Hz (≈126 fs per edge).",
     "The NCB's output goes straight to the clock with nothing after it to correct errors, so its gain must be right (trim) and its "
     "noise and supply sensitivity small (LDO rail)."),
64: ("Two SKY130 current-starved cells with a 4-bit capacitor bank are simulated in ngspice: delay versus V_ctrl for several codes.",
     "Transient simulations with `.meas` give the delay at each V_ctrl; the local gain is the slope; the code adds 0.5 fF steps "
     "and scales the gain (130 → 345 fs/mV at 1.3 V).",
     "Real device models show what the square law hides: strong non-linearity near threshold and how much range and gain a simple "
     "cell really gives — the starting point for the Phase 7 NCB design."),
66: ("Each output edge's timing error after FFNC is (1 − G_tK_t) times the VCO's error at the sampling instant.",
     "The SSPD turns the VCO edge error ΔT into $v = K_t\\Delta T$; the NCB delays the edge by $-G_tv$; so "
     "$\\Delta T_{out} = (1-G_tK_t)\\Delta T$. The sample is held for 32 VCO edges, during which the VCO keeps wandering.",
     "G_t = 1/K_t removes the error at the sample but not the drift between samples — the time-domain picture of the hold's "
     "bandwidth limit."),
69: ("After cancellation, some noise sources disappear from the output and others do not.",
     "Every source gets two transfer functions (to out1 and out2). Sources that perturb the VCO after the comparison point (VCO, "
     "loop-filter R, supply) are multiplied by (1 − G_can); sources entering through the SSPD (SSPD, REF) are passed on; the NCB adds "
     "with transfer 1.",
     "The SSPD can only measure what happens to the VCO relative to the reference; it cannot tell its own noise or reference "
     "noise from a real error, and it never sees the NCB."),
70: ("The sampler folds VCO noise from around multiples of f_REF into the band that FFNC corrects; FFNC also cancels the "
     "loop-filter resistor's noise, which allows a 5× smaller C1.",
     "Detected spectrum $S_s(f) = f_{REF}\\sum_k S_\\phi(f-kf_{REF})$ (Thijssen): aliases pass through $|G_{can}|^2$ into out2. "
     "R1 noise enters at the VCO input, so it is multiplied by (1 − G_can); for a fixed zero 1/(R_1C_1), a 5× larger R1 allows 5× "
     "smaller C1.",
     "Aliasing sets a floor on what FFNC can achieve (small for our ring); the R1 argument turns noise cancellation into area "
     "saving (Nagam: 50 pF → 10 pF with the same out2 noise)."),
71: ("A 50 kHz tone on the VCO supply is cancelled imperfectly; the residual tone at out2 is measured and the NCB gain code that "
     "minimises it is kept.",
     "Residual ∝ |1 − G_can(F_cal)|·|1/(1+LG)|; at 50 kHz the path phase is ~0, so the residue measures gain error only; correlation "
     "with the injected tone extracts it from noise; sweep (or sign-step with cal_out) the 16 codes.",
     "Best tone cancellation and best noise cancellation need the same condition (G_t = 1/K_t), so a simple foreground tone test "
     "sets the noise canceller correctly."),
}
