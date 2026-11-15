EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "gps_module"
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector_Generic:Conn_01x05 J1
U 1 1 1A91B54A
P 1600 2400
F 0 "J1" H 1600 2100 50  0000 C CNN
F 1 "PPS TXD RXD GND VCC" H 1600 2700 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical" H 1600 2400 50  0001 C CNN
F 3 "~" H 1600 2400 50  0001 C CNN
	1    1600 2400
	1    0    0    -1  
$EndComp
$Comp
L Device:FerriteBead FB1
U 1 1 18C705DD
P 1600 5000
F 0 "FB1" H 1700 4950 50  0000 L CNN
F 1 "600R" H 1700 5050 50  0000 L CNN
F 2 "Inductor_SMD:L_0603_1608Metric" H 1600 5000 50  0001 C CNN
F 3 "~" H 1600 5000 50  0001 C CNN
F 4 "C19330" H 1600 5000 50  0001 C CNN "LCSC"
F 5 "BLM18AG601SN1D" H 1600 5000 50  0001 C CNN "MPN"
	1    1600 5000
	1    0    0    -1  
$EndComp
$Comp
L Device:C C1
U 1 1 CB530E03
P 2200 5000
F 0 "C1" H 2300 4950 50  0000 L CNN
F 1 "10uF 10V" H 2300 5050 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 2200 5000 50  0001 C CNN
F 3 "~" H 2200 5000 50  0001 C CNN
F 4 "C95841" H 2200 5000 50  0001 C CNN "LCSC"
F 5 "CL21B106KOQNNNE" H 2200 5000 50  0001 C CNN "MPN"
	1    2200 5000
	1    0    0    -1  
$EndComp
$Comp
L Device:C C2
U 1 1 525A5FB9
P 2700 5000
F 0 "C2" H 2800 4950 50  0000 L CNN
F 1 "100nF" H 2800 5050 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 2700 5000 50  0001 C CNN
F 3 "~" H 2700 5000 50  0001 C CNN
F 4 "C1591" H 2700 5000 50  0001 C CNN "LCSC"
F 5 "CL10B104KB8NNNC" H 2700 5000 50  0001 C CNN "MPN"
	1    2700 5000
	1    0    0    -1  
$EndComp
$Comp
L RF_GPS:MAX-M10S U1
U 1 1 D7CBBBD4
P 5500 2700
F 0 "U1" H 5500 1900 50  0000 C CNN
F 1 "MAX-M10S-00B" H 5500 3500 50  0000 C CNN
F 2 "RF_GPS:ublox_MAX" H 5500 2700 50  0001 C CNN
F 3 "https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf" H 5500 2700 50  0001 C CNN
F 4 "C4153167" H 5500 2700 50  0001 C CNN "LCSC"
F 5 "MAX-M10S-00B" H 5500 2700 50  0001 C CNN "MPN"
	1    5500 2700
	1    0    0    -1  
$EndComp
$Comp
L Device:R R1
U 1 1 988A2D13
P 8500 2200
F 0 "R1" V 8500 1900 50  0000 C CNN
F 1 "0R" V 8500 2500 50  0000 C CNN
F 2 "Resistor_SMD:R_0603_1608Metric" V 8500 2200 50  0001 C CNN
F 3 "~" V 8500 2200 50  0001 C CNN
	1    8500 2200
	0    -1    -1    0  
$EndComp
$Comp
L Device:Antenna AE1
U 1 1 52C9859F
P 9200 2000
F 0 "AE1" H 9200 1650 50  0000 C CNN
F 1 "18x18 mm L1 patch" H 9200 2350 50  0000 C CNN
F 2 "gps_module:Patch_18x18_TH" H 9200 2000 50  0001 C CNN
F 3 "~" H 9200 2000 50  0001 C CNN
F 4 "C784395" H 9200 2000 50  0001 C CNN "LCSC"
F 5 "BWGNSCNX18-18W4" H 9200 2000 50  0001 C CNN "MPN"
	1    9200 2000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R2
