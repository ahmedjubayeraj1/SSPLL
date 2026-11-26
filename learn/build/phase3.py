"""Phase 3 - Type-II charge-pump PLL, its limits and fixes (roadmap steps 33-45). Part A: steps 33-39."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nb import Book

b = Book("Phase 3 — Type-II charge-pump PLL: operation, limits and fixes (steps 33–45)",
         "The charge pump plus capacitor adds a second integrator: the static phase error disappears, but two integrators "
         "give −180° and the loop needs a resistor (a zero) to be stable. This phase derives the CP-PLL completely, designs "
         "one for our frequency plan (50 MHz × 32 = 1.6 GHz) — the simulated Type-II baseline of the step-8 decision — "
         "and then shows the three limits that push a ring-oscillator design toward the sub-sampling PLL: N² noise, "
         "charge-pump spurs, and the bandwidth ceiling.")

# ------------------------------------------------------------------------------------------------ step 33
b.step(33, "The phase-frequency detector", "three states, reset path, frequency detection, dead zone")
b.md(r"""
### What happens
A PFD has two D flip-flops (D tied high) clocked by REF and DIV, and an AND gate that resets both. A REF edge sets **UP**; a DIV
edge sets **DN**; when both are high the AND resets them after a short delay $t_{rst}$.

### How (three states)
| State | UP | DN | Leaves on |
|---|---|---|---|
| S0 (idle) | 0 | 0 | REF edge → S+, DIV edge → S− |
| S+ (REF leads) | 1 | 0 | DIV edge → reset → S0 |
| S− (DIV leads) | 0 | 1 | REF edge → reset → S0 |

The UP (or DN) pulse width equals the time between the edges: $t_{UP} = \frac{\Delta\phi}{2\pi}T_{REF}$, linear over $\pm2\pi$.

**Frequency detection.** If REF is faster, two REF edges can arrive between DIV edges; the second finds the PFD already in S+, so
UP stays high most of the time and the average output keeps the sign of the frequency error. This gives unlimited pull-in.

**Dead zone.** For very small $\Delta\phi$ the UP pulse is too short for the charge-pump switches to turn on fully; no charge flows,
so the loop gain is zero near lock and the phase wanders inside a band (jitter). **Fix:** the reset delay $t_{rst}$ keeps *both*
UP and DN on for a minimum time every cycle, so even tiny differences produce a proportional net charge.
""")
b.code(r"""
def pfd_sim(f_ratio, ncyc=40, phi0=0.3):
    # edges: REF at k/1, DIV at (k + phi0)/f_ratio ; returns time axis and UP-DN state
    tr = np.arange(0, ncyc+1)*1.0
    td = (np.arange(0, int(ncyc*f_ratio)+2) + phi0)/f_ratio
    ev = sorted([(t, "R") for t in tr] + [(t, "D") for t in td])
    t_axis = np.linspace(0, ncyc, 8000); st = np.zeros_like(t_axis)
    s, last = 0, 0.0
    times, states = [0.0], [0]
    for t, e in ev:
        if e == "R": s = 0 if s == -1 else 1
        else:        s = 0 if s == 1 else -1
        times.append(t); states.append(s)
    idx = np.searchsorted(times, t_axis, side="right") - 1
    return t_axis, np.array(states)[idx]
def frame(r):
    t, s = pfd_sim(r)
    return ([dict(x=t, y=s, name="UP - DN (PFD state)", line=dict(shape="hv")),
             dict(x=t, y=np.cumsum(s)/(np.arange(len(s))+1), name="running average")],
            f"f_REF / f_DIV = {r}: average output {s.mean():+.2f} -> " + ("equal frequencies: the average is just the 0.3-cycle phase error"
            if r == 1.0 else "pushes VCO up" if s.mean() > 0 else "pushes VCO down"))
fig = sweep([0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.25], frame, "f_REF / f_DIV", active=4,
            layout=lambda f: f.update_xaxes(title="time (reference periods)").update_yaxes(range=[-1.2, 1.2]))
show(fig, 420)
""")
b.code(r"""
# Dead zone: average CP current vs phase error when pulses shorter than t_on produce no current
dphi = np.linspace(-0.2, 0.2, 801)                                # rad
T = 20e-9; ton = 150e-12                                           # charge-pump turn-on time
def avg_current(dp, trst):
    w = abs(dp)/(2*np.pi)*T                                         # PFD pulse width
    if trst == 0:
        eff = np.maximum(w - ton, 0)                                # pulse must exceed t_on
    else:
        eff = np.where(trst > ton, w, np.maximum(w + trst - ton, 0) - np.maximum(trst - ton, 0))
    return np.sign(dp)*eff/T
fig = go.Figure()
for trst, nm in ((0, "no reset delay: dead zone"), (100e-12, "t_rst = 100 ps (< t_on)"), (300e-12, "t_rst = 300 ps (> t_on): linear")):
    fig.add_trace(go.Scatter(x=np.degrees(dphi), y=avg_current(dphi, trst), name=nm))
