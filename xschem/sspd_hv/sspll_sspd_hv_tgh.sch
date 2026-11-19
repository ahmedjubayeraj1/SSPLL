v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_sspd_hv_tgh: 5 V transmission gate a-b, on while g = 1 / gb = 0 (gates swing 0 / 3.3 V). There is no low-Vt 5 V device: the nMOS sees V_GS = 3.3 - 1.65 V at mid-rail, so the pMOS carries about half the conductance} 40 -420 0 0 0.3 0.3 {}
N 320 -30 320 -120 {lab=}
N 320 -120 580 -120 {lab=}
N 580 -120 580 -30 {lab=}
N 320 30 320 120 {lab=}
N 320 120 580 120 {lab=}
N 580 120 580 30 {lab=}
N 60 -120 320 -120 {lab=}
N 580 120 860 120 {lab=}
N 60 0 280 0 {lab=}
N 620 0 860 0 {lab=}
N 60 -300 140 -300 {lab=}
N 60 300 140 300 {lab=}
C {sky130_fd_pr/nfet3_g5v0d10v5.sym} 300 0 0 0 {name=XN L=0.5 W=1 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=nfet_g5v0d10v5 spiceprefix=X body=VSS}
C {sky130_fd_pr/pfet3_g5v0d10v5.sym} 600 0 0 1 {name=XP L=0.5 W=2 nf=1 mult=1 ad="'int((nf+1)/2) * W/nf * 0.29'" pd="'2*int((nf+1)/2) * (W/nf + 0.29)'" as="'int((nf+2)/2) * W/nf * 0.29'" ps="'2*int((nf+2)/2) * (W/nf + 0.29)'" nrd="'0.29 / W'" nrs="'0.29 / W'" sa=0 sb=0 sd=0 model=pfet_g5v0d10v5 spiceprefix=X body=VDDA}
C {devices/iopin.sym} 60 -120 0 0 {name=p_a lab=a}
C {devices/iopin.sym} 860 120 0 1 {name=p_b lab=b}
C {devices/ipin.sym} 60 0 0 0 {name=p_g lab=g}
C {devices/ipin.sym} 860 0 0 1 {name=p_gb lab=gb}
C {devices/iopin.sym} 60 -300 0 0 {name=p_VDDA lab=VDDA}
C {devices/lab_pin.sym} 140 -300 0 1 {name=l_VDDA_7 sig_type=std_logic lab=VDDA}
C {devices/iopin.sym} 60 300 0 0 {name=p_VSS lab=VSS}
C {devices/lab_pin.sym} 140 300 0 1 {name=l_VSS_9 sig_type=std_logic lab=VSS}
