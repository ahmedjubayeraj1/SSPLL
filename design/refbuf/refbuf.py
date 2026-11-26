"""refbuf.py - roadmap step 76: REF_IN receiver (reference buffer), SKY130.

 REF_IN pad ──┬── C_AC (MIM) ── vin ──┬──────────── S1: current-reuse inverter (thick oxide, VDDA) ── s1 ── S2 ── s2
   R_PU/R_PD  │  (pad held at VDDA/2)  └── R_B (poly) ──┘ (self-bias: vin DC = s1 DC = trip point)
 s2 (0..3.3 V) ── LS: thick-oxide inverter on VDDL ── B1: thin-oxide inverter (VDDL) ── refclk (1.8 V domain)
 Header current source (pMOS, 16 x a 2.5 uA bias unit) limits S1's current and puts its devices in moderate inversion
 (high gm/I -> low noise per uA).  Every device is (model, W per finger, nf, L)."""
import os, re, subprocess, tempfile
import numpy as np
PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/pdk")
LIB = f"{PDK_ROOT}/sky130A/libs.tech/ngspice/sky130.lib.spice"

D = dict(
    N1=("nfet_g5v0d10v5", 10.0, 12, 1.0),     # S1 input nMOS (120 um / 1 um, moderate inversion)
    P1=("pfet_g5v0d10v5", 10.0, 12, 1.0),     # S1 input pMOS, body tied to its source (own n-well)
    PH=("pfet_g5v0d10v5", 2.0, 1, 4.0),       # header unit (mirror of the bias diode), m = MH; long L = low gm, low noise
    PD=("pfet_g5v0d10v5", 2.0, 1, 4.0),       # bias diode (1 unit, fed by 2.5 uA from the bias generator)
    MH=24, IB=2.5e-6, P1BODY="src",
    C_H=1.82e-12,                             # decouples the header node: p1 adds its g_m, header noise is shunted
    R_B=5e6, C_AC=3.64e-12, R_PAD=500e3,
    N2=("nfet_g5v0d10v5", 1.0, 1, 0.5), P2=("pfet_g5v0d10v5", 2.0, 1, 0.5),     # S2 (VDDA)
    NL=("nfet_g5v0d10v5", 1.0, 1, 0.5), PL=("pfet_g5v0d10v5", 2.0, 1, 0.5),     # LS inverter on VDDL
    NB=("nfet_01v8", 1.0, 1, 0.15), PB=("pfet_01v8", 2.0, 1, 0.15),             # B1 (VDDL)
)


def _m(name, d, g, s, b, dev, m=1):
    model, w, nf, l = dev
    ad = int((nf + 1)/2)*w*0.29; as_ = int((nf + 2)/2)*w*0.29
    pd = 2*int((nf + 1)/2)*(w + 0.29); ps = 2*int((nf + 2)/2)*(w + 0.29)
    return (f"x{name} {d} {g} {s} {b} sky130_fd_pr__{model} w={w*nf:.3f} l={l} nf={nf} m={m} "
            f"ad={ad:.4f} as={as_:.4f} pd={pd:.3f} ps={ps:.3f}\n")


def core(p):
    """Ideal-passive receiver: ports pad vin s1 out VDDA VDDL VSS ib (ib: bias current drawn out of the diode)."""
    c = ".subckt rx pad vin s1 out VDDA VDDL VSS ib\n"
    c += f"rpu VDDA pad {p['R_PAD']}\nrpd pad VSS {p['R_PAD']}\ncac pad vin {p['C_AC']}\nrb vin s1 {p['R_B']}\n"
    c += _m("pd", "ib", "ib", "VDDA", "VDDA", p["PD"])
    c += _m("ph", "vh", "ib", "VDDA", "VDDA", p["PH"], m=p["MH"])
    if p["C_H"]:
        c += f"ch vh VDDA {p['C_H']}\n"
    c += _m("p1", "s1", "vin", "vh", "vh" if p["P1BODY"] == "src" else "VDDA", p["P1"]) + _m("n1", "s1", "vin", "VSS", "VSS", p["N1"])
    c += _m("p2", "s2", "s1", "VDDA", "VDDA", p["P2"]) + _m("n2", "s2", "s1", "VSS", "VSS", p["N2"])
    c += _m("pl", "s3", "s2", "VDDL", "VDDL", p["PL"]) + _m("nl", "s3", "s2", "VSS", "VSS", p["NL"])
    c += _m("pb", "out", "s3", "VDDL", "VDDL", p["PB"]) + _m("nb", "out", "s3", "VSS", "VSS", p["NB"])
    return c + ".ends\n"


