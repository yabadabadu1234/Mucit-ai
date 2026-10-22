"""Yerel calisir (KiCad kutuphanesi ister): tasarim verisini ders/veri/*.json olarak yazar. Siteyi ureten uret.py yalniz bu JSON'lari okur."""
import sys, os, json
K = os.path.dirname(os.path.abspath(__file__))
U = os.path.join(K, '..', 'uretim')
sys.path.insert(0, U)
import verici, alici
import pcbnew

def cikar(ad, modul, pcb):
    s = modul.kur()
    parcalar = {}
    aglar = {}
    for c in s.parcalar:
        pins = {}
        for p in c.pins:
            no = p['num']
            if no in pins:
                continue
            pins[no] = {'ad': p['name'], 'ag': c.net.get(no)}
        for no, ag in c.net.items():
            if ag:
                aglar.setdefault(ag, []).append([c.ref, no])
        parcalar[c.ref] = {'ref': c.ref, 'deger': c.deger, 'fp': c.fp, 'sembol': c.libad, 'mpn': c.alanlar.get('MPN', ''),
                           'dnp': c.dnp, 'grup': c.grup, 'pinler': pins}
    b = pcbnew.LoadBoard(pcb)
    konum = {}
    for f in b.GetFootprints():
        bb = f.GetBoundingBox(False, False)
        p = f.GetPosition()
        konum[f.GetReference()] = {'x': round(p.x / 1e6, 2), 'y': round(p.y / 1e6, 2), 'donme': round(f.GetOrientationDegrees(), 1),
                                   'arka': f.GetLayerName() == 'B.Cu', 'g': round(bb.GetWidth() / 1e6, 2), 'y_': round(bb.GetHeight() / 1e6, 2)}
    def kat(l):
        return b.GetLayerName(l)
    padler = []
    cizgiler = []
    for f in b.GetFootprints():
        ref = f.GetReference()
        for p in f.Pads():
            sh = p.GetShape(); sz = p.GetSize(); pos = p.GetPosition()
            t = {pcbnew.PAD_SHAPE_CIRCLE: 'c', pcbnew.PAD_SHAPE_OVAL: 'o', pcbnew.PAD_SHAPE_RECT: 'r', pcbnew.PAD_SHAPE_ROUNDRECT: 'r'}.get(sh, 'r')
            kt = [kat(l) for l in p.GetLayerSet().Seq() if kat(l) in ('F.Cu', 'B.Cu')]
            dz = p.GetDrillSize()
            padler.append({'ref': ref, 'no': p.GetNumber(), 'ag': p.GetNetname(), 't': t, 'x': round(pos.x / 1e6, 3), 'y': round(pos.y / 1e6, 3),
                           'w': round(sz.x / 1e6, 3), 'h': round(sz.y / 1e6, 3), 'a': round(p.GetOrientationDegrees(), 1), 'k': kt,
                           'd': round(dz.x / 1e6, 3), 'npth': p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH})
        for g in f.GraphicalItems():
            ln = kat(g.GetLayer())
            if ln not in ('F.Silkscreen', 'B.Silkscreen', 'F.Courtyard', 'B.Courtyard'):
                continue
            if not hasattr(g, 'GetShape'):
                continue
            tip = g.GetShape()
            if tip == pcbnew.SHAPE_T_SEGMENT:
                a, e = g.GetStart(), g.GetEnd()
                cizgiler.append({'k': ln, 'ref': ref, 'p': [round(a.x / 1e6, 2), round(a.y / 1e6, 2), round(e.x / 1e6, 2), round(e.y / 1e6, 2)]})
            elif tip == pcbnew.SHAPE_T_RECT:
                a, e = g.GetStart(), g.GetEnd()
                x0, y0, x1, y1 = [round(v / 1e6, 2) for v in (a.x, a.y, e.x, e.y)]
                for q in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
                    cizgiler.append({'k': ln, 'ref': ref, 'p': list(q)})
            elif tip == pcbnew.SHAPE_T_CIRCLE:
                c = g.GetCenter(); r = g.GetRadius()
                cizgiler.append({'k': ln, 'ref': ref, 'c': [round(c.x / 1e6, 2), round(c.y / 1e6, 2), round(r / 1e6, 2)]})
    izler = []; viyalar = []
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            p = t.GetPosition()
            viyalar.append({'x': round(p.x / 1e6, 3), 'y': round(p.y / 1e6, 3), 'w': round(t.GetWidth() / 1e6, 2), 'd': round(t.GetDrillValue() / 1e6, 2), 'ag': t.GetNetname()})
        else:
            a, e = t.GetStart(), t.GetEnd()
            izler.append({'k': kat(t.GetLayer()), 'ag': t.GetNetname(), 'w': round(t.GetWidth() / 1e6, 3),
                          'p': [round(a.x / 1e6, 3), round(a.y / 1e6, 3), round(e.x / 1e6, 3), round(e.y / 1e6, 3)]})
    kenar = []
    for g in b.GetDrawings():
        if kat(g.GetLayer()) == 'Edge.Cuts':
            tip = g.GetShape()
            if tip == pcbnew.SHAPE_T_SEGMENT:
                a, e = g.GetStart(), g.GetEnd()
                kenar.append({'t': 's', 'p': [round(a.x / 1e6, 3), round(a.y / 1e6, 3), round(e.x / 1e6, 3), round(e.y / 1e6, 3)]})
            elif tip == pcbnew.SHAPE_T_ARC:
                a, m, e = g.GetStart(), g.GetArcMid(), g.GetEnd()
                kenar.append({'t': 'a', 'p': [round(v / 1e6, 3) for v in (a.x, a.y, m.x, m.y, e.x, e.y)]})
    kb = b.GetBoardEdgesBoundingBox()
    d = {'ad': ad, 'baslik': s.baslik, 'parcalar': parcalar, 'aglar': aglar, 'konum': konum,
         'padler': padler, 'cizgiler': cizgiler, 'izler': izler, 'viyalar': viyalar, 'kenar': kenar, 'kart': {'x': kb.GetX() / 1e6, 'y': kb.GetY() / 1e6, 'g': kb.GetWidth() / 1e6, 'y_': kb.GetHeight() / 1e6}}
    json.dump(d, open(os.path.join(K, 'veri', ad + '.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    print(ad, len(parcalar), 'parca', len(aglar), 'ag', len(konum), 'ayak izi')

cikar('verici', verici, os.path.join(K, '..', 'verici', 'verici.kicad_pcb'))
cikar('alici', alici, os.path.join(K, '..', 'alici', 'alici.kicad_pcb'))
