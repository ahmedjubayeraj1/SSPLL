"""clkgen_hv.py - roadmap step 77 redone for the device-rule migration: the 1.8 V clock generator (kept, now on VDDD)
plus level shifters and 5 V drivers, so the SSPD switches and the pulsed-Gm switches (5 V devices on VDDA) get
0 / 3.3 V control pairs.

 refhv (VDDA, receiver S2) ────────────────────────────────────────── drv5 ── cks (falls = sample), cksb
 refclk (VDDD) ─ xi0, xi1 ─ r2 ─┐
                                ├─ xi2, xi3 ─ g2 ─ pulser_g ─ start_g ─ LS_G1 ─ inv5 ─┐
                                │                         └─ stop_g ── LS_G2 ─── pout5 (2 step drivers, NOR / NAND) ── ckg / ckgb
                                │                         └─ pg (1.8 V pulse) ─ hlatch (reset by r1 = refclk low)
                                │                                                  └─ hin ─ pulser_h ─ start_h / stop_h
                                └────────────────────────────────── LS_H1 / LS_H2 ─ pout5 ── ckh / ckhb (W_H)

Edge-pair level shifting (new in this redo). A cross-coupled level shifter has a fast rising output (its input nMOS
pulls the latch) and a slow falling output (the latch must flip back), about 0.2-0.4 ns apart at ss. A 200 ps Gm
pulse sent through one level shifter would shrink by that difference or vanish, and a 200 ps pulse sent through a
5 V buffer chain is filtered away by its slow edges. So each pulse is sent as two RISING steps, start and stop,
through two identical level shifters and two identical step drivers, and the pulse is formed only at the output
gates (start AND NOT stop): both edges see the same delay, the width survives. The sampling edge also uses the rising
(fast) output. Every falling edge happens when refclk falls, where nothing is timed.
The sampling edge itself does not cross the domains at all: it comes from the receiver's 3.3 V node (refhv).

Every device is (model, W per finger, nf, L)."""
import os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "cco"))
sys.path.insert(0, os.path.join(ROOT, "design", "refbuf"))
import clkgen as C
import cco_hv as CC
LIB, run, xings, _m, inv, nor2 = C.LIB, C.run, C.xings, C._m, C.inv, C.nor2
N5, P5 = "nfet_g5v0d10v5", "pfet_g5v0d10v5"

D = dict(C.D)
D.update(
    # 5 V gates sized for equal rise and fall delay: thick-oxide pMOS / nMOS = 2.5 (step77hv_size.py: 61 / 62 ps at
    # fan-out 1); the drivers taper by about 3 per stage
    INV5S=((N5, 1.0, 1, 0.5), (P5, 2.5, 1, 0.5)),       # 5 V small inverter
    INV5M=((N5, 2.5, 1, 0.5), (P5, 6.25, 1, 0.5)),      # 5 V medium
    INV5L=((N5, 4.0, 2, 0.5), (P5, 10.0, 2, 0.5)),      # 5 V driver output stage (8 / 20 um total)
    INV5A=((N5, 2.5, 1, 0.5), (P5, 6.25, 1, 0.5)),      # first inverter of the driver's in-phase (2-stage) path
    TG5T=((N5, 0.75, 1, 0.5), (P5, 0.75, 1, 0.5)),        # the same TG in the step drivers of the pulse outputs
    TG5=((N5, 1.5, 1, 0.5), (P5, 1.5, 1, 0.5)),         # always-on transmission gate in the in-phase path: it adds
                                                        # about one inverter delay, so o and ob switch together
    INV5T=((N5, 2.0, 1, 0.5), (P5, 5.0, 1, 0.5)),       # output stage of the step drivers inside the pulse outputs
    NOR5L=((N5, 2.0, 1, 0.5), (P5, 5.0, 2, 0.5)),       # pulse output NOR: series pMOS 5x the nMOS (10 um each)
    NAND5L=((N5, 2.0, 2, 0.5), (P5, 5.0, 1, 0.5)),      # pulse output NAND: series nMOS 4 um each, pMOS 5 um
    CG=("cap_mim_m3_1", 4.0, 1, 4.0),                   # Gm pulser C: tau ~ 530 ps typ, >= 280 ps at ff_ll / 110 C
                                                        # (a 210 ps pulse no longer reaches full swing there)
    CH=("cap_mim_m3_1", 4.5, 1, 4.5),                   # hold pulser C (W_H ~1.8 ns tt, so the hold ends before tracking
                                                        # resumes at the slowest corner with the longer gap 1)
    # gap-1 delay (added after step 79): the pulsed Gm needs about 2-3 ns after the sample to recover from the 800 MHz
    # tracking swing of the SSPD (its degeneration R_S x source capacitance); with the 0.6 ns gap the charge per period
    # at lock was 4.4 fC and the gain 73 % of G tau, with 3 ns 0.7 fC and 102 % (step79hv_det.py / recovery runs)
    RDL=("res_xhigh_po_0p35", 0.35, 1, 6.0), CDL=("cap_mim_m3_1", 5.3, 1, 5.3),
)
# loads of the 3.3 V pairs: 5 V switch gates of the SSPD (step 78) and the Gm (step 79), estimated about 2x the
# 1.8 V switches of 13 Nov (thick oxide: 1/3 the C per area, but longer and wider devices); checked in steps 78 / 79
LOADS = dict(cks=60e-15, cksb=60e-15, ckh=40e-15, ckhb=40e-15, ckg=40e-15, ckgb=40e-15)


