#!/usr/bin/env python3
"""step74_plots.py - figures of the step-74 report (docs/img/step74_*.png)."""
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
base, q3 = D("step74_base.json"), D("step74_q3.json"); ch = D("step74_char_q3.json")

# 1. ISF and flicker shares
fig, ax = plt.subplots(1, 2, figsize=(12, 3.9))
for d, c, lab in ((base, P[0], "base cell"), (q3, P[1], "step-74 cell")):
    h = np.array(d["h"]); ph = np.arange(len(h))/len(h)
    ax[0].plot(np.r_[ph, 1], np.r_[h, h[0]]/1e12, "-o", color=c, ms=3.5, lw=1.8,
               label=f"{lab}: h_dc/h_rms = {d['hdc_over_hrms']:.2f}")
ax[0].axhline(0, color=MUTED, lw=0.8); ax[0].set_xlabel("injection time / period"); ax[0].set_ylabel("h = dφ/dq (rad/pC)")
style(ax[0], "Impulse sensitivity of node p1"); ax[0].legend(frameon=False, fontsize=8)
names = {"x1.xp2": "main pMOS", "x1.xn2": "main nMOS", "x1.xs2": "tune switch S", "x1.xt1n": "TG nMOS (own)",
         "x2.xt1n": "TG nMOS (next)", "x1.xt1p": "TG pMOS (own)", "x2.xt1p": "TG pMOS (next)"}
keys = list(names); y = np.arange(len(keys)); hgt = 0.38
fl = lambda d: np.array([d["shares"][k][1] for k in keys])*10**(d["Lfl"]/10)
ref = 10**(base["Lfl"]/10)
ax[1].barh(y + hgt/2, fl(base)/ref*100, hgt, color=P[0], label=f"base: corner {base['fc3']/1e6:.2f} MHz")
ax[1].barh(y - hgt/2, fl(q3)/ref*100, hgt, color=P[1], label=f"step-74: corner {q3['fc3']/1e6:.2f} MHz")
ax[1].set_yticks(y, [names[k] for k in keys]); ax[1].invert_yaxis()
ax[1].set_xlabel("flicker up-conversion, % of the base cell's total"); style(ax[1], "Who causes the 1/f³ noise")
ax[1].legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step74_isf.png"), dpi=150)

# 2. frequency range vs current and ring-node voltage
fig, ax = plt.subplots(1, 2, figsize=(12, 3.9))
for (k, lab), c in zip((("tt_27", "tt, 27 °C, 10 fF"), ("ss_110", "ss, 110 °C, 15 fF"), ("ff_-40", "ff, −40 °C, 5 fF")), P):
    r = ch["f_vs_I"][k]; I = [x[0]*1e3 for x in r]
    ax[0].plot(I, [x[1]/1e9 for x in r], "-o", color=c, ms=3.5, lw=1.8, label=lab)
    ax[1].plot(I, [x[2] for x in r], "-o", color=c, ms=3.5, lw=1.8, label=lab)
for f in (1.44, 1.6, 1.76):
    ax[0].axhline(f, color=MUTED, lw=0.8, ls=":")
ax[0].text(0.92, 1.775, "1.76 GHz", color=MUTED, fontsize=8); ax[0].text(0.92, 1.455, "1.44 GHz", color=MUTED, fontsize=8)
ax[0].set_xlabel("CCO feed current (mA)"); ax[0].set_ylabel("f (GHz)"); style(ax[0], "Coarse tuning: frequency vs feed current")
ax[0].legend(frameon=False, fontsize=8)
ax[1].axhline(1.8, color=MUTED, lw=0.8, ls=":"); ax[1].text(0.92, 1.81, "1.8 V limit", color=MUTED, fontsize=8)
ax[1].set_xlabel("CCO feed current (mA)"); ax[1].set_ylabel("ring supply node (V)"); style(ax[1], "Ring-node voltage")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step74_range.png"), dpi=150)

# 3. fine tuning
fig, ax = plt.subplots(figsize=(7.5, 3.8))
for (k, lab), c in zip((("tt_27", "tt, 27 °C"), ("ss_110", "ss, 110 °C"), ("ff_-40", "ff, −40 °C")), P):
    r = [x for x in ch["f_vs_vtune"][k] if x[1]]
    v = np.array([x[0] for x in r]); f = np.array([x[1] for x in r])
    f0 = np.interp(0.9, v, f)
    ax.plot(v, (f/f0 - 1)*100, "-o", color=c, ms=3.5, lw=1.8, label=f"{lab} (f at 0.9 V = {f0/1e9:.2f} GHz)")
ax.axvspan(0.6, 1.2, color=GRID, alpha=0.8, lw=0); ax.text(0.62, -11.5, "V_cont window 0.6–1.2 V", color=MUTED, fontsize=8)
ax.set_xlabel("vtune (V)"); ax.set_ylabel("frequency change from vtune = 0.9 V (%)")
style(ax, "Fine tuning at the 1.6 GHz current: K_VCO < 0"); ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step74_tuning.png"), dpi=150)
print("figures written")
