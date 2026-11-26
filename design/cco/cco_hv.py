"""cco_hv.py - roadmap step 75 redone for the device-rule migration: current-controlled supply (CCO) of the 3-stage
5 V ring VCO (step 74 HV), all devices 5 V-rated (g5v0d10v5) on VDDA = 3.3 V, control bits from 1.8 V logic.

                VDDA ──┬────────────────┬─────────────────────── (C_F = MIM tiles between VDDA and vgo, over the array)
                  MREF (1 unit, diode)  │            MOUT (NOUT units)
                       vgr ──[ R_F ]── vgo ────────────┘    │
                       │                                   ring node (vring, step 74 HV ring) <── VTEST injection
          DAC: unit sinks I_u = IBIAS/2 (x NBASE always on + 1,2,4,8,16 switched by cco_code)
          IBIAS 5 uA -> 2-unit nMOS diode sets the unit current

I_out = NOUT x I_u x (NBASE + code).  Differences from the 1.6 GHz CCO (cco.py, kept for the record):
  * ring range 0.70 mA (ff/-40 C, 720 MHz) .. 1.46 mA (ss/110 C, 880 MHz) instead of 0.89 .. 1.93 mA -> NOUT 25 -> 17,
    NBASE 11 -> 13 (LSB 42.5 uA instead of 62.5 uA);
  * no clamp: the ring is now built from 5 V devices, its node may go up to VDDA (and the 1.8 V rail is gone);
  * headroom: the ring node reaches 2.37 V at ss/110 C (was 1.65 V), so MOUT has 0.60 V at VDDA = 2.97 V;
  * VDDA rejection matters more without the LDO: K_vdd = K_I x dI/dVDDA <= 5 MHz/V (step 72 HV). A plain mirror gives
    66-110 MHz/V (MOUT's g_ds at the held ring node); a cascode whose gate follows VDDA, an RC-filtered cascode bias and
    R_F's body on VDDA bring it to about 5 MHz/V.
Every device is (model, W per finger, nf, L): the netlist is the layout."""
import os, re, subprocess, tempfile
import numpy as np
import cco as c18                     # helpers of the 1.6 GHz CCO: device line, ngspice runner, level shifter
PDK_ROOT = c18.PDK_ROOT; LIB = c18.LIB; HERE = c18.HERE
_m = c18._m; run = c18.run

# Ground split (24 Nov 2026): two grounds, VSSA for the VDDA domain and VSSD for the VDDD domain. The level shifter is
# the one cell that sits in both: its thin-oxide input inverter runs on VDDD / VSSD, every 5 V device (pull-downs,
# cross-coupled loads, output inverters) on VDDA / VSSA. Same devices and sizes as the step-75 cell (cco.LS); only the
# ground of the input inverter is now its own pin.
LS = """.subckt sspll_ls_1v8_3v3 in out outb VDDD VDDA VSSA VSSD
* 1.8 V -> 3.3 V level shifter: thin-oxide input inverter on VDDD / VSSD, thick-oxide cross-coupled pMOS load,
* thick-oxide pull-downs driven by in / inb, thick-oxide output inverters (out follows in, outb is its inverse), on VDDA / VSSA
xpi inb in VDDD VDDD sky130_fd_pr__pfet_01v8 w=1 l=0.15 nf=1 m=1
xni inb in VSSD VSSD sky130_fd_pr__nfet_01v8 w=0.5 l=0.15 nf=1 m=1
xp1 x y VDDA VDDA sky130_fd_pr__pfet_g5v0d10v5 w=1 l=0.5 nf=1 m=1
xp2 y x VDDA VDDA sky130_fd_pr__pfet_g5v0d10v5 w=1 l=0.5 nf=1 m=1
xn1 x in VSSA VSSA sky130_fd_pr__nfet_g5v0d10v5 w=3 l=0.5 nf=1 m=1
xn2 y inb VSSA VSSA sky130_fd_pr__nfet_g5v0d10v5 w=3 l=0.5 nf=1 m=1
xpo out x VDDA VDDA sky130_fd_pr__pfet_g5v0d10v5 w=2 l=0.5 nf=1 m=1
xno out x VSSA VSSA sky130_fd_pr__nfet_g5v0d10v5 w=1 l=0.5 nf=1 m=1
xpb outb y VDDA VDDA sky130_fd_pr__pfet_g5v0d10v5 w=2 l=0.5 nf=1 m=1
xnb outb y VSSA VSSA sky130_fd_pr__nfet_g5v0d10v5 w=1 l=0.5 nf=1 m=1
.ends
"""

