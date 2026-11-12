#!/usr/bin/env python3
"""make_spectre_models.py - build a Spectre-ready copy of the FROZEN open-source sky130A models
(open_pdks 1689ac3f) for use with a Virtuoso kit such as sky130_release_0.0.4.

What it does (no model value is changed - syntax and naming only):
 1. copies  $PDK_ROOT/sky130A/libs.tech/ngspice  and  libs.ref/sky130_fd_pr/spice  into OUT,
    keeping the relative layout the include lines rely on;
 2. moves each subcircuit's parameter defaults from a '.param' line in the body onto the '.subckt' line
    (Spectre treats body .param as fixed constants, so instance w/l would be ignored);
 3. writes OUT/sspll_kit_wrap.spice: subcircuits with the kit's short cell names (nfet_01v8, res_xhigh_po_0p35,
    cap_mim_m3_1 ...) that take the kit's SI units (w=20u) and call the frozen sky130_fd_pr__ models in um.
Usage:  python3 make_spectre_models.py  [PDK_ROOT]  [OUT]
        defaults: PDK_ROOT=$PDK_ROOT, OUT=$HOME/sky130A_frozen_spectre
In ADE > Setup > Model Libraries use exactly two entries (remove the kit's own sky130.lib.spice):
   OUT/sky130A/libs.tech/ngspice/sky130.lib.spice   section tt   (or ss, ff, sf, fs ...)
   OUT/sspll_kit_wrap.spice                           (no section)
"""
import os, re, sys, shutil, json
pdk_root = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PDK_ROOT", "")
out = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/sky130A_frozen_spectre")
src = os.path.join(pdk_root, "sky130A")
if not os.path.isdir(os.path.join(src, "libs.tech", "ngspice")):
    sys.exit(f"no sky130A models under {src} - pass PDK_ROOT")
# record which PDK this was built from
commit = "unknown"
try:
    commit = json.load(open(os.path.join(src, ".config", "nodeinfo.json")))["commit"]["open_pdks"]
except Exception:
    pass
for sub in ("libs.tech/ngspice", "libs.ref/sky130_fd_pr/spice"):
    d = os.path.join(out, "sky130A", sub)
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(os.path.join(src, sub), d)

PAT = re.compile(r"^(\.subckt[^\n]*)\n\+[ \t]*\n(\.param[^\n]*(?:\n\+[^\n]*)*)", re.M | re.I)
def fix(m):
    head, prm = m.group(1), m.group(2)
    prm = re.sub(r"^\.param", "", prm, flags=re.I)
    prm = " ".join(l.lstrip("+").strip() for l in prm.split("\n"))
    prm = re.sub(r"\s*=\s*", "=", prm).strip()
    return f"{head} {prm}"
nfix = nfile = 0
spdir = os.path.join(out, "sky130A", "libs.ref/sky130_fd_pr/spice")
for f in os.listdir(spdir):
    p = os.path.join(spdir, f)
    if not f.endswith(".spice"): continue
    t = open(p, errors="ignore").read()
    t2, k = PAT.subn(fix, t)
    if k:
        open(p, "w").write(t2); nfix += k; nfile += 1

