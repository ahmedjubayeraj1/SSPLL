#!/usr/bin/env python3
"""d2s_hv.py - differential-to-single-ended amplifier (D2S) between the SSPD hold output and the noise-cancellation
block (NCB). Every analog device is 5 V-rated (g5v0d10v5) on VDDA = 3.3 V, ground VSSA; the enable comes from the
1.8 V control through one level shifter.

            VDDA ───┬──────────────┬─────────────────────────┬───────────────┐
                   MP1 (diode)    MP2                       MPD (diode)     MP0 (N0 units, gate pg)
                    d1 ───────────┤gate                      pd ── R_F ── pg ┤ (C_F from pg to VDDA)
                    │             vff ◄───────────────────────────────────────┘
          inp ── MN1             MN2 ── inm                  │
                    s1 ── R_DEG ── s2                        MK (K0 units, gate ib)
                    MT1 (en)      MT2 (en)                   │
                    │             │         vff ── R_L ── VSSA
            VSSA ───┴─────────────┴───────────────────────────────────────────── (ib: bias diode MB, 2 uA unit)

What happens: the degenerated pair turns v_id = inp - inm into a current difference +-di = v_id / (R_DEG + 2/g_m);
the pMOS mirror copies MN1's current to vff, where MN2 takes its own, so 2 di flows into R_L:
    vff = V_0 + G (inp - inm),   G = 2 R_L / (R_DEG + 2/g_m),   V_0 = I_0 R_L
R_L and R_DEG are made of the same unit resistor (ratio), so G hardly moves with process, temperature or VDDA.
I_0 (N0 pMOS units fed by the K0-unit pMOS diode, its gate low-pass filtered by R_F C_F) sets the output level.
At the top level inp = v2m, inm = v2p, so vff = V_0 - G (v2p - v2m): at lock (v2p - v2m < 0) vff sits above V_0,
where MN2 has the most headroom. en_b = 1 (ffnc_en = 0) turns the tails off: vff = V_0, i.e. FFNC off at the same NCB operating point.
Every device is (model, W per finger, nf, L)."""
import os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "clkgen"))
import clkgen_hv as K
from clkgen_hv import _m, LIB
N5, P5 = "nfet_g5v0d10v5", "pfet_g5v0d10v5"

D = dict(
    MN=(P5, 8.0, 1, 1.0),            # input pair (pMOS, own n-well tied to the source: no body effect); L = 1 um: flicker
    MP=(P5, 16.0, 1, 2.0),           # pMOS bias unit (2 uA, weak inversion: low V_SD,sat for the tails at ss -40 C)
    MPR=(P5, 8.0, 1, 1.0),           # level-source unit: same W/L as MP at half the area (less drain capacitance on r)
    MPS=(P5, 2.0, 1, 0.5),           # pMOS tail switch (gate enb), one per unit; always-on copy in the bias diode
    MTM=4,                           # tail units per side: I_T = 8 uA (gain raised to 1.5 for the NCB, see the doc)
    K0=2,                            # pMOS bias diode units (fed by K0 nMOS units from ib)
    MT=(N5, 1.0, 1, 8.0),            # nMOS unit at ib (2 uA, the Gm design's quiet unit)
    MNM=(N5, 2.0, 1, 2.0),           # nMOS mirror (diode + output), 6 uA each: short enough for a fast mirror pole
    MR=(N5, 2.0, 1, 1.0), NR=7,      # output-level diode: nMOS fed by NR level-source units (~22 uA): vff rests at its V_GS (1.23 V)
    RU=("res_xhigh_po_0p69", 0.69, 6.76),   # unit resistor (~20 kOhm); R_L = NL units, R_DEG = ND units, in series
    NL=2, ND=2, NDUM=1,              # R_L = 2 units, R_DEG = 2 units; a dummy unit at each end of each string
    CF=(P5, 10.0, 1, 10.0), NCF=0,   # optional bias-line capacitor (pMOS gate cap, pg to VDDA)
    CR=(N5, 10.0, 1, 10.0), NCR=0,   # optional decoupling of r (rejected: it removes the 1/g_m(MR) part of G above ~30 MHz)
    IT=2e-6,                         # unit current (the bias input ib)
)


