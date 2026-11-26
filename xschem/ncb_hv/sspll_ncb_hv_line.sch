v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ncb_hv_line: input inverter X0 (load on the ring's clock), starved inverters x1 / x2 with a capacitor bank on each output (a, b), output inverter X3. Each input edge passes two controlled transitions} 40 -560 0 0 0.3 0.3 {}
N 320 -90 320 10 {lab=}
N 280 -120 240 -120 {lab=}
N 240 -120 240 40 {lab=}
N 240 40 280 40 {lab=}
N 320 -150 320 -180 {lab=}
N 320 70 320 100 {lab=}
N 240 -40 160 -40 {lab=}
N 320 -40 700 -40 {lab=}
N 700 0 640 0 {lab=}
N 700 40 640 40 {lab=}
N 760 -90 760 -120 {lab=}
N 760 90 760 120 {lab=}
N 1800 0 1740 0 {lab=}
N 1800 40 1740 40 {lab=}
N 1860 -90 1860 -120 {lab=}
N 1860 90 1860 120 {lab=}
N 900 0 1300 0 {lab=}
N 1300 0 1300 340 {lab=}
N 1300 340 1450 340 {lab=}
N 1300 0 1300 -40 {lab=}
N 1300 -40 1800 -40 {lab=}
N 2000 0 2400 0 {lab=}
N 2400 0 2400 340 {lab=}
N 2400 340 2550 340 {lab=}
N 1450 380 1390 380 {lab=}
N 1450 420 1390 420 {lab=}
N 1450 460 1390 460 {lab=}
N 1450 500 1390 500 {lab=}
N 1450 540 1390 540 {lab=}
N 1450 580 1390 580 {lab=}
N 1450 620 1390 620 {lab=}
N 1450 660 1390 660 {lab=}
N 1510 290 1510 260 {lab=}
N 1510 710 1510 740 {lab=}
N 2550 380 2490 380 {lab=}
N 2550 420 2490 420 {lab=}
N 2550 460 2490 460 {lab=}
N 2550 500 2490 500 {lab=}
N 2550 540 2490 540 {lab=}
N 2550 580 2490 580 {lab=}
N 2550 620 2490 620 {lab=}
N 2550 660 2490 660 {lab=}
N 2610 290 2610 260 {lab=}
N 2610 710 2610 740 {lab=}
N 2820 100 2820 200 {lab=}
N 2780 70 2740 70 {lab=}
N 2740 70 2740 230 {lab=}
N 2740 230 2780 230 {lab=}
N 2820 40 2820 10 {lab=}
N 2820 260 2820 290 {lab=}
N 2400 150 2740 150 {lab=}
N 2820 150 3100 150 {lab=}
N 60 900 140 900 {lab=}
N 60 950 140 950 {lab=}
N 60 1000 140 1000 {lab=}
N 60 1050 140 1050 {lab=}
N 60 1100 140 1100 {lab=}
N 60 1150 140 1150 {lab=}
N 60 1200 140 1200 {lab=}
N 60 1250 140 1250 {lab=}
N 60 1300 140 1300 {lab=}
N 60 1350 140 1350 {lab=}
N 60 1400 140 1400 {lab=}
N 60 1500 140 1500 {lab=}
N 60 1550 140 1550 {lab=}
C {sspll_ncb_hv_sinv.sym} 800 0 0 0 {name=x1}
C {sspll_ncb_hv_sinv.sym} 1900 0 0 0 {name=x2}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 300 -120 0 0 {name=X0P L=0.5 W=2.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 300 40 0 0 {name=X0N L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 320 -180 0 0 {name=l_VDDA_4 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 320 100 0 0 {name=l_VSSA_5 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 160 -40 0 0 {name=l_in_6 sig_type=std_logic lab=in}
C {devices/lab_pin.sym} 640 0 0 0 {name=l_nb_7 sig_type=std_logic lab=nb}
C {devices/lab_pin.sym} 640 40 0 0 {name=l_pd_8 sig_type=std_logic lab=pd}
C {devices/lab_pin.sym} 760 -120 0 0 {name=l_VDDA_9 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 760 120 0 0 {name=l_VSSA_10 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1740 0 0 0 {name=l_nb_11 sig_type=std_logic lab=nb}
C {devices/lab_pin.sym} 1740 40 0 0 {name=l_pd_12 sig_type=std_logic lab=pd}
C {devices/lab_pin.sym} 1860 -120 0 0 {name=l_VDDA_13 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1860 120 0 0 {name=l_VSSA_14 sig_type=std_logic lab=VSSA}
C {sspll_ncb_hv_bank.sym} 1550 500 0 0 {name=xba}
C {sspll_ncb_hv_bank.sym} 2650 500 0 0 {name=xbb}
C {devices/lab_pin.sym} 1300 0 0 1 {name=l_a_17 sig_type=std_logic lab=a}
C {devices/lab_pin.sym} 2400 0 0 1 {name=l_b_18 sig_type=std_logic lab=b}
C {devices/lab_pin.sym} 1390 380 0 0 {name=l_c0_19 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 1390 420 0 0 {name=l_c1_20 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 1390 460 0 0 {name=l_c2_21 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 1390 500 0 0 {name=l_c3_22 sig_type=std_logic lab=c3}
C {devices/lab_pin.sym} 1390 540 0 0 {name=l_c0b_23 sig_type=std_logic lab=c0b}
C {devices/lab_pin.sym} 1390 580 0 0 {name=l_c1b_24 sig_type=std_logic lab=c1b}
C {devices/lab_pin.sym} 1390 620 0 0 {name=l_c2b_25 sig_type=std_logic lab=c2b}
C {devices/lab_pin.sym} 1390 660 0 0 {name=l_c3b_26 sig_type=std_logic lab=c3b}
C {devices/lab_pin.sym} 1510 260 0 0 {name=l_VDDA_27 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1510 740 0 0 {name=l_VSSA_28 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 2490 380 0 0 {name=l_c0_29 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 2490 420 0 0 {name=l_c1_30 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 2490 460 0 0 {name=l_c2_31 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 2490 500 0 0 {name=l_c3_32 sig_type=std_logic lab=c3}
C {devices/lab_pin.sym} 2490 540 0 0 {name=l_c0b_33 sig_type=std_logic lab=c0b}
C {devices/lab_pin.sym} 2490 580 0 0 {name=l_c1b_34 sig_type=std_logic lab=c1b}
C {devices/lab_pin.sym} 2490 620 0 0 {name=l_c2b_35 sig_type=std_logic lab=c2b}
C {devices/lab_pin.sym} 2490 660 0 0 {name=l_c3b_36 sig_type=std_logic lab=c3b}
C {devices/lab_pin.sym} 2610 260 0 0 {name=l_VDDA_37 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 2610 740 0 0 {name=l_VSSA_38 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 2800 70 0 0 {name=X3P L=0.5 W=5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 2800 230 0 0 {name=X3N L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 2820 10 0 0 {name=l_VDDA_41 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 2820 290 0 0 {name=l_VSSA_42 sig_type=std_logic lab=VSSA}
C {devices/opin.sym} 3100 150 0 1 {name=p_out lab=out}
C {devices/ipin.sym} 60 900 0 0 {name=p_in lab=in}
C {devices/lab_pin.sym} 140 900 0 1 {name=l_in_45 sig_type=std_logic lab=in}
C {devices/ipin.sym} 60 950 0 0 {name=p_nb lab=nb}
C {devices/lab_pin.sym} 140 950 0 1 {name=l_nb_47 sig_type=std_logic lab=nb}
C {devices/ipin.sym} 60 1000 0 0 {name=p_pd lab=pd}
C {devices/lab_pin.sym} 140 1000 0 1 {name=l_pd_49 sig_type=std_logic lab=pd}
C {devices/ipin.sym} 60 1050 0 0 {name=p_c0 lab=c0}
C {devices/lab_pin.sym} 140 1050 0 1 {name=l_c0_51 sig_type=std_logic lab=c0}
C {devices/ipin.sym} 60 1100 0 0 {name=p_c1 lab=c1}
C {devices/lab_pin.sym} 140 1100 0 1 {name=l_c1_53 sig_type=std_logic lab=c1}
C {devices/ipin.sym} 60 1150 0 0 {name=p_c2 lab=c2}
C {devices/lab_pin.sym} 140 1150 0 1 {name=l_c2_55 sig_type=std_logic lab=c2}
C {devices/ipin.sym} 60 1200 0 0 {name=p_c3 lab=c3}
C {devices/lab_pin.sym} 140 1200 0 1 {name=l_c3_57 sig_type=std_logic lab=c3}
C {devices/ipin.sym} 60 1250 0 0 {name=p_c0b lab=c0b}
C {devices/lab_pin.sym} 140 1250 0 1 {name=l_c0b_59 sig_type=std_logic lab=c0b}
C {devices/ipin.sym} 60 1300 0 0 {name=p_c1b lab=c1b}
C {devices/lab_pin.sym} 140 1300 0 1 {name=l_c1b_61 sig_type=std_logic lab=c1b}
C {devices/ipin.sym} 60 1350 0 0 {name=p_c2b lab=c2b}
C {devices/lab_pin.sym} 140 1350 0 1 {name=l_c2b_63 sig_type=std_logic lab=c2b}
C {devices/ipin.sym} 60 1400 0 0 {name=p_c3b lab=c3b}
C {devices/lab_pin.sym} 140 1400 0 1 {name=l_c3b_65 sig_type=std_logic lab=c3b}
C {devices/iopin.sym} 60 1500 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 1500 0 1 {name=l_VDDA_67 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 1550 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 1550 0 1 {name=l_VSSA_69 sig_type=std_logic lab=VSSA}
