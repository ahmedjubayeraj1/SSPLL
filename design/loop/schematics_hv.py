#!/usr/bin/env python3
"""schematics_hv.py - step 80: xschem schematics of the main-loop filter (hierarchical, drawing checks) and the LVS
reference:
   sspll_lf_hv_r1      R1: three res_xhigh_po_2p85 segments drawn as the meander they are in the layout, two dummies
   sspll_lf_hv_c1tile  one C1 tile: 9 nfet_g5v0d10v5 MOS capacitors (gate = top) and the cap_mim_m3_1 above them
   sspll_lf_hv         C2 on vctl, R1 from vctl to vz, two C1 tiles on vz
Every device returns to VSSA (analog ground)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
from xsch import Sch, symbol
import json
import lf_hv as F
OUT = os.path.join(ROOT, "xschem", "lf_hv")
N5 = "nfet3_g5v0d10v5"
RES = "sky130_fd_pr/res_xhigh_po_2p85.sym"; MIM = "sky130_fd_pr/cap_mim_m3_1.sym"


def stub(s, pt, name, dx=0, dy=0, flip=0):
    q = (pt[0] + dx, pt[1] + dy)
    s.wire(pt, q); s.label(name, q[0], q[1], flip=flip)


def gnd_pin(s, y):
    s.pin("VSSA", "inout", 60, y); s.wire((60, y), (140, y)); s.label("VSSA", 140, y, flip=1)


def r1(p):
    s = Sch("sspll_lf_hv_r1")
    rm, rw, ns, rl = p["R1"]
    s.text(f"sspll_lf_hv_r1: R1 = {ns} x {rm} (W {rw} um, L {rl} um) in series,", 40, -370, 0.3)
    s.text("drawn as the layout meander (bottom-bottom, top-top); XRD0 / XRD1: dummy strips, all ends on VSSA", 40, -330, 0.3)
    xs = [400 + 300*k for k in range(ns)]
    R = [s.dev(RES, f"XR{k}", x, 0, f"L={rl} mult=1 model={rm} spiceprefix=X") for k, x in enumerate(xs)]
    s.pin("a", "inout", 200, -150); s.wire((200, -150), (400, -150), R[0]["P"])
    for k in range(ns - 1):                       # meander: M-M at the bottom, P-P at the top
        if k % 2 == 0:
            s.wire(R[k]["M"], (xs[k], 90), (xs[k + 1], 90), R[k + 1]["M"])
        else:
            s.wire(R[k]["P"], (xs[k], -90), (xs[k + 1], -90), R[k + 1]["P"])
    last = R[-1]["M"] if ns % 2 == 1 else R[-1]["P"]
    yb = 150 if ns % 2 == 1 else -150
    s.pin("b", "inout", xs[-1] + 200, yb, flip=1); s.wire(last, (xs[-1], yb), (xs[-1] + 200, yb))
    for r in R:
        stub(s, r["B"], "VSSA", -60)
    for k, x in enumerate((xs[0] - 300 + 50, xs[-1] + 300 + 50)):
        Rd = s.dev(RES, f"XRD{k}", x, 0, f"L={rl} mult=1 model={rm} spiceprefix=X")
        stub(s, Rd["P"], "VSSA", 0, -40); stub(s, Rd["M"], "VSSA", 0, 40); stub(s, Rd["B"], "VSSA", -60)
    gnd_pin(s, 300)
    return s


def c1tile(p):
    s = Sch("sspll_lf_hv_c1tile")
    m, w, nf, l = p["MC"]; cm, cw, cl = p["MIM1"]
    s.text(f"sspll_lf_hv_c1tile: {p['NMC']} MOS capacitors {m} W = L = {w:g} um in a 3 x 3 array", 40, -370, 0.3)
    s.text(f"(gate = top; drain, source, body = VSSA) and one {cm} {cw:g} x {cl:g} um above them (capm = top, met3 = VSSA)",
           40, -330, 0.3)
    M = s.mos("XC", N5, 400, 0, w, l, nf, body="VSSA", mult=p["NMC"])
    C = s.dev(MIM, "XM", 800, 0, f"W={cw} L={cl} MF=1 model={cm} spiceprefix=X")
    s.pin("top", "inout", 200, 0); s.wire((200, 0), (300, 0)); s.wire((300, 0), M["G"])
    s.wire((300, 0), (300, -200), (800, -200), C["c0"])
    stub(s, M["D"], "VSSA", 0, -60); stub(s, M["S"], "VSSA", 0, 60); stub(s, C["c1"], "VSSA", 0, 60)
    gnd_pin(s, 250)
    return s


def top(p, RXY, TXY):
    s = Sch("sspll_lf_hv")
    m2, w2, l2, n2 = p["C2"]
    s.text("sspll_lf_hv: main-loop filter. C2 on vctl takes each Gm packet first; R1 carries it into the C1 tiles on vz.",
           40, -420, 0.3)
    s.text("zero 1/(2 pi R1 C1), pole (C1 + C2)/(2 pi R1 C1 C2). Ground VSSA.", 40, -380, 0.3)
    R = s.sub("sspll_lf_hv_r1.sym", RXY, "xr1", 800, 0)
    ya = R["a"][1]
    s.pin("vctl", "inout", 200, ya); s.wire((200, ya), (400, ya)); s.wire((400, ya), R["a"])
    C2 = s.dev(MIM, "XC2", 400, 200, f"W={w2} L={l2} MF={n2} model={m2} spiceprefix=X")
    s.wire((400, ya), C2["c0"]); stub(s, C2["c1"], "VSSA", 0, 60)
    stub(s, R["VSSA"], "VSSA", 0, 40)
    T1 = s.sub("sspll_lf_hv_c1tile.sym", TXY, "xc1_0", 1300, 200)
    T2 = s.sub("sspll_lf_hv_c1tile.sym", TXY, "xc1_1", 1600, 200)
    yb = R["b"][1]
    s.wire(R["b"], (T1["top"][0], yb)); s.wire((T1["top"][0], yb), T1["top"])
    xm = (T1["top"][0] + T2["top"][0])//2
    s.wire((T1["top"][0], yb), (xm, yb)); s.wire((xm, yb), (T2["top"][0], yb), T2["top"])
    s.label("vz", xm, yb)
    stub(s, T1["VSSA"], "VSSA", 0, 40); stub(s, T2["VSSA"], "VSSA", 0, 40)
    gnd_pin(s, 500)
    return s


def drawn():
    S = json.load(open(os.path.join(HERE, "data", "step80hv_size.json")))
    return dict(F.D, R1=tuple(S["R1"]), C2=tuple(S["C2"]))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p = drawn()
    RXY = symbol(os.path.join(OUT, "sspll_lf_hv_r1.sym"), "sspll_lf_hv_r1", left=[("a", "inout")], right=[("b", "inout")],
                 bottom=[("VSSA", "inout")])
    TXY = symbol(os.path.join(OUT, "sspll_lf_hv_c1tile.sym"), "sspll_lf_hv_c1tile", left=[], right=[],
                 top=[("top", "inout")], bottom=[("VSSA", "inout")])
    symbol(os.path.join(OUT, "sspll_lf_hv.sym"), "sspll_lf_hv", left=[("vctl", "inout")], right=[],
           bottom=[("VSSA", "inout")])
    for name, sch in (("sspll_lf_hv_r1", r1(p)), ("sspll_lf_hv_c1tile", c1tile(p)), ("sspll_lf_hv", top(p, RXY, TXY))):
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        print(name, ":", "\n  ".join(errs) or "drawing check clean")
    open(os.path.join(ROOT, "xschem", "netlist", "ref_lf_hv.spice"), "w").write(F.lvs_reference(p))
