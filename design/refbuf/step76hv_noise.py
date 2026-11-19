#!/usr/bin/env python3
"""step76hv_noise.py - phase noise of the 5 V REF receiver and its effect on the 800 MHz PLL (step 76 redo).

 1. S1 gate-referred noise spectrum (.noise at the self-bias point, M14) - S1 is the same circuit as on 13 Nov.
 2. Per-edge white jitter of S1 by transient noise (M15): a pad-referred white source of S1's plateau density, the
    circuit otherwise noiseless; 3.3 V pp square (typical CMOS crystal oscillator) and 1 V pp / 0.4 V pp sine.
 3. Jitter added by the output chain S2 (5 V, VDDA) -> level shifter (5 V on VDDD) -> NOR (1.8 V on VDDD) (M17): white
    drain-noise current of each stage at its trip point injected at its output node, noiseless input.
 4. Supply terms from step76hv_supply.py (M21): L(f) = (2 pi f_ref)^2 K(f)^2 S_v(f) / 2 for VDDA and VDDD.
 5. System (M9, design/budget/hv_system.py): the REF chain L(f) replaces the step-72 HV allocation; the clock-generator
    sampling edge and the SSPD isolation buffers keep their step-77 / step-78 values until those steps are redone.
-> data/step76hv_noise.json"""
import os, re, sys, json
import numpy as np
from multiprocessing import Pool
import refbuf as R, refbuf_hv as H
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "budget"))
FREF = 50e6
CLKGEN = (-163.4, 30e3)     # step 77 sampling edge (0.15 ps per edge, M17), kept until step 77 is redone
SSPDBUF = (-169.0, 30e3)    # step 78 isolation buffers (0.080 ps on the differential crossing), kept until step 78 HV
VN = dict(typ=100e-9, pess=300e-9)   # VDDA noise at the die (step 72 HV), 10 kHz corner


def stage_noise(lines, vdd):
    """White drain-current noise (A^2/Hz at 1 GHz) of a stage held at its trip point (input a = output y = V_M).
    lines: device lines with nodes a (in), y (out), VDD, 0."""
    net = (f"* stage noise\n.lib {R.LIB} tt\n.temp 27\nvdd VDD 0 {vdd}\n{lines}"
           "vm y ym 0\nvo ym 0 dc {vt}\nva a 0 dc {vt} ac 1\nh1 o 0 vm 1\n")
    lo, hi = 0.15*vdd, 0.85*vdd
    for _ in range(18):
        mid = (lo + hi)/2
        out, _ = R.run(net.replace("{vt}", f"{mid:.5f}") + ".control\nop\nprint i(vm)\n.endc\n.end\n")
        i = float(re.search(r"i\(vm\) = (\S+)", out).group(1))
        lo, hi = (mid, hi) if i > 0 else (lo, mid)
    out, _ = R.run(net.replace("{vt}", f"{mid:.5f}") +
                   ".control\noption sparse\nnoise v(o) va lin 1 1e9 1e9\nprint onoise_spectrum\n.endc\n.end\n")
    return float(re.search(r"onoise_spectrum = (\S+)", out).group(1))**2, mid


def chain_S():
    p, q, m = R.D, R.PDK, R._m
    s2 = m("p2", "y", "a", "VDD", "VDD", p["P2"]) + m("n2", "y", "a", "0", "0", p["N2"])
    ls = m("pl", "y", "a", "VDD", "VDD", p["PL"]) + m("nl", "y", "a", "0", "0", p["NL"])
    nor = (m("pb", "xb", "a", "VDD", "VDD", q["PB2"]) + m("pb2", "y", "0", "xb", "VDD", q["PB2"]) + m("nb", "y", "a", "0", "0", p["NB"])
           + m("nb2", "y", "0", "0", "0", q["NB2"]))
    return {"s2": stage_noise(s2, 3.3), "s3": stage_noise(ls, 1.8), "refclk": stage_noise(nor, 1.8)}


def flat_tail():
    """The top cell's body at top level (so noise sources can be attached to s2, s3, refclk)."""
    full = H.full()
    i = full.index(".subckt sspll_refbuf_hv ")
    body = full[full.index("\n", i) + 1: full.rindex(".ends")]
    return full[:i], body


