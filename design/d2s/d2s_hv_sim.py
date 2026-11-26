#!/usr/bin/env python3
"""d2s_hv_sim.py - verification of the diff-to-SE amplifier (D2S). -> data/d2s_hv_sim.json (one key per part)
A  DC transfer over MOS x R/C corners, temperature and VDDA, at the SSPD's sampled common mode for that condition:
   V_0, G at v_d = 0 and over the lock window, linear range, supply current                               (M28)
B  small signal: G(f), f_3dB and phase at f_ref/7.8 with the 40 fF NCB load; input capacitance per input   (M28)
C  noise: input-referred spectrum (resistors replaced by ideal ones of the same value: the PDK poly resistors
   are noiseless in ngspice), converted to output timing with the SSPD gain -> jitter 10 kHz-40 MHz       (M29)
D  VDDA -> vff (inputs at a fixed CM, and with the CM following VDDA as the SSPD's does), CM -> vff        (M21)
E  whole path: SSPD + clock generator + D2S core in one beat run: vff per period vs phase, slope, alpha
   with the real input capacitance, settling after each hold update                                       (M18)
F  mismatch Monte Carlo (mc_mm_switch = 1, 60 seeds): V_0 and G spread                                    (M30)
G  enable: en = 0 -> vff = V_0 independent of the input, current                                           (M28)
H  at lock (ring at exactly 16 f_ref): vff ripple at f_ref -> NCB delay modulation -> reference spur       (M19)
Usage: python3 d2s_hv_sim.py [A B C ...]   (default: all)"""
import os, re, json, sys
import numpy as np
from multiprocessing import Pool
import d2s_hv as A
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "sspd"))
DATA = os.path.join(HERE, "data", "d2s_hv_sim.json")
SSPD = json.load(open(os.path.join(ROOT, "design", "sspd", "data", "sspd_hv_sim.json")))["char"]
# conditions: the SSPD's (corner, temp, VDDA) set; its sampled CM and dv/dt (per side) for each
COND = []
for r in SSPD:
    k = (r["corner"], r["temp"], r["vdda"])
    if r["vddd"] in (1.8, 1.71, 1.89) and r["fref"] == 50e6 and k not in [c[:3] for c in COND]:
        COND.append((r["corner"], r["temp"], r["vdda"], r["cm"], 2*r["dvdt"], r["A"]))
TT = COND[0]
WIN = (-0.10, 0.30)          # v_d = inp - inm = v2m - v2p over the lock window: lock point 0.14-0.23 V, +-0.05 V signal


def load():
    return json.load(open(DATA)) if os.path.exists(DATA) else {}


def save(key, val):
    d = load(); d[key] = val
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    json.dump(d, open(DATA, "w"), indent=1)


def tag(c):
    return f"{c[0]} {c[1]} °C, {c[2]} V"


# ---------------------------------------------------------------- A
def part_a(c):
    corner, temp, vdda, cm, kt, a = c
    r = A.dc_transfer(corner=corner, temp=temp, vdda=vdda, cm=cm, span=0.5)
    v, g = r["v"], r["g"]
    w = (v >= WIN[0]) & (v <= WIN[1])
    return dict(cond=tag(c), cm=cm, V0=r["V0"], G=r["G"], Gmin=float(g[w].min()), Gmax=float(g[w].max()),
                lin=r["lin"], I=r["I"], P=r["P"], vmin=float(r["y"][w].min()), vmax=float(r["y"][w].max()),
                curve=[v[::4].tolist(), r["y"][::4].tolist()])


# ---------------------------------------------------------------- B
def part_b(c):
    corner, temp, vdda, cm, kt, a = c
    r = A.ac(corner=corner, temp=temp, vdda=vdda, cm=cm, vid=0.18)
    return dict(cond=tag(c), G0=r["G0"], f3=r["f3"], ph=r["ph_6M"], cin_inp=r["cin_inp"], cin_inm=r["cin_inm"],
                f=r["f"][::4].tolist(), mag=np.abs(r["Gf"])[::4].tolist())


# ---------------------------------------------------------------- C
def rvalue(model, l, corner, temp):
    net = (f"* r\n.lib {A.LIB} {corner}\n.temp {temp}\nvx a 0 1\n"
           f"xr a 0 0 sky130_fd_pr__{model} l={l} mult=1 m=1\n.control\nop\nprint -1/i(vx)\n.endc\n.end\n")
    o, _ = A.run(net)
    return float(re.search(r"-1/i\(vx\) = (\S+)", o).group(1))


