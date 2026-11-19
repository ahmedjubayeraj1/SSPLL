#!/usr/bin/env python3
"""step77hv_supply.py - supply-to-edge sensitivity of the whole reference path REF_IN -> receiver (step 76 HV) ->
clock generator (this step) -> cks falling (the SSPD sampling instant), method M21 (differential sinusoidal
modulation). Both blocks share VDDA and VDDD, so their sensitivities add with their signs: only the combined run
gives the number that sets the VDDD requirement. Reference input: 3.3 V pp square (CMOS crystal oscillator); --sine1: 1 V pp sine -> data/step77hv_supply_1v.json.
The edge is read where cks crosses VDDA/2 at that instant (the SSPD switches are on VDDA).
The first run (sampling edge through refclk and a level shifter, VDDD 376 ps/V) is kept as
data/step77hv_supply_via_vddd.json; this run is the final architecture (sampling edge from refhv).
-> data/step77hv_supply.json"""
import os, re, json, sys
import numpy as np
from multiprocessing import Pool
import clkgen_hv as K
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "refbuf"))
import refbuf_hv as H
F = 50e6; T = 1/F
SINE = "--sine1" in sys.argv          # 1 V pp sine reference (the smallest usual XO amplitude) instead of the 3.3 V square
VPP, WAVE = (1.0, "sine") if SINE else (3.3, "square")


def netlist(vdda, vddd, b):
    rx = H.full().replace(K.CC.LS, "")          # the level-shifter subcircuit is defined once, in the clock generator
    return (f"* REF path\n.lib {K.LIB} tt\n.temp 27\n{rx}{K.cells()}vdda VDDA 0 {vdda}\nvddd VDDD 0 {vddd}\n"
            f"iib ib 0 2.5e-6\nven pll_en 0 1.8\n"
            "xrx pad0 refclk refhv ib pll_en VDDA VDDD 0 sspll_refbuf_hv\n"
            "xcg refclk refhv cks cksb ckg ckgb ckh ckhb VDDD VDDA 0 sspll_clkgen_hv\n" +
            "".join(f"c{k} {k} 0 {v}\n" for k, v in K.LOADS.items()) + H.src(3.3, VPP, F, WAVE) +
            f".ic v(xrx.vin)={b['vin']} v(xrx.s1)={b['s1']}\n")


def edges(rail, amp, fm, tset, tstop, b):
    mod = lambda v0: f"sin({v0} {amp} {fm} {tset})" if amp else f"{v0}"
    net = netlist(mod(3.3) if rail == "vdda" else 3.3, mod(1.8) if rail == "vddd" else 1.8, b)
    net += f".control\nsave v(cks) v(VDDA)\ntran 2p {tstop} 0 5p\nwrdata w.txt v(cks) v(VDDA)\n.endc\n.end\n"
    _, d = K.run(net, ["w.txt"])
    z = d["w.txt"]
    te = K.xings(z[:, 0], z[:, 1] - z[:, 3]/2, 0.0, False)
    return te[te > tset]


def job(a):
    rail, fm = a
    b = H.op()
    if fm == 0:                                  # DC: +10 mV step, both runs from their own settled bias
        tset, tstop = 20*T, 40*T
        bb = H.op(vdda=3.31 if rail == "vdda" else 3.3, vddd=1.81 if rail == "vddd" else 1.8)
        def run(v):
            net = netlist(3.3 + (v if rail == "vdda" else 0), 1.8 + (v if rail == "vddd" else 0), bb if v else b)
            net += f".control\nsave v(cks) v(pad0)\ntran 2p {tstop} 0 5p\nwrdata w.txt v(cks) v(pad0)\n.endc\n.end\n"
            _, d = K.run(net, ["w.txt"]); z = d["w.txt"]
            vda = 3.3 + (v if rail == "vdda" else 0)
            tc = K.xings(z[:, 0], z[:, 1], vda/2, False); tp = K.xings(z[:, 0], z[:, 3], 1.65, True)
            tc, tp = tc[tc > tset], tp[tp > tset - T]
            return np.mean([tc[(tc > x) & (tc < x + T)][0] - x for x in tp if np.any((tc > x) & (tc < x + T))])
        return dict(rail=rail, fm=0.0, k=(run(10e-3) - run(0))/10e-3)
    tset = 20*T; tstop = tset + max(3/fm, 40*T)
    t1, t0 = edges(rail, 10e-3, fm, tset, tstop, b), edges(rail, 0, fm, tset, tstop, b)
    n = min(len(t1), len(t0)); dt = t1[:n] - t0[:n]
    A = np.c_[np.ones(n), np.sin(2*np.pi*fm*(t0[:n] - tset)), np.cos(2*np.pi*fm*(t0[:n] - tset))]
    c, *_ = np.linalg.lstsq(A, dt, rcond=None)
    return dict(rail=rail, fm=fm, k=float(np.hypot(c[1], c[2]))/10e-3, phase=float(np.degrees(np.arctan2(c[2], c[1]))),
                n=n, resid=float((dt - A @ c).std()))


if __name__ == "__main__":
    jobs = [(r, f) for f in (1e6, 0.0, 5e6, 20e6) for r in ("vddd", "vdda")]
    with Pool(2) as pool:
        res = pool.map(job, jobs)
    for r in res:
        print(f"{r['rail']} f_m {r['fm']/1e6:5.2f} MHz: {abs(r['k'])*1e12:6.1f} ps/V", flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "step77hv_supply_1v.json" if SINE else "step77hv_supply.json"), "w"), indent=1)
