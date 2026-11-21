"""Kur'ân'daki kökler ve kökü olmayan lügat başlıkları; kaynak: Quranic Arabic Corpus 0.4 (morfoloji).
kokler() -> [(ad, fl, (sûre, âyet, kelime, parça))] kararlı sırayla; fl=0 gerçek kök, fl=1 lügat başlığı."""
import re, lzma, pathlib
KH = pathlib.Path(__file__).resolve().parent.parent.parent
BW = {"'": 'ء', '|': 'آ', '>': 'أ', '&': 'ؤ', '<': 'إ', '}': 'ئ', 'A': 'ا', 'b': 'ب', 'p': 'ة', 't': 'ت', 'v': 'ث', 'j': 'ج', 'H': 'ح', 'x': 'خ', 'd': 'د', '*': 'ذ', 'r': 'ر', 'z': 'ز', 's': 'س', '$': 'ش', 'S': 'ص', 'D': 'ض', 'T': 'ط', 'Z': 'ظ', 'E': 'ع', 'g': 'غ', 'f': 'ف', 'q': 'ق', 'k': 'ك', 'l': 'ل', 'm': 'م', 'n': 'ن', 'h': 'ه', 'w': 'و', 'Y': 'ى', 'y': 'ي', '`': 'ٰ', '{': 'ٱ'}
def bw(s, kok):
    o = ''
    for c in s:
        if kok: o += 'ء' if c in "A'><&}|" else BW.get(c, '')
        else: o += BW.get(c, '')
    return o
def norm_ar(s):
    s = re.sub('[ؐ-ًؚ-ٰٟۖ-ۭـ]', '', s)
    return s.replace('ٱ', 'ا').replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ؤ', 'ء').replace('ئ', 'ء')
def lugat_basligi(s): return norm_ar(bw(s, False))
def ilkler():
    O = {}
    with lzma.open(KH / 'kaynak' / 'lugat' / 'ham' / 'quranic_arabic_corpus_morphology_0.4.txt.xz', 'rt', encoding='utf-8') as f_:
        for ln in f_:
            if not ln.startswith('('): continue
            loc, form, tag, ft = ln.rstrip('\n').split('\t')
            if not ft.startswith('STEM'): continue
            s_, a_, w_, m_ = (int(v) for v in loc.strip('()').split(':'))
            F = {x.split(':')[0]: x.split(':', 1)[1] for x in ft.split('|') if ':' in x}
            if 'ROOT' in F: k, fl = bw(F['ROOT'], True), 0
            else: k, fl = lugat_basligi(F.get('LEM') or form), 1
            if k and (k, fl) not in O: O[(k, fl)] = (s_, a_, w_, m_)
    return O
def kokler(): return sorted(((k, fl, y) for (k, fl), y in ilkler().items()), key=lambda t: (t[1], t[0]))

def tum():
    """Bütün âyetler: AYK['s:a'] = [[kök, fl, yeni(0/1)], ...] tekil, kelime sırasıyla; KEL['s:a'] = {kelime_no: [(kök, fl), ...]}; SAY[(kök, fl)] = [âyet sayısı, geçiş]; ILK[(kök, fl)] = 's:a'."""
    AYK = {}; KEL = {}; SAY = {}; ILK = {}; gor = set(); son = {}
    with lzma.open(KH / 'kaynak' / 'lugat' / 'ham' / 'quranic_arabic_corpus_morphology_0.4.txt.xz', 'rt', encoding='utf-8') as f_:
        for ln in f_:
            if not ln.startswith('('): continue
            loc, form, tag, ft = ln.rstrip('\n').split('\t')
            if not ft.startswith('STEM'): continue
            s_, a_, w_, m_ = (int(v) for v in loc.strip('()').split(':'))
            F = {x.split(':')[0]: x.split(':', 1)[1] for x in ft.split('|') if ':' in x}
            if 'ROOT' in F: k, fl = bw(F['ROOT'], True), 0
            else: k, fl = lugat_basligi(F.get('LEM') or form), 1
            if not k: continue
            key = '%d:%d' % (s_, a_)
            L = AYK.setdefault(key, [])
            yeni = 0
            if (k, fl) not in gor: gor.add((k, fl)); ILK[(k, fl)] = key; yeni = 1
            if not any(x[0] == k and x[1] == fl for x in L): L.append([k, fl, yeni])
            KEL.setdefault(key, {}).setdefault(w_, []).append((k, fl))
            c = SAY.setdefault((k, fl), [0, 0]); c[1] += 1
            if son.get((k, fl)) != key: son[(k, fl)] = key; c[0] += 1
    return AYK, KEL, SAY, ILK
