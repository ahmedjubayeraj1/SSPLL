v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_vco: ring core + 10 AC-coupled buffers (8 dummies keep every node equally loaded)} 200 -800 0 0 0.35 0.35 {}
T {VDD = ring supply node, fed by the CCO current | VDDBUF = 1.8 V regulated rail | vtune = fine tuning} 200 -755 0 0 0.25 0.25 {}
N 960 -430 960 -520 {lab=}
N 1000 -430 1000 -560 {lab=}
N 420 -640 1000 -640 {lab=}
N 1000 -640 1580 -640 {lab=}
N 1000 -680 1000 -640 {lab=}
N 460 640 1000 640 {lab=}
N 1000 640 1540 640 {lab=}
N 1000 680 1000 640 {lab=}
N 960 430 960 640 {lab=}
N 900 -320 800 -320 {lab=}
N 740 -370 740 -380 {lab=}
N 740 -380 420 -380 {lab=}
N 740 -270 740 -260 {lab=}
N 740 -260 460 -260 {lab=}
N 600 -320 560 -320 {lab=}
N 850 -320 850 -400 {lab=}
N 900 -160 800 -160 {lab=}
N 740 -210 740 -220 {lab=}
N 740 -220 420 -220 {lab=}
N 740 -110 740 -100 {lab=}
N 740 -100 460 -100 {lab=}
N 600 -160 570 -160 {lab=}
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
N 900 320 800 320 {lab=}
N 740 270 740 260 {lab=}
N 740 260 420 260 {lab=}
N 740 370 740 380 {lab=}
N 740 380 460 380 {lab=}
N 600 320 570 320 {lab=}
N 420 -640 420 -380 {lab=}
N 420 -380 420 -220 {lab=}
N 420 -220 420 -60 {lab=}
N 420 -60 420 100 {lab=}
N 420 100 420 260 {lab=}
N 460 640 460 380 {lab=}
N 460 380 460 220 {lab=}
N 460 220 460 60 {lab=}
N 460 60 460 -100 {lab=}
N 460 -100 460 -260 {lab=}
N 1100 -320 1200 -320 {lab=}
N 1260 -370 1260 -380 {lab=}
N 1260 -380 1580 -380 {lab=}
N 1260 -270 1260 -260 {lab=}
N 1260 -260 1540 -260 {lab=}
N 1400 -320 1440 -320 {lab=}
N 1150 -320 1150 -400 {lab=}
N 1100 -160 1200 -160 {lab=}
N 1260 -210 1260 -220 {lab=}
N 1260 -220 1580 -220 {lab=}
N 1260 -110 1260 -100 {lab=}
N 1260 -100 1540 -100 {lab=}
N 1400 -160 1430 -160 {lab=}
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
N 1100 320 1200 320 {lab=}
N 1260 270 1260 260 {lab=}
N 1260 260 1580 260 {lab=}
N 1260 370 1260 380 {lab=}
N 1260 380 1540 380 {lab=}
N 1400 320 1430 320 {lab=}
N 1580 -640 1580 -380 {lab=}
N 1580 -380 1580 -220 {lab=}
N 1580 -220 1580 -60 {lab=}
N 1580 -60 1580 100 {lab=}
N 1580 100 1580 260 {lab=}
N 1540 640 1540 380 {lab=}
N 1540 380 1540 220 {lab=}
N 1540 220 1540 60 {lab=}
N 1540 60 1540 -100 {lab=}
N 1540 -100 1540 -260 {lab=}
C {sspll_vco_core.sym} 1000 0 0 0 {name=xcore}
C {devices/iopin.sym} 960 -520 0 0 {name=p_VDD lab=VDD}
C {devices/ipin.sym} 1000 -560 0 0 {name=p_vtune lab=vtune}
C {devices/iopin.sym} 1000 -680 0 0 {name=p_VDDBUF lab=VDDBUF}
C {devices/iopin.sym} 1000 680 0 0 {name=p_VSS lab=VSS}
C {sspll_vco_acbuf.sym} 700 -320 0 1 {name=xb_vop}
C {devices/opin.sym} 560 -320 0 1 {name=p_clkp lab=clkp}
C {devices/opin.sym} 850 -400 0 0 {name=p_vop lab=vop}
C {sspll_vco_acbuf.sym} 700 -160 0 1 {name=xb_p1}
C {devices/lab_pin.sym} 570 -160 0 0 {name=l_nc_p1_9 sig_type=std_logic lab=nc_p1}
C {sspll_vco_acbuf.sym} 700 0 0 1 {name=xb_p2}
C {devices/lab_pin.sym} 570 0 0 0 {name=l_nc_p2_11 sig_type=std_logic lab=nc_p2}
C {sspll_vco_acbuf.sym} 700 160 0 1 {name=xb_p3}
C {devices/lab_pin.sym} 570 160 0 0 {name=l_nc_p3_13 sig_type=std_logic lab=nc_p3}
C {sspll_vco_acbuf.sym} 700 320 0 1 {name=xb_p4}
C {devices/lab_pin.sym} 570 320 0 0 {name=l_nc_p4_15 sig_type=std_logic lab=nc_p4}
C {sspll_vco_acbuf.sym} 1300 -320 0 0 {name=xb_vom}
C {devices/opin.sym} 1440 -320 0 0 {name=p_clkm lab=clkm}
C {devices/opin.sym} 1150 -400 0 1 {name=p_vom lab=vom}
C {sspll_vco_acbuf.sym} 1300 -160 0 0 {name=xb_m1}
C {devices/lab_pin.sym} 1430 -160 0 1 {name=l_nc_m1_20 sig_type=std_logic lab=nc_m1}
C {sspll_vco_acbuf.sym} 1300 0 0 0 {name=xb_m2}
C {devices/lab_pin.sym} 1430 0 0 1 {name=l_nc_m2_22 sig_type=std_logic lab=nc_m2}
C {sspll_vco_acbuf.sym} 1300 160 0 0 {name=xb_m3}
C {devices/lab_pin.sym} 1430 160 0 1 {name=l_nc_m3_24 sig_type=std_logic lab=nc_m3}
C {sspll_vco_acbuf.sym} 1300 320 0 0 {name=xb_m4}
C {devices/lab_pin.sym} 1430 320 0 1 {name=l_nc_m4_26 sig_type=std_logic lab=nc_m4}
