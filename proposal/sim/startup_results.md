# Ring start-up check (10 Nov 2026)

Symmetric power-up: current ramps 0 -> I in 2 ns, every node starts at 0 V (no differential kick).

| Ring | tt 27C | ss 110C 10fF | ff -40C | fs 27C | sf 27C |
|---|---|---|---|---|---|
| 4-stage, original cell | latched | latched (supply 1.95 V) | latched | latched | oscillates |
| 5-stage, original cell | 2.41 GHz | 2.36 GHz | 2.34 GHz | - | - |
| 4-stage + 2/1 um cross-coupled latch | 2.64 GHz | 1.91 GHz @1.5 mA | 1.80 GHz | 2.59 GHz | measure unclear |

Latched state (4-stage, original cell): vop = vom = high, p1 = m1 = low, p2 = m2 = high, p3 = m3 = low.
Forced common-mode latch with the cross-coupled cell stayed stuck at ss and fs, but that run has exactly
zero differential signal (perfectly symmetric netlist); it needs a mismatch/noise run to decide.

5-stage with lighter MOS tuning cap (ss 110C, 10fF, 1.6 mA): W=3 -> 1.942 GHz, W=1.5 -> 1.948, W=0.75 -> 1.952 GHz.
The tuning cap is not the dominant load.

## Architecture comparison (10 Nov 2026, ss 110C, 10 fF wiring per node, ring supply kept <= 1.75 V)

4-stage + cross-coupled latch, forced common-mode state + 10 mV differential kick:
latch 1/0.5 um stays stuck at tt, ss, fs; latch 2/1 um stays stuck at ss, fs. Rejected.
Speed with latch at ss/110/10fF: 1/0.5 -> 2.38 GHz needs 1.82 V; 2/1 -> 2.31 GHz needs 1.90 V.

5-stage, all cell widths scaled (r5s_tmpl.sp, %SC%), ss/110/10fF:
x1.5: 2.0 mA 1.928 GHz 1.637 V; 2.3 mA 2.104 GHz 1.723 V; 2.6 mA 2.266 GHz 1.805 V  -> fmax(1.75 V) ~2.16 GHz
x2.0: 2.6 mA 2.012 GHz 1.622 V; 3.0 mA 2.200 GHz 1.708 V; 3.4 mA 2.373 GHz 1.791 V -> fmax(1.75 V) ~2.29 GHz
x1.0: fmax(1.75 V) ~1.94 GHz

Jitter budget (10 kHz-40 MHz, typ off/on, pess off/on, fs):
5-stage x1.0 N=36 1.769 GHz: 2612/1706, 4375/2843
5-stage x1.5 N=36 1.769 GHz: 2280/1504, 3819/2499
5-stage x1.0 N=32 1.573 GHz: 2934/1906, 4916/3182
4-stage N=48 2.359 GHz (reference): 2467/1615, 4133/2689
