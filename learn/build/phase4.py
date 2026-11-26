"""Phase 4 - Sub-sampling PLL: basics, what it solves, its limits and fixes (roadmap steps 46-58). Part A: 46-52."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nb import Book

b = Book("Phase 4 — The sub-sampling PLL (steps 46–58)",
         "Sampling the VCO directly with the reference turns timing error into a large voltage. There is no divider in the "
         "loop, and the phase-detector and charge-pump noise are **not** multiplied by N² (Gao, Klumperink, Bohsali, Nauta, "
         "JSSC 2009). This phase builds the SSPLL from the sampling theorem up, derives every gain and noise term for our "
         "50 MHz × 32 = 1.6 GHz design, and simulates acquisition with the dead-zone FLL — the exact architecture of the proposal.")

SIM = r'''
def sspll_sim(off_ref, use_fll=True, ncyc=2500, kick_at=None, kick_V=0.0, A=0.5, beta=1.0e-6, Kv_Hz=300e6,
              fref=50e6, N=32, fc=2.5e6, pm_deg=50, Ifll=10e-6, dz=0.65*np.pi, tau=0.2e-9):
    """Cycle-by-cycle SSPLL with an optional dead-zone FLL.
    VCO free-running at (N + off_ref)*fref; SSPD samples A*sin(e) where e = VCO phase - 2*pi*N*k (wrapped);
    pulsed Gm injects -(beta*2*pi)... charge so that the average current is -beta*sin(e) per rad (small-signal beta A/rad);
    FLL: PFD between REF and VCO/N with cycle-slip memory p (rad of REF) and a dead zone |p| < dz.
    Loop filter = 3rd-order design for f_c, pm with the SSPD gain beta (A/rad of VCO phase)."""
    from scipy.linalg import expm
    T = 1/fref; Kv = 2*np.pi*Kv_Hz
    d = sl.loop_design_type2(fc, pm_deg, 2*np.pi*N*beta, Kv, N)      # same equations: I_p/(2 pi N) -> beta
    R, C1, C2 = d['R'], d['C1'], d['C2']
    Am = np.array([[-1/(R*C1), 1/(R*C1), 0], [1/(R*C2), -1/(R*C2), 0], [0, Kv, 0]])
    Bv = np.array([0, 1/C2, 0])
    def prop(dt):
        M = np.zeros((4, 4)); M[:3, :3] = Am; M[:3, 3] = Bv
        E = expm(M*dt); return E[:3, :3], E[:3, 3]
    E1, b1 = prop(tau); E2, b2 = prop(T - tau)
    x = np.zeros(3); p = 0.0; psi_prev = 0.0; fll_on = False
    out = dict(t=[], f=[], e=[], vc=[], fll=[])
    for k in range(ncyc):
        phi = 2*np.pi*(N + off_ref)*k + x[2]                 # VCO phase at the k-th REF edge (rad)
        e = np.angle(np.exp(1j*(phi - 2*np.pi*N*k)))          # wrapped VCO phase error seen by the SSPD
        i_ss = -beta*np.sin(e)*T/tau                         # pulsed Gm: average current -beta*sin(e)
        psi = phi/N - 2*np.pi*k                               # divider phase vs REF (rad of REF)
        p += psi - psi_prev; psi_prev = psi
        if p > 2*np.pi: p -= 2*np.pi                          # PFD cycle slip keeps the sign (frequency detection)
        if p < -2*np.pi: p += 2*np.pi
        i_f = 0.0
        if use_fll and abs(p) > dz:
            i_f = -np.sign(p)*Ifll*(abs(p)/(2*np.pi))*T/tau   # same charge as a PFD pulse of width |p|/2pi*T
        if kick_at is not None and k == kick_at:
            x[0] += kick_V; x[1] += kick_V                     # disturbance moves the whole filter state
        x = E1 @ x + b1*(i_ss + i_f); x = E2 @ x
        if k % 5 == 0:
            out['t'].append(k*T); out['e'].append(e); out['vc'].append(x[1]); out['fll'].append(i_f != 0)
            out['f'].append(N + off_ref + Kv_Hz*x[1]/fref)    # VCO frequency in units of f_REF
    return {k: np.array(v) for k, v in out.items()}, d
'''

# ------------------------------------------------------------------------------------------------ step 46
b.step(46, "Sampling fundamentals: sample-and-hold, aliasing, sub-sampling 1.6 GHz at 50 MHz", "spectrum plot")
b.md(r"""
### What happens
Sampling a signal at rate $f_s$ cannot distinguish frequencies that differ by multiples of $f_s$: a tone at $f$ appears at the
**alias** $|f - kf_s|$ closest to DC. Sub-sampling deliberately samples a high-frequency signal far below Nyquist.

