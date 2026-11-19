"""refbuf_hv.py - roadmap step 76 redone for the device-rule migration: REF_IN receiver in 5 V devices on VDDA, with a
3.3 -> 1.8 V level shifter into the 1.8 V clock generator on VDDD. There is no LDO and no VDDL any more.

 REF_IN ──┬── C_AC (MIM) ── vin ──┬── S1: current-reuse inverter (5 V, header-fed from VDDA) ── s1 ── S2 (5 V, VDDA) ── refhv (s2)
  R_PU/R_PD (pad at VDDA/2)       └── R_B (xhigh-poly, 5 MOhm) ──┘  self-bias: vin DC = s1 DC = trip point
 refhv (0..3.3 V, also an output: the clock generator's sampling edge, step 77 HV) ── LS: 5 V inverter on VDDD (gate takes 3.3 V, output 0..1.8 V) ── s3 ── NOR(s3, enl) on VDDD ── refclk

What changed from the 1.6 GHz design (refbuf.py, kept for the record):
  * the level-shifter inverter and the 1.8 V output NOR were on VDDL (the LDO output); they are now on VDDD, the
    harness 1.8 V digital supply. VDDD is noisier than an LDO output, so the edge's VDDD sensitivity is now measured
    and turned into a VDDD noise requirement (step76hv_supply.py);
  * the pll_en inverter is on VDDD; the enable level shifter is the step-75 HV cell sspll_ls_1v8_3v3;
  * the loop now has N = 16, so reference noise reaches the output with +24 dB instead of +30 dB.
S1, S2, the bias, R_B, C_AC and C_H are unchanged: they were already 5 V devices on VDDA (step 76, 13 Nov)."""
import os, re, sys
import numpy as np
import refbuf as R
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "cco"))
import cco_hv as C
LIB, run, xings, _m = R.LIB, R.run, R.xings, R._m
D, PDK = R.D, R.PDK


def full(p=D, q=PDK):
    """Drawn receiver. Top ports: REF_IN refclk refhv ib pll_en VDDA VDDD VSS."""
    rm, n, L = q["RB_SEG"]
    c = C.LS + ".subckt sspll_refbuf_hv_rb a b VSS\n* R_B: %d segments of %s, L = %g um each\n" % (n, rm, L)
    nodes = ["a"] + [f"n{i}" for i in range(1, n)] + ["b"]
    for i in range(n):
        c += f"xr{i} {nodes[i]} {nodes[i+1]} VSS sky130_fd_pr__{rm} l={L} mult=1 m=1\n"
    c += ".ends\n"
    c += ".subckt sspll_refbuf_hv_s1 vin s1 ib en enb VDDA VSS\n"
    c += "* S1: current-reuse inverter, header = MH units mirrored from the bias diode, C_H decouples the header node\n"
    c += _m("pd", "ib", "ib", "VDDA", "VDDA", p["PD"]) + _m("ph", "vh", "ib", "VDDA", "VDDA", p["PH"], m=p["MH"])
    cm, nt, s = q["CH"]
    c += f"xch vh VDDA sky130_fd_pr__{cm} w={s} l={s} m={nt}\n"
    c += _m("p1", "s1", "vin", "vh", "vh", p["P1"]) + _m("n1", "s1", "vin", "VSS", "VSS", p["N1"])
    c += _m("pen", "ib", "en", "VDDA", "VDDA", q["PEN"]) + _m("ns1", "s1", "enb", "VSS", "VSS", q["NS1"])
    c += ".ends\n"
    # refhv (added in step 77 HV): S2's 0..3.3 V output, the reference edge in the VDDA domain. The clock generator
    # takes the SSPD sampling edge from it, so that edge never passes a VDDD gate (VDDD noise moved it 376 ps/V)
    c += ".subckt sspll_refbuf_hv REF_IN refclk refhv ib pll_en VDDA VDDD VSS\n"
    rm2, _, L2 = q["RPAD"]
    c += f"xrpu VDDA REF_IN VSS sky130_fd_pr__{rm2} l={L2} mult=1 m=1\nxrpd REF_IN VSS VSS sky130_fd_pr__{rm2} l={L2} mult=1 m=1\n"
    cm, nt, s = q["CAC"]
    c += f"xcac vin REF_IN sky130_fd_pr__{cm} w={s} l={s} m={nt}\n"
    c += "xrb vin s1 VSS sspll_refbuf_hv_rb\nxs1 vin s1 ib en enb VDDA VSS sspll_refbuf_hv_s1\n"
    c += "xls pll_en en enb VDDD VDDA VSS sspll_ls_1v8_3v3\n"
    c += _m("p2", "refhv", "s1", "VDDA", "VDDA", p["P2"]) + _m("n2", "refhv", "s1", "VSS", "VSS", p["N2"])
    # 3.3 -> 1.8 V level shift: a 5 V inverter on VDDD. Its gate oxide takes the full 3.3 V swing of s2; its output
    # swings 0..VDDD. (A 1.8 V device cannot take 3.3 V on its gate.)
    c += _m("pl", "s3", "refhv", "VDDD", "VDDD", p["PL"]) + _m("nl", "s3", "refhv", "VSS", "VSS", p["NL"])
    c += _m("pei", "enl", "pll_en", "VDDD", "VDDD", q["PEI"]) + _m("nei", "enl", "pll_en", "VSS", "VSS", q["NEI"])
    # output NOR(s3, enl): refclk = not s3 when enabled, 0 when disabled
    c += _m("pb", "xb", "s3", "VDDD", "VDDD", q["PB2"]) + _m("pb2", "refclk", "enl", "xb", "VDDD", q["PB2"])
    c += _m("nb", "refclk", "s3", "VSS", "VSS", p["NB"]) + _m("nb2", "refclk", "enl", "VSS", "VSS", q["NB2"])
    return c + ".ends\n"


