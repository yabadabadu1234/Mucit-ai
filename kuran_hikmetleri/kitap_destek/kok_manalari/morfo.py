"""Quranic Arabic Corpus morfolojisinden kelime parçaları (önek · gövde · sonek) ve köklerin Kur'ân'daki isim biçimleri.
Kullanan: kok_kitabi.py (lügat başlığı biçimleri, müştak kartında Kur'ân'da görülen biçimler)."""
import lzma, re, collections
from kuran_kokleri import KH, bw, lugat_basligi

def iskelet(s):
    """Harfler ve uzun ünlüler (hareke, şedde, sükûn ve küçük işaretler atılır; hançer elif uzun ünlü olarak kalır)."""
    s = (s or '').replace('\u0670', '\u0627')
    s = re.sub('[\u0610-\u061a\u064b-\u065f\u06d6-\u06ed\u0640]', '', s)
    for a, b in (('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ٱ', 'ا'), ('ؤ', 'و'), ('ئ', 'ي'), ('ى', 'ي'), ('ء', ''), ('ة', 'ه')): s = s.replace(a, b)
    return s

def yukle():
    KELIME = collections.OrderedDict()                                # (s,a,w) -> [segment]
    with lzma.open(KH / 'kaynak' / 'lugat' / 'ham' / 'quranic_arabic_corpus_morphology_0.4.txt.xz', 'rt', encoding='utf-8') as f:
        for ln in f:
            if not ln.startswith('('): continue
            loc, form, tag, ft = ln.rstrip('\n').split('\t')
            p = ft.split('|'); s_, a_, w_, m_ = (int(v) for v in loc.strip('()').split(':'))
            F = {x.split(':')[0]: x.split(':', 1)[1] for x in p if ':' in x}
            bayrak = {x for x in p if ':' not in x}
            seg = {'tur': p[0], 'tag': tag, 'biçim': bw(form, False), 'F': F, 'bayrak': bayrak, 'ozel': p[1] if p[0] in ('PREFIX', 'SUFFIX') else ''}
            if p[0] == 'STEM':
                if 'ROOT' in F: seg['anahtar'] = (bw(F['ROOT'], True), 0)
                else:
                    k = lugat_basligi(F.get('LEM') or form); seg['anahtar'] = (k, 1) if k else None
                seg['lem'] = bw(F['LEM'], False) if 'LEM' in F else ''
            KELIME.setdefault((s_, a_, w_), []).append(seg)
    return KELIME

KELIME = yukle()

def lugat_kelimeleri():
    """(k,1) -> {parça kimliği: [adet, ilk 's:a']}; parça kimliği = ((tur, ozel/tag, biçim), ...) kelimenin bütün parçaları sırayla."""
    O = collections.defaultdict(dict)
    for (s_, a_, w_), segs in KELIME.items():
        keys = {g['anahtar'] for g in segs if g['tur'] == 'STEM' and g.get('anahtar') and g['anahtar'][1] == 1}
        if not keys: continue
        kim = tuple((g['tur'], g['ozel'] if g['tur'] != 'STEM' else g['tag'], g['biçim'], g.get('anahtar') if g['tur'] == 'STEM' else None) for g in segs)
        for k in keys:
            d = O[k].setdefault(kim, [0, '%d:%d' % (s_, a_)]); d[0] += 1
    return O

def kok_isimleri():
    """kök -> {(lem, sınıf): [adet, ilk 's:a'], ...}; sınıf: 'fâil' (ACT PCPL) · 'mef‘ûl' (PASS PCPL) · 'masdar' (VN) · '' (öteki isim ve sıfatlar)"""
    O = collections.defaultdict(dict)
    for (s_, a_, w_), segs in KELIME.items():
        for g in segs:
            if g['tur'] != 'STEM' or g['F'].get('ROOT') is None or g['F'].get('POS') not in ('N', 'ADJ'): continue
            k = bw(g['F']['ROOT'], True); lem = bw(g['F'].get('LEM', ''), False)
            if not lem: continue
            b = g['bayrak']; c = 'fâil' if ('ACT' in b and 'PCPL' in b) else ('mef‘ûl' if ('PASS' in b and 'PCPL' in b) else ('masdar' if 'VN' in b else ''))
            d = O[k].setdefault((lem, c), [0, '%d:%d' % (s_, a_)]); d[0] += 1
    return O
