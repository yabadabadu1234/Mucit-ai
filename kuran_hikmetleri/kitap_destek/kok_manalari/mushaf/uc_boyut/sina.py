import sys, math, itertools, json, pathlib
import numpy as np
import munasebet_geometri as G
HERE = pathlib.Path(__file__).resolve().parent
OUT = []
def p(*a):
    s = ' '.join(str(x) for x in a); print(s); OUT.append(s)

def nokta(S): return {u: (S['x'][u], S['y'][u]) for u in S['ids']}

def tam_coz(ad):
    mk, P = G.yukle(ad); S = G.kur(mk, P); X, Y, Z = G.izgara(S)
    fam, zs = G.coz_gaye_agaci(nokta(S), X, Y, Z)
    return mk, P, S, X, Y, Z, fam, zs

def f1(a, b):
    if not a and not b: return 1.0
    return len(a & b) / len(a | b)

for ad in G.json.load(open(G.HERE / 'munasebet_anahtar.json', encoding='utf-8'))['pasajlar']:
    p('=====', ad)
    mk, P, S, X, Y, Z, fam, zs = tam_coz(ad)
    ben = G.beklenen_aile(P)
    # T0 tam çözüm
    mm = G.coz_makam(S['th'], len(mk)); mok = sum(mm[u] == mk.index(S['bi'][u]['makam']) for u in S['ids'])
    p('T0 makam okuma', mok, '/', len(S['ids']), '| gaye ailesi IoU', round(f1(fam, ben), 3), '| beklenen', len(ben), 'çözülen', len(fam))
    # çukur
    ck = G.coz_cukur(Z, X, Y, None)
    p('T5 hazif: çözülen oyuklar (x,y)', ck, '| beklenen yarık x', [S['x'][h['sonra']] + 0.5 for h in P['hazif']])
    # T1 izdüşüm kaybı: her izdüşümden okunabilen hüküm sayısı
    gerc = {'sira': 1, 'makam': 1, 'derinlik': 1, 'gaye': 1, 'hazif': 1}
    # (x,th): sıra+makam; (y,z): derinlik (y), z; (x,z)=max_y z
    zmax_x = Z.max(axis=0)
    ckx = [round(float(X[0][i]), 2) for i in range(2, len(zmax_x) - 2) if zmax_x[i] < zmax_x[i-1] and zmax_x[i] < zmax_x[i+1]]
    p('T1 izdüşümler: (x,θ) makam doğru', mok, '| (x,θ) gaye ağacı: okunamaz (z yok) | (x,z)-zarfı yerel çukurlar', ckx, '| (y,z): derinlik+yükseklik, sıra yok')
    # tam gaye çözümü yalnız (x,y,z)'den: x veya y atılınca
    Xd = X.copy(); Yd = Y.copy()
    # y atıldı: tüm noktalar y=ortak
    nk = {u: (S['x'][u], 0.0) for u in S['ids']}
    fam_y, _ = G.coz_gaye_agaci(nk, X, Y, Z)
    nk2 = {u: (0.0, S['y'][u]) for u in S['ids']}
    fam_x, _ = G.coz_gaye_agaci(nk2, X, Y, Z)
    p('T2 eksen ablasyonu: gaye IoU tam', round(f1(fam, ben), 3), '| y atılırsa', round(f1(fam_y, ben), 3), '| x atılırsa', round(f1(fam_x, ben), 3), '| θ atılırsa makam', 'şans=1/%d' % len(mk))
    # T3 süreklilik
    zl = np.array([zs[u] for u in S['ids']]).min() * 0.5
    from scipy import ndimage as nd
    lab, n = nd.label(Z >= zl)
    ixs = {u: (np.abs(X[0]-S['x'][u]).argmin(), np.abs(Y[:,0]-S['y'][u]).argmin()) for u in S['ids']}
    comp = {lab[j, i] for u, (i, j) in ixs.items()}
    p('T3 süreklilik: eşik', round(float(zl), 2), '| noktaların bulunduğu bağlı bileşen sayısı', len(comp - {0}), '(1 olmalı)')
    # T4 tekrar
    for a, b in P['tekrar']:
        za, zb = zs[a], zs[b]
        p('T4 tekrar', S['bi'][a]['konu'], '(', a, b, ') aynı konu, z farkı', round(abs(za - zb), 3), '| makam', S['bi'][a]['makam'], S['bi'][b]['makam'], '| gaye', S['bi'][a]['gaye'], S['bi'][b]['gaye'], '| z eşit değil?', abs(za - zb) > 1e-3)
    # T6 yer değiştirme: iki birim yer değiştirir; illet tersine döner + gaye ağacı değişir
    n_degis = 0; n_toplam = 0; ters_toplam = 0
    ids = S['ids']
    for i, j in itertools.combinations(range(len(ids)), 2):
        s2 = list(ids); s2[i], s2[j] = s2[j], s2[i]
        S2 = G.kur(mk, P, sira=s2); X2, Y2, Z2 = G.izgara(S2)
        fam2, _ = G.coz_gaye_agaci(nokta(S2), X2, Y2, Z2)
        ters = sum(1 for b in P['birimler'] for q in b['illet'] if S2['x'][q] > S2['x'][b['id']])
        n_toplam += 1; n_degis += (fam2 != fam) or ters > 0; ters_toplam += ters > 0
    p('T6 yer değiştirme: %d çift takasın %d\'inde şekil değişti (illet-tersinmesi görünen: %d; gaye ağacı değişen: aşağıda)' % (n_toplam, n_degis, ters_toplam))
    # gaye ağacı değişim sayısını ayrıca say
    ch = 0
    for i, j in itertools.combinations(range(len(ids)), 2):
        s2 = list(ids); s2[i], s2[j] = s2[j], s2[i]
        S2 = G.kur(mk, P, sira=s2); X2, Y2, Z2 = G.izgara(S2)
        fam2, _ = G.coz_gaye_agaci(nokta(S2), X2, Y2, Z2); ch += fam2 != fam
    p('   gaye ailesi takas sonrası değişen çift:', ch, '/', n_toplam)
    # T7 elle koordinat yok: determinizm + tek ilişki değişince koordinat değişir
    S_a = G.kur(mk, P); S_b = G.kur(mk, P)
    det = S_a['x'] == S_b['x'] and S_a['y'] == S_b['y']
    import copy
    P2 = copy.deepcopy(P); u0 = P2['birimler'][-1]; u0['illet'] = []  # son birimin illeti kaldırılırsa y değişmeli
    S_c = G.kur(mk, P2)
    p('T7 determinizm', det, '| tek ilişki değişince y değişti', S_c['y'] != S_a['y'])
open(HERE / 'OLCUM.txt', 'w', encoding='utf-8').write('\n'.join(OUT))
