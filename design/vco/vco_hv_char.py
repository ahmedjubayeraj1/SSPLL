#!/usr/bin/env python3
"""vco_hv_char.py [VARIANT] - characterisation of the chosen 5 V ring (method M1), 800 MHz design:
  1. f and ring-node voltage vs feed current at tt/27, ss/110, ff/-40 (vtune 1.65 V; wiring 10 / 15 / 5 fF per node)
  2. f vs vtune at the 800 MHz current (tt, ss/110, ff/-40) -> K_VCO over the 1.0-2.3 V window of step 73
  3. range: current and ring node for 880 MHz at ss/110 (15 fF) and for 720 MHz at ff/-40 (5 fF); sf/fs at the nominal I
  4. power-up start-up from all-zero nodes (tt, ss/110, ff/-40), and at tt with +-2 % width mismatch in stage 1
  5. output buffer: supply current and output swing at tt / ss 110 / ff -40 (PDK MIM and poly resistor)
-> data/vco_hv_char_VARIANT.json"""
import sys, json, os
from multiprocessing import Pool
import vco_hv as v
from vco_hv_point import VARIANTS
name = sys.argv[1] if len(sys.argv) > 1 else "hl6"; p = VARIANTS[name]
I0 = json.load(open(os.path.join(v.HERE, "data", f"vco_hv_{name}.json")))["I"]
out = {"variant": name, "I0": I0}
C3 = [("tt", 27, 10e-15, 3.3), ("ss", 110, 15e-15, 2.97), ("ff", -40, 5e-15, 3.63)]
Is = [0.6e-3, 0.8e-3, 1.0e-3, 1.25e-3, 1.5e-3, 1.8e-3]
out["f_vs_I"] = {}
for c, t, cp, vd in C3:
    r = v.freq_sweep(p, Is, corner=c, temp=t, cpar=cp, vdda=vd)
    out["f_vs_I"][f"{c}_{t}"] = [(I, x.get("f"), x.get("vdd_avg"), x.get("vdd_max"), x.get("ppd")) for I, x in zip(Is, r)]
    print(c, t, [(round(I*1e3, 2), round((x.get("f") or 0)/1e6, 1), round(x.get("vdd_avg") or 0, 3)) for I, x in zip(Is, r)], flush=True)
vts = [0.6, 1.0, 1.3, 1.65, 1.98, 2.3, 2.6]
out["f_vs_vtune"] = {}
for c, t, cp, vd in C3:
    with Pool(2) as pool:
        r = pool.map(v._one, [(p, dict(I=I0, corner=c, temp=t, cpar=cp, vtune=x, vdda=vd)) for x in vts])
    out["f_vs_vtune"][f"{c}_{t}"] = [(x, y.get("f"), y.get("vdd_avg")) for x, y in zip(vts, r)]
    print("vtune", c, t, [(x, round((y.get("f") or 0)/1e6, 1)) for x, y in zip(vts, r)], flush=True)
out["range"] = {}
for (c, t, cp, vd), ft, Ig in ((C3[1], 0.88e9, 1.4e-3), (C3[2], 0.72e9, 0.6e-3), (C3[0], 0.72e9, 0.8e-3), (C3[0], 0.88e9, 1.15e-3)):
    I, r = v.find_current(p, ft, I0=Ig, corner=c, temp=t, cpar=cp, vdda=vd)
    out["range"][f"{c}_{t}_{ft/1e6:.0f}"] = (I, r.get("f"), r.get("vdd_avg"), r.get("vdd_max"))
    print("range", c, t, ft/1e6, round(I*1e3, 3), round(r.get("vdd_avg", 0), 3), round(r.get("vdd_max", 0), 3), flush=True)
out["skew"] = {}
for c in ("sf", "fs"):
    x = v.run_full(v.netlist(p, I=I0, corner=c, temp=27))
    out["skew"][c] = (x.get("f"), x.get("vdd_avg"))
    print("skew", c, x.get("f"), x.get("vdd_avg"), flush=True)
out["startup"] = {}   # superseded: the read-out here sees power-up chatter; use vco_hv_startup.py
for c, t, cp, vd in []:
    r = v.run_full(v.netlist(p, I=I0, corner=c, temp=t, cpar=cp, vdda=vd, mode="pwrup", tstop=40e-9, r0=10, r1=30))
    out["startup"][f"{c}_{t}"] = (r.get("f"), r.get("ta"), r.get("ppd"))
    print("startup", c, t, r.get("f"), r.get("ta"), r.get("ppd"), flush=True)
for tag, mm in ():
    r = v.run_full(v.netlist(p, I=I0, mode="pwrup", tstop=40e-9, r0=10, r1=30, mism=mm))
    out["startup"][tag] = (r.get("f"), r.get("ta"), r.get("ppd"))
    print("startup", tag, r.get("f"), r.get("ta"), r.get("ppd"), flush=True)
out["buffer"] = {}
for c, t, vd in (("tt", 27, 3.3), ("ss", 110, 2.97), ("ff", -40, 3.63)):
    out["buffer"][f"{c}_{t}"] = v.buffer_current(c, t, vd, f=0.88e9 if c == "ss" else 0.8e9, swing=1.6)
    print("buffer", c, t, out["buffer"][f"{c}_{t}"], flush=True)
json.dump(out, open(os.path.join(v.HERE, "data", f"vco_hv_char_{name}.json"), "w"), indent=1)
