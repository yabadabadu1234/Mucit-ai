"""Kur'ân kök uzayının yerleşimi (F 3-I 401). Oda hiyerarşisi: sûre ⊃ kısım ⊃ âyet ⊃ kök hücresi.
Her âyet odasının başlığı TAM âyettir; başlık payı âyetin uzunluğuna göre oluşur. Odalar satırda ve sütunda hizalıdır
(hepsi hücre ızgarasına oturur), sıra sağdan sola, satır sonunda yine sağdan sola; kapalı dikdörtgen şartı yoktur, kenar girintili olabilir.
Birim: hücre eni = 1. Hücre boyu = A5 oranı."""
import math, json, pathlib, functools
from PIL import ImageFont
HERE = pathlib.Path(__file__).resolve().parent
KH = HERE.parent.parent
CH = 210 / 148; ORAN = 148 / 210
FA = 1.0             # âyet yazısı punto (birim: yazı puntosu)
SATIR = 1.85         # âyet satır aralığı (punto katı)
ADIM = 1.0           # ızgara adımı: bütün oda ebatları buna oturur
AG = 0.15            # oda içi boşluk
KB = 2.0; SB = 3.2   # kısım ve sûre başlık payı
CELL = 3.0           # hücre eni (yazı puntosu cinsinden)
_F = ImageFont.truetype(str(HERE / 'yazi' / 'Amiri-Regular.ttf'), 100)
def gen(t): return _F.getlength(t) / 100.0
def snap(v, s=ADIM): return math.ceil(v / s - 1e-9) * s

_AYET = {}
def ayet_metin(s, a):
    if s not in _AYET: _AYET[s] = json.load(open(KH / 'kaynak' / 'sure' / ('%d.json' % s), encoding='utf-8'))['verses']
    t = _AYET[s][a - 1]['arabic'].strip()
    return t + ' \ufd3f' + ''.join(chr(0x660 + int(c)) for c in str(a)) + '\ufd3e'

@functools.lru_cache(maxsize=None)
def sar(metin, genislik):
    W = genislik - 2 * AG; o = []; b = ''
    for w in metin.split():
        d = (b + ' ' + w) if b else w
        if b and gen(d) * FA * 1.06 > W: o.append(b); b = w
        else: b = d
    if b: o.append(b)
    return tuple(o)

def ayet_sekilleri(s, a, n, c):
    """Âyet odasının olası şekilleri (Pareto): (en, boy, özellik)."""
    t = ayet_metin(s, a); ch = c * CH; S = {}
    for kk in range(1, min(n, 14) + 1):
        for Wt in sorted({float(snap(kk * c + 2 * AG)), *[float(x) for x in range(4, 61, 3)]}):
            w = max(snap(kk * c + 2 * AG), Wt); L = sar(t, w)
            bh = len(L) * FA * SATIR + 0.3; r = math.ceil(n / kk); h = snap(bh + r * ch + 2 * AG)
            if h not in S or w < S[h][0]: S[h] = (w, h, dict(k=kk, L=L, bh=bh, c=c, s=s, a=a, n=n))
    out = []; eh = 1e18
    for w, h, sp in sorted(S.values(), key=lambda z: z[0]):
        if h < eh - 1e-9: out.append((w, h, sp)); eh = h
    return out

def shelf(olc, Wmax, bas):
    x = 0.0; y = bas + AG; sh = 0.0; used = 0.0; pos = []
    for w, h in olc:
        if x > 0 and x + w > Wmax - 2 * AG + 1e-9: y += sh; sh = 0.0; x = 0.0
        pos.append((x, y)); x += w; used = max(used, x); sh = max(sh, h)
    y += sh
    return pos, used + 2 * AG, snap(y + AG)

