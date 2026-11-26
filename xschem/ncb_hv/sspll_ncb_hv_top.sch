v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ncb_hv_top: NCB with the 4-bit gain code g0-g3 (1.8 V control) shifted to the code lines: out -> ck, outb -> ckb (g_k = 1: 2^k unit capacitors on each starved node)} 40 -560 0 0 0.3 0.3 {}
N 400 0 340 0 {lab=}
N 600 -20 660 -20 {lab=}
N 600 20 660 20 {lab=}
N 460 -70 460 -100 {lab=}
N 500 -70 500 -100 {lab=}
N 460 70 460 100 {lab=}
N 500 70 500 100 {lab=}
N 400 400 340 400 {lab=}
N 600 380 660 380 {lab=}
N 600 420 660 420 {lab=}
N 460 330 460 300 {lab=}
N 500 330 500 300 {lab=}
N 460 470 460 500 {lab=}
N 500 470 500 500 {lab=}
N 400 800 340 800 {lab=}
N 600 780 660 780 {lab=}
N 600 820 660 820 {lab=}
N 460 730 460 700 {lab=}
N 500 730 500 700 {lab=}
N 460 870 460 900 {lab=}
N 500 870 500 900 {lab=}
N 400 1200 340 1200 {lab=}
N 600 1180 660 1180 {lab=}
N 600 1220 660 1220 {lab=}
N 460 1130 460 1100 {lab=}
N 500 1130 500 1100 {lab=}
N 460 1270 460 1300 {lab=}
N 500 1270 500 1300 {lab=}
N 1400 120 1340 120 {lab=}
N 1400 160 1340 160 {lab=}
N 1400 200 1340 200 {lab=}
N 1400 240 1340 240 {lab=}
N 1400 280 1340 280 {lab=}
N 1400 320 1340 320 {lab=}
N 1400 360 1340 360 {lab=}
N 1400 400 1340 400 {lab=}
N 1400 440 1340 440 {lab=}
N 1400 480 1340 480 {lab=}
N 1600 300 1660 300 {lab=}
N 1460 70 1460 40 {lab=}
N 1460 530 1460 560 {lab=}
N 60 1900 140 1900 {lab=}
N 60 1950 140 1950 {lab=}
N 60 2000 140 2000 {lab=}
N 60 2050 140 2050 {lab=}
N 60 2100 140 2100 {lab=}
N 60 2150 140 2150 {lab=}
N 2100 1900 2200 1900 {lab=}
N 60 2250 140 2250 {lab=}
N 60 2300 140 2300 {lab=}
N 60 2350 140 2350 {lab=}
N 60 2400 140 2400 {lab=}
C {../cco_hv/sspll_ls_1v8_3v3.sym} 500 0 0 0 {name=xls0}
C {devices/lab_pin.sym} 340 0 0 0 {name=l_g0_1 sig_type=std_logic lab=g0}
C {devices/lab_pin.sym} 660 -20 0 1 {name=l_c0_2 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 660 20 0 1 {name=l_c0b_3 sig_type=std_logic lab=c0b}
C {devices/lab_pin.sym} 460 -100 0 0 {name=l_VDDD_4 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 500 -100 0 1 {name=l_VDDA_5 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 460 100 0 0 {name=l_VSSA_6 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 500 100 0 1 {name=l_VSSD_7 sig_type=std_logic lab=VSSD}
C {../cco_hv/sspll_ls_1v8_3v3.sym} 500 400 0 0 {name=xls1}
C {devices/lab_pin.sym} 340 400 0 0 {name=l_g1_9 sig_type=std_logic lab=g1}
C {devices/lab_pin.sym} 660 380 0 1 {name=l_c1_10 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 660 420 0 1 {name=l_c1b_11 sig_type=std_logic lab=c1b}
C {devices/lab_pin.sym} 460 300 0 0 {name=l_VDDD_12 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 500 300 0 1 {name=l_VDDA_13 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 460 500 0 0 {name=l_VSSA_14 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 500 500 0 1 {name=l_VSSD_15 sig_type=std_logic lab=VSSD}
C {../cco_hv/sspll_ls_1v8_3v3.sym} 500 800 0 0 {name=xls2}
C {devices/lab_pin.sym} 340 800 0 0 {name=l_g2_17 sig_type=std_logic lab=g2}
C {devices/lab_pin.sym} 660 780 0 1 {name=l_c2_18 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 660 820 0 1 {name=l_c2b_19 sig_type=std_logic lab=c2b}
C {devices/lab_pin.sym} 460 700 0 0 {name=l_VDDD_20 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 500 700 0 1 {name=l_VDDA_21 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 460 900 0 0 {name=l_VSSA_22 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 500 900 0 1 {name=l_VSSD_23 sig_type=std_logic lab=VSSD}
C {../cco_hv/sspll_ls_1v8_3v3.sym} 500 1200 0 0 {name=xls3}
C {devices/lab_pin.sym} 340 1200 0 0 {name=l_g3_25 sig_type=std_logic lab=g3}
C {devices/lab_pin.sym} 660 1180 0 1 {name=l_c3_26 sig_type=std_logic lab=c3}
C {devices/lab_pin.sym} 660 1220 0 1 {name=l_c3b_27 sig_type=std_logic lab=c3b}
C {devices/lab_pin.sym} 460 1100 0 0 {name=l_VDDD_28 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 500 1100 0 1 {name=l_VDDA_29 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 460 1300 0 0 {name=l_VSSA_30 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 500 1300 0 1 {name=l_VSSD_31 sig_type=std_logic lab=VSSD}
C {sspll_ncb_hv.sym} 1500 300 0 0 {name=xa}
C {devices/lab_pin.sym} 1340 120 0 0 {name=l_in_33 sig_type=std_logic lab=in}
C {devices/lab_pin.sym} 1340 160 0 0 {name=l_vff_34 sig_type=std_logic lab=vff}
C {devices/lab_pin.sym} 1340 200 0 0 {name=l_c0_35 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 1340 240 0 0 {name=l_c1_36 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 1340 280 0 0 {name=l_c2_37 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 1340 320 0 0 {name=l_c3_38 sig_type=std_logic lab=c3}
C {devices/lab_pin.sym} 1340 360 0 0 {name=l_c0b_39 sig_type=std_logic lab=c0b}
C {devices/lab_pin.sym} 1340 400 0 0 {name=l_c1b_40 sig_type=std_logic lab=c1b}
C {devices/lab_pin.sym} 1340 440 0 0 {name=l_c2b_41 sig_type=std_logic lab=c2b}
C {devices/lab_pin.sym} 1340 480 0 0 {name=l_c3b_42 sig_type=std_logic lab=c3b}
C {devices/lab_pin.sym} 1660 300 0 1 {name=l_out_43 sig_type=std_logic lab=out}
C {devices/lab_pin.sym} 1460 40 0 0 {name=l_VDDA_44 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1460 560 0 0 {name=l_VSSA_45 sig_type=std_logic lab=VSSA}
C {devices/ipin.sym} 60 1900 0 0 {name=p_in lab=in}
C {devices/lab_pin.sym} 140 1900 0 1 {name=l_in_47 sig_type=std_logic lab=in}
C {devices/ipin.sym} 60 1950 0 0 {name=p_vff lab=vff}
C {devices/lab_pin.sym} 140 1950 0 1 {name=l_vff_49 sig_type=std_logic lab=vff}
C {devices/ipin.sym} 60 2000 0 0 {name=p_g0 lab=g0}
C {devices/lab_pin.sym} 140 2000 0 1 {name=l_g0_51 sig_type=std_logic lab=g0}
C {devices/ipin.sym} 60 2050 0 0 {name=p_g1 lab=g1}
C {devices/lab_pin.sym} 140 2050 0 1 {name=l_g1_53 sig_type=std_logic lab=g1}
C {devices/ipin.sym} 60 2100 0 0 {name=p_g2 lab=g2}
C {devices/lab_pin.sym} 140 2100 0 1 {name=l_g2_55 sig_type=std_logic lab=g2}
C {devices/ipin.sym} 60 2150 0 0 {name=p_g3 lab=g3}
C {devices/lab_pin.sym} 140 2150 0 1 {name=l_g3_57 sig_type=std_logic lab=g3}
C {devices/opin.sym} 2200 1900 0 1 {name=p_out lab=out}
C {devices/lab_pin.sym} 2100 1900 0 0 {name=l_out_59 sig_type=std_logic lab=out}
C {devices/iopin.sym} 60 2250 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 2250 0 1 {name=l_VDDA_61 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 2300 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 140 2300 0 1 {name=l_VDDD_63 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 60 2350 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 2350 0 1 {name=l_VSSA_65 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 60 2400 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 140 2400 0 1 {name=l_VSSD_67 sig_type=std_logic lab=VSSD}
