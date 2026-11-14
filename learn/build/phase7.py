"""Phase 7 - block design. Step 72: noise/power/area budget; step 73: loop parameters."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nb import Book
from qa72 import QA72
from qa73 import QA73
from qa74 import QA74

b = Book("Phase 7 — Block design (steps 72–74)",
         "Phases 1–6 explained *why* each block exists. Phase 7 designs them — and the first design step is to decide how "
         "much each block is allowed to cost: jitter, power and area (step 72); the second is the loop itself (step 73). "
         "This notebook splits the proposal's targets "
         "(1.4 ps typ / 3.2 ps max with FFNC, −110/−120 dBc/Hz at 300 kHz, 9 mW, 0.08 mm²) into one allocation per block, "
         "shows which allocations are critical, and lets you move them with sliders. The same numbers are in "
         "`docs/design/step72_budget.md`; the model is `design/budget/step72_budget.py`.")

B = r'''
import sys; sys.path.insert(0, "../models"); sys.path.insert(0, "../design/budget")
import pllmodel as pm, step72_budget as bud
f = pm.freq_axis(n=700)
def total(corner, on, **kw):
    ff, S = bud.spectra(corner, on, f=f, **kw)
    j, L = bud.jitter(S, ff, 1.6e9)
    return j, L, S
i300 = int(abs(f - 3e5).argmin())
'''

b.step(72, "Phase-noise and power budget per block, and the jitter target", "budget table")
b.md(r"""
### What happens
Every block — crystal, reference receiver, SSPD, charge pump, loop-filter resistor, ring, current source, NCB, LDO — adds its
own small random timing error to the output edges. These errors are independent, so the output jitter is their
**root-sum-square**, each shaped by the path from the block to the output. A budget fixes, *before* any transistor is sized,
how much each block may contribute so the sum meets the specification, and gives each block a pass/fail number in its own
units.

### How it happens
Each source enters at a physical place in the loop; its transfer to the output follows from Phases 3–6:

$$S_{out}(f) = \big[N^2 S_{REF} + S_{PD}\big]\big|H + G_c(1-H)\big|^2 + S_{VCO}\big|(1-G_c)(1-H)\big|^2
 + S_{NCB} + (\omega_0 K_s)^2 S_{v,LDO} + |G_c|^2 S_{alias}$$

$$\sigma_t = \frac{1}{2\pi f_0}\sqrt{\int_{10\,\mathrm{kHz}}^{40\,\mathrm{MHz}} S_{out}(f)\,df},\qquad
\sigma_t^2 = \sum_i \sigma_{t,i}^2 .$$

Each block's physics gives its source in its own units, then converted to dBc/Hz:

| Block | Source | Conversion |
|---|---|---|
| REF (XO + receiver) | floor $L_{REF}$ | $\times N^2$ (+30.1 dB); per-edge jitter $\sigma = \sqrt{L f_{REF}}/(2\pi f_{REF})$ |
| SSPD | $kT/C$ | $L = kT/(2 C_s A^2 f_{REF})$ |
| Pulsed-Gm CP | $4kT\gamma g_m$ during duty $d$ | $L = kT\gamma/(2A^2 g_m d)$, with $\beta = 2A g_m d$ |
| Loop-filter $R_1$ | $4kTR_1$ | $\times |C_1/(C_1+C_2+sR_1C_1C_2)|^2\,(K_{VCO}/\omega)^2$ |
| CCO | $i_n$ (A/√Hz) | $S_\varphi = (K_I i_n)^2/f^2$ |
| NCB / LDO | floor / $v_n$ | 1:1 / $(\omega_0 K_s v_n)^2$ |

