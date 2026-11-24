v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_sscp_hv: pulsed-Gm charge pump, no current mirror. Five slices; each slice's output drain x is steered to vctl (loop filter) during ckg and to vdump otherwise; each complementary drain xc sits on vdump, so vdump sees no net} 40 -1060 0 0 0.3 0.3 {}
T {AC current while v1 tracks the ring. The dump buffer holds vdump at vctl. pb comes from a replica half-slice whose input sits at VDDA/2; buses drawn as wires (v1p, v1m, ib, pb on top; x, vdump at the bottom); enables by name} 40 -1020 0 0 0.3 0.3 {}
N 470 80 470 400 {lab=}
N 470 400 600 400 {lab=}
N 490 120 490 440 {lab=}
N 490 440 600 440 {lab=}
N 510 160 510 480 {lab=}
N 510 480 600 480 {lab=}
N 530 200 530 520 {lab=}
N 530 520 600 520 {lab=}
N 600 560 560 560 {lab=}
N 600 600 560 600 {lab=}
N 800 480 840 480 {lab=}
N 840 480 840 1000 {lab=}
N 800 520 860 520 {lab=}
N 860 520 860 1040 {lab=}
N 660 350 660 320 {lab=}
N 660 650 660 680 {lab=}
N 1170 80 1170 400 {lab=}
N 1170 400 1300 400 {lab=}
N 1190 120 1190 440 {lab=}
N 1190 440 1300 440 {lab=}
N 1210 160 1210 480 {lab=}
N 1210 480 1300 480 {lab=}
N 1230 200 1230 520 {lab=}
N 1230 520 1300 520 {lab=}
N 1300 560 1260 560 {lab=}
N 1300 600 1260 600 {lab=}
N 1500 480 1540 480 {lab=}
N 1540 480 1540 1000 {lab=}
N 1500 520 1560 520 {lab=}
N 1560 520 1560 1040 {lab=}
N 1360 350 1360 320 {lab=}
N 1360 650 1360 680 {lab=}
N 1870 80 1870 400 {lab=}
N 1870 400 2000 400 {lab=}
N 1890 120 1890 440 {lab=}
N 1890 440 2000 440 {lab=}
N 1910 160 1910 480 {lab=}
N 1910 480 2000 480 {lab=}
N 1930 200 1930 520 {lab=}
N 1930 520 2000 520 {lab=}
N 2000 560 1960 560 {lab=}
N 2000 600 1960 600 {lab=}
N 2200 480 2240 480 {lab=}
N 2240 480 2240 1000 {lab=}
N 2200 520 2260 520 {lab=}
N 2260 520 2260 1040 {lab=}
N 2060 350 2060 320 {lab=}
N 2060 650 2060 680 {lab=}
N 2570 80 2570 400 {lab=}
N 2570 400 2700 400 {lab=}
N 2590 120 2590 440 {lab=}
N 2590 440 2700 440 {lab=}
N 2610 160 2610 480 {lab=}
N 2610 480 2700 480 {lab=}
N 2630 200 2630 520 {lab=}
N 2630 520 2700 520 {lab=}
N 2700 560 2660 560 {lab=}
N 2700 600 2660 600 {lab=}
N 2900 480 2940 480 {lab=}
N 2940 480 2940 1000 {lab=}
N 2900 520 2960 520 {lab=}
N 2960 520 2960 1040 {lab=}
N 2760 350 2760 320 {lab=}
N 2760 650 2760 680 {lab=}
N 3270 80 3270 400 {lab=}
N 3270 400 3400 400 {lab=}
N 3290 120 3290 440 {lab=}
N 3290 440 3400 440 {lab=}
N 3310 160 3310 480 {lab=}
N 3310 480 3400 480 {lab=}
N 3330 200 3330 520 {lab=}
N 3330 520 3400 520 {lab=}
N 3400 560 3360 560 {lab=}
N 3400 600 3360 600 {lab=}
N 3600 480 3640 480 {lab=}
N 3640 480 3640 1000 {lab=}
N 3600 520 3660 520 {lab=}
N 3660 520 3660 1040 {lab=}
N 3460 350 3460 320 {lab=}
N 3460 650 3460 680 {lab=}
N 250 80 3270 80 {lab=}
N 250 120 3290 120 {lab=}
N 250 160 3310 160 {lab=}
N 250 200 3330 200 {lab=}
N 840 1000 3960 1000 {lab=}
N 860 1040 5460 1040 {lab=}
N 3960 560 3960 1000 {lab=}
N 3960 1000 3960 1460 {lab=}
N 3960 560 4060 560 {lab=}
N 3960 1460 4060 1460 {lab=}
N 4060 600 4000 600 {lab=}
N 4060 640 4000 640 {lab=}
N 4120 510 4120 480 {lab=}
N 4120 690 4120 720 {lab=}
N 4060 1500 4000 1500 {lab=}
N 4060 1540 4000 1540 {lab=}
N 4120 1410 4120 1380 {lab=}
N 4120 1590 4120 1620 {lab=}
N 4260 1500 4340 1500 {lab=}
N 4260 600 4610 600 {lab=}
N 4610 600 4610 1160 {lab=}
N 4610 1160 4880 1160 {lab=}
N 4880 1160 4880 1460 {lab=}
N 4880 1460 4960 1460 {lab=}
N 4610 600 5860 600 {lab=}
N 5160 1500 5240 1500 {lab=}
N 5660 1870 5660 1810 {lab=}
N 5660 1930 5660 1990 {lab=}
N 4960 1500 4910 1500 {lab=}
N 4960 1540 4910 1540 {lab=}
N 5020 1410 5020 1380 {lab=}
N 5020 1590 5020 1620 {lab=}
N 280 -300 240 -300 {lab=}
N 240 -300 240 -370 {lab=}
N 240 -370 320 -370 {lab=}
N 320 -370 320 -330 {lab=}
N 320 -370 320 -410 {lab=}
N 320 -270 320 -240 {lab=}
N 1320 -910 1320 -940 {lab=}
N 1280 -880 1220 -880 {lab=}
N 1320 -850 1320 -710 {lab=}
N 1320 -650 1320 -450 {lab=}
N 1280 -680 1240 -680 {lab=}
N 1240 -680 1240 -550 {lab=}
N 1240 -550 1320 -550 {lab=}
N 1240 -680 1180 -680 {lab=}
N 1320 -390 1320 -260 {lab=}
N 1320 -200 1320 -70 {lab=}
N 1280 -230 1220 -230 {lab=}
N 1280 -40 1220 -40 {lab=}
N 1320 -10 1320 20 {lab=}
N 800 -670 800 -710 {lab=}
N 800 -610 800 -390 {lab=}
N 800 -330 800 -290 {lab=}
N 780 -640 720 -640 {lab=}
N 780 -360 720 -360 {lab=}
N 800 -500 960 -500 {lab=}
N 960 -500 960 -420 {lab=}
N 960 -420 1280 -420 {lab=}
N 60 1300 140 1300 {lab=}
N 60 1350 140 1350 {lab=}
N 60 1400 140 1400 {lab=}
N 60 1450 140 1450 {lab=}
N 60 1500 140 1500 {lab=}
N 60 1550 140 1550 {lab=}
N 60 1600 140 1600 {lab=}
N 60 1650 140 1650 {lab=}
N 60 1700 140 1700 {lab=}
N 60 1750 140 1750 {lab=}
N 60 1800 140 1800 {lab=}
N 60 1850 140 1850 {lab=}
N 60 1900 140 1900 {lab=}
N 60 1950 140 1950 {lab=}
N 60 2000 140 2000 {lab=}
N 60 2050 140 2050 {lab=}
N 60 -960 140 -960 {lab=}
N 60 2300 140 2300 {lab=}
C {sspll_sscp_hv_slice.sym} 700 500 0 0 {name=xs1}
C {sspll_sscp_hv_slice.sym} 1400 500 0 0 {name=xs2}
C {sspll_sscp_hv_slice.sym} 2100 500 0 0 {name=xs3}
C {sspll_sscp_hv_slice.sym} 2800 500 0 0 {name=xs4}
C {sspll_sscp_hv_slice.sym} 3500 500 0 0 {name=xs5}
C {devices/lab_pin.sym} 560 560 0 0 {name=l_e1_5 sig_type=std_logic lab=e1}
C {devices/lab_pin.sym} 560 600 0 0 {name=l_eb1_6 sig_type=std_logic lab=eb1}
C {devices/lab_pin.sym} 660 320 0 0 {name=l_VDDA_7 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 660 680 0 0 {name=l_VSSA_8 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1260 560 0 0 {name=l_e2_9 sig_type=std_logic lab=e2}
C {devices/lab_pin.sym} 1260 600 0 0 {name=l_eb2_10 sig_type=std_logic lab=eb2}
C {devices/lab_pin.sym} 1360 320 0 0 {name=l_VDDA_11 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1360 680 0 0 {name=l_VSSA_12 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1960 560 0 0 {name=l_e3_13 sig_type=std_logic lab=e3}
C {devices/lab_pin.sym} 1960 600 0 0 {name=l_eb3_14 sig_type=std_logic lab=eb3}
C {devices/lab_pin.sym} 2060 320 0 0 {name=l_VDDA_15 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 2060 680 0 0 {name=l_VSSA_16 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 2660 560 0 0 {name=l_e4_17 sig_type=std_logic lab=e4}
C {devices/lab_pin.sym} 2660 600 0 0 {name=l_eb4_18 sig_type=std_logic lab=eb4}
C {devices/lab_pin.sym} 2760 320 0 0 {name=l_VDDA_19 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 2760 680 0 0 {name=l_VSSA_20 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 3360 560 0 0 {name=l_e5_21 sig_type=std_logic lab=e5}
C {devices/lab_pin.sym} 3360 600 0 0 {name=l_eb5_22 sig_type=std_logic lab=eb5}
C {devices/lab_pin.sym} 3460 320 0 0 {name=l_VDDA_23 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 3460 680 0 0 {name=l_VSSA_24 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 250 80 0 0 {name=l_v1p_25 sig_type=std_logic lab=v1p}
C {devices/lab_pin.sym} 250 120 0 0 {name=l_v1m_26 sig_type=std_logic lab=v1m}
C {devices/lab_pin.sym} 250 160 0 0 {name=l_ib_27 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 250 200 0 0 {name=l_pb_28 sig_type=std_logic lab=pb}
C {devices/lab_pin.sym} 5460 1040 0 0 {name=l_vdump_29 sig_type=std_logic lab=vdump}
C {sspll_sscp_hv_tg.sym} 4160 600 0 0 {name=xtf}
C {sspll_sscp_hv_tg.sym} 4160 1500 0 0 {name=xtd}
C {devices/lab_pin.sym} 4000 600 0 0 {name=l_ckg_32 sig_type=std_logic lab=ckg}
C {devices/lab_pin.sym} 4000 640 0 0 {name=l_ckgb_33 sig_type=std_logic lab=ckgb}
C {devices/lab_pin.sym} 4120 480 0 0 {name=l_VDDA_34 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 4120 720 0 0 {name=l_VSSA_35 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 4000 1500 0 0 {name=l_ckgb_36 sig_type=std_logic lab=ckgb}
C {devices/lab_pin.sym} 4000 1540 0 0 {name=l_ckg_37 sig_type=std_logic lab=ckg}
C {devices/lab_pin.sym} 4120 1380 0 0 {name=l_VDDA_38 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 4120 1620 0 0 {name=l_VSSA_39 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 4340 1500 0 1 {name=l_vdump_40 sig_type=std_logic lab=vdump}
C {sspll_sscp_hv_buf.sym} 5060 1500 0 0 {name=xbuf}
C {devices/iopin.sym} 5860 600 0 1 {name=p_vctl lab=vctl}
C {devices/lab_pin.sym} 5240 1500 0 1 {name=l_vdump_43 sig_type=std_logic lab=vdump}
C {sky130_fd_pr/cap_mim_m3_1.sym} 5660 1900 0 0 {name=XCDUMP W=22.4 L=22.4 MF=2 model=cap_mim_m3_1 spiceprefix=X}
C {devices/lab_pin.sym} 5660 1810 0 0 {name=l_vdump_45 sig_type=std_logic lab=vdump}
C {devices/lab_pin.sym} 5660 1990 0 0 {name=l_VSSA_46 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 4910 1500 0 0 {name=l_ib_47 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 4910 1540 0 0 {name=l_pll_en_48 sig_type=std_logic lab=pll_en}
C {devices/lab_pin.sym} 5020 1380 0 0 {name=l_VDDA_49 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 5020 1620 0 0 {name=l_VSSA_50 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 300 -300 0 0 {name=XNB L=8.0 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 320 -410 0 0 {name=l_ib_52 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 320 -240 0 0 {name=l_VSSA_53 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1300 -880 0 0 {name=XRPE L=0.5 W=2 nf=1 mult=12 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1300 -680 0 0 {name=XRP L=4.0 W=4 nf=1 mult=12 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/lab_pin.sym} 1320 -940 0 0 {name=l_VDDA_56 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1220 -880 0 0 {name=l_VSSA_57 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1300 -420 0 0 {name=XRD L=1.0 W=4 nf=1 mult=6 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 1180 -680 0 0 {name=l_pb_59 sig_type=std_logic lab=pb}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1300 -230 0 0 {name=XRE L=0.5 W=1 nf=1 mult=12 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1300 -40 0 0 {name=XRT L=8.0 W=1 nf=1 mult=12 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 1220 -230 0 0 {name=l_pll_en_62 sig_type=std_logic lab=pll_en}
C {devices/lab_pin.sym} 1220 -40 0 0 {name=l_ib_63 sig_type=std_logic lab=ib}
C {devices/lab_pin.sym} 1320 20 0 0 {name=l_VSSA_64 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 800 -640 0 0 {name=XRC1 L=150.0 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 800 -360 0 0 {name=XRC2 L=150.0 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 800 -710 0 0 {name=l_VDDA_67 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 800 -290 0 0 {name=l_VSSA_68 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 720 -640 0 0 {name=l_VSSA_69 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 720 -360 0 0 {name=l_VSSA_70 sig_type=std_logic lab=VSSA}
C {devices/ipin.sym} 60 1300 0 0 {name=p_v1p lab=v1p}
C {devices/lab_pin.sym} 140 1300 0 1 {name=l_v1p_72 sig_type=std_logic lab=v1p}
C {devices/ipin.sym} 60 1350 0 0 {name=p_v1m lab=v1m}
C {devices/lab_pin.sym} 140 1350 0 1 {name=l_v1m_74 sig_type=std_logic lab=v1m}
C {devices/ipin.sym} 60 1400 0 0 {name=p_ckg lab=ckg}
C {devices/lab_pin.sym} 140 1400 0 1 {name=l_ckg_76 sig_type=std_logic lab=ckg}
C {devices/ipin.sym} 60 1450 0 0 {name=p_ckgb lab=ckgb}
C {devices/lab_pin.sym} 140 1450 0 1 {name=l_ckgb_78 sig_type=std_logic lab=ckgb}
C {devices/iopin.sym} 60 1500 0 0 {name=p_ib lab=ib}
C {devices/lab_pin.sym} 140 1500 0 1 {name=l_ib_80 sig_type=std_logic lab=ib}
C {devices/ipin.sym} 60 1550 0 0 {name=p_e1 lab=e1}
C {devices/lab_pin.sym} 140 1550 0 1 {name=l_e1_82 sig_type=std_logic lab=e1}
C {devices/ipin.sym} 60 1600 0 0 {name=p_e2 lab=e2}
C {devices/lab_pin.sym} 140 1600 0 1 {name=l_e2_84 sig_type=std_logic lab=e2}
C {devices/ipin.sym} 60 1650 0 0 {name=p_e3 lab=e3}
C {devices/lab_pin.sym} 140 1650 0 1 {name=l_e3_86 sig_type=std_logic lab=e3}
C {devices/ipin.sym} 60 1700 0 0 {name=p_e4 lab=e4}
C {devices/lab_pin.sym} 140 1700 0 1 {name=l_e4_88 sig_type=std_logic lab=e4}
C {devices/ipin.sym} 60 1750 0 0 {name=p_e5 lab=e5}
C {devices/lab_pin.sym} 140 1750 0 1 {name=l_e5_90 sig_type=std_logic lab=e5}
C {devices/ipin.sym} 60 1800 0 0 {name=p_eb1 lab=eb1}
C {devices/lab_pin.sym} 140 1800 0 1 {name=l_eb1_92 sig_type=std_logic lab=eb1}
C {devices/ipin.sym} 60 1850 0 0 {name=p_eb2 lab=eb2}
C {devices/lab_pin.sym} 140 1850 0 1 {name=l_eb2_94 sig_type=std_logic lab=eb2}
C {devices/ipin.sym} 60 1900 0 0 {name=p_eb3 lab=eb3}
C {devices/lab_pin.sym} 140 1900 0 1 {name=l_eb3_96 sig_type=std_logic lab=eb3}
C {devices/ipin.sym} 60 1950 0 0 {name=p_eb4 lab=eb4}
C {devices/lab_pin.sym} 140 1950 0 1 {name=l_eb4_98 sig_type=std_logic lab=eb4}
C {devices/ipin.sym} 60 2000 0 0 {name=p_eb5 lab=eb5}
C {devices/lab_pin.sym} 140 2000 0 1 {name=l_eb5_100 sig_type=std_logic lab=eb5}
C {devices/ipin.sym} 60 2050 0 0 {name=p_pll_en lab=pll_en}
C {devices/lab_pin.sym} 140 2050 0 1 {name=l_pll_en_102 sig_type=std_logic lab=pll_en}
C {devices/iopin.sym} 60 -960 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -960 0 1 {name=l_VDDA_104 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 2300 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 2300 0 1 {name=l_VSSA_106 sig_type=std_logic lab=VSSA}
