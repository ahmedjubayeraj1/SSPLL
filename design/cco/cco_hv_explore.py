#!/usr/bin/env python3
"""cco_hv_explore.py - choice of the output-mirror unit for the 5 V CCO (step 75 redo): for each candidate unit
(W per finger x nf, L) measure (1) compliance: output current vs ring node at the worst headroom (code 31, IBIAS 4 uA,
ss/110 C, VDDA 2.97 V), (2) VDDA rejection |dI/dVDDA| and K_vdd = K_I x |dI/dVDDA| at tt (code 10, ring node 1.89 V),
(3) output noise at 10 kHz / 100 kHz / 1 MHz (tt). -> data/cco_hv_explore.json"""
import json, os
from multiprocessing import Pool
import numpy as np
import cco_hv as c
KI = 0.62e12                                  # Hz/A, step 74 HV ring near 1 mA (tt)
CANDS = {"L2_W40": ("pfet_g5v0d10v5", 20.0, 2, 2.0), "L2_W60": ("pfet_g5v0d10v5", 20.0, 3, 2.0),
         "L3_W60": ("pfet_g5v0d10v5", 20.0, 3, 3.0), "L4_W80": ("pfet_g5v0d10v5", 20.0, 4, 4.0),
         "L4_W120": ("pfet_g5v0d10v5", 20.0, 6, 4.0)}


def one(name):
    p = dict(c.D, UP=CANDS[name])
    comp = [(vr, c.op_current(p, "ss", 110, 2.97, 4e-6, 31, vr)) for vr in (1.5, 2.0, 2.2, 2.37, 2.5)]
    ps = c.psr(p)
    f, n = c.noise(p)
    at = lambda arr, x: float(arr[np.argmin(abs(np.array([a for a, _ in arr]) - x))][1]) if isinstance(arr, list) else None
    psr_at = {str(x): float(min(ps, key=lambda q: abs(q[0] - x))[1]) for x in (1e3, 1e5, 1e6, 1e7)}
    noi = {str(x): float(n[np.argmin(abs(f - x))]) for x in (1e4, 1e5, 1e6, 1e7)}
    i_tt = c.op_current(p, "tt", 27, 3.3, 5e-6, 10, 1.89)
    return name, dict(comp=comp, psr=psr_at, kvdd=psr_at["1000000.0"]*KI, noise=noi, i_tt=i_tt)


if __name__ == "__main__":
    with Pool(2) as pool:
        res = dict(pool.map(one, list(CANDS)))
    for k, r in res.items():
        comp = r["comp"]; drop = 1 - comp[3][1]/comp[0][1]
        print(f"{k:8s} I(tt,code10) {r['i_tt']*1e3:.3f} mA | compliance ss: " +
              " ".join(f"{v}V:{i*1e3:.3f}" for v, i in comp) + f" (drop to 2.37 V {100*drop:.1f} %) | "
              f"dI/dVDDA 1k {r['psr']['1000.0']*1e6:.1f} 1M {r['psr']['1000000.0']*1e6:.1f} uA/V -> K_vdd {r['kvdd']/1e6:.1f} MHz/V | "
              f"noise 10k/100k/1M {r['noise']['10000.0']*1e12:.0f}/{r['noise']['100000.0']*1e12:.1f}/{r['noise']['1000000.0']*1e12:.2f} pA/rtHz")
    json.dump(res, open(os.path.join(c.HERE, "data", "cco_hv_explore.json"), "w"), indent=1)
