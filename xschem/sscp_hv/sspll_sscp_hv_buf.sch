v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_sscp_hv_buf: dump buffer, nMOS-input OTA in unity gain (XA2's gate is the output). Tail XBT (x10 units mirrored from nb, 20 uA) through the enable XBE} 40 -460 0 0 0.3 0.3 {}
N 420 -290 420 -320 {lab=}
N 980 -290 980 -320 {lab=}
N 420 -230 420 -50 {lab=}
N 980 -230 980 -50 {lab=}
N 380 -260 340 -260 {lab=}
N 340 -260 340 -140 {lab=}
N 340 -140 420 -140 {lab=}
N 1020 -260 1080 -260 {lab=}
N 340 -140 300 -140 {lab=}
N 380 -20 320 -20 {lab=}
N 980 -140 1200 -140 {lab=}
N 1020 -20 1080 -20 {lab=}
N 420 10 420 70 {lab=}
N 420 70 980 70 {lab=}
N 980 70 980 10 {lab=}
N 700 70 700 160 {lab=}
N 700 220 700 340 {lab=}
N 660 190 600 190 {lab=}
N 660 370 600 370 {lab=}
N 700 400 700 430 {lab=}
N 60 560 140 560 {lab=}
N 60 610 140 610 {lab=}
N 60 660 140 660 {lab=}
N 1300 560 1400 560 {lab=}
N 60 -500 140 -500 {lab=}
N 60 760 140 760 {lab=}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 400 -260 0 0 {name=XL1 L=2.0 W=16 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1000 -260 0 1 {name=XL2 L=2.0 W=16 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 400 -20 0 0 {name=XA1 L=2.0 W=8 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1000 -20 0 1 {name=XA2 L=2.0 W=8 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 420 -320 0 0 {name=l_VDDA_4 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 980 -320 0 0 {name=l_VDDA_5 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1080 -260 0 1 {name=l_o1_6 sig_type=std_logic lab=o1}
C {devices/lab_pin.sym} 300 -140 0 0 {name=l_o1_7 sig_type=std_logic lab=o1}
C {devices/lab_pin.sym} 320 -20 0 0 {name=l_inp_8 sig_type=std_logic lab=inp}
C {devices/lab_pin.sym} 1200 -140 0 1 {name=l_out_9 sig_type=std_logic lab=out}
C {devices/lab_pin.sym} 1080 -20 0 1 {name=l_out_10 sig_type=std_logic lab=out}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 680 190 0 0 {name=XBE L=0.5 W=1 nf=1 mult=10 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 680 370 0 0 {name=XBT L=8.0 W=2 nf=1 mult=10 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 600 190 0 0 {name=l_en_13 sig_type=std_logic lab=en}
C {devices/lab_pin.sym} 600 370 0 0 {name=l_nb_14 sig_type=std_logic lab=nb}
C {devices/lab_pin.sym} 700 430 0 0 {name=l_VSS_15 sig_type=std_logic lab=VSS}
C {devices/ipin.sym} 60 560 0 0 {name=p_inp lab=inp}
C {devices/lab_pin.sym} 140 560 0 1 {name=l_inp_17 sig_type=std_logic lab=inp}
C {devices/ipin.sym} 60 610 0 0 {name=p_nb lab=nb}
C {devices/lab_pin.sym} 140 610 0 1 {name=l_nb_19 sig_type=std_logic lab=nb}
C {devices/ipin.sym} 60 660 0 0 {name=p_en lab=en}
C {devices/lab_pin.sym} 140 660 0 1 {name=l_en_21 sig_type=std_logic lab=en}
C {devices/opin.sym} 1400 560 0 1 {name=p_out lab=out}
C {devices/lab_pin.sym} 1300 560 0 0 {name=l_out_23 sig_type=std_logic lab=out}
C {devices/iopin.sym} 60 -500 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -500 0 1 {name=l_VDDA_25 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 760 0 0 {name=p_VSS lab=VSS}
C {devices/lab_pin.sym} 140 760 0 1 {name=l_VSS_27 sig_type=std_logic lab=VSS}
