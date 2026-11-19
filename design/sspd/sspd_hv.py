"""sspd_hv.py - roadmap step 78 redone for the device-rule migration: sub-sampling phase detector with hold, every device
5 V-rated (g5v0d10v5) on VDDA = 3.3 V, sampling the 800 MHz ring (step 74 HV) at 50 MHz.

Per side (p from clkp, m from clkm, the ring's 3.3 V buffered outputs):
  isolation buffer  two 5 V inverters (xb1 small: little load on clkp; xb2 drives the sampling network)
  R_s               series xhigh-poly resistor; with C1 it rounds the square into a near-sine of defined slope
                    (dv/dt at the crossing = (VDDA/2)/tau_s, tau_s = R_total C1,total), so A = VDDA/(2 w0 tau_s)
  sw1 / C1          sampling TG (5 V nMOS + pMOS) onto C1; tracks while cks = 1, samples when cks falls
  swd / CD          dummy sampler on the opposite phase: xb2 always drives one capacitor (no f_ref supply ripple)
  sw2 / C2          hold TG: after the Gm pulse has read C1, ckh shares C1 onto C2 for the NCB
Differences from the 1.6 GHz SSPD (sspd.py, kept for the record):
  * VDDA 3.3 V instead of VDDL 1.8 V and half the carrier: A = VDDA/(2 w0 tau_s) -> the target A = 0.8 V/rad
    (step 72 HV) needs tau_s = 0.41 ns instead of 0.18 ns, so R_s is larger at the same C1;
  * there is no low-V_T 5 V device: the sampling nMOS sits at V_GS = 3.3 - 1.65 V, so it is wider than the lvt
    1.8 V switch, and the pMOS carries half the conductance;
  * the clock pairs come from the 5 V outputs of the step-77 HV clock generator (cks/cksb from refhv).
Every device is (model, W per finger, nf, L)."""
import os, re, sys, subprocess, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "clkgen"))
import clkgen_hv as K
from clkgen_hv import _m, inv5, LIB
import clkgen as C18
N5, P5 = "nfet_g5v0d10v5", "pfet_g5v0d10v5"

D = dict(
    B1=((N5, 0.6, 1, 0.5), (P5, 1.5, 1, 0.5)),         # isolation buffer, first inverter (small load on clkp)
    B2=((N5, 2.0, 1, 0.5), (P5, 5.0, 1, 0.5)),         # second inverter, drives R_s + C
    RS=("res_xhigh_po_0p35", 0.35, 1, 0.6),            # series resistor: A = 0.81 V/rad at tt (step78hv_size.py)
    SWN=(N5, 3.0, 1, 0.5), SWP=(P5, 6.0, 1, 0.5),       # sampling / dummy TG
    HWN=(N5, 1.0, 1, 0.5), HWP=(P5, 2.0, 1, 0.5),       # hold TG
    # C1 resized after step 79: the Gm's measured input capacitance is 26.5 fF at tt (final mirror-less Gm,
    # step79hv_cin.py; 24-29 fF over corners and codes), not the 8 fF placeholder. C1 = 2.69 x 2.69 um (16.2 fF) keeps
    # C1 + C_Gm = 42.7 fF, so the sampled node, A, alpha, kT/C and power stay where they were, and the dummy CD
    # (= C1 + C_Gm) stays 4.4 x 4.4 um. (The step-78 verification ran with 2.73 um + a 26.0 fF load: the same 42.7 fF.)
    C1=("cap_mim_m3_1", 2.69, 1, 2.69), C2=("cap_mim_m3_1", 4.0, 1, 4.0),   # 16.2 / 34.6 fF
    CD=("cap_mim_m3_1", 4.4, 1, 4.4),                  # 41.6 fF: dummy = C1 + the Gm input
)
LOAD = dict(gm=26.5e-15, ncb=4e-15)    # Gm input on v1 (measured in step 79: 26.5 fF at lock, tt) and the NCB input on v2 (placeholder)
VCODRV = ((N5, 1.2, 1, 0.5), (P5, 3.0, 1, 0.5))      # the ring's AC-coupled buffer output stage (step 74 HV)


