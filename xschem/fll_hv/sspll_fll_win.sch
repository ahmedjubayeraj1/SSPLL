v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_fll_win: refclk and div delayed by three clkdlybuf4s50 (w_in tap, about 1.07 ns) or, while lock = 1, by seven} 40 -300 0 0 0.3 0.3 {}
T {(w_out tap, about 2.5 ns): refw / divw clock the window flip-flops. cclk (counter clock) follows after both.} 40 -260 0 0 0.3 0.3 {}
N 260 0 200 0 {lab=}
N 340 0 510 0 {lab=}
N 590 0 760 0 {lab=}
N 840 0 925 0 {lab=}
N 925 0 1010 0 {lab=}
N 1090 0 1260 0 {lab=}
N 1340 0 1510 0 {lab=}
N 1590 0 1760 0 {lab=}
N 1840 0 1880 0 {lab=}
N 2160 80 2100 80 {lab=}
N 2160 120 2100 120 {lab=}
N 2160 160 2100 160 {lab=}
N 2240 100 2300 100 {lab=}
N 260 300 200 300 {lab=}
N 340 300 510 300 {lab=}
N 590 300 760 300 {lab=}
N 840 300 925 300 {lab=}
N 925 300 1010 300 {lab=}
N 1090 300 1260 300 {lab=}
N 1340 300 1510 300 {lab=}
N 1590 300 1760 300 {lab=}
N 1840 300 1880 300 {lab=}
N 2160 380 2100 380 {lab=}
N 2160 420 2100 420 {lab=}
N 2160 460 2100 460 {lab=}
N 2240 400 2300 400 {lab=}
N 2160 -100 2100 -100 {lab=}
N 2240 -100 2410 -100 {lab=}
N 2490 -100 2550 -100 {lab=}
N 100 600 180 600 {lab=}
N 100 660 180 660 {lab=}
N 100 720 180 720 {lab=}
N 2750 600 2530 600 {lab=}
N 2750 660 2530 660 {lab=}
N 2750 720 2530 720 {lab=}
N 100 800 180 800 {lab=}
N 100 860 180 860 {lab=}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 300 0 0 0 {name=xwr1 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 200 0 0 0 {name=l_refclk_1 sig_type=std_logic lab=refclk}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 550 0 0 0 {name=xwr2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 800 0 0 0 {name=xwr3 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 1050 0 0 0 {name=xwr4 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 925 0 0 1 {name=l_r3_5 sig_type=std_logic lab=r3}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 1300 0 0 0 {name=xwr5 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 1550 0 0 0 {name=xwr6 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 1800 0 0 0 {name=xwr7 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1880 0 0 1 {name=l_r7_9 sig_type=std_logic lab=r7}
C {sky130_stdcells/mux2_1.sym} 2200 100 0 0 {name=xwrm VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 2100 80 0 0 {name=l_r3_11 sig_type=std_logic lab=r3}
C {devices/lab_pin.sym} 2100 120 0 0 {name=l_r7_12 sig_type=std_logic lab=r7}
C {devices/lab_pin.sym} 2100 160 0 0 {name=l_lock_13 sig_type=std_logic lab=lock}
C {devices/lab_pin.sym} 2300 100 0 1 {name=l_refw_14 sig_type=std_logic lab=refw}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 300 300 0 0 {name=xwd1 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 200 300 0 0 {name=l_div_16 sig_type=std_logic lab=div}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 550 300 0 0 {name=xwd2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 800 300 0 0 {name=xwd3 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 1050 300 0 0 {name=xwd4 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 925 300 0 1 {name=l_d3_20 sig_type=std_logic lab=d3}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 1300 300 0 0 {name=xwd5 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 1550 300 0 0 {name=xwd6 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/clkdlybuf4s50_1.sym} 1800 300 0 0 {name=xwd7 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1880 300 0 1 {name=l_d7_24 sig_type=std_logic lab=d7}
C {sky130_stdcells/mux2_1.sym} 2200 400 0 0 {name=xwdm VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 2100 380 0 0 {name=l_d3_26 sig_type=std_logic lab=d3}
C {devices/lab_pin.sym} 2100 420 0 0 {name=l_d7_27 sig_type=std_logic lab=d7}
C {devices/lab_pin.sym} 2100 460 0 0 {name=l_lock_28 sig_type=std_logic lab=lock}
C {devices/lab_pin.sym} 2300 400 0 1 {name=l_divw_29 sig_type=std_logic lab=divw}
C {sky130_stdcells/clkdlybuf4s25_1.sym} 2200 -100 0 0 {name=xcc1 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/buf_1.sym} 2450 -100 0 0 {name=xcc2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 2100 -100 0 0 {name=l_r7_32 sig_type=std_logic lab=r7}
C {devices/lab_pin.sym} 2550 -100 0 1 {name=l_cclk_33 sig_type=std_logic lab=cclk}
C {devices/ipin.sym} 100 600 0 0 {name=p_refclk lab=refclk}
C {devices/lab_pin.sym} 180 600 0 1 {name=l_refclk_35 sig_type=std_logic lab=refclk}
C {devices/ipin.sym} 100 660 0 0 {name=p_div lab=div}
C {devices/lab_pin.sym} 180 660 0 1 {name=l_div_37 sig_type=std_logic lab=div}
C {devices/ipin.sym} 100 720 0 0 {name=p_lock lab=lock}
C {devices/lab_pin.sym} 180 720 0 1 {name=l_lock_39 sig_type=std_logic lab=lock}
C {devices/opin.sym} 2750 600 0 1 {name=p_refw lab=refw}
C {devices/lab_pin.sym} 2530 600 0 0 {name=l_refw_41 sig_type=std_logic lab=refw}
C {devices/opin.sym} 2750 660 0 1 {name=p_divw lab=divw}
C {devices/lab_pin.sym} 2530 660 0 0 {name=l_divw_43 sig_type=std_logic lab=divw}
C {devices/opin.sym} 2750 720 0 1 {name=p_cclk lab=cclk}
C {devices/lab_pin.sym} 2530 720 0 0 {name=l_cclk_45 sig_type=std_logic lab=cclk}
C {devices/iopin.sym} 100 800 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 180 800 0 1 {name=l_VDDD_47 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 100 860 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 180 860 0 1 {name=l_VSSD_49 sig_type=std_logic lab=VSSD}
