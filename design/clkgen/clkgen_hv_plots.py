#!/usr/bin/env python3
"""clkgen_hv_plots.py - figures of the clock-generator redo (clock generator with 3.3 V outputs): docs/img/clkgen_hv_*.png.
Run clkgen_hv_sim.py (and --timing), clkgen_hv_supply.py and clkgen_hv_noise.py first."""
import os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import clkgen_hv as K
HERE = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(HERE, "..", "..", "docs", "img")
INK, MUTED, GRID = "#1f2328", "#59636e", "#e6e8eb"; P = ["#2a78d6", "#eb6834", "#1baf7a", "#f0a30a", "#8250df", "#d1495b"]
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
ld = lambda n: json.load(open(os.path.join(HERE, "data", f"clkgen_hv_{n}.json")))
def style(ax, t):
    ax.set_title(t, loc="left", color=INK, fontsize=10.5); ax.grid(True, color=GRID); ax.set_axisbelow(True)
S, U, N = ld("sim"), ld("supply"), ld("noise")
U1, UO = ld("supply_1v"), ld("supply_via_vddd")

# 1 --- waveforms at tt (one period after refclk rises)
T = 20e-9
net = (f"* w\n.lib {K.LIB} tt\n.temp 27\n{K.cells()}vddd VDDD 0 1.8\nvdda VDDA 0 3.3\n"
       f"vrh refhv 0 pulse(0 3.3 5n 0.3n 0.3n 9.7n 20n)\nvin refclk 0 pulse(0 1.8 5.2n 0.3n 0.3n 9.7n 20n)\n"
       "x1 refclk refhv cks cksb ckg ckgb ckh ckhb VDDD VDDA 0 0 sspll_clkgen_hv\n" +
       "".join(f"c{k} {k} 0 {v}\n" for k, v in K.LOADS.items()) +
       ".control\ntran 2p 50n\nwrdata w.txt v(refclk) v(cks) v(cksb) v(ckg) v(ckgb) v(ckh) v(ckhb)\n.endc\n.end\n")
_, d = K.run(net, ["w.txt"]); z = d["w.txt"]; t = z[:, 0]; w = (t > 44.6e-9) & (t < 51.5e-9)
fig, ax = plt.subplots(4, 1, figsize=(11, 6.2), sharex=True)
for a, (i, nm, col) in zip(ax, ((1, "refclk (1.8 V, VDDD; refhv 0.2 ns earlier)", INK), (2, "cks / cksb", P[0]), (4, "ckg / ckgb (Gm pulse)", P[1]),
                               (6, "ckh / ckhb (hold)", P[2]))):
    a.plot((t[w] - 45e-9)*1e9, z[w, 2*i - 1], color=col)
    if i > 1:
        a.plot((t[w] - 45e-9)*1e9, z[w, 2*i + 1], color=col, ls="--")
    a.set_ylabel("V"); a.text(0.01, 0.75, nm, transform=a.transAxes, color=MUTED, fontsize=8); a.grid(True, color=GRID)
ax[-1].set_xlabel("time after the refclk rising edge (ns)")
ax[0].set_title("Clock generator outputs at tt, 27 °C (solid: true phase, dashed: complement)", loc="left", fontsize=10.5)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "clkgen_hv_timing.png"), dpi=150)

# 2 --- corners: tau x K_VCO, gaps, W_H
R = [r for r in S["timing"] if not r.get("failed")]
lab = [f"{r['corner']} {r['temp']}°C {r['vddd']}/{r['vdda']} V" + (f" {r['f']/1e6:.0f} MHz" if r['f'] != 50e6 else "") +
       (f" {r['vpp']} V {r['wave']}" if (r['wave'], r['vpp']) != ("square", 3.3) else "") for r in R]
y = np.arange(len(R))
fig, ax = plt.subplots(1, 3, figsize=(13, 7.5), sharey=True)
ax[0].barh(y, [r["tau"]*1e12 for r in R], color=P[1]); ax[0].set_xlabel("τ (ps)"); style(ax[0], "Gm pulse width τ")
ax[0].set_yticks(y, lab, fontsize=7)
ax[1].barh(y - 0.2, [r["gap1"]*1e12 for r in R], 0.4, color=P[0], label="gap 1 (sample → Gm)")
ax[1].barh(y + 0.2, [r["gap2"]*1e12 for r in R], 0.4, color=P[2], label="gap 2 (Gm → hold)")
ax[1].axvline(100, color=P[3], ls="--"); ax[1].set_xlabel("ps"); style(ax[1], "Non-overlap gaps (≥ 100 ps)")
ax[1].legend(frameon=False, fontsize=8)
ax[2].barh(y, [r["W_H"]*1e9 for r in R], color=P[4]); ax[2].axvline(1.5, color=P[3], ls="--")
ax[2].set_xlabel("ns"); style(ax[2], "Hold pulse W_H (≥ 1.5 ns)")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "clkgen_hv_corners.png"), dpi=150)

# 3 --- REF chain: supply sensitivity of the whole path and the chain's phase noise
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for (r, nm), col in zip((("vddd", "VDDD"), ("vdda", "VDDA")), P):
    pts = sorted((max(x["fm"], 1e3), abs(x["k"])*1e12) for x in U if x["rail"] == r)
    ax[0].semilogx(*np.array(pts).T, "-o", color=col, label=f"{nm}, 3.3 V square (final)")
    pts = sorted((max(x["fm"], 1e3), abs(x["k"])*1e12) for x in U1 if x["rail"] == r)
    ax[0].semilogx(*np.array(pts).T, "--s", color=col, ms=4, label=f"{nm}, 1 V sine (final)")
    pts = sorted((max(x["fm"], 1e3), abs(x["k"])*1e12) for x in UO if x["rail"] == r)
    ax[0].semilogx(*np.array(pts).T, ":^", color=col, ms=4, alpha=0.6, label=f"{nm}, first version (via refclk)")
ax[0].set_yscale("log"); ax[0].set_ylim(1, 3000); ax[0].set_xlabel("ripple frequency (Hz); 1 kHz point = DC step"); ax[0].set_ylabel("ps/V")
style(ax[0], "Supply → sampling edge, REF_IN → cks"); ax[0].legend(frameon=False, fontsize=8)
f = np.array(N["fL"]); L = N["L"]["3.3_typ"]
for k, col, ls, nm in (("rx_white", P[0], "-", "receiver, white"), ("clkgen", P[1], "-", "clock generator + LS (M17)"),
                       ("vdda", P[3], "--", "VDDA 100 nV/√Hz"), ("vddd", P[2], "--", "VDDD 100 nV/√Hz"),
                       ("sspd_buf", P[4], ":", "SSPD buffers (placeholder)"), ("chain", INK, "-", "REF chain total")):
    ax[1].semilogx(f, L[k], ls, color=col, lw=2 if k == "chain" else 1.3, label=nm)
ax[1].axhline(-155, color=P[3], ls=":"); ax[1].set_ylim(-190, -140); ax[1].set_xlabel("offset (Hz)")
ax[1].set_ylabel("L at 50 MHz (dBc/Hz)"); style(ax[1], "REF chain phase noise, typ, 3.3 V square"); ax[1].legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(IMG, "clkgen_hv_noise.png"), dpi=150)
print("figures written")
