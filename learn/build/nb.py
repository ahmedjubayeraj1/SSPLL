"""nb.py - tiny notebook builder for the learning notebooks (keeps the content reviewable as Python source)."""
import os, re, sys, nbformat as nbf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from www import WWW

SETUP = """# setup - run this cell first (Shift+Enter). Figures are interactive: drag the slider under each plot,
# hover for values, drag to zoom, double-click to reset.
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sspll_learn as sl
from sspll_learn import P, show, sweep, bode, kT
np.set_printoptions(precision=4, suppress=True)
print("ready - proposal design point:", f"{P['fref']/1e6:.0f} MHz x {P['N']} = {P['f0']/1e9:.2f} GHz")"""

HOWTO = """**How to use this notebook.** Every step follows the same loop: **What happens** (the observation) →
**How it happens** (the mechanism and the equations, in Razavi's notation) → **Why it happens** (the physical
reason) → an interactive figure → **Try it** (what to change and what to look for) → **Interview questions**
(click a question to open the answer; try to answer it aloud first).

Notation (Razavi, *RF Microelectronics* ch. 9 and *Design of CMOS PLLs*): $\\phi_{in}$, $\\phi_{out}$ input and output
phase; $\\omega_{out} = \\omega_0 + K_{VCO} V_{cont}$; $K_{PD}$ phase-detector gain; $I_p$ charge-pump current;
$R_1, C_1, C_2$ loop filter; $N$ divide ratio; $\\omega_n$, $\\zeta$ natural frequency and damping;
$H(s) = \\Phi_{out}/\\Phi_{in}$. Frequencies $f$ in Hz, angular $\\omega = 2\\pi f$ in rad/s.
Design numbers are the submitted proposal's: $f_{REF} = 50$ MHz, $N = 32$, $f_{out} = 1.6$ GHz, $f_c \\approx 2.5$ MHz."""


class Book:
    def __init__(self, title, intro):
        self.cells = [nbf.v4.new_markdown_cell(f"# {title}\n\n{intro}\n\n{HOWTO}"),
                      None,  # table of contents, filled at save
                      nbf.v4.new_code_cell(SETUP)]
        self.toc = []
        self.nq = 0

    def step(self, n, title, roadmap=""):
        anchor = f"step-{n}"
        self.toc.append((n, title, anchor))
        extra = f"\n\n*Roadmap step {n}: {roadmap}*" if roadmap else ""
        self.cells.append(nbf.v4.new_markdown_cell(f"<a id='{anchor}'></a>\n## Step {n} — {title}{extra}"))
        if n in WWW:
            w, h, y = WWW[n]
            self.cells.append(nbf.v4.new_markdown_cell(
                f"### What happens\n{w}\n\n### How it happens\n{h}\n\n### Why it happens\n{y}"))
        from wwh_supplement import S
        if n in S:   # what/how/why parts this step does not already have under those headings
            order = ("What happens", "How it happens", "Why it happens")
            parts = [f"### {k}\n{S[n][k].strip()}" for k in order if k in S[n]]
            self.cells.append(nbf.v4.new_markdown_cell("\n\n".join(parts)))

    def md(self, text):
        self.cells.append(nbf.v4.new_markdown_cell(text.strip("\n")))

    def code(self, text):
        self.cells.append(nbf.v4.new_code_cell(text.strip("\n")))

    def qa(self, pairs, n=None):
        self.nq += len(pairs)
        items = []
        for i, (q, a) in enumerate(pairs, 1):
            items.append(f"<details><summary><b>Q{i}.</b> {q}</summary>\n\n{a.strip()}\n\n</details>")
        head = f"### Interview questions — step {n}" if n else "### Interview questions"
        self.cells.append(nbf.v4.new_markdown_cell(head + f" ({len(pairs)})\n\n" + "\n\n".join(items)))

    def save(self, path):
        toc = ["## Contents", ""] + [f"- [Step {n} — {t}](#{a})" for n, t, a in self.toc]
        toc += ["", f"*{len(self.toc)} steps, {self.nq} interview questions.*"]
        self.cells[1] = nbf.v4.new_markdown_cell("\n".join(toc))
        nb = nbf.v4.new_notebook(); nb["cells"] = self.cells
        nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        nbf.write(nb, path)
        print(f"-> {path}: {len(self.toc)} steps, {self.nq} questions, {len(self.cells)} cells")
