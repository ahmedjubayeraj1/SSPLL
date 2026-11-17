#!/usr/bin/env python3
"""make_dut.py - write the device-under-test netlists used by every testbench in tb/ (and by LVS).
They are generated from the same Python that the design scripts simulate, so the decks here always test the
current design. Run again after any design change:  python3 tb/make_dut.py"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in ("vco", "cco", "refbuf", "clkgen"):
    sys.path.insert(0, os.path.join(ROOT, "design", d))
import vco, cco, refbuf, clkgen
OUT = os.path.join(ROOT, "tb", "dut")
os.makedirs(OUT, exist_ok=True)


def vco_sim():
    """Hierarchical VCO as drawn (sspll_vco -> core -> dcell, acbuf with PDK MIM/poly), plus a parasitic capacitor
    of {cpar} on each ring output (layout estimate, set with .param cpar=10f in the testbench)."""
    c = vco.lvs_reference(vco.FINAL)
    c = c.replace(".subckt sspll_vco_dcell inp inm outp outm vtune VDD VSS\n",
                  ".subckt sspll_vco_dcell inp inm outp outm vtune VDD VSS\ncpp outp VSS {cpar}\ncpm outm VSS {cpar}\n")
    return "* sspll_vco (step 74): ports VDD vtune VDDBUF VSS vop vom clkp clkm\n" + c


files = {"sspll_vco.spice": vco_sim(),
         "sspll_cco.spice": "* sspll_cco (step 75): ports VDDA VDDD VDDL VSS vring ibias vtest code0..code4 pll_en vtest_en\n"
                            + cco.full(cco.D),
         "sspll_refbuf.spice": "* sspll_refbuf (step 76): ports REF_IN refclk ib pll_en VDDA VDDL VDDD VSS\n"
                               + refbuf.full(),
         "sspll_clkgen.spice": "* sspll_clkgen (step 77): ports refclk cks cksb ckh ckhb ckg ckgb VDD VSS\n" + clkgen.cells()}
for n, txt in files.items():
    open(os.path.join(OUT, n), "w").write(txt)
    print("->", os.path.join("tb", "dut", n))
