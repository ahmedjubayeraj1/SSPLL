#!/usr/bin/env python3
"""schematics.py - step 77 xschem schematics (hierarchical, real wiring, drawing checks):
   sspll_ckg_drv (complementary driver), sspll_ckg_pulse_h / _g (RC pulsers), sspll_clkgen (top)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
from xsch import Sch, symbol
import clkgen as K
OUT = os.path.join(ROOT, "xschem", "clkgen")
N18, P18 = "nfet3_01v8", "pfet3_01v8"
RES = "sky130_fd_pr/res_xhigh_po_0p35.sym"; MIM = "sky130_fd_pr/cap_mim_m3_1.sym"
DRV_PINS = dict(left=[("in", "in")], right=[("o", "out"), ("ob", "out")], top=[("VDD", "inout")], bottom=[("VSS", "inout")])
PUL_PINS = dict(left=[("in", "in")], right=[("out", "out")], top=[("VDD", "inout")], bottom=[("VSS", "inout")])


def rails(s, x, y_top, y_bot):
    s.label("VDD", x, y_top); s.label("VSS", x, y_bot)


def inverter(s, name, x, y, size):
    """pMOS over nMOS; returns the input point (on the gate tie) and the output point (on the drain tie)."""
    n, p = size
    P = s.mos(name + "P", P18, x, y - 80, p[1], p[3], p[2], body="VDD")
    N = s.mos(name + "N", N18, x, y + 80, n[1], n[3], n[2], body="VSS")
    s.wire(P["D"], N["D"])
    s.wire(P["G"], (x - 60, P["G"][1]), (x - 60, N["G"][1]), N["G"])
    s.wire(P["S"], (P["S"][0], P["S"][1] - 30)); s.label("VDD", P["S"][0], P["S"][1] - 30)
    s.wire(N["S"], (N["S"][0], N["S"][1] + 30)); s.label("VSS", N["S"][0], N["S"][1] + 30)
    return (x - 60, y), (P["D"][0], y)


def nor2(s, name, x, y, size):
    """NOR2: pMOS in series (a on top), nMOS in parallel. Returns input points a, b and the output point."""
    n, p = size
    PA = s.mos(name + "PA", P18, x, y - 180, p[1], p[3], p[2], body="VDD")
    PB = s.mos(name + "PB", P18, x, y - 70, p[1], p[3], p[2], body="VDD")
    NA = s.mos(name + "NA", N18, x, y + 90, n[1], n[3], n[2], body="VSS")
    NB = s.mos(name + "NB", N18, x + 260, y + 90, n[1], n[3], n[2], body="VSS")
    s.wire(PA["D"], PB["S"]); s.wire(PB["D"], NA["D"])
    s.wire((PB["D"][0], y + 20), (NB["D"][0], y + 20), NB["D"])
    s.wire(PA["S"], (PA["S"][0], PA["S"][1] - 30)); s.label("VDD", PA["S"][0], PA["S"][1] - 30)
    for M_ in (NA, NB):
        s.wire(M_["S"], (M_["S"][0], M_["S"][1] + 30)); s.label("VSS", M_["S"][0], M_["S"][1] + 30)
    s.wire(PA["G"], (x - 100, PA["G"][1]), (x - 100, NA["G"][1]), NA["G"])                      # input a
    s.wire(PB["G"], (x - 60, PB["G"][1]), (x - 60, y + 190), (NB["G"][0] - 40, y + 190),
           (NB["G"][0] - 40, NB["G"][1]), NB["G"])                                              # input b
    return (x - 100, y - 120), (x - 60, y + 150), (PB["D"][0], y)


def drv(p):
    s = Sch("sspll_ckg_drv")
    s.text("sspll_ckg_drv: o follows in through 2 inverters, ob is inverted through 3; the last stage of each drives "
           "the switch gates", 40, -380, 0.3)
    s.pin("in", "in", 60, 0)
    ia, oa = inverter(s, "XA", 300, 0, p["INVS"]); ib, ob_ = inverter(s, "XB", 560, 0, p["INVL"])
    ic, oc = inverter(s, "XC", 300, 420, p["INVS"]); id_, od = inverter(s, "XD", 560, 420, p["INVM"])
    ie, oe = inverter(s, "XE", 820, 420, p["INVL"])
    s.wire((60, 0), ia); s.wire((140, 0), (140, 420), ic)
    s.wire(oa, ib); s.wire(oc, id_); s.wire(od, ie)
    s.wire(ob_, (1000, 0)); s.pin("o", "out", 1000, 0, flip=1)
    s.wire(oe, (1000, 420)); s.pin("ob", "out", 1000, 420, flip=1)
    s.pin("VDD", "inout", 60, -300); s.wire((60, -300), (140, -300)); s.label("VDD", 140, -300, flip=1)
    s.pin("VSS", "inout", 60, 700); s.wire((60, 700), (140, 700)); s.label("VSS", 140, 700, flip=1)
    return s


def pulser(p, nm):
    R, C = ("RH", "CH") if nm == "h" else ("RG", "CG")
    rm, _, _, L = p[R]; cm, cw, _, cl = p[C]
    s = Sch(f"sspll_ckg_pulse_{nm}")
    s.text(f"sspll_ckg_pulse_{nm}: out = in AND NOT(in delayed by XR-XC) = NOR(inb, dly): one positive pulse per "
           f"rising edge of in (R: L = {L} um, C: {cw} x {cl} um)", 40, -560, 0.3)
    s.pin("in", "in", 60, 0)
    i2, o2 = inverter(s, "X2", 300, 0, p["INVS"])                       # drives the RC
    Rr = s.dev(RES, "XR", 460, 0, f"L={L} mult=1 model={rm} spiceprefix=X", rot=3)
    Cc = s.dev(MIM, "XC", 600, 90, f"W={cw} L={cl} MF=1 model={cm} spiceprefix=X")
    i3, o3 = inverter(s, "X3", 800, 0, p["INVS"])                       # restores the edge: dly
    i1, o1 = inverter(s, "X1", 300, 480, p["INVS"])                     # inb
    s.wire((60, 0), i2); s.wire((140, 0), (140, 480), i1)
    s.wire(o2, Rr["P"] if Rr["P"][0] < Rr["M"][0] else Rr["M"])
    rc_end = Rr["M"] if Rr["P"][0] < Rr["M"][0] else Rr["P"]
    s.wire(rc_end, (Cc["c0"][0], rc_end[1]), i3)
    s.wire((Cc["c0"][0], rc_end[1]), Cc["c0"])
    s.wire(Cc["c1"], (Cc["c1"][0], Cc["c1"][1] + 30)); s.label("VSS", Cc["c1"][0], Cc["c1"][1] + 30)
    s.wire(Rr["B"], (Rr["B"][0], Rr["B"][1] - 30)); s.label("VSS", Rr["B"][0], Rr["B"][1] - 30)
    a, b, o = nor2(s, "X4", 1260, 300, p["NOR"])
    s.wire(o1, (1100, 480), (1100, a[1]), a)                             # inb -> a
    s.wire(o3, (1000, 0), (1000, 450), (1120, 450), (1120, b[1]), b)       # dly -> b
    s.wire(o, (1660, 300)); s.pin("out", "out", 1660, 300, flip=1)
    s.pin("VDD", "inout", 60, -400); s.wire((60, -400), (140, -400)); s.label("VDD", 140, -400, flip=1)
    s.pin("VSS", "inout", 60, 760); s.wire((60, 760), (140, 760)); s.label("VSS", 140, 760, flip=1)
    return s


def top(p, DXY, PXY):
    s = Sch("sspll_clkgen")
    s.text("sspll_clkgen: refclk (step 76) -> sampling pair cks/cksb (sw1 samples at the refclk rising edge), hold "
           "pulse ckh/ckhb (sw2), Gm pulse ckg/ckgb (tau = 200 ps, t_p ~ 2.6 ns after the sampling edge)", 40, -460, 0.3)
    s.text("all devices 1.8 V core (VDD = VDDL, the regulated rail); supplies of the sub-cells connected by name", 40, -420, 0.25)
    s.pin("refclk", "in", 60, 0)
    i0, o0 = inverter(s, "XI0", 260, 0, p["INVM"]); i1, o1 = inverter(s, "XI1", 520, 0, p["INVM"])
    s.wire((60, 0), i0); s.wire(o0, i1)
    DS = s.sub("sspll_ckg_drv.sym", DXY, "xds", 1100, 0)
    s.wire(o1, (640, 0), DS["in"])
    # row 2: gap 1, hold pulser, hold driver
    j2, q2 = inverter(s, "XI2", 260, 560, p["INVS"]); j3, q3 = inverter(s, "XI3", 520, 560, p["INVS"])
    s.wire((640, 0), (640, 280), (160, 280), (160, 560), j2); s.wire(q2, j3)
    PH = s.sub("sspll_ckg_pulse_h.sym", PXY, "xph", 820, 560)
    DH = s.sub("sspll_ckg_drv.sym", DXY, "xdh", 1240, 560)
    s.wire(q3, PH["in"]); s.wire(PH["out"], (1020, PH["out"][1]), (1020, DH["in"][1]), DH["in"])
    # row 3: gap 2, Gm pulser, Gm driver
    j4, q4 = inverter(s, "XI4", 260, 1120, p["INVS"]); j5, q5 = inverter(s, "XI5", 520, 1120, p["INVS"])
    j6, q6 = inverter(s, "XI6", 780, 1120, p["INVS"])
    s.wire((1020, PH["out"][1]), (1020, 840), (160, 840), (160, 1120), j4)
    s.wire(q4, j5); s.wire(q5, j6)
    PG = s.sub("sspll_ckg_pulse_g.sym", {k: v for k, v in PXY.items()}, "xpg", 1080, 1120)
    DG = s.sub("sspll_ckg_drv.sym", DXY, "xdg", 1500, 1120)
    s.wire(q6, PG["in"]); s.wire(PG["out"], DG["in"])
    for D_, a, b in ((DS, "cksb", "cks"), (DH, "ckh", "ckhb"), (DG, "ckg", "ckgb")):
        s.wire(D_["o"], (1900, D_["o"][1])); s.pin(a, "out", 1900, D_["o"][1], flip=1)
        s.wire(D_["ob"], (1900, D_["ob"][1])); s.pin(b, "out", 1900, D_["ob"][1], flip=1)
    for X in (DS, DH, DG, PH, PG):
        s.wire(X["VDD"], (X["VDD"][0], X["VDD"][1] - 20)); s.label("VDD", X["VDD"][0], X["VDD"][1] - 20)
        s.wire(X["VSS"], (X["VSS"][0], X["VSS"][1] + 20)); s.label("VSS", X["VSS"][0], X["VSS"][1] + 20)
    s.pin("VDD", "inout", 60, -320); s.wire((60, -320), (140, -320)); s.label("VDD", 140, -320, flip=1)
    s.pin("VSS", "inout", 60, 1400); s.wire((60, 1400), (140, 1400)); s.label("VSS", 140, 1400, flip=1)
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    DXY = symbol(os.path.join(OUT, "sspll_ckg_drv.sym"), "sspll_ckg_drv", **DRV_PINS)
    PXY = symbol(os.path.join(OUT, "sspll_ckg_pulse_h.sym"), "sspll_ckg_pulse_h", **PUL_PINS)
    symbol(os.path.join(OUT, "sspll_ckg_pulse_g.sym"), "sspll_ckg_pulse_g", **PUL_PINS)
    symbol(os.path.join(OUT, "sspll_clkgen.sym"), "sspll_clkgen", left=[("refclk", "in")],
           right=[("cks", "out"), ("cksb", "out"), ("ckh", "out"), ("ckhb", "out"), ("ckg", "out"), ("ckgb", "out")],
           top=[("VDD", "inout")], bottom=[("VSS", "inout")])
    for name, sch in (("sspll_ckg_drv", drv(K.D)), ("sspll_ckg_pulse_h", pulser(K.D, "h")),
                      ("sspll_ckg_pulse_g", pulser(K.D, "g")), ("sspll_clkgen", top(K.D, DXY, PXY))):
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        print(name, ":", "\n  ".join(errs) or "drawing check clean")
