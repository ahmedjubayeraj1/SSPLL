"""v2_eq.py - version-2 "Reading the equation" boxes for the learning notebooks.

Every display equation of the version-1 notebooks gets a box right after the paragraph that contains it:
a table of every symbol (meaning, unit, value in our design), the equation in plain words, why it has this form, and a
worked number. EXPLAIN is a list of (key, box); the key is a piece of the equation's LaTeX that identifies it (the
first matching key wins, so more specific keys come first). nb.py reports any display equation without a box."""


def E(rows, words, why="", num="", watch=""):
    t = ["<div style='border-left:4px solid #2a78d6;background:#f4f8fd;padding:10px 14px;margin:8px 0'>",
         "", "**Reading the equation**", "", "| Symbol | What it is | Unit | In our design |", "|---|---|---|---|"]
    t += [f"| {s} | {m} | {u} | {v} |" for s, m, u, v in rows]
    t += ["", f"**In words.** {words}"]
    if why:
        t += ["", f"**Why it looks like this.** {why}"]
    if num:
        t += ["", f"**Put numbers in.** {num}"]
    if watch:
        t += ["", f"**Watch out.** {watch}"]
    return "\n".join(t + ["", "</div>"])


EXPLAIN = [
# =============================================================================================== phase 1
("f_{out} = N\\,f_{REF} = 32", E(
    [("$f_{out}$", "output frequency of the PLL (the VCO frequency)", "Hz", "1.6 GHz"),
     ("$N$", "multiplication (division) ratio — how many VCO cycles fit in one reference cycle", "—", "32"),
     ("$f_{REF}$", "reference frequency from the crystal oscillator", "Hz", "50 MHz")],
    "When the loop is locked, the output makes exactly N cycles in every reference cycle.",
    "Locked means the phases track. If two phases track, their slopes — the frequencies — are equal. The loop "
    "compares $f_{out}/N$ (after the divider, or after sub-sampling) with $f_{REF}$, so $f_{out}/N = f_{REF}$.",
    "$32 \\times 50\\ \\text{MHz} = 1600\\ \\text{MHz}$. A 45 MHz crystal gives 1.44 GHz, a 55 MHz one 1.76 GHz — our "
    "required range.")),
("\\Delta v \\approx \\frac{dv}{dt}\\,\\delta t", E(
    [("$v(t) = A\\sin\\omega_{in}t$", "the signal being sampled (e.g. by an ADC)", "V", "—"),
     ("$A$", "signal amplitude (peak)", "V", "—"),
     ("$\\omega_{in} = 2\\pi f_{in}$", "angular frequency of the signal", "rad/s", "e.g. $2\\pi\\cdot100$ MHz"),
     ("$\\delta t$", "timing error of one sampling instant (jitter)", "s", "random, rms $\\sigma_t$"),
     ("$\\Delta v$", "voltage error caused by sampling at the wrong time", "V", "—"),
     ("$\\overline{\\Delta v^2}$", "mean-square voltage error (average over many samples)", "V²", "—"),
     ("$\\sigma_t$", "rms jitter of the sampling clock", "s", "1.4 ps (spec, FFNC on)")],
    "Sampling a little early or late gives a voltage error equal to the signal's slope times the time error.",
    "Near any instant a smooth signal looks like a straight line: $\\Delta v = \\text{slope}\\times\\Delta t$ (first "
    "term of a Taylor series). The slope of a sine is $A\\omega\\cos\\omega t$; the average of $\\cos^2$ is 1/2, which "
    "gives the factor 2 in the denominator.",
    "$A = 1$ V, $f_{in} = 100$ MHz, $\\sigma_t = 1.4$ ps: rms error $= 1\\cdot 2\\pi 10^8\\cdot1.4\\times10^{-12}/\\sqrt2 "
    "= 0.62$ mV.")),
("\\text{SNR}_{jitter} = -20\\log_{10}", E(
    [("$\\text{SNR}_{jitter}$", "best signal-to-noise ratio a sampler can reach with this clock", "dB", "61 dB at 100 MHz"),
     ("$f_{in}$", "frequency of the sampled signal", "Hz", "100 MHz (example)"),
     ("$\\sigma_t$", "rms clock jitter", "s", "1.4 ps"),
     ("$\\text{ENOB}$", "effective number of bits that SNR corresponds to", "bits", "9.9"),
     ("1.76, 6.02", "constants of an ideal N-bit quantizer: SNR = 6.02·N + 1.76 dB", "dB", "—")],
    "SNR = signal power / jitter-noise power = $1/(\\omega_{in}\\sigma_t)^2$, written in dB.",
    "Signal power is $A^2/2$, error power $A^2\\omega^2\\sigma_t^2/2$ (previous box): $A$ cancels, so the ceiling "
    "depends only on how fast the signal moves ($f_{in}$) and how uncertain the clock is ($\\sigma_t$). "
    "$10\\log(x^2) = 20\\log x$.",
    "$-20\\log(2\\pi\\cdot10^8\\cdot1.4\\times10^{-12}) = -20\\log(8.8\\times10^{-4}) = 61.1$ dB → "
    "$(61.1-1.76)/6.02 = 9.9$ bits.",
    "Halving the jitter gains 6 dB (one bit) — at every input frequency.")),
("\\omega(t) = \\frac{d\\phi}{dt}", E(
    [("$\\phi(t)$", "phase: the total angle the oscillator has turned through", "rad", "grows ~$2\\pi\\cdot1.6\\times10^9$ per second"),
     ("$\\omega(t)$", "instantaneous angular frequency", "rad/s", "$2\\pi\\cdot1.6$ GHz"),
     ("$\\tau$", "integration variable (past time)", "s", "—")],
    "Frequency is how fast the phase grows; phase is the sum (integral) of all past frequency.",
    "Like speed and distance: speed = d(distance)/dt and distance = ∫speed·dt. A frequency error that lasts for a "
    "while leaves a phase error that stays even after the frequency is corrected.",
    "A frequency 1 MHz too high for 1 µs adds $2\\pi\\cdot10^6\\cdot10^{-6} = 2\\pi$ rad — one full extra cycle.",
    "Because phase integrates frequency, a PLL (which controls phase) automatically controls frequency too.")),
("\\omega_{out} = \\omega_0 + K_{VCO}V_{cont}", E(
    [("$\\omega_{out}$", "VCO output angular frequency", "rad/s", "$2\\pi\\cdot1.6$ GHz"),
     ("$\\omega_0$", "frequency at $V_{cont} = 0$ (the intercept of the tuning line)", "rad/s", "—"),
     ("$K_{VCO}$", "VCO gain: frequency change per volt of control", "rad/s/V (or Hz/V ×2π)", "$2\\pi\\cdot(-326)$ MHz/V (fine tune)"),
     ("$V_{cont}$", "control voltage from the loop filter", "V", "0.7–1.2 V lock window")],
    "The VCO is a voltage-to-frequency converter: a straight line with slope $K_{VCO}$.",
    "Real VCOs are only roughly linear; this is the tangent line at the operating point. All loop dynamics use this "
    "slope.",
    "0.1 V more control voltage → $-326\\ \\text{MHz/V}\\times0.1 = -32.6$ MHz (our K_VCO is negative: more vtune, "
    "more capacitance, lower frequency).",
    "Units: datasheets give Hz/V; loop equations need rad/s/V — multiply by 2π.")),
("\\phi_{out}(t) = \\omega_0 t + K_{VCO}", E(
    [("$\\phi_{out}(t)$", "total output phase", "rad", "—"),
     ("$\\omega_0 t$", "phase the VCO would accumulate with zero control (the 'carrier' ramp)", "rad", "—"),
     ("$\\phi_{ex}(t)$", "excess phase: the part caused by the control voltage", "rad", "—"),
     ("$K_{VCO}\\int V_{cont}\\,dt$", "integral of the frequency change", "rad", "—")],
    "Output phase = a steady ramp + the integral of the control voltage times $K_{VCO}$.",
    "Integrate the VCO line $\\omega = \\omega_0 + K_{VCO}V_{cont}$ over time (phase = ∫ω dt). The ramp $\\omega_0t$ is "
    "the same for every waveform, so loop analysis tracks only $\\phi_{ex}$.",
    watch="This integral is why a VCO is an integrator in phase — the source of one pole at s = 0 in every PLL.")),
("\\frac{\\Phi_{ex}(s)}{V_{cont}(s)} = \\frac{K_{VCO}}{s}", E(
    [("$\\Phi_{ex}(s)$", "Laplace transform of the excess phase", "rad·s", "—"),
     ("$V_{cont}(s)$", "Laplace transform of the control voltage", "V·s", "—"),
     ("$s$", "Laplace variable; on the frequency axis $s = j\\omega$", "1/s", "—"),
     ("$K_{VCO}/s$", "transfer function of an ideal integrator with gain $K_{VCO}$", "rad/V", "—")],
    "In the Laplace domain integration is division by $s$, so the VCO's phase response is $K_{VCO}/s$.",
    "∫x dt ↔ X(s)/s. On the frequency axis $|K_{VCO}/j\\omega| = K_{VCO}/\\omega$: a slow wobble of $V_{cont}$ makes a "
    "big phase wobble, a fast one a small one, and the phase lags the voltage by 90°.",
    "A 1 mV sine at 1 MHz on $V_{cont}$: phase amplitude $= 2\\pi\\cdot326\\times10^6\\cdot10^{-3}/(2\\pi\\cdot10^6) = 0.33$ rad.")),
("\\overline{I} = \\frac{Q}{T_{REF}} = I_p", E(
    [("$\\overline{I}$", "charge-pump current averaged over one reference period", "A", "—"),
     ("$Q$", "charge delivered in one period", "C", "—"),
     ("$T_{REF}$", "reference period $= 1/f_{REF}$", "s", "20 ns"),
     ("$I_p$", "charge-pump current while it is on", "A", "—"),
     ("$\\Delta\\phi$", "phase error between reference and divided output", "rad", "—")],
    "The pump is on for the fraction Δφ/2π of each period, so its average current is $I_p$ times that fraction.",
    "On-time $= (\\Delta\\phi/2\\pi)T_{REF}$, charge $= I_p\\times$on-time, average = charge/period. This makes the "
    "PFD+CP gain $K_{PD} = I_p/2\\pi$ A/rad.",
    "$I_p = 100$ µA, $\\Delta\\phi = 0.1$ rad: $\\overline I = 100\\,\\mu\\text{A}\\cdot0.1/6.28 = 1.6$ µA.")),
("\\Delta V_{cont} = \\frac{\\Delta\\phi_0}{2\\pi}\\,T_{REF}", E(
    [("$\\Delta V_{cont}$", "step of the control voltage each reference period", "V", "—"),
     ("$\\Delta\\phi_0$", "a constant phase error", "rad", "—"),
     ("$I_p/C_1$", "slew rate of the capacitor voltage while the pump is on", "V/s", "—")],
    "A constant phase error charges the capacitor by the same amount every period, so $V_{cont}$ keeps ramping.",
    "$\\Delta V = Q/C_1$ with $Q = I_p\\cdot(\\Delta\\phi_0/2\\pi)T_{REF}$. A ramp that never stops is an integrator: "
    "the capacitor adds a second integrator to the loop (type II), which forces the steady-state phase error to zero.")),
("\\frac{V_{cont}(s)}{\\Delta\\Phi(s)} = \\frac{I_p}{2\\pi C_1 s}", E(
    [("$I_p/2\\pi$", "PFD + charge-pump gain", "A/rad", "—"),
     ("$1/(C_1 s)$", "impedance of the capacitor (current → voltage, integrating)", "Ω", "—")],
    "Phase error → current ($I_p/2\\pi$) → voltage on a capacitor ($1/sC_1$).",
    "Averaged over many periods the pump is a current source proportional to phase error, and a capacitor "
    "integrates current. The $1/s$ is the second integrator of a type-II loop.")),
("Z_1(s) = R_1 + \\frac{1}{sC_1}", E(
    [("$Z_1(s)$", "impedance of the series R–C branch of the loop filter", "Ω", "—"),
     ("$R_1$", "series resistor (sets the zero, i.e. the damping)", "Ω", "11 kΩ (step 73)"),
     ("$C_1$", "main integrating capacitor", "F", "17.1 pF"),
     ("$\\omega_z = 1/R_1C_1$", "zero frequency of the filter", "rad/s", "$2\\pi\\cdot0.85$ MHz")],
    "Current into a resistor in series with a capacitor: a proportional part ($R_1$) plus an integrating part ($1/sC_1$).",
    "With $C_1$ alone the loop is two integrators, phase −180°, and it oscillates. $R_1$ adds a voltage step that "
    "reacts *immediately* to the phase error (proportional path) — the zero at $1/R_1C_1$ gives back phase.",
    "$1/(2\\pi\\cdot11\\,\\text{k}\\Omega\\cdot17.1\\,\\text{pF}) = 0.85$ MHz.")),
("Z(s) = \\frac{1+sR_1C_1}{s(C_1+C_2)\\left(1+sR_1", E(
    [("$C_2$", "small capacitor in parallel that smooths the voltage steps of $R_1$", "F", "2.2 pF"),
     ("$C_1 + C_2$", "total capacitance seen at very low frequency", "F", "19.3 pF"),
     ("$\\omega_{p3}$", "third pole, where $C_2$ shorts $R_1$", "rad/s", "$2\\pi\\cdot7.4$ MHz"),
     ("$\\omega_z$", "zero", "rad/s", "$2\\pi\\cdot0.85$ MHz")],
    "The full second-order filter: integrator at DC, a zero that adds phase, and a pole at $\\omega_{p3}$ that rolls "
    "off the ripple.",
    "$Z = Z_1 \\parallel (1/sC_2)$. Multiply out the parallel combination and you get this form. Below $\\omega_z$ it "
    "is $1/s(C_1+C_2)$; between $\\omega_z$ and $\\omega_{p3}$ it is flat ≈ $R_1$; above $\\omega_{p3}$ it falls again.",
    "$\\omega_{p3}/\\omega_z = 1 + C_1/C_2 = 8.8$; the crossover $f_c = 2.5$ MHz sits between 0.85 and 7.4 MHz — "
    "close to their geometric mean, where the phase boost is largest.")),
("\\Phi_{div}(s) = \\frac{1}{N}\\Phi_{out}(s)", E(
    [("$\\Phi_{div}$", "phase at the divider output", "rad", "—"),
     ("$\\Phi_{out}$", "VCO phase", "rad", "—"),
     ("$N$", "division ratio", "—", "32")],
    "A divider by N turns every N cycles into one, so it divides phase (and its fluctuations) by N.",
    "One VCO cycle is 2π of VCO phase but only 2π/N of divided phase. Any phase step at the VCO appears N times "
    "smaller after the divider.")),
("G(s) = \\frac{K_{PD}\\,F(s)\\,K_{VCO}}{N\\,s}", E(
    [("$G(s)$", "open-loop gain: go once around the loop, cut open at the PD", "—", "$|G| = 1$ at $f_c = 2.5$ MHz"),
     ("$K_{PD}$", "phase-detector gain", "V/rad or A/rad", "$I_p/2\\pi$ for a CP"),
     ("$F(s)$", "loop-filter transfer (for a CP: the impedance Z(s))", "V/V or Ω", "—"),
     ("$K_{VCO}/s$", "VCO as phase integrator", "rad/V", "—"),
     ("$1/N$", "divider", "—", "1/32")],
    "Multiply the gains of every block around the loop: detector × filter × VCO × divider.",
    "The loop gain decides everything: where $|G| \\gg 1$ the output tracks the reference; where $|G| \\ll 1$ the "
    "loop does nothing and the VCO runs free.")),
("H(s) = \\frac{\\Phi_{out}}{\\Phi_{in}} = N\\frac{G(s)}{1+G(s)}", E(
    [("$H(s)$", "closed-loop transfer from reference phase to output phase", "—", "≈ N in band"),
     ("$\\Phi_{in}$", "reference phase", "rad", "—"),
     ("$\\Phi_e$", "phase error at the PD", "rad", "—"),
     ("$E(s)$", "error transfer function", "—", "→ 0 at DC (type II)")],
    "Output phase = N × reference phase where the loop gain is large, and nothing where it is small.",
    "Standard negative feedback: forward path $NG$, feedback $1/N$ → $NG/(1+G)$. When $|G| \\gg 1$, "
    "$G/(1+G) \\to 1$; when $|G| \\ll 1$, $\\to G \\to 0$. $E = 1/(1+G)$ is what is left uncorrected.",
    "Our loop at 100 kHz: $|G| \\approx 250$, so H/N ≈ 0.996 and E ≈ 0.004 (the reference is tracked). At 25 MHz: $|G| \\approx 0.03$, so H/N ≈ 0.03 (the VCO runs free).")),
# --------------------------------------------------------------------------------------------- phase 1 b
("PM = 180° + \\angle G(j\\omega_c)", E(
    [("$PM$", "phase margin", "degrees", "50° (step 73)"),
     ("$\\omega_c$", "crossover (unity-gain) frequency, where $|G| = 1$", "rad/s", "$2\\pi\\cdot2.5$ MHz"),
     ("$\\angle G$", "phase of the open-loop gain", "degrees", "−130° at $\\omega_c$")],
    "Phase margin is how far the loop phase is from −180° at the frequency where its gain is 1.",
    "At −180° and gain 1 the fed-back signal equals the input with inverted sign twice — it sustains itself: "
    "oscillation. The margin measures the distance from that point; small margin = ringing and peaking.",
    "−130° at crossover → PM = 50°: about 1.3 dB peaking and ~20 % step overshoot.")),
("\\angle G(j\\omega) = -180° + \\arctan", E(
    [("−180°", "the two integrators ($K_{VCO}/s$ and the capacitor's $1/s$)", "deg", "—"),
     ("$\\arctan(\\omega/\\omega_z)$", "phase added by the zero", "deg", "—"),
     ("$\\arctan(\\omega/\\omega_{p3})$", "phase taken away by the third pole", "deg", "—")],
    "Each integrator costs 90°, the zero gives back up to 90°, the extra pole takes some back.",
    "Phase of a product = sum of phases; $\\angle(1 + j\\omega/\\omega_z) = \\arctan(\\omega/\\omega_z)$.",
    "At 2.5 MHz: $-180 + \\arctan(2.5/0.85) - \\arctan(2.5/7.4) = -180 + 71 - 19 = -128°$ → PM ≈ 52°.")),
("PM_{max} = \\arctan b - \\arctan\\frac1b,\\qquad b^2", E(
    [("$b$", "spacing factor: $\\omega_c = b\\,\\omega_z = \\omega_{p3}/b$", "—", "≈ 3"),
     ("$b^2 = \\omega_{p3}/\\omega_z$", "ratio of pole to zero", "—", "$1 + C_1/C_2$"),
     ("$PM_{max}$", "the best phase margin this filter can give", "deg", "≈ 53°")],
    "The phase boost is largest exactly between the zero and the pole (geometric mean), and the ratio $C_1/C_2$ sets it.",
    "Put $\\omega_c = \\sqrt{\\omega_z\\omega_{p3}}$ in the previous box: $\\arctan b - \\arctan(1/b)$. A wider "
    "spacing (bigger $C_1/C_2$) → more phase margin but less ripple filtering.",
    "$C_1/C_2 = 7.8 \\Rightarrow b = 2.96 \\Rightarrow \\arctan 2.96 - \\arctan 0.34 = 71.3 - 18.7 = 52.6°$.")),
("\\phi_{e}(\\infty) = \\lim_{s\\to0} s\\,E(s)", E(
    [("$\\phi_e(\\infty)$", "phase error after everything has settled", "rad", "0 for a type-II loop and a frequency step"),
     ("$\\lim_{s\\to0} sF(s)$", "final-value theorem: the value of $f(t)$ at $t\\to\\infty$", "—", "—"),
     ("$\\Phi_{in}(s)$", "the input disturbance (step: $\\Delta\\phi/s$; frequency step: $\\Delta\\omega/s^2$)", "—", "—")],
    "To find where an error ends up, multiply its Laplace transform by s and let s go to zero.",
    "Each integrator in $G$ puts a factor $s$ in $E = 1/(1+G)$ at low frequency. A frequency step ($1/s^2$) needs "
    "two of them to give zero error — that is why the CP-PLL is type II.")),
("\\frac{d\\phi_e}{dt} = \\Delta\\omega - K\\sin\\phi_e", E(
    [("$\\phi_e$", "phase error", "rad", "—"),
     ("$\\Delta\\omega$", "initial frequency difference between VCO and reference", "rad/s", "—"),
     ("$K$", "loop gain of a first-order loop ($K_{PD}K_{VCO}$)", "rad/s", "—"),
     ("$\\sin\\phi_e$", "the real (non-linear) characteristic of a mixer/sine PD", "—", "—")],
    "The phase error changes because of the frequency difference, and the loop pulls it back by $K\\sin\\phi_e$.",
    "If $|\\Delta\\omega| < K$ there is a $\\phi_e$ where the right side is zero — the loop locks. If not, $\\phi_e$ "
    "keeps sliding (cycle slipping): the pull-in limit $|\\Delta\\omega| = K$.")),
("\\mathcal L(\\Delta f) = \\frac{\\text{power in 1 Hz", E(
    [("$\\mathcal L(\\Delta f)$", "single-sideband phase noise at offset Δf", "dBc/Hz", "−110 dBc/Hz at 300 kHz (FFNC off)"),
     ("$\\Delta f$", "offset frequency from the carrier", "Hz", "10 kHz…40 MHz"),
     ("dBc/Hz", "dB relative to the carrier, in a 1 Hz bandwidth", "—", "—"),
     ("$S_\\phi$", "one-sided power spectral density of the phase", "rad²/Hz", "—")],
    "How much noise power sits 1 Hz wide at a distance Δf from the carrier, compared with the carrier power.",
    "For small phase noise $\\cos(\\omega t + \\phi_n) \\approx \\cos\\omega t - \\phi_n\\sin\\omega t$: the phase "
    "noise appears as two sidebands, each carrying half of $S_\\phi$ → $S_\\phi = 2\\mathcal L$.",
    "−110 dBc/Hz = $10^{-11}$ per Hz → $S_\\phi = 2\\times10^{-11}$ rad²/Hz.")),
("\\sigma_t = \\frac{1}{2\\pi f_0}\\sqrt{\\int_{f_1}^{f_2} 2", E(
    [("$\\sigma_t$", "rms jitter", "s", "1.26 ps (FFNC on, corrected)"),
     ("$f_0$", "carrier (output) frequency", "Hz", "1.6 GHz"),
     ("$f_1, f_2$", "integration limits", "Hz", "10 kHz, 40 MHz"),
     ("$2\\cdot10^{\\mathcal L/10}$", "$S_\\phi$ in rad²/Hz (from dBc/Hz)", "rad²/Hz", "—")],
    "Add up (integrate) all the phase-noise power between the limits, take the square root to get rms phase, divide "
    "by $2\\pi f_0$ to turn radians into seconds.",
    "Total phase variance $\\sigma_\\phi^2 = \\int S_\\phi df$ (Parseval). One cycle is 2π rad = $1/f_0$ s, so "
    "seconds = radians / $(2\\pi f_0)$.",
    "If the integral gives $1.6\\times10^{-4}$ rad², $\\sigma_\\phi = 12.6$ mrad → $12.6\\times10^{-3}/(2\\pi\\cdot1.6\\times10^9) = 1.25$ ps.")),
("\\mathcal L(\\Delta f) = \\frac{\\sigma_{per}^2 f_0^3}{\\Delta f^2}", E(
    [("$\\sigma_{per}$", "rms period jitter of a free-running oscillator", "s", "—"),
     ("$f_0^3/\\Delta f^2$", "how a random walk of phase looks in frequency", "—", "—")],
    "A free-running oscillator with independent period errors has phase noise falling at 20 dB/decade.",
    "Each period adds an independent error; errors accumulate (random walk), whose spectrum is $\\propto 1/f^2$. "
    "This is the link between a time-domain number (period jitter) and the $1/f^2$ region of $\\mathcal L$.")),
("\\frac{8}{3\\eta}\\,\\frac{kT}{P}", E(
    [("$k$", "Boltzmann constant", "J/K", "$1.38\\times10^{-23}$"),
     ("$T$", "absolute temperature", "K", "300 K"),
     ("$P$", "power of the ring oscillator", "W", "≈ 4.6 mW"),
     ("$V_{DD}$", "ring supply voltage", "V", "≈ 1.38 V"),
     ("$V_{char}$", "characteristic voltage: $V_{ov}/\\gamma$ (long channel ≈ $V_{DD}-V_{TH}$ ...)", "V", "—"),
     ("$\\eta$", "shape factor of the transitions (0.75–1)", "—", "—"),
     ("$f_0$", "oscillation frequency", "Hz", "1.6 GHz")],
    "A ring's thermal phase noise is set mainly by kT/P: for a given frequency, the only lever is power.",
    "Each switching event dumps $CV_{DD}^2$ of energy and adds noise of order $kT/C$; more power = bigger C at the "
    "same frequency = relatively less noise. That is why the ring 'FoM' is roughly constant (Hajimiri; Abidi).",
    "Doubling power improves $\\mathcal L$ by only 3 dB — the reason this project uses FFNC instead of brute power.")),
("\\Phi_{out} = \\underbrace{N\\frac{G}{1+G}}", E(
    [("$\\Phi_{REF}, \\Phi_{PD}, \\Phi_{div}$", "noise of the reference, detector and divider (input-referred)", "rad", "—"),
     ("$\\Phi_{VCO}$", "free-running VCO phase noise", "rad", "—"),
     ("$NG/(1+G)$", "low-pass with gain N — applied to everything at the loop input", "—", "—"),
     ("$1/(1+G)$", "high-pass — applied to the VCO", "—", "—")],
    "Input-side noise is multiplied by N and low-passed; VCO noise is high-passed. The loop bandwidth splits the "
    "two jobs.",
    "Inside the bandwidth the loop corrects the VCO to follow the (multiplied) reference; outside it cannot react, "
    "so the VCO's own noise appears. Choosing $f_c$ = choosing where to swap.",
    "N = 32 → reference noise +30 dB in band. A ring VCO is noisy, so we want a wide loop (2.5 MHz).")),
# =============================================================================================== phase 2
("G(s) = \\frac{K_{PD}K_{VCO}}{s\\,(1+s/\\omega_{LPF})}", E(
    [("$K_{PD}$", "mixer/XOR phase-detector gain", "V/rad", "—"),
     ("$\\omega_{LPF}$", "corner of the RC low-pass after the PD", "rad/s", "—"),
     ("$H(s)$", "closed-loop transfer (N = 1 here)", "—", "—")],
    "Type-I loop: one integrator (the VCO) and one extra pole (the low-pass that removes PD ripple).",
    "Insert $G$ into $G/(1+G)$ and multiply top and bottom by $s(1+s/\\omega_{LPF})$: a second-order system.")),
("\\omega_n = \\sqrt{\\omega_{LPF}\\,K_{PD}K_{VCO}},\\qquad \\zeta", E(
    [("$\\omega_n$", "natural frequency (how fast the loop reacts)", "rad/s", "—"),
     ("$\\zeta$", "damping factor (1/√2 ≈ 0.707 is the usual target)", "—", "—"),
     ("$K = K_{PD}K_{VCO}$", "loop gain", "rad/s", "—")],
    "Speed rises with $\\sqrt{K}$, but damping falls with $\\sqrt{K}$ — you cannot set both freely.",
    "Compare the denominator with the standard form $s^2 + 2\\zeta\\omega_ns + \\omega_n^2$ (after scaling by "
    "$\\omega_{LPF}$).",
    watch="This coupling is the first limitation of the type-I loop: more gain (less static error) = less damping.")),
("\\Delta\\phi_{ss} = \\frac{\\Delta\\omega}{K_{PD}K_{VCO}}", E(
    [("$\\Delta\\phi_{ss}$", "static phase error needed to hold the VCO off its free-running frequency", "rad", "—"),
     ("$\\Delta\\omega$", "required frequency shift", "rad/s", "—")],
    "To pull the VCO by Δω, the type-I loop needs a constant phase error that produces the control voltage.",
    "With no integrator in the filter, the only way to hold a constant $V_{cont}$ is a constant PD output = "
    "constant phase error: $\\Delta\\omega = K_{VCO}V_{cont} = K_{VCO}K_{PD}\\Delta\\phi$.",
    "Needs Δω = 2π·10 MHz and K = 2π·50 MHz/rad → 0.2 rad static error, changing with frequency and temperature.")),
("\\Big|F(j2\\omega_{REF})\\Big|", E(
    [("$|F(j2\\omega_{REF})|$", "how much the low-pass attenuates the PD ripple at $2f_{REF}$", "—", "—"),
     ("$\\omega_{LPF}$", "low-pass corner", "rad/s", "—")],
    "Summary of the type-I trade-offs in one line: bandwidth, damping, ripple and static error all depend on "
    "$\\omega_{LPF}$ and $K$.",
    "A mixer PD produces ripple at twice the reference; the first-order filter attenuates it by about "
    "$\\omega_{LPF}/2\\omega_{REF}$. Lower $\\omega_{LPF}$ → less ripple but less damping.")),
("\\text{spur (dBc)} = 20\\log_{10}\\frac{K_{VCO}A_m}{2\\omega_m}", E(
    [("$A_m$", "amplitude of the ripple on $V_{cont}$", "V", "—"),
     ("$\\omega_m$", "ripple frequency", "rad/s", "$2\\omega_{REF}$ for a mixer PD"),
     ("spur", "level of each sideband relative to the carrier", "dBc", "—")],
    "A sinusoidal ripple on the control voltage frequency-modulates the VCO and creates sidebands.",
    "FM with peak deviation $K_{VCO}A_m$ at rate $\\omega_m$ has modulation index $\\beta = K_{VCO}A_m/\\omega_m$; "
    "for small β each sideband is β/2 of the carrier.",
    "$K_{VCO} = 2\\pi\\cdot300$ MHz/V, $A_m = 1$ µV, ripple at $f_m = 100$ MHz: $20\\log(300\\cdot10^6\\cdot10^{-6}/(2\\cdot100\\cdot10^6)) = -116.5$ dBc (the 2π factors cancel).")),
("F(s) = \\frac{1+s\\tau_2}{1+s\\tau_1}", E(
    [("$\\tau_1 = (R_1+R_2)C$", "pole time constant", "s", "—"),
     ("$\\tau_2 = R_2C$", "zero time constant", "s", "—")],
    "A lag-lead filter: a pole for filtering and a zero that restores phase.",
    "The extra resistor $R_2$ in series with C lets the high-frequency gain stay at $R_2/(R_1+R_2)$ instead of "
    "falling to zero — this decouples damping from bandwidth.")),
("H(s) = \\frac{K(1+s\\tau_2)}{\\tau_1 s^2", E(
    [("$K$", "DC loop gain $K_{PD}K_{VCO}$", "rad/s", "—"),
     ("$\\omega_n = \\sqrt{K/\\tau_1}$", "natural frequency", "rad/s", "—"),
     ("$\\zeta$", "damping, now with an extra term $\\tau_2$", "—", "—")],
    "With the lag-lead filter the damping gets a term $\\tau_2$ that you can choose independently of $K$.",
    "The zero contributes $s\\tau_2 K$ to the middle coefficient, adding damping without reducing the gain.")),
("H_{ZOH}(s) = \\frac{1-e^{-sT_{REF}}}{sT_{REF}}", E(
    [("$H_{ZOH}$", "zero-order hold: holds a sampled value for one period", "—", "—"),
     ("$e^{-sT_{REF}/2}$", "equivalent pure delay of half a period", "—", "10 ns at 50 MHz")],
    "A sampled detector that holds its output for a period behaves like a delay of half a period.",
    "The hold output is the average of the last period, centred T/2 in the past. A delay adds phase lag "
    "$\\omega T/2$ that grows with frequency — it eats phase margin when $f_c$ approaches $f_{REF}$.",
    "At $f_c = 2.5$ MHz: $360°\\cdot2.5\\times10^6\\cdot10\\times10^{-9} = 9°$ of lost phase margin.")),
# =============================================================================================== phase 3
("G(s) = \\frac{I_p}{2\\pi}\\cdot\\frac{1}{C_1s}", E(
    [("$I_p/2\\pi$", "PFD + CP gain", "A/rad", "—"),
     ("$1/C_1s$", "capacitor-only filter", "Ω", "—"),
     ("$K_{VCO}/Ns$", "VCO and divider", "rad/(V·s)", "—")],
    "With only a capacitor the loop has two integrators: phase −180° at every frequency — unstable.",
    "Each $1/s$ contributes −90°. A loop with −180° at crossover has zero phase margin: it oscillates. Hence the "
    "resistor $R_1$.")),
("G(s) = \\frac{I_pK_{VCO}}{2\\pi NC_1}\\cdot\\frac{1+sR_1C_1}{s^2}:", E(
    [("$1 + sR_1C_1$", "the zero added by $R_1$", "—", "—")],
    "Adding $R_1$ multiplies the loop gain by $(1+sR_1C_1)$: above $\\omega_z$ the phase climbs back towards −90°.",
    "The resistor turns the current pulses into immediate voltage steps (a proportional path) in parallel with the "
    "integrating capacitor.")),
("\\frac{H(s)}{N} = \\frac{G}{1+G} = \\frac{2\\zeta\\omega_n s", E(
    [("$\\omega_n$", "natural frequency", "rad/s", "—"),
     ("$\\zeta$", "damping", "—", "—"),
     ("$2\\zeta\\omega_n s$ in the numerator", "the zero — it makes the type-II response peak a little even when ζ is large", "—", "—")],
    "The classic second-order type-II PLL response (ignoring $C_2$).",
    "Substitute $G$ into $G/(1+G)$ and compare with $s^2 + 2\\zeta\\omega_ns + \\omega_n^2$.")),
("\\omega_n = \\sqrt{\\frac{I_pK_{VCO}}{2\\pi NC_1}}", E(
    [("$I_p$", "charge-pump current", "A", "—"),
     ("$C_1$", "loop-filter capacitor", "F", "17.1 pF"),
     ("$R_1$", "loop-filter resistor", "Ω", "11 kΩ"),
     ("$N$", "division ratio", "—", "32")],
    "The CP current, VCO gain and capacitor set the speed; the resistor alone adds damping.",
    "Read off from the denominator. Unlike type I, $\\zeta$ grows with $R_1$, so speed and damping are set "
    "separately: $\\omega_n$ by $I_p/C_1$, $\\zeta$ by $R_1$.",
    watch="$\\zeta \\propto \\sqrt{I_pK_{VCO}}$: when $K_{VCO}$ varies over PVT the damping varies with its square root.")),
("PM_{max} = \\arctan b - \\arctan\\frac1b = \\arctan\\frac{b^2-1}{2b}", E(
    [("$b$", "zero–crossover–pole spacing", "—", "≈ 3")],
    "The same phase-margin formula as in phase 1, in closed form.",
    "$\\tan(a - c) = (\\tan a - \\tan c)/(1+\\tan a\\tan c)$ with $\\tan a = b$, $\\tan c = 1/b$.",
    "$b = 3$: $\\arctan(8/6) = 53.1°$.")),
("C_{tot} = C_1+C_2 = \\frac{b\\,I_pK_{VCO}}", E(
    [("$C_{tot}$", "total loop-filter capacitance", "F", "19.3 pF"),
     ("$\\omega_c$", "target crossover", "rad/s", "$2\\pi\\cdot2.5$ MHz"),
     ("$b$", "spacing factor chosen for the PM", "—", "≈ 3")],
    "A recipe: choose $f_c$ and PM → $b$ → total C → split into $C_1$, $C_2$ → $R_1$.",
    "Set $|G(j\\omega_c)| = 1$ with the zero and pole placed at $\\omega_c/b$ and $b\\omega_c$; solving for C gives "
    "this. The geometry (b) sets the phase, the magnitude condition sets the absolute values.",
    "Step 73 used the exact sampled model instead, but this hand formula gives the same values within ~10 %.")),
("\\Delta PM \\approx 360°\\cdot f_c\\cdot\\frac{T_{REF}}{2}", E(
    [("$\\Delta PM$", "phase margin lost by the sampling delay", "deg", "9° at 2.5 MHz"),
     ("$f_c/f_{REF}$", "how close the loop bandwidth is to the sampling rate", "—", "1/20")],
    "The half-period hold delay eats phase margin in proportion to $f_c/f_{REF}$.",
    "A delay $T$ has phase $-\\omega T$; at $\\omega_c$ with $T = T_{REF}/2$: $360°f_cT_{REF}/2$.",
    "This is the reason for the rule $f_c \\le f_{REF}/10$ (we use 1/20 = 9° lost).")),
("\\mathcal L_{in\\text{-}band} = \\mathcal L_{1Hz}", E(
    [("$\\mathcal L_{1Hz}$", "PFD/CP figure of merit normalised to 1 Hz reference and N = 1", "dBc/Hz", "≈ −220…−230"),
     ("$10\\log f_{REF}$", "more comparisons per second → more noise events", "dB", "+77 dB at 50 MHz"),
     ("$20\\log N$", "phase multiplication by N", "dB", "+30 dB at N = 32")],
    "The in-band noise floor of a classic CP-PLL: a fixed detector figure + the reference rate + N².",
    "Detector noise is input-referred phase noise; the loop multiplies phase by N (power N²). The $20\\log N$ term "
    "is exactly what the sub-sampling PD removes for its own noise.",
    "−225 + 77 + 30 = −118 dBc/Hz in band — not good enough for 1.4 ps with a ring; the SSPLL does better.")),
("\\text{spur} = 20\\log_{10}\\frac{K_{VCO}|V_1|}{2\\omega_{REF}},\\qquad V_1", E(
    [("$V_1$", "first harmonic (at $f_{REF}$) of the control-voltage ripple", "V", "—"),
     ("$c_1$", "first Fourier coefficient of the charge-pump current pulses", "A", "—"),
     ("$Z(j\\omega_{REF})$", "loop-filter impedance at the reference frequency", "Ω", "—")],
    "Reference spur = FM sideband caused by the ripple that the CP pulses leave on $V_{cont}$.",
    "Mismatch/leakage makes a pulse every period; its harmonic at $f_{REF}$ through the filter impedance is the "
    "ripple; FM with index $K_{VCO}V_1/\\omega_{REF}$ gives sidebands of half that.")),
# =============================================================================================== phase 4
("v_k = A\\sin\\!\\big(2\\pi f_{VCO}kT_{REF}", E(
    [("$v_k$", "the k-th sample of the VCO waveform", "V", "—"),
     ("$A$", "VCO amplitude at the sampler", "V", "≈ 0.6 V (buffer swing)"),
     ("$k$", "sample index", "—", "0, 1, 2, …"),
     ("$\\phi$", "phase of the VCO at the sampling instants", "rad", "—")],
    "Sampling a 1.6 GHz sine at exactly 50 MHz picks the same point of the waveform every time — the sample is DC.",
    "$\\sin(x + 2\\pi\\cdot\\text{integer}) = \\sin x$: if $f_{VCO} = Nf_{REF}$ the term $2\\pi Nf_{REF}kT_{REF} = "
    "2\\pi Nk$ drops out. Any difference $f_{VCO} - Nf_{REF}$ makes the samples drift (a beat).",
    watch="Sub-sampling cannot tell N from N±1 — that is why a frequency-locked loop must bring the VCO close first.")),
("v_{sam} = A\\sin(\\omega_{VCO}\\Delta t)\\approx", E(
    [("$\\Delta t$", "timing offset of the VCO zero crossing from the sampling edge", "s", "—"),
     ("$K_t = A\\omega_{VCO}$", "SSPD gain in volts per second of timing error", "V/s", "$0.6\\cdot2\\pi\\cdot1.6\\times10^9 = 6$ V/ns"),
     ("$K_{PD} = A$", "SSPD gain in volts per radian of VCO phase", "V/rad", "≈ 0.6 V/rad"),
     ("$\\Delta\\phi_{VCO}$", "VCO phase error", "rad", "—")],
    "Near the zero crossing the sine is a steep line: the sampled voltage measures the timing error directly.",
    "$\\sin x \\approx x$ for small x. The slope of a 1.6 GHz sine is huge, so the SSPD gain per unit of *reference* "
    "phase is $N$ times larger than a PFD's — detector noise is not multiplied by $N^2$.",
    "1 ps of timing error → 6 mV — easy to see above the switch's kT/C noise (≈ 0.2 mV for 100 fF).")),
("G(s) = \\beta\\,Z(s)\\,\\frac{K_{VCO}}{s},\\qquad \\Phi_{out}", E(
    [("$\\beta$", "SSPD + pulsed-Gm gain: average current per radian of VCO phase", "A/rad", "0.78 µA/rad (corrected)"),
     ("$Z(s)$", "loop-filter impedance", "Ω", "—"),
     ("$\\Phi_{n,SSPD}$", "SSPD noise referred to VCO phase", "rad", "—")],
    "No divider in the loop: the gain β already works in VCO phase, and the reference phase enters multiplied by N.",
    "The SSPD compares the VCO directly with the reference edge; the reference phase (and its noise) counts N times, "
    "but the SSPD's own noise counts only once.")),
("\\mathcal L_{SSPD} = \\frac{kT}{C\\,A^2 f_{REF}}", E(
    [("$kT/C$", "noise sampled on the hold capacitor each time the switch opens", "V²", "(0.2 mV)² for 100 fF"),
     ("$C$", "sampling capacitor", "F", "100 fF"),
     ("$A$", "VCO amplitude at the sampler", "V", "—"),
     ("$f_{REF}$", "number of samples per second", "Hz", "50 MHz")],
    "The sampling noise, divided by the gain squared, spread over the reference bandwidth, gives the SSPD's phase noise.",
    "Voltage noise $\\sigma_v^2 = kT/C$ per sample → phase noise $\\sigma_\\phi^2 = kT/(CA^2)$; white samples at rate "
    "$f_{REF}$ spread this over $f_{REF}$ (one-sided $2/f_{REF}$, and $\\mathcal L = S_\\phi/2$). Differential: noise "
    "×2, signal ×2 (power ×4) → 3 dB better.",
    "$4.1\\times10^{-21}/(10^{-13}\\cdot0.36\\cdot5\\times10^7) = 2.3\\times10^{-15}$ → −146 dBc/Hz referred to the VCO — "
    "far below a PFD's −118.")),
("\\beta = \\frac{2A\\,g_m\\,\\tau}{T_{REF}}", E(
    [("$g_m$", "transconductance of the pulsed Gm cell", "S", "78 µS (3 units, corrected)"),
     ("$\\tau$", "width of the current pulse (how long the Gm is on)", "s", "≈ 0.25 × 20 ns"),
     ("$2A\\sin\\Delta\\phi$", "differential sampled voltage", "V", "—"),
     ("$\\tau/T_{REF}$", "duty cycle of the Gm pulse", "—", "—")],
    "Average charge-pump current per radian = sampled voltage × transconductance × fraction of time it is on.",
    "The pulse prevents the Gm from driving the loop filter the whole period (reducing ripple/spurs) and sets a "
    "clean, PVT-stable gain through $\\tau/T$.")),
("H_{cs}(z) = \\frac{1-\\alpha}{1-\\alpha z^{-1}}", E(
    [("$z^{-1}$", "one sample (one reference period) of delay", "—", "—"),
     ("$\\alpha$", "share of the old charge that stays when two capacitors are connected", "—", "0.5 (equal caps)")],
    "Charge sharing between the sample and hold capacitors acts as a first-order low-pass in the sampled domain.",
    "Each period the new sample mixes with the old held value: $y_k = \\alpha y_{k-1} + (1-\\alpha)x_k$ — a "
    "discrete RC filter, which adds delay (phase lag) to the loop.")),
("\\text{spur} \\approx 20\\log_{10}\\frac{\\beta}{2} = 20\\log_{10}\\left(\\frac{f_0}{f_{REF}}", E(
    [("$f_0/f_{REF}$", "N: the VCO sees N cycles of disturbance per reference period", "—", "32"),
     ("$\\Delta C/\\Sigma C$", "relative kick-back mismatch of the sampler", "—", "—"),
     ("$\\sin(\\pi d)/\\pi$", "Fourier factor of the disturbance pulse of duty d", "—", "—")],
    "The sampler kicks the VCO once per reference period; mismatch turns the kick into a reference spur.",
    "Charge injection modulates the VCO phase at $f_{REF}$; dummy samplers and isolation buffers reduce $\\Delta C$.")),
# =============================================================================================== phase 5
("t_d \\approx \\frac{C_L\\,V_{DD}/2}{I}", E(
    [("$t_d$", "delay of one stage (input crossing → output crossing)", "s", "tens of ps"),
     ("$C_L$", "load capacitance at the stage output", "F", "—"),
     ("$V_{DD}/2$", "voltage swing needed to reach the switching threshold", "V", "—"),
     ("$I$", "current that charges or discharges the load", "A", "—")],
    "Delay = time to move a charge $C_L\\cdot V_{DD}/2$ with a current $I$.",
    "$Q = CV$ and $Q = It$ ⇒ $t = CV/I$. Everything that changes $I$ (control voltage) or $C_L$ (capacitor bank) "
    "changes the delay.")),
("t_d \\propto \\frac{C_L\\,V_{DD}}{(V_{DD}-V_{TH})^\\alpha}", E(
    [("$V_{TH}$", "threshold voltage", "V", "≈ 0.45 V (1.8 V nMOS)"),
     ("$\\alpha$", "velocity-saturation index (2 for long channel, ~1.3 for short)", "—", "—")],
    "Delay versus supply: the drain current grows as $(V_{DD} - V_{TH})^\\alpha$, the charge as $V_{DD}$.",
    "Alpha-power law (Sakurai): it shows how strongly supply noise changes the delay — the supply sensitivity of the NCB.")),
("\\tau \\approx \\frac{C_L V_{sw}}{I_{starve}}", E(
    [("$I_{starve}$", "current allowed by the starving transistor", "A", "—"),
     ("$V_{ctrl}$", "control voltage of the starving device", "V", "—"),
     ("$k$", "transconductance parameter $\\mu C_{ox}W/L$", "A/V²", "—"),
     ("$K_{DL}$", "delay-line gain: delay change per volt", "s/V", "—")],
    "A current-starved stage: control voltage → current (square law) → delay (CV/I). Its gain is −2τ/(V_ctrl − V_TH).",
    "Differentiate $\\tau = C V/(\\tfrac{k}{2}V_{ov}^2)$ with respect to $V_{ctrl}$: $d\\tau/dV = -2\\tau/V_{ov}$.",
    watch="The gain depends on τ and $V_{ov}$ — it varies over PVT, which is why the cancellation gain is calibrated (ncb_code).")),
("\\sigma_{t}^2 \\approx \\frac{kT\\,C_L}{I^2}", E(
    [("$\\sigma_t$", "rms jitter added by one stage", "s", "—"),
     ("$\\gamma$", "channel-noise factor", "—", "≈ 1"),
     ("$V_{ov}$", "overdrive of the switching device", "V", "—")],
    "A delay stage adds jitter ∝ $\\sqrt{kT/C_L}$ relative to its delay; more capacitance (more power) = less "
    "relative jitter.",
    "Voltage noise at the switching instant ($kT/C$ plus channel noise) divided by the slew rate $I/C_L$.",
    "The NCB must add less jitter than it removes — this sets its minimum power.")),
("G_{t,NCB} = \\frac{1}{K_{t,SSPD}}", E(
    [("$G_{t,NCB}$", "required delay change per volt of the NCB", "s/V", "≈ 0.17 ns/V"),
     ("$K_{t,SSPD} = A\\cdot2\\pi f_0$", "SSPD gain in volts per second of timing error", "V/s", "≈ 6 V/ns")],
    "To cancel, the delay line must turn the SSPD voltage back into exactly the same timing error: its gain is the "
    "inverse of the SSPD gain.",
    "SSPD: Δt → $K_t\\Delta t$ volts; NCB: volts → $G_t\\cdot$volts seconds. The product $G_tK_t$ must be 1.")),
# =============================================================================================== phase 6
("\\phi_{out2} = \\phi_{out1} - G_{can}\\,\\phi_{e}", E(
    [("$\\phi_{out1}$", "phase of the PLL output (before cancellation)", "rad", "—"),
     ("$\\phi_{out2}$", "phase after the noise-cancelling delay line", "rad", "—"),
     ("$G_{can}$", "cancellation gain (ideally 1)", "—", "set by ncb_code"),
     ("$\\phi_e$", "phase error measured by the SSPD", "rad", "—")],
    "Measure the remaining phase error, then delay the output by exactly that amount, with the opposite sign.",
    "The SSPD already measures $\\phi_{out1} - N\\phi_{REF}$ every period. Subtracting it moves the output back to "
    "$N\\phi_{REF}$ — the clean, multiplied reference.")),
("\\Delta T_{out} = \\Delta T_{VCO} - G_tK_t", E(
    [("$\\Delta T_{VCO}$", "timing error of the VCO edge", "s", "—"),
     ("$G_tK_t$", "cancellation path gain (SSPD × NCB)", "—", "1 ideally"),
     ("$T_0$", "constant delay of the NCB (does not matter for jitter)", "s", "—")],
    "The residual error is $(1 - G_tK_t)$ times the VCO error: with a gain of exactly 1 it vanishes.",
    "A 10 % gain error leaves 10 % of the noise: −20 dB, not perfect cancellation — calibration matters.")),
("\\frac{|r|}{|n|} = \\left|1 - G e^{j\\theta}\\right|", E(
    [("$r$", "residual noise after cancellation", "—", "—"),
     ("$n$", "noise before cancellation", "—", "—"),
     ("$G$", "magnitude of the cancellation gain", "—", "—"),
     ("$\\theta$", "phase error of the cancellation path (delay mismatch)", "rad", "—")],
    "Cancellation is a subtraction of two vectors; both a gain error and a timing (phase) error leave a residue.",
    "Write the cancelled signal as $n - Gn e^{j\\theta}$ and take the magnitude.",
    "G = 1, θ = 10° → $|1 - e^{j0.175}| = 0.17$ → 15 dB reduction. G = 0.9, θ = 0 → 20 dB.")),
("S_s(f) = f_{REF}\\sum_k", E(
    [("$S_s$", "spectrum of the SSPD output (a sampled signal)", "—", "—"),
     ("$S_{\\phi,in}$", "phase noise at the SSPD input", "rad²/Hz", "—"),
     ("$f - kf_{REF}$", "every copy (alias) of the spectrum shifted by multiples of $f_{REF}$", "Hz", "—")],
    "Sampling folds all noise above $f_{REF}/2$ back into the baseband — the cancellation path sees aliased noise too.",
    "A sampler multiplies by a train of impulses, whose spectrum is a train at $kf_{REF}$; convolution makes copies.",
    watch="Aliased high-frequency VCO noise that the NCB adds back is the $|G_c|^2S_{alias}$ term of the budget.")),
("|r(F_{cal})| \\propto \\left|1 - G_{can}(F_{cal})\\right|", E(
    [("$F_{cal}$", "frequency of the calibration tone", "Hz", "50 kHz (proposal)"),
     ("$LG$", "loop gain at that frequency", "—", "—")],
    "The residue of an injected tone measures how far the cancellation gain is from 1 — the basis of the calibration.",
    "Inject a tone, look at how much of it is left at the output, step ncb_code until the residue is smallest.")),
# =============================================================================================== phase 7
("S_{out}(f) = \\big[N^2 S_{REF} + S_{PD}\\big]", E(
    [("$S_{out}$", "output phase-noise PSD", "rad²/Hz", "—"),
     ("$S_{REF}$", "reference (XO + buffer) phase noise", "rad²/Hz", "−155 dBc/Hz floor"),
     ("$S_{PD}$", "SSPD + Gm noise referred to VCO phase", "rad²/Hz", "—"),
     ("$H$", "closed-loop transfer (normalised)", "—", "—"),
     ("$G_c$", "feedforward cancellation transfer", "—", "≈ 1 in band when FFNC on, 0 when off"),
     ("$S_{VCO}$", "free-running VCO noise", "rad²/Hz", "−98.7 dBc/Hz at 1 MHz"),
     ("$S_{NCB}$", "noise added by the delay line", "rad²/Hz", "—"),
     ("$K_s$", "supply sensitivity of the NCB delay", "s/V", "—"),
     ("$S_{v,LDO}$", "regulator voltage noise", "V²/Hz", "—"),
     ("$S_{alias}$", "folded VCO noise in the cancellation path", "rad²/Hz", "—")],
    "The whole noise budget in one line: every source times its own transfer function to the output, all added.",
    "Uncorrelated noises add in power. Input-side noise sees $H + G_c(1-H)$ (the loop plus whatever FFNC re-adds); "
    "VCO noise sees $(1-G_c)(1-H)$ — first high-passed by the loop, then reduced again by FFNC.")),
("\\sigma_t = \\frac{1}{2\\pi f_0}\\sqrt{\\int_{10\\,\\mathrm{kHz}}", E(
    [("$\\sigma_{t,i}$", "jitter contribution of source i alone", "s", "—")],
    "Integrate the total spectrum for the jitter; since noises are independent, contributions add in squares.",
    "Variance of a sum of independent variables = sum of variances. This is why a budget is a table of "
    "$\\sigma_{t,i}^2$ and why halving the largest term helps most.")),
("L(s) \\approx \\beta K_{VCO}\\frac{Z(s)}{s}e^{-st_p}", E(
    [("$L(s)$", "loop gain of the SSPLL", "—", "—"),
     ("$t_p$", "delay from the sampling instant to the Gm current pulse", "s", "2.5 ns"),
     ("$e^{-st_p}$", "pure delay", "—", "−2.3° at 2.5 MHz")],
    "The continuous approximation of the sub-sampling loop: gain, filter, VCO integrator and a small delay.",
    "Good below ~$f_{REF}/10$; step 73 used the exact discrete model (next box) to be sure.")),
("x[k+1] = e^{AT}x[k] + e^{A(T-t_p)}B\\,q[k]", E(
    [("$x[k]$", "state of the loop filter + VCO at sample k (capacitor voltages, phase)", "—", "—"),
     ("$A, B, C$", "state-space matrices of the continuous filter and VCO", "—", "—"),
     ("$e^{AT}$", "how the state evolves over one period with no input", "—", "—"),
     ("$q[k]$", "charge pulse delivered in period k", "C", "—"),
     ("$L(z)$", "exact discrete-time loop gain", "—", "—")],
    "The exact sampled model: between pulses the filter evolves freely; each pulse kicks the state.",
    "Solve the linear ODE exactly over one period (matrix exponential). This captures the hold, the pulse timing "
    "and aliasing that the continuous model ignores.")),
("\\mathcal{L}_{th}(\\Delta f) = \\frac{2N\\langle h^2 S_{th}\\rangle}", E(
    [("$h(t)$", "impulse sensitivity function (ISF): phase shift per unit injected charge", "rad/C", "measured, M2"),
     ("$S_{th}$", "thermal noise current PSD of the device (cyclostationary)", "A²/Hz", "—"),
     ("$\\langle\\cdot\\rangle$", "average over one oscillation period", "—", "—"),
     ("$B$", "flicker coefficient: $S_{fl} = B/f$", "A²", "—"),
     ("$N$", "number of identical noise sources (stages)", "—", "—")],
    "Each device's noise is weighted by how sensitive the ring is at the moment it injects; flicker is weighted by "
    "the ISF's average (DC) part.",
    "Hajimiri–Lee: phase = ∫ h(t) i_n(t) dt. Random current with PSD $S$ gives a phase random walk with spectrum "
    "$\\langle h^2S\\rangle/\\omega^2$. Flicker is slow, so only the DC part of h converts it — a symmetric "
    "waveform (small $h_{dc}$) suppresses the 1/f³ region.")),
("I_{CCO} = M\\,I_u\\,(N_{base} + \\text{code})", E(
    [("$I_{CCO}$", "current into the ring's supply node", "A", "0.69–2.63 mA"),
     ("$M$", "output mirror ratio", "—", "25"),
     ("$I_u$", "DAC unit current ($I_{BIAS}/2$)", "A", "2.5 µA"),
     ("$N_{base}$", "always-on units", "—", "11"),
     ("code", "5-bit coarse-tuning word cco_code", "—", "0…31")],
    "Ring current = mirror ratio × unit current × number of active units.",
    "Binary-weighted unit sinks give a linear current DAC; the base units set the minimum.",
    "Code 10: $25\\times2.5\\,\\mu\\text{A}\\times21 = 1.31$ mA ≈ 1.6 GHz at tt.")),
("S_{i,out} \\approx 4kT\\gamma g_{m,out}", E(
    [("$S_{i,out}$", "output-current noise PSD of the CCO", "A²/Hz", "(8.7 pA/√Hz)² at 1 MHz"),
     ("$4kT\\gamma g_{m,out}$", "channel noise of the output transistor", "A²/Hz", "—"),
     ("$R_F, C_F$", "filter resistor and capacitor between the mirror gates", "Ω, F", "10 MΩ, 7.3 pF"),
     ("$f_F$", "filter corner $1/2\\pi R_FC_F$", "Hz", "2.2 kHz")],
    "Output noise = the output device's own noise + the resistor's noise, which the filter removes above $f_F$ "
    "— and, surprisingly, a *larger* $R_F$ leaves *less* of it.",
    "The resistor's noise voltage $4kTR_F$ is low-passed by the RC; above the corner what passes is "
    "$4kTR_F/(\\omega R_FC_F)^2 = 4kT/(\\omega^2C_F^2R_F)$ — inversely proportional to $R_F$.",
    "Hence 10 MΩ instead of 300 kΩ cut the noise from 21 to 8.7 pA/√Hz.")),
("\\sigma_t = \\frac{\\sigma_v}{s},\\qquad s = \\pi f_{ref} V_{pp}", E(
    [("$\\sigma_v$", "rms noise voltage at the receiver threshold", "V", "—"),
     ("$s$", "slope of the input waveform at the crossing", "V/s", "0.157 V/ns for 1 V pp at 50 MHz"),
     ("$V_{pp}$", "peak-to-peak input amplitude", "V", "0.4–3.3 V"),
     ("$\\mathcal L_{floor}$", "phase-noise floor caused by independent jitter on every edge", "dBc/Hz", "−159.9 at 3.3 V pp")],
    "Noise moves the edge by noise/slope; independent jitter on every edge gives a flat phase-noise floor.",
    "The slope of $\\tfrac{V_{pp}}{2}\\sin(2\\pi ft)$ at zero is $\\pi fV_{pp}$. White per-edge jitter σ sampled at "
    "$f_{ref}$ has $S_\\phi = 2(2\\pi f_{ref}\\sigma)^2/f_{ref}$, $\\mathcal L = S_\\phi/2$.",
    "σ = 0.23 ps at 50 MHz: $(2\\pi\\cdot5\\times10^7\\cdot2.3\\times10^{-13})^2/5\\times10^7 = 1.0\\times10^{-16}$ → −160 dBc/Hz.")),
]
