import sys

HARF = {'ا': 'ā', 'ب': 'b', 'ت': 't', 'ث': 'ṯ', 'ج': 'c', 'ح': 'ḥ', 'خ': 'ḫ', 'د': 'd', 'ذ': 'ẕ',
        'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'ş', 'ص': 'ṣ', 'ض': 'ḍ', 'ط': 'ṭ', 'ظ': 'ẓ', 'ع': 'ʿ',
        'غ': 'ğ', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'v',
        'ي': 'y', 'ء': 'ʾ', 'أ': 'ʾ', 'إ': 'ʾ'}
SAKIN = set('اويءأإىة')
LIT = {'X': 'ت', 'm': 'م', 't': 'ت', 'n': 'ن', 's': 'س', 'y': 'ي', 'w': 'و', 'A': 'ا', 'U': 'و', 'I': 'ي',
       'Y': 'ى', 'T': 'ة', 'E': 'أ', 'W': 'ا', 'Q': 'ء'}
HAR = {'a': 'َ', 'i': 'ِ', 'u': 'ُ', '0': 'ْ'}
SHD = 'ّ'
MADD = {'A': 'ā', 'U': 'ū', 'I': 'ī', 'Y': 'ā'}


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


def kok_sinifi(k):
    if len(k) != 3:
        return 'uç_harfli_değil'
    if any(h in SAKIN for h in k):
        return 'illetli_veya_hemzeli'
    return 'müdaaf' if k[1] == k[2] else 'sahîh'


def harfle(ts, kok):
    out = []
    for t in ts:
        c = t['c']
        if c in '1234':
            ch = kok[int(c) - 1]
        else:
            ch = LIT[c]
        out.append({'ch': ch, 'v': t['v'], 'sh': t['sh'], 'c': c, 'slot': c if c in '1234' else None})
    f = kok[0]
    for i, x in enumerate(out):
        if x['c'] == 'X':
            if f in 'دذ':
                x['ch'] = 'د'
                x['sh'] = True
                j = i - 1
                if out[j]['slot'] == '1':
                    out.pop(j)
                break
            if f in 'ز':
                x['ch'] = 'د'
            if f in 'صضطظ':
                x['ch'] = 'ط'
            break
    return out


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
            if r and r[-1]['v'] == '0' and a['v'] in 'aiu' and a['v'] != '':
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
        c = x['c']
        if c in MADD:
            s += MADD[c]
            continue
        if c == 'T':
            continue
        ch = HARF.get(x['ch'], x['ch'])
        if c == 'W':
            ch = ''
        s += ch * (2 if x['sh'] else 1)
        nxt = L[i + 1]['c'] if i + 1 < len(L) else ''
        if x['v'] in ('a', 'i', 'u') and nxt not in MADD:
            s += x['v']
    return s


def uret(spec_toks, kok):
    L, n = idgham(harfle(spec_toks, kok))
    return arapca(L), latin(L), n


def mensub(ts):
    t = kopya(ts)
    if t[-1]['c'] == 'T':
        t.pop()
    if t[-1]['c'] in MADD:
        return None
    t[-1]['v'] = 'i'
    t.append(tok('y', '', True))
    return t


def sinai(ts):
    t = kopya(ts)
    if t[-1]['c'] == 'T':
        t.pop()
    if t[-1]['c'] in MADD:
        return None
    t[-1]['v'] = 'i'
    t += [tok('y', 'a', True), tok('T')]
    return t


def tesniye(ts):
    t = kopya(ts)
    c = t[-1]['c']
    if c == 'T':
        t[-1] = tok('t', 'a')
    elif c == 'Y':
        t[-1] = tok('y', 'a')
    elif c in MADD:
        return None
    else:
        t[-1]['v'] = 'a'
    t += [tok('A'), tok('n')]
    return t


def salim_muz(ts, hal):
    t = kopya(ts)
    if t[-1]['c'] in MADD or t[-1]['c'] == 'T':
        return None
    t[-1]['v'] = 'u' if hal == 'u' else 'i'
    t += [tok('U' if hal == 'u' else 'I'), tok('n')]
    return t


def salim_muen(ts):
    t = kopya(ts)
    if t[-1]['c'] == 'T':
        t.pop()
    elif t[-1]['c'] in MADD:
        return None
    t[-1]['v'] = 'a'
    t += [tok('A'), tok('t')]
    return t


def muennes(ts):
    t = kopya(ts)
    if t[-1]['c'] in MADD or t[-1]['c'] == 'T':
        return None
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


