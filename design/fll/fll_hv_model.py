#!/usr/bin/env python3
"""fll_hv_model.py - time-domain model of frequency acquisition (FLL) and the hand-over to the
sub-sampling loop, with the loop filter, the VCO tuning curves, the Gm detector charge curve and the
clock-generator packet timing. Method M26 (fixed-step behavioural simulation, every block reduced to its measured law).

Blocks and laws (all times from the reference rising edge of each period, T = 20 ns):
  VCO      f(V_cont) from the VCO tuning curve at the corner (negative slope: higher V_cont = slower ring),
           scaled in current so that 800 MHz falls at V_cont = 1.8 V (the coarse code puts it there).
  divider  /16: an edge every 16 VCO cycles, t_div after the VCO edge.
  PFD      tri-state: UP set by the reference edge, DN by the divider edge, both cleared t_rst after both are set.
  dead zone  the charge pump conducts only the part of UP / DN longer than t_dz (removes the reset pulse).
  FLL CP   UP (VCO slow) sinks I_cp from vctl (lower V_cont = faster ring), DN sources I_cp.
  SSPLL    every period the SSPD samples the VCO phase at the reference edge; the Gm delivers q(phi) (the Gm design
           curve, +-6 fC) centred t_p after the sample, over tau.
  lock detector  o1 = UP still high t_w after the reference edge; o2 = DN still high t_w after the divider edge.
           Unlocked: t_w = w_in (narrow); nlock consecutive periods with o1 = o2 = 0 set lock_det.
           Locked: t_w = w_out (wide); nloss consecutive periods with o1 or o2 clear it (hysteresis, so the SSPLL may
           move the divider phase by up to half a VCO period without losing lock_det).
           While lock_det = 1 the FLL charge pump is off; the SSPLL alone holds lock.
Filter: exact discrete state update of C2 || (R1 + C1) for each fixed step with constant current."""
import os, sys, json
import numpy as np
from scipy.linalg import expm
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
T, N, F0 = 20e-9, 16, 800e6

# loop filter (tt 27 C, 1.8 V) + 175 fF load
R1, C1, C2 = 20.26e3, 8.836e-12, 0.960e-12 + 0.175e-12


def tuning(corner="tt"):
    c = json.load(open(os.path.join(ROOT, "design", "vco", "data", "vco_hv_char_hl6.json")))["f_vs_vtune"]
    a = np.array(c[{"tt": "tt_27", "ss": "ss_110", "ff": "ff_-40"}[corner]])
    v, f = a[:, 0], a[:, 1]
    # extend: flat below 0.6 V (tuning switch off), last slope above 2.6 V down to 3.3 V
    v = np.r_[0.0, v, 3.3]; f = np.r_[f[0], f, f[-1] + (f[-1] - f[-2])/(v[-2] - v[-3])*(3.3 - v[-2])]
    k = F0/np.interp(1.8, v, f)              # coarse code: lock point at 1.8 V
    return lambda x: k*np.interp(x, v, f)


def detector():
    d = json.load(open(os.path.join(ROOT, "design", "sscp", "data", "sscp_hv_det.json")))
    r = [x for x in d if x["corner"] == "tt" and x["vc"] == 1.8][0]
    a = np.array(r["rows"]); o = np.argsort(a[:, 0]); ph, q = a[o, 0], a[o, 1]
    ph = np.r_[ph[-1] - 2*np.pi, ph, ph[0] + 2*np.pi]; q = np.r_[q[-1], q, q[0]]
    # orientation: theta = VCO phase at the sample; VCO ahead -> must slow down -> raise V_cont -> charge into vctl > 0
    phi0 = r["phi0"]; s = np.sign(np.interp(phi0 + 0.05, ph, q) - np.interp(phi0 - 0.05, ph, q))
    return lambda x: s*np.interp((phi0 + x) % (2*np.pi), ph, q)


P0 = dict(icp=60e-6, t_dz=0.3e-9, t_rst=0.2e-9, w_in=0.6e-9, w_out=2.0e-9, nlock=16, nloss=4, t_div=0.9e-9,
          t_p=2.62e-9, tau=0.53e-9, qscale=1.0, sspll=True, fll=True)


