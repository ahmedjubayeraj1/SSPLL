v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_fll_cp: current-steering charge pump, 5 V devices on VDDA / VSSA. ib (5 uA) -> diode XND; sink mirror XNS (x12)} 40 -560 0 0 0.3 0.3 {}
T {steered to vctl by up5 or to VDDA by up5b; source mirror XPS (x12, via XN1 -> diode XPD) steered to vctl by dn5b or} 40 -520 0 0 0.3 0.3 {}
T {to VSSA by dn5. The mirrors stay in saturation, so their gates are not kicked. act5b = 1 shorts ib: everything off.} 40 -480 0 0 0.3 0.3 {}
N 100 60 320 60 {lab=}
N 320 60 320 170 {lab=}
N 320 60 570 60 {lab=}
N 570 60 570 170 {lab=}
N 320 170 320 120 {lab=}
N 320 120 240 120 {lab=}
N 240 120 240 200 {lab=}
N 240 200 280 200 {lab=}
N 320 230 320 270 {lab=}
N 570 230 570 270 {lab=}
N 530 200 470 200 {lab=}
N 920 130 920 200 {lab=}
N 920 200 920 270 {lab=}
N 920 200 1170 200 {lab=}
N 1170 200 1170 130 {lab=}
N 920 330 920 370 {lab=}
N 880 300 820 300 {lab=}
N 880 100 820 100 {lab=}
N 1130 100 1070 100 {lab=}
N 1170 70 1170 30 {lab=}
N 1520 170 1520 -100 {lab=}
N 1520 -100 1520 -220 {lab=}
N 1520 -100 1440 -100 {lab=}
N 1440 -100 1440 -250 {lab=}
N 1440 -250 1480 -250 {lab=}
N 1520 230 1520 270 {lab=}
N 1480 200 1420 200 {lab=}
N 1520 -280 1520 -320 {lab=}
N 920 -320 920 -250 {lab=}
N 920 -250 920 -180 {lab=}
N 920 -250 1170 -250 {lab=}
N 1170 -250 1170 -180 {lab=}
N 920 -380 920 -420 {lab=}
N 880 -350 820 -350 {lab=}
N 880 -150 820 -150 {lab=}
N 1130 -150 1070 -150 {lab=}
N 1170 -120 1170 -80 {lab=}
N 920 -120 920 -30 {lab=}
N 920 -30 920 70 {lab=}
N 920 -30 1300 -30 {lab=}
N 100 300 180 300 {lab=}
N 100 360 180 360 {lab=}
N 100 420 180 420 {lab=}
N 100 480 180 480 {lab=}
N 100 540 180 540 {lab=}
N 100 -300 180 -300 {lab=}
N 100 620 180 620 {lab=}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 300 200 0 0 {name=XND L=4.0 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 550 200 0 0 {name=XNK L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/iopin.sym} 100 60 0 0 {name=p_ib lab=ib}
C {devices/lab_pin.sym} 240 120 0 0 {name=l_ib_3 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 320 270 0 0 {name=l_VSSA_4 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 570 270 0 0 {name=l_VSSA_5 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 470 200 0 0 {name=l_act5b_6 sig_type=std_logic lab=act5b}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 900 300 0 0 {name=XNS L=4.0 W=1 nf=1 mult=12 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 900 100 0 0 {name=XSU L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1150 100 0 0 {name=XSUX L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 920 370 0 0 {name=l_VSSA_10 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 820 300 0 0 {name=l_ib_11 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 820 100 0 0 {name=l_up5_12 sig_type=std_logic lab=up5}
C {devices/lab_pin.sym} 1070 100 0 0 {name=l_up5b_13 sig_type=std_logic lab=up5b}
C {devices/lab_pin.sym} 1170 30 0 0 {name=l_VDDA_14 sig_type=std_logic lab=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1500 200 0 0 {name=XN1 L=4.0 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1500 -250 0 0 {name=XPD L=4.0 W=2.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 1440 -100 0 0 {name=l_pd_17 sig_type=std_logic lab=pd}
C {devices/lab_pin.sym} 1520 270 0 0 {name=l_VSSA_18 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1420 200 0 0 {name=l_ib_19 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 1520 -320 0 0 {name=l_VDDA_20 sig_type=std_logic lab=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 900 -350 0 0 {name=XPS L=4.0 W=2.5 nf=1 mult=12 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 900 -150 0 0 {name=XSD L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1150 -150 0 0 {name=XSDX L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 920 -420 0 0 {name=l_VDDA_24 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 820 -350 0 0 {name=l_pd_25 sig_type=std_logic lab=pd}
C {devices/lab_pin.sym} 820 -150 0 0 {name=l_dn5b_26 sig_type=std_logic lab=dn5b}
C {devices/lab_pin.sym} 1070 -150 0 0 {name=l_dn5_27 sig_type=std_logic lab=dn5}
C {devices/lab_pin.sym} 1170 -80 0 0 {name=l_VSSA_28 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 1300 -30 0 1 {name=p_vctl lab=vctl}
C {devices/ipin.sym} 100 300 0 0 {name=p_up5 lab=up5}
C {devices/lab_pin.sym} 180 300 0 1 {name=l_up5_31 sig_type=std_logic lab=up5}
C {devices/ipin.sym} 100 360 0 0 {name=p_up5b lab=up5b}
C {devices/lab_pin.sym} 180 360 0 1 {name=l_up5b_33 sig_type=std_logic lab=up5b}
C {devices/ipin.sym} 100 420 0 0 {name=p_dn5 lab=dn5}
C {devices/lab_pin.sym} 180 420 0 1 {name=l_dn5_35 sig_type=std_logic lab=dn5}
C {devices/ipin.sym} 100 480 0 0 {name=p_dn5b lab=dn5b}
C {devices/lab_pin.sym} 180 480 0 1 {name=l_dn5b_37 sig_type=std_logic lab=dn5b}
C {devices/ipin.sym} 100 540 0 0 {name=p_act5b lab=act5b}
C {devices/lab_pin.sym} 180 540 0 1 {name=l_act5b_39 sig_type=std_logic lab=act5b}
C {devices/iopin.sym} 100 -300 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 180 -300 0 1 {name=l_VDDA_41 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 100 620 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 180 620 0 1 {name=l_VSSA_43 sig_type=std_logic lab=VSSA}
