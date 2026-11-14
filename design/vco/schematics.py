#!/usr/bin/env python3
"""schematics.py - step 74 xschem schematics, drawn hierarchically with real wiring:
   sspll_vco_dcell (transistors) -> sspll_vco_core (5 cells in a ring) -> sspll_vco (core + output buffers).
Writes xschem/vco/*.sch and *.sym and runs the drawing checks of tools/xsch.py.  Usage: python3 schematics.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
from xsch import Sch, symbol
OUT = os.path.join(ROOT, "xschem", "vco")


def sym3(model):
    return model.replace("_01v8", "3_01v8")


def dcell(p):
    s = Sch("sspll_vco_dcell")
    XC = 700                                   # mirror axis: the right half is the mirror image of the left half
    VDD, VSS, VT = -320, 300, 230              # rails and the vtune bus
    s.text("sspll_vco_dcell: pseudo-differential delay cell (the ring uses 5)", 40, -520, 0.4)
    s.text("left: inp -> outm   right: inm -> outp   TG1: inp -> outp   TG2: inm -> outm (always on)", 40, -470, 0.25)
    s.text("fine tuning: vtune turns on S, which hangs MOS cap C on the output (higher vtune = lower f)", 40, -440, 0.25)
    s.wire((60, VDD), (XC, VDD), (1340, VDD)); s.wire((60, VSS), (XC, VSS), (1340, VSS)); s.wire((60, VT), (XC, VT), (1340, VT))
    s.pin("VDD", "inout", 60, VDD); s.pin("VSS", "inout", 60, VSS); s.pin("vtune", "in", 60, VT)
    taps = {}
    for side in (0, 1):
        m = (lambda x: x) if side == 0 else (lambda x: 2*XC - x)
        fl, k = side, side + 1
        inn, out = ("inp", "outm") if side == 0 else ("inm", "outp")
        P = s.mos(f"XP{k}", sym3(p["P"][0]), m(220), -200, p["P"][1], p["P"][3], p["P"][2], body="VDD", flip=fl)
        N = s.mos(f"XN{k}", sym3(p["N"][0]), m(220), -60, p["N"][1], p["N"][3], p["N"][2], body="VSS", flip=fl)
        S = s.mos(f"XS{k}", sym3(p["S"][0]), m(480), -60, p["S"][1], p["S"][3], p["S"][2], body="VSS", flip=fl)
        C = s.mos(f"XC{k}", sym3(p["C"][0]), m(480), 110, p["C"][1], p["C"][3], p["C"][2], body="VSS", flip=fl)
        s.wire(P["S"], (P["S"][0], VDD)); s.wire(P["D"], (P["D"][0], -130), N["D"]); s.wire(N["S"], (N["S"][0], VSS))
        gx = m(150)
        s.wire(P["G"], (gx, P["G"][1]), (gx, -130), (gx, N["G"][1]), N["G"])
        s.pin(inn, "in", m(40), -130, flip=fl)
        s.wire((m(40), -130), (gx, -130))
        # output node: inverter drain -> switch drain
        s.wire((P["D"][0], -130), (m(360), -130), (S["D"][0], -130), S["D"])
        # switch gate from the vtune bus
        s.wire(S["G"], (m(420), S["G"][1]), (m(420), VT))
        # switch source -> MOS-cap gate; cap drain and source -> VSS
        s.wire(S["S"], (S["S"][0], 40), (m(440), 40), (m(440), C["G"][1]), C["G"])
        s.wire(C["D"], (C["D"][0], 60), (m(620), 60), (m(620), 160), (m(620), VSS))
        s.wire(C["S"], (C["S"][0], VSS))
        taps[out] = (m(360), -130)
    # transmission gates, below the core: TG1 (inp -> outp) at y = 460, TG2 (inm -> outm) at y = 700
    for k, (src_x, dst, y, side) in enumerate(((40, "outp", 460, 0), (1360, "outm", 700, 1)), start=1):
        m = (lambda x: x) if side == 0 else (lambda x: 2*XC - x)
        fl = side
        TN = s.mos(f"XT{k}N", sym3(p["TN"][0]), m(480), y, p["TN"][1], p["TN"][3], p["TN"][2], body="VSS", flip=fl)
        TP = s.mos(f"XT{k}P", sym3(p["TP"][0]), m(740), y, p["TP"][1], p["TP"][3], p["TP"][2], body="VDD", flip=fl)
        top, bot = y - 50, y + 60
        s.wire(TN["D"], (TN["D"][0], top)); s.wire(TP["S"], (TP["S"][0], top))
        s.wire((src_x, -130), (src_x, top), (TN["D"][0], top), (TP["S"][0], top))
        tx, ty = taps[dst]
        s.wire(TN["S"], (TN["S"][0], bot)); s.wire(TP["D"], (TP["D"][0], bot))
        s.wire((TN["S"][0], bot), (TP["D"][0], bot), (tx, bot), (tx, ty)) if side == 0 else \
            s.wire((TN["S"][0], bot), (TP["D"][0], bot), (tx, bot), (tx, ty))
        # gates: nMOS to VDD, pMOS to VSS (labels next to the gate)
        s.wire(TN["G"], (m(400), TN["G"][1])); s.label("VDD", m(400), TN["G"][1], flip=1 - fl)
        s.wire(TP["G"], (m(660), TP["G"][1])); s.label("VSS", m(660), TP["G"][1], flip=1 - fl)
    s.pin("outm", "out", 360, 820); s.wire((360, 820), (360, 760))
    s.pin("outp", "out", 1040, 820, flip=1); s.wire((1040, 820), (1040, 520))
    return s


DCELL_PINS = dict(left=[("inp", "in"), ("inm", "in")], right=[("outp", "out"), ("outm", "out")],
                  top=[("VDD", "inout")], bottom=[("vtune", "in"), ("VSS", "inout")])
BUF_PINS = dict(left=[("in", "in")], right=[("out", "out")], top=[("VDD", "inout")], bottom=[("VSS", "inout")])
P_NODES = ["vop", "p1", "p2", "p3", "p4"]; M_NODES = ["vom", "m1", "m2", "m3", "m4"]
CORE_PINS = dict(left=[(n, "inout") for n in P_NODES], right=[(n, "inout") for n in M_NODES],
                 top=[("VDD", "inout"), ("vtune", "in")], bottom=[("VSS", "inout")])


def acbuf():
    """AC-coupled self-biased inverter buffer: MIM coupling cap, poly feedback resistor, two inverters."""
    s = Sch("sspll_vco_acbuf")
    VDD, VSS = -260, 440
    s.text("sspll_vco_acbuf: AC-coupled self-biased buffer (one on every ring node, so all nodes see the same load)", 40, -420, 0.35)
    s.text("CC blocks the ring's DC level; RF biases inverter 1 at its trip point; inverter 2 restores full-swing edges", 40, -375, 0.25)
    s.wire((60, VDD), (500, VDD), (840, VDD)); s.wire((60, VSS), (400, VSS), (840, VSS))
    s.pin("VDD", "inout", 60, VDD); s.pin("VSS", "inout", 60, VSS); s.pin("in", "in", 60, -20)
    Cc = s.dev("sky130_fd_pr/cap_mim_m3_1.sym", "XCC", 160, -20, "W=4.2 L=4.2 MF=1 model=cap_mim_m3_1 spiceprefix=X", rot=1)
    s.wire((60, -20), Cc["c1"]); s.wire(Cc["c0"], (260, -20), (320, -20))
    P1 = s.mos("XP1", "pfet3_01v8", 380, -110, 2, 0.15, 1, body="VDD")
    N1 = s.mos("XN1", "nfet3_01v8", 380, 70, 1, 0.15, 1, body="VSS")
    s.wire(P1["S"], (P1["S"][0], VDD)); s.wire(N1["S"], (N1["S"][0], VSS)); s.wire(P1["D"], (P1["D"][0], -20), N1["D"])
    s.wire(P1["G"], (320, P1["G"][1]), (320, -20), (320, N1["G"][1]), N1["G"])
    Rf = s.dev("sky130_fd_pr/res_xhigh_po_0p35.sym", "XRF", 330, 340, "L=39.8 mult=1 model=res_xhigh_po_0p35 spiceprefix=X", rot=3)
    s.wire((260, -20), (260, 340), Rf["P"]); s.wire(Rf["B"], (Rf["B"][0], VSS))
    s.wire((P1["D"][0], -20), (520, -20), (560, -20)); s.wire((520, -20), (520, 340), Rf["M"])
    P2 = s.mos("XP2", "pfet3_01v8", 620, -110, 4, 0.15, 1, body="VDD")
    N2 = s.mos("XN2", "nfet3_01v8", 620, 70, 2, 0.15, 1, body="VSS")
    s.wire(P2["S"], (P2["S"][0], VDD)); s.wire(N2["S"], (N2["S"][0], VSS)); s.wire(P2["D"], (P2["D"][0], -20), N2["D"])
    s.wire(P2["G"], (560, P2["G"][1]), (560, -20), (560, N2["G"][1]), N2["G"])
    s.wire((P2["D"][0], -20), (800, -20)); s.pin("out", "out", 800, -20, flip=1)
    return s


def core():
    """5 delay cells in a ring; stage k drives stage k+1; the last stage feeds back crossed (outp -> inm, outm -> inp),
    which makes the differential loop inverting (it oscillates) while each half keeps an odd inverter count (no latch)."""
    s = Sch("sspll_vco_core")
    VDD, VT, VSS = -200, 200, 240
    s.text("sspll_vco_core: 5-stage pseudo-differential ring (cells x1..x5), fed by the CCO current on VDD", 40, -400, 0.35)
    s.text("the crossed feedback (bottom) closes the ring: x5.outp -> x1.inm (vom), x5.outm -> x1.inp (vop)", 40, -355, 0.25)
    for y, nm, d in ((VDD, "VDD", "inout"), (VT, "vtune", "in"), (VSS, "VSS", "inout")):
        s.wire((200, y), (2000, y)); s.pin(nm, d, 200, y)
    X = [300 + 400*k for k in range(5)]
    cells = [s.sub("sspll_vco_dcell.sym", DCELL_XY, f"x{k + 1}", X[k], 0) for k in range(5)]
    for c in cells:
        s.wire(c["VDD"], (c["VDD"][0], VDD)); s.wire(c["vtune"], (c["vtune"][0], VT)); s.wire(c["VSS"], (c["VSS"][0], VSS))
    for k in range(4):
        a, b = cells[k], cells[k + 1]
        mx = (a["outp"][0] + b["inp"][0])//2
        s.wire(a["outp"], (mx, -20), b["inp"]); s.wire(a["outm"], (mx, 20), b["inm"])
        s.wire((mx, -20), (mx, -110)); s.pin(P_NODES[k + 1], "inout", mx, -110)
        s.wire((mx, 20), (mx, 120)); s.pin(M_NODES[k + 1], "inout", mx, 120)
    a, b = cells[4], cells[0]
    xr = a["outp"][0]
    s.wire(a["outp"], (xr + 100, -20), (xr + 100, 300), (100, 300), (100, 20), (130, 20), b["inm"])
    s.wire(a["outm"], (xr + 60, 20), (xr + 60, 340), (60, 340), (60, -20), (130, -20), b["inp"])
    s.wire((130, -20), (130, -110)); s.pin("vop", "inout", 130, -110)
    s.wire((130, 20), (130, 120)); s.pin("vom", "inout", 130, 120)
    return s


def vco_top():
    """Ring core + one AC-coupled buffer on each of its 10 nodes (equal loading). vop/vom: raw taps to the SSPD;
    clkp/clkm: buffered taps to the dividers and the NCB; the 8 other buffers are dummies."""
    s = Sch("sspll_vco")
    PITCH = 160
    s.text("sspll_vco: ring core + 10 AC-coupled buffers (8 dummies keep every node equally loaded)", 200, -800, 0.35)
    s.text("VDD = ring supply node, fed by the CCO current | VDDBUF = 1.8 V regulated rail | vtune = fine tuning", 200, -755, 0.25)
    core = s.sub("sspll_vco_core.sym", CORE_XY, "xcore", 1000, 0)
    s.wire(core["VDD"], (core["VDD"][0], -520)); s.pin("VDD", "inout", core["VDD"][0], -520)
    s.wire(core["vtune"], (core["vtune"][0], -560)); s.pin("vtune", "in", core["vtune"][0], -560)
    s.wire((420, -640), (1000, -640), (1580, -640)); s.pin("VDDBUF", "inout", 1000, -680); s.wire((1000, -680), (1000, -640))
    s.wire((460, 640), (1000, 640), (1540, 640)); s.pin("VSS", "inout", 1000, 680); s.wire((1000, 680), (1000, 640))
    s.wire(core["VSS"], (core["VSS"][0], 640))
    for side, nodes in ((0, P_NODES), (1, M_NODES)):
        m = (lambda x: x) if side == 0 else (lambda x: 2000 - x)
        xv, xs = m(420), m(460)                         # VDDBUF and VSS verticals of this column
        ys = []
        for k, n in enumerate(nodes):
            cp = core[n]; y = cp[1]
            b = s.sub("sspll_vco_acbuf.sym", BUF_XY, f"xb_{n}", m(700), y, flip=1 - side)
            s.wire(cp, b["in"])
            s.wire(b["VDD"], (b["VDD"][0], y - 60), (xv, y - 60))
            s.wire(b["VSS"], (b["VSS"][0], y + 60), (xs, y + 60))
            ys.append(y)
            if n in ("vop", "vom"):
                s.pin("clkp" if n == "vop" else "clkm", "out", m(560), y, flip=1 - side)
                s.wire(b["out"], (m(560), y))
                s.wire((m(850), y), (m(850), y - 80)); s.pin(n, "out", m(850), y - 80, flip=side)
            else:
                s.wire(b["out"], (m(570), y)); s.label(f"nc_{n}", m(570), y, flip=side)
        s.wire((xv, -640), *[(xv, y - 60) for y in ys])
        s.wire((xs, 640), *[(xs, y + 60) for y in ys[::-1]])
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    import vco
    global DCELL_XY, BUF_XY, CORE_XY
    DCELL_XY = symbol(os.path.join(OUT, "sspll_vco_dcell.sym"), "sspll_vco_dcell", **DCELL_PINS,
                      title="pseudo-diff delay cell")
    BUF_XY = symbol(os.path.join(OUT, "sspll_vco_acbuf.sym"), "sspll_vco_acbuf", **BUF_PINS, title="AC-coupled buffer")
    CORE_XY = symbol(os.path.join(OUT, "sspll_vco_core.sym"), "sspll_vco_core", **CORE_PINS, pitch=160)
    for name, sch in (("sspll_vco_dcell", dcell(vco.FINAL)), ("sspll_vco_acbuf", acbuf()), ("sspll_vco_core", core()),
                      ("sspll_vco", vco_top())):
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        print(name, ":", "\n  ".join(errs) or "drawing check clean")
