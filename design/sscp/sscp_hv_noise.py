#!/usr/bin/env python3
"""sscp_hv_noise.py - the pulsed-Gm charge pump in the 800 MHz system (method M9, design/budget/hv_system.py).

Gm noise: the output current noise S_i(f) (.noise with the Gm connected to the filter) is gated with duty d = tau/T,
so the average current noise is d S_i; the detector converts phase into average current with beta = 2 A G d. The
equivalent phase noise at the detector input (in-loop, like detector noise, not x N^2):
    S_phi = d S_i / beta^2 = S_i / (4 A^2 G^2 d),   L = S_phi / 2
(the same as the budget model kT gamma/(A^2 g_m d) with S_i = 4 kT gamma g_m and G = g_m).
VDDA: a current Y v_dda reaches the filter only during the pulse -> phase error Y v / (2 A G):
    S_phi = |Y|^2 S_v / (2 A G)^2
REF chain and SSPD: the SSPD design. -> data/sscp_hv_noise.json"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
for q in ("design/budget", "models"):
    sys.path.insert(0, os.path.join(ROOT, q))
import hv_system as HS
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
SIM = J("design", "sscp", "data", "sscp_hv_sim.json")
S78 = J("design", "sspd", "data", "sspd_hv_noise.json")
T77 = J("design", "clkgen", "data", "clkgen_hv_sim.json")
VN = dict(typ=100e-9, pess=300e-9)
T = 20e-9

if __name__ == "__main__":
    fl = np.array(S78["fL"])
    G = next(r["G"] for r in SIM["dc"] if r["corner"] == "tt" and r["vc"] == 1.8 and r["code"] == "00")
    tau = next(r["tau"] for r in T77["timing"] if r.get("corner") == "tt" and r.get("temp") == 27 and r.get("vddd") == 1.8
               and r.get("vdda") == 3.3 and r.get("f") == 50e6 and r.get("wave") == "square")
    d = tau/T; A = S78["A_tt"]
    fn, n = np.array(SIM["noise"]["f"]), np.array(SIM["noise"]["n"])
    Si = lambda q: np.exp(np.interp(np.log(q), np.log(fn), np.log(n**2)))
    fy, y = np.array(SIM["psr"]["f"]), np.array(SIM["psr"]["y"])
    Y = lambda q: np.exp(np.interp(np.log(q), np.log(fy), np.log(np.maximum(y, 1e-30))))
    L_gm = lambda q: 10*np.log10(Si(q)/(4*A**2*G**2*d)/2)
    out = dict(G=G, tau=tau, d=d, A=A, beta=2*A*G*d, L_gm_1M=float(L_gm(1e6)), L_gm_10k=float(L_gm(1e4)), sys={})
    print(f"G {G*1e6:.2f} uS, tau {tau*1e12:.0f} ps, d {d:.4f}, A {A:.3f} V/rad -> beta {2*A*G*d*1e6:.3f} uA/rad; "
          f"Gm noise L {L_gm(1e4):.1f} (10 kHz) / {L_gm(1e6):.1f} (1 MHz) dBc/Hz", flush=True)
    for key in ("3.3", "1.0"):
        for cn in ("typ", "pess"):
            chain = np.array(S78["L"][f"{key}_{cn}"]["chain"])
            L_vd = lambda q, cn=cn: 10*np.log10(Y(q)**2*VN[cn]**2*(1 + 10e3/q)/(2*A*G)**2/2)
            pd = {"pulsed-Gm charge pump": L_gm, "VDDA into the Gm": L_vd}
            o = HS.system(cn, ref=lambda q, c=chain: np.interp(np.log(q), np.log(fl), c), pd=pd,
                          corner_over=dict(A=A if cn == "typ" else S78["A_min"], Cs=S78["Cs"]))
            out["sys"][f"{key}_{cn}"] = o
            print(f"{key} V pp {cn}: Gm {o['on']['terms']['pulsed-Gm charge pump']:.3f} ps, VDDA into Gm "
                  f"{o['on']['terms']['VDDA into the Gm']:.3f} ps; system off {o['off']['total']:.2f} / on {o['on']['total']:.2f} ps, "
                  f"L300k {o['off']['L300k']:.1f} / {o['on']['L300k']:.1f}", flush=True)
    chain = np.array(S78["L"]["3.3_pess"]["chain"])
    o = HS.system("worst", ref=lambda q: np.interp(np.log(q), np.log(fl), chain),
                  pd={"pulsed-Gm charge pump": L_gm,
                      "VDDA into the Gm": lambda q: 10*np.log10(Y(q)**2*VN["pess"]**2*(1 + 10e3/q)/(2*A*G)**2/2)},
                  corner_over=dict(A=S78["A_min"], Cs=S78["Cs"]))
    out["sys"]["3.3_worst"] = o
    print(f"worst: off {o['off']['total']:.2f} / on {o['on']['total']:.2f} ps")
    json.dump(out, open(os.path.join(HERE, "data", "sscp_hv_noise.json"), "w"), default=float)