def cells(p=D):
    c = ".subckt sspll_sspd_hv_tg a b g gb VDDA VSS\n* 5 V transmission gate: on while g = 1 (gb = 0)\n"
    c += _m("xn", "a", "g", "b", "VSS", p["SWN"]) + _m("xp", "a", "gb", "b", "VDDA", p["SWP"]) + ".ends\n"
    c += ".subckt sspll_sspd_hv_tgh a b g gb VDDA VSS\n* hold transmission gate (smaller)\n"
    c += _m("xn", "a", "g", "b", "VSS", p["HWN"]) + _m("xp", "a", "gb", "b", "VDDA", p["HWP"]) + ".ends\n"
    rm, rw, _, rl = p["RS"]
    c += ".subckt sspll_sspd_hv_side clk v1 v2 cks cksb ckh ckhb VDDA VSS\n"
    c += "* isolation buffer -> R_s -> sampler sw1/C1 + dummy swd/CD (opposite phase); hold sw2/C2\n"
    c += inv5("xb1", "clk", "b1", p["B1"]) + inv5("xb2", "b1", "b2", p["B2"])
    c += f"xrs b2 f VSS sky130_fd_pr__{rm} l={rl} mult=1 m=1\n"
    c += "xs1 f v1 cks cksb VDDA VSS sspll_sspd_hv_tg\nxsd f vd cksb cks VDDA VSS sspll_sspd_hv_tg\n"
    c += "xs2 v1 v2 ckh ckhb VDDA VSS sspll_sspd_hv_tgh\n"
    for nm, node in (("C1", "v1"), ("CD", "vd"), ("C2", "v2")):
        cm, w, _, l = p[nm]
        c += f"x{nm.lower()} {node} VSS sky130_fd_pr__{cm} w={w} l={l} m=1\n"
    c += ".ends\n"
    c += ".subckt sspll_sspd_hv clkp clkm v1p v1m v2p v2m cks cksb ckh ckhb VDDA VSS\n"
    c += "xsp clkp v1p v2p cks cksb ckh ckhb VDDA VSS sspll_sspd_hv_side\n"
    c += "xsm clkm v1m v2m cks cksb ckh ckhb VDDA VSS sspll_sspd_hv_side\n.ends\n"
    return c


def run(net, files=()):
    with tempfile.TemporaryDirectory() as d:
        C18.spinit(d)
        open(os.path.join(d, "r.sp"), "w").write(net)
        out = subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d, timeout=20000).stdout
        data = {f: np.loadtxt(os.path.join(d, f)) for f in files if os.path.exists(os.path.join(d, f))}
    return out, data


