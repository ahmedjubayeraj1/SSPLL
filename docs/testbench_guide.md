# Testbench guide: how every simulation in this project is set up, why, and how to rebuild it yourself

This guide covers every testbench of the 5 V-device design (the block designs) and is extended with each new block. Every
bench is built as a netlist string by the block's script (`design/<block>/<block>_hv.py`) and run over corners,
temperatures, supplies and codes by the step scripts (`design/<block>/<block>_hv_*.py`), which save their numbers in
`design/<block>/data/*.json`. For each bench the entry says what it measures, why it is set up that way, what to look
at, the result, the pitfalls, and how to rebuild it in xschem and Cadence. The method numbers (M1, M2, …) are the
measurement methods; each step note in `docs/design/` explains the methods it uses.

---

## 1. What a testbench is

A testbench is a circuit around the **device under test (DUT)**. It has four parts, and every bench here is written
in this order:

| Part | Question it answers | Example |
|---|---|---|
| **Models and conditions** | which process corner, which temperature? | `.lib …/sky130.lib.spice ss` and `.temp 110` |
| **Stimulus and supplies** | what drives the DUT? | supplies, bias current, input signal (sine, pulse, DC level, code bits) |
| **Load and environment** | what does the DUT drive, what is it connected to? | capacitive load of the next block, an ideal stand-in for a block not designed yet |
| **Analysis and measurement** | what do we compute, and which number comes out? | `.op`, `.dc`, `.ac`, `.noise`, `.tran` + `meas`, `print`, `wrdata` |

**Golden rule: replace every neighbour by the simplest thing that behaves like it at the port**, and say so. The ring
is tested with an *ideal current source* instead of the current DAC, so we see the ring alone. The current DAC is
tested with an *ideal voltage source* instead of the ring, so we see the current source alone. Then one bench closes
the gap by putting the real neighbour back (for example the whole-detector bench M22 of the Gm design: phase detector,
clock generator and charge pump together).

**Always load the PDK `.spiceinit`.** Every run copies it next to the netlist; without it the sky130 models give
different results.

## 2. The analysis toolbox (what each analysis is good for)
## 3. The analysis toolbox (what each analysis is good for)

| Analysis | What it computes | Use it for | Spectre / ADE equivalent |
|---|---|---|---|
| `op` | DC operating point | bias points, currents, region of every device (`show all`) | dc (save oppoint) |
| `dc src a b step` | operating point while sweeping a source | I–V curves, compliance, transfer curves | dc sweep |
| `ac dec n f1 f2` | small-signal response around the op | gain, bandwidth, supply rejection (put `ac 1` on the supply) | ac |
| `noise v(out) src dec n f1 f2` | noise density at an output, every device's noise through its exact transfer | noise of biased analog blocks; needs `option sparse` with the sky130 setup | noise |
| `tran step stop` | time-domain, large-signal | oscillators, switching, delay, duty, start-up | tran |
| `trnoise(...)` source | a random noise voltage or current in a transient | jitter of switching circuits (ngspice has no device noise in transients) | tran with noise enabled (`noisefmax`), or pss + pnoise |
| `meas` | one number from a result: `when`, `find … at`, `trig … targ`, `avg`, `pp`, `max` | delays, frequencies, levels | calculator / OCEAN |
| `.control` loops: `foreach`, `alter`, `destroy all` | sweeps without re-reading the netlist | f(I), f(vtune), code sweeps | parametric analysis |

Two ngspice details you will meet:
- After a new analysis, the old results belong to an older *plot*. Keep numbers you still need in shell variables:
  `set a = "$&x"`, used later as `$a`.
- `option sparse` is needed for `.noise` (the KLU solver selected by `.spiceinit` fails on it).

---


---

## 3. The testbenches, block by block

Each entry gives: **purpose** · **set-up and why** · **what to look at** · **result (tt, 27 °C unless noted)** · **pitfalls**.

#### 5 V ring VCO benches (M1, M2) — `design/vco/vco_hv.py`
- **Purpose.** Size the 3-stage 5 V ring for 800 MHz, measure its phase noise, tuning and range, and prove that it starts.
- **Common setup (`netlist()`).**
  - Three `dcell` instances; stage 3 feeds back crossed (outp → inm, outm → inp).
  - An ideal current source `ivco` stands for the CCO and feeds the ring's supply node `vddvco`, with 0.5 pF of decoupling.
  - `vtn` sets vtune. `vdda` (3.3 V, or 2.97 / 3.63 V at the corners) feeds the six AC-coupled buffers, each loaded with 15 fF.
  - `cpar` adds wiring capacitance on every node: 10 fF at tt, 15 at ss, 5 at ff.
  - `.ic` starts the ring differentially; `uic` skips the operating point.
- **Read-out.**
  - f = (r1 − r0)/(t_b − t_a) from the rising zero crossings of vd = v(vop) − v(vom).
  - The average ring-node voltage (`vdd_avg`) is the voltage the CCO must supply.
  - `ibuf` = average i(vdda), the buffer current.
- **Benches built on it.**
  - **`vco_hv_point.py`** (find the current, then the ISF):
    - A secant search on log f vs log I finds the current for 800 MHz.
    - `isf_noise()` injects ±4 fC at 12 phases into node p1 (24 runs), each 1 ps wide, and reads the shift of a later zero crossing: h = −2π·Δt/T/(2q).
    - The bias of every device touching p1 is saved over one period (`@m…[vgs]`, `[vds]`). Their noise comes from tables of a W = 1 µm device on a V_GS × V_DS grid up to 3.3 V (`noise_table()`, ngspice `.noise`: white part at 1 GHz, flicker coefficient from 1 kHz).
    - L_th and L_fl follow from the ISF formulas; the 1/f³ corner is where they are equal.
  - **`vco_hv_char.py`:**
    - f vs I at three corners;
    - f vs vtune at the 800 MHz current;
    - the currents for 880 MHz (ss/110 °C) and 720 MHz (ff/−40 °C), with the secant search;
    - sf/fs;
    - buffer current and swing (`buffer_current()`: one buffer with the PDK MIM and poly resistor, driven by a 1.6 V square wave).
  - **`vco_hv_startup.py`:**
    - All nodes and `vddvco` start at 0 V, and the current ramps up over 2 ns.
    - Start-up time = when |vd| first exceeds 1 V. The frequency is counted over 10 periods after 40 ns, and the swing is measured over 40–60 ns.
    - Repeated with ±2 % width mismatch in stage 1 (`mism=`).
- **Pitfalls.**
  - Do not count zero crossings from t = 0 at power-up: vd chatters around 0 V at numerical-noise level and gives nonsense frequencies.
  - Make the window long enough for r1 cycles at the lowest frequency (60 ns).
  - The injection runs save only `v(vop) v(vom) v(vddvco) vdda#branch`. Every vector a `meas` uses must be in that list.

#### 5 V CCO benches (M10, M11, M13) — `design/cco/cco_hv.py`
- **Purpose.** Prove that the CCO delivers the ring's current range at every corner, that it stays a current source up to the ring-node voltage, that VDDA noise does not reach the ring (there is no LDO), and that its own noise fits the budget.
- **Common setup (`tb()`).**
  - The drawn circuit `full()`: 7 level shifters, DAC, MREF, R_F (PDK xhigh-poly, body VDDA), C_F (MIM), MOUT, cascode MC, MB, R_CAS, C_CAS, enable devices and the VTEST gate.
  - Ideal `vdda` (3.3 V, or 2.97 / 3.63 V), ideal `vddd` 1.8 V, current source `iib` 5 µA (4 / 6 µA for IBIAS ±20 %).
  - The ring is replaced by an ideal voltage source `vr` at the ring-node voltage of the corner (tt 1.89 V, ss/110 °C 2.37 V, ff/−40 °C 1.60 V). `i(vr)` is the output current.
  - Code bits come from ideal 1.8 V sources through the level shifters, as on the chip.
