v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_sscp_hv_slice: one Gm unit. Degenerated nMOS pair XN1/XN2 (R_S between the sources); tail sinks XT1/XT2 (2 units each) mirrored from nb, switched by en through XE1/XE2; each drain has its own pMOS source} 40 -820 0 0 0.3 0.3 {}
T {XPC/XPX (biased by pb, switched by enb through XPE1/XPE2) equal to its tail: x = I(XPX) - I(XN2) is the output, xc = I(XPC) - I(XN1) goes to the dump node. No mirror: nothing slow in the signal path} 40 -780 0 0 0.3 0.3 {}
N 420 -650 420 -680 {lab=}
N 980 -650 980 -680 {lab=}
N 420 -590 420 -430 {lab=}
N 980 -590 980 -430 {lab=}
N 380 -620 320 -620 {lab=}
N 1020 -620 1080 -620 {lab=}
N 380 -400 320 -400 {lab=}
N 1020 -400 1080 -400 {lab=}
N 420 -370 420 -150 {lab=}
N 980 -370 980 -150 {lab=}
N 420 -260 340 -260 {lab=}
N 980 -260 1060 -260 {lab=}
N 380 -120 320 -120 {lab=}
N 1020 -120 1080 -120 {lab=}
N 420 -90 420 60 {lab=}
N 420 60 600 60 {lab=}
N 980 -90 980 60 {lab=}
N 980 60 800 60 {lab=}
N 660 110 660 140 {lab=}
N 420 60 420 230 {lab=}
N 980 60 980 230 {lab=}
N 380 260 320 260 {lab=}
N 1020 260 1080 260 {lab=}
N 420 290 420 430 {lab=}
N 980 290 980 430 {lab=}
N 380 460 320 460 {lab=}
N 1020 460 1080 460 {lab=}
N 420 490 420 520 {lab=}
N 980 490 980 520 {lab=}
N 60 700 140 700 {lab=}
N 60 750 140 750 {lab=}
N 60 800 140 800 {lab=}
N 60 850 140 850 {lab=}
N 60 900 140 900 {lab=}
N 60 950 140 950 {lab=}
N 1300 700 1400 700 {lab=}
N 1300 750 1400 750 {lab=}
N 60 -900 140 -900 {lab=}
N 60 1050 140 1050 {lab=}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 400 -620 0 0 {name=XPE1 L=0.5 W=2 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1000 -620 0 1 {name=XPE2 L=0.5 W=2 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 400 -400 0 0 {name=XPC L=4.0 W=4 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1000 -400 0 1 {name=XPX L=4.0 W=4 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 420 -680 0 0 {name=l_VDDA_4 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 980 -680 0 0 {name=l_VDDA_5 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 320 -620 0 0 {name=l_enb_6 sig_type=std_logic lab=enb}
C {devices/lab_pin.sym} 1080 -620 0 1 {name=l_enb_7 sig_type=std_logic lab=enb}
C {devices/lab_pin.sym} 320 -400 0 0 {name=l_pb_8 sig_type=std_logic lab=pb}
C {devices/lab_pin.sym} 1080 -400 0 1 {name=l_pb_9 sig_type=std_logic lab=pb}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 400 -120 0 0 {name=XN1 L=1.0 W=4 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1000 -120 0 1 {name=XN2 L=1.0 W=4 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 340 -260 0 0 {name=l_xc_12 sig_type=std_logic lab=xc}
C {devices/lab_pin.sym} 1060 -260 0 1 {name=l_x_13 sig_type=std_logic lab=x}
C {devices/lab_pin.sym} 320 -120 0 0 {name=l_v1p_14 sig_type=std_logic lab=v1p}
C {devices/lab_pin.sym} 1080 -120 0 1 {name=l_v1m_15 sig_type=std_logic lab=v1m}
C {sspll_sscp_hv_rs.sym} 700 60 0 0 {name=xrs}
C {devices/lab_pin.sym} 660 140 0 0 {name=l_VSS_17 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 400 260 0 0 {name=XE1 L=0.5 W=1 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1000 260 0 1 {name=XE2 L=0.5 W=1 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 320 260 0 0 {name=l_en_20 sig_type=std_logic lab=en}
C {devices/lab_pin.sym} 1080 260 0 1 {name=l_en_21 sig_type=std_logic lab=en}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 400 460 0 0 {name=XT1 L=8.0 W=1 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1000 460 0 1 {name=XT2 L=8.0 W=1 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 320 460 0 0 {name=l_nb_24 sig_type=std_logic lab=nb}
C {devices/lab_pin.sym} 1080 460 0 1 {name=l_nb_25 sig_type=std_logic lab=nb}
C {devices/lab_pin.sym} 420 520 0 0 {name=l_VSS_26 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 980 520 0 0 {name=l_VSS_27 sig_type=std_logic lab=VSS}
C {devices/ipin.sym} 60 700 0 0 {name=p_v1p lab=v1p}
C {devices/lab_pin.sym} 140 700 0 1 {name=l_v1p_29 sig_type=std_logic lab=v1p}
C {devices/ipin.sym} 60 750 0 0 {name=p_v1m lab=v1m}
C {devices/lab_pin.sym} 140 750 0 1 {name=l_v1m_31 sig_type=std_logic lab=v1m}
C {devices/ipin.sym} 60 800 0 0 {name=p_nb lab=nb}
C {devices/lab_pin.sym} 140 800 0 1 {name=l_nb_33 sig_type=std_logic lab=nb}
C {devices/ipin.sym} 60 850 0 0 {name=p_pb lab=pb}
C {devices/lab_pin.sym} 140 850 0 1 {name=l_pb_35 sig_type=std_logic lab=pb}
C {devices/ipin.sym} 60 900 0 0 {name=p_en lab=en}
C {devices/lab_pin.sym} 140 900 0 1 {name=l_en_37 sig_type=std_logic lab=en}
C {devices/ipin.sym} 60 950 0 0 {name=p_enb lab=enb}
C {devices/lab_pin.sym} 140 950 0 1 {name=l_enb_39 sig_type=std_logic lab=enb}
C {devices/iopin.sym} 1400 700 0 1 {name=p_x lab=x}
C {devices/lab_pin.sym} 1300 700 0 0 {name=l_x_41 sig_type=std_logic lab=x}
C {devices/iopin.sym} 1400 750 0 1 {name=p_xc lab=xc}
C {devices/lab_pin.sym} 1300 750 0 0 {name=l_xc_43 sig_type=std_logic lab=xc}
C {devices/iopin.sym} 60 -900 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -900 0 1 {name=l_VDDA_45 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 1050 0 0 {name=p_VSS lab=VSS}
C {devices/lab_pin.sym} 140 1050 0 1 {name=l_VSS_47 sig_type=std_logic lab=VSS}
