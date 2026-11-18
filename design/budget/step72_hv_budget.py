#!/usr/bin/env python3
"""step72_hv_budget.py - roadmap step 72, redone for the device-rule migration (18 Nov 2026):
50 MHz x 16 = 800 MHz, all analog blocks in 5 V devices (nfet/pfet_g5v0d10v5) on VDDA 3.3 V, digital in 1.8 V devices,
no LDO (the NCB and buffers sit on VDDA), 3-stage pseudo-differential ring (ring B) fed by the CCO.

Same model as step72_budget.py (the 1.6 GHz basis, kept unchanged for the record), with three changes:
  1. Every allocation is written at 800 MHz in its own units - no hidden frequency scaling. The ring and CCO keep the
     step-74/75 power and figure of merit: at the same power and FoM, L(1 MHz) is 20 log(1.6/0.8) = 6.02 dB lower at
     800 MHz and the ring's timing jitter is unchanged (ring jitter ~ 1/sqrt(P), independent of f0).
  2. "LDO noise through the NCB" is replaced by two supply paths of the raw VDDA: through the NCB delay (K_s, s/V, added
     directly at the output when FFNC is on) and into the ring through the CCO's finite output impedance
     (K_vdd, Hz/V, VCO-like: high-passed by the loop and cancelled by the FFNC).
  3. Power and area for 5 V analog + 1.8 V logic, level shifters, the /1-/16 output divider, no LDO.
Device data behind the allocations: design/feas/hv_noise.py (5 V devices: thermal gamma 1.1 nMOS / 0.53 pMOS vs 1.87 /
1.22 for the 1.8 V devices at g_m/I_D = 10).
Run from the repo root:  python3 design/budget/step72_hv_budget.py  -> design/budget/budget_hv.csv, budget_hv.json
"""
import os, sys, csv, json
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "models")); sys.path.insert(0, os.path.join(ROOT, "learn"))
import pllmodel as pm
from sspll_learn import loop_design_type2

kT = 1.380649e-23*300
FREF, N = 50e6, 16
F0 = N*FREF
KV_HZ = 150e6                       # fine-tuning gain at 800 MHz (300 MHz/V at 1.6 GHz scaled with f0; step 74 sets it)
FC, PMDEG = 2.5e6, 50               # f_ref/20, as before
D6 = 20*np.log10(1.6e9/F0)          # 6.02 dB: same power and FoM, half the carrier

