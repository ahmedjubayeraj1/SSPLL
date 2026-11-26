"""Phase 0 — the toolkit (version 2 only): the mathematics, circuit and noise ideas every later phase uses,
taught from zero with one worked number per equation. Build: SSPLL_V2=1 python3 learn/build/phase0.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nb import Book
from v2_eq import EXPLAIN, E

# boxes for the toolkit's own equations (put in front so they are found first)
EXPLAIN[:0] = [
("v(t) = A\\sin(\\omega t + \\phi_0)", E(
    [("$v(t)$", "the voltage at time t", "V", "—"),
     ("$A$", "amplitude (peak value)", "V", "e.g. 0.5 V"),
     ("$\\omega$", "angular frequency: how many radians per second", "rad/s", "$2\\pi\\cdot50$ MHz $= 3.14\\times10^8$"),
     ("$f$", "frequency: cycles per second", "Hz", "50 MHz"),
     ("$T$", "period: seconds per cycle", "s", "20 ns"),
     ("$\\phi_0$", "starting phase (where in the cycle we are at t = 0)", "rad", "—")],
    "A sine is a rotating pointer seen from the side: it turns $\\omega$ radians every second, starting at angle $\\phi_0$.",
    "One full turn is 2π radians, and the pointer makes f turns per second, so $\\omega = 2\\pi f$ and $T = 1/f$.",
    "50 MHz: $T = 1/(50\\times10^6) = 20$ ns; $\\omega = 2\\pi\\cdot50\\times10^6 = 3.14\\times10^8$ rad/s.")),
("\\phi(t) = \\phi_0 + \\int_0^t \\omega(\\tau)", E(
    [("$\\phi(t)$", "total angle turned up to time t", "rad", "—"),
     ("$\\omega(\\tau)$", "frequency at each earlier instant τ (may change)", "rad/s", "—"),
     ("$\\Delta\\phi$", "phase difference between two oscillators", "rad", "—"),
     ("$\\Delta f$", "their frequency difference", "Hz", "—")],
    "Phase is the running total of frequency, like distance is the running total of speed.",
    "If the speed of rotation changes, the angle covered is the area under the speed-versus-time curve.",
    "Two clocks 1 kHz apart: their phase difference grows by $2\\pi\\cdot1000$ rad every second — one full cycle "
    "every millisecond.")),
("e^{j\\theta} = \\cos\\theta + j\\sin\\theta", E(
    [("$j$", "the imaginary unit, $j^2 = -1$ (engineers write j, mathematicians i)", "—", "—"),
     ("$\\theta$", "angle", "rad", "—"),
     ("$a + jb$", "a complex number: a point (a, b) in the plane", "—", "—"),
     ("$|a+jb|$", "its length (magnitude)", "—", "—"),
     ("$\\angle(a+jb)$", "its angle (phase) from the positive real axis", "rad or °", "—")],
    "A complex number is an arrow; $e^{j\\theta}$ is an arrow of length 1 at angle θ.",
    "Multiplying arrows multiplies lengths and adds angles — exactly what a chain of amplifiers and delays does to a "
    "sine. That is why circuits are analysed with complex numbers.",
    "$1 + j1$: length $\\sqrt2 = 1.414$, angle 45°. $1/(1+j1)$: length 0.707, angle −45°.")),
("\\text{dB} = 10\\log_{10}\\frac{P_2}{P_1}", E(
    [("$P_1, P_2$", "two powers", "W", "—"),
     ("$V_1, V_2$", "two voltages (across the same resistance)", "V", "—"),
     ("dBc", "dB relative to the carrier (the main tone)", "—", "—"),
     ("dBc/Hz", "dBc in a 1 Hz-wide slice of spectrum", "—", "—")],
    "Decibels turn ratios into additions: ×10 in power is +10 dB, ×2 is +3 dB; ×10 in voltage is +20 dB.",
    "Power goes with voltage squared, and $\\log(x^2) = 2\\log x$ — hence 10 for powers and 20 for voltages.",
    "N = 32 multiplies phase by 32, i.e. phase-noise power by $32^2$: $20\\log 32 = +30.1$ dB.")),
("H(s) = \\frac{1}{1 + sRC}", E(
    [("$H(s)$", "transfer function: output/input in the Laplace domain", "—", "—"),
     ("$s$", "complex frequency; for sine waves $s = j\\omega$", "1/s", "—"),
     ("$R$, $C$", "resistor, capacitor", "Ω, F", "—"),
     ("$\\omega_p = 1/RC$", "pole (corner) frequency", "rad/s", "—"),
     ("$|H(j\\omega)|$", "gain at frequency ω", "—", "—"),
     ("$\\angle H(j\\omega)$", "phase shift at ω", "°", "—")],
    "An RC low-pass passes slow signals, attenuates fast ones by 20 dB per decade above $1/RC$, and delays them by "
    "up to 90°.",
    "Voltage divider with the capacitor's impedance $1/sC$: $H = (1/sC)/(R + 1/sC) = 1/(1 + sRC)$. At "
    "$\\omega = 1/RC$ the denominator is $1 + j$: gain 0.707 (−3 dB), phase −45°.",
    "R = 10 kΩ, C = 10 pF: corner $1/(2\\pi\\cdot10^4\\cdot10^{-11}) = 1.6$ MHz. At 16 MHz the gain is 0.1 (−20 dB).")),
("\\frac{Y}{X} = \\frac{G}{1+G}", E(
    [("$X$, $Y$", "input and output of the feedback system", "—", "—"),
     ("$G$", "loop gain: gain once around the loop", "—", "—"),
     ("$1/(1+G)$", "error transfer: how much of the input is not followed", "—", "—"),
     ("$\\omega_c$", "crossover: frequency where $|G| = 1$", "rad/s", "—"),
     ("$PM = 180° + \\angle G(j\\omega_c)$", "phase margin", "°", "45–60° is healthy")],
    "Where the loop gain is large the output follows the input; where it is small the loop gives up.",
    "$Y = G(X - Y) \\Rightarrow Y(1+G) = GX$. If $G = 100$, $Y/X = 0.99$; if $G = 0.01$, $Y/X \\approx 0.01$. "
    "Trouble happens when $G \\approx -1$ (gain 1 and phase −180°): $1 + G \\to 0$ and the output explodes — "
    "phase margin keeps us away from that point.",
    "PM 50° → closed-loop peaking ≈ 1.3 dB and step overshoot ≈ 20 %; PM 30° → ≈ 6 dB and ≈ 40 %.")),
("\\frac{\\omega_n^2}{s^2 + 2\\zeta\\omega_n s + \\omega_n^2}", E(
    [("$\\omega_n$", "natural frequency: how fast the system responds", "rad/s", "—"),
     ("$\\zeta$", "damping factor: how much it rings", "—", "0.707 = 'just right'"),
     ("$t$", "time after a step", "s", "—"),
     ("overshoot", "how far the step response goes past its final value", "%", "$e^{-\\pi\\zeta/\\sqrt{1-\\zeta^2}}$")],
    "The standard second-order system: a mass on a spring with friction. ζ < 1 rings, ζ = 1 is critically "
    "damped, ζ > 1 is sluggish.",
    "Every PLL with a filter capacitor and a VCO has two integrators and behaves like this near its bandwidth.",
    "ζ = 0.5: overshoot $e^{-\\pi\\cdot0.5/0.866} = 16\\%$; ζ = 0.707: 4.3 %.")),
("f_{alias} = \\left|f - k f_s\\right|", E(
    [("$f$", "frequency of the signal being sampled", "Hz", "1.6 GHz (VCO)"),
     ("$f_s$", "sampling rate", "Hz", "50 MHz (reference)"),
     ("$k$", "the integer that brings the result into $0…f_s/2$", "—", "32"),
     ("$f_{alias}$", "the frequency the samples appear to have", "Hz", "0 when locked")],
    "Samples cannot tell a fast signal from a slow one that passes through the same sample points.",
    "Sampling at $f_s$ cannot distinguish $f$ from $f + kf_s$ because $\\sin(2\\pi(f + kf_s)nT_s) = \\sin(2\\pi fnT_s)$ "
    "(the extra phase is a whole number of turns).",
    "1.6001 GHz sampled at 50 MHz: $|1600.1 - 32\\cdot50| = 0.1$ MHz — the samples beat slowly at 100 kHz. This is "
    "exactly how the sub-sampling PD sees the VCO.")),
("\\overline{v_n^2} = 4kTR\\,\\Delta f", E(
    [("$\\overline{v_n^2}$", "mean-square noise voltage", "V²", "—"),
     ("$k$", "Boltzmann constant", "J/K", "$1.38\\times10^{-23}$"),
     ("$T$", "temperature", "K", "300 K"),
     ("$R$", "resistance", "Ω", "—"),
     ("$\\Delta f$", "bandwidth considered", "Hz", "—"),
     ("$4kTR$", "noise PSD of a resistor", "V²/Hz", "$1.66\\times10^{-20}R$")],
    "Every resistor makes a random noise voltage; its power grows with resistance, temperature and bandwidth.",
    "Thermal agitation of electrons (Johnson–Nyquist). 'White': the same density at every frequency.",
    "1 kΩ: $\\sqrt{4kT\\cdot1000} = 4$ nV/√Hz. Over 1 MHz: 4 µV rms.")),
("\\overline{v_C^2} = \\frac{kT}{C}", E(
    [("$\\overline{v_C^2}$", "total noise on a capacitor fed through a resistor", "V²", "—"),
     ("$C$", "capacitance", "F", "100 fF (sampler)")],
    "The noise left on a capacitor depends only on C, not on the resistor that charges it.",
    "Bigger R = more noise density ($4kTR$) but less bandwidth ($1/(4RC)$ noise bandwidth); the product is $kT/C$.",
    "100 fF: $\\sqrt{4.14\\times10^{-21}/10^{-13}} = 0.20$ mV rms; 1 pF: 64 µV.")),
("\\sigma^2 = \\int_{f_1}^{f_2} S(f)\\,df", E(
    [("$S(f)$", "power spectral density (noise power per Hz)", "V²/Hz or rad²/Hz", "—"),
     ("$\\sigma^2$", "total noise power (variance) in the band", "V² or rad²", "—"),
     ("$|H(j2\\pi f)|^2$", "power gain of a filter at f", "—", "—"),
     ("$\\sigma_{tot}^2 = \\sum\\sigma_i^2$", "independent noises add in power", "—", "—")],
    "Noise is described by how its power is spread over frequency; integrate to get the total; a filter multiplies "
    "the spectrum by $|H|^2$; independent noises add in squares.",
    "The square of the rms value is the area under the PSD (Parseval). Power, not amplitude, adds for uncorrelated "
    "signals because the cross terms average to zero.",
    "Noises of 3 and 4 units together: $\\sqrt{3^2+4^2} = 5$, not 7. Halving the biggest one helps most.")),
("I_D = \\frac{1}{2}\\mu C_{ox}\\frac{W}{L}", E(
    [("$I_D$", "drain current", "A", "—"),
     ("$\\mu C_{ox}$", "mobility × gate-oxide capacitance per area (process constant)", "A/V²", "≈ 270 µA/V² (nfet_01v8)"),
     ("$W$, $L$", "channel width and length", "µm", "—"),
     ("$V_{GS}$", "gate-source voltage", "V", "—"),
     ("$V_{TH}$", "threshold voltage", "V", "≈ 0.45 V (nfet_01v8)"),
     ("$V_{ov} = V_{GS} - V_{TH}$", "overdrive", "V", "0.1–0.3 V typical"),
     ("$g_m$", "transconductance: $dI_D/dV_{GS}$", "S", "—"),
     ("$g_m/I_D$", "efficiency: g_m per µA (max ≈ 25 V⁻¹ in weak inversion)", "1/V", "—"),
     ("$\\gamma$", "channel-noise factor", "—", "≈ 1")],
    "In saturation the current grows with the square of the overdrive; $g_m = 2I_D/V_{ov}$; the transistor's own "
    "channel noise is $4kT\\gamma g_m$ (thermal) plus flicker that grows at low frequency and falls with gate area.",
    "Square-law model: charge in the channel ∝ $C_{ox}V_{ov}$, speed ∝ μ·field. Differentiating gives $g_m$. Small "
    "$V_{ov}$ (moderate/weak inversion) gives the most $g_m$ per µA — used in the reference buffer.",
    "$I_D = 100$ µA at $V_{ov} = 0.2$ V → $g_m = 1$ mS, noise $\\sqrt{4kT\\cdot1\\,\\text{mS}} = 4$ pA/√Hz.")),
]

b = Book("Phase 0 — The toolkit: mathematics, circuits and noise from zero",
         "Everything the later phases assume, taught from the beginning: sine waves and phase, complex numbers, "
         "decibels, transfer functions and Bode plots, feedback and stability, second-order systems, sampling and "
         "aliasing, noise and how it adds, and the MOSFET facts a PLL designer uses every day. Each section ends with "
         "a few check-yourself questions.")

# ------------------------------------------------------------------------------------------------ T1
b.step("T1", "Sine waves, frequency, period and phase")
b.md(r"""
Every signal in a PLL is (close to) a sine wave or a square wave with the same timing. A sine is fully described by
three numbers: how big (amplitude), how fast (frequency), and where it starts (phase).
$$v(t) = A\sin(\omega t + \phi_0),\qquad \omega = 2\pi f,\qquad T = \frac1f$$
**Picture.** Imagine the hand of a clock turning steadily. Its height above the centre, plotted against time, is a sine.
The angle of the hand is the **phase**. How many turns per second is the **frequency**.
""")
b.code(r"""
t = np.linspace(0, 60e-9, 600)
def frame(ph):
    return ([dict(x=t*1e9, y=np.sin(2*np.pi*50e6*t), name="reference, phase 0"),
             dict(x=t*1e9, y=np.sin(2*np.pi*50e6*t + np.radians(ph)), name=f"shifted by {ph}°")],
            f"Two 50 MHz sines; a phase shift of {ph}° is a time shift of {ph/360*20:.1f} ns (= phase/360° × 20 ns)")
