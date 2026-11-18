"""Phase 7 - block design. Step 72: noise/power/area budget; step 73: loop parameters."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nb import Book
from qa72 import QA72, QA72HV
from qa73 import QA73, QA73HV
from qa74 import QA74
from qa75 import QA75
from qa76 import QA76
from qa77 import QA77
from qa78 import QA78

b = Book("Phase 7 — Block design (steps 72–78)",
         "Phases 1–6 explained *why* each block exists. Phase 7 designs them — and the first design step is to decide how "
         "much each block is allowed to cost: jitter, power and area (step 72); the second is the loop itself (step 73). "
         "This notebook splits the proposal's targets "
         "(1.4 ps typ / 3.2 ps max with FFNC, −110/−120 dBc/Hz at 300 kHz, 9 mW, 0.08 mm²) into one allocation per block, "
         "shows which allocations are critical, and lets you move them with sliders. The same numbers are in "
         "`docs/design/step72_budget.md`; the model is `design/budget/step72_budget.py`. **Device-rule migration (18 Nov 2026):** "
         "all analog blocks now use 5 V devices and the output is 50 MHz × 16 = 800 MHz; step 72 has been redone for it "
         "(section *Step 72 redo*, `docs/design/step72_hv_budget.md`). Steps 73–78 below are still the 1.6 GHz designs "
         "and are being redone in 5 V devices.")

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

# ------------------------------------------------------------------------------------------------ step 72 redo (800 MHz, 5 V)
BH = r"""
import sys, json; sys.path.insert(0, "../models"); sys.path.insert(0, "../design/budget")
import pllmodel as pm, step72_hv_budget as hv
fh = pm.freq_axis(n=700)
def total_hv(corner, on, **kw):
    ff, S = hv.spectra(corner, on, f=fh, **kw)
    j, L = hv.jitter(S, ff)
    return j, L, S
j300 = int(abs(fh - 3e5).argmin())
"""
b.md(r"""
<a id='step-72-hv'></a>
### Step 72 redo — 800 MHz with 5 V analog devices (18 Nov 2026)

**What happens.** The challenge rules changed: every analog block must use the 5 V devices (`nfet/pfet_g5v0d10v5`) and
only logic may use 1.8 V devices. A full-swing 3-stage ring in 5 V devices tops out at about 1.1 GHz at ss 110 °C, so the
output moved to **50 MHz × 16 = 800 MHz** and the regulated 1.8 V rail (the LDO) was dropped. The budget is redone with the
same model; the surprise is that the jitter does not change.

**How it happens.** A ring's phase noise per milliwatt is described by its figure of merit:

$$\text{FoM}_{ring} = \mathcal{L}(\Delta f) + 10\log\frac{P}{1\,\text{mW}} - 20\log\frac{f_0}{\Delta f}$$

At fixed power and FoM, $\mathcal{L} \propto f_0^2$: 6.02 dB lower at half the carrier. Jitter divides the integrated phase
noise by $(2\pi f_0)^2$, so the carrier cancels:

$$\sigma_{t,ring}^2 = \frac{\int 2\cdot 10^{\mathcal{L}(\Delta f)/10}\, d\Delta f}{(2\pi f_0)^2} \;\propto\; \frac{1}{P}$$

Without the LDO the NCB and the ring's current source see the raw VDDA. Two new terms replace the LDO term — one adds at
the output (the NCB delay moves by $K_s$ per volt), one enters as VCO noise (the ring frequency moves by $K_{vdd}$ per volt
through the CCO's finite output impedance):

$$S_{\varphi,NCB}(f) = (2\pi f_0 K_s)^2\, S_{v,DD}(f), \qquad
S_{\varphi,ring}(f) = \frac{K_{vdd}^2\, S_{v,DD}(f)}{f^2}\,\big|(1-G_c)(1-H)\big|^2$$

**Why it happens this way.** Timing jitter is a time error; frequency only converts it to radians and back. Thick-oxide
devices are slow (f_T 10.9 GHz vs 58 GHz) but *quieter* per unit $g_m$ — their long channels have little excess thermal
noise (γ ≈ 1.1 instead of 1.9) — so a 5 V ring at the step-74 power can reach the step-74 FoM. The budget assumes it does
(typ) and also covers missing it by 3 dB with a doubled 1/f³ corner (pess). Full write-up:
`docs/design/step72_hv_budget.md`; model: `design/budget/step72_hv_budget.py`.
""")
b.code(BH + r"""
rows = {(c, o): total_hv(c, o)[0] for c in ("typ", "pess") for o in (False, True)}
print(f"{'block':44s} {'typ off':>8s} {'typ on':>8s} {'pess off':>9s} {'pess on':>8s}   (ps rms, 10 kHz-40 MHz, 800 MHz)")
for k in rows[("typ", True)]:
    v = [rows[(c, o)].get(k, 0)*1e12 for c in ("typ", "pess") for o in (False, True)]
    print(f"{k:44s} {v[0]:8.3f} {v[1]:8.3f} {v[2]:9.3f} {v[3]:8.3f}")
print(f"{'proposal target':44s} {'2.6 typ':>8s} {'1.6 typ':>8s} {'5.0 max':>9s} {'3.2 max':>8s}")
""")
b.md("**Figure 72.6 — where the jitter comes from at 800 MHz** (typ). Compare with Figure 72.1: the bars are almost the same "
     "length in picoseconds, the LDO bar is gone and two VDDA bars have appeared.")
b.code(BH + r"""
j0, _, _ = total_hv("typ", False); j1, _, _ = total_hv("typ", True)
names = sorted([k for k in j1 if k != "TOTAL"], key=lambda k: max(j1[k], j0.get(k, 0)))
fig = go.Figure()
fig.add_trace(go.Bar(y=names, x=[j0.get(k, 0)*1e12 for k in names], orientation="h", name=f"FFNC off ({j0['TOTAL']*1e12:.2f} ps)", marker_color="#2a78d6"))
fig.add_trace(go.Bar(y=names, x=[j1[k]*1e12 for k in names], orientation="h", name=f"FFNC on ({j1['TOTAL']*1e12:.2f} ps)", marker_color="#eb6834"))
fig.update_layout(barmode="group", height=500, xaxis_title="rms jitter contribution (ps)", title="Jitter budget per block, typ, 800 MHz")
show(fig)
""")
b.md(r"""
**Figure 72.7 — what if the thick-oxide ring misses the FoM?** Slide the penalty on the ring's thermal noise (0 dB = the
step-74 FoM at the same power). The proposal's maximum (3.2 ps with FFNC on) still holds at 6 dB (2.40 ps); the typical
1.6 ps holds up to a 2 dB penalty (1.62 ps), and the FFNC-off typical 2.6 ps likewise (2.56 ps).
""")
b.code(BH + r"""
RING = "ring VCO core (5 V, 3-stage)"
L0, fc3 = hv.ALLOC[RING]["typ"]
def frame(pen):
    tr = []; note = []
    for on, col in ((False, "#2a78d6"), (True, "#eb6834")):
        j, L, _ = total_hv("typ", on, over={RING: (L0 + pen, fc3)})
        tr.append(dict(x=fh, y=L, name=f"FFNC {'on' if on else 'off'}", line=dict(color=col)))
        note.append(f"{'on' if on else 'off'}: {j['TOTAL']*1e12:.2f} ps, L(300k) {L[j300]:.1f}")
    tr.append(dict(x=[3e5, 3e5], y=[-114, -124], name="spec typ (off, on)", mode="markers",
                   marker=dict(size=9, color="#59636e", symbol="circle")))
    return tr, f"ring FoM penalty {pen:.0f} dB (L(1 MHz) = {L0 + pen:.1f} dBc/Hz) — " + " | ".join(note)
