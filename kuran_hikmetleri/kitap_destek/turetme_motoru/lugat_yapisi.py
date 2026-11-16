"""Lügat maddesini kısımlarına ayırır: başlık, yazılış, tür, köken, numaralı manalar (etiket, tanım, misaller) ve deyimler."""
import re
BUYUK = 'A-ZÇĞİÖŞÜÂÎÛ'
ETIKET = re.compile(r'^((?:[a-zçğıöşüâîû]+\.\s){1,3})')
MISAL = re.compile(r'“[^”]+”|[^“()]+?\([^()]{2,60}\)\.?')


def misaller(t):
    out = []
    for m in MISAL.finditer(t):
        s = m.group(0).strip(' .')
        if not s: continue
        k = re.match(r'^(.*)\(([^()]{2,60})\)$', s)
        if s.startswith('“'): out.append([s.strip('“”'), ''])
        elif k and len(k.group(1).strip()) > 3: out.append([k.group(1).strip(' .'), k.group(2).strip()])
    return out


def mana_parcala(t):
    t = t.strip(); et = ''
    m = ETIKET.match(t)
    if m: et, t = m.group(1).strip(), t[m.end():]
    if ':' in t:
        tanim, gerisi = t.split(':', 1)
        return {'etiket': et, 'tanim': tanim.strip(' .'), 'misaller': misaller(gerisi)}
    return {'etiket': et, 'tanim': t.strip(' .'), 'misaller': []}


def kubbealti(madde, t):
    d = {'eser': 'Kubbealtı', 'madde': madde, 'yazilis': '', 'tur': '', 'koken': '', 'manalar': [], 'deyimler': []}
    m = re.match(r'^\(\s*([^)]*?)\s*\)\s*', t)
    if m: d['yazilis'] = m.group(1); t = t[m.end():]
    m = re.match(r'^((?:[a-zçğıöşüâîû]+\.\s?){1,3})', t)
    if m: d['tur'] = m.group(1).strip(); t = t[m.end():]
    m = re.match(r'^\(([^)]*)\)\s*', t)
    if m: d['koken'] = m.group(1).strip(); t = t[m.end():]
    ana, _, dey = t.partition('ѻ')
    parca = re.split(r'(?:^|\s)(\d{1,2})\.\s', ' ' + ana)
    if len(parca) > 1:
        for i in range(1, len(parca) - 1, 2):
            x = mana_parcala(parca[i + 1]); x['no'] = int(parca[i]); d['manalar'].append(x)
    elif ana.strip():
        x = mana_parcala(ana); x['no'] = 1; d['manalar'].append(x)
    for p in re.split(r'(?<=[.”])\s+(?=[' + BUYUK + r'][^:.]{1,80}?:\s)', dey.strip()):
        if ':' not in p: continue
        bas, ger = p.split(':', 1)
        x = mana_parcala(ger); x['deyim'] = bas.strip(); d['deyimler'].append(x)
    return d


AR = re.compile(r'[؀-ۿﭐ-﻿ً-ْ]+')


def luggat(madde, t):
    t = AR.sub('', t).strip()
    return {'eser': 'Luggat', 'madde': madde, 'manalar': [dict(mana_parcala(t), no=1)], 'deyimler': []}


def kamus(eser, madde, t):
    d = {'eser': eser, 'madde': madde, 'manalar': [], 'deyimler': []}
    m = re.match(r'^\s*(\S+)\s*\[([^\]]*)\]\s*(\([^)]*\))?\s*', t)
    if m: d['yazilis'] = m.group(1); d['okunus'] = m.group(2); d['koken'] = (m.group(3) or '').strip('() '); t = t[m.end():]
    for i, p in enumerate(re.split(r'(?<=[.!])\s+(?=Ve\s)', t)):
        p = re.sub(r'^Ve\s+', '', p).strip()
        if not p: continue
        mis = []
        for mm in re.finditer(r'(?:yukâlu|kavluhû|kavluhum)\s*:\s*([؀-ۿً-ْ\s]+)', p):
            mis.append([mm.group(1).strip(), ''])
        d['manalar'].append({'no': i + 1, 'etiket': '', 'tanim': p, 'misaller': mis})
    return d


def yapilandir(maddeler):
    out = []
    for m in maddeler:
        e, t = m['eser'], m['mana']
        if e == 'Kubbe Altı': out.append(kubbealti(m['madde'], t))
        elif e == 'Luggat': out.append(luggat(m['madde'], t))
        elif e in ('Kamus', 'Vankulu'): out.append(kamus(e, m['madde'], t))
    seen, son = set(), []
    for d in out:
        key = (d['eser'], json_key(d))
        if key in seen: continue
        seen.add(key); son.append(d)
    return son


def json_key(d):
    return '|'.join(x['tanim'] for x in d['manalar'])[:200]
