#!/usr/bin/env python3
"""ncb_hv_sim.py - verification of the noise-cancellation block (NCB). -> data/ncb_hv_sim.json (one key per part)
A  delay and K_d = -dt/dvff against the gain code, at the lock-point vff of each condition (V_0 + G v_d,lock from the
   D2S verification); duty error, power. tt: all 16 codes; other conditions: codes 0, 5, 10, 15             (M31)
B  control path: vff -> nb / pd small-signal bandwidth, capacitance on vff                                (M28)
C  VDDA -> delay (vff fixed: the D2S refers it to VSSA)                                                    (M21)
D  noise of the bias path, referred to vff (.noise, option sparse) -> timing through K_d                  (M29)
E  mismatch Monte Carlo at tt, code 8: delay and K_d spread                                               (M30)
Coverage (calibration): required K_d = 1 / (G K_t) per condition, against what the codes reach -> best code and the
residual gain error. Usage: python3 ncb_hv_sim.py [A B C D E]"""
import os, json, sys
import numpy as np
from multiprocessing import Pool
import ncb_hv as N
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(HERE, "data", "ncb_hv_sim.json")
SSPD = {(r["corner"], r["temp"], r["vdda"]): r for r in
        json.load(open(os.path.join(ROOT, "design", "sspd", "data", "sspd_hv_sim.json")))["char"] if r["fref"] == 50e6}
P27 = os.path.join(HERE, "data", "ncb_hv_p27.json")    # SSPD and D2S at 27 C, nominal VDDA, for the four corner sections
if os.path.exists(P27):
    _p = json.load(open(P27))
    SSPD.update({tuple(r["key"]): r for r in _p["sspd"]})
D2S = {r["cond"]: r for r in json.load(open(os.path.join(ROOT, "design", "d2s", "data", "d2s_hv_sim.json")))["A"]}
if os.path.exists(P27):
    D2S.update({r["cond"]: r for r in _p["d2s"]})
P27C = [("ss", 27, 3.3), ("ff", 27, 3.3), ("ss_hh", 27, 3.3), ("ff_ll", 27, 3.3)]
CONDS = [("tt", 27, 3.3), ("tt", -40, 3.3), ("tt", 110, 3.3), ("ss_hh", 110, 2.97), ("ss_hh", -40, 2.97),
         ("ff_ll", -40, 3.63), ("ff_ll", 110, 3.63), ("ss", 110, 2.97), ("ff", -40, 3.63), ("sf", 27, 3.3), ("fs", 27, 3.3)] + P27C
# calibration happens once per die at 27 C, nominal supply; the code then stays while temperature and VDDA move
FAMILY = {("tt", 27, 3.3): [("tt", -40, 3.3), ("tt", 110, 3.3)], ("ss", 27, 3.3): [("ss", 110, 2.97)],
          ("ff", 27, 3.3): [("ff", -40, 3.63)], ("ss_hh", 27, 3.3): [("ss_hh", 110, 2.97), ("ss_hh", -40, 2.97)],
          ("ff_ll", 27, 3.3): [("ff_ll", -40, 3.63), ("ff_ll", 110, 3.63)], ("sf", 27, 3.3): [], ("fs", 27, 3.3): []}
PHI_LOCK = 0.10                      # rad from the SSPD crossing (Gm design: 74-129 mrad)


def tag(c):
    return f"{c[0]} {c[1]} °C, {c[2]} V"


def op(c):
    """Lock-point quantities of a condition: K_t (diff, V/s), G and V_0 of the D2S, v_d and vff at lock."""
    s = SSPD[c]; g = D2S[tag(c)]
    kt = 2*s["dvdt"]; vd = 2*s["A"]*PHI_LOCK
    return dict(kt=kt, G=g["G"], V0=g["V0"], vd=vd, vff=g["V0"] + g["G"]*vd, kreq=1/(g["G"]*kt))


def load():
    return json.load(open(DATA)) if os.path.exists(DATA) else {}


