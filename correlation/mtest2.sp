.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
vr a 0 1
xn1 a a 1 0 sky130_fd_pr__nfet_01v8 w=1 l=0.15 m=1
v1 1 0 0
xn8 a a 8 0 sky130_fd_pr__nfet_01v8 w=1 l=0.15 m=8
v8 8 0 0
xh1 a 2 0 sky130_fd_pr__res_high_po_0p35 l=20 m=1
v2 2 0 0
xh8 a 3 0 sky130_fd_pr__res_high_po_0p35 l=20 m=8
v3 3 0 0
.control
op
print i(v8)/i(v1) i(v3)/i(v2)
.endc
.end
