"""Tek komut: python3 kavram_uzayi.py [--png]
43 kavram uzayı (mana_tasnif.orta) içinde kökleri mana yakınlığına göre yerleştirir; her kavram uzayının içinde
mana bölgeleri çıkarır ve hiyerarşiyi (üst kategori > kavram uzayı > bölge > kök) KAVRAM_UZAYI.json'a yazar."""
import json, glob, math, re, sys, pathlib, collections
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial import ConvexHull
from agac_oku import oku
HERE = pathlib.Path(__file__).resolve().parent
KOK = HERE.parents[1] / 'kelime_kaydi/kuranda_var/kokler'
AD = {'adj.all':'sıfatlar','adj.pert':'nisbet sıfatları','adv.all':'zarflar','noun.Tops':'en üst kavramlar','noun.act':'fiil ve amel',
'noun.animal':'hayvanlar','noun.artifact':'yapılmış şeyler','noun.attribute':'vasıflar','noun.body':'beden','noun.cognition':'idrak ve ilim',
'noun.communication':'söz ve haber','noun.event':'hâdiseler','noun.feeling':'hisler','noun.food':'yiyecek','noun.group':'topluluklar',
'noun.location':'mekânlar','noun.object':'tabiî cisimler','noun.person':'insanlar','noun.phenomenon':'tabiat hâdiseleri','noun.plant':'bitkiler',
'noun.possession':'mülk ve mal','noun.process':'süreçler','noun.quantity':'miktar ve sayı','noun.relation':'münasebetler','noun.shape':'şekiller',
'noun.state':'hâller','noun.substance':'maddeler','noun.time':'zaman','verb.body':'beden fiilleri','verb.change':'değişme',
'verb.cognition':'düşünme fiilleri','verb.communication':'söyleme fiilleri','verb.competition':'çekişme ve savaş','verb.consumption':'yeme içme',
'verb.contact':'temas ve dokunma','verb.creation':'yapma ve yaratma','verb.emotion':'duygu fiilleri','verb.motion':'hareket',
'verb.perception':'algılama','verb.possession':'sahip olma ve verme','verb.social':'içtimaî fiiller','verb.stative':'durum fiilleri','verb.weather':'hava hâlleri'}
DUR = set('bir ve ile da de ki şey şeyin bir bu olmak etmek yapmak vermek kılmak gibi veya ya bu o ile için'.split())
A = oku()
def metin(L): return ' '.join(n['mana'] + ' ' + metin(n['turev']) for n in L)
def asil(L): return [n['mana'] for n in L]
K, T, UST, ORTA = [], [], [], []
for k, L in A.items():
    m = (json.load(open(KOK / f'{k}.json', encoding='utf-8')).get('mana_tasnif') or {})
    K.append(k); T.append(metin(L)); UST.append(m.get('ust') or 'tasnifsiz'); ORTA.append(m.get('orta') or 'tasnifsiz')
tok = lambda s: [w for w in re.findall(r"[a-zçğıöşüâîû']+", s.lower()) if w not in DUR and len(w) > 2]
X = TfidfVectorizer(tokenizer=tok, ngram_range=(1, 2), min_df=2, sublinear_tf=True, token_pattern=None).fit(T)
V = X.transform(T); kel = np.array(X.get_feature_names_out())
Z = TruncatedSVD(96, random_state=0).fit_transform(V); Z /= np.linalg.norm(Z, axis=1, keepdims=True) + 1e-9
orta_ler = sorted(set(ORTA)); oi = {o: i for i, o in enumerate(orta_ler)}
from sklearn.manifold import MDS
mer = np.array([Z[[i for i in range(len(K)) if ORTA[i] == o]].mean(0) for o in orta_ler]); mer /= np.linalg.norm(mer, axis=1, keepdims=True)
D = np.clip(1 - mer @ mer.T, 0, None); np.fill_diagonal(D, 0)
M = MDS(2, dissimilarity='precomputed', random_state=0, normalized_stress='auto').fit_transform(D)
say = np.array([sum(1 for x in ORTA if x == o) for o in orta_ler]); R = 9 * np.sqrt(say) + 18
M = M / np.abs(M).max() * 700
for _ in range(400):
    for a in range(len(M)):
        for b in range(a + 1, len(M)):
            d = M[b] - M[a]; n = np.linalg.norm(d) + 1e-9; g = R[a] + R[b] + 12 - n
            if g > 0: M[a] -= d / n * g / 2; M[b] += d / n * g / 2
    M *= 0.995