### Why it happens this way
The reference is a *time* error, so it is multiplied by $N^2$; the SSPD and CP see the VCO directly, so they are not. The
oscillator's noise is high-passed by the loop $(1-H)$ and again by $(1-G_c)$ with FFNC. The NCB and LDO come *after*
everything, so nothing filters them. Aliasing is the price of FFNC: the SSPD folds VCO noise at $f \pm kf_{REF}$ into the band
and the cancellation path adds it to the output. The relative size of the contributions below follows from these facts.
""")
b.code(B + r'''
rows = {}
for c in ("typ", "pess"):
    for on in (False, True):
        rows[(c, on)] = total(c, on)[0]
print(f"{'block':40s} {'typ off':>8s} {'typ on':>8s} {'pess off':>9s} {'pess on':>8s}   (ps rms, 10 kHz-40 MHz)")
for k in rows[("typ", True)]:
    v = [rows[(c, o)].get(k, 0)*1e12 for c in ("typ", "pess") for o in (False, True)]
    print(f"{k:40s} {v[0]:8.3f} {v[1]:8.3f} {v[2]:9.3f} {v[3]:8.3f}")
print(f"{'spec':40s} {'2.3 typ':>8s} {'1.4 typ':>8s} {'4.7 max':>9s} {'3.2 max':>8s}")
''')
b.md("**Figure 72.1 — where the jitter comes from** (typ, FFNC off vs on). Hover for values.")
b.code(B + r'''
j0, _, _ = total("typ", False); j1, _, _ = total("typ", True)
names = sorted([k for k in j1 if k != "TOTAL"], key=lambda k: j1[k])
fig = go.Figure()
fig.add_trace(go.Bar(y=names, x=[j0.get(k, 0)*1e12 for k in names], orientation="h", name=f"FFNC off ({j0['TOTAL']*1e12:.2f} ps)", marker_color="#2a78d6"))
fig.add_trace(go.Bar(y=names, x=[j1[k]*1e12 for k in names], orientation="h", name=f"FFNC on ({j1['TOTAL']*1e12:.2f} ps)", marker_color="#eb6834"))
fig.update_layout(barmode="group", height=480, xaxis_title="rms jitter contribution (ps)", title="Jitter budget per block, typ")
show(fig)
''')
b.md(r"""
**Try it.** Square the bars: the ring's $1.87^2 = 3.5$ ps² is 78% of the FFNC-off variance; the SSPD's $0.014^2$ is 0.004%.
A block at one third of the largest adds only 5% to the total — that is why you do not spend effort on small bars.