D = dict(
    UP=("pfet_g5v0d10v5", 20.0, 2, 2.0),     # mirror unit pMOS (sized in cco_hv_explore.py)
    UN=("nfet_g5v0d10v5", 1.0, 1, 4.0),      # DAC / bias unit nMOS (2.5 uA)
    SW=("nfet_g5v0d10v5", 1.0, 1, 0.5),      # DAC unit switch
    NOUT=17, NBASE=14, R_F=10e6, C_F=10.92e-12,
    RSEG=("res_xhigh_po_0p35", 20, 87.48), CTILE=("cap_mim_m3_1", 6, 30.0),
    TGN=("nfet_g5v0d10v5", 2.0, 1, 0.5), TGP=("pfet_g5v0d10v5", 2.0, 1, 0.5), RINJ=("res_xhigh_po_0p35", 1, 3.39),
    PEN=("pfet_g5v0d10v5", 2.0, 1, 0.5), NEN=("nfet_g5v0d10v5", 2.0, 1, 0.5),
    # cascode (cco_hv_casc.py, cco_hv_headroom.py): MC 80 um per output unit, gate vcas = VDDA - V_SG(MB) carried by
    # KB DAC units, RC-filtered; C_F 6 tiles and CCAS 4 tiles keep both gates on VDDA at high frequency
    CASC=("pfet_g5v0d10v5", 20.0, 4, 0.5), MB=("pfet_g5v0d10v5", 4.0, 1, 4.0), KB=4,
    RCAS=("res_xhigh_po_0p35", 8, 87.48), CCAS=("cap_mim_m3_1", 4, 30.0))


def _cascode(p, vdda, vss, vring, ibias, en=None):
    """Output stage. Without CASC: MOUT drives the ring node directly. With CASC: MOUT -> cascode MC -> ring node;
    MC's gate (vcas) comes from a diode-connected pMOS MB from VDDA carrying KB DAC units, so vcas follows VDDA, and a
    MIM (CCAS) from vcas to VDDA holds it there at high frequency. Then MOUT's drain moves with VDDA like its gate
    and source: no current change through MOUT's C_gd or g_ds."""
    if not p.get("CASC"):
        return _m("mout", vring, "vgo", vdda, vdda, p["UP"], m=p["NOUT"])
    c = _m("mout", "vc", "vgo", vdda, vdda, p["UP"], m=p["NOUT"])
    c += _m("mc", vring, "vcas", "vc", vdda, p["CASC"], m=p["NOUT"])
    c += _m("mb", "vcb", "vcb", vdda, vdda, p["MB"])
    sw = f"{en}" if en else "vdda"
    c += _m("ub", "db", ibias, vss, vss, p["UN"], m=p["KB"]) + _m("sb", "vcb", sw, "db", vss, p["SW"], m=p["KB"])
    # RC low-pass vcb -> vcas: the bias branch is a plain mirror of IBIAS (not behind R_F / C_F), so without it the
    # IBIAS input diode's noise reaches the cascode gate and, through MOUT's g_ds, the output (12 pA/rtHz at 1 MHz)
    rm, nseg, rl = p["RCAS"]
    nodes = ["vcb"] + [f"rc{i}" for i in range(1, nseg)] + ["vcas"]
    for i in range(nseg):
        c += f"xrc{i} {nodes[i]} {nodes[i+1]} {vdda} sky130_fd_pr__{rm} l={rl} mult=1 m=1\n"
    cm, nt, sz = p["CCAS"]
    c += f"xccas vcas {vdda} sky130_fd_pr__{cm} w={sz} l={sz} m={nt}\n"
    return c


def core(p, code, ideal_rc=True):
    """CCO core subckt: ports vdda vss vring ibias; code switches as ideal 3.3 V gate levels."""
    c = ".subckt cco vdda vss vring ibias\n"
    c += _m("mref", "vgr", "vgr", "vdda", "vdda", p["UP"])
    c += _cascode(p, "vdda", "vss", "vring", "ibias")
    if ideal_rc:
        c += f"rf vgr vgo {p['R_F']}\ncf vgo vdda {p['C_F']}\n"
    c += _m("nb", "ibias", "ibias", "vss", "vss", p["UN"], m=2)
    bits = [p["NBASE"]] + [2**k for k in range(5)]
    on = [True] + [bool(code >> k & 1) for k in range(5)]
    for k, (n, e) in enumerate(zip(bits, on)):
        c += _m(f"u{k}", f"d{k}", "ibias", "vss", "vss", p["UN"], m=n)
        c += _m(f"s{k}", "vgr", f"en{k}", f"d{k}", "vss", p["SW"], m=n)
        c += f"ven{k} en{k} 0 {3.3 if e else 0}\n"
    return c + ".ends\n"


