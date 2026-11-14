#!/usr/bin/env python3
"""step72_budget.py - roadmap step 72: phase-noise, jitter, power and area budget per block for the SSPLL + FFNC
of the submitted proposal (50 MHz x 32 = 1.6 GHz, f_c = 2.5 MHz, PM 50 deg).

The total reproduces the proposal's basis (pllmodel.TYP / PESS: 2.29 / 1.40 ps typ); here every lumped term of that
model is split into the blocks that will be designed, each with its own noise allocation, so every block gets a
number it must meet in Phase 7 and verify in Phase 8.  Run from the repo root:
    python3 design/budget/step72_budget.py      -> design/budget/budget.csv, docs/img/step72_*.png, printed tables
"""
import os, sys, csv
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "models")); sys.path.insert(0, os.path.join(ROOT, "learn"))
import pllmodel as pm
from sspll_learn import loop_design_type2

kT = 1.380649e-23*300
FREF, N = 50e6, 32
KV_HZ = 300e6                       # fine-tuning gain (assumed until the VCO is designed, step 74)
FC, PMDEG = 2.5e6, 50

# ---------------------------------------------------------------- per-block noise allocations (typ, pess)
ALLOC = {
 # name: dict(kind, typ, pess)  kind: 'ref' (x N^2, in-loop), 'pd' (in-loop, VCO-referred), 'vco' (high-passed,
 #        cancelled by FFNC), 'out' (after the NCB: added directly). Values are L in dBc/Hz with a 1/f corner.
 "XO (crystal oscillator, board)":      dict(kind="ref", typ=(-155, 30e3), pess=(-155, 100e3)),
 "REF receiver + clock generator edge": dict(kind="ref", typ=(-155, 30e3), pess=(-151, 100e3)),
 "SSPD sampler (kT/C)":                 dict(kind="pd"),
 "pulsed-Gm charge pump":               dict(kind="pd"),
 "loop-filter resistor R1":             dict(kind="lfr"),
 # ring: thermal level from the step-6 transient-noise sim of the 5 x 1.5 cell; the 1/f^3 corner is halved from the
 # simulated 1.1 MHz (longer ring nMOS, rise/fall symmetry - step 74 must show it); fallback: icp_trim -> f_c 2.8 MHz
 "ring VCO core":                       dict(kind="vco", typ=(-98.35, 0.60e6), pess=(-97.35, 1.2e6)),
 # CCO: thermal floor of a 1.31 mA source with ~1.2 V headroom (7 pA/rtHz); flicker corner 0.3 MHz from a
 # large-area thick-oxide output mirror with an RC-filtered gate (step 75)
 "CCO current DAC + mirror":            dict(kind="vco", typ=(-104.2, 0.30e6), pess=(-101.2, 0.6e6)),
 "NCB delay line (intrinsic)":          dict(kind="out", typ=(-150, 1e6), pess=(-146, 3e6)),
 "LDO noise through the NCB":           dict(kind="ldo", typ=40e-9, pess=80e-9),
}
CORNER = dict(typ=dict(A=0.5, gamma=1.0, gm=100e-6, duty=0.01, Cs=100e-15, gerr=0.10, Ks=4*26e-12),
              pess=dict(A=0.35, gamma=1.5, gm=100e-6, duty=0.01, Cs=100e-15, gerr=0.30, Ks=4*30e-12))


def loop(fref=FREF, n=N, fc=FC):
    p = CORNER["typ"]
    beta = 2*p["A"]*p["gm"]*p["duty"]                       # A per VCO rad (pulsed Gm, step 50)
    d = loop_design_type2(fc, PMDEG, 2*np.pi*n*beta, 2*np.pi*KV_HZ, n)
    return beta, d


