"""cco.py - roadmap step 75: current-controlled supply (CCO) of the ring VCO, SKY130 3.3 V devices.

                VDDA ──┬───────────────┬──────────────┬──────────── (MIM C_f between VDDA and vgo, over the array)
                  MREF (1 unit, diode)  │          MOUT (NOUT units)
                       vgr ──[ R_f ]── vgo ─────────┘    │
                       │                                ring node (vring) ──> ring VCO, clamp, VTEST injection
          DAC: unit sinks 2.5 uA (x NBASE always on + 1,2,4,8,16 switched by cco_code)
          IBIAS 5 uA -> 2-unit nMOS diode sets the unit current
I_out = NOUT x 2.5 uA x (NBASE + code). Every device is (model, W per finger, nf, L) so the netlist is the layout."""
import os, re, subprocess, tempfile
import numpy as np
PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/pdk")
LIB = f"{PDK_ROOT}/sky130A/libs.tech/ngspice/sky130.lib.spice"
HERE = os.path.dirname(os.path.abspath(__file__))

D = dict(
    UP=("pfet_g5v0d10v5", 20.0, 2, 2.0),     # mirror unit pMOS (W 40 um, L 2 um)
    UN=("nfet_g5v0d10v5", 1.0, 1, 4.0),      # DAC / bias unit nMOS (2.5 uA)
    SW=("nfet_g5v0d10v5", 1.0, 1, 0.5),      # DAC unit switch
    NOUT=25, NBASE=11, R_F=10e6, C_F=7.28e-12,
    # filter as PDK devices: R_F = 20 series segments of res_xhigh_po_0p35 (L 87.48 um each), C_F = 4 MIM 30x30 tiles
    RSEG=("res_xhigh_po_0p35", 20, 87.48), CTILE=("cap_mim_m3_1", 4, 30.0),
    # ring-node clamp (active, two-stage): replica pMOS diode from the 1.8 V rail sets vclamp; sense pMOS (source =
    # ring node, gate = vclamp) drives RS; when its current x RS exceeds the shunt nMOS threshold, the shunt sinks the
    # excess. Onset is exponential (sense device in weak inversion) and the shunt adds gain -> sharp knee near VDDL.
    PCL=("pfet_01v8", 1.0, 1, 0.15), RS=("res_xhigh_po_0p35", 1, 56.0), NSH=("nfet_01v8", 5.0, 4, 0.15), K_CL=1,
    # VTEST injection: 3.3 V transmission gate + 20 kOhm poly resistor into the ring node
    TGN=("nfet_g5v0d10v5", 2.0, 1, 0.5), TGP=("pfet_g5v0d10v5", 2.0, 1, 0.5), RINJ=("res_xhigh_po_0p35", 1, 3.39),
    # enable: pMOS pull-up on the output gate, nMOS pull-down on the bias input
    PEN=("pfet_g5v0d10v5", 2.0, 1, 0.5), NEN=("nfet_g5v0d10v5", 2.0, 1, 0.5))


def _m(name, d, g, s, b, dev, m=1):
    model, w, nf, l = dev
    ad = int((nf + 1)/2)*w*0.29; as_ = int((nf + 2)/2)*w*0.29
    pd = 2*int((nf + 1)/2)*(w + 0.29); ps = 2*int((nf + 2)/2)*(w + 0.29)
    return (f"x{name} {d} {g} {s} {b} sky130_fd_pr__{model} w={w*nf:.3f} l={l} nf={nf} m={m} "
            f"ad={ad:.4f} as={as_:.4f} pd={pd:.3f} ps={ps:.3f}\n")


