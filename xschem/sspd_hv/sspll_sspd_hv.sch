v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_sspd_hv: sub-sampling phase detector with hold. v1p - v1m (the fresh sample) goes to the pulsed Gm (step 79), v2p - v2m (held for a whole period) to the NCB amplifier} 40 -520 0 0 0.3 0.3 {}
T {clkp / clkm: the 5 V ring's buffered outputs (step 74 HV); cks/cksb, ckh/ckhb from the clock generator (step 77 HV, 3.3 V); every device 5 V-rated on VDDA} 40 -470 0 0 0.25 0.25 {}
N 60 -80 600 -80 {lab=}
N 60 520 600 520 {lab=}
N 800 -20 1300 -20 {lab=}
N 800 20 1300 20 {lab=}
N 600 -40 540 -40 {lab=}
N 600 0 540 0 {lab=}
N 600 40 540 40 {lab=}
N 600 80 540 80 {lab=}
N 660 -130 660 -150 {lab=}
N 660 130 660 150 {lab=}
N 800 580 1300 580 {lab=}
N 800 620 1300 620 {lab=}
N 600 560 540 560 {lab=}
N 600 600 540 600 {lab=}
N 600 640 540 640 {lab=}
N 600 680 540 680 {lab=}
N 660 470 660 450 {lab=}
N 660 730 660 750 {lab=}
N 60 1100 160 1100 {lab=}
N 60 1160 160 1160 {lab=}
N 60 1220 160 1220 {lab=}
N 60 1280 160 1280 {lab=}
N 60 -380 140 -380 {lab=}
N 60 1360 140 1360 {lab=}
C {sspll_sspd_hv_side.sym} 700 0 0 0 {name=xsp}
C {sspll_sspd_hv_side.sym} 700 600 0 0 {name=xsm}
C {devices/ipin.sym} 60 -80 0 0 {name=p_clkp lab=clkp}
C {devices/ipin.sym} 60 520 0 0 {name=p_clkm lab=clkm}
C {devices/opin.sym} 1300 -20 0 1 {name=p_v1p lab=v1p}
C {devices/opin.sym} 1300 20 0 1 {name=p_v2p lab=v2p}
C {devices/lab_pin.sym} 540 -40 0 0 {name=l_cks_6 sig_type=std_logic lab=cks}
C {devices/lab_pin.sym} 540 0 0 0 {name=l_cksb_7 sig_type=std_logic lab=cksb}
C {devices/lab_pin.sym} 540 40 0 0 {name=l_ckh_8 sig_type=std_logic lab=ckh}
C {devices/lab_pin.sym} 540 80 0 0 {name=l_ckhb_9 sig_type=std_logic lab=ckhb}
C {devices/lab_pin.sym} 660 -150 0 0 {name=l_VDDA_10 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 660 150 0 0 {name=l_VSS_11 sig_type=std_logic lab=VSS}
C {devices/opin.sym} 1300 580 0 1 {name=p_v1m lab=v1m}
C {devices/opin.sym} 1300 620 0 1 {name=p_v2m lab=v2m}
C {devices/lab_pin.sym} 540 560 0 0 {name=l_cks_14 sig_type=std_logic lab=cks}
C {devices/lab_pin.sym} 540 600 0 0 {name=l_cksb_15 sig_type=std_logic lab=cksb}
C {devices/lab_pin.sym} 540 640 0 0 {name=l_ckh_16 sig_type=std_logic lab=ckh}
C {devices/lab_pin.sym} 540 680 0 0 {name=l_ckhb_17 sig_type=std_logic lab=ckhb}
C {devices/lab_pin.sym} 660 450 0 0 {name=l_VDDA_18 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 660 750 0 0 {name=l_VSS_19 sig_type=std_logic lab=VSS}
C {devices/ipin.sym} 60 1100 0 0 {name=p_cks lab=cks}
C {devices/lab_pin.sym} 160 1100 0 1 {name=l_cks_21 sig_type=std_logic lab=cks}
C {devices/ipin.sym} 60 1160 0 0 {name=p_cksb lab=cksb}
C {devices/lab_pin.sym} 160 1160 0 1 {name=l_cksb_23 sig_type=std_logic lab=cksb}
C {devices/ipin.sym} 60 1220 0 0 {name=p_ckh lab=ckh}
C {devices/lab_pin.sym} 160 1220 0 1 {name=l_ckh_25 sig_type=std_logic lab=ckh}
C {devices/ipin.sym} 60 1280 0 0 {name=p_ckhb lab=ckhb}
C {devices/lab_pin.sym} 160 1280 0 1 {name=l_ckhb_27 sig_type=std_logic lab=ckhb}
C {devices/iopin.sym} 60 -380 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -380 0 1 {name=l_VDDA_29 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 1360 0 0 {name=p_VSS lab=VSS}
C {devices/lab_pin.sym} 140 1360 0 1 {name=l_VSS_31 sig_type=std_logic lab=VSS}
