"""Phase 3 part B: steps 40-45."""

SPUR_FN = r'''
def cp_spur(Ip, mism, t_on, Ileak, d, Kv, fref, nh=60, qinj=0.0):
    """Reference spur of a CP-PLL from UP/DN mismatch (fraction) and leakage (A).
    Builds one period of the charge-pump current at lock (net charge = 0), takes its Fourier series,
    passes it through the filter Z(jk w_ref) and converts the first-harmonic ripple to a spur:
    spur = 20 log(K_VCO |V1| / (2 w_ref)) (narrowband FM). Returns spur dBc, static offset (deg), t (s), v (V), i (A)."""
    T = 1/fref; Iu, Id = Ip*(1+mism/2), Ip*(1-mism/2)
    q = -(Iu - Id)*t_on + Ileak*T - qinj                    # net charge the extra pulse must supply
    ex_up = q/Iu if q > 0 else 0.0; ex_dn = -q/Id if q < 0 else 0.0
    pulses = [(0.0, t_on + ex_up, Iu), (0.0, t_on + ex_dn, -Id), (0.0, T, -Ileak),   # (start, end, current)
              (t_on + 0.3e-9, t_on + 0.32e-9, qinj/20e-12)]                          # switch charge injection at turn-off
    w0 = 2*np.pi*fref
    Z = lambda s: (1+s*d['R']*d['C1'])/(s*(d['C1']+d['C2'])*(1+s*d['R']*d['C1']*d['C2']/(d['C1']+d['C2'])))
    t = np.linspace(0, T, 4000, endpoint=False); v = np.zeros_like(t); V1 = 0
    for k in range(1, nh+1):                                 # exact Fourier coefficients of rectangular pulses
        ck = sum(I*(np.exp(-1j*k*w0*a) - np.exp(-1j*k*w0*b_))/(1j*k*w0) for a, b_, I in pulses)*2/T
        Vk = ck*Z(1j*k*w0)
        v += np.real(Vk*np.exp(1j*k*w0*t))
        if k == 1: V1 = abs(Vk)
    spur = 20*np.log10(max(Kv*V1/(2*w0), 1e-12))
    off = 360*(ex_up - ex_dn)/T
    td = np.linspace(0, 1e-9, 2001)                          # fine grid for drawing the current
    i = sum(I*((td >= a) & (td < b_)) for a, b_, I in pulses)
    t = (t, td)
    return spur, off, t, v, i
'''


