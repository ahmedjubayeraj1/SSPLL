v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_fll_ds: 3.3 -> 1.8 V down-shifter. A 5 V inverter on VDDD takes the 0..VDDA clock on its thick gates;} 40 -420 0 0 0.3 0.3 {}
T {two 1.8 V inverters restore the edges (out in phase with in).} 40 -380 0 0 0.3 0.3 {}
N 100 0 300 0 {lab=}
N 300 0 300 -100 {lab=}
N 300 -100 380 -100 {lab=}
N 300 0 300 100 {lab=}
N 300 100 380 100 {lab=}
N 420 -130 420 -170 {lab=}
N 420 130 420 170 {lab=}
N 420 -70 420 0 {lab=}
N 420 0 420 70 {lab=}
N 420 0 600 0 {lab=}
N 600 0 600 -100 {lab=}
N 600 -100 680 -100 {lab=}
N 600 0 600 100 {lab=}
N 600 100 680 100 {lab=}
N 720 -130 720 -170 {lab=}
N 720 130 720 170 {lab=}
N 720 -70 720 0 {lab=}
N 720 0 720 70 {lab=}
N 720 0 900 0 {lab=}
N 900 0 900 -100 {lab=}
N 900 -100 980 -100 {lab=}
N 900 0 900 100 {lab=}
N 900 100 980 100 {lab=}
N 1020 -130 1020 -170 {lab=}
N 1020 130 1020 170 {lab=}
N 1020 -70 1020 0 {lab=}
N 1020 0 1020 70 {lab=}
N 1020 0 1200 0 {lab=}
N 100 -300 180 -300 {lab=}
N 100 300 180 300 {lab=}
C {devices/ipin.sym} 100 0 0 0 {name=p_in lab=in}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 400 -100 0 0 {name=XDP L=0.5 W=6 nf=2 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 400 100 0 0 {name=XDN L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSD}
C {devices/lab_pin.sym} 420 -170 0 0 {name=l_VDDD_3 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 420 170 0 0 {name=l_VSSD_4 sig_type=std_logic lab=VSSD}
C {sky130_fd_pr/pfet3_01v8.sym} 700 -100 0 0 {name=XI1P L=0.15 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 700 100 0 0 {name=XI1N L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {devices/lab_pin.sym} 720 -170 0 0 {name=l_VDDD_7 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 720 170 0 0 {name=l_VSSD_8 sig_type=std_logic lab=VSSD}
C {sky130_fd_pr/pfet3_01v8.sym} 1000 -100 0 0 {name=XI2P L=0.15 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 1000 100 0 0 {name=XI2N L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {devices/lab_pin.sym} 1020 -170 0 0 {name=l_VDDD_11 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1020 170 0 0 {name=l_VSSD_12 sig_type=std_logic lab=VSSD}
C {devices/opin.sym} 1200 0 0 1 {name=p_out lab=out}
C {devices/iopin.sym} 100 -300 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 180 -300 0 1 {name=l_VDDD_15 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 100 300 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 180 300 0 1 {name=l_VSSD_17 sig_type=std_logic lab=VSSD}
