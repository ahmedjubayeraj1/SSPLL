v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_vco_hv: ring core + 6 AC-coupled buffers (4 dummies keep every node equally loaded)} 200 -800 0 0 0.35 0.35 {}
T {VRING = ring supply node, fed by the CCO current | VDDA = 3.3 V analog supply (buffers) | vtune = fine tuning} 200 -755 0 0 0.25 0.25 {}
N 960 -270 960 -520 {lab=}
N 1000 -270 1000 -560 {lab=}
N 420 -640 1000 -640 {lab=}
N 1000 -640 1580 -640 {lab=}
N 1000 -680 1000 -640 {lab=}
N 460 640 1000 640 {lab=}
N 1000 640 1540 640 {lab=}
N 1000 680 1000 640 {lab=}
N 960 270 960 640 {lab=}
N 900 -160 800 -160 {lab=}
N 740 -210 740 -220 {lab=}
N 740 -220 420 -220 {lab=}
N 740 -110 740 -100 {lab=}
N 740 -100 460 -100 {lab=}
N 600 -160 560 -160 {lab=}
N 900 0 800 0 {lab=}
N 740 -50 740 -60 {lab=}
N 740 -60 420 -60 {lab=}
N 740 50 740 60 {lab=}
N 740 60 460 60 {lab=}
N 600 0 570 0 {lab=}
N 900 160 800 160 {lab=}
N 740 110 740 100 {lab=}
N 740 100 420 100 {lab=}
N 740 210 740 220 {lab=}
N 740 220 460 220 {lab=}
N 600 160 570 160 {lab=}
N 420 -640 420 -220 {lab=}
N 420 -220 420 -60 {lab=}
N 420 -60 420 100 {lab=}
N 460 640 460 220 {lab=}
N 460 220 460 60 {lab=}
N 460 60 460 -100 {lab=}
N 1100 -160 1200 -160 {lab=}
N 1260 -210 1260 -220 {lab=}
N 1260 -220 1580 -220 {lab=}
N 1260 -110 1260 -100 {lab=}
N 1260 -100 1540 -100 {lab=}
N 1400 -160 1440 -160 {lab=}
N 1100 0 1200 0 {lab=}
N 1260 -50 1260 -60 {lab=}
N 1260 -60 1580 -60 {lab=}
N 1260 50 1260 60 {lab=}
N 1260 60 1540 60 {lab=}
N 1400 0 1430 0 {lab=}
N 1100 160 1200 160 {lab=}
N 1260 110 1260 100 {lab=}
N 1260 100 1580 100 {lab=}
N 1260 210 1260 220 {lab=}
N 1260 220 1540 220 {lab=}
N 1400 160 1430 160 {lab=}
N 1580 -640 1580 -220 {lab=}
N 1580 -220 1580 -60 {lab=}
N 1580 -60 1580 100 {lab=}
N 1540 640 1540 220 {lab=}
N 1540 220 1540 60 {lab=}
N 1540 60 1540 -100 {lab=}
C {sspll_vco_hv_core.sym} 1000 0 0 0 {name=xcore}
C {devices/iopin.sym} 960 -520 0 0 {name=p_VRING lab=VRING}
C {devices/ipin.sym} 1000 -560 0 0 {name=p_vtune lab=vtune}
C {devices/iopin.sym} 1000 -680 0 0 {name=p_VDDA lab=VDDA}
C {devices/iopin.sym} 1000 680 0 0 {name=p_VSS lab=VSS}
C {sspll_vco_hv_acbuf.sym} 700 -160 0 1 {name=xb_vop}
C {devices/opin.sym} 560 -160 0 1 {name=p_clkp lab=clkp}
C {sspll_vco_hv_acbuf.sym} 700 0 0 1 {name=xb_p1}
C {devices/lab_pin.sym} 570 0 0 0 {name=l_nc_p1_8 sig_type=std_logic lab=nc_p1}
C {sspll_vco_hv_acbuf.sym} 700 160 0 1 {name=xb_p2}
C {devices/lab_pin.sym} 570 160 0 0 {name=l_nc_p2_10 sig_type=std_logic lab=nc_p2}
C {sspll_vco_hv_acbuf.sym} 1300 -160 0 0 {name=xb_vom}
C {devices/opin.sym} 1440 -160 0 0 {name=p_clkm lab=clkm}
C {sspll_vco_hv_acbuf.sym} 1300 0 0 0 {name=xb_m1}
C {devices/lab_pin.sym} 1430 0 0 1 {name=l_nc_m1_14 sig_type=std_logic lab=nc_m1}
C {sspll_vco_hv_acbuf.sym} 1300 160 0 0 {name=xb_m2}
C {devices/lab_pin.sym} 1430 160 0 1 {name=l_nc_m2_16 sig_type=std_logic lab=nc_m2}
