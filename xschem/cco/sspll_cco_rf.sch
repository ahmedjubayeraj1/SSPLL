v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_cco_rf: 20 x res_xhigh_po_0p35 (L = 87.48 um) in series = 10 Mohm (gate filter of the output mirror)} 40 -330 0 0 0.3 0.3 {}
T {bodies of all segments to VSS (drawn as labels at each body pin)} 40 -290 0 0 0.25 0.25 {}
N 60 -160 180 -160 {lab=}
N 180 -160 180 -90 {lab=}
N 160 -60 140 -60 {lab=}
N 180 -30 180 -10 {lab=}
N 180 -10 440 -10 {lab=}
N 440 -10 440 -30 {lab=}
N 460 -60 480 -60 {lab=}
N 440 -90 440 -110 {lab=}
N 440 -110 700 -110 {lab=}
N 700 -110 700 -90 {lab=}
N 680 -60 660 -60 {lab=}
N 700 -30 700 -10 {lab=}
N 700 -10 960 -10 {lab=}
N 960 -10 960 -30 {lab=}
N 980 -60 1000 -60 {lab=}
N 960 -90 960 -110 {lab=}
N 960 -110 1220 -110 {lab=}
N 1220 -110 1220 -90 {lab=}
N 1200 -60 1180 -60 {lab=}
N 1220 -30 1220 -10 {lab=}
N 1220 -10 1480 -10 {lab=}
N 1480 -10 1480 -30 {lab=}
N 1500 -60 1520 -60 {lab=}
N 1480 -90 1480 -110 {lab=}
N 1480 -110 1740 -110 {lab=}
N 1740 -110 1740 -90 {lab=}
N 1720 -60 1700 -60 {lab=}
N 1740 -30 1740 -10 {lab=}
N 1740 -10 2000 -10 {lab=}
N 2000 -10 2000 -30 {lab=}
N 2020 -60 2040 -60 {lab=}
N 2000 -90 2000 -110 {lab=}
N 2000 -110 2260 -110 {lab=}
N 2260 -110 2260 -90 {lab=}
N 2240 -60 2220 -60 {lab=}
N 2260 -30 2260 -10 {lab=}
N 2260 -10 2520 -10 {lab=}
N 2520 -10 2520 -30 {lab=}
N 2540 -60 2560 -60 {lab=}
N 2520 -90 2520 -120 {lab=}
N 2520 -120 2670 -120 {lab=}
N 2670 -120 2670 140 {lab=}
N 2670 140 2520 140 {lab=}
N 2520 140 2520 170 {lab=}
N 2500 200 2480 200 {lab=}
N 2520 230 2520 250 {lab=}
N 2520 250 2260 250 {lab=}
N 2260 250 2260 230 {lab=}
N 2280 200 2300 200 {lab=}
N 2260 170 2260 150 {lab=}
N 2260 150 2000 150 {lab=}
N 2000 150 2000 170 {lab=}
N 1980 200 1960 200 {lab=}
N 2000 230 2000 250 {lab=}
N 2000 250 1740 250 {lab=}
N 1740 250 1740 230 {lab=}
N 1760 200 1780 200 {lab=}
N 1740 170 1740 150 {lab=}
N 1740 150 1480 150 {lab=}
N 1480 150 1480 170 {lab=}
N 1460 200 1440 200 {lab=}
N 1480 230 1480 250 {lab=}
N 1480 250 1220 250 {lab=}
N 1220 250 1220 230 {lab=}
N 1240 200 1260 200 {lab=}
N 1220 170 1220 150 {lab=}
N 1220 150 960 150 {lab=}
N 960 150 960 170 {lab=}
N 940 200 920 200 {lab=}
N 960 230 960 250 {lab=}
N 960 250 700 250 {lab=}
N 700 250 700 230 {lab=}
N 720 200 740 200 {lab=}
N 700 170 700 150 {lab=}
N 700 150 440 150 {lab=}
N 440 150 440 170 {lab=}
N 420 200 400 200 {lab=}
N 440 230 440 250 {lab=}
N 440 250 180 250 {lab=}
N 180 250 180 230 {lab=}
N 200 200 220 200 {lab=}
N 180 170 180 140 {lab=}
N 180 140 60 140 {lab=}
N 60 380 120 380 {lab=}
C {devices/iopin.sym} 60 -160 0 0 {name=p_a lab=a}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 180 -60 0 0 {name=XR0 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 140 -60 0 0 {name=l_VSS_2 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 440 -60 2 0 {name=XR1 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 480 -60 0 1 {name=l_VSS_4 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 700 -60 0 0 {name=XR2 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 660 -60 0 0 {name=l_VSS_6 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 960 -60 2 0 {name=XR3 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 1000 -60 0 1 {name=l_VSS_8 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 1220 -60 0 0 {name=XR4 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 1180 -60 0 0 {name=l_VSS_10 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 1480 -60 2 0 {name=XR5 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 1520 -60 0 1 {name=l_VSS_12 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 1740 -60 0 0 {name=XR6 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 1700 -60 0 0 {name=l_VSS_14 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 2000 -60 2 0 {name=XR7 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 2040 -60 0 1 {name=l_VSS_16 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 2260 -60 0 0 {name=XR8 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 2220 -60 0 0 {name=l_VSS_18 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 2520 -60 2 0 {name=XR9 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 2560 -60 0 1 {name=l_VSS_20 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 2520 200 0 0 {name=XR10 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 2480 200 0 0 {name=l_VSS_22 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 2260 200 2 0 {name=XR11 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 2300 200 0 1 {name=l_VSS_24 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 2000 200 0 0 {name=XR12 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 1960 200 0 0 {name=l_VSS_26 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 1740 200 2 0 {name=XR13 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 1780 200 0 1 {name=l_VSS_28 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 1480 200 0 0 {name=XR14 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 1440 200 0 0 {name=l_VSS_30 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 1220 200 2 0 {name=XR15 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 1260 200 0 1 {name=l_VSS_32 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 960 200 0 0 {name=XR16 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 920 200 0 0 {name=l_VSS_34 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 700 200 2 0 {name=XR17 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 740 200 0 1 {name=l_VSS_36 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 440 200 0 0 {name=XR18 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 400 200 0 0 {name=l_VSS_38 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 180 200 2 0 {name=XR19 L=87.48 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/lab_pin.sym} 220 200 0 1 {name=l_VSS_40 sig_type=std_logic lab=VSS}
C {devices/iopin.sym} 60 140 0 0 {name=p_b lab=b}
C {devices/iopin.sym} 60 380 0 0 {name=p_VSS lab=VSS}
C {devices/lab_pin.sym} 120 380 0 1 {name=l_VSS_43 sig_type=std_logic lab=VSS}
