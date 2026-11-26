import refbuf as r, numpy as np, sys, json
from multiprocessing import Pool
def ev(kw):
    p = dict(r.D, **kw)
    try:
        o = r.op(p=p); f, S, fg, vi = r.input_noise(p=p)
        sw = np.sqrt(np.interp(3e8, f, S))*1e9; s1 = np.sqrt(np.interp(1e6, f, S))*1e9
        d50 = abs(np.interp(5e7, fg, vi))
        return kw, dict(vin=round(o["vin"], 3), idd=round(o["idd"]*1e6, 1), a1m=round(o["a1m"]), sw300M=round(sw, 2), s1M=round(s1, 2), s300k=round(np.sqrt(np.interp(3e5, f, S))*1e9/abs(np.interp(5e7, fg, vi)), 2), div50=round(d50, 3), fom=round(sw/d50, 2))
    except Exception as e:
        return kw, str(e)[:80]
N5 = ("nfet_g5v0d10v5", 10.0, 8, 0.5); P5 = ("pfet_g5v0d10v5", 10.0, 8, 0.5)
H4 = dict(PH=("pfet_g5v0d10v5", 2.0, 1, 4.0), PD=("pfet_g5v0d10v5", 2.0, 1, 4.0))
C = [
 dict(C_H=2e-12, P1BODY="src", MH=24, N1=("nfet_g5v0d10v5", 10.0, 8, 1.0), P1=("pfet_g5v0d10v5", 10.0, 8, 1.0), C_AC=4e-12, **H4),
 dict(C_H=2e-12, P1BODY="src", MH=24, N1=("nfet_g5v0d10v5", 10.0, 12, 1.0), P1=("pfet_g5v0d10v5", 10.0, 12, 1.0), C_AC=4e-12, **H4),
 dict(C_H=2e-12, P1BODY="src", MH=24, N1=("nfet_g5v0d10v5", 10.0, 6, 0.8), P1=("pfet_g5v0d10v5", 10.0, 8, 0.8), C_AC=4e-12, **H4),
 dict(C_H=2e-12, P1BODY="src", MH=24, N1=("nfet_g5v0d10v5", 10.0, 8, 1.0), P1=("pfet_g5v0d10v5", 10.0, 8, 1.0), C_AC=6e-12, **H4),
]
if __name__ == "__main__":
    with Pool(4) as pool:
        for kw, res in pool.map(ev, C): print(kw, res, flush=True)
