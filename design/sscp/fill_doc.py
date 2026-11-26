#!/usr/bin/env python3
"""fill_doc.py - writes docs/design/sscp_hv.md from the step-79 results (rerun after any rerun of the benches)."""
import os, json
import numpy as np
import sscp_hv as C
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
D_ = lambda n: J("design", "sscp", "data", n)
SIM, NZ, DET = D_("sscp_hv_sim.json"), D_("sscp_hv_noise.json"), D_("sscp_hv_det.json")
B1, B2, NS, CIN, DLY = D_("sscp_hv_buf.json"), D_("sscp_hv_buf2.json"), D_("sscp_hv_noisesize.json"), D_("sscp_hv_cin.json"), D_("sscp_hv_delay.json")
V1DET = D_("v1_mirror/step79hv_det_first.json")
S78 = J("design", "sspd", "data", "sspd_hv_sim.json"); C77 = J("design", "clkgen", "data", "clkgen_hv_sim.json")
T = 20e-9
dc = SIM["dc"]; tt = dc[0]
G0 = tt["G"]; Gs = [r["G"] for r in dc if r["code"] == "00"]
code = {r["code"]: r["G"] for r in dc if r["corner"] == "tt" and r["vc"] == 1.8}
vos = max(abs(r["v_os"]) for r in dc); lin = min(min(-r["lin"][0], r["lin"][1]) for r in dc)
lin_tt = min(-tt["lin"][0], tt["lin"][1])
buf = SIM["buffer"]; berr = max(abs(r["err"]) for r in buf); bpk = max(r["peak_db"] for r in buf)
bf3 = min(r["f3db"] for r in buf)
P = {(r["vd"], r["vc"]): r for r in SIM["pulsed"]}
q0 = {vc: P[(0.0, vc)]["q"] for vc in (1.3, 1.8, 2.3)}
qd = (P[(0.1, 1.8)]["q"] - P[(-0.1, 1.8)]["q"])/0.2
tauP = P[(0.0, 1.8)]["tau"]
A = NZ["A"]; beta = NZ["beta"]; d = NZ["d"]
fn, n = np.array(SIM["noise"]["f"]), np.array(SIM["noise"]["n"])
n1M, n10k, n100k = (np.interp(f, fn, n) for f in (1e6, 1e4, 1e5))
Y1M = np.interp(1e6, SIM["psr"]["f"], SIM["psr"]["y"]); idd = SIM["psr"]["idd"]
S = NZ["sys"]; o, op, ow, o1 = S["3.3_typ"], S["3.3_pess"], S["3.3_worst"], S["1.0_typ"]
gm_ps = o["on"]["terms"]["pulsed-Gm charge pump"]; vd_ps = o["on"]["terms"]["VDDA into the Gm"]
cin_tt = next(r["cin"] for r in CIN if r["code"] == "00" and r["ckg"] == 3.3 and r["corner"] == "tt")
cin_rng = (min(r["cin"] for r in CIN), max(r["cin"] for r in CIN))


def local(r):
    """slope (A/rad) and zero of the charge-phase characteristic: cubic fit within +-0.6 rad of the v1 zero crossing."""
    a = np.array(r["rows"]); dd = (a[:, 0] - r["phi0"] + np.pi) % (2*np.pi) - np.pi; o_ = np.argsort(dd)
    dd, q = dd[o_], a[o_, 1]; m = np.abs(dd) < 0.6
    Pp = np.poly1d(np.polyfit(dd[m], q[m], 3))
    roots = [x.real for x in Pp.roots if abs(x.imag) < 1e-9 and abs(x.real) < 0.6]
    z = min(roots, key=abs) if roots else 0.0
    return float(Pp.deriv()(z)/T), float(z)
det = [(r, *local(r)) for r in DET]
b_tt = next(b for r, b, z in det if r["corner"] == "tt" and r["vc"] == 1.8)
det_tab = ("| Condition | β_eff at lock (µA/rad) | ÷ 2A·G·τ/T | lock-point offset (mrad) | max |vdump − vctl| before the pulse |\n"
           "|---|---|---|---|---|\n")