def chain_jitter(a):
    """a = (S dict, scale, seed, vpp, wave): refclk rising-edge jitter from the output chain only."""
    S, scale, seed, vpp, wave = a
    subs, body = flat_tail(); nt = 4e-12; T = 1/FREF; ncyc = 80   # 80 edges: +-8 % on sigma
    src = "".join(f"in_{n} 0 {n} dc 0 trnoise({scale*np.sqrt(S[n][0]/(2*nt)):.4e} {nt} 0 0)\n" for n in ("s2", "s3", "refclk"))
    b = H.op()
    net = (f"* chain jitter\n.lib {R.LIB} tt\n.temp 27\n{subs}{body}vss VSS 0 0\nvdda VDDA 0 3.3\nvddd VDDD 0 1.8\niib ib 0 2.5e-6\n"
           f"ven pll_en 0 1.8\ncl refclk 0 50f\n" + H.src(3.3, vpp, FREF, wave).replace("pad0", "REF_IN") + src +
           f".ic v(vin)={b['vin']} v(s1)={b['s1']}\n.options seed={seed}\n.control\n"
           f"save v(REF_IN) v(refclk)\ntran {nt} {(ncyc + 20)*T} {20*T} {nt}\nwrdata w.txt v(REF_IN) v(refclk)\n.endc\n.end\n")
    _, d = R.run(net, ["w.txt"])
    z = d["w.txt"]; t = z[:, 0]
    tp, _ = R.xings(t, z[:, 1], 1.65, True); to, _ = R.xings(t, z[:, 3], 0.9, True)
    dly = np.array([to[to > x][0] - x for x in tp[:-1] if np.any(to > x)])
    k = np.arange(len(dly)); dev = dly - np.polyval(np.polyfit(k, dly, 4), k)
    assert len(dly) > 0.9*ncyc, f"only {len(dly)} edges: the transient stopped early"
    return dict(sigma=float(dev.std()), n=len(dly), mean=float(dly.mean()))


def tn(a):
    vpp, wave, Sw, seed = a
    te = R.tnoise(Sw, vpp=vpp, ncyc=300, seed=seed, wave=wave)
    x = np.array(R.edge_stats(te)["dev"]); k = np.arange(len(x)); x = x - np.polyval(np.polyfit(k, x, 4), k)
    return dict(vpp=vpp, wave=wave, abs=float(x.std()), per=float(np.diff(x).std()), n=len(x))


def job(j):
    """Runs one transient-noise job; results are cached in data/step76hv_cache/ so a restart does not lose them."""
    key = "_".join(str(x) for x in (j[0],) + tuple(v for v in j[1:] if not isinstance(v, dict)))
    fn = os.path.join(HERE, "data", "step76hv_cache", key + ".json")
    if os.path.exists(fn):
        return json.load(open(fn))
    r = tn(j[1:]) if j[0] == "tn" else chain_jitter(j[1:])
    os.makedirs(os.path.dirname(fn), exist_ok=True); json.dump(r, open(fn, "w"))
    return r


def L_supply(f, K, vn):
    """dBc/Hz at the reference from a supply with noise vn (white, 10 kHz 1/f corner) and edge sensitivity K(f) (s/V)."""
    Sv = vn**2*(1 + 10e3/f)
    return 10*np.log10((2*np.pi*FREF)**2*K(f)**2*Sv/2)


