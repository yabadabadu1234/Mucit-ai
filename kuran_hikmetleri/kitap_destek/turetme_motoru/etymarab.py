import collections
import json
import lzma
import os
import re

import istikak as I
import kaikki_suz as K

HAM = os.path.join(os.path.dirname(__file__), '..', '..', 'kaynak', 'lugat', 'ham', 'etymarab_polyglotta.jsonl.xz')


def kok_adaylari(ar):
    ar = K.sade(ar)
    adaylar = []
    for p in re.split(r'[/،,]', ar):
        p = re.sub(r'[()\s]', '', p)
        p = I.normala(p)
        if 2 <= len(p) <= 4:
            adaylar.append(p)
    return adaylar


def yukle():
    satirlar = [json.loads(l) for l in lzma.open(HAM, 'rt', encoding='utf-8')]
    latin_ar = {}
    kokler = {}
    sonra = []
    for r in satirlar:
        t = r.get('text', '')
        if not t:
            continue
        if r['level'] == '2':
            m = re.match(r'Back to library EtymArab (.*?) BP\b', t)
            if not m:
                continue
            bas = m.group(1)
            ma = re.search(r'([\u0600-\u06ff][\u0600-\u06ff/() ]*)$', bas)
            if not ma:
                continue
            latin = bas[:ma.start()].strip()
            for k in kok_adaylari(ma.group(1)):
                latin_ar.setdefault(latin, []).append(k)
                kokler.setdefault(k, {'kaynak': 'EtymArab, Oslo Üniversitesi (Bibliotheca Polyglotta)', 'latin': latin, 'dolu': len(re.findall(r'‘[^.…\s][^’]{2,}’', t)) > 0, 'kok_maddesi': t, 'kelime_maddeleri': []})
        else:
            sonra.append(t)
    anahtarlar = sorted(latin_ar, key=len, reverse=True)
    for t in sonra:
        m = re.search(r'√\s*(.+)', t)
        if not m:
            continue
        for a_ in anahtarlar:
            if m.group(1).startswith(a_):
                for k in latin_ar[a_]:
                    kokler[k]['kelime_maddeleri'].append(t)
                break
    return kokler
