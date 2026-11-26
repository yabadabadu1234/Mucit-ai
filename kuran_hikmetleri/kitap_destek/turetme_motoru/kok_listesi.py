import json
import os
import re
import sys

K = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
KD = os.path.join(K, 'kelime_kaydi')
SIRA = 'ءبتثجحخدذرزسشصضطظعغفقكلمنهوياة'
LATIN = {
    'ء': 'e', 'ب': 'b', 'ت': 't', 'ث': 'ṡ', 'ج': 'c', 'ح': 'h', 'خ': 'ḫ', 'د': 'd', 'ذ': 'ẕ', 'ر': 'r', 'ز': 'z',
    'س': 's', 'ش': 'ş', 'ص': 'ṣ', 'ض': 'ḍ', 'ط': 'ṭ', 'ظ': 'ẓ', 'ع': 'ʿ', 'غ': 'ğ', 'ف': 'f', 'ق': 'ḳ', 'ك': 'k',
    'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'ĥ', 'و': 'v', 'ي': 'y', 'ا': 'ā', 'ة': 'ẗ',
}
GURULTU = re.compile('[ـً-ْٰ]')
GENISLIK = 100
ARA = ' ' * 4

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baz_fiil as BF


def temiz(k):
    return GURULTU.sub('', k).replace('ى', 'ي')


def latin(k):
    return ''.join(LATIN[c] for c in k)


def anahtar(k):
    return tuple(SIRA.index(c) for c in k)


def topla():
    sonuc = {}
    for ad in ('kuranda_var', 'kuranda_yok'):
        d0 = os.path.join(KD, ad, 'kokler')
        for fn in sorted(os.listdir(d0)):
            d = json.load(open(os.path.join(d0, fn), encoding='utf-8'))
            d.setdefault('kelimeler', [])
            tur = BF.kok_turu(d)['tur']
            k = temiz(d['kok'])
            if k not in sonuc or ad == 'kuranda_var':
                sonuc[k] = tur
    return sonuc


def bolum(baslik, kokler):
    satirlar = [baslik, '']
    onceki = None
    cizgi = ''
    for k in sorted(kokler, key=anahtar):
        if onceki is not None and k[0] != onceki:
            satirlar.append(cizgi)
            satirlar.append('')
            cizgi = ''
        onceki = k[0]
        x = latin(k)
        if cizgi and len(cizgi) + len(ARA) + len(x) > GENISLIK:
            satirlar.append(cizgi)
            cizgi = x
        else:
            cizgi = cizgi + ARA + x if cizgi else x
    satirlar.append(cizgi)
    return '\n'.join(satirlar)


def calis():
    s = topla()
    fiil = [k for k, t in s.items() if t == 'fiil']
    isim = [k for k, t in s.items() if t == 'isim']
    tum = [latin(k) for k in s]
    assert len(set(tum)) == len(tum)
    metin = bolum('FİİL KÖKLERİ', fiil) + '\n\n\n' + bolum('İSİM KÖKLERİ', isim) + '\n'
    with open(os.path.join(KD, 'KOKLER.txt'), 'w', encoding='utf-8') as f:
        f.write(metin)
    return len(fiil), len(isim)


if __name__ == '__main__':
    print(calis())
