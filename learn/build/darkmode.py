#!/usr/bin/env python3
"""darkmode.py - reading themes for the exported notebook pages (learn/html, learn/html/v2): Light, Sepia, Dark.

    python3 learn/build/darkmode.py learn/html/*.html learn/html/v2/*.html     # post-process pages in place

export.py calls add_dark() on every page it writes, so a fresh export already has the theme button; this script also
upgrades pages exported before (an older theme injection is removed first, so it can be run again safely).

The button in the top bar cycles Light -> Sepia -> Dark. With no stored choice the page starts in Sepia (warm paper,
brown text: easy on the eyes) or, if the device is set to dark, in Dark (warm brown-black with cream text, not the
cold grey of JupyterLab's own dark theme). The choice is stored in localStorage.

How it works
- Page colours: JupyterLab styles everything through CSS variables (--jp-layout-color0, --jp-content-font-color1,
  --md-grey-100 ...). jlab_dark_vars.css holds nbconvert's own dark-theme values ("--HTMLExporter.theme=dark"),
  scoped to html.sspll-dark. On top of it both warm themes replace the grey ramp (--md-grey-50 ... 900), the page
  backgrounds and the text colours with a warm brown ramp, so every JupyterLab element follows.
- Plotly figures use the plotly_white template (colours come from the template, not from the figure). The theme swaps
  in a warm sepia or warm dark template (plotly_theme_templates.json, built from plotly_white / plotly_dark with the
  page's paper, text and grid colours) and back to the figure's own template for Light; trace colours stay the same.
- PNG outputs: light-background images (e.g. matplotlib) are shown inverted with the hue rotated back in Dark; the
  xschem schematic pictures already have a black background and are left alone (a script reads each corner pixel).
- The v2 teacher boxes and the top bar carry inline light backgrounds; they get warm equivalents.
"""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
MARK = "/*sspll-theme-2*/"
OLD = re.compile(r"<(script|style)>/\*sspll-(?:dark|theme-\d+)\*/.*?</\1>|<button id=\"sspll-theme\"[^>]*>.*?</button>", re.S)

HEAD = ("<script>" + MARK + "(function(){var t=null;try{t=localStorage.getItem('sspll-theme')}catch(e){}"
        "if(t!=='light'&&t!=='sepia'&&t!=='dark')t=(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches)"
        "?'dark':'sepia';if(t!=='light')document.documentElement.classList.add('sspll-'+t)})();</script>")

# warm ramps that replace JupyterLab's grey ramp (50 ... 900)
SEPIA = dict(zip((50, 100, 200, 300, 400, 500, 600, 700, 800, 900),
                 ("#fbf5e6", "#efe4cc", "#e6d8ba", "#dac8a4", "#c7b08a", "#a68f6a", "#887253", "#6a5740", "#4d3e2d", "#33291d")))
WDARK = dict(zip((50, 100, 200, 300, 400, 500, 600, 700, 800, 900),
                 ("#f6ecd9", "#eadcc2", "#d9c6a3", "#c4ad87", "#a08a68", "#7e6a50", "#5f4f3b", "#45392b", "#33291f", "#271f17")))


def ramp(r):
    return "".join(f"--md-grey-{k}:{v};" for k, v in r.items())


