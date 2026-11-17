#!/usr/bin/env python3
"""sspd_char.py w.txt [f_ref] [nb] - post-processing of tb_sspd_char (method M18).
Reads the wrdata file (columns: t, cks, t, ckg, t, ckh, t, v1p, t, v1m, t, v2p, t, v2m, t, i(vdd), t, clkp) and prints:
  A      phase-detector gain per side: (1/2) d(v1p - v1m)/dphi at the rising zero crossing (V/rad)
  alpha  hold memory: v2[k] = (1 - alpha) v1[k] + alpha v2[k-1] (least-squares fit), alpha = C2/(C1 + C2)
  CM     common mode of v1 at the sampling instant; power = 1.8 V x average SSPD supply current
How: every falling edge of cks is a sample; v1 is read in the middle of the Gm pulse (ckg high), v2 0.5 ns after the
hold pulse; the VCO phase of each sample is 2 pi f_vco t_sample (mod 2 pi) because the VCO squares start at t = 0."""
import sys
import numpy as np
z = np.loadtxt(sys.argv[1]); fref = float(sys.argv[2]) if len(sys.argv) > 2 else 50e6
nb = float(sys.argv[3]) if len(sys.argv) > 3 else 32
fv = (32 + 1/nb)*fref; T = 1/fref; t = z[:, 0]
cks, ckg, ckh, v1p, v1m, v2p, v2m, idd, clkp = (z[:, 2*i + 1] for i in range(9))
def x(v, rising):
    a = v - 0.9; k = np.where((a[:-1] < 0) & (a[1:] >= 0))[0] if rising else np.where((a[:-1] > 0) & (a[1:] <= 0))[0]
    return t[k] - a[k]*(t[k + 1] - t[k])/(a[k + 1] - a[k])
ts, gr, gf, hf = x(cks, False), x(ckg, True), x(ckg, False), x(ckh, False)
rows = []
for s in ts[ts > 2*T]:
    a, b, h = gr[gr > s], gf[gf > s], hf[hf > s]
    if len(a) and len(b) and len(h):
        tm = (a[0] + b[0])/2
        rows.append((s, (2*np.pi*fv*s) % (2*np.pi), np.interp(tm, t, v1p) - np.interp(tm, t, v1m),
                     np.interp(h[0] + 0.5e-9, t, v2p) - np.interp(h[0] + 0.5e-9, t, v2m),
                     (np.interp(tm, t, v1p) + np.interp(tm, t, v1m))/2))
r = np.array(rows); o = np.argsort(r[:, 1]); ph, v = r[o, 1], r[o, 2]
i0 = next(i for i in range(len(v)) if v[i - 1] < 0 <= v[i])
phi0 = (ph[i0 - 1] - v[i0 - 1]*((ph[i0] - ph[i0 - 1]) % (2*np.pi))/(v[i0] - v[i0 - 1])) % (2*np.pi)
d = (ph - phi0 + np.pi) % (2*np.pi) - np.pi; m = abs(d) < 0.35
A = np.polyfit(d[m], v[m], 1)[0]/2
X = np.vstack([r[1:, 2], r[:-1, 3]]).T; c, *_ = np.linalg.lstsq(X, r[1:, 3], rcond=None)
w = t > 2*T; P = -1.8*np.trapezoid(idd[w], t[w])/(t[w][-1] - t[w][0])
print(f"samples {len(r)}  A = {A:.3f} V/rad  lock phase {phi0:.2f} rad  alpha = {c[1]:.3f}  v1 range "
      f"{v.min():.3f}..{v.max():.3f} V  CM {r[:, 4].mean():.3f} V  power {P*1e3:.3f} mW")