### How
Sample $v(t) = A\sin(2\pi f_{VCO}t + \phi)$ at $t_k = kT_{REF}$:
$$v_k = A\sin\!\big(2\pi f_{VCO}kT_{REF} + \phi\big) = A\sin\!\big(2\pi (f_{VCO}-Nf_{REF})kT_{REF} + \phi\big)$$
because $2\pi Nf_{REF}kT_{REF} = 2\pi Nk$ is a whole number of cycles. So the samples are a sine at the **beat frequency**
$f_{VCO}-Nf_{REF}$. When $f_{VCO} = 32\times50\text{ MHz} = 1.6$ GHz exactly, the beat is zero and **every sample has the same value**
$A\sin\phi$ — a DC level that depends only on the phase.

### Why it works as a phase detector
The sampler is a mixer with the reference's harmonics: the $N$-th harmonic of the sampling pulse train down-converts the VCO to DC.
No divider is needed to "bring the VCO down" to $f_{REF}$.
""")
b.code(r"""
fref, N = 50e6, 32
t = np.linspace(0, 12/fref, 6000); k = np.arange(13)
def frame(df_MHz):
    fv = N*fref + df_MHz*1e6
    v = np.sin(2*np.pi*fv*t + 0.4)
    vk = np.sin(2*np.pi*fv*k/fref + 0.4)
    beat = np.sin(2*np.pi*df_MHz*1e6*t + 0.4)
    return ([dict(x=t*1e9, y=v, name="VCO waveform", line=dict(width=0.6)),
             dict(x=k/fref*1e9, y=vk, mode="markers", marker=dict(size=10), name="samples at REF edges"),
             dict(x=t*1e9, y=beat, name="beat |f_VCO - 32 f_REF|", line=dict(dash="dash"))],
            f"f_VCO = {fv/1e9:.4f} GHz: samples form a {abs(df_MHz):.1f} MHz beat" + (" -> DC (locked)" if df_MHz == 0 else ""))
fig = sweep([-4, -2, -1, 0, 1, 2, 4], frame, "f_VCO - 1.6 GHz (MHz)", active=4,
            layout=lambda f: f.update_xaxes(title="time (ns)").update_yaxes(range=[-1.3, 1.3]))
show(fig, 440)
""")
b.qa([
    ("What is sub-sampling?",
     "Sampling a band-pass signal at a rate below twice its highest frequency (but adequate for its bandwidth); the signal aliases to a lower frequency. In an SSPLL the VCO aliases to DC at lock."),
    ("Why are the samples constant at lock?",
     "$f_{VCO} = Nf_{REF}$ exactly, so between two samples the VCO completes exactly N cycles and is at the same phase."),
    ("What frequency do the samples show when the VCO is off by Δf?",
     "The beat $|f_{VCO} - kf_{REF}|$ for the nearest integer k; e.g. 1.601 GHz sampled at 50 MHz shows 1 MHz."),
    ("Why is a sampler equivalent to a mixer here?",
     "The sampling pulse train contains all harmonics of $f_{REF}$; the 32nd harmonic multiplies the VCO and produces a DC term proportional to $\\sin\\phi$."),
    ("What is aliasing and why is it usually avoided?",
     "Frequency components above Nyquist fold into the band; in data conversion it corrupts the signal, so anti-alias filters are used. In the SSPLL the folding is the mechanism; its side effect is that VCO noise at offsets around multiples of $f_{REF}$ also folds (relevant for FFNC, Phase 6)."),
    ("What sampling bandwidth must the SSPD switch have?",
     "Enough to track a 1.6 GHz waveform: the switch on-resistance × sampling capacitor must be well below the VCO period (track time constant ≪ 100 ps) to avoid gain loss and phase shift."),
    ("Does the SSPD care about f_REF duty cycle?",
     "Only the sampling edge matters; duty affects the track/hold time available."),
    ("What is the 'aperture jitter' of a sampler and why does it matter here?",
     "Uncertainty of the sampling instant; it adds directly to the measured phase error, like reference jitter (×N² at the output)."),
    ("How many samples per VCO period does the SSPD take?",
     "One sample every 32 VCO periods — far from Nyquist for the waveform, but the information needed (phase at one point) is captured."),
], 46)

# ------------------------------------------------------------------------------------------------ step 47
b.step(47, "Why the sample is DC at lock; sample ∝ timing error; K_t and K_PD", "K_t = slope at the zero crossing; K = A (sine) or edge slope (ring)")
b.md(r"""
### What happens
At lock the loop drives the sampled value to the zero crossing of the VCO waveform. A small timing error $\Delta t$ between the
reference edge and the VCO zero crossing then gives a proportional sample.

