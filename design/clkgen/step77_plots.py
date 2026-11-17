#!/usr/bin/env python3
"""step77_plots.py - figures of the step-77 report (docs/img/step77_*.png) and the waveform data for the notebook."""
import os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import clkgen as C
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); IMG = os.path.join(ROOT, "docs", "img")
P = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]; INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
def style(ax, t):
    ax.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_title(t, loc="left", color=INK, fontsize=10)

wf = os.path.join(HERE, "data", "step77_wave.json")
if not os.path.exists(wf):
    T = 20e-9
    net = (f"* wave\n.lib {C.LIB} tt\n.temp 27\n{C.cells()}vdd VDD 0 1.8\n"
           f"vin refclk 0 pulse(0 1.8 5n 375p 375p 9.625n 20n)\nx1 refclk cks cksb ckh ckhb ckg ckgb VDD 0 sspll_clkgen\n" +
           "".join(f"c{k} {k} 0 {v}\n" for k, v in C.LOADS.items()) +
           ".control\ntran 2p 70n 60n\nwrdata w.txt v(refclk) v(cks) v(ckh) v(ckg)\n.endc\n.end\n")
    _, d = C.run(net, ["w.txt"]); z = d["w.txt"]
    sel = slice(None, None, max(1, len(z)//2500))
    json.dump(dict(t=(z[sel, 0] - 60e-9).tolist(), refclk=z[sel, 1].tolist(), cks=z[sel, 3].tolist(),
                   ckh=z[sel, 5].tolist(), ckg=z[sel, 7].tolist()), open(wf, "w"))
w = json.load(open(wf)); s = json.load(open(os.path.join(HERE, "data", "step77_sim.json")))

fig, ax = plt.subplots(figsize=(12, 4.2))
t = np.array(w["t"])*1e9
for i, (k, lab) in enumerate((("refclk", "refclk (input)"), ("cks", "cks: sw1 tracks while high"),
                              ("ckh", "ckh: hold transfer"), ("ckg", "ckg: Gm pulse"))):
    ax.plot(t, np.array(w[k]) + 2.2*(3 - i), color=P[i], lw=1.6)
    ax.text(5.0, 2.2*(3 - i) + 1.95, lab, color=P[i], fontsize=8.5)
ax.axvline(5.42, color=MUTED, lw=0.8, ls=":")
ax.text(5.47, -0.55, "sampling instant: cks falls 226 ps after the refclk crossing", color=MUTED, fontsize=8)
ax.set_xlim(4.5, 9.5); ax.set_yticks([]); ax.set_xlabel("time (ns), tt, 27 °C, VDDL 1.8 V")
style(ax, "Clock generator timing: sample → (gap) → hold pulse 2.15 ns → (gap) → Gm pulse 202 ps; t_p = 2.63 ns")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step77_timing.png"), dpi=150)

tm = s["timing"]
lab = [f"{r['corner']} {r['temp']}°C {r['vdd']}V" + ("" if r["f"] == 50e6 else f" {r['f']/1e6:.0f}MHz") +
       ("" if r["duty"] == 0.5 else f" duty {r['duty']}") + ("" if r["tr"] == 300e-12 else f" tr {r['tr']*1e12:.0f}p") for r in tm]
fig, ax = plt.subplots(1, 3, figsize=(13, 5.2), sharey=True)
y = np.arange(len(tm))
for a, k, sc, lim, ttl, c in ((ax[0], "tau", 1e12, (150, 250), "Gm pulse width τ (ps)", P[0]),
                              (ax[1], "t_p", 1e9, (None, 5), "t_p (ns), limit 5 ns", P[1]),
                              (ax[2], "gap1", 1e12, (100, None), "non-overlap gaps (ps), ≥ 100", P[2])):
    a.scatter([r[k]*sc for r in tm], y, color=c, s=18, zorder=3, label="gap 1" if k == "gap1" else None)
    if k == "gap1":
        a.scatter([r["gap2"]*sc for r in tm], y, color=P[3], s=18, marker="s", zorder=3, label="gap 2")
        a.legend(frameon=False, fontsize=8, loc="lower right")
    for L_ in lim:
        if L_ is not None:
            a.axvline(L_, color=P[4], lw=1, ls="--")
    style(a, ttl)
ax[0].text(152, len(tm) - 0.6, "±25 % band", color=P[4], fontsize=8)
ax[0].set_yticks(y, lab, fontsize=7.5); ax[0].invert_yaxis()
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step77_corners.png"), dpi=150)
print("plots done")