show(sweep([0, 30, 45, 90, 180, 270], frame, "phase shift (deg)", active=2,
           layout=lambda f: f.update_xaxes(title="time (ns)").update_yaxes(title="v (V)")))
""")
b.md(r"""
**Try it.** A phase of 90° is a quarter of the period (5 ns at 50 MHz); 360° is a whole period, which looks identical
to 0°. Phase and time are the same thing measured in different units: $\Delta t = \dfrac{\Delta\phi}{2\pi f}$.
That one line converts every phase-noise number into jitter later.
""")
b.qa([("What is the period of a 1.6 GHz clock?", "$T = 1/1.6\\times10^9 = 625$ ps."),
      ("How many seconds is 1 mrad of phase at 1.6 GHz?", "$\\Delta t = 10^{-3}/(2\\pi\\cdot1.6\\times10^9) = 0.1$ ps."),
      ("Why use ω instead of f?", "Derivatives of $\\sin(\\omega t)$ give $\\omega\\cos(\\omega t)$ — equations stay free of 2π factors.")], "T1")

# ------------------------------------------------------------------------------------------------ T2
b.step("T2", "Phase is the integral of frequency")
b.md(r"""
The single most important idea for PLLs:
$$\phi(t) = \phi_0 + \int_0^t \omega(\tau)\,d\tau \qquad\Longleftrightarrow\qquad \omega(t) = \frac{d\phi}{dt}$$
If two oscillators differ in frequency by $\Delta f$, their phase difference grows like a ramp: $\Delta\phi = 2\pi\Delta f\,t$.
A loop that keeps the phase difference *constant* therefore forces the frequencies to be *exactly equal*. That is how a
PLL gets perfect frequency accuracy.
""")
b.code(r"""
t = np.linspace(0, 10e-6, 400)
def frame(df_khz):
    return ([dict(x=t*1e6, y=np.degrees(2*np.pi*df_khz*1e3*t), name="phase difference")],
            f"Frequency difference {df_khz} kHz → the phase difference grows {df_khz*360/1000:.2f}° per µs")
