#!/usr/bin/env python3
"""schematics_hv.py - xschem schematics of the diff-to-SE amplifier (hierarchical, drawing checks) and the LVS reference:
   sspll_d2s_hv_rdeg   R_DEG: ND unit resistors in series, a dummy at each end
   sspll_d2s_hv_rl     R_L: NL unit resistors in series, a dummy at each end
   sspll_d2s_hv        bias line, degenerated pMOS pair with split tails, nMOS mirror, R_L to the output-level diode
   sspll_d2s_hv_top    level shifter for ffnc_en + core
Every analog device is on VDDA / VSSA; the level shifter also has VDDD / VSSD."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
from xsch import Sch, symbol
import d2s_hv as A
OUT = os.path.join(ROOT, "xschem", "d2s_hv")
N5, P5 = "nfet3_g5v0d10v5", "pfet3_g5v0d10v5"
LS_PINS = dict(left=[("in", "in")], right=[("out", "out"), ("outb", "out")], top=[("VDDD", "inout"), ("VDDA", "inout")],
               bottom=[("VSSA", "inout"), ("VSSD", "inout")])


def stub(s, pt, name, dx=0, dy=0, flip=0):
    q = (pt[0] + dx, pt[1] + dy)
    s.wire(pt, q); s.label(name, q[0], q[1], flip=flip)


def M(s, name, kind, x, y, dev, body, mult=1, flip=0):
    return s.mos(name, kind, x, y, dev[1], dev[3], dev[2], body=body, mult=mult, flip=flip)


def rstring(cell, n, p, title):
    """n unit resistors drawn as the meander they are in the layout, a dummy unit at each end (all ends on VSSA)."""
    s = Sch(cell)
    rm, rw, rl = p["RU"]
    res = f"sky130_fd_pr/{rm}.sym"
    s.text(f"{cell}: {title} = {n} x {rm} (W {rw} um, L {rl} um, about 20 kOhm each) in series; XRD0 / XRD1: dummies", 40, -370, 0.3)
    xs = [400 + 300*(k + 1) for k in range(n)]
    D0 = s.dev(res, "XRD0", 400, 0, f"L={rl} mult=1 model={rm} spiceprefix=X")
    R = [s.dev(res, f"XR{k}", x, 0, f"L={rl} mult=1 model={rm} spiceprefix=X") for k, x in enumerate(xs)]
    D1 = s.dev(res, "XRD1", xs[-1] + 300, 0, f"L={rl} mult=1 model={rm} spiceprefix=X")
    s.pin("a", "inout", 200, -150); s.wire((200, -150), (xs[0], -150), R[0]["P"])
    for k in range(n - 1):
        if k % 2 == 0:
            s.wire(R[k]["M"], (xs[k], 90), (xs[k + 1], 90), R[k + 1]["M"])
        else:
            s.wire(R[k]["P"], (xs[k], -90), (xs[k + 1], -90), R[k + 1]["P"])
    end = R[-1]["M"] if n % 2 == 1 else R[-1]["P"]
    yb = 150 if n % 2 == 1 else -150
    xe = xs[-1] + 600
    s.wire(end, (xs[-1], yb), (xe, yb)); s.pin("b", "inout", xe, yb, flip=1)
    for D in (D0, D1):
        stub(s, D["P"], "VSSA", 0, -40); stub(s, D["M"], "VSSA", 0, 40); stub(s, D["B"], "VSSA", -60)
    for X in R:
        stub(s, X["B"], "VSSA", -60)
    s.pin("VSSA", "inout", 60, 260); s.wire((60, 260), (140, 260)); s.label("VSSA", 140, 260, flip=1)
    return s


def core(p, DXY, LXY):
    s = Sch("sspll_d2s_hv")
    m, k0, nr = p["MTM"], p["K0"], p["NR"]
    s.text("sspll_d2s_hv: diff-to-SE amplifier. Degenerated pMOS pair XN1 / XN2 (each in its own n-well, body = source), "
           f"R_DEG between the sources, split tails XT1 / XT2 ({m} units each) switched by enb", 40, -1160, 0.3)
    s.text("through XE1 / XE2; nMOS mirror XM1 / XM2 turns the current difference into 2 di at vff; R_L from vff to r, "
           "the nMOS diode XR fed by XRP: vff = V_GS(XR) + G (inp - inm). Bias line pg: XPD diode fed by XK from ib", 40, -1120, 0.3)
    X1, X2, XB, XO = 800, 1500, 250, 2200
    # bias column
    PD = M(s, "XPD", P5, XB, -820, p["MP"], "VDDA", mult=k0); PDS = M(s, "XPDS", P5, XB, -600, p["MPS"], "VDDA", mult=k0)
    stub(s, PD["S"], "VDDA", 0, -30); s.wire(PD["D"], PDS["S"]); stub(s, PDS["G"], "VSSA", -60)
    K_ = M(s, "XK", N5, XB, -300, p["MT"], "VSSA", mult=k0)
    s.wire(PDS["D"], K_["D"])
    pgp = (PDS["D"][0], (PDS["D"][1] + K_["D"][1])//2)
    s.wire(PD["G"], (PD["G"][0] - 40, PD["G"][1]), (PD["G"][0] - 40, pgp[1]), pgp)
    stub(s, (pgp[0], pgp[1] + 40), "pg", 100, 0, flip=1)
    stub(s, K_["G"], "ib", -60); stub(s, K_["S"], "VSSA", 0, 30)
    B_ = M(s, "XB", N5, XB, 200, p["MT"], "VSSA")
    s.wire(B_["G"], (B_["G"][0] - 40, B_["G"][1]), (B_["G"][0] - 40, B_["D"][1] - 40), (B_["D"][0], B_["D"][1] - 40), B_["D"])
    stub(s, (B_["D"][0], B_["D"][1] - 40), "ib", 0, -40); stub(s, B_["S"], "VSSA", 0, 30)
    if p["NCF"]:
        CF = M(s, "XCF", P5, XB, 600, p["CF"], "VDDA", mult=p["NCF"])
        stub(s, CF["G"], "pg", -60); stub(s, CF["S"], "VDDA", 0, -30); stub(s, CF["D"], "VDDA", 0, 30)
    # pair column
    T1 = M(s, "XT1", P5, X1, -820, p["MP"], "VDDA", mult=m); T2 = M(s, "XT2", P5, X2, -820, p["MP"], "VDDA", mult=m, flip=1)
    E1 = M(s, "XE1", P5, X1, -600, p["MPS"], "VDDA", mult=m); E2 = M(s, "XE2", P5, X2, -600, p["MPS"], "VDDA", mult=m, flip=1)
    for T, E, sd in ((T1, E1, -1), (T2, E2, 1)):
        stub(s, T["S"], "VDDA", 0, -30); s.wire(T["D"], E["S"])
        stub(s, T["G"], "pg", 60*sd, flip=int(sd > 0)); stub(s, E["G"], "enb", 60*sd, flip=int(sd > 0))
    N1 = M(s, "XN1", P5, X1, -180, p["MN"], "s1"); N2 = M(s, "XN2", P5, X2, -180, p["MN"], "s2", flip=1)
    ys = -400
    R = s.sub("sspll_d2s_hv_rdeg.sym", DXY, "xrdeg", (X1 + X2)//2 - 60, ys - 60)
    s.wire(E1["D"], (E1["D"][0], ys), N1["S"]); s.wire(E2["D"], (E2["D"][0], ys), N2["S"])
    s.wire((N1["S"][0], ys), (R["a"][0] - 40, ys), (R["a"][0] - 40, R["a"][1]), R["a"])
    s.wire((N2["S"][0], ys), (R["b"][0] + 40, ys), (R["b"][0] + 40, R["b"][1]), R["b"])
    stub(s, R["VSSA"], "VSSA", 0, 30)
    stub(s, (N1["S"][0], ys + 50), "s1", -60); stub(s, (N2["S"][0], ys + 50), "s2", 60, flip=1)   # the n-wells' net
    stub(s, N1["G"], "inp", -60); stub(s, N2["G"], "inm", 60, flip=1)
    M1 = M(s, "XM1", N5, X1, 300, p["MNM"], "VSSA"); M2 = M(s, "XM2", N5, X2, 300, p["MNM"], "VSSA", flip=1)
    s.wire(N1["D"], M1["D"]); s.wire(N2["D"], M2["D"])
    yd = (N1["D"][1] + M1["D"][1])//2
    s.wire(M1["G"], (M1["G"][0] - 40, M1["G"][1]), (M1["G"][0] - 40, yd), (M1["D"][0], yd))
    stub(s, (M1["G"][0] - 40, yd), "d1", -60)
    stub(s, M2["G"], "d1", 60, flip=1)
    stub(s, M1["S"], "VSSA", 0, 30); stub(s, M2["S"], "VSSA", 0, 30)
    # output level column
    RP = M(s, "XRP", P5, XO, -820, p["MP"], "VDDA", mult=nr); RS = M(s, "XRS", P5, XO, -600, p["MPS"], "VDDA", mult=nr)
    stub(s, RP["S"], "VDDA", 0, -30); s.wire(RP["D"], RS["S"]); stub(s, RP["G"], "pg", -60); stub(s, RS["G"], "VSSA", -60)
    MR = M(s, "XR", N5, XO, 300, p["MR"], "VSSA")
    s.wire(RS["D"], MR["D"])
    yr = (RS["D"][1] + MR["D"][1])//2 + 160
    s.wire(MR["G"], (MR["G"][0] - 40, MR["G"][1]), (MR["G"][0] - 40, yr), (MR["D"][0], yr))
    stub(s, MR["S"], "VSSA", 0, 30)
    L_ = s.sub("sspll_d2s_hv_rl.sym", LXY, "xrl", (X2 + XO)//2 - 40, -60)
    s.wire((M2["D"][0], yd), (L_["a"][0] - 60, yd), (L_["a"][0] - 60, L_["a"][1]), L_["a"])
    s.wire(L_["b"], (MR["D"][0], L_["b"][1]))
    stub(s, L_["VSSA"], "VSSA", 0, 30)
    s.wire((L_["a"][0] - 60, yd), (L_["a"][0] - 60, 620), (XO + 500, 620)); s.pin("vff", "out", XO + 500, 620, flip=1)
    for k, nm in enumerate(("inp", "inm", "ib", "enb")):
        y = 900 + 50*k
        s.pin(nm, "in" if nm != "ib" else "inout", 60, y); s.wire((60, y), (140, y)); s.label(nm, 140, y, flip=1)
    s.pin("VDDA", "inout", 60, -1060); s.wire((60, -1060), (140, -1060)); s.label("VDDA", 140, -1060, flip=1)
    s.pin("VSSA", "inout", 60, 1250); s.wire((60, 1250), (140, 1250)); s.label("VSSA", 140, 1250, flip=1)
    return s


def top(CXY, LS):
    s = Sch("sspll_d2s_hv_top")
    s.text("sspll_d2s_hv_top: diff-to-SE amplifier with the ffnc_en level shifter (1.8 V control -> 3.3 V en / en_b). "
           "inp = v2m, inm = v2p: vff = V_0 - G (v2p - v2m)", 40, -460, 0.3)
    L = s.sub("../cco_hv/sspll_ls_1v8_3v3.sym", LS, "xls", 500, 0)
    C = s.sub("sspll_d2s_hv.sym", CXY, "xa", 1300, 0)
    stub(s, L["in"], "ffnc_en", -60); stub(s, L["out"], "en", 60, flip=1); stub(s, L["outb"], "en_b", 60, flip=1)
    for pin, net in (("inp", "v2m"), ("inm", "v2p"), ("ib", "ib"), ("enb", "en_b")):
        stub(s, C[pin], net, -60)
    stub(s, C["vff"], "vff", 60, flip=1)
    for X, sup, gnd in ((L, ("VDDD", "VDDA"), ("VSSA", "VSSD")), (C, ("VDDA",), ("VSSA",))):
        for k, nm in enumerate(sup):
            stub(s, X[nm], nm, 0, -30, flip=k)
        for k, nm in enumerate(gnd):
            stub(s, X[nm], nm, 0, 30, flip=k)
    for k, (nm, d) in enumerate((("v2p", "in"), ("v2m", "in"), ("ib", "inout"), ("ffnc_en", "in"))):
        y = 600 + 50*k
        s.pin(nm, d, 60, y); s.wire((60, y), (140, y)); s.label(nm, 140, y, flip=1)
    s.pin("vff", "out", 2000, 600, flip=1); s.wire((1900, 600), (2000, 600)); s.label("vff", 1900, 600)
    for k, nm in enumerate(("VDDA", "VDDD")):
        s.pin(nm, "inout", 60, -350 + 50*k); s.wire((60, -350 + 50*k), (140, -350 + 50*k)); s.label(nm, 140, -350 + 50*k, flip=1)
    for k, nm in enumerate(("VSSA", "VSSD")):
        s.pin(nm, "inout", 60, 1000 + 50*k); s.wire((60, 1000 + 50*k), (140, 1000 + 50*k)); s.label(nm, 140, 1000 + 50*k, flip=1)
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p = A.D
    LS = symbol("/tmp/ls_tmp.sym", "sspll_ls_1v8_3v3", **LS_PINS)
    DXY = symbol(os.path.join(OUT, "sspll_d2s_hv_rdeg.sym"), "sspll_d2s_hv_rdeg", left=[("a", "inout")], right=[("b", "inout")],
                 bottom=[("VSSA", "inout")])
    LXY = symbol(os.path.join(OUT, "sspll_d2s_hv_rl.sym"), "sspll_d2s_hv_rl", left=[("a", "inout")], right=[("b", "inout")],
                 bottom=[("VSSA", "inout")])
    CXY = symbol(os.path.join(OUT, "sspll_d2s_hv.sym"), "sspll_d2s_hv",
                 left=[("inp", "in"), ("inm", "in"), ("ib", "inout"), ("enb", "in")], right=[("vff", "out")],
                 top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    symbol(os.path.join(OUT, "sspll_d2s_hv_top.sym"), "sspll_d2s_hv_top",
           left=[("v2p", "in"), ("v2m", "in"), ("ib", "inout"), ("ffnc_en", "in")], right=[("vff", "out")],
           top=[("VDDA", "inout"), ("VDDD", "inout")], bottom=[("VSSA", "inout"), ("VSSD", "inout")])
    for name, sch in (("sspll_d2s_hv_rdeg", rstring("sspll_d2s_hv_rdeg", p["ND"], p, "R_DEG")),
                      ("sspll_d2s_hv_rl", rstring("sspll_d2s_hv_rl", p["NL"], p, "R_L")),
                      ("sspll_d2s_hv", core(p, DXY, LXY)), ("sspll_d2s_hv_top", top(CXY, LS))):
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        print(name, ":", "\n  ".join(errs) or "drawing check clean")
    open(os.path.join(ROOT, "xschem", "netlist", "ref_d2s_hv.spice"), "w").write(A.lvs_reference())