def run(net, files=()):
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, ".spiceinit"), "w").write(open(f"{PDK_ROOT}/sky130A/libs.tech/ngspice/spinit").read())
        open(os.path.join(d, "r.sp"), "w").write(net)
        out = subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d, timeout=5000).stdout
        data = {f: np.loadtxt(os.path.join(d, f)) for f in files if os.path.exists(os.path.join(d, f))}
    return out, data


def head(corner="tt", temp=27, vdda=3.3, vddl=1.8, ib=None, p=D):
    ib = p["IB"] if ib is None else ib
    return (f"* refbuf\n.lib {LIB} {corner}\n.temp {temp}\n{core(p)}vdda VDDA 0 {vdda}\nvddl VDDL 0 {vddl}\n"
            f"iib ib 0 {ib}\n")


def op(corner="tt", temp=27, vdda=3.3, p=D):
    """Self-bias point: v(vin), I(VDDA), gain of S1 (dc, from a tiny ac at the pad is not possible -> use .tf-like ac)."""
    net = head(corner, temp, vdda, p=p) + """vsrc padx 0 dc 0 ac 1
rs padx pad0 50
cpad pad0 0 1p
x1 pad0 vin s1 out VDDA VDDL 0 ib rx
.control
op
print v(vin)
print v(s1)
print vdda#branch
ac dec 20 1e3 1e9
let g = mag(v(s1)/v(vin))
meas ac a50 find g at=50e6
meas ac a1m find g at=1e6
.endc
.end
"""
    out, _ = run(net)
    g = lambda k: float(re.search(rf"{re.escape(k)}\s*=\s*(\S+)", out).group(1))
    return dict(vin=g("v(vin)"), s1=g("v(s1)"), idd=-g("vdda#branch"), a1m=g("a1m"), a50=g("a50"))


def xings(t, v, lev, rising=True):
    """Interpolated crossing times of v through lev."""
    a = v - lev
    k = np.where((a[:-1] < 0) & (a[1:] >= 0))[0] if rising else np.where((a[:-1] > 0) & (a[1:] <= 0))[0]
    return t[k] - a[k]*(t[k + 1] - t[k])/(a[k + 1] - a[k]), k


def tran(corner="tt", temp=27, vdda=3.3, vpp=1.0, f=50e6, wave="sine", cl=50e-15, p=D, ncyc=14, ib=None, vddl=1.8):
    """Large-signal behaviour: S1 slope at its bias level on the edge that makes out rise, delay pad->out, duty,
    rise time 10-90 %, mean supply currents, S1 swing."""
    T = 1/f; vb = op(corner, temp, vdda, p)["s1"]
    if wave == "sine":
        src = f"vsrc padx 0 sin({vdda/2} {vpp/2} {f})"
    else:   # square around VDDA/2 (AC-coupled), 0.5 ns edges
        src = f"vsrc padx 0 pulse({vdda/2 - vpp/2} {vdda/2 + vpp/2} 0 0.5n 0.5n {T/2 - 0.5e-9} {T})"
    net = head(corner, temp, vdda, vddl, ib=ib, p=p) + f"""{src}
rs padx pad0 50
x1 pad0 vin s1 out VDDA VDDL 0 ib rx
cl out 0 {cl}
.ic v(vin)={vb} v(s1)={vb}
.control
tran 2p {ncyc*T} 0 2p
wrdata w.txt v(pad0) v(s1) v(out) vdda#branch vddl#branch
.endc
.end
"""
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; t = z[:, 0]; pad, s1, out, ia, il = z[:, 1], z[:, 3], z[:, 5], -z[:, 7], -z[:, 9]
    w = t > (ncyc - 5)*T
    tp, _ = xings(t, pad, vdda/2, True); to, _ = xings(t, out, vddl/2, True); tf, _ = xings(t, out, vddl/2, False)
    ts, k = xings(t, s1, vb, False)
    tp, to, tf = tp[tp > (ncyc - 5)*T], to[to > (ncyc - 5)*T], tf[tf > (ncyc - 5)*T]
    ks = k[ts > (ncyc - 5)*T]
    sl = np.array([abs(s1[j + 1] - s1[j])/(t[j + 1] - t[j]) for j in ks])
    dly = np.mean([to[to > x][0] - x for x in tp[:-1]])
    hi = np.mean([tf[tf > x][0] - x for x in to[:-1]])
    t1, _ = xings(t, out, 0.1*vddl, True); t2, _ = xings(t, out, 0.9*vddl, True)
    t1 = t1[t1 > (ncyc - 5)*T]; tr = np.mean([t2[t2 > x][0] - x for x in t1[:-1]])
    tt = t[w]; avg = lambda y: np.trapezoid(y[w], tt)/(tt[-1] - tt[0])
    return dict(slope_s1=float(sl.mean()), delay=float(dly), duty=float(hi/T), trise=float(tr), ia=float(avg(ia)),
                il=float(avg(il)), s1min=float(s1[w].min()), s1max=float(s1[w].max()), vb=vb)


