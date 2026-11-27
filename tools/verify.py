#!/usr/bin/env python3
"""verify.py - check the design on your own computer without writing any code.

  python3 tools/verify.py                  this help
  python3 tools/verify.py setup            are ngspice, xschem, netgen and the PDK where the scripts expect them?
  python3 tools/verify.py list             the blocks, what each quick check measures, and how long it takes
  python3 tools/verify.py ncb              quick check of one block at tt, 27 C, nominal supplies (1-3 minutes)
  python3 tools/verify.py all              quick check of every block, one after the other (about 12 minutes)
  python3 tools/verify.py lvs              schematic-vs-netlist check (LVS) of every cell
  python3 tools/verify.py full ncb         the block's complete verification (all corners, Monte Carlo): hours

Every quick check runs the same functions the design used, compares each number with the value stored in the
repository (design/<block>/data/*.json) and prints PASS when they agree within the tolerance shown.

Results are written to results/ (open them in Excel or LibreOffice):
  results/verify_<block>_<date>.csv     this run: quantity, your value, repository value, difference, PASS / FAIL
  results/verify_history.csv            one line per quantity per run, so you can see every run you ever made
Every ngspice netlist the check runs is kept in results/netlists/<block>/ with the PDK's .spiceinit, so you can open it
yourself:  cd results/netlists/ncb && ngspice r_01.spice   then, at the ngspice prompt:  plot v(inp) v(outp)"""
import os, sys, json, csv, time, shutil, subprocess, datetime, importlib

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
for f in ("design/clkgen", "design/cco", "design/vco", "design/refbuf", "design/sspd", "design/sscp", "design/fll",
          "design/d2s", "design/ncb", "design/loop", "design/budget", "tools", "models", "learn"):
    sys.path.insert(0, os.path.join(ROOT, f))
RES = os.path.join(ROOT, "results")
DATA = lambda blk, f: json.load(open(os.path.join(ROOT, "design", blk, "data", f)))

# ------------------------------------------------------------------ keep every netlist that is simulated
_orig_run = subprocess.run
_keep = {"dir": None, "n": 0}


def _run_and_keep(cmd, *a, **kw):
    if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == "ngspice" and _keep["dir"]:
        src = os.path.join(kw.get("cwd") or ".", cmd[-1])
        if os.path.exists(src):
            _keep["n"] += 1
            shutil.copy(src, os.path.join(_keep["dir"], f"r_{_keep['n']:02d}.spice"))
    return _orig_run(cmd, *a, **kw)


subprocess.run = _run_and_keep


def row(name, value, ref, unit, scale=1.0, tol=0.02, absol=None):
    """One compared quantity. tol = relative tolerance; absol = absolute tolerance (for values near zero)."""
    if value is None:
        return dict(quantity=name, unit=unit, yours=None, repo=ref*scale if ref is not None else None, diff="", ok=False)
    v, r = value*scale, (ref*scale if ref is not None else None)
    if r is None:
        return dict(quantity=name, unit=unit, yours=v, repo=None, diff="", ok=True)
    d = v - r
    ok = abs(d) <= (absol if absol is not None else tol*abs(r))
    rel = f"{d/r*100:+.2f} %" if r else f"{d:+.3g}"
    return dict(quantity=name, unit=unit, yours=v, repo=r, diff=rel, ok=ok)


# ------------------------------------------------------------------ the quick checks, one per block
def chk_cco():
    import cco_hv as C
    ref = [r for r in DATA("cco", "cco_hv_sim.json")["dc"] if r[:6] == ["tt", 27, 3.3, 5e-6, 10, 1.89]][0][6]
    i = C.op_current(C.D, "tt", 27, 3.3, 5e-6, 10, 1.89)
    return [row("ring feed current, code 10, ring node 1.89 V", abs(i), abs(ref), "mA", 1e3)]


def chk_vco():
    import vco_hv as V
    from vco_hv_point import VARIANTS
    ref = [x for x in DATA("vco", "vco_hv_char_hl6.json")["f_vs_I"]["tt_27"] if abs(x[0] - 1e-3) < 1e-9][0]
    r = V.run_full(V.netlist(VARIANTS["hl6"], corner="tt", temp=27, I=1e-3, cpar=10e-15, vdda=3.3))
    return [row("ring frequency at 1.0 mA feed", r.get("f"), ref[1], "MHz", 1e-6),
            row("ring node voltage (average)", r.get("vdd_avg"), ref[2], "V", absol=0.01)]


