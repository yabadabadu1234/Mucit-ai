import re, sys, os, glob, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSC = os.path.join(KOK, 'msc2020')

KALIP = {
    '00': '{X} hakkında umûmî mürâcaat eserleri (el kitapları, lügatler, kitâbiyât fihristleri ve emsâli)',
    '01': '{X} hakkında medhal mâhiyetinde şerh ve beyan (ders kitapları, talîmî makaleler ve emsâli)',
    '02': '{X} hakkında tetkik mâhiyetinde şerh ve beyan (müstakil risâleler, umûmî nazar makaleleri)',
    '04': '{X} sahasındaki meselelere dair programlar (yazılımlar), menba metinleri ve emsâli',
    '05': '{X} sahasındaki meselelere dair tecrübî çalışmalar',
    '06': '{X} hakkında ilmî meclis zabıtları, kongreler, mecmualar ve emsâli',
    '08': '{X} sahasındaki meselelere dair hesap usulleri',
    '10': '{X} sahasındaki meselelere dair riyâzî numûne kurma (temsil) yahut taklit (benzetim)',
    '11': '{X} sahasındaki meselelere dair tetkik verileri',
}
HICBIRI = 'Yukarıdakilerin hiçbiri olmayıp bu babda bulunanlar'
KODLAR = r'\d\d(?:-XX|-\d\d|[A-Z]xx|[A-Z]\d\d)'


def kodlari_cevir(s):
    return s.replace(' and ', ' ve ').replace('–', '–')


def ayrica_bak(ing):
    m = re.search(r'\[See also ((?:' + KODLAR + r')(?:(?:, | and |, and )' + KODLAR + r')*)\]\s*$', ing)
    if m:
        return ' [Ayrıca bakınız: ' + kodlari_cevir(m.group(1)) + ']'
    return ''


def main():
    kaynak = []
    for satir in open(os.path.join(MSC, 'kaynak.tsv'), encoding='utf-8'):
        kod, ing = satir.rstrip('\n').split('\t')
        kaynak.append((kod, ing))
    ceviri, ilgi, notlar = {}, {}, {}
    for yol in sorted(glob.glob(os.path.join(MSC, 'ceviri', '*.tsv'))):
        for no, satir in enumerate(open(yol, encoding='utf-8'), 1):
            satir = satir.rstrip('\n')
            if not satir.strip():
                continue
            parca = satir.split('\t')
            if parca[0].startswith('@ilgi'):
                ilgi[parca[0][5:].strip() or os.path.basename(yol)[:2]] = parca[1]
                continue
            assert len(parca) in (2, 3), (yol, no, satir)
            assert parca[0] not in ceviri, ('mükerrer', parca[0])
            ceviri[parca[0]] = parca[1]
            if len(parca) == 3:
                notlar[parca[0]] = parca[2]
    bilinen = {k for k, _ in kaynak}
    yabanci = [k for k in ceviri if k not in bilinen]
    assert not yabanci, ('kaynakta olmayan kod', yabanci[:10])
    cikti, eksik = [], collections.Counter()
    for kod, ing in kaynak:
        bab = kod[:2]
        osm = ceviri.get(kod)
        if osm is None:
            m = re.match(r'^\d\d-(\d\d)$', kod)
            if m and m.group(1) in KALIP and bab in ilgi and 'pertaining to' in ing:
                osm = KALIP[m.group(1)].format(X=ilgi[bab]) + ayrica_bak(ing)
            elif kod.endswith('99') and ing == 'None of the above, but in this section':
                osm = HICBIRI
        elif '[' not in osm:
            osm = osm + ayrica_bak(ing)
        if osm is None:
            eksik[bab] += 1
            osm = ''
        cikti.append((kod, ing, osm, notlar.get(kod, '')))
    with open(os.path.join(MSC, 'msc2020_osmanlica.tsv'), 'w', encoding='utf-8') as f:
        f.write('kod\tİngilizce\tOsmanlıca\tkayıt\n')
        for r in cikti:
            f.write('\t'.join(r) + '\n')
    with open(os.path.join(MSC, 'MSC2020_OSMANLICA.md'), 'w', encoding='utf-8') as f:
        f.write('# MSC2020 Riyâzî Mevzûlar Tasnifi — Osmanlıca Karşılıklarıyla\n\n')
        f.write('Bu sahife `araclar/msc_birlestir.py` ile `kaynak.tsv` ve `ceviri/` dosyalarından üretilir; elle değiştirilmez.\n\n')
        toplam = len(cikti)
        tamam = sum(1 for r in cikti if r[2])
        f.write('Toplam madde: %d · karşılığı bulunan: %d · kalan: %d\n\n' % (toplam, tamam, toplam - tamam))
        for kod, ing, osm, nt in cikti:
            if kod.endswith('-XX'):
                f.write('\n## %s — %s\n\n%s\n\n| Kod | İngilizce | Osmanlıca | Kayıt |\n| :-- | :-- | :-- | :-- |\n' % (kod, osm or ing, ing))
                continue
            if re.match(r'^\d\d[A-Z]xx$', kod):
                f.write('| **%s** | **%s** | **%s** | %s |\n' % (kod, ing.replace('|', '\\|'), osm.replace('|', '\\|'), nt))
                continue
            f.write('| %s | %s | %s | %s |\n' % (kod, ing.replace('|', '\\|'), osm.replace('|', '\\|'), nt))
    print('toplam', len(cikti), 'karşılıksız', sum(eksik.values()))
    for b in sorted(eksik):
        print(' bab', b, 'karşılıksız', eksik[b])


main()
