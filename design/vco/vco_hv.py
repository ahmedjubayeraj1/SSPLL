"""vco_hv.py - roadmap step 74 redone for the device-rule migration: parametric 3-stage pseudo-differential ring VCO
in 5 V devices (nfet/pfet_g5v0d10v5, L >= 0.5 um) for 800 MHz, current-fed by the CCO from VDDA = 3.3 V.

Same cell topology as the 1.6 GHz design (vco.py, kept for the record), one half shown; the other half is mirrored:
  main inverter  P (pfet) / N (nfet)  inp -> outm, inm -> outp
  fine tuning    switch S (nfet, gate = vtune) from out to a MOS cap C (nfet gate cap)  -> K_VCO < 0
  coupling       always-on transmission gate TN/TP: inp -> outp, inm -> outm (ties the two halves, sets the phase)
Three stages: each half is an odd inverter loop through the crossed last stage, so the ring cannot latch.
Output buffers: AC-coupled, self-biased 5 V inverter pairs on VDDA (MIM + poly feedback resistor), one on every ring
node so the six nodes are loaded alike (two are used, four are dummies whose output is left open).

Functions: netlist(), run(), freq_sweep(), find_current(), noise_table(), isf_noise(), buffer_current(), lvs_reference().
Every device is (model, W per finger, nf, L): the netlist is the layout (integer fingers, unit widths).
"""
import os, re, subprocess, tempfile, numpy as np
from multiprocessing import Pool
import vco as v18                     # helpers of the 1.8 V design: device line (_m), PDK .spiceinit, result parser

PDK_ROOT = v18.PDK_ROOT; LIB = v18.LIB; HERE = v18.HERE
N5, P5 = "nfet_g5v0d10v5", "pfet_g5v0d10v5"
NST = 3
P_ = ["vop"] + [f"p{k}" for k in range(1, NST)]
M_ = ["vom"] + [f"m{k}" for k in range(1, NST)]

# starting point = feasibility ring B (design/feas/hv_vco.py), tuning switch and cap added
START = dict(P=(P5, 5.0, 2, 0.5), N=(N5, 4.0, 1, 0.5), S=(N5, 4.0, 1, 0.5), C=(N5, 5.0, 1, 1.0),
             TN=(N5, 1.5, 1, 0.5), TP=(P5, 3.0, 1, 0.5))


def scaled(p, s, keys=("P", "N", "TN", "TP", "S", "C")):
    """Widen the listed devices by s in whole fingers of the same unit width (layout-friendly scaling)."""
    q = dict(p)
    for k in keys:
        if not isinstance(p.get(k), tuple):
            continue
        m, w, nf, l = p[k]
        tot = w*nf*s
        nf2 = max(1, int(round(tot/w)))
        q[k] = (m, w, nf2, l)
    return q


