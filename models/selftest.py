#!/usr/bin/env python3
"""selftest.py - checks that the Python setup works and that pllmodel reproduces the proposal numbers."""
import os, sys, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
for m in ("numpy", "scipy", "matplotlib"):
    mod = importlib.import_module(m); print(f"{m:11s} {mod.__version__}")
from pllmodel import TYP, PESS, TYP_10NOV, jitter
ok = True
for name, d, v, want in (("TYP sspll", TYP, "sspll", 2.29), ("TYP ffnc", TYP, "ffnc", 1.40),
                         ("10 Nov sspll", TYP_10NOV, "sspll", 2.40), ("10 Nov ffnc", TYP_10NOV, "ffnc", 1.56)):
    got = jitter(d, v)[0]["TOTAL"] * 1e12
    good = abs(got - want) < 0.01; ok &= good
    print(f"{name:13s} {got:.2f} ps (expect {want:.2f})  {'ok' if good else 'MISMATCH'}")
print("SELFTEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
