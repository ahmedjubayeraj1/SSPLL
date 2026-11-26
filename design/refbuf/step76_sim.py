#!/usr/bin/env python3
"""step76_sim.py - verification of the drawn REF receiver (PDK resistors and MIM capacitors, enable, level shifter).
A  bias point over corners x VDDA            (method M10: DC operating point)
B  large-signal transient over amplitude, corner, frequency: delay, duty, edge rate, supply current   (M16)
C  supply sensitivity of the edge time (ps/mV) from VDDA and VDDL steps of 10 mV                       (M16)
D  start-up after pll_en and the disabled state                                                        (M16)
Writes data/step76_sim.json."""
import os, re, json, sys
import numpy as np
from multiprocessing import Pool
import refbuf as R

HERE = os.path.dirname(os.path.abspath(__file__))
CORNERS = [("tt", 27), ("ss", 110), ("ff", -40), ("sf", 27), ("fs", 27)]


def head(corner, temp, vdda, vddl=1.8, en=1.8, ib=2.5e-6):
    en_src = f"ven pll_en 0 {en}" if not isinstance(en, str) else f"ven pll_en 0 {en}"
    return (f"* refbuf full\n.lib {R.LIB} {corner}\n.temp {temp}\n{R.full()}"
            f"vdda VDDA 0 {vdda}\nvddl VDDL 0 {vddl}\nvddd VDDD 0 1.8\niib ib 0 {ib}\n{en_src}\n"
            f"x1 pad0 refclk ib pll_en VDDA VDDL VDDD 0 sspll_refbuf\ncl refclk 0 50f\n")


def op(a):
    corner, temp, vdda = a
    net = head(corner, temp, vdda) + "vsrc pad0 0 dc 0\n.control\nop\nprint v(x1.vin)\nprint v(x1.s1)\nprint vdda#branch\n.endc\n.end\n"
    net = net.replace("vsrc pad0 0 dc 0", f"rs padx pad0 50\nvsrc padx 0 dc {vdda/2}")
    out, _ = R.run(net)
    g = lambda k: float(re.search(rf"{re.escape(k)} = (\S+)", out).group(1))
    return dict(corner=corner, temp=temp, vdda=vdda, vin=g("v(x1.vin)"), s1=g("v(x1.s1)"), idd=-g("vdda#branch"))


def tran(a):
    """a = (corner, temp, vdda, vpp, f, wave, vddl). Edge statistics over the last 5 of 14 cycles."""
    corner, temp, vdda, vpp, f, wave, vddl = a
    T = 1/f; ncyc = 14
    src = (f"vsrc padx 0 sin({vdda/2} {vpp/2} {f})" if wave == "sine" else
           f"vsrc padx 0 pulse({vdda/2 - vpp/2} {vdda/2 + vpp/2} 0 0.5n 0.5n {T/2 - 0.5e-9} {T})")
    b = op((corner, temp, vdda))
    net = head(corner, temp, vdda, vddl) + f"""{src}
rs padx pad0 50
.ic v(x1.vin)={b['vin']} v(x1.s1)={b['s1']}
.control
tran 2p {ncyc*T} 0 2p
wrdata w.txt v(pad0) v(refclk) vdda#branch vddl#branch
.endc
.end
"""
    _, d = R.run(net, ["w.txt"])
    z = d["w.txt"]; t, pad, out, ia, il = z[:, 0], z[:, 1], z[:, 3], -z[:, 5], -z[:, 7]
    t0 = (ncyc - 5)*T; w = t > t0
    tp, _ = R.xings(t, pad, vdda/2, True); to, _ = R.xings(t, out, vddl/2, True); tf, _ = R.xings(t, out, vddl/2, False)
    tp, to, tf = tp[tp > t0], to[to > t0], tf[tf > t0]
    dly = float(np.mean([to[to > x][0] - x for x in tp[:-1]]))
    hi = float(np.mean([tf[tf > x][0] - x for x in to[:-1]]))
    t1, _ = R.xings(t, out, 0.1*vddl, True); t2, _ = R.xings(t, out, 0.9*vddl, True); t1 = t1[t1 > t0]
    tr = float(np.mean([t2[t2 > x][0] - x for x in t1[:-1]]))
    tt = t[w]; avg = lambda y: float(np.trapezoid(y[w], tt)/(tt[-1] - tt[0]))
    return dict(corner=corner, temp=temp, vdda=vdda, vpp=vpp, f=f, wave=wave, vddl=vddl, delay=dly, duty=hi/T,
                trise=tr, ia=avg(ia), il=avg(il), power=vdda*avg(ia) + vddl*avg(il))


