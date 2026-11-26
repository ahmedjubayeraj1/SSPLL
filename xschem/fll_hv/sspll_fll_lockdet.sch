v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_fll_lockdet: o1 = up still high at refw, o2 = dn still high at divw, out = o1 + o2; inc = lock XNOR out.} 40 -460 0 0 0.3 0.3 {}
T {4-bit run counter c3..c0 (next = g ? c + 1 : 0, g = inc AND NOT term); term = c == 15 (unlocked) or c == 3 (locked);} 40 -420 0 0 0.3 0.3 {}
T {the lock flag toggles when inc AND term. act = fll_en AND NOT lock; lock_det = lock; fll_dir = o1 (ring slow).} 40 -380 0 0 0.3 0.3 {}
N 210 -220 150 -220 {lab=}
N 210 -200 150 -200 {lab=}
N 210 -180 150 -180 {lab=}
N 210 30 150 30 {lab=}
N 210 50 150 50 {lab=}
N 210 70 150 70 {lab=}
N 390 -220 480 -220 {lab=}
N 480 -220 480 -100 {lab=}
N 480 -100 540 -100 {lab=}
N 390 30 510 30 {lab=}
N 510 30 510 -60 {lab=}
N 510 -60 540 -60 {lab=}
N 660 -80 720 -80 {lab=}
N 720 -80 790 -80 {lab=}
N 790 -120 730 -120 {lab=}
N 910 -100 970 -100 {lab=}
N 1210 -250 1150 -250 {lab=}
N 1290 -250 1350 -250 {lab=}
N 1190 -130 1130 -130 {lab=}
N 1190 -90 1130 -90 {lab=}
N 1310 -110 1370 -110 {lab=}
N 1190 10 1130 10 {lab=}
N 1190 50 1130 50 {lab=}
N 1310 30 1370 30 {lab=}
N 1190 150 1130 150 {lab=}
N 1190 190 1130 190 {lab=}
N 1310 170 1370 170 {lab=}
N 1190 270 1130 270 {lab=}
N 1190 310 1130 310 {lab=}
N 1190 350 1130 350 {lab=}
N 1310 310 1370 310 {lab=}
N 1190 430 1130 430 {lab=}
N 1190 470 1130 470 {lab=}
N 1310 450 1370 450 {lab=}
N 1190 570 1130 570 {lab=}
N 1190 610 1130 610 {lab=}
N 1310 590 1370 590 {lab=}
N 1660 -270 1600 -270 {lab=}
N 1660 -230 1600 -230 {lab=}
N 1660 -190 1600 -190 {lab=}
N 1740 -250 1840 -250 {lab=}
N 1840 -250 1910 -250 {lab=}
N 1990 -250 2050 -250 {lab=}
N 1640 -70 1580 -70 {lab=}
N 1640 -30 1580 -30 {lab=}
N 1760 -50 1820 -50 {lab=}
N 1640 80 1580 80 {lab=}
N 1640 120 1580 120 {lab=}
N 1760 100 1820 100 {lab=}
N 2090 -270 2030 -270 {lab=}
N 2090 -230 2030 -230 {lab=}
N 2210 -250 2410 -250 {lab=}
N 2410 -270 2350 -270 {lab=}
N 2410 -230 2350 -230 {lab=}
N 2590 -270 2650 -270 {lab=}
N 2090 -70 2030 -70 {lab=}
N 2090 -30 2030 -30 {lab=}
N 2210 -50 2410 -50 {lab=}
N 2410 -70 2350 -70 {lab=}
N 2410 -30 2350 -30 {lab=}
N 2590 -70 2650 -70 {lab=}
N 2090 130 2030 130 {lab=}
N 2090 170 2030 170 {lab=}
N 2210 150 2410 150 {lab=}
N 2410 130 2350 130 {lab=}
N 2410 170 2350 170 {lab=}
N 2590 130 2650 130 {lab=}
N 2090 330 2030 330 {lab=}
N 2090 370 2030 370 {lab=}
N 2210 350 2410 350 {lab=}
N 2410 330 2350 330 {lab=}
N 2410 370 2350 370 {lab=}
N 2590 330 2650 330 {lab=}
N 2090 580 2030 580 {lab=}
N 2090 620 2030 620 {lab=}
N 2210 600 2410 600 {lab=}
N 2410 580 2350 580 {lab=}
N 2410 620 2350 620 {lab=}
N 2590 580 2650 580 {lab=}
N 260 400 200 400 {lab=}
N 340 400 490 400 {lab=}
N 490 360 430 360 {lab=}
N 610 380 670 380 {lab=}
N 260 600 200 600 {lab=}
N 340 600 400 600 {lab=}
N 260 750 200 750 {lab=}
N 340 750 400 750 {lab=}
N 100 950 180 950 {lab=}
N 100 1010 180 1010 {lab=}
N 100 1070 180 1070 {lab=}
N 100 1130 180 1130 {lab=}
N 100 1190 180 1190 {lab=}
N 100 1250 180 1250 {lab=}
N 2900 950 2680 950 {lab=}
N 2900 1010 2680 1010 {lab=}
N 2900 1070 2680 1070 {lab=}
N 2900 1130 2680 1130 {lab=}
N 100 1350 180 1350 {lab=}
N 100 1410 180 1410 {lab=}
C {sky130_stdcells/dfrtp_1.sym} 300 -200 0 0 {name=xo1 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/dfrtp_1.sym} 300 50 0 0 {name=xo2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 150 -220 0 0 {name=l_refw_2 sig_type=std_logic lab=refw}
C {devices/lab_pin.sym} 150 -200 0 0 {name=l_up_3 sig_type=std_logic lab=up}
C {devices/lab_pin.sym} 150 -180 0 0 {name=l_fll_en_4 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 150 30 0 0 {name=l_divw_5 sig_type=std_logic lab=divw}
C {devices/lab_pin.sym} 150 50 0 0 {name=l_dn_6 sig_type=std_logic lab=dn}
C {devices/lab_pin.sym} 150 70 0 0 {name=l_fll_en_7 sig_type=std_logic lab=fll_en}
C {sky130_stdcells/or2_1.sym} 600 -80 0 0 {name=xoo VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 480 -220 0 1 {name=l_o1_9 sig_type=std_logic lab=o1}
C {sky130_stdcells/xnor2_1.sym} 850 -100 0 0 {name=xix VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 720 -80 0 1 {name=l_out_11 sig_type=std_logic lab=out}
C {devices/lab_pin.sym} 730 -120 0 0 {name=l_lock_12 sig_type=std_logic lab=lock}
C {devices/lab_pin.sym} 970 -100 0 1 {name=l_inc_13 sig_type=std_logic lab=inc}
C {sky130_stdcells/inv_1.sym} 1250 -250 0 0 {name=xs0 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1150 -250 0 0 {name=l_c0_15 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 1350 -250 0 1 {name=l_s0_16 sig_type=std_logic lab=s0}
C {sky130_stdcells/xor2_1.sym} 1250 -110 0 0 {name=xs1 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1130 -130 0 0 {name=l_c1_18 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 1130 -90 0 0 {name=l_c0_19 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 1370 -110 0 1 {name=l_s1_20 sig_type=std_logic lab=s1}
C {sky130_stdcells/and2_1.sym} 1250 30 0 0 {name=xt2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1130 10 0 0 {name=l_c1_22 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 1130 50 0 0 {name=l_c0_23 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 1370 30 0 1 {name=l_t2_24 sig_type=std_logic lab=t2}
C {sky130_stdcells/xor2_1.sym} 1250 170 0 0 {name=xs2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1130 150 0 0 {name=l_c2_26 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 1130 190 0 0 {name=l_t2_27 sig_type=std_logic lab=t2}
C {devices/lab_pin.sym} 1370 170 0 1 {name=l_s2_28 sig_type=std_logic lab=s2}
C {sky130_stdcells/and3_1.sym} 1250 310 0 0 {name=xt3 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1130 270 0 0 {name=l_c2_30 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 1130 310 0 0 {name=l_c1_31 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 1130 350 0 0 {name=l_c0_32 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 1370 310 0 1 {name=l_t3_33 sig_type=std_logic lab=t3}
C {sky130_stdcells/xor2_1.sym} 1250 450 0 0 {name=xs3 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1130 430 0 0 {name=l_c3_35 sig_type=std_logic lab=c3}
C {devices/lab_pin.sym} 1130 470 0 0 {name=l_t3_36 sig_type=std_logic lab=t3}
C {devices/lab_pin.sym} 1370 450 0 1 {name=l_s3_37 sig_type=std_logic lab=s3}
C {sky130_stdcells/and2_1.sym} 1250 590 0 0 {name=xt4 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1130 570 0 0 {name=l_c3_39 sig_type=std_logic lab=c3}
C {devices/lab_pin.sym} 1130 610 0 0 {name=l_t3_40 sig_type=std_logic lab=t3}
C {devices/lab_pin.sym} 1370 590 0 1 {name=l_t4_41 sig_type=std_logic lab=t4}
C {sky130_stdcells/mux2_1.sym} 1700 -250 0 0 {name=xtm VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/inv_1.sym} 1950 -250 0 0 {name=xtn VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1600 -270 0 0 {name=l_t4_44 sig_type=std_logic lab=t4}
C {devices/lab_pin.sym} 1600 -230 0 0 {name=l_t2_45 sig_type=std_logic lab=t2}
C {devices/lab_pin.sym} 1600 -190 0 0 {name=l_lock_46 sig_type=std_logic lab=lock}
C {devices/lab_pin.sym} 1840 -250 0 1 {name=l_term_47 sig_type=std_logic lab=term}
C {devices/lab_pin.sym} 2050 -250 0 1 {name=l_nterm_48 sig_type=std_logic lab=nterm}
C {sky130_stdcells/and2_1.sym} 1700 -50 0 0 {name=xg VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/and2_1.sym} 1700 100 0 0 {name=xtg VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 1580 -70 0 0 {name=l_inc_51 sig_type=std_logic lab=inc}
C {devices/lab_pin.sym} 1580 -30 0 0 {name=l_nterm_52 sig_type=std_logic lab=nterm}
C {devices/lab_pin.sym} 1820 -50 0 1 {name=l_g_53 sig_type=std_logic lab=g}
C {devices/lab_pin.sym} 1580 80 0 0 {name=l_inc_54 sig_type=std_logic lab=inc}
C {devices/lab_pin.sym} 1580 120 0 0 {name=l_term_55 sig_type=std_logic lab=term}
C {devices/lab_pin.sym} 1820 100 0 1 {name=l_tg_56 sig_type=std_logic lab=tg}
C {sky130_stdcells/and2_1.sym} 2150 -250 0 0 {name=xn0 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/dfrtp_1.sym} 2500 -250 0 0 {name=xc0 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 2030 -270 0 0 {name=l_g_59 sig_type=std_logic lab=g}
C {devices/lab_pin.sym} 2030 -230 0 0 {name=l_s0_60 sig_type=std_logic lab=s0}
C {devices/lab_pin.sym} 2350 -270 0 0 {name=l_cclk_61 sig_type=std_logic lab=cclk}
C {devices/lab_pin.sym} 2350 -230 0 0 {name=l_fll_en_62 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 2650 -270 0 1 {name=l_c0_63 sig_type=std_logic lab=c0}
C {sky130_stdcells/and2_1.sym} 2150 -50 0 0 {name=xn1 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/dfrtp_1.sym} 2500 -50 0 0 {name=xc1 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 2030 -70 0 0 {name=l_g_66 sig_type=std_logic lab=g}
C {devices/lab_pin.sym} 2030 -30 0 0 {name=l_s1_67 sig_type=std_logic lab=s1}
C {devices/lab_pin.sym} 2350 -70 0 0 {name=l_cclk_68 sig_type=std_logic lab=cclk}
C {devices/lab_pin.sym} 2350 -30 0 0 {name=l_fll_en_69 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 2650 -70 0 1 {name=l_c1_70 sig_type=std_logic lab=c1}
C {sky130_stdcells/and2_1.sym} 2150 150 0 0 {name=xn2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/dfrtp_1.sym} 2500 150 0 0 {name=xc2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 2030 130 0 0 {name=l_g_73 sig_type=std_logic lab=g}
C {devices/lab_pin.sym} 2030 170 0 0 {name=l_s2_74 sig_type=std_logic lab=s2}
C {devices/lab_pin.sym} 2350 130 0 0 {name=l_cclk_75 sig_type=std_logic lab=cclk}
C {devices/lab_pin.sym} 2350 170 0 0 {name=l_fll_en_76 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 2650 130 0 1 {name=l_c2_77 sig_type=std_logic lab=c2}
C {sky130_stdcells/and2_1.sym} 2150 350 0 0 {name=xn3 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/dfrtp_1.sym} 2500 350 0 0 {name=xc3 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 2030 330 0 0 {name=l_g_80 sig_type=std_logic lab=g}
C {devices/lab_pin.sym} 2030 370 0 0 {name=l_s3_81 sig_type=std_logic lab=s3}
C {devices/lab_pin.sym} 2350 330 0 0 {name=l_cclk_82 sig_type=std_logic lab=cclk}
C {devices/lab_pin.sym} 2350 370 0 0 {name=l_fll_en_83 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 2650 330 0 1 {name=l_c3_84 sig_type=std_logic lab=c3}
C {sky130_stdcells/xor2_1.sym} 2150 600 0 0 {name=xlx VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/dfrtp_1.sym} 2500 600 0 0 {name=xlf VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 2030 580 0 0 {name=l_lock_87 sig_type=std_logic lab=lock}
C {devices/lab_pin.sym} 2030 620 0 0 {name=l_tg_88 sig_type=std_logic lab=tg}
C {devices/lab_pin.sym} 2350 580 0 0 {name=l_cclk_89 sig_type=std_logic lab=cclk}
C {devices/lab_pin.sym} 2350 620 0 0 {name=l_fll_en_90 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 2650 580 0 1 {name=l_lock_91 sig_type=std_logic lab=lock}
C {sky130_stdcells/inv_1.sym} 300 400 0 0 {name=xli VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/and2_1.sym} 550 380 0 0 {name=xla VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 200 400 0 0 {name=l_lock_94 sig_type=std_logic lab=lock}
C {devices/lab_pin.sym} 430 360 0 0 {name=l_fll_en_95 sig_type=std_logic lab=fll_en}
C {devices/lab_pin.sym} 670 380 0 1 {name=l_act_96 sig_type=std_logic lab=act}
C {sky130_stdcells/buf_1.sym} 300 600 0 0 {name=xob1 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {sky130_stdcells/buf_1.sym} 300 750 0 0 {name=xob2 VGND=VSSD VNB=VSSD VPB=VDDD VPWR=VDDD prefix=sky130_fd_sc_hd__}
C {devices/lab_pin.sym} 200 600 0 0 {name=l_lock_99 sig_type=std_logic lab=lock}
C {devices/lab_pin.sym} 400 600 0 1 {name=l_lock_det_100 sig_type=std_logic lab=lock_det}
C {devices/lab_pin.sym} 200 750 0 0 {name=l_o1_101 sig_type=std_logic lab=o1}
C {devices/lab_pin.sym} 400 750 0 1 {name=l_fll_dir_102 sig_type=std_logic lab=fll_dir}
C {devices/ipin.sym} 100 950 0 0 {name=p_up lab=up}
C {devices/lab_pin.sym} 180 950 0 1 {name=l_up_104 sig_type=std_logic lab=up}
C {devices/ipin.sym} 100 1010 0 0 {name=p_dn lab=dn}
C {devices/lab_pin.sym} 180 1010 0 1 {name=l_dn_106 sig_type=std_logic lab=dn}
C {devices/ipin.sym} 100 1070 0 0 {name=p_refw lab=refw}
C {devices/lab_pin.sym} 180 1070 0 1 {name=l_refw_108 sig_type=std_logic lab=refw}
C {devices/ipin.sym} 100 1130 0 0 {name=p_divw lab=divw}
C {devices/lab_pin.sym} 180 1130 0 1 {name=l_divw_110 sig_type=std_logic lab=divw}
C {devices/ipin.sym} 100 1190 0 0 {name=p_cclk lab=cclk}
C {devices/lab_pin.sym} 180 1190 0 1 {name=l_cclk_112 sig_type=std_logic lab=cclk}
C {devices/ipin.sym} 100 1250 0 0 {name=p_fll_en lab=fll_en}
C {devices/lab_pin.sym} 180 1250 0 1 {name=l_fll_en_114 sig_type=std_logic lab=fll_en}
C {devices/opin.sym} 2900 950 0 1 {name=p_lock lab=lock}
C {devices/lab_pin.sym} 2680 950 0 0 {name=l_lock_116 sig_type=std_logic lab=lock}
C {devices/opin.sym} 2900 1010 0 1 {name=p_act lab=act}
C {devices/lab_pin.sym} 2680 1010 0 0 {name=l_act_118 sig_type=std_logic lab=act}
C {devices/opin.sym} 2900 1070 0 1 {name=p_lock_det lab=lock_det}
C {devices/lab_pin.sym} 2680 1070 0 0 {name=l_lock_det_120 sig_type=std_logic lab=lock_det}
C {devices/opin.sym} 2900 1130 0 1 {name=p_fll_dir lab=fll_dir}
C {devices/lab_pin.sym} 2680 1130 0 0 {name=l_fll_dir_122 sig_type=std_logic lab=fll_dir}
C {devices/iopin.sym} 100 1350 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 180 1350 0 1 {name=l_VDDD_124 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 100 1410 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 180 1410 0 1 {name=l_VSSD_126 sig_type=std_logic lab=VSSD}
