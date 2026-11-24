#!/usr/bin/env python3
"""lvs_hv_all.py - writes the LVS reference netlists of the six 5 V blocks from the simulated netlists, then runs
xschem/lvs.sh on every drawn cell that has a matching .subckt in its block's reference (cell by cell, bottom up, so a
mismatch points at the cell that has it). Prints one line per cell: match / mismatch and the property-error line."""
import os, re, sys, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import ground_split_check as G

BLOCKS = dict(cco_hv="ref_cco_hv", clkgen_hv="ref_clkgen_hv", refbuf_hv="ref_refbuf_hv", sspd_hv="ref_sspd_hv",
              sscp_hv="ref_sscp_hv", vco_hv="ref_vco_hv")

if __name__ == "__main__":
    nets = G.netlists()
    xs = os.path.join(ROOT, "xschem")
    bad = 0
    for blk, ref in BLOCKS.items():
        open(os.path.join(xs, "netlist", ref + ".spice"), "w").write(nets[ref])
        subckts = re.findall(r"^\.subckt (\S+)", nets[ref], re.M)
        for cell in subckts:
            sch = os.path.join(blk, cell + ".sch")
            if not os.path.exists(os.path.join(xs, sch)):
                continue
            out = subprocess.run(["./lvs.sh", sch, f"netlist/{ref}.spice", cell], cwd=xs, capture_output=True,
                                 text=True).stdout.strip().split("\n")
            res = out[0] if out else "no result"
            prop = out[1] if len(out) > 1 else ""
            ok = "match" in res.lower() and "do not" not in res.lower() and ("no property" in prop.lower() or not prop)
            bad += not ok
            print(f"{blk:10s} {cell:24s} {res}  {prop}")
    print("all cells match" if bad == 0 else f"{bad} cell(s) need attention")
    sys.exit(1 if bad else 0)
