#!/usr/bin/env python3
"""step78_sim.py - SSPD characteristic over 17 conditions (method M18, beat run). Writes data/step78_char.json."""
import os, json
from multiprocessing import Pool
import sspd as S
HERE = os.path.dirname(os.path.abspath(__file__))
if __name__ == "__main__":
    with Pool(2) as pool:
        res = pool.map(S._char, S.COND)
    json.dump(res, open(os.path.join(HERE, "data", "step78_char.json"), "w"))
    for r in res:
        print(r["corner"], r["temp"], r["vdd"], r["fref"]/1e6, "A %.3f alpha %.3f cm %.3f P %.3f mW" % (r["A"], r["alpha"], r["cm"], r["power"]*1e3))
