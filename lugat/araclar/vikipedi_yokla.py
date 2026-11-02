import os, glob
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(KOK, 'vikipedi')
unsur = {r.split('\t')[0] for r in open(os.path.join(V, 'unsurlar.tsv'), encoding='utf-8').read().rstrip('\n').split('\n')[1:]}
gorulen, hata = {}, 0
for y in sorted(glob.glob(os.path.join(V, 'ceviri', '*.tsv'))):
    for no, r in enumerate(open(y, encoding='utf-8'), 1):
        p = r.rstrip('\n').split('\t')
        if len(p) < 2 or not p[1]:
            print('boş karşılık', os.path.basename(y), no, r.strip()); hata += 1; continue
        if p[0] not in unsur:
            print('unsurlarda yok', os.path.basename(y), no, p[0]); hata += 1
        if p[0] in gorulen:
            print('mükerrer', os.path.basename(y), no, p[0], 'evvelce', gorulen[p[0]]); hata += 1
        gorulen[p[0]] = os.path.basename(y)
print('karşılık', len(gorulen), 'unsur', len(unsur), 'hata', hata)
raise SystemExit(1 if hata else 0)