def build(b):
    # -------------------------------------------------------------------------------------------- step 40
    b.step(40, "Limit: CP mismatch, leakage, charge sharing, clock feedthrough → ripple → reference spurs", "spur derivation")
    b.md(r"""
### What happens
At lock an ideal CP delivers no net charge and $V_{cont}$ is perfectly still. Real charge pumps disturb $V_{cont}$ once per reference
period, the VCO is frequency-modulated at $f_{REF}$ and **reference spurs** appear at $f_{out}\pm f_{REF}$.

### How (one mechanism at a time)
- **UP/DN mismatch** $\Delta I$ with reset pulses $t_{on}$: the net charge $\Delta I\,t_{on}$ must be cancelled, so the loop settles at a
  **static phase offset** $\Delta\phi = 2\pi\frac{\Delta I\,t_{on}}{I_pT_{REF}}$; each period a short positive and negative current
  pulse remain → ripple.
- **Leakage** $I_{leak}$ (CP off-current, MOS-cap or varactor leakage) discharges the filter between pulses; the loop answers with a
  pulse of charge $I_{leak}T_{REF}$ each period → offset $2\pi I_{leak}/I_p$ and a sawtooth ripple.
- **Charge sharing** (internal CP nodes at the rail when off, step 42), **charge injection and clock feedthrough** of the switches.

**Spur level** (narrowband FM, first harmonic $V_1$ of the ripple):
$$\text{spur} = 20\log_{10}\frac{K_{VCO}|V_1|}{2\omega_{REF}},\qquad V_1 = |c_1|\cdot|Z(j\omega_{REF})|,$$
with $c_1$ the first Fourier coefficient of the CP current. The code below does this calculation for the step-38 design.

**What the numbers show.** With ideal switches, mismatch and leakage alone give very low spurs for this filter (mismatch makes a
*doublet* — two opposite charges 150 ps apart — that almost cancels at 50 MHz). Charge injection and clock feedthrough of real
switches (tens of fC, not cancelled within the period) dominate: compare the printed injection results.

### Why it matters
The proposal limits the spur to −45 dBc (max). The filter attenuates $f_{REF}$ only by $|Z(j\omega_{REF})|$ — a wider loop (smaller
capacitors) means larger $|Z|$ and larger spurs.
""")
    b.code(SPUR_FN + r'''
Ip, Kv, N, fref = 100e-6, 2*np.pi*300e6, 32, 50e6
d = sl.loop_design_type2(2.5e6, 60, Ip, Kv, N)
def frame(m_pct):
    sp, off, (t, td), v, i = cp_spur(Ip, m_pct/100, 150e-12, 0.0, d, Kv, fref)
    return ([dict(x=td*1e9, y=i*1e6, name="CP current (uA), first 1 ns", row=1, col=1),
             dict(x=t*1e9, y=(v - v.mean())*1e6, name="V_cont ripple (uV), whole period", row=2, col=1)],
            f"UP/DN mismatch {m_pct}% with 150 ps reset pulses: static offset {off:.3f} deg, reference spur {sp:.1f} dBc")
fig = sweep([0.5, 1, 2, 5, 10, 20], frame, "current mismatch (%)", active=2, rows=2, cols=1, shared_xaxes=True,
            subplot_titles=("charge-pump current (first 1 ns of the period)", "ripple on V_cont over one period"), height=560, maxpts=2001,
            layout=lambda f: f.update_xaxes(title_text="time within the period (ns)", row=2, col=1))
show(fig)
Il = np.logspace(-12, -7, 40)
sp = [cp_spur(Ip, 0.0, 150e-12, x, d, Kv, fref)[0] for x in Il]
fig = go.Figure(go.Scatter(x=Il, y=sp, name="spur vs leakage"))
fig.update_xaxes(type="log", title="leakage current (A)").update_yaxes(title="reference spur (dBc)")
show(fig, 360)
for q in (1e-15, 3e-15, 10e-15):
    print(f"charge injection {q*1e15:.0f} fC per period (switch turn-off, 0.3 ns after the pulse): spur {cp_spur(Ip, 0.0, 150e-12, 0.0, d, Kv, fref, qinj=q)[0]:.1f} dBc")
''')
    b.qa([
        ("Why does CP mismatch cause a static phase offset?",
         "With reset pulses both sources are on each cycle; the mismatch leaves net charge $\\Delta I t_{on}$, so the loop shifts the edges until the longer pulse of one source supplies the opposite charge: $\\Delta\\phi = 2\\pi\\Delta I t_{on}/(I_pT)$."),
        ("Why does mismatch cause spurs even though the average current is zero?",
         "The charge is delivered as a short positive and negative pulse at slightly different times; the waveform repeats every period and has energy at $f_{REF}$ and harmonics."),
        ("Derive the leakage-induced phase offset.",
         "Charge balance: $I_p\\frac{\\Delta\\phi}{2\\pi}T = I_{leak}T$ → $\\Delta\\phi = 2\\pi I_{leak}/I_p$."),
        ("How do you estimate the spur from a ripple voltage?",
         "First-harmonic amplitude $V_1$ of $V_{cont}$; phase modulation index $\\beta = K_{VCO}V_1/\\omega_{REF}$; spur $=20\\log(\\beta/2)$ dBc."),
        ("Why are spurs worse with a wider loop?",
         "Smaller capacitors → larger filter impedance at $f_{REF}$ → larger ripple for the same disturbance charge; also less attenuation by C2."),
        ("Which leakage sources exist in a SKY130 loop filter?",
         "CP switch off-current, junction leakage of the CP output, gate leakage of a thin-oxide MOS cap (C1), and at high temperature all of these grow exponentially."),
        ("What are charge injection and clock feedthrough?",
         "When a switch turns off, its channel charge splits to both terminals (injection); the gate edge couples through $C_{gd}$ (feedthrough). Both put charge on $V_{cont}$ each period."),
        ("Why do spurs fall at f_REF ± ... and how are they measured?",
         "The disturbance is periodic at $f_{REF}$, so it phase-modulates the VCO at $f_{REF}$; measured with a spectrum analyser as dBc relative to the carrier."),
        ("Proposal spur limit and our measurement trick?",
         "−45 dBc max (FFNC off). Measured at /16 output (+24.1 dB to refer to 1.6 GHz), and with pll_en off to separate reference feedthrough."),
        ("How does the SSPLL change the spur mechanisms?",
         "The CP is a pulsed transconductor driven by the held sample; at lock the sample is near zero so the CP current is near zero; spurs come mainly from sampler kickback and pulse feedthrough (Phase 4)."),
        ("What is the effect of mismatch on in-band noise?",
         "Indirect: the static offset makes the CP operate with both sources on longer, injecting more noise; mismatch itself is a deterministic spur source."),
    ], 40)

    # -------------------------------------------------------------------------------------------- step 41
    b.step(41, "Limit summary: dead zone, C1 area, and the bandwidth–spur–noise trade-off", "summary table")
    b.md(r"""
### What happens
Every CP-PLL design is a three-way trade-off with the loop bandwidth in the middle:

| Raise $f_c$ → | Effect | Why |
|---|---|---|
| VCO noise | ↓ suppressed more | $1/(1+G)$ high-pass moves up |
| in-band ×N² noise | ↑ passes more | $NG/(1+G)$ low-pass widens |
| reference spur | ↑ | smaller C → larger $|Z(j\omega_{REF})|$ |
| area | ↓ | $C_{tot}\propto1/f_c^2$ |
| stability | ↓ | sampling delay $180°f_c/f_{REF}$ |

Plus the **dead zone** (fixed with reset delay, which then causes the mismatch spur). The plot computes the first three rows for the
step-38 design family (60° PM, 2% mismatch with 150 ps reset pulses).
""")
    b.code(SPUR_FN + r'''
import sys; sys.path.insert(0, "../models")
import pllmodel as pm
Ip, Kv, N, fref = 100e-6, 2*np.pi*300e6, 32, 50e6
fcs = np.logspace(np.log10(0.3e6), np.log10(5e6), 15)
area, spur, jit = [], [], []
for fc in fcs:
    d = sl.loop_design_type2(fc, 60, Ip, Kv, N)
    area.append((d['C1']/7.48e-15 + d['C2']/2.03e-15)/1e3)
    spur.append(cp_spur(Ip, 0.02, 150e-12, 0, d, Kv, fref)[0])
    jit.append(pm.jitter(pm.TYPE2_TYP.but(fc=fc), "type2")[0]["TOTAL"]*1e12)
fig = make_subplots(rows=1, cols=3, subplot_titles=("filter area (1000 um^2)", "reference spur (dBc)", "rms jitter (ps)"))
fig.add_trace(go.Scatter(x=fcs, y=area, name="area"), 1, 1)
fig.add_trace(go.Scatter(x=fcs, y=spur, name="spur"), 1, 2)
fig.add_trace(go.Scatter(x=fcs, y=jit, name="jitter"), 1, 3)
fig.update_xaxes(type="log", title_text="f_c (Hz)").update_yaxes(type="log", row=1, col=1)
show(fig, 400)
''')
    b.qa([
        ("Summarise the CP-PLL bandwidth trade-off.",
         "Wider: less VCO noise, smaller filter, faster lock; but more in-band (×N²) noise, larger reference spurs and less stability margin."),
        ("Why does the filter area scale as 1/f_c²?",
         "$C_{tot} = bI_pK_{VCO}/(2\\pi N\\omega_c^2)$."),
        ("Which PLL types prefer a narrow bandwidth?",
         "PLLs with a clean VCO (LC) and noisy reference, or jitter-cleaning PLLs that must filter an input clock."),
        ("Why can't a ring-oscillator CP-PLL simply use a 10 MHz bandwidth at 50 MHz reference?",
         "$f_{REF}/5$ is beyond the sampled-loop stability limit; the ×N² in-band floor and spurs also rise."),
        ("What is the largest area block of a typical integrated CP-PLL?",
         "The loop-filter capacitor C1 (Nagam notes the zero capacitor is typically the largest component)."),
        ("How can you shrink C1 without changing dynamics?",
         "Capacitor multiplication, dual-path filters (separate integral and proportional paths with scaled currents), lower $I_p$ with a larger R1 (noise penalty), or (with FFNC) accept more R1 noise because FFNC cancels it (Phase 6)."),
        ("Is the dead zone still an issue in modern PLLs?",
         "Not with a reset-delay PFD; the cost moved to mismatch-induced spurs."),
        ("How do spurs and jitter combine in an rms jitter number?",
         "Deterministic spurs add jitter $\\sigma = \\sqrt2\\cdot10^{spur/20}/(2\\pi f_0)$ per spur pair (if inside the integration band); −55 dBc at 50 MHz offset is outside 40 MHz, so it does not enter our jitter band."),
    ], 41)

    # -------------------------------------------------------------------------------------------- step 42
    b.step(42, "Fixes: reset delay, matched CP with op-amp equalised drains, dump-node buffer", "schematics in words")
    b.md(r"""
### Reset delay (dead zone)
Insert delay in the PFD reset path so UP and DN overlap for $t_{rst} > t_{on}$ of the CP switches (step 33 figure).

### Matched charge pump with op-amp equalised drains
**What:** UP (PMOS source) and DN (NMOS sink) currents depend on their drain voltages through channel-length modulation, so they
match only at one $V_{cont}$. **How:** a replica branch copies the output voltage onto the replica drains and an op-amp adjusts the
PMOS (or NMOS) bias until the replica currents are equal; the main branch then matches at any $V_{cont}$ within compliance.
Residual mismatch ≈ (unaided mismatch)/(1 + A_op-amp).

### Dump node with a unity-gain buffer (charge sharing)
**What:** when a CP switch is off, the internal node between switch and current source drifts to a rail. When the switch closes, that
node's capacitance $C_x$ shares charge with $V_{cont}$: $\Delta V = \frac{C_x(V_x-V_{cont})}{C_x+C_{filter}}$ every cycle. **How:** steer the current
to a *dump* node held at $V_{cont}$ by a unity-gain buffer instead of switching it off, so $V_x \approx V_{cont}$ always and nothing is shared.
Our SSPLL's pulsed-Gm charge pump uses the same dump-node idea (Phase 4, step 50).
""")
    b.code(r'''
V = np.linspace(0.2, 1.6, 200); Vdd = 1.8
fig = go.Figure()
for lam in (0.05, 0.1, 0.2):
    up = 1 + lam*(Vdd - V - Vdd/2); dn = 1 + lam*(V - Vdd/2)            # equal at V = Vdd/2
    mis = 100*(up - dn)
    fig.add_trace(go.Scatter(x=V, y=mis, name=f"simple CP, lambda = {lam} 1/V"))
    fig.add_trace(go.Scatter(x=V, y=mis/(1+100), name=f"op-amp equalised (A = 40 dB), lambda = {lam}", line=dict(dash="dash")))
fig.update_xaxes(title="V_cont (V)").update_yaxes(title="UP - DN mismatch (%)")
show(fig, 420)
Cx, Cf = 20e-15, 1e-12
print("charge-sharing step for C_x = 20 fF at 0.9 V difference into 1 pF:", f"{Cx*0.9/(Cx+Cf)*1e3:.1f} mV per cycle")
''')
    b.qa([
        ("Why do UP and DN currents mismatch as V_cont changes?",
         "Channel-length modulation: the PMOS current falls as $V_{cont}$ rises (less $V_{SD}$) and the NMOS current rises; they cross at one voltage only."),
        ("How does an op-amp improve CP matching?",
         "In a replica branch it forces the replica drain to $V_{cont}$ and servo-adjusts one current source until replica UP = DN; the output branch shares the bias and drain voltage, so mismatch shrinks by the op-amp gain."),
        ("What is charge sharing in a CP and how is it fixed?",
         "Internal nodes at a rail connect to the output when a switch closes and share charge. Fix: keep those nodes at $V_{cont}$ with a unity-gain buffer and steer current to a dump node instead of turning it off."),
        ("What is current steering vs switching a current source on/off?",
         "Steering keeps the source always on and switches its current between the output and a dump path: faster, no turn-on transient, no charge-sharing node drift."),
        ("How does a PFD reset delay affect CP noise?",
         "Both currents conduct for $t_{rst}$ every cycle, so their noise is injected for that time; a longer delay means more in-band CP noise."),
        ("Name a spur-reduction technique that does not change the CP.",
         "Sampled (S&H) loop filter, spur-aware loop filter poles, higher-order filtering, randomising the reference (only in fractional-N), or a smaller $K_{VCO}$."),
        ("Why do differential charge pumps help?",
         "Common-mode disturbances (injection, feedthrough, supply) cancel; they need a common-mode feedback loop and a differential VCO control input."),
        ("What is the compliance range of a CP and how does it limit the VCO range?",
         "Output range over which both current sources stay saturated; the usable $V_{cont}$ range (hence fine-tuning range) is limited to it."),
    ], 42)

    # -------------------------------------------------------------------------------------------- step 43
    b.step(43, "Fixes: sample-reset/S&H filters, calibration, and a PD gain that does not shrink with N", "the bridge to the SSPD")
    b.md(r"""
### Sampled (S&H) loop filter
**What:** isolate the VCO from the charge-pump activity. **How:** let the CP pulses settle on a separate capacitor, then *sample* the
result onto the VCO control node after the pulse has ended. $V_{cont}$ changes once per period by a clean step, with no $I_pR_1$ spike
in between. **Why:** the spur energy comes from the spike; a held voltage contains only the slow loop correction.

### Calibration
Measure and trim CP mismatch (e.g. adjust one current source until the static phase offset is zero), or trim $K_{VCO}$/bandwidth.

### A PD whose gain does not shrink with N
In a CP-PLL, the detector gain *referred to the VCO* is $\frac{I_p}{2\pi N}$ per VCO radian: a larger N makes the detector "see" less of
the VCO's phase error, so its own noise matters N² more. A **sub-sampling PD** measures the VCO phase directly, with gain
$K = A$ (V per VCO radian) independent of N — Phase 4.
""")
    b.code(r'''
T = 20e-9; Ip = 100e-6; R1, C1, C2 = 18.05e3, 13.16e-12, 1.018e-12; tw = 0.5e-9
t = np.linspace(0, 3*T, 3000); dt = t[1]-t[0]
v1 = v2 = 0.0; out = []
for tt in t:
    i = Ip if (tt % T) < tw else 0.0
    i_r = (v2 - v1)/R1
    v1 += i_r/C1*dt; v2 += (i - i_r)/C2*dt
    out.append(v2)
out = np.array(out)
ts = np.floor((t - 0.5*T)/T)*T + 0.5*T                       # last sampling instant (mid-period, after the pulse)
held = np.where(t >= 0.5*T, out[np.clip(np.round(ts/dt).astype(int), 0, len(t)-1)], 0.0)
fig = go.Figure([go.Scatter(x=t*1e9, y=out*1e3, name="V_cont, plain filter (spike I_p R1 each pulse)"),
                 go.Scatter(x=t*1e9, y=held*1e3, name="sampled filter output (updated once per period)", line=dict(shape="hv"))])
fig.update_xaxes(title="time (ns)").update_yaxes(title="mV")
show(fig, 400)
''')
    b.qa([
        ("How does a sampled loop filter reduce spurs?",
         "It hides the CP transient from the VCO: the VCO sees only a held voltage updated after the pulse settles, removing the $I_pR_1$ spike and much of the switching glitch."),
        ("What does a sampled filter cost?",
         "Extra delay (phase margin), extra switch charge injection, and complexity."),
        ("What is the CP gain referred to VCO phase?",
         "$I_p/(2\\pi N)$ A per VCO radian — it shrinks with N, so the detector's own noise is relatively N² larger."),
        ("What is the sub-sampling PD gain referred to VCO phase?",
         "$A$ V per VCO radian (sampled amplitude), independent of N."),
        ("How can you calibrate CP mismatch in the background?",
         "Measure the static phase offset or the average error (e.g. with a TDC or a replica) and adjust one current source digitally until the offset is zero."),
        ("Why does the SSPLL need less spur filtering than a CP-PLL?",
         "At lock the sampled error is ~0, so the pulsed Gm injects almost no charge; there is no PFD reset pulse with both currents on."),
        ("What is the 'reference spur' mechanism unique to sampling PDs?",
         "Kickback: the sampling switch disturbs the VCO node when it opens/closes and loads it with a time-varying capacitance."),
        ("Name a modern PD that keeps the PFD's acquisition but adds sub-sampling's low noise.",
         "Hsu et al.'s PFD with an auxiliary sub-sampling PD (CICC 2011), and the sub-sampling-assisted PFD papers in the project files."),
    ], 43)

    # -------------------------------------------------------------------------------------------- step 44
    b.step(44, "Fix for ring-VCO noise: a wider f_c needs lower in-band noise", "bridge note: motivates the SSPLL")
    b.md(r"""
### What happens
With a ring VCO, the jitter-optimal bandwidth depends on the in-band floor: the lower the floor, the wider the optimum, and the lower the
jitter. Move the slider: the curve's minimum slides right and down as the floor drops from CP-PLL levels (−111 dBc/Hz) to SSPLL levels
(−130 dBc/Hz) — until it hits the $f_{REF}/20$ stability/spur wall.

### Why this is the case for an SSPLL
A CP-PLL can only lower its floor by more CP current (power, area) or a higher $f_{REF}$ (crystal limits). The SSPLL removes the N²
factor from the detector noise — an instant ~20 dB — so the loop can use the full $f_{REF}/20$ bandwidth productively. Beyond that wall,
the only remaining lever on ring noise is **feedforward cancellation** (Phase 6).
""")
    b.code(r'''
import sys; sys.path.insert(0, "../models")
import pllmodel as pm
fcs = np.logspace(5, np.log10(6.25e6), 40)
def frame(floor):
    d = pm.TYP.but(pd=floor)
    j = np.array([pm.jitter(d.but(fc=fc), "sspll")[0]["TOTAL"] for fc in fcs])*1e12
    i = np.argmin(j)
    return ([dict(x=fcs, y=j, name="rms jitter vs bandwidth"),
             dict(x=[2.5e6, 2.5e6], y=[0, 20], name="f_REF/20 wall", line=dict(dash="dot", color="grey"))],
            f"in-band floor {floor} dBc/Hz: optimum f_c = {fcs[i]/1e6:.2f} MHz -> {j[i]:.2f} ps; at 2.5 MHz {np.interp(2.5e6, fcs, j):.2f} ps")
fig = sweep([-105, -111, -115, -120, -125, -130, -135], frame, "in-band floor at the output (dBc/Hz)", active=1,
            layout=lambda f: f.update_xaxes(type="log", title="loop bandwidth f_c (Hz)").update_yaxes(title="ps", range=[0, 10]))
show(fig, 440)
''')
    b.qa([
        ("Why does a ring-VCO PLL benefit more from low in-band noise than an LC PLL?",
         "The ring's free-running noise is high, so the jitter-optimal bandwidth is wide; at a wide bandwidth the in-band floor sets the total."),
        ("What two levers lower a CP-PLL's in-band floor?",
         "More CP current (lower normalised floor) and a higher reference frequency (lower N)."),
        ("By how much does an SSPLL lower the detector floor compared with a CP-PLL here?",
         "From about −111 to −130 dBc/Hz output-referred in our budget (~19 dB), mostly by removing the N² factor."),
        ("What limits the SSPLL bandwidth once its floor is low?",
         "Sampling and hold delay (stability) and spur/ripple considerations: ~$f_{REF}/20$; the reference floor ×N² also remains."),
        ("After the bandwidth wall, what else can reduce ring-VCO jitter?",
         "More VCO power, better VCO topology, supply regulation, or feedforward noise cancellation (FFNC) which works beyond the loop bandwidth up to ~$f_{REF}/8$."),
        ("Why is the optimum bandwidth of the SSPLL in this model at the f_REF/8 edge?",
         "The model has no sampling-delay penalty; the real loop is limited near $f_{REF}/20$ — treat model results beyond that as unreliable."),
    ], 44)

    # -------------------------------------------------------------------------------------------- step 45
    b.step(45, "Lab: behavioural Type-II PLL at 1.6 GHz (frequency steps, slewing, settling)", "results")
    b.md(r"""
### What you do
Use the cycle-by-cycle simulator with the step-38 filter ($I_p$ = 100 µA, $R_1$ = 18.05 kΩ, $C_1$ = 13.16 pF, $C_2$ = 1.02 pF,
$K_{VCO}$ = 2π·300 MHz/V, N = 32), apply a 200 MHz output-frequency step, and vary the loop bandwidth (the filter is redesigned
for each $f_c$ at 60° PM). A wide loop tracks the step linearly. A narrow loop cannot follow: the phase error exceeds the PFD's ±2π
range, the PFD saturates, the CP delivers its maximum average current and $V_{cont}$ **slews** — this is how a PFD acquires frequency.
The final $V_{cont}$ must equal $\Delta\omega/K_{VCO}$ = 667 mV.

**Transistor-level baseline:** the optional SKY130 Type-II implementation (same VCO, CP and filter as computed here) is step 88 of
Phase 7; the numbers here are its targets.
""")
    b.code(r'''
Ip, Kv, N, fref = 100e-6, 2*np.pi*300e6, 32, 50e6
d = sl.loop_design_type2(2.5e6, 60, Ip, Kv, N)
def frame(fc_MHz):
    d = sl.loop_design_type2(fc_MHz*1e6, 60, Ip, Kv, N)
    t, e, vc = sl.cp_pll_sim(Ip, d['R'], d['C1'], d['C2'], Kv, N, fref, ncyc=2000, f_step=200e6/N)
    sat = np.mean(abs(e) >= 2*np.pi)
    return ([dict(x=t*1e6, y=vc*1e3, name="V_cont (mV)", row=1, col=1),
             dict(x=[0, t[-1]*1e6], y=[2*np.pi*200e6/Kv*1e3]*2, name="expected final V_cont", line=dict(dash="dot"), row=1, col=1),
             dict(x=t*1e6, y=np.clip(e, -2*np.pi, 2*np.pi), name="PFD phase error (rad, clipped at 2pi)", row=2, col=1)],
            f"200 MHz output step, f_c = {fc_MHz} MHz: PFD saturated {100*sat:.0f}% of cycles; V_cont after 40 us {vc[-1]*1e3:.0f} mV "
            f"(expected {2*np.pi*200e6/Kv*1e3:.0f} mV)")
fig = sweep([0.2, 0.3, 0.5, 1.0, 2.5], frame, "loop bandwidth f_c (MHz)", active=1, rows=2, cols=1, shared_xaxes=True,
            subplot_titles=("control voltage", "phase error at the PFD"), height=600,
            layout=lambda f: f.update_xaxes(title_text="time (us)", row=2, col=1))
show(fig)
''')
    b.md("**What to look for.** At 2.5 MHz the PFD never saturates: its ±2π range is generous for a fast loop. At 0.3 MHz it saturates for "
         "28% of the cycles and at 0.2 MHz almost always: $V_{cont}$ ramps (slew-limited acquisition), then linear settling takes over. "
         "Lock time grows with the frequency error and with a narrower loop — the reason the proposal's lock time is specified from "
         "`pll_en` with the coarse code already set.")
    b.qa([
        ("Why does a large frequency step make V_cont ramp linearly?",
         "The phase error exceeds the PFD range, the PFD stays in one state, the CP delivers ~constant maximum current into the filter: a constant slope $I_p/C_{tot}$."),
        ("What is the slew rate of V_cont during acquisition here?",
         "At full PFD duty the CP current goes into the capacitors: $I_p/(C_1+C_2) \\approx 100\\,\\mu A/14.2\\,pF \\approx 7$ V/µs; times $K_{VCO}$ this is how fast the VCO frequency can move (here ~2 GHz/µs, so the average over the slewing phase is set by the duty)."),
        ("How do you reduce lock time for large steps?",
         "Coarse digital calibration of the VCO band, bandwidth boosting during acquisition, or a faster frequency detector path."),
        ("How do you verify a behavioural model against a transistor-level PLL?",
         "Match block gains ($K_{VCO}$, $I_p$, filter) from transistor sims, then compare lock transients, final $V_{cont}$, overshoot and settling time."),
        ("What does the final V_cont tell you?",
         "The VCO gain: $\\Delta V = \\Delta\\omega/K_{VCO}$; any discrepancy reveals a different $K_{VCO}$ (or a non-linear tuning curve) in the circuit."),
        ("Why do lock-time specs start 'with the coarse code set'?",
         "Coarse calibration removes the large frequency error; the remaining lock is fast and predictable. Including coarse search would make lock time depend on the search algorithm."),
        ("What would a cycle slip look like in this simulation?",
         "The phase error crossing ±2π (wrapping) during the transient instead of decaying monotonically."),
        ("What do you expect from the SKY130 Type-II baseline compared with this model?",
         "Same bandwidth and PM if gains match; extra effects: CP mismatch/leakage spurs, dead-zone residue, non-linear $K_{VCO}$, divider jitter, supply noise."),
    ], 45)
