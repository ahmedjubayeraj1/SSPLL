#!/usr/bin/env python3
"""step73_loop.py - roadmap step 73: loop parameters (f_c, PM, beta, R1, C1, C2) chosen from the out2 (FFNC-on)
jitter model, checked with the exact sampled-data loop, and realised with PDK-legal, layout-friendly components.

Run from the repo root:  python3 design/loop/step73_loop.py
Needs design/loop/data/moscap_cv.csv and rc_corners.csv (design/loop/spice/run_cv.sh, run_rc.sh; already committed).
Writes design/loop/data/step73_*.csv and docs/img/step73_*.png and prints the design sheet."""
import os, sys, csv, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
for p in ("models", "learn", "design/budget", "design/loop", "tools"):
    sys.path.insert(0, os.path.join(ROOT, p))
import sampled_loop as sl
import step72_budget as bud
from pdk_limits import check

T, FREF, N, F0 = 20e-9, 50e6, 32, 1.6e9
KV = 2*np.pi*300e6                 # fine-tuning gain, rad/s/V (assumed until step 74; only beta*KV matters below)
FC, PM = 2.5e6, 50.0               # chosen below from the jitter model
TP = 2.5e-9                        # charge packet delay after the sampling edge (requirement on step 77, <= 5 ns)
A, DUTY = 0.5, 0.01                # SSPD sampled amplitude (V), Gm pulse duty tau/T (200 ps / 20 ns)
KT = 1.380649e-23*300

# ---------------------------------------------------------------- measured component data (frozen PDK, ngspice)
CV = list(csv.DictReader(open(os.path.join(HERE, "data", "moscap_cv.csv"))))
RC = list(csv.DictReader(open(os.path.join(HERE, "data", "rc_corners.csv"))))
def cmos_density(v, corner="tt", temp="27"):          # fF/um^2 of nfet_01v8 W = L = 10 um (100 um^2)
    pts = [(float(r["vg"]), float(r["c_mos_fF"])/100) for r in CV if r["corner"] == corner and r["temp"] == temp]
    x, y = zip(*sorted(pts)); return float(np.interp(v, x, y))
C_MOS_UNIT = cmos_density(0.9)*100e-15                 # one 10 x 10 um MOS cap unit at V_cont = 0.9 V
C_MIM_TILE = float(RC[1]["c_mim_fF"])*1e-15            # one 30 x 30 um cap_mim_m3_1 tile, tt
def mim(w, l):                                         # cap_mim_m3_1 model: 2.00 fF/um^2 + 0.164 fF/um perimeter
    return (2.0*w*l + 0.164*2*(w + l))*1e-15
R_XHIGH_2P85 = (701.1, 139.0)                          # Ohm/um body, Ohm both heads (docs/sky130_cheatsheet.md)
rx = [float(r["r_xhigh_po_ohm"]) for r in RC]; rx0 = float(RC[1]["r_xhigh_po_ohm"])
R_SPREAD = (min(rx)/rx0, max(rx)/rx0)
cm = [float(r["c_mim_fF"]) for r in RC]; MIM_SPREAD = (min(cm)/cm[1], max(cm)/cm[1])


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


def realise(d):
    """Snap C1 to whole layout tiles, then rescale beta (beta*KV fixed => same loop) so R and C2 follow."""
    tile = 9*C_MOS_UNIT + C_MIM_TILE                    # 3x3 MOS units (W = L = 10 um) with one 30x30 MIM on top
    ntile = max(1, int(round(d["C1"]/tile)))
    C1 = ntile*tile; k = C1/d["C1"]
    R = d["R"]/k; C2t = d["C2"]*k
    # C2: two equal cap_mim_m3_1 rectangles, 30 um x w (side-by-side, common terminal); solve w
    w = (C2t/2/1e-15 - 0.164*2*30)/(2.0*30 + 0.164*2)
    C2 = 2*mim(30, w)
    Lr = (R - R_XHIGH_2P85[1])/R_XHIGH_2P85[0]
    beta = 1e-6*k
    return dict(ntile=ntile, tile_pF=tile*1e12, C1=C1, R=R, C2=C2, C2_w=w, R_len=Lr, beta=beta,
                gm=beta/(2*A*DUTY), k=k)


