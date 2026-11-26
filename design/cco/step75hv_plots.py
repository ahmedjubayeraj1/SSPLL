#!/usr/bin/env python3
"""step75hv_plots.py - figures of the step-75 redo (5 V CCO for the 800 MHz ring): docs/img/step75hv_*.png.
Run step75hv_sim.py, step75hv_vdda.py, step75hv_noise.py (and step75hv_headroom.py for the design study) first."""
import os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(HERE, "..", "..", "docs", "img")
INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"; P = ["#2a78d6", "#eb6834", "#1baf7a", "#f0a30a", "#8250df"]
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
ld = lambda n: json.load(open(os.path.join(HERE, "data", f"step75hv_{n}.json")))
def style(ax, t):
    ax.set_title(t, loc="left", color=INK, fontsize=10.5); ax.grid(True, color=GRID); ax.set_axisbelow(True)
S = ld("sim"); IMIN, IMAX = 0.704e-3, 1.462e-3          # step 74 HV: ff/-40 C 720 MHz, ss/110 C 880 MHz

# 1 --- DC: code sweep at tt, and the range over corners / VDDA / IBIAS
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
tt = [r for r in S["dc"][90:]]
ax[0].plot([r[4] for r in tt], [r[-1]*1e3 for r in tt], "-o", ms=3, color=P[0])
ax[0].set_xlabel("cco_code"); ax[0].set_ylabel("output current (mA)")
lsb = np.diff([r[-1] for r in tt]); ax[0].text(1, tt[-1][-1]*1e3*0.96, f"LSB {np.mean(lsb)*1e6:.1f} µA (min {lsb.min()*1e6:.1f}, max {lsb.max()*1e6:.1f})",
                                               color=MUTED, fontsize=8)
style(ax[0], "Code sweep, tt 27 °C, VDDA 3.3 V, IBIAS 5 µA")
for k, (ib, col) in enumerate(zip((4e-6, 5e-6, 6e-6), P)):
    for code, mk in ((0, "v"), (10, "o"), (31, "^")):
        v = [r[-1]*1e3 for r in S["dc"][:90] if r[3] == ib and r[4] == code]
        ax[1].plot([code + (k - 1)*0.8]*2, [min(v), max(v)], "-", color=col, lw=3, solid_capstyle="butt",
                   label=f"IBIAS {ib*1e6:.0f} µA" if code == 0 else None)
ax[1].axhline(IMIN*1e3, color=P[3], ls="--"); ax[1].axhline(IMAX*1e3, color=P[3], ls="--")
ax[1].text(12, IMIN*1e3 - 0.07, "0.704 mA: ff/−40 °C, 720 MHz", color=MUTED, fontsize=8)
ax[1].text(12, IMAX*1e3 + 0.03, "1.462 mA: ss/110 °C, 880 MHz", color=MUTED, fontsize=8)
ax[1].set_xticks([0, 10, 31]); ax[1].set_xlabel("cco_code"); ax[1].set_ylabel("output current (mA)")
style(ax[1], "Spread over 5 corners × VDDA 2.97/3.63 V"); ax[1].legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step75hv_dc.png"), dpi=150)

# 2 --- compliance and VDDA rejection vs supply level
V = ld("vdda")
fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
for (tag, lab), col in zip((("comp_tt_code10", "tt 27 °C, VDDA 3.3 V, code 10"),
                            ("comp_ss_worst", "ss 110 °C, VDDA 2.97 V, code 31, IBIAS 4 µA")), P):
    d = np.array(S[tag]); ax[0].plot(d[:, 0], abs(d[:, 1])*1e3, color=col, label=lab)
ax[0].axvline(2.37, color=MUTED, ls=":"); ax[0].text(2.39, 0.5, "ring node\nss 880 MHz", color=MUTED, fontsize=8, transform=ax[0].get_xaxis_transform())
ax[0].axvline(1.89, color=MUTED, ls=":"); ax[0].text(1.91, 0.5, "tt 800 MHz", color=MUTED, fontsize=8, transform=ax[0].get_xaxis_transform())
ax[0].set_xlabel("ring node voltage (V)"); ax[0].set_ylabel("output current (mA)")
style(ax[0], "Compliance: current vs ring node"); ax[0].legend(frameon=False, fontsize=8, loc="center left")
for (tag, lab), col in zip((("tt_800", "tt 27 °C, 800 MHz (node 1.89 V)"), ("ss_800", "ss 110 °C, 800 MHz (node 2.25 V)"),
                            ("ss_880", "ss 110 °C, 880 MHz (node 2.37 V)")), P):
    ax[1].semilogy([q["vdda"] for q in V[tag]], [q["kvdd"]/1e6 for q in V[tag]], "-o", ms=4, color=col, label=lab)
