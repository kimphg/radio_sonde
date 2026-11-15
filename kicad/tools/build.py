import copy, math, uuid, os, sys
from sexp import *

PROJ = 'radiosonde'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/radiosonde'
os.makedirs(OUT, exist_ok=True)
U = lambda: str(uuid.uuid4())
ROOT = U()

# ---------- custom RA-02 symbol (pin 1 = ANT, visible, unconnected) ----------
def make_ra02():
    e = flatten('RF_Module', 'Ai-Thinker-Ra-02')
    def walk(x):
        for c in x:
            if isinstance(c, list):
                if c[0] == 'pin' and child(c, 'number')[0][1] == S('1'):
                    if 'hide' in c: c.remove('hide')
                    at = child(c, 'at')[0]; at[1:4] = ['-10.16', '-10.16', '0']
                    child(c, 'name')[0][1] = S('ANT')
                else: walk(c)
    walk(e)
    for p in child(e, 'property'):
        if p[1] == S('Value'): p[2] = S('RA-02')
        if p[1] == S('Description'): p[2] = S('Ai-Thinker Ra-02 SX1278 433 MHz LoRa module (pin 1 = ANT pad, IPEX used)')
    e[1] = S('RA-02')
    for u in child(e, 'symbol'): u[1] = S(u[1][1].replace('Ai-Thinker-Ra-02', 'RA-02'))
    return e

RA02 = make_ra02()

BP_ROW1 = ['PB12','PB13','PB14','PB15','PA8','PA9','PA10','PA11','PA12','PA15','PB3','PB4','PB5','PB6','PB7','PB8','PB9','5V','GND','3V3']
BP_ROW2 = ['VBAT','PC13','PC14','PC15','PA0','PA1','PA2','PA3','PA4','PA5','PA6','PA7','PB0','PB1','PB10','PB11','NRST','3V3','GND','GND']
def make_bluepill():
    def pin(num, name, x, ang, y):
        t = {'3V3': 'power_in', 'GND': 'power_in', '5V': 'passive', 'VBAT': 'passive', 'NRST': 'passive'}.get(name, 'bidirectional')
        return ['pin', t, 'line', ['at', x, y, ang], ['length', 5.08],
                ['name', S(name), ['effects', ['font', ['size', 1.27, 1.27]]]],
                ['number', S(str(num)), ['effects', ['font', ['size', 1.27, 1.27]]]]]
    ps = []
    for i, n in enumerate(BP_ROW1): ps.append(pin(i + 1, n, -17.78, 0, round(24.13 - 2.54 * i, 2)))
    for i, n in enumerate(BP_ROW2): ps.append(pin(i + 21, n, 17.78, 180, round(24.13 - 2.54 * i, 2)))
    def pr(k, v, y, hide=False):
        eff = ['effects', ['font', ['size', 1.27, 1.27]]] + (['hide'] if hide else [])
        return ['property', S(k), S(v), ['at', 0, y, 0], eff]
    return ['symbol', S('BluePill'), ['in_bom', 'yes'], ['on_board', 'yes'],
            pr('Reference', 'U', 29.21), pr('Value', 'BluePill', -29.21),
            pr('Footprint', 'radiosonde:BluePill_Socket', 0, True), pr('Datasheet', '~', 0, True),
            pr('Description', 'STM32F103C8T6 Blue Pill board in 2x20 female headers (pin 1 = PB12, pin 21 = VBAT, both at USB end)', 0, True),
            ['symbol', S('BluePill_0_1'), ['rectangle', ['start', -12.7, 27.94], ['end', 12.7, -27.94],
                ['stroke', ['width', 0.254], ['type', 'default']], ['fill', ['type', 'background']]]],
            ['symbol', S('BluePill_1_1')] + ps]

