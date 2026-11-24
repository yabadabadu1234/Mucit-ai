"""Kur'ân kök atlası -- yaklaştırma usulüyle kitap (F 3-I 412).
Tek komut: python3 kok_kitabi.py [--dene 1,2] [--cilt N] [--ikinci]
Basamaklar: I bütün harita · II bölge haritaları · III sûre haritası · IV kısım haritası · V âyet sayfası · VI kök (lügat) sayfaları.
Harita şekilleri kök uzayının yerleşiminden (yerlesim_onbellek.json) vektörel (SVG) çizilir; âyet metni, meal ve kök sayfaları kaynaktan aynen gelir.
Çıktı: kok_kitabi/cilt_<n>.pdf ve kok_kitabi/KITAP_DURUMU.json"""
import runpy, json, sys, re, html, math, pathlib, collections, functools, subprocess, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
NS = runpy.run_path(str(HERE / 'kok_uzayi_uret.py'))
R = NS['R']; SUR = NS['SUR']; KUME = NS['KUME']; KA = NS['KA']; KEL = NS['KEL']; AYK = NS['AYK']; SAY = NS['SAY']; ILKT = NS['ILKT']; SAYFA = NS['SAYFA']; KL = NS['KL']; NO = NS['NO']; KU = R['KU']
from PIL import ImageFont
import mushaf_dizgi as MD
import lugat_sayfa as LS
import edat_manalari as EM
import morfo as MF
CIKTI = HERE / 'kok_kitabi'
YAZI = HERE / 'yazi'
SERIF = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 100)
AMIRI_L = ImageFont.truetype(str(HERE / 'yazi' / 'Amiri-Regular.ttf'), 100)
def genis(t, f=1.0): return SERIF.getlength(t) / 100.0 * f
E = html.escape
def kisa(s, n=70): s = ' '.join(str(s).split()); return s if len(s) <= n else s[:n - 1].rstrip() + '…'

# ---------------------------------------------------------------- veri düzeni
SU = {int(r[4].split(' ')[0]): r for r in R['SU']}                      # sûre odaları
KI = collections.defaultdict(list)
for r in R['KI']: KI[r[6]].append(r)
AY = {a[4]: a for a in R['AY']}                                         # âyet odaları
GP = collections.defaultdict(list)
for p in R['GP']: GP[p[10]].append(p)
ME = R['ME']; AK = R['AK']; DS = R['DS']; KF = R['KF']
ORD = list(AK.keys()); ORI = {k: i for i, k in enumerate(ORD)}
KOK_SIRASI = [(k, fl) for k, fl, _ in KL]
OCC = collections.defaultdict(list)                                    # (kök, fl) -> âyet anahtarları (mushaf sırası)
for _k in AK:
    for _x in AK[_k]: OCC[(_x[0], _x[1])].append(_k)
SUREKOK = collections.defaultdict(collections.Counter)                 # sûre -> {(kök, fl): âyet sayısı}
for _k in AK:
    for _x in AK[_k]: SUREKOK[int(_k.split(':')[0])][(_x[0], _x[1])] += 1
SIRA_KOK = sorted(KOK_SIRASI, key=lambda x: ORI[ILKT[x]])            # ilk geçiş sırasıyla
ESIKLER = [50, 100, 250, 500, 750, 1000, 1250, 1500, 1750]                                # NO sırası
YENI = {key: [x for x in AK[key] if x[2]] for key in ORD}
YENI_AYET = [k for k in ORD if YENI[k]]
CUM = []; _c = 0
for key in ORD: _c += len(YENI[key]); CUM.append(_c)
TOPK = CUM[-1]
SADI = {s: r[4].split(' · ', 1)[1] for s, r in SU.items()}              # 'Bakara (البقرة)'
SLAT = {s: SADI[s].split(' (')[0] for s in SU}
AYKIS = {}                                                              # âyet -> kısım satırı
for s, L in KI.items():
    for k in L:
        for key, a in AY.items():
            pass
_AYS = collections.defaultdict(list)
for key, a in AY.items(): _AYS[int(key.split(':')[0])].append(a)
for s, L in KI.items():
    for a in _AYS[s]:
        cx, cy = a[0] + a[2] / 2, a[1] + a[3] / 2
        for k in L:
            if k[0] <= cx <= k[0] + k[2] and k[1] <= cy <= k[1] + k[3]: AYKIS[a[4]] = k; break
assert len(AYKIS) == 6236, len(AYKIS)
KIS_AYET = collections.defaultdict(list)                                # kısım satırı id -> âyet anahtarları (mushaf sırası)
for key in ORD: KIS_AYET[id(AYKIS[key])].append(key)
KISIM_NO = {}                                                           # id(kısım satırı) -> (sûre, sıra)
for s, L in KI.items():
    for i, k in enumerate(L): KISIM_NO[id(k)] = (s, i)
KOKYER = {}                                                             # (kök, fl) -> GP satırı
for p in R['GP']: KOKYER[(p[6], p[7])] = p
_, KSZ = LS.hepsi()
LUGAT_KOMBO = MF.lugat_kelimeleri()                                      # (k,1) -> {parça dizisi: [adet, ilk 's:a']}
KOK_ISIM = MF.kok_isimleri()                                            # kök -> {(lem, sınıf): [adet, ilk 's:a']}

