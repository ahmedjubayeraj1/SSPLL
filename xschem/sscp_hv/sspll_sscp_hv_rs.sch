v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_sscp_hv_rs: source-degeneration resistor, res_xhigh_po_0p35, L = 17.2 um (about 98 kOhm); body to VSS} 40 -300 0 0 0.3 0.3 {}
N 200 -120 400 -120 {lab=}
N 400 -120 400 -30 {lab=}
N 200 120 400 120 {lab=}
N 400 120 400 30 {lab=}
N 380 0 320 0 {lab=}
N 60 220 140 220 {lab=}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 400 0 0 0 {name=XR0 L=17.2 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {devices/iopin.sym} 200 -120 0 0 {name=p_a lab=a}
C {devices/iopin.sym} 200 120 0 0 {name=p_b lab=b}
C {devices/lab_pin.sym} 320 0 0 0 {name=l_VSSA_3 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 60 220 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 220 0 1 {name=l_VSSA_5 sig_type=std_logic lab=VSSA}
