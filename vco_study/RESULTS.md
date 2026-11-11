# 3-stage vs 5-stage pseudo-differential ring VCO: feasibility (11 Nov 2026)

Question: can a 3-stage pseudo-differential ring at 2.4 GHz (50 MHz x 48, range 2.16-2.64 GHz) meet the
proposal's constraints on speed, start-up, area, phase noise, power and FoM, and is it better than the
proposal's 5-stage x1.5 ring at 1.6 GHz (50 MHz x 32)?

All runs: ngspice-42, sky130A open_pdks 1689ac3f (pinned), delay cell of `sspll_vco_dcell.sch`
with every width scaled by SC, AC-coupled buffer on every node, ideal current feed (CCO), vtune = 0.9 V.
Benches: `ringgen.py` (netlist), `sweep.sh` (speed), `startup.sh` / `startup_time.py` (start-up),
`isf.py` (phase noise), `compare.py` + `cases.txt` (jitter, power, FoM). Raw numbers in `results/`.

## 1. Speed (ring supply must stay <= 1.75 V)

| Ring | Corner | Current for 2.64 GHz (top of range) | Ring supply | f at 1.75 V | Margin over 2.64 GHz |
|---|---|---|---|---|---|
| 3 x1.0 | ss 110 C 10 fF | 1.02 mA | 1.52 V | ~3.40 GHz | 29% |
| 3 x1.5 | ss 110 C 10 fF | ~1.3 mA | ~1.45 V | ~3.83 GHz | 45% |
| 5 x1.5 (proposal, needs 1.76 GHz) | ss 110 C 10 fF | 1.66 mA | 1.63 V | ~2.16 GHz | 23% |

Low end (2.16 GHz at ff -40 C, 0 fF): 3 x1.0 needs ~0.36 mA at ~1.13 V - inside the 5-bit CCO DAC range.
Typical 2.4 GHz (tt 27 C 10 fF): 3 x1.0 0.73 mA, 3 x1.5 0.93 mA. 5 x1.5 at 1.6 GHz: 1.31 mA.

## 2. Start-up

Odd stage count: each half of the pseudo-differential ring is a 3-inverter ring, so the common-mode
latch of the 4-stage ring cannot occur. Symmetric power-up (all nodes 0 V, current ramp 2 ns) and a forced
common-mode state + 10 mV kick both end in the differential mode at tt, ss/110, ff/-40, fs, sf, for x1.0 and x1.5.

| Ring | tt | ss 110 C | ff -40 C | fs | sf |
|---|---|---|---|---|---|
| 3 x1.0, time to 1 V differential | 6.8 ns | 3.9 ns | 2.9 ns | 3.2 ns | 3.1 ns |
| 5 x1.5, time to 1 V differential | 2.2 ns | 3.2 ns | 1.9 ns | 2.4 ns | 2.7 ns |

(Symmetric start relies on numerical asymmetry; real mismatch and noise only make it faster.)
Note: a 40 ns run at fs read 3.53 GHz in power-up mode vs 3.13 GHz forced - an artefact of the
measurement window catching the start-up transient; 120 ns runs settle to the same 3.127 GHz in both.

## 3. Phase noise (ISF extraction, thermal noise only)

Method (Hajimiri-Lee): inject +/-1 fC (1 ps pulse) into one node at 24 phases of a cycle; the shift of a
zero crossing 60 cycles later gives h(t) = dphi/dq. Channel noise of every device on that node
S_i(t) = 4kT(gamma gm + gds), gamma = 1, from the large-signal operating point over one cycle.
L(df) = 2N <h^2 S_i> / (2 (2 pi df)^2). Linearity checked: q = 0.5 fC and 2 fC give the same h within 0.2%.

| Ring | f0 | I (tt, 5 fF) | P_VCO (x9/8 x 3.3 V) | L(1 MHz), thermal | VCO FoM | ISF dc/rms |
|---|---|---|---|---|---|---|
| 3 x1.0 | 2.403 GHz | 0.61 mA | 2.26 mW | **-93.0 dBc/Hz** | 157.1 dB | 0.58 |
| 3 x1.5 | 2.398 GHz | 0.817 mA | 3.03 mW | **-93.9 dBc/Hz** | 156.7 dB | - |
| 5 x1.5 | 1.602 GHz | 1.08 mA | 4.01 mW | **-98.1 dBc/Hz** | 156.2 dB | 0.66 |

