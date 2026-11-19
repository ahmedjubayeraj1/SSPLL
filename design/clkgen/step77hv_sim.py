#!/usr/bin/env python3
"""step77hv_sim.py - verification of the 5 V-output clock generator (step 77 redo). -> data/step77hv_sim.json
A  timing over MOS x R/C corners, temperature, VDDD, VDDA, reference frequency, REF_IN amplitude and waveform (M16)
B  tau x K_VCO over corners (the loop sees the product; K_VCO from step 74 HV)                             (M16)
C  jitter the clock generator adds to the sampling edge (refhv -> cks falling, 5 V driver): transient noise with a
   white current of each stage's trip-point noise at the driver nodes and at refhv (S2), behind the real receiver
   (flat copy, noiseless input; S1's own white jitter is step 76's)                                          (M17)
Timing benches run with the real receiver in front (clkgen_hv.tran), so the reference input is a REF_IN waveform."""
import os, re, json, sys
import numpy as np
from multiprocessing import Pool
import clkgen_hv as K
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "refbuf"))
Q, W = (3.3, "square"), (1.0, "sine")
COND = [("tt", 27, 1.8, 3.3, 50e6) + Q, ("tt", 27, 1.71, 3.3, 50e6) + Q, ("tt", 27, 1.89, 3.3, 50e6) + Q,
        ("tt", 27, 1.8, 2.97, 50e6) + Q, ("tt", 27, 1.8, 3.63, 50e6) + Q,
        ("tt", -40, 1.8, 3.3, 50e6) + Q, ("tt", 110, 1.8, 3.3, 50e6) + Q,
        ("ss", 110, 1.71, 2.97, 50e6) + Q, ("ss", -40, 1.71, 2.97, 50e6) + Q,
        ("ff", -40, 1.89, 3.63, 50e6) + Q, ("ff", 110, 1.89, 3.63, 50e6) + Q,
        ("ss_hh", 110, 1.71, 2.97, 50e6) + Q, ("ss_hh", -40, 1.71, 2.97, 50e6) + Q,
        ("ff_ll", -40, 1.89, 3.63, 50e6) + Q, ("ff_ll", 110, 1.89, 3.63, 50e6) + Q,
        ("sf", 27, 1.8, 3.3, 50e6) + Q, ("fs", 27, 1.8, 3.3, 50e6) + Q,
        ("hl", 27, 1.8, 3.3, 50e6) + Q, ("lh", 27, 1.8, 3.3, 50e6) + Q,
        ("tt", 27, 1.8, 3.3, 45e6) + Q, ("tt", 27, 1.8, 3.3, 55e6) + Q,
        ("tt", 27, 1.8, 3.3, 50e6) + W, ("tt", 27, 1.8, 3.3, 50e6, 0.4, "sine"),
        ("ss", 110, 1.71, 2.97, 50e6, 0.4, "sine"), ("ff", -40, 1.89, 3.63, 50e6, 0.4, "sine")]
KVCO = {"tt": 1.0, "ss": 110/173, "ff": 250/173}    # step 74 HV: -173 / -110 / -250 MHz/V (tt / ss 110 C / ff -40 C)


def timing(a):
    c, t, vd, va, f, vpp, wave = a
    base = dict(corner=c, temp=t, vddd=vd, vdda=va, f=f, vpp=vpp, wave=wave)
    try:
        r = K.tran(c, t, vd, va, f, vpp, wave)
    except StopIteration:
        return dict(base, failed=True)
    return dict(base, **{k: float(v) for k, v in r.items()})


def stage_S(lines, vdd):
    import step76hv_noise as N
    return N.stage_noise(lines, vdd)


def path_noise():
    """White drain-noise current (A^2/Hz) at the trip point of S2 and of the sampling driver's stages."""
    p, m = K.D, K._m
    import refbuf as R
    inv = lambda size: m("n", "y", "a", "0", "0", size[0]) + m("p", "y", "a", "VDD", "VDD", size[1])
    jobs = dict(S2=(inv((R.D["N2"], R.D["P2"])), 3.3), INV5S=(inv(p["INV5S"]), 3.3), INV5M=(inv(p["INV5M"]), 3.3),
                INV5L=(inv(p["INV5L"]), 3.3))
    return {k: stage_S(*v)[0] for k, v in jobs.items()}


