v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_cco_dac: unit current sinks (2.5 uA each at IBIAS = 5 uA) switched into vgr} 40 -420 0 0 0.35 0.35 {}
T {base: 13 units (switch = en) | binary: 1, 2, 4, 8, 16 units (switches = c0..c4) | 3.3 V devices} 40 -375 0 0 0.25 0.25 {}
N 60 260 1900 260 {lab=}
N 60 0 160 0 {lab=}
N 160 0 240 0 {lab=}
N 240 0 240 30 {lab=}
N 160 0 160 60 {lab=}
N 160 60 200 60 {lab=}
N 240 90 240 260 {lab=}
N 160 60 160 170 {lab=}
N 160 170 410 170 {lab=}
N 410 170 690 170 {lab=}
N 690 170 970 170 {lab=}
N 970 170 1250 170 {lab=}
N 1250 170 1530 170 {lab=}
N 1530 170 1810 170 {lab=}
N 480 -90 480 -200 {lab=}
N 480 -30 480 60 {lab=}
N 480 120 480 260 {lab=}
N 440 90 410 90 {lab=}
N 410 90 410 170 {lab=}
N 440 -60 410 -60 {lab=}
N 410 -60 410 -130 {lab=}
N 760 -90 760 -200 {lab=}
N 760 -30 760 60 {lab=}
N 760 120 760 260 {lab=}
N 720 90 690 90 {lab=}
N 690 90 690 170 {lab=}
N 720 -60 690 -60 {lab=}
N 690 -60 690 -130 {lab=}
N 1040 -90 1040 -200 {lab=}
N 1040 -30 1040 60 {lab=}
N 1040 120 1040 260 {lab=}
N 1000 90 970 90 {lab=}
N 970 90 970 170 {lab=}
N 1000 -60 970 -60 {lab=}
N 970 -60 970 -130 {lab=}
N 1320 -90 1320 -200 {lab=}
N 1320 -30 1320 60 {lab=}
N 1320 120 1320 260 {lab=}
N 1280 90 1250 90 {lab=}
N 1250 90 1250 170 {lab=}
N 1280 -60 1250 -60 {lab=}
N 1250 -60 1250 -130 {lab=}
N 1600 -90 1600 -200 {lab=}
N 1600 -30 1600 60 {lab=}
N 1600 120 1600 260 {lab=}
N 1560 90 1530 90 {lab=}
N 1530 90 1530 170 {lab=}
N 1560 -60 1530 -60 {lab=}
N 1530 -60 1530 -130 {lab=}
N 1880 -90 1880 -200 {lab=}
N 1880 -30 1880 60 {lab=}
N 1880 120 1880 260 {lab=}
N 1840 90 1810 90 {lab=}
N 1810 90 1810 170 {lab=}
N 1840 -60 1810 -60 {lab=}
N 1810 -60 1810 -130 {lab=}
N 480 -200 1880 -200 {lab=}
N 1880 -200 1900 -200 {lab=}
C {devices/iopin.sym} 60 0 0 0 {name=p_ibias lab=ibias}
C {devices/iopin.sym} 60 260 0 0 {name=p_VSS lab=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 220 60 0 0 {name=XNB L=4.0 W=1 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 460 -60 0 0 {name=XS0 L=0.5 W=1 nf=1 mult=13 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 460 90 0 0 {name=XU0 L=4.0 W=1 nf=1 mult=13 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/ipin.sym} 410 -130 0 0 {name=p_en lab=en}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 740 -60 0 0 {name=XS1 L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 740 90 0 0 {name=XU1 L=4.0 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/ipin.sym} 690 -130 0 0 {name=p_c0 lab=c0}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1020 -60 0 0 {name=XS2 L=0.5 W=1 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1020 90 0 0 {name=XU2 L=4.0 W=1 nf=1 mult=2 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/ipin.sym} 970 -130 0 0 {name=p_c1 lab=c1}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1300 -60 0 0 {name=XS3 L=0.5 W=1 nf=1 mult=4 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1300 90 0 0 {name=XU3 L=4.0 W=1 nf=1 mult=4 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/ipin.sym} 1250 -130 0 0 {name=p_c2 lab=c2}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1580 -60 0 0 {name=XS4 L=0.5 W=1 nf=1 mult=8 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1580 90 0 0 {name=XU4 L=4.0 W=1 nf=1 mult=8 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/ipin.sym} 1530 -130 0 0 {name=p_c3 lab=c3}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1860 -60 0 0 {name=XS5 L=0.5 W=1 nf=1 mult=16 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1860 90 0 0 {name=XU5 L=4.0 W=1 nf=1 mult=16 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {devices/ipin.sym} 1810 -130 0 0 {name=p_c4 lab=c4}
C {devices/iopin.sym} 1900 -200 0 1 {name=p_vgr lab=vgr}
