#!/usr/bin/env python3
"""hv_noise.py - thermal and flicker noise of the 5 V devices (g5v0d10v5) vs the 1.8 V devices, for the step-72 HV
budget. Each device is biased at g_m/I_D = 10 S/A, V_DS = 0.9 V (1.8 V) or 1.5 V (5 V), I_D = 100 uA; ngspice .noise
gives the drain-current noise PSD S_id(f). Reported: gamma = S_id,thermal/(4kT g_m), the 1/f corner (S_flicker =
S_thermal) and the gate-referred flicker voltage at 10 kHz. Run: python3 design/feas/hv_noise.py -> hv_noise.json"""
import os, re, json, subprocess, tempfile, numpy as np
PDK = os.environ.get("PDK_ROOT", "/home/claude/pdk"); LIB = f"{PDK}/sky130A/libs.tech/ngspice/sky130.lib.spice"
HERE = os.path.dirname(os.path.abspath(__file__)); kT = 1.380649e-23*300
DEV = [("nfet_01v8", 0.15, 0.9), ("nfet_01v8", 0.5, 0.9), ("nfet_g5v0d10v5", 0.5, 1.5), ("nfet_g5v0d10v5", 1.0, 1.5),
       ("pfet_01v8", 0.15, 0.9), ("pfet_g5v0d10v5", 0.5, 1.5), ("pfet_g5v0d10v5", 1.0, 1.5)]


def spinit(d):
    open(os.path.join(d, ".spiceinit"), "w").write("set ngbehavior=hsa\nset ng_nomodcheck\nset skywaterpdk\noption noinit\n")


def run(net):
    with tempfile.TemporaryDirectory() as d:
        fn = os.path.join(d, "n.sp"); open(fn, "w").write(net); spinit(d)
        return subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, cwd=d).stdout


def ckt(model, w, l, vgs, vds):
    """device with W split into m parallel fingers of at most 40 um (the model bins end near 100 um)"""
    p = model.startswith("p"); vdd = 3.3 if "g5v0" in model else 1.8
    m = int(np.ceil(w/40)); w = round(w/m, 3)
    if p:
        return (f"vs s 0 {vdd}\nvg g 0 dc {vdd-vgs} ac 1\nvd d 0 {vdd-vds}\n"
                f"xm d g s s sky130_fd_pr__{model} w={w} l={l} nf=1 m={m}\n")
    return f"vg g 0 dc {vgs} ac 1\nvd d 0 {vds}\nxm d g 0 0 sky130_fd_pr__{model} w={w} l={l} nf=1 m={m}\n"


def sweep(model, w, l, vds, vs):
    """drain current vs V_GS in one ngspice run (dc sweep of the gate source)."""
    p = model.startswith("p"); vdd = 3.3 if "g5v0" in model else 1.8
    a, b = ((vdd - vs[0], vdd - vs[-1]) if p else (vs[0], vs[-1]))
    step = -(vs[1]-vs[0]) if p else (vs[1]-vs[0])
    out = run(f"* sweep\n.lib {LIB} tt\n.temp 27\n{ckt(model, w, l, vs[0], vds)}.control\noption sparse\n"
              f"dc vg {a} {b} {step}\nprint i(vd)\n.endc\n.end\n")
    i = [abs(float(x)) for x in re.findall(r"^\d+\s+\S+\s+(\S+)", out, re.M)]
    return np.array(i[:len(vs)])


def point(model, l, vds, gmid=10.0, I=100e-6):
    # g_m/I_D = d ln(I)/dV_GS on W = 10 um; find V_GS where it equals gmid, then scale W to I
    vs = np.round(np.arange(0.3, 3.0 if 'g5v0' in model else 1.8, 0.01), 3); Iw = sweep(model, 10, l, vds, vs)
    gi = np.gradient(np.log(Iw), vs); k0 = int(np.argmax(gi)); k = k0 + np.where(gi[k0:] < gmid)[0][0]   # past the leakage region
    vgs = np.interp(gmid, [gi[k], gi[k-1]], [vs[k], vs[k-1]]); i10 = np.interp(vgs, vs, Iw)
    w = round(10*I/i10, 2)
    out = run(f"* noise\n.lib {LIB} tt\n.temp 27\n{ckt(model, w, l, vgs, vds)}h1 o 0 vd 1\n.control\noption sparse\n"
              f"noise v(o) vg dec 10 100 1g\nsetplot noise1\nprint onoise_spectrum inoise_spectrum\n.endc\n.end\n")
    rows = re.findall(r"^\d+\s+(\S+)\s+(\S+)\s+(\S+)", out, re.M)
    f = np.array([float(r[0]) for r in rows]); so = np.array([float(r[1])**2 for r in rows]); si = np.array([float(r[2])**2 for r in rows])
    gm = np.sqrt(so[-1]/si[-1]) if si[-1] > 0 else 0       # |gain| = sqrt(So/Si)
    sth = so[-1]; corner = f[np.argmin(np.abs(so - 2*sth))]
    return dict(model=model, l=l, w=w, vgs=round(float(vgs), 3), gm=gm, gamma=sth/(4*kT*gm),
                corner_hz=float(corner), vn_10k=float(np.sqrt(np.interp(1e4, f, si))), area_um2=w*l)


if __name__ == "__main__":
    res = [point(m, l, v) for m, l, v in DEV]
    for r in res:
        print(f"{r['model']:16s} L {r['l']:.2f} W {r['w']:6.2f}  gm {r['gm']*1e3:.2f} mS  gamma {r['gamma']:.2f}  "
              f"1/f corner {r['corner_hz']/1e6:7.2f} MHz  vn(10k) {r['vn_10k']*1e9:6.1f} nV/rtHz  WL {r['area_um2']:.1f} um2")
    json.dump(res, open(os.path.join(HERE, "hv_noise.json"), "w"), indent=1)
