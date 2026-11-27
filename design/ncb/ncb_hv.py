#!/usr/bin/env python3
"""ncb_hv.py - noise-cancellation block (NCB): a voltage-controlled delay line on VDDA, 5 V devices, driven by the
ring's clock and steered by vff from the diff-to-SE amplifier.

  line:   in ── X0 (input inverter) ── n0 ── X1 (starved) ── a ── X2 (starved) ── b ── X3 (output) ── out
                                                  │                 │
                                         cap bank on a      cap bank on b      (4-bit, binary, transmission gates)
  X1 / X2: inverters with a pMOS starver (gate pd) in the source of the pMOS and an nMOS starver (gate nb) in the
  source of the nMOS, so both edges of a and b are current-limited and the duty cycle is kept.

  bias:  vff ── MI (nMOS, KI units of the D2S level diode, 2/1 um) ── pd: pMOS diode ── copy ── nb: nMOS diode
  At rest vff = V_GS of the D2S's 2/1 um diode at 20 uA, so MI carries KI x 20 uA at every corner (replica bias), and
  the starvers a fixed multiple of that. A higher vff -> more starving current -> shorter delay:
      t_d = C_node dV / I_s,    K_d = -dt/dvff = t_d (g_m,MI / I_MI)
  The cap bank scales C_node and with it K_d: the 4-bit code is the FFNC gain calibration.

  cap bank: bit k = a transmission gate (nMOS gate c_k, pMOS gate c_kb) in series with 2^k unit nMOS gate capacitors.
  c_k = VDDA (code bit 1) closes the gate and adds the capacitors to the node. The code comes from 1.8 V control through
  level shifters (sspll_ncb_hv_top: g_k -> c_k, c_kb).
Every device is (model, W per finger, nf, L)."""
import os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "clkgen")); sys.path.insert(0, os.path.join(ROOT, "design", "sspd"))
sys.path.insert(0, os.path.join(ROOT, "design", "d2s"))
import clkgen_hv as K
from clkgen_hv import _m, LIB
from d2s_hv import run
N5, P5 = "nfet_g5v0d10v5", "pfet_g5v0d10v5"

D = dict(
    X0=((N5, 1.0, 1, 0.5), (P5, 2.5, 1, 0.5)),   # input inverter (load on clkp)
    XS=((N5, 3.0, 1, 0.5), (P5, 8.0, 1, 0.5)),   # starved inverter: switching nMOS / pMOS
    X3=((N5, 2.0, 1, 0.5), (P5, 5.0, 1, 0.5)),   # output inverter
    MS=(N5, 2.0, 1, 0.5), MSN=20,                # nMOS starver: MSN units of the MND unit
    MSP=(P5, 4.0, 1, 0.5), MSPN=30,              # pMOS starver: MSPN units of the pMOS mirror unit
    MND=(N5, 2.0, 1, 0.5),                       # nMOS diode unit (nb)
    MI=(N5, 2.0, 1, 1.0), KI=1,                  # input device: KI units of the D2S level diode (2/1 um)
    RI=("res_xhigh_po_0p69", 0.69, 6.76), NRI=0, # optional source degeneration of MI (units of 20 kOhm)
    MPM=(P5, 4.0, 1, 0.5),                       # pMOS mirror (diode + copy)
    CU=(N5, 1.0, 1, 0.5),                        # unit capacitor of the bank (nMOS gate cap to VSSA); bit k = 2^k units
    SW=(N5, 0.5, 1, 0.5), SWP=(P5, 0.5, 1, 0.5), # unit series switch: transmission gate (ck = VDDA, ckb = 0 V: on)
    NB=4,
    INV=False,                                   # four inverters: out in phase with in
)


