"""Gerçek kavram kafesi, üç boyutlu (silindirik) yerleşim.
 yükseklik z = kafes katmanı (üstte en umumî, altta en hususî)
 yarıçap   r = köke uzaklık (esas merkezde; mecaz uzaklaştıkça dışarıda)
 açı       θ = sıralama; kuralları sağlayan dizilişten gelir."""
import json, math, itertools, pathlib, collections
from kafes2_veri import nodes, M, W
import kafes3_kafes as K

HERE = pathlib.Path(__file__).resolve().parent
KAV, cover, kavram, KELIME, MANA, ATT, OBJ, inc = K.KAV, K.cover, K.kavram, K.KELIME, K.MANA, K.ATT, K.OBJ, K.inc
IDX = {e: i for i, e in enumerate(KAV)}
TOP = IDX[frozenset(OBJ)]
BOT = IDX[frozenset()]

# kenarlar (üst, alt)
E = [(IDX[b], IDX[a]) for b, a in cover]
par = collections.defaultdict(list); kid = collections.defaultdict(list)
for u, a in E: par[a].append(u); kid[u].append(a)

# katman = en uzun yol
rank = {}
def rk(i):
    if i in rank: return rank[i]
    rank[i] = 0 if not par[i] else 1 + max(rk(p) for p in par[i])
    return rank[i]
for i in range(len(KAV)): rk(i)

# vasıf -> kavram, nesne -> kavram
mu = {a: IDX[K.ext_att[a]] for a in ATT}
gamma = {}
for i, e in enumerate(KAV):
    I = kavram[e][1]
    for o in OBJ:
        if inc[o] == I: gamma[o] = i

# türeme derinliği (köke uzaklık)
depth = {}
def dp(a):
    if a in depth: return depth[a]
    p = MANA[a]['ebeveyn']
    depth[a] = 1 if (not p or p == ['E']) else 1 + max(dp(q) for q in p if q != 'E') if any(q != 'E' for q in p) else 1
    return depth[a]
for a in ATT:
    if a != 'R2': dp(a)
depth['R2'] = 0.6
own = collections.defaultdict(list)
for a in ATT: own[mu[a]].append(a)
words = collections.defaultdict(list)
for o, c in gamma.items(): words[c].append(o)

# --- katman içi sıralama: ardışıklık kısıtını sağlayan dizilişi bul -------------
def coz(elemanlar, kumeler, tercih):
    """elemanlar sırada yan yana; her küme bitişik; tercih: istenen konum (küçük önce)."""
    kumeler = [frozenset(k) for k in kumeler if 1 < len(k) < len(elemanlar)]
    el = sorted(elemanlar, key=lambda x: (tercih.get(x, 0), x))
    best = []
    def gecerli(sira):
        n = len(sira)
        pos = {x: i for i, x in enumerate(sira)}
        for S in kumeler:
            ps = sorted(pos[x] for x in S if x in pos)
            if not ps: continue
            if ps[-1] - ps[0] + 1 != len(ps): return False
            if len(ps) < len(S) and ps[-1] != n - 1: return False
        return True
    sayac = [0]
    def dfs(sira, kalan):
        sayac[0] += 1
        if sayac[0] > 2_000_000: return None
        if not kalan: return list(sira)
        for x in sorted(kalan, key=lambda y: (tercih.get(y, 0), y)):
            sira.append(x)
            if gecerli(sira):
                r = dfs(sira, [y for y in kalan if y != x])
                if r: return r
            sira.pop()
        return None
    return dfs([], el)

