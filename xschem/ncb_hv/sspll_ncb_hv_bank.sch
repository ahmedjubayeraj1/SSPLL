v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ncb_hv_bank: 4-bit switched capacitor bank on node n. Bit k: transmission gate XSNk / XSPk (on when ck = VDDA, ckb = 0 V) in series with the nMOS gate capacitor XCk, all 2^k units} 40 -560 0 0 0.3 0.3 {}
N 420 -230 420 -320 {lab=}
N 420 -320 680 -320 {lab=}
N 680 -320 680 -230 {lab=}
N 420 -170 420 -80 {lab=}
N 420 -80 680 -80 {lab=}
N 680 -80 680 -170 {lab=}
N 570 -320 570 -380 {lab=}
N 380 -200 320 -200 {lab=}
N 720 -200 780 -200 {lab=}
N 570 -80 570 -40 {lab=}
N 570 -40 470 -40 {lab=}
N 470 -40 470 100 {lab=}
N 470 100 530 100 {lab=}
N 570 70 570 40 {lab=}
N 570 130 570 160 {lab=}
N 1070 -230 1070 -320 {lab=}
N 1070 -320 1330 -320 {lab=}
N 1330 -320 1330 -230 {lab=}
N 1070 -170 1070 -80 {lab=}
N 1070 -80 1330 -80 {lab=}
N 1330 -80 1330 -170 {lab=}
N 1220 -320 1220 -380 {lab=}
N 1030 -200 970 -200 {lab=}
N 1370 -200 1430 -200 {lab=}
N 1220 -80 1220 -40 {lab=}
N 1220 -40 1120 -40 {lab=}
N 1120 -40 1120 100 {lab=}
N 1120 100 1180 100 {lab=}
N 1220 70 1220 40 {lab=}
N 1220 130 1220 160 {lab=}
N 1720 -230 1720 -320 {lab=}
N 1720 -320 1980 -320 {lab=}
N 1980 -320 1980 -230 {lab=}
N 1720 -170 1720 -80 {lab=}
N 1720 -80 1980 -80 {lab=}
N 1980 -80 1980 -170 {lab=}
N 1870 -320 1870 -380 {lab=}
N 1680 -200 1620 -200 {lab=}
N 2020 -200 2080 -200 {lab=}
N 1870 -80 1870 -40 {lab=}
N 1870 -40 1770 -40 {lab=}
N 1770 -40 1770 100 {lab=}
N 1770 100 1830 100 {lab=}
N 1870 70 1870 40 {lab=}
N 1870 130 1870 160 {lab=}
N 2370 -230 2370 -320 {lab=}
N 2370 -320 2630 -320 {lab=}
N 2630 -320 2630 -230 {lab=}
N 2370 -170 2370 -80 {lab=}
N 2370 -80 2630 -80 {lab=}
N 2630 -80 2630 -170 {lab=}
N 2520 -320 2520 -380 {lab=}
N 2330 -200 2270 -200 {lab=}
N 2670 -200 2730 -200 {lab=}
N 2520 -80 2520 -40 {lab=}
N 2520 -40 2420 -40 {lab=}
N 2420 -40 2420 100 {lab=}
N 2420 100 2480 100 {lab=}
N 2520 70 2520 40 {lab=}
N 2520 130 2520 160 {lab=}
N 60 400 140 400 {lab=}
N 60 450 140 450 {lab=}
N 60 500 140 500 {lab=}
N 60 550 140 550 {lab=}
N 60 600 140 600 {lab=}
N 60 650 140 650 {lab=}
N 60 700 140 700 {lab=}
N 60 750 140 750 {lab=}
N 60 800 140 800 {lab=}
N 60 900 140 900 {lab=}
N 60 950 140 950 {lab=}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 400 -200 0 0 {name=XSN0 L=0.5 W=0.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 700 -200 0 1 {name=XSP0 L=0.5 W=0.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 570 -380 0 0 {name=l_n_2 sig_type=std_logic lab=n}
C {devices/lab_pin.sym} 320 -200 0 0 {name=l_c0_3 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 780 -200 0 1 {name=l_c0b_4 sig_type=std_logic lab=c0b}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 550 100 0 0 {name=XC0 L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 570 40 0 0 {name=l_VSSA_6 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 570 160 0 0 {name=l_VSSA_7 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1050 -200 0 0 {name=XSN1 L=0.5 W=0.5 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1350 -200 0 1 {name=XSP1 L=0.5 W=0.5 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 1220 -380 0 0 {name=l_n_10 sig_type=std_logic lab=n}
C {devices/lab_pin.sym} 970 -200 0 0 {name=l_c1_11 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 1430 -200 0 1 {name=l_c1b_12 sig_type=std_logic lab=c1b}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1200 100 0 0 {name=XC1 L=0.5 W=1 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 1220 40 0 0 {name=l_VSSA_14 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1220 160 0 0 {name=l_VSSA_15 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1700 -200 0 0 {name=XSN2 L=0.5 W=0.5 nf=1 mult=4 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 2000 -200 0 1 {name=XSP2 L=0.5 W=0.5 nf=1 mult=4 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 1870 -380 0 0 {name=l_n_18 sig_type=std_logic lab=n}
C {devices/lab_pin.sym} 1620 -200 0 0 {name=l_c2_19 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 2080 -200 0 1 {name=l_c2b_20 sig_type=std_logic lab=c2b}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1850 100 0 0 {name=XC2 L=0.5 W=1 nf=1 mult=4 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 1870 40 0 0 {name=l_VSSA_22 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1870 160 0 0 {name=l_VSSA_23 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 2350 -200 0 0 {name=XSN3 L=0.5 W=0.5 nf=1 mult=8 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 2650 -200 0 1 {name=XSP3 L=0.5 W=0.5 nf=1 mult=8 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 2520 -380 0 0 {name=l_n_26 sig_type=std_logic lab=n}
C {devices/lab_pin.sym} 2270 -200 0 0 {name=l_c3_27 sig_type=std_logic lab=c3}
C {devices/lab_pin.sym} 2730 -200 0 1 {name=l_c3b_28 sig_type=std_logic lab=c3b}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 2500 100 0 0 {name=XC3 L=0.5 W=1 nf=1 mult=8 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 2520 40 0 0 {name=l_VSSA_30 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 2520 160 0 0 {name=l_VSSA_31 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 60 400 0 0 {name=p_n lab=n}
C {devices/lab_pin.sym} 140 400 0 1 {name=l_n_33 sig_type=std_logic lab=n}
C {devices/iopin.sym} 60 450 0 0 {name=p_c0 lab=c0}
C {devices/lab_pin.sym} 140 450 0 1 {name=l_c0_35 sig_type=std_logic lab=c0}
C {devices/iopin.sym} 60 500 0 0 {name=p_c1 lab=c1}
C {devices/lab_pin.sym} 140 500 0 1 {name=l_c1_37 sig_type=std_logic lab=c1}
C {devices/iopin.sym} 60 550 0 0 {name=p_c2 lab=c2}
C {devices/lab_pin.sym} 140 550 0 1 {name=l_c2_39 sig_type=std_logic lab=c2}
C {devices/iopin.sym} 60 600 0 0 {name=p_c3 lab=c3}
C {devices/lab_pin.sym} 140 600 0 1 {name=l_c3_41 sig_type=std_logic lab=c3}
C {devices/iopin.sym} 60 650 0 0 {name=p_c0b lab=c0b}
C {devices/lab_pin.sym} 140 650 0 1 {name=l_c0b_43 sig_type=std_logic lab=c0b}
C {devices/iopin.sym} 60 700 0 0 {name=p_c1b lab=c1b}
C {devices/lab_pin.sym} 140 700 0 1 {name=l_c1b_45 sig_type=std_logic lab=c1b}
C {devices/iopin.sym} 60 750 0 0 {name=p_c2b lab=c2b}
C {devices/lab_pin.sym} 140 750 0 1 {name=l_c2b_47 sig_type=std_logic lab=c2b}
C {devices/iopin.sym} 60 800 0 0 {name=p_c3b lab=c3b}
C {devices/lab_pin.sym} 140 800 0 1 {name=l_c3b_49 sig_type=std_logic lab=c3b}
C {devices/iopin.sym} 60 900 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 900 0 1 {name=l_VDDA_51 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 950 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 950 0 1 {name=l_VSSA_53 sig_type=std_logic lab=VSSA}
