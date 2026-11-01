import os, re, sys, glob, math, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSC = os.path.join(KOK, 'msc2020', 'msc2020_osmanlica.tsv')
VIKI = sys.argv[1] if len(sys.argv) > 1 else os.path.join(KOK, 'vikipedi')
CIKTI = sys.argv[2] if len(sys.argv) > 2 else os.path.join(KOK, 'telif')
ONEK = re.compile(r'^(lists? of|outline of|glossary of|index of|tables? of|timeline of)\s+', re.I)
BOS = {'and', 'or', 'of', 'the', 'in', 'on', 'for', 'to', 'a', 'an', 'with', 'by', 'etc', 'other', 'general',
       'theory', 'topics', 'mathematics', 'mathematical', 'its', 'their', 'related', 'including', 'aspects', 'problems'}


def sade(s):
    s = re.sub(r'\[[^\]]*\]|\{[^}]*\}', ' ', s).lower()
    s = re.sub(r'[^0-9a-zà-ɏ]+', ' ', s)
    return ' '.join(s.split())


def kelimeler(s):
    return {k[:-1] if k.endswith('s') and len(k) > 4 else k for k in sade(s).split() if k not in BOS and len(k) > 2}


def msc_oku():
    satirlar = open(MSC, encoding='utf-8').read().rstrip('\n').split('\n')[1:]
    return [tuple((r.split('\t') + [''] * 4)[:4]) for r in satirlar]


def msc_ustu(kod):
    if kod.endswith('-XX'):
        return ''
    if re.match(r'^\d\d-\d\d$', kod) or re.match(r'^\d\d[A-Z]xx$', kod):
        return kod[:2] + '-XX'
    return kod[:3] + 'xx'


def viki_oku():
    yol = os.path.join(VIKI, 'unsurlar.tsv')
    if not os.path.exists(yol):
        return [], {}
    unsur = []
    for r in open(yol, encoding='utf-8').read().rstrip('\n').split('\n')[1:]:
        p = r.split('\t')
        unsur.append((p[0], [x for x in p[2].split(' | ') if x] if len(p) > 2 else []))
    ceviri = {}
    for y in sorted(glob.glob(os.path.join(VIKI, 'ceviri', '*.tsv'))):
        for r in open(y, encoding='utf-8'):
            p = r.rstrip('\n').split('\t')
            if len(p) >= 2 and not p[0].startswith('@'):
                assert p[0] not in ceviri, ('mükerrer Vikipedi karşılığı', p[0])
                ceviri[p[0]] = (p[1], p[2] if len(p) > 2 else '')
    return unsur, ceviri


def main():
    msc = msc_oku()
    unsur, viki_ceviri = viki_oku()
    adlar = [u[0] for u in unsur]
    assert len(set(adlar)) == len(adlar), 'unsurlar.tsv içinde mükerrer başlık var'
    sade_msc = collections.defaultdict(list)
    for kod, ing, _, _ in msc:
        sade_msc[sade(ing)].append(kod)
    basliklar = {kod: (ing, osm) for kod, ing, osm, _ in msc}
    msc_kume = [(kod, kelimeler(ing)) for kod, ing, _, _ in msc]
    sayi = collections.Counter(k for _, kk in msc_kume for k in kk)
    agirlik = {k: math.log(len(msc) / s) for k, s in sayi.items()}

    def en_yakin(baslik, liste_kume):
        enk, puan = '', 0.0
        for kod, kk in msc_kume:
            p = 2 * sum(agirlik[k] for k in baslik & kk) + sum(agirlik[k] for k in liste_kume & kk)
            if p > puan:
                enk, puan = kod, p
        if not enk:
            return ''
        return enk if enk.endswith('-XX') or re.match(r'^\d\d[A-Z]xx$', enk) else msc_ustu(enk)

    telif, tekrar, ustsuz = [], 0, 0
    tekrar_eden = collections.defaultdict(list)
    for u, listeler in unsur:
        kodlar = sade_msc.get(sade(u))
        if kodlar:
            tekrar += 1
            for k in kodlar:
                tekrar_eden[k].append((u, listeler))
    for kod, ing, osm, kayit in msc:
        viki = tekrar_eden.get(kod, [])
        mense = 'MSC2020 + Vikipedi' if viki else 'MSC2020'
        vlist = ' | '.join(sorted({x for _, ls in viki for x in ls}))
        ust = msc_ustu(kod)
        telif.append((kod, mense, ing, osm, ust, basliklar.get(ust, ('', ''))[1], vlist, kayit))
    for u, listeler in unsur:
        if sade(u) in sade_msc:
            continue
        liste_kume = set()
        for l in listeler:
            liste_kume |= kelimeler(ONEK.sub('', l))
        ust = en_yakin(kelimeler(u), liste_kume)
        kayit = viki_ceviri.get(u, ('', ''))[1]
        if ust:
            kayit = (kayit + '; ' if kayit else '') + 'üst başlık kelime örtüşmesiyle otomatik tayin edildi'
        else:
            ustsuz += 1
            kayit = (kayit + '; ' if kayit else '') + 'üst başlık tayin edilemedi'
        osm = viki_ceviri.get(u, ('', ''))[0]
        telif.append(('V:' + u, 'Vikipedi', u, osm, ust, basliklar.get(ust, ('', ''))[1], ' | '.join(sorted(listeler)), kayit))
    beklenen = len(msc) + len(unsur) - tekrar
    if len(telif) != beklenen:
        raise SystemExit('HATA: telif mensup sayısı %d, beklenen %d (MSC %d + Vikipedi %d − tekrar %d)'
                         % (len(telif), beklenen, len(msc), len(unsur), tekrar))
    os.makedirs(CIKTI, exist_ok=True)
    with open(os.path.join(CIKTI, 'telif.tsv'), 'w', encoding='utf-8') as f:
        f.write('kimlik\tmenşe\tİngilizce\tOsmanlıca\tüst başlık kodu\tüst başlık\tVikipedi listeleri\tkayıt\n')
        for r in telif:
            f.write('\t'.join(r) + '\n')
    karsiliksiz = sum(1 for r in telif if not r[3])
    with open(os.path.join(CIKTI, 'TELIF.md'), 'w', encoding='utf-8') as f:
        f.write('# Telif — MSC2020 ile Vikipedi Listelerinin İmtizâcı\n\n')
        f.write('Bu sahife `araclar/telif.py` ile üretilir; elle değiştirilmez. Ana kaynaklar ve karşılık dosyaları yerinde durur.\n\n')
        f.write('| Ölçü | Sayı |\n| :-- | --: |\n')
        for ad, s in (('MSC2020 unsuru', len(msc)), ('Vikipedi unsuru', len(unsur)), ('Tekrar (birleştirilen)', tekrar),
                      ('Telif mensubu', len(telif)), ('Üst başlığı tayin edilemeyen Vikipedi unsuru', ustsuz),
                      ('Osmanlıca karşılığı henüz olmayan mensup', karsiliksiz)):
            f.write('| %s | %d |\n' % (ad, s))
        f.write('\nDoğrulama: %d = %d + %d − %d tuttu.\n' % (len(telif), len(msc), len(unsur), tekrar))
    print('telif', len(telif), '= MSC', len(msc), '+ Vikipedi', len(unsur), '− tekrar', tekrar,
          '· üstsüz', ustsuz, '· karşılıksız', karsiliksiz)


main()
