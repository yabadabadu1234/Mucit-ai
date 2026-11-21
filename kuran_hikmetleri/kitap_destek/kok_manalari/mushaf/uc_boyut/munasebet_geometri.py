import json, pathlib, itertools, math
import numpy as np
from scipy import ndimage
HERE = pathlib.Path(__file__).resolve().parent
RED = (ValueError, KeyError)

def yukle(ad):
    d = json.load(open(HERE / 'munasebet_anahtar.json', encoding='utf-8'))
    return d['makam'], d['pasajlar'][ad]

def derinlik(birimler):
    dep = {}
    for b in birimler:
        dep[b['id']] = 0 if not b['illet'] else 1 + max(dep[i] for i in b['illet'])
    return dep

def gaye_kapsam(birimler, gayeler):
    ata = dict((g, p) for g, p in gayeler)
    kap = {g: set() for g in ata}
    for b in birimler:
        g = b['gaye']
        while g is not None:
            kap[g].add(b['id']); g = ata[g]
    return kap

def gaye_yuksek(gayeler):
    cocuk = {g: [] for g, _ in gayeler}
    for g, p in gayeler:
        if p is not None: cocuk[p].append(g)
    def h(g): return 0 if not cocuk[g] else 1 + max(h(c) for c in cocuk[g])
    return {g: h(g) for g in cocuk}

def kur(makam, P, sira=None):
    """Kapalı formüller: x=sıra, y=illet derinliği, th=2π·makam/M, z(x,y)=Σ A_g N(p;μ_g,σ_g) − Σ B_h N(p;ν_h,s)."""
    B = P['birimler']; ids = [b['id'] for b in B]
    if sira is not None: ids = sira
    bi = {b['id']: b for b in B}
    x = {u: float(i) for i, u in enumerate(ids)}
    dep = derinlik_all(bi)
    y = {u: float(dep[u]) for u in ids}
    th = {u: 2 * math.pi * makam.index(bi[u]['makam']) / len(makam) for u in ids}
    kap = gaye_kapsam(B, P['gayeler']); yuk = gaye_yuksek(P['gayeler'])
    dome = {}
    for g, S in kap.items():
        if not S: continue
        px = np.array([x[u] for u in S]); py = np.array([y[u] for u in S])
        mu = (px.mean(), py.mean())
        sx = 0.3 * (px.max() - px.min()) + 0.45; sy = 0.3 * (py.max() - py.min()) + 0.45
        dome[g] = (1.0 + yuk[g], mu, (sx, sy))
    pit = []
    for h in P['hazif']:
        i = ids.index(h['sonra']); xs = x[h['sonra']] + 0.5
        kom = [ids[k] for k in (i, i + 1) if 0 <= k < len(ids)]
        ys = float(np.mean([y[u] for u in kom]))
        pit.append((xs, ys, 0.22, 0.5 * dome[h["gaye"]][0]))
    return dict(ids=ids, x=x, y=y, th=th, dome=dome, pit=pit, kap=kap, bi=bi)

def derinlik_all(bi):
    dep = {}
    def d(u):
        if u not in dep: dep[u] = 0 if not bi[u]['illet'] else 1 + max(d(i) for i in bi[u]['illet'])
        return dep[u]
    for u in bi: d(u)
    return dep

def z_at(S, X, Y):
    z = np.zeros_like(X, dtype=float)
    for A, (mx, my), (sx, sy) in S['dome'].values():
        z += A * np.exp(-0.5 * (((X - mx) / sx) ** 2 + ((Y - my) / sy) ** 2))
    for (px, py, s, B) in S['pit']:
        z -= B * np.exp(-0.5 * (((X - px) / s) ** 2 + ((Y - py) / 0.35) ** 2))
    return z

def izgara(S, n=240):
    xs = np.linspace(-1, len(S['ids']), n); ys = np.linspace(-1, max(S['y'].values()) + 1.5, n)
    X, Y = np.meshgrid(xs, ys); return X, Y, z_at(S, X, Y)

# ---------- ÇÖZÜCÜLER: yalnız (grid z, noktalar x,y,th) girdi alır; anahtara bakmaz ----------
def coz_makam(th, M): return {u: int(round(t / (2 * math.pi) * M)) % M for u, t in th.items()}

def _tepe_agi(Z):
    """Her ızgara noktasını en dik çıkışla bir yerel tepeye bağlar (havza)."""
    H, W = Z.shape; hedef = -np.ones((H, W), int)
    def yukari(i, j):
        best = (Z[i, j], i, j)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                a, b = i + di, j + dj
                if 0 <= a < H and 0 <= b < W and Z[a, b] > best[0]: best = (Z[a, b], a, b)
        return best[1], best[2]
    for i in range(H):
        for j in range(W):
            a, b = i, j; yol = []
            while hedef[a, b] < 0:
                yol.append((a, b)); na, nb = yukari(a, b)
                if (na, nb) == (a, b): hedef[a, b] = a * W + b; break
                a, b = na, nb
            t = hedef[a, b]
            for (c, d) in yol: hedef[c, d] = t
    return hedef

def coz_gaye_agaci(S_nokta, X, Y, Z, dusuk=0.0):
    """Havza esaslı: birimleri tepe-havzasına böl; tepe ≥ iki birimi tutuyorsa yaprak gaye; kök = tümü."""
    ids = list(S_nokta); H = _tepe_agi(Z)
    ix = {u: (np.abs(Y[:, 0] - S_nokta[u][1]).argmin(), np.abs(X[0] - S_nokta[u][0]).argmin()) for u in ids}
    grp = {}
    for u in ids: grp.setdefault(int(H[ix[u]]), set()).add(u)
    fam = set(frozenset(s) for s in grp.values() if len(s) >= 2)
    fam.add(frozenset(ids))
    zs = {u: Z[ix[u]] for u in ids}
    return fam, zs

def coz_cukur(Z, X, Y, noktalar):
    """Noktalar çevresinden uzakta kalan, çevresine göre derin yerel minimumlar (izgara üzerinde)."""
    from scipy import ndimage as nd
    mn = nd.minimum_filter(Z, size=31); mx = nd.maximum_filter(Z, size=31)
    ad = (Z == mn) & ((mx - Z) > 0.25)
    H, W = Z.shape; out = []
    for i, j in zip(*np.nonzero(ad)):
        if 15 < i < H - 16 and 15 < j < W - 16: out.append((round(float(X[0][j]), 2), round(float(Y[:, 0][i]), 2)))
    return out

def beklenen_aile(P):
    kap = gaye_kapsam(P['birimler'], P['gayeler']); ata = dict(P['gayeler'])
    yap = set(g for g in kap if g not in set(a for a in ata.values() if a) and len(kap[g]) >= 2)
    fam = set(frozenset(kap[g]) for g in yap); fam.add(frozenset(b['id'] for b in P['birimler']))
    return fam
