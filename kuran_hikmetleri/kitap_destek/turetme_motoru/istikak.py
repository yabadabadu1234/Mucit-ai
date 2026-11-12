import sys

HARF = {'ا': 'ā', 'ب': 'b', 'ت': 't', 'ث': 'ṯ', 'ج': 'c', 'ح': 'ḥ', 'خ': 'ḫ', 'د': 'd', 'ذ': 'ẕ',
        'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'ş', 'ص': 'ṣ', 'ض': 'ḍ', 'ط': 'ṭ', 'ظ': 'ẓ', 'ع': 'ʿ',
        'غ': 'ğ', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'w',
        'ي': 'y', 'ء': 'ʾ', 'أ': 'ʾ', 'إ': 'ʾ', 'ؤ': 'ʾ', 'ئ': 'ʾ', 'ى': 'ā'}
NORM = {'أ': 'ء', 'إ': 'ء', 'آ': 'ء', 'ؤ': 'ء', 'ئ': 'ء'}
LIT = {'X': 'ت', 'm': 'م', 't': 'ت', 'n': 'ن', 's': 'س', 'y': 'ي', 'w': 'و', 'A': 'ا', 'U': 'و', 'I': 'ي',
       'Y': 'ى', 'T': 'ة', 'E': 'أ', 'W': 'ا', 'Q': 'ء'}
HAR = {'a': 'َ', 'i': 'ِ', 'u': 'ُ', '0': 'ْ'}
SHD = 'ّ'
MADD = {'A': 'ā', 'U': 'ū', 'I': 'ī', 'Y': 'ā'}
RANK = {'i': 3, 'u': 2, 'a': 1}


def tok(code, v='', sh=False):
    return {'c': code, 'v': v, 'sh': sh}


def parse(spec):
    r = []
    for t in spec.split():
        rest = t[1:]
        sh = '+' in rest
        v = rest.replace('+', '')
        r.append(tok(t[0], v, sh))
    return r


def kopya(ts):
    return [dict(t) for t in ts]


def normala(k):
    return ''.join(NORM.get(h, h) for h in k)


def kok_sinifi(k):
    if len(k) != 3:
        return None, 'üç harfli değil'
    if any(h in 'اى' for h in k):
        return None, 'kök harfi elif veya elif-i maksûre'
    z = [h in 'وي' for h in k]
    n = sum(z)
    if n == 0:
        if k[1] == k[2]:
            return 'muzâ‘af', ''
        return ('mehmûz' if 'ء' in k else 'sâlim'), ''
    if n == 1:
        if z[0]:
            return 'misâl', ''
        if z[1]:
            if k[2] == 'ء':
                return 'ecvef+mehmûz-lâm (birleşik)', ''
            return 'ecvef', ''
        return 'nâkıs', ''
    if n == 2:
        if z[0] and z[2]:
            return 'lefîf-mefrûk', ''
        if z[1] and z[2]:
            if k[1] == k[2]:
                return 'lefîf-makrûn (ayn ve lâm aynı harf)', ''
            return 'lefîf-makrûn', ''
        return 'misâl+ecvef (birleşik)', ''
    return 'üç harfi illetli (birleşik)', ''


ECVEF = {
    "1a A 2i 3": "1a A Qi 3",
    "ma 10 2u U 3": "ma 1V M 3",
    "ma 10 2a 3": "ma 1a A 3",
    "ma 10 2i 3": "ma 1i I 3",
    "ma 10 2a 3a T": "ma 1a A 3a T",
    "ma 10 2i 3a T": "ma 1i I 3a T",
    "1i 20 3": "1i I 3",
    "1u 20 3": "1u U 3",
    "1a 2a 3": "1a A 3",
    "1i 2a A 3": "1i ya A 3",
    "1i 2a A 3a T": "1i ya A 3a T",
    "1i 2a 3": "1i ya 3",
    "1i 20 3a T": "1i I 3a T",
    "Ei 10 2a A 3": "Ei 1a A 3a T",
    "mu 10 2i 3": "mu 1i I 3",
    "mu 10 2a 3": "mu 1a A 3",
    "Wi n0 1i 2a A 3": "Wi n0 1i ya A 3",
    "mu n0 1a 2i 3": "mu n0 1a A 3",
    "Wi 10 Xi 2a A 3": "Wi 10 Xi ya A 3",
    "mu 10 Xa 2i 3": "mu 10 Xa A 3",
    "mu 10 Xa 2a 3": "mu 10 Xa A 3",
    "Wi s0 ti 10 2a A 3": "Wi s0 ti 1a A 3a T",
    "mu s0 ta 10 2i 3": "mu s0 ta 1i I 3",
    "mu s0 ta 10 2a 3": "mu s0 ta 1a A 3",
}

