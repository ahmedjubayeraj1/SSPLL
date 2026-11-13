"""Phase 1 - PLL fundamentals from first principles (roadmap steps 11-24). Part A: steps 11-17."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nb import Book

b = Book("Phase 1 — PLL fundamentals from first principles (steps 11–24)",
         "This phase builds the PLL from $v = A\\sin\\phi(t)$ upward, so every later equation has a physical meaning you "
         "can rebuild on paper. By the end you can derive $H(s)$ of any PLL, judge its stability, predict its "
         "steady-state errors, and turn a phase-noise plot into an rms-jitter number — the four things an "
         "interviewer will test first.")

# ------------------------------------------------------------------------------------------------ step 11
b.step(11, "Why a PLL exists", "crystals stop at tens of MHz, chips need GHz; jitter limits ADC SNR")
b.md(r"""
### What happens
A quartz crystal is the most stable and lowest-noise frequency source available, but a fundamental-mode crystal
oscillator is practical only up to a few tens of MHz (thinner quartz for higher frequency becomes fragile; overtone
modes go higher but pull and start-up get harder). Our proposal uses a **50 MHz** crystal oscillator. The chip needs
**1.6 GHz** (and 800/400/200/100 MHz taps). A PLL multiplies the crystal frequency by $N = 32$ while *inheriting*
its long-term accuracy and, inside the loop bandwidth, much of its low noise.

### How it happens
A voltage-controlled oscillator (VCO) can run at any frequency in its range but drifts and is noisy. The PLL
divides the VCO output by $N$, compares its **phase** with the reference, and steers the VCO until the two phases
track. If the phases track, the frequencies must be equal, so
$$f_{out} = N\,f_{REF} = 32 \times 50\ \text{MHz} = 1.6\ \text{GHz}.$$

### Why the clock quality matters: jitter → SNR
Sample a sine $v(t) = A\sin(\omega_{in} t)$ at instants that are off by a random time error $\delta t$ with rms
$\sigma_t$. The voltage error is the slope times the time error:
$$\Delta v \approx \frac{dv}{dt}\,\delta t = A\,\omega_{in}\cos(\omega_{in}t)\,\delta t
\;\Rightarrow\; \overline{\Delta v^2} = \frac{A^2\omega_{in}^2\sigma_t^2}{2}.$$
Dividing the signal power $A^2/2$ by this noise power:
$$\boxed{\text{SNR}_{jitter} = -20\log_{10}\!\left(2\pi f_{in}\,\sigma_t\right)}\qquad
\text{ENOB} = \frac{\text{SNR}-1.76}{6.02}.$$
For our target $\sigma_t = 1.4$ ps and $f_{in} = 100$ MHz: $\text{SNR} = -20\log(2\pi\cdot10^8\cdot1.4\cdot10^{-12}) = 61.1$ dB,
about 9.9 bits. That is why a *jitter* number, not just a frequency, is the PLL's main specification.
""")
b.code(r"""
fin = np.logspace(6, 9.5, 300)                      # input frequency 1 MHz ... 3.2 GHz
def frame(sig_ps):
    snr = -20*np.log10(2*np.pi*fin*sig_ps*1e-12)
    s100 = -20*np.log10(2*np.pi*100e6*sig_ps*1e-12)
    return ([dict(x=fin, y=snr, name=f"sigma_t = {sig_ps} ps", mode="lines"),
             dict(x=[100e6], y=[s100], name="100 MHz input", mode="markers", marker=dict(size=10))],
            f"Jitter-limited SNR: {s100:.1f} dB = {(s100-1.76)/6.02:.1f} bits at 100 MHz for sigma_t = {sig_ps} ps")
fig = sweep([0.1, 0.2, 0.5, 0.84, 1.0, 1.4, 2.3, 3.2, 5.0, 10.0], frame, "rms jitter (ps)", active=5,
            layout=lambda f: f.update_xaxes(type="log", title="input frequency f_in (Hz)")
                              .update_yaxes(title="SNR (dB)", range=[20, 110]))
show(fig)
""")
b.md(r"""
**Try it.** Move the slider from 1.4 ps (FFNC on, our spec) to 2.3 ps (FFNC off): the 100 MHz SNR drops by
$20\log(2.3/1.4) = 4.3$ dB — almost one bit. Every halving of jitter buys 6 dB (one bit) at every input frequency.

