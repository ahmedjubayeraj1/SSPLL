"""ringgen.py - generate an N-stage pseudo-differential ring VCO netlist (cell from sspll_vco_dcell.sch)
for the pinned sky130A PDK (open_pdks 1689ac3f). Widths of every cell device scaled by SC.
usage: python3 ringgen.py N SC corner temp I_A vtune cpar_F mode out.sp
mode: run   - start with a differential kick, measure f, supply, swing
      pwrup - symmetric power-up (current ramps from 0, all nodes 0 V)
      cm    - forced common-mode state plus 10 mV differential kick
      ref/inj:<node>:<t_inj>:<q> - ISF runs (reference, or charge injection)
"""
import sys
N, SC = int(sys.argv[1]), float(sys.argv[2])
corner, temp, I, vt, cpar, mode, out = sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9]
PDK = "/home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice"
def m(name, d, g, s, b, typ, w, l):
    w = round(w*SC, 3)
    return (f"x{name} {d} {g} {s} {b} sky130_fd_pr__{typ} w={w} l={l} nf=1 "
            f"ad={w*0.29:.4f} as={w*0.29:.4f} pd={2*(w+0.29):.3f} ps={2*(w+0.29):.3f}\n")
cell = ".subckt dcell inp inm outp outm vtune vdd vss\n"
cell += m("p1","outm","inp","vdd","vdd","pfet_01v8",8,0.15) + m("n1","outm","inp","vss","vss","nfet_01v8",4,0.15)
cell += m("p2","outp","inm","vdd","vdd","pfet_01v8",8,0.15) + m("n2","outp","inm","vss","vss","nfet_01v8",4,0.15)
cell += m("s1","outm","vtune","n1","vss","nfet_01v8",1.5,0.15) + m("c1","vss","n1","vss","vss","nfet_01v8",3,0.5)
cell += m("s2","outp","vtune","n2","vss","nfet_01v8",1.5,0.15) + m("c2","vss","n2","vss","vss","nfet_01v8",3,0.5)
cell += m("t1n","inp","vdd","outp","vss","nfet_01v8",0.42,0.15) + m("t1p","inp","vss","outp","vdd","pfet_01v8",0.42,0.15)
cell += m("t2n","inm","vdd","outm","vss","nfet_01v8",0.42,0.15) + m("t2p","inm","vss","outm","vdd","pfet_01v8",0.42,0.15)
cell += f"cpp outp vss {cpar}\ncpm outm vss {cpar}\n.ends\n"
buf = """.subckt acbuf in vdd vss
cc in g 36f
rf g x 228k
xp1 x g vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15 ad=0.58 as=0.58 pd=4.58 ps=4.58
xn1 x g vss vss sky130_fd_pr__nfet_01v8 w=1 l=0.15 ad=0.29 as=0.29 pd=2.58 ps=2.58
xp2 o x vdd vdd sky130_fd_pr__pfet_01v8 w=4 l=0.15 ad=1.16 as=1.16 pd=8.58 ps=8.58
xn2 o x vss vss sky130_fd_pr__nfet_01v8 w=2 l=0.15 ad=0.58 as=0.58 pd=4.58 ps=4.58
.ends
"""
# ring: stage k inputs (p_{k-1}, m_{k-1}); last stage crosses: outp->vom, outm->vop
P = ["vop"] + [f"p{k}" for k in range(1, N)] ; M = ["vom"] + [f"m{k}" for k in range(1, N)]
lines = []
for k in range(N):
    ip, im = P[k], M[k]
    op, om = (P[k+1], M[k+1]) if k < N-1 else ("vom", "vop")
    lines.append(f"x{k+1} {ip} {im} {op} {om} vtune vddvco vss dcell\n")
nodes = P + M
bufs = "".join(f"xb_{n} {n} vddbuf vss acbuf\n" for n in nodes)
src = f"ivco 0 vddvco dc {I}\n" if mode != "pwrup" else f"ivco 0 vddvco pwl(0 0 2n {I})\n"
if mode == "pwrup":
    ic = "v(vddvco)=0 " + " ".join(f"v({n})=0" for n in nodes)
elif mode == "cm":
    ic = "v(vddvco)=1.4 " + " ".join(f"v({P[k]})={1.4 if k%2==0 else 0} v({M[k]})={1.4 if k%2==0 else 0}" for k in range(N))
    ic = ic.replace("v(vop)=1.4", "v(vop)=1.41")
else:
    ic = "v(vddvco)=1.3 v(vop)=0 v(vom)=1.3"
inj = ""
tstop, tstep = "40n", "1p"
if mode.startswith("inj"):
    _, node, tinj, q = mode.split(":")
    # charge q delivered as a 1 ps rectangular current pulse into the node
    inj = f"iinj 0 {node} pwl(0 0 {tinj} 0 {float(tinj)+1e-13} {float(q)/1e-12} {float(tinj)+1e-12} {float(q)/1e-12} {float(tinj)+1.1e-12} 0)\n"
ctl = """.control
option noinit
tran {step} {stop} 0 {step} uic
let vd = v(vop)-v(vom)
meas tran t1 when vd=0 rise=40
meas tran t2 when vd=0 rise=60
let f = 20/(t2-t1)
meas tran vdd_avg avg v(vddvco) from=t1 to=t2
meas tran ppd pp vd from=t1 to=t2
print f vdd_avg ppd
{extra}
.endc
"""
extra = ""
if mode.startswith("ref") or mode.startswith("inj"):
    extra = "meas tran tz when vd=0 rise=150\nprint tz"
    tstop = "60n"
if mode == "ref":
    # save device small-signal conductances for the cyclostationary noise of node p1 (and its mirror m1)
    extra += "\nwrdata ref_waves.txt v(vop) v(vom) v(p1) v(m1) v(vddvco)"
net = f"""* {N}-stage pseudo-diff ring, SC={SC}, {corner} {temp}C, I={I}, vtune={vt}, cpar={cpar}, mode={mode}
.lib {PDK} {corner}
.temp {temp}
{cell}{buf}vss vss 0 0
vbuf vddbuf 0 1.8
vtn vtune 0 {vt}
{src}cdec vddvco 0 0.5p
{''.join(lines)}{bufs}{inj}.ic {ic}
{ctl.format(step=tstep, stop=tstop, extra=extra)}.end
"""
open(out, "w").write(net)