**Figure 72.2 — the ring 1/f³ corner and the 300 kHz spec.** The proposal specifies −110 dBc/Hz typ at 300 kHz with FFNC off.
Move the ring's 1/f³ corner: at the simulated 1.1 MHz the spec is missed by ~1.5 dB; the budget allocates ≤ 0.6 MHz.
""")
b.code(B + r'''
def frame(fc3):
    tr = []; note = []
    for on, col in ((False, "#2a78d6"), (True, "#eb6834")):
        j, L, _ = total("typ", on, over={"ring VCO core": (-98.35, fc3)})
        tr.append(dict(x=f, y=L, name=f"FFNC {'on' if on else 'off'}", line=dict(color=col)))
        note.append(f"{'on' if on else 'off'}: {j['TOTAL']*1e12:.2f} ps, L(300k) {L[i300]:.1f}")
    tr.append(dict(x=[3e5, 3e5], y=[-110, -120], name="spec typ (off, on)", mode="markers",
                   marker=dict(size=9, color="#59636e", symbol="circle")))
    return tr, f"ring f_c3 = {fc3/1e6:.2f} MHz — " + " | ".join(note)
def lay(fig):
    fig.update_xaxes(type="log", title="offset (Hz)"); fig.update_yaxes(title="L(f) at 1.6 GHz (dBc/Hz)", range=[-140, -95])
show(sweep([0.2e6, 0.3e6, 0.4e6, 0.5e6, 0.6e6, 0.8e6, 1.1e6, 1.5e6, 2.2e6], frame, "ring 1/f³ corner",
           fmt="{:.2g} Hz", active=4, layout=lay))
''')
b.md(r"""
**Figure 72.3 — loop bandwidth as the fallback knob.** If step 74 cannot lower the corner, `icp_trim` raises $f_c$ (it scales
$\beta$). Watch FFNC-off improve while FFNC-on barely moves (the cancellation already removes the VCO noise near $f_c$), and
remember the price: the sample-and-hold delay costs $\approx 180°\,f_c/f_{REF}$ of phase margin.
""")
b.code(B + r'''
def frame(fc):
    tr = []; note = []
    for on, col in ((False, "#2a78d6"), (True, "#eb6834")):
        j, L, _ = total("typ", on, fc=fc)
        tr.append(dict(x=f, y=L, name=f"FFNC {'on' if on else 'off'}", line=dict(color=col)))
        note.append(f"{'on' if on else 'off'} {j['TOTAL']*1e12:.2f} ps, L300k {L[i300]:.1f}")
    return tr, f"f_c = {fc/1e6:.1f} MHz (hold-delay PM loss {180*fc/50e6:.0f}°) — " + " | ".join(note)
def lay(fig):
    fig.update_xaxes(type="log", title="offset (Hz)"); fig.update_yaxes(title="L(f) (dBc/Hz)", range=[-140, -95])
show(sweep([1.5e6, 2.0e6, 2.5e6, 2.8e6, 3.0e6, 3.5e6, 4.0e6], frame, "loop bandwidth", fmt="{:.2g} Hz", active=2, layout=lay))
''')
b.md(r"""
**Figure 72.4 — the CCO current noise.** The CCO's thermal floor is fixed by physics: a source of current $I$ with headroom
$V_h$ has $i_n^2 \approx 4kT\cdot 2I/V_h$ → about 7 pA/√Hz at 1.31 mA and 1.2 V. Only its flicker corner is a design choice
(large-area devices, RC-filtered mirror gate). Slide the corner.
""")
b.code(B + r'''
KI = 1.22e12
def frame(fcf):
    tr = []; note = []
    for on, col in ((False, "#2a78d6"), (True, "#eb6834")):
        j, L, S = total("typ", on, over={"CCO current DAC + mirror": (-104.2, fcf)})
        tr.append(dict(x=f, y=10*np.log10(S["CCO current DAC + mirror"]/2), name=f"CCO part, FFNC {'on' if on else 'off'}", line=dict(color=col)))
        note.append(f"{'on' if on else 'off'} total {j['TOTAL']*1e12:.2f} ps (CCO {j['CCO current DAC + mirror']*1e12:.2f})")
    return tr, f"CCO 1/f corner {fcf/1e6:.2f} MHz, i_n = 7.2 pA/√Hz at 1 MHz — " + " | ".join(note)
def lay(fig):
    fig.update_xaxes(type="log", title="offset (Hz)"); fig.update_yaxes(title="CCO contribution at the output (dBc/Hz)", range=[-160, -100])
show(sweep([0.05e6, 0.1e6, 0.2e6, 0.3e6, 0.5e6, 1.1e6, 2.2e6], frame, "CCO flicker corner", fmt="{:.2g} Hz", active=3, layout=lay))
''')
b.md("**Figure 72.5 — sensitivity.** Total jitter when one block alone is 3 dB worse than its allocation. Long bars = critical allocations; short bars = slack you can trade for power, area or robustness.")
b.code(B + r'''
sens = bud.sensitivity()
base = total("typ", True)[0]["TOTAL"]*1e12
names = sorted(sens, key=lambda k: sens[k][1])
fig = go.Figure(go.Bar(y=names, x=[sens[k][1] - base for k in names], orientation="h", marker_color="#eb6834",
                       name="FFNC on", hovertemplate="%{y}: +%{x:.3f} ps<extra></extra>"))
fig.update_layout(height=430, xaxis_title=f"increase of total typ jitter (ps) over {base:.2f} ps", title="Block +3 dB → total jitter (FFNC on)")
show(fig)
''')
b.md(r"""
### Power and area

Blocks on the 1.8 V LDO rail draw their current from VDDA = 3.3 V, so every mA there costs **3.3 mW**; the ring is fed from
VDDA through the CCO (4.86 mW). Logic that can run from VDDD costs 1.8 mW/mA — that is why dividers and FLL logic live there.
""")
b.code(B + r'''
tot = {"on": 0, "off": 0, "on_w": 0, "off_w": 0}
print(f"{'block':46s} {'supply':6s} {'I (mA)':>7s} {'P typ':>7s} {'P worst':>8s}")
for name, sup, i, p, pw, ncb in bud.power_table():
    print(f"{name:46s} {sup:6s} {i:7.3f} {p:7.2f} {pw:8.2f}")
    tot["on"] += p; tot["on_w"] += pw
    if not ncb: tot["off"] += p; tot["off_w"] += pw
print(f"TOTAL FFNC on {tot['on']:.2f} mW (worst {tot['on_w']:.2f}; spec 9.0 typ / 15 max)")
print(f"TOTAL FFNC off {tot['off']:.2f} mW (worst {tot['off_w']:.2f}; spec 7.5 typ / 13 max)")
j = total("typ", True)[0]["TOTAL"]
print(f"FoM = {10*np.log10(j**2*tot['on']):.1f} dB (proposal -227.5)")
print("\narea:", ", ".join(f"{n} {a}" for n, a in bud.AREA), f"\n-> {sum(a for _, a in bud.AREA)} um^2 (spec 80,000 typ)")
''')
b.md(r"""
### Layout convenience, decided now

