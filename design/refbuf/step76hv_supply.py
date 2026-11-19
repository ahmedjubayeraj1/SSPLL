#!/usr/bin/env python3
"""step76hv_supply.py - supply-to-edge sensitivity of the REF receiver, VDDA and VDDD (method M21, new in the redo).

Why: without an LDO the receiver's analog stages sit on the raw VDDA, and its level shifter and output gate on the
harness VDDD. Any supply noise that moves the refclk edge is reference phase noise, multiplied by N^2 = 16^2 in band.
Two measurements:
  DC  : delay change for a +10 mV step, each case at its own settled bias (slow noise, below the R_B self-bias loop);
  AC  : 10 mV sine on the rail at f_m = 0.3, 1, 5, 20 MHz; the refclk edge times are fitted to a sinusoid at f_m
        (least squares with offset and slope) -> |dt/dV| at f_m. f_m < f_ref/2, so every edge samples the ripple.
Inputs: 3.3 V pp square (CMOS crystal oscillator, the typical case) and 1 V pp sine.
-> data/step76hv_supply.json"""
import os, json
from multiprocessing import Pool
import refbuf_hv as H
HERE = os.path.dirname(os.path.abspath(__file__))


def job(a):
    kind, rail, fm, vpp, wave = a
    if kind == "dc":
        return dict(kind="dc", fm=0.0, **H.supply_dc(rail, vpp=vpp, wave=wave))
    nper = 2 if fm < 0.5e6 else 3
    return dict(kind="ac", **H.supply_mod(rail, fm=fm, vpp=vpp, wave=wave, nper=nper))


if __name__ == "__main__":
    import sys
    old = []
    if "--diff" in sys.argv:
        # third pass: every AC point again with the differential method (modulated minus unmodulated run)
        old = [r for r in json.load(open(os.path.join(HERE, "data", "step76hv_supply.json"))) if r["kind"] == "dc"]
    elif "--redo" in sys.argv:
        # second pass (19 Nov): the AC runs of VDDD (edge read at VDDD/2) and the 0.3 MHz runs (3 periods, quadratic
        # detrend) are repeated; the DC points and the VDDA runs above 0.3 MHz are kept
        old = [r for r in json.load(open(os.path.join(HERE, "data", "step76hv_supply.json")))
               if r["kind"] == "dc" or (r["rail"] == "vdda" and r["fm"] > 0.5e6)]
    jobs = []
    for rail in ("vdda", "vddd"):
        jobs += [("dc", rail, 0, 3.3, "square"), ("dc", rail, 0, 1.0, "sine")]
        jobs += [("ac", rail, fm, 3.3, "square") for fm in (0.3e6, 1e6, 5e6, 20e6)]
        jobs += [("ac", rail, fm, 1.0, "sine") for fm in (1e6, 5e6)]
    keep = {(r["kind"], r["rail"], r["fm"], r["vpp"]) for r in old}
    jobs = [j for j in jobs if (j[0], j[1], j[2], j[3]) not in keep]
    jobs.sort(key=lambda j: -(1/j[2] if j[2] else 0))          # longest runs first
    with Pool(2) as pool:
        res = old + pool.map(job, jobs)
    for r in sorted(res, key=lambda r: (r["rail"], r["vpp"], r["fm"])):
        print(f"{r['rail']} {r['vpp']} V pp {r['wave']:6s} f_m {r['fm']/1e6:5.2f} MHz: {abs(r['k'])*1e12:7.1f} ps/V", flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "step76hv_supply.json"), "w"), indent=1)