**Key takeaways.** (1) A PLL is a frequency multiplier with memory of phase. (2) The crystal sets accuracy; the PLL
sets how much of the crystal's quality survives the multiplication. (3) Clock jitter becomes a hard SNR ceiling
$-20\log(2\pi f_{in}\sigma_t)$ that no ADC design can beat.
""")
b.qa([
    ("Why not just use a 1.6 GHz crystal?",
     "Fundamental-mode quartz resonators get thinner as frequency rises; above roughly 50–100 MHz they become fragile and hard to make. Overtone and SAW/BAW resonators reach higher, but with less pulling range, higher cost and often worse close-in noise. A PLL from a cheap low-frequency crystal is smaller, programmable and cheaper."),
    ("What does a PLL inherit from the reference, and what not?",
     "Long-term frequency accuracy exactly ($f_{out}=Nf_{REF}$ on average) and the reference phase noise inside the loop bandwidth, multiplied by $N^2$ (+20log N dB). Outside the bandwidth the output follows the VCO's own noise, not the reference."),
    ("Derive the jitter-limited SNR of an ADC.",
     "$v=A\\sin\\omega t$, sampling error $\\delta t$ gives $\\Delta v = A\\omega\\cos(\\omega t)\\,\\delta t$; mean square $A^2\\omega^2\\sigma_t^2/2$; signal power $A^2/2$; SNR $= 1/(\\omega\\sigma_t)^2$ → $-20\\log(2\\pi f_{in}\\sigma_t)$."),
    ("Does the jitter SNR depend on the signal amplitude or the sampling rate?",
     "No. Both signal and error scale with $A$, and the per-sample error does not depend on $f_s$ (for white jitter). It depends only on the input frequency and the rms jitter."),
    ("How much jitter is allowed for a 12-bit ADC at 200 MHz input?",
     "12 bits → SNR ≈ 74 dB → $\\sigma_t = 10^{-74/20}/(2\\pi\\cdot 2\\times10^8) \\approx 0.16$ ps. Hence high-speed ADCs need LC PLLs or noise-cancelled ring PLLs."),
    ("Which jitter is relevant for an ADC: period jitter or absolute jitter?",
     "Absolute (accumulated, time-interval-error) jitter integrated over the band that aliases into the signal band — essentially the integrated phase noise from a low offset up to about $f_s/2$. Period jitter matters more for digital timing closure."),
    ("Why is jitter given as 'integrated from 10 kHz to 40 MHz'?",
     "Rms jitter is the integral of phase noise over an offset band. The lower limit excludes slow wander that a receiver tracks or that is outside the application's concern; the upper limit is set by the application (here roughly $f_{REF}$-related noise). Different bands give different numbers, so the band must always be stated."),
    ("What sets the maximum frequency of a ring-oscillator PLL in SKY130?",
     "The delay of one stage: $f = 1/(2N_{stages}t_d)$. With 1.8 V devices and layout wiring, a 5-stage ring reaches about 2.2 GHz at the slow corner in our study, so 1.6 GHz keeps ~35% speed margin."),
    ("Why use a ring oscillator instead of an LC oscillator here?",
     "Area (no inductor), wide tuning range, multiphase outputs, and it is a standard-cell-friendly block. The price is ~20–30 dB worse phase noise per unit power, which this project attacks with a wide loop and feedforward noise cancellation."),
    ("What is the jitter figure of merit and our target?",
     "$FoM = 10\\log[(\\sigma_t/1\\,s)^2 (P/1\\,mW)]$. With 1.4 ps and 9 mW: $20\\log(1.4\\times10^{-12}) + 10\\log 9 = -237.1+9.5 = -227.5$ dB."),
    ("If you double the power of a ring oscillator, what happens to its jitter?",
     "Phase noise scales as $1/P$ for a fixed frequency (Hajimiri), so free-running jitter falls by $\\sqrt2$ (3 dB). That is why FoM is a fair comparison: it normalises jitter to power."),
    ("Name three systems where PLL jitter is the limiting factor.",
     "ADC/DAC sampling clocks, serial-link transmitters/receivers (eye closure, BER), RF local oscillators (reciprocal mixing, EVM)."),
    ("What does the PLL output look like before lock?",
     "The VCO runs at whatever frequency its control voltage gives; the phase detector produces a beat at the difference frequency, and acquisition circuits (PFD or FLL) pull the frequency until phase lock is possible."),
    ("Why do we also provide /2, /4, /8, /16 outputs?",
     "SoC blocks need several clock rates. Absolute jitter in seconds is preserved through an ideal divider, so the divided clocks carry the same jitter while phase noise in dBc/Hz drops by $20\\log M$."),
    ("Why is phase noise in dBc/Hz 24 dB lower at the /16 output, but the jitter the same?",
     "Dividing by M divides phase by M (phase power by $M^2$ → −20log M dB) but also divides the frequency by M, so $\\sigma_t = \\sigma_\\phi/(2\\pi f)$ is unchanged."),
], 11)

# ------------------------------------------------------------------------------------------------ step 12
b.step(12, "Phase and frequency from scratch; the VCO is a phase integrator", "ω = dφ/dt, φ = ∫ω dt, so a VCO is K_VCO/s")
b.md(r"""
### What happens
A periodic signal $x(t) = A\cos\phi(t)$ is described completely by its **phase** $\phi(t)$, which counts cycles
(×2π). Frequency is how fast the phase advances:
$$\omega(t) = \frac{d\phi}{dt}\qquad\Longleftrightarrow\qquad \phi(t) = \int_{-\infty}^{t}\omega(\tau)\,d\tau.$$

### How it happens in a VCO
An ideal VCO maps control voltage to frequency linearly (Razavi, *RF Microelectronics*, ch. 8):
$$\omega_{out} = \omega_0 + K_{VCO}V_{cont}\quad [K_{VCO}\text{ in rad/s/V}].$$
Therefore the output phase is
$$\phi_{out}(t) = \omega_0 t + K_{VCO}\!\int V_{cont}\,dt = \omega_0 t + \phi_{ex}(t),$$
where $\phi_{ex}$ is the **excess phase** — the only part a PLL controls. Taking the Laplace transform:
$$\boxed{\frac{\Phi_{ex}(s)}{V_{cont}(s)} = \frac{K_{VCO}}{s}}$$

### Why it matters
The VCO is an **integrator** of control voltage into phase. A constant $V_{cont}$ step does not shift the phase by a
constant; it makes the phase **ramp** forever (a frequency change). This free integrator is why every PLL is at
least Type I, and why the loop can force *zero frequency error* even with a finite gain elsewhere.
""")
b.code(r"""
f0, Kv = 1e9, 2*np.pi*300e6          # 1 GHz toy VCO, 300 MHz/V (so the waveforms stay readable)
t = np.linspace(0, 20e-9, 2000)       # 20 ns
t_step = 5e-9
def frame(dV):
    vcont = np.where(t > t_step, dV, 0.0)
    f_inst = f0 + Kv/(2*np.pi)*vcont
    phi_ex = np.cumsum(Kv*vcont)*(t[1]-t[0])
    return ([dict(x=t*1e9, y=np.cos(2*np.pi*f0*t), name="VCO with V_cont = 0", line=dict(dash="dot"), row=1, col=1),
             dict(x=t*1e9, y=np.cos(2*np.pi*f0*t + phi_ex), name="VCO with step", row=1, col=1),
             dict(x=t*1e9, y=f_inst/1e9, name="frequency (GHz)", row=2, col=1),
             dict(x=t*1e9, y=phi_ex, name="excess phase (rad)", row=3, col=1)],
            f"Step of {dV*1e3:.0f} mV at 5 ns: frequency +{Kv*dV/2/np.pi/1e6:.0f} MHz, phase ramps at {Kv*dV/1e9:.2f} rad/ns")
