# Ring phase noise - Spectre vs ngspice (12 Nov 2026)

Circuit: 5-stage x1.5 ring (previous design's `sspll_vco_dcell`, widths x1.5), ideal 1.08 mA feed, 5 fF/node,
vtune 0.9 V, tt 27 C, frozen sky130A models (v4). Spectre MMSIM 15.1 autonomous PSS + time-average Pnoise.
L(df) = S_out(f0+df)/P_c with P_c = |V1|^2/2, |V1(vop-vom)| = 1.5512 V. Parser: `parse_pnoise.py`.

| Offset | Spectre | ngspice ISF (model noise) | Difference |
|---|---|---|---|
| 100 kHz | -75.1 | -66.7 | 8.4 dB |
| 300 kHz | -88.9 | -80.4 | 8.5 dB |
| 1 MHz | -102.1 (thermal -107.0, flicker -103.8) | -94.3 (-97.5 / -97.1) | 7.8 dB |
| 3 MHz | -114.5 | -105.7 | 8.8 dB |
| 10 MHz | -125.9 | -117.0 | 8.9 dB |
| flicker = thermal | 2.41 MHz | 1.1 MHz | |
| f0 | 1.6021 GHz | 1.6022 GHz | 0.006% |

Open: the ~8 dB gap. Next check: single-device drain noise in Spectre vs ngspice (66.8 / 6.80 pA/rtHz nfet,
5.41 / 3.53 pA/rtHz pfet at 1 MHz / 1 GHz). Until resolved the proposal keeps the more pessimistic (ISF) numbers.
