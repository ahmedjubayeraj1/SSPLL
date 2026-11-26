"""sspd.py - roadmap step 78: sub-sampling phase detector with hold (SKY130, VDDL = 1.8 V).

Per side (p from clkp, m from clkm, the VCO's buffered outputs of step 74):
  isolation buffer  two inverters (xb1 small: tiny load on clkp; xb2 drives the sampling network)
  R_s               series poly resistor; with C1 it rounds the square wave into a near-sine of defined slope
                    (dv/dt at the crossing = (VDD/2)/tau_s, tau_s = R_total C1,total), so A = VDD/(2 w0 tau_s)
  sw1 / C1          sampling switch (TG: nfet_01v8_lvt + pfet_01v8) onto C1; tracks while cks = 1, samples when cks falls
  swd / CD          dummy sampler on the same node, driven by the opposite phase: the buffer always drives one capacitor,
                    so its delay and supply current do not change at f_ref (no reference spur from the SSPD current)
  sw2 / C2          hold switch: after the Gm pulse has read C1, ckh shares C1 onto C2, which holds for the NCB
The Gm (step 79) reads v1p - v1m during ckg (right after the sample, before the sharing): no charge-sharing pole in
the loop. The NCB (via the diff-to-SE amplifier) reads v2: first-order hold alpha = C2/(C1 + C2) as in the FFNC model.
Every device is (model, W per finger, nf, L) like design/clkgen/clkgen.py."""
import os, sys, json, subprocess, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "clkgen"))
import clkgen as K
from clkgen import _m, inv, LIB, spinit

N18, P18, NLVT = "nfet_01v8", "pfet_01v8", "nfet_01v8_lvt"
D = dict(
    B1=((N18, 0.42, 1, 0.15), (P18, 0.84, 1, 0.15)),     # isolation buffer, first inverter (small load on clkp)
    B2=((N18, 2.0, 1, 0.15), (P18, 4.0, 1, 0.15)),       # second inverter, drives R_s + C
    RS=("res_xhigh_po_0p69", 0.69, 1, 0.6),             # series resistor 2.16 kOhm (sets most of tau_s)
    SWN=(NLVT, 3.0, 1, 0.15), SWP=(P18, 1.5, 1, 0.15),   # sampling / dummy TG (lvt nMOS: the signal sits mid-rail)
    HWN=(NLVT, 1.0, 1, 0.15), HWP=(P18, 1.0, 1, 0.15),   # hold TG
    C1=("cap_mim_m3_1", 4.0, 1, 4.0), C2=("cap_mim_m3_1", 4.0, 1, 4.0),   # 34.7 fF each
    CD=("cap_mim_m3_1", 4.35, 1, 4.35),                 # dummy 40.7 fF = C1 + the Gm input (6 fF)
)
LOAD = dict(gm=6e-15, ncb=4e-15)        # placeholders for the Gm input (on v1) and the diff-to-SE input (on v2)


def tg(name, a, b, g, gb, n, p):
    return _m(name + "n", a, g, b, "VSS", n) + _m(name + "p", a, gb, b, "VDD", p)


def cells(p=D):
    c = ".subckt sspll_sspd_tg a b g gb VDD VSS\n* transmission gate: on while g = 1 (gb = 0)\n"
    c += _m("xn", "a", "g", "b", "VSS", p["SWN"]) + _m("xp", "a", "gb", "b", "VDD", p["SWP"]) + ".ends\n"
    c += ".subckt sspll_sspd_tgh a b g gb VDD VSS\n* hold transmission gate (smaller)\n"
    c += _m("xn", "a", "g", "b", "VSS", p["HWN"]) + _m("xp", "a", "gb", "b", "VDD", p["HWP"]) + ".ends\n"
    rm, rw, _, rl = p["RS"]
    c += ".subckt sspll_sspd_side clk v1 v2 cks cksb ckh ckhb VDD VSS\n"
    c += "* isolation buffer -> R_s -> sampler sw1/C1 + dummy sampler swd/CD (opposite phase) ; hold sw2/C2\n"
    c += inv("xb1", "clk", "b1", p["B1"]) + inv("xb2", "b1", "b2", p["B2"])
    c += f"xrs b2 f VSS sky130_fd_pr__{rm} l={rl} mult=1 m=1\n"
    c += "xs1 f v1 cks cksb VDD VSS sspll_sspd_tg\nxsd f vd cksb cks VDD VSS sspll_sspd_tg\n"
    c += "xs2 v1 v2 ckh ckhb VDD VSS sspll_sspd_tgh\n"
    for nm, node in (("C1", "v1"), ("CD", "vd"), ("C2", "v2")):
        cm, w, _, l = p[nm]
        c += f"x{nm.lower()} {node} VSS sky130_fd_pr__{cm} w={w} l={l} m=1\n"     # top plate on the signal, bottom on VSS
    c += ".ends\n"
    c += ".subckt sspll_sspd clkp clkm v1p v1m v2p v2m cks cksb ckh ckhb VDD VSS\n"
    c += "xsp clkp v1p v2p cks cksb ckh ckhb VDD VSS sspll_sspd_side\n"
    c += "xsm clkm v1m v2m cks cksb ckh ckhb VDD VSS sspll_sspd_side\n.ends\n"
    return c