def chk_refbuf():
    import refbuf_hv as R
    ref = [x for x in DATA("refbuf", "refbuf_hv_sim.json")["tran"] if x["corner"] == "tt" and x["temp"] == 27
           and x["vdda"] == 3.3 and x["vddd"] == 1.8 and x["wave"] == "square"][0]
    r = R.tran("tt", 27, 3.3, 1.8, vpp=3.3, wave="square")
    return [row("delay pad -> refclk (3.3 V square in)", r["delay"], ref["delay"], "ns", 1e9, tol=0.05),
            row("duty cycle of refclk", r["duty"], ref["duty"], "%", 100, absol=1.0),
            row("power", r["power"], ref["power"], "mW", 1e3, tol=0.05)]


def chk_clkgen():
    import clkgen_hv as K
    ref = [x for x in DATA("clkgen", "clkgen_hv_sim.json")["timing"] if x["corner"] == "tt" and x["temp"] == 27
           and x["vdda"] == 3.3 and x["vddd"] == 1.8][0]
    r = K.tran("tt", 27, 1.8, 3.3)
    return [row("sampling edge delay t_s", r["t_s"], ref["t_s"], "ps", 1e12, tol=0.03),
            row("Gm pulse width tau", r["tau"], ref["tau"], "ps", 1e12, tol=0.03),
            row("gap 2 (hold -> next sample)", r["gap2"], ref["gap2"], "ps", 1e12, tol=0.05),
            row("power", r["power"], ref["power"], "mW", 1e3, tol=0.05)]


def chk_sspd():
    import sspd_hv as S
    ref = [x for x in DATA("sspd", "sspd_hv_sim.json")["char"] if x["corner"] == "tt" and x["temp"] == 27
           and x["vdda"] == 3.3 and x["fref"] == 50e6][0]
    r = S.characteristic(corner="tt", temp=27, vdda=3.3)
    return [row("detector gain A per side", r["A"], ref["A"], "V/rad", tol=0.03),
            row("hold memory alpha", r["alpha"], ref["alpha"], "", absol=0.01),
            row("sampled common mode", r["cm"], ref["cm"], "V", absol=0.01),
            row("power", r["power"], ref["power"], "mW", 1e3, tol=0.05)]


def chk_sscp():
    import sscp_hv as C
    ref = [x for x in DATA("sscp", "sscp_hv_sim.json")["dc"] if x["corner"] == "tt" and x["vc"] == 1.8 and x["code"] == "00"][0]
    r = C.dc_transfer(corner="tt", temp=27, vdda=3.3, vc=1.8, en=(1, 1, 1, 0, 0), cm=3.3*0.503)
    return [row("transconductance G (code 00, V_cont 1.8 V)", abs(r["G"]), ref["G"], "uS", 1e6, tol=0.03),
            row("input offset", r["v_os"], ref["v_os"], "mV", 1e3, absol=1.0)]


def chk_fll():
    import fll_hv as F
    ref = [x for x in DATA("fll", "fll_hv_div.json") if x["corner"] == "tt"][0]
    ratio, _, i = F.div_test(800e6)
    return [row("divide ratio at 800 MHz", ratio, 16, "", absol=0.01),
            row("divider supply current at 800 MHz", i, ref["i_vddd_800"], "uA", 1e6, tol=0.05)]


def chk_loop():
    import lf_hv as L, lf_hv_sim as LS
    ref = [x for x in DATA("loop", "lf_hv_corners.json") if x["corner"] == "tt" and x["temp"] == 27 and x["vc"] == 1.8][0]
    S = DATA("loop", "lf_hv_size.json")               # the drawn filter: R1 and C2 as sized by lf_hv_sim.py part 'size'
    p = dict(L.D, R1=tuple(S["R1"]), C2=tuple(S["C2"]))
    f, Y = LS.ac(p, "tt", 27, (1.8,))[1.8]
    r = LS.fit(f, Y)
    return [row("R1 (fitted from AC)", r["R"], ref["R"], "kOhm", 1e-3),
            row("C1", r["C1"], ref["C1"], "pF", 1e12),
            row("C2", r["C2"], ref["C2"], "pF", 1e12)]


