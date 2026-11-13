"""pllmodel - phase-domain noise and jitter model for the SKY130 SSPLL + FFNC (Chipalooza #4).

One model, three variants (roadmap step 8):
  'type2'  classic charge-pump PLL: PFD + CP + /N in the loop. Detector noise is referred to the output x N^2.
  'sspll'  sub-sampling PLL: SSPD + CP, no divider in the loop. Detector noise is NOT multiplied by N^2.
  'ffnc'   sspll + feedforward noise cancellation (Nagam & Kinget, JSSC 2018).

Output-referred phase (all spectra are SSB L(f) in dBc/Hz, phase PSD = 2*10^(L/10) rad^2/Hz):
  phi_out = (1-Gc)(1-H) phi_vco + [H + Gc(1-H)] (N phi_ref + n_pd) + n_ncb
H = closed-loop transfer (type-II, 3rd order), Gc = cancellation path (0 when FFNC is off).
The sspll/ffnc equations are those of proposal/jitter_budget.py; TYP reproduces the proposal's 2.3 / 1.4 ps,
TYP_10NOV reproduces proposal/final_budget.txt (2.40 / 1.56 ps).
"""
import numpy as np

__all__ = ["Design", "freq_axis", "load_curve", "loop_H", "loop_G", "ffnc_Gc", "vco_L", "floor_L", "spectra",
           "jitter", "optimum_fc", "TYP", "PESS", "TYP_10NOV", "PESS_10NOV",
           "TYPE2_TYP", "TYPE2_PESS"]


def freq_axis(fmin=1e3, fmax=200e6, n=6000):
    """Log-spaced offset-frequency axis (Hz)."""
    return np.logspace(np.log10(fmin), np.log10(fmax), n)


class Design(dict):
    """Parameters of one design point. Keys (units):
    fref (Hz), N, fc (loop bandwidth, Hz), pm (phase margin, deg),
    vco1M (VCO L at 1 MHz, dBc/Hz), fc3 (VCO 1/f^3 corner, Hz),
    ref (reference floor, dBc/Hz at fref), ref_fc1 (its 1/f corner, Hz),
    pd (detector+CP floor referred to the OUTPUT, dBc/Hz) - used by sspll/ffnc,
    fom1hz (PFD+CP normalised floor, dBc/Hz at 1 Hz) - used by type2: pd = fom1hz + 10log fref + 20log N,
    pd_fc1 (detector 1/f corner, Hz), ncb (delay-line floor, dBc/Hz), ncb_fc1 (Hz), gerr (FFNC gain error, 0..1).
    Optional vco_f, vco_L (arrays): a simulated free-running VCO curve that replaces vco1M/fc3 (see load_curve)."""
    @property
    def f0(self):
        return self["N"] * self["fref"]

    def but(self, **kw):
        """Copy with some parameters changed: d.but(fc=1e6)."""
        d = Design(self); d.update(kw); return d


def load_curve(path, fcol=0, Lcol=1, delimiter=None):
    """Read an L(f) table (offset Hz, dBc/Hz) written by an ngspice/Spectre script or an instrument; returns (f, L).
    Lines starting with # or a header row are skipped."""
    rows = []
    for line in open(path):
        parts = line.replace(",", " ").split() if delimiter is None else line.split(delimiter)
        try:
            rows.append((float(parts[fcol]), float(parts[Lcol])))
        except (ValueError, IndexError):
            continue
    a = np.array(sorted(rows))
    return a[:, 0], a[:, 1]


def vco_L(f, L1M, fc3):
    """Free-running ring: -20 dB/dec (thermal), +10 dB/dec more below the 1/f^3 corner fc3."""
    return L1M + 20 * np.log10(1e6 / f) + 10 * np.log10(1 + fc3 / f)


def floor_L(f, Lfloor, fc1=0.0):
    """White floor with a 1/f corner fc1."""
    return Lfloor + 10 * np.log10(1 + fc1 / f)


def loop_G(f, fc, pm_deg=50):
    """Open-loop gain of a type-II, 3rd-order loop (two integrators, zero, pole),
    zero and pole placed symmetrically about the crossover fc so the phase margin is pm_deg."""
    s = 2j * np.pi * f
    pm = np.radians(pm_deg); b = (1 + np.sin(pm)) / np.cos(pm)
    wc = 2 * np.pi * fc; wz, wp = wc / b, wc * b
    G = (1 + s / wz) / (s ** 2 * (1 + s / wp))
    G0 = (1 + 1j * wc / wz) / ((1j * wc) ** 2 * (1 + 1j * wc / wp))
    return G / np.abs(G0)                      # |G(fc)| = 1 by construction


def loop_H(f, fc, pm_deg=50):
    """Closed-loop transfer H = G/(1+G): low-pass for reference/detector noise; 1-H is high-pass for the VCO."""
    G = loop_G(f, fc, pm_deg)
    return G / (1 + G)