def jitter(a):
    """Receiver (flat top cell, step 76 HV) + the sampling driver's inverted path (flat: c1, c2, cks); trnoise currents
    at refhv (S2) and at c1, c2, cks. 3.3 V square reference, 80 edges at 50 MHz."""
    S, scale, seed, nedge = a
    import step76hv_noise as N, refbuf_hv as H, refbuf as R
    subs, body = N.flat_tail(); p, m = K.D, K._m
    inv = lambda nm, i, o, size: m(nm + "n", o, i, "VSS", "VSS", size[0]) + m(nm + "p", o, i, "VDDA", "VDDA", size[1])
    drv = inv("c", "refhv", "c1", p["INV5S"]) + inv("d", "c1", "c2", p["INV5M"]) + inv("e", "c2", "cks", p["INV5L"])
    nodes = dict(refhv="S2", c1="INV5S", c2="INV5M", cks="INV5L")
    nt = 4e-12; T = 20e-9; b = H.op()
    src = "".join(f"in_{n} 0 {n} dc 0 trnoise({scale*np.sqrt(S[sz]/(2*nt)):.4e} {nt} 0 0)\n" for n, sz in nodes.items())
    net = (f"* sampling edge jitter\n.lib {R.LIB} tt\n.temp 27\n{subs}{body}{drv}vss VSS 0 0\nvdda VDDA 0 3.3\n"
           f"vddd VDDD 0 1.8\niib ib 0 2.5e-6\nven pll_en 0 1.8\ncl refclk 0 50f\nccks cks 0 60f\n" +
           H.src(3.3, 3.3, 50e6, "square").replace("pad0", "REF_IN") + src +
           f".ic v(vin)={b['vin']} v(s1)={b['s1']}\n.options seed={seed}\n.control\nsave v(REF_IN) v(cks)\n"
           f"tran {nt} {(nedge + 20)*T} {20*T} {nt}\nwrdata w.txt v(REF_IN) v(cks)\n.endc\n.end\n")
    _, d = K.run(net, ["w.txt"])
    z = d["w.txt"]; t = z[:, 0]
    tr = K.xings(t, z[:, 1], 1.65, True); tf = K.xings(t, z[:, 3], 1.65, False)
    dly = np.array([tf[(tf > x) & (tf < x + 3e-9)][0] - x for x in tr[:-1] if np.any((tf > x) & (tf < x + 3e-9))])
    assert len(dly) > 0.9*nedge, f"only {len(dly)} edges"
    k = np.arange(len(dly)); dev = dly - np.polyval(np.polyfit(k, dly, 4), k)
    return dict(sigma=float(dev.std()), n=len(dly), mean=float(dly.mean()))


if __name__ == "__main__":
    res = {}
    only_timing = "--timing" in sys.argv          # rerun A and B only, keep the jitter result (C) of the last full run
    if only_timing:
        old = json.load(open(os.path.join(HERE, "data", "step77hv_sim.json")))
    with Pool(2) as pool:
        res["timing"] = pool.map(timing, COND)
    print("A done", flush=True)
    for r in res["timing"]:
        if r.get("failed"):
            print("  FAILED", r, flush=True); continue
        print(f"  {r['corner']:5s} {r['temp']:4d} C {r['vddd']}/{r['vdda']} V {r['f']/1e6:.0f} MHz {r['vpp']} V {r['wave']}: "
              f"t_s {r['t_s']*1e12:.0f} skew {r['skew_s']*1e12:.0f}/{r['skew_g']*1e12:.0f} gap1 {r['gap1']*1e12:.0f} tau {r['tau']*1e12:.0f} "
              f"gap2 {r['gap2']*1e12:.0f} W_H {r['W_H']*1e9:.2f} t_p {r['t_p']*1e12:.0f} fall_cks {r['fall_cks']*1e12:.0f} "
              f"P {r['p_vdda']*1e6:.0f}+{r['p_vddd']*1e6:.0f} uW", flush=True)
    tau = {(r["corner"], r["temp"]): r["tau"] for r in res["timing"] if not r.get("failed")}
    t0 = tau[("tt", 27)]
    res["tauK"] = {f"{c}_{t}": dict(tau=tau[(c, t)]/t0, K=KVCO[c[:2]], prod=tau[(c, t)]/t0*KVCO[c[:2]])
                   for c, t in (("ss", 110), ("ss", -40), ("ff", -40), ("ff", 110), ("ss_hh", 110), ("ff_ll", -40))}
    print("B", {k: round(v["prod"], 2) for k, v in res["tauK"].items()}, flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "step77hv_sim.json"), "w"), indent=1)   # checkpoint after A and B
    if only_timing:
        res.update(S=old["S"], jitter=old["jitter"])
        json.dump(res, open(os.path.join(HERE, "data", "step77hv_sim.json"), "w"), indent=1)
        raise SystemExit
    S = path_noise(); res["S"] = S
    print("C noise", {k: f"{np.sqrt(v)*1e12:.2f} pA/rtHz" for k, v in S.items()}, flush=True)
    with Pool(2) as pool:
        j = pool.map(jitter, [(S, 1.0, 1, 80), (S, 1e-6, 1, 80)])
    s = np.sqrt(max(j[0]["sigma"]**2 - j[1]["sigma"]**2, 0))
    res["jitter"] = dict(raw=j[0], baseline=j[1], sigma=float(s), L_floor=float(10*np.log10((2*np.pi*50e6*s)**2/50e6)),
                         note="S2 + sampling driver; S1's white jitter is step 76's")
    print(f"C jitter {s*1e15:.1f} fs (raw {j[0]['sigma']*1e15:.1f}, baseline {j[1]['sigma']*1e15:.1f}), floor {res['jitter']['L_floor']:.1f} dBc/Hz", flush=True)
    json.dump(res, open(os.path.join(HERE, "data", "step77hv_sim.json"), "w"), indent=1)