The budget tells you which nodes are noise-critical, so the schematic can already be drawn the way it will be laid out:

- **Ring (dominant):** 5 identical cells, U-shaped placement so the wrap-around wire matches the others, dummy loads on unused
  taps, integer fingers per device so each cell is one abutting row.
- **CCO (second):** 1:8 mirror as 9 unit devices in a common-centroid row with end dummies; binary DAC from unit cells;
  RC-filtered gate (long high-resistance poly + MOS cap under the array); 3.3 V devices in their own guard ring.
- **Reference receiver (×N²):** short, shielded route from the pad; own VDDA branch; far from the ring.
- **SSPD, CP:** fully differential, mirror-symmetric, unit MIM tiles with a dummy ring, ABBA input pair, non-minimum L.
- **Loop filter:** R1 as equal legs of wide poly; C1 MOS cap with MIM stacked above (~9.5 fF/µm², V_cont > 0.6 V); C2 linear MIM; tiles ≤ 30×30 µm.
- **NCB / LDO:** NCB at the output buffer with its own LDO decap; LDO pass device as unit fingers along the supply edge.
- **Everywhere:** few distinct unit devices; supply domains as bands (VDDA / LDO 1.8 V / VDDD); level shifters only at band edges.
""")
b.qa(QA72, 72)

# ------------------------------------------------------------------------------------------------ step 73
L73 = r'''
import sys, json, csv; sys.path.insert(0, "../models"); sys.path.insert(0, "../design/budget"); sys.path.insert(0, "../design/loop")
import sampled_loop as sl
D = json.load(open("../design/loop/data/step73_design.json"))
R, C1, C2, KV, beta, tp, T = D["R"], D["C1"], D["C2"], D["KV"], D["beta"], D["tp"], 20e-9
'''
b.step(73, "Loop parameters (f_c, PM, β, R1, C1, C2) from the out2 jitter model", "design sheet")
b.md(r"""
### What happens
The loop filter and the charge-pump gain decide how the work is split: **below $f_c$** the loop makes the VCO follow the
clean reference, **above $f_c$** the VCO runs free and FFNC removes its noise up to about $f_{REF}/8$. Step 73 picks
$f_c$ and PM from the jitter model, computes $R_1, C_1, C_2$ for the *real, sampled* loop, and turns them into PDK devices
in whole layout tiles.

### How it happens
$$L(s) \approx \beta K_{VCO}\frac{Z(s)}{s}e^{-st_p},\quad Z(s) = \frac{1+sR_1C_1}{s(C_1+C_2)(1+sR_1\frac{C_1C_2}{C_1+C_2})},
\quad \beta = 2A\,g_m\frac{\tau}{T}$$

Closed-form start (zero and pole around $\omega_c$, spread $b=\tan(45°+\varphi_{lead}/2)$):
$C_{tot} = b\beta K_{VCO}/\omega_c^2$, $C_2 = C_{tot}/b^2$, $C_1 = C_{tot}-C_2$, $R_1 = b/(\omega_c C_1)$, with
$\varphi_{lead} = PM + 360°f_c t_p$. Then the **exact sampled model** corrects it: the SSPD samples once per period and the
Gm delivers one packet $q[k] = \beta T\theta_e[k]$ a delay $t_p$ later, so
$$x[k+1] = e^{AT}x[k] + e^{A(T-t_p)}B\,q[k],\qquad L(z) = \beta T\,C(zI-e^{AT})^{-1}e^{A(T-t_p)}B .$$

