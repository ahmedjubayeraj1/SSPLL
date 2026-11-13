#!/usr/bin/env python3
"""step8_variants.py - Type-II CP-PLL vs SSPLL vs SSPLL+FFNC with the same ring, reference and N (roadmap step 8).
Writes models/out/step8_variants.csv and docs/img/step8_variants_L.png.   Run from the repo root or models/."""
import os, sys, csv
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pllmodel import TYP, PESS, TYPE2_TYP, TYPE2_PESS, jitter, optimum_fc
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

ROOT = os.path.dirname(HERE)
os.makedirs(os.path.join(HERE, "out"), exist_ok=True); os.makedirs(os.path.join(ROOT, "docs", "img"), exist_ok=True)
cases = [("Type-II CP-PLL", "type2", TYPE2_TYP, TYPE2_PESS), ("SSPLL", "sspll", TYP, PESS),
         ("SSPLL + FFNC", "ffnc", TYP, PESS)]
rows = []
print(f"{'variant':16s} {'corner':5s} {'jitter@2.5MHz':>13s} {'VCO':>5s} {'REF':>5s} {'PD+CP':>6s} {'L(100k)':>8s} {'L(1M)':>7s}")
for name, v, dt, dp in cases:
    for corner, d in (("typ", dt), ("pess", dp)):
        j, f, L = jitter(d, v)
        at = lambda x: L[np.argmin(abs(f - x))]
        r = dict(variant=name, corner=corner, jitter_ps=j["TOTAL"] * 1e12, vco_ps=j["VCO"] * 1e12,
                 ref_ps=j["REF x N^2"] * 1e12, pd_ps=j["PD + CP"] * 1e12, L100k=at(1e5), L300k=at(3e5), L1M=at(1e6))
        rows.append(r)
        print(f"{name:16s} {corner:5s} {r['jitter_ps']:10.2f} ps {r['vco_ps']:5.2f} {r['ref_ps']:5.2f} {r['pd_ps']:6.2f} "
              f"{r['L100k']:8.1f} {r['L1M']:7.1f}")
with open(os.path.join(HERE, "out", "step8_variants.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

fig, ax = plt.subplots(figsize=(7.5, 4.4))
for (name, v, dt, _), c in zip(cases, ("#c2410c", "#1d4ed8", "#15803d")):
    j, f, L = jitter(dt, v)
    ax.semilogx(f, L, color=c, lw=1.8, label=f"{name}: {j['TOTAL']*1e12:.2f} ps rms")
ax.set(xlim=(1e3, 100e6), ylim=(-150, -80), xlabel="Offset frequency (Hz)", ylabel="L(f) at 1.6 GHz (dBc/Hz)",
       title="Same ring, reference and N = 32, loop bandwidth 2.5 MHz (typical)")
ax.axvspan(10e3, 40e6, color="0.92", zorder=0, label="jitter band 10 kHz-40 MHz")
ax.grid(True, which="both", lw=0.4, alpha=0.5); ax.legend(fontsize=8, loc="lower left")
fig.tight_layout(); p = os.path.join(ROOT, "docs", "img", "step8_variants_L.png"); fig.savefig(p, dpi=150)
print("->", p)
