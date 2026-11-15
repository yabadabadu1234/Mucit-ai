import json, html, pathlib
from kafes2_veri import nodes, M, W, HERE

# çocuk sırası; AB bir sanal gruptur: A ve B yan yana, ortak çocuk N ikisinin arasında
KID = {
    'E': ['AB', 'C', 'H'],
    'AB': ['w_A1', 'D', 'N', 'F', 'G', 'w_B1', 'w_B2', 'w_B3'],
    'C': ['w_C1'],
    'H': ['w_H1', 'w_H2', 'w_H3', 'w_H4'],
    'D': ['w_D1', 'w_D2', 'w_D3', 'w_D4', 'w_D5', 'J', 'K', 'L'],
    'J': ['w_J1', 'w_J2', 'w_J3', 'w_J4', 'w_J5'],
    'K': ['w_K1', 'w_K2', 'U'],
    'U': ['w_U1', 'w_U2', 'w_U3', 'X', 'Y', 'Z'],
    'X': ['w_X1', 'w_X2', 'w_X3'],
    'Y': ['w_Y1'], 'Z': ['w_Z1'],
    'L': ['w_L1', 'w_L2', 'w_L3', 'w_L4', 'w_L5', 'w_L6'],
    'N': ['w_N1', 'w_N2'],
    'F': ['w_F1', 'w_F2', 'w_F3', 'w_F4', 'w_F5', 'w_F6'],
    'G': ['w_G1', 'w_G2', 'w_G3'],
    'R2': ['w_R21'],
}
# A ve B'nin gerçek çocukları (denetim için)
GERCEK = {'A': ['w_A1', 'D', 'N'], 'B': ['N', 'F', 'G', 'w_B1', 'w_B2', 'w_B3']}
for k in ('E', 'C', 'H', 'D', 'J', 'K', 'U', 'X', 'Y', 'Z', 'L', 'N', 'F', 'G', 'R2'):
    GERCEK[k] = KID[k] if k != 'E' else ['A', 'B', 'C', 'H']
for p, ch in GERCEK.items():
    for c in ch:
        assert p in nodes[c]['ebeveyn'], (p, c)
for i, n in nodes.items():
    for p in n['ebeveyn']:
        assert i in GERCEK[p], (p, i)

WM, HM = 176, 66
WWK, HWK, GW, SATIR = 104, 54, 6, 4      # kelime kutusu, boşluk, satırda en çok kelime
GAP = 12
KAT_ARASI = 96


def kelime_mi(i): return i in nodes and nodes[i]['tur'] == W


def parcala(ch):
    """Çocuk listesini sıradaki parçalara böl: ardışık kelimeler tek kümedir."""
    out, cur = [], []
    for c in ch:
        if kelime_mi(c): cur.append(c)
        else:
            if cur: out.append(('k', cur)); cur = []
            out.append(('m', c))
    if cur: out.append(('k', cur))
    return out


def kume_gen(n):
    s = min(n, SATIR)
    return s * WWK + (s - 1) * GW


def genislik(i):
    ch = KID.get(i, [])
    kendi = WM if i not in ('AB',) else 0
    if not ch: return max(kendi, WM)
    toplam = 0
    ps = parcala(ch)
    for t, v in ps:
        toplam += (kume_gen(len(v)) if t == 'k' else genislik(v))
    toplam += GAP * (len(ps) - 1)
    return max(kendi, toplam)


X, KUME = {}, []        # X: düğüm merkez x; KUME: (ebeveyn, [kelimeler], x_sol, x_sag, katman)
LAYER = {}


def kat(i):
    if i in LAYER: return LAYER[i]
    p = nodes[i]['ebeveyn']
    LAYER[i] = 0 if not p else 1 + max(kat(x) for x in p)
    return LAYER[i]
for i in nodes: kat(i)


def yerlestir(i, sol):
    w = genislik(i)
    ch = KID.get(i, [])
    if not ch:
        X[i] = sol + w / 2
        return w
    ps = parcala(ch)
    toplam = sum((kume_gen(len(v)) if t == 'k' else genislik(v)) for t, v in ps) + GAP * (len(ps) - 1)
    cur = sol + (w - toplam) / 2
    kenarlar = []
    for t, v in ps:
        if t == 'k':
            gw = kume_gen(len(v))
            KUME.append((i, v, cur, cur + gw))
            for k, wid in enumerate(v):
                X[wid] = cur + (k % SATIR) * (WWK + GW) + WWK / 2
            kenarlar.append((cur, cur + gw))
            cur += gw + GAP
        else:
            gw = genislik(v)
            yerlestir(v, cur)
            kenarlar.append((cur, cur + gw) if v == 'AB' else (X[v] - WM / 2, X[v] + WM / 2))
            cur += gw + GAP
    if i != 'AB':
        X[i] = (kenarlar[0][0] + kenarlar[-1][1]) / 2
    return w

