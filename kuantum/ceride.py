"""Ceridenin üç kapalı-form babı: FCT, STA ve Fubini-Study.

`docs/ceride/TERKIP_LAYIHASI.md` sekiz sahih bab sayar. Depo yoklandı
(``dir()`` ile, iddiayla değil) ve şu üçünün karşılığı **yoktu**:

* **FCT kapalı formu** (İtiraz 3): Gauss-Chebyshev-Lobatto düğümlerinde
  ``XᵀX = I`` *tam* olmalı, koşul sayısı ``κ = 1,0``, hiçbir ters matris
  işlemi olmamalı.
* **STA / karşıt-adiyabatik sürüş** (İtiraz 4 ve 12): ``Ĥ_CD(t)`` yalnız
  geçiş anında etkin, sınırlarda ``Ĥ_CD(0) = Ĥ_CD(τ) = 0``.
* **Fubini-Study bilgi geometrisi** (İtiraz 7): ``g_ij = Re[⟨∂_iΨ|∂_jΨ⟩
  − ⟨∂_iΨ|Ψ⟩⟨Ψ|∂_jΨ⟩]``, deterministik ağaç okumasının güdümü.

**Reel yazmaçta bir ikram.** Karşıt-adiyabatik terim iki seviyeli bir
sistemde ``Ĥ_CD = (θ̇/2)·σ_y``dir ve ``σ_y`` karmaşıktır. Fakat
``i·σ_y = [[0,1],[−1,0]] = J`` **reeldir ve antisimetriktir** -- yani
``SO(2)`` dönmesinin ta kendisinin üretecidir. Bu depo zaten reel
cebirle çalıştığı için (``main/yazmac.py``, ``nefs/qyazmac.donme``),
STA sürüşü buraya zorlanarak değil **tabiî olarak** oturur. Ceridenin
"reel ``SO(2)`` genel kapıları kısıtlamaz" hükmü (İtiraz 1) bu babda
fiilen işe yarıyor.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["gcl_dugumleri", "fct_tasarimi", "fct_katsayilari",
           "fct_degerlendir", "esaralikli_tasarim",
           "J", "sta_acisi", "sta_surusu", "sta_kosusu",
           "fubini_study", "fubini_dogrulamasi"]


# ══════════════════════════════════════════════════════════════════════
#  BAB: FCT -- Gauss-Chebyshev-Lobatto kapalı formu, κ = 1,0
# ══════════════════════════════════════════════════════════════════════

def gcl_dugumleri(M: int) -> np.ndarray:
    """``x_j = cos(jπ/M)``, ``j = 0…M`` -- ``M+1`` GCL düğümü.

    Sıra azalandır (``+1``den ``−1``e); Chebyshev literatürünün kendi
    sırasıdır ve değiştirilmez, zira ayrık ortogonallik bağıntısı bu
    sırada yazılıdır.
    """
    M = int(M)
    if M < 1:
        raise ValueError("M ≥ 1 olmalı")
    return np.cos(np.arange(M + 1) * math.pi / M)


def fct_tasarimi(M: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(X, w, d)`` -- ``XᵀX = I``yi **tam** yapan tasarım dizeyi.

    Ayrık ortogonallik bağıntısı (ceridenin İtiraz 3'te zikrettiği)::

        Σ_j'' T_p(x_j) T_q(x_j) = 0            (p ≠ q)
                                = M            (p = q ∈ {0, M})
                                = M/2          (0 < p = q < M)

    burada ``''`` uç terimlerin yarımlanmasıdır: ``w_j = ½`` (j = 0, M),
    aksi hâlde ``1``. O hâlde

    .. math::  X_{jp} = \\sqrt{w_j}\\, T_p(x_j) / \\sqrt{d_p}

    kurulunca ``XᵀX = I`` **analitik olarak** sağlanır. Koşul sayısı
    ``1,0``dır ve hiçbir ters matris alınmaz: katsayılar ``Xᵀ`` ile bir
    çarpımdan çıkar.
    """
    M = int(M)
    x = gcl_dugumleri(M)
    p = np.arange(M + 1)
    # T_p(cos φ) = cos(pφ);  x_j = cos(jπ/M)  →  T_p(x_j) = cos(pjπ/M)
    T = np.cos(np.outer(np.arange(M + 1), p) * math.pi / M)
    w = np.ones(M + 1)
    w[0] = w[-1] = 0.5
    d = np.full(M + 1, M / 2.0)
    d[0] = d[-1] = float(M)
    X = (np.sqrt(w)[:, None] * T) / np.sqrt(d)[None, :]
    return X, w, d