### Why it happens this way
Sampling and the packet delay cost phase that a continuous model does not see (it would give 40.6° instead of 50° at
$t_p$ = 11 ns). The loop sees only the product $\beta K_{VCO}$, so the big passives can be frozen now and the unknown
$K_{VCO}$ absorbed later by the small $g_m$ cells. A MOS capacitor is non-linear, so $C_1$ can be a dense MOS cap only
if $V_{cont}$ stays where it is flat.
""")
b.md(r"""
**Figure 73.1 — what pins $f_c$.** Slide $f_c$ (PM 50°). Watch three numbers in the title: out2 jitter (barely moves),
out1 $L$(300 kHz) (needs $f_c \ge 2.5$ MHz for −110 dBc/Hz) and the FFNC jitter reduction (needs $f_c \le 2.5$ MHz for
35 %). Only 2.5 MHz meets both typ values.
""")
b.code(B + r'''
def frame(fc):
    tr = []; jj = {}
    for on, col in ((False, "#2a78d6"), (True, "#eb6834")):
        j, L, _ = total("typ", on, fc=fc)
        jj[on] = (j["TOTAL"]*1e12, L[i300])
        tr.append(dict(x=f, y=L, name=f"{'out2 (FFNC on)' if on else 'out1 (FFNC off)'}", line=dict(color=col)))
    red = 100*(1 - jj[True][0]/jj[False][0])
    return tr, (f"f_c {fc/1e6:.1f} MHz: out1 {jj[False][0]:.2f} ps, L300k {jj[False][1]:.1f} | out2 {jj[True][0]:.2f} ps | "
                f"FFNC reduction {red:.0f} %")
def lay(fig):
    fig.update_xaxes(type="log", title="offset (Hz)"); fig.update_yaxes(title="L(f) (dBc/Hz)", range=[-140, -95])
show(sweep([1.5e6, 2.0e6, 2.5e6, 3.0e6, 3.5e6, 4.0e6, 5.0e6], frame, "f_c", fmt="{:.2g} Hz", active=2, layout=lay))
''')
b.md(r"""
**Figure 73.2 — the packet delay $t_p$ eats phase margin.** The filter is fixed (designed for $t_p$ = 2.5 ns). Slide
$t_p$ and watch the phase at crossover. The dashed line is the continuous model, which cannot see the delay at all.
""")
b.code(L73 + r'''
f = np.logspace(4, np.log10(0.49/T), 400)
s = 2j*np.pi*f
Lc = beta*KV*(1 + s*R*C1)/(s*(C1 + C2)*(1 + s*R*C1*C2/(C1 + C2)))/s
def frame(t):
    L = sl.loop_gain(f, R, C1, C2, KV, beta, T, t)
    fc, pm_ = sl.margins(R, C1, C2, KV, beta, T, t)
    ph = np.degrees(np.unwrap(np.angle(L))); ph -= 360*np.round(ph[0]/360)
    return ([dict(x=f, y=ph, name="sampled loop ∠L", line=dict(color="#2a78d6")),
             dict(x=f, y=np.degrees(np.unwrap(np.angle(Lc))), name="continuous ∠L", line=dict(color="#eb6834", dash="dash"))],
            f"t_p = {t*1e9:.1f} ns: f_c = {fc/1e6:.2f} MHz, PM = {pm_:.1f}°  (delay lag at f_c = {360*fc*t:.1f}°)")
def lay(fig):
    fig.update_xaxes(type="log", title="frequency (Hz)"); fig.update_yaxes(title="phase of L (deg)", range=[-260, -100])
    fig.add_vline(x=D["fc"], line_width=1, line_color="#59636e")
show(sweep([0.5e-9, 1e-9, 2.5e-9, 5e-9, 8e-9, 11e-9], frame, "packet delay t_p", fmt="{:.2g} s", active=2, layout=lay))
''')
b.md(r"""
**Figure 73.3 — loop-gain spread and `icp_trim`.** $m = (A g_m \tau K_{VCO})$/nominal varies over PVT. Slide $m$ and watch
the phase-step response (cycle by cycle, exact): small $m$ → slow and under-damped, large $m$ → fast but ringing. The
`icp_trim` codes multiply $\beta$ by 0.67 / 1 / 1.33 / 1.67 to pull $m$ back towards 1.
""")
b.code(L73 + r'''
def frame(m):
    t, e, v = sl.step(R, C1, C2, KV, beta*m, T, tp, ncyc=150, phi_step=1.0)
    fc, pm_ = sl.margins(R, C1, C2, KV, beta*m, T, tp)
    return ([dict(x=t*1e6, y=e/(2*np.pi*1.6e9)*1e12, name="phase error", line=dict(color="#2a78d6", shape="hv")),
             dict(x=[0, 3], y=[10, 10], name="±10 ps", line=dict(color="#59636e", dash="dot")),
             dict(x=[0, 3], y=[-10, -10], name="−10 ps", line=dict(color="#59636e", dash="dot"), showlegend=False)],
            f"m = {m:.2f}: f_c = {fc/1e6:.2f} MHz, PM = {pm_:.1f}°")
def lay(fig):
    fig.update_xaxes(title="time after a 1 rad phase step (µs)", range=[0, 3]); fig.update_yaxes(title="phase error (ps)", range=[-60, 100])
show(sweep([0.35, 0.5, 0.67, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0], frame, "loop-gain multiplier m", fmt="{:.2f}", active=4, layout=lay))
''')
b.md(r"""
**Figure 73.4 — why $V_{cont}$ must stay in 0.6–1.2 V.** The measured C-V of the nfet_01v8 MOS capacitor (ngspice, frozen
PDK) at three temperatures and three corners. Below about 0.6 V the channel disappears and $C_1$ collapses — the zero
would move up and the phase margin would fall.
""")
b.code(r'''
import csv
rows = list(csv.DictReader(open("../design/loop/data/moscap_cv.csv")))
fig = go.Figure()
cols = {"tt": "#2a78d6", "ss": "#eb6834", "ff": "#1baf7a"}; dash = {"-40": "dot", "27": "solid", "110": "dash"}
for c in ("tt", "ss", "ff"):
    for t in ("-40", "27", "110"):
        r = [x for x in rows if x["corner"] == c and x["temp"] == t]
        fig.add_trace(go.Scatter(x=[float(x["vg"]) for x in r], y=[float(x["c_mos_fF"])/100 for x in r], name=f"{c}, {t} °C",
                                 line=dict(color=cols[c], dash=dash[t], width=2 if t == "27" else 1.2)))
fig.add_vrect(x0=0.6, x1=1.2, fillcolor="#e6e8eb", opacity=0.5, line_width=0, annotation_text="V_cont window")
fig.update_layout(height=420, title="nfet_01v8 gate capacitance density (W = L = 10 µm)",
                  xaxis_title="V_gate (V)", yaxis_title="C (fF/µm²)")
show(fig)
''')
b.md(r"""
### The design sheet

