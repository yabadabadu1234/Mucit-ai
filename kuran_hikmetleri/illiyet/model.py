import os, json, pathlib, collections, math
import numpy as np
B = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).resolve().parent
G = pathlib.Path(os.environ["EVREN_GOMME_DIZIN"])
rng = np.random.default_rng(7)
kokler = json.load(open(G / "kokler.json", encoding="utf-8"))
idx = {k: i for i, k in enumerate(kokler)}
n = len(kokler)
K = np.load(G / "kok.npy"); A = np.load(G / "ayet.npy")
akey = json.load(open(G / "ayet_anahtar.json")); aidx = {k: i for i, k in enumerate(akey)}
kenar = json.load(open(HERE / "metin_kenarlari.json", encoding="utf-8"))
ayet_kok = collections.defaultdict(set); kok_ayet = collections.defaultdict(set)
for l in open(B / "veri_harici/eyupipler/quran-morphology.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("\t")
    if len(p) < 4: continue
    s, a, _, _ = p[0].split(":")
    r = next((t[5:] for t in p[3].split("|") if t.startswith("ROOT:")), None)
    if r in idx and f"{s}:{a}" in aidx:
        kok_ayet[r].add(aidx[f"{s}:{a}"]); ayet_kok[f"{s}:{a}"].add(r)
C = np.zeros_like(K)
for r, S in kok_ayet.items():
    C[idx[r]] = A[list(S)].mean(0)
C /= np.linalg.norm(C, axis=1, keepdims=True) + 1e-9
Z = K + C
Z /= np.linalg.norm(Z, axis=1, keepdims=True)
Z = Z - Z.mean(0)
U_, S_, Vt = np.linalg.svd(Z, full_matrices=False)
d = 96
Zp = U_[:, :d] * S_[:d]; Zp /= Zp.std()
pos = []
for key, v in kenar.items():
    x, y = key.split("|")
    if x in idx and y in idx:
        pos.append((idx[x], idx[y], sum(v["n"].values())))
pos = np.array(pos)
print("kök", n, "yönlü metin çifti", len(pos))
def sig(x): return 1 / (1 + np.exp(-x))
class M:
    def __init__(s, r=24, bias=True, l2=1e-3):
        s.r = r; s.bias = bias; s.l2 = l2
        s.W1 = rng.normal(0, .1, (d, r)); s.W2 = rng.normal(0, .1, (d, r))
        s.a = np.zeros(n); s.e = np.zeros(n)
    def skor(s, i, j, Zq=None):
        Zq = Zp if Zq is None else Zq
        v = ((Zq[i] @ s.W1) * (Zq[j] @ s.W2)).sum(1)
        return v + (s.a[i] + s.e[j] if s.bias else 0)
    def egit(s, P, it=600, neg=5, lr=0.03):
        P = np.array(P); par = [s.W1, s.W2, s.a, s.e]
        m = [np.zeros_like(p) for p in par]; v = [np.zeros_like(p) for p in par]
        posset = set(map(tuple, P[:, :2]))
        for t in range(1, it + 1):
            ni = rng.integers(0, n, len(P) * neg); nj = rng.integers(0, n, len(P) * neg)
            ok = np.array([(a, b) not in posset and a != b for a, b in zip(ni, nj)])
            ni, nj = ni[ok], nj[ok]
            I = np.concatenate([P[:, 0], ni]); J = np.concatenate([P[:, 1], nj])
            y = np.concatenate([np.ones(len(P)), np.zeros(len(ni))])
            w = np.concatenate([np.ones(len(P)) * neg * .5, np.ones(len(ni))])
            p = sig(s.skor(I, J)); g = (p - y) * w / w.sum()
            ZI = Zp[I]; ZJ = Zp[J]
            gW1 = ZI.T @ (g[:, None] * (ZJ @ s.W2)) + s.l2 * s.W1
            gW2 = ZJ.T @ (g[:, None] * (ZI @ s.W1)) + s.l2 * s.W2
            ga = np.bincount(I, g, n) if s.bias else np.zeros(n); ge = np.bincount(J, g, n) if s.bias else np.zeros(n)
            for k, (pp, gg) in enumerate(zip(par, [gW1, gW2, ga, ge])):
                m[k] = .9 * m[k] + .1 * gg; v[k] = .999 * v[k] + .001 * gg * gg
                pp -= lr * (m[k] / (1 - .9 ** t)) / (np.sqrt(v[k] / (1 - .999 ** t)) + 1e-8)
        return s
def auc(sp, sn):
    a = np.concatenate([sp, sn]); r = a.argsort().argsort() + 1
    return (r[:len(sp)].sum() - len(sp) * (len(sp) + 1) / 2) / (len(sp) * len(sn))
perm = rng.permutation(len(pos)); cut = int(.8 * len(pos))
tr, te = pos[perm[:cut]], pos[perm[cut:]]
posall = set(map(tuple, pos[:, :2]))
ni = rng.integers(0, n, 20000); nj = rng.integers(0, n, 20000)
ok = np.array([(a, b) not in posall and a != b for a, b in zip(ni, nj)]); ni, nj = ni[ok][:len(te) * 5], nj[ok][:len(te) * 5]
sonuc = {}
for ad, kw in [("derece_yalniz", dict(r=1, bias=True)), ("tam_model", dict(r=24, bias=True)), ("icerik_yalniz", dict(r=24, bias=False))]:
    mm = M(**kw)
    if ad == "derece_yalniz": mm.W1 *= 0; mm.W2 *= 0
    mm.egit(tr, it=500)
    if ad == "derece_yalniz": mm.W1 *= 0; mm.W2 *= 0
    sp = mm.skor(te[:, 0], te[:, 1]); sn = mm.skor(ni, nj)
    ters = mm.skor(te[:, 1], te[:, 0])
    yon_ok = np.array([(int(b), int(a)) not in set(map(tuple, tr[:, :2])) for a, b in te[:, :2]])
    sonuc[ad] = {"AUC": round(float(auc(sp, sn)), 4), "yon_dogrulugu": round(float((sp[yon_ok] > ters[yon_ok]).mean()), 4), "yon_n": int(yon_ok.sum())}
    print(ad, sonuc[ad], flush=True)
sonuc["test_cift"] = int(len(te)); sonuc["egitim_cift"] = int(len(tr))
json.dump(sonuc, open(HERE / "olcu.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
fin = M(r=24, bias=True).egit(pos, it=700)
np.savez(G / "model.npz", W1=fin.W1, W2=fin.W2, a=fin.a, e=fin.e, Zp=Zp)
print("model kaydedildi")