fig = sweep([0.0, 0.05, 0.1, 0.2, 0.3, 0.5], frame, "V_cont step (V)", active=3, rows=3, cols=1,
            subplot_titles=("waveform", "instantaneous frequency (GHz)", "excess phase phi_ex (rad)"),
            shared_xaxes=True, height=650,
            layout=lambda f: f.update_xaxes(title_text="time (ns)", row=3, col=1))
show(fig)
""")
b.md(r"""
**Try it.** With a 0.2 V step the frequency jumps by 60 MHz *instantly*, but the phase only starts to *ramp*: after
the step the stepped waveform slides further and further away from the reference waveform. Phase is the integral
of frequency.

**Key takeaways.** $\omega = d\phi/dt$; a VCO is $K_{VCO}/s$ from $V_{cont}$ to excess phase; a PLL works on
excess phase; the integrator is free and perfect (an oscillator never "forgets" a cycle).
""")
b.qa([
    ("Why is a VCO modelled as $K_{VCO}/s$ and not as a gain $K_{VCO}$?",
     "Its input controls frequency, and phase is the integral of frequency. In the phase domain (the variable a PLL compares) the VCO is an ideal integrator, $\\Phi_{ex}/V_{cont} = K_{VCO}/s$."),
    ("What is 'excess phase'?",
     "The deviation of the oscillator's phase from the ideal ramp $\\omega_0 t$: $\\phi_{ex}(t) = \\phi_{out}(t) - \\omega_0 t = K_{VCO}\\int V_{cont}dt$. Linear PLL analysis is done entirely on excess phases."),
    ("Units of $K_{VCO}$ in the equations?",
     "rad/s/V. Datasheets give Hz/V; multiply by $2\\pi$. Forgetting the $2\\pi$ is the most common loop-design error."),
    ("A VCO with $K_{VCO}=2\\pi\\cdot100$ MHz/V gets a 1 mV step. What happens to its phase after 1 µs?",
     "Frequency changes by 100 kHz; phase grows by $2\\pi\\cdot10^5\\cdot10^{-6} = 0.63$ rad and keeps growing linearly."),
    ("Can a PLL lock with a constant frequency difference between input and VCO free-running frequency?",
     "Yes, the loop applies whatever $V_{cont}$ is needed. In a Type-I loop that requires a constant phase error; in a Type-II loop the filter's integrator holds $V_{cont}$ with zero phase error."),
    ("Is $K_{VCO}$ constant in practice?",
     "No. In ring oscillators it varies with control voltage, process and temperature, often by 2–3×. Loop bandwidth and phase margin move with it; designs check stability at the extreme $K_{VCO}$ values."),
    ("What is the instantaneous frequency of $\\cos(\\omega_0t + m\\sin\\omega_mt)$?",
     "$\\omega_0 + m\\omega_m\\cos\\omega_m t$: peak deviation $m\\omega_m$. This is how small periodic phase modulation (spurs) relates to frequency modulation."),
    ("Why is $\\phi_{out} = \\int\\omega\\,dt$ an ideal integrator without leakage?",
     "Because phase is a count of zero crossings: an oscillator cannot 'forget' a cycle it has completed. Any frequency error accumulates as phase error without bound. This is also why free-running phase noise grows as $1/f^2$ (a random walk)."),
    ("How does $V_{cont}$ noise appear at the output?",
     "As phase noise $S_\\phi(f) = K_{VCO}^2 S_v(f)/(2\\pi f)^2$: white voltage noise becomes $1/f^2$ phase noise, filtered by the loop's high-pass $1-H$ when locked."),
    ("Why does a larger $K_{VCO}$ make a PLL noisier?",
     "Every noise voltage on $V_{cont}$ (filter resistor, CP, supply coupling) is multiplied by $K_{VCO}$. Designs use a coarse tuning code plus a small fine $K_{VCO}$ for this reason."),
    ("Express the sampled phase of a 1.6 GHz VCO 32 cycles after a reference edge if it runs 1 ppm fast.",
     "Extra phase $= 2\\pi\\cdot32\\cdot10^{-6} = 2.0\\times10^{-4}$ rad per reference period, accumulating each period unless corrected."),
    ("Difference between phase modulation and frequency modulation in this picture?",
     "PM: the modulating signal sets $\\phi$ directly; FM: it sets $d\\phi/dt$. A VCO is an FM modulator from $V_{cont}$; seen from phase it is PM through an integrator."),
], 12)

# ------------------------------------------------------------------------------------------------ step 13
b.step(13, "Phase detectors and their gain K_PD", "XOR, mixer, sample-and-hold, PFD; gain and linear range of each")
b.md(r"""
### What happens
A phase detector (PD) produces an output whose **average** is a function of the phase difference
$\Delta\phi = \phi_{1}-\phi_{2}$ of its inputs. Its small-signal slope $K_{PD} = d\overline{V}/d\Delta\phi$ (V/rad) or
$d\overline{I}/d\Delta\phi$ (A/rad) is the PD's contribution to loop gain.

### How each one works
| PD | Average output | $K_{PD}$ | Linear range | Detects frequency? |
|---|---|---|---|---|
| XOR (50% duty squares) | $V_{DD}\,\Delta\phi/\pi$, triangular | $V_{DD}/\pi$ | 0 … π (lock at π/2) | no |
| Mixer (sines) | $\frac{A_1A_2}{2}\cos\Delta\phi$ | $\frac{A_1A_2}{2}$ at $\Delta\phi=\pi/2$ | ±≈π/4 around π/2 | no |
| Sample-and-hold (sample a sine $A\sin\theta$ with an edge) | $A\sin\theta_e$ | $A$ (per rad of the sampled signal) | ±≈π/4 around 0 | no |
| PFD + charge pump | $I_p\,\Delta\phi/2\pi$ | $I_p/2\pi$ (A/rad) | ±2π | **yes** |

### Why they differ
XOR and mixer outputs swing at **2× the input frequency**; only their average carries phase, so a filter must remove a
large ripple. The sample-and-hold output is a DC level once locked (no ripple) — the root idea of the sub-sampling PD.
The PFD is a state machine; its output depends on *which edge came first*, so it also sees frequency differences.
""")
b.code(r"""
dphi = np.linspace(-2*np.pi, 2*np.pi, 401)
def xor_avg(dp, duty):
    th = np.linspace(0, 1, 2000, endpoint=False)
    a = (th % 1) < duty
    return np.array([np.mean(a ^ (((th - p/(2*np.pi)) % 1) < duty)) for p in dp])
