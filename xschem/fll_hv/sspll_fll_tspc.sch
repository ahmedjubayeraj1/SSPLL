v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_fll_tspc: TSPC flip-flop with D = qb, so it divides ck by 2. Stage 1: x = not qb while ck is low;} 40 -460 0 0 0.3 0.3 {}
T {stage 2 precharges y while ck is low, y = not x after the rising edge; stage 3: qb = not y while ck is high; q = not qb.} 40 -420 0 0 0.3 0.3 {}
N 420 -250 420 -290 {lab=}
N 420 -190 420 -130 {lab=}
N 420 -70 420 0 {lab=}
N 420 0 420 70 {lab=}
N 420 130 420 170 {lab=}
N 380 -220 320 -220 {lab=}
N 380 -100 320 -100 {lab=}
N 380 100 320 100 {lab=}
N 670 -130 670 -170 {lab=}
N 670 -70 670 0 {lab=}
N 670 0 670 70 {lab=}
N 670 130 670 190 {lab=}
N 670 250 670 290 {lab=}
N 420 0 540 0 {lab=}
N 540 0 540 100 {lab=}
N 540 100 630 100 {lab=}
N 630 -100 570 -100 {lab=}
N 630 220 570 220 {lab=}
N 920 -130 920 -170 {lab=}
N 920 -70 920 0 {lab=}
N 920 0 920 70 {lab=}
N 920 130 920 190 {lab=}
N 920 250 920 290 {lab=}
N 670 0 790 0 {lab=}
N 790 0 790 -100 {lab=}
N 790 -100 880 -100 {lab=}
N 790 0 790 220 {lab=}
N 790 220 880 220 {lab=}
N 880 100 820 100 {lab=}
N 920 0 1050 0 {lab=}
N 1050 0 1050 -100 {lab=}
N 1050 -100 1130 -100 {lab=}
N 1050 0 1050 100 {lab=}
N 1050 100 1130 100 {lab=}
N 1170 -130 1170 -170 {lab=}
N 1170 130 1170 170 {lab=}
N 1170 -70 1170 0 {lab=}
N 1170 0 1170 70 {lab=}
N 1170 0 1350 0 {lab=}
N 100 400 180 400 {lab=}
N 100 -350 180 -350 {lab=}
N 100 500 180 500 {lab=}
N 100 560 180 560 {lab=}
C {sky130_fd_pr/pfet3_01v8.sym} 400 -220 0 0 {name=XP1A L=0.15 W=1.26 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/pfet3_01v8.sym} 400 -100 0 0 {name=XP1B L=0.15 W=1.26 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 400 100 0 0 {name=XN1 L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {devices/lab_pin.sym} 420 -290 0 0 {name=l_VDDD_3 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 420 170 0 0 {name=l_VSSD_4 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 320 -220 0 0 {name=l_qb_5 sig_type=std_logic lab=qb}
C {devices/lab_pin.sym} 320 -100 0 0 {name=l_ck_6 sig_type=std_logic lab=ck}
C {devices/lab_pin.sym} 320 100 0 0 {name=l_qb_7 sig_type=std_logic lab=qb}
C {sky130_fd_pr/pfet3_01v8.sym} 650 -100 0 0 {name=XP2 L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 650 100 0 0 {name=XN2A L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {sky130_fd_pr/nfet3_01v8.sym} 650 220 0 0 {name=XN2B L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {devices/lab_pin.sym} 670 -170 0 0 {name=l_VDDD_11 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 670 290 0 0 {name=l_VSSD_12 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 540 0 0 0 {name=l_x_13 sig_type=std_logic lab=x}
C {devices/lab_pin.sym} 570 -100 0 0 {name=l_ck_14 sig_type=std_logic lab=ck}
C {devices/lab_pin.sym} 570 220 0 0 {name=l_ck_15 sig_type=std_logic lab=ck}
C {sky130_fd_pr/pfet3_01v8.sym} 900 -100 0 0 {name=XP3 L=0.15 W=1.26 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 900 100 0 0 {name=XN3A L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {sky130_fd_pr/nfet3_01v8.sym} 900 220 0 0 {name=XN3B L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {devices/lab_pin.sym} 920 -170 0 0 {name=l_VDDD_19 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 920 290 0 0 {name=l_VSSD_20 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 790 0 0 0 {name=l_y_21 sig_type=std_logic lab=y}
C {devices/lab_pin.sym} 820 100 0 0 {name=l_ck_22 sig_type=std_logic lab=ck}
C {sky130_fd_pr/pfet3_01v8.sym} 1150 -100 0 0 {name=XIP L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 1150 100 0 0 {name=XIN L=0.15 W=0.65 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {devices/lab_pin.sym} 1170 -170 0 0 {name=l_VDDD_25 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1170 170 0 0 {name=l_VSSD_26 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 1050 0 0 1 {name=l_qb_27 sig_type=std_logic lab=qb}
C {devices/opin.sym} 1350 0 0 1 {name=p_q lab=q}
C {devices/opin.sym} 100 400 0 0 {name=p_qb lab=qb}
C {devices/lab_pin.sym} 180 400 0 1 {name=l_qb_30 sig_type=std_logic lab=qb}
C {devices/ipin.sym} 100 -350 0 0 {name=p_ck lab=ck}
C {devices/lab_pin.sym} 180 -350 0 1 {name=l_ck_32 sig_type=std_logic lab=ck}
C {devices/iopin.sym} 100 500 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 180 500 0 1 {name=l_VDDD_34 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 100 560 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 180 560 0 1 {name=l_VSSD_36 sig_type=std_logic lab=VSSD}
