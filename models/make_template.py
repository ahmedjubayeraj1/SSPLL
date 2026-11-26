#!/usr/bin/env python3
"""make_template.py - writes models/template.ipynb (roadmap step 9). Edit the cells here, not in the notebook,
so the template stays reproducible:  python3 models/make_template.py && jupyter nbconvert --execute --inplace models/template.ipynb"""
import os, nbformat as nbf
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
C = []
C.append(md("""# SSPLL phase-domain template

Template for every loop-level calculation in this project: loop gain, noise transfer, phase noise, jitter, and the
comparison of the three variants (Type-II CP-PLL, SSPLL, SSPLL + FFNC). Copy it for a new study
(`cp template.ipynb study_<topic>.ipynb`), change the design point, and replace model curves with simulated ones
as blocks get designed.

The model is `models/pllmodel` (plain Python, no hidden state). Every number in a cell comes from a function you
can read there. Output-referred phase:

$$\\varphi_{out} = (1-G_c)(1-H)\\,\\varphi_{vco} + \\left[H + G_c(1-H)\\right](N\\varphi_{ref} + n_{pd}) + n_{ncb}$$

$H$ is the closed-loop response, $G_c$ the cancellation path (0 when FFNC is off)."""))
C.append(code("""import os, sys
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.abspath("."))          # run from models/
import pllmodel as pm
plt.rcParams.update({"figure.figsize": (7.5, 4), "axes.grid": True, "grid.alpha": 0.4,
                     "figure.autolayout": True})
OUT = "out"; os.makedirs(OUT, exist_ok=True)"""))
C.append(md("""## 1. Design point
`pm.TYP` is the basis of the submitted proposal; `pm.PESS` the pessimistic corner. Change values with `.but(...)`,
e.g. `d = pm.TYP.but(fc=2e6)`. Units are in the `Design` docstring (`help(pm.Design)`)."""))
C.append(code("""d = pm.TYP            # <- change here
for k, v in d.items():
    print(f"{k:8s} {v}")
print(f"f0 = {d.f0/1e9:.3f} GHz")"""))
C.append(md("""## 2. The loop: why the VCO is high-passed and the reference low-passed
$G$ has two integrators (the charge pump integrating onto the filter capacitor, and the VCO integrating frequency into
phase), so $|G|$ is huge at low offsets. $H = G/(1+G) \\to 1$ there: the output follows the reference.
$1-H = 1/(1+G) \\to 0$: the loop removes the VCO's own wander. Above the crossover $f_c$ the loop gives up, so
$1-H \\to 1$ and the free-running VCO noise appears at the output."""))
C.append(code("""f = pm.freq_axis()
G = pm.loop_G(f, d["fc"], d["pm"]); H = G / (1 + G)
fig, ax = plt.subplots()
ax.loglog(f, abs(G), label="|G| open loop"); ax.loglog(f, abs(H), label="|H| (ref, detector)")
ax.loglog(f, abs(1 - H), label="|1-H| (VCO)")
ax.axvline(d["fc"], ls="--", c="0.5"); ax.set(ylim=(1e-3, 1e3), xlabel="offset (Hz)", ylabel="magnitude")
ax.legend(); fig.savefig(f"{OUT}/loop_transfer.png", dpi=130)
pk = 20*np.log10(abs(H).max()); print(f"closed-loop peaking {pk:.2f} dB at phase margin {d['pm']} deg")"""))
C.append(md("""## 3. Output phase noise and jitter of one variant
Jitter is $\\sigma_t = \\sqrt{\\int 2\\cdot10^{L(f)/10} df}\\,/\\,(2\\pi f_0)$ over 10 kHz-40 MHz (the spec's band)."""))
C.append(code("""variant = "ffnc"      # "type2" | "sspll" | "ffnc"
src = pm.TYPE2_TYP if variant == "type2" else d
j, f, Ltot = pm.jitter(src, variant)
_, S = pm.spectra(src, variant, f)
fig, ax = plt.subplots()
for k, v in S.items():
    ax.semilogx(f, 10*np.log10(v/2), lw=1, label=f"{k}: {j[k]*1e12:.2f} ps")
ax.semilogx(f, Ltot, "k", lw=2, label=f"total: {j['TOTAL']*1e12:.2f} ps")
ax.set(xlim=(1e3, 1e8), ylim=(-160, -80), xlabel="offset (Hz)", ylabel="L(f) (dBc/Hz)", title=variant)
ax.legend(fontsize=8); fig.savefig(f"{OUT}/L_{variant}.png", dpi=130)
at = lambda x: Ltot[np.argmin(abs(f - x))]
print(f"L(300 kHz) = {at(3e5):.1f} dBc/Hz, L(1 MHz) = {at(1e6):.1f} dBc/Hz")"""))
C.append(md("""## 4. Loop bandwidth: where is the optimum?
A wider loop suppresses more VCO noise but passes more reference and detector noise. The Type-II loop finds its
optimum early because its detector noise is multiplied by $N^2$. The model has no sampling delay, so it is
optimistic above about $f_{ref}/20$ (2.5 MHz here); treat the region beyond that as unreliable.

Notice what FFNC does: it makes the jitter almost independent of the loop bandwidth, because the cancellation
removes the VCO noise that a narrow loop would otherwise leave behind. That is why a ring-oscillator PLL with FFNC
does not need an extreme loop bandwidth."""))
C.append(code("""fcs = np.logspace(5, np.log10(d["fref"]/8), 40)
fig, ax = plt.subplots()
for name, v, dd in (("Type-II", "type2", pm.TYPE2_TYP), ("SSPLL", "sspll", d), ("SSPLL+FFNC", "ffnc", d)):
    fo, jo, tab = pm.optimum_fc(dd, v, fcs)
    ax.semilogx(tab[:, 0], tab[:, 1]*1e12, label=f"{name} (min {jo*1e12:.2f} ps at {fo/1e6:.1f} MHz)")
ax.axvline(d["fref"]/20, ls="--", c="0.5"); ax.text(d["fref"]/20, ax.get_ylim()[1]*0.95, " f_ref/20", fontsize=8)
ax.set(xlabel="loop bandwidth fc (Hz)", ylabel="rms jitter (ps)", ylim=(0, 6)); ax.legend(fontsize=8)
fig.savefig(f"{OUT}/fc_sweep.png", dpi=130)"""))
C.append(md("""## 5. FFNC gain error: how fine must the 4-bit `ncb_code` be?
Cancellation leaves a residue proportional to the gain error. In this model the reduction is fairly tolerant and
even peaks at a small *under*-gain (about 10-15 %): the cancellation path has a phase lag (sample-and-hold delay and
a pole), so near f_ref/8 a full-gain correction overshoots, and slightly less gain hurts less there.
The 4-bit code step must keep the calibrated error well inside the flat part; the real curve is set in Phase 6/7."""))
C.append(code("""gerrs = np.linspace(0, 0.6, 25)
off = pm.jitter(d, "sspll")[0]["TOTAL"]
red = [100*(1 - pm.jitter(d.but(gerr=g), "ffnc")[0]["TOTAL"]/off) for g in gerrs]
fig, ax = plt.subplots(); ax.plot(gerrs*100, red)
ax.axhline(20, ls="--", c="r"); ax.text(1, 21, "spec minimum 20 %", color="r", fontsize=8)
ax.set(xlabel="FFNC gain error (%)", ylabel="jitter reduction (%)"); fig.savefig(f"{OUT}/gerr.png", dpi=130)
print(f"reduction at 10% error: {red[np.argmin(abs(gerrs-0.10))]:.0f} %, at 30%: {red[np.argmin(abs(gerrs-0.30))]:.0f} %")"""))
C.append(md("""## 6. Replacing a model curve with a simulated one
When the VCO is designed, its simulated phase noise (ngspice ISF/trnoise script, or Spectre pnoise) is written as a
two-column table: offset in Hz, L in dBc/Hz. `pm.load_curve` reads it and `vco_f`/`vco_L` replace the model.
Here a table is written from the model itself, only to show the mechanics; point `path` at a real file."""))
C.append(code("""path = f"{OUT}/example_vco_curve.csv"
ff = np.logspace(3, 8, 51)
np.savetxt(path, np.column_stack([ff, pm.vco_L(ff, d["vco1M"], d["fc3"])]), delimiter=",", header="f_Hz,L_dBcHz")
vf, vL = pm.load_curve(path)                       # <- your simulated file
d_sim = d.but(vco_f=vf, vco_L=vL)
print(f"model curve {pm.jitter(d, 'ffnc')[0]['TOTAL']*1e12:.3f} ps, table {pm.jitter(d_sim, 'ffnc')[0]['TOTAL']*1e12:.3f} ps")"""))
C.append(md("""## 7. Your notes
What changed in this copy, why, and what result you took from it. Keep figures in `out/` (not committed); commit
the notebook only with cleared outputs or with small plots."""))
nb = nbf.v4.new_notebook(); nb["cells"] = C
nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.ipynb")
nbf.write(nb, p); print("->", p)
