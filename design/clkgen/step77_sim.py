#!/usr/bin/env python3
"""step77_sim.py - verification of the clock generator (step 77). Writes data/step77_sim.json.
A  timing over MOS x R/C corners, temperature, VDDL, reference frequency, refclk duty and edge rate   (method M16)
B  jitter of the sampling edge: transient noise with a white noise current at every node of the sampling path,
   at the level each inverter makes at its trip point (from .noise)                                   (method M17)"""
import os, json, re
import numpy as np
from multiprocessing import Pool
import clkgen as C

HERE = os.path.dirname(os.path.abspath(__file__))
COND = [("tt", 27, 1.8, 50e6, 0.5, 300e-12), ("tt", 27, 1.71, 50e6, 0.5, 300e-12), ("tt", 27, 1.89, 50e6, 0.5, 300e-12),
        ("tt", -40, 1.8, 50e6, 0.5, 300e-12), ("tt", 110, 1.8, 50e6, 0.5, 300e-12),
        ("ss_hh", 110, 1.71, 50e6, 0.5, 300e-12), ("ss_hh", -40, 1.71, 50e6, 0.5, 300e-12),
        ("ff_ll", -40, 1.89, 50e6, 0.5, 300e-12), ("ff_ll", 110, 1.89, 50e6, 0.5, 300e-12),
        ("ss", 110, 1.71, 50e6, 0.5, 300e-12), ("ff", -40, 1.89, 50e6, 0.5, 300e-12),
        ("sf", 27, 1.8, 50e6, 0.5, 300e-12), ("fs", 27, 1.8, 50e6, 0.5, 300e-12),
        ("hl", 27, 1.8, 50e6, 0.5, 300e-12), ("lh", 27, 1.8, 50e6, 0.5, 300e-12),
        ("tt", 27, 1.8, 45e6, 0.5, 300e-12), ("tt", 27, 1.8, 55e6, 0.5, 300e-12),
        ("tt", 27, 1.8, 50e6, 0.35, 300e-12), ("tt", 27, 1.8, 50e6, 0.65, 300e-12),
        ("tt", 27, 1.8, 50e6, 0.5, 230e-12), ("tt", 27, 1.8, 50e6, 0.5, 410e-12)]


def timing(a):
    corner, temp, vdd, f, duty, tr = a
    r = C.tran(corner, temp, vdd, f, duty, tr)
    return dict(corner=corner, temp=temp, vdd=vdd, f=f, duty=duty, tr=tr, **{k: float(v) for k, v in r.items()})


def jitter(seed=1, nedge=150, fin=500e6, nt=1e-12, S=None, scale=1.0):
    """Sampling path only (input buffer + driver of cks/cksb) with a trnoise current at every internal node."""
    S = S or {k: C.inv_noise(C.D[k])[0] for k in ("INVS", "INVM", "INVL")}
    # node -> size of the inverter that drives it
    nodes = dict(r1="INVM", r2="INVM", a1="INVS", cksb="INVL", c1="INVS", c2="INVM", cks="INVL")
    T = 1/fin; vdd = 1.8
    # ngspice cannot attach sources to hierarchical nodes: build a flat copy of the sampling path instead
    p = C.D
    flat = (C.inv("xi0", "refclk", "r1", p["INVM"]) + C.inv("xi1", "r1", "r2", p["INVM"]) +
            C.inv("xa", "r2", "a1", p["INVS"]) + C.inv("xb", "a1", "cksb", p["INVL"]) +
            C.inv("xc", "r2", "c1", p["INVS"]) + C.inv("xd", "c1", "c2", p["INVM"]) + C.inv("xe", "c2", "cks", p["INVL"]))
    flat = flat.replace(" VSS ", " 0 ")
    src = "".join(f"in{n} 0 {n} dc 0 trnoise({scale*np.sqrt(S[sz]/(2*nt)):.4e} {nt} 0 0)\n" for n, sz in nodes.items())
    net = (f"* sampling-path jitter\n.lib {C.LIB} tt\n.temp 27\nvdd VDD 0 {vdd}\n{flat}"
           f"vin refclk 0 pulse(0 {vdd} 0.2n 375p 375p {T/2 - 375e-12} {T})\n"
           "ccks cks 0 30f\nccksb cksb 0 30f\n" + src +
           f".options seed={seed}\n.control\ntran {nt} {(nedge + 2)*T} {2*T} {nt}\nwrdata w.txt v(refclk) v(cks)\n.endc\n.end\n")
    _, d = C.run(net, ["w.txt"])
    z = d["w.txt"]; t = z[:, 0]
    tr = C.xings(t, z[:, 1], vdd/2, True); tf = C.xings(t, z[:, 3], vdd/2, False)
    dly = np.array([tf[(tf > x) & (tf < x + 0.6e-9)][0] - x for x in tr[:-1]])   # the cks edge belonging to this refclk edge
    k = np.arange(len(dly)); dev = dly - np.polyval(np.polyfit(k, dly, 4), k)      # remove slow numerical drift
    return dict(sigma=float(dev.std()), sigma_raw=float(dly.std()), mean=float(dly.mean()), n=len(dly),
                S={k: float(v) for k, v in S.items()})


if __name__ == "__main__":
    if not os.environ.get("ONLY_JITTER"):
        with Pool(2) as pool:
            res = dict(timing=pool.map(timing, COND))
        print("A done", flush=True)
    old = json.load(open(os.path.join(HERE, "data", "step77_sim.json"))) if os.path.exists(os.path.join(HERE, "data", "step77_sim.json")) else {}
    if "timing" in old and os.environ.get("ONLY_JITTER"):
        res = dict(timing=old["timing"])
    S = old.get("jitter", {}).get("S")
    res["jitter"] = jitter(S=S)
    res["jitter"]["baseline"] = jitter(S=res["jitter"]["S"], scale=1e-6)["sigma"]
    s = res["jitter"]["sigma"]
    res["jitter"]["L_floor"] = float(10*np.log10((2*np.pi*50e6*s)**2/50e6))
    print("B", {k: v for k, v in res["jitter"].items() if k != "S"}, flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "step77_sim.json"), "w"))
