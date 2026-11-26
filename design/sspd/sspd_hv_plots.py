#!/usr/bin/env python3
"""sspd_hv_plots.py - figures of the SSPD report (docs/img/sspd_hv_*.png)."""
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

S = json.load(open(os.path.join(HERE, "data", "sspd_hv_sim.json")))
N = json.load(open(os.path.join(HERE, "data", "sspd_hv_noise.json")))
C = [c for c in S["char"] if "A" in c]; tt = C[0]

# 1. sampled characteristic and hold
r = np.array(tt["rows"]); d = (r[:, 1] - tt["phi0"] + np.pi) % (2*np.pi) - np.pi; o = np.argsort(d)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
ax[0].plot(d[o], r[o, 2], "o-", color=P[0], ms=4, lw=1.4, label="v1p − v1m (read by the Gm)")
ax[0].plot(d[o], r[o, 3], "s", color=P[1], ms=3.5, label="v2p − v2m (held for the NCB)")
x = np.linspace(-0.6, 0.6, 2); ax[0].plot(x, 2*tt["A"]*x, color=INK, lw=1, ls="--", label=f"slope 2A = {2*tt['A']:.3f} V/rad")
ax[0].axhline(0, color=MUTED, lw=0.8); ax[0].axvline(0, color=MUTED, lw=0.8)
ax[0].set_xlabel("ring phase at the sampling instant, relative to the lock point (rad)"); ax[0].set_ylabel("V")
ax[0].legend(frameon=False, fontsize=8, loc="upper left")
style(ax[0], "Sampled characteristic (beat run, tt 27 °C, 3.3 V)")
k = np.arange(len(r)); ax[1].plot(k, r[:, 2], "o-", color=P[0], ms=3, lw=1, label="v1 (new sample)")
ax[1].plot(k, r[:, 3], "s-", color=P[1], ms=3, lw=1, label=f"v2 = (1−α)·v1 + α·v2[k−1], α = {tt['alpha']:.3f}")
ax[1].set_xlabel("reference period k"); ax[1].set_ylabel("V"); ax[1].legend(frameon=False, fontsize=8)
style(ax[1], "Hold: C2 follows C1 with a first-order memory")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "sspd_hv_char.png"), dpi=150)

# 2. corners
lab = [f"{c['corner']} {c['temp']}°C {c['vdda']}/{c['vddd']} V" + ("" if c["fref"] == 50e6 else f" {c['fref']/1e6:.0f} MHz") for c in C]
fig, ax = plt.subplots(1, 3, figsize=(13, 5.2), sharey=True); y = np.arange(len(C))
for a, k_, sc, ttl, c_, lim in ((ax[0], "A", 1, "A (V/rad per side); target 0.8, floor 0.5", P[0], (0.5, 0.8)),
                                (ax[1], "cm", 1, "common mode of v1 (V)", P[2], ()),
                                (ax[2], "power", 1e3, "SSPD power (mW, VDDA)", P[1], ())):
    a.scatter([c[k_]*sc for c in C], y, color=c_, s=20, zorder=3)
    for L_ in lim:
        a.axvline(L_, color=P[4], lw=1, ls="--")
    style(a, ttl)
ax[0].set_yticks(y, lab, fontsize=7.5); ax[0].invert_yaxis()
fig.tight_layout(); fig.savefig(os.path.join(IMG, "sspd_hv_corners.png"), dpi=150)

# 3. kick-back
K = S["kick"]
fig, ax = plt.subplots(1, 2, figsize=(12, 3.8), gridspec_kw=dict(width_ratios=[2, 1]))
ax[0].stem(np.array(K["wave"]["dt_edges"]), K["wave"]["dt"], linefmt=P[0], markerfmt="o", basefmt=" ")
ax[0].set_xlabel("time (ns), 3 reference periods"); ax[0].set_ylabel("clkp edge shift (fs)")
style(ax[0], f"Kick-back on the ring buffer output: max {K['dt_max']*1e15:.0f} fs, spur estimate {K['spur_dbc']:.0f} dBc")
ax[1].bar(["with dummy", "without dummy"], [K["I_fref"]*1e6, K["I_fref_nodummy"]*1e6], color=[P[2], P[1]])
ax[1].set_yscale("log"); ax[1].set_ylabel("SSPD supply current at f_ref (µA)")
style(ax[1], "Why the dummy sampler")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "sspd_hv_kick.png"), dpi=150)

# 4. REF chain with the measured SSPD parts
f = np.array(N["fL"]); L = N["L"]["3.3_typ"]
names = dict(rx_white="receiver S1 (white)", rx_slow="receiver (slow)", clkgen="clock generator (M17)",
             vdda="VDDA → sampling edge", vddd="VDDD → sampling edge", sspd_buf="SSPD buffers (M17)",
             sspd_buf_vdda="SSPD buffers, VDDA")
fig, ax = plt.subplots(figsize=(9, 4.2))
for i, (k_, nm) in enumerate(names.items()):
    ax.semilogx(f, L[k_], color=(P + [MUTED, "#8250df"])[i], lw=1.2, label=nm)
ax.semilogx(f, L["chain"], color=INK, lw=2.2, label="REF chain total")
ax.axhline(-155, color=P[4], ls="--", lw=1, label="allocation −155 dBc/Hz")
ax.set_ylim(-200, -130); ax.set_xlabel("offset (Hz)"); ax.set_ylabel("dBc/Hz at 50 MHz")
ax.legend(frameon=False, fontsize=7.5, ncol=2, loc="upper right")
style(ax, "REF chain at the detector, 3.3 V square, typ (×N² = +24 dB in band)")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "sspd_hv_noise.png"), dpi=150)
print("plots done")
