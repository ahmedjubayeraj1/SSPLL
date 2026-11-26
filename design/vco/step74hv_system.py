#!/usr/bin/env python3
"""step74hv_system.py - what the step-74 ring (hl6) does to the system: K_VCO -> Gm unit (beta*K_VCO fixed by step 73),
ring phase noise -> step-72 HV jitter budget (with the step-73 filter), ring + buffer power -> power budget and FoM.
Run after step74hv_point.py hl6 and step74hv_char.py hl6.  -> data/step74hv_system.json"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "design", "budget")); sys.path.insert(0, os.path.join(ROOT, "models"))
import step72_hv_budget as bud
n = json.load(open(os.path.join(HERE, "data", "step74hv_hl6.json")))
c = json.load(open(os.path.join(HERE, "data", "step74hv_char_hl6.json")))
L73 = json.load(open(os.path.join(ROOT, "design", "loop", "data", "step73_hv_design.json")))

# K_VCO over the V_cont window. Step 73 assumed 1.0-2.3 V; the switch only starts to conduct above about 1.2 V
# (thick-oxide V_T plus body effect), so f is flat below 1.3 V: the window is moved to 1.3-2.3 V (step 74 decision).
K = {}; K_old = {}
for k, v in c["f_vs_vtune"].items():
    f = {x: fx for x, fx, _ in v}
    K[k] = (f[2.3] - f[1.3])/1.0; K_old[k] = (f[2.3] - f[1.0])/1.3
Ktt = K["tt_27"]
gm_unit = L73["gm"]/3*abs(150e6/Ktt)          # beta*K_VCO fixed: g_m scales with 150 MHz/V / |K_VCO|
I = n["I"]; P_ring = I*9/8*3.3
b = c["buffer"]["tt_27"]["running"][0]; P_buf = 2*b*3.3      # two active buffers (clkp, clkm); four dummies have no supply
RING = "ring VCO core (5 V, 3-stage)"
res = {}
for corner, over in (("typ", {RING: (n["Lth"], n["fc3"])}), ("pess", {RING: (n["Lth"] + 3, 2*n["fc3"])})):
    for on in (False, True):
        f, S = bud.spectra(corner, on, over=over, lf=(L73["R"], L73["C1"], L73["C2"]))
        j, L = bud.jitter(S, f)
        res[f"{corner}_{'on' if on else 'off'}"] = dict(jit=j["TOTAL"]*1e12, ring=j[RING]*1e12,
                                                         L300k=float(L[np.argmin(abs(f - 3e5))]), L1M=float(L[np.argmin(abs(f - 1e6))]))
# power: replace the ring and buffer rows of the step-72 HV table with the measured values
rows = bud.power_table()
p_on = sum(p for _, _, _, p, _, _ in rows) - rows[0][3] - rows[1][3] + P_ring*1e3 + P_buf*1e3
p_off = p_on - [p for name, _, _, p, _, ncb in rows if ncb][0]
fom = 10*np.log10((res["typ_on"]["jit"]*1e-12)**2*p_on)
out = dict(K=K, K_old_window=K_old, gm_unit=gm_unit, I=I, P_ring_mW=P_ring*1e3, P_buf_mW=P_buf*1e3, I_buf=b, budget=res, P_on=p_on, P_off=p_off, FoM=fom,
           Lth=n["Lth"], fc3=n["fc3"])
json.dump(out, open(os.path.join(HERE, "data", "step74hv_system.json"), "w"), indent=1)
print("K_VCO (MHz/V, 1.3-2.3 V):", {k: round(v/1e6, 1) for k, v in K.items()}, " | over 1.0-2.3 V:", {k: round(v/1e6, 1) for k, v in K_old.items()})
print(f"Gm unit {gm_unit*1e6:.2f} uS (step 73: {L73['gm']/3*1e6:.2f} uS at 150 MHz/V)")
print(f"ring {I*1e3:.3f} mA -> {P_ring*1e3:.2f} mW from VDDA (budget 4.86); buffers 2 x {b*1e6:.0f} uA -> {P_buf*1e3:.2f} mW (budget 0.99)")
for k, v in res.items():
    print(f"  {k}: jitter {v['jit']:.2f} ps (ring {v['ring']:.2f}), L(300k) {v['L300k']:.1f}, L(1M) {v['L1M']:.1f}")
print(f"power FFNC on {p_on:.2f} mW, off {p_off:.2f} mW; FoM {fom:.1f} dB")
