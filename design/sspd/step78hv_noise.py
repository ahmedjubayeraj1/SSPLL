#!/usr/bin/env python3
"""step78hv_noise.py - the 5 V SSPD in the 800 MHz system (method M9, design/budget/hv_system.py).

 * REF chain = step 77 HV chain (receiver + clock generator + VDDA / VDDD terms) with the SSPD isolation-buffer part
   replaced by this step's measurement: white jitter (M17, the two sides' buffers are independent, the differential
   crossing sees sigma/sqrt 2) plus the buffers' VDDA sensitivity (a common delay change of both sides is a timing
   shift of the sampled crossing, reference-like). 1/f corner of the logic noise assumed 30 kHz as before.
 * kT/C and the detector gain: the measured A (tt) and C_s = C1 + Gm input + switch junctions replace the step-72
   corner values.
-> data/step78hv_noise.json"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
for q in ("design/budget", "models"):
    sys.path.insert(0, os.path.join(ROOT, q))
import hv_system as HS
import pllmodel as pm
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
C77 = J("design", "clkgen", "data", "step77hv_noise.json")
SIM = J("design", "sspd", "data", "step78hv_sim.json")
FREF = 50e6
VN = dict(typ=100e-9, pess=300e-9)
CS = 34.7e-15 + 8e-15 + 3e-15           # C1 + Gm input (step 79 placeholder) + TG junctions


if __name__ == "__main__":
    fl = np.array(C77["fL"])
    sig = SIM["buf"]["sigma"]/np.sqrt(2)
    Kb = abs(SIM["bufsup"]["k"])
    A = {r["corner"] + str(r["temp"]): r["A"] for r in SIM["char"] if "A" in r and r["vdda"] == 3.3 and r["fref"] == 50e6}
    A_tt = next(r["A"] for r in SIM["char"] if r.get("corner") == "tt" and r.get("temp") == 27 and r.get("vdda") == 3.3
                and r.get("fref") == 50e6 and r.get("vddd") == 1.8)
    A_min = min(r["A"] for r in SIM["char"] if "A" in r)
    out = dict(fL=fl.tolist(), sigma_buf_diff=sig, K_buf=Kb, A_tt=A_tt, A_min=A_min, Cs=CS, L={}, sys={})
    Lbuf = pm.floor_L(fl, 10*np.log10((2*np.pi*FREF*sig)**2/FREF), 30e3)
    for key in ("3.3", "1.0"):
        for cn in ("typ", "pess"):
            P = {k: np.array(v) for k, v in C77["L"][f"{key}_{cn}"].items()}
            P["sspd_buf"] = Lbuf
            P["sspd_buf_vdda"] = 10*np.log10((2*np.pi*FREF)**2*Kb**2*VN[cn]**2*(1 + 10e3/fl)/2)
            P.pop("chain")
            chain = 10*np.log10(sum(10**(v/10) for v in P.values()))
            out["L"][f"{key}_{cn}"] = {k: v.tolist() for k, v in P.items()} | dict(chain=chain.tolist())
            fn = lambda q, c=chain: np.interp(np.log(q), np.log(fl), c)
            over = dict(A=A_tt, Cs=CS) if cn == "typ" else dict(A=A_min, Cs=CS)
            out["sys"][f"{key}_{cn}"] = o = HS.system(cn, ref=fn, corner_over=over)
            print(f"{key} V pp {cn}: chain floor {chain[-1]:.1f} dBc/Hz (SSPD buffers {Lbuf[-1]:.1f}, their VDDA "
                  f"{P['sspd_buf_vdda'][-1]:.1f}); kT/C {o['on']['terms']['SSPD sampler (kT/C)']:.3f} ps; system off "
                  f"{o['off']['total']:.2f} / on {o['on']['total']:.2f} ps, L300k {o['off']['L300k']:.1f} / {o['on']['L300k']:.1f}", flush=True)
    o = HS.system("worst", ref=lambda q: np.interp(np.log(q), np.log(fl), out["L"]["3.3_pess"]["chain"]),
                  corner_over=dict(A=A_min, Cs=CS))
    out["sys"]["3.3_worst"] = o
    print(f"worst: off {o['off']['total']:.2f} / on {o['on']['total']:.2f} ps")
    json.dump(out, open(os.path.join(HERE, "data", "step78hv_noise.json"), "w"), default=float)
