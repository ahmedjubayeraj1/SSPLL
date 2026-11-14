"""Phase 7 - block design. Step 72: phase-noise, jitter, power and area budget per block."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nb import Book
from qa72 import QA72

b = Book("Phase 7 — Step 72: the noise, power and area budget per block",
         "Phases 1–6 explained *why* each block exists. Phase 7 designs them — and the first design step is to decide how "
         "much each block is allowed to cost: jitter, power and area. This notebook splits the proposal's targets "
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
b.save(os.path.join(os.path.dirname(__file__), "..", "phase7_step72_budget.ipynb"))
