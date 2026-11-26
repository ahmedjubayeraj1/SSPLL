# Architecture decision (frozen for the 23 Nov 2026 proposal)

- Reference: external crystal oscillator, 45-55 MHz, 50 MHz nominal (floor <= -155 dBc/Hz)
- Fixed N = 32 -> f_out 1.44-1.76 GHz, 1.600 GHz nominal
- Ring: 5-stage pseudo-differential (odd -> no common-mode latch), every cell device 1.5x original width
- Oscillator fed by 5-bit current DAC + 1:8 mirror from 3.3 V; ring supply node <= 1.8 V by design
- SSPD + pulsed-Gm CP + type-II filter, ~2.5 MHz loop bandwidth
- Feedforward noise cancellation (NCB), 4-bit gain, bypassable (ffnc_en)
- New small LDO (3.3 V devices, VREF 1.2 V) -> 1.8 V analog rail for SSPD, CP, ring buffers, NCB; the ring itself is fed by the CCO (step 8)
- On silicon: SSPLL and SSPLL + FFNC (ffnc_en). Type-II CP-PLL baseline: simulation only, same ring and N (step 8, docs/architecture_decision.md)
- Dead-zone FLL with /32 TSPC divider
- Outputs: f_out and /2, /4, /8, /16 taps to the SoC; CLK_OUT /16, /32, /64 for measurement
- Pads: REF_IN (analog, self-biased VDDA/2, AC-coupled receiver), CLK_OUT, VTEST (analog)

Rejected (evidence in sim/startup_results.md): 4-stage ring (latches), 4-stage + cross-coupled latch
(stays latched, too slow), 5-stage at 2.36 GHz (exceeds 1.8 V at ss/110 C), programmable N (scope, 2-person team).

Key numbers: final_budget.txt. Typ jitter 1.56 ps on / 2.40 ps off @ 1.6 GHz; spec max 3.2 / 4.7 ps.