- **Why the ring is a voltage source.** The CCO's job is to deliver a current into a node whose voltage the ring decides. A voltage source at the worst-case node voltage tests the current source under exactly that drain voltage. For supply rejection it is the worst case: a real ring node has a finite impedance that would absorb part of the current ripple.
- **Benches.**
  - **A — DC (`op`, `cco_hv_sim.py`).** 5 corners × VDDA 2.97/3.63 V × IBIAS 4/5/6 µA × code 0/10/31, plus a code sweep at tt. Pass: code 31 at IBIAS 4 µA ≥ 1.462 mA and code 0 at IBIAS 6 µA ≤ 0.704 mA, each within the fine-tune range.
  - **B — compliance (`dc vr 0 2.8 0.1`).** Current vs ring-node voltage at the least headroom (ss/110 °C, 2.97 V, code 31, IBIAS 4 µA). Pass: ≤ 3 % drop at 2.37 V.
  - **C — supply rejection (`ac` with `vdda dc 3.3 ac 1`).** |i(vr)| per volt of VDDA from 100 Hz to 100 MHz. K_vdd = K_I·|dI/dVDDA| with K_I from 0.62 / 0.41 / 0.85 GHz/mA. Pass: ≤ 5 MHz/V at 1 MHz (tt).
  - **`cco_hv_vdda.py`.** Bench C at 1 MHz for VDDA 2.97…3.63 V at three operating points, combined with `op` to read the current. Shows where the cascode loses saturation.
  - **D — disable and VTEST (`op`).** pll_en = 0: output current ≈ 0. vtest_en = 1 with vtest 10 mV above the ring node: current step = 10 mV / R_INJ.
  - **E — level shifter (`tran`).** One `sspll_ls_1v8_3v3` with 20 fF loads, a 1.8 V pulse in, delays read with `meas ... when v(out)=VDDA/2`, levels with `max`/`min`. ss/110 °C and ff/−40 °C, VDDA 2.97/3.63 V, VDDD 1.71/1.89 V.
  - **Noise (`cco_hv.noise()`).** `.noise v(o) iib dec 10 1e3 1e8`: the ring source `vr` is split by an ammeter `vm`, and a CCVS `h1 o 0 vm 1` turns the output current into a voltage, so `onoise_spectrum` is in A/√Hz. Pass: ≤ 7.05 pA/√Hz at 1 MHz.
  - **`cco_hv_noise.py`.** Puts the noise spectrum and K_vdd(f) into the budget phase-domain model with the VCO ring and the loop-design filter (typ / pess / worst).
- **Pitfalls.**
  - ngspice prints the pMOS-output current with a sign; plots use |I|.
  - Give R_F's and R_CAS's xhigh-poly segments their body terminal (3rd pin) explicitly: on VSS it costs 7× in supply rejection.
  - `.noise` needs the `.spiceinit` of the PDK in the run directory; `noise()` copies it.
  - A PSR run with code 31 at IBIAS 5 µA at ss pushes 1.8 mA, more than any corner needs: do not use that point for the budget.
- **xschem.** `xschem/cco_hv/sspll_cco_hv.sym` in a testbench with `vsource` for VDDA (value `dc 3.3 ac 1` for C), `isource` for IBIAS, `vsource` at the ring pin, and a `code_shown` block with the `.control` lines above. Cadence: the same with `vdc`/`idc`, an `ac` analysis with `acm=1` on VDDA, and `noise` with the output as `i(vr)` (Spectre supports current outputs directly).

#### 5 V REF receiver benches (M10, M14–M17, M21) — `design/refbuf/refbuf_hv.py`
- **Purpose.** Prove that the receiver turns any 0.4–3.3 V pp reference into a clean refclk edge on VDDD at every corner, that its own noise and the noise it picks up from VDDA and VDDD stay inside the REF-chain allocation (−155 dBc/Hz at 50 MHz), and that it starts and stops cleanly.
- **Common setup (`head()`).**
  - The drawn circuit `full()`: pad divider (2 × 500 kΩ xhigh-poly), C_AC (2 MIM tiles), R_B (10 segments), S1 with header and C_H, S2 on VDDA, the 5 V level-shift inverter and the 1.8 V NOR on VDDD, the enable level shifter.
  - Ideal `vdda`, `vddd`, `iib` (2.5 µA out of the bias diode), `ven` for pll_en, 50 fF load on refclk (the clock-generator input).
  - Reference source `vsrc` + 50 Ω (`src()`): a sine of V_pp around VDDA/2, or a square with 0.5 ns edges (a CMOS crystal oscillator).
  - `.ic` puts vin and s1 at the self-bias point from `op()`, so a run does not have to wait 4 µs for the AC-coupled input to settle.
- **Benches.**
  - **A — bias (`op`).** 6 corners (incl. ss/−40 °C, the slowest thick-oxide level shifter) × VDDA 2.97/3.3/3.63 V: v(vin) = trip point, I(VDDA).
  - **B — large signal (`tran`, M16).** 14 cycles; the last 5 give delay pad → refclk (both at mid-level: VDDA/2 and VDDD/2), duty, 10–90 % rise, average supply currents and power. Amplitude sweep at tt, corners at both supply limits (VDDA 2.97 V with VDDD 1.71 V, 3.63 V with 1.89 V), 45 / 55 MHz.
  - **C — supply sensitivity (`supply_dc`, `supply_mod`, M21).** DC: delay with VDDA (or VDDD) +10 mV minus nominal, each at its own settled bias. AC: two transients from the same start, one with a 10 mV sine on the rail at f_m and one without; the edge-by-edge difference is fitted to a sinusoid at f_m. Edges are read where refclk crosses VDDD/2 *at that instant*, because the clock generator on VDDD switches there.
  - **D — start-up (`startup`).** pll_en steps at 0.5 µs; refclk edges counted at 0.9 V; settled = first edge after which every period is within 2 % of T. While disabled: I(VDDA), I(VDDD), refclk level.
  - **Noise (`refbuf_hv_noise.py`).** S1 gate-referred `.noise` at the self-bias point (M14); per-edge jitter of S1 with the white plateau injected at the pad by `trnoise` (M15); the output chain S2 → level shifter → NOR with a `trnoise` current of each stage's trip-point noise at its output (M17, flat copy of the top cell so the sources can reach the nodes, `save` of the two vectors only); supply terms L = (2π f_ref)²·K(f)²·S_v/2.
- **Pitfalls.**
  - A single modulated run fitted to "line + sinusoid" read 345 ps/V at 0.3 MHz instead of 35: the AC-coupled self-bias still drifts for microseconds after the start and the fit took the drift for ripple. The differential (modulated − unmodulated) form removes the drift exactly.
  - Reading the VDDD edge at a fixed 0.9 V added a false 80 ps/V (half the ripple divided by the edge slope): the receiving gate's threshold moves with VDDD.
  - A long trnoise transient with every node saved ran out of memory and stopped after 28 edges without an error message: `save` only the vectors you need, and check the edge count.
- **xschem.** `xschem/refbuf_hv/sspll_refbuf_hv.sym` with `vsource` on VDDA, VDDD (value `dc 1.8` or `sin(1.8 10m 1e6 0.4u)` for C), an `isource` from ib to ground, `vsource` + `res` 50 Ω on REF_IN, `capa` 50 fF on refclk, and a `code_shown` block with the `.control` lines above. Cadence: the same with `vsin`/`vpulse`, `idc`, `vdc`; the supply ripple with `vsin` (delay 0.4 µs) and the edge times from the calculator's `cross()` on refclk − VDDD/2.

