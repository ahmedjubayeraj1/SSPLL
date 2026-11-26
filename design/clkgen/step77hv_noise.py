#!/usr/bin/env python3
"""step77hv_noise.py - the REF chain (receiver step 76 HV + clock generator + level shifters, this step) in the
800 MHz system (method M9 with design/budget/hv_system.py).

Chain L(f) at 50 MHz =  receiver S1 white + quasi-static parts (step76hv_noise.json; S1 only: since this step
                        the sampling edge leaves the receiver at S2's output, refhv)
                      + sampling-edge white jitter of the clock generator (M17, step77hv_sim.json), 1/f corner 30 kHz
                        (assumed, as on 13 Nov: logic flicker is not in M17)
                      + VDDA and VDDD terms with the COMBINED edge sensitivity REF_IN -> cks (M21, step77hv_supply.json; 1 V sine: _1v.json)
                      + SSPD isolation buffers (step 78, -169 dBc/Hz, kept until step 78 is redone)
For the 1 V sine reference the combined sensitivity is only measured with the square input; the clock generator's
own part (combined minus receiver, square input) is added in magnitude to the receiver's sine value (conservative).
-> data/step77hv_noise.json"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
for q in ("design/budget", "models"):
    sys.path.insert(0, os.path.join(ROOT, q))
import hv_system as HS
import pllmodel as pm
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
RX = J("design", "refbuf", "data", "step76hv_noise.json")
RXS = J("design", "refbuf", "data", "step76hv_supply.json")
SIM = J("design", "clkgen", "data", "step77hv_sim.json")
SUP = J("design", "clkgen", "data", "step77hv_supply.json")
_p1 = os.path.join(ROOT, "design", "clkgen", "data", "step77hv_supply_1v.json")
SUP1 = json.load(open(_p1)) if os.path.exists(_p1) else None
FREF = 50e6
SSPDBUF = (-169.0, 30e3)
VN = dict(typ=100e-9, pess=300e-9)


def Kcurve(pts):
    fx, kx = np.array(sorted((max(f, 1e3), abs(k)) for f, k in pts)).T
    return lambda q: np.exp(np.interp(np.log(q), np.log(fx), np.log(kx)))


def L_supply(f, K, vn):
    return 10*np.log10((2*np.pi*FREF)**2*K(f)**2*vn**2*(1 + 10e3/f)/2)


if __name__ == "__main__":
    fl = np.array(RX["fL"])
    Kc = {r: Kcurve([(x["fm"], x["k"]) for x in SUP if x["rail"] == r]) for r in ("vdda", "vddd")}
    Kc1 = {r: Kcurve([(x["fm"], x["k"]) for x in SUP1 if x["rail"] == r]) for r in ("vdda", "vddd")} if SUP1 else None
    Kr = {(r, v): Kcurve([(x["fm"], x["k"]) for x in RXS if x["rail"] == r and x["vpp"] == v])
          for r in ("vdda", "vddd") for v in (3.3, 1.0)}
    # clock generator's own part (magnitude), from the square-input runs
    Kg = {r: (lambda q, r=r: np.abs(Kc[r](q) - Kr[(r, 3.3)](q))) for r in ("vdda", "vddd")}
    sig = SIM["jitter"]["sigma"]
    Lck = pm.floor_L(fl, 10*np.log10((2*np.pi*FREF*sig)**2/FREF), 30e3)
    out = dict(fL=fl.tolist(), sigma_ckg=sig, L={}, sys={},
               K={r: {str(f): float(Kc[r](f)) for f in (1e3, 1e6, 5e6, 2e7)} for r in Kc},
               Kg={r: {str(f): float(Kg[r](f)) for f in (1e3, 1e6, 5e6, 2e7)} for r in Kg})
    for key, vpp in (("3.3", 3.3), ("1.0", 1.0)):
        for cn in ("typ", "pess"):
            L = RX["L"][f"{key}_{cn}"]
            if vpp > 2:
                Ka, Kd = Kc["vdda"], Kc["vddd"]
            elif SUP1:                                   # combined REF_IN -> cks run with the 1 V pp sine (M21)
                Ka, Kd = Kc1["vdda"], Kc1["vddd"]
            else:                                        # estimate until that run exists
                Ka = lambda q: Kr[("vdda", 1.0)](q) + Kg["vdda"](q); Kd = lambda q: Kr[("vddd", 1.0)](q) + Kg["vddd"](q)
            La, Ld = L_supply(fl, Ka, VN[cn]), L_supply(fl, Kd, VN[cn])
            # receiver white part: S1 only (period jitter / sqrt 2, step 76 M15). Step 76's "white" also held its
            # output chain S2 -> level shifter -> NOR, which is no longer in the sampling path; S2 is inside this
            # step's M17 run (refhv node), so it is not counted twice.
            s1 = next(x["per"]/np.sqrt(2) for x in RX["tn"] if x["vpp"] == vpp)
            rxw = np.full_like(fl, 10*np.log10((2*np.pi*FREF*s1)**2/FREF))
            parts = dict(rx_white=rxw, rx_slow=np.array(L["slow"]), vdda=La, vddd=Ld, clkgen=Lck,
                         sspd_buf=pm.floor_L(fl, *SSPDBUF))
            chain = 10*np.log10(sum(10**(v/10) for v in parts.values()))
            out["L"][f"{key}_{cn}"] = {k: v.tolist() for k, v in parts.items()} | dict(chain=chain.tolist())
            fn = lambda q, c=chain: np.interp(np.log(q), np.log(fl), c)
            out["sys"][f"{key}_{cn}"] = o = HS.system(cn, ref=fn)
            print(f"{key} V pp {cn}: chain floor {chain[-1]:.1f} dBc/Hz (rx white {parts['rx_white'][-1]:.1f}, clkgen "
                  f"{Lck[-1]:.1f}, VDDA {La[-1]:.1f}, VDDD {Ld[-1]:.1f}); system off {o['off']['total']:.2f} / on "
                  f"{o['on']['total']:.2f} ps, L300k {o['off']['L300k']:.1f} / {o['on']['L300k']:.1f}", flush=True)
    o = HS.system("worst", ref=lambda q: np.interp(np.log(q), np.log(fl), out["L"]["3.3_pess"]["chain"]))
    out["sys"]["3.3_worst"] = o
    print(f"worst: off {o['off']['total']:.2f} / on {o['on']['total']:.2f} ps")
    K1 = float(Kc["vddd"](1e6))
    out["vddd_max"] = float(np.sqrt(2*10**(-165/10)/(2*np.pi*FREF)**2)/K1)
    print(f"combined VDDD sensitivity {K1*1e12:.0f} ps/V -> VDDD <= {out['vddd_max']*1e9:.0f} nV/rtHz for -165 dBc/Hz")
    json.dump(out, open(os.path.join(HERE, "data", "step77hv_noise.json"), "w"), default=float)