P = np.zeros((len(K), 2))
for oi_, o in enumerate(orta_ler):
    ix = [i for i in range(len(K)) if ORTA[i] == o]
    if len(ix) > 5: L = TSNE(2, perplexity=min(20, len(ix) - 2), init='pca', random_state=0, metric='cosine').fit_transform(Z[ix] + 1e-6)
    else: L = np.array([[math.cos(t), math.sin(t)] for t in np.linspace(0, 2 * math.pi, len(ix), endpoint=False)]) if len(ix) > 1 else np.zeros((1, 2))
    L = L - L.mean(0); r = np.linalg.norm(L, axis=1).max() + 1e-9
    yon = M[oi_] / (np.linalg.norm(M[oi_]) + 1e-9)
    P[ix] = M[oi_] + L / r * (R[oi_] - 10)
P = P - P.min(0) + 80; P = P / P.max() * 1640 + 80
sim = Z @ Z.T; np.fill_diagonal(sim, -1)
komsu = {K[i]: [K[j] for j in np.argsort(-sim[i])[:4]] for i in range(len(K))}
H, bolgeler = {}, []
for o in orta_ler:
    ix = [i for i in range(len(K)) if ORTA[i] == o]
    n = len(ix); kb = max(1, round(n / 14))
    lab = AgglomerativeClustering(kb, metric='cosine', linkage='average').fit_predict(Z[ix] + 1e-6) if n > 2 and kb > 1 else np.zeros(n, int)
    for b in range(kb):
        uy = [ix[j] for j in range(n) if lab[j] == b]
        if not uy: continue
        w = np.asarray(V[uy].sum(0)).ravel(); ad = ', '.join(kel[np.argsort(-w)[:3]])
        bolgeler.append({'orta': o, 'ad': ad, 'kokler': [K[i] for i in uy]})
    ust = collections.Counter(UST[i] for i in ix).most_common(1)[0][0]
    H.setdefault(ust, {})[o] = {'ad': AD.get(o, o), 'bolgeler': [b for b in bolgeler if b['orta'] == o]}
