import os, sys, subprocess, re
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from sexp import parse, find, first
from pcbgen import mm, vec

FR = '/tmp/claude-0/tools/freerouting.jar'

def dsn_yaz(b, yol, siniflar=None):
    ok = pcbnew.ExportSpecctraDSN(b, yol)
    assert ok
    t = open(yol).read()
    if siniflar:
        # siniflar: {sinif_adi: (genislik_um, [net adlari])}
        for ad, (gen, netler) in siniflar.items():
            if not netler:
                continue
            blok = '  (class %s %s\n    (circuit\n      (use_via "Via[0-3]_600:300_um")\n    )\n    (rule\n      (width %d)\n      (clearance 150)\n    )\n  )\n' % (ad, ' '.join('"%s"' % n if not n.startswith('"') else n for n in netler), gen * 10)
            t = t.replace('  )\n  (wiring', blok + '  )\n  (wiring', 1) if False else t
    open(yol, 'w').write(t)

def fr_calistir(dsn, ses, gecis=40, zaman=900):
    if os.path.exists(ses):
        os.remove(ses)
    cmd = ['xvfb-run', '-a', 'java', '-jar', FR, '-de', dsn, '-do', ses, '-mp', str(gecis)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=zaman)
    return p.stdout + p.stderr

def ses_uygula(b, ses):
    root = parse(open(ses).read())
    pl = first(root, 'placement')
    res = first(pl, 'resolution')
    birim = 10.0  # um 10 -> 0.1 um
    nm_per = 1000.0 / birim  # nm per unit
    ro = first(root, 'routes')
    net_out = first(ro, 'network_out')
    n_w = n_v = 0
    for net in find(net_out, 'net'):
        ad = str(net[1])
        ni = b.FindNet(ad)
        assert ni is not None, ad
        for w in find(net, 'wire'):
            path = first(w, 'path')
            layer = str(path[1]); gen = float(path[2])
            pts = [float(v) for v in path[3:]]
            pts = [(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(b)
                t.SetStart(pcbnew.VECTOR2I(int(x1 * nm_per), int(-y1 * nm_per)))
                t.SetEnd(pcbnew.VECTOR2I(int(x2 * nm_per), int(-y2 * nm_per)))
                t.SetWidth(int(gen * nm_per))
                t.SetLayer(b.GetLayerID(layer))
                t.SetNet(ni)
                b.Add(t); n_w += 1
        for v in find(net, 'via'):
            nm = str(v[1])
            x, y = float(v[2]), float(v[3])
            m = re.search(r'_(\d+):(\d+)_um', nm)
            dia, drl = int(m.group(1)), int(m.group(2))
            via = pcbnew.PCB_VIA(b)
            via.SetPosition(pcbnew.VECTOR2I(int(x * nm_per), int(-y * nm_per)))
            via.SetWidth(dia * 1000); via.SetDrill(drl * 1000)
            via.SetViaType(pcbnew.VIATYPE_THROUGH)
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetNet(ni)
            b.Add(via); n_v += 1
    return n_w, n_v

def zone(b, net, layer, w, h, margin=0.0, thermal=True):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetNet(b.FindNet(net))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in [(margin, margin), (w - margin, margin), (w - margin, h - margin), (margin, h - margin)]:
        ol.Append(mm(x), mm(y))
    z.SetMinThickness(mm(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
    z.SetLocalClearance(mm(0.3))
    b.Add(z)
    return z

def doldur(b):
    zf = pcbnew.ZONE_FILLER(b)
    zf.Fill(b.Zones())

def drc(b, yol):
    pcbnew.WriteDRCReport(b, yol, pcbnew.EDA_UNITS_MILLIMETRES, True)
    return open(yol).read()

def drc_ozet(rep, goster=12):
    import collections
    bloklar = re.split(r'\n(?=\[)', rep)
    sayac = collections.Counter()
    ornek = collections.defaultdict(list)
    for bl in bloklar:
        m = re.match(r'\[(\w+)\]', bl)
        if not m:
            continue
        sev = 'error' if 'Severity: error' in bl else 'warning'
        k = m.group(1) + ('' if sev == 'error' else '(w)')
        sayac[k] += 1
        if len(ornek[k]) < goster:
            ornek[k].append(' | '.join(x.strip() for x in bl.split('\n')[1:]))
    return sayac, ornek

import math

def _nokta_dikdortgen(px, py, x0, y0, x1, y1):
    dx = max(x0 - px, 0, px - x1)
    dy = max(y0 - py, 0, py - y1)
    return math.hypot(dx, dy)

def _nokta_dogru(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    l2 = vx * vx + vy * vy
    if l2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / l2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))

def _dogru_dikdortgen(ax, ay, bx, by, x0, y0, x1, y1):
    n = 24
    m = 1e9
    for i in range(n + 1):
        t = i / n
        m = min(m, _nokta_dikdortgen(ax + t * (bx - ax), ay + t * (by - ay), x0, y0, x1, y1))
    return m

MERKEZ = {}

def plane_via(b, aglar, W, H, via_d=0.5, via_drill=0.25, klirens=0.15, iz=0.25, kenar=0.6, sadece=None):
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    I2 = pcbnew.In2_Cu
    def ob_topla():
        obs = {F: [], B: [], I2: []}
        for pad in b.GetPads():
            bb = pad.GetBoundingBox()
            r = (bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6)
            for L in (F, B, I2):
                if pad.IsOnLayer(L):
                    obs[L].append(('r', r, pad.GetNetCode(), id(pad)))
        for t in b.GetTracks():
            if t.GetClass() == 'PCB_VIA':
                p = t.GetPosition(); rr = t.GetWidth() / 2e6
                for L in (F, B, I2):
                    obs[L].append(('c', (p.x / 1e6, p.y / 1e6, rr), t.GetNetCode(), 0))
            else:
                L = t.GetLayer()
                if L in obs:
                    s, e = t.GetStart(), t.GetEnd()
                    obs[L].append(('s', (s.x / 1e6, s.y / 1e6, e.x / 1e6, e.y / 1e6, t.GetWidth() / 2e6), t.GetNetCode(), 0))
        return obs
    kutular = []
    for fp in b.GetFootprints():
        for z in fp.Zones():
            if z.GetIsRuleArea():
                kutular.append(z)
    def dist_ob(o, px, py):
        k, d = o[0], o[1]
        if k == 'r': return _nokta_dikdortgen(px, py, *d)
        if k == 'c': return math.hypot(px - d[0], py - d[1]) - d[2]
        return _nokta_dogru(px, py, *d[:4]) - d[4]
    def dist_ob_dogru(o, ax, ay, bx, by):
        k, d = o[0], o[1]
        if k == 'r': return _dogru_dikdortgen(ax, ay, bx, by, *d)
        if k == 'c':
            return _nokta_dogru(d[0], d[1], ax, ay, bx, by) - d[2]
        m = 1e9
        n = 40
        for i in range(n + 1):
            t = i / n
            m = min(m, _nokta_dogru(ax + t * (bx - ax), ay + t * (by - ay), *d[:4]))
        return m - d[4]
    sonuc = {'eklendi': 0, 'bulunamadi': []}
    yaricap = via_d / 2
    def delikler():
        h = []
        for pad in b.GetPads():
            dz = pad.GetDrillSize()
            if dz.x > 0:
                p = pad.GetPosition(); h.append((p.x / 1e6, p.y / 1e6, dz.x / 2e6))
        for t in b.GetTracks():
            if t.GetClass() == 'PCB_VIA':
                p = t.GetPosition(); h.append((p.x / 1e6, p.y / 1e6, t.GetDrillValue() / 2e6))
        return h
    for ad in aglar:
        ni = b.FindNet(ad)
        nc = ni.GetNetCode()
        pads = [p for p in b.GetPads() if p.GetNetCode() == nc and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
        if sadece:
            pads = [q for q in pads if (q.GetParent().GetReference(), q.GetNumber()) in sadece]
        for pad in pads:
            obs = ob_topla()
            dl = delikler()
            L = F if pad.IsOnLayer(F) else B
            c = pad.GetPosition(); cx, cy = c.x / 1e6, c.y / 1e6
            # zaten bir via ile ayni agda ve cok yakin mi
            ok = None
            for r in (0.9, 1.1, 1.4, 1.8, 2.3, 3.0, 4.0):
                ks = list(range(16))
                mk = MERKEZ.get(pad.GetParent().GetReference())
                if mk:
                    ta = math.atan2(mk[1] - cy, mk[0] - cx)
                    ks.sort(key=lambda kk: abs(math.atan2(math.sin(2 * math.pi * kk / 16 - ta), math.cos(2 * math.pi * kk / 16 - ta))))
                for k in ks:
                    a = 2 * math.pi * k / 16
                    qx, qy = cx + r * math.cos(a), cy + r * math.sin(a)
                    if qx < kenar + yaricap or qx > W - kenar - yaricap or qy < kenar + yaricap or qy > H - kenar - yaricap:
                        continue
                    if any(z.Outline().Collide(pcbnew.VECTOR2I(int(qx * 1e6), int(qy * 1e6)), int(0.5 * 1e6)) for z in kutular):
                        continue
                    sorun = False
                    for (hx, hy, hr) in dl:
                        if math.hypot(qx - hx, qy - hy) < via_drill / 2 + hr + 0.3:
                            sorun = True; break
                    if sorun: continue
                    for LL in (F, B, I2):
                        for o in obs[LL]:
                            if o[2] == nc:
                                continue
                            if dist_ob(o, qx, qy) < yaricap + klirens:
                                sorun = True; break
                        if sorun: break
                    if sorun: continue
                    for o in obs[L]:
                        if o[2] == nc or o[3] == id(pad):
                            continue
                        if dist_ob_dogru(o, cx, cy, qx, qy) < iz / 2 + klirens:
                            sorun = True; break
                    if sorun: continue
                    ok = (qx, qy); break
                if ok: break
            if not ok:
                # ayni agdaki yakin bir ayak veya via'ya duz iz
                hedefler = []
                for p2 in b.GetPads():
                    if p2.GetNetCode() == nc and p2.m_Uuid != pad.m_Uuid and p2.IsOnLayer(L):
                        q2 = p2.GetPosition()
                        hedefler.append((math.hypot(q2.x / 1e6 - cx, q2.y / 1e6 - cy), q2, id(p2)))
                hedefler.sort(key=lambda h: h[0])
                for dd, q2, pid in hedefler[:6]:
                    if dd > 6.0:
                        break
                    qx, qy = q2.x / 1e6, q2.y / 1e6
                    sorun = False
                    for o in obs[L]:
                        if o[2] == nc or o[3] == id(pad) or o[3] == pid:
                            continue
                        if dist_ob_dogru(o, cx, cy, qx, qy) < iz / 2 + klirens:
                            sorun = True; break
                    if not sorun:
                        t = pcbnew.PCB_TRACK(b)
                        t.SetStart(c); t.SetEnd(q2); t.SetWidth(int(iz * 1e6)); t.SetLayer(L); t.SetNet(ni)
                        b.Add(t); sonuc['eklendi'] += 1; ok = 'bagli'
                        break
                if ok == 'bagli':
                    continue
                vs = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA' and t.GetNetCode() == nc]
                vs.sort(key=lambda t: math.hypot(t.GetPosition().x / 1e6 - cx, t.GetPosition().y / 1e6 - cy))
                for v0 in vs[:6]:
                    qx, qy = v0.GetPosition().x / 1e6, v0.GetPosition().y / 1e6
                    if math.hypot(qx - cx, qy - cy) > 9.0:
                        break
                    sorun = False
                    for o in obs[L]:
                        if o[2] == nc or o[3] == id(pad):
                            continue
                        if dist_ob_dogru(o, cx, cy, qx, qy) < iz / 2 + klirens:
                            sorun = True; break
                    if not sorun:
                        t = pcbnew.PCB_TRACK(b)
                        t.SetStart(c); t.SetEnd(v0.GetPosition()); t.SetWidth(int(iz * 1e6)); t.SetLayer(L); t.SetNet(ni)
                        b.Add(t); sonuc['eklendi'] += 1; ok = 'bagli'
                        break
                if ok == 'bagli':
                    continue
                sonuc['bulunamadi'].append((ad, pad.GetParent().GetReference(), pad.GetNumber()))
                continue
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(int(ok[0] * 1e6), int(ok[1] * 1e6)))
            v.SetWidth(int(via_d * 1e6)); v.SetDrill(int(via_drill * 1e6))
            v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(F, B); v.SetNet(ni)
            b.Add(v)
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(c); t.SetEnd(pcbnew.VECTOR2I(int(ok[0] * 1e6), int(ok[1] * 1e6)))
            t.SetWidth(int(iz * 1e6)); t.SetLayer(L); t.SetNet(ni)
            b.Add(t)
            sonuc['eklendi'] += 1
            if sadece:
                # arka yuzde ayni agdaki en yakin via'ya duz iz
                obs2 = ob_topla()
                vs = [v1 for v1 in b.GetTracks() if v1.GetClass() == 'PCB_VIA' and v1.GetNetCode() == nc and (v1.GetPosition().x != v.GetPosition().x or v1.GetPosition().y != v.GetPosition().y)]
                vs.sort(key=lambda v1: math.hypot(v1.GetPosition().x / 1e6 - ok[0], v1.GetPosition().y / 1e6 - ok[1]))
                for v1 in vs[:8]:
                    qx, qy = v1.GetPosition().x / 1e6, v1.GetPosition().y / 1e6
                    if all(dist_ob_dogru(o, ok[0], ok[1], qx, qy) >= iz / 2 + klirens for o in obs2[B] if o[2] != nc):
                        t2 = pcbnew.PCB_TRACK(b)
                        t2.SetStart(v.GetPosition()); t2.SetEnd(v1.GetPosition()); t2.SetWidth(int(iz * 1e6)); t2.SetLayer(B); t2.SetNet(ni)
                        b.Add(t2); sonuc['bagli'] = sonuc.get('bagli', 0) + 1
                        break
    return sonuc


def delik_koruma(b, pay=0.45):
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.In1_Cu); ls.AddLayer(pcbnew.In2_Cu)
    n = 0
    for pad in b.GetPads():
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            p = pad.GetPosition(); r = pad.GetDrillSize().x / 2e6 + pay
            z = pcbnew.ZONE(b)
            z.SetIsRuleArea(True)
            z.SetDoNotAllowCopperPour(True)
            z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
            z.SetLayerSet(ls)
            ol = z.Outline(); ol.NewOutline()
            for k in range(24):
                a = 2 * math.pi * k / 24
                ol.Append(int(p.x + r * 1e6 * math.cos(a)), int(p.y + r * 1e6 * math.sin(a)))
            b.Add(z); n += 1
    return n
