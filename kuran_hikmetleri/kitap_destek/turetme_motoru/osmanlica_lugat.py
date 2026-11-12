import html
import json
import os
import re
import ssl
import sys
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import istikak as I

API = 'https://lugat-api.osmanlica.online/api/kelime?kelime='
KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
ONBELLEK = os.path.join(KOK, 'kaynak', 'lugat', 'osmanlica_sorgular.jsonl')
HRK = re.compile('[ًٌٍَُِّْٰـ]')
CEV = {'ٱ': 'ا', 'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ؤ': 'ء', 'ئ': 'ء', 'ة': 'ه', 'ک': 'ك', 'ی': 'ي', 'ڤ': 'ف', 'پ': 'ب', 'چ': 'ج', 'ژ': 'ز', 'گ': 'ك'}
ZAYIF = set('اويء')
HARF = {'ب': 'b', 'ت': 't', 'ث': 's', 'ج': 'c', 'ح': 'h', 'خ': 'h', 'د': 'd', 'ذ': 'z', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'ş', 'ص': 's',
        'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': '', 'غ': 'g', 'ف': 'f', 'ق': 'k', 'ك': 'k', 'ل': 'l', 'm': 'm', 'م': 'm', 'ن': 'n', 'ه': 'h',
        'ة': 'e', 'ء': '', 'أ': '', 'إ': '', 'ؤ': '', 'ئ': '', 'ٱ': 'a', 'آ': 'a'}
SERT = {'b': 'p', 'd': 't', 'c': 'ç', 'g': 'k'}
_CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')


def sade(s):
    s = unicodedata.normalize('NFKC', s)
    s = HRK.sub('', s)
    return ''.join(CEV.get(c, c) for c in s)


def latin(w):
    w = unicodedata.normalize('NFKC', w)
    o, n = [], len(w)
    for i, c in enumerate(w):
        nx = w[i + 1] if i + 1 < n else ''
        pv = w[i - 1] if i else ''
        if c in 'ًٌٍْـ':
            continue
        if c == 'َ':
            o.append('a')
        elif c == 'ِ':
            o.append('i')
        elif c == 'ُ':
            o.append('u')
        elif c == 'ّ':
            if o and o[-1] not in 'aiu':
                o.append(o[-1])
        elif c == 'ٰ':
            o.append('a')
        elif c in 'اى':
            if pv != 'َ':
                o.append('a')
        elif c == 'و':
            if pv == 'ُ':
                continue
            o.append('v' if nx == 'َ' or i == 0 else 'u')
        elif c == 'ي':
            if pv == 'ِ':
                continue
            o.append('y' if nx == 'َ' or i == 0 else 'i')
        elif c in HARF:
            o.append(HARF[c])
    return ''.join(o)


def sorgular(lemma, tr_kelimeler=()):
    q = []
    s = latin(lemma)
    if len(s) >= 3:
        q.append(s)
        if s[-1] in SERT:
            q.append(s[:-1] + SERT[s[-1]])
    for t in tr_kelimeler:
        t = t.strip().lower()
        if len(t) >= 3 and ' ' not in t:
            q.append(t)
    return list(dict.fromkeys(q))


def cek(q):
    u = urllib.request.Request(API + urllib.parse.quote(q), headers={'User-Agent': 'curl/8.5.0', 'Accept': 'application/json'})
    for _ in range(3):
        try:
            with urllib.request.urlopen(u, timeout=30, context=_CTX) as r:
                d = json.load(r)
            return d.get('data') or []
        except Exception:
            pass
    return None


def arapca_spanlar(h):
    out = []
    for m in re.finditer(r"<span class='Arabic[^']*'>([^<]+)</span>", h or ''):
        out.append(sade(m.group(1)))
    return out


def kok_uyar(kok, span):
    sert = [c for c in sade(kok) if c not in ZAYIF]
    if len(sert) < 2:
        return False
    k = [c for c in sade(kok)]
    i = 0
    for c in sert:
        j = span.find(c, i)
        if j < 0:
            return False
        i = j + 1
    return True


def temiz(h):
    return html.unescape(re.sub(r'<[^>]+>', ' ', h or '')).replace('\r', ' ').strip()


ASCII = str.maketrans({'â': 'a', 'î': 'i', 'û': 'u', 'ı': 'i', 'İ': 'i', 'ş': 's', 'ç': 'c', 'ğ': 'g', 'ö': 'o', 'ü': 'u', 'Â': 'a', 'Î': 'i', 'Û': 'u'})
ARAPCA_ESERLER = {'Kamus', 'Vankulu', 'Kamus-u Türki', 'Lugat-ı Remzi'}


def baslik(s):
    s = s.translate(ASCII).lower()
    return re.sub(r'[^a-z]', '', s)


def sec(kok, sorgu_listesi, veri):
    hedef = {baslik(x) for x in sorgu_listesi} | {baslik(x[:-1] + {'b': 'p', 'd': 't', 'c': 'c', 'g': 'k'}[x[-1]]) for x in sorgu_listesi if x and x[-1] in 'bdcg'}
    out = []
    for e in veri:
        sp = arapca_spanlar(e.get('mana_html'))
        ark = any(kok_uyar(kok, x) for x in sp[:3])
        bas = baslik(e['kelime'])
        tam = bas in hedef
        if ark:
            es = 'arapça yazılış kökle uyuştu' + (' · başlık tam' if tam else '')
        elif tam and e['eser_isim'] in ARAPCA_ESERLER:
            es = 'başlık tam (Arapça kaynaklı sözlük)'
        else:
            continue
        out.append({'eser': e['eser_isim'], 'madde': e['kelime'], 'arapca': sp[:3], 'mana': re.sub(r'\s+', ' ', temiz(e['mana_html'])), 'id': e['id'], 'eslesme': es})
    return out


def lemma_tara(kok, lemma):
    q = sorgular(lemma)
    sonuc, hata = {}, 0
    for a in q:
        v = cek(a)
        if v is None:
            hata += 1
            continue
        for x in sec(kok, q, v):
            sonuc[x['id']] = x
    return {'sorgular': q, 'maddeler': list(sonuc.values()), 'hata': hata}


def tum_tara(isci=12):
    kel = json.load(open(os.path.join(KOK, 'kaynak', 'sozluk', 'kelimeler.json'), encoding='utf-8'))
    isler = sorted({(I.normala(k['kok']), k['lem']) for k in kel if k['kok'] and k['lem'] and k['tur'] != 'Harf'})
    ob = yukle_onbellek()
    yap = [(k, l) for k, l in isler if k + '|' + l not in ob]
    print('lemma', len(isler), 'yapılacak', len(yap), flush=True)
    f = open(ONBELLEK, 'a', encoding='utf-8')
    n = 0

    def is_(kl):
        return kl, lemma_tara(*kl)
    with ThreadPoolExecutor(isci) as ex:
        for kl, r in ex.map(is_, yap):
            if r['hata'] and not r['maddeler']:
                continue
            f.write(json.dumps({'q': kl[0] + '|' + kl[1], 'd': r}, ensure_ascii=False) + '\n')
            n += 1
            if n % 200 == 0:
                f.flush()
                print(n, flush=True)
    f.close()


def yukle_onbellek():
    d = {}
    if os.path.exists(ONBELLEK):
        for ln in open(ONBELLEK, encoding='utf-8'):
            x = json.loads(ln)
            d[x['q']] = x['d']
    return d


if __name__ == '__main__':
    tum_tara()
