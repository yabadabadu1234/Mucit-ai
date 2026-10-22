import sys, os, re, math, heapq
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy import ndimage
import pcbnew
import yonlendir as Y
from pcbgen import mm

R = 0.05
KLR = 0.22
VIA_D, VIA_DR = 0.5, 0.25


def dunya(v):
    return int(round(v / R))


class Izgara:
    def __init__(self, b, W, H):
        self.b = b; self.W = W; self.H = H
        self.nx = int(W / R) + 1; self.ny = int(H / R) + 1
        self.F, self.B = pcbnew.F_Cu, pcbnew.B_Cu
        self.kur()

    def disk(self, lab, l, cx, cy, r, nc):
        x0 = max(0, int((cx - r) / R) - 1); x1 = min(self.nx - 1, int((cx + r) / R) + 1)
        y0 = max(0, int((cy - r) / R) - 1); y1 = min(self.ny - 1, int((cy + r) / R) + 1)
        if x1 < x0 or y1 < y0: return
        ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        m = (xs * R - cx) ** 2 + (ys * R - cy) ** 2 <= r * r
        self.isle(lab[l], y0, x0, m, nc)

    def isle(self, a, y0, x0, m, nc):
        sub = a[y0:y0 + m.shape[0], x0:x0 + m.shape[1]]
        bos = (sub == 0) & m
        ayni = (sub == nc) & m
        cak = m & ~bos & ~ayni
        sub[bos] = nc
        sub[cak] = -1

    def kutu(self, lab, l, x0, y0, x1, y1, nc):
        i0 = max(0, int(math.floor(x0 / R + 0.5))); i1 = min(self.nx - 1, int(math.floor(x1 / R + 0.5)))
        j0 = max(0, int(math.floor(y0 / R + 0.5))); j1 = min(self.ny - 1, int(math.floor(y1 / R + 0.5)))
        if i1 < i0 or j1 < j0: return
        m = np.ones((j1 - j0 + 1, i1 - i0 + 1), bool)
        self.isle(lab[l], j0, i0, m, nc)

    def kur(self):
        b = self.b
        lab = np.zeros((2, self.ny, self.nx), np.int32)
        trk = np.zeros((2, self.ny, self.nx), np.int32)
        for pad in b.GetPads():
            bb = pad.GetBoundingBox()
            r = (bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6)
            nc = pad.GetNetCode() if pad.GetNetCode() > 0 else 100000 + (id(pad) % 90000)
            for l, L in enumerate((self.F, self.B)):
                if pad.IsOnLayer(L):
                    self.kutu(lab, l, *r, nc)
            dz = pad.GetDrillSize()
            if dz.x > 0:
                p = pad.GetPosition()
                for l in (0, 1):
                    self.disk(lab, l, p.x / 1e6, p.y / 1e6, dz.x / 2e6 + 0.1, nc)
        for t in b.GetTracks():
            nc = t.GetNetCode()
            if t.GetClass() == 'PCB_VIA':
                p = t.GetPosition()
                for l in (0, 1):
                    self.disk(lab, l, p.x / 1e6, p.y / 1e6, t.GetWidth() / 2e6, nc)
            else:
                L = t.GetLayer()
                if L not in (self.F, self.B): continue
                l = 0 if L == self.F else 1
                s, e = t.GetStart(), t.GetEnd()
                ax, ay, bx, by = s.x / 1e6, s.y / 1e6, e.x / 1e6, e.y / 1e6
                n = max(1, int(math.hypot(bx - ax, by - ay) / (R / 2)))
                hw = t.GetWidth() / 2e6
                for i in range(n + 1):
                    u = i / n
                    self.disk(trk, l, ax + u * (bx - ax), ay + u * (by - ay), hw, nc)
        for fp in b.GetFootprints():
            for z in fp.Zones():
                if z.GetIsRuleArea() and (z.GetDoNotAllowTracks() or z.GetDoNotAllowVias()):
                    bb = z.Outline().BBox()
                    ls = z.GetLayerSet()
                    for l, LL in ((0, self.F), (1, self.B)):
                        if not ls.Contains(LL): continue
                        self.kutu(lab, l, bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6, -1)
        k = int(0.5 / R)
        lab[:, :k, :] = -1; lab[:, -k:, :] = -1; lab[:, :, :k] = -1; lab[:, :, -k:] = -1
        self.lab = lab; self.trk = trk

    def yasak(self, nc, w, yumusak=False):
        out = []; via = []
        for l in (0, 1):
            dig = (self.lab[l] != 0) & (self.lab[l] != nc)
            if not yumusak:
                dig = dig | ((self.trk[l] != 0) & (self.trk[l] != nc))
            d = ndimage.distance_transform_edt(~dig) * R
            out.append(d >= KLR + w / 2 - 0.02)
            via.append(d >= KLR + VIA_D / 2 - 0.02)
        return np.array(out), np.array(via[0] & via[1])

    def ara(self, nc, w, bas, hed, va_c=40.0, yumusak=False):
        ok, vok = self.yasak(nc, w, yumusak)
        if yumusak:
            ceza = np.zeros((2, self.ny, self.nx), np.float32)
            for l in (0, 1):
                dig = (self.trk[l] != 0) & (self.trk[l] != nc)
                d = ndimage.distance_transform_edt(~dig) * R
                ceza[l] = np.where(d < KLR + w / 2, 24.0, 0.0)
                vok = vok & (d >= KLR + VIA_D / 2) if l == 0 else vok & (d >= KLR + VIA_D / 2)
        else:
            ceza = None
        (l0, x0, y0), (l1, x1, y1) = bas, hed
        for (l, x, y) in ((l0, x0, y0), (l1, x1, y1)):
            cx, cy = dunya(x), dunya(y); r = int(0.5 / R)
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r and 0 <= cy + dy < self.ny and 0 <= cx + dx < self.nx:
                        ok[l, cy + dy, cx + dx] = True
        nx, ny = self.nx, self.ny
        g = np.full((2, ny, nx), np.inf, np.float32)
        par = np.full((2, ny, nx), -1, np.int64)
        s = (l0, dunya(y0), dunya(x0)); t = (l1, dunya(y1), dunya(x1))
        g[s] = 0
        def h(y, x):
            dx, dy = abs(x - t[2]), abs(y - t[1])
            return (max(dx, dy) + 0.414 * min(dx, dy))
        pq = [(h(s[1], s[2]), 0.0, s)]
        nb = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
        n = 0
        while pq:
            f, gc, cur = heapq.heappop(pq)
            if gc > g[cur]: continue
            if cur == t:
                yol = []
                while cur != s:
                    yol.append(cur)
                    p = par[cur]
                    cur = (int(p // (ny * nx)), int((p // nx) % ny), int(p % nx))
                yol.append(s)
                return yol[::-1]
            n += 1
            if n > 16000000: return None
            l, y, x = cur
            for dy, dx, c in nb:
                yy, xx = y + dy, x + dx
                if not (0 <= yy < ny and 0 <= xx < nx): continue
                if not ok[l, yy, xx]: continue
                if dy and dx and not (ok[l, y, xx] and ok[l, yy, x]): continue
                ng = gc + c + (ceza[l, yy, xx] if ceza is not None else 0.0)
                if ng < g[l, yy, xx]:
                    g[l, yy, xx] = ng; par[l, yy, xx] = (l * ny + y) * nx + x
                    heapq.heappush(pq, (ng + h(yy, xx), ng, (l, yy, xx)))
            if vok[y, x]:
                l2 = 1 - l
                if ok[l2, y, x]:
                    ng = gc + va_c
                    if ng < g[l2, y, x]:
                        g[l2, y, x] = ng; par[l2, y, x] = (l * ny + y) * nx + x
                        heapq.heappush(pq, (ng + h(y, x), ng, (l2, y, x)))
        return None


def sadelestir(yol):
    # (katman,y,x) listesi -> parcalar: ('iz', l, [(x,y)...]) ve ('via', x, y)
    parcalar = []; cur = [yol[0]]
    for a in yol[1:]:
        if a[0] != cur[-1][0]:
            parcalar.append(cur); cur = [a]
        else:
            cur.append(a)
    parcalar.append(cur)
    out = []
    for i, p in enumerate(parcalar):
        nok = [p[0]]
        for k in range(1, len(p) - 1):
            a, b_, c = p[k - 1], p[k], p[k + 1]
            if (b_[1] - a[1], b_[2] - a[2]) != (c[1] - b_[1], c[2] - b_[2]):
                nok.append(b_)
        nok.append(p[-1]) if len(p) > 1 else None
        out.append((p[0][0], [(q[2] * R, q[1] * R) for q in nok]))
    return out


def ekle(b, nc, w, parcalar):
    ni = b.FindNetsByNetcode(nc) if hasattr(b, 'FindNetsByNetcode') else None
    net = b.FindNet(nc)
    yeni = []
    prev = None
    for l, pts in parcalar:
        L = pcbnew.F_Cu if l == 0 else pcbnew.B_Cu
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1))); t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
            t.SetWidth(mm(w)); t.SetLayer(L); t.SetNet(net)
            b.Add(t); yeni.append(t)
        if prev is not None:
            x, y = pts[0]
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
            v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DR)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net)
            b.Add(v); yeni.append(v)
        prev = l
    return yeni