# ---------------------------------------------------------------- per-block noise allocations at 800 MHz (typ, pess)
# kind: 'ref' (x N^2, in-loop), 'pd' (in-loop), 'lfr' (loop-filter R), 'vco' (high-passed, cancelled by FFNC),
#       'out' (after the NCB, added directly), 'supply_ncb' (VDDA through the NCB delay), 'supply_vco' (VDDA into the ring)
ALLOC = {
 "XO (crystal oscillator, board)":           dict(kind="ref", typ=(-155, 30e3), pess=(-155, 100e3)),
 "REF receiver + clock gen + level shifter":  dict(kind="ref", typ=(-155, 30e3), pess=(-151, 100e3)),
 "SSPD sampler (kT/C)":                      dict(kind="pd"),
 "pulsed-Gm charge pump":                    dict(kind="pd"),
 "loop-filter resistor R1":                  dict(kind="lfr"),
 # ring: step-74 FoM (Lth -98.35 dBc/Hz at 1 MHz from 1.6 GHz) at the same power -> -104.4 at 800 MHz; 1/f^3 corner as
 # achieved in step 74 (0.6 MHz). pess: 3 dB worse thermal (FoM not reached in thick oxide) and a 1.2 MHz corner.
 "ring VCO core (5 V, 3-stage)":             dict(kind="vco", typ=(-98.35 - D6, 0.60e6), pess=(-98.35 - D6 + 3, 1.2e6)),
 # CCO: same 1.31 mA source, same current noise; the Hz/A gain halves at 800 MHz -> 6 dB lower in dBc/Hz
 "CCO current DAC + mirror":                 dict(kind="vco", typ=(-104.2 - D6, 0.30e6), pess=(-101.2 - D6, 0.6e6)),
 # NCB: the same timing noise as the 1.6 GHz allocation (-150 dBc/Hz there) -> 6 dB lower in dBc/Hz at 800 MHz
 "NCB delay line (intrinsic)":               dict(kind="out", typ=(-150 - D6, 1e6), pess=(-146 - D6, 3e6)),
 # raw VDDA at the die: board regulator + on-chip decoupling; 1/f corner 10 kHz. K_s = NCB delay sensitivity (s/V)
 "VDDA noise through the NCB":               dict(kind="supply_ncb", typ=(100e-9, 104e-12), pess=(300e-9, 120e-12)),
 # K_vdd = ring frequency pushing by VDDA through the CCO output impedance (Hz/V)
 "VDDA noise into the ring (CCO r_out)":     dict(kind="supply_vco", typ=(100e-9, 5e6), pess=(300e-9, 20e6)),
}
# A per VCO radian doubles at half the carrier (same edge slope, step 78: 0.51 V/rad at 1.6 GHz); Cs = step-78 C1 + parasitics
CORNER = dict(typ=dict(A=0.8, gamma=1.1, gm=100e-6, duty=0.01, Cs=46e-15, gerr=0.10),
              pess=dict(A=0.5, gamma=1.5, gm=100e-6, duty=0.01, Cs=35e-15, gerr=0.30))


def loop(fref=FREF, n=N, fc=FC, pmdeg=PMDEG, corner="typ"):
    p = CORNER[corner]
    beta = 2*p["A"]*p["gm"]*p["duty"]                       # A per VCO rad (pulsed Gm, step 50)
    d = loop_design_type2(fc, pmdeg, 2*np.pi*n*beta, 2*np.pi*KV_HZ, n)
    return beta, d


def spectra(corner, ffnc, fref=FREF, n=N, f=None, alias=True, fc=None, pmd=None, over=None, lf=None):
    """Output phase-noise PSD per block (rad^2/Hz) at f0 = n*fref. over = {block: value} replaces an allocation;
    lf = (R1, C1, C2) uses a realised loop filter for the R1 noise term (step 73) instead of the closed-form one."""
    f = pm.freq_axis(n=3000) if f is None else f
    fc = FC if fc is None else fc
    pmd = PMDEG if pmd is None else pmd
    over = over or {}
    c = CORNER[corner]; f0 = n*fref
    beta, d = loop(fref, n, fc, pmd)
    H = pm.loop_H(f, fc, pmd)
    Gc = pm.ffnc_Gc(f, fref, c["gerr"], on=ffnc)
    T_in = np.abs(H + Gc*(1-H))**2; T_vco = np.abs((1-Gc)*(1-H))**2
    lin = lambda L: 2*10**(L/10)
    sc = 20*np.log10(f0/F0)                                  # 45 / 55 MHz points: ring and CCO at the same power
    S = {}
    for name, a in ALLOC.items():
        k = a["kind"]
        val = over.get(name, a.get(corner))
        if k == "ref":
            L, fc1 = val; S[name] = lin(pm.floor_L(f, L, fc1) + 20*np.log10(n))*T_in
        elif k == "pd" and "kT/C" in name:
            L = 10*np.log10(kT/(2*c["Cs"]*c["A"]**2*fref))  # differential sampler (step 49)
            S[name] = lin(np.full_like(f, L))*T_in
        elif k == "pd":
            L = 10*np.log10(kT*c["gamma"]/(c["A"]**2*c["gm"]*c["duty"])/2)   # gated Gm noise, beta = 2 A gm d
            S[name] = lin(pm.floor_L(f, L, 300e3))*T_in
        elif k == "lfr":
            s = 2j*np.pi*f
            R_, C1_, C2_ = lf if lf is not None else (d["R"], d["C1"], d["C2"])
            Hr = C1_/((C1_ + C2_) + s*R_*C1_*C2_)
            S[name] = 4*kT*R_*np.abs(Hr)**2*(2*np.pi*KV_HZ)**2/(2*np.pi*f)**2*T_vco
        elif k == "vco":
            L1, fc3 = val; S[name] = lin(pm.vco_L(f, L1 + sc, fc3))*T_vco
        elif k == "out":
            L, fc1 = val; S[name] = lin(pm.floor_L(f, L, fc1) + sc) if ffnc else 0*f
        elif k == "supply_ncb":
            vn, Ks = val; Sv = vn**2*(1 + 10e3/f)
            S[name] = (2*np.pi*f0*Ks)**2*Sv if ffnc else 0*f
        elif k == "supply_vco":
            vn, Kvdd = val; Sv = vn**2*(1 + 10e3/f)
            S[name] = Kvdd**2*Sv/f**2*T_vco
    if ffnc and alias:                                       # Thijssen aliasing of VCO-like noise (step 70)
        vco_like = sum(S[k]/np.maximum(T_vco, 1e-30) for k in ALLOC if ALLOC[k]["kind"] in ("vco", "lfr", "supply_vco"))
        fa = lambda x: np.interp(np.abs(x), f, vco_like*np.abs(1-H)**2, left=vco_like[0], right=0)
        S["aliasing of VCO noise (k = 1..3)"] = sum(fa(f - k*fref) + fa(f + k*fref) for k in (1, 2, 3))*np.abs(Gc)**2
    return f, S


