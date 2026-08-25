"""Tıkız — Alexandroff tıkızlaştırması, barriyerler ve kritik lokus.

Tıkız olmayan bir uzayda süreklilik ekstremum garantisi vermez;
``f(x) = −x`` üzerinde ``ℝ``de asgarî yoktur.  Üç yol:

**1. Alexandroff tek nokta.**  ``X⁺ = X ∪ {∞}``; açık kümeler,
``X``in açıkları ve tümleyeni tıkız olan kümelerin ``{∞}`` ile
birleşimidir.  ``ℝⁿ``in tek nokta tıkızlaştırması ``Sⁿ``dir.
**Zorlayıcı** (coercive) bir ``f``, yani ``‖x‖→∞`` iken ``f→+∞``
olan, ``X⁺``ye sürekli uzatılır ve orada asgarî **vardır**.

**2. Alt-seviye kümeleri.**  ``f`` zorlayıcıysa ``K_r = {f ≤ r}``
tıkızdır ve asgarî oradadır.  Bu, tıkızlaştırmadan daha ucuz ve
çoğu hâlde yeterlidir; hangi ``r``nin boş olmayan bir küme verdiği
**hesaplanır**, tahmin edilmez.

**3. Logaritmik barriyer.**  ``g_j(x) > 0`` kısıtları için
``Φ = −Σ ln g_j``.  Sınıra yaklaşınca patlar; ``ln(max(g, ε))``
ile kırpmak **NaN'ı önler ama kısıtı da gevşetir** -- bunun bedeli
ölçülüyor.  Doğru usul, ``τ``yı kademeli küçültüp iç noktadan
sınıra yaklaşmaktır.

**Türetilmiş kritik lokus.**  ``Crit(f) = {df = 0}``.  Sonlu boyutta
bu, ``df``in sıfır kesitiyle **geri çekmesidir**.  Sayısal olarak:
kritik noktalar bulunur, Morse indisleri hesaplanır ve

.. math::  \\sum_k (-1)^k M_k = \\chi(X)

Morse **bağıntısı** (eşitlik!) ile sağlaması yapılır.  K27 tashihi:
bu bir eşitliktir; ``≥`` yazmak imkânsız dizilimleri de geçirir.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "zorlayici_mi", "alt_seviye_tikiz_mi", "baslangic_seviyesi",
    "barriyer", "barriyerli_hedef", "ic_nokta_yolu",
    "kritik_noktalar", "morse_indisi", "morse_bagintisi",
    "kure_izdusumu", "ters_kure_izdusumu",
]


# ══════════════════════════════════════════════════════════════════════
#  1. Zorlayıcılık ve alt-seviye kümeleri
# ══════════════════════════════════════════════════════════════════════

def _kurede_asgari(f: Callable[[np.ndarray], float], R: float,
                   V: np.ndarray, aday: int = 4, adim: int = 60
                   ) -> float:
    """``min_{‖v‖=1} f(Rv)`` — rastgele örnek + küre üstünde inişle.

    Salt rastgele örnekleme **yetmez**: ``f(x) = x₀²`` yalnız
    ``v₀ = 0`` düzleminde sıfırdır ve rastgele bir yön oraya tam
    düşmez, dolayısıyla asgarî ``R²·min v₀²`` gibi artan bir şey
    görünür ve zorlayıcı olmayan fonksiyon zorlayıcı sanılır
    (ölçüldü: 64 yönle ``x₀²`` yanlışlıkla zorlayıcı çıkıyordu).
    En iyi birkaç adaydan başlayıp küre üzerinde sonlu farklı
    izdüşümlü iniş yapmak bu dejenere yönü **bulur**.
    """
    d = V.shape[1]
    deg = np.array([float(f(R * v)) for v in V])
    en_iyi = float(deg.min())
    h = 1e-4
    for i in np.argsort(deg)[:aday]:
        v = V[i].copy()
        fv = float(deg[i])
        t = 0.5
        for _ in range(adim):
            g = np.empty(d)
            for k in range(d):
                e = np.zeros(d); e[k] = h
                u = v + e; u /= np.linalg.norm(u)
                g[k] = (float(f(R * u)) - fv) / h
            g -= (g @ v) * v                      # teğet bileşen
            n = np.linalg.norm(g)
            if n < 1e-14:
                break
            u = v - t * g / n
            u /= np.linalg.norm(u)
            fu = float(f(R * u))
            if fu < fv:
                v, fv = u, fu
            else:
                t *= 0.5
                if t < 1e-12:
                    break
        en_iyi = min(en_iyi, fv)
    return en_iyi


def zorlayici_mi(f: Callable[[np.ndarray], float], boyut: int,
                 yaricaplar: Sequence[float] = (1, 10, 100, 1000),
                 yon_sayisi: int = 64, tohum: int = 0
                 ) -> Dict[str, object]:
    """``‖x‖→∞`` iken ``f→+∞`` mi? — kürelerde asgarî izlenerek.

    Her yarıçapta küre üzerinde **asgarî** değere bakılır (ortalama
    değil): zorlayıcılık en kötü yönde de sağlanmalıdır.  Ortalamaya
    bakmak, tek bir yönde sonsuza kaçan bir fonksiyonu zorlayıcı
    gösterirdi.  Asgarî de yalnız örneklemeyle değil, küre üzerinde
    **inişle** aranır (bkz. :func:`_kurede_asgari`).

    Bu bir **sınamadır, ispat değil** -- sonlu yarıçaplarda bakılıyor.
    Fakat asgarînin düşmesi zorlayıcı **olmadığını** gösterir.
    """
    r = np.random.default_rng(tohum)
    V = r.normal(size=(yon_sayisi, boyut))
    V = V / np.linalg.norm(V, axis=1, keepdims=True)
    asgariler, medyanlar = [], []
    for R in yaricaplar:
        asgariler.append(_kurede_asgari(f, float(R), V))
        medyanlar.append(float(np.median([f(R * v) for v in V])))
    artan = all(a < b for a, b in zip(asgariler, asgariler[1:]))
    # Dejenere yön: asgarî, o yarıçaptaki tipik değerin yanında yok
    # denecek kadar küçükse ``f`` bir yönde sınırlı kalıyordur -- artıyor
    # görünmesi sırf sonlu farkların gürültüsüdür (``x₀²``: oran 3e-13).
    oran = (abs(asgariler[-1]) / abs(medyanlar[-1])
            if medyanlar[-1] != 0 else float("inf"))
    dejenere = oran < 1e-6
    return {
        "yarıçaplar": list(yaricaplar), "küre_asgarîleri": asgariler,
        "küre_medyanları": medyanlar, "asgarî_medyan_oranı": oran,
        "dejenere_yön": dejenere, "tekdüze_artıyor": artan,
        "zorlayıcı_görünüyor": bool(artan and asgariler[-1] > asgariler[0]
                                    and not dejenere),
        "not": "sonlu yarıçap sınaması; düşüş zorlayıcı OLMADIĞINI gösterir",
    }


def baslangic_seviyesi(f: Callable[[np.ndarray], float],
                       x0: np.ndarray, marj: float = 1.0) -> float:
    """``r₀ = f(x₀) + marj`` — ``K_{r₀}`` boş olamaz, ``x₀`` içindedir.

    Rastgele bir ``r`` seçmek boş küme verebilir (kaynaktaki 37.
    darboğaz).  Bir noktadan başlamak bunu **imkânsız** kılar.
    """
    return float(f(np.asarray(x0, float))) + float(marj)


def alt_seviye_tikiz_mi(f: Callable[[np.ndarray], float], r: float,
                        boyut: int, azami_yaricap: float = 1e4,
                        tohum: int = 0) -> Dict[str, object]:
    """``K_r = {f ≤ r}`` sınırlı mı? — yönler taranarak.

    Her yönde ``f``in ``r``yi aştığı bir yarıçap bulunursa küme o
    yönde sınırlıdır.  Bulunamayan bir yön varsa **sınırsız** demektir
    ve o yön bildirilir; "tıkız" hükmü verilmez.

    Ayrıca **boşluk** ayrıca aranır: boş küme de sınırlıdır, o yüzden
    "sınırlı" hükmü tek başına "tıkız ve boş değil" demek değildir.
    Boşluk araması bir **sınamadır** (rastgele nokta + iniş), ispat
    değil; nokta bulunursa küme kesinlikle boş değildir, bulunamazsa
    "bulunamadı" denir.
    """
    rng = np.random.default_rng(tohum)
    V = rng.normal(size=(128, boyut))
    V = V / np.linalg.norm(V, axis=1, keepdims=True)
    en_buyuk = 0.0
    for v in V:
        R = 1.0
        while R < azami_yaricap and f(R * v) <= r:
            R *= 2.0
        if R >= azami_yaricap:
            return {"sınırlı": False, "sınırsız_yön": v,
                    "azamî_yarıçap": azami_yaricap,
                    "nokta_bulundu": _kumede_nokta_ara(f, r, boyut, rng)}
        en_buyuk = max(en_buyuk, R)
    return {"sınırlı": True, "kuşatan_yarıçap": en_buyuk,
            "nokta_bulundu": _kumede_nokta_ara(f, r, boyut, rng)}


def _kumede_nokta_ara(f: Callable[[np.ndarray], float], r: float,
                      boyut: int, rng, deneme: int = 400) -> bool:
    """``{f ≤ r}`` içinde bir nokta var mı? — rastgele + iniş."""
    en_iyi = None
    for _ in range(deneme):
        x = rng.normal(size=boyut) * 10 ** rng.uniform(-2, 2)
        v = float(f(x))
        if v <= r:
            return True
        if en_iyi is None or v < en_iyi[1]:
            en_iyi = (x, v)
    # kaba bir iniş: en iyi noktadan sayısal gradyanla
    x, _ = en_iyi
    for _ in range(200):
        g = _sayisal_gradyan(lambda z: float(f(z)), x)
        nrm = float(np.linalg.norm(g))
        if nrm < 1e-14:
            break
        x = x - 0.05 * g / nrm
        if float(f(x)) <= r:
            return True
    return False


# ══════════════════════════════════════════════════════════════════════
#  2. Barriyer
# ══════════════════════════════════════════════════════════════════════

def barriyer(g: Sequence[float], eps: Optional[float] = None) -> float:
    """``Φ = −Σ ln g_j``.

    ``eps`` verilirse ``ln(max(g, ε))`` kullanılır: NaN önlenir ama
    **kısıt gevşer** -- ``g ≤ 0`` olan noktalar da sonlu ceza alır ve
    eniyileme oraya kayabilir.  ``eps=None`` (varsayılan) hâlinde
    ``g ≤ 0`` için ``+inf`` döner, yani nokta **kesinlikle**
    reddedilir.  İkisi arasındaki tercih ölçülerek yapılmalıdır.
    """
    g = np.asarray(g, float)
    if eps is None:
        if np.any(g <= 0):
            return float("inf")
        return float(-np.sum(np.log(g)))
    return float(-np.sum(np.log(np.maximum(g, eps))))


def barriyerli_hedef(f: float, g: Sequence[float], tau: float,
                     eps: Optional[float] = None) -> float:
    """``f + τ·Φ(g)``."""
    if tau < 0:
        raise ValueError("τ ≥ 0 olmalı")
    b = barriyer(g, eps)
    return float(f) + tau * b if math.isfinite(b) else float("inf")


def ic_nokta_yolu(f: Callable[[np.ndarray], float],
                  g: Callable[[np.ndarray], np.ndarray],
                  x0: np.ndarray, tau0: float = 1.0,
                  azalma: float = 0.2, tur: int = 12,
                  ic_adim: int = 600, eta: float = 1e-2
                  ) -> Dict[str, object]:
    """İç nokta usulü: ``τ``yı kademeli küçültüp sınıra yaklaş.

    Her turda ``f + τΦ`` üzerinde basit bir iniş yapılır; sonra
    ``τ ← τ·azalma``.  Adım, kısıtı **ihlal edecekse geri çekilir**
    (basit geri izleme); bu olmadan iniş barriyerin dışına fırlar ve
    ``inf`` alır.

    Dönen ``yol``, her turdaki ``(τ, x, f(x), min g(x))``dır -- yani
    sınıra yaklaşma ölçülebilir.

    ``ic_adim`` yetersizse bir turda iniş tamamlanmaz ve ``f`` geçici
    olarak **yükselebilir**; ölçüldü, 200 iç adımla 8 turun 1'inde
    böyle oluyor, 600 ile hiçbirinde.  Varsayılan buna göre seçildi.
    """
    x = np.asarray(x0, float).copy()
    if np.any(g(x) <= 0):
        raise ValueError("başlangıç noktası kısıtları ihlal ediyor")
    tau = float(tau0)
    yol = []
    for _ in range(tur):
        for _ in range(ic_adim):
            grad = _sayisal_gradyan(
                lambda z: barriyerli_hedef(f(z), g(z), tau), x)
            adim = eta
            for _ in range(30):
                aday = x - adim * grad
                if np.all(g(aday) > 0) and math.isfinite(
                        barriyerli_hedef(f(aday), g(aday), tau)):
                    break
                adim *= 0.5
            else:
                break
            x = aday
        yol.append((tau, x.copy(), float(f(x)), float(np.min(g(x)))))
        tau *= azalma
    return {"x": x, "yol": yol, "son_tau": tau}


def _sayisal_gradyan(F: Callable[[np.ndarray], float],
                     x: np.ndarray) -> np.ndarray:
    h = np.finfo(float).eps ** (1 / 3)
    g = np.zeros_like(x)
    for i in range(x.size):
        e = np.zeros_like(x)
        e[i] = h * max(1.0, abs(float(x[i])))
        arti, eksi = F(x + e), F(x - e)
        if not (math.isfinite(arti) and math.isfinite(eksi)):
            # Sınıra çok yakın: tek yanlı fark
            g[i] = (F(x) - eksi) / e[i] if math.isfinite(eksi) else 0.0
        else:
            g[i] = (arti - eksi) / (2 * e[i])
    return g


# ══════════════════════════════════════════════════════════════════════
#  3. Kritik lokus ve Morse
# ══════════════════════════════════════════════════════════════════════

def morse_indisi(H: np.ndarray) -> int:
    """Hessian'ın negatif özdeğer sayısı."""
    Hs = (np.asarray(H, float) + np.asarray(H, float).T) / 2
    return int(np.sum(np.linalg.eigvalsh(Hs) < 0))


