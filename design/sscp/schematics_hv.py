#!/usr/bin/env python3
"""schematics_hv.py - step 79: xschem schematics of the 5 V pulsed-Gm charge pump (hierarchical, drawing checks) and the
LVS reference:
   sspll_sscp_hv_rs     degeneration resistor
   sspll_sscp_hv_slice  degenerated input pair with switched tail sinks (one Gm unit)
   sspll_sscp_hv_buf    dump buffer (5 V OTA, unity gain)
   sspll_sscp_hv_tg     steering transmission gate
   sspll_sscp_hv        five slices (no mirror), replica pMOS bias, steering TGs, dump buffer, bias diode
   sspll_sscp_hv_dec    icp_trim decoder (1.8 V, VDDD) + four level shifters
   sspll_sscp_hv_top    decoder + core
Short labelled stubs join nets inside a cell where a drawn wire would cross devices; every device terminal is wired.
Ground split (24 Nov 2026): the Gm core cells are on VSSA; the decoder's 1.8 V gates on VSSD; the level shifters, the
decoder cell and the top cell have both grounds."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
from xsch import Sch, symbol
import sscp_hv as C
import importlib.util
_sp = importlib.util.spec_from_file_location("ckg_sch_hv", os.path.join(ROOT, "design", "clkgen", "schematics_hv.py"))
_ck = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_ck)
OUT = os.path.join(ROOT, "xschem", "sscp_hv")
N5, P5, N18, P18 = "nfet3_g5v0d10v5", "pfet3_g5v0d10v5", "nfet3_01v8", "pfet3_01v8"
RES = "sky130_fd_pr/res_xhigh_po_0p35.sym"
LS_PINS = dict(left=[("in", "in")], right=[("out", "out"), ("outb", "out")], top=[("VDDD", "inout"), ("VDDA", "inout")],
               bottom=[("VSSA", "inout"), ("VSSD", "inout")])


def stub(s, pt, name, dx=0, dy=0, flip=0):
    q = (pt[0] + dx, pt[1] + dy)
    s.wire(pt, q); s.label(name, q[0], q[1], flip=flip)


def M(s, name, kind, x, y, dev, body, mult=1, flip=0):
    return s.mos(name, kind, x, y, dev[1], dev[3], dev[2], body=body, mult=mult, flip=flip)


def supplies(s, names, y0, ybot):
    for k, nm in enumerate(names):
        y = y0 + 50*k
        s.pin(nm, "inout", 60, y); s.wire((60, y), (140, y)); s.label(nm, 140, y, flip=1)
    s.pin("VSSA", "inout", 60, ybot); s.wire((60, ybot), (140, ybot)); s.label("VSSA", 140, ybot, flip=1)


def rs(p):
    s = Sch("sspll_sscp_hv_rs")
    rm, rw, rl = p["RS"]
    s.text(f"sspll_sscp_hv_rs: source-degeneration resistor, {rm}, L = {rl} um (about {2000*rl/0.35/1e3:.0f} kOhm); body to VSS", 40, -300, 0.3)
    R = s.dev(RES, "XR0", 400, 0, f"L={rl} mult=1 model={rm} spiceprefix=X")
    s.pin("a", "inout", 200, -120); s.wire((200, -120), (400, -120), R["P"])
    s.pin("b", "inout", 200, 120); s.wire((200, 120), (400, 120), R["M"])
    stub(s, R["B"], "VSSA", -60)
    s.pin("VSSA", "inout", 60, 220); s.wire((60, 220), (140, 220)); s.label("VSSA", 140, 220, flip=1)
    return s


def slice_(p, RXY):
    s = Sch("sspll_sscp_hv_slice")
    m = p["MTM"]
    s.text("sspll_sscp_hv_slice: one Gm unit. Degenerated nMOS pair XN1/XN2 (R_S between the sources); tail sinks XT1/XT2 "
           f"({m} units each) mirrored from nb, switched by en through XE1/XE2; each drain has its own pMOS source", 40, -820, 0.3)
    s.text("XPC/XPX (biased by pb, switched by enb through XPE1/XPE2) equal to its tail: x = I(XPX) - I(XN2) is the output, "
           "xc = I(XPC) - I(XN1) goes to the dump node. No mirror: nothing slow in the signal path", 40, -780, 0.3)
    PE1 = M(s, "XPE1", P5, 400, -620, p["MPE"], "VDDA", mult=m); PE2 = M(s, "XPE2", P5, 1000, -620, p["MPE"], "VDDA", mult=m, flip=1)
    PC = M(s, "XPC", P5, 400, -400, p["MP"], "VDDA", mult=m); PX = M(s, "XPX", P5, 1000, -400, p["MP"], "VDDA", mult=m, flip=1)
    stub(s, PE1["S"], "VDDA", 0, -30); stub(s, PE2["S"], "VDDA", 0, -30)
    s.wire(PE1["D"], PC["S"]); s.wire(PE2["D"], PX["S"])
    stub(s, PE1["G"], "enb", -60); stub(s, PE2["G"], "enb", 60, flip=1)
    stub(s, PC["G"], "pb", -60); stub(s, PX["G"], "pb", 60, flip=1)
    N1 = M(s, "XN1", N5, 400, -120, p["MN"], "VSSA"); N2 = M(s, "XN2", N5, 1000, -120, p["MN"], "VSSA", flip=1)
    s.wire(PC["D"], N1["D"]); s.wire(PX["D"], N2["D"])
    xc_pt = (PC["D"][0], (PC["D"][1] + N1["D"][1])//2); x_pt = (PX["D"][0], (PX["D"][1] + N2["D"][1])//2)
    stub(s, xc_pt, "xc", -80); stub(s, x_pt, "x", 80, flip=1)
    stub(s, N1["G"], "v1p", -60); stub(s, N2["G"], "v1m", 60, flip=1)
    R = s.sub("sspll_sscp_hv_rs.sym", RXY, "xrs", 700, 60)
    s.wire(N1["S"], (N1["S"][0], R["a"][1]), R["a"]); s.wire(N2["S"], (N2["S"][0], R["b"][1]), R["b"])
    stub(s, R["VSSA"], "VSSA", 0, 30)
    E1 = M(s, "XE1", N5, 400, 260, p["MTS"], "VSSA", mult=m); E2 = M(s, "XE2", N5, 1000, 260, p["MTS"], "VSSA", mult=m, flip=1)
    s.wire((N1["S"][0], R["a"][1]), E1["D"]); s.wire((N2["S"][0], R["b"][1]), E2["D"])
    stub(s, E1["G"], "en", -60); stub(s, E2["G"], "en", 60, flip=1)
    T1 = M(s, "XT1", N5, 400, 460, p["MT"], "VSSA", mult=m); T2 = M(s, "XT2", N5, 1000, 460, p["MT"], "VSSA", mult=m, flip=1)
    s.wire(E1["S"], T1["D"]); s.wire(E2["S"], T2["D"])
    stub(s, T1["G"], "nb", -60); stub(s, T2["G"], "nb", 60, flip=1)
    stub(s, T1["S"], "VSSA", 0, 30); stub(s, T2["S"], "VSSA", 0, 30)
    for nm, y in (("v1p", 700), ("v1m", 750), ("nb", 800), ("pb", 850), ("en", 900), ("enb", 950)):
        s.pin(nm, "in", 60, y); s.wire((60, y), (140, y)); s.label(nm, 140, y, flip=1)
    for nm, y in (("x", 700), ("xc", 750)):
        s.pin(nm, "inout", 1400, y, flip=1); s.wire((1300, y), (1400, y)); s.label(nm, 1300, y)
    s.pin("VDDA", "inout", 60, -900); s.wire((60, -900), (140, -900)); s.label("VDDA", 140, -900, flip=1)
    s.pin("VSSA", "inout", 60, 1050); s.wire((60, 1050), (140, 1050)); s.label("VSSA", 140, 1050, flip=1)
    return s


def buf(p):
    s = Sch("sspll_sscp_hv_buf")
    s.text("sspll_sscp_hv_buf: dump buffer, nMOS-input OTA in unity gain (XA2's gate is the output). Tail XBT (x10 units "
           "mirrored from nb, 20 uA) through the enable XBE", 40, -460, 0.3)
    L1 = M(s, "XL1", P5, 400, -260, p["BP"], "VDDA"); L2 = M(s, "XL2", P5, 1000, -260, p["BP"], "VDDA", flip=1)
    A1 = M(s, "XA1", N5, 400, -20, p["BN"], "VSSA"); A2 = M(s, "XA2", N5, 1000, -20, p["BN"], "VSSA", flip=1)
    stub(s, L1["S"], "VDDA", 0, -30); stub(s, L2["S"], "VDDA", 0, -30)
    s.wire(L1["D"], A1["D"]); s.wire(L2["D"], A2["D"])
    yo = (L1["D"][1] + A1["D"][1])//2
    s.wire(L1["G"], (L1["G"][0] - 40, L1["G"][1]), (L1["G"][0] - 40, yo), (L1["D"][0], yo))       # XL1 diode
    stub(s, L2["G"], "o1", 60, flip=1); stub(s, (L1["G"][0] - 40, yo), "o1", -40, 0)
    stub(s, A1["G"], "inp", -60)
    s.wire((L2["D"][0], yo), (1200, yo)); s.label("out", 1200, yo, flip=1)
    stub(s, A2["G"], "out", 60, flip=1)
    ys = A1["S"][1] + 60
    s.wire(A1["S"], (A1["S"][0], ys), (A2["S"][0], ys), A2["S"])
    m = int(round(p["BIT"]/p["IT"]))
    BE = M(s, "XBE", N5, 680, ys + 120, p["MTS"], "VSSA", mult=m); BT = M(s, "XBT", N5, 680, ys + 300, p["BT"], "VSSA", mult=m)
    s.wire((BE["D"][0], ys), BE["D"]); s.wire(BE["S"], BT["D"])
    stub(s, BE["G"], "en", -60); stub(s, BT["G"], "nb", -60); stub(s, BT["S"], "VSSA", 0, 30)
    for nm, y in (("inp", 560), ("nb", 610), ("en", 660)):
        s.pin(nm, "in", 60, y); s.wire((60, y), (140, y)); s.label(nm, 140, y, flip=1)
    s.pin("out", "out", 1400, 560, flip=1); s.wire((1300, 560), (1400, 560)); s.label("out", 1300, 560)
    s.pin("VDDA", "inout", 60, -500); s.wire((60, -500), (140, -500)); s.label("VDDA", 140, -500, flip=1)
    s.pin("VSSA", "inout", 60, 760); s.wire((60, 760), (140, 760)); s.label("VSSA", 140, 760, flip=1)
    return s


def tg(p):
    s = Sch("sspll_sscp_hv_tg")
    n, pp = p["TGN"], p["TGP"]
    s.text("sspll_sscp_hv_tg: 5 V steering transmission gate a-b, on while g = 1 / gb = 0", 40, -420, 0.3)
    N = s.mos("XN", N5, 300, 0, n[1], n[3], n[2], body="VSSA")
    P = s.mos("XP", P5, 600, 0, pp[1], pp[3], pp[2], body="VDDA", flip=1)
    s.wire(N["D"], (N["D"][0], -120), (P["S"][0], -120), P["S"])
    s.wire(N["S"], (N["S"][0], 120), (P["D"][0], 120), P["D"])
    s.pin("a", "inout", 60, -120); s.wire((60, -120), (N["D"][0], -120))
    s.pin("b", "inout", 860, 120, flip=1); s.wire((P["D"][0], 120), (860, 120))
    s.pin("g", "in", 60, 0); s.wire((60, 0), N["G"])
    s.pin("gb", "in", 860, 0, flip=1); s.wire(P["G"], (860, 0))
    s.pin("VDDA", "inout", 60, -300); s.wire((60, -300), (140, -300)); s.label("VDDA", 140, -300, flip=1)
    s.pin("VSSA", "inout", 60, 300); s.wire((60, 300), (140, 300)); s.label("VSSA", 140, 300, flip=1)
    return s


def core(p, SXY, BXY, TXY):
    s = Sch("sspll_sscp_hv")
    m = p["MTM"]; rm = p.get("RM", 1); rcm, rcw, rcl = p["RCM"]
    s.text("sspll_sscp_hv: pulsed-Gm charge pump, no current mirror. Five slices; each slice's output drain x is steered to vctl "
           "(loop filter) during ckg and to vdump otherwise; each complementary drain xc sits on vdump, so vdump sees no net", 40, -1060, 0.3)
    s.text("AC current while v1 tracks the ring. The dump buffer holds vdump at vctl. pb comes from a replica half-slice whose input "
           "sits at VDDA/2; buses drawn as wires (v1p, v1m, ib, pb on top; x, vdump at the bottom); enables by name", 40, -1020, 0.3)
    YV1P, YV1M, YIB, YPB, YX, YXC = 80, 120, 160, 200, 1000, 1040
    xs = [700 + 700*k for k in range(C.NSL)]
    Xs = [s.sub("sspll_sscp_hv_slice.sym", SXY, f"xs{k+1}", x, 500) for k, x in enumerate(xs)]
    for k, X in enumerate(Xs):
        for pin, bus, dx in (("v1p", YV1P, 130), ("v1m", YV1M, 110), ("nb", YIB, 90), ("pb", YPB, 70)):
            px, py = X[pin]
            s.wire((px - dx, bus), (px - dx, py), (px, py))
        stub(s, X["en"], f"e{k+1}", -40); stub(s, X["enb"], f"eb{k+1}", -40)
        for pin, bus, dx in (("x", YX, 40), ("xc", YXC, 60)):
            px, py = X[pin]
            s.wire((px, py), (px + dx, py), (px + dx, bus))
        stub(s, X["VDDA"], "VDDA", 0, -30); stub(s, X["VSSA"], "VSSA", 0, 30)
    for bus, nm, pin, dx in ((YV1P, "v1p", "v1p", 130), (YV1M, "v1m", "v1m", 110), (YIB, "ib", "nb", 90), (YPB, "pb", "pb", 70)):
        s.wire((250, bus), (Xs[-1][pin][0] - dx, bus)); s.label(nm, 250, bus)
    xe = Xs[-1]["x"][0] + 60
    XT = xe + 500
    s.wire((Xs[0]["x"][0] + 40, YX), (XT - 200, YX))
    s.wire((Xs[0]["xc"][0] + 60, YXC), (XT + 1300, YXC)); s.label("vdump", XT + 1300, YXC)
    # steering TGs and the dump buffer
    TF = s.sub("sspll_sscp_hv_tg.sym", TXY, "xtf", XT, 600); TD = s.sub("sspll_sscp_hv_tg.sym", TXY, "xtd", XT, 1500)
    s.wire((XT - 200, TF["a"][1]), (XT - 200, YX), (XT - 200, TD["a"][1]))
    s.wire((XT - 200, TF["a"][1]), TF["a"]); s.wire((XT - 200, TD["a"][1]), TD["a"])
    for X, g, gb in ((TF, "ckg", "ckgb"), (TD, "ckgb", "ckg")):
        stub(s, X["g"], g, -60); stub(s, X["gb"], gb, -60); stub(s, X["VDDA"], "VDDA", 0, -30); stub(s, X["VSSA"], "VSSA", 0, 30)
    stub(s, TD["b"], "vdump", 80, flip=1)
    B = s.sub("sspll_sscp_hv_buf.sym", BXY, "xbuf", XT + 900, 1500)
    XC = XT + 450
    s.wire(TF["b"], (XC, TF["b"][1]), (XC, B["inp"][1] - 300), (B["inp"][0] - 80, B["inp"][1] - 300),
           (B["inp"][0] - 80, B["inp"][1]), B["inp"])
    s.wire((XC, TF["b"][1]), (XT + 1700, TF["b"][1])); s.pin("vctl", "inout", XT + 1700, TF["b"][1], flip=1)
    stub(s, B["out"], "vdump", 80, flip=1)
    if p.get("CDUMP"):
        cm, cw, cn, cl = p["CDUMP"]
        CDm = s.dev("sky130_fd_pr/cap_mim_m3_1.sym", "XCDUMP", XT + 1500, 1900, f"W={cw} L={cl} MF={cn} model={cm} spiceprefix=X")
        stub(s, CDm["c0"], "vdump", 0, -60); stub(s, CDm["c1"], "VSSA", 0, 60)
    stub(s, B["nb"], "ib", -50); stub(s, B["en"], "pll_en", -50)
    stub(s, B["VDDA"], "VDDA", 0, -30); stub(s, B["VSSA"], "VSSA", 0, 30)
    # bias: unit diode on ib, replica half-slice for pb
    NB = M(s, "XNB", N5, 300, -300, p["MT"], "VSSA")
    s.wire(NB["G"], (NB["G"][0] - 40, NB["G"][1]), (NB["G"][0] - 40, NB["D"][1] - 40), (NB["D"][0], NB["D"][1] - 40), NB["D"])
    stub(s, (NB["D"][0], NB["D"][1] - 40), "ib", 0, -40); stub(s, NB["S"], "VSSA", 0, 30)
    XR = 1300
    RPE = M(s, "XRPE", P5, XR, -880, p["MPE"], "VDDA", mult=m*rm); RP = M(s, "XRP", P5, XR, -680, p["MP"], "VDDA", mult=m*rm)
    stub(s, RPE["S"], "VDDA", 0, -30); stub(s, RPE["G"], "VSSA", -60); s.wire(RPE["D"], RP["S"])
    RD = M(s, "XRD", N5, XR, -420, p["MN"], "VSSA", mult=rm)
    s.wire(RP["D"], RD["D"])
    pbp = (RP["D"][0], (RP["D"][1] + RD["D"][1])//2)
    s.wire(RP["G"], (RP["G"][0] - 40, RP["G"][1]), (RP["G"][0] - 40, pbp[1]), pbp)
    stub(s, (RP["G"][0] - 40, RP["G"][1]), "pb", -60)
    RE = M(s, "XRE", N5, XR, -230, p["MTS"], "VSSA", mult=m*rm); RT = M(s, "XRT", N5, XR, -40, p["MT"], "VSSA", mult=m*rm)
    s.wire(RD["S"], RE["D"]); s.wire(RE["S"], RT["D"])
    stub(s, RE["G"], "pll_en", -60); stub(s, RT["G"], "ib", -60); stub(s, RT["S"], "VSSA", 0, 30)
    R1 = s.dev(RES, "XRC1", 800, -640, f"L={rcl} mult=1 model={rcm} spiceprefix=X")
    R2 = s.dev(RES, "XRC2", 800, -360, f"L={rcl} mult=1 model={rcm} spiceprefix=X")
    stub(s, R1["P"], "VDDA", 0, -40); s.wire(R1["M"], R2["P"]); stub(s, R2["M"], "VSSA", 0, 40)
    stub(s, R1["B"], "VSSA", -60); stub(s, R2["B"], "VSSA", -60)
    vc_ = (R1["M"][0], (R1["M"][1] + R2["P"][1])//2)
    s.wire(vc_, (vc_[0] + 160, vc_[1]), (vc_[0] + 160, RD["G"][1]), RD["G"])
    names = [("v1p", "in"), ("v1m", "in"), ("ckg", "in"), ("ckgb", "in"), ("ib", "inout")] + \
            [(f"e{k+1}", "in") for k in range(C.NSL)] + [(f"eb{k+1}", "in") for k in range(C.NSL)] + [("pll_en", "in")]
    for k, (nm, d) in enumerate(names):
        y = 1300 + 50*k
        s.pin(nm, d, 60, y); s.wire((60, y), (140, y)); s.label(nm, 140, y, flip=1)
    s.pin("VDDA", "inout", 60, -960); s.wire((60, -960), (140, -960)); s.label("VDDA", 140, -960, flip=1)
    s.pin("VSSA", "inout", 60, 2300); s.wire((60, 2300), (140, 2300)); s.label("VSSA", 140, 2300, flip=1)
    return s


def nand2(s, name, x, y, size):
    """1.8 V NAND2 on VDDD: series nMOS (a on top), parallel pMOS. Returns input points a, b and the output point."""
    n, p = size
    PA = s.mos(name + "PA", P18, x, y - 100, p[1], p[3], p[2], body="VDDD")
    PB = s.mos(name + "PB", P18, x + 220, y - 100, p[1], p[3], p[2], body="VDDD")
    NA = s.mos(name + "NA", N18, x, y + 90, n[1], n[3], n[2], body="VSSD")
    NB = s.mos(name + "NB", N18, x, y + 210, n[1], n[3], n[2], body="VSSD")
    s.wire(PA["D"], NA["D"]); s.wire(NA["S"], NB["D"])
    s.wire((PA["D"][0], y), (PB["D"][0], y), PB["D"])
    for P_ in (PA, PB):
        stub(s, P_["S"], "VDDD", 0, -30)
    stub(s, NB["S"], "VSSD", 0, 30)
    s.wire(PA["G"], (x - 80, PA["G"][1]), (x - 80, NA["G"][1]), NA["G"])
    s.wire(PB["G"], (PB["G"][0] - 30, PB["G"][1]), (PB["G"][0] - 30, PB["G"][1] + 60), (x - 40, PB["G"][1] + 60),
           (x - 40, NB["G"][1]), NB["G"])
    return (x - 80, y), (x - 40, NB["G"][1]), (PB["D"][0] + 40, y)


def dec(p, LS):
    s = Sch("sspll_sscp_hv_dec")
    s.text("sspll_sscp_hv_dec: icp_trim decoder (1.8 V, VDDD): e12 = en; e3 = en AND NOT(icp1 AND NOT icp0); "
           "e4 = en AND icp0; e5 = en AND icp1 AND icp0; four level shifters to the 5 V enable gates", 40, -560, 0.3)
    inv = lambda nm, x, y: _ck.inverter(s, nm, x, y, C.DL["INV"], "VDDD")
    g = {}
    i0, o0 = inv("XI0", 300, 0); stub(s, i0, "icp0", -60); stub(s, o0, "c0b", 60, flip=1)
    gates = [("XA", "icp1", "c0b", "a3", 700, 0), ("XB", "pll_en", "a3", "e3b", 1300, 0), ("XC", "pll_en", "icp0", "e4b", 700, 600),
             ("XD", "icp1", "icp0", "a5b", 1300, 600), ("XE", "pll_en", "a5", "e5b", 700, 1200)]
    for nm, a, b, y_, x, y in gates:
        pa, pb, po = nand2(s, nm, x, y, C.DL["NAND"])
        stub(s, pa, a, -60); stub(s, pb, b, -60); s.wire((po[0] - 40, po[1]), po); s.label(y_, po[0], po[1], flip=1)
    for nm, a, y_, x, y in (("XI3", "e3b", "e3l", 1900, 0), ("XI4", "e4b", "e4l", 1900, 600), ("XI5", "a5b", "a5", 1900, 1200),
                            ("XI6", "e5b", "e5l", 2300, 1200)):
        i_, o_ = inv(nm, x, y); stub(s, i_, a, -60); stub(s, o_, y_, 60, flip=1)
    for k, (nm, i) in enumerate((("e12", "pll_en"), ("e3", "e3l"), ("e4", "e4l"), ("e5", "e5l"))):
        L = s.sub("../cco_hv/sspll_ls_1v8_3v3.sym", LS, f"xls{nm}", 2900, 1700*0 + 400*k)
        stub(s, L["in"], i, -60); stub(s, L["out"], nm, 60, flip=1); stub(s, L["outb"], nm + "_b", 60, flip=1)
        stub(s, L["VDDD"], "VDDD", 0, -30); stub(s, L["VDDA"], "VDDA", 0, -30, flip=1)
        stub(s, L["VSSA"], "VSSA", 0, 30); stub(s, L["VSSD"], "VSSD", 0, 30, flip=1)
    for k, nm in enumerate(("icp0", "icp1", "pll_en")):
        y = 1700 + 50*k
        s.pin(nm, "in", 60, y); s.wire((60, y), (140, y)); s.label(nm, 140, y, flip=1)
    for k, nm in enumerate(("e12", "e3", "e4", "e5", "e12_b", "e3_b", "e4_b", "e5_b")):
        y = 1700 + 50*k
        s.pin(nm, "out", 3500, y, flip=1); s.wire((3400, y), (3500, y)); s.label(nm, 3400, y)
    s.pin("VDDD", "inout", 60, -500); s.wire((60, -500), (140, -500)); s.label("VDDD", 140, -500, flip=1)
    s.pin("VDDA", "inout", 60, -450); s.wire((60, -450), (140, -450)); s.label("VDDA", 140, -450, flip=1)
    s.pin("VSSA", "inout", 60, 2150); s.wire((60, 2150), (140, 2150)); s.label("VSSA", 140, 2150, flip=1)
    s.pin("VSSD", "inout", 60, 2200); s.wire((60, 2200), (140, 2200)); s.label("VSSD", 140, 2200, flip=1)
    return s


def top(DXY, CXY):
    s = Sch("sspll_sscp_hv_top")
    s.text("sspll_sscp_hv_top: pulsed-Gm charge pump with its trim decoder; slices 1 and 2 follow pll_en (e12), "
           "slices 3-5 follow the decoded icp_trim, the dump buffer follows pll_en", 40, -460, 0.3)
    Dd = s.sub("sspll_sscp_hv_dec.sym", DXY, "xdec", 500, 0); Cc = s.sub("sspll_sscp_hv.sym", CXY, "xgm", 1300, 0)
    for pin in ("icp0", "icp1", "pll_en"):
        stub(s, Dd[pin], pin, -60)
    for pin in ("e12", "e3", "e4", "e5", "e12_b", "e3_b", "e4_b", "e5_b"):
        stub(s, Dd[pin], pin, 60, flip=1)
    for pin, net in (("v1p", "v1p"), ("v1m", "v1m"), ("ckg", "ckg"), ("ckgb", "ckgb"), ("ib", "ib"), ("e1", "e12"),
                     ("e2", "e12"), ("e3", "e3"), ("e4", "e4"), ("e5", "e5"), ("eb1", "e12_b"), ("eb2", "e12_b"),
                     ("eb3", "e3_b"), ("eb4", "e4_b"), ("eb5", "e5_b"), ("pll_en", "e12")):
        stub(s, Cc[pin], net, -60)
    stub(s, Cc["vctl"], "vctl", 60, flip=1)
    for X, sup, gnd in ((Dd, ("VDDD", "VDDA"), ("VSSA", "VSSD")), (Cc, ("VDDA",), ("VSSA",))):
        for k, nm in enumerate(sup):            # the second label of a pair points the other way (no overlap)
            stub(s, X[nm], nm, 0, -30, flip=k)
        for k, nm in enumerate(gnd):
            stub(s, X[nm], nm, 0, 30, flip=k)
    names = [("v1p", "in"), ("v1m", "in"), ("ckg", "in"), ("ckgb", "in"), ("ib", "inout"), ("icp0", "in"), ("icp1", "in"),
             ("pll_en", "in")]
    for k, (nm, d) in enumerate(names):
        y = 700 + 50*k
        s.pin(nm, d, 60, y); s.wire((60, y), (140, y)); s.label(nm, 140, y, flip=1)
    s.pin("vctl", "inout", 2000, 700, flip=1); s.wire((1900, 700), (2000, 700)); s.label("vctl", 1900, 700)
    s.pin("VDDA", "inout", 60, -350); s.wire((60, -350), (140, -350)); s.label("VDDA", 140, -350, flip=1)
    s.pin("VDDD", "inout", 60, -300); s.wire((60, -300), (140, -300)); s.label("VDDD", 140, -300, flip=1)
    s.pin("VSSA", "inout", 60, 1200); s.wire((60, 1200), (140, 1200)); s.label("VSSA", 140, 1200, flip=1)
    s.pin("VSSD", "inout", 60, 1250); s.wire((60, 1250), (140, 1250)); s.label("VSSD", 140, 1250, flip=1)
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p = C.D
    LS = symbol("/tmp/ls_tmp.sym", "sspll_ls_1v8_3v3", **LS_PINS)
    RXY = symbol(os.path.join(OUT, "sspll_sscp_hv_rs.sym"), "sspll_sscp_hv_rs", left=[("a", "inout")], right=[("b", "inout")],
                 bottom=[("VSSA", "inout")])
    SXY = symbol(os.path.join(OUT, "sspll_sscp_hv_slice.sym"), "sspll_sscp_hv_slice",
                 left=[("v1p", "in"), ("v1m", "in"), ("nb", "in"), ("pb", "in"), ("en", "in"), ("enb", "in")],
                 right=[("x", "inout"), ("xc", "inout")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    BXY = symbol(os.path.join(OUT, "sspll_sscp_hv_buf.sym"), "sspll_sscp_hv_buf", left=[("inp", "in"), ("nb", "in"), ("en", "in")],
                 right=[("out", "out")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    TXY = symbol(os.path.join(OUT, "sspll_sscp_hv_tg.sym"), "sspll_sscp_hv_tg", left=[("a", "inout"), ("g", "in"), ("gb", "in")],
                 right=[("b", "inout")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    CXY = symbol(os.path.join(OUT, "sspll_sscp_hv.sym"), "sspll_sscp_hv",
                 left=[("v1p", "in"), ("v1m", "in"), ("ckg", "in"), ("ckgb", "in"), ("ib", "inout")] +
                      [(f"e{k+1}", "in") for k in range(C.NSL)] + [(f"eb{k+1}", "in") for k in range(C.NSL)] + [("pll_en", "in")],
                 right=[("vctl", "inout")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    DXY = symbol(os.path.join(OUT, "sspll_sscp_hv_dec.sym"), "sspll_sscp_hv_dec",
                 left=[("icp0", "in"), ("icp1", "in"), ("pll_en", "in")], right=[("e12", "out"), ("e3", "out"), ("e4", "out"), ("e5", "out"),
                        ("e12_b", "out"), ("e3_b", "out"), ("e4_b", "out"), ("e5_b", "out")],
                 top=[("VDDD", "inout"), ("VDDA", "inout")], bottom=[("VSSA", "inout"), ("VSSD", "inout")])
    symbol(os.path.join(OUT, "sspll_sscp_hv_top.sym"), "sspll_sscp_hv_top",
           left=[("v1p", "in"), ("v1m", "in"), ("ckg", "in"), ("ckgb", "in"), ("ib", "inout"), ("icp0", "in"), ("icp1", "in"),
                 ("pll_en", "in")], right=[("vctl", "inout")], top=[("VDDA", "inout"), ("VDDD", "inout")], bottom=[("VSSA", "inout"), ("VSSD", "inout")])
    for name, sch in (("sspll_sscp_hv_rs", rs(p)), ("sspll_sscp_hv_slice", slice_(p, RXY)), ("sspll_sscp_hv_buf", buf(p)),
                      ("sspll_sscp_hv_tg", tg(p)), ("sspll_sscp_hv", core(p, SXY, BXY, TXY)), ("sspll_sscp_hv_dec", dec(p, LS)),
                      ("sspll_sscp_hv_top", top(DXY, CXY))):
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        print(name, ":", "\n  ".join(errs) or "drawing check clean")
    open(os.path.join(ROOT, "xschem", "netlist", "ref_sscp_hv.spice"), "w").write(C.lvs_reference())