def paketle(cs, bas, tut=70):
    """Çocukların şekil listelerinden ebeveynin şekil listesi: hedef satır boyu Hr ve en W taranır; satır içi üst hizalı, sağdan sola."""
    ah = sorted({round(h, 3) for L in cs for (w, h, _) in L}); Hs = ah[::max(1, len(ah) // 30)] + [ah[-1]]; best = {}
    for Hr in Hs:
        pick = []
        for L in cs:
            ok = [(i, z) for i, z in enumerate(L) if z[1] <= Hr + 1e-9]
            pick.append(min(ok, key=lambda q: q[1][0]) if ok else min(enumerate(L), key=lambda q: q[1][1]))
        ws = [z[0] for i, z in pick]; mx = max(ws); top = sum(ws); n_ = min(40, int(top - mx) + 1)
        Wc = sorted({int(math.ceil(mx + 2 * AG)) + int(round(k)) for k in [j * (top - mx) / max(n_ - 1, 1) for j in range(n_)]})
        for W in Wc:
            pos, w, h = shelf([(z[0], z[1]) for i, z in pick], W, bas)
            if h not in best or w < best[h][0]: best[h] = (w, [(ci, i, x, y) for ci, ((i, z), (x, y)) in enumerate(zip(pick, pos))])
    out = []; eh = 1e18
    for h, (w, lay) in sorted(best.items(), key=lambda kv: kv[1][0]):
        if h < eh - 1e-9: out.append((w, h, lay)); eh = h
    if len(out) > tut:
        ix = sorted({int(round(j * (len(out) - 1) / (tut - 1))) for j in range(tut)}); out = [out[i] for i in ix]
    return out

def kur(SUR, KOKA, NO, SAYFA, KAPAK):
    surler = []
    for s, adi, na, KIS in SUR:
        kis = []
        for kad, ay in KIS:
            ao = []
            for a in ay:
                r = KOKA.get('%d:%d' % (s, a), [])
                if r: ao.append(dict(tip='a', kok=r, sek=ayet_sekilleri(s, a, len(r), CELL), kids=[]))
            if ao: kis.append(dict(tip='k', ad=kad, s=s, kids=ao, sek=paketle([x['sek'] for x in ao], KB)))
        if kis: surler.append(dict(tip='s', s=s, ad='%d · %s' % (s, adi), kids=kis, sek=paketle([k['sek'] for k in kis], SB)))
    kok_ = paketle([S['sek'] for S in surler], 0, 120)
    sk = lambda z: z[0] * z[1] * (1 + 0.5 * abs(math.log(z[0] / z[1] / 1.65)))
    w, h, lay = min(kok_, key=sk)
    SU, KI, AY, GP = [], [], [], []
    def yer(nodes, lay, X, Y, w):
        for ci, i, x, y in lay:
            nd = nodes[ci]; cw, ch, sub = nd['sek'][i]
            yield nd, sub, cw, ch, X + w - (x + cw), Y + y
    for S, sub, sw, sh_, SX, SY in yer(surler, lay, 0.0, 0.0, w):
        SU.append([round(SX, 3), round(SY, 3), round(sw, 3), round(sh_, 3), S['ad'], round(SB, 3)])
        for K, ksub, kw, kh, KX, KY in yer(S['kids'], sub, SX, SY, sw):
            KI.append([round(KX, 3), round(KY, 3), round(kw, 3), round(kh, 3), K['ad'], round(KB, 3), S['s']])
            for A, sp, aw, ah, AX, AYY in yer(K['kids'], ksub, KX, KY, kw):
                AY.append([round(AX, 3), round(AYY, 3), round(aw, 3), round(ah, 3), '%d:%d' % (sp['s'], sp['a']), round(sp['bh'], 3), list(sp['L'])])
                kk = sp['k']; cc = sp['c']; r0 = AYY + sp['bh'] + AG
                for j, (kok, fl) in enumerate(A['kok']):
                    ri, ci = divmod(j, kk); no = NO[(kok, fl)]; nc = KAPAK.get(str(no), 0)
                    GP.append([round(AX + aw - AG - (ci + 1) * cc, 3), round(r0 + ri * cc * CH, 3), cc, round(cc * CH, 4), no, nc + SAYFA.get(str(no), 0), kok, fl, nc])
    return dict(SU=SU, KI=KI, AY=AY, GP=GP, W=round(w, 3), H=round(h, 3), FA=FA, SATIR=SATIR, CELL=CELL)
