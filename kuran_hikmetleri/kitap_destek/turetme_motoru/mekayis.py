import os
import re

import istikak as I

YOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'kaynak', 'lugat', 'mekayis_samela.txt')
HRK = re.compile('[ًٌٍَُِْٰـ]')
BAS = re.compile(r'^\(([^)]{2,12})\)\s+(ال\S+(?:\s+ال\S+)?\s+و?ال\S+)')
SAYFA = re.compile(r'^\(\d+/\d+\)$')
_C = []


def kok_yaz(h):
    out = []
    for c in HRK.sub('', h.replace(' ', '')):
        if c == 'ّ':
            if out:
                out.append(out[-1])
        else:
            out.append(c)
    return ''.join(out)


def yukle():
    if _C:
        return _C[0]
    S = [x.strip() for x in open(YOL, encoding='utf-8').read().split('\n')]
    basliklar = []
    for i, l in enumerate(S):
        m = BAS.match(HRK.sub('', l)) if '(' in l[:2] else None
        if not m:
            continue
        ham = re.match(r'^\(([^)]{2,14})\)', l).group(1)
        r = kok_yaz(ham)
        if re.fullmatch('[ء-ي]{3,5}', r):
            basliklar.append((i, r, ham))
    d = {}
    for n, (i, r, ham) in enumerate(basliklar):
        son = basliklar[n + 1][0] if n + 1 < len(basliklar) else len(S)
        govde = [x for x in S[i:son] if x and not SAYFA.match(x) and not x.startswith(('باب ', 'كتاب '))]
        k = I.normala(r)
        d.setdefault(k, []).append({'baslik': ham, 'metin': '\n'.join(govde)})
    _C.append(d)
    return d


if __name__ == '__main__':
    d = yukle()
    import turkce as T
    ours = set(T.db())
    print(len(d), len(set(d) & ours), len(set(d) - ours), sum(len(v) for v in d.values()))
    k = next(iter(d)); print(k, d[k][0]['metin'][:300])