def core(p, code, ideal_rc=True):
    """CCO core subckt: ports vdda vss vring ibias. code = cco_code (0..31), switches as ideal 3.3 V gate levels."""
    c = ".subckt cco vdda vss vring ibias\n"
    c += _m("mref", "vgr", "vgr", "vdda", "vdda", p["UP"])
    c += _m("mout", "vring", "vgo", "vdda", "vdda", p["UP"], m=p["NOUT"])
    if ideal_rc:
        c += f"rf vgr vgo {p['R_F']}\ncf vgo vdda {p['C_F']}\n"
    c += _m("nb", "ibias", "ibias", "vss", "vss", p["UN"], m=2)            # IBIAS input diode (5 uA)
    bits = [p["NBASE"]] + [2**k for k in range(5)]
    on = [True] + [bool(code >> k & 1) for k in range(5)]
    for k, (n, e) in enumerate(zip(bits, on)):
        c += _m(f"u{k}", f"d{k}", "ibias", "vss", "vss", p["UN"], m=n)
        c += _m(f"s{k}", "vgr", f"en{k}", f"d{k}", "vss", p["SW"], m=n)
        c += f"ven{k} en{k} 0 {3.3 if e else 0}\n"
    return c + ".ends\n"


def run(net):
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, ".spiceinit"), "w").write(open(f"{PDK_ROOT}/sky130A/libs.tech/ngspice/spinit").read())
        open(os.path.join(d, "r.sp"), "w").write(net)
        return subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d, timeout=3000).stdout


def dc(p, code, corner="tt", temp=27, vdda=3.3, vring=1.45):
    net = f"""* cco dc
.lib {LIB} {corner}
.temp {temp}
{core(p, code)}vdda vdda 0 {vdda}
iib 0 ibias 5u
vr vring 0 {vring}
x1 vdda 0 vring ibias cco
.control
op
print -vr#branch v(x1.vgr)
.endc
.end
"""
    out = run(net)
    i = float(re.search(r"vr#branch = (\S+)", out).group(1))
    vg = float(re.search(r"v\(x1\.vgr\) = (\S+)", out).group(1))
    return -i if i < 0 else i, vg


def noise(p, code, corner="tt", temp=27, vdda=3.3, vring=1.45, fmin=1e3, fmax=1e8):
    """Output current noise (A/rtHz) into an ideal ring-node source vs frequency (.noise through a CCVS)."""
    net = f"""* cco noise
.lib {LIB} {corner}
.temp {temp}
{core(p, code)}vdda vdda 0 {vdda}
iib 0 ibias dc 5u ac 1
vr vring 0 {vring}
x1 vdda 0 vr2 ibias cco
vm vr2 vring 0
h1 o 0 vm 1
.control
option sparse
noise v(o) iib dec 10 {fmin} {fmax}
setplot noise1
wrdata noise.txt onoise_spectrum
.endc
.end
"""
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, ".spiceinit"), "w").write(open(f"{PDK_ROOT}/sky130A/libs.tech/ngspice/spinit").read())
        open(os.path.join(d, "r.sp"), "w").write(net)
        subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d, timeout=3000)
        z = np.loadtxt(os.path.join(d, "noise.txt"))
    return z[:, 0], z[:, 1]


LS = """.subckt sspll_ls_1v8_3v3 in out outb VDDD VDDA VSS
* 1.8 V -> 3.3 V level shifter: thin-oxide input inverter on VDDD, thick-oxide cross-coupled pMOS load,
* thick-oxide pull-downs driven by in / inb, thick-oxide output inverters (out follows in, outb is its inverse)
xpi inb in VDDD VDDD sky130_fd_pr__pfet_01v8 w=1 l=0.15 nf=1 m=1
xni inb in VSS VSS sky130_fd_pr__nfet_01v8 w=0.5 l=0.15 nf=1 m=1
xp1 x y VDDA VDDA sky130_fd_pr__pfet_g5v0d10v5 w=1 l=0.5 nf=1 m=1
xp2 y x VDDA VDDA sky130_fd_pr__pfet_g5v0d10v5 w=1 l=0.5 nf=1 m=1
xn1 x in VSS VSS sky130_fd_pr__nfet_g5v0d10v5 w=3 l=0.5 nf=1 m=1
xn2 y inb VSS VSS sky130_fd_pr__nfet_g5v0d10v5 w=3 l=0.5 nf=1 m=1
xpo out x VDDA VDDA sky130_fd_pr__pfet_g5v0d10v5 w=2 l=0.5 nf=1 m=1
xno out x VSS VSS sky130_fd_pr__nfet_g5v0d10v5 w=1 l=0.5 nf=1 m=1
xpb outb y VDDA VDDA sky130_fd_pr__pfet_g5v0d10v5 w=2 l=0.5 nf=1 m=1
xnb outb y VSS VSS sky130_fd_pr__nfet_g5v0d10v5 w=1 l=0.5 nf=1 m=1
.ends
"""


