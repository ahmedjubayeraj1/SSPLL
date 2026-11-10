# Proposal evidence (Chipalooza #4, step 2)

Everything behind the numbers in the proposal doc
(https://claude.ai/artifact/KHovStHrgfVBviGQHPkxWL).

| File | What it is |
|---|---|
| jitter_budget.py | Phase-domain jitter model (loop + feedforward cancellation, Nagam & Kinget structure). `python3 jitter_budget.py` prints the scenario table and writes budget.csv |
| budget.csv | Model output: optimistic / typical / pessimistic, FFNC off and on |
| sim/ring5_tmpl.sp, sim/ring4_tmpl.sp | ngspice ring-VCO feasibility benches (5- and 4-stage), placeholders %CORNER% %TEMP% %IVCO% %VT% %CPAR% |
| sim/tspc_tmpl.sp | TSPC divide-by-2 speed check |
| sim/core_*.lib, sim/base_params.spice | Minimal sky130 core-device libraries built from google/skywater-pdk-libs-sky130_fd_pr (raw models; use with `.option scale=1e-6` and sim/.spiceinit) |
| sim/vco_feasibility_results.csv | Simulated ring frequency and supply voltage per corner, current and wiring load |

Key results: the 5-stage ring needs 1.84-2.01 V at ss/110 C for 2.36 GHz once
5-10 fF wiring per node is added (over the 1.8 V rating); the 4-stage ring needs
at most 1.73 V at 2.40 GHz. Typical jitter (10 kHz-40 MHz) 2.47 ps without
cancellation, 1.62 ps with it.

Note: the minimal libraries point at /home/claude/... paths; in the repo, switch
them to the open_pdks sky130A combined models ($PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice).
