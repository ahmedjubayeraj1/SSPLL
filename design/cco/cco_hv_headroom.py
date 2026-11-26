#!/usr/bin/env python3
"""cco_hv_headroom.py - the cascoded CCO needs V_SD(MOUT) + V_SD(MC) above both devices' V_dsat; at the worst corner
(ss / 110 C, VDDA 2.97 V, ring node 2.37 V for 880 MHz) only 0.60 V is left, and with 40 um units both devices sat in
triode there (V_dsat 0.49 V each): K_vdd = 248 MHz/V at that corner. Wider units lower V_dsat (and raise g_m, i.e.
noise). Sweep the unit widths and the cascode-bias diode; report worst-corner current and K_vdd, tt K_vdd and tt noise.
-> data/cco_hv_headroom.json"""
import json, os, re
from multiprocessing import Pool
import numpy as np
import cco_hv as c
KI = {"tt": 0.62e12, "ss": 0.41e12}
P5 = "pfet_g5v0d10v5"
CANDS = {
    "W40_W40":   dict(c.D),
    "W80_W80":   dict(c.D, UP=(P5, 20.0, 4, 2.0), CASC=(P5, 20.0, 4, 0.5)),
    "W80_W160":  dict(c.D, UP=(P5, 20.0, 4, 2.0), CASC=(P5, 20.0, 8, 0.5)),
    "W120_W160": dict(c.D, UP=(P5, 20.0, 6, 2.0), CASC=(P5, 20.0, 8, 0.5)),
    "W80_W160_MB4": dict(c.D, UP=(P5, 20.0, 4, 2.0), CASC=(P5, 20.0, 8, 0.5), MB=(P5, 4.0, 1, 4.0)),
}
CANDS2 = {
    "W40_W40_MB4": dict(c.D, MB=(P5, 4.0, 1, 4.0)),
    "W40_W80_MB4": dict(c.D, CASC=(P5, 20.0, 4, 0.5), MB=(P5, 4.0, 1, 4.0)),
    "W80_W160_MB4_C8_CC4": dict(c.D, UP=(P5, 20.0, 4, 2.0), CASC=(P5, 20.0, 8, 0.5), MB=(P5, 4.0, 1, 4.0),
                                CTILE=("cap_mim_m3_1", 8, 30.0), CCAS=("cap_mim_m3_1", 4, 30.0)),
    "W40_W80_MB4_C6_CC4": dict(c.D, CASC=(P5, 20.0, 4, 0.5), MB=(P5, 4.0, 1, 4.0),
                               CTILE=("cap_mim_m3_1", 6, 30.0), CCAS=("cap_mim_m3_1", 4, 30.0)),
}
import sys
if len(sys.argv) > 1 and sys.argv[1] == "2":
    CANDS = CANDS2


def at1M(pairs):
    return min(pairs, key=lambda q: abs(q[0] - 1e6))[1]


def psr_at(p, corner, t, vdda, ib, code, vr):
    o = c.run(c.tb(p, corner, t, vdda=vdda, ib=ib, code=code, vring=f"vr vring 0 {vr}", vdda_ac=True,
                   ctl="ac dec 5 1e4 1e7\nprint abs(vr#branch)"))
    return at1M([(float(f), float(v)) for f, v in re.findall(r"^\d+\s+(\S+)\s+(\S+)", o, re.M)])


def one(name):
    p = CANDS[name]
    i_ss = c.op_current(p, "ss", 110, 2.97, 4e-6, 31, 2.37)
    i_ss15 = c.op_current(p, "ss", 110, 2.97, 4e-6, 31, 1.5)
    k_ss = psr_at(p, "ss", 110, 2.97, 4e-6, 31, 2.37)*KI["ss"]
    k_ss33 = psr_at(p, "ss", 110, 3.3, 4e-6, 31, 2.37)*KI["ss"]
    k_tt = psr_at(p, "tt", 27, 3.3, 5e-6, 10, 1.89)*KI["tt"]
    f, n = c.noise(p)
    return name, dict(i_ss=abs(i_ss), i_ss15=abs(i_ss15), k_ss=k_ss, k_ss33=k_ss33, k_tt=k_tt,
                      n1M=float(n[np.argmin(abs(f - 1e6))]), n100k=float(n[np.argmin(abs(f - 1e5))]))


if __name__ == "__main__":
    with Pool(2) as pool:
        res = dict(pool.map(one, list(CANDS)))
    for k, r in res.items():
        print(f"{k:14s} ss worst: I {r['i_ss']*1e3:.3f} mA ({100*(1-r['i_ss']/r['i_ss15']):.1f} % below 1.5 V) K_vdd {r['k_ss']/1e6:6.1f} MHz/V "
              f"(at VDDA 3.3: {r['k_ss33']/1e6:5.1f}) | tt K_vdd {r['k_tt']/1e6:5.2f} MHz/V | tt noise 100k/1M {r['n100k']*1e12:.1f}/{r['n1M']*1e12:.2f} pA/rtHz")
    fn = os.path.join(c.HERE, "data", "cco_hv_headroom.json")
    old = json.load(open(fn)) if os.path.exists(fn) else {}
    old.update(res); json.dump(old, open(fn, "w"), indent=1)