def lay(fig):
    fig.update_xaxes(type="log", title="offset (Hz)"); fig.update_yaxes(title="L(f) at 800 MHz (dBc/Hz)", range=[-145, -95])
show(sweep([0, 1, 2, 3, 4, 5, 6], frame, "ring FoM penalty", fmt="{:.0f} dB", active=0, layout=lay))
""")
b.md(r"""
**Figure 72.8 — why the CCO must be cascoded.** Without an LDO, VDDA noise reaches the ring through the CCO's output
impedance. Here VDDA carries a poor 300 nV/√Hz; slide the ring's supply pushing $K_{vdd}$. At 5 MHz/V (a cascoded,
long-channel CCO) it adds 0.29 ps with FFNC off; at 20 MHz/V (1.17 ps) it is larger than the CCO's own noise (0.90 ps), and at
40 MHz/V (2.35 ps, a simple mirror) larger than the ring itself.
""")
b.code(BH + r"""
SUP = "VDDA noise into the ring (CCO r_out)"
def frame(k):
    tr = []; note = []
    for on, col in ((False, "#2a78d6"), (True, "#eb6834")):
        j, L, S = total_hv("typ", on, over={SUP: (300e-9, k*1e6)})
        tr.append(dict(x=fh, y=10*np.log10(np.maximum(S[SUP], 1e-30)/2), name=f"VDDA part, FFNC {'on' if on else 'off'}", line=dict(color=col)))
        note.append(f"{'on' if on else 'off'} total {j['TOTAL']*1e12:.2f} ps (VDDA {j[SUP]*1e15:.0f} fs)")
    return tr, f"K_vdd = {k:g} MHz/V at 300 nV/√Hz — " + " | ".join(note)
def lay(fig):
    fig.update_xaxes(type="log", title="offset (Hz)"); fig.update_yaxes(title="VDDA contribution (dBc/Hz)", range=[-170, -100])
show(sweep([1, 2, 5, 10, 20, 40], frame, "K_vdd", fmt="{:g} MHz/V", active=2, layout=lay))
""")
b.md(r"""
**The device data behind the allocations.** `design/feas/hv_noise.py` biases each device at $g_m/I_D = 10$, 100 µA and
simulates its drain-current noise with ngspice `.noise`. Read γ (thermal noise per $g_m$, lower is better) and the 1/f
corner (where flicker equals thermal).
""")
b.code(r"""
import json
d = json.load(open("../design/feas/hv_noise.json"))
print(f"{'device':16s} {'L':>5s} {'W':>7s} {'gamma':>6s} {'1/f corner':>11s} {'vn(10k)':>12s}")
for r in d:
    print(f"{r['model']:16s} {r['l']:5.2f} {r['w']:7.1f} {r['gamma']:6.2f} {r['corner_hz']/1e6:8.2f} MHz {r['vn_10k']*1e9:7.1f} nV/√Hz")
""")
b.md(r"""
**Power at 800 MHz.** Everything analog now runs from VDDA = 3.3 V (3.3 mW per mA); logic from VDDD = 1.8 V. The LDO is gone
(−0.48 mW); level shifters (+0.33 mW) and the output divider (+0.12 mW) arrive. The total stays at about 9 mW.
""")
b.code(BH + r"""
tot = {"on": 0, "off": 0, "on_w": 0, "off_w": 0}
for name, sup, i, p, pw, ncb in hv.power_table():
    print(f"{name:74s} {sup:5s} {i:6.3f} mA {p:6.2f} mW (worst {pw:5.2f})")
    tot["on"] += p; tot["on_w"] += pw
    if not ncb: tot["off"] += p; tot["off_w"] += pw
j = total_hv("typ", True)[0]["TOTAL"]
print(f"TOTAL FFNC on {tot['on']:.2f} mW (worst {tot['on_w']:.2f}); off {tot['off']:.2f} mW (worst {tot['off_w']:.2f})")
print(f"FoM = {10*np.log10(j**2*tot['on']):.1f} dB; area {sum(a for _, a in hv.AREA)} um^2")
""")
b.qa(QA72HV, "72 — 800 MHz redo")

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

# ------------------------------------------------------------------------------------------------ step 73 redo (800 MHz, 5 V)
L73H = r"""
import sys, json, csv; sys.path.insert(0, "../models"); sys.path.insert(0, "../design/budget"); sys.path.insert(0, "../design/loop")
import sampled_loop as sl, pllmodel as pm, step72_hv_budget as hv
DH = json.load(open("../design/loop/data/step73_hv_design.json"))
fh = pm.freq_axis(n=700)
"""
b.md(r"""
<a id='step-73-hv'></a>
### Step 73 redo — loop parameters for 800 MHz with 5 V devices (18 Nov 2026)

**What happens.** The loop keeps its shape: $f_c$ = 2.5 MHz, PM = 50°, zero and pole at 0.88 / 7.13 MHz. What changes
is the big capacitor. $C_1$ must now be a thick-oxide MOS capacitor (`nfet_g5v0d10v5`), which stores 2.6× less charge
per µm² (2.87 against 7.48 fF/µm²) and is flat only above 1.0 V.

**How it happens.** Only $\beta K_{VCO}/C$ and $R_1C_1$ set the loop. Scale $C_1, C_2$ and $\beta$ down by the same
factor and $R_1$ up, and the loop is unchanged. The price is the thermal noise of the larger $R_1$, which reaches the VCO
through the filter divider:

$$S_{\varphi,R_1}(f) = 4kTR_1\left|\frac{C_1}{C_1+C_2+j2\pi fR_1C_1C_2}\right|^2\frac{K_{VCO}^2}{f^2}\,\big|(1-G_c)(1-H)\big|^2$$

**Why it happens this way.** Inversion capacitance is $C_{ox} = \varepsilon_{ox}/t_{ox}$: the thicker oxide of the
5 V device lowers it, and its higher threshold moves the flat region up. The window moves to 1.0–2.3 V, centred at
VDDA/2. With 2 tiles ($C_1$ = 8.81 pF, $R_1$ = 20.6 kΩ) the extra $R_1$ noise costs 0.013 ps and the filter fits in
about 3 800 µm². Full write-up: `docs/design/step73_hv_loop.md`.
""")
b.code(L73H + r"""
print(f"f_c {DH['fc']/1e6:.2f} MHz, PM {DH['pm']:.1f} deg (t_p {DH['tp']*1e9:.1f} ns), zero {DH['fz']/1e6:.3f} MHz, pole {DH['fp']/1e6:.2f} MHz")
print(f"beta {DH['beta']*1e9:.0f} nA/rad -> g_m {DH['gm']*1e6:.1f} uS = 3 units x {DH['gm']/3*1e6:.2f} uS (A {DH['A']} V/rad, duty {DH['duty']})")
print(f"C1 {DH['C1']*1e12:.2f} pF = {DH['ntile']} tiles x {DH['tile_pF']:.3f} pF; C2 {DH['C2']*1e12:.3f} pF; R1 {DH['R']/1e3:.2f} kOhm "
      f"(xhigh_po_2p85, L {DH['R_len']:.1f} um); area ~{DH['area_um2']:.0f} um2")