# 2b. remove Monte Carlo terms 'MC_MM_SWITCH*AGAUSS(..)*(..)' and 'MC_PR_SWITCH*AGAUSS(..)..'.
#     Older Spectre (MMSIM 15.1) rejects AGAUSS in model cards. In every corner section (tt, ss, ff, sf, fs, ...)
#     both switches are 0, so each term is exactly 0: nominal results are unchanged (verified in ngspice).
#     Consequence: the 'mc' Monte Carlo sections do nothing in Spectre - run Monte Carlo in ngspice.
SW = re.compile(r"MC_(MM|PR)_SWITCH\s*\*\s*AGAUSS\s*\(", re.I)
def strip_mc(t):
    out, i, n = [], 0, 0
    while True:
        m = SW.search(t, i)
        if not m:
            out.append(t[i:]); return "".join(out), n
        s = m.start()
        j = s - 1                                   # operator before the term
        while j >= 0 and t[j] in " \t": j -= 1
        lead = t[j] if j >= 0 and t[j] in "+-" else ""
        k, depth = m.end(), 1                       # skip AGAUSS( ... )
        while depth:
            depth += {"(": 1, ")": -1}.get(t[k], 0); k += 1
        while True:                                 # further factors: *(...), *name, *number
            r = k
            while r < len(t) and t[r] in " \t": r += 1
            if r < len(t) and t[r] in "*/":
                r += 1
                while t[r] in " \t": r += 1
                if t[r] == "(":
                    d = 1; r += 1
                    while d:
                        d += {"(": 1, ")": -1}.get(t[r], 0); r += 1
                else:
                    while r < len(t) and (t[r].isalnum() or t[r] in "_." or
                                          (t[r] in "+-" and t[r-1] in "eE" and t[r-2].isdigit())): r += 1
                    if r < len(t) and t[r] == "(":      # function call such as sqrt(...)
                        d = 1; r += 1
                        while d:
                            d += {"(": 1, ")": -1}.get(t[r], 0); r += 1
                k = r
            else:
                break
        if lead:
            out.append(t[i:j]); i = k
        else:
            out.append(t[i:s] + "0"); i = k
        n += 1
nmc = 0
for base in ("libs.ref/sky130_fd_pr/spice", "libs.tech/ngspice"):
    for dp, _, fs in os.walk(os.path.join(out, "sky130A", base)):
        for f in fs:
            if not f.endswith(".spice"): continue
            p = os.path.join(dp, f)
            t = open(p, errors="ignore").read()
            if "AGAUSS" not in t.upper(): continue
            t2, k = strip_mc(t)
            if k:
                open(p, "w").write(t2); nmc += k

# 2c. MMSIM 15.1 SPICE-reader limits:
#   - voltage-dependent resistors 'r = {.. v(a,b) ..}' are not accepted -> evaluate at 0 V across the resistor
#     (small-signal value; the size of this approximation is listed in tools/cadence/README.md)
#   - '{expr}' parameter expressions are rejected on .subckt header lines -> written as 'expr' (quotes)
#   - '(x)**2' -> pow(x,2)
VREF = re.compile(r"\bv\(\s*[\w.]+\s*(,\s*[\w.]+\s*)?\)", re.I)
BRACE = re.compile(r"\{([^{}']*)\}", re.S)
def pow2(st):                                   # (x)**2 -> pow((x),2), x may contain parentheses
    while "**2" in st:
        k = st.index("**2"); j = k - 1
        if st[j] != ")": st = st[:k] + "*" + st[k:].replace("**2", "", 1).replace("", "", 0); break
        d = 1; j -= 1
        while d:
            d += {")": 1, "(": -1}.get(st[j], 0); j -= 1
        st = st[:j+1] + "pow(" + st[j+1:k] + ",2)" + st[k+3:]
    return st
def fix_lines(t):
    lines = t.split("\n"); stm = []; k_r = k_b = 0
    i = 0; res = []
    while i < len(lines):                       # group a statement with its '+' continuation lines
        if lines[i].lstrip().startswith("*") or not lines[i].strip():
            res.append(lines[i]); i += 1; continue
        grp = [lines[i]]; cm = []; i += 1
        while i < len(lines):
            s = lines[i].lstrip()
            if s.startswith("+"): grp.append(lines[i]); i += 1
            elif s.startswith("*") and i + 1 < len(lines) and any(x.lstrip().startswith("+") for x in lines[i+1:i+3]):
                cm.append(lines[i]); i += 1        # comment inside a continued statement: move it in front
            else: break
        st = "\n".join(grp)
        head = st.lstrip()
        if re.match(r"r\S*\s+\S+\s+\S+\s+r\s*=", head, re.I) and VREF.search(st):
            st = VREF.sub("0", st); k_r += 1
        if "**2" in st: st = pow2(st)
        st2 = BRACE.sub(lambda m: "'" + m.group(1) + "'", st)
        if st2 != st: k_b += 1
        res.extend(cm); res.append(st2)
    return "\n".join(res), k_r, k_b
