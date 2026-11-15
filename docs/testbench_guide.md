# Testbench guide: how every simulation in this project is set up, why, and how to rebuild it yourself

This guide covers every testbench used so far (steps 74–76) and will be extended with each new block. For every
testbench there is a **stand-alone ngspice deck** in `tb/`. Each deck has comments on every line and can be run
without any of the Python scripts. The Python scripts in `design/<block>/` run the same decks in loops over corners,
amplitudes, codes and so on. The *method* behind each testbench (what / why / how / limits) is recorded as M1…M16 in
`docs/methods.md`, and the list is also in `design/SSPLL_design_log.xlsx`.

---

## 0. Two direct answers first

### "How did you check LVS? Did you make a layout?"
**No layout exists yet.** Layout starts in phase 9. What I ran so far is **schematic-vs-netlist** LVS. It answers this
question: *is the schematic I drew exactly the circuit I simulated?* It catches wrong wiring, swapped pins, wrong sizes
and missing devices in the drawing. It does **not** check a layout.

How it works (`xschem/lvs.sh`):

1. **xschem netlists the drawn schematic** in LVS format: the top cell becomes a `.subckt`, with real device names and
   sizes. The command is `xschem -x --tcl "set lvs_netlist 1" --command "xschem set format lvs_format; xschem netlist"`.
2. The **reference netlist** is the netlist the simulations use. It is written by the design script, for example
   `cco.full()` or `refbuf.full()`. It is the same text as `tb/dut/*.spice`.
3. **netgen** compares the two, using the PDK's setup file `sky130A/libs.tech/netgen/sky130A_setup.tcl`. That file says
   which device parameters must match (W, L, nf, m, resistor length…) and which devices may be merged.
   The result is either `Circuits match uniquely` or a list of mismatched nets and devices.

To run it yourself:
`cd xschem && PDK_ROOT=<pdk> ./lvs.sh refbuf/sspll_refbuf.sch netlist/ref_refbuf.spice sspll_refbuf`.
Create the reference first, for example `python3 -c "import refbuf; open('netlist/ref_refbuf.spice','w').write(refbuf.full())"`
from `design/refbuf`, or simply use `tb/dut/sspll_refbuf.spice`.

**The real LVS comes in the layout phase:**
1. Magic extracts the layout: `extract all; ext2spice lvs; ext2spice`. This gives the devices and connections that are
   really drawn.
2. netgen compares that extracted netlist with the **same** xschem netlist.
3. Then DRC (Magic and KLayout) and parasitic extraction (`ext2spice cthresh 0`) for post-layout simulation.

The schematic-vs-netlist check done now guarantees that the schematic, the reference for layout LVS later, is the
circuit that was verified.

### What I found while writing this guide
The step-74 VCO scripts (`design/vco/vco.py`) ran ngspice **without** the PDK's `.spiceinit`. That file sets
`ngbehavior=hsa`, the HSPICE-compatibility mode the sky130 model files are written for. The CCO, the reference buffer
and every deck in `tb/` do load it.

With the correct setup, the same ring at the same current runs **4.6 % faster**:
- 1.676 instead of 1.602 GHz at 1.437 mA, tt;
- its ring node sits about 50 mV lower.

Corrected f(I) from `tb_vco_fi` at 10 fF per node:

| Corner | Current for the target frequency | Ring node |
|---|---|---|
| tt | 1.6 GHz needs ≈ 1.35 mA (was 1.437) | 1.38 V |
| ss, 110 °C | 1.76 GHz needs ≈ 1.93 mA (was 2.02) | ≈ 1.70 V |
| ff, −40 °C | 1.44 GHz needs ≈ 1.0 mA | — |

K_VCO over the 0.7–1.2 V lock window is ≈ −366 MHz/V (was −300), from `tb_vco_ktune`.

Every change goes in the safe direction (less current, lower ring voltage), and the CCO range of step 75 still covers
it. **Done on 15 Nov:** the step-74 characterisation was re-run with the correct setup (see the correction table in
`docs/design/step74_vco.md`). The CCO base count went from 13 to 11 units for the lower ff current. The clamp
model, the budget and the margin tracker were updated.
**Lesson for your own work:** always load the PDK `.spiceinit`. `tb/run.sh` does it for you.

