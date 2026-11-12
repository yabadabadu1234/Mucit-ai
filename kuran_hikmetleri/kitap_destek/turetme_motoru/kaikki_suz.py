import json
import re
import sys
import unicodedata

HAREKE = re.compile('[ً-ْٰـ]')


def sade(s):
    return HAREKE.sub('', s)


def kok_bul(d):
    for t in d.get('etymology_templates', []) or []:
        if t.get('name') == 'ar-rootbox':
            a = t.get('args', {})
            harfler = [a[k] for k in sorted(a, key=lambda x: int(x) if x.isdigit() else 99) if k.isdigit()]
            if harfler:
                return ''.join(h.replace(' ', '') for h in harfler)
    for s in d.get('senses', []):
        for c in s.get('categories', []) or []:
            m = re.match(r'Arabic terms belonging to the root (.+)', c.get('name', ''))
            if m:
                return m.group(1).replace(' ', '')
    for h in d.get('head_templates', []) or []:
        if h.get('name') in ('ar-verb form', 'ar-verb'):
            a = (h.get('args', {}).get('1') or '')
            m = re.match(r'\+?([ء-ي]{3,4})<', a)
            if m and h.get('name') == 'ar-verb form':
                return m.group(1)
    return None


def kelimeler(liste):
    c = []
    for x in liste or []:
        if isinstance(x, dict):
            w = x.get('word') or x.get('roman') or ''
            if w:
                c.append(w)
        elif isinstance(x, str):
            c.append(x)
    return c


def siki(d):
    r = {'w': d['word'], 'u': sade(d['word']), 'p': d['pos']}
    if d.get('etymology_number'):
        r['n'] = d['etymology_number']
    ht = d.get('head_templates') or []
    if ht:
        r['h'] = ht[0].get('name', '')
        ex = ht[0].get('expansion', '')
        if ex:
            r['e'] = ex[:400]
    et = d.get('etymology_text')
    if et:
        r['t'] = et
    sab = []
    for t in d.get('etymology_templates', []) or []:
        if t.get('name') == 'ety':
            continue
        ex = (t.get('expansion') or '')[:200]
        sab.append([t.get('name', ''), ex])
    if sab:
        r['s'] = sab
    gl = []
    etk = set()
    fo = []
    for s in d.get('senses', []):
        for g in s.get('glosses', []) or []:
            gl.append(g)
        etk.update(s.get('tags', []) or [])
        for f in s.get('form_of', []) or []:
            if isinstance(f, dict) and f.get('word'):
                fo.append(f['word'])
        for k in ('synonyms', 'antonyms'):
            if s.get(k):
                r.setdefault(k, []).extend(kelimeler(s[k]))
    if gl:
        r['g'] = gl
    if etk:
        r['tag'] = sorted(etk)
    if fo:
        r['fo'] = fo
    rom = [f['form'] for f in d.get('forms', []) or [] if 'romanization' in (f.get('tags') or [])]
    if rom:
        r['r'] = rom[:3]
    snd = []
    for x in d.get('sounds', []) or []:
        if x.get('ipa'):
            snd.append(x['ipa'])
    if snd:
        r['ipa'] = snd[:3]
    for k, a in (('descendants', 'ds'), ('derived', 'dr'), ('related', 'rl'), ('coordinate_terms', 'ct'), ('hypernyms', 'hy'), ('hyponyms', 'ho')):
        v = d.get(k)
        if v:
            r[a] = [[x.get('lang_code', ''), x.get('word', ''), x.get('roman', '')] if k == 'descendants' else (x.get('word', '') if isinstance(x, dict) else x) for x in v if isinstance(x, (dict, str))]
    el = d.get('etymology_links')
    if el:
        r['el'] = el
    if d.get('wikipedia'):
        r['wp'] = d['wikipedia']
    return r