def baglantisizlar(rep):
    out = []
    for m in re.finditer(r'\[unconnected_items\][^\n]*\n[^\n]*\n\s+@\(([\d.]+) mm, ([\d.]+) mm\): ([^\n]*)\n\s+@\(([\d.]+) mm, ([\d.]+) mm\): ([^\n]*)', rep):
        x1, y1, a, x2, y2, c = m.groups()
        net = re.search(r'\[([^\]]+)\]', a).group(1)
        la = re.search(r'on (F|B)\.Cu', a); lc = re.search(r'on (F|B)\.Cu', c)
        l1 = 1 if (la and la.group(1) == 'B') else 0
        l2 = 1 if (lc and lc.group(1) == 'B') else 0
        out.append((net, (l1, float(x1), float(y1)), (l2, float(x2), float(y2))))
    return out


def sorun_say(b, yol='/tmp/claude-0/drc_izg.rpt'):
    Y.doldur(b)
    rep = Y.drc(b, yol)
    s, o = Y.drc_ozet(rep, 1)
    return sum(v for k, v in s.items() if not k.endswith('(w)') and not k.startswith('lib') and k != 'unconnected_items'), rep


def calistir(yol, cikis, W, H):
    b = pcbnew.LoadBoard(yol)
    taban, rep = sorun_say(b)
    print('taban hata', taban)
    kara = set(); rip = {}
    b.Save(cikis)
    for tur in range(120):
        liste = [x for x in baglantisizlar(rep) if (x[0], x[1], x[2]) not in kara]
        if not liste: break
        net, bas, hed = liste[0]
        try:
            nc = b.FindNet(net).GetNetCode()
        except Exception:
            kara.add((net, bas, hed)); print('net bulunamadi', net); continue
        I = Izgara(b, W, H)
        tercih = 0.5 if net.startswith('+12V') else (0.4 if net in ('VBAT_MOD', 'LAMBA_SW') else 0.25)
        yapildi = False
        for w in (tercih, 0.25, 0.2):
            yolu = I.ara(nc, w, bas, hed)
            if yolu is None: continue
            yeni = ekle(b, nc, w, sadelestir(yolu))
            k, rep2 = sorun_say(b)
            if k > taban:
                for t in yeni: b.Remove(t)
                print('red', net, w, k - taban)
                continue
            taban = k; rep = rep2; yapildi = True; b.Save(cikis)
            print('kabul', net, w, bas[1:], hed[1:])
            break
        if not yapildi and rip.get(net, 0) < 2:
            rip[net] = rip.get(net, 0) + 1
            yolu = I.ara(nc, 0.2, bas, hed, yumusak=True)
            if yolu is not None:
                pts = [(q[2] * R, q[1] * R, q[0]) for q in yolu]
                sok = []
                for t in list(b.GetTracks()):
                    if t.GetClass() == 'PCB_VIA' or t.GetNetCode() == nc: continue
                    l = 0 if t.GetLayer() == pcbnew.F_Cu else 1
                    sx, sy, ex, ey = t.GetStart().x / 1e6, t.GetStart().y / 1e6, t.GetEnd().x / 1e6, t.GetEnd().y / 1e6
                    lim = KLR + 0.1 + t.GetWidth() / 2e6
                    for (px, py, pl) in pts[::2]:
                        if pl == l and Y._nokta_dogru(px, py, sx, sy, ex, ey) < lim:
                            sok.append(t); break
                if sok and len(sok) <= 12:
                    sakla = [(t, t.GetNetname()) for t in sok]
                    for t in sok: b.Remove(t)
                    yeni = ekle(b, nc, 0.2, sadelestir(yolu))
                    k, rep2 = sorun_say(b)
                    if k > taban:
                        b = pcbnew.LoadBoard(cikis)
                        print('rip red', net, k - taban, len(sok))
                    else:
                        taban = k; rep = rep2; yapildi = True; b.Save(cikis)
                        print('RIP kabul', net, 'sokulen', len(sok), sorted({n for _, n in sakla}))
        if not yapildi:
            kara.add((net, bas, hed)); print('olmadi', net, bas, hed)
    k, rep = sorun_say(b)
    b.BuildConnectivity()
    print('kalan baglantisiz', b.GetConnectivity().GetUnconnectedCount(False), 'hata', k)
    b.Save(cikis)
    return rep


if __name__ == '__main__':
    W, H = float(sys.argv[3]), float(sys.argv[4])
    calistir(sys.argv[1], sys.argv[2], W, H)
