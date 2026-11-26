#!/usr/bin/env python3
"""cco_hv_sim.py - verification of the 5 V CCO (step 75 redo; methods M10, M11, M13):
 A. DC: output current vs cco_code over 5 corners x VDDA 2.97/3.63 V x IBIAS 4/5/6 uA, ring node held at the voltage
    the ring has at that corner (ss 2.37 V, ff 1.60 V, others 1.89 V)                                   (M10)
 B. compliance: current vs ring node at the least headroom (code 31, IBIAS 4 uA, ss/110 C, VDDA 2.97 V) and at tt (M10)
 C. VDDA rejection: AC transfer VDDA -> output current, K_vdd = K_I x |dI/dVDDA|, at tt/ss/ff               (M11)
 D. disable: output current with pll_en = 0; VTEST injection gain                                         (M10)
 E. level shifter transient at VDDD 1.71 V / VDDA 3.63 V and 1.89 / 2.97 V, ss/110 C and ff/-40 C            (M13)
 F. code sweep 0..31 at tt (LSB size)
-> data/cco_hv_sim.json"""
import json, os, re
from multiprocessing import Pool
import numpy as np
import cco_hv as c
p = c.D
KI = {"tt": 0.62e12, "ss": 0.41e12, "ff": 0.85e12}
VR = {"tt": 1.89, "ss": 2.37, "ff": 1.60, "sf": 1.89, "fs": 1.89}


def opc(args):
    corner, t, vdda, ib, code, vr = args
    return c.op_current(p, corner, t, vdda, ib, code, vr)


if __name__ == "__main__":
    res = {}
    jobs = [(cn, t, v, ib, code, VR[cn]) for cn, t in (("tt", 27), ("ss", 110), ("ff", -40), ("sf", 27), ("fs", 27))
            for v in (2.97, 3.63) for ib in (4e-6, 5e-6, 6e-6) for code in (0, 10, 31)]
    jobs += [("tt", 27, 3.3, 5e-6, code, 1.89) for code in range(32)]
    with Pool(2) as pool:
        I = pool.map(opc, jobs)
    res["dc"] = [list(j) + [abs(i) if i is not None else None] for j, i in zip(jobs, I)]
    print("A done", flush=True)
    for ib in (4e-6, 5e-6, 6e-6):
        for code in (0, 10, 31):
            v = [r[-1] for r in res["dc"][:90] if r[3] == ib and r[4] == code]
            print(f"  IBIAS {ib*1e6:.0f} uA code {code:2d}: {min(v)*1e3:.3f}-{max(v)*1e3:.3f} mA", flush=True)
    vr = np.round(np.arange(0.0, 2.81, 0.1), 2)
    for tag, args in (("ss_worst", ("ss", 110, 2.97, 4e-6, 31)), ("tt_code10", ("tt", 27, 3.3, 5e-6, 10))):
        o = c.run(c.tb(p, *args[:2], vdda=args[2], ib=args[3], code=args[4], ctl="dc vr 0 2.8 0.1\nprint -vr#branch"))
        res[f"comp_{tag}"] = list(zip(vr.tolist(), [float(x) for x in re.findall(r"^\d+\s+\S+\s+(\S+)", o, re.M)]))
        print("B", tag, [(a, round(b*1e3, 3)) for a, b in res[f"comp_{tag}"][15:]], flush=True)
    res["psr"] = {}
    for cn, t, code, vdda in (("tt", 27, 10, 3.3), ("ss", 110, 31, 2.97), ("ff", -40, 0, 3.63)):
        o = c.run(c.tb(p, cn, t, vdda=vdda, code=code, vring=f"vr vring 0 {VR[cn]}", vdda_ac=True,
                       ctl="ac dec 5 1e2 1e8\nprint abs(vr#branch)"))
        res["psr"][cn] = [(float(f), float(v)) for f, v in re.findall(r"^\d+\s+(\S+)\s+(\S+)", o, re.M)]
        k1 = min(res["psr"][cn], key=lambda q: abs(q[0] - 1e6))[1]
        print(f"C {cn}: |dI/dVDDA| at 1 MHz {k1*1e6:.2f} uA/V -> K_vdd {k1*KI[cn]/1e6:.2f} MHz/V", flush=True)
    off = c.run(c.tb(p, "tt", 27, en=0, ctl="op\nprint -vr#branch"))
    res["off_current"] = float(re.search(r"vr#branch = (\S+)", off).group(1))
    inj = c.run(c.tb(p, "tt", 27, ctl="op\nprint -vr#branch", extra="").replace("vvt vtest_en 0 0", "vvt vtest_en 0 1.8")
                .replace("vt vtest 0 1.89", "vt vtest 0 1.90"))
    i0 = c.op_current(p, "tt", 27, 3.3, 5e-6, 10, 1.89)
    res["vtest"] = dict(i_with_10mV=float(re.search(r"vr#branch = (\S+)", inj).group(1)), i0=i0)
    print("D off", res["off_current"], "vtest +10 mV ->", (res["vtest"]["i_with_10mV"] - i0)*1e9, "nA", flush=True)

    def ls(args):
        cn, t, vdda, vddd = args
        net = (f"* ls\n.lib {c.LIB} {cn}\n.temp {t}\n{c.LS}vdda VDDA 0 {vdda}\nvddd VDDD 0 {vddd}\n"
               f"vin in 0 pulse(0 {vddd} 1n 0.2n 0.2n 20n 40n)\nx1 in out outb VDDD VDDA 0 0 sspll_ls_1v8_3v3\n"
               f"cl1 out 0 20f\ncl2 outb 0 20f\n.control\ntran 10p 80n\nmeas tran tr when v(out)={vdda/2} rise=1\n"
               f"meas tran tf when v(out)={vdda/2} fall=1\nmeas tran vh max v(out) from=10n to=20n\n"
               f"meas tran vl min v(out) from=30n to=40n\nprint tr tf vh vl\n.endc\n.end\n")
        o = c.run(net)
        return {k: float(v) for k, v in re.findall(r"^(tr|tf|vh|vl) = (\S+)", o, re.M)}
    cases = [("ss", 110, 3.63, 1.71), ("ff", -40, 3.63, 1.71), ("ss", 110, 2.97, 1.71), ("ff", -40, 2.97, 1.89)]
    with Pool(2) as pool:
        res["ls"] = {f"{a}_{b}_{v}_{d}": r for (a, b, v, d), r in zip(cases, pool.map(ls, cases))}
    print("E", res["ls"], flush=True)
    json.dump(res, open(os.path.join(c.HERE, "data", "cco_hv_sim.json"), "w"), indent=1)
