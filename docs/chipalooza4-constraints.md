# Chipalooza #4 — confirmed constraints (step 1 deliverable)

Revised 2026-11-10. Living version with full reasoning and sources:
https://claude.ai/artifact/SBCDWUv8wme5tZhRAVSPZQ

Source: https://opencircuitdesign.com/chipalooza/rules-4.html
Rule numbers below are the page's own numbering (27 numbered rules; Rules 6,
7 and 23 have sub-items). challenge-4.html is a stale stub showing 2027 —
ignore it.

## Rule map (for quick lookup)
| # | Subject |
|---|---|
| 1 | Official name; Sky130 process conformance |
| 2 | Start date, 9 Nov 2026 |
| 3 | 27 weeks to tapeout |
| 4 | Teams: 3 or fewer preferred, not required (ours: 2) |
| 5 | Proposals due 23 Nov 2026 |
| 6 | Proposal contents (6.1–6.7) |
| 7 | Useful SoC block incl. PLLs; available resources (7.1–7.6) |
| 8 | Challenge #1 designs at github.com/fossi-foundation/ |
| 9 | Target spec is the designer's, met post-layout; changes need approval |
| 10 | 1.8 V logic library, dual 1.8 V core / 3.3 V periphery pads |
| 11 | Up to 18 designs; ranking; slot sharing |
| 12 | Public git repository |
| 13 | Open-source verifiable; AI allowed in support only |
| 14 | All source files; unverifiable designs not awarded |
| 15 | Behavioral documentation in the repo |
| 16 | No data dumps; sign-off DRC/LVS required |
| 17 | Open-source licence, Apache 2.0 preferred |
| 18 | Repository template (Dorrer IHP template as interim) |
| 19 | PVT corners, commercial spec, 110 C max acceptable |
| 20 | Slot size TBD in harness repo; standalone + wrapper layouts; artwork |
| 21 | 1 to 3 dedicated pins; custom pads with approval |
| 22 | 4 shared analog lines, switches < 5 ohm |
| 23 | Review gates (23.1–23.4) |
| 24 | Slot assignments at the layout review at the latest |
| 25 | Not ready by final review -> may miss tapeout |
| 26 | $1500 award, half tapeout / half measurement |
| 27 | Changes announced at fossi-chat.org/#chipalooza |

## Schedule (Rules 2, 3, 5, 23, 24, 25) — our work ends 22 Feb 2027
| Date | Milestone |
|---|---|
| 9 Nov 2026 | Challenge launches |
| 9–23 Nov 2026 | Write proposals |
| 23 Nov 2026 | Proposals due |
| week of 23 Nov 2026 | Proposal review (23.1) |
| 23 Nov – 28 Dec 2026 | Schematic design & pre-layout verification |
| week of 28 Dec 2026 | Schematic design review (23.2) |
| 28 Dec 2026 – 1 Feb 2027 | Layout & post-layout verification |
| week of 1 Feb 2027 | Layout design review (23.3); SLOT ASSIGNMENTS (Rule 24) |
| 1–22 Feb 2027 | Slot integration |
| week of 22 Feb 2027 | Final design review (23.4) |
| 22 Feb – 19 May 2027 | Chip top-level integration (organizers) |
| 19 May 2027 | Chip Foundry tapeout |

13 weeks of design between the proposal deadline and the final review.
Rule 24: the layout review judges the STANDALONE block; the final review
judges the SLOT integration. Rule 25: not ready by the final review -> may
not reach tapeout.

## Rule 7 explicitly asks for PLLs
"The proposed IP block should be a block that is useful within the context of
a system-on-chip (SoC). This includes all of the IP blocks that were created
for the Efabless Chipalooza Challenge #1, as well as additional useful blocks
like PLLs, programmable filters, etc."
None of the 25 blocks taped out in Challenge #1 is a PLL. Strongest pitch.
Rule 8: Challenge #1 designs at https://github.com/fossi-foundation/
Naming convention: sky130_<designer initials>_ip__<block>

## Per-slot resources (Rule 7.1–7.6)
- 7.1 Supplies: 1.8 V digital, 3.3 V analog (per-slot pMOS power switch)
- 7.2 One bandgap-referenced bias voltage
- 7.3 Up to 2 bandgap-referenced current sources
- 7.4 Up to 24 digital controls in, 12 digital test signals out
- 7.5 Up to 4 shared analog signal lines (multiplexed by project)
- 7.6 Up to 3 dedicated pins, any digital or analog pad from the pad library
- Exceptions need approval.
Rule 21: slots have 1 to 3 dedicated pins; the default analog pads may be
replaced by any signal pad. Custom pads need approval, must match foundry pad
size/configuration, abut cleanly, and be independently verified.

## Rule 10 — voltage domains, NEW DESIGN WORK
Harness uses a 1.8 V logic library and the standard Sky130 dual 1.8 V core /
3.3 V periphery pad library. Analog designs operating at the periphery range
should be designed for 3.3 V. Designs running at 1.8 V on-chip that interface
to the padframe for testing MUST ensure overvoltage protection on inputs and
outputs. Our 1.8 V PLL core receives a reference pad and drives an output pad,
so that protection is ours to build and verify.

