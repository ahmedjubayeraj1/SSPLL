v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ncb_hv_sinv: current-starved inverter. XSP (gate pd, mirror of the bias) limits the rising edge of o, XS (gate nb) the falling edge; XP / XN switch} 40 -640 0 0 0.3 0.3 {}
N 420 -450 420 -480 {lab=}
N 420 -390 420 -210 {lab=}
N 420 -150 420 50 {lab=}
N 420 110 420 290 {lab=}
N 420 350 420 380 {lab=}
N 380 -420 320 -420 {lab=}
N 380 320 320 320 {lab=}
N 380 -180 340 -180 {lab=}
N 340 -180 340 80 {lab=}
N 340 80 380 80 {lab=}
N 340 -50 260 -50 {lab=}
N 420 -50 700 -50 {lab=}
N 60 560 140 560 {lab=}
N 60 610 140 610 {lab=}
N 60 660 140 660 {lab=}
N 60 760 140 760 {lab=}
N 60 810 140 810 {lab=}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 400 -420 0 0 {name=XSP L=0.5 W=4 nf=1 mult=30 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 400 -180 0 0 {name=XP L=0.5 W=8 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 400 80 0 0 {name=XN L=0.5 W=3 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 400 320 0 0 {name=XS L=0.5 W=2 nf=1 mult=20 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 420 -480 0 0 {name=l_VDDA_4 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 420 380 0 0 {name=l_VSSA_5 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 320 -420 0 0 {name=l_pd_6 sig_type=std_logic lab=pd}
C {devices/lab_pin.sym} 320 320 0 0 {name=l_nb_7 sig_type=std_logic lab=nb}
C {devices/lab_pin.sym} 260 -50 0 0 {name=l_i_8 sig_type=std_logic lab=i}
C {devices/opin.sym} 700 -50 0 1 {name=p_o lab=o}
C {devices/ipin.sym} 60 560 0 0 {name=p_i lab=i}
C {devices/lab_pin.sym} 140 560 0 1 {name=l_i_11 sig_type=std_logic lab=i}
C {devices/ipin.sym} 60 610 0 0 {name=p_nb lab=nb}
C {devices/lab_pin.sym} 140 610 0 1 {name=l_nb_13 sig_type=std_logic lab=nb}
C {devices/ipin.sym} 60 660 0 0 {name=p_pd lab=pd}
C {devices/lab_pin.sym} 140 660 0 1 {name=l_pd_15 sig_type=std_logic lab=pd}
C {devices/iopin.sym} 60 760 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 760 0 1 {name=l_VDDA_17 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 810 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 810 0 1 {name=l_VSSA_19 sig_type=std_logic lab=VSSA}
