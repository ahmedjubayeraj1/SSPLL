#!/usr/bin/env python3
"""edges.py file.txt [f_ref] [--fall] [--col N] - jitter from a wrdata waveform file (time, voltage) of a clock.
Finds the rising crossings of half the swing (linear interpolation), fits the ideal grid t_k = t0 + k T, removes a
4th-order polynomial (slow settling of bias points), and prints the rms deviation (absolute jitter), the period
jitter and the phase-noise floor L = (2 pi f sigma)^2 / f that white jitter of that size gives."""
import sys
import numpy as np
args = [a for a in sys.argv[1:] if not a.startswith("--")]
col = int(sys.argv[sys.argv.index("--col") + 1]) if "--col" in sys.argv else 1
if "--col" in sys.argv:
    args = [a for a in args if a != str(col)]
z = np.loadtxt(args[0]); t, v = z[:, 0], z[:, col]
f = float(args[1]) if len(args) > 1 else 50e6
if "--fall" in sys.argv:          # falling edges: flip the waveform
    v = -v
lev = (v.max() + v.min())/2; a = v - lev
k = np.where((a[:-1] < 0) & (a[1:] >= 0))[0]
te = t[k] - a[k]*(t[k + 1] - t[k])/(a[k + 1] - a[k])
n = np.arange(len(te)); dev = te - np.polyval(np.polyfit(n, te, 4), n)
s = dev.std()
print(f"edges {len(te)}, absolute jitter {s*1e12:.3f} ps, period jitter {np.diff(dev).std()*1e12:.3f} ps "
      f"(= sqrt(2) x absolute if white), floor L = {10*np.log10((2*np.pi*f*s)**2/f):.1f} dBc/Hz")