def ideal_r(net, corner, temp):
    """Replace every poly-resistor instance by an ideal R of the same value (thermal noise 4kTR)."""
    cache = {}
    def rep(m):
        name, a, b, model, l = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        key = (model, l)
        if key not in cache:
            cache[key] = rvalue(model, l, corner, temp)
        return f"r{name} {a} {b} {cache[key]:.1f}"
    return re.sub(r"^x(\S+) (\S+) (\S+) \S+ sky130_fd_pr__(res_\S+) l=(\S+) mult=1 m=1$", rep, net, flags=re.M)


def noise_run(c, ideal=True):
    corner, temp, vdda, cm, kt, a = c
    net = A.head(corner=corner, temp=temp, vdda=vdda) + (
        f"vcm cmn 0 {cm}\nvd vdif 0 dc 0.18 ac 1\nep inp cmn vdif 0 0.5\nem inm cmn vdif 0 -0.5\n"
        ".control\noption sparse\nnoise v(vff) vd dec 20 1e3 1e9\nsetplot noise1\nwrdata n.txt inoise_spectrum onoise_spectrum\n.endc\n.end\n")
    if ideal:
        net = ideal_r(net, corner, temp)
    _, d = A.run(net, ["n.txt"])
    z = d["n.txt"]
    return z[:, 0], z[:, 1], z[:, 3]


def part_c(c):
    corner, temp, vdda, cm, kt, a = c
    f, vin, vout = noise_run(c, True)
    _, vin_mos, _ = noise_run(c, False)              # transistors only (PDK resistors noiseless)
    S_t = vin**2/kt**2                                 # s^2/Hz at the output, after the calibrated NCB
    band = (f >= 10e3) & (f <= 40e6)
    jit = float(np.sqrt(np.trapezoid(S_t[band], f[band])))
    L = 10*np.log10((2*np.pi*800e6)**2*S_t/2)
    white = float(np.interp(20e6, f, vin)); k = np.where(vin > np.sqrt(2)*white)[0]
    return dict(cond=tag(c), f=f.tolist(), vin=vin.tolist(), vin_mos=vin_mos.tolist(), jit=jit,
                vin_1M=float(np.interp(1e6, f, vin)), vin_20M=white,
                corner_f=float(f[k[-1]]) if len(k) else 0.0, L_1M=float(np.interp(1e6, f, L)),
                L_10M=float(np.interp(10e6, f, L)))


# ---------------------------------------------------------------- D
def part_d(c):
    corner, temp, vdda, cm, kt, a = c
    out = dict(cond=tag(c))
    k = cm/vdda
    for case, inp in (("cm_fixed", f"vp inp 0 {cm + 0.09}\nvm inm 0 {cm - 0.09}\n"),
                      ("cm_tracks", f"ep inp 0 VDDA 0 {(cm + 0.09)/vdda}\nem inm 0 VDDA 0 {(cm - 0.09)/vdda}\n")):
        net = A.head(corner=corner, temp=temp, vdda=vdda).replace(f"vdda VDDA 0 {vdda}", f"vdda VDDA 0 dc {vdda} ac 1") + inp + (
            ".control\nac dec 10 1e3 1e9\nlet m = abs(v(vff))\nwrdata s.txt m\n.endc\n.end\n")
        _, d = A.run(net, ["s.txt"])
        z = d["s.txt"]
        out[case] = dict(f=z[:, 0].tolist(), h=z[:, 1].tolist(), h_lf=float(z[0, 1]), h_1M=float(np.interp(1e6, z[:, 0], z[:, 1])),
                         h_max=float(z[z[:, 0] <= 40e6, 1].max()))
    net = A.head(corner=corner, temp=temp, vdda=vdda) + (
        f"vc cmn 0 dc {cm} ac 1\nep inp cmn 0 0 0\nvp inp cmn 0.09\nvm inm cmn -0.09\n"
        ".control\nac dec 10 1e3 1e9\nlet m = abs(v(vff))\nwrdata s.txt m\n.endc\n.end\n").replace("ep inp cmn 0 0 0\n", "")
    _, d = A.run(net, ["s.txt"])
    z = d["s.txt"]
    out["cm"] = dict(h_lf=float(z[0, 1]), h_max=float(z[z[:, 0] <= 40e6, 1].max()))
    g = part_a(c)["G"]
    out["Ks_ps_per_V"] = out["cm_tracks"]["h_max"]/(g*kt)*1e12
    out["G"] = g
    return out


