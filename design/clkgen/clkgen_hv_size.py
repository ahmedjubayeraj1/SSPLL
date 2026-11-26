#!/usr/bin/env python3
"""clkgen_hv_size.py - sizing study of the 5 V side of the clock generator.
 1. P/N ratio of a 5 V inverter for equal rise and fall delay (fan-out 1 chain)            -> 2.5
 2. always-on transmission gate in the driver's in-phase path (o) for zero skew between cks and cksb
 3. pulser C for tau = 200 ps and W_H about 2.2 ns
 4. power split: the same run with zero output load, and with the level shifters only
-> data/clkgen_hv_size.json"""
import os, json, sys
import numpy as np
from multiprocessing import Pool
import clkgen_hv as K
HERE = os.path.dirname(os.path.abspath(__file__))
N5, P5 = K.N5, K.P5


def ratio(k):
    N = (N5, 2.0, 1, 0.5); P = (P5, 2.0*k, 1, 0.5)
    c = "".join(K.inv5(f"x{i}", f"n{i}", f"n{i+1}", (N, P)) for i in range(4))
    net = (f"* r\n.lib {K.LIB} tt\n.temp 27\nvdda VDDA 0 3.3\nvss VSS 0 0\nvssa VSSA 0 0\nvssd VSSD 0 0\nvin n0 0 pulse(0 3.3 1n 50p 50p 4n 10n)\n{c}"
           ".control\ntran 1p 12n\nwrdata w.txt v(n1) v(n2) v(n3)\n.endc\n.end\n")
    _, d = K.run(net, ["w.txt"]); z = d["w.txt"]; t = z[:, 0]
    a = K.xings(t, z[:, 3], 1.65, True)[0] - K.xings(t, z[:, 1], 1.65, False)[0]
    b = K.xings(t, z[:, 5], 1.65, False)[0] - K.xings(t, z[:, 3], 1.65, True)[0]
    return dict(k=k, rise=a, fall=b)


def variant(kw):
    try:
        return _variant(kw)
    except StopIteration:                       # an output never switched: report it (inside Pool.map a
        return dict(tag=kw["tag"], failed=True) # StopIteration would silently cut the result list)


def _variant(kw):
    p = dict(K.D); p.update({k: v for k, v in kw.items() if k != "tag" and k != "loads"})
    loads = kw.get("loads", K.LOADS)
    r = K.tran(p=p, loads=loads)
    return dict(tag=kw["tag"], **{k: float(v) for k, v in r.items()})


if __name__ == "__main__":
    out = {}
    with Pool(2) as pool:
        old = os.path.join(HERE, "data", "clkgen_hv_size.json")
        out["ratio"] = json.load(open(old))["ratio"] if os.path.exists(old) else pool.map(ratio, [1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
        V = [dict(tag="base")]
        for cg in (3.0, 4.0):                                            # Gm pulser C side (um): tau
            V.append(dict(tag=f"CG{cg}", CG=("cap_mim_m3_1", cg, 1, cg)))
        for w in (0.6, 1.0):                                            # TG of the pulse step drivers: skew of ckg/ckgb
            V.append(dict(tag=f"TGT{w}", TG5T=((N5, w, 1, 0.5), (P5, w, 1, 0.5))))
        V.append(dict(tag="noload", loads={k: 1e-18 for k in K.LOADS}))
        out["variants"] = pool.map(variant, V)
    json.dump(out, open(os.path.join(HERE, "data", "clkgen_hv_size.json"), "w"), indent=1)
    for r in out["ratio"]:
        print(f"P/N {r['k']}: rise {r['rise']*1e12:.1f} ps, fall {r['fall']*1e12:.1f} ps")
    for r in out["variants"]:
        print(r["tag"], "FAILED: an output did not switch") if r.get("failed") else print(f"{r['tag']:8s} t_s {r['t_s']*1e12:6.1f} skew {r['skew_s']*1e12:6.1f} skew_g {r['skew_g']*1e12:6.1f} tau {r['tau']*1e12:6.1f} gap1 {r['gap1']*1e12:5.1f} "
              f"gap2 {r['gap2']*1e12:5.1f} W_H {r['W_H']*1e9:.2f} ns t_p {r['t_p']*1e12:5.0f} P VDDA {r['p_vdda']*1e6:.0f} uW VDDD {r['p_vddd']*1e6:.0f} uW")
    json.dump(out, open(os.path.join(HERE, "data", "clkgen_hv_size.json"), "w"), indent=1)