def bench(p=D, corner="tt", temp=27, vdda=3.3, vddd=1.8, fref=50e6, nb=48, nper=None, td=0.0, refon=True, extra="",
          save="", tstep=2e-12, n=16):
    """SSPD + the step-77 HV clock generator. The 'VCO' is two ideal squares at f = (n + 1/nb) f_ref behind a 5 V
    inverter like the ring's buffer output stage, so the sampling phase slides by 2 pi / nb per reference period (beat).
    The reference edges are ideal: refhv (0..VDDA, the receiver's S2 output) and refclk (0..VDDD, 0.2 ns later, as
    the receiver's level shifter and NOR make it)."""
    fv = (n + 1/nb)*fref; Tv = 1/fv; T = 1/fref; nper = nper or nb + 2
    tr = 60e-12
    src = (f"vvp vp 0 pulse(0 {vdda} {td} {tr} {tr} {Tv/2 - tr} {Tv})\n"
           f"vvm vm 0 pulse({vdda} 0 {td} {tr} {tr} {Tv/2 - tr} {Tv})\n")
    drv = re.sub(r"\bVSS\b", "0", inv5("xdp", "vp", "clkp", VCODRV, "VDRV") + inv5("xdm", "vm", "clkm", VCODRV, "VDRV"))
    ref = (f"vrh refhv 0 pulse(0 {vdda} {T/4} 300p 300p {T/2 - 300e-12} {T})\n"
           f"vrc refclk 0 pulse(0 {vddd} {T/4 + 0.2e-9} 300p 300p {T/2 - 300e-12} {T})\n") if refon else "vrh refhv 0 0\nvrc refclk 0 0\n"
    net = (f"* sspd hv bench\n.lib {LIB} {corner}\n.temp {temp}\n{K.cells()}{cells(p)}"
           f"vdda VDDA 0 {vdda}\nvdrv VDRV 0 {vdda}\nvck VCK 0 {vdda}\nvckd VCKD 0 {vddd}\n{src}{drv}{ref}"
           f"cclp clkp 0 10f\ncclm clkm 0 10f\n"
           "xcg refclk refhv cks cksb ckg ckgb ckh ckhb VCKD VCK 0 sspll_clkgen_hv\n"
           "xpd clkp clkm v1p v1m v2p v2m cks cksb ckh ckhb VDDA 0 sspll_sspd_hv\n"
           f"cg1 v1p 0 {LOAD['gm']}\ncg2 v1m 0 {LOAD['gm']}\ncn1 v2p 0 {LOAD['ncb']}\ncn2 v2m 0 {LOAD['ncb']}\n"
           f"cckg ckg 0 40f\ncckgb ckgb 0 40f\n{extra}"
           f".control\noption interp\nsave v(cks) v(ckg) v(ckh) v(v1p) v(v1m) v(v2p) v(v2m) vdda#branch v(clkp) {save}\n"
           f"tran {tstep} {nper*T}\n"
           f"wrdata w.txt v(cks) v(ckg) v(ckh) v(v1p) v(v1m) v(v2p) v(v2m) i(vdda) v(clkp) {save}\n.endc\n.end\n")
    return net, fv


def characteristic(p=D, corner="tt", temp=27, vdda=3.3, vddd=1.8, fref=50e6, nb=32, keep=False):
    """Beat run -> sampled characteristic v1d(phi), v2d, A (per side, V/rad), alpha, SSPD power, sampled CM."""
    net, fv = bench(p, corner, temp, vdda, vddd, fref, nb)
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; t = z[:, 0]; g = lambda i: z[:, 2*i + 1]
    cks, ckg, ckh, v1p, v1m, v2p, v2m, ida, clkp = (g(i) for i in range(9))
    T = 1/fref; m = vdda/2
    ts = K.xings(t, cks, m, False)
    tg = K.xings(t, ckg, m, True); tgf = K.xings(t, ckg, m, False); th = K.xings(t, ckh, m, False)
    rows = []
    for s in ts:
        a = tg[tg > s]; b = tgf[tgf > s]; h = th[th > s]
        if len(a) == 0 or len(b) == 0 or len(h) == 0 or s < 2*T:
            continue
        tm = (a[0] + b[0])/2; th2 = h[0] + 0.5e-9
        v1 = np.interp(tm, t, v1p) - np.interp(tm, t, v1m)
        v2 = np.interp(th2, t, v2p) - np.interp(th2, t, v2m)
        cm = (np.interp(tm, t, v1p) + np.interp(tm, t, v1m))/2
        rows.append((s, (2*np.pi*fv*s) % (2*np.pi), v1, v2, cm))
    r = np.array(rows)
    ph, v1 = r[:, 1], r[:, 2]
    o = np.argsort(ph); ph_s, v1_s = ph[o], v1[o]
    idx = [i for i in range(len(ph_s)) if v1_s[i - 1] < 0 <= v1_s[i]]
    i0 = idx[0]
    dp = (ph_s[i0] - ph_s[i0 - 1]) % (2*np.pi)
    phi0 = (ph_s[i0 - 1] + (0 - v1_s[i0 - 1])*dp/(v1_s[i0] - v1_s[i0 - 1])) % (2*np.pi)
    dphi = (ph_s - phi0 + np.pi) % (2*np.pi) - np.pi
    msk = np.abs(dphi) < 0.35
    slope = np.polyfit(dphi[msk], v1_s[msk], 1)[0]
    v2 = r[:, 3]; X = np.vstack([r[1:, 2], v2[:-1]]).T
    c_, *_ = np.linalg.lstsq(X, v2[1:], rcond=None)
    w = t > 2*T
    P = -vdda*np.trapezoid(ida[w], t[w])/(t[w][-1] - t[w][0])
    res = dict(corner=corner, temp=temp, vdda=vdda, vddd=vddd, fref=fref, fvco=fv, A=float(slope/2), phi0=float(phi0),
               alpha=float(c_[1]), gain_v2=float(c_[0] + c_[1]), vmax=float(v1.max()), vmin=float(v1.min()),
               cm=float(np.mean(r[:, 4])), power=float(P), dvdt=float(slope/2*2*np.pi*fv))
    if keep:
        res["rows"] = r.tolist()
    return res


