* rc_corners.sp - roadmap step 73: loop-filter R and C values over the R/C corner sections and temperature.
* R: res_high_po_1p41 L = 40 um (about 9.5 kOhm); res_xhigh_po_1p41 L = 6.5 um. C: cap_mim_m3_1 30 x 30 um.
.lib "PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice" CORNER
.temp TEMP
VR a 0 dc 0 ac 1
XR1 a 0 0 sky130_fd_pr__res_high_po_1p41 l=40
VX x 0 dc 0 ac 1
XR2 x 0 0 sky130_fd_pr__res_xhigh_po_1p41 l=6.5
VC m 0 dc 0.9 ac 1
XC m 0 sky130_fd_pr__cap_mim_m3_1 w=30 l=30
.control
ac lin 1 1e6 1e6
let rh = -1/real(VR#branch)
let rx = -1/real(VX#branch)
let cm = -imag(VC#branch)/(2*pi*1e6)*1e15
echo "$&rh $&rx $&cm" > rc_out.txt
.endc
.end
