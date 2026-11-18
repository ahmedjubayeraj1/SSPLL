#!/usr/bin/env python3
"""step74hv_startup.py [VARIANT] - power-up start-up of the 5 V ring (method M1, corrected read-out):
all nodes and the ring supply start at 0 V, the CCO current ramps in 2 ns. Read-out: the time when |v(vop)-v(vom)|
first exceeds 1 V (start-up time), and f (10 periods from the first rising zero crossing after 40 ns) and the differential swing in 40-60 ns.
(The first version measured between the 10th and 30th zero crossing of vd, which at power-up are numerical chatter
around 0 V in the first ns: it reported 'no oscillation' although the ring starts. See the design log, step 74-HV.)
Cases: tt/27, ss/110, ff/-40 symmetric; tt, ss, ff with +-2 % width mismatch in stage 1. -> data/step74hv_startup_VARIANT.json"""
import sys, os, re, json, subprocess, tempfile
import vco_hv as v
from step74hv_point import VARIANTS
name = sys.argv[1] if len(sys.argv) > 1 else "hl6"; p = VARIANTS[name]
I0 = json.load(open(os.path.join(v.HERE, "data", f"step74hv_{name}.json")))["I"]
C3 = [("tt", 27, 10e-15, 3.3), ("ss", 110, 15e-15, 2.97), ("ff", -40, 5e-15, 3.63)]
out = {}
for c, t, cp, vd in C3:
    for tag, mm in (("sym", None), ("mism+", dict(P=1.02, N=0.98, TN=1.02)), ("mism-", dict(P=0.98, N=1.02, TN=0.98))):
        net = v.netlist(p, I=I0, corner=c, temp=t, cpar=cp, vdda=vd, mode="pwrup", tstop=60e-9, r0=40, r1=60, mism=mm)
        net = net.replace("print f vdd_avg", "let avd = abs(vd)\nmeas tran tst when avd=1.0 cross=1\nmeas tran psw pp vd from=40n to=60n\n"
                          "meas tran tq1 when vd=0 rise=1 td=40n\nmeas tran tq2 when vd=0 rise=11 td=40n\nlet fq = 10/(tq2-tq1)\n"
                          "print tst psw fq\nprint f vdd_avg")
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "r.sp"), "w").write(net); v.v18.spinit(d)
            o = subprocess.run(["ngspice", "-b", "r.sp"], capture_output=True, text=True, cwd=d).stdout
        g = lambda k: (lambda m: float(m.group(1)) if m else None)(re.search(rf"^{k} = (\S+)", o, re.M))
        out[f"{c}_{t}_{tag}"] = dict(t_start=g("tst"), f=g("fq"), swing=g("psw"), vring=g("vdd_avg"))
        r = out[f"{c}_{t}_{tag}"]
        print(c, t, tag, f"|vd| > 1 V at {r['t_start']*1e9 if r['t_start'] else -1:.2f} ns, f {(r['f'] or 0)/1e6:.1f} MHz, "
              f"swing {r['swing'] or 0:.2f} V", flush=True)
json.dump(out, open(os.path.join(v.HERE, "data", f"step74hv_startup_{name}.json"), "w"), indent=1)