def lvs_reference(p=D):
    return cells(p)


def kick(p=D, phi0=0.0, corner="tt", temp=27, vdda=3.3, fref=50e6, nper=7, t_s=0.425e-9):
    """Kick-back at lock (f = 16 f_ref, sampling at the zero crossing; method M19). Compares clkp with the clock
    generator switching against the reference held still (sampler tracking): edge-time displacement of clkp -> spur
    estimate at f_ref; also the SSPD supply current at f_ref with and without the dummy sampler."""
    T = 1/fref; fv = 16*fref; Tv = 1/fv
    s_est = T/4 + t_s                                           # refhv edge + cks delay (step 77 HV, incl. receiver)
    td = (s_est - phi0/(2*np.pi*fv)) % Tv
    out = {}
    for tag, pp, refon in (("normal", p, True), ("static", p, False),
                           ("nodummy", dict(p, CD=("cap_mim_m3_1", 2.0, 1, 2.0)), True)):
        net, _ = bench(pp, corner, temp, vdda, 1.8, fref, nb=1e15, nper=nper, td=td, refon=refon, tstep=1e-12, n=16)
        _, d = run(net, ["w.txt"])
        z = d["w.txt"]; t = z[:, 0]; g = lambda i: z[:, 2*i + 1]
        out[tag] = dict(t=t, clkp=g(8), ida=g(7), v1=g(3) - g(4), cks=g(0))
    a, b = out["normal"], out["static"]
    w0 = 3*T
    ea = np.sort(np.concatenate([K.xings(a["t"], a["clkp"], vdda/2, r) for r in (True, False)]))
    eb = np.sort(np.concatenate([K.xings(b["t"], b["clkp"], vdda/2, r) for r in (True, False)]))
    ea, eb = ea[ea > w0], eb[eb > w0]; n = min(len(ea), len(eb)) - 1
    ea, eb = ea[:n], eb[:n]
    dt = ea - eb
    k = (ea - w0) < (nper - 4)*T
    ph = 2*np.pi*fv*dt[k]; tt = ea[k]
    a1 = 2*abs(np.mean(ph*np.exp(-2j*np.pi*fref*tt)))
    def harm(o):
        mm = (o["t"] > w0) & (o["t"] < w0 + (nper - 4)*T); ti, ii = o["t"][mm], o["ida"][mm]
        return float(2*abs(np.trapezoid(ii*np.exp(-2j*np.pi*fref*ti), ti)/(ti[-1] - ti[0])))
    return dict(dt_max=float(np.max(np.abs(dt[k]))), dt_rms=float(np.std(dt[k])), spur_dbc=float(20*np.log10(a1/2 + 1e-30)),
                I_fref=harm(out["normal"]), I_fref_nodummy=harm(out["nodummy"]),
                wave=dict(dt_edges=((ea[k] - w0)*1e9).tolist(), dt=(dt[k]*1e15).tolist()))


