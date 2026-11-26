#!/usr/bin/env python3
"""loop_hv.py - the loop design redone for the device-rule migration: loop parameters (f_c, PM, beta, R1, C1, C2)
for 50 MHz x 16 = 800 MHz with every analog device 5 V-rated (the loop-filter MOS capacitor is now nfet_g5v0d10v5).

Same method as the archived 1.6 GHz loop script (SSPLL_Personal, design/loop/) (kept for the 1.6 GHz record):
  A. f_c and PM from the jitter model (design/budget/budget_hv.py) against the proposal targets;
  B. R1, C1, C2 for the exact sampled loop (design/loop/sampled_loop.py), packet delay from the clock-generator clock generator;
  C. realisation with PDK-legal, tile-based devices, C-V data from design/loop/spice/run_cv_hv.sh;
  D. robustness over the loop-gain spread m and the R / C corners;
  E. requirements handed to the other steps.
Run from the repo root:  python3 design/loop/loop_hv.py   (needs design/loop/data/moscap_hv_cv.csv, rc_corners.csv)
Writes design/loop/data/loop_hv_design.json, loop_hv_jitter_grid.csv."""
import os, sys, csv, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
for p in ("models", "learn", "design/budget", "design/loop", "tools"):
    sys.path.insert(0, os.path.join(ROOT, p))
import sampled_loop as sl
import budget_hv as bud
from pdk_limits import check

T, FREF, N, F0 = 20e-9, 50e6, 16, 800e6
KV = 2*np.pi*150e6                 # fine-tuning gain, rad/s/V (budget assumption; the VCO design sets it, only beta*KV matters)
FC, PM = 2.5e6, 50.0               # chosen in section A
TP = 0.5e-9                        # packet delay: the clock-generator design measured t_p 0.28 ns (0.18-0.50) + one level shifter
A, DUTY = 0.8, 0.01                # SSPD gain per side (V/rad, budget), Gm pulse duty tau/T (200 ps / 20 ns)
VC_WIN, VC_NOM = (1.0, 2.3), 1.65  # V_cont window and centre (VDDA/2): the 5 V MOS cap is flat above 1.0 V
SPEC = dict(out1_typ=2.6, out2_typ=1.6, out1_max=5.0, out2_max=3.2, L300_typ=-114.0, red_typ=35.0, red_min=20.0)

# ---------------------------------------------------------------- measured component data (frozen PDK, ngspice)
CV = list(csv.DictReader(open(os.path.join(HERE, "data", "moscap_hv_cv.csv"))))
RC = list(csv.DictReader(open(os.path.join(HERE, "data", "rc_corners.csv"))))


def cmos_density(v, corner="tt", temp="27"):
    """fF/um^2 of nfet_g5v0d10v5 used as a capacitor, W = L = 10 um (100 um^2)."""
    pts = [(float(r["vg"]), float(r["c_mos_fF"])/100) for r in CV if r["corner"] == corner and r["temp"] == temp]
    x, y = zip(*sorted(pts)); return float(np.interp(v, x, y))


C_MOS_UNIT = cmos_density(VC_NOM)*100e-15             # one 10 x 10 um 5 V MOS cap unit at the window centre
C_MIM_TILE = float(RC[1]["c_mim_fF"])*1e-15            # one 30 x 30 um cap_mim_m3_1, tt


def mim(w, l):                                         # cap_mim_m3_1: 2.00 fF/um^2 + 0.164 fF/um perimeter
    return (2.0*w*l + 0.164*2*(w + l))*1e-15


R_XHIGH_2P85 = (701.1, 139.0)                          # Ohm/um body, Ohm both heads
rx = [float(r["r_xhigh_po_ohm"]) for r in RC]; rx0 = float(RC[1]["r_xhigh_po_ohm"])
R_SPREAD = (min(rx)/rx0, max(rx)/rx0)
cm = [float(r["c_mim_fF"]) for r in RC]; MIM_SPREAD = (min(cm)/cm[1], max(cm)/cm[1])
TILE = 9*C_MOS_UNIT + C_MIM_TILE                       # 3 x 3 MOS units under one 30 x 30 MIM, about 35 x 35 um
TILE_UM = 35.0


