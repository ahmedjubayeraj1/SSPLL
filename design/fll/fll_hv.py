"""fll_hv.py - the frequency-locked loop (FLL) that brings the ring to 16 x f_ref before the
sub-sampling loop takes over. Digital on VDDD / VSSD (1.8 V devices and sky130_fd_sc_hd standard cells), the charge
pump on VDDA / VSSA (5 V devices).

  clkp (3.3 V, ring buffer) -> DS (3.3 -> 1.8 V down-shifter) -> 4 x TSPC /2 -> div (50 MHz)
  refclk (1.8 V) and div -> PFD (2 x dfrtp + nand2 reset) -> UP / DN
  UP / DN -> dead zone (AND with a 0.3 ns delayed copy) -> AND NOT lock_det -> level shifters -> 5 V charge pump -> vctl
  UP / DN -> lock detector (effective window about 0.6 ns to acquire, 2 ns to hold; 16 periods in, 4 out)
           -> lock_det, fll_dir
Every MOS device is (model, W per finger, fingers, L)."""
import os, sys, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "clkgen"))
from clkgen import _m, LIB, spinit, xings
import subprocess, tempfile


def run(net, files=(), timeout=30000):
    """ngspice batch run (as clkgen.run, with a longer time limit for the µs-long FLL transients)"""
    with tempfile.TemporaryDirectory() as d:
        spinit(d)
        open(os.path.join(d, "r.sp"), "w").write(net)
        pr = subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d, timeout=timeout)
        out = pr.stdout + "\n[stderr]\n" + pr.stderr[-3000:]
        data = {f: np.loadtxt(os.path.join(d, f)) for f in files if os.path.exists(os.path.join(d, f))}
    return out, data
N18, P18, N5, P5 = "nfet_01v8", "pfet_01v8", "nfet_g5v0d10v5", "pfet_g5v0d10v5"

D = dict(
    DSN=(N5, 1.0, 1, 0.5), DSP=(P5, 3.0, 2, 0.5),        # down-shifter: 5 V inverter on VDDD (input swings to VDDA)
    DSI=((N18, 1.0, 1, 0.15), (P18, 2.0, 1, 0.15)),      # 1.8 V inverters after it
    # TSPC /2: stage 1 (p-stack, D = qb), stage 2 (precharge), stage 3 (output)
    T1N=(N18, 0.84, 1, 0.15), T1P=(P18, 1.26, 1, 0.15),
    T2N=(N18, 0.84, 1, 0.15), T2P=(P18, 0.84, 1, 0.15),
    T3N=(N18, 0.84, 1, 0.15), T3P=(P18, 1.26, 1, 0.15),
    TI=((N18, 0.65, 1, 0.15), (P18, 1.0, 1, 0.15)),      # inverter q = not qb (clock of the next stage)
)


def tspc(p=D):
    """positive-edge TSPC flip-flop with D = qb: divides ck by 2. q = not qb."""
    return (".subckt sspll_fll_tspc ck q qb VDDD VSSD\n"
            "* TSPC /2: stage 1 x = not qb while ck low; stage 2 precharges y while ck low, y = not x on the rising edge;"
            "\n* stage 3 qb = not y while ck high (holds while ck low); q = not qb\n" +
            _m("p1a", "a", "qb", "VDDD", "VDDD", p["T1P"]) + _m("p1b", "x", "ck", "a", "VDDD", p["T1P"]) +
            _m("n1", "x", "qb", "VSSD", "VSSD", p["T1N"]) +
            _m("p2", "y", "ck", "VDDD", "VDDD", p["T2P"]) + _m("n2a", "y", "x", "b", "VSSD", p["T2N"]) +
            _m("n2b", "b", "ck", "VSSD", "VSSD", p["T2N"]) +
            _m("p3", "qb", "y", "VDDD", "VDDD", p["T3P"]) + _m("n3a", "qb", "ck", "c", "VSSD", p["T3N"]) +
            _m("n3b", "c", "y", "VSSD", "VSSD", p["T3N"]) +
            _m("ni", "q", "qb", "VSSD", "VSSD", p["TI"][0]) + _m("pi", "q", "qb", "VDDD", "VDDD", p["TI"][1]) +
            ".ends\n")


