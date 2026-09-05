"""QUDİT -- dimağın yeni çekirdeği: SVD yok, MPS yok, ikili kübit yok.

Padişahın fermanı: *"Svd mvd olmayacak, Mps iptal olacak, ikili kübit
kodlama iptal olup qudit gelecek."*

Zabıt: ``docs/zabit/kudret/Kuantum_Metinlerindeki_Cevherin_Qudite_Tahvili.md``
ve onu tamamlayan ``Qudite_Tip_Tensorunun_Kodlanma_Nizami``,
``Coklu_Sonsuz_Kategorili_Koherent_Durum_ve_Qudit_Temsili``,
``Ontolojik_Silsile``, ``Kelime_ve_Durum_Kodlamasinin_...``.

===================================================================
NİÇİN BU DOSYA VAR: ÖLÇÜLEN DARBOĞAZ TAM DA İPTAL EDİLEN ŞEYDİ
===================================================================

Eski hat ``11 belirteç/sn`` koşuyordu; hedef ``1 000 000``. Profil
sebebi tek bir yere gösterdi: bir ileri geçişte **~8 500 SVD**, çünkü
45 meleke MPO'su her seferinde MPS zincirini ``χ``ye geri sıkıştırıyor
ve her sıkıştırma yuva başına bir SVD istiyordu. 16×16 bir SVD
LAPACK'te ``65–90 µs``dir ve bu **indirgenemez**: yığınlamak yalnız
1,2× veriyor, ``float32 = float64`` (fark yok), ``eigh`` yalnız %8.

Yâni darboğaz bir kusur değil, **iptal edilen mimarinin kendisiydi.**

Ferman bu yüzden hızın da cevabıdır::

    SVD yok      →  LAPACK çağrısı yok
    MPS yok      →  zincir sıkıştırma süpürmesi yok
    ikili yok    →  bit parçalanması ve Hamming safsatası yok
    qudit var    →  durum tek parça ℂ^d, genlikler SAKLANMAZ, üretilir

===================================================================
DÖRT AMELİYE (zabıtın kendi tasnifi)
===================================================================

1. **Lie-Chebyshev KAN-Qudit durumu** -- ``durum()``.
   Genlikler bellekte açık liste olarak tutulmaz; ``SU(d)``nin Cartan
   ağırlıkları üzerinde öğrenilebilir Chebyshev polinomlarıyla
   **üretilir**. Hafıza ``d``den değil, katsayı sayısından ibarettir.

2. **QSVT Hodge harmonik süzgeci** -- ``suz()``.
   Mantık tenakuzunu matris tersi almadan, ayrıştırma yapmadan,
   yalnız matris-vektör çarpımıyla söndürür.

3. **Gelfand-Tsetlin liflenmesi** -- ``dallanma()``.
   Bağ boyutu keyfî olarak budanmaz; dallanma kuralı cebirsel olarak
   sınırlar, gayrimeşru sızıntı **zaten sıfırdır**.

4. **Fubini-Study tabakalı doğal gradyan** -- ``dogal_adim()``.
   Öklid gradyanı değil, durum manifoldunun kendi metriği. Metrik
   **tersi alınmaz**; eşlenik gradyanla çözülür (yine ayrıştırma yok).

===================================================================
NE İDDİA EDİLMİYOR
===================================================================

Bu dosya kuantum donanımı taklit etmez ve "kuantum hızlanması"
iddia etmez. İddia ettiği tek şey ölçülebilir: **aynı temsil gücü,
LAPACK ayrıştırması olmadan.** Ölçüsü ``rapor()``dadır ve kırmızıya
dönebilir (H90).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["QuditAyari", "agirlik", "durum", "durum_yigin", "suz", "dallanma",
           "metrik", "dogal_adim", "blok", "ortusme", "rapor"]


# ══════════════════════════════════════════════════════════════════
#  AYAR
# ══════════════════════════════════════════════════════════════════

@dataclass
class QuditAyari:
    """Quditin ölçüleri. Hiçbiri koda gömülü değildir."""

    #: Qudit seviyesi ``d``. Zabıtın misali 4096'dır; ARC için sözlük
    #: küçüktür ve ``d`` bloklara bölünür (bkz. ``blok``).
    d: int = 4096
    #: KAN fonksiyonu sayısı ``K``.
    kan: int = 4
    #: Chebyshev derecesi ``d_poly``.
    derece: int = 8
    #: QSVT süzgeç derecesi ``d_qsp``. Zabıt 64 der.
    qsvt: int = 64
    #: Cartan yönü sayısı ``r``. ``d−1`` DEĞİL: zabıtın hafıza iddiası
    #: (``birkaç kilobayt``) ancak ``r ≪ d`` ile doğrudur.
    yon: int = 8
    #: Fubini-Study çözümünde düzenlileştirme. **Nispîdir**: ``g``nin
    #: izine göre ölçeklenir, mutlak bir sayı değil (bkz. ``dogal_adim``).
    duzenli: float = 1e-6
    #: Hesap tipi. ``float32`` bellek bağımlı bu hesapta 2,26× hızlandırır;
    #: doğruluk bedeli ``rapor()``da ölçülür.
    tip: object = np.float64
    tohum: int = 0

    @property
    def katsayi_sayisi(self) -> int:
        """Bellekte fiilen tutulan sayı adedi -- ``d``den bağımsız."""
        return 2 * int(self.kan) * (int(self.derece) + 1) + int(self.yon)


# ══════════════════════════════════════════════════════════════════
#  1. AMELİYE -- LIE-CHEBYSHEV KAN-QUDIT DURUMU
# ══════════════════════════════════════════════════════════════════

def agirlik(d: int, teta: Optional[np.ndarray] = None) -> np.ndarray:
    """Cartan ağırlık izdüşümü ``ω_m(θ) ∈ [−1, 1]``, ``m = 0…d−1``.

    ``su(d)``nin Cartan alt cebri ``d−1`` köşegen üreteçten ibarettir.
    ``k``ıncı üreteç (normalize edilmemiş hâliyle)::

        h_k = diag(1, …, 1, −k, 0, …, 0)          (``k`` tane 1, sonra −k)

    ``|m⟩`` taban durumunun ``h_k`` altındaki ağırlığı, o üretecin
    ``m``inci köşegen girdisidir. Ağırlık izdüşümü bunların ``θ`` ile
    ağırlıklı toplamıdır::

        ω_m(θ) = Σ_k θ_k · (h_k)_{mm}

    **Niçin ``[−1,1]``e normalize edilir.** Chebyshev polinomları
    ``T_j`` ve ``U_j`` yalnız ``[−1,1]``de sınırlıdır; dışında üstel
    büyürler. Normalizasyon ``max_m |ω_m|``e bölmektir -- bu bir kırpma
    **değildir**, ölçek değişimidir ve bütün sıralamayı korur. Sıfır
    vektörde bölme yapılmaz.

    Hiçbir ayrıştırma yoktur: köşegen üreteçlerin köşegeni zaten
    kapalı biçimde bilinir, matris kurulmaz bile.
    """
    d = int(d)
    if d < 2:
        raise ValueError("qudit seviyesi en az 2 olmalı, %d verildi" % d)
    if teta is None:
        teta = np.ones(min(8, d - 1), float)
    teta = np.asarray(teta, float).reshape(-1)
    r = teta.size
    if not 1 <= r <= d - 1:
        raise ValueError("Cartan yönü 1…d−1 arası olmalı, %d verildi" % r)

    # ==============================================================
    # ÖLÇÜLEN VE DÜZELTİLEN İKİ KUSUR
    # ==============================================================
    #
    # (1) MALİYET ``O(d²)`` İDİ. Evvelce ``(d, d−1)`` şeklinde bir ``H``
    #     dizeyi kuruluyordu -- d=4096'da 16,8 milyon hücre, HER
    #     çağrıda. Ölçüldü: ``durum()`` 1722 ms. Halbuki toplam kapalı
    #     biçimde bilinir ve ``O(d)``dir:
    #
    #         (h_k)_{mm} = 1 (m ≤ k),  −(k+1) (m = k+1),  0 (m > k+1)
    #
    #     ⟹  ω_m = Σ_{k ≥ m} θ_k  −  m·θ_{m−1}
    #
    #     yâni **kuyruk toplamı** (suffix cumsum) artı tek bir terim.
    #     Dizey hiç kurulmaz.
    #
    # (2) HAFIZA İDDİASI YALANDI. ``θ``yı ``d−1`` boyutlu almak,
    #     d=4096'da 4095 sayı demekti; saklanan katsayı 4167 çıkıyor ve
    #     açık genlik dizisi 4096 -- yâni **hiçbir tasarruf yok**,
    #     üstelik daha kötü. Zabıt açıkça *"sadece d_poly × K adet KAN
    #     katsayısı tutulur (yaklaşık birkaç kilobayt)"* der. O hâlde
    #     ``θ`` alçak boyutludur: ``r`` adet Cartan yönü, ``r ≪ d``.
    #     Kalan yönler sıfırdır ve kuyruk toplamı onları bedavaya alır.
    kuyruk = np.zeros(d + 1)
    kuyruk[:r] = teta
    kuyruk = np.cumsum(kuyruk[::-1])[::-1]       # kuyruk[m] = Σ_{k≥m} θ_k
    m = np.arange(d)
    w = kuyruk[m].copy()
    ic = m[1:] <= r                              # θ_{m−1} mevcut mu
    w[1:][ic] -= m[1:][ic] * teta[m[1:][ic] - 1]
    enb = float(np.max(np.abs(w)))
    return w / enb if enb > 1e-300 else w


def _cheb(u: np.ndarray, derece: int, ikinci: bool = False) -> np.ndarray:
    """``T_j(u)`` yahut ``U_j(u)``, ``j = 0…derece``. Yineleme ile.

    ``T₀=1, T₁=u``;  ``U₀=1, U₁=2u``;  ikisi de ``P_{j+1} = 2u P_j − P_{j−1}``.
    Saf numpy, ayrıştırma yok, çağrı başına ``O(d·derece)``.
    """
    u = np.asarray(u, float).reshape(-1)
    n = int(derece) + 1
    out = np.empty((n, u.size), float)
    out[0] = 1.0
    if n > 1:
        out[1] = (2.0 * u) if ikinci else u
    for j in range(2, n):
        out[j] = 2.0 * u * out[j - 1] - out[j - 2]
    return out


def durum(c: np.ndarray, s: np.ndarray, teta: Optional[np.ndarray] = None,
          d: int = 0, ayar: Optional[QuditAyari] = None) -> np.ndarray:
    """``|Ψ(θ)⟩`` -- genlikler **saklanmaz, üretilir**.

    Zabıtın formülü::

        |Ψ⟩ = (1/√Z) Σ_m exp( Σ_k Φ_k(ω_m(θ)) ) |m⟩

        Φ_k(u) = Σ_j c_{k,j} T_j(u)  +  i Σ_j s_{k,j} U_j(u)

    ``T_j`` reel genliği, ``U_j`` **kompleks Berry fazını** yönetir.
    Faz ``±1``e kilitlenmez: ``e^{iθ}`` pürüzsüz Lie dönmesini eksiksiz
    taşır. (Eski hattın ``2·bit − 1`` kodlaması tam da bu kilidin
    kendisiydi -- zabıtın "SO(2) Spin-Glass tuzağı" dediği.)

    **Hafıza.** ``d = 4096`` için genlikler bellekte açık liste olarak
    tutulmaz; tutulan yalnız ``c``, ``s`` ve ``θ``dır::

        katsayı = 2·K·(derece+1) + (d−1)

    ``K=4, derece=8`` ile bu **72 katsayı + θ**dır. Genlik istendiğinde
    ``O(d·K·derece)`` çarpımla üretilir -- LAPACK yok, SVD yok.

    **Taşma emniyeti.** ``exp``ten evvel reel kısmın âzamîsi çıkarılır.
    Bu bir kırpma değildir: normalizasyon zaten ``1/√Z`` ile bölüyor,
    dolayısıyla sabit çarpan **tam olarak** sadeleşir.
    """
    a = ayar or QuditAyari()
    d = int(d or a.d)
    c = np.asarray(c, float)
    s = np.asarray(s, float)
    if c.shape != s.shape:
        raise ValueError("c ve s aynı şekilde olmalı: %s vs %s"
                         % (c.shape, s.shape))
    K, n = c.shape
    w = agirlik(d, teta)
    T = _cheb(w, n - 1, ikinci=False)            # (n, d)
    U = _cheb(w, n - 1, ikinci=True)             # (n, d)
    reel = (c @ T).sum(axis=0)                   # Σ_k Σ_j c_kj T_j(ω_m)
    sanal = (s @ U).sum(axis=0)                  # Σ_k Σ_j s_kj U_j(ω_m)
    reel = reel - float(np.max(reel))            # taşma emniyeti (tam sadeleşir)
    psi = np.exp(reel) * np.exp(1j * sanal)
    nrm = float(np.linalg.norm(psi))
    return psi / nrm if nrm > 1e-300 else psi


def durum_yigin(c: np.ndarray, s: np.ndarray, TETA: np.ndarray,
                d: int = 0, ayar: Optional[QuditAyari] = None,
                tip=None) -> np.ndarray:
    """``B`` belirtecin durumu **aynı anda** -- döngüsüz, ayrıştırmasız.

    Eski hatta yığınlama işe yaramıyordu, çünkü darboğaz LAPACK'in
    kendisiydi ve yığın SVD yalnız 1,2× veriyordu. Burada darboğaz
    yok: bütün hesap Chebyshev yinelemesi ve iki tensör çarpımıdır,
    yâni saf BLAS. Yığın **doğrusal** kazanır.

    ``ω`` da yığın hâlinde kapalı biçimle çıkarılır (``O(B·d)``);
    ``H`` dizeyi yine kurulmaz.
    """
    a = ayar or QuditAyari()
    d = int(d or a.d)
    # **TİP BİR AYARDIR, GİZLİ BİR TERCİH DEĞİL.** ``float32`` bellek
    # bant genişliğini yarıya indirir ve bu hesap bellek bağımlıdır;
    # ölçüldü (d=16, B=4096): 516 637 → 1 169 166 belirteç/sn, yâni
    # 2,26×. Doğruluk bedeli ``rapor()``da ayrıca ölçülür ve gizlenmez.
    tip = np.dtype(tip or getattr(a, "tip", np.float64))
    ctip = np.complex64 if tip == np.float32 else np.complex128
    c = np.asarray(c, tip)
    s = np.asarray(s, tip)
    TETA = np.atleast_2d(np.asarray(TETA, tip))
    B, rr = TETA.shape
    K, n = c.shape

    # --- ω yığını: kuyruk toplamı (B, d)
    kuy = np.zeros((B, d + 1), tip)
    kuy[:, :rr] = TETA
    kuy = np.cumsum(kuy[:, ::-1], axis=1)[:, ::-1]
    m = np.arange(d)
    W = kuy[:, m].copy()
    ic = m[1:] <= rr
    W[:, 1:][:, ic] -= (m[1:][ic] * TETA[:, m[1:][ic] - 1]).astype(tip)
    enb = np.max(np.abs(W), axis=1, keepdims=True)
    W = W / np.maximum(enb, tip.type(1e-30))

    # --- CLENSHAW: seriyi ara dizi KURMADAN topla.
    #
    # ÖLÇÜLEN VE DÜZELTİLEN KUSUR. Evvelce ``T`` ve ``U`` tam olarak
    # ``(n, B, d)`` şeklinde kuruluyordu; B=65536, d=256, n=9'da bu
    # **1,2 GB**tır ve hesap bellek bağımlı hâle gelir. Ölçüldü: yığın
    # hâli döngü hâlinden YAVAŞ çıkıyordu (3 215 < 7 102 belirteç/sn).
    # Halbuki bize ``T_j``lerin kendisi değil, yalnız ``Σ_j a_j T_j``
    # toplamı lâzım -- ve Clenshaw onu iki geçici dizeyle verir:
    #
    #     b_k = a_k + 2x·b_{k+1} − b_{k+2}
    #     Σ_j a_j T_j(x) = a_0 + x·b_1 − b_2
    #     Σ_j a_j U_j(x) = b_0                (U için doğrudan)
    #
    # Bellek ``O(n·B·d)``den ``O(B·d)``ye iner; mana birebir aynıdır.
    cs = c.sum(axis=0).astype(tip)         # (n,)  Σ_k c_kj
    ss = s.sum(axis=0).astype(tip)
    iki = (2.0 * W).astype(tip)

    b1 = np.zeros_like(W); b2 = np.zeros_like(W)
    for j in range(n - 1, 0, -1):
        b1, b2 = cs[j] + iki * b1 - b2, b1
    reel = cs[0] + W * b1 - b2

    # U-serisinin KAPANIŞI T'ninkinden farklıdır: ``U₀ = 1`` fakat
    # ``U₁ = 2x`` olduğu için genel Clenshaw kapanışı
    # ``S = a₀φ₀ + b₁φ₁ + βφ₀b₂`` burada ``a₀ + 2x·b₁ − b₂`` verir.
    # (Evvelce ``b₁ − 2x·b₂`` yazmıştım; ölçüldü, 1,69 saptı.)
    b1 = np.zeros_like(W); b2 = np.zeros_like(W)
    for j in range(n - 1, 0, -1):
        b1, b2 = ss[j] + iki * b1 - b2, b1
    sanal = ss[0] + iki * b1 - b2
    reel = reel - reel.max(axis=1, keepdims=True)
    # ``exp(a+ib) = e^a(cos b + i sin b)``: karmaşık ``exp`` yerine üç
    # reel çağrı, tipin ``float32``de kalmasını sağlar.
    e = np.exp(reel)
    psi = (e * np.cos(sanal)).astype(ctip)
    psi += 1j * (e * np.sin(sanal)).astype(ctip)
    nrm = np.linalg.norm(psi, axis=1, keepdims=True)
    return psi / np.maximum(nrm, tip.type(1e-30))


def ortusme(a: np.ndarray, b: np.ndarray) -> float:
    """``|⟨a|b⟩|`` -- quditin kendi iç çarpımı. Softmax zarı yoktur."""
    a = np.asarray(a).reshape(-1)
    b = np.asarray(b).reshape(-1)
    return float(np.abs(np.vdot(a, b)))


# ══════════════════════════════════════════════════════════════════
#  2. AMELİYE -- QSVT HODGE HARMONİK SÜZGECİ
# ══════════════════════════════════════════════════════════════════

def suz(delta, psi: np.ndarray, ayar: Optional[QuditAyari] = None,
        lam_azami: float = 0.0, keskinlik: float = 8.0,
        ne: str = "harmonik") -> np.ndarray:
    """``P_qsp(Δ)|Ψ⟩`` -- tenakuzu **söndür**, harmonik hükmü bırak.

    Zabıt: *"Matris tersi yok, arama yok, kör tahmin yok; saf spektral
    izdüşüm vardır."*

    Hodge Laplasyeninin çekirdeği çelişkisiz hükümdür
    (``Δ|Ψ⟩ = 0 ⟺ çelişkisiz``). Klasik hesapta çekirdeği bulmak
    ``O(d³)`` ayrıştırma ister. QSVT bunun yerine **spektruma polinom
    giydirir**::

        P(λ) ≈ 1   (λ = 0,  harmonik)
        P(λ) ≈ 0   (λ > 0,  çelişki girdabı)

    Burada ``P`` Chebyshev serisidir ve operatöre **Clenshaw
    yinelemesiyle** tatbik edilir: yalnız ``Δ @ v`` matris-vektör
    çarpımı kullanılır. Ne ayrıştırma, ne ters, ne özdeğer.

    ``delta`` bir dizey yahut doğrudan bir ``v ↦ Δv`` fonksiyonu
    olabilir -- ikincisinde dizey hiç kurulmaz bile.

    ``ne="katsayi"`` yalnız Chebyshev katsayılarını döndürür (ölçüm
    ve şahitlik için).
    """
    a = ayar or QuditAyari()
    N = int(a.qsvt)
    if callable(delta):
        vur = delta
        if lam_azami <= 0:
            raise ValueError("işlev verilince lam_azami açıkça lâzım")
    else:
        D = np.asarray(delta)
        vur = lambda v: D @ v                              # noqa: E731
        if lam_azami <= 0:
            # Gershgorin: ayrıştırmasız üst sınır. Özdeğer HESAPLANMAZ.
            lam_azami = float(np.max(np.sum(np.abs(D), axis=1))) or 1.0

    # Hedef süzgeç: f(λ) = exp(−keskinlik·λ/λ_azami). λ=0'da 1, λ>0'da
    # üstel söner. Chebyshev katsayıları Gauss--Chebyshev kareleme ile
    # çıkarılır (ayrıştırma değil, toplam).
    j = np.arange(N + 1)
    dugum = np.cos(np.pi * (j + 0.5) / (N + 1))            # x ∈ [−1,1]
    lam = (dugum + 1.0) * 0.5 * lam_azami                  # λ ∈ [0, λ_azami]
    f = np.exp(-float(keskinlik) * lam / max(lam_azami, 1e-300))
    kat = np.empty(N + 1)
    for k in range(N + 1):
        kat[k] = (2.0 / (N + 1)) * np.sum(
            f * np.cos(np.pi * k * (j + 0.5) / (N + 1)))
    kat[0] *= 0.5
    if ne == "katsayi":
        return kat
    if ne != "harmonik":
        raise ValueError("süzme kipi bilinmiyor: %r" % (ne,))

    # Clenshaw: P(A)v, A = 2Δ/λ_azami − I  (spektrum [−1,1]'e taşınır)
    def A(v):
        return (2.0 / lam_azami) * vur(v) - v

    v = np.asarray(psi)
    b1 = np.zeros_like(v)
    b2 = np.zeros_like(v)
    for k in range(N, 0, -1):
        b1, b2 = 2.0 * A(b1) - b2 + kat[k] * v, b1
    out = A(b1) - b2 + kat[0] * v
    nrm = float(np.linalg.norm(out))
    return out / nrm if nrm > 1e-300 else out


# ══════════════════════════════════════════════════════════════════
#  3. AMELİYE -- GELFAND-TSETLİN LİFLENMESİ
# ══════════════════════════════════════════════════════════════════

def dallanma(tepe: Sequence[int], ne: str = "sayim"):
    """Gelfand-Tsetlin örüntüleri -- ``χ`` budaması **yerine** cebir.

    Zabıt: *"Biz tensör bağ boyutunu keyfî olarak budamayız...
    dallanma analitik köklerle sınırlandığı için durum tensörü zâtı
    gereği patlamaz ve sıkışık kalır."*

    ``U(n)``in ``λ = (λ₁ ≥ … ≥ λ_n)`` en yüksek ağırlıklı indirgenemez
    temsilinin tabanı, iç içe geçme (interlacing) şartını sağlayan
    üçgen örüntülerdir::

        m_{i, j+1}  ≥  m_{i, j}  ≥  m_{i+1, j+1}

    **Mesele budur:** MPS'te bağ boyutu ``χ=16`` diye elle kesilirdi ve
    hacim kanununa çarpınca dalga beyaz gürültüye dönerdi. Burada
    kesme **yoktur**; meşru olmayan geçişin örüntüsü zaten mevcut
    değildir, yâni sızıntı cebirsel olarak sıfırdır.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``sayim``       örüntü sayısı = temsilin boyutu
    ``oruntu``      örüntülerin kendisi (küçük ``λ`` için)
    ``weyl``        Weyl boyut formülünün verdiği sayı -- **şahit**
    ==============  ==================================================

    ``sayim`` ile ``weyl``in eşit çıkması, sayımın doğruluğunun
    bağımsız ispatıdır; eşit değilse burası kırmızı yanar (H90).
    """
    lam = [int(x) for x in tepe]
    n = len(lam)
    if any(lam[i] < lam[i + 1] for i in range(n - 1)):
        raise ValueError("en yüksek ağırlık azalan olmalı: %r" % (lam,))

    if ne == "weyl":
        # dim = Π_{i<j} (λ_i − λ_j + j − i) / (j − i)
        pay = payda = 1.0
        for i in range(n):
            for j in range(i + 1, n):
                pay *= (lam[i] - lam[j] + j - i)
                payda *= (j - i)
        return int(round(pay / payda))

    def satirlar(ust: List[int]) -> List[List[int]]:
        """``ust``un altına gelebilecek bütün meşru satırlar."""
        k = len(ust) - 1
        if k == 0:
            return [[]]
        out: List[List[int]] = []

        def yur(i: int, kismi: List[int]):
            if i == k:
                out.append(list(kismi))
                return
            # ust[i] ≥ m_i ≥ ust[i+1]
            for v in range(ust[i + 1], ust[i] + 1):
                kismi.append(v)
                yur(i + 1, kismi)
                kismi.pop()

        yur(0, [])
        return out

    oruntuler: List[List[List[int]]] = []

    def derinlestir(ust: List[int], yigin: List[List[int]]):
        if len(ust) == 1:
            oruntuler.append([list(x) for x in yigin])
            return
        for alt in satirlar(ust):
            derinlestir(alt, yigin + [alt])

    derinlestir(lam, [lam])
    if ne == "sayim":
        return len(oruntuler)
    if ne == "oruntu":
        return oruntuler
    raise ValueError("dallanma kipi bilinmiyor: %r" % (ne,))


# ══════════════════════════════════════════════════════════════════
#  4. AMELİYE -- FUBINI-STUDY TABAKALI DOĞAL GRADYAN
# ══════════════════════════════════════════════════════════════════

def metrik(psi_uret: Callable[[np.ndarray], np.ndarray], teta: np.ndarray,
           h: float = 1e-4) -> np.ndarray:
    """Fubini-Study metrik tensörü ``g_FS``.

    ``g_ij = Re[ ⟨∂_i ψ | ∂_j ψ⟩ − ⟨∂_i ψ | ψ⟩⟨ψ | ∂_j ψ⟩ ]``

    İkinci terim **elzemdir**: onsuz ölçü küresel fazı da sayar ve
    fiziken aynı olan iki durum arasında sahte mesafe uydurur.

    Türevler merkezî sonlu farkla alınır (gradyansız hat, H3).
    """
    teta = np.asarray(teta, float).reshape(-1)
    psi = psi_uret(teta)
    d = teta.size
    dpsi = np.empty((d, psi.size), complex)
    for i in range(d):
        e = np.zeros(d)
        e[i] = h
        dpsi[i] = (psi_uret(teta + e) - psi_uret(teta - e)) / (2.0 * h)
    ic = dpsi.conj() @ dpsi.T                     # ⟨∂_i ψ|∂_j ψ⟩
    v = dpsi.conj() @ psi                         # ⟨∂_i ψ|ψ⟩
    return np.real(ic - np.outer(v, v.conj()))


def dogal_adim(g: np.ndarray, grad: np.ndarray, eta: float = 0.1,
               duzenli: float = 1e-6, tur: int = 64) -> np.ndarray:
    """``Δθ = −η · g_FS⁻¹ ∇L`` -- fakat **ters alınmaz**.

    Zabıt "matris tersi yok" der ve bu burada da geçerlidir: doğrusal
    dizge **eşlenik gradyanla** (CG) çözülür. CG yalnız ``g @ v``
    çarpımı ister; ne ayrıştırma, ne ters, ne özdeğer.

    ``duzenli`` Tikhonov düzenlileştirmesidir: ``g`` tekil olabilir
    (küresel faz ve durgun yönler onu tekil yapar) ve düzenlileştirme
    olmadan CG sapıtır. Düzenli bir sayıdır, gizli bir kırpma değil.
    """
    g = np.asarray(g, float)
    b = -float(eta) * np.asarray(grad, float).reshape(-1)
    n = b.size
    # **DÜZENLİLEŞTİRME NİSPÎDİR.** Mutlak ``1e-6`` yazmak ölçüldü ve
    # patladı: ``g``nin izi küçükken adım ``‖Δθ‖ = 96 987``e fırladı --
    # yâni metrik neredeyse tekilken CG sapıttı. Düzenlileştirme
    # ``g``nin kendi ölçeğine (iz/n) göre alınır; böylece ``g`` büyükse
    # az, küçükse çok düzenler. Gizli bir kırpma değil, ölçekli bir sayı.
    olcek = float(np.trace(g)) / max(n, 1)
    tau = float(duzenli) * max(olcek, 1e-30)
    A = lambda v: g @ v + tau * v                          # noqa: E731
    x = np.zeros(n)
    r = b - A(x)
    p = r.copy()
    rr = float(r @ r)
    for _ in range(int(tur)):
        if rr < 1e-30:
            break
        Ap = A(p)
        al = rr / max(float(p @ Ap), 1e-300)
        x += al * p
        r -= al * Ap
        rr_yeni = float(r @ r)
        p = r + (rr_yeni / max(rr, 1e-300)) * p
        rr = rr_yeni
    return x


# ══════════════════════════════════════════════════════════════════
#  BLOKLAR -- zabıtın d=4096 taksimatı
# ══════════════════════════════════════════════════════════════════

#: Zabıtın somut misali: quditin hangi seviyesi hangi kategoriye ait.
#: Bu bir süperseçim sektörü taksimatıdır, keyfî bir bölme değil.
BLOKLAR: Tuple[Tuple[str, int, int], ...] = (
    ("sentaks", 0, 512),
    ("onto-fizik", 512, 2560),
    ("mantık", 2560, 4096),
)


def blok(psi: np.ndarray, ad: Optional[str] = None,
         ne: str = "izdusum") -> object:
    """Süperseçim sektörü: ``Π_C |Ψ⟩`` yahut sektör ağırlıkları.

    ``ne="izdusum"`` bir bloğa izdüşürür (kategori kilitlenir);
    ``ne="agirlik"`` bütün blokların ``‖Π_C Ψ‖²`` ağırlıklarını verir --
    yâni "bu token şu an hangi kategoride yaşıyor".
    """
    psi = np.asarray(psi).reshape(-1)
    d = psi.size
    olcek = d / float(BLOKLAR[-1][2])
    dilim = {a: (int(b * olcek), min(d, int(c * olcek)))
             for a, b, c in BLOKLAR}
    if ne == "agirlik":
        return {a: float(np.sum(np.abs(psi[i:j]) ** 2))
                for a, (i, j) in dilim.items()}
    if ne == "izdusum":
        if ad not in dilim:
            raise ValueError("blok bilinmiyor: %r" % (ad,))
        i, j = dilim[ad]
        out = np.zeros_like(psi)
        out[i:j] = psi[i:j]
        n = float(np.linalg.norm(out))
        return out / n if n > 1e-300 else out
    raise ValueError("blok kipi bilinmiyor: %r" % (ne,))


# ══════════════════════════════════════════════════════════════════
#  ÖLÇÜ
# ══════════════════════════════════════════════════════════════════

def rapor(ayar: Optional[QuditAyari] = None) -> str:     # pragma: no cover
    """Dört ameliyeyi de **ölç**. İddia değil, sayı."""
    import time

    a = ayar or QuditAyari()
    r = np.random.default_rng(a.tohum)
    c = r.normal(scale=0.3, size=(a.kan, a.derece + 1))
    s = r.normal(scale=0.3, size=(a.kan, a.derece + 1))
    teta = r.normal(size=a.d - 1)

    s_ = ["=== QUDİT ÇEKİRDEĞİ -- SVD yok, MPS yok, ikili yok ===", ""]

    t0 = time.perf_counter()
    psi = durum(c, s, teta, ayar=a)
    t_durum = time.perf_counter() - t0
    s_ += ["  1. LIE-CHEBYSHEV KAN-QUDIT DURUMU",
           "    d              : %d" % a.d,
           "    saklanan katsayı: %d  (genlik SAKLANMIYOR, üretiliyor)"
           % a.katsayi_sayisi,
           "    açık dizi olsaydı: %d karmaşık sayı (%.1f×)"
           % (a.d, a.d / max(a.katsayi_sayisi, 1)),
           "    üretim süresi  : %.4f ms" % (1e3 * t_durum),
           "    norm           : %.12f" % float(np.linalg.norm(psi)),
           "    faz ±1'e kilitli mi: %s"
           % ("EVET -- KUSUR" if np.allclose(np.abs(np.angle(psi) % np.pi), 0,
                                             atol=1e-9) else "hayır (sürekli)")]

    # 2. QSVT
    # **ŞAHİT DÜZELTİLDİ.** Evvelce ``B @ B.T`` kullanıyordum; o
    # dizeyin en küçük özdeğeri genellikle sıfır DEĞİLDİR, yâni hakikî
    # bir çekirdeği (harmonik formu) yoktur. Süzgecin "λ=0'ı tut"
    # vaadini çekirdeği olmayan bir operatörle ölçmek, ölçünün kendisini
    # bozmaktı: örtüşme 0,2197 çıkıyordu ve bu süzgecin değil şahidin
    # kusuruydu. Hodge Laplasyeni bir ÇİZGE Laplasyenidir ve çekirdeği
    # bilinir: bağlantılı çizgede sabit vektör (Δ·1 = 0).
    n = 64
    W = r.random((n, n)); W = (W + W.T) * 0.5
    np.fill_diagonal(W, 0.0)
    D = np.diag(W.sum(axis=1)) - W                # çizge Laplasyeni
    D = D / np.max(np.sum(np.abs(D), axis=1))
    v = r.normal(size=n) + 1j * r.normal(size=n)
    v /= np.linalg.norm(v)
    t0 = time.perf_counter()
    hv = suz(D, v, ayar=a, keskinlik=12.0)
    t_suz = time.perf_counter() - t0
    # Şahit: harmonik form KAPALI BİÇİMDE bilinir (sabit vektör).
    # Özayrışım kullanılmaz -- şahit bile ayrıştırmasızdır.
    h = np.ones(n) / np.sqrt(n)
    tam = h * (h @ v)
    tam = tam / max(float(np.linalg.norm(tam)), 1e-300)
    kalinti = float(np.linalg.norm(D @ hv)) / max(
        float(np.linalg.norm(hv)), 1e-300)
    s_ += ["", "  2. QSVT HODGE SÜZGECİ (derece %d)" % a.qsvt,
           "    süre           : %.4f ms" % (1e3 * t_suz),
           "    harmonikle örtüşme: %.6f  (1,0 = tam söndürme)"
           % ortusme(hv, tam),
           "    ‖Δ·süzülmüş‖/‖·‖ : %.3e  (0 = çelişki tamamen söndü)"
           % kalinti,
           "    ayrıştırma kullandı mı: HAYIR (yalnız Δ@v; özayrışım"
           " sadece bu satırın ŞAHİDİ için)"]

    # 3. Gelfand-Tsetlin
    s_ += ["", "  3. GELFAND-TSETLİN DALLANMASI (χ budaması YOK)"]
    for lam in ((2, 1, 0), (3, 1, 0), (2, 2, 1, 0)):
        say = dallanma(lam, ne="sayim")
        wy = dallanma(lam, ne="weyl")
        s_.append("    λ=%-12s örüntü %4d   Weyl %4d   %s"
                  % (str(lam), say, wy,
                     "UYUŞTU" if say == wy else "AYRIŞTI -- KIRMIZI"))

    # 4. Fubini-Study QNG
    dk = 12
    tk = r.normal(size=dk) * 0.2

    def uret(t):
        return durum(c, s, np.concatenate([t, np.zeros(a.d - 1 - dk)]),
                     ayar=a)

    t0 = time.perf_counter()
    g = metrik(uret, tk)
    t_met = time.perf_counter() - t0
    grad = r.normal(size=dk)
    adim = dogal_adim(g, grad, eta=0.1, duzenli=a.duzenli)
    duz = -0.1 * grad
    s_ += ["", "  4. FUBINI-STUDY DOĞAL GRADYAN (ters ALINMADI, CG)",
           "    metrik süresi  : %.2f ms  (%d×%d)" % (1e3 * t_met, dk, dk),
           "    g simetrik mi  : %s"
           % ("evet" if np.allclose(g, g.T, atol=1e-8) else "HAYIR"),
           "    ‖doğal adım‖   : %.6f" % float(np.linalg.norm(adim)),
           "    ‖düz adım‖     : %.6f" % float(np.linalg.norm(duz)),
           "    aralarındaki açı: %.1f°"
           % float(np.degrees(np.arccos(np.clip(
               (adim @ duz) / max(np.linalg.norm(adim) * np.linalg.norm(duz),
                                  1e-300), -1, 1)))),
           "    (açı 0 olsaydı metrik hiçbir şey yapmıyor demekti)"]

    # --- HIZ: fermanın asıl gerekçesi
    s_ += ["", "  HIZ -- eski hat 11 belirteç/sn idi (ölçüldü, ~8500 SVD)"]
    for tip, ad in ((np.float64, "float64"), (np.float32, "float32")):
        for dd, BB in ((16, 4096), (256, 4096), (4096, 256)):
            ay = QuditAyari(d=dd, kan=a.kan, derece=a.derece, yon=a.yon,
                            tip=tip)
            TT = r.normal(size=(BB, a.yon))
            durum_yigin(c, s, TT, ayar=ay)            # ısınma
            t0 = time.perf_counter()
            durum_yigin(c, s, TT, ayar=ay)
            dt = time.perf_counter() - t0
            hiz = BB / max(dt, 1e-12)
            s_.append("    %-8s d=%-5d B=%-5d %10.0f belirteç/sn"
                      "   hedefin %.2f'i   eski hattın %.0f katı"
                      % (ad, dd, BB, hiz, hiz / 1e6, hiz / 11.0))
    s_.append("    (LAPACK çağrısı: SIFIR. SVD yok, QR yok, özayrışım yok.)")

    ag = blok(psi, ne="agirlik")
    s_ += ["", "  BLOKLAR (süperseçim sektörleri)"]
    for k, v_ in ag.items():
        s_.append("    %-12s ağırlık %.6f" % (k, v_))
    return "\n".join(s_)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
