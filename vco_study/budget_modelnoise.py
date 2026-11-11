"""Re-run the proposal jitter budget with the ring phase noise from isf2.py (model thermal + flicker, tt 27 C).
Ring noise at 5 fF scaled to the 10 fF power basis (-0.85 dB); CCO/supply allowance +1 dB typ, pessimistic +4 dB and 2x 1/f^3 corner."""
src = open("../proposal/jitter_budget.py").read().split("# scenarios:")[0]
ns = {}; exec(src, ns)
import numpy as np
ns['fref'], ns['N'], ns['f0'] = 50e6, 32, 1.6e9
base = dict(fc=2.5e6, ref=-152, ref_fc1=30e3, pd=-130, ncb=-150, ncb_fc1=1e6, gerr=0.10)
pessb = dict(base, ref=-148, ref_fc1=100e3, pd=-125, ncb=-146, ncb_fc1=3e6, gerr=0.30)
cases = {
 "proposal typ (assumed)":        dict(base, vco1M=-95.6, fc3=200e3),
 "proposal pess (assumed)":       dict(pessb, vco1M=-91.6, fc3=500e3),
 "model-noise typ":               dict(base, vco1M=-97.5-0.85+1, fc3=1.10e6),
 "model-noise pess":              dict(pessb, vco1M=-97.5-0.85+4, fc3=2.2e6),
}
i3 = np.argmin(abs(ns['f']-300e3))
for n, p in cases.items():
    a, La = ns['jitter'](p, False); b, Lb = ns['jitter'](p, True)
    print(f"{n:26s} vco1M {p['vco1M']:6.1f} fc3 {p['fc3']/1e6:4.2f} MHz | jitter off {a['TOTAL']*1e12:4.2f} ps on {b['TOTAL']*1e12:4.2f} ps "
          f"(-{100*(1-b['TOTAL']/a['TOTAL']):.0f}%) | L300k off {La[i3]:6.1f} on {Lb[i3]:6.1f}")
for fc in (2.0e6, 3.0e6, 4.0e6):
    p = dict(cases["model-noise typ"], fc=fc); a = ns['jitter'](p, False)[0]['TOTAL']; b = ns['jitter'](p, True)[0]['TOTAL']
    print(f"   loop bandwidth {fc/1e6:.1f} MHz, model-noise typ: off {a*1e12:.2f} ps, on {b*1e12:.2f} ps")
