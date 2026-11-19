v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_refbuf_hv: REF_IN receiver. Pad held at VDDA/2 (XRPU/XRPD), AC coupling C_AC (XCAC), self-biased gain stage S1 (R_B = xrb), S2 on VDDA, 5 V inverter on VDDD (3.3 -> 1.8 V level shift), output NOR on VDDD} 40 -600 0 0 0.3 0.3 {}
T {refclk rises with REF_IN; pll_en = 0 turns S1 off and holds refclk low. Control nets en / enb / enl are connected by name} 40 -560 0 0 0.25 0.25 {}
N 60 -360 1250 -360 {lab=}
N 60 420 2500 420 {lab=}
N 200 -150 200 -360 {lab=}
N 200 -90 200 0 {lab=}
N 280 90 280 0 {lab=}
N 280 150 280 420 {lab=}
N 180 -120 160 -120 {lab=}
N 260 120 240 120 {lab=}
N 60 0 200 0 {lab=}
N 200 0 350 0 {lab=}
N 410 0 500 0 {lab=}
N 500 0 500 80 {lab=}
N 500 80 660 80 {lab=}
N 500 0 500 -180 {lab=}
N 500 -180 780 -180 {lab=}
N 840 -130 840 -110 {lab=}
N 720 30 720 -360 {lab=}
N 720 250 720 420 {lab=}
N 660 160 600 160 {lab=}
N 660 200 600 200 {lab=}
N 60 300 620 300 {lab=}
N 620 300 620 120 {lab=}
N 620 120 660 120 {lab=}
N 1120 -90 1120 -360 {lab=}
N 1120 150 1120 420 {lab=}
N 1120 -30 1120 30 {lab=}
N 1120 30 1120 90 {lab=}
N 860 140 1020 140 {lab=}
N 980 -180 1020 -180 {lab=}
N 1020 -180 1020 140 {lab=}
N 1020 30 1050 30 {lab=}
N 1080 -60 1050 -60 {lab=}
N 1050 -60 1050 30 {lab=}
N 1050 30 1050 120 {lab=}
N 1050 120 1080 120 {lab=}
N 1120 30 1350 30 {lab=}
N 1380 -60 1350 -60 {lab=}
N 1350 -60 1350 30 {lab=}
N 1350 30 1350 120 {lab=}
N 1350 120 1380 120 {lab=}
N 1420 150 1420 420 {lab=}
N 1420 -30 1420 30 {lab=}
N 1420 30 1420 90 {lab=}
N 1420 -90 1420 -300 {lab=}
N 1420 -300 2500 -300 {lab=}
N 1820 -210 1820 -300 {lab=}
N 1820 -150 1820 -90 {lab=}
N 1820 -30 1820 30 {lab=}
N 1820 30 2040 30 {lab=}
N 2040 30 2040 90 {lab=}
N 1820 30 1820 90 {lab=}
N 1820 150 1820 420 {lab=}
N 2040 150 2040 420 {lab=}
N 1420 30 1700 30 {lab=}
N 1780 -180 1700 -180 {lab=}
N 1700 -180 1700 30 {lab=}
N 1700 30 1700 120 {lab=}
N 1700 120 1780 120 {lab=}
N 1780 -60 1750 -60 {lab=}
N 2000 120 1970 120 {lab=}
N 2040 30 2500 30 {lab=}
N 60 640 200 640 {lab=}
N 200 640 320 640 {lab=}
N 520 620 560 620 {lab=}
N 520 660 560 660 {lab=}
N 380 570 380 550 {lab=}
N 420 570 420 550 {lab=}
N 380 710 380 730 {lab=}
N 200 640 200 820 {lab=}
N 200 820 900 820 {lab=}
N 900 820 900 740 {lab=}
N 980 560 900 560 {lab=}
N 900 560 900 740 {lab=}
N 900 740 980 740 {lab=}
N 1020 530 1020 500 {lab=}
N 1020 770 1020 800 {lab=}
N 1020 590 1020 650 {lab=}
N 1020 650 1020 710 {lab=}
N 1020 650 1120 650 {lab=}
C {devices/iopin.sym} 60 -360 0 0 {name=p_VDDA lab=VDDA}
C {devices/iopin.sym} 60 420 0 0 {name=p_VSS lab=VSS}
C {devices/iopin.sym} 60 0 0 0 {name=p_REF_IN lab=REF_IN}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 200 -120 0 0 {name=XRPU L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 280 120 0 0 {name=XRPD L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 160 -120 0 0 {name=l_VSS_5 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 240 120 0 0 {name=l_VSS_6 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/cap_mim_m3_1.sym} 380 0 1 0 {name=XCAC W=30.0 L=30.0 MF=2 model=cap_mim_m3_1 spiceprefix=X}
C {sspll_refbuf_hv_s1.sym} 760 140 0 0 {name=xs1}
C {sspll_refbuf_hv_rb.sym} 880 -180 0 0 {name=xrb}
C {devices/lab_pin.sym} 840 -110 0 0 {name=l_VSS_10 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 600 160 0 0 {name=l_en_11 sig_type=std_logic lab=en}
C {devices/lab_pin.sym} 600 200 0 0 {name=l_enb_12 sig_type=std_logic lab=enb}
C {devices/iopin.sym} 60 300 0 0 {name=p_ib lab=ib}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1100 -60 0 0 {name=XP2 L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1100 120 0 0 {name=XN2 L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1400 -60 0 0 {name=XPL L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1400 120 0 0 {name=XNL L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/iopin.sym} 2500 -300 0 1 {name=p_VDDD lab=VDDD}
C {sky130_fd_pr/pfet3_01v8.sym} 1800 -180 0 0 {name=XPB L=0.15 W=4 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/pfet3_01v8.sym} 1800 -60 0 0 {name=XPB2 L=0.15 W=4 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 1800 120 0 0 {name=XNB L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_01v8.sym} 2020 120 0 0 {name=XNB2 L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 1750 -60 0 0 {name=l_enl_23 sig_type=std_logic lab=enl}
C {devices/lab_pin.sym} 1970 120 0 0 {name=l_enl_24 sig_type=std_logic lab=enl}
C {devices/opin.sym} 2500 30 0 1 {name=p_refclk lab=refclk}
C {devices/ipin.sym} 60 640 0 0 {name=p_pll_en lab=pll_en}
C {../cco_hv/sspll_ls_1v8_3v3.sym} 420 640 0 0 {name=xls}
C {devices/lab_pin.sym} 560 620 0 1 {name=l_en_28 sig_type=std_logic lab=en}
C {devices/lab_pin.sym} 560 660 0 1 {name=l_enb_29 sig_type=std_logic lab=enb}
C {devices/lab_pin.sym} 380 550 0 0 {name=l_VDDD_30 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 420 550 0 1 {name=l_VDDA_31 sig_type=std_logic lab=VDDA}
C {devices/lab_pin.sym} 380 730 0 0 {name=l_VSS_32 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 1000 560 0 0 {name=XPEI L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 1000 740 0 0 {name=XNEI L=0.15 W=0.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 1020 500 0 1 {name=l_VDDD_35 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1020 800 0 1 {name=l_VSS_36 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1120 650 0 1 {name=l_enl_37 sig_type=std_logic lab=enl}
