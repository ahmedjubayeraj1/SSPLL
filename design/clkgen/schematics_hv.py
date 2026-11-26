#!/usr/bin/env python3
"""schematics_hv.py - xschem schematics of the clock generator with 3.3 V outputs (hierarchical, real
wiring, drawing checks) and the LVS reference:
   sspll_ckg_edges_g / _h  1.8 V RC edge pairs (start = in, stop = delayed edge, pls = 1.8 V pulse)
   sspll_ckg_hlatch        hold trigger latch (as on 13/17 Nov)
   sspll_ckg_drv5 / drv5t  5 V complementary drivers (always-on TG + 2 inverters / 3 inverters)
   sspll_ckg_pout5         5 V pulse output: two step drivers, NOR (o) and NAND (ob)
   sspll_clkgen_hv         top: 1.8 V core on VDDD, 5 level shifters, 5 V outputs on VDDA
Ground split (24 Nov 2026): the 1.8 V cells (edge pairs, delay, latch, the top's 1.8 V inverters) are on VDDD / VSSD,
the 5 V cells (drivers, pulse outputs) on VDDA / VSSA, the level shifters have both grounds."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
from xsch import Sch, symbol
import clkgen_hv as K
import importlib.util
_sp = importlib.util.spec_from_file_location("schematics_ckg18", os.path.join(HERE, "schematics.py"))
S18 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(S18)   # the 13 Nov drawing helpers (by path:
                                                                           # design/cco has a schematics.py too)
OUT = os.path.join(ROOT, "xschem", "clkgen_hv")
N18, P18, N5, P5 = "nfet3_01v8", "pfet3_01v8", "nfet3_g5v0d10v5", "pfet3_g5v0d10v5"
RES = S18.RES; MIM = S18.MIM
LS_PINS = dict(left=[("in", "in")], right=[("out", "out"), ("outb", "out")], top=[("VDDD", "inout"), ("VDDA", "inout")],
               bottom=[("VSSA", "inout"), ("VSSD", "inout")])
GND = {"VDDA": "VSSA", "VDDD": "VSSD"}          # the ground that goes with each supply (generic VDD -> VSS)


def inverter(s, name, x, y, size, vdd="VDD", thick=False):
    n, p = size
    P = s.mos(name + "P", P5 if thick else P18, x, y - 80, p[1], p[3], p[2], body=vdd)
    vss = GND.get(vdd, "VSS")
    N = s.mos(name + "N", N5 if thick else N18, x, y + 80, n[1], n[3], n[2], body=vss)
    s.wire(P["D"], N["D"])
    s.wire(P["G"], (x - 60, P["G"][1]), (x - 60, N["G"][1]), N["G"])
    s.wire(P["S"], (P["S"][0], P["S"][1] - 30)); s.label(vdd, P["S"][0], P["S"][1] - 30)
    s.wire(N["S"], (N["S"][0], N["S"][1] + 30)); s.label(vss, N["S"][0], N["S"][1] + 30)
    return (x - 60, y), (P["D"][0], y)


def supplies(s, vdd, ytop, ybot):
    s.pin(vdd, "inout", 60, ytop); s.wire((60, ytop), (140, ytop)); s.label(vdd, 140, ytop, flip=1)
    vss = GND.get(vdd, "VSS")
    s.pin(vss, "inout", 60, ybot); s.wire((60, ybot), (140, ybot)); s.label(vss, 140, ybot, flip=1)


def edges(p, nm):
    """As the 13 Nov pulser, with the delayed edge brought out as 'stop' and the 1.8 V pulse as 'pls'."""
    R, C = ("RH", "CH") if nm == "h" else ("RG", "CG")
    rm, _, _, L = p[R]; cm, cw, _, cl = p[C]
    s = Sch(f"sspll_ckg_edges_{nm}")
    s.text(f"sspll_ckg_edges_{nm}: stop rises ln2 RC + 2 gates after in rises (R: L = {L} um, C: {cw} x {cl} um); "
           "pls = in AND NOT stop = NOR(inb, stop), the 1.8 V pulse", 40, -560, 0.3)
    s.pin("in", "in", 60, 0)
    i2, o2 = inverter(s, "X2", 300, 0, p["INVS"])
    Rr = s.dev(RES, "XR", 460, 0, f"L={L} mult=1 model={rm} spiceprefix=X", rot=3)
    Cc = s.dev(MIM, "XC", 600, 90, f"W={cw} L={cl} MF=1 model={cm} spiceprefix=X")
    i3, o3 = inverter(s, "X3", 800, 0, p["INVS"])
    i1, o1 = inverter(s, "X1", 300, 480, p["INVS"])
    s.wire((60, 0), i2); s.wire((140, 0), (140, 480), i1)
    s.wire(o2, Rr["P"] if Rr["P"][0] < Rr["M"][0] else Rr["M"])
    rc_end = Rr["M"] if Rr["P"][0] < Rr["M"][0] else Rr["P"]
    s.wire(rc_end, (Cc["c0"][0], rc_end[1]), i3)
    s.wire((Cc["c0"][0], rc_end[1]), Cc["c0"])
    s.wire(Cc["c1"], (Cc["c1"][0], Cc["c1"][1] + 30)); s.label("VSS", Cc["c1"][0], Cc["c1"][1] + 30)
    s.wire(Rr["B"], (Rr["B"][0], Rr["B"][1] - 30)); s.label("VSS", Rr["B"][0], Rr["B"][1] - 30)
    a, b, o = S18.nor2(s, "X4", 1260, 300, p["NOR"])
    s.wire(o1, (1100, 480), (1100, a[1]), a)
    s.wire(o3, (1000, 0), (1000, 450), (1120, 450), (1120, b[1]), b)
    s.wire((1000, 0), (1700, 0)); s.pin("stop", "out", 1700, 0, flip=1)
    s.wire(o, (1700, 300)); s.pin("pls", "out", 1700, 300, flip=1)
    supplies(s, "VDD", -400, 760)
    return s.rename({"VDD": "VDDD", "VSS": "VSSD"})      # 1.8 V cell: digital supply and ground


def dly(p):
    """Gap-1 RC delay: inverter -> R -> C -> three inverters (non-inverting; the last two restore a sharp edge)."""
    rm, _, _, L = p["RDL"]; cm, cw, _, cl = p["CDL"]
    s = Sch("sspll_ckg_dly")
    s.text(f"sspll_ckg_dly: gap-1 delay, both edges about ln2 RC + 4 gates (R: L = {L} um, C: {cw} x {cl} um). It gives the "
           "pulsed Gm about 2.4 ns after the sample to recover from the SSPD's 800 MHz tracking swing", 40, -560, 0.3)
    s.pin("in", "in", 60, 0)
    i1, o1 = inverter(s, "X1", 300, 0, p["INVS"])
    Rr = s.dev(RES, "XR", 460, 0, f"L={L} mult=1 model={rm} spiceprefix=X", rot=3)
    Cc = s.dev(MIM, "XC", 600, 90, f"W={cw} L={cl} MF=1 model={cm} spiceprefix=X")
    i2, o2 = inverter(s, "X2", 800, 0, p["INVS"]); i3, o3 = inverter(s, "X3", 1060, 0, p["INVS"])
    i4, o4 = inverter(s, "X4", 1320, 0, p["INVS"])
    s.wire((60, 0), i1)
    s.wire(o1, Rr["P"] if Rr["P"][0] < Rr["M"][0] else Rr["M"])
    rc_end = Rr["M"] if Rr["P"][0] < Rr["M"][0] else Rr["P"]
    s.wire(rc_end, (Cc["c0"][0], rc_end[1]), i2)
    s.wire((Cc["c0"][0], rc_end[1]), Cc["c0"])
    s.wire(Cc["c1"], (Cc["c1"][0], Cc["c1"][1] + 30)); s.label("VSS", Cc["c1"][0], Cc["c1"][1] + 30)
    s.wire(Rr["B"], (Rr["B"][0], Rr["B"][1] - 30)); s.label("VSS", Rr["B"][0], Rr["B"][1] - 30)
    s.wire(o2, i3); s.wire(o3, i4)
    s.wire(o4, (1700, 0)); s.pin("out", "out", 1700, 0, flip=1)
    supplies(s, "VDD", -400, 400)
    return s.rename({"VDD": "VDDD", "VSS": "VSSD"})


def drv5(p, nm, L, TG):
    s = Sch(f"sspll_ckg_{nm}")
    s.text(f"sspll_ckg_{nm}: o follows in through an always-on TG and 2 inverters, ob is inverted through 3; "
           "the TG adds about one gate delay so o and ob switch together (5 V devices on VDDA)", 40, -420, 0.3)
    tn, tp = p[TG]
    s.pin("in", "in", 60, 0)
    TN = s.mos("XTN", N5, 300, 90, tn[1], tn[3], tn[2], body="VSSA")
    TP = s.mos("XTP", P5, 300, -110, tp[1], tp[3], tp[2], body="VDDA")
    # the TG: nMOS source / pMOS source on in, both drains on a0
    s.wire((60, 0), (180, 0), (180, TN["S"][1]), TN["S"])
    s.wire((180, 0), (180, TP["S"][1] - 80), (TP["S"][0], TP["S"][1] - 80), TP["S"])
    s.wire(TN["D"], (TN["D"][0], 0)); s.wire(TP["D"], (TP["D"][0], 0))
    s.wire(TN["G"], (TN["G"][0] - 40, TN["G"][1])); s.label("VDDA", TN["G"][0] - 40, TN["G"][1])
    s.wire(TP["G"], (TP["G"][0] - 40, TP["G"][1])); s.label("VSSA", TP["G"][0] - 40, TP["G"][1])
    ia, oa = inverter(s, "XA", 560, 0, p["INV5A"], "VDDA", True); ib, ob_ = inverter(s, "XB", 820, 0, p[L], "VDDA", True)
    s.wire((TN["D"][0], 0), ia); s.wire(oa, ib)
    ic, oc = inverter(s, "XC", 560, 480, p["INV5S"], "VDDA", True); id_, od = inverter(s, "XD", 820, 480, p["INV5M"], "VDDA", True)
    ie, oe = inverter(s, "XE", 1080, 480, p[L], "VDDA", True)
    s.wire((140, 0), (140, 480), ic); s.wire(oc, id_); s.wire(od, ie)
    s.wire(ob_, (1260, 0)); s.pin("o", "out", 1260, 0, flip=1)
    s.wire(oe, (1260, 480)); s.pin("ob", "out", 1260, 480, flip=1)
    supplies(s, "VDDA", -340, 760)
    return s


def pout5(p, DXY):
    s = Sch("sspll_ckg_pout5")
    s.text("sspll_ckg_pout5: start and stop are rising steps; each gets a complementary step driver (drv5t); the pulse "
           "exists only at the output gates: o = NOR(NOT start, stop), ob = NAND(start, NOT stop)", 40, -520, 0.3)
    s.pin("start", "in", 60, 0); s.pin("stop", "in", 60, 600)
    DA = s.sub("sspll_ckg_drv5t.sym", DXY, "xda", 360, 0); DB = s.sub("sspll_ckg_drv5t.sym", DXY, "xdb", 360, 600)
    s.wire((60, 0), DA["in"]); s.wire((60, 600), DB["in"])
    for D_ in (DA, DB):
        s.wire(D_["VDDA"], (D_["VDDA"][0], D_["VDDA"][1] - 20)); s.label("VDDA", D_["VDDA"][0], D_["VDDA"][1] - 20)
        s.wire(D_["VSSA"], (D_["VSSA"][0], D_["VSSA"][1] + 20)); s.label("VSSA", D_["VSSA"][0], D_["VSSA"][1] + 20)
    for pin, net in ((DA["o"], "st"), (DA["ob"], "stb"), (DB["o"], "sp"), (DB["ob"], "spb")):
        s.wire(pin, (pin[0] + 60, pin[1])); s.label(net, pin[0] + 60, pin[1], flip=1)
    (nn, np_), (an, ap) = p["NOR5L"], p["NAND5L"]
    X = 1000
    PA = s.mos("XPA", P5, X, -220, np_[1], np_[3], np_[2], body="VDDA"); PB = s.mos("XPB", P5, X, -100, np_[1], np_[3], np_[2], body="VDDA")
    NA = s.mos("XNA", N5, X, 80, nn[1], nn[3], nn[2], body="VSSA"); NB = s.mos("XNB", N5, X + 260, 80, nn[1], nn[3], nn[2], body="VSSA")
    s.wire(PA["D"], PB["S"]); s.wire(PB["D"], NA["D"]); s.wire((PB["D"][0], 0), (NB["D"][0], 0), NB["D"])
    s.wire(PA["S"], (PA["S"][0], PA["S"][1] - 30)); s.label("VDDA", PA["S"][0], PA["S"][1] - 30)
    for M_ in (NA, NB):
        s.wire(M_["S"], (M_["S"][0], M_["S"][1] + 30)); s.label("VSSA", M_["S"][0], M_["S"][1] + 30)
    for M_, net in ((PA, "stb"), (NA, "stb"), (PB, "sp"), (NB, "sp")):
        s.wire(M_["G"], (M_["G"][0] - 40, M_["G"][1])); s.label(net, M_["G"][0] - 40, M_["G"][1])
    s.wire((PB["D"][0], 0), (PB["D"][0] + 400, 0)); s.pin("o", "out", PB["D"][0] + 400, 0, flip=1)
    QA = s.mos("XQA", P5, X, 520, ap[1], ap[3], ap[2], body="VDDA"); QB = s.mos("XQB", P5, X + 260, 520, ap[1], ap[3], ap[2], body="VDDA")
    MA = s.mos("XMA", N5, X, 700, an[1], an[3], an[2], body="VSSA"); MB = s.mos("XMB", N5, X, 820, an[1], an[3], an[2], body="VSSA")
    s.wire(QA["D"], MA["D"]); s.wire(MA["S"], MB["D"]); s.wire((QA["D"][0], 610), (QB["D"][0], 610), QB["D"])
    for M_ in (QA, QB):
        s.wire(M_["S"], (M_["S"][0], M_["S"][1] - 30)); s.label("VDDA", M_["S"][0], M_["S"][1] - 30)
    s.wire(MB["S"], (MB["S"][0], MB["S"][1] + 30)); s.label("VSSA", MB["S"][0], MB["S"][1] + 30)
    for M_, net in ((QA, "st"), (MA, "st"), (QB, "spb"), (MB, "spb")):
        s.wire(M_["G"], (M_["G"][0] - 40, M_["G"][1])); s.label(net, M_["G"][0] - 40, M_["G"][1])
    s.wire((QB["D"][0], 610), (PB["D"][0] + 400, 610)); s.pin("ob", "out", PB["D"][0] + 400, 610, flip=1)
    supplies(s, "VDDA", -460, 1000)
    return s


def ortho(s):
    """Wrap s.wire so that a step between two points that are not in line becomes horizontal - vertical -
    horizontal, with the vertical part halfway (sub-cell pins do not sit on the row lines)."""
    raw = s.wire
    def wire(*pts):
        q = [pts[0]]
        for a in pts[1:]:
            b = q[-1]
            if a[0] != b[0] and a[1] != b[1]:
                xm = (a[0] + b[0])//2
                q += [(xm, b[1]), (xm, a[1])]
            q.append(a)
        return raw(*q)
    s.wire = wire
    return s


def top(p, LS, EXY, LXY, DXY, PXY, DLXY):
    s = ortho(Sch("sspll_clkgen_hv"))
    s.text("sspll_clkgen_hv: sampling pair from refhv (receiver, 3.3 V) through a 5 V driver; 1.8 V core on VDDD (refclk buffer, "
           "gap inverters, RC edge pairs, hold latch); each pulse crosses to VDDA as two rising steps and is formed at the 5 V output gates", 40, -560, 0.3)
    s.text("cks falls (sw1 samples) at the reference rising edge; ckg = Gm pulse (tau 530 ps); ckh = hold pulse; "
           "supplies of the sub-cells and internal nets joined by name", 40, -520, 0.25)
    s.pin("refclk", "in", 60, 0)
    i0, o0 = inverter(s, "XI0", 260, 0, p["INVM"], "VDDD"); i1, o1 = inverter(s, "XI1", 520, 0, p["INVM"], "VDDD")
    xm = (o0[0] + i1[0])//2
    s.wire((60, 0), i0); s.wire(o0, (xm, 0)); s.wire((xm, 0), i1)
    s.wire((xm, 0), (xm, 40)); s.label("r1", xm, 40)
    s.wire(o1, (680, 0))
    # sampling pair: from refhv (the receiver's 3.3 V edge) straight into the 5 V driver
    s.pin("refhv", "in", 60, -200)
    DS = s.sub("sspll_ckg_drv5.sym", DXY, "xds", 1400, -200)
    s.wire((60, -200), (1000, -200), DS["in"])
    # Gm row
    DL = s.sub("sspll_ckg_dly.sym", DLXY, "xdl", 400, 640)
    s.wire((680, 0), (680, 360), (160, 360), (160, DL["in"][1]), DL["in"])
    s.wire(DL["VDDD"], (DL["VDDD"][0], DL["VDDD"][1] - 30)); s.label("VDDD", DL["VDDD"][0], DL["VDDD"][1] - 30)
    s.wire(DL["VSSD"], (DL["VSSD"][0], DL["VSSD"][1] + 30)); s.label("VSSD", DL["VSSD"][0], DL["VSSD"][1] + 30)
    EG = s.sub("sspll_ckg_edges_g.sym", EXY, "xeg", 900, 640)
    q3 = DL["out"]
    s.wire(q3, (720, q3[1]), (720, 640), EG["in"])
    LG1 = s.sub("../cco_hv/sspll_ls_1v8_3v3.sym", LS, "xlsg1", 1400, 500)
    LG2 = s.sub("../cco_hv/sspll_ls_1v8_3v3.sym", LS, "xlsg2", 1400, 820)
    s.wire((720, 640), (720, 500), (1200, 500), (1200, LG1["in"][1]), LG1["in"])
    s.wire(EG["stop"], (1240, EG["stop"][1]), (1240, LG2["in"][1]), LG2["in"])
    PG = s.sub("sspll_ckg_pout5.sym", PXY, "xpg", 1900, 660)
    s.wire(LG1["out"], (1700, LG1["out"][1]), (1700, PG["start"][1]), PG["start"])
    s.wire(LG2["out"], (1740, LG2["out"][1]), (1740, PG["stop"][1]), PG["stop"])
    s.wire(EG["pls"], (EG["pls"][0] + 40, EG["pls"][1])); s.label("pg", EG["pls"][0] + 40, EG["pls"][1], flip=1)
    # hold row
    HL = s.sub("sspll_ckg_hlatch.sym", LXY, "xhl", 360, 1300)
    s.wire(HL["s"], (HL["s"][0] - 60, HL["s"][1])); s.label("pg", HL["s"][0] - 60, HL["s"][1])
    s.wire(HL["r"], (HL["r"][0] - 60, HL["r"][1])); s.label("r1", HL["r"][0] - 60, HL["r"][1])
    k4, h4 = inverter(s, "XI4", 720, 1300, p["INVS"], "VDDD"); k5, h5 = inverter(s, "XI5", 980, 1300, p["INVS"], "VDDD")
    k6, h6 = inverter(s, "XI6", 1240, 1300, p["INVS"], "VDDD"); k7, h7 = inverter(s, "XI7", 1500, 1300, p["INVS"], "VDDD")
    s.wire(HL["out"], (620, HL["out"][1]), (620, 1300), k4); s.wire(h4, k5); s.wire(h5, k6); s.wire(h6, k7)
    EH = s.sub("sspll_ckg_edges_h.sym", EXY, "xeh", 1840, 1300)
    s.wire(h7, (1660, 1300), EH["in"])
    LH1 = s.sub("../cco_hv/sspll_ls_1v8_3v3.sym", LS, "xlsh1", 2340, 1160)
    LH2 = s.sub("../cco_hv/sspll_ls_1v8_3v3.sym", LS, "xlsh2", 2340, 1480)
    s.wire((1660, 1300), (1660, 1100), (2140, 1100), (2140, LH1["in"][1]), LH1["in"])
    s.wire(EH["stop"], (2180, EH["stop"][1]), (2180, LH2["in"][1]), LH2["in"])
    s.wire(EH["pls"], (EH["pls"][0] + 40, EH["pls"][1])); s.label("ph", EH["pls"][0] + 40, EH["pls"][1], flip=1)
    PH = s.sub("sspll_ckg_pout5.sym", PXY, "xph", 2840, 1320)
    s.wire(LH1["out"], (2640, LH1["out"][1]), (2640, PH["start"][1]), PH["start"])
    s.wire(LH2["out"], (2680, LH2["out"][1]), (2680, PH["stop"][1]), PH["stop"])
    # unused complementary outputs of the level shifters: short stubs with their own net names
    for X, nm in ((LG1, "g2hb"), (LG2, "gshb"), (LH1, "hinhb"), (LH2, "hshb")):
        s.wire(X["outb"], (X["outb"][0] + 40, X["outb"][1])); s.label(nm, X["outb"][0] + 40, X["outb"][1], flip=1)
    for D_, a, b in ((DS, "cksb", "cks"), (PG, "ckg", "ckgb"), (PH, "ckh", "ckhb")):
        s.wire(D_["o"], (3300, D_["o"][1])); s.pin(a, "out", 3300, D_["o"][1], flip=1)
        s.wire(D_["ob"], (3300, D_["ob"][1])); s.pin(b, "out", 3300, D_["ob"][1], flip=1)
    for X in (LG1, LG2, LH1, LH2):
        s.wire(X["VDDD"], (X["VDDD"][0], X["VDDD"][1] - 20)); s.label("VDDD", X["VDDD"][0], X["VDDD"][1] - 20)
        s.wire(X["VDDA"], (X["VDDA"][0], X["VDDA"][1] - 20)); s.label("VDDA", X["VDDA"][0], X["VDDA"][1] - 20, flip=1)
    for X in (DS, PG, PH):
        s.wire(X["VDDA"], (X["VDDA"][0], X["VDDA"][1] - 20)); s.label("VDDA", X["VDDA"][0], X["VDDA"][1] - 20)
    for X in (EG, EH, HL):
        s.wire(X["VDDD"], (X["VDDD"][0], X["VDDD"][1] - 20)); s.label("VDDD", X["VDDD"][0], X["VDDD"][1] - 20)
    LSS = (LG1, LG2, LH1, LH2)    # level shifters: VSSA label to the left of its pin, VSSD to the right (no overlap)
    # grounds: 5 V cells and the level shifters' output side on VSSA, 1.8 V cells and the level shifters' input on VSSD
    for X, g in [(X, "VSSA") for X in (LG1, LG2, LH1, LH2, DS, PG, PH)] + [(X, "VSSD") for X in (LG1, LG2, LH1, LH2, EG, EH, HL)]:
        s.wire(X[g], (X[g][0], X[g][1] + 20)); s.label(g, X[g][0], X[g][1] + 20, flip=1 if (g == "VSSD" and X in LSS) else 0)
    s.pin("VDDD", "inout", 60, -380); s.wire((60, -380), (140, -380)); s.label("VDDD", 140, -380, flip=1)
    s.pin("VDDA", "inout", 60, -330); s.wire((60, -330), (140, -330)); s.label("VDDA", 140, -330, flip=1)
    s.pin("VSSA", "inout", 60, 1800); s.wire((60, 1800), (140, 1800)); s.label("VSSA", 140, 1800, flip=1)
    s.pin("VSSD", "inout", 60, 1850); s.wire((60, 1850), (140, 1850)); s.label("VSSD", 140, 1850, flip=1)
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p = K.D
    LS = symbol("/tmp/ls_tmp.sym", "sspll_ls_1v8_3v3", **LS_PINS)
    EXY = symbol(os.path.join(OUT, "sspll_ckg_edges_g.sym"), "sspll_ckg_edges_g", left=[("in", "in")],
                 right=[("stop", "out"), ("pls", "out")], top=[("VDDD", "inout")], bottom=[("VSSD", "inout")])
    symbol(os.path.join(OUT, "sspll_ckg_edges_h.sym"), "sspll_ckg_edges_h", left=[("in", "in")],
           right=[("stop", "out"), ("pls", "out")], top=[("VDDD", "inout")], bottom=[("VSSD", "inout")])
    LXY = symbol(os.path.join(OUT, "sspll_ckg_hlatch.sym"), "sspll_ckg_hlatch", left=[("s", "in"), ("r", "in")],
                 right=[("out", "out")], top=[("VDDD", "inout")], bottom=[("VSSD", "inout")])
    DXY = symbol(os.path.join(OUT, "sspll_ckg_drv5.sym"), "sspll_ckg_drv5", left=[("in", "in")],
                 right=[("o", "out"), ("ob", "out")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    symbol(os.path.join(OUT, "sspll_ckg_drv5t.sym"), "sspll_ckg_drv5t", left=[("in", "in")],
           right=[("o", "out"), ("ob", "out")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    PXY = symbol(os.path.join(OUT, "sspll_ckg_pout5.sym"), "sspll_ckg_pout5", left=[("start", "in"), ("stop", "in")],
                 right=[("o", "out"), ("ob", "out")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    symbol(os.path.join(OUT, "sspll_clkgen_hv.sym"), "sspll_clkgen_hv", left=[("refclk", "in"), ("refhv", "in")],
           right=[("cks", "out"), ("cksb", "out"), ("ckg", "out"), ("ckgb", "out"), ("ckh", "out"), ("ckhb", "out")],
           top=[("VDDD", "inout"), ("VDDA", "inout")], bottom=[("VSSA", "inout"), ("VSSD", "inout")])
    DLXY = symbol(os.path.join(OUT, "sspll_ckg_dly.sym"), "sspll_ckg_dly", left=[("in", "in")], right=[("out", "out")],
                  top=[("VDDD", "inout")], bottom=[("VSSD", "inout")])
    cells = (("sspll_ckg_dly", dly(p)), ("sspll_ckg_edges_g", edges(p, "g")), ("sspll_ckg_edges_h", edges(p, "h")),
             ("sspll_ckg_hlatch", S18.hlatch(p).rename({"VDD": "VDDD", "VSS": "VSSD"})), ("sspll_ckg_drv5", drv5(p, "drv5", "INV5L", "TG5").rename({"VSS": "VSSA"})),
             ("sspll_ckg_drv5t", drv5(p, "drv5t", "INV5T", "TG5T").rename({"VSS": "VSSA"})), ("sspll_ckg_pout5", pout5(p, DXY)),
             ("sspll_clkgen_hv", top(p, LS, EXY, LXY, DXY, PXY, DLXY)))
    for name, sch in cells:
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        print(name, ":", "\n  ".join(errs) or "drawing check clean")
    open(os.path.join(ROOT, "xschem", "netlist", "ref_clkgen_hv.spice"), "w").write(K.lvs_reference())
