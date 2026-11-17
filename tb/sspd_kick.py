#!/usr/bin/env python3
"""sspd_kick.py a.txt b.txt - post-processing of tb_sspd_kick (method M19).
a: clock generator running; b: refclk = 0 (no switching). Prints the clkp edge displacement (a - b), the spur estimate
at f_ref, the largest voltage difference on clkp, the f_ref component of the SSPD supply current and v1p - v1m just
after a sample (≈ 0 means the run sits at the lock point)."""
import sys
import numpy as np
fref, f0 = 50e6, 1.6e9
def load(fn):
    z = np.loadtxt(fn); return z[:, 0], z[:, 1], z[:, 3], z[:, 5], z[:, 7] - z[:, 9]
def edges(t, v):
    a = v - 0.9; k = np.where(np.sign(a[:-1]) != np.sign(a[1:]))[0]
    return t[k] - a[k]*(t[k + 1] - t[k])/(a[k + 1] - a[k])
ta, ca, ia, ka, va = load(sys.argv[1]); tb, cb, ib, kb, vb = load(sys.argv[2])
w0 = 60e-9; ea, eb = edges(ta, ca), edges(tb, cb); ea, eb = ea[ea > w0], eb[eb > w0]
n = min(len(ea), len(eb)); ea, eb = ea[:n], eb[:n]; m = ea < w0 + 4/fref
dt = (ea - eb)[m]; ph = 2*np.pi*f0*dt
a1 = 2*abs(np.mean(ph*np.exp(-2j*np.pi*fref*ea[m])))
mm = (ta > w0) & (ta < w0 + 4/fref)
I1 = 2*abs(np.trapezoid(ia[mm]*np.exp(-2j*np.pi*fref*ta[mm]), ta[mm])/(4/fref))
dv = np.max(abs(ca[mm] - np.interp(ta[mm], tb, cb)))
ts = edges(ta, ka); ts = ts[ts > w0]
print(f"clkp edge shift max {abs(dt).max()*1e15:.2f} fs, rms {dt.std()*1e15:.2f} fs; spur estimate {20*np.log10(a1/2 + 1e-30):.1f} dBc; "
      f"max |dv(clkp)| {dv*1e3:.3f} mV; SSPD current at f_ref {I1*1e6:.2f} uA; v1p - v1m after the sample "
      f"{np.interp(ts[0] + 0.15e-9, ta, va)*1e3:.0f} mV")