show(sweep([10, 50, 100, 500, 1000], frame, "Δf (kHz)", active=2,
           layout=lambda f: f.update_xaxes(title="time (µs)").update_yaxes(title="phase difference (deg)")))
""")
b.qa([("A VCO is 100 kHz too fast for 5 µs. How much extra phase does it collect?", "$2\\pi\\cdot10^5\\cdot5\\times10^{-6} = \\pi$ rad = 180° — half a cycle."),
      ("Why is a VCO an integrator in a PLL?", "The control voltage sets frequency; the loop compares phase; phase is the integral of frequency → $K_{VCO}/s$.")], "T2")

# ------------------------------------------------------------------------------------------------ T3
b.step("T3", "Complex numbers and phasors")
b.md(r"""
A sine wave of one frequency can be represented by one complex number (a *phasor*): its length is the amplitude, its
angle is the phase.
$$e^{j\theta} = \cos\theta + j\sin\theta,\qquad |a + jb| = \sqrt{a^2+b^2},\qquad \angle(a+jb) = \arctan\frac{b}{a}$$
A circuit acting on a sine multiplies its phasor by a complex gain: it scales the amplitude and rotates the phase.
Chains of blocks multiply gains and **add phases** — the reason loop phase is a sum of terms like $-90°$ and
$+\arctan(\omega/\omega_z)$.
""")
b.qa([("What are the magnitude and angle of $j$?", "Length 1, angle +90°. Multiplying by $j$ is a quarter-turn — a 90° phase lead."),
      ("What does dividing by $j\\omega$ do to a sine?", "Scales it by $1/\\omega$ and delays it by 90° — that is integration.")], "T3")

# ------------------------------------------------------------------------------------------------ T4
b.step("T4", "Decibels: dB, dBc, dBc/Hz")
b.md(r"""
$$\text{dB} = 10\log_{10}\frac{P_2}{P_1} = 20\log_{10}\frac{V_2}{V_1}$$
| Ratio | Power | Voltage |
|---|---|---|
| ×2 | +3 dB | +6 dB |
| ×10 | +10 dB | +20 dB |
| ×100 | +20 dB | +40 dB |
| ×1/1000 | −30 dB | −60 dB |