def cell(p):
    """tune = "switch" (1.8 V design: nMOS switch S, gate = vtune, to a MOS cap C; K_VCO < 0) or
    "var" (nMOS varactor: gate = output node, source/drain = vtune, body = VSS; no switch) or
    "pvar" (pMOS varactor in its own n-well: gate = output node, source/drain/well = vtune; inverts while the node is
    below vtune - |V_tp|, so a higher vtune adds capacitance: K_VCO < 0).
    TN = None leaves out the TG nMOS (pMOS-only coupling)."""
    _m = v18._m
    c = ".subckt dcell inp inm outp outm vtune vdd vss\n"
    c += _m("p1", "outm", "inp", "vdd", "vdd", p["P"]) + _m("n1", "outm", "inp", "vss", "vss", p["N"])
    c += _m("p2", "outp", "inm", "vdd", "vdd", p["P"]) + _m("n2", "outp", "inm", "vss", "vss", p["N"])
    if p.get("tune", "switch") == "switch":
        c += _m("s1", "outm", "vtune", "c1n", "vss", p["S"]) + _m("c1", "vss", "c1n", "vss", "vss", p["C"])
        c += _m("s2", "outp", "vtune", "c2n", "vss", p["S"]) + _m("c2", "vss", "c2n", "vss", "vss", p["C"])
    elif p["tune"] == "var":
        c += _m("c1", "vtune", "outm", "vtune", "vss", p["C"]) + _m("c2", "vtune", "outp", "vtune", "vss", p["C"])
    else:                                   # "pvar": pMOS varactor, gate = node, source/drain/n-well = vtune
        c += _m("c1", "vtune", "outm", "vtune", "vtune", p["C"]) + _m("c2", "vtune", "outp", "vtune", "vtune", p["C"])
    if p.get("TN"):
        c += _m("t1n", "inp", "vdd", "outp", "vss", p["TN"]) + _m("t2n", "inm", "vdd", "outm", "vss", p["TN"])
    c += _m("t1p", "inp", "vss", "outp", "vdd", p["TP"]) + _m("t2p", "inm", "vss", "outm", "vdd", p["TP"])
    c += "cpp outp vss {cpar}\ncpm outm vss {cpar}\n.ends\n"
    return c


# AC-coupled buffer in 5 V devices on VDDA: MIM couples the ring node to the gate of a self-biased inverter (feedback
# resistor from its output), a second inverter squares the edge. First stage at L = 0.5 um, 1.5 / 0.6 um: a first
# try at L = 1 um (0.84 / 0.42) drew less current but swung only 1.1 V at ss / 110 C / 880 MHz (step 74-HV log).
BUF = """.subckt acbuf in o vdd vss
xcc g in sky130_fd_pr__cap_mim_m3_1 w=4.2 l=4.2 m=1
xrf g x vss sky130_fd_pr__res_xhigh_po_0p35 l=39.8 mult=1 m=1
xp1 x g vdd vdd sky130_fd_pr__pfet_g5v0d10v5 w=1.5 l=0.5 nf=1 ad=0.44 as=0.44 pd=3.58 ps=3.58
xn1 x g vss vss sky130_fd_pr__nfet_g5v0d10v5 w=0.6 l=0.5 nf=1 ad=0.17 as=0.17 pd=1.78 ps=1.78
xp2 o x vdd vdd sky130_fd_pr__pfet_g5v0d10v5 w=3 l=0.5 nf=1 ad=0.87 as=0.87 pd=6.58 ps=6.58
xn2 o x vss vss sky130_fd_pr__nfet_g5v0d10v5 w=1.2 l=0.5 nf=1 ad=0.35 as=0.35 pd=2.98 ps=2.98
.ends
"""
# same buffer with ideal R and C of the PDK devices' values (MIM 38.47 fF, poly R 228 kOhm): for the long runs
BUF_IDEAL = BUF.replace("xcc g in sky130_fd_pr__cap_mim_m3_1 w=4.2 l=4.2 m=1", "cc g in 38.47f").replace(
    "xrf g x vss sky130_fd_pr__res_xhigh_po_0p35 l=39.8 mult=1 m=1", "rf g x 228.0k\ncrg g vss 3.05f\ncrx x vss 3.05f")