def robustness(R, C1, C2, beta):
    """PM and f_c vs loop-gain multiplier m (A, g_m, tau, K_VCO spread) at the R / C extremes."""
    ms = np.unique(np.round(np.r_[np.geomspace(0.35, 3.0, 25), 1.0], 4))
    mos = [cmos_density(v, c, t)/cmos_density(0.9) for v in (0.6, 1.2) for c in ("ss", "ff") for t in ("-40", "110")]
    cases = {"nominal": (1, 1, 1)}
    for rn, rk in (("R min", R_SPREAD[0]), ("R max", R_SPREAD[1])):
        fm = 9*C_MOS_UNIT/(9*C_MOS_UNIT + C_MIM_TILE)      # MOS share of a C1 tile
        for cn, ck1, ck2 in (("C min", min(mos)*fm + (1 - fm)*MIM_SPREAD[0], MIM_SPREAD[0]),
                             ("C max", max(mos)*fm + (1 - fm)*MIM_SPREAD[1], MIM_SPREAD[1])):
            cases[f"{rn}, {cn}"] = (rk, ck1, ck2)
    out = {}
    for name, (rk, c1k, c2k) in cases.items():
        out[name] = [sl.margins(R*rk, C1*c1k, C2*c2k, KV, beta*m, T, TP) for m in ms]
    return ms, out, (min(mos), max(mos))


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
    with open(os.path.join(HERE, "data", "step73_jitter_grid.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(grid[0])); w.writeheader(); w.writerows(grid)
    print("jitter grid (ps) / L300k: PM 50 row")
    for r in grid:
        if r["pm"] == 50:
            print(f"  fc {r['fc']/1e6:.1f}: out1 typ {r['out1_typ_ps']:.2f} ({r['out1_typ_L300k']:.1f}) out2 typ {r['out2_typ_ps']:.2f} "
                  f"pess {r['out1_pess_ps']:.2f}/{r['out2_pess_ps']:.2f}  reduction {r['reduction_typ_pct']:.0f}%")

    # sampled-loop design at the chosen point, then layout-snapped realisation
    d = sl.design(FC, PM, 1e-6, KV, T, TP)
    z = realise(d)
    fc_r, pm_r = sl.margins(z["R"], z["C1"], z["C2"], KV, z["beta"], T, TP)
    f = np.logspace(4, np.log10(0.49/T), 800)
    H = sl.closed_loop(f, z["R"], z["C1"], z["C2"], KV, z["beta"], T, TP)
    peak = 20*np.log10(np.max(np.abs(H))); f3 = f[np.argmin(abs(np.abs(H) - 1/np.sqrt(2)))]
    t, e, v = sl.step(z["R"], z["C1"], z["C2"], KV, z["beta"], T, TP, ncyc=500, phi_step=1.0)
    tol = 10e-12*2*np.pi*F0                             # +-10 ps at 1.6 GHz in rad
    settle = t[np.max(np.where(np.abs(e) > tol)[0]) + 1]
    over = -np.min(e)/1.0*100
    # PM vs packet delay (requirement on the clock generator)
    tps = [0.5e-9, 1e-9, 2.5e-9, 5e-9, 8e-9, 11e-9]
    pm_tp = [sl.margins(z["R"], z["C1"], z["C2"], KV, z["beta"], T, x)[1] for x in tps]
    ms, rob, mosr = robustness(z["R"], z["C1"], z["C2"], z["beta"])
    noise = lf_noise_jitter(z["R"], z["C1"], z["C2"])
    # icp_trim: Gm unit count 3 nominal; offset-binary decode 00 -> 3, 01 -> 4, 10 -> 2, 11 -> 5 units
    trim = {"00": 3, "01": 4, "10": 2, "11": 5}
    # beta trade (area vs R noise) at the same f_c, PM
    trade = []
    for bt in (0.5e-6, 0.75e-6, 1e-6, 1.5e-6, 2e-6):
        k = bt/1e-6; R_, C1_, C2_ = d["R"]/k, d["C1"]*k, d["C2"]*k
        nj = lf_noise_jitter(R_, C1_, C2_)
        area = C1_/(z["tile_pF"]*1e-12)*34**2 + C2_/2e-15*1.15
        trade.append((bt, R_, C1_, C2_, area, nj["typ_off"][0], nj["typ_on"][0], nj["typ_off"][1], nj["typ_on"][1]))

    # project rule: every device inside the PDK min/max (tools/pdk_limits.py)
    devs = [("res_xhigh_po_2p85", None, z["R_len"]), ("nfet_01v8", 10, 10), ("cap_mim_m3_1", 30, 30),
            ("cap_mim_m3_1", 30, z["C2_w"])]
    viol = [x for d_, w_, l_ in devs for x in check(d_, w=w_, l=l_)]
    print("PDK limit check:", "all devices legal" if not viol else viol)
    assert not viol, viol
    print(f"\nsampled-loop design (tp {TP*1e9:.1f} ns): R {d['R']/1e3:.2f} k, C1 {d['C1']*1e12:.2f} p, C2 {d['C2']*1e12:.3f} p, "
          f"lead {d['lead']:.1f} deg, fz {d['fz']/1e6:.3f} MHz, fp {d['fp']/1e6:.2f} MHz")
    print(f"realised: C1 = {z['ntile']} tiles x {z['tile_pF']:.3f} pF = {z['C1']*1e12:.2f} pF; beta = {z['beta']*1e9:.0f} nA/rad "
          f"(gm {z['gm']*1e6:.1f} uS = 3 units x {z['gm']/3*1e6:.2f}); R1 = {z['R']/1e3:.2f} kOhm (xhigh_po_2p85, L {z['R_len']:.2f} um); "
          f"C2 = {z['C2']*1e12:.3f} pF (2 x MIM 30 x {z['C2_w']:.2f} um)")
    print(f"  sampled margins: fc {fc_r/1e6:.3f} MHz, PM {pm_r:.2f} deg; |H| peak {peak:.2f} dB, f_3dB {f3/1e6:.2f} MHz; "
          f"phase-step overshoot {over:.1f}%, settles to +-10 ps in {settle*1e6:.2f} us")
    print("  PM vs tp:", [(round(a*1e9, 1), round(b, 1)) for a, b in zip(tps, pm_tp)])
    print(f"  R spread {R_SPREAD}, MIM spread {MIM_SPREAD}, MOS cap (0.6-1.2 V, ss/ff, -40/110) {mosr}")
    i1 = int(np.where(ms == 1.0)[0][0])
    for name, res in rob.items():
        ok = [m for m, (fc_, pm_) in zip(ms, res) if pm_ >= 45]; ok40 = [m for m, (fc_, pm_) in zip(ms, res) if pm_ >= 40]
        print(f"  {name:18s}: PM>=45 for m in [{min(ok):.2f}, {max(ok):.2f}], PM>=40 for [{min(ok40):.2f}, {max(ok40):.2f}];"
              f"  m=1: fc {res[i1][0]/1e6:.2f} MHz PM {res[i1][1]:.1f}")
    allc = [r for v in rob.values() for r in v]
    for lo, hi in ((0.75, 1.3), (0.8, 1.25), (0.6, 1.6)):
        sel = [r for v in rob.values() for m, r in zip(ms, v) if lo - 1e-9 <= m <= hi + 1e-9]
        print(f"  residual m in [{lo}, {hi}] at all R/C corners: PM {min(r[1] for r in sel):.1f}-{max(r[1] for r in sel):.1f} deg, "
              f"fc {min(r[0] for r in sel)/1e6:.2f}-{max(r[0] for r in sel)/1e6:.2f} MHz")
    print("  LF R noise (ps contribution / total):", {k: (round(a, 3), round(b, 3)) for k, (a, b) in noise.items()})
    print("\nbeta trade: beta(uA/rad) R(k) C1(p) C2(p) area(um2) Rjit off/on total off/on")
    for r in trade:
        print("  " + " ".join(f"{x:.3g}" for x in (r[0]*1e6, r[1]/1e3, r[2]*1e12, r[3]*1e12, r[4], *r[5:])))
    out = dict(fc=fc_r, pm=pm_r, tp=TP, KV=KV, R=z["R"], C1=z["C1"], C2=z["C2"], beta=z["beta"], gm=z["gm"],
               ntile=z["ntile"], tile_pF=z["tile_pF"], R_len=z["R_len"], C2_w=z["C2_w"], fz=1/(2*np.pi*z["R"]*z["C1"]),
               fp=(z["C1"] + z["C2"])/(2*np.pi*z["R"]*z["C1"]*z["C2"]), peak_dB=peak, f3dB=f3, settle_s=settle,
               overshoot_pct=over, pm_vs_tp=list(zip(tps, pm_tp)), trim=trim, noise=noise,
               robust={k: [(float(m), float(a), float(b)) for m, (a, b) in zip(ms, v)] for k, v in rob.items()},
               trade=trade, mos_range=mosr, R_spread=R_SPREAD, MIM_spread=MIM_SPREAD)
    json.dump(out, open(os.path.join(HERE, "data", "step73_design.json"), "w"), indent=1, default=float)
    print("-> design/loop/data/step73_design.json")