def frame(duty):
    x = xor_avg(dphi, duty)
    return ([dict(x=dphi/np.pi, y=x, name=f"XOR, duty {duty:.2f} (x V_DD)", row=1, col=1),
             dict(x=dphi/np.pi, y=0.5*np.cos(dphi), name="mixer, A1A2 = 1 (V)", row=1, col=2),
             dict(x=dphi/np.pi, y=0.5*np.sin(dphi), name="S&H of a 0.5 V sine (V)", row=2, col=1),
             dict(x=dphi/np.pi, y=dphi/(2*np.pi), name="PFD+CP (x I_p)", row=2, col=2)],
            f"Average PD output vs phase difference. XOR peak = {x.max():.2f} V_DD at duty {duty:.2f}")
fig = sweep([0.3, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7], frame, "XOR input duty cycle", active=3, rows=2, cols=2,
            subplot_titles=("XOR", "mixer", "sample-and-hold", "PFD + charge pump"), height=600,
            layout=lambda f: f.update_xaxes(title_text="dphi / pi"))
show(fig)
""")
b.md(r"""
**Try it.** Move the XOR duty cycle away from 0.5: the triangle loses its full swing and gets flat tops — the gain
and the usable range both shrink. That is why XOR detectors need 50% duty-cycle inputs (Phase 2, step 28). The PFD
characteristic is a straight line over ±2π and depends on neither duty cycle nor amplitude.

**Key takeaways.** $K_{PD}$ is the slope at the lock point. Multiplying PDs (XOR, mixer) have periodic, bounded
characteristics and ripple at $2\omega$; the S&H PD has no ripple; the PFD has the widest range and detects frequency.
""")
b.qa([
    ("Derive the mixer phase-detector output.",
     "$A_1\\cos\\omega t\\cdot A_2\\cos(\\omega t+\\Delta\\phi) = \\frac{A_1A_2}{2}[\\cos\\Delta\\phi + \\cos(2\\omega t+\\Delta\\phi)]$; the low-pass filter keeps $\\frac{A_1A_2}{2}\\cos\\Delta\\phi$. Zero output at $\\Delta\\phi=\\pi/2$, slope $-A_1A_2/2$ there."),
    ("Why does a mixer or XOR PLL lock at 90° and not at 0°?",
     "The average output must equal the value that holds $V_{cont}$; for a symmetric output the zero-average/centre point of the characteristic is at $\\pi/2$, where the slope is maximum. At 0° the slope is zero (no gain)."),
    ("Derive the XOR gain.",
     "For 50% squares the output is high for a fraction $\\Delta\\phi/\\pi$ of each half period, so the average is $V_{DD}\\Delta\\phi/\\pi$ for $0\\le\\Delta\\phi\\le\\pi$: $K_{PD}=V_{DD}/\\pi$."),
    ("What is the main drawback of the XOR PD?",
     "Large ripple at $2f_{REF}$ that must be filtered (limits bandwidth, causes spurs), sensitivity to duty cycle, no frequency detection, and a static phase error in a Type-I loop."),
    ("What does 'linear range' of a PD mean and why does it matter?",
     "The range of $\\Delta\\phi$ over which the characteristic is close to a straight line. Outside it the loop gain falls or changes sign; large disturbances can cause cycle slips."),
    ("Why does a PFD detect frequency but an XOR does not?",
     "The PFD remembers which input edge came first: with unequal frequencies one output is active most of the time, giving a non-zero average with the right sign. The XOR output averages to $V_{DD}/2$ over a beat period."),
    ("What is $K_{PD}$ of a PFD with charge pump?",
     "$\\bar I = I_p\\Delta\\phi/(2\\pi)$, so $K_{PD} = I_p/2\\pi$ in A/rad. It drives a filter impedance, not a voltage node."),
    ("What limits the linear range of a PFD to ±2π?",
     "When the phase error exceeds 2π an edge is 'skipped' (a cycle slip); the characteristic wraps. Reset delay and dead time also shave the range near ±2π."),
    ("What is the gain of a sample-and-hold PD sampling $A\\sin(\\omega_{VCO}t)$?",
     "A timing error $\\Delta t$ gives $V = A\\sin(\\omega_{VCO}\\Delta t) \\approx A\\omega_{VCO}\\Delta t$; per radian of VCO phase, $K = A$ (V/rad). In seconds, $K_t = A\\omega_{VCO}$ (V/s)."),
    ("Which PD gains depend on signal amplitude, and why is that a problem?",
     "Mixer and sample-and-hold. Amplitude varies over PVT, so the loop gain and bandwidth move; designs either limit the amplitude or accept the spread in phase margin."),
    ("What is a bang-bang (binary) PD?",
     "It outputs only the sign of the phase error (early/late), e.g. a flip-flop. The gain is nonlinear (depends on jitter), used in CDRs and digital PLLs."),
    ("Which PD is used in our SSPLL main loop, and in the FLL?",
     "Main loop: a sub-sampling (sample-and-hold) PD that samples the 1.6 GHz output with the 50 MHz reference. FLL: a PFD with a dead zone comparing the reference with the /32 divider output."),
    ("Why is the output of an XOR at lock a square wave and not DC?",
     "Two 50% squares 90° apart produce an XOR output at $2f$ with 50% duty; only its average is $V_{DD}/2$. This $2f$ ripple modulates the VCO unless filtered."),
    ("What happens to a mixer PD if one input has harmonics?",
     "Harmonics mix with harmonics; the PLL can lock to a harmonic or subharmonic of the reference (false lock). PFDs do not have this problem."),
], 13)

# ------------------------------------------------------------------------------------------------ step 14
b.step(14, "Charge pump: current pulses, charge per cycle, average current", "I_avg = I_p·Δφ/2π")
b.md(r"""
### What happens
The PFD outputs an UP (or DN) pulse as wide as the time between the two input edges. The charge pump turns that
pulse into a current $\pm I_p$ for exactly that time, so each reference period it delivers a packet of charge.

