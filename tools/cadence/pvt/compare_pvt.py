#!/usr/bin/env python3
"""compare_pvt.py - read the Spectre psfascii results of run_corr_pvt.sh and compare with expected_pvt.csv.
usage: compare_pvt.py OUT_DIR expected_pvt.csv frozen|kit
frozen: PASS when every value is within TOL of ngspice (same model files, so only numerics may differ).
kit:    no pass/fail; prints the kit-vs-frozen difference per device and corner (|diff| > 2% marked)."""
import sys, os, re, csv, glob
out, exp_csv, mode = sys.argv[1], sys.argv[2], sys.argv[3]
TOL = 0.5          # % for frozen mode
FLAG = 2.0         # % marked in kit mode (correlation/README acceptance for R and C)
DEV = [  # key, what, kind (dc current or ac magnitude), how to show it
    ("V1", "xhigh 0.35 x 20 um", "dc", "R"), ("V2", "xhigh 0.35 x 1.36 um (LF R1)", "dc", "R"),
    ("V3", "xhigh 5.73 x 5.41 um", "dc", "R"), ("V4", "xhigh 5.73 x 0.65 um", "dc", "R"),
    ("V5", "high 0.35 x 20 um", "dc", "R"), ("V6", "xhigh 5.73 x 5.41 um, m=8", "dc", "R"),
    ("VC1", "MIM 5 x 5 um", "ac", "C"), ("VC2", "MIM 20 x 20 um", "ac", "C"), ("VC3", "MIM 20 x 20 um, m=2", "ac", "C"),
    ("VDN", "nfet 4/0.15, Vgs=Vds=0.9", "dc", "I"), ("VDN7", "nfet 4/0.15, m=7", "dc", "I"),
    ("VDP", "pfet 8/0.15, Vsg=Vsd=0.9", "dc", "I")]
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
PAT = re.compile(r'^"([^"]+)"\s+(?:"[^"]+"\s+)?(\(\s*(%s)\s+(%s)\s*\)|%s)\s*$' % (NUM, NUM, NUM), re.M)

def read_psf(path):
    """name -> float (|complex| for AC) from the VALUE section of a psfascii file; first value per name."""
    t = open(path, errors="ignore").read()
    if "VALUE" not in t: return {}
    v = {}
    for m in PAT.finditer(t.split("VALUE", 1)[1]):
        name = m.group(1)
        if name in v: continue
        val = abs(complex(float(m.group(3)), float(m.group(4)))) if m.group(3) else abs(float(m.group(2)))
        v[name] = val
    return v

def point(d):
    psf = os.path.join(d, "psf")
    dc, ac = {}, {}
    for f in glob.glob(os.path.join(psf, "*")):
        b = os.path.basename(f)
        if b.endswith(".dc") and "dcop" in b.lower(): dc.update(read_psf(f))
        elif b.endswith(".ac"): ac.update(read_psf(f))
    def get(src, k):
        for n in (k + ":p", k + ":1", k):
            if n in src: return src[n]
        return None
    return {k: get(dc if kind == "dc" else ac, k) for k, _, kind, _ in DEV}

exp = {(r["corner"], int(float(r["temp"]))): {k: float(r[k]) for k, *_ in DEV} for r in csv.DictReader(open(exp_csv))}
worst, fails, missing, rows = 0.0, [], [], []
print(f"# Step 7 correlation, mode = {mode}\n")
print(f"Spectre on {'converted frozen models' if mode == 'frozen' else 'the kit models'} vs ngspice on the converted "
      f"frozen models (open_pdks 1689ac3f). diff = Spectre / ngspice - 1 of the measured current.\n")
for (c, t), e in exp.items():
    d = os.path.join(out, f"{c}_{t}")
    if not os.path.isdir(d) or os.path.exists(os.path.join(d, "MISSING")):
        missing.append(f"{c} {t}"); continue
    s = point(d)
    for k, what, kind, show in DEV:
        if s[k] is None: fails.append(f"{c} {t} {k}: no value in psf"); continue
        diff = (s[k] / e[k] - 1) * 100
        if mode == "frozen":
            worst = max(worst, abs(diff))
            if abs(diff) > TOL: fails.append(f"{c} {t} {k} ({what}): {diff:+.2f}%")
        rows.append((c, t, k, what, show, s[k], e[k], diff))
# table: one line per device and corner/temperature; values in R (Ohm), C (fF) or I (A)
def fmt(show, i, kind_c=False):
    if show == "R": return f"{1 / i:.5g} Ohm"
    if show == "C": return f"{i / (2 * 3.141592653589793 * 1e6) * 1e15:.5g} fF"
    return f"{i:.5g} A"
print("| corner | T (C) | source | device | Spectre | ngspice | diff |")
print("|---|---|---|---|---|---|---|")
for c, t, k, what, show, sv, ev, diff in rows:
    mark = " **!**" if (mode == "kit" and abs(diff) > FLAG) or (mode == "frozen" and abs(diff) > TOL) else ""
    print(f"| {c} | {t} | {k} | {what} | {fmt(show, sv)} | {fmt(show, ev)} | {diff:+.2f}%{mark} |")
print()
if missing: print("Missing corner/temperature points:", ", ".join(missing), "\n")
if mode == "frozen":
    ok = not fails and not missing
    print(f"**{'PASS' if ok else 'FAIL'}** - worst |diff| {worst:.3f}% (limit {TOL}%) over {len(rows)} values.")
    for f in fails: print("-", f)
    sys.exit(0 if ok else 2)
else:
    # summary per device: worst over corners/temperatures
    print("Summary (kit vs frozen, worst over all points):\n")
    print("| device | worst diff | at |")
    print("|---|---|---|")
    for k, what, *_ in DEV:
        r = [x for x in rows if x[2] == k]
        if r:
            w = max(r, key=lambda x: abs(x[7]))
            print(f"| {what} | {w[7]:+.2f}% | {w[0]} {w[1]} C |")
    for f in fails: print("-", f)