print(f"peaking {DH['peak_dB']:.2f} dB, f_3dB {DH['f3dB']/1e6:.2f} MHz, overshoot {DH['overshoot_pct']:.1f} %, settles to +-10 ps in {DH['settle_s']*1e6:.2f} us")
print("R1 noise (contribution / total, ps):", {k: (round(a, 3), round(b_, 3)) for k, (a, b_) in DH["noise"].items()})
print(f"residual m 0.75-1.3 at all R/C corners: PM {DH['residual']['0.75-1.3'][0]:.1f}-{DH['residual']['0.75-1.3'][1]:.1f} deg")
""")
b.md(r"""
**Figure 73.6 — the thick-oxide capacitor.** C-V of the 5 V MOS capacitor at three corners against the 1.8 V device of the
first design. The shaded band is the new $V_{cont}$ window.
""")
b.code(r"""
import csv
cvh = list(csv.DictReader(open("../design/loop/data/moscap_hv_cv.csv")))
cvl = list(csv.DictReader(open("../design/loop/data/moscap_cv.csv")))
fig = go.Figure()
for (c, t), col, w in ((("tt", "27"), "#2a78d6", 3), (("ss", "-40"), "#7fb0ea", 1.5), (("ff", "110"), "#7fb0ea", 1.5)):
    rr = [r for r in cvh if r["corner"] == c and r["temp"] == t]
    fig.add_trace(go.Scatter(x=[float(r["vg"]) for r in rr], y=[float(r["c_mos_fF"])/100 for r in rr], mode="lines+markers",
                             name=f"nfet_g5v0d10v5 {c} {t} °C", line=dict(color=col, width=w)))
rr = [r for r in cvl if r["corner"] == "tt" and r["temp"] == "27"]
fig.add_trace(go.Scatter(x=[float(r["vg"]) for r in rr], y=[float(r["c_mos_fF"])/100 for r in rr], mode="lines",
                         name="nfet_01v8 (first design) tt", line=dict(color="#eb6834", dash="dash")))
fig.add_vrect(x0=1.0, x1=2.3, fillcolor="#e6e8eb", opacity=0.5, line_width=0)
fig.update_layout(height=420, xaxis_title="V_cont (V)", yaxis_title="capacitance density (fF/µm²)", yaxis_range=[0, 9])
show(fig)
""")
b.md(r"""
**Figure 73.7 — how many C1 tiles?** The loop is the same for any tile count; only $R_1$ and the area change. Slide
the number of tiles and watch the $R_1$ noise and the totals. Two tiles is the knee: three cost 1 500 µm² more for
0.013 ps.
""")
b.code(L73H + r"""
TR = {t["ntile"]: t for t in DH["trade"]}
def frame(n):
    t = TR[n]; tr = []; note = []
    for on, col in ((False, "#2a78d6"), (True, "#eb6834")):
        ff, S = hv.spectra("typ", on, f=fh, lf=(t["R"], t["C1"], t["C2"]))
        k = "loop-filter resistor R1"
        tr.append(dict(x=ff, y=10*np.log10(np.maximum(S[k], 1e-30)/2), name=f"R1 noise, FFNC {'on' if on else 'off'}", line=dict(color=col)))
    return tr, (f"{n} tile(s): C1 {t['C1']*1e12:.1f} pF, R1 {t['R']/1e3:.1f} kΩ, area {t['area']:.0f} µm² — R1 jitter "
                f"{t['rj_off']:.3f} / {t['rj_on']:.3f} ps, total {t['tot_off']:.3f} / {t['tot_on']:.3f} ps (off / on)")
def lay(fig):
    fig.update_xaxes(type="log", title="offset (Hz)"); fig.update_yaxes(title="R1 contribution (dBc/Hz)", range=[-160, -110])
show(sweep([1, 2, 3, 4, 5, 6], frame, "C1 tiles", fmt="{:d}", active=1, layout=lay))
""")
b.qa(QA73HV, "73 — 800 MHz redo")

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

1.352 mA for 1.6 GHz (tt), ring node 1.38 V; $\mathcal{L}$(1 MHz) −98.66 dBc/Hz thermal, $1/f^3$ corner 0.60 MHz;
$K_{VCO}$ −326 MHz/V (0.6–1.2 V); $K_I$ 0.84 GHz/mA; 1.44–1.76 GHz over corners with the ring node ≤ 1.65 V (10 fF/node);
start-up < 9 ns. System: 2.04 / 1.32 ps (FFNC off/on), 9.55 mW, FoM −227.8 dB. Full report: `docs/design/step74_vco.md`.
""")
b.qa(QA74, 74)