def buf_chain(p=D, vdda=3.3, extra="", fin=0.8e9, tstop=60e-9, nt=None, cload=None):
    """Flat isolation-buffer path: ring buffer stage -> XB1 -> XB2 -> R_s -> C (the sampling capacitor while it
    tracks). Returns a netlist (crossing of node f is the edge the sampler sees)."""
    T = 1/fin; tr = 60e-12
    rm, _, _, rl = p["RS"]
    cl = cload if cload is not None else 46e-15
    return (f"* buffer path\n.lib {LIB} tt\n.temp 27\nvdda VDDA 0 {vdda}\nvdrv VDRV 0 3.3\n"
            f"vin vp 0 pulse(0 3.3 0 {tr} {tr} {T/2 - tr} {T})\n" +
            re.sub(r"\bVSS\b", "0", inv5("xd", "vp", "clkp", VCODRV, "VDRV") + inv5("xb1", "clkp", "b1", p["B1"]) +
                   inv5("xb2", "b1", "b2", p["B2"])) +
            f"xrs b2 f 0 sky130_fd_pr__{rm} l={rl} mult=1 m=1\ncf f 0 {cl}\ncclp clkp 0 10f\n{extra}")


def buf_jitter(p=D, S=None, seed=1, scale=1.0, nt=1e-12, tstop=200e-9):
    """Method M17 on the isolation buffer: trnoise currents of XB1's and XB2's trip-point noise at b1 and b2;
    rms jitter of the filtered crossing at f (both edges, detrended). clkp itself is common with the ring output."""
    import step77hv_sim as S77
    m = _m
    inv = lambda size: m("n", "y", "a", "0", "0", size[0]) + m("p", "y", "a", "VDD", "VDD", size[1])
    S = S or {k: S77.stage_S(inv(p[k]), 3.3)[0] for k in ("B1", "B2")}
    src = "".join(f"in{n} 0 {n} dc 0 trnoise({scale*np.sqrt(S[k]/(2*nt)):.4g} {nt} 0 0)\n" for n, k in (("b1", "B1"), ("b2", "B2")))
    net = buf_chain(p, extra=src) + (f".options seed={seed}\n.control\nsave v(f)\ntran {nt} {tstop} 4n {nt}\n"
                                    "wrdata w.txt v(f)\n.endc\n.end\n")
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; t, v = z[:, 0], z[:, 1]; T = 1/0.8e9
    lev = 0.5*(v[t > 5e-9].max() + v[t > 5e-9].min())
    sig = []
    for r in (True, False):
        e = K.xings(t, v, lev, r); e = e[e > 5e-9]
        k = np.round((e - e[0])/T); x = e - e[0] - k*T
        x = x - np.polyval(np.polyfit(k, x, 4), k)
        sig.append(x.std())
    return dict(sigma=float(np.mean(sig)), S={k: float(v) for k, v in S.items()}, n=int(len(e)))


def buf_supply(p=D, dv=10e-3):
    """Static VDDA sensitivity of the isolation-buffer delay (clkp crossing -> f crossing at mid-level), ps/V. The
    buffer has no slow nodes, so the static value holds up to f_ref/2 (as M21 showed for the VDDD gates of step 76)."""
    def dly(v):
        net = buf_chain(p, vdda=v) + ".control\ntran 1p 20n\nwrdata w.txt v(clkp) v(f)\n.endc\n.end\n"
        _, d = run(net, ["w.txt"]); z = d["w.txt"]; t = z[:, 0]
        a = K.xings(t, z[:, 1], 1.65, True); b = K.xings(t, z[:, 3], v/2, True)   # two inversions: f follows clkp
        a, b = a[a > 8e-9], b[b > 8e-9]
        return np.mean([b[b > x][0] - x for x in a[:-1]])
    return dict(k=(dly(3.3 + dv) - dly(3.3))/dv, d0=dly(3.3))
