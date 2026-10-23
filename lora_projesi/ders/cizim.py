import math
from html import escape

ROT = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}


def _don(px, py, rot):
    t = math.radians(rot)
    return (round(px * math.cos(t) - py * math.sin(t), 3), round(px * math.sin(t) + py * math.cos(t), 3))


class Cizim:
    """Gercek devre sembolleriyle sema cizer ve baglantisini gercek ag listesiyle denetler."""

    def __init__(self, ad, w, h, parcalar, aglar=None):
        self.ad = ad
        self.w, self.h = w, h
        self.parcalar = parcalar
        self.katman = {'tel': [], 'sembol': [], 'yazi': [], 'isaret': [], 'nokta': []}
        self.pinler = {}
        self.noktalar = {}
        self.teller = []
        self.etiketler = []
        self.guc = []
        self.isaretler = []
        self.ciz_ref = set()
        self.ogeler = []
        self.tel_ilk = []
        self.tel_ag = {}

    # ------------------------------------------------------------ temel
    def _g(self, ref, govde, x, y, rot):
        return '<g class="parca" data-ref="%s" transform="translate(%s,%s) rotate(%s)">%s</g>' % (ref, x, y, rot, govde)

    def _yaz(self, x, y, metin, sinif='deger', anchor='middle'):
        ek = ' data-ag="%s"' % escape(metin) if sinif in ('agad', 'rayad') else ''
        self.katman['yazi'].append('<text class="%s" x="%s" y="%s" text-anchor="%s"%s>%s</text>' % (sinif, x, y, anchor, ek, escape(metin)))

    def _pin(self, ref, no, x, y):
        self.pinler[(ref, str(no))] = (round(x, 2), round(y, 2))
        self.noktalar.setdefault((round(x, 2), round(y, 2)), []).append((ref, str(no)))

    def _deger(self, ref):
        p = self.parcalar[ref]
        return p.deger

    def _iki(self, ref, x, y, rot, govde, uzunluk=60, deger_yaz=True, yazi_yon=None, pinler=('1', '2'), yazi_dy=0):
        self.ciz_ref.add(ref)
        self.katman['sembol'].append(self._g(ref, govde, x, y, rot))
        a = _don(0, 0, rot); b = _don(uzunluk, 0, rot)
        self._pin(ref, pinler[0], x + a[0], y + a[1])
        self._pin(ref, pinler[1], x + b[0], y + b[1])
        cx, cy = x + _don(uzunluk / 2, 0, rot)[0], y + _don(uzunluk / 2, 0, rot)[1]
        if deger_yaz:
            if rot in (0, 180):
                self.katman['yazi'].append('<text x="%s" y="%s" text-anchor="middle"><tspan class="ref">%s</tspan><tspan class="deger" dx="6">%s</tspan></text>' % (
                    cx, cy - 14, escape(ref), escape(self._deger(ref))))
            else:
                self._yaz(cx + 14, cy - 3 + yazi_dy, ref, 'ref', 'start')
                self._yaz(cx + 14, cy + 11 + yazi_dy, self._deger(ref), 'deger', 'start')
        return {'a': (x + a[0], y + a[1]), 'b': (x + b[0], y + b[1]), 'm': (cx, cy)}

    # ------------------------------------------------------------ iki uclu semboller
    def direnc(self, ref, x, y, rot=0, **k):
        g = '<path d="M0 0H15M45 0H60"/><rect x="15" y="-6" width="30" height="12"/>'
        return self._iki(ref, x, y, rot, g, **k)

    def kondansator(self, ref, x, y, rot=0, kutuplu=False, **k):
        g = '<path d="M0 0H26M34 0H60M26 -12V12"/>'
        if kutuplu:
            g += '<path d="M36 -12Q30 0 36 12" /><text class="art" x="14" y="-6" text-anchor="middle" transform="rotate(%s 14 -6)">+</text>' % (-rot)
        else:
            g += '<path d="M34 -12V12"/>'
        return self._iki(ref, x, y, rot, g, **k)

    def bobin(self, ref, x, y, rot=0, **k):
        yaylar = 'a5 5 0 0 1 10 0 ' * 4
        g = '<path d="M0 0H10 M10 0%sM50 0H60" fill="none"/>' % yaylar.replace('M10 0', '')
        g = '<path d="M0 0H10"/><path d="M10 0 ' + yaylar + '"/><path d="M50 0H60"/>'
        return self._iki(ref, x, y, rot, g, **k)

    def boncuk(self, ref, x, y, rot=0, **k):
        g = '<path d="M0 0H15M45 0H60"/><rect x="15" y="-6" width="30" height="12" class="dolu"/>'
        return self._iki(ref, x, y, rot, g, **k)

    def sigorta(self, ref, x, y, rot=0, **k):
        g = '<path d="M0 0H15M45 0H60"/><rect x="15" y="-6" width="30" height="12"/><path d="M19 7L41 -7"/>'
        return self._iki(ref, x, y, rot, g, **k)

    def _anot_katot(self, ref, k_pin):
        p = self.parcalar[ref]
        if k_pin is None:
            for no, pn in p.pinler.items():
                if pn['ad'] == 'K':
                    k_pin = no
        assert k_pin is not None, (ref, 'katot ayagi bulunamadi')
        a = [no for no in p.pinler if no != k_pin]
        assert len(a) == 1, (ref, a)
        return (a[0], k_pin)

    def diyot(self, ref, x, y, rot=0, tur='diyot', k_pin=None, **k):
        pn = self._anot_katot(ref, k_pin)
        g = '<path d="M0 0H22M38 0H60"/><path d="M22 -9V9L38 0Z" class="dolu"/>'
        if tur == 'zener':
            g += '<path d="M33 -9H38V9H43"/>'
        elif tur == 'schottky':
            g += '<path d="M33 -6V-9H38V9H43V6"/>'
        elif tur == 'tvs':
            g += '<path d="M33 -9H38V9H43"/>'
        else:
            g += '<path d="M38 -9V9"/>'
        return self._iki(ref, x, y, rot, g, pinler=pn, **k)

    def led(self, ref, x, y, rot=0, k_pin=None, **k):
        pn = self._anot_katot(ref, k_pin)
        g = ('<path d="M0 0H22M38 0H60"/><path d="M22 -9V9L38 0Z" class="dolu"/><path d="M38 -9V9"/>'
             '<path d="M26 -14L36 -24M32 -12L42 -22" class="ok"/><path d="M36 -24l-5 1M36 -24l-1 5M42 -22l-5 1M42 -22l-1 5" class="ok"/>')
        return self._iki(ref, x, y, rot, g, pinler=pn, **k)

    def kristal(self, ref, x, y, rot=0, **k):
        g = '<path d="M0 0H22M38 0H60"/><path d="M22 -10V10M38 -10V10"/><rect x="26" y="-7" width="8" height="14"/>'
        return self._iki(ref, x, y, rot, g, **k)

    def dugme(self, ref, x, y, rot=0, **k):
        g = '<path d="M0 0H18M42 0H60"/><circle cx="18" cy="0" r="2"/><circle cx="42" cy="0" r="2"/><path d="M14 -10H46M30 -10V-16M18 -3V-10M42 -3V-10"/>'
        g = '<path d="M0 0H18M42 0H60"/><circle cx="18" cy="0" r="2" class="dolu"/><circle cx="42" cy="0" r="2" class="dolu"/><path d="M16 -9H44M30 -9V-17"/>'
        return self._iki(ref, x, y, rot, g, **k)

    def pil(self, ref, x, y, rot=0, **k):
        g = '<path d="M0 0H22M38 0H60M22 -14V14M30 -8V8M38 -14V14" /><path d="M22 -14V14M38 -14V14"/><path d="M30 -8V8"/><text class="art" x="12" y="-8" text-anchor="middle">+</text>'
        g = '<path d="M0 0H18M42 0H60"/><path d="M18 -14V14M24 -7V7M30 -14V14M36 -7V7M42 -14V14"/>'
        return self._iki(ref, x, y, rot, g, **k)

    # ------------------------------------------------------------ transistor
    def npn(self, ref, x, y, rot=0):
        self.ciz_ref.add(ref)
        g = ('<path d="M0 0H25M25 -14V14M25 -7L40 -20V-30M25 7L40 20V30"/><circle cx="25" cy="0" r="28" class="cevre"/>'
             '<path d="M35 14L40 20L32 18Z" class="dolu"/>')
        self.katman['sembol'].append(self._g(ref, g, x, y, rot))
        b = _don(0, 0, rot); c = _don(40, -30, rot); e = _don(40, 30, rot)
        self._pin(ref, 1, x + b[0], y + b[1]); self._pin(ref, 3, x + c[0], y + c[1]); self._pin(ref, 2, x + e[0], y + e[1])
        self._yaz(x + _don(48, 0, rot)[0] + (8 if rot == 0 else 0), y + _don(48, 0, rot)[1] - 4, ref, 'ref', 'start')
        self._yaz(x + _don(48, 0, rot)[0] + (8 if rot == 0 else 0), y + _don(48, 0, rot)[1] + 10, self._deger(ref), 'deger', 'start')
        return {'B': (x + b[0], y + b[1]), 'C': (x + c[0], y + c[1]), 'E': (x + e[0], y + e[1])}

    def pmos(self, ref, x, y, rot=0, pinler=('1', '2', '3'), ayna=False, yazi=(52, -2), yazi_hiza='start'):
        """kapi (0,0); kaynak ustte (40,-30); savak altta (40,30). ayna=True: once soldan saga yansitilir, sonra dondurulur."""
        self.ciz_ref.add(ref)
        g = ('<path d="M0 0H18M18 -12V12M24 -14V-6M24 -4V4M24 6V14M24 -10H40V-30M24 10H40V30M24 0H33V-10"/>'
             '<path d="M30 0L25 -3V3Z" class="dolu"/><circle cx="33" cy="-10" r="1.8" class="dolu"/>')
        tr = 'translate(%s,%s) rotate(%s)%s' % (x, y, rot, ' scale(-1,1)' if ayna else '')
        self.katman['sembol'].append('<g class="parca" data-ref="%s" transform="%s">%s</g>' % (ref, tr, g))
        m = -1 if ayna else 1
        gt = _don(0, 0, rot); s_ = _don(40 * m, -30, rot); d = _don(40 * m, 30, rot)
        self._pin(ref, pinler[0], x + gt[0], y + gt[1]); self._pin(ref, pinler[1], x + s_[0], y + s_[1]); self._pin(ref, pinler[2], x + d[0], y + d[1])
        self._yaz(x + yazi[0], y + yazi[1], ref, 'ref', yazi_hiza)
        self._yaz(x + yazi[0], y + yazi[1] + 14, self._deger(ref), 'deger', yazi_hiza)
        return {'G': (x + gt[0], y + gt[1]), 'S': (x + s_[0], y + s_[1]), 'D': (x + d[0], y + d[1])}

    # ------------------------------------------------------------ kutu (entegre, konnektor)
    def kutu(self, ref, x, y, sol, sag, ust=(), alt=(), genislik=140, baslik=None, sinif='ic', pinaralik=20, goster_deger=True, baslik_yok=False):
        """sol/sag/ust/alt: [(pinno, ad)] listeleri. (x,y) sol ust kose. Pinler dis uca 'kisa' = 15 px."""
        self.ciz_ref.add(ref)
        n = max(len(sol), len(sag), 1)
        h = (n + 1) * pinaralik + (18 if alt else 0)
        w = genislik
        govde = '<rect class="%s" x="%s" y="%s" width="%s" height="%s" rx="3"/>' % (sinif, x, y, w, h)
        self.katman['sembol'].append('<g class="parca" data-ref="%s">%s</g>' % (ref, govde))
        res = {}
        def yan(liste, ux, dy_dir):
            for i, ent in enumerate(liste):
                no, ad = ent[0], ent[1]
                nc = len(ent) > 2 and ent[2] == 'nc'
                py = y + (i + 1) * pinaralik
                if dy_dir < 0:
                    ex, ix = x - 15, x
                    self.katman['tel'].append('<path class="pinuc" d="M%s %sH%s"/>' % (ex, py, ix))
                    self._yaz(x + 5, py + 4, ad, 'pinad', 'start')
                    (self._yaz(ex + 6, py - 4, str(no), 'pinno', 'middle') if not isinstance(no, (list, tuple)) else self._yaz(ex - 14, py - 15, '·'.join(str(q) for q in no), 'pinno', 'end'))
                else:
                    ex, ix = x + w + 15, x + w
                    self.katman['tel'].append('<path class="pinuc" d="M%s %sH%s"/>' % (ix, py, ex))
                    self._yaz(x + w - 5, py + 4, ad, 'pinad', 'end')
                    (self._yaz(ex - 6, py - 4, str(no), 'pinno', 'middle') if not isinstance(no, (list, tuple)) else self._yaz(ex + 14, py - 5, '·'.join(str(q) for q in no), 'pinno', 'start'))
                if nc:
                    self.katman['yazi'].append('<text x="%s" y="%s" text-anchor="middle" class="not" font-size="14">×</text>' % (ex, py + 5))
                    continue
                for n_ in (no if isinstance(no, (list, tuple)) else [no]):
                    self._pin(ref, n_, ex, py)
                res[str(no) if not isinstance(no, (list, tuple)) else str(no[0])] = (ex, py)
        yan(sol, x, -1)
        yan(sag, x, 1)
        for i, ent in enumerate(ust):
            no, ad = ent[0], ent[1]
            px = x + (i + 1) * (w / (len(ust) + 1))
            self.katman['tel'].append('<path class="pinuc" d="M%s %sV%s"/>' % (px, y - 15, y))
            self._yaz(px, y + 14, ad, 'pinad', 'middle')
            self._yaz(px + 8, y - 18, '·'.join(str(q) for q in no) if isinstance(no, (list, tuple)) else str(no), 'pinno', 'start')
            [self._pin(ref, q, px, y - 15) for q in (no if isinstance(no, (list, tuple)) else [no])]; res[str(no if not isinstance(no, (list, tuple)) else no[0])] = (px, y - 15)
        for i, ent in enumerate(alt):
            no, ad = ent[0], ent[1]
            px = x + (i + 1) * (w / (len(alt) + 1))
            if len(ent) > 2 and ent[2] == 'nc':
                self.katman['tel'].append('<path class="pinuc" d="M%s %sV%s"/>' % (px, y + h, y + h + 15))
                self._yaz(px, y + h - 6, ad, 'pinad', 'middle')
                self._yaz(px, y + h + 30, '×', 'not', 'middle')
                continue
            self.katman['tel'].append('<path class="pinuc" d="M%s %sV%s"/>' % (px, y + h, y + h + 15))
            self._yaz(px, y + h - 6, ad, 'pinad', 'middle')
            self._yaz(px + 8, y + h + 22, '·'.join(str(q) for q in no) if isinstance(no, (list, tuple)) else str(no), 'pinno', 'start')
            [self._pin(ref, q, px, y + h + 15) for q in (no if isinstance(no, (list, tuple)) else [no])]; res[str(no if not isinstance(no, (list, tuple)) else no[0])] = (px, y + h + 15)
        bas = ref + ('  ' + (baslik or self._deger(ref)) if goster_deger else '')
        if baslik_yok:
            pass
        elif ust:
            self._yaz(x + w / 2, y + h - 24, bas, 'ref')
        else:
            self._yaz(x + w / 2, y - 6, bas, 'ref')
        return res

    # ------------------------------------------------------------ tel, nokta, etiket
    def tel(self, *noktalar, ag=None):
        """noktalar: (x,y) dizisi; dik kirilimlar icin aralara nokta ver."""
        pts = [(round(a, 2), round(b, 2)) for a, b in noktalar]
        d = 'M' + ' L'.join('%s %s' % p for p in pts)
        tid = len(self.tel_ilk)
        self.tel_ilk.append(pts[0])
        self.katman['tel'].append('<path class="tel" d="%s" data-ag="@@T%d@@"/>' % (d, tid))
        for p in pts:
            self.noktalar.setdefault(p, [])
        for a, b in zip(pts, pts[1:]):
            self.teller.append((a, b))
        return pts[-1]

    def nokta(self, x, y):
        self.katman['nokta'].append('<circle class="dugum" cx="%s" cy="%s" r="3.4"/>' % (x, y))
        self.noktalar.setdefault((round(x, 2), round(y, 2)), [])

    def toprak(self, x, y):
        self.katman['sembol'].append('<g class="toprak" data-ag="GND"><path d="M%s %sV%s"/><path d="M%s %sH%s M%s %sH%s M%s %sH%s"/></g>' % (
            x, y, y + 10, x - 11, y + 10, x + 11, x - 7, y + 15, x + 7, x - 3, y + 20, x + 3))
        self.guc.append(('GND', (round(x, 2), round(y, 2))))

    def ray(self, ad, x, y, yon='yukari'):
        if yon == 'yukari':
            self.katman['sembol'].append('<g class="ray" data-ag="%s"><path d="M%s %sV%s M%s %sH%s"/></g>' % (escape(ad), x, y, y - 12, x - 10, y - 12, x + 10))
            self._yaz(x, y - 18, ad, 'rayad')
        else:
            self.katman['sembol'].append('<g class="ray" data-ag="%s"><path d="M%s %sV%s M%s %sH%s"/></g>' % (escape(ad), x, y, y + 12, x - 10, y + 12, x + 10))
            self._yaz(x, y + 26, ad, 'rayad')
        self.guc.append((ad, (round(x, 2), round(y, 2))))

    def etiket(self, ad, x, y, yon='sag'):
        """ag etiketi; ayni adli etiketler elektriksel olarak birlesiktir."""
        if yon == 'sag':
            self._yaz(x + 6, y - 4, ad, 'agad', 'start')
        elif yon == 'sol':
            self._yaz(x - 6, y - 4, ad, 'agad', 'end')
        elif yon == 'yukari':
            self._yaz(x, y - 8, ad, 'agad', 'middle')
        else:
            self._yaz(x, y + 16, ad, 'agad', 'middle')
        self.etiketler.append((ad, (round(x, 2), round(y, 2))))

    def ic_bag(self, a, b, etiket='içeriden bağlı'):
        """Bir parcanin iki ayagi icerden bagliysa kesikli cizgiyle gosterir ve denetimde birlesik sayar."""
        pa, pb = self.pinler[a], self.pinler[b]
        self.katman['nokta'].append('<path class="pinuc" stroke-dasharray="5 4" d="M%s %sL%s %s"/>' % (pa[0] + 18, pa[1] + 9, pb[0] - 18, pb[1] + 9))
        self.teller.append((pa, pb))
        self.noktalar.setdefault(pa, []); self.noktalar.setdefault(pb, [])

    def not_(self, x, y, metin, anchor='start', sinif='not'):
        self._yaz(x, y, metin, sinif, anchor)

    def bolge(self, x, y, w, h, baslik):
        self.katman['tel'].insert(0, '<rect class="bolge" x="%s" y="%s" width="%s" height="%s" rx="8"/>' % (x, y, w, h))
        self._yaz(x + 10, y + 16, baslik, 'bolgead', 'start')

    def isaret(self, no, x, y):
        self.isaretler.append(no)
        self.katman['isaret'].append('<g class="isaret" data-no="%s" transform="translate(%s,%s)"><circle r="10"/><text y="4" text-anchor="middle">%s</text></g>' % (no, x, y, no))

    # ------------------------------------------------------------ denetim
    def denetle(self, aglar):
        """aglar: {ag_adi: {(ref,pin),...}} gercek ag listesi.
        Cizilen tel/etiket/guc birlesimlerinden elektriksel bilesenler cikarilir ve gercek agla kiyaslanir."""
        ebeveyn = {}
        def bul(a):
            ebeveyn.setdefault(a, a)
            while ebeveyn[a] != a:
                ebeveyn[a] = ebeveyn[ebeveyn[a]]
                a = ebeveyn[a]
            return a
        def bir(a, b):
            ebeveyn[bul(a)] = bul(b)
        for (a, b) in self.teller:
            bir(('n',) + a, ('n',) + b)
        for p in self.noktalar:
            bul(('n',) + p)
        for (ad, p) in self.etiketler + self.guc:
            bir(('n',) + p, ('ad', ad))
        # T baglantilari: bir telin ucu baska telin ic noktasina degiyorsa, nokta() ile ilan edilmis olmali
        for (ref, no), p in self.pinler.items():
            bir(('n',) + p, ('pin', ref, no))
        gercek = {}
        for ad, kume in aglar.items():
            for rp in kume:
                gercek[rp] = ad
        kok_ag = {}
        for (ref, no), p in self.pinler.items():
            if (ref, no) in gercek:
                kok_ag.setdefault(bul(('n',) + p), gercek[(ref, no)])
        for (ad, p) in self.etiketler + self.guc:
            kok_ag.setdefault(bul(('n',) + p), ad)
        for tid, p in enumerate(self.tel_ilk):
            self.tel_ag[tid] = kok_ag.get(bul(('n',) + p), '')
        bilesen = {}
        for (ref, no) in self.pinler:
            bilesen.setdefault(bul(('pin', ref, no)), []).append((ref, no))
        hatalar = []
        for kok, pinler in bilesen.items():
            adlar = {gercek.get(rp, '(agsiz)') for rp in pinler}
            if len(adlar) > 1:
                hatalar.append('KISA DEVRE: ayni telde farkli aglar %s <- %s' % (sorted(adlar), pinler[:6]))
        per_ag = {}
        for kok, pinler in bilesen.items():
            for rp in pinler:
                per_ag.setdefault(gercek.get(rp, '(agsiz)'), set()).add(kok)
        for ad, kokler in per_ag.items():
            if len(kokler) > 1 and ad != '(agsiz)':
                hatalar.append('KOPUK: %s agi cizimde %d ayri parcada' % (ad, len(kokler)))
        # cizilen her parcanin cizilen pinleri gercek ag listesinde var mi
        for (ref, no) in self.pinler:
            if (ref, no) not in gercek:
                hatalar.append('AGSIZ PIN cizildi: %s.%s' % (ref, no))
        return hatalar

    # ------------------------------------------------------------ cikti
    def svg(self):
        k = self.katman
        import re as _re
        def _ag(m):
            return escape(self.tel_ag.get(int(m.group(1)), ''))
        for anahtar in ('tel',):
            k[anahtar] = [_re.sub(r'@@T(\d+)@@', _ag, x) for x in k[anahtar]]
        return ('<svg class="sema" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" role="img" aria-label="%s">%s</svg>' % (
            self.w, self.h, escape(self.ad), ''.join(k['tel'] + k['sembol'] + k['nokta'] + k['yazi'] + k['isaret'])))