### How
$$v_{sam} = A\sin(\omega_{VCO}\Delta t)\approx \underbrace{A\,\omega_{VCO}}_{K_t\ [\text{V/s}]}\Delta t = \underbrace{A}_{K_{PD}\ [\text{V/rad}]}\Delta\phi_{VCO}.$$
For a ring oscillator the waveform is closer to a trapezoid; the gain is the **slope at the crossing**: $K_t = SR$ (slew rate, V/s) and
$K_{PD} = SR/\omega_{VCO}$ (V per VCO radian). Nagam & Kinget write $K_{t,SSPD}$ (V/s) and $K_{\phi,SSPD} = K_{t,SSPD}/(2\pi f_{out})$.

**Numbers (assumed amplitude A = 0.5 V at 1.6 GHz):** $K_{PD} = 0.5$ V/rad, $K_t = 0.5\cdot2\pi\cdot1.6\times10^9 = 5.0$ mV/ps.
Compare a PFD/CP: $I_p/(2\pi N)$ = 100 µA/(2π·32) = 0.50 µA per VCO radian into the filter.

### Why it matters
The SSPD gain is large and referred directly to VCO phase — so its own noise, divided by this gain, is tiny in phase terms. It is also
**amplitude-dependent** (A or SR changes with supply and corner), which moves the loop gain (step 56).
""")
b.code(r"""
fv = 1.6e9; tt = np.linspace(-0.4/fv, 0.4/fv, 400)
def frame(dt_ps):
    sine = 0.5*np.sin(2*np.pi*fv*tt)
    ring = 0.5*np.tanh(3*np.sin(2*np.pi*fv*tt))/np.tanh(3)          # sharper, ring-like waveform
    vs_s = 0.5*np.sin(2*np.pi*fv*dt_ps*1e-12); vs_r = 0.5*np.tanh(3*np.sin(2*np.pi*fv*dt_ps*1e-12))/np.tanh(3)
    return ([dict(x=tt*1e12, y=sine, name="sine, A = 0.5 V"), dict(x=tt*1e12, y=ring, name="ring-like waveform"),
             dict(x=[dt_ps, dt_ps], y=[vs_s, vs_r], mode="markers", marker=dict(size=11), name="samples at REF edge")],
            f"timing error {dt_ps} ps: sine sample {vs_s*1e3:.1f} mV (K_t = {0.5*2*np.pi*fv*1e-12*1e3:.2f} mV/ps), "
            f"ring sample {vs_r*1e3:.1f} mV (steeper slope, saturates earlier)")
fig = sweep([-60, -20, -5, 0, 5, 20, 60, 120], frame, "timing error (ps)", active=4,
            layout=lambda f: f.update_xaxes(title="time around the VCO zero crossing (ps)").update_yaxes(title="V"))
show(fig, 430)
""")
b.qa([
    ("Derive the SSPD gain.",
     "$v = A\\sin(\\omega_{VCO}\\Delta t) \\approx A\\omega_{VCO}\\Delta t$; per VCO radian $K_{PD} = A$; per second $K_t = A\\omega_{VCO}$."),
    ("Why does the SSPLL lock at a zero crossing?",
     "That is where the sample is zero for zero CP current (no correction needed) and where the slope (gain) is maximum, so the equilibrium is stable and linear."),
    ("Which zero crossing — rising or falling?",
     "The one with the slope sign that gives negative feedback for the chosen CP polarity; the other crossing is an unstable equilibrium."),
    ("How do you define the SSPD gain for a ring oscillator?",
     "By the slope (slew rate) of the sampled waveform at the crossing: $K_t = dv/dt$; it depends on the ring's swing and rise time."),
    ("How does the SSPD gain compare with a CP-PLL detector referred to the VCO?",
     "CP: $I_p/(2\\pi N)$ A per VCO radian (shrinks with N). SSPD: $A$ V per VCO radian, then $g_m$ (and duty) converts it to current — orders of magnitude larger before scaling."),
    ("Why is the SSPD gain amplitude-dependent and is that a problem?",
     "It is the waveform slope; the amplitude varies with supply, corner and frequency, so loop gain (bandwidth, PM) varies; designs limit the variation or accept it with margin."),
    ("What is the timing resolution needed to read 1 mV of SSPD output?",
     "$1\\,mV / 5.0\\,mV/ps \\approx 0.2$ ps — the SSPD is a very sensitive timing detector."),
    ("What limits the linear range of the SSPD?",
     "The sine's curvature: linear only for $|\\Delta\\phi| \\ll \\pi/2$, i.e. about ±40 ps of a 625 ps period for <10% gain error; beyond ±π/2 the slope reverses."),
    ("Relation between K_t and K_phi in Nagam & Kinget?",
     "$K_{\\phi,SSPD} = K_{t,SSPD}/(2\\pi f_{out})$; the NCB gain must be $1/K_t$ (s/V), equivalently $1/K_\\phi$ (rad/V)."),
], 47)

# ------------------------------------------------------------------------------------------------ step 48
b.step(48, "Phase-domain model: virtual ×N on the reference, no ÷N in the feedback", "why PD/CP noise skips N² but reference noise does not")
b.md(r"""
### What happens
The SSPD compares the VCO phase with the reference phase **multiplied by N** (in VCO radians, the reference edge advances
$2\pi N$ per period). There is no divider in the feedback.

