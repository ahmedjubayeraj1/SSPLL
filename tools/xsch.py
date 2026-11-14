"""xsch.py - write readable, hierarchical xschem schematics from Python, and check them.

Every cell is drawn with real wires (no hidden connections except the MOS body, which the 3-terminal sky130 symbols
show as text), then a symbol is generated so the cell can be placed inside the next level of hierarchy - the same
flow as in Cadence Virtuoso: cell -> symbol -> instance in the parent schematic.

Checks run on every save:
  * no two wire segments of different nets overlap along a line, and no wire passes *through* a pin or a wire end it
    is not connected to (a crossing of two wires without a junction is allowed and is not a connection);
  * every pin of every instance is touched by a wire end (no floating pins);
  * approximate text boxes of instance labels and free text do not overlap each other, and no wire runs through them.
Coordinates follow xschem: x to the right, y downwards, 10-unit grid.
"""
import os, re, itertools

SYM = {  # pin offsets at rot = 0, flip = 0 (from the PDK / xschem library symbols)
    "sky130_fd_pr/nfet3_01v8.sym": {"D": (20, -30), "G": (-20, 0), "S": (20, 30)},
    "sky130_fd_pr/nfet3_01v8_lvt.sym": {"D": (20, -30), "G": (-20, 0), "S": (20, 30)},
    "sky130_fd_pr/pfet3_01v8.sym": {"S": (20, -30), "G": (-20, 0), "D": (20, 30)},
    "sky130_fd_pr/nfet3_g5v0d10v5.sym": {"D": (20, -30), "G": (-20, 0), "S": (20, 30)},
    "sky130_fd_pr/pfet3_g5v0d10v5.sym": {"S": (20, -30), "G": (-20, 0), "D": (20, 30)},
    "sky130_fd_pr/cap_mim_m3_1.sym": {"c0": (0, -30), "c1": (0, 30)},
    "sky130_fd_pr/res_xhigh_po_2p85.sym": {"P": (0, -30), "M": (0, 30), "B": (-20, 0)},
    "sky130_fd_pr/res_xhigh_po_0p35.sym": {"P": (0, -30), "M": (0, 30), "B": (-20, 0)},
    "devices/ipin.sym": {"p": (0, 0)}, "devices/opin.sym": {"p": (0, 0)}, "devices/iopin.sym": {"p": (0, 0)},
    "devices/lab_pin.sym": {"p": (0, 0)}, "devices/isource.sym": {"p": (0, -30), "m": (0, 30)},
    "devices/vsource.sym": {"p": (0, -30), "m": (0, 30)}, "devices/capa.sym": {"p": (0, -30), "m": (0, 30)},
    "devices/res.sym": {"p": (0, -30), "m": (0, 30)}, "devices/gnd.sym": {"p": (0, 0)},
}
# label boxes drawn by the PDK MOS symbols (rot 0), from their T lines: (x0, y0, x1, y1), mirrored with the symbol
# (measured on xschem renders of the 3-terminal symbols: name left of the drain lead, model / nf / W/L right of it)
MOS_TEXT = [(-16, -31, 8, -18), (28, -31, 92, -18), (30, -3, 62, 8), (30, 9, 102, 21)]
MOS_BODY_TEXT = (24, -16, 46, -4)


def xf(dx, dy, rot, flip):
    if flip:
        dx = -dx
    for _ in range(rot % 4):
        dx, dy = -dy, dx
    return dx, dy


MOS_PROPS = ('ad="\'int((nf+1)/2) * W/nf * 0.29\'" pd="\'2*int((nf+1)/2) * (W/nf + 0.29)\'" '
             'as="\'int((nf+2)/2) * W/nf * 0.29\'" ps="\'2*int((nf+2)/2) * (W/nf + 0.29)\'" '
             'nrd="\'0.29 / W\'" nrs="\'0.29 / W\'" sa=0 sb=0 sd=0')