CSS_COMMON = """
#sspll-theme{float:right;font:13px system-ui,sans-serif;padding:3px 10px;border-radius:14px;cursor:pointer;
  border:1px solid #cbd5e1;background:#fff;color:#0f172a}
html.sspll-sepia #sspll-theme{background:#f6eedb;color:#3b2a19;border-color:#c7b08a}
html.sspll-dark #sspll-theme{background:#2a2119;color:#eadcc2;border-color:#5a4936}
html.sspll-dark{color-scheme:dark}
html.sspll-sepia a{color:#9a4a12}
html.sspll-dark a{color:#e3ad72}
"""
CSS_NB = ("""
html.sspll-sepia{""" + ramp(SEPIA) + """
  --jp-layout-color0:#f6eedb;--jp-layout-color1:#f6eedb;
  --jp-ui-font-color0:rgba(59,42,25,1);--jp-ui-font-color1:rgba(59,42,25,.92);--jp-ui-font-color2:rgba(59,42,25,.62);
  --jp-ui-font-color3:rgba(59,42,25,.45);--jp-content-font-color0:rgba(59,42,25,1);--jp-content-font-color1:rgba(59,42,25,.95);
  --jp-content-font-color2:rgba(59,42,25,.65);--jp-content-font-color3:rgba(59,42,25,.45);
  --jp-rendermime-table-row-hover-background:#eadbb9;--jp-mirror-editor-variable-color:#3b2a19}
html.sspll-dark{""" + ramp(WDARK) + """
  --jp-layout-color0:#1e1712;--jp-layout-color1:#271f17;--jp-cell-editor-background:#271f17;
  --jp-ui-font-color0:rgba(240,228,206,1);--jp-ui-font-color1:rgba(240,228,206,.9);--jp-ui-font-color2:rgba(240,228,206,.6);
  --jp-ui-font-color3:rgba(240,228,206,.42);--jp-content-font-color0:rgba(240,228,206,1);--jp-content-font-color1:rgba(234,220,194,1);
  --jp-content-font-color2:rgba(234,220,194,.72);--jp-content-font-color3:rgba(234,220,194,.5);
  --jp-rendermime-table-row-background:#271f17;--jp-rendermime-table-row-hover-background:#3a2e22}
html.sspll-sepia,html.sspll-sepia body,html.sspll-dark,html.sspll-dark body{background:var(--jp-layout-color0)}
html.sspll-sepia [style*="background:#f8fafc"]{background:#ecdfc3!important;border-bottom-color:#d3bf98!important;color:#3b2a19}
html.sspll-sepia [style*="background:#f4f8fd"]{background:#efe3c6!important}
html.sspll-sepia [style*="border-left:4px solid #2a78d6"]{border-left-color:#b0703a!important}
html.sspll-dark [style*="background:#f8fafc"]{background:#241c15!important;border-bottom-color:#45392b!important;color:#eadcc2}
html.sspll-dark [style*="background:#f4f8fd"]{background:#2c2219!important}
html.sspll-dark [style*="border-left:4px solid #2a78d6"]{border-left-color:#d29a5c!important}
html.sspll-dark .jp-OutputArea-output img.sspll-inv{filter:invert(.9) hue-rotate(180deg) sepia(.25)}
html.sspll-sepia .jp-OutputArea-output img.sspll-inv{filter:sepia(.25)}
""")
CSS_INDEX = """
html.sspll-sepia body{background:#f6eedb;color:#3b2a19}
html.sspll-sepia td,html.sspll-sepia th{border-bottom-color:#dac8a4}
html.sspll-dark body{background:#1e1712;color:#eadcc2}
html.sspll-dark td,html.sspll-dark th{border-bottom-color:#45392b}
#sspll-theme{position:absolute;top:1rem;right:1rem;float:none}
"""