def cells(p=D):
    xs = p["XS"]
    c = (".subckt sspll_ncb_hv_bank n c0 c1 c2 c3 c0b c1b c2b c3b VDDA VSSA\n* 4-bit switched capacitor bank: bit k = transmission "
         "gate (ck / ckb) in series with an nMOS gate capacitor, both 2^k units\n")
    for k in range(p["NB"]):
        c += (_m(f"sn{k}", "n", f"c{k}", f"x{k}", "VSSA", p["SW"], m=2**k) + _m(f"sp{k}", "n", f"c{k}b", f"x{k}", "VDDA", p["SWP"], m=2**k) +
              _m(f"c{k}", "VSSA", f"x{k}", "VSSA", "VSSA", p["CU"], m=2**k))
    c += ".ends\n"
    c += (".subckt sspll_ncb_hv_sinv i o nb pd VDDA VSSA\n* current-starved inverter: rising edge limited by the pMOS "
          "starver (gate pd), falling edge by the nMOS starver (gate nb)\n" +
          _m("sp", "q", "pd", "VDDA", "VDDA", p["MSP"], m=p["MSPN"]) + _m("p", "o", "i", "q", "VDDA", xs[1]) +
          _m("n", "o", "i", "s", "VSSA", xs[0]) + _m("s", "s", "nb", "VSSA", "VSSA", p["MS"], m=p["MSN"]) + ".ends\n")
    c += (".subckt sspll_ncb_hv_line in out nb pd c0 c1 c2 c3 c0b c1b c2b c3b VDDA VSSA\n* delay line: input inverter, one current-starved "
          "inverter with the cap bank on its output, output inverter\n" +
          K.inv5("x0", "in", "n0", p["X0"]) +
          "x1 n0 a nb pd VDDA VSSA sspll_ncb_hv_sinv\nxba a c0 c1 c2 c3 c0b c1b c2b c3b VDDA VSSA sspll_ncb_hv_bank\n"
          "x2 a b nb pd VDDA VSSA sspll_ncb_hv_sinv\nxbb b c0 c1 c2 c3 c0b c1b c2b c3b VDDA VSSA sspll_ncb_hv_bank\n" +
          K.inv5("x3", "b", "out", p["X3"]) + ".ends\n")
    c += (".subckt sspll_ncb_hv_bias vff nb pd VDDA VSSA\n* vff -> MI (replica of the D2S level diode) -> pMOS mirror -> nMOS diode nb\n" +
          (_m("i", "pd", "vff", "si", "VSSA", p["MI"], m=p["KI"]) +
           "".join(f"xri{k} {'si' if k == 0 else f'si{k}'} {f'si{k+1}' if k < p['NRI'] - 1 else 'VSSA'} VSSA "
                   f"sky130_fd_pr__{p['RI'][0]} l={p['RI'][2]} mult=1 m=1\n" for k in range(p["NRI"]))
           if p["NRI"] else _m("i", "pd", "vff", "VSSA", "VSSA", p["MI"], m=p["KI"])) +
          _m("pd", "pd", "pd", "VDDA", "VDDA", p["MPM"]) + _m("po", "nb", "pd", "VDDA", "VDDA", p["MPM"]) +
          _m("nd", "nb", "nb", "VSSA", "VSSA", p["MND"]) + ".ends\n")
    c += (".subckt sspll_ncb_hv in out vff c0 c1 c2 c3 c0b c1b c2b c3b VDDA VSSA\n* NCB core: bias + one delay line (code line c_k at "
          "VDDA = bit k capacitors in)\n"
          "xb vff nb pd VDDA VSSA sspll_ncb_hv_bias\n"
          "xl in out nb pd c0 c1 c2 c3 c0b c1b c2b c3b VDDA VSSA sspll_ncb_hv_line\n.ends\n")
    return re.sub(r"\bVSS\b", "VSSA", c)


def full(p=D):
    """Drawn cell: core + four level shifters for the gain code (1.8 V). Ports: inp inm outp outm vff g0 g1 g2 g3
    VDDA VDDD VSSA VSSD. g_k = 1 closes the bit-k transmission gates (2^k unit capacitors on the starved node)."""
    c = K.CC.LS + cells(p)
    c += ".subckt sspll_ncb_hv_top in out vff g0 g1 g2 g3 VDDA VDDD VSSA VSSD\n"
    for k in range(p["NB"]):
        c += f"xls{k} g{k} c{k} c{k}b VDDD VDDA VSSA VSSD sspll_ls_1v8_3v3\n"
    c += "xa in out vff c0 c1 c2 c3 c0b c1b c2b c3b VDDA VSSA sspll_ncb_hv\n.ends\n"
    return c


def lvs_reference(p=D):
    return full(p)


VCODRV = ((N5, 1.2, 1, 0.5), (P5, 3.0, 1, 0.5))       # the ring's buffer output stage (VCO design)


def bench(p=D, corner="tt", temp=27, vdda=3.3, vff=1.53, code=8, f=800e6, ncyc=10, cl=20e-15, extra="", save="",
          vff_src=None, tstep=1e-12):
    """Two 0..VDDA squares at f behind the ring's buffer stage drive inp / inm (plus 10 fF of other loads: SSPD, FLL);
    vff a DC source; code by ideal code-line voltages; C_L on each output."""
    T = 1/f; tr = 60e-12
    src = (f"vvp vp 0 pulse(0 {vdda} 0 {tr} {tr} {T/2 - tr} {T})\nvvm vm 0 pulse({vdda} 0 0 {tr} {tr} {T/2 - tr} {T})\n")
    drv = re.sub(r"\bVSSA?\b", "0", K.inv5("xdp", "vp", "inp", VCODRV, "VDRV") + K.inv5("xdm", "vm", "inm", VCODRV, "VDRV"))
    cl_ = "".join(f"vc{k} c{k} 0 {vdda if (code >> k) & 1 else 0}\nvcb{k} c{k}b 0 {0 if (code >> k) & 1 else vdda}\n"
                  for k in range(p["NB"]))
    vs = vff_src or f"vvf vff 0 {vff}\n"
    return (f"* ncb\n.lib {LIB} {corner}\n.temp {temp}\n{cells(p)}vdda VDDA 0 {vdda}\nvdrv VDRV 0 {vdda}\n{src}{drv}"
            f"cip inp 0 10f\ncim inm 0 10f\n{vs}{cl_}xn inp outp vff c0 c1 c2 c3 c0b c1b c2b c3b VDDA 0 sspll_ncb_hv\n"
            f"clp outp 0 {cl}\n{extra}"
            f".control\noption interp\nsave v(inp) v(outp) vdda#branch {save}\ntran {tstep} {ncyc*T}\n"
            f"wrdata w.txt v(inp) v(outp) i(vdda) {save}\n.endc\n.end\n")