Phase noise is quoted in **dBc/Hz**: how strong the noise is in a 1 Hz slice, compared with the carrier. −120 dBc/Hz
means the noise in each hertz is $10^{-12}$ of the carrier power.
""")
b.qa([("−110 dBc/Hz vs −120 dBc/Hz: how much more noise power?", "10 dB = 10× more."),
      ("Multiplying a clock by 32 changes phase noise by?", "+20 log 32 = +30.1 dB.")], "T4")

# ------------------------------------------------------------------------------------------------ T5
b.step("T5", "Transfer functions, poles, zeros and Bode plots")
b.md(r"""
A **transfer function** says how much of an input sine of frequency ω comes out, and with what phase. Use the Laplace
variable $s$ (set $s = j\omega$ for sines). Two building blocks explain every PLL filter:

- **Integrator** $1/s$: gain $1/\omega$, i.e. falls 20 dB per decade, with phase −90° everywhere.
- **RC low-pass** (one pole):
$$H(s) = \frac{1}{1 + sRC}$$
  It is flat below $1/RC$ and falls 20 dB/decade above it, with a phase going from 0 to −90°.
- **Zero** $(1 + s/\omega_z)$: the mirror image — the gain *rises* above $\omega_z$ and the phase goes *up* by up to 90°.
  The loop-filter zero exists to give phase back.

