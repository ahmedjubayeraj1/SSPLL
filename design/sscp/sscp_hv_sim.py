#!/usr/bin/env python3
"""sscp_hv_sim.py - verification of the 5 V pulsed-Gm charge pump (step 79). -> data/sscp_hv_sim.json
A  DC transfer (Gm on): G, offset, linear range over corners, VDDA, V_cont = 1.3 / 1.8 / 2.3 V and the trim codes  (M10)
B  pulsed operation with the step-77 HV clock generator: average current into the loop filter vs input, charge per
   period at zero input (charge injection / mismatch -> static phase offset and f_ref ripple)                     (M16)
C  output current noise with the Gm on (.noise, CCVS read-out)                                                       (M11)
D  dump buffer: tracking error vdump - vctl and closed-loop AC (peaking = stability)                                  (M10)
E  VDDA rejection: output current per volt of VDDA at zero input (AC)                                                (M11)
F  power from VDDA (DC, 3 slices)"""
import os, re, json, sys
import numpy as np
from multiprocessing import Pool
import sscp_hv as C
HERE = os.path.dirname(os.path.abspath(__file__))
CODES = {"00": (1, 1, 1, 0, 0), "01": (1, 1, 1, 1, 0), "10": (1, 1, 0, 0, 0), "11": (1, 1, 1, 1, 1)}
CORN = [("tt", 27, 3.3), ("ss", 110, 2.97), ("ss", -40, 2.97), ("ff", -40, 3.63), ("ff", 110, 3.63), ("sf", 27, 3.3),
        ("fs", 27, 3.3), ("ss_hh", 110, 2.97), ("ff_ll", -40, 3.63), ("hl", 27, 3.3), ("lh", 27, 3.3)]


def dcjob(a):
    c, t, va, vc, code = a
    r = C.dc_transfer(corner=c, temp=t, vdda=va, vc=vc, en=CODES[code], cm=va*0.503)
    return dict(corner=c, temp=t, vdda=va, vc=vc, code=code, G=abs(r["G"]), v_os=r["v_os"], lin=r["lin"],
                imax=r["imax"], imin=r["imin"])


def pulsed(a):
    """a = (vd, vc). Real clock generator (ideal refhv / refclk edges), 8 periods; average current into vctl over the
    last 4 and the charge per period."""
    vd, vc = a
    T = 20e-9; p = C.D
    net = (f"* pulsed gm\n.lib {C.LIB} tt\n.temp 27\n{C.K.cells()}{C.full(p).replace(C.K.CC.LS, '')}"
           f"vdda VDDA 0 3.3\nvddd VDDD 0 1.8\niib 0 ib {p['IT']}\nvpen pll_en 0 1.8\nvc0 icp0 0 0\nvc1 icp1 0 0\n"
           f"vrh refhv 0 pulse(0 3.3 5n 300p 300p {T/2 - 300e-12} {T})\nvrc refclk 0 pulse(0 1.8 5.2n 300p 300p {T/2 - 300e-12} {T})\n"
           "xcg refclk refhv cks cksb ckg ckgb ckh ckhb VDDD VDDA 0 0 sspll_clkgen_hv\n"
           f"ccks cks 0 60f\nccksb cksb 0 60f\nckh1 ckh 0 40f\nckh2 ckhb 0 40f\n"
           f"vp v1p 0 {1.66 + vd/2}\nvm v1m 0 {1.66 - vd/2}\nvvc vctl 0 {vc}\n"
           "x1 v1p v1m vctl ckg ckgb ib icp0 icp1 pll_en VDDA VDDD 0 0 sspll_sscp_hv_top\n"
           f".control\nsave vvc#branch v(ckg)\ntran 2p {8*T}\nwrdata w.txt vvc#branch v(ckg)\n.endc\n.end\n")
    _, d = C.run(net, ["w.txt"])
    z = d["w.txt"]; t, i = z[:, 0], z[:, 1]
    w = t > 4*T
    q = np.trapezoid(i[w], t[w])/4                       # charge per period INTO the source = into the filter
    tg = C.K.xings(t, z[:, 3], 1.65, True); tf = C.K.xings(t, z[:, 3], 1.65, False)
    tg, tf = tg[tg > 4*T], tf[tf > 4*T]
    tau = float(np.mean(tf[:len(tg)] - tg[:len(tf)])) if len(tg) and len(tf) else float("nan")
    return dict(vd=vd, vc=vc, q=float(q), i_avg=float(q/T), tau=tau)


