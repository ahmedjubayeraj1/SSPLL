"""vco.py - parametric 5-stage pseudo-differential ring VCO for the frozen SKY130 PDK.

Cell (one half; the other half is mirrored), after Nagam & Kinget and the proposal's x1.5 cell:
  main inverter  P (pfet) / N (nfet)  in -> out   (inp -> outm, inm -> outp)
  fine tuning    switch S (nfet, gate = vtune) from out to a MOS-cap C (nfet gate cap) -> K_VCO < 0
  coupling       always-on transmission gate TN/TP from inp -> outp (and inm -> outm) ties the two halves
Every device is described by (model, W per finger, nf, L) so the netlist is the layout: integer fingers, unit widths.

Functions: netlist(), run(), freq(), find_current(), isf_noise().  Paths: PDK from $PDK_ROOT (default /home/claude/pdk).
"""
import os, re, subprocess, tempfile, numpy as np
from multiprocessing import Pool

PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/pdk")
LIB = f"{PDK_ROOT}/sky130A/libs.tech/ngspice/sky130.lib.spice"
HERE = os.path.dirname(os.path.abspath(__file__))

# proposal cell x1.5 (old cell: P 8, N 4, S 1.5, C 3/0.5, TG 0.42 -> x1.5), drawn with integer fingers
BASE = dict(P=("pfet_01v8", 3.0, 4, 0.15), N=("nfet_01v8", 3.0, 2, 0.15),
            S=("nfet_01v8", 2.25, 1, 0.15), C=("nfet_01v8", 4.5, 1, 0.5),
            TN=("nfet_01v8", 0.63, 1, 0.15), TP=("pfet_01v8", 0.63, 1, 0.15))

# VCO cell: the base cell with the two flicker sources found by the ISF (fine-tune switch S, TG nMOS) drawn at
# L = 0.3 um (S keeps W/L = 15; TN keeps W = 0.84 um). 1/f^3 corner 1.02 -> 0.57 MHz for +9 % current.
FINAL = dict(BASE, S=("nfet_01v8", 4.5, 1, 0.3), TN=("nfet_01v8", 0.84, 1, 0.3))


def _m(name, d, g, s, b, dev):
    model, w, nf, l = dev
    wt = w*nf          # xschem sky130 symbol formulas: shared diffusion of multi-finger devices
    ad = int((nf + 1)/2)*w*0.29; as_ = int((nf + 2)/2)*w*0.29
    pd = 2*int((nf + 1)/2)*(w + 0.29); ps = 2*int((nf + 2)/2)*(w + 0.29)
    return (f"x{name} {d} {g} {s} {b} sky130_fd_pr__{model} w={wt:.3f} l={l} nf={nf} "
            f"ad={ad:.4f} as={as_:.4f} pd={pd:.3f} ps={ps:.3f}\n")


def cell(p):
    c = ".subckt dcell inp inm outp outm vtune vdd vss\n"
    c += _m("p1", "outm", "inp", "vdd", "vdd", p["P"]) + _m("n1", "outm", "inp", "vss", "vss", p["N"])
    c += _m("p2", "outp", "inm", "vdd", "vdd", p["P"]) + _m("n2", "outp", "inm", "vss", "vss", p["N"])
    c += _m("s1", "outm", "vtune", "c1n", "vss", p["S"]) + _m("c1", "vss", "c1n", "vss", "vss", p["C"])
    c += _m("s2", "outp", "vtune", "c2n", "vss", p["S"]) + _m("c2", "vss", "c2n", "vss", "vss", p["C"])
    c += _m("t1n", "inp", "vdd", "outp", "vss", p["TN"]) + _m("t1p", "inp", "vss", "outp", "vdd", p["TP"])
    c += _m("t2n", "inm", "vdd", "outm", "vss", p["TN"]) + _m("t2p", "inm", "vss", "outm", "vdd", p["TP"])
    c += "cpp outp vss {cpar}\ncpm outm vss {cpar}\n.ends\n"
    return c


