* kitwrap_m.sp - does instance m= multiply through the wrapper subcircuit (ngspice-42)?
.lib OUT/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.include OUT/sspll_kit_wrap.spice
v1 a 0 dc 0 ac 1
xc1 a b1 cap_mim_m3_1 l=20u w=20u
vb1 b1 0 0
xc2 a b2 cap_mim_m3_1 l=20u w=20u m=2
vb2 b2 0 0
xn1 a2 a2 n1 0 nfet_01v8 w=4u l=0.15u
vn1 n1 0 0
xn2 a2 a2 n2 0 nfet_01v8 w=4u l=0.15u m=7
vn2 n2 0 0
va a2 0 0.9
.control
op
print i(vn2)/i(vn1)
ac lin 1 1meg 1meg
let c1 = imag(i(vb1))/(2*pi*1e6)*1e15
let c2 = imag(i(vb2))/(2*pi*1e6)*1e15
print c1 c2
.endc
.end
