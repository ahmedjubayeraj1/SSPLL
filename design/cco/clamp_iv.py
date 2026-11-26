"""clamp_iv.py - clamp current vs ring-node voltage (difference of the CCO output with and without the clamp)."""
import re, sys, numpy as np
from multiprocessing import Pool
import cco
from step75_sim import tb
def iv(args):
    c, t, ib, k = args
    p = dict(cco.D, K_CL=k)
    net = tb(c, t, 3.3, ib, 31, ctl="dc vr 1.5 1.9 0.025\nprint -vr#branch").replace(cco.full(cco.D), cco.full(p))
    o = cco.run(net)
    return [float(x) for x in re.findall(r"^\d+\s+\S+\s+(\S+)", o, re.M)]
if __name__ == "__main__":
    V = np.arange(1.5, 1.9001, 0.025)
    for c, t in (("ss", 110), ("tt", 27), ("ff", -40)):
        with Pool(2) as pool:
            a0, a = pool.map(iv, [(c, t, 5e-6, 0), (c, t, 5e-6, 1)])
        ic = np.array(a0) - np.array(a)
        print(c, t, " ".join(f"{v:.3f}:{-i*1e3:.3f}" for v, i in zip(V, ic) if v >= 1.65))
