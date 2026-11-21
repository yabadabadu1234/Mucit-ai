"""Mushaf dizgisi (F 3-I 406-407): âyet metnini DEĞİŞTİRMEDEN, yalnız satır kırma, girinti, yaslama ve boşlukla mana bağlarını yerleşime kodlar.
Kural seti sabittir (7 kural); her âyette yeni icat yoktur; zar yoktur; aynı girdi aynı çıktıyı verir.
Kelime ve işaretler olduğu gibi, sırasıyla, bölünmeden yazılır; ölçüt yalnız kelimelerin kök iskeleti ve harekelerinden okunur."""
import pathlib, functools, unicodedata
from PIL import ImageFont
HERE = pathlib.Path(__file__).resolve().parent
FA = 1.0; AG = 0.15; INS = 1.4; GAP1 = 0.5; GAP2 = 1.6; HG = 0.75
KURALLAR = ('ARA', 'ISTISNA', 'CEVAP', 'ZITLIK', 'HITAP', 'NAKIL', 'PARALEL')
_F = ImageFont.truetype(str(HERE / 'yazi' / 'Amiri-Regular.ttf'), 100)
def gen(t): return _F.getlength(t) / 100.0

DURAK = ('ۖ', 'ۗ', 'ۘ', 'ۚ')   # sılâ, kıylâ, lâzım, câiz: durulması beklenen işaretler
MUANAKA = 'ۛ'
def isaret(t): return all('ۖ' <= c <= 'ۜ' for c in t)

_HARF = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ى': 'ي', 'ة': 'ه'}
def iskelet(w):
    s = ''.join(_HARF.get(c, c) for c in w if ('ء' <= c <= 'ي' and c != 'ـ') or c == 'ٱ')
    return s
def atif(w):   # başta "وَ" veya "فَ" (fetha) bağlacı mı
    return len(w) > 1 and w[0] in 'وف' and w[1] == 'َ'
def cekirdek(w):
    s = iskelet(w)
    return s[1:] if atif(w) and len(s) > 2 else s
def fa_cevap(w): return len(w) > 3 and w[0] == 'ف' and w[1] == '\u064e' and w[3] != '\u0652'

SART = ('اذا', 'لو', 'لولا', 'كلما', 'لين')
NAKIL_FIIL = ('قل', 'قال', 'قالوا', 'قالت', 'قلنا', 'قلت', 'قالا', 'يقول', 'يقولون', 'تقول', 'تقولون', 'تقولوا', 'تقولن', 'نقول', 'اقول', 'قيل')
NIDA = ('يايها', 'ياايها', 'يايتها', 'يابني', 'ياقوم', 'ياعبادي', 'ياابت', 'يااهل', 'يابت', 'يابنيء')
ZIT = ('بل', 'لكن')

def sart_mi(w):
    c = cekirdek(w)
    if c in SART: return True
    g = w[2:] if atif(w) else w
    return c == 'ان' and g[:1] == 'إ' and '\u0651' not in w