def head(corner="tt", temp=27, vdda="3.3", vddd="1.8", en="1.8", ib=2.5e-6, p=D, cl=50e-15):
    """Netlist head: supplies may be numbers or source expressions (e.g. 'sin(3.3 0.01 1e6)')."""
    return (f"* refbuf HV\n.lib {LIB} {corner}\n.temp {temp}\n{full(p)}vdda VDDA 0 {vdda}\nvddd VDDD 0 {vddd}\n"
            f"iib ib 0 {ib}\nven pll_en 0 {en}\nx1 pad0 refclk refhv ib pll_en VDDA VDDD 0 sspll_refbuf_hv\ncl refclk 0 {cl}\n")


def src(vdda, vpp, f, wave):
    T = 1/f
    if wave == "sine":
        return f"vsrc padx 0 sin({vdda/2} {vpp/2} {f})\nrs padx pad0 50\n"
    return f"vsrc padx 0 pulse({vdda/2 - vpp/2} {vdda/2 + vpp/2} 0 0.5n 0.5n {T/2 - 0.5e-9} {T})\nrs padx pad0 50\n"


def op(corner="tt", temp=27, vdda=3.3, vddd=1.8, p=D):
    net = head(corner, temp, vdda, vddd, p=p) + f"vsrc padx 0 dc {vdda/2}\nrs padx pad0 50\n"
    net += ".control\nop\nprint v(x1.vin)\nprint v(x1.s1)\nprint vdda#branch\nprint vddd#branch\n.endc\n.end\n"
    out, _ = run(net)
    g = lambda k: float(re.search(rf"{re.escape(k)} = (\S+)", out).group(1))
    return dict(vin=g("v(x1.vin)"), s1=g("v(x1.s1)"), ia=-g("vdda#branch"), id=-g("vddd#branch"))


def tran(corner="tt", temp=27, vdda=3.3, vddd=1.8, vpp=1.0, f=50e6, wave="sine", ncyc=14, p=D, ib=2.5e-6):
    """Delay pad -> refclk, duty, 10-90 % rise, supply currents and power over the last 5 of ncyc cycles."""
    T = 1/f; b = op(corner, temp, vdda, vddd, p)
    net = head(corner, temp, vdda, vddd, ib=ib, p=p) + src(vdda, vpp, f, wave)
    net += (f".ic v(x1.vin)={b['vin']} v(x1.s1)={b['s1']}\n.control\ntran 2p {ncyc*T} 0 2p\n"
            f"wrdata w.txt v(pad0) v(refclk) vdda#branch vddd#branch v(x1.s1)\n.endc\n.end\n")
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; t, pad, out, ia, idd, s1 = z[:, 0], z[:, 1], z[:, 3], -z[:, 5], -z[:, 7], z[:, 9]
    t0 = (ncyc - 5)*T; w = t > t0
    tp, _ = xings(t, pad, vdda/2, True); to, _ = xings(t, out, vddd/2, True); tf, _ = xings(t, out, vddd/2, False)
    tp, to, tf = tp[tp > t0], to[to > t0], tf[tf > t0]
    dly = float(np.mean([to[to > x][0] - x for x in tp[:-1]]))
    hi = float(np.mean([tf[tf > x][0] - x for x in to[:-1]]))
    t1, _ = xings(t, out, 0.1*vddd, True); t2, _ = xings(t, out, 0.9*vddd, True); t1 = t1[t1 > t0]
    tr = float(np.mean([t2[t2 > x][0] - x for x in t1[:-1]]))
    tt = t[w]; avg = lambda y: float(np.trapezoid(y[w], tt)/(tt[-1] - tt[0]))
    return dict(corner=corner, temp=temp, vdda=vdda, vddd=vddd, vpp=vpp, f=f, wave=wave, delay=dly, duty=hi/T, trise=tr,
                ia=avg(ia), id=avg(idd), power=vdda*avg(ia) + vddd*avg(idd), vmax=float(out[w].max()), vmin=float(out[w].min()))


