#!/usr/bin/env python3
"""step75_noise.py - output-current noise of the complete CCO (PDK passives, all devices) by .noise (method M11),
put into the jitter budget (method M9). -> data/step75_noise.json"""
import json, os, re, subprocess, tempfile
import numpy as np
import cco, budget_link as bl
p = cco.D


def full_noise(c="tt", t=27, code=10, vring=1.45):
    net = (f"* noise\n.lib {cco.LIB} {c}\n.temp {t}\n{cco.full(p)}vdda VDDA 0 3.3\nvddd VDDD 0 1.8\nvddl VDDL 0 1.8\n"
           f"iib 0 ibias dc 5u ac 1\nvr vring 0 {vring}\nvt vtest 0 {vring}\nven pll_en 0 1.8\nvvt vtest_en 0 0\n"
           + "".join(f"vc{k} code{k} 0 {1.8 if code >> k & 1 else 0}\n" for k in range(5)) +
           "x1 VDDA VDDD VDDL 0 vr2 ibias vtest code0 code1 code2 code3 code4 pll_en vtest_en sspll_cco\n"
           "vm vr2 vring 0\nh1 o 0 vm 1\n.control\noption sparse\nnoise v(o) iib dec 10 1e3 1e8\nsetplot noise1\n"
           "wrdata noise.txt onoise_spectrum\n.endc\n.end\n")
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "r.sp"), "w").write(net)
        subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d, timeout=3000)
        z = np.loadtxt(os.path.join(d, "noise.txt"))
    return z[:, 0], z[:, 1]


if __name__ == "__main__":
    f, n = full_noise()
    r = bl.cco_jitter(f, n)
    at = lambda x: float(n[np.argmin(abs(f - x))])
    res = dict(f=f.tolist(), n=n.tolist(), at={str(x): at(x) for x in (1e4, 1e5, 3e5, 1e6, 1e7)},
               off=r[False], on=r[True])
    print({k: round(v*1e12, 2) for k, v in res["at"].items()}, "pA/rtHz")
    print("FFNC off: CCO %.3f ps, total %.3f ps, L300k %.1f | on: CCO %.3f, total %.3f, L300k %.1f" % (*r[False], *r[True]))
    json.dump(res, open(os.path.join(cco.HERE, "data", "step75_noise.json"), "w"), indent=1, default=float)
