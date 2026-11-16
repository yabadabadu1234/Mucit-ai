"""Müştakları üç sınıfa ayırır: mesmû' (lügatte/Kur'ân'da geçer), kıyâsî (görülmez ama kaideye uygun), aykırı (kaideye aykırı uydurma).
Kaideler: sülâsî masdarda bâbın gâlib kaidesi (fe'ale geçişli fa'l, geçişsiz fu'ûl; fe'ile fa'al; fe'ule fa'âle/fu'ûle),
mezîd müştaklarda bâbın lügatte kullanılması, sıfat-ı müşebbehe ve mübalağada kıyâsî sîgalar, mekânda muzâri harekesi."""
import re
import turkce as T
HAREKE = re.compile('[ً-ْٰ]')
ROMA = {'I': '', 'II': 'II', 'III': 'III', 'IV': 'IV', 'V': 'V', 'VI': 'VI', 'VII': 'VII', 'VIII': 'VIII', 'IX': 'IX', 'X': 'X', 'XI': 'XI', 'XII': 'XII', 'XIII': 'XIII'}
KURAN_BAB = {"fe'ale": '', "af'ale": 'IV', "fe''ale": 'II', "ifte'ale": 'VIII', 'fâale': 'III', "istef'ale": 'X', "tefe''ale": 'V', 'tefâale': 'VI', "infe'ale": 'VII', "if'alle": 'IX'}
MUBALAGA_KIYASI = {"fa''āl", "mif'āl", "fa'ūl", "fa'īl", "fa'il"}
MEZID_MASDAR = {"taf'īl", "mufā'ale", "fi'āl", "if'āl", "tafa''ul", "tafā'ul", "infi'āl", "ifti'āl", "if'ilāl", "istif'āl", "if'īlāl", "if'iv'āl", "if'ivvāl"}
KIYASI_GRUP = ('ism-i merre', "ism-i hey'et", 'masdar-ı mîmî', 'tafdîl', 'tasğîr')


def sade(s):
    return HAREKE.sub('', s)


def ar_kelimeler(metin):
    return re.findall(r'[؀-ۿً-ْٰ]+', metin or '')


def bilgi(d):
    k = d['kok']; soz = d.get('sozlukler') or {}
    mesmu, bablar, harekeler = set(), set(), set()
    for e in soz.get('kaikki_vikisozluk') or []:
        for w in ar_kelimeler(e.get('e', '')):
            mesmu.add(w)
        if e.get('p') == 'verb':
            m = re.match(r'(\S+) • \([^)]*\) ([IVX]+) (\((.*)\))?', e.get('e', ''))
            if m and m.group(2) in ROMA:
                bablar.add(ROMA[m.group(2)])
                if m.group(2) == 'I':
                    mz = re.search(r'non-past (\S+)', m.group(4) or '')
                    harekeler.add((ayn(m.group(1), k), ayn(mz.group(1), k) if mz else '?'))
    for e in d.get('kelimeler', []):
        for w in (e.get('lemma'), e.get('kelime')):
            if w: mesmu.add(w); mesmu.add(re.sub('^ٱل', '', w))
        if e.get('bab') in KURAN_BAB: bablar.add(KURAN_BAB[e['bab']])
    for L in (d.get('mustaklar') or {}).values():
        for x in L:
            if x[5] and x[5].startswith('Vikisözlük'): mesmu.add(x[1])
    return mesmu, bablar, harekeler


def ayn(w, k):
    for i, ch in enumerate(w):
        if ch == k[1] and i + 1 < len(w) and w[i + 1] in 'َُِ':
            return {'َ': 'a', 'ُ': 'u', 'ِ': 'i'}[w[i + 1]]
    return '?'


def galib_masdar(harekeler, gecisli):
    if not harekeler:
        return {"fa'l"}
    s = set()
    for m, z in harekeler:
        if m == 'u': s |= {"fa'āle", "fu'ūle"}
        elif m == 'i': s |= ({"fa'al"} if not gecisli else {"fa'l", "fa'al"})
        else: s |= ({"fa'l"} if gecisli else {"fu'ūl"})
    return s


def siniflar(d):
    """d: kök dosyası; döner: {(grup, sıra): 'mesmu'|'kiyasi'|'aykiri'}"""
    mesmu, bablar, harekeler = bilgi(d)
    bil = T.kok_bilgisi(d['kok'])
    gecisli = bool(bil) and bil.get('tr') in ('tr', 'aux')
    galib = galib_masdar(harekeler, gecisli)
    muzari = {z for _, z in harekeler}
    K = d.get('kaliplar') or {}
    out = {}
    for g, L in (d.get('mustaklar') or {}).items():
        for j, x in enumerate(L):
            kal = K.get(str(x[0]), [g, '', '', ''])
            grup, ad, etiket, bab = kal[0], kal[1], kal[2], kal[3]
            vez = ad.split(' + ')[0].strip()
            if x[1] in mesmu:
                out[(g, j)] = 'mesmu'; continue
            if bab and bab not in bablar:
                out[(g, j)] = 'aykiri'; continue
            if 'sülâsî' in grup or not bab:
                if not bablar or '' in bablar or not harekeler:
                    pass
            if grup.startswith('masdar · sülâsî'):
                s = 'kiyasi' if vez in galib else 'aykiri'
            elif (grup.startswith('masdar ·') or grup.startswith('ism-i merre ·')) and bab:
                s = 'kiyasi' if vez in MEZID_MASDAR else 'aykiri'
            elif grup.startswith('masdar') or grup.startswith('mekân/zaman/masdar'):
                s = 'kiyasi'
            elif grup.startswith('ism-i fâil') or grup.startswith('ism-i mef'):
                s = 'kiyasi' if (bab or gecisli or not grup.startswith('ism-i mef')) and 'lâzım bâb' not in etiket else 'aykiri'
            elif grup.startswith('mekân/zaman'):
                s = 'kiyasi' if (vez == "maf'al" and (not muzari or muzari & {'a', 'u', '?'})) or (vez == "maf'il" and 'i' in muzari) else 'aykiri'
            elif grup.startswith('âlet'):
                s = 'kiyasi' if gecisli else 'aykiri'
            elif grup.startswith(KIYASI_GRUP):
                s = 'kiyasi'
            elif grup.startswith('sıfat-ı müşebbehe'):
                m = {h for h, _ in harekeler}
                s = 'kiyasi' if (vez == "fa'īl" and 'u' in m) or (vez == "fa'il" and 'i' in m and not gecisli) else 'aykiri'
            elif grup.startswith('mübalağa'):
                s = 'kiyasi' if vez in MUBALAGA_KIYASI and gecisli else 'aykiri'
            elif grup.startswith('mensûb') or grup.startswith('masdar-ı sınâî'):
                s = 'kiyasi' if vez in galib or vez in ("fâ'il", "maf'ûl", "maf'al") else 'aykiri'
            else:
                s = 'aykiri'
            out[(g, j)] = s
    return out
