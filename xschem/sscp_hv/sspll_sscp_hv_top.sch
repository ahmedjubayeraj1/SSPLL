v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_sscp_hv_top: pulsed-Gm charge pump with its trim decoder; slices 1 and 2 follow pll_en (e12), slices 3-5 follow the decoded icp_trim, the dump buffer follows pll_en} 40 -460 0 0 0.3 0.3 {}
N 400 -40 340 -40 {lab=}
N 400 0 340 0 {lab=}
N 400 40 340 40 {lab=}
N 600 -140 660 -140 {lab=}
N 600 -100 660 -100 {lab=}
N 600 -60 660 -60 {lab=}
N 600 -20 660 -20 {lab=}
N 600 20 660 20 {lab=}
N 600 60 660 60 {lab=}
N 600 100 660 100 {lab=}
N 600 140 660 140 {lab=}
N 1200 -300 1140 -300 {lab=}
N 1200 -260 1140 -260 {lab=}
N 1200 -220 1140 -220 {lab=}
N 1200 -180 1140 -180 {lab=}
N 1200 -140 1140 -140 {lab=}
N 1200 -100 1140 -100 {lab=}
N 1200 -60 1140 -60 {lab=}
N 1200 -20 1140 -20 {lab=}
N 1200 20 1140 20 {lab=}
N 1200 60 1140 60 {lab=}
N 1200 100 1140 100 {lab=}
N 1200 140 1140 140 {lab=}
N 1200 180 1140 180 {lab=}
N 1200 220 1140 220 {lab=}
N 1200 260 1140 260 {lab=}
N 1200 300 1140 300 {lab=}
N 1400 0 1460 0 {lab=}
N 460 -190 460 -220 {lab=}
N 500 -190 500 -220 {lab=}
N 460 190 460 220 {lab=}
N 500 190 500 220 {lab=}
N 1260 -350 1260 -380 {lab=}
N 1260 350 1260 380 {lab=}
N 60 700 140 700 {lab=}
N 60 750 140 750 {lab=}
N 60 800 140 800 {lab=}
N 60 850 140 850 {lab=}
N 60 900 140 900 {lab=}
N 60 950 140 950 {lab=}
N 60 1000 140 1000 {lab=}
N 60 1050 140 1050 {lab=}
N 1900 700 2000 700 {lab=}
N 60 -350 140 -350 {lab=}
N 60 -300 140 -300 {lab=}
N 60 1200 140 1200 {lab=}
N 60 1250 140 1250 {lab=}
C {sspll_sscp_hv_dec.sym} 500 0 0 0 {name=xdec}
C {sspll_sscp_hv.sym} 1300 0 0 0 {name=xgm}
C {devices/lab_pin.sym} 340 -40 0 0 {name=l_icp0_2 sig_type=std_logic lab=icp0}
C {devices/lab_pin.sym} 340 0 0 0 {name=l_icp1_3 sig_type=std_logic lab=icp1}
C {devices/lab_pin.sym} 340 40 0 0 {name=l_pll_en_4 sig_type=std_logic lab=pll_en}
C {devices/lab_pin.sym} 660 -140 0 1 {name=l_e12_5 sig_type=std_logic lab=e12}
C {devices/lab_pin.sym} 660 -100 0 1 {name=l_e3_6 sig_type=std_logic lab=e3}
C {devices/lab_pin.sym} 660 -60 0 1 {name=l_e4_7 sig_type=std_logic lab=e4}
C {devices/lab_pin.sym} 660 -20 0 1 {name=l_e5_8 sig_type=std_logic lab=e5}
C {devices/lab_pin.sym} 660 20 0 1 {name=l_e12_b_9 sig_type=std_logic lab=e12_b}
C {devices/lab_pin.sym} 660 60 0 1 {name=l_e3_b_10 sig_type=std_logic lab=e3_b}
C {devices/lab_pin.sym} 660 100 0 1 {name=l_e4_b_11 sig_type=std_logic lab=e4_b}
C {devices/lab_pin.sym} 660 140 0 1 {name=l_e5_b_12 sig_type=std_logic lab=e5_b}
C {devices/lab_pin.sym} 1140 -300 0 0 {name=l_v1p_13 sig_type=std_logic lab=v1p}
C {devices/lab_pin.sym} 1140 -260 0 0 {name=l_v1m_14 sig_type=std_logic lab=v1m}
C {devices/lab_pin.sym} 1140 -220 0 0 {name=l_ckg_15 sig_type=std_logic lab=ckg}
C {devices/lab_pin.sym} 1140 -180 0 0 {name=l_ckgb_16 sig_type=std_logic lab=ckgb}
C {devices/lab_pin.sym} 1140 -140 0 0 {name=l_ib_17 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 1140 -100 0 0 {name=l_e12_18 sig_type=std_logic lab=e12}
C {devices/lab_pin.sym} 1140 -60 0 0 {name=l_e12_19 sig_type=std_logic lab=e12}
C {devices/lab_pin.sym} 1140 -20 0 0 {name=l_e3_20 sig_type=std_logic lab=e3}
C {devices/lab_pin.sym} 1140 20 0 0 {name=l_e4_21 sig_type=std_logic lab=e4}
C {devices/lab_pin.sym} 1140 60 0 0 {name=l_e5_22 sig_type=std_logic lab=e5}
C {devices/lab_pin.sym} 1140 100 0 0 {name=l_e12_b_23 sig_type=std_logic lab=e12_b}
C {devices/lab_pin.sym} 1140 140 0 0 {name=l_e12_b_24 sig_type=std_logic lab=e12_b}
C {devices/lab_pin.sym} 1140 180 0 0 {name=l_e3_b_25 sig_type=std_logic lab=e3_b}
C {devices/lab_pin.sym} 1140 220 0 0 {name=l_e4_b_26 sig_type=std_logic lab=e4_b}
C {devices/lab_pin.sym} 1140 260 0 0 {name=l_e5_b_27 sig_type=std_logic lab=e5_b}
C {devices/lab_pin.sym} 1140 300 0 0 {name=l_e12_28 sig_type=std_logic lab=e12}
C {devices/lab_pin.sym} 1460 0 0 1 {name=l_vctl_29 sig_type=std_logic lab=vctl}
C {devices/lab_pin.sym} 460 -220 0 0 {name=l_VDDD_30 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 500 -220 0 1 {name=l_VDDA_31 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 460 220 0 0 {name=l_VSSA_32 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 500 220 0 1 {name=l_VSSD_33 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 1260 -380 0 0 {name=l_VDDA_34 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1260 380 0 0 {name=l_VSSA_35 sig_type=std_logic lab=VSSA}
C {devices/ipin.sym} 60 700 0 0 {name=p_v1p lab=v1p}
C {devices/lab_pin.sym} 140 700 0 1 {name=l_v1p_37 sig_type=std_logic lab=v1p}
C {devices/ipin.sym} 60 750 0 0 {name=p_v1m lab=v1m}
C {devices/lab_pin.sym} 140 750 0 1 {name=l_v1m_39 sig_type=std_logic lab=v1m}
C {devices/ipin.sym} 60 800 0 0 {name=p_ckg lab=ckg}
C {devices/lab_pin.sym} 140 800 0 1 {name=l_ckg_41 sig_type=std_logic lab=ckg}
C {devices/ipin.sym} 60 850 0 0 {name=p_ckgb lab=ckgb}
C {devices/lab_pin.sym} 140 850 0 1 {name=l_ckgb_43 sig_type=std_logic lab=ckgb}
C {devices/iopin.sym} 60 900 0 0 {name=p_ib lab=ib}
C {devices/lab_pin.sym} 140 900 0 1 {name=l_ib_45 sig_type=std_logic lab=ib}
C {devices/ipin.sym} 60 950 0 0 {name=p_icp0 lab=icp0}
C {devices/lab_pin.sym} 140 950 0 1 {name=l_icp0_47 sig_type=std_logic lab=icp0}
C {devices/ipin.sym} 60 1000 0 0 {name=p_icp1 lab=icp1}
C {devices/lab_pin.sym} 140 1000 0 1 {name=l_icp1_49 sig_type=std_logic lab=icp1}
C {devices/ipin.sym} 60 1050 0 0 {name=p_pll_en lab=pll_en}
C {devices/lab_pin.sym} 140 1050 0 1 {name=l_pll_en_51 sig_type=std_logic lab=pll_en}
C {devices/iopin.sym} 2000 700 0 1 {name=p_vctl lab=vctl}
C {devices/lab_pin.sym} 1900 700 0 0 {name=l_vctl_53 sig_type=std_logic lab=vctl}
C {devices/iopin.sym} 60 -350 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -350 0 1 {name=l_VDDA_55 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 -300 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 140 -300 0 1 {name=l_VDDD_57 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 60 1200 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 1200 0 1 {name=l_VSSA_59 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 60 1250 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 140 1250 0 1 {name=l_VSSD_61 sig_type=std_logic lab=VSSD}