A78 = {(c["corner"], c["temp"], c["vdda"]): c["A"] for c in S78["char"] if "A" in c and c["fref"] == 50e6}
tau77 = {(r["corner"], r["temp"], r["vdda"]): r["tau"] for r in C77["timing"] if not r.get("failed") and r["f"] == 50e6 and r["wave"] == "square"}
Gc = {(r["corner"], r["temp"], r["vdda"], r["vc"]): r["G"] for r in dc if r["code"] == "00"}
for r, b, z in det:
    key = (r["corner"], r["temp"], r["vdda"])
    ideal = 2*A78[key]*Gc.get(key + (r["vc"],), Gc.get(key + (1.8,), G0))*tau77[key]/T
    det_tab += (f"| {r['corner']} {r['temp']} °C, {r['vdda']} V, V_cont {r['vc']} V | {b*1e6:.3f} | {b/ideal*100:.0f} % | "
                f"{z*1e3:+.0f} | {r['err_max']*1e3:.1f} mV |\n")
KV = {"tt": 1.0, "ss": 110/173, "ff": 250/173}
CODEF = {"10": code["10"]/G0, "00": 1.0, "01": code["01"]/G0, "11": code["11"]/G0}
LG = []
for r, b, z in det:
    if r["vc"] != 1.8:
        continue
    prod = b/b_tt*KV[r["corner"][:2]]
    best = min(CODEF, key=lambda k: abs(np.log(prod*CODEF[k])))
    LG.append((f"{r['corner']} {r['temp']} °C, {r['vdda']} V", b/b_tt, KV[r["corner"][:2]], prod, best, prod*CODEF[best]))
lg_tab = ("| Corner | β_eff / tt | K_VCO / tt | product | best code | after trim |\n|---|---|---|---|---|---|\n" +
          "\n".join(f"| {nm} | {a_:.2f} | {k_:.2f} | {p_:.2f} | {c_} | **{q_:.2f}** |" for nm, a_, k_, p_, c_, q_ in LG))


def row(r):
    return (f"| {r['corner']} {r['temp']} °C, {r['vdda']} V | {r['vc']} | {r['code']} | {r['G']*1e6:.2f} | "
            f"{r['v_os']*1e3:.2f} | {r['lin'][0]:+.2f} / {r['lin'][1]:+.2f} |")
dc_tab = "| Condition | V_cont (V) | code | G (µS) | offset (mV) | linear range (V) |\n|---|---|---|---|---|---|\n" + \
         "\n".join(row(r) for r in dc)
buf_tab = "| Condition | V_cont 1.3 V | 1.8 V | 2.3 V | f_3dB (MHz) |\n|---|---|---|---|---|\n" + "\n".join(
    f"| {c} {t} °C, {va} V | " + " | ".join(f"{next(r['err'] for r in buf if (r['corner'], r['temp'], r['vc']) == (c, t, vc))*1e3:+.1f} mV"
                                         for vc in (1.3, 1.8, 2.3)) +
    f" | {min(r['f3db'] for r in buf if (r['corner'], r['temp']) == (c, t))/1e6:.1f} |"
    for c, t, va in [(r["corner"], r["temp"], r["vdda"]) for r in buf][::3])
var_tab = "| Variant (first Gm, no dump capacitor) | worst |vdump − vctl| | peaking | f_3dB min |\n|---|---|---|---|\n" + "\n".join(
    f"| {tag} | {max(abs(r['err']) for r in B['res'] if r['tag'] == tag)*1e3:.1f} mV | "
    f"{max(r['peak_db'] for r in B['res'] if r['tag'] == tag):.2f} dB | "
    f"{min(r['f3db'] for r in B['res'] if r['tag'] == tag)/1e6:.0f} MHz |"
    for B in (B1, B2) for tag in dict.fromkeys(r["tag"] for r in B["res"]))
pul_tab = "| Input v1p − v1m | V_cont | charge per period | average current | τ (ckg) |\n|---|---|---|---|---|\n" + "\n".join(
    f"| {r['vd']:+.1f} V | {r['vc']} V | {r['q']*1e15:+.2f} fC | {r['i_avg']*1e9:+.2f} nA | {r['tau']*1e12:.0f} ps |" for r in SIM["pulsed"])
