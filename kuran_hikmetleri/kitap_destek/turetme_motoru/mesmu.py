"""Müştakları üç sınıfa ayırır: mesmû' (lügatte/Kur'ân'da geçer), kıyâsî (görülmez ama kaideye uygun), aykırı (kaideye aykırı uydurma).
Kaideler: sülâsî masdarda bâbın gâlib kaidesi (fe'ale geçişli fa'l, geçişsiz fu'ûl; fe'ile fa'al; fe'ule fa'âle/fu'ûle),
mezîd müştaklarda bâbın lügatte kullanılması, sıfat-ı müşebbehe ve mübalağada kıyâsî sîgalar, mekânda muzâri harekesi."""
import collections
import re
import istikak as I
import turkce as T
import wikt
HAREKE = re.compile('[ً-ْٰ]')
ROMA = {'I': '', 'II': 'II', 'III': 'III', 'IV': 'IV', 'V': 'V', 'VI': 'VI', 'VII': 'VII', 'VIII': 'VIII', 'IX': 'IX', 'X': 'X', 'XI': 'XI', 'XII': 'XII', 'XIII': 'XIII'}
KURAN_BAB = {"fe'ale": '', "af'ale": 'IV', "fe''ale": 'II', "ifte'ale": 'VIII', 'fâale': 'III', "istef'ale": 'X', "tefe''ale": 'V', 'tefâale': 'VI', "infe'ale": 'VII', "if'alle": 'IX'}
MUBALAGA_KIYASI = {"fa''āl", "mif'āl", "fa'ūl", "fa'īl", "fa'il"}
MEZID_MASDAR = {"taf'īl", "mufā'ale", "fi'āl", "if'āl", "tafa''ul", "tafā'ul", "infi'āl", "ifti'āl", "if'ilāl", "istif'āl", "if'īlāl", "if'iv'āl", "if'ivvāl"}
KIYASI_GRUP = ('ism-i merre', "ism-i hey'et", 'masdar-ı mîmî', 'tafdîl', 'tasğîr')


def motor_satirlari(kok):
    sinif, satir, red = I.tablo(kok)
    T.isle(kok, satir)
    wikt.isle(kok, satir)
    gruplar = collections.OrderedDict()
    for x in satir:
        gruplar.setdefault(x['grup'], []).append([x['ad'], x['etiket'], x['ar'], x['lat'], x.get('tr', ''), x.get('guven', ''), x.get('tanik', '')])
    return gruplar


def mustak_tam(d):
    if 'mustak' in d:
        return d['mustak']
    if 'mustak_kanit' not in d:
        return {}
    gruplar = motor_satirlari(d['kok'])
    for g, j, *satir in d['mustak_kanit']:
        gruplar[g][j] = satir
    return gruplar


def genislet(d):
    if 'mustak_kanit' not in d:
        return dict(d)
    tam = mustak_tam(d)
    return collections.OrderedDict(('mustak', tam) if k == 'mustak_kanit' else (k, v) for k, v in d.items())


def kanit_ayir(kok, mustak):
    gruplar = motor_satirlari(kok)
    if list(gruplar) != list(mustak) or any(len(gruplar[g]) != len(rows) for g, rows in mustak.items()):
        return None
    return [[g, j] + r for g, rows in mustak.items() for j, r in enumerate(rows) if r != gruplar[g][j]]


def sade(s):
    return HAREKE.sub('', s)


def ar_kelimeler(metin):
    return re.findall(r'[؀-ۿً-ْٰ]+', metin or '')


def bilgi(d):
    k = d['kok']
    mesmu, bablar, harekeler = set(), set(), set()
    for e in d.get('vikisozluk') or []:
        for w in ar_kelimeler(e.get('baslik', '')):
            mesmu.add(w)
        if e.get('tur') == 'verb':
            m = re.match(r'(\S+) • \([^)]*\) ([IVX]+) (\((.*)\))?', e.get('baslik', ''))
            if m and m.group(2) in ROMA:
                bablar.add(ROMA[m.group(2)])
                if m.group(2) == 'I':
                    mz = re.search(r'non-past (\S+)', m.group(4) or '')
                    harekeler.add((ayn(m.group(1), k), ayn(mz.group(1), k) if mz else '?'))
    for g in d.get('kelimeler', []):
        for w in [g.get('lemma')] + [b.get('kelime') for b in g.get('bicimler', [])]:
            if w: mesmu.add(w); mesmu.add(re.sub('^ٱل', '', w))
        if g.get('bab') in KURAN_BAB: bablar.add(KURAN_BAB[g['bab']])
    for L in mustak_tam(d).values():
        for x in L:
            if (x[6] and x[6].startswith('Vikisözlük')) or x[5] in ('lugat', 'kuran'): mesmu.add(x[2])
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
    out = {}
    for g, L in mustak_tam(d).items():
        for j, x in enumerate(L):
            bm = re.search(r'bâb ([IVX]+)', g)
            grup, ad, etiket, bab = g, x[0], x[1], bm.group(1) if bm else ''
            vez = ad.split(' + ')[0].strip()
            if x[2] in mesmu:
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