---

## 1. What a testbench is

A testbench is a circuit around the **device under test (DUT)**. It has four parts, and every deck in `tb/` is written
in this order:

| Part | Question it answers | Example |
|---|---|---|
| **Models and conditions** | which process corner, which temperature? | `.lib …/sky130.lib.spice ss` and `.temp 110` |
| **Stimulus and supplies** | what drives the DUT? | supplies, bias current, input signal (sine, pulse, DC level, code bits) |
| **Load and environment** | what does the DUT drive, what is it connected to? | capacitive load of the next block, an ideal stand-in for a block not designed yet |
| **Analysis and measurement** | what do we compute, and which number comes out? | `.op`, `.dc`, `.ac`, `.noise`, `.tran` + `meas`, `print`, `wrdata` |

**Golden rule: replace every neighbour by the simplest thing that behaves like it at the port**, and say so. The ring
is tested with an *ideal current source* instead of the CCO, so we see the ring alone. The CCO is tested with an *ideal
voltage source* instead of the ring, so we see the current source alone. Then one testbench closes the gap: in
`tb_cco_clamp` a behavioural model of the ring's measured I–V is put back.

## 2. The files

```
tb/run.sh            runner: copies the PDK .spiceinit, fills in __PDK__ __CORNER__ __TEMP__ __DUT__, runs ngspice -b
tb/make_dut.py       writes tb/dut/*.spice (the DUT netlists) from the design scripts; re-run after any design change
tb/dut/              sspll_vco.spice  sspll_cco.spice  sspll_refbuf.spice   (hierarchical, same names as the schematics)
tb/vco/  tb/cco/  tb/refbuf/      the decks
tb/edges.py          jitter from a clock waveform (edge times -> rms deviation -> phase-noise floor)
tb/out/<deck>/       results: ngspice.log, data files (not in git)
```

Run any deck like this. The corner and temperature are optional and default to tt and 27 °C:
```
export PDK_ROOT=/path/that/contains/sky130A      # e.g. ~/.volare/sky130A/..  or /usr/local/share/pdk
tb/run.sh tb/cco/tb_cco_dc.spice ss 110
```

### Anatomy of a deck (from `tb_vco_tran.spice`)
```spice
.lib __PDK__/libs.tech/ngspice/sky130.lib.spice __CORNER__   ; models of one corner (tt ss ff sf fs)
.temp __TEMP__
.include __DUT__/sspll_vco.spice                              ; the circuit under test
.param cpar=10f ivco=1.437m                                   ; knobs you can change
ivco 0 vring dc {ivco}                                        ; stimulus: current INTO node vring
x1 vring vtune VDDBUF VSS vop vom clkp clkm sspll_vco         ; DUT instance (port order = .subckt line)
.ic v(vring)=1.3 v(vop)=0 v(vom)=1.3                          ; initial state
.control                                                      ; ngspice script: analyses + post-processing
tran 2p 26n 0 2p uic
meas tran ta when vd=0 rise=12                                ; a number out of a waveform
echo "RESULT f = $&f Hz"                                      ; print it
.endc
```

**Source sign convention** (the commonest beginner error):
- `I1 a b 5u` drives 5 µA *from a through the source to b*. So `iib 0 ibias 5u` pushes 5 µA **into** node ibias, and
  `iib ib 0 2.5u` pulls 2.5 µA **out of** node ib.
- The branch current `i(vx)` of a voltage source is positive when current flows *into its + terminal from the circuit*.

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

## 4. The testbenches, one by one

Each entry gives: **purpose** · **set-up and why** · **what to look at** · **result I got (tt, 27 °C unless noted)** ·
**pitfalls** · **how to draw it in xschem** · **how to run it in Cadence**.

### Step 74 — VCO (`tb/vco/`)

#### tb_vco_tran — oscillation frequency and ring-node voltage (method M1)
- **Purpose.** Frequency and supply-node voltage of the ring at one feed current.
- **Set-up.**
  - The CCO is replaced by an **ideal current source** into the ring's supply node (`ivco 0 vring`), with 0.5 pF of
    routing capacitance.
  - vtune is held at 0.9 V, the middle of the lock window; the buffers have their own 1.8 V supply.
  - `.param cpar=10f` adds the estimated layout capacitance on every ring output.