### How
A phase error $\Delta\phi$ (rad of the reference) is a time error $\Delta t = \frac{\Delta\phi}{2\pi}T_{REF}$. The charge per
period is $Q = I_p\Delta t$, so the **average** current is
$$\overline{I} = \frac{Q}{T_{REF}} = I_p\frac{\Delta\phi}{2\pi}.$$
Into a capacitor $C_1$ the control voltage moves by (Razavi eq. 9.12)
$$\Delta V_{cont} = \frac{\Delta\phi_0}{2\pi}\,T_{REF}\,\frac{I_p}{C_1}\quad\text{every period,}$$
i.e. a staircase that rises without limit for a constant phase error. The continuous-time (CT) approximation replaces
the staircase by its average ramp: the PFD/CP/C cascade is an **integrator**
$$\frac{V_{cont}(s)}{\Delta\Phi(s)} = \frac{I_p}{2\pi C_1 s}.$$

### Why it matters
Combined with the VCO (another integrator) this gives the loop **two integrators** — Type II — and so zero static phase
error. The CT approximation is valid only when the loop changes little in one reference period ($f_c \ll f_{REF}$).
""")
b.code(r"""
Tref, Ip, C1 = 20e-9, 100e-6, 10e-12            # 50 MHz reference, 100 uA, 10 pF
t = np.linspace(0, 8*Tref, 1601)
def frame(dphi_deg):
    dt = dphi_deg/360*Tref
    up = ((t % Tref) < dt).astype(float)
    v = np.cumsum(up*Ip)*(t[1]-t[0])/C1
    v_ct = Ip*dphi_deg/360/C1*t
    return ([dict(x=t*1e9, y=up, name="UP pulse", row=1, col=1),
             dict(x=t*1e9, y=v*1e3, name="V_cont (staircase)", row=2, col=1),
             dict(x=t*1e9, y=v_ct*1e3, name="CT approximation (ramp)", line=dict(dash="dash"), row=2, col=1)],
            f"dphi = {dphi_deg} deg: pulse {dt*1e9:.2f} ns, step {Ip*dt/C1*1e3:.2f} mV per period, I_avg = {Ip*dphi_deg/360*1e6:.1f} uA")
fig = sweep([5, 10, 20, 45, 90, 180], frame, "phase error (deg)", active=2, rows=2, cols=1, shared_xaxes=True, maxpts=1601,
            subplot_titles=("PFD UP output", "control voltage on C1 (mV)"), height=560,
            layout=lambda f: f.update_xaxes(title_text="time (ns)", row=2, col=1))
show(fig)
""")
b.md(r"""
**Try it.** Double the phase error: the pulses double in width, the step per period doubles, the average current
doubles — the PFD/CP is *linear* in $\Delta\phi$ (until ±2π). The dashed ramp is the CT approximation through the middle of
the staircase.

**Key takeaways.** $\overline I = I_p\Delta\phi/2\pi$; a charge pump into a capacitor is an integrator; the staircase vs ramp
difference is the sampled-data nature that limits the loop bandwidth to about $f_{REF}/10$ (step 37).
""")
b.qa([
    ("Why is a charge-pump PLL called Type II?",
     "The CP into a capacitor integrates the phase error and the VCO integrates the control voltage: two poles at the origin in the open loop."),
    ("Derive the average charge-pump current.",
     "Pulse width $\\Delta t = \\Delta\\phi T/2\\pi$, charge $I_p\\Delta t$ per period $T$: $\\bar I = I_p\\Delta\\phi/2\\pi$."),
    ("Why is the PFD/CP/C cascade not strictly linear?",
     "It is a sampled system: charge is delivered in pulses once per period. Doubling $\\Delta\\phi$ doubles the pulse width but the waveform is not simply scaled at every instant. The CT approximation averages it."),
    ("What is the continuous-time approximation and when is it valid?",
     "Replacing the per-cycle charge packets by their average current. Valid when the loop bandwidth is much lower than $f_{REF}$ (rule of thumb $f_c < f_{REF}/10$)."),
    ("What happens to $V_{cont}$ with a constant phase error and only a capacitor?",
     "It ramps without bound (integrator), forcing the VCO frequency to change until the phase error becomes zero. That is why the steady-state phase error is zero."),
    ("Why do charge pumps use current sources and not resistors?",
     "A current source gives charge independent of the output voltage (over its compliance range), keeping $K_{PD}$ constant as $V_{cont}$ moves."),
    ("What is charge-pump compliance and why does it matter?",
     "The range of output voltage over which UP and DN currents stay equal and constant. Outside it the currents mismatch, causing static phase offset and spurs, and the VCO tuning range usable by the loop shrinks."),
    ("What happens when UP and DN currents are mismatched?",
     "At lock the net charge per period must be zero, so the PFD settles at a phase offset where the longer pulse of the weaker source balances the stronger one. The mismatch pulses each period create ripple and reference spurs."),
    ("Why does the PFD output both UP and DN briefly at lock?",
     "The reset path has a finite delay; both outputs are high for that delay every cycle. This removes the dead zone but makes mismatch currents flow every period."),
    ("How much charge does our proposal's SSPLL charge pump deliver differently?",
     "It is a pulsed transconductor: current $g_m V_{sample}$ for a short pulse $\\tau$ per period, so average current $g_m V\\tau/T$. It is driven by a voltage, not by a pulse width (Phase 4, step 50)."),
    ("Compute $\\Delta V_{cont}$ per period for $\\Delta\\phi=10°$, $I_p=100$ µA, $C=10$ pF, $f_{REF}=50$ MHz.",
     "$\\Delta t = (10/360)\\cdot20$ ns = 0.556 ns; $Q = 55.6$ fC; $\\Delta V = 5.56$ mV per period."),
    ("What are clock feedthrough and charge injection in a charge pump?",
     "Switching transistors couple the control edges through their gate-drain capacitance and dump channel charge onto the output each period; both create periodic disturbances → reference spurs."),
], 14)

# ------------------------------------------------------------------------------------------------ step 15
b.step(15, "Loop filter: why a capacitor integrates current; Z(s) of C, R+C, R+C‖C2", "Bode plots of Z(s)")
b.md(r"""
### What happens
The loop filter converts the charge-pump current into the control voltage. Its transimpedance $Z(s) = V_{cont}/I$
shapes the loop gain.

