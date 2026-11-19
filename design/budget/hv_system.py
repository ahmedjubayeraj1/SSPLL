#!/usr/bin/env python3
"""hv_system.py - the step-72 HV phase-domain model (method M9) with every block measured so far in the 800 MHz / 5 V
redo put in place of its allocation. Each design step from 76 on calls system() with its own block, so all steps
report the same, cumulative system number.

Measured blocks used (update this list when a step is finished):
  step 73 HV  loop filter R1, C1, C2                       design/loop/data/step73_hv_design.json
  step 74 HV  ring thermal L and 1/f^3 corner (hl6)        design/vco/data/step74hv_hl6.json
  step 75 HV  CCO output-current noise, K_vdd(f)           design/cco/data/step75hv_noise.json, step75hv_sim.json
  step 76 HV  REF receiver L(f) + its supply terms         design/refbuf/data/step76hv_noise.json (when present)
Corners: typ (tt, VDDA noise 100 nV/rtHz), pess (ring +3 dB / corner x2, VDDA 300 nV/rtHz, K_vdd at ss/110 C, 3.13 V),
worst (as pess with VDDA at 2.97 V)."""
import os, sys, json
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for q in ("models", "learn", "design/budget"):
    sys.path.insert(0, os.path.join(ROOT, q))
import pllmodel as pm
import step72_hv_budget as b
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
RING = J("design", "vco", "data", "step74hv_hl6.json")
L73 = J("design", "loop", "data", "step73_hv_design.json")
CCO = J("design", "cco", "data", "step75hv_noise.json")
CSIM = J("design", "cco", "data", "step75hv_sim.json")
KI = 0.62e12
REFNAME = "REF receiver + clock gen + level shifter"


def kvdd_f(f, k1):
    d = np.array(CSIM["psr"]["tt"]); ktt = np.exp(np.interp(np.log(f), np.log(d[:, 0]), np.log(d[:, 1]*KI)))
    return np.maximum(k1, np.where(f > 1e6, ktt, 0))


def system(corner="typ", ref=None, extra=None, band=(10e3, 40e6)):
    """ref: callable f -> L_ref(f) in dBc/Hz AT THE REFERENCE (50 MHz) for the whole REF chain (receiver, clock
    generator, level shifters, SSPD buffers); None keeps the step-72 allocation.
    extra: {name: callable f -> L(f) dBc/Hz at the reference} added as further in-loop reference terms.
    Returns {"off": {...}, "on": {...}} with per-term jitter (ps), total (ps), L(300 kHz) and L(1 MHz) (dBc/Hz)."""
    kc = "typ" if corner == "typ" else "pess"
    kv = CCO["kvdd"][{"typ": "typ", "pess": "pess", "worst": "worst"}[corner]]
    f0, _ = b.spectra(kc, False, lf=(L73["R"], L73["C1"], L73["C2"]))
    over = {"ring VCO core (5 V, 3-stage)": (RING["Lth"], RING["fc3"]) if kc == "typ" else (RING["Lth"] + 3, 2*RING["fc3"]),
            "VDDA noise into the ring (CCO r_out)": (b.ALLOC["VDDA noise into the ring (CCO r_out)"][kc][0], kvdd_f(f0, kv))}
    out = {}
    for on in (False, True):
        f, S = b.spectra(kc, on, over=over, lf=(L73["R"], L73["C1"], L73["C2"]))
        H = pm.loop_H(f, b.FC, b.PMDEG); Gc = pm.ffnc_Gc(f, b.FREF, b.CORNER[kc]["gerr"], on=on)
        T_in = np.abs(H + Gc*(1 - H))**2; T_vco = np.abs((1 - Gc)*(1 - H))**2
        si = np.exp(np.interp(np.log(f), np.log(CCO["f"]), np.log(np.array(CCO["n"])**2)))
        S["CCO current DAC + mirror"] = KI**2*si/f**2*T_vco
        if ref is not None:
            S[REFNAME] = 2*10**(ref(f)/10)*b.N**2*T_in
        for name, fn in (extra or {}).items():
            S[name] = 2*10**(fn(f)/10)*b.N**2*T_in
        j, L = b.jitter(S, f, band=band)
        out["on" if on else "off"] = dict(terms={k: float(v*1e12) for k, v in j.items()}, total=float(j["TOTAL"]*1e12),
                                          L300k=float(L[np.argmin(abs(f - 3e5))]), L1M=float(L[np.argmin(abs(f - 1e6))]))
    return out


if __name__ == "__main__":
    for cn in ("typ", "pess", "worst"):
        r = system(cn)
        print(cn, {k: (round(v["total"], 3), round(v["L300k"], 1)) for k, v in r.items()})