def chk_d2s():
    import d2s_hv as A
    ref = [x for x in DATA("d2s", "d2s_hv_sim.json")["A"] if x["cond"].startswith("tt 27") and "3.3" in x["cond"]][0]
    r = A.dc_transfer(corner="tt", temp=27, vdda=3.3, cm=ref["cm"])
    return [row("gain G", r["G"], ref["G"], "V/V", tol=0.02),
            row("output at zero input V0", r["V0"], ref["V0"], "V", absol=0.01)]


def chk_ncb():
    import ncb_hv as N, ncb_hv_sim as S
    ref = [x for x in DATA("ncb", "ncb_hv_sim.json")["A"] if x["cond"].startswith("tt 27") and x["code"] == 8][0]
    r = N.kd(corner="tt", temp=27, vdda=3.3, vff=ref["vff"], code=8)
    return [row("delay at code 8", r["td"], ref["td"], "ps", 1e12, tol=0.01),
            row("delay gain K_d at code 8", r["Kd"], ref["Kd"], "ps/V", 1e12, tol=0.03),
            row("duty-cycle error", r["duty"], ref["duty"], "ps", 1e12, absol=1.5e-12),
            row("power", r["P"], ref["P"], "mW", 1e3, tol=0.03)]


BLOCKS = {  # name: (check, what it measures, minutes, full-verification command)
    "cco": (chk_cco, "ring feed current at code 10 (DC operating point)", 0.5, "design/cco/cco_hv_sim.py"),
    "vco": (chk_vco, "ring frequency and ring voltage at 1 mA (transient)", 1, "design/vco/vco_hv_char.py"),
    "refbuf": (chk_refbuf, "reference receiver delay, duty cycle, power (transient)", 1.5, "design/refbuf/refbuf_hv_sim.py"),
    "clkgen": (chk_clkgen, "clock generator timing: t_s, tau, gap 2, power (transient)", 1.5, "design/clkgen/clkgen_hv_sim.py"),
    "sspd": (chk_sspd, "detector gain, hold memory, common mode, power (beat transient)", 6, "design/sspd/sspd_hv_sim.py"),
    "sscp": (chk_sscp, "charge-pump transconductance and offset (DC sweep)", 0.5, "design/sscp/sscp_hv_sim.py"),
    "fll": (chk_fll, "divide-by-16 at 800 MHz and its supply current (transient)", 1, "design/fll/fll_hv_sim.py"),
    "loop": (chk_loop, "loop filter R1, C1, C2 from an AC run", 0.5, "design/loop/lf_hv_sim.py"),
    "d2s": (chk_d2s, "diff-to-SE amplifier gain and output level (DC sweep)", 0.5, "design/d2s/d2s_hv_sim.py"),
    "ncb": (chk_ncb, "noise-cancellation block delay, delay gain, duty, power (2 transients)", 1, "design/ncb/ncb_hv_sim.py"),
}


def fmt(x):
    if x is None:
        return "-"
    return f"{x:.4g}" if isinstance(x, float) else str(x)


def quick(blk):
    fn, what, mins, _ = BLOCKS[blk]
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    _keep["dir"] = os.path.join(RES, "netlists", blk); _keep["n"] = 0
    shutil.rmtree(_keep["dir"], ignore_errors=True); os.makedirs(_keep["dir"])
    try:
        import clkgen
        clkgen.spinit(_keep["dir"])                  # so 'ngspice r_01.spice' works in that folder
    except Exception:
        pass
    print(f"\n=== {blk}: {what}  (about {mins} min) ===", flush=True)
    t0 = time.time()
    try:
        rows = fn()
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}\n  -> run 'python3 tools/verify.py setup' first; if that is clean, send this message.")
        rows = [dict(quantity="check ran", unit="", yours=None, repo=None, diff=str(e)[:80], ok=False)]
    dt = time.time() - t0
    w = max(len(r["quantity"]) for r in rows)
    print(f"  {'quantity':{w}s}  {'unit':6s} {'yours':>10s} {'repository':>11s} {'difference':>11s}  result")
    for r in rows:
        print(f"  {r['quantity']:{w}s}  {r['unit']:6s} {fmt(r['yours']):>10s} {fmt(r['repo']):>11s} {r['diff']:>11s}  "
              f"{'PASS' if r['ok'] else 'FAIL'}")
    print(f"  ({dt:.0f} s; netlists kept in results/netlists/{blk}/, {_keep['n']} files)")
    os.makedirs(RES, exist_ok=True)
    fn_csv = os.path.join(RES, f"verify_{blk}_{stamp}.csv")
    keys = ["quantity", "unit", "yours", "repo", "diff", "ok"]
    with open(fn_csv, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=keys); wr.writeheader(); wr.writerows(rows)
    hist = os.path.join(RES, "verify_history.csv"); new = not os.path.exists(hist)
    with open(hist, "a", newline="") as fh:
        wr = csv.writer(fh)
        if new:
            wr.writerow(["date", "block"] + keys)
        for r in rows:
            wr.writerow([stamp, blk] + [r[k] for k in keys])
    _keep["dir"] = None
    return all(r["ok"] for r in rows)