### How
A capacitor obeys $i = C\,dv/dt$, so $v = \frac1C\int i\,dt$ → $Z_C = \frac{1}{sC}$: an integrator. Adding a series
resistor gives
$$Z_1(s) = R_1 + \frac{1}{sC_1} = \frac{1+sR_1C_1}{sC_1}\qquad\text{(pole at 0, zero at } \omega_z = 1/R_1C_1).$$
The current through $R_1$ makes $V_{cont}$ jump by $I_pR_1$ every time the CP turns on, so a ripple capacitor $C_2$
is added in parallel:
$$Z(s) = \frac{1+sR_1C_1}{s(C_1+C_2)\left(1+sR_1\frac{C_1C_2}{C_1+C_2}\right)},\qquad
\omega_z = \frac{1}{R_1C_1},\quad \omega_{p3} = \frac{C_1+C_2}{R_1C_1C_2}.$$

### Why
The integrator (pole at 0) gives Type II; the zero restores phase (+90° at high frequency) so the loop can be stable
(step 34); the extra pole from $C_2$ filters the ripple but takes phase back. Between $\omega_z$ and $\omega_{p3}$ the filter is
almost a resistor, $|Z|\approx R_1$ — that flat region is where the crossover frequency is placed.
""")
b.code(r"""
f = np.logspace(3, 9, 500)
R1, C1 = 18.05e3, 13.16e-12                       # the 2.5 MHz design of step 24 / 38
def frame(ratio):
    C2 = C1*ratio
    Zc  = lambda s: 1/(s*C1)
    Zrc = lambda s: R1 + 1/(s*C1)
    Z3  = lambda s: (1+s*R1*C1)/(s*(C1+C2)*(1+s*R1*C1*C2/(C1+C2)))
    out = []
    for name, Z, dash in (("C1 only", Zc, "dot"), ("R1 + C1", Zrc, "dash"), (f"R1 + C1 || C2 (C2/C1={ratio})", Z3, None)):
        m, p = bode(Z, f)
        out.append(dict(x=f, y=m, name=name, line=dict(dash=dash), row=1, col=1))
        out.append(dict(x=f, y=p, name=name+" phase", line=dict(dash=dash), showlegend=False, row=2, col=1))
    fz = 1/(2*np.pi*R1*C1); fp = (C1+C2)/(2*np.pi*R1*C1*C2)
    return out, f"zero {fz/1e6:.2f} MHz, third pole {fp/1e6:.2f} MHz, pole/zero ratio = 1 + C1/C2 = {1+1/ratio:.1f}"
fig = sweep([0.02, 0.05, 0.0774, 0.1, 0.2, 0.5], frame, "C2 / C1", fmt="{:.3g}", active=2, rows=2, cols=1,
            shared_xaxes=True, subplot_titles=("|Z| (dB Ohm)", "phase of Z (deg)"), height=620,
            layout=lambda f: f.update_xaxes(type="log").update_xaxes(title_text="frequency (Hz)", row=2, col=1))
show(fig)
""")
b.md(r"""
**Try it.** At $C_2/C_1 = 0.077$ (our 60° design) the phase climbs from −90° back toward 0° after the zero and turns
down again at the third pole; the maximum phase sits at $\sqrt{\omega_z\omega_{p3}}$. A bigger $C_2$ pulls the pole toward the
zero and the phase bump collapses — less phase margin (step 36).
""")
b.qa([
    ("Why must a charge-pump loop filter contain a resistor?",
     "With a capacitor alone the loop has two integrators and −180° phase at every frequency: zero phase margin, the loop rings or oscillates. The series R creates a zero that adds up to +90°."),
    ("Write $Z(s)$ of R1 in series with C1, all in parallel with C2.",
     "$Z = \\frac{1+sR_1C_1}{s(C_1+C_2)(1+sR_1C_s)}$ with $C_s = C_1C_2/(C_1+C_2)$."),
    ("Why add C2?",
     "Each CP pulse makes $V_{cont}$ jump by $I_pR_1$; that step modulates the VCO and makes large reference spurs. C2 smooths it, at the cost of a third pole (less phase margin)."),
    ("What is the impedance of the filter at the crossover frequency in a well-designed loop?",
     "Approximately $R_1$ (the flat region between the zero and the third pole), slightly reduced by $C_1/(C_1+C_2)$."),
    ("Where should the zero and the third pole sit relative to crossover?",
     "Symmetrically on a log scale: $\\omega_z = \\omega_c/b$, $\\omega_{p3} = b\\,\\omega_c$, with $b = \\sqrt{1+C_1/C_2}$; this maximises phase margin for a given capacitor ratio."),
    ("Which component dominates the loop-filter area and why?",
     "C1. It sets the zero at low frequency (below crossover) with a resistor that must stay small for noise: $C_1 = 1/(\\omega_z R_1)$."),
    ("How does the resistor's thermal noise reach the output?",
     "As a voltage $\\sqrt{4kTR_1}$ on $V_{cont}$ (shaped by the capacitors), turned into frequency noise by $K_{VCO}$ and high-pass filtered by the loop like VCO noise. Larger R1 → more noise; FFNC can cancel it (Phase 6)."),
    ("What is an active loop filter and when is it used?",
     "An op-amp integrator realising $Z(s)$; it allows a $V_{cont}$ range independent of the CP compliance. It adds op-amp noise and power; most integrated PLLs use passive filters."),
    ("How do you implement 13 pF in SKY130?",
     "MIM caps at about 2 fF/µm² (≈6500 µm² as 30×30 µm tiles) or a 1.8 V MOS cap at ~7.5 fF/µm² (≈1760 µm²), the latter only if biased above ~0.6 V (cheat sheet)."),
    ("What does the phase of Z do between the zero and the pole?",
     "It rises from −90° toward 0° after the zero and falls back to −90° after the pole; the peak phase is $\\arctan b - \\arctan(1/b)$ at the geometric mean frequency."),
    ("What is the effect of R1 C1 process spread on the loop?",
     "The zero moves (±30% across R/C corners in SKY130, step 7 finding); phase margin and peaking change. Designs centre PM so that extreme R/C corners still keep about 45°."),
], 15)

# ------------------------------------------------------------------------------------------------ step 16
b.step(16, "Divider: why ÷N divides both frequency and phase", "waveform sketch")
b.md(r"""
### What happens
A ÷N counter produces one output cycle for every $N$ input cycles. Its output frequency is $f_{in}/N$, and a phase
change at its input appears **divided by N** at its output.