def startup(corner="tt", temp=27, vdda=3.3, vpp=1.0, f=50e6):
    """pll_en steps 0 -> 1.8 V at 0.5 us; returns refclk edge times and the input bias waveform (decimated)."""
    T = 1/f; tstop = 25e-6
    net = head(corner, temp, vdda, en="pwl(0 0 0.5u 0 0.501u 1.8)") + f"""vsrc padx 0 sin({vdda/2} {vpp/2} {f})
rs padx pad0 50
.control
tran 20p {tstop} 0 50p
wrdata w.txt v(refclk) v(x1.vin) vdda#branch
.endc
.end
"""
    _, d = R.run(net, ["w.txt"])
    z = d["w.txt"]; t, out, vin, ia = z[:, 0], z[:, 1], z[:, 3], -z[:, 5]
    to, _ = R.xings(t, out, 0.9, True)
    per = np.diff(to)
    good = np.where(np.abs(per - T) < 0.02*T)[0]
    # first edge after which every following period is within 2 % of T
    k0 = next((k for k in range(len(per)) if np.all(np.abs(per[k:] - T) < 0.02*T)), None)
    sel = slice(None, None, max(1, len(t)//3000))
    off = t < 0.5e-6
    return dict(t_first=float(to[0]) if len(to) else None, t_settled=float(to[k0]) if k0 is not None else None,
                idd_off=float(np.mean(ia[off][len(ia[off])//2:])), out_off=float(np.max(out[off][len(out[off])//2:])),
                t=t[sel].tolist(), vin=vin[sel].tolist(), out=out[sel].tolist())


if __name__ == "__main__":
    res = {}
    with Pool(2) as pool:
        res["op"] = pool.map(op, [(c, t, v) for c, t in CORNERS for v in (2.97, 3.3, 3.63)])
        print("A done", flush=True)
        jobs = [("tt", 27, 3.3, v, 50e6, "sine", 1.8) for v in (0.4, 0.7, 1.0, 2.0, 3.3)]
        jobs += [("tt", 27, 3.3, 3.3, 50e6, "square", 1.8)]
        jobs += [(c, t, 3.63, 0.4, 50e6, "sine", 1.8) for c, t in CORNERS[1:]]
        jobs += [(c, t, v, 1.0, 50e6, "sine", 1.8) for c, t in (("ss", 110), ("ff", -40)) for v in (2.97, 3.63)]
        jobs += [("tt", 27, 3.3, 1.0, f, "sine", 1.8) for f in (45e6, 55e6)]
        jobs += [("tt", 27, 3.3, 1.0, 50e6, "sine", 1.71), ("tt", 27, 3.3, 1.0, 50e6, "sine", 1.89)]
        res["tran"] = pool.map(tran, jobs)
        print("B done", flush=True)
        sens = pool.map(tran, [("tt", 27, 3.31, 1.0, 50e6, "sine", 1.8), ("tt", 27, 3.3, 1.0, 50e6, "sine", 1.81),
                               ("tt", 27, 3.31, 3.3, 50e6, "sine", 1.8), ("tt", 27, 3.3, 3.3, 50e6, "sine", 1.81)])
    base = {x["vpp"]: x for x in res["tran"][:5]}
    res["sens"] = dict(vdda_1v=(sens[0]["delay"] - base[1.0]["delay"])/10e-3, vddl_1v=(sens[1]["delay"] - base[1.0]["delay"])/10e-3,
                       vdda_3v3=(sens[2]["delay"] - base[3.3]["delay"])/10e-3, vddl_3v3=(sens[3]["delay"] - base[3.3]["delay"])/10e-3)
    print("C", res["sens"], flush=True)
    res["startup"] = startup()
    print("D", {k: v for k, v in res["startup"].items() if not isinstance(v, list)}, flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "step76_sim.json"), "w"))
