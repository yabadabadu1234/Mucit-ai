"""Tek komut: python3 kavram_uzayi.py [--png]
Kategori uzayı (F 3-I 380): her mevzu bir dikdörtgen oda, bölgeler oda içinde bloklar, çekirdekler blokta ızgara. Her nokta bir kökün bir ASLIDIR; kavramı kategori/*.txt'den (elle) gelir.
Yakın kavramlar yan yana, kavram içinde manası yakın asıllar komşu. Hiyerarşi: üst kategori > kavram > bölge > asıl."""
import json, math, re, sys, pathlib, collections
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE, MDS
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from agac_oku import oku
import kategori_agaci as KA
HERE = pathlib.Path(__file__).resolve().parent
A = oku(); KT = KA.oku()
DUR = set('bir ve ile için gibi veya şey şeyin olmak etmek yapmak kılmak vermek'.split())
def metin(n): return n['mana'] + ' ' + ' '.join(metin(c) for c in n['turev'])
N = []  # (kök, asıl sırası, asıl, kod, metin)
for k, L in A.items():
    for i, n in enumerate(L): N.append((k, i, n['mana'], KT[k][i], metin(n), len(L)))
tok = lambda s: [w for w in re.findall(r"[a-zçğıöşüâîû']+", s.lower()) if w not in DUR and len(w) > 2]
X = TfidfVectorizer(tokenizer=tok, ngram_range=(1, 2), min_df=2, sublinear_tf=True, token_pattern=None).fit([n[4] for n in N])
V = X.transform([n[4] for n in N]); kel = np.array(X.get_feature_names_out())
Z = TruncatedSVD(96, random_state=0).fit_transform(V); Z /= np.linalg.norm(Z, axis=1, keepdims=True) + 1e-9
KODLAR = [c for _, L in KA.AGAC for c, _ in L]
ix_of = {c: [i for i, n in enumerate(N) if n[3] == c] for c in KODLAR}
mer = np.array([Z[ix_of[c]].mean(0) for c in KODLAR]); mer /= np.linalg.norm(mer, axis=1, keepdims=True)
ust_i = {c: u for u, (_, L) in enumerate(KA.AGAC) for c, _ in L}
D = np.clip(1 - mer @ mer.T, 0, None) + 0.35 * np.array([[ust_i[a] != ust_i[b] for b in KODLAR] for a in KODLAR]); np.fill_diagonal(D, 0)
M = MDS(2, dissimilarity='precomputed', random_state=0, normalized_stress='auto').fit_transform(D)
say = np.array([len(ix_of[c]) for c in KODLAR]); R = 7.5 * np.sqrt(say) + 16
M = M / np.abs(M).max() * 700
R = R * 0.9
for _ in range(500):
    for a in range(len(M)):
        for b in range(a + 1, len(M)):
            d = M[b] - M[a]; n = np.linalg.norm(d) + 1e-9; g = R[a] + R[b] - n
            if g > 0: M[a] -= d / n * g / 2; M[b] += d / n * g / 2
    M *= 0.995
P = np.zeros((len(N), 2)); bolge = [None] * len(N); BOL = []
for ci, c in enumerate(KODLAR):
    ix = ix_of[c]; Zi = Z[ix] + 1e-6
    L = TSNE(2, perplexity=min(20, len(ix) - 2), init='pca', random_state=0, metric='cosine').fit_transform(Zi) if len(ix) > 5 else np.array([[math.cos(t), math.sin(t)] for t in np.linspace(0, 2 * math.pi, len(ix), endpoint=False)])
    L = L - L.mean(0); P[ix] = M[ci] + L / (np.linalg.norm(L, axis=1).max() + 1e-9) * (R[ci] - 8)
    kb = max(1, round(len(ix) / 15))
    lab = AgglomerativeClustering(kb, metric='cosine', linkage='average').fit_predict(Zi) if kb > 1 else np.zeros(len(ix), int)
    for b in range(kb):
        uy = [ix[j] for j in range(len(ix)) if lab[j] == b]
        w = np.asarray(V[uy].sum(0)).ravel(); BOL.append({'kavram': c, 'ad': ', '.join(kel[np.argsort(-w)[:3]]), 'uyeler': uy})
        for i in uy: bolge[i] = len(BOL) - 1
def kare(oge, x, y, w, h):
    """Kareleştirilmiş ağaç haritası (squarified treemap): [(anahtar, alan)] -> {anahtar: (x, y, w, h)}"""
    oge = [o for o in oge if o[1] > 0]; top = sum(a for _, a in oge); o = {}
    oge = [(k, a * w * h / top) for k, a in oge]
    def kotu(sira, kenar):
        s_ = sum(a for _, a in sira); return max(max(kenar * kenar * a / s_ / s_, s_ * s_ / kenar / kenar / a) for _, a in sira)
    while oge:
        kenar = min(w, h); sira = [oge.pop(0)]
        while oge and kotu(sira + [oge[0]], kenar) <= kotu(sira, kenar): sira.append(oge.pop(0))
        s_ = sum(a for _, a in sira)
        if w >= h:
            ew = s_ / h; yy = y
            for k, a_ in sira: o[k] = (x, yy, ew, a_ / ew); yy += a_ / ew
            x += ew; w -= ew
        else:
            eh = s_ / w; xx = x
            for k, a_ in sira: o[k] = (xx, y, a_ / eh, eh); xx += a_ / eh
            y += eh; h -= eh
    return o
