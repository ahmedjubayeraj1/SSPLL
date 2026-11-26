#!/usr/bin/env python3
"""cco_hv_vdda.py - how VDDA rejection of the 5 V CCO depends on the supply level at the slow corner (method M11).

Why this run exists: at ss/110 C the ring needs a 2.37 V node for 880 MHz (top of the coarse range) and 2.25 V for
800 MHz (the operating point, the VCO characterisation: 1.32 mA). With VDDA at its -10 % limit (2.97 V) MOUT + cascode MC
have only 0.60 V (880 MHz) or 0.72 V (800 MHz) between them, both leave saturation, r_out collapses and K_vdd rises
to ~110 MHz/V (cco_hv_headroom.py). This sweep finds the VDDA level above which K_vdd is back near the 5 MHz/V
allocation, so the datasheet can state 'full jitter spec for VDDA >= x V, functional down to 2.97 V'.

Cases: ss/110 C, IBIAS 5 uA, code 17 (1.32 mA, 800 MHz) with the ring node at 2.25 V, and code 31 with IBIAS 4 uA at
2.37 V (880 MHz, the range edge); tt/27 C code 10 at 1.89 V as the reference. VDDA 2.97 ... 3.63 V.
-> data/cco_hv_vdda.json"""
import json, os
from multiprocessing import Pool
import cco_hv as c
KI = {"tt": 0.62e12, "ss": 0.41e12}
CASES = {"ss_800": ("ss", 110, 17, 5e-6, 2.25), "ss_880": ("ss", 110, 31, 4e-6, 2.37), "tt_800": ("tt", 27, 10, 5e-6, 1.89)}
VDDA = [2.97, 3.05, 3.13, 3.2, 3.3, 3.47, 3.63]


def one(args):
    tag, vdda = args
    cn, t, code, ib, vr = CASES[tag]
    o = c.run(c.tb(c.D, cn, t, vdda=vdda, ib=ib, code=code, vring=f"vr vring 0 {vr}", vdda_ac=True,
                   ctl="op\nprint -vr#branch\nac dec 5 1e2 1e8\nprint abs(vr#branch)"))
    import re
    i0 = float(re.search(r"vr#branch = (\S+)", o).group(1))
    psr = [(float(f), float(v)) for f, v in re.findall(r"^\d+\s+(\S+)\s+(\S+)", o, re.M)]
    k1 = min(psr, key=lambda q: abs(q[0] - 1e6))[1]
    return tag, vdda, i0, k1, k1*KI[cn]


if __name__ == "__main__":
    jobs = [(t, v) for t in CASES for v in VDDA]
    with Pool(2) as pool:
        r = pool.map(one, jobs)
    out = {t: [dict(vdda=v, i=i, didv=k, kvdd=kv) for tt, v, i, k, kv in r if tt == t] for t in CASES}
    for t, rows in out.items():
        print(t, [(q["vdda"], round(q["i"]*1e3, 3), round(q["kvdd"]/1e6, 1)) for q in rows])
    json.dump(out, open(os.path.join(c.HERE, "data", "cco_hv_vdda.json"), "w"), indent=1)
