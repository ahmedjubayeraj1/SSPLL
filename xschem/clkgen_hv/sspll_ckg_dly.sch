v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ckg_dly: gap-1 delay, both edges about ln2 RC + 4 gates (R: L = 6.0 um, C: 5.3 x 5.3 um). It gives the pulsed Gm about 2.4 ns after the sample to recover from the SSPD's 800 MHz tracking swing} 40 -560 0 0 0.3 0.3 {}
N 320 -50 320 50 {lab=}
N 280 -80 240 -80 {lab=}
N 240 -80 240 80 {lab=}
N 240 80 280 80 {lab=}
N 320 -110 320 -140 {lab=}
N 320 110 320 140 {lab=}
N 820 -50 820 50 {lab=}
N 780 -80 740 -80 {lab=}
N 740 -80 740 80 {lab=}
N 740 80 780 80 {lab=}
N 820 -110 820 -140 {lab=}
N 820 110 820 140 {lab=}
N 1080 -50 1080 50 {lab=}
N 1040 -80 1000 -80 {lab=}
N 1000 -80 1000 80 {lab=}
N 1000 80 1040 80 {lab=}
N 1080 -110 1080 -140 {lab=}
N 1080 110 1080 140 {lab=}
N 1340 -50 1340 50 {lab=}
N 1300 -80 1260 -80 {lab=}
N 1260 -80 1260 80 {lab=}
N 1260 80 1300 80 {lab=}
N 1340 -110 1340 -140 {lab=}
N 1340 110 1340 140 {lab=}
N 60 0 240 0 {lab=}
N 320 0 430 0 {lab=}
N 490 0 600 0 {lab=}
N 600 0 740 0 {lab=}
N 600 0 600 60 {lab=}
N 600 120 600 150 {lab=}
N 460 20 460 -10 {lab=}
N 820 0 1000 0 {lab=}
N 1080 0 1260 0 {lab=}
N 1340 0 1700 0 {lab=}
N 60 -400 140 -400 {lab=}
N 60 400 140 400 {lab=}
C {devices/ipin.sym} 60 0 0 0 {name=p_in lab=in}
C {sky130_fd_pr/pfet3_01v8.sym} 300 -80 0 0 {name=X1P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 300 80 0 0 {name=X1N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 320 -140 0 0 {name=l_VDD_3 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 320 140 0 0 {name=l_VSS_4 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 460 0 3 0 {name=XR L=6.0 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {sky130_fd_pr/cap_mim_m3_1.sym} 600 90 0 0 {name=XC W=5.3 L=5.3 MF=1 model=cap_mim_m3_1 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 800 -80 0 0 {name=X2P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 800 80 0 0 {name=X2N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 820 -140 0 0 {name=l_VDD_9 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 820 140 0 0 {name=l_VSS_10 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 1060 -80 0 0 {name=X3P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 1060 80 0 0 {name=X3N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 1080 -140 0 0 {name=l_VDD_13 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 1080 140 0 0 {name=l_VSS_14 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 1320 -80 0 0 {name=X4P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 1320 80 0 0 {name=X4N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 1340 -140 0 0 {name=l_VDD_17 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 1340 140 0 0 {name=l_VSS_18 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 600 150 0 0 {name=l_VSS_19 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 460 -10 0 0 {name=l_VSS_20 sig_type=std_logic lab=VSS}
C {devices/opin.sym} 1700 0 0 1 {name=p_out lab=out}
C {devices/iopin.sym} 60 -400 0 0 {name=p_VDD lab=VDD}
C {devices/lab_pin.sym} 140 -400 0 1 {name=l_VDD_23 sig_type=std_logic lab=VDD}
C {devices/iopin.sym} 60 400 0 0 {name=p_VSS lab=VSS}
C {devices/lab_pin.sym} 140 400 0 1 {name=l_VSS_25 sig_type=std_logic lab=VSS}
