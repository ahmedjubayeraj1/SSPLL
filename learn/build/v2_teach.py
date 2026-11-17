"""v2_teach.py - the teacher's layer of the version-2 notebooks: for every phase a map (the story in plain words,
what you need to know first, what you will be able to do afterwards, how to study it) and a symbol glossary.
nb.py puts it right after the title when the notebooks are built with SSPLL_V2=1."""

HOW_TO_READ = r"""
**How version 2 teaches.** Version 1 is kept unchanged (same site, `Phase n` pages). Version 2 adds a teacher's
layer on top of every page.

- **A map** at the start: the story in plain words, what you need first, what you will be able to do afterwards.
- **A symbol glossary** for the phase: every letter used, with its unit and our design value.
- **A blue "Reading the equation" box** after every displayed equation. It gives:
  - every symbol: what it is, its unit and its value in our design;
  - the equation in plain words;
  - why it has this form, i.e. where it comes from;
  - a worked number;
  - and where it applies, a trap to watch out for.

**How to study one step.** (1) Read *What happens* and say it in your own words. (2) For each equation, cover the
blue box and try to name every symbol, then check. (3) Redo the worked number on paper. (4) Move the slider of the
figure and predict the change *before* you look. (5) Answer two interview questions aloud. If something is unclear,
go back to the matching section of **Phase 0 — the toolkit**.
"""


def gloss(rows):
    t = ["| Symbol | Meaning | Unit | Our design |", "|---|---|---|---|"]
    return "\n".join(t + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows])


