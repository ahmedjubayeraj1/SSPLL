"""loop_type2.py - closed-form third-order charge-pump loop filter (moved here from learn/sspll_learn.py on 25 Nov 2026,
when the learning material moved to the private repo; the function is unchanged)."""
import numpy as np


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