### How
Let $\beta$ be the SSPD+CP gain in amperes per VCO radian (step 50: $\beta = 2A g_m\tau/T_{REF}$). Then
$$G(s) = \beta\,Z(s)\,\frac{K_{VCO}}{s},\qquad \Phi_{out} = \frac{G}{1+G}\big(N\Phi_{REF} + \Phi_{n,SSPD}\big) + \frac{1}{1+G}\Phi_{VCO}.$$
Compare the CP-PLL: $G = \frac{I_p}{2\pi N}Z\frac{K_{VCO}}{s}$ and $\Phi_{out} = \frac{NG}{1+G}(\Phi_{REF} + \Phi_{n,PFD/CP})+\dots$

**Noise referral.** An SSPD voltage noise $v_n$ appears as $\Phi_{n,SSPD} = v_n/A$ **VCO** radians; it reaches the output with gain 1
in band. A PFD/CP noise current $i_n$ appears as $2\pi i_n/I_p$ **reference** radians and reaches the output ×N. Reference
jitter is a time error; any loop converts it to $N\times$ more VCO radians — so reference noise is ×N² in both.

### Why it matters
The detector's noise floor drops by roughly $20\log N$ (30 dB for N = 32), leaving the reference (crystal + buffer) as the in-band
limit: −152 dBc/Hz + 30.1 = −121.9 dBc/Hz at 1.6 GHz in our budget.
""")
b.code(r"""
import sys; sys.path.insert(0, "../models")
import pllmodel as pm
f = pm.freq_axis(n=500)
def frame(fc_MHz):
    H = pm.loop_H(f, fc_MHz*1e6, 50)
    return ([dict(x=f, y=20*np.log10(abs(H)) + 20*np.log10(32), name="REF -> out: N H (+30.1 dB in band)"),
             dict(x=f, y=20*np.log10(abs(H)), name="SSPD noise (VCO rad) -> out: H"),
             dict(x=f, y=20*np.log10(abs(H)) + 20*np.log10(32), name="CP-PLL PFD/CP noise (REF rad) -> out: N H", line=dict(dash="dot")),
             dict(x=f, y=20*np.log10(abs(1-H)), name="VCO -> out: 1 - H")],
            f"noise transfer functions, f_c = {fc_MHz} MHz (PM 50 deg)")
fig = sweep([1.0, 2.5, 5.0], frame, "f_c (MHz)", active=1,
            layout=lambda f: f.update_xaxes(type="log", title="offset (Hz)").update_yaxes(title="dB", range=[-60, 40]))
show(fig, 440)
""")
b.qa([
    ("Why is PD noise not multiplied by N² in an SSPLL?",
     "The SSPD measures the VCO phase directly (gain A per VCO radian); its noise referred to the output is $v_n/A$ VCO radians with unity in-band gain. A PFD measures divided phase, so its noise referred to the output is multiplied by N."),
    ("Is the reference noise still multiplied by N²?",
     "Yes: a reference timing error $\\Delta t$ is $2\\pi f_{out}\\Delta t = N\\cdot2\\pi f_{REF}\\Delta t$ VCO radians; the loop reproduces it."),
    ("What is the loop gain of an SSPLL?",
     "$G = \\beta Z(s) K_{VCO}/s$ with $\\beta$ in A per VCO radian; formally the CP-PLL expression with $I_p/(2\\pi N)$ replaced by $\\beta$."),
    ("Where does the 'virtual multiplication by N' come from?",
     "Each reference period corresponds to N VCO cycles, so the reference phase expressed in VCO radians is $N\\phi_{REF}$; the SSPD compares $\\phi_{VCO}$ with that."),
    ("What is the in-band floor of our SSPLL according to the budget?",
     "Reference: −152 + 30.1 = −121.9 dBc/Hz; SSPD+CP: −130 dBc/Hz (typ). The reference dominates in band."),
    ("Does the divider noise matter in an SSPLL?",
     "Not in lock: the divider (FLL) is outside the main loop and its PFD is in its dead zone."),
    ("Why do SSPLLs reach −120 to −126 dBc/Hz in-band at 2 GHz (Gao) while CP-PLLs rarely do?",
     "No N² on the detector; the remaining floor is the reference (×N²) and the sampler/Gm noise referred by a large gain A."),
    ("In which units must you be careful when mixing SSPLL and CP-PLL formulas?",
     "SSPLL gains are per VCO radian, CP-PLL gains per reference radian (factor N), and $K_{VCO}$ is in rad/s/V."),
], 48)

# ------------------------------------------------------------------------------------------------ step 49
b.step(49, "Sampler kT/C noise: single-ended vs differential, numbers for 54 fF and 100 fF", "noise table")
b.md(r"""
### What happens
Each time the sampling switch opens, the capacitor freezes a random thermal-noise voltage of variance $kT/C$ (independent of the
switch resistance: a larger R gives more noise density but a narrower bandwidth).

