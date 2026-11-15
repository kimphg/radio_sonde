# Radiosonde project: session handoff

Context for continuing this project in a local Claude Code session. Put this file in the project root (next to `radiosonde.kicad_pro`); Claude Code loads `CLAUDE.md` automatically.

## Goal
A weather-balloon radiosonde for flights up to **15 km**, powered by **3×AA** cells.
- **Radio:** Ai-Thinker RA-02 (SX1278, 433 MHz LoRa)
- **Pressure:** MS5607
- **Air temperature:** PT1000 RTD read by a MAX31865
- **Humidity:** an external SHT31 probe on J9 (I2C)
- **Position:** an optional u-blox NEO-6M GPS module on a 5-pin socket
- **MCU:** an **STM32F103C8T6 soldered on the board** (rev B, LQFP-48). It replaced a plug-in Blue Pill. Rev A used an ATmega328P-AU and was superseded.

## Current status (rev B)
| Item | Status |
|---|---|
| Schematic `radiosonde.kicad_sch` | Done, KiCad 7 format (opens in 8/9). Netlist checked pin by pin. **ERC not run yet** (the KiCad 7 CLI has no ERC). |
| PCB `radiosonde.kicad_pcb` | 90×45 mm, 2 layers, with a 40×30 mm GPS area at the lower left. All footprints placed, nets assigned, GND pours on F.Cu and B.Cu. **Not routed, zones not filled, DRC not run.** |
| Firmware `firmware/radiosonde/radiosonde.ino` | STM32duino sketch. **Never compiled.** |
| Project libraries | `radiosonde.kicad_sym` (RA-02; the BluePill symbol is unused), `radiosonde.pretty` (U4 footprint; BluePill_Socket is unused), `sym-lib-table`, `fp-lib-table` |
| Generator scripts `tools/` | `build.py` writes the schematic, symbols and footprint. `pcb.py` writes the PCB from a netlist using the pcbnew Python module. `sexp.py` is an S-expression helper. |

**Important:** the scripts read the KiCad stock libraries from `/usr/share/kicad/...` on Linux. The schematic and PCB have since been edited directly (the VINA filter), so **do not regenerate**: the scripts would overwrite those edits.

## Design decisions (and why)
- **MS5607, not BMP280:** pressure at 15 km is about 120 hPa. The BMP280 bottoms out at 300 hPa (about 9 km); the MS5607 covers 10–1200 mbar.
- **TPS63001 buck-boost to 3.3 V:** 3×AA spans about 5.4 V (fresh lithium) down to about 2.7 V (end of life), so the output must work both above and below 3.3 V. The TPS63001's VIN max is 5.5 V. PS/SYNC is tied to GND for power-save mode, and its FB pin goes to VOUT (it is the fixed 3.3 V version).
- **TPS63001 VINA filter:** the control-stage supply comes from VBAT through R3 (100 Ω) with C2 (100 nF) on VINA, matching TI's typical application. Keep R3 and C2 next to U5 pin 8. #FLG3 is a PWR_FLAG on VINA, needed because ERC can't see power through R3.
- **Lithium AA (Energizer L91):** alkaline cells collapse in the cold.
- **Reverse-polarity protection:** a DMG2305UX P-FET (D to battery, S to load, G to GND), followed by an SPDT power switch.
- **PT1000 + MAX31865 in 4-wire mode:** measures −60 to +80 °C.
  - RREF (R8) = 3.97 kΩ, 0.1%, 25 ppm/°C. Valid range is 350 Ω to 10 kΩ, and 4 kΩ is optimum for a PT1000.
  - CI = 10 nF C0G across RTDIN±.
  - 10 MΩ from RTDIN+ to BIAS, so a broken lead is detected.
  - FORCE2 is tied to GND.
