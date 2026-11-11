# Measurement without an own lab (11 Nov 2026)

## What the rules ask
- Rule 6.5: an outline of a measurement-based test plan (main proposal document).
- Rule 6.6: a list of **available** test equipment, sent separately. Access to a facility counts; ownership is not required.
- Rule 26: the second half of the award ($750) is paid on measurement, characterization and published results.
- Timeline: tapeout 19 May 2027; measurement starts when packaged parts and a board are available, months later.

## What each spec needs

| Measurement | Instrument | Requirement | Cost class |
|---|---|---|---|
| Lock, frequency range, divider ratios | Oscilloscope or frequency counter | CLK_OUT <= 110 MHz (/16) | low |
| Lock time (+/-10 ps) | Oscilloscope, 2 channels, REF_IN and CLK_OUT /32 | >= 500 MHz bandwidth, single-shot capture | medium |
| Reference 45-55 MHz | Low-noise crystal oscillators on the board (48, 50, 52 MHz) or a generator | Floor <= -150 dBc/Hz, or the reference dominates in-band noise | low (oscillators) |
| Phase noise, RMS jitter, FFNC on/off | Phase-noise analyzer, or spectrum analyzer with a phase-noise option | 100 MHz carrier (/16); floor below -150 dBc/Hz at 300 kHz-40 MHz offsets (spec -120 dBc/Hz at 1.6 GHz reads -144 at /16) | **high - the one you must borrow** |
| Reference spurs | Spectrum analyzer | -55 dBc at 1.6 GHz reads -79 dBc at /16 | medium-high |
| Power | 2-3 bench supplies + DMM or SMU | uA resolution on 1.8 V and 3.3 V | low |
| Digital control | Microcontroller board driving the Rule 7.4 inputs | 24 static inputs, 12 status outputs | low |

## Plan
1. **Do the cheap tests yourself.** Design the test board so lock, frequency, power and control need only a
   microcontroller, supplies, a DMM and a modest scope (bought, borrowed or shared).
2. **Borrow only the phase-noise instrument, for 1-2 days.** Arrive with the board debugged and scripts ready:
   a short, well-prepared visit is easier to get approved.
3. **Where to ask** (confirm before 23 Nov if possible, an email is enough):
   - an EEE department RF/microwave lab (current or former university, or a professor you know);
   - a semiconductor or telecom company lab (local design centres often own phase-noise analyzers);
   - an instrument distributor's demo/application lab, or short-term rental;
   - a collaborator abroad who measures your board (you ship it and the scripts);
   - the organizers: ask whether the program offers measurement support or a common test board
     (added to the open-question list).
4. **In the Rule 6.6 attachment** name the facility and the instruments with model numbers once confirmed; if not
   yet confirmed, name who you are arranging access with and the fallback.

## Design choices that lower the equipment bar (already in the proposal)
- /16, /32, /64 on CLK_OUT: carriers <= 110 MHz are easy for any analyzer and for the board.
- FFNC on/off switch: the jitter *reduction* is a relative measurement on the same chip and instrument, so it holds
  even when the absolute floor of the instrument is marginal.
- VTEST analog mux and status bits: debug without probing the die.
