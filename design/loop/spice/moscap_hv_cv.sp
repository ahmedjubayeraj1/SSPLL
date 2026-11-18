* moscap_hv_cv.sp - step 73 redo (5 V analog devices): small-signal C-V of the loop-filter capacitor candidates.
* X1: nfet_g5v0d10v5 used as a capacitor, gate = V_cont, drain/source/body = VSS; unit W = 10 um, L = 10 um (100 um^2).
* X2: cap_mim_m3_1 30 x 30 um (met3 / capm).  X3: cap_mim_m3_2 30 x 30 um (met4 / capm2), stackable on top of X2.
* C from the AC current at 1 MHz: C = -Im(I)/(2 pi f).
* Run: PDK_ROOT=/path/to/pdk ./run_cv_hv.sh   ->  ../data/moscap_hv_cv.csv
.lib "PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice" CORNER
.temp TEMP
V1 g 0 dc 0 ac 1
X1 0 g 0 0 sky130_fd_pr__nfet_g5v0d10v5 w=10 l=10
V2 m 0 dc 0 ac 1
X2 m 0 sky130_fd_pr__cap_mim_m3_1 w=30 l=30
V3 n 0 dc 0 ac 1
X3 n 0 sky130_fd_pr__cap_mim_m3_2 w=30 l=30
.control
echo "vg c_mos_fF c_mim1_fF c_mim2_fF" > cv_out.txt
foreach v 0 0.2 0.4 0.6 0.8 0.9 1.0 1.1 1.2 1.3 1.4 1.5 1.6 1.8 2.0 2.2 2.4 2.6 2.8 3.0 3.3
  alter V1 dc = $v
  alter V2 dc = $v
  alter V3 dc = $v
  ac lin 1 1e6 1e6
  let cm = -imag(V1#branch)/(2*pi*1e6)*1e15
  let c1 = -imag(V2#branch)/(2*pi*1e6)*1e15
  let c2 = -imag(V3#branch)/(2*pi*1e6)*1e15
  echo "$v $&cm $&c1 $&c2" >> cv_out.txt
  destroy all
end
.endc
.end