def spectra(corner, ffnc, fref=FREF, n=N, f=None, alias=True, fc=None, over=None):
    """Output phase-noise PSD per block (rad^2/Hz). fc overrides the loop bandwidth; over = {block: value} replaces
    that block's allocation for this corner (e.g. {"ring VCO core": (-98.35, 0.6e6)})."""
    f = pm.freq_axis(n=3000) if f is None else f
    fc = FC if fc is None else fc
    over = over or {}
    c = CORNER[corner]; f0 = n*fref
    beta, d = loop(fref, n, fc)
    H = pm.loop_H(f, fc, PMDEG)
    Gc = pm.ffnc_Gc(f, fref, c["gerr"], on=ffnc)
    T_in = np.abs(H + Gc*(1-H))**2; T_vco = np.abs((1-Gc)*(1-H))**2
    lin = lambda L: 2*10**(L/10)
    scale = 10*np.log10(f0/1.6e9)                           # ring L ~ f0 (P ~ f0) for the 45/55 MHz points
    S = {}
    for name, a in ALLOC.items():
        k = a["kind"]
        if name in over:
            a = dict(a); a[corner] = over[name]
        if k == "ref":
            L, fc1 = a[corner]; S[name] = lin(pm.floor_L(f, L, fc1) + 20*np.log10(n))*T_in
        elif k == "pd" and "kT/C" in name:
            L = 10*np.log10(kT/(2*c["Cs"]*c["A"]**2*fref))  # differential sampler (step 49)
            S[name] = lin(np.full_like(f, L))*T_in
        elif k == "pd":
            L = 10*np.log10(kT*c["gamma"]/(c["A"]**2*c["gm"]*c["duty"])/2)   # gated Gm noise, beta = 2 A gm d
            S[name] = lin(pm.floor_L(f, L, 300e3))*T_in
        elif k == "lfr":
            s = 2j*np.pi*f
            Hr = d["C1"]/((d["C1"] + d["C2"]) + s*d["R"]*d["C1"]*d["C2"])
            Sphi = 4*kT*d["R"]*np.abs(Hr)**2*(2*np.pi*KV_HZ)**2/(2*np.pi*f)**2
            S[name] = Sphi*T_vco
        elif k == "vco":
            L1, fc3 = a[corner]; S[name] = lin(pm.vco_L(f, L1 + scale, fc3))*T_vco
        elif k == "out":
            L, fc1 = a[corner]; S[name] = lin(pm.floor_L(f, L, fc1)) if ffnc else 0*f
        elif k == "ldo":
            vn = a[corner]; Sv = vn**2*(1 + 10e3/f)          # LDO output noise with a 10 kHz 1/f corner
            S[name] = (2*np.pi*f0*c["Ks"])**2*Sv if ffnc else 0*f
    if ffnc and alias:                                       # Thijssen aliasing of VCO-like noise (step 70)
        vco_like = sum(S[k] / np.maximum(T_vco, 1e-30) for k in ALLOC if ALLOC[k]["kind"] in ("vco", "lfr"))
        fa = lambda x: np.interp(np.abs(x), f, vco_like*np.abs(1-H)**2, left=vco_like[0], right=0)
        S["aliasing of VCO noise (k = 1..3)"] = sum(fa(f - k*fref) + fa(f + k*fref) for k in (1, 2, 3))*np.abs(Gc)**2
    return f, S


def jitter(S, f, f0, band=(10e3, 40e6)):
    m = (f >= band[0]) & (f <= band[1])
    out = {k: np.sqrt(np.trapezoid(v[m], f[m]))/(2*np.pi*f0) for k, v in S.items()}
    out["TOTAL"] = np.sqrt(sum(v**2 for v in out.values()))
    L = 10*np.log10(sum(S.values())/2)
    return out, L


# ---------------------------------------------------------------- power and area (proposal design basis, 13 Nov)
# (block, supply, typ current mA, supply V typ, NCB?)  ring: CCO 1.31 mA x 9/8 (DAC + reference branch) from VDDA
POWER = [("ring VCO via CCO (1:8 mirror + DAC)", "VDDA", 1.31*9/8, 3.3, False, 7.46),
         ("ring output buffers (to SSPD, NCB, divider)", "LDO", 0.30, 3.3, False, None),
         ("SSPD + clock generator / pulser", "LDO", 0.12, 3.3, False, None),
         ("pulsed-Gm charge pump", "LDO", 0.05, 3.3, False, None),
         ("FLL charge pump (quiet in lock)", "LDO", 0.02, 3.3, False, None),
         ("bias distribution (IBIAS mirrors)", "LDO", 0.05, 3.3, False, None),
         ("NCB delay line", "LDO", 0.44, 3.3, True, None),
         ("LDO load reserve", "LDO", 0.10, 3.3, False, None),
         ("LDO quiescent (error amp, divider)", "VDDA", 0.15/3.3, 3.3, False, None),
         ("REF receiver (3.3 V, self-biased)", "VDDA", 0.2/3.3, 3.3, False, None),
         ("dividers (/32 TSPC), PFD, FLL logic, decode", "VDDD", 0.3/1.8, 1.8, False, None)]
AREA = [("ring VCO", 3000), ("CCO DAC + 1:8 mirror", 6000), ("SSPD, REF receiver, pulser", 3000),
        ("pulsed-Gm CP + loop filter", 5000), ("FLL (/32, PFD, CP)", 3000), ("NCB", 2500),
        ("LDO (new, not in the proposal table)", 4000), ("dividers, bias, control, pad interface", 4000),
        ("decoupling", 15000), ("routing / guard rings", 12000)]


def power_table():
    rows = []
    for name, sup, i, v, ncb, worst in POWER:
        p = i*1e-3*v*1e3
        pw = worst if worst else i*1.3*1e-3*(3.63 if sup != "VDDD" else 1.89)*1e3
        rows.append((name, sup, i, p, pw, ncb))
    return rows


