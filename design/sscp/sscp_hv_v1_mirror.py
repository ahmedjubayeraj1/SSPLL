"""sscp_hv.py - roadmap step 79: pulsed-Gm charge pump (sub-sampling charge pump), every analog device 5 V-rated
(g5v0d10v5) on VDDA = 3.3 V, the trim decoder in 1.8 V logic.

                 VDDA ──┬───────────────┬──── (one pMOS mirror for all slices: MP1 diode on d1, MP2 output on x)
                       MP1 (diode)     MP2
                        d1              x ──┬── TG_F (ckg / ckgb) ── vctl   (loop filter, step 80)
   slice k (k = 1..5):  │               │   └── TG_D (ckgb / ckg) ── vdump  (held at vctl by the dump buffer)
       v1p ── MN1 ──────┘    MN2 ───────┘
               s1 ── R_S ── s2                (source degeneration: G = 1 / (1/g_m + R_S/2) per slice)
               MT1           MT2              (tail sinks I_T/2 each, mirrored from IBIAS, switched by the trim bits)
   dump buffer: 5 V OTA in unity gain, input vctl, output vdump

What happens: the SSPD's fresh sample v1p - v1m (= 2 A phi) becomes a current G (v1p - v1m) at node x. During the
Gm pulse (ckg, tau ~ 530 ps) x is connected to the loop filter, the rest of the period to the dump node, which the
buffer holds at the loop-filter voltage. The pair and the mirror never switch off, and x never jumps in voltage,
so no turn-on transient and no charge sharing reach the filter. Average current into the filter:
    I = G (2 A phi) tau / T   ->   beta = 2 A G tau / T   (step 50)
The trim (icp_trim, step 73): 00 -> 3 slices, 01 -> 4, 10 -> 2, 11 -> 5.
Every device is (model, W per finger, nf, L)."""
import os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "clkgen")); sys.path.insert(0, os.path.join(ROOT, "design", "sspd"))
import clkgen_hv as K
from clkgen_hv import _m, LIB
import sspd_hv as S
N5, P5 = "nfet_g5v0d10v5", "pfet_g5v0d10v5"

D = dict(
    MN=(N5, 4.0, 1, 1.0),            # input pair (per slice), L = 1 um: flicker
    MT=(N5, 1.0, 1, 4.0),            # tail sink I_T/2 = 2 uA per side per slice (mirror of the 2 uA unit at ib)
    MTS=(N5, 1.0, 1, 0.5),           # tail enable switch
    MP=(P5, 2.0, 1, 4.0),            # mirror pMOS (one unit per slice, all in parallel)
    RS=("res_xhigh_po_0p35", 0.35, 36.0),   # degeneration R_S per slice (~206 kOhm): G = 6.14 uS per slice (step 79 sizing)
    NSEG=1,
    IT=2e-6,                          # tail current per side per slice (I_T/2)
    TGN=(N5, 2.0, 1, 0.5), TGP=(P5, 4.0, 1, 0.5),      # steering TGs
    # dump buffer: nMOS-input 5 V OTA, mirror load, tail 20 uA; unity gain. Resized after the first run (step79hv_buf.py):
    # BN 4/1 + BP 4/2 lost tracking at ss 110 C, 2.97 V, V_cont 2.3 V (-92 mV: V_in,max = VDDA - V_SG(l1) + V_TN); the wider
    # pMOS lowers V_SG, the longer channels raise the gain against the V_DS mismatch of the two input devices:
    # |vdump - vctl| <= 9.4 mV over V_cont 1.3-2.3 V and the corners, peaking <= 1.2 dB, f_3dB >= 167 MHz
    BN=(N5, 8.0, 1, 2.0), BP=(P5, 16.0, 1, 2.0), BT=(N5, 2.0, 1, 4.0), BIT=20e-6,
)
NSL = 5                               # slices
G_TARGET = 18.43e-6                   # three slices: beta 0.790 uA/rad with A 0.812 V/rad, tau 528 ps (steps 73/77/78)


