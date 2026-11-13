"""Phase 5 - Voltage-controlled delay line, the noise-cancellation block (roadmap steps 59-64)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nb import Book

b = Book("Phase 5 — The voltage-controlled delay line: noise-cancellation block (steps 59–64)",
         "An inverter's delay is roughly $C\\cdot V/I$, so changing $I$ or $C$ with a voltage gives a delay you can steer by "
         "femtoseconds per millivolt. This phase derives that from first principles, measures it on real SKY130 devices with "
         "ngspice (netlists in `learn/spice/`, run with `PDK_ROOT=... ./run_sky130.sh`), and turns the FFNC requirement into "
         "a specification for our 1.6 GHz NCB.")

LOAD = r'''
inv = np.loadtxt("data/inv_delay_vdd.csv", skiprows=1)            # vdd, tphl, tplh  (SKY130 tt, 27 C)
vc = np.loadtxt("data/vcdl_starved.csv", skiprows=1)              # code, vctl, tdr, tdf (two starved cells)
'''

# ------------------------------------------------------------------------------------------------ step 59
b.step(59, "Inverter delay from first principles", "t_d ≈ C_L·V_DD/(2·I), RC model, why delay depends on supply and load")
b.md(r"""
### What happens
An inverter output does not switch instantly: it must charge or discharge its load capacitance $C_L$ through a transistor.