BUF = """.subckt acbuf in vdd vss
* MIM: c0 (top plate, capm) on the buffer gate g, c1 (bottom plate, met3) on the strongly driven ring node
xcc g in sky130_fd_pr__cap_mim_m3_1 w=4.2 l=4.2 m=1
xrf g x vss sky130_fd_pr__res_xhigh_po_0p35 l=39.8 mult=1 m=1
xp1 x g vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15 nf=1 ad=0.58 as=0.58 pd=4.58 ps=4.58
xn1 x g vss vss sky130_fd_pr__nfet_01v8 w=1 l=0.15 nf=1 ad=0.29 as=0.29 pd=2.58 ps=2.58
xp2 o x vdd vdd sky130_fd_pr__pfet_01v8 w=4 l=0.15 nf=1 ad=1.16 as=1.16 pd=8.58 ps=8.58
xn2 o x vss vss sky130_fd_pr__nfet_01v8 w=2 l=0.15 nf=1 ad=0.58 as=0.58 pd=4.58 ps=4.58
.ends
"""
# same buffer with ideal R and C of the PDK devices' values (C 38.47 fF, R 227.4 kOhm from the PDK models): used for
# the long characterisation runs because the PDK MIM / poly-resistor subcircuits make the transient ~5x slower.
BUF_IDEAL = BUF.replace("xcc g in sky130_fd_pr__cap_mim_m3_1 w=4.2 l=4.2 m=1", "cc g in 38.47f").replace(
    "xrf g x vss sky130_fd_pr__res_xhigh_po_0p35 l=39.8 mult=1 m=1", "rf g x 228.0k\ncrg g vss 3.05f\ncrx x vss 3.05f")
NST = 5
P_ = ["vop"] + [f"p{k}" for k in range(1, NST)]
M_ = ["vom"] + [f"m{k}" for k in range(1, NST)]


def netlist(p, corner="tt", temp=27, I=1.31e-3, vtune=0.9, cpar=10e-15, tstop=26e-9, tstep=2e-12, mode="run",
            inj=None, save=None, r0=None, r1=None, vbuf=1.8, extra="", opt="", buf="ideal"):
    lines = []
    for k in range(NST):
        ip, im = P_[k], M_[k]
        op, om = (P_[k+1], M_[k+1]) if k < NST-1 else ("vom", "vop")
        lines.append(f"x{k+1} {ip} {im} {op} {om} vtune vddvco vss dcell\n")
    bufs = "".join(f"xb_{n} {n} vddbuf vss acbuf\n" for n in P_ + M_)
    src = f"ivco 0 vddvco dc {I}\n" if mode != "pwrup" else f"ivco 0 vddvco pwl(0 0 2n {I})\n"
    ic = "v(vddvco)=1.3 v(vop)=0 v(vom)=1.3" if mode != "pwrup" else "v(vddvco)=0 " + " ".join(f"v({n})=0" for n in P_ + M_)
    injl = ""
    if inj:
        node, t, q = inj
        injl = (f"iinj 0 {node} pwl(0 0 {t:.6e} 0 {t+1e-13:.6e} {q/1e-12:.6e} {t+1e-12:.6e} {q/1e-12:.6e} "
                f"{t+1.1e-12:.6e} 0)\n")
    r0 = r0 or 12; r1 = r1 or 32
    if save == "min":                       # injection runs: keep only what the measurement needs (much faster)
        sv, wr = "save v(vop) v(vom) v(vddvco)\n", ""
    else:
        sv = f"save all {save}\n" if save else ""
        wr = f"wrdata {{wr}} {save}\n" if save else ""
    return f"""* the VCO ring: {corner} {temp} C, I = {I}, vtune = {vtune}, cpar = {cpar}
.lib {LIB} {corner}
.temp {temp}
{cell(p).replace('{cpar}', f'{cpar:.4e}')}{BUF if buf == "pdk" else BUF_IDEAL}vss vss 0 0
vbuf vddbuf 0 {vbuf}
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
print f vdd_avg vdd_max ppd vmax vmin ta tb
{wr}.endc
.end
"""


def spinit(d):
    """Copy the PDK's ngspice init file into the run folder as .spiceinit. Without it (until 15 Nov 2026) the ring ran
    4.6 % slow: ngbehavior=hsa is needed to read the sky130 model files correctly."""
    open(os.path.join(d, ".spiceinit"), "w").write(open(os.path.join(os.path.dirname(LIB), "spinit")).read())


