"""qa79.py - interview questions of step 79 (pulsed-Gm charge pump in 5 V devices, 19-20 Nov 2026).
Numbers come from design/sscp/data/step79hv_*.json; @@...@@ tokens are filled at build time (qa79())."""
import os, json
import numpy as np
_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "design", "sscp", "data")


def _num():
    J = lambda n: json.load(open(os.path.join(_D, n)))
    S, N, DET = J("step79hv_sim.json"), J("step79hv_noise.json"), J("step79hv_det.json")
    dc = S["dc"]; G0 = dc[0]["G"]; code = {r["code"]: r["G"] for r in dc if r["corner"] == "tt" and r["vc"] == 1.8}
    Gs = [r["G"] for r in dc if r["code"] == "00"]
    r = next(x for x in DET if x["corner"] == "tt" and x["vc"] == 1.8)
    a = np.array(r["rows"]); dd = (a[:, 0] - r["phi0"] + np.pi) % (2*np.pi) - np.pi; o = np.argsort(dd)
    dd, q = dd[o], a[o, 1]; m = np.abs(dd) < 0.6; P = np.poly1d(np.polyfit(dd[m], q[m], 3))
    z = min((x.real for x in P.roots if abs(x.imag) < 1e-9 and abs(x.real) < 0.6), key=abs)
    fn, n = np.array(S["noise"]["f"]), np.array(S["noise"]["n"])
    return dict(G=f"{G0*1e6:.2f}", Gmin=f"{min(Gs)*1e6:.1f}", Gmax=f"{max(Gs)*1e6:.1f}", beta=f"{N['beta']*1e6:.3f}",
                beff=f"{P.deriv()(z)/20e-9*1e6:.2f}", c10=f"{code['10']/G0:.2f}", c01=f"{code['01']/G0:.2f}",
                c11=f"{code['11']/G0:.2f}", berr=f"{max(abs(x['err']) for x in S['buffer'])*1e3:.1f}",
                n1M=f"{np.interp(1e6, fn, n)*1e12:.2f}", gm=f"{N['sys']['3.3_typ']['on']['terms']['pulsed-Gm charge pump']*1e3:.0f}",
                L1M=f"{N['L_gm_1M']:.1f}")