NAKIS = {
    "1a A 2i 3": "1a A 2i I",
    "ma 10 2u U 3": {'w': "ma 10 2u w+", 'y': "ma 10 2i y+"},
    "ma 10 2a 3": "ma 10 2a Y",
    "ma 10 2i 3": "ma 10 2i I",
    "ma 10 2a 3a T": "ma 10 2a A T",
    "ma 10 2i 3a T": "ma 10 2i ya T",
    "mi 10 2a 3": "mi 10 2a Y",
    "mi 10 2a A 3": "mi 10 2a A Q",
    "mi 10 2a 3a T": "mi 10 2a A T",
    "Ea 10 2a 3": "Ea 10 2a Y",
    "1u 20 3a Y": "1u 20 ya Y",
    "1a 2a 3": {'w': "1a 2a A", 'y': "1a 2a Y"},
    "1i 2a 3": "1i 2a Y",
    "1u 2a 3": "1u 2a Y",
    "1u 2u U 3": {'w': "1u 2u w+", 'y': "1u 2i y+"},
    "1u 2u 3": {'w': "1u 2u w+", 'y': "1u 2i y+"},
    "1i 2a A 3": "1i 2a A Q",
    "1u 2a A 3": "1u 2a A Q",
    "1a 2a A 3": "1a 2a A Q",
    "1i 2a A 3a T": "1i 2a A ya T",
    "1a 2a A 3a T": "1a 2a A T",
    "1u 2u U 3a T": {'w': "1u 2u w+a T", 'y': "1u 2i y+a T"},
    "1a 2i I 3": "1a 2i y+",
    "1a 2u U 3": "1a 2u w+",
    "1a 2i 3": "1a 2i I",
    "1a 2u 3": "1a 2u w+",
    "1a 2+a A 3": "1a 2+a A Q",
    "1a 2+a A 3a T": "1a 2+a A ya T",
    "1u 2a y0 3": "1u 2a y+",
    "1u 2a y0 3a T": "1u 2a y+a T",
    "1a 2a 3a T": "1a 2a A T",
    "1i 2a 3a T": "1i 2a ya T",
    "ta 10 2i I 3": "ta 10 2i ya T",
    "ta 10 2i 3a T": "ta 10 2i ya T",
    "1i 2+i A 3": "1i 2+i A Q",
    "mu 1a 2+i 3": "mu 1a 2+i I",
    "mu 1a 2+a 3": "mu 1a 2+a Y",
    "mu 1a A 2a 3a T": "mu 1a A 2a A T",
    "mu 1a A 2i 3": "mu 1a A 2i I",
    "mu 1a A 2a 3": "mu 1a A 2a Y",
    "Ei 10 2a A 3": "Ei 10 2a A Q",
    "mu 10 2i 3": "mu 10 2i I",
    "mu 10 2a 3": "mu 10 2a Y",
    "ta 1a 2+u 3": "ta 1a 2+i I",
    "mu ta 1a 2+i 3": "mu ta 1a 2+i I",
    "mu ta 1a 2+a 3": "mu ta 1a 2+a Y",
    "ta 1a A 2u 3": "ta 1a A 2i I",
    "mu ta 1a A 2i 3": "mu ta 1a A 2i I",
    "mu ta 1a A 2a 3": "mu ta 1a A 2a Y",
    "Wi n0 1i 2a A 3": "Wi n0 1i 2a A Q",
    "mu n0 1a 2i 3": "mu n0 1a 2i I",
    "Wi 10 Xi 2a A 3": "Wi 10 Xi 2a A Q",
    "mu 10 Xa 2i 3": "mu 10 Xa 2i I",
    "mu 10 Xa 2a 3": "mu 10 Xa 2a Y",
    "Wi s0 ti 10 2a A 3": "Wi s0 ti 10 2a A Q",
    "mu s0 ta 10 2i 3": "mu s0 ta 10 2i I",
    "mu s0 ta 10 2a 3": "mu s0 ta 10 2a Y",
    "Ea 10 2a A 3": "Ea 10 2a A Q",
    "Ea 10 2i 3a T": "Ea 10 2i ya T",
    "Ea 1a A 2i 3": "Ea 1a A 2i I",
    "Ea 1a A 2i I 3": "Ea 1a A 2i y+",
    "1u 2+a A 3": "1u 2+a A Q",
    "ma 1a A 2i 3": "ma 1a A 2i I",
    "ma 1a A 2i I 3": "ma 1a A 2i y+",
    "1a wa A 2i 3": "1a wa A 2i I",
    "1u 2a 3 A Q": None,
    "1a 2a A Qi 3": None,
}

NAKIS_AGIR = {
    "Wi 10 2i 3a A 3": "Wi 10 2i 3a A Q",
    "mu 10 2a 3+": "mu 10 2a 3i I",
    "Wi 10 2i I 3a A 3": "Wi 10 2i I 3a A Q",
    "mu 10 2a A 3+": "mu 10 2a A 3i I",
    "Wi 10 2i w0 2a A 3": "Wi 10 2i w0 2a A Q",
    "Wi 10 2i w+a A 3": "Wi 10 2i w+a A Q",
}

SKIP = object()


