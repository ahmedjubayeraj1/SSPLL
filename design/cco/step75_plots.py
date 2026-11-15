#!/usr/bin/env python3
"""step75_plots.py - figures of the step-75 report (docs/img/step75_*.png)."""
import os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); IMG = os.path.join(ROOT, "docs", "img")
P = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]; INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
def style(ax, t):
    ax.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_title(t, loc="left", color=INK, fontsize=10)
D = lambda n: json.load(open(os.path.join(HERE, "data", n)))
s, nz = D("step75_sim.json"), D("step75_noise.json")
dc = s["dc"]

# 1. current vs code and the IBIAS / corner spread
fig, ax = plt.subplots(1, 2, figsize=(12, 3.9))
sw = [r for r in dc[90:]]
ax[0].plot([r[4] for r in sw], [-r[5]*1e3 for r in sw], "-o", color=P[0], ms=3, lw=1.8, label="tt, 27 °C, IBIAS 5 µA, VDDA 3.3 V")
ax[0].plot(range(32), [62.5e-3*(13 + k) for k in range(32)], "--", color=MUTED, lw=1, label="ideal 62.5 µA × (13 + code)")
ax[0].axhspan(0.97, 2.26, color=P[2], alpha=0.10, lw=0)
ax[0].text(0.5, 2.3, "ring needs 0.97–2.26 mA over all corners", color=P[2], fontsize=8)
ax[0].set_xlabel("cco_code"); ax[0].set_ylabel("I into ring node (mA)"); style(ax[0], "Coarse tuning: current vs code")
ax[0].legend(frameon=False, fontsize=8, loc="lower right")
for k, (ib, c) in enumerate(((4e-6, P[1]), (5e-6, P[0]), (6e-6, P[3]))):
    for code, mk in ((0, "v"), (31, "^")):
        v = [-r[5]*1e3 for r in dc[:90] if r[3] == ib and r[4] == code]
        x = np.full(len(v), k) + (0.12 if code else -0.12)
        ax[1].scatter(x, v, color=c, marker=mk, s=22, label=f"code {code}" if k == 1 else None)
ax[1].axhline(0.97, color=P[2], lw=1, ls="--"); ax[1].axhline(2.02, color=P[4], lw=1, ls="--")
ax[1].text(2.35, 1.0, "max needed at code 0\n(ff, −40 °C)", fontsize=7.5, color=P[2], va="bottom")
ax[1].text(2.35, 2.05, "min needed at code 31\n(ss, 110 °C, 10 fF)", fontsize=7.5, color=P[4], va="bottom")
ax[1].set_xticks([0, 1, 2], ["IBIAS 4 µA", "5 µA", "6 µA"]); ax[1].set_xlim(-0.5, 3.2)
ax[1].set_ylabel("I (mA), 5 corners × VDDA 2.97/3.63 V"); style(ax[1], "Range survives ±20 % IBIAS and all corners")
ax[1].legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step75_dc.png"), dpi=150)

# 2. compliance and clamp
fig, ax = plt.subplots(1, 2, figsize=(12, 3.9))
cp = np.array(s["compliance"])
ax[0].plot(cp[:, 0], -cp[:, 1]*1e3, "-o", color=P[0], ms=3, lw=1.8, label="ss, 110 °C, VDDA 2.97 V, IBIAS 4 µA, code 31")
ax[0].axvspan(1.38, 1.8, color=P[2], alpha=0.10, lw=0); ax[0].text(1.40, 0.9, "ring-node\nrange", fontsize=8, color=P[2])
ax[0].set_xlabel("ring-node voltage (V)"); ax[0].set_ylabel("I (mA)"); ax[0].set_ylim(-0.6, 2.7); ax[0].text(1.85, 0.2, "clamp sinks the\nexcess above 1.8 V", fontsize=8, color=MUTED)
style(ax[0], "Compliance at the worst headroom")
ax[0].legend(frameon=False, fontsize=8, loc="lower left")
cl = s["clamp"]
for ib, c in ((4e-6, P[1]), (6e-6, P[3])):
    r = [x for x in cl if x[0] == ib]
    ax[1].plot([x[1] for x in r], [x[2] for x in r], "-o", color=c, ms=3.5, lw=1.8, label=f"IBIAS {ib*1e6:.0f} µA")
ax[1].axhline(1.8, color=P[4], lw=1, ls="--"); ax[1].text(0.5, 1.805, "1.80 V absolute limit", color=P[4], fontsize=8, va="bottom")
ax[1].set_xlabel("cco_code"); ax[1].set_ylabel("ring node (V)"); style(ax[1], "Clamp: ss, 110 °C ring, VDDA 3.63 V")
ax[1].legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step75_clamp.png"), dpi=150)

# 3. noise and supply rejection
fig, ax = plt.subplots(1, 2, figsize=(12, 3.9))
f, n = np.array(nz["f"]), np.array(nz["n"])
ax[0].loglog(f, n*1e12, color=P[0], lw=1.8, label="complete CCO, tt, code 10 (.noise)")
ax[0].axhline(10.3, color=P[1], lw=1, ls="--"); ax[0].text(1.2e3, 11, "white-noise requirement 10.3 pA/√Hz", color=P[1], fontsize=8)
ax[0].axvspan(1e4, 4e7, color=P[2], alpha=0.06, lw=0)
ax[0].set_xlabel("offset frequency (Hz)"); ax[0].set_ylabel("output current noise (pA/√Hz)")
style(ax[0], f"Output noise: jitter {nz['off'][0]:.2f} / {nz['on'][0]:.2f} ps (FFNC off / on)")
ax[0].legend(frameon=False, fontsize=8, loc="upper right")
ps = np.array(s["psr"])
ax[1].semilogx(ps[:, 0], ps[:, 1]*1e3, color=P[0], lw=1.8, label="|ΔI / ΔVDDA|, tt, code 10")
ax[1].set_xlabel("frequency (Hz)"); ax[1].set_ylabel("mA / V  (= µA / mV)"); style(ax[1], "Supply → current (AC)")
ax[1].legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step75_noise.png"), dpi=150)
print("plots done")
