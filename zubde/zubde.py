import sys, re, pathlib

LEVHA_HADDI = 100
DAL_HADDI = 9
SATIR = re.compile(r'^(\d+(?:\.\d+)*)\s+([A-Z])([*?]?)\s+(.*)$')
BAG = re.compile(r'^([<!=~])(\d+(?:\.\d+)*)$')
CINSLER = set('KBTHDMSIUVN')


def oku(yol):
    dugumler, sira, son = {}, [], None
    for no, ham in enumerate(pathlib.Path(yol).read_text(encoding='utf-8').splitlines(), 1):
        if not ham.strip():
            continue
        if ham[0] in ' \t':
            assert son is not None, 'satır %d: gövde düğümsüz' % no
            dugumler[son]['govde'].append(ham.strip())
            continue
        m = SATIR.match(ham)
        assert m, 'satır %d: düğüm satırı okunamadı: %s' % (no, ham)
        adres, cins, damga, kalan = m.groups()
        assert cins in CINSLER, 'satır %d: cins bilinmiyor: %s' % (no, cins)
        assert adres not in dugumler, 'satır %d: adres iki kere: %s' % (no, adres)
        kelimeler, baglar = kalan.split(), []
        while kelimeler and BAG.match(kelimeler[-1]):
            b = BAG.match(kelimeler.pop())
            baglar.insert(0, (b.group(1), b.group(2)))
        dugumler[adres] = dict(adres=adres, cins=cins, damga=damga, levha=' '.join(kelimeler),
                               baglar=baglar, govde=[], satir=no, sira=len(sira))
        sira.append(adres)
        son = adres
    return dugumler, sira


def baba(adres):
    if adres == '0':
        return None
    return adres.rsplit('.', 1)[0] if '.' in adres else '0'


def denetle(d, sira):
    ihlal = []
    assert sira and sira[0] == '0', 'ilk düğüm kök (0) olmalı'
    cocuk = {a: [] for a in sira}
    for a in sira[1:]:
        b = baba(a)
        if b not in d or d[b]['sira'] > d[a]['sira']:
            ihlal.append('K6 %s: babası (%s) evvel yazılmamış' % (a, b))
            continue
        cocuk[b].append(a)
    gorulen = {}
    for a in sira:
        n = d[a]
        if len(n['levha']) > LEVHA_HADDI:
            ihlal.append('K1 %s: levha %d harf' % (a, len(n['levha'])))
        if not n['levha']:
            ihlal.append('K1 %s: levha boş' % a)
        if len(cocuk[a]) > DAL_HADDI:
            ihlal.append('K2 %s: %d çocuk' % (a, len(cocuk[a])))
        if n['cins'] == 'H' and not n['damga'] and not any(t == '<' for t, _ in n['baglar']):
            ihlal.append('K3 %s: hüküm dayanaksız ve damgasız' % a)
        metin = ' '.join([n['levha']] + n['govde']).lower()
        if metin in gorulen:
            ihlal.append('K4 %s: %s ile aynı muhteva' % (a, gorulen[metin]))
        gorulen[metin] = a
        for t, h in n['baglar']:
            if h not in d:
                ihlal.append('K6 %s: bağın ucu yok: %s' % (a, h))
            elif t == '<' and d[h]['sira'] >= n['sira']:
                ihlal.append('K6 %s: sonra yazılana dayanıyor: %s' % (a, h))
    return ihlal, cocuk


def boy(n):
    return len(n['levha']) + sum(len(g) for g in n['govde'])


def koni(d, a, bellek):
    if a in bellek:
        return bellek[a]
    k = {a}
    for t, h in d[a]['baglar']:
        if t == '<' and h in d:
            k |= koni(d, h, bellek)
    bellek[a] = k
    return k


def olc(d, sira, cocuk):
    bellek = {}
    derinlik = max(a.count('.') + 1 if a != '0' else 0 for a in sira)
    kat = {}
    for a in sira:
        s = 0 if a == '0' else a.count('.') + 1
        kat[s] = kat.get(s, 0) + len(d[a]['levha'])
    toplam = sum(boy(d[a]) for a in sira)
    isaret = sum(len(a) + 2 + len(d[a]['damga']) + sum(len(h) + 2 for _, h in d[a]['baglar']) for a in sira)
    koniler = {a: sum(boy(d[x]) for x in koni(d, a, bellek)) for a in sira}
    baslar = {}
    gecen = 0
    for a in sira:
        gecen += boy(d[a])
        baslar[a] = gecen
    return dict(dugum=len(sira), derinlik=derinlik, oz=toplam, isaret=isaret, hacim=toplam + isaret,
                kat_harf=kat, azami_koni=max(koniler.values()),
                ortalama_koni=round(sum(koniler.values()) / len(sira)),
                ortalama_bas=round(sum(baslar.values()) / len(sira)),
                bulma_haddi=LEVHA_HADDI * DAL_HADDI * derinlik), koniler


def sayfa(yol):
    kalip = (pathlib.Path(__file__).parent / 'uygulama.html').read_text(encoding='utf-8')
    kaynak = pathlib.Path(yol).read_text(encoding='utf-8')
    assert '</script' not in kaynak.lower(), 'kaynakta betik kapanışı olamaz'
    return kalip.replace('__KAYNAK__', kaynak)


def kos(yol, asil=None):
    d, sira = oku(yol)
    ihlal, cocuk = denetle(d, sira)
    olcu, _ = olc(d, sira, cocuk)
    print(yol)
    for k in ('dugum', 'derinlik', 'oz', 'isaret', 'hacim', 'bulma_haddi', 'azami_koni', 'ortalama_koni', 'ortalama_bas'):
        print('  %-14s %s' % (k, olcu[k]))
    print('  kat_harf      ', olcu['kat_harf'])
    if asil:
        a = len(pathlib.Path(asil).read_text(encoding='utf-8'))
        olcu['asil'] = a
        print('  asıl metin     %d harf; nispet %.3f' % (a, olcu['hacim'] / a))
    print('  ihlâl          %d' % len(ihlal))
    for i in ihlal:
        print('   ', i)
    cikti = pathlib.Path(yol).with_suffix('.html')
    cikti.write_text(sayfa(yol), encoding='utf-8')
    return len(ihlal)


if __name__ == '__main__':
    assert len(sys.argv) >= 2, 'kullanım: python zubde.py dosya.zbd [asıl_metin]'
    sys.exit(1 if kos(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None) else 0)
