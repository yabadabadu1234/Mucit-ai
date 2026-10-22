import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from pcbgen import mm, vec

def sinir(f, katman):
    xs = []; ys = []
    for g in f.GraphicalItems():
        if g.GetLayer() == katman:
            bb = g.GetBoundingBox()
            xs += [bb.GetLeft() / 1e6, bb.GetRight() / 1e6]; ys += [bb.GetTop() / 1e6, bb.GetBottom() / 1e6]
    return (min(xs), max(xs), min(ys), max(ys)) if xs else None

def pad_konum(f, no):
    return [(p.GetPosition().x / 1e6, p.GetPosition().y / 1e6) for p in f.Pads() if p.GetNumber() == str(no)]

class Yer:
    def __init__(self, pano, W, H, kenar=0.7):
        self.p = pano; self.W = W; self.H = H; self.kenar = kenar
        self.kutu = {'F': {}, 'B': {}}
        self.yasak = []
        self.sabit = set()

    def _kutu(self, ref):
        f = self.p.fps[ref]
        arka = f.IsFlipped()
        k = sinir(f, pcbnew.B_CrtYd if arka else pcbnew.F_CrtYd)
        if ref in self.ozel:
            k = sinir(f, pcbnew.B_Fab if arka else pcbnew.F_Fab)
        return arka, k

    ozel = {'U1'}

    def kaydet(self, ref, tht=False):
        if ref in self.ozel:
            self.poli = self.p.fps[ref].GetCourtyard(pcbnew.F_CrtYd)
        arka, k = self._kutu(ref)
        if k is None:
            return
        for side in (('B',) if arka else ('F',)) if not tht else ('F', 'B'):
            self.kutu[side][ref] = k
        f = self.p.fps[ref]
        for z in f.Zones():
            if z.GetIsRuleArea():
                bb = z.GetBoundingBox()
                self.yasak.append((bb.GetLeft() / 1e6, bb.GetRight() / 1e6, bb.GetTop() / 1e6, bb.GetBottom() / 1e6, ref))

    def sabit_ekle(self, ref, x, y, rot, arka=False, tht=False):
        self.p.parca_ekle(ref, x, y, rot, arka)
        self.kaydet(ref, tht)
        self.sabit.add(ref)

    poli = None

    def _poli_cakisma(self, k):
        if self.poli is None:
            return False
        x0, x1, y0, y1 = k
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), ((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2), ((x0 + x1) / 2, (y0 + y1) / 2)]
        return any(self.poli.Collide(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)), int(0.3e6)) for x, y in pts)

    def _cakisma(self, ref, k, side, bos=0.3):
        if side == 'F' and self._poli_cakisma(k):
            return True
        for r2, k2 in self.kutu[side].items():
            if r2 == ref: continue
            if k[0] - bos < k2[1] and k2[0] - bos < k[1] and k[2] - bos < k2[3] and k2[2] - bos < k[3]:
                return True
        for (x0, x1, y0, y1, r2) in self.yasak:
            if r2 == ref: continue
            if k[0] < x1 and x0 < k[1] and k[2] < y1 and y0 < k[3]:
                return True
        if k[0] < self.kenar or k[1] > self.W - self.kenar or k[2] < self.kenar or k[3] > self.H - self.kenar:
            return True
        return False

    def pasif_ekle(self, ref, ap, side_arka=False, rmax=18.0, yon=None):
        """ap: (x, y) capa konumu; yakin bos yer arar."""
        p = self.p
        f0 = p.parca_ekle(ref, ap[0], ap[1], 0, side_arka)
        side = 'B' if side_arka else 'F'
        adaylar = []
        r = 1.2
        while r <= rmax:
            n = max(12, int(r * 6))
            for k in range(n):
                a = 2 * math.pi * k / n
                adaylar.append((r, ap[0] + r * math.cos(a), ap[1] + r * math.sin(a)))
            r += 0.6
        adaylar.sort(key=lambda t: t[0])
        for r, x, y in adaylar:
            for rot in (0, 90):
                f0.SetPosition(vec(x, y))
                f0.SetOrientationDegrees(rot if not side_arka else rot)
                kk = sinir(f0, pcbnew.B_CrtYd if side_arka else pcbnew.F_CrtYd)
                if kk is None: continue
                if not self._cakisma(ref, kk, side):
                    self.kutu[side][ref] = kk
                    return (x, y, rot)
        raise RuntimeError('yer bulunamadi: ' + ref)
