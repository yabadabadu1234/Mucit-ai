# nazm_elle/*.json -> nazm_blok.json (sayfanın renk betiği için)
# Anahtar: âyetin harekesiz, durak işaretsiz Arapça metni. Değer: blokların [Arapça, Türkçe, vazife] listesi.
import json, glob, re, unicodedata
def norm(s):
    # renk.js'deki norm() ile birebir aynı kural
    s = re.sub(r'[\u064B-\u0670\u0640\u06D6-\u06ED]', '', s)
    s = re.sub(r'[\u0621\u0624\u0626]', '', s)
    s = re.sub(r'[\u0625\u0623\u0622\u0671]', '\u0627', s).replace('\u0649', '\u064A')
    return re.sub(r'\s+', ' ', s).strip()
out = {}
for f in sorted(glob.glob('nazm_elle/*.json')):
    d = json.load(open(f, encoding='utf-8'))
    for a in d['ayetler']:
        w = {k['i']: k['ar'] for k in a['kelimeler']}
        ar = ' '.join(w[i] for i in sorted(w))
        out[norm(ar)] = {'s': d['sure'], 'a': a['ayet'],
                         'b': [[' '.join(w[i] for i in b['ar']), b['tr'], b['v']] for b in a['bloklar']]}
json.dump(out, open('nazm_blok.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(out), 'ayet')
