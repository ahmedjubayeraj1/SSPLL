v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ckg_pout5: start and stop are rising steps; each gets a complementary step driver (drv5t); the pulse exists only at the output gates: o = NOR(NOT start, stop), ob = NAND(start, NOT stop)} 40 -520 0 0 0.3 0.3 {}
N 60 0 260 0 {lab=}
N 60 600 260 600 {lab=}
N 320 -70 320 -90 {lab=}
N 320 70 320 90 {lab=}
N 320 530 320 510 {lab=}
N 320 670 320 690 {lab=}
N 460 -20 520 -20 {lab=}
N 460 20 520 20 {lab=}
N 460 580 520 580 {lab=}
N 460 620 520 620 {lab=}
N 1020 -190 1020 -130 {lab=}
N 1020 -70 1020 50 {lab=}
N 1020 0 1280 0 {lab=}
N 1280 0 1280 50 {lab=}
N 1020 -250 1020 -280 {lab=}
N 1020 110 1020 140 {lab=}
N 1280 110 1280 140 {lab=}
N 980 -220 940 -220 {lab=}
N 980 80 940 80 {lab=}
N 980 -100 940 -100 {lab=}
N 1240 80 1200 80 {lab=}
N 1020 0 1420 0 {lab=}
N 1020 550 1020 670 {lab=}
N 1020 730 1020 790 {lab=}
N 1020 610 1280 610 {lab=}
N 1280 610 1280 550 {lab=}
N 1020 490 1020 460 {lab=}
N 1280 490 1280 460 {lab=}
N 1020 850 1020 880 {lab=}
N 980 520 940 520 {lab=}
N 980 700 940 700 {lab=}
N 1240 520 1200 520 {lab=}
N 980 820 940 820 {lab=}
N 1280 610 1420 610 {lab=}
N 60 -460 140 -460 {lab=}
N 60 1000 140 1000 {lab=}
C {devices/ipin.sym} 60 0 0 0 {name=p_start lab=start}
C {devices/ipin.sym} 60 600 0 0 {name=p_stop lab=stop}
C {sspll_ckg_drv5t.sym} 360 0 0 0 {name=xda}
C {sspll_ckg_drv5t.sym} 360 600 0 0 {name=xdb}
C {devices/lab_pin.sym} 320 -90 0 0 {name=l_VDDA_4 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 320 90 0 0 {name=l_VSSA_5 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 320 510 0 0 {name=l_VDDA_6 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 320 690 0 0 {name=l_VSSA_7 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 520 -20 0 1 {name=l_st_8 sig_type=std_logic lab=st}
C {devices/lab_pin.sym} 520 20 0 1 {name=l_stb_9 sig_type=std_logic lab=stb}
C {devices/lab_pin.sym} 520 580 0 1 {name=l_sp_10 sig_type=std_logic lab=sp}
C {devices/lab_pin.sym} 520 620 0 1 {name=l_spb_11 sig_type=std_logic lab=spb}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1000 -220 0 0 {name=XPA L=0.5 W=10 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1000 -100 0 0 {name=XPB L=0.5 W=10 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1000 80 0 0 {name=XNA L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1260 80 0 0 {name=XNB L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 1020 -280 0 0 {name=l_VDDA_16 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1020 140 0 0 {name=l_VSSA_17 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1280 140 0 0 {name=l_VSSA_18 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 940 -220 0 0 {name=l_stb_19 sig_type=std_logic lab=stb}
C {devices/lab_pin.sym} 940 80 0 0 {name=l_stb_20 sig_type=std_logic lab=stb}
C {devices/lab_pin.sym} 940 -100 0 0 {name=l_sp_21 sig_type=std_logic lab=sp}
C {devices/lab_pin.sym} 1200 80 0 0 {name=l_sp_22 sig_type=std_logic lab=sp}
C {devices/opin.sym} 1420 0 0 1 {name=p_o lab=o}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1000 520 0 0 {name=XQA L=0.5 W=5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1260 520 0 0 {name=XQB L=0.5 W=5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1000 700 0 0 {name=XMA L=0.5 W=4 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1000 820 0 0 {name=XMB L=0.5 W=4 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 1020 460 0 0 {name=l_VDDA_28 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1280 460 0 0 {name=l_VDDA_29 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1020 880 0 0 {name=l_VSSA_30 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 940 520 0 0 {name=l_st_31 sig_type=std_logic lab=st}
C {devices/lab_pin.sym} 940 700 0 0 {name=l_st_32 sig_type=std_logic lab=st}
C {devices/lab_pin.sym} 1200 520 0 0 {name=l_spb_33 sig_type=std_logic lab=spb}
C {devices/lab_pin.sym} 940 820 0 0 {name=l_spb_34 sig_type=std_logic lab=spb}
C {devices/opin.sym} 1420 610 0 1 {name=p_ob lab=ob}
C {devices/iopin.sym} 60 -460 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -460 0 1 {name=l_VDDA_37 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 1000 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 1000 0 1 {name=l_VSSA_39 sig_type=std_logic lab=VSSA}
