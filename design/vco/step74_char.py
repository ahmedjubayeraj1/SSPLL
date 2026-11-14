#!/usr/bin/env python3
"""step74_char.py VARIANT - frequency characterisation of the chosen VCO cell (method M1):
  1. f and ring-node voltage vs feed current at tt/27, ss/110, ff/-40, sf/27, fs/27 (vtune 0.9 V, 10 fF per node)
  2. f vs vtune at the 1.6 GHz current (tt, ss/110, ff/-40) -> K_VCO in the 0.6-1.2 V window
  3. power-up start-up from all-zero nodes (tt, ss/110, ff/-40)
-> data/step74_char_VARIANT.json"""
import sys, json, os
import numpy as np
import vco
from step74_point import VARIANTS
name = sys.argv[1]; p = VARIANTS[name]
out = {"variant": name}
corners = [("tt", 27, 10e-15), ("ss", 110, 15e-15), ("ff", -40, 5e-15), ("sf", 27, 10e-15), ("fs", 27, 10e-15)]
Is = [0.6e-3, 0.9e-3, 1.2e-3, 1.5e-3, 1.8e-3, 2.1e-3]
out["f_vs_I"] = {}
for c, t, cp in corners:
    r = vco.freq_sweep(p, Is, corner=c, temp=t, cpar=cp)
    out["f_vs_I"][f"{c}_{t}"] = [(I, x.get("f"), x.get("vdd_avg"), x.get("vdd_max"), x.get("ppd")) for I, x in zip(Is, r)]
    print(c, t, [(round(I*1e3, 2), round((x.get("f") or 0)/1e9, 3), round(x.get("vdd_avg") or 0, 3)) for I, x in zip(Is, r)], flush=True)
I0 = json.load(open(os.path.join(vco.HERE, "data", f"step74_{name}.json")))["I"]
vts = [0.3, 0.6, 0.75, 0.9, 1.05, 1.2, 1.5]
out["f_vs_vtune"] = {}
for c, t, cp in corners[:3]:
    from multiprocessing import Pool
    with Pool(2) as pool:
        r = pool.map(vco._one, [(p, dict(I=I0, corner=c, temp=t, cpar=cp, vtune=v)) for v in vts])
    out["f_vs_vtune"][f"{c}_{t}"] = [(v, x.get("f"), x.get("vdd_avg")) for v, x in zip(vts, r)]
    print("vtune", c, t, [(v, round((x.get("f") or 0)/1e9, 4)) for v, x in zip(vts, r)], flush=True)
out["startup"] = {}
for c, t, cp in corners[:3]:
    r = vco.run(vco.netlist(p, I=I0, corner=c, temp=t, cpar=cp, mode="pwrup"))
    out["startup"][f"{c}_{t}"] = (r.get("f"), r.get("ta"), r.get("ppd"))
    print("startup", c, t, r.get("f"), r.get("ta"), r.get("ppd"), flush=True)
json.dump(out, open(os.path.join(vco.HERE, "data", f"step74_char_{name}.json"), "w"), indent=1)