- **Why a transient.** An oscillator is a large-signal limit cycle and has no useful small-signal operating point.
  Only a transient shows its frequency, like a frequency counter.
- **Start-up kick.** `.ic v(vop)=0 v(vom)=1.3` plus `uic`. A perfectly symmetric circuit can sit at its metastable
  point forever in a noiseless simulator.
- **Measurement.**
  - Wait 12 cycles for start-up.
  - Time 20 rising zero-crossings of `vop − vom`: `f = 20/(tb − ta)`.
  - `avg` and `max` of v(vring) over the same window give the ring-node voltage.
- **Result.** 1.676 GHz, 1.399 V, 2.90 V differential swing (1.437 mA).
- **Pitfalls.**
  - Do not measure during start-up.
  - The time step must be much smaller than the period: 2 ps against 600 ps.
  - Always load the PDK `.spiceinit` (section 0).

#### tb_vco_fi and tb_vco_ktune — f(I), K_I and f(vtune), K_VCO (M1 in a loop)
- **Set-up.** The same transient inside `foreach … alter ivco dc = $ii … end`, or `alter vtn dc = $vt`. Each run
  prints one line. `destroy all` frees memory between runs.
- **Results.** f(I) at tt: 1.28 / 1.47 / 1.64 / 1.81 GHz at 1.0 / 1.2 / 1.4 / 1.6 mA, so K_I ≈ 0.85–0.9 GHz/mA. ss
  and ff are in section 0. f(vtune) at tt: 1.752 GHz at 0.7 V, 1.676 at 0.9 V, 1.569 at 1.2 V, so K_VCO ≈ −366 MHz/V.
- **Reading K_VCO.** The slope df/dvtune is negative and flattens below about 0.7 V (the switches turn off), which
  sets the 0.7–1.2 V lock window.

#### tb_vco_startup — does the ring start by itself?
- **Set-up.**
  - Everything starts at 0 V and the current ramps from 0 to 1.437 mA in 2 ns, like the CCO turning on.
  - A 0.1 fF extra on one output (1 % mismatch) stands for the random mismatch of real silicon.
- **Measurement.** The time when `vop − vom` first passes 0.5 V.
- **Result.** 2.0 ns at tt. Run `ss 110` too.

#### tb_vco_isf_point — one point of the impulse sensitivity function (M2)
- **Idea.** A small charge q injected into a ring node at time τ shifts the phase permanently by Δφ = h(τ)·q.
  h(τ), the ISF, tells how sensitive the ring is to noise at each moment of the cycle.
- **Set-up.** Run 1 without and run 2 with a 2 fC kick (2 mA for 1 ps) into vop at 10.2 ns. The kick is enabled
  between the two runs with `alter @iinj[pulse] = [...]`.
- **Measurement.** Compare one zero-crossing long after the kick: Δt → Δφ = 2πfΔt → h = Δφ/q.
- **Result.** h = −0.68 rad/pC at that moment.
- **The full method.** `vco.isf_noise()` repeats this at 12 moments for every node and combines h with each device's
  noise from M3 into phase noise:

  $$\mathcal{L}_{th}(\Delta f) = \frac{\overline{h^2 S_{th}}}{2(2\pi\Delta f)^2}, \qquad \text{(Hajimiri–Lee)}$$

  plus the flicker term through the DC part of h.

#### tb_dev_noise — noise of one transistor (M3)
- **Set-up.**
  - The device is biased by ideal sources.
  - A 0 V source measures its drain current.
  - A CCVS (`h1 o 0 vm 1`) turns that current into a voltage, so `.noise` reports **A/√Hz**. The `ac 1` on the gate
    source only names the noise input.
- **Result.** nfet_01v8, 4.5/0.3 µm, Vgs 0.75 V: 264 pA/√Hz at 1 kHz (flicker), 4.2 pA/√Hz at 100 MHz (thermal).
  Where the two cross is the flicker corner.

### Step 75 — CCO (`tb/cco/`)