def run(net, files=()):
    with tempfile.TemporaryDirectory() as d:
        spinit(d)
        open(os.path.join(d, "r.sp"), "w").write(net)
        out = subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d, timeout=20000).stdout
        data = {f: np.loadtxt(os.path.join(d, f)) for f in files if os.path.exists(os.path.join(d, f))}
    return out, data


def bench(p=D, corner="tt", temp=27, vdd=1.8, fref=50e6, nb=48, nper=None, td=0.0, refon=True, extra="", save="",
          tstep=2e-12):
    """SSPD + the real clock generator. The 'VCO' is two ideal squares at f = (32 + 1/nb) f_ref behind a driver inverter
    like the acbuf output stage (2 / 4 um), so the sampling phase slides by 2 pi / nb every reference period (beat)."""
    fv = (32 + 1/nb)*fref; Tv = 1/fv; T = 1/fref; nper = nper or nb + 2
    tr = 40e-12
    src = (f"vvp vp 0 pulse(0 {vdd} {td} {tr} {tr} {Tv/2 - tr} {Tv})\n"
           f"vvm vm 0 pulse({vdd} 0 {td} {tr} {tr} {Tv/2 - tr} {Tv})\n")
    drv = (inv("xdp", "vp", "clkpb", ((N18, 2.0, 1, 0.15), (P18, 4.0, 1, 0.15))).replace("VDD", "VDRV").replace("VSS", "0") +
           inv("xdm", "vm", "clkmb", ((N18, 2.0, 1, 0.15), (P18, 4.0, 1, 0.15))).replace("VDD", "VDRV").replace("VSS", "0"))
    drv = drv.replace(" clkpb ", " clkp ").replace(" clkmb ", " clkm ")
    # clkp is the inverted vp: fine, only the phase reference changes (known from the source)
    net = (f"* sspd bench\n.lib {LIB} {corner}\n.temp {temp}\n{K.cells()}{cells(p)}"
           f"vdd VDD 0 {vdd}\nvdrv VDRV 0 {vdd}\nvck VCK 0 {vdd}\n{src}{drv}"
           f"cclp clkp 0 10f\ncclm clkm 0 10f\n" +
           (f"vin refclk 0 pulse(0 {vdd} {T/4} 375p 375p {T/2 - 375e-12} {T})\n" if refon else "vin refclk 0 0\n") +
           "xcg refclk cks cksb ckh ckhb ckg ckgb VCK 0 sspll_clkgen\n" +
           "xpd clkp clkm v1p v1m v2p v2m cks cksb ckh ckhb VDD 0 sspll_sspd\n"
           f"cg1 v1p 0 {LOAD['gm']}\ncg2 v1m 0 {LOAD['gm']}\ncn1 v2p 0 {LOAD['ncb']}\ncn2 v2m 0 {LOAD['ncb']}\n"
           f"cckg ckg 0 20f\ncckgb ckgb 0 20f\n{extra}"
           f".control\noption interp\ntran {tstep} {nper*T}\n"
           f"wrdata w.txt v(cks) v(ckg) v(ckh) v(v1p) v(v1m) v(v2p) v(v2m) i(vdd) v(clkp) {save}\n.endc\n.end\n")
    return net, fv