def ozel_spec(spec, kok, bay):
    if bay['nakis']:
        if spec in NAKIS:
            o = NAKIS[spec]
            if o is None:
                return SKIP
            if isinstance(o, dict):
                o = o['w'] if kok[2] == 'و' else o['y']
            return o
        return spec
    if bay['ecvef']:
        o = ECVEF.get(spec)
        if o is None:
            return spec
        w = kok[1]
        return o.replace('1V', '1' + ('u' if w == 'و' else 'i')).replace(' M ', ' ' + ('U' if w == 'و' else 'I') + ' ')
    return spec


def harfle(ts, kok, var=None):
    out = []
    for t in ts:
        c = t['c']
        ch = kok[int(c) - 1] if c in '1234' else LIT[c]
        out.append({'ch': ch, 'v': t['v'], 'sh': t['sh'], 'c': c, 'slot': c if c in '1234' else None})
    f = kok[0]
    for i, x in enumerate(out):
        if x['c'] == 'X':
            asim = f in 'دذوينطظ' or (f == 'ء' and var == 'asim')
            if f == 'ز':
                x['ch'] = 'د'
            elif f in 'صض':
                x['ch'] = 'ط'
            if asim:
                x['ch'] = 'د' if f in 'دذ' else ('ط' if f == 'ط' else ('ظ' if f == 'ظ' else 'ت'))
                x['sh'] = True
                if out[i - 1]['slot'] == '1':
                    out.pop(i - 1)
            break
    return out


def misal_gecisi(L):
    for i, x in enumerate(L):
        if i and x['slot'] == '1' and x['v'] == '0' and x['ch'] in 'وي' and L[i - 1]['v'] in ('i', 'u'):
            if L[i - 1]['v'] == 'i':
                x['ch'], x['c'] = 'ي', 'I'
            else:
                x['ch'], x['c'] = 'و', 'U'
            x['v'] = ''
            x['slot'] = None
    return L


def mak_secimi(L, i):
    x = L[i]
    o = x['v']
    if i == 0:
        return 'إ' if o == 'i' else 'أ'
    p = L[i - 1]
    pc, pv = p['c'], p['v']
    if pc == 'A':
        return {'a': 'ء', 'i': 'ئ', 'u': 'ؤ'}.get(o, 'ء')
    if pc == 'U' or pc == 'Y':
        return 'ء'
    if pc == 'I':
        return 'ئ' if o in RANK else 'ء'
    if pv in ('0', ''):
        return {'a': 'أ', 'i': 'ئ', 'u': 'ؤ'}.get(o, 'ء')
    s = max([o if o in RANK else '', pv], key=lambda v: RANK.get(v, 0))
    return {'i': 'ئ', 'u': 'ؤ', 'a': 'أ'}[s]


def hemze_gecisi(L):
    out = []
    i = 0
    while i < len(L):
        x = L[i]
        if x['c'] == 'E' and i + 1 < len(L) and L[i + 1]['ch'] == 'ء' and L[i + 1]['v'] == '0' \
                and L[i + 1]['slot'] == '1':
            if x['v'] == 'a':
                ar, lat = 'آ', 'ʾā'
            elif x['v'] == 'i':
                ar, lat = 'إِي', 'ʾī'
            else:
                ar, lat = 'أُو', 'ʾū'
            out.append({'ch': ar, 'v': '', 'sh': False, 'c': 'H', 'slot': None, 'ar': ar, 'lat': lat})
            i += 2
            continue
        if x['ch'] == 'ء' and x['c'] in '1234Q':
            ilk = i == 0 or (out and out[-1]['v'] in ('a', '0', '') and out[-1]['c'] not in ('U', 'I'))
            if ilk and x['v'] == 'a' and i + 1 < len(L) and L[i + 1]['c'] == 'A':
                out.append({'ch': 'آ', 'v': '', 'sh': False, 'c': 'H', 'slot': None, 'ar': 'آ', 'lat': 'ʾā'})
                i += 2
                continue
            y = dict(x)
            y['ch'] = mak_secimi(out + [y], len(out))
            out.append(y)
            i += 1
            continue
        out.append(x)
        i += 1
    return out


def cift_hemze(L):
    for i in range(len(L) - 1):
        if L[i]['ch'] in 'ءأإؤئ' and L[i + 1]['ch'] in 'ءأإؤئ' and L[i]['slot'] != '1' and L[i + 1]['slot'] == '3' \
                and L[i + 1]['v'] == '':
            L[i]['ch'] = 'ء'
            del L[i + 1]
            break
    return L


def idgham(L):
    n = 0
    i = 0
    r = []
    while i < len(L):
        a = L[i]
        if (i + 1 < len(L) and a['slot'] == '2' and L[i + 1]['slot'] == '3' and a['ch'] == L[i + 1]['ch']
                and not a['sh'] and not L[i + 1]['sh']):
            b = dict(L[i + 1])
            b['sh'] = True
            if r and r[-1]['v'] == '0' and a['v'] in ('a', 'i', 'u'):
                r[-1] = dict(r[-1])
                r[-1]['v'] = a['v']
            r.append(b)
            i += 2
            n += 1
            continue
        r.append(a)
        i += 1
    return r, n


