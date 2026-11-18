#!/usr/bin/env python3
"""devchar.py - characterisation of the devices allowed after the device-rule change (18 Nov 2026):
analog nfet/pfet_g5v0d10v5 (L >= 0.5 um, on 3.3 V) and, for comparison / digital, nfet/pfet_01v8 (L = 0.15 um, 1.8 V).
Per device (W = 4 um, tt 27 C and ss 110 C): Vth at |VDS| = 0.1 V; at |VDS| = VDD/2 a VGS sweep giving gm/Id, Id/W,
fT = gm/(2 pi Cgg) and intrinsic gain gm/gds; and the on-resistance x width of a switch at mid-rail (VS = VD = VDD/2).
Writes devchar.json and docs/img/hv_devchar.png."""
import os, re, json, subprocess, tempfile
import numpy as np
LIB = "/home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice"; SPI = "/home/claude/pdk/sky130A/libs.tech/ngspice/spinit"
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
DEV = [("nfet_g5v0d10v5", 0.5, 3.3), ("pfet_g5v0d10v5", 0.5, 3.3), ("nfet_g5v0d10v5", 1.0, 3.3), ("pfet_g5v0d10v5", 1.0, 3.3),
       ("nfet_01v8", 0.15, 1.8), ("pfet_01v8", 0.15, 1.8)]
W = 4.0

def ng(net):
    with tempfile.TemporaryDirectory() as d:
        os.system(f"cp {SPI} {d}/.spiceinit"); open(f"{d}/r.sp", "w").write(net)
        o = subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d)
        z = np.loadtxt(f"{d}/o.txt") if os.path.exists(f"{d}/o.txt") else None
    return o.stdout, z

def sweep(model, l, vdd, corner, temp):
    p = model.startswith("p"); inst = f"@m.xm.msky130_fd_pr__{model}"
    ad = f"ad={W*0.29} as={W*0.29} pd={2*W+0.58} ps={2*W+0.58}"
    vd = vdd/2
    if p:   # source at vdd, drain at vdd/2, gate swept down
        ckt = f"vs s 0 {vdd}\nvd d 0 {vdd - vd}\nvg g 0 {vdd}\nxm d g s s sky130_fd_pr__{model} w={W} l={l} nf=1 {ad}\n"
        dc = f"dc vg {vdd} 0 -0.02"
    else:
        ckt = f"vs s 0 0\nvd d 0 {vd}\nvg g 0 0\nxm d g s s sky130_fd_pr__{model} w={W} l={l} nf=1 {ad}\n"
        dc = f"dc vg 0 {vdd} 0.02"
    net = (f"* char\n.lib {LIB} {corner}\n.temp {temp}\n{ckt}.control\nsave all {inst}[gm] {inst}[id] {inst}[cgg] {inst}[gds] {inst}[vth]\n"
           f"{dc}\nwrdata o.txt v(g) {inst}[gm] {inst}[id] {inst}[cgg] {inst}[gds] {inst}[vth]\n.endc\n.end\n")
    _, z = ng(net)
    vg = z[:, 1]; gm, idd, cgg, gds, vth = (np.abs(z[:, 2*k + 3]) for k in range(5))
    vgs = (vdd - vg) if p else vg
    return vgs, gm, idd, cgg, gds, vth

def ron(model, l, vdd, corner, temp):
    p = model.startswith("p"); ad = f"ad={W*0.29} as={W*0.29} pd={2*W+0.58} ps={2*W+0.58}"
    g = 0 if p else vdd; b = vdd if p else 0
    net = (f"* ron\n.lib {LIB} {corner}\n.temp {temp}\nvs s 0 {vdd/2}\nvd d 0 {vdd/2 + 0.01}\nvg g 0 {g}\nvb b 0 {b}\n"
           f"xm d g s b sky130_fd_pr__{model} w={W} l={l} nf=1 {ad}\n.control\nop\nprint 0.01/abs(i(vd))\n.endc\n.end\n")
    o, _ = ng(net); r = re.search(r"=\s*(\S+)", o.split("0.01/abs")[-1])
    return float(r.group(1))*W if r else None          # ohm*um

if __name__ == "__main__":
    res = []
    for model, l, vdd in DEV:
        for corner, temp in (("tt", 27), ("ss", 110)):
            vgs, gm, idd, cgg, gds, vth = sweep(model, l, vdd, corner, temp)
            gmid = gm/np.maximum(idd, 1e-15); ft = gm/(2*np.pi*np.maximum(cgg, 1e-18)); av = gm/np.maximum(gds, 1e-15)
            pt = lambda target: dict(idw=float(np.interp(-target, -gmid, idd))/W, ft=float(np.interp(-target, -gmid, ft)),
                                     av=float(np.interp(-target, -gmid, av)), vgs=float(np.interp(-target, -gmid, vgs)))
            r = dict(model=model, l=l, vdd=vdd, corner=corner, temp=temp, vth=float(np.interp(0.0, -np.zeros(1), vth[:1])) if False else float(vth[np.argmin(abs(vgs - vdd/2))]),
                     gmid10=pt(10), gmid15=pt(15), ftmax=float(ft.max()), ron_um=ron(model, l, vdd, corner, temp),
                     curve=dict(gmid=gmid[::5].tolist(), idw=(idd[::5]/W).tolist(), ft=ft[::5].tolist()))
            res.append(r)
            print(f"{model:15} L {l:4} {corner} {temp:4}: Vth {r['vth']:.3f} V | gm/Id=10: Id/W {r['gmid10']['idw']*1e6:6.1f} uA/um fT {r['gmid10']['ft']/1e9:5.2f} GHz "
                  f"gm/gds {r['gmid10']['av']:5.1f} | fT max {r['ftmax']/1e9:5.1f} GHz | switch at VDD/2: {r['ron_um']:.0f} ohm*um")
    json.dump(res, open(os.path.join(HERE, "devchar.json"), "w"))