#### 5 V clock-generator benches (M16, M17, M21) — `design/clkgen/clkgen_hv.py`
- **Purpose.** Prove four things:
  - the three clock pairs have the right order, gaps and widths at every corner on a 3.3 V swing:
    - cks/cksb for the sampling switch;
    - ckg/ckgb for the Gm pulse;
    - ckh/ckhb for the hold transfer;
  - the product τ·K_VCO, which sets the loop gain, stays near its nominal value;
  - the sampling edge adds almost no jitter;
  - VDDD noise no longer moves the sampling edge.
- **Why the receiver is always in front.**
  - Since this redo, the two inputs come from different places:
    - the sampling edge comes from `refhv` (the receiver's S2 output on VDDA);
    - the Gm and hold timing come from `refclk` (on VDDD).
  - The relative timing of the two inputs is part of what is being verified. An ideal source on each would hide exactly the errors we look for.
  - So every timing bench drives REF_IN through 50 Ω and the real receiver (`tran()`).
- **Common setup (`tran()`).**
  - The receiver `xrx` (flat netlist from `refbuf_hv.full()`) runs on `vdda`/`vddd`.
  - The clock generator `x1` runs on its own sources `vdda2`/`vddd2` at the same voltages, so its power can be read alone.
  - Loads equal the gate capacitance of what each output drives:
    - **60 fF** on cks/cksb (the 5 V sampling switch);
    - **40 fF** on ckg/ckgb/ckh/ckhb.

    If the SSPD design or 79 draws bigger switches, rerun with the new loads.
  - `.ic` puts the receiver's AC-coupled input at its self-bias point, so there is no 4 µs wait.
  - The run is 4 cycles with `tran 2p`. Every edge is read in the **last** cycle at VDDA/2, because all outputs swing 0–3.3 V.
- **Read-out** (all from one run):

| Name | from → to | Meaning | Requirement |
|---|---|---|---|
| t_s | REF_IN rise → cks fall | sampling instant | only stable, not small |
| skew_s | cks fall → cksb rise | complementary sampling pair | ≤ ±30 ps |
| gap1 | later of cks/cksb → ckg rise | switch open before Gm reads C | > 0 at every corner |
| τ | ckg rise → ckg fall | Gm pulse width | τ·K_VCO within ±15 % |
| skew_g | ckg rise → ckgb fall | complementary Gm pair | small vs τ |
| gap2 | later ckg/ckgb fall → ckh rise | Gm off before C1 → C2 sharing | > 50 ps |
| W_H | ckh rise → ckh fall | hold transfer time | ≥ 5 τ_settle of C1–C2 |
| t_p | cks fall → middle of ckg | loop delay | ≤ 5 ns |
| power | — | avg I(vdda2)·VDDA + I(vddd2)·VDDD | — |

- **Benches (`clkgen_hv_sim.py`).**
  - **A — timing (M16).** 25 conditions:
    - tt at nominal, at each supply limit, and at −40/110 °C;
    - ss/ff with matching supply limits;
    - **ss_hh / ff_ll** (MOS and R/C together, because τ is set by an R·C);
    - sf/fs and hl/lh;
    - 45/55 MHz;
    - the reference as a 3.3 V square, a 1 V sine, and a 0.4 V sine (the smallest allowed REF_IN amplitude).
  - **B — τ·K_VCO.**
    - Normalise τ at each corner to τ at tt.
    - Normalise K_VCO at that corner to K_VCO at tt (the VCO design: 173 / 110 / 250 MHz/V).
    - Multiply the two. The loop sees the product, so a long τ where the VCO is weak partly cancels.
  - **C — sampling-edge jitter (M17).** Same method as the reference-receiver design:
    - Build a flat copy of the receiver and the cks path (INV5S → INV5M → INV5L).
    - Put a white `trnoise` current at refhv, c1, c2 and cks. Each equals the trip-point noise of the stage that drives the node.
    - `path_noise()` gets those densities from `.noise` on one inverter biased at its own V_M.
    - NT = 4 ps, so NA = √(S_i/(2·NT)).
    - Measure 80 edges after 20 settling cycles.
    - Subtract a **noiseless baseline** run (all NA × 10⁻⁶) in quadrature.
    - Only S1's white jitter is left out here; the reference-receiver design covers it.
  - **D — supply sensitivity (M21, `clkgen_hv_supply.py`).**
    - Path: REF_IN → cks, with the receiver and the clock generator on the **same** rails.
    - AC: two runs from the same start. One has a 10 mV sine on VDDA (or VDDD) at f_m = 1, 5 or 20 MHz; the other has none.
    - The edge-by-edge difference is fitted to a sinusoid at f_m.
    - DC: a +10 mV step, with each run starting from its own settled bias.
    - cks is read at VDDA/2 of that instant.
  - **Noise budget (`clkgen_hv_noise.py`).**
    - The REF chain at 50 MHz is the sum of:
      - S1 white (reference-receiver design);
      - clock-generator white (from C, 1/f corner 30 kHz);
      - the VDDA and VDDD terms with the combined K(f) from D;
      - the SSPD buffer floor.
    - This chain then goes into the system model (`hv_system.py`) as the reference.
- **Results (tt, 27 °C).**
  - Timing:
    - t_s 425 ps, skew_s −11 ps, gap1 2.36 ns (the RC delay added after the Gm design);
    - τ 528 ps (322–951 ps over corners);
    - gap2 177 ps (min 108 ps, fs);
    - W_H 1.84 ns (1.20–3.31 ns; the hold ends ≤ 8.2 ns after the sample);
    - t_p 2.62 ns (≤ 4.15 ns).
  - Power 0.72 mW.
  - τ·K_VCO: 0.89 (ff_ll) to 1.14 (ss_hh).
  - Sampling-edge jitter 78 fs → −169.2 dBc/Hz.
  - Supply: VDDD 2.1 ps/V (was 377 via refclk), VDDA 148–175 ps/V (3.3 V square) and 323–1410 ps/V (1 V sine); REF chain -164.2 dBc/Hz typ.
- **Pitfalls.**
  - A 1.8 V-to-3.3 V level shifter cannot pass a 200–500 ps pulse at ss: the pulse is filtered away. So only **edges** cross the domains here:
    - `edges_g/h` make a start edge and a stop edge on VDDD;
    - each edge is level-shifted;
    - the pulse is rebuilt on VDDA as start AND NOT stop in `pout5`.
  - Read the pulse widths only at the **combined** corners. Plain ss/ff keep R and C typical and miss the τ extremes.
  - In the old architecture the sampling edge came through a VDDD level shifter and moved 376 ps/V with VDDD. Keep that result (`clkgen_hv_supply_via_vddd.json`) to compare with.
  - `tran()` asserts that every edge exists in the last cycle. A StopIteration means a pulse vanished; the bench reports it as `failed` instead of stopping the pool.
- **xschem.**
  - Place `xschem/clkgen_hv/sspll_clkgen_hv.sym` behind `xschem/refbuf_hv/sspll_refbuf_hv.sym`.
  - Sources: `vsource` + `res` 50 Ω on REF_IN; `isource` 2.5 µA on ib; `vsource` on VDDA/VDDD, with separate ones for the clock generator so its power can be read.
  - Loads: `capa` 60 fF on cks/cksb and 40 fF on the others.
  - A `code_shown` block holds the `tran` and `meas` lines.
- **Cadence.**
  - The same circuit with `vpulse`/`vsin`, `idc`, `vdc`.
  - Read the edges with the calculator's `cross(sig 1.65 n "rising"/"falling")` and `delay()`.
  - For C: transient noise, or pss + pnoise at the cks crossing.
  - For D: `vsin` with a delay on the rail.

#### 5 V SSPD benches (M17, M18, M19, M21) — `design/sspd/sspd_hv.py`
- **Purpose.** Prove four things:
  - the 5 V sampler has the detector gain the loop was designed for (A = 0.8 V/rad), at every corner;
  - the hold has the expected first-order memory;
  - switching the sampler does not disturb the ring;
  - the isolation buffers add little reference-like noise.
- **Common setup (`bench()`).**
  - DUT `sspll_sspd_hv` (both sides) plus the clock-generator clock generator, which makes all six clock phases from ideal edges:
    - refhv: 0–VDDA, the receiver's S2 node;
    - refclk: 0–VDDD, 0.2 ns later, as the receiver makes it.
  - The "ring": two ideal complementary 0/VDDA squares (60 ps edges), each behind a 5 V inverter sized like the ring's buffer output stage (1.2/3 µm). So clkp/clkm have a realistic source impedance, which matters for the kick-back.
  - Loads: 26 fF on each v1 (the first Gm's measured input; the final Gm has 26.5 fF with C1 0.5 fF larger, the same node) and 4 fF on each v2 (the NCB input).
- **Benches (`sspd_hv_sim.py`).**
  - **A — sampled characteristic (M18, `characteristic`).**
    - **Beat.** The ring runs at f = (16 + 1/32)·f_ref, so the sampling instant slides 2π/32 of a ring cycle per period. One 34-period run sweeps the whole characteristic: no phase sweep with 32 separate runs.
    - **Readings.**
      - v1p − v1m in the middle of each Gm pulse (what the Gm will read);
      - v2p − v2m 0.5 ns after each hold pulse;
      - A = half the slope of a line fit within ±0.35 rad of the zero crossing;
      - α and the hold DC gain from a least-squares fit of v2[k] = a·v1[k] + b·v2[k−1];
      - power = VDDA × average I(VDDA) of the SSPD.
    - **Conditions.** 18 in total:
      - tt at VDDA 2.97/3.3/3.63 V;
      - VDDD 1.71 V;
      - −40/110 °C;
      - ss_hh/ff_ll at both temperatures and both supply limits;
      - ss, ff, sf, fs, hl, lh;
      - 45/55 MHz.
  - **B — kick-back (M19, `kick`).**
    - The ring runs at exactly 16·f_ref, with the sampling instant on the zero crossing (locked).
    - Run 1: the clock generator switches.
    - Run 2: the reference is held, so the sampler tracks and nothing switches.
    - The difference of the clkp edge times is the kick-back. Its f_ref component, as the phase deviation 2π·f_0·Δt, gives the spur estimate 20·log(a1/2).
    - A third run with a 2 × 2 µm dummy capacitor (no real dummy) gives the f_ref supply current without the dummy sampler.
  - **C — isolation-buffer jitter (M17, `buf_jitter`).**
    - Flat path: ring buffer stage → XB1 → XB2 → R_s → C.
    - White `trnoise` currents at b1 and b2, each the trip-point noise of the inverter driving that node.
    - 800 MHz input, then a 4th-order detrend.
    - Run the noiseless baseline (sources × 10⁻⁶) and subtract it in quadrature.
    - The differential crossing sees σ/√2 (the two sides are independent).
  - **D — buffer supply sensitivity (M21 DC form, `buf_supply`).** Delay of the flat buffer path at VDDA and VDDA + 10 mV. The DC form is enough here: plain inverters have no bias loop or coupling capacitor, so their sensitivity is flat in frequency.
  - **Noise budget (`sspd_hv_noise.py`).** The clock-generator REF chain with the SSPD-buffer placeholder replaced by C and D. Then the system model, with the measured A and C_s (kT/C).
- **Results (tt, 27 °C, 3.3 V).**
  - A 0.811 V/rad (0.536–1.145 over the 18 conditions); α 0.451; hold DC gain 1.004.
  - CM 1.66 V; power 1.03 mW.
  - Kick-back 69 fs (spur −99 dBc); f_ref supply current 0.80 µA with the dummy vs 27.9 µA without.
  - Buffer jitter 83 fs per side (−171.6 dBc/Hz); buffer VDDA 22 ps/V.
- **Pitfalls.**
  - Use the combined MOS + R/C corners. A is set by R_s·C1, and plain ss/ff keep R and C typical.
  - A is proportional to VDDA. Always pair the slow corner with VDDA 2.97 V, or the minimum A is missed.
  - In the kick-back runs, read the edges of clkp (the shared buffer output), not of b1. The kick-back that matters is what reaches the ring side.
  - The beat run's first two periods carry the start-up of the RC nodes: they are skipped (s < 2T).
- **xschem.**
  - Place `xschem/sspd_hv/sspll_sspd_hv.sym` and `xschem/clkgen_hv/sspll_clkgen_hv.sym`.
  - Sources: `vsource` pulse for refhv, refclk, vp and vm, each behind an inverter from the PDK symbols (5 V devices).
  - Loads: `capa` on v1/v2.
  - A `code_shown` block with `tran 2p 680n` and `wrdata`.
  - Post-processing as in `characteristic()`.
- **Cadence.**
  - The same with `vpulse`.
  - Characteristic: read v1p − v1m at the Gm-pulse times with the calculator's `value(sig time)` on a time list, or run pss with the beat frequency as the fundamental.
  - Kick-back: two transients and `cross()` on clkp.
  - Buffer jitter: transient noise or pss + pnoise.

#### 5 V pulsed-Gm charge pump benches (M10, M11, M16, M18) — `design/sscp/sscp_hv.py`
- **Purpose.** Prove six things:
  - with its real detector in front, the Gm gives the loop gain the loop design designed for (β = 2A·G·τ/T = 0.79 µA/rad), and the lock point sits inside the Gm's linear range;
  - G holds over corners, V_cont and the trim codes;
  - steering the output between the filter and the dump node leaves little charge per period;
  - the dump node is held at V_cont over the whole window;
  - the pump's noise and its VDDA rejection fit the budget;
  - the trim decoder sets the right number of slices.
- **The most important lesson of this step: test a block with its real neighbour.**
  - The first Gm passed every bench with DC sources on v1.
  - Only the whole-detector bench (bench B below) showed what the SSPD's real waveform does to it: v1 tracks the 800 MHz ring for half of every period.
  - That bench found three faults: the mirror was too slow, the dump node rippled, and the Gm needs recovery time.
- **Common setup (`head()`).**
  - DUT `sspll_sscp_hv`: five slices, the replica bias, two steering TGs, the dump buffer and 2 pF.
  - v1p/v1m are ideal sources around 0.503·VDDA (the SSPD's sampled common mode).
  - vctl is an ideal source at V_cont. The current into it, `i(vvc)`, is the current into the loop filter. A source is used because the filter holds V_cont nearly constant over one period, and the source measures every femtocoulomb.
  - ib: 2 µA from an ideal current source (the bias generator's unit).
  - e1–e5 and eb1–eb5: ideal sources at the code's pattern (00 → 3 slices, 01 → 4, 10 → 2, 11 → 5).
- **Benches.**
  - **B — whole detector (M18 extended, `sscp_hv_det.py`).**
    - Setup: the SSPD beat bench (ring at (16 + 1/32)·f_ref behind a 5 V buffer stage, the real clock generator) with the real Gm on v1 instead of the placeholder capacitor.
    - Readings:
      - every period, the charge into vctl (integral of `i(vvc)` from 1 ns before the sample over one period);
      - the ring phase at the sample;
      - vdump − vctl just before the pulse.
    - β_eff = (slope of charge vs phase at the charge's zero) / T, from a cubic fit within ±0.6 rad. The zero itself is the lock point.
    - Conditions: tt at V_cont 1.3 / 1.8 / 2.3 V, ss_hh 110 °C at 2.97 V, ff_ll −40 °C at 3.63 V.
  - **Recovery sweep (`sscp_hv_delay.py`).** The locked detector with ckg/ckgb from ideal sources at 0.7 / 2 / 3 / 4.5 ns after the sample. Two lock phases give the gain per volt; the charge at lock gives the static error. This set the clock-generator design's gap-1 delay.
  - **A — DC transfer (M10, `dc_transfer`).**
    - ckg held high, so x is connected to vctl.
    - `dc` sweep of v1p − v1m over ±0.8 V.
    - G = the slope at 0 V; offset = −I(0)/G; linear range = where the slope stays within 10 % of G.
    - Conditions: 11 corners at V_cont 1.8 V; V_cont 1.3 / 2.3 V at tt, ss 110 °C and ff −40 °C; codes 01/10/11 at tt.
  - **D — dump buffer (`buffer_check`).** `op` gives vdump − vctl; `ac` with 1 V on vctl gives |vdump/vctl| (peaking, f_3dB). 5 corners × V_cont 1.3 / 1.8 / 2.3 V.
  - **Pulsed with DC inputs (M16, `pulsed`).** The real clock generator makes ckg/ckgb from ideal refhv/refclk edges; v1 is DC. Integrate `i(vvc)` over 4 periods. This isolates the steering: switch injection and dump error, without the Gm's recovery.
  - **C — noise (M11, `noise`).**
    - `.noise` of the current into vctl: vvc is split by an ammeter `vmeas`, and a CCVS `h1` turns that current into a voltage.
    - In the system the current noise is gated with duty d = τ/T, so it becomes S_φ = S_i/(4A²G²d) (`sscp_hv_noise.py`).
    - To find the devices responsible: `noise ... 1` (one summary point per decade) and `setplot noise2; print all` give each device's integrated contribution (`sscp_hv_noisesize.py` uses this breakdown).
  - **E — VDDA rejection (M11, `psr`).** `ac` with 1 V on VDDA and zero input gives |i(vvc)| per volt; it acts only during the pulse, so S_φ = |Y|²S_v/(2AG)². The same run's `op` gives I(VDDA).
  - **Input capacitance (`sscp_hv_cin.py`).** `ac` with 1 V on v1p gives C_in = Im(I)/(2πf) at 50–200 MHz, for every code, ckg on/off, three corners. The SSPD's C1 is sized with it.
- **Results (tt, 27 °C, final design).** G 18.51 µS (17.5–19.6 over corners and V_cont); offset ≤ 12 mV; linear ±0.38 V at tt (≥ ±0.23 V); codes ×0.67 / 1 / 1.33 / 1.66. Whole detector: β_eff 0.81 µA/rad at tt (0.79 with the final C1), lock point −74 to −129 mrad, β_eff 0.69–0.81 over the corners. Dump buffer ≤ 11.7 mV, f_3dB ≥ 5 MHz with 2 pF. Pulsed with DC inputs: 9.0 fC/V (G·τ = 9.5), +0.58 / +0.24 / −0.11 fC at V_cont 1.3 / 1.8 / 2.3 V. Noise 3.9 / 1.48 pA/√Hz at 10 kHz / 1 MHz → 224 fs in the system. VDDA → 1.08 µA/V at 1 MHz (6 fs). C_in 26.5 fF. I(VDDA) 90 µA.
- **Pitfalls.**
  - A DC-input bench cannot reveal a slow internal node: the node is always settled. Test with the real waveform (bench B) before believing a pulsed circuit.
  - Sign: `dc_transfer` records −i(vvc), the current the source pushes *out* into the circuit. With v1p > v1m the Gm pushes current into vctl, so that slope is negative (G is reported as its magnitude). The loop polarity follows from this sign.
  - In bench A ckg is a static 3.3 V, so the dump path plays no part; bench D covers it separately.
  - `lvs.sh` used to read only netgen's topology line. A multiplier drawn ×1 against ×12 in the netlist still read "match"; the script now also prints netgen's property errors.
- **xschem.**
  - `xschem/sscp_hv/sspll_sscp_hv_top.sym` (with the decoder) or `sspll_sscp_hv.sym` (enables as pins).
  - `vsource` for v1p/v1m, vctl and VDDA; `isource` for ib.
  - For C: an ammeter `vsource 0` in series with vctl and a `ccvs`.
  - Bench B: the SSPD bench schematic with this symbol on v1.
- **Cadence.**
  - The same with `vdc`/`idc`; Spectre `noise` takes `i(vvc)` as the output directly, and its noise summary sorts the contributors.
  - E: `ac` with `acm=1` on VDDA.
  - B: a transient and the calculator's `integ(i(vvc) t1 t2)` per period.

#### 5 V loop-filter benches (M24, M25) — `design/loop/lf_hv_sim.py`
- **Purpose.** Prove four things about the filter as it is built from PDK devices:
  - its three elements R1, C1, C2 have the values the loop needs, with everything else on vctl counted;
  - those values hold over corners, temperature and V_cont well enough that PM ≥ 45° after the trim;
  - the 3-element model used by the loop analysis describes the real network;
  - its noise and leakage are what the budget assumes.
- **M24 — large-signal-averaged port capacitance (part `load`).**
  - **What.** The capacitance that a slow signal sees at an input whose devices are switching fast: here the ring's
    tuning gates, whose capacitance follows the 800 MHz swing.
  - **Why not AC.** An AC analysis linearises at one DC point, which is one instant of the oscillation. The filter sees
    the charge per volt averaged over many cycles.
  - **How.** Transient of the running ring (`vco_hv.netlist`, hl6, 0.994 mA) with vtune = V_cont + 50 mV·sin(2π·25 MHz·t).
    After 40 ns of start-up, the current out of the vtune source is multiplied by cos(ωt) and sin(ωt) and integrated
    over 400 ns (10 sine periods, about 320 ring periods). C = in-phase amplitude/(ω·50 mV); G = quadrature
    amplitude/50 mV.
  - **Choices.** 25 MHz is far below 800 MHz (the ring current averages out) and far above the loop bandwidth.
    50 mV is small enough to be linear and large enough to beat numerical noise. The window holds whole periods of
    the sine, so the DC and the 800 MHz terms integrate to zero.
  - The Gm port is a plain AC at its operating point (it has no fast internal waveform when ckg is static), with the
    steering TG off and on, weighted by the duty τ/T.
- **M25 — passive-network extraction and exact sampled loop (parts `size`, `corners`, `loop`).**
  - **DUT.** `sspll_lf_hv` alone: vctl driven by `vvc` (DC = V_cont, AC = 1). The admittance Y = −I(vvc).
  - **Analysis.** `ac dec 10 1e4 5e7`, then a least-squares fit of Y = sC2 + 1/(R1 + 1/(sC1)) on log-magnitude and
    phase. The fit returns R1, C1, C2 and the worst relative error of the model below 25 MHz.
  - **Sweep.** 5 MOS × 5 R/C corner sections (e.g. `ss_hh`) × −40 / 27 / 110 °C × V_cont 1.3 / 1.8 / 2.3 V. The MOS
    capacitor follows the MOS letter, R1 and the MIMs follow the R/C letters.
  - **Loop.** The extracted values plus the M24 load go into `sampled_loop.py` (matrix-exponential solution over one
    reference period with the packet injected t_p after the sample). It gives f_c, PM, closed-loop peaking, f_3dB and
    the settling of a 1 rad step.
  - **Sizing.** With C1 fixed, a 2-variable solver finds R1 and C2 for f_c = 2.5 MHz and PM = 50°. The R1 segment
    length and C2 width are updated from the result (699.2 Ω/µm, MIM 2.0 fF/µm² + 0.164 fF/µm), and the
    simulate–fit–solve loop repeats until f_c is within 5 kHz and PM within 0.1°.
- **Noise (part `noise`).** `iin` (AC 1) into vctl, a 1 TΩ `noisy=0` resistor to a 1.8 V source for the DC point,
  `.noise v(vctl) iin`. **`option sparse` is required:** ngspice's KLU solver does not support noise. Run twice:
  drawn R1, and R1 replaced by an ideal resistor of the fitted value. The SKY130 poly resistors are behavioural, so
  ngspice gives them **no thermal noise**: only the second run shows 4kTR1.
- **Leakage (part `leak`).** `op` with vctl held at 1.3 / 2.3 V, hot corners. The current into the filter is its
  leakage.
- **Packet (part `pulse`).** A 0.53 ns current pulse carrying the charge of 0.1 rad into the drawn filter plus the
  175 fF load. Compared with the closed-form response of the 3-element model. **Start from the operating point:** with
  `uic` the MOS capacitor's internal charge is not at equilibrium, and vctl drifts by millivolts.
- **xschem.** `xschem/lf_hv/sspll_lf_hv.sym`; `vsource` on vctl with `value="dc 1.8 ac 1"`; an `.ac` and a
  `.control` block with the fit done in Python on the `wrdata` output.
- **Cadence.** The same circuit with `vdc` (`acm=1`); Spectre `ac`, then `xf` or the calculator for Y. For noise use
  Spectre `noise`; check whether the Cadence kit's poly resistor carries thermal noise (Spectre's own resistor with
  a voltage coefficient does). The lock-in of M24 is a `tran` plus the calculator's `integ(i*cos)`.

#### FLL benches (M26, M27) — `design/fll/fll_hv_acq.py`, `fll_hv_sim.py`, `fll_hv_closed.py`
- **Purpose.** Show three things:
  - the FLL brings the ring to 16 × f_ref from any start (V_cont 0–3.3 V, any phase, all corners) and hands over to
    the sub-sampling loop without a fight;
  - each circuit does what the model assumes: divider speed, charge-pump current, dead zone, lock-detector windows;
  - the transistor-level FLL in closed loop follows the model.
- **M26 — fixed-step behavioural simulation of a dual-loop PLL (`fll_hv_model.py`, `fll_hv_acq.py`).**
  - **What.** Every block reduced to its measured law, stepped every 50 ps over 6–12 µs:
    - ring: f(V_cont) from the VCO tuning curve;
    - divider: an edge every 16 ring cycles, t_div later;
    - PFD: tri-state with reset time, dead zone, and a ±I_cp pump;
    - SSPD + Gm: the Gm charge curve q(φ), delivered t_p after the sample;
    - lock detector: the logic of `sspll_fll_lockdet`.
    - The filter state is updated with the exact matrix exponential of C2 ∥ (R1 + C1) for each step.
  - **Why.** Acquisition takes µs of 800 MHz cycles. A transistor-level PLL run of that length takes hours per case,
    and the sweep needs 900 cases. Linear models cannot show cycle slips, harmonic locking, dead zones or the hand-over.
  - **How it was trusted.** One case was compared with a transistor-level run (M27). The block laws come from the
    benches below.
  - **Sweeps.** 5 start voltages × 3 corners × 4 start phases for every parameter set: I_cp, window w_in, count,
    gain ×0.6 / ×1.5, t_p 1.8 / 4.2 ns, t_div 0.5 / 2 ns. Pass = 800.000 MHz, lock_det high for the last 40
    periods, and the phase settled. Lock time = the last moment the ring phase was more than 10 ps from its final
    value.
  - **Part E.** The same model with the FLL off, started near 700, 750, 850 and 900 MHz. It shows why the FLL is
    needed: the sub-sampling loop locks to whatever multiple of 50 MHz is nearest.
- **Divider bench (`fll_hv_sim.py div`).** A 0..VDDA square with 60 ps edges drives `sspll_fll_div16`, and the bench
  checks that every output period is 16 input periods (±2 %). It bisects between 1 and 6 GHz, at 5 corners with
  VDDD at its limits. **Why:** if the divider cannot follow the fastest ring, it outputs fewer edges. The PFD then
  reads "too slow", pushes the ring faster still, and the loop locks up at the rail. The divider must therefore be
  faster than the ring at its fastest (code 31, V_cont = 0) at every corner.
- **Charge-pump bench (`fll_hv_sim.py cp`).** `sspll_fll_cp` alone. vctl is held by a source at 0.3–3.0 V, up5 and
  dn5 are driven statically, and the source current is the pump current. Run at 3 corners × IBIAS ±20 %. Off-state
  leakage is measured with act5b = 1 at 110 °C.
- **Open-loop bench (`fll_hv_sim.py open`, `fll_hv.bench_open`).** The whole `sspll_fll_hv`:
  - clkp is a square 0.2 % faster than 800 MHz, so the divider edge walks 40 ps per period across the reference
    edge;
  - vctl is held at 1.8 V by a source, and the charge per period is ∫i(vvc) over one period centred on the
    reference edge;
  - the run lasts 2.2 µs, about 110 periods.
  - **One run gives the whole transfer:** charge vs Δt (the dead zone and the ±I_cp slope), the lock_det rise after
    16 in-window periods, the switch to the 2 ns window, and the release after 4 out-of-window periods (hysteresis).
- **M27 — closed loop with a behavioural ring (`fll_hv_closed.py`).**
  - **The ring is replaced by a phase integrator.** A B-source current f(V_cont) (a `pwl` table from the VCO
    curve) charges a 1 F capacitor, so v(phi) counts cycles. `clkp = 1.65·(1 + tanh(6·sin 2π·v(phi)))` turns it into
    a 0..3.3 V clock.
  - **Everything else is real:** the transistor-level FLL and the drawn loop filter plus 175 fF of load.
  - **Why behavioural.** The real ring would add about 30 % of the run time and nothing the FLL test needs; the ring
    itself was verified in the VCO design.
  - **Start.** A 1 GΩ resistor to the start voltage sets the DC point (τ = 10 ms, invisible in a few µs).
    `option interp` keeps the output file small.
  - **Compared with:** the M26 model with the sub-sampling loop off, same start.
- **xschem.** `xschem/fll_hv/sspll_fll_hv.sym`; the standard cells come from `sky130_stdcells/*.sym` (pins A, B, X / Y
  and supplies as properties). Include `design/fll/stdcells/sky130_fd_sc_hd_fll.spice` (`.include`) in the testbench,
  because the PDK installation here has no standard-cell SPICE.
- **Cadence.** Use the kit's standard-cell views (or import the same SPICE with `spiceIn`); the divider and open-loop
  benches are `tran`, and the charge per period is `integ(i("/vvc/PLUS") t1 t2)`. The behavioural ring is easiest as
  Verilog-A (`V(clk) <+ 1.65*(1 + tanh(6*sin(2*`M_PI*phase)))` with `phase = idt(f(V(vctl)))`).

#### Diff-to-SE amplifier benches (M28–M30, M18, M19, M21) — `design/d2s/d2s_hv_sim.py`
- **Purpose.** Show that the D2S turns v2p − v2m into vff with a steady gain, fast enough, quiet enough and with a
  supply-independent rest level, and that it does so with the real SSPD in front of it.
- **M28 — amplifier characterisation (parts A, B, G).**
  - **DUT.** `sspll_d2s_hv` with ideal sources: VDDA, ib = 2 µA (`iib VDDA ib`), en_b, 40 fF on vff (the NCB input).
  - **DC transfer (A).** B-sources put inp = CM + v_d/2 and inm = CM − v_d/2; `dc vd -0.5 0.5 0.005`. CM is the SSPD's
    measured sampled common mode at that condition (it tracks VDDA). From vff(v_d): V_0 (v_d = 0), G = dvff/dv_d at 0
    and its minimum over the lock window (v_d = −0.10…+0.30 V), and the range where G stays within 10 %.
  - **AC (B).** inp = AC +0.5, inm = AC −0.5 at the lock-window bias (v_d = 0.18 V): |G(f)|, f_3dB, phase at f_ref/7.8.
  - **Input capacitance (B).** One input AC 1 V, the other AC 0, `ac lin 1 1e6 1e6`; C = Im(I)/(2π f). It includes the
    Miller part from vff, which is why the two inputs differ.
  - **Enable (G).** The DC sweep again with en_b = VDDA: vff must stay at V_0 whatever the input.
  - **Why this way:** the D2S is used at DC-to-tens-of-MHz signals around a bias point, so DC and AC at that point
    describe it; the sweep over the window shows what happens away from the point.
- **M29 — noise to output timing (part C).**
  - One differential source `vd` (AC 1) drives the inputs through two E-sources (±0.5), so `.noise v(vff) vd` refers
    the noise to the differential input.
  - **`option sparse`** (KLU does not support noise) and **every poly resistor replaced by an ideal R of the same value**
    (`ideal_r()`: the value is measured with an `op` at that corner and temperature). The SKY130 poly resistors are
    noiseless in ngspice; without this step R_DEG and R_L (about half of the white noise) would be missing. A second run
    with the PDK resistors gives the transistor-only spectrum.
  - **Conversion:** after calibration the chain makes 1/K_t seconds of NCB delay per volt at the D2S input, so
    S_t(f) = S_v,in(f)/K_t², with K_t = 2·dv/dt of the SSPD at the same condition. The jitter is √∫S_t df from 10 kHz to
    40 MHz; it adds at the output with transfer one.
- **M21 — supply (part D).** `vdda` gets `ac 1`. Two cases: inputs at a fixed CM, and inputs as E-sources from VDDA
  (CM/VDDA = the SSPD's ratio), because the real CM follows VDDA. A third run moves only the CM. K_s = max |vff/VDDA| up to
  40 MHz divided by G·K_t: the output timing per volt of VDDA.
- **M30 — mismatch Monte Carlo (part F).** `.param mc_mm_switch=1` after the `.lib` line switches on the per-device
  mismatch of the SKY130 models; `setseed N` in the `.control` block gives each run its own draw. 60 runs of a short
  DC sweep: V_0 and G. **Why:** the offset sets where the NCB sits, the gain spread what the calibration must cover.
- **Whole path (part E, M18).** The SSPD bench (`sspd_hv.bench`: SSPD + clock generator, ring = squares at
  (16 + 1/64)·f_ref, so the sampling phase walks 2π/64 per period) with the D2S core instead of the 4 fF placeholder on
  v2. Per period: v2p − v2m and vff just before the next hold, against the phase. Slopes near the crossing give the gain of
  the whole path. **Why:** it checks the D2S with the real hold waveform and with its own capacitance on C2.
- **Lock ripple (part H, M19).** The same bench with the ring at exactly 16·f_ref (nb = 10¹⁵) and the sampling phase
  set φ0 from the crossing, as the SSPD's kick-back bench. vff over the last periods: its f_ref component a1 becomes an
  NCB delay modulation a1/(G·K_t) every period, i.e. a reference spur 20·log(π f_0 Δt_1).
- **xschem.** `xschem/d2s_hv/sspll_d2s_hv.sym`; two `vsource` on the inputs (`value="dc 1.75 ac 0.5"` and
  `"dc 1.57 ac -0.5"`), an `isource` for ib, a `capa` 40f on vff; `.dc`, `.ac`, `.noise` in a `code_shown` block; add
  `.param mc_mm_switch=1` for Monte Carlo.
- **Cadence.** Same benches with `vdc` / `idc`; Spectre `dc`, `ac`, `noise` (check whether the kit's poly resistors
  carry thermal noise), `montecarlo` with mismatch only; the whole path is the SSPD testbench with the D2S symbol on v2.

#### moscap_hv_cv — C-V of the 5 V loop-filter capacitor (M6)
- **Purpose.** The loop design needs the capacitance per area of the thick-oxide MOS capacitor that now forms C1, and the
  V_cont range over which it is flat. It also needs MIM1 and MIM2 for comparison.
- **Setup.** `design/loop/spice/moscap_hv_cv.sp`, three independent one-device circuits, each driven by its own source (DC bias + AC 1):
  - X1: nfet_g5v0d10v5, W = L = 10 µm. Gate on the source; drain, source and body on ground. This is the capacitor exactly as it sits in the tile.
  - X2: cap_mim_m3_1, 30 × 30 µm.
  - X3: cap_mim_m3_2, 30 × 30 µm.
- **How it works.**
  - At each DC point, `ac lin 1 1e6 1e6` gives the small-signal current, and C = −Im(I)/(2π·1 MHz).
  - 1 MHz is well below any RC corner of a 100 µm² gate, so the result is the pure capacitance.
  - `foreach` steps the bias from 0 to 3.3 V with `alter`.
  - `run_cv_hv.sh` loops over tt/ss/ff and −40/27/110 °C and appends `corner,temp,vg,c_mos_fF,c_mim1_fF,c_mim2_fF` to `design/loop/data/moscap_hv_cv.csv`.
- **Result (tt, 27 °C).**
  - MOS: 2.87 fF/µm² at 1.65 V; 2.81 at 1.0 V; 2.90 at 2.3 V; 1.3 at 0 V.
  - MIM1 and MIM2: 1.820 pF per 30 × 30 µm each.
  - Over 1.0–2.3 V and all corners the MOS cap stays within ×0.93–1.06 of its value at 1.65 V.
- **Run.** `PDK_ROOT=/path/to/pdk design/loop/spice/run_cv_hv.sh` (about 20 s).
- **Pitfall.** Tie the body to the source/drain (ground). A floating or separately biased body changes the curve.

#### Device noise at fixed g_m/I_D — 5 V vs 1.8 V devices (M20, the system budget)
- **Purpose.** The budget for 800 MHz assumes that a ring built from 5 V devices can reach the VCO FoM.
  This bench checks that assumption at the device level: thermal-noise factor γ, 1/f corner and flicker voltage for
  each device family and length used in the analog blocks.
- **Setup.** `design/feas/hv_noise.py`, one transistor, with no testbench schematic:
  - The gate is driven by `vg` (DC bias plus AC 1); the drain is held at V_DS by `vd`. That is 0.9 V for 1.8 V devices and 1.5 V for 5 V devices; a pMOS is referred to its own source supply.
  - A CCVS `h1 o 0 vd 1` turns the drain current into the output voltage `v(o)`, so `.noise v(o) vg` gives the drain-current noise PSD directly (onoise) and the gate-referred voltage (inoise).
- **How the operating point is set.**
  - One `dc vg` sweep on a 10 µm device gives I_D(V_GS), and g_m/I_D = d ln I_D/dV_GS.
  - The script takes the V_GS where g_m/I_D falls to 10, searching above the g_m/I_D peak so that the leakage region at low V_GS is skipped.
  - It then scales W to 100 µA, in fingers of at most 40 µm, because the model bins end near 100 µm.
  - Equal g_m/I_D and current mean equal g_m, so every remaining difference is the device's own noise.
- **Read-out.**
  - γ = onoise²(1 GHz)/(4kT·g_m), with g_m = √(onoise²/inoise²) at 1 GHz.
  - The 1/f corner is the frequency where onoise² is twice its 1 GHz value.
  - v_n(10 kHz) = inoise at 10 kHz.
- **Result (tt, 27 °C).**
  - 5 V nMOS, L = 0.5 µm: γ 1.10, corner 50 MHz.
  - 5 V nMOS, L = 1 µm: γ 1.46, corner 2.5 MHz.
  - 5 V pMOS, L = 0.5 µm: γ 0.53, corner 2.0 MHz.
  - 5 V pMOS, L = 1 µm: γ 0.55, corner 0.2 MHz.
  - 1.8 V nMOS, L = 0.15 µm: γ 1.87, corner 158 MHz.
  - 1.8 V pMOS, L = 0.15 µm: γ 1.22, corner 1.0 MHz.
- **Run.** `python3 design/feas/hv_noise.py` → `design/feas/hv_noise.json`, about 1 min.
- **Pitfalls.**
  - One `.op` per V_GS point means one PDK load per point: 600 launches took more than 10 min. Use one `dc` sweep per device.
  - A high-V_T device can show g_m/I_D < 10 at V_GS = 0.3 V because of leakage. Search above the peak.
  - Very wide devices fall outside the model bins and give an empty `.noise` output. Use `m` fingers.

### Grounds in the benches: VSSA and VSSD (24 Nov 2026)

Since the ground split, see `docs/design/ground_split.md`:
- Every 5 V cell has VSSA (analog ground), VSSD (digital ground), or both.
- A mixed cell (level shifter, receiver, clock generator, CCO, charge-pump decoder and top) has both, side by side in its port list. A bench passes two ground nodes to it: `x1 ... VDDD VDDA 0 0 sspll_clkgen_hv`.
- A bench that pastes a cell's body at the top level must define both nets: `vssa VSSA 0 0` and `vssd VSSD 0 0`.

**Why ideal 0 V on both.** Pre-layout there is nothing between the two grounds. A noise or bounce model now would be a guess, because the ground resistance, the package and the digital current are only known after layout. With both at 0 V, a bench simulates exactly the circuit it did before the split. Method M23 proves this by comparing the netlists with VSSA = VSSD, so the block designs needed no re-run.

**Post-layout.** The top-level bench replaces the two ideal grounds with:
- the extracted VSSA and VSSD;
- a package model on each: about 1–2 nH bond wire plus its resistance, to the harness ground;
- the real digital switching current.

Only then can ground bounce appear in the sampling-edge jitter and the charge-pump error.

**Pitfalls.**
- A bench that still passes one ground node to a mixed cell fails with a node-count error in ngspice. `tools/ground_split_check.py check` finds such lines without running anything.
- In a flattened body, VSSA or VSSD left undefined is a floating node, not ground. ngspice does not always complain; the operating point just goes wrong.

---

---

## 4. Drawing a testbench in xschem (same recipe for every bench)
1. `xschem --rcfile xschem/xschemrc` → *File → New schematic*, save it as `xschem/tb/tb_<name>.sch`.
2. **DUT:** *Insert symbol* (Shift-I) → `xschem/<block>_hv/sspll_<cell>.sym`. Its pins are the same as the `.subckt`
   line in the block's reference netlist `xschem/netlist/ref_<block>_hv.spice` (written by `tools/lvs_hv_all.py`).
3. **Sources:** from `devices/`: `vsource.sym` (supplies, DC levels, `sin(…)`, `pulse(…)`, `pwl(…)`, `trnoise(…)` in
   the *value* field), `isource.sym` (IBIAS, an ideal current DAC), `capa.sym` (loads), `res.sym` (50 Ω source
   impedance), `gnd.sym`. Watch the source arrow: it shows the current direction. For a behavioural neighbour use
   `bsource.sym` with `VALUE="I = pwl(v(node), …)"`.
4. **Grounds:** a mixed cell has VSSA and VSSD pins; connect both (to `gnd.sym` before layout).
5. **Labels:** `lab_pin.sym` on every net you want to plot or measure.
6. **Models and corner:** the `sky130_fd_pr/corner.sym` symbol, which holds the `.lib … tt` line, or a `code_shown.sym`
   block with `.lib`, `.temp` and `.param` lines.
7. **Analysis:** a second `code_shown.sym` block, with the property `value=` holding the whole `.control … .endc`
   section. Set `only_toplevel=true`.
8. *Netlist* → *Simulate* (or `ngspice -b` on the netlist in `xschem/simulations/`). Load the `.raw` file in xschem's
   graph (`devices/launcher.sym` + `graph.sym`) to look at waveforms.

## 5. The same testbenches in Cadence Virtuoso (Spectre)
1. Import the DUT: the reference netlists `xschem/netlist/ref_<block>_hv.spice` (hierarchical, same cell names as the
   schematics), or redraw from the xschem PNGs in `docs/img/`. Then create a testbench cell with `analogLib` sources
   (`vdc`, `idc`, `vsin`, `vpulse`, `vpwl`, `cap`, `res`).
2. ADE L / Explorer → *Setup → Model Libraries*: the kit's `sky130.lib.scs`, section `tt` (or `ss`, `ff`…).
   *Setup → Temperature*.
3. Analyses, by the table in section 2:
   - `dc` with *save DC operating point* for M10;
   - `ac` with the AC magnitude on the supply source for supply rejection;
   - `noise`, output = the net or the probe current, input source = the one with AC magnitude, for M3/M11/M14;
   - `tran` for M1/M13/M16.
4. **Transient noise (M15, M17).** Spectre can do device noise in transient: *tran → Transient Noise → noisefmax*
   (e.g. 50 GHz), *noiseseed*. No injected source is needed, which makes it a good cross-check of the ngspice method.
   Better still for jitter: **pss + pnoise** with *jitter* output.
5. **Measurements.** The ADE *Calculator*: `cross()` for edge times, `frequency()`, `average()`, `delay()`,
   `dutyCycle()`, `riseTime()`. Save them as outputs and sweep with *Parametric Analysis*. Corners go in the *Corners*
   setup.
6. **Ring start-up.** Use *ic* on the ring nodes (Simulation → Convergence Aids → Initial Condition) or a short
   current pulse.

## 6. From one bench to the full characterisation
The scripts build the circuits as strings, run them in parallel over the conditions, and save the numbers to
`design/<block>/data/*.json`. The plots in `docs/img/` come from those files.

| Block | Scripts (`design/<block>/`) |
|---|---|
| Budget, the system budget | `budget/budget_hv.py`, `hv_system.py`, `budget_hv_plots.py`; devices `feas/hv_noise.py`, `feas/hv_vco.py` |
| Loop | `loop/loop_hv.py`, `loop_hv_plots.py` |
| Ring VCO | `vco/vco_hv.py`, `vco_hv_point.py`, `vco_hv_char.py`, `vco_hv_startup.py`, `vco_hv_system.py` |
| Current DAC | `cco/cco_hv.py`, `cco_hv_sim.py`, `cco_hv_noise.py`, `cco_hv_casc.py`, `cco_hv_headroom.py`, `cco_hv_vdda.py` |
| REF receiver | `refbuf/refbuf_hv.py`, `refbuf_hv_sim.py`, `refbuf_hv_noise.py`, `refbuf_hv_supply.py` |
| Clock generator | `clkgen/clkgen_hv.py`, `clkgen_hv_sim.py`, `clkgen_hv_size.py`, `clkgen_hv_noise.py`, `clkgen_hv_supply.py` |
| SSPD | `sspd/sspd_hv.py`, `sspd_hv_sim.py`, `sspd_hv_size.py`, `sspd_hv_noise.py`, `sspd_hv_check.py` |
| Pulsed-Gm charge pump | `sscp/sscp_hv.py`, `sscp_hv_sim.py`, `sscp_hv_det.py`, `sscp_hv_delay.py`, `sscp_hv_buf.py`, `sscp_hv_cin.py`, `sscp_hv_size.py`, `sscp_hv_noise.py` |
| Loop filter | `loop/lf_hv.py`, `lf_hv_sim.py`, `lf_hv_plots.py`, `schematics_hv.py` |
| FLL | `fll/fll_hv.py`, `fll_hv_model.py`, `fll_hv_acq.py`, `fll_hv_sim.py`, `fll_hv_closed.py`, `fll_hv_plots.py`, `schematics_hv.py` |

When you change a design, rerun the block's `schematics_hv.py`, then `python3 tools/lvs_hv_all.py`, then the step
scripts: LVS first shows whether the drawing still matches what is simulated.