- **Cold handling:** the MAX31865 is rated only to −40 °C, and the RA-02 to −20 °C. The PCB and batteries fly in an insulated foam box; only the PT1000 probe sits outside.
- **Box heater:** R15–R22 are eight 120 Ω 0.25 W 1206 resistors in parallel from VBAT_PROT, switched low-side by AO3400A Q2 from PA8.
  - **Power:** 15 Ω total, about 1.35 W at 4.5 V and 300 mA. 120 Ω keeps each resistor within 0.25 W at 5.4 V, so a stuck-on heater can't overstress them. Cold cells under load may give about 0.9–1.2 W.
  - **Before SW1:** the heater taps VBAT_PROT so its current doesn't go through the power switch. R14 holds Q2 off when the MCU is off or in reset, so SW1 still turns the heater off.
  - **Layout:** the resistors are spread around the cold-sensitive parts: R15–R17 along the right edge of the RA-02, R18 and R19 beside and below the STM32, R20 above crystal Y1, and R21 and R22 on either side of the MAX31865 (R22 sits between it and reference resistor R8). None is beside the TPS63001. The nearest heater is about 4.4 mm from the MS5607, which is the thermostat sensor, so check the 10/15 °C thresholds against a second thermometer in the box. Use wide traces (at least 0.5 mm) for VBAT_PROT, HEAT_SW and Q2's source.
  - **Limit:** with 20 mm foam and no sun, the model passes −20 °C at about 13.8 km even with 1.2 W, because holding temperature at 15 km needs about 3–4 W. 40 mm foam stays above −20 °C through the ascent and an hour at 15 km.
- **SHT31 humidity probe on J9:** it must sit outside the foam box in moving air; on the board it would measure the warm box air. It shares I2C1 with the MS5607, so a shorted probe cable would also take out pressure data. Keep the cable short, and shield the sensor from sun and rain. The bus runs at 100 kHz because it leaves the board. The SHT31 is rated only to −40 °C, reached at about 8.5 km in the standard atmosphere (higher in the tropics, lower in a mid-latitude winter), so treat humidity above that as out of spec and cold-test the probe before flight. It was kept over −60 °C capacitive sensors such as the HS1101LF, which need an analog readout and were hard to source.
- **On-board MCU:** U1 is the STM32F103C8T6 on LQFP-48, with the same pin assignments and clock as the Blue Pill build, so the firmware is unchanged. There is no USB connector or AMS1117. Power LED D2 runs from +3V3 through R23 and draws about 1.3 mA whenever SW1 is on.
  - **Power:** VDD and VBAT are on +3V3, with C6, C7 and C8 at the three VDD pins and C11 as bulk. VDDA comes through ferrite FB1 with C9 and C10, per the ST datasheet. The battery ADC reference is VDDA.
  - **Clock:** Y1 is 8 MHz, 20 pF load, rated −40 to +85 °C, with 33 pF load capacitors C19 and C20. Keep Y1 tight to pins 5 and 6, with no other signals under it.
  - **Boot and reset:** R11 pulls BOOT0 low, R12 pulls PB2 (BOOT1) low, and C12 is on NRST. There is no reset button; NRST is on J10.
  - **Programming:** use SWD on J10 (GND, SWCLK, SWDIO, NRST, BOOT0, 3V3). For the USART1 ROM bootloader, jumper J10 pins 5 and 6, reset, then use J4.
- **GPS area:** x 0.4–40.4, y 14.7–44.7 mm is marked on silkscreen. The module footprint on J6 and the GPS_AREA rule area around it keep it free of other parts. Tracks and GND pour are allowed under it. It sits at the far end from the RA-02 and the heater.
- **GPS module footprint:** `GPS_NEO6M_5pin` comes from `GPS-MODULE-GPS-NEO-6M_2026-11-06.dxf`: 27.56 × 26.42 mm, five pins at 2.54 mm, and one Ø3 mm hole. The pin row is at x 37.4, y 24.72–34.88, and the hole at (14.79, 19.51). The DXF shows only one hole, so the other side is held by the socket alone. Check the footprint against the real module with a 1:1 print before ordering, because a mirrored footprint would swap VCC and PPS.
- **RA-02 antenna:** pin 1 (ANT) is deliberately left open and the module's IPEX connector is used. In the custom symbol, pin 1 is unhidden and renamed ANT; the stock symbol stacks it as a hidden GND.
- **433 MHz SRD band:** the firmware uses 434.0 MHz, SF9, BW125, 17 dBm. Check local rules.