| Parameter | Value |
|---|---|
| $f_c$, PM | 2.50 MHz, 50.0° (exact sampled loop, packet delay $t_p$ = 2.5 ns, $\le$ 5 ns required) |
| $\beta$ | 0.848 µA/rad = $2A g_m d$ with $A$ = 0.5 V, $d$ = 1 %, $g_m$ = 84.8 µS = 3 units × 28.3 µS |
| $R_1$ | 11.01 kΩ — res_xhigh_po_2p85, L = 15.5 µm |
| $C_1$ | 17.11 pF — 2 tiles × (9 nfet_01v8 W = L = 10 µm + 1 cap_mim_m3_1 30×30 µm on top) |
| $C_2$ | 2.205 pF — 2 × cap_mim_m3_1 30 × 18.1 µm |
| zero / pole | 0.845 / 7.40 MHz; peaking 2.5 dB; $f_{3dB}$ 4.3 MHz; step settles in 0.34 µs |
| $V_{cont}$ window | 0.6–1.2 V |
| `icp_trim` | 00 → ×1, 01 → ×1.33, 10 → ×0.67, 11 → ×1.67 (Gm unit count 3 / 4 / 2 / 5) |
| residual spread after trim | $m$ within ×0.75–×1.3 → PM 45.5–50° at every R/C corner |

