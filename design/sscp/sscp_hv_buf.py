#!/usr/bin/env python3
"""sscp_hv_buf.py - resizing of the dump buffer after the first Gm run (ss 110 C, VDDA 2.97 V, V_cont 2.3 V:
vdump 92 mV below vctl, no tracking). The input-range limit of an nMOS-input OTA with a pMOS mirror load in unity gain is
    V_in,max = VDDA - V_SG(l1) + V_TN
so the mirror's V_SG must fall: a wider, shorter pMOS at the same current. Each variant is checked at the corners that
bound the V_cont window (1.3-2.3 V). -> data/sscp_hv_buf.json"""
import os, re, json
import numpy as np
from multiprocessing import Pool
import sscp_hv as C
HERE = os.path.dirname(os.path.abspath(__file__))
N5, P5 = C.N5, C.P5
VAR = {"BP4/2 (first)": dict(), "BP8/1": dict(BP=(P5, 8.0, 1, 1.0)), "BP12/1": dict(BP=(P5, 12.0, 1, 1.0)),
       "BP16/1": dict(BP=(P5, 16.0, 1, 1.0)), "BP12/1 BN8/1": dict(BP=(P5, 12.0, 1, 1.0), BN=(N5, 8.0, 1, 1.0))}
# round 2 (after round 1 showed a systematic error that grows linearly with |V_cont - 1.8 V|: the two input devices see
# different V_DS, so the finite output resistance gives an offset; longer channels raise the gain)
VAR2 = {"BP16/2 BN8/2": dict(BP=(P5, 16.0, 1, 2.0), BN=(N5, 8.0, 1, 2.0)),
        "BP24/2 BN8/2": dict(BP=(P5, 24.0, 1, 2.0), BN=(N5, 8.0, 1, 2.0)),
        "BP24/2 BN12/3": dict(BP=(P5, 24.0, 1, 2.0), BN=(N5, 12.0, 1, 3.0)),
        "BP32/3 BN12/3": dict(BP=(P5, 32.0, 1, 3.0), BN=(N5, 12.0, 1, 3.0))}
PTS = [("ss", 110, 2.97, 2.3), ("ss", -40, 2.97, 2.3), ("ss_hh", 110, 2.97, 2.3), ("tt", 27, 3.3, 2.3), ("tt", 27, 3.3, 1.8),
       ("tt", 27, 3.3, 1.3), ("ff", 110, 3.63, 1.3), ("ff", -40, 3.63, 1.3), ("ff", -40, 3.63, 1.8), ("ss", 110, 2.97, 1.3)]


def one(a):
    tag, (c, t, va, vc) = a
    p = dict(C.D); p.update(VAR[tag])
    net = C.head(p, corner=c, temp=t, vdda=va, vc=vc).replace(f"vvc vctl 0 {vc}", f"vvc vctl 0 dc {vc} ac 1") + (
        f"vp v1p 0 {va*0.503}\nvm v1m 0 {va*0.503}\n.control\nop\nprint v(x1.vdump)\n"
        "ac dec 20 1e3 3e9\nwrdata a.txt mag(v(x1.vdump))\n.endc\n.end\n")
    out, d = C.run(net, ["a.txt"])
    vdump = float(re.search(r"v\(x1.vdump\) = (\S+)", out).group(1))
    z = d["a.txt"]; m = z[:, 1]
    f3 = float(z[np.argmax(m < 0.707), 0]) if np.any(m < 0.707) else float("nan")
    return dict(tag=tag, corner=c, temp=t, vdda=va, vc=vc, err=vdump - vc, peak_db=float(20*np.log10(m.max())), f3db=f3)


if __name__ == "__main__":
    import sys
    R2 = "--round2" in sys.argv
    if R2:
        VAR.update(VAR2)
    tags = list(VAR2) if R2 else list(VAR)
    jobs = [(tag, pt) for tag in tags for pt in PTS]
    with Pool(2) as pool:
        res = pool.map(one, jobs)
    for tag in tags:
        rr = [r for r in res if r["tag"] == tag]
        print(f"{tag:14s} worst |err| {max(abs(r['err']) for r in rr)*1e3:6.1f} mV, peaking {max(r['peak_db'] for r in rr):.2f} dB, "
              f"f3dB min {min(r['f3db'] for r in rr)/1e6:.0f} MHz", flush=True)
        for r in rr:
            print(f"    {r['corner']:5s} {r['temp']:4d} {r['vdda']} V vctl {r['vc']}: err {r['err']*1e3:7.2f} mV, "
                  f"peak {r['peak_db']:.2f} dB, f3dB {r['f3db']/1e6:.0f} MHz", flush=True)
    json.dump(dict(var={k: {kk: list(vv) if isinstance(vv, tuple) else vv for kk, vv in VAR[k].items()} for k in tags},
                   res=res), open(os.path.join(HERE, "data", "sscp_hv_buf2.json" if R2 else "sscp_hv_buf.json"), "w"), indent=1)