def ds(p=D):
    n, pp = p["DSI"]
    return (".subckt sspll_fll_ds in out VDDD VSSD\n"
            "* 3.3 -> 1.8 V down-shifter: a 5 V inverter on VDDD takes the 0..VDDA clock on its thick gates;\n"
            "* two 1.8 V inverters restore the edges (out in phase with in)\n" +
            _m("dn", "o1", "in", "VSSD", "VSSD", p["DSN"]) + _m("dp", "o1", "in", "VDDD", "VDDD", p["DSP"]) +
            _m("i1n", "o2", "o1", "VSSD", "VSSD", n) + _m("i1p", "o2", "o1", "VDDD", "VDDD", pp) +
            _m("i2n", "out", "o2", "VSSD", "VSSD", n) + _m("i2p", "out", "o2", "VDDD", "VDDD", pp) + ".ends\n")


def div16(p=D):
    return (tspc(p) + ds(p) +
            ".subckt sspll_fll_div16 clkp div VDDD VSSD\n* clkp (0..VDDA) -> down-shifter -> 4 x TSPC /2 -> div = clkp / 16\n"
            "xds clkp c0 VDDD VSSD sspll_fll_ds\n"
            "xt1 c0 c1 c1b VDDD VSSD sspll_fll_tspc\nxt2 c1 c2 c2b VDDD VSSD sspll_fll_tspc\n"
            "xt3 c2 c3 c3b VDDD VSSD sspll_fll_tspc\nxt4 c3 div c4b VDDD VSSD sspll_fll_tspc\n.ends\n")


def div_test(fin, corner="tt", temp=27, vddd=1.8, vdda=3.3, tr=60e-12, p=D, ncyc=48, cload=10e-15):
    """drive clkp with a 0..VDDA square at fin; count div edges after settling. Returns (ratio, t_delay, I(VDDD))."""
    T_ = 1/fin; tstop = (ncyc + 16)*T_*1.0 + 16*16*T_
    net = (f"* div16\n.lib {LIB} {corner}\n.temp {temp}\n{div16(p)}vdd VDDD 0 {vddd}\nvss VSSD 0 0\n"
           f"vin clkp 0 pulse(0 {vdda} {T_/2} {tr} {tr} {T_/2 - tr} {T_})\n"
           f"x1 clkp div VDDD VSSD sspll_fll_div16\ncl div 0 {cloada if False else cload}\n" if False else
           f"* div16\n.lib {LIB} {corner}\n.temp {temp}\n{div16(p)}vdd VDDD 0 {vddd}\nvss VSSD 0 0\n"
           f"vin clkp 0 pulse(0 {vdda} {T_/2} {tr} {tr} {T_/2 - tr} {T_})\n"
           f"x1 clkp div VDDD VSSD sspll_fll_div16\ncl div 0 {cload}\n"
           f".control\ntran {T_/40} {tstop} 0 {T_/40}\nwrdata w.txt v(div) v(clkp) i(vdd)\n.endc\n.end\n")
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; t, v, vin, i = z[:, 0], z[:, 1], z[:, 3], z[:, 5]
    tr_ = xings(t, v, vddd/2)
    tr_ = tr_[tr_ > 0.25*tstop]
    if len(tr_) < 3:
        return 0.0, None, None
    per = np.diff(tr_)
    ratio = np.median(per)/T_
    okp = np.allclose(per, 16*T_, rtol=0.02)
    return (ratio if okp else -ratio), None, float(-np.mean(i[t > 0.25*tstop]))


# ------------------------------------------------------------------ standard cells (sky130_fd_sc_hd)
STDLIB = os.path.join(HERE, "stdcells", "sky130_fd_sc_hd_fll.spice")
_PORTS = {m.group(1): m.group(2).split() for m in re.finditer(r"^\.subckt (\S+) (.*)$", open(STDLIB).read(), re.M)}


