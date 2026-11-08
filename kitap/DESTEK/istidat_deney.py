import json, itertools, pathlib
import numpy as np
from scipy import stats
rng = np.random.default_rng(23)

def scm(p=6):
    W = np.zeros((p, p))
    for j in range(1, p):
        for i in range(j):
            if rng.random() < .5: W[i, j] = rng.uniform(.6, 1.4) * rng.choice([-1, 1])
    hedef = next(j for j in range(p - 1, 0, -1) if W[:, j].any())
    return W, hedef

def uret(W, n, mud):
    p = len(W); X = np.zeros((n, p))
    for j in range(p):
        if j in mud:
            X[:, j] = rng.normal(0, mud[j], n)
        else:
            X[:, j] = X @ W[:, j] + rng.normal(0, 1, n)
    return X

def ayni_mi(Xe, y, S):
    res = []
    A = np.vstack(Xe)[:, S] if S else np.zeros((sum(len(x) for x in Xe), 0))
    Y = np.concatenate(y); D = np.column_stack([A, np.ones(len(Y))])
    b = np.linalg.lstsq(D, Y, rcond=None)[0]
    r = Y - D @ b; i = 0
    for x in Xe:
        res.append(r[i:i + len(x)]); i += len(x)
    if len(res) < 2: return 1.0
    p1 = stats.f_oneway(*res).pvalue; p2 = stats.levene(*res).pvalue
    return min(1.0, 2 * min(p1, p2))

def kesfet(W, hedef, ke, n=400):
    p = len(W); diger = [j for j in range(p) if j != hedef]
    Xe = [uret(W, n, {})]
    for _ in range(ke - 1):
        k = rng.integers(1, len(diger) + 1)
        sec = rng.choice(diger, k, replace=False)
        Xe.append(uret(W, n, {int(j): float(rng.uniform(.5, 3)) for j in sec}))
    y = [x[:, hedef] for x in Xe]
    kabul = []
    for r in range(0, len(diger) + 1):
        for S in itertools.combinations(diger, r):
            if ayni_mi(Xe, y, list(S)) > .05: kabul.append(set(S))
    if not kabul: return set()
    return set.intersection(*kabul)

olcu = {}
satir = {}
for ke in (1, 2, 4, 8, 16):
    ra = []; fa = []
    for _ in range(120):
        W, h = scm(); gercek = set(np.where(W[:, h] != 0)[0])
        bul = kesfet(W, h, ke)
        ra.append(len(bul & gercek) / len(gercek)); fa.append(len(bul - gercek) / max(1, len(bul)) if bul else 0.0)
    satir[ke] = {"anma": round(float(np.mean(ra)), 3), "yanlis_bulus_orani": round(float(np.mean(fa)), 3)}
    print("ortam", ke, satir[ke], flush=True)
olcu["etkin_degismezlik_kesfi"] = satir

def ib(px, pyx, K, beta, it=300):
    m = len(px); q = rng.dirichlet(np.ones(K), m)
    for _ in range(it):
        pt = px @ q + 1e-12
        pyt = (q * px[:, None]).T @ pyx / pt[:, None]
        kl = np.array([[np.sum(pyx[x] * np.log((pyx[x] + 1e-12) / (pyt[t] + 1e-12))) for t in range(K)] for x in range(m)])
        q = pt[None, :] * np.exp(-beta * kl); q /= q.sum(1, keepdims=True)
    pt = px @ q
    return float(np.exp(-np.sum(pt * np.log(pt + 1e-12))))
px = np.ones(12) / 12; grup = np.repeat([0, 1, 2], 4)
pg = np.array([.15, .5, .85]); pyx = np.column_stack([1 - pg[grup], pg[grup]]); pyx = np.where(np.arange(12)[:, None] % 4 == 0, pyx + .02 * np.array([-1, 1]), pyx)
beta = {}
for b in (0.5, 1, 2, 4, 8, 16, 32, 64):
    beta[b] = round(float(np.mean([ib(px, pyx, 6, b) for _ in range(5)])), 3)
olcu["bilgi_darboğazı_etkin_kume"] = beta
olcu["acik_hasr_eksik_kutle_alfa1"] = {n: round(1 / (n + 1), 5) for n in (5, 20, 100, 1000)}

def deger_iterasyonu(K, sig=1.0, d=.5, g=.95, N=161, L=6):
    lam = np.linspace(-L, L, N); p = 1 / (1 + np.exp(-lam))
    P = np.zeros((N, N))
    for i in range(N):
        for s, w in ((d, p[i]), (-d, 1 - p[i])):
            ym = lam[i] + s
            ker = np.exp(-(lam - ym) ** 2 / (2 * sig ** 2)); ker /= ker.sum(); P += 0
            P[i] += w * ker
    r = np.stack([1 - p, p], 1); V = np.zeros((N, 2))
    for _ in range(2000):
        Q = np.zeros((N, 2, 2))
        for a in (0, 1):
            for a0 in (0, 1):
                Q[:, a0, a] = r[:, a] - K * (a != a0) + g * (P @ V[:, a])
        Vn = Q.max(2)
        if np.abs(Vn - V).max() < 1e-9: break
        V = Vn
    pol = Q.argmax(2)
    ust = lam[np.argmax(pol[:, 0] == 1)] if (pol[:, 0] == 1).any() else None
    alt = lam[N - 1 - np.argmax(pol[::-1, 1] == 0)] if (pol[:, 1] == 0).any() else None
    return None if ust is None or alt is None else round(float(ust - alt), 3)
olcu["gecis_maliyeti_ile_iz_an_bandi"] = {K: deger_iterasyonu(K) for K in (0.0, 0.02, 0.1, 0.3, 1.0)}

n = 4; perm = list(itertools.permutations(range(n)))
adalet = lambda x: n * x.min(axis=1)
def deney_bilkuvve():
    X = rng.dirichlet(np.ones(n), 300)
    aday = {"degisme_01": lambda x: x[:, [1, 0, 2, 3]], "degisme_23": lambda x: x[:, [0, 1, 3, 2]], "degisme_02": lambda x: x[:, [2, 1, 0, 3]],
            "dongu": lambda x: np.roll(x, 1, 1), "olcek": lambda x: np.clip(x * 1.3, 0, 1), "kaydir": lambda x: np.clip(x + .1, 0, 1),
            "ters_sira": lambda x: x[:, ::-1]}
    kus = {a: float(np.mean(np.abs(adalet(g(X)) - adalet(X)))) for a, g in aday.items()}
    return kus
olcu["kendi_hareketleriyle_grup_kesfi"] = {a: round(v, 4) for a, v in deney_bilkuvve().items()}
def kuvvet(x): return np.sort(x, axis=1)
Xt = rng.dirichlet(np.ones(n), 3000); yt = adalet(Xt)
F = lambda x: np.column_stack([np.ones(len(x))] + [kuvvet(x)[:, i] for i in range(n)])
w = np.linalg.lstsq(F(Xt), yt, rcond=None)[0]
Xs = rng.dirichlet(np.ones(n), 2000)
olcu["kesfedilen_degismezlik_ile_genelleme_RMSE_permute"] = round(float(np.sqrt(np.mean((F(Xs[:, rng.permutation(n)]) @ w - adalet(Xs)) ** 2))), 5)
json.dump(olcu, open(pathlib.Path(__file__).with_name("istidat_olcu.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in olcu.items() if k != "etkin_degismezlik_kesfi"}, indent=1, ensure_ascii=False))
