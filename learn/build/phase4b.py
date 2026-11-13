"""Phase 4 part B: steps 53-58."""


def build(b, SIM):
    # -------------------------------------------------------------------------------------------- step 53
    b.step(53, "What the SSPLL solves (request 8)", "N² on PD/CP, divider noise and power, CP-mismatch insensitivity, low ripple, a wider f_c for ring VCOs")
    b.md(r"""
| Problem of the Type-II CP-PLL | How the SSPLL solves it | Why |
|---|---|---|
| PFD/CP noise ×N² (+30.1 dB at N = 32) | detector noise referred to VCO phase with gain A, not ×N² | no divider in the loop (step 48) |
| divider noise and power in the loop | no divider in the main loop; the FLL divider is idle in lock | SSPD samples the VCO directly |
| CP mismatch → static offset and spurs | at lock the sample ≈ 0, so the Gm current ≈ 0; no reset pulses with both sources on | the detector output itself is zero at lock |
| ripple from $I_pR_1$ steps every period | small pulsed current proportional to a tiny sample | the "error" is a voltage near zero |
| high in-band floor limits the bandwidth of a ring PLL | floor drops ~20 dB → the full $f_{REF}/20$ bandwidth suppresses ring noise | step 44 |
| — | the held voltage is a direct measure of each edge's timing error | enables FFNC (Phase 6) |

Numbers on our design point (same ring, reference, N, 2.5 MHz; models/step8_variants.py):
""")
    b.code(r'''
import sys; sys.path.insert(0, "../models")
import pllmodel as pm
rows = []
for name, v, d in (("Type-II CP-PLL", "type2", pm.TYPE2_TYP), ("SSPLL", "sspll", pm.TYP), ("SSPLL + FFNC", "ffnc", pm.TYP)):
    j, f, L = pm.jitter(d, v)
    rows.append((name, j["TOTAL"]*1e12, L[np.argmin(abs(f-1e5))], L[np.argmin(abs(f-1e6))]))
fig = make_subplots(rows=1, cols=2, subplot_titles=("rms jitter 10 kHz-40 MHz (ps)", "phase noise (dBc/Hz)"))
fig.add_trace(go.Bar(x=[r[0] for r in rows], y=[r[1] for r in rows], text=[f"{r[1]:.2f}" for r in rows], name="jitter"), 1, 1)
fig.add_trace(go.Bar(x=[r[0] for r in rows], y=[r[2] for r in rows], name="L(100 kHz)"), 1, 2)
fig.add_trace(go.Bar(x=[r[0] for r in rows], y=[r[3] for r in rows], name="L(1 MHz)"), 1, 2)
fig.update_yaxes(range=[-125, -95], row=1, col=2)
show(fig, 420)
for r in rows: print(f"{r[0]:15s} jitter {r[1]:.2f} ps   L(100k) {r[2]:.1f}   L(1M) {r[3]:.1f} dBc/Hz")
''')
    b.qa([
        ("List the problems a sub-sampling PLL solves.",
         "No N² on PD/CP noise, no divider noise/power in the loop, insensitivity to CP mismatch (zero current at lock), low ripple/spurs from the CP, and enough in-band headroom to use a wide bandwidth with a ring VCO."),
        ("Why is an SSPLL insensitive to charge-pump mismatch?",
         "At lock the sampled voltage is ~0, so the transconductor's net output current is ~0; there are no PFD reset pulses with both sources on. Gm offset still matters (it shifts the lock point slightly)."),
        ("What is the in-band phase noise of a good SSPLL?",
         "Limited by the reference ×N² and the sampler/Gm: Gao reported −126 dBc/Hz at 2.2 GHz; our budget is −120 dBc/Hz at 1.6 GHz (FFNC on)."),
        ("Does the SSPLL reduce reference noise?",
         "No; reference (crystal + buffer) noise is still ×N² and becomes the in-band limit."),
        ("How much does the SSPLL improve jitter for our ring VCO at the same bandwidth?",
         "From 2.52 to 2.29 ps (typical): modest, because the ring dominates; the bigger benefit is enabling FFNC (to 1.40 ps)."),
        ("What does the SSPLL cost?",
         "An acquisition loop (FLL), sampler kickback/load-modulation spurs, amplitude-dependent gain, narrow linear range, hold delay (lower usable bandwidth)."),
        ("Why does the SSPLL save power compared with a CP-PLL?",
         "No high-speed divider running in lock in the main loop; the FLL divider can even be gated off after lock."),
        ("Why does the SSPLL enable FFNC but a CP-PLL does not?",
         "FFNC needs a continuous voltage proportional to the timing error of each edge; the SSPD's held sample is exactly that. A PFD gives pulse widths."),
        ("What is FoM of Gao's 2.2 GHz SSPLL?",
         "0.15 ps rms at 7.6 mW (ISSCC 2009): about −247 dB — an LC-VCO design; ring SSPLLs are around −225 to −236 dB (Nagam −236.3 with FFNC)."),
    ], 53)

    # -------------------------------------------------------------------------------------------- step 54
    b.step(54, "Limit: narrow capture range, false lock, slow relock after a disturbance (Hsu, Geng)", "explanation and simulation")
    b.md(r"""
### What happens
After a disturbance (supply step, coupling burst) that moves the VCO frequency by more than the capture range, the SSPD loop alone
re-locks to the **nearest harmonic**, which may be wrong. With a dead-zone FLL it returns to $32f_{REF}$, but only after the FLL
notices (the divided phase must leave the dead zone) — **relock is slow**.

### How the literature attacks it
- **Hsu, Tripurari, Yu, Kinget (CICC 2011):** a PFD with an *auxiliary* SSPD — the PFD loop keeps acquisition robust while the SSPD lowers
  in-band noise.
- **Geng, Xie, Wang (TCAS-II 2021):** a *quadrature* SSPD samples I and Q; the pair detects the direction of frequency error, giving
  fast relock under interference without a separate FLL.

Below: lock first, then kick $V_{cont}$ at 30 µs. Second figure: the **dead-zone width** itself — too narrow and the FLL and SSPD fight
(limit cycle); wide enough and the hand-over is clean.
""")
    b.code(SIM + r'''
def frame(kick_mV):
    r0, _ = sspll_sim(0.0, use_fll=False, ncyc=5000, kick_at=1500, kick_V=kick_mV*1e-3)
    r1, _ = sspll_sim(0.0, use_fll=True, ncyc=5000, kick_at=1500, kick_V=kick_mV*1e-3)
    late = np.where(abs(r1['f'] - 32) > 2e-3)[0]
    tr = (r1['t'][late[-1]] - 30e-6)*1e6 if len(late) else 0
    return ([dict(x=r0['t']*1e6, y=r0['f'], name="SSPD only"), dict(x=r1['t']*1e6, y=r1['f'], name="with FLL")],
            f"V_cont kick {kick_mV} mV ({kick_mV*1e-3*300e6/50e6:.2f} f_REF): SSPD alone ends at {np.round(r0['f'][-1]):.0f} x f_REF; "
            f"with FLL at {np.round(r1['f'][-1]):.0f} x f_REF, relock {tr:.1f} us after the kick")
fig = sweep([20, 60, 120, 200, 300, 500], frame, "kick on V_cont (mV)", active=3,
            layout=lambda f: f.update_xaxes(title="time (us)").update_yaxes(title="VCO frequency / f_REF"))
show(fig, 430)
def frame2(dzp):
    r, _ = sspll_sim(2.4, use_fll=True, ncyc=6000, dz=dzp*np.pi)
    clean = r['fll'][-300:].sum() == 0 and r['f'][-300:].std() < 1e-3
    return ([dict(x=r['t']*1e6, y=r['f'], name="VCO frequency / f_REF"),
             dict(x=r['t']*1e6, y=30 + r['fll'].astype(float), name="FLL active (offset 30)", line=dict(shape="hv"))],
            f"dead zone +/-{dzp} pi (rad of REF): " + ("clean hand-over, FLL silent in lock" if clean else "FLL and SSPD fight: limit cycle"))
fig = sweep([0.3, 0.4, 0.5, 0.65, 0.8], frame2, "dead zone (x pi)", active=3,
            layout=lambda f: f.update_xaxes(title="time (us)").update_yaxes(range=[29.8, 35]))
show(fig, 430)
''')
    b.qa([
        ("Why is the relock of an SSPLL slow?",
         "The SSPD cannot detect frequency; the FLL only acts after the divided phase error leaves its dead zone, then must pull the frequency back, then hand over again."),
        ("What happens if a disturbance moves the VCO by one f_REF and the FLL is off?",
         "The SSPD locks to the neighbouring harmonic (31 or 33 × f_REF) — a false lock that persists."),
        ("What did Hsu et al. propose?",
         "A PFD-based PLL with an auxiliary sub-sampling PD to suppress in-band noise while keeping the PFD's robust acquisition."),
        ("What is a quadrature SSPD and why does it help?",
         "Two samplers 90° apart (I/Q); the rotation direction of the (I,Q) vector reveals the sign of the frequency error, so frequency can be corrected directly — fast relock (Geng et al.)."),
        ("What sets the width of the FLL dead zone?",
         "Large enough to contain an SSPD lock point and transient phase wander (≥ π/N plus margin), small enough to catch slips to neighbouring harmonics (the divided phase moves 2π per beat)."),
        ("What happens with a too-narrow dead zone (seen in the simulation)?",
         "After frequency acquisition the SSPD's lock point can sit just outside the dead zone; the FLL keeps pushing, the SSPD slips, and the two loops form a limit cycle."),
        ("How do you make the FLL robust over PVT?",
         "Choose the dead zone with margin, a modest FLL current (fast enough but not overpowering), and verify lock from many initial offsets and corners, including a mid-lock disturbance."),
        ("What kind of disturbances cause relock events in an SoC?",
         "Large supply/ground bounce from digital activity, substrate coupling bursts, power-gating events on the VCO supply."),
        ("How could you detect loss of lock on chip?",
         "Lock detector: count VCO/32 vs REF cycles over a window, or monitor whether the FLL becomes active (`fll_active` output in the proposal)."),
    ], 54)

    # -------------------------------------------------------------------------------------------- step 55
    b.step(55, "Limit: sampler spurs (load modulation, charge injection, charge sharing); REF noise still ×N²; ring noise beyond f_c", "derivations")
    b.md(r"""
### What happens
The sampler is connected to the VCO only part of the time. Each reference period it (1) **changes the load** on the sampled node, (2)
**injects charge** (kickback) into it when the switch toggles, and (3) **shares charge** between the sampling and hold capacitors and the
VCO node. All three repeat at $f_{REF}$ → reference spurs.

### How (load modulation, first order)
A ring's period is proportional to the total switched node capacitance $\Sigma C$. If the sampler adds $\Delta C$ during a fraction $d$ of
each period, the VCO frequency drops by $\delta f = f_0\,\Delta C/\Sigma C$ for that fraction. The first Fourier component of this
rectangular frequency modulation is $a_1 = \frac{2\delta f}{\pi}\sin(\pi d)$, a phase modulation $\beta = a_1/f_{REF}$, and
$$\text{spur} \approx 20\log_{10}\frac{\beta}{2} = 20\log_{10}\left(\frac{f_0}{f_{REF}}\frac{\Delta C}{\Sigma C}\frac{\sin\pi d}{\pi}\right).$$
With $f_0/f_{REF} = 32$, even $\Delta C/\Sigma C = 10^{-3}$ gives about −40 dBc: an **isolation buffer** (tiny, constant input capacitance)
between VCO and sampler is mandatory, plus a dummy sampler on the complementary node to balance the load.

### The other two limits
**Reference noise** is still ×N² (−121.9 dBc/Hz in band); the REF buffer must be very low-noise. **Ring noise beyond $f_c$** is not
touched by any loop: the SSPLL alone stays at ~2.3 ps; FFNC (Phase 6) attacks exactly this band.
""")
    b.code(r'''
dC = np.logspace(-3, 1, 200)*1e-15                         # added capacitance while sampling (F)
SigC = 300e-15                                              # total switched ring-node capacitance (assumed 10 nodes x 30 fF)
def frame(d):
    spur = 20*np.log10(32*dC/SigC*np.sin(np.pi*d)/np.pi)
    return ([dict(x=dC*1e15, y=spur, name=f"load modulation, duty {d}"),
             dict(x=[dC[0]*1e15, dC[-1]*1e15], y=[-45, -45], name="proposal limit -45 dBc", line=dict(dash="dot"))],
            f"track duty {d}: {np.interp(0.1e-15, dC, spur):.0f} dBc for 0.1 fF, {np.interp(1e-15, dC, spur):.0f} dBc for 1 fF of load change")
fig = sweep([0.05, 0.1, 0.25, 0.5], frame, "fraction of the period the sampler tracks", active=3,
            layout=lambda f: f.update_xaxes(type="log", title="capacitance change seen by the VCO (fF)").update_yaxes(title="spur (dBc)"))
show(fig, 420)
''')
    b.qa([
        ("What is VCO load modulation in an SSPLL?",
         "The sampler's capacitance appears on the VCO node only while tracking; the VCO frequency changes periodically at $f_{REF}$ → spurs."),
        ("Estimate the spur from load modulation.",
         "$\\delta f/f_0 = \\Delta C/\\Sigma C$ for fraction d; $\\beta = 2\\delta f\\sin(\\pi d)/(\\pi f_{REF})$; spur $= 20\\log(\\beta/2)$."),
        ("Why does the spur scale with f_0/f_REF?",
         "A given fractional frequency deviation accumulates more phase over a longer reference period: $\\beta \\propto \\delta f/f_{REF}$."),
        ("What is kickback?",
         "Charge injected into the VCO node by the sampling switch's gate edges (feedthrough and channel charge), once per period."),
        ("How do dummy samplers help?",
         "A matched switch on the complementary node (or a half-size dummy) cancels injected charge and balances the load seen by both VCO outputs."),
        ("Why use an isolation buffer between VCO and sampler?",
         "Its input capacitance is small and constant, so the VCO sees almost no load change; the buffer absorbs the kickback. It costs power and adds its own noise."),
        ("What is the 'DLL-tuned tracking edge' idea?",
         "Track the VCO only for a short window just before the sampling edge (timed by a delay), reducing the load-modulation duty d."),
        ("Which noise remains ×N² in the SSPLL?",
         "Reference (crystal) and reference buffer noise, and sampling-edge jitter."),
        ("Why does the SSPLL not fix ring noise beyond the loop bandwidth?",
         "No loop suppresses VCO noise above $f_c$; only a cleaner VCO, more power, or feedforward cancellation helps there."),
        ("What spur levels did Nagam report?",
         "Reference spurs of −60.2 dBc without cancellation and −55.2 dBc with cancellation (the NCB path also couples the reference)."),
    ], 55)

    # -------------------------------------------------------------------------------------------- step 56
    b.step(56, "Limit: sinusoidal gain non-linearity, ambiguity beyond ±π/2, ring supply sensitivity", "explanation")
    b.md(r"""
### What happens
The SSPD characteristic is $v = A\sin\Delta\phi$ (sine VCO) or a saturating curve (ring). Its slope — the loop gain — is $A\cos\Delta\phi$:
- near 0 it is maximal and linear;
- at ±π/2 the gain falls to zero (the loop stops correcting);
- beyond ±π/2 the slope is **negative**: the equilibrium there is unstable, the loop pushes the phase away → cycle slip;
- the amplitude A (or the ring's slew rate) depends on **supply, corner and temperature**, so loop bandwidth and FFNC gain move with them.

### Why it matters
Large phase errors during transients get *less* correction (slower recovery) and may slip; a supply step that changes the ring's swing
changes both $f_c$ and the cancellation gain $K_{t}$ — one reason FFNC needs calibration (Phase 6).
""")
    b.code(r'''
ph = np.linspace(-np.pi, np.pi, 400)
def frame(e_deg):
    e = np.radians(e_deg)
    return ([dict(x=np.degrees(ph), y=np.sin(ph), name="SSPD characteristic sin(dphi) (x A)"),
             dict(x=np.degrees(ph), y=np.cos(ph), name="local gain cos(dphi)", line=dict(dash="dash")),
             dict(x=[e_deg], y=[np.sin(e)], mode="markers", marker=dict(size=12), name="operating point")],
            f"phase error {e_deg} deg: local gain {np.cos(e):.2f} x A" + ("  -> NEGATIVE: unstable, the loop pushes away (slip)" if np.cos(e) < 0 else ""))
fig = sweep([0, 20, 45, 70, 90, 110, 150], frame, "phase error (deg)", active=2,
            layout=lambda f: f.update_xaxes(title="VCO phase error at the sample (deg)").update_yaxes(range=[-1.2, 1.2]))
show(fig, 420)
''')
    b.qa([
        ("What is the small-signal gain of an SSPD at phase error Δφ?",
         "$A\\cos\\Delta\\phi$: maximum at 0, zero at ±π/2, negative beyond."),
        ("Why is there an ambiguity beyond ±π/2?",
         "The sine is symmetric; a sample value corresponds to two phases, one on each slope. On the negative slope feedback becomes positive and the phase runs away to the next stable point."),
        ("How does the ring supply affect the SSPLL loop?",
         "The ring's swing and edge rate change with supply → $K_{PD}$ changes → loop bandwidth and FFNC gain change; supply noise also directly modulates the VCO frequency."),
        ("How do you make the SSPD gain less amplitude-dependent?",
         "Limit/saturate the waveform with a buffer (gain set by the buffer's slope), regulate the ring supply, or calibrate (Nagam's NCB gain calibration absorbs $K_t$ changes)."),
        ("Why might large phase transients recover slowly in an SSPLL?",
         "The effective gain falls as cos(Δφ); at large errors the loop gain is small, so recovery is slow and may slip."),
        ("Is the PFD characteristic better in this respect?",
         "Yes: linear over ±2π with constant slope, and frequency detection beyond; the SSPD trades this robustness for low noise."),
        ("What is the linear range in time for our 1.6 GHz VCO?",
         "±π/2 VCO radians ≈ ±156 ps; for <10% gain error, about ±0.45 rad ≈ ±45 ps."),
        ("How does the ring waveform shape change the characteristic?",
         "A sharper (more square) waveform gives a steeper slope near the crossing (higher gain) but a narrower linear range, saturating sooner."),
    ], 56)

    # -------------------------------------------------------------------------------------------- step 57
    b.step(57, "Fixes: dummy samplers, isolation buffers, tracking window, low-noise REF buffer, combined PD, QSSPD, FFNC", "limit-to-fix table")
    b.md(r"""
| Limit | Fix | Where in our design |
|---|---|---|
| false lock / narrow capture | dead-zone FLL (÷32 + PFD + CP) | FLL block, `fll_en`, `fll_active` |
| slow relock | quadrature SSPD (Geng) or PFD + auxiliary SSPD (Hsu) | future scope; FLL with tuned dead zone now |
| load modulation | isolation buffer, short tracking window (delay-tuned) | AC-coupled buffers on ring nodes |
| kickback / charge injection | dummy sampler on the complementary node, differential sampling | differential SSPD with dummies |
| charge sharing / hold lag | sized $C_s/C_h$, non-overlapping clocks, early Gm pulse | two-switch SSPD (Nagam), clock generator |
| filter area from high gain | pulsed Gm ($\beta = 2Ag_m\tau/T$) | pulsed-Gm CP, RC/derived pulser |
| amplitude-dependent gain | limit the swing, current-fed (CCO) ring, calibration | CCO supply; NCB gain calibration |
| REF noise ×N² | low-noise, steep-edge REF buffer; clean crystal (≤ −155 dBc/Hz floor) | self-biased 3.3 V receiver |
| ring noise beyond $f_c$ | **feedforward noise cancellation** | NCB delay line, `ffnc_en`, `ncb_code` |
""")
    b.qa([
        ("Name three ways to reduce SSPLL reference spurs.",
         "Isolation buffers between VCO and sampler, dummy samplers/differential sampling, a short tracking window (low duty), and careful layout symmetry."),
        ("Why must the reference buffer be very low-noise in an SSPLL?",
         "Reference noise is ×N² and, with the detector noise removed from N², it is the dominant in-band source."),
        ("What does a combined PFD/SSPD give you?",
         "Robust acquisition and frequency detection from the PFD with in-band noise from the SSPD (Hsu)."),
        ("What problem does FFNC solve that no loop technique can?",
         "VCO noise between the loop bandwidth and ~$f_{REF}/8$, where the loop cannot help."),
        ("Why does a CCO (current-fed ring) help the SSPLL?",
         "Better supply rejection (current source output resistance) → less supply-induced phase noise and gain variation; also lower supply-path noise than an LDO in our study."),
        ("Which fixes cost power?",
         "Isolation buffers, low-noise REF buffer, FFNC delay line and its amplifier; the proposal budgets about 0.8 mW for the NCB."),
        ("How does a non-overlapping clock generator help the two-switch SSPD?",
         "It guarantees sw2 opens/closes only when sw1 is open, so the hold node never connects directly to the tracking node."),
    ], 57)

    # -------------------------------------------------------------------------------------------- step 58
    b.step(58, "Lab: SSPLL lock, explained waveform by waveform", "annotated plots")
    b.md(r"""
### What you do
Run the full behavioural SSPLL from different coarse-calibration errors and read every waveform:
1. **VCO frequency** — FLL drags it toward $32f_{REF}$ (straight ramps = PFD saturated), then the SSPD takes over.
2. **SSPD sample** $\sin(e)$ — a beat while out of lock; it freezes near 0 at lock.
3. **FLL activity** — on during acquisition, off in lock (dead zone).
4. **$V_{cont}$** — settles at the value that cancels the coarse error: $\Delta V = -\text{offset}\cdot f_{REF}/K_{VCO}$.

The transistor-level testbenches of the previous design (`tb_top_lock`, `tb_top_spur`, `tb_sscp_chain` in the project, 2.36 GHz) show
the same sequence; the new 1.6 GHz benches are written in Phase 8 and must reproduce these waveforms.
""")
    b.code(SIM + r'''
def frame(off):
    r, d = sspll_sim(off, use_fll=True, ncyc=4000)
    late = np.where(abs(r['f'] - 32) > 2e-3)[0]
    tl = r['t'][late[-1]]*1e6 if len(late) else 0
    return ([dict(x=r['t']*1e6, y=r['f'], name="f_VCO / f_REF", row=1, col=1),
             dict(x=r['t']*1e6, y=np.sin(r['e']), name="SSPD sample sin(e)", row=2, col=1),
             dict(x=r['t']*1e6, y=r['fll'].astype(float), name="FLL active", line=dict(shape="hv"), row=3, col=1),
             dict(x=r['t']*1e6, y=r['vc']*1e3, name="V_cont (mV)", row=4, col=1)],
            f"coarse error {off:+.1f} f_REF ({off*50:.0f} MHz): locked at 32 x f_REF after {tl:.1f} us; final V_cont {r['vc'][-1]*1e3:.0f} mV "
            f"(expected {-off*50e6/300e6*1e3:.0f} mV)")
fig = sweep([-2.0, -0.8, 0.4, 1.0, 1.8, 3.0], frame, "coarse frequency error (multiples of f_REF)", active=3, rows=4, cols=1,
            shared_xaxes=True, subplot_titles=("VCO frequency / f_REF", "SSPD sample", "FLL active", "V_cont (mV)"), height=800,
            vertical_spacing=0.06, layout=lambda f: f.update_xaxes(title_text="time (us)", row=4, col=1))
show(fig)
''')
    b.qa([
        ("Describe the lock sequence of our SSPLL.",
         "Coarse code sets the CCO near 1.6 GHz; the FLL (÷32 + PFD) pulls the frequency to 32 f_REF; its divided phase error enters the dead zone and the FLL goes quiet; the SSPD loop locks the phase to the nearest VCO zero crossing; FFNC can then be enabled."),
        ("What does a beating SSPD sample tell you?",
         "The VCO is not at an integer multiple of f_REF; the beat frequency is the distance to the nearest harmonic."),
        ("How do you confirm in simulation that the PLL locked to the right harmonic?",
         "Measure the VCO frequency over many reference periods (or count VCO/32 vs REF edges): it must be exactly 32 × f_REF; the FLL must be inactive."),
        ("What final V_cont do you expect for a coarse error of +1 f_REF with K_VCO = 300 MHz/V?",
         "−50 MHz / 300 MHz/V = −167 mV relative to the free-running point."),
        ("Why is lock time longer for larger coarse errors?",
         "The FLL slews the frequency at a limited rate (its CP current into the filter), and each harmonic crossing takes time before the SSPD can hold."),
        ("What would you check in the transistor-level lock bench besides lock?",
         "Ripple on V_cont, spurs (FFT), FLL hand-over timing, power, behaviour over PVT and Monte Carlo, and that the ring supply node stays below 1.8 V."),
        ("Why are behavioural results checked before transistor sims?",
         "They are fast, expose architecture-level issues (dead-zone width, FLL strength, loop stability) and give targets for the circuits."),
    ], 58)
