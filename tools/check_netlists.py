#!/usr/bin/env python3
"""check_netlists.py - connectivity checks on the xschem netlists in netlist/.

Checks, per netlist and across the hierarchy:
  E1 missing symbol      xschem wrote "IS MISSING" (symbol not found -> device silently dropped)
  E2 undefined subckt    an X instance calls a subcircuit defined nowhere (not ours, not a PDK device)
  E3 pin-count mismatch  an X instance passes a different number of nets than its .subckt has pins
  E4 duplicate instance  two instances with the same name in one subcircuit
  W1 dangling net        a net that touches exactly one device pin and is not a subcircuit port
  W2 unused port         a subcircuit port that connects to nothing inside the cell
Exit code 1 if any E-type finding exists.  Usage:  python3 tools/check_netlists.py [netlist_dir]
"""
import re, sys, glob, os, collections

root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'netlist')
files = sorted(glob.glob(os.path.join(root, '**', '*.spice'), recursive=True))
PDK_PREFIX = 'sky130_fd_pr__'

def logical_lines(text):
    out = []
    for raw in text.splitlines():
        if raw.startswith('+') and out:
            out[-1] += ' ' + raw[1:]
        else:
            out.append(raw)
    return out

subckts = {}          # name -> (pins, body lines, file)
tops = []             # (file, body lines) for netlists without an enclosing subckt
missing = []
for f in files:
    txt = open(f, errors='ignore').read()
    for m in re.finditer(r'^\*\s+(\S+)\s+-\s+(\S+)\s+IS MISSING', txt, re.M):
        missing.append((os.path.relpath(f, root), m.group(1), m.group(2)))
    cur = None; body = []; top = []
    in_ctrl = False
    for ln in logical_lines(txt):
        s = ln.strip()
        low = s.lower()
        if low.startswith('.control'): in_ctrl = True; continue
        if low.startswith('.endc'): in_ctrl = False; continue
        if in_ctrl or not s or s.startswith('*'): continue
        if low.startswith('.subckt'):
            tok = s.split()
            pins = [t.lower() for t in tok[2:] if '=' not in t]
            cur = tok[1]; body = []; subckts[cur] = (pins, body, os.path.relpath(f, root)); continue
        if low.startswith('.ends'):
            cur = None; continue
        if s.startswith('.'): continue
        (body if cur else top).append(s)
    if top: tops.append((os.path.relpath(f, root), top))

QUOTED = re.compile(r"\"[^\"]*\"|'[^']*'|\{[^}]*\}")

def instances(lines):
    for s in lines:
        s = QUOTED.sub('Q', s)                    # parameter expressions may contain spaces
        s = re.sub(r'\s*=\s*', '=', s)            # "W = 2" -> "W=2"
        tok = s.split()
        tok = [tok[0]] + [t.lower() if '=' not in t else t for t in tok[1:-1]] + tok[-1:]  # SPICE nets are case-insensitive
        name = tok[0]; kind = name[0].upper()
        args = [t for t in tok[1:] if '=' not in t]
        if kind == 'X':
            yield name, 'X', args[:-1], args[-1] if args else None
        elif kind in 'MRCLDVIEFGHBQJ':
            nodes = {'M': 4, 'Q': 3, 'J': 3, 'E': 4, 'G': 4, 'F': 2, 'H': 2, 'D': 2}.get(kind, 2)
            yield name, kind, args[:nodes], None

err = []; warn = []

# Nets used inside a subcircuit without being one of its pins are xschem globals (e.g. a vcc label);
# a top-level source driving such a net is not dangling.
globals_ = set()
for _n, (_pins, _body, _f) in subckts.items():
    for _name, _kind, _nodes, _sub in instances(_body):
        globals_.update(x for x in _nodes if x not in _pins)
for f, inst, sc in missing:
    err.append(f"E1 {f}: instance {inst} uses missing symbol '{sc}'")

def check_body(where, pins, lines):
    seen = collections.Counter(); nets = collections.Counter()
    for name, kind, nodes, sub in instances(lines):
        seen[name.lower()] += 1
        for n in nodes: nets[n] += 1
        if kind == 'X' and sub:
            if sub in subckts:
                want = len(subckts[sub][0])
                if want != len(nodes):
                    err.append(f"E3 {where}: {name} passes {len(nodes)} nets to {sub}, which has {want} pins")
            elif not sub.startswith(PDK_PREFIX):
                err.append(f"E2 {where}: {name} calls undefined subcircuit '{sub}'")
    for name, c in seen.items():
        if c > 1: err.append(f"E4 {where}: instance name {name} used {c} times")
    gnd = {'0', 'gnd', 'vss', 'vdd'}
    for n, c in nets.items():
        if c == 1 and n not in pins and n.lower() not in gnd and not (not pins and n in globals_):
            warn.append(f"W1 {where}: net '{n}' touches only one pin")
    for p in pins:
        if nets[p] == 0:
            warn.append(f"W2 {where}: port '{p}' is not connected inside the cell")

for name, (pins, body, f) in sorted(subckts.items()):
    check_body(f"{f}:{name}", pins, body)
for f, top in tops:
    check_body(f, [], top)

print(f"checked {len(files)} netlists, {len(subckts)} subcircuits, {len(tops)} top-level netlists")
for e in err: print(e)
for w in warn: print(w)
print(f"RESULT: {len(err)} errors, {len(warn)} warnings")
sys.exit(1 if err else 0)
