#!/usr/bin/env python3
"""ground_split_check.py - proves that splitting the single ground VSS into VSSA (analog, VDDA domain) and VSSD
(digital, VDDD domain) changed nothing in the simulated circuits, and that every instance line still has the right
number of nodes.

  snap DIR   write the LVS reference netlists and the bench netlists that can be built without running ngspice
  check DIR  build the same netlists from the current code, collapse VSSA and VSSD back into one VSS, and compare
             them with the snapshot line by line; then count the nodes on every instance of a sspll_ cell found in
             the design scripts and compare with the cell's port count

Why the comparison is a proof. With VSSA = VSSD = 0 V (every pre-layout bench) the two nets are one node, so a netlist
whose VSSA and VSSD are merged is the circuit that was simulated before if, and only if, it is the old netlist. The
merge rule: rename VSSA and VSSD to VSS, then drop a VSS that directly follows another VSS in a .subckt port list or
in an instance's node list (a mixed cell has the two grounds side by side, 'VSSA VSSD'; the old cell had one 'VSS').
"""
import os, re, sys, glob, importlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in ("cco", "clkgen", "refbuf", "sspd", "sscp", "vco", "loop"):
    sys.path.insert(0, os.path.join(ROOT, "design", d))


def netlists():
    """name -> netlist text, built without running a simulator."""
    import cco_hv, clkgen_hv, refbuf_hv, sspd_hv, sscp_hv, vco_hv
    from step74hv_point import VARIANTS
    n = {}
    n["ref_cco_hv"] = cco_hv.full(cco_hv.D)
    n["ref_clkgen_hv"] = clkgen_hv.lvs_reference()
    n["ref_refbuf_hv"] = refbuf_hv.lvs_reference()
    n["ref_sspd_hv"] = sspd_hv.lvs_reference()
    n["ref_sscp_hv"] = sscp_hv.lvs_reference()
    n["ref_vco_hv"] = vco_hv.lvs_reference(VARIANTS["hl6"])
    n["tb_cco_hv"] = cco_hv.tb(cco_hv.D, "tt", 27)
    n["tb_refbuf_hv"] = refbuf_hv.head()
    n["tb_sspd_hv"] = sspd_hv.bench()[0]
    n["tb_sscp_hv"] = sscp_hv.head()
    return n


def collapse(text):
    """Merge VSSA and VSSD into one node VSS. A cell whose port list holds 'VSSA VSSD' side by side (a mixed cell)
    gets the pair merged into one port, and every instance of it gets the two matching nodes merged (whatever they are
    called in the bench, e.g. '0 0' -> '0'); then every remaining VSSA / VSSD is renamed VSS."""
    pair = {}
    for m in re.finditer(r"^\.subckt (\S+)((?: \S+)*)", text, re.M):
        pl = m.group(2).split()
        for i in range(len(pl) - 1):
            if pl[i] == "VSSA" and pl[i + 1] == "VSSD":
                pair[m.group(1)] = i
    out = []
    for line in text.split("\n"):
        tok = line.split()
        if tok and tok[0] == ".subckt" and tok[1] in pair:
            i = pair[tok[1]] + 2
            tok = tok[:i + 1] + tok[i + 2:]
            line = " ".join(tok)
        elif tok and re.match(r"^x", tok[0]) and tok[-1] in pair:
            i = pair[tok[-1]] + 1
            tok = tok[:i + 1] + tok[i + 2:]
            line = " ".join(tok)
        out.append(re.sub(r"\bVSS[AD]\b", "VSS", line))
    return "\n".join(out)


def canon_ports(text):
    """Inside each .subckt, replace its port names by their positions (<1>, <2>, ...): a port renamed consistently
    in the cell (e.g. a 1.8 V cell's VDD / VSS now called VDDD / VSSD) is the same circuit, ports connect by position."""
    out, names = [], None
    for line in text.split("\n"):
        tok = line.split()
        if tok[:1] == [".subckt"]:
            names = {n: f"<{i}>" for i, n in enumerate(tok[2:], 1)}
            line = " ".join(tok[:2] + [names[n] for n in tok[2:]])
        elif tok[:1] == [".ends"]:
            names = None
        elif names and tok and not line.startswith("*"):
            line = " ".join(names.get(t, t) for t in tok)
        out.append(line)
    return "\n".join(out)


