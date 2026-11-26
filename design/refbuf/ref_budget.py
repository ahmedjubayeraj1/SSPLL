"""ref_budget.py - put the simulated REF receiver phase noise into the step-72 jitter budget (method M9).

L_rx(f) = (2 pi f_ref)^2 / (2 s^2) * S_LF(f)  +  (2 pi f_ref sigma_w)^2 / f_ref
          quasi-static part (flicker, R_B)        white per-edge part (from the transient-noise run)
s = slope of the gate voltage at its crossing (pi f_ref V_pp x |C_AC divider| for a sine). In the PLL the reference noise is multiplied by
N^2 and low-passed by |H + G_c (1 - H)|^2. The ring (step 74) and the CCO (step 75) use their simulated spectra."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
for p in ("models", "learn", "design/budget", "design/cco"):
    sys.path.insert(0, os.path.join(ROOT, p))
import pllmodel as pm
import step72_budget as b
import importlib.util
_sp = importlib.util.spec_from_file_location("cco_budget", os.path.join(ROOT, "design", "cco", "budget_link.py"))
_cb = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_cb)
RING, KI_TT = _cb.RING, _cb.KI_TT

CLKGEN = (-163.4, 30e3)   # clock-generator sampling edge (step 77: 0.15 ps per edge, M17); flicker corner still assumed
SSPDBUF = (-169.0, 30e3)   # SSPD isolation buffers (step 78, M17: 0.113 ps per side -> 0.080 ps on the differential crossing)
b.CORNER["typ"]["Cs"] = 46e-15  # step 78: C1 node = 34.7 fF MIM + 6 fF Gm input + switch parasitics (kT/C, M9)
NAME = "REF receiver + clock generator edge"   # = the step-72 allocation key it replaces (SSPD buffers added here too)


def L_rx(f, fn, Sn, Sw, sigma_w, vpp, div, fref=b.FREF):
    """Receiver phase noise at the reference (dBc/Hz). fn, Sn: GATE-referred noise PSD (V^2/Hz, relative to the trip
    point); Sw: its white plateau; div: |v_gate/v_pad| at f_ref, so the gate slope is pi f_ref V_pp div;
    sigma_w: per-edge white jitter (s) at this amplitude from the transient-noise run."""
    s = np.pi*fref*vpp*div
    Slf = np.clip(np.exp(np.interp(np.log(f), np.log(fn), np.log(Sn))) - Sw, 0, None)
    L = (2*np.pi*fref)**2/(2*s**2)*Slf + (2*np.pi*fref*sigma_w)**2/fref
    return 10*np.log10(L)


def system(Lrx_f, Lrx, corner="typ"):
    """Total jitter (ps) and L(300 kHz) with this receiver, the step-74 ring and the step-75 CCO, FFNC off / on."""
    cco = json.load(open(os.path.join(ROOT, "design", "cco", "data", "step75_noise.json")))
    out = {}
    for on in (False, True):
        f, S = b.spectra(corner, on, over={"ring VCO core": RING})
        H = pm.loop_H(f, b.FC, b.PMDEG); Gc = pm.ffnc_Gc(f, b.FREF, b.CORNER[corner]["gerr"], on=on)
        T_in = np.abs(H + Gc*(1 - H))**2; T_vco = np.abs((1 - Gc)*(1 - H))**2
        si = np.exp(np.interp(np.log(f), np.log(cco["f"]), np.log(np.array(cco["n"])**2)))
        S["CCO current DAC + mirror"] = KI_TT**2*si/f**2*T_vco
        lrx = np.interp(np.log(f), np.log(Lrx_f), Lrx)
        clk = pm.floor_L(f, *CLKGEN); spb = pm.floor_L(f, *SSPDBUF)
        S[NAME] = 2*(10**(lrx/10) + 10**(clk/10) + 10**(spb/10))*b.N**2*T_in
        j, L = b.jitter(S, f, 1.6e9)
        out[on] = dict(rx_ps=float(j[NAME]*1e12), total_ps=float(j["TOTAL"]*1e12),
                       L300k=float(L[np.argmin(abs(f - 3e5))]))
    return out
