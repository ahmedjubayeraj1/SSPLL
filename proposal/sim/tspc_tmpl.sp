* TSPC divide-by-2 fmax check  CORNER=%C% T=%T% VDD=%V% F=%F%
.option scale=1e-6
.include "/home/claude/feas/core_%C%.lib"
.param mc_mm_switch=0 mc_pr_switch=0
.temp %T%
.subckt tspc ck d q vdd
* stage1
xp1 a d vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15 ad=0.58 as=0.58 pd=4.58 ps=4.58
xp2 n1 ck a vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15 ad=0.58 as=0.58 pd=4.58 ps=4.58
xn1 n1 d 0 0 sky130_fd_pr__nfet_01v8 w=1 l=0.15 ad=0.29 as=0.29 pd=2.58 ps=2.58
* stage2
xp3 n2 ck vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15 ad=0.58 as=0.58 pd=4.58 ps=4.58
xn2 n2 n1 b 0 sky130_fd_pr__nfet_01v8 w=1.5 l=0.15 ad=0.43 as=0.43 pd=3.58 ps=3.58
xn3 b ck 0 0 sky130_fd_pr__nfet_01v8 w=1.5 l=0.15 ad=0.43 as=0.43 pd=3.58 ps=3.58
* stage3
xp4 q n2 vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15 ad=0.58 as=0.58 pd=4.58 ps=4.58
xn4 q ck c 0 sky130_fd_pr__nfet_01v8 w=1.5 l=0.15 ad=0.43 as=0.43 pd=3.58 ps=3.58
xn5 c n2 0 0 sky130_fd_pr__nfet_01v8 w=1.5 l=0.15 ad=0.43 as=0.43 pd=3.58 ps=3.58
.ends
.subckt inv a y vdd
xp y a vdd vdd sky130_fd_pr__pfet_01v8 w=2 l=0.15 ad=0.58 as=0.58 pd=4.58 ps=4.58
xn y a 0 0 sky130_fd_pr__nfet_01v8 w=1 l=0.15 ad=0.29 as=0.29 pd=2.58 ps=2.58
.ends
vdd vdd 0 %V%
* clock: sine through two inverters (realistic edges)
vck cks 0 sin(%HALF% %HALF% %F%)
xi1 cks ck1 vdd inv
xi2 ck1 ck vdd inv
x1 ck q q vdd tspc
xi3 q qb vdd inv
cl q 0 3f
.tran 2p 20n
.control
run
meas tran t1 when v(q)=%HALF% rise=10
meas tran t2 when v(q)=%HALF% rise=20
let fout = 10/(t2-t1)
let ratio = %F%/fout
print fout ratio
.endc
.end