def write_bluepill_fp(out):
    os.makedirs(f'{out}/radiosonde.pretty', exist_ok=True)
    L = ['(footprint "BluePill_Socket" (version 20221018) (generator pcbnew) (layer "F.Cu")',
         '  (descr "STM32 Blue Pill in 2x20 2.54 mm female headers, rows 15.24 mm apart. Top view, USB at left. Pin 1 = PB12, pin 21 = VBAT.")',
         '  (attr through_hole)',
         '  (fp_text reference "REF**" (at 24.13 -12.7) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
         '  (fp_text value "BluePill" (at 24.13 12.7) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
         '  (fp_text user "USB" (at -1.2 0 90) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
         '  (fp_text user "B12" (at 0 -5.2) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
         '  (fp_text user "VB" (at 0 5.2) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
         '  (fp_text user "3V3" (at 48.26 -5.2) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
         '  (fp_text user "GND" (at 48.26 5.2) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
         '  (fp_rect (start -3.2 -11.43) (end 50.1 11.43) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))',
         '  (fp_rect (start -3.45 -11.68) (end 50.35 11.68) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))',
         '  (fp_rect (start -3.2 -11.43) (end 50.1 11.43) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))']
    for i in range(20):
        for row, y, base in ((0, -7.62, 1), (1, 7.62, 21)):
            n = base + i
            shape = 'rect' if n in (1, 21) else 'circle'
            L.append(f'  (pad "{n}" thru_hole {shape} (at {round(2.54*i,2)} {y}) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask"))')
    L.append(')')
    open(f'{out}/radiosonde.pretty/BluePill_Socket.kicad_mod', 'w').write('\n'.join(L) + '\n')
    open(f'{out}/fp-lib-table', 'w').write('(fp_lib_table\n  (lib (name "radiosonde")(type "KiCad")(uri "${KIPRJMOD}/radiosonde.pretty")(options "")(descr "Project footprints"))\n)\n')

BLUEPILL = make_bluepill()
write_bluepill_fp(OUT)
with open(f'{OUT}/{PROJ}.kicad_sym', 'w') as f:
    f.write(dump(['kicad_symbol_lib', ['version', '20220914'], ['generator', 'kicad_symbol_editor'], RA02, BLUEPILL]))

def getsym(lib, name):
    if lib == 'radiosonde': return copy.deepcopy(RA02 if name == 'RA-02' else BLUEPILL)
    return flatten(lib, name)

# ---------- schematic model ----------
parts, items = [], []
libsyms = {}
FP = dict(
    R='Resistor_SMD:R_0603_1608Metric', C='Capacitor_SMD:C_0603_1608Metric',
    C8='Capacitor_SMD:C_0805_2012Metric')

def part(ref, lib, sym, value, fp, x, y, nets, rot=0, extra=None):
    parts.append(dict(ref=ref, lib=lib, sym=sym, value=value, fp=fp, x=x, y=y, rot=rot, nets=nets, extra=extra or {}))

def R(ref, val, x, y, n1, n2, rot=0): part(ref, 'Device', 'R', val, FP['R'], x, y, {'1': n1, '2': n2}, rot)
def C(ref, val, x, y, n1, n2, fp=None): part(ref, 'Device', 'C', val, fp or FP['C'], x, y, {'1': n1, '2': n2})
def note(x, y, txt, size=2.0):
    items.append(['text', S(txt), ['at', x, y, 0], ['effects', ['font', ['size', size, size]] + (['bold'] if size > 2 else []), ['justify', 'left']], ['uuid', U()]])

G = 2.54
# ===== POWER =====
note(20, 22, 'POWER: 3xAA -> TPS63001 buck-boost 3.3 V', 2.5)
part('J1', 'Connector_Generic', 'Conn_01x02', 'BATT 3xAA', 'Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal', 30.48, 48.26, {'1': 'VBAT_RAW', '2': 'GND'})
part('Q1', 'Device', 'Q_PMOS_GSD', 'DMG2305UX', 'Package_TO_SOT_SMD:SOT-23', 55.88, 48.26, {'1': 'GND', '2': 'VBAT_PROT', '3': 'VBAT_RAW'})
part('SW1', 'Switch', 'SW_SPDT', 'POWER', 'Button_Switch_SMD:SW_SPDT_PCM12', 81.28, 48.26, {'2': 'VBAT_PROT', '1': 'VBAT', '3': None})
part('U5', 'Regulator_Switching', 'TPS63001', 'TPS63001', 'Package_SON:Texas_DRC0010J_ThermalVias', 124.46, 50.8,
     {'5': 'VBAT', '8': 'VBAT', '6': 'VBAT', '7': 'GND', '4': 'SW_L1', '2': 'SW_L2', '1': '+3V3', '10': '+3V3', '3': 'GND', '9': 'GND'})
