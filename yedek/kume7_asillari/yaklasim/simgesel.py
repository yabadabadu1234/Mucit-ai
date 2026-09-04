"""
Simgesel bağlanım: kapalı biçimli bir ifade ARAMAK.

Sayısal yaklaşım bir tablo verir; simgesel bağlanım bir FORMÜL verir.
Formülün kıymeti dışdeğerlemededir (extrapolation): tablo, verinin
görülmediği yerde hiçbir şey söylemez; formül söyler -- doğru formülse.

Burada SINDy usulü kullanılır: bir aday terim kütüphanesi kurulur,
her alt küme için en küçük kareler çözülür, ve modeller **Occam cezası**
ile sıralanır. Ceza olarak BIC alınır:

    BIC = m·log(RSS/m) + k·log m          (m: örnek, k: terim sayısı)

Üç şey ölçülür:
  1. Temiz veride doğru formül tam olarak bulunuyor mu?
  2. Gürültülü veride ceza, gereksiz terimleri eliyor mu?
  3. **Zaaf**: doğru formül kütüphanenin DIŞINDAYSA ne oluyor? (Cevap:
     usul sessizce yanlış bir formül döndürür; "bulamadım" demez.)
"""
from __future__ import annotations

from itertools import combinations
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np

Terim = Tuple[str, Callable[[np.ndarray], np.ndarray]]


def varsayilan_kutuphane() -> List[Terim]:
    return [
        ("1", lambda x: np.ones_like(x)),
        ("x", lambda x: x),
        ("x^2", lambda x: x * x),
        ("x^3", lambda x: x ** 3),
        ("sin x", lambda x: np.sin(x)),
        ("cos x", lambda x: np.cos(x)),
        ("exp x", lambda x: np.exp(x)),
        ("1/(1+x^2)", lambda x: 1.0 / (1.0 + x * x)),
    ]


def _uydur(
    x: np.ndarray, y: np.ndarray, terimler: Sequence[Terim]
) -> Tuple[np.ndarray, float]:
    A = np.stack([f(x) for _, f in terimler], axis=1)
    kat, *_ = np.linalg.lstsq(A, y, rcond=None)
    rss = float(np.sum((A @ kat - y) ** 2))
    return kat, rss


def bic(rss: float, m: int, k: int, taban: float = 1e-20) -> float:
    """BIC; ``taban`` sayısal gürültü zeminidir.

    Tabansız hâlde temiz veride iki farklı model ``RSS ≈ 10⁻²⁸`` ve
    ``10⁻²⁹`` verir; bu fark ANLAMSIZDIR (yuvarlama), fakat ``m·log RSS``
    onu ``m·log 10`` kadar büyütüp fazla terimli modeli seçtirir. Ölçüm
    sırasında tam olarak bu oldu: 2 terimli doğru model yerine 3 terimli
    bir model kazandı. Taban, kayan noktalı sıfırı sıfır saymaktır.
    """
    return m * np.log(max(rss, taban * m) / m) + k * np.log(m)


def ara(
    x: np.ndarray,
    y: np.ndarray,
    kutuphane: Sequence[Terim] | None = None,
    azami_terim: int = 3,
) -> Dict[str, object]:
    """Kütüphanenin ``≤ azami_terim`` boyutlu bütün alt kümelerini tarar."""
    kutuphane = list(kutuphane or varsayilan_kutuphane())
    m = len(x)
    en_iyi = None
    sirali: List[Tuple[float, Tuple[str, ...], np.ndarray, float]] = []
    for k in range(1, azami_terim + 1):
        for alt in combinations(range(len(kutuphane)), k):
            secilen = [kutuphane[i] for i in alt]
            kat, rss = _uydur(x, y, secilen)
            skor = bic(rss, m, k)
            adlar = tuple(ad for ad, _ in secilen)
            sirali.append((skor, adlar, kat, rss))
            if en_iyi is None or skor < en_iyi[0]:
                en_iyi = (skor, adlar, kat, rss)
    sirali.sort(key=lambda t: t[0])
    skor, adlar, kat, rss = en_iyi  # type: ignore[misc]
    return {
        "formul": " + ".join("%.4f·%s" % (c, a) for c, a in zip(kat, adlar)),
        "terimler": adlar,
        "katsayilar": kat,
        "rss": rss,
        "bic": skor,
        "ilk_bes": [(round(s, 2), a) for s, a, _, _ in sirali[:5]],
    }