VCO FoM = -L + 20 log(f0/df) - 10 log(P/1 mW). The rings are equally efficient within 1 dB.
**The proposal's 5-stage assumption (-95.6 dBc/Hz) is 3.4 dB above the simulated thermal floor**
(-99.0 dBc/Hz once scaled to the 10 fF power basis), leaving that margin for flicker and CCO noise.
Not included: flicker (the large dc ISF of both rings means flicker up-conversion is real; the loop at
2.5 MHz suppresses it), CCO current-source noise, supply noise, gamma > 1 (up to ~1.7 dB worse).

## 4. Jitter, power, FoM (proposal model, same 3.35 dB non-thermal allowance on every ring)

| Case | P_VCO | L(1 MHz) | Jitter typ off / on | Jitter pess off / on | P total (FFNC on) | PLL FoM |
|---|---|---|---|---|---|---|
| 5 x1.5, 1.6 GHz, N = 32 (proposal) | 4.86 mW | -95.6 | 2.41 / 1.57 ps | 4.03 / 2.61 ps | 7.41 mW | -227.4 dB |
| 3 x1.0, 2.4 GHz, N = 48 | 2.71 mW | -90.4 | 2.91 / 1.87 ps | **4.87** / 3.13 ps | 5.76 mW | -227.0 dB |
| 3 x1.5, 2.4 GHz, N = 48 | 3.47 mW | -91.1 | 2.69 / 1.73 ps | 4.50 / 2.90 ps | 6.52 mW | -227.1 dB |

Other blocks at 2.4 GHz assumed +0.5 mW (dividers, SSPD buffer and the extra /3 at 1.5x frequency).
3 x1.0 breaks the proposal's 4.7 ps maximum (FFNC off). Matching the 5-stage jitter needs about
1.5x the 3 x1.0 ring power (about 4.0 mW VCO, 7.05 mW total, FoM about -227.6 dB).

## 5. Area

Ring cores are tiny either way (3 x1.0 about 250 um2, 5 x1.5 about 750 um2 of device area) - under 2% of the
0.06 mm2 block. N = 48 needs a /3 stage (a few gates). Loop filter, LDO and FFNC dominate area; unchanged.

## 6. Verdict

The 3-stage ring is **feasible**: speed (29-45% margin), start-up, area and power all pass.
It is **not better** on the metric that ranks PLLs: jitter-power FoM is the same within 0.4 dB, and
at equal ring power it gives more absolute jitter. It also moves SSPD sampling, FFNC delay line and the
first divider to 2.4-2.64 GHz (TSPC margin drops from 139% to 59%) and would force a proposal rewrite
12 days before the deadline. Recommendation: **keep the 5-stage x1.5 ring at 1.6 GHz.**
Reasons that could still favour 3 stages: a 2.4 GHz ISM-band output, or reuse of old blocks planned for 2.36 GHz.

## 7. Update (11 Nov 2026): phase noise with the models' own noise

`isf2.py` replaces the gamma = 1 assumption with the drain-noise tables of the pinned models
(`../correlation/noisegrid.py`: thermal and 1/f noise of a W = 1 um device over a 10 x 10 Vgs/Vds grid,
scaled by W) and adds flicker up-conversion through the dc part of the ISF.

| Ring | f0 | L(1 MHz) thermal | L(1 MHz) flicker | L(1 MHz) total | 1/f^3 corner |
|---|---|---|---|---|---|
| 5 x1.5, 1.08 mA | 1.602 GHz | -97.5 | -97.1 | **-94.2 dBc/Hz** | 1.1 MHz |
| 3 x1.0, 0.61 mA | 2.403 GHz | -91.8 | -89.4 | **-87.4 dBc/Hz** | 1.75 MHz |

nMOS flicker in these models is very high (corner tens of MHz at the device), so the 1/f^3 corner of the ring is
~1 MHz, not the 0.2 MHz (typ) / 0.5 MHz (pess) the proposal assumed. The 3-stage verdict does not change.

Proposal budget re-run (`budget_modelnoise.py`, 5-stage, 10 fF power basis, +1 dB CCO allowance typ, +4 dB and
2x corner pessimistic):

| Case | Jitter off / on | L(300 kHz) off / on |
|---|---|---|
| Proposal, typ (assumed) | 2.41 / 1.57 ps | -110.6 / -120.4 |
| Model noise, typ | 2.29 / 1.40 ps | -108.1 / -120.0 |
| Proposal, pess (assumed) | 4.03 / 2.61 ps | -104.7 / -112.6 |
| Model noise, pess | 3.71 / 2.25 ps | -102.6 / -111.3 |

Jitter and FFNC-on specs still hold. The FFNC-off phase noise at 300 kHz does not: typ -108 vs the proposed -111,
pessimistic -102.6 vs the -102 maximum (0.6 dB margin). Recommended spec: typ -108, max -100 dBc/Hz.
Still not included: CCO current-source noise beyond the +1 dB allowance, supply noise.
