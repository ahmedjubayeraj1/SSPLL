#!/usr/bin/env python3
"""refbuf_hv_plots.py - figures of the receiver redo (5 V REF receiver, VDDD level shifter): docs/img/refbuf_hv_*.png.
Run refbuf_hv_sim.py, refbuf_hv_supply.py and refbuf_hv_noise.py first."""
import os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(HERE, "..", "..", "docs", "img")
INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"; P = ["#2a78d6", "#eb6834", "#1baf7a", "#f0a30a", "#8250df"]
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
ld = lambda n: json.load(open(os.path.join(HERE, "data", f"refbuf_hv_{n}.json")))
def style(ax, t):
    ax.set_title(t, loc="left", color=INK, fontsize=10.5); ax.grid(True, color=GRID); ax.set_axisbelow(True)
S, U, N = ld("sim"), ld("supply"), ld("noise")

# 1 --- large signal: delay and duty vs amplitude at tt, and over corners
fig, ax = plt.subplots(1, 2, figsize=(12, 6.5), gridspec_kw=dict(width_ratios=[1, 1.3]))
a = [r for r in S["tran"] if r["corner"] == "tt" and r["vddd"] == 1.8 and r["f"] == 50e6]
sn = sorted([r for r in a if r["wave"] == "sine"], key=lambda r: r["vpp"])
ax[0].plot([r["vpp"] for r in sn], [r["delay"]*1e9 for r in sn], "-o", color=P[0], label="delay (ns), sine")
ax[0].plot([r["vpp"] for r in sn], [r["duty"]*10 for r in sn], "-s", color=P[1], label="duty / 10 (%), sine")
sq = [r for r in a if r["wave"] == "square"][0]
ax[0].plot([3.3], [sq["delay"]*1e9], "D", color=P[0], ms=8, label=f"3.3 V square: {sq['delay']*1e12:.0f} ps, duty {sq['duty']*100:.1f} %")
ax[0].set_xlabel("REF_IN amplitude (V pp)"); style(ax[0], "Delay and duty at tt, 50 MHz"); ax[0].legend(frameon=False, fontsize=8)
c = [r for r in S["tran"] if r["corner"] != "tt" and r["f"] == 50e6]
lab = [f"{r['corner']} {r['temp']}°C, {r['vdda']}/{r['vddd']} V, {r['vpp']} V {r['wave']}" for r in c]
y = np.arange(len(c))
ax[1].barh(y, [r["delay"]*1e9 for r in c], color=[P[0] if r["wave"] == "square" else P[2] for r in c])
ax[1].set_yticks(y, lab, fontsize=7); ax[1].set_xlim(0, 3.0); ax[1].set_xlabel("delay REF_IN → refclk (ns)")
for k, r in enumerate(c):
    ax[1].text(r["delay"]*1e9 + 0.03, k, f"duty {r['duty']*100:.0f} %, {r['power']*1e3:.2f} mW", va="center", fontsize=7, color=MUTED)
style(ax[1], "Corners × supply limits (blue: 3.3 V square, green: 0.4 V sine)")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "refbuf_hv_tran.png"), dpi=150)

# 2 --- supply sensitivity vs ripple frequency
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for k, rail in enumerate(("vdda", "vddd")):
    for (vpp, w), col in zip(((3.3, "square"), (1.0, "sine")), P):
        pts = sorted((max(x["fm"], 1e3), abs(x["k"])*1e12) for x in U if x["rail"] == rail and x["vpp"] == vpp)
        ax[k].semilogx(*np.array(pts).T, "-o", color=col, label=f"{vpp} V pp {w}")
    ax[k].set_xlabel("supply ripple frequency (Hz); 1 kHz point = DC step"); ax[k].set_ylabel("|Δt_edge / ΔV| (ps/V)")
    ax[k].set_ylim(0, None)
    style(ax[k], f"{rail.upper()} → refclk edge"); ax[k].legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "refbuf_hv_supply.png"), dpi=150)

# 3 --- phase noise of the receiver at the reference, its parts, and the chain against the target
fl = np.array(N["fL"])
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for k, key in enumerate(("3.3_typ", "1.0_typ")):
    L = N["L"][key]
    for nm, col, ls in (("white", P[0], "-"), ("slow", P[4], "-"), ("vdda", P[1], "--"), ("vddd", P[2], "--"), ("chain", INK, "-")):
        ax[k].semilogx(fl, L[nm], ls, color=col, lw=2 if nm == "chain" else 1.3,
                       label={"white": "S1 + output chain, white", "slow": "S1 flicker / R_B (quasi-static)",
                              "vdda": "VDDA 100 nV/√Hz", "vddd": "VDDD 100 nV/√Hz", "chain": "REF chain total (+ clock gen, SSPD buffers)"}[nm])
    ax[k].axhline(-155, color=P[3], ls=":"); ax[k].text(1.2e3, -154, "target −155 dBc/Hz", color=MUTED, fontsize=8)
    ax[k].set_ylim(-200, -130); ax[k].set_xlabel("offset (Hz)"); ax[k].set_ylabel("L at 50 MHz (dBc/Hz)")
    style(ax[k], ("3.3 V pp square (CMOS XO)" if k == 0 else "1 V pp sine") + ", typ"); ax[k].legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "refbuf_hv_noise.png"), dpi=150)

# 4 --- start-up
st = S["startup"]
fig, ax = plt.subplots(1, 1, figsize=(11, 3.4))
for (k, v), col in zip(st.items(), P):
    t, x = np.array(v["t"]), np.array(v["vin"]); w = 60                       # window ~ several reference periods
    n = len(x)//w; tt = t[:n*w].reshape(n, w).mean(1); hi = x[:n*w].reshape(n, w).max(1); lo = x[:n*w].reshape(n, w).min(1)
    ax.fill_between(tt*1e6, lo, hi, color=col, alpha=0.15, lw=0)
    ax.plot(tt*1e6, (hi + lo)/2, color=col, label=f"centre of v(vin), {k.replace('_', ' ')} °C; refclk settled at {v['t_settled']*1e6:.2f} µs")
ax.axvline(0.5, color=MUTED, ls=":"); ax.text(0.55, ax.get_ylim()[1]*0.95, "pll_en ↑", color=MUTED, fontsize=8)
ax.set_xlabel("time (µs)"); ax.set_ylabel("V"); style(ax, "Start-up: the centre of the AC-coupled input (shaded: its swing) climbs to the trip point")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "refbuf_hv_startup.png"), dpi=150)
print("figures written")
