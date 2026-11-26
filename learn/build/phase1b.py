"""Phase 1 part B: steps 18-24."""


def build(b):
    # -------------------------------------------------------------------------------------------- step 18
    b.step(18, "Order and type", "type = number of integrators (poles at the origin) in G(s)")
    b.md(r"""
### What happens
Two numbers classify every PLL. **Type** = number of poles of the open-loop gain $G(s)$ at the origin
(integrators). **Order** = degree of the closed-loop denominator (number of closed-loop poles).

### How to read them off
| Loop | $G(s)$ | Type | Order |
|---|---|---|---|
| XOR/mixer + RC + VCO | $\frac{K_{PD}K_{VCO}}{N s(1+s/\omega_{LPF})}$ | I | 2 |
| PFD/CP + C1 + VCO | $\frac{I_pK_{VCO}}{2\pi N C_1 s^2}$ | II | 2 (unstable) |
| PFD/CP + R1C1 + VCO | $\frac{I_pK_{VCO}(1+sR_1C_1)}{2\pi N C_1 s^2}$ | II | 2 |
| PFD/CP + R1C1‖C2 + VCO | $\frac{I_pK_{VCO}(1+sR_1C_1)}{2\pi N (C_1+C_2)s^2(1+sR_1C_s)}$ | II | 3 |
| our SSPLL (pulsed $G_m$ + R1C1‖C2 + VCO, plus hold) | same shape, no $N$, extra hold delay | II | 3 (+ delay) |

### Why it matters
**Type sets the steady-state error** (step 20): Type I tracks a phase step with zero error but a frequency step with a
constant phase error; Type II tracks both with zero error. **Order sets the difficulty of stability**: each extra pole
costs phase. Higher type than II is rare in integrated PLLs because three integrators give −270° and are hard to stabilise.
""")
    b.code(r"""
f = np.logspace(3, 9, 400); s = 2j*np.pi*f
G1 = 2*np.pi*2.5e6/s                                    # Type I, crossover 2.5 MHz
wz = 2*np.pi*2.5e6/3.73; wp = 2*np.pi*2.5e6*3.73
G2 = (2*np.pi*2.5e6)**2/3.73*(1+s/wz)/(s**2*(1+s/wp))    # Type II, crossover 2.5 MHz, PM 60
fig = make_subplots(rows=1, cols=2, subplot_titles=("|G| (dB)", "phase of G (deg)"))
for g, n in ((G1, "Type I: -20 dB/dec"), (G2, "Type II: -40 dB/dec, zero, pole")):
    fig.add_trace(go.Scatter(x=f, y=20*np.log10(abs(g)), name=n), 1, 1)
    fig.add_trace(go.Scatter(x=f, y=np.degrees(np.unwrap(np.angle(g))), name=n+" phase", showlegend=False), 1, 2)
fig.update_xaxes(type="log", title_text="frequency (Hz)")
show(fig, 420)
""")
    b.qa([
        ("Define the type and the order of a PLL.",
         "Type: number of open-loop poles at s = 0. Order: number of closed-loop poles (degree of $1+G$'s numerator polynomial)."),
        ("What type is a charge-pump PLL and why?",
         "Type II: the CP into a capacitor and the VCO are both integrators."),
        ("Why are Type-III PLLs rare?",
         "Three integrators give −270°; two zeros are needed to recover phase margin, the loop becomes conditionally stable (unstable if the gain drops, e.g. during saturation) and acquisition is slow."),
        ("What is the low-frequency slope of |G| for Type I and Type II?",
         "−20 dB/decade and −40 dB/decade respectively."),
        ("Is our SSPLL Type I or Type II?",
         "Type II: the pulsed-Gm charge pump drives a capacitor (integrator) and the VCO integrates. Nagam & Kinget and Gao use the same structure."),
        ("Is a second-order Type-II loop always stable?",
         "With a zero (series R) yes for any gain in the CT model (root locus stays in the left half plane); without the zero it is marginally stable. Sampling effects still limit gain (Gardner)."),
        ("What does the third pole add, and is the loop still Type II?",
         "It filters ripple and costs phase; the type is unchanged (still two poles at the origin); the order becomes three."),
        ("Can a PLL have zero steady-state phase error for a frequency ramp?",
         "Only if it is Type III. A Type-II loop tracks a frequency ramp with a constant phase error (step 20)."),
        ("How do you identify type from a step response measurement?",
         "Apply a frequency step to the reference: a residual constant phase error → Type I; zero final error → Type II."),
        ("What is a 'loop order' versus 'filter order'?",
         "Filter order counts the filter's poles (e.g. C1 and C2 → one pole at zero plus one real pole); loop order adds the VCO integrator. A '2nd-order filter' gives a 3rd-order loop."),
    ], 18)

    # -------------------------------------------------------------------------------------------- step 19
    b.step(19, "Stability: Bode, crossover, phase margin, root locus", "why 45–65° is chosen")
    b.md(r"""
### What happens
A feedback loop becomes unstable if, at the frequency where $|G| = 1$, the phase reaches −180°: the fed-back signal
returns inverted twice (Barkhausen) and grows. **Phase margin** measures the distance from that point:
$$PM = 180° + \angle G(j\omega_c),\qquad |G(j\omega_c)| = 1.$$

### How, for the 3rd-order Type-II loop
$$\angle G(j\omega) = -180° + \arctan\frac{\omega}{\omega_z} - \arctan\frac{\omega}{\omega_{p3}}.$$
Placing $\omega_z = \omega_c/b$ and $\omega_{p3} = b\,\omega_c$ (symmetric on a log axis) maximises the phase at $\omega_c$:
$$PM_{max} = \arctan b - \arctan\frac1b,\qquad b^2 = \frac{\omega_{p3}}{\omega_z} = 1+\frac{C_1}{C_2}.$$
So $PM = 60°$ needs $b = \tan(45°+PM/2) = 3.73$, $C_1/C_2 = b^2-1 = 12.9$.

### Why 45–65°
Low PM → closed-loop peaking (noise amplification near $f_c$) and ringing/long settling. High PM → the zero and pole are far
apart: a huge $C_1$ (area) and weak ripple filtering, and for the same $f_c$ a slower step response. 50–60° is the usual
optimum for integrated jitter. The root locus shows the same: as loop gain varies, closed-loop poles move; good PM keeps
the complex pair well damped.
""")
    b.code(r"""
from scipy import signal
fc = 2.5e6; wc = 2*np.pi*fc
f = np.logspace(4, 9, 500); s = 2j*np.pi*f
t = np.linspace(0, 3e-6, 1500)
def frame(pm):
    b_ = np.tan(np.radians(45+pm/2)); wz, wp = wc/b_, wc*b_; K = wc**2/b_
    g = K*(1+s/wz)/(s**2*(1+s/wp))
    sysH = signal.lti([K/wz, K], [1/wp, 1, K/wz, K])        # H/N = G/(1+G)
    _, y = signal.step(sysH, T=t)
    peak = 20*np.log10(np.max(abs(g/(1+g))))
    return ([dict(x=f, y=20*np.log10(abs(g)), name="|G| (dB)", row=1, col=1),
             dict(x=f, y=np.degrees(np.unwrap(np.angle(g))), name="phase G (deg)", row=1, col=2),
             dict(x=f, y=20*np.log10(abs(g/(1+g))), name="|H/N| (dB)", row=1, col=1),
             dict(x=t*1e6, y=y, name="phase-step response", row=2, col=1),
             dict(x=t*1e6, y=np.ones_like(t), name="final value", line=dict(dash="dot"), row=2, col=1)],
            f"PM {pm} deg: C1/C2 = {b_**2-1:.1f}, closed-loop peaking {peak:.2f} dB, overshoot {100*(y.max()-1):.0f} %")
fig = sweep([30, 40, 45, 50, 55, 60, 65, 70, 75], frame, "phase margin (deg)", active=5, rows=2, cols=2,
            subplot_titles=("magnitude", "phase of G", "step response of H/N", ""), height=640,
            layout=lambda f: f.update_xaxes(type="log", row=1, col=1).update_xaxes(type="log", row=1, col=2)
                              .update_yaxes(range=[-40, 60], row=1, col=1).update_yaxes(range=[-200, -90], row=1, col=2)
                              .update_xaxes(title_text="time (us)", row=2, col=1))
show(fig)
""")
    b.md("**Root locus.** Keep the zero and pole of the 60° design fixed and scale the loop gain (e.g. $I_p$ or $K_{VCO}$ "
         "changing over PVT). The closed-loop poles move; the title shows the phase margin you would actually get.")
    b.code(r"""
b_ = np.tan(np.radians(75)); wz, wp = wc/b_, wc*b_; K0 = wc**2/b_
def frame(m):
    K = K0*m
    p = np.roots([1/wp, 1, K/wz, K])
    g = K*(1+s/wz)/(s**2*(1+s/wp)); fcx = sl.crossover(f, 20*np.log10(abs(g)))
    pm = 180 + np.degrees(np.angle(K*(1+2j*np.pi*fcx/wz)/((2j*np.pi*fcx)**2*(1+2j*np.pi*fcx/wp))))
    locus = [np.roots([1/wp, 1, K0*mm/wz, K0*mm]) for mm in np.logspace(-1.5, 1.5, 200)]
    L = np.array(locus)
    return ([dict(x=L.real.flatten()/wc, y=L.imag.flatten()/wc, mode="markers", marker=dict(size=3, color="#cbd5e1"), name="locus"),
             dict(x=p.real/wc, y=p.imag/wc, mode="markers", marker=dict(size=12), name="closed-loop poles"),
             dict(x=[-1/b_], y=[0], mode="markers", marker=dict(symbol="circle-open", size=12), name="zero")],
            f"gain x{m}: crossover {fcx/1e6:.2f} MHz, PM {pm:.0f} deg")
fig = sweep([0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 10.0], frame, "loop-gain multiplier", active=3,
            layout=lambda f: f.update_xaxes(title="Re{s}/w_c", range=[-5, 0.5]).update_yaxes(title="Im{s}/w_c", range=[-3, 3]))
show(fig, 480)
""")
    b.md(r"""
**Try it.** Drop the PM to 30°: 6 dB of peaking and a 52% overshoot. At 60°: 1.7 dB and 19%. At 75°: 0.8 dB but
$C_1/C_2 = 57$ (huge $C_1$). In the root locus, a 4× gain change moves the crossover by ~3× and costs ~15° of margin —
why designs centre PM near 60° when $K_{VCO}$ and the CP gain spread with PVT.
""")
    b.qa([
        ("Define phase margin.",
         "$PM = 180° + \\angle G(j\\omega_c)$ where $|G(j\\omega_c)| = 1$. It is how much additional phase lag would make the loop oscillate."),
        ("Derive the maximum phase margin of a 3rd-order Type-II loop.",
         "$\\angle G = -180° + \\arctan(\\omega/\\omega_z) - \\arctan(\\omega/\\omega_p)$; maximised at $\\omega=\\sqrt{\\omega_z\\omega_p}$; with $b=\\sqrt{\\omega_p/\\omega_z}$, $PM_{max} = \\arctan b - \\arctan(1/b)$."),
        ("Relate $C_1/C_2$ to the pole/zero spacing.",
         "$\\omega_p/\\omega_z = (C_1+C_2)/C_2 = 1 + C_1/C_2 = b^2$."),
        ("What $C_1/C_2$ gives 60° and 45° phase margin?",
         "60°: $b = \\tan 75° = 3.73$, $C_1/C_2 = 12.9$. 45°: $b = \\tan 67.5° = 2.41$, $C_1/C_2 = 4.8$."),
        ("Why not choose 80° phase margin?",
         "It needs $C_1/C_2 \\approx 130$ (enormous $C_1$), gives poor ripple filtering, and slows the transient for the same crossover."),
        ("Relationship between PM and closed-loop peaking?",
         "For the 3rd-order Type-II loop with symmetric zero/pole: 60° → 1.7 dB, 45° → ~3 dB, 30° → ~6 dB (see the slider). Peaking multiplies in-band noise near $f_c$, so lower PM raises integrated jitter."),
        ("What is gain margin and why is it rarely quoted for PLLs?",
         "How much the gain can grow before instability. A Type-II CT loop has no −180° crossing above $\\omega_c$ (phase returns to −180° only asymptotically), so gain margin is infinite in the CT model; the real limit comes from sampling delay (Gardner)."),
        ("What happens to PM if $K_{VCO}$ doubles?",
         "Crossover moves up toward the third pole; PM falls (and $f_c$ rises ~1.6–2×). If $K_{VCO}$ halves, crossover moves toward the zero; PM also falls. Maximum PM only at the design gain."),
        ("What is conditional stability?",
         "A loop stable at the design gain but unstable if the gain *decreases* (phase dips below −180° at lower frequencies). Type-III loops and loops with extra low-frequency poles can be conditionally stable."),
        ("How does the root locus of a Type-II loop with a zero look?",
         "Two poles start at the origin, move into the left half plane on a circle around the zero and return to the real axis; with the third pole, one branch goes to −∞ and the pair can approach the imaginary axis at very high gain."),
        ("What is the relation between ζ and PM for second-order loops?",
         "Approximately $PM \\approx 100\\zeta$ degrees for $\\zeta < 0.7$ (e.g. ζ = 0.5 → ~51°)."),
        ("How does a pure time delay $T_d$ affect PM?",
         "It adds phase $-\\omega_c T_d$ (rad) without changing magnitude: PM loss $= 360° f_c T_d$. A half-period hold ($T_d = T_{REF}/2$) at $f_c = f_{REF}/10$ costs 18°."),
        ("How would you measure phase margin in simulation?",
         "Break the loop in the phase-domain model (or with a behavioural model) and run AC; or fit the closed-loop step response overshoot; in transistor-level sims, extract the block gains and compute G(s)."),
    ], 19)

    # -------------------------------------------------------------------------------------------- step 20
    b.step(20, "Time response and steady-state error", "phase step, frequency step, ramp; final-value theorem per type")
    b.md(r"""
### What happens
Apply three standard inputs to the reference phase: a **phase step** $\Phi_{in}=\Delta\phi/s$, a **frequency step**
$\Phi_{in}=\Delta\omega/s^2$ (phase ramp), and a **frequency ramp** $\Phi_{in}=\dot\omega/s^3$. Watch the phase error.

### How: the final-value theorem
$$\phi_{e}(\infty) = \lim_{s\to0} s\,E(s)\,\Phi_{in}(s),\qquad E = \frac1{1+G}.$$
| Input | Type I ($G\approx K/s$) | Type II ($G\approx K/s^2$) |
|---|---|---|
| phase step $\Delta\phi/s$ | 0 | 0 |
| frequency step $\Delta\omega/s^2$ | $\Delta\omega/K$ | 0 |
| frequency ramp $\dot\omega/s^3$ | ∞ | $\dot\omega/K$ |

### Why
Each integrator in the loop "absorbs" one order of input: to hold a new frequency the VCO needs a new $V_{cont}$. In
Type I that voltage can only come from a **standing phase error** through $K_{PD}$; in Type II the filter capacitor
stores it, so the error can return to zero.
""")
    b.code(r"""
from scipy import signal
wc = 2*np.pi*2.5e6
t = np.linspace(0, 4e-6, 2000)
E1 = signal.lti([1, 0], [1, wc])                                     # Type I: G = wc/s
wz = wc/3.73; K2 = wc**2/3.73*1.0
E2 = signal.lti([1, 0, 0], [1, K2/wz, K2])                           # Type II, 2nd order: G = K(1+s/wz)/s^2
inputs = {"phase step (1 rad)": np.ones_like(t),
          "frequency step (1 Mrad/s)": 1e6*t,
          "frequency ramp (1e12 rad/s^2)": 0.5e12*t**2}
def frame(name):
    u = inputs[name]
    _, e1, _ = signal.lsim(E1, u, t); _, e2, _ = signal.lsim(E2, u, t)
    return ([dict(x=t*1e6, y=u, name="input phase (rad)", line=dict(dash="dot")),
             dict(x=t*1e6, y=e1, name="error, Type I"), dict(x=t*1e6, y=e2, name="error, Type II")],
            f"{name}: final error Type I {e1[-1]:.3g} rad, Type II {e2[-1]:.3g} rad")
fig = sweep(list(inputs), frame, "input", fmt="{}", active=1,
            layout=lambda f: f.update_xaxes(title="time (us)").update_yaxes(title="rad", range=[-0.3, 1.3]))
show(fig, 450)
""")
    b.md(r"""
**Try it.** Frequency step: Type I settles at $\Delta\omega/K = 10^6/(2\pi\cdot2.5\cdot10^6) = 0.064$ rad, Type II returns to 0.
Frequency ramp: Type I grows without bound, Type II settles at $\dot\omega/K = 10^{12}/K_2$.
""")
    b.qa([
        ("State the final-value theorem.",
         "$\\lim_{t\\to\\infty} x(t) = \\lim_{s\\to0} sX(s)$, valid if all poles of $sX(s)$ are in the left half plane."),
        ("Steady-state phase error of a Type-I loop for a frequency step $\\Delta\\omega$?",
         "$\\Delta\\omega/K$ with $K = K_{PD}K_{VCO}/N$ (the DC loop gain constant)."),
        ("Why can a Type-II loop track a frequency step with zero phase error?",
         "The integrating filter holds the new control voltage on its capacitor; no phase error is needed to sustain it."),
        ("Steady-state error of a Type-II loop for a frequency ramp?",
         "Constant: $\\dot\\omega/K$ where $G\\approx K/s^2$ at low frequency ($K = I_pK_{VCO}/(2\\pi N(C_1+C_2))$)."),
        ("Where does a frequency ramp occur in practice?",
         "Temperature drift of the reference, Doppler in receivers, spread-spectrum clocking (triangular frequency modulation)."),
        ("How long does a Type-II PLL take to settle after a phase step?",
         "Roughly $4/(\\zeta\\omega_n)$ for 2% settling; with $f_c = 2.5$ MHz and PM ≈ 60°, of order 0.5–1 µs. Lock time from a large frequency step is dominated by frequency acquisition, not by this."),
        ("Why is the proposal's lock time spec 5 µs typ / 20 µs max, much longer than 1/f_c?",
         "It includes frequency acquisition by the FLL (slewing the VCO across its offset) and hand-over to the SSPD loop, then linear settling to ±10 ps."),
        ("What is cycle slipping in a step response?",
         "If the transient phase error exceeds the PD's linear range (±π for an SSPD, ±2π for a PFD), the error wraps and the loop loses a cycle; the linear step response no longer applies."),
        ("What is the error response to a phase step in Type I first-order loop?",
         "$\\phi_e(t) = \\Delta\\phi\\,e^{-Kt}$: a single exponential with time constant $1/K$."),
        ("Why does overshoot in a Type-II step response happen even with high PM?",
         "The zero in $H(s)$: the closed-loop transfer has a zero at $\\omega_z$ which adds overshoot independent of damping (the step response overshoots even for ζ ≥ 1)."),
    ], 20)

    # -------------------------------------------------------------------------------------------- step 21
    b.step(21, "Acquisition: lock range, pull-in range, capture range, cycle slips", "explanation and simulation")
    b.md(r"""
### What happens
Linear analysis assumes lock. Starting from a frequency difference $\Delta\omega$, a loop with a sinusoidal (mixer-like)
PD may lock quickly, lock after slipping cycles, or never lock.

### How: first-order loop with a sinusoidal PD
$$\frac{d\phi_e}{dt} = \Delta\omega - K\sin\phi_e .$$
- If $|\Delta\omega| \le K$, there is an equilibrium $\sin\phi_e = \Delta\omega/K$: **lock** (hold-in range $= K$).
- If $|\Delta\omega| > K$, $d\phi_e/dt$ never reaches 0: the phase error keeps growing — **cycle slips** — at an average
  beat frequency $\omega_{beat} = \sqrt{\Delta\omega^2-K^2}$.

Definitions (Gardner/Best): **hold-in (lock) range**: static range over which lock can be maintained;
**lock-in (capture) range**: range over which the loop locks without slipping a cycle (≈ loop bandwidth);
**pull-in range**: range over which it eventually locks after slipping cycles (in Type II with a sinusoidal PD the filter
integrator slowly pulls it in); **pull-out**: largest frequency step that does not cause a slip.

### Why a PFD solves it
A PFD's average output keeps the right sign whatever the frequency difference, so a CP-PLL pulls in over the entire VCO
range. An SSPD behaves like a sinusoidal PD with period $T_{VCO}$ (it cannot tell harmonics apart) — the reason our PLL
needs an FLL (Phase 4, step 52).
""")
    b.code(r"""
from scipy.integrate import solve_ivp
K = 2*np.pi*1e6                                  # loop constant K = 2*pi*1 MHz: hold-in range 1 MHz
t = np.linspace(0, 10e-6, 3000)
def frame(r):
    dw = r*K
    sol = solve_ivp(lambda tt, p: [dw - K*np.sin(p[0])], (0, t[-1]), [0.0], t_eval=t, max_step=2e-9)
    pe = sol.y[0]
    ferr = (dw - K*np.sin(pe))/(2*np.pi)
    msg = "locks (phase error settles)" if r <= 1 else f"no lock: beat {np.sqrt(dw**2-K**2)/2/np.pi/1e3:.0f} kHz"
    return ([dict(x=t*1e6, y=pe/(2*np.pi), name="phase error (cycles)", row=1, col=1),
             dict(x=t*1e6, y=ferr/1e3, name="frequency error (kHz)", row=2, col=1)],
            f"dw/K = {r}: {msg}")
fig = sweep([0.3, 0.6, 0.9, 0.99, 1.01, 1.1, 1.5, 2.0], frame, "frequency offset dw / K", active=4, rows=2, cols=1,
            shared_xaxes=True, subplot_titles=("phase error (cycles)", "frequency error (kHz)"), height=560,
            layout=lambda f: f.update_xaxes(title_text="time (us)", row=2, col=1))
show(fig)
""")
    b.md("**Try it.** Just above $\\Delta\\omega/K = 1$ the phase error creeps, then slips a whole cycle quickly, again and again: "
         "the frequency error is a pulse train, its average is the beat frequency. Below 1 it settles at $\\arcsin(\\Delta\\omega/K)$.")
    b.qa([
        ("Define hold-in, pull-in, lock-in (capture) and pull-out ranges.",
         "Hold-in: frequency range over which lock is maintained statically. Lock-in: offset range from which the loop locks within one beat (no cycle slip). Pull-in: range from which it eventually locks, possibly after slips. Pull-out: largest frequency step that does not cause a slip."),
        ("What is the hold-in range of a first-order loop with a sinusoidal PD?",
         "$|\\Delta\\omega| \\le K$ where $K = K_{PD}K_{VCO}$ (the loop constant)."),
        ("What is the beat frequency when the loop is out of lock?",
         "$\\sqrt{\\Delta\\omega^2 - K^2}$ (Adler-like equation)."),
        ("Why does a PFD-based PLL have a pull-in range equal to the VCO range?",
         "The PFD produces a non-zero average with the correct sign for any frequency difference, so the CP keeps pushing the VCO toward the reference."),
        ("Why can a sub-sampling PD lock to the wrong frequency?",
         "It samples at $f_{REF}$ and cannot distinguish $f_{VCO} = Nf_{REF}$ from $(N\\pm1)f_{REF}$: all give a DC sample. An FLL or a PFD-based acquisition loop must first set the right harmonic."),
        ("What is a cycle slip and why is it bad?",
         "The phase error passes ±π (or ±2π) and the loop locks one cycle away. In data links it causes bit errors; in frequency synthesis, momentary frequency error; in our FFNC it means a large transient."),
        ("How does loop bandwidth relate to the lock-in range?",
         "The lock-in (capture) range is of the order of the loop bandwidth: offsets inside it are captured without slipping."),
        ("What is false lock in a mixer PLL?",
         "Locking to a harmonic or sideband (e.g. with square-wave inputs locking at $f_{in}\\cdot m/n$), producing a wrong output frequency with the PD output at its lock value."),
        ("How do you speed up acquisition?",
         "Coarse frequency calibration (digital band selection), a frequency detector (PFD/FLL), temporarily widening the bandwidth (gear shifting), pre-charging $V_{cont}$."),
        ("Why does our design use a dead-zone FLL instead of a plain PFD loop in parallel?",
         "A PFD loop would keep injecting charge-pump noise and mismatch spurs after lock. The dead zone makes it quiet once the phase error is small, leaving the low-noise SSPD loop in control."),
    ], 21)

    # -------------------------------------------------------------------------------------------- step 22
    b.step(22, "Noise basics: L(f), ring-oscillator noise, jitter and σ_t from ∫L(f)", "worked integration")
    b.md(r"""
### What happens
A real oscillator's zero crossings wander. In frequency domain this is **phase noise**: power spread around the carrier.

### How it is defined and measured
For a signal $A\cos(\omega_0t + \phi_n(t))$ with small $\phi_n$:
$$\mathcal L(\Delta f) = \frac{\text{power in 1 Hz at } f_0+\Delta f}{\text{carrier power}}\ \ [\text{dBc/Hz}],\qquad
S_\phi(\Delta f) \approx 2\,\mathcal L(\Delta f)\ [\text{rad}^2/\text{Hz, one-sided}].$$
**Absolute (rms) jitter** over a band:
$$\boxed{\sigma_t = \frac{1}{2\pi f_0}\sqrt{\int_{f_1}^{f_2} 2\cdot10^{\mathcal L(f)/10}\,df}}$$
Other jitter definitions: **period jitter** (variation of one period), **cycle-to-cycle** (difference of adjacent periods).
For a free-running oscillator with white noise sources, timing error grows as a random walk, $\sigma_{\Delta T}=\kappa\sqrt{\Delta T}$, and
$$\mathcal L(\Delta f) = \frac{\sigma_{per}^2 f_0^3}{\Delta f^2}\qquad(\sigma_{per} = \text{period jitter}).$$
Check with our Spectre transient-noise result: $\sigma_{per} = 88$ fs at 1.602 GHz → $\mathcal L(1\,\text{MHz}) = -105$ dBc/Hz
(the thermal part; flicker adds on top).

### Why rings are noisy (Hajimiri & Abidi)
For a ring oscillator with power $P$ (white noise, all stages switching),
$$\mathcal L(\Delta f) \approx \frac{8}{3\eta}\,\frac{kT}{P}\,\frac{V_{DD}}{V_{char}}\,\frac{f_0^2}{\Delta f^2},\qquad \eta\approx 0.75\text{–}1,$$
independent of the number of stages for fixed $P$ and $f_0$: phase noise improves only with power (1/P). This gives a
practical ceiling of the figure of merit $FoM = -\mathcal L + 20\log(f_0/\Delta f) - 10\log(P/1\,\text{mW}) \approx 160$–$165$ dB.
""")
    b.code(r"""
import sys; sys.path.insert(0, "../models")
import pllmodel as pm
j, f, L = pm.jitter(pm.TYP, "ffnc", band=(1e3, 200e6))       # proposal design point, FFNC on
def frame(f1):
    m = (f >= f1) & (f <= 40e6)
    cum = np.sqrt(np.cumsum(2*10**(L[m]/10) * np.gradient(f[m])))/(2*np.pi*pm.TYP.f0)*1e12
    return ([dict(x=f, y=L, name="L(f) (dBc/Hz)", row=1, col=1),
             dict(x=f[m], y=cum, name="cumulative jitter (ps)", row=2, col=1)],
            f"rms jitter from {f1/1e3:.0f} kHz to 40 MHz = {cum[-1]:.2f} ps (spec band 10 kHz-40 MHz)")
fig = sweep([1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6], frame, "lower integration limit (Hz)", fmt="{:.0e}", active=2,
            rows=2, cols=1, shared_xaxes=True, subplot_titles=("phase noise at 1.6 GHz, FFNC on", "jitter accumulated from f1 up to f"),
            height=600, layout=lambda f: f.update_xaxes(type="log").update_xaxes(title_text="offset (Hz)", row=2, col=1))
show(fig)
""")
    b.code(r"""
# Ring-oscillator phase noise vs power for a given FoM (L(1 MHz) at 1.6 GHz), with our three estimates
Pm = np.logspace(-1, 1.5, 100)               # mW
fig = go.Figure()
for fom in (155, 160, 165):
    fig.add_trace(go.Scatter(x=Pm, y=-fom + 20*np.log10(1.6e9/1e6) - 10*np.log10(Pm), name=f"FoM {fom} dB"))
for name, Lv, P in (("ngspice ISF (proposal basis)", -97.35, 4.86), ("Spectre transient noise", -99.0, 4.86),
                    ("Spectre pnoise (optimistic)", -102.1, 4.86)):
    fig.add_trace(go.Scatter(x=[P], y=[Lv], mode="markers", marker=dict(size=11), name=name))
fig.update_xaxes(type="log", title="oscillator power incl. CCO (mW)").update_yaxes(title="L(1 MHz) at 1.6 GHz (dBc/Hz)")
show(fig, 430)
""")
    b.md(r"""
**Try it.** Move the lower limit from 10 kHz to 1 kHz: the jitter barely changes (little noise there), while the
cumulative curve rises steeply between ~0.5 and 5 MHz — the loop-bandwidth hump dominates, which is exactly the
band FFNC attacks. (Our ring estimates sit at FoM ≈ 155–159 dB on total CCO power, below the ~165 dB bound, because the
power counts the 3.3 V CCO mirror.)
""")
    b.qa([
        ("Define L(Δf).",
         "Single-sideband noise power in a 1 Hz bandwidth at offset Δf from the carrier, divided by the carrier power, in dBc/Hz."),
        ("How are $S_\\phi$ and L related?",
         "For small phase deviations $S_\\phi(f) \\approx 2\\mathcal L(f)$ (one-sided $S_\\phi$), since the phase noise splits into two sidebands."),
        ("How do you convert phase noise to rms jitter?",
         "$\\sigma_t = \\sqrt{2\\int 10^{\\mathcal L/10}df}/(2\\pi f_0)$ over the stated band."),
        ("Quick estimate: flat -100 dBc/Hz from 0 to 1 MHz at 1.6 GHz, what jitter?",
         "$\\sigma_\\phi = \\sqrt{2\\cdot10^{-10}\\cdot10^6} = 0.0141$ rad; $\\sigma_t = 0.0141/(2\\pi\\cdot1.6\\times10^9) = 1.4$ ps."),
        ("Why does free-running phase noise fall at 20 dB/decade?",
         "White frequency noise integrates to a random walk of phase; $S_\\phi \\propto S_\\omega/\\omega^2$ → $1/f^2$. Flicker sources give $1/f^3$ near the carrier."),
        ("What is the 1/f³ corner and why is it not equal to the device flicker corner?",
         "The offset where flicker-induced phase noise equals white-induced. Up-conversion depends on the dc value of the ISF (waveform symmetry), so the 1/f³ corner can be well below or above the device 1/f corner."),
        ("State Hajimiri's ring-oscillator phase-noise result and its main conclusion.",
         "$\\mathcal L \\approx \\frac{8}{3\\eta}\\frac{kT}{P}\\frac{V_{DD}}{V_{char}}\\frac{f_0^2}{\\Delta f^2}$; for fixed power and frequency it does not depend on the number of stages; only more power (or less $V_{DD}/V_{char}$) helps."),
        ("Define the oscillator FoM.",
         "$FoM = -\\mathcal L(\\Delta f) + 20\\log(f_0/\\Delta f) - 10\\log(P/1\\,mW)$. Rings ≲ 165 dB, good LC oscillators 185–195 dB."),
        ("Difference between period jitter, cycle-to-cycle jitter and absolute jitter?",
         "Period: rms deviation of each period from the mean. Cycle-to-cycle: rms difference of adjacent periods. Absolute (TIE): rms deviation of edges from ideal positions — what integrated phase noise gives."),
        ("Relate period jitter to phase noise for a free-running oscillator.",
         "$\\mathcal L(\\Delta f) = \\sigma_{per}^2 f_0^3/\\Delta f^2$ (white noise region)."),
        ("Why does the absolute jitter of a free-running oscillator diverge?",
         "Timing error accumulates as a random walk ($\\sigma\\propto\\sqrt{t}$); a PLL bounds it by correcting the phase at every reference edge."),
        ("Why do Spectre pnoise and transient noise disagree for our ring?",
         "Sideband convention of the converted pnoise output (factor 2, 3 dB) — found in step 7; device noise itself matched to 0.0 dB."),
        ("What is AM-to-PM conversion?",
         "Amplitude noise converted to phase noise by nonlinear capacitances/thresholds; in ring oscillators the output is rail-to-rail, so phase noise dominates."),
        ("How does supply noise create phase noise in a ring?",
         "$K_{VDD} = \\partial f/\\partial V_{DD}$ turns supply noise into frequency noise: $S_\\phi = K_{VDD}^2S_v/f^2$. Rings have large $K_{VDD}$ — why ours is current-fed and FFNC also cancels supply noise."),
        ("Which band contributes most to our PLL's jitter?",
         "Around the loop bandwidth (≈0.5–5 MHz), where ring noise is no longer suppressed by the loop and still high — Nagam reports ~75% of jitter in 25 kHz–5 MHz for his design."),
    ], 22)

    # -------------------------------------------------------------------------------------------- step 23
    b.step(23, "Noise transfer: in-loop sources low-pass and ×N², VCO high-pass; optimum bandwidth", "noise-shaping plots")
    b.md(r"""
### What happens
Every noise source in the loop reaches the output, but through different transfer functions.

### How
With $G$ the loop gain:
$$\Phi_{out} = \underbrace{N\frac{G}{1+G}}_{\text{low-pass, gain }N}(\Phi_{REF}+\Phi_{PD}+\Phi_{div}) + \underbrace{\frac{1}{1+G}}_{\text{high-pass}}\Phi_{VCO}.$$
Reference, PD/CP and divider noise (referred to the PD input) are multiplied by $N$ in amplitude (**+20 log N dB**, +30.1 dB
for $N=32$) inside the bandwidth. The VCO's own noise is suppressed inside the bandwidth and passes outside.

### Why there is an optimum bandwidth
Widening $f_c$ removes more VCO noise but lets more (×N²) in-band noise through. The total is roughly minimised where the
**in-band floor meets the free-running VCO curve**. A ring VCO is very noisy, so it wants a wide loop; a CP-PLL's ×N²
floor stops it — which motivates the SSPLL (Phase 4).
""")
    b.code(r"""
import sys; sys.path.insert(0, "../models")
import pllmodel as pm
def frame(fc_MHz):
    d = pm.TYPE2_TYP.but(fc=fc_MHz*1e6)
    j, f, L = pm.jitter(d, "type2", band=(10e3, 40e6))
    _, S = pm.spectra(d, "type2", f)
    tr = [dict(x=f, y=10*np.log10(v/2), name=f"{k}: {j[k]*1e12:.2f} ps") for k, v in S.items()]
    tr.append(dict(x=f, y=pm.vco_L(f, d['vco1M'], d['fc3']), name="free-running VCO", line=dict(dash="dot")))
    tr.append(dict(x=f, y=L, name="total", line=dict(width=3, color="black")))
    return tr, f"Type-II CP-PLL, f_c = {fc_MHz} MHz: total jitter {j['TOTAL']*1e12:.2f} ps (10 kHz-40 MHz)"
fig = sweep([0.3, 0.5, 1.0, 1.5, 2.0, 2.5, 3.5, 5.0], frame, "loop bandwidth (MHz)", active=5,
            layout=lambda f: f.update_xaxes(type="log", title="offset (Hz)", range=[3, 8]).update_yaxes(title="dBc/Hz", range=[-150, -60]))
show(fig, 500)
""")
    b.md("**Try it.** At 0.3 MHz the ring dominates (12 ps); 2.5 MHz gives 2.5 ps and 5 MHz 2.1 ps — but 5 MHz is "
         "$f_{REF}/10$, the stability limit, and the ×N² PD/CP floor (≈ −111 dBc/Hz) now dominates in-band. Phases 3 and 4 explain "
         "why the SSPLL lowers that floor to −130 dBc/Hz.")
    b.qa([
        ("Write the output phase noise of a PLL in terms of its sources.",
         "$S_{out} = |NG/(1+G)|^2(S_{ref}+S_{PD}+S_{div}) + |1/(1+G)|^2 S_{VCO}$ (all referred to their natural points)."),
        ("Why is in-band reference noise multiplied by N²?",
         "Phase is multiplied by N (the loop forces $\\phi_{out} = N\\phi_{ref}$); power scales as $N^2$, i.e. +20log N dB."),
        ("What is the normalised PD/CP noise floor (FoM_1Hz)?",
         "$\\mathcal L_{1Hz}$: in-band noise normalised as $\\mathcal L_{in-band} - 10\\log f_{REF} - 20\\log N$. Good CP-PLLs reach −220 to −230 dBc/Hz; we assumed −218 typ for SKY130."),
        ("Where is the optimum loop bandwidth?",
         "Near the offset where the in-band floor (×N²) intersects the free-running VCO noise, adjusted for peaking; then neither source dominates around $f_c$."),
        ("Why does a ring-VCO PLL want a wide bandwidth?",
         "Ring phase noise is high; the loop suppresses it only below $f_c$, so a wider loop removes more of it."),
        ("Name two things that limit how wide you can make the bandwidth.",
         "Stability of the sampled loop (≈ $f_{REF}/10$ for a CP-PLL, less with hold delay) and reference spurs/in-band noise passing through."),
        ("How does peaking change integrated jitter?",
         "Peaking amplifies in-band noise near $f_c$ and VCO noise just above it, adding a hump to the spectrum and to the integral."),
        ("What noise sources are 'VCO-like' (high-passed)?",
         "Any noise injected at the VCO input or output: VCO intrinsic noise, filter resistor noise (via $K_{VCO}$), supply noise on the VCO."),
        ("If the reference floor is −152 dBc/Hz at 50 MHz, what is its in-band contribution at 1.6 GHz?",
         "−152 + 20log32 = −121.9 dBc/Hz."),
        ("Why does the proposal still have 2.3 ps jitter without FFNC even with an SSPLL?",
         "The ring noise outside (and just inside) the 2.5 MHz bandwidth still dominates; lowering the in-band floor helps only up to the loop bandwidth limit."),
    ], 23)

    # -------------------------------------------------------------------------------------------- step 24
    b.step(24, "Lab: behavioural PLL in Python and ngspice; check H(s) and lock", "notebook and testbench")
    b.md(r"""
### What you do
1. **Sampled-data simulation.** `sl.cp_pll_sim` simulates a PFD/charge-pump PLL one reference period at a time, with the
   filter and VCO integrated *exactly* between edges (matrix exponential). Compare its phase-step error with the linear
   CT prediction $E(s)=1/(1+G)$ while the bandwidth grows toward $f_{REF}$.
2. **ngspice phase-domain model.** `learn/spice/pll_phase_domain.cir` (controlled sources + real R/C) — run it and
   compare $H(s)$ with Python (already done in step 17: agreement to $10^{-4}$ dB).
3. **Your own Verilog-A PLL.** If you have an ideal Verilog-A PLL, run it with the same $I_p$, $R_1$, $C_1$, $C_2$, $K_{VCO}$, $N$ and
   compare its lock transient with the sampled-data curve below.
""")
    b.code(r"""
from scipy import signal
Ip, Kv, N, fref = 100e-6, 2*np.pi*300e6, 32, 50e6
def frame(ratio):
    fc = fref*ratio
    d = sl.loop_design_type2(fc, 60, Ip, Kv, N)
    t, err, vc = sl.cp_pll_sim(Ip, d['R'], d['C1'], d['C2'], Kv, N, fref, ncyc=int(12/ratio), phi_step=0.5)
    Ct, Cs = d['C1']+d['C2'], d['C1']*d['C2']/(d['C1']+d['C2'])
    k = Ip*Kv/(2*np.pi*N*Ct)
    den = np.polyadd([d['R']*Cs, 1, 0, 0], [k*d['R']*d['C1'], k])
    _, e = signal.step(signal.lti([d['R']*Cs, 1, 0, 0], den), T=t)
    return ([dict(x=t*1e6, y=err/0.5, name="sampled-data sim (PFD/CP, exact)", mode="lines+markers", marker=dict(size=3)),
             dict(x=t*1e6, y=e, name="linear CT model E(s)", line=dict(dash="dash"))],
            f"f_c = f_REF/{1/ratio:.0f} = {fc/1e6:.2f} MHz: R1 = {d['R']/1e3:.1f} k, C1 = {d['C1']*1e12:.2f} p, C2 = {d['C2']*1e12:.3f} p")
fig = sweep([1/40, 1/20, 1/10, 1/6, 1/4, 1/3], frame, "f_c / f_REF", fmt="{:.3f}", active=1,
            layout=lambda f: f.update_xaxes(title="time (us)").update_yaxes(title="phase error / step", range=[-1.5, 1.5]))
show(fig, 460)
""")
    b.md(r"""
**Try it.** At $f_c = f_{REF}/20$ (our 2.5 MHz) the sampled loop and the CT model overlap. At $f_{REF}/10$ the sampled loop
rings slightly more than predicted; at $f_{REF}/4$ the error swings past −100% of the step; at $f_{REF}/3$ the loop is
unstable (the error grows and clips at the PFD range). The CT model, which ignores that the PFD acts only once per period,
is blind to all of this (**Gardner's limit**, Phase 3 step 37).

**Run the ngspice model yourself:**
```
cd learn/spice && ngspice -b pll_phase_domain.cir      # writes learn/data/pll_phase_domain.csv
```
**Exercise.** Change $I_p$ to 50 µA in both the netlist and the Python cell without re-designing the filter: predict the new
crossover (≈ ×0.6) and PM before running.
""")
    b.qa([
        ("Why simulate a PLL in the phase domain instead of transistor level?",
         "Speed: a 1.6 GHz VCO needs ps time steps for µs of lock (millions of points). Phase-domain models run in milliseconds and expose $H(s)$, stability and noise directly; transistor sims then verify the block gains."),
        ("What does a sampled-data (discrete-time) PLL model capture that the CT model misses?",
         "That the PFD/CP updates only once per reference period: the effective delay, the staircase control voltage and the resulting instability as $f_c$ approaches $f_{REF}$."),
        ("How do you build a PLL phase-domain model in SPICE?",
         "Nodes are phases: VCCS $I_p/2\\pi\\cdot(\\phi_{in}-\\phi_{div})$ into the real filter; VCO as VCCS $K_{VCO}V_{cont}$ into 1 F; divider as VCVS 1/N; AC analysis gives H(s)."),
        ("How do you verify a PLL behavioural model?",
         "Check DC gain of H = N, crossover and PM against hand calculation, step-response overshoot, and lock from a frequency offset; compare two independent implementations (Python vs SPICE)."),
        ("What is the role of Verilog-A in PLL design?",
         "Behavioural models of blocks (VCO, PFD, CP, divider) that run in Spectre/ngspice (via OpenVAF/OSDI) with transistor-level blocks swapped in one at a time — a mixed-level verification strategy."),
        ("How long does our PLL take to settle after a small phase step?",
         "With $f_c$ = 2.5 MHz, PM 60°: about 0.5 µs to a few percent, as in the plot."),
        ("Why does the sampled loop diverge from the CT model as $f_c$ approaches $f_{REF}$?",
         "The loop acts on information that is up to one period old; equivalent to a delay of ~T/2 plus zero-order hold, which costs phase $\\approx 180°\\,f_c/f_{REF}$ and eventually makes the loop unstable."),
        ("What is a good bandwidth ratio for a CP-PLL and for an SSPLL?",
         "CP-PLL up to ~$f_{REF}/10$; SSPLL ~$f_{REF}/20$ because of the additional hold delay and spur considerations (Nagam uses $\\omega_{REF}/20$)."),
        ("What is the exact-discretisation method used in the simulator?",
         "Between edges the system is LTI with a constant input; the state update is $x_{k+1} = e^{A\\Delta t}x_k + \\int e^{A\\tau}B\\,d\\tau\\cdot u$, computed with an augmented matrix exponential."),
        ("Which parameters of the behavioural model must later come from transistor simulation?",
         "$K_{VCO}$ and its spread, charge-pump/Gm gain and pulse width, sampler gain (ring amplitude), filter R/C values over corners, and noise of each block."),
    ], 24)
