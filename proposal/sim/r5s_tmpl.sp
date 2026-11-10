* sspll ring VCO feasibility: CORNER=%CORNER% TEMP=%TEMP% I=%IVCO% VT=%VT% CPAR=%CPAR%
.option scale=1e-6
.include "/home/claude/feas/core_%CORNER%.lib"
.param mc_mm_switch=0 mc_pr_switch=0
.temp %TEMP%
.param cpar=%CPAR% SC=%SC%
* --- delay cell (from sspll_vco_dcell.sch) ---
.subckt dcell inp inm outp outm vtune vdd vss
xp1 outm inp vdd vdd sky130_fd_pr__pfet_01v8 w={8.0*SC} l=0.15 ad={8.0*SC*0.29} as={8.0*SC*0.29} pd={2*(8.0*SC+0.29)} ps={2*(8.0*SC+0.29)}
xn1 outm inp vss vss sky130_fd_pr__nfet_01v8 w={4.0*SC} l=0.15 ad={4.0*SC*0.29} as={4.0*SC*0.29} pd={2*(4.0*SC+0.29)} ps={2*(4.0*SC+0.29)}
xp2 outp inm vdd vdd sky130_fd_pr__pfet_01v8 w={8.0*SC} l=0.15 ad={8.0*SC*0.29} as={8.0*SC*0.29} pd={2*(8.0*SC+0.29)} ps={2*(8.0*SC+0.29)}
xn2 outp inm vss vss sky130_fd_pr__nfet_01v8 w={4.0*SC} l=0.15 ad={4.0*SC*0.29} as={4.0*SC*0.29} pd={2*(4.0*SC+0.29)} ps={2*(4.0*SC+0.29)}
xs1 outm vtune n1 vss sky130_fd_pr__nfet_01v8 w={1.5*SC} l=0.15 ad={1.5*SC*0.29} as={1.5*SC*0.29} pd={2*(1.5*SC+0.29)} ps={2*(1.5*SC+0.29)}
xc1 vss n1 vss vss sky130_fd_pr__nfet_01v8 w={3.0*SC} l=0.5 ad={3.0*SC*0.29} as={3.0*SC*0.29} pd={2*(3.0*SC+0.29)} ps={2*(3.0*SC+0.29)}
xs2 outp vtune n2 vss sky130_fd_pr__nfet_01v8 w={1.5*SC} l=0.15 ad={1.5*SC*0.29} as={1.5*SC*0.29} pd={2*(1.5*SC+0.29)} ps={2*(1.5*SC+0.29)}
xc2 vss n2 vss vss sky130_fd_pr__nfet_01v8 w={3.0*SC} l=0.5 ad={3.0*SC*0.29} as={3.0*SC*0.29} pd={2*(3.0*SC+0.29)} ps={2*(3.0*SC+0.29)}
xt1n inp vdd outp vss sky130_fd_pr__nfet_01v8 w={0.42*SC} l=0.15 ad={0.42*SC*0.29} as={0.42*SC*0.29} pd={2*(0.42*SC+0.29)} ps={2*(0.42*SC+0.29)}
xt1p inp vss outp vdd sky130_fd_pr__pfet_01v8 w={0.42*SC} l=0.15 ad={0.42*SC*0.29} as={0.42*SC*0.29} pd={2*(0.42*SC+0.29)} ps={2*(0.42*SC+0.29)}
xt2n inm vdd outm vss sky130_fd_pr__nfet_01v8 w={0.42*SC} l=0.15 ad={0.42*SC*0.29} as={0.42*SC*0.29} pd={2*(0.42*SC+0.29)} ps={2*(0.42*SC+0.29)}
xt2p inm vss outm vdd sky130_fd_pr__pfet_01v8 w={0.42*SC} l=0.15 ad={0.42*SC*0.29} as={0.42*SC*0.29} pd={2*(0.42*SC+0.29)} ps={2*(0.42*SC+0.29)}
cpp outp vss {cpar}
cpm outm vss {cpar}
.ends
* --- AC-coupled buffer load (from sspll_acbuf.sch; MIM 4x4 ~ 36 fF ideal, Rf ~ 228k ideal) ---
.subckt acbuf in vdd vss
cc in g 36f
rf g x 228k
xp1 x g vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15 ad=0.58 as=0.58 pd=4.58 ps=4.58
xn1 x g vss vss sky130_fd_pr__nfet_01v8 w=1 l=0.15 ad=0.29 as=0.29 pd=2.58 ps=2.58
xp2 o x vdd vdd sky130_fd_pr__pfet_01v8 w=4 l=0.15 ad=1.16 as=1.16 pd=8.58 ps=8.58
xn2 o x vss vss sky130_fd_pr__nfet_01v8 w=2 l=0.15 ad=0.58 as=0.58 pd=4.58 ps=4.58
.ends
vss vss 0 0
vbuf vddbuf 0 1.8
vtn vtune 0 %VT%
ivco 0 vddvco dc %IVCO%
cdec vddvco 0 0.5p
x1 vop vom p1 m1 vtune vddvco vss dcell
x2 p1 m1 p2 m2 vtune vddvco vss dcell
x3 p2 m2 p3 m3 vtune vddvco vss dcell
x4 p3 m3 p4 m4 vtune vddvco vss dcell
x5 p4 m4 vom vop vtune vddvco vss dcell
xb1 vop vddbuf vss acbuf
xb2 vom vddbuf vss acbuf
xb3 p1 vddbuf vss acbuf
xb4 m1 vddbuf vss acbuf
xb5 p2 vddbuf vss acbuf
xb6 m2 vddbuf vss acbuf
xb7 p3 vddbuf vss acbuf
xb8 m3 vddbuf vss acbuf
xb9 p4 vddbuf vss acbuf
xb10 m4 vddbuf vss acbuf
.ic v(vddvco)=1.2 v(vop)=0 v(vom)=1.2
.tran 2p 25n 0 2p uic
.control
run
let vd = v(vop)-v(vom)
meas tran t1 when vd=0 rise=20
meas tran t2 when vd=0 rise=30
let f = 10/(t2-t1)
meas tran vdd_avg avg v(vddvco) from=t1 to=t2
meas tran vpp pp v(vop) from=t1 to=t2
print f vdd_avg vpp
.endc
.end
