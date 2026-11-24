v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ckg_hlatch: NOR latch, q set by s (ckg, the Gm pulse) and reset by r (cks = 1 while refclk is low); out = q AND NOT s rises when the Gm pulse ends and triggers the hold pulser} 40 -520 0 0 0.3 0.3 {}
T {cross-coupled nets q and qb and the second use of s are joined by name (labels)} 40 -470 0 0 0.25 0.25 {}
N 420 -150 420 -100 {lab=}
N 420 -40 420 60 {lab=}
N 420 20 680 20 {lab=}
N 680 20 680 60 {lab=}
N 420 -210 420 -240 {lab=}
N 420 120 420 150 {lab=}
N 680 120 680 150 {lab=}
N 380 -180 300 -180 {lab=}
N 300 -180 300 90 {lab=}
N 300 90 380 90 {lab=}
N 380 -70 340 -70 {lab=}
N 340 -70 340 190 {lab=}
N 340 190 600 190 {lab=}
N 600 190 600 90 {lab=}
N 600 90 640 90 {lab=}
N 420 750 420 800 {lab=}
N 420 860 420 960 {lab=}
N 420 920 680 920 {lab=}
N 680 920 680 960 {lab=}
N 420 690 420 660 {lab=}
N 420 1020 420 1050 {lab=}
N 680 1020 680 1050 {lab=}
N 380 720 300 720 {lab=}
N 300 720 300 990 {lab=}
N 300 990 380 990 {lab=}
N 380 830 340 830 {lab=}
N 340 830 340 1090 {lab=}
N 340 1090 600 1090 {lab=}
N 600 1090 600 990 {lab=}
N 600 990 640 990 {lab=}
N 1420 300 1420 350 {lab=}
N 1420 410 1420 510 {lab=}
N 1420 470 1680 470 {lab=}
N 1680 470 1680 510 {lab=}
N 1420 240 1420 210 {lab=}
N 1420 570 1420 600 {lab=}
N 1680 570 1680 600 {lab=}
N 1380 270 1300 270 {lab=}
N 1300 270 1300 540 {lab=}
N 1300 540 1380 540 {lab=}
N 1380 380 1340 380 {lab=}
N 1340 380 1340 640 {lab=}
N 1340 640 1600 640 {lab=}
N 1600 640 1600 540 {lab=}
N 1600 540 1640 540 {lab=}
N 60 -120 300 -120 {lab=}
N 60 780 300 780 {lab=}
N 340 150 220 150 {lab=}
N 340 1050 220 1050 {lab=}
N 1300 330 1220 330 {lab=}
N 1340 600 1220 600 {lab=}
N 420 0 980 0 {lab=}
N 420 900 980 900 {lab=}
N 1420 450 1700 450 {lab=}
N 60 -400 140 -400 {lab=}
N 60 1300 140 1300 {lab=}
C {sky130_fd_pr/pfet3_01v8.sym} 400 -180 0 0 {name=X1PA L=0.15 W=1.68 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/pfet3_01v8.sym} 400 -70 0 0 {name=X1PB L=0.15 W=1.68 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 400 90 0 0 {name=X1NA L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {sky130_fd_pr/nfet3_01v8.sym} 660 90 0 0 {name=X1NB L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {devices/lab_pin.sym} 420 -240 0 0 {name=l_VDD_4 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 420 150 0 0 {name=l_VSS_5 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 680 150 0 0 {name=l_VSS_6 sig_type=std_logic lab=VSSD}
C {sky130_fd_pr/pfet3_01v8.sym} 400 720 0 0 {name=X2PA L=0.15 W=1.68 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/pfet3_01v8.sym} 400 830 0 0 {name=X2PB L=0.15 W=1.68 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 400 990 0 0 {name=X2NA L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {sky130_fd_pr/nfet3_01v8.sym} 660 990 0 0 {name=X2NB L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {devices/lab_pin.sym} 420 660 0 0 {name=l_VDD_11 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 420 1050 0 0 {name=l_VSS_12 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 680 1050 0 0 {name=l_VSS_13 sig_type=std_logic lab=VSSD}
C {sky130_fd_pr/pfet3_01v8.sym} 1400 270 0 0 {name=X3PA L=0.15 W=1.68 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/pfet3_01v8.sym} 1400 380 0 0 {name=X3PB L=0.15 W=1.68 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 1400 540 0 0 {name=X3NA L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {sky130_fd_pr/nfet3_01v8.sym} 1660 540 0 0 {name=X3NB L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {devices/lab_pin.sym} 1420 210 0 0 {name=l_VDD_18 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1420 600 0 0 {name=l_VSS_19 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 1680 600 0 0 {name=l_VSS_20 sig_type=std_logic lab=VSSD}
C {devices/ipin.sym} 60 -120 0 0 {name=p_r lab=r}
C {devices/ipin.sym} 60 780 0 0 {name=p_s lab=s}
C {devices/lab_pin.sym} 220 150 0 0 {name=l_qb_23 sig_type=std_logic lab=qb}
C {devices/lab_pin.sym} 220 1050 0 0 {name=l_q_24 sig_type=std_logic lab=q}
C {devices/lab_pin.sym} 1220 330 0 0 {name=l_qb_25 sig_type=std_logic lab=qb}
C {devices/lab_pin.sym} 1220 600 0 0 {name=l_s_26 sig_type=std_logic lab=s}
C {devices/lab_pin.sym} 980 0 0 1 {name=l_q_27 sig_type=std_logic lab=q}
C {devices/lab_pin.sym} 980 900 0 1 {name=l_qb_28 sig_type=std_logic lab=qb}
C {devices/opin.sym} 1700 450 0 1 {name=p_out lab=out}
C {devices/iopin.sym} 60 -400 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 140 -400 0 1 {name=l_VDD_31 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 60 1300 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 140 1300 0 1 {name=l_VSS_33 sig_type=std_logic lab=VSSD}
