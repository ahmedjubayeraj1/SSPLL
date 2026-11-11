"""isf2.py - phase noise of the ring with the MODEL's own noise (thermal + flicker), using
 - h(t) = dphi/dq from isf.py (results in isf_<N>_<SC>_<I>/isf.txt)
 - bias of every device on node p1 over one cycle (new reference run here)
 - drain-noise tables of a W=1 um device from ../correlation/noisegrid.py (thermal S_th and 1/f coefficient B)
Thermal:  L_th(df)  = 2N <h^2 S_th(t)> / (2 dw^2)
Flicker:  L_fl(df)  = 2N sum_dev <h(t) sqrt(B_dev(t))>^2 / df / (2 dw^2)   (1/f noise up-converted by the ISF dc part)
usage: python3 isf2.py N SC I"""
import sys, subprocess, re, numpy as np
from scipy.interpolate import RegularGridInterpolator as RGI
N, SC, I = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
tag = f"isf_{N}_{SC}_{I}"
dev = {"x1.xp2": ("p", 8), "x1.xn2": ("n", 4), "x1.xs2": ("n", 1.5), "x1.xt1n": ("n", 0.42),
       "x1.xt1p": ("p", 0.42), "x2.xt1n": ("n", 0.42), "x2.xt1p": ("p", 0.42)}
def vec(d, p): return f"@m.{d}.msky130_fd_pr__{'pfet' if dev[d][0]=='p' else 'nfet'}_01v8[{p}]"
subprocess.run(["python3", "ringgen.py", str(N), str(SC), "tt", "27", I, "0.9", "5f", "ref", f"{tag}/ref3.sp"], check=True)
s = open(f"{tag}/ref3.sp").read()
sv = " ".join(vec(d, p) for d in dev for p in ("vgs", "vds"))
s = s.replace("tran 1p 60n 0 1p uic", "tran 1p 60n 0 1p uic").replace("rise=150", "rise=130")
s = s.replace("option noinit", f"option noinit reltol=1e-4\nsave all {sv}")
s = s.replace("meas tran tz when vd=0 rise=130", "meas tran tz when vd=0 rise=130\nmeas tran t0 when vd=0 rise=70")
s = re.sub(r"wrdata ref_waves.txt .*", f"wrdata {tag}/ref_bias.txt {sv}\nprint t0", s)
open(f"{tag}/ref3.sp", "w").write(s)
out = subprocess.run(["ngspice", "-b", f"{tag}/ref3.sp"], capture_output=True, text=True).stdout
f0 = float(re.search(r"^f = (\S+)", out, re.M).group(1)); t0 = float(re.search(r"^t0 = (\S+)", out, re.M).group(1))
T = 1/f0
g = np.loadtxt(f"{tag}/ref_bias.txt"); t = g[:, 0]; cols = g[:, 1::2]
m = (t >= t0) & (t < t0 + T); tt = t[m]; C = cols[m]
dt = np.diff(np.r_[tt, t0 + T])
hk = np.loadtxt(f"{tag}/isf.txt"); K = len(hk)
hf = np.interp((tt - t0)/T, np.r_[hk[:, 0], 1.0], np.r_[hk[:, 1], hk[0, 1]])
tabs = {}
for k in ("n", "p"):
    z = np.load(f"../correlation/noisegrid_{k}.npz")
    tabs[k] = (RGI((z["vgs"], z["vds"]), z["sth"], bounds_error=False, fill_value=None),
               RGI((z["vgs"], z["vds"]), z["b"], bounds_error=False, fill_value=None))
th = 0.0; fl = 0.0; rows = []
for i, (d, (k, w)) in enumerate(dev.items()):
    vgs, vds = C[:, 2*i], C[:, 2*i+1]
    # ngspice reports BSIM4 pMOS vgs, vds already sign-corrected (positive when on): no flip needed
    rev = vds < 0                                   # device conducting the other way: swap source and drain
    vgs = np.where(rev, vgs - vds, vgs); vds = np.abs(vds)
    pts = np.c_[np.clip(vgs, 0.2, 1.8), np.clip(vds, 0.02, 1.8)]
    Sth = np.clip(tabs[k][0](pts), 0, None)*w*SC
    B = np.clip(tabs[k][1](pts), 0, None)*w*SC
    a_th = np.sum(hf**2*Sth*dt)/T
    a0 = np.sum(hf*np.sqrt(B)*dt)/T
    th += a_th; fl += a0**2
    rows.append((d, a_th, a0**2))
dw = 2*np.pi*1e6
Lth = 10*np.log10(2*N*th/(2*dw**2)); Lfl = 10*np.log10(2*N*fl/1e6/(2*dw**2))
Ltot = 10*np.log10(10**(Lth/10) + 10**(Lfl/10))
fc3 = 1e6*10**((Lfl - Lth)/10)
print(f"N={N} SC={SC} I={I}: f0 = {f0/1e9:.4f} GHz")
for d, a, b in rows: print(f"   {d:9s} thermal share {100*a/th:5.1f}%   flicker share {100*b/fl:5.1f}%")
print(f"L(1 MHz): thermal {Lth:.1f}, flicker {Lfl:.1f}, total {Ltot:.1f} dBc/Hz;  1/f^3 corner {fc3/1e6:.2f} MHz")
open(f"{tag}/result2.txt", "w").write(f"f0 {f0}\nLth {Lth}\nLfl {Lfl}\nLtot {Ltot}\nfc3 {fc3}\n")