def netlist(p, corner="tt", temp=27, I=1.0e-3, vtune=1.65, cpar=10e-15, tstop=60e-9, tstep=4e-12, mode="run",
            inj=None, save=None, r0=12, r1=28, vdda=3.3, extra="", opt="", buf="ideal", cload=15e-15, mism=None):
    """One transient of the ring fed by an ideal current source I (the CCO). cpar = wiring per node, cload = what each
    buffer drives (the SSPD / NCB / divider inputs, or the dummy's open output). mism = {instance: dW factor} for start-up."""
    lines = []
    for k in range(NST):
        ip, im = P_[k], M_[k]
        op, om = (P_[k+1], M_[k+1]) if k < NST-1 else ("vom", "vop")
        lines.append(f"x{k+1} {ip} {im} {op} {om} vtune vddvco vss dcell\n")
    bufs = "".join(f"xb_{n} {n} bo_{n} vdda vss acbuf\ncb_{n} bo_{n} vss {cload:.4e}\n" for n in P_ + M_)
    src = f"ivco 0 vddvco dc {I}\n" if mode != "pwrup" else f"ivco 0 vddvco pwl(0 0 2n {I})\n"
    ic = "v(vddvco)=2.0 v(vop)=0 v(vom)=2.0" if mode != "pwrup" else "v(vddvco)=0 " + " ".join(f"v({n})=0" for n in P_ + M_)
    injl = ""
    if inj:
        node, t, q = inj
        injl = (f"iinj 0 {node} pwl(0 0 {t:.6e} 0 {t+1e-13:.6e} {q/1e-12:.6e} {t+1e-12:.6e} {q/1e-12:.6e} "
                f"{t+1.1e-12:.6e} 0)\n")
    if save == "min":
        sv, wr = "save v(vop) v(vom) v(vddvco) vdda#branch\n", ""
    else:
        sv = f"save all {save}\n" if save else ""
        wr = f"wrdata {{wr}} {save}\n" if save else ""
    body = cell(p).replace('{cpar}', f'{cpar:.4e}')
    if mism:                                  # a mismatched copy of the cell for stage 1 (start-up check)
        q = {k: ((x[0], x[1]*mism.get(k, 1.0), x[2], x[3]) if isinstance(x, tuple) else x) for k, x in p.items()}
        body += cell(q).replace(".subckt dcell", ".subckt dcellm").replace('{cpar}', f'{cpar:.4e}')
        lines[0] = lines[0].replace(" dcell\n", " dcellm\n")
    return f"""* step 74 HV ring: {corner} {temp} C, I = {I}, vtune = {vtune}, cpar = {cpar}
.lib {LIB} {corner}
.temp {temp}
{body}{BUF if buf == "pdk" else BUF_IDEAL}vss vss 0 0
vdda vdda 0 {vdda}
vtn vtune 0 {vtune}
{src}cdec vddvco 0 0.5p
{''.join(lines)}{bufs}{injl}{extra}.ic {ic}
.control
option noinit {opt}
{sv}tran {tstep} {tstop} 0 {tstep} uic
let vd = v(vop)-v(vom)
meas tran ta when vd=0 rise={r0}
meas tran tb when vd=0 rise={r1}
let f = {r1 - r0}/(tb-ta)
meas tran vdd_avg avg v(vddvco) from=ta to=tb
meas tran vdd_max max v(vddvco) from=ta to=tb
meas tran ppd pp vd from=ta to=tb
meas tran vmax max v(vop) from=ta to=tb
meas tran vmin min v(vop) from=ta to=tb
meas tran ibuf avg i(vdda) from=ta to=tb
print f vdd_avg vdd_max ppd vmax vmin ta tb ibuf
{wr}.endc
.end
"""


def run(net, wr=None):
    r = v18.run(net, wr)
    return r


def run_full(net):
    """run() plus the buffer supply current (avg i(vdda))."""
    with tempfile.TemporaryDirectory() as d:
        fn = os.path.join(d, "r.sp"); open(fn, "w").write(net); v18.spinit(d)
        out = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, timeout=3000, cwd=d).stdout
    r = {}
    for k in ("f", "vdd_avg", "vdd_max", "ppd", "vmax", "vmin", "ta", "tb", "ibuf"):
        m = re.search(rf"^{k} = (\S+)", out, re.M)
        if m:
            r[k] = float(m.group(1))
    return r


def _one(args):
    p, kw = args
    return run_full(netlist(p, **kw))


def freq_sweep(p, Is, **kw):
    with Pool(2) as pool:
        return pool.map(_one, [(p, dict(kw, I=I)) for I in Is])


