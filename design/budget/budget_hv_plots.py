#!/usr/bin/env python3
"""budget_hv_plots.py - figures for the 800 MHz (5 V analog) budget: docs/img/budget_hv_*.png."""
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import budget_hv as b

C1, C2, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1f2328", "#59636e", "#e6e8eb"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
img = os.path.join(ROOT, "docs", "img")
SPEC = dict(off=(-114, -108), on=(-124, -116))          # proposal L(300 kHz) typ / max after this budget

# 1) jitter contribution per block, typ, FFNC off / on
f, Soff = b.spectra("typ", False); _, Son = b.spectra("typ", True)
joff, _ = b.jitter(Soff, f); jon, _ = b.jitter(Son, f)
names = sorted([k for k in jon if k != "TOTAL"], key=lambda k: max(jon[k], joff.get(k, 0)))
y = np.arange(len(names)); h = 0.38
fig, ax = plt.subplots(figsize=(8.8, 5.2))
ax.barh(y + h/2 + 0.02, [joff.get(k, 0)*1e12 for k in names], h, color=C1, label=f"FFNC off (total {joff['TOTAL']*1e12:.2f} ps)")
ax.barh(y - h/2 - 0.02, [jon[k]*1e12 for k in names], h, color=C2, label=f"FFNC on (total {jon['TOTAL']*1e12:.2f} ps)")
for i, k in enumerate(names):
    ax.text(jon[k]*1e12 + 0.02, i - h/2 - 0.02, f"{jon[k]*1e15:.0f} fs", va="center", fontsize=8, color=MUTED)
ax.set_yticks(y, names); ax.set_xlabel("rms jitter contribution, 10 kHz–40 MHz (ps)")
ax.grid(axis="x", color=GRID); ax.set_axisbelow(True)
ax.set_title("5 V analog jitter budget per block, typ, 50 MHz × 16 = 800 MHz", loc="left", color=INK, fontsize=11)
ax.legend(frameon=False, loc="lower right")
fig.tight_layout(); fig.savefig(os.path.join(img, "budget_hv_jitter_blocks.png"), dpi=150)

# 2) total phase noise, typ and pess, FFNC off / on, with the 300 kHz spec points
fig, ax = plt.subplots(figsize=(8.8, 4.6))
for corner, ls in (("typ", "-"), ("pess", "--")):
    for on, col in ((False, C1), (True, C2)):
        f, S = b.spectra(corner, on); L = 10*np.log10(sum(S.values())/2)
        ax.semilogx(f, L, ls, color=col, lw=2 if corner == "typ" else 1.4, label=f"{corner}, FFNC {'on' if on else 'off'}")
for col, (typ, mx) in ((C1, SPEC["off"]), (C2, SPEC["on"])):
    ax.scatter([3e5], [typ], marker="o", s=46, color=col, edgecolor="white", linewidth=1.5, zorder=5)
    ax.scatter([3e5], [mx], marker="v", s=52, color=col, edgecolor="white", linewidth=1.5, zorder=5)
ax.scatter([], [], marker="o", color=MUTED, label="spec typ at 300 kHz")
ax.scatter([], [], marker="v", color=MUTED, label="spec max at 300 kHz")
ax.set_xlim(1e4, 4e7); ax.set_ylim(-155, -95)
ax.set_xlabel("offset frequency (Hz)"); ax.set_ylabel("L(f) at 800 MHz (dBc/Hz)")
ax.grid(True, which="major", color=GRID); ax.set_axisbelow(True)
ax.set_title("Budgeted output phase noise (800 MHz) vs the 300 kHz spec", loc="left", color=INK, fontsize=11)
ax.legend(frameon=False, ncol=3, loc="lower left", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(img, "budget_hv_phase_noise.png"), dpi=150)
print("figures written")
