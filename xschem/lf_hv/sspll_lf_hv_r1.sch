v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_lf_hv_r1: R1 = 3 x res_xhigh_po_2p85 (W 2.85 um, L 9.44 um) in series,} 40 -370 0 0 0.3 0.3 {}
T {drawn as the layout meander (bottom-bottom, top-top); XRD0 / XRD1: dummy strips, all ends on VSSA} 40 -330 0 0 0.3 0.3 {}
N 200 -150 400 -150 {lab=}
N 400 -150 400 -30 {lab=}
N 400 30 400 90 {lab=}
N 400 90 700 90 {lab=}
N 700 90 700 30 {lab=}
N 700 -30 700 -90 {lab=}
N 700 -90 1000 -90 {lab=}
N 1000 -90 1000 -30 {lab=}
N 1000 30 1000 150 {lab=}
N 1000 150 1200 150 {lab=}
N 380 0 320 0 {lab=}
N 680 0 620 0 {lab=}
N 980 0 920 0 {lab=}
N 150 -30 150 -70 {lab=}
N 150 30 150 70 {lab=}
N 130 0 70 0 {lab=}
N 1350 -30 1350 -70 {lab=}
N 1350 30 1350 70 {lab=}
N 1330 0 1270 0 {lab=}
N 60 300 140 300 {lab=}
C {sky130_fd_pr/res_xhigh_po_2p85.sym} 400 0 0 0 {name=XR0 L=9.44 mult=1 model=res_xhigh_po_2p85 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_2p85.sym} 700 0 0 0 {name=XR1 L=9.44 mult=1 model=res_xhigh_po_2p85 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_2p85.sym} 1000 0 0 0 {name=XR2 L=9.44 mult=1 model=res_xhigh_po_2p85 spiceprefix=X}
C {devices/iopin.sym} 200 -150 0 0 {name=p_a lab=a}
C {devices/iopin.sym} 1200 150 0 1 {name=p_b lab=b}
C {devices/lab_pin.sym} 320 0 0 0 {name=l_VSSA_5 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 620 0 0 0 {name=l_VSSA_6 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 920 0 0 0 {name=l_VSSA_7 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/res_xhigh_po_2p85.sym} 150 0 0 0 {name=XRD0 L=9.44 mult=1 model=res_xhigh_po_2p85 spiceprefix=X}
C {devices/lab_pin.sym} 150 -70 0 0 {name=l_VSSA_9 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 150 70 0 0 {name=l_VSSA_10 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 70 0 0 0 {name=l_VSSA_11 sig_type=std_logic lab=VSSA}
C {sky130_fd_pr/res_xhigh_po_2p85.sym} 1350 0 0 0 {name=XRD1 L=9.44 mult=1 model=res_xhigh_po_2p85 spiceprefix=X}
C {devices/lab_pin.sym} 1350 -70 0 0 {name=l_VSSA_13 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1350 70 0 0 {name=l_VSSA_14 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1270 0 0 0 {name=l_VSSA_15 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 60 300 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 300 0 1 {name=l_VSSA_17 sig_type=std_logic lab=VSSA}