def arapca(L):
    s = ''
    for x in L:
        if 'ar' in x:
            s += x['ar']
            continue
        ch = x['ch']
        if x['c'] == 'E' and x['v'] == 'i':
            ch = 'إ'
        s += ch
        if x['sh']:
            s += SHD
        if x['v'] in HAR and x['c'] not in MADD:
            s += HAR[x['v']]
    return s


def latin(L):
    s = ''
    for i, x in enumerate(L):
        if 'lat' in x:
            s += x['lat']
            continue
        c = x['c']
        if c in MADD:
            s += MADD[c]
            continue
        if c == 'T':
            continue
        ch = '' if c == 'W' else HARF.get(x['ch'], x['ch'])
        s += ch * (2 if x['sh'] else 1)
        nxt = L[i + 1]['c'] if i + 1 < len(L) else ''
        if x['v'] in ('a', 'i', 'u') and nxt not in MADD:
            s += x['v']
    return s


def uret(ts, kok, var=None):
    L = harfle(ts, kok, var)
    L = misal_gecisi(L)
    L = hemze_gecisi(L)
    L = cift_hemze(L)
    if var == 'izhar':
        n = 0
    else:
        L, n = idgham(L)
    return arapca(L), latin(L), n


def mensub(ts):
    t = kopya(ts)
    if t[-1]['c'] == 'T':
        t.pop()
    c = t[-1]['c']
    if c == 'I':
        t[-1] = tok('y', '', True)
    elif c == 'Y':
        t.pop()
        t += [tok('w', 'i'), tok('y', '', True)]
    elif c in MADD:
        return None
    else:
        t[-1]['v'] = 'i'
        t.append(tok('y', '', True))
    return t


def sinai(ts):
    t = kopya(ts)
    if t[-1]['c'] == 'T':
        t.pop()
    c = t[-1]['c']
    if c == 'I':
        t[-1] = tok('y', 'a', True)
    elif c == 'Y':
        t.pop()
        t += [tok('w', 'i'), tok('y', 'a', True)]
    elif c in MADD:
        return None
    else:
        t[-1]['v'] = 'i'
        t.append(tok('y', 'a', True))
    t.append(tok('T'))
    return t


def tesniye(ts):
    t = kopya(ts)
    c = t[-1]['c']
    if c == 'T':
        t[-1] = tok('t', 'a')
    elif c in ('Y', 'I'):
        t[-1] = tok('y', 'a')
    elif c == 'A':
        t[-1] = tok('w', 'a')
    elif c in MADD:
        return None
    else:
        t[-1]['v'] = 'a'
    t += [tok('A'), tok('n')]
    return t


def salim_muz(ts, hal):
    t = kopya(ts)
    c = t[-1]['c']
    if c == 'T' or c == 'A' or c == 'U':
        return None
    if c == 'I':
        t.pop()
        t[-1]['v'] = 'u' if hal == 'u' else 'i'
    elif c == 'Y':
        t.pop()
        t[-1]['v'] = 'a'
        t.append(tok('w', '0') if hal == 'u' else tok('y', '0'))
        t.append(tok('n'))
        return t
    else:
        t[-1]['v'] = 'u' if hal == 'u' else 'i'
    t += [tok('U' if hal == 'u' else 'I'), tok('n')]
    return t


def salim_muen(ts):
    t = kopya(ts)
    c = t[-1]['c']
    if c == 'T':
        t.pop()
        t[-1]['v'] = 'a'
    elif c in ('I', 'Y'):
        t[-1] = tok('y', 'a')
    elif c == 'A':
        t[-1] = tok('w', 'a')
    elif c in MADD:
        return None
    else:
        t[-1]['v'] = 'a'
    t += [tok('A'), tok('t')]
    return t


def muennes(ts):
    t = kopya(ts)
    c = t[-1]['c']
    if c == 'I':
        t[-1] = tok('y', 'a')
    elif c in MADD or c == 'T':
        return None
    else:
        t[-1]['v'] = 'a'
    t.append(tok('T'))
    return t


def merre(ts):
    t = kopya(ts)
    if t[-1]['c'] in ('T', 'Y', 'U', 'I'):
        return None
    if t[-1]['c'] != 'A':
        t[-1]['v'] = 'a'
    t.append(tok('T'))
    return t