def delays(p=D, corner="tt", temp=27, vdda=3.3, vff=1.53, code=8, f=800e6, ncyc=10, **kw):
    """Delay of each edge (in -> out at VDDA/2, last 4 periods), mean delay, rise / fall edge difference, power."""
    net = bench(p, corner, temp, vdda, vff, code, f, ncyc, **kw)
    out, d = run(net, ["w.txt"])
    z = d["w.txt"]; t = z[:, 0]; g = lambda i: z[:, 2*i + 1]
    ip, op, ida = g(0), g(1), g(2)
    T = 1/f; m = vdda/2; t0 = (ncyc - 4)*T
    res = {}
    for nm, a, b in (("p", ip, op),):
        for rising in (True, False):
            ti = K.xings(t, a, m, rising); to = K.xings(t, b, m, rising != p.get("INV", True))
            ti = ti[ti > t0]
            dd = [to[to > x][0] - x for x in ti if len(to[to > x])]
            res[nm + ("r" if rising else "f")] = float(np.mean(dd))
    w = t > t0
    P = -vdda*np.trapezoid(ida[w], t[w])/(t[w][-1] - t[w][0])
    td = np.mean(list(res.values()))
    return dict(td=float(td), edges=res, duty_err=float(res["pr"] - res["pf"]), P=float(P))


def kd(p=D, corner="tt", temp=27, vdda=3.3, vff=1.53, code=8, dv=0.02, **kw):
    """K_d = -d t_d / d vff by a central difference of +-dv (two runs)."""
    a = delays(p, corner, temp, vdda, vff - dv, code, **kw); b = delays(p, corner, temp, vdda, vff + dv, code, **kw)
    return dict(Kd=float((a["td"] - b["td"])/(2*dv)), td=(a["td"] + b["td"])/2, P=(a["P"] + b["P"])/2,
                duty=(a["duty_err"] + b["duty_err"])/2)


def ac_ctrl(p=D, corner="tt", temp=27, vdda=3.3, vff=1.53, code=8):
    """Control path, small signal at the operating point with the line idle (in = 0): vff -> nb and -> pd (|H| and
    f_3dB relative to 100 kHz), and the capacitance vff presents (Im(I)/2 pi f at 1 MHz)."""
    cl_ = "".join(f"vc{k} c{k} 0 {vdda if (code >> k) & 1 else 0}\nvcb{k} c{k}b 0 {0 if (code >> k) & 1 else vdda}\n"
                  for k in range(p["NB"]))
    net = (f"* ncb ac\n.lib {LIB} {corner}\n.temp {temp}\n{cells(p)}vdda VDDA 0 {vdda}\nvin in 0 0\n{cl_}"
           f"vvf vff 0 dc {vff} ac 1\nxn in out vff c0 c1 c2 c3 c0b c1b c2b c3b VDDA 0 sspll_ncb_hv\n"
           ".control\nac dec 20 1e5 1e10\nlet a1 = abs(v(xn.nb))\nlet a2 = abs(v(xn.pd))\nlet ci = imag(i(vvf))\n"
           "wrdata a.txt a1 a2 ci\n.endc\n.end\n")
    _, d = run(net, ["a.txt"])
    z = d["a.txt"]; f = z[:, 0]; h1, h2, ci = z[:, 1], z[:, 3], z[:, 5]
    f3 = lambda h: float(f[np.where(h < h[0]/np.sqrt(2))[0][0]]) if (h < h[0]/np.sqrt(2)).any() else float("nan")
    return dict(f3_nb=f3(h1), f3_pd=f3(h2), cin=float(abs(np.interp(1e6, f, ci))/(2*np.pi*1e6)), f=f, h_nb=h1, h_pd=h2)


def ks(p=D, corner="tt", temp=27, vdda=3.3, vff=1.53, code=8, dv=0.1):
    """Delay sensitivity to VDDA with vff fixed (it is referred to VSSA by the D2S)."""
    a = delays(p, corner, temp, vdda - dv, vff, code); b = delays(p, corner, temp, vdda + dv, vff, code)
    return float((b["td"] - a["td"])/(2*dv))


if __name__ == "__main__":
    for code in (0, 8, 15):
        r = kd(code=code)
        print(f"code {code:2d}: t_d {r['td']*1e12:.1f} ps, K_d {r['Kd']*1e12:.1f} ps/V, duty err {r['duty']*1e12:.2f} ps, P {r['P']*1e3:.3f} mW")
