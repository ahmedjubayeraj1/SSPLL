#!/usr/bin/env python3
"""step79hv_det.py - the whole detector: 5 V SSPD (step 78 HV) + pulsed Gm (this step) + the step-77 HV clock generator,
with the real Gm on v1 (no placeholder load). Beat run (ring at (16 + 1/32) f_ref): every reference period gives one
sample of the ring phase and one charge packet into the loop filter (vctl held by an ideal source). From the packets
vs phase: the effective detector gain beta_eff = (dq/dphi)/T at the lock point, the charge at the lock point (static
phase offset q/(T beta)), and the charge-phase characteristic over the whole cycle (method M18, extended to M16).
Why this bench: bench B of step79hv_sim.py drives v1 with DC sources, but on the chip v1 tracks the 800 MHz ring
waveform for half of every period and the Gm's current then flows into the dump node; the dump buffer's output
resistance turns that current into a vdump - vctl difference that is charged into the filter when x is switched.
-> data/step79hv_det.json"""
import os, sys, json
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "sspd"))
import sscp_hv as C
import sspd_hv as S
K = C.K
COND = [("tt", 27, 3.3, 1.8), ("tt", 27, 3.3, 1.3), ("tt", 27, 3.3, 2.3), ("ss_hh", 110, 2.97, 1.8), ("ff_ll", -40, 3.63, 1.8)]


def run(a, nb=32):
    corner, temp, vdda, vc = a[:4]
    pp = dict(C.D); pp.update(a[4] if len(a) > 4 else {})
    vddd = 1.8 if corner == "tt" else (1.71 if vdda < 3.3 else 1.89)
    net, fv = S.bench(corner=corner, temp=temp, vdda=vdda, vddd=vddd, nb=nb, save="i(vvc) v(x1.xgm.vdump) v(x1.xgm.x)")
    net = net.replace(f"cg1 v1p 0 {S.LOAD['gm']}\ncg2 v1m 0 {S.LOAD['gm']}\n", "").replace("cckg ckg 0 40f\ncckgb ckgb 0 40f\n", "")
    gm = (C.full(pp).replace(K.CC.LS, "") +
          f"vddd VDDD 0 {vddd}\niib 0 ib {pp['IT']}\nvpen pll_en 0 {vddd}\nvc0 icp0 0 0\nvc1 icp1 0 0\nvvc vctl 0 {vc}\n"
          "x1 v1p v1m vctl ckg ckgb ib icp0 icp1 pll_en VDDA VDDD 0 sspll_sscp_hv_top\n")
    net = net.replace("xcg refclk refhv", gm + "xcg refclk refhv", 1)
    _, d = S.run(net, ["w.txt"])
    z = d["w.txt"]; t = z[:, 0]; g = lambda i: z[:, 2*i + 1]
    cks, ckg, v1p, v1m, ivc, vdump, x = g(0), g(1), g(3), g(4), g(9), g(10), g(11)
    T = 20e-9; ts = K.xings(t, cks, vdda/2, False); ts = ts[ts > 2*T]
    rows = []
    for s in ts[:-1]:
        w = (t >= s - 1e-9) & (t < s - 1e-9 + T)
        q = np.trapezoid(ivc[w], t[w])                                   # into the filter
        tg = K.xings(t, ckg, vdda/2, True); tg = tg[tg > s][0]
        v1 = np.interp(tg + 0.2e-9, t, v1p) - np.interp(tg + 0.2e-9, t, v1m)
        err = np.interp(tg - 20e-12, t, vdump) - vc                     # vdump - vctl just before the pulse
        rows.append(((2*np.pi*fv*s) % (2*np.pi), q, v1, err))
    r = np.array(rows)
    ph, q, v1 = r[:, 0], r[:, 1], r[:, 2]
    o = np.argsort(ph); ph_s, v1_s, q_s = ph[o], v1[o], q[o]
    i0 = [i for i in range(len(ph_s)) if v1_s[i - 1] < 0 <= v1_s[i]][0]
    dp = (ph_s[i0] - ph_s[i0 - 1]) % (2*np.pi)
    phi0 = (ph_s[i0 - 1] + (0 - v1_s[i0 - 1])*dp/(v1_s[i0] - v1_s[i0 - 1])) % (2*np.pi)
    dphi = (ph_s - phi0 + np.pi) % (2*np.pi) - np.pi
    m = np.abs(dphi) < 0.35
    c = np.polyfit(dphi[m], q_s[m], 1)
    return dict(var=a[5] if len(a) > 5 else "", corner=corner, temp=temp, vdda=vdda, vc=vc, beta_eff=float(c[0]/T), q0=float(c[1]), phi_os=float(-c[1]/c[0]),
                err_max=float(np.max(np.abs(r[:, 3]))), rows=r.tolist(), phi0=float(phi0))


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else ""
    if tag == "cdump":                    # dump-node decoupling study at tt, V_cont 1.8 V
        cond = [("tt", 27, 3.3, 1.8, dict(CDUMP=("cap_mim_m3_1", 22.4, 1, 22.4)), "CDUMP 1 pF"),
                ("tt", 27, 3.3, 1.8, dict(CDUMP=("cap_mim_m3_1", 22.4, 2, 22.4)), "CDUMP 2 pF")]
    else:
        cond = COND
    with Pool(2) as pool:
        res = pool.map(run, cond)
    for x in res:
        print(f"{x['var']} {x['corner']:5s} {x['temp']:4d} C {x['vdda']} V V_cont {x['vc']}: beta_eff {x['beta_eff']*1e6:.3f} uA/rad, "
              f"q(lock) {x['q0']*1e15:+.2f} fC -> phase offset {x['phi_os']*1e3:+.1f} mrad, |vdump - vctl| before the pulse "
              f"<= {x['err_max']*1e3:.1f} mV", flush=True)
    json.dump(res, open(os.path.join(HERE, "data", f"step79hv_det{('_' + tag) if tag else ''}.json"), "w"))
