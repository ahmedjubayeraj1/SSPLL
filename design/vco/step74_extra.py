#!/usr/bin/env python3
"""step74_extra.py - start-up with a realistic 1 % mismatch (0.1 fF extra on vop) from all-zero nodes, and the top of
the range at ss / 110 C with 10 and 15 fF per node. -> data/step74_extra.json"""
import json, os
from multiprocessing import Pool
import vco
p = vco.FINAL; I0 = 1.437e-3
jobs = []
for c, t, cp in (("tt", 27, 10e-15), ("ss", 110, 15e-15), ("ff", -40, 5e-15)):
    jobs.append((f"startup_{c}", p, dict(I=I0, corner=c, temp=t, cpar=cp, mode="pwrup", tstop=30e-9, r0=10, r1=30,
                                         extra="cmis vop vss 0.1f\n")))
for cp in (10e-15, 15e-15):
    for I in (2.1e-3, 2.4e-3):
        jobs.append((f"ss110_{cp*1e15:.0f}fF_{I*1e3:.1f}mA", p, dict(I=I, corner="ss", temp=110, cpar=cp, tstop=30e-9, r0=8, r1=24)))
def one(j):
    return j[0], vco.run(vco.netlist(j[1], **j[2]))
with Pool(2) as pool:
    res = dict(pool.map(one, jobs))
for k, v in res.items():
    print(k, {a: round(b, 4) if a not in ("f", "ta", "tb") else b for a, b in v.items()}, flush=True)
json.dump(res, open(os.path.join(vco.HERE, "data", "step74_extra.json"), "w"), indent=1)