# ---------------------------------------------------------------- E
def part_e(c):
    import sspd_hv as S
    corner, temp, vdda, cm, kt, a = c
    vddd = 1.8 if corner in ("tt", "sf", "fs", "hl", "lh") else (1.71 if vdda < 3.3 else 1.89)
    S.LOAD["ncb"] = 1e-18
    ex = (A.cells() + f"iib VDDA ib {A.D['IT']}\nvenb enb 0 0\ncl vff 0 40f\n"
          "xd2s v2m v2p vff ib enb VDDA 0 sspll_d2s_hv\n")
    net, fv = S.bench(S.D, corner, temp, vdda, vddd, 50e6, 64, extra=ex, save="v(vff)")
    _, d = A.run(net, ["w.txt"], timeout=20000)
    z = d["w.txt"]; t = z[:, 0]; g = lambda i: z[:, 2*i + 1]
    cks, ckh, v2p, v2m, vff = g(0), g(2), g(5), g(6), g(9)
    T = 2e-8; m = vdda/2
    ts = A.K.xings(t, cks, m, False); th = A.K.xings(t, ckh, m, False); thr = A.K.xings(t, ckh, m, True)
    rows, settle = [], []
    for s in ts:
        h = th[th > s]
        if s < 2*T or len(h) == 0 or h[0] + T - 1e-9 > t[-1]:
            continue
        te = h[0] + T - 1.0e-9                         # end of the hold period, just before the next update
        v2 = np.interp(te, t, v2p) - np.interp(te, t, v2m)
        rows.append(((2*np.pi*fv*s) % (2*np.pi), v2, float(np.interp(te, t, vff))))
        # settling: time after the hold switch closes (ckh rising) for vff to cover 90 % of its step
        hr = thr[thr < h[0]][-1]
        w = (t >= hr) & (t <= te); tw, yw = t[w], vff[w]
        y0 = np.interp(hr, t, vff); y1 = yw[-1]
        if abs(y1 - y0) > 5e-3:
            k = np.where(np.abs(yw - y0) >= 0.9*abs(y1 - y0))[0]
            settle.append(float(tw[k[0]] - h[0]))
    r = np.array(rows)
    ph, v2, y = r[:, 0], r[:, 1], r[:, 2]
    o = np.argsort(ph); ph, v2, y = ph[o], v2[o], y[o]
    xs = [i for i in range(1, len(ph)) if (v2[i - 1] < 0) != (v2[i] < 0) and abs(v2[i] - v2[i - 1]) < 1.0]
    if not xs:
        return dict(cond=tag(c), failed="no zero crossing of v2 in the beat", ph=ph.tolist(), v2=v2.tolist(), vff=y.tolist())
    i0 = xs[0]
    phi0 = ph[i0 - 1] + (0 - v2[i0 - 1])*(ph[i0] - ph[i0 - 1])/(v2[i0] - v2[i0 - 1])
    dphi = (ph - phi0 + np.pi) % (2*np.pi) - np.pi
    msk = np.abs(dphi) < 0.35                          # +-0.35 rad around the crossing (about 7 beat points)
    k_v2 = np.polyfit(dphi[msk], v2[msk], 1)[0]
    if k_v2 < 0:                                       # falling crossing found: use the rising one's convention
        k_v2 = -k_v2; dphi = -dphi
    k_ff = np.polyfit(dphi[msk], y[msk], 1)[0]
    w = (t > 30*T) & (t < 31.5*T)                      # one hold period of raw waveform for the figure
    wave = [((t[w] - 30*T)*1e9)[::4].tolist(), ckh[w][::4].tolist(), (v2p - v2m)[w][::4].tolist(), vff[w][::4].tolist()]
    return dict(cond=tag(c), k_v2=float(k_v2), k_vff=float(k_ff), G_path=float(-k_ff/k_v2), twoA=2*a, wave=wave,
                settle_90=float(np.median(settle)) if settle else None,
                dphi=dphi.tolist(), v2=v2.tolist(), vff=y.tolist())