def sensitivity(corner="typ", db=3.0):
    """jitter (ps) when one block's noise is db worse than its allocation."""
    out = {}
    for name in ALLOC:
        f, S = spectra(corner, True); f, S0 = spectra(corner, False)
        k = 10**(db/10)
        S[name] = S.get(name, 0*f)*k; S0[name] = S0.get(name, 0*f)*k
        out[name] = (jitter(S0, f, N*FREF)[0]["TOTAL"]*1e12, jitter(S, f, N*FREF)[0]["TOTAL"]*1e12)
    return out


if __name__ == "__main__":
    beta, d = loop()
    print(f"loop: beta = {beta*1e9:.0f} nA/rad, R1 = {d['R']/1e3:.2f} kOhm, C1 = {d['C1']*1e12:.2f} pF, C2 = {d['C2']*1e12:.2f} pF, "
          f"zero {d['fz']/1e6:.2f} MHz, pole {d['fp']/1e6:.2f} MHz")
    rows = []
    res = {}
    for corner in ("typ", "pess"):
        for ffnc in (False, True):
            for fref in (45e6, 50e6, 55e6):
                f, S = spectra(corner, ffnc, fref=fref)
                j, L = jitter(S, f, N*fref)
                res[(corner, ffnc, fref)] = (j, L, f)
    keys = list(res[("typ", True, 50e6)][0].keys())
    print("\njitter contributions at 50 MHz, 10 kHz-40 MHz (ps rms)")
    print(f"{'block':40s} {'typ off':>8s} {'typ on':>8s} {'pess off':>9s} {'pess on':>8s}")
    for k in keys:
        v = [res[(c, o, 50e6)][0].get(k, 0)*1e12 for c in ("typ", "pess") for o in (False, True)]
        print(f"{k:40s} {v[0]:8.3f} {v[1]:8.3f} {v[2]:9.3f} {v[3]:8.3f}")
        rows.append([k] + [f"{x:.4f}" for x in v])
    print("\ntotal over the reference range (ps):")
    for fref in (45e6, 50e6, 55e6):
        t = [res[(c, o, fref)][0]["TOTAL"]*1e12 for c in ("typ", "pess") for o in (False, True)]
        Lt = [res[(c, o, fref)] for c in ("typ", "pess") for o in (False, True)]
        l300 = [x[1][np.argmin(abs(x[2]-3e5))] for x in Lt]
        print(f"  {fref/1e6:.0f} MHz: typ off {t[0]:.2f} on {t[1]:.2f} | pess off {t[2]:.2f} on {t[3]:.2f} | "
              f"L(300k) typ off {l300[0]:.1f} on {l300[1]:.1f}, pess off {l300[2]:.1f} on {l300[3]:.1f}")
    with open(os.path.join(ROOT, "design", "budget", "budget.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["block", "typ_off_ps", "typ_on_ps", "pess_off_ps", "pess_on_ps"]); w.writerows(rows)

    print("\npower (mW): block, supply, I typ (mA), P typ, P worst")
    tot = {"on": [0, 0], "off": [0, 0]}
    for name, sup, i, p, pw, ncb in power_table():
        print(f"  {name:45s} {sup:5s} {i:6.3f} {p:6.2f} {pw:6.2f}")
        tot["on"][0] += p; tot["on"][1] += pw
        if not ncb: tot["off"][0] += p; tot["off"][1] += pw
    print(f"  TOTAL on {tot['on'][0]:.2f} (worst {tot['on'][1]:.2f}); off {tot['off'][0]:.2f} (worst {tot['off'][1]:.2f})")
    j = res[("typ", True, 50e6)][0]["TOTAL"]
    print(f"  FoM typ = {10*np.log10(j**2*tot['on'][0]):.1f} dB")
    print("\narea (um^2):", sum(a for _, a in AREA), [f"{n}: {a}" for n, a in AREA])
    print("\nsensitivity: block +3 dB -> total jitter typ off / on (ps)")
    for k, (a, b2) in sensitivity().items():
        print(f"  {k:40s} {a:.3f} {b2:.3f}")
    # block conversions
    c = CORNER["typ"]
    for nm, L in (("XO", -155), ("REF receiver", -155)):
        sig = np.sqrt(10**(L/10)*FREF)/(2*np.pi*FREF)
        print(f"{nm}: {L} dBc/Hz floor = {sig*1e15:.0f} fs rms per reference edge; at 1 Vpp sine "
              f"(slope {np.pi*1.0*FREF:.2e} V/s) = {sig*np.pi*FREF*1e6:.0f} uV rms at the threshold")
    KI = 1.22e12
    for L in (-104.2, -101.2):
        print(f"CCO {L}: i_n = {np.sqrt(2*10**(L/10))*1e6/KI*1e12:.2f} pA/rtHz at 1 MHz (K_I {KI:.2e} Hz/A)")
    print(f"R1 noise = {np.sqrt(4*kT*d['R'])*1e9:.1f} nV/rtHz")