bk = {k: bi for bi, b in enumerate(bolgeler) for k in b['kokler']}
json.dump({'hiyerarsi': H, 'kokler': {K[i]: {'xy': [round(float(P[i, 0]), 1), round(float(P[i, 1]), 1)], 'ust': UST[i], 'orta': ORTA[i], 'bolge': bolgeler[bk[K[i]]]['ad'],
           'asil': asil(A[K[i]]), 'komsu': komsu[K[i]]} for i in range(len(K))}}, open(HERE / 'KAVRAM_UZAYI.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
RENK = ['#b3541e', '#2f6fb3', '#3f7f3a', '#8a3fa0', '#b8860b', '#2c8c7c', '#a0304a', '#5a6b2a', '#6d5bd0', '#c06a00', '#777']
ustler = sorted(set(UST)); ur = {u: RENK[i % len(RENK)] for i, u in enumerate(ustler)}
def zarf(pts, pad):
    pts = np.array(pts)
    if len(pts) < 3: c = pts.mean(0); return [(c[0] + pad * math.cos(a), c[1] + pad * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12)]
    h = pts[ConvexHull(pts).vertices]; c = h.mean(0)
    return [tuple(c + (p - c) * (1 + pad / (np.linalg.norm(p - c) + 1e-9))) for p in h]
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
cer = box(40, 40, 1760, 1760)
V_ = Voronoi(np.vstack([P, [[-5000, -5000], [-5000, 7000], [7000, -5000], [7000, 7000]]]))
hucre = []
for i in range(len(K)):
    r = V_.regions[V_.point_region[i]]
    hucre.append(Polygon([V_.vertices[v] for v in r]).intersection(cer) if -1 not in r and r else None)
def yol(g):
    gs = getattr(g, 'geoms', [g]); return ''.join('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in q.exterior.coords) + 'Z' for q in gs if q.geom_type == 'Polygon')
svg = []
for i, k in enumerate(K):
    if hucre[i] is not None:
        bi = bk[k]; ton = 0.16 + 0.22 * ((bi * 37) % 7) / 6
        svg.append(f'<path d="{yol(hucre[i])}" fill="{ur[UST[i]]}" fill-opacity="{ton:.2f}" stroke="var(--zemin)" stroke-width=".6"/>')
for b in bolgeler:
    g = unary_union([hucre[K.index(k)] for k in b['kokler'] if hucre[K.index(k)] is not None])
    svg.append(f'<path d="{yol(g)}" fill="none" stroke="var(--yazi)" stroke-opacity=".35" stroke-width="1"><title>{b["ad"]}</title></path>')
for o in orta_ler:
    ix = [i for i in range(len(K)) if ORTA[i] == o]
    g = unary_union([hucre[i] for i in ix if hucre[i] is not None])
    svg.append(f'<path d="{yol(g)}" fill="none" stroke="var(--yazi)" stroke-width="2.4"/>')
    c = g.representative_point(); svg.append(f'<text class="kad" x="{c.x:.0f}" y="{c.y:.0f}">{AD.get(o, o)}</text>')
for i, k in enumerate(K):
    svg.append(f'<g class="k" data-k="{k}"><circle cx="{P[i,0]:.1f}" cy="{P[i,1]:.1f}" r="1.8" fill="var(--yazi)"/><text x="{P[i,0]+3:.1f}" y="{P[i,1]+3:.1f}">{k}</text></g>')
lej = ''.join(f'<span><i style="background:{ur[u]}"></i>{u}</span>' for u in ustler)
HTML = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kavram Uzayı</title>
<link href="https://fonts.googleapis.com/css2?family=Amiri&display=swap" rel="stylesheet"><style>
:root{{--zemin:#fbf8ef;--yazi:#2b2410;--ince:#8a7f62}}@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--zemin:#1d1b16;--yazi:#eee6cf;--ince:#a99f83}}}}
body{{margin:0;background:var(--zemin);color:var(--yazi);font-family:Georgia,serif}}#lej{{padding:8px 16px;font-size:13px;display:flex;flex-wrap:wrap;gap:12px}}
#lej i{{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:4px}}svg{{width:100%;height:calc(100vh - 40px);cursor:grab}}
.k text{{font-family:Amiri,serif;font-size:10px;fill:var(--yazi)}}.kad{{font-size:15px;font-weight:bold;text-anchor:middle;fill:var(--yazi);paint-order:stroke;stroke:var(--zemin);stroke-width:4;pointer-events:none}}
.bo{{fill:none;stroke:var(--ince);stroke-dasharray:3 3;stroke-width:.8}}#bil{{position:fixed;right:12px;top:44px;max-width:300px;background:var(--zemin);border:1px solid var(--ince);padding:8px;font-size:13px;display:none}}
.cz{{stroke:#b8860b;stroke-width:1.5}}</style></head><body><div id="lej">{lej}<span style="color:var(--ince)">· her kök bir hücre · kalın sınır: kavram uzayı · ince sınır: mana bölgesi · köke dokun: en yakın dört kök</span></div>
<svg id="s" viewBox="0 0 1800 1800"><g id="g">{''.join(svg)}<g id="cz"></g></g></svg><div id="bil"></div>
<script>const V={json.dumps({K[i]: [float(P[i,0]), float(P[i,1]), AD.get(ORTA[i], ORTA[i]), bolgeler[bk[K[i]]]['ad'], asil(A[K[i]]), komsu[K[i]]] for i in range(len(K))}, ensure_ascii=False)};
const s=document.getElementById('s');let vb=[0,0,1800,1800],dr=null;const up=()=>s.setAttribute('viewBox',vb.join(' '));
s.onwheel=e=>{{e.preventDefault();const f=e.deltaY>0?1.15:0.87,r=s.getBoundingClientRect(),mx=vb[0]+(e.clientX-r.left)/r.width*vb[2],my=vb[1]+(e.clientY-r.top)/r.height*vb[3];vb=[mx-(mx-vb[0])*f,my-(my-vb[1])*f,vb[2]*f,vb[3]*f];up()}};
s.onpointerdown=e=>dr=[e.clientX,e.clientY,vb[0],vb[1]];onpointerup=()=>dr=null;s.onpointermove=e=>{{if(!dr)return;const r=s.getBoundingClientRect();vb[0]=dr[2]-(e.clientX-dr[0])/r.width*vb[2];vb[1]=dr[3]-(e.clientY-dr[1])/r.height*vb[3];up()}};
document.querySelectorAll('.k').forEach(g=>g.onclick=()=>{{const k=g.dataset.k,v=V[k];document.getElementById('cz').innerHTML=v[5].map(n=>`<line class="cz" x1="${{v[0]}}" y1="${{v[1]}}" x2="${{V[n][0]}}" y2="${{V[n][1]}}"/>`).join('');
const b=document.getElementById('bil');b.style.display='block';b.innerHTML=`<b style="font-family:Amiri;font-size:22px">${{k}}</b><br>${{v[2]}} › ${{v[3]}}<br><br>${{v[4].join(' / ')}}<br><br>yakınları: ${{v[5].map(n=>`<a href="zihin_haritasi.html#${{n}}" style="font-family:Amiri">${{n}}</a>`).join(' ')}}`}});</script></body></html>"""
(HERE / 'kavram_uzayi.html').write_text(HTML, encoding='utf-8')
if '--png' in sys.argv:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'); g = b.new_page(viewport={'width': 1500, 'height': 1540}, device_scale_factor=2)
        g.goto((HERE / 'kavram_uzayi.html').as_uri()); g.wait_for_timeout(1500); g.screenshot(path=str(HERE / 'kavram_uzayi.png'))
        g.evaluate("vb=[700,700,450,450];up()"); g.wait_for_timeout(300); g.screenshot(path=str(HERE / 'kavram_uzayi_yakin.png')); b.close()
