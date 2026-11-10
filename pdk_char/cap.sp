* Capacitor characterization (pinned sky130A 1689ac3f), tt, 27 C, AC at 1 MHz
.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.param s1=5 s2=10 s3=20 s4=30
* MIM m3_1 (met3-capm-met4), square sides 5,10,20,30 um
v1 n1 0 dc 0 ac 1
xc1 n1 0 sky130_fd_pr__cap_mim_m3_1 w={s1} l={s1} mf=1
v2 n2 0 dc 0 ac 1
xc2 n2 0 sky130_fd_pr__cap_mim_m3_1 w={s2} l={s2} mf=1
v3 n3 0 dc 0 ac 1
xc3 n3 0 sky130_fd_pr__cap_mim_m3_1 w={s3} l={s3} mf=1
v4 n4 0 dc 0 ac 1
xc4 n4 0 sky130_fd_pr__cap_mim_m3_1 w={s4} l={s4} mf=1
* MIM m3_2 (met4-capm2-met5)
v5 n5 0 dc 0 ac 1
xc5 n5 0 sky130_fd_pr__cap_mim_m3_2 w={s2} l={s2} mf=1
v6 n6 0 dc 0 ac 1
xc6 n6 0 sky130_fd_pr__cap_mim_m3_2 w={s4} l={s4} mf=1
* nMOS gate cap, 1.8 V device, W=10 L=10, S/D/B grounded, gate bias swept below
v7 g7 0 dc 0.9 ac 1
xm7 0 g7 0 0 sky130_fd_pr__nfet_01v8 w=10 l=10 nf=1 ad=2.9 as=2.9 pd=20.58 ps=20.58
* 3.3 V (g5v0d10v5) nMOS gate cap W=10 L=10
v8 g8 0 dc 1.65 ac 1
xm8 0 g8 0 0 sky130_fd_pr__nfet_g5v0d10v5 w=10 l=10 nf=1 ad=2.9 as=2.9 pd=20.58 ps=20.58
.control
ac lin 1 1e6 1e6
echo "CAP idx C_fF"
foreach i 1 2 3 4 5 6 7 8
  let c = -imag(v{$i}#branch)/(2*pi*1e6)*1e15
  echo "CAP $i $&c"
end
alter v7 dc=0
alter v8 dc=0
ac lin 1 1e6 1e6
let c7 = -imag(v7#branch)/(2*pi*1e6)*1e15
let c8 = -imag(v8#branch)/(2*pi*1e6)*1e15
echo "CAP0 7 $&c7"
echo "CAP0 8 $&c8"
alter v7 dc=1.8
alter v8 dc=3.3
ac lin 1 1e6 1e6
let c7 = -imag(v7#branch)/(2*pi*1e6)*1e15
let c8 = -imag(v8#branch)/(2*pi*1e6)*1e15
echo "CAPMAX 7 $&c7"
echo "CAPMAX 8 $&c8"
.endc
.end
