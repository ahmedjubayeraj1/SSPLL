v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_vco_hv_core: 3-stage pseudo-differential ring (cells x1..x3), fed by the CCO current on VDD} 40 -400 0 0 0.35 0.35 {}
T {the crossed feedback (bottom) closes the ring: x3.outp -> x1.inm (vom), x3.outm -> x1.inp (vop)} 40 -355 0 0 0.25 0.25 {}
N 200 -200 1200 -200 {lab=}
N 200 200 1200 200 {lab=}
N 200 240 1200 240 {lab=}
N 260 -70 260 -200 {lab=}
N 260 70 260 200 {lab=}
N 300 70 300 240 {lab=}
N 660 -70 660 -200 {lab=}
N 660 70 660 200 {lab=}
N 700 70 700 240 {lab=}
N 1060 -70 1060 -200 {lab=}
N 1060 70 1060 200 {lab=}
N 1100 70 1100 240 {lab=}
N 400 -20 500 -20 {lab=}
N 500 -20 600 -20 {lab=}
N 400 20 500 20 {lab=}
N 500 20 600 20 {lab=}
N 500 -20 500 -110 {lab=}
N 500 20 500 120 {lab=}
N 800 -20 900 -20 {lab=}
N 900 -20 1000 -20 {lab=}
N 800 20 900 20 {lab=}
N 900 20 1000 20 {lab=}
N 900 -20 900 -110 {lab=}
N 900 20 900 120 {lab=}
N 1200 -20 1300 -20 {lab=}
N 1300 -20 1300 300 {lab=}
N 1300 300 100 300 {lab=}
N 100 300 100 20 {lab=}
N 100 20 130 20 {lab=}
N 130 20 200 20 {lab=}
N 1200 20 1260 20 {lab=}
N 1260 20 1260 340 {lab=}
N 1260 340 60 340 {lab=}
N 60 340 60 -20 {lab=}
N 60 -20 130 -20 {lab=}
N 130 -20 200 -20 {lab=}
N 130 -20 130 -110 {lab=}
N 130 20 130 120 {lab=}
C {devices/iopin.sym} 200 -200 0 0 {name=p_VDD lab=VDD}
C {devices/ipin.sym} 200 200 0 0 {name=p_vtune lab=vtune}
C {devices/iopin.sym} 200 240 0 0 {name=p_VSSA lab=VSSA}
C {sspll_vco_hv_dcell.sym} 300 0 0 0 {name=x1}
C {sspll_vco_hv_dcell.sym} 700 0 0 0 {name=x2}
C {sspll_vco_hv_dcell.sym} 1100 0 0 0 {name=x3}
C {devices/iopin.sym} 500 -110 0 0 {name=p_p1 lab=p1}
C {devices/iopin.sym} 500 120 0 0 {name=p_m1 lab=m1}
C {devices/iopin.sym} 900 -110 0 0 {name=p_p2 lab=p2}
C {devices/iopin.sym} 900 120 0 0 {name=p_m2 lab=m2}
C {devices/iopin.sym} 130 -110 0 0 {name=p_vop lab=vop}
C {devices/iopin.sym} 130 120 0 0 {name=p_vom lab=vom}