import itertools
def hesapla(sira):
    X.clear(); KUME.clear()
    KID['AB'] = sira
    x_cur = 24
    for r in ('E', 'R2'):
        w = genislik(r)
        yerlestir(r, x_cur)
        x_cur += w + 40
    # A ve B'nin yerleri, çocuklarının kutu aralığının ortası
    for p in ('A', 'B'):
        L, R = [], []
        for c in GERCEK[p]:
            if kelime_mi(c):
                L.append(X[c] - WWK / 2); R.append(X[c] + WWK / 2)
            else:
                L.append(X[c] - WM / 2); R.append(X[c] + WM / 2)
        X[p] = (min(L) + max(R)) / 2
    return abs(X['N'] - (X['A'] + X['B']) / 2)
A_oge = ['w_A1', 'D']
B_oge = ['F', 'G', 'w_B1', 'w_B2', 'w_B3']
en = None
for pa in itertools.permutations(A_oge):
    for pb in itertools.permutations(['F', 'G', 'KB']):
        bb = []
        for q in pb:
            bb += ['w_B1', 'w_B2', 'w_B3'] if q == 'KB' else [q]
        sira = list(pa) + ['N'] + bb
        d = hesapla(sira)
        if en is None or d < en[0]: en = (d, sira)
hesapla(en[1])
print('AB sırası', en[1], 'N sapması', round(en[0], 1))
# AB'nin bir kutusu yok; E'nin x'i: A ve H'nin merkez ortası değil, tüm çocuk aralığı
L, R = [], []
for c in ('A', 'B', 'C', 'H'):
    L.append(X[c] - WM / 2); R.append(X[c] + WM / 2)
X['E'] = (min(L) + max(R)) / 2

# katman içi sıra için sol kenarlara göre denetim
def kutu(i):
    if kelime_mi(i): return (X[i] - WWK / 2, X[i] + WWK / 2)
    return (X[i] - WM / 2, X[i] + WM / 2)
ihlal = []
for p, ch in GERCEK.items():
    cl = [c for c in ch]
    if not cl: continue
    Lc = LAYER[cl[0]]
    lo = min(kutu(c)[0] for c in cl); hi = max(kutu(c)[1] for c in cl)
    for o in nodes:
        if o in cl or LAYER[o] != Lc: continue
        a, b = kutu(o)
        if a < hi and b > lo: ihlal.append(('araya_giren', p, o))
    # çocuk ebeveynin bir altında mı
    for c in cl:
        if LAYER[c] != LAYER[p] + 1: ihlal.append(('katman', p, c))
for i, n in nodes.items():
    if len(n['ebeveyn']) > 1:
        ps = n['ebeveyn']
        lo = min(kutu(p)[0] for p in ps); hi = max(kutu(p)[1] for p in ps)
        for o in nodes:
            if o in ps or LAYER[o] != LAYER[ps[0]]: continue
            a, b = kutu(o)
            if a < hi and b > lo: ihlal.append(('ebeveyn_arasina_giren', i, o))
sapma = {i: round(X[i] - sum(X[p] for p in nodes[i]['ebeveyn']) / len(nodes[i]['ebeveyn']), 1)
         for i in nodes if len(nodes[i]['ebeveyn']) > 1}
ebv = {}
for p, ch in GERCEK.items():
    lo = min(kutu(c)[0] for c in ch); hi = max(kutu(c)[1] for c in ch)
    ebv[p] = round(X[p] - (lo + hi) / 2, 1)

# dikey
nl = max(LAYER.values()) + 1
sat_say = {}
for p, v, l, r in KUME:
    sat_say[LAYER[v[0]]] = max(sat_say.get(LAYER[v[0]], 1), (len(v) + SATIR - 1) // SATIR)
YT, yy = {}, 28
for L in range(nl):
    YT[L] = yy
    h = HM
    if L in sat_say: h = max(h, sat_say[L] * HWK + (sat_say[L] - 1) * GW + 12)
    yy += h + KAT_ARASI
H_TOT = yy - KAT_ARASI + 30
W_TOT = max(max(kutu(i)[1] for i in nodes), max(r for _, _, _, r in KUME)) + 24
def Y(i):
    return YT[LAYER[i]]

RENK = {'esas': '#f1d98a', 'a': '#cfe6ff', 'b': '#d8f0c6', 'c': '#ffd9b8', 'h': '#f2cfe8', 'ab': '#cfeee6', 'dis': '#e3e3e3'}
RENK_K = {'a': '#eaf4ff', 'b': '#eef9e6', 'c': '#fff0e1', 'h': '#fbe9f5', 'ab': '#e6f8f4', 'dis': '#f3f3f3', 'esas': '#fbf0c8'}
esc = html.escape


def sar(t, n=24):
    w = t.split(); out = []; cur = ''
    for k in w:
        if len(cur) + len(k) + 1 > n and cur: out.append(cur); cur = k
        else: cur = (cur + ' ' + k).strip()
    if cur: out.append(cur)
    return out

S = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_TOT:.0f}" height="{H_TOT:.0f}" viewBox="0 0 {W_TOT:.0f} {H_TOT:.0f}" font-family="Amiri, Noto Naskh Arabic, DejaVu Sans, sans-serif">',
     '<rect width="100%" height="100%" fill="#fffdf6"/>']