def run(net, wr=None):
    with tempfile.TemporaryDirectory() as d:
        fn = os.path.join(d, "r.sp")
        if wr:
            net = net.replace("{wr}", wr)
        open(fn, "w").write(net)
        spinit(d)                              # PDK .spiceinit (ngbehavior=hsa) - required by the sky130 models
        out = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, timeout=3000, cwd=d).stdout
    r = {}
    for k in ("f", "vdd_avg", "vdd_max", "ppd", "vmax", "vmin", "ta", "tb"):
        m = re.search(rf"^{k} = (\S+)", out, re.M)
        if m:
            r[k] = float(m.group(1))
    return r


def _one(args):
    p, kw = args
    return run(netlist(p, **kw))


def freq_sweep(p, Is, **kw):
    """f, ring-node voltage etc. for a list of feed currents (2 parallel ngspice jobs)."""
    with Pool(2) as pool:
        return pool.map(_one, [(p, dict(kw, I=I)) for I in Is])


def find_current(p, f_target, I0=1.2e-3, **kw):
    """Feed current that gives f_target (secant on log f vs log I; f ~ I^a)."""
    a, b = I0*0.85, I0*1.15
    ra, rb = freq_sweep(p, [a, b], **kw)
    for _ in range(4):
        ex = np.log(rb["f"]/ra["f"])/np.log(b/a)
        c = b*(f_target/rb["f"])**(1/ex)
        rc = run(netlist(p, I=c, **kw))
        a, ra, b, rb = b, rb, c, rc
        if abs(rc["f"]/f_target - 1) < 2e-3:
            break
    return c, rc


# ------------------------------------------------------------------ device noise tables (thermal + 1/f), per model and L
VGS = np.array([0.2, 0.35, 0.5, 0.65, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8])
VDS = np.array([0.02, 0.1, 0.2, 0.35, 0.5, 0.7, 0.9, 1.2, 1.5, 1.8])


def _noise_pt(args):
    model, l, vgs, vds = args
    pch = model.startswith("pfet")
    if pch:
        ckt = (f"vs s 0 1.8\nvg g 0 dc {1.8-vgs} ac 1\nvd d 0 {1.8-vds}\n"
               f"xm d g s s sky130_fd_pr__{model} w=1 l={l} nf=1 ad=0.29 as=0.29 pd=2.58 ps=2.58\n")
    else:
        ckt = (f"vg g 0 dc {vgs} ac 1\nvd d 0 {vds}\n"
               f"xm d g 0 0 sky130_fd_pr__{model} w=1 l={l} nf=1 ad=0.29 as=0.29 pd=2.58 ps=2.58\n")
    net = f"""* noise point
.lib {LIB} tt
.temp 27
{ckt}h1 o 0 vd 1
.control
option sparse
noise v(o) vg dec 1 1k 1g
setplot noise1
print onoise_spectrum
.endc
.end
"""
    with tempfile.TemporaryDirectory() as d:
        fn = os.path.join(d, "n.sp"); open(fn, "w").write(net); spinit(d)
        out = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, cwd=d).stdout
    sp = dict((float(a), float(b)**2) for a, b in re.findall(r"^\d+\s+(\S+)\s+(\S+)", out, re.M))
    B = sp[1e3]*1e3
    return max(sp[1e9] - B/1e9, 0.0), B


def noise_table(model, l):
    """(S_th, B) on the VGS x VDS grid for a W = 1 um device; cached in data/noisegrid_<model>_<l>.npz."""
    fn = os.path.join(HERE, "data", f"noisegrid_{model}_{l}.npz")
    if os.path.exists(fn):
        z = np.load(fn); return z["sth"], z["b"]
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    pts = [(model, l, a, b) for a in VGS for b in VDS]
    with Pool(2) as pool:
        r = pool.map(_noise_pt, pts)
    sth = np.array([x[0] for x in r]).reshape(len(VGS), len(VDS)); b = np.array([x[1] for x in r]).reshape(len(VGS), len(VDS))
    np.savez(fn, vgs=VGS, vds=VDS, sth=sth, b=b)
    return sth, b


# ------------------------------------------------------------------ ISF phase noise with the models' thermal + flicker noise
def _inj(args):
    p, kw, tau, q = args
    r = run(netlist(p, inj=("p1", tau, q), save="min", **kw))
    return r.get("tb")


