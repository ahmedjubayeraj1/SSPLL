"""lf_hv.py - roadmap step 80: the main-loop filter, every device 5 V-rated or passive, ground VSSA.

        vctl ──┬──────────────── R1 ──────────────── vz ──┬──────────┐
               │   (3 res_xhigh_po_2p85 segments in        │          │
              C2    series, folded, a dummy strip on      C1 tile 1  C1 tile 2
               │    each side)                             │          │
        VSSA ──┴───────────────────────────────────────────┴──────────┘

   C1 tile = 9 nfet_g5v0d10v5 MOS capacitors (W = L = 10 um; gate = vz, drain / source / body = VSSA) under one
             cap_mim_m3_1 30 x 30 um (capm top plate = vz, met3 bottom plate = VSSA): about 4.4 pF in 35 x 35 um.
   C2      = 2 cap_mim_m3_1 (top plate = vctl, bottom plate = VSSA).

What happens: once per reference period the pulsed Gm (step 79) pushes a charge packet q = beta T phi_e into vctl.
C2 takes it first (fast step of vctl: proportional path through the zero), then it shares into C1 through R1 with time
constant R1 C1 C2 / (C1 + C2) (pole); C1 keeps the integral (type-2 integrator). The VCO (step 74) reads vctl.
  Z(s) = (1 + s R1 C1) / (s (C1 + C2) (1 + s R1 C1 C2 / (C1 + C2)))
  zero f_z = 1 / (2 pi R1 C1),  pole f_p = (C1 + C2) / (2 pi R1 C1 C2)
Every device is (model, W, nf or count, L)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "clkgen"))
from clkgen_hv import _m, LIB, run
N5 = "nfet_g5v0d10v5"

D = dict(
    R1=("res_xhigh_po_2p85", 2.85, 3, 9.30),   # model, W (fixed by the model), segments in series, L per segment (um)
    RDUM=2,                                     # dummy segments (same L), both ends on VSSA, one on each side of R1
    MC=(N5, 10.0, 1, 10.0),                     # MOS capacitor unit, W = L = 10 um
    NMC=9,                                      # MOS units per C1 tile (3 x 3 under the MIM)
    MIM1=("cap_mim_m3_1", 30.0, 30.0),          # C1 tile top plate, w x l (um)
    NT=2,                                       # C1 tiles
    C2=("cap_mim_m3_1", 30.0, 9.30, 2),         # C2: model, w, l, count
)


def cells(p=D):
    rm, rw, ns, rl = p["R1"]
    c = (f".subckt sspll_lf_hv_r1 a b VSSA\n"
         f"* R1: {ns} x {rm} L = {rl} um in series (folded), {p['RDUM']} dummy segments on VSSA\n")
    nodes = ["a"] + [f"m{i}" for i in range(1, ns)] + ["b"]
    for i in range(ns):
        c += f"xr{i} {nodes[i]} {nodes[i+1]} VSSA sky130_fd_pr__{rm} l={rl} mult=1 m=1\n"
    for i in range(p["RDUM"]):
        c += f"xrd{i} VSSA VSSA VSSA sky130_fd_pr__{rm} l={rl} mult=1 m=1\n"
    c += ".ends\n"
    cm, cw, cl = p["MIM1"]
    c += (".subckt sspll_lf_hv_c1tile top VSSA\n"
          f"* C1 tile: {p['NMC']} MOS capacitors (gate = top) under one {cm} {cw} x {cl} um (capm = top, met3 = VSSA)\n" +
          _m("c", "VSSA", "top", "VSSA", "VSSA", p["MC"], m=p["NMC"]) +
          f"xm top VSSA sky130_fd_pr__{cm} w={cw} l={cl} m=1\n.ends\n")
    m2, w2, l2, n2 = p["C2"]
    c += (".subckt sspll_lf_hv vctl VSSA\n"
          "* type-2 loop filter: C2 on vctl, R1 from vctl to vz, C1 tiles on vz; ground VSSA\n"
          "xr1 vctl vz VSSA sspll_lf_hv_r1\n" +
          "".join(f"xc1_{k} vz VSSA sspll_lf_hv_c1tile\n" for k in range(p["NT"])) +
          f"xc2 vctl VSSA sky130_fd_pr__{m2} w={w2} l={l2} m={n2}\n.ends\n")
    return c


def lvs_reference(p=D):
    return cells(p)


def ideal(p=D, cmos_fF=287.3, r_um=701.1, r_head=139.0, mim=lambda w, l: 2.0*w*l + 0.164*2*(w + l)):
    """Hand values (step 73 densities) of R1, C1, C2: R per segment = r_um L + r_head; C1 = NT (NMC C_mos + MIM)."""
    rm, rw, ns, rl = p["R1"]
    R = ns*(r_um*rl + r_head)
    C1 = p["NT"]*(p["NMC"]*cmos_fF + mim(*p["MIM1"][1:]))*1e-15
    C2 = p["C2"][3]*mim(p["C2"][1], p["C2"][2])*1e-15
    return R, C1, C2