def egri(x1, y1, x2, y2, col, sw):
    ym = (y1 + y2) / 2
    return f'<path d="M{x1:.1f},{y1:.1f} C{x1:.1f},{ym:.1f} {x2:.1f},{ym:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{col}" stroke-width="{sw}"/>'
# mana kenarları
for i, n in nodes.items():
    if n['tur'] != M: continue
    for p in n['ebeveyn']:
        S.append(egri(X[p], Y(p) + HM, X[i], Y(i), '#9a8a5c', 1.7))
# kelime kümeleri
for p, v, l, r in KUME:
    L = LAYER[v[0]]
    rows = (len(v) + SATIR - 1) // SATIR
    hh = rows * HWK + (rows - 1) * GW + 8
    reals = [q for q in nodes if False]
    gp = p
    if p == 'AB':
        # küme hangi gerçek ebeveyne ait
        gp = 'A' if v[0] == 'w_A1' else 'B'
    xp = X[gp]
    S.append(f'<rect x="{l-4:.1f}" y="{YT[L]-4:.1f}" width="{r-l+8:.1f}" height="{hh:.1f}" rx="9" fill="#f2ecd8" fill-opacity=".55" stroke="#d6caa0" stroke-width="1"/>')
    S.append(egri(xp, Y(gp) + HM, (l + r) / 2, YT[L] - 4, '#c9bf9d', 1.1))
# sebep etiketleri
for i, n in nodes.items():
    if n['tur'] == M and n['sebep']:
        p = n['ebeveyn']
        x1 = sum(X[q] for q in p) / len(p)
        y1 = max(Y(q) + HM for q in p)
        xm = X[i]
        ym = y1 + (Y(i) - y1) * (0.64 if len(p) == 1 else 0.45)
        sat = sar(n['sebep'], 26)
        h = 12 * len(sat) + 4
        S.append(f'<rect x="{xm-86:.1f}" y="{ym-h/2:.1f}" width="172" height="{h}" rx="5" fill="#fffdf6" fill-opacity="0.94"/>')
        for k, t in enumerate(sat):
            S.append(f'<text x="{xm:.1f}" y="{ym-h/2+11+12*k:.1f}" font-size="10.5" text-anchor="middle" fill="#7a5a14" font-style="italic">{esc(t)}</text>')
# kutular
for i, n in nodes.items():
    if n['tur'] == M:
        a, b = kutu(i); yt = Y(i)
        S.append(f'<rect x="{a:.1f}" y="{yt:.1f}" width="{WM}" height="{HM}" rx="9" fill="{RENK[n["renk"]]}" stroke="#7a6a3c" stroke-width="1.4"/>')
        ls = sar(n['metin'], 24)
        for k, t in enumerate(ls):
            S.append(f'<text x="{X[i]:.1f}" y="{yt+(HM-13.5*len(ls))/2+10+13.5*k:.1f}" font-size="12.5" font-weight="700" text-anchor="middle" fill="#2b2410">{esc(t)}</text>')
for p, v, l, r in KUME:
    L = LAYER[v[0]]
    for k, wid in enumerate(v):
        n = nodes[wid]
        a = X[wid] - WWK / 2
        yt = YT[L] + (k // SATIR) * (HWK + GW)
        gp = ('A' if v[0] == 'w_A1' else 'B') if p == 'AB' else p
        S.append(f'<rect x="{a:.1f}" y="{yt:.1f}" width="{WWK}" height="{HWK}" rx="7" fill="{RENK_K.get(nodes[gp]["renk"], "#fff")}" stroke="#a89a70" stroke-width="1"/>')
        S.append(f'<text x="{X[wid]:.1f}" y="{yt+21:.1f}" font-size="19" text-anchor="middle" fill="#1a1a1a" direction="rtl">{esc(n["ar"])}</text>')
        S.append(f'<text x="{X[wid]:.1f}" y="{yt+36:.1f}" font-size="10" text-anchor="middle" fill="#222">{esc(n["tr"])}</text>')
        tg = n['tag'] + (' ' + n['kuran'] if n['kuran'] else '')
        S.append(f'<text x="{X[wid]:.1f}" y="{yt+49:.1f}" font-size="8.8" text-anchor="middle" fill="#777">{esc(tg)}</text>')
S.append('</svg>')
(HERE / 'kafes2.svg').write_text('\n'.join(S), encoding='utf-8')
rapor = dict(dugum=len(nodes), mana_dugumu=sum(1 for n in nodes.values() if n['tur'] == M),
             kelime_kutusu=sum(1 for n in nodes.values() if n['tur'] == W), katman=nl,
             ihlal=ihlal, birlesik_cocuk_sapma=sapma,
             ebeveyn_ortadan_en_buyuk_sapma=max(abs(v) for v in ebv.values()),
             ebeveyn_sapma=ebv, genislik=round(W_TOT), yukseklik=round(H_TOT))
(HERE / 'kafes2_rapor.json').write_text(json.dumps(rapor, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps(rapor, ensure_ascii=False, indent=1))