def find_current(p, f_target, I0=1.0e-3, **kw):
    """Feed current that gives f_target (secant on log f vs log I)."""
    a, b = I0, I0*1.15
    ra, rb = freq_sweep(p, [a, b], **kw)
    c, rc = b, rb
    for _ in range(5):
        ex = np.log(rb["f"]/ra["f"])/np.log(b/a)
        c = b*(f_target/rb["f"])**(1/ex)
        rc = run_full(netlist(p, I=c, **kw))
        a, ra, b, rb = b, rb, c, rc
        if abs(rc["f"]/f_target - 1) < 2e-3:
            break
    return c, rc


# ------------------------------------------------------------------ device noise tables of the 5 V devices (3.3 V grid)
VGS = np.array([0.3, 0.6, 0.8, 1.0, 1.2, 1.5, 1.8, 2.1, 2.5, 2.9, 3.3])
VDS = np.array([0.02, 0.1, 0.25, 0.5, 0.8, 1.2, 1.6, 2.0, 2.5, 3.0, 3.3])


def _noise_pt(args):
    model, l, vgs, vds = args
    if model.startswith("pfet"):
        ckt = (f"vs s 0 3.3\nvg g 0 dc {3.3-vgs} ac 1\nvd d 0 {3.3-vds}\n"
               f"xm d g s s sky130_fd_pr__{model} w=1 l={l} nf=1 ad=0.29 as=0.29 pd=2.58 ps=2.58\n")
    else:
        ckt = (f"vg g 0 dc {vgs} ac 1\nvd d 0 {vds}\n"
               f"xm d g 0 0 sky130_fd_pr__{model} w=1 l={l} nf=1 ad=0.29 as=0.29 pd=2.58 ps=2.58\n")
    net = f"* noise point\n.lib {LIB} tt\n.temp 27\n{ckt}h1 o 0 vd 1\n.control\noption sparse\n" \
          f"noise v(o) vg dec 1 1k 1g\nsetplot noise1\nprint onoise_spectrum\n.endc\n.end\n"
    with tempfile.TemporaryDirectory() as d:
        fn = os.path.join(d, "n.sp"); open(fn, "w").write(net); v18.spinit(d)
        out = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, cwd=d).stdout
    sp = dict((float(a), float(b)**2) for a, b in re.findall(r"^\d+\s+(\S+)\s+(\S+)", out, re.M))
    B = sp[1e3]*1e3
    return max(sp[1e9] - B/1e9, 0.0), B


def noise_table(model, l):
    """(S_th, B) on the VGS x VDS grid for a W = 1 um device; cached in data/noisegrid_<model>_<l>.npz.
    S_th = white drain-current noise (A^2/Hz), B = flicker coefficient: S_fl(f) = B/f (A^2)."""
    fn = os.path.join(HERE, "data", f"noisegrid_{model}_{l}.npz")
    if os.path.exists(fn):
        z = np.load(fn); return z["sth"], z["b"]
    pts = [(model, l, a, b) for a in VGS for b in VDS]
    with Pool(2) as pool:
        r = pool.map(_noise_pt, pts)
    sth = np.array([x[0] for x in r]).reshape(len(VGS), len(VDS)); b = np.array([x[1] for x in r]).reshape(len(VGS), len(VDS))
    # the g5v0d10v5 nMOS model returns nan for the 1 GHz noise deep in triode (high V_GS, V_DS <= 0.25 V); those few
    # points take the largest finite value of their V_GS row (the saturation value) - conservative
    bad = ~np.isfinite(sth)
    for i, j in np.argwhere(bad):
        sth[i, j] = np.nanmax(sth[i])
    np.savez(fn, vgs=VGS, vds=VDS, sth=sth, b=b, filled=np.argwhere(bad))
    return sth, b


# ------------------------------------------------------------------ ISF phase noise (Hajimiri-Lee), method M2
def _inj(args):
    p, kw, tau, q = args
    r = run_full(netlist(p, inj=("p1", tau, q), save="min", **kw))
    return r.get("tb")