def full(p):
    """Complete CCO with PDK passives, clamp, VTEST injection, enable and level shifters (the drawn circuit).
    Ports: VDDA VDDD VDDL VSS vring ibias vtest code0..code4 pll_en vtest_en."""
    c = LS + ".subckt sspll_cco_dac vgr ibias en c0 c1 c2 c3 c4 VSS\n"
    c += "* IBIAS 5 uA -> 2-unit diode; unit sinks 2.5 uA: NBASE always-on units (switch = en) + binary 1..16\n"
    c += _m("nb", "ibias", "ibias", "VSS", "VSS", p["UN"], m=2)
    for k, (n, g) in enumerate(zip([p["NBASE"]] + [2**i for i in range(5)], ["en", "c0", "c1", "c2", "c3", "c4"])):
        c += _m(f"u{k}", f"d{k}", "ibias", "VSS", "VSS", p["UN"], m=n)
        c += _m(f"s{k}", "vgr", g, f"d{k}", "VSS", p["SW"], m=n)
    c += ".ends\n"
    c += ".subckt sspll_cco VDDA VDDD VDDL VSS vring ibias vtest code0 code1 code2 code3 code4 pll_en vtest_en\n"
    for k in range(5):
        c += f"xls{k} code{k} c{k} c{k}b VDDD VDDA VSS sspll_ls_1v8_3v3\n"
    c += "xlsen pll_en en enb VDDD VDDA VSS sspll_ls_1v8_3v3\nxlsvt vtest_en vt vtb VDDD VDDA VSS sspll_ls_1v8_3v3\n"
    c += "xdac vgr ibias en c0 c1 c2 c3 c4 VSS sspll_cco_dac\n"
    c += _m("mref", "vgr", "vgr", "VDDA", "VDDA", p["UP"])
    c += _m("mout", "vring", "vgo", "VDDA", "VDDA", p["UP"], m=p["NOUT"])
    model, nseg, L = p["RSEG"]
    nodes = ["vgr"] + [f"rf{i}" for i in range(1, nseg)] + ["vgo"]
    for i in range(nseg):
        c += f"xrf{i} {nodes[i]} {nodes[i+1]} VSS sky130_fd_pr__{model} l={L} mult=1 m=1\n"
    cm, nt, s = p["CTILE"]
    c += f"xcf vgo VDDA sky130_fd_pr__{cm} w={s} l={s} m={nt}\n"
    c += _m("pen", "vgo", "en", "VDDA", "VDDA", p["PEN"]) + _m("nen", "ibias", "enb", "VSS", "VSS", p["NEN"])
    # clamp: replica diode from VDDL carrying one DAC unit, clamp device K_CL units from vring to VSS
    c += _m("urep", "vcl", "ibias", "VSS", "VSS", p["UN"])
    c += _m("prep", "vcl", "vcl", "VDDL", "VDDL", p["PCL"])
    c += _m("psen", "vsn", "vcl", "vring", "vring", p["PCL"])
    rm, _, rl = p["RS"]
    c += f"xrs vsn VSS VSS sky130_fd_pr__{rm} l={rl} mult=1 m=1\n"
    if p["K_CL"]:
        c += _m("nsh", "vring", "vsn", "VSS", "VSS", p["NSH"])
    # VTEST injection
    c += _m("tgn", "vtest", "vt", "vinj", "VSS", p["TGN"]) + _m("tgp", "vtest", "vtb", "vinj", "VDDA", p["TGP"])
    rm, _, rl = p["RINJ"]
    c += f"xrinj vinj vring VSS sky130_fd_pr__{rm} l={rl} mult=1 m=1\n"
    return c + ".ends\n"