QA79_RAW = [
("What is a pulsed-Gm charge pump and why does a sub-sampling PLL use one?",
 "A transconductor that is connected to the loop filter only for a short pulse after each sample. The SSPD delivers a "
 "held voltage proportional to the phase error, not UP/DOWN pulses, so a PFD-style pump has nothing to steer. The Gm "
 "turns the held voltage into a current G·(v1p − v1m) for a time τ; averaged over the period that is a current "
 "proportional to the phase error, with no dead zone and no PFD."),
("Derive β = 2A·G·τ/T.",
 "The differential sample is v1p − v1m = 2A·φ (A per side, in V/rad). During the pulse the current into the filter is "
 "G·2Aφ; it flows for τ out of every period T, so the average is I = G·2Aφ·τ/T and β = I/φ = 2A·G·τ/T. With A = 0.811 "
 "V/rad, G = @@G@@ µS, τ = 528 ps, T = 20 ns: @@beta@@ µA/rad. In the whole detector the measured slope at lock is "
 "@@beff@@ µA/rad: the TG edges and the Gm's finite recovery take the rest."),
("Why did the first Gm, which looked right with DC inputs, fail with the real SSPD?",
 "It folded the left drain's current to the output through a shared pMOS mirror. At 6 µA a mirror of five 2/4 µm "
 "pMOS has its gate pole near 30 MHz. With DC inputs nothing moves, so the bench showed the right G. With the SSPD, v1 "
 "tracks the 800 MHz ring for half of every period and jumps to the held value 0.6 ns before the pulse; the mirror "
 "side was still averaging the tracking waveform. The whole-detector beat run measured β_eff = 0.17 µA/rad instead of "
 "0.79, with 3–4 fC per period at lock. The fix: no mirror; each drain gets its own pMOS current source."),
("Why is the pulse 2.4 ns after the sample and not right after it?",
 "During tracking v1 swings ±2 V at 800 MHz, far beyond the Gm's ±0.4 V linear range. The degeneration resistor and "
 "the source capacitance (about 100 kΩ × 12 fF) keep a memory of that swing for about a nanosecond and a half. A "
 "sweep of the pulse delay on the locked detector gave 4.4 fC per period at lock and 73 % of G·τ at 0.7 ns, 0.7 fC "
 "and 102 % at 3 ns. The clock generator got an RC delay (gap 1 = 2.36 ns at tt); the loop delay grows to 2.6 ns, "
 "which costs about 1.4° of phase margin."),
("What do the dump buffer and the 2 pF do, and what happens without them?",
 "Outside the pulse x is connected to vdump, which the buffer holds at vctl, so x is at the same voltage in both phases "
 "and no charge is shared when it switches. While v1 tracks, the Gm pushes an 800 MHz current into vdump; without the "
 "capacitor vdump swung ±90 mV and was up to 90 mV off vctl at the switch, i.e. a few fC into the filter every period. "
 "With 2 pF the DC error is ≤ @@berr@@ mV and the ripple about a millivolt."),
("Why does each drain have its own current source, and how is the offset between them kept small?",
 "So that nothing slow sits in the signal path: the output drain's current is I_P − I_N2, set by a pMOS source and "
 "the input transistor alone. The price is that the pMOS source must equal the tail current, or the difference flows "
 "into the filter. The pMOS gate line comes from a replica half-slice whose input sits at VDDA/2 (where the SSPD's "
 "common mode is), so its tail sees the same V_DS as the slices' tails; with a plain diode bias the offset was 33 mV, "
 "with the replica 7 mV at tt."),
("Why was the replica bias the largest noise source, and how was that fixed?",
 "The replica's noise moves pb, and pb drives every pMOS source of every enabled slice: its noise current is copied into "
 "x with the ratio of the slice current to the replica current. ngspice's noise summary put 74 % of the output noise "
 "there. A replica six times larger copies its noise six times weaker; longer current sources (pMOS L 4 µm, tails "
 "L 8 µm) have less gm, and so less noise, per microamp. Output noise fell from 2.98 to @@n1M@@ pA/√Hz at 1 MHz; "
 "the Gm now costs @@gm@@ fs in the system."),
("How do the trim codes work, and why slices rather than a current DAC?",
 "Five identical slices; the 1.8 V decoder enables 2, 3, 4 or 5 (codes 10, 00, 01, 11), giving G × @@c10@@ / 1 / "
 "@@c01@@ / @@c11@@. A ratio set by counting identical devices is exact to matching, does not move the bias point of the "
 "active slices and keeps the degeneration ratio (and so the PVT stability of G) the same at every code."),
("Why is the decoder in 1.8 V logic, with complementary enables?",
 "The device rule: analog blocks use 5 V devices on VDDA, digital logic 1.8 V devices on VDDD. The decoder sets the "
 "trim, so it sits on VDDD and drives the 5 V enables through four level shifters. Each slice switches nMOS tails "
 "(on with en = 1) and pMOS sources (on with enb = 0), so the level shifters' complementary outputs are used too."),
("How was G measured, and why is its sign negative in the testbench?",
 "With ckg held high, x is connected to vctl, which is an ideal source; a dc sweep of v1p − v1m and the slope at 0 V "
 "give G (@@Gmin@@–@@Gmax@@ µS over corners and V_cont). The bench writes −i(vvc), the current the source pushes out "
 "into the circuit; with v1p > v1m the Gm pushes current into vctl, so that slope is negative. The sign fixes which "
 "zero crossing of the SSPD characteristic is the stable lock point."),
]


def qa79():
    n = _num()
    out = []
    for q, a in QA79_RAW:
        for k, v in n.items():
            a = a.replace(f"@@{k}@@", v)
        out.append((q, a))
    return out
