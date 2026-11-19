v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ckg_edges_h: stop rises ln2 RC + 2 gates after in rises (R: L = 6.0 um, C: 6.0 x 6.0 um); pls = in AND NOT stop = NOR(inb, stop), the 1.8 V pulse} 40 -560 0 0 0.3 0.3 {}
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
N 320 430 320 530 {lab=}
N 280 400 240 400 {lab=}
N 240 400 240 560 {lab=}
N 240 560 280 560 {lab=}
N 320 370 320 340 {lab=}
N 320 590 320 620 {lab=}
N 60 0 240 0 {lab=}
N 140 0 140 480 {lab=}
N 140 480 240 480 {lab=}
N 320 0 430 0 {lab=}
N 490 0 600 0 {lab=}
N 600 0 740 0 {lab=}
N 600 0 600 60 {lab=}
N 600 120 600 150 {lab=}
N 460 20 460 -10 {lab=}
N 1280 150 1280 200 {lab=}
N 1280 260 1280 360 {lab=}
N 1280 320 1540 320 {lab=}
N 1540 320 1540 360 {lab=}
N 1280 90 1280 60 {lab=}
N 1280 420 1280 450 {lab=}
N 1540 420 1540 450 {lab=}
N 1240 120 1160 120 {lab=}
N 1160 120 1160 390 {lab=}
N 1160 390 1240 390 {lab=}
N 1240 230 1200 230 {lab=}
N 1200 230 1200 490 {lab=}
N 1200 490 1460 490 {lab=}
N 1460 490 1460 390 {lab=}
N 1460 390 1500 390 {lab=}
N 320 480 1100 480 {lab=}
N 1100 480 1100 180 {lab=}
N 1100 180 1160 180 {lab=}
N 820 0 1000 0 {lab=}
N 1000 0 1000 450 {lab=}
N 1000 450 1120 450 {lab=}
N 1120 450 1200 450 {lab=}
N 1000 0 1700 0 {lab=}
N 1280 300 1700 300 {lab=}
N 60 -400 140 -400 {lab=}
N 60 760 140 760 {lab=}
C {devices/ipin.sym} 60 0 0 0 {name=p_in lab=in}
C {sky130_fd_pr/pfet3_01v8.sym} 300 -80 0 0 {name=X2P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 300 80 0 0 {name=X2N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 320 -140 0 0 {name=l_VDD_3 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 320 140 0 0 {name=l_VSS_4 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 460 0 3 0 {name=XR L=6.0 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {sky130_fd_pr/cap_mim_m3_1.sym} 600 90 0 0 {name=XC W=6.0 L=6.0 MF=1 model=cap_mim_m3_1 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 800 -80 0 0 {name=X3P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 800 80 0 0 {name=X3N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 820 -140 0 0 {name=l_VDD_9 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 820 140 0 0 {name=l_VSS_10 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 300 400 0 0 {name=X1P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 300 560 0 0 {name=X1N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 320 340 0 0 {name=l_VDD_13 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 320 620 0 0 {name=l_VSS_14 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 600 150 0 0 {name=l_VSS_15 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 460 -10 0 0 {name=l_VSS_16 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 1260 120 0 0 {name=X4PA L=0.15 W=1.68 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/pfet3_01v8.sym} 1260 230 0 0 {name=X4PB L=0.15 W=1.68 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 1260 390 0 0 {name=X4NA L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_01v8.sym} 1520 390 0 0 {name=X4NB L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 1280 60 0 0 {name=l_VDD_21 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 1280 450 0 0 {name=l_VSS_22 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1540 450 0 0 {name=l_VSS_23 sig_type=std_logic lab=VSS}
C {devices/opin.sym} 1700 0 0 1 {name=p_stop lab=stop}
C {devices/opin.sym} 1700 300 0 1 {name=p_pls lab=pls}
C {devices/iopin.sym} 60 -400 0 0 {name=p_VDD lab=VDD}
C {devices/lab_pin.sym} 140 -400 0 1 {name=l_VDD_27 sig_type=std_logic lab=VDD}
C {devices/iopin.sym} 60 760 0 0 {name=p_VSS lab=VSS}
C {devices/lab_pin.sym} 140 760 0 1 {name=l_VSS_29 sig_type=std_logic lab=VSS}
