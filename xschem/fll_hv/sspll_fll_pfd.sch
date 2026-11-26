v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_fll_pfd: tri-state PFD (two dfrtp, D = 1, NAND reset, held in reset while fll_en = 0) and the dead zone:} 40 -460 0 0 0.3 0.3 {}
T {upg = up AND (up delayed ~0.26 ns) AND act, so the reset pulse and edges closer than the delay never reach the pump.} 40 -420 0 0 0.3 0.3 {}
N 410 -170 350 -170 {lab=}
N 410 130 350 130 {lab=}
N 410 -150 350 -150 {lab=}
N 410 150 350 150 {lab=}
N 590 -170 650 -170 {lab=}
N 650 -170 650 -20 {lab=}
N 650 -20 790 -20 {lab=}
N 590 130 680 130 {lab=}
N 680 130 680 20 {lab=}
N 680 20 790 20 {lab=}
N 910 0 1010 0 {lab=}
N 1090 0 1150 0 {lab=}
N 1150 0 1190 0 {lab=}
N 1190 40 1130 40 {lab=}
N 1310 20 1370 20 {lab=}
N 410 -130 350 -130 {lab=}
N 410 170 350 170 {lab=}
N 1010 -300 950 -300 {lab=}
N 1090 -300 1260 -300 {lab=}
N 1340 -300 1480 -300 {lab=}
N 1480 -300 1540 -300 {lab=}
N 1540 -340 1480 -340 {lab=}
N 1540 -260 1480 -260 {lab=}
N 1660 -300 1720 -300 {lab=}
N 1010 300 950 300 {lab=}
N 1090 300 1260 300 {lab=}
N 1340 300 1480 300 {lab=}
N 1480 300 1540 300 {lab=}
N 1540 260 1480 260 {lab=}
N 1540 340 1480 340 {lab=}
N 1660 300 1720 300 {lab=}
N 100 500 180 500 {lab=}
N 100 560 180 560 {lab=}
N 100 620 180 620 {lab=}
N 100 680 180 680 {lab=}
N 2000 500 1780 500 {lab=}
N 2000 560 1780 560 {lab=}
N 2000 620 1780 620 {lab=}
N 2000 680 1780 680 {lab=}
N 100 760 180 760 {lab=}
N 100 820 180 820 {lab=}
C {sky130_stdcells/dfrtp_1.sym} 500 -150 0 0 {name=xfu VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/dfrtp_1.sym} 500 150 0 0 {name=xfd VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 350 -170 0 0 {name=l_refclk_2 sig_type=std_logic lab=refclk}
C {devices/lab_pin.sym} 350 130 0 0 {name=l_div_3 sig_type=std_logic lab=div}
C {devices/lab_pin.sym} 350 -150 0 0 {name=l_VDDD_4 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 350 150 0 0 {name=l_VDDD_5 sig_type=std_logic lab=VDDD}
C {sky130_stdcells/nand2_1.sym} 850 0 0 0 {name=xrn VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/buf_1.sym} 1050 0 0 0 {name=xrd VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/and2_1.sym} 1250 20 0 0 {name=xre VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1130 40 0 0 {name=l_fll_en_9 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 1370 20 0 1 {name=l_rb_10 sig_type=std_logic lab=rb}
C {devices/lab_pin.sym} 350 -130 0 0 {name=l_rb_11 sig_type=std_logic lab=rb}
C {devices/lab_pin.sym} 350 170 0 0 {name=l_rb_12 sig_type=std_logic lab=rb}
C {devices/lab_pin.sym} 650 -170 0 1 {name=l_up_13 sig_type=std_logic lab=up}
C {devices/lab_pin.sym} 680 130 0 1 {name=l_dn_14 sig_type=std_logic lab=dn}
C {sky130_stdcells/clkdlybuf4s25_1.sym} 1050 -300 0 0 {name=xzu1 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/buf_1.sym} 1300 -300 0 0 {name=xzu2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/and3_1.sym} 1600 -300 0 0 {name=xgu VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 950 -300 0 0 {name=l_up_18 sig_type=std_logic lab=up}
C {devices/lab_pin.sym} 1480 -340 0 0 {name=l_up_19 sig_type=std_logic lab=up}
C {devices/lab_pin.sym} 1480 -260 0 0 {name=l_act_20 sig_type=std_logic lab=act}
C {devices/lab_pin.sym} 1720 -300 0 1 {name=l_upg_21 sig_type=std_logic lab=upg}
C {sky130_stdcells/clkdlybuf4s25_1.sym} 1050 300 0 0 {name=xzd1 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/buf_1.sym} 1300 300 0 0 {name=xzd2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/and3_1.sym} 1600 300 0 0 {name=xgd VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 950 300 0 0 {name=l_dn_25 sig_type=std_logic lab=dn}
C {devices/lab_pin.sym} 1480 260 0 0 {name=l_dn_26 sig_type=std_logic lab=dn}
C {devices/lab_pin.sym} 1480 340 0 0 {name=l_act_27 sig_type=std_logic lab=act}
C {devices/lab_pin.sym} 1720 300 0 1 {name=l_dng_28 sig_type=std_logic lab=dng}
C {devices/ipin.sym} 100 500 0 0 {name=p_refclk lab=refclk}
C {devices/lab_pin.sym} 180 500 0 1 {name=l_refclk_30 sig_type=std_logic lab=refclk}
C {devices/ipin.sym} 100 560 0 0 {name=p_div lab=div}
C {devices/lab_pin.sym} 180 560 0 1 {name=l_div_32 sig_type=std_logic lab=div}
C {devices/ipin.sym} 100 620 0 0 {name=p_fll_en lab=fll_en}
C {devices/lab_pin.sym} 180 620 0 1 {name=l_fll_en_34 sig_type=std_logic lab=fll_en}
C {devices/ipin.sym} 100 680 0 0 {name=p_act lab=act}
C {devices/lab_pin.sym} 180 680 0 1 {name=l_act_36 sig_type=std_logic lab=act}
C {devices/opin.sym} 2000 500 0 1 {name=p_up lab=up}
C {devices/lab_pin.sym} 1780 500 0 0 {name=l_up_38 sig_type=std_logic lab=up}
C {devices/opin.sym} 2000 560 0 1 {name=p_dn lab=dn}
C {devices/lab_pin.sym} 1780 560 0 0 {name=l_dn_40 sig_type=std_logic lab=dn}
C {devices/opin.sym} 2000 620 0 1 {name=p_upg lab=upg}
C {devices/lab_pin.sym} 1780 620 0 0 {name=l_upg_42 sig_type=std_logic lab=upg}
C {devices/opin.sym} 2000 680 0 1 {name=p_dng lab=dng}
C {devices/lab_pin.sym} 1780 680 0 0 {name=l_dng_44 sig_type=std_logic lab=dng}
C {devices/iopin.sym} 100 760 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 180 760 0 1 {name=l_VDDD_46 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 100 820 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 180 820 0 1 {name=l_VSSD_48 sig_type=std_logic lab=VSSD}