# ---------------------------------------------------------------- H
def part_h(args):
    """At lock: ring at exactly 16 f_ref, sampled phi0 from the zero crossing (as the SSPD's kick bench). vff over the
    last periods: its ripple at f_ref modulates the NCB delay every period -> a reference-spur contribution."""
    import sspd_hv as S
    c, phi0 = args
    corner, temp, vdda, cm, kt, a = c
    vddd = 1.8 if corner in ("tt", "sf", "fs", "hl", "lh") else (1.71 if vdda < 3.3 else 1.89)
    S.LOAD["ncb"] = 1e-18
    T = 2e-8; fv = 16/T; Tv = 1/fv; nper = 8
    td = (T/4 + 0.425e-9 - phi0/(2*np.pi*fv)) % Tv
    ex = (A.cells() + f"iib VDDA ib {A.D['IT']}\nvenb enb 0 0\ncl vff 0 40f\n"
          "xd2s v2m v2p vff ib enb VDDA 0 sspll_d2s_hv\n")
    net, _ = S.bench(S.D, corner, temp, vdda, vddd, 50e6, nb=1e15, nper=nper, td=td, extra=ex, save="v(vff)", tstep=2e-12)
    _, d = A.run(net, ["w.txt"], timeout=20000)
    z = d["w.txt"]; t = z[:, 0]; g = lambda i: z[:, 2*i + 1]
    ckh, v2, vff = g(2), g(5) - g(6), g(9)
    w = (t > (nper - 3)*T) & (t < nper*T); tw, yw = t[w], vff[w]
    a1 = 2*abs(np.trapezoid(yw*np.exp(-2j*np.pi*tw/T), tw)/(tw[-1] - tw[0]))
    G = part_a(c)["G"]
    dt1 = a1/(G*kt)                                    # delay modulation at f_ref after the calibrated NCB
    spur = 20*np.log10(np.pi*fv*dt1 + 1e-30)           # PM: beta = 2 pi f0 dt1, sideband beta / 2
    m = (t > (nper - 1)*T)
    return dict(cond=tag(c), phi0=phi0, v2=float(np.mean(v2[w])), vff=float(np.mean(yw)), vff_pp=float(yw.max() - yw.min()),
                a1=float(a1), dt1=float(dt1), spur=float(spur),
                wave=[((t[m] - (nper - 1)*T)*1e9)[::3].tolist(), ckh[m][::3].tolist(), v2[m][::3].tolist(), vff[m][::3].tolist()])


# ---------------------------------------------------------------- F
def part_f(seed):
    corner, temp, vdda, cm, kt, a = TT
    net = A.head().replace(".temp 27", ".temp 27\n.param mc_mm_switch=1") + (
        f"vd vdif 0 0\nbp inp 0 v={cm} + v(vdif)/2\nbm inm 0 v={cm} - v(vdif)/2\n"
        f".control\nsetseed {seed}\ndc vd -0.05 0.05 0.05\nwrdata w.txt v(vff)\n.endc\n.end\n")
    _, d = A.run(net, ["w.txt"])
    z = d["w.txt"]
    return dict(seed=seed, V0=float(z[1, 1]), G=float((z[2, 1] - z[0, 1])/0.1))


# ---------------------------------------------------------------- G
def part_g(c):
    corner, temp, vdda, cm, kt, a = c
    on = A.dc_transfer(corner=corner, temp=temp, vdda=vdda, cm=cm, span=0.3)
    off = A.dc_transfer(corner=corner, temp=temp, vdda=vdda, cm=cm, span=0.3, en=False)
    return dict(cond=tag(c), V0_on=on["V0"], V0_off=off["V0"], dv_off=float(off["y"].max() - off["y"].min()),
                I_on=on["I"], I_off=off["I"])


if __name__ == "__main__":
    parts = sys.argv[1:] or list("ABCDEFG")
    with Pool(2) as pool:
        if "A" in parts:
            save("A", pool.map(part_a, COND))
        if "B" in parts:
            save("B", pool.map(part_b, COND))
        if "C" in parts:
            save("C", pool.map(part_c, [COND[0], COND[6], COND[8], COND[5]]))
        if "D" in parts:
            save("D", pool.map(part_d, [COND[0], COND[6], COND[8]]))
        if "E" in parts:
            save("E", pool.map(part_e, [COND[0], COND[5]]))
        if "H" in parts:
            save("H", pool.map(part_h, [(COND[0], -0.656), (COND[5], -0.54)]))   # phi0 for v2p - v2m at the lock point (2A x -0.1 rad)
        if "F" in parts:
            save("F", pool.map(part_f, range(1, 61)))
        if "G" in parts:
            save("G", pool.map(part_g, [COND[0], COND[6], COND[8]]))
    d = load()
    for k in parts:
        print(k, json.dumps(d.get(k), default=str)[:1500] if k in "FG" else "")
        if k in "ABCDEH":
            for r in d.get(k, []):
                print("  ", {q: (round(v, 4) if isinstance(v, float) else v) for q, v in r.items()
                             if not isinstance(v, (list, dict))})