U 1 1 01837CA9
P 8500 3200
F 0 "R2" V 8500 2900 50  0000 C CNN
F 1 "0R DNP" V 8500 3500 50  0000 C CNN
F 2 "Resistor_SMD:R_0603_1608Metric" V 8500 3200 50  0001 C CNN
F 3 "~" V 8500 3200 50  0001 C CNN
	1    8500 3200
	0    -1    -1    0  
$EndComp
$Comp
L Connector:Conn_Coaxial J2
U 1 1 8398E4F0
P 9400 3200
F 0 "J2" H 9400 2850 50  0000 C CNN
F 1 "U.FL" H 9400 3550 50  0000 C CNN
F 2 "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical" H 9400 3200 50  0001 C CNN
F 3 "~" H 9400 3200 50  0001 C CNN
F 4 "C88374" H 9400 3200 50  0001 C CNN "LCSC"
F 5 "U.FL-R-SMT-1(80)" H 9400 3200 50  0001 C CNN "MPN"
	1    9400 3200
	1    0    0    -1  
$EndComp
$Comp
L Device:L L1
U 1 1 4CCB12CC
P 8500 5000
F 0 "L1" H 8600 4950 50  0000 L CNN
F 1 "27nH DNP" H 8600 5050 50  0000 L CNN
F 2 "Inductor_SMD:L_0603_1608Metric" H 8500 5000 50  0001 C CNN
F 3 "~" H 8500 5000 50  0001 C CNN
	1    8500 5000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R3
U 1 1 76844C3F
P 9100 5000
F 0 "R3" H 9200 4950 50  0000 L CNN
F 1 "10R" H 9200 5050 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric" H 9100 5000 50  0001 C CNN
F 3 "~" H 9100 5000 50  0001 C CNN
	1    9100 5000
	1    0    0    -1  
$EndComp
$Comp
L Mechanical:MountingHole H1
U 1 1 28A7D7C8
P 1600 6299
F 0 "H1" H 1600 6049 50  0000 C CNN
F 1 "3 mm" H 1600 6549 50  0000 C CNN
F 2 "MountingHole:MountingHole_3mm" H 1600 6299 50  0001 C CNN
F 3 "~" H 1600 6299 50  0001 C CNN
	1    1600 6299
	1    0    0    -1  
$EndComp
Wire Wire Line
	1400 2200 1300 2200
Wire Wire Line
	1400 2300 1300 2300
Wire Wire Line
	1400 2400 1300 2400
Wire Wire Line
	1400 2500 1300 2500
Wire Wire Line
	1400 2600 1300 2600
Wire Wire Line
	1600 4850 1600 4750
Wire Wire Line
	1600 5150 1600 5250
Wire Wire Line
	2200 4850 2200 4750
Wire Wire Line
	2200 5150 2200 5250
Wire Wire Line
	2700 4850 2700 4750
Wire Wire Line
	2700 5150 2700 5250
Wire Wire Line
	4900 2300 4800 2300
Wire Wire Line
	4900 2400 4800 2400
Wire Wire Line
	5300 2000 5300 1900
Wire Wire Line
	5400 2000 5400 1900
Wire Wire Line
	5500 2000 5500 1900
Wire Wire Line
	5500 3400 5500 3500
Wire Wire Line
	5700 2000 5700 1900
Wire Wire Line
	6100 2700 6200 2700
Wire Wire Line
	6100 3000 6200 3000
Wire Wire Line
	8350 2200 8250 2200
Wire Wire Line
	8350 3200 8250 3200
Wire Wire Line
	8500 4850 8500 4750
Wire Wire Line
	8500 5150 8500 5250
Wire Wire Line
	8650 2200 8750 2200
Wire Wire Line
	8650 3200 8750 3200
Wire Wire Line
	9100 4850 9100 4750
Wire Wire Line
	9100 5150 9100 5250
Wire Wire Line
	9200 2200 9200 2300