# ---------------------------------------------------------------- vektörel harita
RENK_FILL = {0: '#fbf3d8', 1: '#e6eef7'}
class Harita:
    """Vektörel harita. Her öğe (y0, y1, xml, yasak) olarak tutulur; yasak=True öğeler (yazı, kart) şerit keserken bölünmez."""
    KCAP = 2.0
    def __init__(self, x, y, w, h, wmm, hmm=None, ad='', kcap=None):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.k = min(wmm / w, hmm / h) if hmm else min(wmm / w, kcap or self.KCAP)
        self.o = []; self.ad = ad
    def mm(self, v): return v / self.k                                   # milimetre -> dünya birimi
    def px(self, v): return v * self.k                                   # dünya birimi -> milimetre
    def ekle(self, xml, y0, y1, yasak=False): self.o.append((y0, y1, xml, yasak))
    def dik(self, x, y, w, h, fill, st='#555', sw=0.15, r=0.0, dash=None, ek='', yasak=False):
        self.ekle('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="%s" stroke="%s" stroke-width="%.3f"%s%s%s/>' % (x, y, w, h, fill, st, sw, ' rx="%.2f"' % r if r else '', ' stroke-dasharray="%s"' % dash if dash else '', ' ' + ek if ek else ''), y, y + h, yasak)
    def yaz(self, t, x, y, f, fill='#2b2410', anchor='middle', fam='FreeSerif', bold=False, ek=''):
        self.ekle('<text x="%.3f" y="%.3f" font-size="%.3f" text-anchor="%s" fill="%s" font-family="%s"%s%s>%s</text>' % (x, y, f, anchor, fill, fam, ' font-weight="700"' if bold else '', ' ' + ek if ek else '', E(t)), y - f * 0.95, y + f * 0.4, True)
    def sigdir(self, t, x, y, w, h, fam='FreeSerif', bold=False, fill='#2b2410', alt_mm=1.5, ust_mm=None):
        """kutuya sığan en büyük yazı; render ölçüsü alt_mm'den küçükse yazılmaz"""
        g = genis(t, 1.0) * (1.08 if bold else 1.0)
        f = min(w * 0.94 / max(g, 1e-6), h * 0.8)
        if ust_mm: f = min(f, self.mm(ust_mm))
        if self.px(f) < alt_mm: return False
        self.yaz(t, x + w / 2, y + h / 2 + f * 0.33, f, fill=fill, fam=fam, bold=bold); return True
    TANIM = '<defs><pattern id="tar" patternUnits="userSpaceOnUse" width="1.3" height="1.3" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.3" stroke="#555" stroke-width="0.16" opacity=".45"/></pattern></defs>'
    def svg(self, ek_stil='', y0=None, y1=None):
        y0 = self.y if y0 is None else y0; y1 = self.y + self.h if y1 is None else y1
        W, H = self.w * self.k, (y1 - y0) * self.k
        ic = ''.join(o[2] for o in self.o if o[1] >= y0 - 0.5 and o[0] <= y1 + 0.5)
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.3f %.3f %.3f %.3f" width="%.3fmm" height="%.3fmm" style="display:block;%s">%s%s</svg>' % (self.x, y0, self.w, y1 - y0, W, H, ek_stil, self.TANIM, ic)
    def kesler(self, maxmm=38.0):
        """Şerit kesim yerleri: yazı ve kartların arasındaki boşluklardan, şerit boyu maxmm'yi aşmayacak biçimde."""
        top, bot = self.y, self.y + self.h; mx = self.mm(maxmm)
        yas = sorted((max(a, top), min(b, bot)) for a, b, _, y in self.o if y and b > top and a < bot)
        birl = []
        for a, b in yas:
            if birl and a <= birl[-1][1]: birl[-1][1] = max(birl[-1][1], b)
            else: birl.append([a, b])
        bos = []; c = top
        for a, b in birl:
            if a > c: bos.append((c, a))
            c = max(c, b)
        if c < bot: bos.append((c, bot))
        cuts = [top]; c = top; zorunlu = 0
        while bot - c > mx:
            hedef = c + mx; n = None
            for ga, gb in reversed(bos):
                if ga <= hedef and gb > c + 0.3 * mx:
                    n = min(hedef, gb) if ga <= hedef <= gb else (ga + gb) / 2
                    if n > c + 0.3 * mx: break
                    n = None
            if n is None: n = hedef; zorunlu += 1
            cuts.append(n); c = n
        cuts.append(bot); self.zorunlu = zorunlu
        return cuts
    def sutun_yerlestir(self, wmm, kmax, aralik=3.0, kolon=3):
        """Dar harita için sütun sayısını ve ölçeği seçer: genişliği en az %85 doldurmayı hedefler."""
        aday = []
        for c in range(1, kolon + 1):
            k = min(kmax, (wmm - (c - 1) * aralik) / (c * self.w)); aday.append((c, k, (c * self.w * k + (c - 1) * aralik) / wmm))
        sec = next((a for a in aday if a[2] >= 0.85 and a[1] >= 0.7 * min(kmax, aday[0][1])), max(aday, key=lambda a: (round(a[2], 1), a[1])))
        self.sut, self.k = sec[0], sec[1]; return self
    def _bos(self, lo, hi):
        yas = sorted((max(a, lo), min(b, hi)) for a, b, _, y in self.o if y and b > lo and a < hi)
        birl = []
        for a, b in yas:
            if birl and a <= birl[-1][1]: birl[-1][1] = max(birl[-1][1], b)
            else: birl.append([a, b])
        return birl
    def kes_n(self, lo, hi, n):
        """[lo,hi] aralığını n parçaya, ideal eşit yerlerin en yakın serbest noktasından keser (yazı ve kartın içinden kesmez)."""
        birl = self._bos(lo, hi); out = [lo]
        for i in range(1, n):
            ideal = lo + (hi - lo) * i / n; y = ideal
            for a, b in birl:
                if a < ideal < b: y = a if ideal - a <= b - ideal else b; break
            out.append(max(y, out[-1])); 
        out.append(hi); return out
    def serit_html(self, maxmm=38.0, kolon=3, aralik=3.0):
        """Haritayı yığılan şeritler olarak verir; dar harita sütunlara bölünür, şeritler satır satır (sağdan sola) dizilir."""
        top, bot = self.y, self.y + self.h; Wmm = self.w * self.k
        sut = getattr(self, 'sut', None) or (max(1, min(kolon, int((122 + aralik) // (Wmm + aralik)))) if Wmm < 60 else 1)
        if sut == 1:
            cuts = self.kesler(maxmm)
            return '<div class="hm">%s</div>' % ''.join('<div class="sr">%s</div>' % self.svg('', a, b) for a, b in zip(cuts[:-1], cuts[1:]))
        bant = self.kes_n(top, bot, sut); n = max(1, math.ceil(max(b - a for a, b in zip(bant[:-1], bant[1:])) * self.k / maxmm))
        kol = [self.kes_n(a, b, n) for a, b in zip(bant[:-1], bant[1:])]
        satirlar = []
        for r in range(n):
            hucre = ''.join('<div class="sr">%s</div>' % self.svg('', c[r], c[r + 1]) for c in kol)
            satirlar.append('<div class="sr2">%s</div>' % hucre)
        return '<div class="hm ms">%s</div>' % ''.join(satirlar)

def boy_kutu(r, kenar=2.0): return r[0] - kenar, r[1] - kenar, r[2] + 2 * kenar, r[3] + 2 * kenar

def harita_butun(vurgu=None, kume=None, wmm=122, adlar=False, bolge=None):
    """Bütün harita: sûre odaları küme rengiyle. vurgu: (x,y,w,h) kırmızı çerçeve; kume: yalnız bu küme koyu."""
    h = Harita(0, 0, R['W'], R['H'], wmm)
    for s, r in SU.items():
        sol = kume is not None and r[8] != kume
        h.dik(r[0], r[1], r[2], r[3], r[6] if not sol else '#eeeeee', '#4a3f28' if not sol else '#bbbbbb', 0.5, 1.0)
        if adlar and not sol:
            if not h.sigdir(SLAT[s], r[0], r[1], r[2], r[5], bold=True, alt_mm=1.6): h.sigdir('%d' % s, r[0], r[1], r[2], r[3], bold=True, alt_mm=1.6, ust_mm=2.6)
        elif not sol:
            h.sigdir('%d' % s, r[0], r[1], r[2], r[3], bold=True, alt_mm=1.8, ust_mm=2.6)
    if vurgu: h.dik(vurgu[0], vurgu[1], vurgu[2], vurgu[3], 'none', '#c0392b', max(1.4, h.mm(0.5)), 0)
    return h

def konum_haritasi(kutu, wmm=30):
    """Küçük 'buradasınız' haritası: bütün harita üstünde kırmızı çerçeve."""
    h = harita_butun(None, None, wmm)
    h.o = []
    h.ekle('<rect x="0" y="0" width="%.1f" height="%.1f" fill="#fffdf6" stroke="#8a7f62" stroke-width="2"/>' % (R['W'], R['H']), 0, R['H'])
    for r in SU.values(): h.ekle('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" stroke="none"/>' % (r[0], r[1], r[2], r[3], r[6]), r[1], r[1] + r[3])
    x, y, w, hh = kutu; kk = max(w, hh * 0.001); mn = h.mm(0.7)
    h.ekle('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" stroke="#c0392b" stroke-width="%.2f"/>' % (x - mn, y - mn, w + 2 * mn, hh + 2 * mn, max(2.4, h.mm(0.45))), y - mn, y + hh + mn)
    return h.svg()

def ayet_kutusu(h, a, yeni_cizgi=True):
    key = a[4]; yn = a[7] > 0; su = SU[int(key.split(':')[0])]
    fill = su[7] if yn else '#f4f1e6'
    h.dik(a[0], a[1], a[2], a[3], fill, '#4a3f28' if yn else '#8a7f62', 0.28 if yn else 0.2, 0.35, None if yn else '0.7 0.5')
    if not yn: h.ekle('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="url(#tar)" stroke="none"/>' % (a[0], a[1], a[2], a[3]), a[1], a[1] + a[3])

def ayet_icerik(h, a, metin=True, meal=True, koklar=True, kok_yazi=True):
    """Âyet odasının içi: Arapça satırlar (kelime yeri aynen), meal satırları, kök hücreleri."""
    key = a[4]; st = DS.get(key, ''); f = min(R['FA'], R['FA'] * (a[2] - 0.3) / max(max((sum(MD.gen(t) for t in l[0]) + (len(l[0]) - 1) * MD.gen(' ') + sum(l[1]) * MD.HG + (l[2] if l[3] in 'RM' else 0)) for l in a[6]), 1e-6))
    if metin:
        sp = MD.gen(' ') * f
        for l in a[6]:
            wt = (sum(MD.gen(t) for t in l[0]) + (len(l[0]) - 1) * MD.gen(' ') + sum(l[1]) * MD.HG) * f
            ins = l[2] * f; xr = a[0] + a[2] - 0.15 - ins if l[3] == 'R' else a[0] + 0.15 + (ins if l[3] == 'M' else 0) + wt
            y = a[1] + 0.15 + (l[4] + 0.55) * f * R['SATIR']
            for k, t in enumerate(l[0]):
                if k: xr -= sp
                if l[1][k]: xr -= MD.HG * f
                d = st[l[5][k]] if st and l[5][k] < len(st) else '0'
                h.yaz(t, xr, y + f * 0.3, f, fill='#8a5a00' if d == '1' else '#2b2410', anchor='end', fam='Amiri', bold=d == '1', ek='data-r="%.2f,%.2f,%.2f,%.2f"' % (a[0], a[1], a[2], a[3]))
                xr -= MD.gen(t) * f
    if meal and a[9]:
        fm = R['FM']
        for j, ln in enumerate(a[9]):
            gl = AMIRI_L.getlength(ln) / 100.0 * fm; izin = a[2] - 0.6
            tl = ' textLength="%.3f" lengthAdjust="spacingAndGlyphs"' % izin if gl > izin else ''
            h.yaz(ln, a[0] + 0.3, a[1] + a[5] + (j + 0.5) * fm * R['MS'] + fm * 0.33, fm, fill='#4a3f28', anchor='start', fam='Amiri', ek='data-r="%.2f,%.2f,%.2f,%.2f"%s' % (a[0], a[1], a[2], a[3], tl))
    if koklar:
        for p in GP.get(key, []):
            h.dik(p[0] + p[2] * 0.03, p[1] + p[3] * 0.03, p[2] * 0.94, p[3] * 0.94, RENK_FILL[p[7]], '#8a6d1d' if not p[7] else '#2f6fb3', 0.15, 0.3, yasak=True)
            if kok_yazi:
                f_ = min(p[2] * 0.62 / max(MD.gen(p[6]), 1e-6), p[2] * 0.55)
                if h.px(f_) >= 1.2: h.yaz(p[6], p[0] + p[2] / 2, p[1] + p[3] * 0.42 + f_ * 0.3, f_, fam='Amiri', bold=True, ek='data-r="%.2f,%.2f,%.2f,%.2f"' % (p[0], p[1], p[2], p[3]))
                an = KA.get(p[6], '') if not p[7] else ''
                if an:
                    t = an.split(':', 1)[1].strip() if ':' in an else an
                    t = kisa(t.split(';')[0], 22); f2 = min(p[2] * 0.9 / max(genis(t), 1e-6), p[3] * 0.11)
                    if h.px(f2) >= 1.15: h.yaz(t, p[0] + p[2] / 2, p[1] + p[3] * 0.86, f2, fill='#3a3220', ek='data-r="%.2f,%.2f,%.2f,%.2f"' % (p[0], p[1], p[2], p[3]))

def harita_sure(s, wmm=122, hmm=112, vurgu=None):
    r = SU[s]; x, y, w, hh = boy_kutu(r, 1.2); h = Harita(x, y, w, hh, wmm, None, kcap=1.2).sutun_yerlestir(wmm, 1.6)
    h.dik(r[0], r[1], r[2], r[3], r[6], '#4a3f28', 0.4, 1.0)
    h.sigdir(SADI[s].split(' (')[0] + ' (%d)' % s, r[0], r[1], r[2], r[5], bold=True, alt_mm=1.6, ust_mm=3.4)
    for k in KI[s]:
        h.dik(k[0], k[1], k[2], k[3], k[7], '#4a3f28', 0.25, 0.5)
        h.sigdir(k[4], k[0], k[1], k[2], k[5], bold=True, fill='#1f4f86', alt_mm=1.3, ust_mm=2.4)
    for a in _AYS[s]:
        ayet_kutusu(h, a)
        if h.px(min(a[2], a[3])) > 2.2:
            h.sigdir(a[4].split(':')[1], a[0], a[1], a[2], min(a[3], 4.0), bold=True, alt_mm=1.3, ust_mm=2.2)
    for a in _AYS[s]:
        for p in GP.get(a[4], []):
            h.dik(p[0], p[1], p[2], p[3], RENK_FILL[p[7]], '#8a6d1d' if not p[7] else '#2f6fb3', 0.12, 0.2)
    if vurgu: h.dik(vurgu[0], vurgu[1], vurgu[2], vurgu[3], 'none', '#c0392b', max(0.8, h.mm(0.45)), 0)
    return h

def kisim_parcalari(k, wmm=122, hmm=124, mm_birim=0.95):
    """Kısım odasını okunur ölçekte (en az mm_birim mm/birim) parçalara böler; kesim, âyet odalarını kesmeyen yerden seçilir."""
    s = k[6]; w, hh = k[2], k[3]; kx, ky = k[0], k[1]
    ay = [a for key in KIS_AYET[id(k)] for a in [AY[key]]]
    mw, mh = wmm / mm_birim, 1e9
    def kes(lo, hi, maks, yon):
        if hi - lo <= maks: return [lo, hi]
        sn = [lo]; c = lo
        while hi - c > maks:
            ideal = c + maks; best = None
            for dx in [i * 0.5 for i in range(0, 120)]:
                x = ideal - dx
                if x <= c + maks * 0.5: break
                n = sum(1 for a in ay if (a[yon] < x < a[yon] + a[yon + 2]))
                if best is None or n < best[0]: best = (n, x)
                if n == 0: break
            sn.append(best[1]); c = best[1]
        sn.append(hi); return sn
    xs = kes(kx, kx + w, mw, 0); ys = kes(ky, ky + hh, mh, 1)
    P = []
    for yj in range(len(ys) - 1):
        for xi in range(len(xs) - 2, -1, -1):               # sağdan sola
            P.append((xs[xi], ys[yj], xs[xi + 1] - xs[xi], ys[yj + 1] - ys[yj]))
    return P

def harita_kisim(k, parca, wmm=122, hmm=124):
    s = k[6]; x, y, w, hh = parca; kk = 0.6
    kf = math.sqrt(0.85 * 122 * 172 / (w * hh)); kmax = max(0.95, min(4.5, kf))
    h = Harita(x, y, w, hh, wmm, None, kcap=kmax).sutun_yerlestir(wmm, kmax)
    h.dik(k[0], k[1], k[2], k[3], k[7], '#1f4f86', 0.3, 0.6)
    h.sigdir(k[4], k[0], k[1], k[2], k[5], bold=True, fill='#1f4f86', alt_mm=1.4, ust_mm=2.6)
    for key in KIS_AYET[id(k)]:
        a = AY[key]
        if a[0] > x + w or a[0] + a[2] < x or a[1] > y + hh or a[1] + a[3] < y: continue
        ayet_kutusu(h, a); ayet_icerik(h, a)
        r = min(0.9, a[2] / 9)
        h.ekle('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="#6b7b4a"/>' % (a[0] + r * 1.1, a[1] + r * 0.2, r), a[1] + r * 0.2 - r, a[1] + r * 0.2 + r, True)
        h.yaz(key.split(':')[1], a[0] + r * 1.1, a[1] + r * 0.2 + r * 0.33, r * 0.95, fill='#fff', bold=True)
    return h

def harita_ayet_odasi(key, wmm=100, hmm=62):
    a = AY[key]; h = Harita(a[0] - 0.6, a[1] - 0.6, a[2] + 1.2, a[3] + 1.2, wmm, hmm)
    ayet_kutusu(h, a); ayet_icerik(h, a); return h

def konum_kisim(k, a, wmm=34):
    """Âyetin kısım içindeki yeri: kısım odası küçük, âyet kırmızı."""
    x, y, w, hh = boy_kutu(k, 1.0); h = Harita(x, y, w, hh, wmm, wmm)
    h.dik(k[0], k[1], k[2], k[3], k[7], '#1f4f86', 0.4, 0.5)
    for key in KIS_AYET[id(k)]:
        b = AY[key]; yn = b[7] > 0
        h.dik(b[0], b[1], b[2], b[3], '#e9d9a0' if yn else '#f4f1e6', '#4a3f28', 0.25, 0.3)
    h.dik(a[0], a[1], a[2], a[3], '#e8a79d', '#c0392b', max(0.7, h.mm(0.4)), 0.3)
    return h.svg()

# ---------------------------------------------------------------- sayfa gövdeleri
ILKL = NS['ILKL']
BAS = ['I Bütün harita', 'II Bölge', 'III Sûre', 'IV Kısım', 'V Âyet', 'VI Kök']
REF = {}                                                                # kimlik -> (cilt, sayfa); ikinci geçişte doludur
KAYIT = []                                                              # bu cildin bağlantı kimlikleri
def ref(i, kisa_=False):
    c, p = REF.get(i, (0, 0)); return '%d/%04d' % (c, p)
def anc(i): KAYIT.append(i); return 'id="%s"' % i
def AR(s): return '<span class="ar">%s</span>' % s

def sf(i, basamak, yol, icerik, sinif=''):
    bs = ''.join('<span class="%s">%s</span>' % ('a' if n + 1 == basamak else '', t) for n, t in enumerate(BAS))
    tag = {1: 'h1', 2: 'h1', 3: 'h1', 4: 'h2', 5: 'h3'}[basamak]
    return '<section class="sf %s" %s><div class="bs">%s</div><%s class="yol">%s</%s>%s</section>' % (sinif, anc(i), bs, tag, re.sub(r'<[^>]+>', '', yol), tag, icerik)

def yol_sure(s): return 'Harita › %s › %s' % (KUME[s], SADI[s])
def yol_kisim(k): s = k[6]; return yol_sure(s) + ' › %s' % E(k[4])

def anlam(k, fl, n=60):
    if fl: return kisa(EM.LEX[k][1], n)
    t = KA.get(k, ''); return kisa(t.split(';')[0] if ';' in t else t, n)

def kok_no(k, fl): return NO[(k, fl)]

def tokenler(key):
    a = AY[key]; T = {}
    for l in a[6]:
        for k, t in enumerate(l[0]): T[l[5][k]] = t
    return [T[i] for i in sorted(T)], DS.get(key, '')

def ayet_arapca(key, buyuk=True):
    T, st = tokenler(key)
    return ' '.join('<span class="w%s">%s</span>' % (st[i] if st and i < len(st) else '0', t) for i, t in enumerate(T))

def kelime_tablosu(key):
    """Hizalı âyetlerde kelime -> kök -> anlam; yeni kök ● altın, tekrar ○ ilk geçiş sayfasıyla."""
    s, ay = map(int, key.split(':')); V = NS['V_'] if False else None
    kw = KEL.get(key, {})
    if not kw or key not in DS: return ''
    T, st = tokenler(key)
    kelimeler = [(i, t) for i, t in enumerate(T) if st[i] != '0' or True]
    # kelime numarası = imza olmayan belirteçlerin sırası; DS dizisi imzalar için '0' verir, kök olmayan kelimeler de '0' olabilir
    sig = [MD.isaret(t) for t in T]
    j = 0; satir = []
    for i, t in enumerate(T):
        if sig[i]: continue
        j += 1
        for (k, fl) in kw.get(j, []):
            yeni = ILKL.get((k, fl)) and ILKL[(k, fl)][:3] == (s, ay, j)
            no = kok_no(k, fl)
            satir.append('<tr><td class="ar k">%s</td><td class="ar k">%s</td><td>%s</td><td class="m">%s</td></tr>' % (t, k, E(anlam(k, fl, 54)), ('<b>● yeni</b> · s. %s' % ref('K%d' % no)) if yeni else ('○ ilk %s · s. %s' % (ILKT[(k, fl)], ref('K%d' % no)))))
    if not satir: return ''
    return '<table class="kt"><tr><th>kelime</th><th>kök</th><th>anlamı</th><th>durum</th></tr>%s</table>' % ''.join(satir)

def ilerleme(o):
    return '<div class="ilr">kök hazinesi: <b>%d</b> / %d (%%%.1f)<div class="bar"><i style="width:%.1f%%"></i></div></div>' % (CUM[o], TOPK, 100 * CUM[o] / TOPK, 100 * CUM[o] / TOPK)

def sonraki_gecisler(x, key, n=3):
    L = OCC[(x[0], x[1])]; i = L.index(key); return L[i + 1:i + 1 + n]

def sayfa_ayet(key):
    s, ay = map(int, key.split(':')); a = AY[key]; k = AYKIS[key]; o = ORI[key]; yeni = YENI[key]
    kno = KISIM_NO[id(k)]
    onc = next((ORD[j] for j in range(o - 1, -1, -1) if YENI[ORD[j]]), None); son = next((ORD[j] for j in range(o + 1, len(ORD)) if YENI[ORD[j]]), None)
    mil = [e for e in ESIKLER if CUM[o] - len(yeni) < e <= CUM[o]]
    ics = ['<div class="ah"><div><span class="no">%s</span> <span class="rz">✦ +%d yeni kök</span><div class="gr">%s · %s</div></div><div class="lk">%s</div></div>' % (key, len(yeni), E(SADI[s]), E(KUME[s]), konum_kisim(k, a, 22)),
           '<div class="arb">%s</div>' % ayet_arapca(key), '<div class="ml">%s<div class="kay">meal: Hayrat Neşriyat</div></div>' % E(ME[key]),
           kelime_tablosu(key)]
    if not ics[-1]:
        ics[-1] = '<table class="kt"><tr><th>kök</th><th>anlamı</th><th>durum</th></tr>%s</table>' % ''.join('<tr><td class="ar k">%s</td><td>%s</td><td class="m">%s</td></tr>' % (x[0], E(anlam(x[0], x[1], 54)), ('<b>● yeni</b> · s. %s' % ref('K%d' % kok_no(x[0], x[1]))) if x[2] else ('○ ilk %s · s. %s' % (x[3], ref('K%d' % kok_no(x[0], x[1]))))) for x in AK[key])
    oda = '<div class="hm" style="flex:none;width:auto;background:none">%s</div>' % harita_ayet_odasi(key, 100, 46).svg()
    sg = ''.join('<span class="sg"><span class="ar">%s</span> → %s</span>' % (x[0], ' · '.join('%s <small>s. %s</small>' % (g, ref('A' + g.replace(':', '_'))) for g in sonraki_gecisler(x, key)) or '<small>başka âyette geçmez</small>') for x in yeni)
    yan = ['<div class="gr"><b>Haritadaki odası</b> solda. <b>Bu yeni köklerin sonraki geçişleri</b> (en çok üç âyet): %s</div>' % sg, ilerleme(o)]
    if mil: yan.append('<div class="mil">★ Bu âyetle kök hazineniz %s eşiğini aşıyor.</div>' % ', '.join(str(e) for e in mil))
    yan.append('<div class="not">Bu âyetle gelen %d yeni kökün lügat sayfaları bu sayfadan hemen sonra gelir: %s</div>' % (len(yeni), ' · '.join('<span class="ar">%s</span>' % x[0] for x in yeni)))
    ics.append('<div class="oda2">%s<div class="yan">%s</div></div>' % (oda, ''.join(yan)))
    ics.append('<div class="gr">önceki yeni kök âyeti: %s · sonraki: %s · kısım haritası: s. %s · sûre kapısı: s. %s &nbsp; ☐ okudum &nbsp; ☐ ezberledim</div>' % (('%s s. %s' % (onc, ref('A' + onc.replace(':', '_')))) if onc else '—', ('%s s. %s' % (son, ref('A' + son.replace(':', '_')))) if son else '—', ref('KS%d_%d_1' % kno), ref('S%d' % s)))
    return sf('A' + key.replace(':', '_'), 5, '%s › %s › <b>%s</b>' % (yol_sure(s), E(k[4]), key), ''.join(ics), 'ay')

def blok_tekrar(keys):
    """Yeni kök getirmeyen, ardışık âyetler: kısa girişler; her kök ilk geçişine bağlanır."""
    o = ['<div class="yh">∅ Yeni kök getirmeyen âyetler · %s – %s <span>(bütün kökleri daha evvel görüldü)</span></div>' % (keys[0], keys[-1])]
    for key in keys:
        ch = ' '.join('<span class="ck"><span class="ar">%s</span> <small>%s · s. %s</small></span>' % (x[0], x[3], ref('K%d' % kok_no(x[0], x[1]))) for x in AK[key])
        o.append('<div class="ye" %s><div class="yn"><b>%s</b> ∅ <span class="gr">kök hazinesi %d</span></div><div class="arb k2">%s</div><div class="ml">%s</div><div class="cl">%s</div></div>' % (anc('A' + key.replace(':', '_')), key, CUM[ORI[key]], ayet_arapca(key), E(ME[key]), ch))
    return ''.join(o)

CESIT = [('masdar', lambda g: g.startswith('masdar ·')), ('ism-i merre', lambda g: g.startswith('ism-i merre')), ('ism-i hey’et', lambda g: g.startswith('ism-i hey')),
         ('ism-i fâil', lambda g: g.startswith('ism-i fâil')), ('ism-i mef‘ûl', lambda g: g.startswith('ism-i mef‘ûl')), ('sıfat-ı müşebbehe', lambda g: g == 'sıfat-ı müşebbehe'),
         ('mübalağa (mübalağalı ism-i fâil)', lambda g: g == 'mübalağa'), ('ism-i tafdîl', lambda g: g.startswith('tafdîl')), ('ism-i mekân ve zaman', lambda g: g.startswith('mekân/zaman')),
         ('masdar-ı mîmî', lambda g: g.startswith('masdar-ı mîmî') or g.startswith('mekân/zaman/masdar-ı mîmî')), ('ism-i âlet', lambda g: g.startswith('âlet')), ('tasğîr', lambda g: g.startswith('tasğîr')),
         ('ism-i mensûb', lambda g: g == 'mensûb'), ('masdar-ı sınâî', lambda g: g.startswith('masdar-ı sınâî')), ('ism-i masdar', lambda g: g.startswith('ism-i masdar')),
         ('ism-i cins', lambda g: g.startswith('ism-i cins')), ('cem‘-i mükesser', lambda g: g.startswith('cem‘-i mükesser')), ('cem‘u’l-cem‘', lambda g: g.startswith('cem‘u’l-cem‘'))]
CESIT_AD = [c[0] for c in CESIT] + ['Kur’ân’da görülen öteki isimler']
@functools.lru_cache(maxsize=None)
def kok_json(k):
    f = LS.KR / 'kokler' / (k + '.json')
    return json.load(open(f, encoding='utf-8')) if f.exists() else None

def mustak_satirlari(k):
    """Sabit sıralı çeşit listesi: her çeşit için [(biçim, ‘●’ Kur’ân’da | ‘○’ kıyâsî, Türkçe, ilk yer)]; olmayan çeşit boş liste."""
    d = kok_json(k); G = d['mustaklar'] if d else {}
    G = sorted(G.items(), key=lambda kv: ('bâb' in kv[0] or 'Rubâ' in kv[0], list(G).index(kv[0])))      # sülâsî önce
    kur = KOK_ISIM.get(k, {}); sat = [[] for _ in CESIT_AD]
    motor = collections.defaultdict(list)                       # iskelet -> [(çeşit indeksi, biçim, Türkçe)]
    for g, L in G:
        for ci, (ad, f) in enumerate(CESIT):
            if f(g):
                for row in L: motor[MF.iskelet(row[1])].append((ci, row[1], row[3]))
    ek = []
    for (lem, c), (n, ilk) in kur.items():
        yer = '%s · %d geçiş' % (ilk, n); kayit = None
        if c: ci = {'fâil': 3, 'mef‘ûl': 4, 'masdar': 0}[c]; sat[ci].append((lem, '●', next((t for cj, b, t in motor.get(MF.iskelet(lem), []) if cj == ci), ''), yer)); continue
        eş = motor.get(MF.iskelet(lem), [])
        if eş:
            for cj in sorted({e[0] for e in eş}): sat[cj].append((lem, '●', next(t for ck, b, t in eş if ck == cj), yer))
        else: ek.append((lem, '●', '', yer))
    sat[-1] = ek
    for ci in range(len(CESIT)):
        gor = {MF.iskelet(x[0]) for x in sat[ci]}
        for cj, b, t in [e for v in motor.values() for e in v if e[0] == ci]:
            if len(sat[ci]) >= 2: break
            if MF.iskelet(b) in gor: continue
            gor.add(MF.iskelet(b)); sat[ci].append((b, '○', t, ''))
        sat[ci] = sat[ci][:2]
    return sat

def mustak_karti(k):
    sat = mustak_satirlari(k); o = []
    for i, (ad, L) in enumerate(zip(CESIT_AD, sat)):
        hucre = ' '.join('<span class="mb"><span class="ar">%s</span> <b>%s</b>%s%s</span>' % (E(b), m, (' ' + E(kisa(t, 15))) if t else '', (' <small>%s</small>' % E(y.split(' · ')[0])) if y else '') for b, m, t, y in L) if L else '<span class="cr">✗</span>'
        o.append('<tr class="%s"><td class="mn">%d</td><td class="ma">%s</td><td>%s</td></tr>' % ('yok' if not L else '', i + 1, E(ad), hucre))
    return '<div class="h2">Müştaklar <small>(her kökte aynı sıra · ● Kur’ân’da görülen biçim · ○ kıyâsî biçim · ✗ bu çeşit yok)</small></div><table class="mt">%s</table>' % ''.join(o)

def koksuz_govde(k):
    tur, kisa_, kul = EM.LEX[k]; v = LUGAT_KOMBO.get((k, 1), {})
    top = sum(x[0] for x in v.values()); ay = SAY.get((k, 1), [0, 0])
    o = ['<div class="kok">%s</div><div class="alt">%s · Kur’ân’da %d âyette, %d geçiş · ilk yer %s</div>' % (E(k), E(tur), ay[0], ay[1], ILKT[(k, 1)]),
         '<div class="h2">Manası <small>(bu başlığa mahsus; her lügat başlığı kendi manasıyla yazılır)</small></div>']
    o += ['<div class="mana"><b>%d. %s</b></div>' % (i + 1, E(m)) for i, m in enumerate(kul)]
    if v:
        o.append('<div class="h2">Kur’ân’da görülen biçimleri <small>(%d biçim · önek + gövde + sonek ayrı ayrı yazılır)</small></div><div class="bg">' % len(v))
        for kim, (n, ilk) in sorted(v.items(), key=lambda kv: (-kv[1][0], kv[1][1])):
            tam = ''.join(b for t_, ad, b, a in kim); pr = []
            for t_, ad, b, a in kim:
                if t_ == 'PREFIX': m = EM.ONEK[ad][1]
                elif t_ == 'SUFFIX': m = EM.SONEK[ad]
                elif a and a[1] == 1: m = EM.LEX[a[0]][1]
                elif a: m = anlam(a[0], 0, 22)
                else: m = ''
                pr.append('<span class="pp"><span class="ar">%s</span> %s</span>' % (E(b), E(m)))
            o.append('<div class="bc"><div class="bt"><span class="ar">%s</span><small>%d× · %s · s. %s</small></div><div class="bp">%s</div></div>' % (E(tam), n, ilk, ref('A' + ilk.replace(':', '_')), ' + '.join(pr)))
        o.append('</div>')
    return ''.join(o)

@functools.lru_cache(maxsize=None)
def kok_govde(k, fl):
    if fl: return koksuz_govde(k)
    body = LS.kok_sayfa(k)
    body = re.sub(r'<h2>(.*?)</h2>', r'<div class="h2">\1</div>', body, flags=re.S)
    i = body.find('<div class="h2">')
    kart = mustak_karti(k)
    return body[:i] + kart + body[i:] if i >= 0 else body + kart

SIKLIK = {(k, 0): i + 1 for i, (a, g, k) in enumerate(sorted([(v[0], v[1], k) for (k, fl), v in SAY.items() if fl == 0], key=lambda x: (-x[0], -x[1], x[2])))}
def sayfa_kok(k, fl, ilk_key):
    no = kok_no(k, fl); f = KF.get(k if fl == 0 else k + '·', [0, 0])
    sira = SIKLIK.get((k, fl)); et = ' · <b>yalnız bir âyette geçer</b>' if f[0] == 1 else (' · sıklıkta %d. kök (ilk yüz)' % sira if sira and sira <= 100 else '')
    ust = '<div class="kb"><span class="bs2">VI Kök</span> %s › ilk geçiş <b>%s</b> · Kur\'ân\'da %d âyette, %d geçiş%s · K%d</div>' % (E(SADI[int(ilk_key.split(':')[0])]), ilk_key, f[0], f[1], et, no)
    return '<section class="ks" %s>%s<div class="kg">%s</div></section>' % (anc('K%d' % no), ust, kok_govde(k, fl))

# ---------------------------------------------------------------- sûre ve kısım sayfaları
def sure_parcalari(s, wmm=122, hmm=118, mm_birim=0.5):
    r = SU[s]; rects = [a for a in _AYS[s]]
    mw, mh = wmm / mm_birim, 1e9
    if r[2] <= mw and r[3] <= mh: return [(r[0] - 1.2, r[1] - 1.2, r[2] + 2.4, r[3] + 2.4)]
    def kes(lo, hi, maks, yon):
        if hi - lo <= maks: return [lo, hi]
        sn = [lo]; c = lo
        while hi - c > maks:
            ideal = c + maks; best = None
            for dx in [i * 0.5 for i in range(0, 200)]:
                x = ideal - dx
                if x <= c + maks * 0.5: break
                n = sum(1 for a in rects if a[yon] < x < a[yon] + a[yon + 2])
                if best is None or n < best[0]: best = (n, x)
                if n == 0: break
            sn.append(best[1]); c = best[1]
        sn.append(hi); return sn
    xs = kes(r[0] - 1.2, r[0] + r[2] + 1.2, mw, 0); ys = kes(r[1] - 1.2, r[1] + r[3] + 1.2, mh, 1)
    return [(xs[i], ys[j], xs[i + 1] - xs[i], ys[j + 1] - ys[j]) for j in range(len(ys) - 1) for i in range(len(xs) - 2, -1, -1)]

def sure_ek(s, ay, yn, nk):
    yeni_k = [x for key in ORD if int(key.split(':')[0]) == s for x in YENI[key]]
    en = [x for x, c in SUREKOK[s].most_common(40) if True][:6]
    kart = ''.join('<span class="kc"><span class="ar">%s</span> %s</span>' % (x[0], E(anlam(x[0], x[1], 30))) for x in yeni_k[:8])
    cok = ''.join('<span class="kc"><span class="ar">%s</span> %s <small>(%d âyet)</small></span>' % (x[0], E(anlam(x[0], x[1], 26)), SUREKOK[s][x]) for x in en)
    ayni = [t for t in sorted(SU) if SU[t][8] == SU[s][8] and t != s][:10]
    onc = 'sûre %d s. %s' % (s - 1, ref('S%d' % (s - 1))) if s > 1 else '—'; son = 'sûre %d s. %s' % (s + 1, ref('S%d' % (s + 1))) if s < 114 else '—'
    return '<div class="sk"><div class="gr">Bu sûrenin âyetlerinin <b>%%%d</b>’i yeni kök getirir (%d / %d).</div>%s%s<div class="gr">Aynı mevzu kümesindeki öbür sûreler: %s</div><div class="gr">önceki: %s · sonraki: %s &nbsp; ☐ okudum ☐ tekrar ettim ☐ ezberledim</div><div class="nt"></div><div class="nt"></div></div>' % (round(100 * yn / max(len(ay), 1)), yn, len(ay), ('<div class="gr"><b>İlk görülen kökler</b> (ilk sekizi):</div>' + kart) if kart else '', ('<div class="gr"><b>Bu sûrede en çok geçen kökler:</b></div>' + cok) if cok else '', ' · '.join('%d' % t for t in ayni) or '—', onc, son)

def sayfa_sure_kapisi(s):
    r = SU[s]; L = KI[s]; ay = _AYS[s]; yn = sum(1 for a in ay if a[7] > 0); nk = sum(a[7] for a in ay)
    P = sure_parcalari(s)
    satir = ''.join('<tr><td>%d</td><td>%s</td><td>%d</td><td>%d</td><td class="m">s. %s</td></tr>' % (i + 1, E(k[4]), len(KIS_AYET[id(k)]), sum(AY[x][7] for x in KIS_AYET[id(k)]), ref('KS%d_%d_1' % (s, i))) for i, k in enumerate(L))
    h = harita_sure(s, 122, None, None)
    ics = ['<div class="sb">%s</div><div class="ab">%s</div>' % (E(SADI[s].split(' (')[0]) + ' · %d' % s, SADI[s].split(' (')[1].rstrip(')')),
           '<div class="ic"><div class="ozt">mevzu kümesi: <b>%s</b><br>%d âyet · %d kısım<br>yeni kök getiren âyet: <b>%d</b> · getirmeyen: %d<br>bu sûrede ilk görülen kök: <b>%d</b><br>kök hazinesi: %d → %d / %d</div><div class="lk">%s</div></div>' % (E(KUME[s]), len(ay), len(L), yn, len(ay) - yn, nk, CUM[ORI['%d:1' % s]] - len(YENI['%d:1' % s]), CUM[ORI['%d:%d' % (s, len(ay))]], TOPK, konum_haritasi((r[0], r[1], r[2], r[3]), 32)),
           h.serit_html(),
           '<table class="kt"><tr><th>#</th><th>kısım</th><th>âyet</th><th>yeni kök</th><th>harita</th></tr>%s</table>' % satir,
           sure_ek(s, ay, yn, nk),
           '<div class="gr">Bu harita sûre odasının tamamıdır; ayrıntı için kısım haritalarına (basamak IV) geçilir.%s</div>' % (' Sûre odası geniş olduğundan aşağıda %d parça hâlinde de verilir.' % len(P) if len(P) > 1 else '')]
    o = [sf('S%d' % s, 3, yol_sure(s), ''.join(ics), 'sure')]
    if len(P) > 1:
        for j, pc in enumerate(P):
            hh = harita_sure(s, 122, 118, None); hh = _parca_sure(s, pc)
            o.append(sf('S%d_p%d' % (s, j + 1), 3, yol_sure(s) + ' › parça %d/%d' % (j + 1, len(P)), hh.serit_html() + '<div class="gr">Parça %d / %d (sağdan sola, yukarıdan aşağı).</div>' % (j + 1, len(P)), 'sureparca'))
    return ''.join(o)

def _parca_sure(s, pc):
    x, y, w, hh = pc; h = Harita(x, y, w, hh, 122, None, kcap=1.2).sutun_yerlestir(122, 1.6); r = SU[s]
    h.dik(r[0], r[1], r[2], r[3], r[6], '#4a3f28', 0.4, 1.0); h.sigdir(SADI[s].split(' (')[0] + ' (%d)' % s, r[0], r[1], r[2], r[5], bold=True, alt_mm=1.6, ust_mm=3.4)
    for k in KI[s]:
        if k[0] > x + w or k[0] + k[2] < x or k[1] > y + hh or k[1] + k[3] < y: continue
        h.dik(k[0], k[1], k[2], k[3], k[7], '#4a3f28', 0.25, 0.5); h.sigdir(k[4], k[0], k[1], k[2], k[5], bold=True, fill='#1f4f86', alt_mm=1.3, ust_mm=2.4)
    for a in _AYS[s]:
        if a[0] > x + w or a[0] + a[2] < x or a[1] > y + hh or a[1] + a[3] < y: continue
        ayet_kutusu(h, a)
        if h.px(min(a[2], a[3])) > 2.0: h.sigdir(a[4].split(':')[1], a[0], a[1], a[2], min(a[3], 4.0), bold=True, alt_mm=1.3, ust_mm=2.2)
        for p in GP.get(a[4], []): h.dik(p[0], p[1], p[2], p[3], RENK_FILL[p[7]], '#8a6d1d' if not p[7] else '#2f6fb3', 0.12, 0.2)
    return h

def sayfalar_kisim(s, i):
    k = KI[s][i]; P = kisim_parcalari(k); o = []
    keys = KIS_AYET[id(k)]; yk = [x for x in keys if YENI[x]]
    for j, pc in enumerate(P):
        h = harita_kisim(k, pc)
        ek = ''
        if j == 0:
            ek = '<div class="ic"><div class="ozt"><b>%s</b><br>âyet %s – %s · %d âyet<br>yeni kök getiren âyet: <b>%d</b> · yeni kök: <b>%d</b></div><div class="lk">%s</div></div>' % (E(k[4]), keys[0], keys[-1], len(keys), len(yk), sum(len(YENI[x]) for x in keys), konum_haritasi((SU[s][0], SU[s][1], SU[s][2], SU[s][3]), 28))
        ics = ek + h.serit_html() + '<div class="gr">%s Âyet sayfaları: %s</div>' % ('Parça %d / %d. ' % (j + 1, len(P)) if len(P) > 1 else '', ' · '.join('%s s. %s' % (x, ref('A' + x.replace(':', '_'))) for x in yk[:6]) + ('…' if len(yk) > 6 else '') if yk else 'bu kısımda yeni kök getiren âyet yoktur')
        o.append(sf('KS%d_%d_%d' % (s, i, j + 1), 4, yol_kisim(k) + (' › parça %d/%d' % (j + 1, len(P)) if len(P) > 1 else ''), ics, 'kisim'))
    return ''.join(o)

def ozet_kisim(k):
    keys = KIS_AYET[id(k)]; Y = [x for key in keys for x in YENI[key]]
    if not Y: return ''
    return '<div class="oz"><div class="yh">Bu kısmın hatırlama kartı · yeni kökler (%d)</div>%s</div>' % (len(Y), ''.join('<span class="kc"><span class="ar">%s</span> %s</span>' % (x[0], E(anlam(x[0], x[1], 38))) for x in Y))

def govde_sure(s, i0=0, i1=None):
    i1 = len(KI[s]) if i1 is None else i1
    o = [sayfa_sure_kapisi(s)] if i0 == 0 else []
    for i, k in enumerate(KI[s]):
        if not (i0 <= i < i1): continue
        o.append(sayfalar_kisim(s, i)); keys = KIS_AYET[id(k)]; bl = []
        def bosalt():
            if bl: o.append('<section class="tk">%s</section>' % blok_tekrar(list(bl))); bl.clear()
        for key in keys:
            if YENI[key]:
                bosalt(); o.append(sayfa_ayet(key))
                for x in YENI[key]: o.append(sayfa_kok(x[0], x[1], key))
            else: bl.append(key)
        bosalt(); o.append('<section class="tk oz-s">%s</section>' % ozet_kisim(k) if ozet_kisim(k) else '')
    yk = [x for key in ORD if int(key.split(':')[0]) == s for x in YENI[key]]
    if yk and i1 == len(KI[s]): o.append('<section class="tk"><div class="oz"><div class="yh">%s sûresinde ilk görülen bütün kökler (%d)</div>%s</div></section>' % (E(SLAT[s]), len(yk), ''.join('<span class="kc"><span class="ar">%s</span> %s</span>' % (x[0], E(anlam(x[0], x[1], 30))) for x in yk)))
    return ''.join(o)

# ---------------------------------------------------------------- ön söz, haritalar, içindekiler
TR_SIRA = 'aâbcçdefgğhıîijklmnoöprsştuûüvyz'
def tr_anahtar(t):
    t = t.lower().replace('i̇', 'i')
    return [TR_SIRA.index(c) if c in TR_SIRA else 99 for c in t if c.isalpha()]
AR_SIRA = 'ءابتثجحخدذرزسشصضطظعغفقكلمنهوىي'
def ar_anahtar(k): return [AR_SIRA.index(c) if c in AR_SIRA else 99 for c in k]
ROMEN = None

def sayfa_kapak(c_ad, alt):
    return '<section class="kapak"><div class="k1">KUR’ÂN KÖK ATLASI</div><div class="k2">yaklaştırma usulüyle bir okuma kitabı</div><div class="k3 ar">القرآن الكريم · جذور</div><div class="k4">%s</div><div class="k5">%s</div></section>' % (E(c_ad), E(alt))

def sayfa_kunye():
    return '<section class="sf kunye"><h1 class="sb">Künye</h1><p>Bu kitap, <b>Kur’ân kök uzayı</b> haritasından (kok_uzayi.html) çıkarılmıştır; haritadaki her oda ve her kök bu kitapta bir sayfa olarak durur.</p><table class="kt"><tr><td>sûre</td><td>%d</td></tr><tr><td>kısım</td><td>%d</td></tr><tr><td>âyet</td><td>6236 (yeni kök getiren %d · getirmeyen %d)</td></tr><tr><td>kök ve lügat başlığı</td><td>%d (kök %d · lügat başlığı %d)</td></tr><tr><td>kök sayfası (lügat)</td><td>%d</td></tr></table><p class="kn"><b>Kaynaklar.</b> Âyet metni: Kur’ân-ı Kerîm metni, kaynak/sure dosyaları (Arapça aynen, hiçbir harf eksiltilmedi). Meal: Hayrat Neşriyat (tipografik apostrof ’ ile). Kök ve kelime çözümlemesi: Quranic Arabic Corpus morfolojisi 0.4. Kök sayfaları: Kubbealtı Lügati, Kamus, Vankulu, Luggat, Mekâyîs ve Cebel mihveri (Türkçe tercümeleriyle), Arabic Ontology (ücretsiz sürüm, CC-BY-4.0, SinaLab), EtymArab, Vikisözlük (CC-BY-SA); atıf ayrıntıları kök sayfalarının içindedir.</p><p class="kn"><b>Dürüstlük notu.</b> Kelime–kök hizası âyetlerin %%%.1f’inde kurulabilmiştir; kalan âyetlerde kelime kelime işaretleme yapılmaz, kök listesi yine verilir. “Lügat başlığı” harf, zamir, edat ve özel adlar gibi kökü olmayan kelimelerdir.</p></section>' % (
        len(SU), len(R['KI']), sum(1 for k in ORD if YENI[k]), sum(1 for k in ORD if not YENI[k]), len(KOK_SIRASI), sum(1 for x in KOK_SIRASI if x[1] == 0), sum(1 for x in KOK_SIRASI if x[1] == 1), sum(SAYFA.get(str(n), 0) for n in range(len(KOK_SIRASI))), 100 * len(DS) / 6236)

def merdiven():
    """Altı basamağı gerçek örnekle (2:255) gösteren küçük haritalar."""
    s = 2; k = AYKIS['2:255']; a = AY['2:255']; r = SU[2]
    kutular = [None, (r[0], r[1], r[2], r[3] * 0 + r[3]), None, None, None, None]
    ks = [('I', 'Bütün harita', konum_haritasi((0, 0, R['W'], R['H']), 36)),
          ('II', 'Bölge', konum_haritasi((0, 0, R['W'] / 3, R['H'] / 2), 36)),
          ('III', 'Sûre', konum_haritasi((r[0], r[1], r[2], r[3]), 36)),
          ('IV', 'Kısım', konum_haritasi((k[0], k[1], k[2], k[3]), 36)),
          ('V', 'Âyet', konum_haritasi((a[0], a[1], a[2], a[3]), 36)),
          ('VI', 'Kök', konum_haritasi((a[0] + a[2] - 6, a[1] + a[3] - 8, 5, 7), 36))]
    return '<div class="mv">%s</div>' % ''.join('<div class="mc"><div class="mb">%s</div>%s<div class="mt">%s</div></div>' % (b, svg, t) for b, t, svg in ks)

def sayfa_kilavuz():
    return ''.join([
        '<section class="sf"><h1 class="sb">Bu kitap nasıl okunur</h1>',
        '<p class="ln">Elinizdeki kitap bir <b>harita</b>dır ve haritalar uzaktan okunur: önce bütün, sonra bir parça, sonra daha yakın bir parça; en sonunda tek bir âyete ve o âyetin getirdiği tek bir köke varılır. Kitabın sayfaları bu yaklaşmanın sırasını izler. Altı basamak vardır; her basamak bir öncekinin içindeki küçük bir kırmızı çerçevenin büyütülmüş hâlidir.</p>',
        merdiven(),
        '<p class="ln"><b>I · Bütün harita.</b> Kur’ân’ın bütün sûreleri tek sayfada, mevzu kümesinin rengiyle. <b>II · Bölge.</b> Aynı harita altı parça; sûre adları okunur. <b>III · Sûre.</b> Bir sûrenin odası: içindeki kısımlar ve âyet kutuları. <b>IV · Kısım.</b> Bir kısmın âyet odaları ve her odanın içindeki yeni kök hücreleri. <b>V · Âyet.</b> Âyetin Arapçası, meali, kelime–kök tablosu. <b>VI · Kök.</b> Âyetle gelen her yeni kökün lügat sayfaları.</p>',
        '<p class="ln">Her sayfanın başındaki altı kutuluk şerit hangi basamakta olduğunuzu, küçük harita ise bütün harita üzerinde nerede bulunduğunuzu gösterir.</p></section>',
        '<section class="sf"><h1 class="sb">İşaretler</h1>',
        '<table class="kt isr"><tr><td>✦</td><td><b>yeni kök getiren âyet</b>: haritada düz ve kalın çizgili kutu; sayfası kendine ayrılmıştır.</td></tr>',
        '<tr><td>∅</td><td><b>yeni kök getirmeyen âyet</b>: haritada kesik çizgili ve taramalı kutu; kısa girişlerle, ardışık olarak verilir.</td></tr>',
        '<tr><td>●</td><td><b>yeni kök</b>: bu âyette ilk defa görülen kök. Âyet metninde bu kökün kelimesi <span class="w1">kalın ve altı çizili</span> yazılır (renksiz baskıda da ayırt edilir).</td></tr>',
        '<tr><td>○</td><td><b>tekrar eden kök</b>: daha evvel görülmüş kök; yanında ilk görüldüğü âyet ve lügat sayfasının yeri yazılır.</td></tr>',
        '<tr><td>s. 3/0412</td><td><b>sayfa göstergesi</b>: <i>cilt/sayfa</i>. Örneğin 3/0412, 3. cildin 412. sayfasıdır. Cilt 0 haritalar ve kılavuzu, son cilt dizinleri taşır.</td></tr>',
        '<tr><td>kök hazinesi</td><td>Kur’ân baştan sona okunurken şimdiye kadar kaç kökün görüldüğü; her âyet sayfasının altında çubukla gösterilir.</td></tr>',
        '<tr><td>lügat başlığı</td><td>Kökü olmayan kelime (harf, zamir, edat, özel ad). Kök sayfası yerine kelime sayfası verilir.</td></tr></table>',
        '<h1 class="sb" style="margin-top:6mm">Sayfa düzeni</h1><p class="ln">Sûreye girerken önce <i>sûre kapısı</i>nı okuyun: kısımların listesi ve haritadaki yeri oradadır. Kısım haritasında âyet kutularının içindeki küçük kartlar o âyetle gelen yeni köklerdir. Âyet sayfasından sonra gelen sayfalar, o âyetin yeni köklerinin lügat sayfalarıdır; kitap, bir âyeti ve getirdiği kökleri her zaman yan yana tutar.</p></section>'])

def grafik_hazine():
    """Kök hazinesi eğrisi (âyet sırasıyla) ve sûre başına yeni kök çubukları."""
    W_, H_ = 122, 62; x0, y0 = 12, 4; gw, gh = W_ - 15, H_ - 12
    pts = ' '.join('%.2f,%.2f' % (x0 + gw * i / (len(CUM) - 1), y0 + gh * (1 - CUM[i] / TOPK)) for i in range(0, len(CUM), 6))
    e = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%dmm" height="%dmm"><rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#8a7f62" stroke-width=".3"/><polyline points="%s" fill="none" stroke="#8a5a00" stroke-width=".7"/>' % (W_, H_, W_, H_, x0, y0, gw, gh, pts)]
    for v in (0, 500, 1000, 1500, TOPK): e.append('<text x="%.1f" y="%.1f" font-size="3" text-anchor="end" font-family="FreeSerif">%d</text>' % (x0 - 1, y0 + gh * (1 - v / TOPK) + 1, v))
    cum = 0
    for s in range(1, 115):
        cum += len(_AYS[s]); x = x0 + gw * cum / 6236
        e.append('<line x1="%.2f" y1="%d" x2="%.2f" y2="%d" stroke="#bbb" stroke-width=".12"/>' % (x, y0 + gh, x, y0 + gh + 1.2))
    for s in (1, 2, 4, 9, 18, 36, 56, 78, 114):
        cs = sum(len(_AYS[t]) for t in range(1, s)); x = x0 + gw * cs / 6236
        e.append('<text x="%.2f" y="%d" font-size="2.6" text-anchor="middle" font-family="FreeSerif">%d</text>' % (x, y0 + gh + 4.2, s))
    e.append('<text x="%d" y="%d" font-size="2.8" text-anchor="middle" font-family="FreeSerif">âyet sırası (altta sûre numaraları) →</text></svg>' % (x0 + gw / 2, H_ - 1))
    return ''.join(e)

def grafik_cubuk():
    yeni = [sum(len(YENI[x]) for x in ORD if int(x.split(':')[0]) == s) for s in range(1, 115)]
    mx = max(yeni); W_, H_ = 122, 52; x0, y0 = 8, 4; gw, gh = W_ - 10, H_ - 12; bw = gw / 114
    e = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%dmm" height="%dmm">' % (W_, H_, W_, H_)]
    for i, v in enumerate(yeni): e.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" stroke="#4a3f28" stroke-width=".08"/>' % (x0 + i * bw, y0 + gh * (1 - v / mx), bw * 0.9, gh * v / mx, SU[i + 1][6]))
    for s in (1, 2, 3, 4, 5, 7, 9, 18, 36, 56, 114): e.append('<text x="%.2f" y="%d" font-size="2.3" text-anchor="middle" font-family="FreeSerif">%d</text>' % (x0 + (s - 0.5) * bw, y0 + gh + 3.5, s))
    e.append('<text x="%d" y="%d" font-size="2.8" font-family="FreeSerif">en çok: sûre %d, %d yeni kök</text></svg>' % (x0 + 25, y0 + 6, yeni.index(mx) + 1, mx))
    return ''.join(e)

def sayfa_butun():
    h = harita_butun(None, None, 122, adlar=False)
    leg = ''.join('<div><i style="background:%s"></i>%s · %d sûre</div>' % (k[1], E(k[0]), k[2]) for k in KU)
    return sf('HARITA', 1, 'Harita › bütün', '<h1 class="sb">Bütün harita</h1><p class="ln">Kur’ân’ın yüz on dört sûresi, tek bir levha üzerinde. Her kutu bir sûredir; kutunun alanı, o sûrenin taşıdığı âyet ve kök hücrelerinin toplam alanıyla orantılıdır. Renkler sûrenin mevzu kümesini gösterir. Okuma sağdan sola ve yukarıdan aşağıdır: Fâtiha sağ üstte, Nâs ise sol alttadır.</p>%s<div class="lg">%s</div><p class="gr">%d sûre · %d kısım · %d âyet · %d kök hücresi. Sonraki basamak: altı bölge haritası.</p>' % (h.serit_html(36), leg, len(SU), len(R['KI']), 6236, len(R['GP'])), 'butun') + sf('HAZINE', 1, 'Harita › kök hazinesi', '<h1 class="sb">Kök hazinesi</h1><p class="ln">Kur’ân baştan sona okunurken her âyette yeni kökler görülür. Aşağıdaki eğri, âyet sırasına göre görülmüş köklerin toplamını gösterir: eğri başta diktir, sonra yatıklaşır; yani ilk sûreler en çok yeni kök getirir ve sonraki âyetler ağırlıkla daha evvel görülmüş köklere dayanır.</p><div class="hm">%s</div><p class="ln">Sûre başına ilk görülen köklerin sayısı:</p><div class="hm">%s</div>' % (grafik_hazine(), grafik_cubuk()), 'butun')

def bolge_parcalari():
    rects = list(SU.values()); mw, mh = 122 / 0.22, 150 / 0.22
    def kes(lo, hi, maks, yon):
        if hi - lo <= maks: return [lo, hi]
        sn = [lo]; c = lo
        while hi - c > maks:
            ideal = c + maks; best = None
            for dx in [i * 0.5 for i in range(0, 300)]:
                x = ideal - dx
                if x <= c + maks * 0.5: break
                n = sum(1 for a in rects if a[yon] < x < a[yon] + a[yon + 2])
                if best is None or n < best[0]: best = (n, x)
                if n == 0: break
            sn.append(best[1]); c = best[1]
        sn.append(hi); return sn
    xs = kes(0, R['W'], mw, 0); ys = kes(0, R['H'], mh, 1)
    return [(xs[i], ys[j], xs[i + 1] - xs[i], ys[j + 1] - ys[j]) for j in range(len(ys) - 1) for i in range(len(xs) - 2, -1, -1)]

def sayfalar_bolge():
    P = bolge_parcalari(); o = []
    for j, pc in enumerate(P):
        x, y, w, hh = pc; h = Harita(x, y, w, hh, 122, None)
        for s, r in SU.items():
            if r[0] > x + w or r[0] + r[2] < x or r[1] > y + hh or r[1] + r[3] < y: continue
            h.dik(r[0], r[1], r[2], r[3], r[6], '#4a3f28', 0.4, 1.0)
            for k in KI[s]: h.dik(k[0], k[1], k[2], k[3], k[7], '#4a3f28', 0.15, 0.3)
            if not h.sigdir(SLAT[s] + ' · %d' % s, r[0], r[1], r[2], r[3], bold=True, alt_mm=1.7, ust_mm=3.4): h.sigdir('%d' % s, r[0], r[1], r[2], r[3], bold=True, alt_mm=1.7, ust_mm=3.4)
        ss = sorted(s for s, r in SU.items() if not (r[0] > x + w or r[0] + r[2] < x or r[1] > y + hh or r[1] + r[3] < y))
        o.append(sf('B%d' % (j + 1), 2, 'Harita › bölge %d/%d' % (j + 1, len(P)), '<h1 class="sb">Bölge %d / %d</h1><div class="ic"><div class="ozt">bu parçadaki sûreler: %d–%d (%d sûre)</div><div class="lk">%s</div></div>%s<div class="gr">Sûre kapıları: %s</div>' % (j + 1, len(P), ss[0], ss[-1], len(ss), konum_haritasi((x, y, w, hh), 30), h.serit_html(36), ' · '.join('%d s. %s' % (s, ref('S%d' % s)) for s in ss[:14]) + ('…' if len(ss) > 14 else '')), 'bolge'))
    return ''.join(o)

def sayfalar_kume():
    o = []
    for i, ku in enumerate(KU):
        ss = [s for s in sorted(SU) if SU[s][8] == i]
        h = harita_butun(None, i, 100)
        satir = ''.join('<tr><td>%d</td><td>%s</td><td>%d</td><td>%d</td><td class="m">s. %s</td></tr>' % (s, E(SLAT[s]), len(_AYS[s]), sum(a[7] for a in _AYS[s]), ref('S%d' % s)) for s in ss)
        o.append(sf('Kume%d' % i, 2, 'Harita › mevzu kümesi', '<h1 class="sb">%s</h1><p class="ln">%d sûre · renk: <i class="ren" style="background:%s"></i></p>%s<table class="kt"><tr><th>#</th><th>sûre</th><th>âyet</th><th>yeni kök</th><th>kapı</th></tr>%s</table>' % (E(ku[0]), len(ss), ku[1], h.serit_html(36), satir), 'kume'))
    return ''.join(o)

def sayfa_cilt_haritasi(plan):
    pal = ['#c9d6a3', '#e7c58f', '#a9c7de', '#d9b0d4', '#f0d58a', '#b5d8c8', '#e3a9a0', '#c6c1e3', '#d8cba5', '#9fd0d6', '#e5b98c', '#bcd48f']
    sur_c = {g[0]: n for n, ad, a, b, c in plan for g in c if g[1] == 0}
    h = Harita(0, 0, R['W'], R['H'], 122)
    for s, r in SU.items():
        h.dik(r[0], r[1], r[2], r[3], pal[sur_c.get(s, 1) % len(pal)], '#4a3f28', 0.5, 1.0)
        h.sigdir('%d' % sur_c.get(s, 0), r[0], r[1], r[2], r[3], bold=True, alt_mm=2.0, ust_mm=6.0)
    return sf('CILTHARITA', 1, 'Giriş › ciltler haritada', '<h1 class="sb">Ciltler haritada</h1><p class="ln">Aşağıdaki levhada her sûre, kendi bulunduğu cildin numarasıyla işaretlidir; aynı renkteki sûreler aynı ciltte durur.</p>%s' % h.serit_html(36), 'cilt')

def sayfa_oneri():
    return '<section class="sf"><h1 class="sb">Çalışma önerisi</h1><ol class="ln"><li><b>Sûre kapısı:</b> sûrenin kısım listesine ve haritadaki yerine bakın.</li><li><b>Kısım haritası:</b> kısımdaki âyet kutularını ve içlerindeki yeni kök kartlarını gözden geçirin; kesik çizgili kutular yeni kök getirmeyen âyetlerdir.</li><li><b>Âyet sayfası:</b> Arapçayı okuyun, altın ve altı çizili kelimeleri kök tablosuyla eşleştirin, mealle karşılaştırın.</li><li><b>Kök sayfası:</b> kök anlamını ve mana ağacını okuyun; lügat metinleri ayrıntı içindir, ilk okumada bir göz atmak yeter.</li><li><b>Tekrar:</b> kısım sonundaki hatırlama kartını yüksek sesle okuyun; kartta anlamını hatırlamadığınız kök varsa dizinden sayfasını bulun.</li><li><b>İlerleme:</b> kök hazinesi çubuğu sizi her âyet sayfasında yüzdeyle bilgilendirir.</li></ol><p class="ln">Kitap, bir sûreyi baştan sona okumaya göre kurulmuştur; fakat dizinler sayesinde bir kökten âyete, bir âyetten köke her yönde gidilebilir.</p></section>'

def sayfalar_icindekiler(plan):
    c_satir = ''.join('<tr><td>%d</td><td>%s</td><td class="m">%s – %s</td><td class="m">%s</td></tr>' % (n, E(ad), a, b, '%d sayfa' % SAYI.get(n, 0)) for n, ad, a, b in plan)
    s_satir = ''.join('<tr><td>%d</td><td>%s</td><td class="m">s. %s</td></tr>' % (s, E(SADI[s]), ref('S%d' % s)) for s in range(1, 115))
    return sf('ICIN', 1, 'Giriş › içindekiler', '<h1 class="sb">Ciltler</h1><table class="kt"><tr><th>cilt</th><th>kapsam</th><th>sûreler</th><th>boy</th></tr><tr><td>0</td><td>Kılavuz ve haritalar</td><td class="m">—</td><td class="m">%s</td></tr>%s</table><h1 class="sb" style="margin-top:5mm">Sûre içindekileri</h1><div class="iki"><table class="kt">%s</table></div>' % ('%d sayfa' % SAYI.get(0, 0), c_satir, s_satir), 'icin')
SAYI = {}

# ---------------------------------------------------------------- dizinler
def sayfalar_dizin():
    o = []
    kk = sorted([x for x in KOK_SIRASI if x[1] == 0], key=lambda x: ar_anahtar(x[0]))
    satir = ''.join('<div class="dz"><span class="ar">%s</span><span class="da">%s</span><small>%s · s. %s</small></div>' % (k, E(anlam(k, 0, 30)), ILKT[(k, 0)], ref('K%d' % NO[(k, 0)])) for k, fl in kk)
    o.append(sf('D1', 1, 'Dizin › kökler (Arapça abece sırasıyla)', '<h1 class="sb">Kök dizini</h1><p class="ln">%d kök, Arapça abece sırasıyla (hemzeli kökler, yani ء ile başlayanlar, abecenin başındadır); yanında anlamı, ilk geçtiği âyet ve lügat sayfasının yeri.</p><div class="cok3">%s</div>' % (len(kk), satir), 'dizin'))
    lb = sorted([x for x in KOK_SIRASI if x[1] == 1], key=lambda x: ar_anahtar(x[0]))
    satir = ''.join('<div class="dz"><span class="ar">%s</span><small>%s · s. %s</small></div>' % (k, ILKT[(k, 1)], ref('K%d' % NO[(k, 1)])) for k, fl in lb)
    o.append(sf('D2', 1, 'Dizin › lügat başlıkları', '<h1 class="sb">Lügat başlıkları dizini</h1><p class="ln">%d başlık (kökü olmayan kelimeler: harf, zamir, edat, özel ad).</p><div class="cok4">%s</div>' % (len(lb), satir), 'dizin'))
    G = set()
    for k, fl in kk:
        t = KA.get(k, '')
        if ':' in t: t = t.split(':', 1)[1]
        for g in re.split(r'[;,]', re.sub(r'\([^)]*\)', '', t)):
            g = g.strip(' .’\'')
            if 1 < len(g) < 34: G.add((g, k))
    tl = sorted(G, key=lambda x: (tr_anahtar(x[0]), x[1]))
    satir = ''.join('<div class="dz"><span class="da">%s</span><span class="ar">%s</span><small>s. %s</small></div>' % (E(g), k, ref('K%d' % NO[(k, 0)])) for g, k in tl)
    o.append(sf('D3', 1, 'Dizin › Türkçe anlamlar', '<h1 class="sb">Türkçe anlam dizini</h1><p class="ln">Kök sözlüğündeki Türkçe karşılıklar abece sırasıyla; her karşılığın yanında kökü ve sayfası.</p><div class="cok3">%s</div>' % satir, 'dizin'))
    ay = []
    for s in range(1, 115):
        ks = [x for x in ORD if int(x.split(':')[0]) == s and YENI[x]]
        if ks: ay.append('<div class="ad"><b>%d · %s</b> ' % (s, E(SLAT[s])) + ' '.join('<span>%s <small>%s</small></span>' % (x.split(':')[1], ref('A' + x.replace(':', '_'))) for x in ks) + '</div>')
    o.append(sf('D4', 1, 'Dizin › yeni kök getiren âyetler', '<h1 class="sb">Âyet dizini</h1><p class="ln">Yeni kök getiren %d âyet; sûre sûre, âyet numarası ve sayfası.</p>%s' % (sum(1 for x in ORD if YENI[x]), ''.join(ay)), 'dizin'))
    sk = sorted([(v[0], v[1], k) for (k, fl), v in SAY.items() if fl == 0], key=lambda x: (-x[0], -x[1], x[2]))[:120]
    satir = ''.join('<tr><td>%d</td><td class="ar k">%s</td><td>%s</td><td>%d</td><td>%d</td><td class="m">s. %s</td></tr>' % (i + 1, k, E(anlam(k, 0, 44)), a, g, ref('K%d' % NO[(k, 0)])) for i, (a, g, k) in enumerate(sk))
    hap = sorted([k for (k, fl), v in SAY.items() if fl == 0 and v[0] == 1], key=ar_anahtar)
    o.append(sf('D5', 1, 'Dizin › sıklık', '<h1 class="sb">En çok geçen kökler</h1><table class="kt"><tr><th>#</th><th>kök</th><th>anlamı</th><th>âyet</th><th>geçiş</th><th>sayfa</th></tr>%s</table>' % satir, 'dizin') + sf('D6', 1, 'Dizin › yalnız bir âyette geçen kökler', '<h1 class="sb">Yalnız bir âyette geçen kökler</h1><p class="ln">%d kök Kur’ân’da yalnız bir âyette görülür; hepsi, geçtiği âyetle birlikte.</p><div class="cok4">%s</div>' % (len(hap), ''.join('<div class="dz"><span class="ar">%s</span><small>%s · s. %s</small></div>' % (k, ILKT[(k, 0)], ref('K%d' % NO[(k, 0)])) for k in hap)), 'dizin'))
    sr = ''.join('<div class="dz"><b>%d</b><span class="ar">%s</span><span class="da">%s</span><small>%s · s. %s</small></div>' % (i + 1, k, E(anlam(k, fl, 26)), ILKT[(k, fl)], ref('K%d' % NO[(k, fl)])) for i, (k, fl) in enumerate(SIRA_KOK))
    o.append(sf('D7', 1, 'Dizin › okuma sırasıyla kök listesi', '<h1 class="sb">Okuma sırasıyla kök listesi</h1><p class="ln">Kur’ân baştan sona okunurken köklerin ilk görüldüğü sırayla %d madde; bu liste, kök hazinesini sırayla edinmek isteyen için bir çalışma defteridir.</p><div class="cok3">%s</div>' % (len(SIRA_KOK), sr), 'dizin'))
    kd = ''.join('<tr><td>%d</td><td>%s</td><td class="m">%s – %s</td><td class="m">s. %s</td></tr>' % (s, E(k[4]), KIS_AYET[id(k)][0], KIS_AYET[id(k)][-1], ref('KS%d_%d_1' % (s, i))) for s in range(1, 115) for i, k in enumerate(KI[s]))
    o.append(sf('D8', 1, 'Dizin › kısımlar', '<h1 class="sb">Kısım dizini</h1><p class="ln">%d kısım; sûre numarası, kısım başlığı, âyet aralığı ve kısım haritasının sayfası.</p><table class="kt iki2">%s</table>' % (len(R['KI']), kd), 'dizin'))
    ab = sorted(range(1, 115), key=lambda t: tr_anahtar(SLAT[t]))
    o.append(sf('D9', 1, 'Dizin › sûre adları (abece sırasıyla)', '<h1 class="sb">Sûre adları dizini</h1><table class="kt">%s</table>' % ''.join('<tr><td>%s</td><td class="ar k">%s</td><td>%d</td><td class="m">s. %s</td></tr>' % (E(SLAT[t]), E(SADI[t].split(' (')[1].rstrip(')')), t, ref('S%d' % t)) for t in ab), 'dizin'))
    pl = []
    for gun in (30, 60, 100):
        sat = []
        for g in range(gun):
            a0 = round(g * 6236 / gun); a1 = round((g + 1) * 6236 / gun) - 1
            yk = CUM[a1] - (CUM[a0 - 1] if a0 else 0)
            sat.append('<tr><td>%d</td><td class="m">%s – %s</td><td>%d</td><td class="m">s. %s</td></tr>' % (g + 1, ORD[a0], ORD[a1], yk, ref('A' + ORD[a0].replace(':', '_'))))
        pl.append('<h2 class="sb2">%d günde okuma planı</h2><table class="kt"><tr><th>gün</th><th>âyetler</th><th>yeni kök</th><th>başlangıç sayfası</th></tr>%s</table>' % (gun, ''.join(sat)))
    o.append(sf('D10', 1, 'Dizin › okuma planları', '<h1 class="sb">Okuma planları</h1><p class="ln">Âyetler gün sayısına eşit bölünmüştür (her gün yaklaşık aynı sayıda âyet); yeni kök sayısı o günün kök yükünü gösterir. Yeni kök yükü, başlarda yüksek, sonlarda düşüktür.</p>' + ''.join(pl), 'dizin'))
    return ''.join(o)

# ---------------------------------------------------------------- biçim
def css(c_ad):
    return '''@font-face{font-family:Amiri;src:url("file://%(y)s/Amiri-Regular.ttf");font-weight:400}@font-face{font-family:Amiri;src:url("file://%(y)s/Amiri-Bold.ttf");font-weight:700}
@page{size:148mm 210mm;margin:12mm 13mm 15mm 13mm;background:#fffdf6;@bottom-center{content:counter(page);font:7.5pt FreeSerif,serif;color:#6b5a3a}@bottom-left{content:"%(c)s";font:7pt FreeSerif,serif;color:#8a7f62}}
html{background:#fffdf6}body{margin:0;font:9.4pt/1.42 FreeSerif,"DejaVu Serif",serif;color:#2b2410}
.ar{font-family:Amiri,serif;direction:rtl;unicode-bidi:isolate}
.sr{break-inside:avoid;line-height:0;border-left:.2mm solid #d9ceaa;border-right:.2mm solid #d9ceaa;background:#fff}.sr2{display:flex;flex-direction:row-reverse;justify-content:center;align-items:flex-start;gap:3mm;break-inside:avoid;line-height:0}.hm{margin:1.5mm 0;border:0}.sf{margin-top:3mm}.sf.ay{margin-top:5mm;border-top:.5mm solid #3b2605;padding-top:1.6mm}.ks{margin-top:4mm;border-top:.4mm solid #8a6d1d;padding-top:1.4mm}.tk{margin-top:3mm}.ay .ah,.ay .bs,.ay .yol{break-inside:avoid;break-after:avoid}.ay .arb,.ay .ml{orphans:2;widows:2}.kb,.kg .kok,.kg .alt{break-after:avoid}.kapak{break-before:right}
.bs{display:flex;gap:1mm;font:6.4pt FreeSerif,serif;margin:0 0 1.6mm}.bs span{padding:.25mm 1.5mm;border:.2mm solid #8a7f62;border-radius:1mm;color:#8a7f62}.bs span.a{background:#8a6d1d;color:#fff;border-color:#8a6d1d;font-weight:700}
.yol{font:7.4pt FreeSerif,serif;font-weight:400;color:#6b5a3a;margin:0 0 2.2mm}
.sb{font:700 15pt FreeSerif,serif;margin:0 0 1.5mm;color:#3b2605}.ab{font:700 22pt Amiri,serif;direction:rtl;text-align:right;color:#5a3d0c;margin:-8mm 0 0}
.hm{margin:1.5mm 0;border:.2mm solid #d9ceaa;background:#fff}.gr{font-size:7.8pt;color:#6b5a3a;margin:1.5mm 0}.ln{text-align:justify;hyphens:auto;margin:0 0 2.4mm}
.ic{display:flex;justify-content:space-between;gap:3mm;margin:0 0 1.5mm;align-items:flex-start}.ozt{font-size:8.6pt;line-height:1.45}.lk svg{border:.2mm solid #8a7f62}
table.kt{border-collapse:collapse;width:100%%;font-size:7.9pt;margin:1mm 0}.sg{display:inline-block;margin-right:3mm;white-space:nowrap}.sg .ar{font-size:11pt}.sg small{font-size:6.4pt}.oda{break-inside:avoid}.oda2{display:flex;gap:4mm;align-items:flex-start;break-inside:avoid}.oda2 .yan{flex:1}.kt th{background:#eee3bb;text-align:right;font-weight:700;padding:.6mm 1.2mm;border:.15mm solid #bfb48c;text-align:left}.kt td{padding:.3mm 1.1mm;border:.15mm solid #d9ceaa;vertical-align:top}.kt td.ar{font-size:13pt;line-height:1.5;text-align:right}.sb2{font:700 11pt FreeSerif,serif;margin:3mm 0 1mm}.kt td.m{font-size:7.6pt;color:#5a4f38;white-space:nowrap}
.isr td:first-child{font-size:12pt;text-align:center;white-space:nowrap;width:22mm}
.ah{display:flex;justify-content:space-between;align-items:flex-start;margin:0 0 2mm}.no{font:700 17pt FreeSerif,serif;color:#3b2605}.rz{font:700 8.6pt FreeSerif,serif;background:#c9a227;padding:.4mm 2mm;border-radius:1.5mm;border:.25mm solid #7a5a00}
.arb{font:20pt/1.95 Amiri,serif;direction:rtl;text-align:justify;margin:0 0 2mm;color:#2b2410}.arb.k2{font-size:15pt;line-height:1.9}
.w1{font-weight:700;color:#7a4a00;border-bottom:.35mm solid #8a5a00}.w3{color:#6b5a3a}
.ml{font-size:9pt;line-height:1.45;margin:0 0 2.5mm;color:#2b2410;border-left:.8mm solid #d9ceaa;padding-left:2.4mm}
.not,.ilr{font-size:8.2pt;margin:2mm 0}.bar{height:1.6mm;background:#e5dcbc;border-radius:1mm;margin:.8mm 0}.bar i{display:block;height:1.6mm;background:#8a6d1d;border-radius:1mm}
.yh{font:700 8.6pt FreeSerif,serif;background:#eee3bb;padding:.7mm 2mm;margin:0 0 1.6mm;border-left:1.2mm dashed #8a7f62}.yh span{font-weight:400;font-size:7.4pt;color:#5a4f38}
.ye{border-top:.2mm dashed #bfb48c;padding:1.2mm 0 1.4mm}.ye .yn{break-after:avoid}.ye .cl{break-inside:avoid}.ye .ml{break-inside:auto}.yh{break-after:avoid}.yn{font-size:8pt}.yn b{font-size:9.6pt}.cl{margin-top:.6mm}.ck{display:inline-block;margin:.3mm 1.2mm .3mm 0;padding:0 1.3mm;border:.2mm solid #bfb48c;border-radius:1.2mm;font-size:6.8pt;background:#faf6e6}.ck .ar{font-size:11pt}.ck small{font-size:6.3pt;color:#6b5a3a}
.oz{margin-top:3mm;border:.3mm solid #8a6d1d;padding:1.5mm;break-inside:avoid}.kc{display:inline-block;margin:.5mm 1.5mm .5mm 0;font-size:7.6pt}.kc .ar{font-size:12pt;font-weight:700}
.kb{font:7.4pt FreeSerif,serif;color:#6b5a3a;border-bottom:.2mm solid #d9ceaa;margin:0 0 1mm;padding:0 0 .6mm}.bs2{display:inline-block;background:#8a6d1d;color:#fff;font-weight:700;padding:.2mm 1.4mm;border-radius:1mm;margin-right:1.4mm}
.kg{font:9.6pt/1.42 FreeSerif,"DejaVu Serif",serif}.kg .kok{font-family:Amiri,serif;font-weight:700;font-size:40pt;line-height:1.5;text-align:center;direction:rtl;margin:1mm 0 0;color:#5a3d0c}.kg .alt{text-align:center;font-size:9pt;color:#6b5a3a;margin:0 0 3mm}
.kg .h2{font:700 10.5pt FreeSerif,serif;color:#fff;background:#8a6d1d;margin:4mm 0 1.6mm;padding:1mm 2.4mm;border-radius:1.2mm;break-after:avoid}.kg .h2 small{font-weight:400;font-size:8pt;opacity:.9}
.kg .mana{margin:0 0 1.4mm;break-inside:avoid}.kg .mana b{font-size:10.4pt}.kg .tur{margin:.3mm 0 0 5mm;font-size:9pt;color:#4a3f28}.kg .osm{font-size:9pt;line-height:1.38;margin:0 0 1.4mm;text-align:justify}.kg .osm b{color:#5a3d0c}.kg .en{font-size:8.2pt;line-height:1.38;color:#3a3220;text-align:justify;hyphens:auto}
.mt{border-collapse:collapse;width:100%%;font-size:8.2pt;margin:0 0 2mm}.mt td{border:.15mm solid #d9ceaa;padding:.1mm 1.2mm;vertical-align:middle;line-height:1.25}.mt .mn{width:5mm;text-align:right;color:#8a7f62;font-size:7pt}.mt .ma{width:30mm;font-size:7.6pt;font-weight:700;color:#3b2605}.mt tr.yok td{background:#f6efe0;color:#8a7f62}.mt .cr{color:#a0291a;font-weight:700;font-size:11pt}.mb{display:inline-block;margin-right:2.4mm;white-space:nowrap}.mb .ar{font-size:11pt;line-height:1.75}.mb b{color:#8a5a00;font-size:8pt}.mb small{font-size:6.3pt;color:#6b5a3a}\n.kg .bg{display:grid;grid-template-columns:1fr 1fr;gap:1mm 3mm}.kg .bc{border:.2mm solid #d9ceaa;padding:.6mm 1.4mm;break-inside:avoid;background:#fffaf0}.kg .bt{display:flex;justify-content:space-between;align-items:baseline}.kg .bt .ar{font-size:17pt;line-height:1.5}.kg .bt small{font-size:6.2pt;color:#6b5a3a}.kg .bp{font-size:7.4pt;line-height:1.7;color:#3a3220}.kg .pp .ar{font-size:11pt}\n.kg .kelime{display:flex;justify-content:space-between;gap:3mm;border-bottom:.2mm solid #d9ceaa;padding:1mm 0;break-inside:avoid}.kg .kelime .ar{font-size:15pt;flex:none}.kg .kelime div{flex:1}.kg .ar{font-family:Amiri,serif}
.kapak{text-align:center;padding-top:42mm}.k1{font:700 25pt FreeSerif,serif;letter-spacing:1mm;color:#3b2605}.k2{font-size:11pt;margin:4mm 0 14mm;color:#6b5a3a}.k3{font-size:38pt;color:#5a3d0c}.k4{font:700 15pt FreeSerif,serif;margin:20mm 0 3mm}.k5{font-size:9.5pt;color:#6b5a3a}
.mv{display:flex;flex-wrap:wrap;gap:3mm;margin:2mm 0}.mc{width:37mm;text-align:center}.mb{font:700 11pt FreeSerif,serif;color:#8a6d1d}.mt{font-size:8.4pt}
.lg{display:grid;grid-template-columns:1fr 1fr;gap:.6mm 4mm;font-size:7.8pt;margin:1.5mm 0}.lg i{display:inline-block;width:3mm;height:3mm;border:.2mm solid #4a3f28;margin-right:1.4mm;vertical-align:-.6mm}.ren{display:inline-block;width:5mm;height:3mm;border:.2mm solid #4a3f28;vertical-align:-.4mm}
.cok3{column-count:3;column-gap:3mm;font-size:7.6pt}.cok4{column-count:4;column-gap:2.4mm;font-size:7.4pt}.dz{break-inside:avoid;display:flex;gap:1.2mm;align-items:baseline;border-bottom:.1mm dotted #bfb48c;padding:.15mm 0}.dz .ar{font-size:12pt;flex:none}.dz .da{flex:1}.dz small{font-size:6.4pt;color:#6b5a3a;white-space:nowrap}
.ad{font-size:7.8pt;margin:0 0 1.4mm;text-align:justify}.ad span{display:inline-block;margin-right:1.5mm}.ad small{font-size:6.4pt;color:#6b5a3a}.iki .kt{font-size:7.6pt}
.kn{font-size:8.4pt;text-align:justify;margin:2mm 0}.kay{font-size:6.4pt;color:#8a7f62;margin-top:.6mm}.mil{font:700 9pt FreeSerif,serif;background:#fff3c4;border:.3mm solid #c9a227;padding:1mm 2mm;margin:2mm 0}.nt{border-bottom:.2mm solid #bfb48c;height:6mm}.sk{margin-top:1.5mm}.oda .hm{margin:.6mm 0}
''' % {'y': YAZI, 'c': c_ad}

def cilt_html(c_ad, govde):
    return '<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Kur’ân Kök Atlası · %s</title><style>%s</style></head><body>%s<div style="position:absolute;left:0;top:0;width:1px;height:1px;overflow:hidden;font-size:1px;line-height:1px;opacity:0;color:transparent">%s</div></body></html>' % (E(c_ad), css(c_ad), govde, ''.join('<a href="#%s">.</a>' % i for i in KAYIT))

# ---------------------------------------------------------------- cilt planı, üretim
def tahmin(s):
    ay = _AYS[s]; yk = [a for a in ay if a[7] > 0]
    n = 1 + (len(sure_parcalari(s)) if len(sure_parcalari(s)) > 1 else 0)
    n += sum(len(kisim_parcalari(k)) for k in KI[s]) + len(yk)
    n += sum(SAYFA.get(str(NO[(x[0], x[1])]), 1) for a in yk for x in YENI[a[4]])
    n += math.ceil((len(ay) - len(yk)) / 5.0) + len(KI[s]) // 3
    return n

OLCU_YOL = CIKTI / 'OLCU.json'
def K_KI(t): return KI[t]
def olcu_oku():
    return json.load(open(OLCU_YOL)) if OLCU_YOL.exists() else None

def birimler_olcu(olcu):
    """(sûre, kısım sırası) -> ölçülmüş sayfa sayısı; sûre kapısı ilk kısma eklenir."""
    return {(s, i): olcu['%d_%d' % (s, i)] for s in range(1, 115) for i in range(len(KI[s]))}

def planla(hedef=1400):
    olcu = olcu_oku(); cilt = []; cur = []; top = 0
    for s in range(1, 115):
        if olcu:
            for i in range(len(KI[s])):
                t = olcu['%d_%d' % (s, i)]
                if cur and top + t > hedef: cilt.append(cur); cur = []; top = 0
                cur.append((s, i)); top += t
        else:
            t = tahmin(s)
            if cur and top + t > hedef: cilt.append(cur); cur = []; top = 0
            cur += [(s, i) for i in range(len(KI[s]))]; top += t
    if cur: cilt.append(cur)
    plan = []
    for n, c in enumerate(cilt):
        gruplar = []
        for s, i in c:
            if gruplar and gruplar[-1][0] == s and gruplar[-1][2] == i: gruplar[-1][2] = i + 1
            else: gruplar.append([s, i, i + 1])
        ss = sorted({g[0] for g in gruplar})
        parca = []
        for g in gruplar:
            t = SLAT[g[0]]; tam = g[1] == 0 and g[2] == len(KI[g[0]])
            parca.append(t if tam else '%s (%d–%d. kısım)' % (t, g[1] + 1, g[2]))
        ad = ', '.join(parca) if len(parca) <= 3 else '%s … %s' % (parca[0], parca[-1])
        plan.append((n + 1, ad, ss[0], ss[-1], [tuple(g) for g in gruplar]))
    return plan

def sayfa_cilt_basligi(n, ad, grup):
    ss = [g[0] for g in grup] if grup else []
    return '<section class="sf" %s><div class="bs"></div><h1 class="sb">Cilt %d</h1><p class="ln"><b>%s</b>%s</p><table class="kt">%s</table></section>' % (anc('C%d' % n), n, E(ad), ' · %d sûre bölümü' % len(ss) if ss else '', ''.join('<tr><td>%d</td><td>%s</td><td class="m">kısım %d–%d · s. %s</td></tr>' % (g[0], E(SADI[g[0]]), g[1] + 1, g[2], ref('S%d' % g[0] if g[1] == 0 else 'KS%d_%d_1' % (g[0], g[1]))) for g in grup))

def govde_cilt0(plan):
    return sayfa_kapak('Cilt 0 · Kılavuz ve Haritalar', 'Basamak I ve II · içindekiler') + sayfa_kunye() + sayfa_kilavuz() + sayfa_oneri() + sayfa_butun() + sayfalar_bolge() + sayfalar_kume() + sayfa_cilt_haritasi([(n, ad, a, b, c) for n, ad, a, b, c in plan]) + sayfalar_icindekiler([(n, ad, a, b) for n, ad, a, b, c in plan])

def render_pdf(html_yol, pdf_yol):
    from playwright.sync_api import sync_playwright
    import glob
    C = sorted(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux*/chrome'))[-1]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=C); g = b.new_page(); g.set_default_timeout(0)
        g.goto(pathlib.Path(html_yol).as_uri(), wait_until='load'); g.evaluate('document.fonts.ready')
        g.pdf(path=str(pdf_yol), prefer_css_page_size=True, print_background=True, outline=True, tagged=True); b.close()

def cozum(pdf_yol, n):
    import pypdf
    r = pypdf.PdfReader(str(pdf_yol)); out = {}
    for ad, d in r.named_destinations.items():
        out[ad.lstrip('/')] = (n, r.get_destination_page_number(d) + 1)
    return out, len(r.pages)

def meta_yaz(P, ad):
    import pypdf
    w = pypdf.PdfWriter(clone_from=str(P)); w.add_metadata({'/Title': 'Kur’ân Kök Atlası · ' + ad, '/Author': 'Kur’ân Kök Atlası (kok_kitabi.py ile üretildi)', '/Subject': 'Yaklaştırma usulüyle Kur’ân kök haritası: harita, âyet ve kök sayfaları'}); w.write(str(P))

def uret(plan, secim=None, ikinci=True, son=False):
    CIKTI.mkdir(exist_ok=True); (CIKTI / 'gecici').mkdir(exist_ok=True)
    birimler = [(0, 'Cilt 0 · Kılavuz ve Haritalar', None)] + [(n, 'Cilt %d · %s' % (n, ad), c) for n, ad, a, b, c in plan] + [(len(plan) + 1, 'Cilt %d · Dizinler' % (len(plan) + 1), 'D')]
    if secim is not None: birimler = [b for b in birimler if b[0] in secim]
    gecis = [2, 3, 4, 5] if son else ([1, 2] if ikinci else [1])
    kaydi = False
    if (secim is not None or son) and REF == {} and (CIKTI / 'REF.json').exists(): _d = json.load(open(CIKTI / 'REF.json')); REF.update({k: tuple(v) for k, v in _d['REF'].items()}); SAYI.update({int(k): v for k, v in _d['SAYI'].items()})
    for g in gecis:
        for n, ad, c in birimler:
            KAYIT.clear(); t = time.time()
            if c is None: govde = govde_cilt0(plan)
            elif c == 'D': govde = sayfa_cilt_basligi(n, 'Dizinler', []).replace('<table class="kt"></table>', '') + sayfalar_dizin()
            else: govde = sayfa_cilt_basligi(n, ad.split(' · ', 1)[1], c) + ''.join(govde_sure(*g) for g in c)
            H = CIKTI / 'gecici' / ('cilt_%d.html' % n); P = (CIKTI / 'gecici' if g == 1 else CIKTI) / ('cilt_%d.pdf' % n)
            H.write_text(cilt_html(ad, govde), encoding='utf-8'); render_pdf(H, P)
            if g == 1:
                d, say = cozum(P, n); REF.update(d); SAYI[n] = say
                json.dump({'REF': REF, 'SAYI': SAYI}, open(CIKTI / 'REF.json', 'w'))
            elif son:
                d, say = cozum(P, n)
                if any(REF.get(i) != v for i, v in d.items()) or SAYI.get(n) != say: kaydi = True
                REF.update(d); SAYI[n] = say
                json.dump({'REF': REF, 'SAYI': SAYI}, open(CIKTI / 'REF.json', 'w'))
            print('geçiş', g, 'cilt', n, 'sayfa', SAYI.get(n), '%.0f sn' % (time.time() - t), flush=True)
        if son and g > 2 or son and g == 2:
            json.dump({'REF': REF, 'SAYI': SAYI}, open(CIKTI / 'REF.json', 'w'))
            print('geçiş', g, 'kayma var' if kaydi else 'kayma yok: kimlikler durağan', flush=True)
            if not kaydi: break
            kaydi = False
    if secim is None and (ikinci or son):
        durum = {'sure': len(SU), 'kisim': len(R['KI']), 'ayet': 6236, 'yeni_kok_getiren_ayet': len(YENI_AYET), 'kok_ve_lugat_basligi': len(KOK_SIRASI), 'ciltler': {str(n): {'sayfa': SAYI.get(n), 'bayt': (CIKTI / ('cilt_%d.pdf' % n)).stat().st_size} for n, ad, c in birimler}, 'toplam_sayfa': sum(SAYI.get(n, 0) for n, ad, c in birimler)}
        json.dump(durum, open(CIKTI / 'KITAP_DURUMU.json', 'w'), ensure_ascii=False, indent=1)
    return birimler

def olcu_yaz():
    """Bütün çapaların sayfa konumundan her kısım diliminin gerçek sayfa sayısı."""
    d = json.load(open(CIKTI / 'REF.json')); REF_ = {k: tuple(v) for k, v in d['REF'].items()}; SAYI_ = {int(k): v for k, v in d['SAYI'].items()}
    L = []
    for k, (c, p) in REF_.items():
        m = re.match(r'^(S(\d+)|KS(\d+)_(\d+)_1)$', k)
        if m: L.append((c, p, int(m.group(2) or m.group(3)), 0 if m.group(2) else int(m.group(4)), bool(m.group(2))))
    L.sort(); olcu = {}
    for j, (c, p, s, i, kapi) in enumerate(L):
        son = L[j + 1][1] if j + 1 < len(L) and L[j + 1][0] == c else SAYI_[c] + 1
        olcu['%d_%d' % (s, i)] = olcu.get('%d_%d' % (s, i), 0) + son - p
    json.dump(olcu, open(OLCU_YOL, 'w')); return olcu

if __name__ == '__main__':
    if '--olc' in sys.argv:
        pl = planla(); uret(pl, None, ikinci=False); o = olcu_yaz(); print('ölçüm yazıldı', sum(o.values()), 'sayfa'); sys.exit(0)
    plan = planla()
    print('plan:', [(n, ad) for n, ad, a, b, c in plan], flush=True)
    secim = None
    if '--dene' in sys.argv:
        ss = [int(x) for x in sys.argv[sys.argv.index('--dene') + 1].split(',')]
        plan = [(1, 'deneme', ss[0], ss[-1], [(t, 0, len(K_KI(t))) for t in ss])]; secim = {1}
    elif '--cilt' in sys.argv: secim = {int(x) for x in sys.argv[sys.argv.index('--cilt') + 1].split(',')}
    uret(plan, secim, ikinci='--tek' not in sys.argv, son='--son' in sys.argv)
