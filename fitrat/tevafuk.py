"""Tevâfuk — bağımsız şahitlerin birbirini teyidinin ölçülmesi.

Birden çok delil aynı hükmü gösteriyorsa bu, hükmü kuvvetlendirir.
Ama **ne kadar** kuvvetlendirdiği, delillerin birbirinden ne kadar
bağımsız olduğuna bağlıdır: aynı kaynaktan beslenen on şahit, bir
şahitten pek fazlasını söylemez.

Bu yüzden tevâfuk ölçüsü **çift bazında** ve şartlı bağımsızlıkla
ağırlıklandırılarak kurulur:

.. math::

   \\mathrm{Tevafuk} = \\frac{2}{m(m-1)}
      \\sum_{k<l} w_{kl}\\; a(d_k, d_l),
   \\qquad w_{kl} = 1 - \\bigl|\\rho(d_k, d_l \\mid H)\\bigr|

``a(·,·)`` iki delilin aynı yöne işaret edip etmediği, ``ρ(·,·|H)``
ise **hüküm verildiğinde** aralarında kalan artık bağıntıdır.  Hüküm
şarta bağlandıktan sonra hâlâ bağıntılıysalar, ortak bir başka
kaynakları var demektir ve o çiftin katkısı kısılır.

Toplamın ``k < l`` üzerinden gitmesi ve ``2/(m(m−1))`` ile normalize
edilmesi kasıtlıdır: her çift **bir kere** sayılır, hiçbir delil
kendisiyle tevâfuk etmiş sayılmaz, ve ölçü delil sayısından bağımsız
olarak ``[−1, 1]`` aralığında kalır.

Ayrıca **Bayes teyit ölçüsü**: bağımsız şahitler için log-olabilirlik
oranları toplanır,

.. math::  \\ln\\frac{P(H|D)}{P(\\neg H|D)}
           = \\ln\\frac{P(H)}{P(\\neg H)} + \\sum_k \\ln \\Lambda_k

Bağımlılık varsa bu toplam **fazla sayar**; modül fazla saymanın
miktarını da ölçer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "sartli_bagintisi", "cift_uyusmasi", "tevafuk_olcusu",
    "log_olabilirlik_orani", "bayes_yigma", "fazla_sayma",
    "sahit_uret",
]


# ══════════════════════════════════════════════════════════════════════
#  Şartlı bağıntı
# ══════════════════════════════════════════════════════════════════════

def _pearson(u: np.ndarray, v: np.ndarray) -> float:
    """Sabit değişkende 0 döner — sıfıra bölmek yerine 'bağıntı yok'."""
    u = np.asarray(u, float); v = np.asarray(v, float)
    if u.size < 2:
        return 0.0
    du, dv = u - u.mean(), v - v.mean()
    payda = np.sqrt(float(du @ du) * float(dv @ dv))
    if payda < 1e-15:
        return 0.0
    return float(du @ dv / payda)


def sartli_bagintisi(dk: np.ndarray, dl: np.ndarray,
                     H: np.ndarray) -> float:
    """``ρ(d_k, d_l | H)`` — hüküm katmanlarında ağırlıklı ortalama.

    ``H`` ikili (0/1) olduğundan şartlı bağıntı, iki katmanda ayrı ayrı
    hesaplanıp katman büyüklüğüyle ağırlıklandırılır.  Bu, kısmî
    bağıntı (partial correlation) formülüne göre daha doğrudandır ve
    ``H``in ikili olduğu hâlde tam sonucu verir; kısmî bağıntı ise
    doğrusallık farz eder.

    Bir katmanda 2'den az örnek varsa o katman **atlanır** (ağırlığı
    sıfırdır); iki örnekten bağıntı uydurulmaz.
    """
    dk = np.asarray(dk, float); dl = np.asarray(dl, float)
    H = np.asarray(H)
    toplam, agirlik = 0.0, 0.0
    for h in (0, 1):
        m = H == h
        n = int(m.sum())
        if n < 3:
            continue
        toplam += n * _pearson(dk[m], dl[m])
        agirlik += n
    return toplam / agirlik if agirlik > 0 else 0.0


def cift_uyusmasi(dk: np.ndarray, dl: np.ndarray) -> float:
    """``a(d_k, d_l)`` — iki delil aynı yöne mi işaret ediyor?

    Ham Pearson bağıntısı kullanılır: ``+1`` tam uyuşma, ``−1`` tam
    zıtlık, ``0`` alâkasızlık.
    """
    return _pearson(dk, dl)


def tevafuk_olcusu(deliller: Sequence[np.ndarray], H: np.ndarray
                   ) -> Dict[str, object]:
    """Şartlı-bağımsızlıkla ağırlıklandırılmış tevâfuk.

    ``m < 2`` ise tevâfuk tanımsızdır (tek şahit kendisiyle tevâfuk
    etmez); ``None`` döner, sıfır değil — ikisi ayrı şeydir.
    """
    m = len(deliller)
    if m < 2:
        return {"tevafuk": None, "çift_sayısı": 0, "çiftler": [],
                "sebep": "en az iki delil lazım"}
    H = np.asarray(H)
    ciftler: List[Dict[str, float]] = []
    toplam = 0.0
    for k in range(m):
        for l in range(k + 1, m):           # k < l : her çift BİR kere
            a = cift_uyusmasi(deliller[k], deliller[l])
            rho = sartli_bagintisi(deliller[k], deliller[l], H)
            w = 1.0 - abs(rho)
            toplam += w * a
            ciftler.append({"k": k, "l": l, "uyuşma": a,
                            "artık_bağıntı": rho, "ağırlık": w,
                            "katkı": w * a})
    n_cift = m * (m - 1) // 2
    return {
        "tevafuk": toplam / n_cift,
        "ağırlıksız_tevafuk": sum(c["uyuşma"] for c in ciftler) / n_cift,
        "çift_sayısı": n_cift,
        "çiftler": ciftler,
    }


# ══════════════════════════════════════════════════════════════════════
#  Bayes yığma
# ══════════════════════════════════════════════════════════════════════

def log_olabilirlik_orani(d: np.ndarray, H: np.ndarray,
                          duzeltme: float = 0.5) -> float:
    """``ln Λ = ln[P(d=1|H)/P(d=1|¬H)]`` — ikili delil için.

    ``duzeltme`` Jeffreys düzeltmesidir (her hücreye ½): örneklem
    küçükken sıfır hücre ``ln 0 = −∞`` verir ve bir şahit tek başına
    hükmü kesinleştirir.  Düzeltme bunu engeller ve **taraf tutmaz**
    (her iki hücreye de aynı miktarda eklenir).
    """
    d = np.asarray(d).astype(int)
    H = np.asarray(H).astype(int)
    p1 = (float(np.sum(d[H == 1])) + duzeltme) / (float(np.sum(H == 1))
                                                  + 2 * duzeltme)
    p0 = (float(np.sum(d[H == 0])) + duzeltme) / (float(np.sum(H == 0))
                                                  + 2 * duzeltme)
    return float(np.log(p1 / p0))


def bayes_yigma(deliller: Sequence[np.ndarray], H: np.ndarray,
                onsel_oran: float = 1.0) -> Dict[str, object]:
    """Bağımsızlık farzıyla log-oranların toplanması."""
    lo = [log_olabilirlik_orani(d, H) for d in deliller]
    return {"log_Λ'lar": lo, "toplam": float(np.sum(lo)),
            "ardıl_log_oran": float(np.log(onsel_oran) + np.sum(lo))}


def fazla_sayma(deliller: Sequence[np.ndarray], H: np.ndarray
                ) -> Dict[str, object]:
    """Bağımsızlık farzı ne kadar fazla saydırıyor?

    Ölçüt: bütün delillerin toplamı ile, **birbiriyle en az bağıntılı**
    tek delilin katkısının karşılaştırılması değil — bu yanıltırdı.
    Bunun yerine tevâfuk ağırlıklarının ortalaması alınır: ağırlık 1'e
    ne kadar yakınsa yığma o kadar meşrudur.  Ağırlıklı toplam,
    fiilen "kaç bağımsız şahide denk geldiğini" verir.
    """
    t = tevafuk_olcusu(deliller, H)
    if t["tevafuk"] is None:
        return {"muteber_şahit_sayısı": float(len(deliller)),
                "sebep": t["sebep"]}
    y = bayes_yigma(deliller, H)
    ort_agirlik = float(np.mean([c["ağırlık"] for c in t["çiftler"]]))
    m = len(deliller)
    # m şahidin fiilî sayısı: tam bağımsızsa m, tam bağımlıysa 1.
    muteber = 1.0 + (m - 1.0) * ort_agirlik
    return {
        "şahit_sayısı": m,
        "ortalama_ağırlık": ort_agirlik,
        "muteber_şahit_sayısı": muteber,
        "ham_toplam_logΛ": y["toplam"],
        "düzeltilmiş_logΛ": y["toplam"] * muteber / m,
        "fazla_sayma_oranı": m / muteber if muteber > 0 else float("inf"),
    }


# ══════════════════════════════════════════════════════════════════════
#  Şahit üretimi — sağlamalar için
# ══════════════════════════════════════════════════════════════════════

def sahit_uret(n: int, m: int, dogruluk: float, ortak_kaynak: float,
               tohum: int = 0) -> Tuple[np.ndarray, List[np.ndarray]]:
    """``m`` şahit üret; ``ortak_kaynak`` bağımlılığın şiddeti.

    Her şahit, olasılık ``dogruluk`` ile hükmü doğru bildirir.  Ayrıca
    ``ortak_kaynak`` olasılığıyla, kendi gözlemi yerine **ortak bir
    gürültü kaynağını** bildirir — bu, "hepsi aynı dedikoduyu duymuş"
    hâlidir ve şahitler arasında hüküm verildikten sonra da kalan bir
    bağıntı doğurur.

    ``ortak_kaynak = 0`` iken şahitler ``H`` verildiğinde şartlı
    bağımsızdır; ``1`` iken hepsi tek bir şahide iner.
    """
    r = np.random.default_rng(tohum)
    H = r.integers(0, 2, n)
    ortak = r.integers(0, 2, n)
    deliller = []
    for _ in range(m):
        kendi = np.where(r.random(n) < dogruluk, H, 1 - H)
        ortak_mi = r.random(n) < ortak_kaynak
        deliller.append(np.where(ortak_mi, ortak, kendi))
    return H, deliller


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s: List[str] = []
    n, m = 4000, 5

    s.append("=== Tevâfuk: bağımsız şahitler v ortak kaynaklı şahitler ===")
    s.append(f"  n={n} müşahede, m={m} şahit, her birinin doğruluğu 0.80")
    s.append("")
    s.append("  ortak_kaynak   tevafuk  ağırlıksız  ort.ağırlık"
             "  muteber şahit  fazla sayma")
    for ok in (0.0, 0.2, 0.5, 0.8, 1.0):
        H, D = sahit_uret(n, m, 0.80, ok, tohum=42)
        t = tevafuk_olcusu(D, H)
        f = fazla_sayma(D, H)
        s.append(f"    {ok:.1f}          {t['tevafuk']:+.4f}   "
                 f"{t['ağırlıksız_tevafuk']:+.4f}      "
                 f"{f['ortalama_ağırlık']:.4f}        "
                 f"{f['muteber_şahit_sayısı']:.3f}         "
                 f"{f['fazla_sayma_oranı']:.3f}")
    s.append("")
    s.append("  Ağırlıksız tevâfuk TEKDÜZE DEĞİL: önce düşüyor (0→0.2),")
    s.append("  sonra 1'e tırmanıyor. Sebebi ölçülebilir: az miktarda ortak")
    s.append("  kaynak, şahitlerin bir kısmını H ile alâkasız bir işarete")
    s.append("  çevirdiği için önce uyuşmayı SEYRELTİYOR; kaynak baskın")
    s.append("  hâle gelince ise şahitler birbirinin kopyası oluyor.")
    s.append("  Ağırlıklı ölçü ve muteber şahit sayısı ise tekdüze düşüyor —")
    s.append("  aranan da budur: ham uyuşma yanıltır, artık bağıntı yanıltmaz.")

    s.append("\n=== Bayes yığma fazla sayıyor mu? ===")
    for ok in (0.0, 0.8):
        H, D = sahit_uret(n, m, 0.80, ok, tohum=7)
        f = fazla_sayma(D, H)
        s.append(f"  ortak_kaynak={ok}: ham Σlog Λ = {f['ham_toplam_logΛ']:.4f}"
                 f"  düzeltilmiş = {f['düzeltilmiş_logΛ']:.4f}"
                 f"  (muteber {f['muteber_şahit_sayısı']:.2f}/{m} şahit)")

    s.append("\n=== Sınır hâlleri ===")
    H, D = sahit_uret(n, 1, 0.8, 0.0, tohum=1)
    s.append(f"  tek şahitte tevâfuk = {tevafuk_olcusu(D, H)['tevafuk']}"
             "   (sıfır değil — TANIMSIZ)")
    H, D = sahit_uret(n, 2, 0.8, 0.0, tohum=1)
    t = tevafuk_olcusu(D, H)
    s.append(f"  iki bağımsız şahit: çift sayısı = {t['çift_sayısı']}"
             f"  tevafuk = {t['tevafuk']:+.4f}")
    # Birbirinin tam zıddı iki şahit
    H2 = np.array([0, 1] * 500)
    d1 = H2.copy(); d2 = 1 - H2
    t2 = tevafuk_olcusu([d1, d2], H2)
    s.append(f"  tam zıt iki şahit: uyuşma = "
             f"{t2['çiftler'][0]['uyuşma']:+.1f}"
             f"  tevafuk = {t2['tevafuk']:+.4f}")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
