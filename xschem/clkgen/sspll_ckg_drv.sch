v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ckg_drv: o follows in through 2 inverters, ob is inverted through 3; the last stage of each drives the switch gates} 40 -380 0 0 0.3 0.3 {}
N 320 -50 320 50 {lab=}
N 280 -80 240 -80 {lab=}
N 240 -80 240 80 {lab=}
N 240 80 280 80 {lab=}
N 320 -110 320 -140 {lab=}
N 320 110 320 140 {lab=}
N 580 -50 580 50 {lab=}
N 540 -80 500 -80 {lab=}
N 500 -80 500 80 {lab=}
N 500 80 540 80 {lab=}
N 580 -110 580 -140 {lab=}
N 580 110 580 140 {lab=}
N 320 370 320 470 {lab=}
N 280 340 240 340 {lab=}
N 240 340 240 500 {lab=}
N 240 500 280 500 {lab=}
N 320 310 320 280 {lab=}
N 320 530 320 560 {lab=}
N 580 370 580 470 {lab=}
N 540 340 500 340 {lab=}
N 500 340 500 500 {lab=}
N 500 500 540 500 {lab=}
N 580 310 580 280 {lab=}
N 580 530 580 560 {lab=}
N 840 370 840 470 {lab=}
N 800 340 760 340 {lab=}
N 760 340 760 500 {lab=}
N 760 500 800 500 {lab=}
N 840 310 840 280 {lab=}
N 840 530 840 560 {lab=}
N 60 0 240 0 {lab=}
N 140 0 140 420 {lab=}
N 140 420 240 420 {lab=}
N 320 0 500 0 {lab=}
N 320 420 500 420 {lab=}
N 580 420 760 420 {lab=}
N 580 0 1000 0 {lab=}
N 840 420 1000 420 {lab=}
N 60 -300 140 -300 {lab=}
N 60 700 140 700 {lab=}
C {devices/ipin.sym} 60 0 0 0 {name=p_in lab=in}
C {sky130_fd_pr/pfet3_01v8.sym} 300 -80 0 0 {name=XAP L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 300 80 0 0 {name=XAN L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 320 -140 0 0 {name=l_VDD_3 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 320 140 0 0 {name=l_VSS_4 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 560 -80 0 0 {name=XBP L=0.15 W=8 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 560 80 0 0 {name=XBN L=0.15 W=4 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 580 -140 0 0 {name=l_VDD_7 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 580 140 0 0 {name=l_VSS_8 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 300 340 0 0 {name=XCP L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 300 500 0 0 {name=XCN L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 320 280 0 0 {name=l_VDD_11 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 320 560 0 0 {name=l_VSS_12 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 560 340 0 0 {name=XDP L=0.15 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 560 500 0 0 {name=XDN L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 580 280 0 0 {name=l_VDD_15 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 580 560 0 0 {name=l_VSS_16 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 820 340 0 0 {name=XEP L=0.15 W=8 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 820 500 0 0 {name=XEN L=0.15 W=4 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 840 280 0 0 {name=l_VDD_19 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 840 560 0 0 {name=l_VSS_20 sig_type=std_logic lab=VSS}
C {devices/opin.sym} 1000 0 0 1 {name=p_o lab=o}
C {devices/opin.sym} 1000 420 0 1 {name=p_ob lab=ob}
C {devices/iopin.sym} 60 -300 0 0 {name=p_VDD lab=VDD}
C {devices/lab_pin.sym} 140 -300 0 1 {name=l_VDD_24 sig_type=std_logic lab=VDD}
C {devices/iopin.sym} 60 700 0 0 {name=p_VSS lab=VSS}
C {devices/lab_pin.sym} 140 700 0 1 {name=l_VSS_26 sig_type=std_logic lab=VSS}
