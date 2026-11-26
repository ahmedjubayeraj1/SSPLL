#!/usr/bin/env python3
"""step79hv_noisesize.py - noise-driven resizing of the mirror-less Gm. The first version (tails and pMOS sources of
4 uA per side, replica of one half-slice) had 2.98 pA/rtHz at 1 MHz and 8.7 at 10 kHz into the filter: 0.43 ps of
system jitter and L(300 kHz) FFNC on -123.0 dBc/Hz (> -124 typ). The noise breakdown (ngspice noise summary) put 74 %
in the replica bias (its noise is copied onto pb and into every pMOS source) and most of the rest in the slices' current
sources. Levers: a larger replica (RM), less bias current (MTM), current sources with less gm (longer L).
For every variant R_S is re-tuned for G = 18.42 uS (secant on the resistor length), then .noise and the corner G.
-> data/step79hv_noisesize.json"""
import os, json
import numpy as np
from multiprocessing import Pool
import sscp_hv as C
HERE = os.path.dirname(os.path.abspath(__file__))
N5, P5 = C.N5, C.P5
V = {"MTM2 RM1 (first)": dict(MTM=2, RM=1), "MTM2 RM6": dict(MTM=2, RM=6), "MTM1 RM6": dict(MTM=1, RM=6),
     "MTM1 RM6 MP4/4": dict(MTM=1, RM=6, MP=(P5, 4.0, 1, 4.0)),
     "MTM1 RM6 MP4/4 MT1/8": dict(MTM=1, RM=6, MP=(P5, 4.0, 1, 4.0), MT=(N5, 1.0, 1, 8.0)),
     "MTM2 RM6 MP4/4 MT1/8": dict(MTM=2, RM=6, MP=(P5, 4.0, 1, 4.0), MT=(N5, 1.0, 1, 8.0))}


def G_of(p, L, **kw):
    q = dict(p); q["RS"] = ("res_xhigh_po_0p35", 0.35, float(L))
    return abs(C.dc_transfer(q, **kw)["G"]), q


def noise(p):
    net = C.head(p).replace("vvc vctl 0 1.8", "vvc v2 0 1.8\nvmeas vctl v2 0\nh1 o 0 vmeas 1") + (
        "vp v1p 0 dc 1.66 ac 1\nvm v1m 0 1.66\n.control\noption sparse\nnoise v(o) vp dec 10 1e3 1e8\nsetplot noise1\n"
        "wrdata n.txt onoise_spectrum\n.endc\n.end\n")
    _, d = C.run(net, ["n.txt"]); z = d["n.txt"]
    return z[:, 0], z[:, 1]


def one(tag):
    p = dict(C.D); p.update(V[tag])
    L0, L1 = 12.0, 20.0
    g0, _ = G_of(p, L0); g1, _ = G_of(p, L1)
    for _ in range(4):                                   # secant on log G vs log L
        L2 = float(np.exp(np.log(L0) + (np.log(18.42e-6) - np.log(g0))*(np.log(L1) - np.log(L0))/(np.log(g1) - np.log(g0))))
        L2 = min(max(L2, 1.0), 80.0)
        g2, q = G_of(p, L2)
        L0, g0, L1, g1 = L1, g1, L2, g2
        if abs(g2/18.42e-6 - 1) < 0.005:
            break
    f, n = noise(q)
    corners = {c: abs(C.dc_transfer(q, corner=c, temp=t, vdda=va, cm=va*0.503)["G"]) for c, t, va in
               (("ss", 110, 2.97), ("ff", -40, 3.63))}
    r = C.dc_transfer(q)
    return dict(tag=tag, RS_L=L1, G=g1, G_ss=corners["ss"], G_ff=corners["ff"], lin=r["lin"], v_os=r["v_os"],
                n10k=float(np.interp(1e4, f, n)), n100k=float(np.interp(1e5, f, n)), n1M=float(np.interp(1e6, f, n)),
                f=f.tolist(), n=n.tolist())


if __name__ == "__main__":
    with Pool(2) as pool:
        res = pool.map(one, list(V))
    for r in res:
        print(f"{r['tag']:24s} R_S L {r['RS_L']:5.1f} um: G {r['G']*1e6:.2f} uS (ss {r['G_ss']/r['G']:.3f}, ff {r['G_ff']/r['G']:.3f}), "
              f"lin +-{min(-r['lin'][0], r['lin'][1]):.2f} V, v_os {r['v_os']*1e3:.1f} mV; noise {r['n10k']*1e12:.2f} / "
              f"{r['n100k']*1e12:.2f} / {r['n1M']*1e12:.2f} pA/rtHz at 10k / 100k / 1M", flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "step79hv_noisesize.json"), "w"))