def noise_s1(corner="tt", temp=27, vdda=3.3, p=D, fmin=1e2, fmax=2e10):
    """Output noise PSD (V^2/Hz) of S1 at its self-bias (= crossing) point, pad driven by a 50-ohm source; also the
    contributions of the main devices (integrated, V^2)."""
    net = head(corner, temp, vdda, p=p) + f"""vsrc padx 0 dc {vdda/2} ac 1
rs padx pad0 50
x1 pad0 vin s1 out VDDA VDDL 0 ib rx
.control
option sparse
noise v(s1) vsrc dec 40 {fmin} {fmax}
setplot noise1
wrdata n.txt onoise_spectrum
setplot noise2
print all
.endc
.end
"""
    out, d = run(net, ["n.txt"])
    z = d["n.txt"]
    tot = {m.group(1): float(m.group(2)) for m in re.finditer(r"\n(onoise_\S+)\s*=\s*(\S+)", out)}
    return z[:, 0], z[:, 1]**2, tot


def gain_s1(corner="tt", temp=27, vdda=3.3, p=D, fmin=1e2, fmax=2e10):
    """Small-signal transfer pad -> s1 (complex) at the self-bias point, same source as noise_s1."""
    net = head(corner, temp, vdda, p=p) + f"""vsrc padx 0 dc {vdda/2} ac 1
rs padx pad0 50
x1 pad0 vin s1 out VDDA VDDL 0 ib rx
.control
option sparse
ac dec 40 {fmin} {fmax}
wrdata g.txt v(s1) v(vin)
.endc
.end
"""
    _, d = run(net, ["g.txt"])
    z = d["g.txt"]
    return z[:, 0], z[:, 1] + 1j*z[:, 2], z[:, 4] + 1j*z[:, 5]


def input_noise(corner="tt", temp=27, vdda=3.3, p=D):
    """Gate-referred (at vin) noise PSD of the receiver, V^2/Hz, single-sided."""
    f, S, _ = noise_s1(corner, temp, vdda, p)
    fg, s1, vi = gain_s1(corner, temp, vdda, p)
    A = s1/vi                                         # amplifier gain vin -> s1 (with the R_B loop closed)
    return f, S/np.abs(np.interp(f, fg, A.real) + 1j*np.interp(f, fg, A.imag))**2, fg, vi


def tnoise(Sw, corner="tt", temp=27, vdda=3.3, vpp=1.0, f=50e6, ncyc=600, nt=10e-12, p=D, cl=50e-15, seed=1,
           wave="sine"):
    """Transient-noise jitter: a white noise voltage of single-sided PSD Sw (V^2/Hz, pad-referred) in series with the
    source; the circuit itself is noiseless. Returns the out rising-edge times (after 20 settling cycles)."""
    T = 1/f; vb = op(corner, temp, vdda, p)["s1"]; na = np.sqrt(Sw/(2*nt))
    src = (f"vsrc padx 0 sin({vdda/2} {vpp/2} {f})" if wave == "sine" else
           f"vsrc padx 0 pulse({vdda/2 - vpp/2} {vdda/2 + vpp/2} 0 0.5n 0.5n {T/2 - 0.5e-9} {T})")
    net = head(corner, temp, vdda, p=p) + f"""{src}
vn padx padn trnoise({na} {nt} 0 0)
rs padn pad0 50
x1 pad0 vin s1 out VDDA VDDL 0 ib rx
cl out 0 {cl}
.ic v(vin)={vb} v(s1)={vb}
.options seed={seed}
.control
tran {nt} {(ncyc + 20)*T} {20*T} {nt}
wrdata w.txt v(out)
.endc
.end
"""
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]
    te, _ = xings(z[:, 0], z[:, 1], 0.9, True)
    return te


def edge_stats(te, f=50e6):
    """Absolute jitter (rms deviation from the best-fit ideal grid) and period jitter."""
    k = np.arange(len(te)); a, b = np.polyfit(k, te, 1)
    dev = te - (a*k + b)
    return dict(abs=float(dev.std()), per=float(np.diff(te).std()), n=len(te), dev=dev)


