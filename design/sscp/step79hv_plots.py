#!/usr/bin/env python3
"""step79hv_plots.py - figures of the step-79 report (docs/img/step79hv_*.png). Runs four quick DC sweeps (tt, the trim
codes) for the transfer curves; everything else comes from data/step79hv_sim.json and step79hv_noise.json."""
import os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sscp_hv as C
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); IMG = os.path.join(ROOT, "docs", "img")
P = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]; INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
def style(ax, t):
    ax.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_title(t, loc="left", color=INK, fontsize=10)

S = json.load(open(os.path.join(HERE, "data", "step79hv_sim.json"))); N = json.load(open(os.path.join(HERE, "data", "step79hv_noise.json")))
CODES = {"10 (2 slices)": (1, 1, 0, 0, 0), "00 (3 slices)": (1, 1, 1, 0, 0), "01 (4 slices)": (1, 1, 1, 1, 0), "11 (5 slices)": (1, 1, 1, 1, 1)}

# 1. DC transfer (tt, codes) and G over the conditions
fig, ax = plt.subplots(1, 2, figsize=(12, 4.3), gridspec_kw=dict(width_ratios=[1.1, 1]))
for (nm, en), col in zip(CODES.items(), P):
    r = C.dc_transfer(en=en, cm=3.3*0.503)
    v, i = np.array(r["v"]), -np.array(r["i"])          # current INTO vctl (the filter)
    ax[0].plot(v, i*1e6, color=col, lw=1.6, label=f"code {nm}: G {abs(r['G'])*1e6:.1f} µS")
ax[0].axhline(0, color=MUTED, lw=0.8); ax[0].axvline(0, color=MUTED, lw=0.8)
ax[0].set_xlabel("v1p − v1m (V)"); ax[0].set_ylabel("current into vctl while ckg = 1 (µA)")
ax[0].legend(frameon=False, fontsize=8); style(ax[0], "DC transfer at tt, 27 °C, V_cont 1.8 V")
dc = [r for r in S["dc"] if r["code"] == "00"]
lab = [f"{r['corner']} {r['temp']}°C {r['vdda']} V, V_cont {r['vc']}" for r in dc]
y = np.arange(len(dc))
ax[1].scatter([r["G"]*1e6 for r in dc], y, color=P[0], s=22, zorder=3)
g0 = dc[0]["G"]*1e6
for f_ in (0.93, 1.07):
    ax[1].axvline(g0*f_, color=P[4], ls="--", lw=1)
ax[1].set_yticks(y, lab, fontsize=7.5); ax[1].invert_yaxis(); ax[1].set_xlabel("G (µS), code 00")
style(ax[1], "G over corners and V_cont (dashed: ±7 %)")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step79hv_dc.png"), dpi=150)

# 2. noise: output current noise and the detector-referred phase noise
fn, n = np.array(S["noise"]["f"]), np.array(S["noise"]["n"])
A, G, d = N["A"], N["G"], N["d"]
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].loglog(fn, n*1e12, color=P[0]); ax[0].set_xlabel("frequency (Hz)"); ax[0].set_ylabel("pA/√Hz")
style(ax[0], "Output current noise into vctl (Gm on, 3 slices)")
L = 10*np.log10(n**2/(4*A**2*G**2*d)/2)
ax[1].semilogx(fn, L, color=P[1], label="pulsed Gm, detector-referred (not ×N²)")
fy, yy = np.array(S["psr"]["f"]), np.array(S["psr"]["y"])
Lv = 10*np.log10(np.maximum(yy, 1e-30)**2*(100e-9)**2*(1 + 10e3/fy)/(2*A*G)**2/2)
ax[1].semilogx(fy, Lv, color=P[2], ls="--", label="VDDA 100 nV/√Hz into the Gm")
ax[1].set_xlim(1e3, 1e8); ax[1].set_ylim(-190, -120); ax[1].set_xlabel("offset (Hz)"); ax[1].set_ylabel("dBc/Hz")
ax[1].legend(frameon=False, fontsize=8); style(ax[1], "As phase noise at the detector")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step79hv_noise.png"), dpi=150)
print("plots done")