## Pin map (STM32F103C8T6)
| Net | Pin | Notes |
|---|---|---|
| SCK / MISO / MOSI | PA5 / PA6 / PA7 | SPI1, shared by RA-02 and MAX31865 |
| LORA_NSS / LORA_RST / LORA_DIO0 / LORA_DIO1 | PA4 / PB0 / PB1 / PB10 | 10k pull-up on NSS |
| RTD_CS / RTD_DRDY | PB12 / PB13 | 10k pull-up on CS. The MAX31865 needs SPI mode 1 or 3; the SX1278 uses mode 0. |
| SCL / SDA | PB6 / PB7 | I2C1 at 100 kHz, 4.7k pull-ups. MS5607 at 0x77 (CSB = GND, PS = 3V3). SHT31 probe on J9 at 0x44. |
| GPS_TX / GPS_RX | PA2 / PA3 | USART2 (GPS_TX goes to the GPS RX) |
| TXD / RXD | PA9 / PA10 | USART1, to FTDI header J4 (debug / ROM bootloader) and serial extension J8. Only one device may drive RXD at a time. |
| VBAT_SENSE | PA0 | 100k/100k divider; 5.4 V gives 2.7 V |
| HEAT_CTL | PA8 | through R13 to Q2 gate, high turns the heater on |
| LED | PB14 | through 1k to a green 0603 LED |
| EXP1 / EXP2 | PA1 / PB15 | on expansion header J7, with I2C and 3V3/GND |
| SWDIO / SWCLK | PA13 / PA14 | on J10 |
| OSC_IN / OSC_OUT | PD0 / PD1 (pins 5, 6) | crystal Y1 |
| BOOT1 | PB2 | pulled low by R12 |

**Unused MCU pins:** PA11, PA12, PA15, PB3, PB4, PB5, PB8, PB9, PB11, PC13, PC14 and PC15 are left open.

## Sourcing
Symbols carry hidden `LCSC` and `MPN` fields, chosen on 2026-11-05 with more than 500 in stock at LCSC.
- **R8 is RT0603BRD073K97L (C861386).** The original 4.02 kΩ ≤10 ppm spec had no verified in-stock part, so this is 25 ppm: about 0.19 °C of drift over a 30 °C board temperature swing, against 0.08 °C at 10 ppm. If R8 changes again, update `RREF` and the MAX31865 fault thresholds in the firmware to match.
- **U4 is the TQFN-20 MAX31865ATP+T (C118474)** because SSOP-20 stock was 3 or fewer. Its footprint is in the project library, with five 0.3 mm vias tying the exposed pad to GND.
- **J6 is one DS1023-1x5SF11 socket (C7509517).** It is 8.5 mm tall, so check that the module's underside parts clear the board.
- **J8 is not on the BOM:** it is plain 1×5 2.54 mm through-hole pads, so any header can be soldered in.
- **D1 must stay a roughly 2 V LED.** A 3 V green LED gets about 0.2 mA from 3.3 V through R4.
- **U1 is C8734** (ST STM32F103C8T6). J10 uses the same 1×6 header as J4 and J7. C10 uses the same part as C16.

## Reference designators
| Ref | Part |
|---|---|
| J1 | Battery, JST-PH 2-pin |
| Q1 | Reverse-polarity P-FET |
| SW1 | Power switch |
| U5 | TPS63001 |
| L1 | 2.2 µH, Coilcraft LPS4018 |
| C1 | Input capacitor |
| R3, C2 | VINA filter: 100 Ω from VBAT, 100 nF to GND |
| C3, C4 | 22 µF output capacitors |
| R1, R2, C5 | Battery-sense divider |
| U1 | STM32F103C8T6 (LQFP-48) |
| C6, C7, C8, C11 | MCU VDD decoupling (three 100 nF, 10 µF bulk) |
| FB1, C9, C10 | VDDA filter: ferrite, 1 µF, 10 nF |
| Y1, C19, C20 | 8 MHz crystal and 33 pF load capacitors |
| R11, R12 | BOOT0 and BOOT1 pull-downs, 10 kΩ |
| C12 | NRST capacitor, 100 nF |
| R4, D1 | Status LED on PB14 (silkscreen STA) |
| R23, D2 | Power LED on +3V3 (silkscreen PWR), same parts as R4 and D1 |
| R15–R22 | Heater, 120 Ω 1206 0.25 W, all in parallel |
| Q2, R13, R14 | Heater switch: AO3400A, 100 Ω gate resistor, 10 kΩ gate pull-down |
| U2 | RA-02 |
| C13, C14 | RA-02 decoupling |
| R5 | NSS pull-up |
| U3 | MS5607 (LGA-8 3×5 mm) |
| C15 | MS5607 decoupling |
| R6, R7 | I2C pull-ups |
| U4 | MAX31865ATP+T (TQFN-20-EP, 5×5 mm), rotated 180° so the RTD pins face J5 |
| R8 | RREF, 3.97 kΩ |
| C16 | CI |
| R9 | 10 MΩ |
| C17, C18 | MAX31865 decoupling |
| R10 | CS pull-up |
| J5 | PT1000 4-wire connector, JST-PH 4-pin |
| J4 | FTDI 1×6 (GND, NC, 3V3, RXD, TXD, NC) |
| J6 | GPS socket 1×5 2.54 mm. Pin 1 PPS (not connected), pin 2 module TXD to GPS_RX, pin 3 module RXD to GPS_TX, pin 4 GND, pin 5 VCC to +3V3. |
| J7 | Expansion 1×6 |
| J8 | Serial extension 1×5 (3V3, 3V3, TXD, RXD, GND), shares USART1 with J4 |
| J9 | Humidity probe, JST-PH 4-pin (3V3, GND, SDA, SCL) |
| J10 | SWD / boot 1×6 (GND, SWCLK, SWDIO, NRST, BOOT0, 3V3) |
| H1, H2 | M3 holes |
| #FLG1, #FLG2, #FLG3, #FLG4 | PWR_FLAG on VBAT, GND, VINA and VDDA |

