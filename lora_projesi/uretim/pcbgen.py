import os, sys, math
import xml.etree.ElementTree as ET
import pcbnew

FP = '/usr/share/kicad/footprints/'
EXTRA_FP = os.path.join(os.path.dirname(__file__), 'kutuphane')

def mm(v):
    return pcbnew.FromMM(v)

def vec(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))

def fp_yukle(ad):
    lib, name = ad.split(':')
    for base in (FP, EXTRA_FP + '/'):
        yol = base + lib + '.pretty'
        if os.path.isdir(yol):
            f = pcbnew.FootprintLoad(yol, name)
            if f is not None:
                return f
    raise KeyError(ad)

def netlist_oku(xml):
    t = ET.parse(xml).getroot()
    parcalar = {}
    for c in t.find('components'):
        ref = c.get('ref')
        fp = c.findtext('footprint')
        val = c.findtext('value')
        alan = {f.get('name'): f.text for f in c.iter('field')}
        parcalar[ref] = dict(fp=fp, val=val, alan=alan, dnp=False)
    ag = {}
    for n in t.find('nets'):
        ad = n.get('name')
        ad = ad[1:] if ad.startswith('/') else ad
        ag[ad] = [(x.get('ref'), x.get('pin')) for x in n]
    return parcalar, ag

class Pano:
    def __init__(self, xml, w, h, katman=2, yuvarlak=0.0):
        self.b = pcbnew.NewBoard('x')
        self.w, self.h = w, h
        self.parcalar, self.ag = netlist_oku(xml)
        self.fps = {}
        self.netler = {}
        self._cerceve(w, h, yuvarlak)
        self.katman = katman
        self.b.SetCopperLayerCount(katman)

    def _cerceve(self, w, h, r):
        b = self.b
        def seg(x1, y1, x2, y2):
            s = pcbnew.PCB_SHAPE(b)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(vec(x1, y1)); s.SetEnd(vec(x2, y2))
            s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1))
            b.Add(s)
        def arc(cx, cy, sx, sy, ex, ey):
            s = pcbnew.PCB_SHAPE(b)
            s.SetShape(pcbnew.SHAPE_T_ARC)
            s.SetCenter(vec(cx, cy)); s.SetStart(vec(sx, sy)); s.SetEnd(vec(ex, ey))
            s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1))
            b.Add(s)
        if r <= 0:
            seg(0, 0, w, 0); seg(w, 0, w, h); seg(w, h, 0, h); seg(0, h, 0, 0)
        else:
            seg(r, 0, w - r, 0); seg(w, r, w, h - r); seg(w - r, h, r, h); seg(0, h - r, 0, r)
            arc(w - r, r, w - r, 0, w, r)
            arc(w - r, h - r, w, h - r, w - r, h)
            arc(r, h - r, r, h, 0, h - r)
            arc(r, r, 0, r, r, 0)

    def net(self, ad):
        if ad not in self.netler:
            n = pcbnew.NETINFO_ITEM(self.b, ad)
            self.b.Add(n)
            self.netler[ad] = n
        return self.netler[ad]

    def parca_ekle(self, ref, x, y, rot=0, alt=False):
        p = self.parcalar[ref]
        f = fp_yukle(p['fp'])
        f.SetReference(ref)
        f.SetValue(p['val'] or '')
        f.Value().SetVisible(False)
        f.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        f.Reference().SetTextThickness(mm(0.12))
        self.b.Add(f)
        f.SetPosition(vec(x, y))
        if alt:
            f.Flip(vec(x, y), True)
        f.SetOrientationDegrees(rot)
        self.fps[ref] = f
        return f

    def netleri_ata(self):
        for ad, nodes in self.ag.items():
            if ad.startswith('unconnected-'):
                continue
            n = self.net(ad)
            for ref, pin in nodes:
                f = self.fps.get(ref)
                if f is None:
                    continue
                pads = [pd for pd in f.Pads() if pd.GetNumber() == pin]
                assert pads, (ref, pin)
                for pd in pads:
                    pd.SetNet(n)

    def delik(self, x, y, d=3.2):
        f = pcbnew.FootprintLoad(FP + 'MountingHole.pretty', 'MountingHole_3.2mm_M3' if d > 3 else 'MountingHole_2.7mm_M2.5')
        self.b.Add(f)
        f.SetPosition(vec(x, y))
        f.SetReference('H%d' % (len([1 for _ in self.b.GetFootprints()])))
        return f

    def kaydet(self, yol):
        self.b.Save(yol)