part('L1', 'Device', 'L', '2.2uH 1.5A (LPS4018)', 'Inductor_SMD:L_Coilcraft_LPS4018', 101.6, 81.28, {'1': 'SW_L1', '2': 'SW_L2'})
C('C1', '10uF 10V', 30.48, 81.28, 'VBAT', 'GND', FP['C8'])
C('C2', '100nF', 43.18, 81.28, 'VBAT', 'GND')
C('C3', '22uF 6.3V', 121.92, 81.28, '+3V3', 'GND', FP['C8'])
C('C4', '22uF 6.3V', 134.62, 81.28, '+3V3', 'GND', FP['C8'])
R('R1', '100k 1%', 60.96, 81.28, 'VBAT', 'VBAT_SENSE')
R('R2', '100k 1%', 73.66, 81.28, 'VBAT_SENSE', 'GND')
C('C5', '100nF', 86.36, 81.28, 'VBAT_SENSE', 'GND')
part('#FLG1', 'power', 'PWR_FLAG', 'PWR_FLAG', '', 43.18, 104.14, {'1': 'VBAT'})
part('#FLG2', 'power', 'PWR_FLAG', 'PWR_FLAG', '', 55.88, 104.14, {'1': 'GND'})
note(20, 112, 'Use lithium AA (Energizer L91) - alkaline cells lose most capacity below -20 C.')
note(20, 118, 'VBAT_SENSE = VBAT / 2  ->  PA0 (ADC1_IN0, 3.3 V ref; 5.4 V max -> 2.7 V)')

# ===== MCU =====
note(165, 22, 'MCU: STM32F103C8T6 Blue Pill (plug-in, 2x20 female headers)', 2.5)
part('U1', 'radiosonde', 'BluePill', 'BluePill STM32F103C8T6', 'radiosonde:BluePill_Socket', 200.66, 81.28, {'1': 'RTD_CS', '2': 'RTD_DRDY', '3': 'LED', '4': 'EXP2', '5': None, '6': 'TXD', '7': 'RXD', '8': None, '9': None, '10': None, '11': None, '12': None, '13': None, '14': 'SCL', '15': 'SDA', '16': None, '17': None, '18': None, '19': 'GND', '20': '+3V3', '21': None, '22': None, '23': None, '24': None, '25': 'VBAT_SENSE', '26': 'EXP1', '27': 'GPS_TX', '28': 'GPS_RX', '29': 'LORA_NSS', '30': 'SCK', '31': 'MISO', '32': 'MOSI', '33': 'LORA_RST', '34': 'LORA_DIO0', '35': 'LORA_DIO1', '36': None, '37': None, '38': '+3V3', '39': 'GND', '40': 'GND'})
C('C8', '100nF', 241.3, 68.58, '+3V3', 'GND')
C('C11', '10uF', 254.0, 68.58, '+3V3', 'GND', FP['C8'])
R('R4', '1k', 266.7, 137.16, 'LED', 'LED_A')
part('D1', 'Device', 'LED', 'GREEN', 'LED_SMD:LED_0603_1608Metric', 266.7, 152.4, {'2': 'LED_A', '1': 'GND'}, rot=90)
note(165, 118, 'Power the Blue Pill ONLY from its 3V3 pins (TPS63001). 5V pin is not connected.')
note(165, 124, 'Do not fly with USB plugged in. Remove the Blue Pill power LED to save ~2 mA.')
note(165, 130, 'Programming: SWD header at the end of the Blue Pill, or USART1 bootloader (BOOT0=1) via J4.')

# ===== LORA =====
note(300, 22, 'RADIO: RA-02 SX1278 433 MHz', 2.5)
part('U2', 'radiosonde', 'RA-02', 'RA-02', 'RF_Module:Ai-Thinker-Ra-01-LoRa', 340.36, 50.8, {
    '3': '+3V3', '2': 'GND', '12': 'SCK', '13': 'MISO', '14': 'MOSI', '15': 'LORA_NSS', '4': 'LORA_RST',
    '5': 'LORA_DIO0', '6': 'LORA_DIO1', '7': None, '8': None, '10': None, '11': None, '1': None})
C('C13', '10uF', 375.92, 50.8, '+3V3', 'GND', FP['C8'])
C('C14', '100nF', 388.62, 50.8, '+3V3', 'GND')
R('R5', '10k', 375.92, 78.74, '+3V3', 'LORA_NSS')

# ===== PRESSURE =====
note(300, 100, 'PRESSURE: MS5607 (I2C 0x77)', 2.5)
part('U3', 'Sensor_Pressure', 'MS5607-02BA', 'MS5607-02BA03', 'Package_LGA:LGA-8_3x5mm_P1.25mm', 340.36, 124.46, {
    '1': '+3V3', '2': '+3V3', '3': 'GND', '4': 'GND', '6': None, '7': 'SDA', '8': 'SCL'})
C('C15', '100nF', 368.3, 124.46, '+3V3', 'GND')
R('R6', '4.7k', 381.0, 124.46, '+3V3', 'SDA')
R('R7', '4.7k', 393.7, 124.46, '+3V3', 'SCL')