# =====================================================================
#  Sınamalar
# =====================================================================
def temiz_veride_bulunuyor_mu() -> Dict[str, object]:
    """``y = 2x² − 3sin x``: doğru terim kümesi tam olarak bulunmalı."""
    x = np.linspace(-2, 2, 200)
    y = 2.0 * x * x - 3.0 * np.sin(x)
    r = ara(x, y)
    return {
        "bulunan": r["formul"],
        "terimler": r["terimler"],
        "dogru_terimler": bool(set(r["terimler"]) == {"x^2", "sin x"}),
        "katsayilar_dogru": bool(
            np.allclose(sorted(r["katsayilar"]), sorted([2.0, -3.0]), atol=1e-8)
        ),
        "rss": r["rss"],
    }


def ceza_fazla_terimi_eliyor_mu(gurultu: float = 0.05, tohum: int = 0) -> Dict[str, object]:
    """Gürültülü veride: cezasız ölçüt (RSS) hep en büyük modeli seçer,
    BIC ise doğru boyutta durur."""
    rng = np.random.default_rng(tohum)
    x = np.linspace(-2, 2, 200)
    y = 2.0 * x * x - 3.0 * np.sin(x) + gurultu * rng.normal(size=x.size)
    kut = varsayilan_kutuphane()

    en_iyi_rss = None
    for k in range(1, 4):
        for alt in combinations(range(len(kut)), k):
            _, rss = _uydur(x, y, [kut[i] for i in alt])
            adlar = tuple(kut[i][0] for i in alt)
            if en_iyi_rss is None or rss < en_iyi_rss[0]:
                en_iyi_rss = (rss, adlar)

    r = ara(x, y)
    return {
        "rss_secimi": en_iyi_rss[1],
        "rss_secimi_boyut": len(en_iyi_rss[1]),
        "bic_secimi": r["terimler"],
        "bic_secimi_boyut": len(r["terimler"]),
        "bic_daha_sade": bool(len(r["terimler"]) < len(en_iyi_rss[1])),
        "bic_dogruyu_buldu": bool(set(r["terimler"]) == {"x^2", "sin x"}),
    }


def kutuphane_disinda_ne_oluyor() -> Dict[str, object]:
    """**Zaaf.** Hedef ``y = log(2+x)``; kütüphanede logaritma YOK.

    Usul yine de bir formül döndürür ve o formül ARALIKTA iyi görünür.
    Yanlışlık ancak DIŞARIDA ortaya çıkar. Yani simgesel bağlanımın
    çıktısı 'kanun' diye okunamaz; ancak kütüphane doğru kurulduysa
    kanundur.
    """
    x = np.linspace(-1, 1, 200)
    y = np.log(2.0 + x)
    r = ara(x, y)
    kut = dict(varsayilan_kutuphane())
    A_ic = np.stack([kut[a](x) for a in r["terimler"]], axis=1)
    ic_hata = float(np.sqrt(np.mean((A_ic @ r["katsayilar"] - y) ** 2)))

    xd = np.linspace(3, 8, 200)          # eğitim aralığının DIŞI
    yd = np.log(2.0 + xd)
    A_dis = np.stack([kut[a](xd) for a in r["terimler"]], axis=1)
    dis_hata = float(np.sqrt(np.mean((A_dis @ r["katsayilar"] - yd) ** 2)))
    return {
        "bulunan": r["formul"],
        "aralik_ici_hata": ic_hata,
        "aralik_disi_hata": dis_hata,
        # hedefin aralık içi salınımı ~1.1; %1'in altı "iyi görünüyor"dur
        "hedef_genligi": float(np.max(y) - np.min(y)),
        "icerde_iyi_gorunuyor": bool(ic_hata < 0.01 * (np.max(y) - np.min(y))),
        "disarida_bozuluyor": bool(dis_hata > 100 * max(ic_hata, 1e-12)),
        "usul_bilmedigini_soylemiyor": True,
    }


def rapor() -> str:
    s = ["=== simgesel ==="]
    a = temiz_veride_bulunuyor_mu()
    s.append("temiz veri   %s   (doğru terimler=%s, katsayılar=%s, rss=%.2e)"
             % (a["bulunan"], a["dogru_terimler"], a["katsayilar_dogru"], a["rss"]))
    b = ceza_fazla_terimi_eliyor_mu()
    s.append("Occam cezası RSS seçimi=%s (k=%d) | BIC seçimi=%s (k=%d) | BIC sade=%s doğru=%s"
             % (b["rss_secimi"], b["rss_secimi_boyut"], b["bic_secimi"],
                b["bic_secimi_boyut"], b["bic_daha_sade"], b["bic_dogruyu_buldu"]))
    c = kutuphane_disinda_ne_oluyor()
    s.append("zaaf         log(2+x) için bulunan: %s" % c["bulunan"])
    s.append("             aralık içi=%.2e  aralık dışı=%.4g  içerde iyi=%s dışarıda bozuk=%s"
             % (c["aralik_ici_hata"], c["aralik_disi_hata"],
                c["icerde_iyi_gorunuyor"], c["disarida_bozuluyor"]))
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
