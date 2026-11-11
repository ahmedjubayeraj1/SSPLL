* corr_rc.sp - reference values of SKY130 R and C as ngspice + open_pdks 1689ac3f simulate them.
* Same benches must be repeated in Spectre with the Cadence kit (see README.md). tt corner.
.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.param vr=1 tk=27
.temp 27
* resistors: R = V / I  (sub terminal at 0 V)
vr a 0 {vr}
xr1 a 1 0 sky130_fd_pr__res_xhigh_po_0p35 l=20 mult=1 m=1
v1 1 0 0
xr2 a 2 0 sky130_fd_pr__res_xhigh_po_0p35 l=1.36 mult=1 m=1
v2 2 0 0
xr3 a 3 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41 mult=1 m=1
v3 3 0 0
xr4 a 4 0 sky130_fd_pr__res_xhigh_po_5p73 l=0.65 mult=1 m=1
v4 4 0 0
xr5 a 5 0 sky130_fd_pr__res_high_po_0p35 l=20 mult=1 m=1
v5 5 0 0
xr6 a 6 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41 mult=8
v6 6 0 0
xr7 a 7 0 sky130_fd_pr__res_xhigh_po_5p73 l=5.41 mult=8 m=8
v7 7 0 0
* MIM caps at 1 MHz: C = Im(I)/(2 pi f)
vc c 0 dc 0 ac 1
xc1 c 11 sky130_fd_pr__cap_mim_m3_1 w=5 l=5 mf=1 m=1
vc1 11 0 0
xc2 c 12 sky130_fd_pr__cap_mim_m3_1 w=20 l=20 mf=1 m=1
vc2 12 0 0
xc3 c 13 sky130_fd_pr__cap_mim_m3_1 w=30 l=30 mf=1 m=1
vc3 13 0 0
xc4 c 14 sky130_fd_pr__cap_mim_m3_1 w=20 l=20 mf=2
vc4 14 0 0
xc5 c 15 sky130_fd_pr__cap_mim_m3_1 w=20 l=20 mf=2 m=2
vc5 15 0 0
.control
foreach t 27 110
  set temp = $t
  option temp = $t
  foreach v 0.05 1.0
    alterparam vr = $v
    reset
    op
    echo "T=$t V=$v  R(Ohm): xhigh0p35_L20 xhigh0p35_L1.36 xhigh5p73_L5.41 xhigh5p73_L0.65 high0p35_L20 | 8x(mult only) 8x(mult+m)"
    print $v/i(v1) $v/i(v2) $v/i(v3) $v/i(v4) $v/i(v5) $v/i(v6) $v/i(v7)
  end
end
option temp = 27
ac lin 1 1meg 1meg
echo "C(fF) at 1 MHz: 5x5 20x20 30x30 | 20x20 mf=2 only | 20x20 mf=2 m=2"
print imag(i(vc1))/(2*pi*1e6)*1e15 imag(i(vc2))/(2*pi*1e6)*1e15 imag(i(vc3))/(2*pi*1e6)*1e15 imag(i(vc4))/(2*pi*1e6)*1e15 imag(i(vc5))/(2*pi*1e6)*1e15
.endc
.end