MASDAR_SULASI = [
    ("fa'l", "1a 20 3"), ("fi'l", "1i 20 3"), ("fu'l", "1u 20 3"),
    ("fa'al", "1a 2a 3"), ("fi'al", "1i 2a 3"), ("fu'ul", "1u 2u 3"),
    ("fu'ūl", "1u 2u U 3"), ("fi'āl", "1i 2a A 3"), ("fu'āl", "1u 2a A 3"),
    ("fa'āl", "1a 2a A 3"), ("fa'āle", "1a 2a A 3a T"), ("fu'ūle", "1u 2u U 3a T"),
    ("fi'āle", "1i 2a A 3a T"), ("fa'īl", "1a 2i I 3"), ("fa'ūl", "1a 2u U 3"),
    ("fa'alān", "1a 2a 3a A n"), ("fu'lān", "1u 20 3a A n"), ("fi'lān", "1i 20 3a A n"),
    ("fa'lā", "1a 20 3a Y"), ("fu'lā", "1u 20 3a Y"), ("fi'lā", "1i 20 3a Y"),
    ("fa'ale", "1a 2a 3a T"), ("fi'ale", "1i 2a 3a T"),
]
SIFAT_MUSEBBEHE = [
    ("fa'īl", "1a 2i I 3"), ("fa'ūl", "1a 2u U 3"), ("fa'il", "1a 2i 3"), ("fa'ul", "1a 2u 3"),
    ("fa'al", "1a 2a 3"), ("fa'l", "1a 20 3"), ("fu'ul", "1u 2u 3"), ("fa'lān", "1a 20 3a A n"),
    ("fu'āl", "1u 2a A 3"), ("fa'āl", "1a 2a A 3"),
]
MUBALAGA = [
    ("fa''āl", "1a 2+a A 3"), ("fa''āle", "1a 2+a A 3a T"), ("fa'ūl", "1a 2u U 3"),
    ("fa''ūl", "1a 2+u U 3"), ("fi''īl", "1i 2+i I 3"), ("fu''āl", "1u 2+a A 3"),
    ("mif'āl", "mi 10 2a A 3"), ("mif'īl", "mi 10 2i I 3"), ("fa'īl", "1a 2i I 3"), ("fa''al", "1a 2+a 3"),
]
CEMI_MUKESSER = [
    ("ef'āl", "Ea 10 2a A 3"), ("ef'ile", "Ea 10 2i 3a T"), ("efâ'il", "Ea 1a A 2i 3"),
    ("efâ'îl", "Ea 1a A 2i I 3"), ("fu'ūl", "1u 2u U 3"), ("fu'ul", "1u 2u 3"), ("fi'āl", "1i 2a A 3"),
    ("fi'al", "1i 2a 3"), ("fi'ale", "1i 2a 3a T"), ("fu'al", "1u 2a 3"), ("fu'alā'", "1u 2a 3 A Q"),
    ("fa'ale", "1a 2a 3a T"), ("fu''āl", "1u 2+a A 3"), ("fa'āl", "1a 2a A 3"), ("fa'al", "1a 2a 3"),
    ("mefâ'il", "ma 1a A 2i 3"), ("mefâ'îl", "ma 1a A 2i I 3"), ("fevâ'il", "1a wa A 2i 3"),
    ("fe'âil", "1a 2a A Qi 3"), ("fu'ayl(cem')", "1u 2a y0 3"),
]

ISM_MASDAR = [("fa'âl (kelâm, selâm)", "1a 2a A 3"), ("fu'ûl (vudû')", "1u 2u U 3"), ("fi'âl", "1i 2a A 3"),
              ("fu'l (şükr)", "1u 20 3"), ("fa'âle (belâğa)", "1a 2a A 3a T"), ("fi'âle", "1i 2a A 3a T"),
              ("fu'ûle", "1u 2u U 3a T"), ("fa'l", "1a 20 3"), ("fi'l", "1i 20 3")]
ISM_CINS = [("fa'l", "1a 20 3"), ("fa'al", "1a 2a 3"), ("fi'l", "1i 20 3"), ("fu'l", "1u 20 3"),
            ("fa'îl", "1a 2i I 3"), ("fi'al", "1i 2a 3"), ("fu'ul", "1u 2u 3"), ("fa'âl", "1a 2a A 3")]

