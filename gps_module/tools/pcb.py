"""Build gps_module.kicad_pcb from gps_module.net. Run with KiCad's Python:

  "C:/Program Files/KiCad/10.0/bin/python.exe" tools/pcb.py

All coordinates are millimetres in the top view. The outline, pin row and hole match the
GPS_NEO6M_5pin footprint (J6) on the radiosonde: pin row at x 2.159, hole at (24.765, 23.368).
"""
import math, os, sys
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import parse, child

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPROOT = 'C:/Program Files/KiCad/10.0/share/kicad/footprints'
W, H = 27.559, 26.416
PIN_X, PIN1_Y = 2.159, 8.001
HOLE = (24.765, 23.368)
FEED = (15.5, 10.5)          # patch feed pin
mm = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(mm(x), mm(y))

net = parse(open(f'{D}/gps_module.net', encoding='utf-8').read())[0]
comps, padnet, netnames = {}, {}, []
for c in child(child(net, 'components')[0], 'comp'):
    ref = child(c, 'ref')[0][1][1]
    comps[ref] = (child(c, 'footprint')[0][1][1], child(c, 'value')[0][1][1])
for n in child(child(net, 'nets')[0], 'net'):
    name = child(n, 'name')[0][1][1]; netnames.append(name)
    for x in child(n, 'node'):
        padnet[(child(x, 'ref')[0][1][1], child(x, 'pin')[0][1][1])] = name

b = pcbnew.BOARD()
nets = {}
for nm in netnames:
    ni = pcbnew.NETINFO_ITEM(b, nm); b.Add(ni); nets[nm] = ni

# ref: (x, y, rotation, side)   side B = bottom
P = {
    'J1': (PIN_X, PIN1_Y, 180, 'B'), 'H1': (HOLE[0], HOLE[1], 0, 'F'), 'AE1': (FEED[0], FEED[1], 0, 'F'),
    'U1': (11.5, 19.5, 0, 'B'),
    'R2': (19.125, 16.2, 0, 'B'), 'R1': (18.3, 13.95, 90, 'B'), 'J2': (23.325, 16.2, 0, 'B'),
    'L1': (19.95, 18.45, 270, 'B'), 'R3': (19.95, 21.45, 270, 'B'),
    'FB1': (4.75, 16.9, 90, 'B'), 'C2': (4.75, 13.9, 90, 'B'), 'C1': (6.9, 12.5, 90, 'B'),
}
# reference labels: None = hidden (no room), (x, y) = moved
REFPOS = {'R1': None, 'R2': None, 'L1': None, 'R3': None, 'FB1': None, 'H1': None, 'AE1': (15.5, 4.5),
          'C1': (6.9, 10.0), 'C2': (4.75, 11.7), 'J2': (23.3, 12.9), 'U1': (11.5, 25.4), 'J1': None}
fps = {}
for ref, (fp, val) in comps.items():
    lib, name = fp.split(':')
    m = pcbnew.FootprintLoad(f'{D}/gps_module.pretty' if lib == 'gps_module' else f'{FPROOT}/{lib}.pretty', name)
    if m is None:
        sys.exit('missing footprint ' + fp)
    m.SetReference(ref); m.SetValue(val)
    m.SetFPID(pcbnew.LIB_ID(lib, name))
    x, y, r, side = P[ref]
    b.Add(m)
    m.SetPosition(V(x, y))
    if side == 'B':
        m.Flip(V(x, y), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    m.SetOrientationDegrees(r)
    for pad in m.Pads():
        nm = padnet.get((ref, pad.GetNumber()))
        if nm:
            pad.SetNet(nets[nm])
    fps[ref] = m
    if ref in ('R2', 'L1'):
        m.SetDNP(True)
    if ref == 'H1':
        m.SetExcludedFromBOM(True)
    if ref == 'AE1':
        for pad_ in m.Pads():
            pad_.SetRemoveUnconnected(True); pad_.SetKeepTopBottom(False)
    rp = REFPOS.get(ref, 'keep')
    if rp is None:
        m.Reference().SetVisible(False)
    elif rp != 'keep':
        m.Reference().SetPosition(V(*rp[:2])); m.Reference().SetTextAngleDegrees(0)
    m.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); m.Reference().SetTextThickness(mm(0.12))


def pad(ref, key):
    """Pad centre by pad number, or by net name when key starts with '/'."""
    for p in fps[ref].Pads():
        if (key.startswith('/') and p.GetNetname() == key) or p.GetNumber() == key:
            return (pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y))
    sys.exit(f'no pad {ref} {key}')


def track(netname, pts, w, layer=pcbnew.B_Cu):
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(V(*a)); t.SetEnd(V(*c)); t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(nets[netname]); b.Add(t)


def via(netname, x, y, size=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetDrill(mm(drill)); v.SetNet(nets[netname])
    try:
        v.SetWidth(pcbnew.F_Cu, mm(size))
    except TypeError:
        v.SetWidth(mm(size))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); b.Add(v)


if '--pads' in sys.argv:
    for ref in fps:
        for p in fps[ref].Pads():
            print(ref, p.GetNumber(), p.GetNetname(), round(pcbnew.ToMM(p.GetPosition().x), 3), round(pcbnew.ToMM(p.GetPosition().y), 3))

