* kitwrap_test.sp - your LF cell exactly as the Virtuoso netlist writes it (kit names, SI units),
* through sspll_kit_wrap.spice + the converted frozen models. Plus the MOS reference bias.
.lib OUT/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.include OUT/sspll_kit_wrap.spice
.temp 27
* --- LF, from the ADE netlist: C0 (vctrl 0) cap_mim_m3_1 l=20u w=20u m=2 / R0 (vctrl net4 0) res_xhigh_po_0p35 r=9.70657K l=1.36u w=350n
vt vctrl 0 dc 1 ac 1
xc0 vctrl 0 cap_mim_m3_1 l=20u w=20u m=2
xr0 vctrl net4 0 res_xhigh_po_0p35 r=9.70657k l=1.36u w=350n
vs net4 0 0
* --- MOS reference: nfet W=4 L=0.15, Vgs=Vds=0.9 (expect 188.5 uA)
vg g 0 0.9
vd d 0 0.9
xn d g 0 0 nfet_01v8 w=4u l=0.15u ad=1.16p as=1.16p pd=8.58u ps=8.58u
.control
op
echo "R0 (kit names, SI units) at 1 V:"
print 1/i(vs)
echo "nfet Id:"
print -i(vd)
ac lin 1 1meg 1meg
let ctot = (imag(i(vt))*-1)/(2*pi*1e6)*1e15 - 0
echo "C0 total incl. m=2 (fF), from source current minus resistor branch:"
let cr = imag(i(vs))/(2*pi*1e6)*1e15
print ctot cr
.endc
.end
