* 5-stage pseudo-diff ring, SC=1.5, tt 27C, I=1.08m, vtune=0.9, cpar=5f, mode=run
.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.temp 27
.subckt dcell inp inm outp outm vtune vdd vss
xp1 outm inp vdd vdd sky130_fd_pr__pfet_01v8 w=12.0 l=0.15 nf=1 ad=3.4800 as=3.4800 pd=24.580 ps=24.580
xn1 outm inp vss vss sky130_fd_pr__nfet_01v8 w=6.0 l=0.15 nf=1 ad=1.7400 as=1.7400 pd=12.580 ps=12.580
xp2 outp inm vdd vdd sky130_fd_pr__pfet_01v8 w=12.0 l=0.15 nf=1 ad=3.4800 as=3.4800 pd=24.580 ps=24.580
xn2 outp inm vss vss sky130_fd_pr__nfet_01v8 w=6.0 l=0.15 nf=1 ad=1.7400 as=1.7400 pd=12.580 ps=12.580
xs1 outm vtune n1 vss sky130_fd_pr__nfet_01v8 w=2.25 l=0.15 nf=1 ad=0.6525 as=0.6525 pd=5.080 ps=5.080
xc1 vss n1 vss vss sky130_fd_pr__nfet_01v8 w=4.5 l=0.5 nf=1 ad=1.3050 as=1.3050 pd=9.580 ps=9.580
xs2 outp vtune n2 vss sky130_fd_pr__nfet_01v8 w=2.25 l=0.15 nf=1 ad=0.6525 as=0.6525 pd=5.080 ps=5.080
xc2 vss n2 vss vss sky130_fd_pr__nfet_01v8 w=4.5 l=0.5 nf=1 ad=1.3050 as=1.3050 pd=9.580 ps=9.580
xt1n inp vdd outp vss sky130_fd_pr__nfet_01v8 w=0.63 l=0.15 nf=1 ad=0.1827 as=0.1827 pd=1.840 ps=1.840
xt1p inp vss outp vdd sky130_fd_pr__pfet_01v8 w=0.63 l=0.15 nf=1 ad=0.1827 as=0.1827 pd=1.840 ps=1.840
xt2n inm vdd outm vss sky130_fd_pr__nfet_01v8 w=0.63 l=0.15 nf=1 ad=0.1827 as=0.1827 pd=1.840 ps=1.840
xt2p inm vss outm vdd sky130_fd_pr__pfet_01v8 w=0.63 l=0.15 nf=1 ad=0.1827 as=0.1827 pd=1.840 ps=1.840
cpp outp vss 5f
cpm outm vss 5f
.ends
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
vtn vtune 0 0.9
ivco 0 vddvco dc 1.08m
cdec vddvco 0 0.5p
x1 vop vom p1 m1 vtune vddvco vss dcell
x2 p1 m1 p2 m2 vtune vddvco vss dcell
x3 p2 m2 p3 m3 vtune vddvco vss dcell
x4 p3 m3 p4 m4 vtune vddvco vss dcell
x5 p4 m4 vom vop vtune vddvco vss dcell
xb_vop vop vddbuf vss acbuf
xb_p1 p1 vddbuf vss acbuf
xb_p2 p2 vddbuf vss acbuf
xb_p3 p3 vddbuf vss acbuf
xb_p4 p4 vddbuf vss acbuf
xb_vom vom vddbuf vss acbuf
xb_m1 m1 vddbuf vss acbuf
xb_m2 m2 vddbuf vss acbuf
xb_m3 m3 vddbuf vss acbuf
xb_m4 m4 vddbuf vss acbuf
.ic v(vddvco)=1.3 v(vop)=0 v(vom)=1.3
.control
option noinit
tran 1p 40n 0 1p uic
let vd = v(vop)-v(vom)
meas tran t1 when vd=0 rise=40
meas tran t2 when vd=0 rise=60
let f = 20/(t2-t1)
meas tran vdd_avg avg v(vddvco) from=t1 to=t2
meas tran ppd pp vd from=t1 to=t2
print f vdd_avg ppd

.endc
.end