ax[1].axhline(5, color=P[3], ls="--"); ax[1].text(3.4, 5.6, "allocation 5 MHz/V (typ)", color=MUTED, fontsize=8)
ax[1].axhline(20, color=P[3], ls=":"); ax[1].text(3.4, 22, "pessimistic 20 MHz/V", color=MUTED, fontsize=8)
ax[1].set_xlabel("VDDA (V)"); ax[1].set_ylabel("K_vdd = K_I·|dI/dVDDA| at 1 MHz (MHz/V)")
style(ax[1], "Supply pushing vs VDDA level (headroom)"); ax[1].legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step75hv_compliance.png"), dpi=150)

# 3 --- PSR vs frequency, and output noise vs allocation
N = ld("noise")
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
KI = {"tt": 0.62e12, "ss": 0.41e12, "ff": 0.85e12}
lab = {"tt": "tt 27 °C, 3.3 V, code 10", "ss": "ss 110 °C, 2.97 V, code 31 at IBIAS 5 µA = 1.78 mA (beyond need)", "ff": "ff −40 °C, 3.63 V, code 0"}
for (cn, d), col in zip(S["psr"].items(), P):
    d = np.array(d); ax[0].loglog(d[:, 0], d[:, 1]*KI[cn]/1e6, color=col, label=lab[cn])
ax[0].axhline(5, color=P[3], ls="--"); ax[0].set_xlabel("frequency of the VDDA ripple (Hz)")
ax[0].set_ylabel("K_vdd (MHz/V)"); style(ax[0], "VDDA → ring frequency (AC, ring node held)")
ax[0].legend(frameon=False, fontsize=8)
ax[1].loglog(N["f"], np.array(N["n"])*1e12, color=P[0], label="CCO output current noise (.noise)")
ax[1].plot([1e6], [N["alloc_1M"]*1e12], "D", color=P[1], label=f"allocation at 1 MHz: {N['alloc_1M']*1e12:.1f} pA/√Hz")
ax[1].set_xlabel("offset frequency (Hz)"); ax[1].set_ylabel("i_n (pA/√Hz)"); style(ax[1], "Output current noise, tt 27 °C, code 10")
ax[1].legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step75hv_noise.png"), dpi=150)

# 4 --- design study: K_vdd and noise per variant (step75hv_headroom.py)
H = ld("headroom"); ks = list(H)
fig, ax = plt.subplots(1, 2, figsize=(11, max(3.5, 0.32*len(ks) + 1)))
y = np.arange(len(ks)); hh = 0.38
ax[0].barh(y + hh/2, [H[k]["k_tt"]/1e6 for k in ks], hh, color=P[0], label="tt, 3.3 V")
ax[0].barh(y - hh/2, [H[k]["k_ss33"]/1e6 for k in ks], hh, color=P[1], label="ss 110 °C, 3.3 V, node 2.37 V")
ax[0].set_xscale("log"); ax[0].axvline(5, color=P[3], ls="--"); ax[0].set_yticks(y, ks, fontsize=7)
ax[0].set_xlabel("K_vdd at 1 MHz (MHz/V)"); style(ax[0], "Cascode variants: supply pushing"); ax[0].legend(frameon=False, fontsize=8)
ax[1].barh(y, [H[k]["n1M"]*1e12 for k in ks], color=P[2]); ax[1].set_yticks(y, ["" for _ in ks])
ax[1].axvline(N["alloc_1M"]*1e12, color=P[3], ls="--"); ax[1].set_xlabel("i_n at 1 MHz (pA/√Hz)")
style(ax[1], "Cascode variants: output noise")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step75hv_variants.png"), dpi=150)
print("figures written")