### How — referred to output phase noise
One sample per reference period: $\sigma_v^2 = kT/C$ (single-ended). In VCO radians $\sigma_\phi^2 = \sigma_v^2/A^2$. A white sequence held
for $T_{REF}$ has a one-sided PSD of $2\sigma^2/f_{REF}$ at low frequency, so (with $\mathcal L = S_\phi/2$)
$$\mathcal L_{SSPD} = \frac{kT}{C\,A^2 f_{REF}}\ (\text{single-ended}),\qquad
\mathcal L_{SSPD,diff} = \frac{2kT/C}{(2A)^2 f_{REF}} = \frac{kT}{2CA^2f_{REF}}\ (\text{differential, 3 dB better}).$$
This in-band noise is **not** multiplied by N.

### Why the numbers matter
With A = 0.5 V (assumed) and 50 MHz: 100 fF → −144.8 dBc/Hz (SE), −147.8 (diff); 54 fF → −142.1 / −145.1. All are ≥ 20 dB below the
reference contribution (−121.9), which is why Nagam & Kinget conclude a 100 fF sampler is negligible compared with the reference buffer.
""")
b.code(r"""
Cs = np.array([25, 54, 100, 200, 400])*1e-15
def frame(A):
    se = 10*np.log10(kT/(Cs*A**2*50e6)); di = se - 10*np.log10(2)
    return ([dict(x=Cs*1e15, y=se, mode="lines+markers", name="single-ended"), dict(x=Cs*1e15, y=di, mode="lines+markers", name="differential"),
             dict(x=[25, 400], y=[-152+30.1]*2, name="REF floor x N^2 (-121.9)", line=dict(dash="dot"))],
            f"A = {A} V at f_REF = 50 MHz: 100 fF -> {10*np.log10(kT/(100e-15*A**2*50e6)):.1f} dBc/Hz (SE), 54 fF -> {10*np.log10(kT/(54e-15*A**2*50e6)):.1f} dBc/Hz")
fig = sweep([0.2, 0.3, 0.5, 0.7, 0.9], frame, "sampled amplitude A (V)", active=2,
            layout=lambda f: f.update_xaxes(type="log", title="sampling capacitor (fF)").update_yaxes(title="in-band L at 1.6 GHz (dBc/Hz)", range=[-160, -115]))
