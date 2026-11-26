#!/usr/bin/env python3
"""step79hv_cin.py - input capacitance of the Gm on v1p (what the SSPD's C1 node sees), Gm on (ckg = 1) and off (ckg = 0),
for the trim codes. AC: 1 V on v1p, C_in = Im(I(vp)) / (2 pi f) at 50-200 MHz. -> data/step79hv_cin.json"""
import os, re, json
import numpy as np
import sscp_hv as C
HERE = os.path.dirname(os.path.abspath(__file__))
CODES = {"10": (1, 1, 0, 0, 0), "00": (1, 1, 1, 0, 0), "01": (1, 1, 1, 1, 0), "11": (1, 1, 1, 1, 1)}
res = []
for code, en in CODES.items():
    for ckg in (3.3, 0.0):
        for corner in (("tt", 27), ("ss", 110), ("ff", -40)):
            net = C.head(corner=corner[0], temp=corner[1], en=en, ckg=ckg) + (
                "vp v1p 0 dc 1.66 ac 1\nvm v1m 0 1.66\n.control\nac lin 4 50e6 200e6\n"
                "wrdata a.txt imag(i(vp))\n.endc\n.end\n")
            _, d = C.run(net, ["a.txt"])
            z = d["a.txt"]; cin = float(np.median(np.abs(z[:, 1])/(2*np.pi*z[:, 0])))
            res.append(dict(code=code, ckg=ckg, corner=corner[0], temp=corner[1], cin=cin))
            print(f"code {code} ckg {ckg} {corner}: C_in {cin*1e15:.2f} fF", flush=True)
json.dump(res, open(os.path.join(HERE, "data", "step79hv_cin.json"), "w"), indent=1)
