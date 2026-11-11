* does m= multiply subcircuit instances in ngspice-42 with these models?
.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
vr a 0 1
xr6 a 6 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41 mult=1 m=1
v6 6 0 0
xr7 a 7 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41 mult=8 m=8
v7 7 0 0
xn1 a a 0 0 sky130_fd_pr__nfet_01v8 w=1 l=0.15 m=1
xn8 a a 8 0 sky130_fd_pr__nfet_01v8 w=1 l=0.15 m=8
v8 8 0 0
vc c 0 dc 0 ac 1
xc2 c 12 sky130_fd_pr__cap_mim_m3_1 w=20 l=20 mf=1 m=1
vc2 12 0 0
xc4 c 14 sky130_fd_pr__cap_mim_m3_1 w=20 l=20 mf=2
vc4 14 0 0
xc5 c 15 sky130_fd_pr__cap_mim_m3_1 w=20 l=20 mf=2 m=2
vc5 15 0 0
.control
op
print 1/i(v6) 1/i(v7) i(v8)
ac lin 1 1meg 1meg
let c2 = imag(i(vc2))/(2*pi*1e6)*1e15
let c4 = imag(i(vc4))/(2*pi*1e6)*1e15
let c5 = imag(i(vc5))/(2*pi*1e6)*1e15
print c2 c4 c5
.endc
.end
