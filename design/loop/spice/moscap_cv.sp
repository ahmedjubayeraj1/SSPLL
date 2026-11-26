* moscap_cv.sp - small-signal C-V of the loop-filter capacitors (frozen SKY130 PDK).
* X1: nfet_01v8 used as a capacitor, gate = V_cont, drain/source/body = VSS; unit W = 10 um, L = 10 um (100 um^2).
* X2: cap_mim_m3_1 30 x 30 um tile. C from the AC current at 1 MHz: C = Im(I)/(2 pi f).
* Run: PDK_ROOT=/path/to/pdk ./run_cv.sh   ->  ../../../design/loop/data/moscap_cv.csv
.lib "PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice" CORNER
.temp TEMP
.param vg=0.9
V1 g 0 dc {vg} ac 1
X1 0 g 0 0 sky130_fd_pr__nfet_01v8 w=10 l=10
V2 m 0 dc {vg} ac 1
X2 m 0 sky130_fd_pr__cap_mim_m3_1 w=30 l=30
.control
set wr_singlescale
let vs = 0
echo "vg c_mos_fF c_mim_fF" > cv_out.txt
foreach v 0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8
  alter V1 dc = $v
  alter V2 dc = $v
  ac lin 1 1e6 1e6
  let cm = -imag(V1#branch)/(2*pi*1e6)*1e15
  let ci = -imag(V2#branch)/(2*pi*1e6)*1e15
  echo "$v $&cm $&ci" >> cv_out.txt
  destroy all
end
.endc
.end