### How
If the input edges move by a time $\Delta t$, the output edges (which are copies of every $N$-th input edge) move by the
same $\Delta t$. In radians: the input phase change is $\Delta\phi_{in} = 2\pi f_{in}\Delta t$ and the output phase change is
$\Delta\phi_{out} = 2\pi \frac{f_{in}}{N}\Delta t = \Delta\phi_{in}/N$. So in the phase domain
$$\Phi_{div}(s) = \frac{1}{N}\Phi_{out}(s).$$

### Why it matters
In the loop, the divider is the $1/N$ in the feedback path. Its consequences: (1) the closed loop multiplies the input
phase (and anything added at the PD input) by $N$ at low frequency, i.e. **noise power ×N²**; (2) the divider is also a
*sampler* — it only passes information once per output period; (3) time jitter is preserved, phase jitter is divided.
""")
b.code(r"""
fin, N = 1.0, 4                                  # normalised: input period 1, divide by 4 for readability
t = np.linspace(0, 12, 3000)
def frame(shift):
    tin = t - np.where(t > 4, shift, 0)          # input edges move by 'shift' after t = 4
    vin = (np.sin(2*np.pi*fin*tin) > 0).astype(float)
    vout = (np.sin(2*np.pi*fin*tin/N) > 0).astype(float)
    ref = (np.sin(2*np.pi*fin*t/N) > 0).astype(float)
    return ([dict(x=t, y=vin+2.4, name="input (period 1)"),
             dict(x=t, y=vout+1.2, name="divided output (/4)"),
             dict(x=t, y=ref, name="divided output without shift", line=dict(dash="dot"))],
            f"time shift {shift:.2f}: input phase {360*shift:.0f} deg -> output phase {360*shift/N:.0f} deg (same time shift)")
fig = sweep([0.0, 0.1, 0.25, 0.5, 1.0], frame, "input time shift (input periods)", active=2, height=420,
            layout=lambda f: f.update_xaxes(title="time (input periods)").update_yaxes(showticklabels=False))
show(fig)
""")
b.qa([
    ("Why does a divider divide phase by N?",
     "It preserves time shifts of edges, but the output period is N times longer, so the same time shift is a phase N times smaller."),
    ("Does a divider reduce jitter?",
     "It preserves absolute time jitter of the edges it passes (plus its own), but phase noise in dBc/Hz drops by 20log N because the frequency is N times lower."),
    ("What is a TSPC divider and why is it used at GHz?",
     "True single-phase clocked flip-flop: dynamic logic with one clock phase, few transistors and small load; fast enough for the first ÷2 stages at GHz (our ÷32 starts with TSPC stages)."),
    ("Why is divider noise multiplied by N² at the PLL output?",
     "Divider jitter appears at the PD input like reference jitter; the loop forces the output phase to N times the PD input phase inside the bandwidth, so noise power is ×N²."),
    ("How does a sub-sampling PLL avoid the divider in the loop?",
     "The SSPD samples the VCO directly with the reference; the loop compares the VCO phase with N times the reference phase without dividing. A divider is only used in the FLL for acquisition and turned quiet once locked."),
    ("What is the difference between a synchronous and an asynchronous (ripple) divider?",
     "Synchronous: all flip-flops clocked by the input, output edge timed by the input clock (low jitter). Ripple: each stage clocks the next, delays and jitter accumulate; fine for slow taps, bad for the feedback path."),
    ("Why do dividers need a retiming flip-flop in low-jitter PLLs?",
     "To resynchronise the divided edge to the clean VCO edge, removing the accumulated jitter of the counter."),
    ("What is a dual-modulus prescaler?",
     "A divider that switches between N and N+1 under control; combined with counters it gives programmable (and fractional, with a modulator) division."),
    ("Is a divider linear in the phase domain?",
     "Yes for small phase changes ($\\Phi_{div} = \\Phi_{out}/N$), but it is a sampled system; its output carries information only at its edges."),
    ("What is the power of a ÷32 TSPC chain at 1.6 GHz roughly?",
     "Dominated by the first stage: $P \\approx C V_{DD}^2 f$; with ~20 fF switched at 1.6 GHz and 1.8 V that is ~0.1 mW per stage, halving each stage; the proposal budgets 0.7 mW for the whole FLL."),
], 16)

# ------------------------------------------------------------------------------------------------ step 17
b.step(17, "Linear phase-domain model: G(s), H(s), E(s)", "block diagram and equations")
b.md(r"""
### What happens
Once locked, all signals in the loop are small deviations of phase. Each block becomes a transfer function and the
PLL becomes a linear feedback system.

### How
Forward path: PD gain $K_{PD}$, filter $F(s)$ (or $Z(s)$ for a CP), VCO $K_{VCO}/s$; feedback path $1/N$.
The **open-loop gain** (loop gain) is
$$G(s) = \frac{K_{PD}\,F(s)\,K_{VCO}}{N\,s}\qquad\text{(CP-PLL: } G(s) = \frac{I_p}{2\pi}Z(s)\frac{K_{VCO}}{Ns}).$$
The closed-loop transfer from input phase to output phase and the error transfer are
$$\boxed{H(s) = \frac{\Phi_{out}}{\Phi_{in}} = N\frac{G(s)}{1+G(s)}},\qquad
\frac{\Phi_e}{\Phi_{in}} = E(s) = \frac{1}{1+G(s)}.$$
(Razavi writes $H(s)$ for $N=1$; here the factor $N$ is kept explicit.)

