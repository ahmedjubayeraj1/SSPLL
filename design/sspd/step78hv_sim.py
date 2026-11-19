#!/usr/bin/env python3
"""step78hv_sim.py - verification of the 5 V SSPD (step 78 redo). -> data/step78hv_sim.json
A  sampled characteristic (A, alpha, CM, power) over MOS x R/C corners, temperature, VDDA, VDDD, f_ref    (M18)
B  kick-back on the ring output and f_ref supply current, with and without the dummy sampler          (M19)
C  isolation-buffer jitter: trip-point noise currents of XB1 / XB2 (transient noise)                   (M17)
D  VDDA sensitivity of the isolation-buffer delay (a timing shift ahead of the sampler = reference-like) (M21, static)"""
import os, json, sys
import numpy as np
from multiprocessing import Pool
import sspd_hv as S
HERE = os.path.dirname(os.path.abspath(__file__))
COND = [("tt", 27, 3.3, 1.8, 50e6), ("tt", 27, 2.97, 1.8, 50e6), ("tt", 27, 3.63, 1.8, 50e6), ("tt", 27, 3.3, 1.71, 50e6),
        ("tt", -40, 3.3, 1.8, 50e6), ("tt", 110, 3.3, 1.8, 50e6), ("ss_hh", 110, 2.97, 1.71, 50e6),
        ("ss_hh", -40, 2.97, 1.71, 50e6), ("ff_ll", -40, 3.63, 1.89, 50e6), ("ff_ll", 110, 3.63, 1.89, 50e6),
        ("ss", 110, 2.97, 1.71, 50e6), ("ff", -40, 3.63, 1.89, 50e6), ("sf", 27, 3.3, 1.8, 50e6), ("fs", 27, 3.3, 1.8, 50e6),
        ("hl", 27, 3.3, 1.8, 50e6), ("lh", 27, 3.3, 1.8, 50e6), ("tt", 27, 3.3, 1.8, 45e6), ("tt", 27, 3.3, 1.8, 55e6)]


def char(a):
    c, t, va, vd, f = a
    try:
        r = S.characteristic(corner=c, temp=t, vdda=va, vddd=vd, fref=f, keep=(a == COND[0]))
    except Exception as e:                       # report, do not lose the other conditions
        return dict(corner=c, temp=t, vdda=va, vddd=vd, fref=f, failed=str(e)[:200])
    return r


if __name__ == "__main__":
    res = {}
    with Pool(2) as pool:
        res["char"] = pool.map(char, COND)
    for r in res["char"]:
        if "failed" in r:
            print("FAILED", r, flush=True); continue
        print(f"  {r['corner']:5s} {r['temp']:4d} C {r['vdda']}/{r['vddd']} V {r['fref']/1e6:.0f} MHz: A {r['A']:.3f} V/rad, "
              f"alpha {r['alpha']:.3f}, v2 gain {r['gain_v2']:.3f}, CM {r['cm']:.3f} V, P {r['power']*1e3:.3f} mW", flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "step78hv_sim.json"), "w"))
    phi0 = next(r["phi0"] for r in res["char"] if r["corner"] == "tt" and r["vdda"] == 3.3 and r["fref"] == 50e6 and r["temp"] == 27)
    res["kick"] = S.kick(phi0=0.0)
    print("B", {k: v for k, v in res["kick"].items() if k != "wave"}, flush=True)
    j = S.buf_jitter(); jb = S.buf_jitter(S=j["S"], scale=1e-6)
    s = float(np.sqrt(max(j["sigma"]**2 - jb["sigma"]**2, 0)))
    res["buf"] = dict(raw=j, baseline=jb, sigma=s, L_floor=float(10*np.log10((2*np.pi*50e6*s/np.sqrt(2))**2/50e6)))
    print(f"C buffer jitter {s*1e15:.1f} fs per side (baseline {jb['sigma']*1e15:.1f}); differential crossing /sqrt2 -> "
          f"{res['buf']['L_floor']:.1f} dBc/Hz at 50 MHz", flush=True)
    res["bufsup"] = S.buf_supply()
    print(f"D buffer VDDA sensitivity {res['bufsup']['k']*1e12:.1f} ps/V (delay {res['bufsup']['d0']*1e12:.0f} ps)", flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "step78hv_sim.json"), "w"))