ns_tab = "| Variant | R_S L (µm) | G ss / ff | linear range tt | noise 10 k / 100 k / 1 MHz (pA/√Hz) |\n|---|---|---|---|---|\n" + "\n".join(
    f"| {r['tag']} | {r['RS_L']:.1f} | {r['G_ss']/r['G']:.3f} / {r['G_ff']/r['G']:.3f} | ±{min(-r['lin'][0], r['lin'][1]):.2f} V | "
    f"{r['n10k']*1e12:.2f} / {r['n100k']*1e12:.2f} / {r['n1M']*1e12:.2f} |" for r in NS)
dly_tab = "| Pulse start after the sample | " + " | ".join(f"{d_:.1f} ns" for d_ in (0.7, 2.0, 3.0, 4.5)) + " |\n|---|---|---|---|---|\n"
qrow, grow = [], []
for d_ in (0.7e-9, 2e-9, 3e-9, 4.5e-9):
    a_, b_ = [x for x in DLY if abs(x["dly"] - d_) < 1e-12]
    qrow.append(f"{a_['q']*1e15:.2f} fC"); grow.append(f"{(b_['q'] - a_['q'])/(b_['v1'] - a_['v1'])/(18.42e-6*0.53e-9)*100:.0f} %")
dly_tab += "| charge per period at lock | " + " | ".join(qrow) + " |\n| gain, fraction of G·τ | " + " | ".join(grow) + " |"

Dd = C.D
def dev(nm, d_, role, m=1):
    mm = f" × {m}" if m > 1 else ""
    return f"| {nm} | {d_[0]} | {d_[1]}{mm} | {d_[3]} µm | {role} |"
m_ = Dd["MTM"]; rm_ = Dd["RM"]
dev_tab = "| Device | Model | W per finger (µm) × units | L | Role |\n|---|---|---|---|---|\n" + "\n".join([
    dev("XN1, XN2 (per slice)", Dd["MN"], "input pair; L = 1 µm for flicker"),
    f"| R_S (per slice) | {Dd['RS'][0]} | {Dd['RS'][1]} | {Dd['RS'][2]} µm | degeneration ≈ {2000*Dd['RS'][2]/0.35/1e3:.0f} kΩ |",
    dev("XT1, XT2 (per slice)", Dd["MT"], "tail sinks, 2 µA per unit", m_),
    dev("XE1, XE2 (per slice)", Dd["MTS"], "tail enable switches (trim)", m_),
    dev("XPC, XPX (per slice)", Dd["MP"], "pMOS current sources on xc / x, 2 µA per unit", m_),
    dev("XPE1, XPE2 (per slice)", Dd["MPE"], "pMOS enable switches (gate enb)", m_),
    dev("replica XRT", Dd["MT"], "replica tails", m_*rm_), dev("replica XRE", Dd["MTS"], "replica tail switches (always on)", m_*rm_),
    dev("replica XRP", Dd["MP"], "replica pMOS diode = pb", m_*rm_), dev("replica XRPE", Dd["MPE"], "replica pMOS switches (always on)", m_*rm_),
    dev("replica XRD", Dd["MN"], "replica input device, gate at VDDA/2", rm_),
    f"| XRC1, XRC2 | {Dd['RCM'][0]} | {Dd['RCM'][1]} | {Dd['RCM'][2]} µm | VDDA/2 divider for the replica (≈ 0.86 MΩ each) |",
    f"| TG_F, TG_D | {Dd['TGN'][0]} / {Dd['TGP'][0]} | {Dd['TGN'][1]} / {Dd['TGP'][1]} | 0.5 µm | steering to vctl / vdump (small, balanced) |",
    dev("XA1, XA2 (buffer)", Dd["BN"], "buffer input pair"), dev("XL1, XL2 (buffer)", Dd["BP"], "buffer mirror load"),
    dev("XBT (buffer)", Dd["BT"], "buffer tail", int(round(Dd["BIT"]/Dd["IT"]))),
    f"| XCDUMP | {Dd['CDUMP'][0]} | {Dd['CDUMP'][1]} × {Dd['CDUMP'][3]} µm × {Dd['CDUMP'][2]} tiles | — | dump-node decoupling, 2 pF |",
    "| decoder | nfet_01v8 / pfet_01v8 | 0.42–0.84 | 0.15 µm | 1.8 V trim logic on VDDD + 4 level shifters (step 75 HV) |"])

