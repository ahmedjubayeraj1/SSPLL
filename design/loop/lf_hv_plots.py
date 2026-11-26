#!/usr/bin/env python3
"""lf_hv_plots.py - figures of Loop filter in real devices: docs/img/lf_hv_*.png.
Run lf_hv_sim.py first."""
import os, sys, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import sampled_loop as sl
import lf_hv_sim as S
P = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
IMG = os.path.join(ROOT, "docs", "img")
J = lambda n: json.load(open(os.path.join(S.DATA, f"lf_hv_{n}.json")))
L, C, LP, N, PU, SZ = J("load"), J("corners"), J("loop"), J("noise"), J("pulse"), J("size")
nom = next(r for r in C if r["corner"] == "tt" and r["temp"] == 27 and r["vc"] == 1.8)
p = dict(S.F.D, R1=tuple(SZ["R1"]), C2=tuple(SZ["C2"]))


def style(ax, title):
    ax.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_title(title, loc="left", color=INK, fontsize=10)


# 1 --- impedance: SPICE vs 3-element model, and the corner envelope
f, Y = S.ac(p, "tt", 27, (1.8,))[1.8]
s = 2j*np.pi*f
Ym = s*nom["C2"] + 1/(nom["R"] + 1/(s*nom["C1"]))
fig, ax = plt.subplots(1, 3, figsize=(12.5, 3.8))
ax[0].loglog(f, 1/np.abs(Y), color=P[0], lw=2.2, label="SPICE, drawn filter (tt, 27 °C, 1.8 V)")
ax[0].loglog(f, 1/np.abs(Ym), "--", color=INK, lw=1, label="R1 + C1 ∥ C2 model (fitted)")
fz = 1/(2*np.pi*nom["R"]*nom["C1"]); fp = (nom["C1"] + nom["C2"])/(2*np.pi*nom["R"]*nom["C1"]*nom["C2"])
for x, t in ((fz, "zero"), (fp, "pole")):
    ax[0].axvline(x, color=MUTED, lw=0.8, ls=":"); ax[0].text(x*1.08, 2e5, f"{t}\n{x/1e6:.2f} MHz", color=MUTED, fontsize=8)
ax[0].text(fp*1.08, 9e4, "(filter alone;\n7.8 MHz with\nthe 175 fF load)", color=MUTED, fontsize=7)
ax[0].set_xlabel("frequency (Hz)"); ax[0].set_ylabel("|Z| (Ω)"); ax[0].legend(frameon=False, fontsize=8)
style(ax[0], "Filter impedance seen from vctl")
ax[1].semilogx(f, np.degrees(np.angle(1/Y)), color=P[0], lw=2.2)
ax[1].semilogx(f, np.degrees(np.angle(1/Ym)), "--", color=INK, lw=1)
ax[1].set_xlabel("frequency (Hz)"); ax[1].set_ylabel("phase of Z (°)"); style(ax[1], "Phase: −90° → lead → −90°")
err = np.abs(Ym - Y)/np.abs(Y)*100
ax[2].semilogx(f, err, color=P[1], lw=2)
ax[2].set_xlabel("frequency (Hz)"); ax[2].set_ylabel("|model − SPICE| / |SPICE| (%)")
style(ax[2], f"Model error (worst over 225 runs: {max(r['err_max'] for r in C)*100:.2f} %)")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "lf_hv_z.png"), dpi=150); plt.close(fig)

# 2 --- R1, C1, C2 over corners, temperature and V_cont
fig, ax = plt.subplots(1, 3, figsize=(12.5, 3.8))
for i, m in enumerate(S.MOS):
    for ls, temp in ((":", -40), ("-", 27), ("--", 110)):
        rr = sorted([r for r in C if r["mos"] == m and r["rc"] == "tt" and r["temp"] == temp], key=lambda r: r["vc"])
        ax[0].plot([r["vc"] for r in rr], [r["C1"]*1e12 for r in rr], ls, color=P[i], lw=1.8,
                   label=f"{m}" if temp == 27 else None)
