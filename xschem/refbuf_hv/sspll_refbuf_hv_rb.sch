v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_refbuf_hv_rb: 10 x res_xhigh_po_0p35 (L = 87.48 um) in series = 5 Mohm (self-bias feedback of S1)} 40 -330 0 0 0.3 0.3 {}
T {bodies of all segments to VSS (labels at each body pin)} 40 -290 0 0 0.25 0.25 {}
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
N 2520 -90 2520 -130 {lab=}
N 2520 -130 40 -130 {lab=}
N 40 100 120 100 {lab=}
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
C {devices/iopin.sym} 40 -130 0 0 {name=p_b lab=b}
C {devices/iopin.sym} 40 100 0 0 {name=p_VSS lab=VSS}
C {devices/lab_pin.sym} 120 100 0 1 {name=l_VSS_23 sig_type=std_logic lab=VSS}