A **Bode plot** shows gain (dB) and phase (degrees) against log frequency. Products become sums, so you can sketch it
by adding straight-line pieces.
""")
b.code(r"""
f = np.logspace(3, 9, 400)
def frame(R_k):
    H = 1/(1 + 2j*np.pi*f*R_k*1e3*10e-12)
    fp = 1/(2*np.pi*R_k*1e3*10e-12)
    return ([dict(x=f, y=20*np.log10(abs(H)), name="gain (dB)", row=1, col=1),
             dict(x=f, y=np.degrees(np.angle(H)), name="phase (deg)", row=2, col=1)],
            f"RC low-pass, C = 10 pF, R = {R_k} kΩ: corner 1/(2πRC) = {fp/1e6:.2f} MHz (−3 dB and −45° there)")
fig = sweep([1, 3, 10, 30, 100], frame, "R (kΩ)", rows=2, cols=1, shared_xaxes=True, active=2, height=560,
            layout=lambda f: (f.update_xaxes(type="log"), f.update_xaxes(title="frequency (Hz)", row=2, col=1)))
show(fig)
""")
b.qa([("What is the gain of a 1 MHz RC low-pass at 10 MHz?", "About −20 dB (×0.1), phase ≈ −84°."),
      ("Why does a loop filter have a zero?", "Two integrators give −180°; a zero adds up to +90° near crossover so the loop is stable.")], "T5")

# ------------------------------------------------------------------------------------------------ T6
b.step("T6", "Feedback, loop gain, stability and second-order systems")
b.md(r"""
Feed the output back and subtract it from the input. With forward gain G:
$$\frac{Y}{X} = \frac{G}{1+G},\qquad \frac{X - Y}{X} = \frac{1}{1+G}$$
Large $|G|$ → the output follows; small $|G|$ → the loop does nothing. **Stability:** if at the frequency where
$|G| = 1$ the phase of G is close to −180°, the correction arrives late enough to *add* instead of subtract, and the
loop rings or oscillates. **Phase margin** measures how far from −180° we are.

