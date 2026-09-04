"""
Çok değerli, bulanık ve paratutarlı mantıklar.

Bu dosyanın omurgası **kalıntı (residuation) bağıntısıdır**:

    a ⊗ b ≤ c   ⟺   a ≤ (b → c)

Bir t-normu ile bir gerektirmenin AYNI cebre ait olmasının ölçütü budur.
Kaynak metinlerdeki T89 tashihi tam olarak buradan çıkıyordu:
Łukasiewicz gerektirmesi ``min(1, 1−a+b)``, ``min``in değil **kuvvetli
ve**in (``max(0, a+b−1)``) kalıntısıdır. Aşağıda ikisi de ızgarada
sınanır ve ``min`` ile bağıntının BOZULDUĞU somut bir üçlü gösterilir.

Ayrıca her t-normu için dört aksiyom (değişme, birleşme, tekdüzelik,
birim) ızgarada denetlenir; sınır hâlleri (``a=0``, ``b=0``) ayrıca
yoklanır -- T90 ve T94 tashihlerinin sebebi oydu.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

TNorm = Callable[[float, float], float]
Kalinti = Callable[[float, float], float]

EPS = 1e-9


def _izgara(n: int = 21) -> List[float]:
    return [k / (n - 1) for k in range(n)]


# =====================================================================
#  T-normları ve kalıntıları
# =====================================================================
def ikisi_birden_ne_kadar(a=None, b=None, ne: str = "Łukasiewicz",
                          tur: str = "ve", p: float = 2.0):
    """İKİSİ BİRDEN NE KADAR DOĞRU -- **tek terkip** (kütük H226).

    Küme: sekiz t-normu (``t_lukasiewicz, t_godel, t_carpim, t_zayif,
    t_nilpotent_minimum, t_schweizer_sklar, t_yager, t_dombi``) ve dört
    kalıntısı (``i_lukasiewicz, i_godel, i_carpim,
    i_nilpotent_minimum``). On iki isim, **tek** amelin durakları idi:
    iki dereceli doğruluğu birleştirmek, yahut o birleştirmenin
    **eşleniğini** (kalıntı) almak.

    ==============  ==================================================
    ``tur``         döndürdüğü
    ==============  ==================================================
    ``ve``          ``a ⊗ b`` -- iki önerme birden ne kadar doğru
    ``ise``         ``a → b`` -- kalıntı (Galois eşleniği)
    ``çekirdek``    ``(⊗, →)`` çifti; kalıntısı yoksa ``(⊗, None)``
    ==============  ==================================================

    Adlar: ``Łukasiewicz``, ``Gödel``, ``çarpım``, ``nilpotent min``,
    ``en zayıf``, ``Schweizer-Sklar``, ``Yager``, ``Dombi``. Son üçü
    ``p`` parametresi alır.

    **T89 -- kalıntı eşlenikliği.** ``a → b = min(1, 1−a+b)``
    alındığında eşlenik t-norm ``min(a,b)`` **değildir**; kuvvetli ve
    ``a ⊗ b = max(0, a+b−1)``dir. Bu, kalıntı bağıntısının
    ``a ⊗ b ≤ c ⟺ a ≤ (b → c)`` tek satırından çıkar ve
    ``lukasiewicz_min_ile_bozulur`` bunu karşı örnekle mühürler.
    ``min`` ile eşlenen kalıntı Gödel gerektirmesidir, Łukasiewicz'inki
    değil.

    **T90 (çarpım kalıntısı):** ``min(1, b/a)`` ``a = 0``da tanımsızdır;
    kalıntı biçiminde yazılınca hem tanım kümesi tamamlanır hem ``min``
    gereksizleşir. **T94 (Dombi):** ``a = 0``da ``(1−a)/a`` patlar,
    ``T(0,b) = 0`` dalı açıkça yazılır. **T95 (Schweizer-Sklar):**
    ``max(0,·)`` kesmesi yalnız ``p > 0`` içindir; ``p < 0`` iken
    ``a^p + b^p − 1 > 0`` dâima sağlanır ve kesme yanlış dala götürür.
    """
    def T(a: float, b: float) -> float:
        if ne == "Łukasiewicz":
            return max(0.0, a + b - 1.0)          # KUVVETLİ ve
        if ne == "Gödel":
            return min(a, b)
        if ne == "çarpım":
            return a * b
        if ne == "nilpotent min":
            return min(a, b) if a + b > 1.0 else 0.0
        if ne == "en zayıf":                      # drastic product
            if a == 1.0:
                return b
            if b == 1.0:
                return a
            return 0.0
        if ne == "Schweizer-Sklar":
            if a == 0.0 or b == 0.0:
                return 0.0
            u = a ** p + b ** p - 1.0
            return (max(0.0, u) if p > 0 else u) ** (1.0 / p)
        if ne == "Yager":
            return 1.0 - min(1.0, ((1 - a) ** p + (1 - b) ** p) ** (1.0 / p))
        if ne == "Dombi":
            if a <= 0.0 or b <= 0.0:
                return 0.0
            if a >= 1.0:
                return b
            if b >= 1.0:
                return a
            u = ((1 - a) / a) ** p + ((1 - b) / b) ** p
            return 1.0 / (1.0 + u ** (1.0 / p))
        raise ValueError("t-normu bilinmiyor: %r" % (ne,))

    def I(a: float, b: float) -> float:
        if ne == "Łukasiewicz":
            return min(1.0, 1.0 - a + b)
        if ne == "Gödel":
            return 1.0 if a <= b else b
        if ne == "çarpım":
            return 1.0 if a <= b else b / a       # a > b ≥ 0 ⇒ a > 0
        if ne == "nilpotent min":
            return 1.0 if a <= b else max(1.0 - a, b)
        raise ValueError("bu t-normunun kapalı kalıntısı yazılmadı: %r"
                         % (ne,))

    if tur == "çekirdek":
        return T, (I if ne in KALINTILI else None)
    if tur == "ve":
        return T(float(a), float(b))
    if tur == "ise":
        return I(float(a), float(b))
    raise ValueError("kip bilinmiyor: %r" % (tur,))


KALINTILI: Tuple[str, ...] = ("Łukasiewicz", "Gödel", "çarpım",
                              "nilpotent min")

TNORM_ADLARI: Tuple[Tuple[str, str, float], ...] = (
    ("Łukasiewicz", "Łukasiewicz", 0.0),
    ("Gödel (min)", "Gödel", 0.0),
    ("çarpım", "çarpım", 0.0),
    ("nilpotent min", "nilpotent min", 0.0),
    ("Schweizer-Sklar p=2", "Schweizer-Sklar", 2.0),
    ("Schweizer-Sklar p=0.5", "Schweizer-Sklar", 0.5),
    ("Yager p=2", "Yager", 2.0),
    ("Dombi p=2", "Dombi", 2.0),
    ("en zayıf (drastic)", "en zayıf", 0.0),
)

TNORMLAR: Dict[str, TNorm] = {
    baslik: ikisi_birden_ne_kadar(ne=k, p=pp, tur="çekirdek")[0]
    for baslik, k, pp in TNORM_ADLARI}

KALINTILAR: Dict[str, Tuple[TNorm, Kalinti]] = {
    k: ikisi_birden_ne_kadar(ne=k, tur="çekirdek") for k in KALINTILI}






# =====================================================================
#  Aksiyom denetimi
# =====================================================================
def tnorm_aksiyomlari(T: TNorm, n: int = 15,
                      tol: float = 1e-9) -> Dict[str, object]:
    """Değişme, birleşme, tekdüzelik, birim ve sınır şartları.

    Birleşme sayısal olarak denetlenir (kesirli üsler yüzünden tam
    eşitlik beklenmez); tolerans açıkça bildirilir.
    """
    g = _izgara(n)
    degisme = birlesme = tekduze = birim = sinir = True
    en_buyuk_birlesme_sapmasi = 0.0
    for a in g:
        if abs(T(a, 1.0) - a) > tol or T(a, 0.0) > tol:
            birim = False
        for b in g:
            if abs(T(a, b) - T(b, a)) > tol:
                degisme = False
            for c in g:
                s = abs(T(T(a, b), c) - T(a, T(b, c)))
                en_buyuk_birlesme_sapmasi = max(en_buyuk_birlesme_sapmasi, s)
                if s > 1e-7:
                    birlesme = False
            if b > a and T(a, 0.5) - T(b, 0.5) > tol:
                tekduze = False
    for a in g:
        if T(0.0, a) > tol or T(a, 0.0) > tol:
            sinir = False
    return {
        "değişme": degisme,
        "birleşme": birlesme,
        "birleşme_azamî_sapma": en_buyuk_birlesme_sapmasi,
        "tekdüzelik": tekduze,
        "birim T(a,1)=a": birim,
        "sınır T(a,0)=0": sinir,
        "t-normu": degisme and birlesme and tekduze and birim and sinir,
    }


def kalinti_saglaniyor_mu(T: TNorm, I: Kalinti, n: int = 21,
                          tol: float = 1e-9) -> Dict[str, object]:
    """``a ⊗ b ≤ c ⟺ a ≤ (b → c)`` ızgarada sınanır."""
    g = _izgara(n)
    ihlal: List[Tuple[float, float, float, str]] = []
    for a in g:
        for b in g:
            for c in g:
                sol = T(a, b) <= c + tol
                sag = a <= I(b, c) + tol
                if sol != sag:
                    ihlal.append((a, b, c, "⇒" if sol else "⇐"))
    return {
        "sağlanıyor": not ihlal,
        "ihlal_sayısı": len(ihlal),
        "ilk_ihlal": ihlal[0] if ihlal else None,
    }


def lukasiewicz_min_ile_bozulur(n: int = 21) -> Dict[str, object]:
    """**T89'un fiilî sağlaması.**

    Łukasiewicz gerektirmesi ``min`` ile eşlenik DEĞİLDİR; bağıntının
    bozulduğu somut bir üçlü gösterilir.
    """
    dogru = kalinti_saglaniyor_mu(ikisi_birden_ne_kadar(ne="Łukasiewicz", tur="çekirdek")[0], ikisi_birden_ne_kadar(ne="Łukasiewicz", tur="çekirdek")[1], n)
    yanlis = kalinti_saglaniyor_mu(ikisi_birden_ne_kadar(ne="Gödel", tur="çekirdek")[0], ikisi_birden_ne_kadar(ne="Łukasiewicz", tur="çekirdek")[1], n)
    return {
        "⊗ = max(0,a+b−1) ile kalıntı sağlanıyor": dogru["sağlanıyor"],
        "⊗ = min ile kalıntı sağlanıyor": yanlis["sağlanıyor"],
        "min ile ihlal sayısı": yanlis["ihlal_sayısı"],
        "min ile ilk ihlal (a,b,c)": yanlis["ilk_ihlal"],
    }


# =====================================================================
#  Üç değerli mantıklar: Kleene, Łukasiewicz, Priest (LP)
# =====================================================================
# Değerler: 0 (yanlış), 1 (ara), 2 (doğru).  LP'de ara değer ``b``,
# yani "hem doğru hem yanlış"tır ve BELİRLENMİŞ (designated) sayılır;
# Kleene'de ``u``, yani "belirsiz"dir ve belirlenmiş DEĞİLDİR. İki
# mantığın bütün farkı budur.
UC_DEGIL = (2, 1, 0)
UC_VE = [[0, 0, 0], [0, 1, 1], [0, 1, 2]]
UC_VEYA = [[0, 1, 2], [1, 1, 2], [2, 2, 2]]


def uc_ise_kleene(a: int, b: int) -> int:
    return UC_VEYA[UC_DEGIL[a]][b]


def uc_ise_lukasiewicz(a: int, b: int) -> int:
    """``a ≤ b`` ise 2; değilse ``2 − (a − b)``."""
    return 2 if a <= b else 2 - (a - b)


def uc_degerli_gecerli_mi(oncüller: Sequence[Callable[[Tuple[int, ...]], int]],
                          netice: Callable[[Tuple[int, ...]], int],
                          n_deg: int, belirlenmis: Tuple[int, ...]) -> bool:
    """Öncüller belirlenmiş değer alırken netice de alıyor mu?"""
    for atama in _uclu_atamalar(n_deg):
        if all(p(atama) in belirlenmis for p in oncüller):
            if netice(atama) not in belirlenmis:
                return False
    return True


def _uclu_atamalar(k: int) -> Iterable[Tuple[int, ...]]:
    if k == 0:
        yield ()
        return
    for kuyruk in _uclu_atamalar(k - 1):
        for v in (0, 1, 2):
            yield (v,) + kuyruk


def lp_patlamiyor() -> Dict[str, object]:
    """Priest'in LP'sinde ``A, ¬A ⊬ B`` -- ex falso İPTAL.

    LP'de ``b`` belirlenmiştir; ``A = b`` iken ``¬A = b`` de belirlenmiş
    olur, fakat ``B = 0`` seçilebilir. Klasik mantıkta (yalnız ``2``
    belirlenmiş) bu imkânsızdır.
    """
    A = lambda v: v[0]
    nA = lambda v: UC_DEGIL[v[0]]
    B = lambda v: v[1]
    lp = uc_degerli_gecerli_mi([A, nA], B, 2, (1, 2))
    klasik_gibi = uc_degerli_gecerli_mi([A, nA], B, 2, (2,))
    # önemsizleşmeme: çelişkiyi doğrulayan ama B'yi yalanlayan bir atama
    tanik = None
    for atama in _uclu_atamalar(2):
        if A(atama) in (1, 2) and nA(atama) in (1, 2) and B(atama) not in (1, 2):
            tanik = atama
            break
    return {
        "LP'de A,¬A ⊨ B": lp,                    # False olmalı
        "klasik belirlenmişle A,¬A ⊨ B": klasik_gibi,   # True olmalı
        "tanık (A,B) değerleri": tanik,
        "önemsizleşmiyor": (not lp) and klasik_gibi,
    }


# =====================================================================
#  Jainist Syādvāda: yedi mod
# =====================================================================
TEMEL_YUKLEM = ("asti", "nāsti", "avaktavya")


def syadvada_modlari() -> List[Tuple[str, ...]]:
    """**T126'nın tashihli hâli**: yedi mod, üç yüklemin BOŞ OLMAYAN alt
    kümeleridir.

    ``2³ − 1 = 7``; yani "niçin yedi?" sorusunun cevabı türetilir,
    ezberlenmez. Sıralama, klasik ``saptabhaṅgī`` sırasıdır.
    """
    sira = [(0,), (1,), (0, 1), (2,), (0, 2), (1, 2), (0, 1, 2)]
    return [tuple(TEMEL_YUKLEM[i] for i in alt) for alt in sira]


def syadvada_tamlik() -> Dict[str, object]:
    modlar = syadvada_modlari()
    kumeler = {frozenset(m) for m in modlar}
    butun_bos_olmayan = {frozenset(TEMEL_YUKLEM[i] for i in alt)
                         for k in range(1, 4)
                         for alt in _alt_kumeler(3, k)}
    return {
        "mod_sayısı": len(modlar),
        "2³−1": 2 ** 3 - 1,
        "tam_ve_tekrarsız": kumeler == butun_bos_olmayan,
        "modlar": ["·".join(m) for m in modlar],
    }


def _alt_kumeler(n: int, k: int) -> Iterable[Tuple[int, ...]]:
    from itertools import combinations
    return combinations(range(n), k)


# =====================================================================
#  Rapor
# =====================================================================
def rapor() -> str:
    satir = ["=== çok değerli ve bulanık mantıklar ===",
             "%-24s %-8s %-8s %-9s %-8s %s"
             % ("t-normu", "değişme", "birleşme", "tekdüze", "birim", "t-normu mu")]
    for ad, T in TNORMLAR.items():
        r = tnorm_aksiyomlari(T)
        satir.append("%-24s %-8s %-8s %-9s %-8s %s"
                     % (ad, r["değişme"], r["birleşme"], r["tekdüzelik"],
                        r["birim T(a,1)=a"], r["t-normu"]))
    satir.append("")
    satir.append("Kalıntı bağıntısı  a⊗b ≤ c ⟺ a ≤ (b→c):")
    for ad, (T, I) in KALINTILAR.items():
        r = kalinti_saglaniyor_mu(T, I)
        satir.append("  %-16s %s  (ihlal: %d)"
                     % (ad, r["sağlanıyor"], r["ihlal_sayısı"]))
    satir.append("")
    L = lukasiewicz_min_ile_bozulur()
    satir.append("T89 sağlaması -- Łukasiewicz gerektirmesi:")
    satir.append("  kuvvetli ve ile kalıntı: %s" % L["⊗ = max(0,a+b−1) ile kalıntı sağlanıyor"])
    satir.append("  min ile kalıntı        : %s  (ihlal %d, ilk: %s)"
                 % (L["⊗ = min ile kalıntı sağlanıyor"], L["min ile ihlal sayısı"],
                    L["min ile ilk ihlal (a,b,c)"]))
    satir.append("")
    p = lp_patlamiyor()
    satir.append("Paratutarlı LP: A,¬A ⊨ B → %s   (klasik belirlenmişle → %s)"
                 % (p["LP'de A,¬A ⊨ B"], p["klasik belirlenmişle A,¬A ⊨ B"]))
    satir.append("  önemsizleşmiyor: %s   tanık (A,B) = %s"
                 % (p["önemsizleşmiyor"], p["tanık (A,B) değerleri"]))
    satir.append("")
    s = syadvada_tamlik()
    satir.append("Syādvāda: %d mod = 2³−1 = %d, tam ve tekrarsız: %s"
                 % (s["mod_sayısı"], s["2³−1"], s["tam_ve_tekrarsız"]))
    for m in s["modlar"]:                                    # type: ignore[union-attr]
        satir.append("    syād-" + m)
    return "\n".join(satir)


if __name__ == "__main__":
    print(rapor())
