"""Phase-domain jitter budget for the SKY130 SSPLL + FFNC (Chipalooza #4 proposal).
Output-referred model (Nagam & Kinget JSSC'18 structure):
  phi_out = (1-Gc)(1-H) phi_vco_free + [H + Gc(1-H)] (N phi_ref + n_pd) + n_ncb
Run:  python3 jitter_budget.py   -> prints jitter table, writes budget.csv
"""
import numpy as np
fref, N = 49.152e6, 48
f0 = N*fref
f = np.logspace(np.log10(1e3), np.log10(200e6), 6000)
w = 2*np.pi*f
s = 1j*w

def dB2lin(L): return 10**(L/10)            # L in dBc/Hz (SSB) -> rad^2/Hz is 2*10^(L/10)

def vco_L(L1M, fc3):                         # ring + CCO: -20 dB/dec, 1/f^3 below fc3
    return L1M + 20*np.log10(1e6/f) + 10*np.log10(1 + fc3/f)

def floor_L(Lfloor, fc1=0.0):                # white floor with 1/f corner
    return Lfloor + 10*np.log10(1 + fc1/f)

def loop_H(fc, pm_deg=50):                   # type-II, zero/pole symmetric about fc
    pm = np.radians(pm_deg); b = (1+np.sin(pm))/np.cos(pm)
    wc = 2*np.pi*fc; wz, wp = wc/b, wc*b
    G = (wc**2*b) * (1+s/wz)/(s**2*(1+s/wp))  # |G(wc)| = 1 by construction
    G = G/np.abs((wc**2*b)*(1+1j*wc/wz)/((1j*wc)**2*(1+1j*wc/wp)))
    return G/(1+G)

def ffnc_G(gain_err, on):                    # cancellation path G_SSPD*G_NCB
    if not on: return np.zeros_like(f, dtype=complex)
    fp = (fref/7.8)/np.tan(np.radians(60)-np.pi/7.8)  # -60 deg at fref/7.8 (Nagam)
    x = f/fref
    return (1-gain_err)*np.sinc(x)*np.exp(-1j*np.pi*x)/(1+1j*f/fp)

def jitter(p, ffnc, band=(10e3, 40e6)):
    H = loop_H(p['fc'])
    Gc = ffnc_G(p['gerr'], ffnc)
    T_vco = np.abs((1-Gc)*(1-H))**2
    T_in  = np.abs(H + Gc*(1-H))**2
    Lv  = vco_L(p['vco1M'], p['fc3'])
    Lref = floor_L(p['ref'], p['ref_fc1']) + 20*np.log10(N)
    Lpd = floor_L(p['pd'])
    Lncb = floor_L(p['ncb'], p['ncb_fc1']) if ffnc else -400*np.ones_like(f)
    S = {'VCO (ring+CCO)': 2*dB2lin(Lv)*T_vco,
         'REF x N^2':      2*dB2lin(Lref)*T_in,
         'SSPD+CP':        2*dB2lin(Lpd)*T_in,
         'NCB':            2*dB2lin(Lncb)}
    m = (f >= band[0]) & (f <= band[1])
    out = {k: np.sqrt(np.trapezoid(v[m], f[m]))/(2*np.pi*f0) for k, v in S.items()}
    out['TOTAL'] = np.sqrt(sum(v**2 for v in out.values()))
    Ltot = 10*np.log10(sum(S.values())/2)
    return out, Ltot

# scenarios: typ = schematic-level expectation; pess = post-layout worst PVT + margin
typ  = dict(fc=2.5e6, vco1M=-92, fc3=200e3, ref=-152, ref_fc1=30e3, pd=-130,
            ncb=-150, ncb_fc1=1e6, gerr=0.10)
pess = dict(fc=2.5e6, vco1M=-88, fc3=500e3, ref=-148, ref_fc1=100e3, pd=-125,
            ncb=-146, ncb_fc1=3e6, gerr=0.30)
opt  = dict(typ, vco1M=-95, fc3=100e3, ref=-155)

rows = []
for name, p in [('optimistic', opt), ('typical', typ), ('pessimistic', pess)]:
    for ff in (False, True):
        j, L = jitter(p, ff)
        i300 = np.argmin(abs(f-300e3)); i1M = np.argmin(abs(f-1e6))
        rows.append((name, 'FFNC on' if ff else 'FFNC off', j, L[i300], L[i1M]))
        print(f"{name:11s} {'FFNC on ' if ff else 'FFNC off'}  "
              f"total {j['TOTAL']*1e15:6.0f} fs | " +
              " ".join(f"{k} {v*1e15:5.0f}" for k, v in j.items() if k!='TOTAL') +
              f" | L(300k) {L[i300]:6.1f}  L(1M) {L[i1M]:6.1f} dBc/Hz")
# loop-bandwidth sensitivity, typical
print("\nfc sweep (typical):")
for fc in (1.5e6, 2.0e6, 2.5e6, 3.0e6, 4.0e6):
    a = jitter(dict(typ, fc=fc), False)[0]['TOTAL']; b = jitter(dict(typ, fc=fc), True)[0]['TOTAL']
    print(f"  fc {fc/1e6:3.1f} MHz: off {a*1e15:5.0f} fs  on {b*1e15:5.0f} fs  reduction {100*(1-b/a):4.1f}%")
# 1k-100M band for Nagam comparison
a = jitter(typ, False, (1e3,100e6))[0]['TOTAL']; b = jitter(typ, True, (1e3,100e6))[0]['TOTAL']
print(f"\ntypical, 1 kHz-100 MHz: off {a*1e15:.0f} fs, on {b*1e15:.0f} fs")
with open('budget.csv','w') as fh:
    fh.write("scenario,ffnc,total_fs,vco_fs,ref_fs,pd_fs,ncb_fs,L300k,L1M\n")
    for n, ff, j, l3, l1 in rows:
        fh.write(f"{n},{ff},{j['TOTAL']*1e15:.0f},{j['VCO (ring+CCO)']*1e15:.0f},{j['REF x N^2']*1e15:.0f},"
                 f"{j['SSPD+CP']*1e15:.0f},{j['NCB']*1e15:.0f},{l3:.1f},{l1:.1f}\n")