### Why
$|G|\gg1$ at low frequency → $H\to N$: the output follows $N\times$ the input; the error vanishes. $|G|\ll1$ at high
frequency → $H\to0$: the output ignores the input and keeps the VCO's own phase. The **crossover** $|G(j\omega_c)|=1$
is the loop bandwidth. The same $1/(1+G)$ shapes VCO noise (step 23).
""")
b.code(r"""
import os, sys
f = np.logspace(3, 9, 500)
Ip, Kv, N = 100e-6, 2*np.pi*300e6, 32
def frame(fc_MHz):
    d = sl.loop_design_type2(fc_MHz*1e6, 60, Ip, Kv, N)
    Z = lambda s: (1+s*d['R']*d['C1'])/(s*(d['C1']+d['C2'])*(1+s*d['R']*d['C1']*d['C2']/(d['C1']+d['C2'])))
    G = lambda s: Ip/(2*np.pi)*Z(s)*Kv/(N*s)
    s = 2j*np.pi*f
    g = G(s)
    return ([dict(x=f, y=20*np.log10(abs(g)), name="|G| open loop"),
             dict(x=f, y=20*np.log10(abs(g/(1+g))), name="|H/N| closed loop"),
             dict(x=f, y=20*np.log10(abs(1/(1+g))), name="|E| = |1/(1+G)|")],
            f"f_c = {fc_MHz} MHz, PM 60 deg: R1 = {d['R']/1e3:.1f} kOhm, C1 = {d['C1']*1e12:.1f} pF, C2 = {d['C2']*1e12:.2f} pF")
fig = sweep([0.5, 1.0, 1.5, 2.0, 2.5, 3.5, 5.0], frame, "loop bandwidth f_c (MHz)", active=4,
            layout=lambda f: f.update_xaxes(type="log", title="offset frequency (Hz)")
                              .update_yaxes(title="dB", range=[-60, 80]))
show(fig)

# cross-check with ngspice (learn/spice/pll_phase_domain.cir, f_c = 2.5 MHz design)
a = np.loadtxt("data/pll_phase_domain.csv")
d = sl.loop_design_type2(2.5e6, 60, Ip, Kv, N)
Z = lambda s: (1+s*d['R']*d['C1'])/(s*(d['C1']+d['C2'])*(1+s*d['R']*d['C1']*d['C2']/(d['C1']+d['C2'])))
G = lambda s: Ip/(2*np.pi)*Z(s)*Kv/(N*s)
g = G(2j*np.pi*a[:, 0])
print("ngspice vs Python, max |H| difference: %.2e dB" % np.max(abs(a[:, 1] - 20*np.log10(abs(N*g/(1+g))))))
""")
b.md(r"""
**Try it.** As $f_c$ grows, $|H/N|$ stays flat to a higher frequency and $|E|$ (the VCO-noise high-pass) suppresses
more. The filter values update: a wider loop needs a smaller $C_1$ (area ∝ $1/f_c^2$). The ngspice phase-domain netlist
(`learn/spice/pll_phase_domain.cir`) reproduces the Python $H(s)$ to $10^{-4}$ dB — the same model in a circuit simulator.
""")
b.qa([
    ("Write the open-loop gain of a charge-pump PLL.",
     "$G(s) = \\frac{I_p}{2\\pi}\\,Z(s)\\,\\frac{K_{VCO}}{s}\\,\\frac1N$."),
    ("What is the low-frequency value of $H(s) = \\Phi_{out}/\\Phi_{in}$ and why?",
     "N. When $|G|\\to\\infty$, $\\Phi_{out}/N = \\Phi_{in}$: the divided output tracks the input exactly."),
    ("Define loop bandwidth.",
     "Usually the crossover frequency where $|G| = 1$ (0 dB). The −3 dB bandwidth of $H$ is somewhat higher (by ~1.2–1.5× depending on PM)."),
    ("Why is $E(s) = 1/(1+G)$ important besides steady-state error?",
     "It is also the transfer function from VCO phase noise to output: the loop high-pass-filters VCO noise with $1/(1+G)$."),
    ("What assumptions does the linear phase model make?",
     "Locked loop, small phase errors (inside the PD linear range), continuous-time averaging of sampled blocks ($f_c\\ll f_{REF}$), linear $K_{VCO}$."),
    ("How can you simulate a PLL's H(s) in SPICE without the GHz signals?",
     "Build the phase-domain model with controlled sources: node voltages represent phases, a VCCS for the PD/CP, real R/C for the filter, a VCCS into a 1 F capacitor for the VCO integrator, a VCVS of 1/N for the divider; run an AC analysis."),
    ("What does $|H|$ peaking indicate?",
     "Low phase margin. Peaking amplifies reference and PD noise around the bandwidth and causes ringing in the step response."),
    ("Name the poles and zeros of G(s) for a third-order CP-PLL.",
     "Two poles at the origin (CP integrator, VCO), one zero at $1/R_1C_1$, one pole at $(C_1+C_2)/(R_1C_1C_2)$."),
    ("Why does $C_1$ scale as $1/f_c^2$?",
     "From the crossover condition $C_t = b I_pK_{VCO}/(2\\pi N\\omega_c^2)$: halving $f_c$ quadruples the total capacitance."),
    ("Why is the closed-loop transfer called low-pass for the input and high-pass for the VCO?",
     "$H/N = G/(1+G)$ → 1 at low frequency, 0 at high; $1/(1+G)$ → 0 at low, 1 at high. Their sum is 1 for any loop (complementary)."),
    ("Can a PLL bandwidth exceed $f_{REF}/2$?",
     "No meaningful sense: the PD only updates once per reference period (Nyquist). Practical CP-PLLs stay below ~$f_{REF}/10$, SSPLLs ~$f_{REF}/20$ for spur and phase reasons."),
    ("How do you measure the loop bandwidth on silicon?",
     "Modulate the reference phase/frequency and measure the output response vs modulation frequency, or read the phase-noise plot: the shoulder where VCO noise takes over approximates $f_c$."),
], 17)

sys.path.insert(0, os.path.dirname(__file__))
import phase1b
phase1b.build(b)
b.save(os.path.join(os.path.dirname(__file__), "..", "phase1_fundamentals.ipynb"))