# ---- RF path, 0.8 mm wide and as short as the parts allow (bottom layer)
RF = 0.8
rf_in = pad('U1', '11')
track('/RF_IN', [rf_in, pad('R2', '/RF_IN')], RF)
track('/RF_IN', [pad('R2', '/RF_IN'), pad('R1', '/RF_IN')], RF)
track('/ANT_PATCH', [pad('R1', '/ANT_PATCH'), FEED], RF)
track('/ANT_EXT', [pad('R2', '/ANT_EXT'), pad('J2', '1')], RF)
track('/ANT_EXT', [pad('R2', '/ANT_EXT'), pad('L1', '/ANT_EXT')], 0.4)
# ---- antenna bias
bias = pad('L1', '/BIAS')
track('/BIAS', [bias, pad('R3', '/BIAS')], 0.3)
vrf = pad('U1', '14'); r3v = pad('R3', '/VCC_RF')
track('/VCC_RF', [vrf, (17.9, vrf[1]), (18.6, vrf[1] + 0.7), (18.6, r3v[1]), r3v], 0.3)
# ---- supply
fbv, fbf = pad('FB1', '/VCC'), pad('FB1', '/VCC_F')
track('/VCC', [pad('J1', '5'), fbv], 0.4)
p8, p7, p6 = pad('U1', '8'), pad('U1', '7'), pad('U1', '6')
track('/VCC_F', [fbf, p8, p7, p6], 0.4)
c2f, c1f = pad('C2', '/VCC_F'), pad('C1', '/VCC_F')
track('/VCC_F', [fbf, c2f], 0.4)
track('/VCC_F', [c2f, (c1f[0] - 1.2, c1f[1] + 0.9), c1f], 0.4)
# ---- UART and PPS: top-layer lanes in the strip left of the patch, then a via down to U1
for netname, jpin, upin, lane in (('/PPS', '1', '4', 5.0), ('/TXD', '2', '2', 4.3), ('/RXD', '3', '3', 3.6)):
    j, u = pad('J1', jpin), pad('U1', upin)
    track(netname, [j, (lane - 0.4, j[1]), (lane, j[1] + 0.4), (lane, u[1])], 0.25, pcbnew.F_Cu)
    via(netname, lane, u[1])
    track(netname, [(lane, u[1]), u], 0.25)
# ---- ground stitching between the top plane and the bottom pour
for x, y in ((8, 2.5), (14, 2.5), (20, 2.5), (25.5, 4), (25.5, 10), (10, 8), (21, 8), (12, 12.5), (22, 12.5), (25.8, 16.2),
             (14.3, 25), (20, 24.5), (8, 25.3), (1.5, 3), (1.5, 23)):
    via('/GND', x, y)

# ---- outline
pts = [(0, 0), (W, 0), (W, H), (0, H)]
for i in range(4):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(V(*pts[i])); s.SetEnd(V(*pts[(i + 1) % 4]))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)

# ---- ground on both layers; the top one is the patch ground plane
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(nets['/GND'])
    ol = z.Outline(); ol.NewOutline()
    for x, y in ((0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)):
        ol.Append(mm(x), mm(y))
    z.SetLocalClearance(mm(0.25)); z.SetMinThickness(mm(0.2)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.25)); z.SetThermalReliefSpokeWidth(mm(0.4))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)

# ---- no top copper around the feed pin
k = pcbnew.ZONE(b); k.SetIsRuleArea(True); k.SetLayer(pcbnew.F_Cu); k.SetZoneName('FEED_CLEARANCE')
k.SetDoNotAllowZoneFills(True); k.SetDoNotAllowTracks(True); k.SetDoNotAllowVias(True); k.SetDoNotAllowPads(False); k.SetDoNotAllowFootprints(False)
ol = k.Outline(); ol.NewOutline()
for i in range(24):
    a = 2 * math.pi * i / 24
    ol.Append(mm(FEED[0] + 1.9 * math.cos(a)), mm(FEED[1] + 1.9 * math.sin(a)))
b.Add(k)


def text(s, x, y, layer, size=0.8, rot=0, just=None):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(layer); t.SetPosition(V(x, y))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(size * 0.15))
    if rot:
        t.SetTextAngleDegrees(rot)
    if just is not None:
        t.SetHorizJustify(just)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    b.Add(t)


for i, name in enumerate(('PPS', 'TXD', 'RXD', 'GND', 'VCC')):
    text(name, 3.3, PIN1_Y + 2.54 * i, pcbnew.F_SilkS, 0.8, just=pcbnew.GR_TEXT_H_ALIGN_LEFT)
# all legend text on the front, in the strip below the patch antenna
L = pcbnew.GR_TEXT_H_ALIGN_LEFT
text('CM-GNSS-425 rev A', 0.9, 20.9, pcbnew.F_SilkS, 1.0, just=L)
# product label on the back, in the clear strip above the parts
text('CM-GNSS-425', 15, 1.7, pcbnew.B_SilkS, 1.2)
text('Charming Electronic', 15, 3.6, pcbnew.B_SilkS, 0.9)
text('Made in Vietnam', 15, 5.2, pcbnew.B_SilkS, 0.9)
text('R1 (by feed pin) = patch', 0.9, 22.5, pcbnew.F_SilkS, 0.8, just=L)
text('R2 (by u.FL) = ext. antenna', 0.9, 23.9, pcbnew.F_SilkS, 0.8, just=L)
text('L1 (below R2) = active ant. only', 0.9, 25.3, pcbnew.F_SilkS, 0.8, just=L)

b.GetDesignSettings().SetCopperLayerCount(2)
pcbnew.SaveBoard(f'{D}/gps_module.kicad_pcb', b)
# filling a board that was never loaded from disk crashes pcbnew, so reload first
b = pcbnew.LoadBoard(f'{D}/gps_module.kicad_pcb')
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(f'{D}/gps_module.kicad_pcb', b)
print('footprints', len(b.GetFootprints()), 'tracks', len(b.GetTracks()))