def save(key, val):
    d = load(); d[key] = val
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    json.dump(d, open(DATA, "w"), indent=1)


def part_a(args):
    c, code = args
    o = op(c)
    r = N.kd(N.D, c[0], c[1], c[2], o["vff"], code)
    return dict(cond=tag(c), code=code, vff=o["vff"], Kd=r["Kd"], td=r["td"], duty=r["duty"], P=r["P"])


def part_b(c):
    o = op(c); r = N.ac_ctrl(N.D, c[0], c[1], c[2], o["vff"], 8)
    return dict(cond=tag(c), f3_nb=r["f3_nb"], f3_pd=r["f3_pd"], cin=r["cin"])


def part_c(c):
    o = op(c)
    return dict(cond=tag(c), Ks=N.ks(N.D, c[0], c[1], c[2], o["vff"], 8))


def part_d(c):
    """Bias-path noise: .noise of v(nb) and v(pd) referred to vff (inoise). Delay noise = K_d x that voltage."""
    o = op(c)
    cl_ = "".join(f"vc{k} c{k} 0 {c[2] if (8 >> k) & 1 else 0}\nvcb{k} c{k}b 0 {0 if (8 >> k) & 1 else c[2]}\n" for k in range(4))
    out = dict(cond=tag(c))
    for node in ("nb", "pd"):
        net = (f"* ncb noise\n.lib {N.LIB} {c[0]}\n.temp {c[1]}\n{N.cells()}vdda VDDA 0 {c[2]}\nvin in 0 0\n{cl_}"
               f"vvf vff 0 dc {o['vff']} ac 1\nxn in out vff c0 c1 c2 c3 c0b c1b c2b c3b VDDA 0 sspll_ncb_hv\n"
               f".control\noption sparse\nnoise v(xn.{node}) vvf dec 20 1e3 1e9\nsetplot noise1\nwrdata n.txt inoise_spectrum\n"
               ".endc\n.end\n")
        _, d = N.run(net, ["n.txt"])
        z = d["n.txt"]; out["f"] = z[:, 0].tolist(); out["vin_" + node] = z[:, 1].tolist()
    return out


def part_e(seed):
    """Mismatch: both vff values in ONE ngspice session (alter + second tran), so the random draws made when the
    netlist is parsed are the same for the two runs."""
    o = op(CONDS[0])
    net = N.bench(N.D, "tt", 27, 3.3, o["vff"] - 0.02, 8).replace(".temp 27", ".temp 27\n.param mc_mm_switch=1")
    net = net.replace("wrdata w.txt v(inp) v(outp) i(vdda) ", "wrdata w.txt v(inp) v(outp) i(vdda) \n"
                      f"alter vvf = {o['vff'] + 0.02}\ntran 1e-12 1.25e-08\nwrdata w2.txt v(inp) v(outp) i(vdda) ")
    _, d = N.run(net, ["w.txt", "w2.txt"])
    res = []
    for f in ("w.txt", "w2.txt"):
        z = d[f]; t = z[:, 0]; ip, opp = z[:, 1], z[:, 3]
        T = 1.25e-9; t0 = 6*T; m = 1.65; dl = []
        for rising in (True, False):
            ti = N.K.xings(t, ip, m, rising); to = N.K.xings(t, opp, m, rising); ti = ti[ti > t0]
            dl.append(np.mean([to[to > x][0] - x for x in ti if len(to[to > x])]))
        res.append((float(np.mean(dl)), float(dl[0] - dl[1])))
    (a, da), (b, db) = res
    return dict(seed=seed, td=(a + b)/2, Kd=(a - b)/0.04, duty=(da + db)/2)


