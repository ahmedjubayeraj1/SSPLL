"""Phase 6 - Feedforward noise cancellation (roadmap steps 65-71)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nb import Book

b = Book("Phase 6 — Feedforward noise cancellation (steps 65–71)",
         "The SSPD already measures each edge's timing error. Feedforward noise cancellation (FFNC) feeds that measurement to "
         "the delay line of Phase 5 and moves each output edge back by the same amount — with no stability limit, because "
         "there is no feedback (Nagam & Kinget, JSSC 2018; limits analysed by Thijssen, Klumperink, Quinlan, Nauta, TCAS-II "
         "2018). This phase derives the cancellation in the time and frequency domains, finds its bandwidth, its noise "
         "transfer functions, the aliasing limit, and the calibration used by our `ncb_code`.")

PM = r'''
import sys; sys.path.insert(0, "../models")
import pllmodel as pm
d = pm.TYP; fref, f0 = d["fref"], d.f0
f = pm.freq_axis(n=700)
'''

# ------------------------------------------------------------------------------------------------ step 65
b.step(65, "Feedforward vs feedback: measure the error and subtract it", "why there is no stability limit")
b.md(r"""
### What happens
A **feedback** loop corrects an error by acting on its cause and waiting for the result to come back: it must be slow enough to stay
stable, so it only helps below its bandwidth. **Feedforward** measures the error and subtracts it downstream; nothing comes back,
so there is no loop to destabilise.

### How in our PLL
$$\phi_{out2} = \phi_{out1} - G_{can}\,\phi_{e},\qquad \phi_e \approx \phi_{out1} - N\phi_{REF}\ (\text{what the SSPD measures}).$$
If the cancellation path gain $G_{can} = G_{SSPD}\cdot G_{NCB} = 1$, the VCO's own phase deviation is removed from $\phi_{out2}$.

### Why it is attractive, and what it costs
- **No stability limit**: the useful band is set by the *detector and delay path*, up to about $f_{REF}/7.8$ (Nagam) — far beyond the
  $f_{REF}/20$ loop bandwidth.
- **No error correction of its own**: the gain must be *right* (calibration), the path must be *fast* (phase lag), and anything the
  path adds (NCB noise, aliased noise) goes straight to the output.
""")
b.code(PM + r'''
H = pm.loop_H(f, d["fc"], 50)
def frame(gerr_pct):
    Gc = pm.ffnc_Gc(f, fref, gerr_pct/100)
    return ([dict(x=f, y=20*np.log10(abs(1-H)), name="feedback alone: |1 - H|"),
             dict(x=f, y=20*np.log10(abs(1-Gc)), name="feedforward alone: |1 - G_can|"),
             dict(x=f, y=20*np.log10(abs((1-Gc)*(1-H))), name="both: |(1 - G_can)(1 - H)|", line=dict(width=3))],
            f"VCO-noise suppression; FFNC gain error {gerr_pct}%: floor {20*np.log10(max(gerr_pct, 0.01)/100):.0f} dB at low offsets")
fig = sweep([0, 5, 10, 20, 30, 50], frame, "gain error (%)", active=2,
            layout=lambda f_: f_.update_xaxes(type="log", title="offset (Hz)").update_yaxes(title="dB", range=[-80, 10]))
show(fig, 440)
''')
b.qa([
    ("Explain feedforward vs feedback cancellation.",
     "Feedback measures the output and corrects the cause, limited by loop stability; feedforward measures the error and subtracts it downstream, no loop, so no stability limit but no automatic correction of its own gain error."),
    ("Why is there no stability limit in FFNC?",
     "The NCB output does not feed back into the SSPD or the VCO; there is no closed loop whose phase margin could vanish."),
    ("What limits the bandwidth of FFNC then?",
     "Phase lag in the cancellation path (hold delay, charge sharing, amplifier and NCB poles): once the correction lags by more than 60°, it adds noise instead of removing it."),
    ("What does FFNC require that feedback does not?",
     "An accurate gain ($G_{can} = 1$) maintained over PVT (calibration), and a low-noise path, because its noise is not suppressed."),
    ("Where else is feedforward cancellation used?",
     "Noise-cancelling LNAs (Bruccoleri/Razavi examples), feedforward amplifier linearisation, digital PLL DTC-based quantisation-noise cancellation."),
    ("What are out1 and out2 in Nagam's paper?",
     "out1: the PLL output before cancellation (VCO); out2: after the NCB (cancelled). Comparing them on one die shows the benefit."),
    ("Why does FFNC need an SSPD and not a PFD?",
     "It needs a continuous, linear measurement of each edge's timing error as a voltage, available every reference period; the SSPD hold node provides exactly this."),
    ("What did Nagam & Kinget measure?",
     "2–2.8 GHz ring PLL in 65 nm: jitter 891 fs → 633 fs (≈29% reduction) with FFNC, 5.86 mW, 0.022 mm², FoM −236.3 dB."),
], 65)

# ------------------------------------------------------------------------------------------------ step 66
b.step(66, "Time domain: ΔT_eff = (G_t·K_t − 1)·ΔT_VCO, so cancellation needs G_t = 1/K_t", "derivation and waveform sketch")
b.md(r"""
### What happens
At each reference edge the SSPD samples the VCO; the held voltage $v = K_t\,\Delta T_{VCO}$ ($K_t$ in V/s). The NCB delays the VCO edges
by $G_t v$ ($G_t$ in s/V), *opposite* to the measured error. The output edge error becomes
$$\Delta T_{out} = \Delta T_{VCO} - G_tK_t\,\Delta T_{VCO} = (1 - G_tK_t)\,\Delta T_{VCO}\quad(+\text{a constant } T_0)$$
so **$G_t = 1/K_t$ cancels the error completely** — at the sampling instant.

