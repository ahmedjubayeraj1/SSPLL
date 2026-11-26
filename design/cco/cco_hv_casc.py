#!/usr/bin/env python3
"""cco_hv_casc.py - cascoded output stage for the 5 V CCO: the plain mirror gave K_vdd = 66-110 MHz/V
(target <= 5) because MOUT's C_gd ties its gate to the (AC-quiet) ring node, so the gate does not follow VDDA. A
cascode MC whose gate (vcas) follows VDDA moves MOUT's drain with VDDA. Sweep the bias diode MB (sets how much of the
0.60 V headroom MOUT and MC each get) and report compliance at the worst corner, K_vdd and noise. -> data/cco_hv_casc.json"""
import json, os
from multiprocessing import Pool
import numpy as np
import cco_hv as c
KI = 0.62e12
BASE = dict(c.D, CASC=("pfet_g5v0d10v5", 20.0, 2, 0.5), KB=4, CCAS=("cap_mim_m3_1", 1, 20.0))
CANDS = {f"MB_W{w}_L{l}": dict(BASE, MB=("pfet_g5v0d10v5", w, 1, l)) for w, l in ((2.0, 4.0), (1.0, 4.0), (1.0, 8.0), (0.5, 8.0))}


def one(name):
    p = CANDS[name]
    comp = [(vr, c.op_current(p, "ss", 110, 2.97, 4e-6, 31, vr)) for vr in (1.5, 2.0, 2.2, 2.37, 2.5)]
    comp_tt = [(vr, c.op_current(p, "tt", 27, 3.3, 5e-6, 10, vr)) for vr in (1.5, 1.89, 2.3, 2.6)]
    ps = c.psr(p)
    f, n = c.noise(p)
    psr_at = {str(x): float(min(ps, key=lambda q: abs(q[0] - x))[1]) for x in (1e3, 1e4, 1e5, 1e6, 1e7)}
    noi = {str(x): float(n[np.argmin(abs(f - x))]) for x in (1e4, 1e5, 1e6, 1e7)}
    return name, dict(comp=comp, comp_tt=comp_tt, psr=psr_at, kvdd=psr_at["1000000.0"]*KI, noise=noi)


if __name__ == "__main__":
    with Pool(2) as pool:
        res = dict(pool.map(one, list(CANDS)))
    for k, r in res.items():
        comp = r["comp"]; drop = 1 - comp[3][1]/comp[0][1]
        print(f"{k:12s} ss: " + " ".join(f"{v}V:{abs(i)*1e3:.3f}" for v, i in comp) + f" (drop {100*drop:.1f} %) | tt: " +
              " ".join(f"{v}V:{abs(i)*1e3:.3f}" for v, i in r["comp_tt"]) + " | dI/dVDDA " +
              " ".join(f"{float(f):.0e}:{v*1e6:.2f}" for f, v in r["psr"].items()) + f" uA/V -> K_vdd(1M) {r['kvdd']/1e6:.2f} MHz/V | "
              f"noise 10k/100k/1M {r['noise']['10000.0']*1e12:.0f}/{r['noise']['100000.0']*1e12:.1f}/{r['noise']['1000000.0']*1e12:.2f}")
    json.dump(res, open(os.path.join(c.HERE, "data", "cco_hv_casc.json"), "w"), indent=1)
