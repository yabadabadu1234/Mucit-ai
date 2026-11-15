"""Kapı: bir ajan bölümü bitirdi diye durumu 'tamam' yapınca bu kapı sert şartları sayar; geçmezse sebepleri ajana geri verilir."""
import sys

import osmanlica_denetle as D

SERT = ('etiket_kapanis_hatali', 'serh_yok', 'esas_yok', 'tashih_notu', 'arapca_kaynakta_yok', 'ilave_dolu')


def kapi(dizin, bolum):
    kay = D.kaynak_metni(dizin)
    r = D.denetle(dizin + '/' + bolum, dizin, kay)
    hata = []
    if r['bos_tercume']:
        hata.append('%d satırın tercüme: alanı boş' % r['bos_tercume'])
    for k in SERT:
        if k in r['sorunlar']:
            n, ornek = r['sorunlar'][k]
            hata.append('%s: %d satır, örnek: %s' % (k, n, ornek))
    return hata


if __name__ == '__main__':
    h = kapi(sys.argv[1], sys.argv[2])
    print('; '.join(h))
    sys.exit(1 if h else 0)
