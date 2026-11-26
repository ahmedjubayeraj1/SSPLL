# Proposal specification, final values (20 Nov 2026)

The proposal (rev 101) lists only final values. This note records how each one was set.
Each value is the pre-layout prediction after the block designs, plus a margin for layout parasitics and silicon.
Keep it for the review.

## Margins used

| Quantity | Margin | Why |
|---|---|---|
| Jitter | +20 % | extracted parasitics (slower edges, extra node capacitance on the 3.3 V clocks), layout-dependent device shifts, measurement-setup noise |
| Phase noise L(300 kHz) | +2 dB | the same causes, in dB (+20 % jitter ≈ +1.6 dB) |
| Power | +15 % | routing capacitance on the 3.3 V clock and sampler nets (C·V²·f), extra buffering after layout |
| Spur | kept (−55 / −45 dBc) | predictions are far below: SSPD kick-back −99 dBc; the Gm's charge at lock is cancelled within the pulse |

## Prediction → specification

Predictions come from the system model `design/budget/hv_system.py`, which uses the measured blocks (`design/sscp/data/sscp_hv_noise.json`).
Conditions: typical = tt, 3.3 V square reference; maximum = worst case or the pessimistic chain.

| Row | Pre-layout | With margin | Proposal before | Proposal now |
|---|---|---|---|---|
| Jitter, FFNC off, typ | 1.98 ps | 2.38 ps | 2.6 | **2.4** |
| Jitter, FFNC off, max | 3.70 ps (worst) | 4.44 ps | 5.0 | **4.5** |
| Jitter, FFNC on, typ | 1.33 ps | 1.60 ps | 1.6 | **1.6** |
| Jitter, FFNC on, max | 2.50 ps (worst) | 3.00 ps | 3.2 | **3.0** |
| Jitter reduction by FFNC, typ | 33 % | about 30 % | 35 | **30** |
| L(300 kHz), FFNC off, typ | −117.1 dBc/Hz | −115.1 | −114 | **−115** |
| L(300 kHz), FFNC off, max | −112.5 (pess) | −110.5 | −108 | **−110** |
| L(300 kHz), FFNC on, typ | −124.9 dBc/Hz | −122.9 | −124 | **−123** |
| L(300 kHz), FFNC on, max | −118.7 (pess); −118.0 (1 V sine, pess) | −116.0 | −116 | **−116** |
| Power, FFNC on, typ | 8.38 mW | 9.64 mW | 9.1 | **9.6** |
| Power, FFNC on, max | ≈ 11.7 mW (worst corner, block sums) | 13.4 mW | 15 | **14** |
| Power, FFNC off, typ | 6.93 mW | 7.97 mW | 7.7 | **8.0** |
| Power, FFNC off, max | ≈ 9.6 mW | 11.0 mW | 13 | **11** |
| Jitter FoM (1.6 ps, 9.6 mW) | | | −226.3 dB | **−226.1 dB** |
| Abstract | | | "about 9 mW" | **"about 10 mW"** |

The two rows that got looser are the typical L(300 kHz) with FFNC on (−124 → −123 dBc/Hz) and the typical power (9.1 → 9.6 mW).
Neither block moved toward worse noise; they loosened only because the margin is now inside the number:
- pre-layout predictions: −124.9 dBc/Hz and 8.38 mW;
- with margin: −122.9 dBc/Hz and 9.64 mW.

Every other row is equal or tighter.

## Typical power, block by block (FFNC on, tt)

| Block | Step | mW |
|---|---|---|
| After the VCO design: ring 3.69 (instead of 4.86), two buffers 0.59 (instead of 0.99), other blocks as budgeted | 74 | 7.55 |
| CCO overhead 0.23 (instead of 0.41) | 75 | −0.18 |
| REF receiver 0.23 (instead of 0.20) | 76 | +0.03 |
| Clock generator 0.72 (instead of 0.41 incl. level shifters) | 77 | +0.31 |
| SSPD 1.03 (instead of 0.49) | 78 | +0.54 |
| Pulsed-Gm charge pump 0.30 (instead of 0.17) | 79 | +0.13 |
| **Total** | | **8.38** |

FFNC off removes the NCB (1.45 mW): 6.93 mW.

## Worst-case power (block sums, ×1.3 current at 3.63 V where a block has no measured worst case)

| Block | Value (mW) |
|---|---|
| Ring + CCO | 4.64 + 0.30 |
| Output buffers | 0.77 |
| SSPD | 1.36 (ff_ll) |
| Clock generator | 0.96 |
| Gm | 0.39 |
| Receiver | 0.39 |
| FLL charge pump | 0.09 |
| Bias | 0.24 |
| NCB | 2.08 |
| Dividers and logic | 0.43 |
| **Total** | **≈ 11.7 (FFNC on), ≈ 9.6 (FFNC off)** |
