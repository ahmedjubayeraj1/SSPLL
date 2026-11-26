"""Phase 2 - Type-I PLL, its limits and their fixes (roadmap steps 25-32)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nb import Book

b = Book("Phase 2 — Type-I PLL: operation, limits and fixes (steps 25–32)",
         "A Type-I loop has one integrator (the VCO), so it must keep a **phase error** to hold the control voltage. "
         "That single fact explains almost all of its limits: static phase error, a coupling between bandwidth, damping "
         "and ripple, spurs, and a narrow capture range. Each fix in this phase leads toward the charge-pump PLL "
         "(Phase 3) or the sample-and-hold detector at the heart of our sub-sampling PLL (Phase 4).")

# ------------------------------------------------------------------------------------------------ step 25
b.step(25, "The Type-I loop and its transfer function", "mixer or XOR + first-order RC + VCO: derive H(s), ω_n, ζ")
b.md(r"""
### What happens
The simplest PLL: a multiplying phase detector (mixer or XOR), a first-order RC low-pass filter and a VCO.

### How (Razavi, *RF Microelectronics* §9.2)
With $K_{PD}$ (V/rad), $F(s) = \frac{1}{1+s/\omega_{LPF}}$ and $K_{VCO}/s$ (take $N=1$ for clarity; with a divider replace
$K_{VCO}$ by $K_{VCO}/N$ and multiply $H$ by $N$):
$$G(s) = \frac{K_{PD}K_{VCO}}{s\,(1+s/\omega_{LPF})},\qquad
H(s) = \frac{G}{1+G} = \frac{K_{PD}K_{VCO}}{\dfrac{s^2}{\omega_{LPF}} + s + K_{PD}K_{VCO}}.$$
Comparing with the standard second-order form $\dfrac{\omega_n^2}{s^2+2\zeta\omega_n s+\omega_n^2}$:
$$\boxed{\omega_n = \sqrt{\omega_{LPF}\,K_{PD}K_{VCO}},\qquad \zeta = \frac12\sqrt{\frac{\omega_{LPF}}{K_{PD}K_{VCO}}}}$$
The closed-loop poles are $\omega_{p1,2} = -\zeta\omega_n \pm \omega_n\sqrt{\zeta^2-1}$; the decay time constant is
$1/(\zeta\omega_n) = 2/\omega_{LPF}$ — set by the filter alone.

### Why it matters
Only **two** knobs ($K = K_{PD}K_{VCO}$ and $\omega_{LPF}$) set three things: bandwidth, damping and ripple rejection. That is the
coupling problem of step 27.
""")
b.code(r"""
from scipy import signal
wl = 2*np.pi*5e6                                          # omega_LPF = 2*pi*5 MHz
t = np.linspace(0, 3e-6, 1200); f = np.logspace(4, 9, 400)
def frame(r):                                             # r = K / omega_LPF
    K = r*wl
    wn, z = np.sqrt(wl*K), 0.5*np.sqrt(wl/K)
    H = signal.lti([K], [1/wl, 1, K])
    _, y = signal.step(H, T=t)
    _, mag, _ = signal.bode(H, w=2*np.pi*f)
    return ([dict(x=t*1e6, y=y, name="phase-step response", row=1, col=1),
             dict(x=f, y=mag, name="|H| (dB)", row=1, col=2)],
            f"K/w_LPF = {r}: w_n = 2pi x {wn/2/np.pi/1e6:.2f} MHz, zeta = {z:.2f}, decay time 2/w_LPF = {2/wl*1e9:.0f} ns")
fig = sweep([0.1, 0.25, 0.5, 1, 2, 4, 10], frame, "K / w_LPF", active=1, rows=1, cols=2,
            subplot_titles=("step response", "closed-loop magnitude"), height=420,
            layout=lambda f: f.update_xaxes(title_text="time (us)", row=1, col=1)
                              .update_xaxes(type="log", title_text="Hz", row=1, col=2).update_yaxes(range=[-40, 15], row=1, col=2))
