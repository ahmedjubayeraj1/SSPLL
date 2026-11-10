# pdk_char/ - measuring the PDK devices used in docs/sky130_cheatsheet.md

| File | What it measures |
|---|---|
| res.sp | xhigh_po and high_po resistance for all five legal widths at L = 10 and 20 um -> Ohm/um and head resistance |
| cap.sp | MIM (m3_1, m3_2) capacitance at 5/10/20/30 um sides -> area and perimeter density; nMOS gate capacitance vs bias |
| mos_bins.txt | legal L and W for each transistor type, read from the model bins |
| res_table.md | the resistor design table derived from res.sp |

Run: edit the `.lib` line to point at `$PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice`, then `ngspice -b res.sp` (needs the `.spiceinit` here).
