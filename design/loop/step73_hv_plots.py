#!/usr/bin/env python3
"""step73_hv_plots.py - figures of the step-73 redo (800 MHz, 5 V devices): docs/img/step73hv_*.png.
Run step73_hv_loop.py first."""
import os, sys, csv, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import sampled_loop as sl
P = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
IMG = os.path.join(ROOT, "docs", "img")
D = json.load(open(os.path.join(HERE, "data", "step73_hv_design.json")))
G = [dict((k, float(v)) for k, v in r.items()) for r in csv.DictReader(open(os.path.join(HERE, "data", "step73_hv_jitter_grid.csv")))]
T = 20e-9

def style(ax, title):
    ax.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_title(title, loc="left", color=INK, fontsize=10)

# 1 --- why f_c = 2.5 MHz
g = sorted([r for r in G if r["pm"] == 50], key=lambda r: r["fc"]); fc = np.array([r["fc"] for r in g])/1e6
fig, ax = plt.subplots(1, 3, figsize=(12, 3.8))
for i, (k, lab) in enumerate((("out1_typ_ps", "out1 (FFNC off), typ"), ("out2_typ_ps", "out2 (FFNC on), typ"),
                              ("out1_pess_ps", "out1, pess"), ("out2_pess_ps", "out2, pess"))):
    ax[0].plot(fc, [r[k] for r in g], "-o" if "typ" in k else "--", color=P[i % 2], ms=3.5, lw=2 if "typ" in k else 1.3, label=lab)
ax[0].set_xlabel("loop bandwidth f_c (MHz)"); ax[0].set_ylabel("rms jitter (ps)"); style(ax[0], "Jitter at 800 MHz, 10 kHz–40 MHz (PM 50°)")
ax[0].legend(frameon=False, fontsize=8)
ax[1].plot(fc, [r["out1_typ_L300k"] for r in g], "-o", color=P[0], ms=3.5, lw=2, label="out1 typ")
ax[1].axhline(-114, color=MUTED, lw=1, ls=":"); ax[1].text(3.6, -113.4, "spec typ −114", color=MUTED, fontsize=8)
ax[1].set_xlabel("f_c (MHz)"); ax[1].set_ylabel("L(300 kHz), dBc/Hz"); style(ax[1], "FFNC-off phase noise at 300 kHz")
ax[2].plot(fc, [r["reduction_typ_pct"] for r in g], "-o", color=P[1], ms=3.5, lw=2)
ax[2].axhline(35, color=MUTED, lw=1, ls=":"); ax[2].text(3.6, 36.5, "spec typ 35 %", color=MUTED, fontsize=8)
ax[2].axhline(20, color=MUTED, lw=1, ls=":"); ax[2].text(3.6, 21.5, "spec min 20 %", color=MUTED, fontsize=8)
ax[2].set_xlabel("f_c (MHz)"); ax[2].set_ylabel("jitter reduction by FFNC (%)"); style(ax[2], "FFNC jitter reduction, typ")
for a in ax:
    a.axvline(2.5, color=INK, lw=0.8, alpha=0.5)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step73hv_fc_choice.png"), dpi=150)

