#!/usr/bin/env python3
"""hv_vco.py - feasibility of a ring VCO in 5 V devices (g5v0d10v5, L >= 0.5 um) for the device-rule migration.
Candidates (all with a 5 V output-buffer inverter + 10 fF on every ring node and 8 fF wiring per node):
  A  3-stage single-ended inverter ring, supplied from the CCO node (ideal voltage V_ring stands for the CCO)
  B  3-stage pseudo-differential ring (step-74 cell style: two inverter rings tied by always-on transmission gates)
  C3/C4  Maneatis differential ring (symmetric pMOS loads, nMOS tail), 3 or 4 stages, replica-biased: an ideal
     amplifier sets the tail bias so that a replica half-cell output equals V_bp; control = V_bp (swing = VDD - V_bp)
Worst corner for speed: ss, 110 C, VDDA = 3.0 V; A/B get at most V_ring = 2.6 V (0.4 V for the CCO mirror)."""
import os, re, sys, json, subprocess, tempfile
import numpy as np
from multiprocessing import Pool
LIB = "/home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice"
SPI = "/home/claude/pdk/sky130A/libs.tech/ngspice/spinit"
HERE = os.path.dirname(os.path.abspath(__file__))
N5, P5 = "sky130_fd_pr__nfet_g5v0d10v5", "sky130_fd_pr__pfet_g5v0d10v5"

def m(name, d, g, s, b, mod, w, l=0.5):
    return f"{name} {d} {g} {s} {b} {mod} w={w} l={l} nf=1 ad={w*0.29:.3f} as={w*0.29:.3f} pd={2*w+0.58:.3f} ps={2*w+0.58:.3f}\n"

def buf(node, vdd):            # output buffer on every ring node + its load, wiring cap
    return (m(f"xbn_{node}", f"b_{node}", node, "0", "0", N5, 1.0) + m(f"xbp_{node}", f"b_{node}", node, vdd, vdd, P5, 2.5) +
            f"cb_{node} b_{node} 0 10f\ncw_{node} {node} 0 8f\n")

def ring_A(n=3, wn=4, wp=10):
    c = ""
    for i in range(n):
        a, b = f"a{i}", f"a{(i+1) % n}"
        c += m(f"xn{i}", b, a, "0", "0", N5, wn) + m(f"xp{i}", b, a, "vr", "vr", P5, wp) + buf(b, "vdda")
    return c, ("a0", "a1"), "iin 0 a0 pulse(0 300u 0.1n 10p 10p 100p 1)\n"

def ring_B(n=3, wn=4, wp=10, wt=1.5):
    c = ""; P = [f"p{i}" for i in range(n)]; M = [f"q{i}" for i in range(n)]
    for k in range(n):
        ip, im = P[k], M[k]; op, om = (P[k+1], M[k+1]) if k < n-1 else (M[0], P[0])
        c += (m(f"xp1_{k}", om, ip, "vr", "vr", P5, wp) + m(f"xn1_{k}", om, ip, "0", "0", N5, wn) +
              m(f"xp2_{k}", op, im, "vr", "vr", P5, wp) + m(f"xn2_{k}", op, im, "0", "0", N5, wn) +
              m(f"xt1n_{k}", ip, "vr", op, "0", N5, wt) + m(f"xt1p_{k}", ip, "0", op, "vr", P5, 2*wt) +
              m(f"xt2n_{k}", im, "vr", om, "0", N5, wt) + m(f"xt2p_{k}", im, "0", om, "vr", P5, 2*wt))
    for x in P + M: c += buf(x, "vdda")
    return c, ("p0", "q0"), "iin 0 p0 pulse(0 300u 0.1n 10p 10p 100p 1)\n"

