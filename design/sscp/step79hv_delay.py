#!/usr/bin/env python3
"""step79hv_delay.py - recovery of the pulsed Gm after the SSPD's tracking phase: the locked detector (SSPD + Gm, ring at
exactly 16 f_ref, sampling near the zero crossing) with the Gm's steering clocks from ideal sources at a variable delay
after the sample (0.7 / 2 / 3 / 4.5 ns, 0.53 ns wide). Two lock phases 0.06 rad apart give the gain per volt of v1; the
charge at lock is the static error. Run on the first mirror-less Gm (before the noise resize) with the 2 pF dump
capacitor; it set the step-77 gap-1 delay. -> data/step79hv_delay.json"""
import os, sys, json, numpy as np
sys.path.insert(0, "/home/claude/SSPLL/design/sscp"); sys.path.insert(0, "/home/claude/SSPLL/design/sspd")
from multiprocessing import Pool
import sscp_hv as C, sspd_hv as S
K = C.K
def one(a):
    phi, dly = a
    T = 20e-9; fv = 16*50e6; Tv = 1/fv
    s_est = T/4 + 0.425e-9
    td = (s_est - phi/(2*np.pi*fv)) % Tv
    pp = dict(C.D); pp["CDUMP"] = ("cap_mim_m3_1", 22.4, 2, 22.4)
    net, _ = S.bench(nb=1e15, nper=8, td=td, save="i(vvc)", n=16)
    net = net.replace(f"cg1 v1p 0 {S.LOAD['gm']}\ncg2 v1m 0 {S.LOAD['gm']}\n", "").replace("cckg ckg 0 40f\ncckgb ckgb 0 40f\n", "")
    # the Gm's steering clocks: ideal, 'dly' after the sampling edge (cks falls ~0.425 ns after refhv at T/4), width 0.53 ns
    t0 = T/4 + 0.425e-9 + dly
    gm = (C.full(pp).replace(K.CC.LS, "") + f"vddd VDDD 0 1.8\niib 0 ib {pp['IT']}\nvpen pll_en 0 1.8\nvc0 icp0 0 0\nvc1 icp1 0 0\nvvc vctl 0 1.8\n"
          f"vg gg 0 pulse(0 3.3 {t0} 80p 80p 0.45n {T})\nvgb ggb 0 pulse(3.3 0 {t0} 80p 80p 0.45n {T})\n"
          "x1 v1p v1m vctl gg ggb ib icp0 icp1 pll_en VDDA VDDD 0 0 sspll_sscp_hv_top\ncg1 gg 0 9f\ncg2 ggb 0 9f\n")
    net = net.replace("xcg refclk refhv", gm + "xcg refclk refhv", 1)
    _, d = S.run(net, ["w.txt"]); z = d["w.txt"]; t = z[:, 0]; ivc = z[:, 19]
    q = [float(np.trapezoid(ivc[(t > k*T) & (t < (k+1)*T)], t[(t > k*T) & (t < (k+1)*T)])) for k in range(4, 8)]
    ts = K.xings(t, z[:, 1], 1.65, False); v1 = float(np.interp(ts[-2] + 1e-9, t, z[:, 7]) - np.interp(ts[-2] + 1e-9, t, z[:, 9]))
    return dict(phi=phi, dly=dly, q=float(np.mean(q[-2:])), v1=v1)
jobs = [(phi, d) for d in (0.7e-9, 2e-9, 3e-9, 4.5e-9) for phi in (-0.46, -0.40)]
with Pool(2) as p:
    r = p.map(one, jobs)
json.dump(r, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "step79hv_delay.json"), "w"))
for d in (0.7e-9, 2e-9, 3e-9, 4.5e-9):
    a, b = [x for x in r if x["dly"] == d]
    g = (b["q"] - a["q"])/(b["v1"] - a["v1"])
    print(f"delay {d*1e9:.1f} ns: q(lock) {a['q']*1e15:+.2f} fC at v1 {a['v1']*1e3:.0f} mV, gain {g*1e15:.2f} fC/V (G*tau ~ {18.42e-6*0.53e-9*1e15:.2f})")