# ------------------------------------------------------------------------------------------------ step 75
V75 = r"""
import json
import numpy as np
from IPython.display import Image, display
D = lambda n: json.load(open("../design/cco/data/" + n))
s, nz = D("step75_sim.json"), D("step75_noise.json")
"""
b.step(75, "Current-fed VCO supply (CCO) with PDK-legal resistors", "schematic")
b.md(r"""
### What happens
The ring has no supply of its own: a pMOS current source from VDDA (3.3 V) pushes a current $I_{CCO}$ into its supply
node, and the ring settles at the voltage where it draws exactly that current. The current is the coarse frequency
knob, set by a 5-bit code. IBIAS (5 µA from the harness) is the only reference.

### How it happens
$$I_{CCO} = M\,I_u\,(N_{base} + \text{code}) = 25 \times 2.5\,\mu\text{A} \times (11 + \text{code}) = 0.69\ldots2.63\ \text{mA}$$
IBIAS → 2-unit nMOS diode → unit sinks (11 always on + binary 1…16) → 1-unit pMOS diode MREF → RC filter
($R_F$ = 10 MΩ, $C_F$ = 7.3 pF) → 25-unit pMOS MOUT → ring node. The filter makes the reference side invisible above
$f_F = 1/(2\pi R_F C_F) \approx 2$ kHz; what is left is MOUT's own noise plus the resistor's:
$$S_{i,out} \approx 4kT\gamma g_{m,out} + g_{m,out}^2\,\frac{4kTR_F}{1+(2\pi f R_F C_F)^2}
\;\xrightarrow{f \gg f_F}\; 4kT\gamma g_{m,out} + \frac{g_{m,out}^2\,4kT}{(2\pi f C_F)^2 R_F}$$
so a **larger** $R_F$ gives **less** in-band noise. Frequency noise is $S_f = K_I^2 S_i$, phase noise $S_\phi = S_f/f^2$.

### Why it happens this way
A current feed isolates the ring from VDDA (high output impedance), and current is what the ring's frequency is
proportional to. The ±20 % IBIAS tolerance sets the code range (3.4 : 1). The 1:25 ratio keeps the reference branch's
own supply current at 4 % of the ring current, which is what brings the worst-case power back under 15 mW. Above the
1.8 V rail the ring's thin-oxide devices would be over-stressed, so an active clamp sinks any excess current once the
ring node reaches VDDL.

**Methods used:** M10 (DC operating points and compliance), M11 (.noise of the output current, AC supply rejection),
M12 (clamp with the ring's measured I–V), M13 (level-shifter transient), M4/M5 (LVS, drawing checks). `docs/methods.md`.
""")
b.md("**Figure 75.1 — coarse tuning.** Slider: IBIAS. Each point is one corner × VDDA; the band is the current the ring needs.")
b.code(V75 + r"""
dc = s["dc"]
def frame(ib):
    tr = []
    for code, c in ((0, "#1baf7a"), (10, "#2a78d6"), (31, "#eb6834")):
        r = [x for x in dc[:90] if x[3] == ib*1e-6 and x[4] == code]
        tr.append(dict(x=[f"{x[0]}/{x[1]}°C/{x[2]}V" for x in r], y=[-x[5]*1e3 for x in r], mode="markers",
                       name=f"code {code}", marker=dict(color=c, size=8)))
    tr += [dict(x=[f"{x[0]}/{x[1]}°C/{x[2]}V" for x in dc[:90] if x[3] == ib*1e-6 and x[4] == 0], y=[0.97]*10,
                name="code 0 must be ≤ 0.97 mA (ff, −40 °C)", line=dict(color="#1baf7a", dash="dot")),
           dict(x=[f"{x[0]}/{x[1]}°C/{x[2]}V" for x in dc[:90] if x[3] == ib*1e-6 and x[4] == 0], y=[2.02]*10,
                name="code 31 must be ≥ 2.02 mA (ss, 110 °C)", line=dict(color="#eb6834", dash="dot"))]
    return tr, f"IBIAS {ib} µA"
def lay(fig):
    fig.update_yaxes(title_text="I into ring node (mA)")
show(sweep([4, 5, 6], frame, "IBIAS (µA)", fmt="{}", active=1, layout=lay))
""")
b.md("**Figure 75.2 — compliance and the clamp.** Left: current vs ring-node voltage at the least headroom; right: the "
     "ring node at ss/110 °C (where the ring needs the most voltage) for every code.")
b.code(V75 + r"""
fig = make_subplots(rows=1, cols=2, subplot_titles=("I (mA) vs ring node (V): ss, 110 °C, VDDA 2.97 V, code 31",
                                                    "ring node (V) vs code: ss, 110 °C, VDDA 3.63 V"))
cp = np.array(s["compliance"])
fig.add_trace(go.Scatter(x=cp[:, 0], y=-cp[:, 1]*1e3, name="I out", line=dict(color="#2a78d6")), row=1, col=1)
for ib, c in ((4e-6, "#eb6834"), (6e-6, "#eda100")):
    r = [x for x in s["clamp"] if x[0] == ib]
    fig.add_trace(go.Scatter(x=[x[1] for x in r], y=[x[2] for x in r], name=f"IBIAS {ib*1e6:.0f} µA",
                             line=dict(color=c)), row=1, col=2)
fig.add_hline(y=1.8, line_dash="dot", line_color="#e87ba4", row=1, col=2)
fig.update_yaxes(range=[-0.6, 2.7], row=1, col=1); fig.update_layout(height=420)
show(fig)
""")
b.md("**Figure 75.3 — output-current noise and supply rejection** (complete circuit with PDK resistors and capacitors).")
b.code(V75 + r"""
fig = make_subplots(rows=1, cols=2, subplot_titles=("output noise (pA/√Hz)", "|ΔI/ΔVDDA| (µA/mV)"))
fig.add_trace(go.Scatter(x=nz["f"], y=np.array(nz["n"])*1e12, name="CCO noise", line=dict(color="#2a78d6")), row=1, col=1)
fig.add_hline(y=10.3, line_dash="dot", line_color="#eb6834", row=1, col=1)
ps = np.array(s["psr"])
fig.add_trace(go.Scatter(x=ps[:, 0], y=ps[:, 1]*1e3, name="supply → current", line=dict(color="#1baf7a")), row=1, col=2)
fig.update_xaxes(type="log"); fig.update_yaxes(type="log", row=1, col=1); fig.update_layout(height=420)
show(fig)
print("jitter contribution of the CCO: %.2f ps (FFNC off) / %.2f ps (on); system total %.2f / %.2f ps; L(300 kHz) %.1f / %.1f dBc/Hz"
      % (nz["off"][0], nz["on"][0], nz["off"][1], nz["on"][1], nz["off"][2], nz["on"][2]))
""")
b.md("**The schematics** (CCO top → DAC, filter resistor, level shifter; LVS-clean against the simulated netlist).")
b.code(r"""
from IPython.display import Image, display
for n in ("cco", "cco_dac", "cco_rf", "ls_1v8_3v3"):
    print("sspll_" + n); display(Image(filename=f"../docs/img/step75_sch_{n}.png", width=900))
""")
b.md(r"""
### Sizing table and results
| Device | Model | W × nf × m | L | Role |
|---|---|---|---|---|
| XNB | nfet_g5v0d10v5 | 1 × 1 × 2 | 4 µm | IBIAS input diode (2 units) |
| XU0…XU5 | nfet_g5v0d10v5 | 1 × 1 × (11, 1, 2, 4, 8, 16) | 4 µm | DAC unit sinks, 2.5 µA each |
| XS0…XS5 | nfet_g5v0d10v5 | 1 × 1 × same | 0.5 µm | DAC switches (en, c0…c4) |
| XMREF | pfet_g5v0d10v5 | 40 (2 × 20) × 1 | 2 µm | reference diode (1 unit) |
| XMOUT | pfet_g5v0d10v5 | 40 (2 × 20) × 25 | 2 µm | output mirror (25 units) |
| xrf (20 segments) | res_xhigh_po_0p35 | 0.35 | 87.48 µm each | $R_F$ = 10 MΩ |
| XCF | cap_mim_m3_1 | 30 × 30 × 4 | — | $C_F$ = 7.3 pF (over MOUT) |
| XPREP / XUREP | pfet_01v8 1/0.15 / nfet_g5v0 1/4 | | | clamp replica (sets vcl) |
| XPSEN / XRS | pfet_01v8 1/0.15 / xhigh_po_0p35 56 µm | | | clamp sense, 320 kΩ |
| XNSH | nfet_01v8 | 20 (4 × 5) | 0.15 µm | clamp shunt |
| XTGN / XTGP / XRINJ | g5v0 2/0.5 / xhigh_po_0p35 3.39 µm | | | VTEST injection, 20 kΩ |

Every device passes `tools/pdk_limits.py`. tt code 0/10/31: 0.71 / 1.34 / 2.67 mA (after the 15 Nov correction, NBASE 11); over 5 corners × VDDA 2.97–3.63 V
× IBIAS 4–6 µA: code 31 ≥ 2.20 mA (needs 2.02), code 0 ≤ 1.02 mA (needs 0.97 — the 50 µA excess at ff/−40 °C/IBIAS
6 µA is ≈ 60 MHz, inside the ±75 MHz fine-tune range). Ring node ≤ 1.793 V in the worst case. Output noise 8.9 pA/√Hz at
1 MHz (needs ≤ 10.3); CCO jitter 0.70 / 0.44 ps, system 1.96 / 1.27 ps, L(300 kHz) −110.9 / −120.0 dBc/Hz.
Supply → current ≤ 0.25 µA/mV. Level shifter: full 3.63 V swing, rise 1.4–1.6 ns. Full report: `docs/design/step75_cco.md`.
""")
b.qa(QA75, 75)