def kurallari_uygula(T, kurallar=KURALLAR):
    n = len(T); isr = [isaret(t) for t in T]
    sondaki = [0]; depth = [0] * n; side = ['R'] * n; brk = [False] * n; gap = [0] * n; hg = [0] * n
    def durak_son(i):
        for e in range(i, n):
            if isr[e] and T[e][0] in DURAK: return e
        return n - 1
    def sonraki(i):
        k = i + 1
        while k < n and isr[k]: k += 1
        return k
    def kir(i, g=0):
        while i < n and isr[i]: i += 1
        if i < n: brk[i] = True; gap[i] = max(gap[i], g) if i > 0 else 0
    if 'ARA' in kurallar:
        ms = [i for i in range(n) if isr[i] and T[i][0] == MUANAKA]
        for a, b in zip(ms[0::2], ms[1::2]):
            for k in range(a + 1, b + 1): depth[k] += 2
            kir(a + 1)
    if 'ISTISNA' in kurallar:
        for i in range(n):
            if not isr[i] and iskelet(T[i]) in ('الا', 'والا', 'فالا') and T[i].lstrip('وفَ')[:1] == 'إ':
                for k in range(i, durak_son(i) + 1): side[k] = 'L'; depth[k] += 1
                kir(i)
    if 'CEVAP' in kurallar:
        sartlar = [i for i in range(n) if not isr[i] and sart_mi(T[i])]
        for si, i in enumerate(sartlar):
            lim = sartlar[si + 1] if si + 1 < len(sartlar) else n
            j = next((k for k in range(i + 2, lim) if not isr[k] and fa_cevap(T[k])), None)
            if j is None: continue
            kir(i)
            for k in range(j, min(durak_son(j), lim - 1) + 1): side[k] = 'L'
            kir(j)
    if 'ZITLIK' in kurallar:
        for i in range(n):
            if not isr[i] and cekirdek(T[i]) in ZIT:
                kir(i, 1)
    if 'HITAP' in kurallar:
        for i in range(n):
            if isr[i] or iskelet(T[i]) not in NIDA: continue
            c = iskelet(T[i]); j = i
            if c in ('يايها', 'ياايها', 'يايتها'):
                j = sonraki(i)
                if j < n and cekirdek(T[j]) in ('الذين', 'اللذين'): j = sonraki(j)
            elif c == 'يااهل': j = sonraki(i)
            gap[i] = 2; brk[i] = True; k = sonraki(j)
            if k < n: kir(k, 2)
            else: sondaki[0] = 2
    if 'NAKIL' in kurallar:
        for i in range(n):
            if not isr[i] and cekirdek(T[i]) in NAKIL_FIIL:
                k = sonraki(i)
                if k >= n: continue
                for q in range(k, durak_son(k) + 1): depth[q] += 1
                kir(k)
    if 'PARALEL' in kurallar:
        for i in range(1, n):
            if not isr[i] and atif(T[i]) and T[i][0] == 'و':
                hg[i] = 1
    for i in range(1, n):
        if not isr[i] and (depth[i] != depth[i - 1] or side[i] != side[i - 1]): brk[i] = True
        if isr[i]:
            depth[i] = depth[i - 1]; side[i] = side[i - 1]
    return depth, side, brk, gap, hg, sondaki[0]

def kes(T, kurallar=KURALLAR):
    """Segmentler: [derinlik, yaslama, boşluk, [belirteç indisleri], {indis: yatay boşluk}]"""
    depth, side, brk, gap, hg, son = kurallari_uygula(T, kurallar)
    segs = []
    for i in range(len(T)):
        if not segs or (brk[i] and not isaret(T[i])):
            segs.append([depth[i], side[i], gap[i], [i], {}])
        else: segs[-1][3].append(i)
        if hg[i] and len(segs[-1][3]) > 1: segs[-1][4][i] = 1
        elif hg[i]: segs[-1][4][i] = 0   # satır başındaki yatay boşluk görünmez; yeni segment kendisi ayrımdır
    return segs, son

@functools.lru_cache(maxsize=None)
def yerles(arapca, sayi, W, kurallar=KURALLAR):
    """Döner: (satırlar, yükseklik). satır = (belirteçler, yatay_boşluk_bayrakları, girinti_em, yaslama, y_satır, indisler)."""
    T = tuple(arapca.split()); (segs, son) = kes(T, kurallar); satirlar = []; y = 0.0; ilk = True
    SON = ' \ufd3f' + ''.join(chr(0x660 + int(c)) for c in str(sayi)) + '\ufd3e'
    for si, (d, sd, g, idx, hgs) in enumerate(segs):
        inset = 0.0 if sd == 'C' else d * INS
        avail = W - 2 * AG - inset
        if g and (not ilk or g == 2): y += (GAP1 if g == 1 else GAP2)
        ilk = False
        tk = []; fl = []; ix = []; w = 0.0
        for q, k in enumerate(idx):
            p = T[k] + (SON if (si == len(segs) - 1 and q == len(idx) - 1) else '')
            h = 1 if hgs.get(k) else 0
            wp = gen(p) * FA * 1.06 + (gen(' ') * FA * 1.06 if tk else 0.0) + h * HG
            if tk and w + wp > avail:
                satirlar.append((tuple(tk), tuple(fl), inset, sd, y, tuple(ix))); y += 1.0; tk = []; fl = []; ix = []; w = 0.0; wp = gen(p) * FA * 1.06 + h * HG
            tk.append(p); fl.append(h); ix.append(k); w += wp
        satirlar.append((tuple(tk), tuple(fl), inset, sd, y, tuple(ix))); y += 1.0
    if son: y += GAP2
    return tuple(satirlar), y

def metin_butunlugu(arapca, sayi, W, kurallar=KURALLAR):
    """Sıfır metin müdahalesi: satırlardaki belirteçler sırayla birleşince asıl metin + âyet sonu işareti çıkmalı."""
    sat, _ = yerles(arapca, sayi, W, kurallar)
    SON = ' \ufd3f' + ''.join(chr(0x660 + int(c)) for c in str(sayi)) + '\ufd3e'
    return ' '.join(t for s_ in sat for t in s_[0]) == ' '.join(arapca.split()) + SON
