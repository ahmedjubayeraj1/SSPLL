v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_d2s_hv_top: diff-to-SE amplifier with the ffnc_en level shifter (1.8 V control -> 3.3 V en / en_b). inp = v2m, inm = v2p: vff = V_0 - G (v2p - v2m)} 40 -460 0 0 0.3 0.3 {}
N 400 0 340 0 {lab=}
N 600 -20 660 -20 {lab=}
N 600 20 660 20 {lab=}
N 1200 -60 1140 -60 {lab=}
N 1200 -20 1140 -20 {lab=}
N 1200 20 1140 20 {lab=}
N 1200 60 1140 60 {lab=}
N 1400 0 1460 0 {lab=}
N 460 -70 460 -100 {lab=}
N 500 -70 500 -100 {lab=}
N 460 70 460 100 {lab=}
N 500 70 500 100 {lab=}
N 1260 -110 1260 -140 {lab=}
N 1260 110 1260 140 {lab=}
N 60 600 140 600 {lab=}
N 60 650 140 650 {lab=}
N 60 700 140 700 {lab=}
N 60 750 140 750 {lab=}
N 1900 600 2000 600 {lab=}
N 60 -350 140 -350 {lab=}
N 60 -300 140 -300 {lab=}
N 60 1000 140 1000 {lab=}
N 60 1050 140 1050 {lab=}
C {../cco_hv/sspll_ls_1v8_3v3.sym} 500 0 0 0 {name=xls}
C {sspll_d2s_hv.sym} 1300 0 0 0 {name=xa}
C {devices/lab_pin.sym} 340 0 0 0 {name=l_ffnc_en_2 sig_type=std_logic lab=ffnc_en}
C {devices/lab_pin.sym} 660 -20 0 1 {name=l_en_3 sig_type=std_logic lab=en}
C {devices/lab_pin.sym} 660 20 0 1 {name=l_en_b_4 sig_type=std_logic lab=en_b}
C {devices/lab_pin.sym} 1140 -60 0 0 {name=l_v2m_5 sig_type=std_logic lab=v2m}
C {devices/lab_pin.sym} 1140 -20 0 0 {name=l_v2p_6 sig_type=std_logic lab=v2p}
C {devices/lab_pin.sym} 1140 20 0 0 {name=l_ib_7 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 1140 60 0 0 {name=l_en_b_8 sig_type=std_logic lab=en_b}
C {devices/lab_pin.sym} 1460 0 0 1 {name=l_vff_9 sig_type=std_logic lab=vff}
C {devices/lab_pin.sym} 460 -100 0 0 {name=l_VDDD_10 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 500 -100 0 1 {name=l_VDDA_11 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 460 100 0 0 {name=l_VSSA_12 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 500 100 0 1 {name=l_VSSD_13 sig_type=std_logic lab=VSSD}
C {devices/lab_pin.sym} 1260 -140 0 0 {name=l_VDDA_14 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1260 140 0 0 {name=l_VSSA_15 sig_type=std_logic lab=VSSA}
C {devices/ipin.sym} 60 600 0 0 {name=p_v2p lab=v2p}
C {devices/lab_pin.sym} 140 600 0 1 {name=l_v2p_17 sig_type=std_logic lab=v2p}
C {devices/ipin.sym} 60 650 0 0 {name=p_v2m lab=v2m}
C {devices/lab_pin.sym} 140 650 0 1 {name=l_v2m_19 sig_type=std_logic lab=v2m}
C {devices/iopin.sym} 60 700 0 0 {name=p_ib lab=ib}
C {devices/lab_pin.sym} 140 700 0 1 {name=l_ib_21 sig_type=std_logic lab=ib}
C {devices/ipin.sym} 60 750 0 0 {name=p_ffnc_en lab=ffnc_en}
C {devices/lab_pin.sym} 140 750 0 1 {name=l_ffnc_en_23 sig_type=std_logic lab=ffnc_en}
C {devices/opin.sym} 2000 600 0 1 {name=p_vff lab=vff}
C {devices/lab_pin.sym} 1900 600 0 0 {name=l_vff_25 sig_type=std_logic lab=vff}
C {devices/iopin.sym} 60 -350 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -350 0 1 {name=l_VDDA_27 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 -300 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 140 -300 0 1 {name=l_VDDD_29 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 60 1000 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 1000 0 1 {name=l_VSSA_31 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 60 1050 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 140 1050 0 1 {name=l_VSSD_33 sig_type=std_logic lab=VSSD}