**Layout convenience built into these numbers:** $C_1$ is an integer number of identical tiles (β was rescaled to fit
the tiles, not the other way round); $C_2$ is two equal MIM rectangles; $R_1$ is one body of a legal width; the trim is
done with identical Gm unit cells, not with odd-sized devices; the MIM over the MOS cap shields the filter node from
routing above. Full sheet with every number: `docs/design/step73_loop.md`.
""")
b.qa(QA73, 73)

# ------------------------------------------------------------------------------------------------ step 74
V74 = r'''
import json, base64
from IPython.display import Image, display
D = lambda n: json.load(open("../design/vco/data/" + n))
base, q3, ch = D("step74_base.json"), D("step74_q3.json"), D("step74_char_q3.json")
'''
b.step(74, "VCO redesign: stages, LVT, sizing for frequency, K_VCO and phase noise", "schematic and sizing table")
b.md(r"""
### What happens
The ring's frequency is set by how fast each stage charges its load: more CCO current means faster edges. vtune hangs a
little extra capacitance on every output for fine tuning. Every transistor's noise moves the edges a little. White
(thermal) noise gives phase noise falling at −20 dB/dec. Slow flicker (1/f) noise is up-converted into close-in phase
noise falling at −30 dB/dec, and below the $1/f^3$ corner it dominates.

### How it happens
A current-fed ring settles at the supply voltage $V_{ring}$ where its average current equals the CCO current, so
$f \approx I/(N C_{node} V_{ring})$, $K_I = \partial f/\partial I$, $K_{VCO} = \partial f/\partial v_{tune}$.
Phase noise follows the ISF $h(\tau) = d\phi/dq$:
$$\mathcal{L}_{th}(\Delta f) = \frac{2N\langle h^2 S_{th}\rangle}{2(2\pi\Delta f)^2},\qquad
\mathcal{L}_{fl}(\Delta f) = \frac{2N\langle h\sqrt{B}\rangle^2}{\Delta f\,2(2\pi\Delta f)^2}.$$

### Why it happens this way
Flicker only becomes phase noise through the **dc part** of $h$ (here 0.67 of its rms), and a device's flicker density
scales like $1/(WL)$. The smallest devices on an output node therefore dominate: the fine-tune switch and the coupling TG
nMOS. The main inverters contribute only 13 %. Enlarging just those two devices fixes the noise for 9 % more current;
scaling the whole ring would cost power one-for-one.

