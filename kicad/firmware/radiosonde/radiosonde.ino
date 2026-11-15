// Radiosonde firmware - on-board STM32F103C8T6, 8 MHz crystal (STM32duino core: board "Generic STM32F1 series", part "BluePill F103C8")
// Upload via ST-Link (SWD) or USART1 bootloader. Libraries: LoRa (Sandeep Mistry), TinyGPSPlus (Mikal Hart)
#include <SPI.h>
#include <Wire.h>
#include <LoRa.h>
#include <TinyGPSPlus.h>

// ---- pin map (matches schematic) ----
const uint32_t PIN_LORA_NSS = PA4;
const uint32_t PIN_LORA_RST = PB0;
const uint32_t PIN_LORA_DIO0 = PB1;
const uint32_t PIN_RTD_CS = PB12;
const uint32_t PIN_RTD_DRDY = PB13;
const uint32_t PIN_LED = PB14;
const uint32_t PIN_VBAT = PA0;      // divider 100k/100k
const uint32_t PIN_HEATER = PA8;    // HIGH turns on R15-R22 through Q2
// SPI1 = PA5/PA6/PA7, I2C1 = PB6 (SCL) / PB7 (SDA)

const long LORA_FREQ = 434000000L;  // 433.05-434.79 MHz SRD band - check local rules
const float RREF = 3970.0f, R0 = 1000.0f;  // R8; the fault thresholds in maxInit() depend on this value
const uint8_t MS5607_ADDR = 0x77;   // CSB = GND
const uint8_t SHT31_ADDR = 0x44;    // external probe on J9, ADDR pin low
const float HEAT_ON_C = 10.0f, HEAT_OFF_C = 15.0f;  // board temperature band, starts early because the heater can't keep up at 15 km
const float HEAT_MIN_VBAT = 3.0f;  // 1.0 V per cell; below this the heater stays off until reset, so the radio keeps running

HardwareSerial gpsSerial(PA3, PA2);   // USART2: RX=PA3 <- GPS TX, TX=PA2 -> GPS RX
HardwareSerial dbg(PA10, PA9);        // USART1 debug / bootloader (J4)
TinyGPSPlus gps;
uint16_t msC[8];
uint32_t frame = 0;
bool heaterOn = false, heaterLocked = false;

// ---------------- MAX31865 ----------------
SPISettings maxSPI(1000000, MSBFIRST, SPI_MODE1);
void maxWrite(uint8_t reg, uint8_t v) {
  SPI.beginTransaction(maxSPI); digitalWrite(PIN_RTD_CS, LOW);
  SPI.transfer(reg | 0x80); SPI.transfer(v);
  digitalWrite(PIN_RTD_CS, HIGH); SPI.endTransaction();
}
void maxRead(uint8_t reg, uint8_t *b, uint8_t n) {
  SPI.beginTransaction(maxSPI); digitalWrite(PIN_RTD_CS, LOW);
  SPI.transfer(reg & 0x7F);
  while (n--) *b++ = SPI.transfer(0);
  digitalWrite(PIN_RTD_CS, HIGH); SPI.endTransaction();
}
void maxInit() {
  maxWrite(0x03, 0x56); maxWrite(0x04, 0xDE);  // high fault ~ +90 C
  maxWrite(0x05, 0x2E); maxWrite(0x06, 0xA8);  // low fault  ~ -70 C
  maxWrite(0x00, 0xC3);                        // VBIAS, auto, 4-wire, clear, 50 Hz
}
float rtdTemp() {  // NAN on fault
  uint8_t d[2]; maxRead(0x01, d, 2);
  if (d[1] & 1) { maxWrite(0x00, 0xC3); return NAN; }
  uint16_t code = ((uint16_t)d[0] << 8 | d[1]) >> 1;
  float r = code * RREF / 32768.0f;
  const float A = 3.9083e-3f, B = -5.775e-7f;
  return (-A + sqrt(A * A - 4.0f * B * (1.0f - r / R0))) / (2.0f * B);
}

// ---------------- MS5607 ----------------
void msCmd(uint8_t c) { Wire.beginTransmission(MS5607_ADDR); Wire.write(c); Wire.endTransmission(); }
uint32_t msAdc(uint8_t conv) {
  msCmd(conv); delay(10);
  msCmd(0x00); Wire.requestFrom(MS5607_ADDR, (uint8_t)3);
  uint32_t v = 0; for (uint8_t i = 0; i < 3; i++) v = (v << 8) | Wire.read();
  return v;
}
void msInit() {
  msCmd(0x1E); delay(5);
  for (uint8_t i = 0; i < 8; i++) {
    msCmd(0xA0 + 2 * i); Wire.requestFrom(MS5607_ADDR, (uint8_t)2);
    msC[i] = (uint16_t)Wire.read() << 8 | Wire.read();
  }
}
void msRead(float &p_hPa, float &t_C) {
  uint32_t D1 = msAdc(0x48), D2 = msAdc(0x58);  // OSR 4096
  int32_t dT = (int32_t)D2 - ((int32_t)msC[5] << 8);
  int32_t TEMP = 2000 + (int64_t)dT * msC[6] / 8388608LL;
  int64_t OFF = ((int64_t)msC[2] << 17) + ((int64_t)msC[4] * dT) / 64;
  int64_t SENS = ((int64_t)msC[1] << 16) + ((int64_t)msC[3] * dT) / 128;
  if (TEMP < 2000) {  // 2nd-order compensation (MS5607 datasheet)
    int64_t T2 = ((int64_t)dT * dT) >> 31, t = TEMP - 2000;
    int64_t OFF2 = 61 * t * t / 16, SENS2 = 2 * t * t;
    if (TEMP < -1500) { int64_t u = TEMP + 1500; OFF2 += 15 * u * u; SENS2 += 8 * u * u; }
    TEMP -= T2; OFF -= OFF2; SENS -= SENS2;
  }
  int32_t P = (((int64_t)D1 * SENS >> 21) - OFF) >> 15;  // 0.01 mbar
  p_hPa = P / 100.0f; t_C = TEMP / 100.0f;
}
float baroAlt(float p) {  // ISA, valid to 20 km
  if (p > 226.321f) return 44330.8f * (1.0f - pow(p / 1013.25f, 0.190263f));
  return 11000.0f - 6341.6f * log(p / 226.321f);
}

