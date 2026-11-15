# Radiosonde rev B

The MCU is an STM32F103C8T6 (LQFP-48) soldered on the board. The rest of the board:
- RA-02 (SX1278, 433 MHz) LoRa radio
- MS5607 pressure sensor (10–1200 mbar)
- MAX31865 + PT1000 for 4-wire air temperature
- 3×AA cells into a TPS63001 3.3 V buck-boost
- Box heater: eight 120 Ω 0.25 W resistors switched by Q2 from PA8

Made with KiCad 7; opens in KiCad 8/9.

## Files
- `radiosonde.kicad_pro / .kicad_sch / .kicad_pcb`: the project
- `radiosonde.kicad_sym`: project symbols
  - `BluePill`: unused since the MCU moved on board
  - `RA-02`: pin 1 = ANT, left open; the module's IPEX connector is used
- `radiosonde.pretty/`: the U4 TQFN footprint; `BluePill_Socket` is unused
- `radiosonde_schematic.pdf`: printable schematic
- `firmware/radiosonde/radiosonde.ino`: STM32duino sketch
- `tools/`: Python scripts that regenerated these files

## PCB status
The board is 90 × 45 mm, 2 layers, with a 40 × 30 mm area at the lower left for a plug-in NEO-6M GPS module on J6 (5 pins: PPS, TXD, RXD, GND, VCC). Print the PCB 1:1 and check the module against it before ordering. All footprints are placed, nets assigned and GND pours added on both layers. **Not routed.**

To finish it:
1. Route the board, by hand or with Freerouting.
2. Press B to fill the zones.
3. Run DRC.

## Pin map
| Function | STM32 pin |
|---|---|
| SPI1 SCK / MISO / MOSI (shared by LoRa and MAX31865) | PA5 / PA6 / PA7 |
| LoRa NSS / RST / DIO0 / DIO1 | PA4 / PB0 / PB1 / PB10 |
| MAX31865 CS / DRDY | PB12 / PB13 |
| I2C1 SCL / SDA (MS5607 at 0x77, expansion) | PB6 / PB7 |
| GPS on USART2: TX → GPS RX, RX ← GPS TX | PA2 / PA3 |
| Debug / bootloader on USART1 (J4): TX / RX | PA9 / PA10 |
| Battery sense (100k/100k divider) | PA0 |
| Heater switch Q2 | PA8 |
| Status LED | PB14 |
| Expansion J7 | PA1, PB15, I2C |
| SWD on J10: SWDIO / SWCLK | PA13 / PA14 |

## Power notes
- **MCU supply:** VDD and VBAT come from the TPS63001 3.3 V rail. VDDA comes through ferrite FB1.
- **Programming:** SWD on J10. For the USART1 bootloader, jumper J10 pins 5 and 6, reset, then use J4.
- **Lower the clock to stretch battery life.** At 72 MHz the board draws about 25 mA, plus the radio's transmit bursts. Lithium AA cells (about 3 Ah) last many hours, far more than a 2–3 hour flight.

## Flight notes (15 km)
- **Pressure:** at 15 km it is about 120 hPa, which is within the MS5607's range.
- **Cold:** put the PCB and batteries in an insulated foam box. The RA-02 is only rated down to −20 °C, so cold-test it before you fly. Only the PT1000 probe goes outside.
- **Batteries:** use lithium AA (Energizer L91). Alkaline cells collapse in the cold.
- **GPS:** the sketch sends the u-blox airborne (<1 g) mode command at startup.
- **Firmware build:** in the Arduino IDE, choose Tools → C Runtime Library → "Newlib Nano + Float Printf". Without it, the float fields in the packet come out empty.
- **Regulations:** check local rules for 433 MHz transmit power and for balloon launches.
