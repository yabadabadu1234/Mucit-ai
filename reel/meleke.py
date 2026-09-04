"""41 idrak melekesinin reel dik kapı kaydı.

Kaynak: ``docs/kaynak/reel_meleke_operatorleri.tex`` ve
``docs/kaynak/meleke_kuantum_kapilari.tex``.

**Boyut.**  Varsayılan ``VARSAYILAN_BOYUT = 512``; hızlı deneme için
``HIZLI_BOYUT = 128``.  Her kapı ``D×D`` reel diktir ve **tam dizey
kurulmadan** uygulanabilir (Givens/Householder/köşegen/permütasyon
çarpanları).  Ölçülüyor: ``D=512``de çarpanlı uygulama tam dizeye göre
kaç kat hızlı ve fark ne.

**Tashihler burada işletiliyor.**

* **M9/M10 -- Householder.**  ``I − 2vvᵀ`` bir *yansımadır*: yalnız
  ``v`` yönündeki bileşeni negatifler.  Bütün durumu ``−1`` ile
  çarpması ancak ``Ψ ∥ v`` iken olur.  Üstelik dik olduğu için
  ``‖UΨ‖ = ‖Ψ‖``: **genlik yok edilemez, yalnız yeniden dağıtılır**.
  Risalenin "tenakuz genliği sıfırlanır" iddiası bu yüzden tek bir
  yansımayla gerçekleşmez; sıfırlama ancak *izdüşüm* (üniter olmayan,
  ölçüm sınıfı bir işlem) ile olur.  İkisi de burada var ve farkları
  ölçülüyor.
* **M11/M12 -- İhtimal kapısı.**  ``diag(√P)`` üniter değildir
  (``AᵀA = diag(P)``); ``diag(P)`` hiç değildir.  Kapı listesinde
  değil, **ölçüm işleci** olarak tutuluyor ve adı ``M_`` ile başlıyor.
* **M13 -- Şek/zan/yakîn.**  Üç ayrı taban vektörü değil, tek bir
  ``SO(2)`` dönme açısının üç aralığıdır.
* **M14/M15 -- Cebir.**  Yapı sabitleriyle kapalılık **üreteçlerin**
  (``X = J·H ∈ so(2N)``) özelliğidir; grup elemanlarının komütatörü
  ``so(2N)``de bile değildir.  Ölçülüyor.
* **M16 -- Çarpım.**  ``Π U_k`` ile ``exp(Σ X_k)`` ancak üreteçler sıra
  değiştirirse eşittir; Trotter hatası ölçülüyor.
* **M30 -- Parite.**  ``(−1)^k·I`` genel bir işarettir, ölçülemez;
  parite kapısı ihlal **alt uzayına** bağlanmalıdır.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .hartley import hartley, spektral_suzgec

__all__ = [
    "VARSAYILAN_BOYUT", "HIZLI_BOYUT", "MELEKE_ADLARI",
    "Kapi", "kapi_kur",
    "meleke_kapilari", "kapi_dizeyi", "zincir_uygula",
    "diklik_raporu", "grup_komutatoru_cebirde_mi",
    "carpim_trotter_farki", "genel_isaret_olculemez",
]

VARSAYILAN_BOYUT = 512
HIZLI_BOYUT = 128

MELEKE_ADLARI: Tuple[str, ...] = (
    "Müşahede", "İllet Keşfi", "Gaye Belirleme", "Fıtratı İdrak",
    "Tecrit", "Tasavvur", "Teemmül", "Tenakuz Bulma", "Tezat İdraki",
    "Tahkik", "Şek-Zan-Yakîn", "Muhakeme", "İspat", "Tahlil", "Terkip",
    "İhtimal Hesabı", "Kıyas", "Temsil", "Teşbih", "Temkin", "Tashih",
    "Tertip", "Tafsil", "Mizan", "İntaç", "Hafıza", "İrade", "Kelam",
    "Tefsir", "Tevil", "Fesahat", "Talakat", "Belagat", "Sanat",
    "Münazara", "Tedbir", "Teyakkuz", "Tefekkür", "Tahayyül",
    "Teenni", "Tevekkül",
)
assert len(MELEKE_ADLARI) == 41


# ══════════════════════════════════════════════════════════════════════
#  1. Çarpan biçiminde kapılar (tam dizey kurulmaz)
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Kapi:
    """Reel dik bir kapı — **uygulama** olarak tutulur, dizey olarak değil.

    ``uygula(x)`` vektöre (veya sütun yığınına) tatbik eder; ``dizey()``
    ancak istenirse ``D×D``yi kurar.  ``dik`` alanı kapının gerçekten
    dik olup olmadığını söyler; üniter olmayan işleçler (ölçüm) de bu
    sınıfta tutulur ama ``dik=False`` işaretlenir.
    """
    ad: str
    uygula: Callable[[np.ndarray], np.ndarray]
    boyut: int
    dik: bool = True
    aciklama: str = ""

    def dizey(self) -> np.ndarray:
        return self.uygula(np.eye(self.boyut))

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self.uygula(x)


def kapi_kur(ne: str = "yansıma", v=None, aci=None, ciftler=None,
             D: int = 0, isaret=None, perm=None, P=None,
             theta: float = 0.0, i: int = 0, j: int = 1,
             ad: str = "") -> Kapi:
    """HANGİ KAPIYI KURACAĞIZ -- tek terkip (kütük H226).

    Küme: ``householder``, ``izdusum_sifirlama``, ``givens_zinciri``,
    ``kosegen_isaret``, ``permutasyon``, ``hartley_kapisi``,
    ``so2_dondurme``, ``olcum_isleci_kok_p``. Sekiz isim, üç
    çekirdeğin durakları idi ve birleştirilince iki **özdeşlik** açığa
    çıktı:

    1. **Bir yönü bastırmak** -- ``I − α·vvᵀ``. ``α = 2`` yansımadır
       (Householder, dik, involutif); ``α = 1`` izdüşümdür (genliği
       gerçekten siler, **üniter değildir**). İkisi ayrı yazıldığında
       "genlik sıfırlanır" ile "genlik yansıtılır" bambaşka iki şey
       gibi duruyordu; hâlbuki aralarındaki tek fark bir katsayıdır ve
       diklik tam o katsayıda kaybolur.
    2. **Her ekseni ölçeklemek** -- ``diag(d)``. ``d = ±1`` tezattır
       (dik, involutif); ``d = √P`` ölçüm işlecidir (``AᵀA = diag(P)
       ≠ I``, üniter **değil**). Yine tek çekirdek, yine diklik farkı
       yalnız ``d``dedir.

    Kalan üçü ayrı çekirdeklerdir ve öyle kalır: Givens dönmeleri
    çarpımı (``so2_dondurme`` onun tek açılı hâlidir), permütasyon
    (indis toplaması) ve RHT.

    ==================  ==============================================
    ``ne``              kurduğu
    ==================  ==============================================
    ``yansıma``         ``I − 2vvᵀ`` -- Householder (M9: yalnız ``v``
                        bileşenini negatifler, bütün durumu değil)
    ``silme``           ``I − vvᵀ`` -- izdüşüm; ÜNİTER DEĞİL
    ``givens``          Givens dönmeleri çarpımı, ``O(kD)``
    ``so2``             tek açılı Givens (M13: şek/zan/yakîn aynı
                        ``SO(2)`` açısının üç aralığıdır)
    ``işaret``          ``diag(±1)`` -- §9 Tezat
    ``ölçüm``           ``diag(√P)`` -- M11/M12, kapı DEĞİL
    ``permütasyon``     indis toplaması -- dik, ``O(D)``
    ``hartley``         RHT -- dik, involutif, ``O(D log D)``
    ==================  ==============================================

    Hiçbirinde tam dizey kurulmaz; ``Kapi`` bir ``x ↦ f(x)`` taşır ve
    ``dizey()`` yalnız denetim için açılır.
    """
    if ne in ("yansıma", "silme"):
        alfa = 2.0 if ne == "yansıma" else 1.0
        v = np.asarray(v, float)
        v = v / np.linalg.norm(v)
        D = v.shape[0]

        def f(x, v=v, alfa=alfa):
            x = np.asarray(x, float)
            return x - alfa * np.multiply.outer(v, v @ x)

        if ne == "yansıma":
            return Kapi(ad or "Householder", f, D, True,
                        "yansıma: yalnız v bileşeni işaret değiştirir (M9)")
        return Kapi(ad or "İzdüşüm", f, D, False,
                    "izdüşüm: genliği gerçekten siler ama ÜNİTER DEĞİL")

    if ne in ("işaret", "ölçüm"):
        if ne == "işaret":
            d = np.asarray(isaret, float)
        else:
            d = np.sqrt(np.clip(np.asarray(P, float), 0.0, None))
        D = d.shape[0]

        def g(x, d=d):
            return d[:, None] * x if np.ndim(x) > 1 else d * np.asarray(x)

        if ne == "işaret":
            return Kapi(ad or "Tezat", g, D, True, "köşegen ±1")
        return Kapi(ad or "İhtimal (ÖLÇÜM)", g, D, False,
                    "diag(√P): AᵀA = diag(P) ≠ I -- kapı değil")

    if ne == "so2":
        return kapi_kur("givens", aci=[theta], ciftler=[(i, j)], D=D,
                        ad=ad or "Şek-Zan-Yakîn")

    if ne == "givens":
        aci = np.asarray(aci, float)
        ciftler = [(int(a), int(b)) for a, b in ciftler]

        def h(x, aci=aci, ciftler=ciftler):
            y = np.array(x, float, copy=True)
            for (a, b), th in zip(ciftler, aci):
                c, sn = math.cos(th), math.sin(th)
                ya, yb = y[a].copy(), y[b].copy()
                y[a] = c * ya - sn * yb
                y[b] = sn * ya + c * yb
            return y

        return Kapi(ad or "Givens", h, D, True, "Givens dönmeleri çarpımı")

    if ne == "permütasyon":
        perm = np.asarray(perm, int)
        return Kapi(ad or "Tertip", lambda x: np.asarray(x)[perm],
                    perm.shape[0], True, "permütasyon")

    if ne == "hartley":
        def r(x):
            x = np.asarray(x, float)
            return hartley(x.T).T if np.ndim(x) > 1 else hartley(x)

        return Kapi(ad or "Tasavvur", r, D, True, "reel Hartley dönüşümü")

    raise ValueError("kapı nev'i bilinmiyor: %r" % (ne,))



# ══════════════════════════════════════════════════════════════════════
#  2. 41 melekenin kaydı
# ══════════════════════════════════════════════════════════════════════

def meleke_kapilari(D: int = VARSAYILAN_BOYUT, tohum: int = 0
                    ) -> List[Kapi]:
    """41 melekenin reel dik kapı listesi — hepsi çarpan biçiminde.

    Kapılar temsilîdir (parametreler tohumdan üretilir); mesele
    **yapıdır**: hepsi dik, hepsi tam dizey kurulmadan uygulanabilir,
    ve hiçbiri üniter olmayan bir işleci "kapı" diye saymaz.
    """
    r = np.random.default_rng(tohum)
    K: List[Kapi] = []
    for k, ad in enumerate(MELEKE_ADLARI):
        tur = k % 5
        if tur == 0:
            v = r.normal(size=D)
            K.append(kapi_kur("yansıma", v=v, ad=ad))
        elif tur == 1:
            m = max(4, D // 8)
            ciftler = [(int(a), int(b)) for a, b in
                       r.integers(0, D, size=(m, 2)) if a != b]
            K.append(kapi_kur("givens",
                              aci=r.uniform(0, 2 * math.pi, len(ciftler)),
                              ciftler=ciftler, D=D, ad=ad))
        elif tur == 2:
            K.append(kapi_kur("işaret", isaret=r.choice([-1.0, 1.0], size=D), ad=ad))
        elif tur == 3:
            K.append(kapi_kur("permütasyon", perm=r.permutation(D), ad=ad))
        else:
            K.append(kapi_kur("hartley", D=D, ad=ad))
    assert len(K) == 41
    return K


def kapi_dizeyi(k: Kapi) -> np.ndarray:
    return k.dizey()


def zincir_uygula(kapilar: Sequence[Kapi], x: np.ndarray) -> np.ndarray:
    """``(Π U_k) x`` — sırayla, tam dizey kurulmadan."""
    y = np.asarray(x, float)
    for k in kapilar:
        y = k(y)
    return y


def diklik_raporu(kapilar: Sequence[Kapi]) -> Dict[str, object]:
    """Her kapı için ``‖UᵀU − I‖`` — iddia ile ölçüm yan yana."""
    sat = []
    for k in kapilar:
        M = k.dizey()
        sat.append((k.ad, k.dik,
                    float(np.abs(M.T @ M - np.eye(k.boyut)).max())))
    return {"satırlar": sat,
            "dik_olanlarda_azamî": max((s for _, d, s in sat if d),
                                       default=0.0),
            "dik_olmayan": [(a, s) for a, d, s in sat if not d]}


# ══════════════════════════════════════════════════════════════════════
#  3. Tashihlerin tartılması
# ══════════════════════════════════════════════════════════════════════

def grup_komutatoru_cebirde_mi(D: int = 16, tohum: int = 0
                               ) -> Dict[str, float]:
    """**M14/M15:** ``[U_i, U_j]`` ``so(D)``de mi? — hayır.

    ``so(D)`` yatkın-simetriktir; iki dik dizeyin komütatörü genelde
    yatkın-simetrik değildir.  Üreteçlerin komütatörü ise **her zaman**
    ``so(D)``dedir; ikisi de ölçülüyor.
    """
    r = np.random.default_rng(tohum)
    Q1, _ = np.linalg.qr(r.normal(size=(D, D)))
    Q2, _ = np.linalg.qr(r.normal(size=(D, D)))
    C = Q1 @ Q2 - Q2 @ Q1
    X1 = r.normal(size=(D, D)); X1 = X1 - X1.T
    X2 = r.normal(size=(D, D)); X2 = X2 - X2.T
    CX = X1 @ X2 - X2 @ X1
    olc = max(float(np.abs(C).max()), 1e-30)
    return {"grup_komutatörü_normu": float(np.abs(C).max()),
            "grup_yatkın_sapması": float(np.abs(C + C.T).max()),
            "grup_bağıl_sapma": float(np.abs(C + C.T).max() / olc),
            "üreteç_yatkın_sapması": float(np.abs(CX + CX.T).max()),
            "üreteç_normu": float(np.abs(CX).max())}


def carpim_trotter_farki(D: int = 8, n: int = 3, tohum: int = 0
                         ) -> Dict[str, float]:
    """**M16:** ``exp(ΣX_k)`` ile ``Π exp(X_k)`` farkı.

    Sıra değiştiren (aynı anda köşegenleşen) üreteçlerde sıfır,
    genelinde değil.
    """
    r = np.random.default_rng(tohum)
    X = []
    for i in range(n):
        A = r.normal(size=(D, D)); X.append(A - A.T)

    def uexp(M):
        w, V = np.linalg.eig(M)
        return np.real((V * np.exp(w)) @ np.linalg.inv(V))

    sol = uexp(sum(X))
    sag = np.eye(D)
    for Xi in X:
        sag = sag @ uexp(Xi)
    # sıra değiştiren hâl: hepsi aynı tabanda blok-dönme
    Q, _ = np.linalg.qr(r.normal(size=(D, D)))
    Y = []
    for i in range(n):
        th = r.normal(size=D // 2)
        B = np.zeros((D, D))
        for j, t in enumerate(th):
            B[2 * j, 2 * j + 1] = -t
            B[2 * j + 1, 2 * j] = t
        Y.append(Q @ B @ Q.T)
    solk = uexp(sum(Y))
    sagk = np.eye(D)
    for Yi in Y:
        sagk = sagk @ uexp(Yi)
    return {"genel_fark": float(np.abs(sol - sag).max()),
            "komut_eden_fark": float(np.abs(solk - sagk).max()),
            "komutatör_normu": float(np.abs(X[0] @ X[1] - X[1] @ X[0]).max())}


def genel_isaret_olculemez(D: int = 8, tohum: int = 0) -> Dict[str, float]:
    """**M30:** ``−I`` genel işareti hiçbir ölçümle görülmez.

    ``ρ = ΨΨᵀ`` ile ``(−Ψ)(−Ψ)ᵀ`` aynıdır; alt uzaya bağlı işaret ise
    görülür.
    """
    r = np.random.default_rng(tohum)
    psi = r.normal(size=D); psi /= np.linalg.norm(psi)
    rho = np.outer(psi, psi)
    genel = np.outer(-psi, -psi)
    v = r.normal(size=D); v /= np.linalg.norm(v)
    yerel = kapi_kur("yansıma", v=v)(psi)
    return {"genel_işaret_farkı": float(np.abs(rho - genel).max()),
            "alt_uzay_işareti_farkı":
                float(np.abs(rho - np.outer(yerel, yerel)).max())}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim(D: int = VARSAYILAN_BOYUT) -> str:
    s = []
    s.append("=== 41 meleke kapısı, D = %d (varsayılan) ===" % D)
    K = meleke_kapilari(D)
    rap = diklik_raporu(K)
    s.append("  kapı sayısı = %d   dik olanlarda azamî ‖UᵀU−I‖ = %.2e"
             % (len(K), rap["dik_olanlarda_azamî"]))
    s.append("  ilk beş kapı: " + ", ".join("%s(%s)" % (k.ad,
             k.aciklama.split(":")[0]) for k in K[:5]))
    s.append("  üniter olmayan kapı sayısı = %d  (kayıtta yok, olması "
             "gereken de bu)" % len(rap["dik_olmayan"]))

    s.append("\n=== Çarpan biçimi vs tam dizey: hız ve fark ===")
    for d in (HIZLI_BOYUT, VARSAYILAN_BOYUT):
        Kd = meleke_kapilari(d)
        x = np.random.default_rng(3).normal(size=d)
        zincir_uygula(Kd, x)
        t0 = time.perf_counter()
        for _ in range(10):
            a = zincir_uygula(Kd, x)
        t1 = (time.perf_counter() - t0) / 10
        t2 = time.perf_counter()
        M = np.eye(d)
        for k in Kd:
            M = k.dizey() @ M
        t3 = time.perf_counter() - t2
        b = M @ x
        s.append("  D=%4d  çarpanlı %8.3f ms   tam dizey %9.3f ms  "
                 "(%6.1f×)   fark=%.2e"
                 % (d, t1 * 1e3, t3 * 1e3, t3 / max(t1, 1e-12),
                    float(np.abs(a - b).max())))
    s.append("  Hızlı deneme boyutu %d, varsayılan %d." % (HIZLI_BOYUT,
                                                           VARSAYILAN_BOYUT))

    s.append("\n=== M9: Householder durumun TAMAMINI negatiflemiyor ===")
    r = np.random.default_rng(0)
    d = 8
    v = r.normal(size=d); v /= np.linalg.norm(v)
    U = kapi_kur("yansıma", v=v)
    Pj = kapi_kur("silme", v=v)
    for ad, psi in (("rastgele Ψ", r.normal(size=d)),
                    ("Ψ = v (paralel)", v.copy())):
        psi = psi / np.linalg.norm(psi)
        s.append("  %-16s ‖UΨ + Ψ‖ = %.4f   ‖UΨ‖ = %.6f  (norm korunuyor)"
                 % (ad, float(np.linalg.norm(U(psi) + psi)),
                    float(np.linalg.norm(U(psi)))))
    psi = r.normal(size=d); psi /= np.linalg.norm(psi)
    s.append("  Genlik gerçekten silinsin isteniyorsa İZDÜŞÜM gerekir:")
    s.append("    yansıma  : ⟨v|UΨ⟩ = %+.6f   ‖UΨ‖ = %.6f"
             % (float(v @ U(psi)), float(np.linalg.norm(U(psi)))))
    s.append("    izdüşüm  : ⟨v|PΨ⟩ = %+.2e   ‖PΨ‖ = %.6f  ← norm DÜŞTÜ"
             % (float(v @ Pj(psi)), float(np.linalg.norm(Pj(psi)))))
    s.append("  Üniter kapı genliği yok edemez, yalnız dağıtır.")

    s.append("\n=== M11/M12: ihtimal işleci üniter değil ===")
    P = r.random(6); P /= P.sum()
    M = kapi_kur("ölçüm", P=P)
    A = M.dizey()
    s.append("  diag(√P): ‖AᵀA − I‖ = %.4f   (kapı sayılamaz)"
             % float(np.abs(A.T @ A - np.eye(6)).max()))
    A2 = np.diag(P)
    s.append("  diag(P) : ‖AᵀA − I‖ = %.4f   (reel nüshadaki hâl, daha da "
             "uzak)" % float(np.abs(A2.T @ A2 - np.eye(6)).max()))

    s.append("\n=== M13: şek/zan/yakîn tek bir SO(2) açısı ===")
    for ad, th in (("yakîn", 0.02), ("zan", 0.5), ("şek", math.pi / 4)):
        G = kapi_kur("so2", theta=th, D=2).dizey()
        e0 = np.array([1.0, 0.0])
        y = G @ e0
        s.append("  %-6s θ=%.4f   |⟨0|y⟩|²=%.4f  |⟨1|y⟩|²=%.4f   "
                 "‖GᵀG−I‖=%.1e"
                 % (ad, th, y[0] ** 2, y[1] ** 2,
                    float(np.abs(G.T @ G - np.eye(2)).max())))
    s.append("  Üçü de tek bir dik dönmenin farklı açılarıdır; üçüncü bir")
    s.append("  taban vektörüne ihtiyaç yok ve üniterlik hiç bozulmuyor.")

    s.append("\n=== M14/M15: grup komütatörü so(D)'de değil ===")
    g = grup_komutatoru_cebirde_mi(16)
    s.append("  iki DİK dizey  : ‖C‖=%.4f   ‖C+Cᵀ‖=%.4f  (bağıl %.3f)"
             % (g["grup_komutatörü_normu"], g["grup_yatkın_sapması"],
                g["grup_bağıl_sapma"]))
    s.append("  iki ÜRETEÇ     : ‖C‖=%.4f   ‖C+Cᵀ‖=%.2e   ← so(D)'de"
             % (g["üreteç_normu"], g["üreteç_yatkın_sapması"]))

    s.append("\n=== M16: Π U_k = exp(Σ X_k) ancak sıra değiştirirse ===")
    c = carpim_trotter_farki()
    s.append("  genel üreteçler   : fark = %.4f   ([X₁,X₂] normu %.4f)"
             % (c["genel_fark"], c["komutatör_normu"]))
    s.append("  sıra değiştirenler: fark = %.2e" % c["komut_eden_fark"])

    s.append("\n=== M30: genel işaret ölçülemez ===")
    m = genel_isaret_olculemez()
    s.append("  ρ(Ψ) ile ρ(−Ψ) farkı        = %.2e  ← görülemez"
             % m["genel_işaret_farkı"])
    s.append("  ρ(Ψ) ile ρ(yansıtılmış) farkı = %.4f  ← görülebilir"
             % m["alt_uzay_işareti_farkı"])
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    import sys
    D = int(sys.argv[1]) if len(sys.argv) > 1 else VARSAYILAN_BOYUT
    print(_gosterim(D))
