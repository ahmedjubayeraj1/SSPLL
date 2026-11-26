v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_vco_hv_acbuf: AC-coupled self-biased buffer, 5 V devices on VDDA (one on every ring node)} 40 -420 0 0 0.35 0.35 {}
T {CC blocks the ring's DC level; RF biases inverter 1 at its trip point; inverter 2 restores full-swing edges} 40 -375 0 0 0.25 0.25 {}
N 60 -260 500 -260 {lab=}
N 500 -260 840 -260 {lab=}
N 60 440 400 440 {lab=}
N 400 440 840 440 {lab=}
N 60 -20 130 -20 {lab=}
N 190 -20 260 -20 {lab=}
N 260 -20 320 -20 {lab=}
N 400 -140 400 -260 {lab=}
N 400 100 400 440 {lab=}
N 400 -80 400 -20 {lab=}
N 400 -20 400 40 {lab=}
N 360 -110 320 -110 {lab=}
N 320 -110 320 -20 {lab=}
N 320 -20 320 70 {lab=}
N 320 70 360 70 {lab=}
N 260 -20 260 340 {lab=}
N 260 340 300 340 {lab=}
N 330 360 330 440 {lab=}
N 400 -20 520 -20 {lab=}
N 520 -20 560 -20 {lab=}
N 520 -20 520 340 {lab=}
N 520 340 360 340 {lab=}
N 640 -140 640 -260 {lab=}
N 640 100 640 440 {lab=}
N 640 -80 640 -20 {lab=}
N 640 -20 640 40 {lab=}
N 600 -110 560 -110 {lab=}
N 560 -110 560 -20 {lab=}
N 560 -20 560 70 {lab=}
N 560 70 600 70 {lab=}
N 640 -20 800 -20 {lab=}
C {devices/iopin.sym} 60 -260 0 0 {name=p_VDD lab=VDD}
C {devices/iopin.sym} 60 440 0 0 {name=p_VSSA lab=VSSA}
C {devices/ipin.sym} 60 -20 0 0 {name=p_in lab=in}
C {sky130_fd_pr/cap_mim_m3_1.sym} 160 -20 1 0 {name=XCC W=4.2 L=4.2 MF=1 model=cap_mim_m3_1 spiceprefix=X}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 380 -110 0 0 {name=XP1 L=0.5 W=1.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 380 70 0 0 {name=XN1 L=0.5 W=0.6 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 330 340 3 0 {name=XRF L=39.8 mult=1 model=res_xhigh_po_0p35 spiceprefix=X}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 620 -110 0 0 {name=XP2 L=0.5 W=3 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDD}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 620 70 0 0 {name=XN2 L=0.5 W=1.2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/opin.sym} 800 -20 0 1 {name=p_out lab=out}