# ------------------------------------------------------------------------------------------------ step 76
V76 = r"""
import json
import numpy as np
from IPython.display import Image, display
D = lambda n: json.load(open("../design/refbuf/data/" + n))
nz, sim, tn = D("step76_noise.json"), D("step76_sim.json"), D("step76_tnoise.json")
"""
b.step(76, "REF buffer (REF_IN receiver): low-noise edge", "schematic")
b.md(r"""
### What happens
The crystal oscillator's waveform arrives on the REF_IN pad: anything from a 0.4 V pp sine to a 0–3.3 V square wave.
The receiver AC-couples it, amplifies it around its own switching point and delivers a 1.8 V CMOS edge, `refclk`, to the
clock generator. Every bit of noise at the moment of the crossing moves the edge in time; inside the loop bandwidth
that timing error reaches the output multiplied by $N = 32$ in phase ($N^2$ = +30 dB in power).

### How it happens
Noise $v_n$ at a crossing of slope $s$ shifts the edge by $v_n/s$:
$$\sigma_t = \frac{\sigma_v}{s},\qquad s = \pi f_{ref} V_{pp}\ \text{(sine)},\qquad
\mathcal{L}_{floor} = \frac{(2\pi f_{ref}\,\sigma_t)^2}{f_{ref}} .$$
The receiver's own white noise $S_w$ is integrated over an effective bandwidth $B_{eff}$ (about S1's gain-bandwidth):
$\sigma_v^2 \approx S_w B_{eff}$. The first stage S1 is a current-reuse inverter (XN1/XP1, 120 µm each) fed by a 60 µA
header current source; $R_B$ = 5 MΩ from its output to its input biases it exactly at its trip point, $C_{AC}$ = 3.6 pF
couples the signal in, $C_H$ = 1.8 pF makes the header node an AC ground so both devices add $g_m$.

### Why it happens this way
Jitter per edge is set by noise per unit of input slope, so a steep input is the cheapest fix: a full-swing input is
3.3× steeper than 1 V pp and gives 10 dB less phase noise. On chip, lower noise costs $g_m$, i.e. current: moderate
inversion behind a current source gives the most $g_m$ per µA, and $C_H$ lets the pMOS contribute too.

**Methods used:** M10 (bias point), M14 (noise at the crossing point), M15 (transient-noise jitter), M16 (large-signal
transient, supply sensitivity, start-up), M9 (system budget), M4/M5 (LVS, drawing checks). `docs/methods.md`.
""")
b.md("**Figure 76.1 — receiver phase noise vs input amplitude.** Slider: amplitude of the 50 MHz sine at the pad.")
b.code(V76 + r"""
fl = nz["fL"]
def frame(v):
    k = str(v)
    return ([dict(x=fl, y=nz["L"][k], name=f"receiver, {k} V pp", line=dict(color="#2a78d6")),
             dict(x=fl, y=[-155]*len(fl), name="step-72 allocation", line=dict(color="#e87ba4", dash="dot"))],
            f"{k} V pp: σ = {nz['sigma'][k]['abs']*1e12:.2f} ps per edge — system {nz['sys'][k]['false']['total_ps']:.2f} / "
            f"{nz['sys'][k]['true']['total_ps']:.2f} ps, L(300 kHz) {nz['sys'][k]['false']['L300k']:.1f} / {nz['sys'][k]['true']['L300k']:.1f} dBc/Hz")
def lay(fig):
    fig.update_xaxes(type="log", title_text="offset (Hz)"); fig.update_yaxes(title_text="L at 50 MHz (dBc/Hz)", range=[-170, -135])
show(sweep([0.4, 1.0, 3.3], frame, "V_pp", fmt="{}", active=2, layout=lay))
""")
b.md("**Figure 76.2 — transient-noise edge times (method M15).** Each point is one `refclk` rising edge; the spread is the per-edge jitter.")
b.code(V76 + r"""
fig = go.Figure()
for r, c in zip([r for r in tn["runs"] if r["Sw"] > 0], ("#2a78d6", "#1baf7a", "#eb6834")):
    x = np.array(r["dev"]); k = np.arange(len(x)); x = x - np.polyval(np.polyfit(k, x, 4), k)
    fig.add_trace(go.Scatter(y=x*1e12, mode="lines", name=f"{r['vpp']} V pp (σ {x.std()*1e12:.2f} ps)", line=dict(color=c, width=1)))
fig.update_layout(height=400, xaxis_title="edge number", yaxis_title="deviation from the ideal grid (ps)")
show(fig)
""")
b.md("**Figure 76.3 — delay, duty and supply current over corners and amplitudes** (drawn circuit with PDK passives). Hover for the condition.")
b.code(V76 + r"""
fig = make_subplots(rows=1, cols=3, subplot_titles=("delay pad → refclk (ns)", "duty (%)", "power (mW)"))
lab = [f"{r['corner']}/{r['temp']}°C/{r['vdda']} V/{r['vpp']} V pp {r['wave']}/{r['f']/1e6:.0f} MHz/VDDL {r['vddl']}" for r in sim["tran"]]
for i, (k, sc) in enumerate((("delay", 1e9), ("duty", 100), ("power", 1e3))):
    fig.add_trace(go.Scatter(x=list(range(len(lab))), y=[r[k]*sc for r in sim["tran"]], mode="markers", text=lab,
                             marker=dict(color="#2a78d6", size=7), showlegend=False), row=1, col=i + 1)
fig.add_hline(y=45, line_dash="dot", line_color="#eb6834", row=1, col=2)
fig.update_xaxes(title_text="condition #"); fig.update_layout(height=400)
show(fig)
""")
b.md("**The schematics** (receiver top → S1 cell, R_B cell, level shifter from step 75; LVS-clean against the simulated netlist).")
b.code(r"""
from IPython.display import Image, display
for n in ("refbuf", "refbuf_s1", "refbuf_rb"):
    print("sspll_" + n); display(Image(filename=f"../docs/img/step76_sch_{n}.png", width=900))
""")
b.md(r"""
### Sizing table and results
| Device | Model | W per finger × nf × m | L | Role |
|---|---|---|---|---|
| XRPU / XRPD | res_xhigh_po_0p35 | 0.35 | 87.48 µm | pad divider, 500 kΩ each |
| XCAC | cap_mim_m3_1 | 30 × 30 µm × 2 | — | $C_{AC}$ = 3.6 pF (bottom plate on the pad) |
| xrb (10 segments) | res_xhigh_po_0p35 | 0.35 | 87.48 µm | $R_B$ = 5 MΩ |
| XPD / XPH | pfet_g5v0d10v5 | 2 × 1 × (1 / 24) | 4 µm | bias diode / header (60 µA) |
| XCH | cap_mim_m3_1 | 30 × 30 µm | — | $C_H$ = 1.8 pF |
| XP1 / XN1 | p/nfet_g5v0d10v5 | 10 × 12 | 1 µm | S1, moderate inversion; XP1 body = source |
| XPEN / XNS1 | p/nfet_g5v0d10v5 | 2 × 1 | 0.5 µm | enable |
| XP2 / XN2 | p/nfet_g5v0d10v5 | 2 / 1 | 0.5 µm | S2 (VDDA) |
| XPL / XNL | p/nfet_g5v0d10v5 | 2 / 1 | 0.5 µm | 3.3 → 1.8 V inverter on VDDL |
| XPB, XPB2 / XNB, XNB2 | p/nfet_01v8 | 4 / 1 | 0.15 µm | output NOR |

Per-edge jitter 0.23 / 0.61 / 1.15 ps at 3.3 / 1.0 / 0.4 V pp; system at 3.3 V pp 1.95 / 1.26 ps, L(300 kHz)
−111.0 / −120.7 dBc/Hz (FFNC off / on). Full report: `docs/design/step76_refbuf.md`.
""")
b.qa(QA76, 76)