def isf_noise(p, I, K=12, q=4e-15, corner="tt", temp=27, vtune=1.65, cpar=10e-15, r0=10, r1=22, tstep=3e-12, f_guess=0.8e9):
    """ISF of node p1 (one of the 2N equivalent nodes): +-q injections at K phases; noise of every channel touching p1
    from the W = 1 um tables scaled by W, with their bias over one cycle.
    Returns dict(f0, Lth, Lfl, Ltot (dBc/Hz at 1 MHz), fc3 (Hz), h, hdc_over_hrms, shares)."""
    from scipy.interpolate import RegularGridInterpolator as RGI
    devs = {"x1.xp2": p["P"], "x1.xn2": p["N"], "x1.xs2": p.get("S"), "x1.xt1n": p.get("TN"), "x1.xt1p": p["TP"],
            "x2.xt1n": p.get("TN"), "x2.xt1p": p["TP"]}
    if p.get("tune", "switch") != "switch":
        devs.pop("x1.xs2")                      # varactor: its channel current flows to vtune, not into the node
    devs = {k: d for k, d in devs.items() if d}
    vec = lambda d, k: f"@m.{d}.msky130_fd_pr__{devs[d][0]}[{k}]"
    sv = " ".join(vec(d, k) for d in devs for k in ("vgs", "vds"))
    base = dict(corner=corner, temp=temp, vtune=vtune, cpar=cpar, r0=r0, r1=r1, tstep=tstep, opt="reltol=1e-4")
    with tempfile.TemporaryDirectory() as d:
        wr = os.path.join(d, "bias.txt")
        ref0 = v18.run(netlist(p, I=I, tstop=(r1 + 3)/(0.8*f_guess), save=sv, **base), wr=wr)
        g = np.loadtxt(wr)
    T = (ref0["tb"] - ref0["ta"])/(r1 - r0); t0 = ref0["ta"]
    tstop = t0 + (r1 - r0 + 3)*T
    jobs = [(p, dict(base, I=I, tstop=tstop), t0 + k*T/K, s*q) for k in range(K) for s in (1, -1)]
    with Pool(2) as pool:
        tz = pool.map(_inj, jobs)
    h = np.array([-2*np.pi*(tz[2*k] - tz[2*k + 1])/T/(2*q) for k in range(K)])
    t = g[:, 0]; cols = g[:, 1::2]
    m = (t >= t0) & (t < t0 + T); tt = t[m]; C = cols[m]; dt = np.diff(np.r_[tt, t0 + T])
    hf = np.interp((tt - t0)/T, np.r_[np.arange(K)/K, 1.0], np.r_[h, h[0]])
    th = fl = 0.0; shares = {}
    for i, (dname, (model, w, nf, l)) in enumerate(devs.items()):
        sth, b = noise_table(model, l)
        fs = RGI((VGS, VDS), sth, bounds_error=False, fill_value=None)
        fb = RGI((VGS, VDS), b, bounds_error=False, fill_value=None)
        vgs, vds = C[:, 2*i], C[:, 2*i + 1]
        # ngspice reports a pMOS's vgs/vds as positive magnitudes (type-normalised), like the tables
        rev = vds < 0; vgs = np.where(rev, vgs - vds, vgs); vds = np.abs(vds)
        pts = np.c_[np.clip(vgs, VGS[0], VGS[-1]), np.clip(vds, VDS[0], VDS[-1])]
        W = w*nf
        St = np.clip(fs(pts), 0, None)*W; Bt = np.clip(fb(pts), 0, None)*W
        a_th = np.sum(hf**2*St*dt)/T; a0 = np.sum(hf*np.sqrt(Bt)*dt)/T
        th += a_th; fl += a0**2; shares[dname] = (a_th, a0**2)
    dw = 2*np.pi*1e6; N2 = 2*NST
    Lth = 10*np.log10(N2*th/(2*dw**2)); Lfl = 10*np.log10(N2*fl/1e6/(2*dw**2))
    Ltot = 10*np.log10(10**(Lth/10) + 10**(Lfl/10))
    return dict(f0=1/T, I=I, Lth=Lth, Lfl=Lfl, Ltot=Ltot, fc3=1e6*10**((Lfl - Lth)/10), h=h.tolist(),
                hdc_over_hrms=float(np.mean(h)/np.sqrt(np.mean(h**2))),
                shares={k: (v[0]/th, v[1]/fl) for k, v in shares.items()})