def norm(text):
    """Comment lines dropped, white space normalised, port names by position."""
    lines = [" ".join(l.split()) for l in text.split("\n") if not l.lstrip().startswith("*")]
    return canon_ports("\n".join(lines))


def ports(texts):
    p = {}
    for t in texts:
        for m in re.finditer(r"^\.subckt (\S+)((?: \S+)*)", t, re.M):
            p[m.group(1)] = len(m.group(2).split())
    return p


def instance_counts(nports):
    """Every instance of a sspll_ cell written in a design script string: node count vs port count."""
    bad, seen = [], 0
    files = glob.glob(os.path.join(ROOT, "design", "*", "*hv*.py"))      # the 5 V design (the 1.8 V files are the record)
    pat = re.compile(r"(?:^|[\"'\\n]|\\n)(x[\w{}\[\]]*)((?: +[^ \"'\\\n]+)+?) +(sspll_\w+)(?=\\n|\"|'|\s*$)")
    for f in files:
        if "v1_mirror" in f or "/sspll_" in f:
            continue
        txt = open(f).read()
        for m in pat.finditer(txt):
            cell = m.group(3)
            if cell not in nports:
                continue
            seen += 1
            n = len(m.group(2).split())
            if n != nports[cell]:
                bad.append(f"{os.path.relpath(f, ROOT)}: {m.group(1)} ... {cell}: {n} nodes, cell has {nports[cell]}")
    return seen, bad


if __name__ == "__main__":
    mode, d = sys.argv[1], sys.argv[2]
    nets = netlists()
    if mode == "snap":
        os.makedirs(d, exist_ok=True)
        for k, v in nets.items():
            open(os.path.join(d, k + ".spice"), "w").write(v)
        print(f"{len(nets)} netlists written to {d}")
        sys.exit(0)
    ok = True
    for k, v in nets.items():
        old = norm(open(os.path.join(d, k + ".spice")).read())
        new = norm(collapse(v))
        same = old == new
        ok &= same
        na = len(re.findall(r"\bVSSA\b", v)); nd = len(re.findall(r"\bVSSD\b", v)); nv = len(re.findall(r"\bVSS\b", v))
        print(f"{k:16s} {'IDENTICAL' if same else 'DIFFERENT'} with VSSA = VSSD   (VSSA x{na}, VSSD x{nd}, plain VSS x{nv})")
        if not same:
            import difflib
            for l in list(difflib.unified_diff(old.split("\n"), new.split("\n"), lineterm="", n=0))[:20]:
                print("   ", l)
    # domain audit: a 1.8 V (thin-oxide) device must not touch VDDA / VSSA; every 5 V device that returns to VSSD is
    # listed (it is allowed only where its supply is VDDD, e.g. the receiver's 3.3 -> 1.8 V inverter)
    viol, d5 = [], set()
    for k, v in nets.items():
        if not k.startswith("ref_"):
            continue
        for l in v.split("\n"):
            t = l.split()
            if len(t) > 5 and t[0].startswith("x") and "sky130_fd_pr__" in t[5] and "fet" in t[5]:
                term = t[1:5]
                if "01v8" in t[5] and ({"VDDA", "VSSA"} & set(term)):
                    viol.append(f"{k}: {l[:60]}")
                if "g5v0" in t[5] and "VSSD" in term:
                    d5.add(f"{k}: {t[0]} ({t[5].split('__')[1]}, terminals {' '.join(term)})")
    print(f"domain audit: thin-oxide devices on VDDA / VSSA: {len(viol)}")
    for x in viol:
        print("   ", x)
    print("5 V devices returning to VSSD (supplied from VDDD):")
    for x in sorted(d5):
        print("   ", x)
    ok &= not viol
    seen, bad = instance_counts(ports(nets.values()))
    print(f"instance lines checked: {seen}; node-count mismatches: {len(bad)}")
    for b in bad:
        print("   ", b)
    sys.exit(0 if ok and not bad else 1)