# ------------------------------------------------------------------------------------------------ step 77
V77 = r"""
import json
import numpy as np
from IPython.display import Image, display
D = lambda n: json.load(open("../design/clkgen/data/" + n))
sim, wv = D("step77_sim.json"), D("step77_wave.json")
"""
b.step(77, "Clock generator: sampling clocks, hold pulse, Gm pulse", "schematic")
b.md(r"""
### What happens
Every reference period the sub-sampling phase detector does three things in a fixed order: it **samples** the VCO on
C1 (the sampling switch opens), **converts** the sample into charge with a short Gm current pulse of width $\tau$ (the Gm
reads C1), and then **transfers** the sample to C2 for the NCB (the hold switch closes for $W_H$). *(Order revised in
step 78: reading C2 after the C1–C2 charge sharing would have put a pole z = 0.5 into the loop.)* The clock generator turns the single `refclk` edge into
these three phases — three complementary pairs cks/cksb, ckh/ckhb, ckg/ckgb — and guarantees that they never overlap.

### How it happens
Inverter chains make the small delays (the non-overlap gaps); an **RC pulser** makes each pulse. Its output is the
input AND its own R-C-delayed copy, so a rising edge gives one pulse as long as the RC delay plus the gates:
$$\text{out} = \overline{\overline{\text{in}} + \overline{\text{in}_{RC}}} = \text{in}\cdot\text{in}_{RC},\qquad
\tau \approx \ln 2\,R\,C + t_{gates}$$
The hold pulse is fired by the *end* of the Gm pulse through a small NOR latch (set by ckg, reset while refclk is
low), so the order can never break and the hold pulser's RC is reset for ~10 ns every period. The loop sees the delay from the
sampling instant to the middle of the Gm pulse and the phase-detector gain set by the pulse width:
$$t_p = t_{gap1} + \frac{\tau}{2},\qquad \beta = 2A\,g_m\frac{\tau}{T}$$
Only the sampling edge carries noise into the loop (the later edges act on a sample already taken). Its per-edge
jitter makes a white floor at the reference; in a transient we reproduce each inverter's noise with a trnoise current
of amplitude NA:
$$\mathcal{L}_{floor} = \frac{(2\pi f_{ref}\,\sigma_t)^2}{f_{ref}},\qquad NA = \sqrt{\frac{S_i}{2\,NT}}$$

### Why it happens this way
The sampling path is the shortest (5 stages) with the strongest drivers because it is the only one whose noise reaches
the output. $\tau$ is set mostly by gates, not by the resistor: gate delay grows when transistors are slow — exactly
when the ring VCO's gain $K_{VCO}$ falls — so $\beta K_{VCO}$ is compensated (×0.86–1.21) although $\tau$ alone spreads
106–408 ps. When `pll_en` = 0 refclk is held low: cks = 1 (track), no pulses — the block needs no enable pin.

**Methods used:** M16 (large-signal transient over 21 conditions incl. the combined MOS + R/C corners), M17 (transient
noise with per-node noise currents at the trip level), M9 (system budget), M4/M5 (LVS, drawing checks). `docs/methods.md`.
""")
b.md("**Figure 77.1 — the three phases at tt, 27 °C.** Zoom on the first nanoseconds to see the gaps.")
b.code(V77 + r"""
t = np.array(wv["t"])*1e9
fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03)
for i, (k, c) in enumerate((("refclk", "#59636e"), ("cks", "#2a78d6"), ("ckh", "#1baf7a"), ("ckg", "#eb6834"))):
    fig.add_trace(go.Scatter(x=t, y=wv[k], name=k, line=dict(color=c, width=1.6)), row=i + 1, col=1)
    fig.update_yaxes(title_text=k + " (V)", row=i + 1, col=1)
fig.update_xaxes(title_text="time (ns)", row=4, col=1); fig.update_layout(height=560)
show(fig)
""")
b.md("**Figure 77.2 — timing over 21 conditions** (corners, temperature, VDDL, f_ref, duty, refclk edge). Dashed lines: requirements. Hover for the condition.")
b.code(V77 + r"""
T = sim["timing"]
lab = [f"{a['corner']} {a['temp']}°C {a['vdd']} V {a['f']/1e6:.0f} MHz duty {a['duty']} tr {a['tr']*1e12:.0f} ps" for a in T]
fig = make_subplots(rows=1, cols=4, subplot_titles=("τ (ps)", "W_H (ns)", "t_p (ns)", "min gap (ps)"))
for i, (f, req) in enumerate(((lambda a: a["tau"]*1e12, None), (lambda a: a["W_H"]*1e9, 1.5),
                              (lambda a: a["t_p"]*1e9, 5), (lambda a: min(a["gap1"], a["gap2"])*1e12, 100))):
    fig.add_trace(go.Scatter(x=list(range(len(T))), y=[f(a) for a in T], mode="markers", text=lab,
                             marker=dict(color="#2a78d6", size=7), showlegend=False), row=1, col=i + 1)
    if req: fig.add_hline(y=req, line_dash="dot", line_color="#eb6834", row=1, col=i + 1)
fig.update_xaxes(title_text="condition #"); fig.update_layout(height=380)
show(fig)
""")
b.md("**Figure 77.3 — τ·K_VCO compensation.** τ from this step, K_VCO from step 74 (relative to tt). The loop needs the product, not τ alone. Hover the bars.")
b.code(V77 + r"""
T = {f"{a['corner']} {a['temp']}": a["tau"] for a in sim["timing"] if a["f"] == 5e7 and a["duty"] == 0.5 and a["tr"] == 3e-10}
tn = sim["timing"][0]["tau"]
rows = [("ss 110", 0.684), ("ss_hh 110", 0.684), ("tt 27", 1.0), ("ff -40", 1.485), ("ff_ll -40", 1.485)]
x = [r[0] + " °C" for r in rows]; tr = [T[r[0]]/tn for r in rows]; kr = [r[1] for r in rows]
fig = go.Figure([go.Bar(x=x, y=tr, name="τ / τ_tt", marker_color="#59636e"),
                 go.Bar(x=x, y=kr, name="K_VCO / K_tt", marker_color="#1baf7a"),
                 go.Bar(x=x, y=[a*b for a, b in zip(tr, kr)], name="product", marker_color="#2a78d6")])
fig.add_hrect(y0=0.75, y1=1.25, fillcolor="#2a78d6", opacity=0.07, line_width=0)
fig.update_layout(barmode="group", height=400, yaxis_title="relative to tt", bargap=0.25)
show(fig)
""")
b.md(r"""**Figure 77.4 — jitter of the sampling edge (method M17).** Each inverter's trip-point noise current, the
measured σ and the floor it makes at 50 MHz.""")
b.code(V77 + r"""
j = sim["jitter"]
print("noise current at the trip point:", {k: f"{np.sqrt(v)*1e12:.2f} pA/rtHz" for k, v in j["S"].items()})
print(f"edges {j['n']}: sigma raw {j['sigma_raw']*1e12:.2f} ps (numerical drift), detrended {j['sigma']*1e12:.3f} ps, "
      f"noiseless baseline {j['baseline']*1e12:.4f} ps")
print(f"floor at 50 MHz: {j['L_floor']:.1f} dBc/Hz (allocation -160)")
s = np.logspace(-14, -11.5, 60); L = 10*np.log10((2*np.pi*5e7*s)**2/5e7)
fig = go.Figure([go.Scatter(x=s*1e12, y=L, name="L = (2π f σ)² / f", line=dict(color="#2a78d6")),
                 go.Scatter(x=[j["sigma"]*1e12], y=[j["L_floor"]], mode="markers", name="clock generator",
                            marker=dict(size=11, color="#eb6834"))])
fig.add_hline(y=-160, line_dash="dot", line_color="#e87ba4")
fig.update_xaxes(type="log", title_text="per-edge jitter σ (ps)"); fig.update_yaxes(title_text="floor (dBc/Hz)")
fig.update_layout(height=380); show(fig)
""")
b.md("**The schematics** (top → RC pulser → complementary driver; LVS-clean against the simulated netlist).")
b.code(r"""
from IPython.display import Image, display
for n in ("clkgen", "ckg_pulse_h", "ckg_hlatch", "ckg_drv"):
    print("sspll_" + n); display(Image(filename=f"../docs/img/step77_sch_{n}.png", width=900))
""")
b.md(r"""
### Sizing table and results
| Device | Model | W per finger × nf | L | Role |
|---|---|---|---|---|
| INVS (n / p) | nfet_01v8 / pfet_01v8 | 0.42 / 0.84 × 1 | 0.15 µm | gap and pulser inverters |
| INVM (n / p) | nfet_01v8 / pfet_01v8 | 1 / 2 × 1 | 0.15 µm | refclk buffer, driver middle stage |
| INVL (n / p) | nfet_01v8 / pfet_01v8 | 2 / 4 × 2 | 0.15 µm | driver outputs |
| NOR2 (n / p) | nfet_01v8 / pfet_01v8 | 0.84 / 1.68 × 1 | 0.15 µm | pulser gates, 3-NOR hold latch |
| R_H / C_H | res_xhigh_po_0p35 / cap_mim_m3_1 | 0.35 × 6 µm / 6 × 6 µm | — | 34.9 kΩ, 76 fF: hold pulse 2.15 ns |
| R_G / C_G | res_xhigh_po_0p35 / cap_mim_m3_1 | 0.35 × 0.5 µm / 3.5 × 3.5 µm | — | 3.48 kΩ, 27 fF: Gm pulse 202 ps |

tt: $t_s$ 228 ps, gaps 171 / 318 ps, $\tau$ 200 ps, $W_H$ 2.16 ns, $t_p$ 0.28 ns, 82 µW, jitter 0.15 ps (−163.4 dBc/Hz).
Worst: $t_p$ 0.50 ns, $W_H$ 1.51 ns, gap 110 ps. (Revised in step 78; the first version had $t_p$ = 2.63 ns.) System (3.3 V pp): 1.963 / 1.254 ps, L(300 kHz) −110.9 / −121.0 dBc/Hz.
Full report: `docs/design/step77_clkgen.md`; testbenches: `docs/testbench_guide.md`, step 77.
""")
b.qa(QA77, 77)

