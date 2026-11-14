v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_vco_dcell: pseudo-differential delay cell (the ring uses 5)} 40 -520 0 0 0.4 0.4 {}
T {left: inp -> outm   right: inm -> outp   TG1: inp -> outp   TG2: inm -> outm (always on)} 40 -470 0 0 0.25 0.25 {}
T {fine tuning: vtune turns on S, which hangs MOS cap C on the output (higher vtune = lower f)} 40 -440 0 0 0.25 0.25 {}
N 60 -320 700 -320 {lab=}
N 700 -320 1340 -320 {lab=}
N 60 300 700 300 {lab=}
N 700 300 1340 300 {lab=}
N 60 230 700 230 {lab=}
N 700 230 1340 230 {lab=}
N 240 -230 240 -320 {lab=}
N 240 -170 240 -130 {lab=}
N 240 -130 240 -90 {lab=}
N 240 -30 240 300 {lab=}
N 200 -200 150 -200 {lab=}
N 150 -200 150 -130 {lab=}
N 150 -130 150 -60 {lab=}
N 150 -60 200 -60 {lab=}
N 40 -130 150 -130 {lab=}
N 240 -130 360 -130 {lab=}
N 360 -130 500 -130 {lab=}
N 500 -130 500 -90 {lab=}
N 460 -60 420 -60 {lab=}
N 420 -60 420 230 {lab=}
N 500 -30 500 40 {lab=}
N 500 40 440 40 {lab=}
N 440 40 440 110 {lab=}
N 440 110 460 110 {lab=}
N 500 80 500 60 {lab=}
N 500 60 620 60 {lab=}
N 620 60 620 160 {lab=}
N 620 160 620 300 {lab=}
N 500 140 500 300 {lab=}
N 1160 -230 1160 -320 {lab=}
N 1160 -170 1160 -130 {lab=}
N 1160 -130 1160 -90 {lab=}
N 1160 -30 1160 300 {lab=}
N 1200 -200 1250 -200 {lab=}
N 1250 -200 1250 -130 {lab=}
N 1250 -130 1250 -60 {lab=}
N 1250 -60 1200 -60 {lab=}
N 1360 -130 1250 -130 {lab=}
N 1160 -130 1040 -130 {lab=}
N 1040 -130 900 -130 {lab=}
N 900 -130 900 -90 {lab=}
N 940 -60 980 -60 {lab=}
N 980 -60 980 230 {lab=}
N 900 -30 900 40 {lab=}
N 900 40 960 40 {lab=}
N 960 40 960 110 {lab=}
N 960 110 940 110 {lab=}
N 900 80 900 60 {lab=}
N 900 60 780 60 {lab=}
N 780 60 780 160 {lab=}
N 780 160 780 300 {lab=}
N 900 140 900 300 {lab=}
N 500 430 500 410 {lab=}
N 760 430 760 410 {lab=}
N 40 -130 40 410 {lab=}
N 40 410 500 410 {lab=}
N 500 410 760 410 {lab=}
N 500 490 500 520 {lab=}
N 760 490 760 520 {lab=}
N 500 520 760 520 {lab=}
N 760 520 1040 520 {lab=}
N 1040 520 1040 -130 {lab=}
N 460 460 400 460 {lab=}
N 720 460 660 460 {lab=}
N 900 670 900 650 {lab=}
N 640 670 640 650 {lab=}
N 1360 -130 1360 650 {lab=}
N 1360 650 900 650 {lab=}
N 900 650 640 650 {lab=}
N 900 730 900 760 {lab=}
N 640 730 640 760 {lab=}
N 900 760 640 760 {lab=}
N 640 760 360 760 {lab=}
N 360 760 360 -130 {lab=}
N 940 700 1000 700 {lab=}
N 680 700 740 700 {lab=}
N 360 820 360 760 {lab=}
N 1040 820 1040 520 {lab=}
C {devices/iopin.sym} 60 -320 0 0 {name=p_VDD lab=VDD}
C {devices/iopin.sym} 60 300 0 0 {name=p_VSS lab=VSS}
C {devices/ipin.sym} 60 230 0 0 {name=p_vtune lab=vtune}
C {sky130_fd_pr/pfet3_01v8.sym} 220 -200 0 0 {name=XP1 L=0.15 W=12 nf=4 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 220 -60 0 0 {name=XN1 L=0.15 W=6 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_01v8.sym} 480 -60 0 0 {name=XS1 L=0.3 W=4.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_01v8.sym} 480 110 0 0 {name=XC1 L=0.5 W=4.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/ipin.sym} 40 -130 0 0 {name=p_inp lab=inp}
C {sky130_fd_pr/pfet3_01v8.sym} 1180 -200 0 1 {name=XP2 L=0.15 W=12 nf=4 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 1180 -60 0 1 {name=XN2 L=0.15 W=6 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_01v8.sym} 920 -60 0 1 {name=XS2 L=0.3 W=4.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_01v8.sym} 920 110 0 1 {name=XC2 L=0.5 W=4.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/ipin.sym} 1360 -130 0 1 {name=p_inm lab=inm}
C {sky130_fd_pr/nfet3_01v8.sym} 480 460 0 0 {name=XT1N L=0.3 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 740 460 0 0 {name=XT1P L=0.15 W=0.63 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {devices/lab_pin.sym} 400 460 0 1 {name=l_VDD_15 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 660 460 0 1 {name=l_VSS_16 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/nfet3_01v8.sym} 920 700 0 1 {name=XT2N L=0.3 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 660 700 0 1 {name=XT2P L=0.15 W=0.63 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {devices/lab_pin.sym} 1000 700 0 0 {name=l_VDD_19 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 740 700 0 0 {name=l_VSS_20 sig_type=std_logic lab=VSS}
C {devices/opin.sym} 360 820 0 0 {name=p_outm lab=outm}
C {devices/opin.sym} 1040 820 0 1 {name=p_outp lab=outp}