// ---------------- SHT31 humidity probe ----------------
uint8_t shtCrc(const uint8_t *d, uint8_t n) {  // polynomial 0x31, init 0xFF
  uint8_t crc = 0xFF;
  while (n--) {
    crc ^= *d++;
    for (uint8_t i = 0; i < 8; i++) crc = (crc & 0x80) ? (crc << 1) ^ 0x31 : crc << 1;
  }
  return crc;
}
void shtRead(float &rh, float &t_C) {  // both NAN if the probe is missing or the data is corrupt
  rh = NAN; t_C = NAN;
  Wire.beginTransmission(SHT31_ADDR); Wire.write(0x24); Wire.write(0x00);  // single shot, high repeatability
  if (Wire.endTransmission() != 0) return;
  delay(20);
  if (Wire.requestFrom(SHT31_ADDR, (uint8_t)6) != 6) return;
  uint8_t d[6]; for (uint8_t i = 0; i < 6; i++) d[i] = Wire.read();
  if (shtCrc(d, 2) != d[2] || shtCrc(d + 3, 2) != d[5]) return;
  t_C = -45.0f + 175.0f * ((uint16_t)d[0] << 8 | d[1]) / 65535.0f;
  rh = 100.0f * ((uint16_t)d[3] << 8 | d[4]) / 65535.0f;
}

// ---------------- GPS: u-blox airborne <1g mode (required above 18 km, recommended always) ----------------
const uint8_t UBX_AIRBORNE[] = {0xB5,0x62,0x06,0x24,0x24,0x00,0xFF,0xFF,0x06,0x03,0x00,0x00,0x00,0x00,0x10,0x27,0x00,0x00,
  0x05,0x00,0xFA,0x00,0xFA,0x00,0x64,0x00,0x2C,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x16,0xDC};

float vbat() {
  uint32_t s = 0; for (uint8_t i = 0; i < 8; i++) s += analogRead(PIN_VBAT);
  return (s / 8.0f) * 3.3f / 4095.0f * 2.0f;  // calibrate per board
}

void heaterUpdate(float t_board, float vb) {
  if (vb < HEAT_MIN_VBAT) heaterLocked = true;
  if (heaterLocked || isnan(t_board) || t_board < -60.0f || t_board > 85.0f) heaterOn = false;
  else if (t_board < HEAT_ON_C) heaterOn = true;
  else if (t_board > HEAT_OFF_C) heaterOn = false;
  digitalWrite(PIN_HEATER, heaterOn ? HIGH : LOW);
}

void setup() {
  digitalWrite(PIN_HEATER, LOW); pinMode(PIN_HEATER, OUTPUT);
  pinMode(PIN_LED, OUTPUT); pinMode(PIN_RTD_CS, OUTPUT); digitalWrite(PIN_RTD_CS, HIGH);
  dbg.begin(115200);
  analogReadResolution(12);
  SPI.begin();
  Wire.setSDA(PB7); Wire.setSCL(PB6); Wire.begin(); Wire.setClock(100000);  // 100 kHz: the bus runs down the J9 probe cable
  maxInit(); msInit();
  gpsSerial.begin(9600);
  gpsSerial.write(UBX_AIRBORNE, sizeof(UBX_AIRBORNE));
  LoRa.setPins(PIN_LORA_NSS, PIN_LORA_RST, PIN_LORA_DIO0);
  if (!LoRa.begin(LORA_FREQ)) { while (1) { digitalWrite(PIN_LED, !digitalRead(PIN_LED)); delay(100); } }
  LoRa.setSpreadingFactor(9); LoRa.setSignalBandwidth(125E3); LoRa.setCodingRate4(5);
  LoRa.setTxPower(17, PA_OUTPUT_PA_BOOST_PIN); LoRa.enableCrc();
}

void loop() {
  uint32_t t0 = millis();
  while (millis() - t0 < 900) while (gpsSerial.available()) gps.encode(gpsSerial.read());

  float p, tint; msRead(p, tint);
  float tair = rtdTemp(), vb = vbat();
  heaterUpdate(tint, vb);
  float rh, trh; shtRead(rh, trh);
  char buf[140];
  // frame,lat,lon,gps_alt,press_hPa,baro_alt,t_air,t_board,vbat,sats,rh,t_rh,heat   (Arduino IDE: Tools > C Runtime Library > "Newlib Nano + Float Printf")
  snprintf(buf, sizeof(buf), "$RS,%lu,%.6f,%.6f,%.0f,%.2f,%.0f,%.2f,%.1f,%.2f,%d,%.1f,%.1f,%d", (unsigned long)frame++,
           gps.location.lat(), gps.location.lng(), gps.altitude.meters(), p, baroAlt(p), tair, tint, vb, (int)gps.satellites.value(), rh, trh, heaterOn ? 1 : 0);

  digitalWrite(PIN_LED, HIGH);
  LoRa.beginPacket(); LoRa.print(buf); LoRa.endPacket();
  digitalWrite(PIN_LED, LOW);
  dbg.println(buf);
}