def jitter(S, f, f0=F0, band=(10e3, 40e6)):
    m = (f >= band[0]) & (f <= band[1])
    out = {k: np.sqrt(np.trapezoid(v[m], f[m]))/(2*np.pi*f0) for k, v in S.items()}
    out["TOTAL"] = np.sqrt(sum(v**2 for k, v in out.items()))
    L = 10*np.log10(sum(S.values())/2)
    return out, L


# ---------------------------------------------------------------- power (supply, I typ mA, V, NCB?, P worst mW or None)
POWER = [("ring VCO via CCO (1:8 mirror + DAC), 5 V devices", "VDDA", 1.31*9/8, 3.3, False, 7.46),
         ("ring output buffers (to SSPD, NCB, divider LS)", "VDDA", 0.30, 3.3, False, None),
         ("SSPD (5 V sampler + dummy, shaping buffers)", "VDDA", 0.15, 3.3, False, None),
         ("level shifters 1.8<->3.3 V (sampling/Gm/hold clocks, 800 MHz to divider)", "VDDA", 0.10, 3.3, False, None),
         ("pulsed-Gm charge pump", "VDDA", 0.05, 3.3, False, None),
         ("FLL charge pump (quiet in lock)", "VDDA", 0.02, 3.3, False, None),
         ("bias distribution (IBIAS mirrors)", "VDDA", 0.05, 3.3, False, None),
         ("NCB delay line", "VDDA", 0.44, 3.3, True, None),
         ("REF receiver (5 V, self-biased)", "VDDA", 0.2/3.3, 3.3, False, None),
         ("clock generator (step 77, 1.8 V logic)", "VDDD", 0.08/1.8, 1.8, False, None),
         ("/16 TSPC divider, PFD, FLL logic, decode", "VDDD", 0.20/1.8, 1.8, False, None),
         ("output divider /1-/16 + glitch-free mux", "VDDD", 0.12/1.8, 1.8, False, None)]
# area (um^2): 5 V devices need wider spacing and guard rings (~1.3-2x the 1.8 V layout)
AREA = [("ring VCO (3-stage, 5 V)", 4000), ("CCO DAC + 1:8 mirror", 6000), ("SSPD, REF receiver, pulser", 4000),
        ("level shifters", 1000), ("pulsed-Gm CP + loop filter", 5000), ("FLL (/16, PFD, CP)", 3000),
        ("NCB (5 V)", 4000), ("output divider + mux", 1000), ("dividers, bias, control, pad interface", 4000),
        ("decoupling", 15000), ("routing / guard rings", 13000)]