def jitter_grid():
    fcs = [1.5e6, 2.0e6, 2.5e6, 3.0e6, 3.5e6, 4.0e6, 5.0e6]; pms = [40, 45, 50, 55, 60, 65]
    rows = []
    for pmd in pms:
        for fc in fcs:
            r = dict(pm=pmd, fc=fc)
            for c in ("typ", "pess"):
                for on in (False, True):
                    f, S = bud.spectra(c, on, fc=fc, pmd=pmd)
                    j, L = bud.jitter(S, f, F0)
                    key = f"{'out2' if on else 'out1'}_{c}"
                    r[key + "_ps"] = j["TOTAL"]*1e12; r[key + "_L300k"] = float(L[np.argmin(abs(f - 3e5))])
            r["reduction_typ_pct"] = 100*(1 - r["out2_typ_ps"]/r["out1_typ_ps"])
            rows.append(r)
    return rows


def realise(d, beta0, ntile=None):
    """Snap C1 to whole tiles, rescale beta (beta*KV/C fixed => same loop), then R1 and C2 follow."""
    n = ntile or max(1, int(round(d["C1"]/TILE)))
    C1 = n*TILE; k = C1/d["C1"]
    R = d["R"]/k; C2t = d["C2"]*k
    w = (C2t/2/1e-15 - 0.164*2*30)/(2.0*30 + 0.164*2)  # two equal cap_mim_m3_1, 30 um x w
    C2 = 2*mim(30, w)
    Lr = (R - R_XHIGH_2P85[1])/R_XHIGH_2P85[0]
    beta = beta0*k
    area = n*TILE_UM**2 + 2*(30 + 5)*(w + 5) + 3*(Lr/3 + 6)*6   # tiles + C2 + R1 folded in 3 with dummies
    return dict(ntile=n, tile_pF=TILE*1e12, C1=C1, R=R, C2=C2, C2_w=w, R_len=Lr, beta=beta,
                gm=beta/(2*A*DUTY), k=k, area_um2=area)


def mos_spread():
    """C1-tile multiplier over the V_cont window, ss/ff, -40/110 C (MOS share only; the MIM spread is separate)."""
    v = [cmos_density(x, c, t)/cmos_density(VC_NOM) for x in VC_WIN for c in ("ss", "ff", "tt") for t in ("-40", "27", "110")]
    return min(v), max(v)


def robustness(R, C1, C2, beta):
    ms = np.unique(np.round(np.r_[np.geomspace(0.35, 3.0, 25), 1.0], 4))
    lo, hi = mos_spread(); fm = 9*C_MOS_UNIT/TILE
    cases = {"nominal": (1, 1, 1)}
    for rn, rk in (("R min", R_SPREAD[0]), ("R max", R_SPREAD[1])):
        for cn, ck1, ck2 in (("C min", lo*fm + (1 - fm)*MIM_SPREAD[0], MIM_SPREAD[0]),
                             ("C max", hi*fm + (1 - fm)*MIM_SPREAD[1], MIM_SPREAD[1])):
            cases[f"{rn}, {cn}"] = (rk, ck1, ck2)
    out = {name: [sl.margins(R*rk, C1*c1k, C2*c2k, KV, beta*m, T, TP) for m in ms]
           for name, (rk, c1k, c2k) in cases.items()}
    return ms, out, (lo, hi)


def lf_noise_jitter(R, C1, C2):
    res = {}
    for c in ("typ", "pess"):
        for on in (False, True):
            f, S = bud.spectra(c, on, lf=(R, C1, C2))
            j, _ = bud.jitter(S, f, F0)
            res[f"{c}_{'on' if on else 'off'}"] = (j["loop-filter resistor R1"]*1e12, j["TOTAL"]*1e12)
    return res