def _rstr(name, a, b, n, p=D, ndum=None):
    """n unit resistors in series from a to b, plus ndum dummy units (both ends on VSSA) at each end."""
    rm, rw, rl = p["RU"]; ndum = p["NDUM"] if ndum is None else ndum
    nodes = [a] + [f"{name}_{i}" for i in range(1, n)] + [b]
    c = "".join(f"x{name}{i} {nodes[i]} {nodes[i+1]} VSSA sky130_fd_pr__{rm} l={rl} mult=1 m=1\n" for i in range(n))
    c += "".join(f"x{name}d{i} VSSA VSSA VSSA sky130_fd_pr__{rm} l={rl} mult=1 m=1\n" for i in range(2*ndum))
    return c


def cells(p=D):
    m, k0, nr = p["MTM"], p["K0"], p["NR"]
    c = (".subckt sspll_d2s_hv_rdeg a b VSSA\n* R_DEG: unit resistors in series, a dummy unit at each end\n" +
         _rstr("r", "a", "b", p["ND"], p) + ".ends\n" +
         ".subckt sspll_d2s_hv_rl a b VSSA\n* R_L: unit resistors in series, a dummy unit at each end\n" +
         _rstr("r", "a", "b", p["NL"], p) + ".ends\n")
    c += (".subckt sspll_d2s_hv inp inm vff ib enb VDDA VSSA\n"
          "* diff-to-SE amplifier: vff = V_GS(MR) + 2 R_L / (R_DEG + 2/g_m) (inp - inm); en = 0: tails off, vff = V_GS(MR)\n"
          "* bias: unit nMOS diode at ib; K0 units sink from the pMOS diode (bias line pg)\n" +
          _m("b", "ib", "ib", "VSSA", "VSSA", p["MT"]) + _m("k", "pg", "ib", "VSSA", "VSSA", p["MT"], m=k0) +
          _m("pds", "pg", "VSSA", "pq", "VDDA", p["MPS"], m=k0) + _m("pd", "pq", "pg", "VDDA", "VDDA", p["MP"], m=k0) +
          (_m("cf", "VDDA", "pg", "VDDA", "VDDA", p["CF"], m=p["NCF"]) if p["NCF"] else "") +
          "* degenerated pMOS pair (body = source), split tails (MTM units each, switch enb)\n" +
          _m("n1", "d1", "inp", "s1", "s1", p["MN"]) + _m("n2", "vff", "inm", "s2", "s2", p["MN"]) +
          "xrdeg s1 s2 VSSA sspll_d2s_hv_rdeg\n" +
          _m("e1", "s1", "enb", "t1", "VDDA", p["MPS"], m=m) + _m("t1", "t1", "pg", "VDDA", "VDDA", p["MP"], m=m) +
          _m("e2", "s2", "enb", "t2", "VDDA", p["MPS"], m=m) + _m("t2", "t2", "pg", "VDDA", "VDDA", p["MP"], m=m) +
          "* nMOS mirror: MN1's current to vff\n" +
          _m("m1", "d1", "d1", "VSSA", "VSSA", p["MNM"]) + _m("m2", "vff", "d1", "VSSA", "VSSA", p["MNM"]) +
          "* load R_L from vff to the output-level node r: nMOS diode MR fed by NR pMOS units\n" +
          "xrl vff r VSSA sspll_d2s_hv_rl\n" +
          _m("rs", "r", "VSSA", "rq", "VDDA", p["MPS"], m=nr) + _m("rp", "rq", "pg", "VDDA", "VDDA", p["MPR"] or p["MP"], m=nr) +
          _m("r", "r", "r", "VSSA", "VSSA", p["MR"]) +
          (_m("cr", "VSSA", "r", "VSSA", "VSSA", p["CR"], m=p["NCR"]) if p["NCR"] else "") +
          ".ends\n")
    return c


def full(p=D):
    """Drawn cell: the core plus the level shifter for ffnc_en (1.8 V control). Ports: v2p v2m vff ib ffnc_en
    VDDA VDDD VSSA VSSD. inp = v2m, inm = v2p (vff rises when the ring is late, see the module text)."""
    c = K.CC.LS + cells(p)
    c += (".subckt sspll_d2s_hv_top v2p v2m vff ib ffnc_en VDDA VDDD VSSA VSSD\n"
          "xls ffnc_en en en_b VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\n"
          "xa v2m v2p vff ib en_b VDDA VSSA sspll_d2s_hv\n.ends\n")
    return c


def lvs_reference(p=D):
    return full(p)