def supply_mod(rail="vdda", fm=1e6, amp=10e-3, corner="tt", temp=27, vpp=3.3, wave="square", f=50e6, nper=3, p=D):
    """Supply-to-edge transfer by sinusoidal supply modulation (method M21), differential form.
    Two transients from the same start: rail = V0 + amp*sin(2 pi fm (t - tset)) and rail = V0. The refclk rising-edge
    times of the two runs are subtracted edge by edge, which removes the slow drift of the AC-coupled self-bias after
    the start exactly; the difference is fitted to offset + sinusoid at fm. Returns |dt/dV| (s/V) and its phase.
    The edge is read where refclk crosses VDDD/2 at that instant (the next gate, the clock generator, is on VDDD)."""
    T = 1/f; vdda, vddd = 3.3, 1.8; b = op(corner, temp, vdda, vddd, p)
    tset = 20*T
    tstop = tset + max(nper/fm, 40*T)
    def edges(a):
        mod = lambda v0: f"sin({v0} {a} {fm} {tset})" if a else f"{v0}"
        net = head(corner, temp, mod(vdda) if rail == "vdda" else vdda, mod(vddd) if rail == "vddd" else vddd, p=p)
        net += src(vdda, vpp, f, wave)
        net += (f".ic v(x1.vin)={b['vin']} v(x1.s1)={b['s1']}\n.control\ntran 2p {tstop} 0 5p\n"
                f"wrdata w.txt v(refclk) v(VDDD)\n.endc\n.end\n")
        _, d = run(net, ["w.txt"])
        z = d["w.txt"]
        te, _ = xings(z[:, 0], z[:, 1] - z[:, 3]/2, 0.0, True)
        return te[te > tset]
    t1, t0 = edges(amp), edges(0)
    n = min(len(t1), len(t0)); t1, t0 = t1[:n], t0[:n]
    dt = t1 - t0
    A = np.c_[np.ones_like(t1), np.sin(2*np.pi*fm*(t0 - tset)), np.cos(2*np.pi*fm*(t0 - tset))]
    c, *_ = np.linalg.lstsq(A, dt, rcond=None)
    mag = float(np.hypot(c[1], c[2]))
    return dict(rail=rail, fm=fm, amp=amp, vpp=vpp, wave=wave, k=mag/amp, phase=float(np.degrees(np.arctan2(c[2], c[1]))),
                n=n, resid=float((dt - A @ c).std()), method="differential")


def supply_dc(rail="vdda", dv=10e-3, corner="tt", temp=27, vpp=3.3, wave="square", p=D):
    """Static supply sensitivity: delay change for a +dv step on the rail, each case at its own settled bias."""
    a = tran(corner, temp, vpp=vpp, wave=wave, p=p)
    b = tran(corner, temp, vdda=3.3 + (dv if rail == "vdda" else 0), vddd=1.8 + (dv if rail == "vddd" else 0),
             vpp=vpp, wave=wave, p=p)
    return dict(rail=rail, vpp=vpp, wave=wave, k=(b["delay"] - a["delay"])/dv)


def startup(corner="tt", temp=27, vdda=3.3, vpp=1.0, f=50e6, wave="sine"):
    """pll_en steps 0 -> VDDD at 0.5 us; first edge, the edge after which every period is within 2 % of T,
    supply current and refclk level while disabled."""
    T = 1/f; tstop = 25e-6
    net = head(corner, temp, vdda, 1.8, en="pwl(0 0 0.5u 0 0.501u 1.8)") + src(vdda, vpp, f, wave)
    net += f".control\ntran 20p {tstop} 0 50p\nwrdata w.txt v(refclk) v(x1.vin) vdda#branch vddd#branch\n.endc\n.end\n"
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; t, out, vin, ia, idd = z[:, 0], z[:, 1], z[:, 3], -z[:, 5], -z[:, 7]
    to, _ = xings(t, out, 0.9, True); per = np.diff(to)
    k0 = next((k for k in range(len(per)) if np.all(np.abs(per[k:] - T) < 0.02*T)), None)
    off = (t > 0.25e-6) & (t < 0.5e-6)
    sel = slice(None, None, max(1, len(t)//3000))
    return dict(t_first=float(to[0]) if len(to) else None, t_settled=float(to[k0]) if k0 is not None else None,
                ia_off=float(np.mean(ia[off])), id_off=float(np.mean(idd[off])), out_off=float(np.max(out[off])),
                t=t[sel].tolist(), vin=vin[sel].tolist(), out=out[sel].tolist())


def lvs_reference():
    return full()