def full(p):
    """The drawn circuit: DAC, mirror, PDK R_F and C_F, enable, VTEST injection, level shifters.
    Ports: VDDA VDDD VSSA VSSD vring ibias vtest code0..code4 pll_en vtest_en."""
    c = LS + ".subckt sspll_cco_hv_dac vgr ibias en c0 c1 c2 c3 c4 VSSA\n"
    c += _m("nb", "ibias", "ibias", "VSSA", "VSSA", p["UN"], m=2)
    for k, (n, g) in enumerate(zip([p["NBASE"]] + [2**i for i in range(5)], ["en", "c0", "c1", "c2", "c3", "c4"])):
        c += _m(f"u{k}", f"d{k}", "ibias", "VSSA", "VSSA", p["UN"], m=n)
        c += _m(f"s{k}", "vgr", g, f"d{k}", "VSSA", p["SW"], m=n)
    c += ".ends\n"
    c += ".subckt sspll_cco_hv VDDA VDDD VSSA VSSD vring ibias vtest code0 code1 code2 code3 code4 pll_en vtest_en\n"
    for k in range(5):
        c += f"xls{k} code{k} c{k} c{k}b VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\n"
    c += "xlsen pll_en en enb VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\nxlsvt vtest_en vt vtb VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\n"
    c += "xdac vgr ibias en c0 c1 c2 c3 c4 VSSA sspll_cco_hv_dac\n"
    c += _m("mref", "vgr", "vgr", "VDDA", "VDDA", p["UP"])
    c += _cascode(p, "VDDA", "VSSA", "vring", "ibias", en="en")
    # R_F: body terminal on VDDA (the serpentine is drawn over an n-well tied to VDDA). With the body on VSS, the
    # poly-to-substrate capacitance (~60 fF) pulls the gate node towards VSSA at high frequency, so the gate stops
    # following VDDA and VDDA ripple becomes current ripple (step 75 HV: 34 -> see cco_hv_casc.py).
    model, nseg, L = p["RSEG"]
    nodes = ["vgr"] + [f"rf{i}" for i in range(1, nseg)] + ["vgo"]
    for i in range(nseg):
        c += f"xrf{i} {nodes[i]} {nodes[i+1]} VDDA sky130_fd_pr__{model} l={L} mult=1 m=1\n"
    cm, nt, s = p["CTILE"]
    c += f"xcf vgo VDDA sky130_fd_pr__{cm} w={s} l={s} m={nt}\n"
    c += _m("pen", "vgo", "en", "VDDA", "VDDA", p["PEN"]) + _m("nen", "ibias", "enb", "VSSA", "VSSA", p["NEN"])
    c += _m("tgn", "vtest", "vt", "vinj", "VSSA", p["TGN"]) + _m("tgp", "vtest", "vtb", "vinj", "VDDA", p["TGP"])
    rm, _, rl = p["RINJ"]
    c += f"xrinj vinj vring VSSA sky130_fd_pr__{rm} l={rl} mult=1 m=1\n"
    return c + ".ends\n"


def tb(p, c, t, vdda=3.3, ib=5e-6, code=10, vring="vr vring 0 1.89", en=1.8, vddd=1.8, ctl="", extra="", vdda_ac=False):
    """Testbench around the drawn circuit: ideal supplies, IBIAS source, ring node held by a voltage source vr
    (its current is the CCO output), code bits from ideal 1.8 V sources."""
    bits = "".join(f"vc{k} code{k} 0 {vddd if code >> k & 1 else 0}\n" for k in range(5))
    vd = f"vdda VDDA 0 dc {vdda} ac 1\n" if vdda_ac else f"vdda VDDA 0 {vdda}\n"
    return (f"* step75 HV tb\n.lib {LIB} {c}\n.temp {t}\n{full(p)}{vd}vddd VDDD 0 {vddd}\niib 0 ibias {ib}\n"
            f"{vring}\nvt vtest 0 1.89\nven pll_en 0 {en}\nvvt vtest_en 0 0\n{bits}{extra}"
            f"x1 VDDA VDDD 0 0 vring ibias vtest code0 code1 code2 code3 code4 pll_en vtest_en sspll_cco_hv\n"
            f".control\n{ctl}\n.endc\n.end\n")


def op_current(p, c, t, vdda=3.3, ib=5e-6, code=10, vr=1.89):
    out = run(tb(p, c, t, vdda, ib, code, vring=f"vr vring 0 {vr}", ctl="op\nprint -vr#branch"))
    m = re.search(r"vr#branch = (\S+)", out)
    return float(m.group(1)) if m else None


def psr(p, c="tt", t=27, code=10, vr=1.89, ib=5e-6):
    """|dI_out/dVDDA| (A/V) vs frequency with the ring node held at vr (AC 1 V on VDDA)."""
    o = run(tb(p, c, t, ib=ib, code=code, vring=f"vr vring 0 {vr}", vdda_ac=True,
               ctl="ac dec 5 1e2 1e8\nprint abs(vr#branch)"))
    return [(float(f), float(v)) for f, v in re.findall(r"^\d+\s+(\S+)\s+(\S+)", o, re.M)]


def noise(p, c="tt", t=27, code=10, vr=1.89, ib=5e-6):
    """Output current noise (A/rtHz) of the drawn circuit into the held ring node (.noise through a CCVS)."""
    net = tb(p, c, t, ib=ib, code=code, vring=f"vr vr2 0 {vr}\nvm vring vr2 0\nh1 o 0 vm 1",
             ctl="option sparse\nnoise v(o) iib dec 10 1e3 1e8\nsetplot noise1\nwrdata noise.txt onoise_spectrum")
    net = net.replace(f"iib 0 ibias {ib}", f"iib 0 ibias dc {ib} ac 1")
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, ".spiceinit"), "w").write(open(f"{PDK_ROOT}/sky130A/libs.tech/ngspice/spinit").read())
        open(os.path.join(d, "r.sp"), "w").write(net)
        subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d, timeout=3000)
        z = np.loadtxt(os.path.join(d, "noise.txt"))
    return z[:, 0], z[:, 1]
