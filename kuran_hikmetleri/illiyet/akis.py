import os, json, pathlib, collections
import numpy as np
B = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).resolve().parent
G = pathlib.Path(os.environ["EVREN_GOMME_DIZIN"])
kokler = json.load(open(G / "kokler.json", encoding="utf-8")); idx = {k: i for i, k in enumerate(kokler)}
K = np.load(G / "kok.npy").astype(np.float64); A = np.load(G / "ayet.npy").astype(np.float64)
akey = json.load(open(G / "ayet_anahtar.json")); sure = np.array([int(k.split(":")[0]) for k in akey])
kok_ayet = collections.defaultdict(list)
aidx = {k: i for i, k in enumerate(akey)}
for l in open(B / "veri_harici/eyupipler/quran-morphology.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("\t")
    if len(p) < 4: continue
    s, a, _, _ = p[0].split(":")
    r = next((t[5:] for t in p[3].split("|") if t.startswith("ROOT:")), None)
    if r in idx and f"{s}:{a}" in aidx and aidx[f"{s}:{a}"] not in kok_ayet[r]: kok_ayet[r].append(aidx[f"{s}:{a}"])
C = np.zeros_like(K)
for r, S in kok_ayet.items(): C[idx[r]] = A[S].mean(0)
C /= np.linalg.norm(C, axis=1, keepdims=True) + 1e-12
Z = K + C; Z /= np.linalg.norm(Z, axis=1, keepdims=True)
tum = np.vstack([A, K]); mu = tum.mean(0)
U, S, Vt = np.linalg.svd(tum - mu, full_matrices=False)
def proje(M, d): return (M - mu) @ Vt[:d].T
kenar = json.load(open(HERE / "metin_kenarlari.json", encoding="utf-8"))
pos = np.array([(idx[a], idx[b]) for a, b in (k.split("|") for k in kenar) if a in idx and b in idx])
rng = np.random.default_rng(3)
def auc(sp, sn):
    a = np.concatenate([sp, sn]); r = a.argsort().argsort() + 1
    return (r[:len(sp)].sum() - len(sp) * (len(sp) + 1) / 2) / (len(sp) * len(sn))
def degerlendir(J, ad):
    Nn = J - J.T
    sp = J[pos[:, 0], pos[:, 1]]
    ni = pos[rng.integers(0, len(pos), 20000), 0]; nj = pos[rng.integers(0, len(pos), 20000), 1]
    ok = ni != nj; sn = J[ni[ok], nj[ok]]
    yon = (Nn[pos[:, 0], pos[:, 1]] > 0).mean()
    print(f"{ad}: AUC(dengeli)={auc(sp, sn):.3f}  yön={yon:.3f}", flush=True)
    return dict(AUC=round(float(auc(sp, sn)), 4), yon=round(float(yon), 4))
sonuc = {}
for d in (64, 128, 256):
    Ap = proje(A, d); Zp = proje(Z, d)
    for lag in (1, 2, 3):
        X = []; Y = []
        for s in range(1, 115):
            m = np.where(sure == s)[0]
            if len(m) > lag: X.append(Ap[m[:-lag]]); Y.append(Ap[m[lag:]])
        X = np.vstack(X); Y = np.vstack(Y)
        for lam in (1.0, 100.0):
            T = np.linalg.solve(X.T @ X + lam * np.eye(d), X.T @ Y)
            J = Zp @ T @ Zp.T
            sonuc[f"d{d}_lag{lag}_lam{lam}"] = degerlendir(J, f"d={d} lag={lag} λ={lam}")
json.dump(sonuc, open(HERE / "akis_olcu.json", "w"), indent=1)
