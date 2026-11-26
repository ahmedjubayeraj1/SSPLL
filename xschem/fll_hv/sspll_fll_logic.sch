v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_fll_logic: PFD + dead zone, lock-detector windows and lock detector (sky130_fd_sc_hd on VDDD / VSSD).} 40 -400 0 0 0.3 0.3 {}
N 460 -110 460 -150 {lab=}
N 460 110 460 150 {lab=}
N 460 510 460 470 {lab=}
N 460 690 460 730 {lab=}
N 1260 150 1260 110 {lab=}
N 1260 450 1260 490 {lab=}
N 400 -60 340 -60 {lab=}
N 400 560 340 560 {lab=}
N 400 -20 340 -20 {lab=}
N 400 600 340 600 {lab=}
N 400 20 340 20 {lab=}
N 400 60 340 60 {lab=}
N 600 -60 660 -60 {lab=}
N 600 -20 660 -20 {lab=}
N 600 20 660 20 {lab=}
N 600 60 660 60 {lab=}
N 400 640 340 640 {lab=}
N 600 560 660 560 {lab=}
N 600 600 660 600 {lab=}
N 600 640 660 640 {lab=}
N 1200 200 1140 200 {lab=}
N 1200 240 1140 240 {lab=}
N 1200 280 1140 280 {lab=}
N 1200 320 1140 320 {lab=}
N 1200 360 1140 360 {lab=}
N 1200 400 1140 400 {lab=}
N 1400 240 1460 240 {lab=}
N 1400 280 1460 280 {lab=}
N 1400 320 1460 320 {lab=}
N 1400 360 1460 360 {lab=}
N 100 1100 180 1100 {lab=}
N 100 1160 180 1160 {lab=}
N 100 1220 180 1220 {lab=}
N 2000 1100 1780 1100 {lab=}
N 2000 1160 1780 1160 {lab=}
N 2000 1220 1780 1220 {lab=}
N 2000 1280 1780 1280 {lab=}
N 2000 1340 1780 1340 {lab=}
N 100 1300 180 1300 {lab=}
N 100 1360 180 1360 {lab=}
C {sspll_fll_pfd.sym} 500 0 0 0 {name=xpfd}
C {sspll_fll_win.sym} 500 600 0 0 {name=xwin}
C {sspll_fll_lockdet.sym} 1300 300 0 0 {name=xld}
C {devices/lab_pin.sym} 460 -150 0 0 {name=l_VDDD_3 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 460 150 0 0 {name=l_VSSD_4 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 460 470 0 0 {name=l_VDDD_5 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 460 730 0 0 {name=l_VSSD_6 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 1260 110 0 0 {name=l_VDDD_7 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1260 490 0 0 {name=l_VSSD_8 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 340 -60 0 0 {name=l_refclk_9 sig_type=std_logic lab=refclk}
C {devices/lab_pin.sym} 340 560 0 0 {name=l_refclk_10 sig_type=std_logic lab=refclk}
C {devices/lab_pin.sym} 340 -20 0 0 {name=l_div_11 sig_type=std_logic lab=div}
C {devices/lab_pin.sym} 340 600 0 0 {name=l_div_12 sig_type=std_logic lab=div}
C {devices/lab_pin.sym} 340 20 0 0 {name=l_fll_en_13 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 340 60 0 0 {name=l_act_14 sig_type=std_logic lab=act}
C {devices/lab_pin.sym} 660 -60 0 1 {name=l_up_15 sig_type=std_logic lab=up}
C {devices/lab_pin.sym} 660 -20 0 1 {name=l_dn_16 sig_type=std_logic lab=dn}
C {devices/lab_pin.sym} 660 20 0 1 {name=l_upg_17 sig_type=std_logic lab=upg}
C {devices/lab_pin.sym} 660 60 0 1 {name=l_dng_18 sig_type=std_logic lab=dng}
C {devices/lab_pin.sym} 340 640 0 0 {name=l_lock_19 sig_type=std_logic lab=lock}
C {devices/lab_pin.sym} 660 560 0 1 {name=l_refw_20 sig_type=std_logic lab=refw}
C {devices/lab_pin.sym} 660 600 0 1 {name=l_divw_21 sig_type=std_logic lab=divw}
C {devices/lab_pin.sym} 660 640 0 1 {name=l_cclk_22 sig_type=std_logic lab=cclk}
C {devices/lab_pin.sym} 1140 200 0 0 {name=l_up_23 sig_type=std_logic lab=up}
C {devices/lab_pin.sym} 1140 240 0 0 {name=l_dn_24 sig_type=std_logic lab=dn}
C {devices/lab_pin.sym} 1140 280 0 0 {name=l_refw_25 sig_type=std_logic lab=refw}
C {devices/lab_pin.sym} 1140 320 0 0 {name=l_divw_26 sig_type=std_logic lab=divw}
C {devices/lab_pin.sym} 1140 360 0 0 {name=l_cclk_27 sig_type=std_logic lab=cclk}
C {devices/lab_pin.sym} 1140 400 0 0 {name=l_fll_en_28 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 1460 240 0 1 {name=l_lock_29 sig_type=std_logic lab=lock}
C {devices/lab_pin.sym} 1460 280 0 1 {name=l_act_30 sig_type=std_logic lab=act}
C {devices/lab_pin.sym} 1460 320 0 1 {name=l_lock_det_31 sig_type=std_logic lab=lock_det}
C {devices/lab_pin.sym} 1460 360 0 1 {name=l_fll_dir_32 sig_type=std_logic lab=fll_dir}
C {devices/ipin.sym} 100 1100 0 0 {name=p_refclk lab=refclk}
C {devices/lab_pin.sym} 180 1100 0 1 {name=l_refclk_34 sig_type=std_logic lab=refclk}
C {devices/ipin.sym} 100 1160 0 0 {name=p_div lab=div}
C {devices/lab_pin.sym} 180 1160 0 1 {name=l_div_36 sig_type=std_logic lab=div}
C {devices/ipin.sym} 100 1220 0 0 {name=p_fll_en lab=fll_en}
C {devices/lab_pin.sym} 180 1220 0 1 {name=l_fll_en_38 sig_type=std_logic lab=fll_en}
C {devices/opin.sym} 2000 1100 0 1 {name=p_upg lab=upg}
C {devices/lab_pin.sym} 1780 1100 0 0 {name=l_upg_40 sig_type=std_logic lab=upg}
C {devices/opin.sym} 2000 1160 0 1 {name=p_dng lab=dng}
C {devices/lab_pin.sym} 1780 1160 0 0 {name=l_dng_42 sig_type=std_logic lab=dng}
C {devices/opin.sym} 2000 1220 0 1 {name=p_act lab=act}
C {devices/lab_pin.sym} 1780 1220 0 0 {name=l_act_44 sig_type=std_logic lab=act}
C {devices/opin.sym} 2000 1280 0 1 {name=p_lock_det lab=lock_det}
C {devices/lab_pin.sym} 1780 1280 0 0 {name=l_lock_det_46 sig_type=std_logic lab=lock_det}
C {devices/opin.sym} 2000 1340 0 1 {name=p_fll_dir lab=fll_dir}
C {devices/lab_pin.sym} 1780 1340 0 0 {name=l_fll_dir_48 sig_type=std_logic lab=fll_dir}
C {devices/iopin.sym} 100 1300 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 180 1300 0 1 {name=l_VDDD_50 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 100 1360 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 180 1360 0 1 {name=l_VSSD_52 sig_type=std_logic lab=VSSD}