def sc(name, cell, vdd="VDDD", vss="VSSD", **pins):
    """instance of sky130_fd_sc_hd__<cell>: pins by name (A=..., Y=...), supplies VPWR/VPB = vdd, VGND/VNB = vss"""
    ports = _PORTS["sky130_fd_sc_hd__" + cell]
    sup = dict(VPWR=vdd, VPB=vdd, VGND=vss, VNB=vss)
    nets = [sup[p] if p in sup else pins[p] for p in ports]
    return f"x{name} {' '.join(nets)} sky130_fd_sc_hd__{cell}\n"


# ------------------------------------------------------------------ PFD, dead zone, lock detector (standard cells, VDDD)
def pfd():
    return (".subckt sspll_fll_pfd refclk div fll_en act up dn upg dng VDDD VSSD\n"
            "* PFD: two resettable flip-flops (D = 1) and a NAND reset; reset also held while fll_en = 0.\n"
            "* Dead zone: the charge pump sees only the part of UP / DN longer than about 0.26 ns (removes the reset pulse),\n"
            "* and only while act = 1 (FLL enabled and not locked)\n" +
            sc("fu", "dfrtp_1", CLK="refclk", D="VDDD", RESET_B="rb", Q="up") +
            sc("fd", "dfrtp_1", CLK="div", D="VDDD", RESET_B="rb", Q="dn") +
            sc("rn", "nand2_1", A="up", B="dn", Y="rn") + sc("rd", "buf_1", A="rn", X="rnd") +
            sc("re", "and2_1", A="rnd", B="fll_en", X="rb") +
            sc("zu1", "clkdlybuf4s25_1", A="up", X="upd1") + sc("zu2", "buf_1", A="upd1", X="upd") +
            sc("zd1", "clkdlybuf4s25_1", A="dn", X="dnd1") + sc("zd2", "buf_1", A="dnd1", X="dnd") +
            sc("gu", "and3_1", A="up", B="upd", C="act", X="upg") + sc("gd", "and3_1", A="dn", B="dnd", C="act", X="dng") +
            ".ends\n")


def win():
    c = (".subckt sspll_fll_win refclk div lock refw divw cclk VDDD VSSD\n"
         "* lock-detector windows: refclk and div delayed by three clkdlybuf4s50 (w_in tap, about 1.07 ns at tt) or, while\n"
         "* locked, seven (w_out tap, about 2.5 ns). The effective window is the tap delay minus the PFD reset time\n"
         "* (0.3 ns) and the flip-flop setup time: about 0.6 ns / 2 ns. cclk (the counter clock) comes after both\n")
    for src, t in (("refclk", "r"), ("div", "d")):
        c += (sc(f"w{t}1", "clkdlybuf4s50_1", A=src, X=f"{t}1") +
              "".join(sc(f"w{t}{k}", "clkdlybuf4s50_1", A=f"{t}{k-1}", X=f"{t}{k}") for k in range(2, 8)) +
              sc(f"w{t}m", "mux2_1", A0=f"{t}3", A1=f"{t}7", S="lock", X="refw" if t == "r" else "divw"))
    c += sc("cc1", "clkdlybuf4s25_1", A="r7", X="cc1") + sc("cc2", "buf_1", A="cc1", X="cclk") + ".ends\n"
    return c