def ring_C(n=3, wd=4, wl=4, wt=8):
    c = ""; P = [f"p{i}" for i in range(n)]; M = [f"q{i}" for i in range(n)]
    for k in range(n):
        ip, im = P[k], M[k]; op, om = (P[k+1], M[k+1]) if k < n-1 else (M[0], P[0])
        t = f"t{k}"
        c += (m(f"xi1_{k}", om, ip, t, "0", N5, wd) + m(f"xi2_{k}", op, im, t, "0", N5, wd) +
              m(f"xtl_{k}", t, "vbn", "0", "0", N5, wt) +
              m(f"xd1_{k}", om, om, "vdda", "vdda", P5, wl) + m(f"xc1_{k}", om, "vbp", "vdda", "vdda", P5, wl) +
              m(f"xd2_{k}", op, op, "vdda", "vdda", P5, wl) + m(f"xc2_{k}", op, "vbp", "vdda", "vdda", P5, wl))
    for x in P + M: c += buf(x, "vdda")
    # replica half cell: input device fully on; amplifier sets vbn so that v(rep) = vbp
    c += (m("xri", "rep", "vdda", "rt", "0", N5, wd) + m("xrt", "rt", "vbn", "0", "0", N5, wt) +
          m("xrd", "rep", "rep", "vdda", "vdda", P5, wl) + m("xrc", "rep", "vbp", "vdda", "vdda", P5, wl) +
          "bamp vbn 0 v = max(0.3, min(3.3, 0.9 + 50*(v(rep) - v(vbp))))\ncbn vbn 0 1p\n")
    return c, ("p0", "q0"), "iin 0 p0 pulse(0 300u 0.1n 10p 10p 100p 1)\n"

RINGS = dict(A=lambda: ring_A(), B=lambda: ring_B(), C3=lambda: ring_C(3), C4=lambda: ring_C(4))

def sim(kind, corner, temp, vdda, ctrl, tstop=40e-9):
    body, (o1, o2), kick = RINGS[kind]()
    sup = f"vdda vdda 0 {vdda}\n" + (f"vr vr 0 {ctrl}\n" if kind in ("A", "B") else f"vbp vbp 0 {ctrl}\n")
    iname = "vr" if kind in ("A", "B") else "vdda"
    net = (f"* {kind}\n.lib {LIB} {corner}\n.temp {temp}\n{sup}{body}{kick}.control\noption interp\ntran 2p {tstop}\n"
           f"let vd = v({o1}) - v({o2})\nmeas tran t1 when vd=0 rise=15\nmeas tran t2 when vd=0 rise=35\n"
           f"meas tran ir avg i({iname}) from=15n to={tstop}\nmeas tran ia avg i(vdda) from=15n to={tstop}\n"
           f"meas tran sw pp v({o1}) from=20n to={tstop}\nprint t1 t2 ir ia sw\n.endc\n.end\n")
    with tempfile.TemporaryDirectory() as d:
        os.system(f"cp {SPI} {d}/.spiceinit")
        open(f"{d}/r.sp", "w").write(net)
        o = subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d).stdout
    g = lambda k: (lambda r: float(r.group(1)) if r else None)(re.search(rf"^{k}\s*=\s*(\S+)", o, re.M))
    t1, t2 = g("t1"), g("t2")
    f = 20/(t2 - t1) if t1 and t2 and t2 > t1 else 0.0
    ir, ia, sw = g("ir"), g("ia"), g("sw")
    # supply current of the core: A/B ring current at V_ring is drawn from VDDA by the CCO; C draws from VDDA directly
    icore = abs(ir or 0); iall = abs(ia or 0) + (icore if kind in ("A", "B") else 0)
    return dict(kind=kind, corner=corner, temp=temp, vdda=vdda, ctrl=ctrl, f=f, icore=icore, P=iall*vdda, swing=sw)

def _s(a): return sim(*a)

if __name__ == "__main__":
    jobs = []
    for k in ("A", "B"):
        for v in (1.4, 1.8, 2.2, 2.6, 3.0):
            jobs += [(k, "tt", 27, 3.3, v), (k, "ss", 110, 3.0, v), (k, "ff", -40, 3.6, v)]
    for k in ("C3", "C4"):
        for vbp in (2.4, 2.2, 2.0, 1.8, 1.6, 1.4, 1.2):
            jobs += [(k, "tt", 27, 3.3, vbp), (k, "ss", 110, 3.0, vbp - 0.3), (k, "ff", -40, 3.6, vbp + 0.3)]
    with Pool(2) as p:
        res = p.map(_s, jobs)
    json.dump(res, open(os.path.join(HERE, "hv_vco.json"), "w"), indent=0)
    for r in res:
        print(f"{r['kind']:3} {r['corner']} {r['temp']:4} VDDA {r['vdda']} ctrl {r['ctrl']:.2f}: f {r['f']/1e9:.3f} GHz  "
              f"I_core {r['icore']*1e3:.3f} mA  P {r['P']*1e3:.2f} mW  swing {r['swing'] or 0:.2f} V")