show(fig)
""")
b.md("**Try it.** $K/\\omega_{LPF} = 0.25$ gives ζ = 1 (critically damped). Raising $K$ to get a faster/wider loop drops ζ: at "
     "$K/\\omega_{LPF} = 10$, ζ = 0.16 and the step response rings for microseconds even though $\\omega_n$ grew.")
b.qa([
    ("Derive H(s) of a Type-I PLL with an RC filter.",
     "$G = K_{PD}K_{VCO}/[s(1+s/\\omega_{LPF})]$; $H = G/(1+G) = K_{PD}K_{VCO}/(s^2/\\omega_{LPF} + s + K_{PD}K_{VCO})$."),
    ("Give ω_n and ζ of the Type-I loop.",
     "$\\omega_n = \\sqrt{\\omega_{LPF}K_{PD}K_{VCO}}$, $\\zeta = \\frac12\\sqrt{\\omega_{LPF}/(K_{PD}K_{VCO})}$."),
    ("What sets the settling time constant of a Type-I loop?",
     "$1/(\\zeta\\omega_n) = 2/\\omega_{LPF}$, independent of $K$: only the filter corner speeds it up."),
    ("What is the type and the order of this loop?",
     "Type I (one integrator, the VCO), second order (VCO pole plus the RC pole)."),
    ("Why is a mixer PD modelled as a constant $K_{PD}$?",
     "Near the lock point (90°) the average output $\\frac{A_1A_2}{2}\\cos\\Delta\\phi$ is linear in the deviation; $K_{PD} = A_1A_2/2$. The $2\\omega$ term is treated as a disturbance (ripple)."),
    ("How does a divider change the Type-I equations?",
     "$K_{VCO}$ becomes $K_{VCO}/N$ in $G$, so $\\omega_n$ falls by $\\sqrt N$, ζ rises by $\\sqrt N$, and $H$'s low-frequency value is N."),
    ("What is the root locus of the Type-I second-order loop?",
     "Two open-loop poles at 0 and $-\\omega_{LPF}$; as $K$ grows they meet at $-\\omega_{LPF}/2$ and split vertically: the real part stays at $-\\omega_{LPF}/2$, so damping falls as $K$ rises."),
    ("Why does an XOR Type-I loop lock at 90°?",
     "Its triangular characteristic is centred at $\\pi/2$ (average $V_{DD}/2$), the point of maximum symmetric range; the control voltage needed to hold the VCO frequency shifts it away from 90° (static error)."),
    ("What is the −3 dB bandwidth of this loop for ζ = 0.707?",
     "Equal to $\\omega_n$ for ζ = 0.707 (Butterworth)."),
    ("Is the Type-I loop stable for any K?",
     "Yes in the CT model (two poles, phase never reaches −180°), but damping goes to zero as K → ∞; real loops with extra delay become unstable."),
    ("Where is a Type-I PLL still used today?",
     "Clock-multiplying DLLs are Type-I by nature; sampling-PD loops (sample-and-hold) with low ripple; some CDRs; and as an educational stepping stone."),
], 25)

# ------------------------------------------------------------------------------------------------ step 26
b.step(26, "Limit: static phase error", "Δφ = Δω/K_loop, and why one integrator forces it")
b.md(r"""
### What happens
If the input frequency differs from the VCO free-running frequency by $\Delta\omega = \omega_{in}-\omega_0$, a locked Type-I loop
sits at a **constant phase error**.

### How
In lock, $\omega_{out} = \omega_{in}$, so the VCO needs $V_{cont} = \Delta\omega/K_{VCO}$. In a Type-I loop the only source of that DC
voltage is the PD: $V_{cont} = K_{PD}\,\Delta\phi$ (the RC filter has unity DC gain). Hence
$$\boxed{\Delta\phi_{ss} = \frac{\Delta\omega}{K_{PD}K_{VCO}}}$$
(final-value theorem gives the same: $\lim_{s\to0}s\cdot\frac{1}{1+G}\cdot\frac{\Delta\omega}{s^2} = \Delta\omega/K$).

### Why it is a problem
(1) The output edges are skewed from the input by $\Delta\phi$ — bad for clock alignment and de-skew. (2) $\Delta\phi$ eats the PD's
linear range: when $\Delta\phi$ reaches the edge of the characteristic (±π/2 around 90° for XOR), lock is lost. (3) The phase
error varies with PVT because $\omega_0$ and $K_{VCO}$ do. Larger $K$ reduces it but lowers ζ (step 27).
""")
b.code(r"""
Vdd = 1.8; Kpd = Vdd/np.pi                                   # XOR
df = np.linspace(-200e6, 200e6, 401)                         # frequency offset (Hz)
def frame(Kv_MHz):
    Kv = 2*np.pi*Kv_MHz*1e6
    dphi = 2*np.pi*df/(Kpd*Kv)                                # rad
    dphi_c = np.where(abs(dphi) <= np.pi/2, dphi, np.nan)    # XOR range: 0..pi around pi/2
    hold = Kpd*Kv*np.pi/2/(2*np.pi)
    return ([dict(x=df/1e6, y=np.degrees(dphi_c), name="static phase error (deg)"),
             dict(x=[-hold/1e6, hold/1e6], y=[-90, 90], mode="markers", marker=dict(size=10), name="lock lost (edge of XOR range)")],
            f"XOR (K_PD = V_DD/pi = {Kpd:.2f} V/rad), K_VCO = {Kv_MHz} MHz/V: hold-in range +/-{hold/1e6:.0f} MHz, "
            f"{360*1e6/(Kpd*Kv_MHz*1e6):.2f} deg per MHz of offset")
fig = sweep([50, 100, 200, 300, 500, 1000], frame, "K_VCO (MHz/V)", active=3,
            layout=lambda f: f.update_xaxes(title="input minus free-running frequency (MHz)").update_yaxes(title="deg", range=[-100, 100]))
