#!/usr/bin/env python3
"""fll_hv_acq.py - step 81: acquisition sweeps with the time-domain model fll_hv_model.py (method M26).
  A  FLL charge-pump current I_cp: lock time over start voltage, corner and start phase
  B  lock-detector settings (window w_in, count nlock) at the chosen I_cp
  C  robustness: loop gain x0.6 / x1.5 (K_VCO, beta, I_cp spread), packet delay 1.8 / 4.2 ns, divider delay 0.5-2 ns
  D  FLL loop alone, linear: f_c and PM of the FLL loop vs I_cp (same filter, N = 16)
  E  why the FLL exists: the sub-sampling loop alone, started near 750 / 850 MHz, locks there (python3 fll_hv_acq.py E
     adds only this part to the existing results)
Results: data/fll_hv_acq.json"""
import os, sys, json, itertools
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "design", "loop"))
import fll_hv_model as M
import sampled_loop as sl
V0S = (0.0, 0.8, 1.6, 2.4, 3.3); CORNERS = ("tt", "ss", "ff"); TH0 = (0.05, 0.3, 0.55, 0.8)


def one(a):
    v0, c, th, p, tstop = a
    o = M.simulate(v0, c, p, tstop=tstop, theta0=th)
    lk = o["lock"]
    ok = abs(o["f"][-1] - M.F0) < 1e3 and lk[-1] and bool(lk[-40:].all())
    return dict(v0=v0, corner=c, th=th, p={k: v for k, v in p.items() if not callable(v)}, ok=bool(ok),
                t_lock=float(M.lock_time(o)), t_det=float(o["t"][np.argmax(lk)]) if lk.any() else None,
                toggles=int(np.sum(np.diff(lk.astype(int)) != 0)), f_end=float(o["f"][-1]))


def sweep(ps, tstop=12e-6):
    args = [(v0, c, th, p, tstop) for p in ps for v0 in V0S for c in CORNERS for th in TH0]
    with Pool(2) as P:
        return P.map(one, args)


def summary(rows, key):
    out = {}
    for r in rows:
        out.setdefault(key(r), []).append(r)
    res = []
    for k, rr in out.items():
        tl = np.array([r["t_lock"] for r in rr if r["ok"]])
        res.append(dict(key=k, n=len(rr), fail=sum(not r["ok"] for r in rr), typ=float(np.median(tl)) if len(tl) else None,
                        max=float(tl.max()) if len(tl) else None, toggles=max(r["toggles"] for r in rr)))
        print(f"  {k}: {len(rr)} runs, fail {res[-1]['fail']}, lock time median {res[-1]['typ']*1e6 if res[-1]['typ'] else 0:.2f} us, "
              f"max {res[-1]['max']*1e6 if res[-1]['max'] else 0:.2f} us, max lock_det toggles {res[-1]['toggles']}", flush=True)
    return res


def fll_linear():
    rows = []
    for icp in (10e-6, 20e-6, 40e-6, 60e-6, 80e-6):
        for kv in (110e6, 173e6, 250e6):
            beq = icp/(2*np.pi*M.N)
            fc, pm = sl.margins(M.R1, M.C1, M.C2, 2*np.pi*kv, beq, M.T, 1.5e-9)
            rows.append(dict(icp=icp, kv=kv, fc=fc, pm=pm))
    return rows


def harmonic():
    f = M.tuning("tt"); vs = np.linspace(0.6, 2.6, 2001); rows = []
    for target in (701e6, 752e6, 849e6, 851e6, 898e6):
        v0 = float(vs[np.argmin(abs(f(vs) - target))])
        a = M.simulate(v0, "tt", dict(fll=False), tstop=4e-6); b = M.simulate(v0, "tt", {}, tstop=6e-6)
        rows.append(dict(start=float(f(v0)), v0=v0, sspll_only=float(a["f"][-1]), with_fll=float(b["f"][-1]),
                         t_lock=float(M.lock_time(b))))
        print(f"  start {f(v0)/1e6:.1f} MHz: SSPLL alone -> {a['f'][-1]/1e6:.3f} MHz; with FLL -> {b['f'][-1]/1e6:.3f} MHz "
              f"in {M.lock_time(b)*1e6:.2f} us", flush=True)
    return rows


