#!/usr/bin/env python3
"""step76_plots.py - figures of the step-76 report (docs/img/step76_*.png)."""
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
nz, s, tn = D("step76_noise.json"), D("step76_sim.json"), D("step76_tnoise.json")

# 1. noise: pad-referred spectrum and receiver phase noise per amplitude
fig, ax = plt.subplots(1, 2, figsize=(12, 3.9))
f = np.array(nz["f"]); w = (f > 1e3) & (f < 5e9)
ax[0].loglog(f[w], np.sqrt(np.array(nz["Sgate"])[w])*1e9, color=P[0], lw=1.8, label="gate-referred, at vin (M14)")
ax[0].loglog(f[w], np.sqrt(np.array(nz["Sgate"])[w])/nz["div50"]*1e9, color=P[1], lw=1.4, ls="--",
             label=f"referred to the pad with the 50 MHz divider ({nz['div50']:.2f})")
ax[0].axhline(np.sqrt(nz["Swg"])*1e9, color=MUTED, lw=1, ls=":")
ax[0].text(1.5e3, np.sqrt(nz["Swg"])*1e9*1.12, "white plateau (injected in M15)", color=MUTED, fontsize=8)
ax[0].set_xlabel("frequency (Hz)"); ax[0].set_ylabel("input noise (nV/√Hz)"); style(ax[0], "Input-referred noise of the receiver (tt)")
ax[0].legend(frameon=False, fontsize=8, loc="lower left"); ax[0].set_ylim(0.3, 20)
fl = np.array(nz["fL"])
for k, c in (("3.3", P[2]), ("1.0", P[0]), ("0.4", P[1])):
    ax[1].semilogx(fl, nz["L"][k], color=c, lw=1.8, label=f"{k} V pp sine: σ = {nz['sigma'][k]['abs']*1e12:.2f} ps per edge")
ax[1].axhline(-155, color=P[4], lw=1, ls="--"); ax[1].text(1.2e3, -154.3, "step-72 allocation −155 dBc/Hz", color=P[4], fontsize=8)
ax[1].set_xlabel("offset (Hz)"); ax[1].set_ylabel("L at 50 MHz (dBc/Hz)"); style(ax[1], "Receiver phase noise at the reference")
ax[1].legend(frameon=False, fontsize=8, loc="lower left"); ax[1].set_ylim(-170, -135)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step76_noise.png"), dpi=150)

# 2. transient-noise edge deviations (M15)
fig, ax = plt.subplots(1, 2, figsize=(12, 3.6))
for r, c in zip([r for r in tn["runs"] if r["Sw"] > 0], (P[0], P[2], P[1])):
    x = np.array(r["dev"]); k = np.arange(len(x)); x = x - np.polyval(np.polyfit(k, x, 4), k)
    ax[0].plot(k, x*1e12, color=c, lw=0.8, label=f"{r['vpp']} V pp")
    ax[1].hist(x*1e12, bins=40, histtype="step", color=c, lw=1.5, density=True, label=f"{r['vpp']} V pp: σ {x.std()*1e12:.2f} ps")
ax[0].set_xlabel("edge number"); ax[0].set_ylabel("edge-time deviation (ps)"); style(ax[0], "Transient noise: refclk edge times (M15)")
ax[0].legend(frameon=False, fontsize=8, ncol=3, loc="upper right")
ax[1].set_xlabel("deviation (ps)"); ax[1].set_ylabel("density"); style(ax[1], "Per-edge jitter distribution")
ax[1].legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step76_tnoise.png"), dpi=150)

# 3. large-signal: delay / duty over amplitude and corners, start-up
fig, ax = plt.subplots(1, 2, figsize=(12, 3.9))
amp = [r for r in s["tran"] if r["corner"] == "tt" and r["wave"] == "sine" and r["f"] == 50e6 and r["vddl"] == 1.8]
amp.sort(key=lambda r: r["vpp"])
ax[0].plot([r["vpp"] for r in amp], [r["delay"]*1e9 for r in amp], "-o", color=P[0], ms=4, lw=1.8, label="delay pad → refclk (ns)")
ax2 = ax[0].twinx(); ax2.spines["top"].set_visible(False)
ax2.plot([r["vpp"] for r in amp], [r["duty"]*100 for r in amp], "-s", color=P[1], ms=4, lw=1.8, label="duty (%)")
ax2.axhline(45, color=P[1], lw=1, ls=":"); ax2.set_ylabel("duty (%)"); ax2.set_ylim(40, 60)
ax[0].set_xlabel("input amplitude (V pp sine, 50 MHz)"); ax[0].set_ylabel("delay (ns)"); style(ax[0], "Delay and duty vs input amplitude (tt)")
h1, l1 = ax[0].get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax[0].legend(h1 + h2, l1 + l2, frameon=False, fontsize=8, loc="upper center")
su = s["startup"]; t = np.array(su["t"])*1e6
ax[1].plot(t, su["vin"], color=P[0], lw=1.4, label="v(vin): 50 MHz signal on its settling bias")
ax[1].plot(t, np.array(su["out"])*0 + np.nan, color=P[2])
if su["t_settled"]:
    ax[1].axvline(su["t_settled"]*1e6, color=P[2], lw=1, ls="--")
    ax[1].text(su["t_settled"]*1e6 + 0.5, -0.42, f"periods within 2 % from {su['t_settled']*1e6:.1f} µs;\nthe bias keeps settling slowly", color=P[2], fontsize=8)
ax[1].set_xlabel("time (µs), pll_en rises at 0.5 µs"); ax[1].set_ylabel("V"); style(ax[1], "Start-up after pll_en (tt, 1 V pp)")
ax[1].legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step76_tran.png"), dpi=150)
print("plots done")
