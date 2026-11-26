#!/usr/bin/env python3
"""refbuf_hv_sim.py - verification of the drawn 5 V REF receiver with its VDDD level shifter (step 76 redo).
A  bias point over 5 corners x VDDA 2.97 / 3.3 / 3.63 V                                         (M10)
B  large-signal transient: amplitude 0.4-3.3 V pp sine and a 3.3 V square at tt; corners at the VDDA and VDDD limits
   (the level shifter now runs from VDDD 1.71-1.89 V, so ss at -40 C, where the thick-oxide V_T is highest, is added);
   45 / 55 MHz                                                                                     (M16)
D  start-up after pll_en, and the disabled state                                                   (M16)
-> data/refbuf_hv_sim.json  (the supply sensitivity is refbuf_hv_supply.py, the noise refbuf_hv_noise.py)"""
import os, json
from multiprocessing import Pool
import refbuf_hv as H
HERE = os.path.dirname(os.path.abspath(__file__))
CORNERS = [("tt", 27), ("ss", 110), ("ff", -40), ("sf", 27), ("fs", 27), ("ss", -40)]


def op(a):
    c, t, v = a
    return dict(corner=c, temp=t, vdda=v, **H.op(c, t, v))


def tran(a):
    c, t, vdda, vddd, vpp, f, wave = a
    return H.tran(c, t, vdda, vddd, vpp, f, wave)


if __name__ == "__main__":
    res = {}
    with Pool(2) as pool:
        res["op"] = pool.map(op, [(c, t, v) for c, t in CORNERS for v in (2.97, 3.3, 3.63)])
        print("A done", flush=True)
        for r in res["op"]:
            print(f"  {r['corner']} {r['temp']:4d} C VDDA {r['vdda']}: vin {r['vin']:.3f} V, I(VDDA) {r['ia']*1e6:.1f} uA", flush=True)
        jobs = [("tt", 27, 3.3, 1.8, v, 50e6, "sine") for v in (0.4, 0.7, 1.0, 2.0, 3.3)]
        jobs += [("tt", 27, 3.3, 1.8, 3.3, 50e6, "square")]
        jobs += [(c, t, va, vd, vpp, 50e6, w) for c, t in CORNERS[1:] for va, vd in ((2.97, 1.71), (3.63, 1.89))
                 for vpp, w in ((0.4, "sine"), (3.3, "square"))]
        jobs += [("tt", 27, 3.3, 1.8, 1.0, f, "sine") for f in (45e6, 55e6)]
        jobs += [("tt", 27, 3.3, vd, 3.3, 50e6, "square") for vd in (1.71, 1.89)]
        res["tran"] = pool.map(tran, jobs)
    print("B done", flush=True)
    for r in res["tran"]:
        print(f"  {r['corner']} {r['temp']:4d} {r['vdda']}/{r['vddd']} V {r['vpp']} V pp {r['wave']:6s} {r['f']/1e6:.0f} MHz: "
              f"delay {r['delay']*1e9:.3f} ns, duty {r['duty']*100:.1f} %, rise {r['trise']*1e12:.0f} ps, "
              f"P {r['power']*1e3:.3f} mW (VDDD {r['id']*1e6:.1f} uA), swing {r['vmin']:.2f}..{r['vmax']:.2f} V", flush=True)
    res["startup"] = {f"{c}_{t}": H.startup(c, t) for c, t in (("tt", 27), ("ss", 110), ("ff", -40))}
    for k, v in res["startup"].items():
        print("D", k, {q: x for q, x in v.items() if not isinstance(x, list)}, flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "refbuf_hv_sim.json"), "w"))
