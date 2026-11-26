v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_d2s_hv_rdeg: R_DEG = 2 x res_xhigh_po_0p69 (W 0.69 um, L 6.76 um, about 20 kOhm each) in series; XRD0 / XRD1: dummies} 40 -370 0 0 0.3 0.3 {}
N 200 -150 700 -150 {lab=}
N 700 -150 700 -30 {lab=}
N 700 30 700 90 {lab=}
N 700 90 1000 90 {lab=}
N 1000 90 1000 30 {lab=}
N 1000 -30 1000 -150 {lab=}
N 1000 -150 1600 -150 {lab=}
N 400 -30 400 -70 {lab=}
N 400 30 400 70 {lab=}
N 380 0 320 0 {lab=}
N 1300 -30 1300 -70 {lab=}
N 1300 30 1300 70 {lab=}
N 1280 0 1220 0 {lab=}
N 680 0 620 0 {lab=}
N 980 0 920 0 {lab=}
N 60 260 140 260 {lab=}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 400 0 0 0 {name=XRD0 L=6.76 mult=1 model=res_xhigh_po_0p69 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 700 0 0 0 {name=XR0 L=6.76 mult=1 model=res_xhigh_po_0p69 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 1000 0 0 0 {name=XR1 L=6.76 mult=1 model=res_xhigh_po_0p69 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 1300 0 0 0 {name=XRD1 L=6.76 mult=1 model=res_xhigh_po_0p69 spiceprefix=X}
C {devices/iopin.sym} 200 -150 0 0 {name=p_a lab=a}
C {devices/iopin.sym} 1600 -150 0 1 {name=p_b lab=b}
C {devices/lab_pin.sym} 400 -70 0 0 {name=l_VSSA_6 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 400 70 0 0 {name=l_VSSA_7 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 320 0 0 0 {name=l_VSSA_8 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1300 -70 0 0 {name=l_VSSA_9 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1300 70 0 0 {name=l_VSSA_10 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1220 0 0 0 {name=l_VSSA_11 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 620 0 0 0 {name=l_VSSA_12 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 920 0 0 0 {name=l_VSSA_13 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 60 260 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 260 0 1 {name=l_VSSA_15 sig_type=std_logic lab=VSSA}