class Sch:
    def __init__(self, name, title=""):
        self.name = name; self.inst = []; self.wires = []; self.texts = []; self.title = title
        self.pins = []        # (name, dir, x, y)
        self.extra_sym = {}   # user symbols: path -> pin offsets

    # ---- placement
    def mos(self, name, kind, x, y, w, l, nf=1, body="VSS", flip=0, rot=0, mult=1):
        sym = f"sky130_fd_pr/{kind}.sym"; model = kind.replace("3_", "_")
        props = (f"name={name} L={l} W={w*nf:g} nf={nf} mult={mult} {MOS_PROPS} model={model} spiceprefix=X "
                 f"body={body}")
        return self._add(sym, x, y, rot, flip, props, name)

    def dev(self, sym, name, x, y, props="", rot=0, flip=0):
        return self._add(sym, x, y, rot, flip, f"name={name} {props}".strip(), name)

    def sub(self, sym_path, pins, name, x, y, rot=0, flip=0):
        self.extra_sym[sym_path] = pins
        return self._add(sym_path, x, y, rot, flip, f"name={name}", name)

    def _add(self, sym, x, y, rot, flip, props, name):
        pins = (self.extra_sym.get(sym) or SYM[sym])
        P = {k: (x + xf(*v, rot, flip)[0], y + xf(*v, rot, flip)[1]) for k, v in pins.items()}
        self.inst.append(dict(sym=sym, x=x, y=y, rot=rot, flip=flip, props=props, name=name, pins=P))
        return P

    def pin(self, name, direction, x, y, flip=0):
        sym = {"in": "devices/ipin.sym", "out": "devices/opin.sym", "inout": "devices/iopin.sym"}[direction]
        self.pins.append((name, direction))
        self.inst.append(dict(sym=sym, x=x, y=y, rot=0, flip=flip, props=f"name=p_{name} lab={name}", name=f"p_{name}",
                              pins={"p": (x, y)}, label=name))
        return (x, y)

    def label(self, name, x, y, flip=0):
        self.inst.append(dict(sym="devices/lab_pin.sym", x=x, y=y, rot=0, flip=flip,
                              props=f"name=l_{name}_{len(self.inst)} sig_type=std_logic lab={name}",
                              name="", pins={"p": (x, y)}, label=name))
        return (x, y)

    def wire(self, *pts, lab=""):
        """Orthogonal polyline through the given points (each step must be horizontal or vertical)."""
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            assert x1 == x2 or y1 == y2, f"wire not orthogonal: {(x1, y1)} -> {(x2, y2)}"
            if (x1, y1) != (x2, y2):
                self.wires.append((x1, y1, x2, y2, lab))

    def text(self, s, x, y, size=0.3):
        self.texts.append((s, x, y, size))

    # ---- checks
    def check(self):
        errs = []
        segs = [(min(a, c), min(b, d), max(a, c), max(b, d), lab) for a, b, c, d, lab in self.wires]
        pts_all = set()
        for a, b, c, d, _ in self.wires:
            pts_all.add((a, b)); pts_all.add((c, d))
        pinpts = {}
        for i in self.inst:
            for k, p in i["pins"].items():
                pinpts.setdefault(p, []).append(f"{i['name'] or i.get('label')}.{k}")
        # nets by geometry (union-find over wire ends, pins and T-junctions)
        par = {}
        def f(a):
            par.setdefault(a, a)
            while par[a] != a:
                par[a] = par[par[a]]; a = par[a]
            return a
        def u(a, b): par[f(a)] = f(b)
        def on(p, s):
            x, y = p; x1, y1, x2, y2 = s[:4]
            return (x1 == x2 == x and y1 <= y <= y2) or (y1 == y2 == y and x1 <= x <= x2)
        for s in segs:
            u((s[0], s[1]), (s[2], s[3]))
            for p in list(pts_all) + list(pinpts):
                if on(p, s):
                    interior = p not in ((s[0], s[1]), (s[2], s[3]))
                    if interior and p in pinpts and p not in pts_all:
                        errs.append(f"wire {s[:4]} passes through pin {pinpts[p]} (connects it - draw to it instead)")
                    u(p, (s[0], s[1]))
        # collinear overlaps of different nets
        for s, t in itertools.combinations(segs, 2):
            if s[0] == s[2] == t[0] == t[2] and max(s[1], t[1]) < min(s[3], t[3]) and f((s[0], s[1])) != f((t[0], t[1])):
                errs.append(f"vertical wires overlap: {s[:4]} / {t[:4]}")
            if s[1] == s[3] == t[1] == t[3] and max(s[0], t[0]) < min(s[2], t[2]) and f((s[0], s[1])) != f((t[0], t[1])):
                errs.append(f"horizontal wires overlap: {s[:4]} / {t[:4]}")
        # floating pins
        for p, who in pinpts.items():
            if not any(on(p, s) for s in segs):
                errs.append(f"pin not wired: {who} at {p}")
        # text boxes
        boxes = []
        for i in self.inst:
            if i["sym"].startswith("sky130_fd_pr/") and "fet" in i["sym"] and i["rot"] == 0:
                for (a, b, c, d) in MOS_TEXT + [MOS_BODY_TEXT]:
                    if i["flip"]:
                        a, c = -c, -a
                    boxes.append((i["x"] + a, i["y"] + b, i["x"] + c, i["y"] + d, i["name"]))
        for s, x, y, size in self.texts:
            boxes.append((x, y, x + 22*size*len(s), y + 45*size, s[:20]))
        for A, Bx in itertools.combinations(boxes, 2):
            if A[0] < Bx[2] and Bx[0] < A[2] and A[1] < Bx[3] and Bx[1] < A[3]:
                errs.append(f"text overlap: {A[4]} / {Bx[4]}")
        for bx in boxes:
            for s in segs:
                x1, y1, x2, y2 = s[:4]
                if x1 == x2 and bx[0] < x1 < bx[2] and y1 < bx[3] and y2 > bx[1]:
                    errs.append(f"wire {s[:4]} runs through text of {bx[4]}")
                if y1 == y2 and bx[1] < y1 < bx[3] and x1 < bx[2] and x2 > bx[0]:
                    errs.append(f"wire {s[:4]} runs through text of {bx[4]}")
        return errs

    # ---- output
    def save(self, path):
        L = ["v {xschem version=3.4.4 file_version=1.2}", "G {}", "K {}", "V {}", "S {}", "E {}"]
        for s, x, y, size in self.texts:
            L.append(f"T {{{s}}} {x} {y} 0 0 {size} {size} {{}}")
        for x1, y1, x2, y2, lab in self.wires:
            L.append(f"N {x1} {y1} {x2} {y2} {{lab={lab}}}")
        for i in self.inst:
            L.append(f"C {{{i['sym']}}} {i['x']} {i['y']} {i['rot']} {i['flip']} {{{i['props']}}}")
        open(path, "w").write("\n".join(L) + "\n")
        errs = self.check()
        return errs


