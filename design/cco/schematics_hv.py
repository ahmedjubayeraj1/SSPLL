#!/usr/bin/env python3
"""schematics_hv.py - step 75 redo (5 V CCO for the 3-stage 5 V ring, 800 MHz): xschem schematics (hierarchical,
real wiring, drawing checks), generated from schematics.py (the 1.6 GHz drawing) with these changes:
   sspll_cco_hv_dac (13 base units), sspll_cco_hv_rf (10 Mohm, body on VDDA), sspll_cco_hv_rcas (cascode-bias filter,
   8 segments, body on VDDA), sspll_cco_hv (mirror x17 with a VDDA-tracking cascode, no clamp, no VDDL);
   the level shifter sspll_ls_1v8_3v3 is the same cell.
Ground split (24 Nov 2026): every 5 V device returns to VSSA; the level shifter's thin-oxide input inverter to VSSD
(its own short rail and pin), so the level shifter and the top cell have both grounds."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
from xsch import Sch, symbol
import cco_hv as cco
OUT = os.path.join(ROOT, "xschem", "cco_hv")
G5N, G5P, N18, P18 = "nfet3_g5v0d10v5", "pfet3_g5v0d10v5", "nfet3_01v8", "pfet3_01v8"
RES = "sky130_fd_pr/res_xhigh_po_0p35.sym"; MIM = "sky130_fd_pr/cap_mim_m3_1.sym"
LS_PINS = dict(left=[("in", "in")], right=[("out", "out"), ("outb", "out")], top=[("VDDD", "inout"), ("VDDA", "inout")],
               bottom=[("VSSA", "inout"), ("VSSD", "inout")])
DAC_PINS = dict(left=[("ibias", "inout"), ("en", "in"), ("c0", "in"), ("c1", "in"), ("c2", "in"), ("c3", "in"),
                      ("c4", "in")], right=[("vgr", "inout")], top=[], bottom=[("VSSA", "inout")])
RF_PINS = dict(left=[("a", "inout")], right=[("b", "inout")], top=[], bottom=[("VB", "inout")])


def ls():
    s = Sch("sspll_ls_1v8_3v3")
    VDDT, VSS = -300, 320
    s.text("sspll_ls_1v8_3v3: 1.8 V -> 3.3 V level shifter (out = in, outb = not in)", 40, -460, 0.35)
    s.text("input inverter on VDDD / VSSD (thin oxide) | cross-coupled thick-oxide latch and output inverters on VDDA / VSSA", 40, -415, 0.25)
    s.wire((60, VDDT), (300, VDDT)); s.pin("VDDD", "inout", 60, VDDT)
    s.wire((460, VDDT), (1720, VDDT)); s.pin("VDDA", "inout", 1720, VDDT, flip=1)
    s.wire((60, VSS), (300, VSS)); s.pin("VSSD", "inout", 60, VSS)                         # input inverter's ground
    s.wire((460, VSS), (900, VSS), (1720, VSS)); s.pin("VSSA", "inout", 1720, VSS, flip=1)  # 5 V devices' ground
    PI = s.mos("XPI", P18, 200, -140, 1, 0.15, 1, body="VDDD"); NI = s.mos("XNI", N18, 200, 40, 0.5, 0.15, 1, body="VSSD")
    s.wire(PI["S"], (PI["S"][0], VDDT)); s.wire(NI["S"], (NI["S"][0], VSS)); s.wire(PI["D"], (PI["D"][0], -50), NI["D"])
    s.wire(PI["G"], (150, PI["G"][1]), (150, -50), (150, NI["G"][1]), NI["G"])
    s.pin("in", "in", 40, -50); s.wire((40, -50), (150, -50))
    P1 = s.mos("XP1", G5P, 560, -140, 1, 0.5, 1, body="VDDA"); P2 = s.mos("XP2", G5P, 1000, -140, 1, 0.5, 1, body="VDDA", flip=1)
    N1 = s.mos("XN1", G5N, 560, 40, 3, 0.5, 1, body="VSSA"); N2 = s.mos("XN2", G5N, 1000, 40, 3, 0.5, 1, body="VSSA", flip=1)
    for d in (P1, P2):
        s.wire(d["S"], (d["S"][0], VDDT))
    for d in (N1, N2):
        s.wire(d["S"], (d["S"][0], VSS))
    s.wire(P1["D"], N1["D"])          # node x (column 580): one straight segment, so wires can cross it
    s.wire(P2["D"], N2["D"])          # node y (column 980)
    # cross coupling: x -> XP2 gate, y -> XP1 gate
    s.wire((P1["D"][0], -80), (1060, -80), (1490, -80)); s.wire((1060, -80), (1060, P2["G"][1]), P2["G"])
    s.wire((P2["D"][0], -40), (500, -40), (500, P1["G"][1]), P1["G"])     # y -> XP1 gate, crossing node x
    s.wire((P2["D"][0], -20), (1190, -20))
    # in -> XN1 gate (below), inb -> XN2 gate (below)
    s.wire((40, -50), (40, 240), (520, 240), (520, N1["G"][1]), N1["G"])
    s.wire((PI["D"][0], -50), (340, -50), (340, 200), (1080, 200), (1080, N2["G"][1]), N2["G"])
    # output inverters: outb = not y (at 1250), out = not x (at 1550)
    for nm, xg, xc, node_y, pin, px in (("B", 1190, 1250, -20, "outb", 1400), ("O", 1490, 1550, -80, "out", 1700)):
        P = s.mos(f"XP{nm}", G5P, xc, -140, 2, 0.5, 1, body="VDDA"); N = s.mos(f"XN{nm}", G5N, xc, 40, 1, 0.5, 1, body="VSSA")
        s.wire(P["S"], (P["S"][0], VDDT)); s.wire(N["S"], (N["S"][0], VSS)); s.wire(P["D"], (P["D"][0], -50), N["D"])
        s.wire(P["G"], (xg, P["G"][1]), (xg, node_y), (xg, N["G"][1]), N["G"])
        s.wire((P["D"][0], -50), (px, -50)); s.pin(pin, "out", px, -50, flip=1)
    return s


def dac(p):
    s = Sch("sspll_cco_hv_dac")
    VGR, VSS, IB = -200, 260, 170
    s.text("sspll_cco_hv_dac: unit current sinks (2.5 uA each at IBIAS = 5 uA) switched into vgr", 40, -420, 0.35)
    s.text(f"base: {p['NBASE']} units (switch = en) | binary: 1, 2, 4, 8, 16 units (switches = c0..c4) | 3.3 V devices", 40, -375, 0.25)
    s.pin("ibias", "inout", 60, 0); s.pin("VSSA", "inout", 60, VSS); s.wire((60, VSS), (1900, VSS))
    D = s.mos("XNB", G5N, 220, 60, p["UN"][1], p["UN"][3], p["UN"][2], body="VSSA", mult=2)
    s.wire((60, 0), (160, 0), (240, 0), D["D"])
    s.wire((160, 0), (160, D["G"][1]), D["G"]); s.wire(D["S"], (D["S"][0], VSS))
    names = ["en", "c0", "c1", "c2", "c3", "c4"]; mults = [p["NBASE"]] + [2**k for k in range(5)]
    xs = [460 + 280*k for k in range(6)]
    s.wire((160, D["G"][1]), (160, IB), *[(x - 50, IB) for x in xs])
    for k, (x, nm, m) in enumerate(zip(xs, names, mults)):
        S = s.mos(f"XS{k}", G5N, x, -60, p["SW"][1], p["SW"][3], p["SW"][2], body="VSSA", mult=m)
        U = s.mos(f"XU{k}", G5N, x, 90, p["UN"][1], p["UN"][3], p["UN"][2], body="VSSA", mult=m)
        s.wire(S["D"], (S["D"][0], VGR)); s.wire(S["S"], U["D"]); s.wire(U["S"], (U["S"][0], VSS))
        s.wire(U["G"], (x - 50, U["G"][1]), (x - 50, IB))
        s.wire(S["G"], (x - 50, S["G"][1]), (x - 50, -130)); s.pin(nm, "in", x - 50, -130)
    s.wire((xs[0] + 20, VGR), (xs[-1] + 20, VGR), (1900, VGR)); s.pin("vgr", "inout", 1900, VGR, flip=1)
    return s


def rf(p, key="RSEG", cell="sspll_cco_hv_rf", what="10 Mohm (gate filter of the output mirror)"):
    """Segments in a serpentine: odd segments are drawn upside down (rot 2) so every series link is a short
    wire between neighbouring ends (bottom-bottom, top-top) that never passes over a resistor."""
    s = Sch(cell)
    model, n, L = p[key]
    s.text(f"{cell}: {n} x res_xhigh_po_0p35 (L = {L} um) in series = {what}", 40, -330, 0.3)
    s.text("bodies of all segments to VB (pin; VDDA in the CCO: the serpentine sits on an n-well tied to VDDA)", 40, -290, 0.25)
    per, dx = min(10, n), 260
    s.pin("a", "inout", 60, -160)
    prev = (60, -160)
    for i in range(n):
        row, col = divmod(i, per)
        x = 180 + dx*col if row == 0 else 180 + dx*(per - 1 - col)
        y = -60 if row == 0 else 200
        rot = 0 if i % 2 == 0 else 2
        R = s.dev(RES, f"XR{i}", x, y, f"L={L} mult=1 model={model} spiceprefix=X", rot=rot)
        if i == 0:
            s.wire(prev, (R["P"][0], prev[1]), R["P"])
        elif i == per:                                   # row change: around the right end, clear of the last body label
            s.wire(prev, (prev[0], prev[1] - 30), (prev[0] + 150, prev[1] - 30), (prev[0] + 150, R["P"][1] - 30),
                   (R["P"][0], R["P"][1] - 30), R["P"])
        else:
            yy = prev[1] + (20 if prev[1] > y else -20)
            s.wire(prev, (prev[0], yy), (R["P"][0], yy), R["P"])
        bx, by = R["B"]
        side = -1 if rot == 0 else 1
        s.wire(R["B"], (bx + side*20, by)); s.label("VB", bx + side*20, by, flip=0 if side < 0 else 1)
        prev = R["M"]
    s.wire(prev, (prev[0], prev[1] - 30), (60, prev[1] - 30)); s.pin("b", "inout", 60, prev[1] - 30)
    s.pin("VB", "inout", 60, 380); s.wire((60, 380), (120, 380)); s.label("VB", 120, 380, flip=1)
    return s


def cco_top(p):
    s = Sch("sspll_cco_hv")
    VDDA_Y, VSS_Y = -400, 420
    s.text("sspll_cco_hv: current-fed supply of the 5 V ring VCO (every analog device 5 V-rated, g5v0d10v5)", 40, -620, 0.35)
    s.text("IBIAS -> DAC (cco_code) -> MREF diode -> 10 Mohm / 10.9 pF filter -> MOUT (x17) -> cascode MC (x17) -> ring node vring;"
           " VTEST injects a test tone", 40, -575, 0.25)
    s.text("cascode gate vcas = VDDA - V_SG(MB), RC-filtered and held to VDDA by CCAS: MOUT's drain follows VDDA -> low K_vdd;"
           " control bits are level-shifted from VDDD (left column) and connected by name", 40, -545, 0.25)
    ins = [("code0", "c0"), ("code1", "c1"), ("code2", "c2"), ("code3", "c3"), ("code4", "c4"), ("pll_en", "en"),
           ("vtest_en", "vt")]
    for k, (pin, net) in enumerate(ins):
        y = -380 + 200*k
        L = s.sub("sspll_ls_1v8_3v3.sym", LS_XY, f"xls_{net}", 300, y)
        s.pin(pin, "in", 100, y); s.wire((100, y), L["in"])
        s.wire(L["out"], (L["out"][0] + 40, L["out"][1])); s.label(net, L["out"][0] + 40, L["out"][1], flip=1)
        s.wire(L["outb"], (L["outb"][0] + 40, L["outb"][1])); s.label(net + "b", L["outb"][0] + 40, L["outb"][1], flip=1)
        for sup in ("VDDD", "VDDA"):
            s.wire(L[sup], (L[sup][0], L[sup][1] - 20)); s.label(sup, L[sup][0], L[sup][1] - 20, flip=1 if sup == "VDDA" else 0)
        for g in ("VSSA", "VSSD"):
            s.wire(L[g], (L[g][0], L[g][1] + 20)); s.label(g, L[g][0], L[g][1] + 20, flip=1 if g == "VSSD" else 0)
    s.wire((1150, VDDA_Y), (2000, VDDA_Y), (2750, VDDA_Y)); s.pin("VDDA", "inout", 1150, VDDA_Y)
    s.wire((1150, VSS_Y), (2000, VSS_Y), (2750, VSS_Y)); s.pin("VSSA", "inout", 1150, VSS_Y)
    s.pin("VDDD", "inout", 100, 1080); s.wire((100, 1080), (220, 1080)); s.label("VDDD", 220, 1080, flip=1)
    s.pin("VSSD", "inout", 100, 1130); s.wire((100, 1130), (220, 1130)); s.label("VSSD", 220, 1130, flip=1)
    Dc = s.sub("sspll_cco_hv_dac.sym", DAC_XY, "xdac", 900, 450)
    s.pin("ibias", "inout", 640, 250); s.wire((640, 250), (700, 250), (700, Dc["ibias"][1]), Dc["ibias"])
    for nm in ("en", "c0", "c1", "c2", "c3", "c4"):
        s.wire(Dc[nm], (Dc[nm][0] - 40, Dc[nm][1])); s.label(nm, Dc[nm][0] - 40, Dc[nm][1])
    s.wire(Dc["VSSA"], (Dc["VSSA"][0], 680)); s.label("VSSA", Dc["VSSA"][0], 680)
    NEN = s.mos("XNEN", G5N, 760, 150, p["NEN"][1], p["NEN"][3], p["NEN"][2], body="VSSA")
    s.wire(NEN["D"], (NEN["D"][0], 100), (700, 100), (700, 250)); s.wire(NEN["S"], (NEN["S"][0], 210)); s.label("VSSA", NEN["S"][0], 210)
    s.wire(NEN["G"], (NEN["G"][0] - 30, NEN["G"][1])); s.label("enb", NEN["G"][0] - 30, NEN["G"][1])
    # mirror: MREF diode, filter, MOUT, cascode MC
    MR = s.mos("XMREF", G5P, 1300, -200, p["UP"][1], p["UP"][3], p["UP"][2], body="VDDA")
    MO = s.mos("XMOUT", G5P, 1700, -200, p["UP"][1], p["UP"][3], p["UP"][2], body="VDDA", mult=p["NOUT"])
    MC = s.mos("XMC", G5P, 1700, 60, p["CASC"][1], p["CASC"][3], p["CASC"][2], body="VDDA", mult=p["NOUT"])
    s.wire(MR["S"], (MR["S"][0], VDDA_Y)); s.wire(MO["S"], (MO["S"][0], VDDA_Y))
    s.wire(MR["G"], (1260, MR["G"][1]), (1260, -120), (MR["D"][0], -120)); s.wire(MR["D"], (MR["D"][0], -120))
    s.wire((MR["D"][0], -120), (MR["D"][0], 40), (MR["D"][0], Dc["vgr"][1]), Dc["vgr"])
    RF = s.sub("sspll_cco_hv_rf.sym", RF_XY, "xrf", 1500, 40)
    s.wire((MR["D"][0], 40), RF["a"]); s.wire(RF["VB"], (RF["VB"][0], 140)); s.label("VDDA", RF["VB"][0], 140)
    s.wire(RF["b"], (1640, 40), (1640, -60), (1640, MO["G"][1]), MO["G"])
    CF = s.dev(MIM, "XCF", 1500, -110, f"W=30 L=30 MF={p['CTILE'][1]} model=cap_mim_m3_1 spiceprefix=X", rot=2)
    s.wire(CF["c1"], (1500, VDDA_Y)); s.wire(CF["c0"], (1500, -60), (1640, -60))
    PEN = s.mos("XPEN", G5P, 1950, -300, p["PEN"][1], p["PEN"][3], p["PEN"][2], body="VDDA")
    s.wire(PEN["S"], (PEN["S"][0], VDDA_Y)); s.wire(PEN["D"], (PEN["D"][0], -250), (1640, -250), (1640, MO["G"][1]))
    s.wire(PEN["G"], (PEN["G"][0] - 30, PEN["G"][1])); s.label("en", PEN["G"][0] - 30, PEN["G"][1])
    s.wire(MO["D"], MC["S"])                                     # node vc: MOUT drain = cascode source
    s.wire(MC["G"], (MC["G"][0] - 30, MC["G"][1])); s.label("vcas", MC["G"][0] - 30, MC["G"][1])
    # ring node (y = 200)
    RY = 200
    s.wire(MC["D"], (MC["D"][0], RY), (2530, RY), (2750, RY)); s.pin("vring", "inout", 2750, RY, flip=1)
    # cascode bias: MB diode from VDDA, KB DAC units (switch = en), RC filter (8 segments), CCAS to VDDA
    MB = s.mos("XMB", G5P, 1950, 560, p["MB"][1], p["MB"][3], p["MB"][2], body="VDDA")
    SB = s.mos("XSB", G5N, 1950, 700, p["SW"][1], p["SW"][3], p["SW"][2], body="VSSA", mult=p["KB"])
    UB = s.mos("XUB", G5N, 1950, 840, p["UN"][1], p["UN"][3], p["UN"][2], body="VSSA", mult=p["KB"])
    s.wire(MB["S"], (MB["S"][0], MB["S"][1] - 20)); s.label("VDDA", MB["S"][0], MB["S"][1] - 20, flip=1)
    s.wire(MB["D"], (MB["D"][0], 610), (MB["D"][0], 640), SB["D"])
    s.wire(MB["G"], (1900, MB["G"][1]), (1900, 610), (MB["D"][0], 610))
    s.wire(SB["G"], (SB["G"][0] - 30, SB["G"][1])); s.label("en", SB["G"][0] - 30, SB["G"][1])
    s.wire(SB["S"], UB["D"])
    s.wire(UB["G"], (UB["G"][0] - 30, UB["G"][1])); s.label("ibias", UB["G"][0] - 30, UB["G"][1])
    s.wire(UB["S"], (UB["S"][0], UB["S"][1] + 20)); s.label("VSSA", UB["S"][0], UB["S"][1] + 20)
    RC = s.sub("sspll_cco_hv_rcas.sym", RC_XY, "xrcas", 2250, 620)
    s.wire((MB["D"][0], 640), (2100, 640), (2100, RC["a"][1]), RC["a"])
    s.wire(RC["VB"], (RC["VB"][0], RC["VB"][1] + 20)); s.label("VDDA", RC["VB"][0], RC["VB"][1] + 20)
    s.wire(RC["b"], (RC["b"][0] + 40, RC["b"][1])); s.label("vcas", RC["b"][0] + 40, RC["b"][1], flip=1)
    CC = s.dev(MIM, "XCCAS", 2600, 720, f"W={p['CCAS'][2]} L={p['CCAS'][2]} MF={p['CCAS'][1]} model=cap_mim_m3_1 spiceprefix=X", rot=2)
    s.wire(CC["c1"], (CC["c1"][0], CC["c1"][1] - 30)); s.label("VDDA", CC["c1"][0], CC["c1"][1] - 30, flip=1)
    s.wire(CC["c0"], (CC["c0"][0], CC["c0"][1] + 30)); s.label("vcas", CC["c0"][0], CC["c0"][1] + 30, flip=1)
    # VTEST injection: TG + 20 kOhm
    TN = s.mos("XTGN", G5N, 2400, -250, p["TGN"][1], p["TGN"][3], p["TGN"][2], body="VSSA")
    TP = s.mos("XTGP", G5P, 2620, -250, p["TGP"][1], p["TGP"][3], p["TGP"][2], body="VDDA")
    s.wire(TN["D"], (TN["D"][0], -310)); s.wire(TP["S"], (TP["S"][0], -310)); s.wire((TN["D"][0], -310), (TP["S"][0], -310), (2750, -310))
    s.pin("vtest", "in", 2750, -310, flip=1)
    s.wire(TN["S"], (TN["S"][0], -180)); s.wire(TP["D"], (TP["D"][0], -180)); s.wire((TN["S"][0], -180), (2530, -180), (TP["D"][0], -180))
    s.wire(TN["G"], (TN["G"][0] - 30, TN["G"][1])); s.label("vt", TN["G"][0] - 30, TN["G"][1])
    s.wire(TP["G"], (TP["G"][0] - 30, TP["G"][1])); s.label("vtb", TP["G"][0] - 30, TP["G"][1])
    RI = s.dev(RES, "XRINJ", 2530, -90, f"L={p['RINJ'][2]} mult=1 model=res_xhigh_po_0p35 spiceprefix=X")
    s.wire((2530, -180), RI["P"]); s.wire(RI["M"], (2530, RY)); s.wire(RI["B"], (RI["B"][0] - 20, RI["B"][1])); s.label("VSSA", RI["B"][0] - 20, RI["B"][1])
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    global LS_XY, DAC_XY, RF_XY, RC_XY
    LS_XY = symbol(os.path.join(OUT, "sspll_ls_1v8_3v3.sym"), "sspll_ls_1v8_3v3", **LS_PINS)
    DAC_XY = symbol(os.path.join(OUT, "sspll_cco_hv_dac.sym"), "sspll_cco_hv_dac", **DAC_PINS)
    RF_XY = symbol(os.path.join(OUT, "sspll_cco_hv_rf.sym"), "sspll_cco_hv_rf", **RF_PINS)
    RC_XY = symbol(os.path.join(OUT, "sspll_cco_hv_rcas.sym"), "sspll_cco_hv_rcas", **RF_PINS)
    for name, sch in (("sspll_ls_1v8_3v3", ls()), ("sspll_cco_hv_dac", dac(cco.D)), ("sspll_cco_hv_rf", rf(cco.D)),
                      ("sspll_cco_hv_rcas", rf(cco.D, "RCAS", "sspll_cco_hv_rcas", "4 Mohm (cascode-bias filter)")),
                      ("sspll_cco_hv", cco_top(cco.D))):
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        print(name, ":", "\n  ".join(errs) or "drawing check clean")
