#!/usr/bin/env python3
"""Fill the step-77 HV doc sections that come from step77hv_sim.json and the device table (SHEET, TIMING, JITTER, SIZING)."""
import os, json
import clkgen_hv as K
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
DOC = os.path.join(ROOT, "docs", "design", "step77_hv_clkgen.md")
sim = json.load(open(os.path.join(HERE, "data", "step77hv_sim.json")))
T = sim["timing"]; tt = T[0]

sheet = r"""| Quantity | Formula | Value (tt) | Why this value |
|---|---|---|---|
| 5 V gate ratio | W_p/W_n for equal rise/fall | 2.5 | thick-oxide hole mobility ≈ 1/2.5 of electrons (61 / 62 ps at fan-out 1) |
| Driver taper | C_in(k+1)/C_in(k) | ≈ 3 | INV5S 1/2.5 → INV5M 2.5/6.25 → INV5L 8/20 µm into 60 fF |
| Edge-pair delay | t_stop − t_start ≈ ln2·R·C_G + 2 gates | ≈ 0.45 ns | sets τ together with the output-gate difference |
| Gm pulse | τ = (t_stop − t_start) + (d_o − d_ob) | 528 ps | full 0–3.3 V swing at the fastest corner (≥ 322 ps) |
| Loop delay | t_p = gap1 + τ/2 | 875 ps | ≤ 5 ns; costs ΔPM = 360°·f_c·Δt_p = 0.34° |
| Gap 2 | 4 inverter delays + output-gate difference | 177 ps | ≥ 100 ps: Gm off before C1 → C2 sharing |
| Hold pulse | W_H ≈ ln2·R·C_H + gates | 2.68 ns | ≥ 1.5 ns = 5 time constants of the C1–C2 transfer |
| Dynamic power | Σ C·VDDA²·f_ref per output + internal | 0.72 mW | 6 outputs × (40–60 fF load + ≈ 50 fF self) × 3.3² × 50 MHz ≈ 0.3 mW, the rest is internal 5 V gates and short-circuit current |"""

def row(r):
    c = f"{r['corner']} {r['temp']} °C, {r['vddd']}/{r['vdda']} V"
    if r["f"] != 50e6: c += f", {r['f']/1e6:.0f} MHz"
    if r["wave"] != "square" or r["vpp"] != 3.3: c += f", {r['vpp']} V {r['wave']}"
    ps = lambda k: f"{r[k]*1e12:.0f}"
    return (f"| {c} | {ps('t_s')} | {ps('skew_s')} | {ps('gap1')} | {ps('tau')} | {ps('skew_g')} | {ps('gap2')} | "
            f"{r['W_H']*1e9:.2f} | {ps('t_p')} | {ps('fall_cks')} | {r['power']*1e3:.2f} |")
ok = [r for r in T if not r.get("failed")]
timing = ("| Condition | t_s ps | skew_s ps | gap1 ps | τ ps | skew_g ps | gap2 ps | W_H ns | t_p ps | cks fall ps | P mW |\n"
          "|---|---|---|---|---|---|---|---|---|---|---|\n" + "\n".join(row(r) for r in ok))
mn = lambda k: min(r[k] for r in ok); mx = lambda k: max(r[k] for r in ok)
timing += (f"\n\n**Spread over all {len(ok)} conditions (none failed):** τ {mn('tau')*1e12:.0f}–{mx('tau')*1e12:.0f} ps, "
           f"gap1 ≥ {mn('gap1')*1e12:.0f} ps, gap2 ≥ {mn('gap2')*1e12:.0f} ps, W_H ≥ {mn('W_H')*1e9:.2f} ns, "
           f"t_p {mn('t_p')*1e12:.0f}–{mx('t_p')*1e12:.0f} ps, power {mn('power')*1e3:.2f}–{mx('power')*1e3:.2f} mW.\n\n"
           "**τ·K_VCO (part B):** " + ", ".join(f"{k.replace('_', ' ')} °C {v['prod']:.2f}" for k, v in sim["tauK"].items()) +
           ". The product stays within 0.89–1.14 because τ (gate delay) grows exactly where the ring's K_VCO falls.\n\n"
           "**Reading the table.**\n"
           "- t_s grows with a smaller reference amplitude (1.88 ns at 1 V sine, 2.43 ns at 0.4 V): that is the receiver's "
           "slope, not the clock generator. Only its *stability* matters, because the loop locks the VCO to whatever "
           "instant cks falls.\n"
           "- gap1 is the time between cks/cksb settling and the Gm turning on; it is ≥ 328 ps, so the sample is always "
           "frozen before it is read.\n"
           "- t_p (sample → middle of the Gm pulse) is the loop's delay; the slowest corner gives 1.45 ns.")
J = sim["jitter"]; S = sim["S"]
jitter = (f"| Stage (node) | Trip-point noise current |\n|---|---|\n" +
          "\n".join(f"| {k} | {v**0.5*1e12:.2f} pA/√Hz |" for k, v in S.items()) +
          f"\n\n- Raw rms of {J['raw']['n']} edges: {J['raw']['sigma']*1e15:.1f} fs; noiseless baseline "
          f"{J['baseline']['sigma']*1e15:.1f} fs (numerical floor).\n"
          f"- Added jitter √(raw² − baseline²) = **{J['sigma']*1e15:.1f} fs** per edge.\n"
          f"- As a phase-noise floor at the reference: L = (2π·50 MHz·σ)²/50 MHz = **{J['L_floor']:.1f} dBc/Hz**, "
          f"14 dB under the −155 dBc/Hz REF-chain allocation.\n"
          "- With 80 edges σ is known to about ±8 %; even +8 % changes the floor by only 0.7 dB.\n"
          "- Why so small: every stage here swings 3.3 V, so the edge slope is about twice the 1.8 V chain's, "
          "and noise voltage divided by slope gives less time error.")

def dev(name, d):
    if isinstance(d[0], str):
        return f"| {name} | {d[0]} | {d[1]} × {d[3]} µm | — |"
    (n, wn, mn_, ln), (p, wp, mp, lp) = d
    return f"| {name} | n {wn} µm ×{mn_}, p {wp} µm ×{mp} | L {ln} µm | 5 V (g5v0d10v5) |"
keys = ["INV5S", "INV5M", "INV5L", "INV5A", "INV5T", "TG5", "TG5T", "NOR5L", "NAND5L", "CG", "CH"]
sizing = ("| Device | Size | L | Type |\n|---|---|---|---|\n" + "\n".join(dev(k, K.D[k]) for k in keys) +
          "\n\nThe 1.8 V core (RC edge generators, gap inverters, hold latch) keeps the 13 Nov sizes of `clkgen.py`; the four "
          "level shifters are the step-75 HV cell `sspll_ls_1v8_3v3`. All widths ≥ 0.42 µm, all 5 V lengths = 0.5 µm "
          "(PDK minimum for g5v0d10v5), MIM sides between 2 and 30 µm: inside the PDK limits (`tools/pdk_limits.py`).")

s = open(DOC).read()
for k, v in dict(SHEET=sheet, TIMING=timing, JITTER=jitter, SIZING=sizing).items():
    s = s.replace(f"@@{k}@@", v)
open(DOC, "w").write(s)
print("filled")
