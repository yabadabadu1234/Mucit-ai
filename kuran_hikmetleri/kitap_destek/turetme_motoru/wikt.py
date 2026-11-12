import json
import os
import re
from collections import defaultdict

import dogrula as D
import istikak as I

YOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'veri')
ARAP = re.compile('[ء-ْٰٱ]+')
_K = []


def yukle():
    if _K:
        return _K[0]
    d = defaultdict(list)
    for ln in open(os.path.join(YOL, 'ar_kok.jsonl'), encoding='utf-8'):
        e = json.loads(ln)
        d[I.normala(e['k'])].append(e)
    _K.append(d)
    return d


def masdarlar(e):
    x = e['e']
    i = x.find('verbal noun')
    if i < 0:
        return []
    return ARAP.findall(re.sub(r'\([^)]*\)', ' ', x[i + 11:]))


def tanik_kumesi(kok):
    t = {}
    for e in yukle().get(I.normala(kok), []):
        ing = (e['g'] or [''])[0][:70]
        if e['p'] != 'verb':
            for parca in e['l'].split(' or '):
                t[D.norm(parca.strip())] = ing
        for m in masdarlar(e):
            t.setdefault(D.norm(m), 'masdar (bâb %s): %s' % (e['f'], ing))
    return t


def gecislilik(kok):
    gec = []
    for e in yukle().get(I.normala(kok), []):
        if e['p'] == 'verb' and e['f'] == 'I':
            if 'transitive' in e['t']:
                gec.append('tr')
            elif 'intransitive' in e['t']:
                gec.append('intr')
    return gec


HAREKE = re.compile('[\u064B-\u0652\u0670]')


def harekesiz(s):
    return HAREKE.sub('', s)


def isle(kok, satir):
    t = tanik_kumesi(kok)
    sade = {harekesiz(f): g for f, g in t.items() if harekesiz(f) == f}
    n = 0
    for s in satir:
        a = t.get(D.norm(s['ar']))
        if a is None:
            a = sade.get(harekesiz(s['ar']))
        s['tanik'] = ('Vikisözlük: ' + a) if a is not None else ''
        n += bool(a is not None)
    return n, len(t)
