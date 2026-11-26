#!/usr/bin/env python3
"""schematics_hv.py - xschem schematics of the noise-cancellation block (hierarchical, drawing checks) and the LVS
reference:
   sspll_ncb_hv_bank   4-bit switched capacitor bank (transmission gate + nMOS gate capacitor per bit)
   sspll_ncb_hv_sinv   current-starved inverter (pMOS starver on pd, nMOS starver on nb)
   sspll_ncb_hv_line   input inverter, two starved inverters with a bank each, output inverter
   sspll_ncb_hv_bias   vff -> MI -> pMOS mirror (pd) -> nMOS diode (nb)
   sspll_ncb_hv        bias + line
   sspll_ncb_hv_top    four level shifters for the gain code + core
Every analog device is on VDDA / VSSA; the level shifters also have VDDD / VSSD."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
from xsch import Sch, symbol
import ncb_hv as A
_sp = importlib.util.spec_from_file_location("ckg_sch_hv", os.path.join(ROOT, "design", "clkgen", "schematics_hv.py"))
_ck = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_ck)
OUT = os.path.join(ROOT, "xschem", "ncb_hv")
N5, P5 = "nfet3_g5v0d10v5", "pfet3_g5v0d10v5"
LS_PINS = dict(left=[("in", "in")], right=[("out", "out"), ("outb", "out")], top=[("VDDD", "inout"), ("VDDA", "inout")],
               bottom=[("VSSA", "inout"), ("VSSD", "inout")])
CODE = [f"c{k}" for k in range(4)] + [f"c{k}b" for k in range(4)]


def stub(s, pt, name, dx=0, dy=0, flip=0):
    q = (pt[0] + dx, pt[1] + dy)
    s.wire(pt, q); s.label(name, q[0], q[1], flip=flip)


def M(s, name, kind, x, y, dev, body, mult=1, flip=0):
    return s.mos(name, kind, x, y, dev[1], dev[3], dev[2], body=body, mult=mult, flip=flip)


def pins(s, names, x, y0, d="in", flip=0, step=50):
    for k, nm in enumerate(names):
        y = y0 + step*k
        if flip:
            s.pin(nm, d, x, y, flip=1); s.wire((x - 100, y), (x, y)); s.label(nm, x - 100, y)
        else:
            s.pin(nm, d, x, y); s.wire((x, y), (x + 80, y)); s.label(nm, x + 80, y, flip=1)


def bank(p):
    s = Sch("sspll_ncb_hv_bank")
    s.text("sspll_ncb_hv_bank: 4-bit switched capacitor bank on node n. Bit k: transmission gate XSNk / XSPk (on when ck = VDDA, "
           "ckb = 0 V) in series with the nMOS gate capacitor XCk, all 2^k units", 40, -560, 0.3)
    for k in range(p["NB"]):
        x = 400 + 650*k; m = 2**k
        Nn = M(s, f"XSN{k}", N5, x, -200, p["SW"], "VSSA", mult=m)
        Pp = M(s, f"XSP{k}", P5, x + 300, -200, p["SWP"], "VDDA", mult=m, flip=1)
        s.wire(Nn["D"], (Nn["D"][0], -320), (Pp["S"][0], -320), Pp["S"])
        s.wire(Nn["S"], (Nn["S"][0], -80), (Pp["D"][0], -80), Pp["D"])
        stub(s, (Nn["D"][0] + 150, -320), "n", 0, -60)
        stub(s, Nn["G"], f"c{k}", -60); stub(s, Pp["G"], f"c{k}b", 60, flip=1)
        C = M(s, f"XC{k}", N5, x + 150, 100, p["CU"], "VSSA", mult=m)
        s.wire((Nn["S"][0] + 150, -80), (Nn["S"][0] + 150, -40), (C["G"][0] - 60, -40), (C["G"][0] - 60, C["G"][1]), C["G"])
        stub(s, C["D"], "VSSA", 0, -30); stub(s, C["S"], "VSSA", 0, 30)
    pins(s, ["n"] + CODE, 60, 400, "inout")
    pins(s, ["VDDA", "VSSA"], 60, 900, "inout")
    return s


def sinv(p):
    s = Sch("sspll_ncb_hv_sinv")
    xs = p["XS"]
    s.text("sspll_ncb_hv_sinv: current-starved inverter. XSP (gate pd, mirror of the bias) limits the rising edge of o, "
           "XS (gate nb) the falling edge; XP / XN switch", 40, -640, 0.3)
    SP = M(s, "XSP", P5, 400, -420, p["MSP"], "VDDA", mult=p["MSPN"])
    Pp = M(s, "XP", P5, 400, -180, xs[1], "VDDA"); Nn = M(s, "XN", N5, 400, 80, xs[0], "VSSA")
    S_ = M(s, "XS", N5, 400, 320, p["MS"], "VSSA", mult=p["MSN"])
    stub(s, SP["S"], "VDDA", 0, -30); s.wire(SP["D"], Pp["S"]); s.wire(Pp["D"], Nn["D"]); s.wire(Nn["S"], S_["D"])
    stub(s, S_["S"], "VSSA", 0, 30)
    stub(s, SP["G"], "pd", -60); stub(s, S_["G"], "nb", -60)
    s.wire(Pp["G"], (340, Pp["G"][1]), (340, Nn["G"][1]), Nn["G"]); stub(s, (340, -50), "i", -80)
    yo = (Pp["D"][1] + Nn["D"][1])//2
    s.wire((Pp["D"][0], yo), (700, yo)); s.pin("o", "out", 700, yo, flip=1)
    pins(s, ["i", "nb", "pd"], 60, 560)
    pins(s, ["VDDA", "VSSA"], 60, 760, "inout")
    return s


def line(p, SXY, BXY):
    s = Sch("sspll_ncb_hv_line")
    s.text("sspll_ncb_hv_line: input inverter X0 (load on the ring's clock), starved inverters x1 / x2 with a capacitor bank on "
           "each output (a, b), output inverter X3. Each input edge passes two controlled transitions", 40, -560, 0.3)
    X1 = s.sub("sspll_ncb_hv_sinv.sym", SXY, "x1", 800, 0); X2 = s.sub("sspll_ncb_hv_sinv.sym", SXY, "x2", 1900, 0)
    i0, o0 = _ck.inverter(s, "X0", 300, X1["i"][1], p["X0"], "VDDA", thick=True)
    stub(s, i0, "in", -80)
    s.wire(o0, X1["i"])
    for X in (X1, X2):
        stub(s, X["nb"], "nb", -60); stub(s, X["pd"], "pd", -60)
        stub(s, X["VDDA"], "VDDA", 0, -30); stub(s, X["VSSA"], "VSSA", 0, 30)
    xa_, xb_ = 1300, 2400
    Ba = s.sub("sspll_ncb_hv_bank.sym", BXY, "xba", xa_ + 250, 500)
    Bb = s.sub("sspll_ncb_hv_bank.sym", BXY, "xbb", xb_ + 250, 500)
    s.wire(X1["o"], (xa_, X1["o"][1])); s.wire((xa_, X1["o"][1]), (xa_, Ba["n"][1]), Ba["n"])
    s.wire((xa_, X1["o"][1]), (xa_, X2["i"][1]), X2["i"])
    s.label("a", xa_, X1["o"][1], flip=1)
    s.wire(X2["o"], (xb_, X2["o"][1]), (xb_, Bb["n"][1]), Bb["n"])
    s.label("b", xb_, X2["o"][1], flip=1)
    for B in (Ba, Bb):
        for c in CODE:
            stub(s, B[c], c, -60)
        stub(s, B["VDDA"], "VDDA", 0, -30); stub(s, B["VSSA"], "VSSA", 0, 30)
    i3, o3 = _ck.inverter(s, "X3", 2800, X2["o"][1] + 150, p["X3"], "VDDA", thick=True)
    s.wire((xb_, i3[1]), i3)
    s.wire(o3, (3100, o3[1])); s.pin("out", "out", 3100, o3[1], flip=1)
    pins(s, ["in", "nb", "pd"] + CODE, 60, 900)
    pins(s, ["VDDA", "VSSA"], 60, 1500, "inout")
    return s


def bias(p):
    s = Sch("sspll_ncb_hv_bias")
    s.text("sspll_ncb_hv_bias: XI (KI units of the D2S level diode, gate vff) sets the current of the pMOS diode XPD (line pd); "
           "XPO copies it into the nMOS diode XND (line nb). At rest vff = V_GS of the D2S diode: XI is its replica", 40, -560, 0.3)
    PD = M(s, "XPD", P5, 400, -300, p["MPM"], "VDDA"); I_ = M(s, "XI", N5, 400, 100, p["MI"], "VSSA", mult=p["KI"])
    PO = M(s, "XPO", P5, 1000, -300, p["MPM"], "VDDA", flip=1); ND = M(s, "XND", N5, 1000, 100, p["MND"], "VSSA", flip=1)
    for P_ in (PD, PO):
        stub(s, P_["S"], "VDDA", 0, -30)
    stub(s, I_["S"], "VSSA", 0, 30); stub(s, ND["S"], "VSSA", 0, 30)
    s.wire(PD["D"], I_["D"]); s.wire(PO["D"], ND["D"])
    y1 = (PD["D"][1] + I_["D"][1])//2
    s.wire(PD["G"], (PD["G"][0] - 40, PD["G"][1]), (PD["G"][0] - 40, y1), (PD["D"][0], y1))
    stub(s, (PD["G"][0] - 40, PD["G"][1]), "pd", -80); stub(s, PO["G"], "pd", 60, flip=1)
    y2 = (PO["D"][1] + ND["D"][1])//2
    s.wire(ND["G"], (ND["G"][0] + 40, ND["G"][1]), (ND["G"][0] + 40, y2), (ND["D"][0], y2))
    stub(s, (ND["G"][0] + 40, y2), "nb", 80, flip=1)
    stub(s, I_["G"], "vff", -60)
    pins(s, ["vff"], 60, 500); pins(s, ["nb", "pd"], 1500, 500, "out", flip=1)
    pins(s, ["VDDA", "VSSA"], 60, 650, "inout")
    return s


def core(LXY, BIXY):
    s = Sch("sspll_ncb_hv")
    s.text("sspll_ncb_hv: noise-cancellation block. Bias (vff -> pd, nb) and one delay line in -> out; code lines c0-c3 "
           "(VDDA = capacitor in) and their complements c0b-c3b", 40, -460, 0.3)
    B = s.sub("sspll_ncb_hv_bias.sym", BIXY, "xb", 500, 0); L = s.sub("sspll_ncb_hv_line.sym", LXY, "xl", 1400, 0)
    stub(s, B["vff"], "vff", -60); stub(s, B["nb"], "nb", 60, flip=1); stub(s, B["pd"], "pd", 60, flip=1)
    for pin in ["in", "nb", "pd"] + CODE:
        stub(s, L[pin], pin, -60)
    stub(s, L["out"], "out", 60, flip=1)
    for X in (B, L):
        stub(s, X["VDDA"], "VDDA", 0, -30); stub(s, X["VSSA"], "VSSA", 0, 30)
    pins(s, ["in", "vff"] + CODE, 60, 800)
    pins(s, ["out"], 2200, 800, "out", flip=1)
    pins(s, ["VDDA", "VSSA"], 60, 1400, "inout")
    return s


def top(CXY, LS):
    s = Sch("sspll_ncb_hv_top")
    s.text("sspll_ncb_hv_top: NCB with the 4-bit gain code g0-g3 (1.8 V control) shifted to the code lines: out -> ck, "
           "outb -> ckb (g_k = 1: 2^k unit capacitors on each starved node)", 40, -560, 0.3)
    for k in range(4):
        Lk = s.sub("../cco_hv/sspll_ls_1v8_3v3.sym", LS, f"xls{k}", 500, 400*k)
        stub(s, Lk["in"], f"g{k}", -60); stub(s, Lk["out"], f"c{k}", 60, flip=1); stub(s, Lk["outb"], f"c{k}b", 60, flip=1)
        stub(s, Lk["VDDD"], "VDDD", 0, -30); stub(s, Lk["VDDA"], "VDDA", 0, -30, flip=1)
        stub(s, Lk["VSSA"], "VSSA", 0, 30); stub(s, Lk["VSSD"], "VSSD", 0, 30, flip=1)
    C = s.sub("sspll_ncb_hv.sym", CXY, "xa", 1500, 300)
    for pin in ["in", "vff"] + CODE:
        stub(s, C[pin], pin, -60)
    stub(s, C["out"], "out", 60, flip=1)
    stub(s, C["VDDA"], "VDDA", 0, -30); stub(s, C["VSSA"], "VSSA", 0, 30)
    pins(s, ["in", "vff", "g0", "g1", "g2", "g3"], 60, 1900)
    pins(s, ["out"], 2200, 1900, "out", flip=1)
    pins(s, ["VDDA", "VDDD", "VSSA", "VSSD"], 60, 2250, "inout")
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p = A.D
    LS = symbol("/tmp/ls_tmp.sym", "sspll_ls_1v8_3v3", **LS_PINS)
    BXY = symbol(os.path.join(OUT, "sspll_ncb_hv_bank.sym"), "sspll_ncb_hv_bank", left=[("n", "inout")] + [(c, "in") for c in CODE],
                 right=[], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    SXY = symbol(os.path.join(OUT, "sspll_ncb_hv_sinv.sym"), "sspll_ncb_hv_sinv", left=[("i", "in"), ("nb", "in"), ("pd", "in")],
                 right=[("o", "out")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    LXY = symbol(os.path.join(OUT, "sspll_ncb_hv_line.sym"), "sspll_ncb_hv_line",
                 left=[("in", "in"), ("nb", "in"), ("pd", "in")] + [(c, "in") for c in CODE], right=[("out", "out")],
                 top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    BIXY = symbol(os.path.join(OUT, "sspll_ncb_hv_bias.sym"), "sspll_ncb_hv_bias", left=[("vff", "in")],
                  right=[("nb", "out"), ("pd", "out")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    CXY = symbol(os.path.join(OUT, "sspll_ncb_hv.sym"), "sspll_ncb_hv", left=[("in", "in"), ("vff", "in")] + [(c, "in") for c in CODE],
                 right=[("out", "out")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    symbol(os.path.join(OUT, "sspll_ncb_hv_top.sym"), "sspll_ncb_hv_top",
           left=[("in", "in"), ("vff", "in"), ("g0", "in"), ("g1", "in"), ("g2", "in"), ("g3", "in")], right=[("out", "out")],
           top=[("VDDA", "inout"), ("VDDD", "inout")], bottom=[("VSSA", "inout"), ("VSSD", "inout")])
    for name, sch in (("sspll_ncb_hv_bank", bank(p)), ("sspll_ncb_hv_sinv", sinv(p)), ("sspll_ncb_hv_line", line(p, SXY, BXY)),
                      ("sspll_ncb_hv_bias", bias(p)), ("sspll_ncb_hv", core(LXY, BIXY)), ("sspll_ncb_hv_top", top(CXY, LS))):
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        print(name, ":", "\n  ".join(errs) or "drawing check clean")
    open(os.path.join(ROOT, "xschem", "netlist", "ref_ncb_hv.spice"), "w").write(A.lvs_reference())