show(fig, 430)
""")
b.qa([
    ("Why does a Type-I PLL have a static phase error?",
     "To hold the VCO at a frequency different from its free-running value it needs a DC control voltage, and the only source of DC is the PD output, which requires a non-zero phase difference."),
    ("Derive the static phase error.",
     "$V_{cont} = \\Delta\\omega/K_{VCO}$ and $V_{cont} = K_{PD}\\Delta\\phi$ → $\\Delta\\phi = \\Delta\\omega/(K_{PD}K_{VCO})$."),
    ("How can you reduce the static error without changing the loop?",
     "Centre the VCO free-running frequency at the input (calibration/coarse tuning), so $\\Delta\\omega \\approx 0$."),
    ("What is the hold-in range of an XOR Type-I loop?",
     "The PD output can supply $\\pm K_{PD}\\pi/2$ around its centre, so $|\\Delta\\omega| \\le K_{PD}K_{VCO}\\pi/2$."),
    ("Why does the error change over temperature?",
     "Free-running VCO frequency and $K_{VCO}$ drift; $\\Delta\\omega$ and $K$ change, and so does $\\Delta\\phi$."),
    ("Does a Type-II loop have static phase error?",
     "Ideally zero; practically a small offset from charge-pump mismatch, leakage and PFD delays (Phase 3, step 40)."),
    ("Why is static phase error a problem in clock de-skew?",
     "The purpose is to align output edges to input edges; any static error is a fixed skew that varies with PVT."),
    ("What is the final-value-theorem proof of the static error?",
     "$\\phi_e(\\infty) = \\lim_{s\\to0} s\\frac{1}{1+K/s}\\frac{\\Delta\\omega}{s^2} = \\Delta\\omega/K$."),
    ("Can you increase K arbitrarily to remove the error?",
     "No: ζ ∝ $1/\\sqrt K$, so the loop becomes underdamped; ripple also passes more strongly to the VCO."),
    ("A mixer PD with $A_1A_2/2 = 0.2$ V and $K_{VCO} = 2\\pi\\cdot100$ MHz/V; 5 MHz offset. Static error?",
     "$K = 0.2\\cdot2\\pi\\cdot10^8 = 1.26\\times10^8$ s⁻¹; $\\Delta\\phi = 2\\pi\\cdot5\\times10^6/1.26\\times10^8 = 0.25$ rad ≈ 14°."),
], 26)

# ------------------------------------------------------------------------------------------------ step 27
b.step(27, "Limit: bandwidth, damping and ripple are coupled", "raising K lowers ζ; narrowing the filter lowers ζ")
b.md(r"""
### What happens
You want (a) a wide bandwidth (fast, suppresses VCO noise), (b) ζ ≈ 0.7 (no ringing), (c) strong ripple rejection at $2\omega_{REF}$
(low spurs), and (d) a small static error. A Type-I loop cannot have all four.

### How
$$\omega_n = \sqrt{\omega_{LPF}K},\qquad \zeta = \tfrac12\sqrt{\omega_{LPF}/K},\qquad
\Big|F(j2\omega_{REF})\Big| \approx \frac{\omega_{LPF}}{2\omega_{REF}},\qquad \Delta\phi_{ss} = \frac{\Delta\omega}{K}.$$
- More ripple rejection → smaller $\omega_{LPF}$ → ζ falls.
- Smaller static error → larger $K$ → ζ falls.
- Fixing ζ = 0.707 forces $K = \omega_{LPF}/2$, so $\omega_n = \omega_{LPF}/\sqrt2$: **the bandwidth is tied to the ripple filter**.

### Why
With one integrator, the filter pole is both the ripple filter and the only element that shapes the dynamics. A second,
independent time constant (a zero, step 29) or a second integrator (step 31) is needed to decouple them.
""")
b.code(r"""
fref = 50e6; Ks = np.logspace(5, 10, 300)
def frame(fl_MHz):
    wl = 2*np.pi*fl_MHz*1e6
    z = 0.5*np.sqrt(wl/Ks); wn = np.sqrt(wl*Ks)
    rip = 20*np.log10(wl/(2*2*np.pi*fref))
    return ([dict(x=Ks, y=z, name="zeta", row=1, col=1),
             dict(x=Ks, y=0.707*np.ones_like(Ks), name="zeta = 0.707", line=dict(dash="dot"), row=1, col=1),
             dict(x=Ks, y=wn/2/np.pi/1e6, name="f_n (MHz)", row=1, col=2)],
            f"f_LPF = {fl_MHz} MHz: ripple at 2 f_REF attenuated by {-rip:.0f} dB; zeta = 0.707 only at K = {wl/2:.2e} 1/s "
            f"-> f_n = {wl/np.sqrt(2)/2/np.pi/1e6:.2f} MHz")
fig = sweep([0.2, 0.5, 1, 2, 5, 10], frame, "filter corner f_LPF (MHz)", active=3, rows=1, cols=2,
            subplot_titles=("damping vs loop gain K", "natural frequency vs K"), height=420,
            layout=lambda f: f.update_xaxes(type="log", title_text="K = K_PD K_VCO (1/s)").update_yaxes(type="log", row=1, col=1)
                              .update_yaxes(type="log", row=1, col=2))