ax[0].set_xlabel("V_cont (V)"); ax[0].set_ylabel("C1 (pF)"); ax[0].legend(frameon=False, fontsize=8, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.17),
             title="MOS corner (— 27, ··· −40, -- 110 °C)", title_fontsize=7.5)
style(ax[0], "C1 (2 tiles): MOS share follows V_cont")
for i, rc in enumerate(S.RCC):
    rcn = rc or "tt"
    rr = sorted([r for r in C if r["mos"] == "tt" and r["rc"] == rcn and r["vc"] == 1.8], key=lambda r: r["temp"])
    ax[1].plot([r["temp"] for r in rr], [r["R"]/1e3 for r in rr], "-o", color=P[i], ms=4, lw=1.8, label=rcn)
    ax[2].plot([r["temp"] for r in rr], [r["C2"]*1e12 for r in rr], "-o", color=P[i], ms=4, lw=1.8, label=rcn)
ax[1].set_xlabel("temperature (°C)"); ax[1].set_ylabel("R1 (kΩ)"); ax[1].legend(frameon=False, fontsize=8, title="R/C corner", title_fontsize=7.5)
style(ax[1], "R1: xhigh poly, negative TC")
ax[2].set_xlabel("temperature (°C)"); ax[2].set_ylabel("C2 (pF, filter only)"); style(ax[2], "C2: MIM, corner only")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "lf_hv_corners.png"), dpi=150); plt.close(fig)

# 3 --- loop at the PVT points: gain, closed loop, step; robustness map
fig, ax = plt.subplots(1, 3, figsize=(12.5, 3.8))
ff = np.logspace(4, np.log10(0.49/S.T), 500)
for i, r in enumerate(LP["rows"]):
    lab = f"{r['name'].split(',')[0]}, {r['vc']} V"
    Lg = sl.loop_gain(ff, r["R"], r["C1"], r["C2"] + r["cl"], 2*np.pi*r["kv"], r["beta"], S.T, r["tp"])
    H = Lg/(1 + Lg)
    ax[0].semilogx(ff, 20*np.log10(np.abs(Lg)), color=P[i], lw=1.8, label=f"{lab}: PM {r['pm']:.1f}°")
    ax[1].semilogx(ff, 20*np.log10(np.abs(H)), color=P[i], lw=1.8, label=f"{lab}: {r['peak']:.2f} dB")
    t, e, _ = sl.step(r["R"], r["C1"], r["C2"] + r["cl"], 2*np.pi*r["kv"], r["beta"], S.T, r["tp"], ncyc=100, phi_step=1.0)
    ax[2].plot(t*1e6, e, color=P[i], lw=1.6, label=f"{lab}: {r['settle']*1e6:.2f} µs")
ax[0].axhline(0, color=MUTED, lw=0.8); ax[0].set_ylim(-30, 50)
ax[0].set_xlabel("frequency (Hz)"); ax[0].set_ylabel("|L| (dB)"); ax[0].legend(frameon=False, fontsize=7.5)
style(ax[0], "Open loop (exact sampled model)")
ax[1].set_ylim(-12, 5); ax[1].set_xlabel("frequency (Hz)"); ax[1].set_ylabel("|H| (dB)"); ax[1].legend(frameon=False, fontsize=7.5)
style(ax[1], "Closed loop: peaking")
ax[2].set_xlabel("time (µs)"); ax[2].set_ylabel("phase error (rad)"); ax[2].legend(frameon=False, fontsize=7.5)
style(ax[2], "1 rad reference step: settling to ±10 ps")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "lf_hv_loop.png"), dpi=150); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
for i, (k, v) in enumerate(LP["rob"].items()):
    a = np.array([x for x in v["pts"] if x[2] == x[2]])
    col = P[["nominal", "R C min", "R C max"].index(k.split(" |")[0])]
    ls = {"1.8": ":", "2.6": "-", "4.2": "--"}[k.split("t_p ")[1][:3]]
    ax[0].semilogx(a[:, 0], a[:, 2], ls, color=col, lw=1.8, label=k)
    ax[1].loglog(a[:, 0], a[:, 1]/1e6, ls, color=col, lw=1.8)