### How
To swing the output by $V_{DD}/2$ (the 50% point) with an average current $I$:
$$t_d \approx \frac{C_L\,V_{DD}/2}{I}\qquad\text{(charge = current × time).}$$
With a saturated device $I \approx \frac{\mu C_{ox}}{2}\frac WL (V_{DD}-V_{TH})^2$ (long channel) or $\propto (V_{DD}-V_{TH})^\alpha$ with
$\alpha\approx1.2$–$1.5$ (short channel, Sakurai's alpha-power law):
$$t_d \propto \frac{C_L\,V_{DD}}{(V_{DD}-V_{TH})^\alpha}.$$
**RC view:** the on-transistor is a resistance $R_{on}\approx 1/[\mu C_{ox}\frac WL(V_{DD}-V_{TH})]$, $t_d\approx 0.69R_{on}C_L$.

### Why it matters for the NCB
Delay depends on **load** (that is how a capacitor bank tunes it), on **current** (how a starved cell tunes it) and on **supply** (an
error source: supply noise becomes delay noise directly at the output). The SKY130 simulation below (W/L = 2/0.15 p, 1/0.15 n,
FO1 + 5 fF) gives about 32 ps at 1.8 V and a supply sensitivity of about −26 ps/V (26 fs/mV) per stage.
""")
b.code(LOAD + r'''
vdd, td = inv[:, 0], (inv[:, 1] + inv[:, 2])/2
fit = np.polyfit(np.log(vdd - 0.45), np.log(td/vdd), 1)           # t_d/V = k (V - Vt)^-alpha  with Vt ~ 0.45 V
alpha = -fit[0]
sens = np.gradient(td, vdd)
fig = make_subplots(rows=1, cols=2, subplot_titles=("inverter delay (SKY130 tt, ngspice)", "supply sensitivity d t_d / d V_DD"))
fig.add_trace(go.Scatter(x=vdd, y=td*1e12, mode="markers+lines", name="simulated t_d (ps)"), 1, 1)
fig.add_trace(go.Scatter(x=vdd, y=np.exp(np.polyval(fit, np.log(vdd-0.45)))*vdd*1e12, name=f"alpha-power fit, alpha = {alpha:.2f}", line=dict(dash="dash")), 1, 1)
fig.add_trace(go.Scatter(x=vdd, y=sens*1e12, mode="markers+lines", name="ps per V"), 1, 2)
fig.update_xaxes(title_text="V_DD (V)")
show(fig, 400)
i18 = np.argmin(abs(vdd-1.8))
print(f"at 1.8 V: t_d = {td[i18]*1e12:.1f} ps, sensitivity {sens[i18]*1e12:.1f} ps/V = {sens[i18]*1e15/1e3:.1f} fs/mV per stage")
''')
b.qa([
    ("Derive the delay of an inverter.",
     "The output must move $V_{DD}/2$ by charging $C_L$ with current I: $t_d \\approx C_LV_{DD}/(2I)$; with $I\\propto(V_{DD}-V_{TH})^\\alpha$, $t_d\\propto C_LV_{DD}/(V_{DD}-V_{TH})^\\alpha$."),
    ("What is the alpha-power law?",
     "Sakurai–Newton model of short-channel drain current $I_D\\propto(V_{GS}-V_{TH})^\\alpha$ with α between 1 (velocity saturated) and 2 (long channel)."),
    ("Why does inverter delay decrease with supply?",
     "Drive current grows faster ($\\propto(V-V_T)^\\alpha$) than the charge needed ($\\propto V$)."),
    ("What is FO4 delay and why is it used?",
     "Delay of an inverter driving four copies of itself; a technology speed metric independent of sizing (SKY130 ≈ 50–60 ps at tt)."),
    ("How do you measure propagation delay in SPICE?",
     "`.meas tran` from the input crossing $V_{DD}/2$ to the output crossing $V_{DD}/2$ (rise and fall separately, then average)."),
    ("Why does supply noise turn into jitter in a delay line?",
     "$\\Delta t_d = (\\partial t_d/\\partial V_{DD})\\,\\Delta V_{DD}$: with ~26 ps/V per stage, 1 mV of supply noise is 26 fs per stage, directly at the output (no loop suppresses it)."),
    ("Why are rise and fall delays different?",
     "PMOS and NMOS drive strengths differ (mobility, sizing); balanced sizing (W_p ≈ 2–3 W_n) equalises them."),
    ("What is the RC model of an inverter delay?",
     "$t_d \\approx 0.69 R_{on}C_L$ with $R_{on}$ the average on-resistance of the conducting transistor."),
    ("How does temperature affect the delay?",
     "Mobility falls with temperature (slower), $V_{TH}$ falls (faster); at 1.8 V the mobility effect usually wins: slower at hot."),
], 59)

# ------------------------------------------------------------------------------------------------ step 60
b.step(60, "Current-starved cell: delay vs control voltage, delay gain dτ/dV, linear range", "plot")
b.md(r"""
### What happens
Put a transistor in series with each inverter device and set its gate with $V_{ctrl}$: it limits ("starves") the current, so the delay
follows $V_{ctrl}$. A PMOS mirror makes the pull-up track the pull-down.

### How
$$\tau \approx \frac{C_L V_{sw}}{I_{starve}},\qquad I_{starve}\approx\frac{k}{2}(V_{ctrl}-V_{TH})^2
\ \Rightarrow\ \boxed{K_{DL} = \frac{d\tau}{dV_{ctrl}} = -\frac{2\tau}{V_{ctrl}-V_{TH}}}$$
The gain is large (and very nonlinear) near threshold and small at high $V_{ctrl}$, where the starving device no longer limits and the
cell behaves like a plain inverter. The SKY130 simulation shows how strong this is: the two-cell gain falls from 251 fs/mV at
1.2 V to 130 at 1.3 V and 78 at 1.4 V — about ±60% over ±0.1 V. The signal the NCB must follow is the residual timing error times
$K_t$: ±10 ps × 5–8.5 mV/ps ≈ ±50–85 mV, so this simple cell would change its own gain noticeably over the swing.

### Why it matters
FFNC needs $\tau(V)$ to be linear over the range of sampled voltages (± tens of mV around the operating point) and its gain to match
$1/K_{t,SSPD}$; a non-linear $K_{DL}$ turns into gain error over the swing. Linearisation options for Phase 7: operate where the curve
is flatter and add amplifier gain in front, capacitive (varactor) control, source degeneration of the starving devices, or splitting
the delay over more, lightly-starved stages.
""")
b.code(LOAD + r'''
c0 = vc[vc[:, 0] == 0]; v, tau = c0[:, 1], (c0[:, 2] + c0[:, 3])/2
g = np.gradient(tau, v)
def frame(v0):
    i = np.argmin(abs(v - v0)); t0, k0 = tau[i], g[i]
    vv = np.linspace(v0-0.15, v0+0.15, 20)
    return ([dict(x=v, y=tau*1e12, mode="lines+markers", name="2-cell delay (ps), SKY130 tt"),
             dict(x=vv, y=(t0 + k0*(vv - v0))*1e12, name="tangent at the operating point", line=dict(dash="dash"))],
            f"V_ctrl = {v0} V: delay {t0*1e12:.0f} ps, gain {k0*1e12:.0f} ps/V = {k0*1e15/1e3:.0f} fs/mV (two cells)")
fig = sweep([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6], frame, "operating point V_ctrl (V)", active=3,
            layout=lambda f: f.update_xaxes(title="V_ctrl (V)").update_yaxes(title="delay (ps)", type="log"))
show(fig, 430)
''')
b.qa([
    ("How does a current-starved delay cell work?",
     "Series transistors limit the charging/discharging current; their gate voltage sets the current and hence the delay $\\approx C V_{sw}/I$."),
    ("Derive the delay gain of a starved cell.",
     "$\\tau = CV/I$, $I = \\frac k2(V_c - V_T)^2$ → $d\\tau/dV_c = -2\\tau/(V_c - V_T)$."),
    ("Why is the gain non-linear?",
     "Current is quadratic (or worse near threshold) in $V_{ctrl}$; the delay is its reciprocal; the slope changes a lot with operating point."),
    ("Why mirror the control to the PMOS side?",
     "So rising and falling edges are both controlled; otherwise only one edge's delay changes and duty cycle distorts."),
    ("What limits the delay range?",
     "Near threshold the cell becomes very slow and noisy (and may fail to switch); at high control the starving device no longer limits."),
    ("What is the delay gain needed by our NCB, roughly?",
     "About 120–200 fs/mV referred to the SSPD sample (step 63), split between the SSPD-to-NCB amplifier and the delay line."),
    ("Why choose a longer channel for the starving devices (L = 0.3 µm here)?",
     "Higher output resistance (current less dependent on the node voltage) and lower 1/f noise per area; matching is better."),
    ("How else can a delay be voltage-controlled?",
     "Varactor / MOS-cap load (capacitive control), shunt-capacitor with a switch resistance, or supply-modulated (not recommended for low noise)."),
], 60)

# ------------------------------------------------------------------------------------------------ step 61
b.step(61, "Capacitive control and gain trimming with a 4-bit capacitor bank", "as in Nagam's C_b")
b.md(r"""
### What happens
Delay can also be tuned by the **load**: a varactor or a MOS capacitor whose capacitance depends on voltage, or a bank of switched
capacitors. In a starved cell, the **gain** $d\tau/dV$ scales with the total load $C_L$ — so a digital capacitor bank trims the gain.

### How
$\tau \approx C_L V_{sw}/I(V_{ctrl})$ → $K_{DL} = \frac{d\tau}{dV} = -C_L\frac{V_{sw}}{I^2}\frac{dI}{dV}$: **proportional to $C_L$**. With
$C_L = C_0 + \text{code}\cdot\Delta C$, the gain moves linearly with the code. Nagam & Kinget tune the NCB gain with a digital capacitor bank
($C_b$); our proposal has a 4-bit `ncb_code`, required to span about 0.6–1.5× of nominal to cover the SSPD gain spread over PVT.

**MOS capacitor C–V** (SKY130 cheat sheet): a 1.8 V NMOS gate cap is ~2.2 fF/µm² at 0 V and ~7.5 fF/µm² above ~0.6 V — a usable
voltage-variable load (varactor), but its non-linearity sets the linear range.

### Why it matters
Calibration (Phase 6, step 71) can only work if the code changes the gain monotonically with fine enough steps: Nagam targets better than
30% gain precision for >10 dB cancellation.
""")
b.code(LOAD + r'''
codes = np.unique(vc[:, 0])
def gain_at(code, v0=1.3):
    c = vc[vc[:, 0] == code]; t = (c[:, 2] + c[:, 3])/2
    return np.gradient(t, c[:, 1])[np.argmin(abs(c[:, 1] - v0))], t[np.argmin(abs(c[:, 1] - v0))]
gs = [gain_at(c) for c in codes]
fig = make_subplots(rows=1, cols=2, subplot_titles=("delay vs V_ctrl per code", "gain at V_ctrl = 1.3 V vs code"))
for c in codes:
    cc = vc[vc[:, 0] == c]
    fig.add_trace(go.Scatter(x=cc[:, 1], y=(cc[:, 2]+cc[:, 3])/2*1e12, name=f"code {int(c)} (C_b = {c*0.5:.1f} fF)"), 1, 1)
fig.add_trace(go.Scatter(x=codes, y=[-g[0]*1e15/1e3 for g in gs], mode="markers+lines", name="|gain| (fs/mV)"), 1, 2)
fig.update_yaxes(type="log", title_text="ps", row=1, col=1).update_xaxes(title_text="V_ctrl (V)", row=1, col=1).update_xaxes(title_text="code", row=1, col=2)
show(fig, 420)
print("gain at 1.3 V (fs/mV):", {int(c): round(-g[0]*1e15/1e3) for c, g in zip(codes, gs)},
      " ratio code15/code0 = %.2f" % (gs[-1][0]/gs[0][0]))
''')
b.qa([
    ("Why does a capacitor bank change the delay *gain* of a starved cell?",
     "$d\\tau/dV = -C_LV_{sw}(dI/dV)/I^2$ is proportional to the load $C_L$; adding capacitance scales the slope."),
    ("Why trim the NCB gain digitally?",
     "Cancellation requires $G_{NCB}K_{SSPD} = 1$; both vary with PVT and amplitude; a code set by calibration restores the product."),
    ("What range and resolution does our ncb_code need?",
     "About 0.6–1.5× of nominal; 16 steps give ~6% per step, well within Nagam's <30% precision target for >10 dB cancellation."),
    ("What is a varactor-based delay cell?",
     "A fixed-current cell loaded by a voltage-variable capacitor (MOS varactor); delay follows C(V). Often more linear and less noisy than heavy starving."),
    ("What limits a MOS varactor as a delay control?",
     "Strong C–V non-linearity around threshold (2.2 → 7.5 fF/µm² in SKY130), leakage, and the need to bias it in its steep region."),
    ("How do you implement a switched-capacitor bank?",
     "Binary-weighted capacitors (MIM or MOS) connected to the delay node through switches; switch resistance and parasitic capacitance when off must be accounted for."),
    ("Does the capacitor bank add jitter?",
     "Indirectly: slower edges (more C for the same current) make the cell more sensitive to noise; jitter grows with delay."),
    ("Why not trim the gain with the starving current instead?",
     "That moves the operating point (delay and linear range) together with the gain; a capacitor bank changes gain with less change of the bias point."),
], 61)

# ------------------------------------------------------------------------------------------------ step 62
b.step(62, "Delay-cell jitter (it grows with delay), supply sensitivity, 1/f noise in the starving devices", "numbers")
b.md(r"""
### What happens
The NCB's own noise goes **straight to the output** (Nagam: $TF_{ncb,2} = 1$): every femtosecond it adds is final.

### How (first-order thermal jitter of one transition)
Two random effects move the crossing: the sampled noise on the node ($kT/C$ divided by the slew rate $I/C$) and the device current noise
integrated during the transition. A standard estimate is
$$\sigma_{t}^2 \approx \frac{kT\,C_L}{I^2}\left(1+\frac{2\gamma V_{DD}}{V_{ov}}\right)
\quad\Rightarrow\quad \frac{\sigma_t}{t_d} = \frac{2}{V_{DD}}\sqrt{\frac{kT}{C_L}}\sqrt{1+\frac{2\gamma V_{DD}}{V_{ov}}}$$
using $t_d = C_LV_{DD}/(2I)$: **for a given load, jitter is proportional to delay** — a slow (heavily starved) cell is a noisy cell.

**Supply sensitivity:** ≈ −26 ps/V per stage (step 59) → 1 mV supply noise ≈ 26 fs. **Flicker:** the starving devices run at low
overdrive with small currents; their 1/f current noise directly modulates the delay at low offsets — use large-area (long-L)
starving devices.

### Why it matters — translating to dBc/Hz
White edge jitter $\sigma_e$ added to every VCO edge gives a phase-noise floor $\mathcal L = (2\pi f_0\sigma_e)^2/f_0$. Our budget's
−150 dBc/Hz NCB floor at 1.6 GHz corresponds to $\sigma_e \approx 126$ fs per edge.
""")
b.code(r'''
C = np.array([5, 10, 20, 40])*1e-15; gamma, Vdd, Vov = 1.0, 1.8, 0.3
f0 = 1.6e9
def frame(I_uA):
    I = I_uA*1e-6
    sig = np.sqrt(kT*C/I**2*(1 + 2*gamma*Vdd/Vov))
    td = C*Vdd/(2*I)
    L = 10*np.log10((2*np.pi*f0*sig)**2/f0)
    return ([dict(x=C*1e15, y=sig*1e15, mode="lines+markers", name="sigma_t per transition (fs)", row=1, col=1),
             dict(x=C*1e15, y=td*1e12, mode="lines+markers", name="delay (ps)", row=1, col=1),
             dict(x=C*1e15, y=L, mode="lines+markers", name="L floor if added to every edge (dBc/Hz)", row=1, col=2),
             dict(x=[5, 40], y=[-150, -150], name="NCB budget -150 dBc/Hz", line=dict(dash="dot"), row=1, col=2)],
            f"I = {I_uA} uA: 10 fF load -> delay {10e-15*Vdd/(2*I)*1e12:.0f} ps, jitter {np.sqrt(kT*10e-15/I**2*(1+2*gamma*Vdd/Vov))*1e15:.0f} fs per transition")
fig = sweep([25, 50, 100, 200, 400], frame, "cell current I (uA)", active=2, rows=1, cols=2,
            subplot_titles=("jitter and delay vs load", "equivalent phase-noise floor at 1.6 GHz"), height=420,
            layout=lambda f: f.update_xaxes(title_text="load C (fF)").update_yaxes(type="log", row=1, col=1))
show(fig)
print("sigma_e for -150 dBc/Hz at 1.6 GHz:", f"{np.sqrt(10**(-15)*f0)/(2*np.pi*f0)*1e15:.0f} fs")
''')
b.qa([
    ("Why does delay-cell jitter grow with delay?",
     "For a given load, a longer delay means a smaller current: smaller slew rate and longer integration of noise; $\\sigma_t/t_d$ is roughly constant, so $\\sigma_t\\propto t_d$."),
    ("Estimate the jitter of one transition.",
     "$\\sigma_t^2 \\approx (kTC/I^2)(1+2\\gamma V_{DD}/V_{ov})$. Example 10 fF, 100 µA, γ = 1, $V_{ov}$ = 0.3 V: $\\sqrt{kTC}/I$ = 64 fs, times $\\sqrt{13}$ = 3.6 → ≈ 230 fs per transition (delay 90 ps)."),
    ("Why is NCB noise critical in FFNC?",
     "It is added after the cancellation point with transfer function 1 to the output; nothing suppresses it."),
    ("How do you convert per-edge white jitter into a phase-noise floor?",
     "$\\mathcal L = \\sigma_\\phi^2/f_0$ with $\\sigma_\\phi = 2\\pi f_0\\sigma_e$ (white jitter sampled once per period, one-sided PSD $2\\sigma_\\phi^2/f_0$)."),
    ("How do you reduce delay-line jitter?",
     "Fewer, faster stages (only the delay range you need), more current per load, larger devices for 1/f, clean supply (LDO rail), avoid operating near threshold."),
    ("Why does the NCB sit on the LDO rail in our design?",
     "Its supply sensitivity (~26 ps/V/stage) would convert supply noise straight into output jitter; the LDO cleans the rail (step 8 decision)."),
    ("What is the role of 1/f noise in starved cells?",
     "Low-frequency current fluctuations of the starving devices modulate the delay slowly: close-in phase noise at the NCB output. Long-channel, large-area starving devices reduce it."),
    ("How would you simulate delay-line jitter in ngspice?",
     "Transient noise (`trnoise` sources or `.option` noise in recent ngspice) with many edges, then measure the standard deviation of edge-to-edge delay; or PSS/pnoise in Spectre (time-average sampled noise)."),
], 62)

# ------------------------------------------------------------------------------------------------ step 63
b.step(63, "Our NCB specification at 1.6 GHz", "gain = 1/K_t, ±10 ps range, code span 0.6–1.5×, noise below the REF floor")
b.md(r"""
### What the NCB must do
Delay each VCO edge by $-\Delta t$ when the SSPD reports $+\Delta t$:
$$G_{t,NCB} = \frac{1}{K_{t,SSPD}} = \frac{1}{A\,\omega_{VCO}}\ \ [\text{s/V}],\qquad K_{t,SSPD} = A\cdot2\pi f_0.$$
(Nagam: $G_{\phi,NCB} = 2\pi f_{out}G_{t,NCB}$, $K_{\phi,SSPD} = K_{t,SSPD}/2\pi f_{out}$; cancellation needs $G_{t}K_{t} = 1$.)

**Scaling from the old design:** the old 2.36 GHz design needed 79.4 fs/mV overall, i.e. $K_t$ = 12.6 mV/ps ($A$ ≈ 0.85 V). With the same
amplitude at 1.6 GHz, $K_t$ = 8.55 mV/ps → **117 fs/mV**; with the conservative $A$ = 0.5 V used in these notebooks, 199 fs/mV.
The slider computes it for any amplitude, and how it splits between the SSPD-to-NCB amplifier (gain $A_{d}$, step 82 of Phase 7) and the
delay line.

| Item | Target | Reason |
|---|---|---|
| overall gain referred to the SSPD sample | $1/(A\cdot2\pi\cdot1.6\,\text{GHz})$: 117 fs/mV (A = 0.85 V) … 199 fs/mV (A = 0.5 V) | cancellation condition |
| delay range | ±10 ps around nominal | ≈ ±4σ of the 2.3 ps residual VCO jitter before cancellation |
| gain trim | 0.6–1.5× in 16 codes (`ncb_code[3:0]`) | SSPD gain spread over PVT; <30% error after calibration |
| noise | floor ≤ −150 dBc/Hz (≈126 fs per edge) | well below the REF floor ×N² (−121.9) and the cancelled ring noise |
| supply | LDO 1.8 V rail | supply sensitivity |
| power | ≈ 0.8 mW (proposal budget, 0.44 mA on the LDO rail) | |
| bypass | `ffnc_en` = 0 sets the delay to a fixed value | FFNC on/off comparison on the same die |
""")
b.code(r'''
f0 = 1.6e9
def frame(A):
    Kt = A*2*np.pi*f0
    G = 1/Kt
    Ad = np.array([1, 2, 4, 8])
    return ([dict(x=Ad, y=G/Ad*1e15/1e3*np.ones(4), mode="lines+markers", name="required delay-line gain (fs/mV at its input)")],
            f"A = {A} V: K_t = {Kt*1e-12*1e3:.2f} mV/ps -> overall NCB gain {G*1e15/1e3:.0f} fs/mV referred to the SSPD sample")
fig = sweep([0.3, 0.5, 0.7, 0.85, 1.0], frame, "SSPD amplitude A (V)", active=3,
            layout=lambda f: f.update_xaxes(type="log", title="gain of the SSPD-to-NCB amplifier A_d").update_yaxes(type="log", title="fs/mV"))
show(fig, 400)
print("two starved cells at V_ctrl = 1.3 V give ~130 fs/mV (step 60): an amplifier gain A_d near 1 with A = 0.85 V, or ~1.5 with A = 0.5 V")
''')
b.qa([
    ("What is the cancellation condition for the NCB gain?",
     "$G_{t,NCB}K_{t,SSPD} = 1$ (time domain), equivalently $G_{\\phi,NCB}K_{\\phi,SSPD} = 1$ (phase domain)."),
    ("Compute the NCB gain for A = 0.85 V at 1.6 GHz.",
     "$K_t = 0.85\\cdot2\\pi\\cdot1.6\\times10^9 = 8.55$ mV/ps → $G_t = 117$ fs/mV."),
    ("Why did the old design need 79.4 fs/mV and the new one more?",
     "$G_t = 1/(A\\omega_{VCO})$: a lower VCO frequency (1.6 vs 2.36 GHz) means a smaller SSPD slope, so more delay per millivolt."),
    ("Why ±10 ps of range?",
     "It must cover the VCO's timing error relative to the reference that FFNC is supposed to remove: with ~2.3 ps rms before cancellation, ±10 ps is about ±4σ."),
    ("Why must the NCB gain be programmable?",
     "The SSPD gain depends on amplitude (PVT) and the delay-line gain on process; a fixed design would leave tens of percent gain error."),
    ("What happens when ffnc_en = 0?",
     "The NCB delay is held at a fixed value (no modulation), so the output equals the PLL output plus a constant delay — the reference measurement for the jitter-reduction spec."),
    ("Why is the NCB noise budget −150 dBc/Hz?",
     "So the NCB contribution stays well below the remaining noise after cancellation (REF ×N² at −121.9 in band, residual ring noise) — Nagam: NCB noise must be non-dominant."),
    ("Where does the NCB sit relative to the output dividers?",
     "Before them: the dividers (/2…/16) take the cancelled clock, so all taps benefit."),
    ("What are the proposal's NCB power and area estimates?",
     "About 0.8 mW typ (0.44 mA from the LDO rail) and 2500 µm² including the 4-bit capacitor bank."),
], 63)

# ------------------------------------------------------------------------------------------------ step 64
b.step(64, "Lab: the delay line in SKY130 — delay vs V_ctrl, gain per code, range, jitter, power", "characterisation plots")
b.md(r"""
### What you do
1. Run `learn/spice/vcdl_starved.sp` (via `run_sky130.sh`) — two current-starved SKY130 cells with a 4-bit bank of 0.5 fF steps.
2. Read the **operating point** where the gain is close to the step-63 requirement and the curve is most linear.
3. Check the **range**: delay change over ±50 mV around the operating point.
4. Estimate **jitter** with the step-62 formula (or transient noise) and **power** $\approx C_{tot}V_{DD}^2f_0$ per cell.

The slider moves the code; the title gives gain, linearity and range at $V_{ctrl}$ = 1.3 V. This is a learning circuit, not the final NCB
(Phase 7, step 83): there the cells are sized for the gain range with an amplifier in front, on the LDO rail.
""")
b.code(LOAD + r'''
def frame(code):
    c = vc[vc[:, 0] == code]; v, t = c[:, 1], (c[:, 2] + c[:, 3])/2
    g = np.gradient(t, v); i = np.argmin(abs(v - 1.3))
    lin = abs(g[i+1] - g[i-1])/abs(g[i])*100
    rng = (np.interp(1.25, v, t) - np.interp(1.35, v, t))*1e12
    return ([dict(x=v, y=t*1e12, mode="lines+markers", name="delay (ps)", row=1, col=1),
             dict(x=v, y=-g*1e15/1e3, mode="lines+markers", name="|gain| (fs/mV)", row=1, col=2)],
            f"code {int(code)}: gain {-g[i]*1e15/1e3:.0f} fs/mV at 1.3 V, gain change over +/-0.1 V {lin:.0f}%, delay range over +/-50 mV {rng:.1f} ps")
fig = sweep(list(np.unique(vc[:, 0])), frame, "capacitor-bank code", fmt="{:.0f}", active=1, rows=1, cols=2,
            subplot_titles=("delay vs V_ctrl", "local gain"), height=420,
            layout=lambda f: f.update_xaxes(title_text="V_ctrl (V)").update_yaxes(type="log"))
show(fig)
Cn = 15e-15
print(f"dynamic power of one cell at 1.6 GHz with ~{Cn*1e15:.0f} fF switched: {Cn*1.8**2*1.6e9*1e6:.0f} uW")
''')
b.qa([
    ("How do you characterise a VCDL?",
     "Delay vs control voltage per gain code (transient + .meas), local gain and its linearity, range, jitter (transient noise), power, supply sensitivity, over PVT."),
    ("How do you choose the operating point of the NCB?",
     "Where the gain matches the requirement with the flattest gain-vs-voltage curve and enough range on both sides; then fix it with the common-mode of the SSPD-to-NCB amplifier."),
    ("What does 'gain change over ±0.1 V' tell you?",
     "Non-linearity: a large change means the cancellation gain depends on the instantaneous error (residue grows with large errors)."),
    ("How do you measure delay-line gain in Cadence?",
     "Same transient with a parametric sweep of V_ctrl and a calculator expression `delay()` per point; or use PSS-based sensitivity."),
    ("What is the dominant power of the NCB?",
     "Dynamic switching $CV^2f$ at 1.6 GHz for each stage plus the amplifier's bias current."),
    ("Why simulate with the real PDK instead of the square-law model?",
     "Short-channel and threshold effects make the curve differ strongly from the square law, especially near threshold; the gain must come from the real models."),
    ("What would you change if the gain is too small?",
     "Increase the load (cap bank), operate closer to threshold (more gain, more noise and non-linearity), add a stage, or raise the amplifier gain $A_d$."),
    ("What corners matter most for the NCB?",
     "Slow corner/hot (most delay and gain), fast/cold (least), and R/C corners if the bank uses MIM; the gain code must cover the spread."),
], 64)

b.save(os.path.join(os.path.dirname(__file__), "..", "phase5_vcdl.ipynb"))