def isf_noise(p, I, K=12, q=2e-15, corner="tt", temp=27, vtune=0.9, cpar=10e-15, r0=12, r1=26, tstep=1.5e-12):
    """Hajimiri-Lee ISF of node p1 (one of the 2N equivalent nodes): +-q injections at K phases; device noise of
    every channel touching p1 from the W = 1 um tables scaled by W, with their bias over one cycle.
    Returns dict(f0, Lth, Lfl, Ltot (dBc/Hz at 1 MHz), fc3 (Hz), h (rad/C), hdc_over_hrms, shares)."""
    from scipy.interpolate import RegularGridInterpolator as RGI
    devs = {"x1.xp2": p["P"], "x1.xn2": p["N"], "x1.xs2": p["S"], "x1.xt1n": p["TN"], "x1.xt1p": p["TP"],
            "x2.xt1n": p["TN"], "x2.xt1p": p["TP"]}
    vec = lambda d, k: f"@m.{d}.msky130_fd_pr__{devs[d][0]}[{k}]"
    sv = " ".join(vec(d, k) for d in devs for k in ("vgs", "vds"))
    base = dict(corner=corner, temp=temp, vtune=vtune, cpar=cpar, r0=r0, r1=r1, tstep=tstep, opt="reltol=1e-4")
    # reference run: period, t0 and device bias over one cycle
    with tempfile.TemporaryDirectory() as d:
        wr = os.path.join(d, "bias.txt")
        ref0 = run(netlist(p, I=I, tstop=(r1 + 3)/1.3e9, save=sv, **base), wr=wr)
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
        rev = vds < 0; vgs = np.where(rev, vgs - vds, vgs); vds = np.abs(vds)
        pts = np.c_[np.clip(vgs, 0.2, 1.8), np.clip(vds, 0.02, 1.8)]
        W = w*nf
        St = np.clip(fs(pts), 0, None)*W; Bt = np.clip(fb(pts), 0, None)*W/(1.0)   # B ~ W for fixed L (per-um table)
        a_th = np.sum(hf**2*St*dt)/T; a0 = np.sum(hf*np.sqrt(Bt)*dt)/T
        th += a_th; fl += a0**2; shares[dname] = (a_th, a0**2)
    dw = 2*np.pi*1e6; N2 = 2*NST
    Lth = 10*np.log10(N2*th/(2*dw**2)); Lfl = 10*np.log10(N2*fl/1e6/(2*dw**2))
    Ltot = 10*np.log10(10**(Lth/10) + 10**(Lfl/10))
    return dict(f0=1/T, I=I, Lth=Lth, Lfl=Lfl, Ltot=Ltot, fc3=1e6*10**((Lfl - Lth)/10), h=h.tolist(),
                hdc_over_hrms=float(np.mean(h)/np.sqrt(np.mean(h**2))),
                shares={k: (v[0]/th, v[1]/fl) for k, v in shares.items()})


def lvs_reference(p):
    """The simulated circuit as a hierarchical netlist with the schematic's cell and pin names (for netgen)."""
    import re as _re
    c = cell(p).replace(".subckt dcell inp inm outp outm vtune vdd vss",
                        ".subckt sspll_vco_dcell inp inm outp outm vtune VDD VSS")
    c = "\n".join(l for l in c.split("\n") if not l.startswith("cp")) + "\n"
    b = BUF.replace(".subckt acbuf in vdd vss", ".subckt sspll_vco_acbuf in out VDD VSS").replace(" o x ", " out x ")
    c += b
    c = _re.sub(r"\bvdd\b", "VDD", c); c = _re.sub(r"\bvss\b", "VSS", c)
    core = [".subckt sspll_vco_core vop p1 p2 p3 p4 vom m1 m2 m3 m4 VDD vtune VSS"]
    for k in range(NST):
        op, om = (P_[k+1], M_[k+1]) if k < NST-1 else ("vom", "vop")
        core.append(f"x{k+1} {P_[k]} {M_[k]} {op} {om} vtune VDD VSS sspll_vco_dcell")
    core.append(".ends")
    top = [".subckt sspll_vco VDD vtune VDDBUF VSS vop vom clkp clkm",
           "xcore vop p1 p2 p3 p4 vom m1 m2 m3 m4 VDD vtune VSS sspll_vco_core"]
    for n in P_ + M_:
        o = {"vop": "clkp", "vom": "clkm"}.get(n, f"nc_{n}")
        top.append(f"xb_{n} {n} {o} VDDBUF VSS sspll_vco_acbuf")
    top.append(".ends")
    return c + "\n".join(core) + "\n" + "\n".join(top) + "\n"