levels = collections.defaultdict(list)
for i in range(len(KAV)): levels[rank[i]].append(i)
NL = max(levels) + 1
order = {0: [TOP]}
for L in range(1, NL):
    lst = levels[L]
    # tercih: ebeveynlerin konum ortası
    prev = {x: k for k, x in enumerate(order[L - 1])} if (L - 1) in order else {}
    tercih = {x: sum(prev.get(p, 0) for p in par[x]) / max(1, len(par[x])) for x in lst}
    kumeler = []
    # bu katmandaki düğümlerin çocuk kümeleri (aynı katmanda kalanlar)
    for p in range(len(KAV)):
        ch = [c for c in kid[p] if rank[c] == L]
        if len(ch) > 1: kumeler.append(ch)
    # bu katmandaki çok ebeveynli çocukların ebeveyn kümeleri (üst katman, bu katmana kısıt değil; üst katmanda çözülmeli)
    # üst katman kısıtı: ebeveynleri aynı katmanda ve birden çoksa bitişik
    for c in range(len(KAV)):
        ps = [p for p in par[c] if rank[p] == L]
        if len(ps) > 1: kumeler.append(ps)
    sira = coz(lst, kumeler, tercih)
    assert sira, ('çözülemedi', L)
    order[L] = sira

# --- açılar: katmanda eşit aralıklı; çocuk, ebeveynlerinin ortasında -----------
ang = {}
for L in range(NL):
    lst = order[L]
    if L == 0: ang[lst[0]] = 0.0; continue
    ref = order[1]
n1 = len(order[1])
SEAM = 0.0
for k, x in enumerate(order[1]):
    ang[x] = 2 * math.pi * k / n1
for L in range(2, NL):
    # istenen açı: ebeveynlerin (aynı katmandaki ya da üstteki) ortası; çakışmayı gider
    tg = {}
    for x in order[L]:
        ps = [p for p in par[x] if p in ang]
        tg[x] = sum(ang[p] for p in ps) / len(ps) if ps else 0.0
    ang.update(tg)
ang[TOP] = 0.0; ang[BOT] = 0.0
# ortak ebeveynsiz kelimelerin altı: çocuk ebeveyniyle aynı açıda

# yarıçap = köke uzaklık
def r_of(i):
    if i in (TOP, BOT): return 0.0
    os_ = own.get(i, [])
    if os_: return max(depth[a] for a in os_)
    ps = par[i]
    return sum(r_of(p) for p in ps) / len(ps)
RD = 520.0
R = {i: r_of(i) * RD for i in range(len(KAV))}
R[TOP] = 0.0; R[BOT] = 0.0
ZG = 640.0
Z = {i: -rank[i] * ZG for i in range(len(KAV))}
if True:
    # alt düğüm: son katman
    Z[BOT] = -rank[BOT] * ZG

# --- kural denetimi (aynı katmanda, her yarıçapta) ----------------------------
def arc_between(a_list, L, hepsi=True):
    lst = order[L]
    pos = [lst.index(x) for x in a_list]
    lo, hi = min(pos), max(pos)
    return [lst[k] for k in range(lo, hi + 1) if lst[k] not in a_list]
ihlal = []
for p in range(len(KAV)):
    ch = [c for c in kid[p]]
    byrank = collections.defaultdict(list)
    for c in ch: byrank[rank[c]].append(c)
    for L, g in byrank.items():
        if len(g) > 1 and arc_between(g, L): ihlal.append(('cocuk_arasina_girdi', p, g, arc_between(g, L)))
for c in range(len(KAV)):
    byrank = collections.defaultdict(list)
    for p in par[c]: byrank[rank[p]].append(p)
    for L, g in byrank.items():
        if len(g) > 1 and arc_between(g, L): ihlal.append(('ebeveyn_arasina_girdi', c, g, arc_between(g, L)))
# hiza: çok ebeveynli düğümün açısı ebeveyn açılarının ortası (aynı katmandakiler için)
hiza = {}
for c in range(len(KAV)):
    ps = [p for p in par[c] if rank[p] == min(rank[q] for q in par[c])] if par[c] else []
    if len(ps) > 1:
        hiza[c] = round(math.degrees(ang[c] - sum(ang[p] for p in ps) / len(ps)), 2)
atlayan = [(u, a) for u, a in E if rank[a] - rank[u] > 1]

# --- sebep (türeme) kenarları -------------------------------------------------
sebep = collections.OrderedDict()
def kavram_of(a):
    return TOP if a == 'E' else mu[a]
