* old-design resistors and MIM caps with the pinned PDK (tt, 27 C)
.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.temp 27
v1 a 0 1
xrsr a b1 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41 mult=1
vb1 b1 0 0
xrsm a b2 0 sky130_fd_pr__res_xhigh_po_5p73 l=0.65 mult=1
vb2 b2 0 0
xrf a b3 0 sky130_fd_pr__res_xhigh_po_0p35 l=271 mult=1
vb3 b3 0 0
xr1 a b4 0 sky130_fd_pr__res_xhigh_po_0p35 l=1.36 mult=1
vb4 b4 0 0
xrpul a b5 0 sky130_fd_pr__res_xhigh_po_0p35 l=8.75 mult=1
vb5 b5 0 0
xrsm8 a b6 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41 mult=8
vb6 b6 0 0
.control
op
print 1/i(vb1) 1/i(vb2) 1/i(vb3) 1/i(vb4) 1/i(vb5) 1/i(vb6)
.endc
.end
