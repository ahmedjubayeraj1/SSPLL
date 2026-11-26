#!/usr/bin/env python3
"""sscp_hv_size.py - sizing of the mirror-less Gm (v2): tail units per side (MTM) and R_S length for
G = 18.43 uS with three slices (beta 0.79 uA/rad), checked at tt and at the two corners that bound G,
plus the speed that killed the mirror version: the output current's step response to a v1 step (ckg held on).
-> data/sscp_hv_size.json"""
import os, json
import numpy as np
from multiprocessing import Pool
import sscp_hv as C
HERE = os.path.dirname(os.path.abspath(__file__))
import sys
if "--replica" in sys.argv:          # round 2: with the replica bias (the first round showed a 33 mV systematic offset)
    V = [dict(MTM=2, RS=("res_xhigh_po_0p35", 0.35, L)) for L in (17.0, 18.0)]
else:
    V = [dict(MTM=2, RS=("res_xhigh_po_0p35", 0.35, L)) for L in (14.0, 18.0, 22.0)] + \
        [dict(MTM=3, RS=("res_xhigh_po_0p35", 0.35, L)) for L in (16.0, 20.0, 24.0)]
CORN = [("tt", 27, 3.3), ("ss", 110, 2.97), ("ff", -40, 3.63)]


def step(p, corner="tt", temp=27, vdda=3.3):
    """v1p - v1m steps 0 -> +0.1 V at 2 ns (50 ps edge); ckg on; output current into vctl vs time."""
    net = C.head(p, corner=corner, temp=temp, vdda=vdda) + (
        f"vp v1p 0 pwl(0 {vdda*0.503} 2n {vdda*0.503} 2.05n {vdda*0.503 + 0.05})\n"
        f"vm v1m 0 pwl(0 {vdda*0.503} 2n {vdda*0.503} 2.05n {vdda*0.503 - 0.05})\n"
        ".control\ntran 2p 8n\nwrdata w.txt i(vvc)\n.endc\n.end\n")
    _, d = C.run(net, ["w.txt"])
    z = d["w.txt"]; t, i = z[:, 0], z[:, 1]
    i0 = np.interp(1.9e-9, t, i); i1 = np.interp(7.9e-9, t, i)
    fr = lambda dt: float((np.interp(2.0e-9 + dt, t, i) - i0)/(i1 - i0))
    return dict(f025=fr(0.25e-9), f05=fr(0.5e-9), f1=fr(1.0e-9), f2=fr(2.0e-9))


def one(kw):
    p = dict(C.D); p.update(kw)
    out = dict(MTM=kw["MTM"], RS_L=kw["RS"][2], corners={})
    for c, t, va in CORN:
        r = C.dc_transfer(p, corner=c, temp=t, vdda=va, cm=va*0.503)
        out["corners"][c] = dict(G=abs(r["G"]), v_os=r["v_os"], lin=r["lin"])
    out["step"] = step(p)
    return out


if __name__ == "__main__":
    with Pool(2) as pool:
        res = pool.map(one, V)
    for r in res:
        g = {k: v["G"]*1e6 for k, v in r["corners"].items()}
        print(f"MTM {r['MTM']} R_S L {r['RS_L']:4.1f} um: G tt {g['tt']:.2f} uS (ss {g['ss']:.2f}, ff {g['ff']:.2f}; "
              f"{min(g.values())/g['tt']:.3f}-{max(g.values())/g['tt']:.3f}), lin +-{-r['corners']['tt']['lin'][0]:.2f} V, "
              f"v_os {r['corners']['tt']['v_os']*1e3:.1f} mV; step settled {r['step']['f025']:.2f} / {r['step']['f05']:.2f} / "
              f"{r['step']['f1']:.2f} / {r['step']['f2']:.2f} at 0.25 / 0.5 / 1 / 2 ns", flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "sscp_hv_size_replica.json" if "--replica" in sys.argv else "sscp_hv_size.json"), "w"), indent=1)