## Rule 20 — slot area STILL TBD
- "The slot size and I/O configuration (TBD) will be specified in the harness
  repository." No sky130 harness repo exists yet; expect sky130_ocd_chipalooza.
- FAQ estimate (IHP): 520 x 250 um on 6.6 mm2; 750 x 340 um on 10 mm2.
- DESIGN TARGET until confirmed: 520 x 250 um = 0.13 mm2.
- Two layouts: standalone (reusable) + slot wrapper. Do not expand to fill the
  slot. Extra slot area may be used for artwork if density rules pass.

## Resistances
- Per-slot power switch: 1.4 ohm on the IHP test tapeout; assume < 1 ohm.
- Rule 22: shared analog switches < 5 ohm, but each bus reaches all 18
  projects, so bus loading not switch resistance is the limit. The FAQ's
  220 ohm describes the 2024 Efabless sky130 test chips, NOT this harness.
  "should not be relied on for high-frequency analog signaling".

## Rule 9 — the specification is binding
"The target specification of the circuit is up to the designer ... The design
will need to meet the given specification in post-layout verification. Changes
to the target specification mid-design must be approved."
=> The 23 Nov numbers bind us for the rest of the challenge. Promise what
post-layout can hold, not the schematic best case.

## Verification and sign-off (Rules 13–19)
- Rule 19: PVT corners, commercial spec; 110 C max acceptable, wider preferred.
- Rule 13: must be verifiable with OPEN SOURCE tools. Commercial tools may be
  used for design, but a design that cannot be verified as meeting spec with
  open source tools is rejected. AI may be used in support of circuit design
  but must NOT be a requirement for the end user to use, verify or modify the
  block.
- Rule 14: all source files for all views must be in the repo; designs that
  cannot be independently verified will not be awarded.
  (ngspice has no production pnoise — our biggest risk.)
- Rule 15: full behavioral documentation in the repo, any reasonable format.
- Rule 16: sign-off DRC + LVS required; plots not raw dumps, but raw data must
  be reproducible from the sources on demand.
- Rule 12: public git repo. Rule 17: Apache 2.0 preferred.
- Rule 18: follow the repository template once published; Simon Dorrer's IHP
  template is the interim reference. IIC-OSIC-TOOLS workflow encouraged.

## Rule 26 — award
$1500 per project: half at tapeout, half at measurement, characterization and
published results.

## Rule 11 — chip
Up to 18 designs. More proposals may be accepted than fit; if oversubscribed,
designs are ranked. Slots may be shared (esp. where padframe pins are
underused), which complicates per-slot power measurement. We use all 3 pins,
so we should ask for a dedicated slot.

## Design consequences for the SSPLL
1. 2.359296 GHz cannot leave the chip. The FAQ discourages custom high-speed
   drivers and prefers an output divider. Add an on-chip /16 to 147.456 MHz.
   - Absolute RMS jitter in seconds is PRESERVED through an ideal divider:
     phi_out = phi_in/N and f_out = f_in/N, so sigma_t is unchanged.
   - Phase noise (dBc/Hz) and reference spurs (dBc) read 20*log10(N) low:
     +24 dB correction for /16. Must be stated in the test plan.
2. Rule 22: the 49.152 MHz reference needs a dedicated pad, not the shared mux.
3. Rule 7.6 / 21: the 3 dedicated pins are fully spent: REF in, divided clock
   out, and VDD_vco access for supply-noise injection / FFNC calibration.
   Control-voltage monitoring goes to a shared analog line via a buffer.
4. Rule 10: overvoltage protection on the reference input and divided output.
5. Rules 13–14: open-source jitter verification must be in the proposal — ISF
   for the VCO, trnoise + Python phase extraction for the loop, and a
   phase-domain model cross-checked against both.
6. Rule 4: team of 2 meets the 3-or-fewer preference.

## Proposal package, due 23 Nov (Rule 6)
Email to chipalooza@opencircuitdesign.com. Interest survey (separate):
forms.gle/bsKn8W44M9gQoc2R6
Main document (no personal/institutional details — it becomes public docs):
  6.1 Type of IP block
  6.2 List of I/O, including test ports
  6.3 Functional description
  6.4 Target specification: average, minimum, maximum, plus absolute limits
  6.5 Outline of a measurement-based test plan
Sent separately:
  6.6 List of available test equipment
  6.7 CVs of the designers

## Open questions for the organizers
1. Rule 20: sky130 harness repo publication date and slot footprint in um?
2. Rule 22: can we take < 5 ohm, and what is the bus capacitance with all 18
   projects attached?
3. (removed: team of 2 meets Rule 4)
4. Rule 10: recommended overvoltage-protection / level-shift arrangement, or
   an existing pad cell, for a 49 MHz input and ~147 MHz output from a 1.8 V
   core?
5. Should the measurement divider sit in our slot and draw our slot supply,
   and can it be gated separately so PLL core power can be reported alone?
6. Rule 11: is per-slot current measured through the power switch? Can we have
   a dedicated slot?
7. Rule 19: what temperature range will the sky130 parts be characterized over?
8. Rule 9: process and latest usable point for an approved mid-design spec
   change?
9. Rule 26 / 6.6: does the program offer any measurement support (shared lab, phase-noise analyzer access, common test
   board) for teams without their own RF lab?
