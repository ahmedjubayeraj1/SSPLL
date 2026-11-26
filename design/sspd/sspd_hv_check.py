#!/usr/bin/env python3
"""sspd_hv_check.py - re-check of the SSPD at tt after the two later changes: C1 = 2.59 um with the final Gm's 27.6 fF
(same 42.7 fF node) and the clock-generator gap-1 delay (the Gm and hold pulses now come 2.4 ns after the sample).
Characteristic (M18) and kick-back (M19) at tt. -> data/sspd_hv_check.json"""
import os, json
from multiprocessing import Pool
import sspd_hv as S
HERE = os.path.dirname(os.path.abspath(__file__))
def job(k):
    if k == "char":
        r = S.characteristic(); r.pop("rows", None); return k, r
    r = S.kick(); r.pop("wave", None); return k, r
if __name__ == "__main__":
    with Pool(2) as p:
        res = dict(p.map(job, ["char", "kick"]))
    print(f"A {res['char']['A']:.3f} V/rad, alpha {res['char']['alpha']:.3f}, gain_v2 {res['char']['gain_v2']:.3f}, P {res['char']['power']*1e3:.3f} mW; "
          f"kick {res['kick']['dt_max']*1e15:.1f} fs, spur {res['kick']['spur_dbc']:.1f} dBc, I_fref {res['kick']['I_fref']*1e6:.2f} uA")
    json.dump(res, open(os.path.join(HERE, "data", "sspd_hv_check.json"), "w"), indent=1)
