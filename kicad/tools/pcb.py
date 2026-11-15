import sys, pcbnew
sys.path.insert(0, '/home/claude/gen')
from sexp import parse, child

D = '/home/claude/radiosonde'
FPROOT = '/usr/share/kicad/footprints'
net = parse(open(f'{D}/radiosonde.net').read())[0]

comps = {}
for c in child(child(net, 'components')[0], 'comp'):
    ref = child(c, 'ref')[0][1][1]
    fp = child(c, 'footprint')[0][1][1] if child(c, 'footprint') else ''
    val = child(c, 'value')[0][1][1]
    comps[ref] = (fp, val)
padnet = {}
netnames = []
for n in child(child(net, 'nets')[0], 'net'):
    name = child(n, 'name')[0][1][1]; netnames.append(name)
    for x in child(n, 'node'):
        padnet[(child(x, 'ref')[0][1][1], child(x, 'pin')[0][1][1])] = name

W, H = 90.0, 60.0
mm = pcbnew.FromMM
b = pcbnew.BOARD()
nets = {}
for nm in netnames:
    ni = pcbnew.NETINFO_ITEM(b, nm); b.Add(ni); nets[nm] = ni

# placement (mm, rotation deg)
P = {
 'J1': (6, 8, 90), 'Q1': (14, 6, 0), 'SW1': (22, 4, 0), 'C1': (10, 15, 0), 'C2': (10, 18, 0),
 'U5': (22, 13, 0), 'L1': (30, 14, 0), 'C3': (36, 11, 90), 'C4': (36, 15, 90),
 'R1': (44, 6, 90), 'R2': (47, 6, 90), 'C5': (50, 6, 90),
 'U1': (12, 33, 0), 'C8': (64, 21, 90), 'C11': (64, 25, 90),
 'R4': (40, 48, 0), 'D1': (44, 48, 0),
 'U2': (76, 14, 0), 'C13': (65, 6, 90), 'C14': (65, 10, 90), 'R5': (65, 15, 90),
 'U3': (60, 52, 0), 'C15': (60, 47, 0), 'R6': (65, 50, 90), 'R7': (68, 50, 90),
 'U4': (72, 38, 0), 'R8': (80, 34, 90), 'R9': (80, 39, 90), 'C16': (80, 44, 90),
 'C17': (66, 33, 90), 'C18': (66, 37, 90), 'R10': (66, 42, 90), 'J5': (87, 40, 90),
 'J4': (5, 36, 0), 'J6': (24, 54, 0), 'J7': (36, 54, 90),
 'H1': (3.5, 56.5, 0), 'H2': (86.5, 56.5, 0),
}
missing = []
for ref, (fp, val) in comps.items():
    if not fp: continue
    lib, name = fp.split(':')
    m = pcbnew.FootprintLoad(f'{D}/radiosonde.pretty' if lib == 'radiosonde' else f'{FPROOT}/{lib}.pretty', name)
    if m is None: missing.append(fp); continue
    m.SetReference(ref); m.SetValue(val)
    x, y, r = P.get(ref, (45, 30, 0))
    m.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); m.SetOrientationDegrees(r)
    for pad in m.Pads():
        nm = padnet.get((ref, pad.GetNumber()))
        if nm: pad.SetNet(nets[nm])
    b.Add(m)

# outline
pts = [(0, 0), (W, 0), (W, H), (0, H)]
for i in range(4):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(mm(pts[i][0]), mm(pts[i][1])))
    s.SetEnd(pcbnew.VECTOR2I(mm(pts[(i + 1) % 4][0]), mm(pts[(i + 1) % 4][1])))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)

# GND pours both layers
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(nets['/GND'])
    ol = z.Outline(); ol.NewOutline()
    for x, y in pts: ol.Append(mm(x + 0.3 if x == 0 else x - 0.3), mm(y + 0.3 if y == 0 else y - 0.3))
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    b.Add(z)

t = pcbnew.PCB_TEXT(b); t.SetText('RADIOSONDE rev B (Blue Pill)'); t.SetLayer(pcbnew.F_SilkS)
t.SetPosition(pcbnew.VECTOR2I(mm(45), mm(3))); t.SetTextSize(pcbnew.VECTOR2I(mm(1.5), mm(1.5))); b.Add(t)

ds = b.GetDesignSettings(); ds.SetCopperLayerCount(2)
b.Save(f'{D}/radiosonde.kicad_pcb')
print('footprints', len(b.GetFootprints()), 'missing', missing)