ax[0].axhline(45, color=MUTED, lw=0.8, ls=":"); ax[0].set_xlabel("loop-gain multiplier m = β K_VCO / (β K_VCO)_nom")
ax[0].set_ylabel("PM (°)"); ax[0].legend(frameon=False, fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.55, -0.17)); style(ax[0], "Phase margin vs gain, filter corners × t_p")
ax[1].set_xlabel("m"); ax[1].set_ylabel("f_c (MHz)"); style(ax[1], "Crossover vs gain")
import matplotlib.ticker as mt
for a_ in ax:
    a_.xaxis.set_major_formatter(mt.FormatStrFormatter("%g")); a_.xaxis.set_minor_formatter(mt.NullFormatter())
    a_.set_xticks([0.4, 0.6, 1, 2, 3])
ax[1].yaxis.set_major_formatter(mt.FormatStrFormatter("%g")); ax[1].yaxis.set_minor_formatter(mt.NullFormatter())
ax[1].set_yticks([1, 2, 3, 4, 6])
for a_ in ax:
    a_.axvspan(0.75, 1.3, color=P[2], alpha=0.08)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "lf_hv_robust.png"), dpi=150); plt.close(fig)

# 4 --- noise and the packet
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
fn, vn, vp = np.array(N["f"]), np.array(N["ideal_r"]), np.array(N["pdk"])
k = 1.380649e-23; Tk = 300.15
Ct = nom["C1"] + nom["C2"]; tp_ = nom["R"]*nom["C1"]*nom["C2"]/Ct
th = np.sqrt(4*k*Tk*nom["R"]*(nom["C1"]/Ct)**2/(1 + (2*np.pi*fn*tp_)**2))
ax[0].loglog(fn, vn*1e9, color=P[0], lw=2.2, label="SPICE, R1 as an ideal resistor")
ax[0].loglog(fn, vp*1e9, color=P[1], lw=2.2, label="SPICE, PDK poly R1 (noiseless model!)")
ax[0].loglog(fn, th*1e9, "--", color=INK, lw=1, label="4kTR1 · (C1/C_tot)² / (1 + (ωτ_p)²)")
ax[0].set_xlabel("frequency (Hz)"); ax[0].set_ylabel("noise at vctl (nV/√Hz)"); ax[0].legend(frameon=False, fontsize=8)
style(ax[0], "Filter noise at vctl (Gm side open)")
t = np.array(PU["t"])*1e9; m_ = (t > 8) & (t < 120)
ax[1].plot(t[m_], np.array(PU["v"])[m_]*1e3, color=P[0], lw=2.2, label="SPICE, drawn filter + 175 fF load")
ax[1].plot(t[m_], np.array(PU["vi"])[m_]*1e3, "--", color=INK, lw=1, label="3-element model")
ax[1].axhline(PU["dv_ideal"]*1e3, color=MUTED, lw=0.8, ls=":")
ax[1].text(95, PU["dv_ideal"]*1e3 - 0.09, "q / C_tot", color=MUTED, fontsize=8)
ax[1].set_xlabel("time (ns)"); ax[1].set_ylabel("Δvctl (mV)"); ax[1].legend(frameon=False, fontsize=8)
style(ax[1], f"One Gm packet ({PU['q']*1e15:.2f} fC in 0.53 ns)")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "lf_hv_noise_pulse.png"), dpi=150); plt.close(fig)
print("-> docs/img/lf_hv_{z,corners,loop,robust,noise_pulse}.png")
