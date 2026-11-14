#!/usr/bin/env python3
"""build_log.py - writes design/SSPLL_design_log.xlsx and docs/methods.md from log_data.py.
Run:  python3 design/log/build_log.py   (then, for cached formula values: python3 <xlsx skill>/scripts/recalc.py file)"""
import os, sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.formatting.rule import FormulaRule
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import log_data as D

F = "Arial"; HDR = PatternFill("solid", fgColor="1F3864"); HFONT = Font(name=F, bold=True, color="FFFFFF", size=10)
BODY = Font(name=F, size=10); INPUT = Font(name=F, size=10, color="0000FF"); WRAP = Alignment(wrap_text=True, vertical="top")
thin = Side(style="thin", color="D0D5DD"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)


def sheet(wb, name, headers, rows, widths, inputs=()):
    ws = wb.create_sheet(name)
    ws.append(headers)
    for r in rows:
        ws.append(list(r))
    for c, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(1, c).column_letter].width = w
    for cell in ws[1]:
        cell.font = HFONT; cell.fill = HDR; cell.alignment = Alignment(wrap_text=True, vertical="center"); cell.border = BOX
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = INPUT if cell.column in inputs else BODY; cell.alignment = WRAP; cell.border = BOX
    ws.freeze_panes = "A2"
    return ws


wb = Workbook(); wb.remove(wb.active)
# README
ws = wb.create_sheet("README")
info = [("SSPLL + FFNC design log (Chipalooza #4, SKY130A)", None),
        ("Generated from design/log/log_data.py by design/log/build_log.py - edit the Python data, then rebuild.", None),
        ("Sheets", None),
        ("Steps", "roadmap steps done so far, status, deliverable file, key result"),
        ("Methods", "every measurement / analysis method: what it gives, why this method, how it works, how to run it, limits"),
        ("Devices", "every sized device with its PDK legal range; the Check column is a formula (OK / VIOLATION)"),
        ("PDK limits", "legal ranges per device model (from the frozen PDK model bins and pcell / DRC rules)"),
        ("Problems", "potential and real design problems: symptom, cause, solution, status"),
        ("Results", "key numbers vs spec/target; Margin and Pass are formulas"),
        ("Colours", "blue text = values copied from simulation or the spec (inputs); black = formulas")]
for r, (a, b) in enumerate(info, 1):
    ws.cell(r, 1, a).font = Font(name=F, bold=(r in (1, 3)), size=12 if r == 1 else 10)
    if b:
        ws.cell(r, 2, b).font = BODY
ws.column_dimensions["A"].width = 22; ws.column_dimensions["B"].width = 110

sheet(wb, "Steps", ["Step", "Title", "Status", "Deliverable", "Key result"], [tuple(map(str, s)) for s in D.STEPS],
      [8, 42, 22, 34, 80])
sheet(wb, "Methods", ["ID", "Method", "Used in step", "What it gives", "Why this method", "How it works", "How to run it",
                      "Limits / accuracy"], D.METHODS, [5, 26, 9, 34, 44, 60, 38, 34])

# PDK limits
lim = sheet(wb, "PDK limits", ["Model", "L min (um)", "L max (um)", "W min per finger (um)", "W max per finger (um)", "Note"],
            D.LIMITS, [22, 11, 11, 14, 14, 30], inputs=(2, 3, 4, 5))
nl = len(D.LIMITS) + 1
# Devices with formula checks against the limits sheet
dv = sheet(wb, "Devices", ["Block", "Instance", "Model", "W per finger (um)", "nf", "L (um)", "Role", "Check"],
           [r + ("",) for r in D.DEVICES], [14, 14, 20, 12, 6, 10, 38, 12], inputs=(4, 5, 6))
for i in range(2, len(D.DEVICES) + 2):
    m = f"MATCH(C{i},'PDK limits'!$A$2:$A${nl},0)"
    g = lambda col: f"INDEX('PDK limits'!${col}$2:${col}${nl},{m})"
    dv[f"H{i}"] = (f'=IFERROR(IF(AND(F{i}>={g("B")},F{i}<={g("C")},D{i}>={g("D")},D{i}<={g("E")}),"OK","VIOLATION"),'
                   f'"model not in limits")')
red = PatternFill("solid", fgColor="F8CBAD"); green = PatternFill("solid", fgColor="C6EFCE")
dv.conditional_formatting.add(f"H2:H{len(D.DEVICES) + 1}", FormulaRule(formula=['H2="OK"'], fill=green))
dv.conditional_formatting.add(f"H2:H{len(D.DEVICES) + 1}", FormulaRule(formula=['H2<>"OK"'], fill=red))

sheet(wb, "Problems", ["Step", "Area", "Problem", "How it shows up", "Cause", "Solution", "Status"],
      [tuple(map(str, p[:2])) + p[2:] for p in D.PROBLEMS], [7, 16, 40, 36, 36, 52, 14])

rs = sheet(wb, "Results", ["Parameter", "Value", "Spec / target", "Unit", "Type (max/min)", "Step", "Note", "Margin", "Pass"],
           [r[:6] + (r[6],) for r in D.RESULTS], [40, 10, 12, 9, 12, 6, 36, 10, 8], inputs=(2, 3))
for i in range(2, len(D.RESULTS) + 2):
    rs[f"H{i}"] = f'=IF(E{i}="max",C{i}-B{i},B{i}-C{i})'
    rs[f"H{i}"].number_format = "0.00;-0.00;0"
    rs[f"I{i}"] = f'=IF(H{i}>=0,"PASS","FAIL")'
rs.conditional_formatting.add(f"I2:I{len(D.RESULTS) + 1}", FormulaRule(formula=['I2="PASS"'], fill=green))
rs.conditional_formatting.add(f"I2:I{len(D.RESULTS) + 1}", FormulaRule(formula=['I2="FAIL"'], fill=red))

out = os.path.join(ROOT, "design", "SSPLL_design_log.xlsx")
wb.save(out)

# methods.md (same content, readable on GitHub)
md = ["# Measurement and analysis methods", "",
      "Generated from `design/log/log_data.py` (also in `design/SSPLL_design_log.xlsx`, sheet Methods). For every "
      "method: what it gives, why this method was chosen, how it works, how to run it yourself, and its limits.", ""]
for m in D.METHODS:
    md += [f"## {m[0]}. {m[1]} (step {m[2]})", "", f"**What it gives.** {m[3]}", "", f"**Why this method.** {m[4]}", "",
           f"**How it works.** {m[5]}", "", f"**How to run it.** `{m[6]}`", "", f"**Limits.** {m[7] or '-'}", ""]
open(os.path.join(ROOT, "docs", "methods.md"), "w").write("\n".join(md))
print("->", out, "and docs/methods.md")