A PLL with a filter capacitor and a VCO responds like a mass on a spring:
$$H(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$
""")
b.code(r"""
t = np.linspace(0, 12, 600)          # time in units of 1/omega_n
def frame(z):
    if z < 1:
        wd = np.sqrt(1 - z*z)
        y = 1 - np.exp(-z*t)*(np.cos(wd*t) + z/wd*np.sin(wd*t))
    elif z == 1:
        y = 1 - np.exp(-t)*(1 + t)
    else:
        r1, r2 = -z + np.sqrt(z*z - 1), -z - np.sqrt(z*z - 1)
        y = 1 + (r2*np.exp(r1*t) - r1*np.exp(r2*t))/(r1 - r2)
    os_ = 100*(y.max() - 1)
    return ([dict(x=t, y=y, name="step response")], f"ζ = {z}: overshoot {max(os_, 0):.1f} %")
show(sweep([0.2, 0.3, 0.5, 0.707, 1.0, 2.0], frame, "damping ζ", active=3,
           layout=lambda f: f.update_xaxes(title="time × ω_n").update_yaxes(title="output (final value 1)", range=[0, 1.7])))
""")
b.qa([("What happens to a loop with 0° phase margin?", "It oscillates at the crossover frequency."),
      ("Which damping gives no overshoot and the fastest settling?", "ζ ≈ 1 (critical); ζ = 0.707 settles about as fast with 4 % overshoot.")], "T6")

# ------------------------------------------------------------------------------------------------ T7
b.step("T7", "Sampling and aliasing")
b.md(r"""
A sampler looks at a signal only at instants $nT_s$. It cannot tell apart frequencies that differ by multiples of $f_s$:
$$f_{alias} = \left|f - k f_s\right|$$
A sample-and-hold keeps each sample for one period, which acts like a delay of half a period ($T_s/2$). Both facts
matter in a sub-sampling PLL: the 1.6 GHz VCO sampled at 50 MHz looks like DC when locked (alias at 0 Hz), and the
hold delay costs phase margin.
""")
b.code(r"""
t = np.linspace(0, 400e-9, 4000); ts = np.arange(0, 400e-9, 20e-9)
def frame(df_mhz):
    f = 1.6e9 + df_mhz*1e6
    return ([dict(x=t*1e9, y=np.sin(2*np.pi*f*t), name="VCO (fast)", line=dict(width=0.5)),
             dict(x=ts*1e9, y=np.sin(2*np.pi*f*ts), name="samples every 20 ns", mode="markers+lines", marker=dict(size=8))],
            f"VCO 1.6 GHz + {df_mhz} MHz sampled at 50 MHz: the samples trace a {abs(df_mhz):.2g} MHz sine (alias)")
show(sweep([0, 0.5, 1, 2, 5], frame, "VCO offset (MHz)", active=2,
           layout=lambda f: f.update_xaxes(title="time (ns)").update_yaxes(title="v")))
""")
b.qa([("What do the samples show when the VCO is exactly 32 × 50 MHz?", "A constant value — the phase of the VCO at the sampling edge."),
      ("Can the sampler tell 1.60 GHz from 1.65 GHz?", "No: both alias to 0 Hz. That is why an FLL first brings the VCO near the right harmonic.")], "T7")

# ------------------------------------------------------------------------------------------------ T8
b.step("T8", "Noise: resistors, capacitors, spectra and how noise adds")
b.md(r"""
Noise is random, so we describe it by its **power** and how that power is spread over frequency (the power spectral
density, PSD).
- A resistor: $$\overline{v_n^2} = 4kTR\,\Delta f$$
- A capacitor charged through any resistor keeps $$\overline{v_C^2} = \frac{kT}{C}$$
- Total noise in a band and through a filter: $$\sigma^2 = \int_{f_1}^{f_2} S(f)\,df,\qquad S_{out}(f) = |H(j2\pi f)|^2 S_{in}(f)$$
- Independent noises add in **power**: $\sigma_{tot} = \sqrt{\sigma_1^2 + \sigma_2^2 + \dots}$

The figure shows the kT/C result: change R and the total noise on the capacitor stays the same.
""")
b.code(r"""
f = np.logspace(3, 11, 800); C = 100e-15
def frame(R_k):
    R = R_k*1e3
    S = 4*kT*R/(1 + (2*np.pi*f*R*C)**2)
    tot = np.sqrt(np.trapezoid(S, f))
    return ([dict(x=f, y=np.sqrt(S)*1e9, name="noise density on C")],
            f"R = {R_k} kΩ, C = 100 fF: total {tot*1e3:.3f} mV rms (kT/C = {np.sqrt(kT/C)*1e3:.3f} mV) — independent of R")
show(sweep([0.1, 1, 10, 100], frame, "R (kΩ)", active=1,
           layout=lambda f: f.update_xaxes(type="log", title="frequency (Hz)").update_yaxes(type="log", title="nV/√Hz")))
""")
b.qa([("Two independent noises of 1 ps and 1 ps: total?", "√2 ps = 1.41 ps, not 2 ps."),
      ("Why does a bigger sampling capacitor reduce SSPD noise?", "Its kT/C noise falls as 1/C.")], "T8")

# ------------------------------------------------------------------------------------------------ T9
b.step("T9", "MOSFET facts a PLL designer uses every day")
b.md(r"""
In saturation (long-channel square law):
$$I_D = \frac{1}{2}\mu C_{ox}\frac{W}{L}\left(V_{GS} - V_{TH}\right)^2,\qquad g_m = \frac{2I_D}{V_{ov}},\qquad
\overline{i_n^2} = 4kT\gamma g_m\,\Delta f + \frac{K_f}{C_{ox}WL}\frac{I_D^{a}}{f}\Delta f$$
- $g_m/I_D$ tells how much transconductance each µA buys: about 10 V⁻¹ in strong inversion, up to ~25 V⁻¹ in weak.
- Longer L: more output resistance, better matching, less flicker noise — but slower.
- **SKY130 devices used here:**
  - `nfet_01v8` / `pfet_01v8`: 1.8 V core devices, L ≥ 0.15 µm (fast; ring, SSPD, logic).
  - `*_g5v0d10v5`: 3.3 V-tolerant devices, L ≥ 0.5 µm (anything on VDDA or a pad).
  - `res_xhigh_po_*`: high-value poly resistors.
  - `cap_mim_m3_1`: MIM capacitors, about 2 fF/µm², placed over active circuits.
""")
b.qa([("Why are the CCO and reference-buffer devices thick-oxide?", "They connect to 3.3 V or a pad; thin-oxide devices are rated for 1.8 V."),
      ("How do you get more g_m without more current?", "Lower the overdrive (wider device, moderate inversion): higher g_m/I_D — at the cost of area and speed.")], "T9")

b.save(os.path.join(os.path.dirname(__file__), "..", "phase0_toolkit.ipynb"))