## Firmware notes
- **Board settings:** STM32duino core, board "Generic STM32F1 series", part "BluePill F103C8". That target still fits, because the chip and 8 MHz crystal are the same. Set **C Runtime Library to "Newlib Nano + Float Printf"**, otherwise the `%f` fields in the packet print empty.
- **Libraries:** LoRa (Sandeep Mistry) and TinyGPSPlus.
- **Packet format (CSV over LoRa, also printed on USART1):** `$RS,frame,lat,lon,gps_alt,press_hPa,baro_alt,t_air,t_board,vbat,sats,rh,t_rh,heat` (`rh` and `t_rh` print `nan` if the probe is missing or its CRC fails; `heat` is 1 while the heater is on)
- **MS5607:** uses OSR 4096 and the 2nd-order compensation from the datasheet (OFF uses C2·2^17 + C4·dT/2^6, SENS uses C1·2^16 + C3·dT/2^7).
- **Barometric altitude:** ISA model, with the isothermal layer above 11 km.
- **MAX31865:**
  - Config byte 0xC3: VBIAS on, auto conversion, 4-wire, fault clear, 50 Hz filter.
  - Fault thresholds: high 0x56DE (about +90 °C), low 0x2EA8 (about −70 °C), both calculated for RREF = 3.97 kΩ.
  - Temperature comes from the quadratic Callendar–Van Dusen formula (A = 3.9083e-3, B = −5.775e-7). Ignoring the C term costs about 0.04 °C of error at −60 °C.
- **Heater:** on below 10 °C and off above 15 °C, using the MS5607 board temperature once per packet. It stays off if that reading is invalid, and locks off until reset if VBAT drops below 3.0 V.
- **GPS:** sends the UBX-CFG-NAV5 airborne (<1 g, dynModel 6) command at startup.

## Open TODO list
1. Open the project in KiCad 8/9. Accept the format upgrade, run **ERC**, and fix any findings.
2. **Verify footprints:** print the PCB 1:1 and check the RA-02 footprint (it reuses the stock `Ai-Thinker-Ra-01-LoRa` SMD-16) and the MS5607 LGA-8 footprint.
3. Refine the placement if needed, then route the board.
   - Keep the TPS63001 loop (VIN capacitor → IC → L1 → VOUT capacitors) tight.
   - Keep the MS5607 away from the regulator's heat.
   - Use short, symmetric traces for the RTD inputs.
   - Leave RF keep-out around the RA-02.
4. Fill zones (B) and run **DRC**. Export Gerbers, BOM and position files.
5. Compile the firmware. Bench-test each subsystem: LoRa link, MS5607 readings against a reference, RTD against an ice bath, GPS lock, and battery ADC calibration.
6. Optional:
   - Lowering the MCU clock or adding sleep between frames.
   - A cold-chamber test at −40 °C.
   - A LoRa receiver / ground-station sketch.

## Useful commands
```bash
# KiCad 8+ CLI checks
kicad-cli sch erc --severity-all -o erc.rpt radiosonde.kicad_sch
kicad-cli pcb drc -o drc.rpt radiosonde.kicad_pcb
kicad-cli sch export pdf -o radiosonde_schematic.pdf radiosonde.kicad_sch

# Firmware build
arduino-cli compile --fqbn "STMicroelectronics:stm32:GenF1:pnum=BLUEPILL_F103C8,rtlib=nanofp" firmware/radiosonde
```