show(fig)
""")
b.qa([
    ("Why are bandwidth and ripple rejection coupled in a Type-I loop?",
     "The RC pole both filters the ripple and sets the dynamics; for acceptable ζ, $\\omega_n \\approx \\omega_{LPF}/\\sqrt2$, so a lower corner (better ripple filtering) means a narrower loop."),
    ("What happens to ζ when you increase K to reduce static error?",
     "It falls as $1/\\sqrt K$; the loop rings."),
    ("Estimate ripple attenuation of an RC filter at $2f_{REF}$.",
     "$|F| \\approx \\omega_{LPF}/(2\\omega_{REF})$ for $2\\omega_{REF}\\gg\\omega_{LPF}$, i.e. −20 dB/decade."),
    ("For ζ = 0.707 what is K in terms of $\\omega_{LPF}$?",
     "$K = \\omega_{LPF}/2$."),
    ("Give two ways to break the coupling.",
     "Add a zero (lead-lag filter: ζ set by the zero, step 29) or add an integrator (Type II, step 31)."),
    ("Why not use a higher-order low-pass filter for more ripple rejection?",
     "Each extra pole adds phase lag near crossover; stability degrades and ζ falls further."),
    ("How does ripple appear in the output spectrum?",
     "As FM sidebands at ±2f_REF (XOR/mixer) with level $20\\log(K_{VCO}A_m/(2\\cdot2\\omega_{REF}))$ dBc for small modulation (step 28)."),
    ("Why is a Type-I loop still attractive in some DLLs?",
     "A DLL's delay line is not an integrator, so its loop is first order and unconditionally stable; there the Type-I limitations are milder."),
    ("Is the coupling also present in a Type-II CP-PLL?",
     "Weaker: R1 sets the zero and C2 the ripple pole independently, and the integrator removes the static error; but bandwidth vs spur (C2) and phase margin trade-offs remain."),
    ("Which limit hurts a ring-oscillator PLL most?",
     "Bandwidth: a ring needs a wide loop to suppress its noise, but the Type-I ripple constraint keeps the loop narrow."),
], 27)

# ------------------------------------------------------------------------------------------------ step 28
b.step(28, "Limit: ripple → spurs; narrow capture; duty-cycle sensitivity; harmonic false lock", "spectra")
b.md(r"""
### What happens
At lock an XOR outputs a 50% square wave at $2f_{REF}$ between 0 and $V_{DD}$. The RC filter reduces but does not remove it,
so $V_{cont}$ carries a ripple that **frequency-modulates** the VCO, creating **spurs** at $f_{out}\pm 2f_{REF}$.

### How
The fundamental of a 0…$V_{DD}$ square wave has amplitude $\frac{2}{\pi}V_{DD}$. After the filter,
$A_m \approx \frac{2V_{DD}}{\pi}\cdot\frac{\omega_{LPF}}{2\omega_{REF}}$. A sinusoidal control ripple $A_m\cos\omega_mt$ gives a
phase deviation $\beta = K_{VCO}A_m/\omega_m$ and, for $\beta\ll1$, two sidebands of relative amplitude $\beta/2$:
$$\text{spur (dBc)} = 20\log_{10}\frac{K_{VCO}A_m}{2\omega_m},\qquad \omega_m = 2\omega_{REF}.$$
**Other Type-I limits:** narrow capture range (≈ the loop bandwidth, step 21); XOR gain and range depend on input duty cycle
(step 13 figure); with square-wave inputs a mixer/XOR can lock to harmonics or sub-harmonics (**false lock**), because
harmonics of both inputs also mix to DC.
""")
b.code(r"""
Vdd, fref = 1.8, 50e6; wm = 2*2*np.pi*fref
fl = np.logspace(5, 8, 300)
def frame(Kv_MHz):
    Kv = 2*np.pi*Kv_MHz*1e6
    Am = 2*Vdd/np.pi * (2*np.pi*fl)/np.sqrt(wm**2 + (2*np.pi*fl)**2)
    beta = Kv*Am/wm
    spur = 20*np.log10(beta/2)
    i = np.argmin(abs(fl-1e6))
    return ([dict(x=fl, y=spur, name="spur at f_out +/- 2 f_REF (dBc)")],
            f"K_VCO = {Kv_MHz} MHz/V: with f_LPF = 1 MHz the spur is {spur[i]:.0f} dBc (proposal spec: below -45 dBc)")
fig = sweep([30, 100, 300, 1000], frame, "K_VCO (MHz/V)", active=2,
            layout=lambda f: f.update_xaxes(type="log", title="filter corner f_LPF (Hz)").update_yaxes(title="dBc", range=[-90, 10]))