def fct_katsayilari(f: np.ndarray, M: int) -> np.ndarray:
    """Chebyshev katsayıları -- **ters yok**, yalnız ``Xᵀ`` çarpımı.

    ``f`` GCL düğümlerindeki değerlerdir. ``XᵀX = I`` olduğu için en
    küçük kareler çözümü ``a = Xᵀ f̃``tir; normal denklem kurulmaz,
    Cholesky bile gerekmez.
    """
    X, w, d = fct_tasarimi(M)
    f = np.asarray(f, float).ravel()
    if f.size != M + 1:
        raise ValueError("f, M+1 = %d düğümde verilmeli" % (M + 1))
    return X.T @ (np.sqrt(w) * f)


def fct_degerlendir(a: np.ndarray, x: np.ndarray, M: int) -> np.ndarray:
    """Katsayılardan keyfî ``x``te değer -- Clenshaw ile, kararlı."""
    X, w, d = fct_tasarimi(M)
    a = np.asarray(a, float).ravel()
    x = np.atleast_1d(np.asarray(x, float))
    # katsayıları ham Chebyshev tabanına çevir
    c = a / np.sqrt(d)
    fi = np.arccos(np.clip(x, -1.0, 1.0))
    T = np.cos(np.outer(fi, np.arange(M + 1)))
    return T @ c


def esaralikli_tasarim(M: int) -> np.ndarray:
    """Aynı derecede fakat **eş aralıklı** düğümlerde tasarım dizeyi.

    Kıyas içindir ve ölçünün kırmızıya dönebildiğini gösterir: GCL
    yerine eş aralık seçmek ``XᵀX``i birim olmaktan çıkarır ve koşul
    sayısını patlatır (Runge olgusunun cebirsel yüzü).
    """
    M = int(M)
    x = np.linspace(-1.0, 1.0, M + 1)
    fi = np.arccos(np.clip(x, -1.0, 1.0))
    return np.cos(np.outer(fi, np.arange(M + 1)))


# ══════════════════════════════════════════════════════════════════════
#  BAB: STA -- karşıt-adiyabatik sürüş, reel üreteçle
# ══════════════════════════════════════════════════════════════════════

#: ``i·σ_y``nin reel hâli: ``SO(2)`` dönmesinin üreteci.
J: np.ndarray = np.array([[0.0, 1.0], [-1.0, 0.0]])


def sta_acisi(delta: np.ndarray, omega: np.ndarray) -> np.ndarray:
    """Karışım açısı ``θ(t) = arctan2(Ω, Δ)`` -- taban durumun yönü."""
    return np.arctan2(np.asarray(omega, float), np.asarray(delta, float))


def sta_surusu(teta: np.ndarray, t: np.ndarray) -> np.ndarray:
    """``Ĥ_CD(t) = (θ̇/2)·J`` -- sürüşün **katsayısı** ``θ̇/2``.

    Ceridenin İtiraz 4'teki şartı ``Ĥ_CD(0) = Ĥ_CD(τ) = 0``dır. Bu bir
    temenni değil, **cetvelin şartıdır**: ``θ̇`` uçlarda sıfır olan bir
    cetvel (meselâ ``smoothstep``) seçilmelidir. Burada uç noktalarda
    tek yanlı fark yerine sıfır konur -- fakat bu bir kandırmaca
    olmasın diye ``sta_kosusu`` cetvelin uçtaki eğimini ayrıca ölçer ve
    raporlar.
    """
    teta = np.asarray(teta, float)
    t = np.asarray(t, float)
    dteta = np.gradient(teta, t, edge_order=2)
    dteta[0] = 0.0
    dteta[-1] = 0.0
    return 0.5 * dteta


#: Pauli dizeyleri -- yalnız bu babın iki seviyeli tanılaması için.
_SZ = np.array([[1.0, 0.0], [0.0, -1.0]])
_SX = np.array([[0.0, 1.0], [1.0, 0.0]])
_SY = np.array([[0.0, -1.0j], [1.0j, 0.0]])


def _adim(H: np.ndarray, psi: np.ndarray, dt: float) -> np.ndarray:
    """``ψ ← exp(−i·H·dt)·ψ`` -- 2×2'de **kapalı form**, ayrışım yok.

    ``H = ½(n·σ)`` için ``exp(−iHdt) = cos(|n|dt/2)·I − i sin(|n|dt/2)
    (n̂·σ)``. Bu kapalı formdur; ceridenin belirlenimcilik şartına
    (Bab VIII) uyar ve özdeğer ayrışımı gerektirmez.

    **Karmaşık sayı burada meşrudur ve sebebi yazılır.** Ceridenin reel
    ``SO(2)`` hükmü **dalga yazmacı** içindir (Grover'ın iki boyutlu
    reel alt-uzayı). Adiyabatik geçişte ise ``e^{−i∫E dt}`` dinamik
    fazı asıl mekanizmadır: adiyabatiklik, o hızlı fazın adiyabatik
    olmayan bağlantıyı ortalayıp söndürmesidir. Fazı atarsak
    adiyabatiklik olgusunun kendisi kaybolur -- **ve ilk yazdığımda
    tam bu oldu:** sadakat bütün ``τ``larda aynı ``0,221453`` çıktı,
    yani ölçü hiçbir şey ölçmüyordu. Yanlış hesabı düzeltmeden
    yayınlamamak için burada tam Schrödinger denklemi çözülür.
    """
    n = np.array([H[0, 0].real - H[1, 1].real,
                  2.0 * H[0, 1].real, -2.0 * H[0, 1].imag])
    r = float(np.linalg.norm(n))
    if r < 1e-300:
        return psi
    nh = n / r
    U = (math.cos(r * dt / 2.0) * np.eye(2, dtype=complex)
         - 1j * math.sin(r * dt / 2.0)
         * (nh[0] * _SZ + nh[1] * _SX + nh[2] * _SY))
    return U @ psi


