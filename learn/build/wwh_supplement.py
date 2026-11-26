"""Missing 'What happens / How it happens / Why it happens' sections, inserted right after the step heading.
Only the parts a step did not already have under these exact headings."""

S = {
24: {"How it happens": r"""The sampled-data simulator advances the loop one reference period at a time: at each edge it computes the PFD
pulse width from the phase error, injects $\pm I_p$ for that time, and propagates the filter and VCO state *exactly* to the next edge
with a matrix exponential. The ngspice model replaces phases by node voltages: a VCCS $\frac{I_p}{2\pi}(\phi_{in}-\phi_{div})$ drives the
real $R_1$, $C_1$, $C_2$; a VCCS into a 1 F capacitor integrates $K_{VCO}V_{cont}$ into phase; a VCVS of $1/N$ is the divider.""",
     "Why it happens": r"""Two independent implementations that agree (Python vs ngspice to $10^{-4}$ dB) prove the equations; the sampled
model shows what the continuous-time model hides — the loop acts on information up to one period old, so it loses phase margin and
finally oscillates as $f_c$ approaches $f_{REF}$."""},
28: {"Why it happens": r"""A multiplying detector produces the phase information as the *average* of a waveform at $2f_{REF}$; the filter
can only attenuate that waveform, never remove it, and the VCO integrates whatever ripple remains into periodic phase modulation.
Capture is narrow because, for offsets beyond the loop bandwidth, the detector output is a beat whose average is ~0; harmonics of
square-wave inputs also mix to DC, so the loop can be satisfied at the wrong ratio."""},
32: {"How it happens": r"""The simulation integrates real square waves: the XOR output is filtered by a first-order RC (Euler step,
200 points per reference period) and drives a VCO whose phase advances by $2\pi(1+\Delta f)dt + K_{VCO}(V_{cont}-V_{DD}/2)dt$. The phase
difference is read directly from the two phase accumulators.""",
     "Why it happens": r"""The static error appears because the VCO needs a DC control voltage that only a phase error can supply; the
ripple appears because the XOR toggles at $2f_{REF}$; the slip inside the static hold-in range appears because the underdamped loop
(ζ ≈ 0.25) overshoots past the edge of the XOR characteristic during the transient."""},
33: {"Why it happens": r"""The PFD is a memory element (two flip-flops): it records *which* edge arrived first and holds that state until
the other edge comes. That memory is what lets it tell frequency apart from phase, and the time it holds the state is exactly the
time difference — hence a pulse width proportional to $\Delta\phi$. The dead zone comes from the charge pump, not the logic: real
switches need a minimum pulse to turn on."""},
35: {"What happens": r"""With $R_1$ in series with $C_1$ the charge-pump PLL becomes a stable second-order Type-II loop: it settles after a
phase step with an overshoot set by ζ, and its closed-loop response shows a small peak near $\omega_n$ even when well damped."""},
38: {"What happens": r"""We turn the equations of steps 35–36 into actual component values for the Type-II baseline at our frequency
plan (50 MHz × 32 = 1.6 GHz, $f_c$ = 2.5 MHz, PM = 60°) and check that every component can be drawn in SKY130.""",
     "How it happens": r"""Fix $f_c$, PM, $N$, $K_{VCO}$ and choose $I_p$; then $b=\tan(45°+PM/2)$, $C_{tot}=bI_pK_{VCO}/(2\pi N\omega_c^2)$,
$C_2=C_{tot}/b^2$, $C_1=C_{tot}-C_2$, $R_1=b/(\omega_cC_1)$; finally convert R to a poly-resistor length and C to MIM or MOS-cap
area with the cheat-sheet densities."""},
41: {"How it happens": r"""For each loop bandwidth the filter is redesigned at 60° PM; the area comes from the capacitor densities, the
spur from the Fourier series of the charge-pump current through $Z(j\omega_{REF})$ (step 40), and the jitter from the phase-domain
noise model (step 23).""",
     "Why it happens": r"""All three depend on the same capacitors: smaller capacitors (wider loop) mean less area but a larger
impedance at $f_{REF}$ (spurs) and a wider window for ×N² noise; larger ones do the opposite. The loop bandwidth is the single knob
that moves all of them, so it is always a compromise."""},
42: {"What happens": r"""Three circuit fixes remove the non-idealities of steps 33 and 40: the dead zone, the UP/DN current mismatch
across the control-voltage range, and the charge-sharing glitch when a charge-pump switch closes.""",
     "How it happens": r"""(1) Delay in the PFD reset path keeps both switches on for $t_{rst}>t_{on}$ every cycle. (2) A replica branch
and an op-amp force the replica drain to $V_{cont}$ and servo one current source until UP = DN; the output branch copies the bias, so
mismatch falls by the op-amp gain. (3) Current is steered to a dump node held at $V_{cont}$ by a unity-gain buffer instead of being
switched off, so the internal node never drifts to a rail.""",
     "Why it happens": r"""Each problem has a physical cause the fix removes: switches need time to turn on (dead zone); channel-length
modulation makes currents depend on drain voltage (mismatch); a floating internal node charges to a rail and shares that charge on
reconnection (glitch)."""},
43: {"What happens": r"""Instead of only improving the charge pump, these fixes change *what the VCO sees* (a sampled filter), trim the
remaining error (calibration), or change the detector itself so its gain referred to the VCO no longer shrinks with N.""",
     "How it happens": r"""A sampled loop filter lets the charge-pump pulse settle on a separate capacitor and transfers the result to
the VCO node only after the pulse; a calibration loop measures the static phase offset and adjusts one current source; a
sub-sampling detector samples the VCO itself so its gain is $A$ volts per VCO radian instead of $I_p/(2\pi N)$.""",
     "Why it happens": r"""Spurs come from the fast transient on $V_{cont}$, which the hold hides; mismatch is a fixed error that a
measurement can cancel; and the N² noise penalty comes from detecting the *divided* phase — remove the divider from the detection and
the penalty disappears."""},
44: {"How it happens": r"""For each in-band floor the model sweeps the loop bandwidth and integrates the output phase noise
(10 kHz–40 MHz); the minimum of the jitter curve is the optimum bandwidth, and the dotted line marks the $f_{REF}/20$ limit set by
sampling delay and spurs."""},
45: {"How it happens": r"""The same cycle-by-cycle simulator as step 24 applies a 200 MHz output-frequency step as a phase ramp at the
reference; the PFD error is clipped at ±2π, so when the loop cannot follow, the charge pump delivers its maximum average current and
$V_{cont}$ ramps.""",
     "Why it happens": r"""A wide loop corrects the phase before it grows beyond the PFD range; a narrow loop cannot, the phase error
exceeds 2π, the PFD saturates and the loop can only move the VCO frequency as fast as $I_p/C_{tot}$ allows — slew-limited acquisition."""},
50: {"Why it happens": r"""The SSPD gain is large because the sampled voltage is the VCO waveform itself, $A$ volts per VCO radian, with
no division by N; for a few-MHz loop that gain would demand nanofarads of filter capacitance. Gating the transconductor reduces the
*average* gain by the duty $\tau/T$ while the noise power falls only by $\tau/T$ (not its square), hence the noise penalty."""},
51: {"How it happens": r"""The held voltage is updated once per period (zero-order hold: magnitude sinc, a $T/2$ delay), and the hold
capacitor mixes each new sample with the old value by charge sharing, $v_h[k] = (1-\alpha)v_s[k] + \alpha v_h[k-1]$, a discrete
low-pass. Both add phase lag at the loop's crossover."""},
52: {"Why it happens": r"""Sampling cannot count cycles: after a whole number of VCO periods the waveform looks identical, so the SSPD
sees every harmonic of $f_{REF}$ as "locked". Only a detector that compares *frequencies* (the divided VCO against the reference in a
PFD) can tell 31, 32 and 33 apart; the dead zone exists so that this noisy detector stops acting once its job is done."""},
53: {"What happens": r"""Compared with a Type-II charge-pump PLL using the same ring, reference, N and bandwidth, the SSPLL lowers the
in-band noise, removes the divider from the loop, and makes the charge-pump mismatch largely irrelevant — and it produces the held
error voltage that FFNC needs.""",
     "How it happens": r"""The detector samples the VCO directly (no ÷N in the loop), its noise is referred to VCO phase through a large
gain $A$, and at lock its output is ~0 so the transconductor injects almost no charge.""",
     "Why it happens": r"""The N² penalty, divider noise and charge-pump mismatch all come from comparing a *divided* clock with
switched *current pulses*; the SSPD compares the undivided waveform as a *voltage* that is zero at lock, so those mechanisms have
nothing to act on."""},
54: {"Why it happens": r"""The SSPD's characteristic repeats every VCO cycle, so a disturbance that moves the VCO more than the capture
range lets it settle on any neighbouring harmonic; the FLL only reacts once the divided phase leaves its dead zone, which takes many
reference periods, so recovery is slow. A dead zone too narrow to contain an SSPD lock point makes the two loops pull against each other."""},
55: {"Why it happens": r"""The sampler is a time-varying circuit attached to the VCO: its capacitance, injected charge and charge sharing
all repeat every reference period, which is exactly a periodic modulation of the VCO at $f_{REF}$ — a spur. Because the VCO integrates
frequency for a full reference period, a fractional frequency change is amplified by $f_0/f_{REF} = 32$ in phase."""},
56: {"How it happens": r"""The local loop gain is the slope of the characteristic at the operating point, $A\cos\Delta\phi$ for a sine (the
ring's waveform behaves similarly but saturates earlier); the amplitude $A$ or the slew rate itself changes with supply, corner and
temperature."""},
57: {"What happens": r"""Each limitation of steps 52–56 is mapped to the technique that removes it and to the block of our design that
implements it.""",
     "How it happens": r"""Acquisition problems are solved by adding frequency detection (FLL, auxiliary PFD, quadrature SSPD); spurs by
isolating and balancing the sampler; gain variation by limiting the swing, current-feeding the ring and calibrating; and ring noise beyond
the loop bandwidth by feedforward cancellation.""",
     "Why it happens": r"""The SSPD trades robustness for low noise; every fix adds back a missing property (frequency detection,
isolation, gain stability, out-of-band suppression) without bringing back the N² noise penalty."""},
58: {"How it happens": r"""The behavioural model samples the wrapped VCO phase at each reference edge, drives the pulsed transconductor,
runs the FLL's PFD with cycle-slip memory and a dead zone, and integrates filter and VCO exactly between edges; the four plots show
frequency, the SSPD sample, FLL activity and $V_{cont}$.""",
     "Why it happens": r"""Far from lock the PFD saturates and pulls the frequency (straight ramps); near 32 × f_REF the divided phase
enters the dead zone, the FLL goes quiet and the SSPD, which only sees phase, locks to the nearest zero crossing; $V_{cont}$ ends where it
cancels the coarse error, $\Delta V = -\Delta f/K_{VCO}$."""},
63: {"How it happens": r"""The SSPD converts timing error to voltage with slope $K_t = A\cdot2\pi f_0$; the NCB must convert it back with
$G_t = 1/K_t$. The delay range follows from the residual jitter before cancellation, the trim range from the expected spread of $K_t$, and
the noise target from the phase-noise budget.""",
     "Why it happens": r"""Cancellation is a subtraction: any gain error leaves a proportional residue, any NCB noise is added in full,
and any range shortfall clips the correction — so each item of the specification protects one part of the cancellation."""},
64: {"How it happens": r"""ngspice runs the SKY130 netlist for each code and control voltage, measures the delay between the input of
cell 2 and the output of cell 3 with `.meas`, and the notebook differentiates delay vs $V_{ctrl}$ to get the local gain.""",
     "Why it happens": r"""The delay is $C_LV_{sw}/I(V_{ctrl})$: the capacitor bank scales $C_L$ (and so the gain), while the strongly
non-linear $I(V_{ctrl})$ near threshold makes the gain change quickly with the operating point."""},
66: {"How it happens": r"""The SSPD turns the edge error into $v = K_t\Delta T_{VCO}$ at each reference edge and holds it; the NCB adds
a delay $-G_tv$ to every VCO edge until the next sample, so each output edge carries $(1-G_tK_t)$ times the error measured at the last
sample plus whatever the VCO wandered since."""},
69: {"What happens": r"""After cancellation, some noise sources disappear from the output (VCO, loop-filter resistor, VCO supply), some
pass unchanged or slightly larger (reference, SSPD), and one is new (the NCB itself).""",
     "How it happens": r"""Each source reaches out2 through the loop transfer function multiplied by $(1-G_{can})$ if the SSPD sees it as
a VCO error, or with an extra feedforward term $G_{can}/(1+LG)$ if it enters through the SSPD; the NCB's noise is added after the
measurement with transfer function 1."""},
70: {"What happens": r"""Three effects of FFNC on loop design: VCO noise near multiples of $f_{REF}$ folds into the cancellation band and
is injected into the output (aliasing); the loop no longer needs to be as wide; and the loop-filter capacitor can shrink because the
larger resistor's noise is cancelled.""",
     "How it happens": r"""The sampler sees $f_{REF}\sum_k S_\phi(f-kf_{REF})$; the cancellation path passes that folded spectrum with
$|G_{can}|^2$. For the filter, keeping $\omega_z = 1/(R_1C_1)$ while raising $R_1$ lets $C_1$ fall in proportion; the added resistor noise
enters at the VCO input, where FFNC removes it."""},
71: {"How it happens": r"""A 50 kHz tone on the VCO supply creates sidebands; the cancelled output's residual tone is demodulated by a
calibration SSPD, correlated with the injected tone, and the gain code is stepped until the residue is minimum (`cal_out` gives its sign).
At 50 kHz the path's phase is ~0, so the residue is $\propto|1-G|$."""},
}
