#!/usr/bin/env python3
"""schematics_hv.py - xschem schematics of the FLL (hierarchical, drawing checks) and the LVS reference.
   sspll_fll_ds       3.3 -> 1.8 V down-shifter (5 V inverter on VDDD + two 1.8 V inverters)
   sspll_fll_tspc     TSPC /2 cell (9 transistors + output inverter)
   sspll_fll_div16    down-shifter + 4 x TSPC
   sspll_fll_pfd      PFD + dead zone (sky130_fd_sc_hd cells)
   sspll_fll_win      lock-detector window delays (sky130_fd_sc_hd cells)
   sspll_fll_lockdet  window flip-flops, run counter, lock flag (sky130_fd_sc_hd cells)
   sspll_fll_logic    pfd + win + lockdet
   sspll_fll_cp       5 V current-steering charge pump
   sspll_fll_hv       top: div16, logic, 3 level shifters (../cco_hv), charge pump
Digital cells sit on VDDD / VSSD, the charge pump on VDDA / VSSA. In the standard-cell schematics the data paths
are wired; nets that fan out across the sheet (counter state, lock) use net labels."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
import xsch
from xsch import Sch, symbol
import fll_hv as F
OUT = os.path.join(ROOT, "xschem", "fll_hv")
SCLIB = os.path.join(os.environ.get("PDK_ROOT", "/home/claude/pdk"), "sky130A", "libs.tech", "xschem", "sky130_stdcells")
N18, P18, N5, P5 = "nfet3_01v8", "pfet3_01v8", "nfet3_g5v0d10v5", "pfet3_g5v0d10v5"
LS_PINS = dict(left=[("in", "in")], right=[("out", "out"), ("outb", "out")], top=[("VDDD", "inout"), ("VDDA", "inout")],
               bottom=[("VSSA", "inout"), ("VSSD", "inout")])


def stdsym(cell):
    """register a sky130_stdcells symbol: pin offsets from its B 5 boxes"""
    key = f"sky130_stdcells/{cell}.sym"
    if key not in xsch.SYM:
        txt = open(os.path.join(SCLIB, cell + ".sym")).read()
        pins = {}
        for m in re.finditer(r"^B 5 (\S+) (\S+) (\S+) (\S+) \{name=(\w+)", txt, re.M):
            x0, y0, x1, y1 = map(float, m.groups()[:4])
            pins[m.group(5)] = (int(round((x0 + x1)/2)), int(round((y0 + y1)/2)))
        xsch.SYM[key] = pins
    return key


def cell(s, c, name, x, y, flip=0):
    return s.dev(stdsym(c), name, x, y, "VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__", flip=flip)


def stub(s, pt, name, dx=0, dy=0, flip=None):
    q = (pt[0] + dx, pt[1] + dy)
    s.wire(pt, q)
    s.label(name, q[0], q[1], flip=(1 if dx > 0 else 0) if flip is None else flip)
    return q


def mos(s, name, kind, x, y, dev, body, mult=1):
    m, w, nf, l = dev
    return s.mos(name, kind, x, y, w, l, nf, body=body, mult=mult)


# ------------------------------------------------------------------ MOS-level cells
def inv_col(s, nm, x, a, p, n, vdd, vss, kn=N18, kp=P18):
    """inverter at column x: pMOS at y -100, nMOS at y 100, gates joined at (x - 100, 0); returns output point (x+20, 0)"""
    P = mos(s, nm + "P", kp, x, -100, p, vdd); Nn = mos(s, nm + "N", kn, x, 100, n, vss)
    s.wire(a, (x - 100, 0)); s.wire((x - 100, 0), (x - 100, -100), P["G"]); s.wire((x - 100, 0), (x - 100, 100), Nn["G"])
    stub(s, P["S"], vdd, 0, -40, 0); stub(s, Nn["S"], vss, 0, 40, 0)
    s.wire(P["D"], (x + 20, 0)); s.wire((x + 20, 0), Nn["D"])
    return (x + 20, 0)


def ds(p):
    s = Sch("sspll_fll_ds")
    s.text("sspll_fll_ds: 3.3 -> 1.8 V down-shifter. A 5 V inverter on VDDD takes the 0..VDDA clock on its thick gates;",
           40, -420, 0.3)
    s.text("two 1.8 V inverters restore the edges (out in phase with in).", 40, -380, 0.3)
    s.pin("in", "in", 100, 0)
    o1 = inv_col(s, "XD", 400, (100, 0), p["DSP"], p["DSN"], "VDDD", "VSSD", N5, P5)
    o2 = inv_col(s, "XI1", 700, o1, p["DSI"][1], p["DSI"][0], "VDDD", "VSSD")
    o3 = inv_col(s, "XI2", 1000, o2, p["DSI"][1], p["DSI"][0], "VDDD", "VSSD")
    s.pin("out", "out", 1200, 0, flip=1); s.wire(o3, (1200, 0))
    s.pin("VDDD", "inout", 100, -300); stub(s, (100, -300), "VDDD", 80, 0)
    s.pin("VSSD", "inout", 100, 300); stub(s, (100, 300), "VSSD", 80, 0)
    return s


def tspc(p):
    s = Sch("sspll_fll_tspc")
    s.text("sspll_fll_tspc: TSPC flip-flop with D = qb, so it divides ck by 2. Stage 1: x = not qb while ck is low;", 40, -460, 0.3)
    s.text("stage 2 precharges y while ck is low, y = not x after the rising edge; stage 3: qb = not y while ck is high; q = not qb.",
           40, -420, 0.3)
    A = mos(s, "XP1A", P18, 400, -220, p["T1P"], "VDDD"); B = mos(s, "XP1B", P18, 400, -100, p["T1P"], "VDDD")
    C = mos(s, "XN1", N18, 400, 100, p["T1N"], "VSSD")
    stub(s, A["S"], "VDDD", 0, -40, 0); s.wire(A["D"], B["S"]); s.wire(B["D"], (420, 0)); s.wire((420, 0), C["D"])
    stub(s, C["S"], "VSSD", 0, 40, 0)
    stub(s, A["G"], "qb", -60); stub(s, B["G"], "ck", -60); stub(s, C["G"], "qb", -60)
    P2 = mos(s, "XP2", P18, 650, -100, p["T2P"], "VDDD"); N2A = mos(s, "XN2A", N18, 650, 100, p["T2N"], "VSSD")
    N2B = mos(s, "XN2B", N18, 650, 220, p["T2N"], "VSSD")
    stub(s, P2["S"], "VDDD", 0, -40, 0); s.wire(P2["D"], (670, 0)); s.wire((670, 0), N2A["D"]); s.wire(N2A["S"], N2B["D"])
    stub(s, N2B["S"], "VSSD", 0, 40, 0)
    s.wire((420, 0), (540, 0), (540, 100), N2A["G"]); s.label("x", 540, 0)
    stub(s, P2["G"], "ck", -60); stub(s, N2B["G"], "ck", -60)
    P3 = mos(s, "XP3", P18, 900, -100, p["T3P"], "VDDD"); N3A = mos(s, "XN3A", N18, 900, 100, p["T3N"], "VSSD")
    N3B = mos(s, "XN3B", N18, 900, 220, p["T3N"], "VSSD")
    stub(s, P3["S"], "VDDD", 0, -40, 0); s.wire(P3["D"], (920, 0)); s.wire((920, 0), N3A["D"]); s.wire(N3A["S"], N3B["D"])
    stub(s, N3B["S"], "VSSD", 0, 40, 0)
    s.wire((670, 0), (790, 0)); s.wire((790, 0), (790, -100), P3["G"]); s.wire((790, 0), (790, 220), N3B["G"])
    s.label("y", 790, 0)
    stub(s, N3A["G"], "ck", -60)
    o = inv_col(s, "XI", 1150, (920, 0), p["TI"][1], p["TI"][0], "VDDD", "VSSD")
    s.label("qb", 1050, 0, flip=1)
    s.pin("q", "out", 1350, 0, flip=1); s.wire(o, (1350, 0))
    s.pin("qb", "out", 100, 400); stub(s, (100, 400), "qb", 80, 0)
    s.pin("ck", "in", 100, -350); stub(s, (100, -350), "ck", 80, 0)
    s.pin("VDDD", "inout", 100, 500); stub(s, (100, 500), "VDDD", 80, 0)
    s.pin("VSSD", "inout", 100, 560); stub(s, (100, 560), "VSSD", 80, 0)
    return s


def div16(DSXY, TXY):
    s = Sch("sspll_fll_div16")
    s.text("sspll_fll_div16: clkp (0..VDDA) -> down-shifter -> four TSPC /2 -> div = clkp / 16 (50 MHz at lock).", 40, -300, 0.3)
    s.pin("clkp", "in", 100, 0)
    X = s.sub("sspll_fll_ds.sym", DSXY, "xds", 400, 0)
    s.wire((100, 0), (X["in"][0], 0)) if X["in"][1] == 0 else s.wire((100, 0), (200, 0), (200, X["in"][1]), X["in"])
    prev = X["out"]
    for k in range(4):
        T = s.sub("sspll_fll_tspc.sym", TXY, f"xt{k+1}", 800 + 400*k, 0)
        s.wire(prev, (prev[0] + 60, prev[1])); s.wire((prev[0] + 60, prev[1]), (prev[0] + 60, T["ck"][1]), T["ck"]) \
            if prev[1] != T["ck"][1] else s.wire((prev[0] + 60, prev[1]), T["ck"])
        stub(s, T["qb"], f"c{k+1}b", 0, 60, 1)
        for sup in ("VDDD", "VSSD"):
            stub(s, T[sup], sup, 0, -40 if sup == "VDDD" else 40, 0)
        prev = T["q"]
    s.pin("div", "out", prev[0] + 300, prev[1], flip=1); s.wire(prev, (prev[0] + 300, prev[1]))
    for sup in ("VDDD", "VSSD"):
        stub(s, X[sup], sup, 0, -40 if sup == "VDDD" else 40, 0)
    s.pin("VDDD", "inout", 100, 300); stub(s, (100, 300), "VDDD", 80, 0)
    s.pin("VSSD", "inout", 100, 360); stub(s, (100, 360), "VSSD", 80, 0)
    return s


def cp(p):
    s = Sch("sspll_fll_cp")
    k = p["NCP"]
    s.text(f"sspll_fll_cp: current-steering charge pump, 5 V devices on VDDA / VSSA. ib (5 uA) -> diode XND; sink mirror XNS (x{k})",
           40, -560, 0.3)
    s.text(f"steered to vctl by up5 or to VDDA by up5b; source mirror XPS (x{k}, via XN1 -> diode XPD) steered to vctl by dn5b or",
           40, -520, 0.3)
    s.text("to VSSA by dn5. The mirrors stay in saturation, so their gates are not kicked. act5b = 1 shorts ib: everything off.",
           40, -480, 0.3)
    # bias column
    ND = mos(s, "XND", N5, 300, 200, p["CPN"], "VSSA"); NK = mos(s, "XNK", N5, 550, 200, p["SWN"], "VSSA")
    s.pin("ib", "inout", 100, 60); s.wire((100, 60), (320, 60)); s.wire((320, 60), ND["D"])
    s.wire((320, 60), (570, 60), NK["D"]); s.wire(ND["D"], (320, 120), (240, 120)); s.wire((240, 120), (240, 200), ND["G"])
    s.label("ib", 240, 120)
    stub(s, ND["S"], "VSSA", 0, 40, 0); stub(s, NK["S"], "VSSA", 0, 40, 0); stub(s, NK["G"], "act5b", -60)
    # sink path
    NS = mos(s, "XNS", N5, 900, 300, p["CPN"], "VSSA", mult=k)
    SU = mos(s, "XSU", N5, 900, 100, p["SWN"], "VSSA"); SX = mos(s, "XSUX", N5, 1150, 100, p["SWN"], "VSSA")
    s.wire(SU["S"], (920, 200)); s.wire((920, 200), NS["D"]); s.wire((920, 200), (1170, 200), SX["S"])
    stub(s, NS["S"], "VSSA", 0, 40, 0); stub(s, NS["G"], "ib", -60); stub(s, SU["G"], "up5", -60)
    stub(s, SX["G"], "up5b", -60); stub(s, SX["D"], "VDDA", 0, -40, 0)
    # source path
    N1 = mos(s, "XN1", N5, 1500, 200, p["CPN"], "VSSA"); PD = mos(s, "XPD", P5, 1500, -250, p["CPP"], "VDDA")
    s.wire(N1["D"], (1520, -100)); s.wire((1520, -100), PD["D"]); s.wire((1520, -100), (1440, -100))
    s.wire((1440, -100), (1440, -250), PD["G"]); s.label("pd", 1440, -100)
    stub(s, N1["S"], "VSSA", 0, 40, 0); stub(s, N1["G"], "ib", -60); stub(s, PD["S"], "VDDA", 0, -40, 0)
    PS = mos(s, "XPS", P5, 900, -350, p["CPP"], "VDDA", mult=k)
    SD = mos(s, "XSD", P5, 900, -150, p["SWP"], "VDDA"); SDX = mos(s, "XSDX", P5, 1150, -150, p["SWP"], "VDDA")
    s.wire(PS["D"], (920, -250)); s.wire((920, -250), SD["S"]); s.wire((920, -250), (1170, -250), SDX["S"])
    stub(s, PS["S"], "VDDA", 0, -40, 0); stub(s, PS["G"], "pd", -60); stub(s, SD["G"], "dn5b", -60)
    stub(s, SDX["G"], "dn5", -60); stub(s, SDX["D"], "VSSA", 0, 40, 0)
    # output
    s.wire(SD["D"], (920, -30)); s.wire((920, -30), SU["D"]); s.wire((920, -30), (1300, -30))
    s.pin("vctl", "inout", 1300, -30, flip=1)
    for nm, y in (("up5", 300), ("up5b", 360), ("dn5", 420), ("dn5b", 480), ("act5b", 540)):
        s.pin(nm, "in", 100, y); stub(s, (100, y), nm, 80, 0)
    s.pin("VDDA", "inout", 100, -300); stub(s, (100, -300), "VDDA", 80, 0)
    s.pin("VSSA", "inout", 100, 620); stub(s, (100, 620), "VSSA", 80, 0)
    return s


# ------------------------------------------------------------------ standard-cell sheets
def pins_left(s, names, x=100, y0=0, dy=60, kind="in"):
    for k, n in enumerate(names):
        s.pin(n, kind, x, y0 + dy*k); stub(s, (x, y0 + dy*k), n, 80, 0)


def pins_right(s, names, x, y0=0, dy=60):
    for k, n in enumerate(names):
        s.pin(n, "out", x, y0 + dy*k, flip=1); stub(s, (x, y0 + dy*k), n, -220, 0, 0)


def pfd():
    s = Sch("sspll_fll_pfd")
    s.text("sspll_fll_pfd: tri-state PFD (two dfrtp, D = 1, NAND reset, held in reset while fll_en = 0) and the dead zone:", 40, -460, 0.3)
    s.text("upg = up AND (up delayed ~0.26 ns) AND act, so the reset pulse and edges closer than the delay never reach the pump.",
           40, -420, 0.3)
    U = cell(s, "dfrtp_1", "xfu", 500, -150); Dn = cell(s, "dfrtp_1", "xfd", 500, 150)
    stub(s, U["CLK"], "refclk", -60); stub(s, Dn["CLK"], "div", -60)
    stub(s, U["D"], "VDDD", -60); stub(s, Dn["D"], "VDDD", -60)
    RN = cell(s, "nand2_1", "xrn", 850, 0); RD = cell(s, "buf_1", "xrd", 1050, 0); RE = cell(s, "and2_1", "xre", 1250, 20)
    s.wire(U["Q"], (650, U["Q"][1])); s.wire((650, U["Q"][1]), (650, RN["A"][1]), RN["A"])
    s.wire(Dn["Q"], (680, Dn["Q"][1])); s.wire((680, Dn["Q"][1]), (680, RN["B"][1]), RN["B"])
    s.wire(RN["Y"], RD["A"]) if RN["Y"][1] == RD["A"][1] else s.wire(RN["Y"], (950, RN["Y"][1]), (950, RD["A"][1]), RD["A"])
    s.wire(RD["X"], (1150, RD["X"][1]), (1150, RE["A"][1]), RE["A"]); stub(s, RE["B"], "fll_en", -60)
    stub(s, RE["X"], "rb", 60); stub(s, U["RESET_B"], "rb", -60); stub(s, Dn["RESET_B"], "rb", -60)
    s.label("up", 650, U["Q"][1], flip=1); s.label("dn", 680, Dn["Q"][1], flip=1)
    rows = (("u", U, -300, "up", "upg"), ("d", Dn, 300, "dn", "dng"))
    for t, F_, y, nm, og in rows:
        Z1 = cell(s, "clkdlybuf4s25_1", f"xz{t}1", 1050, y); Z2 = cell(s, "buf_1", f"xz{t}2", 1300, y)
        G = cell(s, "and3_1", f"xg{t}", 1600, y)
        stub(s, Z1["A"], nm, -60)
        s.wire(Z1["X"], Z2["A"]) if Z1["X"][1] == Z2["A"][1] else None
        s.wire(Z2["X"], (1480, Z2["X"][1]), (1480, G["B"][1]), G["B"])
        stub(s, G["A"], nm, -60); stub(s, G["C"], "act", -60)
        stub(s, G["X"], og, 60)
    pins_left(s, ["refclk", "div", "fll_en", "act"], y0=500)
    pins_right(s, ["up", "dn", "upg", "dng"], 2000, y0=500)
    s.pin("VDDD", "inout", 100, 760); stub(s, (100, 760), "VDDD", 80, 0)
    s.pin("VSSD", "inout", 100, 820); stub(s, (100, 820), "VSSD", 80, 0)
    return s


def win():
    s = Sch("sspll_fll_win")
    s.text("sspll_fll_win: refclk and div delayed by three clkdlybuf4s50 (w_in tap, about 1.07 ns) or, while lock = 1, by seven",
           40, -300, 0.3)
    s.text("(w_out tap, about 2.5 ns): refw / divw clock the window flip-flops. cclk (counter clock) follows after both.",
           40, -260, 0.3)
    for t, src, y, outn in (("r", "refclk", 0, "refw"), ("d", "div", 300, "divw")):
        prev = None
        for k in range(1, 8):
            X = cell(s, "clkdlybuf4s50_1", f"xw{t}{k}", 300 + 250*(k - 1), y)
            if prev is None:
                stub(s, X["A"], src, -60)
            elif k == 4:                      # tap 3 for the mux: split the wire at the label
                mid = (prev[0] + X["A"][0])//2
                s.wire(prev, (mid, prev[1])); s.wire((mid, prev[1]), X["A"]); s.label(f"{t}3", mid, prev[1], flip=1)
            else:
                s.wire(prev, X["A"])
            prev = X["X"]
        s.label(f"{t}7", prev[0] + 40, prev[1], flip=1); s.wire(prev, (prev[0] + 40, prev[1]))
        Mx = cell(s, "mux2_1", f"xw{t}m", 2200, y + 100)
        stub(s, Mx["A0"], f"{t}3", -60); stub(s, Mx["A1"], f"{t}7", -60); stub(s, Mx["S"], "lock", -60)
        stub(s, Mx["X"], outn, 60)
    C1 = cell(s, "clkdlybuf4s25_1", "xcc1", 2200, -100); C2 = cell(s, "buf_1", "xcc2", 2450, -100)
    stub(s, C1["A"], "r7", -60); s.wire(C1["X"], C2["A"]); stub(s, C2["X"], "cclk", 60)
    pins_left(s, ["refclk", "div", "lock"], y0=600)
    pins_right(s, ["refw", "divw", "cclk"], 2750, y0=600)
    s.pin("VDDD", "inout", 100, 800); stub(s, (100, 800), "VDDD", 80, 0)
    s.pin("VSSD", "inout", 100, 860); stub(s, (100, 860), "VSSD", 80, 0)
    return s


def lockdet():
    s = Sch("sspll_fll_lockdet")
    s.text("sspll_fll_lockdet: o1 = up still high at refw, o2 = dn still high at divw, out = o1 + o2; inc = lock XNOR out.",
           40, -460, 0.3)
    s.text("4-bit run counter c3..c0 (next = g ? c + 1 : 0, g = inc AND NOT term); term = c == 15 (unlocked) or c == 3 (locked);",
           40, -420, 0.3)
    s.text("the lock flag toggles when inc AND term. act = fll_en AND NOT lock; lock_det = lock; fll_dir = o1 (ring slow).",
           40, -380, 0.3)
    O1 = cell(s, "dfrtp_1", "xo1", 300, -200); O2 = cell(s, "dfrtp_1", "xo2", 300, 50)
    for O, ck, d in ((O1, "refw", "up"), (O2, "divw", "dn")):
        stub(s, O["CLK"], ck, -60); stub(s, O["D"], d, -60); stub(s, O["RESET_B"], "fll_en", -60)
    OO = cell(s, "or2_1", "xoo", 600, -80)
    s.wire(O1["Q"], (480, O1["Q"][1]), (480, OO["A"][1]), OO["A"]); s.wire(O2["Q"], (510, O2["Q"][1]), (510, OO["B"][1]), OO["B"])
    s.label("o1", 480, O1["Q"][1], flip=1)
    IX = cell(s, "xnor2_1", "xix", 850, -100)          # B in line with the OR output: one straight wire
    s.wire(OO["X"], (720, OO["X"][1])); s.wire((720, OO["X"][1]), IX["B"]); s.label("out", 720, OO["X"][1], flip=1)
    stub(s, IX["A"], "lock", -60)
    stub(s, IX["Y"], "inc", 60)
    # incrementer column
    g = [("inv_1", "xs0", dict(A="c0"), "Y", "s0"), ("xor2_1", "xs1", dict(A="c1", B="c0"), "X", "s1"),
         ("and2_1", "xt2", dict(A="c1", B="c0"), "X", "t2"), ("xor2_1", "xs2", dict(A="c2", B="t2"), "X", "s2"),
         ("and3_1", "xt3", dict(A="c2", B="c1", C="c0"), "X", "t3"), ("xor2_1", "xs3", dict(A="c3", B="t3"), "X", "s3"),
         ("and2_1", "xt4", dict(A="c3", B="t3"), "X", "t4")]
    for k, (c, nm, ins, o, on) in enumerate(g):
        X = cell(s, c, nm, 1250, -250 + 140*k)
        for pn, net in ins.items():
            stub(s, X[pn], net, -60)
        stub(s, X[o], on, 60)
    TM = cell(s, "mux2_1", "xtm", 1700, -250); TN = cell(s, "inv_1", "xtn", 1950, -250)
    stub(s, TM["A0"], "t4", -60); stub(s, TM["A1"], "t2", -60); stub(s, TM["S"], "lock", -60)
    s.wire(TM["X"], (1840, TM["X"][1])); s.wire((1840, TM["X"][1]), (1840, TN["A"][1]), TN["A"]) \
        if TM["X"][1] != TN["A"][1] else s.wire((1840, TM["X"][1]), TN["A"])
    s.label("term", 1840, TM["X"][1], flip=1)
    stub(s, TN["Y"], "nterm", 60)
    G = cell(s, "and2_1", "xg", 1700, -50); TG = cell(s, "and2_1", "xtg", 1700, 100)
    stub(s, G["A"], "inc", -60); stub(s, G["B"], "nterm", -60); stub(s, G["X"], "g", 60)
    stub(s, TG["A"], "inc", -60); stub(s, TG["B"], "term", -60); stub(s, TG["X"], "tg", 60)
    for i in range(4):
        Nn = cell(s, "and2_1", f"xn{i}", 2150, -250 + 200*i); Cf = cell(s, "dfrtp_1", f"xc{i}", 2500, -250 + 200*i)
        stub(s, Nn["A"], "g", -60); stub(s, Nn["B"], f"s{i}", -60)
        s.wire(Nn["X"], (2300, Nn["X"][1]), (2300, Cf["D"][1]), Cf["D"]) if Nn["X"][1] != Cf["D"][1] else s.wire(Nn["X"], Cf["D"])
        stub(s, Cf["CLK"], "cclk", -60); stub(s, Cf["RESET_B"], "fll_en", -60); stub(s, Cf["Q"], f"c{i}", 60)
    LX = cell(s, "xor2_1", "xlx", 2150, 600); LF = cell(s, "dfrtp_1", "xlf", 2500, 600)
    stub(s, LX["A"], "lock", -60); stub(s, LX["B"], "tg", -60)
    s.wire(LX["X"], (2300, LX["X"][1]), (2300, LF["D"][1]), LF["D"]) if LX["X"][1] != LF["D"][1] else s.wire(LX["X"], LF["D"])
    stub(s, LF["CLK"], "cclk", -60); stub(s, LF["RESET_B"], "fll_en", -60); stub(s, LF["Q"], "lock", 60)
    LI = cell(s, "inv_1", "xli", 300, 400); LA = cell(s, "and2_1", "xla", 550, 380)   # B in line with the inverter output
    stub(s, LI["A"], "lock", -60); s.wire(LI["Y"], LA["B"])
    stub(s, LA["A"], "fll_en", -60); stub(s, LA["X"], "act", 60)
    B1 = cell(s, "buf_1", "xob1", 300, 600); B2 = cell(s, "buf_1", "xob2", 300, 750)
    stub(s, B1["A"], "lock", -60); stub(s, B1["X"], "lock_det", 60); stub(s, B2["A"], "o1", -60); stub(s, B2["X"], "fll_dir", 60)
    pins_left(s, ["up", "dn", "refw", "divw", "cclk", "fll_en"], y0=950)
    pins_right(s, ["lock", "act", "lock_det", "fll_dir"], 2900, y0=950)
    s.pin("VDDD", "inout", 100, 1350); stub(s, (100, 1350), "VDDD", 80, 0)
    s.pin("VSSD", "inout", 100, 1410); stub(s, (100, 1410), "VSSD", 80, 0)
    return s


def logic(PXY, WXY, LXY):
    s = Sch("sspll_fll_logic")
    s.text("sspll_fll_logic: PFD + dead zone, lock-detector windows and lock detector (sky130_fd_sc_hd on VDDD / VSSD).", 40, -400, 0.3)
    P = s.sub("sspll_fll_pfd.sym", PXY, "xpfd", 500, 0); W = s.sub("sspll_fll_win.sym", WXY, "xwin", 500, 600)
    L = s.sub("sspll_fll_lockdet.sym", LXY, "xld", 1300, 300)
    for X in (P, W, L):
        stub(s, X["VDDD"], "VDDD", 0, -40, 0); stub(s, X["VSSD"], "VSSD", 0, 40, 0)
    for nm in ("refclk", "div"):
        stub(s, P[nm], nm, -60); stub(s, W[nm], nm, -60)
    stub(s, P["fll_en"], "fll_en", -60); stub(s, P["act"], "act", -60)
    stub(s, P["up"], "up", 60); stub(s, P["dn"], "dn", 60); stub(s, P["upg"], "upg", 60); stub(s, P["dng"], "dng", 60)
    stub(s, W["lock"], "lock", -60)
    for nm in ("refw", "divw", "cclk"):
        stub(s, W[nm], nm, 60)
    for nm in ("up", "dn", "refw", "divw", "cclk", "fll_en"):
        stub(s, L[nm], nm, -60)
    for nm in ("lock", "act", "lock_det", "fll_dir"):
        stub(s, L[nm], nm, 60)
    pins_left(s, ["refclk", "div", "fll_en"], y0=1100)
    pins_right(s, ["upg", "dng", "act", "lock_det", "fll_dir"], 2000, y0=1100)
    s.pin("VDDD", "inout", 100, 1300); stub(s, (100, 1300), "VDDD", 80, 0)
    s.pin("VSSD", "inout", 100, 1360); stub(s, (100, 1360), "VSSD", 80, 0)
    return s


def top(DXY, LGXY, CPXY, LSXY):
    s = Sch("sspll_fll_hv")
    s.text("sspll_fll_hv (FLL design): clkp / 16 against refclk; PFD with dead zone and lock detector on VDDD; level shifters;",
           40, -500, 0.3)
    s.text("60 uA current-steering charge pump on VDDA into the loop filter (vctl). The pump is off while lock_det = 1.", 40, -460, 0.3)
    Dv = s.sub("sspll_fll_div16.sym", DXY, "xdv", 400, 0)
    Lg = s.sub("sspll_fll_logic.sym", LGXY, "xlg", 1000, 0)
    s.pin("clkp", "in", 100, Dv["clkp"][1]); s.wire((100, Dv["clkp"][1]), Dv["clkp"])
    s.wire(Dv["div"], (Dv["div"][0] + 80, Dv["div"][1])); s.label("div", Dv["div"][0] + 80, Dv["div"][1], flip=1)
    stub(s, Lg["div"], "div", -60)
    s.pin("refclk", "in", 100, -300); stub(s, (100, -300), "refclk", 80, 0); stub(s, Lg["refclk"], "refclk", -60)
    s.pin("fll_en", "in", 100, -360); stub(s, (100, -360), "fll_en", 80, 0); stub(s, Lg["fll_en"], "fll_en", -60)
    for X in (Dv, Lg):
        stub(s, X["VDDD"], "VDDD", 0, -40, 0); stub(s, X["VSSD"], "VSSD", 0, 40, 0)
    outs = {}
    for k, (nm, o, ob) in enumerate((("upg", "up5", "up5b"), ("dng", "dn5", "dn5b"), ("act", "act5", "act5b"))):
        L = s.sub("../cco_hv/sspll_ls_1v8_3v3.sym", LSXY, f"xl{nm[0]}", 1700, -250 + 300*k)
        stub(s, Lg[nm], nm, 60); stub(s, L["in"], nm, -60); stub(s, L["out"], o, 60); stub(s, L["outb"], ob, 60)
        for sup, fl in (("VDDD", 0), ("VDDA", 1)):
            stub(s, L[sup], sup, 0, -40, fl)
        for sup, fl in (("VSSA", 0), ("VSSD", 1)):
            stub(s, L[sup], sup, 0, 40, fl)
    C = s.sub("sspll_fll_cp.sym", CPXY, "xcp", 2300, 0)
    for nm in ("ib", "up5", "up5b", "dn5", "dn5b", "act5b"):
        stub(s, C[nm], nm, -60)
    stub(s, C["VDDA"], "VDDA", 0, -40, 0); stub(s, C["VSSA"], "VSSA", 0, 40, 0)
    s.pin("vctl", "inout", C["vctl"][0] + 200, C["vctl"][1], flip=1); s.wire(C["vctl"], (C["vctl"][0] + 200, C["vctl"][1]))
    s.pin("ib", "inout", 100, 500); stub(s, (100, 500), "ib", 80, 0)
    stub(s, Lg["lock_det"], "lock_det", 60); stub(s, Lg["fll_dir"], "fll_dir", 60)
    pins_right(s, ["lock_det", "fll_dir"], 2700, y0=500)
    for k, sup in enumerate(("VDDA", "VDDD", "VSSA", "VSSD")):
        s.pin(sup, "inout", 100, 600 + 60*k); stub(s, (100, 600 + 60*k), sup, 80, 0)
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p = F.D
    S = {}
    S["ds"] = symbol(os.path.join(OUT, "sspll_fll_ds.sym"), "sspll_fll_ds", left=[("in", "in")], right=[("out", "out")],
                     top=[("VDDD", "inout")], bottom=[("VSSD", "inout")])
    S["tspc"] = symbol(os.path.join(OUT, "sspll_fll_tspc.sym"), "sspll_fll_tspc", left=[("ck", "in")],
                       right=[("q", "out"), ("qb", "out")], top=[("VDDD", "inout")], bottom=[("VSSD", "inout")])
    S["div16"] = symbol(os.path.join(OUT, "sspll_fll_div16.sym"), "sspll_fll_div16", left=[("clkp", "in")],
                        right=[("div", "out")], top=[("VDDD", "inout")], bottom=[("VSSD", "inout")])
    S["pfd"] = symbol(os.path.join(OUT, "sspll_fll_pfd.sym"), "sspll_fll_pfd",
                      left=[("refclk", "in"), ("div", "in"), ("fll_en", "in"), ("act", "in")],
                      right=[("up", "out"), ("dn", "out"), ("upg", "out"), ("dng", "out")],
                      top=[("VDDD", "inout")], bottom=[("VSSD", "inout")])
    S["win"] = symbol(os.path.join(OUT, "sspll_fll_win.sym"), "sspll_fll_win",
                      left=[("refclk", "in"), ("div", "in"), ("lock", "in")],
                      right=[("refw", "out"), ("divw", "out"), ("cclk", "out")], top=[("VDDD", "inout")],
                      bottom=[("VSSD", "inout")])
    S["lockdet"] = symbol(os.path.join(OUT, "sspll_fll_lockdet.sym"), "sspll_fll_lockdet",
                          left=[("up", "in"), ("dn", "in"), ("refw", "in"), ("divw", "in"), ("cclk", "in"), ("fll_en", "in")],
                          right=[("lock", "out"), ("act", "out"), ("lock_det", "out"), ("fll_dir", "out")],
                          top=[("VDDD", "inout")], bottom=[("VSSD", "inout")])
    S["logic"] = symbol(os.path.join(OUT, "sspll_fll_logic.sym"), "sspll_fll_logic",
                        left=[("refclk", "in"), ("div", "in"), ("fll_en", "in")],
                        right=[("upg", "out"), ("dng", "out"), ("act", "out"), ("lock_det", "out"), ("fll_dir", "out")],
                        top=[("VDDD", "inout")], bottom=[("VSSD", "inout")])
    S["cp"] = symbol(os.path.join(OUT, "sspll_fll_cp.sym"), "sspll_fll_cp",
                     left=[("ib", "inout"), ("up5", "in"), ("up5b", "in"), ("dn5", "in"), ("dn5b", "in"), ("act5b", "in")],
                     right=[("vctl", "inout")], top=[("VDDA", "inout")], bottom=[("VSSA", "inout")])
    symbol(os.path.join(OUT, "sspll_fll_hv.sym"), "sspll_fll_hv",
           left=[("clkp", "in"), ("refclk", "in"), ("fll_en", "in"), ("ib", "inout")],
           right=[("vctl", "inout"), ("lock_det", "out"), ("fll_dir", "out")],
           top=[("VDDA", "inout"), ("VDDD", "inout")], bottom=[("VSSA", "inout"), ("VSSD", "inout")])
    LSXY = symbol("/tmp/ls_tmp.sym", "sspll_ls_1v8_3v3", **LS_PINS)
    sheets = [("sspll_fll_ds", ds(p)), ("sspll_fll_tspc", tspc(p)), ("sspll_fll_div16", div16(S["ds"], S["tspc"])),
              ("sspll_fll_pfd", pfd()), ("sspll_fll_win", win()), ("sspll_fll_lockdet", lockdet()),
              ("sspll_fll_logic", logic(S["pfd"], S["win"], S["lockdet"])), ("sspll_fll_cp", cp(p)),
              ("sspll_fll_hv", top(S["div16"], S["logic"], S["cp"], LSXY))]
    bad = 0
    for name, sch in sheets:
        errs = sch.save(os.path.join(OUT, name + ".sch"))
        bad += len(errs)
        print(name, ":", "\n  ".join(errs[:12]) or "drawing check clean")
    ref = F.fll_top()
    open(os.path.join(ROOT, "xschem", "netlist", "ref_fll_hv.spice"), "w").write(ref)
