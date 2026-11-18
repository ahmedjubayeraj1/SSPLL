# Output divider ÷1 / ÷2 / ÷4 / ÷8 / ÷16 — plan and applications (18 Nov 2026)

With the VCO at 800 MHz (50 MHz × 16), a 3-bit select gives five outputs.

| Select | Output | Real applications |
|---|---|---|
| ÷1 | **800 MHz** | DDR3-1600 memory interface (800 MHz clock, data on both edges); MIPI D-PHY at 1.6 Gb/s per lane (the forwarded clock runs at half the bit rate, 800 MHz); half-rate clock for 1.6 Gb/s serialisers; sampling clock for fast ADCs/DACs |
| ÷2 | **400 MHz** | DDR2-800 / LPDDR at 400 MHz; MIPI D-PHY at 800 Mb/s per lane; core clock of high-end MCUs and DSPs |
| ÷4 | **200 MHz** | Octal-SPI / xSPI and HyperBus memories (up to 200 MHz); system bus and peripheral clocks; FPGA fabric clocks |
| ÷8 | **100 MHz** | The PCIe reference-clock frequency (compliance with a given PCIe generation must be checked against that standard's jitter filter); SoC bus clocks; SDRAM controllers |
| ÷16 | **50 MHz** | The RMII Ethernet reference clock (50 MHz); MCU peripheral clocks; and the **measurement output**: the standard SKY130 GPIO pad is specified for about 33 MHz output, so the slower outputs can leave the chip on a normal pad while 800 MHz needs a dedicated fast pad (Rule 21) |

**Why these and not others.** Powers of two come from a chain of ÷2 flip-flops: every output has a 50 % duty cycle,
the chain is simple, fast and testable, and it is the same structure the frequency-acquisition loop already needs
(÷16 = N). Odd ratios (÷3, ÷5, ÷6) need extra duty-cycle correction and are left as an option.

**Circuit (digital, 1.8 V devices on VCCD).**
- Level shifter 3.3 → 1.8 V from the VCO's buffered output (analog domain).
- Four true-single-phase-clock (TSPC) ÷2 stages: 800 → 400 → 200 → 100 → 50 MHz. The ÷16 tap also feeds the frequency
  loop's PFD, so the divider costs almost no extra hardware.
- A 5:1 glitch-free multiplexer (select retimed to the selected clock), 3 select bits from the slot's digital
  controls (Rule 7.4: 24 available), and an output driver to the pad or the slot boundary.
- Estimated power ~0.1–0.2 mW plus the pad driver; area ~20 × 30 µm.

**Verification added.** One testbench per ratio (frequency, duty cycle, added jitter by M17, switching between
ratios without glitches) at the corners; the full PLL spec is guaranteed at the 800 MHz VCO for every ratio, since the
divider only divides the same clock.