def cells(p=D):
    rm, rw, rl = p["RS"]
    c = f".subckt sspll_sscp_hv_rs a b VSS\n* degeneration resistor: {p['NSEG']} x {rm} L = {rl} um in series\n"
    nodes = ["a"] + [f"n{i}" for i in range(1, p["NSEG"])] + ["b"]
    for i in range(p["NSEG"]):
        c += f"xr{i} {nodes[i]} {nodes[i+1]} VSS sky130_fd_pr__{rm} l={rl} mult=1 m=1\n"
    c += ".ends\n"
    c += (".subckt sspll_sscp_hv_slice v1p v1m d1 x nb en VSS\n"
          "* degenerated pair: drains d1 (mirror diode) and x (output); tails mirrored from nb, enabled by en\n" +
          _m("n1", "d1", "v1p", "s1", "VSS", p["MN"]) + _m("n2", "x", "v1m", "s2", "VSS", p["MN"]) +
          "xrs s1 s2 VSS sspll_sscp_hv_rs\n" +
          _m("t1", "t1", "nb", "VSS", "VSS", p["MT"]) + _m("t2", "t2", "nb", "VSS", "VSS", p["MT"]) +
          _m("e1", "s1", "en", "t1", "VSS", p["MTS"]) + _m("e2", "s2", "en", "t2", "VSS", p["MTS"]) + ".ends\n")
    bn, bp, bt = p["BN"], p["BP"], p["BT"]
    c += (".subckt sspll_sscp_hv_buf inp out nb en VDDA VSS\n* dump buffer: nMOS-input OTA, unity gain (out -> inm)\n" +
          _m("a1", "o1", "inp", "bs", "VSS", bn) + _m("a2", "out", "out", "bs", "VSS", bn) +
          _m("l1", "o1", "o1", "VDDA", "VDDA", bp) + _m("l2", "out", "o1", "VDDA", "VDDA", bp) +
          _m("bt", "bt", "nb", "VSS", "VSS", bt, m=int(round(p["BIT"]/p["IT"]))) +
          _m("be", "bs", "en", "bt", "VSS", p["MTS"], m=int(round(p["BIT"]/p["IT"]))) + ".ends\n")
    tn, tp = p["TGN"], p["TGP"]
    c += (".subckt sspll_sscp_hv_tg a b g gb VDDA VSS\n" + _m("n", "a", "g", "b", "VSS", tn) +
          _m("p", "a", "gb", "b", "VDDA", tp) + ".ends\n")
    c += ".subckt sspll_sscp_hv v1p v1m vctl ckg ckgb ib e1 e2 e3 e4 e5 pll_en VDDA VSS\n"
    c += _m("nb", "ib", "ib", "VSS", "VSS", p["MT"]) + "* bias diode: IBIAS-derived unit current into ib\n"
    for k in range(NSL):
        c += f"xs{k+1} v1p v1m d1 x ib e{k+1} VSS sspll_sscp_hv_slice\n"
    c += _m("p1", "d1", "d1", "VDDA", "VDDA", p["MP"], m=NSL) + _m("p2", "x", "d1", "VDDA", "VDDA", p["MP"], m=NSL)
    c += "xtf x vctl ckg ckgb VDDA VSS sspll_sscp_hv_tg\nxtd x vdump ckgb ckg VDDA VSS sspll_sscp_hv_tg\n"
    c += "xbuf vctl vdump ib pll_en VDDA VSS sspll_sscp_hv_buf\n"
    if p.get("CDUMP"):                                   # decoupling of the dump node (MIM tiles to VSS)
        cm, w, n, l = p["CDUMP"]
        c += f"xcdump vdump VSS sky130_fd_pr__{cm} w={w} l={l} m={n}\n"
    return c + ".ends\n"


def run(net, files=()):
    return S.run(net, files)


def head(p=D, corner="tt", temp=27, vdda=3.3, vc=1.8, en=(1, 1, 1, 0, 0), ckg=3.3, cm=1.66):
    """Static bench: ideal v1p / v1m around cm, vctl held by a source (its current is the output), ckg static."""
    e = "".join(f"ve{k+1} e{k+1} 0 {vdda if b else 0}\n" for k, b in enumerate(en))
    return (f"* sscp hv\n.lib {LIB} {corner}\n.temp {temp}\n{cells(p)}vdda VDDA 0 {vdda}\n"
            f"iib 0 ib {p['IT']}\nvpen pll_en 0 {vdda}\n{e}vckg ckg 0 {ckg}\nvckgb ckgb 0 {vdda - ckg}\n"
            f"vvc vctl 0 {vc}\n"
            "x1 v1p v1m vctl ckg ckgb ib e1 e2 e3 e4 e5 pll_en VDDA 0 sspll_sscp_hv\n")