def power_table():
    rows = []
    for name, sup, i, v, ncb, worst in POWER:
        p = i*v
        pw = worst if worst else i*1.3*(3.63 if sup != "VDDD" else 1.89)
        rows.append((name, sup, i, p, pw, ncb))
    return rows


def sensitivity(corner="typ", db=3.0):
    """jitter (ps) FFNC off / on when one block's noise is db worse than its allocation."""
    out = {}
    f, S1 = spectra(corner, True); f, S0 = spectra(corner, False)
    for name in list(S1):
        k = 10**(db/10)
        a = dict(S0); b2 = dict(S1)
        if name in a: a[name] = a[name]*k
        b2[name] = b2[name]*k
        out[name] = (jitter(a, f)[0]["TOTAL"]*1e12, jitter(b2, f)[0]["TOTAL"]*1e12)
    return out


def run_all():
    res = {}
    for corner in ("typ", "pess"):
        for ffnc in (False, True):
            for fref in (45e6, 50e6, 55e6):
                f, S = spectra(corner, ffnc, fref=fref)
                j, L = jitter(S, f, N*fref)
                res[(corner, ffnc, fref)] = (j, L, f)
    return res


if __name__ == "__main__":
    beta, d = loop()
    print(f"f0 = {F0/1e6:.0f} MHz, N = {N}; loop: beta = {beta*1e9:.0f} nA/rad, R1 = {d['R']/1e3:.2f} kOhm, "
          f"C1 = {d['C1']*1e12:.2f} pF, C2 = {d['C2']*1e12:.2f} pF, zero {d['fz']/1e6:.2f} MHz, pole {d['fp']/1e6:.2f} MHz")
    res = run_all()
    keys = list(res[("typ", True, 50e6)][0].keys())
    rows = []
    print("\njitter contributions at 50 MHz (800 MHz out), 10 kHz-40 MHz (ps rms)")
    print(f"{'block':44s} {'typ off':>8s} {'typ on':>8s} {'pess off':>9s} {'pess on':>8s}")
    for k in keys:
        v = [res[(c, o, 50e6)][0].get(k, 0)*1e12 for c in ("typ", "pess") for o in (False, True)]
        print(f"{k:44s} {v[0]:8.3f} {v[1]:8.3f} {v[2]:9.3f} {v[3]:8.3f}")
        rows.append([k] + [f"{x:.4f}" for x in v])
    summary = {}
    print("\ntotal over the reference range (ps; L in dBc/Hz):")
    for fref in (45e6, 50e6, 55e6):
        t = [res[(c, o, fref)][0]["TOTAL"]*1e12 for c in ("typ", "pess") for o in (False, True)]
        Lt = [res[(c, o, fref)] for c in ("typ", "pess") for o in (False, True)]
        l300 = [float(x[1][np.argmin(abs(x[2]-3e5))]) for x in Lt]
        l1m = [float(x[1][np.argmin(abs(x[2]-1e6))]) for x in Lt]
        summary[f"{fref/1e6:.0f}"] = dict(jit=t, L300k=l300, L1M=l1m)
        print(f"  {fref/1e6:.0f} MHz ({N*fref/1e6:.0f} MHz out): typ off {t[0]:.2f} on {t[1]:.2f} | pess off {t[2]:.2f} on {t[3]:.2f} | "
              f"L(300k) typ {l300[0]:.1f} / {l300[1]:.1f}, pess {l300[2]:.1f} / {l300[3]:.1f} | "
              f"L(1M) typ {l1m[0]:.1f} / {l1m[1]:.1f}")
    with open(os.path.join(ROOT, "design", "budget", "budget_hv.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["block", "typ_off_ps", "typ_on_ps", "pess_off_ps", "pess_on_ps"]); w.writerows(rows)

    print("\npower (mW): block, supply, I typ (mA), P typ, P worst")
    tot = {"on": [0, 0], "off": [0, 0]}
    for name, sup, i, p, pw, ncb in power_table():
        print(f"  {name:72s} {sup:5s} {i:6.3f} {p:6.2f} {pw:6.2f}")
        tot["on"][0] += p; tot["on"][1] += pw
        if not ncb: tot["off"][0] += p; tot["off"][1] += pw
    print(f"  TOTAL on {tot['on'][0]:.2f} (worst {tot['on'][1]:.2f}); off {tot['off'][0]:.2f} (worst {tot['off'][1]:.2f})")
    j = res[("typ", True, 50e6)][0]["TOTAL"]; j0 = res[("typ", False, 50e6)][0]["TOTAL"]
    fom = 10*np.log10(j**2*tot['on'][0]*1e-3/1e-3); fom0 = 10*np.log10(j0**2*tot['off'][0])
    print(f"  FoM typ = {fom:.1f} dB (FFNC on), {fom0:.1f} dB (off)")
    area = sum(a for _, a in AREA)
    print(f"\narea: {area} um^2 = {area/1e6:.3f} mm^2")
    sens = sensitivity()
    print("\nsensitivity: block +3 dB -> total jitter typ off / on (ps)")
    for k, (a, b2) in sens.items():
        print(f"  {k:44s} {a:.3f} {b2:.3f}")
    # block targets in each block's own units
    c = CORNER["typ"]
    print("\nblock targets (typ):")
    for nm, a in ALLOC.items():
        if a["kind"] in ("ref", "vco", "out"):
            print(f"  {nm:44s} L = {a['typ'][0]:.1f} dBc/Hz, corner {a['typ'][1]/1e3:.0f} kHz  (pess {a['pess'][0]:.1f}, {a['pess'][1]/1e3:.0f} kHz)")
        elif a["kind"].startswith("supply"):
            print(f"  {nm:44s} v_n = {a['typ'][0]*1e9:.0f} nV/rtHz, K = {a['typ'][1]:.3g}  (pess {a['pess'][0]*1e9:.0f}, {a['pess'][1]:.3g})")
    sig = lambda L, fr: np.sqrt(10**(L/10)*fr)/(2*np.pi*fr)
    print(f"  ring: L(1 MHz) {ALLOC['ring VCO core (5 V, 3-stage)']['typ'][0]:.1f} dBc/Hz at {F0/1e6:.0f} MHz = "
          f"FoM {ALLOC['ring VCO core (5 V, 3-stage)']['typ'][0] + 10*np.log10(1.31*9/8*3.3) - 20*np.log10(F0/1e6):.1f} dB with the CCO supply power")
    KI = 1.22e12/2
    for L in (ALLOC["CCO current DAC + mirror"]["typ"][0], ALLOC["CCO current DAC + mirror"]["pess"][0]):
        print(f"  CCO {L:.1f}: i_n = {np.sqrt(2*10**(L/10))*1e6/KI*1e12:.2f} pA/rtHz at 1 MHz (K_I {KI:.2e} Hz/A)")
    print(f"  R1 noise = {np.sqrt(4*kT*d['R'])*1e9:.1f} nV/rtHz")
    json.dump(dict(f0=F0, N=N, loop=dict(beta=beta, R=d["R"], C1=d["C1"], C2=d["C2"], fz=d["fz"], fp=d["fp"]),
                   summary=summary, contrib={r[0]: [float(x) for x in r[1:]] for r in rows},
                   power=dict(on=tot["on"], off=tot["off"]), fom_on=fom, fom_off=fom0, area_um2=area,
                   sens={k: list(v) for k, v in sens.items()}),
              open(os.path.join(ROOT, "design", "budget", "budget_hv.json"), "w"), indent=1)