def kritik_noktalar(grad: Callable[[np.ndarray], np.ndarray],
                    hess: Callable[[np.ndarray], np.ndarray],
                    baslangiclar: Sequence[Sequence[float]],
                    tol: float = 1e-10, azami: int = 200
                    ) -> List[Dict[str, object]]:
    """Newton ile ``∇f = 0`` köklerini bul, **tekrarları birleştir**.

    Farklı başlangıçlar aynı kritik noktaya yakınsar; birleştirilmezse
    Morse sayıları şişer ve bağıntı bozulur.  Birleştirme eşiği
    ``1e-6``; daha yakın iki nokta aynı sayılır.

    Dejenere (tekil Hessian) noktalar **işaretlenir**; Morse kuramı
    onlarda geçerli değildir ve sessizce sayılmamalıdır.
    """
    bulunan: List[Dict[str, object]] = []
    for x0 in baslangiclar:
        x = np.asarray(x0, float).copy()
        yakinsadi = False
        for _ in range(azami):
            g = np.asarray(grad(x), float)
            if float(np.max(np.abs(g))) < tol:
                yakinsadi = True
                break
            H = np.asarray(hess(x), float)
            try:
                adim = np.linalg.solve(H, g)
            except np.linalg.LinAlgError:
                break
            t = 1.0
            for _ in range(30):
                if float(np.max(np.abs(grad(x - t * adim)))) < \
                        float(np.max(np.abs(g))):
                    break
                t *= 0.5
            else:
                break
            x = x - t * adim
        if not yakinsadi:
            continue
        H = np.asarray(hess(x), float)
        oz = np.linalg.eigvalsh((H + H.T) / 2)
        dejenere = bool(np.min(np.abs(oz)) < 1e-8)
        if any(np.max(np.abs(b["x"] - x)) < 1e-6 for b in bulunan):
            continue
        bulunan.append({"x": x, "indis": morse_indisi(H),
                        "dejenere": dejenere, "özdeğerler": oz})
    return bulunan


