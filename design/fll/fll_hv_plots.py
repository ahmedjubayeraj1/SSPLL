#!/usr/bin/env python3
"""fll_hv_plots.py - figures of step 81 (FLL): docs/img/fll_hv_*.png. Run fll_hv_acq.py, fll_hv_sim.py and
fll_hv_closed.py first."""
import os, sys, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import fll_hv_model as M
P = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
IMG = os.path.join(ROOT, "docs", "img")
J = lambda n: json.load(open(os.path.join(HERE, "data", f"fll_hv_{n}.json"))) \
    if os.path.exists(os.path.join(HERE, "data", f"fll_hv_{n}.json")) else None


def style(ax, title):
    ax.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_title(title, loc="left", color=INK, fontsize=10)


# 1 --- acquisition from four start voltages (tt), FLL + SSPLL
fig, ax = plt.subplots(1, 3, figsize=(13, 3.9))
for i, v0 in enumerate((0.0, 1.0, 2.5, 3.3)):
    o = M.simulate(v0, "tt", tstop=4e-6, theta0=0.3)
    t = o["t"]*1e6
    ax[0].plot(t, o["v"], color=P[i], lw=1.6, label=f"start {v0} V")
    ax[1].plot(t, o["f"]/1e6, color=P[i], lw=1.6)
    ph = (o["ph"] - o["ph"][-1])/M.F0*1e12
    ax[2].plot(t, np.clip(ph, -2000, 2000), color=P[i], lw=1.4)
    tl = t[np.argmax(o["lock"])]
    ax[0].plot([tl], [np.interp(tl, t, o["v"])], "o", color=P[i], ms=5)
ax[0].set_xlabel("time (µs)"); ax[0].set_ylabel("V_cont (V)"); ax[0].legend(frameon=False, fontsize=8)
style(ax[0], "V_cont (dot: lock_det rises)")
ax[1].set_xlabel("time (µs)"); ax[1].set_ylabel("ring frequency (MHz)"); ax[1].set_ylim(550, 1000)
style(ax[1], "Frequency: FLL pulls to 16 × 50 MHz")
ax[2].set_xlabel("time (µs)"); ax[2].set_ylabel("ring phase − final (ps)"); ax[2].set_ylim(-1500, 1500)
style(ax[2], "Phase: the SSPLL finishes the job")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "fll_hv_acq.png"), dpi=150); plt.close(fig)

# 2 --- lock time statistics
A = J("acq")
if A:
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 3.9))
    groups = {}
    for r in A["A"]:
        groups.setdefault(r["p"]["icp"], []).append(r)
    xs = sorted(groups)
    for i, k in enumerate(xs):
        tl = [r["t_lock"]*1e6 for r in groups[k] if r["ok"]]
        nf = sum(not r["ok"] for r in groups[k])
        ax[0].scatter(np.full(len(tl), i) + np.random.default_rng(1).uniform(-0.15, 0.15, len(tl)), tl, s=10,
                      color=P[0], alpha=0.6)
        ax[0].plot([i - 0.25, i + 0.25], [np.median(tl)]*2, color=INK, lw=1.5)
        if nf:
            ax[0].text(i, 9.6, f"{nf} of {len(groups[k])}\nno lock", ha="center", color=P[1], fontsize=8)
    ax[0].set_xticks(range(len(xs))); ax[0].set_xticklabels([f"{k*1e6:.0f}" for k in xs])
    ax[0].set_xlabel("FLL charge-pump current I_cp (µA)"); ax[0].set_ylabel("lock time to ±10 ps (µs)"); ax[0].set_ylim(0, 11)
    style(ax[0], "Lock time: 5 start voltages × 3 corners × 4 phases")
    labs, med, mx = [], [], []
    for r in A["B_sum"] + A["C_sum"]:
        k = r["key"]
        if k.startswith("icp"):
            a_, b_ = k.split(", "); k = f"I_cp {float(a_.split()[1])*1e6:.0f} µA, β ×{b_.split()[1]}"
        elif k.startswith("t_"):
            nm_, v_ = k.split(); k = f"{nm_} {float(v_)*1e9:.1f} ns"
        labs.append(k); med.append((r["typ"] or 0)*1e6); mx.append((r["max"] or 0)*1e6)
    y = np.arange(len(labs))
    ax[1].barh(y, mx, color=P[0], alpha=0.35, label="max"); ax[1].barh(y, med, color=P[0], label="median")
    for i, r in enumerate(A["B_sum"] + A["C_sum"]):
        if r["fail"]:
            ax[1].text(mx[i] + 0.1, i, f"{r['fail']} fail", va="center", color=P[1], fontsize=8)
    ax[1].set_yticks(y); ax[1].set_yticklabels(labs, fontsize=7.5); ax[1].invert_yaxis()
    ax[1].set_xlabel("lock time (µs)"); ax[1].legend(frameon=False, fontsize=8)
    style(ax[1], "Lock-detector settings and robustness")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "fll_hv_locktime.png"), dpi=150); plt.close(fig)

