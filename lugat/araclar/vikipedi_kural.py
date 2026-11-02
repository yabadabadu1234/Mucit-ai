import os, re

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIKI = os.path.join(KOK, 'vikipedi')
KURALLAR = [
    (re.compile(r'^([\d,]+) \(number\)$'), lambda m: '%s (adet)' % m.group(1), ''),
    (re.compile(r'^[\d,]+$'), lambda m: m.group(0), 'nakil: rakam'),
]


BAS = {
    'theorem': 'kaziyyesi', 'theorems': 'kaziyyeleri', 'conjecture': 'tahmini', 'lemma': 'mukaddimesi', 'inequality': 'adem-i müsâvâtı',
    'equation': 'muâdelesi', 'equations': 'muâdeleleri', 'identity': 'ayniyeti', 'formula': 'düstûru', 'algorithm': 'hârizmîsi',
    'problem': 'meselesi', 'number': 'adedi', 'numbers': 'adetleri', 'constant': 'sâbiti', 'function': 'tâbii', 'functions': 'tâbileri',
    'polynomial': 'kesîrü\'l-hudûdu', 'polynomials': 'kesîrü\'l-hudûdları', 'space': 'fezâsı', 'spaces': 'fezâları', 'group': 'zümresi',
    'transform': 'tahvîli', 'distribution': 'tevzîi', 'criterion': 'mi\'yârı', 'method': 'usulü', 'series': 'silsilesi',
    'sequence': 'tevâlîsi', 'integral': 'tamâmîsi', 'operator': 'âmili', 'matrix': 'masfûfesi', 'curve': 'münhanîsi',
    'surface': 'sathı', 'manifold': 'müteşa\'ibi', 'ring': 'halkası', 'algebra': 'cebri', 'condition': 'şartı', 'conditions': 'şartları',
    'graph': 'rabıta şekli', 'polygon': 'kesîrü\'l-adlâ\'ı', 'triangle': 'müsellesi', 'circle': 'dâiresi', 'point': 'noktası',
    'points': 'noktaları', 'line': 'hattı', 'measure': 'mikyâsı', 'process': 'cereyanı', 'category': 'makûlesi', 'complex': 'mürekkebi',
    'bundle': 'huzmesi', 'sheaf': 'destesi', 'variety': 'mütenevviası', 'lattice': 'kafesi', 'paradox': 'mugalatası',
}
HUSUSI = {'Q5': 'şahıs ismi', 'Q5633421': 'mecmua ismi', 'Q737498': 'mecmua ismi', 'Q1002697': 'mecmua ismi', 'Q41298': 'mecmua ismi',
          'Q11424': 'film ismi', 'Q5398426': 'dizi ismi', 'Q7397': 'yazılım ismi', 'Q341': 'yazılım ismi', 'Q9143': 'programlama lisanı ismi',
          'Q571': 'kitap ismi', 'Q7725634': 'eser ismi', 'Q47461344': 'eser ismi', 'Q3918': 'dârülfünun ismi', 'Q43229': 'teşkilât ismi',
          'Q4830453': 'şirket ismi', 'Q618779': 'mükâfat ismi', 'Q1656682': 'hâdise ismi', 'Q2085381': 'neşriyatçı ismi',
          'Q1194951': 'mükâfat ismi', 'Q15632617': 'hayâlî şahıs ismi', 'Q95074': 'hayâlî şahıs ismi'}
MEKAN = {'Q6256', 'Q3624078', 'Q515', 'Q1549591', 'Q5119', 'Q1637706', 'Q35657', 'Q10864048', 'Q3957', 'Q532', 'Q15284', 'Q486972',
         'Q107390', 'Q34876', 'Q1093829', 'Q484170', 'Q747074', 'Q123705', 'Q200250'}
NAKIL_SEMT = re.compile(r"^((?:[A-Z][\w\-–'’.]*\s?)+?)('s|’s)? ([a-z]+)$")


def main():
    rows = [r.split('\t')[0] for r in open(os.path.join(VIKI, 'unsurlar.tsv'), encoding='utf-8').read().rstrip('\n').split('\n')[1:]]
    kucuk = set()
    for u in rows:
        kucuk |= {w for w in re.findall(r"[A-Za-z]+", u) if w.islower()}
    for r in open(os.path.join(KOK, 'msc2020', 'kaynak.tsv'), encoding='utf-8'):
        kucuk |= {w for w in re.findall(r"[A-Za-z]+", r) if w.islower()}
    ozel = set()
    metinler = rows + [r.split('\t')[1] for r in open(os.path.join(KOK, 'msc2020', 'kaynak.tsv'), encoding='utf-8').read().rstrip('\n').split('\n')]
    for u in metinler:
        kel = re.findall(r"[A-Za-zÀ-ɏ]+", u)
        ozel |= {w for w in kel[1:] if w[0].isupper()}
    sifat = {}
    yol = os.path.join(VIKI, 'sifatlar.tsv')
    if os.path.exists(yol):
        for r in open(yol, encoding='utf-8').read().rstrip('\n').split('\n')[1:]:
            p = r.split('\t')
            sifat[p[0]] = (set(p[3].split(',')) - {''}, p[4])
    cikti = []
    for u in rows:
        tip, tr = sifat.get(u, (set(), ''))
        hus = [HUSUSI[q] for q in sorted(tip) if q in HUSUSI]
        if hus:
            cikti.append((u, u, 'nakil: ' + hus[0] + ' (Vikiveri P31)'))
            continue
        if tip & MEKAN:
            cikti.append((u, tr or u, ('Türkçe Vikipedi başlığından alındı; mekân ismi' if tr else 'nakil: mekân ismi') + ' (Vikiveri P31)'))
            continue
        for desen, cevir, kayit in KURALLAR:
            m = desen.match(u)
            if m:
                cikti.append((u, cevir(m), kayit))
                break
        else:
            m = NAKIL_SEMT.match(u)
            if m and m.group(3) in BAS:
                isim = m.group(1).strip()
                kelime = re.findall(r"[A-Za-zÀ-ɏ0-9]+", isim)
                kisaltma = any(re.search(r'[A-Z]{2}|\d', w) for w in kelime)
                if not kisaltma and kelime and (m.group(2) or all(w in ozel and w.lower() not in kucuk for w in kelime)):
                    cikti.append((u, isim + ' ' + BAS[m.group(3)], 'nakil: hususî isim; kalıpla karşılandı'))
    with open(os.path.join(VIKI, 'ceviri', '00_kural.tsv'), 'w', encoding='utf-8') as f:
        for r in cikti:
            f.write('\t'.join(r) + '\n')
    print('kaideyle karşılanan', len(cikti))


main()