### Why the cancellation is not perfect between samples
The sample is held for a whole reference period (32 VCO edges). The VCO keeps wandering after the sample, so edges late in the period
are corrected with stale information. The simulation below uses a VCO timing error with the spectrum of a ring inside a 2.5 MHz loop,
samples it every $T_{REF}$, holds it, and subtracts $G_tK_t$ times the held value from every VCO edge.
""")
b.code(r'''
rng = np.random.default_rng(1)
fref, N = 50e6, 32; T0 = 1/(N*fref); nref = 400; n = nref*N
w = rng.standard_normal(n)*0.06e-12
x = np.zeros(n)                                   # VCO edge timing error: random walk, pulled back by the loop (2.5 MHz)
a = np.exp(-2*np.pi*2.5e6*T0)
for k in range(1, n): x[k] = a*x[k-1] + w[k]
held = np.repeat(x[::N], N)[:n]                    # SSPD sample at each REF edge, held for N VCO edges
t = np.arange(n)*T0
def frame(g):
    y = x - g*held
    show_n = 6*N
    return ([dict(x=t[:show_n]*1e9, y=x[:show_n]*1e12, name="VCO edge error (ps)"),
             dict(x=t[:show_n]*1e9, y=held[:show_n]*1e12, name="held SSPD sample (as timing)", line=dict(shape="hv", dash="dot")),
             dict(x=t[:show_n]*1e9, y=y[:show_n]*1e12, name="after cancellation (ps)")],
            f"G_t K_t = {g}: rms edge error {np.std(x)*1e12:.2f} ps -> {np.std(y)*1e12:.2f} ps (over {nref} reference periods)")
fig = sweep([0.0, 0.5, 0.8, 0.9, 1.0, 1.2, 1.5], frame, "G_t x K_t", active=4,
            layout=lambda f_: f_.update_xaxes(title="time (ns)").update_yaxes(title="ps"))
show(fig, 440)
''')
b.qa([
    ("Derive the time-domain cancellation condition.",
     "Sample $v = K_t\\Delta T$; NCB delay $-G_tv$; output error $(1-G_tK_t)\\Delta T$; zero for $G_t = 1/K_t$."),
    ("Why is cancellation imperfect even with G_t = 1/K_t?",
     "The correction is updated once per reference period and held; the VCO wanders between samples, so edges far from the sample are corrected with outdated information (the hold's sinc/delay)."),
    ("What happens with G_t·K_t = 2?",
     "The error is inverted and as large as before: no improvement ($|1-2| = 1$). Above 2 it gets worse."),
    ("What is T_0 in the time-domain equation?",
     "The constant (nominal) delay of the NCB at zero sample — a fixed phase shift between out1 and out2, harmless."),
    ("Why does FFNC help most for slowly wandering errors?",
     "A slow error changes little within a reference period, so the held sample is still accurate for all 32 edges; fast errors (near $f_{REF}$) change within the period."),
    ("What is the relationship between K_t and K_phi?",
     "$K_\\phi = K_t/(2\\pi f_{out})$ (V/rad); $G_\\phi = 2\\pi f_{out}G_t$ (rad/V); the product is the same."),
    ("Does FFNC change the PLL's loop dynamics?",
     "No; the NCB is outside the loop (after the VCO tap used by the SSPD). The loop sees the VCO, not out2."),
    ("In which sign must the NCB act?",
     "Opposite to the measured error: if the VCO edge is late (positive sample), out2's edge must be advanced (less delay)."),
], 66)

# ------------------------------------------------------------------------------------------------ step 67
b.step(67, "Frequency domain: phasor cancellation, the 60° rule, the gain-error floor", "plots")
b.md(r"""
### What happens
At one offset frequency the noise is a phasor $n$; the cancellation adds $e = -G\,n\,e^{j\theta}$ (gain $G$, phase error $\theta$). The residue
$$\frac{|r|}{|n|} = \left|1 - G e^{j\theta}\right| = \sqrt{(1 - G\cos\theta)^2 + (G\sin\theta)^2}.$$

