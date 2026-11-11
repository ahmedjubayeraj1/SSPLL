.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
vr a 0 1
xa a 1 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41
v1 1 0 0
xb a 2 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41 m=8
v2 2 0 0
xc a 3 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41 mult=8 m=8
v3 3 0 0
xd a 4 0 sky130_fd_pr__res_high_po_0p35 l=20 mult=8 m=8
v4 4 0 0
xe a 5 0 sky130_fd_pr__res_high_po_0p35 l=20
v5 5 0 0
.control
op
print i(v2)/i(v1) i(v3)/i(v1) i(v4)/i(v5)
.endc
.end
