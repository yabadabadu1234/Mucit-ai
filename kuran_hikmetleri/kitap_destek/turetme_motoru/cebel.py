import json
import os
import re

import istikak as I

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
CIKTI = os.path.join(KOK, 'kaynak', 'lugat', 'cebel_mihveri.json')
HRK = re.compile('[ًٌٍَُِّْٰـ]')
CEV = {'ک': 'ك', 'ی': 'ي', 'ى': 'ي', 'ہ': 'ه', 'ۃ': 'ة', 'ە': 'ه', 'ھ': 'ه', 'ں': 'ن'}
BASLIK = re.compile(r'^\W{0,4}\(([^)]{2,40})\)\s*:?\s*$')
MIHVER = 'المعنى المحوري'


def temiz(s):
    s = HRK.sub('', s)
    return ''.join(CEV.get(c, c) for c in s)


def kokler(ic):
    out = []
    for p in re.split(r'[-–—\s]+', temiz(ic)):
        if re.fullmatch('[ء-ي]{3,4}', p):
            out.append(I.normala(p))
    return out


def cikar(yol):
    S = open(yol, encoding='utf-8').read().split('\n')
    sonuc = {}
    n = len(S)
    i = 0
    while i < n:
        m = BASLIK.match(S[i].strip())
        if not m:
            i += 1
            continue
        ks = kokler(m.group(1))
        j = i + 1
        govde = []
        while j < n and not BASLIK.match(S[j].strip()) and j - i < 80:
            govde.append(S[j].strip())
            j += 1
        metin = '\n'.join(govde)
        p = metin.find(MIHVER)
        if ks and p >= 0:
            kalan = metin[p:]
            son = kalan.find('\n\n')
            mih = re.sub(r'\s+', ' ', kalan[:son if son > 0 else 700][:900]).strip()
            for k in ks:
                sonuc.setdefault(k, []).append({'kokler': ks, 'mihveri': mih})
        i = j
    return sonuc


if __name__ == '__main__':
    import sys
    import turkce as T
    d = cikar(sys.argv[1])
    ours = set(T.db())
    print(len(d), 'bizde', len(set(d) & ours), 'yok', len(set(d) - ours))
    json.dump({'durum': 'OCR (archive.org djvu); doğrulanmadı; F 3-A 25-E', 'kaynak': 'Muhammed Hasan Hasan Cebel, el-Mu\'cemü\'l-İştikâkıyyü\'l-Mü\'asssal li-Elfâzi\'l-Kur\'âni\'l-Kerîm', 'kokler': d}, open(CIKTI, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    k = next(iter(d)); print(k, d[k][0])
