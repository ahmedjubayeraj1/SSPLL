#!/usr/bin/env python3
"""d2s_hv_plots.py - figures of the diff-to-SE amplifier: docs/img/d2s_hv_*.png. Run d2s_hv_sim.py (and
d2s_hv_system.py for the system figure) first."""
import os, sys, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
P = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
IMG = os.path.join(ROOT, "docs", "img")
d = json.load(open(os.path.join(HERE, "data", "d2s_hv_sim.json")))
SEL = ("tt 27 °C, 3.3 V", "ss_hh -40 °C, 2.97 V", "ff_ll 110 °C, 3.63 V", "ss 110 °C, 2.97 V", "ff -40 °C, 3.63 V")


def style(ax, title):
    ax.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_title(title, loc="left", color=INK, fontsize=10)


# 1 --- DC transfer and local gain over corners; AC gain
fig, ax = plt.subplots(1, 3, figsize=(12.5, 3.8))
for k, name in enumerate(SEL):
    r = next(x for x in d["A"] if x["cond"] == name)
    v, y = map(np.array, r["curve"])
    ax[0].plot(v, y, color=P[k], lw=1.8, label=name)
    ax[1].plot(v, np.gradient(y, v), color=P[k], lw=1.8)
for a in ax[:2]:
    a.axvspan(-0.10, 0.30, color=GRID, alpha=0.6, lw=0)
ax[0].text(-0.08, ax[0].get_ylim()[0] + 0.05, "lock window", color=MUTED, fontsize=8)
ax[0].set_xlabel("v_d = inp − inm = v2m − v2p (V)"); ax[0].set_ylabel("vff (V)"); ax[0].legend(frameon=False, fontsize=7.5)
style(ax[0], "DC transfer: vff = V_0 + G v_d")
ax[1].set_xlabel("v_d (V)"); ax[1].set_ylabel("local gain dvff / dv_d (V/V)"); style(ax[1], "Local gain over the input range")
for k, name in enumerate(SEL):
    r = next(x for x in d["B"] if x["cond"] == name)
    ax[2].semilogx(r["f"], 20*np.log10(np.array(r["mag"])), color=P[k], lw=1.8)
ax[2].axvline(50e6/7.8, color=MUTED, ls=":", lw=0.8); ax[2].text(50e6/7.8*1.1, -12, "f_ref / 7.8", color=MUTED, fontsize=8)
ax[2].set_ylim(-20, 4); ax[2].set_xlabel("frequency (Hz)"); ax[2].set_ylabel("|G(f)| (dB)")
style(ax[2], "Small-signal gain, 40 fF load")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "d2s_hv_transfer.png"), dpi=150); plt.close(fig)

# 2 --- noise and supply
fig, ax = plt.subplots(1, 3, figsize=(12.5, 3.8))
for k, r in enumerate(d["C"]):
    ax[0].loglog(r["f"], np.array(r["vin"])*1e9, color=P[k], lw=1.8, label=f"{r['cond']}: {r['jit']*1e15:.0f} fs")
r0 = d["C"][0]
ax[0].loglog(r0["f"], np.array(r0["vin_mos"])*1e9, "--", color=INK, lw=0.9, label="tt, transistors only")
ax[0].set_xlim(1e3, 1e9); ax[0].set_xlabel("frequency (Hz)"); ax[0].set_ylabel("input-referred noise (nV/√Hz)")
ax[0].legend(frameon=False, fontsize=7.5); style(ax[0], "Input-referred noise (jitter 10 kHz–40 MHz)")
for k, r in enumerate(d["D"]):
    ax[1].loglog(r["cm_tracks"]["f"], r["cm_tracks"]["h"], color=P[k], lw=1.8, label=r["cond"])
    ax[1].loglog(r["cm_fixed"]["f"], r["cm_fixed"]["h"], ":", color=P[k], lw=1.2)
ax[1].set_xlabel("frequency (Hz)"); ax[1].set_ylabel("|vff / VDDA| (V/V)"); ax[1].legend(frameon=False, fontsize=7.5)
style(ax[1], "VDDA → vff (solid: CM follows VDDA)")
F = d["F"]; v0 = np.array([x["V0"] for x in F]); g = np.array([x["G"] for x in F])
ax[2].scatter((v0 - v0.mean())*1e3, g, s=14, color=P[0])
ax[2].set_xlabel("V_0 − mean (mV)"); ax[2].set_ylabel("G (V/V)")
style(ax[2], f"Mismatch, {len(F)} runs: σ(V_0) {v0.std()*1e3:.1f} mV, σ(G) {g.std()/g.mean()*100:.2f} %")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "d2s_hv_noise.png"), dpi=150); plt.close(fig)

# 3 --- whole path (SSPD + D2S in one run): beat (part E) and lock (part H)
if "E" in d and "H" in d:
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    for k, r in enumerate(d["E"]):
        ph = np.array(r["dphi"]); o = np.argsort(ph); ph = ph[o]; m = np.abs(ph) < 0.8
        ax[0].plot(ph[m], np.array(r["v2"])[o][m], color=P[k], lw=1.2, ls=":")
        ax[0].plot(ph[m], np.array(r["vff"])[o][m], color=P[k], lw=1.8,
                   label=f"{r['cond']}: vff / (v2p − v2m) = −{r['G_path']:.3f}")
    ax[0].set_xlabel("ring phase at the sampling edge, from the crossing (rad)"); ax[0].set_ylabel("V")
    ax[0].legend(frameon=False, fontsize=7.5); style(ax[0], "Beat run: v2p − v2m (dotted) and vff (solid)")
    for k, r in enumerate(d["H"]):
        t, ckh, v2, vff = map(np.array, r["wave"])
        ax[1].plot(t, (vff - vff.mean())*1e3, color=P[k], lw=1.8, label=f"{r['cond']}: spur ≤ {r['spur']:.0f} dBc")
    t, ckh = map(np.array, d["H"][0]["wave"][:2])
    ax[1].fill_between(t, -12, 12, where=ckh > 1.6, color=GRID, lw=0)
    ax[1].text(t[np.argmax(ckh > 1.6)], 9, " ckh (hold)", color=MUTED, fontsize=8)
    ax[1].set_xlabel("time in the period (ns)"); ax[1].set_ylabel("vff − mean (mV)"); ax[1].set_ylim(-12, 12)
    ax[1].legend(frameon=False, fontsize=7.5); style(ax[1], "At lock: vff over one reference period")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "d2s_hv_path.png"), dpi=150); plt.close(fig)
print("figures written")