### How the two limits come out
- **Gain only** ($\theta = 0$): residue $|1-G|$ → the **gain-error floor** $20\log|1-G|$ (10% error → −20 dB, 30% → −10.5 dB).
- **Phase only** ($G = 1$): residue $\sqrt{2-2\cos\theta} = 2\sin(\theta/2)$, which is < 1 only for $|\theta| < 60°$ (Nagam's criterion).
  Beyond 60° the "cancellation" adds noise (up to +6 dB at 180°).

### Why it matters
The cancellation bandwidth is where the path's phase reaches −60° (step 68); inside it, the depth is set by gain accuracy (calibration).
Nagam targets >10 dB cancellation, i.e. better than 30% gain precision.
""")
b.code(r'''
th = np.linspace(0, 180, 361)
def frame(G):
    r = 20*np.log10(abs(1 - G*np.exp(1j*np.radians(th))) + 1e-12)
    i60 = np.argmin(abs(r))
    return ([dict(x=th, y=r, name=f"residue |1 - G e^(j theta)|, G = {G}"),
             dict(x=[0, 180], y=[0, 0], name="no cancellation (0 dB)", line=dict(dash="dot"))],
            f"G = {G}: floor at theta = 0 is " + ("-inf (perfect)" if G == 1.0 else f"{20*np.log10(abs(1-G)):.1f} dB") + "; benefit vanishes at theta = {th[np.where(r > 0)[0][0]] if (r > 0).any() else 180:.0f} deg")
fig = sweep([0.5, 0.7, 0.9, 1.0, 1.1, 1.3, 1.5], frame, "path gain G", active=3,
            layout=lambda f_: f_.update_xaxes(title="phase error of the cancellation path (deg)").update_yaxes(title="residue (dB)", range=[-45, 8]))
show(fig, 420)
''')
b.qa([
    ("Derive the residue of phasor cancellation.",
     "$r = n - Gne^{j\\theta}$ → $|r|/|n| = |1 - Ge^{j\\theta}| = \\sqrt{1 - 2G\\cos\\theta + G^2}$."),
    ("Prove the 60° rule.",
     "For G = 1: $|r|/|n| = \\sqrt{2-2\\cos\\theta} = 2\\sin(\\theta/2) < 1 \\iff |\\theta| < 60°$."),
    ("What cancellation depth does a 10% gain error allow?",
     "$20\\log(0.1) = -20$ dB at low offsets (where θ ≈ 0)."),
    ("Nagam's precision requirement for >10 dB cancellation?",
     "Better than ~30% gain precision ($20\\log 0.3 = -10.5$ dB)."),
    ("Is over-gain or under-gain worse?",
     "Symmetric in magnitude at θ = 0 ($|1-G|$), but with phase lag a slightly lower gain reduces the residue near the band edge (the model's optimum was ~10–15% under-gain)."),
    ("What happens beyond the 60° frequency?",
     "The correction adds noise: up to 2× (6 dB) at 180°. The sinc of the hold reduces G there, limiting the penalty (Nagam saw about +2 dB up to $\\omega_{REF}$)."),
    ("Why is it called a phasor argument and is it rigorous for noise?",
     "Each spectral component of stationary noise is processed by the linear path; the residue PSD is $|1-G_{can}(j\\omega)|^2$ times the noise PSD — the phasor picture applied per frequency."),
    ("How do gain and phase errors combine?",
     "$|1-Ge^{j\\theta}|^2 = (1-G)^2 + 4G\\sin^2(\\theta/2)$: a gain term plus a phase term."),
], 67)

# ------------------------------------------------------------------------------------------------ step 68
b.step(68, "The cancellation path G_can and its bandwidth (ω_REF/7.8)", "Bode plots")
b.md(r"""
### What happens
$G_{can}(j\omega) = G_{SSPD}(j\omega)\cdot G_{\phi,NCB}$. The SSPD transfer includes the hold (sinc, half-period delay) and the charge
sharing between the sampling and hold capacitors; the amplifier and the NCB add their own poles.

### How much bandwidth
- First principles (ZOH × charge sharing, equal caps, α = 0.5): the phase reaches −60° at **$f_{REF}/6$**; with no charge sharing
  (α = 0): $f_{REF}/3$.
- Nagam & Kinget's empirical $G_{SSPD}$ (fitted to their circuit, including the extra lag) reaches −60° at **$\omega_{REF}/7.8$** — that is the
  model in `models/pllmodel` and in our proposal budget: 50 MHz/7.8 ≈ **6.4 MHz** of cancellation bandwidth, versus a 2.5 MHz loop.

### Why it matters
Ring-oscillator noise dominates between the loop bandwidth and a few MHz (Nagam: 25 kHz–5 MHz carries ~75% of the jitter): a
cancellation bandwidth of ~$f_{REF}/8$ covers it. Any extra pole (slow amplifier, slow NCB) shrinks this band.
""")
b.code(PM + r'''
T = 1/fref; ff = np.logspace(5, np.log10(fref/2), 500); z = np.exp(2j*np.pi*ff*T)
def frame(alpha):
    g1 = np.sinc(ff*T)*np.exp(-1j*np.pi*ff*T)*(1-alpha)/(1-alpha/z)            # first-principles path
    g2 = pm.ffnc_Gc(ff, fref, 0.0)                                              # Nagam's empirical path (model)
    p1, p2 = np.degrees(np.unwrap(np.angle(g1))), np.degrees(np.unwrap(np.angle(g2)))
    f1 = ff[np.where(p1 < -60)[0][0]]; f2 = ff[np.where(p2 < -60)[0][0]]
    return ([dict(x=ff, y=p1, name="phase: ZOH x charge sharing", row=1, col=1),
             dict(x=ff, y=p2, name="phase: Nagam empirical (model)", row=1, col=1),
             dict(x=[ff[0], ff[-1]], y=[-60, -60], name="-60 deg", line=dict(dash="dot"), row=1, col=1),
             dict(x=ff, y=20*np.log10(abs(1-g1)), name="residue |1 - G_can|, first principles", row=1, col=2),
             dict(x=ff, y=20*np.log10(abs(1-g2)), name="residue, empirical", row=1, col=2)],
            f"alpha = {alpha}: -60 deg at f_REF/{fref/f1:.1f} (first principles) and f_REF/{fref/f2:.1f} (Nagam's fit)")
fig = sweep([0.0, 0.25, 0.5, 0.75], frame, "charge-sharing alpha = C_h/(C_s+C_h)", active=2, rows=1, cols=2,
            subplot_titles=("phase of G_can (deg)", "residue (dB)"), height=430,
            layout=lambda f_: f_.update_xaxes(type="log", title_text="offset (Hz)").update_yaxes(range=[-200, 0], row=1, col=1))
show(fig)
''')
b.qa([
    ("What is G_can?",
     "The transfer from the VCO phase (as sampled) to the phase correction at out2: $G_{SSPD}(j\\omega)\\cdot G_{\\phi,NCB}$; ideally 1."),
    ("How is the FFNC bandwidth defined?",
     "The offset where the phase of $G_{can}$ reaches −60°, beyond which cancellation stops helping."),
    ("What is the FFNC bandwidth for our 50 MHz reference?",
     "About $f_{REF}/7.8$ ≈ 6.4 MHz (Nagam's model), vs a 2.5 MHz loop bandwidth."),
    ("Why does charge sharing between C_s and C_h reduce the bandwidth?",
     "It forms a discrete low-pass (pole) adding phase lag on top of the hold's half-period delay."),
    ("How could you widen the cancellation bandwidth?",
     "Higher f_REF, a pulser/early update instead of a full hold, a smaller hold capacitor (smaller α), faster amplifier/NCB, or dual-edge sampling (twice per period)."),
    ("Does the loop-filter capacitor ratio matter for FFNC?",
     "Indirectly: it sets the loop bandwidth and how much VCO noise remains for FFNC; Nagam's analysis also notes the effect of the SSPD's own capacitor ratio on $G_{SSPD}$."),
    ("Why is a −60° bandwidth of f_REF/8 enough for a ring PLL?",
     "Most ring-induced jitter lies between the loop bandwidth and a few MHz; above ~f_REF/8 the ring noise is already falling at 20 dB/dec and contributes less."),
    ("What does dual-edge FFNC mean (future scope)?",
     "Sampling on both reference edges doubles the update rate, halving the hold delay and roughly doubling the cancellation bandwidth."),
], 68)

# ------------------------------------------------------------------------------------------------ step 69
b.step(69, "Noise transfer functions after cancellation", "VCO, loop-filter R and supply noise are cancelled; REF, SSPD, NCB and aliases are not")
b.md(r"""
### Transfer functions (Nagam & Kinget, with LG the loop gain and out1/out2 before/after cancellation)
| Source | to out1 | to out2 |
|---|---|---|
| VCO | $\frac{1}{1+LG}$ | $\frac{1}{1+LG}(1-G_{can})$ — **cancelled** |
| loop-filter R (at VCO input) | $\frac{K_{VCO}/j\omega}{1+LG}$ | $\times(1-G_{can})$ — **cancelled** |
| VCO supply | $\frac{K_{VCO,vdd}/j\omega}{1+LG}$ | $\times(1-G_{can})$ — **cancelled** (PSNA) |
| SSPD | $\frac{LG}{1+LG}$ | $\frac{LG}{1+LG}+\frac{G_{can}}{1+LG}$ — **not cancelled** (slightly more at high offsets) |
| REF | $N\times$ SSPD's | $N\times$ SSPD's — **not cancelled**, sets the floor |
| NCB | 0 | 1 — **added** |

### Why
Everything that disturbs the VCO *after* the reference comparison looks like VCO phase error and is measured by the SSPD, so it is
cancelled. What enters *through* the SSPD (its own noise, the reference) is indistinguishable from a true error and is passed on.
The NCB comes after the measurement, so it is never seen.
""")
b.code(PM + r'''
H = pm.loop_H(f, d["fc"], 50); LG = H/(1-H)
def frame(ge):
    Gc = pm.ffnc_Gc(f, fref, ge/100)
    return ([dict(x=f, y=20*np.log10(abs(1/(1+LG))), name="VCO -> out1", line=dict(dash="dot")),
             dict(x=f, y=20*np.log10(abs((1-Gc)/(1+LG))), name="VCO / LF-R / supply -> out2"),
             dict(x=f, y=20*np.log10(abs(LG/(1+LG))), name="SSPD -> out1", line=dict(dash="dot")),
             dict(x=f, y=20*np.log10(abs(LG/(1+LG) + Gc/(1+LG))), name="SSPD -> out2 (REF: +30.1 dB)"),
             dict(x=f, y=np.zeros_like(f), name="NCB -> out2", line=dict(dash="dash"))],
            f"noise transfer functions with {ge}% NCB gain error (f_c 2.5 MHz, G_can from Nagam's model)")
fig = sweep([0, 10, 30], frame, "gain error (%)", active=1,
            layout=lambda f_: f_.update_xaxes(type="log", title="offset (Hz)").update_yaxes(title="dB", range=[-60, 10]))
show(fig, 440)
''')
b.qa([
    ("Which noise sources does FFNC cancel?",
     "Anything that perturbs the VCO phase after the comparison point: VCO intrinsic noise, loop-filter resistor noise, VCO supply noise (and charge-pump noise appearing at the VCO input)."),
    ("Which noise sources does FFNC not cancel?",
     "Reference (×N²), SSPD (sampler) noise, NCB noise, and aliased noise from above $f_{REF}/2$."),
    ("Why is SSPD noise slightly increased at out2?",
     "It also reaches out2 directly through the feedforward path: extra term $G_{can}/(1+LG)$, significant above the loop bandwidth."),
    ("What sets the noise floor after cancellation?",
     "The reference (crystal + buffer) ×N²; Nagam notes the REF noise ultimately limits the attenuation."),
    ("Why does FFNC improve supply-noise rejection?",
     "Supply-induced VCO phase modulation is measured by the SSPD like any VCO error and subtracted: Nagam reports power-supply noise attenuation (PSNA) with a 1 mVpp tone."),
    ("Why must the NCB's own noise be small?",
     "Its transfer to out2 is 1 at all frequencies; the proposal budgets its floor at −150 dBc/Hz."),
    ("What is TF_vco,2 at very low offsets with 10% gain error?",
     "$|1-G_{can}|\\cdot|1/(1+LG)|$ ≈ 0.1 × (already small) — an extra −20 dB on top of the loop's suppression."),
    ("Above which offset does FFNC slightly worsen VCO noise?",
     "Above the −60° frequency (~f_REF/7.8), where $|1-G_{can}| > 1$ (Nagam: about +2 dB up to $\\omega_{REF}$)."),
], 69)

# ------------------------------------------------------------------------------------------------ step 70
b.step(70, "Aliasing (Thijssen), why a narrower loop can help with FFNC, and the 5× smaller filter capacitor", "analysis")
b.md(r"""
### Aliasing — what happens
The SSPD samples at $f_{REF}$, so VCO noise at offsets around $kf_{REF}$ folds onto the low-frequency band (Thijssen et al.):
$$S_s(f) = f_{REF}\sum_k S_{\phi,in}(f - kf_{REF})\quad(\text{detected spectrum, their eq. 10}).$$
The cancellation path cannot tell aliased noise from true low-frequency error, so it **injects** the aliased VCO noise into out2. The
model below adds the $k = \pm1,\pm2,\pm3$ aliases of the closed-loop VCO noise, filtered by $|G_{can}|^2$.

### Why a narrower loop can help
Without FFNC the loop must be wide to suppress the ring. With FFNC the ring noise is cancelled up to ~$f_{REF}/8$ anyway, so a narrower loop
loses little — and gains less in-band noise peaking, less hold-delay phase lag, smaller spurs.

### The 5× smaller loop-filter capacitor (Nagam & Kinget)
$C_1 = 1/(\omega_zR_1)$: a larger $R_1$ allows a smaller $C_1$ for the same zero, but $R_1$'s noise (referred to the VCO input) grows. FFNC
cancels that noise. Nagam: $R_1$ from 4 kΩ to 20 kΩ and $C_1$ from 50 pF to 10 pF; noise +7 dB at out1, but back to −124 dBc/Hz at out2
(vs −125 before). Area is the price that FFNC buys back.
""")
b.code(PM + r'''
H = pm.loop_H(f, d["fc"], 50); Gc = pm.ffnc_Gc(f, fref, d["gerr"])
lin = lambda L: 2*10**(L/10)
Svco = lambda ff: lin(pm.vco_L(np.maximum(ff, 1e3), d["vco1M"], d["fc3"]))*abs(1 - pm.loop_H(np.maximum(ff, 1e3), d["fc"], 50))**2
base = Svco(f)
def frame(kmax):
    alias = sum(Svco(abs(f - k*fref)) + Svco(abs(f + k*fref)) for k in range(1, kmax+1)) if kmax else 0*f
    out2 = base*abs(1-Gc)**2 + alias*abs(Gc)**2
    m = (f >= 1e4) & (f <= 40e6)
    j1 = np.sqrt(np.trapezoid(base[m], f[m]))/(2*np.pi*f0); j2 = np.sqrt(np.trapezoid(out2[m], f[m]))/(2*np.pi*f0)
    return ([dict(x=f, y=10*np.log10(base/2), name="VCO at out1 (after the loop)"),
             dict(x=f, y=10*np.log10(out2/2), name=f"VCO at out2, aliases k <= {kmax}")],
            f"aliases up to k = {kmax}: VCO-only jitter {j1*1e12:.2f} ps -> {j2*1e12:.2f} ps after FFNC")
fig = sweep([0, 1, 2, 3], frame, "number of folded harmonics k", active=1,
            layout=lambda f_: f_.update_xaxes(type="log", title="offset (Hz)").update_yaxes(title="dBc/Hz", range=[-150, -95]))
show(fig, 430)
# loop-filter resistor noise, before and after cancellation (Nagam's argument, with our numbers)
Kv = 2*np.pi*300e6
def lf_noise(R, C1, C2):
    s = 2j*np.pi*f
    Hr = C1/((C1 + C2) + s*R*C1*C2)                   # R noise to V_cont through the filter
    Sphi = 4*kT*R*abs(Hr)**2*Kv**2/(2*np.pi*f)**2
    return 10*np.log10(Sphi*abs(1-H)**2/2), 10*np.log10(Sphi*abs((1-H)*(1-Gc))**2/2)
fig = go.Figure()
for scale, dash in ((1, None), (5, "dash")):
    R, C1, C2 = 18.05e3*scale, 13.16e-12/scale, 1.018e-12/scale
    a1, a2 = lf_noise(R, C1, C2)
    fig.add_trace(go.Scatter(x=f, y=a1, name=f"R1 x{scale} (C1 = {C1*1e12:.1f} pF): out1", line=dict(dash=dash)))
    fig.add_trace(go.Scatter(x=f, y=a2, name=f"R1 x{scale}: out2 (cancelled)", line=dict(dash=dash)))
fig.update_xaxes(type="log", title="offset (Hz)").update_yaxes(title="loop-filter R noise (dBc/Hz)", range=[-170, -110])
show(fig, 420)
''')
b.qa([
    ("What is aliasing in the context of FFNC?",
     "The SSPD samples at $f_{REF}$, so VCO noise near multiples of $f_{REF}$ folds into the low-frequency band the NCB corrects; the NCB then injects that folded noise into the output."),
    ("Give Thijssen's expression for the detected spectrum.",
     "$S_s(f) = f_{REF}\\sum_k S_{\\phi,in}(f - kf_{REF})$."),
    ("How do you reduce aliasing penalties?",
     "Higher f_REF, a loop that already suppresses VCO noise near multiples of f_REF (it can't — they are far above f_c), lower VCO noise at high offsets, or band-limiting the sampled signal (not possible in a pure sampler)."),
    ("Why can a narrower loop be acceptable with FFNC?",
     "FFNC cancels ring noise up to ~f_REF/8, so the loop no longer has to be wide; narrower loops reduce peaking, spurs and hold-induced phase-margin loss."),
    ("Explain the 5× smaller filter capacitor.",
     "For a fixed zero $1/(R_1C_1)$, raising $R_1$ 5× allows $C_1$ 5× smaller; the extra resistor noise (it appears at the VCO input) is cancelled by FFNC. Nagam: 4 kΩ/50 pF → 20 kΩ/10 pF with the same out2 noise."),
    ("What else must change when R1 increases with the same zero?",
     "The loop gain: $G_m$ (β) must be reduced to keep the same bandwidth (Nagam), and reference spurs from the CP pulse through a larger R1 must be checked."),
    ("Is the R-noise argument specific to SSPLLs?",
     "The cancellation needs FFNC (hence an SSPD); without FFNC the larger R1 noise would raise out1 noise by ~7 dB in Nagam's example."),
    ("How much does aliasing cost in our model?",
     "See the slider: a few percent of jitter for k = 1…3 with the proposal's ring noise; it grows if the ring is noisier at 50–150 MHz offsets."),
], 70)

# ------------------------------------------------------------------------------------------------ step 71
b.step(71, "Calibration: supply tone, residue detection, gain-code sweep", "why a low-frequency tone isolates gain error")
b.md(r"""
### What happens (Nagam & Kinget, our test plan step 6)
A small **test tone** at $F_{cal}$ = 50 kHz is applied to the VCO supply (our `VTEST` on ANA0 into the oscillator current feed). It creates
sidebands at $f_{out}\pm F_{cal}$. FFNC cancels them like any VCO disturbance; the **residual** tone at out2 is
$$|r(F_{cal})| \propto \left|1 - G_{can}(F_{cal})\right|\cdot\left|\frac{1}{1+LG(F_{cal})}\right|.$$
A second SSPD (calibration path) demodulates out2; the residue is correlated with the original tone; the decision logic steps
`ncb_code` to minimise it (in Nagam's chip off-chip; in ours `cal_out` gives the sign of the error).

### Why a low-frequency tone isolates the gain error
At 50 kHz the cancellation path has essentially **no phase lag** ($\theta\approx 0$; the −60° point is at 6.4 MHz), so the residue depends only
on $|1-G|$: minimising the tone sets $G = 1$, which is exactly the condition for best *noise* cancellation (both require
$G_{t,NCB} = 1/K_{t,SSPD}$). The loop attenuates the tone at 50 kHz too, but equally for every code, so the *minimum* is unaffected.

### The model below
The true SSPD gain spreads over PVT (slider); the 4-bit code spans 0.6–1.5× of nominal. Sweep the code, find the minimum residue,
and see the resulting jitter.

**Notice:** calibration lands on $G \approx 1$ and gives 1.44 ps, slightly *worse* than the budget's 1.40 ps, which assumed 10% gain error.
The model's noise optimum is a ~10% *under*-gain because of the path's phase lag near $f_{REF}/8$ (`models/template.ipynb`, section 5). A
deliberate calibration offset of about one code below the tone minimum would recover it — a small refinement for Phase 7.
""")
b.code(PM + r'''
codes = np.arange(16)
gain_of_code = 0.6 + 0.9*codes/15                  # NCB gain relative to nominal 1/K_t(nominal)
Fcal = 50e3
def frame(kt_rel):                                   # actual SSPD gain relative to nominal
    g = gain_of_code*kt_rel                          # loop-path product G_can at low frequency
    Gcal = np.array([pm.ffnc_Gc(np.array([Fcal]), fref, 1-gg)[0] for gg in g])
    Hc = pm.loop_H(np.array([Fcal]), d["fc"], 50)[0]
    resid = 20*np.log10(abs((1-Gcal)*(1-Hc)) + 1e-9)
    best = int(np.argmin(resid))
    jit = [pm.jitter(d.but(gerr=1-gg), "ffnc")[0]["TOTAL"]*1e12 for gg in g]
    return ([dict(x=codes, y=resid, mode="lines+markers", name="residual tone at out2 (dB rel. tone)", row=1, col=1),
             dict(x=codes, y=jit, mode="lines+markers", name="rms jitter with this code (ps)", row=1, col=2)],
            f"actual SSPD gain {kt_rel:.2f} x nominal: calibration picks code {best} (G = {g[best]:.2f}) -> jitter {jit[best]:.2f} ps "
            f"(FFNC off {pm.jitter(d, 'sspll')[0]['TOTAL']*1e12:.2f} ps)")
fig = sweep([0.7, 0.85, 1.0, 1.2, 1.4], frame, "actual SSPD gain / nominal", fmt="{:.2f}", active=2, rows=1, cols=2,
            subplot_titles=("calibration residue vs code", "jitter vs code"), height=430,
            layout=lambda f_: f_.update_xaxes(title_text="ncb_code"))
show(fig)
''')
b.qa([
    ("How is the FFNC gain calibrated?",
     "Inject a low-frequency supply tone, measure the residual tone at the cancelled output (demodulated by a calibration SSPD and correlated with the tone), and choose the NCB gain code that minimises it."),
    ("Why does minimising a supply tone also minimise noise?",
     "Both cancellations require the same condition, $G_{t,NCB} = 1/K_{t,SSPD}$ ($G_{can} = 1$)."),
    ("Why calibrate at 50 kHz and not at 5 MHz?",
     "At low offsets the cancellation path has negligible phase lag, so the residue measures pure gain error; at high offsets the phase error would bias the result."),
    ("What does correlation with the injected tone achieve?",
     "Synchronous detection: it extracts the residual tone's amplitude (and sign) from noise, so small residues can be measured."),
    ("Foreground vs background calibration?",
     "Foreground: run at start-up with an injected tone (Nagam, our design). Background: continuously, e.g. with a small pseudo-random signal; robust to drift but more complex (future scope)."),
    ("What resolution does the code need?",
     "Enough that the residual gain error after calibration is ≲10–15% (−16…−20 dB floor); 16 codes over 0.6–1.5× give ~6% steps."),
    ("What is cal_out in the proposal?",
     "A digital test output giving the sign of the calibration error, letting an external host (or later on-chip logic) step ncb_code."),
    ("How is the calibration done in our measurement plan?",
     "Inject a 50 kHz tone on ANA0 (VTEST), step ncb_code 0–15 and keep the code with the smallest tone sideband at CLK_OUT; then verify jitter reduction."),
    ("What if the SSPD gain drifts with temperature after calibration?",
     "The gain error grows and cancellation depth falls; recalibrate at temperature, or use background calibration; the proposal tests at temperature extremes."),
    ("Measured in Nagam's chip: how was the code found and how robust was it?",
     "A 0.3 mVpp 50 kHz tone on the VCO supply, sweeping the NCB code while monitoring the calibration residue; even 30% gain error still gave ~1.5× jitter reduction."),
], 71)

b.save(os.path.join(os.path.dirname(__file__), "..", "phase6_ffnc.ipynb"))