def setup():
    ok = True
    def line(name, good, detail, fix=""):
        nonlocal ok
        ok &= good
        print(f"  {'OK  ' if good else 'FAIL'} {name:22s} {detail}" + (f"\n         fix: {fix}" if not good and fix else ""))
    print("Checking your setup:")
    for tool, arg in (("ngspice", "-v"), ("xschem", "--version"), ("netgen", "-batch quit"), ("magic", "--version")):
        p = shutil.which(tool) or (shutil.which("netgen-lvs") if tool == "netgen" else None)
        if not p:
            line(tool, tool in ("magic",), "not found" + (" (needed only for layout)" if tool == "magic" else ""),
                 "install it, or start the IIC-OSIC-TOOLS container, or add its folder to PATH")
            continue
        try:
            out = _orig_run([tool] + arg.split(), capture_output=True, text=True, timeout=30)
            txt = [l for l in (out.stdout + out.stderr).splitlines() if any(c.isalnum() for c in l)]
            pick = [l for l in txt if tool in l.lower() or "version" in l.lower()]
            line(tool, True, ((pick or txt or [p])[0]).strip()[:70])
        except Exception as e:
            line(tool, True, f"{p} ({e.__class__.__name__} asking its version)")
    import clkgen
    line("PDK models", os.path.exists(clkgen.LIB), clkgen.LIB,
         "set PDK_ROOT to the folder that contains sky130A, e.g.  export PDK_ROOT=/foss/pdks  (then rerun)")
    sp = os.path.join(os.path.dirname(clkgen.LIB), "spinit")
    line("PDK spinit", os.path.exists(sp), sp, "the PDK install is incomplete (libs.tech/ngspice/spinit missing)")
    for mod in ("numpy", "scipy", "matplotlib"):
        try:
            m = importlib.import_module(mod); line(mod, True, getattr(m, "__version__", ""))
        except ImportError:
            line(mod, False, "not installed", f"pip install {mod}")
    vf = os.path.join(ROOT, "versions.txt")
    if os.path.exists(vf):
        want = [l.strip() for l in open(vf) if "ngspice" in l.lower()][:1]
        print(f"  info the repository was verified with: {want[0] if want else 'see versions.txt'}")
    print("Setup is ready." if ok else "Fix the FAIL lines, then run this again.")
    return ok


def main(args):
    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__); return 0
    cmd = args[0]
    if cmd == "setup":
        return 0 if setup() else 1
    if cmd == "list":
        print(f"  {'block':7s} {'minutes':>7s}  quick check measures")
        for b, (_, what, m, full) in BLOCKS.items():
            print(f"  {b:7s} {m:7.1f}  {what}\n  {'':7s} {'':7s}  full verification: python3 {full}")
        return 0
    if cmd == "lvs":
        return subprocess.call([sys.executable, os.path.join(ROOT, "tools", "lvs_hv_all.py")])
    if cmd == "full":
        if len(args) < 2 or args[1] not in BLOCKS:
            print("usage: python3 tools/verify.py full <block>   blocks:", " ".join(BLOCKS)); return 1
        script = os.path.join(ROOT, BLOCKS[args[1]][3])
        print(f"Running {BLOCKS[args[1]][3]} {' '.join(args[2:])}\nThis repeats the block's complete verification and "
              "overwrites its data/*.json with your results (git shows the differences: 'git diff --stat').")
        return subprocess.call([sys.executable, script] + args[2:], cwd=os.path.dirname(script))
    if cmd == "all":
        res = {b: quick(b) for b in BLOCKS}
        print("\n=== summary ===")
        for b, ok in res.items():
            print(f"  {b:7s} {'PASS' if ok else 'FAIL'}")
        return 0 if all(res.values()) else 1
    if cmd in BLOCKS:
        return 0 if quick(cmd) else 1
    print(f"unknown command '{cmd}'. Blocks: {' '.join(BLOCKS)}; commands: setup list all lvs full"); return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