All CCO decks drive the code bits as DC levels (0 / 1.8 V) and use the real level shifters inside the DUT.

#### tb_cco_dc — current vs code (M10)
- **Set-up.**
  - The ring is an **ideal 1.45 V source** `vr`, and `i(vr)` is the CCO output current.
  - IBIAS = 5 µA into the block.
  - A loop sets the five code-bit sources from the code: `b0 = c % 2`, `b1 = floor(c/2) % 2` and so on.
- **Why `op`.** A current source is a DC circuit; an operating point is exact and takes milliseconds.
- **Result.** Code 0 / 10 / 31 = 0.710 / 1.344 / 2.666 mA, against 62.5 µA × (11 + code) ideal.
- **What to do with it.** Run all 5 corners. Change `iib` to 4u and 6u and `vdda` to 2.97 / 3.63 V. Code 31 must stay
  ≥ the ss/110 °C requirement and code 0 ≤ the ff/−40 °C requirement.

#### tb_cco_compliance — is it still a current source near the top? (M10)
- **Set-up.** `dc vr 0 2.4 0.05` at code 31.
- **Reading.** The current must be flat up to ≈ 1.8 V (output pMOS saturated). Above VDDL the clamp sinks current and
  the curve falls.
- **Result (tt).** 2.73 mA at 0.4 V, 2.67 at 1.4 V, 2.64 at 1.7 V, 0.94 mA at 1.8 V (clamp active).
- **Worst case.** Set `vdda` to 2.97 and `iib` to 4u, and run `ss 110`.

#### tb_cco_noise — output-current noise (M11)
- **Set-up.** Like tb_dev_noise: ammeter `vm` plus CCVS `h1`. The ring source stays at 1.45 V, code 10.
- **Measurement.** `wrdata` writes the spectrum. Single-frequency `noise … lin 1 f f` runs print exact values.
- **Result.** 8.7 pA/√Hz at 1 MHz (requirement ≤ 10.3), 122 pA/√Hz at 10 kHz (filtered reference flicker).
- **Then.** The spectrum goes into the PLL model (M9): S_φ = K_I²·S_i/f², shaped by |(1−G_c)(1−H)|².

#### tb_cco_psr — supply → current (M11)
- **Set-up.** `vdda … ac 1`, an AC analysis. |i(vr)| is then directly A per V of ripple.
- **Result.** 0.25 / 0.21 / 0.18 mA/V at 10 kHz / 1 MHz / 10 MHz, so 1 mV of ripple gives ≈ 0.2 µA.

#### tb_cco_clamp — ring node with the real ring and the clamp (M12)
- **Set-up.**
  - The ring is put back as a **behavioural current sink** `Bring … I = pwl(v(vring), …)`: its measured average I–V
    at ss/110 °C (from M1 runs).
  - The worst case: IBIAS 6 µA, VDDA 3.63 V, code 31.
- **Why.** The DC result of the real ring + CCO + clamp is the intersection of their characteristics (load line).
  Simulating the oscillating ring for every code would take hours and give the same DC point.
- **Result (ss, 110 °C).** Ring node 1.785 V, ring current 2.40 mA.
- **Note.** The pwl table comes from the corrected step-74 runs (0.9–2.4 mA simulated, extrapolated above with the
  measured slope of 0.287 V/mA).

#### tb_ls_tran — level shifter (M13)
- **Set-up.** Lowest VDDD (1.71 V) with highest VDDA (3.63 V), 20 fF loads, a pulse at the input.
- **Measurement.** 10–90 % rise and fall, delay, high and low levels.
- **Result (tt).** 0.26 / 0.20 ns rise/fall, 0.33 ns delay, full 0–3.63 V swing.
- **Also run.** `ss 110` and `ff -40`.

### Step 76 — reference buffer (`tb/refbuf/`)