def run(net, files=(), timeout=6000):
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as d:
        K.C.spinit(d)
        open(os.path.join(d, "r.sp"), "w").write(net)
        r = subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d, timeout=timeout)
        data = {f: np.loadtxt(os.path.join(d, f)) for f in files if os.path.exists(os.path.join(d, f))}
    return r.stdout + r.stderr, data


def head(p=D, corner="tt", temp=27, vdda=3.3, en=True, ib=None, cl=40e-15, title="d2s"):
    """Core with ideal sources: VDDA, ib (2 uA unit into the diode), en, a load C_L on vff (the NCB input)."""
    ib = p["IT"] if ib is None else ib
    return (f"* {title}\n.lib {LIB} {corner}\n.temp {temp}\n{cells(p)}vdda VDDA 0 {vdda}\n"
            f"iib VDDA ib {ib}\nvenb enb 0 {0 if en else vdda}\ncl vff 0 {cl}\n"
            "xa inp inm vff ib enb VDDA 0 sspll_d2s_hv\n")


def dc_transfer(p=D, corner="tt", temp=27, vdda=3.3, cm=1.66, span=0.5, en=True, ib=None):
    """vff vs v_id = inp - inm around cm: V_0, G at 0, G over the operating window, linear range."""
    net = head(p, corner, temp, vdda, en, ib) + (
        f"vd vdif 0 0\nbp inp 0 v={cm} + v(vdif)/2\nbm inm 0 v={cm} - v(vdif)/2\n"
        f".control\noption gmin=1e-15\ndc vd {-span} {span} 0.005\nwrdata w.txt v(vff) i(vdda)\n.endc\n.end\n")
    out, d = run(net, ["w.txt"])
    z = d["w.txt"]; v, y, ida = z[:, 0], z[:, 1], z[:, 3]
    g = np.gradient(y, v); k0 = np.argmin(abs(v))
    lin = v[np.abs(g - g[k0]) < 0.1*abs(g[k0])] if abs(g[k0]) > 1e-3 else np.array([0.0])
    return dict(v=v, y=y, g=g, V0=float(y[k0]), G=float(g[k0]), lin=(float(lin.min()), float(lin.max())),
                I=float(-ida[k0]), P=float(-ida[k0]*vdda))


if __name__ == "__main__":
    for cm in (1.45, 1.66, 1.9):
        r = dc_transfer(cm=cm)
        print(f"cm {cm}: V0 {r['V0']:.3f} G {r['G']:.3f} lin {r['lin']} I {r['I']*1e6:.1f} uA")


def ac(p=D, corner="tt", temp=27, vdda=3.3, cm=1.66, vid=0.0, cl=40e-15, ib=None):
    """Small-signal: differential gain G(f) (v_id = 1 split +-1/2), f_3dB; input capacitance of each input at 1 MHz
    (one input driven, the other held; C = Im(I)/(2 pi f)), including the Miller part from vff."""
    out = {}
    net = head(p, corner, temp, vdda, True, ib, cl) + (
        f"vp inp 0 dc {cm + vid/2} ac 0.5\nvm inm 0 dc {cm - vid/2} ac -0.5\n"
        f".control\nac dec 40 1e5 1e10\nlet gr = real(v(vff))\nlet gi = imag(v(vff))\nwrdata w.txt gr gi\n.endc\n.end\n")
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; f = z[:, 0]; g = z[:, 1] + 1j*z[:, 3]
    mag = abs(g); g0 = mag[0]
    k = np.where(mag < g0/np.sqrt(2))[0]
    out.update(f=f, Gf=g, G0=float(g0), f3=float(f[k[0]]) if len(k) else float("nan"),
               ph_6M=float(np.degrees(np.angle(np.interp(6.4e6, f, g.real) + 1j*np.interp(6.4e6, f, g.imag)))))
    for side, a, b in (("inp", "ac 1", "ac 0"), ("inm", "ac 0", "ac 1")):
        net = head(p, corner, temp, vdda, True, ib, cl) + (
            f"vp inp 0 dc {cm + vid/2} {a}\nvm inm 0 dc {cm - vid/2} {b}\n"
            f".control\nac lin 1 1e6 1e6\nlet ii = imag(i(v{'p' if side == 'inp' else 'm'}))\nwrdata c.txt ii\n.endc\n.end\n")
        _, d = run(net, ["c.txt"])
        out["cin_" + side] = float(abs(np.atleast_2d(d["c.txt"])[0, 1])/(2*np.pi*1e6))
    return out