# ------------------------------------------------------------------------------------------------ step 78
V78 = r"""
import json
import numpy as np
from IPython.display import Image, display
D = lambda n: json.load(open("../design/sspd/data/" + n))
ch, kk, jj = D("step78_char.json"), D("step78_kick.json"), D("step78_jitter.json")
"""
b.step(78, "SSPD with hold: sampler, dummy sampler, isolation buffers", "schematic")
b.md(r"""
### What happens
At every reference edge the sub-sampling phase detector freezes the VCO waveform on a capacitor C1. Near lock the
frozen voltage is proportional to the time between the VCO zero crossing and the reference edge — that is the phase
error, measured with no divider. Right after the sample the pulsed Gm (step 79) reads v1p − v1m; then the sample is
shared onto C2, which holds it for a whole period for the NCB.

### How it happens
Per side: the VCO output (clkp) → two **isolation inverters** → a series resistor $R_s$ → node f → the **sampling
switch** onto C1 (35 fF) and, on the opposite phase, a **dummy sampler** onto CD. $R_s$ and C1 round the square into
a near-sine whose slope at the crossing is exactly $(V_{DD}/2)/\tau_s$, so the gain per side in volts per radian is
$$A = \frac{1}{\omega_0}\left.\frac{dv}{dt}\right|_{cross} = \frac{V_{DD}}{2\,\omega_0\,\tau_s},\qquad
\tau_s = (R_s + R_{buf} + R_{sw})\,C_{1,tot}$$
After the Gm pulse, the hold switch shares C1 with C2, which keeps a memory of the previous value:
$$v_2[k] = (1-\alpha)\,v_1[k] + \alpha\,v_2[k-1],\qquad \alpha = \frac{C_{2,tot}}{C_{1,tot} + C_{2,tot}}$$
The sampled kT/C noise, divided by the gain, is a white phase floor that is **not** multiplied by N²:
$$\mathcal{L}_{kT/C} = \frac{kT}{2\,C\,A^2 f_{ref}}$$

### Why it happens this way
- The RC near-sine gives a gain set by R·C with a linear range of ±0.7 rad; a raw square would give an
  inverter-dependent slope linear over picoseconds. kT/C does not depend on R.
- **The Gm reads C1, not C2.** Reading after the sharing would put the pole z = α ≈ 0.5 inside the PLL loop
  (16° of phase lag at f_c = f_ref/20). Step 77's clock order was changed for this.
- The dummy keeps the buffer's load — and its supply current — the same in every phase: no ripple at f_ref on the LDO.
- 35 fF instead of 100 fF saves a third of the power; kT/C stays 15 dB under the reference at the output.

**Methods used:** M18 (beat-frequency characteristic), M19 (kick-back by difference of two transients), M17 (isolation
buffer jitter), M9 (system budget), M4/M5 (LVS, drawing checks). `docs/methods.md`.
""")
b.md("**Figure 78.1 — the sampled characteristic** (beat run, tt). Slider: how far from the lock point the line fit reaches; the slope of the fit is 2A.")
b.code(V78 + r"""
tt = ch[0]; r = np.array(tt["rows"]); d = (r[:, 1] - tt["phi0"] + np.pi) % (2*np.pi) - np.pi; o = np.argsort(d)
def frame(w):
    m = np.abs(d) < w; s = np.polyfit(d[m], r[m, 2], 1)[0]
    x = np.linspace(-w, w, 2)
    return ([dict(x=d[o], y=r[o, 2], name="v1p − v1m (Gm reads this)", mode="lines+markers", line=dict(color="#2a78d6")),
             dict(x=d[o], y=r[o, 3], name="v2p − v2m (held for the NCB)", mode="markers", marker=dict(color="#eb6834", size=6)),
             dict(x=x, y=s*x, name="line fit", line=dict(color="#1f2328", dash="dash"))],
            f"fit over ±{w} rad: 2A = {s:.3f} V/rad → A = {s/2:.3f} V (the gain falls as the fit leaves the linear part)")
def lay(fig):
    fig.update_xaxes(title_text="VCO phase at the sample, relative to lock (rad)"); fig.update_yaxes(title_text="V")
show(sweep([0.2, 0.35, 0.7, 1.0, 1.5], frame, "fit half-width (rad)", fmt="{}", active=1, layout=lay))
""")
b.md("**Figure 78.2 — A, common mode and power over 17 conditions** (combined MOS + R/C corners). Hover for the condition.")
b.code(V78 + r"""
lab = [f"{c['corner']} {c['temp']}°C {c['vdd']} V {c['fref']/1e6:.0f} MHz" for c in ch]
fig = make_subplots(rows=1, cols=3, subplot_titles=("A (V/rad); floor 0.35", "common mode of v1 (V)", "power (mW)"))
for i, (k, sc) in enumerate((("A", 1), ("cm", 1), ("power", 1e3))):
    fig.add_trace(go.Scatter(x=list(range(len(ch))), y=[c[k]*sc for c in ch], mode="markers", text=lab,
                             marker=dict(color="#2a78d6", size=8), showlegend=False), row=1, col=i + 1)
fig.add_hline(y=0.35, line_dash="dot", line_color="#eb6834", row=1, col=1)
fig.add_hline(y=0.5, line_dash="dot", line_color="#59636e", row=1, col=1)
fig.update_xaxes(title_text="condition #"); fig.update_layout(height=380)
show(fig)
""")
b.md("**Figure 78.3 — kick-back and the dummy sampler (method M19).** Left: how much the sampler moves each clkp edge. Right: SSPD supply current at f_ref.")
b.code(V78 + r"""
fig = make_subplots(rows=1, cols=2, column_widths=[0.65, 0.35],
                    subplot_titles=(f"clkp edge shift: max {kk['dt_max']*1e15:.1f} fs, spur ≈ {kk['spur_dbc']:.0f} dBc", "f_ref current (µA)"))
fig.add_trace(go.Scatter(x=kk["wave"]["dt_edges"], y=kk["wave"]["dt"], mode="markers", marker=dict(color="#2a78d6", size=6),
                         showlegend=False), row=1, col=1)
fig.add_trace(go.Bar(x=["with dummy", "without dummy"], y=[kk["I_fref"]*1e6, kk["I_fref_nodummy"]*1e6],
                     marker_color=["#1baf7a", "#eb6834"], showlegend=False), row=1, col=2)
fig.update_yaxes(type="log", row=1, col=2); fig.update_xaxes(title_text="time (ns)", row=1, col=1)
fig.update_yaxes(title_text="fs", row=1, col=1); fig.update_layout(height=360)
show(fig)
print(f"isolation-buffer jitter (M17): {jj['sigma']*1e12:.3f} ps per side, {jj['sigma']/np.sqrt(2)*1e12:.3f} ps differential, "
      f"baseline {jj['baseline']*1e12:.4f} ps")
""")
b.md("**Figure 78.4 — what kT/C costs.** Slider: the sampling capacitance. The floor is far below the reference contribution (×N²) at the output.")
b.code(V78 + r"""
kT = 1.380649e-23*300; A = ch[0]["A"]
def frame(C):
    C = C*1e-15; L = 10*np.log10(kT/(2*C*A**2*50e6)); f = np.logspace(4, 7.4, 50)
    return ([dict(x=f, y=[L]*len(f), name="SSPD kT/C (not ×N²)", line=dict(color="#2a78d6")),
             dict(x=f, y=[-163.4 + 30.1]*len(f), name="clock-generator edge ×N²", line=dict(color="#eb6834", dash="dot"))],
            f"C = {C*1e15:.0f} fF: kT/C floor {L:.1f} dBc/Hz, {(-133.3) - L:.1f} dB under the clock generator alone")
def lay(fig):
    fig.update_xaxes(type="log", title_text="offset (Hz)"); fig.update_yaxes(title_text="dBc/Hz at the output", range=[-155, -125])
show(sweep([20, 35, 46, 70, 100], frame, "C (fF)", fmt="{}", active=2, layout=lay))
""")
b.md("**The schematics** (top → one side → transmission gate; LVS-clean against the simulated netlist).")
b.code(r"""
from IPython.display import Image, display
for n in ("sspd", "sspd_side", "sspd_tg"):
    print("sspll_" + n); display(Image(filename=f"../docs/img/step78_sch_{n}.png", width=900))
""")
b.md(r"""
### Sizing table and results
| Device | Model | W per finger × nf | L | Role |
|---|---|---|---|---|
| XB1 (n / p) | nfet_01v8 / pfet_01v8 | 0.42 / 0.84 × 1 | 0.15 µm | isolation buffer input (~2 fF on clkp) |
| XB2 (n / p) | nfet_01v8 / pfet_01v8 | 2 / 4 × 1 | 0.15 µm | drives $R_s$ + C |
| XRS | res_xhigh_po_0p69 | 0.69 | 0.6 µm | $R_s$ = 2.16 kΩ |
| sampling / dummy TG | nfet_01v8_lvt / pfet_01v8 | 3 / 1.5 × 1 | 0.15 µm | lvt nMOS: the signal sits mid-rail |
| hold TG | nfet_01v8_lvt / pfet_01v8 | 1 / 1 × 1 | 0.15 µm | C1 → C2 |
| XC1, XC2 / XCD | cap_mim_m3_1 | 4 × 4 / 4.35 × 4.35 µm | — | 34.7 fF / 40.7 fF (= C1 + Gm input) |

A = 0.514 V/rad (0.35–0.77 over corners, ±1.5 % over temperature), α = 0.473, kick-back ≤ 2.3 fs (spur ≤ −134 dBc),
supply current at f_ref 0.76 µA (42 µA without the dummy), buffer jitter 0.080 ps (−169 dBc/Hz), 0.47 mW. System:
1.964 / 1.256 ps, L(300 kHz) −110.9 / −120.9 dBc/Hz. Power is above the step-72 allocation (power review after step 82).
Full report: `docs/design/step78_sspd.md`; testbenches: `docs/testbench_guide.md`, step 78.
""")
b.qa(QA78, 78)
b.save(os.path.join(os.path.dirname(__file__), "..", "phase7_design.ipynb"))
