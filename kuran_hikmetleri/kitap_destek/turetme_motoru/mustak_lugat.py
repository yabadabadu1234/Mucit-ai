"""Lügatte geçen müştakları Osmanlıca lügatlerde arar. Okunuş Arapça harekeden, ince ve kalın iki ünlü uyumuyla üretilir;
madde ancak Arapça yazılışı müştakla aynıysa kabul edilir. Sonuç önbelleğe yazılır."""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
import osmanlica_lugat as O
ONB = os.path.join(O.KOK, 'kaynak', 'lugat', 'mustak_osmanlica.jsonl')
UNSUZ = {'ب': 'b', 'ت': 't', 'ث': 's', 'ج': 'c', 'ح': 'h', 'خ': 'h', 'د': 'd', 'ذ': 'z', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'ş', 'ص': 's',
         'ض': 'z', 'ط': 't', 'ظ': 'z', 'غ': 'g', 'ف': 'f', 'ق': 'k', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h'}
def okunus(w, kip):
    w = re.sub('^ٱ?ال', '', w); o = []; i = 0; sesli = [0]
    def a_u(): 
        n = sesli[0]; sesli[0] += 1
        ince = kip == 'ince' or (kip == 'karma' and n > 0)
        return ('e', 'ü') if ince else ('a', 'u')
    while i < len(w):
        c = w[i]; nx = w[i + 1] if i + 1 < len(w) else ''
        if c in UNSUZ: o.append(UNSUZ[c])
        elif c in 'وي' and o and o[-1] in 'aeuüi' and nx not in 'َُِّ':
            if c == 'و' and o[-1] in 'uü': o[-1] = 'û'
            elif c == 'ي' and o[-1] == 'i': o[-1] = 'î'
            else: o.append('v' if c == 'و' else 'y')
        elif c == 'و': o.append('v')
        elif c == 'ي': o.append('y')
        elif c in 'اى' and o and o[-1] in 'ae': o[-1] = 'â'
        elif c == 'َ': o.append(a_u()[0])
        elif c == 'ُ': o.append(a_u()[1])
        elif c == 'ِ': a_u(); o.append('i')
        elif c == 'ّ' and o: o.append(o[-1] if o[-1] not in 'aeuüiâîû' else o[-2])
        elif c == 'ة':
            if not (o and o[-1] in 'ae'): o.append(a_u()[0])
        i += 1
    return ''.join(o).replace('ûû', 'û').replace('îî', 'î')
def sorgular(w):
    q = []
    for kip in ('ince', 'karma', 'kalin'):
        s = okunus(w, kip)
        q.append(s)
        if w.endswith('ة'): q.append(s + 't')
    return list(dict.fromkeys(x for x in q if len(x) >= 3))
def norm(s):
    s = O.sade(s); s = re.sub('^ال', '', s)
    return re.sub('[هت]$', 'ه', s)
def ilk_arapca(t):
    m = re.search(r'[؀-ۿً-ْ]{2,}', t)
    return m.group(0) if m else ''
def tara(kok, w):
    hedef = norm(w); out, hata = {}, 0
    for q in sorgular(w):
        v = O.cek(q)
        if v is None: hata += 1; continue
        for e in v:
            t = re.sub(r'\s+', ' ', O.temiz(e.get('mana_html')))
            sp = [norm(x) for x in O.arapca_spanlar(e.get('mana_html'))[:3]] + [norm(ilk_arapca(t))]
            if hedef in sp:
                out[e['id']] = {'eser': e['eser_isim'], 'madde': e['kelime'], 'mana': t}
        if out: break
    return {'sorgular': sorgular(w), 'maddeler': list(out.values()), 'hata': hata}
def yukle():
    d = {}
    if os.path.exists(ONB):
        for ln in open(ONB, encoding='utf-8'):
            x = json.loads(ln); d[x['q']] = x['d']
    return d
if __name__ == '__main__':
    isler = [tuple(x) for x in json.load(open(sys.argv[1], encoding='utf-8'))]
    ob = yukle(); yap = [x for x in isler if x[0] + '|' + x[1] not in ob]
    print('yapılacak', len(yap), flush=True)
    f = open(ONB, 'a', encoding='utf-8'); n = 0
    with ThreadPoolExecutor(24) as ex:
        for kl, r in ex.map(lambda kl: (kl, tara(*kl)), yap):
            if r['hata'] and not r['maddeler']: continue
            f.write(json.dumps({'q': kl[0] + '|' + kl[1], 'd': r}, ensure_ascii=False) + '\n'); n += 1
            if n % 500 == 0: f.flush(); print(n, flush=True)
    f.close(); print('bitti', n)


AR = re.compile(r'[؀-ۿﭐ-﻿ً-ْ]+')
def kisalt(t, n=80):
    t = re.sub(r'\s+', ' ', AR.sub('', t)).strip(' ,;:.-–()')
    t = re.split(r'(?<=[a-zçğıöşüâîû)])[.:;] ', t)[0]
    return t if len(t) <= n else t[:n].rsplit(' ', 1)[0] + '…'
def mana_cikar(maddeler):
    by = {}
    for m in maddeler: by.setdefault(m['eser'], []).append(m)
    for m in by.get('Luggat', []):
        t = kisalt(m['mana'])
        if len(t) >= 3: return t, 'Luggat'
    for m in by.get('Kubbe Altı', []):
        t = m['mana']
        t = re.sub(r'^.*?\(\s*Ar\.[^)]*\)\s*', '', t) if 'Ar.' in t[:200] else re.sub(r'^\([^)]*\)\s*\S+\.\s*', '', t)
        m1 = re.search(r'\b1\.\s*(.*?)(?=\s2\.\s|$)', t)
        t = kisalt(m1.group(1) if m1 else t)
        if len(t) >= 3: return t, 'Kubbealtı'
    for e in ('Kamus', 'Vankulu'):
        for m in by.get(e, []):
            t = re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', AR.sub(' ', m['mana']))
            t = re.sub(r'^\s*(ve\s+)?', '', re.sub(r'\s+', ' ', t))
            t = kisalt(re.sub(r'\bmanâsına(dır)?.*', '', t))
            if len(t) >= 3: return t, e
    return None, None