**Methods used:** M1 (transient frequency), M2 (ISF with the models' noise), M3 (noise tables), M4 (LVS), M5 (drawing
checks). What, why and how for each: `docs/methods.md`.
""")
b.md("**Figure 74.1 — the ISF of one ring node and who causes the flicker.** Hover to compare the base cell and the step-74 cell.")
b.code(V74 + r'''
fig = make_subplots(rows=1, cols=2, subplot_titles=("ISF h(τ) of node p1 (rad/pC)", "flicker share (% of the base cell's total)"))
for d, c, n in ((base, "#2a78d6", "base cell"), (q3, "#eb6834", "step-74 cell")):
    h = np.array(d["h"]); ph = np.arange(len(h))/len(h)
    fig.add_trace(go.Scatter(x=np.r_[ph, 1], y=np.r_[h, h[0]]/1e12, name=f"{n} (corner {d['fc3']/1e6:.2f} MHz)",
                             line=dict(color=c)), row=1, col=1)
names = {"x1.xp2": "main pMOS", "x1.xn2": "main nMOS", "x1.xs2": "tune switch S", "x1.xt1n": "TG nMOS (own)",
         "x2.xt1n": "TG nMOS (next)", "x1.xt1p": "TG pMOS (own)", "x2.xt1p": "TG pMOS (next)"}
ref = 10**(base["Lfl"]/10)
for d, c in ((base, "#2a78d6"), (q3, "#eb6834")):
    fig.add_trace(go.Bar(y=list(names.values()), x=[d["shares"][k][1]*10**(d["Lfl"]/10)/ref*100 for k in names],
                         orientation="h", marker_color=c, showlegend=False), row=1, col=2)
fig.update_layout(height=430, barmode="group"); fig.update_xaxes(title_text="injection time / period", row=1, col=1)
show(fig)
print(f"base: Lth {base['Lth']:.2f}, Lfl {base['Lfl']:.2f}, corner {base['fc3']/1e6:.2f} MHz, I {base['I']*1e3:.3f} mA")
print(f"step-74: Lth {q3['Lth']:.2f}, Lfl {q3['Lfl']:.2f}, corner {q3['fc3']/1e6:.2f} MHz, I {q3['I']*1e3:.3f} mA")
''')
b.md("**Figure 74.2 — coarse tuning range and ring-node voltage over corners.** Slider: process/temperature corner.")
b.code(V74 + r'''
labs = {"tt_27": "tt, 27 °C, 10 fF", "ss_110": "ss, 110 °C, 15 fF", "ff_-40": "ff, −40 °C, 5 fF"}
def frame(k):
    r = ch["f_vs_I"][k]; I = [x[0]*1e3 for x in r]
    return ([dict(x=I, y=[x[1]/1e9 for x in r], name="f (GHz)", line=dict(color="#2a78d6"), row=1, col=1),
             dict(x=I, y=[1.44]*len(I), name="1.44 GHz", line=dict(color="#59636e", dash="dot"), row=1, col=1),
             dict(x=I, y=[1.76]*len(I), name="1.76 GHz", line=dict(color="#59636e", dash="dash"), row=1, col=1),
             dict(x=I, y=[x[2] for x in r], name="ring node (V)", line=dict(color="#eb6834"), row=1, col=2),
             dict(x=I, y=[1.8]*len(I), name="1.8 V limit", line=dict(color="#59636e", dash="dot"), row=1, col=2)],
            labs[k])
def lay(fig):
    fig.update_xaxes(title_text="CCO feed current (mA)")
show(sweep(list(labs), frame, "corner", fmt="{}", active=0, rows=1, cols=2,
           subplot_titles=("frequency (GHz)", "ring supply node (V)"), layout=lay))
''')
b.md("**Figure 74.3 — fine tuning.** $K_{VCO}$ is negative; below about 0.7 V the switch turns off and the curve flattens, so the lock window is 0.7–1.2 V.")
b.code(V74 + r'''
fig = go.Figure()
cols = {"tt_27": "#2a78d6", "ss_110": "#eb6834", "ff_-40": "#1baf7a"}
for k, c in cols.items():
    r = [x for x in ch["f_vs_vtune"][k] if x[1]]
    fig.add_trace(go.Scatter(x=[x[0] for x in r], y=[x[1]/1e9 for x in r], name=k.replace("_", ", ") + " °C", line=dict(color=c)))
fig.add_vrect(x0=0.7, x1=1.2, fillcolor="#e6e8eb", opacity=0.5, line_width=0, annotation_text="lock window")
fig.update_layout(height=420, xaxis_title="vtune (V)", yaxis_title="f (GHz) at the 1.6 GHz current", title="Fine tuning")
show(fig)
''')
b.md("**The schematics** (xschem, hierarchical: cell → ring core → VCO; LVS-clean against the simulated netlist).")
b.code(r'''
from IPython.display import Image, display
for n in ("sspll_vco_dcell", "sspll_vco_core", "sspll_vco", "sspll_vco_acbuf"):
    print(n); display(Image(filename=f"../docs/img/step74_{n}.png", width=900))
''')
b.md(r"""
### Sizing table and results
| Device | Model | W × nf | L | Role |
|---|---|---|---|---|
| XP1/XP2 | pfet_01v8 | 3.0 µm × 4 | 0.15 µm | main inverter pMOS |
| XN1/XN2 | nfet_01v8 | 3.0 µm × 2 | 0.15 µm | main inverter nMOS |
| XS1/XS2 | nfet_01v8 | 4.5 µm × 1 | **0.30 µm** | fine-tune switch |
| XC1/XC2 | nfet_01v8 | 4.5 µm × 1 | 0.50 µm | fine-tune MOS cap |
| XT1N/XT2N | nfet_01v8 | 0.84 µm × 1 | **0.30 µm** | coupling TG nMOS |
| XT1P/XT2P | pfet_01v8 | 0.63 µm × 1 | 0.15 µm | coupling TG pMOS |

1.437 mA for 1.6 GHz (tt), ring node 1.45 V; $\mathcal{L}$(1 MHz) −98.7 dBc/Hz thermal, $1/f^3$ corner 0.57 MHz;
$K_{VCO}$ −300 MHz/V (0.6–1.2 V); $K_I$ 0.85 GHz/mA; 1.44–1.76 GHz over corners with the ring node ≤ 1.71 V (10 fF/node);
start-up < 9 ns. System: 2.04 / 1.32 ps (FFNC off/on), 9.55 mW, FoM −227.8 dB. Full report: `docs/design/step74_vco.md`.
""")
b.qa(QA74, 74)
b.save(os.path.join(os.path.dirname(__file__), "..", "phase7_design.ipynb"))