# ===== RTD =====
note(270, 165, 'TEMPERATURE: MAX31865 + PT1000 4-wire', 2.5)
part('U4', 'Sensor_Temperature', 'MAX31865xAP', 'MAX31865AAP+', 'Package_SO:SSOP-20_5.3x7.2mm_P0.65mm', 309.88, 213.36, {
    '1': 'RTD_DRDY', '14': 'MOSI', '15': 'SCK', '16': 'RTD_CS', '17': 'MISO', '2': '+3V3', '3': '+3V3', '13': 'GND', '18': 'GND',
    '4': 'RTD_BIAS', '5': 'RTD_BIAS', '6': 'RTD_REFN', '7': 'RTD_REFN', '8': 'RTD_F+', '9': 'GND', '10': 'RTD_S+', '11': 'RTD_S-', '12': 'RTD_F-'})
R('R8', '4.02k 0.1% 10ppm', 350.52, 200.66, 'RTD_BIAS', 'RTD_REFN')
C('C16', '10nF C0G', 365.76, 223.52, 'RTD_S+', 'RTD_S-')
R('R9', '10M', 375.92, 200.66, 'RTD_S+', 'RTD_BIAS')
C('C17', '100nF', 271.78, 241.3, '+3V3', 'GND')
C('C18', '100nF', 284.48, 241.3, '+3V3', 'GND')
R('R10', '10k', 271.78, 190.5, '+3V3', 'RTD_CS')
part('J5', 'Connector_Generic', 'Conn_01x04', 'PT1000 4-wire', 'Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical', 391.16, 215.9,
     {'1': 'RTD_F+', '2': 'RTD_S+', '3': 'RTD_S-', '4': 'RTD_F-'})

# ===== CONNECTORS =====
note(20, 165, 'CONNECTORS: FTDI (USART1), GPS (USART2), expansion', 2.5)
part('J4', 'Connector_Generic', 'Conn_01x06', 'FTDI 3V3', 'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical', 88.9, 193.04,
     {'1': 'GND', '2': None, '3': '+3V3', '4': 'RXD', '5': 'TXD', '6': None})
part('J6', 'Connector_Generic', 'Conn_01x04', 'GPS (u-blox, airborne mode)', 'Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical', 139.7, 193.04,
     {'1': '+3V3', '2': 'GND', '3': 'GPS_TX', '4': 'GPS_RX'})
part('J7', 'Connector_Generic', 'Conn_01x06', 'EXPANSION', 'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical', 190.5, 193.04,
     {'1': '+3V3', '2': 'GND', '3': 'SDA', '4': 'SCL', '5': 'EXP1', '6': 'EXP2'})
part('H1', 'Mechanical', 'MountingHole', 'M3', 'MountingHole:MountingHole_3.2mm_M3', 38.1, 236.22, {})
part('H2', 'Mechanical', 'MountingHole', 'M3', 'MountingHole:MountingHole_3.2mm_M3', 50.8, 236.22, {})
note(20, 250, 'GPS_TX = PA2 (USART2 TX) -> GPS RX,  GPS_RX = GPS TX -> PA3.   FTDI pin4 = adapter TXO -> PA10 (USART1 RX).  EXP1 = PA1, EXP2 = PB15.')
note(20, 256, 'Electronics are rated -40..+85 C (RA-02 -20..+70 C, Blue Pill clones untested in cold): fly the PCB + batteries in an insulated foam box; only the PT1000 probe outside.')
note(20, 262, 'Footprints from KiCad stock libs. RA-02 uses the Ra-01 SMD-16 footprint (same 17x16 mm, 2.0 mm pitch) - check against your module before ordering.')

# ---------- emit ----------
def xform(px, py, rot):
    t = math.radians(rot); sx, sy = px, -py
    return (round(sx * math.cos(t) + sy * math.sin(t), 4), round(-sx * math.sin(t) + sy * math.cos(t), 4))

def fmt(v): return ('%.4f' % v).rstrip('0').rstrip('.')

