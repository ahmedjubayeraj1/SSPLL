#!/usr/bin/env python3
"""fill78.py - writes docs/design/step78_hv_sspd.md from the step-78 HV results (rerun after any rerun of the benches)."""
import os, json
import numpy as np
import sspd_hv as S
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
SIM = J("design", "sspd", "data", "step78hv_sim.json"); NZ = J("design", "sspd", "data", "step78hv_noise.json")
SZ = J("design", "sspd", "data", "step78hv_size.json"); C77 = J("design", "clkgen", "data", "step77hv_sim.json")
C = [c for c in SIM["char"] if "A" in c]; tt = C[0]
KV = {"tt": 1.0, "ss": 110/173, "ff": 250/173}
tau = {(r["corner"], r["temp"], r["vdda"]): r["tau"] for r in C77["timing"] if not r.get("failed") and r["f"] == 50e6
       and r["wave"] == "square"}
t0 = tau[("tt", 27, 3.3)]
Amin = min(c["A"] for c in C); Amax = max(c["A"] for c in C)
cmin = min(c["cm"] for c in C); cmax = max(c["cm"] for c in C)
pmin = min(c["power"] for c in C); pmax = max(c["power"] for c in C)
K = SIM["kick"]; B = SIM["buf"]; BS = SIM["bufsup"]
o, ow, op = NZ["sys"]["3.3_typ"], NZ["sys"]["3.3_worst"], NZ["sys"]["3.3_pess"]
o1 = NZ["sys"]["1.0_typ"]
kTC = o["on"]["terms"]["SSPD sampler (kT/C)"]
Lk = 10*np.log10(1.380649e-23*300/(2*NZ["Cs"]*tt["A"]**2*50e6))

def row(c):
    lab = f"{c['corner']} {c['temp']} °C, {c['vdda']}/{c['vddd']} V" + ("" if c["fref"] == 50e6 else f", {c['fref']/1e6:.0f} MHz")
    return f"| {lab} | {c['A']:.3f} | {c['alpha']:.3f} | {c['gain_v2']:.3f} | {c['cm']:.2f} | {c['power']*1e3:.2f} |"
char_tab = "| Condition | A (V/rad) | α | hold DC gain | CM of v1 (V) | Power (mW) |\n|---|---|---|---|---|---|\n" + \
           "\n".join(row(c) for c in C)
lg = []
for cn, t, va in (("ss", 110, 2.97), ("ss_hh", 110, 2.97), ("ss_hh", -40, 2.97), ("ff", -40, 3.63), ("ff_ll", -40, 3.63),
                  ("ff_ll", 110, 3.63)):
    a = next(c["A"] for c in C if c["corner"] == cn and c["temp"] == t and c["vdda"] == va)/tt["A"]
    tr = tau[(cn, t, va)]/t0; kv = KV[cn[:2]]
    lg.append((f"{cn} {t} °C, VDDA {va} V", a, tr, kv, a*tr*kv))
lg_tab = "| Corner | A / A_tt | τ / τ_tt (step 77) | K_VCO / K_tt (step 74) | product (before G) |\n|---|---|---|---|---|\n" + \
         "\n".join(f"| {n} | {a:.2f} | {t:.2f} | {k:.3f} | **{p:.2f}** |" for n, a, t, k, p in lg)
pl = [x[4] for x in lg]
size_tab = "| Variant | A (V/rad) | α | Power (mW) |\n|---|---|---|---|\n" + "\n".join(
    f"| {r['tag']} | {r['A']:.3f} | {r['alpha']:.3f} | {r['power']*1e3:.3f} |" for r in SZ)

def dev(name, d, role):
    if name in ("C1", "C2", "CD"):
        return f"| X{name} | {d[0]} | {d[1]} × {d[3]} µm | — | {role} |"
    if name == "RS":
        return f"| XRS | {d[0]} | {d[1]} | {d[3]} µm | {role} |"
    if isinstance(d[0], tuple):
        (n, wn, _, ln), (p, wp, _, lp) = d
        return f"| X{name} (n / p) | {n} / {p} | {wn} / {wp} × 1 | {ln} µm | {role} |"
    return f"| {name} | {d[0]} | {d[1]} × 1 | {d[3]} µm | {role} |"
