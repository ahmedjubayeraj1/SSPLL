"""compare.py - 3-stage (2.4 GHz, N=48) vs 5-stage x1.5 (1.6 GHz, N=32) using the proposal jitter model.
VCO phase noise from isf.py (thermal); the proposal's 1/f^3 corner and pessimistic +4 dB are kept the same."""
import math, sys
sys.path.insert(0, "../proposal")
src = open("../proposal/jitter_budget.py").read().split("# scenarios:")[0]
ns = {}; exec(src, ns)
def budget(N, fref, L1M):
    ns['fref'], ns['N'], ns['f0'] = fref, N, N*fref
    typ = dict(fc=2.5e6, vco1M=L1M, fc3=200e3, ref=-152, ref_fc1=30e3, pd=-130, ncb=-150, ncb_fc1=1e6, gerr=0.10)
    pess = dict(typ, vco1M=L1M+4, fc3=500e3, ref=-148, ref_fc1=100e3, pd=-125, ncb=-146, ncb_fc1=3e6, gerr=0.30)
    r = {}
    for nm, p in (('typ', typ), ('pess', pess)):
        for ff in (False, True):
            j, L = ns['jitter'](p, ff); i = abs(ns['f']-300e3).argmin()
            r[(nm, ff)] = (j['TOTAL']*1e12, L[i], j)
    return r
cases = [l.split() for l in open("cases.txt") if l.strip() and not l.startswith('#')]
print(f"{'case':28s} {'f0':>6s} {'Iring':>6s} {'Pvco':>5s} {'L1M':>6s} {'FoMvco':>6s} | jit typ off/on   pess off/on | L300k typ off/on | Ptot on | FoM_pll")
for name, N, fref, I_mA, L1M, other in cases:
    N, fref, I_mA, L1M, other = int(N), float(fref), float(I_mA), float(L1M), float(other)
    f0 = N*fref; P = I_mA*9/8*3.3
    fom_vco = -L1M + 20*math.log10(f0/1e6) - 10*math.log10(P)
    r = budget(N, fref, L1M)
    to, tn, po, pn = r[('typ',False)], r[('typ',True)], r[('pess',False)], r[('pess',True)]
    Pt = P + other
    fom = 20*math.log10(tn[0]*1e-12) + 10*math.log10(Pt)
    print(f"{name:28s} {f0/1e9:6.3f} {I_mA:6.2f} {P:5.2f} {L1M:6.1f} {fom_vco:6.1f} | {to[0]:5.2f}/{tn[0]:5.2f}   {po[0]:5.2f}/{pn[0]:5.2f} | {to[1]:6.1f}/{tn[1]:6.1f} | {Pt:6.2f} | {fom:6.1f}")