# ------------------------------------------------------------------------------------------------ the drawn circuit
PDK = dict(RB_SEG=("res_xhigh_po_0p35", 10, 87.48),   # R_B = 10 x ~500 kOhm = 5 Mohm
           RPAD=("res_xhigh_po_0p35", 1, 87.48),      # pad divider, 500 kOhm each
           CAC=("cap_mim_m3_1", 2, 30.0),             # C_AC = 2 tiles 30 x 30 um = 3.64 pF
           CH=("cap_mim_m3_1", 1, 30.0),              # C_H  = 1 tile = 1.82 pF
           PEN=("pfet_g5v0d10v5", 2.0, 1, 0.5),       # header-gate pull-up (off when en = 0)
           NS1=("nfet_g5v0d10v5", 2.0, 1, 0.5),       # s1 pull-down (disabled state)
           NEI=("nfet_01v8", 0.5, 1, 0.15), PEI=("pfet_01v8", 1.0, 1, 0.15),   # local pll_en inverter (VDDL)
           NB2=("nfet_01v8", 1.0, 1, 0.15), PB2=("pfet_01v8", 4.0, 1, 0.15))   # NOR gate: 2nd input = enb_l


def full(p=D, q=PDK):
    """Receiver with PDK passives, enable and level shifter. Top ports: REF_IN refclk ib pll_en VDDA VDDL VDDD VSS."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cco"))
    import cco
    rm, n, L = q["RB_SEG"]
    c = cco.LS + ".subckt sspll_refbuf_rb a b VSS\n* R_B: %d segments of %s, L = %g um each\n" % (n, rm, L)
    nodes = ["a"] + [f"n{i}" for i in range(1, n)] + ["b"]
    for i in range(n):
        c += f"xr{i} {nodes[i]} {nodes[i+1]} VSS sky130_fd_pr__{rm} l={L} mult=1 m=1\n"
    c += ".ends\n"
    c += ".subckt sspll_refbuf_s1 vin s1 ib en enb VDDA VSS\n"
    c += "* S1: current-reuse inverter, header = MH units mirrored from the bias diode, C_H decouples the header node\n"
    c += _m("pd", "ib", "ib", "VDDA", "VDDA", p["PD"]) + _m("ph", "vh", "ib", "VDDA", "VDDA", p["PH"], m=p["MH"])
    cm, nt, s = q["CH"]
    c += f"xch vh VDDA sky130_fd_pr__{cm} w={s} l={s} m={nt}\n"
    c += _m("p1", "s1", "vin", "vh", "vh", p["P1"]) + _m("n1", "s1", "vin", "VSS", "VSS", p["N1"])
    c += _m("pen", "ib", "en", "VDDA", "VDDA", q["PEN"]) + _m("ns1", "s1", "enb", "VSS", "VSS", q["NS1"])
    c += ".ends\n"
    c += ".subckt sspll_refbuf REF_IN refclk ib pll_en VDDA VDDL VDDD VSS\n"
    rm2, _, L2 = q["RPAD"]
    c += f"xrpu VDDA REF_IN VSS sky130_fd_pr__{rm2} l={L2} mult=1 m=1\nxrpd REF_IN VSS VSS sky130_fd_pr__{rm2} l={L2} mult=1 m=1\n"
    cm, nt, s = q["CAC"]
    c += f"xcac vin REF_IN sky130_fd_pr__{cm} w={s} l={s} m={nt}\n"
    c += "xrb vin s1 VSS sspll_refbuf_rb\nxs1 vin s1 ib en enb VDDA VSS sspll_refbuf_s1\n"
    c += "xls pll_en en enb VDDD VDDA VSS sspll_ls_1v8_3v3\n"
    c += _m("p2", "s2", "s1", "VDDA", "VDDA", p["P2"]) + _m("n2", "s2", "s1", "VSS", "VSS", p["N2"])
    c += _m("pl", "s3", "s2", "VDDL", "VDDL", p["PL"]) + _m("nl", "s3", "s2", "VSS", "VSS", p["NL"])
    c += _m("pei", "enl", "pll_en", "VDDL", "VDDL", q["PEI"]) + _m("nei", "enl", "pll_en", "VSS", "VSS", q["NEI"])
    # output NOR(s3, enl): refclk = not s3 when enabled, 0 when disabled
    c += _m("pb", "xb", "s3", "VDDL", "VDDL", q["PB2"]) + _m("pb2", "refclk", "enl", "xb", "VDDL", q["PB2"])
    c += _m("nb", "refclk", "s3", "VSS", "VSS", p["NB"]) + _m("nb2", "refclk", "enl", "VSS", "VSS", q["NB2"])
    return c + ".ends\n"


def check_pdk(p=D, q=PDK):
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
    import pdk_limits as P
    out = []
    for k, v in list(p.items()) + list(q.items()):
        if isinstance(v, tuple) and len(v) == 4:
            out.append((k, v, P.check(v[0], v[1], v[3], v[2])))
        elif isinstance(v, tuple) and v[0].startswith("res"):
            out.append((k, v, P.check(v[0], 0.35, v[2], 1)))
        elif isinstance(v, tuple) and v[0].startswith("cap"):
            out.append((k, v, P.check(v[0], v[2], v[2], 1)))
    return out
