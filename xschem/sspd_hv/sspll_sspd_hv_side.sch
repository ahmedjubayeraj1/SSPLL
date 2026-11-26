v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_sspd_hv_side: isolation buffer (XB1, XB2) -> R_s -> node f -> sampler xs1/C1 (tracks while cks = 1) and dummy sampler xsd/CD (opposite phase, keeps the buffer load constant); hold xs2/C2 (ckh)} 40 -560 0 0 0.3 0.3 {}
T {R_s = res_xhigh_po_0p35, L = 0.6 um; C1 = C2 = 2.69 x 2.69 um, CD = 4.4 x 4.4 um (= C1 + the Gm input); MIM top plate on the signal, bottom plate on VSSA} 40 -510 0 0 0.25 0.25 {}
N 280 -50 280 50 {lab=}
N 240 -80 200 -80 {lab=}
N 200 -80 200 80 {lab=}
N 200 80 240 80 {lab=}
N 280 -110 280 -140 {lab=}
N 280 110 280 140 {lab=}
N 540 -50 540 50 {lab=}
N 500 -80 460 -80 {lab=}
N 460 -80 460 80 {lab=}
N 460 80 500 80 {lab=}
N 540 -110 540 -140 {lab=}
N 540 110 540 140 {lab=}
N 60 0 200 0 {lab=}
N 280 0 460 0 {lab=}
N 540 0 670 0 {lab=}
N 700 20 700 -90 {lab=}
N 730 0 800 0 {lab=}
N 800 0 800 -40 {lab=}
N 800 -40 900 -40 {lab=}
N 800 -40 800 380 {lab=}
N 800 380 900 380 {lab=}
N 900 0 870 0 {lab=}
N 900 40 870 40 {lab=}
N 960 -90 960 -110 {lab=}
N 960 90 960 110 {lab=}
N 900 420 870 420 {lab=}
N 900 460 870 460 {lab=}
N 960 330 960 310 {lab=}
N 960 510 960 530 {lab=}
N 1460 0 1430 0 {lab=}
N 1460 40 1430 40 {lab=}
N 1520 -90 1520 -110 {lab=}
N 1520 90 1520 110 {lab=}
N 1100 0 1220 0 {lab=}
N 1220 0 1220 100 {lab=}
N 1220 0 1220 -160 {lab=}
N 1220 -160 1400 -160 {lab=}
N 1400 -160 1400 -40 {lab=}
N 1400 -40 1460 -40 {lab=}
N 1220 160 1220 180 {lab=}
N 1220 -160 1220 -260 {lab=}
N 1220 -260 2200 -260 {lab=}
N 1100 420 1220 420 {lab=}
N 1220 420 1220 520 {lab=}
N 1220 580 1220 600 {lab=}
N 1660 0 1780 0 {lab=}
N 1780 0 1780 100 {lab=}
N 1780 160 1780 180 {lab=}
N 1780 0 2200 0 {lab=}
N 60 700 160 700 {lab=}
N 60 760 160 760 {lab=}
N 60 820 160 820 {lab=}
N 60 880 160 880 {lab=}
N 60 -400 140 -400 {lab=}
N 60 960 140 960 {lab=}
C {devices/ipin.sym} 60 0 0 0 {name=p_clk lab=clk}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 260 -80 0 0 {name=XB1P L=0.5 W=1.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 260 80 0 0 {name=XB1N L=0.5 W=0.6 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 280 -140 0 0 {name=l_VDDA_3 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 280 140 0 0 {name=l_VSSA_4 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 520 -80 0 0 {name=XB2P L=0.5 W=5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 520 80 0 0 {name=XB2N L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/lab_pin.sym} 540 -140 0 0 {name=l_VDDA_7 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 540 140 0 0 {name=l_VSSA_8 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 700 0 3 0 {name=XRS L=0.6 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 700 -90 0 0 {name=l_VSSA_10 sig_type=std_logic lab=VSSA}
C {sspll_sspd_hv_tg.sym} 1000 0 0 0 {name=xs1}
C {sspll_sspd_hv_tg.sym} 1000 420 0 0 {name=xsd}
C {sspll_sspd_hv_tgh.sym} 1560 0 0 0 {name=xs2}
C {devices/lab_pin.sym} 870 0 0 0 {name=l_cks_14 sig_type=std_logic lab=cks}
C {devices/lab_pin.sym} 870 40 0 0 {name=l_cksb_15 sig_type=std_logic lab=cksb}
C {devices/lab_pin.sym} 960 -110 0 0 {name=l_VDDA_16 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 960 110 0 0 {name=l_VSSA_17 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 870 420 0 0 {name=l_cksb_18 sig_type=std_logic lab=cksb}
C {devices/lab_pin.sym} 870 460 0 0 {name=l_cks_19 sig_type=std_logic lab=cks}
C {devices/lab_pin.sym} 960 310 0 0 {name=l_VDDA_20 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 960 530 0 0 {name=l_VSSA_21 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1430 0 0 0 {name=l_ckh_22 sig_type=std_logic lab=ckh}
C {devices/lab_pin.sym} 1430 40 0 0 {name=l_ckhb_23 sig_type=std_logic lab=ckhb}
C {devices/lab_pin.sym} 1520 -110 0 0 {name=l_VDDA_24 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 1520 110 0 0 {name=l_VSSA_25 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/cap_mim_m3_1.sym} 1220 130 0 0 {name=XC1 W=2.69 L=2.69 MF=1 model=cap_mim_m3_1 spiceprefix=X}
C {devices/lab_pin.sym} 1220 180 0 0 {name=l_VSSA_27 sig_type=std_logic lab=VSSA}
C {devices/opin.sym} 2200 -260 0 1 {name=p_v1 lab=v1}
C {sky130_fd_pr/cap_mim_m3_1.sym} 1220 550 0 0 {name=XCD W=4.4 L=4.4 MF=1 model=cap_mim_m3_1 spiceprefix=X}
C {devices/lab_pin.sym} 1220 600 0 0 {name=l_VSSA_30 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/cap_mim_m3_1.sym} 1780 130 0 0 {name=XC2 W=3.85 L=3.85 MF=1 model=cap_mim_m3_1 spiceprefix=X}
C {devices/lab_pin.sym} 1780 180 0 0 {name=l_VSSA_32 sig_type=std_logic lab=VSSA}
C {devices/opin.sym} 2200 0 0 1 {name=p_v2 lab=v2}
C {devices/ipin.sym} 60 700 0 0 {name=p_cks lab=cks}
C {devices/lab_pin.sym} 160 700 0 1 {name=l_cks_35 sig_type=std_logic lab=cks}
C {devices/ipin.sym} 60 760 0 0 {name=p_cksb lab=cksb}
C {devices/lab_pin.sym} 160 760 0 1 {name=l_cksb_37 sig_type=std_logic lab=cksb}
C {devices/ipin.sym} 60 820 0 0 {name=p_ckh lab=ckh}
C {devices/lab_pin.sym} 160 820 0 1 {name=l_ckh_39 sig_type=std_logic lab=ckh}
C {devices/ipin.sym} 60 880 0 0 {name=p_ckhb lab=ckhb}
C {devices/lab_pin.sym} 160 880 0 1 {name=l_ckhb_41 sig_type=std_logic lab=ckhb}
C {devices/iopin.sym} 60 -400 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -400 0 1 {name=l_VDDA_43 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 960 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 960 0 1 {name=l_VSSA_45 sig_type=std_logic lab=VSSA}
