v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ncb_hv: noise-cancellation block. Bias (vff -> pd, nb) and one delay line in -> out; code lines c0-c3 (VDDA = capacitor in) and their complements c0b-c3b} 40 -460 0 0 0.3 0.3 {}
N 400 0 340 0 {lab=}
N 600 -20 660 -20 {lab=}
N 600 20 660 20 {lab=}
N 1300 -200 1240 -200 {lab=}
N 1300 -160 1240 -160 {lab=}
N 1300 -120 1240 -120 {lab=}
N 1300 -80 1240 -80 {lab=}
N 1300 -40 1240 -40 {lab=}
N 1300 0 1240 0 {lab=}
N 1300 40 1240 40 {lab=}
N 1300 80 1240 80 {lab=}
N 1300 120 1240 120 {lab=}
N 1300 160 1240 160 {lab=}
N 1300 200 1240 200 {lab=}
N 1500 0 1560 0 {lab=}
N 460 -70 460 -100 {lab=}
N 460 70 460 100 {lab=}
N 1360 -250 1360 -280 {lab=}
N 1360 250 1360 280 {lab=}
N 60 800 140 800 {lab=}
N 60 850 140 850 {lab=}
N 60 900 140 900 {lab=}
N 60 950 140 950 {lab=}
N 60 1000 140 1000 {lab=}
N 60 1050 140 1050 {lab=}
N 60 1100 140 1100 {lab=}
N 60 1150 140 1150 {lab=}
N 60 1200 140 1200 {lab=}
N 60 1250 140 1250 {lab=}
N 2100 800 2200 800 {lab=}
N 60 1400 140 1400 {lab=}
N 60 1450 140 1450 {lab=}
C {sspll_ncb_hv_bias.sym} 500 0 0 0 {name=xb}
C {sspll_ncb_hv_line.sym} 1400 0 0 0 {name=xl}
C {devices/lab_pin.sym} 340 0 0 0 {name=l_vff_2 sig_type=std_logic lab=vff}
C {devices/lab_pin.sym} 660 -20 0 1 {name=l_nb_3 sig_type=std_logic lab=nb}
C {devices/lab_pin.sym} 660 20 0 1 {name=l_pd_4 sig_type=std_logic lab=pd}
C {devices/lab_pin.sym} 1240 -200 0 0 {name=l_in_5 sig_type=std_logic lab=in}
C {devices/lab_pin.sym} 1240 -160 0 0 {name=l_nb_6 sig_type=std_logic lab=nb}
C {devices/lab_pin.sym} 1240 -120 0 0 {name=l_pd_7 sig_type=std_logic lab=pd}
C {devices/lab_pin.sym} 1240 -80 0 0 {name=l_c0_8 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 1240 -40 0 0 {name=l_c1_9 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 1240 0 0 0 {name=l_c2_10 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 1240 40 0 0 {name=l_c3_11 sig_type=std_logic lab=c3}
C {devices/lab_pin.sym} 1240 80 0 0 {name=l_c0b_12 sig_type=std_logic lab=c0b}
C {devices/lab_pin.sym} 1240 120 0 0 {name=l_c1b_13 sig_type=std_logic lab=c1b}
C {devices/lab_pin.sym} 1240 160 0 0 {name=l_c2b_14 sig_type=std_logic lab=c2b}
C {devices/lab_pin.sym} 1240 200 0 0 {name=l_c3b_15 sig_type=std_logic lab=c3b}
C {devices/lab_pin.sym} 1560 0 0 1 {name=l_out_16 sig_type=std_logic lab=out}
C {devices/lab_pin.sym} 460 -100 0 0 {name=l_VDDA_17 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 460 100 0 0 {name=l_VSSA_18 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1360 -280 0 0 {name=l_VDDA_19 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1360 280 0 0 {name=l_VSSA_20 sig_type=std_logic lab=VSSA}
C {devices/ipin.sym} 60 800 0 0 {name=p_in lab=in}
C {devices/lab_pin.sym} 140 800 0 1 {name=l_in_22 sig_type=std_logic lab=in}
C {devices/ipin.sym} 60 850 0 0 {name=p_vff lab=vff}
C {devices/lab_pin.sym} 140 850 0 1 {name=l_vff_24 sig_type=std_logic lab=vff}
C {devices/ipin.sym} 60 900 0 0 {name=p_c0 lab=c0}
C {devices/lab_pin.sym} 140 900 0 1 {name=l_c0_26 sig_type=std_logic lab=c0}
C {devices/ipin.sym} 60 950 0 0 {name=p_c1 lab=c1}
C {devices/lab_pin.sym} 140 950 0 1 {name=l_c1_28 sig_type=std_logic lab=c1}
C {devices/ipin.sym} 60 1000 0 0 {name=p_c2 lab=c2}
C {devices/lab_pin.sym} 140 1000 0 1 {name=l_c2_30 sig_type=std_logic lab=c2}
C {devices/ipin.sym} 60 1050 0 0 {name=p_c3 lab=c3}
C {devices/lab_pin.sym} 140 1050 0 1 {name=l_c3_32 sig_type=std_logic lab=c3}
C {devices/ipin.sym} 60 1100 0 0 {name=p_c0b lab=c0b}
C {devices/lab_pin.sym} 140 1100 0 1 {name=l_c0b_34 sig_type=std_logic lab=c0b}
C {devices/ipin.sym} 60 1150 0 0 {name=p_c1b lab=c1b}
C {devices/lab_pin.sym} 140 1150 0 1 {name=l_c1b_36 sig_type=std_logic lab=c1b}
C {devices/ipin.sym} 60 1200 0 0 {name=p_c2b lab=c2b}
C {devices/lab_pin.sym} 140 1200 0 1 {name=l_c2b_38 sig_type=std_logic lab=c2b}
C {devices/ipin.sym} 60 1250 0 0 {name=p_c3b lab=c3b}
C {devices/lab_pin.sym} 140 1250 0 1 {name=l_c3b_40 sig_type=std_logic lab=c3b}
C {devices/opin.sym} 2200 800 0 1 {name=p_out lab=out}
C {devices/lab_pin.sym} 2100 800 0 0 {name=l_out_42 sig_type=std_logic lab=out}
C {devices/iopin.sym} 60 1400 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 1400 0 1 {name=l_VDDA_44 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 1450 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 1450 0 1 {name=l_VSSA_46 sig_type=std_logic lab=VSSA}