def buffer_current(corner="tt", temp=27, vdda=3.3, f=0.8e9, swing=2.0, cload=15e-15, buf="pdk"):
    """Supply current of one output buffer driven by a 0..swing square wave at f, and with no input (static)."""
    b = BUF if buf == "pdk" else BUF_IDEAL
    out = {}
    for name, src in (("running", f"vin in 0 pulse(0 {swing} 0 {0.15/f:.4e} {0.15/f:.4e} {0.35/f:.4e} {1/f:.4e})\n"),
                      ("static", "vin in 0 0\n")):
        net = (f"* buffer current\n.lib {LIB} {corner}\n.temp {temp}\n{b}vdda vdda 0 {vdda}\nvss vss 0 0\n{src}"
               f"xb in o vdda vss acbuf\ncl o 0 {cload}\n.control\ntran 5p {40/f:.4e}\nmeas tran ia avg i(vdda) from={20/f:.4e} "
               f"to={40/f:.4e}\nmeas tran opp pp v(o) from={20/f:.4e} to={40/f:.4e}\nprint ia opp\n.endc\n.end\n")
        with tempfile.TemporaryDirectory() as d:
            fn = os.path.join(d, "b.sp"); open(fn, "w").write(net); v18.spinit(d)
            o = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, cwd=d).stdout
        ia = re.search(r"^ia = (\S+)", o, re.M); op = re.search(r"^opp = (\S+)", o, re.M)
        out[name] = (abs(float(ia.group(1))) if ia else None, float(op.group(1)) if op else None)
    return out


def lvs_reference(p):
    """The simulated circuit as a hierarchical netlist with the schematic's cell and pin names (for netgen)."""
    c = cell(p).replace(".subckt dcell inp inm outp outm vtune vdd vss",
                        ".subckt sspll_vco_hv_dcell inp inm outp outm vtune VDD VSS")
    c = "\n".join(l for l in c.split("\n") if not l.startswith("cp")) + "\n"
    b = BUF.replace(".subckt acbuf in o vdd vss", ".subckt sspll_vco_hv_acbuf in out VDD VSS").replace(" o x ", " out x ")
    c += b
    c = re.sub(r"\bvdd\b", "VDD", c); c = re.sub(r"\bvss\b", "VSS", c)
    core = [".subckt sspll_vco_hv_core vop p1 p2 vom m1 m2 VDD vtune VSS"]
    for k in range(NST):
        op, om = (P_[k+1], M_[k+1]) if k < NST-1 else ("vom", "vop")
        core.append(f"x{k+1} {P_[k]} {M_[k]} {op} {om} vtune VDD VSS sspll_vco_hv_dcell")
    core.append(".ends")
    top = [".subckt sspll_vco_hv VRING vtune VDDA VSS clkp clkm"]
    top.append("xcore vop p1 p2 vom m1 m2 VRING vtune VSS sspll_vco_hv_core")
    for n in P_ + M_:
        o = {"vop": "clkp", "vom": "clkm"}.get(n, f"nc_{n}")
        top.append(f"xb_{n} {n} {o} VDDA VSS sspll_vco_hv_acbuf")
    top.append(".ends")
    return c + "\n".join(core) + "\n" + "\n".join(top) + "\n"