BAB = [
    ('II', "tef'îl", [("taf'īl", "ta 10 2i I 3"), ("taf'ila", "ta 10 2i 3a T"), ("fi''āl", "1i 2+i A 3")],
     ("mufa''il", "mu 1a 2+i 3"), ("mufa''al", "mu 1a 2+a 3")),
    ('III', "mufâ'ale", [("mufā'ale", "mu 1a A 2a 3a T"), ("fi'āl", "1i 2a A 3")],
     ("mufā'il", "mu 1a A 2i 3"), ("mufā'al", "mu 1a A 2a 3")),
    ('IV', "if'âl", [("if'āl", "Ei 10 2a A 3")],
     ("muf'il", "mu 10 2i 3"), ("muf'al", "mu 10 2a 3")),
    ('V', "tefe''ul", [("tafa''ul", "ta 1a 2+u 3")],
     ("mutafa''il", "mu ta 1a 2+i 3"), ("mutafa''al", "mu ta 1a 2+a 3")),
    ('VI', "tefâ'ul", [("tafā'ul", "ta 1a A 2u 3")],
     ("mutafā'il", "mu ta 1a A 2i 3"), ("mutafā'al", "mu ta 1a A 2a 3")),
    ('VII', "infi'âl (mutâvaa, lâzım)", [("infi'āl", "Wi n0 1i 2a A 3")],
     ("munfa'il", "mu n0 1a 2i 3"), None),
    ('VIII', "ifti'âl", [("ifti'āl", "Wi 10 Xi 2a A 3")],
     ("muftaʿil", "mu 10 Xa 2i 3"), ("muftaʿal", "mu 10 Xa 2a 3")),
    ('IX', "if'ilâl (renk/ayıp, lâzım)", [("if'ilāl", "Wi 10 2i 3a A 3")],
     ("muf'all", "mu 10 2a 3+"), None),
    ('X', "istif'âl", [("istif'āl", "Wi s0 ti 10 2a A 3")],
     ("mustaf'il", "mu s0 ta 10 2i 3"), ("mustaf'al", "mu s0 ta 10 2a 3")),
    ('XI', "if'îlâl (lâzım)", [("if'īlāl", "Wi 10 2i I 3a A 3")], ("muf'āll", "mu 10 2a A 3+"), None),
    ('XII', "if'iv'âl (lâzım)", [("if'iv'āl", "Wi 10 2i w0 2a A 3")], None, None),
    ('XIII', "if'ivvâl (lâzım)", [("if'ivvāl", "Wi 10 2i w+a A 3")], None, None),
]
BAB_RUBAI = [
    ('Rubâ‘î mücerred', "fa'lale", [("fa'lale", "1a 20 3a 4a T"), ("fi'lāl", "1i 20 3a A 4")],
     ("mufa'lil", "mu 1a 20 3i 4"), ("mufa'lal", "mu 1a 20 3a 4")),
    ('Rubâ‘î mutâvaa', "tefa'lul", [("tafa'lul", "ta 1a 20 3u 4")],
     ("mutafa'lil", "mu ta 1a 20 3i 4"), ("mutafa'lal", "mu ta 1a 20 3a 4")),
    ('Rubâ‘î mezîd', "if'inlâl", [("if'inlāl", "Wi 10 2i n0 3a A 4")],
     ("mufanlil", "mu 10 2a n0 3i 4"), ("mufanlal", "mu 10 2a n0 3a 4")),
]
SULASI_MUSTAK = [
    ('ism-i fâil', "fâ'il", "1a A 2i 3", 'fi'),
    ('ism-i mef‘ûl', "maf'ûl", "ma 10 2u U 3", 'mef'),
    ('mekân/zaman', "maf'al", "ma 10 2a 3", None),
    ('mekân/zaman', "maf'il", "ma 10 2i 3", None),
    ('mekân/zaman', "maf'ale", "ma 10 2a 3a T", None),
    ('mekân/zaman', "maf'ile", "ma 10 2i 3a T", None),
    ('âlet', "mif'al", "mi 10 2a 3", None),
    ('âlet', "mif'âl", "mi 10 2a A 3", None),
    ('âlet', "mif'ale", "mi 10 2a 3a T", None),
    ('tafdîl', "af'al", "Ea 10 2a 3", None),
    ('tafdîl (müennes)', "fu'lâ", "1u 20 3a Y", None),
    ('tasğîr', "fu'ayl", "1u 2a y0 3", None),
    ('tasğîr', "fu'ayle", "1u 2a y0 3a T", None),
    ('masdar-ı mîmî', "maf'al", "ma 10 2a 3", None),
    ('ism-i merre', "fa'le", "1a 20 3a T", None),
    ('ism-i hey\'et', "fi'le", "1i 20 3a T", None),
]


