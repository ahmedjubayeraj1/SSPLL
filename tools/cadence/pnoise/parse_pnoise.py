#!/usr/bin/env python3
"""parse_pnoise.py - phase noise L(df) from a Spectre psfascii pnoise result of an oscillator.
L(df) [dBc/Hz] = 10 log10( S_out(f0+df) / P_carrier ),  P_carrier = |V1|^2 / 2, V1 = first harmonic of the output
(each PM sideband carries P_c*L(df); time-average noise, phase noise dominates near the carrier). Also splits the total into
thermal and flicker device contributions.   usage: parse_pnoise.py pn1.pnoise pss1.fd.pss"""
import sys, re, math
pn, fd = sys.argv[1], sys.argv[2]
# carrier from pss fd: first harmonic of vop - vom
t = open(fd).read().split("VALUE", 1)[1]
blocks = re.split(r'\n"freq" ', t)
h1 = blocks[2]
def cv(name, s):
    m = re.search(r'"%s" \(([-\d.e+]+) ([-\d.e+]+)\)' % name, s); return complex(float(m.group(1)), float(m.group(2)))
v1 = cv("vop", h1) - cv("vom", h1)
A = abs(v1); Pc = A*A/2
# pnoise: types (struct member names), then values
txt = open(pn).read()
typ, val = txt.split("\nVALUE\n", 1)
structs = {}; cur_s = None
for ln in typ.split("\nSWEEP\n")[0].split("\n"):
    m = re.match(r'^"([^"]+)" STRUCT\($', ln)
    if m: cur_s = m.group(1); structs[cur_s] = []; continue
    if cur_s:
        m = re.match(r'^"([^"]+)" FLOAT', ln)
        if m: structs[cur_s].append(m.group(1))
        elif ln.startswith(") PROP(") or ln == ")" and not structs[cur_s] == []:
            if ln.startswith(") PROP("): cur_s = None
trace = dict(re.findall(r'^"([^"]+)" "([^"]+)"$', typ.split("\nTRACE\n", 1)[1], re.M))
pts = []; cur = None
toks = re.findall(r'"[^"]*"|\(|\)|[-+\d.eE]+', val)
i = 0
while i < len(toks):
    tk = toks[i]
    if tk == '"relative frequency"':
        cur = {"f": float(toks[i+1]), "dev": {}}; pts.append(cur); i += 2; continue
    if tk.startswith('"'):
        name = tk.strip('"')
        if i+1 < len(toks) and toks[i+1] == "(":
            j = i + 2; nums = []
            while toks[j] != ")": nums.append(float(toks[j])); j += 1
            members = structs.get(trace.get(name, ""), [])
            cur["dev"][name] = dict(zip(members, nums)); i = j + 1; continue
        cur[name] = float(toks[i+1]); i += 2; continue
    i += 1
outkey = "out"
print(f"carrier |V1(vop-vom)| = {A:.4f} V peak, fundamental from pss")
print(f"{'offset':>10s} {'S_out V^2/Hz':>14s} {'L total':>9s} {'thermal':>9s} {'flicker':>9s}   top contributor")
rows = []
for p in pts:
    s = p[outkey]; S = s*s                          # 'out' is V/sqrt(Hz)
    L = 10*math.log10(S/Pc)
    th = fl = 0.0; top = ("", 0)
    for d, mem in p["dev"].items():
        for k, v in mem.items():
            if k == "total": continue
            if k == "fn": fl += v
            else: th += v
            if v > top[1]: top = (f"{d.replace('.x0.msky130_fd_pr__', '.')}.{k}", v)
    tot = th + fl
    p['sum'] = tot
    Lth = 10*math.log10(th/Pc) if th > 0 else float("nan")
    Lfl = 10*math.log10(fl/Pc) if fl > 0 else float("nan")
    rows.append((p["f"], S, L, Lth, Lfl, top, tot))
for f, S, L, Lth, Lfl, top, tot in rows:
    if any(abs(math.log10(f/x)) < 0.02 for x in (1e3, 1e4, 1e5, 3e5, 1e6, 3e6, 1e7, 1e8)) or "-v" in sys.argv:
        print(f"{f:10.3g} {S:14.4e} {L:9.1f} {Lth:9.1f} {Lfl:9.1f}   {top[0]} ({100*top[1]/tot:.0f}%)   sum/out {tot/S:.3f}")
# 1/f^3 corner: where thermal and flicker parts are equal
for a, b in zip(rows, rows[1:]):
    if a[4] > a[3] and b[4] <= b[3]:
        fa, fb = a[0], b[0]; da, db = a[4]-a[3], b[4]-b[3]
        print(f"flicker = thermal at {fa*(fb/fa)**(da/(da-db))/1e6:.2f} MHz"); break
