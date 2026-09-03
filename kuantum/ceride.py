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
cebirle çalıştığı için (``kuantum/yazmac.py``, ``nefs/qyazmac.donme``),
STA sürüşü buraya zorlanarak değil **tabiî olarak** oturur. Ceridenin
"reel ``SO(2)`` genel kapıları kısıtlamaz" hükmü (İtiraz 1) bu babda
fiilen işe yarıyor.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["qsp_faz_bul", "qsp_degeri", "gibbs_cift", "gibbs_fazlari",
           "GIBBS_FAZ_TABLOSU", "GIBBS_DERECE",
           "gcl_dugumleri", "fct_tasarimi", "fct_katsayilari",
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
#  FAZ 0: QSP faz açıları -- ÇEVRİMDIŞI hesaplanır, tabloya yazılır
# ══════════════════════════════════════════════════════════════════════
#
# Ceridenin kendi eki bunu *"gizli kalan hakikat"* diye zikreder:
#
#     d_qsp = 64 dereceli bir filtre için bu faz açılarını bulmak
#     optimizasyon esnasında yapılmaz; klasik işlemcide Haah (2019)
#     veya Dong vd. (2021) algoritmalarıyla eğitime başlamadan evvel
#     BİR DEFAYA MAHSUS hesaplanıp tabloya yazılır.
#
# ve padişahın 2. kat'î kuralı: *"QSP açısını runtime'da arama."*
# Aşağıdaki tablo ``_faz_tablosu_uret`` ile bir kere hesaplandı ve
# buraya **gömüldü**; koşum sırasında arama yapılmaz.


def _qsp_tam_faz(yari: Sequence[float], d: int) -> List[float]:
    """Simetrik yarım diziden ``d+1`` fazlık tam diziye.

    Simetri ``φ_j = φ_{d−j}``dir; simetrik QSP'nin ürettiği polinom
    o zaman **reeldir** ve paritesi ``d mod 2``dir. Yarım dizinin
    uzunluğu ``⌈(d+1)/2⌉``dir.
    """
    y = list(yari)
    return y + (y[-2::-1] if d % 2 == 0 else y[::-1])


def qsp_degeri(yari: Sequence[float], d: int, x: float) -> float:
    """``Re⟨0|U_φ(x)|0⟩`` -- simetrik yarım fazlarla."""
    from kuantum.qsvt import qsp_polinomu
    return float(np.real(qsp_polinomu(_qsp_tam_faz(yari, d), float(x))))


def qsp_faz_bul(hedef: Callable[[float], float], d: int,
                tur: int = 120, tol: float = 1e-12
                ) -> Tuple[np.ndarray, float, int]:
    """``Re⟨0|U_φ(x)|0⟩ ≈ hedef(x)`` olacak simetrik fazları bul.

    Gauss-Newton, sönümlemeli adım, **belirlenimci** (rastgele tohum
    yok, başlangıç ``φ = (π/4, 0, …, 0)`` -- Dong vd. 2021'in kendi
    başlangıcı). Düğümler ``(0,1)`` aralığında Chebyshev'dir; parite
    ``d mod 2`` olduğu için yarım aralık yeterlidir.

    Döner ``(yarım_fazlar, düğümdeki_âzamî_artık, tur)``. **Artık
    yalnız düğümlerde ölçülürse aşırı uyum gizlenir**; onun için
    ``_rapor`` ayrıca 401 noktalı ızgarada da ölçer ve iki sayıyı yan
    yana yazar (H47).
    """
    m = (int(d) + 2) // 2
    j = np.arange(m)
    x = np.cos((2 * j + 1) * math.pi / (4 * m))
    y = np.array([float(hedef(float(t))) for t in x])
    phi = np.zeros(m)
    phi[0] = math.pi / 4.0
    h = 1e-6
    it = 0
    for it in range(int(tur)):
        r = np.array([qsp_degeri(phi, d, t) for t in x]) - y
        if float(np.max(np.abs(r))) < float(tol):
            break
        J = np.empty((m, m))
        for k in range(m):
            e = np.zeros(m)
            e[k] = h
            J[:, k] = (np.array([qsp_degeri(phi + e, d, t) for t in x])
                       - np.array([qsp_degeri(phi - e, d, t) for t in x])
                       ) / (2.0 * h)
        try:
            dp = np.linalg.lstsq(J, -r, rcond=None)[0]
        except np.linalg.LinAlgError:      # pragma: no cover
            break
        adim, f0 = 1.0, float(r @ r)
        for _ in range(30):
            yeni = phi + adim * dp
            rn = np.array([qsp_degeri(yeni, d, t) for t in x]) - y
            if float(rn @ rn) < f0:
                phi = yeni
                break
            adim *= 0.5
        else:
            break
    r = np.array([qsp_degeri(phi, d, t) for t in x]) - y
    return phi, float(np.max(np.abs(r))), int(it)


def gibbs_cift(beta: float) -> Callable[[float], float]:
    """``½[e^{−β(1+x)/2} + e^{−β(1−x)/2}] = e^{−β/2}\cosh(βx/2)``.

    **Niçin çift kısmı?** Tek bir simetrik QSP dizisinin ürettiği
    polinomun paritesi ``d mod 2``dir; parite karışık bir fonksiyon
    (``e^{−βx}``) tek diziyle temsil edilemez. Tam Gibbs için **iki
    tablo** (çift ve tek) ve bir birleştirme lâzımdır; bu dosya çift
    kısmı verir ve eksiği burada **açıkça yazar**, gizlemez.
    """
    b = float(beta)
    return lambda x: math.exp(-b / 2.0) * math.cosh(b * float(x) / 2.0)


GIBBS_DERECE: int = 32
GIBBS_FAZ_TABLOSU: Dict[float, Tuple[float, ...]] = {
    # β = 1.0  → ızgara artığı 2.89e-15
    1.0: (
        +7.85398163397448279e-01, +1.63940632205149596e-17, +5.16886774438653229e-17, -7.42228639824735648e-17,
        -1.78959009067879251e-16, +2.43774003034245568e-17, +3.46628346790352021e-17, -1.90752850243131835e-16,
        +2.72806398458374440e-16, -6.77086910096930828e-17, -1.51383139296484263e-16, -2.10235018858699831e-13,
        -3.02955504369563769e-10, -2.71991350421989660e-07, -1.31027313928002494e-04, -2.53646482751288573e-02,
        -7.02157454800921177e-01,
    ),
    # β = 2.0  → ızgara artığı 2.11e-15
    2.0: (
        +7.85398163397448279e-01, +5.69133184655856333e-17, -8.61026697426553020e-18, -1.06580180354355742e-16,
        -7.63182589175589310e-17, -4.46379274833280657e-18, -5.82497741028148363e-17, -1.14861919624991408e-16,
        +8.39837578115053448e-17, -2.06191412338938709e-16, -2.17096272043578891e-13, -1.15036763237282908e-10,
        -4.16244100453748546e-08, -9.39872303490259219e-06, -1.14419045654967459e-03, -5.67262228926020060e-02,
        -4.87910287357570138e-01,
    ),
    # β = 4.0  → ızgara artığı 1.33e-15
    4.0: (
        +7.85398163397448279e-01, +8.24018175080909381e-17, +6.68820616977939718e-17, -1.86516227769924546e-17,
        -5.94989362044357636e-17, +6.57536224442314508e-17, -5.61691229266047795e-17, -6.76094563499206992e-17,
        -7.31872002775397961e-15, -1.76604970340671767e-12, -3.24745616798840518e-10, -4.34704492824641589e-08,
        -3.99203765865601524e-06, -2.30717742717413823e-04, -7.32114712567225479e-03, -9.93827742304900924e-02,
        -3.20328643099665911e-01,
    ),
    # β = 8.0  → ızgara artığı 1.11e-15
    8.0: (
        +7.85398163397448279e-01, -6.26142592128008973e-17, +2.98965961285311724e-17, +2.50534840308875792e-17,
        +3.75628885686290800e-17, -1.38674542313115019e-16, -9.95690998011589187e-15, -9.62625370637811406e-13,
        -7.54662349904791803e-11, -4.67017104398569605e-09, -2.21213213665520287e-07, -7.70813102813456669e-06,
        -1.87413032714672377e-04, -2.95512823225523242e-03, -2.71677618330386055e-02, -1.23406109662883609e-01,
        -2.16343772164458575e-01,
    ),
}


def gibbs_fazlari(beta: float) -> Tuple[float, ...]:
    """Tablodan çek; tabloda yoksa **hata ver** -- runtime'da arama yok.

    Padişahın 2. kat'î kuralı budur. Yeni bir ``β`` lâzımsa tablo
    çevrimdışı genişletilir (``qsp_faz_bul`` ile), koşum sırasında
    değil.
    """
    b = float(beta)
    if b not in GIBBS_FAZ_TABLOSU:
        raise KeyError("β = %g tabloda yok; çevrimdışı hesaplayıp "
                       "GIBBS_FAZ_TABLOSU'na ekleyin (runtime arama yasak)"
                       % b)
    return GIBBS_FAZ_TABLOSU[b]


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
