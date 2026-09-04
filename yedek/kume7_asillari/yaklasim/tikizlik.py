"""
Varlık: tıkızlık, zorlayıcılık ve tıkızlaştırmanın sınırı.

Eniyilemede iki ayrı soru vardır ve karıştırılmaları en pahalı hatadır:

  * **Var mı?** -- asgarînin varlığı bir TOPOLOJİ meselesidir. Weierstrass:
    tıkız bir kümede sürekli fonksiyon asgarîsine ulaşır. Tıkız olmayan
    uzayda ise infimum var olsa bile ULAŞILMAYABİLİR.
  * **Bulunur mu?** -- bu ayrı bir mesele (bkz. ``kara_kutu``).

``ℝⁿ`` tıkız değildir; kurtarıcı kavram **zorlayıcılıktır** (coercivity):
``‖x‖ → ∞`` iken ``f(x) → ∞`` ise, alt seviye kümeleri ``{f ≤ c}``
kapalı ve SINIRLIDIR, yani tıkızdır; asgarî oradadır. Zorlayıcılık bir
"iyi davranış temennisi" değil, tıkızlığın yerine geçen KESİN şarttır.

Tıkızlaştırma (bir noktada ``+∞`` ekleyerek) her zaman kurtarmaz: bu
dosya, tıkızlaştırmanın **sürekli genişlemeye** izin vermediği iki
klasik karşı örneği sayısal olarak gösterir.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import numpy as np


# =====================================================================
#  1. Zorlayıcılık ⟹ asgarî var
# =====================================================================
def zorlayici_mi(
    f: Callable[[np.ndarray], float],
    boyut: int,
    yaricaplar: Tuple[float, ...] = (1.0, 10.0, 100.0, 1000.0),
    yon_sayisi: int = 200,
    tohum: int = 0,
) -> Dict[str, object]:
    """Zorlayıcılığın SAYISAL delili: küre üzerindeki asgarî değer,
    yarıçap büyüdükçe artıyor mu?

    Bu bir ispat değildir -- sonlu örnekleme ancak *delil* verir. Delilin
    sınırı burada açıkça yazılıdır: yön sayısı sonludur, dolayısıyla dar
    bir "kaçış koridoru" gözden kaçabilir.

    Bu tuzağa yazarken bizzat düşüldü: yalnız rastgele yönlerle
    ``f(x)=Σ_{i≥1}xᵢ²`` (``x₀`` ekseni boyunca sabit sıfır) ZORLAYICI
    göründü, çünkü rastgele bir yön eksene tam oturmaz. Bu yüzden
    **koordinat eksenleri her zaman yön kümesine katılır**; kaçış
    koridorları çoğu zaman eksenlerdedir.
    """
    rng = np.random.default_rng(tohum)
    eksenler = np.concatenate([np.eye(boyut), -np.eye(boyut)], axis=0)
    yonler = rng.normal(size=(yon_sayisi, boyut))
    yonler /= np.linalg.norm(yonler, axis=1, keepdims=True)
    yonler = np.concatenate([eksenler, yonler], axis=0)
    asgariler = []
    for R in yaricaplar:
        degerler = [f(R * u) for u in yonler]
        asgariler.append(float(min(degerler)))
    artiyor = all(asgariler[i] < asgariler[i + 1] for i in range(len(asgariler) - 1))
    return {
        "yaricaplar": list(yaricaplar),
        "kure_asgarileri": asgariler,
        "delil_artiyor": artiyor,
        "kayit": "sonlu yön örneklemesi; ispat değil delil",
    }


def alt_seviye_sinirli_mi(
    f: Callable[[np.ndarray], float],
    boyut: int,
    c: float,
    azami_yaricap: float = 1e4,
    ornek: int = 5000,
    tohum: int = 0,
) -> Dict[str, object]:
    """``{f ≤ c}`` kümesinin sınırlı görünüp görünmediğini yoklar.

    ``zorlayici_mi`` ile aynı ihtiyat: koordinat eksenleri örnekleme
    kümesine zorla katılır, yoksa eksen boyunca uzanan sınırsız bir alt
    seviye kümesi görünmez.
    """
    rng = np.random.default_rng(tohum)
    # logaritmik yarıçap taraması: uzakta hâlâ c'nin altına inen var mı?
    R = np.exp(rng.uniform(np.log(1e-2), np.log(azami_yaricap), size=ornek))
    U = rng.normal(size=(ornek, boyut))
    U /= np.linalg.norm(U, axis=1, keepdims=True)
    eksenler = np.concatenate([np.eye(boyut), -np.eye(boyut)], axis=0)
    U[: len(eksenler)] = eksenler
    R[: len(eksenler)] = azami_yaricap
    X = R[:, None] * U
    icinde = np.array([f(x) <= c for x in X])
    if not icinde.any():
        return {"c": c, "nokta_yok": True, "azami_norm": 0.0, "sinirli_gorunuyor": True}
    azami = float(np.max(np.linalg.norm(X[icinde], axis=1)))
    return {
        "c": c,
        "nokta_yok": False,
        "azami_norm": azami,
        "sinirli_gorunuyor": bool(azami < azami_yaricap * 0.5),
    }


# =====================================================================
#  2. Zorlayıcı OLMAYAN: infimum var, asgarî yok
# =====================================================================
def ulasilmayan_infimum(adim: int = 30) -> Dict[str, object]:
    """``f(x) = e^{−x}`` üzerinde ``ℝ``: ``inf f = 0`` fakat ``f(x) > 0``.

    Gradyan inişi sonsuza kaçar; her adımda "iyileşir", hiçbir zaman
    varmaz. Eniyilemenin başarısızlığı burada usulün kusuru DEĞİLDİR --
    çözüm kümesi boştur.
    """
    x = 0.0
    yol = []
    for _ in range(adim):
        # f' = -e^{-x};  büyük adım ölçekli iniş
        x = x - 10.0 * (-np.exp(-x))
        yol.append((x, float(np.exp(-x))))
    return {
        "son_x": yol[-1][0],
        "son_f": yol[-1][1],
        "infimum": 0.0,
        "kaciyor": yol[-1][0] > yol[0][0] * 10 or yol[-1][0] > 10.0,
        "asgari_ulasilmadi": yol[-1][1] > 0.0,
    }


# =====================================================================
#  3. Tıkızlaştırılamayanlar
# =====================================================================
def sin_bir_bolu_x(yaklasim_sayisi: int = 40) -> Dict[str, object]:
    """``sin(1/x)``: ``x → 0`` iken limit YOKTUR.

    ``(0, 1]`` aralığına ``x = 0`` noktasını ekleyip fonksiyonu sürekli
    genişletmek imkânsızdır: 0'a giden iki dizi seçilir, biri boyunca
    fonksiyon ``+1``e, öbürü boyunca ``−1``e gider. Tıkızlaştırma
    kümeyi tıkız yapar ama fonksiyonu sürekli yapmaz -- Weierstrass'ın
    şartı sağlanmaz.
    """
    k = np.arange(1, yaklasim_sayisi + 1)
    x_arti = 1.0 / (2 * np.pi * k + np.pi / 2)     # sin(1/x) = +1
    x_eksi = 1.0 / (2 * np.pi * k - np.pi / 2)     # sin(1/x) = -1
    f_arti = np.sin(1.0 / x_arti)
    f_eksi = np.sin(1.0 / x_eksi)
    return {
        "x_arti_son": float(x_arti[-1]),
        "x_eksi_son": float(x_eksi[-1]),
        "limit_arti": float(np.max(np.abs(f_arti - 1.0))),
        "limit_eksi": float(np.max(np.abs(f_eksi + 1.0))),
        "iki_dizi_de_sifira_gidiyor": bool(x_arti[-1] < 1e-2 and x_eksi[-1] < 1e-2),
        "limitler_ayrisiyor": bool(
            np.allclose(f_arti, 1.0, atol=1e-12) and np.allclose(f_eksi, -1.0, atol=1e-12)
        ),
    }


def yon_bagimli_limit(yaklasim_sayisi: int = 12) -> Dict[str, object]:
    """``(x²−y²)/(x²+y²)``: orijindeki limit YÖNE bağlıdır.

    Kutupsalda değer ``cos 2θ``dır; yarıçaptan bağımsızdır. Yani orijine
    hangi doğru boyunca yaklaşırsan o doğrunun değerini görürsün. Bu
    fonksiyon delinmiş düzlemde her yerde tanımlı ve süreklidir, fakat
    orijine sürekli genişletilemez.
    """
    r = 10.0 ** (-np.arange(1, yaklasim_sayisi + 1, dtype=float))
    aciler = [0.0, np.pi / 4, np.pi / 2, np.pi / 3]
    izler = {}
    for th in aciler:
        x, y = r * np.cos(th), r * np.sin(th)
        izler[round(th, 6)] = float(((x * x - y * y) / (x * x + y * y))[-1])
    degerler = list(izler.values())
    return {
        "yarıcap_son": float(r[-1]),
        "yone_gore_limitler": izler,
        "cos2theta_ile_uyusuyor": all(
            abs(izler[round(th, 6)] - np.cos(2 * th)) < 1e-12 for th in aciler
        ),
        "limit_yok": bool(max(degerler) - min(degerler) > 0.5),
    }


# =====================================================================
#  4. Örnek hedefler
# =====================================================================
def kare(x: np.ndarray) -> float:
    return float(np.sum(x * x))


def rosenbrock(x: np.ndarray) -> float:
    return float(np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2))


def zorlayici_olmayan(x: np.ndarray) -> float:
    """``x₀`` ekseni boyunca sabit: alt seviye kümesi sınırsız."""
    return float(np.sum(x[1:] ** 2))


def rapor() -> str:
    s = ["=== tikizlik ==="]
    z = zorlayici_mi(kare, 3)
    s.append("zorlayıcı(‖x‖²)  küre asgarileri=%s  artıyor=%s"
             % ([round(v, 3) for v in z["kure_asgarileri"]], z["delil_artiyor"]))
    zn = zorlayici_mi(zorlayici_olmayan, 3)
    s.append("zorlayıcı değil    küre asgarileri=%s  artıyor=%s"
             % ([round(v, 6) for v in zn["kure_asgarileri"]], zn["delil_artiyor"]))
    a = alt_seviye_sinirli_mi(kare, 3, c=4.0)
    b = alt_seviye_sinirli_mi(zorlayici_olmayan, 3, c=4.0)
    s.append("alt seviye {f≤4}  ‖x‖²: azami norm=%.3g sınırlı=%s   |   sınırsız hâl: azami norm=%.3g sınırlı=%s"
             % (a["azami_norm"], a["sinirli_gorunuyor"], b["azami_norm"], b["sinirli_gorunuyor"]))
    u = ulasilmayan_infimum()
    s.append("ulaşılmayan inf   son f=%.3g > inf=0 → %s (x kaçıyor=%s)"
             % (u["son_f"], u["asgari_ulasilmadi"], u["kaciyor"]))
    p = sin_bir_bolu_x()
    s.append("sin(1/x)          iki dizi 0'a gidiyor=%s, limitler ±1'e ayrışıyor=%s"
             % (p["iki_dizi_de_sifira_gidiyor"], p["limitler_ayrisiyor"]))
    q = yon_bagimli_limit()
    s.append("(x²−y²)/(x²+y²)   cos2θ ile uyuşuyor=%s, limit yok=%s"
             % (q["cos2theta_ile_uyusuyor"], q["limit_yok"]))
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
