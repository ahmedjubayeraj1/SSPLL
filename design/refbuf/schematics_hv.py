#!/usr/bin/env python3
"""schematics_hv.py - 5 V devices, no VDDD: xschem schematics, hierarchical, real wiring, drawing checks:
   sspll_refbuf_hv_rb (5 Mohm self-bias resistor, 10 segments), sspll_refbuf_hv_s1 (first gain stage with its header
   current source), sspll_refbuf_hv (pad divider, AC coupling, S1, S2, 3.3 -> 1.8 V level shifter on VDDD, output NOR,
   enable). Generated from schematics.py (the 13 Nov drawing) with VDDD replaced by VDDD; also writes the LVS reference.
Ground split (24 Nov 2026): pad divider, R_B, S1, S2 (VDDA domain) on VSSA; the 3.3 -> 1.8 V inverter, the output NOR
and the pll_en inverter (VDDD domain) on VSSD, with their own ground rail; the enable level shifter has both."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
from xsch import Sch, symbol
import refbuf as R, refbuf_hv as H
OUT = os.path.join(ROOT, "xschem", "refbuf_hv")
G5N, G5P, N18, P18 = "nfet3_g5v0d10v5", "pfet3_g5v0d10v5", "nfet3_01v8", "pfet3_01v8"
RES = "sky130_fd_pr/res_xhigh_po_0p35.sym"; MIM = "sky130_fd_pr/cap_mim_m3_1.sym"
LS_PINS = dict(left=[("in", "in")], right=[("out", "out"), ("outb", "out")], top=[("VDDD", "inout"), ("VDDA", "inout")],
               bottom=[("VSSA", "inout"), ("VSSD", "inout")])
RB_PINS = dict(left=[("a", "inout")], right=[("b", "inout")], top=[], bottom=[("VSSA", "inout")])
S1_PINS = dict(left=[("vin", "in"), ("ib", "inout"), ("en", "in"), ("enb", "in")], right=[("s1", "out")],
               top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
TOP_PINS = dict(left=[("REF_IN", "inout"), ("ib", "inout"), ("pll_en", "in")], right=[("refclk", "out"), ("refhv", "out")],
                top=[("VDDA", "inout"), ("VDDD", "inout")], bottom=[("VSSA", "inout"), ("VSSD", "inout")])


def M(s, name, kind, x, y, dev, body, mult=1, flip=0):
    return s.mos(name, kind, x, y, dev[1], dev[3], dev[2], body=body, mult=mult, flip=flip)


def rb(q):
    """Serpentine of n segments, 10 per row; odd segments upside down so every link is a short end-to-end wire."""
    s = Sch("sspll_refbuf_hv_rb")
    model, n, L = q["RB_SEG"]
    s.text(f"sspll_refbuf_hv_rb: {n} x res_xhigh_po_0p35 (L = {L} um) in series = 5 Mohm (self-bias feedback of S1)", 40, -330, 0.3)
    s.text("bodies of all segments to VSSA (labels at each body pin)", 40, -290, 0.25)
    per, dx, dy = 10, 260, 260
    s.pin("a", "inout", 60, -160)
    prev = (60, -160)
    for i in range(n):
        row, col = divmod(i, per)
        x = 180 + dx*(col if row % 2 == 0 else per - 1 - col)
        y = -60 + dy*row
        rot = 0 if i % 2 == 0 else 2
        Rr = s.dev(RES, f"XR{i}", x, y, f"L={L} mult=1 model={model} spiceprefix=X", rot=rot)
        if i == 0:
            s.wire(prev, (Rr["P"][0], prev[1]), Rr["P"])
        elif col == 0:                                # row change at the right (odd rows start right) or left end
            side = 1 if row % 2 == 1 else -1
            xx = prev[0] + side*150
            s.wire(prev, (prev[0], prev[1] - 30), (xx, prev[1] - 30), (xx, Rr["P"][1] - 30),
                   (Rr["P"][0], Rr["P"][1] - 30), Rr["P"])
        else:
            yy = prev[1] + (20 if prev[1] > y else -20)
            s.wire(prev, (prev[0], yy), (Rr["P"][0], yy), Rr["P"])
        bx, by = Rr["B"]
        side = -1 if rot == 0 else 1
        s.wire(Rr["B"], (bx + side*20, by)); s.label("VSSA", bx + side*20, by, flip=0 if side < 0 else 1)
        prev = Rr["M"]
    yb = prev[1] - 40 if n % 2 == 0 else prev[1] + 40      # leave the last segment away from its own body
    s.wire(prev, (prev[0], yb), (40, yb)); s.pin("b", "inout", 40, yb)
    yv = -60 + 260*((n - 1)//per) + 160
    s.pin("VSSA", "inout", 40, yv); s.wire((40, yv), (120, yv)); s.label("VSSA", 120, yv, flip=1)
    return s


def s1(p, q):
    s = Sch("sspll_refbuf_hv_s1")
    VD, VS = -300, 340
    s.text("sspll_refbuf_hv_s1: first gain stage. Header XPH (x%d units of the bias diode XPD) feeds the current-reuse"
           " inverter XP1/XN1; C_H (XCH) decouples the header node vh" % p["MH"], 40, -470, 0.3)
    s.text("disabled (en = 0): XPEN turns the header off, XNS1 pulls s1 (and through R_B the input) low", 40, -430, 0.25)
    s.pin("VDDA", "inout", 60, VD); s.wire((60, VD), (950, VD))
    s.pin("VSSA", "inout", 60, VS); s.wire((60, VS), (950, VS))
    PD = M(s, "XPD", G5P, 200, -200, p["PD"], "VDDA")
    s.wire(PD["S"], (PD["S"][0], VD)); s.wire(PD["D"], (PD["D"][0], -120))
    s.wire(PD["G"], (160, PD["G"][1]), (160, -120), (PD["D"][0], -120))
    s.pin("ib", "inout", 60, -120); s.wire((60, -120), (160, -120))
    PE = M(s, "XPEN", G5P, 420, -200, q["PEN"], "VDDA")
    s.wire(PE["S"], (PE["S"][0], VD)); s.wire(PE["D"], (PE["D"][0], -120), (PD["D"][0], -120))
    s.wire(PE["G"], (PE["G"][0] - 30, PE["G"][1])); s.label("en", PE["G"][0] - 30, PE["G"][1])
    PH = M(s, "XPH", G5P, 640, -200, p["PH"], "VDDA", mult=p["MH"])
    s.wire(PH["S"], (PH["S"][0], VD))
    s.wire(PH["G"], (PH["G"][0] - 20, PH["G"][1]), (PH["G"][0] - 20, -120), (PE["D"][0], -120))
    cm, nt, sz = q["CH"]
    CH = s.dev(MIM, "XCH", 850, -200, f"W={sz} L={sz} MF={nt} model={cm} spiceprefix=X", rot=2)
    s.wire(CH["c1"], (CH["c1"][0], VD))
    s.wire(PH["D"], (PH["D"][0], -100), (CH["c0"][0], -100), CH["c0"])
    s.wire((CH["c0"][0], -100), (CH["c0"][0] + 60, -100)); s.label("vh", CH["c0"][0] + 60, -100, flip=1)   # P1 body
    P1 = M(s, "XP1", G5P, 640, 0, p["P1"], "vh"); N1 = M(s, "XN1", G5N, 640, 180, p["N1"], "VSSA")
    s.wire((PH["D"][0], -100), P1["S"]); s.wire(P1["D"], (P1["D"][0], 90), N1["D"]); s.wire(N1["S"], (N1["S"][0], VS))
    s.pin("vin", "in", 60, 90); s.wire((60, 90), (560, 90))
    s.wire(P1["G"], (560, P1["G"][1]), (560, 90), (560, N1["G"][1]), N1["G"])
    s.wire((P1["D"][0], 90), (900, 90), (1000, 90)); s.pin("s1", "out", 1000, 90, flip=1)
    NS = M(s, "XNS1", G5N, 880, 180, q["NS1"], "VSSA")
    s.wire(NS["D"], (NS["D"][0], 90)); s.wire(NS["S"], (NS["S"][0], VS))
    s.wire(NS["G"], (NS["G"][0] - 30, NS["G"][1])); s.label("enb", NS["G"][0] - 30, NS["G"][1])
    s.pin("en", "in", 60, 230); s.wire((60, 230), (140, 230)); s.label("en", 140, 230, flip=1)
    s.pin("enb", "in", 60, 280); s.wire((60, 280), (140, 280)); s.label("enb", 140, 280, flip=1)
    return s


def top(p, q, LS_XY, RB_XY, S1_XY):
    s = Sch("sspll_refbuf_hv")
    VD, VS, VL = -360, 420, -300
    s.text("sspll_refbuf_hv: REF_IN receiver. Pad held at VDDA/2 (XRPU/XRPD), AC coupling C_AC (XCAC), self-biased gain"
           " stage S1 (R_B = xrb), S2 on VDDA, 5 V inverter on VDDD (3.3 -> 1.8 V level shift), output NOR on VDDD", 40, -600, 0.3)
    s.text("refclk rises with REF_IN; pll_en = 0 turns S1 off and holds refclk low. Control nets en / enb / enl "
           "are connected by name", 40, -560, 0.25)
    s.pin("VDDA", "inout", 60, VD); s.wire((60, VD), (1250, VD))
    s.pin("VSSA", "inout", 60, VS); s.wire((60, VS), (1250, VS))                 # VDDA-domain ground
    s.pin("VSSD", "inout", 2500, VS, flip=1); s.wire((1340, VS), (2500, VS))     # VDDD-domain ground (XNL, XNB, XNB2)
    s.pin("REF_IN", "inout", 60, 0)
    RU = s.dev(RES, "XRPU", 200, -120, f"L={q['RPAD'][2]} mult=1 model=res_xhigh_po_0p35 spiceprefix=X")
    RD = s.dev(RES, "XRPD", 280, 120, f"L={q['RPAD'][2]} mult=1 model=res_xhigh_po_0p35 spiceprefix=X")
    s.wire(RU["P"], (200, VD)); s.wire(RU["M"], (200, 0)); s.wire(RD["P"], (280, 0)); s.wire(RD["M"], (280, VS))
    for Rr in (RU, RD):
        s.wire(Rr["B"], (Rr["B"][0] - 20, Rr["B"][1])); s.label("VSSA", Rr["B"][0] - 20, Rr["B"][1])
    cm, nt, sz = q["CAC"]
    CA = s.dev(MIM, "XCAC", 380, 0, f"W={sz} L={sz} MF={nt} model={cm} spiceprefix=X", rot=1)
    s.wire((60, 0), (200, 0), CA["c1"])
    S1 = s.sub("sspll_refbuf_hv_s1.sym", S1_XY, "xs1", 760, 140)
    RB = s.sub("sspll_refbuf_hv_rb.sym", RB_XY, "xrb", 880, -180)
    s.wire(CA["c0"], (500, 0), (500, S1["vin"][1]), S1["vin"])
    s.wire((500, 0), (500, RB["a"][1]), RB["a"])
    s.wire(RB["VSSA"], (RB["VSSA"][0], RB["VSSA"][1] + 20)); s.label("VSSA", RB["VSSA"][0], RB["VSSA"][1] + 20)
    s.wire(S1["VDDA"], (S1["VDDA"][0], VD)); s.wire(S1["VSSA"], (S1["VSSA"][0], VS))
    for nm in ("en", "enb"):
        s.wire(S1[nm], (S1[nm][0] - 60, S1[nm][1])); s.label(nm, S1[nm][0] - 60, S1[nm][1])
    s.pin("ib", "inout", 60, 300); s.wire((60, 300), (620, 300), (620, S1["ib"][1]), S1["ib"])
    XS = 1100
    P2 = M(s, "XP2", G5P, XS, -60, p["P2"], "VDDA"); N2 = M(s, "XN2", G5N, XS, 120, p["N2"], "VSSA")
    s.wire(P2["S"], (P2["S"][0], VD)); s.wire(N2["S"], (N2["S"][0], VS)); s.wire(P2["D"], (P2["D"][0], 30), N2["D"])
    s.wire(S1["s1"], (XS - 80, S1["s1"][1]))
    s.wire(RB["b"], (XS - 80, RB["b"][1]), (XS - 80, S1["s1"][1]))
    s.wire((XS - 80, 30), (XS - 50, 30))
    s.wire(P2["G"], (XS - 50, P2["G"][1]), (XS - 50, 30), (XS - 50, N2["G"][1]), N2["G"])
    XL = 1400
    PL = M(s, "XPL", G5P, XL, -60, p["PL"], "VDDD"); NL = M(s, "XNL", G5N, XL, 120, p["NL"], "VSSD")
    s.wire((P2["D"][0], 30), (XL - 120, 30)); s.wire((XL - 120, 30), (XL - 50, 30))
    # refhv: S2's output brought out for the clock generator's sampling edge (clock-generator design)
    s.wire((XL - 120, 30), (XL - 120, 270), (2500, 270)); s.pin("refhv", "out", 2500, 270, flip=1)
    s.wire(PL["G"], (XL - 50, PL["G"][1]), (XL - 50, 30), (XL - 50, NL["G"][1]), NL["G"])
    s.wire(NL["S"], (NL["S"][0], VS)); s.wire(PL["D"], (PL["D"][0], 30), NL["D"])
    s.wire(PL["S"], (PL["S"][0], VL)); s.wire((PL["S"][0], VL), (2500, VL)); s.pin("VDDD", "inout", 2500, VL, flip=1)
    XB = 1800
    PB = M(s, "XPB", P18, XB, -180, q["PB2"], "VDDD"); PB2 = M(s, "XPB2", P18, XB, -60, q["PB2"], "VDDD")
    NB = M(s, "XNB", N18, XB, 120, p["NB"], "VSSD"); NB2 = M(s, "XNB2", N18, XB + 220, 120, q["NB2"], "VSSD")
    s.wire(PB["S"], (PB["S"][0], VL)); s.wire(PB["D"], PB2["S"])
    s.wire(PB2["D"], (PB2["D"][0], 30), (NB2["D"][0], 30), NB2["D"]); s.wire((PB2["D"][0], 30), NB["D"])
    s.wire(NB["S"], (NB["S"][0], VS)); s.wire(NB2["S"], (NB2["S"][0], VS))
    s.wire((PL["D"][0], 30), (XB - 100, 30))
    s.wire(PB["G"], (XB - 100, PB["G"][1]), (XB - 100, 30), (XB - 100, NB["G"][1]), NB["G"])
    s.wire(PB2["G"], (PB2["G"][0] - 30, PB2["G"][1])); s.label("enl", PB2["G"][0] - 30, PB2["G"][1])
    s.wire(NB2["G"], (NB2["G"][0] - 30, NB2["G"][1])); s.label("enl", NB2["G"][0] - 30, NB2["G"][1])
    s.wire((NB2["D"][0], 30), (2500, 30)); s.pin("refclk", "out", 2500, 30, flip=1)
    # enable: pll_en (1.8 V) -> local inverter on VDDD (enl) and level shifter to 3.3 V (en, enb)
    s.pin("pll_en", "in", 60, 640); s.wire((60, 640), (200, 640))
    LS = s.sub("../cco_hv/sspll_ls_1v8_3v3.sym", LS_XY, "xls", 420, 640)
    s.wire((200, 640), LS["in"])
    s.wire(LS["out"], (LS["out"][0] + 40, LS["out"][1])); s.label("en", LS["out"][0] + 40, LS["out"][1], flip=1)
    s.wire(LS["outb"], (LS["outb"][0] + 40, LS["outb"][1])); s.label("enb", LS["outb"][0] + 40, LS["outb"][1], flip=1)
    s.wire(LS["VDDD"], (LS["VDDD"][0], LS["VDDD"][1] - 20)); s.label("VDDD", LS["VDDD"][0], LS["VDDD"][1] - 20)
    s.wire(LS["VDDA"], (LS["VDDA"][0], LS["VDDA"][1] - 20)); s.label("VDDA", LS["VDDA"][0], LS["VDDA"][1] - 20, flip=1)
    for g in ("VSSA", "VSSD"):
        s.wire(LS[g], (LS[g][0], LS[g][1] + 20)); s.label(g, LS[g][0], LS[g][1] + 20, flip=1 if g == "VSSD" else 0)
    PE = M(s, "XPEI", P18, 1000, 560, q["PEI"], "VDDD"); NE = M(s, "XNEI", N18, 1000, 740, q["NEI"], "VSSD")
    s.wire((200, 640), (200, 820), (900, 820), (900, NE["G"][1]))
    s.wire(PE["G"], (900, PE["G"][1]), (900, NE["G"][1]), NE["G"])
    s.wire(PE["S"], (PE["S"][0], 500)); s.label("VDDD", PE["S"][0], 500, flip=1)
    s.wire(NE["S"], (NE["S"][0], 800)); s.label("VSSD", NE["S"][0], 800, flip=1)
    s.wire(PE["D"], (PE["D"][0], 650), NE["D"]); s.wire((PE["D"][0], 650), (1120, 650)); s.label("enl", 1120, 650, flip=1)
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    LS_XY = symbol("/tmp/ls_tmp.sym", "sspll_ls_1v8_3v3", **LS_PINS)        # pin positions of the CCO symbol
    RB_XY = symbol(os.path.join(OUT, "sspll_refbuf_hv_rb.sym"), "sspll_refbuf_hv_rb", **RB_PINS)
    S1_XY = symbol(os.path.join(OUT, "sspll_refbuf_hv_s1.sym"), "sspll_refbuf_hv_s1", **S1_PINS)
    symbol(os.path.join(OUT, "sspll_refbuf_hv.sym"), "sspll_refbuf_hv", **TOP_PINS)
    for name, sch in (("sspll_refbuf_hv_rb", rb(R.PDK)), ("sspll_refbuf_hv_s1", s1(R.D, R.PDK)),
                      ("sspll_refbuf_hv", top(R.D, R.PDK, LS_XY, RB_XY, S1_XY))):
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        print(name, ":", "\n  ".join(errs) or "drawing check clean")
    open(os.path.join(ROOT, "xschem", "netlist", "ref_refbuf_hv.spice"), "w").write(H.lvs_reference())
