"""gam.py - effective thermal-noise gamma and flicker of the sky130 1.8 V devices in the pinned models.
S_id(f) from ngspice .noise at three frequencies; thermal floor = S(10 GHz) corrected for 1/f; gamma = S_th/(4kT gm)."""
import subprocess, re, numpy as np
kT4 = 4*1.380649e-23*300.15
def run(dev, vgs, vds, w):
    if dev == 'n':
        ckt = f"vg g 0 dc {vgs} ac 1\nvd d 0 {vds}\nxm d g 0 0 sky130_fd_pr__nfet_01v8 w={w} l=0.15 nf=1 ad={w*.29} as={w*.29} pd={2*w+.58} ps={2*w+.58}\nh1 o 0 vd 1\n"
        m = "@m.xm.msky130_fd_pr__nfet_01v8"
    else:
        ckt = f"vs s 0 1.8\nvg g 0 dc {1.8-vgs} ac 1\nvd d 0 {1.8-vds}\nxm d g s s sky130_fd_pr__pfet_01v8 w={w} l=0.15 nf=1 ad={w*.29} as={w*.29} pd={2*w+.58} ps={2*w+.58}\nh1 o 0 vd 1\n"
        m = "@m.xm.msky130_fd_pr__pfet_01v8"
    net = f"""* gamma
.lib /home/claude/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.temp 27
{ckt}.control
save all {m}[gm] {m}[gds]
op
print {m}[gm] {m}[gds]
option sparse
noise v(o) vg dec 1 1meg 100g
setplot noise1
print onoise_spectrum
.endc
.end
"""
    open("g.sp", "w").write(net)
    out = subprocess.run(["ngspice", "-b", "g.sp"], capture_output=True, text=True).stdout
    gm = float(re.search(r"\[gm\] = (\S+)", out).group(1)); gds = float(re.search(r"\[gds\] = (\S+)", out).group(1))
    sp = [(float(a), float(b)) for a, b in re.findall(r"^\d+\s+(\S+)\s+(\S+)", out, re.M)]
    f = np.array([x[0] for x in sp]); S = np.array([x[1] for x in sp])**2
    # fit S = A + B/f over the 1 GHz..100 GHz points
    sel = f >= 1e9
    X = np.c_[np.ones(sel.sum()), 1/f[sel]]
    A, B = np.linalg.lstsq(X, S[sel], rcond=None)[0]
    fc = B/A
    return gm, gds, A/(kT4*gm), fc, np.sqrt(S[f == 1e6][0])
for dev, w in (('n', 4), ('p', 8)):
    for vgs, vds in ((0.6, 0.9), (0.9, 0.9), (1.4, 0.9), (1.4, 1.4), (0.9, 0.2)):
        gm, gds, g, fc, s1 = run(dev, vgs, vds, w)
        print(f"{dev}fet W={w} |Vgs|={vgs} |Vds|={vds}: gm={gm*1e3:.3f} mS gds={gds*1e3:.3f} mS  gamma_eff={g:.2f}  "
              f"1/f corner ~{fc/1e6:.0f} MHz  S_id^0.5(1 MHz)={s1:.2e} A/rtHz")