UST = [(u, sum(len(ix_of[c]) for c, _ in L)) for u, (_, L) in enumerate(KA.AGAC)]
UR = kare(sorted(UST, key=lambda t: -t[1]), 40, 40, 1720, 1720)
ODA = {}
for u, (_, L) in enumerate(KA.AGAC):
    x, y, w, h = UR[u]; ODA.update(kare(sorted([(c, len(ix_of[c])) for c, _ in L], key=lambda t: -t[1]), x + 4, y + 4, w - 8, h - 8))
P = np.zeros((len(N), 2)); IC = [8.0] * len(N); hucre = [None] * len(N); BLK = []; ODAS = []
bas = lambda w: min(26.0, max(10.0, w * 0.07))
for c in KODLAR:
    x, y, w, h = ODA[c]; x += 5; y += 5; w -= 10; h -= 10; ODAS.append([round(x, 1), round(y, 1), round(w, 1), round(h, 1), ust_i[c], KA.KOD[c][1]])
    tb = bas(w); bl = [b_ for b_ in range(len(BOL)) if BOL[b_]['kavram'] == c]
    BR = kare(sorted([(b_, len(BOL[b_]['uyeler'])) for b_ in bl], key=lambda t: -t[1]), x + 3, y + tb, w - 6, h - tb - 3)
    for b_, (bx, by, bw, bh) in BR.items():
        bx += 3; by += 3; bw -= 6; bh -= 6; bt = min(12.0, max(5.0, bw * 0.05)); BLK.append([round(bx, 1), round(by, 1), round(bw, 1), round(bh, 1), BOL[b_]['ad'], ust_i[c], round(bt, 1)])
        uy = BOL[b_]['uyeler']; uy = sorted(uy, key=lambda i: (-Z[i, 0]))
        n = len(uy); ih = bh - bt; best = None
        for co in range(1, n + 1):
            ro = math.ceil(n / co); cs = min(bw / co, ih / ro)
            if best is None or cs > best[0]: best = (cs, co, ro)
        cs, co, ro = best; ox = bx + (bw - co * cs) / 2; oy = by + bt + (ih - ro * cs) / 2
        for j, i in enumerate(uy):
            cx = ox + (j % co + 0.5) * cs; cy = oy + (j // co + 0.5) * cs
            P[i] = (cx, cy); IC[i] = cs / 2; hucre[i] = box(cx - cs / 2, cy - cs / 2, cx + cs / 2, cy + cs / 2)
sim = Z @ Z.T; np.fill_diagonal(sim, -1)
ad = lambda i: N[i][0] + ('¹²³⁴⁵⁶'[N[i][1]] if N[i][5] > 1 else '')
H = {}
for u, L in KA.AGAC:
    H[u] = {a: [{'ad': b['ad'], 'asillar': [ad(i) + ' ' + N[i][2] for i in b['uyeler']]} for b in BOL if b['kavram'] == c] for c, a in L}
json.dump({'hiyerarsi': H, 'asillar': {ad(i): {'kok': N[i][0], 'asil': N[i][2], 'kavram': KA.KOD[N[i][3]][1], 'ust': KA.KOD[N[i][3]][0], 'bolge': BOL[bolge[i]]['ad'],
           'xy': [round(float(P[i, 0]), 1), round(float(P[i, 1]), 1)], 'komsu': [ad(j) for j in np.argsort(-sim[i])[:4]]} for i in range(len(N))}},
          open(HERE / 'KAVRAM_UZAYI.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
RENK = ['#7a7a7a', '#5a7a2a', '#b3541e', '#2f6fb3', '#8a3fa0', '#a0304a', '#2c8c7c', '#b8860b', '#6b5a3a']
def halka(g): return [round(c, 1) for xy in g.exterior.coords for c in xy]
HUC = [[halka(hucre[i]), ust_i[N[i][3]], 0.3] for i in range(len(N))]
KAVS = [[[], o[5], [o[0] + o[2] / 2, o[1] + o[3] / 2, o[2] * 0.96, o[3] * 0.9], [o[0] + o[2] / 2, o[1] + bas(o[2]) / 2 + 1, o[2] * 0.96, bas(o[2]) * 0.9]] for o in ODAS]
VER = {ad(i): [float(P[i, 0]), float(P[i, 1]), KA.KOD[N[i][3]][1], BOL[bolge[i]]['ad'], N[i][2], [ad(j) for j in np.argsort(-sim[i])[:4]], N[i][0], i, round(IC[i], 2), A[N[i][0]][N[i][1]]] for i in range(len(N))}
EB = json.load(open(HERE / 'lugat_ebat.json', encoding='utf-8'))
R0 = 0.93 * float(np.median(IC)); SJ = 0.92 * 414 / (2 * R0); C2 = 9 / (11.5 * SJ)
def raf(oge, gen, ara):
    x = y = sh = 0; yer = {}; mx = 0
    for k, w, h in oge:
        if x > 0 and x + w > gen: x = 0; y += sh + ara; sh = 0
        yer[k] = (x, y); x += w + ara; sh = max(sh, h); mx = max(mx, x - ara)
    return yer, mx, y + sh
B2 = {}; HC = {}
for i in range(len(N)):
    r = 0.93 * IC[i]; e = EB.get(N[i][0]); pd = r * 0.12
    w, h = (max(2 * r, e[1] * C2 + pd), max(2 * r, e[2] * C2 + pd)) if e else (2 * r, 2 * r)
    HC[i] = (w, h, e[0] if e else 0)
ARA = R0 * 0.5; BLK2 = []; ODA2 = []; P2 = {}
oda_kut = {}
for c in KODLAR:
    bl = [b_ for b_ in range(len(BOL)) if BOL[b_]['kavram'] == c]; bk = []
    for b_ in bl:
        uy = sorted(BOL[b_]['uyeler'], key=lambda i: (-Z[i, 0])); top = sum(HC[i][0] * HC[i][1] for i in uy)
        gen = max(max(HC[i][0] for i in uy), math.sqrt(top) * 1.3)
        yer, bw, bh = raf([(i, HC[i][0], HC[i][1]) for i in uy], gen, ARA)
        bt = R0 * 0.9; bk.append((b_, bw + 2 * ARA, bh + bt + 2 * ARA, yer, bt))
    top = sum(w * h for _, w, h, _, _ in bk); gen = max(max(w for _, w, _, _, _ in bk), math.sqrt(top) * 1.2)
    yer, rw, rh = raf([(b_, w, h) for b_, w, h, _, _ in bk], gen, ARA * 2)
    tb = R0 * 2.2; oda_kut[c] = (rw + 4 * ARA, rh + tb + 4 * ARA, bk, yer, tb)
SIRA = [c for _, L in KA.AGAC for c, _ in L]
top = sum(oda_kut[c][0] * oda_kut[c][1] for c in SIRA); gen = max(max(oda_kut[c][0] for c in SIRA), math.sqrt(top) * 1.0)
oyer, MW, MH = raf([(c, oda_kut[c][0], oda_kut[c][1]) for c in SIRA], gen, ARA * 6)
K2 = []
for c in SIRA:
    ox, oy = oyer[c]; rw, rh, bk, yer, tb = oda_kut[c]; ODA2.append([round(ox, 1), round(oy, 1), round(rw, 1), round(rh, 1), ust_i[c], KA.KOD[c][1]])
    K2.append([ox + rw / 2, oy + tb / 2, rw * 0.96, tb * 0.8])
    for b_, bw, bh, cyer, bt in bk:
        bx, by = yer[b_]; bx += ox + 2 * ARA; by += oy + tb + 2 * ARA
        BLK2.append([round(bx, 1), round(by, 1), round(bw, 1), round(bh, 1), BOL[b_]['ad'], ust_i[c], round(bt, 1)])
        for i, (cx, cy) in cyer.items():
            w, h, wb = HC[i]; P2[i] = [round(bx + ARA + cx + w / 2, 1), round(by + bt + ARA + cy + h / 2, 1), round(w, 2), round(h, 2), wb]
for i in range(len(N)): VER[ad(i)] += P2[i]
lej = ''.join(f'<span><i style="background:{RENK[u]}"></i>{a}</span>' for u, (a, _) in enumerate(KA.AGAC))
VERI = json.dumps({'V': VER, 'H': HUC, 'B': [], 'K': KAVS, 'R': RENK, 'O': ODAS, 'BL': BLK, 'O2': ODA2, 'BL2': BLK2, 'K2': K2, 'C2': C2}, ensure_ascii=False, separators=(',', ':'))
HTML = (HERE / 'kavram_uzayi_sablon.html').read_text(encoding='utf-8').replace('__LEJ__', lej).replace('__VERI__', VERI).replace('__V__', __import__('hashlib').md5((HERE/'mustak_cizim.js').read_bytes()).hexdigest()[:8])
(HERE / 'kavram_uzayi.html').write_text(HTML, encoding='utf-8')
if '--png' in sys.argv:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'); g = b.new_page(viewport={'width': 1500, 'height': 1560}, device_scale_factor=2)
        g.goto((HERE / 'kavram_uzayi.html').as_uri()); g.wait_for_timeout(1500); g.screenshot(path=str(HERE / 'kavram_uzayi.png')); b.close()