def tablo(kok):
    kok = normala(kok)
    sinif, sebep = kok_sinifi(kok)
    satir, red = [], []
    if sinif is None:
        return 'reddedildi', [], [('kök', kok, sebep)]
    bay = {'nakis': kok[2] in 'وي', 'ecvef': kok[1] in 'وي' and kok[2] not in 'وي', 'misal': kok[0] in 'وي'}
    mudaaf = sinif == 'muzâ‘af'
    sagl = sinif in ('sâlim', 'mehmûz', 'muzâ‘af')

    raw = [False]

    def P(spec):
        if raw[0]:
            if bay['nakis'] and spec in NAKIS_AGIR:
                return parse(NAKIS_AGIR[spec]), True
            return parse(spec), False
        s = ozel_spec(spec, kok, bay)
        if s is SKIP:
            return None
        return parse(s), (s != spec)

    def ekle(grup, ad, ts, kok_, etiket='', bab='', var=None, ilal=False):
        if ts is None:
            red.append((grup, ad, 'bu kök sınıfında bu kalıp yok veya sondaki harf bu eki almaz'))
            return
        a, l, n = uret(ts, kok_, var)
        satir.append({'grup': grup, 'ad': ad, 'ar': a, 'lat': l, 'idg': n,
                      'etiket': etiket + (' · ilal' if ilal else ''), 'bab': bab})

    def turevler(grup, ad, spec, gender, etiket='', bab='', var=None):
        p = P(spec)
        if p is None:
            red.append((grup, ad, 'bu kök sınıfında bu kalıp yok'))
            return
        ts, il = p
        ekle(grup, ad, ts, kok, etiket, bab, var, il)
        if gender:
            ekle(grup, ad + ' + müennes', muennes(ts), kok, etiket, bab, var, il)
        ekle(grup, ad + ' + tesniye', tesniye(ts), kok, etiket, bab, var, il)
        if gender:
            m = muennes(ts)
            if m:
                ekle(grup, ad + ' + müennes tesniye', tesniye(m), kok, etiket, bab, var, il)
            ekle(grup, ad + ' + cem‘-i sâlim müzekker (-ûn)', salim_muz(ts, 'u'), kok, etiket, bab, var, il)
            ekle(grup, ad + ' + cem‘-i sâlim müzekker (-în)', salim_muz(ts, 'i'), kok, etiket, bab, var, il)
            ekle(grup, ad + ' + cem‘-i sâlim müennes (-ât)', salim_muen(ts), kok, etiket, bab, var, il)

    def tek(grup, ad, spec, etiket='', bab='', var=None):
        p = P(spec)
        if p is None:
            red.append((grup, ad, 'bu kök sınıfında bu kalıp yok'))
            return
        ekle(grup, ad, p[0], kok, etiket, bab, var, p[1])

    for ad, sp in MASDAR_SULASI:
        tek('masdar · sülâsî mücerred', ad, sp, 'semâî aday')
    if kok[0] == 'و' and not bay['nakis']:
        tek('masdar · sülâsî mücerred', "fi'a (fâ hazfi: ‘ide, sıle)", "2i 3a T", 'semâî aday')
    for rom, ad, masdarlar, fail, mef in BAB:
        agir = rom in ('IX', 'XI', 'XII', 'XIII')
        raw[0] = False
        izh = None
        if agir:
            if not (sagl and not mudaaf):
                raw[0] = True
                izh = 'izhar'
        for mad_ad, sp in masdarlar:
            tek('masdar · bâb ' + rom + (' (illet harfi izhar)' if izh else ''), mad_ad, sp, 'semâî aday' if izh else 'kıyâsî', rom, izh)
            if rom == 'VIII' and kok[0] == 'ء':
                tek('masdar · bâb VIII (hemze idgamlı)', mad_ad, sp, 'kıyâsî', rom, 'asim')
        for mad_ad, sp in masdarlar:
            if not sp.endswith(' T') and not agir:
                p = P(sp)
                if p is None:
                    continue
                ekle('ism-i merre · bâb ' + rom, mad_ad + ' + tâ', merre(p[0]), kok, 'aday', rom, None, p[1])
        for var in (izh, 'asim'):
            if var == 'asim' and not (rom == 'VIII' and kok[0] == 'ء'):
                continue
            suf = ' (hemze idgamlı)' if var == 'asim' else (' (illet harfi izhar)' if var else '')
            if fail:
                turevler('ism-i fâil · bâb ' + rom + suf, fail[0], fail[1], True, 'kıyâsî', rom, var)
            if mef:
                turevler('ism-i mef‘ûl · bâb ' + rom + suf, mef[0], mef[1], True, 'kıyâsî', rom, var)
                tek('mekân/zaman/masdar-ı mîmî · bâb ' + rom + suf, mef[0], mef[1], 'kıyâsî', rom, var)
        if rom == 'X' and bay['ecvef'] and kok[1] == 'و':
            ekle('masdar · bâb X (vâvı muhafaza: semâî istisnâ)', "istif'āl", parse("Wi s0 ti 10 2a A 3"), kok, 'semâî aday', rom)
            ekle('ism-i fâil · bâb X (vâvı muhafaza: semâî istisnâ)', "mustaf'il", parse("mu s0 ta 10 2i 3"), kok, 'semâî aday', rom)
            ekle('ism-i mef‘ûl · bâb X (vâvı muhafaza: semâî istisnâ)', "mustaf'al", parse("mu s0 ta 10 2a 3"), kok, 'semâî aday', rom)
        raw[0] = False
        if mef is None:
            red.append(('ism-i mef‘ûl · bâb ' + rom, ad, 'YOK (lâzım fiil; kitapta mef‘ûl işaretli değil)'))
    if mudaaf:
        kok4 = kok[0] + kok[1] + kok[0] + kok[1]
        for grp, ad, masdarlar, fail, mef in BAB_RUBAI:
            for mad_ad, sp in masdarlar:
                ekle('masdar · ' + grp, mad_ad, parse(sp), kok4, 'kıyâsî (kök ikilendi)')
            ekle('ism-i fâil · ' + grp, fail[0], parse(fail[1]), kok4, 'kıyâsî')
            ekle('ism-i mef‘ûl · ' + grp, mef[0], parse(mef[1]), kok4, 'kıyâsî')
    else:
        red.append(('rubâ‘î', 'dört harfli bâblar', 'muzâ‘af olmayan üç harfli kökte kök ikilenmez; rubâ‘î kök ayrı bir köktür'))
    for grp, ad, sp, g in SULASI_MUSTAK:
        if grp in ('ism-i fâil', 'ism-i mef‘ûl'):
            turevler(grp + ' · sülâsî', ad, sp, True, 'kıyâsî')
        elif grp.startswith(('tafdîl', 'tasğîr', 'âlet', 'mekân')):
            turevler(grp + ' · sülâsî', ad, sp, False, 'kıyâsî')
        else:
            turevler(grp + ' · sülâsî', ad, sp, False, 'kıyâsî' if grp.startswith('masdar') else 'aday')
    for ad, sp in SIFAT_MUSEBBEHE:
        turevler('sıfat-ı müşebbehe', ad, sp, True, 'semâî aday')
    if bay['ecvef']:
        turevler('sıfat-ı müşebbehe', "fay'il (ecvef: seyyid, meyyit, tayyib)", "1a y+i 3", True, 'ecvef kıyâsı')
    for ad, sp in MUBALAGA:
        turevler('mübalağa', ad, sp, True, 'semâî aday')
    for ad, sp in (("fa'l", "1a 20 3"), ("fâ'il", "1a A 2i 3"), ("maf'ûl", "ma 10 2u U 3"), ("fa'īl", "1a 2i I 3")):
        p = P(sp)
        if p is None:
            continue
        ekle('mensûb', ad + ' + iyy', mensub(p[0]), kok, 'kıyâsî', '', None, p[1])
        ekle('masdar-ı sınâî', ad + ' + iyye', sinai(p[0]), kok, 'kıyâsî', '', None, p[1])
    for ad, sp in ISM_MASDAR:
        tek('ism-i masdar (aday: fiilin harflerinden eksik, masdar manalı)', ad, sp, 'semâî aday')
    for ad, sp in ISM_CINS:
        p = P(sp)
        if p is None:
            continue
        ekle('ism-i cins · ifrâdî (aday)', ad, p[0], kok, 'semâî aday', '', None, p[1])
        ekle('ism-i cins · cem‘î ve tekili (+tâ)', ad + ' + tâ (tekili)', muennes(p[0]), kok, 'semâî aday', '', None, p[1])
    for ad, sp in CEMI_MUKESSER:
        p = P(sp)
        if p is None:
            red.append(('cem‘-i mükesser (aday)', ad, 'bu kök sınıfında bu kalıp yok'))
            continue
        ekle('cem‘-i mükesser (aday)', ad, p[0], kok, 'semâî aday', '', None, p[1])
    for ad, sp in CEMI_MUKESSER:
        p = P(sp)
        if p is None:
            continue
        ekle('cem‘u’l-cem‘ (aday)', ad + ' + ât', salim_muen(p[0]), kok, 'semâî aday', '', None, p[1])
    return sinif, satir, red


