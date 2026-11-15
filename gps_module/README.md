# GPS module for the radiosonde (rev A)

A plug-in GNSS board that replaces the NEO-6M module on J6 of the radiosonde. It uses a u-blox MAX-M10S, which works up to 80 km altitude in its airborne modes.

**Status: generated design, not yet built or tested.** ERC and DRC pass with no errors. Check the points under "Before ordering" first.

## Mechanical

- Board: 27.56 x 26.42 mm, 2 layers, 1.6 mm.
- Pin row: 5 pins at 2.54 mm, 2.16 mm from the left edge (top view). The header is soldered on the bottom side with the pins pointing down into the radiosonde's J6 socket.
- Hole: 3 mm, at (24.77, 23.37) mm from the top-left corner.
- These match the `GPS_NEO6M_5pin` footprint in `../kicad/radiosonde.pretty`.

| Pin | Signal | Direction |
|---|---|---|
| 1 | PPS (time pulse) | module output, not connected on the radiosonde |
| 2 | TXD | module output, to radiosonde GPS_RX |
| 3 | RXD | module input, from radiosonde GPS_TX |
| 4 | GND | |
| 5 | VCC | 3.3 V in |

## Circuit

- **Receiver:** U1 MAX-M10S. V_BCKP is tied to VCC (no backup supply, so every power-on is a cold start). VIO_SEL is open for 3.3 V I/O.
- **Supply filter:** FB1 with C1 and C2, to keep the RA-02's transmit bursts on the 3.3 V rail out of the receiver.
- **Antenna choice:** fit R1 for the on-board patch or R2 for the u.FL connector, never both.
  - R1 is the 0603 next to the patch feed pin. R2 is the one next to the u.FL connector.
- **Active antenna bias:** fit L1 (27 nH, below R2) only when an active antenna is on the u.FL. R3 limits the current. Leave L1 out for a passive antenna, because some are a DC short.
- **Top side:** only the patch antenna. The top copper is its ground plane; the three signal tracks on top run in the strip beside the pin header, outside the patch.

## Before ordering

- **Patch antenna pin position.** I could not open the datasheet for the BWGNSCNX18-18W4 (LCSC C784395). The footprint assumes the feed pin is at the centre of the 18 x 18 mm body, with a 1.3 mm hole. If the pin is off-centre the patch simply sits shifted by that amount; check it still clears the header solder joints (2.3 mm away as drawn) and the mounting hole.
- **Patch tuning.** A patch is tuned for a particular ground-plane size and this board is small, so reception may be weaker than a NEO-6M module with a 25 mm patch. The u.FL option is the fallback.
- **RF tracks** are 0.8 mm wide and under 5 mm long. They are not a calculated 50 ohm line; at this length the mismatch is small.
- **Stock and prices.** LCSC listings for the MAX-M10S-00B (C4153167) showed conflicting stock figures. R1, R2, R3, L1 and J1 have no LCSC number yet.
- **Module height.** The parts on the bottom face the radiosonde board. The tallest is U1 at about 2.5 mm, plus a u.FL plug if used; the J6 socket is 8.5 mm tall.

## Firmware

- Default output is NMEA at 9600 baud, as with the NEO-6M. Sentences start with `$GN...` instead of `$GP...`; TinyGPSPlus accepts both.
- The MAX-M10S starts in the portable model, which is not meant for balloon altitudes. The radiosonde firmware already sends a UBX-CFG-NAV5 "airborne <1g" command at start-up. That is the older configuration message; confirm on the bench that the M10 acknowledges it, or change the firmware to UBX-CFG-VALSET (CFG-NAVSPG-DYNMODEL = 6).

## Files

| File | What it is |
|---|---|
| `gps_module.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | KiCad 10 project |
| `gps_module.pretty/Patch_18x18_TH.kicad_mod` | patch antenna footprint |
| `gps_module_schematic.pdf` | schematic print |
| `gps_module_bom.csv` | parts list |
| `tools/build.py` | regenerates the schematic and footprint |
| `tools/pcb.py` | regenerates the board from `gps_module.net` (run with KiCad's Python) |

Regenerating overwrites manual edits to the schematic and board.