Wire Wire Line
	9200 3200 9100 3200
Wire Wire Line
	9400 3400 9400 3500
Text Label 1300 2200 2    50   ~ 0
PPS
Text Label 1300 2300 2    50   ~ 0
TXD
Text Label 1300 2400 2    50   ~ 0
RXD
Text Label 1300 2500 2    50   ~ 0
GND
Text Label 1300 2600 2    50   ~ 0
VCC
Text Label 1600 4750 1    50   ~ 0
VCC
Text Label 1600 5250 3    50   ~ 0
VCC_F
Text Label 2200 4750 1    50   ~ 0
VCC_F
Text Label 2200 5250 3    50   ~ 0
GND
Text Label 2700 4750 1    50   ~ 0
VCC_F
Text Label 2700 5250 3    50   ~ 0
GND
Text Label 5500 3500 3    50   ~ 0
GND
Text Label 5500 3500 3    50   ~ 0
GND
Text Label 5500 3500 3    50   ~ 0
GND
Text Label 4800 2400 2    50   ~ 0
TXD
Text Label 4800 2300 2    50   ~ 0
RXD
Text Label 6200 3000 0    50   ~ 0
PPS
Text Label 5500 1900 1    50   ~ 0
VCC_F
Text Label 5400 1900 1    50   ~ 0
VCC_F
Text Label 5300 1900 1    50   ~ 0
VCC_F
Text Label 6200 2700 0    50   ~ 0
RF_IN
Text Label 5700 1900 1    50   ~ 0
VCC_RF
Text Label 8250 2200 2    50   ~ 0
RF_IN
Text Label 8750 2200 0    50   ~ 0
ANT_PATCH
Text Label 9200 2300 3    50   ~ 0
ANT_PATCH
Text Label 8250 3200 2    50   ~ 0
RF_IN
Text Label 8750 3200 0    50   ~ 0
ANT_EXT
Text Label 9100 3200 2    50   ~ 0
ANT_EXT
Text Label 9400 3500 3    50   ~ 0
GND
Text Label 8500 4750 1    50   ~ 0
ANT_EXT
Text Label 8500 5250 3    50   ~ 0
BIAS
Text Label 9100 4750 1    50   ~ 0
BIAS
Text Label 9100 5250 3    50   ~ 0
VCC_RF
NoConn ~ 4900 2900
NoConn ~ 4900 3100
NoConn ~ 6100 2500
NoConn ~ 4900 3200
NoConn ~ 4900 2600
NoConn ~ 4900 2700
NoConn ~ 4900 3000
Text Notes 984 1181 0    98   ~ 0
TO RADIOSONDE J6
Text Notes 984 3150 0    59   ~ 0
Pin header on the bottom side, pins down into the socket.
Text Notes 984 3346 0    59   ~ 0
TXD = module output, RXD = module input, 3.3 V logic.
Text Notes 984 4134 0    98   ~ 0
SUPPLY FILTER
Text Notes 4331 1181 0    98   ~ 0
GNSS RECEIVER: u-blox MAX-M10S
Text Notes 4331 3937 0    59   ~ 0
V_BCKP tied to VCC: no backup supply, cold start at every power-on.
Text Notes 4331 4134 0    59   ~ 0
VIO_SEL open = 3.3 V I/O.  RF_IN has an internal DC block, LNA and SAW filter.
Text Notes 4331 4331 0    59   ~ 0
Default: 9600 baud NMEA, portable model. Firmware must select airborne <1g for flight.
Text Notes 7874 1181 0    98   ~ 0
ANTENNA: fit R1 (patch) OR R2 (u.FL), never both
Text Notes 7874 4134 0    59   ~ 0
ACTIVE ANTENNA BIAS (u.FL only): fit L1 to feed VCC_RF to the antenna
Text Notes 7874 5906 0    59   ~ 0
Leave L1 out for a passive antenna: some are a DC short and would load VCC_RF.
$EndSCHEMATC