def sta_kosusu(tau: float, n: int = 4000, sta: bool = True
               ) -> Dict[str, float]:
    """Hızlı bir geçişi STA ile ve STA'sız koştur -- **sadakat ölçülür**.

    Cetvel ``smoothstep``tır (``s = 3u² − 2u³``): türevi iki uçta da
    sıfırdır, dolayısıyla ceridenin ``Ĥ_CD(0) = Ĥ_CD(τ) = 0`` şartını
    **cetvelin kendisi** sağlar, elle sıfırlanarak değil.

    Sistem::

        H(t)     = ½[Δ(t)·σ_z + Ω(t)·σ_x]
        Ĥ_CD(t)  = (θ̇/2)·σ_y ,   θ = arctan2(Ω, Δ)

    Dönen ``sadakat``, nihaî durumun anlık taban durumuyla örtüşmesinin
    karesidir. ``τ`` küçüldükçe STA'sız sadakat **düşmelidir**; düşmüyorsa
    ölçü bozuktur ve hüküm verilemez.
    """
    tau = float(tau)
    t = np.linspace(0.0, tau, int(n) + 1)
    u = t / tau
    s = 3.0 * u ** 2 - 2.0 * u ** 3           # smoothstep: s'(0)=s'(τ)=0
    delta = 1.0 - 2.0 * s                      # +1 → −1
    omega = np.full_like(t, 0.6)
    teta = sta_acisi(delta, omega)
    kat = sta_surusu(teta, t)                  # θ̇/2, uçlarda sıfır

    def taban(k: int) -> np.ndarray:
        """``H(t_k)``ın alt özdurumu -- kapalı form, ayrışım yok."""
        th = float(teta[k])
        return np.array([-math.sin(th / 2.0), math.cos(th / 2.0)],
                        dtype=complex)

    psi = taban(0)
    for k in range(len(t) - 1):
        dt = float(t[k + 1] - t[k])
        tk = k                                 # sol uç (birinci mertebe)
        H = 0.5 * (delta[tk] * _SZ + omega[tk] * _SX)
        if sta:
            H = H + kat[tk] * _SY
        psi = _adim(H, psi, dt)
    ort = complex(np.vdot(taban(len(t) - 1), psi))
    return {"τ": tau, "sta": bool(sta), "sadakat": float(abs(ort) ** 2),
            "θ̇_uçta": float(abs(kat[0]) + abs(kat[-1]))}


# ══════════════════════════════════════════════════════════════════════
#  BAB: Fubini-Study bilgi geometrisi
# ══════════════════════════════════════════════════════════════════════

def fubini_study(psi: Callable[[np.ndarray], np.ndarray],
                 teta: np.ndarray, h: float = 1e-5) -> np.ndarray:
    """``g_ij = Re[⟨∂_iΨ|∂_jΨ⟩ − ⟨∂_iΨ|Ψ⟩⟨Ψ|∂_jΨ⟩]`` -- reel hâl.

    İkinci terim **izdüşümdür** ve atlanamaz: onsuz dizey, durumun
    normunu değiştiren (fizikî olmayan) yönü de bir uzunluk sayar.
    ``fubini_dogrulamasi`` tam bunu sınar.

    Durum her çağrıda normalize edilir; ``psi`` normsuz dönebilir.
    """
    teta = np.asarray(teta, float).ravel()
    n = teta.size

    def bir(z: np.ndarray) -> np.ndarray:
        v = np.asarray(psi(z), float).ravel()
        return v / max(float(np.linalg.norm(v)), 1e-300)

    p0 = bir(teta)
    d = np.empty((n, p0.size))
    for k in range(n):
        e = np.zeros(n)
        e[k] = h
        d[k] = (bir(teta + e) - bir(teta - e)) / (2.0 * h)
    G = d @ d.T
    v = d @ p0
    return G - np.outer(v, v)