def inv5(name, a, y, size, vdd="VDDA", vss="VSSA"):
    n, p = size
    return _m(name + "n", y, a, vss, vss, n) + _m(name + "p", y, a, vdd, vdd, p)


def _d(text):
    """A 1.8 V cell from the clkgen.py helpers (which write VDD / VSS) moved onto the digital rails VDDD / VSSD."""
    return re.sub(r"\bVSS\b", "VSSD", re.sub(r"\bVDD\b", "VDDD", text))


def cells(p=D):
    """Subcircuits: 1.8 V pulser cores with start/stop taps (VDDD / VSSD), the 5 V driver and pulse combiner
    (VDDA / VSSA), the level shifter (step 75 HV; input on VDDD / VSSD, output on VDDA / VSSA) and the top cell
    sspll_clkgen_hv. Ground split (24 Nov 2026): every 1.8 V device and the RC timing parts of the 1.8 V cells return to
    VSSD, every 5 V device to VSSA."""
    c = CC.LS
    # 1.8 V cells (VDDD / VSSD)
    for nm, R, Cc in (("g", "RG", "CG"), ("h", "RH", "CH")):
        rm, w, _, L = p[R]; cm, cw, _, cl = p[Cc]
        e = (f".subckt sspll_ckg_edges_{nm} in stop pls VDD VSS\n"
             f"* RC edge pair: stop rises ln2 RC + 2 gates after in rises; pls = in AND NOT stop (1.8 V pulse)\n")
        e += inv("x1", "in", "inb", p["INVS"]) + inv("x2", "in", "drc", p["INVS"])
        e += f"xr drc rc VSS sky130_fd_pr__{rm} l={L} mult=1 m=1\n"
        e += f"xc rc VSS sky130_fd_pr__{cm} w={cw} l={cl} m=1\n"
        e += inv("x3", "rc", "stop", p["INVS"]) + nor2("x4", "inb", "stop", "pls", p["NOR"])
        c += _d(e) + ".ends\n"
    rm, _, _, L = p["RDL"]; cm, cw, _, cl = p["CDL"]
    c += _d(".subckt sspll_ckg_dly in out VDD VSS\n* RC delay (1.8 V): both edges delayed by about ln2 RC + 4 gates; non-inverting\n" +
          inv("x1", "in", "a", p["INVS"]) + f"xr a rc VSS sky130_fd_pr__{rm} l={L} mult=1 m=1\n"
          f"xc rc VSS sky130_fd_pr__{cm} w={cw} l={cl} m=1\n" + inv("x2", "rc", "b", p["INVS"]) +
          inv("x3", "b", "c", p["INVS"]) + inv("x4", "c", "out", p["INVS"]) + ".ends\n")   # x2-x4 restore a sharp edge
    c += _d(".subckt sspll_ckg_hlatch s r out VDD VSS\n* NOR latch q = set by s, reset by r; out = q AND NOT s\n" +
          nor2("xl1", "r", "qb", "q", p["NOR"]) + nor2("xl2", "s", "q", "qb", p["NOR"]) +
          nor2("xl3", "qb", "s", "out", p["NOR"]) + ".ends\n")
    # 5 V cells (VDDA / VSSA)
    for nm, L, TG in (("drv5", "INV5L", "TG5"), ("drv5t", "INV5T", "TG5T")):
        tn, tp = p[TG]
        c += (f".subckt sspll_ckg_{nm} in o ob VDDA VSSA\n* 5 V complementary driver: o follows in (TG + 2 inverters), ob is\n"
              "* inverted (3 inverters); the always-on TG matches the extra inverter so o and ob switch together\n" +
              _m("tn", "a0", "VDDA", "in", "VSSA", tn) + _m("tp", "a0", "VSSA", "in", "VDDA", tp) +
              inv5("xa", "a0", "a1", p["INV5A"]) + inv5("xb", "a1", "o", p[L]) +
              inv5("xc", "in", "c1", p["INV5S"]) + inv5("xd", "c1", "c2", p["INV5M"]) + inv5("xe", "c2", "ob", p[L]) + ".ends\n")
    (nn, np_), (an, ap) = p["NOR5L"], p["NAND5L"]
    c += (".subckt sspll_ckg_pout5 start stop o ob VDDA VSSA\n"
          "* 5 V pulse output: start and stop are rising STEPS (never a narrow pulse inside a buffer chain); each gets a\n"
          "* complementary step driver, and the pulse exists only at the two output gates:\n"
          "* o = NOR(NOT start, stop) = start AND NOT stop;  ob = NAND(start, NOT stop) = NOT o\n"
          "xda start st stb VDDA VSSA sspll_ckg_drv5t\nxdb stop sp spb VDDA VSSA sspll_ckg_drv5t\n" +
          _m("na", "o", "stb", "VSSA", "VSSA", nn) + _m("nb", "o", "sp", "VSSA", "VSSA", nn) +
          _m("pa", "ox", "stb", "VDDA", "VDDA", np_) + _m("pb", "o", "sp", "ox", "VDDA", np_) +
          _m("ma", "ob", "st", "oy", "VSSA", an) + _m("mb", "oy", "spb", "VSSA", "VSSA", an) +
          _m("qa", "ob", "st", "VDDA", "VDDA", ap) + _m("qb", "ob", "spb", "VDDA", "VDDA", ap) + ".ends\n")
    c += ".subckt sspll_clkgen_hv refclk refhv cks cksb ckg ckgb ckh ckhb VDDD VDDA VSSA VSSD\n"
    c += _d(inv("xi0", "refclk", "r1", p["INVM"]) + inv("xi1", "r1", "r2", p["INVM"]))
    # sampling edge: taken from refhv, the receiver's 3.3 V edge (S2 output, VDDA domain), straight into the 5 V
    # driver: no VDDD gate in the sampling path (through refclk, the level shifter and two VDDD inverters the edge
    # moved 376 ps per volt of VDDD, step77hv_supply_via_vddd.json)
    c += "xds refhv cksb cks VDDA VSSA sspll_ckg_drv5\n"
    # Gm pulse: gap 1 (RC delay, about 2.4 ns, then the edge pair), two level shifters, rebuild, driver
    c += "xdl r2 g2 VDDD VSSD sspll_ckg_dly\n"
    c += "xeg g2 gstop pg VDDD VSSD sspll_ckg_edges_g\n"
    c += "xlsg1 g2 g2h g2hb VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\nxlsg2 gstop gsh gshb VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\n"
    c += "xpg g2h gsh ckg ckgb VDDA VSSA sspll_ckg_pout5\n"
    # hold pulse: latch set by the 1.8 V Gm pulse, reset while refclk is low (r1 = 1); hin rises when the Gm pulse ends
    c += "xhl pg r1 hin VDDD VSSD sspll_ckg_hlatch\n"
    # gap 2: four 1.8 V inverters between the latch and the hold edges (gap 2 >= 100 ps at every corner; with two it
    # was 79 ps at fs, step77hv_sim.py first run)
    c += _d(inv("xi4", "hin", "h1", p["INVS"]) + inv("xi5", "h1", "h2", p["INVS"]) +
            inv("xi6", "h2", "h3", p["INVS"]) + inv("xi7", "h3", "h4", p["INVS"]))
    c += "xeh h4 hstop ph VDDD VSSD sspll_ckg_edges_h\n"
    c += "xlsh1 h4 hinh hinhb VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\nxlsh2 hstop hsh hshb VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\n"
    c += "xph hinh hsh ckh ckhb VDDA VSSA sspll_ckg_pout5\n"
    return c + ".ends\n"