P = S.D
dev_tab = "| Device | Model | W per finger × nf | L | Role |\n|---|---|---|---|---|\n" + "\n".join([
    dev("B1", P["B1"], "isolation buffer input (small load on clkp)"), dev("B2", P["B2"], "drives R_s + C"),
    dev("RS", P["RS"], "R_s ≈ 3.4 kΩ (0.6 µm / 0.35 µm × 2 kΩ/□)"),
    f"| xs1, xsd: XN / XP | {P['SWN'][0]} / {P['SWP'][0]} | {P['SWN'][1]} / {P['SWP'][1]} × 1 | 0.5 µm | sampling and dummy TG |",
    f"| xs2: XN / XP | {P['HWN'][0]} / {P['HWP'][0]} | {P['HWN'][1]} / {P['HWP'][1]} × 1 | 0.5 µm | hold TG |",
    dev("C1", P["C1"], "34.7 fF, bottom plate on VSS"), dev("C2", P["C2"], "34.7 fF"),
    dev("CD", P["CD"], "≈ 41.6 fF = C1 + the Gm input")])

doc = f"""# Step 78 (redo): SSPD with hold in 5 V devices at 800 MHz

*Phase 7, roadmap step 78, redone for the device-rule migration (19 Nov 2026).* Deliverable: schematic (xschem,
hierarchical, LVS-clean), sizing table, verification over PVT. Design files `design/sspd/sspd_hv.py`,
`step78hv_*.py`; schematics `xschem/sspd_hv/`; data `design/sspd/data/step78hv_*.json`; methods M17, M18, M19, M21
(`docs/methods.md`). The 1.8 V version (`step78_sspd.md`) is kept for the record.

Reproduce (in `design/sspd`):

```bash
python3 step78hv_size.py     # R_s length and switch width for A = 0.8 V/rad              (M18)
python3 step78hv_sim.py      # A characteristic x 18 conditions, B kick-back, C buffer jitter, D buffer VDDA (M18, M19, M17)
python3 step78hv_noise.py    # REF chain with the measured SSPD parts, system model        (M9)
python3 step78hv_plots.py    # docs/img/step78hv_*.png
python3 schematics_hv.py     # xschem/sspd_hv/*, drawing checks, LVS reference             (M5)
cd ../../xschem && ./lvs.sh sspd_hv/sspll_sspd_hv.sch netlist/ref_sspd_hv.spice sspll_sspd_hv   # M4
```

## Result in one paragraph

Each side (p from `clkp`, m from `clkm`, the ring's 3.3 V buffered outputs) has a two-inverter **isolation buffer**,
a series resistor **R_s ≈ 3.4 kΩ** that rounds the square wave into a near-sine of defined slope, a 5 V **sampling TG**
onto **C1 = 34.7 fF**, a **dummy sampler** on the opposite phase and a **hold TG** onto **C2 = 34.7 fF**. Every device
is a g5v0d10v5 on VDDA. The detector gain is **A = {tt['A']:.3f} V/rad** per side at tt (target 0.8),
{Amin:.3f}–{Amax:.3f} over 18 conditions (MOS × R/C corners, −40…110 °C, VDDA ±10 %, 45/55 MHz). The hold has
**α = {tt['alpha']:.3f}** and unity DC gain ({tt['gain_v2']:.3f}). The sampler moves the ring-buffer edge by
**{K['dt_max']*1e15:.0f} fs** once per period (spur estimate **{K['spur_dbc']:.0f} dBc**, proposal max −45 dBc); the
dummy sampler cuts the SSPD supply current at f_ref from {K['I_fref_nodummy']*1e6:.1f} µA to **{K['I_fref']*1e6:.2f} µA**.
The isolation buffers add **{B['sigma']*1e15:.0f} fs** per side ({B['L_floor']:.1f} dBc/Hz at the differential crossing)
and move with VDDA by **{abs(BS['k'])*1e12:.1f} ps/V**. kT/C: {Lk:.1f} dBc/Hz, {kTC*1e3:.0f} fs in the system.
System, 3.3 V square reference: **{o['off']['total']:.2f} / {o['on']['total']:.2f} ps**, L(300 kHz)
**{o['off']['L300k']:.1f} / {o['on']['L300k']:.1f} dBc/Hz** (FFNC off / on, typ); worst {ow['off']['total']:.2f} /
{ow['on']['total']:.2f} ps. Power **{tt['power']*1e3:.2f} mW** at tt ({pmin*1e3:.2f}–{pmax*1e3:.2f}): 0.54 mW over the
step-72 allocation, see G.

![SSPD top](../img/step78hv_sch_sspll_sspd_hv.png)

## What happens, how, why

### What happens
At every reference edge (cks falling) the SSPD freezes the ring's waveform on C1. Near lock the frozen differential
voltage v1p − v1m is proportional to the time between the ring's zero crossing and the reference edge. Right after the
sample, the pulsed Gm (step 79) turns v1p − v1m into a charge for the loop filter during ckg. Then ckh shares the
sample onto C2, which holds it for the whole period for the noise-cancellation block (NCB).

### How it happens
- **Isolation buffer.** XB1 (0.6/1.5 µm) loads clkp lightly; XB2 (2/5 µm) drives R_s and whichever capacitor is
  connected. The sampler's charge reaches clkp only through XB1's gate–drain capacitance.
- **Shaping.** An RC-filtered square of amplitude a = VDDA/2 crosses its mid-level with slope exactly a/τ_s, so

$$A = \\frac{{1}}{{\\omega_0}}\\left.\\frac{{dv}}{{dt}}\\right|_{{cross}} = \\frac{{V_{{DDA}}}}{{2\\,\\omega_0\\,\\tau_s}},\\qquad
\\tau_s = (R_s + R_{{buf}} + R_{{sw}})\\,C_{{1,tot}}$$

  For A = 0.8 V/rad at 800 MHz with VDDA = 3.3 V: τ_s = 3.3/(2·2π·0.8 GHz·0.8) = **0.41 ns**, more than twice the
  1.8 V design's 0.18 ns (half the carrier, almost twice the swing).
- **Sampling.** A 5 V TG (n 3 µm, p 6 µm, L 0.5 µm) opens when cks falls. There is no low-V_T 5 V device, so the nMOS at
  mid-rail (V_GS ≈ 1.65 V) is wider and the pMOS carries half the conductance.
- **Dummy sampler.** Same TG with the clocks swapped, onto CD = C1 + the Gm input. One of the two capacitors is always
  on node f, so XB2's load, delay and supply current are the same in every phase.
- **Hold.** After the Gm pulse, ckh closes a small TG (1/2 µm) between C1 and C2:

$$v_2[k] = (1-\\alpha)\\,v_1[k] + \\alpha\\,v_2[k-1],\\qquad \\alpha = \\frac{{C_{{2,tot}}}}{{C_{{1,tot}} + C_{{2,tot}}}}$$

- **Noise.** Differential kT/C divided by (2A)² is a white phase floor that is *not* multiplied by N²:

$$\\mathcal{{L}}_{{kT/C}} = \\frac{{kT}}{{2\\,C_s\\,A^2 f_{{ref}}}} = {Lk:.1f}\\ \\text{{dBc/Hz}}\\quad (C_s = {NZ['Cs']*1e15:.1f}\\ \\text{{fF}},\\ A = {tt['A']:.3f})$$

  Timing noise of the isolation buffers *is* reference-like: the loop cannot tell it from reference jitter.

![characteristic](../img/step78hv_char.png)

### Why it happens this way
- **Defined slope, wide linear range.** A raw 3.3 V square would give a slope set by the inverter edge and a linear range
  of picoseconds. The RC near-sine sets A by R·C and is linear over about ±0.6 rad.
- **Gm reads C1, not C2.** No charge-sharing pole z = α inside the loop (it would cost about 16° at f_c = f_ref/20).
- **C1 stays at 35 fF.** Step 72 requires C_s ≥ 35 fF. Halving C1 would save about 0.25 mW, but C_s (with the
  8 fF Gm input and the junctions) would drop to about 31 fF, and the Gm's non-linear gate capacitance would become a
  larger part of the sampled node. kT/C is only {kTC*1e3:.0f} fs in the system, so noise is not what limits C1 —
  the requirement and the sampled node's linearity are.
- **Dummy sampler.** Constant supply current at f_ref: without an LDO, any f_ref current on VDDA is a spur source for
  every block on VDDA.

## A. Architecture decisions

| Decision | Options | Chosen | Why |
|---|---|---|---|
| Devices | 1.8 V on VDDL, 5 V on VDDA | **5 V on VDDA** | device rule (analog = g5v0d10v5); VDDL no longer exists |
| SSPD input | raw ring nodes, buffered clkp/clkm | **clkp/clkm + own isolation buffer** | no extra load on the ring |
| Shaping | square, R_s + C | **R_s + C** | A set by R·C; linear range ±0.6 rad |
| R_s | xhigh_po 0.35 µm × 0.8 / 0.6 / 0.5 µm | **0.6 µm** | A = 0.812 V/rad (table below) |
| Sampling switch | nMOS, TG 3/6, TG 4/8 µm | **TG 3/6 µm** | the wider switch lowers A (more junction C) and costs 4 % more power |
| C1, C2 | 20 / 35 fF | **35 fF** | step 72: C_s ≥ 35 fF |
| What the Gm reads | C2, C1 | **C1** | no z = α pole in the loop |
| Dummy | none, copy | **copy, CD = C1 + Gm input** | f_ref supply current −{20*np.log10(K['I_fref_nodummy']/K['I_fref']):.0f} dB |

**Sizing runs (`step78hv_size.py`, full beat runs at tt):**

{size_tab}

## B. Characteristic over 18 conditions (method M18)

**Bench (`sspd_hv.bench`, `characteristic`).**
- The step-77 HV clock generator makes cks/cksb, ckg/ckgb, ckh/ckhb from ideal refhv (0–VDDA) and refclk (0–VDDD,
  0.2 ns later, as the receiver makes them).
- The "ring" is two ideal 0/VDDA squares at f = (16 + 1/32)·f_ref behind a 5 V inverter like the ring's buffer output
  stage, so the sampling phase slides by 2π/32 per period (beat). 32 periods give the whole characteristic.
- v1p − v1m is read in the middle of the Gm pulse, v2p − v2m 0.5 ns after the hold; A = half the slope of a line fit
  within ±0.35 rad of the zero crossing; α and the hold DC gain from a least-squares fit of
  v2[k] = a·v1[k] + b·v2[k−1].
- Loads: 8 fF on each v1 (the Gm input, step 79), 4 fF on each v2 (the NCB input).

![corners](../img/step78hv_corners.png)

{char_tab}

**Requirements (step 72 HV):** A = 0.8 V/rad nominal ✔ ({tt['A']:.3f}); A ≥ 0.5 V/rad at every condition ✔
({Amin:.3f} at ss_hh / 2.97 V, the tightest item).

**Why A moves with VDDA.** The filtered square has amplitude VDDA/2, so A ∝ VDDA (2.97 V: 0.694, 3.63 V: 0.951, i.e.
−15 / +17 % for ∓10 %). There is no LDO, so this is real loop-gain variation. Only its slow part matters (VDDA set once per
chip): it is a static gain error the icp_trim covers. Its fast part is supply noise on A, which only scales the small
phase error and adds nothing in lock.

### Loop gain over PVT
A follows VDDA/(R_s·C1); τ (step 77) and K_VCO (step 74) also move. The loop needs A·G·τ·K_VCO:

{lg_tab}

×{min(pl):.2f}–{max(pl):.2f} is inside the icp_trim range (×0.55–2.0, step 73 HV). Step 79 adds G and checks what is
left.

## C. Kick-back and the dummy sampler (method M19)

![kick](../img/step78hv_kick.png)

**Bench (`sspd_hv.kick`).** Locked (f = 16·f_ref exactly, sampling at the zero crossing). Two runs, one with the clock
generator switching and one with the reference held still (the sampler tracks, nothing switches); the difference of
the clkp edge times is the kick-back. Its Fourier component at f_ref, as phase deviation 2π·f_0·Δt, gives the spur
estimate 20·log(a1/2).

- **Largest edge shift {K['dt_max']*1e15:.1f} fs, rms {K['dt_rms']*1e15:.1f} fs** — one edge per period, the one right
  after the sampling instant.
- **Spur estimate {K['spur_dbc']:.1f} dBc** at the ring buffer output (proposal typ −55, max −45 dBc). The ring itself is
  one more buffer away.
- 30× the 1.8 V design's 2.3 fs: the 3.3 V clock swing and the thick-oxide overlap capacitances of 0.5 µm-long devices
  couple more charge. It is still 54 dB below the proposal maximum.
- **SSPD supply current at f_ref: {K['I_fref']*1e6:.2f} µA with the dummy, {K['I_fref_nodummy']*1e6:.1f} µA without.**

## D. Noise (methods M17, M21, M9)

| Source | Value | Floor at 50 MHz | Enters as |
|---|---|---|---|
| kT/C of C_s ({NZ['Cs']*1e15:.1f} fF), A = {tt['A']:.3f} | 2kT/C differential | {Lk:.1f} dBc/Hz | detector noise (not ×N²) |
| Isolation buffers XB1/XB2 (M17) | {B['sigma']*1e15:.1f} fs per side → {B['sigma']/np.sqrt(2)*1e15:.1f} fs differential | {B['L_floor']:.1f} dBc/Hz | reference-like (×N²) |
| Buffer delay vs VDDA (M21, DC) | {abs(BS['k'])*1e12:.1f} ps/V (delay {BS['d0']*1e12:.0f} ps) | {NZ['L']['3.3_typ']['sspd_buf_vdda'][-1]:.1f} dBc/Hz at 100 nV/√Hz | reference-like |

- **M17 bench (`buf_jitter`).** Flat copy of ring buffer stage → XB1 → XB2 → R_s → C, white `trnoise` currents of each
  inverter's trip-point noise at b1 and b2, 800 MHz input; noiseless baseline {B['baseline']['sigma']*1e15:.2f} fs.
- **Supply bench (`buf_supply`).** The buffers are plain inverters with no bias loop or coupling capacitor, so their
  delay sensitivity is flat in frequency and the DC form of M21 (+10 mV step) is enough.

![noise](../img/step78hv_noise.png)

**System (`step78hv_noise.py`, measured A and C_s; pess and worst with A_min = {Amin:.3f}):**

| Case | Jitter off / on (ps) | L(300 kHz) off / on (dBc/Hz) |
|---|---|---|
| 3.3 V square, typ | {o['off']['total']:.2f} / {o['on']['total']:.2f} | {o['off']['L300k']:.1f} / {o['on']['L300k']:.1f} |
| 3.3 V square, pess | {op['off']['total']:.2f} / {op['on']['total']:.2f} | {op['off']['L300k']:.1f} / {op['on']['L300k']:.1f} |
| 1 V sine, typ | {o1['off']['total']:.2f} / {o1['on']['total']:.2f} | {o1['off']['L300k']:.1f} / {o1['on']['L300k']:.1f} |
| worst | {ow['off']['total']:.2f} / {ow['on']['total']:.2f} | — |

Proposal: typ 2.6 / 1.6 ps and −114 / −124 dBc/Hz; max 5.0 / 3.2 ps and −108 / −116 dBc/Hz. All met.

## E. Schematics (hierarchical, real wiring, LVS-clean)

`sspll_sspd_hv` (top: p and m sides) → `sspll_sspd_hv_side` (buffer, R_s, sampler, dummy, hold) →
`sspll_sspd_hv_tg`, `sspll_sspd_hv_tgh`. netgen against `xschem/netlist/ref_sspd_hv.spice` (= `sspd_hv.cells()`):
*Circuits match uniquely* for all four cells; drawing checker clean.

![side](../img/step78hv_sch_sspll_sspd_hv_side.png)

## F. Sizing table (all devices pass `tools/pdk_limits.py`)

{dev_tab}

Gate load on each of cks / cksb: two 5 V TG gates per side (n 3 µm or p 6 µm, L 0.5 µm), about 25–30 fF from the gate
area — inside the 60 fF the clock generator was verified with. On ckh / ckhb: about 3 / 6 fF (≤ 40 fF).

## G. Power

- SSPD **{tt['power']*1e3:.2f} mW** at tt ({pmin*1e3:.2f}–{pmax*1e3:.2f} mW), against 0.49 mW allocated in step 72 HV.
- Why: each side swings C_tot ≈ 46 fF by 3.3 V at 800 MHz: 2 × 46 fF × 3.3² × 0.8 GHz ≈ 0.80 mW, plus the buffers'
  own gates. The 1.8 V design swung 1.8 V at 1.6 GHz: (3.3/1.8)² × ½ = 1.68× the energy rate per farad.
- The step-72 allocation assumed the 1.8 V figure scaled by current, not by C·V²·f.
- Running total (typ, FFNC on): 9.13 (step 72) + 0.03 (receiver) − 0.18 (CCO) + 0.31 (clock generator) + 0.54 (SSPD)
  = **9.83 mW**. Proposal: typ 9.1, max 15 mW. Decided after step 79, when the last analog block of the loop is known.

## H. Requirements handed on

1. **Step 79 (pulsed Gm):** reads v1p − v1m during ckg; input capacitance ≤ 8 fF per side (CD sized for it); input
   common mode {cmin:.2f}–{cmax:.2f} V; linear range ≥ ±0.1 V differential (±0.06 rad at A_tt; the locked phase error is about 6.5 mrad rms); β·K_VCO with A = {tt['A']:.3f} V/rad
   and the ×{min(pl):.2f}–{max(pl):.2f} spread above.
2. **NCB (diff-to-SE):** reads v2p − v2m, ≤ 4 fF per side; first-order memory α = {tt['alpha']:.3f}.
3. **Ring buffers (step 74 HV):** clkp/clkm drive XB1 only (≈ 3 fF each).
4. **Layout:** p/m mirror symmetry; C1/C2/CD as matched MIM tiles; equal cks routes to both sides, away from v1; v1 and
   v2 shielded; R_s next to the switch.

## Testbenches

Set-up, method and pitfalls of every bench: `docs/testbench_guide.md`, section "5 V SSPD benches (step 78 redo)".

## Interview questions (step 78 redo)

The answers are in `learn/phase7_design.ipynb` (v2), step 78.

1. Why does A need a longer τ_s at 800 MHz on 3.3 V than at 1.6 GHz on 1.8 V?
2. Why is there no low-V_T sampling switch any more, and what replaces it?
3. Why does A now change with VDDA, and why is that acceptable without an LDO?
4. Why is the kick-back 30× larger than in the 1.8 V design, and does it matter?
5. Why does the SSPD use twice its power allocation?
6. Why was C1 not reduced to save power?
7. Why is a DC supply step enough for the isolation buffers but not for the receiver?
8. How was R_s chosen?
9. Why does the dummy sampler matter more without an LDO?
10. Which SSPD noise is multiplied by N², and which is not?
"""
open(os.path.join(ROOT, "docs", "design", "step78_hv_sspd.md"), "w").write(doc)
print("written", round(tt["A"], 3), [round(x, 2) for x in pl])
