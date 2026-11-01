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
    cikti = []
    for u in rows:
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
