import json, itertools, pathlib
import numpy as np
rng = np.random.default_rng(11)

def auc(sp, sn):
    a = np.concatenate([sp, sn]); r = a.argsort().argsort() + 1
    return float((r[:len(sp)].sum() - len(sp) * (len(sp) + 1) / 2) / (len(sp) * len(sn)))

def egim(x, y):
    x = x - x.mean(); return float((x @ (y - y.mean())) / (x @ x))

def dunya(tur, ort=6, n=600):
    wa, wb = rng.uniform(.5, 1.5, 2) * rng.choice([-1, 1], 2)
    sa = []; 
    for e in range(ort):
        s = rng.uniform(.3, 3, 3)
        ez, ea, eb = rng.normal(size=(3, n)) * s[:, None]
        if tur == "ab":
            A = ea; B = wb * A + eb
        elif tur == "ba":
            B = eb; A = wb * B + ea
        else:
            Z = ez; A = wa * Z + ea; B = wb * Z + eb
        sa.append((A, B))
    return sa

def kusur(sa, yon):
    b = np.array([egim(A, B) if yon == "ab" else egim(B, A) for A, B in sa])
    return float(b.std() / (np.abs(b).mean() + 1e-9))

N = 400
S = {"ab": [], "ba": [], "kar": []}; R = {"ab": [], "ba": [], "kar": []}; Y = {"ab": [], "ba": []}
for tur in ("ab", "ba", "kar"):
    for _ in range(N):
        sa = dunya(tur)
        d_ab = kusur(sa, "ab"); d_ba = kusur(sa, "ba")
        S[tur].append(-np.log(d_ab + 1e-9)); R[tur].append(abs(np.corrcoef(*zip(*[(A, B) for A, B in [sa[0]]]))[0, 1]) if False else abs(np.corrcoef(sa[0][0], sa[0][1])[0, 1]))
        if tur != "kar": Y[tur].append(d_ab < d_ba)
olcu = {}
neg = np.array(S["ba"] + S["kar"]); pos = np.array(S["ab"])
negk = np.array(R["ba"] + R["kar"]); posk = np.array(R["ab"])
olcu["makuliyet_AUC_ab_vs_digerleri"] = round(auc(pos, neg), 4)
olcu["korelasyon_AUC_ab_vs_digerleri"] = round(auc(posk, negk), 4)
olcu["makuliyet_AUC_ab_vs_karisik"] = round(auc(pos, np.array(S["kar"])), 4)
olcu["korelasyon_AUC_ab_vs_karisik"] = round(auc(posk, np.array(R["kar"])), 4)
olcu["yon_dogrulugu_ab"] = round(float(np.mean(Y["ab"])), 4)
olcu["yon_dogrulugu_ba_dogru_ters"] = round(float(1 - np.mean(Y["ba"])), 4)
eps = 0.05
tab = {}
for n in (3, 5, 10, 20, 40):
    lam = n * np.log((1 - eps) / eps)
    p = 1 / (1 + 4 * np.exp(-lam))
    tab[n] = {"Lambda_nat": round(float(lam), 2), "sonsel_olasilik": float(p), "elenme_ile": "Lambda=sonsuz, olasilik=1 tam"}
olcu["iz_an_tabakalari"] = tab
n = 4; perm = list(itertools.permutations(range(n)))
def ornek(m, sirali):
    x = rng.dirichlet(np.ones(n), m)
    return -np.sort(-x, axis=1) if sirali else x
def adalet(x): return n * x.min(axis=1)
def oz(x):
    cols = [np.ones(len(x))]
    for d in (1, 2, 3):
        for c in itertools.combinations_with_replacement(range(n), d): cols.append(np.prod(x[:, c], axis=1))
    return np.stack(cols, 1)
Xt = ornek(3000, True); yt = adalet(Xt)
Fm = oz(Xt); w = np.linalg.solve(Fm.T @ Fm + 1e-6 * np.eye(Fm.shape[1]), Fm.T @ yt)
f = lambda x: oz(x) @ w
Xs = ornek(2000, True); Xp = np.stack([x[np.array(perm[rng.integers(len(perm))])] for x in ornek(2000, True)])
fs = lambda x: np.mean([f(x[:, list(p)]) for p in perm], axis=0)
rm = lambda a, b: round(float(np.sqrt(np.mean((a - b) ** 2))), 4)
olcu["adalet_kavrami"] = {
    "egitim_bolgesinde_RMSE": rm(f(Xs), adalet(Xs)),
    "permute_edilmis_RMSE": rm(f(Xp), adalet(Xp)),
    "simetrilestirilmis_permute_RMSE": rm(fs(Xp), adalet(Xp)),
    "degismezlik_kusuru_ogrenilen": round(float(np.mean(np.abs(f(Xp) - f(Xp[:, ::-1])))), 4),
    "degismezlik_kusuru_tanimdan": 0.0}
json.dump(olcu, open(pathlib.Path(__file__).with_name("muhakeme_olcu.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(olcu, indent=1, ensure_ascii=False))
