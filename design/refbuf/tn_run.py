"""Background: transient-noise jitter runs (method M15)."""
import refbuf as r, numpy as np, json, sys
from multiprocessing import Pool
f, S, fg, vi = r.input_noise()
Sw = float(np.interp(3e8, f, S)/abs(np.interp(3e8, fg, vi))**2)
def job(a):
    vpp, sw, n, seed = a
    te = r.tnoise(sw, vpp=vpp, ncyc=n, seed=seed)
    st = r.edge_stats(te); return dict(vpp=vpp, Sw=sw, n=st["n"], abs=st["abs"], per=st["per"], dev=st["dev"].tolist())
if __name__ == "__main__":
    jobs = [(1.0, Sw, 300, 1), (3.3, Sw, 300, 2), (0.4, Sw, 300, 3)]
    with Pool(2) as p:
        res = p.map(job, jobs)
    json.dump(dict(Sw=Sw, runs=res), open("data/step76_tnoise.json", "w"))
    for x in res: print(x["vpp"], x["Sw"] > 0, x["n"], "abs %.3g per %.3g" % (x["abs"], x["per"]))