# ---------------------------------------------------------------------------
# KALIP SİCİLİ.  kalıp = (ad, spec, etiket)   etiket: sema = semâî (kıyâsî değil, aday), kiyas = kıyâsî
# ---------------------------------------------------------------------------
MASDAR_SULASI = [
    ("fa'l", "1a 20 3", 'sema'), ("fi'l", "1i 20 3", 'sema'), ("fu'l", "1u 20 3", 'sema'),
    ("fa'al", "1a 2a 3", 'sema'), ("fi'al", "1i 2a 3", 'sema'), ("fu'ul", "1u 2u 3", 'sema'),
    ("fu'ūl", "1u 2u U 3", 'sema'), ("fi'āl", "1i 2a A 3", 'sema'), ("fu'āl", "1u 2a A 3", 'sema'),
    ("fa'āl", "1a 2a A 3", 'sema'), ("fa'āle", "1a 2a A 3a T", 'sema'), ("fu'ūle", "1u 2u U 3a T", 'sema'),
    ("fi'āle", "1i 2a A 3a T", 'sema'), ("fa'īl", "1a 2i I 3", 'sema'), ("fa'ūl", "1a 2u U 3", 'sema'),
    ("fa'alān", "1a 2a 3a A n", 'sema'), ("fu'lān", "1u 20 3a A n", 'sema'), ("fi'lān", "1i 20 3a A n", 'sema'),
    ("fa'lā", "1a 20 3a Y", 'sema'), ("fu'lā", "1u 20 3a Y", 'sema'), ("fi'lā", "1i 20 3a Y", 'sema'),
    ("fa'ale", "1a 2a 3a T", 'sema'), ("fi'ale", "1i 2a 3a T", 'sema'),
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

# bâblar: masdar kalıpları, fâil, mef'ûl
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
    ('VII', "infi'âl (mutâvaa)", [("infi'āl", "Wi n0 1i 2a A 3")],
     ("munfa'il", "mu n0 1a 2i 3"), ("munfa'al", "mu n0 1a 2a 3")),
    ('VIII', "ifti'âl", [("ifti'āl", "Wi 10 Xi 2a A 3")],
     ("muftaʿil", "mu 10 Xa 2i 3"), ("muftaʿal", "mu 10 Xa 2a 3")),
    ('IX', "if'ilâl (renk/ayıp)", [("if'ilāl", "Wi 10 2i 3a A 3")],
     ("muf'all", "mu 10 2a 3+"), None),
    ('X', "istif'âl", [("istif'āl", "Wi s0 ti 10 2a A 3")],
     ("mustaf'il", "mu s0 ta 10 2i 3"), ("mustaf'al", "mu s0 ta 10 2a 3")),
    ('XI', "if'îlâl", [("if'īlāl", "Wi 10 2i I 3a A 3")], ("muf'āll", "mu 10 2a A 3+"), None),
    ('XII', "if'iv'âl", [("if'iv'āl", "Wi 10 2i w0 2a A 3")], None, None),
    ('XIII', "if'ivvâl", [("if'ivvāl", "Wi 10 2i w+0 3a A 3")], None, None),
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
    sinif = kok_sinifi(kok)
    satir = []
    red = []

    def ekle(grup, ad, ts, kok_, etiket='', bab=''):
        if ts is None:
            red.append((grup, ad, 'uygulanamaz (sondaki harf bu eki almaz)'))
            return
        a, l, n = uret(ts, kok_)
        satir.append({'grup': grup, 'ad': ad, 'ar': a, 'lat': l, 'idg': n, 'etiket': etiket, 'bab': bab})

    def turevler(grup, ad, spec, kok_, gender, etiket='', bab='', cem_salim=True):
        ts = parse(spec)
        ekle(grup, ad, ts, kok_, etiket, bab)
        if gender:
            m = muennes(ts)
            ekle(grup, ad + ' + müennes', m, kok_, etiket, bab)
        ekle(grup, ad + ' + tesniye', tesniye(ts), kok_, etiket, bab)
        if gender:
            m = muennes(ts)
            if m:
                ekle(grup, ad + ' + müennes tesniye', tesniye(m), kok_, etiket, bab)
        if gender and cem_salim:
            ekle(grup, ad + ' + cem‘-i sâlim müzekker (-ûn)', salim_muz(ts, 'u'), kok_, etiket, bab)
            ekle(grup, ad + ' + cem‘-i sâlim müzekker (-în)', salim_muz(ts, 'i'), kok_, etiket, bab)
            ekle(grup, ad + ' + cem‘-i sâlim müennes (-ât)', salim_muen(ts), kok_, etiket, bab)

    if sinif not in ('sahîh', 'müdaaf'):
        return sinif, [], [('kök', kok, 'kök sınıfı (%s) bu motorda yok; reddedildi' % sinif)]

    # --- sülâsî mücerred masdarlar
    for ad, sp, e in MASDAR_SULASI:
        ekle('masdar · sülâsî mücerred', ad, parse(sp), kok, 'semâî aday')
    # --- bâblar
    for rom, ad, masdarlar, fail, mef in BAB:
        if rom in ('IX', 'XI', 'XII', 'XIII') and sinif == 'müdaaf':
            red.append(('bâb ' + rom, ad, 'müdaaf kökte bu bâb idgham yaptırır veya yaptırmaz; semâîdir, motor üretmez'))
            continue
        for mad_ad, sp in masdarlar:
            ekle('masdar · bâb ' + rom, mad_ad, parse(sp), kok, 'kıyâsî', rom)
        for mad_ad, sp in masdarlar:
            if not sp.endswith(' T') and rom not in ('IX', 'XI', 'XII', 'XIII'):
                ekle('ism-i merre · bâb ' + rom, mad_ad + ' + tâ', merre(parse(sp)), kok, 'aday', rom)
        if fail:
            turevler('ism-i fâil · bâb ' + rom, fail[0], fail[1], kok, True, 'kıyâsî', rom)
        if mef:
            turevler('ism-i mef‘ûl · bâb ' + rom, mef[0], mef[1], kok, True, 'kıyâsî', rom)
            ekle('mekân/zaman/masdar-ı mîmî · bâb ' + rom, mef[0], parse(mef[1]), kok, 'kıyâsî', rom)
    # --- rubâ'î (yalnız müdaaf köklerde kök ikilenir)
    if sinif == 'müdaaf':
        kok4 = kok[0] + kok[1] + kok[0] + kok[1]
        for grp, ad, masdarlar, fail, mef in BAB_RUBAI:
            for mad_ad, sp in masdarlar:
                ekle('masdar · ' + grp, mad_ad, parse(sp), kok4, 'kıyâsî (kök ikilendi)')
            ekle('ism-i fâil · ' + grp, fail[0], parse(fail[1]), kok4, 'kıyâsî')
            ekle('ism-i mef‘ûl · ' + grp, mef[0], parse(mef[1]), kok4, 'kıyâsî')
    else:
        red.append(('rubâ‘î', 'dört harfli bâblar', 'sahîh üç harfli kökte kök ikilenmez; rubâ‘î kök ayrı bir köktür'))
    # --- sülâsî müştaklar
    for grp, ad, sp, g in SULASI_MUSTAK:
        if grp in ('ism-i fâil', 'ism-i mef‘ûl'):
            turevler(grp + ' · sülâsî', ad, sp, kok, True, 'kıyâsî')
        elif grp.startswith('tafdîl') or grp.startswith('tasğîr') or grp.startswith('âlet') or grp.startswith('mekân'):
            turevler(grp + ' · sülâsî', ad, sp, kok, False, 'kıyâsî')
        else:
            turevler(grp + ' · sülâsî', ad, sp, kok, False, 'kıyâsî' if grp.startswith('masdar') else 'aday')
    for ad, sp in SIFAT_MUSEBBEHE:
        turevler('sıfat-ı müşebbehe', ad, sp, kok, True, 'semâî aday')
    for ad, sp in MUBALAGA:
        turevler('mübalağa', ad, sp, kok, True, 'semâî aday')
    # --- mensûb, sınâî
    for ad, sp in (("fa'l", "1a 20 3"), ("fâ'il", "1a A 2i 3"), ("maf'ûl", "ma 10 2u U 3"), ("fa'īl", "1a 2i I 3")):
        ekle('mensûb', ad + ' + iyy', mensub(parse(sp)), kok, 'kıyâsî')
        ekle('masdar-ı sınâî', ad + ' + iyye', sinai(parse(sp)), kok, 'kıyâsî')
    # --- cem'-i mükesser (kalıp adayları) ve cem'u'l-cem'
    for ad, sp in CEMI_MUKESSER:
        ekle('cem‘-i mükesser (aday)', ad, parse(sp), kok, 'semâî aday')
    for ad, sp in CEMI_MUKESSER:
        ekle('cem‘u’l-cem‘ (aday)', ad + ' + ât', salim_muen(parse(sp)), kok, 'semâî aday')
    return sinif, satir, red


def md(kok, sinif, satir, red):
    benzersiz = len({s['ar'] for s in satir})
    idg = sum(1 for s in satir if s['idg'])
    out = []
    out.append('# İŞTİKAK MOTORU ÇIKTISI — kök %s (%s)\n' % (' '.join(kok), sinif))
    out.append('Arapça ve Latin sütunları **motorun çıktısıdır**; Türkçe ve mana sütunları **elle yazılacak** (boş).\n')
    out.append('Sayım: **%d satır · %d ayrı Arapça biçim · %d satırda idgham uygulandı · %d reddedilen**\n' % (
        len(satir), benzersiz, idg, len(red)))
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
    kok = sys.argv[1]
    sinif, satir, red = tablo(kok)
    yol = sys.argv[2] if len(sys.argv) > 2 else None
    m = md(kok, sinif, satir, red)
    if yol:
        open(yol, 'w', encoding='utf-8').write(m)
    print(kok, sinif, 'satır', len(satir), 'ayrı', len({s['ar'] for s in satir}),
          'idgham', sum(1 for s in satir if s['idg']), 'red', len(red))