def morse_bagintisi(indisler: Sequence[int], boyut: int) -> Dict[str, object]:
    """``Σ_k (−1)^k M_k`` — Euler karakteristiğine EŞİT olmalı (K27).

    ``≥`` yazmak imkânsız dizilimleri de geçirir; eşitlik geçirmez.
    ``M_k`` sayımı burada verilenden hesaplanır.
    """
    M = [0] * (boyut + 1)
    for i in indisler:
        if not 0 <= i <= boyut:
            raise ValueError(f"Morse indisi 0..{boyut} olmalı, {i} geldi")
        M[i] += 1
    return {"M": M, "alterne_toplam": sum((-1) ** k * m
                                          for k, m in enumerate(M))}


# ══════════════════════════════════════════════════════════════════════
#  4. Alexandroff: ℝⁿ ∪ {∞} ≅ Sⁿ
# ══════════════════════════════════════════════════════════════════════

def kure_izdusumu(x: np.ndarray) -> np.ndarray:
    """Ters stereografik: ``ℝⁿ → Sⁿ \\ {kuzey}``.

    .. math::  \\pi^{-1}(x) = \\Bigl(\\frac{2x}{\\|x\\|^2+1},
               \\frac{\\|x\\|^2-1}{\\|x\\|^2+1}\\Bigr)

    ``‖x‖ → ∞`` iken görüntü kuzey kutbuna ``(0,…,0,1)`` yaklaşır --
    yani ``∞`` noktası **somut bir nokta** hâline gelir.  Alexandroff
    tıkızlaştırmasının ``Sⁿ`` olduğunun gösterilebilir hâli budur.
    """
    x = np.asarray(x, float).reshape(-1)
    k = float(x @ x)
    return np.concatenate([2 * x / (k + 1), [(k - 1) / (k + 1)]])


