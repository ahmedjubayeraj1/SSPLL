#!/usr/bin/env python3
"""fll_hv_sim.py - transistor-level characterisation of the FLL (python3 fll_hv_sim.py <part> ...).
  div    /16 with the down-shifter: highest input frequency that still divides by exactly 16, 5 corners (bisection),
         and supply current at 800 MHz
  cp     5 V charge pump: sink / source current vs V_cont, corners, IBIAS +-20 %; off-state leakage (locked) hot
  open   open loop, whole FLL: the ring runs 0.2 % fast so the divider edge sweeps through the reference edge
         (-3 .. +3 ns over 2 us): charge per period vs time offset (dead-zone transfer), lock_det and its hysteresis,
         fll_dir; 3 corners
Results: data/fll_hv_<part>.json"""
import os, sys, json
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fll_hv as F
COND = [("tt", 27, 1.8, 3.3), ("ss", 110, 1.71, 2.97), ("ff", -40, 1.89, 3.63), ("sf", 110, 1.71, 2.97),
        ("fs", -40, 1.89, 3.63)]


def fmax(c):
    corner, temp, vddd, vdda = c
    lo, hi = 1.0e9, 6.0e9
    if F.div_test(hi, corner, temp, vddd, vdda)[0] == 16:
        return dict(corner=corner, temp=temp, vddd=vddd, fmax=hi, note="> upper bound")
    for _ in range(6):
        mid = 0.5*(lo + hi)
        r = F.div_test(mid, corner, temp, vddd, vdda)[0]
        lo, hi = (mid, hi) if abs(r - 16) < 1e-3 else (lo, mid)
    i800 = F.div_test(800e6, corner, temp, vddd, vdda)[2]
    return dict(corner=corner, temp=temp, vddd=vddd, vdda=vdda, fmax=lo, i_vddd_800=i800)


def part_div():
    with Pool(2) as P:
        rows = P.map(fmax, COND)
    for r in rows:
        print(f"  {r['corner']} {r['temp']} C VDDD {r['vddd']}: f_max {r['fmax']/1e9:.2f} GHz, I(VDDD) at 800 MHz "
              f"{(r.get('i_vddd_800') or 0)*1e6:.0f} uA", flush=True)
    return rows


def part_cp():
    import re
    rows = []
    for corner, temp, _, vdda in COND[:3]:
        for ibs in (0.8, 1.0, 1.2):
            r = dict(corner=corner, temp=temp, vdda=vdda, ib=5e-6*ibs, v=[], isink=[], isrc=[])
            for vc in (0.3, 0.6, 1.0, 1.3, 1.8, 2.3, 2.8, 3.0):
                if vc > vdda - 0.2:
                    continue
                net = (f"* cp dc\n.lib {F.LIB} {corner}\n.temp {temp}\n{F.cp()}vdda VDDA 0 {vdda}\niib VDDA ib {5e-6*ibs}\n"
                       f"vvc vctl 0 {vc}\nvu up5 0 {vdda}\nvub up5b 0 0\nvd dn5 0 0\nvdb dn5b 0 {vdda}\nva act5b 0 0\n"
                       "x1 vctl ib up5 up5b dn5 dn5b act5b VDDA 0 sspll_fll_cp\n.control\nop\nlet a = -vvc#branch\nprint a\n"
                       f"alter vu dc=0\nalter vub dc={vdda}\nalter vd dc={vdda}\nalter vdb dc=0\nop\nlet b = -vvc#branch\nprint b\n"
                       ".endc\n.end\n")
                out, _ = F.run(net)
                a, b = [float(x) for x in re.findall(r"^[ab] = (\S+)", out, re.M)]
                r["v"].append(vc); r["isink"].append(a); r["isrc"].append(-b)
            rows.append(r)
            i18 = r["v"].index(1.8)
            print(f"  {corner} {temp} C IBIAS x{ibs}: sink {r['isink'][i18]*1e6:.1f} uA, source {r['isrc'][i18]*1e6:.1f} uA at 1.8 V; "
                  f"sink {min(r['isink'])*1e6:.1f}-{max(r['isink'])*1e6:.1f}, source {min(r['isrc'])*1e6:.1f}-{max(r['isrc'])*1e6:.1f} uA "
                  f"over {r['v'][0]}-{r['v'][-1]} V", flush=True)
    leak = []
    for corner in ("tt", "ff", "ss"):
        for vc in (1.3, 2.3):
            net = (f"* cp off\n.lib {F.LIB} {corner}\n.temp 110\n{F.cp()}vdda VDDA 0 3.3\niib VDDA ib 5u\nvvc vctl 0 {vc}\n"
                   "vu up5 0 0\nvub up5b 0 3.3\nvd dn5 0 3.3\nvdb dn5b 0 3.3\nva act5b 0 3.3\n"
                   "x1 vctl ib up5 up5b dn5 dn5b act5b VDDA 0 sspll_fll_cp\n.control\nop\nlet a = -vvc#branch\nprint a\n.endc\n.end\n")
            out, _ = F.run(net)
            leak.append(dict(corner=corner, vc=vc, i=float(re.findall(r"^a = (\S+)", out, re.M)[0])))
    print("  off-state current into vctl at 110 C (A):", [(x["corner"], x["vc"], f"{x['i']:.2e}") for x in leak])
    return dict(rows=rows, leak=leak)


