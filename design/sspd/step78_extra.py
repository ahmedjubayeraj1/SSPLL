#!/usr/bin/env python3
"""step78_extra.py - kick-back / dummy-sampler test (method M19) and isolation-buffer jitter (method M17).
Writes data/step78_kick.json and data/step78_jitter.json."""
import os, sys, json
from multiprocessing import Pool
import sspd as S
HERE = os.path.dirname(os.path.abspath(__file__))
def job(k):
    if k == "kick":
        tt = json.load(open(os.path.join(HERE, "data", "step78_char.json")))[0]
        r = S.kick(phi0=tt["phi0"]); json.dump(r, open(os.path.join(HERE, "data", "step78_kick.json"), "w"))
        return {k_: v for k_, v in r.items() if k_ != "wave"}
    j = S.buf_jitter(); j["baseline"] = S.buf_jitter(S=j["S"], scale=1e-6)["sigma"]
    json.dump(j, open(os.path.join(HERE, "data", "step78_jitter.json"), "w")); return j
if __name__ == "__main__":
    with Pool(2) as p:
        for r in p.map(job, ["kick", "jit"]): print(r)
