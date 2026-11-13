#!/usr/bin/env python3
"""ngspice_expected.py - expected values for corr_pvt.scs, computed by ngspice on the CONVERTED frozen models
(the same files Spectre reads). One run per corner x temperature; writes expected_pvt.csv.
usage: python3 ngspice_expected.py FROZEN_DIR [out.csv]      FROZEN_DIR = output of make_spectre_models.py
Needs ngspice (42 or 47) and the PDK's spinit as .spiceinit in the working directory (copied automatically)."""
import os, sys, subprocess, tempfile, shutil, csv, re
fz = os.path.abspath(sys.argv[1]); out = sys.argv[2] if len(sys.argv) > 2 else "expected_pvt.csv"
lib = f"{fz}/sky130A/libs.tech/ngspice/sky130.lib.spice"
CORNERS = ["tt", "ss", "ff", "sf", "fs", "ll", "hh", "hl", "lh"]   # ll/hh/hl/lh = tt MOS with low/high R and C
TEMPS = [-40, 27, 110]
# Same devices and biases as corr_pvt.scs. Sizes in um (models' scale=1u). Sources named like the Spectre bench.
# Resistor m= is ignored by ngspice-42 on xhigh, so R6 (m=8) is expected as 8 x R3 (checked by Spectre).
BENCH = """* corr_pvt ngspice twin
.lib {lib} {corner}
.temp {temp}
.option tnom=27
vr a 0 1
xr1 a r1 0 sky130_fd_pr__res_xhigh_po_0p35 l=20
v1 r1 0 0
xr2 a r2 0 sky130_fd_pr__res_xhigh_po_0p35 l=1.36
v2 r2 0 0
xr3 a r3 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41
v3 r3 0 0
xr4 a r4 0 sky130_fd_pr__res_xhigh_po_5p73 l=0.65
v4 r4 0 0
xr5 a r5 0 sky130_fd_pr__res_high_po_0p35 l=20
v5 r5 0 0
vc c 0 dc 0 ac 1
xc1 c c1 sky130_fd_pr__cap_mim_m3_1 w=5 l=5
vc1 c1 0 0
xc2 c c2 sky130_fd_pr__cap_mim_m3_1 w=20 l=20
vc2 c2 0 0
vgn gn 0 0.9
vdn dn 0 0.9
xn1 dn gn 0 0 sky130_fd_pr__nfet_01v8 w=4 l=0.15 ad=1.16 as=1.16 pd=8.58 ps=8.58
vsp sp 0 1.8
vgp gp 0 0.9
vdp dp 0 0.9
xp1 dp gp sp sp sky130_fd_pr__pfet_01v8 w=8 l=0.15 ad=2.32 as=2.32 pd=16.58 ps=16.58
.control
op
print i(v1) i(v2) i(v3) i(v4) i(v5) i(vdn) i(vdp)
ac lin 1 1meg 1meg
print mag(i(vc1)) mag(i(vc2))
.endc
.end
"""
wd = tempfile.mkdtemp()
shutil.copy(f"{fz}/sky130A/libs.tech/ngspice/spinit", f"{wd}/.spiceinit")
rows = []
for c in CORNERS:
    for t in TEMPS:
        open(f"{wd}/b.sp", "w").write(BENCH.format(lib=lib, corner=c, temp=t))
        r = subprocess.run(["ngspice", "-b", "b.sp"], cwd=wd, capture_output=True, text=True)
        v = dict((k.lower(), float(x)) for k, x in re.findall(r"^\s*([\w()]+(?:\([\w]+\))?)\s*=\s*([-+\d.eE]+)", r.stdout, re.M))
        g = lambda n: v.get(n)
        I = {k: abs(g(f"i(v{k})")) for k in ("1", "2", "3", "4", "5", "dn", "dp")}
        row = dict(corner=c, temp=t,
                   V1=I["1"], V2=I["2"], V3=I["3"], V4=I["4"], V5=I["5"], V6=8 * I["3"],
                   VC1=g("mag(i(vc1))"), VC2=g("mag(i(vc2))"), VC3=2 * g("mag(i(vc2))"),
                   VDN=I["dn"], VDN7=7 * I["dn"], VDP=I["dp"])
        if None in row.values(): sys.exit(f"parse failed {c} {t}:\n{r.stdout[-1500:]}\n{r.stderr[-800:]}")
        rows.append(row); print(c, t, " ".join(f"{k}={row[k]:.5g}" for k in list(row)[2:]))
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("->", out)
