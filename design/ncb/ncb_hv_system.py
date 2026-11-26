#!/usr/bin/env python3
"""ncb_hv_system.py - the FFNC path (D2S + NCB) in the system model (method M9). -> data/ncb_hv_system.json
- both control poles (D2S output, NCB bias mirror) multiply the cancellation transfer G_c(f), with the budget's model
  and with the real hold of the SSPD (alpha);
- the measured VDDA sensitivities of the two blocks (added: one supply moves both delays) replace the allocation;
- the D2S noise and the NCB bias-path noise (referred to vff, times K_d) add at the output (RSS);
- the NCB's own switching noise stays at its allocation (-156 dBc/Hz, corner 1 MHz typ), checked by hand in the doc."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
for q in ("models", "design/budget"):
    sys.path.insert(0, os.path.join(ROOT, q))
import pllmodel as pm
import hv_system as H
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
D2 = J("design", "d2s", "data", "d2s_hv_sim.json"); NC = J("design", "ncb", "data", "ncb_hv_sim.json")
ALPHA = J("design", "sspd", "data", "sspd_hv_sim.json")["char"][0]["alpha"]
orig = pm.ffnc_Gc
TT = "tt 27 °C, 3.3 V"


def gc(kind, poles):
    def f_(f, fr, g, on=True):
        if not on:
            return np.zeros_like(f, dtype=complex)
        x = f/fr
        G = orig(f, fr, g, on) if kind == "model" else \
            (1 - g)*np.sinc(x)*np.exp(-1j*np.pi*x)*(1 - ALPHA)/(1 - ALPHA*np.exp(-2j*np.pi*x))
        for fp in poles:
            G = G/(1 + 1j*f/fp)
        return G
    return f_


def jit_from_vff(r, kd):
    f = np.array(r["f"]); v = np.sqrt(np.array(r["vin_nb"])**2 + np.array(r["vin_pd"])**2)/np.sqrt(2)
    b = (f >= 10e3) & (f <= 40e6)
    return float(np.sqrt(np.trapezoid((v[b]*kd)**2, f[b])))


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(ROOT, "design", "d2s")); import d2s_hv as DS
    # the D2S pole with its real load (NCB input 5.6 fF + about 10 fF of wiring) at tt and at the slowest corner
    d2f = {TT: DS.ac(cl=15e-15, vid=0.18)["f3"],
           "ss_hh 110 °C, 2.97 V": DS.ac(corner="ss_hh", temp=110, vdda=2.97, cm=1.4456, cl=15e-15, vid=0.18)["f3"]}
    ncf = {r["cond"]: min(r["f3_nb"], r["f3_pd"]) for r in NC["B"]}
    poles_tt = [d2f[TT], ncf[TT]]; poles_w = [min(d2f.values()), min(ncf.values())]
    ks_d2 = {r["cond"]: r["Ks_ps_per_V"]*1e-12 for r in D2["D"]}
    ks_nc = {r["cond"]: abs(r["Ks"]) for r in NC["C"]}
    ks_typ = ks_d2[TT] + ks_nc[TT]; ks_pess = max(ks_d2.values()) + max(ks_nc.values())
    kd_tt = next(r for r in NC["coverage"] if r["cond"] == TT)["kreq"]
    j_bias = jit_from_vff(next(r for r in NC["D"] if r["cond"] == TT), kd_tt)
    j_bias_w = max(jit_from_vff(r, next(c for c in NC["coverage"] if c["cond"] == r["cond"])["kreq"]) for r in NC["D"])
    j_d2 = D2["C"][0]["jit"]; j_d2_w = max(r["jit"] for r in D2["C"])
    out = dict(poles_tt=poles_tt, poles_worst=poles_w, ks_typ=ks_typ, ks_pess=ks_pess, j_bias=j_bias, j_bias_w=j_bias_w,
               j_d2=j_d2, j_d2_w=j_d2_w, rows=[])
    alloc = dict(H.b.ALLOC["VDDA noise through the NCB"])
    for label, kind, poles, ks in (("budget (allocations)", "model", [], None),
                                   ("model, measured poles and K_s", "model", None, True),
                                   ("real hold, measured poles and K_s", "hold", None, True)):
        res = {}
        for corner in ("typ", "pess"):
            pl = poles if poles is not None else (poles_tt if corner == "typ" else poles_w)
            pm.ffnc_Gc = gc(kind, pl)
            if ks:
                H.b.ALLOC["VDDA noise through the NCB"] = dict(alloc, typ=(alloc["typ"][0], ks_typ), pess=(alloc["pess"][0], ks_pess))
            else:
                H.b.ALLOC["VDDA noise through the NCB"] = dict(alloc)
            r = H.system(corner)["on"]
            extra = (j_d2**2 + j_bias**2) if (ks and corner == "typ") else ((j_d2_w**2 + j_bias_w**2) if ks else 0.0)
            res[corner] = float(np.sqrt(r["total"]**2 + extra*1e24))
            res[corner + "_supply"] = float(r["terms"]["VDDA noise through the NCB"]) if "terms" in r else None
        pm.ffnc_Gc = orig
        out["rows"].append(dict(case=label, **res))
        print(f"{label:38s} FFNC on: typ {res['typ']:.3f} ps, pess {res['pess']:.3f} ps")
    H.b.ALLOC["VDDA noise through the NCB"] = alloc
    # the worst drift after calibration (-38 %) instead of the budget's 30 % pessimistic gain error
    pm.ffnc_Gc = gc("hold", poles_w); H.b.ALLOC["VDDA noise through the NCB"] = dict(alloc, pess=(alloc["pess"][0], ks_pess))
    g0 = H.b.CORNER["pess"]["gerr"]; H.b.CORNER["pess"]["gerr"] = 0.38
    out["pess_gerr38"] = float(np.sqrt(H.system("pess")["on"]["total"]**2 + (j_d2_w**2 + j_bias_w**2)*1e24))
    H.b.CORNER["pess"]["gerr"] = g0; pm.ffnc_Gc = orig; H.b.ALLOC["VDDA noise through the NCB"] = alloc
    print(f"real hold, pess with 38 % gain error: {out['pess_gerr38']:.3f} ps")
    print(f"poles tt {[round(x/1e6) for x in poles_tt]} MHz, worst {[round(x/1e6) for x in poles_w]} MHz; "
          f"K_s typ {ks_typ*1e12:.0f} ps/V, pess {ks_pess*1e12:.0f} ps/V; bias noise {j_bias*1e15:.0f} fs (worst {j_bias_w*1e15:.0f})")
    json.dump(out, open(os.path.join(HERE, "data", "ncb_hv_system.json"), "w"), indent=1)
