#!/usr/bin/env python3
"""Fill the step-77 HV doc sections that need the supply runs and the system model (RESULT, SUPPLY, SYSTEM, POWERREQ,
PROPOSAL) and the testbench-guide supply line. Run after step77hv_supply.py (both waveforms) and step77hv_noise.py."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
DOC = os.path.join(ROOT, "docs", "design", "step77_hv_clkgen.md"); GUIDE = os.path.join(ROOT, "docs", "testbench_guide.md")
J = lambda n: json.load(open(os.path.join(HERE, "data", n)))
SIM, SUP, SUP1, OLD, NZ = J("step77hv_sim.json"), J("step77hv_supply.json"), J("step77hv_supply_1v.json"), \
    J("step77hv_supply_via_vddd.json"), J("step77hv_noise.json")
tt = SIM["timing"][0]
k = lambda d, r: {x["fm"]: abs(x["k"])*1e12 for x in d if x["rail"] == r}
rng = lambda d, r: (min(k(d, r).values()), max(k(d, r).values()))
a3, d3, a1, d1, ao, do = rng(SUP, "vdda"), rng(SUP, "vddd"), rng(SUP1, "vdda"), rng(SUP1, "vddd"), rng(OLD, "vdda"), rng(OLD, "vddd")
S = NZ["sys"]; o, op, ow, o1, o1p = S["3.3_typ"], S["3.3_pess"], S["3.3_worst"], S["1.0_typ"], S["1.0_pess"]
L = NZ["L"]; last = lambda key, part: L[key][part][-1]
J_ = SIM["jitter"]

result = (f"The clock generator keeps its 1.8 V timing core on VDDD and drives the 5 V switches of the SSPD and the Gm with "
          f"0 / 3.3 V clocks. Pulses cross the supply domains as **edge pairs** (two rising steps through identical level "
          f"shifters, the pulse formed at the 3.3 V output gate), and the **sampling edge comes straight from the receiver's "
          f"3.3 V node refhv**, so it never passes a VDDD gate. At tt: sampling instant {tt['t_s']*1e12:.0f} ps after REF_IN, "
          f"cks/cksb skew {tt['skew_s']*1e12:.0f} ps, Gm pulse **τ = {tt['tau']*1e12:.0f} ps** (322–951 ps over 25 conditions; "
          f"τ·K_VCO 0.89–1.14 of nominal), gap 2 ≥ 108 ps, hold ≥ 1.84 ns, loop delay **t_p = {tt['t_p']*1e9:.2f} ns** "
          f"(≤ 1.45 ns). The sampling edge adds **{J_['sigma']*1e15:.0f} fs** ({J_['L_floor']:.1f} dBc/Hz) and moves "
          f"**{d3[1]:.1f} ps/V with VDDD** (was {do[1]:.0f} ps/V through refclk) and {a3[0]:.0f}–{a3[1]:.0f} ps/V with VDDA. "
          f"REF chain floor {last('3.3_typ', 'chain'):.1f} dBc/Hz (allocation −155). System with a 3.3 V square reference: "
          f"**{o['off']['total']:.2f} / {o['on']['total']:.2f} ps**, L(300 kHz) {o['off']['L300k']:.1f} / {o['on']['L300k']:.1f} "
          f"dBc/Hz (FFNC off / on, typ); worst {ow['off']['total']:.2f} / {ow['on']['total']:.2f} ps. Power **{tt['power']*1e3:.2f} mW** "
          f"(0.54–0.95 mW), 0.31 mW over its allocation. Seven cells, all LVS-clean.")

def ktab(d):
    rows = []
    for r in ("vdda", "vddd"):
        kk = k(d, r)
        rows.append(f"| {r.upper()} | " + " | ".join(f"{kk[f]:.1f}" for f in (0.0, 1e6, 5e6, 20e6)) + " |")
    return "\n".join(rows)
supply = (f"**Sensitivity of the sampling instant (ps/V), REF_IN → receiver → clock generator → cks:**\n\n"
          f"| Rail | DC | 1 MHz | 5 MHz | 20 MHz |\n|---|---|---|---|---|\n"
          f"| *3.3 V square reference* | | | | |\n{ktab(SUP)}\n| *1 V pp sine reference* | | | | |\n{ktab(SUP1)}\n"
          f"| *first version (edge via refclk), 3.3 V square* | | | | |\n{ktab(OLD)}\n\n"
          f"**What changed and why.**\n"
          f"- VDDD: {do[0]:.0f}–{do[1]:.0f} → **{d3[0]:.1f}–{d3[1]:.1f} ps/V**. Nothing in the sampling path runs from VDDD any "
          f"more; the small remainder couples in from the VDDD half of the shared receiver (not traced further at this size). "
          f"VDDD can carry any realistic noise: "
          f"{NZ['vddd_max']*1e6:.0f} µV/√Hz would still be below −165 dBc/Hz.\n"
          f"- VDDA: {ao[0]:.0f}–{ao[1]:.0f} → {a3[0]:.0f}–{a3[1]:.0f} ps/V. The edge now passes five VDDA gates "
          f"(S1, S2, three driver inverters) instead of S1 plus the 5 V driver, so it sees a little more of VDDA. "
          f"At 100 nV/√Hz this is a {last('3.3_typ', 'vdda'):.1f} dBc/Hz term, {-155 - last('3.3_typ', 'vdda'):.0f} dB under "
          f"the −155 dBc/Hz allocation (at 300 nV/√Hz: {last('3.3_pess', 'vdda'):.1f}).\n"
          f"- With the 1 V sine the receiver's S1 sees a slope 3.3× smaller, so its threshold moving with VDDA turns into "
          f"{a1[0]:.0f}–{a1[1]:.0f} ps/V; VDDD {d1[0]:.1f}–{d1[1]:.1f} ps/V.\n"
          f"- The delay is read where cks crosses VDDA/2 *at that instant*, because the SSPD switches are VDDA gates.")
def prow(name, key):
    t = L[key]; s = S[key]
    return (f"| {name} | {t['rx_white'][-1]:.1f} | {t['clkgen'][-1]:.1f} | {t['vdda'][-1]:.1f} | {t['vddd'][-1]:.1f} | "
            f"**{t['chain'][-1]:.1f}** | {s['off']['total']:.2f} / {s['on']['total']:.2f} | {s['off']['L300k']:.1f} / {s['on']['L300k']:.1f} |")
system = ("| Case | receiver S1 | clock gen | VDDA | VDDD | REF chain | jitter off / on (ps) | L(300 kHz) off / on |\n"
          "|---|---|---|---|---|---|---|---|\n" + "\n".join([prow("3.3 V square, typ", "3.3_typ"), prow("3.3 V square, pess", "3.3_pess"),
                                                             prow("1 V sine, typ", "1.0_typ"), prow("1 V sine, pess", "1.0_pess")]) +
          f"\n\nFloors in dBc/Hz at 50 MHz (white region). Worst case (3.3 V square, pess chain, worst corners): "
          f"{ow['off']['total']:.2f} / {ow['on']['total']:.2f} ps.\n\n"
          f"**Against the proposal** (typ 2.6 / 1.6 ps, −114 / −124 dBc/Hz; max 5.0 / 3.2 ps, −108 / −116 dBc/Hz): the typical "
          f"reference (3.3 V square) meets every typical value; the 1 V sine meets every maximum and the typical jitter "
          f"({o1['on']['total']:.2f} ps FFNC on), with L(300 kHz) {o1['on']['L300k']:.1f} dBc/Hz against −124 typical — as "
          f"agreed on 19 Nov, the typical column assumes the CMOS square.\n\n"
          f"**Reading it.** The clock generator ({last('3.3_typ', 'clkgen'):.1f}) and VDDA ({last('3.3_typ', 'vdda'):.1f}) are "
          f"now the largest REF-chain terms with a square input, still {-155 - last('3.3_typ', 'chain'):.0f} dB under the "
          f"allocation; with a 1 V sine the receiver's S1 dominates.")
powerreq = ("clock generator 0.72 mW typ (0.54–0.95) against 0.41 mW (0.08 core + 0.33 level shifters): +0.31 mW. Running "
            "total 9.13 + 0.03 (receiver) − 0.18 (CCO) + 0.31 = 9.29 mW typ (proposal 9.1, max 15); settled after step 79, "
            "when the SSPD and the Gm are measured.")
proposal = ("- **Timing, jitter, phase noise:** no change. Every typical and maximum value still holds (table in E).\n"
            "- **Architecture text:** already updated on 19 Nov (the sampling edge stays in the 3.3 V domain; VDDD carries no "
            "noise requirement).\n"
            "- **Power:** the typical rises from 9.13 to 9.29 mW with this step, against the proposal's 9.1 mW. Steps 78 and "
            "79 add the SSPD and the Gm; the power line is decided once, after step 79, with all three numbers measured, "
            "instead of being edited three times.")
s = open(DOC).read()
for kk_, v in dict(RESULT=result, SUPPLY=supply, SYSTEM=system, POWERREQ=powerreq, PROPOSAL=proposal).items():
    s = s.replace(f"@@{kk_}@@", v)
open(DOC, "w").write(s)
g = open(GUIDE).read()
g = g.replace("@@SUP77@@", f"VDDD {d3[1]:.1f} ps/V (was {do[1]:.0f} via refclk), VDDA {a3[0]:.0f}–{a3[1]:.0f} ps/V "
                           f"(3.3 V square) and {a1[0]:.0f}–{a1[1]:.0f} ps/V (1 V sine); REF chain {last('3.3_typ', 'chain'):.1f} dBc/Hz typ.")
open(GUIDE, "w").write(g)
print("filled; left:", s.count("@@"), g.count("@@SUP77@@"))
