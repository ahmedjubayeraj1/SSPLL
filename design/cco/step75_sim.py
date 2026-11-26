#!/usr/bin/env python3
"""step75_sim.py - CCO verification (methods M10-M13 in docs/methods.md):
 A. DC: output current vs cco_code over corner x VDDA x IBIAS, load = ring node source at 1.45 V   (M10)
 B. compliance: output current vs ring-node voltage at max code, VDDA 2.97 V, ss/110 C              (M10)
 C. clamp: ring node vs code with the ring replaced by its measured I-V (step 74, ss/110 C)        (M12)
 D. supply rejection: AC transfer VDDA -> output current                                            (M11)
 E. level shifter: transient at VDDD 1.71 V / VDDA 3.63 V, ss/110 C and ff/-40 C                    (M13)
 Noise (.noise, M11) is in step75_noise.py. -> data/step75_sim.json"""
import json, os, re
from multiprocessing import Pool
import numpy as np
import cco
p = cco.D
HDR = lambda c, t: f".lib {cco.LIB} {c}\n.temp {t}\n" + cco.full(p)


def tb(c, t, vdda=3.3, ib=5e-6, code=10, vring="vr vring 0 1.45", en=1.8, vddd=1.8, ctl="", extra=""):
    bits = " ".join(f"vc{k} code{k} 0 {vddd if code >> k & 1 else 0}\n" for k in range(5))
    return (f"* step75 tb\n{HDR(c, t)}vdda VDDA 0 {vdda}\nvddd VDDD 0 {vddd}\nvddl VDDL 0 1.8\niib 0 ibias {ib}\n"
            f"{vring}\nvt vtest 0 1.45\nven pll_en 0 {en}\nvvt vtest_en 0 0\n{bits}{extra}"
            f"x1 VDDA VDDD VDDL 0 vring ibias vtest code0 code1 code2 code3 code4 pll_en vtest_en sspll_cco\n"
            f".control\n{ctl}\n.endc\n.end\n")


def op_current(args):
    c, t, vdda, ib, code = args
    out = cco.run(tb(c, t, vdda, ib, code, ctl="op\nprint -vr#branch"))
    m = re.search(r"vr#branch = (\S+)", out)
    return float(m.group(1)) if m else None


if __name__ == "__main__":
    res = {}
    # A
    jobs = [(c, t, v, ib, code) for c, t in (("tt", 27), ("ss", 110), ("ff", -40), ("sf", 27), ("fs", 27))
            for v in (2.97, 3.63) for ib in (4e-6, 5e-6, 6e-6) for code in (0, 10, 31)]
    jobs += [("tt", 27, 3.3, 5e-6, code) for code in range(32)]
    with Pool(2) as pool:
        I = pool.map(op_current, jobs)
    res["dc"] = [list(j) + [i] for j, i in zip(jobs, I)]
    print("A done", flush=True)
    # B compliance
    out = cco.run(tb("ss", 110, 2.97, 4e-6, 31, ctl="dc vr 0 2.4 0.1\nprint -vr#branch"))
    vals = [float(x) for x in re.findall(r"^\d+\s+\S+\s+(\S+)", out, re.M)]
    res["compliance"] = list(zip(np.arange(0, 2.41, 0.1).round(2).tolist(), vals))
    print("B", res["compliance"][-8:], flush=True)
    # C clamp: ring replaced by its measured I-V (ss/110 C), IBIAS 4 and 6 uA, VDDA 3.63 V
    import clamp_ring
    with Pool(2) as pool:
        res["clamp"] = pool.map(clamp_ring.one, [(ib, c) for ib in (4e-6, 6e-6) for c in (0, 8, 16, 20, 24, 28, 31)])
    print("C", res["clamp"], flush=True)
    # D supply rejection: VDDA ac 1 -> output current at 1 kHz - 10 MHz
    o = cco.run(tb("tt", 27, ctl="ac dec 5 1e3 1e7\nprint abs(vr#branch)").replace("vdda VDDA 0 3.3", "vdda VDDA 0 dc 3.3 ac 1"))
    res["psr"] = [(float(f), float(v)) for f, v in re.findall(r"^\d+\s+(\S+)\s+(\S+)", o, re.M)]
    print("D", res["psr"][::5], flush=True)
    # E level shifter transient
    def ls(args):
        c, t = args
        net = (f"* ls\n.lib {cco.LIB} {c}\n.temp {t}\n{cco.LS}vdda VDDA 0 3.63\nvddd VDDD 0 1.71\n"
               f"vin in 0 pulse(0 1.71 1n 0.2n 0.2n 20n 40n)\nx1 in out outb VDDD VDDA 0 sspll_ls_1v8_3v3\n"
               f"cl1 out 0 20f\ncl2 outb 0 20f\n.control\ntran 10p 80n\nmeas tran tr when v(out)=1.815 rise=1\n"
               f"meas tran tf when v(out)=1.815 fall=1\nmeas tran vh max v(out) from=10n to=20n\n"
               f"meas tran vl min v(out) from=30n to=40n\nprint tr tf vh vl\n.endc\n.end\n")
        o = cco.run(net)
        return {k: float(v) for k, v in re.findall(r"^(tr|tf|vh|vl) = (\S+)", o, re.M)}
    with Pool(2) as pool:
        res["ls"] = dict(zip(["ss_110", "ff_-40"], pool.map(ls, [("ss", 110), ("ff", -40)])))
    print("E", res["ls"], flush=True)
    json.dump(res, open(os.path.join(cco.HERE, "data", "step75_sim.json"), "w"), indent=1)
