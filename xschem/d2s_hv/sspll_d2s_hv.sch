v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_d2s_hv: diff-to-SE amplifier. Degenerated pMOS pair XN1 / XN2 (each in its own n-well, body = source), R_DEG between the sources, split tails XT1 / XT2 (3 units each) switched by enb} 40 -1160 0 0 0.3 0.3 {}
T {through XE1 / XE2; nMOS mirror XM1 / XM2 turns the current difference into 2 di at vff; R_L from vff to r, the nMOS diode XR fed by XRP: vff = V_GS(XR) + G (inp - inm). Bias line pg: XPD diode fed by XK from ib} 40 -1120 0 0 0.3 0.3 {}
N 270 -850 270 -880 {lab=}
N 270 -790 270 -630 {lab=}
N 230 -600 170 -600 {lab=}
N 270 -570 270 -330 {lab=}
N 230 -820 190 -820 {lab=}
N 190 -820 190 -450 {lab=}
N 190 -450 270 -450 {lab=}
N 270 -410 370 -410 {lab=}
N 230 -300 170 -300 {lab=}
N 270 -270 270 -240 {lab=}
N 230 200 190 200 {lab=}
N 190 200 190 130 {lab=}
N 190 130 270 130 {lab=}
N 270 130 270 170 {lab=}
N 270 130 270 90 {lab=}
N 270 230 270 260 {lab=}
N 820 -850 820 -880 {lab=}
N 820 -790 820 -630 {lab=}
N 780 -820 720 -820 {lab=}
N 780 -600 720 -600 {lab=}
N 1480 -850 1480 -880 {lab=}
N 1480 -790 1480 -630 {lab=}
N 1520 -820 1580 -820 {lab=}
N 1520 -600 1580 -600 {lab=}
N 820 -570 820 -400 {lab=}
N 820 -400 820 -210 {lab=}
N 1480 -570 1480 -400 {lab=}
N 1480 -400 1480 -210 {lab=}
N 820 -400 950 -400 {lab=}
N 950 -400 950 -460 {lab=}
N 950 -460 990 -460 {lab=}
N 1480 -400 1230 -400 {lab=}
N 1230 -400 1230 -460 {lab=}
N 1230 -460 1190 -460 {lab=}
N 1050 -410 1050 -380 {lab=}
N 820 -350 760 -350 {lab=}
N 1480 -350 1540 -350 {lab=}
N 780 -180 720 -180 {lab=}
N 1520 -180 1580 -180 {lab=}
N 820 -150 820 270 {lab=}
N 1480 -150 1480 270 {lab=}
N 780 300 740 300 {lab=}
N 740 300 740 60 {lab=}
N 740 60 820 60 {lab=}
N 740 60 680 60 {lab=}
N 1520 300 1580 300 {lab=}
N 820 330 820 360 {lab=}
N 1480 330 1480 360 {lab=}
N 2220 -850 2220 -880 {lab=}
N 2220 -790 2220 -630 {lab=}
N 2180 -820 2120 -820 {lab=}
N 2180 -600 2120 -600 {lab=}
N 2220 -570 2220 270 {lab=}
N 2180 300 2140 300 {lab=}
N 2140 300 2140 10 {lab=}
N 2140 10 2220 10 {lab=}
N 2220 330 2220 360 {lab=}
N 1480 60 1650 60 {lab=}
N 1650 60 1650 -60 {lab=}
N 1650 -60 1710 -60 {lab=}
N 1910 -60 2220 -60 {lab=}
N 1770 -10 1770 20 {lab=}
N 1650 60 1650 620 {lab=}
N 1650 620 2700 620 {lab=}
N 60 900 140 900 {lab=}
N 60 950 140 950 {lab=}
N 60 1000 140 1000 {lab=}
N 60 1050 140 1050 {lab=}
N 60 -1060 140 -1060 {lab=}
N 60 1250 140 1250 {lab=}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 250 -820 0 0 {name=XPD L=2.0 W=8 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 250 -600 0 0 {name=XPDS L=0.5 W=2 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 270 -880 0 0 {name=l_VDDA_2 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 170 -600 0 0 {name=l_VSSA_3 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 250 -300 0 0 {name=XK L=8.0 W=1 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 370 -410 0 1 {name=l_pg_5 sig_type=std_logic lab=pg}
C {devices/lab_pin.sym} 170 -300 0 0 {name=l_ib_6 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 270 -240 0 0 {name=l_VSSA_7 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 250 200 0 0 {name=XB L=8.0 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 270 90 0 0 {name=l_ib_9 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 270 260 0 0 {name=l_VSSA_10 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 800 -820 0 0 {name=XT1 L=2.0 W=8 nf=1 mult=3 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1500 -820 0 1 {name=XT2 L=2.0 W=8 nf=1 mult=3 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 800 -600 0 0 {name=XE1 L=0.5 W=2 nf=1 mult=3 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1500 -600 0 1 {name=XE2 L=0.5 W=2 nf=1 mult=3 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 820 -880 0 0 {name=l_VDDA_15 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 720 -820 0 0 {name=l_pg_16 sig_type=std_logic lab=pg}
C {devices/lab_pin.sym} 720 -600 0 0 {name=l_enb_17 sig_type=std_logic lab=enb}
C {devices/lab_pin.sym} 1480 -880 0 0 {name=l_VDDA_18 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1580 -820 0 1 {name=l_pg_19 sig_type=std_logic lab=pg}
C {devices/lab_pin.sym} 1580 -600 0 1 {name=l_enb_20 sig_type=std_logic lab=enb}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 800 -180 0 0 {name=XN1 L=1.0 W=8 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=s1}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1500 -180 0 1 {name=XN2 L=1.0 W=8 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=s2}
C {sspll_d2s_hv_rdeg.sym} 1090 -460 0 0 {name=xrdeg}
C {devices/lab_pin.sym} 1050 -380 0 0 {name=l_VSSA_24 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 760 -350 0 0 {name=l_s1_25 sig_type=std_logic lab=s1}
C {devices/lab_pin.sym} 1540 -350 0 1 {name=l_s2_26 sig_type=std_logic lab=s2}
C {devices/lab_pin.sym} 720 -180 0 0 {name=l_inp_27 sig_type=std_logic lab=inp}
C {devices/lab_pin.sym} 1580 -180 0 1 {name=l_inm_28 sig_type=std_logic lab=inm}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 800 300 0 0 {name=XM1 L=2.0 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1500 300 0 1 {name=XM2 L=2.0 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 680 60 0 0 {name=l_d1_31 sig_type=std_logic lab=d1}
C {devices/lab_pin.sym} 1580 300 0 1 {name=l_d1_32 sig_type=std_logic lab=d1}
C {devices/lab_pin.sym} 820 360 0 0 {name=l_VSSA_33 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1480 360 0 0 {name=l_VSSA_34 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 2200 -820 0 0 {name=XRP L=2.0 W=8 nf=1 mult=10 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 2200 -600 0 0 {name=XRS L=0.5 W=2 nf=1 mult=10 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 2220 -880 0 0 {name=l_VDDA_37 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 2120 -820 0 0 {name=l_pg_38 sig_type=std_logic lab=pg}
C {devices/lab_pin.sym} 2120 -600 0 0 {name=l_VSSA_39 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 2200 300 0 0 {name=XR L=1.0 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 2220 360 0 0 {name=l_VSSA_41 sig_type=std_logic lab=VSSA}
C {sspll_d2s_hv_rl.sym} 1810 -60 0 0 {name=xrl}
C {devices/lab_pin.sym} 1770 20 0 0 {name=l_VSSA_43 sig_type=std_logic lab=VSSA}
C {devices/opin.sym} 2700 620 0 1 {name=p_vff lab=vff}
C {devices/ipin.sym} 60 900 0 0 {name=p_inp lab=inp}
C {devices/lab_pin.sym} 140 900 0 1 {name=l_inp_46 sig_type=std_logic lab=inp}
C {devices/ipin.sym} 60 950 0 0 {name=p_inm lab=inm}
C {devices/lab_pin.sym} 140 950 0 1 {name=l_inm_48 sig_type=std_logic lab=inm}
C {devices/iopin.sym} 60 1000 0 0 {name=p_ib lab=ib}
C {devices/lab_pin.sym} 140 1000 0 1 {name=l_ib_50 sig_type=std_logic lab=ib}
C {devices/ipin.sym} 60 1050 0 0 {name=p_enb lab=enb}
C {devices/lab_pin.sym} 140 1050 0 1 {name=l_enb_52 sig_type=std_logic lab=enb}
C {devices/iopin.sym} 60 -1060 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -1060 0 1 {name=l_VDDA_54 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 1250 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 1250 0 1 {name=l_VSSA_56 sig_type=std_logic lab=VSSA}
