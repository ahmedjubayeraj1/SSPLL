#!/usr/bin/env python3
"""darkmode.py - add a light/dark toggle to the exported notebook pages (learn/html, learn/html/v2).

    python3 learn/build/darkmode.py learn/html/*.html learn/html/v2/*.html     # post-process pages in place

export.py calls add_dark() on every page it writes, so a fresh export already has the toggle; this script also
upgrades pages that were exported before (it is idempotent: a page that already has the toggle is skipped).

What switches, and how
- Page colours: JupyterLab styles everything through CSS variables (--jp-layout-color0, --jp-content-font-color1, ...).
  jlab_dark_vars.css holds the variable values of nbconvert's own dark theme ("--HTMLExporter.theme=dark"), scoped to
  html.sspll-dark, so adding that one class to <html> turns the page dark with JupyterLab's real dark palette.
- Plotly figures: each figure uses the plotly_white template (colours come from the template, not from the figure).
  Dark mode swaps in plotly_dark (plotly_dark_template.json, taken from plotly.io) and back to the figure's own
  template for light mode; trace colours stay the same.
- PNG outputs: matplotlib figures have a white background, so in dark mode they are shown inverted with the hue
  rotated back (filter: invert + hue-rotate) - lines become light, colours keep their hue. The xschem schematic
  pictures already have a black background; a small script reads each image's corner pixel and inverts only the
  light ones.
- The v2 teacher boxes and the top bar carry inline light backgrounds; they get dark equivalents.
- Choice: the toggle in the top bar; stored in localStorage; with no stored choice the page follows the device setting.
"""
import os, sys, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
MARK = "/*sspll-dark*/"

HEAD = ("<script>" + MARK + "(function(){var t=null;try{t=localStorage.getItem('sspll-theme')}catch(e){}"
        "var d=t?t==='dark':!!(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches);"
        "if(d)document.documentElement.classList.add('sspll-dark')})();</script>")

CSS_COMMON = """
#sspll-theme{float:right;font:13px system-ui,sans-serif;padding:3px 10px;border-radius:14px;cursor:pointer;
  border:1px solid #cbd5e1;background:#fff;color:#0f172a}
html.sspll-dark #sspll-theme{background:#262626;color:#e5e7eb;border-color:#525252}
html.sspll-dark{color-scheme:dark}
html.sspll-dark a{color:#8ab4ff}
"""
CSS_NB = """
html.sspll-dark,html.sspll-dark body{background:var(--jp-layout-color0)}
html.sspll-dark [style*="background:#f8fafc"]{background:#1b1b1b!important;border-bottom-color:#3a3a3a!important;
  color:#e5e7eb}
html.sspll-dark [style*="background:#f4f8fd"]{background:#16233a!important}
html.sspll-dark [style*="border-left:4px solid #2a78d6"]{border-left-color:#5b9be8!important}
html.sspll-dark .jp-OutputArea-output img.sspll-inv{filter:invert(.92) hue-rotate(180deg)}
"""
CSS_INDEX = """
html.sspll-dark body{background:#111;color:#e5e7eb}
html.sspll-dark td,html.sspll-dark th{border-bottom-color:#333}
#sspll-theme{position:absolute;top:1rem;right:1rem;float:none}
"""

JS = """<script>%s(function(){
var DARK=%s;
function isDark(){return document.documentElement.classList.contains('sspll-dark')}
function plots(){if(!window.Plotly)return;document.querySelectorAll('.js-plotly-plot').forEach(function(gd){
  if(!gd.layout)return;
  if(gd._sspllLight===undefined)gd._sspllLight=JSON.parse(JSON.stringify(gd.layout.template||{}));
  var want=isDark()?'d':'l';
  if(gd._sspllMode===want||(gd._sspllMode===undefined&&want==='l'))return;
  gd._sspllMode=want;
  var L=Object.assign({},gd.layout);L.template=want==='d'?DARK:gd._sspllLight;
  Plotly.react(gd,gd.data,L);
})}
function marks(){document.querySelectorAll('.jp-OutputArea-output img').forEach(function(im){
  if(im._sspllChk)return;var go=function(){try{var c=document.createElement('canvas');c.width=c.height=8;
    var x=c.getContext('2d');x.drawImage(im,0,0,8,8);var d=x.getImageData(0,0,1,1).data;
    if(d[3]<16||d[0]+d[1]+d[2]>600)im.classList.add('sspll-inv');im._sspllChk=1}catch(e){}};
  if(im.complete&&im.naturalWidth)go();else im.addEventListener('load',go)})}
function apply(dark){
  marks();
  document.documentElement.classList.toggle('sspll-dark',dark);
  var b=document.body;
  if(b&&b.hasAttribute('data-jp-theme-light')){b.setAttribute('data-jp-theme-light',dark?'false':'true');
    b.setAttribute('data-jp-theme-name',dark?'JupyterLab Dark':'JupyterLab Light')}
  var k=document.getElementById('sspll-theme');
  if(k){k.textContent=dark?'\\u2600\\ufe0f Light':'\\ud83c\\udf19 Dark';k.setAttribute('aria-pressed',dark?'true':'false')}
  plots();
}
var k=document.getElementById('sspll-theme');
if(k)k.addEventListener('click',function(){var d=!isDark();try{localStorage.setItem('sspll-theme',d?'dark':'light')}catch(e){}apply(d)});
if(window.matchMedia){var mq=matchMedia('(prefers-color-scheme: dark)');var f=function(e){var t=null;
  try{t=localStorage.getItem('sspll-theme')}catch(x){}if(!t)apply(e.matches)};
  if(mq.addEventListener)mq.addEventListener('change',f);else if(mq.addListener)mq.addListener(f)}
apply(isDark());
window.addEventListener('load',function(){apply(isDark());setTimeout(function(){apply(isDark())},400)});
})();</script>"""

BUTTON = '<button id="sspll-theme" type="button" aria-label="Switch light or dark mode">\U0001F319 Dark</button>'


def add_dark(h):
    """Return page h with the light/dark toggle (unchanged if it already has one)."""
    if MARK in h:
        return h
    nb = "jp-Notebook" in h
    vars_css = open(os.path.join(HERE, "jlab_dark_vars.css"), encoding="utf-8").read() if nb else ""
    dark = open(os.path.join(HERE, "plotly_dark_template.json"), encoding="utf-8").read() if nb else "null"
    css = "<style>" + MARK + vars_css + CSS_COMMON + (CSS_NB if nb else CSS_INDEX) + "</style>"
    h = re.sub(r"(<head[^>]*>)", lambda m: m.group(1) + HEAD, h, count=1)
    h = h.replace("</head>", css + "</head>", 1)
    if nb:   # the toggle goes into the sticky top bar that export.nav() puts right after <body>
        m = re.search(r'(<body[^>]*>\s*<div style="position:sticky[^>]*>)', h)
        assert m, "top bar not found"
        h = h[:m.end()] + BUTTON + h[m.end():]
    else:
        h = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + BUTTON, h, count=1)
    i = h.rfind("</body>")
    return h[:i] + JS % (MARK, dark) + h[i:]


if __name__ == "__main__":
    for p in sys.argv[1:]:
        h = open(p, encoding="utf-8").read()
        h2 = add_dark(h)
        if h2 != h:
            open(p, "w", encoding="utf-8").write(h2)
        print(("added  " if h2 != h else "skipped") + " " + p)
