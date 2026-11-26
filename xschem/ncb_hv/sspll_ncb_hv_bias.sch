v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ncb_hv_bias: XI (KI units of the D2S level diode, gate vff) sets the current of the pMOS diode XPD (line pd); XPO copies it into the nMOS diode XND (line nb). At rest vff = V_GS of the D2S diode: XI is its replica} 40 -560 0 0 0.3 0.3 {}
N 420 -330 420 -360 {lab=}
N 980 -330 980 -360 {lab=}
N 420 130 420 160 {lab=}
N 980 130 980 160 {lab=}
N 420 -270 420 70 {lab=}
N 980 -270 980 70 {lab=}
N 380 -300 340 -300 {lab=}
N 340 -300 340 -100 {lab=}
N 340 -100 420 -100 {lab=}
N 340 -300 260 -300 {lab=}
N 1020 -300 1080 -300 {lab=}
N 1020 100 1060 100 {lab=}
N 1060 100 1060 -100 {lab=}
N 1060 -100 980 -100 {lab=}
N 1060 -100 1140 -100 {lab=}
N 380 100 320 100 {lab=}
N 60 500 140 500 {lab=}
N 1400 500 1500 500 {lab=}
N 1400 550 1500 550 {lab=}
N 60 650 140 650 {lab=}
N 60 700 140 700 {lab=}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 400 -300 0 0 {name=XPD L=0.5 W=4 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 400 100 0 0 {name=XI L=1.0 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1000 -300 0 1 {name=XPO L=0.5 W=4 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1000 100 0 1 {name=XND L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 420 -360 0 0 {name=l_VDDA_4 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 980 -360 0 0 {name=l_VDDA_5 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 420 160 0 0 {name=l_VSSA_6 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 980 160 0 0 {name=l_VSSA_7 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 260 -300 0 0 {name=l_pd_8 sig_type=std_logic lab=pd}
C {devices/lab_pin.sym} 1080 -300 0 1 {name=l_pd_9 sig_type=std_logic lab=pd}
C {devices/lab_pin.sym} 1140 -100 0 1 {name=l_nb_10 sig_type=std_logic lab=nb}
C {devices/lab_pin.sym} 320 100 0 0 {name=l_vff_11 sig_type=std_logic lab=vff}
C {devices/ipin.sym} 60 500 0 0 {name=p_vff lab=vff}
C {devices/lab_pin.sym} 140 500 0 1 {name=l_vff_13 sig_type=std_logic lab=vff}
C {devices/opin.sym} 1500 500 0 1 {name=p_nb lab=nb}
C {devices/lab_pin.sym} 1400 500 0 0 {name=l_nb_15 sig_type=std_logic lab=nb}
C {devices/opin.sym} 1500 550 0 1 {name=p_pd lab=pd}
C {devices/lab_pin.sym} 1400 550 0 0 {name=l_pd_17 sig_type=std_logic lab=pd}
C {devices/iopin.sym} 60 650 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 650 0 1 {name=l_VDDA_19 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 700 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 700 0 1 {name=l_VSSA_21 sig_type=std_logic lab=VSSA}
