"""sspll_learn.py - small helpers shared by the Phase 1-6 learning notebooks.

Everything a notebook computes is written out in the notebook itself; this module only does the plumbing:
  * sweep(...)       one figure + a slider that re-draws all traces for each parameter value.
                     The slider is part of the plot (plotly), so it keeps working in the exported HTML page
                     with no Python running.
  * show(fig)        displays a plotly figure in Jupyter and in the HTML export.
  * bode(...)        magnitude/phase of a transfer function given as a callable H(s).
  * cp_pll_sim(...)  cycle-by-cycle (sampled-data) simulation of a charge-pump PLL (exact between edges).
Design numbers of the submitted proposal are collected in P.
"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from IPython.display import HTML, display

# ---- proposal numbers (final revision, 13 Nov 2026) -----------------------------------------------------
P = dict(fref=50e6, N=32, f0=1.6e9, fc=2.5e6, pm=50.0,
         jit_off_typ=2.3e-12, jit_on_typ=1.4e-12, power_on=9.0e-3,
         # assumptions used only for worked examples until Phase 7 measures the real values:
         Kvco_Hz_per_V=300e6,      # fine-tuning gain of the ring [Hz/V]  (assumed)
         A_samp=0.5,               # ring amplitude seen by the sampler [V] (assumed)
         C_samp=100e-15)           # sampling capacitor, as in Nagam & Kinget [F]
kB, T300 = 1.380649e-23, 300.0
kT = kB * T300
COLORS = ["#1d4ed8", "#c2410c", "#15803d", "#7c3aed", "#0f766e", "#b91c1c", "#a16207", "#475569"]
_FIRST = [True]


def show(fig, height=None):
    """Display a plotly figure; loads plotly.js from cdn.plot.ly once per notebook."""
    if height:
        fig.update_layout(height=height)
    fig.update_layout(template="plotly_white", margin=dict(l=60, r=20, t=60, b=50),
                      font=dict(size=12), legend=dict(font=dict(size=11)))
    html = fig.to_html(include_plotlyjs="cdn" if _FIRST[0] else False, full_html=False,
                       config={"displaylogo": False, "responsive": True})
    _FIRST[0] = False
    display(HTML(html))


def _round(a, maxpts):
    try:
        a = np.asarray(a, dtype=float)
    except (ValueError, TypeError):
        return list(a)                      # categorical axis
    if a.size > maxpts:
        a = a[np.unique(np.linspace(0, a.size - 1, maxpts).astype(int))]
    return [None if not np.isfinite(v) else float(f"{v:.4g}") for v in a]


def _clean(t, maxpts=800):
    t = dict(t)
    for k in ("x", "y"):
        if k in t:
            t[k] = _round(t[k], maxpts)
    return t


def sweep(values, fn, label, fmt="{:.3g}", active=None, rows=1, cols=1, subplot_titles=None,
          shared_xaxes=False, layout=None, height=430, vertical_spacing=0.12, maxpts=800):
    """Figure with a slider over `values`.
    fn(v) -> (traces, note): traces is a list of dicts for go.Scatter (x, y, name, mode, line, ... and optional
    'row'/'col'); every call must return the same number of traces in the same order. `note` is shown as the title.
    layout(fig) can set axis types, ranges and labels. Arrays are thinned to maxpts points and rounded to 4 digits
    so the exported page stays small."""
    frames = [fn(v) for v in values]
    frames = [([_clean(t, maxpts) for t in tr], note) for tr, note in frames]
    a = len(values) // 2 if active is None else active
    if rows * cols > 1:
        fig = make_subplots(rows=rows, cols=cols, subplot_titles=subplot_titles, shared_xaxes=shared_xaxes,
                            vertical_spacing=vertical_spacing)
    else:
        fig = go.Figure()
    for i, t in enumerate(frames[a][0]):
        t = dict(t); r, c = t.pop("row", None), t.pop("col", None)
        t.setdefault("line", {}); t["line"] = dict(t["line"]); t["line"].setdefault("color", COLORS[i % len(COLORS)])
        if r:
            fig.add_trace(go.Scatter(**t), row=r, col=c)
        else:
            fig.add_trace(go.Scatter(**t))
    ntr = len(frames[a][0])
    same_x = all(frames[k][0][i]["x"] == frames[a][0][i]["x"] for k in range(len(values)) for i in range(ntr))
    steps = []
    for v, (tr, note) in zip(values, frames):
        upd = {"y": [t["y"] for t in tr]}
        if not same_x:
            upd["x"] = [t["x"] for t in tr]
        steps.append(dict(method="update", label=fmt.format(v), args=[upd, {"title.text": note}]))
    fig.update_layout(title=dict(text=frames[a][1], font=dict(size=13)), height=height,
                      sliders=[dict(active=a, currentvalue=dict(prefix=label + " = "), steps=steps,
                                    pad=dict(t=45), len=0.95)])
    if layout:
        layout(fig)
    return fig


def bode(H, f, deg_unwrap=True):
    """|H| in dB and phase in degrees of H(s) evaluated at s = j*2*pi*f."""
    h = H(2j * np.pi * f)
    ph = np.angle(h)
    if deg_unwrap:
        ph = np.unwrap(ph)
    return 20 * np.log10(np.abs(h)), np.degrees(ph)


def crossover(f, mag_db):
    """First frequency where |G| falls through 0 dB (log interpolation)."""
    i = np.where((mag_db[:-1] > 0) & (mag_db[1:] <= 0))[0]
    if not len(i):
        return np.nan
    i = i[0]
    x0, x1, y0, y1 = np.log10(f[i]), np.log10(f[i + 1]), mag_db[i], mag_db[i + 1]
    return 10 ** (x0 + (0 - y0) * (x1 - x0) / (y1 - y0))


def qa_html(pairs):
    """Interview questions as collapsible items (used by the notebook builder)."""
    out = []
    for i, (q, a) in enumerate(pairs, 1):
        out.append(f"<details><summary><b>Q{i}.</b> {q}</summary>\n\n{a}\n\n</details>")
    return "\n".join(out)


# ---- charge-pump PLL, sampled-data simulation -------------------------------------------------------------
def _expm(M):
    from scipy.linalg import expm
    return expm(M)


def cp_pll_sim(Ip, R, C1, C2, Kvco, N, fref, ncyc=400, phi_step=0.0, f_step=0.0, theta0=0.0):
    """Charge-pump PLL with a PFD, simulated reference cycle by reference cycle.
    Filter: R in series with C1, C2 in parallel (third order). Kvco in rad/s/V. VCO excess phase theta (rad of VCO).
    At each reference edge the PFD sees the phase error (rad of reference)
        dphi = phi_in - theta/N        (phi_in = phi_step + 2*pi*f_step/... ramp for a frequency step)
    and the charge pump injects Ip*sign(dphi) for |dphi|/(2*pi)*Tref seconds. Between edges the filter and VCO
    evolve exactly (matrix exponential), so this captures the discrete-time effects the CT model ignores.
    Returns t (s), dphi (rad of ref, per cycle), vcont (V, per cycle)."""
    T = 1 / fref
    A = np.array([[-1 / (R * C1), 1 / (R * C1), 0.0],
                  [1 / (R * C2), -1 / (R * C2), 0.0],
                  [0.0, Kvco, 0.0]])
    B = np.array([0.0, 1 / C2, 0.0])

    def prop(dt, I):
        M = np.zeros((4, 4)); M[:3, :3] = A; M[:3, 3] = B * I
        E = _expm(M * dt)
        return E[:3, :3], E[:3, 3]
    x = np.array([0.0, 0.0, theta0])
    ts, errs, vcs = [], [], []
    for k in range(ncyc):
        phi_in = phi_step + 2 * np.pi * f_step * k * T     # f_step in Hz at the reference (ramp of input phase)
        d = phi_in - x[2] / N
        dc = float(np.clip(d, -2 * np.pi, 2 * np.pi))
        tw = abs(dc) / (2 * np.pi) * T
        if tw > 0:
            E, b = prop(tw, Ip * np.sign(dc)); x = E @ x + b
        E, b = prop(T - tw, 0.0); x = E @ x + b
        ts.append(k * T); errs.append(d); vcs.append(x[1])
    return np.array(ts), np.array(errs), np.array(vcs)


def loop_design_type2(fc, pm_deg, Ip, Kvco, N):
    """Closed-form third-order charge-pump loop filter for crossover fc and phase margin pm (zero and pole
    symmetric about fc). Kvco in rad/s/V. Returns dict R, C1, C2, fz, fp, b."""
    wc = 2 * np.pi * fc
    b = np.tan(np.radians(45 + pm_deg / 2))          # wp/wc = wc/wz = b, PM = atan(b) - atan(1/b)
    Ct = b * Ip * Kvco / (2 * np.pi * N * wc ** 2)   # |G(j wc)| = 1
    C2 = Ct / b ** 2
    C1 = Ct - C2
    R = b / (wc * C1)
    return dict(R=R, C1=C1, C2=C2, fz=1 / (2 * np.pi * R * C1), fp=1 / (2 * np.pi * R * C1 * C2 / (C1 + C2)), b=b)
