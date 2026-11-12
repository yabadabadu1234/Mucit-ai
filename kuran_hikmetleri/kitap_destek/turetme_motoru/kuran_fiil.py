import collections
import json
import os
import re

import istikak as I

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'kaynak', 'sozluk')
GECMIS = re.compile(r'^(.*?)(d[ıiuü]|t[ıiuü])(m|n|k|nız|niz|nuz|nüz|lar|ler)?$')
GENIS = re.compile(r'^(.*?)([ae]r|[ıiuü]r)(im|ım|um|üm|iz|ız|uz|üz|sin|sın|sun|sün|ler|lar)?$')
EDILGEN = re.compile(r'^(.{2,}?)(il|ıl|ul|ül)$')
YOK_SOZ = {'değil', 'değildir', 'var', 'yok'}
_C = []


def hece(w):
    return sum(1 for c in w if c in 'aeıioöuü')


def adaylar(son):
    m = GECMIS.match(son)
    if m and m.group(1):
        return [m.group(1)], False
    m = GENIS.match(son)
    if m and m.group(1) is not None:
        g, ek = m.group(1), m.group(2)
        c = [g, g + ek[0]] if ek[0] in 'ae' else [g, g + ek[0]]
        if hece(g) >= 2 and ek[0] in 'ae':
            c = [g + ek[0], g]
        return [x for x in c if x], True
    return [], False


def sertle(x):
    d = {'d': 't', 'b': 'p', 'c': 'ç', 'ğ': 'k'}
    w = x.split()
    return ' '.join(w[:-1] + [w[-1][:-1] + d[w[-1][-1]]]) if w[-1][-1] in d else x


def kes(parca, V):
    ks = parca.strip().split()
    if not ks:
        return None
    son = ks[-1].lower()
    if son in YOK_SOZ:
        return None
    c, genis = adaylar(son)
    if not c:
        return None
    sec = None
    for x in c:
        for y in (x, sertle(x)):
            if y in V:
                sec = y
                break
        if sec:
            break
    if sec is None:
        sec = c[0]
    if sec.startswith('neredeyse') or len(sec) < 2 or (len(sec) >= 4 and EDILGEN.match(sec)):
        return None
    ks[-1] = sec
    return ' '.join(ks), genis


def yukle():
    K = json.load(open(os.path.join(KOK, 'kelimeler.json'), encoding='utf-8'))
    L = {x['lem']: x['tr'] for x in json.load(open(os.path.join(KOK, 'lemma_karsilik_uretim.json'), encoding='utf-8'))}
    ham = collections.defaultdict(lambda: collections.defaultdict(list))
    V = set()
    for p in L.values():
        for q in p.split(','):
            w = q.strip().split()
            if w:
                m = GECMIS.match(w[-1].lower())
                if m and len(m.group(1)) >= 2:
                    V.add(m.group(1))
    for x in json.load(open(os.path.join(KOK, '..', 'lugat', 'kok_anlamlari.json'), encoding='utf-8')):
        for it in re.split(r',|;| / ', x['turkce']):
            it = it.strip()
            if it.endswith(('mek', 'mak')) and ' ' not in it:
                V.add(it[:-3])
    for k in K:
        if k['tur'] != 'Fiil' or k['lem'] not in L:
            continue
        for p in L[k['lem']].split(','):
            r = kes(p, V)
            if r and r[0]:
                ham[I.normala(k['kok'])][r[0]].append((k['bab'], k['zaman']))
    out = {}
    for kok, d in ham.items():
        sirali = sorted(d.items(), key=lambda z: (-len(z[1]), z[0]))
        out[kok] = [(s, len(v)) for s, v in sirali]
    return out


def tablo():
    if not _C:
        _C.append(yukle())
    return _C[0]


def stem(kok, ipucu=''):
    t = tablo().get(I.normala(kok))
    if not t:
        return None
    kel = [w.strip(" '\"?.,;:()") for w in re.split(r'\s+', ipucu.lower()) if len(w) >= 3]

    def puan(z):
        s, n = z
        ilk = s.split()[-1] if ' ' not in s else s.split()[0]
        ort = any(w[:3] == ilk[:3] or w[:3] == s.split()[-1][:3] for w in kel)
        return (-int(ort), int(' ' in s), -n, s)
    return sorted(t, key=puan)[0][0]


if __name__ == '__main__':
    t = tablo()
    print(len(t))
    import turkce as T
    uy = ay = 0
    for k, x in T.db().items():
        b = T.kok_bilgisi(k)
        if b['kaynak'] == 'fiil' and k in t:
            ay += 1
            if b['stem'] in [s for s, _ in t[k]]:
                uy += 1
    print('DB fiil ile örtüşen', uy, '/', ay)
    for k in list(t)[:40]:
        print(k, t[k][:3])
