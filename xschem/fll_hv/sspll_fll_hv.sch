v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_fll_hv (step 81): clkp / 16 against refclk; PFD with dead zone and lock detector on VDDD; level shifters;} 40 -500 0 0 0.3 0.3 {}
T {60 uA current-steering charge pump on VDDA into the loop filter (vctl). The pump is off while lock_det = 1.} 40 -460 0 0 0.3 0.3 {}
N 100 0 300 0 {lab=}
N 500 0 580 0 {lab=}
N 900 0 840 0 {lab=}
N 100 -300 180 -300 {lab=}
N 900 -40 840 -40 {lab=}
N 100 -360 180 -360 {lab=}
N 900 40 840 40 {lab=}
N 360 -50 360 -90 {lab=}
N 360 50 360 90 {lab=}
N 960 -130 960 -170 {lab=}
N 960 130 960 170 {lab=}
N 1100 -80 1160 -80 {lab=}
N 1600 -250 1540 -250 {lab=}
N 1800 -270 1860 -270 {lab=}
N 1800 -230 1860 -230 {lab=}
N 1660 -320 1660 -360 {lab=}
N 1700 -320 1700 -360 {lab=}
N 1660 -180 1660 -140 {lab=}
N 1700 -180 1700 -140 {lab=}
N 1100 -40 1160 -40 {lab=}
N 1600 50 1540 50 {lab=}
N 1800 30 1860 30 {lab=}
N 1800 70 1860 70 {lab=}
N 1660 -20 1660 -60 {lab=}
N 1700 -20 1700 -60 {lab=}
N 1660 120 1660 160 {lab=}
N 1700 120 1700 160 {lab=}
N 1100 0 1160 0 {lab=}
N 1600 350 1540 350 {lab=}
N 1800 330 1860 330 {lab=}
N 1800 370 1860 370 {lab=}
N 1660 280 1660 240 {lab=}
N 1700 280 1700 240 {lab=}
N 1660 420 1660 460 {lab=}
N 1700 420 1700 460 {lab=}
N 2200 -100 2140 -100 {lab=}
N 2200 -60 2140 -60 {lab=}
N 2200 -20 2140 -20 {lab=}
N 2200 20 2140 20 {lab=}
N 2200 60 2140 60 {lab=}
N 2200 100 2140 100 {lab=}
N 2260 -150 2260 -190 {lab=}
N 2260 150 2260 190 {lab=}
N 2400 0 2600 0 {lab=}
N 100 500 180 500 {lab=}
N 1100 40 1160 40 {lab=}
N 1100 80 1160 80 {lab=}
N 2700 500 2480 500 {lab=}
N 2700 560 2480 560 {lab=}
N 100 600 180 600 {lab=}
N 100 660 180 660 {lab=}
N 100 720 180 720 {lab=}
N 100 780 180 780 {lab=}
C {sspll_fll_div16.sym} 400 0 0 0 {name=xdv}
C {sspll_fll_logic.sym} 1000 0 0 0 {name=xlg}
C {devices/ipin.sym} 100 0 0 0 {name=p_clkp lab=clkp}
C {devices/lab_pin.sym} 580 0 0 1 {name=l_div_3 sig_type=std_logic lab=div}
C {devices/lab_pin.sym} 840 0 0 0 {name=l_div_4 sig_type=std_logic lab=div}
C {devices/ipin.sym} 100 -300 0 0 {name=p_refclk lab=refclk}
C {devices/lab_pin.sym} 180 -300 0 1 {name=l_refclk_6 sig_type=std_logic lab=refclk}
C {devices/lab_pin.sym} 840 -40 0 0 {name=l_refclk_7 sig_type=std_logic lab=refclk}
C {devices/ipin.sym} 100 -360 0 0 {name=p_fll_en lab=fll_en}
C {devices/lab_pin.sym} 180 -360 0 1 {name=l_fll_en_9 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 840 40 0 0 {name=l_fll_en_10 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 360 -90 0 0 {name=l_VDDD_11 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 360 90 0 0 {name=l_VSSD_12 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 960 -170 0 0 {name=l_VDDD_13 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 960 170 0 0 {name=l_VSSD_14 sig_type=std_logic lab=VSSD}
C {../cco_hv/sspll_ls_1v8_3v3.sym} 1700 -250 0 0 {name=xlu}
C {devices/lab_pin.sym} 1160 -80 0 1 {name=l_upg_16 sig_type=std_logic lab=upg}
C {devices/lab_pin.sym} 1540 -250 0 0 {name=l_upg_17 sig_type=std_logic lab=upg}
C {devices/lab_pin.sym} 1860 -270 0 1 {name=l_up5_18 sig_type=std_logic lab=up5}
C {devices/lab_pin.sym} 1860 -230 0 1 {name=l_up5b_19 sig_type=std_logic lab=up5b}
C {devices/lab_pin.sym} 1660 -360 0 0 {name=l_VDDD_20 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1700 -360 0 1 {name=l_VDDA_21 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1660 -140 0 0 {name=l_VSSA_22 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1700 -140 0 1 {name=l_VSSD_23 sig_type=std_logic lab=VSSD}
C {../cco_hv/sspll_ls_1v8_3v3.sym} 1700 50 0 0 {name=xld}
C {devices/lab_pin.sym} 1160 -40 0 1 {name=l_dng_25 sig_type=std_logic lab=dng}
C {devices/lab_pin.sym} 1540 50 0 0 {name=l_dng_26 sig_type=std_logic lab=dng}
C {devices/lab_pin.sym} 1860 30 0 1 {name=l_dn5_27 sig_type=std_logic lab=dn5}
C {devices/lab_pin.sym} 1860 70 0 1 {name=l_dn5b_28 sig_type=std_logic lab=dn5b}
C {devices/lab_pin.sym} 1660 -60 0 0 {name=l_VDDD_29 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1700 -60 0 1 {name=l_VDDA_30 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1660 160 0 0 {name=l_VSSA_31 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1700 160 0 1 {name=l_VSSD_32 sig_type=std_logic lab=VSSD}
C {../cco_hv/sspll_ls_1v8_3v3.sym} 1700 350 0 0 {name=xla}
C {devices/lab_pin.sym} 1160 0 0 1 {name=l_act_34 sig_type=std_logic lab=act}
C {devices/lab_pin.sym} 1540 350 0 0 {name=l_act_35 sig_type=std_logic lab=act}
C {devices/lab_pin.sym} 1860 330 0 1 {name=l_act5_36 sig_type=std_logic lab=act5}
C {devices/lab_pin.sym} 1860 370 0 1 {name=l_act5b_37 sig_type=std_logic lab=act5b}
C {devices/lab_pin.sym} 1660 240 0 0 {name=l_VDDD_38 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1700 240 0 1 {name=l_VDDA_39 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1660 460 0 0 {name=l_VSSA_40 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1700 460 0 1 {name=l_VSSD_41 sig_type=std_logic lab=VSSD}
C {sspll_fll_cp.sym} 2300 0 0 0 {name=xcp}
C {devices/lab_pin.sym} 2140 -100 0 0 {name=l_ib_43 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 2140 -60 0 0 {name=l_up5_44 sig_type=std_logic lab=up5}
C {devices/lab_pin.sym} 2140 -20 0 0 {name=l_up5b_45 sig_type=std_logic lab=up5b}
C {devices/lab_pin.sym} 2140 20 0 0 {name=l_dn5_46 sig_type=std_logic lab=dn5}
C {devices/lab_pin.sym} 2140 60 0 0 {name=l_dn5b_47 sig_type=std_logic lab=dn5b}
C {devices/lab_pin.sym} 2140 100 0 0 {name=l_act5b_48 sig_type=std_logic lab=act5b}
C {devices/lab_pin.sym} 2260 -190 0 0 {name=l_VDDA_49 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 2260 190 0 0 {name=l_VSSA_50 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 2600 0 0 1 {name=p_vctl lab=vctl}
C {devices/iopin.sym} 100 500 0 0 {name=p_ib lab=ib}
C {devices/lab_pin.sym} 180 500 0 1 {name=l_ib_53 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 1160 40 0 1 {name=l_lock_det_54 sig_type=std_logic lab=lock_det}
C {devices/lab_pin.sym} 1160 80 0 1 {name=l_fll_dir_55 sig_type=std_logic lab=fll_dir}
C {devices/opin.sym} 2700 500 0 1 {name=p_lock_det lab=lock_det}
C {devices/lab_pin.sym} 2480 500 0 0 {name=l_lock_det_57 sig_type=std_logic lab=lock_det}
C {devices/opin.sym} 2700 560 0 1 {name=p_fll_dir lab=fll_dir}
C {devices/lab_pin.sym} 2480 560 0 0 {name=l_fll_dir_59 sig_type=std_logic lab=fll_dir}
C {devices/iopin.sym} 100 600 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 180 600 0 1 {name=l_VDDA_61 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 100 660 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 180 660 0 1 {name=l_VDDD_63 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 100 720 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 180 720 0 1 {name=l_VSSA_65 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 100 780 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 180 780 0 1 {name=l_VSSD_67 sig_type=std_logic lab=VSSD}
