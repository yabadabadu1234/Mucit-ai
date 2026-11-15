"""Kapı: bir ajan bölümü bitirdi diye durumu 'tamam' yapınca bu kapı sert şartları sayar; geçmezse sebepleri ajana geri verilir."""
import sys

import osmanlica_denetle as D

SERT = ('arapca_latin_karisik', 'etiket_kapanis_hatali', 'serh_yok', 'esas_yok', 'tashih_notu', 'uzun_arapca_ibare', 'kaynak_adi_gecti', 'ilave_dolu')


def etiketler(t):
    import re
    c = {}
    for e in D.ETIKET.findall(t):
        k = re.sub(r'\s*\d+$', '', e.strip())
        c[k] = c.get(k, 0) + 1
    return c


def gerileme(dizin, bolum, onceki):
    """İnceleme öncesi sürümle karşılaştırır: hiçbir etiketli kısım azalamaz, tercüme %40'tan fazla kısalamaz (atıf yığınını mantığa çevirmek kısaltabilir)."""
    _, eski = D.bolum_oku(onceki)
    _, yeni = D.bolum_oku(dizin + '/' + bolum)
    ey = {r['id']: r for r in yeni}
    hata = []
    for r in eski:
        t0 = r.get('tercüme', '')
        y = ey.get(r['id'])
        if y is None:
            hata.append('satır silinmiş: %s' % r['id'])
            continue
        t1 = y.get('tercüme', '')
        e0, e1 = etiketler(t0), etiketler(t1)
        kayip = {k: (v, e1.get(k, 0)) for k, v in e0.items() if e1.get(k, 0) < v}
        if kayip:
            hata.append('%s satırında etiketli kısım azalmış %s' % (r['id'][:30], kayip))
        elif len(t1) < 0.6 * len(t0):
            hata.append('%s satırı kısalmış (%d → %d karakter)' % (r['id'][:30], len(t0), len(t1)))
    return hata


def kapi(dizin, bolum, onceki=None):
    kay = D.kaynak_metni(dizin)
    r = D.denetle(dizin + '/' + bolum, dizin, kay)
    hata = []
    if r['bos_tercume']:
        hata.append('%d satırın tercüme: alanı boş' % r['bos_tercume'])
    for k in SERT:
        if k in r['sorunlar']:
            n, ornek = r['sorunlar'][k]
            hata.append('%s: %d satır, örnek: %s' % (k, n, ornek))
    if onceki:
        hata += gerileme(dizin, bolum, onceki)
    return hata


if __name__ == '__main__':
    h = kapi(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print('; '.join(h))
    sys.exit(1 if h else 0)
