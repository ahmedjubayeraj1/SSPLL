"""Interview questions for roadmap step 72 (budget). Shared by the notebook and docs/design/step72_budget.md."""
QA72 = [
("What is a noise budget, and why do it before designing any transistor?",
 "A table that splits the system target (here 1.4 ps typ / 3.2 ps max rms jitter, −110/−120 dBc/Hz at 300 kHz) into one "
 "allocation per block, each in that block's own units (pA/√Hz, nV/√Hz, fs per edge). It turns one system number into "
 "pass/fail tests a single block can be designed and simulated against, and it shows *early* which block dominates — so the "
 "design effort (and power and area) goes there and not to blocks that cannot matter."),
("Why do jitter contributions add in power (rms²) and not linearly?",
 "The sources are physically independent (different devices), so they are uncorrelated and their variances add: "
 "σ² = Σσᵢ². Consequence: a block at half the jitter of the largest one adds only 12% to the total; a block at 1/3 adds 5%. "
 "Fixing small contributors is wasted effort."),
("Write the output phase-noise PSD of the SSPLL with FFNC in terms of the block sources.",
 "S_out(f) = [S_REF·N² + S_PD,eq]·|H + G_c(1−H)|² + S_VCO,eq·|(1−G_c)(1−H)|² + S_NCB + S_alias·|G_c|², where H is the "
 "closed-loop transfer, G_c the cancellation path (SSPD gain × NCB gain, with sinc hold, half-period delay and pole) "
 "and the VCO-like sources (ring, CCO, loop-filter R) all enter at the VCO. Jitter = √(∫S_out df)/(2πf_out), here 10 kHz–40 MHz."),
("Why is the reference noise multiplied by N² but the SSPD noise is not?",
 "The reference sets the *time* of each edge; a time error Δt at f_REF becomes a phase error 2πf_out·Δt at the output, i.e. "
 "N times the reference phase error → N² in power. The SSPD compares the VCO directly (no divider), so its voltage noise "
 "divided by its gain is already a VCO-phase error: no N. That is the whole point of sub-sampling (−130 vs −110.9 dBc/Hz "
 "detector floor at the output, step 8)."),
("Why does FFNC make the reference contribution *worse* (0.20 → 0.31 ps)?",
 "With FFNC on, the in-band transfer becomes |H + G_c(1−H)|²: above the loop bandwidth the cancellation path also passes the "
 "SSPD's view of the reference, so reference (and SSPD/CP) noise reaches the output up to ≈f_REF/8 instead of f_c. FFNC "
 "trades VCO noise for reference noise; it wins because the VCO term is 10× larger."),
("Which block dominates the budget, and what does that tell you?",
 "The ring VCO core (1.87 ps off / 1.13 ps on typ), then the CCO (0.90 / 0.56). Everything else together is < 0.5 ps. "
 "So power, area and design time go to the oscillator and its current source; the SSPD, CP and NCB can be designed for "
 "linearity, spurs and robustness rather than noise."),
("The SSPD kT/C noise contributes only 22 fs. Why not shrink the sampling capacitor to save power?",
 "Because the cap also sets the charge-sharing/kick-back spur and the hold droop; and the SSPD noise is in-band where FFNC "
 "passes it. 100 fF keeps kT/C at −147.8 dBc/Hz (17 dB below the CP allocation), so it is not the limit; going to 25 fF "
 "costs +6 dB noise but buys little power (the ring buffers that drive it set the power). The budget says: free to "
 "choose the cap for spur and matching, as long as Cs ≥ ~50 fF per side."),
("Derive the SSPD kT/C phase-noise floor.",
 "Each side samples kT/C; the differential sample has v² = 2kT/C. The differential slope is 2A per radian of VCO phase, so "
 "one sample carries φ² = (2kT/C)/(2A)² = kT/(2CA²). Samples are independent, so this variance is white over 0…f_REF/2: "
 "S_φ = φ²/(f_REF/2) = kT/(C·A²·f_REF), and L = S_φ/2 = kT/(2·C·A²·f_REF) = −147.8 dBc/Hz for C = 100 fF, A = 0.5 V, "
 "f_REF = 50 MHz."),
("How is the pulsed-Gm charge-pump noise budgeted, and why does the duty cycle matter?",
 "The transconductor's output noise current 4kTγg_m only reaches the loop filter during the pulse (duty d ≈ 1%, 200 ps of "
 "20 ns). The useful signal current is β = 2A·g_m·d (A per rad). Referred to VCO phase: S_φ = 4kTγg_m·d/β² → "
 "L ≈ kTγ/(2A²g_m d) ≈ −140.8 dBc/Hz white, plus a 1/f corner allocated ≤ 300 kHz. Shorter pulses lower the signal more "
 "than the noise at equal g_m, so d is set by β and the spur, not by noise."),
("Why is the loop-filter resistor a visible contributor (0.28 ps) and what are the knobs?",
 "Its 4kTR voltage noise (12.6 nV/√Hz for 9.61 kΩ) is filtered by C1/(C1+C2+sRC1C2) and integrated by K_VCO/s, so it "
 "behaves like VCO noise (high-passed by 1−H, cancelled by FFNC). Knobs: larger β (more CP current → smaller R, larger C, "
 "more area), smaller K_VCO (needs a wider coarse range from the CCO DAC), or a dual-path filter. We accept it: 0.28 ps "
 "adds only ~1% to a 2.1 ps total."),
("Why must the ring 1/f³ corner be halved (1.1 → 0.6 MHz) in this budget?",
 "With the simulated 1.1 MHz corner the proposal's own model gives L(300 kHz) = −108.1 dBc/Hz FFNC-off typ, 1.9 dB short of "
 "the −110 typ in the specification. At 300 kHz the ring is in its 1/f³ region, so L ∝ (1 + f_c3/f); halving f_c3 plus a "
 "lower-flicker CCO brings it to −110.2. Halving needs ~2× gate area in the ring transistors that upconvert flicker, or "
 "better rise/fall symmetry (smaller DC term of the ISF, c₀)."),
("What determines the 1/f³ corner of a ring oscillator?",
 "Hajimiri–Lee: f_1/f³ = f_1/f(device) · (c₀/c_rms)². c₀ is the DC value of the ISF (zero for a perfectly symmetric "
 "waveform), c_rms its rms. So the corner falls with device area (lower device flicker corner) and with symmetry of rise and "
 "fall edges (pMOS/nMOS strength balance, equal loading)."),
("Why is the CCO noise allocated in pA/√Hz, and how do you convert it?",
 "The CCO is a current source: what it delivers to the ring is a noisy current. Frequency noise = K_I·i_n (K_I = ∂f/∂I = "
 "1.22×10¹² Hz/A), phase noise S_φ = (K_I i_n)²/f², L = S_φ/2. L(1 MHz) = −104.2 dBc/Hz ↔ i_n = 7.2 pA/√Hz."),
("Why can't the CCO noise be made arbitrarily small?",
 "A MOS current source of current I with overdrive (headroom) V_ov has i_n² ≈ 4kTγ·2I/V_ov. At 1.31 mA and ~1.2 V "
 "of headroom left by VDDA_min 2.97 V minus the ~1.6–1.8 V ring node, the thermal floor is ≈6–7 pA/√Hz. Degeneration gives "
 "the same limit (4kT/R_s with R_s = V_h/I). Only more headroom or less current helps — the budget therefore allocates the "
 "thermal floor and attacks only the flicker part."),
("Why does a filtered mirror gate help the CCO noise?",
 "In a 1:8 mirror the reference-side noise (DAC unit cells, IBIAS mirror, diode device) is multiplied by 8 at the output. "
 "An RC low-pass on the shared gate (corner ≪ 10 kHz, e.g. a long poly resistor and a MOS cap) removes it inside the "
 "integration band, so only the output devices' own noise remains. It costs area, not power."),
("Why is the NCB intrinsic noise budget so small (31 fs) yet still important?",
 "It is added *after* the loop and the cancellation: nothing filters it, so it appears 1:1 at the output with FFNC on, all "
 "the way to 40 MHz. −150 dBc/Hz white with a 1 MHz flicker corner gives 31 fs. If the delay line were a long chain of "
 "starved inverters, its noise would grow with its delay and could reach hundreds of fs — so the NCB is kept short "
 "(2 cells, small delay range)."),
("How does LDO noise get into the output, and how is that budgeted?",
 "The NCB delay depends on its supply (≈104 ps/V for 4 inverter edges at ~26 ps/V each): a supply noise density v_n becomes "
 "a timing noise K_s·v_n, i.e. phase 2πf_out·K_s·v_n. For ≤ 26 fs contribution the LDO output noise must be ≤ 40 nV/√Hz "
 "(10 kHz flicker corner). The ring itself is fed by the high-impedance CCO, not the LDO, so LDO noise does not modulate "
 "the oscillator directly."),
("What is the aliasing term in the FFNC budget?",
 "The SSPD samples at f_REF, so VCO noise at f ± k·f_REF folds into the 0…f_REF/2 band (Thijssen: S_s(f) = f_REF Σ "
 "S_φ(f − k f_REF)). The cancellation path then *adds* this folded noise to the output (it is not correlated with the "
 "output's own noise at f). It costs 0.19 ps typ — the main reason FFNC cannot cancel everything."),
("Why is the jitter integrated from 10 kHz to 40 MHz?",
 "The proposal's specification band. The lower edge excludes slow wander a downstream system tracks; the upper edge is the "
 "Nyquist range of a 100 MHz-class sampling clock divided output and where the ring's −20 dB/dec skirt has fallen well below "
 "the in-band level. A budget must use the same band as the spec."),
("How do you check a budget against the reference range 45–55 MHz?",
 "Re-run with f_REF = 45 and 55 MHz: f_out scales, the ring's L at 1 MHz scales ~ f_out (same power per edge), the aliasing "
 "and the cancellation bandwidth move with f_REF. Typ jitter goes 2.23/1.51 ps at 45 MHz to 2.01/1.23 ps at 55 MHz "
 "(off/on) — all inside the maxima."),
("What does the 'pessimistic' column represent?",
 "A coherent worst plausible set for the noise numbers: ring +1 dB and 2× 1/f³ corner, CCO +3 dB and 2× corner, reference "
 "receiver +4 dB with a 100 kHz corner, SSPD amplitude 0.35 V, γ = 1.5, NCB −146 dBc/Hz, LDO 80 nV/√Hz and a 30% FFNC gain "
 "error. It is not a SPICE corner; it is the budget's stress case that must still meet the *maximum* spec."),
("The FFNC-on L(300 kHz) is −119.9 typ against a −120 typ spec. Is that a fail?",
 "It is a typ number at the limit, not a guaranteed limit (the max is −110, with 4.5 dB margin pess). At 300 kHz with FFNC on "
 "the floor is set by the reference ×N²: crystal −155 and receiver −155 → −121.2 dBc/Hz together, before any on-chip "
 "noise. Only a cleaner receiver (−157 for ~+0.1 mW) or a better board crystal moves it. This is recorded as a finding."),
("How is the power budget built and why does the LDO domain cost more?",
 "Every block gets a current on a named supply; power = I × supply voltage at the slot. Blocks on the 1.8 V LDO rail draw "
 "their current from VDDA = 3.3 V, so each mA costs 3.3 mW, not 1.8 mW: the LDO burns the 1.5 V difference. That is why "
 "logic that can live on VDDD (1.8 V, 1.8 mW/mA) is put there."),
("Why is the ring fed from VDDA through a CCO instead of from the LDO?",
 "A current-fed ring has low supply sensitivity (the CCO's output impedance isolates it) and the current DAC also gives the "
 "coarse tuning. The price: the ring burns its current at 3.3 V (4.86 mW). Running it from the LDO would cost the same "
 "power from VDDA and add the LDO noise directly to the oscillator."),
("What is the worst-case power and how is it estimated?",
 "Ring at 1.76 GHz, ss, 110 °C, VDDA 3.63 V: 7.46 mW (from the proposal's simulated basis). Other blocks: typ current × 1.3 "
 "at the maximum supply. Total 13.5 mW FFNC on / 11.4 mW off against 15/13 mW maximum."),
("What is the jitter figure of merit and what does this budget give?",
 "FoM = 10·log₁₀[(σ/1 s)²·(P/1 mW)]. σ = 1.36 ps, P = 9.08 mW → −227.8 dB (proposal −227.5). Note the FoM rewards power "
 "and jitter equally in dB: halving the jitter (−6 dB) is worth 4× the power."),
("Why does the area table now include the LDO?",
 "Decision D4 (step 8) added an on-chip LDO for the clean 1.8 V rail; the proposal's area basis listed every block except "
 "it. ~4000 µm² (pass device for ~1.2 mA, error amp, compensation and output cap partly as MOS cap). Total 57,500 µm² — "
 "still below the 0.08 mm² typ."),
("How would you decide between spending 1 mW on a cleaner VCO and 1 mW on a better NCB?",
 "Use the sensitivity of the total to each block: ring +3 dB moves the typ total from 1.36 to 1.77 ps; NCB +3 dB changes "
 "nothing visible. The marginal improvement per mW is far larger at the VCO. A budget makes that comparison numeric."),
("What is the 'sensitivity' table and how is it used during design?",
 "For each block, the total jitter when that block alone is 3 dB worse than allocated. It shows which allocations are "
 "critical (ring, CCO, reference) and which have slack (SSPD, CP, NCB, LDO). Slack can be traded for power, area or "
 "robustness during the block designs."),
("How will each allocation be verified in Phase 8?",
 "Each block's testbench measures its allocation in its own units: SSPD/CP with .noise and PSS-equivalent transient noise "
 "(tb_sspd_char, tb_sscp_*), ring free-running phase noise by transient noise and ISF (tb_vco_*), CCO output current noise "
 "by .noise (tb_cco_ac), LDO output noise and PSRR (tb_ldo_ac), NCB delay noise and supply sensitivity (tb_ncb_*). The "
 "results replace the allocations in step72_budget.py, which recomputes the total."),
("Why keep the budget in a script instead of a spreadsheet?",
 "Because the transfer functions are frequency-dependent and complex (H, 1−H, G_c, aliasing) — a spreadsheet of single "
 "numbers cannot integrate them. A script also re-runs automatically when a simulated curve replaces an allocation, and it "
 "is version-controlled next to the schematics."),
("What layout decisions follow directly from the noise budget?",
 "(1) The ring and its CCO get the cleanest, symmetric placement (dominant noise); (2) the CCO output mirror is large-area, "
 "common-centroid, with a filtered gate; (3) the reference receiver path is short and shielded (it is ×N²); (4) the SSPD "
 "caps are placed symmetrically with dummies (spur, not noise); (5) the NCB is next to the output with its own LDO decap; "
 "(6) the loop-filter C1 stacks MIM over MOS to fit the area."),
("Why is the loop-filter C1 a MOS capacitor with MIM on top, and what is the catch?",
 "C1 = 18.2 pF would need ~9100 µm² as MIM alone (~2 fF/µm²), more than the CP+LF area allocation. A thin-oxide MOS cap "
 "(7.5 fF/µm² at 0.9 V) with a MIM cap stacked above gives ~9.5 fF/µm² → ~1,900 µm² (~11.5 fF/µm² with both MIM layers). Catch: a MOS cap is non-linear and must be kept "
 "in strong inversion/accumulation across the tuning range — acceptable for C1 (the large zero cap), not for C2."),
("What is the effect of a loop-gain (K_VCO or β) error on the budget?",
 "f_c moves (f_c ∝ βK_VCO): a lower f_c lets more VCO noise through and raises FFNC-off jitter; a higher f_c helps here "
 "(2.8 MHz closes the 300 kHz spec alone) but costs phase margin through the sample-and-hold delay (≈ 180°·f_c/f_REF). "
 "icp_trim[1:0] is the knob to recentre f_c after silicon or after the K_VCO of step 74 is known."),
("Why 2× margin between pessimistic budget and the max spec?",
 "The budget's models (ISF-based ring noise, γ, flicker coefficients) carry several-dB uncertainty, and layout parasitics "
 "add noise and power. The proposal says maximum values keep about twice the pre-layout margin; here pess 2.71/1.73 ps vs "
 "4.7/3.2 ps max is 1.7–1.8×."),
("Explain 'L = S_φ/2' and why the code uses 2·10^(L/10).",
 "L(f) is defined as single-sideband noise relative to the carrier; for small phase noise L(f) = S_φ(f)/2 where S_φ is the "
 "one-sided phase PSD. Integrating jitter needs S_φ = 2·10^(L/10) rad²/Hz, then σ_t = √∫S_φ df / (2πf_0)."),
("How does a flicker (1/f) noise source in the CP or SSPD show up at the output?",
 "Below the loop bandwidth H ≈ 1, so a 1/f input source appears as 1/f at the output — it raises L(f) at low offsets "
 "(10–100 kHz). That is why the CP/SSPD allocations include a 300 kHz flicker corner and why their devices are not minimum "
 "length."),
("What would happen to the budget if the reference were 25 MHz with N = 64?",
 "The reference term grows by 20·log(2) = 6 dB (N²), the SSPD term grows because A²·f_REF halves (+3 dB), the cancellation "
 "bandwidth halves (f_REF/8) and aliasing worsens — the 50 MHz reference is a deliberate budget choice."),
("Which allocations are measured on silicon, and how?",
 "Total jitter and L(f) on CLK_OUT (/16 + 24.1 dB), FFNC on vs off on the same chip, supply sensitivity with the VTEST tone, "
 "and power per domain from slot currents with blocks enabled in turn. Individual block noise is not directly observable — "
 "the budget lets you attribute the measured total."),
("A colleague proposes a 3-stage ring to save power. What does the budget say?",
 "The step-6 study: 3 × 1.0 at 0.61 mA gives −87.4 dBc/Hz vs −94.2 for 5 × 1.5 — 6.8 dB worse at the dominant block; jitter "
 "would roughly double. Saving ~2 mW does not pay; the 5-stage verdict stands."),
("Why is the FLL charge pump nearly absent from the noise budget?",
 "It has a dead zone: in lock the phase error sits inside it and the FLL CP is off — no noise current reaches the loop filter. "
 "Its leakage and switch charge injection matter for spurs (step 73), not for random jitter."),
("What are the three numbers every block designer must take away from step 72?",
 "Its noise allocation (in its own units), its supply current on a named supply, and its area. Plus its layout rules from "
 "the budget: which nodes are noise-critical, which must be symmetric and which supply domain it lives in."),
]