show(fig, 420)
""")
b.qa([
    ("Why does an XOR PLL produce spurs at ±2f_REF and not ±f_REF?",
     "At lock the XOR output toggles twice per reference period (both edges), so the ripple fundamental is at $2f_{REF}$."),
    ("Derive the spur level for a sinusoidal ripple.",
     "$\\phi(t) = \\beta\\sin\\omega_mt$ with $\\beta = K_{VCO}A_m/\\omega_m$; for $\\beta\\ll1$, $\\cos(\\omega_0t+\\beta\\sin\\omega_mt) \\approx \\cos\\omega_0t - \\frac\\beta2[\\cos(\\omega_0-\\omega_m)t - \\cos(\\omega_0+\\omega_m)t]$ → each sideband $\\beta/2$."),
    ("What is narrowband FM and when is it valid?",
     "Modulation index $\\beta\\ll1$ (≈ < 0.2 rad): only the first pair of sidebands matters, each at $\\beta/2$; otherwise use Bessel functions $J_n(\\beta)$."),
    ("How does input duty cycle affect an XOR PD?",
     "The triangle is truncated: peak output and gain shrink and the characteristic flattens; with unequal duty cycles the lock point shifts and the range narrows."),
    ("What is false lock and which PDs suffer from it?",
     "Locking with the PD output at its lock value but at the wrong frequency (harmonic/sub-harmonic, or a sideband). Multiplying PDs (mixer, XOR) and sampling PDs; PFDs do not."),
    ("Why is the capture range of a Type-I loop narrow?",
     "The PD output averages to ~zero for frequency offsets beyond the loop bandwidth; only offsets within ~$\\omega_n$ get a DC component strong enough to pull in."),
    ("How do you reduce spurs in a Type-I loop?",
     "Lower $\\omega_{LPF}$ (narrower loop), lower $K_{VCO}$, use a PD with no ripple at lock (sample-and-hold), or add a notch at $2f_{REF}$."),
    ("Proposal spur spec at f_out ± f_REF is −55 dBc typ. Why at f_REF and not 2f_REF for our PLL?",
     "Our SSPD and pulsed charge pump act once per reference period, so disturbances (charge injection, kickback, pulse) repeat at $f_{REF}$."),
    ("Why does a mixer with square waves lock to harmonics?",
     "Odd harmonics of the two squares mix: $3f_1$ with $f_2 = 3f_1$ produces DC too; the loop is satisfied at the wrong ratio."),
    ("Spur from 1 mV ripple at 100 MHz with K_VCO = 2π·300 MHz/V?",
     "$\\beta = 2\\pi\\cdot3\\times10^8\\cdot10^{-3}/(2\\pi\\cdot10^8) = 3\\times10^{-3}$; spur $=20\\log(1.5\\times10^{-3}) = -56.5$ dBc."),
], 28)

# ------------------------------------------------------------------------------------------------ step 29
b.step(29, "Fix: lead-lag filter adds a zero and separates ζ from ω_n", "derivation and plot")
b.md(r"""
### What happens
Replace the RC low-pass by a passive **lag-lead** network: $R_1$ in series, then $R_2$ in series with $C$ to ground.

### How
$$F(s) = \frac{1+s\tau_2}{1+s\tau_1},\qquad \tau_1 = (R_1+R_2)C,\quad \tau_2 = R_2C.$$
With $K = K_{PD}K_{VCO}$:
$$H(s) = \frac{K(1+s\tau_2)}{\tau_1 s^2 + (1+K\tau_2)s + K},\qquad
\boxed{\omega_n = \sqrt{K/\tau_1},\quad \zeta = \frac{\omega_n}{2}\left(\tau_2 + \frac1K\right)}$$
Now $\tau_1$ sets $\omega_n$ and $\tau_2$ (the zero) sets ζ almost independently: you can make the loop narrow and well damped.

### Why it is only a partial fix
At high frequency $F(\infty) = \tau_2/\tau_1 = R_2/(R_1+R_2)$: ripple is attenuated only by this resistor ratio, not by 20 dB/decade.
The static phase error is unchanged (still Type I, still $\Delta\omega/K$ since $F(0) = 1$).
""")
b.code(r"""
from scipy import signal
K = 2*np.pi*20e6; tau1 = 1/(2*np.pi*50e3)                    # wn = sqrt(K/tau1)
t = np.linspace(0, 6e-6, 1500)
def frame(ratio):
    tau2 = ratio*tau1
    wn = np.sqrt(K/tau1); z = wn/2*(tau2+1/K)
    _, y = signal.step(signal.lti([K*tau2, K], [tau1, 1+K*tau2, K]), T=t)
    return ([dict(x=t*1e6, y=y, name="phase-step response")],
            f"tau2/tau1 = {ratio}: f_n = {wn/2/np.pi/1e6:.2f} MHz (fixed), zeta = {z:.2f}, "
            f"ripple floor tau2/tau1 = {20*np.log10(ratio):.0f} dB")
fig = sweep([0.001, 0.003, 0.01, 0.02, 0.05, 0.1], frame, "tau2 / tau1 (zero)", active=2,
            layout=lambda f: f.update_xaxes(title="time (us)").update_yaxes(range=[0, 2]))
