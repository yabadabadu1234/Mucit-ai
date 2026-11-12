import collections
import os
import re
import zipfile

import kaikki_suz as K

ZIP = os.path.join(os.path.dirname(__file__), '..', '..', 'kaynak', 'lugat', 'ham', 'muhassas_ibn_sida_shamile_htm.zip')
ONEK = ('وال', 'فال', 'بال', 'لل', 'كال', 'ال', 'و', 'ف', 'ب', 'ل', 'ك')


def bolumler():
    b = zipfile.ZipFile(ZIP).read('المخصص/المخصص.htm')
    t = b.decode('cp1256')
    x = re.sub(r'<[^>]+>', '\n', t)
    sat = [l.strip() for l in x.split('\n') if l.strip()]
    kitap, bab = '(giriş)', ''
    parca = collections.defaultdict(list)
    for l in sat:
        m = re.match(r'^\(?كتاب ([^()]{2,40})\)?$', l)
        if m:
            kitap, bab = K.sade(m.group(1)).strip(), ''
            continue
        m = re.match(r'^\(باب (.+)\)$', K.sade(l)) if l.startswith('(') else None
        if m and len(l) < 90:
            bab = m.group(1).strip()
            continue
        if re.match(r'^\(\d+/\d+\)$', l):
            continue
        parca[(kitap, bab)].append(l)
    return {k: ' '.join(v) for k, v in parca.items()}


def kelimeler(metin):
    return re.findall(r'[ء-ي]{2,}', K.sade(metin))


def adaylar(w):
    yield w
    for o in ONEK:
        if w.startswith(o) and len(w) - len(o) >= 3:
            yield w[len(o):]


def sinifla(kokler, en_az=4):
    import math
    form = collections.defaultdict(set)
    for k, r in kokler.items():
        for v in r.get('mustaklar', {}).values():
            for x in v:
                form[K.sade(x[1])].add(k)
        for e in r.get('kelimeler', []):
            form[K.sade(e['kelime'])].add(k)
    parca = bolumler()
    kt = collections.Counter()
    say = collections.defaultdict(collections.Counter)
    bsay = collections.defaultdict(collections.Counter)
    for (kit, bab), t in parca.items():
        for w in kelimeler(t):
            kt[kit] += 1
            for a in adaylar(w):
                ks = form.get(a)
                if ks:
                    for k in ks:
                        say[k][kit] += 1 / len(ks)
                        bsay[k][(kit, bab)] += 1 / len(ks)
                    break
    toplam = sum(kt.values())
    sonuc = {}
    for k, c in say.items():
        n = sum(c.values())
        if n < en_az:
            continue
        en = max(c, key=lambda x: (c[x] / kt[x]) / (n / toplam) * min(1, c[x] / en_az))
        bab = max((b for b in bsay[k] if b[0] == en), key=lambda b: bsay[k][b])
        sonuc[k] = {'kaynak': 'İbn Sîde, el-Muhassas (konu sıralı lügat; Şâmile)', 'kitap': en, 'bab': bab[1],
                    'kok_gecis': round(n, 1), 'kitapta_gecis': round(c[en], 1), 'zenginlesme': round((c[en] / kt[en]) / (n / toplam), 2)}
    return sonuc