fig.update_xaxes(title="phase error (deg)").update_yaxes(title="average current / I_p")
show(fig, 400)
""")
b.qa([
    ("Draw and explain the PFD state diagram.",
     "Three states: idle (UP = DN = 0), UP (REF edge came first), DN (DIV edge came first). The opposite edge moves it back to idle through the reset path."),
    ("Why does the PFD detect frequency?",
     "When one input is faster, it delivers more edges; the PFD stays in that input's state most of the time, so the average output has the sign of the frequency difference."),
    ("What is the linear range of a PFD?",
     "±2π (±one reference period). Beyond that it wraps and the characteristic becomes periodic with a sawtooth shape (but keeps the right sign on average in frequency mode)."),
    ("What is the dead zone and why does it matter?",
     "A range of small phase errors where the CP produces no net charge because the pulses are too short to turn the switches on. The loop gain is zero there, so phase wanders randomly — extra jitter."),
    ("How does a reset delay remove the dead zone?",
     "Both UP and DN stay on for at least $t_{rst}$ each cycle, so the switches are always fully on; the net charge is $I_p\\times$ (difference of pulse widths), linear down to zero."),
    ("What does the reset delay cost?",
     "Both currents flow every cycle: any UP/DN mismatch now creates a net charge pulse every period → static phase offset and reference spurs; also more CP noise injected."),
    ("What limits the maximum operating frequency of a PFD?",
     "The reset path delay: an edge arriving during reset is missed. The PFD fails above roughly $1/(2t_{reset})$ and its range shrinks to $2\\pi(1 - t_{rst}/T)$."),
    ("Why is the PFD input the divided VCO and not the VCO itself?",
     "The flip-flops and charge pump cannot run at the VCO frequency, and the comparison must be at $f_{REF}$; hence the divider and its N² penalty."),
    ("What is a 'missing edge' and when does it occur?",
     "During acquisition, two edges of one input between edges of the other; the PFD ignores the extra edge. That is exactly what gives it frequency detection."),
    ("How is a PFD different from a bang-bang PD?",
     "A PFD gives a pulse width proportional to the phase error (linear); a bang-bang PD gives only its sign."),
    ("In our SSPLL, where is a PFD used?",
     "Only in the FLL: REF vs the /32 divider output, with a dead zone added on purpose so it is silent once the phase error is small."),
    ("Why would we *want* a dead zone in the FLL?",
     "So the FLL stops injecting noise and spurs after frequency acquisition; inside the dead zone only the SSPD loop acts."),
], 33)

# ------------------------------------------------------------------------------------------------ step 34
b.step(34, "Charge pump into a bare capacitor: why it cannot be stable, and why a series R fixes it", "Bode plots")
b.md(r"""
### What happens
PFD + CP + a single capacitor $C_1$ + VCO: the loop locks at first glance but rings forever.

### How
$$G(s) = \frac{I_p}{2\pi}\cdot\frac{1}{C_1s}\cdot\frac{K_{VCO}}{Ns} = \frac{I_pK_{VCO}}{2\pi NC_1}\cdot\frac{1}{s^2}\quad\Rightarrow\quad
\angle G = -180°\ \text{at all }\omega.$$
Closed loop: $H \propto \frac{1}{s^2+\omega_n^2}$, poles at $\pm j\omega_n$ — an undamped oscillator (ζ = 0).

Adding $R_1$ in series with $C_1$: $Z = R_1 + \frac{1}{C_1 s}$, so
$$G(s) = \frac{I_pK_{VCO}}{2\pi NC_1}\cdot\frac{1+sR_1C_1}{s^2}:$$
a zero at $\omega_z = 1/R_1C_1$ adds up to +90°.

### Why physically
With only $C_1$, the control voltage is the *integral* of past phase error: by the time the phase error reaches zero, $V_{cont}$
has overshot. The resistor adds a term *proportional* to the present phase error ($I_pR_1$ during each pulse) — an immediate
correction, like the "P" in a PI controller, which damps the loop.
""")
b.code(r"""
from scipy import signal
Ip, Kv, N = 100e-6, 2*np.pi*300e6, 32
d = sl.loop_design_type2(2.5e6, 60, Ip, Kv, N); C1 = d['C1'] + d['C2']
f = np.logspace(4, 9, 400); s = 2j*np.pi*f; t = np.linspace(0, 4e-6, 2000)
def frame(Rk):
    R = Rk*1e3
    G = Ip*Kv/(2*np.pi*N*C1)*(1+s*R*C1)/s**2
    k = Ip*Kv/(2*np.pi*N*C1)
    _, y = signal.step(signal.lti([k*R*C1, k], [1, k*R*C1, k]), T=t)
    pm = 180 + np.degrees(np.angle(G[np.argmin(abs(abs(G)-1))]))
    return ([dict(x=f, y=20*np.log10(abs(G)), name="|G| (dB)", row=1, col=1),
             dict(x=f, y=np.degrees(np.angle(G)), name="phase G (deg)", row=1, col=2),
             dict(x=t*1e6, y=y, name="phase-step response H/N", row=2, col=1)],
            f"R1 = {Rk} kOhm: phase margin {pm:.0f} deg" + ("  (C only: undamped oscillation)" if Rk == 0 else ""))