def dc_transfer(p=D, corner="tt", temp=27, vdda=3.3, vc=1.8, en=(1, 1, 1, 0, 0), cm=1.66, span=0.8):
    """Output current into vctl vs differential input (ckg on): G at 0 V, offset, linear range."""
    net = head(p, corner, temp, vdda, vc, en, 3.3 if True else 0, cm) + (
        f"vd vdif 0 0\nbp v1p 0 v={cm} + v(vdif)/2\nbm v1m 0 v={cm} - v(vdif)/2\n"
        f".control\ndc vd {-span} {span} 0.01\nwrdata w.txt -i(vvc)\n.endc\n.end\n")
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; v, i = z[:, 0], z[:, 1]
    k0 = np.argmin(abs(v)); g = np.gradient(i, v)
    i_os = float(np.interp(0, v, i))
    lin = v[np.abs(g - g[k0]) < 0.1*abs(g[k0])]
    return dict(G=float(g[k0]), i_os=i_os, v_os=float(-i_os/g[k0]), lin=(float(lin.min()), float(lin.max())),
                imax=float(i.max()), imin=float(i.min()), v=v.tolist(), i=i.tolist())


N18, P18 = "nfet_01v8", "pfet_01v8"
DL = dict(INV=((N18, 0.42, 1, 0.15), (P18, 0.84, 1, 0.15)), NAND=((N18, 0.84, 1, 0.15), (P18, 0.84, 1, 0.15)))


def _inv18(nm, a, y):
    n, p = DL["INV"]
    return _m(nm + "n", y, a, "VSS", "VSS", n) + _m(nm + "p", y, a, "VDDD", "VDDD", p)


def _nand18(nm, a, b, y):
    n, p = DL["NAND"]
    return (_m(nm + "na", y, a, nm + "_x", "VSS", n) + _m(nm + "nb", nm + "_x", b, "VSS", "VSS", n) +
            _m(nm + "pa", y, a, "VDDD", "VDDD", p) + _m(nm + "pb", y, b, "VDDD", "VDDD", p))


def full(p=D):
    """Drawn cell with the trim decoder: icp_trim (icp1 icp0) 00 -> 3 slices, 01 -> 4, 10 -> 2, 11 -> 5; pll_en = 0
    turns every slice and the dump buffer off. Decoder in 1.8 V logic on VDDD, four level shifters (step 75 HV) to the
    5 V enable gates. Ports: v1p v1m vctl ckg ckgb ib icp0 icp1 pll_en VDDA VDDD VSS."""
    c = K.CC.LS + cells(p)
    c += ".subckt sspll_sscp_hv_dec icp0 icp1 pll_en e12 e3 e4 e5 VDDD VDDA VSS\n"
    c += "* e12 = en; e3 = en AND NOT(icp1 AND NOT icp0); e4 = en AND icp0; e5 = en AND icp1 AND icp0\n"
    c += _inv18("xi0", "icp0", "c0b") + _nand18("xa", "icp1", "c0b", "a3") + _nand18("xb", "pll_en", "a3", "e3b")
    c += _inv18("xi3", "e3b", "e3l") + _nand18("xc", "pll_en", "icp0", "e4b") + _inv18("xi4", "e4b", "e4l")
    c += _nand18("xd", "icp1", "icp0", "a5b") + _inv18("xi5", "a5b", "a5") + _nand18("xe", "pll_en", "a5", "e5b")
    c += _inv18("xi6", "e5b", "e5l")
    for nm, i in (("e12", "pll_en"), ("e3", "e3l"), ("e4", "e4l"), ("e5", "e5l")):
        c += f"xls{nm} {i} {nm} {nm}_b VDDD VDDA VSS sspll_ls_1v8_3v3\n"
    c += ".ends\n"
    c += ".subckt sspll_sscp_hv_top v1p v1m vctl ckg ckgb ib icp0 icp1 pll_en VDDA VDDD VSS\n"
    c += "xdec icp0 icp1 pll_en e12 e3 e4 e5 VDDD VDDA VSS sspll_sscp_hv_dec\n"
    c += "xgm v1p v1m vctl ckg ckgb ib e12 e12 e3 e4 e5 e12 VDDA VSS sspll_sscp_hv\n.ends\n"
    return c


def lvs_reference(p=D):
    return full(p)
