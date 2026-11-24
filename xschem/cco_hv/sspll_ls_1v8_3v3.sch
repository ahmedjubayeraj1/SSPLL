v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_ls_1v8_3v3: 1.8 V -> 3.3 V level shifter (out = in, outb = not in)} 40 -460 0 0 0.35 0.35 {}
T {input inverter on VDDD / VSSD (thin oxide) | cross-coupled thick-oxide latch and output inverters on VDDA / VSSA} 40 -415 0 0 0.25 0.25 {}
N 60 -300 300 -300 {lab=}
N 460 -300 1720 -300 {lab=}
N 60 320 300 320 {lab=}
N 460 320 900 320 {lab=}
N 900 320 1720 320 {lab=}
N 220 -170 220 -300 {lab=}
N 220 70 220 320 {lab=}
N 220 -110 220 -50 {lab=}
N 220 -50 220 10 {lab=}
N 180 -140 150 -140 {lab=}
N 150 -140 150 -50 {lab=}
N 150 -50 150 40 {lab=}
N 150 40 180 40 {lab=}
N 40 -50 150 -50 {lab=}
N 580 -170 580 -300 {lab=}
N 980 -170 980 -300 {lab=}
N 580 70 580 320 {lab=}
N 980 70 980 320 {lab=}
N 580 -110 580 10 {lab=}
N 980 -110 980 10 {lab=}
N 580 -80 1060 -80 {lab=}
N 1060 -80 1490 -80 {lab=}
N 1060 -80 1060 -140 {lab=}
N 1060 -140 1020 -140 {lab=}
N 980 -40 500 -40 {lab=}
N 500 -40 500 -140 {lab=}
N 500 -140 540 -140 {lab=}
N 980 -20 1190 -20 {lab=}
N 40 -50 40 240 {lab=}
N 40 240 520 240 {lab=}
N 520 240 520 40 {lab=}
N 520 40 540 40 {lab=}
N 220 -50 340 -50 {lab=}
N 340 -50 340 200 {lab=}
N 340 200 1080 200 {lab=}
N 1080 200 1080 40 {lab=}
N 1080 40 1020 40 {lab=}
N 1270 -170 1270 -300 {lab=}
N 1270 70 1270 320 {lab=}
N 1270 -110 1270 -50 {lab=}
N 1270 -50 1270 10 {lab=}
N 1230 -140 1190 -140 {lab=}
N 1190 -140 1190 -20 {lab=}
N 1190 -20 1190 40 {lab=}
N 1190 40 1230 40 {lab=}
N 1270 -50 1400 -50 {lab=}
N 1570 -170 1570 -300 {lab=}
N 1570 70 1570 320 {lab=}
N 1570 -110 1570 -50 {lab=}
N 1570 -50 1570 10 {lab=}
N 1530 -140 1490 -140 {lab=}
N 1490 -140 1490 -80 {lab=}
N 1490 -80 1490 40 {lab=}
N 1490 40 1530 40 {lab=}
N 1570 -50 1700 -50 {lab=}
C {devices/iopin.sym} 60 -300 0 0 {name=p_VDDD lab=VDDD}
C {devices/iopin.sym} 1720 -300 0 1 {name=p_VDDA lab=VDDA}
C {devices/iopin.sym} 60 320 0 0 {name=p_VSSD lab=VSSD}
C {devices/iopin.sym} 1720 320 0 1 {name=p_VSSA lab=VSSA}
C {sky130_fd_pr/pfet3_01v8.sym} 200 -140 0 0 {name=XPI L=0.15 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X body=VDDD}
C {sky130_fd_pr/nfet3_01v8.sym} 200 40 0 0 {name=XNI L=0.15 W=0.5 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X body=VSSD}
C {devices/ipin.sym} 40 -50 0 0 {name=p_in lab=in}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 560 -140 0 0 {name=XP1 L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1000 -140 0 1 {name=XP2 L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 560 40 0 0 {name=XN1 L=0.5 W=3 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1000 40 0 1 {name=XN2 L=0.5 W=3 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1250 -140 0 0 {name=XPB L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1250 40 0 0 {name=XNB L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/opin.sym} 1400 -50 0 1 {name=p_outb lab=outb}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 1550 -140 0 0 {name=XPO L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 1550 40 0 0 {name=XNO L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSSA}
C {devices/opin.sym} 1700 -50 0 1 {name=p_out lab=out}
