v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_refbuf_s1: first gain stage. Header XPH (x24 units of the bias diode XPD) feeds the current-reuse inverter XP1/XN1; C_H (XCH) decouples the header node vh} 40 -470 0 0 0.3 0.3 {}
T {disabled (en = 0): XPEN turns the header off, XNS1 pulls s1 (and through R_B the input) low} 40 -430 0 0 0.25 0.25 {}
N 60 -300 950 -300 {lab=}
N 60 340 950 340 {lab=}
N 220 -230 220 -300 {lab=}
N 220 -170 220 -120 {lab=}
N 180 -200 160 -200 {lab=}
N 160 -200 160 -120 {lab=}
N 160 -120 220 -120 {lab=}
N 60 -120 160 -120 {lab=}
N 440 -230 440 -300 {lab=}
N 440 -170 440 -120 {lab=}
N 440 -120 220 -120 {lab=}
N 400 -200 370 -200 {lab=}
N 660 -230 660 -300 {lab=}
N 620 -200 600 -200 {lab=}
N 600 -200 600 -120 {lab=}
N 600 -120 440 -120 {lab=}
N 850 -230 850 -300 {lab=}
N 660 -170 660 -100 {lab=}
N 660 -100 850 -100 {lab=}
N 850 -100 850 -170 {lab=}
N 850 -100 910 -100 {lab=}
N 660 -100 660 -30 {lab=}
N 660 30 660 90 {lab=}
N 660 90 660 150 {lab=}
N 660 210 660 340 {lab=}
N 60 90 560 90 {lab=}
N 620 0 560 0 {lab=}
N 560 0 560 90 {lab=}
N 560 90 560 180 {lab=}
N 560 180 620 180 {lab=}
N 660 90 900 90 {lab=}
N 900 90 1000 90 {lab=}
N 900 150 900 90 {lab=}
N 900 210 900 340 {lab=}
N 860 180 830 180 {lab=}
N 60 230 140 230 {lab=}
N 60 280 140 280 {lab=}
C {devices/iopin.sym} 60 -300 0 0 {name=p_VDDA lab=VDDA}
C {devices/iopin.sym} 60 340 0 0 {name=p_VSS lab=VSS}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 200 -200 0 0 {name=XPD L=4.0 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/iopin.sym} 60 -120 0 0 {name=p_ib lab=ib}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 420 -200 0 0 {name=XPEN L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 370 -200 0 0 {name=l_en_5 sig_type=std_logic lab=en}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 640 -200 0 0 {name=XPH L=4.0 W=2 nf=1 mult=24 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/cap_mim_m3_1.sym} 850 -200 2 0 {name=XCH W=30.0 L=30.0 MF=1 model=cap_mim_m3_1 spiceprefix=X}
C {devices/lab_pin.sym} 910 -100 0 1 {name=l_vh_8 sig_type=std_logic lab=vh}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 640 0 0 0 {name=XP1 L=1.0 W=120 nf=12 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=vh}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 640 180 0 0 {name=XN1 L=1.0 W=120 nf=12 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/ipin.sym} 60 90 0 0 {name=p_vin lab=vin}
C {devices/opin.sym} 1000 90 0 1 {name=p_s1 lab=s1}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 880 180 0 0 {name=XNS1 L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 830 180 0 0 {name=l_enb_14 sig_type=std_logic lab=enb}
C {devices/ipin.sym} 60 230 0 0 {name=p_en lab=en}
C {devices/lab_pin.sym} 140 230 0 1 {name=l_en_16 sig_type=std_logic lab=en}
C {devices/ipin.sym} 60 280 0 0 {name=p_enb lab=enb}
C {devices/lab_pin.sym} 140 280 0 1 {name=l_enb_18 sig_type=std_logic lab=enb}
