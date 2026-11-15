"""Gerçek kavram kafesi: kelimeler x mana tablosundan hesaplanır.
Nesne = kelime biçimi (tek kutu); vasıf = mana. Kenar = Hasse (içerme) kenarı."""
import itertools, collections
from kafes2_veri import nodes, M, W

ESAS = 'E'
# mana düğümleri (kök E hariç); R2 türeme zincirinin dışındadır
MANA = {i: n for i, n in nodes.items() if n['tur'] == M and i != ESAS}
# kelime biçimleri: aynı Arapça yazılış tek kutu
KELIME = collections.OrderedDict()
for i, n in nodes.items():
    if n['tur'] != W: continue
    k = KELIME.setdefault(n['ar'], dict(ar=n['ar'], tag=n['tag'], kuran=[], anlam={}))
    for p in n['ebeveyn']:
        k['anlam'][p] = n['tr']
    if n['kuran'] and n['kuran'] not in k['kuran']: k['kuran'].append(n['kuran'])
for k in KELIME.values():
    ks = [x for x in k['kuran'] if x != '★']
    k['kuran'] = ks[0] if ks else ('★' if k['kuran'] else '')

OBJ = list(KELIME)                          # nesneler
ATT = list(MANA)                            # vasıflar
inc = {o: frozenset(KELIME[o]['anlam']) for o in OBJ}   # nesnenin vasıfları
ext_att = {a: frozenset(o for o in OBJ if a in inc[o]) for a in ATT}


def intent(E):
    s = set(ATT)
    for o in E: s &= inc[o]
    return frozenset(s) if E else frozenset(ATT)


def extent(I):
    return frozenset(o for o in OBJ if I <= inc[o])

# kapanış: genişlikler = vasıf genişliklerinin kesişimleri
exts = {frozenset(OBJ)} | set(ext_att.values()) | {frozenset()}
ch = True
while ch:
    ch = False
    for a, b in itertools.combinations(list(exts), 2):
        c = a & b
        if c not in exts: exts.add(c); ch = True
# genişlik -> kavram (genişlik, derun)
kavram = {e: (e, intent(e)) for e in exts}
# her genişliğin derunu aynı genişliği vermeli (kapalılık)
for e, (E, I) in kavram.items():
    assert extent(I) == E, (E, I)
KAV = sorted(exts, key=lambda e: (-len(e), sorted(e)))
# Hasse kenarları: e1 < e2 minimal
cover = []
for a in KAV:
    ups = [b for b in KAV if a < b]
    for b in ups:
        if not any(a < c < b for c in ups): cover.append((b, a))   # (üst, alt)

if __name__ == '__main__':
    print('nesne', len(OBJ), 'vasıf', len(ATT), 'kavram', len(KAV), 'kenar', len(cover))
    for e in KAV:
        I = kavram[e][1]
        print(len(e), sorted(I) if len(I) < 6 else 'çok', [KELIME[o]['ar'] + ':' + '/'.join(KELIME[o]['anlam'].values()) for o in list(e)[:3]])
