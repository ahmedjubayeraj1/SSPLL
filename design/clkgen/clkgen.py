"""clkgen.py - roadmap step 77: clock generator for the SSPD and the pulsed-Gm charge pump (SKY130, VDDL = 1.8 V).

From the reference edge (refclk, step 76) it makes three complementary control pairs:
  cks / cksb  sampling switch sw1: tracks the VCO while cks = 1, samples at the refclk rising edge (cks falls)
  ckh / ckhb  hold-transfer switch sw2 (C1 -> C2): a pulse of width W_H that starts a gap after the sampling edge
  ckg / ckgb  Gm current pulse: width tau = 200 ps, starting a gap after the hold pulse ends;
              the delay from the sampling edge to the middle of this pulse is t_p (loop requirement <= 5 ns, 2.5 ns nominal)
Cells: sspll_ckg_drv (complementary driver), sspll_ckg_pulse_h / sspll_ckg_pulse_g (RC pulsers), sspll_clkgen (top).
Every device is (model, W per finger, nf, L)."""
import os, re, subprocess, tempfile
import numpy as np
PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/pdk")
LIB = f"{PDK_ROOT}/sky130A/libs.tech/ngspice/sky130.lib.spice"
N18, P18 = "nfet_01v8", "pfet_01v8"

D = dict(
    INVS=((N18, 0.42, 1, 0.15), (P18, 0.84, 1, 0.15)),      # small inverter
    INVM=((N18, 1.0, 1, 0.15), (P18, 2.0, 1, 0.15)),        # medium
    INVL=((N18, 2.0, 2, 0.15), (P18, 4.0, 2, 0.15)),        # driver output stage (4 / 8 um total)
    NOR=((N18, 0.84, 1, 0.15), (P18, 1.68, 1, 0.15)),       # NOR2: series pMOS are 2x wider
    RH=("res_xhigh_po_0p35", 0.35, 1, 6.0),                 # hold pulser R (length, um)
    CH=("cap_mim_m3_1", 6.0, 1, 6.0),                       # hold pulser C (W x L um)
    RG=("res_xhigh_po_0p35", 0.35, 1, 0.5),                 # Gm pulser R (minimum length: the gates set most of tau)
    CG=("cap_mim_m3_1", 3.5, 1, 3.5),                       # Gm pulser C
)
LOADS = dict(cks=30e-15, cksb=30e-15, ckh=20e-15, ckhb=20e-15, ckg=20e-15, ckgb=20e-15)


def _m(name, d, g, s, b, dev, m=1):
    model, w, nf, l = dev
    ad = int((nf + 1)/2)*w*0.29; as_ = int((nf + 2)/2)*w*0.29
    pd = 2*int((nf + 1)/2)*(w + 0.29); ps = 2*int((nf + 2)/2)*(w + 0.29)
    return (f"x{name} {d} {g} {s} {b} sky130_fd_pr__{model} w={w*nf:.3f} l={l} nf={nf} m={m} "
            f"ad={ad:.4f} as={as_:.4f} pd={pd:.3f} ps={ps:.3f}\n")


def inv(name, a, y, size):
    n, p = size
    return _m(name + "n", y, a, "VSS", "VSS", n) + _m(name + "p", y, a, "VDD", "VDD", p)


def nor2(name, a, b, y, size):
    n, p = size
    return (_m(name + "na", y, a, "VSS", "VSS", n) + _m(name + "nb", y, b, "VSS", "VSS", n) +
            _m(name + "pa", name + "_x", a, "VDD", "VDD", p) + _m(name + "pb", y, b, name + "_x", "VDD", p))


def cells(p=D):
    c = ".subckt sspll_ckg_drv in o ob VDD VSS\n* complementary driver: o follows in (2 stages), ob is inverted (3 stages)\n"
    c += inv("xa", "in", "a1", p["INVS"]) + inv("xb", "a1", "o", p["INVL"])
    c += inv("xc", "in", "c1", p["INVS"]) + inv("xd", "c1", "c2", p["INVM"]) + inv("xe", "c2", "ob", p["INVL"])
    c += ".ends\n"
    for nm, R, C in (("h", "RH", "CH"), ("g", "RG", "CG")):
        rm, w, _, L = p[R]; cm, cw, _, cl = p[C]
        c += (f".subckt sspll_ckg_pulse_{nm} in out VDD VSS\n"
              f"* RC pulser: out = in AND NOT(in delayed by the R-C stage), i.e. a pulse at every rising edge of in\n")
        c += inv("x1", "in", "inb", p["INVS"]) + inv("x2", "in", "drc", p["INVS"])
        c += f"xr drc rc VSS sky130_fd_pr__{rm} l={L} mult=1 m=1\n"
        c += f"xc rc VSS sky130_fd_pr__{cm} w={cw} l={cl} m=1\n"
        c += inv("x3", "rc", "dly", p["INVS"]) + nor2("x4", "inb", "dly", "out", p["NOR"])
        c += ".ends\n"
    c += ".subckt sspll_clkgen refclk cks cksb ckh ckhb ckg ckgb VDD VSS\n"
    c += inv("xi0", "refclk", "r1", p["INVM"]) + inv("xi1", "r1", "r2", p["INVM"])           # input buffer
    c += "xds r2 cksb cks VDD VSS sspll_ckg_drv\n"                                           # sampling pair
    c += inv("xi2", "r2", "h1", p["INVS"]) + inv("xi3", "h1", "h2", p["INVS"])               # gap 1
    c += "xph h2 ph VDD VSS sspll_ckg_pulse_h\nxdh ph ckh ckhb VDD VSS sspll_ckg_drv\n"      # hold pulse
    c += inv("xi4", "ph", "g1", p["INVS"]) + inv("xi5", "g1", "g2", p["INVS"]) + inv("xi6", "g2", "g3", p["INVS"])
    c += "xpg g3 pg VDD VSS sspll_ckg_pulse_g\nxdg pg ckg ckgb VDD VSS sspll_ckg_drv\n"      # Gm pulse
    return c + ".ends\n"