show(fig, 420)
""")
b.qa([
    ("Write the lag-lead transfer function and its time constants.",
     "$F = (1+s\\tau_2)/(1+s\\tau_1)$, $\\tau_1 = (R_1+R_2)C$, $\\tau_2 = R_2C$."),
    ("Give ω_n and ζ of a Type-I loop with a lag-lead filter.",
     "$\\omega_n = \\sqrt{K/\\tau_1}$, $\\zeta = \\frac{\\omega_n}{2}(\\tau_2 + 1/K)$."),
    ("What does the zero do physically?",
     "Above $1/\\tau_2$ the capacitor is a short and the filter looks like a resistive divider: phase lag stops growing, adding damping."),
    ("Why is ripple rejection worse with a lag-lead filter?",
     "Its high-frequency gain is $\\tau_2/\\tau_1$, a constant, so the ripple attenuation does not improve with frequency."),
    ("Does the lag-lead filter remove the static phase error?",
     "No: $F(0) = 1$, the loop is still Type I and the error is still $\\Delta\\omega/K$."),
    ("How do you add ripple filtering back?",
     "A small capacitor across the output (third pole) — exactly C2 in a CP-PLL."),
    ("What is an active PI filter and why is it better?",
     "An op-amp with $R$–$C$ feedback: $F = (1+s\\tau_2)/(s\\tau_1)$, which adds an integrator (Type II): zero static error and independent ζ."),
    ("Root-locus effect of the zero?",
     "It bends the locus back toward the real axis, so higher K no longer drives ζ to zero."),
    ("Which element in a CP-PLL plays the role of the lead-lag zero?",
     "R1 in series with C1; the CP itself provides the integrator."),
], 29)

# ------------------------------------------------------------------------------------------------ step 30
b.step(30, "Fix: a sample-and-hold phase detector — DC with almost no ripple", "the bridge to the sub-sampling PD")
b.md(r"""
### What happens
Instead of multiplying the two signals, **sample** the VCO waveform at each reference edge and **hold** the value until the next
edge. At lock the VCO is sampled at the same point of its waveform every time, so the held output is a **constant**.

### How
Sampling $v_{VCO} = A\sin(\omega_{VCO}t)$ at $t_k = kT_{REF}$ gives $v_k = A\sin\phi_e$ with $\phi_e$ the phase of the VCO at the
reference edge (mod 2π). Near zero, $v_k \approx A\phi_e$: gain $A$ V/rad of VCO phase. The hold is a zero-order hold:
$$H_{ZOH}(s) = \frac{1-e^{-sT_{REF}}}{sT_{REF}}\approx e^{-sT_{REF}/2}\ \ (\text{a half-period delay}).$$

### Why it is the key idea
- **No ripple at lock** → spurs come only from parasitic effects (kickback, charge injection), not from the detector's operation.
- The sampled value is a **direct voltage measure of phase error** — the property FFNC (Phase 6) uses.
- Sampling the VCO at $f_{REF}$ even though $f_{VCO} = Nf_{REF}$ (*sub-sampling*) needs no divider: Phase 4.
Price: the hold delay costs phase margin ($360°\cdot f_c\cdot T/2$), and the detector cannot tell harmonics apart (false lock to $N\pm1$).
""")
b.code(r"""
T = 1.0; t = np.linspace(0, 8, 4000)                         # time in reference periods, VCO at 4x for readability
Nv = 4
def frame(pe_deg):
    pe = np.radians(pe_deg)
    vco = np.sin(2*np.pi*Nv*t + pe)
    ref_sq = (np.sin(2*np.pi*t) >= 0).astype(float)
    vco_sq = (vco >= 0).astype(float)
    xor = np.logical_xor(ref_sq, (np.sin(2*np.pi*t + pe/Nv + np.pi/2) >= 0)).astype(float)
    held = np.sin(pe)*np.ones_like(t)                        # sampled at every reference rising edge
    return ([dict(x=t, y=vco, name="VCO waveform (4 x f_REF)", line=dict(width=1)),
             dict(x=np.arange(0, 8), y=np.sin(pe)*np.ones(8), mode="markers", marker=dict(size=9), name="samples at REF edges"),
             dict(x=t, y=held, name="S&H output (held)", line=dict(width=3)),
             dict(x=t, y=xor*0.5-1.6, name="XOR output at the same error (offset)")],
            f"phase error {pe_deg} deg: held output {np.sin(pe):.3f} x A, constant (no ripple); XOR output toggles every half period")
fig = sweep([-30, -10, 0, 10, 30, 60], frame, "VCO phase error at the sample (deg)", active=3,
            layout=lambda f: f.update_xaxes(title="time (reference periods)").update_yaxes(range=[-1.8, 1.3]))
show(fig, 440)
""")
b.qa([
    ("Why does a sample-and-hold PD produce no ripple at lock?",
     "It samples the VCO at the same phase every reference period, so every sample has the same value; the held output is DC."),
    ("What is the gain of a S&H PD sampling a sine of amplitude A?",
     "$A$ V per radian of the sampled signal's phase (small errors); $A\\omega_{VCO}$ V/s of timing error."),
    ("What is the transfer function of a zero-order hold?",
     "$(1-e^{-sT})/(sT)$: magnitude sinc, phase $-\\omega T/2$ (a half-period delay)."),
    ("What does the half-period delay cost?",
     "Phase margin $\\Delta PM = 360°\\,f_cT/2 = 180°f_c/f_{REF}$: 9° at $f_{REF}/20$, 18° at $f_{REF}/10$."),
    ("Why can a sampling PD lock to the wrong frequency?",
     "Any VCO frequency that is an integer multiple of $f_{REF}$ gives a constant sample; the detector cannot count cycles."),
    ("How is a S&H PD different from a mixer PD in noise?",
     "Its noise is sampling (kT/C) noise held for a period, plus the buffer's; there is no 2f ripple, and in the sub-sampling form its noise is not multiplied by N²."),
    ("What practical effects still create spurs with a S&H PD?",
     "Kickback of the sampling switch onto the VCO, charge injection and clock feedthrough, charge sharing between sampling and hold capacitors, and VCO load modulation as the switch toggles."),
    ("Why is the sampled voltage useful for noise cancellation?",
     "It is a direct, continuous-valued measure of each edge's timing error; scaled by $1/K_{SSPD}$ it can drive a delay line that removes the error (FFNC)."),
    ("Is a S&H PD loop Type I or Type II?",
     "Whatever the rest makes it: with an RC filter it is Type I; with a (pulsed) charge pump into a capacitor it is Type II (our case)."),
    ("Why sample with the reference rather than with the divided VCO?",
     "The reference edge is clean (crystal); sampling the VCO waveform directly converts its phase error into voltage with high gain and no divider noise."),
], 30)

# ------------------------------------------------------------------------------------------------ step 31
b.step(31, "Fix: a frequency detector for acquisition, and a second integrator (→ Type II)", "note")
b.md(r"""
### What happens
Two remaining Type-I problems need structural fixes: **narrow capture/false lock** and **static phase error**.

