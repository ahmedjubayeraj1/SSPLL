#!/usr/bin/env python3
"""step76_noise.py - receiver phase noise and its effect on the PLL (methods M14, M15, M9).
M14: pad-referred noise spectrum from .noise at the self-bias (crossing) point; M15: per-edge white jitter from the
transient-noise runs (data/step76_tnoise.json, edge times detrended with a 4th-order polynomial to remove the start-up drift of the
AC-coupling bias). Writes data/step76_noise.json."""
import os, json
import numpy as np
import refbuf as R, ref_budget as RB
HERE = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    f, Sg, fg, vi = R.input_noise()                     # gate-referred
    div = np.abs(np.interp(f, fg, vi.real) + 1j*np.interp(f, fg, vi.imag))
    Sp = Sg/div**2                                      # pad-referred
    tn = json.load(open(os.path.join(HERE, "data", "step76_tnoise.json")))
    Sw = tn["Sw"]                                       # pad-referred white level injected in M15
    Swg = float(np.interp(3e8, f, Sg))                  # the same plateau at the gate
    div50 = float(np.interp(5e7, f, div))
    sig = {}
    for r in tn["runs"]:
        if r["Sw"] > 0:
            x = np.array(r["dev"]); k = np.arange(len(x)); x = x - np.polyval(np.polyfit(k, x, 4), k)
            sig[r["vpp"]] = dict(abs=float(x.std()), per=float(np.diff(x).std()))
    fl = np.logspace(3, np.log10(25e6), 300)
    out = dict(f=f.tolist(), Sgate=Sg.tolist(), Spad=Sp.tolist(), Sw=Sw, Swg=Swg, div50=div50, sigma=sig, fL=fl.tolist(), L={}, sys={})
    for vpp, s in sorted(sig.items()):
        L = RB.L_rx(fl, f, Sg, Swg, s["abs"], vpp, div50)
        out["L"][str(vpp)] = L.tolist()
        out["sys"][str(vpp)] = RB.system(fl, L)
        print(vpp, "sigma_w %.3f ps" % (s["abs"]*1e12), "L(300k) at ref %.1f" % np.interp(3e5, fl, L),
              "floor %.1f" % L[-1], out["sys"][str(vpp)])
    # equivalent noise bandwidth of the white per-edge jitter at 1 V pp
    out["Beff"] = (sig[1.0]["abs"]*np.pi*50e6*1.0)**2/Sw
    print("B_eff %.3g MHz" % (out["Beff"]/1e6), "Sw pad %.3g nV/rtHz" % (np.sqrt(Sw)*1e9))
    json.dump(out, open(os.path.join(HERE, "data", "step76_noise.json"), "w"))