def simulate(v0=1.0, corner="tt", p=P0, tstop=12e-6, dt=0.05e-9, theta0=0.3, seed=None):
    p = dict(P0, **p)
    f = tuning(corner); q = detector()
    A = np.array([[-1/(R1*C2), 1/(R1*C2)], [1/(R1*C1), -1/(R1*C1)]]); B = np.array([1/C2, 0.0])
    M = expm(np.block([[A, B[:, None]], [np.zeros((1, 3))]])*dt); Ad, Bd = M[:2, :2], M[:2, 2]
    x = np.array([v0, v0])
    theta = theta0                                  # VCO phase in cycles
    nstep = int(round(T/dt)); nper = int(tstop/T)
    divcnt = 0.0                                     # VCO cycles since the last divider edge (counts to 16)
    divcnt = theta0 % 16
    UP = DN = False; t_up = t_dn = 0.0; both_t = None
    o1 = o2 = False; cnt = 0; lock = False
    pend_div = []                                    # pending divider edge times (after t_div)
    out = dict(t=[], v=[], f=[], lock=[], err=[], ph=[])
    theta_ref = theta0                               # where an ideal 800 MHz clock would be (cycles)
    for k in range(nper):
        t0 = k*T
        # SSPD sample at the reference edge (t0): phase error of the VCO in radians (wrapped)
        ph_s = 2*np.pi*(theta % 1.0)
        qs = p["qscale"]*q(ph_s) if p["sspll"] else 0.0
        i_gm_on, i_gm_off = p["t_p"] - p["tau"]/2, p["t_p"] + p["tau"]/2
        i_gm = qs/p["tau"]
        UP = True if p["fll"] else UP; t_up = 0.0
        t_w = p["w_out"] if lock else p["w_in"]      # window: narrow to acquire, wide to hold (hysteresis)
        o1_check = t_w; o1_done = False
        for j in range(nstep):
            t = j*dt
            # VCO advance and divider edges
            fv = f(x[0]); dth = fv*dt
            divcnt += dth; theta += dth
            if divcnt >= 16:
                divcnt -= 16
                pend_div.append(t0 + t + p["t_div"])
            if pend_div and t0 + t >= pend_div[0]:
                pend_div.pop(0)
                if p["fll"]:
                    DN = True; t_dn = 0.0
            # PFD reset
            if UP and DN:
                if both_t is None:
                    both_t = 0.0
                both_t += dt
                if both_t >= p["t_rst"]:
                    UP = DN = False; both_t = None
            if UP: t_up += dt
            if DN: t_dn += dt
            # lock detector samples
            if not o1_done and t >= o1_check:
                o1 = UP; o1_done = True
            # charge pump (dead zone) + Gm packet
            i = 0.0
            if p["fll"] and not lock:
                if UP and t_up > p["t_dz"]: i -= p["icp"]
                if DN and t_dn > p["t_dz"]: i += p["icp"]
            if i_gm_on <= t < i_gm_off:
                i += i_gm
            x = Ad @ x + Bd*i
            x[0] = min(max(x[0], 0.0), 3.3)          # V_cont cannot leave the rails
        # lock counter, clocked once per period after o1 / o2 have been sampled
        o2 = DN and t_dn > t_w
        if not lock:
            cnt = 0 if (o1 or o2) else cnt + 1
            if cnt >= p["nlock"]:
                lock, cnt = True, 0
        else:
            cnt = cnt + 1 if (o1 or o2) else 0          # consecutive out-of-window periods
            if cnt >= p["nloss"]:
                lock, cnt = False, 0
        theta_ref += F0*T
        err = ((theta - theta_ref + 0.5) % 1.0) - 0.5      # VCO phase vs an ideal 800 MHz clock, in VCO cycles
        out["t"].append(t0 + T); out["v"].append(x[0]); out["f"].append(f(x[0])); out["lock"].append(lock)
        out["ph"].append(theta - theta_ref)
    out = {k: np.array(v) for k, v in out.items()}
    return out


def lock_time(o, tol=10e-12):
    """time after which the frequency stays 800 MHz +-100 ppm and the phase stays within +-tol of its final value"""
    ph = o["ph"]/F0                                   # seconds of VCO phase vs the ideal clock (unwrapped)
    fin = ph[-1]
    bad = np.where((np.abs(ph - fin) > tol))[0]
    return o["t"][bad[-1] + 1] if len(bad) and bad[-1] + 1 < len(ph) else (o["t"][0] if not len(bad) else np.nan)


if __name__ == "__main__":
    import time
    t_ = time.time()
    o = simulate(1.0, "tt", tstop=6e-6)
    print(f"{time.time() - t_:.1f} s; final f {o['f'][-1]/1e6:.4f} MHz, V {o['v'][-1]:.3f}, lock_det {o['lock'][-1]}, "
          f"lock time {lock_time(o)*1e6:.2f} us, first lock_det {o['t'][np.argmax(o['lock'])]*1e6 if o['lock'].any() else None}")