def noise():
    net = C.head() .replace("vvc vctl 0 1.8", "vvc v2 0 1.8\nvmeas vctl v2 0\nh1 o 0 vmeas 1") + (
        "vp v1p 0 dc 1.66 ac 1\nvm v1m 0 1.66\n.control\noption sparse\nnoise v(o) vp dec 10 1e3 1e9\n"
        "setplot noise1\nwrdata n.txt onoise_spectrum\n.endc\n.end\n")
    _, d = C.run(net, ["n.txt"])
    z = d["n.txt"]
    return z[:, 0].tolist(), z[:, 1].tolist()


def buffer_check(a):
    c, t, va, vc = a
    net = C.head(corner=c, temp=t, vdda=va, vc=vc).replace(f"vvc vctl 0 {vc}", f"vvc vctl 0 dc {vc} ac 1") + (
        f"vp v1p 0 {va*0.503}\nvm v1m 0 {va*0.503}\n.control\nop\nprint v(x1.vdump)\n"
        "ac dec 10 1e3 1e9\nwrdata a.txt mag(v(x1.vdump))\n.endc\n.end\n")
    out, d = C.run(net, ["a.txt"])
    vdump = float(re.search(r"v\(x1.vdump\) = (\S+)", out).group(1))
    z = d["a.txt"]
    return dict(corner=c, temp=t, vdda=va, vc=vc, err=vdump - vc, peak_db=float(20*np.log10(z[:, 1].max())),
                f3db=float(z[np.argmin(abs(z[:, 1] - 0.707)), 0]))


def psr():
    net = C.head().replace("vdda VDDA 0 3.3", "vdda VDDA 0 dc 3.3 ac 1") + (
        "vp v1p 0 1.66\nvm v1m 0 1.66\n.control\nac dec 10 1e3 1e8\nwrdata a.txt mag(i(vvc))\nop\nprint vdda#branch\n.endc\n.end\n")
    out, d = C.run(net, ["a.txt"])
    z = d["a.txt"]
    return dict(f=z[:, 0].tolist(), y=z[:, 1].tolist(), idd=-float(re.search(r"vdda#branch = (\S+)", out).group(1)))


def part(name, fn):
    """Checkpoint: each part is saved when done, so a restart of the environment does not lose finished parts."""
    f = os.path.join(HERE, "data", f"sscp_hv_part_{name}.json")
    if os.path.exists(f):
        return json.load(open(f))
    r = fn(); json.dump(r, open(f, "w")); return r


if __name__ == "__main__":
    res = {}
    jobs = [(c, t, va, 1.8, "00") for c, t, va in CORN]
    jobs += [("tt", 27, 3.3, vc, "00") for vc in (1.3, 2.3)] + [("ss", 110, 2.97, vc, "00") for vc in (1.3, 2.3)]
    jobs += [("ff", -40, 3.63, vc, "00") for vc in (1.3, 2.3)] + [("tt", 27, 3.3, 1.8, code) for code in ("01", "10", "11")]
    with Pool(2) as pool:
        res["dc"] = part("A", lambda: pool.map(dcjob, jobs))
        print("A done", flush=True)
        for r in res["dc"]:
            print(f"  {r['corner']:5s} {r['temp']:4d} C {r['vdda']} V vctl {r['vc']} code {r['code']}: G {r['G']*1e6:.2f} uS, "
                  f"v_os {r['v_os']*1e3:.2f} mV, linear {r['lin'][0]:.2f}..{r['lin'][1]:.2f} V", flush=True)
        res["buffer"] = part("D", lambda: pool.map(buffer_check, [(c, t, va, vc) for c, t, va in CORN[:5] for vc in (1.3, 1.8, 2.3)]))
        for r in res["buffer"]:
            print(f"  D {r['corner']} {r['temp']} {r['vdda']} vctl {r['vc']}: vdump - vctl {r['err']*1e3:.2f} mV, "
                  f"peaking {r['peak_db']:.2f} dB, f3dB {r['f3db']/1e6:.1f} MHz", flush=True)
        res["pulsed"] = part("B", lambda: pool.map(pulsed, [(0.0, 1.8), (0.1, 1.8), (-0.1, 1.8), (0.0, 1.3), (0.0, 2.3)]))
    for r in res["pulsed"]:
        print(f"  B vd {r['vd']} vctl {r['vc']}: charge/period {r['q']*1e15:.2f} fC, average {r['i_avg']*1e9:.2f} nA, "
              f"tau {r['tau']*1e12:.0f} ps", flush=True)
    f, n = noise(); res["noise"] = dict(f=f, n=n)
    print("C noise at 1 MHz", np.interp(1e6, f, n)*1e12, "pA/rtHz", flush=True)
    res["psr"] = psr()
    print("E |dI/dVDDA| at 1 MHz", np.interp(1e6, res["psr"]["f"], res["psr"]["y"])*1e9, "nA/V; I(VDDA)", res["psr"]["idd"]*1e6, "uA", flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "sscp_hv_sim.json"), "w"))
