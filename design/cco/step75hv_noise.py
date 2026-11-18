#!/usr/bin/env python3
"""step75hv_noise.py - output-current noise of the complete 5 V CCO (.noise, all PDK devices, method M11) and its
effect on the system (method M9): S_phi = K_I^2 S_i / f^2, shaped like VCO noise, put into the step-72 HV budget with
the step-74 HV ring, the step-73 HV loop filter and the measured VDDA push (K_vdd from step75hv_sim.py).
-> data/step75hv_noise.json"""
import json, os, sys
import numpy as np
import cco_hv as c
ROOT = os.path.dirname(os.path.dirname(c.HERE))
for q in ("models", "learn", "design/budget"):
    sys.path.insert(0, os.path.join(ROOT, q))
import pllmodel as pm
import step72_hv_budget as b
RING = json.load(open(os.path.join(ROOT, "design", "vco", "data", "step74hv_hl6.json")))
L73 = json.load(open(os.path.join(ROOT, "design", "loop", "data", "step73_hv_design.json")))
SIM = json.load(open(os.path.join(c.HERE, "data", "step75hv_sim.json")))
VD = json.load(open(os.path.join(c.HERE, "data", "step75hv_vdda.json")))     # step75hv_vdda.py: K_vdd vs VDDA level
KI = 0.62e12                                         # Hz/A, step 74 HV ring near 1 mA (tt)


def kvdd_f(f, k1):
    """K_vdd vs ripple frequency: the flat (r_out) part of the case, k1, and the capacitive part that rises above
    ~2 MHz (VDDA -> C_gd / C_db of the cascode -> ring node), taken from the tt AC run; K(f) = max of the two."""
    d = np.array(SIM["psr"]["tt"]); ktt = np.exp(np.interp(np.log(f), np.log(d[:, 0]), np.log(d[:, 1]*KI)))
    return np.maximum(k1, np.where(f > 1e6, ktt, 0))


def system(fs, Si, kvdd, corner="typ"):
    f0, _ = b.spectra(corner, False, lf=(L73["R"], L73["C1"], L73["C2"]))
    over = {"ring VCO core (5 V, 3-stage)": (RING["Lth"], RING["fc3"]) if corner == "typ" else (RING["Lth"] + 3, 2*RING["fc3"]),
            "VDDA noise into the ring (CCO r_out)": (b.ALLOC["VDDA noise into the ring (CCO r_out)"][corner][0], kvdd_f(f0, kvdd))}
    out = {}
    for on in (False, True):
        f, S = b.spectra(corner, on, over=over, lf=(L73["R"], L73["C1"], L73["C2"]))
        H = pm.loop_H(f, b.FC, b.PMDEG); Gc = pm.ffnc_Gc(f, b.FREF, b.CORNER[corner]["gerr"], on=on)
        Ti = np.abs((1 - Gc)*(1 - H))**2
        si = np.exp(np.interp(np.log(f), np.log(fs), np.log(Si**2)))
        S["CCO current DAC + mirror"] = KI**2*si/f**2*Ti
        j, L = b.jitter(S, f)
        out["on" if on else "off"] = dict(cco=j["CCO current DAC + mirror"]*1e12, vdda=j["VDDA noise into the ring (CCO r_out)"]*1e12,
                                          total=j["TOTAL"]*1e12, L300k=float(L[np.argmin(abs(f - 3e5))]))
    return out


if __name__ == "__main__":
    f, n = c.noise(c.D)
    k1 = min(SIM["psr"]["tt"], key=lambda q: abs(q[0] - 1e6))[1]*KI
    kv = lambda tag, v: next(q["kvdd"] for q in VD[tag] if abs(q["vdda"] - v) < 1e-6)
    at = {str(x): float(n[np.argmin(abs(f - x))]) for x in (1e4, 1e5, 3e5, 1e6, 1e7)}
    # allocation for comparison: L = -110.2 dBc/Hz at 1 MHz (0.3 MHz corner) <=> i_n = sqrt(2*10^(L/10))*1e6/K_I
    alloc = np.sqrt(2*10**(-110.2/10))*1e6/KI
    # cases: typ = tt at 3.3 V; pess = ss/110 C at 800 MHz with VDDA at -5 % (3.13 V, the full-spec supply range);
    # worst = ss/110 C at 800 MHz with VDDA at -10 % (2.97 V, the functional limit, MOUT/MC out of saturation)
    K = dict(typ=k1, pess=kv("ss_800", 3.13), worst=kv("ss_800", 2.97), edge=kv("ss_880", 2.97))
    res = dict(f=f.tolist(), n=n.tolist(), at=at, alloc_1M=alloc, kvdd=K,
               typ=system(f, n, K["typ"]), pess=system(f, n, K["pess"], "pess"), worst=system(f, n, K["worst"], "pess"))
    print("noise", {k: round(v*1e12, 2) for k, v in at.items()}, "pA/rtHz; allocation at 1 MHz", round(alloc*1e12, 2))
    print("K_vdd (MHz/V)", {k: round(v/1e6, 2) for k, v in K.items()})
    for cn in ("typ", "pess", "worst"):
        for k, v in res[cn].items():
            print(f"  {cn} FFNC {k}: CCO {v['cco']:.3f} ps, VDDA {v['vdda']:.3f} ps, total {v['total']:.3f} ps, L300k {v['L300k']:.1f}")
    json.dump(res, open(os.path.join(c.HERE, "data", "step75hv_noise.json"), "w"), indent=1, default=float)