def tran(corner="tt", temp=27, vddd=1.8, vdda=3.3, fref=50e6, vpp=3.3, wave="square", p=D, ncyc=4, loads=LOADS):
    """Timing with the real receiver in front (step 76 HV: refclk on VDDD and refhv on VDDA come from it), outputs read
    at VDDA/2: t_s (REF_IN rising -> cks falling), skews, gap1, tau, gap2, W_H, t_p (sample -> middle of the Gm pulse),
    edge times, power of the clock generator alone (receiver currents subtracted with a second run without it is not
    possible on shared rails: the clock generator's VDDA / VDDD come from their own sources here)."""
    import refbuf_hv as H
    T = 1/fref
    b = H.op(corner, temp, vdda, vddd)
    rx = H.full().replace(CC.LS, "")
    net = (f"* clkgen hv + receiver\n.lib {LIB} {corner}\n.temp {temp}\n{rx}{cells(p)}"
           f"vdda VDDA 0 {vdda}\nvddd VDDD 0 {vddd}\nvdda2 VDDA2 0 {vdda}\nvddd2 VDDD2 0 {vddd}\n"
           f"iib ib 0 2.5e-6\nven pll_en 0 {vddd}\n" + H.src(vdda, vpp, fref, wave) +
           "xrx pad0 refclk refhv ib pll_en VDDA VDDD 0 0 sspll_refbuf_hv\n"
           "x1 refclk refhv cks cksb ckg ckgb ckh ckhb VDDD2 VDDA2 0 0 sspll_clkgen_hv\n" +
           "".join(f"c{k} {k} 0 {v}\n" for k, v in loads.items()) +
           f".ic v(xrx.vin)={b['vin']} v(xrx.s1)={b['s1']}\n"
           f".control\ntran 2p {ncyc*T}\nwrdata w.txt v(pad0) v(cks) v(cksb) v(ckh) v(ckhb) v(ckg) v(ckgb) i(vddd2) i(vdda2)\n.endc\n.end\n")
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; t = z[:, 0]
    sig = {k: z[:, 2*i + 1] for i, k in enumerate(["pad", "cks", "cksb", "ckh", "ckhb", "ckg", "ckgb", "idd", "ida"])}
    m = vdda/2; t0 = (ncyc - 1)*T - 1e-12
    e = lambda k, r, lev=m: next(x for x in xings(t, sig[k], lev, r) if x > t0)
    ref = e("pad", True)
    s_f, sb_r = e("cks", False), e("cksb", True)
    h_r, h_f = e("ckh", True), e("ckh", False)
    g_r, g_f, gb_f = e("ckg", True), e("ckg", False), e("ckgb", False)
    w = t > (ncyc - 1)*T
    Pd = -vddd*np.trapezoid(sig["idd"][w], t[w])/(t[w][-1] - t[w][0])
    Pa = -vdda*np.trapezoid(sig["ida"][w], t[w])/(t[w][-1] - t[w][0])
    def rise(k, falling=False):
        lo, hi_ = (0.9*vdda, 0.1*vdda) if falling else (0.1*vdda, 0.9*vdda)
        a = next(x for x in xings(t, sig[k], lo, not falling) if x > t0)
        b_ = next(x for x in xings(t, sig[k], hi_, not falling) if x > a)
        return b_ - a
    return dict(t_s=s_f - ref, skew_s=sb_r - s_f, gap1=g_r - max(s_f, sb_r), tau=g_f - g_r, skew_g=gb_f - g_r,
                gap2=h_r - max(g_f, gb_f), W_H=h_f - h_r, t_p=(g_r + g_f)/2 - s_f, fall_cks=rise("cks", True),
                rise_ckg=rise("ckg"), p_vddd=Pd, p_vdda=Pa, power=Pd + Pa)


def lvs_reference(p=D):
    return cells(p)