def characteristic(p=D, corner="tt", temp=27, vdd=1.8, fref=50e6, nb=48, keep=False):
    """Beat run -> sampled characteristic v1d(phi), v2d, A, alpha, power, sampling-node CM."""
    net, fv = bench(p, corner, temp, vdd, fref, nb)
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; t = z[:, 0]; g = lambda i: z[:, 2*i + 1]
    cks, ckg, ckh, v1p, v1m, v2p, v2m, idd, clkp = (g(i) for i in range(9))
    T = 1/fref
    ts = K.xings(t, cks, vdd/2, False)                       # sampling instants
    tg = K.xings(t, ckg, vdd/2, True); tgf = K.xings(t, ckg, vdd/2, False)
    th = K.xings(t, ckh, vdd/2, False)
    rows = []
    for k, s in enumerate(ts):
        a = tg[tg > s]; b = tgf[tgf > s]; h = th[th > s]
        if len(a) == 0 or len(b) == 0 or len(h) == 0 or s < 2*T:
            continue
        tm = (a[0] + b[0])/2                                 # middle of the Gm pulse: what the Gm sees
        th2 = h[0] + 0.5e-9                                  # after the hold transfer
        v1 = np.interp(tm, t, v1p) - np.interp(tm, t, v1m)
        v2 = np.interp(th2, t, v2p) - np.interp(th2, t, v2m)
        cm = (np.interp(tm, t, v1p) + np.interp(tm, t, v1m))/2
        # VCO phase at the sampling instant; the ideal vp rises at n*Tv, clkp = inverted vp + driver delay
        phi = (2*np.pi*fv*s) % (2*np.pi)
        rows.append((s, phi, v1, v2, cm))
    r = np.array(rows)
    # zero crossing with positive slope of v1(phi): local fit over +-0.35 rad
    ph, v1 = r[:, 1], r[:, 2]
    o = np.argsort(ph); ph_s, v1_s = ph[o], v1[o]
    idx = [i for i in range(len(ph_s)) if v1_s[i - 1] < 0 <= v1_s[i]]
    i0 = idx[0]
    dp = (ph_s[i0] - ph_s[i0 - 1]) % (2*np.pi)                # the crossing may straddle 2 pi
    phi0 = (ph_s[i0 - 1] + (0 - v1_s[i0 - 1])*dp/(v1_s[i0] - v1_s[i0 - 1])) % (2*np.pi)
    dphi = (ph_s - phi0 + np.pi) % (2*np.pi) - np.pi
    m = np.abs(dphi) < 0.35
    slope = np.polyfit(dphi[m], v1_s[m], 1)[0]              # V per rad, differential
    # hold: v2[k] = (1 - alpha) v1[k] + alpha v2[k-1]
    v2 = r[:, 3]; X = np.vstack([r[1:, 2], v2[:-1]]).T
    c_, *_ = np.linalg.lstsq(X, v2[1:], rcond=None)
    w = t > 2*T
    P = -vdd*np.trapezoid(idd[w], t[w])/(t[w][-1] - t[w][0])
    res = dict(corner=corner, temp=temp, vdd=vdd, fref=fref, fvco=fv, A=float(slope/2), phi0=float(phi0),
               alpha=float(c_[1]), gain_v2=float(c_[0] + c_[1]), vmax=float(v1.max()), vmin=float(v1.min()),
               cm=float(np.mean(r[:, 4])), power=float(P),
               dvdt=float(slope/2*2*np.pi*fv))
    if keep:
        res["rows"] = r.tolist()
    return res


COND = [("tt", 27, 1.8, 50e6), ("tt", 27, 1.71, 50e6), ("tt", 27, 1.89, 50e6), ("tt", -40, 1.8, 50e6),
        ("tt", 110, 1.8, 50e6), ("ss_hh", 110, 1.71, 50e6), ("ss_hh", -40, 1.71, 50e6), ("ff_ll", -40, 1.89, 50e6),
        ("ff_ll", 110, 1.89, 50e6), ("ss", 110, 1.71, 50e6), ("ff", -40, 1.89, 50e6), ("sf", 27, 1.8, 50e6),
        ("fs", 27, 1.8, 50e6), ("hl", 27, 1.8, 50e6), ("lh", 27, 1.8, 50e6), ("tt", 27, 1.8, 45e6), ("tt", 27, 1.8, 55e6)]


def _char(a):
    corner, temp, vdd, fref = a
    return characteristic(corner=corner, temp=temp, vdd=vdd, fref=fref, nb=32, keep=(a == COND[0]))


