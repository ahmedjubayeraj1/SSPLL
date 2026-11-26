v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_lf_hv_c1tile: 9 MOS capacitors nfet_g5v0d10v5 W = L = 10 um in a 3 x 3 array} 40 -370 0 0 0.3 0.3 {}
T {(gate = top; drain, source, body = VSSA) and one cap_mim_m3_1 30 x 30 um above them (capm = top, met3 = VSSA)} 40 -330 0 0 0.3 0.3 {}
N 200 0 300 0 {lab=}
N 300 0 380 0 {lab=}
N 300 0 300 -200 {lab=}
N 300 -200 800 -200 {lab=}
N 800 -200 800 -30 {lab=}
N 420 -30 420 -90 {lab=}
N 420 30 420 90 {lab=}
N 800 30 800 90 {lab=}
N 60 250 140 250 {lab=}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 400 0 0 0 {name=XC L=10.0 W=10 nf=1 mult=9 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/cap_mim_m3_1.sym} 800 0 0 0 {name=XM W=30.0 L=30.0 MF=1 model=cap_mim_m3_1 spiceprefix=X}
C {devices/iopin.sym} 200 0 0 0 {name=p_top lab=top}
C {devices/lab_pin.sym} 420 -90 0 0 {name=l_VSSA_3 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 420 90 0 0 {name=l_VSSA_4 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 800 90 0 0 {name=l_VSSA_5 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 60 250 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 250 0 1 {name=l_VSSA_7 sig_type=std_logic lab=VSSA}