### How
1. **Frequency detector.** Add a detector whose average output follows the *sign of the frequency error* (a PFD, a quadricorrelator,
   or our dead-zone FLL). It pulls the VCO into the capture range; then the phase loop takes over.
2. **Second integrator.** Make the filter integrate: $F(s) = \frac{1+s\tau_2}{s\tau_1}$ (active PI filter) or a charge pump into a
   capacitor. Then $G \propto 1/s^2$ at low frequency and the final-value theorem gives **zero** phase error for a frequency step.

### Why the charge pump wins
A PFD + charge pump provides *both* fixes at once: frequency detection and an integrator, with no op-amp. That is the
Type-II charge-pump PLL of Phase 3. Below, a PI-like integral path is added to a Type-I loop: watch the static error disappear.
""")
b.code(r"""
from scipy import signal
K = 2*np.pi*2e6; t = np.linspace(0, 8e-6, 2000); dw = 2*np.pi*1e6
def frame(r):                                            # integral corner w_i = r*K: G = K/s * (1 + w_i/s)
    wi = r*K
    E = signal.lti([1, 0, 0], [1, K, K*wi])              # 1/(1+G) = s^2/(s^2 + K s + K wi)
    if r == 0:
        E = signal.lti([1, 0], [1, K])
    _, e, _ = signal.lsim(E, dw*t, t)
    return ([dict(x=t*1e6, y=e, name="phase error after a 1 MHz frequency step (rad)")],
            f"integral path w_i = {r} x K: final error {e[-1]:.3f} rad (Type I alone: {dw/K:.3f} rad)")
fig = sweep([0, 0.05, 0.1, 0.25, 0.5], frame, "integral corner w_i / K", active=2,
            layout=lambda f: f.update_xaxes(title="time (us)").update_yaxes(title="rad", range=[-0.05, 0.6]))
show(fig, 420)
""")
b.qa([
    ("How does adding an integrator remove static phase error?",
     "The integrator's output can hold any DC control voltage with zero input; the PD output (phase error) can return to zero."),
    ("What is a quadricorrelator?",
     "A frequency detector using I/Q mixing and differentiation whose output is proportional to the frequency difference; used in analog CDRs and PLLs to extend pull-in."),
    ("Why does a PFD provide both frequency detection and integration?",
     "Its state machine gives a frequency-sensitive average output; driving a charge pump into a capacitor turns that output into an integrated control voltage."),
    ("What new problem does the second integrator create?",
     "Two poles at the origin: −180° phase; a zero is needed for stability (Phase 3, step 34)."),
    ("Why use a frequency-locked loop in an SSPLL instead of the PFD loop permanently?",
     "The SSPD loop has much lower in-band noise; a permanently active PFD/CP adds N²-multiplied noise and spurs. The FLL only acquires and then becomes quiet (dead zone)."),
    ("What is 'hand-over' between two loops?",
     "The transition from the acquisition loop (FLL) to the low-noise phase loop (SSPD), designed so the FLL stops acting once the frequency is right and the phase error is within its dead zone."),
    ("What is the ratio $\\omega_i/K$ in the plot, physically?",
     "The corner frequency of the PI filter's integral path relative to the loop gain; it sets how fast the static error is integrated away (and the damping)."),
    ("Can a Type-I loop with a frequency detector reach zero phase error?",
     "Not with a constant frequency offset: the FD gets the frequency right but the phase loop still needs a phase error to hold the control voltage unless an integrator is added."),
], 31)

# ------------------------------------------------------------------------------------------------ step 32
b.step(32, "Lab: static error vs offset, ripple vs bandwidth (waveform-level simulation)", "plots and answers")
b.md(r"""
### What you do
Simulate a **real-signal** Type-I PLL (not the phase model): two square waves, an XOR, an RC filter and a VCO integrated with a
fine time step. Sweep the frequency offset and watch (1) the static phase error grow as $\Delta\omega/K$, (2) the $2f_{REF}$ ripple
on $V_{cont}$, and (3) loss of lock beyond the hold-in range $K_{PD}K_{VCO}\pi/2$.
""")
b.code(r"""
def xor_pll(df_rel, ncyc=60, nper=200, fl_rel=0.05, K_rel=0.2, Vdd=1.0):
    # normalised: f_REF = 1, VCO free-running = 1 + df_rel; K_VCO chosen so K = K_PD*K_VCO = K_rel*2*pi
    dt = 1/nper; n = ncyc*nper
    Kpd = Vdd/np.pi; Kv = K_rel*2*np.pi/Kpd
    wl = 2*np.pi*fl_rel
    ph_v, vc = 0.0, 0.5*Vdd                      # start at mid-rail (XOR centre)
    out_vc, out_pe = np.empty(n), np.empty(n)
    for k in range(n):
        t = k*dt
        ref = (np.sin(2*np.pi*t) >= 0); vco = (np.sin(ph_v) >= 0)
        x = Vdd*float(ref ^ vco)
        vc += (x - vc)*wl*dt                     # RC low-pass
        ph_v += 2*np.pi*(1 + df_rel)*dt + Kv*(vc - 0.5*Vdd)*dt
        out_vc[k] = vc; out_pe[k] = (2*np.pi*t - ph_v)
    return np.arange(n)*dt, out_vc, out_pe
