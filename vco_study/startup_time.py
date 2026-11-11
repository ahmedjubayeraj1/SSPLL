"""startup_time.py - time for a symmetric power-up to reach full differential swing.
usage: python3 startup_time.py N SC I   (runs tt, ss, ff, fs, sf; two at a time)"""
import sys, subprocess, numpy as np
from multiprocessing import Pool
N, SC, I = sys.argv[1], sys.argv[2], sys.argv[3]
corners = [("tt", "27", "5f"), ("ss", "110", "10f"), ("ff", "-40", "0"), ("fs", "27", "5f"), ("sf", "27", "5f")]

def one(c):
    corner, temp, cpar = c
    fn = f"pw_{N}_{SC}_{corner}.sp"
    subprocess.run(["python3", "ringgen.py", N, SC, corner, temp, I, "0.9", cpar, "pwrup", fn], check=True)
    s = open(fn).read().replace("print f vdd_avg ppd", f"print f vdd_avg ppd\nwrdata {fn[:-3]}.txt v(vop) v(vom)")
    open(fn, "w").write(s)
    subprocess.run(["ngspice", "-b", fn], capture_output=True)
    d = np.loadtxt(f"{fn[:-3]}.txt"); t = d[:, 0]; vd = d[:, 1] - d[:, 3]
    res = []
    for th in (0.1, 1.0):
        k = np.where(abs(vd) > th)[0]
        res.append(t[k[0]]*1e9 if len(k) else float("nan"))
    m = t > t[-1] - 5e-9                      # final frequency from the last 5 ns
    i = np.where((vd[:-1] < 0) & (vd[1:] >= 0) & m[:-1])[0]
    f = (len(i)-1)/(t[i[-1]] - t[i[0]])
    return f"{N}x{SC} {corner:2s} |vd|>0.1V at {res[0]:5.2f} ns, |vd|>1V at {res[1]:5.2f} ns, final f {f/1e9:.3f} GHz"

with Pool(2) as p:
    for line in p.map(one, corners): print(line)
