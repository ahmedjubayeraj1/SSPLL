v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sspll_fll_div16: clkp (0..VDDA) -> down-shifter -> four TSPC /2 -> div = clkp / 16 (50 MHz at lock).} 40 -300 0 0 0.3 0.3 {}
N 100 0 300 0 {lab=}
N 500 0 560 0 {lab=}
N 560 0 700 0 {lab=}
N 900 20 900 80 {lab=}
N 760 -70 760 -110 {lab=}
N 760 70 760 110 {lab=}
N 900 -20 960 -20 {lab=}
N 960 -20 960 0 {lab=}
N 960 0 1100 0 {lab=}
N 1300 20 1300 80 {lab=}
N 1160 -70 1160 -110 {lab=}
N 1160 70 1160 110 {lab=}
N 1300 -20 1360 -20 {lab=}
N 1360 -20 1360 0 {lab=}
N 1360 0 1500 0 {lab=}
N 1700 20 1700 80 {lab=}
N 1560 -70 1560 -110 {lab=}
N 1560 70 1560 110 {lab=}
N 1700 -20 1760 -20 {lab=}
N 1760 -20 1760 0 {lab=}
N 1760 0 1900 0 {lab=}
N 2100 20 2100 80 {lab=}
N 1960 -70 1960 -110 {lab=}
N 1960 70 1960 110 {lab=}
N 2100 -20 2400 -20 {lab=}
N 360 -50 360 -90 {lab=}
N 360 50 360 90 {lab=}
N 100 300 180 300 {lab=}
N 100 360 180 360 {lab=}
C {devices/ipin.sym} 100 0 0 0 {name=p_clkp lab=clkp}
C {sspll_fll_ds.sym} 400 0 0 0 {name=xds}
C {sspll_fll_tspc.sym} 800 0 0 0 {name=xt1}
C {devices/lab_pin.sym} 900 80 0 1 {name=l_c1b_3 sig_type=std_logic lab=c1b}
C {devices/lab_pin.sym} 760 -110 0 0 {name=l_VDDD_4 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 760 110 0 0 {name=l_VSSD_5 sig_type=std_logic lab=VSSD}
C {sspll_fll_tspc.sym} 1200 0 0 0 {name=xt2}
C {devices/lab_pin.sym} 1300 80 0 1 {name=l_c2b_7 sig_type=std_logic lab=c2b}
C {devices/lab_pin.sym} 1160 -110 0 0 {name=l_VDDD_8 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1160 110 0 0 {name=l_VSSD_9 sig_type=std_logic lab=VSSD}
C {sspll_fll_tspc.sym} 1600 0 0 0 {name=xt3}
C {devices/lab_pin.sym} 1700 80 0 1 {name=l_c3b_11 sig_type=std_logic lab=c3b}
C {devices/lab_pin.sym} 1560 -110 0 0 {name=l_VDDD_12 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1560 110 0 0 {name=l_VSSD_13 sig_type=std_logic lab=VSSD}
C {sspll_fll_tspc.sym} 2000 0 0 0 {name=xt4}
C {devices/lab_pin.sym} 2100 80 0 1 {name=l_c4b_15 sig_type=std_logic lab=c4b}
C {devices/lab_pin.sym} 1960 -110 0 0 {name=l_VDDD_16 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 1960 110 0 0 {name=l_VSSD_17 sig_type=std_logic lab=VSSD}
C {devices/opin.sym} 2400 -20 0 1 {name=p_div lab=div}
C {devices/lab_pin.sym} 360 -90 0 0 {name=l_VDDD_19 sig_type=std_logic lab=VDDD}
C {devices/lab_pin.sym} 360 90 0 0 {name=l_VSSD_20 sig_type=std_logic lab=VSSD}
C {devices/iopin.sym} 100 300 0 0 {name=p_VDDD lab=VDDD}
C {devices/lab_pin.sym} 180 300 0 1 {name=l_VDDD_22 sig_type=std_logic lab=VDDD}
C {devices/iopin.sym} 100 360 0 0 {name=p_VSSD lab=VSSD}
C {devices/lab_pin.sym} 180 360 0 1 {name=l_VSSD_24 sig_type=std_logic lab=VSSD}
