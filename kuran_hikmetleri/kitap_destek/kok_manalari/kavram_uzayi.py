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
def yol(g):
    gs = getattr(g, 'geoms', [g]); return ''.join('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in q.exterior.coords) + 'Z' for q in gs if q.geom_type == 'Polygon')
svg = []
for i in range(len(N)):
    ton = 0.15 + 0.22 * ((bolge[i] * 37) % 7) / 6
    svg.append(f'<path d="{yol(hucre[i])}" fill="{RENK[ust_i[N[i][3]]]}" fill-opacity="{ton:.2f}" stroke="var(--zemin)" stroke-width=".6"/>')
for b in BOL:
    svg.append(f'<path d="{yol(unary_union([hucre[i] for i in b["uyeler"]]))}" fill="none" stroke="var(--yazi)" stroke-opacity=".3" stroke-width=".9"><title>{b["ad"]}</title></path>')
for ci, c in enumerate(KODLAR):
    g = unary_union([hucre[i] for i in ix_of[c]])
    svg.append(f'<path d="{yol(g)}" fill="none" stroke="var(--yazi)" stroke-width="2.2"/>')
    p = P[ix_of[c]].mean(0); svg.append(f'<text class="kad" x="{p[0]:.0f}" y="{p[1]:.0f}">{KA.KOD[c][1]}</text>')
for i in range(len(N)):
    svg.append(f'<g class="k" data-k="{ad(i)}"><circle cx="{P[i,0]:.1f}" cy="{P[i,1]:.1f}" r="1.6"/><text x="{P[i,0]+2.5:.1f}" y="{P[i,1]+3:.1f}">{ad(i)}</text></g>')
lej = ''.join(f'<span><i style="background:{RENK[u]}"></i>{a}</span>' for u, (a, _) in enumerate(KA.AGAC))
VER = {ad(i): [float(P[i, 0]), float(P[i, 1]), KA.KOD[N[i][3]][1], BOL[bolge[i]]['ad'], N[i][2], [ad(j) for j in np.argsort(-sim[i])[:4]], N[i][0]] for i in range(len(N))}
HTML = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kavram Uzayı</title>
<link href="https://fonts.googleapis.com/css2?family=Amiri&display=swap" rel="stylesheet"><style>
:root{{--zemin:#fbf8ef;--yazi:#2b2410;--ince:#8a7f62}}@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--zemin:#1d1b16;--yazi:#eee6cf;--ince:#a99f83}}}}
body{{margin:0;background:var(--zemin);color:var(--yazi);font-family:Georgia,serif}}#lej{{padding:8px 16px;font-size:13px;display:flex;flex-wrap:wrap;gap:12px}}
#lej i{{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:4px}}svg{{width:100%;height:calc(100vh - 60px);cursor:grab}}
.k text{{font-family:Amiri,serif;font-size:8.5px;fill:var(--yazi)}}.k circle{{fill:var(--yazi)}}.kad{{font-size:14px;font-weight:bold;text-anchor:middle;fill:var(--yazi);paint-order:stroke;stroke:var(--zemin);stroke-width:4;pointer-events:none}}
#bil{{position:fixed;right:12px;top:60px;max-width:300px;background:var(--zemin);border:1px solid var(--ince);padding:8px;font-size:13px;display:none}}.cz{{stroke:#b8860b;stroke-width:1.5}}</style></head><body>
<div id="lej">{lej}<span style="color:var(--ince)">· her hücre bir kökün bir aslı (¹ ² birinci, ikinci asıl) · kalın sınır: kavram · ince sınır: mana bölgesi</span></div>
<svg id="s" viewBox="0 0 1800 1800"><g>{''.join(svg)}<g id="cz"></g></g></svg><div id="bil"></div>
<script>const V={json.dumps(VER, ensure_ascii=False)};
const s=document.getElementById('s');let vb=[0,0,1800,1800],dr=null;const up=()=>s.setAttribute('viewBox',vb.join(' '));
s.onwheel=e=>{{e.preventDefault();const f=e.deltaY>0?1.15:0.87,r=s.getBoundingClientRect(),mx=vb[0]+(e.clientX-r.left)/r.width*vb[2],my=vb[1]+(e.clientY-r.top)/r.height*vb[3];vb=[mx-(mx-vb[0])*f,my-(my-vb[1])*f,vb[2]*f,vb[3]*f];up()}};
s.onpointerdown=e=>dr=[e.clientX,e.clientY,vb[0],vb[1]];onpointerup=()=>dr=null;s.onpointermove=e=>{{if(!dr)return;const r=s.getBoundingClientRect();vb[0]=dr[2]-(e.clientX-dr[0])/r.width*vb[2];vb[1]=dr[3]-(e.clientY-dr[1])/r.height*vb[3];up()}};
document.querySelectorAll('.k').forEach(g=>g.onclick=()=>{{const k=g.dataset.k,v=V[k],kard=Object.keys(V).filter(x=>V[x][6]==v[6]&&x!=k);
document.getElementById('cz').innerHTML=v[5].map(n=>`<line class="cz" x1="${{v[0]}}" y1="${{v[1]}}" x2="${{V[n][0]}}" y2="${{V[n][1]}}"/>`).join('')+kard.map(n=>`<line x1="${{v[0]}}" y1="${{v[1]}}" x2="${{V[n][0]}}" y2="${{V[n][1]}}" stroke="#a0304a" stroke-dasharray="4 3" stroke-width="1.3"/>`).join('');
const b=document.getElementById('bil');b.style.display='block';b.innerHTML=`<b style="font-family:Amiri;font-size:22px">${{k}}</b> ${{v[4]}}<br>${{v[2]}} › ${{v[3]}}<br><br>yakınları: ${{v[5].join(' ')}}<br>aynı kökün öbür asılları (kırmızı kesik): ${{kard.join(' ')||'yok'}}<br><a href="zihin_haritasi.html#${{v[6]}}">türeme ağacı</a>`}});</script></body></html>"""
(HERE / 'kavram_uzayi.html').write_text(HTML, encoding='utf-8')
if '--png' in sys.argv:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'); g = b.new_page(viewport={'width': 1500, 'height': 1560}, device_scale_factor=2)
        g.goto((HERE / 'kavram_uzayi.html').as_uri()); g.wait_for_timeout(1500); g.screenshot(path=str(HERE / 'kavram_uzayi.png')); b.close()