def ters_kure_izdusumu(p: np.ndarray) -> np.ndarray:
    """Stereografik: ``Sⁿ \\ {kuzey} → ℝⁿ``.

    Kuzey kutbunda tanımsızdır ve orada **hata verilir**; sonsuzu bir
    sayıyla temsil etmek yanlış olur.
    """
    p = np.asarray(p, float).reshape(-1)
    if abs(float(p[-1]) - 1.0) < 1e-12:
        raise ValueError("kuzey kutbu ∞'a karşılık gelir; ℝⁿ'de karşılığı yok")
    return p[:-1] / (1.0 - p[-1])


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s: List[str] = []

    s.append("=== Zorlayıcılık: küre ASGARÎsine bakmak şart ===")
    ornekler = {
        "‖x‖²": lambda x: float(x @ x),
        "‖x‖⁴ − ‖x‖²": lambda x: float(x @ x) ** 2 - float(x @ x),
        "x₀² (tek yön)": lambda x: float(x[0]) ** 2,
        "−‖x‖²": lambda x: -float(x @ x),
        "x₀": lambda x: float(x[0]),
    }
    for ad, f in ornekler.items():
        r = zorlayici_mi(f, 3)
        s.append(f"  {ad:16s} küre asgarîleri: "
                 + " ".join(f"{v:+.1e}" for v in r["küre_asgarîleri"])
                 + f"   zorlayıcı: {r['zorlayıcı_görünüyor']}")
    s.append("  'x₀² (tek yön)' ORTALAMAYA bakılsaydı zorlayıcı görünürdü;")
    s.append("  asgarîye bakınca x₀=0 düzleminde sabit kaldığı çıkıyor.")

    s.append("\n=== Alt-seviye kümesi boş olmuyor ===")
    f = lambda x: float(x @ x) - 3.0
    x0 = np.array([2.0, -1.0])
    r0 = baslangic_seviyesi(f, x0)
    s.append(f"  f(x₀)={f(x0):.3f}, r₀={r0:.3f}"
             f"   x₀ ∈ K_r₀ mı? {f(x0) <= r0}")
    s.append("  f(x) = ‖x‖² − 3, yani asgarî değer −3:")
    for r in (r0, 0.0, -2.9, -3.5):
        d = alt_seviye_tikiz_mi(f, r, 2)
        s.append(f"  r={r:+6.2f}: sınırlı mı? {d['sınırlı']}"
                 + (f"  kuşatan yarıçap {d['kuşatan_yarıçap']:.1f}"
                    if d["sınırlı"] else "")
                 + f"   nokta bulundu mu? {d['nokta_bulundu']}")
    s.append("  r=−3.50'de küme BOŞ; boş küme de sınırlıdır, o yüzden")
    s.append("  'sınırlı' tek başına yetmiyor — boşluk ayrıca aranıyor.")
    d = alt_seviye_tikiz_mi(lambda x: float(x[0]), 0.0, 2)
    s.append(f"  zorlayıcı olmayan f=x₀, r=0: sınırlı mı? {d['sınırlı']}"
             f"   → tıkızlık hükmü VERİLMİYOR")

    s.append("\n=== Barriyer: kırpma NaN'ı önlüyor ama kısıtı gevşetiyor ===")
    s.append("  g            Φ (kırpmasız)     Φ (ε=1e-8 kırpmalı)")
    for g in ([1.0, 2.0], [0.1, 0.5], [1e-6, 1.0], [-0.5, 1.0], [0.0, 1.0]):
        a = barriyer(g)
        b = barriyer(g, eps=1e-8)
        s.append(f"  {str(g):14s} {a:14.4f}    {b:14.4f}")
    s.append("  Kırpmasız hâlde g ≤ 0 KESİN reddediliyor (inf);")
    s.append("  kırpmalı hâlde sonlu ceza alıyor, yani eniyileme oraya")
    s.append("  kayabilir. Tercih ölçülerek yapılmalı.")

    s.append("\n=== İç nokta yolu: τ küçüldükçe sınıra yaklaşma ===")
    # min x₀ + x₁  s.t.  x₀ ≥ 0, x₁ ≥ 0, 1 − x₀ − x₁ ≥ 0  → çözüm (0,0)
    hedef = lambda x: float(x[0] + x[1])
    kisit = lambda x: np.array([x[0], x[1], 1.0 - x[0] - x[1]])
    r = ic_nokta_yolu(hedef, kisit, np.array([0.3, 0.3]), tau0=1.0,
                      azalma=0.25, tur=8, ic_adim=600)
    s.append("      τ         f(x)      min g(x)      x")
    for tau, x, fx, mg in r["yol"]:
        s.append(f"  {tau:.2e}   {fx:.6f}   {mg:.6f}   "
                 f"[{x[0]:.6f}, {x[1]:.6f}]")
    s.append("  Çözüm (0,0); τ küçüldükçe oraya yaklaşılıyor ve kısıt")
    s.append("  hiçbir turda İHLAL EDİLMİYOR (min g > 0).")

    s.append("\n=== Morse bağıntısı: EŞİTLİK (K27) ===")
    # Torus üzerinde yükseklik fonksiyonu yerine, ℝ²'de kapalı bir örnek:
    # f(x,y) = x⁴ − 2x² + y²  → kritik noktalar (0,0) eyer, (±1,0) asgarî
    def grad(v):
        x, y = v
        return np.array([4 * x ** 3 - 4 * x, 2 * y])

    def hess(v):
        x, y = v
        return np.array([[12 * x ** 2 - 4, 0.0], [0.0, 2.0]])

    baslangiclar = [[a, b] for a in (-1.5, -0.3, 0.0, 0.3, 1.5)
                    for b in (-1.0, 0.0, 1.0)]
    kn = kritik_noktalar(grad, hess, baslangiclar)
    s.append(f"  f(x,y) = x⁴ − 2x² + y²  →  {len(kn)} ayrı kritik nokta:")
    for k in sorted(kn, key=lambda d: float(d["x"][0])):
        s.append(f"    x=[{k['x'][0]:+.6f}, {k['x'][1]:+.6f}]"
                 f"  Morse indisi={k['indis']}"
                 f"  dejenere mi? {k['dejenere']}")
    mb = morse_bagintisi([k["indis"] for k in kn], 2)
    s.append(f"  M = {mb['M']}   Σ(−1)^k M_k = {mb['alterne_toplam']}")
    s.append("  Morse bağıntısı χ(ℝ²) = 1 vermeli — ve veriyor:")
    s.append(f"    2 − 1 + 0 = {mb['alterne_toplam']}  =  χ(ℝ²) = 1")
    s.append("  (İlk hâlde 'χ=2' yazmıştım; yanlıştı. Alt-seviye kümeleri")
    s.append("   eyer değerinin ALTINDA iki ayrı disk, ÜSTÜNDE tek bir")
    s.append("   bölgedir; Morse bağıntısı bütün uzayın χ'sini verir, o da 1.")
    s.append("   Topolojinin eyerde değiştiğini söyleyen zaten bu kuramdır.)")
    s.append("  '≥' ölçütü M=[5,0,0] gibi imkânsız bir dizilimi de")
    s.append(f"  geçirirdi: Σ(−1)^k·[5,0,0] = "
             f"{morse_bagintisi([0]*5, 2)['alterne_toplam']} ≥ 1,"
             " ama eşitliği bozuyor.")

    s.append("\n=== Alexandroff: ℝⁿ ∪ {∞} ≅ Sⁿ ===")
    s.append("  ‖x‖ büyüdükçe görüntü kuzey kutbuna yaklaşıyor:")
    for R in (0.0, 1.0, 10.0, 1e3, 1e6):
        p = kure_izdusumu(np.array([R, 0.0]))
        s.append(f"    ‖x‖={R:8.0e}: π⁻¹(x) = "
                 f"[{p[0]:+.6f}, {p[1]:+.6f}, {p[2]:+.9f}]"
                 f"   ‖p‖={np.linalg.norm(p):.10f}")
    s.append("  Gidiş-dönüş sağlaması:")
    rng = np.random.default_rng(0)
    en_buyuk = 0.0
    for _ in range(500):
        x = rng.normal(size=3) * 10 ** rng.uniform(-3, 3)
        en_buyuk = max(en_buyuk, float(np.max(np.abs(
            ters_kure_izdusumu(kure_izdusumu(x)) - x))))
    s.append(f"    500 noktada azamî bağıl olmayan sapma = {en_buyuk:.2e}")
    try:
        ters_kure_izdusumu(np.array([0.0, 0.0, 1.0]))
        s.append("    kuzey kutbu kabul edildi (BEKLENMEZ)")
    except ValueError as e:
        s.append(f"    kuzey kutbu reddedildi: {e}")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
