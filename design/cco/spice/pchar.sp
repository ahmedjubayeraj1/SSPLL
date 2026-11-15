* g5v0d10v5 pfet: Vsg and Vov for given current (diode-connected), W = 10 um x m, L = LL
.lib "/home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice" CORNER
.temp TEMP
.param LL=LVAL
vdd s 0 3.3
idd g 0 dc 2.5m
xm g g s s sky130_fd_pr__pfet_g5v0d10v5 w=200 l={LL} nf=20 m=1
.control
op
let vsg = 3.3 - v(g)
print vsg
let vth = @m.xm.msky130_fd_pr__pfet_g5v0d10v5[vth]
print vth
.endc
.end