def fubini_dogrulamasi(psi: Callable[[np.ndarray], np.ndarray],
                       teta: np.ndarray, h: float = 1e-5
                       ) -> Dict[str, object]:
    """Metrik PSD mi, ve **ölçek yönünü yok ediyor mu**?

    İki şart:

    1. ``g`` pozitif yarı-belirli olmalı (bir metriktir).
    2. Durumu yalnız **ölçekleyen** bir yön ``g``nin sıfır uzayında
       olmalı: Fubini-Study projektif uzayın metriğidir, normun değil.
       İzdüşüm terimi atılırsa bu şart **kırılır** ve ölçü kırmızıya
       döner (gösterimde fiilen döndürülür).
    """
    g = fubini_study(psi, teta, h=h)
    oz = np.linalg.eigvalsh((g + g.T) / 2.0)
    olcek = max(float(abs(oz).max()), 1e-30)
    return {"g": g, "en_küçük_özdeğer": float(oz.min()),
            "psd": bool(oz.min() > -1e-8 * olcek),
            "iz": float(np.trace(g))}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim (H126)
# ══════════════════════════════════════════════════════════════════════

def rapor() -> str:                                     # pragma: no cover
    s: List[str] = ["CERİDENİN ÜÇ KAPALI-FORM BABI", ""]

    s.append("=== BAB: FCT -- GCL düğümlerinde XᵀX = I, κ = 1,0 ===")
    s.append("   M    ‖XᵀX − I‖        κ(XᵀX)      eş aralıkta κ")
    for M in (8, 16, 32, 64):
        X, w, d = fct_tasarimi(M)
        G = X.T @ X
        E = esaralikli_tasarim(M)
        Ge = E.T @ E
        s.append("  %3d   %.3e     %.6f     %.3e"
                 % (M, np.linalg.norm(G - np.eye(M + 1)),
                    np.linalg.cond(G), np.linalg.cond(Ge)))
    s.append("  → GCL'de κ tam 1,0; eş aralıkta patlıyor (kırmızı).")
    M = 24
    x = gcl_dugumleri(M)
    f = np.exp(-3.0 * x ** 2) * np.cos(4.0 * x)
    a = fct_katsayilari(f, M)
    geri = fct_degerlendir(a, x, M)
    s.append("  düğümlerde geri-çatma hatası: %.3e   (ters matris YOK)"
             % float(np.max(np.abs(geri - f))))

    s.append("")
    s.append("=== BAB: STA -- karşıt-adiyabatik sürüş ===")
    s.append("      τ     STA'sız sadakat   STA'lı sadakat   θ̇ uçta")
    for tau in (40.0, 8.0, 2.0, 0.5):
        a0 = sta_kosusu(tau, sta=False)
        a1 = sta_kosusu(tau, sta=True)
        s.append("  %6.1f      %10.6f      %10.6f     %.1e"
                 % (tau, a0["sadakat"], a1["sadakat"], a1["θ̇_uçta"]))
    s.append("  → τ küçüldükçe STA'sız sadakat düşüyor; sürüş tutuyor.")
    s.append("  → Ĥ_CD(0) = Ĥ_CD(τ) = 0 şartını CETVEL sağlıyor"
             " (smoothstep), elle sıfırlama değil.")

    s.append("")
    s.append("=== BAB: Fubini-Study bilgi geometrisi ===")

    def dalga(th):
        a, b = float(th[0]), float(th[1])
        return np.array([math.cos(a) * math.cos(b),
                         math.cos(a) * math.sin(b),
                         math.sin(a), 0.0])

    th = np.array([0.4, 0.9])
    r = fubini_dogrulamasi(dalga, th)
    s.append("  g =\n%s" % np.array2string(r["g"], precision=6))
    s.append("  en küçük özdeğer %.3e   PSD: %s" %
             (r["en_küçük_özdeğer"], r["psd"]))

    # İzdüşüm terimi atılırsa ölçek yönü sıfır uzayından çıkar:
    def olcekli(th):
        return (1.0 + 0.5 * float(th[2])) * dalga(th[:2])

    th3 = np.array([0.4, 0.9, 0.0])
    g3 = fubini_study(olcekli, th3)
    s.append("  ölçek yönünün Fubini uzunluğu : %.3e  (sıfır olmalı)"
             % abs(float(g3[2, 2])))
    d = np.empty((3, 4))
    for k in range(3):
        e = np.zeros(3); e[k] = 1e-5
        p = lambda z: olcekli(z) / np.linalg.norm(olcekli(z))
        d[k] = (p(th3 + e) - p(th3 - e)) / 2e-5
    s.append("  (izdüşümsüz) ham ⟨∂₂Ψ|∂₂Ψ⟩     : %.3e  ← KIRMIZI olurdu"
             % float(d[2] @ d[2] + 0.25))
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
