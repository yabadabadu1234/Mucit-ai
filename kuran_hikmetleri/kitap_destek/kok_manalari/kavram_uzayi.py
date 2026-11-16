"""Tek komut: python3 kavram_uzayi.py [--png]
Voronoi kavram uzayı (galeri usulü 43). Her nokta bir kökün bir ASLIDIR; kavramı kategori/*.txt'den (elle) gelir.
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
P = P - P.min(0); P = P / P.max() * 1600 + 100
sim = Z @ Z.T; np.fill_diagonal(sim, -1)
ad = lambda i: N[i][0] + ('¹²³⁴⁵⁶'[N[i][1]] if N[i][5] > 1 else '')
H = {}
for u, L in KA.AGAC:
    H[u] = {a: [{'ad': b['ad'], 'asillar': [ad(i) + ' ' + N[i][2] for i in b['uyeler']]} for b in BOL if b['kavram'] == c] for c, a in L}
json.dump({'hiyerarsi': H, 'asillar': {ad(i): {'kok': N[i][0], 'asil': N[i][2], 'kavram': KA.KOD[N[i][3]][1], 'ust': KA.KOD[N[i][3]][0], 'bolge': BOL[bolge[i]]['ad'],
           'xy': [round(float(P[i, 0]), 1), round(float(P[i, 1]), 1)], 'komsu': [ad(j) for j in np.argsort(-sim[i])[:4]]} for i in range(len(N))}},
          open(HERE / 'KAVRAM_UZAYI.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
RENK = ['#7a7a7a', '#5a7a2a', '#b3541e', '#2f6fb3', '#8a3fa0', '#a0304a', '#2c8c7c', '#b8860b', '#6b5a3a']
cer = box(40, 40, 1760, 1760)
Vo = Voronoi(np.vstack([P, [[-5000, -5000], [-5000, 7000], [7000, -5000], [7000, 7000]]]))
from shapely.geometry import MultiPoint
kab = MultiPoint([tuple(x) for x in P]).convex_hull.buffer(22)
hucre = []
for i in range(len(N)):
    r = Vo.regions[Vo.point_region[i]]; poly = Polygon([Vo.vertices[v] for v in r]).intersection(cer)
    hucre.append(poly.intersection(kab))
def halka(g):
    if g.geom_type != 'Polygon': g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
    return [round(c, 1) for xy in g.exterior.coords for c in xy]
def halkalar(g):
    return [[round(c, 1) for xy in q.exterior.coords for c in xy] for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon']
from shapely.geometry import Point
IC = [max(4.0, hucre[i].exterior.distance(Point(P[i, 0], P[i, 1]))) if hucre[i].geom_type == 'Polygon' else 8.0 for i in range(len(N))]
HUC = [[halka(hucre[i]), ust_i[N[i][3]], round(0.15 + 0.22 * ((bolge[i] * 37) % 7) / 6, 2)] for i in range(len(N))]
BOLS = [halkalar(unary_union([hucre[i] for i in b['uyeler']])) for b in BOL]
KAVS = [[halkalar(unary_union([hucre[i] for i in ix_of[c]])), KA.KOD[c][1], [round(float(x), 1) for x in P[ix_of[c]].mean(0)]] for c in KODLAR]
VER = {ad(i): [float(P[i, 0]), float(P[i, 1]), KA.KOD[N[i][3]][1], BOL[bolge[i]]['ad'], N[i][2], [ad(j) for j in np.argsort(-sim[i])[:4]], N[i][0], i, round(IC[i], 2), A[N[i][0]][N[i][1]]] for i in range(len(N))}
lej = ''.join(f'<span><i style="background:{RENK[u]}"></i>{a}</span>' for u, (a, _) in enumerate(KA.AGAC))
VERI = json.dumps({'V': VER, 'H': HUC, 'B': BOLS, 'K': KAVS, 'R': RENK}, ensure_ascii=False, separators=(',', ':'))
HTML = (HERE / 'kavram_uzayi_sablon.html').read_text(encoding='utf-8').replace('__LEJ__', lej).replace('__VERI__', VERI).replace('__V__', __import__('hashlib').md5((HERE/'mustak_cizim.js').read_bytes()).hexdigest()[:8])
(HERE / 'kavram_uzayi.html').write_text(HTML, encoding='utf-8')
if '--png' in sys.argv:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'); g = b.new_page(viewport={'width': 1500, 'height': 1560}, device_scale_factor=2)
        g.goto((HERE / 'kavram_uzayi.html').as_uri()); g.wait_for_timeout(1500); g.screenshot(path=str(HERE / 'kavram_uzayi.png')); b.close()
