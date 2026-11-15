"""clamp_ring.py - ring-node voltage vs cco_code with the ring replaced by its measured I-V (step 74, ss/110 C,
10 fF/node, extrapolated above 2.4 mA), worst IBIAS (6 uA) and VDDA (3.63 V). Also the current stolen by the clamp."""
import re, sys
from multiprocessing import Pool
import cco
from step75_sim import tb
# ring I-V at ss / 110 C (step 74 re-run with the PDK .spiceinit, 15 Nov): 0.9-2.4 mA simulated (M1), above 2.4 mA
# extrapolated with the measured slope 0.287 V/mA
RING = "Bring vring 0 I = pwl(v(vring), 0,0, 1.303,0.9m, 1.449,1.3m, 1.58,1.7m, 1.70,2.1m, 1.785,2.4m, 1.93,2.9m, 2.07,3.4m, 2.21,3.9m)"
def one(args):
    ib, code = args
    o = cco.run(tb("ss", 110, 3.63, ib, code, vring=RING, ctl="op\nprint v(vring)"))
    v = float(re.search(r"v\(vring\) = (\S+)", o).group(1))
    import numpy as np
    i = float(np.interp(v, [0, 1.38, 1.51, 1.627, 1.737, 1.817, 1.95, 2.2], [0, .9e-3, 1.3e-3, 1.7e-3, 2.1e-3, 2.4e-3, 2.9e-3, 3.9e-3]))
    return ib, code, v, i
if __name__ == "__main__":
    jobs = [(ib, c) for ib in (4e-6, 6e-6) for c in (0, 8, 16, 20, 24, 28, 31)] if "quick" not in sys.argv else [(4e-6, 31), (6e-6, 31)]
    with Pool(2) as pool:
        for ib, c, v, i in pool.map(one, jobs):
            print(f"IBIAS {ib*1e6:.0f} uA code {c:2d}: ring node {v:.3f} V, ring current {abs(i)*1e3:.3f} mA")
