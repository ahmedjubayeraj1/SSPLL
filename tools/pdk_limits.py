#!/usr/bin/env python3
"""pdk_limits.py - legal size ranges of the SKY130 devices used in this design, and a checker.

Every schematic value must lie inside these ranges (project rule: never below the PDK minimum or above the maximum).
Sources: model bins of the frozen PDK (lmin/lmax/wmin/wmax per finger, sky130_fd_pr/spice), DRC rules and pcell limits
in docs/sky130_cheatsheet.md. The Cadence kit (sky130_release_0.0.4) pcells must be checked against the same table
when the cells are drawn in Virtuoso.

    from pdk_limits import check
    check("res_xhigh_po_2p85", l=15.5)            -> [] if legal, else a list of violations
    python3 tools/pdk_limits.py                    -> prints the table
"""
MOS = {  # device: (Lmin, Lmax, Wmin per finger, Wmax per finger) in um
    "nfet_01v8": (0.15, 100, 0.36, 100), "pfet_01v8": (0.15, 100, 0.42, 100),
    "nfet_01v8_lvt": (0.15, 100, 0.42, 100), "pfet_01v8_lvt": (0.35, 100, 0.42, 100),
    "pfet_01v8_hvt": (0.15, 100, 0.36, 100),
    "nfet_g5v0d10v5": (0.50, 100, 0.42, 100), "pfet_g5v0d10v5": (0.50, 100, 0.42, 100),
}
RES_W = (0.35, 0.69, 1.41, 2.85, 5.73)          # only legal poly-resistor widths (rpm.1b-f)
RES_LMIN = 0.50                                   # um, pcell minimum body length
RES_LFOLD = 100.0                                 # um, longer bodies are legal but must be folded (layout rule of thumb)
MIM = (2.0, 30.0)                                 # cap_mim_m3_1 / m3_2 side, um (pcell); larger caps are tiled


def check(device, w=None, l=None, nf=1):
    """Return a list of violations (empty = legal). w, l in um; for resistors give the type with width suffix."""
    v = []
    if device in MOS:
        lmin, lmax, wmin, wmax = MOS[device]
        if l is not None and not lmin <= l <= lmax: v.append(f"{device}: L = {l} um outside [{lmin}, {lmax}]")
        if w is not None:
            wf = w/nf
            if not wmin <= wf <= wmax: v.append(f"{device}: W/finger = {wf:.3f} um outside [{wmin}, {wmax}]")
    elif device.startswith(("res_xhigh_po", "res_high_po")):
        wid = float(device.split("_")[-1].replace("p", ".")) if device[-1].isdigit() else w
        if wid not in RES_W: v.append(f"{device}: width {wid} um not one of {RES_W}")
        if l is not None and l < RES_LMIN: v.append(f"{device}: L = {l} um below {RES_LMIN}")
        if l is not None and l > RES_LFOLD: v.append(f"{device}: L = {l} um > {RES_LFOLD} - legal, but fold it")
    elif device.startswith("cap_mim_m3"):
        for side in (w, l):
            if side is not None and not MIM[0] <= side <= MIM[1]:
                v.append(f"{device}: side {side} um outside [{MIM[0]}, {MIM[1]}] (tile it)")
    else:
        v.append(f"{device}: not in the limit table - add it before use")
    return v


if __name__ == "__main__":
    print("MOS (L min, L max, W/finger min, W/finger max, um):")
    for k, x in MOS.items():
        print(f"  {k:16s} {x}")
    print(f"poly resistors: widths {RES_W} um only, body L >= {RES_LMIN} um (fold above {RES_LFOLD} um)")
    print(f"MIM caps: each side {MIM[0]}-{MIM[1]} um")
