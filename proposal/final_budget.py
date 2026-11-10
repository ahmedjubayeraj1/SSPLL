"""Final design point: 5-stage pseudo-differential ring (1.5x cell), N = 32, f_ref 45-55 MHz (50 MHz nominal).
Ring phase noise scaled from the 1.769 GHz estimate (-95.2 dBc/Hz at 1 MHz) as L ~ f0^2/P with P ~ f0."""
import math
src = open("jitter_budget.py").read().split("# scenarios:")[0]
ns = {}; exec(src, ns)
N = 32
def point(fref, fc=2.5e6):
    ns['fref'], ns['N'], ns['f0'] = fref, N, N*fref
    f0 = N*fref
    L1 = -95.2 + 10*math.log10(f0/1.769e9)
    typ = dict(fc=fc, vco1M=L1, fc3=200e3, ref=-152, ref_fc1=30e3, pd=-130, ncb=-150, ncb_fc1=1e6, gerr=0.10)
    pess = dict(typ, vco1M=L1+4, fc3=500e3, ref=-148, ref_fc1=100e3, pd=-125, ncb=-146, ncb_fc1=3e6, gerr=0.30)
    out = {}
    for nm, p in (('typ', typ), ('pess', pess)):
        for ff in (False, True):
            j, L = ns['jitter'](p, ff)
            i = abs(ns['f']-300e3).argmin()
            out[(nm, ff)] = (j['TOTAL']*1e12, L[i])
    return f0, L1, out
print("f_ref  f_out   L1M   | typ off  typ on | pess off pess on | L300k typ off/on  pess off/on | reduction typ/pess")
for fr in (45e6, 50e6, 55e6):
    f0, L1, o = point(fr)
    t0, t1, p0, p1 = o[('typ',False)], o[('typ',True)], o[('pess',False)], o[('pess',True)]
    print(f"{fr/1e6:4.0f}  {f0/1e9:5.3f}  {L1:5.1f} | {t0[0]:6.2f} {t1[0]:7.2f} | {p0[0]:7.2f} {p1[0]:7.2f} | "
          f"{t0[1]:6.1f}/{t1[1]:6.1f}   {p0[1]:6.1f}/{p1[1]:6.1f} | {100*(1-t1[0]/t0[0]):4.1f}% / {100*(1-p1[0]/p0[0]):4.1f}%")
# power
def ring_mA_tt(f):  return 1.45*f/1.769e9          # x1.5 ring, tt 27C, 10 fF (from 1.769 GHz point)
def ring_mA_ss(f):  return 2.0*f/1.928e9           # x1.5 ring, ss 110C, 10 fF (2.0 mA -> 1.928 GHz)
other_tt_on, other_tt_off = 2.55, 1.75
for fr in (50e6,):
    f0 = N*fr
    vco_tt = ring_mA_tt(f0)*9/8*3.3
    print(f"\nPower @ {f0/1e9:.2f} GHz tt: VCO {vco_tt:.2f} mW, total on {vco_tt+other_tt_on:.2f}, off {vco_tt+other_tt_off:.2f}")
f0 = N*55e6
vco_ss = ring_mA_ss(f0)*9/8*3.63
print(f"Worst power @ {f0/1e9:.2f} GHz ss/110/3.63V: VCO {vco_ss:.2f} mW, total on {vco_ss+other_tt_on*1.3:.2f}, off {vco_ss+other_tt_off*1.3:.2f}")
f0, L1, o = point(50e6); Ptyp = ring_mA_tt(f0)*9/8*3.3 + other_tt_on
print(f"FoM typ @1.6 GHz: {20*math.log10(o[('typ',True)][0]*1e-12)+10*math.log10(Ptyp):.1f} dB")
print(f"Ring supply @1.76 GHz ss/110/10fF ~ {1.637 - (1.928-1.76)/(1.928-1.711)*(1.637-1.629):.2f} V (interp, x1.5 near 1.63-1.64 V)")