def kick(p=D, phi0=None, corner="tt", temp=27, vdd=1.8, fref=50e6, nper=7):
    """Kick-back and supply ripple at lock (f = 32 f_ref, sampling at the zero crossing).
    Compares clkp with the clock generator running against refclk = 0 (sampler tracking, no switching): edge-time
    displacement of clkp (both edges) -> spur estimate at f_ref; also the SSPD supply current harmonic at f_ref with
    and without the dummy sampler."""
    T = 1/fref; fv = 32*fref; Tv = 1/fv
    s_est = T/4 + 0.1875e-9 + 0.228e-9                       # refclk crossing + t_s (step 77, tt)
    phi0 = 0.0 if phi0 is None else phi0
    td = (s_est - phi0/(2*np.pi*fv)) % Tv
    out = {}
    for tag, pp, refon in (("normal", p, True), ("static", p, False),
                           ("nodummy", dict(p, CD=("cap_mim_m3_1", 2.0, 1, 2.0)), True)):
        net, _ = bench(pp, corner, temp, vdd, fref, nb=1e15, nper=nper, td=td, refon=refon, tstep=1e-12)
        _, d = run(net, ["w.txt"])
        z = d["w.txt"]; t = z[:, 0]; g = lambda i: z[:, 2*i + 1]
        out[tag] = dict(t=t, clkp=g(8), idd=g(7), v1=g(3) - g(4), cks=g(0))
    a, b = out["normal"], out["static"]
    w0 = 3*T
    ea = np.sort(np.concatenate([K.xings(a["t"], a["clkp"], vdd/2, r) for r in (True, False)]))
    eb = np.sort(np.concatenate([K.xings(b["t"], b["clkp"], vdd/2, r) for r in (True, False)]))
    ea, eb = ea[ea > w0], eb[eb > w0]; n = min(len(ea), len(eb)) - 1
    ea, eb = ea[:n], eb[:n]
    dt = ea - eb
    k = (ea - w0) < (nper - 4)*T                                # whole reference periods
    ph = 2*np.pi*fv*dt[k]; tt = ea[k]
    a1 = 2*abs(np.mean(ph*np.exp(-2j*np.pi*fref*tt)))          # fundamental of the phase deviation at f_ref
    dv = np.interp(a["t"], b["t"], b["clkp"]); m = a["t"] > w0
    # supply current at f_ref
    def harm(o):
        mm = (o["t"] > w0) & (o["t"] < w0 + (nper - 4)*T); ti, ii = o["t"][mm], o["idd"][mm]
        return float(2*abs(np.trapezoid(ii*np.exp(-2j*np.pi*fref*ti), ti)/(ti[-1] - ti[0])))
    ts = K.xings(a["t"], a["cks"], vdd/2, False); ts = ts[ts > w0]
    v1s = float(np.interp(ts[0] + 0.15e-9, a["t"], a["v1"]))
    return dict(dt_max=float(np.max(np.abs(dt[k]))), dt_rms=float(np.std(dt[k])), spur_dbc=float(20*np.log10(a1/2 + 1e-30)),
                dv_max=float(np.max(np.abs(a["clkp"][m] - dv[m]))), I_fref=harm(out["normal"]),
                I_fref_nodummy=harm(out["nodummy"]), v1_at_lock=v1s,
                wave=dict(t=((a["t"][m] - w0)*1e9)[::4].tolist(), dt_edges=((ea[k] - w0)*1e9).tolist(), dt=(dt[k]*1e15).tolist()))


def buf_jitter(p=D, seed=1, fin=1.6e9, nt=1e-12, tstop=200e-9, S=None, scale=1.0, cload=45e-15):
    """Method M17 on the isolation buffer: flat copy of driver -> XB1 -> XB2 -> R_s -> C with trnoise currents at b1
    and b2 (the trip-point noise of XB1 and XB2; clkp itself is common to the output path, so VCO-like). Returns the
    rms jitter of the filtered crossing at node f (rising and falling edges)."""
    S = S or {k: K.inv_noise(p[k])[0] for k in ("B1", "B2")}
    vdd = 1.8; T = 1/fin; tr = 40e-12
    rm, _, _, rl = p["RS"]
    net = (f"* buffer jitter\n.lib {LIB} tt\n.temp 27\nvdd VDD 0 {vdd}\n"
           f"vin vp 0 pulse(0 {vdd} 0 {tr} {tr} {T/2 - tr} {T})\n" +
           (inv("xd", "vp", "clkp", ((N18, 2.0, 1, 0.15), (P18, 4.0, 1, 0.15))) + inv("xb1", "clkp", "b1", p["B1"]) +
            inv("xb2", "b1", "b2", p["B2"])).replace(" VSS ", " 0 ") +
           f"xrs b2 f 0 sky130_fd_pr__{rm} l={rl} mult=1 m=1\ncf f 0 {cload}\ncclp clkp 0 10f\n" +
           "".join(f"in{n} 0 {n} dc 0 trnoise({scale*np.sqrt(S[k]/(2*nt)):.4g} {nt} 0 0)\n" for n, k in (("b1", "B1"), ("b2", "B2"))) +
           f".options seed={seed}\n.control\ntran {nt} {tstop} 4n {nt}\nwrdata w.txt v(f)\n.endc\n.end\n")
    _, d = run(net, ["w.txt"])
    z = d["w.txt"]; t, v = z[:, 0], z[:, 1]
    lev = 0.5*(v[t > 5e-9].max() + v[t > 5e-9].min())
    sig = []
    for r in (True, False):
        e = K.xings(t, v, lev, r); e = e[e > 5e-9]
        k = np.round((e - e[0])/T); x = e - e[0] - k*T
        x = x - np.polyval(np.polyfit(k, x, 4), k)
        sig.append(x.std())
    return dict(sigma=float(np.mean(sig)), S={k: float(v) for k, v in S.items()}, n=int(len(e)))


if __name__ == "__main__":
    import time
    t0 = time.time()
    r = characteristic(keep=False)
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, f"{time.time() - t0:.0f} s")
