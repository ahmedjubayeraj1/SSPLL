#!/usr/bin/env python3
"""d2s_hv_system.py - what the D2S does to the system jitter (method M9, the budget phase-domain model).
1. its pole in the cancellation path: G_c(f) x 1 / (1 + j f / f_3dB), at the tt and the slowest f_3dB measured (part B);
   once with the budget's cancellation model (Nagam's pole, -60 deg at f_ref / 7.8) and once with the real hold of this
   SSPD (first-order memory alpha, v2[k] = (1 - alpha) v1[k] + alpha v2[k-1]), which has less phase lag;
2. its noise: the measured input-referred spectrum (part C) is a timing error added at the output (after the
   calibrated NCB, transfer 1), RSS-added to the FFNC-on total;
3. its gain drift after calibration: G changes with temperature at a fixed corner -> the gain error of the cancellation.
-> data/d2s_hv_system.json"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
for q in ("models", "design/budget"):
    sys.path.insert(0, os.path.join(ROOT, q))
import pllmodel as pm
import hv_system as H
d = json.load(open(os.path.join(HERE, "data", "d2s_hv_sim.json")))
SSPD = json.load(open(os.path.join(ROOT, "design", "sspd", "data", "sspd_hv_sim.json")))["char"]
ALPHA = SSPD[0]["alpha"]
orig = pm.ffnc_Gc


def gc(kind, fd):
    def f_(f, fr, g, on=True):
        if not on:
            return np.zeros_like(f, dtype=complex)
        if kind == "model":
            G = orig(f, fr, g, on)
        else:
            x = f/fr
            G = (1 - g)*np.sinc(x)*np.exp(-1j*np.pi*x)*(1 - ALPHA)/(1 - ALPHA*np.exp(-2j*np.pi*x))
        return G/(1 + 1j*f/fd) if fd else G
    return f_


if __name__ == "__main__":
    f3 = {r["cond"]: r["f3"] for r in d["B"]}
    f_tt, f_min = f3["tt 27 °C, 3.3 V"], min(f3.values())
    out = dict(alpha=ALPHA, f3_tt=f_tt, f3_min=f_min, rows=[])
    for kind in ("model", "real hold"):
        for label, fd in (("no D2S pole", None), ("D2S pole, tt", f_tt), ("D2S pole, slowest", f_min)):
            pm.ffnc_Gc = gc(kind, fd)
            r = {c: H.system(c)["on"]["total"] for c in ("typ", "pess")}
            out["rows"].append(dict(cancel=kind, case=label, fd=fd, typ=r["typ"], pess=r["pess"]))
            print(f"{kind:10s} {label:20s} on: typ {r['typ']:.3f} ps, pess {r['pess']:.3f} ps")
    pm.ffnc_Gc = orig
    jt = d["C"][0]["jit"]; jw = max(r["jit"] for r in d["C"])
    base = next(r for r in out["rows"] if r["cancel"] == "model" and r["case"] == "D2S pole, tt")
    out["noise_tt"], out["noise_worst"] = jt, jw
    out["total_typ"] = float(np.hypot(base["typ"], jt*1e12)); out["total_pess"] = float(np.hypot(base["pess"], jw*1e12))
    print(f"D2S noise {jt*1e15:.0f} fs (tt), {jw*1e15:.0f} fs (worst of the noise corners)")
    print(f"FFNC on with the D2S (budget cancellation model): typ {out['total_typ']:.3f} ps, pess {out['total_pess']:.3f} ps")
    # gain drift: G over temperature at tt (part A) -> worst relative change from the 27 C value
    g = {r["cond"]: r["G"] for r in d["A"]}
    g27 = g["tt 27 °C, 3.3 V"]; drift = max(abs(g["tt -40 °C, 3.3 V"]/g27 - 1), abs(g["tt 110 °C, 3.3 V"]/g27 - 1))
    out["drift"] = drift
    for ge in (0.0, drift, 0.10):
        H.b.CORNER["typ"]["gerr"] = ge
        r = H.system("typ")["on"]["total"]
        out.setdefault("gerr", []).append(dict(gerr=ge, typ=r))
        print(f"gain error {ge*100:4.1f} %: FFNC on typ {r:.3f} ps")
    H.b.CORNER["typ"]["gerr"] = 0.10
    json.dump(out, open(os.path.join(HERE, "data", "d2s_hv_system.json"), "w"), indent=1)