def ffnc_Gc(f, fref, gain_err, on=True):
    """Cancellation path G_SSPD*G_NCB: sample-and-hold (sinc, half-period delay), pole giving -60 deg at fref/7.8
    (Nagam & Kinget), scaled by (1 - gain error)."""
    if not on:
        return np.zeros_like(f, dtype=complex)
    fp = (fref / 7.8) / np.tan(np.radians(60) - np.pi / 7.8)
    x = f / fref
    return (1 - gain_err) * np.sinc(x) * np.exp(-1j * np.pi * x) / (1 + 1j * f / fp)


def spectra(d, variant, f=None):
    """Output phase-noise contributions (rad^2/Hz, double-sided-to-single: 2*10^(L/10)) for variant
    'type2' | 'sspll' | 'ffnc'. Returns (f, dict name -> PSD)."""
    f = freq_axis() if f is None else f
    lin = lambda L: 2 * 10 ** (L / 10)
    H = loop_H(f, d["fc"], d.get("pm", 50))
    on = variant == "ffnc"
    Gc = ffnc_Gc(f, d["fref"], d.get("gerr", 0.0), on)
    T_vco = np.abs((1 - Gc) * (1 - H)) ** 2
    T_in = np.abs(H + Gc * (1 - H)) ** 2
    if variant == "type2":
        pd = d["fom1hz"] + 10 * np.log10(d["fref"]) + 20 * np.log10(d["N"])
    else:
        pd = d["pd"]
    if "vco_f" in d:   # simulated/measured free-running curve, interpolated on log f
        Lv = np.interp(np.log10(f), np.log10(d["vco_f"]), d["vco_L"])
    else:
        Lv = vco_L(f, d["vco1M"], d["fc3"])
    S = {"VCO": lin(Lv) * T_vco,
         "REF x N^2": lin(floor_L(f, d["ref"], d.get("ref_fc1", 0)) + 20 * np.log10(d["N"])) * T_in,
         "PD + CP": lin(floor_L(f, pd, d.get("pd_fc1", 0))) * T_in}
    if on:
        S["NCB"] = lin(floor_L(f, d["ncb"], d.get("ncb_fc1", 0))) * np.ones_like(f)
    return f, S


def jitter(d, variant, band=(10e3, 40e6), f=None):
    """RMS jitter (s) per contribution and 'TOTAL', integrated over band; also total L(f) in dBc/Hz."""
    f, S = spectra(d, variant, f)
    m = (f >= band[0]) & (f <= band[1])
    out = {k: np.sqrt(np.trapezoid(v[m], f[m])) / (2 * np.pi * d.f0) for k, v in S.items()}
    out["TOTAL"] = np.sqrt(sum(v ** 2 for v in out.values()))
    Ltot = 10 * np.log10(sum(S.values()) / 2)
    return out, f, Ltot


def optimum_fc(d, variant, fcs=None, **kw):
    """Loop bandwidth that minimises total jitter; returns (fc_opt, jitter_s, array of (fc, jitter))."""
    fcs = np.logspace(np.log10(100e3), np.log10(d["fref"] / 8), 60) if fcs is None else fcs
    js = np.array([jitter(d.but(fc=fc), variant, **kw)[0]["TOTAL"] for fc in fcs])
    i = int(np.argmin(js))
    return fcs[i], js[i], np.column_stack([fcs, js])


# --- design points ------------------------------------------------------------------------------
# Basis of the submitted proposal (final revision 13 Nov 2026, "Design basis" tab): ring phase noise from the
# ngspice ISF with model noise, -97.5 dBc/Hz at 1 MHz scaled to the 10 fF power basis (-0.85 dB), plus a CCO/supply
# allowance (+1 dB typ, +4 dB pess) and the ISF flicker corner (1.1 MHz typ, 2x pess). Gives 2.29 / 1.40 ps (spec 2.3 / 1.4).
# The ISF basis is pessimistic: Spectre transient noise puts the ring near -99 dBc/Hz (tools/cadence/pnoise/RESULT.md).
TYP = Design(fref=50e6, N=32, fc=2.5e6, pm=50, vco1M=-97.5 - 0.85 + 1, fc3=1.10e6, ref=-152, ref_fc1=30e3,
             pd=-130, ncb=-150, ncb_fc1=1e6, gerr=0.10)
PESS = TYP.but(vco1M=-97.5 - 0.85 + 4, fc3=2.2e6, ref=-148, ref_fc1=100e3, pd=-125, ncb=-146, ncb_fc1=3e6, gerr=0.30)
# Earlier basis (10 Nov, proposal/final_budget.py): ring scaled from -95.2 dBc/Hz at 1.769 GHz -> 2.40 / 1.56 ps.
_L1M = -95.2 + 10 * np.log10(1.6e9 / 1.769e9)
TYP_10NOV = TYP.but(vco1M=_L1M, fc3=200e3)
PESS_10NOV = PESS.but(vco1M=_L1M + 4, fc3=500e3)
# Type-II CP-PLL with the same ring, reference and N. PFD+CP normalised floor (Banerjee FoM_1Hz):
# -218 dBc/Hz typical for a well-designed CP in a 130 nm process, -212 pessimistic, CP flicker corner 100/300 kHz.
TYPE2_TYP = TYP.but(fom1hz=-218, pd_fc1=100e3)
TYPE2_PESS = PESS.but(fom1hz=-212, pd_fc1=300e3)