# Step 72 redo for the device-rule migration: 800 MHz, 5 V analog devices, no LDO (docs/design/step72_hv_budget.md)
QA72HV = [
("Why is a ring oscillator's timing jitter independent of its frequency at fixed power and FoM, while its phase noise in "
 "dBc/Hz is not?",
 "In the 1/f² region L(Δf) ≈ (2kT/P)·η·(V_DD/V_char)·(f₀/Δf)², so at fixed P and FoM L ∝ f₀². Jitter is the integral of "
 "the phase PSD divided by (2πf₀)², which removes the f₀² again: σ_t² ∝ 1/P. Halving the carrier (1.6 → 0.8 GHz) lowers "
 "L(1 MHz) by 6.02 dB and leaves the seconds unchanged — which is why the 800 MHz budget gives 2.12 / 1.37 ps, the same as "
 "the 1.6 GHz budget (2.11 / 1.36 ps), at the same ring power."),
("At N = 16 the reference noise is multiplied by N² = 256 instead of 1024. Does the reference contribute less jitter?",
 "No. N² converts a reference *time* error into output *phase*: φ_out = 2πf_out·Δt. Halving f_out halves the phase for the "
 "same Δt, so the dBc/Hz drop by 6 dB, but dividing by (2πf_out)² to get seconds undoes it. A timing error at the "
 "reference stays the same timing error at the output (0.20 ps off / 0.31 ps on here, as before)."),
("Thick-oxide (5 V) devices are about 5× slower. How can they give the same or better ring phase noise per milliwatt?",
 "Phase noise per milliwatt is set by the noise current per unit g_m (γ) and by the swing relative to the noise (V_char), "
 "not by f_T. hv_noise.py finds γ = 1.10 for the 5 V nMOS and 0.53 for the 5 V pMOS against 1.87 and 1.22 for the 1.8 V "
 "devices: 2.3–3.6 dB less thermal noise per g_m, because the long channel has no short-channel excess noise. Speed only "
 "limits how high the ring can go (1.1 GHz at ss 110 °C), which is why the carrier moved to 800 MHz."),
("What does γ mean, and why is it larger in short-channel devices?",
 "γ is the ratio of the drain thermal-noise current to 4kT·g_m: S_id = 4kTγg_m. A long-channel device in saturation has "
 "γ ≈ 2/3. In short channels the high lateral field heats the carriers and velocity saturation lowers g_m for the same "
 "channel noise, so γ rises to 1.5–2.5. The 0.15 µm 1.8 V nMOS shows 1.87; the 0.5 µm 5 V nMOS, with a thick oxide and a "
 "weaker field, shows 1.10."),
("Why does VDDA noise through the NCB add directly to the output, while VDDA noise into the ring is cancelled by the FFNC?",
 "The NCB is the last block: a supply change shifts its delay by K_s·Δv, an output timing error that nothing after it can "
 "see — S_φ = (2πf₀K_s)²S_v. A supply change in the ring changes its *frequency* (K_vdd·Δv), so it integrates to phase like "
 "any VCO noise; the loop high-passes it and the SSPD measures the resulting phase error, which the FFNC then removes."),
("How would you measure K_vdd and K_s in simulation, and why must K_vdd stay small although the loop high-passes it?",
 "K_vdd: run the free-running ring at two VDDA values (or a small sine on VDDA) and take Δf/ΔV (tb_vco_kvdd). K_s: drive the "
 "NCB with a fixed input and measure the output-edge delay at two VDDA values (Δt/ΔV). K_vdd matters because the noise it "
 "brings in is VCO-like and grows as 1/f²: at 20 MHz/V and 300 nV/√Hz it adds 1.17 ps with FFNC off — as much as "
 "the CCO. A cascoded CCO with L ≥ 1 µm keeps it at 5 MHz/V (0.10 ps)."),
("Going from L = 0.5 µm to 1 µm cuts the 5 V nMOS 1/f corner by 20×, though the gate area grows only about 6×. Why?",
 "At constant g_m/I_D and current, the longer device is wider and its gate area W·L grows ~6×, which lowers the flicker "
 "PSD ~6×. But the corner frequency is flicker divided by thermal, and thermal per g_m stays about the same, so area alone "
 "gives ~6×. The rest comes from the model: SKY130's flicker parameters depend on the length bin (short devices have more "
 "edge and halo-implant traps per area). Lesson: for current sources, take the length the model rewards and measure it — "
 "hv_noise.py is that measurement."),
("Why does the SSPD gain A per VCO radian double at half the carrier, and what does that do to its kT/C noise?",
 "A = (edge slope)/ω₀: the sampler converts a timing error into a voltage through the slope, and one radian at 800 MHz is "
 "twice as long in time as at 1.6 GHz. With the same slope, A doubles. The kT/C term L = kT/(2C_sA²f_REF) falls by 6 dB in "
 "rad² — the same timing error in seconds — and stays negligible (0.04 ps)."),
]
