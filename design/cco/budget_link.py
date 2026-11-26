"""budget_link.py - put a simulated CCO output-current noise spectrum into the step-72 jitter budget (method M9).
S_phi(f) = K_I^2 S_i(f) / f^2 (the current noise frequency-modulates the ring), shaped by |(1 - G_c)(1 - H)|^2."""
import os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in ("models", "learn", "design/budget"):
    sys.path.insert(0, os.path.join(ROOT, p))
import pllmodel as pm
import step72_budget as b

KI_TT = 0.847e12          # Hz/A, step 74 (tt, 27 C, 1.3-1.7 mA)
RING = (-98.71, 0.57e6)   # step-74 ring


def cco_jitter(fs, Si, corner="typ", KI=KI_TT):
    """Returns {(ffnc): (cco contribution ps, total ps)} with the step-74 ring and this CCO spectrum."""
    out = {}
    for on in (False, True):
        f, S = b.spectra(corner, on, over={"ring VCO core": RING})
        H = pm.loop_H(f, b.FC, b.PMDEG); Gc = pm.ffnc_Gc(f, b.FREF, b.CORNER[corner]["gerr"], on=on)
        Ti = np.abs((1 - Gc)*(1 - H))**2
        si = np.exp(np.interp(np.log(f), np.log(fs), np.log(Si**2)))      # A^2/Hz (Si given in A/rtHz)
        S["CCO current DAC + mirror"] = KI**2*si/f**2*Ti
        j, L = b.jitter(S, f, 1.6e9)
        out[on] = (j["CCO current DAC + mirror"]*1e12, j["TOTAL"]*1e12, float(L[np.argmin(abs(f - 3e5))]))
    return out
