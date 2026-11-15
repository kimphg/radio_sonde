"""Generate gps_module.kicad_sch (label-connected), the patch footprint and the library tables.

Run with any Python 3:  python tools/build.py
Then tools/pcb.py (KiCad's Python) builds the board from the exported netlist.
"""
import copy, math, os, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import *

PROJ = 'gps_module'
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = lambda: str(uuid.uuid4())
ROOT = 'a6f0c6e2-5a39-4c55-9d0b-6d2f3a1e7b10'

parts, items, libsyms = [], [], {}
R0603, C0603, C0805 = 'Resistor_SMD:R_0603_1608Metric', 'Capacitor_SMD:C_0603_1608Metric', 'Capacitor_SMD:C_0805_2012Metric'


def part(ref, lib, sym, value, fp, x, y, nets, rot=0, lcsc='', mpn='', dnp=False):
    parts.append(dict(ref=ref, lib=lib, sym=sym, value=value, fp=fp, x=x, y=y, rot=rot, nets=nets, lcsc=lcsc, mpn=mpn, dnp=dnp))


def note(x, y, txt, size=1.5):
    items.append(['text', S(txt), ['at', x, y, 0], ['effects', ['font', ['size', size, size]] + (['bold'] if size > 2 else []), ['justify', 'left']], ['uuid', U()]])


# ===== connector to the radiosonde (J6 there): same pin order as the NEO-6M module =====
note(25, 30, 'TO RADIOSONDE J6', 2.5)
part('J1', 'Connector_Generic', 'Conn_01x05', 'PPS TXD RXD GND VCC', 'Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical', 40.64, 60.96,
     {'1': 'PPS', '2': 'TXD', '3': 'RXD', '4': 'GND', '5': 'VCC'})
note(25, 80, 'Pin header on the bottom side, pins down into the socket.')
note(25, 85, 'TXD = module output, RXD = module input, 3.3 V logic.')

# ===== supply filter =====
note(25, 105, 'SUPPLY FILTER', 2.5)
part('FB1', 'Device', 'FerriteBead', '600R', 'Inductor_SMD:L_0603_1608Metric', 40.64, 127, {'1': 'VCC', '2': 'VCC_F'}, lcsc='C19330', mpn='BLM18AG601SN1D')
part('C1', 'Device', 'C', '10uF 10V', C0805, 55.88, 127, {'1': 'VCC_F', '2': 'GND'}, lcsc='C95841', mpn='CL21B106KOQNNNE')
part('C2', 'Device', 'C', '100nF', C0603, 68.58, 127, {'1': 'VCC_F', '2': 'GND'}, lcsc='C1591', mpn='CL10B104KB8NNNC')
part('#FLG1', 'power', 'PWR_FLAG', 'PWR_FLAG', '', 81.28, 127, {'1': 'VCC_F'})
part('#FLG2', 'power', 'PWR_FLAG', 'PWR_FLAG', '', 93.98, 127, {'1': 'GND'})

# ===== receiver =====
note(110, 30, 'GNSS RECEIVER: u-blox MAX-M10S', 2.5)
part('U1', 'RF_GPS', 'MAX-M10S', 'MAX-M10S-00B', 'RF_GPS:ublox_MAX', 139.7, 68.58, {
    '1': 'GND', '10': 'GND', '12': 'GND', '2': 'TXD', '3': 'RXD', '4': 'PPS', '5': None,
    '6': 'VCC_F', '7': 'VCC_F', '8': 'VCC_F', '9': None, '11': 'RF_IN', '13': None, '14': 'VCC_RF',
    '15': None, '16': None, '17': None, '18': None}, lcsc='C4153167', mpn='MAX-M10S-00B')
note(110, 100, 'V_BCKP tied to VCC: no backup supply, cold start at every power-on.')
note(110, 105, 'VIO_SEL open = 3.3 V I/O.  RF_IN has an internal DC block, LNA and SAW filter.')
note(110, 110, 'Default: 9600 baud NMEA, portable model. Firmware must select airborne <1g for flight.')

