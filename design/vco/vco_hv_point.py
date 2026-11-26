#!/usr/bin/env python3
"""vco_hv_point.py NAME [I0] - one design point of the step-74 redo (5 V, 3 stages, 800 MHz): current for 800 MHz
(tt, 27 C, 10 fF wiring, vtune 1.65 V), then ISF phase noise (thermal + flicker) at that current. -> data/vco_hv_NAME.json"""
import sys, json, os
import vco_hv as v
S2 = v.scaled(v.START, 2.0)
VARIANTS = {
    "s2": S2,                                                        # feasibility ring B x2 with the switched-cap tuning
    "tponly": dict(S2, TN=None, TP=(v.P5, 3.0, 4, 0.5)),             # pMOS-only coupling (no TG nMOS)
    "halftune": dict(S2, S=(v.N5, 4.0, 1, 0.5), C=(v.N5, 5.0, 1, 1.0)),  # half the switch and cap: K_VCO about -80 MHz/V
    "tnlong": dict(S2, TN=(v.N5, 1.5, 2, 1.0)),                       # TG nMOS at L = 1 um, same W
    "hl": dict(S2, S=(v.N5, 4.0, 1, 0.5), C=(v.N5, 5.0, 1, 1.0), TN=(v.N5, 1.5, 2, 1.0)),
    "hl3": dict(S2, S=(v.N5, 4.0, 2, 1.0), C=(v.N5, 5.0, 1, 1.0), TN=(v.N5, 1.5, 2, 1.0)),   # + switch at L 1 um, same W/L
    "hl4": dict(S2, S=(v.N5, 4.0, 2, 1.0), C=(v.N5, 5.0, 1, 1.0), TN=(v.N5, 1.5, 2, 1.0), N=(v.N5, 4.0, 3, 0.5)),  # N x1.5
    "hl5": dict(S2, S=(v.N5, 4.0, 2, 1.0), C=(v.N5, 5.0, 1, 1.0), TN=(v.N5, 1.5, 2, 1.0), N=(v.N5, 4.0, 1, 0.5)),  # N x0.5
    # hl6: hl3 with N at 6 um (between hl3 and hl5), every device x1.25 for thermal margin
    "hl6": dict(P=(v.P5, 5.0, 5, 0.5), N=(v.N5, 3.75, 2, 0.5), S=(v.N5, 5.0, 2, 1.0), C=(v.N5, 6.25, 1, 1.0),
                TN=(v.N5, 1.875, 2, 1.0), TP=(v.P5, 3.75, 2, 0.5)),
    "hl2": dict(S2, S=(v.N5, 4.0, 1, 0.5), C=(v.N5, 5.0, 1, 1.0), TN=(v.N5, 1.5, 4, 1.0)),   # TG nMOS L 1 um, W x2
}
if __name__ == "__main__":
    name = sys.argv[1]; p = VARIANTS[name] if name in VARIANTS else json.loads(sys.argv[3])
    I0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8e-3
    I, r = v.find_current(p, 0.8e9, I0=I0)
    print(f"{name}: I = {I*1e3:.3f} mA, f = {r['f']/1e9:.4f} GHz, ring node {r['vdd_avg']:.3f} V, ppd {r['ppd']:.2f} V", flush=True)
    n = v.isf_noise(p, I)
    n.update(name=name, p={k: (list(x) if isinstance(x, tuple) else x) for k, x in p.items()}, vring=r["vdd_avg"], ppd=r["ppd"])
    json.dump(n, open(os.path.join(v.HERE, "data", f"vco_hv_{name}.json"), "w"), indent=1)
    print(f"{name}: f0 {n['f0']/1e9:.4f} GHz  Lth {n['Lth']:.2f}  Lfl {n['Lfl']:.2f}  Ltot {n['Ltot']:.2f}  fc3 {n['fc3']/1e6:.2f} MHz  "
          f"hdc/hrms {n['hdc_over_hrms']:.3f}", flush=True)
    for k, (a, b) in n["shares"].items():
        print(f"   {k:9s} thermal {100*a:5.1f} %  flicker {100*b:5.1f} %", flush=True)