if __name__ == "__main__" and sys.argv[1:] == ["F"]:
    # the circuit as measured at transistor level: dead zone 0.4 (tt) .. 0.65 ns (ss), effective w_in 0.45 .. 0.8 ns
    path = os.path.join(HERE, "data", "fll_hv_acq.json"); R = json.load(open(path))
    print("F: measured dead zone and windows")
    # tt / ss / ff as measured on the open-loop bench (dead zone, reset, acquire window, hold window)
    rows = sweep([dict(M.P0, t_dz=dz, t_rst=rst, w_in=w, w_out=wo) for dz, rst, w, wo in (
        (0.4e-9, 0.31e-9, 0.60e-9, 1.99e-9), (0.65e-9, 0.56e-9, 0.74e-9, 2.86e-9), (0.3e-9, 0.2e-9, 0.48e-9, 1.45e-9))])
    R["F"] = rows; R["F_sum"] = summary(rows, lambda r: f"t_dz {r['p']['t_dz']*1e9:.2f} ns, w_in {r['p']['w_in']*1e9:.2f} ns, "
                                                      f"w_out {r['p']['w_out']*1e9:.2f} ns")
    json.dump(R, open(path, "w"), indent=1, default=float); sys.exit()

if __name__ == "__main__" and sys.argv[1:] == ["E"]:
    path = os.path.join(HERE, "data", "fll_hv_acq.json"); R = json.load(open(path))
    print("E: sub-sampling loop alone vs with the FLL"); R["E"] = harmonic()
    json.dump(R, open(path, "w"), indent=1, default=float); sys.exit()

if __name__ == "__main__":
    R = {}
    print("D: FLL loop alone (linear, exact sampled model)")
    R["linear"] = fll_linear()
    for r in R["linear"]:
        print(f"  I_cp {r['icp']*1e6:.0f} uA, K_VCO {r['kv']/1e6:.0f} MHz/V: f_c {r['fc']/1e6:.2f} MHz, PM {r['pm']:.1f}")
    print("A: I_cp")
    rows = sweep([dict(M.P0, icp=i) for i in (10e-6, 20e-6, 40e-6, 60e-6, 80e-6)])
    R["A"] = rows; R["A_sum"] = summary(rows, lambda r: f"I_cp {r['p']['icp']*1e6:.0f} uA")
    print("B: lock detector")
    rows = sweep([dict(M.P0, w_in=w, nlock=n) for w, n in ((0.4e-9, 16), (0.6e-9, 8), (0.6e-9, 32), (1.0e-9, 16), (2.0e-9, 16))])
    R["B"] = rows; R["B_sum"] = summary(rows, lambda r: f"w_in {r['p']['w_in']*1e9:.1f} ns, nlock {r['p']['nlock']}")
    print("C: robustness")
    ps = [dict(M.P0, icp=M.P0["icp"]*g, qscale=g) for g in (0.6, 1.5)] + \
         [dict(M.P0, t_p=tp) for tp in (1.8e-9, 4.2e-9)] + [dict(M.P0, t_div=td) for td in (0.5e-9, 2.0e-9)]
    rows = sweep(ps)
    R["C"] = rows; R["C_sum"] = summary(rows, lambda r: ", ".join(f"{k} {v:.3g}" for k, v in r["p"].items()
                                                                if k in ("icp", "qscale", "t_p", "t_div") and v != M.P0[k]) or "nominal")
    print("E: sub-sampling loop alone vs with the FLL"); R["E"] = harmonic()
    json.dump(R, open(os.path.join(HERE, "data", "fll_hv_acq.json"), "w"), indent=1, default=float)
