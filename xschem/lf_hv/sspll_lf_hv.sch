v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_lf_hv: main-loop filter. C2 on vctl takes each Gm packet first; R1 carries it into the C1 tiles on vz.} 40 -420 0 0 0.3 0.3 {}
T {zero 1/(2 pi R1 C1), pole (C1 + C2)/(2 pi R1 C1 C2). Ground VSSA.} 40 -380 0 0 0.3 0.3 {}
N 200 0 400 0 {lab=}
N 400 0 700 0 {lab=}
N 400 0 400 170 {lab=}
N 400 230 400 290 {lab=}
N 760 50 760 90 {lab=}
N 900 0 1260 0 {lab=}
N 1260 0 1260 150 {lab=}
N 1260 0 1410 0 {lab=}
N 1410 0 1560 0 {lab=}
N 1560 0 1560 150 {lab=}
N 1260 250 1260 290 {lab=}
N 1560 250 1560 290 {lab=}
N 60 500 140 500 {lab=}
C {sspll_lf_hv_r1.sym} 800 0 0 0 {name=xr1}
C {devices/iopin.sym} 200 0 0 0 {name=p_vctl lab=vctl}
C {sky130_fd_pr/cap_mim_m3_1.sym} 400 200 0 0 {name=XC2 W=30.0 L=7.74 MF=2 model=cap_mim_m3_1 spiceprefix=X}
C {devices/lab_pin.sym} 400 290 0 0 {name=l_VSSA_3 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 760 90 0 0 {name=l_VSSA_4 sig_type=std_logic lab=VSSA}
C {sspll_lf_hv_c1tile.sym} 1300 200 0 0 {name=xc1_0}
C {sspll_lf_hv_c1tile.sym} 1600 200 0 0 {name=xc1_1}
C {devices/lab_pin.sym} 1410 0 0 0 {name=l_vz_7 sig_type=std_logic lab=vz}
C {devices/lab_pin.sym} 1260 290 0 0 {name=l_VSSA_8 sig_type=std_logic lab=VSSA}
C {devices/lab_pin.sym} 1560 290 0 0 {name=l_VSSA_9 sig_type=std_logic lab=VSSA}
C {devices/iopin.sym} 60 500 0 0 {name=p_VSSA lab=VSSA}
C {devices/lab_pin.sym} 140 500 0 1 {name=l_VSSA_11 sig_type=std_logic lab=VSSA}
