import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mushaf_dizgi as M
SUT = 4; COLS = 104; ADIM = 6; BOSLUK = 3
def fatiha_ayetleri():
    v = json.load(open(HERE.parent.parent / 'kaynak' / 'sure' / '1.json', encoding='utf-8'))['verses']
    return [v[i]['arabic'].strip().split() for i in range(1, 7)]
# Yapı ağacı: padişahın Fâtiha şemasından okunmuş KAYIT (veri; kural değil). (ad, ayet_no, ilk, son, saf, şerit, derinlik)
DUGUM = [
    ('A', 2, 0, 1, 1, 'ana', 0), ('C', 2, 2, 3, 1, 'ana', 1), ('B', 3, 0, 1, 1, 'yan', 1), ('D', 4, 0, 2, 1, 'ana', 2),
    ('E', 5, 0, 1, 2, 'ana', 0), ('F', 5, 2, 3, 2, 'ana', 1), ('G', 6, 0, 2, 2, 'ana', 2), ('H', 7, 0, 3, 2, 'ana', 3),
    ('I', 7, 4, 6, 3, 'ana', 3), ('J', 7, 7, 8, 3, 'ana', 4)]
SAF_YONU = {1: 'R', 2: 'L', 3: 'R'}
# Şemadan okunan referans (dugum sırasıyla): kenarlar, safların sırası
REF_KENAR = {(0, 1), (0, 2), (1, 3), (4, 5), (5, 6), (6, 7), (6, 8), (8, 9)}
REF_SAFLAR = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
REF_YON = ['R', 'L', 'R']
def metin_bol():
    ay = fatiha_ayetleri(); out = []
    for ad, a, i, j, s, ser, d in DUGUM:
        out.append(ay[a - 2][i:j + 1])
    flat = [t for n in out for t in n]; asil = [t for x in ay for t in x]
    assert flat == asil, 'metin bütünlüğü bozuldu'
    return out
def kutu(t): return '█' * max(1, round(M.gen(t) * SUT))
def satirlar():
    parc = metin_bol(); L = []
    for k, (ad, a, i, j, s, ser, d) in enumerate(DUGUM):
        kut = ' '.join(kutu(t) for t in reversed(parc[k]))
        yon = SAF_YONU[s]
        if ser == 'yan': yon = 'L' if yon == 'R' else 'R'
        L.append(dict(saf=s, yon=yon, derin=d, kut=kut, n=len(parc[k])))
    return L
def sanat():
    L = satirlar(); rows = []; prev = None
    for k, l in enumerate(L):
        if prev is not None and l['saf'] != prev:
            rows += ['   |' + ' ' * COLS + '|'] * BOSLUK
        prev = l['saf']; ins = l['derin'] * ADIM; pad = COLS - len(l['kut']) - ins
        s = (' ' * pad + l['kut'] + ' ' * ins) if l['yon'] == 'R' else (' ' * ins + l['kut'] + ' ' * pad)
        rows.append('%02d |%s| (%d kutu)' % (k + 1, s, l['n']))
    return '\n'.join(rows)
def coz(art):
    """Maskeli iskeleti yalnız geometriyle okur: bant, yön, derinlik, ebeveyn."""
    L = []; bos = 0; band = 0; sat = []
    for r in art.split('\n'):
        if r.startswith('   |'):
            bos += 1; continue
        if bos >= BOSLUK: band += 1
        bos = 0
        ic = r[4:4 + COLS]; sol = len(ic) - len(ic.lstrip(' ')); sag = len(ic) - len(ic.rstrip(' '))
        yon = 'R' if sol > sag or (sag == 0 and sol > 0) else 'L'
        if sag == 0 and sol > 0: yon = 'R'
        elif sol == 0 and sag > 0: yon = 'L'
        elif sol >= sag: yon = 'R'
        else: yon = 'L'
        ins = (sag if yon == 'R' else sol) // ADIM
        sat.append(dict(band=band, yon=yon, derin=ins))
    # şerit: bandın ilk satırının yönü ana şerit
    taban = {}
    for s in sat: taban.setdefault(s['band'], s['yon'])
    for s in sat: s['ana'] = (s['yon'] == taban[s['band']])
    kenar = set()
    for k, s in enumerate(sat):
        if s['derin'] == 0 and s['ana']: continue
        for q in range(k - 1, -1, -1):
            if sat[q]['ana'] and sat[q]['derin'] == s['derin'] - 1: kenar.add((q, k)); break
    bantlar = {}
    for k, s in enumerate(sat): bantlar.setdefault(s['band'], []).append(k)
    return kenar, [bantlar[b] for b in sorted(bantlar)], [taban[b] for b in sorted(taban)]
if __name__ == '__main__':
    art = sanat(); print(art)
    kenar, bant, yon = coz(art)
    print('kenarlar', sorted(kenar)); print('bantlar', bant); print('yönler', yon)
    print('İZOMORF' if (kenar == REF_KENAR and bant == REF_SAFLAR and yon == REF_YON) else 'DENK DEĞİL')
