#!/usr/bin/env python3
"""step74_point.py NAME - one design point of the step-74 study: current for 1.6 GHz (tt, 27 C, 10 fF, vtune 0.9)
and ISF phase noise (thermal + flicker) at that current. Variants are defined in VARIANTS. -> data/step74_NAME.json"""
import sys, json, os
import vco
B = vco.BASE
VARIANTS = {
    "base": dict(B),
    "nlvt": dict(B, N=("nfet_01v8_lvt", 3.0, 2, 0.15)),
    "nL025": dict(B, N=("nfet_01v8", 4.0, 2, 0.25)),
    "pwide": dict(B, P=("pfet_01v8", 3.5, 4, 0.15)),
    "nnarrow": dict(B, N=("nfet_01v8", 2.5, 2, 0.15)),
    "pL018": dict(B, P=("pfet_01v8", 3.5, 4, 0.18)),
    # quiet: the flicker sources found in "base" (tuning switch, TG nMOS) drawn at L = 0.5 um, same W/L
    "quiet": dict(B, S=("nfet_01v8", 3.75, 2, 0.5), TN=("nfet_01v8", 2.1, 1, 0.5)),
    # q2: same idea at L = 0.3 um (gate area x4 instead of x11) - less extra load
    "q2": dict(B, S=("nfet_01v8", 4.5, 1, 0.3), TN=("nfet_01v8", 1.26, 1, 0.3)),
    # q3: switch at L = 0.3 um, TG nMOS kept short but half as wide (its coupling job is shared with the pMOS)
    "q3": dict(B, S=("nfet_01v8", 4.5, 1, 0.3), TN=("nfet_01v8", 0.84, 1, 0.3)),
}
if __name__ == "__main__":
    name = sys.argv[1]; p = VARIANTS[name]
    I0 = float(sys.argv[2]) if len(sys.argv) > 2 else 1.25e-3
    I, r = vco.find_current(p, 1.6e9, I0=I0)
    print(f"{name}: I = {I*1e3:.3f} mA, f = {r['f']/1e9:.4f} GHz, ring node {r['vdd_avg']:.3f} V", flush=True)
    n = vco.isf_noise(p, I)
    n.update(name=name, p={k: list(v) for k, v in p.items()}, vring=r["vdd_avg"], ppd=r["ppd"])
    json.dump(n, open(os.path.join(vco.HERE, "data", f"step74_{name}.json"), "w"), indent=1)
    print(f"{name}: f0 {n['f0']/1e9:.4f} GHz  Lth {n['Lth']:.2f}  Lfl {n['Lfl']:.2f}  Ltot {n['Ltot']:.2f}  fc3 {n['fc3']/1e6:.2f} MHz  "
          f"hdc/hrms {n['hdc_over_hrms']:.3f}", flush=True)
    for k, (a, b) in n["shares"].items():
        print(f"   {k:9s} thermal {100*a:5.1f} %  flicker {100*b:5.1f} %")