if __name__ == "__main__":
    import hv_system as HS
    import pllmodel as pm
    out = {}
    f, Sg, fg, vi = R.input_noise()
    Swg = float(np.interp(3e8, f, Sg)); div = np.abs(np.interp(f, fg, vi.real) + 1j*np.interp(f, fg, vi.imag))
    div50 = float(np.interp(5e7, f, div)); Sw = Swg/float(np.interp(3e8, f, div))**2
    out.update(f=f.tolist(), Sgate=Sg.tolist(), Swg=Swg, Sw_pad=Sw, div50=div50)
    print(f"S1 gate white {np.sqrt(Swg)*1e9:.2f} nV/rtHz, pad {np.sqrt(Sw)*1e9:.2f}, |v_gate/v_pad| at 50 MHz {div50:.3f}", flush=True)
    S = chain_S(); out["chain_S"] = {k: list(v) for k, v in S.items()}
    print("chain noise", {k: (f"{np.sqrt(v[0])*1e12:.2f} pA/rtHz", round(v[1], 3)) for k, v in S.items()}, flush=True)
    jobs = [("tn", 3.3, "square", Sw, 1), ("tn", 1.0, "sine", Sw, 2), ("tn", 0.4, "sine", Sw, 3),
            ("ch", S, 1.0, 4, 3.3, "square"), ("ch", S, 1e-6, 4, 3.3, "square"), ("ch", S, 1.0, 5, 1.0, "sine")]
    with Pool(2) as pool:
        r = pool.map(job, jobs)
    out["tn"] = r[:3]; out["chain"] = dict(square=r[3], baseline=r[4], sine1=r[5])
    for x in r[:3]:
        print(f"S1 per-edge white jitter {x['vpp']} V pp {x['wave']}: {x['abs']*1e12:.3f} ps (period/sqrt2 {x['per']/np.sqrt(2)*1e12:.3f})")
    ch_sq = np.sqrt(max(r[3]["sigma"]**2 - r[4]["sigma"]**2, 0)); ch_s1 = np.sqrt(max(r[5]["sigma"]**2 - r[4]["sigma"]**2, 0))
    out["chain"]["sigma_sq"] = float(ch_sq); out["chain"]["sigma_s1"] = float(ch_s1)
    print(f"output chain: {r[3]['sigma']*1e12:.3f} ps raw, baseline {r[4]['sigma']*1e12:.3f} -> {ch_sq*1e12:.3f} ps (square), "
          f"{ch_s1*1e12:.3f} ps (1 V sine)", flush=True)
    # supply sensitivity K(f): DC point at 1 kHz, AC points, flat beyond 20 MHz (edges sample up to 25 MHz)
    sup = json.load(open(os.path.join(HERE, "data", "step76hv_supply.json")))
    def Kf(rail, vpp):
        pts = sorted((max(x["fm"], 1e3), abs(x["k"])) for x in sup if x["rail"] == rail and x["vpp"] == vpp)
        fx, kx = np.array(pts).T
        return lambda q: np.exp(np.interp(np.log(q), np.log(fx), np.log(kx)))
    fl = np.logspace(3, np.log10(25e6), 400)                # 1 kHz ... 25 MHz (f_ref/2)
    cases = {"3.3": (3.3, "square"), "1.0": (1.0, "sine"), "0.4": (0.4, "sine")}
    # white per-edge jitter = period jitter / sqrt 2 (independent edges). For the sines this equals the detrended
    # absolute jitter; for the square input the absolute value (0.13 ps) is dominated by a slow numerical wander of
    # the 10 ps time grid against 0.5 ns edges, which the period difference removes (0.034 ps)
    sig = {str(x["vpp"]): x["per"]/np.sqrt(2) for x in out["tn"]}
    # VDDD noise that keeps the VDDD term 10 dB under the -155 dBc/Hz chain target (3.3 V square, K at 1 MHz)
    K1 = Kf("vddd", 3.3)(1e6)
    out["vddd_max"] = float(np.sqrt(2*10**(-165/10)/(2*np.pi*FREF)**2)/K1)
    print(f"VDDD noise for -165 dBc/Hz: {out['vddd_max']*1e9:.0f} nV/rtHz (K_VDDD {K1*1e12:.0f} ps/V)", flush=True)
    out["L"] = {}; out["sys"] = {}
    for key, (vpp, wave) in cases.items():
        kv = "3.3" if vpp > 2 else "1.0"
        s_w = np.hypot(sig[key], out["chain"]["sigma_sq" if vpp > 2 else "sigma_s1"])
        # gate slope at the crossing: sine pi f V_pp x divider; square: V_pp over the 0.5 ns source edge x divider
        s = np.pi*FREF*vpp*div50 if wave == "sine" else vpp/0.5e-9*div50
        Slf = np.clip(np.exp(np.interp(np.log(fl), np.log(f), np.log(Sg))) - Swg, 1e-40, None)
        Lq = 10*np.log10((2*np.pi*FREF)**2/(2*s**2)*Slf)
        Lw = np.full_like(fl, 10*np.log10((2*np.pi*FREF*s_w)**2/FREF))
        terms = dict(white=Lw, slow=Lq)
        for cn in ("typ", "pess"):
            La = L_supply(fl, Kf("vdda", float(kv)), VN[cn]); Ld = L_supply(fl, Kf("vddd", float(kv)), VN[cn])
            rx = 10*np.log10(10**(Lw/10) + 10**(Lq/10) + 10**(La/10) + 10**(Ld/10))
            chainL = 10*np.log10(10**(rx/10) + 10**(pm.floor_L(fl, *CLKGEN)/10) + 10**(pm.floor_L(fl, *SSPDBUF)/10))
            out["L"][f"{key}_{cn}"] = dict(rx=rx.tolist(), vdda=La.tolist(), vddd=Ld.tolist(), white=Lw.tolist(), slow=Lq.tolist(),
                                          chain=chainL.tolist())
            fn = lambda q, c=chainL: np.interp(np.log(q), np.log(fl), c)
            out["sys"][f"{key}_{cn}"] = HS.system(cn, ref=fn)
            o = out["sys"][f"{key}_{cn}"]
            print(f"{key} V pp {cn}: rx floor {rx[-1]:.1f} (white {Lw[-1]:.1f}, VDDA {La[-1]:.1f}, VDDD {Ld[-1]:.1f}), "
                  f"rx L(1 kHz) {rx[0]:.1f}; system off {o['off']['total']:.2f} / on {o['on']['total']:.2f} ps, "
                  f"L300k {o['off']['L300k']:.1f} / {o['on']['L300k']:.1f}, ref chain {o['on']['terms'][HS.REFNAME]:.3f} ps", flush=True)
    out["fL"] = fl.tolist()
    o = HS.system("worst", ref=lambda q: np.interp(np.log(q), np.log(fl), out["L"]["3.3_pess"]["chain"]))
    out["sys"]["3.3_worst"] = o
    print(f"worst (ss/110 C, VDDA 2.97 V): off {o['off']['total']:.2f} / on {o['on']['total']:.2f} ps")
    json.dump(out, open(os.path.join(HERE, "data", "step76hv_noise.json"), "w"), default=float)
