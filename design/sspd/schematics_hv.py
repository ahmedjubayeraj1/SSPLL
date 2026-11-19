#!/usr/bin/env python3
"""schematics_hv.py - step 78 redo (5 V devices on VDDA): xschem schematics, hierarchical, real wiring, drawing checks:
   sspll_sspd_hv_tg / _tgh (5 V transmission gates), sspll_sspd_hv_side (isolation buffer, R_s, sampler, dummy
   sampler, hold), sspll_sspd_hv (top: p and m sides). Derived from schematics.py (13-17 Nov drawing); also writes the
   LVS reference."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "design", "clkgen"))
from xsch import Sch, symbol
import sspd_hv as S
import importlib.util
_sp = importlib.util.spec_from_file_location("ckg_sch_hv", os.path.join(ROOT, "design", "clkgen", "schematics_hv.py"))
_ck = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_ck)
inverter = lambda s, name, x, y, size: _ck.inverter(s, name, x, y, size, "VDDA", True)   # 5 V inverter on VDDA
OUT = os.path.join(ROOT, "xschem", "sspd_hv")
MIM = "sky130_fd_pr/cap_mim_m3_1.sym"
TG_PINS = dict(left=[("a", "inout"), ("g", "in"), ("gb", "in")], right=[("b", "inout")],
               top=[("VDDA", "inout")], bottom=[("VSS", "inout")])


def tg(p, name, kn, kp):
    n, pp = p[kn], p[kp]
    s = Sch(name)
    s.text(f"{name}: 5 V transmission gate a-b, on while g = 1 / gb = 0 (gates swing 0 / 3.3 V). There is no low-Vt "
           "5 V device: the nMOS sees V_GS = 3.3 - 1.65 V at mid-rail, so the pMOS carries about half the conductance", 40, -420, 0.3)
    N = s.mos("XN", "nfet3_g5v0d10v5", 300, 0, n[1], n[3], n[2], body="VSS")
    P = s.mos("XP", "pfet3_g5v0d10v5", 600, 0, pp[1], pp[3], pp[2], body="VDDA", flip=1)
    s.wire(N["D"], (N["D"][0], -120), (P["S"][0], -120), P["S"])
    s.wire(N["S"], (N["S"][0], 120), (P["D"][0], 120), P["D"])
    s.pin("a", "inout", 60, -120); s.wire((60, -120), (N["D"][0], -120))
    s.pin("b", "inout", 860, 120, flip=1); s.wire((P["D"][0], 120), (860, 120))
    s.pin("g", "in", 60, 0); s.wire((60, 0), N["G"])
    s.pin("gb", "in", 860, 0, flip=1); s.wire(P["G"], (860, 0))
    s.pin("VDDA", "inout", 60, -300); s.wire((60, -300), (140, -300)); s.label("VDDA", 140, -300, flip=1)
    s.pin("VSS", "inout", 60, 300); s.wire((60, 300), (140, 300)); s.label("VSS", 140, 300, flip=1)
    return s


def side(p, TXY):
    s = Sch("sspll_sspd_hv_side")
    rm, rw, _, rl = p["RS"]
    s.text("sspll_sspd_hv_side: isolation buffer (XB1, XB2) -> R_s -> node f -> sampler xs1/C1 (tracks while cks = 1) "
           "and dummy sampler xsd/CD (opposite phase, keeps the buffer load constant); hold xs2/C2 (ckh)", 40, -560, 0.3)
    s.text(f"R_s = {rm}, L = {rl} um; C1 = C2 = {p['C1'][1]} x {p['C1'][3]} um, CD = {p['CD'][1]} x {p['CD'][3]} um "
           "(= C1 + the Gm input); MIM top plate on the signal, bottom plate on VSS", 40, -510, 0.25)
    s.pin("clk", "in", 60, 0)
    i1, o1 = inverter(s, "XB1", 260, 0, p["B1"]); i2, o2 = inverter(s, "XB2", 520, 0, p["B2"])
    s.wire((60, 0), i1); s.wire(o1, i2)
    R = s.dev(f"sky130_fd_pr/{rm}.sym", "XRS", 700, 0, f"L={rl} mult=1 model={rm} spiceprefix=X", rot=3)
    a_, b_ = (R["P"], R["M"]) if R["P"][0] < R["M"][0] else (R["M"], R["P"])
    s.wire(o2, a_)
    s.wire(R["B"], (R["B"][0], R["B"][1] - 110)); s.label("VSS", R["B"][0], R["B"][1] - 110)
    X1 = s.sub("sspll_sspd_hv_tg.sym", TXY, "xs1", 1000, 0)
    XD = s.sub("sspll_sspd_hv_tg.sym", TXY, "xsd", 1000, 420)
    X2 = s.sub("sspll_sspd_hv_tgh.sym", TXY, "xs2", 1560, 0)
    fx = 800
    s.wire(b_, (fx, b_[1]), (fx, X1["a"][1]), X1["a"])
    s.wire((fx, X1["a"][1]), (fx, XD["a"][1]), XD["a"])
    # clock gate stubs (distribution nets joined by name)
    for X, g, gb in ((X1, "cks", "cksb"), (XD, "cksb", "cks"), (X2, "ckh", "ckhb")):
        s.wire(X["g"], (X["g"][0] - 30, X["g"][1])); s.label(g, X["g"][0] - 30, X["g"][1])
        s.wire(X["gb"], (X["gb"][0] - 30, X["gb"][1])); s.label(gb, X["gb"][0] - 30, X["gb"][1])
        s.wire(X["VDDA"], (X["VDDA"][0], X["VDDA"][1] - 20)); s.label("VDDA", X["VDDA"][0], X["VDDA"][1] - 20)
        s.wire(X["VSS"], (X["VSS"][0], X["VSS"][1] + 20)); s.label("VSS", X["VSS"][0], X["VSS"][1] + 20)
    # v1 node: C1, hold switch input, output pin to the Gm
    c1x = X1["b"][0] + 120
    C1 = s.dev(MIM, "XC1", c1x, X1["b"][1] + 130, f"W={p['C1'][1]} L={p['C1'][3]} MF=1 model={p['C1'][0]} spiceprefix=X")
    s.wire(X1["b"], (c1x, X1["b"][1]), C1["c0"])
    s.wire((c1x, X1["b"][1]), (c1x, X1["b"][1] - 160), (X2["a"][0] - 60, X1["b"][1] - 160),
           (X2["a"][0] - 60, X2["a"][1]), X2["a"])
    s.wire(C1["c1"], (C1["c1"][0], C1["c1"][1] + 20)); s.label("VSS", C1["c1"][0], C1["c1"][1] + 20)
    s.wire((c1x, X1["b"][1] - 160), (c1x, -260), (2200, -260)); s.pin("v1", "out", 2200, -260, flip=1)
    # dummy capacitor
    CD = s.dev(MIM, "XCD", XD["b"][0] + 120, XD["b"][1] + 130,
               f"W={p['CD'][1]} L={p['CD'][3]} MF=1 model={p['CD'][0]} spiceprefix=X")
    s.wire(XD["b"], (XD["b"][0] + 120, XD["b"][1]), CD["c0"])
    s.wire(CD["c1"], (CD["c1"][0], CD["c1"][1] + 20)); s.label("VSS", CD["c1"][0], CD["c1"][1] + 20)
    # v2 node: C2, output pin to the NCB amplifier
    c2x = X2["b"][0] + 120
    C2 = s.dev(MIM, "XC2", c2x, X2["b"][1] + 130, f"W={p['C2'][1]} L={p['C2'][3]} MF=1 model={p['C2'][0]} spiceprefix=X")
    s.wire(X2["b"], (c2x, X2["b"][1]), C2["c0"])
    s.wire(C2["c1"], (C2["c1"][0], C2["c1"][1] + 20)); s.label("VSS", C2["c1"][0], C2["c1"][1] + 20)
    s.wire((c2x, X2["b"][1]), (2200, X2["b"][1])); s.pin("v2", "out", 2200, X2["b"][1], flip=1)
    for k, y in (("cks", 700), ("cksb", 760), ("ckh", 820), ("ckhb", 880)):
        s.pin(k, "in", 60, y); s.wire((60, y), (160, y)); s.label(k, 160, y, flip=1)
    s.pin("VDDA", "inout", 60, -400); s.wire((60, -400), (140, -400)); s.label("VDDA", 140, -400, flip=1)
    s.pin("VSS", "inout", 60, 960); s.wire((60, 960), (140, 960)); s.label("VSS", 140, 960, flip=1)
    return s


def top(SXY):
    s = Sch("sspll_sspd_hv")
    s.text("sspll_sspd_hv: sub-sampling phase detector with hold. v1p - v1m (the fresh sample) goes to the pulsed Gm "
           "(step 79), v2p - v2m (held for a whole period) to the NCB amplifier", 40, -520, 0.3)
    s.text("clkp / clkm: the 5 V ring's buffered outputs (step 74 HV); cks/cksb, ckh/ckhb from the clock generator "
           "(step 77 HV, 3.3 V); every device 5 V-rated on VDDA", 40, -470, 0.25)
    P = s.sub("sspll_sspd_hv_side.sym", SXY, "xsp", 700, 0)
    M = s.sub("sspll_sspd_hv_side.sym", SXY, "xsm", 700, 600)
    s.pin("clkp", "in", 60, P["clk"][1]); s.wire((60, P["clk"][1]), P["clk"])
    s.pin("clkm", "in", 60, M["clk"][1]); s.wire((60, M["clk"][1]), M["clk"])
    for X, a, b in ((P, "v1p", "v2p"), (M, "v1m", "v2m")):
        s.wire(X["v1"], (1300, X["v1"][1])); s.pin(a, "out", 1300, X["v1"][1], flip=1)
        s.wire(X["v2"], (1300, X["v2"][1])); s.pin(b, "out", 1300, X["v2"][1], flip=1)
        for k in ("cks", "cksb", "ckh", "ckhb"):
            s.wire(X[k], (X[k][0] - 60, X[k][1])); s.label(k, X[k][0] - 60, X[k][1])
        s.wire(X["VDDA"], (X["VDDA"][0], X["VDDA"][1] - 20)); s.label("VDDA", X["VDDA"][0], X["VDDA"][1] - 20)
        s.wire(X["VSS"], (X["VSS"][0], X["VSS"][1] + 20)); s.label("VSS", X["VSS"][0], X["VSS"][1] + 20)
    for k, y in (("cks", 1100), ("cksb", 1160), ("ckh", 1220), ("ckhb", 1280)):
        s.pin(k, "in", 60, y); s.wire((60, y), (160, y)); s.label(k, 160, y, flip=1)
    s.pin("VDDA", "inout", 60, -380); s.wire((60, -380), (140, -380)); s.label("VDDA", 140, -380, flip=1)
    s.pin("VSS", "inout", 60, 1360); s.wire((60, 1360), (140, 1360)); s.label("VSS", 140, 1360, flip=1)
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    TXY = symbol(os.path.join(OUT, "sspll_sspd_hv_tg.sym"), "sspll_sspd_hv_tg", **TG_PINS)
    symbol(os.path.join(OUT, "sspll_sspd_hv_tgh.sym"), "sspll_sspd_hv_tgh", **TG_PINS)
    SXY = symbol(os.path.join(OUT, "sspll_sspd_hv_side.sym"), "sspll_sspd_hv_side",
                 left=[("clk", "in"), ("cks", "in"), ("cksb", "in"), ("ckh", "in"), ("ckhb", "in")],
                 right=[("v1", "out"), ("v2", "out")], top=[("VDDA", "inout")], bottom=[("VSS", "inout")])
    symbol(os.path.join(OUT, "sspll_sspd_hv.sym"), "sspll_sspd_hv",
           left=[("clkp", "in"), ("clkm", "in"), ("cks", "in"), ("cksb", "in"), ("ckh", "in"), ("ckhb", "in")],
           right=[("v1p", "out"), ("v1m", "out"), ("v2p", "out"), ("v2m", "out")],
           top=[("VDDA", "inout")], bottom=[("VSS", "inout")])
    for name, sch in (("sspll_sspd_hv_tg", tg(S.D, "sspll_sspd_hv_tg", "SWN", "SWP")),
                      ("sspll_sspd_hv_tgh", tg(S.D, "sspll_sspd_hv_tgh", "HWN", "HWP")),
                      ("sspll_sspd_hv_side", side(S.D, TXY)), ("sspll_sspd_hv", top(SXY))):
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        print(name, ":", "\n  ".join(errs) or "drawing check clean")
    open(os.path.join(ROOT, "xschem", "netlist", "ref_sspd_hv.spice"), "w").write(S.lvs_reference())