labels_at = []
sym_insts = []
for p in parts:
    key = f"{p['lib']}:{p['sym']}"
    base = getsym(p['lib'], p['sym'])
    if key not in libsyms:
        e = copy.deepcopy(base); e[1] = S(key)
        libsyms[key] = e
    ps = pins(base)
    ys = [q['y'] for q in ps] or [0]; xs = [q['x'] for q in ps] or [0]
    is_pwr = p['ref'].startswith('#')
    big = len(ps) > 4
    # property placement
    if big:
        rpos = (p['x'], p['y'] - max(ys) - 2.54, 0); vpos = (p['x'], p['y'] - min(ys) + 2.54, 0)
    elif p['rot'] == 0 and p['sym'] in ('R', 'C', 'L'):
        rpos = (p['x'] + 2.54, p['y'] - 1.27, 0); vpos = (p['x'] + 2.54, p['y'] + 1.27, 0)
    else:
        rpos = (p['x'], p['y'] - max(abs(min(ys)), max(ys), 2.54) - 3.81, 0); vpos = (p['x'], p['y'] + max(abs(min(ys)), max(ys), 2.54) + 3.81, 0)
    just = ['justify', 'left'] if (not big and p['rot'] == 0 and p['sym'] in ('R', 'C', 'L')) else None
    def P(k, v, pos, hide=False):
        eff = ['effects', ['font', ['size', 1.27, 1.27]]]
        if just and k in ('Reference', 'Value'): eff.append(just)
        if hide: eff.append('hide')
        return ['property', S(k), S(v), ['at', fmt(pos[0]), fmt(pos[1]), 0], eff]
    inst = ['symbol', ['lib_id', S(key)], ['at', fmt(p['x']), fmt(p['y']), p['rot']], ['unit', 1],
            ['in_bom', 'no' if is_pwr else 'yes'], ['on_board', 'no' if is_pwr else 'yes'], ['dnp', 'no'], ['uuid', U()],
            P('Reference', p['ref'], rpos, hide=is_pwr), P('Value', p['value'], vpos, hide=is_pwr),
            P('Footprint', p['fp'], (p['x'], p['y'], 0), True), P('Datasheet', prop(base, 'Datasheet') or '~', (p['x'], p['y'], 0), True)]
    for q in ps: inst.append(['pin', S(q['num']), ['uuid', U()]])
    inst.append(['instances', ['project', S(PROJ), ['path', S('/' + ROOT), ['reference', S(p['ref'])], ['unit', 1]]]])
    sym_insts.append(inst)
    # connections
    for q in ps:
        if q['hidden']: continue
        dx, dy = xform(q['x'], q['y'], p['rot'])
        X, Y = round(p['x'] + dx, 4), round(p['y'] + dy, 4)
        if q['num'] not in p['nets']:
            if p['sym'] == 'MountingHole': continue
            raise SystemExit(f"{p['ref']} pin {q['num']} {q['name']} unassigned")
        net = p['nets'][q['num']]
        if net is None:
            items.append(['no_connect', ['at', fmt(X), fmt(Y)], ['uuid', U()]]); continue
        if is_pwr:
            # flag pin points down; put label below
            ang = 270
        else:
            ang = (q['a'] + p['rot'] + 180) % 360
        just2 = {0: 'left', 180: 'right', 90: 'left', 270: 'right'}[ang]
        items.append(['label', S(net), ['at', fmt(X), fmt(Y), ang], ['fields_autoplaced'],
                      ['effects', ['font', ['size', 1.27, 1.27]], ['justify', just2, 'bottom']], ['uuid', U()]])
        labels_at.append((net, X, Y))

sch = ['kicad_sch', ['version', '20230121'], ['generator', 'eeschema'], ['uuid', ROOT], ['paper', S('A3')],
       ['title_block', ['title', S('Radiosonde - Blue Pill + RA-02 LoRa + MS5607 + MAX31865/PT1000')], ['date', S('2026-11-05')], ['rev', S('B')],
        ['comment', 1, S('3xAA, TPS63001 3.3 V buck-boost, target 15 km')]],
       ['lib_symbols'] + list(libsyms.values())] + items + sym_insts + \
      [['sheet_instances', ['path', S('/'), ['page', S('1')]]]]
open(f'{OUT}/{PROJ}.kicad_sch', 'w').write(dump(sch) + '\n')

open(f'{OUT}/sym-lib-table', 'w').write(
    '(sym_lib_table\n  (lib (name "radiosonde")(type "KiCad")(uri "${KIPRJMOD}/radiosonde.kicad_sym")(options "")(descr "Project symbols"))\n)\n')
import json
json.dump({"board": {}, "meta": {"filename": f"{PROJ}.kicad_pro", "version": 1},
           "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
           "sheets": [[ROOT, ""]], "text_variables": {}}, open(f'{OUT}/{PROJ}.kicad_pro', 'w'), indent=2)
print('parts', len(parts), 'labels', len(labels_at))