def md(kok, sinif, satir, red):
    benzersiz = len({s['ar'] for s in satir})
    idg = sum(1 for s in satir if s['idg'])
    il = sum(1 for s in satir if 'ilal' in s['etiket'])
    out = ['# İŞTİKAK MOTORU ÇIKTISI — kök %s (%s)\n' % (' '.join(kok), sinif),
           'Arapça ve Latin sütunları **motorun çıktısıdır**; Türkçe ve mana sütunları **elle yazılacak** (boş).\n',
           'Sayım: **%d satır · %d ayrı Arapça biçim · %d satırda idgam · %d satırda ilal kaidesi · %d reddedilen**\n' % (
               len(satir), benzersiz, idg, il, len(red))]
    grup = {}
    for s in satir:
        grup.setdefault(s['grup'], []).append(s)
    for g, rows in grup.items():
        out.append('\n## %s (%d)\n' % (g, len(rows)))
        out.append('| kalıp | Arapça | Latin | etiket | Türkçe | mana değişmesi |')
        out.append('| :-- | :-- | :-- | :-- | :-- | :-- |')
        for r in rows:
            out.append('| %s | %s | %s | %s |  |  |' % (r['ad'], r['ar'], r['lat'], r['etiket']))
    if red:
        out.append('\n## Reddedilenler ve sebebi\n')
        out.append('| grup | kalıp | sebep |')
        out.append('| :-- | :-- | :-- |')
        for g, a, sb in red:
            out.append('| %s | %s | %s |' % (g, a, sb))
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    kok = normala(sys.argv[1])
    sinif, satir, red = tablo(kok)
    yol = sys.argv[2] if len(sys.argv) > 2 else None
    m = md(kok, sinif, satir, red)
    if yol:
        open(yol, 'w', encoding='utf-8').write(m)
    print(kok, sinif, 'satır', len(satir), 'ayrı', len({s['ar'] for s in satir}),
          'idgam', sum(1 for s in satir if s['idg']), 'red', len(red))
