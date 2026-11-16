"""Kök dosyalarındaki müştak Türkçelerini turkce.py kurallarıyla yeniden yazar; Kur'ân'da geçen müştakta Kur'ân kelimesinin Türkçesi esastır."""
import json, glob, os, collections
import turkce as T
import mustak_lugat as ML
import lugat_yapisi as LY
LUG = ML.yukle()
from kelime_kaydi import okunur
KLAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'kelime_kaydi')
say = collections.Counter()
for f in glob.glob(os.path.join(KLAS, 'kuranda_*', 'kokler', '*.json')):
    d = json.load(open(f, encoding='utf-8')); k = d['kok']; K = d.get('kaliplar') or {}
    if not d.get('mustaklar'): continue
    kur = {}
    for e in d.get('kelimeler', []):
        tr = (e.get('turkce') or {}).get('lemma')
        if e.get('lemma') and tr: kur.setdefault(e['lemma'], tr)
    yap = {}
    satir = []
    for g, L in d['mustaklar'].items():
        for x in L:
            kal = K.get(str(x[0]), [g, '', '', ''])
            satir.append({'grup': kal[0], 'ad': kal[1], 'etiket': kal[2], 'bab': kal[3], 'ar': x[1], '_x': x})
    try:
        T.isle(k, satir)
    except Exception as e:
        say['hata'] += 1; continue
    for s in satir:
        x = s['_x']
        lm = LUG.get(k + '|' + s['ar'])
        lt, le = ML.mana_cikar(lm['maddeler']) if lm else (None, None)
        if lm and lm['maddeler'] and s['ar'] not in yap:
            yy = LY.yapilandir(lm['maddeler'])
            if yy: yap[s['ar']] = yy
        if lt:
            x[3], x[4] = lt, 'lugat'; say['lugat'] += 1
            if le not in (x[5] or ''): x[5] = ((x[5] + ' · ') if x[5] else '') + le
        elif s['ar'] in kur:
            x[3], x[4] = kur[s['ar']], 'kuran'; say['kuran'] += 1
            if not x[5]: x[5] = "Kur'ân"
        else:
            x[3], x[4] = s.get('tr', x[3]), s.get('guven', x[4]); say['kural'] += 1
    soz = d.setdefault('sozlukler', {})
    if yap: soz['mustak_lugat'] = yap
    else: soz.pop('mustak_lugat', None)
    open(f, 'w', encoding='utf-8').write(okunur(d))
print(dict(say))
