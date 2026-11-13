#!/usr/bin/env python3
"""export.py - build, execute and export the learning notebooks to a small static web site (learn/html/).

    python3 learn/build/export.py            # all phases
    python3 learn/build/export.py 1 3        # only phase 1 and 3

The pages load plotly.js from a local copy (plotly.min.js next to the pages) and MathJax from cdnjs, so they work
offline in a browser (except equations) and as a hosted page. The .ipynb files in learn/ are saved with cleared
outputs; open them in Jupyter and run all cells to get the same interactive figures there."""
import os, re, sys, subprocess, shutil, glob, html
HERE = os.path.dirname(os.path.abspath(__file__)); LEARN = os.path.dirname(HERE); OUT = os.path.join(LEARN, "html")
PHASES = {1: ("phase1.py", "phase1_fundamentals", "PLL fundamentals (steps 11–24)"),
          2: ("phase2.py", "phase2_type1", "Type-I PLL, limits and fixes (steps 25–32)"),
          3: ("phase3.py", "phase3_type2_cppll", "Type-II charge-pump PLL (steps 33–45)"),
          4: ("phase4.py", "phase4_sspll", "Sub-sampling PLL (steps 46–58)"),
          5: ("phase5.py", "phase5_vcdl", "Voltage-controlled delay line / NCB (steps 59–64)"),
          6: ("phase6.py", "phase6_ffnc", "Feedforward noise cancellation (steps 65–71)")}
sel = [int(a) for a in sys.argv[1:]] or [p for p in PHASES if os.path.exists(os.path.join(HERE, PHASES[p][0]))]
os.makedirs(OUT, exist_ok=True)
import plotly
shutil.copy(os.path.join(os.path.dirname(plotly.__file__), "package_data", "plotly.min.js"), os.path.join(OUT, "plotly.min.js"))
MJ = ("<script>window.MathJax={tex:{inlineMath:[['$','$'],['\\\\(','\\\\)']],displayMath:[['$$','$$'],['\\\\[','\\\\]']],"
      "processEscapes:true},svg:{fontCache:'global'}};</script><script src=\"mathjax-tex-svg.js\"></script>")
MJSRC = "/tmp/package/es5/tex-svg.js"
if not os.path.exists(MJSRC):
    subprocess.run("cd /tmp && npm pack mathjax@3 >/dev/null 2>&1 && tar xzf mathjax-3*.tgz", shell=True, check=True)
shutil.copy(MJSRC, os.path.join(OUT, "mathjax-tex-svg.js"))
avail = [p for p in PHASES if os.path.exists(os.path.join(HERE, PHASES[p][0]))]


def nav(cur):
    links = ['<a href="index.html">Index</a>'] + [
        (f'<b>Phase {p}</b>' if p == cur else f'<a href="{PHASES[p][1]}.html">Phase {p}</a>') for p in avail]
    return ('<div style="position:sticky;top:0;z-index:9;background:#f8fafc;border-bottom:1px solid #e2e8f0;'
            'padding:8px 14px;font:14px system-ui,sans-serif">' + " · ".join(links) + "</div>")


for p in sel:
    script, stem, title = PHASES[p]
    subprocess.run([sys.executable, os.path.join(HERE, script)], check=True)
    nbp = os.path.join(LEARN, stem + ".ipynb")
    tmp = os.path.join("/tmp", stem + "_exec.ipynb")
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", nbp, "--output", tmp,
                    "--ExecutePreprocessor.timeout=1200"], check=True, cwd=LEARN, capture_output=True)
    subprocess.run(["jupyter", "nbconvert", "--to", "html", tmp, "--output", os.path.join(OUT, stem + ".html"),
                    "--HTMLExporter.theme=light"], check=True, capture_output=True)
    h = open(os.path.join(OUT, stem + ".html"), encoding="utf-8").read()
    h = re.sub(r'<script[^>]*require\.js[^>]*></script>', '', h)
    h = re.sub(r'<script charset="utf-8"[^>]*src="https://cdn\.plot\.ly/[^"]*"></script>',
               '<script src="plotly.min.js"></script>', h)
    h = re.sub(r'<!-- Load mathjax -->.*?<!-- End of mathjax configuration -->', lambda m: MJ, h, count=1, flags=re.S)
    h = re.sub(r"(<body[^>]*>)", r"\1" + nav(p), h, count=1)
    h = re.sub(r"<title>.*?</title>", f"<title>Phase {p} — {html.escape(title)}</title>", h, count=1, flags=re.S)
    open(os.path.join(OUT, stem + ".html"), "w", encoding="utf-8").write(h)
    nerr = h.count('class="ansi-red-fg"') + h.count("Traceback (most recent call last)")
    print(f"phase {p}: {os.path.getsize(os.path.join(OUT, stem + '.html'))/1e6:.1f} MB, errors in outputs: {nerr}")
    subprocess.run(["jupyter", "nbconvert", "--clear-output", "--inplace", nbp], check=True, capture_output=True)

rows = []
for p in avail:
    script, stem, title = PHASES[p]
    n_q = 0
    if os.path.exists(os.path.join(LEARN, stem + ".ipynb")):
        n_q = open(os.path.join(LEARN, stem + ".ipynb"), encoding="utf-8").read().count("<summary><b>Q")
    rows.append(f'<tr><td>Phase {p}</td><td><a href="{stem}.html">{html.escape(title)}</a></td><td>{n_q}</td></tr>')
idx = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SSPLL + FFNC learning notebooks</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;color:#0f172a}}
table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #e2e8f0;padding:.5rem;text-align:left}}
a{{color:#1d4ed8}}</style></head><body>
<h1>SSPLL + FFNC for SKY130 — learning notebooks</h1>
<p>Phases 1–6 of the Chipalooza #4 roadmap: the theory from first principles, with interactive figures (drag the slider
under a plot, hover for values, drag to zoom, double-click to reset) and interview questions for every step (tap a question
to open the answer). Design numbers follow the submitted proposal: 50 MHz × 32 = 1.6 GHz, f<sub>c</sub> ≈ 2.5 MHz, FFNC on/off.</p>
<table><tr><th></th><th>Notebook</th><th>Interview questions</th></tr>{''.join(rows)}</table>
<p>Source: <code>learn/</code> in github.com/ahmedjubayeraj1/SSPLL — run the same notebooks in Jupyter
(<code>./tools/setup_python.sh</code>, then open <code>learn/*.ipynb</code>).</p></body></html>"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(idx)
print("site ->", OUT)