# ===== antenna selection =====
note(200, 30, 'ANTENNA: fit R1 (patch) OR R2 (u.FL), never both', 2.5)
part('R1', 'Device', 'R', '0R', R0603, 215.9, 55.88, {'1': 'RF_IN', '2': 'ANT_PATCH'}, rot=90)
part('AE1', 'Device', 'Antenna', '18x18 mm L1 patch', 'gps_module:Patch_18x18_TH', 233.68, 50.8, {'1': 'ANT_PATCH'}, lcsc='C784395', mpn='BWGNSCNX18-18W4')
part('R2', 'Device', 'R', '0R DNP', R0603, 215.9, 81.28, {'1': 'RF_IN', '2': 'ANT_EXT'}, rot=90, dnp=True)
part('J2', 'Connector', 'Conn_Coaxial', 'U.FL', 'Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical', 238.76, 81.28, {'1': 'ANT_EXT', '2': 'GND'}, lcsc='C88374', mpn='U.FL-R-SMT-1(80)')
note(200, 105, 'ACTIVE ANTENNA BIAS (u.FL only): fit L1 to feed VCC_RF to the antenna')
part('L1', 'Device', 'L', '27nH DNP', 'Inductor_SMD:L_0603_1608Metric', 215.9, 127, {'1': 'ANT_EXT', '2': 'BIAS'}, dnp=True)
part('R3', 'Device', 'R', '10R', R0603, 231.14, 127, {'1': 'BIAS', '2': 'VCC_RF'})
note(200, 150, 'Leave L1 out for a passive antenna: some are a DC short and would load VCC_RF.')

part('H1', 'Mechanical', 'MountingHole', '3 mm', 'MountingHole:MountingHole_3mm', 40.64, 160, {})


# ---------- emit ----------
def xform(px, py, rot):
    t = math.radians(rot); sx, sy = px, -py
    return (round(sx * math.cos(t) + sy * math.sin(t), 4), round(-sx * math.sin(t) + sy * math.cos(t), 4))


def fmt(v):
    return ('%.4f' % v).rstrip('0').rstrip('.')


sym_insts = []
nlabels = 0
for p in parts:
    key = f"{p['lib']}:{p['sym']}"
    base = flatten(p['lib'], p['sym'])
    if key not in libsyms:
        e = copy.deepcopy(base); e[1] = S(key); libsyms[key] = e
    ps = pins(base)
    ys = [q['y'] for q in ps] or [0]
    is_pwr = p['ref'].startswith('#')
    big = len(ps) > 4
    small = p['sym'] in ('R', 'C', 'L', 'FerriteBead')
    if big:
        rpos = (p['x'], p['y'] - max(ys) - 2.54); vpos = (p['x'], p['y'] - min(ys) + 2.54)
    elif small and p['rot'] == 0:
        rpos = (p['x'] + 2.54, p['y'] - 1.27); vpos = (p['x'] + 2.54, p['y'] + 1.27)
    else:
        d = max(abs(min(ys)), max(ys), 2.54) + 3.81
        rpos = (p['x'], p['y'] - d); vpos = (p['x'], p['y'] + d)
    just = ['justify', 'left'] if (small and p['rot'] == 0) else None

    def P(k, v, pos, hide=False):
        eff = ['effects', ['font', ['size', 1.27, 1.27]]]
        if just and k in ('Reference', 'Value'):
            eff.append(just)
        if hide:
            eff.append('hide')
        return ['property', S(k), S(v), ['at', fmt(pos[0]), fmt(pos[1]), 0], eff]

    here = (p['x'], p['y'])
    inst = ['symbol', ['lib_id', S(key)], ['at', fmt(p['x']), fmt(p['y']), p['rot']], ['unit', 1],
            ['in_bom', 'no' if is_pwr else 'yes'], ['on_board', 'no' if is_pwr else 'yes'], ['dnp', 'yes' if p['dnp'] else 'no'], ['uuid', U()],
            P('Reference', p['ref'], rpos, hide=is_pwr), P('Value', p['value'], vpos, hide=is_pwr),
            P('Footprint', p['fp'], here, True), P('Datasheet', prop(base, 'Datasheet') or '~', here, True)]
    if p['lcsc']:
        inst += [P('LCSC', p['lcsc'], here, True), P('MPN', p['mpn'], here, True)]
    for q in ps:
        inst.append(['pin', S(q['num']), ['uuid', U()]])
    inst.append(['instances', ['project', S(PROJ), ['path', S('/' + ROOT), ['reference', S(p['ref'])], ['unit', 1]]]])
    sym_insts.append(inst)
    for q in ps:
        if q['hidden']:
            continue
        dx, dy = xform(q['x'], q['y'], p['rot'])
        X, Y = round(p['x'] + dx, 4), round(p['y'] + dy, 4)
        if q['num'] not in p['nets']:
            if p['sym'] == 'MountingHole':
                continue
            raise SystemExit(f"{p['ref']} pin {q['num']} {q['name']} unassigned")
        net = p['nets'][q['num']]
        if net is None:
            items.append(['no_connect', ['at', fmt(X), fmt(Y)], ['uuid', U()]]); continue
        ang = 270 if is_pwr else (q['a'] + p['rot'] + 180) % 360
        j2 = {0: 'left', 180: 'right', 90: 'left', 270: 'right'}[ang]
        items.append(['label', S(net), ['at', fmt(X), fmt(Y), ang], ['fields_autoplaced'],
                      ['effects', ['font', ['size', 1.27, 1.27]], ['justify', j2, 'bottom']], ['uuid', U()]])
        nlabels += 1

