"""sampled_loop.py - exact sampled-data model of the SSPLL main loop (roadmap step 73).

Each reference period T the SSPD samples the VCO phase error; the pulsed Gm then dumps one charge packet
q[k] = beta*T*theta_e[k] into the loop filter a delay t_p after the sampling edge (t_p is set by the clock generator).
Between packets the filter (C2 || (R + C1)) and the VCO (d theta/dt = Kvco*v_c) evolve freely, so the loop is solved
exactly with the matrix exponential - no continuous-time approximation, so delay and sampling effects are included.

State x = [v_c, v_C1, theta]:  C2 dv_c/dt = i - (v_c - v_C1)/R ;  C1 dv_C1/dt = (v_c - v_C1)/R ;  d theta/dt = Kvco v_c
"""
import numpy as np
from scipy.linalg import expm


def _A(R, C1, C2, Kv):
    return np.array([[-1/(R*C2), 1/(R*C2), 0], [1/(R*C1), -1/(R*C1), 0], [Kv, 0, 0]])


def discrete(R, C1, C2, Kv, T, tp):
    """x[k+1] = Phi x[k] + G q[k]; theta[k] = Cx[k]  (q injected tp after the sample at kT)."""
    A = _A(R, C1, C2, Kv)
    Phi = expm(A*T)
    G = expm(A*(T - tp)) @ np.array([1/C2, 0, 0])
    return Phi, G, np.array([0, 0, 1.0])


def loop_gain(f, R, C1, C2, Kv, beta, T, tp):
    """Open-loop gain L(e^{j w T}) from theta_e to theta (q = beta*T*theta_e)."""
    Phi, G, C = discrete(R, C1, C2, Kv, T, tp)
    z = np.exp(2j*np.pi*np.asarray(f)*T)
    I = np.eye(3)
    return np.array([beta*T*(C @ np.linalg.solve(zz*I - Phi, G)) for zz in np.atleast_1d(z)])


def margins(R, C1, C2, Kv, beta, T, tp, fmin=1e4, fmax=None):
    """Crossover frequency (Hz) and phase margin (deg) of the sampled loop (search below f_ref/2)."""
    fmax = 0.49/T if fmax is None else fmax
    f = np.logspace(np.log10(fmin), np.log10(fmax), 3000)
    L = loop_gain(f, R, C1, C2, Kv, beta, T, tp)
    m = np.abs(L)
    i = np.where((m[:-1] >= 1) & (m[1:] < 1))[0]
    if len(i) == 0:
        return np.nan, np.nan
    i = i[0]
    x = (np.log(m[i]) - 0) / (np.log(m[i]) - np.log(m[i+1]))
    fc = np.exp(np.log(f[i]) + x*(np.log(f[i+1]) - np.log(f[i])))
    ph = np.angle(loop_gain([fc], R, C1, C2, Kv, beta, T, tp)[0], deg=True)
    return fc, 180 + (ph if ph < 0 else ph - 360)


def closed_loop(f, R, C1, C2, Kv, beta, T, tp):
    L = loop_gain(f, R, C1, C2, Kv, beta, T, tp)
    return L/(1 + L)


def step(R, C1, C2, Kv, beta, T, tp, ncyc=600, phi_step=0.0, f_step=0.0):
    """Cycle-by-cycle response to a reference phase step (rad) or a VCO frequency step (Hz).
    Returns t (s), phase error at each sample (rad), v_c (V) at each sample."""
    Phi, G, C = discrete(R, C1, C2, Kv, T, tp)
    x = np.zeros(3); th_ref = phi_step
    ts, es, vs = [], [], []
    for k in range(ncyc):
        th_ref_k = th_ref + 2*np.pi*f_step*k*T * 0    # a VCO frequency step is modelled as a ramp of the VCO phase
        e = th_ref_k - (C @ x) - 2*np.pi*f_step*k*T
        ts.append(k*T); es.append(e); vs.append(x[0])
        x = Phi @ x + G*(beta*T*e)
    return np.array(ts), np.array(es), np.array(vs)


def design(fc, pm_deg, beta, Kv, T, tp, iters=40):
    """R, C1, C2 so that the *sampled* loop has crossover fc and phase margin pm_deg, including the packet delay tp
    and sampling. Starts from the continuous closed form with the delay lag added to the lead, then corrects."""
    wc = 2*np.pi*fc
    lead = pm_deg + np.degrees(wc*tp)
    scale = 1.0
    for _ in range(iters):
        b = np.tan(np.radians(45 + lead/2))
        Ct = b*beta*Kv/(wc**2)*scale
        C2 = Ct/b**2; C1 = Ct - C2; R = b/(wc*C1)
        fc_s, pm_s = margins(R, C1, C2, Kv, beta, T, tp)
        if abs(fc_s/fc - 1) < 1e-4 and abs(pm_s - pm_deg) < 0.01:
            break
        scale *= (fc_s/fc)**2           # |L| ~ 1/w^2 near... crossover moves ~ sqrt(gain): fix with C
        lead += (pm_deg - pm_s)
    return dict(R=R, C1=C1, C2=C2, b=b, lead=lead, fc=fc_s, pm=pm_s,
                fz=1/(2*np.pi*R*C1), fp=(C1 + C2)/(2*np.pi*R*C1*C2))