def lockdet():
    return (".subckt sspll_fll_lockdet up dn refw divw cclk fll_en lock act lock_det fll_dir VDDD VSSD\n"
            "* o1 = UP still high at refw; o2 = DN still high at divw; out = o1 or o2. inc = lock ? out : not out.\n"
            "* 4-bit run counter c3..c0: counts in-window periods to lock (terminal 15) and, while locked, out-of-window\n"
            "* periods to unlock (terminal 3); the lock flag toggles at the terminal count. act = fll_en and not lock\n" +
            sc("o1", "dfrtp_1", CLK="refw", D="up", RESET_B="fll_en", Q="o1") +
            sc("o2", "dfrtp_1", CLK="divw", D="dn", RESET_B="fll_en", Q="o2") +
            sc("oo", "or2_1", A="o1", B="o2", X="out") + sc("ix", "xnor2_1", A="lock", B="out", Y="inc") +
            sc("s0", "inv_1", A="c0", Y="s0") + sc("s1", "xor2_1", A="c1", B="c0", X="s1") +
            sc("t2", "and2_1", A="c1", B="c0", X="t2") + sc("s2", "xor2_1", A="c2", B="t2", X="s2") +
            sc("t3", "and3_1", A="c2", B="c1", C="c0", X="t3") + sc("s3", "xor2_1", A="c3", B="t3", X="s3") +
            sc("t4", "and2_1", A="c3", B="t3", X="t4") +
            sc("tm", "mux2_1", A0="t4", A1="t2", S="lock", X="term") + sc("tn", "inv_1", A="term", Y="nterm") +
            sc("g", "and2_1", A="inc", B="nterm", X="g") + sc("tg", "and2_1", A="inc", B="term", X="tg") +
            "".join(sc(f"n{i}", "and2_1", A="g", B=f"s{i}", X=f"n{i}") for i in range(4)) +
            "".join(sc(f"c{i}", "dfrtp_1", CLK="cclk", D=f"n{i}", RESET_B="fll_en", Q=f"c{i}") for i in range(4)) +
            sc("lx", "xor2_1", A="lock", B="tg", X="lnext") +
            sc("lf", "dfrtp_1", CLK="cclk", D="lnext", RESET_B="fll_en", Q="lock") +
            sc("li", "inv_1", A="lock", Y="lockb") + sc("la", "and2_1", A="fll_en", B="lockb", X="act") +
            sc("ob1", "buf_1", A="lock", X="lock_det") + sc("ob2", "buf_1", A="o1", X="fll_dir") + ".ends\n")


def logic():
    return (pfd() + win() + lockdet() +
            ".subckt sspll_fll_logic refclk div fll_en upg dng act lock_det fll_dir VDDD VSSD\n"
            "* PFD + dead zone, window delays, lock detector (sky130_fd_sc_hd cells on VDDD / VSSD)\n"
            "xpfd refclk div fll_en act up dn upg dng VDDD VSSD sspll_fll_pfd\n"
            "xwin refclk div lock refw divw cclk VDDD VSSD sspll_fll_win\n"
            "xld up dn refw divw cclk fll_en lock act lock_det fll_dir VDDD VSSD sspll_fll_lockdet\n.ends\n")


# ------------------------------------------------------------------ 5 V charge pump (VDDA / VSSA)
D.update(
    CPN=(N5, 1.0, 1, 4.0),     # nMOS mirror unit (5 uA)
    CPP=(P5, 2.5, 1, 4.0),     # pMOS mirror unit (5 uA)
    NCP=12,                    # I_cp = 12 x 5 uA = 60 uA
    SWN=(N5, 1.0, 1, 0.5), SWP=(P5, 2.0, 1, 0.5),
)


def cp(p=D):
    k = p["NCP"]
    return (".subckt sspll_fll_cp vctl ib up5 up5b dn5 dn5b act5b VDDA VSSA\n"
            f"* FLL charge pump, current-steering: ib (5 uA) -> nMOS diode; sink mirror x{k} steered to vctl by up5 (VCO slow:\n"
            f"* pull vctl down, ring faster) or to VDDA by up5b; source mirror x{k} (through an nMOS x1 -> pMOS diode) steered\n"
            "* to vctl by dn5b low (VCO fast) or to VSSA by dn5 low. The mirrors never leave saturation, so their gates are\n"
            "* not kicked. act5b high (FLL idle or locked) shorts the ib gate: both mirrors off, no current\n" +
            _m("nd", "ib", "ib", "VSSA", "VSSA", p["CPN"]) + _m("nk", "ib", "act5b", "VSSA", "VSSA", p["SWN"]) +
            _m("ns", "ns", "ib", "VSSA", "VSSA", p["CPN"], m=k) +
            _m("su", "vctl", "up5", "ns", "VSSA", p["SWN"]) + _m("sux", "VDDA", "up5b", "ns", "VSSA", p["SWN"]) +
            _m("n1", "pd", "ib", "VSSA", "VSSA", p["CPN"]) +
            _m("pd", "pd", "pd", "VDDA", "VDDA", p["CPP"]) +
            _m("ps", "ps", "pd", "VDDA", "VDDA", p["CPP"], m=k) +
            _m("sd", "vctl", "dn5b", "ps", "VDDA", p["SWP"]) + _m("sdx", "VSSA", "dn5", "ps", "VDDA", p["SWP"]) +
            ".ends\n")