JS = """<script>%s(function(){
var T=%s,ORDER=['light','sepia','dark'],LABEL={light:'\\u2600\\ufe0f Light',sepia:'\\ud83d\\udcdc Sepia',dark:'\\ud83c\\udf19 Dark'};
var R=document.documentElement;
function cur(){return R.classList.contains('sspll-dark')?'dark':R.classList.contains('sspll-sepia')?'sepia':'light'}
function marks(){document.querySelectorAll('.jp-OutputArea-output img').forEach(function(im){
  if(im._sspllChk)return;var go=function(){try{var c=document.createElement('canvas');c.width=c.height=8;
    var x=c.getContext('2d');x.drawImage(im,0,0,8,8);var d=x.getImageData(0,0,1,1).data;
    if(d[3]<16||d[0]+d[1]+d[2]>600)im.classList.add('sspll-inv');im._sspllChk=1}catch(e){}};
  if(im.complete&&im.naturalWidth)go();else im.addEventListener('load',go)})}
function plots(){if(!window.Plotly||!T)return;var want=cur();
  document.querySelectorAll('.js-plotly-plot').forEach(function(gd){
    if(!gd.layout)return;
    if(gd._sspllLight===undefined)gd._sspllLight=JSON.parse(JSON.stringify(gd.layout.template||{}));
    if(gd._sspllMode===want||(gd._sspllMode===undefined&&want==='light'))return;
    gd._sspllMode=want;
    var L=Object.assign({},gd.layout);L.template=want==='light'?gd._sspllLight:T[want];
    Plotly.react(gd,gd.data,L);
  })}
function apply(t){
  R.classList.remove('sspll-sepia','sspll-dark');if(t!=='light')R.classList.add('sspll-'+t);
  var b=document.body;
  if(b&&b.hasAttribute('data-jp-theme-light')){b.setAttribute('data-jp-theme-light',t==='dark'?'false':'true');
    b.setAttribute('data-jp-theme-name',t==='dark'?'JupyterLab Dark':'JupyterLab Light')}
  var k=document.getElementById('sspll-theme');
  if(k){k.textContent=LABEL[t];k.title='Theme: '+t+' (tap for the next one)'}
  marks();plots();
}
var k=document.getElementById('sspll-theme');
if(k)k.addEventListener('click',function(){var t=ORDER[(ORDER.indexOf(cur())+1)%%3];
  try{localStorage.setItem('sspll-theme',t)}catch(e){}apply(t)});
if(window.matchMedia){var mq=matchMedia('(prefers-color-scheme: dark)');var f=function(e){var t=null;
  try{t=localStorage.getItem('sspll-theme')}catch(x){}if(!t)apply(e.matches?'dark':'sepia')};
  if(mq.addEventListener)mq.addEventListener('change',f);else if(mq.addListener)mq.addListener(f)}
apply(cur());
window.addEventListener('load',function(){apply(cur());setTimeout(function(){apply(cur())},400)});
})();</script>"""

BUTTON = '<button id="sspll-theme" type="button" aria-label="Change the reading theme">\U0001F4DC Sepia</button>'


def add_dark(h):
    """Return page h with the Light / Sepia / Dark theme button (an older injection is replaced)."""
    if MARK in h:
        return h
    h = OLD.sub("", h)
    nb = "jp-Notebook" in h
    vars_css = open(os.path.join(HERE, "jlab_dark_vars.css"), encoding="utf-8").read() if nb else ""
    tpl = open(os.path.join(HERE, "plotly_theme_templates.json"), encoding="utf-8").read() if nb else "null"
    css = "<style>" + MARK + vars_css + CSS_COMMON + (CSS_NB if nb else CSS_INDEX) + "</style>"
    h = re.sub(r"(<head[^>]*>)", lambda m: m.group(1) + HEAD, h, count=1)
    h = h.replace("</head>", css + "</head>", 1)
    if nb:   # the button goes into the sticky top bar that export.nav() puts right after <body>
        m = re.search(r'(<body[^>]*>\s*<div style="position:sticky[^>]*>)', h)
        assert m, "top bar not found"
        h = h[:m.end()] + BUTTON + h[m.end():]
    else:
        h = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + BUTTON, h, count=1)
    i = h.rfind("</body>")
    return h[:i] + JS % (MARK, tpl) + h[i:]


if __name__ == "__main__":
    for p in sys.argv[1:]:
        h = open(p, encoding="utf-8").read()
        h2 = add_dark(h)
        if h2 != h:
            open(p, "w", encoding="utf-8").write(h2)
        print(("updated" if h2 != h else "skipped") + " " + p)
