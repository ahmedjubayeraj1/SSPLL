"""noisegrid.py - drain-current noise of a W=1 um, L=0.15 um sky130 1.8 V device over a (Vgs, Vds) grid,
from ngspice .noise with the pinned models. Splits it into white (thermal) and 1/f parts:
  B (flicker coefficient, A^2) = S(1 kHz) x 1 kHz ;  S_th = S(1 GHz) - B/1 GHz.
Writes noisegrid_<n|p>.npz used by isf2.py."""
import subprocess, re, numpy as np, os
from multiprocessing import Pool
VGS = np.array([0.2, 0.35, 0.5, 0.65, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8])
VDS = np.array([0.02, 0.1, 0.2, 0.35, 0.5, 0.7, 0.9, 1.2, 1.5, 1.8])
def one(args):
    dev, vgs, vds = args
    fn = f"ng_{dev}_{vgs}_{vds}.sp"
    if dev == 'n':
        ckt = f"vg g 0 dc {vgs} ac 1\nvd d 0 {vds}\nxm d g 0 0 sky130_fd_pr__nfet_01v8 w=1 l=0.15 nf=1 ad=0.29 as=0.29 pd=2.58 ps=2.58\n"
        m = "@m.xm.msky130_fd_pr__nfet_01v8"
    else:
        ckt = f"vs s 0 1.8\nvg g 0 dc {1.8-vgs} ac 1\nvd d 0 {1.8-vds}\nxm d g s s sky130_fd_pr__pfet_01v8 w=1 l=0.15 nf=1 ad=0.29 as=0.29 pd=2.58 ps=2.58\n"
        m = "@m.xm.msky130_fd_pr__pfet_01v8"
    open(fn, "w").write(f"""* noise grid
.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.temp 27
{ckt}h1 o 0 vd 1
.control
save all {m}[id] {m}[gm]
op
print {m}[id] {m}[gm]
option sparse
noise v(o) vg dec 1 1k 1g
setplot noise1
print onoise_spectrum
.endc
.end
""")
    out = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True).stdout
    os.remove(fn)
    idv = abs(float(re.search(r"\[id\] = (\S+)", out).group(1)))
    sp = dict((float(a), float(b)**2) for a, b in re.findall(r"^\d+\s+(\S+)\s+(\S+)", out, re.M))
    B = sp[1e3]*1e3
    Sth = max(sp[1e9] - B/1e9, 0.0)
    return idv, Sth, B, sp[1e3]/sp[1e4]
if __name__ == "__main__":
    for dev in ('n', 'p'):
        jobs = [(dev, a, b) for a in VGS for b in VDS]
        with Pool(2) as p: res = p.map(one, jobs)
        r = np.array(res).reshape(len(VGS), len(VDS), 4)
        np.savez(f"noisegrid_{dev}.npz", vgs=VGS, vds=VDS, id=r[..., 0], sth=r[..., 1], b=r[..., 2], slope=r[..., 3])
        i = list(VGS).index(1.0); j = list(VDS).index(0.9)
        print(f"{dev}fet W=1: at |Vgs|=1.0 |Vds|=0.9  Id={r[i,j,0]*1e6:.1f} uA  S_th={r[i,j,1]:.2e} A2/Hz  "
              f"B={r[i,j,2]:.2e} A2  corner={r[i,j,2]/r[i,j,1]/1e6:.1f} MHz  S(1k)/S(10k)={r[i,j,3]:.1f}")
