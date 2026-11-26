v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_cco: current-fed supply of the ring VCO (all devices touching VDDA are 3.3 V devices)} 40 -620 0 0 0.35 0.35 {}
T {IBIAS -> DAC (cco_code) -> MREF diode -> 10 Mohm / 7.3 pF filter -> MOUT (x25) -> ring node vring; active clamp keeps vring <= VDDL; VTEST injects a test tone} 40 -575 0 0 0.25 0.25 {}
T {control bits arrive on VDDD (1.8 V) and are level-shifted to 3.3 V (left column); 3.3 V control nets are connected by name} 40 -545 0 0 0.25 0.25 {}
N 100 -380 200 -380 {lab=}
N 400 -400 440 -400 {lab=}
N 400 -360 440 -360 {lab=}
N 260 -450 260 -470 {lab=}
N 300 -450 300 -470 {lab=}
N 260 -310 260 -290 {lab=}
N 100 -180 200 -180 {lab=}
N 400 -200 440 -200 {lab=}
N 400 -160 440 -160 {lab=}
N 260 -250 260 -270 {lab=}
N 300 -250 300 -270 {lab=}
N 260 -110 260 -90 {lab=}
N 100 20 200 20 {lab=}
N 400 0 440 0 {lab=}
N 400 40 440 40 {lab=}
N 260 -50 260 -70 {lab=}
N 300 -50 300 -70 {lab=}
N 260 90 260 110 {lab=}
N 100 220 200 220 {lab=}
N 400 200 440 200 {lab=}
N 400 240 440 240 {lab=}
N 260 150 260 130 {lab=}
N 300 150 300 130 {lab=}
N 260 290 260 310 {lab=}
N 100 420 200 420 {lab=}
N 400 400 440 400 {lab=}
N 400 440 440 440 {lab=}
N 260 350 260 330 {lab=}
N 300 350 300 330 {lab=}
N 260 490 260 510 {lab=}
N 100 620 200 620 {lab=}
N 400 600 440 600 {lab=}
N 400 640 440 640 {lab=}
N 260 550 260 530 {lab=}
N 300 550 300 530 {lab=}
N 260 690 260 710 {lab=}
N 100 820 200 820 {lab=}
N 400 800 440 800 {lab=}
N 400 840 440 840 {lab=}
N 260 750 260 730 {lab=}
N 300 750 300 730 {lab=}
N 260 890 260 910 {lab=}
N 1150 -400 2000 -400 {lab=}
N 2000 -400 2750 -400 {lab=}
N 1150 420 2000 420 {lab=}
N 2000 420 2750 420 {lab=}
N 100 1080 220 1080 {lab=}
N 1700 560 1830 560 {lab=}
N 640 250 700 250 {lab=}
N 700 250 700 330 {lab=}
N 700 330 800 330 {lab=}
N 800 370 760 370 {lab=}
N 800 410 760 410 {lab=}
N 800 450 760 450 {lab=}
N 800 490 760 490 {lab=}
N 800 530 760 530 {lab=}
N 800 570 760 570 {lab=}
N 860 620 860 680 {lab=}
N 780 120 780 100 {lab=}
N 780 100 700 100 {lab=}
N 700 100 700 250 {lab=}
N 780 180 780 210 {lab=}
N 740 150 710 150 {lab=}
N 1320 -230 1320 -400 {lab=}
N 1720 -230 1720 -400 {lab=}
N 1280 -200 1260 -200 {lab=}
N 1260 -200 1260 -120 {lab=}
N 1260 -120 1320 -120 {lab=}
N 1320 -170 1320 -120 {lab=}
N 1320 -120 1320 40 {lab=}
N 1320 40 1320 450 {lab=}
N 1320 450 1000 450 {lab=}
N 1320 40 1400 40 {lab=}
N 1460 90 1460 140 {lab=}
N 1600 40 1640 40 {lab=}
N 1640 40 1640 -60 {lab=}
N 1640 -60 1640 -200 {lab=}
N 1640 -200 1680 -200 {lab=}
N 1500 -140 1500 -400 {lab=}
N 1500 -80 1500 -60 {lab=}
N 1500 -60 1640 -60 {lab=}
N 1970 -330 1970 -400 {lab=}
N 1970 -270 1970 -250 {lab=}
N 1970 -250 1640 -250 {lab=}
N 1640 -250 1640 -200 {lab=}
N 1930 -300 1900 -300 {lab=}
N 1720 -170 1720 0 {lab=}
N 1720 0 2270 0 {lab=}
N 2270 0 2530 0 {lab=}
N 2530 0 2750 0 {lab=}
N 1830 560 1870 560 {lab=}
N 1870 560 1870 570 {lab=}
N 1870 630 1870 690 {lab=}
N 1870 690 1870 750 {lab=}
N 1830 600 1800 600 {lab=}
N 1800 600 1800 690 {lab=}
N 1800 690 1870 690 {lab=}
N 1870 810 1870 860 {lab=}
N 1830 780 1800 780 {lab=}
N 2070 0 2070 90 {lab=}
N 2030 120 1990 120 {lab=}
N 1990 120 1990 720 {lab=}
N 1990 720 1870 720 {lab=}
N 2070 150 2070 260 {lab=}
N 2070 320 2070 420 {lab=}
N 2050 290 2030 290 {lab=}
N 2070 230 2190 230 {lab=}
N 2190 230 2190 290 {lab=}
N 2190 290 2230 290 {lab=}
N 2270 260 2270 0 {lab=}
N 2270 320 2270 420 {lab=}
N 2420 -280 2420 -310 {lab=}
N 2640 -280 2640 -310 {lab=}
N 2420 -310 2640 -310 {lab=}
N 2640 -310 2750 -310 {lab=}
N 2420 -220 2420 -180 {lab=}
N 2640 -220 2640 -180 {lab=}
N 2420 -180 2530 -180 {lab=}
N 2530 -180 2640 -180 {lab=}
N 2380 -250 2350 -250 {lab=}
N 2600 -250 2570 -250 {lab=}
N 2530 -180 2530 -120 {lab=}
N 2530 -60 2530 0 {lab=}
N 2510 -90 2490 -90 {lab=}
C {sspll_ls_1v8_3v3.sym} 300 -380 0 0 {name=xls_c0}
C {devices/ipin.sym} 100 -380 0 0 {name=p_code0 lab=code0}
C {devices/lab_pin.sym} 440 -400 0 1 {name=l_c0_2 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 440 -360 0 1 {name=l_c0b_3 sig_type=std_logic lab=c0b}
C {devices/lab_pin.sym} 260 -470 0 0 {name=l_VDDD_4 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 300 -470 0 1 {name=l_VDDA_5 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 260 -290 0 0 {name=l_VSS_6 sig_type=std_logic lab=VSS}
C {sspll_ls_1v8_3v3.sym} 300 -180 0 0 {name=xls_c1}
C {devices/ipin.sym} 100 -180 0 0 {name=p_code1 lab=code1}
C {devices/lab_pin.sym} 440 -200 0 1 {name=l_c1_9 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 440 -160 0 1 {name=l_c1b_10 sig_type=std_logic lab=c1b}
C {devices/lab_pin.sym} 260 -270 0 0 {name=l_VDDD_11 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 300 -270 0 1 {name=l_VDDA_12 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 260 -90 0 0 {name=l_VSS_13 sig_type=std_logic lab=VSS}
C {sspll_ls_1v8_3v3.sym} 300 20 0 0 {name=xls_c2}
C {devices/ipin.sym} 100 20 0 0 {name=p_code2 lab=code2}
C {devices/lab_pin.sym} 440 0 0 1 {name=l_c2_16 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 440 40 0 1 {name=l_c2b_17 sig_type=std_logic lab=c2b}
C {devices/lab_pin.sym} 260 -70 0 0 {name=l_VDDD_18 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 300 -70 0 1 {name=l_VDDA_19 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 260 110 0 0 {name=l_VSS_20 sig_type=std_logic lab=VSS}
C {sspll_ls_1v8_3v3.sym} 300 220 0 0 {name=xls_c3}
C {devices/ipin.sym} 100 220 0 0 {name=p_code3 lab=code3}
C {devices/lab_pin.sym} 440 200 0 1 {name=l_c3_23 sig_type=std_logic lab=c3}
C {devices/lab_pin.sym} 440 240 0 1 {name=l_c3b_24 sig_type=std_logic lab=c3b}
C {devices/lab_pin.sym} 260 130 0 0 {name=l_VDDD_25 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 300 130 0 1 {name=l_VDDA_26 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 260 310 0 0 {name=l_VSS_27 sig_type=std_logic lab=VSS}
C {sspll_ls_1v8_3v3.sym} 300 420 0 0 {name=xls_c4}
C {devices/ipin.sym} 100 420 0 0 {name=p_code4 lab=code4}
C {devices/lab_pin.sym} 440 400 0 1 {name=l_c4_30 sig_type=std_logic lab=c4}
C {devices/lab_pin.sym} 440 440 0 1 {name=l_c4b_31 sig_type=std_logic lab=c4b}
C {devices/lab_pin.sym} 260 330 0 0 {name=l_VDDD_32 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 300 330 0 1 {name=l_VDDA_33 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 260 510 0 0 {name=l_VSS_34 sig_type=std_logic lab=VSS}
C {sspll_ls_1v8_3v3.sym} 300 620 0 0 {name=xls_en}
C {devices/ipin.sym} 100 620 0 0 {name=p_pll_en lab=pll_en}
C {devices/lab_pin.sym} 440 600 0 1 {name=l_en_37 sig_type=std_logic lab=en}
C {devices/lab_pin.sym} 440 640 0 1 {name=l_enb_38 sig_type=std_logic lab=enb}
C {devices/lab_pin.sym} 260 530 0 0 {name=l_VDDD_39 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 300 530 0 1 {name=l_VDDA_40 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 260 710 0 0 {name=l_VSS_41 sig_type=std_logic lab=VSS}
C {sspll_ls_1v8_3v3.sym} 300 820 0 0 {name=xls_vt}
C {devices/ipin.sym} 100 820 0 0 {name=p_vtest_en lab=vtest_en}
C {devices/lab_pin.sym} 440 800 0 1 {name=l_vt_44 sig_type=std_logic lab=vt}
C {devices/lab_pin.sym} 440 840 0 1 {name=l_vtb_45 sig_type=std_logic lab=vtb}
C {devices/lab_pin.sym} 260 730 0 0 {name=l_VDDD_46 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 300 730 0 1 {name=l_VDDA_47 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 260 910 0 0 {name=l_VSS_48 sig_type=std_logic lab=VSS}
C {devices/iopin.sym} 1150 -400 0 0 {name=p_VDDA lab=VDDA}
C {devices/iopin.sym} 1150 420 0 0 {name=p_VSS lab=VSS}
C {devices/iopin.sym} 100 1080 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 220 1080 0 1 {name=l_VDDD_52 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 1700 560 0 0 {name=p_VDDL lab=VDDL}
C {sspll_cco_dac.sym} 900 450 0 0 {name=xdac}
C {devices/iopin.sym} 640 250 0 0 {name=p_ibias lab=ibias}
C {devices/lab_pin.sym} 760 370 0 0 {name=l_en_56 sig_type=std_logic lab=en}
C {devices/lab_pin.sym} 760 410 0 0 {name=l_c0_57 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 760 450 0 0 {name=l_c1_58 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 760 490 0 0 {name=l_c2_59 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 760 530 0 0 {name=l_c3_60 sig_type=std_logic lab=c3}
C {devices/lab_pin.sym} 760 570 0 0 {name=l_c4_61 sig_type=std_logic lab=c4}
C {devices/lab_pin.sym} 860 680 0 0 {name=l_VSS_62 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 760 150 0 0 {name=XNEN L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 780 210 0 0 {name=l_VSS_64 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 710 150 0 0 {name=l_enb_65 sig_type=std_logic lab=enb}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1300 -200 0 0 {name=XMREF L=2.0 W=40 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1700 -200 0 0 {name=XMOUT L=2.0 W=40 nf=2 mult=25 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sspll_cco_rf.sym} 1500 40 0 0 {name=xrf}
C {devices/lab_pin.sym} 1460 140 0 0 {name=l_VSS_69 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/cap_mim_m3_1.sym} 1500 -110 2 0 {name=XCF W=30 L=30 MF=4 model=cap_mim_m3_1 spiceprefix=X}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1950 -300 0 0 {name=XPEN L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 1900 -300 0 0 {name=l_en_72 sig_type=std_logic lab=en}
C {devices/iopin.sym} 2750 0 0 1 {name=p_vring lab=vring}
C {sky130_fd_pr/pfet3_01v8.sym} 1850 600 0 0 {name=XPREP L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDL}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1850 780 0 0 {name=XUREP L=4.0 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 1870 860 0 0 {name=l_VSS_76 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1800 780 0 0 {name=l_ibias_77 sig_type=std_logic lab=ibias}
C {sky130_fd_pr/pfet3_01v8.sym} 2050 120 0 0 {name=XPSEN L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=vring}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 2070 290 0 0 {name=XRS L=56.0 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 2030 290 0 0 {name=l_VSS_80 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/nfet3_01v8.sym} 2250 290 0 0 {name=XNSH L=0.15 W=20 nf=4 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 2400 -250 0 0 {name=XTGN L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 2620 -250 0 0 {name=XTGP L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/ipin.sym} 2750 -310 0 1 {name=p_vtest lab=vtest}
C {devices/lab_pin.sym} 2350 -250 0 0 {name=l_vt_85 sig_type=std_logic lab=vt}
C {devices/lab_pin.sym} 2570 -250 0 0 {name=l_vtb_86 sig_type=std_logic lab=vtb}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 2530 -90 0 0 {name=XRINJ L=3.39 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 2490 -90 0 0 {name=l_VSS_88 sig_type=std_logic lab=VSS}
