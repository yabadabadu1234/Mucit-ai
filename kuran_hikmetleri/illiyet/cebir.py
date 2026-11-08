import os, json, pathlib
import numpy as np
from scipy.cluster.hierarchy import linkage, to_tree, fcluster
from scipy.spatial.distance import squareform
B = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).resolve().parent
G = pathlib.Path(os.environ["EVREN_GOMME_DIZIN"])
kokler = json.load(open(G / "kokler.json", encoding="utf-8")); idx = {k: i for i, k in enumerate(kokler)}
anlam = {x["kok"]: x["turkce"] for x in json.load(open(B / "kaynak/lugat/kok_anlamlari.json", encoding="utf-8"))}
K = np.load(G / "kok_anlam.npy").astype(np.float64); n = len(K)
Kc = K - K.mean(0); Kc /= np.linalg.norm(Kc, axis=1, keepdims=True)
S = Kc @ Kc.T; D = np.arccos(np.clip(S, -1, 1)); np.fill_diagonal(D, 0)
# 1) rütbe: ağaç metriği üzerinden yarıçap. Ortalama bağlantılı ağaç; yükseklik farkından rütbe.
Lk = linkage(squareform(D, checks=False), "average")
kok_dugum = to_tree(Lk)
rutbe = np.zeros(n)
def yuru(d, derin):
    if d.is_leaf(): rutbe[d.id] = derin; return
    yuru(d.get_left(), derin + 1); yuru(d.get_right(), derin + 1)
import sys; sys.setrecursionlimit(10000); yuru(kok_dugum, 0)
merkez = S.mean(1)                       # genellik: ortak özdeğer uzayında merkezîlik
rut = (merkez - merkez.min()) / (merkez.max() - merkez.min())
# 2) mevki: spektral koordinatlar ve kümeler
U, Sg, Vt = np.linalg.svd(Kc, full_matrices=False)
kume = fcluster(Lk, 40, "maxclust") - 1
# 3) münasebet türleri: komşu çiftlerin fark vektörlerinin eksen kümelemesi
nn = np.argsort(-S, axis=1)[:, 1:6]
I = np.repeat(np.arange(n), 5); J = nn.ravel()
V = K[J] - K[I]; nv = np.linalg.norm(V, axis=1); ok = nv > 1e-6; I, J, V = I[ok], J[ok], V[ok] / nv[ok][:, None]
rng = np.random.default_rng(5); kk = 14
C = V[rng.choice(len(V), kk, replace=False)].copy()
for _ in range(40):
    sim = V @ C.T; a = np.abs(sim).argmax(1); sg = np.sign(sim[np.arange(len(V)), a])
    for c in range(kk):
        m = a == c
        if m.sum(): v = (V[m] * sg[m][:, None]).mean(0); C[c] = v / np.linalg.norm(v)
sim = V @ C.T; a = np.abs(sim).argmax(1)
tur = []
for c in range(kk):
    m = np.where(a == c)[0]
    if len(m) < 20: continue
    en = m[np.argsort(-np.abs(sim[m, c]))[:8]]
    tur.append({"id": c, "n": int(len(m)), "ornek": [[kokler[I[e]], kokler[J[e]], int(np.sign(sim[e, c]))] for e in en]})
json.dump({"rutbe": {kokler[i]: round(float(rut[i]), 4) for i in range(n)}, "kume": {kokler[i]: int(kume[i]) for i in range(n)}, "tur": tur,
           "komsu": {kokler[i]: [kokler[j] for j in nn[i]] for i in range(n)}}, open(HERE / "cebir.json", "w", encoding="utf-8"), ensure_ascii=False)
o = np.argsort(-rut)
def t(k): return anlam.get(k, "")[:40]
print("EN ÜST:", [(kokler[i], t(kokler[i])) for i in o[:14]])
print("EN ALT:", [(kokler[i], t(kokler[i])) for i in o[-14:]])
for r in tur[:6]:
    print(r["n"], [(a, b, s) for a, b, s in r["ornek"][:4]])
# 4) yönlü sınama (yalnız ölçü): neticeler nispeten daha mı genel/özel?
kenar = json.load(open(HERE / "metin_kenarlari.json", encoding="utf-8"))
pos = np.array([(idx[a], idx[b]) for a, b in (k.split("|") for k in kenar) if a in idx and b in idx])
print("netice daha merkezî:", (rut[pos[:, 1]] > rut[pos[:, 0]]).mean().round(3))
# komşuluk asimetrisi: j, i'nin komşuluğunda i'den daha üst sırada mı
rk = np.argsort(np.argsort(-S, axis=1), axis=1)
print("rank asimetri (i->j daha yakın j->i'den):", (rk[pos[:, 0], pos[:, 1]] < rk[pos[:, 1], pos[:, 0]]).mean().round(3))