# 2 --- sampled loop gain
R, C1, C2, KV, beta, tp = D["R"], D["C1"], D["C2"], D["KV"], D["beta"], D["tp"]
f = np.logspace(4, np.log10(0.49/T), 600)
L = sl.loop_gain(f, R, C1, C2, KV, beta, T, tp)
s = 2j*np.pi*f
Zc = (1 + s*R*C1)/(s*(C1 + C2)*(1 + s*R*C1*C2/(C1 + C2))); Lc = beta*KV*Zc/s
fig, ax = plt.subplots(2, 1, figsize=(7.5, 5.4), sharex=True)
ax[0].semilogx(f, 20*np.log10(abs(L)), color=P[0], lw=2, label="sampled loop (exact)")
ax[0].semilogx(f, 20*np.log10(abs(Lc)), "--", color=P[1], lw=1.3, label="continuous approximation")
ax[0].axhline(0, color=MUTED, lw=0.8); ax[0].set_ylabel("|L| (dB)"); ax[0].set_ylim(-40, 60)
style(ax[0], f"Open-loop gain: f_c = {D['fc']/1e6:.2f} MHz, PM = {D['pm']:.1f}° (packet delay {tp*1e9:.1f} ns)")
ax[0].legend(frameon=False, fontsize=8)
ph = np.unwrap(np.angle(L)); ph = np.degrees(ph - 2*np.pi*np.round(ph[0]/(2*np.pi)))
ax[1].semilogx(f, ph, color=P[0], lw=2); ax[1].semilogx(f, np.degrees(np.unwrap(np.angle(Lc))), "--", color=P[1], lw=1.3)
ax[1].axhline(-180, color=MUTED, lw=0.8); ax[1].axvline(D["fc"], color=INK, lw=0.8, alpha=0.5)
ax[1].set_ylabel("∠L (deg)"); ax[1].set_xlabel("frequency (Hz)"); ax[1].set_ylim(-280, -100); style(ax[1], "")
for a in ax: a.axvline(D["fz"], color=MUTED, lw=0.6, ls=":"); a.axvline(D["fp"], color=MUTED, lw=0.6, ls=":")
ax[1].text(D["fz"]*1.05, -270, "zero", color=MUTED, fontsize=8); ax[1].text(D["fp"]*1.05, -270, "pole", color=MUTED, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step73hv_loop_gain.png"), dpi=150)

# 3 --- robustness
fig, ax = plt.subplots(1, 2, figsize=(12, 3.9))
for i, (name, rows) in enumerate(D["robust"].items()):
    m = [r[0] for r in rows]
    ax[0].semilogx(m, [r[2] for r in rows], color=P[i], lw=2 if name == "nominal" else 1.3, label=name)
    ax[1].semilogx(m, [r[1]/1e6 for r in rows], color=P[i], lw=2 if name == "nominal" else 1.3, label=name)
for a in ax:
    a.axvspan(0.75, 1.3, color=GRID, alpha=0.8, lw=0); a.set_xlabel("loop-gain multiplier m = (A g_m τ K_VCO) / nominal")
    a.set_xticks([0.4, 0.5, 0.75, 1, 1.3, 2, 3]); a.set_xticklabels(["0.4", "0.5", "0.75", "1", "1.3", "2", "3"])
    a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax[0].axhline(45, color=MUTED, lw=0.8, ls=":"); ax[0].set_ylabel("phase margin (deg)"); ax[0].set_ylim(30, 55)
style(ax[0], "Phase margin at the R/C corners (band: residual after icp_trim)")
ax[1].set_ylabel("f_c (MHz)"); style(ax[1], "Loop bandwidth at the R/C corners")
ax[0].legend(frameon=False, fontsize=8, loc="lower center")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step73hv_robustness.png"), dpi=150)

# 4 --- phase-step response
t, e, v = sl.step(R, C1, C2, KV, beta, T, tp, ncyc=100, phi_step=1.0)
ps = e/(2*np.pi*0.8e9)*1e12
fig, ax = plt.subplots(figsize=(7.5, 3.4))
ax.plot(t*1e6, ps, "-", color=P[0], lw=1.6, drawstyle="steps-post", label="phase error at each sample")
ax.axhspan(-10, 10, color=GRID, alpha=0.9, lw=0); ax.text(1.4, 14, "±10 ps lock window", color=MUTED, fontsize=8)
ax.axvline(D["settle_s"]*1e6, color=INK, lw=0.8, alpha=0.5)
ax.set_xlabel("time after a 1 rad reference phase step (µs)"); ax.set_ylabel("phase error (ps)")
style(ax, f"Linear settling: {D['settle_s']*1e6:.2f} µs to ±10 ps, overshoot {D['overshoot_pct']:.0f} %")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step73hv_step.png"), dpi=150)
print("figures written")

# 5 --- C-V of the 5 V MOS cap vs the 1.8 V one (why the V_cont window moved to 1.0-2.3 V)
cvh = list(csv.DictReader(open(os.path.join(HERE, "data", "moscap_hv_cv.csv"))))
cvl = list(csv.DictReader(open(os.path.join(HERE, "data", "moscap_cv.csv"))))
fig, ax = plt.subplots(figsize=(7.5, 3.6))
for i, (c, t) in enumerate((("tt", "27"), ("ss", "-40"), ("ff", "110"))):
    x = [float(r["vg"]) for r in cvh if r["corner"] == c and r["temp"] == t]
    y = [float(r["c_mos_fF"])/100 for r in cvh if r["corner"] == c and r["temp"] == t]
    ax.plot(x, y, "-o", ms=3, color=P[0], alpha=1 if c == "tt" else 0.5, lw=2 if c == "tt" else 1.2,
            label=f"nfet_g5v0d10v5, {c} {t} °C")
x = [float(r["vg"]) for r in cvl if r["corner"] == "tt" and r["temp"] == "27"]
y = [float(r["c_mos_fF"])/100 for r in cvl if r["corner"] == "tt" and r["temp"] == "27"]
ax.plot(x, y, "--", color=P[1], lw=1.5, label="nfet_01v8 (old design), tt 27 °C")
ax.axhline(2.02, color=MUTED, lw=1, ls=":"); ax.text(2.6, 2.1, "cap_mim_m3_1 ≈ 2.0", color=MUTED, fontsize=8)
ax.axvspan(D["vc_window"][0], D["vc_window"][1], color=GRID, alpha=0.8, lw=0)
ax.text(1.05, 8.2, "V_cont window 1.0–2.3 V", color=MUTED, fontsize=8)
ax.set_xlabel("gate (V_cont) voltage (V)"); ax.set_ylabel("capacitance density (fF/µm²)"); ax.set_ylim(0, 9)
style(ax, "MOS-capacitor C-V: thick oxide gives 2.9 fF/µm², 2.6× less than the 1.8 V device")
ax.legend(frameon=False, fontsize=8, loc="center right")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "step73hv_cv.png"), dpi=150)
print("C-V figure written")
