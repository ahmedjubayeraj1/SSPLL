#!/usr/bin/env python3
"""ncb_hv_plots.py - figures of the noise-cancellation block: docs/img/ncb_hv_*.png. Run ncb_hv_sim.py first."""
import os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ncb_hv_sim as S
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
P = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#8a63d2"]
INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
IMG = os.path.join(ROOT, "docs", "img")
d = S.load()


def style(ax, title):
    ax.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_title(title, loc="left", color=INK, fontsize=10)


# 1 --- K_d against the code, per condition, with the required K_d of each condition
SEL = ["tt 27 °C, 3.3 V", "ss_hh 110 °C, 2.97 V", "ss_hh -40 °C, 2.97 V", "ff_ll -40 °C, 3.63 V", "ff_ll 110 °C, 3.63 V"]
fig, ax = plt.subplots(1, 3, figsize=(12.5, 3.8))
cov = {r["cond"]: r for r in d["coverage"]}
for k, name in enumerate(SEL):
    rows = sorted([r for r in d["A"] if r["cond"] == name], key=lambda r: r["code"])
    ax[0].plot([r["code"] for r in rows], [r["Kd"]*1e12 for r in rows], "o-", color=P[k], lw=1.6, ms=4, label=name)
    ax[0].axhline(cov[name]["kreq"]*1e12, color=P[k], ls=":", lw=1)
    ax[1].plot([r["code"] for r in rows], [r["td"]*1e12 for r in rows], "o-", color=P[k], lw=1.6, ms=4)
ax[0].set_xlabel("gain code"); ax[0].set_ylabel("K_d = −dt/dvff (ps/V)"); ax[0].legend(frameon=False, fontsize=7.5)
style(ax[0], "NCB gain against the code (dotted: required)")
ax[1].set_xlabel("gain code"); ax[1].set_ylabel("delay in → out (ps)"); style(ax[1], "Delay of the line")
C = d["calibration"]
x = np.arange(len(C))
ax[2].bar(x, [r["err"]*100 for r in C], color=P[0], width=0.55, label="at 27 °C, nominal VDDA (code chosen here)")
for i, r in enumerate(C):
    for q in r["drift"]:
        ax[2].plot(i, q["err"]*100, "o", color=P[1] if abs(q["err"]) > 0.3 else P[3], ms=6)
ax[2].plot([], [], "o", color=P[3], label="same code at −40 / 110 °C, VDDA ±10 %")
ax[2].axhline(30, color=MUTED, ls=":", lw=0.8); ax[2].axhline(-30, color=MUTED, ls=":", lw=0.8)
ax[2].set_xticks(x); ax[2].set_xticklabels([r["cond"].split(" ")[0] + f"\ncode {r['code']}" for r in C], fontsize=7.5)
ax[2].set_ylabel("FFNC gain error (%)"); ax[2].set_ylim(-45, 42); ax[2].legend(frameon=False, fontsize=7, loc="upper center")
style(ax[2], "Calibrated once at 27 °C, then drift (±30 %: budget)")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "ncb_hv_gain.png"), dpi=150); plt.close(fig)

# 2 --- control path noise and the delay vs VDDA summary
if "D" in d:
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for k, r in enumerate(d["D"]):
        f = np.array(r["f"])
        ax[0].loglog(f, np.array(r["vin_nb"])*1e9, color=P[k], lw=1.6, label=f"{r['cond']} (nb)")
        ax[0].loglog(f, np.array(r["vin_pd"])*1e9, color=P[k], lw=1.0, ls="--")
    ax[0].set_xlim(1e3, 1e9); ax[0].set_xlabel("frequency (Hz)"); ax[0].set_ylabel("bias noise referred to vff (nV/√Hz)")
    ax[0].legend(frameon=False, fontsize=7.5); style(ax[0], "Bias-path noise (solid nb, dashed pd)")
    ks = d.get("C", [])
    ax[1].bar(range(len(ks)), [r["Ks"]*1e12 for r in ks], color=P[0])
    ax[1].set_xticks(range(len(ks))); ax[1].set_xticklabels([r["cond"].replace(" °C, ", "/").replace(" V", "") for r in ks],
                                                           rotation=30, fontsize=7.5)
    ax[1].set_ylabel("d(delay)/dVDDA (ps/V)"); style(ax[1], "Delay against VDDA (vff fixed)")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "ncb_hv_noise.png"), dpi=150); plt.close(fig)
print("figures written")