def fll_top(p=D):
    """the whole FLL: ports clkp refclk fll_en ib vctl lock_det fll_dir VDDA VDDD VSSA VSSD"""
    from_cco = open(os.path.join(ROOT, "design", "cco", "cco_hv.py")).read()
    ls = re.search(r'LS = """(.*?)"""', from_cco, re.S).group(1)
    return (div16(p) + logic() + cp(p) + ls +
            ".subckt sspll_fll_hv clkp refclk fll_en ib vctl lock_det fll_dir VDDA VDDD VSSA VSSD\n"
            "* the FLL design FLL: /16, PFD + dead zone + lock detector on VDDD; level shifters; 5 V charge pump on VDDA\n"
            "xdv clkp div VDDD VSSD sspll_fll_div16\n"
            "xlg refclk div fll_en upg dng act lock_det fll_dir VDDD VSSD sspll_fll_logic\n"
            "xlu upg up5 up5b VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\n"
            "xld dng dn5 dn5b VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\n"
            "xla act act5 act5b VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\n"
            "xcp vctl ib up5 up5b dn5 dn5b act5b VDDA VSSA sspll_fll_cp\n.ends\n")


def bench_open(corner="tt", temp=27, vddd=1.8, vdda=3.3, fv=800e6, eps=0.0, t0v=0.0, tstop=400e-9, vctl=1.8,
               fll_en_at=5e-9, ib=5e-6, tstep=5e-12, p=D, extra=""):
    """open-loop FLL bench: clkp = 0..VDDA square at fv*(1+eps) starting at t0v; refclk 1.8 V 50 MHz; vctl held by a
    source (the charge pump current is i(vvc)); returns the waveforms"""
    Tv = 1/(fv*(1 + eps)); tr = 60e-12
    net = (f"* fll open loop\n.lib {LIB} {corner}\n.temp {temp}\n.include {STDLIB}\n{fll_top(p)}"
           f"vdda VDDA 0 {vdda}\nvddd VDDD 0 {vddd}\nvssa VSSA 0 0\nvssd VSSD 0 0\n"
           f"iib VDDA ib {ib}\nvvc vctl 0 {vctl}\n"
           f"ven fll_en 0 pwl(0 0 {fll_en_at} 0 {fll_en_at + 0.1e-9} {vddd})\n"
           f"vref refclk 0 pulse(0 {vddd} 10n 100p 100p 9.9n 20n)\n"
           f"vck clkp 0 pulse(0 {vdda} {t0v} {tr} {tr} {Tv/2 - tr} {Tv})\n"
           "x1 clkp refclk fll_en ib vctl lock_det fll_dir VDDA VDDD VSSA VSSD sspll_fll_hv\n" + extra +
           f".control\nsave v(refclk) v(x1.div) v(x1.xlg.up) v(x1.xlg.dn) v(x1.upg) v(x1.dng) vvc#branch v(lock_det) v(fll_dir) "
           f"v(x1.xlg.xld.out) vdda#branch vddd#branch\noption interp\ntran {tstep} {tstop}\n"
           "wrdata w.txt v(refclk) v(x1.div) v(x1.xlg.up) v(x1.xlg.dn) v(x1.upg) v(x1.dng) i(vvc) v(lock_det) v(fll_dir) "
           "v(x1.xlg.xld.out) i(vdda) i(vddd)\n.endc\n.end\n")
    out, d = run(net, ["w.txt"])
    if "w.txt" not in d:
        raise RuntimeError("ngspice gave no data: " + out[-1500:])
    z = d["w.txt"]
    names = ["ref", "div", "up", "dn", "upg", "dng", "icp", "lock", "dir", "out", "idda", "iddd"]
    return {"t": z[:, 0], **{n: z[:, 2*k + 1] for k, n in enumerate(names)}}
