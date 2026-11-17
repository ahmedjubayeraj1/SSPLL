v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_clkgen: refclk (step 76) -> sampling pair cks/cksb (sw1 samples at the refclk rising edge), hold pulse ckh/ckhb (sw2), Gm pulse ckg/ckgb (tau = 200 ps, t_p ~ 2.6 ns after the sampling edge)} 40 -460 0 0 0.3 0.3 {}
T {all devices 1.8 V core (VDD = VDDL, the regulated rail); supplies of the sub-cells connected by name} 40 -420 0 0 0.25 0.25 {}
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
N 540 0 640 0 {lab=}
N 640 0 1000 0 {lab=}
N 280 510 280 610 {lab=}
N 240 480 200 480 {lab=}
N 200 480 200 640 {lab=}
N 200 640 240 640 {lab=}
N 280 450 280 420 {lab=}
N 280 670 280 700 {lab=}
N 540 510 540 610 {lab=}
N 500 480 460 480 {lab=}
N 460 480 460 640 {lab=}
N 460 640 500 640 {lab=}
N 540 450 540 420 {lab=}
N 540 670 540 700 {lab=}
N 640 0 640 280 {lab=}
N 640 280 160 280 {lab=}
N 160 280 160 560 {lab=}
N 160 560 200 560 {lab=}
N 280 560 460 560 {lab=}
N 540 560 720 560 {lab=}
N 920 560 1020 560 {lab=}
N 1020 560 1140 560 {lab=}
N 280 1070 280 1170 {lab=}
N 240 1040 200 1040 {lab=}
N 200 1040 200 1200 {lab=}
N 200 1200 240 1200 {lab=}
N 280 1010 280 980 {lab=}
N 280 1230 280 1260 {lab=}
N 540 1070 540 1170 {lab=}
N 500 1040 460 1040 {lab=}
N 460 1040 460 1200 {lab=}
N 460 1200 500 1200 {lab=}
N 540 1010 540 980 {lab=}
N 540 1230 540 1260 {lab=}
N 800 1070 800 1170 {lab=}
N 760 1040 720 1040 {lab=}
N 720 1040 720 1200 {lab=}
N 720 1200 760 1200 {lab=}
N 800 1010 800 980 {lab=}
N 800 1230 800 1260 {lab=}
N 1020 560 1020 840 {lab=}
N 1020 840 160 840 {lab=}
N 160 840 160 1120 {lab=}
N 160 1120 200 1120 {lab=}
N 280 1120 460 1120 {lab=}
N 540 1120 720 1120 {lab=}
N 800 1120 980 1120 {lab=}
N 1180 1120 1400 1120 {lab=}
N 1200 -20 1900 -20 {lab=}
N 1200 20 1900 20 {lab=}
N 1340 540 1900 540 {lab=}
N 1340 580 1900 580 {lab=}
N 1600 1100 1900 1100 {lab=}
N 1600 1140 1900 1140 {lab=}
N 1060 -70 1060 -90 {lab=}
N 1060 70 1060 90 {lab=}
N 1200 490 1200 470 {lab=}
N 1200 630 1200 650 {lab=}
N 1460 1050 1460 1030 {lab=}
N 1460 1190 1460 1210 {lab=}
N 780 510 780 490 {lab=}
N 780 610 780 630 {lab=}
N 1040 1070 1040 1050 {lab=}
N 1040 1170 1040 1190 {lab=}
N 60 -320 140 -320 {lab=}
N 60 1400 140 1400 {lab=}
C {devices/ipin.sym} 60 0 0 0 {name=p_refclk lab=refclk}
C {sky130_fd_pr/pfet3_01v8.sym} 260 -80 0 0 {name=XI0P L=0.15 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 260 80 0 0 {name=XI0N L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 280 -140 0 0 {name=l_VDD_3 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 280 140 0 0 {name=l_VSS_4 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 520 -80 0 0 {name=XI1P L=0.15 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 520 80 0 0 {name=XI1N L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 540 -140 0 0 {name=l_VDD_7 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 540 140 0 0 {name=l_VSS_8 sig_type=std_logic lab=VSS}
C {sspll_ckg_drv.sym} 1100 0 0 0 {name=xds}
C {sky130_fd_pr/pfet3_01v8.sym} 260 480 0 0 {name=XI2P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 260 640 0 0 {name=XI2N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 280 420 0 0 {name=l_VDD_12 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 280 700 0 0 {name=l_VSS_13 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 520 480 0 0 {name=XI3P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 520 640 0 0 {name=XI3N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 540 420 0 0 {name=l_VDD_16 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 540 700 0 0 {name=l_VSS_17 sig_type=std_logic lab=VSS}
C {sspll_ckg_pulse_h.sym} 820 560 0 0 {name=xph}
C {sspll_ckg_drv.sym} 1240 560 0 0 {name=xdh}
C {sky130_fd_pr/pfet3_01v8.sym} 260 1040 0 0 {name=XI4P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 260 1200 0 0 {name=XI4N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 280 980 0 0 {name=l_VDD_22 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 280 1260 0 0 {name=l_VSS_23 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 520 1040 0 0 {name=XI5P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 520 1200 0 0 {name=XI5N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 540 980 0 0 {name=l_VDD_26 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 540 1260 0 0 {name=l_VSS_27 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 780 1040 0 0 {name=XI6P L=0.15 W=0.84 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_01v8.sym} 780 1200 0 0 {name=XI6N L=0.15 W=0.42 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSS}
C {devices/lab_pin.sym} 800 980 0 0 {name=l_VDD_30 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 800 1260 0 0 {name=l_VSS_31 sig_type=std_logic lab=VSS}
C {sspll_ckg_pulse_g.sym} 1080 1120 0 0 {name=xpg}
C {sspll_ckg_drv.sym} 1500 1120 0 0 {name=xdg}
C {devices/opin.sym} 1900 -20 0 1 {name=p_cksb lab=cksb}
C {devices/opin.sym} 1900 20 0 1 {name=p_cks lab=cks}
C {devices/opin.sym} 1900 540 0 1 {name=p_ckh lab=ckh}
C {devices/opin.sym} 1900 580 0 1 {name=p_ckhb lab=ckhb}
C {devices/opin.sym} 1900 1100 0 1 {name=p_ckg lab=ckg}
C {devices/opin.sym} 1900 1140 0 1 {name=p_ckgb lab=ckgb}
C {devices/lab_pin.sym} 1060 -90 0 0 {name=l_VDD_40 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 1060 90 0 0 {name=l_VSS_41 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1200 470 0 0 {name=l_VDD_42 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 1200 650 0 0 {name=l_VSS_43 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1460 1030 0 0 {name=l_VDD_44 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 1460 1210 0 0 {name=l_VSS_45 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 780 490 0 0 {name=l_VDD_46 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 780 630 0 0 {name=l_VSS_47 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 1040 1050 0 0 {name=l_VDD_48 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 1040 1190 0 0 {name=l_VSS_49 sig_type=std_logic lab=VSS}
C {devices/iopin.sym} 60 -320 0 0 {name=p_VDD lab=VDD}
C {devices/lab_pin.sym} 140 -320 0 1 {name=l_VDD_51 sig_type=std_logic lab=VDD}
C {devices/iopin.sym} 60 1400 0 0 {name=p_VSS lab=VSS}
C {devices/lab_pin.sym} 140 1400 0 1 {name=l_VSS_53 sig_type=std_logic lab=VSS}
