import json, glob, os, collections, re
import turkce as T
import mustak_lugat as ML
import lugat_yapisi as LY
import kok_sadelestir as KS
import mesmu as MS
LUG = ML.yukle()
KLAS = os.environ.get('KELIME_KAYDI') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'kelime_kaydi')
say = collections.Counter()
for f in glob.glob(os.path.join(KLAS, 'kuranda_*', 'kokler', '*.json')):
    d = MS.genislet(json.load(open(f, encoding='utf-8'))); k = d['kok']
    if not d.get('mustak'): continue
    kur = {}
    for g in d.get('kelimeler', []):
        if g.get('lemma') and g.get('tr'): kur.setdefault(g['lemma'], g['tr'])
    yap = {}
    satir = []
    for gr, L in d['mustak'].items():
        bm = re.search(r'bâb ([IVX]+)', gr)
        for x in L:
            satir.append({'grup': gr, 'ad': x[0], 'etiket': x[1], 'bab': bm.group(1) if bm else '', 'ar': x[2], '_x': x})
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
            x[4], x[5] = lt, 'lugat'; say['lugat'] += 1
            if le not in (x[6] or ''): x[6] = ((x[6] + ' · ') if x[6] else '') + le
        elif s['ar'] in kur:
            x[4], x[5] = kur[s['ar']], 'kuran'; say['kuran'] += 1
            if not x[6]: x[6] = "Kur'ân"
        else:
            x[4], x[5] = s.get('tr', x[4]), s.get('guven', x[5]); say['kural'] += 1
    mevcut = {e: [m for m in L if 'manalar' not in m] for e, L in (d.get('lugat') or {}).items()}
    yeni = KS.lugat({'mustak_lugat': yap})
    birlesik = collections.OrderedDict()
    for e in list(mevcut) + [e for e in yeni if e not in mevcut]:
        L = yeni.get(e, []) + mevcut.get(e, [])
        if L: birlesik[e] = L
    if birlesik: d['lugat'] = birlesik
    else: d.pop('lugat', None)
    kanit = MS.kanit_ayir(k, d['mustak'])
    if kanit is not None:
        d = collections.OrderedDict((('mustak_kanit', kanit) if a == 'mustak' else (a, b)) for a, b in d.items())
    open(f, 'w', encoding='utf-8').write(KS.okunur(d) + '\n')
print(dict(say))
