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
def kare(oge, x, y, w, h, sag=False):
    """Kareleştirilmiş ağaç haritası (squarified treemap): [(anahtar, alan)] -> {anahtar: (x, y, w, h)}"""
    X0, W0 = x, w
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
    if sag: o = {k: (2 * X0 + W0 - v[0] - v[2], v[1], v[2], v[3]) for k, v in o.items()}
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
KH = HERE.parent.parent
def izgara(n, x, y, w, h, sag=False):
    if n == 0: return []
    best = None
    for co in range(1, n + 1):
        ro = math.ceil(n / co); cs = min(w / co, h / ro)
        if best is None or cs > best[0]: best = (cs, co, ro)
    cs, co, ro = best; ox = x + (w - co * cs) / 2; oy = y + (h - ro * cs) / 2
    return [((ox + (co - 1 - j % co) * cs) if sag else (ox + (j % co) * cs), oy + (j // co) * cs, cs) for j in range(n)]
KEL = json.load(open(KH / 'kaynak' / 'sozluk' / 'kelimeler.json', encoding='utf-8'))
ILK = collections.defaultdict(list)
for e in KEL:
    if e.get('ilk'): ILK[e['ilk']].append(e['kelime'])
SUR = []
BT = (KH / 'kaynak' / 'sure_bolumlemeleri' / 'sure_bolumlemeleri.md').read_text(encoding='utf-8')
BK = {}
for m in re.finditer(r'^## (\d+)\. .*?$(.*?)(?=^## \d+\. |\Z)', BT, re.M | re.S):
    z = re.search(r'\*\*A\. Kitap verisi.*?\*\*(.*?)(?=\n\*\*B\.|\Z)', m.group(2), re.S)
    BK[int(m.group(1))] = [(x.strip(), int(b), int(c or b)) for x, b, c in re.findall(r'^- (.*?) \(Âyet (\d+)(?:-(\d+))?\)\s*$', z.group(1), re.M)]
for s in range(1, 115):
    d = next(KH.glob('sureler/%03d-*/sure.md' % s)); t = d.read_text(encoding='utf-8')
    adi = re.search(r'^# S\d+ · (.*)$', t, re.M).group(1); na = len(json.load(open(KH / 'kaynak' / 'sure' / f'{s}.json', encoding='utf-8'))['verses'])
    KIS = [(x + (' (%d)' % b if b == c else ' (%d-%d)' % (b, c)), list(range(b, c + 1))) for x, b, c in BK[s]]
    assert sorted(a for _, L in KIS for a in L) == list(range(1, na + 1)), s
    SUR.append((s, adi, na, KIS))
QX, QY, QW, QH = 1900, 40, 1720, 1720
QR = kare([(s[0], s[2] + 8) for s in SUR], QX, QY, QW, QH, True)
QS, QK, QA, QW_ = [], [], [], []
for s, adi, na, KIS in SUR:
    x, y, w, h = QR[s]; x += 3; y += 3; w -= 6; h -= 6; tb = min(30.0, max(3.0, min(w, h) * 0.12))
    QS.append([round(x, 2), round(y, 2), round(w, 2), round(h, 2), '%d · %s' % (s, adi), round(tb, 2)])
    KR = kare([(j, len(k[1])) for j, k in enumerate(KIS)], x + 1, y + tb, w - 2, h - tb - 1, True)
    for j, (kad, ay) in enumerate(KIS):
        kx, ky, kw, kh = KR[j]; kx += 0.8; ky += 0.8; kw -= 1.6; kh -= 1.6; kt = min(14.0, max(1.0, min(kw, kh) * 0.1))
        QK.append([round(kx, 3), round(ky, 3), round(kw, 3), round(kh, 3), kad, round(kt, 3), s])
        for (ax, ay_, cs), a in zip(izgara(len(ay), kx, ky + kt, kw, kh - kt, True), ay):
            g = cs * 0.04; ax += g; ay_ += g; c2 = cs - 2 * g; at = c2 * 0.16
            QA.append([round(ax, 3), round(ay_, 3), round(c2, 3), '%d:%d' % (s, a), round(at, 3)])
            W_ = ILK.get('%d:%d' % (s, a), [])
            for (wx, wy, wc), k in zip(izgara(len(W_), ax, ay_ + at, c2, c2 - at, True), W_):
                QW_.append([round(wx + wc * 0.05, 4), round(wy + wc * 0.05, 4), round(wc * 0.9, 4), k])
lej = ''.join(f'<span><i style="background:{RENK[u]}"></i>{a}</span>' for u, (a, _) in enumerate(KA.AGAC))
VERI = json.dumps({'V': VER, 'H': HUC, 'B': [], 'K': KAVS, 'R': RENK, 'O': ODAS, 'BL': BLK, 'QS': QS, 'QK': QK, 'QA': QA, 'QW': QW_}, ensure_ascii=False, separators=(',', ':'))
HTML = (HERE / 'kavram_uzayi_sablon.html').read_text(encoding='utf-8').replace('__LEJ__', lej).replace('__VERI__', VERI).replace('__V__', __import__('hashlib').md5((HERE/'mustak_cizim.js').read_bytes()).hexdigest()[:8])
(HERE / 'kavram_uzayi.html').write_text(HTML, encoding='utf-8')
if '--png' in sys.argv:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'); g = b.new_page(viewport={'width': 1500, 'height': 1560}, device_scale_factor=2)
        g.goto((HERE / 'kavram_uzayi.html').as_uri()); g.wait_for_timeout(1500); g.screenshot(path=str(HERE / 'kavram_uzayi.png')); b.close()