nvr = nbr = 0
for base in ("libs.ref/sky130_fd_pr/spice", "libs.tech/ngspice"):
    for dp, _, fs in os.walk(os.path.join(out, "sky130A", base)):
        for f in fs:
            if not f.endswith(".spice"): continue
            p = os.path.join(dp, f)
            t = open(p, errors="ignore").read()
            if "{" not in t and "**" not in t and "v(" not in t.lower(): continue
            t2, a, b2 = fix_lines(t)
            if t2 != t:
                open(p, "w").write(t2); nvr += a; nbr += b2

MOS = ["nfet_01v8", "pfet_01v8", "nfet_01v8_lvt", "pfet_01v8_lvt", "pfet_01v8_hvt", "nfet_g5v0d10v5",
       "pfet_g5v0d10v5", "nfet_03v3_nvt", "nfet_05v0_nvt"]
RES = [f"res_{k}_po_{w}" for k in ("xhigh", "high") for w in ("0p35", "0p69", "1p41", "2p85", "5p73")]
CAP = ["cap_mim_m3_1", "cap_mim_m3_2"]
w = [f"* sspll_kit_wrap.spice - kit cell names and SI units -> frozen sky130_fd_pr__ models (sizes in um)",
     f"* built from open_pdks {commit}. Generated by tools/cadence/make_spectre_models.py; do not edit.",
     "* mos_u: factor from the kit's metres to the models' um. 1e6 assumes Spectre applies the models'",
     "* '.option scale=1u'. If the MOS bench current is ~1e6x off, set mos_u=1 (see README).",
     ".param mos_u=1e6", ""]
for n in MOS:
    w += [f".subckt {n} d g s b w=1e-6 l=1.5e-7 nf=1 ad=0 as=0 pd=0 ps=0 nrd=0 nrs=0 sa=0 sb=0 sd=0",
          f"x0 d g s b sky130_fd_pr__{n} w={{w*mos_u}} l={{l*mos_u}} nf={{nf}} ad={{ad*mos_u*mos_u}} "
          f"as={{as*mos_u*mos_u}} pd={{pd*mos_u}} ps={{ps*mos_u}} nrd={{nrd}} nrs={{nrs}} "
          f"sa={{sa*mos_u}} sb={{sb*mos_u}} sd={{sd*mos_u}}", ".ends", ""]
for n in RES:   # width is fixed by the cell name; the kit's w and r parameters are accepted and ignored
    w += [f".subckt {n} r0 r1 b l=5e-6 w=0 r=0", f"x0 r0 r1 b sky130_fd_pr__{n} l={{l*1e6}}", ".ends", ""]
for n in CAP:   # resistor and cap models compute R and C from w, l in um directly (scale does not apply)
    w += [f".subckt {n} c0 c1 w=1e-6 l=1e-6", f"x0 c0 c1 sky130_fd_pr__{n} w={{w*1e6}} l={{l*1e6}}", ".ends", ""]
open(os.path.join(out, "sspll_kit_wrap.spice"), "w").write("\n".join(w).replace("{", "'").replace("}", "'"))
print(f"frozen models from open_pdks {commit} -> {out}")
print(f"moved .param defaults onto .subckt line: {nfix} subcircuits in {nfile} files")
print(f"removed Monte Carlo AGAUSS terms (zero in corner sections): {nmc}")
print(f"voltage-dependent resistor lines evaluated at 0 V: {nvr}; brace expressions rewritten in quotes: {nbr}")
print(f"wrappers: {len(MOS)} MOS, {len(RES)} resistors, {len(CAP)} MIM -> {out}/sspll_kit_wrap.spice")
