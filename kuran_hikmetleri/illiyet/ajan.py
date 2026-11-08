import os, json, pathlib, itertools
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
B = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).resolve().parent
G = pathlib.Path(os.environ["EVREN_GOMME_DIZIN"])
rng = np.random.default_rng(17)
kokler = json.load(open(G / "kokler.json", encoding="utf-8")); idx = {k: i for i, k in enumerate(kokler)}; n = len(kokler)
D = np.load(G / "kok_anlam.npy").astype(np.float64)
Q = {a: np.load(G / f"ajan_{a}.npy").astype(np.float64) for a in ("sebep1", "sebep2", "sebep3", "netice1", "netice2", "netice3", "es", "zit")}
kenar = json.load(open(HERE / "metin_kenarlari.json", encoding="utf-8"))
pos = np.array([(idx[a], idx[b]) for a, b in (k.split("|") for k in kenar) if a in idx and b in idx])
posset = set(map(tuple, pos))
def auc(sp, sn):
    a = np.concatenate([sp, sn]); r = a.argsort().argsort() + 1
    return float((r[:len(sp)].sum() - len(sp) * (len(sp) + 1) / 2) / (len(sp) * len(sn)))
log = {}

def kavram_kesfi():
    ornek = rng.choice(n, 300, replace=False)
    def komsu(M): 
        S = M[ornek] @ M.T; S[np.arange(len(ornek)), ornek] = -9
        return np.argsort(-S, axis=1)[:, :10]
    taban = komsu(D); d = D.shape[1]
    aday = {"ortogonal_donme": lambda M: M @ np.linalg.qr(rng.normal(size=(d, d)))[0],
            "koordinat_permutasyonu": lambda M: M[:, rng.permutation(d)],
            "isaret_cevirme": lambda M: M * rng.choice([-1, 1], d),
            "ortalama_cikarma": lambda M: (M - M.mean(0)) / np.linalg.norm(M - M.mean(0), axis=1, keepdims=True),
            "beyazlatma_ilk64": lambda M: (M - M.mean(0)) @ np.linalg.svd(M - M.mean(0), full_matrices=False)[2][:64].T,
            "gurultu_0.3": lambda M: (M + .3 * rng.normal(size=M.shape) / np.sqrt(d)) / np.linalg.norm(M + .3 * rng.normal(size=M.shape) / np.sqrt(d), axis=1, keepdims=True)}
    kus = {}
    for ad, g in aday.items():
        T = g(D); T = T / np.linalg.norm(T, axis=1, keepdims=True)
        kus[ad] = round(float(1 - np.mean([len(set(a) & set(b)) / 10 for a, b in zip(taban, komsu(T))])), 4)
    return kus
log["kavram_degismezlik_kusuru"] = kavram_kesfi()

def yanit(Qe, Qc):
    return Qe @ D.T - Qc @ D.T
kombi = [(f"netice{k}", f"sebep{l}") for k in (1, 2, 3) for l in (1, 2, 3)]
R = np.stack([yanit(Q[e], Q[c]) for e, c in kombi])
C = R - R.transpose(0, 2, 1)
Ort = C.mean(0); Sd = C.std(0)
simetrik = D @ D.T

def degerlendir(M, ad):
    sp = M[pos[:, 0], pos[:, 1]]
    ni = pos[rng.integers(0, len(pos), 30000), 0]; nj = pos[rng.integers(0, len(pos), 30000), 1]
    ok = np.array([(a, b) not in posset and a != b for a, b in zip(ni, nj)])
    sn = M[ni[ok], nj[ok]]
    yon = float((M[pos[:, 0], pos[:, 1]] > M[pos[:, 1], pos[:, 0]]).mean())
    return {"AUC_dengeli": round(auc(sp, sn), 4), "yon": round(yon, 4)}
sonuc = {"cos_simetrik": degerlendir(simetrik, "cos"), "tek_gorus_C": degerlendir(C[0], "tek"), "ortalama_C": degerlendir(Ort, "ort"),
         "degismezlik_agirlikli": degerlendir(Ort / (Sd + 1e-9), "agirlikli")}
for a, v in sonuc.items(): print(a, v, flush=True)
log["olcu"] = sonuc

pozi = C[:, pos[:, 0], pos[:, 1]]
ok_sayi = (pozi > 0).sum(0)
tab = {"cezm_9_9": ok_sayi == 9, "zan_7_8": (ok_sayi >= 7) & (ok_sayi < 9), "sek_ara": (ok_sayi > 2) & (ok_sayi < 7), "ters_cezm_0_2": ok_sayi <= 2}
log["iz_an_tabakalari_gercek_baglarda"] = {k: int(v.sum()) for k, v in tab.items()}
dogru = (Ort[pos[:, 0], pos[:, 1]] > Ort[pos[:, 1], pos[:, 0]])
log["tabaka_yon_dogrulugu"] = {k: (round(float(dogru[v].mean()), 4) if v.sum() else None) for k, v in tab.items()}

Z = np.hstack([D, Q["es"]]); Z = Z / np.linalg.norm(Z, axis=1, keepdims=True)
Lk = linkage(Z, "average", metric="cosine")
from scipy.cluster.hierarchy import fcluster
gap = np.diff(Lk[::-1, 2])[:60]
kk = int(np.argmax(np.abs(gap))) + 2
kume = fcluster(Lk, kk, "maxclust") - 1
mac = np.zeros((kk, kk)); say = np.zeros((kk, kk))
for a in range(kk):
    for b in range(kk):
        ia, ib = np.where(kume == a)[0], np.where(kume == b)[0]
        if a == b: continue
        blok = C[:, ia][:, :, ib]
        mac[a, b] = blok.mean(); say[a, b] = float(np.all(blok.mean((1, 2)) > 0))
log["hasr"] = {"kume_sayisi": kk, "makro_yon_cezm_cift": int(say.sum())}
json.dump(log, open(HERE / "ajan_olcu.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(log, indent=1, ensure_ascii=False))
np.save(G / "ajan_Ort.npy", Ort); np.save(G / "ajan_kume.npy", kume)