def frame(dfr):
    t, vc, pe = xor_pll(dfr)
    hold = 0.2*np.pi/2                                  # static hold-in: K*pi/2 / (2*pi) in units of f_REF
    pe_deg = np.degrees(pe)
    locked = abs(pe_deg[-1] - pe_deg[-400]) < 5
    state = (f"locked at {pe_deg[-1]:.0f} deg = 90 - {90-pe_deg[-1]:.0f} deg static error "
             f"(predicted {np.degrees(2*np.pi*dfr/(0.2*2*np.pi)):.0f} deg)") if locked else \
            "NOT locked: cycle slips during the underdamped transient (inside the static hold-in range!)"
    return ([dict(x=t, y=vc, name="V_cont (V, Vdd = 1)", row=1, col=1),
             dict(x=t, y=pe_deg, name="phase difference REF - VCO (deg)", row=2, col=1)],
            f"offset {dfr*100:.0f}% of f_REF (static hold-in {hold*100:.0f}%): {state}")
fig = sweep([0.0, 0.02, 0.05, 0.1, 0.12, 0.15, 0.2], frame, "frequency offset (fraction of f_REF)", active=2, rows=2, cols=1,
            shared_xaxes=True, subplot_titles=("control voltage with 2 f_REF ripple", "phase difference"), height=600, maxpts=3000,
            layout=lambda f: f.update_xaxes(title_text="time (reference periods)", row=2, col=1))
show(fig)
""")
b.md(r"""
**What to look for.** Small offsets: the phase settles at 90° minus the predicted static error $\Delta\omega/K$ and $V_{cont}$
shows a triangular ripple at $2f_{REF}$. Larger offsets (still *inside* the static hold-in range of 31%): this loop is
underdamped (ζ ≈ 0.25), the transient overshoots past the edge of the XOR characteristic and the loop slips cycles — the
**lock-in range is smaller than the hold-in range** (step 21).

**Exercise.** Lower the filter corner (`fl_rel=0.02`) in `xor_pll`: the ripple shrinks, but the loop becomes underdamped
(ringing in the phase) — the coupling of step 27 seen in a waveform simulation.
""")
b.qa([
    ("Why does V_cont ripple at 2f_REF in an XOR PLL at lock?",
     "The XOR output is a 50% square at twice the reference frequency at the 90° lock point; the RC only attenuates it."),
    ("What waveform does the ripple have after a single-pole RC with a corner well below 2f_REF?",
     "Approximately triangular (the capacitor integrates the square wave)."),
    ("How do you recognise loss of lock in a transient simulation?",
     "The phase difference drifts without bound (staircase of cycle slips) and V_cont shows a beat at the difference frequency instead of settling."),
    ("Why simulate at the waveform level at all if the phase model is linear?",
     "To see effects the linear model omits: ripple, nonlinear PD characteristic, cycle slips, acquisition and false lock."),
    ("In the lab, why does the static error follow Δω/K only for small offsets?",
     "Near the edge of the PD range the characteristic is no longer linear (triangle tip) and the gain falls."),
    ("What sets the time step in such a simulation?",
     "It must resolve the fastest edges and the ripple: here 200 points per reference period; for a GHz VCO this is why transistor-level lock simulations are slow."),
    ("How would you measure the ripple-induced spur from this simulation?",
     "FFT of the VCO output (or of its phase) over many periods with a window; read the sideband at ±2f_REF relative to the carrier."),
    ("Quiz: a Type-I loop has K = 2π·2 MHz; the input steps by 200 kHz. What is the new static error?",
     "$\\Delta\\phi = 2\\pi\\cdot2\\times10^5/(2\\pi\\cdot2\\times10^6) = 0.1$ rad ≈ 5.7°."),
    ("Quiz: for ζ = 0.707 with f_LPF = 2 MHz, what is f_n?",
     "$f_n = f_{LPF}/\\sqrt2 = 1.41$ MHz."),
    ("Quiz: which of these remove static phase error: lead-lag filter, higher K, PI filter, charge pump?",
     "PI filter and charge pump (both add an integrator). Higher K only reduces it; lead-lag does not change it."),
], 32)

b.save(os.path.join(os.path.dirname(__file__), "..", "phase2_type1.ipynb"))