All decks drive REF_IN from a **50 Ω source** (a real oscillator's output impedance) biased at VDDA/2. The bias input
`ib` is pulled by 2.5 µA, standing in for the future bias generator. refclk is loaded with 50 fF, the clock-generator
input.

#### tb_refbuf_noise — noise at the crossing point (M14)
- **Idea.** With no signal, the first stage sits at its trip point (input = output through R_B). That is exactly the
  operating point it passes through at every edge. Its noise there is the noise that moves the edges.
- **Set-up.**
  - `op`: prints the self-bias point v(x1.vin) = v(x1.s1). Internal nodes of the instance are written `x1.name`.
  - `ac`: gain of S1 |v(s1)/v(vin)| and the C_AC divider |v(vin)/v(pad)|.
  - `noise v(x1.s1) vsrc`: output noise of S1. Dividing it by the gain gives the **gate-referred** noise.
- **Result.** 2.7 nV/√Hz at 1 MHz and 3.2 nV/√Hz at 300 MHz (white plateau); divider 0.68 at 50 MHz.
- **To jitter.** σ_t = σ_v / slope at the gate, with slope = π f V_pp × divider.
- **Pitfall.** Do not refer slow noise to the pad through the AC-coupling high-pass: below its corner that divides by
  a tiny gain and blows up. Refer it at the gate and use the signal's slope at 50 MHz.

#### tb_refbuf_tnoise — per-edge jitter by transient noise (M15)
- **Why.** The first stage is a high-gain comparator. Its small-signal DC gain (~190) is not the gain that applies
  while the input sweeps through the threshold (~30). So "integrated output noise / output slope" overestimates the
  jitter by about 2×. A transient *with noise* measures what really happens.
- **Set-up.**
  - ngspice has no device noise in transient, so the circuit's white noise is injected as `trnoise(NA NT 0 0)` in
    series with the source.
  - Its single-sided PSD is 2·NA²·NT. With S = (3.74 nV/√Hz)² = 1.40×10⁻¹⁷ V²/Hz at the pad and NT = 10 ps,
    NA = √(S/(2NT)) = √(1.40×10⁻¹⁷ / 2×10⁻¹¹) = 0.836 mV.
  - The first 20 cycles are not saved (bias settling); then 300 cycles.
- **Post-processing.** `python3 tb/edges.py tb/out/tb_refbuf_tnoise/edges.txt`:
  - interpolates every rising crossing of half the swing;
  - removes the ideal grid and the slow settling (4th-order fit);
  - prints the rms deviation (absolute jitter), the period jitter (√2 × absolute if the jitter is white), and the
    floor L = (2πfσ)²/f.
- **Result.** 0.61 ps at 1 V pp (−151.4 dBc/Hz), 0.23 ps at 3.3 V pp, 1.15 ps at 0.4 V pp (design script, 300
  edges). This deck on the drawn circuit gave 0.54 ps with 100 edges, the same within the statistics. Change
  `.param vpp` to repeat.
- **Pitfalls.**
  - The time step must equal NT (10 ps). 300 edges give σ to ±4 %, 100 edges to ±7 %. The same `seed` gives the same
    random sequence.
  - **Check NA by hand.** While writing this deck I first typed NA = 2.64 mV instead of 0.836 mV. The jitter came out
    3× too large (1.8 ps), and it took a bisection to find. Two habits catch this:
    - run once with NA ≈ 0: the noiseless baseline must give ≈ 0 ps (here 0.005 ps);
    - run once on the ideal circuit and compare with the design script.

#### tb_refbuf_tran — delay, duty, edge rate, power (M16)
- **Measurement.** `meas … trig … targ` from the pad crossing to the output edge, from rise to fall (high time), and
  over one period.
  - The *n*-th output edge need not belong to the *n*-th input edge, so delay and high time are folded into one period:
    `x − floor(x/T)·T`.
  - Power = average supply currents × supply voltages.
- **Result.** Delay 1.52 ns, duty 48.4 %, rise 295 ps, 0.254 mW (1 V pp).
- **Supply sensitivity.** Run twice with VDDA (or VDDL) 10 mV higher and divide the delay change by 10 mV.

#### tb_refbuf_startup — start-up and disabled state (M16)
- **Set-up.** `pll_en` = 0 for 0.5 µs, then 1.8 V.
- **Results.**
  - Disabled: I(VDDA) = 5.9 µA (pad divider + bias input) and refclk = 0 V.
  - First real clock edge 4.33 µs, i.e. 3.8 µs after enable. The single edge at the enable instant is a glitch.
  - Mean period afterwards 19.99 ns.

---

## 5. Drawing a testbench in xschem (same recipe for every deck)
1. `xschem --rcfile xschem/xschemrc` → *File → New schematic*, save it as `xschem/tb/tb_<name>.sch`.
2. **DUT:** *Insert symbol* (Shift-I) → `xschem/<block>/sspll_<block>.sym`. Its pins are the same as the `.subckt`
   line in `tb/dut`.
3. **Sources:** from `devices/`: `vsource.sym` (supplies, DC levels, `sin(…)`, `pulse(…)`, `pwl(…)`, `trnoise(…)` in
   the *value* field), `isource.sym` (IBIAS, ideal CCO), `capa.sym` (loads), `res.sym` (50 Ω source impedance),
   `gnd.sym`.
   - Watch the source arrow: it shows the current direction, as in section 2.
   - For the behavioural ring use `bsource.sym` with `VALUE="I = pwl(v(vring), …)"`.
4. **Labels:** `lab_pin.sym` on every net you want to plot or measure (vring, vop, vom, refclk…).
5. **Models and corner:** the `sky130_fd_pr/corner.sym` symbol, which holds the `.lib … tt` line, or a `code_shown.sym`
   block with `.lib`, `.temp` and `.param` lines.
6. **Analysis:** a second `code_shown.sym` block, with the property `value=` holding the whole `.control … .endc`
   section of the deck. Set `only_toplevel=true`.
7. *Netlist* → *Simulate* (or `ngspice -b` on the netlist in `xschem/simulations/`). Load the `.raw` file in xschem's
   graph (`devices/launcher.sym` + `graph.sym`) to look at waveforms.

Phase 8 draws these testbench schematics for every block (`tb_vco_*`, `tb_cco_*`, `tb_refin_*`…), and they will be
checked against these decks.

## 6. The same testbenches in Cadence Virtuoso (Spectre)
1. Import the DUT schematics: copy the netlists from `tb/dut/`, or redraw from the xschem PNGs in `docs/img/`. Then
   create a testbench cell with `analogLib` sources (`vdc`, `idc`, `vsin`, `vpulse`, `vpwl`, `cap`, `res`).
2. ADE L / Explorer → *Setup → Model Libraries*: the kit's `sky130.lib.scs`, section `tt` (or `ss`, `ff`…).
   *Setup → Temperature*.
3. Analyses, by the table in section 3:
   - `dc` with *save DC operating point* for M10;
   - `ac` with the AC magnitude on the supply source for PSR;
   - `noise`, output = the net or the probe current, input source = the one with AC magnitude, for M3/M11/M14;
   - `tran` for M1/M13/M16.
4. **Transient noise (M15).** Spectre can do device noise in transient: *tran → Transient Noise → noisefmax* (e.g.
   50 GHz), *noiseseed*. No injected source is needed, which makes it a good cross-check of the ngspice method.
   Better still for jitter: **pss + pnoise** with *jitter* output.
5. **Measurements.** The ADE *Calculator*: `cross()` for edge times, `frequency()`, `average()`, `delay()`,
   `dutyCycle()`, `riseTime()`. Save them as outputs and sweep with *Parametric Analysis*. Corners go in the *Corners*
   setup.
6. **Ring start-up.** Use *ic* on vop/vom (Simulation → Convergence Aids → Initial Condition) or a short current
   pulse.

## 7. From one deck to the full characterisation
The Python scripts in `design/<block>/` build the same circuits as strings, run them in parallel over the conditions,
and save the numbers to `design/<block>/data/*.json`. The plots in `docs/img/` come from those files:

| Block | Scripts |
|---|---|
| VCO | `vco.py` (netlist, run, freq_sweep, isf_noise, noise_table), `step74_char.py` |
| CCO | `cco.py`, `step75_sim.py`, `step75_noise.py`, `clamp_ring.py` |
| Reference buffer | `refbuf.py` (op, tran, noise_s1, input_noise, tnoise), `step76_sim.py`, `tn_run.py`, `step76_noise.py` |

When you change a design, run `python3 tb/make_dut.py` and rerun the decks first: they are the quickest way to see
whether anything moved.
