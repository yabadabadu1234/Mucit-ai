import glob
import re
from pathlib import Path

import numpy as np

from vektor import ONBELLEK

KOK = Path(__file__).resolve().parents[2]


def kisimlar():
    d = {}
    for f in sorted(glob.glob(str(KOK / "sureler" / "*" / "sure.md"))):
        t = open(f, encoding="utf-8").read()
        for s, k, a, b in re.findall(r"\*\*K(\d+)-(\d+)\*\* — .*?\((\d+)-(\d+)\)", t):
            d.setdefault(int(s), []).append((int(k), int(a), int(b)))
    return d


def ozellikler(sure_no, kis):
    z = np.load(ONBELLEK / ("sure%03d.npz" % sure_no))
    ayet, surp, tok = z["ayet"], z["surp"], z["tok"]
    n_ayet = int(ayet.max())
    kelime_sirasi = np.zeros(len(ayet))
    ayet_uzun = np.zeros(len(ayet))
    for a in range(1, n_ayet + 1):
        m = ayet == a
        say = int(m.sum())
        kelime_sirasi[m] = (np.arange(say) + 0.5) / say
        ayet_uzun[m] = say
    satirlar = []
    onceki = 0.0
    for w in range(len(ayet)):
        if w == 0:
            onceki = surp[w]
            continue
        a = int(ayet[w])
        konum_ayet = kelime_sirasi[w]
        sinir_ayet = min(konum_ayet, 1 - konum_ayet)
        k_bul = None
        for (k, ba, so) in kis.get(sure_no, []):
            if ba <= a <= so:
                k_bul = (ba, so)
        if k_bul is None:
            hiy_kisim = rel_kisim = sin_kisim = np.nan
            kis_ayet_sayisi = np.nan
        else:
            ba, so = k_bul
            kardes = so - ba + 1
            hiy_kisim = (a - ba + 0.5) / kardes
            rel_kisim = (a - ba + konum_ayet) / kardes
            sin_kisim = min(rel_kisim, 1 - rel_kisim)
            kis_ayet_sayisi = kardes
        hiy_sure = (a - 0.5) / n_ayet
        satirlar.append([surp[w], tok[w], onceki, konum_ayet, sinir_ayet, hiy_kisim, rel_kisim, sin_kisim, hiy_sure, ayet_uzun[w], np.log1p(w)])
        onceki = surp[w]
    return np.array(satirlar, dtype=np.float64)


def ridge_cv(X, y, grup, lam=1.0, kat=5):
    gr = np.unique(grup)
    rng = np.random.RandomState(0)
    rng.shuffle(gr)
    parca = np.array_split(gr, kat)
    hata = np.zeros(len(y))
    for p in parca:
        te = np.isin(grup, p)
        tr = ~te
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        A = (X[tr] - mu) / sd
        B = (X[te] - mu) / sd
        A1 = np.hstack([A, np.ones((len(A), 1))])
        B1 = np.hstack([B, np.ones((len(B), 1))])
        R = lam * np.eye(A1.shape[1])
        R[-1, -1] = 0
        w = np.linalg.solve(A1.T @ A1 + R, A1.T @ y[tr])
        hata[te] = (B1 @ w - y[te]) ** 2
    return hata.mean(), hata


def rolling(y, grup, n):
    out = np.zeros_like(y)
    for g in np.unique(grup):
        m = grup == g
        v = y[m]
        c = np.convolve(v, np.ones(n) / n, mode="same")
        out[m] = c
    return out


def calis():
    kis = kisimlar()
    sureler = sorted(int(Path(f).stem[4:]) for f in glob.glob(str(ONBELLEK / "sure*.npz")))
    satir, grup = [], []
    for s in sureler:
        o = ozellikler(s, kis)
        satir.append(o)
        grup += [s] * len(o)
    M = np.vstack(satir)
    grup = np.array(grup)
    ok = ~np.isnan(M[:, 5])
    print("sure", len(sureler), "kelime", len(M), "kisimli kelime", int(ok.sum()))
    M = M[ok]
    grup = grup[ok]
    y_ham = M[:, 0]
    taban = M[:, [1, 2, 9, 10]]
    aile = {
        "ayet (nesir)": M[:, [3, 4]],
        "kisim goreli konum": M[:, [6]],
        "kisim en yakin sinir": M[:, [7]],
        "kisim hiyerarsik konum": M[:, [5]],
        "sure hiyerarsik konum": M[:, [8]],
        "kisim hepsi": M[:, [5, 6, 7]],
        "bütün": M[:, [3, 4, 5, 6, 7, 8]],
    }
    for ad, y in (("kelime surpizi", y_ham), ("5'lik yurruyen ort.", rolling(y_ham, grup, 5))):
        mse0, _ = ridge_cv(taban, y, grup)
        print("\n", ad, "taban MSE", round(mse0, 4))
        for a, X in aile.items():
            mse, _ = ridge_cv(np.hstack([taban, X]), y, grup)
            print("  %-26s dMSE %+.4f" % (a, mse - mse0))


if __name__ == "__main__":
    calis()