def _open(c, extra=".option method=gear\n"):
    corner, temp, vddd, vdda = c
    eps = 2.5e-3                       # ring 0.25 % fast: the divider edge moves 50 ps earlier every period
    path = os.path.join(HERE, "data", f"fll_hv_open_{corner}.json")
    if os.path.exists(path):
        return json.load(open(path))
    try:
        w = F.bench_open(corner, temp, vddd, vdda, eps=eps, t0v=11.23e-9, tstop=1.8e-6, tstep=10e-12, extra=extra)
    except Exception as e:
        print(f"  {corner}: FAILED {e}", flush=True)
        return dict(corner=corner, temp=temp, failed=str(e)[-600:], rows=[])
    t = w["t"]
    tr = F.xings(t, w["ref"], vddd/2)
    rows = []
    for k in range(len(tr) - 1):
        a, b = tr[k] - 10e-9, tr[k] + 10e-9        # one period centred on the reference edge
        if a < 50e-9 or b > t[-1]:
            continue
        m = (t >= a) & (t < b)
        q = float(np.trapezoid(w["icp"][m], t[m]))
        hi = lambda v: float(np.trapezoid((v[m] > vddd/2).astype(float), t[m]))
        wu, wd = hi(w["up"]), hi(w["dn"])           # PFD pulse widths (before the dead zone)
        i_ = np.argmin(abs(t - (tr[k] + 9e-9)))
        rows.append(dict(t=float(tr[k]), dt=wu - wd, wu=wu, wd=wd, q=q, lock=float(w["lock"][i_] > vddd/2),
                         dir=float(w["dir"][i_] > vddd/2)))
    pw = dict(idda=float(np.mean(w["idda"][t > 100e-9])), iddd=float(np.mean(w["iddd"][t > 100e-9])))
    r = dict(corner=corner, temp=temp, vddd=vddd, vdda=vdda, eps=eps, rows=rows, power=pw)
    json.dump(r, open(path, "w"), default=float)
    return r


def part_open():
    with Pool(2) as P:
        res = P.map(_open, COND[:3])
    for r in res:
        a = [x for x in r["rows"] if x["dt"] is not None]
        lk = [x for x in a if x["lock"] > 0.9]
        print(f"  {r['corner']}: {len(a)} periods, dt {a[0]['dt']*1e9 if a else 0:.2f} -> {a[-1]['dt']*1e9 if a else 0:.2f} ns; "
              f"lock_det high for dt {min(x['dt'] for x in lk)*1e9 if lk else 0:.2f} .. {max(x['dt'] for x in lk)*1e9 if lk else 0:.2f} ns",
              flush=True)
    return res


if __name__ == "__main__":
    for part in sys.argv[1:]:
        r = globals()["part_" + part]()
        json.dump(r, open(os.path.join(HERE, "data", f"fll_hv_{part}.json"), "w"), indent=1, default=float)