def spinit(d):
    open(os.path.join(d, ".spiceinit"), "w").write(open(os.path.join(os.path.dirname(LIB), "spinit")).read())


def run(net, files=()):
    with tempfile.TemporaryDirectory() as d:
        spinit(d)
        open(os.path.join(d, "r.sp"), "w").write(net)
        out = subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d, timeout=5000).stdout
        data = {f: np.loadtxt(os.path.join(d, f)) for f in files if os.path.exists(os.path.join(d, f))}
    return out, data


def xings(t, v, lev, rising=True):
    a = v - lev
    k = np.where((a[:-1] < 0) & (a[1:] >= 0))[0] if rising else np.where((a[:-1] > 0) & (a[1:] <= 0))[0]
    return t[k] - a[k]*(t[k + 1] - t[k])/(a[k + 1] - a[k])


def tran(corner="tt", temp=27, vdd=1.8, fref=50e6, duty=0.5, tr=300e-12, p=D, ncyc=4):
    """Timing of all outputs over the last cycle; returns delays, widths, gaps, t_p and the supply power."""
    T = 1/fref; hi = duty*T
    net = (f"* clkgen\n.lib {LIB} {corner}\n.temp {temp}\n{cells(p)}vdd VDD 0 {vdd}\n"
           f"vin refclk 0 pulse(0 {vdd} {T/4} {tr/0.8} {tr/0.8} {hi - tr/0.8} {T})\n"
           "x1 refclk cks cksb ckh ckhb ckg ckgb VDD 0 sspll_clkgen\n" +
           "".join(f"c{k} {k} 0 {v}\n" for k, v in LOADS.items()) +
           f".control\ntran 1p {ncyc*T}\nwrdata w.txt v(refclk) v(cks) v(cksb) v(ckh) v(ckhb) v(ckg) v(ckgb) i(vdd)\n.endc\n.end\n")
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; t = z[:, 0]
    sig = {k: z[:, 2*i + 1] for i, k in enumerate(["refclk", "cks", "cksb", "ckh", "ckhb", "ckg", "ckgb", "idd"])}
    m = vdd/2; t0 = (ncyc - 1)*T + T/4 - 1e-12
    e = lambda k, r: next(x for x in xings(t, sig[k], m, r) if x > t0)
    ref = e("refclk", True)
    s_f, sb_r = e("cks", False), e("cksb", True)
    h_r, h_f, hb_f = e("ckh", True), e("ckh", False), e("ckhb", False)
    g_r, g_f, gb_f = e("ckg", True), e("ckg", False), e("ckgb", False)
    w = t > (ncyc - 1)*T
    P = -vdd*np.trapezoid(sig["idd"][w], t[w])/(t[w][-1] - t[w][0])
    def rise(k):
        a = next(x for x in xings(t, sig[k], 0.1*vdd, True) if x > t0); b = next(x for x in xings(t, sig[k], 0.9*vdd, True) if x > a)
        return b - a
    return dict(t_s=s_f - ref, skew_s=sb_r - s_f, gap1=h_r - max(s_f, sb_r), W_H=h_f - h_r, gap2=g_r - h_f,
                tau=g_f - g_r, skew_g=gb_f - g_r, t_p=(g_r + g_f)/2 - s_f, rise_cks=rise("cksb"), rise_ckg=rise("ckg"),
                power=P)


def inv_noise(size, corner="tt", temp=27, vdd=1.8):
    """White drain-current noise (A^2/Hz, at 1 GHz) of an inverter held at its trip point: input = output = V_M."""
    n, p = size
    net = (f"* inv noise\n.lib {LIB} {corner}\n.temp {temp}\nvdd VDD 0 {vdd}\n"
           + inv("x", "a", "y", size).replace(" VSS ", " 0 ") +
           f"vm y ym 0\nvo ym 0 dc {{vtrip}}\nva a 0 dc {{vtrip}} ac 1\nh1 o 0 vm 1\n")
    # trip point: bisection on the DC current through vo
    lo, hi = 0.3*vdd, 0.7*vdd
    for _ in range(18):
        mid = (lo + hi)/2
        out, _ = run(net.replace("{vtrip}", f"{mid:.5f}") + ".control\nop\nprint i(vm)\n.endc\n.end\n")
        i = float(re.search(r"i\(vm\) = (\S+)", out).group(1))
        lo, hi = (mid, hi) if i > 0 else (lo, mid)
    out, _ = run(net.replace("{vtrip}", f"{mid:.5f}") +
                 ".control\noption sparse\nnoise v(o) va lin 1 1e9 1e9\nprint onoise_spectrum\n.endc\n.end\n")
    s = float(re.search(r"onoise_spectrum = (\S+)", out).group(1))
    return s**2, mid
