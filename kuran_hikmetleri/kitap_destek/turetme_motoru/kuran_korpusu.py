import collections
import lzma
import os
import re

import istikak as I
import kaikki_suz as K

HAM = os.path.join(os.path.dirname(__file__), '..', '..', 'kaynak', 'lugat', 'ham', 'quranic_arabic_corpus_morphology_0.4.txt.xz')
KAYNAK = 'Quranic Arabic Corpus 0.4 (Kais Dukes, Leeds Üniversitesi; GNU GPL; http://corpus.quran.com)'
BW = {"'": 'ء', '|': 'آ', '>': 'أ', '&': 'ؤ', '<': 'إ', '}': 'ئ', 'A': 'ا', 'b': 'ب', 'p': 'ة', 't': 'ت', 'v': 'ث', 'j': 'ج', 'H': 'ح', 'x': 'خ', 'd': 'د', '*': 'ذ', 'r': 'ر', 'z': 'ز', 's': 'س', '$': 'ش', 'S': 'ص', 'D': 'ض', 'T': 'ط', 'Z': 'ظ', 'E': 'ع', 'g': 'غ', 'f': 'ف', 'q': 'ق', 'k': 'ك', 'l': 'ل', 'm': 'م', 'n': 'ن', 'h': 'ه', 'w': 'و', 'Y': 'ى', 'y': 'ي', 'F': 'ً', 'N': 'ٌ', 'K': 'ٍ', 'a': 'َ', 'u': 'ُ', 'i': 'ِ', '~': 'ّ', 'o': 'ْ', '`': 'ٰ', '{': 'ٱ', '^': 'ٓ', '#': 'ۜ', '@': 'ۣ', '_': 'ـ', ':': 'ۚ', '[': 'ۖ', ']': 'ۗ', '-': '', ';': '', ',': '', '.': '', 'M': 'ۢ', 'L': 'ۖ', 'O': 'ۥ', 'P': 'ۦ', 'Q': 'ۧ', 'R': 'ۨ', 'U': 'ۡ', 'V': 'ۤ', 'W': 'ۧ', 'X': 'ۜ', 'B': '', 'C': '', 'G': '', 'I': '', 'J': '', '0': '', '1': '', '2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '+': ''}
BAB = {'(II)': 'II', '(III)': 'III', '(IV)': 'IV', '(V)': 'V', '(VI)': 'VI', '(VII)': 'VII', '(VIII)': 'VIII', '(IX)': 'IX', '(X)': 'X', '(XI)': 'XI', '(XII)': 'XII'}


def arapca(b):
    return ''.join(BW.get(c, '') for c in b)


def satirlar():
    for l in lzma.open(HAM, 'rt', encoding='utf-8'):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 4 and p[0].startswith('('):
            yield p


def yukle():
    kok = {}
    for yer, bicim, etiket, ozel in satirlar():
        if 'STEM' not in ozel.split('|'):
            continue
        f = ozel.split('|')
        lem = next((x[4:] for x in f if x.startswith('LEM:')), '')
        root = next((x[5:] for x in f if x.startswith('ROOT:')), '')
        pos = next((x[4:] for x in f if x.startswith('POS:')), etiket)
        if not root:
            continue
        k = I.normala(arapca(root).replace('ا', 'ء'))
        d = kok.setdefault(k, {'kaynak': KAYNAK, 'gecis': 0, 'ilk_yer': yer.strip('()'), 'tur': collections.Counter(), 'bab': collections.Counter(), 'zaman_kip': collections.Counter(), 'fiil_ismi_ozellikleri': collections.Counter(), 'lemmalar': collections.Counter(), 'bicimler': collections.Counter()})
        d['gecis'] += 1
        d['tur'][pos] += 1
        d['lemmalar'][arapca(lem)] += 1
        d['bicimler'][arapca(bicim)] += 1
        for x in f:
            if x in BAB:
                d['bab'][BAB[x]] += 1
            elif x in ('PERF', 'IMPF', 'IMPV'):
                d['zaman_kip'][x] += 1
            elif x in ('ACT', 'PASS', 'PCPL', 'VN'):
                d['fiil_ismi_ozellikleri'][x] += 1
    return {k: {a: (dict(v.most_common()) if isinstance(v, collections.Counter) else v) for a, v in d.items()} for k, d in kok.items()}


def koksuz_lemmalar():
    c = collections.Counter()
    for yer, bicim, etiket, ozel in satirlar():
        f = ozel.split('|')
        if 'STEM' in f and not any(x.startswith('ROOT:') for x in f):
            lem = next((x[4:] for x in f if x.startswith('LEM:')), '')
            pos = next((x[4:] for x in f if x.startswith('POS:')), etiket)
            c[(arapca(lem), pos)] += 1
    return c
