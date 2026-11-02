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
SAYILI = [
    (r'(\d+)-cube', '{0} buudlu mükâab (hiper-mükâab)'), (r'(\d+)-cubic', '{0} buudlu mükâabî'), (r'(\d+)-demicube', '{0} buudlu nîm-mükâab'),
    (r'(\d+)-demicubic', '{0} buudlu nîm-mükâabî'), (r'(\d+)-simplex', '{0} buudlu basît (simpleks)'),
    (r'(\d+)-orthoplex', '{0} buudlu ortopleks (çapraz politop)'), (r'(\d+)-polytopes?', '{0} buudlu politop'),
    (r'(\d+)-cell', '{0} hücreli politop'), (r'(\d+)-manifolds?', '{0} buudlu müteşa\'ib'), (r'(\d+)-category', '{0}-makûle'),
    (r'(\d+)-sphere', '{0} buudlu küre'), (r'(\d+)-torus', '{0} buudlu halka sathı (torus)'), (r'(\d+)-gon', '{0} dıl\'lı kesîrü\'l-adlâ\''),
    (r'(\d+)-bit computing', '{0} bitlik hesap mimârîsi'), (r'(\d+)-bit', '{0} bitlik'), (r'(\d+) (\d+) polytope', '{0}_{{{1}}} politopu'),
    (r'(\d+) (\d+) honeycomb', '{0}_{{{1}}} peteği'), (r'(\d+) symmetry', '{0} tenâzuru'),
]
SONEK = [(' honeycomb', ' peteği'), (' prism', ' menşûru')]


def sayili(u):
    for son, ek in SONEK:
        if u.endswith(son):
            ic = sayili(u[:-len(son)])
            return ic + ek if ic else None
    for desen, kalip in SAYILI:
        m = re.fullmatch(desen, u)
        if m:
            return kalip.format(*m.groups())
    return None


HUSUSI = {'Q5': 'şahıs ismi', 'Q5633421': 'mecmua ismi', 'Q737498': 'mecmua ismi', 'Q1002697': 'mecmua ismi', 'Q41298': 'mecmua ismi',
          'Q11424': 'film ismi', 'Q5398426': 'dizi ismi', 'Q7397': 'yazılım ismi', 'Q341': 'yazılım ismi', 'Q9143': 'programlama lisanı ismi',
          'Q571': 'kitap ismi', 'Q7725634': 'eser ismi', 'Q47461344': 'eser ismi', 'Q3918': 'dârülfünun ismi', 'Q43229': 'teşkilât ismi',
          'Q4830453': 'şirket ismi', 'Q618779': 'mükâfat ismi', 'Q1656682': 'hâdise ismi', 'Q2085381': 'neşriyatçı ismi',
          'Q1194951': 'mükâfat ismi', 'Q11448906': 'mükâfat ismi', 'Q875538': 'dârülfünun ismi', 'Q23002039': 'dârülfünun ismi',
          'Q902104': 'dârülfünun ismi', 'Q163740': 'teşkilât ismi', 'Q45400320': 'teşkilât ismi', 'Q480242': 'teşkilât ismi', 'Q3863': 'seyyârecik ismi',
          'Q31855': 'tetkik müessesesi ismi', 'Q2659904': 'teşkilât ismi', 'Q13406463': 'liste sahifesi ismi', 'Q17524420': 'cemaat ismi', 'Q41710': 'cemaat ismi', 'Q15632617': 'hayâlî şahıs ismi', 'Q95074': 'hayâlî şahıs ismi'}
MEKAN = {'Q839954', 'Q6256', 'Q3624078', 'Q515', 'Q1549591', 'Q5119', 'Q1637706', 'Q35657', 'Q10864048', 'Q3957', 'Q532', 'Q15284', 'Q486972',
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
        s = sayili(u)
        if s:
            cikti.append((u, s, 'sayılı hendesî kalıpla karşılandı'))
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
