* corr_mos.sp - MOS reference values (tt, 27 C): Id, gm, gds, Cgg and drain-current noise
.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.temp 27
vgn gn 0 dc 0.9 ac 1
vdn dn 0 0.9
xn dn gn 0 0 sky130_fd_pr__nfet_01v8 w=4 l=0.15 nf=1 ad=1.16 as=1.16 pd=8.58 ps=8.58
vgp gp 0 dc 0.9 ac 1
vdp dp 0 0.9
vsp sp 0 1.8
xp dp gp sp sp sky130_fd_pr__pfet_01v8 w=8 l=0.15 nf=1 ad=2.32 as=2.32 pd=16.58 ps=16.58
* drain-current sensing for noise: V(on) = Id(noise) x 1 Ohm
hn on 0 vdn 1
hp op 0 vdp 1
.control
save all @m.xn.msky130_fd_pr__nfet_01v8[gm] @m.xn.msky130_fd_pr__nfet_01v8[gds] @m.xn.msky130_fd_pr__nfet_01v8[cgg]
+ @m.xp.msky130_fd_pr__pfet_01v8[gm] @m.xp.msky130_fd_pr__pfet_01v8[gds] @m.xp.msky130_fd_pr__pfet_01v8[cgg]
op
echo "nfet W=4 L=0.15 Vgs=Vds=0.9 | pfet W=8 L=0.15 Vsg=Vsd=0.9"
print -i(vdn) @m.xn.msky130_fd_pr__nfet_01v8[gm] @m.xn.msky130_fd_pr__nfet_01v8[gds] @m.xn.msky130_fd_pr__nfet_01v8[cgg]
print i(vdp) @m.xp.msky130_fd_pr__pfet_01v8[gm] @m.xp.msky130_fd_pr__pfet_01v8[gds] @m.xp.msky130_fd_pr__pfet_01v8[cgg]
option sparse
noise v(on) vgn dec 1 1meg 1g
setplot noise1
echo nfet drain-current noise A/rtHz
print onoise_spectrum
noise v(op) vgp dec 1 1meg 1g
setplot noise3
echo pfet drain-current noise A/rtHz
print onoise_spectrum
.endc
.end