sch = ['kicad_sch', ['version', '20230121'], ['generator', 'eeschema'], ['uuid', ROOT], ['paper', S('A4')],
       ['title_block', ['title', S('GPS module for the radiosonde - u-blox MAX-M10S, patch or u.FL antenna')], ['date', S('2026-11-13')], ['rev', S('A')],
        ['comment', 1, S('Plugs into radiosonde J6: 27.56 x 26.42 mm, 5 pins at 2.54 mm, one 3 mm hole')]],
       ['lib_symbols'] + list(libsyms.values())] + items + sym_insts + [['sheet_instances', ['path', S('/'), ['page', S('1')]]]]
open(f'{OUT}/{PROJ}.kicad_sch', 'w', encoding='utf-8').write(dump(sch) + '\n')

# ---------- patch antenna footprint: origin at the feed pin ----------
fp = '''(footprint "Patch_18x18_TH" (version 20221018) (generator pcbnew) (layer "F.Cu")
  (descr "18 x 18 x 4 mm GPS L1 ceramic patch with a through-hole feed pin. Origin at the pin, drawn with the pin at the patch centre. The pad ring is removed from the top layer and has no top mask opening, so the patch ground face cannot short to it.")
  (tags "GPS patch antenna")
  (attr through_hole)
  (fp_text reference "REF**" (at 0 -10.2) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
  (fp_text value "Patch_18x18_TH" (at 0 10.4) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
  (fp_rect (start -9 -9) (end 9 9) (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS"))
  (fp_rect (start -9 -9) (end 9 9) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))
  (fp_rect (start -9.25 -9.25) (end 9.25 9.25) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))
  (pad "1" thru_hole circle (at 0 0) (size 2.2 2.2) (drill 1.3) (layers "*.Cu" "B.Mask") (remove_unused_layers yes) (keep_end_layers no))
)
'''
open(f'{OUT}/{PROJ}.pretty/Patch_18x18_TH.kicad_mod', 'w', encoding='utf-8').write(fp)
open(f'{OUT}/fp-lib-table', 'w').write('(fp_lib_table\n  (lib (name "gps_module")(type "KiCad")(uri "${KIPRJMOD}/gps_module.pretty")(options "")(descr "Project footprints"))\n)\n')
print('parts', len(parts), 'labels', nlabels)