def symbol(path, name, left, right, top=(), bottom=(), w=None, title=None, pitch=40):
    """Box symbol with pins on the left/right (and top/bottom) edges, 20-unit pin pitch. Returns pin offsets.
    Each pin is (name, dir)."""
    n = max(len(left), len(right), 1)
    h = pitch*n + 20
    w = w or max(160, 40*max(len(top), len(bottom), 1) + 40)
    x0, y0, x1, y1 = -w//2, -h//2, w//2, h//2
    L = ["v {xschem version=3.4.4 file_version=1.2}",
         "G {type=subcircuit\nformat=\"@name @pinlist @symname\"\ntemplate=\"name=x1\"\n}", "V {}", "S {}", "E {}",
         f"L 4 {x0} {y0} {x1} {y0} {{}}", f"L 4 {x1} {y0} {x1} {y1} {{}}", f"L 4 {x1} {y1} {x0} {y1} {{}}",
         f"L 4 {x0} {y1} {x0} {y0} {{}}",
         f"T {{@symname}} 0 -7 0 0 0.2 0.2 {{hcenter=true}}", f"T {{@name}} {x0 - 6} {y0 - 24} 0 1 0.25 0.25 {{}}"]
    pins = {}
    def pin(nm, d, x, y, tx, ty, j):
        L.append(f"B 5 {x - 2.5} {y - 2.5} {x + 2.5} {y + 2.5} {{name={nm} dir={d}}}")
        L.append(f"T {{{nm}}} {tx} {ty} 0 {j} 0.2 0.2 {{}}")
        pins[nm] = (x, y)
    for k, (nm, d) in enumerate(left):
        y = y0 + 10 + pitch*k + pitch//2 + (h - pitch*len(left) - 20)//2
        y = round(y/10)*10
        L.append(f"L 7 {x0 - 20} {y} {x0} {y} {{}}"); pin(nm, d, x0 - 20, y, x0 + 5, y - 6, 0)
    for k, (nm, d) in enumerate(right):
        y = y0 + 10 + pitch*k + pitch//2 + (h - pitch*len(right) - 20)//2
        y = round(y/10)*10
        L.append(f"L 7 {x1} {y} {x1 + 20} {y} {{}}"); pin(nm, d, x1 + 20, y, x1 - 5, y - 6, 1)
    for k, (nm, d) in enumerate(top):
        x = x0 + 40*(k + 1); L.append(f"L 7 {x} {y0 - 20} {x} {y0} {{}}"); pin(nm, d, x, y0 - 20, x + 4, y0 + 4, 0)
    for k, (nm, d) in enumerate(bottom):
        x = x0 + 40*(k + 1); L.append(f"L 7 {x} {y1} {x} {y1 + 20} {{}}"); pin(nm, d, x, y1 + 20, x + 4, y1 - 16, 0)
    open(path, "w").write("\n".join(L) + "\n")
    return pins
