* Poly resistor characterization (pinned sky130A 1689ac3f), tt, 27 C
.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.param L1=10 L2=20
vb sub 0 0
* xhigh_po, 5 widths, two lengths each (1 V across, current read back)
v1a a1 0 1
xr1a a1 0 sub sky130_fd_pr__res_xhigh_po_0p35 l={L1}
v1b b1 0 1
xr1b b1 0 sub sky130_fd_pr__res_xhigh_po_0p35 l={L2}
v2a a2 0 1
xr2a a2 0 sub sky130_fd_pr__res_xhigh_po_0p69 l={L1}
v2b b2 0 1
xr2b b2 0 sub sky130_fd_pr__res_xhigh_po_0p69 l={L2}
v3a a3 0 1
xr3a a3 0 sub sky130_fd_pr__res_xhigh_po_1p41 l={L1}
v3b b3 0 1
xr3b b3 0 sub sky130_fd_pr__res_xhigh_po_1p41 l={L2}
v4a a4 0 1
xr4a a4 0 sub sky130_fd_pr__res_xhigh_po_2p85 l={L1}
v4b b4 0 1
xr4b b4 0 sub sky130_fd_pr__res_xhigh_po_2p85 l={L2}
v5a a5 0 1
xr5a a5 0 sub sky130_fd_pr__res_xhigh_po_5p73 l={L1}
v5b b5 0 1
xr5b b5 0 sub sky130_fd_pr__res_xhigh_po_5p73 l={L2}
* high_po, 5 widths
v6a a6 0 1
xr6a a6 0 sub sky130_fd_pr__res_high_po_0p35 l={L1}
v6b b6 0 1
xr6b b6 0 sub sky130_fd_pr__res_high_po_0p35 l={L2}
v7a a7 0 1
xr7a a7 0 sub sky130_fd_pr__res_high_po_0p69 l={L1}
v7b b7 0 1
xr7b b7 0 sub sky130_fd_pr__res_high_po_0p69 l={L2}
v8a a8 0 1
xr8a a8 0 sub sky130_fd_pr__res_high_po_1p41 l={L1}
v8b b8 0 1
xr8b b8 0 sub sky130_fd_pr__res_high_po_1p41 l={L2}
v9a a9 0 1
xr9a a9 0 sub sky130_fd_pr__res_high_po_2p85 l={L1}
v9b b9 0 1
xr9b b9 0 sub sky130_fd_pr__res_high_po_2p85 l={L2}
v10a a10 0 1
xr10a a10 0 sub sky130_fd_pr__res_high_po_5p73 l={L1}
v10b b10 0 1
xr10b b10 0 sub sky130_fd_pr__res_high_po_5p73 l={L2}
.control
op
let names = 'x'
echo "RES name ra(L=10) rb(L=20)"
foreach i 1 2 3 4 5 6 7 8 9 10
  let ra = -1/v$i{a}#branch
  let rb = -1/v$i{b}#branch
  echo "RES $i $&ra $&rb"
end
.endc
.end
