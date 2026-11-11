"""isf.py - phase noise of a ring by impulse-sensitivity-function (ISF) extraction, ngspice + pinned PDK.
Method (Hajimiri-Lee):
  1. reference run: free-running ring, find period T and a settled zero crossing t0; save gm, gds of every
     device whose drain-source channel touches node p1 over one cycle.
  2. inject +q and -q (1 ps pulse) into p1 at K phases tau_k = t0 + k T/K; the shift of a later zero crossing
     gives h(tau) = dphi/dq  [rad/C]  (difference of +q and -q runs cancels time-grid errors and 2nd-order terms).
  3. thermal channel noise of each device, one-sided S_i(t) = 4kT (gamma*gm + gds); white, cyclostationary.
  4. L(df) = sum over the 2N equivalent nodes of <h(t)^2 S_i(t)> / (2 (2 pi df)^2)   [SSB, dBc/Hz]
Not included: flicker noise, CCO current-source noise, supply noise.
usage: python3 isf.py N SC I_A [K] [q_C] [gamma]
"""
import sys, subprocess, re, os, numpy as np
from multiprocessing import Pool
N, SC, I = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
K = int(sys.argv[4]) if len(sys.argv) > 4 else 24
q = float(sys.argv[5]) if len(sys.argv) > 5 else 2e-15
gamma = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
corner, temp, vt, cpar = "tt", "27", "0.9", "5f"
tag = f"isf_{N}_{SC}_{I}"
os.makedirs(tag, exist_ok=True)
R0, R1 = 70, 130                     # settle 70 cycles, measure 60 cycles later
devs = [f"x1.x{d}" for d in ("p2", "n2", "s2", "t1n", "t1p")] + ["x2.xt1n", "x2.xt1p"]
def typ(d): return "pfet_01v8" if d.endswith("p2") or d.endswith("t1p") else "nfet_01v8"
def vec(d, p): return f"@m.{d}.msky130_fd_pr__{typ(d)}[{p}]"

def make(mode, fn, tstop):
    subprocess.run(["python3", "ringgen.py", str(N), str(SC), corner, temp, I, vt, cpar, mode, fn], check=True)
    s = open(fn).read()
    s = s.replace("tran 1p 60n 0 1p uic", f"tran 1p {tstop} 0 1p uic").replace("rise=150", f"rise={R1}")
    s = s.replace(".control\n", ".control\n").replace("option noinit", "option noinit reltol=1e-4")
    if mode == "ref":
        sv = " ".join(vec(d, p) for d in devs for p in ("gm", "gds"))
        s = s.replace("option noinit reltol=1e-4", f"option noinit reltol=1e-4\nsave all {sv}")
        s = s.replace(f"meas tran tz when vd=0 rise={R1}", f"meas tran tz when vd=0 rise={R1}\nmeas tran t0 when vd=0 rise={R0}")
        s = re.sub(r"wrdata ref_waves.txt .*", f"wrdata {tag}/ref_g.txt {sv}\nprint t0", s)
    open(fn, "w").write(s)

def run(fn):
    out = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, timeout=3000).stdout
    r = {}
    for k in ("f", "tz", "t0"):
        m = re.search(rf"^{k} = (\S+)", out, re.M)
        if m: r[k] = float(m.group(1))
    return r

# reference
f_est = None
make("ref", f"{tag}/ref.sp", "200n")       # long enough for any f > 0.7 GHz
ref = run(f"{tag}/ref.sp")
T = 1/ref["f"]; t0 = ref["t0"]
print(f"N={N} SC={SC} I={I}: f = {ref['f']/1e9:.4f} GHz, T = {T*1e12:.2f} ps, t0 = {t0*1e9:.3f} ns")
# trim tstop for the injection runs
tstop = f"{(R1+3)*T*1e9:.2f}n"
jobs = []
for k in range(K):
    tau = t0 + k*T/K
    for sgn in (+1, -1):
        fn = f"{tag}/inj_{k}_{'p' if sgn>0 else 'm'}.sp"
        make(f"inj:p1:{tau:.6e}:{sgn*q:.4e}", fn, tstop)
        jobs.append((k, sgn, fn))
make("ref", f"{tag}/ref2.sp", tstop)        # same tstop reference for the record
with Pool(2) as pool:
    res = pool.map(run, [j[2] for j in jobs])
tz = {}
for (k, sgn, fn), r in zip(jobs, res): tz[(k, sgn)] = r["tz"]
h = np.array([-2*np.pi*(tz[(k, 1)] - tz[(k, -1)])/T/(2*q) for k in range(K)])     # rad/C
# conductances over one cycle
g = np.loadtxt(f"{tag}/ref_g.txt")
t = g[:, 0]; cols = g[:, 1::2]                     # wrdata: t v t v ...
m = (t >= t0) & (t < t0 + T)
tt, G = t[m], cols[m]
kT = 1.380649e-23*300.15
Si = np.zeros_like(tt)
for i, d in enumerate(devs):
    Si += 4*kT*(gamma*np.abs(G[:, 2*i]) + np.abs(G[:, 2*i+1]))
# periodic interpolation of h onto the fine grid
ph = (tt - t0)/T
hk_ph = np.arange(K)/K
hf = np.interp(ph, np.r_[hk_ph, 1.0], np.r_[h, h[0]])
# uniform-in-time average over one period
dt = np.diff(np.r_[tt, t0+T])
avg = np.sum(hf**2*Si*dt)/T
nodes = 2*N
L1M = 10*np.log10(nodes*avg/(2*(2*np.pi*1e6)**2))
Gamma_rms_over_qmax = np.sqrt(np.mean(h**2))
print(f"h_rms = {Gamma_rms_over_qmax:.3e} rad/C, h_dc = {np.mean(h):.3e}, <Si> = {np.sum(Si*dt)/T:.3e} A^2/Hz")
print(f"L(1 MHz) = {L1M:.1f} dBc/Hz  (thermal only, gamma={gamma}, {nodes} nodes)")
np.savetxt(f"{tag}/isf.txt", np.c_[hk_ph, h], header="phase h[rad/C]")
open(f"{tag}/result.txt", "w").write(f"f {ref['f']}\nL1M {L1M}\nh_rms {Gamma_rms_over_qmax}\n")
