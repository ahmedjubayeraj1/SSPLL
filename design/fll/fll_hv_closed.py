#!/usr/bin/env python3
"""fll_hv_closed.py - closed-loop transient of the transistor-level FLL with the drawn loop filter and a
behavioural ring (method M27): the ring is a phase integrator, d(phi)/dt = f(V_cont) from the VCO tuning curve
(tt, scaled so that 800 MHz falls at 1.8 V), squared to a 0..VDDA clock by tanh(sin). The sub-sampling loop is left
out, so the run shows the FLL alone up to lock_det; the same case is run in the time-domain model (sspll = False) and
the two V_cont trajectories are compared.
python3 fll_hv_closed.py [v0 ...]   -> data/fll_hv_closed.json"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "design", "loop"))
import fll_hv as F
import fll_hv_model as M
import lf_hv as LF
from multiprocessing import Pool


def lf_drawn():
    S = json.load(open(os.path.join(ROOT, "design", "loop", "data", "lf_hv_size.json")))
    return dict(LF.D, R1=tuple(S["R1"]), C2=tuple(S["C2"]))


def run(v0, corner="tt", temp=27, tstop=2.5e-6):
    f = M.tuning(corner)
    vs = np.r_[np.linspace(0, 3.3, 34)]
    table = ", ".join(f"{v:.3f}, {f(v):.6e}" for v in vs)
    net = (f"* fll closed loop\n.lib {F.LIB} {corner}\n.temp {temp}\n.include {F.STDLIB}\n{F.fll_top()}{LF.cells(lf_drawn())}"
           "vdda VDDA 0 3.3\nvddd VDDD 0 1.8\nvssa VSSA 0 0\nvssd VSSD 0 0\niib VDDA ib 5u\n"
           "ven fll_en 0 pwl(0 0 20n 0 20.1n 1.8)\nvref refclk 0 pulse(0 1.8 10n 100p 100p 9.9n 20n)\n"
           f"xlf vctl VSSA sspll_lf_hv\ncld vctl 0 175f\nvinit vi 0 {v0}\nrinit vi vctl 1e9\n"
           f"bvco 0 phi i = pwl(v(vctl), {table})\ncphi phi 0 1\n"
           "bck clkp 0 v = 1.65*(1 + tanh(6*sin(2*3.14159265358979*v(phi))))\n"
           "x1 clkp refclk fll_en ib vctl lock_det fll_dir VDDA VDDD VSSA VSSD sspll_fll_hv\n"
           f".ic v(phi)=0.3\n.control\nsave v(vctl) v(lock_det) v(phi)\noption interp\ntran 10p {tstop} 0 10p\n"
           "wrdata w.txt v(vctl) v(lock_det) v(phi)\n.endc\n.end\n")
    out, d = F.run(net, ["w.txt"])
    if "w.txt" not in d:
        raise RuntimeError(out[-1500:])
    z = d["w.txt"]
    t, v, lk = z[:, 0], z[:, 1], z[:, 3]
    k = np.arange(0, len(t), max(1, len(t)//3000))
    o = M.simulate(v0, corner, dict(sspll=False), tstop=tstop, theta0=0.3)
    return dict(v0=v0, corner=corner, t=t[k].tolist(), v=v[k].tolist(), lock=lk[k].tolist(),
                t_lock=float(t[np.argmax(lk > 0.9)]) if (lk > 0.9).any() else None,
                model=dict(t=o["t"].tolist(), v=o["v"].tolist(), lock=o["lock"].astype(int).tolist()))


if __name__ == "__main__":
    v0s = [float(x) for x in sys.argv[1:]] or [1.0, 2.8]
    with Pool(2) as P:
        res = P.map(run, v0s)
    for r in res:
        tm = np.array(r["model"]["t"]); lm = np.array(r["model"]["lock"])
        print(f"  v0 {r['v0']} V: lock_det at {r['t_lock']*1e6 if r['t_lock'] else -1:.2f} us (transistor FLL), "
              f"{tm[np.argmax(lm)]*1e6 if lm.any() else -1:.2f} us (model); V_cont at lock {np.interp(r['t_lock'] or 0, r['t'], r['v']):.3f} V")
    json.dump(res, open(os.path.join(HERE, "data", "fll_hv_closed.json"), "w"))