TEACH = {
"phase0_toolkit": dict(
 story=r"""Before the PLL itself, the handful of ideas everything else is built on:
- a sine wave and its phase;
- phase as the running total of frequency;
- complex numbers as arrows;
- decibels;
- transfer functions and Bode plots;
- feedback and stability;
- sampling;
- noise;
- the MOSFET.

None of it is hard on its own; together it is the language of PLL design.""",
 need="School algebra and the idea of a derivative and an integral (slope and area).",
 goals="Read every equation of phases 1–7: say what each symbol is, its unit, and estimate its value.",
 glossary=gloss([
    ("$A$, $f$, $\\omega$, $T$, $\\phi$", "amplitude, frequency, angular frequency, period, phase", "V, Hz, rad/s, s, rad", "—"),
    ("$j$", "imaginary unit", "—", "—"),
    ("$s$", "Laplace / complex frequency", "1/s", "—"),
    ("$H(s)$, $G$", "transfer function, loop gain", "—", "—"),
    ("$\\omega_n$, $\\zeta$", "natural frequency, damping", "rad/s, —", "—"),
    ("$f_s$", "sampling rate", "Hz", "50 MHz"),
    ("$k$, $T$", "Boltzmann constant, temperature", "J/K, K", "$1.38\\times10^{-23}$, 300 K"),
    ("$S(f)$, $\\sigma$", "noise PSD, rms value", "—", "—"),
    ("$I_D$, $g_m$, $V_{ov}$, $\\gamma$", "drain current, transconductance, overdrive, noise factor", "A, S, V, —", "—")])),
"phase1_fundamentals": dict(
 story=r"""A crystal gives a very clean 50 MHz but the chip needs 1.6 GHz. A VCO can make 1.6 GHz, but it wanders. A
PLL is a feedback loop that keeps *steering the VCO so that its phase follows the crystal's phase, multiplied by 32*.
This phase builds that loop piece by piece:
- what phase is (the integral of frequency);
- why the VCO is an integrator;
- how a phase detector and charge pump turn phase error into current;
- how a loop filter turns current into the control voltage;
- how to tell whether the loop is stable (phase margin);
- how its noise and jitter are computed.

Every later phase uses these ideas.""",
 need="Sine waves and ω = 2πf, dB, the idea of a transfer function and of feedback. All of it is in Phase 0 (toolkit, sections 1–5).",
 goals="Derive $H(s)$ of a charge-pump PLL; find its phase margin from a Bode plot; predict its steady-state error; "
       "convert a phase-noise plot into rms jitter; explain why the reference noise is multiplied by $N^2$.",
 glossary=gloss([
    ("$f, \\omega$", "frequency, angular frequency $\\omega = 2\\pi f$", "Hz, rad/s", "—"),
    ("$\\phi$", "phase (angle turned)", "rad", "—"),
    ("$f_{REF}$, $T_{REF}$", "reference frequency and period", "Hz, s", "50 MHz, 20 ns"),
    ("$N$", "multiplication ratio", "—", "32"),
    ("$f_{out}$, $f_0$", "output (carrier) frequency", "Hz", "1.6 GHz"),
    ("$K_{VCO}$", "VCO gain", "rad/s/V", "$2\\pi\\cdot(-326)$ MHz/V"),
    ("$V_{cont}$", "control voltage", "V", "0.7–1.2 V"),
    ("$K_{PD}$", "phase-detector gain", "V/rad or A/rad", "—"),
    ("$I_p$", "charge-pump current", "A", "—"),
    ("$R_1, C_1, C_2$", "loop-filter parts", "Ω, F", "11 kΩ, 17.1 pF, 2.2 pF"),
    ("$Z(s)$, $F(s)$", "loop-filter impedance / transfer", "Ω, —", "—"),
    ("$G(s)$", "open-loop gain", "—", "1 at 2.5 MHz"),
    ("$H(s)$, $E(s)$", "closed-loop and error transfer", "—", "—"),
    ("$\\omega_c$, $f_c$", "crossover (loop bandwidth)", "rad/s, Hz", "2.5 MHz"),
    ("$PM$", "phase margin", "°", "50°"),
    ("$\\mathcal L(\\Delta f)$", "phase noise at offset Δf", "dBc/Hz", "−110…−120 at 300 kHz"),
    ("$S_\\phi$", "phase-noise PSD", "rad²/Hz", "—"),
    ("$\\sigma_t$", "rms jitter", "s", "1.26 ps (FFNC on)")])),
"phase2_type1": dict(
 story=r"""The simplest PLL — a mixer, an RC low-pass and a VCO — already locks. Studying it shows *why* real PLLs look
the way they do.
- Its speed and its stability are tied together.
- It needs a phase error to hold any frequency offset.
- Its detector leaves ripple on the VCO.

Each limitation, and its fix, leads straight to the charge-pump (type-II) PLL of phase 3.""",
 need="Phase 1 (loop gain, closed loop, phase margin). Second-order systems: Phase 0, section 6.",
 goals="Compute $\\omega_n$, $\\zeta$ and the static phase error of a type-I loop; explain the bandwidth/damping/ripple "
       "trade-off; show how a lag-lead filter and an integrator remove it.",
 glossary=gloss([
    ("$K = K_{PD}K_{VCO}$", "loop gain of the type-I loop", "rad/s", "—"),
    ("$\\omega_{LPF}$", "corner of the RC low-pass after the PD", "rad/s", "—"),
    ("$\\omega_n$, $\\zeta$", "natural frequency, damping", "rad/s, —", "—"),
    ("$\\Delta\\omega$", "frequency step / offset", "rad/s", "—"),
    ("$\\Delta\\phi_{ss}$", "static phase error", "rad", "—"),
    ("$\\tau_1$, $\\tau_2$", "lag-lead time constants", "s", "—"),
    ("$A_m$, $\\omega_m$", "ripple amplitude and frequency", "V, rad/s", "—")])),
"phase3_type2_cppll": dict(
 story=r"""A phase-frequency detector and a charge pump give an *integrator* in the loop: the static phase error becomes
zero, and the loop can pull in from any frequency. The price is a second integrator that must be stabilised by a zero
($R_1$), and new imperfections: mismatch, leakage and dead zone cause spurs; detector noise is multiplied by $N^2$. This
phase designs a type-II loop with numbers and shows exactly where it is limited. The sub-sampling PLL removes most of
those limits.""",
 need="Phases 1–2; Bode plots and phase margin (Phase 0, sections 4–6).",
 goals="Design $R_1, C_1, C_2$ for a given $f_c$ and PM; explain the zero, the third pole and the sampling delay; "
       "compute the in-band noise floor and the reference spur.",
 glossary=gloss([
    ("$I_p$", "charge-pump current", "A", "—"),
    ("$\\omega_z$", "zero $1/R_1C_1$", "rad/s", "$2\\pi\\cdot0.85$ MHz"),
    ("$\\omega_{p3}$", "third pole", "rad/s", "$2\\pi\\cdot7.4$ MHz"),
    ("$b$", "zero/pole spacing factor", "—", "≈ 3"),
    ("$C_{tot}$", "$C_1 + C_2$", "F", "19.3 pF"),
    ("$\\mathcal L_{1Hz}$", "normalised PFD/CP noise", "dBc/Hz", "≈ −225"),
    ("$V_1$", "control-voltage ripple at $f_{REF}$", "V", "—")])),
"phase4_sspll": dict(
 story=r"""Instead of dividing the VCO down and comparing edges, the sub-sampling phase detector simply *samples* the
1.6 GHz VCO with the 50 MHz reference edge. When the VCO is exactly 32 × 50 MHz, every sample lands on the same point of
the waveform, so the sampled voltage *is* the phase error. The steep 1.6 GHz slope makes the detector gain huge, so
detector and charge-pump noise are no longer multiplied by $N^2$. A frequency-locked loop is still needed to get close,
because sampling cannot tell N from N ± 1.""",
 need="Phase 3 (type-II loop). Sampling and aliasing: Phase 0, section 7. kT/C noise: Phase 0, section 8.",
 goals="Explain why the SSPD gain is $A$ V/rad of VCO phase; compute $\\beta$ and the SSPD noise from kT/C; "
       "explain why an FLL is needed; estimate the sampler spur.",
 glossary=gloss([
    ("$A$", "VCO amplitude at the sampler", "V", "≈ 0.6 V"),
    ("$K_t = A\\omega_{VCO}$", "SSPD gain per second of timing error", "V/s", "≈ 6 V/ns"),
    ("$\\beta$", "SSPD + pulsed-Gm gain", "A/rad", "0.78 µA/rad"),
    ("$g_m$", "Gm-cell transconductance", "S", "78 µS (3 units)"),
    ("$\\tau$", "Gm pulse width", "s", "—"),
    ("$C$", "sampling capacitor", "F", "100 fF"),
    ("$\\alpha$", "charge-sharing ratio", "—", "0.5")])),
"phase5_vcdl": dict(
 story=r"""The noise-cancellation block is a delay line whose delay is set by a voltage. Phase 5 builds one from
first principles:
- delay = charge / current;
- starving the current makes the delay tunable;
- every stage adds a little jitter of its own;
- its gain must match the SSPD gain exactly, so it is made programmable.""",
 need="MOSFET current and noise basics (Phase 0, section 10); charge = current × time.",
 goals="Derive the delay and the gain $K_{DL}$ of a current-starved stage; estimate the jitter a delay line adds; "
       "compute the gain the NCB needs to cancel ($G_t = 1/K_t$).",
 glossary=gloss([
    ("$t_d$, $\\tau$", "stage delay", "s", "—"),
    ("$C_L$", "load capacitance", "F", "—"),
    ("$I$, $I_{starve}$", "charging current", "A", "—"),
    ("$V_{TH}$, $V_{ov}$", "threshold and overdrive voltage", "V", "—"),
    ("$K_{DL}$", "delay-line gain", "s/V", "—"),
    ("$G_{t,NCB}$", "required NCB gain", "s/V", "≈ 0.17 ns/V"),
    ("$\\gamma$", "channel-noise factor", "—", "≈ 1")])),
"phase6_ffnc": dict(
 story=r"""The SSPD measures the remaining phase error of the VCO every reference period. Feedforward noise
cancellation uses that measurement once more: it delays the output edge by the measured error, with the opposite sign,
so the error disappears from the output. It works only as well as the gain and the timing of the cancellation path
match, which is why there is a calibration. It also inherits aliased noise from sampling.""",
 need="Phases 4–5; adding noise in power and transfer functions of noise (Phase 0, section 8).",
 goals="Explain $\\phi_{out2} = \\phi_{out1} - G\\phi_e$; compute the residue for a given gain and phase error; "
       "explain aliasing in the cancellation path and how the calibration finds the right gain.",
 glossary=gloss([
    ("$\\phi_{out1}$, $\\phi_{out2}$", "phase before / after cancellation", "rad", "—"),
    ("$G_{can}$, $G_c$", "cancellation gain / transfer", "—", "≈ 1"),
    ("$\\phi_e$", "SSPD-measured phase error", "rad", "—"),
    ("$\\theta$", "phase error of the cancellation path", "rad", "—"),
    ("$r$, $n$", "residue, original noise", "—", "—"),
    ("$F_{cal}$", "calibration-tone frequency", "Hz", "50 kHz")])),
"phase7_design": dict(
 story=r"""Phase 7 turns the theory into real SKY130 circuits, one block per step, with simulated numbers.
- Budget: what each block may cost in noise and power.
- Loop: the exact sampled loop.
- VCO: a ring with its noise computed from the ISF.
- CCO: its current-feed DAC.
- Reference buffer.
- Clock generator: the three timed phases of the SSPD.

For every block: what it does, how it was sized, how it was verified (methods M1–M17), and what was learned when a
number did not come out as expected.""",
 need="Phases 1–6, and the device basics of Phase 0, section 10. The testbench guide (`docs/testbench_guide.md`) "
      "shows how each simulation was set up.",
 goals="Read a noise/power budget; follow a block from requirement to schematic to verified numbers; explain every "
       "sizing decision and every verification method in an interview.",
 glossary=gloss([
    ("$S_{out}$, $S_{REF}$, $S_{PD}$, $S_{VCO}$", "phase-noise PSDs at the output / of each source", "rad²/Hz", "—"),
    ("$G_c$", "FFNC transfer", "—", "—"),
    ("$t_p$", "sample-to-pulse delay", "s", "2.5 ns"),
    ("$h(t)$", "impulse sensitivity function", "rad/C", "—"),
    ("$K_I$", "VCO frequency per current", "Hz/A", "0.84 GHz/mA"),
    ("$I_{CCO}$, $M$, $I_u$, $N_{base}$", "CCO current, mirror ratio, unit current, base units", "A, —, A, —", "—, 25, 2.5 µA, 11"),
    ("$R_F$, $C_F$", "CCO filter", "Ω, F", "10 MΩ, 7.3 pF"),
    ("$\\sigma_v$, $s$", "threshold noise, input slope", "V, V/s", "—"),
    ("$W_H$, $\\tau$", "hold-pulse width, Gm-pulse width", "s", "2.15 ns, 202 ps"),
    ("$NA$, $NT$", "trnoise amplitude and time step", "A, s", "—, 1 ps")])),
}


def intro(stem):
    t = TEACH.get(stem)
    if not t:
        return None
    return (f"## Teacher's map for this phase\n\n**The story.** {t['story'].strip()}\n\n"
            f"**You need first.** {t['need']}\n\n**After this phase you can.** {t['goals']}\n\n"
            f"**Symbols used in this phase** (more in each blue box):\n\n{t['glossary']}\n\n{HOW_TO_READ.strip()}")