# 3 --- open loop: dead-zone transfer, lock detector; charge pump; divider
O, CP, DV = J("open"), J("cp"), J("div")
if O and CP and DV:
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.9))
    for i, r in enumerate(O):
        a = [x for x in r["rows"] if x["dt"] is not None and abs(x["dt"]) < 4e-9]
        dt = np.array([x["dt"] for x in a])*1e9; q = np.array([x["q"] for x in a])*1e15
        lk = np.array([x["lock"] > 0.9 for x in a])
        ax[0].plot(dt, q, ".", color=P[i], ms=4, label=f"{r['corner']} {r['temp']} °C")
        ax[0].plot(dt[lk], q[lk], "o", mfc="none", color=P[i], ms=7)
    ax[0].plot([-4, -0.4, 0.4, 4], [60e-6*3.6e-9*1e15, 0, 0, -60e-6*3.6e-9*1e15], "--", color=MUTED, lw=1, label="−60 µA × (Δt ∓ 0.4 ns)")
    ax[0].set_xlabel("Δt = UP width − DN width (ns); > 0: ring slow"); ax[0].set_ylabel("charge per period (fC)")
    ax[0].legend(frameon=False, fontsize=8); style(ax[0], "Charge per period; circles: lock_det = 1 (pump off)")
    for i, r in enumerate([x for x in CP["rows"] if x["ib"] == 5e-6]):
        ax[1].plot(r["v"], np.array(r["isink"])*1e6, "-o", ms=3, color=P[i], label=f"sink, {r['corner']} {r['temp']} °C")
        ax[1].plot(r["v"], np.array(r["isrc"])*1e6, "--s", ms=3, color=P[i], label=f"source")
    ax[1].axvspan(1.3, 2.3, color=P[2], alpha=0.08); ax[1].set_xlabel("V_cont (V)"); ax[1].set_ylabel("current (µA)")
    ax[1].legend(frameon=False, fontsize=7, ncol=2); style(ax[1], "Charge pump (IBIAS 5 µA; band = lock window)")
    labs = [f"{r['corner']} {r['temp']} °C\n{r['vddd']} V" for r in DV]
    ax[2].bar(range(len(DV)), [r["fmax"]/1e9 for r in DV], color=P[0], label="divider f_max")
    ring = {"tt": 1.25, "ss": 1.01, "ff": 1.95, "sf": 1.01, "fs": 1.95}
    ax[2].bar(range(len(DV)), [ring[r["corner"]] for r in DV], color=P[1], width=0.4, label="ring at code 31, V_cont 0")
    ax[2].set_xticks(range(len(DV))); ax[2].set_xticklabels(labs, fontsize=7.5); ax[2].set_ylabel("GHz")
    ax[2].legend(frameon=False, fontsize=8); style(ax[2], "Divider speed vs the fastest ring")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "fll_hv_blocks.png"), dpi=150); plt.close(fig)

# 4 --- closed loop: transistor FLL vs model (model from 8 start phases: the divider's start state is random)
CL = J("closed")
if CL:
    fig, ax = plt.subplots(1, 1, figsize=(7.5, 3.9))
    for i, r in enumerate(CL):
        tl = []
        for th in np.linspace(0.02, 15.9, 8):
            o = M.simulate(r["v0"], r["corner"], dict(sspll=False), tstop=2.5e-6, theta0=th)
            ax.plot(o["t"]*1e6, o["v"], color=P[i], lw=0.6, alpha=0.45)
            if o["lock"].any():
                tl.append(o["t"][np.argmax(o["lock"])])
        r["model_tl"] = (min(tl), max(tl)) if tl else None
        ax.plot(np.array(r["t"])*1e6, r["v"], color=P[i], lw=2.4,
                label=f"transistor FLL, start {r['v0']} V")
        if r["t_lock"]:
            ax.axvline(r["t_lock"]*1e6, color=P[i], lw=0.8, ls=":")
        print(f"  start {r['v0']} V: lock_det transistor {r['t_lock']*1e6:.2f} us, model (8 start phases) "
              f"{r['model_tl'][0]*1e6:.2f}-{r['model_tl'][1]*1e6:.2f} us")
    ax.plot([], [], color=MUTED, lw=0.6, label="model, 8 divider start phases (thin, same colour)")
    ax.set_xlabel("time (µs)"); ax.set_ylabel("V_cont (V)"); ax.legend(frameon=False, fontsize=8)
    style(ax, "FLL alone: transistor level vs model (dotted: lock_det)")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "fll_hv_closed.png"), dpi=150); plt.close(fig)
print("-> docs/img/fll_hv_{acq,locktime,blocks,closed}.png")