show(fig, 420)
""")
b.qa([
    ("Why is sampled thermal noise kT/C, independent of R?",
     "Noise density $4kTR$ times the noise bandwidth $1/(4RC)$ gives $kT/C$: a bigger R adds density but narrows the bandwidth by the same factor."),
    ("Derive the in-band phase noise of an SSPD.",
     "$\\sigma_\\phi^2 = kT/(CA^2)$ per sample, white at $f_{REF}$, held: one-sided $S_\\phi = 2\\sigma_\\phi^2/f_{REF}$; $\\mathcal L = S_\\phi/2 = kT/(CA^2f_{REF})$."),
    ("Why is a differential SSPD 3 dB better?",
     "Two caps give $2kT/C$ noise variance on the difference, but the signal slope doubles (4× power), so the ratio improves by 2."),
    ("What is the SSPD noise for C = 100 fF, A = 0.5 V, f_REF = 50 MHz?",
     "$4.14\\times10^{-21}/(10^{-13}\\cdot0.25\\cdot5\\times10^7) = 3.3\\times10^{-15}$ → −144.8 dBc/Hz single-ended."),
    ("Why not make C very small to save area and VCO loading?",
     "Noise rises as 1/C, and charge injection/kickback relative to C grows; also charge sharing with the hold capacitor changes gain."),
    ("Besides kT/C, what other SSPD noise sources exist?",
     "Sampling-edge (aperture) jitter of the reference buffer, the buffer/isolation amplifier noise, the transconductor noise (step 50)."),
    ("Why is the sampler noise not multiplied by N while aperture jitter is?",
     "Aperture jitter is a timing error of the reference edge (×N² like reference noise); kT/C is a voltage error at the detector output, referred through the large gain A."),
    ("Does a higher f_REF help the SSPD noise?",
     "Yes, by $10\\log f_{REF}$: more samples per second average the noise; also N falls, reducing the reference's N² contribution."),
], 49)

# ------------------------------------------------------------------------------------------------ step 50
b.step(50, "Pulsed-Gm charge pump: why the gain is reduced, β = 2·A·g_m·τ/T_REF, noise ∝ T/τ, dump node", "derivation")
b.md(r"""
### What happens
The held sample drives a transconductor $g_m$ whose output current is connected to the loop filter only during a short pulse
$\tau$ each reference period (Gao's "pulser"). The rest of the time the current goes to a **dump** node.

### How
Differential sample $v = 2A\sin\Delta\phi$ → current $g_m v$ for $\tau$ out of $T_{REF}$ → average
$$\overline{I} = g_m\cdot2A\sin\Delta\phi\cdot\frac{\tau}{T_{REF}}\ \Rightarrow\ \boxed{\beta = \frac{2A\,g_m\,\tau}{T_{REF}}\ [\text{A per VCO rad}]}$$
Loop design (step 36 with $I_p/2\pi N\to\beta$): $C_{tot} = \frac{b\,\beta K_{VCO}}{\omega_c^2}$. **The SSPD gain is so large that without
pulsing the filter would need nanofarads**; shrinking the duty $\tau/T$ is the cheapest way to reduce $\beta$.

**Noise.** The transconductor's noise current is gated with the same duty $d = \tau/T$: noise *power* scales with $d$, signal with $d^2$,
so the input-referred noise scales as $1/d$ — **noise ∝ T/τ**. Short pulses save area but cost noise.

**Dump node.** While the pulse is off, the $g_m$ current is steered to a node held at $V_{cont}$ (buffer), so the current source never
turns off and no charge sharing occurs when it reconnects (step 42).
""")
b.code(r"""
Kv, wc = 2*np.pi*300e6, 2*np.pi*2.5e6; A = 0.5; gm = 100e-6; fref = 50e6
bpm = np.tan(np.radians(45+50/2))
def frame(tau_ps):
    beta = 2*A*gm*tau_ps*1e-12*fref
    Ct = bpm*beta*Kv/wc**2
    duty = np.logspace(-3, 0, 200)
    return ([dict(x=duty*100, y=bpm*2*A*gm*duty*Kv/wc**2*1e12, name="C_tot (pF) for f_c = 2.5 MHz, PM 50", row=1, col=1),
             dict(x=duty*100, y=10*np.log10(1/duty), name="relative Gm noise (dB, = 10 log T/tau)", row=1, col=2),
             dict(x=[tau_ps*1e-12*fref*100], y=[Ct*1e12], mode="markers", marker=dict(size=12), name="this tau", row=1, col=1)],
            f"tau = {tau_ps} ps (duty {tau_ps*1e-12*fref*100:.2f}%), g_m = 100 uS, A = 0.5 V: beta = {beta*1e9:.0f} nA/rad, C_tot = {Ct*1e12:.1f} pF")
fig = sweep([50, 100, 200, 400, 1000, 4000, 20000], frame, "pulse width tau (ps)", active=2, rows=1, cols=2,
            subplot_titles=("loop-filter capacitance", "Gm noise penalty"), height=420,
            layout=lambda f: f.update_xaxes(type="log", title_text="duty tau/T (%)").update_yaxes(type="log", row=1, col=1))
show(fig)
""")
b.qa([
    ("Derive β for a pulsed-Gm charge pump.",
     "Current $g_m\\cdot2A\\sin\\Delta\\phi$ for $\\tau$ per period → average $2Ag_m(\\tau/T)\\Delta\\phi$ for small errors → $\\beta = 2Ag_m\\tau/T$."),
    ("Why does an SSPLL need its gain reduced?",
     "The SSPD+Gm gain is so high that, for a few-MHz loop, $C_{tot} = b\\beta K_{VCO}/\\omega_c^2$ would be enormous; pulsing reduces β without changing the detector."),
    ("Why does pulsing increase noise?",
     "Signal current scales with duty d, gated noise power with d: SNR falls as d, input-referred noise rises as 1/d (∝ T/τ)."),
    ("Why use a dump node?",
     "To keep the transconductor always conducting (steered, not switched off) at a node held at $V_{cont}$, avoiding turn-on transients and charge sharing at reconnection."),
    ("What else does the pulse position do?",
     "It sets the effective loop delay: a pulse right after sampling shortens the delay versus a full T/2 hold, improving phase margin (Thijssen)."),
    ("How does the pulse width vary over PVT and why does it matter?",
     "An RC pulser's width follows R and C (±15–35% with R/C corners and temperature); β and the loop bandwidth follow. Our audit suggested timing the pulse from the divided VCO for a PVT-stable width."),
    ("What is the old design's β and its bandwidth?",
     "311 nA/rad with f_c = 1.16 MHz (old slides, 2.36 GHz); the new proposal targets 2.5 MHz."),
    ("What sets the minimum practical τ?",
     "Switch speed and the pulse generator's ability to produce a clean, repeatable pulse; very short pulses make β sensitive to edge shape and add noise."),
    ("How do you check β in simulation?",
     "DC/transient test: apply a known differential sample, measure average output current into a voltage source at $V_{cont}$, divide by $2A\\sin\\Delta\\phi$ (testbench tb_sscp_dc/pulse in Phase 8)."),
    ("Can you reduce β by lowering g_m instead?",
     "Yes, but a small $g_m$ means more noise per unit signal ($v_n^2 \\propto 1/g_m$) and more offset; pulsing keeps $g_m$ healthy."),
], 50)

# ------------------------------------------------------------------------------------------------ step 51
b.step(51, "Loop dynamics with the hold: ZOH sinc, T/2 delay, charge-sharing pole, phase-margin cost", "Bode plots")
b.md(r"""
### What happens
The SSPD is a two-switch sampler (Nagam: sw1 onto $C_1$ at the REF edge, then sw2 shares onto $C_2$, which holds for the NCB and the
Gm). The held voltage changes once per period. Three effects add phase lag to the loop:

1. **Zero-order hold:** $\frac{1-e^{-sT}}{sT}$, magnitude $\text{sinc}(fT)$, phase $-\pi fT$ (delay $T/2$).
2. **Charge sharing** between the sampling and hold capacitors (call them $C_s$ and $C_h$ here to avoid confusion with the loop
   filter): $v_h[k] = \frac{C_s v_s[k] + C_h v_h[k-1]}{C_s+C_h}$, a first-order discrete low-pass with $\alpha = \frac{C_h}{C_s+C_h}$:
   $$H_{cs}(z) = \frac{1-\alpha}{1-\alpha z^{-1}}\quad(\alpha = 0.5\text{ for equal caps}).$$
3. **Pulse position** of the Gm (step 50).

### Why it matters
At $f_c = f_{REF}/20$ the hold delay alone costs 9°; charge sharing with equal caps adds more. The loop filter must be designed with
this extra lag (PM target at the zero/pole placement must include it), and the same lag limits the FFNC bandwidth (Phase 6).
""")
b.code(r"""
fref = 50e6; T = 1/fref; f = np.logspace(5, np.log10(fref/2), 400); z = np.exp(2j*np.pi*f*T)
def frame(alpha):
    zoh = np.sinc(f*T)*np.exp(-1j*np.pi*f*T)
    cs = (1-alpha)/(1-alpha/z)
    tot = zoh*cs
    pm_cost = -np.degrees(np.angle(tot[np.argmin(abs(f-2.5e6))]))
    return ([dict(x=f, y=20*np.log10(abs(tot)), name="|hold x charge sharing| (dB)", row=1, col=1),
             dict(x=f, y=np.degrees(np.angle(zoh)), name="ZOH phase", line=dict(dash="dot"), row=1, col=2),
             dict(x=f, y=np.degrees(np.unwrap(np.angle(tot))), name="total phase", row=1, col=2)],
            f"alpha = C_h/(C_s+C_h) = {alpha}: phase lag at 2.5 MHz = {pm_cost:.1f} deg (hold alone 9.0 deg)")
fig = sweep([0.0, 0.25, 0.5, 0.75], frame, "alpha", active=2, rows=1, cols=2, subplot_titles=("magnitude", "phase (deg)"), height=420,
            layout=lambda f: f.update_xaxes(type="log", title_text="Hz"))
show(fig)
""")
b.qa([
    ("What is the transfer function of a zero-order hold and its delay?",
     "$(1-e^{-sT})/(sT)$; magnitude sinc(fT), linear phase $-\\pi fT$ = a T/2 delay."),
    ("Phase-margin cost of the hold at f_c = f_REF/20?",
     "$180°\\times(1/20) = 9°$."),
    ("Why does Nagam use two switches (sw1/C1, sw2/C2)?",
     "To hold the sample on a separate node (C2) before the next REF edge so the NCB and Gm see a stable voltage, isolated from the next tracking phase; it needs non-overlapping control."),
    ("Derive the charge-sharing transfer function.",
     "$v_h[k](C_s+C_h) = C_sv_s[k] + C_hv_h[k-1]$ → $H(z) = (1-\\alpha)/(1-\\alpha z^{-1})$, $\\alpha = C_h/(C_s+C_h)$."),
    ("What is the DC gain of the charge-sharing stage?",
     "1: in steady state $v_h = v_s$ — the sharing only delays (low-pass), it does not attenuate DC."),
    ("How do you reduce the hold-induced phase lag?",
     "Smaller hold cap relative to sampling cap (α → 0), pulse the Gm early, or a buffer instead of charge sharing (costs noise/power)."),
    ("Does the sinc magnitude matter for the loop?",
     "Little at $f_c \\ll f_{REF}$ (sinc ≈ 1); it matters for FFNC, which works up to ~$f_{REF}/8$."),
    ("Why is an SSPLL bandwidth chosen ≈ f_REF/20 rather than f_REF/10?",
     "The hold and charge-sharing lag plus spur considerations; Nagam's analysis uses $\\omega_{REF}/20$."),
], 51)

# ------------------------------------------------------------------------------------------------ step 52
b.step(52, "Acquisition: periodic SSPD characteristic, false lock to N ± k, dead-zone FLL, hand-over", "sequence and simulation")
b.md(r"""
### What happens
The SSPD output depends on the VCO phase **mod 2π at each reference edge**. Any $f_{VCO} = kf_{REF}$ gives a stable DC sample, so
the SSPD loop happily locks to $k = 31$ or $33$ (**false lock**), and its capture range is only about the loop bandwidth.

### How the dead-zone FLL fixes it
A divider (÷32), a PFD and a small charge pump compare REF with $f_{VCO}/32$. Far from lock the PFD saturates and pulls the frequency
toward $32f_{REF}$ (frequency detection). Near lock the divided phase error is inside a **dead zone** (here ±0.65π of the reference
period ≫ one VCO period $2\pi/32$), the FLL charge pump stays **off**, and the low-noise SSPD loop alone sets the phase — the
**hand-over**. Because the dead zone is wider than one VCO cycle in divider terms, there is always an SSPD lock point inside it.

### The simulation below
Cycle-by-cycle model: SSPD sampling the real phase (wrapped), pulsed Gm, third-order filter, VCO with free-running offset, and the FLL
with a PFD that slips cycles (keeping its sign) and a dead zone. Move the initial offset and compare with and without the FLL.
""")
b.code(SIM + r'''
offs = [0.3, 0.7, 1.3, 2.4, 3.6]
def frame(off):
    r0, _ = sspll_sim(off, use_fll=False, ncyc=5000); r1, d = sspll_sim(off, use_fll=True, ncyc=5000)
    k0, k1 = np.round(r0['f'][-1]), np.round(r1['f'][-1])
    return ([dict(x=r0['t']*1e6, y=r0['f'], name="SSPD loop only"),
             dict(x=r1['t']*1e6, y=r1['f'], name="SSPD + dead-zone FLL"),
             dict(x=[0, r1['t'][-1]*1e6], y=[32, 32], name="target 32 f_REF", line=dict(dash="dot", color="grey"))],
            f"start {32+off:.1f} x f_REF: SSPD alone locks at {k0:.0f} x f_REF" + (" (FALSE LOCK)" if k0 != 32 else "") +
            f"; with FLL at {k1:.0f} x f_REF")
fig = sweep(offs, frame, "initial VCO offset (multiples of f_REF)", active=2,
            layout=lambda f: f.update_xaxes(title="time (us)").update_yaxes(title="VCO frequency / f_REF"))
show(fig, 440)
''')
b.qa([
    ("Why can an SSPLL lock to the wrong frequency?",
     "The SSPD sees only the VCO phase at each reference edge; $f_{VCO} = kf_{REF}$ for any integer k produces constant samples."),
    ("What is the capture range of an SSPD loop?",
     "About the loop bandwidth (and at most ±$f_{REF}/2$ around the target harmonic): outside it the beat averages out."),
    ("How does a dead-zone FLL work?",
     "PFD + divider + CP pull the frequency to $Nf_{REF}$; when the divided phase error is inside the dead zone the CP is off and the SSPD loop takes over."),
    ("How wide must the dead zone be?",
     "Wider than half a VCO period referred to the divider ($\\pi/N$ reference radians) so an SSPD lock point exists inside it, plus margin for transients; but small enough to catch a slip to a neighbouring harmonic."),
    ("Why not keep the PFD loop on permanently?",
     "It would add its N²-multiplied noise and CP spurs, defeating the SSPLL's purpose."),
    ("What happens if the FLL dead zone is too narrow?",
     "The FLL and SSPD fight: the FLL keeps correcting while the SSPD holds a lock point outside the dead zone → jitter and spurs, possibly no stable lock."),
    ("What is hand-over?",
     "The transition from FLL-dominated frequency acquisition to SSPD-only phase lock; designed so it happens automatically by the dead zone."),
    ("Alternatives to a dead-zone FLL?",
     "Coarse digital frequency calibration with a counter, Hsu's PFD with an auxiliary SSPD, a sub-sampling-assisted PFD, or Geng's quadrature SSPD (frequency detection from I/Q samples)."),
    ("How do you test false-lock immunity in simulation?",
     "Start the VCO at several offsets (including ±1 and ±2 harmonics) and over PVT; check the final frequency is always $Nf_{REF}$ (testbench tb_top_lock, Phase 8)."),
    ("What is the `fll_active` test output in the proposal for?",
     "To observe when the FLL is acting (outside its dead zone): it should be active during acquisition and quiet in lock."),
], 52)

sys.path.insert(0, os.path.dirname(__file__))
import phase4b
phase4b.build(b, SIM)
b.save(os.path.join(os.path.dirname(__file__), "..", "phase4_sspll.ipynb"))
