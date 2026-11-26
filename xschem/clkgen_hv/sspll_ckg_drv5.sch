v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ckg_drv5: o follows in through an always-on TG and 2 inverters, ob is inverted through 3; the TG adds about one gate delay so o and ob switch together (5 V devices on VDDA)} 40 -420 0 0 0.3 0.3 {}
N 60 0 180 0 {lab=}
N 180 0 180 120 {lab=}
N 180 120 320 120 {lab=}
N 180 0 180 -220 {lab=}
N 180 -220 320 -220 {lab=}
N 320 -220 320 -140 {lab=}
N 320 60 320 0 {lab=}
N 320 -80 320 0 {lab=}
N 280 90 240 90 {lab=}
N 280 -110 240 -110 {lab=}
N 580 -50 580 50 {lab=}
N 540 -80 500 -80 {lab=}
N 500 -80 500 80 {lab=}
N 500 80 540 80 {lab=}
N 580 -110 580 -140 {lab=}
N 580 110 580 140 {lab=}
N 840 -50 840 50 {lab=}
N 800 -80 760 -80 {lab=}
N 760 -80 760 80 {lab=}
N 760 80 800 80 {lab=}
N 840 -110 840 -140 {lab=}
N 840 110 840 140 {lab=}
N 320 0 500 0 {lab=}
N 580 0 760 0 {lab=}
N 580 430 580 530 {lab=}
N 540 400 500 400 {lab=}
N 500 400 500 560 {lab=}
N 500 560 540 560 {lab=}
N 580 370 580 340 {lab=}
N 580 590 580 620 {lab=}
N 840 430 840 530 {lab=}
N 800 400 760 400 {lab=}
N 760 400 760 560 {lab=}
N 760 560 800 560 {lab=}
N 840 370 840 340 {lab=}
N 840 590 840 620 {lab=}
N 1100 430 1100 530 {lab=}
N 1060 400 1020 400 {lab=}
N 1020 400 1020 560 {lab=}
N 1020 560 1060 560 {lab=}
N 1100 370 1100 340 {lab=}
N 1100 590 1100 620 {lab=}
N 140 0 140 480 {lab=}
N 140 480 500 480 {lab=}
N 580 480 760 480 {lab=}
N 840 480 1020 480 {lab=}
N 840 0 1260 0 {lab=}
N 1100 480 1260 480 {lab=}
N 60 -340 140 -340 {lab=}
N 60 760 140 760 {lab=}
C {devices/ipin.sym} 60 0 0 0 {name=p_in lab=in}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 300 90 0 0 {name=XTN L=0.5 W=1.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 300 -110 0 0 {name=XTP L=0.5 W=1.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 240 90 0 0 {name=l_VDDA_3 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 240 -110 0 0 {name=l_VSSA_4 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 560 -80 0 0 {name=XAP L=0.5 W=6.25 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 560 80 0 0 {name=XAN L=0.5 W=2.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 580 -140 0 0 {name=l_VDDA_7 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 580 140 0 0 {name=l_VSSA_8 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 820 -80 0 0 {name=XBP L=0.5 W=20 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 820 80 0 0 {name=XBN L=0.5 W=8 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 840 -140 0 0 {name=l_VDDA_11 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 840 140 0 0 {name=l_VSSA_12 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 560 400 0 0 {name=XCP L=0.5 W=2.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 560 560 0 0 {name=XCN L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 580 340 0 0 {name=l_VDDA_15 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 580 620 0 0 {name=l_VSSA_16 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 820 400 0 0 {name=XDP L=0.5 W=6.25 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 820 560 0 0 {name=XDN L=0.5 W=2.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 840 340 0 0 {name=l_VDDA_19 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 840 620 0 0 {name=l_VSSA_20 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1080 400 0 0 {name=XEP L=0.5 W=20 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1080 560 0 0 {name=XEN L=0.5 W=8 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 1100 340 0 0 {name=l_VDDA_23 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1100 620 0 0 {name=l_VSSA_24 sig_type=std_logic lab=VSSA}
C {devices/opin.sym} 1260 0 0 1 {name=p_o lab=o}
C {devices/opin.sym} 1260 480 0 1 {name=p_ob lab=ob}
C {devices/iopin.sym} 60 -340 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -340 0 1 {name=l_VDDA_28 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 760 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 760 0 1 {name=l_VSSA_30 sig_type=std_logic lab=VSSA}
