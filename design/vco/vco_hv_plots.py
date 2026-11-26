#!/usr/bin/env python3
"""vco_hv_plots.py - figures of the step-74 redo (5 V, 3-stage ring, 800 MHz): docs/img/vco_hv_*.png.
Run vco_hv_point.py for the variants and vco_hv_char.py hl6 first."""
import os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(HERE, "..", "..", "docs", "img")
INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"; P = ["#2a78d6", "#eb6834", "#1baf7a", "#f0a30a", "#8250df"]
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
ld = lambda n: json.load(open(os.path.join(HERE, "data", f"vco_hv_{n}.json")))
def style(ax, t):
    ax.set_title(t, loc="left", color=INK, fontsize=10.5); ax.grid(True, color=GRID); ax.set_axisbelow(True)

# 1 --- design study: thermal L and 1/f^3 corner per variant
V = [("s2", "feasibility ring ×2"), ("halftune", "half tuning"), ("hl", "+ TG nMOS L 1 µm"), ("hl3", "+ switch L 1 µm"),
     ("hl4", "N ×1.5"), ("hl5", "N ×0.5"), ("hl6", "N 6 µm, all ×1.25 (chosen)")]
D = [(lab, ld(n)) for n, lab in V if os.path.exists(os.path.join(HERE, "data", f"vco_hv_{n}.json"))]
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
y = np.arange(len(D))
ax[0].barh(y, [-d["Lth"] for _, d in D], color=P[0]); ax[0].set_yticks(y, [f"{l}\n{d['I']*1e3:.2f} mA" for l, d in D], fontsize=8)
ax[0].axvline(104.4, color=MUTED, ls=":"); ax[0].text(104.5, -0.6, "need −104.4", color=MUTED, fontsize=8)
ax[0].set_xlim(100, 107.5); ax[0].set_xlabel("−L_thermal(1 MHz) at 800 MHz (dB below carrier; larger = quieter)")
style(ax[0], "Thermal phase noise per variant (ISF, method M2)")
ax[1].barh(y, [d["fc3"]/1e6 for _, d in D], color=P[1]); ax[1].set_yticks(y, ["" for _ in D])
ax[1].axvline(0.6, color=MUTED, ls=":"); ax[1].text(0.62, -0.6, "need ≤ 0.6", color=MUTED, fontsize=8)
ax[1].set_xlabel("1/f³ corner (MHz)"); style(ax[1], "Flicker up-conversion: 1/f³ corner")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "vco_hv_variants.png"), dpi=150)

# 2 --- ISF and noise shares of the chosen cell
n = ld("hl6"); h = np.array(n["h"]); K = len(h)
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
ph = np.r_[np.arange(K), K]/K*360
ax[0].plot(ph, np.r_[h, h[0]]/1e12, "-o", color=P[0], ms=4); ax[0].axhline(np.mean(h)/1e12, color=P[1], ls="--")
ax[0].text(10, np.mean(h)/1e12 + 0.3, f"mean (flicker up-conversion) = {n['hdc_over_hrms']:.2f} × rms", color=P[1], fontsize=8)
ax[0].set_xlabel("injection phase (deg)"); ax[0].set_ylabel("ISF h (rad/pC)"); style(ax[0], "Impulse sensitivity of a ring node (hl6)")
lab = {"x1.xp2": "main pMOS", "x1.xn2": "main nMOS", "x1.xs2": "tune switch", "x1.xt1n": "TG nMOS (own)",
       "x1.xt1p": "TG pMOS (own)", "x2.xt1n": "TG nMOS (next)", "x2.xt1p": "TG pMOS (next)"}
ks = list(n["shares"]); yy = np.arange(len(ks)); hh = 0.38
ax[1].barh(yy + hh/2, [100*n["shares"][k][0] for k in ks], hh, color=P[0], label="thermal")
ax[1].barh(yy - hh/2, [100*n["shares"][k][1] for k in ks], hh, color=P[1], label="flicker")
ax[1].set_yticks(yy, [lab[k] for k in ks], fontsize=8); ax[1].set_xlabel("share of the node's phase noise (%)")
style(ax[1], "Where the noise comes from (hl6)"); ax[1].legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "vco_hv_isf.png"), dpi=150)

# 3 --- frequency vs current at corners, and vs vtune
c = json.load(open(os.path.join(HERE, "data", "vco_hv_char_hl6.json")))
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for (k, v), col in zip(c["f_vs_I"].items(), P):
    pts = [(I, f) for I, f, *_ in v if f]
    ax[0].plot([a*1e3 for a, _ in pts], [b/1e6 for _, b in pts], "-o", ms=4, color=col, label=k.replace("_", " ") + " °C")
ax[0].axhspan(720, 880, color=GRID, alpha=0.7, lw=0); ax[0].text(0.62, 890, "720–880 MHz needed", color=MUTED, fontsize=8)
ax[0].set_xlabel("ring feed current from the CCO (mA)"); ax[0].set_ylabel("f (MHz)")
style(ax[0], "Coarse tuning: frequency vs current"); ax[0].legend(frameon=False, fontsize=8)
for (k, v), col in zip(c["f_vs_vtune"].items(), P):
    pts = [(x, f) for x, f, _ in v if f]
    ax[1].plot([a for a, _ in pts], [b/1e6 for _, b in pts], "-o", ms=4, color=col, label=k.replace("_", " ") + " °C")
ax[1].axvspan(1.3, 2.3, color=GRID, alpha=0.7, lw=0)
ax[1].set_xlabel("vtune (V)"); ax[1].set_ylabel("f (MHz)"); style(ax[1], f"Fine tuning at {c['I0']*1e3:.3f} mA (V_cont window 1.3–2.3 V shaded)")
ax[1].legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "vco_hv_tuning.png"), dpi=150)
print("figures written")
