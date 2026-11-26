* vcdl_starved.sp - SKY130 current-starved delay line with a 4-bit capacitor bank (roadmap steps 60, 61, 64), tt 27 C, 1.8 V.
* Bias: V_ctrl drives the NMOS starving devices directly and, through a diode-connected PMOS mirror, the PMOS ones.
* Each cell: starved inverter + capacitor bank C_b = code x 0.5 fF (ideal caps here; MOS/MIM switched caps in the real NCB).
* Measured: delay of two cells (input of cell 2 to output of cell 3) vs V_ctrl for codes 0, 5, 10, 15.
* Run from learn/spice:  ngspice -b vcdl_starved.sp  -> ../data/vcdl_starved.csv
.lib "PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vctl=1.0 cb=0
.subckt scell a y vdd vbp vbn
XPS s1 vbp vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.3
XP  y a s1 vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15
XN  y a s2 0 sky130_fd_pr__nfet_01v8 w=1 l=0.15
XNS s2 vbn 0 0 sky130_fd_pr__nfet_01v8 w=1 l=0.3
Cb  y 0 {cb}
.ends
.subckt inv a y vdd
XP y a vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15
XN y a 0 0 sky130_fd_pr__nfet_01v8 w=1 l=0.15
.ends
Vdd vdd 0 1.8
Vc vbn 0 {vctl}
XMB vbp vbn 0 0 sky130_fd_pr__nfet_01v8 w=1 l=0.3
XPB vbp vbp vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.3
Vin in 0 pulse(0 1.8 0.3n 30p 30p 3n 6n)
X0 in a0 vdd inv
X1 a0 a1 vdd vbp vbn scell
X2 a1 a2 vdd vbp vbn scell
X3 a2 a3 vdd vbp vbn scell
X4 a3 a4 vdd vbp vbn scell
.control
echo "code vctl tdr tdf" > ../data/vcdl_starved.csv
foreach c 0 5 10 15
  foreach v 0.9 1.0 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8
    let cbv = $c*0.5e-15
    alterparam cb = $&cbv
    alterparam vctl = $v
    reset
    tran 1p 7n
    meas tran tdr trig v(a1) val=0.9 rise=1 targ v(a3) val=0.9 rise=1
    meas tran tdf trig v(a1) val=0.9 fall=1 targ v(a3) val=0.9 fall=1
    echo "$c $v $&tdr $&tdf" >> ../data/vcdl_starved.csv
  end
end
.endc
.end