if __name__ == "__main__":
    grid = jitter_grid()
    with open(os.path.join(HERE, "data", "loop_hv_jitter_grid.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(grid[0])); w.writeheader(); w.writerows(grid)
    print("A. jitter grid at PM 50 (ps; L300k dBc/Hz):")
    for r in grid:
        if r["pm"] == 50:
            print(f"  fc {r['fc']/1e6:.1f}: out1 typ {r['out1_typ_ps']:.2f} (L300 {r['out1_typ_L300k']:.1f}) out2 typ "
                  f"{r['out2_typ_ps']:.2f} | pess {r['out1_pess_ps']:.2f} / {r['out2_pess_ps']:.2f} | reduction {r['reduction_typ_pct']:.0f} %")
    print("  PM rows at fc 2.5 MHz:")
    for r in grid:
        if r["fc"] == 2.5e6:
            print(f"    PM {r['pm']}: out1 {r['out1_typ_ps']:.2f} out2 {r['out2_typ_ps']:.2f} L300 {r['out1_typ_L300k']:.1f} "
                  f"pess {r['out1_pess_ps']:.2f}/{r['out2_pess_ps']:.2f}")

    # B/C. sampled-loop design, then a beta trade (area vs R1 noise) on whole tiles
    beta0 = 1e-6
    d = sl.design(FC, PM, beta0, KV, T, TP)
    print(f"\nB. sampled design at beta 1 uA/rad: R {d['R']/1e3:.2f} k, C1 {d['C1']*1e12:.2f} p, C2 {d['C2']*1e12:.3f} p, "
          f"lead {d['lead']:.1f}, fz {d['fz']/1e6:.3f} MHz, fp {d['fp']/1e6:.2f} MHz")
    print(f"   tile: 9 x nfet_g5v0d10v5 10x10 ({C_MOS_UNIT*1e15:.0f} fF each at {VC_NOM} V) + MIM 30x30 ({C_MIM_TILE*1e15:.0f} fF)"
          f" = {TILE*1e12:.3f} pF in {TILE_UM:.0f} x {TILE_UM:.0f} um")
    trade = []
    print("   tiles  beta(uA/rad)  R1(k)  C1(p)  C2(p)  area(um2)  R1 jit off/on (ps)  total off/on (ps)")
    for n in (1, 2, 3, 4, 5, 6):
        z_ = realise(d, beta0, ntile=n); nj = lf_noise_jitter(z_["R"], z_["C1"], z_["C2"])
        trade.append(dict(ntile=n, beta=z_["beta"], R=z_["R"], C1=z_["C1"], C2=z_["C2"], area=z_["area_um2"],
                          rj_off=nj["typ_off"][0], rj_on=nj["typ_on"][0], tot_off=nj["typ_off"][1], tot_on=nj["typ_on"][1]))
        t_ = trade[-1]
        print(f"   {n:5d}  {t_['beta']*1e6:11.3f}  {t_['R']/1e3:5.2f}  {t_['C1']*1e12:5.2f}  {t_['C2']*1e12:5.2f}  {t_['area']:8.0f}"
              f"  {t_['rj_off']:.3f} / {t_['rj_on']:.3f}        {t_['tot_off']:.3f} / {t_['tot_on']:.3f}")
    NT = 2                                              # chosen: see docs/design/loop_hv.md section C
    z = realise(d, beta0, ntile=NT)
    fc_r, pm_r = sl.margins(z["R"], z["C1"], z["C2"], KV, z["beta"], T, TP)
    f = np.logspace(4, np.log10(0.49/T), 800)
    H = sl.closed_loop(f, z["R"], z["C1"], z["C2"], KV, z["beta"], T, TP)
    peak = 20*np.log10(np.max(np.abs(H))); f3 = f[np.argmin(abs(np.abs(H) - 1/np.sqrt(2)))]
    t, e, v = sl.step(z["R"], z["C1"], z["C2"], KV, z["beta"], T, TP, ncyc=500, phi_step=1.0)
    tol = 10e-12*2*np.pi*F0                            # +-10 ps at 800 MHz in rad
    settle = t[np.max(np.where(np.abs(e) > tol)[0]) + 1]
    over = -np.min(e)*100
    tps = [0.2e-9, 0.5e-9, 1e-9, 2e-9, 2.5e-9, 5e-9]
    pm_tp = [sl.margins(z["R"], z["C1"], z["C2"], KV, z["beta"], T, x)[1] for x in tps]
    ms, rob, mosr = robustness(z["R"], z["C1"], z["C2"], z["beta"])
    noise = lf_noise_jitter(z["R"], z["C1"], z["C2"])
    trim = {"00": 3, "01": 4, "10": 2, "11": 5}

    devs = [("res_xhigh_po_2p85", None, z["R_len"]), ("nfet_g5v0d10v5", 10, 10), ("cap_mim_m3_1", 30, 30),
            ("cap_mim_m3_1", 30, z["C2_w"])]
    viol = [x for d_, w_, l_ in devs for x in check(d_, w=w_, l=l_)]
    print("\nPDK limit check:", "all devices legal" if not viol else viol)
    assert not viol, viol
    print(f"C. realised ({NT} tiles): C1 {z['C1']*1e12:.2f} pF; beta {z['beta']*1e9:.0f} nA/rad (g_m {z['gm']*1e6:.1f} uS = 3 x "
          f"{z['gm']/3*1e6:.2f} uS at A {A} V/rad); R1 {z['R']/1e3:.2f} kOhm (xhigh_po_2p85, L {z['R_len']:.2f} um); C2 "
          f"{z['C2']*1e12:.3f} pF (2 x MIM 30 x {z['C2_w']:.2f} um); C_tot {(z['C1'] + z['C2'])*1e12:.2f} pF; area ~{z['area_um2']:.0f} um2")
    print(f"   zero {1/(2*np.pi*z['R']*z['C1'])/1e6:.3f} MHz, pole {(z['C1'] + z['C2'])/(2*np.pi*z['R']*z['C1']*z['C2'])/1e6:.2f} MHz")
    print(f"   sampled: fc {fc_r/1e6:.3f} MHz, PM {pm_r:.2f}; |H| peak {peak:.2f} dB, f3dB {f3/1e6:.2f} MHz; overshoot {over:.1f} %, "
          f"settles to +-10 ps in {settle*1e6:.2f} us")
    print("   PM vs tp:", [(round(a*1e9, 2), round(b, 1)) for a, b in zip(tps, pm_tp)])
    print(f"   R spread {R_SPREAD}, MIM spread {MIM_SPREAD}, MOS (V_cont {VC_WIN}, all corners) {mosr}")
    i1 = int(np.where(ms == 1.0)[0][0])
    for name, res in rob.items():
        ok = [m for m, (fc_, pm_) in zip(ms, res) if pm_ >= 45]; ok40 = [m for m, (fc_, pm_) in zip(ms, res) if pm_ >= 40]
        print(f"   {name:18s}: PM>=45 for m in [{min(ok):.2f}, {max(ok):.2f}], PM>=40 [{min(ok40):.2f}, {max(ok40):.2f}]; "
              f"m=1 fc {res[i1][0]/1e6:.2f} MHz PM {res[i1][1]:.1f}")
    resid = {}
    for lo, hi in ((0.75, 1.3), (0.6, 1.6)):
        sel = [r for v in rob.values() for m, r in zip(ms, v) if lo - 1e-9 <= m <= hi + 1e-9]
        resid[f"{lo}-{hi}"] = (min(r[1] for r in sel), max(r[1] for r in sel), min(r[0] for r in sel), max(r[0] for r in sel))
        print(f"   residual m {lo}-{hi}: PM {resid[f'{lo}-{hi}'][0]:.1f}-{resid[f'{lo}-{hi}'][1]:.1f} deg, "
              f"fc {resid[f'{lo}-{hi}'][2]/1e6:.2f}-{resid[f'{lo}-{hi}'][3]/1e6:.2f} MHz")
    print("   R1 noise (ps contribution / total):", {k: (round(a, 3), round(b, 3)) for k, (a, b) in noise.items()})
    # FLL slew on the same filter
    ctot = z["C1"] + z["C2"]
    print(f"   FLL: 10 uA into C_tot {ctot*1e12:.1f} pF slews V_cont at {10e-6/ctot/1e6:.2f} V/us")
    out = dict(fc=fc_r, pm=pm_r, tp=TP, KV=KV, A=A, duty=DUTY, R=z["R"], C1=z["C1"], C2=z["C2"], beta=z["beta"], gm=z["gm"],
               ntile=NT, tile_pF=z["tile_pF"], R_len=z["R_len"], C2_w=z["C2_w"], area_um2=z["area_um2"],
               fz=1/(2*np.pi*z["R"]*z["C1"]), fp=(z["C1"] + z["C2"])/(2*np.pi*z["R"]*z["C1"]*z["C2"]),
               peak_dB=peak, f3dB=f3, settle_s=settle, overshoot_pct=over, pm_vs_tp=list(zip(tps, pm_tp)), trim=trim,
               noise=noise, robust={k: [(float(m), float(a), float(b)) for m, (a, b) in zip(ms, v)] for k, v in rob.items()},
               residual=resid, trade=trade, mos_range=mosr, R_spread=R_SPREAD, MIM_spread=MIM_SPREAD,
               vc_window=VC_WIN, vc_nom=VC_NOM, c_mos_unit=C_MOS_UNIT, c_mim_tile=C_MIM_TILE)
    json.dump(out, open(os.path.join(HERE, "data", "loop_hv_design.json"), "w"), indent=1, default=float)
    print("-> design/loop/data/loop_hv_design.json")
