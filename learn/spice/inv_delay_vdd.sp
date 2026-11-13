* inv_delay_vdd.sp - SKY130 inverter delay vs supply (roadmap step 59), tt 27 C.
* Chain: ideal step -> INV1 (shaping) -> INV2 (measured) -> INV3 (load) ; plus 5 fF wiring at the measured output.
* Run from learn/spice:  ngspice -b inv_delay_vdd.sp   -> ../data/inv_delay_vdd.csv  (needs PDK_ROOT pointing at sky130A)
.lib "PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.subckt inv a y vdd
XP y a vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15
XN y a 0 0 sky130_fd_pr__nfet_01v8 w=1 l=0.15
.ends
Vdd vdd 0 {vdd}
Vin in 0 pulse(0 {vdd} 0.2n 20p 20p 1n 2n)
X1 in a vdd inv
X2 a y vdd inv
X3 y z vdd inv
Cw y 0 5f
.control
echo "vdd tphl tplh" > ../data/inv_delay_vdd.csv
foreach v 1.4 1.5 1.6 1.7 1.8 1.9 2.0
  alterparam vdd = $v
  reset
  tran 1p 3n
  let vh = $v/2
  meas tran tphl trig v(a) val=$&vh rise=1 targ v(y) val=$&vh fall=1
  meas tran tplh trig v(a) val=$&vh fall=1 targ v(y) val=$&vh rise=1
  echo "$v $&tphl $&tplh" >> ../data/inv_delay_vdd.csv
end
.endc
.end