def p27():
    """SSPD beat characteristic (method M18) and D2S DC transfer at 27 C / nominal supply for ss, ff, ss_hh, ff_ll."""
    sys.path.insert(0, os.path.join(ROOT, "design", "sspd")); sys.path.insert(0, os.path.join(ROOT, "design", "d2s"))
    import sspd_hv as SS, d2s_hv as DS
    with Pool(2) as pool:
        ch = pool.starmap(SS.characteristic, [(SS.D, c[0], c[1], c[2], 1.8) for c in P27C])
    sp = [dict(key=list(c), A=r["A"], dvdt=r["dvdt"], cm=r["cm"], alpha=r["alpha"]) for c, r in zip(P27C, ch)]
    dd = []
    for c, r in zip(P27C, ch):
        t = DS.dc_transfer(DS.D, c[0], c[1], c[2], r["cm"])
        dd.append(dict(cond=tag(c), G=t["G"], V0=t["V0"]))
    json.dump(dict(sspd=sp, d2s=dd), open(P27, "w"), indent=1)
    return sp, dd


def calibration(A):
    """Code chosen at 27 C (nominal VDDA) per corner section; gain error at that code over temperature and VDDA."""
    kd = {}
    for c in CONDS:
        rows = sorted([r for r in A if r["cond"] == tag(c)], key=lambda r: r["code"])
        if rows:
            kd[c] = np.interp(np.arange(16), [r["code"] for r in rows], [r["Kd"] for r in rows])
    out = []
    for c27, fam in FAMILY.items():
        if c27 not in kd:
            continue
        err = kd[c27]/op(c27)["kreq"] - 1; b = int(np.argmin(abs(err)))
        row = dict(cond=tag(c27), code=b, err=float(err[b]), kreq=op(c27)["kreq"], drift=[])
        for c in fam:
            if c in kd:
                row["drift"].append(dict(cond=tag(c), err=float(kd[c][b]/op(c)["kreq"] - 1)))
        out.append(row)
    return out


def coverage(A):
    """Per condition: K_d(code) (interpolated from the codes simulated), required K_d, best code, residual error."""
    out = []
    for c in CONDS:
        rows = sorted([r for r in A if r["cond"] == tag(c)], key=lambda r: r["code"])
        if not rows:
            continue
        codes = np.array([r["code"] for r in rows]); kd = np.array([r["Kd"] for r in rows])
        allc = np.arange(16); kd16 = np.interp(allc, codes, kd)
        o = op(c); err = kd16/o["kreq"] - 1
        b = int(np.argmin(abs(err)))
        out.append(dict(cond=tag(c), kreq=o["kreq"], kmin=float(kd16.min()), kmax=float(kd16.max()), code=b,
                        err=float(err[b]), inside=bool(kd16.min() <= o["kreq"] <= kd16.max()), vff=o["vff"]))
    return out


if __name__ == "__main__":
    parts = sys.argv[1:] or list("ABCDE")
    if "P" in parts:
        p27()
    with Pool(2) as pool:
        if "A" in parts:
            old = [r for r in load().get("A", []) if r["cond"] in {tag(c) for c in CONDS}] if "keep" in parts else []
            done = {(r["cond"], r["code"]) for r in old}
            jobs = [(CONDS[0], k) for k in range(16)] + [(c, k) for c in CONDS[1:] for k in (0, 5, 10, 15)]
            jobs = [j for j in jobs if (tag(j[0]), j[1]) not in done]
            A = old + pool.map(part_a, jobs); save("A", A); save("coverage", coverage(A)); save("calibration", calibration(A))
        if "B" in parts:
            save("B", pool.map(part_b, CONDS))
        if "C" in parts:
            save("C", pool.map(part_c, [CONDS[0], CONDS[3], CONDS[5], CONDS[4], CONDS[6]]))
        if "D" in parts:
            save("D", pool.map(part_d, [CONDS[0], CONDS[3], CONDS[5]]))
        if "E" in parts:
            save("E", pool.map(part_e, range(1, 25)))
    d = load()
    for k in [q for q in parts if q in "ABCDE"] + (["coverage", "calibration"] if "A" in parts else []):
        for r in d.get(k, []):
            print(k, {q: (round(v, 15) if isinstance(v, float) else v) for q, v in r.items() if not isinstance(v, list)})
