#!/usr/bin/env python3
"""step78hv_size.py - sizing of the 5 V SSPD for A = 0.8 V/rad at 800 MHz (step 72 HV target): series resistor
length and sampling-switch width, each point a full beat run with the step-77 HV clock generator (method M18).
-> data/step78hv_size.json"""
import os, json
from multiprocessing import Pool
import sspd_hv as S
HERE = os.path.dirname(os.path.abspath(__file__))
N5, P5 = S.N5, S.P5
V = [dict(tag="RS0.8", RS=("res_xhigh_po_0p35", 0.35, 1, 0.8)), dict(tag="RS0.6", RS=("res_xhigh_po_0p35", 0.35, 1, 0.6)),
     dict(tag="RS0.5", RS=("res_xhigh_po_0p35", 0.35, 1, 0.5)),
     dict(tag="RS0.6_SW4", RS=("res_xhigh_po_0p35", 0.35, 1, 0.6), SWN=(N5, 4.0, 1, 0.5), SWP=(P5, 8.0, 1, 0.5))]


def one(kw):
    p = dict(S.D); p.update({k: v for k, v in kw.items() if k != "tag"})
    r = S.characteristic(p=p)
    return dict(tag=kw["tag"], **{k: v for k, v in r.items() if isinstance(v, float)})


if __name__ == "__main__":
    with Pool(2) as pool:
        res = pool.map(one, V)
    for r in res:
        print(f"{r['tag']:10s} A {r['A']:.3f} V/rad alpha {r['alpha']:.3f} CM {r['cm']:.3f} V P {r['power']*1e3:.3f} mW", flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "step78hv_size.json"), "w"), indent=1)