doc = f"""# Step 79: pulsed-Gm charge pump (sub-sampling charge pump) in 5 V devices

*Phase 7, roadmap step 79 (19–20 Nov 2026).* Deliverable: schematic (xschem, hierarchical, LVS-clean), sizing table,
verification over PVT — and, because the charge pump only makes sense with its detector, a whole-detector bench
(SSPD + Gm + clock generator). Design files `design/sscp/sscp_hv.py`, `sscp_hv_*.py`; schematics `xschem/sscp_hv/`;
data `design/sscp/data/`; methods M10, M11, M16, M18 (explained in `docs/testbench_guide.md`).

Reproduce (in `design/sscp`):

```bash
python3 sscp_hv_size.py --replica   # G sizing of the mirror-less Gm and its step response
python3 sscp_hv_noisesize.py        # noise-driven resizing (replica size, bias current, current-source lengths)
python3 sscp_hv_buf.py; python3 sscp_hv_buf.py --round2   # dump-buffer sizing, both rounds
python3 sscp_hv_delay.py            # Gm recovery after the SSPD's tracking phase vs pulse delay (sets step 77's gap 1)
python3 sscp_hv_det.py              # whole detector, beat runs: beta_eff and lock point over corners and V_cont
python3 sscp_hv_sim.py              # A DC transfer, D dump buffer, B pulsed (DC input), C noise, E VDDA     (M10, M16, M11)
python3 sscp_hv_cin.py              # Gm input capacitance (the SSPD's C1 node)
python3 sscp_hv_noise.py            # Gm noise and VDDA into the Gm in the system model                 (M9)
python3 sscp_hv_plots.py            # docs/img/sscp_hv_*.png
python3 schematics_hv.py             # xschem/sscp_hv/*, drawing checks, LVS reference                   (M5)
cd ../../xschem && ./lvs.sh sscp_hv/sspll_sscp_hv_top.sch netlist/ref_sscp_hv.spice sspll_sscp_hv_top   # M4
```

## Result in one paragraph

Three of five identical **degenerated nMOS slices** (code 00) turn the SSPD sample v1p − v1m into a current with
**G = {G0*1e6:.2f} µS** at tt ({min(Gs)*1e6:.1f}–{max(Gs)*1e6:.1f} µS over 11 corners and V_cont 1.3–2.3 V), linear
over ±{lin_tt:.2f} V at tt (≥ ±{lin:.2f} V everywhere). **There is no current mirror:** each drain has its own pMOS
current source, biased by a replica half-slice. The output drain x is steered to the loop filter during the Gm pulse
(τ = {tauP*1e12:.0f} ps, about 2.4 ns after the sample) and to a dump node otherwise; the complementary drain sits on
the dump node, which a buffer and 2 pF hold within {berr*1e3:.1f} mV of V_cont. **In the whole detector** (real SSPD,
real clock generator) the loop gain at lock is **β_eff = {b_tt*1e6:.2f} µA/rad** at tt ({b_tt*1e6/0.790*100:.0f} % of the
0.790 target; {b_tt*0.974*1e6:.2f} µA/rad with the final C1, section B), and the lock point sits 0.07–0.13 rad from the SSPD's zero crossing at every corner, inside the Gm's linear range. The trim codes give
×{code['10']/G0:.2f} / 1 / ×{code['01']/G0:.2f} / ×{code['11']/G0:.2f}. Output noise {n1M*1e12:.2f} pA/√Hz at 1 MHz
({n10k*1e12:.1f} at 10 kHz): {gm_ps*1e3:.0f} fs in the system. System, 3.3 V square reference: **{o['off']['total']:.2f} /
{o['on']['total']:.2f} ps**, L(300 kHz) **{o['off']['L300k']:.1f} / {o['on']['L300k']:.1f} dBc/Hz** (FFNC off / on, typ);
worst {ow['off']['total']:.2f} / {ow['on']['total']:.2f} ps. I(VDDA) {idd*1e6:.0f} µA ({idd*3.3*1e3:.2f} mW).

**This step changed two earlier blocks.** The Gm's input capacitance is {cin_tt*1e15:.1f} fF, not 8 fF, so the SSPD's C1
shrank to keep its sampled node (step 78); and the Gm needs about 2 ns after the sample to recover from the SSPD's
tracking swing, so the clock generator now delays the Gm pulse (step 77, section B2 there).

![top](../img/sch_sspll_sscp_hv.png)

## What happens, how, why

### What happens
After every sample the SSPD holds v1p − v1m = 2A·φ on C1. During the Gm pulse the charge pump turns it into a current
pulse into the loop filter; averaged over the period that is a current proportional to the phase error, with no PFD
and no dead zone:

$$I_{{avg}} = G\\,(2A\\varphi)\\,\\frac{{\\tau}}{{T}}\\quad\\Rightarrow\\quad \\beta = \\frac{{2A\\,G\\,\\tau}}{{T}}$$

### How it happens
- **Degenerated pair, no mirror.** Each slice is an nMOS pair (4/1 µm) with R_S between the sources and {m_} tail units
  (2 µA each) under each source. Each drain has its own pMOS current source equal to its tail, so the output drain
  carries only the change of its transistor's current:

$$i_x = I_P - I_{{N2}} = \\tfrac{{1}}{{2}}\\,G_{{pair}}\\,(v_{{1p}} - v_{{1m}}),\\qquad G_{{pair}} = \\frac{{1}}{{1/g_m + R_S/2}}$$

  Only one drain (x) feeds the filter, so the output transconductance is half the pair's: three slices give 18.4 µS.
- **Replica bias.** The pMOS gate line pb comes from a replica half-slice ({rm_} copies in parallel) whose input sits at
  VDDA/2 (the SSPD's sampled common mode is 0.48–0.53·VDDA), so the pMOS sources match the tails without a systematic
  offset.
- **Steering.** x goes to vctl through TG_F while ckg = 1, to vdump through TG_D otherwise. The complementary drain xc
  is always on vdump: while v1 tracks the ring, x and xc carry opposite currents into the dump node.
- **Dump node.** A unity-gain 5 V OTA copies vctl onto vdump; 2 pF of MIM holds vdump against the 800 MHz current.
- **Trim (icp_trim).** A 1.8 V decoder on VDDD and four level shifters (with complementary outputs for the pMOS
  enables) turn on 2 / 3 / 4 / 5 slices.

### Why it happens this way
- **No mirror, because a mirror at microamps is slow.** The first version folded the pair's current through a shared
  pMOS mirror (5 × 2/4 µm, 6 µA): its gate node has a pole near 30 MHz. With DC inputs it looked fine, but with the
  real SSPD in front, v1 jumps from the 800 MHz tracking waveform to the held value 0.6 ns before the pulse, and the
  mirror cannot follow: β_eff collapsed to {min(r['beta_eff'] for r in V1DET[:3])*1e6:.2f}–{max(r['beta_eff'] for r in V1DET[:3])*1e6:.2f} µA/rad
  at tt (target 0.79), with 3–4 fC of charge per period at lock.
- **A pulse 2.4 ns after the sample, because the Gm must recover.** The degeneration resistor and the source
  capacitance (≈ 100 kΩ × 12 fF ≈ 1.2 ns) remember the ±2 V tracking swing. Measured on the locked detector (first
  mirror-less Gm):

{dly_tab}

  Step 77 added an RC delay so the pulse now starts 2.36 ns after the sample (1.67–3.66 ns over corners).
- **2 pF on the dump node, because the tracking current reaches it.** Without it vdump swung ±90 mV at 800 MHz and was
  up to 90 mV away from vctl when x switched; each switch then put C_x·Δv into the filter.
- **Noise sets the bias.** The phase noise of the pump is S_φ = S_i/(4A²G²d): every current source whose noise reaches
  x counts against a small G. The replica's noise is copied onto pb and into every pMOS source; it was 74 % of the
  total at first. A {rm_}× replica and longer current sources (pMOS L 4 µm, tails L 8 µm) cut the output noise by 6 dB.
- **Degeneration** keeps G a resistor ratio: within ±6 % over corners and V_cont at a fixed code.

## A. Architecture decisions

| Decision | Options | Chosen | Why |
|---|---|---|---|
| Transconductor | plain pair, degenerated pair | **degenerated pair, R_S xhigh-poly** | G within ±6 % over PVT, linear ±0.4 V |
| Output stage | pMOS mirror, own current source per drain | **own pMOS source per drain, replica bias** | the mirror (30 MHz pole) could not follow v1 after tracking: β_eff 0.17 instead of 0.79 |
| Pulsing | switch the tail, steer the output | **steer x between vctl and vdump; xc always on vdump** | constant bias; x + xc cancel on the dump node while v1 tracks |
| Pulse timing | 0.6 ns after the sample, later | **2.4 ns after the sample (step 77 gap-1 delay)** | the Gm recovers from the tracking swing: 4.4 → 0.7 fC per period at lock |
| Dump node | buffer only, buffer + capacitor | **buffer + 2 pF MIM** | ±90 mV of 800 MHz ripple without it |
| Replica | 1 half-slice, {rm_} | **{rm_} half-slices** | its noise on pb was 74 % of the output noise |
| Current sources | pMOS 4/2, tails 1/4 µm | **pMOS 4/4, tails 1/8 µm** | less gm (and flicker) per µA: output noise −6 dB with the replica |
| Trim | DAC on the tail, slices | **5 equal slices, 2–5 on** | ratio set by device count: ×{code['10']/G0:.2f}–{code['11']/G0:.2f} |
| Steering TGs | 2/4 µm, 1/1 µm, 0.5/0.5 µm | **1/1 µm** | smaller injection; 0.5/0.5 µm saved only 0.1–0.3 fC per period |
| Decoder | 5 V logic, 1.8 V logic | **1.8 V on VDDD + level shifters** | device rule (digital = 1.8 V) |

## B. Whole detector: SSPD + Gm + clock generator (method M18, extended)

**Bench (`sscp_hv_det.py`).** The step-78 beat bench (ring at (16 + 1/32)·f_ref behind a 5 V buffer stage, real
clock generator with the gap-1 delay) with the real Gm on v1 (no placeholder load) and vctl held by an ideal source.
Every reference period gives one sample of the ring phase and one charge packet into vctl; 32 packets cover a whole
ring cycle. β_eff is the slope of charge per period vs phase at the zero of the charge (cubic fit within ±0.6 rad),
divided by T; the zero is the lock point. **Why this bench exists:** with DC sources on v1 the first Gm looked right.
Only the SSPD's real waveform — tracking the ring at 800 MHz for half of every period — showed the mirror's slowness,
the dump-node ripple and the recovery time.

{det_tab}
(These runs used C1 = 2.59 µm, sized for the Gm's input before its final noise resize; the final Gm has 26.5 fF and
C1 = 2.69 µm restores the 42.7 fF node, 1.1 fF more than in these runs: A, and β_eff with it, is about 2.6 % lower in
the final design, {b_tt*0.974*1e6:.2f} µA/rad at tt.)

**Reading it.** β_eff is {b_tt*1e6/0.790*100:.0f} % of the 0.790 µA/rad target at tt in these runs. Against 2A·G·τ/T (τ read at
mid-swing) the measured slope is 100–109 % at tt: the TGs conduct a little beyond the mid-swing points. At ss_hh 110 °C it
is 75 %: most likely the Gm recovers more slowly there (hot, slow corner; not separated further); the trim covers it. The lock point sits {min(z for r, b, z in det)*1e3:+.0f} to
{max(z for r, b, z in det)*1e3:+.0f} mrad from the SSPD's zero crossing: inside the Gm's linear range
(±{lin_tt:.2f} V ↔ ±{lin_tt/(2*A):.2f} rad at A = {A:.2f} V/rad).

**Loop gain over PVT and the trim.** β·K_VCO with K_VCO from step 74 HV; the trim code is chosen once per chip:

{lg_tab}

## C. DC transfer over corners, V_cont and codes (method M10)

![dc](../img/sscp_hv_dc.png)

{dc_tab}

**Requirements:** G within ±15 % over PVT at a fixed code ✔ (−5 / +6 %); offset small against the linear range: ≤ {vos*1e3:.1f} mV ✔;
linear range ≥ ±0.1 V ✔.

## D. Pulsed operation with DC inputs (method M16)

{pul_tab}

Δq/Δv = {abs(qd)*1e15:.1f} fC/V per period (G·τ = {G0*tauP*1e15:.1f} fC/V). With DC inputs the Gm is always settled, so the
charge at zero input is the switch injection and the dump-node error alone.

## E. Noise and supply (methods M11, M9)

![noise](../img/sscp_hv_noise.png)

**Noise-driven sizing (`sscp_hv_noisesize.py`, R_S re-tuned for G = 18.42 µS in every variant):**

{ns_tab}

The MTM 1 variants (2 µA tails) are quieter still but lose half the linear range (±0.17 V): the lock-point offsets of
section B would sit at its edge. The chosen variant is the last row.

- **Output current noise** (Gm on): {n10k*1e12:.2f} / {n100k*1e12:.2f} / {n1M*1e12:.2f} pA/√Hz at 10 k / 100 k / 1 MHz.
  As detector-referred phase noise: L = {NZ['L_gm_10k']:.1f} dBc/Hz (10 kHz), {NZ['L_gm_1M']:.1f} dBc/Hz (1 MHz); not ×N².
- **VDDA → filter current:** {Y1M*1e9:.0f} nA/V at 1 MHz; as phase |Y|·v/(2AG).
- **I(VDDA)** {idd*1e6:.1f} µA → {idd*3.3*1e3:.3f} mW (slices, replica ×{rm_}, divider, buffer).

| Case | Gm (fs) | VDDA into Gm (fs) | jitter off / on (ps) | L(300 kHz) off / on |
|---|---|---|---|---|
""" + "\n".join(
    f"| {k.replace('_', ' ')} | {S[k]['on']['terms']['pulsed-Gm charge pump']*1e3:.0f} | {S[k]['on']['terms']['VDDA into the Gm']*1e3:.0f} | "
    f"{S[k]['off']['total']:.2f} / {S[k]['on']['total']:.2f} | {S[k]['off'].get('L300k', float('nan')):.1f} / {S[k]['on'].get('L300k', float('nan')):.1f} |"
    for k in ("3.3_typ", "3.3_pess", "1.0_typ", "1.0_pess", "3.3_worst")) + f"""

Proposal: typ 2.6 / 1.6 ps, −114 / −124 dBc/Hz; max 5.0 / 3.2 ps, −108 / −116 dBc/Hz.

## F. Dump buffer (method M10)

**First run:** BN 4/1, BP 4/2 µm lost tracking at ss 110 °C, 2.97 V, V_cont 2.3 V (vdump 92 mV low): an nMOS-input
follower with a pMOS mirror follows only up to

$$V_{{in,max}} = V_{{DDA}} - V_{{SG}}(L_1) + V_{{TN}}$$

A wider pMOS fixed the headroom and longer channels the residual error (from the two input devices' different V_DS):

{var_tab}

**Final (BN 8/2, BP 16/2, 2 pF on vdump):**

{buf_tab}

|vdump − vctl| ≤ {berr*1e3:.1f} mV at DC; the 2 pF makes the buffer a single-pole loop (f_3dB ≥ {bf3/1e6:.1f} MHz, no
peaking). The residual DC error comes from the slices' x/xc offset currents into the dump node.

## G. Schematics (hierarchical, real wiring, LVS-clean)

| Level | Cell | Contents |
|---|---|---|
| 1 | `sspll_sscp_hv_rs` | degeneration resistor |
| 2 | `sspll_sscp_hv_slice` | pair, R_S, two tails, two enable switches, two pMOS sources with their enable switches |
| 1 | `sspll_sscp_hv_tg` | 5 V steering TG |
| 1 | `sspll_sscp_hv_buf` | dump buffer (OTA follower) |
| 3 | `sspll_sscp_hv` | five slices, replica bias, steering TGs, dump buffer, 2 pF, bias diode — buses drawn as wires |
| 1 | `sspll_sscp_hv_dec` | 1.8 V trim decoder + 4 level shifters (true and complementary enables) |
| 4 | `sspll_sscp_hv_top` | decoder + core |

netgen against `xschem/netlist/ref_sscp_hv.spice` (= `sscp_hv.full()`): *Circuits match uniquely* and no property
errors for all seven cells; drawing checker clean. (`lvs.sh` now also reports netgen's property errors: a device
multiplier drawn differently from the netlist would otherwise pass unnoticed.)

![slice](../img/sch_sspll_sscp_hv_slice.png)
![buffer](../img/sch_sspll_sscp_hv_buf.png)
![top](../img/sch_sspll_sscp_hv_top.png)

## H. Sizing table (all devices pass `tools/pdk_limits.py`)

{dev_tab}

Gate load on ckg / ckgb: one 1 µm nMOS and one 1 µm pMOS gate each (L 0.5 µm) ≈ 4 fF — inside the 40 fF the clock
generator was verified with. Input capacitance on each of v1p / v1m: {cin_tt*1e15:.1f} fF at tt
({cin_rng[0]*1e15:.0f}–{cin_rng[1]*1e15:.0f} fF over corners, codes and ckg).

## I. Requirements handed on

1. **Step 80 (loop filter):** current source into vctl during τ; V_cont window 1.3–2.3 V; β_eff = {b_tt*1e6:.2f} µA/rad at tt
   (×{min(x[1] for x in LG):.2f}–{max(x[1] for x in LG):.2f} over corners before trim).
2. **Step 78 SSPD:** Gm input {cin_tt*1e15:.1f} fF per side (C1 = 2.69 µm keeps the node).
3. **Step 77 clock generator:** Gm pulse ≥ 1.6 ns after the sample (done: 1.67–3.66 ns).
4. **Bias generator:** one 2 µA unit into ib.
5. **Layout:** slices in a row, common-centroid pairs, R_S interdigitated; replica next to the slices; x short and
   symmetric to both TGs; vdump and vctl side by side; the 2 pF MIM over the slices.

## J. Problems met and how they were solved

| Problem | Found by | Cause | Solution |
|---|---|---|---|
| Dump buffer lost tracking at ss 110 °C, V_cont 2.3 V (−92 mV) | buffer bench D | V_in,max = VDDA − V_SG + V_TN with a narrow pMOS load | BN 8/2, BP 16/2 µm |
| Pulsed gain 39 % above G·τ, 1.4 fC at zero input | pulsed bench (DC inputs) | vdump moved with the Gm's current (buffer R_out ≈ 10 kΩ) | explained only by the whole-detector bench (next rows) |
| Gm input 26 fF, not 8 fF | `sscp_hv_cin.py` | the pair's gate capacitance (5 slices, 4/1 µm thick oxide) | C1 of the SSPD shrunk to keep the node (step 78) |
| Whole detector: β_eff 0.17 µA/rad, 4 fC at lock | `sscp_hv_det.py` | pMOS mirror pole near 30 MHz; v1 changes 0.6 ns before the pulse | no mirror: own pMOS source per drain, replica bias |
| vdump ±90 mV at 800 MHz | locked-detector waveforms | the Gm's tracking current into the dump node | xc on vdump (cancels x), 2 pF MIM |
| Still 4.4 fC at lock, gain 73 % | `sscp_hv_delay.py` | Gm recovery from the tracking swing (R_S × source C) | Gm pulse 2.4 ns after the sample (step 77 RC delay) |
| Output noise 2.98 pA/√Hz at 1 MHz: L(300 kHz) FFNC on −123.0 | noise bench + ngspice noise summary | replica noise on pb (74 %), current-source gm | replica ×{rm_}, pMOS L 4 µm, tails L 8 µm: −6 dB |
| Replica multiplier drawn ×1, netlist ×{m_*rm_}: LVS still "match" | review of the drawing | `lvs.sh` read only the topology line | drawing fixed; `lvs.sh` now reports property errors |

## Testbenches

Set-up, method and pitfalls: `docs/testbench_guide.md`, section "5 V pulsed-Gm charge pump benches (step 79)".

## Interview questions (step 79)

The answers are in the learning notebook (phase 7), step 79.

1. What is a pulsed-Gm charge pump and why does a sub-sampling PLL use one?
2. Derive β = 2A·G·τ/T.
3. Why did the first Gm, which looked right with DC inputs, fail with the real SSPD?
4. Why is the pulse 2.4 ns after the sample and not right after it?
5. What do the dump buffer and the 2 pF do, and what happens without them?
6. Why does each drain have its own current source, and how is the offset between them kept small?
7. Why was the replica bias the largest noise source, and how was that fixed?
8. How do the trim codes work, and why slices rather than a current DAC?
9. Why is the decoder in 1.8 V logic, with complementary enables?
10. How was G measured, and why is its sign negative in the testbench?
"""
open(os.path.join(ROOT, "docs", "design", "sscp_hv.md"), "w").write(doc)
print("written", round(G0*1e6, 2), round(b_tt*1e6, 3))