fig = sweep([0, 1, 2, 5, 10, 18, 40], frame, "R1 (kOhm)", active=5, rows=2, cols=2,
            subplot_titles=("|G|", "phase of G", "step response", ""), height=620,
            layout=lambda f: f.update_xaxes(type="log", row=1, col=1).update_xaxes(type="log", row=1, col=2)
                              .update_yaxes(range=[-185, -80], row=1, col=2).update_yaxes(range=[0, 2.1], row=2, col=1)
                              .update_xaxes(title_text="time (us)", row=2, col=1))
show(fig)
""")
b.qa([
    ("Why is a CP-PLL with only a capacitor unstable?",
     "Two integrators: $G\\propto1/s^2$, phase −180° everywhere, phase margin 0; closed-loop poles on the imaginary axis."),
    ("What does R1 add in the s-domain and physically?",
     "A zero at $1/R_1C_1$ (+90° phase). Physically, a proportional path: $V_{cont}$ jumps by $I_pR_1$ during each pulse, correcting in proportion to the present error."),
    ("What is the PI-controller analogy?",
     "$Z = R_1 + 1/(sC_1)$ is proportional (R1) plus integral (C1) control of the phase error."),
    ("What is the side effect of R1?",
     "A voltage step $I_pR_1$ on $V_{cont}$ every time the CP turns on → ripple → spurs; hence C2."),
    ("If R1 = 0, what frequency does the loop ring at?",
     "$\\omega_n = \\sqrt{I_pK_{VCO}/(2\\pi NC_1)}$."),
    ("Can you stabilise the loop with a zero elsewhere?",
     "Yes: e.g. a feedforward proportional path (a second CP into a resistor, or a dual-path filter) creates the zero without a series resistor; used to shrink C1."),
    ("Does R1 change the steady-state phase error?",
     "No: the integrator (C1) still guarantees zero error for a frequency step."),
    ("What happens to phase margin as R1 grows very large?",
     "In the 2nd-order model it approaches 90°; with C2 present, crossover moves toward the third pole and PM drops again."),
    ("How does R1 thermal noise appear at the output?",
     "As a voltage on $V_{cont}$, converted by $K_{VCO}$ and shaped like VCO noise (high-pass by the loop); larger R1 means more noise."),
], 34)

# ------------------------------------------------------------------------------------------------ step 35
b.step(35, "The second-order Type-II loop: H(s), ω_n, ζ, and the zero's peaking", "derivation and plots")
b.md(r"""
### How (Razavi, *RF Microelectronics* §9.3; divider included)
$$G(s) = \frac{I_pK_{VCO}}{2\pi NC_1}\frac{1+sR_1C_1}{s^2},\qquad
\frac{H(s)}{N} = \frac{G}{1+G} = \frac{2\zeta\omega_n s + \omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$
$$\boxed{\omega_n = \sqrt{\frac{I_pK_{VCO}}{2\pi NC_1}},\qquad \zeta = \frac{R_1}{2}\sqrt{\frac{I_pC_1K_{VCO}}{2\pi N}}}$$
The zero of $H$ at $\omega_n/(2\zeta)$ makes $|H/N| > 1$ near $\omega_n$ (**peaking**) for any ζ, unlike a pure second-order
low-pass. For ζ ≥ 1 the poles are real; the −3 dB bandwidth is about $2\zeta\omega_n$ for large ζ.

### Why it matters
ζ grows with $R_1$ and with $\sqrt{I_pK_{VCO}}$; bandwidth grows with $\sqrt{I_pK_{VCO}/C_1}$. Since $K_{VCO}$ varies with PVT, both
move together — designs check the extremes. Peaking amplifies in-band noise and is the reason "too much" bandwidth hurts.
""")
b.code(r"""
from scipy import signal
f = np.logspace(4, 9, 500); t = np.linspace(0, 3e-6, 1500); wn = 2*np.pi*1e6
def frame(z):
    num, den = [2*z*wn, wn**2], [1, 2*z*wn, wn**2]
    w, mag, _ = signal.bode(signal.lti(num, den), w=2*np.pi*f)
    _, y = signal.step(signal.lti(num, den), T=t)
    return ([dict(x=f, y=mag, name="|H/N| (dB)", row=1, col=1),
             dict(x=t*1e6, y=y, name="phase-step response", row=1, col=2)],
            f"zeta = {z}: peaking {mag.max():.2f} dB, overshoot {100*(y.max()-1):.0f} %, f_-3dB = {f[np.where(mag > -3)[0][-1]]/1e6:.2f} MHz (f_n = 1 MHz)")
fig = sweep([0.3, 0.5, 0.707, 1.0, 1.5, 2.0, 3.0], frame, "zeta", active=2, rows=1, cols=2,
            subplot_titles=("closed-loop magnitude", "step response"), height=420,
            layout=lambda f: f.update_xaxes(type="log", title_text="Hz", row=1, col=1).update_yaxes(range=[-30, 8], row=1, col=1)
                              .update_xaxes(title_text="time (us)", row=1, col=2))
show(fig)
""")
b.qa([
    ("Derive ω_n and ζ of the second-order CP-PLL.",
     "From $1+G = 0$: $s^2 + \\frac{I_pK_{VCO}R_1}{2\\pi N}s + \\frac{I_pK_{VCO}}{2\\pi NC_1} = 0$ → $\\omega_n^2 = I_pK_{VCO}/(2\\pi NC_1)$, $2\\zeta\\omega_n = I_pK_{VCO}R_1/(2\\pi N)$ → $\\zeta = \\frac{R_1}{2}\\sqrt{I_pC_1K_{VCO}/(2\\pi N)}$."),
    ("Why does a Type-II loop show peaking even with ζ = 1?",
     "The closed-loop zero at $\\omega_n/2\\zeta$ lifts the response before the poles roll it off; ζ = 1 still peaks ~1.25 dB."),
    ("How does ζ depend on I_p and K_VCO?",
     "$\\zeta\\propto\\sqrt{I_pK_{VCO}}$: a 2× spread in $K_{VCO}$ changes ζ by 1.41× and ω_n by 1.41×."),
    ("What is the bandwidth for large ζ?",
     "Approximately $2\\zeta\\omega_n = I_pK_{VCO}R_1/(2\\pi N)$ — set by R1, the CP and the VCO, independent of C1."),
    ("What is the settling time to 1% for a second-order loop?",
     "Approximately $\\ln(100)/(\\zeta\\omega_n) = 4.6/(\\zeta\\omega_n)$ for ζ < 1."),
    ("Why do CP-PLL designers often use ζ ≈ 0.7–1?",
     "Compromise between peaking/overshoot and settling speed; noise peaking and lock time are both reasonable."),
    ("What changes if N doubles with the same filter?",
     "ω_n falls by $\\sqrt2$, ζ falls by $\\sqrt2$, in-band noise rises 6 dB."),
    ("Write H(s) in terms of ω_n and ζ.",
     "$H/N = (2\\zeta\\omega_ns + \\omega_n^2)/(s^2 + 2\\zeta\\omega_ns + \\omega_n^2)$."),
    ("Is the second-order model good enough for design?",
     "For a first estimate; real loops add C2 (third pole), parasitic poles and the sampling delay, so final PM is checked with the third-order and sampled-data models."),
    ("What does the closed-loop zero mean for jitter transfer?",
     "Jitter (and noise) from the reference is amplified by the peaking near ω_n; important in cascaded PLLs and CDR jitter-transfer specs."),
], 35)

# ------------------------------------------------------------------------------------------------ step 36
b.step(36, "Third order: C2 for ripple, pole placement, phase-margin optimum vs C1/C2", "design curves")
b.md(r"""
### What happens
$C_2$ from $V_{cont}$ to ground smooths the $I_pR_1$ steps. It adds a pole $\omega_{p3} = \frac{C_1+C_2}{R_1C_1C_2}$.

### How
With $b^2 = \omega_{p3}/\omega_z = 1 + C_1/C_2$ and crossover at the geometric mean,
$$PM_{max} = \arctan b - \arctan\frac1b = \arctan\frac{b^2-1}{2b}.$$
And the crossover condition gives the closed-form design (used throughout this project, `sl.loop_design_type2`):
$$C_{tot} = C_1+C_2 = \frac{b\,I_pK_{VCO}}{2\pi N\omega_c^2},\quad C_2 = \frac{C_{tot}}{b^2},\quad C_1 = C_{tot}-C_2,\quad R_1 = \frac{b}{\omega_cC_1}.$$

### Why there is a trade-off
Bigger $C_2$ (smaller $C_1/C_2$) → better ripple filtering (lower spurs) but the pole approaches crossover → less PM. Smaller $C_2$ →
more PM but the third pole moves up and filters the ripple less.
""")
b.code(r"""
ratio = np.logspace(0, 2.5, 200)
bb = np.sqrt(1+ratio)
pm = np.degrees(np.arctan(bb) - np.arctan(1/bb))
fig = go.Figure(go.Scatter(x=ratio, y=pm, name="max phase margin"))
for r, lab in ((4.83, "45 deg"), (12.9, "60 deg"), (32.2, "70 deg")):
    fig.add_trace(go.Scatter(x=[r], y=[np.degrees(np.arctan(np.sqrt(1+r)) - np.arctan(1/np.sqrt(1+r)))], mode="markers+text",
                             text=[f"C1/C2 = {r}"], textposition="top left", marker=dict(size=10), name=lab))
fig.update_xaxes(type="log", title="C1 / C2").update_yaxes(title="maximum phase margin (deg)")
show(fig, 400)
""")
b.code(r"""
Ip, Kv, N = 100e-6, 2*np.pi*300e6, 32
f = np.logspace(4, 9, 400); s = 2j*np.pi*f
def frame(pm_t):
    d = sl.loop_design_type2(2.5e6, pm_t, Ip, Kv, N)
    Z = (1+s*d['R']*d['C1'])/(s*(d['C1']+d['C2'])*(1+s*d['R']*d['C1']*d['C2']/(d['C1']+d['C2'])))
    G = Ip/(2*np.pi)*Z*Kv/(N*s)
    step = Ip*d['R']*d['C1']/(d['C1']+d['C2'])   # V_cont jump at the start of a CP pulse (charge splits)
    return ([dict(x=f, y=20*np.log10(abs(G)), name="|G| (dB)", row=1, col=1),
             dict(x=f, y=np.degrees(np.unwrap(np.angle(G))), name="phase G", row=1, col=2)],
            f"PM {pm_t} deg at f_c = 2.5 MHz: C1/C2 = {d['C1']/d['C2']:.1f}, C1 = {d['C1']*1e12:.1f} pF, C2 = {d['C2']*1e12:.2f} pF, "
            f"R1 = {d['R']/1e3:.1f} kOhm, zero {d['fz']/1e6:.2f} MHz, pole {d['fp']/1e6:.1f} MHz")
fig = sweep([40, 45, 50, 55, 60, 65, 70], frame, "target phase margin (deg)", active=4, rows=1, cols=2,
            subplot_titles=("|G|", "phase of G"), height=420,
            layout=lambda f: f.update_xaxes(type="log", title_text="Hz").update_yaxes(range=[-185, -90], row=1, col=2))
show(fig)
""")
b.qa([
    ("Why is C2 needed?",
     "To filter the voltage step $I_pR_1$ (and switching glitches) on $V_{cont}$ that would otherwise modulate the VCO every reference period."),
    ("Where is the third pole?",
     "$\\omega_{p3} = (C_1+C_2)/(R_1C_1C_2) = 1/(R_1C_s)$."),
    ("Derive the maximum PM for a given C1/C2.",
     "PM peaks at $\\sqrt{\\omega_z\\omega_p}$: $\\arctan b - \\arctan(1/b)$ with $b^2 = 1 + C_1/C_2$."),
    ("Typical C1/C2 for 60° PM?",
     "≈ 12.9 ($b = 3.73$)."),
    ("Give the closed-form loop-filter design for given f_c, PM, I_p, K_VCO, N.",
     "$b = \\tan(45°+PM/2)$, $C_{tot} = bI_pK_{VCO}/(2\\pi N\\omega_c^2)$, $C_2 = C_{tot}/b^2$, $C_1 = C_{tot} - C_2$, $R_1 = b/(\\omega_cC_1)$."),
    ("How does C_tot scale with bandwidth?",
     "$\\propto 1/\\omega_c^2$: a 2× wider loop needs 4× less capacitance."),
    ("What is a 4th-order (two extra poles) loop filter for?",
     "An additional RC after the third-order filter for more spur rejection; it costs a few degrees of PM if placed ~5–10× above crossover."),
    ("Why does a large C2 reduce phase margin?",
     "It lowers the third pole toward crossover; the pole's phase lag adds at $\\omega_c$."),
    ("Why place zero and pole symmetrically about crossover?",
     "The phase bump $\\arctan(\\omega/\\omega_z) - \\arctan(\\omega/\\omega_p)$ is maximum at their geometric mean; crossover there gives the maximum PM for that C1/C2."),
    ("What happens to the design if K_VCO is 2× higher than assumed?",
     "Crossover rises ~1.6–2×, no longer at the geometric mean; PM drops by ~5–10° and spurs/peaking increase — design with margin or calibrate the CP current."),
], 36)

# ------------------------------------------------------------------------------------------------ step 37
b.step(37, "Sampled-data reality: Gardner's limit, why f_c ≤ f_REF/10", "plot")
b.md(r"""
### What happens
The PFD/CP acts once per reference period. The continuous-time model assumes a smooth current, which is only true when the loop
changes little per period. As $f_c$ approaches $f_{REF}$, the real loop is less stable than predicted and finally oscillates, even if
the CT phase margin is fine. Gardner (1980) derived the stability boundary of the sampled CP-PLL; the practical result is the
rule **$f_c \lesssim f_{REF}/10$**.

### How (an intuitive model)
Updating once per period is like a zero-order hold, whose phase is a delay of about $T_{REF}/2$:
$$\Delta PM \approx 360°\cdot f_c\cdot\frac{T_{REF}}{2} = 180°\,\frac{f_c}{f_{REF}}.$$
At $f_{REF}/10$ this is 18° (Thijssen et al. quote the same 18° for a sample-and-hold SSPD at $f_{REF}/10$); at $f_{REF}/4$, 45°.

### Why it matters for us
Our SSPLL has an explicit hold (sample, then hold until the next sample), so the delay is real, not just a modelling artefact.
Nagam & Kinget use $\omega_{REF}/20$; the proposal's 2.5 MHz is exactly $f_{REF}/20$ (9° delay penalty).
""")
b.code(r"""
Ip, Kv, N, fref = 100e-6, 2*np.pi*300e6, 32, 50e6
ratios = np.array([1/40, 1/30, 1/20, 1/15, 1/10, 1/8, 1/6, 1/5, 1/4, 1/3.5, 1/3])
over = []
for r in ratios:
    d = sl.loop_design_type2(fref*r, 60, Ip, Kv, N)
    t, e, _ = sl.cp_pll_sim(Ip, d['R'], d['C1'], d['C2'], Kv, N, fref, ncyc=int(30/r), phi_step=0.2)
    over.append(max(-e.min()/0.2, 0))
fig = make_subplots(rows=1, cols=2, subplot_titles=("effective phase margin (CT 60 deg minus hold delay)", "sampled-data simulation: undershoot of the error"))
fig.add_trace(go.Scatter(x=1/ratios, y=60 - 180*ratios, mode="lines+markers", name="60 - 180 f_c/f_REF"), 1, 1)
fig.add_trace(go.Scatter(x=1/ratios, y=np.array(over)*100, mode="lines+markers", name="undershoot (%)"), 1, 2)
fig.update_xaxes(type="log", title_text="f_REF / f_c").update_yaxes(title_text="deg", row=1, col=1).update_yaxes(title_text="%", type="log", row=1, col=2)
show(fig, 420)
""")
b.qa([
    ("Why can't a CP-PLL bandwidth approach f_REF?",
     "The detector updates once per period; the loop sees a delay of ~T/2 and acts on stale information. Beyond ~$f_{REF}/10$ the sampled loop loses margin quickly and becomes unstable (Gardner's limit)."),
    ("Estimate the phase-margin penalty of a half-period delay at f_c = f_REF/10.",
     "$180°\\times0.1 = 18°$."),
    ("Is the continuous-time approximation pessimistic or optimistic?",
     "Optimistic about stability at high $f_c/f_{REF}$: it ignores the sampling delay."),
    ("How do you analyse a CP-PLL exactly?",
     "As a discrete-time system: z-domain model of the PFD/CP charge per cycle and the exact filter/VCO evolution between edges (impulse-invariant), or a cycle-by-cycle simulation like `sl.cp_pll_sim`."),
    ("Why do SSPLLs typically use f_REF/20?",
     "The hold adds a real half-period delay on top of sampling; spur filtering and Nagam's design practice also favour ~$f_{REF}/20$."),
    ("How does a pulser reduce the hold delay of an SSPD?",
     "The charge pump is enabled only during a short pulse right after sampling; the effective delay becomes ~ the pulse position, shorter than T/2 (Thijssen notes this improves stability)."),
    ("What does Gardner's analysis predict for very large loop gain?",
     "Oscillation at ~$f_{REF}/2$: the sampled loop's poles leave the unit circle."),
    ("What is the effect of the divider on the sampling picture?",
     "The comparison rate is $f_{REF}$ regardless of N; N only scales the gain."),
    ("Name two ways to get more bandwidth than f_REF/10 allows.",
     "Raise $f_{REF}$ (higher-frequency crystal or reference doubler), or use both edges / multiple phase detectors per period."),
], 37)

# ------------------------------------------------------------------------------------------------ step 38
b.step(38, "Design procedure with numbers: 50 MHz × 32 = 1.6 GHz, the Type-II baseline", "pick f_c and PM, get R1, C1, C2, I_p, check PDK legality")
b.md(r"""
### Procedure
1. **Bandwidth.** $f_c = f_{REF}/20 = 2.5$ MHz (same as the SSPLL, for a fair comparison; step 8).
2. **Phase margin.** 60° → $b = 3.73$, $C_1/C_2 = 12.9$.
3. **Gains.** $N = 32$; $K_{VCO} = 2\pi\cdot300$ MHz/V (**assumed** fine-tuning gain until Phase 7 measures the ring); $I_p$ free.
4. **Filter** (step 36 closed form). 5. **PDK check** against the cheat sheet: xhigh-poly resistor (≈5.71 kΩ/µm at 0.35 µm width
plus ≈0.59 kΩ heads, from `correlation/corr_rc.sp`), MIM ≈2.03 fF/µm² (30×30 µm max tile), 1.8 V MOS cap ≈7.48 fF/µm² (only above ~0.6 V).

### Why $I_p$ is the main knob
$C_{tot}\propto I_p$ and $R_1\propto 1/I_p$. A large $I_p$ gives big capacitors (area, power) but a small $R_1$ (less thermal noise)
and makes CP noise, leakage and mismatch *relatively* smaller. A small $I_p$ gives a compact filter but a large, noisy $R_1$.
One quantity does **not** change with $I_p$: the ripple step $I_pR_1 = b\,I_p/(\omega_cC_1)$, fixed by $f_c$, PM, $K_{VCO}$ and $N$.
""")
b.code(r"""
Kv, N, fc, pmt = 2*np.pi*300e6, 32, 2.5e6, 60
def frame(Ip_uA):
    d = sl.loop_design_type2(fc, pmt, Ip_uA*1e-6, Kv, N)
    L_r = max((d['R'] - 590)/5714, 0.5)                    # xhigh_po_0p35 length (um), >= 0.5 um
    A_mim = d['C1']/2.03e-15; A_mos = d['C1']/7.48e-15     # um^2
    A_c2 = d['C2']/2.03e-15
    names = ["C1 as MIM", "C1 as MOS cap", "C2 as MIM", "R1 (0.35 um xhigh)"]
    areas = [A_mim, A_mos, A_c2, 0.35*L_r + 2*0.35*2]
    return ([dict(x=names, y=areas, mode="markers+text", text=[f"{a:.0f}" for a in areas], textposition="top center",
                  marker=dict(size=14), name="area (um^2)")],
            f"I_p = {Ip_uA} uA: R1 = {d['R']/1e3:.2f} kOhm (L = {L_r:.1f} um), C1 = {d['C1']*1e12:.2f} pF, C2 = {d['C2']*1e12:.3f} pF, "
            f"I_p R1 = {Ip_uA*1e-6*d['R']*1e3:.0f} mV")
fig = sweep([10, 25, 50, 100, 200, 400], frame, "charge-pump current I_p (uA)", active=3,
            layout=lambda f: f.update_yaxes(type="log", title="area (um^2)", range=[0, 5.3]))
show(fig, 440)
d = sl.loop_design_type2(fc, pmt, 100e-6, Kv, N)
print({k: f"{v:.4g}" for k, v in d.items()})
""")
b.md(r"""
**Result for $I_p$ = 100 µA:** $R_1$ = 18.05 kΩ (xhigh 0.35 × ≈3.1 µm), $C_1$ = 13.16 pF (MIM ≈ 6500 µm² = 8 tiles of 30×30 µm,
or MOS cap ≈ 1760 µm²), $C_2$ = 1.02 pF (MIM ≈ 22×22 µm). All legal. This is the Type-II reference design used in the later steps;
the ngspice phase-domain netlist of Phase 1 uses exactly these values. **R/C corners** (ll/hh, step 7) move $R_1C_1$ by −27…+35%:
check PM at those corners before trusting 60°.
""")
b.qa([
    ("Walk me through a CP-PLL loop-filter design.",
     "Choose $f_c$ (≤ $f_{REF}/10$, here $f_{REF}/20$) and PM (50–60°); from $b = \\tan(45°+PM/2)$ get $C_1/C_2$; from the crossover condition get $C_{tot}$ for a chosen $I_p$; then $C_2$, $C_1$ and $R_1 = b/(\\omega_cC_1)$; check noise, area, spurs and PVT."),
    ("How do you choose I_p?",
     "Trade area ($C\\propto I_p$) against noise and mismatch: larger $I_p$ lowers R1 (less thermal noise) and makes CP noise/leakage relatively smaller, at the cost of capacitor area and CP power."),
    ("Why is I_p·R1 independent of I_p?",
     "$R_1 = b/(\\omega_cC_1)$ and $C_1\\propto I_p$, so $I_pR_1$ depends only on $f_c$, PM, $K_{VCO}$ and N. The ripple step is set by the loop dynamics, not by the CP current."),
    ("How large is 13 pF in SKY130?",
     "≈6500 µm² of MIM (8 tiles of 30×30) or ≈1760 µm² of 1.8 V MOS cap if biased above ~0.6 V."),
    ("Why use a MOS cap for C1 but MIM for C2?",
     "C1 is large and only needs to be roughly linear (it sits at $V_{cont}$, well above threshold); C2 is small and should be linear and low-leakage; MIM fits. MOS caps also leak more."),
    ("What is the resistor length for 18 kΩ in xhigh poly?",
     "≈ (18.05 − 0.59 kΩ heads)/5.71 kΩ/µm ≈ 3.1 µm at 0.35 µm width — legal (L ≥ 0.5 µm)."),
    ("How does K_VCO uncertainty enter the design?",
     "Directly in $C_{tot}$ and $\\omega_c$; designs use the nominal value for sizing and check PM and spurs at $K_{VCO,min/max}$."),
    ("Why did we choose the same f_c for the Type-II baseline as for the SSPLL?",
     "To compare architectures at equal bandwidth: differences in jitter then come from detector noise (N²), not from bandwidth."),
    ("What changes in the design for N = 48 at 49.152 MHz (the old design)?",
     "N enters $C_{tot}\\propto1/N$: 1.5× less capacitance for the same $f_c$ and $I_p$; in-band noise +3.5 dB."),
    ("Which numbers will Phase 7 replace in this design?",
     "$K_{VCO}$ (ring fine-tune gain over PVT), the real $I_p$ and its mismatch, R/C values at corners, parasitic poles."),
], 38)

# ------------------------------------------------------------------------------------------------ step 39
b.step(39, "Limit: PFD, CP and divider noise × N²", "numbers for 50 MHz × 32: +30.1 dB")
b.md(r"""
### What happens
Inside the loop bandwidth, everything that appears at the PFD input (reference, PFD/CP, divider) reaches the output multiplied by
$N$ in phase: **+20 log N = +30.1 dB** for $N = 32$.

### How (normalised figure of merit)
CP-PLL in-band noise is captured by a normalised floor $\mathcal L_{1Hz}$ (Banerjee):
$$\mathcal L_{in\text{-}band} = \mathcal L_{1Hz} + 10\log f_{REF} + 20\log N.$$
For a fixed output frequency $f_0 = Nf_{REF}$, this is $\mathcal L_{1Hz} + 10\log f_0 + 10\log N$: at a fixed $f_0$, a lower reference
(larger N) costs **+10 log N**. With $\mathcal L_{1Hz} = -218$ dBc/Hz: $-218 + 77 + 30.1 = -110.9$ dBc/Hz at 1.6 GHz.

The divider adds its own jitter (each flip-flop's) and power (the first stages run at GHz).

### Why it limits a ring PLL
A ring needs a wide loop (step 23), but a wide loop lets the ×N² floor through. The SSPLL's detector noise is not multiplied by N²
(−130 dBc/Hz output-referred in our budget), which moves the optimum to wider bandwidth.
""")
b.code(r"""
import sys; sys.path.insert(0, "../models")
import pllmodel as pm
Ns = [8, 16, 24, 32, 48, 64]
def frame(Nv):
    fref = 1.6e9/Nv; fc = min(2.5e6, fref/20)
    t2 = pm.TYPE2_TYP.but(N=Nv, fref=fref, fc=fc); ss = pm.TYP.but(N=Nv, fref=fref, fc=fc)
    j2, f, L2 = pm.jitter(t2, "type2"); js, _, Ls = pm.jitter(ss, "sspll")
    floor = -218 + 10*np.log10(fref) + 20*np.log10(Nv)
    return ([dict(x=f, y=L2, name=f"Type-II: {j2['TOTAL']*1e12:.2f} ps"), dict(x=f, y=Ls, name=f"SSPLL: {js['TOTAL']*1e12:.2f} ps")],
            f"N = {Nv}, f_REF = {fref/1e6:.1f} MHz, f_c = {fc/1e6:.2f} MHz: CP-PLL in-band floor {floor:.1f} dBc/Hz (+{20*np.log10(Nv):.1f} dB from N)")
fig = sweep(Ns, frame, "N (f_out fixed at 1.6 GHz)", active=3,
            layout=lambda f: f.update_xaxes(type="log", title="offset (Hz)", range=[3, 8]).update_yaxes(title="dBc/Hz", range=[-150, -80]))
show(fig, 440)
""")
b.qa([
    ("Why is PFD/CP noise multiplied by N²?",
     "It is referred to the PFD input like reference noise; the loop makes $\\phi_{out} = N\\phi_{PD}$ in band; power ×N²."),
    ("What is the normalised in-band phase-noise FoM?",
     "$\\mathcal L_{1Hz} = \\mathcal L_{in-band} - 10\\log f_{REF} - 20\\log N$; good CP-PLLs reach about −220 to −230 dBc/Hz."),
    ("At fixed f_out, how does in-band noise change with f_REF?",
     "$\\mathcal L = \\mathcal L_{1Hz} + 10\\log f_0 + 10\\log N$: halving $f_{REF}$ (doubling N) costs 3 dB."),
    ("Compute the in-band floor for L_1Hz = −218, f_REF = 50 MHz, N = 32.",
     "−218 + 77.0 + 30.1 = −110.9 dBc/Hz."),
    ("Where does divider noise come from?",
     "Thermal noise and supply noise modulating the flip-flop delays; it appears as jitter on the divided edge."),
    ("How does a sub-sampling PD avoid N²?",
     "It compares the VCO directly with the reference (sampling), no divider; its noise is referred to the VCO phase directly (gain A per VCO radian), so it is not multiplied by N. Reference noise is still multiplied by N²."),
    ("Why is reference noise still ×N² in an SSPLL?",
     "The loop still forces $\\phi_{out} = N\\phi_{REF}$: any reference jitter is a time error that equals N times more VCO radians."),
    ("How much power does the divider cost in a CP-PLL?",
     "The first stages switch at $f_{VCO}$; dynamic power $\\sim CV^2f$ per stage; often the second-largest power after the VCO in ring PLLs."),
    ("Is there a jitter-power trade-off in the CP?",
     "Yes: CP current noise $\\propto\\sqrt{I}$ while gain $\\propto I$, so SNR improves with $\\sqrt{I_p}$; more current = lower normalised floor, more power and area."),
], 39)

sys.path.insert(0, os.path.dirname(__file__))
import phase3b
phase3b.build(b)
b.save(os.path.join(os.path.dirname(__file__), "..", "phase3_type2_cppll.ipynb"))