for a in ATT:
    if a == 'R2': continue
    for q in MANA[a]['ebeveyn']:
        s, t = kavram_of(q), mu[a]
        if s == t: continue
        sebep.setdefault((s, t), []).append(MANA[a]['sebep'])


# öndeki bakışta (x,y düzlemi) kutuların üst üste binmesini en aza indiren genel dönüş
KUTU_W, KUTU_H, K = 330, 150, 1.2          # bütün kutular aynı ebatta (css px) ve aynı ölçekte
def boyut_yaklasik(i):
    return KUTU_W * K, KUTU_H * K
SZ = {i: boyut_yaklasik(i) for i in range(len(KAV))}
def cakisma(phi):
    # kutular yatay yatar; üstten bakışta (x, z) düzleminde ayak izleri örtüşüyor mu
    c = 0
    ps = {i: (R[i] * math.cos(ang[i] + phi), R[i] * math.sin(ang[i] + phi)) for i in range(len(KAV))}
    for i in range(len(KAV)):
        for j in range(i + 1, len(KAV)):
            dx = abs(ps[i][0] - ps[j][0]); dy = abs(ps[i][1] - ps[j][1])
            if dx < (SZ[i][0] + SZ[j][0]) / 2 and dy < (SZ[i][1] + SZ[j][1]) / 2: c += 1
    return c
PHI = min((cakisma(2 * math.pi * k / 120), k) for k in range(120))
PHI0 = 2 * math.pi * PHI[1] / 120
for i in ang: ang[i] += PHI0
print('üstten bakışta örtüşen kutu çifti:', PHI[0], 'dönüş (derece):', round(math.degrees(PHI0)))
def etiket(i):
    e = KAV[i]
    t = []
    if i == TOP: t.append('ESAS: ' + nodes['E']['metin'])
    for a in own.get(i, []): t.append(MANA[a]['metin'])
    w = []
    for o in sorted(words.get(i, []), key=lambda o: KELIME[o]['ar']):
        k = KELIME[o]
        an = ' / '.join(dict.fromkeys(k['anlam'].values()))
        w.append(dict(ar=k['ar'], tr=an, tag=k['tag'], kuran=k['kuran']))
    return dict(id=i, rank=rank[i], r=R[i], theta=ang[i], z=Z[i], baslik=t, kelimeler=w,
                kind='top' if i == TOP else 'bot' if i == BOT else 'mid',
                renk=(nodes[own[i][0]]['renk'] if own.get(i) else 'ab'),
                n=len(e))
D = dict(kutu=[KUTU_W, KUTU_H], olcek=K, dugumler=[etiket(i) for i in range(len(KAV))],
         kafes_kenarlari=[[u, a] for u, a in E],
         sebep_kenarlari=[[s, t, v] for (s, t), v in sebep.items()],
         halkalar=[RD * k for k in range(1, int(max(depth.values())) + 1)],
         katman_z=[-L * ZG for L in range(NL)])
(HERE / 'kafes3_veri.json').write_text(json.dumps(D, ensure_ascii=False), encoding='utf-8')
rapor = dict(kutu_ebadi=[KUTU_W, KUTU_H], olcek=K, ust_gorunus_ortusen_cift=PHI[0], nesne=len(OBJ), vasif=len(ATT), kavram_dugumu=len(KAV), hasse_kenari=len(E), katman=NL,
             katman_dugum_sayisi={L: len(order[L]) for L in order}, ihlal=ihlal,
             hiza_sapmasi_derece=hiza, katman_atlayan_kenar=len(atlayan),
             sebep_kenari=len(sebep))
(HERE / 'kafes3_rapor.json').write_text(json.dumps(rapor, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps(rapor, ensure_ascii=False, indent=1))
for L in order: print(L, [ (i, ''.join(own.get(i, [])) or ''.join(sorted(inc[o].__iter__().__next__() if False else '' for o in [])) ) for i in order[L]])
