"""
Kübit yazmacı: milyonlarca kübit, MERA, süperpozisyon ve **ölçülen** dolaşıklık.

Evvelki inşada "kübit" diye bir şey yoktu; belirteç gömmeleri üzerinde
bir ortalama ağacı vardı. Burada gerçek bir kuantum durumu taşınır.

**Temsil.** Durum bir Matris Çarpım Durumudur (MPS):

    |Ψ⟩ = Σ  A₁^{i₁} A₂^{i₂} … A_N^{i_N} |i₁ i₂ … i_N⟩

``A`` dizisi ``(N, χ, 2, χ)`` şeklindedir. Bellek kübit sayısıyla
**doğrusal**: ``N · χ² · 2 · 4`` bayt (float32). ``χ = 8`` için kübit
başına 512 bayt; 6 000 000 kübit **3.07 GB** eder ve tek bir kartın
belleğine sığar. ``2^6000000`` genliğin hiçbir zaman açılmadığı yer
burasıdır.

**Cebir reeldir.** Karmaşık genlik yerine ``ℝ`` üzerinde çalışılır;
faz ``e^{-iπ} = −1`` yerine **işaret** taşır. Yıkıcı girişim aynen
çalışır (zıt işaretli genlikler birbirini sıfırlar), üniterlik yerine
diklik (``QᵀQ = I``) vardır ve norm cebren korunur. Kaybedilen şey
``e^{iθ}``nın ara fazlarıdır; kazanılan şey iki kat bellek ve gerçek
SVD'dir. Bu bir tercihtir ve gizlenmez.

**MERA.** Kübitler bir MERA durumudur (kütük H24): her kademede önce
**dolanıklık çözücü** ``U`` komşu çifti karıştırır, sonra **izometri**
``W`` çifti bir üst kademeye taşır. Kademe sayısı ``log₂N``dir; 1. kübit
ile 6 000 000. kübit arası bağ 23 kademede kurulur.

**Dolaşıklık iddia edilmez, ÖLÇÜLÜR.** ``dolasiklik_entropisi`` bir
kesitteki Schmidt spektrumundan von Neumann entropisini hesaplar:
``S = −Σ λ² log λ²``. Çarpım durumunda tam sıfırdır; dolaşıkta
pozitiftir. Rapor bu sayıyı basar.
"""
from __future__ import annotations

import math
import time

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# PTR bölümünün Chebyshev tabanı. ``kuantum.nqs`` bu dosyayı
# import ETMEZ (ölçüldü), dolayısıyla döngü yoktur.
from kuantum.kapilar import chebyshev

__all__ = ["Yazmac", "hadamard", "dik_iki_kubit", "dik_iki_kubit_yigin",
           "MERAKademe", "mps_birlestir", "mps_kirp", "mps_norm",
           "mps_genlik", "dyadic_katla", "dyadic_katla_yigin",
           "hdtf_yigin", "sozluk_qtt", "token_cekirdegi", "hdtf_kur",
           "hdtf_olcusu", "IcBag", "ic_bag_parametresi",
           "acik_parametre", "ic_bag_kur", "ic_bag_ac",
           "etkin_chi_kiyasi", "vram_cetveli", "qtt_cekirdek_ayristir",
           "qtt_cekirdek_ac", "qtt_parametre", "kapali_form_kiyasi",
           "TensorHalka", "PolinomHalka", "AgacAyar", "AgacYazmaci",
           "Dugum", "UcAgac", "iki_kademeli_donme", "IhtimalYazmaci",
           "kubit_hesabi", "hiyerarsik_ikili_agac_katlama",
           "KulliYazmac"]

_H2 = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.float32) / np.sqrt(2.0)


def hadamard() -> np.ndarray:
    """``H = [[1,1],[1,−1]]/√2`` -- süperpozisyon kapısı.

    ``|0⟩ → (|0⟩+|1⟩)/√2``. ``N`` kübite tatbik edilince ``2^N`` taban
    durumunun **hepsi** eşit genlikle doğar. Bu, MPS'te ``χ = 1`` ile
    tam olarak temsil edilir: süperpozisyon bedava, dolaşıklık pahalıdır.
    """
    return _H2.copy()


#: İki kübitlik kapıların kurulma usulü: ``"cayley"`` yahut ``"us"``.
#:
#: **Ölçüm için değiştirilebilir olmalıdır** (kütük H90). İkisi de
#: ``SO(4)``e düşer ve küçük açıda birebir aynıdır (fark 3,5e-10);
#: ayrıldıkları yer **erişilebilirliktir** -- bkz. ``dik_iki_kubit_us``.
#:
#: **Varsayılan ``"us"``tur ve bu ÖLÇÜMLE karara bağlandı (H120).**
#: Hedef ``diag(1,1,−1,−1)``e (bir π dönmesi) eğim inişiyle uyum
#: aranınca::
#:
#:     usul     beş ayrı tohumda nihaî kayıp   hedefe âzamî mesafe
#:     cayley   0,0714 (hepsinde aynı)         0,188
#:     us       0,000000                       0,0000
#:
#: Cayley her tohumda aynı duvara çarpıyor: tekil noktaya asimptotik
#: yaklaşıyor, asla varamıyor. Bedeli ölçüldü ve **yoktur**: kapı
#: kurmak tek başına 2,5-5 kat pahalı, fakat uçtan uca akış 1,646 sn'ye
#: karşı 1,587 sn -- kapı kurmak, SVD'lerin yanında görünmüyor.
KAPI_USULU: str = "us"


def kapi_usulu(usul: str) -> str:
    """Kapı usulünü değiştir; **evvelki hâli** döndürür."""
    global KAPI_USULU
    if usul not in ("cayley", "us"):
        raise ValueError("usul 'cayley' yahut 'us' olmalı")
    eski = KAPI_USULU
    KAPI_USULU = usul
    return eski


#: ``gesdd`` düşüp Gram yedeğine geçilen kere sayısı -- gizlenmez.
_SVD_YEDEK: int = 0


def _kararli_svd(M: np.ndarray):
    """``np.linalg.svd``in **determinist** ve yakınsaması garanti hâli.

    ===================================================================
    NİÇİN VAR: TAVAN KALKINCA LAPACK YAKINSAMIYOR
    ===================================================================

    χ tavanı icradan kaldırılınca (kütük H149) bağ boyutu büyüdü ve
    LAPACK'in ``gesdd`` sürücüsü bazı dizeylerde ``SVD did not
    converge`` hatası verdi. Yani tavan, imha ettiği bilginin yanında
    bir de sayısal kararlılığı ayakta tutuyormuş; bu bir fayda değil,
    **kusurun kusuru örtmesi**dir.

    Yedek yol **jitter yahut rastgele kaydırma DEĞİLDİR**: ceride
    stokastiği açıkça yasaklar (aynı girdi aynı çıktıyı vermelidir).
    Onun yerine Gram dizeyinin özayrışımı kullanılır ve o determinist:

        M = U S Vᵀ   ⟹   MᵀM = V S² Vᵀ   (yahut  MMᵀ = U S² Uᵀ)

    ``eigh`` simetrik dizeylerde ``gesdd``den kat kat sağlamdır, zira
    Jacobi/QL özyinelemesi simetriyi bozmaz. Küçük tarafın Gram'ı
    alınır ki maliyet ``min(m,n)³`` kalsın.

    HUDUT: Gram almak koşul sayısını **kareler** (κ → κ²), yani çok
    kötü koşullu dizeylerde küçük tekil değerlerin hassasiyeti düşer.
    Onun için bu yol yalnız ``gesdd`` düştüğünde işletilir, daima
    değil; ve düştüğü ``_svd_yedek`` sayacında sayılır, gizlenmez.
    """
    M = np.asarray(M)
    if not np.isfinite(M).all():
        M = np.nan_to_num(M, nan=0.0, posinf=0.0, neginf=0.0)
    try:
        return np.linalg.svd(M, full_matrices=False)
    except np.linalg.LinAlgError:
        pass
    global _SVD_YEDEK
    _SVD_YEDEK += 1
    m, n = M.shape[-2], M.shape[-1]
    if n <= m:                       # MᵀM (n×n) daha küçük
        G = np.swapaxes(M, -1, -2) @ M
        w, V = np.linalg.eigh(G)
        w = np.clip(w[..., ::-1], 0.0, None)
        V = V[..., ::-1]
        s = np.sqrt(w)
        esik = np.maximum(s[..., :1], 1e-30) * 1e-6
        olcek = np.where(s > esik, 1.0 / np.maximum(s, 1e-30), 0.0)
        U = (M @ V) * olcek[..., None, :]
        Vt = np.swapaxes(V, -1, -2)
    else:                            # MMᵀ (m×m) daha küçük
        G = M @ np.swapaxes(M, -1, -2)
        w, U = np.linalg.eigh(G)
        w = np.clip(w[..., ::-1], 0.0, None)
        U = U[..., ::-1]
        s = np.sqrt(w)
        esik = np.maximum(s[..., :1], 1e-30) * 1e-6
        olcek = np.where(s > esik, 1.0 / np.maximum(s, 1e-30), 0.0)
        Vt = (np.swapaxes(U, -1, -2) @ M) * olcek[..., :, None]
    tip = M.dtype
    return U.astype(tip), s.astype(tip), Vt.astype(tip)


def dik_iki_kubit(teta: np.ndarray) -> np.ndarray:
    """6 açıdan ``SO(4)`` kapısı -- usule göre Cayley yahut üstel.

    ``so(4)`` altı boyutludur (``4·3/2``); ters simetrik bir üreteçten
    Cayley dönüşümü ``Q = (I−A)(I+A)⁻¹`` tam dik bir dizey verir.
    Dolaşıklığı üreten budur: çarpım durumundaki iki kübit bu kapıdan
    geçince Schmidt rütbesi 1'den 2'ye çıkar.

    **Cayley'in erişemediği yer vardır ve ölçüldü (H120):** ``det(I+Q)
    = 0`` olan her dönme, yani bütün **π dönmeleri**. Reel yazmaçta
    yegâne faz π olduğu için (H98) bu, melekelerin işaret çevirmeyi
    hiç öğrenememesi demektir. ``KAPI_USULU = "us"`` o boşluğu kapatır.
    """
    if KAPI_USULU == "us":
        return dik_iki_kubit_us(teta)
    A = np.zeros((4, 4), dtype=np.float64)
    iu = np.triu_indices(4, 1)
    A[iu] = np.asarray(teta, float).reshape(-1)[:6]
    A = A - A.T
    I = np.eye(4)
    Q = np.linalg.solve((I + A).T, (I - A).T).T
    return Q.astype(np.float32)


def _so4_ureteci(teta: np.ndarray) -> np.ndarray:
    """``(..., 6)`` açı → ``(..., 4, 4)`` ters simetrik ``so(4)`` üreteci."""
    t = np.asarray(teta, float)
    A = np.zeros(t.shape[:-1] + (4, 4))
    iu = np.triu_indices(4, 1)
    A[..., iu[0], iu[1]] = t[..., :6]
    return A - np.swapaxes(A, -1, -2)


def dik_iki_kubit_us(teta: np.ndarray) -> np.ndarray:
    """6 açıdan ``SO(4)`` kapısı -- **üstel harita** ile, ``exp(A)``.

    ``dik_iki_kubit`` (Cayley) ile aynı işi görür ve aynı gruba düşer;
    farkı **erişebildiği kümededir** ve bu fark ölçüldü.

    **Cayley'in eksiği (kütük H120).** ``Q = (I−A)(I+A)⁻¹`` yalnız
    ``det(I+Q) ≠ 0`` olan ``Q``lara ulaşır. Yani ``−1`` özdeğerli her
    dönme -- bütün **π dönmeleri** -- Cayley'in erişemediği yerdedir.
    Ölçüldü::

        hedef  diag(1, 1, −1, −1)  ∈ SO(4),  det(I+Q) = 0
        exp    ile hata            2,22e-16   (tam)
        Cayley ile en iyi          0,3563     (300 000 rastgele deneme)

    Ve bu, bu mimaride **tam da ihtiyaç duyulan** kapıdır: reel
    yazmaçta ``e^{iθ}`` yoktur, yalnız ``π`` fazı vardır (kütük H98).
    Yani melekelerin öğrenilen kapıları, reel yazmacın sahip olduğu
    **yegâne fazı** kuramıyordu. İşaret çeviren her şey (``faz_z``,
    ``CZ``, ``sadakat`` kapıları) o yüzden elle konmak zorunda kaldı;
    hiçbir meleke onu öğrenemezdi.

    ``exp``, tıkız ve bağlantılı bir grupta **örtendir**: ``SO(4)``ün
    tamamına ulaşır. Maliyet bir ``4×4`` özayrışımdır ve yığın hâlinde
    ``numpy`` tarafından taşınır.

    **Ölçek Cayley'e uydurulmuştur.** Cayley açılınca
    ``(I−A)(I+A)⁻¹ = I − 2A + O(A²)``, ``exp`` ise ``I + A + O(A²)``
    verir; yani aynı açı ikisinde **farklı** kapı demektir. Ölçüldü:
    ``θ ~ 1e-3``te ``exp(−2A)`` ile Cayley arasındaki fark 3,5e-10.
    Bu yüzden burada ``exp(−2A)`` kullanılır ve usul değiştiğinde
    öğrenilmiş bütün açılar aynı manada kalır -- yalnız π dönmeleri
    artık erişilebilirdir.
    """
    return dik_iki_kubit_us_yigin(np.asarray(teta, float).reshape(-1)[:6])


def dik_iki_kubit_us_yigin(teta: np.ndarray) -> np.ndarray:
    """``(..., 6)`` açı → ``(..., 4, 4)`` dik kapı yığını -- ``exp(−2A)``.

    ``A`` ters simetrik ⟹ ``iA`` Hermiteseldir; ``eigh`` tam üsteli
    verir (seri kesmesi yok). Netice cebren ``SO(4)``tedir.
    """
    A = -2.0 * _so4_ureteci(teta)
    oz, V = np.linalg.eigh(1j * A)
    E = np.matmul(V * np.exp(-1j * oz)[..., None, :],
                  np.conjugate(np.swapaxes(V, -1, -2)))
    return np.real(E).astype(np.float32)


def dik_iki_kubit_yigin(teta: np.ndarray) -> np.ndarray:
    """``(..., 6)`` açı → ``(..., 4, 4)`` dik kapı yığını -- Cayley.

    ``dik_iki_kubit``in yığın hâli. ``np.linalg.solve`` yığın eksenini
    kendisi taşır, dolayısıyla Python döngüsü yoktur: 500 parametre
    varyantının kapıları tek çağrıda kurulur.
    """
    if KAPI_USULU == "us":
        return dik_iki_kubit_us_yigin(teta)
    t = np.asarray(teta, float)
    yig = t.shape[:-1]
    A = np.zeros(yig + (4, 4))
    iu = np.triu_indices(4, 1)
    A[..., iu[0], iu[1]] = t[..., :6]
    A = A - np.swapaxes(A, -1, -2)
    I = np.broadcast_to(np.eye(4), yig + (4, 4))
    Q = np.linalg.solve(np.swapaxes(I + A, -1, -2),
                        np.swapaxes(I - A, -1, -2))
    return np.swapaxes(Q, -1, -2).astype(np.float32)


@dataclass
class MERAKademe:
    """Bir MERA kademesinin izi -- ölçüm için."""
    kademe: int
    yuva: int                  # bu kademedeki düğüm sayısı
    bag: int                   # χ
    kesme_hatasi: float        # SVD budamasında atılan ağırlık


class Yazmac:
    """``N`` kübitlik MPS yazmacı -- reel genlikli, dik kapılı."""

    def __init__(self, n: int, bag: int = 8, tohum: int = 0,
                 tip=np.float32, obek: int = 250_000,
                 yigin: int = 1) -> None:
        """``yigin`` (``B``) tane **bağımsız** durum tek dizide taşınır.

        Kullanıcı hükmü: *"doğrudan yığına geç, tek-durum yolunu
        kaldır"* ve *"İKİSİ BİRDEN -- iki eksen (parametre × veri)"*.
        ``B`` o iki eksenin çarpımıdır (``B = P·V``): ``P`` ayrı
        parametre kümesi × ``V`` ayrı girdi. Bir kayıp çağrısının
        tamamı böylece **tek yığında** geçer.

        Kapılar üç şekilde verilebilir ve altyapı üçünü de kabul eder:

        * ``(2,2)`` / ``(4,4)``      -- bütün yığına aynı kapı,
        * ``(m,2,2)`` / ``(m,4,4)``  -- yuvaya göre değişen kapı,
        * ``(B,m,2,2)`` / ``(B,m,4,4)`` -- **yığın üyesine göre** değişen
          kapı; parametre ekseni ancak bununla iş görür.

        Tek durum artık ``yigin=1``dir; ayrı bir kod yolu yoktur.
        """
        if n < 2:
            raise ValueError("n ≥ 2 olmalı")
        self.n, self.bag, self.tip = int(n), int(bag), tip
        self.obek = int(obek)
        self.B = max(1, int(yigin))
        # |00…0⟩ : her yuvada tek genlik 1, yığının her üyesinde
        self.A = np.zeros((self.B, self.n, self.bag, 2, self.bag), dtype=tip)
        self.A[:, :, 0, 0, 0] = 1.0
        self.rng = np.random.default_rng(tohum)
        self.iz: List[MERAKademe] = []
        # ``bag_ust[k]``: ``A[k-1]`` ile ``A[k]`` arasındaki bağın
        # **üst sınırı**. Uçlar 1'dir; başlangıçta durum çarpımdır ve
        # bütün bağlar 1'dir. Bu dizi ``kesme_gerekli_mi``nin tek
        # dayanağıdır ve daima ÜST SINIR olarak tutulur -- şüphede
        # ``bag``a çekilir, yani asla olduğundan küçük gösterilmez.
        self.bag_ust = np.ones(self.n + 1, dtype=np.int64)
        #: Kesme sınırındaki **en dar** nispî boşluk ve kaç kere kesildiği
        #: (bkz. ``_cift_kapi_cekirdek``, kütük H168). Sıfıra yakın bir
        #: boşluk, kayıp yüzeyinin orada türevlenemediğinin delilidir.
        self._kesme_bosluk = float("inf")
        self._kesme_buyukluk = float("inf")
        self._kesme_sayisi = 0
        # **SADAKAT KÜTÜĞÜ (kütük H114).** Kesme telâfisi durumu normlu
        # tutar; o hâlde norm artık kaybı ölçmez. Kaybın hakikî ölçüsü,
        # kapı başına TUTULAN kesrin çarpımıdır::
        #
        #     F = Π_kapı ( Σsk² / Σs² )
        #
        # ``[0,1]``dedir, çarpımsaldır ve kıyas edilebilir. Logaritması
        # tutulur ki çarpım alt taşmasın.
        self._sadakat_log = 0.0
        # **MELEKE BAŞINA χ TAVANI (kütük H118, Dosya 1).** ``bag`` ayrılan
        # yerin üst sınırıdır; ``bag_tavan`` ise O ANDA izin verilen
        # Schmidt rütbesidir. Her meleke kendi sınıfına göre bunu
        # daraltır (çözücüler 1'e kadar), sonra iade eder.
        #
        # Bu bir ÜNİTER iddia değildir ve öyle olduğu iddia edilmiyor:
        # sabit bir üniter kapı bir alt uzayı şartsız söndüremez (H107).
        # Burada yapılan, KESME cetvelidir -- kesme zaten üniter değil,
        # yaklaşıklığın kendisidir. Dosya 1'in tablosu böyle okunur.
        self.bag_tavan = int(bag)

    # -----------------------------------------------------------------
    @property
    def bayt(self) -> int:
        return int(self.A.nbytes)

    def kubit_basina_bayt(self) -> float:
        return self.bayt / (self.n * self.B)

    def _kapi_yigini(self, G: np.ndarray, m: int, d: int) -> np.ndarray:
        """Kapıyı ``(B·m, d, d)`` düzenine getir -- üç şekli de kabul eder."""
        Gt = np.asarray(G, self.tip)
        if Gt.ndim == 2:
            Gt = np.broadcast_to(Gt, (self.B, m, d, d))
        elif Gt.ndim == 3:
            Gt = np.broadcast_to(Gt[None], (self.B, m, d, d))
        return np.ascontiguousarray(Gt).reshape(self.B * m, d, d)

    # -----------------------------------------------------------------
    #  Tek kübitlik kapı -- bütün yuvalara aynı anda
    # -----------------------------------------------------------------
    def tek_kapi(self, G: np.ndarray, yuvalar: Optional[slice] = None) -> None:
        """``A[.., i, ..] ← Σ_j G[i,j] A[.., j, ..]`` -- vektörel.

        Bütün ``N`` yuvaya tek bir ``einsum`` ile uygulanır; Python
        döngüsü yoktur. 6 milyon kübitte bu tek çağrıdır.
        """
        # ÖBEKLİ ve YERİNDE. Bütün diziye tek ``einsum`` yazılıp ölçüldü
        # ve **kaldı**: 6 milyon kübitte durum 2.86 GB iken tepe bellek
        # 8.62 GB'a çıkıyor (çıktı için ikinci bir tam dizi + einsum ara
        # tamponu), sonra MERA'da makine düşüyordu. Öbek başına geçici
        # tampon sabittir; tepe bellek artık kübit sayısından bağımsızdır.
        Gt = np.ascontiguousarray(G.astype(self.tip))
        if yuvalar is None:
            bas, son = 0, self.n
        else:
            bas = yuvalar.start or 0
            son = self.n if yuvalar.stop is None else yuvalar.stop
        adim = max(self.obek, 1)
        for b0 in range(bas, son, adim):
            b1 = min(b0 + adim, son)
            k = b1 - b0
            blok = self.A[:, b0:b1]                   # (B, k, X, 2, X)
            # ``einsum("ij,mjb->mib", …)`` yerine tek yığın çarpımı.
            # Yığın ekseni ``B`` de aynı düzleşmeye girer; kapı bütün
            # yığına aynıdır (yuvaya göre değişeni ``tek_kapi_yigin``).
            v = blok.reshape(self.B * k * self.bag, 2, self.bag)
            v[...] = np.matmul(Gt, v)

    def superpozisyona_sok(self) -> None:
        """Bütün kübitlere Hadamard: ``2^N`` taban durumu eşit genlikle.

        Bundan sonra ``genlik(x)`` her ``x`` dizilişi için ``2^{-N/2}``dir
        ve ``dolasiklik_entropisi`` **sıfırdır** -- süperpozisyon var,
        dolaşıklık yok. İkisinin ayrı şeyler olduğu burada ölçülür.
        """
        self.tek_kapi(hadamard())

    # -----------------------------------------------------------------
    #  İki kübitlik kapı -- fırça düzeninde, SVD ile bölerek
    # -----------------------------------------------------------------
    def cift_kapi(self, G: np.ndarray, ofset: int = 0,
                  alt: int = 0, ust: Optional[int] = None) -> float:
        """``(2i+ofset, 2i+1+ofset)`` çiftlerinin hepsine aynı anda.

        Θ = A_k · A_{k+1} birleştirilir, ``4×4`` kapı fiziksel indekse
        uygulanır, sonra **SVD** ile ikiye bölünüp bağ ``χ``ye budanır.
        Budamada atılan ağırlık döndürülür -- kesme hatası gizlenmez.

        Bütün çiftler tek bir yığın SVD'sinde çözülür; Python döngüsü
        yoktur.

        ``alt``/``ust`` zinciri **daraltır**: kapılar yalnız
        ``[alt, ust)`` aralığında vurulur. Sözleşme ölçümünde (kütük
        H119) ölçüldü ki MERA bütün zincire vuruyor ve daha hiçbir delil
        görülmeden küllî hüküm bloğunu karıştırıyordu -- halbuki
        ``superpozisyon`` o bloğu kasten ``|0⟩``da bırakır. Aralık bu
        yüzden vardır.
        """
        n, X = self.n, self.bag
        ust = n if ust is None else min(int(ust), n)
        alt = max(0, int(alt))
        bas = alt + ofset
        m = (ust - bas) // 2
        if m <= 0:
            return 0.0
        # ÖBEKLEME. Bütün çiftleri tek seferde işlemek, ara tensörleri
        # (Θ ve SVD çıktıları) durumun ~9 katına çıkarıyor -- ölçüldü:
        # 0.48 GB'lık 1 milyon kübitlik durumda tepe bellek 4.42 GB.
        # 6 milyon kübitte bu 26 GB eder ve makine düşer. Öbek boyu
        # sabittir, dolayısıyla tepe bellek kübit sayısından BAĞIMSIZDIR.
        if m > self.obek:
            top = 0.0
            for b0 in range(0, m, self.obek):
                b1 = min(b0 + self.obek, m)
                top += self._cift_kapi_dilim(G, bas + 2 * b0, b1 - b0)
            return top
        return self._cift_kapi_dilim(G, bas, m)

    # -----------------------------------------------------------------
    #  YIĞIN KAPILAR -- asıl hız buradadır
    # -----------------------------------------------------------------
    def tek_kapi_yigin(self, yuvalar: np.ndarray,
                       G: np.ndarray) -> None:
        """``m`` **ayrı** yuvaya ``m`` **ayrı** kapı -- TEK numpy çağrısı.

        **Neden var.** Melekeler kapıları tek tek vuruyordu:
        ``for i: for j: q.tek(veri(i,j), R(θ))``. Ölçüldü -- 3 satırlık
        minik bir koşuda 675 kapı, 0,53 sn; yani kapı başına ~0,8 ms,
        oysa yapılan iş bir ``2×2 @ 2×(χ·χ)`` çarpımıdır ve mikrosaniye
        mertebesindedir. Vaktin tamamı Python çağrı masrafına gidiyordu.
        Burada ``m`` kapı tek bir yığın çarpımına iner.

        ``G`` ya ``(2,2)`` (hepsine aynı kapı) ya da ``(m,2,2)``dir.
        Yuvaların **ayrık** olması şarttır; aksi hâlde numpy'nin süslü
        indeksle yazması aynı yuvaya iki kere yazar ve netice sıraya
        bağlı olur -- sessiz bir yanlış. Onun için denetlenir.
        """
        idx = np.asarray(yuvalar, np.intp) % self.n
        if idx.size == 0:
            return
        if np.unique(idx).size != idx.size:
            raise ValueError("tek_kapi_yigin: yuvalar ayrık olmalı")
        m, X = idx.size, self.bag
        Gt = self._kapi_yigini(G, m, 2)
        # (B, m, X, 2, X) → (B·m, 2, X·X) : fiziksel indis öne
        V = self.A[:, idx].transpose(0, 1, 3, 2, 4
                                     ).reshape(self.B * m, 2, X * X)
        V = np.matmul(Gt, V).reshape(self.B, m, 2, X, X
                                     ).transpose(0, 1, 3, 2, 4)
        self.A[:, idx] = V

    def cift_kapi_yigin(self, sol_yuvalar: np.ndarray,
                        G: np.ndarray) -> float:
        """``(i, i+1)`` çiftlerinin **hepsine** tek yığın SVD'siyle kapı.

        ``sol_yuvalar`` keyfîdir; **düzgün adımlı olmak zorunda değildir**.
        Şart, çiftlerin birbirine değmemesidir (``i+1 < i'``). Böylece
        bir satırın bütün fırça çiftleri, hattâ farklı satırların
        çiftleri, tek bir ``(m, 2χ, 2χ)`` yığın SVD'sinde çözülür.

        Eski ``_cift_kapi_dilim`` yalnız ``stride 2`` diziliş biliyordu;
        zincirde veri ile yerel hüküm kübitleri iç içe olduğu için
        melekelerin çiftleri o kalıba oturmuyor ve her biri **ayrı**
        çağrı oluyordu (547 çağrı, 0,42 sn). Bu, o kısıtı kaldırır.
        """
        idx = np.asarray(sol_yuvalar, np.intp)
        if idx.size == 0:
            return 0.0
        if np.any(idx < 0) or np.any(idx + 1 >= self.n):
            raise IndexError("çift kapı zincir dışına taşıyor")
        s = np.sort(idx)
        if np.any(np.diff(s) < 2):
            raise ValueError("cift_kapi_yigin: çiftler ayrık olmalı")
        return self._cift_kapi_cekirdek(G, idx, idx + 1)

    def _cift_kapi_dilim(self, G: np.ndarray, bas: int, m: int) -> float:
        sol_idx = np.arange(bas, bas + 2 * m, 2, dtype=np.intp)
        return self._cift_kapi_cekirdek(G, sol_idx, sol_idx + 1)

    def kesme_gerekli_mi(self, li: np.ndarray) -> bool:
        """Bu çiftlerde budama **gerekli mi**? Gerekmiyorsa QR yeter.

        **Yeni nesil formül ve niçin gerekti.** Ölçüldü: numpy'nin yığın
        SVD'si gerçek yığın DEĞİLDİR -- matris başına maliyet 32×32'de
        ``4,08e-04``ten ancak ``2,38e-04``e iner (1,7 kat) ve ``m=64``ten
        sonra düzleşir. Yığına geçmenin uçtan uca kazancı bu yüzden
        beklenen 8-16 kat değil **1,4 kat** çıktı. Aynı ölçümde QR,
        SVD'den **3,8-6,8 kat** hızlıdır.

        Çare: ``Θ``nın rütbesi ``χ``yi aşmıyorsa budama diye bir şey
        yoktur ve bölme için SVD gerekmez -- ``Θ = QR`` yeter, üstelik
        **tam**dır (hiçbir şey atılmaz). ``Θ``nın rütbesi
        ``min(2·d_sol, 2·d_sağ)`` ile sınırlıdır; ikisi de ``bag_ust``ta
        tutulur.

        Bu, uyarlanır ``χ`` DEĞİLDİR (kullanıcı sabit ``χ`` dedi):
        bellek yine sabit ``χ``dir, yalnız hesap ucuzlar.
        """
        dl, dr = self._bag_sinirlari(li)
        return 2 * min(dl, dr) > self.bag

    def _bag_sinirlari(self, li: np.ndarray) -> Tuple[int, int]:
        """Bu çiftler için sol ve sağ bağın üst sınırı (hepsinin âzamîsi)."""
        dl = int(self.bag_ust[np.minimum(li, self.n)].max())
        dr = int(self.bag_ust[np.minimum(li + 2, self.n)].max())
        return min(dl, self.bag), min(dr, self.bag)

    def _bag_guncelle(self, li: np.ndarray) -> None:
        yeni = np.minimum(2 * np.minimum(self.bag_ust[li],
                                         self.bag_ust[np.minimum(li + 2,
                                                                 self.n)]),
                          self.bag)
        self.bag_ust[li + 1] = np.maximum(self.bag_ust[li + 1], yeni)

    def _cift_kapi_cekirdek(self, G: np.ndarray, li: np.ndarray,
                            ri: np.ndarray) -> float:
        X = self.bag
        m = li.size
        Bm = self.B * m
        sol = self.A[:, li].reshape(Bm, X, 2, X)
        sag = self.A[:, ri].reshape(Bm, X, 2, X)
        # Θ[m, a, i, j, c] = Σ_b sol[m,a,i,b] sag[m,b,j,c]
        #
        # **Hız kusuru, ölçüldü ve kaldırıldı (kütük H54, 5. borç).**
        # Bu iki büzülme ``np.einsum(..., optimize=True)`` ile
        # yazılmıştı. Profil çıkarıldı: 3 kübitlik minik bir koşuda
        # ``einsum`` 0,420 sn tutuyor ve bunun **0,232 sn'si**
        # ``einsum_path``, yani yol arama. Yani vaktin yarısı, 2×2'lik
        # tensörler için en iyi büzülme sırasını aramaya gidiyordu.
        # Sıra zaten sabittir ve bellidir; ikisi de yığın çarpımıdır:
        #   sol(m,X,2,X) → (m, 2X, X) ,  sag(m,X,2,X) → (m, X, 2X)
        #   çarpım (m, 2X, 2X) tam olarak Θ'nın kendisidir.
        T = np.matmul(sol.reshape(Bm, X * 2, X),
                      sag.reshape(Bm, X, 2 * X)).reshape(Bm, X, 4, X)
        # ``G``nin üç şekli de ``(B·m, 4, 4)``e getirilir.
        Gt = self._kapi_yigini(G, m, 4)
        T = np.matmul(T.transpose(0, 1, 3, 2),
                      Gt.transpose(0, 2, 1)[:, None, :, :])
        T = T.transpose(0, 1, 3, 2)
        # (m, X, 2, 2, X) → (m, X·2, 2·X): sol yuva | sağ yuva kesiti
        T = T.reshape(Bm, X, 2, 2, X).reshape(Bm, X * 2, 2 * X)
        # --- BUDAMA GEREKMİYORSA QR: tam, ucuz, kayıpsız
        if not self.kesme_gerekli_mi(li):
            dl, dr = self._bag_sinirlari(li)
            # **``T``yi gerçek bağ sınırlarına KIRPMAK şarttır.** İlk
            # hâlde ham ``T``ye QR uygulandı ve kırıldı: QR'ın rütbesi
            # matrisin ŞEKLİNDEN gelir (``2χ``), gerçek rütbesinden
            # değil. Sıfır satırlar ``Q``da yine yer kaplıyor ve netice
            # ``χ``ye sığmıyordu. Kırpınca rütbe ``min(2d_sol, 2d_sağ)``
            # olur ve tanım gereği ``χ``yi aşmaz.
            Tk = T.reshape(Bm, X, 2, 2, X)[:, :dl, :, :, :dr]
            Tk = Tk.reshape(Bm, dl * 2, 2 * dr)
            Q, R = np.linalg.qr(Tk)
            r = Q.shape[2]
            yeni_sol = np.zeros((Bm, X, 2, X), dtype=self.tip)
            yeni_sol[:, :dl, :, :r] = Q.reshape(Bm, dl, 2, r)
            yeni_sag = np.zeros((Bm, X, 2, X), dtype=self.tip)
            yeni_sag[:, :r, :, :dr] = R.reshape(Bm, r, 2, dr)
            self.A[:, li] = yeni_sol.reshape(self.B, m, X, 2, X)
            self.A[:, ri] = yeni_sag.reshape(self.B, m, X, 2, X)
            self._bag_guncelle(li)
            return 0.0
        # ``astype(np.float32)`` KALDIRILDI: ``self.tip`` zaten float32
        # ve o çağrı her kapıda tam bir kopya çıkarıyordu. Tip artık
        # baştan sona tektir (kullanıcı hükmü: "her yer float32").
        U, s, Vt = _kararli_svd(T)
        r = max(1, min(X, int(self.bag_tavan), s.shape[1]))
        # **KESME SINIRINDAKİ BOŞLUK -- türevlenebilirliğin ölçüsü.**
        # Budama bir SIRALAMADIR: ``s[r−1]`` ile ``s[r]`` kesiştiğinde
        # tutulan altuzay sıçrar ve kayıp yüzeyi orada türevlenemez.
        # Kütük H88 pürüzün şüphelisini SVD kesmesi diye bırakmış fakat
        # ölçememişti; ölçülemeyişinin sebebi buydu -- boşluk yalnız
        # kesme ANINDA görünür, kesildikten sonra tayfta yeri kalmaz.
        # Sayı burada zabıtlanır ve `nefs/ikiz.py` onu okur.
        if s.shape[1] > r:
            ust = s[:, r - 1]
            alt = s[:, r]
            # **YALANCI YEŞİL TUZAĞI.** ``ust`` ve ``alt`` ikisi de
            # sıfırsa boşluk ``0/1e-30 = 0`` çıkar ve "dejenere" gibi
            # görünür -- hâlbuki orada kesilecek bir şey yoktur.
            # Ölçüye ancak **fiilen atılan** bir ağırlık varken girer.
            gecerli = ust > 1e-12 * (ust.max() + 1e-30)
            if bool(np.any(gecerli)):
                b = np.min(((ust - alt) / (ust + alt + 1e-30))[gecerli])
                self._kesme_bosluk = min(self._kesme_bosluk, float(b))
                self._kesme_buyukluk = min(
                    self._kesme_buyukluk, float(np.min(ust[gecerli])))
                self._kesme_sayisi += 1
        atilan = float(np.sum(s[:, r:] ** 2)) if s.shape[1] > r else 0.0
        toplam = float(np.sum(s ** 2)) + 1e-30
        Uk = U[:, :, :r]                        # (m, 2X, r)
        sk = s[:, :r]
        Vk = Vt[:, :r, :]                       # (m, r, 2X)
        # **BURADA BİR KUSUR VARDI VE KALDIRILDI.** Evvelce tekil
        # değerler ``sk / ‖sk‖`` ile cebren birim yapılıyordu ("norm
        # koru" niyetiyle). Bu yanlıştı: MPS kanonik biçimde değilken
        # ``‖sk‖`` durumun normu değil, o bağdaki ayar (gauge)
        # büyüklüğüdür; birim yapmak durumu her iki-kübitlik kapıda
        # yeniden ölçekler.
        #
        # Ölçüldü (χ=128, kesme = 0, float64): tek TAKAS git-gel sonrası
        # ``‖Δgenlik‖/‖genlik‖ = 2.52e-01``; fakat en iyi ölçek
        # çıkarıldığında kalan 6.5e-08 ve ölçek **0.748**. Yani hata saf
        # bir büzülmeydi: yön doğru, şiddet kayıp. Satır kalkınca aynı
        # ölçüm **1.57e-15** verir -- yani işlem tam tersinir olur.
        #
        # Şimdiye kadar gizlenmesinin sebebi bütün okumaların normalize
        # olmasıdır (``ρ/iz``, ``P/Σ``). Fakat yazmaç o hâliyle üniter
        # DEĞİLDİ; kapılar dik olduğu için norm zaten cebren korunur ve
        # bu satıra hiç ihtiyaç yoktur.
        # İki tam ``(m, X, 2, X)`` tampon tahsis edip sıfırlamak yerine
        # doğrudan yerine yazılır: her kapıda iki tahsis + iki sıfırlama
        # eksilir. ``r < X`` iken artan bağ bileşenleri temizlenmelidir,
        # yoksa eski ayar kalıntısı yeni duruma sızar.
        # --- KESME TELÂFİSİ (kütük H114). Yukarıdaki şerh, ``sk``yı
        # BİRİM yapmanın yanlış olduğunu doğru tespit ediyor: kanonik
        # olmayan biçimde ``‖sk‖`` durumun normu değil ayarın
        # büyüklüğüdür. Fakat oradan "hiç ölçekleme yapma" neticesi
        # çıkarılmıştı ve o da yanlıştı.
        #
        # **Ölçüldü:** akış sonunda ``⟨Ψ|Ψ⟩ = 4,5e-12`` (χ=8), χ=128'de
        # bile ``1,8e-05``. Yani durum normu çarpımsal olarak çöküyor;
        # float32'de genlikler ``1e-6`` mertebesine inince hassasiyet de
        # gidiyor.
        #
        # Doğrusu, ayarı bozmadan **yalnız atılan ağırlığı telâfi
        # etmektir**::
        #
        #     ölçek = √( Σs²  /  Σsk² )          (satır başına)
        #
        # Bu bir skalerdir ve iki-yuva tensörünü skalerle çarpmak
        # durumun TAMAMINI çarpar; dolayısıyla ayar serbestliğine
        # dokunmaz, yalnız kesmenin açtığı gediği kapatır. Kesme
        # nispeti (``atilan/toplam``) yine olduğu gibi raporlanır --
        # unutma gizlenmiyor, yalnız durum durum olarak kalıyor.
        # Bu, TEBD'in standart usulüdür.
        kalan = np.sum(sk ** 2, axis=1)
        tam = np.sum(s ** 2, axis=1)
        olcek = np.sqrt(np.where(kalan > 1e-30, tam / np.maximum(kalan, 1e-30),
                                 1.0))
        sk = sk * olcek[:, None].astype(sk.dtype)
        # Kayıp burada zabıtlanır: telâfi durumu normlu tuttuğu için
        # norm artık kaybı GÖSTERMEZ; gösteren, tutulan kesrin çarpımıdır.
        with np.errstate(divide="ignore", invalid="ignore"):
            self._sadakat_log += float(np.sum(np.log(
                np.clip(kalan / np.maximum(tam, 1e-30), 1e-300, 1.0))))

        kok = np.sqrt(sk)
        yeni_sol = np.zeros((Bm, X, 2, X), dtype=self.tip)
        yeni_sol[:, :, :, :r] = (Uk * kok[:, None, :]).reshape(Bm, X, 2, r)
        yeni_sag = np.zeros((Bm, X, 2, X), dtype=self.tip)
        yeni_sag[:, :r, :, :] = (kok[:, :, None] * Vk).reshape(Bm, r, 2, X)
        self.A[:, li] = yeni_sol.reshape(self.B, m, X, 2, X)
        self.A[:, ri] = yeni_sag.reshape(self.B, m, X, 2, X)
        self._bag_guncelle(li)
        return atilan / toplam

    # -----------------------------------------------------------------
    #  STIEFEL İZOMETRİSİ -- kanonik hâl (ceridenin 1. müdahalesi)
    # -----------------------------------------------------------------
    def kanonikle(self, merkez: Optional[int] = None) -> Dict[str, float]:
        """MPS'i **karışık kanonik** hâle getir; kesmeyi en iyi kıl.

        ===================================================================
        NİÇİN: KESME EN İYİ DEĞİLDİ ve bu kütükte YAZILIYDI
        ===================================================================

        `Yazmac.tekil_yogunluklar`ın şerhi şöyle diyor: *"bu yazmaç
        kanonik biçimde **değildir** (kapılar QR/SVD ile yerinde
        bölünüyor, merkez taşınmıyor)."* Kütük H121 de aynı yerde
        durur.

        Bunun bedeli teknik fakat ağırdır. İki yuvalık ``Θ``nın SVD'si
        **en iyi kesmeyi ancak çevre dik ise** verir. Çevre dik
        değilse tekil değerler, atılan durumların hakikî ağırlığını
        **temsil etmez**: küçük bir tekil değer büyük bir fizikî
        genliğe karşılık gelebilir. Yani her kapıda "en az zararlı
        olanı attım" diyoruz fakat ispatı yok.

        Bu, kütükte ölçülmüş iki büyük kaybın (H146: kapı başına 0,93;
        H147: üç melekede yıkım) **arkasındaki ihtimaldir** ve şimdiye
        kadar hiç sınanmamıştı.

        ===================================================================
        USUL -- Stiefel manifoldunda iki süpürme
        ===================================================================

        Bir MPS tensörü ``A[k] ∈ ℝ^{χ×2×χ}``, ``(χ·2, χ)`` dizeyi olarak
        okunduğunda **Stiefel manifoldunda** bir noktadır: sütunları dik
        ve birim ise ``Aᵀ A = I``. QR ayrışımı tam olarak o manifolda
        izdüşümdür ve **tersinirdir** -- atılan hiçbir şey yoktur, ``R``
        komşuya devredilir.

            sol süpürme  (0 → merkez)  : A[k] = Q ,  A[k+1] ← R·A[k+1]
            sağ süpürme  (n−1 → merkez): A[k] = Qᵀ,  A[k−1] ← A[k−1]·L

        Netice: merkezin solundaki her tensör **sol-izometrik**,
        sağındaki her tensör **sağ-izometriktir**; merkezde duran
        tensörün tekil değerleri artık **hakikî Schmidt katsayılarıdır**
        ve kesme ispatlı olarak en iyidir (Eckart–Young).

        ===================================================================
        HUDUT -- açıkça
        ===================================================================

        * Maliyet ``O(n·χ³)``dir ve **her kapıda yapılamaz**; akışta
          meleke başına bir kere çağrılır (bkz. `nefs/qmeleke.py`).
          Faydası bu maliyete değiyor mu, **ölçülür**, iddia edilmez.
        * Kanoniklik yalnız çağrıldığı **anda** doğrudur; sonraki her
          kapı onu bir parça bozar. O yüzden ``kanonik_hata`` ile ne
          kadar bozulduğu ölçülebilir ve bu fonksiyon kendi iddiasını
          denetleyebilir hâle gelir (H90).
        * Durumu **hiç değiştirmez**: QR tersinirdir, ``R`` atılmaz.
          Sınama bunu ölçer -- değiştirseydi kanoniklik uğruna fizik
          bozulmuş olurdu.
        """
        n, X, B = self.n, self.bag, self.B
        if n < 2:
            return {"sol": 0, "sağ": 0}
        c = int(n // 2 if merkez is None else np.clip(merkez, 0, n - 1))
        A = self.A
        # --- sol süpürme: 0 → c-1 sol-izometrik olsun
        for k in range(c):
            M = A[:, k].reshape(B, X * 2, X).astype(np.float64)
            Q, R = np.linalg.qr(M)                 # (B, X·2, r), (B, r, X)
            r = Q.shape[2]
            yeni = np.zeros((B, X, 2, X), dtype=self.tip)
            yeni[:, :, :, :r] = Q.reshape(B, X, 2, r).astype(self.tip)
            A[:, k] = yeni
            nx = np.zeros((B, X, 2, X), dtype=self.tip)
            # R·A[k+1]: (B,r,X) @ (B,X,2X) → (B,r,2X)
            t = np.matmul(R, A[:, k + 1].reshape(B, X, 2 * X).astype(
                np.float64))
            nx[:, :r] = t.reshape(B, r, 2, X).astype(self.tip)
            A[:, k + 1] = nx
            self.bag_ust[k + 1] = min(int(self.bag_ust[k + 1]), max(r, 1))
        # --- sağ süpürme: n-1 → c+1 sağ-izometrik olsun
        for k in range(n - 1, c, -1):
            M = A[:, k].reshape(B, X, 2 * X).astype(np.float64)
            # LQ ayrışımı = (QR of Mᵀ)ᵀ
            Q, R = np.linalg.qr(M.transpose(0, 2, 1))   # (B,2X,r),(B,r,X)
            r = Q.shape[2]
            yeni = np.zeros((B, X, 2, X), dtype=self.tip)
            yeni[:, :r] = Q.transpose(0, 2, 1).reshape(
                B, r, 2, X).astype(self.tip)
            A[:, k] = yeni
            L = R.transpose(0, 2, 1)                    # (B, X, r)
            nx = np.zeros((B, X, 2, X), dtype=self.tip)
            # A[k-1]·L: (B, X·2, X) @ (B, X, r) → (B, X·2, r)
            t = np.matmul(A[:, k - 1].reshape(B, X * 2, X).astype(np.float64),
                          L)
            nx[:, :, :, :r] = t.reshape(B, X, 2, r).astype(self.tip)
            A[:, k - 1] = nx
            self.bag_ust[k] = min(int(self.bag_ust[k]), max(r, 1))
        return {"merkez": float(c), "sol": float(c), "sağ": float(n - 1 - c)}

    def kanonik_hata(self, merkez: Optional[int] = None) -> float:
        """Kanoniklikten **âzamî sapma** -- ölçüt kendini denetlesin.

        Sol taraf için ``‖Aᵀ A − I‖_∞``, sağ taraf için ``‖A Aᵀ − I‖_∞``.
        ``kanonikle`` çağrıldıktan hemen sonra makine hassasiyetinde
        olmalı; kapılar vurdukça büyümeli. Büyümüyorsa ölçüt kördür.
        """
        n, X, B = self.n, self.bag, self.B
        if n < 2:
            return 0.0
        c = int(n // 2 if merkez is None else np.clip(merkez, 0, n - 1))
        en = 0.0
        for k in range(c):
            M = self.A[:, k].reshape(B, X * 2, X).astype(np.float64)
            g = np.matmul(M.transpose(0, 2, 1), M)
            # yalnız fiilen kullanılan bağ bloğuna bakılır
            d = max(1, int(self.bag_ust[min(k + 1, self.n)]))
            g = g[:, :d, :d]
            en = max(en, float(np.max(np.abs(g - np.eye(d)[None]))))
        for k in range(n - 1, c, -1):
            M = self.A[:, k].reshape(B, X, 2 * X).astype(np.float64)
            g = np.matmul(M, M.transpose(0, 2, 1))
            d = max(1, int(self.bag_ust[min(k, self.n)]))
            g = g[:, :d, :d]
            en = max(en, float(np.max(np.abs(g - np.eye(d)[None]))))
        return en

    # -----------------------------------------------------------------
    #  Yuvaya mahsus kapılar, takas ve **tek süpürme**
    # -----------------------------------------------------------------
    def tek_kapi_yuva(self, i: int, G: np.ndarray) -> None:
        """Yalnız ``i``inci yuvaya tek kübitlik kapı.

        ``tek_kapi`` aynı kapıyı bütün yuvalara vurur; melekelerin
        çoğunda ise her yuvaya **kendi** kapısı lazımdır.
        """
        self.tek_kapi_yigin(np.array([int(i) % self.n], np.intp), G)

    def cift_kapi_yuva(self, i: int, G: np.ndarray) -> float:
        """``(i, i+1)`` komşu çiftine tek bir ``4×4`` kapı.

        ``_cift_kapi_dilim``in ``m = 1`` hâli; kesme hatasını döndürür.
        """
        i = int(i)
        if i < 0 or i + 1 >= self.n:
            raise IndexError("çift kapı için i, i+1 zincirde olmalı")
        return self._cift_kapi_dilim(G, i, 1)

    #: SWAP: ``|ij⟩ → |ji⟩``. İki kübitlik indeks düzeni ``2i+j``dir
    #: (bkz. ``_cift_kapi_dilim``deki ``reshape(m, X, 4, X)``).
    TAKAS = np.array([[1., 0., 0., 0.],
                      [0., 0., 1., 0.],
                      [0., 1., 0., 0.],
                      [0., 0., 0., 1.]], dtype=np.float32)

    def takas(self, i: int) -> float:
        """``i`` ile ``i+1``i yer değiştir -- **tam**, yaklaşık değil."""
        return self.cift_kapi_yuva(i, self.TAKAS)

    def supurme(self, blok_bas: int, blok_uzunluk: int,
                duraklar: Sequence[int], kapi,
                geri_gotur: bool = True) -> Dict[str, float]:
        """Bir bloğu zincirde **bir kere** yürüt, geçerken kapıları vur.

        Naif usulde her uzak kapı için ayrı gidip gelinir: ``k`` kapı ve
        ortalama ``D`` mesafe için ``O(k·D)`` takas. Zincirde ``k``
        durağın hepsine uğranacaksa bu ``O(N²)``dir.

        Burada blok soldan sağa **tek** süpürülür; her durağın yanından
        geçerken kapı orada vurulur. Toplam takas ``O(N)``dir. Bu,
        dikkatteki "tek geçişte hepsini hallet" fikrinin MPS
        karşılığıdır.

        **Ne kadar aynı?** Ölçüldü (14 kübit, 4 durak, float64,
        genlikler üzerinden -- yani ayardan bağımsız):

        =====  =====================  ==================
        ``χ``  süpürme − naif         süpürme kesmesi
        =====  =====================  ==================
        64     2.10e-03               4.07e-30
        128    3.39e-05               5.68e-30
        256    6.18e-07               1.14e-29
        512    6.57e-07               2.28e-29
        =====  =====================  ==================

        ``χ`` yeterliyken fark sayısal hassasiyete iner (çok sayıda SVD
        biriktiği için tam sıfır olmaz). ``χ`` darken fark gerçektir ve
        kesmeden gelir: iki usul zinciri farklı yollardan geçtiği için
        farklı yerlerde budama yapar. "Birebir aynıdır" DENMEZ; ölçülen
        budur.

        Takas sayısı: bu misalde 20'ye karşı 44 (2.2×). Kazanç durak
        sayısıyla büyür: ``k`` durak ve ``D`` ortalama mesafe için naif
        ``2kD``, süpürme ``~2D``.

        ``geri_gotur`` VARSAYILAN OLARAK AÇIKTIR ve öyle olmalıdır.
        Kapatmak o an bir şey kaybettirmez (durum, hangi kübitin ipte
        kaçıncı boncuk olduğu dışında aynıdır) fakat **borç bırakır**:
        (1) yerellik gider -- blok ortada kalırsa bir satırın kendi
        kübitleri ikiye bölünür, sonraki melekenin "yerel" kapısı artık
        yerel değildir; (2) takas, geçtiği kesitlerde dolaşıklığı
        sürükler ve ``χ``yi zorlar, yani **kesme hatası** biriktirir.
        Geri götürmek o sürüklemeyi geri sarar. Maliyet iki katıdır ve
        hâlâ ``O(N)``dir.

        ``kapi(durak, blok_yeri) -> 4×4 dizey | None`` çağrılır; ``None``
        dönerse o durakta kapı vurulmaz.
        """
        yer = int(blok_bas)
        kesme = 0.0
        takas_sayisi = 0
        vurulan = 0
        # Duraklar, bloğun YOL SIRASINA göre dizilir. Artan sırada
        # dizmek kurulup ölçüldü ve **kaldı**: blok sağ uçtan başlayıp en
        # soldaki durağa gidiyor, sonra geri sağa dönüyordu -- zikzak,
        # yani tek süpürme değil. Yön, durakların ağırlık merkezinden
        # okunur; sıra o yönde tekdüze (monoton) olur.
        ham = [int(x) for x in duraklar]
        if not ham:
            return {"takas": 0.0, "kapı": 0.0, "kesme": 0.0,
                    "blok_yeri": float(blok_bas)}
        yon = 1.0 if (sum(ham) / len(ham)) >= blok_bas else -1.0
        hedefler = sorted(ham, key=lambda h: (h - blok_bas) * yon)
        # Blok, sol ucundan itibaren sağa doğru yürür. Blok ``blok_uzunluk``
        # kübittir; yürütmek, bloğun sol komşusuyla takasını blok boyunca
        # tekrarlamaktır.
        for hedef in hedefler:
            while yer > hedef + 1:
                for k in range(blok_uzunluk):
                    kesme += self.takas(yer - 1 + k)
                    takas_sayisi += 1
                yer -= 1
            while yer + blok_uzunluk <= hedef:
                for k in range(blok_uzunluk - 1, -1, -1):
                    kesme += self.takas(yer + k)
                    takas_sayisi += 1
                yer += 1
            # blok artık durağın bitişiğinde: kapıyı vur
            G = kapi(hedef, yer)
            if G is not None:
                komsu = yer - 1 if yer > hedef else yer + blok_uzunluk - 1
                komsu = max(0, min(komsu, self.n - 2))
                kesme += self.cift_kapi_yuva(komsu, G)
                vurulan += 1
        if geri_gotur:
            while yer > blok_bas:
                for k in range(blok_uzunluk):
                    kesme += self.takas(yer - 1 + k)
                    takas_sayisi += 1
                yer -= 1
            while yer < blok_bas:
                for k in range(blok_uzunluk - 1, -1, -1):
                    kesme += self.takas(yer + k)
                    takas_sayisi += 1
                yer += 1
        return {"takas": float(takas_sayisi), "kapı": float(vurulan),
                "kesme": float(kesme), "blok_yeri": float(yer)}

    # -----------------------------------------------------------------
    #  MPO: kübitleri oynatmadan bütün zincire aynı anda etki et
    # -----------------------------------------------------------------
    def mpo_uygula_hizli(self, W: Dict[int, np.ndarray], D: int,
                         bas: int = 0, son: Optional[int] = None,
                         sol_sinir: Optional[np.ndarray] = None,
                         sag_sinir: Optional[np.ndarray] = None,
                         esik: float = 1e-6) -> float:
        """Zip-up ile dene; **kesme ısırırsa** iki geçişliye geri dön.

        ===================================================================
        BU KANUN ÖLÇÜMDEN ÇIKTI, TERCİHTEN DEĞİL
        ===================================================================

        İki usul, ``n = 12``de **tam yoğun dalgayla** (kesmesiz hakikat)
        yüzleştirildi. Sadakat, gauge'dan bağımsız tek hakemdir --
        ``sadakat_log`` ile ölçmenin ne getirdiğini kütük H167 yazıyor.

            D    χ    ε    | iki geçiş   zip      | sadakat_2g  sadakat_zip
            ─────────────────────────────────────────────────────────────
             8    8  0,05  |  0,0082 s  0,0020 s  |  1,000000   1,000000
             8   16  0,05  |  1,1999 s  0,0078 s  |  1,000000   1,000000
            16   16  0,05  |  5,1103 s  0,0742 s  |  1,000000   1,000000
            16   16  0,40  |  4,7007 s  0,0714 s  |  1,000000   1,000000
            ─────────────────────────────────────────────────────────────
            16    8  0,15  |  0,1683 s  0,0063 s  |  0,902517   0,491593
            16    8  0,40  |  1,3226 s  0,0071 s  |  0,883912   0,486003

        **Hüküm:** ``χ`` yettiği sürece ikisi de makine hassasiyetinde
        aynıdır ve zip **22-186 kat** hızlıdır. ``χ`` yetmediğinde zip
        çöker (0,49 v 0,90), zira soldan sağa yürürken sağdaki çevreyi
        görmemiştir ve kırpması Eckart-Young manasında en iyi değildir.

        O hâlde usul sabit seçilmez, **kesmeye bakılarak** seçilir: zip
        denenir, attığı ağırlık ``esik``i aşarsa durum geri alınır ve
        iki geçişli usul koşar. Yedek yol pahalıdır fakat yalnız
        kesmenin fiilen ısırdığı hâllerde koşar -- ve o hâllerde zaten
        hızdan evvel doğruluk lâzımdır.
        """
        yedek = self.A.copy()
        ust = self.bag_ust.copy()
        atilan = self.mpo_uygula_zip(W, D, bas=bas, son=son,
                                     sol_sinir=sol_sinir,
                                     sag_sinir=sag_sinir)
        if atilan <= float(esik):
            return atilan
        # kesme ısırdı: durumu geri al, en iyi kırpmayı yapan usule geç
        self.A = yedek
        self.bag_ust = ust
        return self.mpo_uygula(W, D, bas=bas, son=son,
                               sol_sinir=sol_sinir, sag_sinir=sag_sinir)

    def mpo_uygula_zip(self, W: Dict[int, np.ndarray], D: int,
                       bas: int = 0, son: Optional[int] = None,
                       sol_sinir: Optional[np.ndarray] = None,
                       sag_sinir: Optional[np.ndarray] = None) -> float:
        """MPO'yu **tek geçişte** uygula: bağ hiç ``χ·D``ye çıkmadan kırpılır.

        ===================================================================
        NİÇİN VAR: ``mpo_uygula``NIN MASRAFI YANLIŞ YERDE
        ===================================================================

        ``mpo_uygula`` iki geçişlidir: evvelâ bütün zincirde bağ ``χ·D``ye
        **çıkarılır**, sonra sağdan sola QR ile kanonikleştirilip soldan
        sağa SVD ile ``χ``ye indirilir. Profil çıkarıldı ve masrafın
        yeri bulundu: vaktin **%84'ü** o QR süpürmesindedir ve QR,
        birleştirilmiş bağda, yani ``(2χD) × (χD)`` dizeylerde
        koşmaktadır. χ = D = 16'da bu ``512 × 256``dır ve yuva başına
        ``6,7e7`` FLOP eder; halbuki kırpılmış bağda aynı iş
        ``(2χ) × (χD)``, yani ``32 × 256``dır.

        Zip-up usulü (Stoudenmire-White) bağı hiç şişirmez: soldan sağa
        yürünür, her yuvada MPO ile MPS büzülür, **derhal** SVD ile
        ``χ``ye kırpılır ve artan kısım bir sonraki yuvaya taşınır::

            Θ[r,i,q,b] = Σ_{p,a} taşınan[r,p,a] · T[p,a,i,q,b]
            (r·2, D·X) → SVD → r' ≤ χ
            yeni çekirdek = U ,  taşınan = S·Vᵀ

        Böylece hiçbir yerde ``χ·D`` bağlı bir tensör kanonikleştirilmez.

        **Bedeli vardır ve gizlenmez:** iki geçişli usul, kırpmadan evvel
        zinciri kanonikleştirdiği için Eckart-Young manasında **en iyi**
        kırpmayı yapar; zip-up ise soldan sağa yürürken sağdaki çevreyi
        henüz görmemiştir, dolayısıyla kırpması en iyi **değildir**.
        Fark ölçülür (`nefs/hiz.py`) ve hangi usulün kullanılacağı
        ölçüye bakılarak seçilir, iddiaya değil.
        """
        son = self.n if son is None else int(son)
        bas = max(0, int(bas))
        if son <= bas:
            return 0.0
        X = self.bag
        tip = self.tip
        Bn = self.B
        kimlik = np.zeros((D, 2, 2, D), dtype=tip)
        for w in range(D):
            kimlik[w, 0, 0, w] = 1.0
            kimlik[w, 1, 1, w] = 1.0

        sl = np.zeros(D, tip) if sol_sinir is None else np.asarray(sol_sinir,
                                                                   tip)
        sr = np.zeros(D, tip) if sag_sinir is None else np.asarray(sag_sinir,
                                                                   tip)
        if sol_sinir is None:
            sl[0] = 1.0
        if sag_sinir is None:
            sr[0] = 1.0

        # ``tasinan[B, r, p, a]`` -- soldan gelen kalıntı. Başlangıçta
        # ``r = 1``dir ve MPS'in sol ucu 0. bağ indisinde durur.
        tas = np.zeros((Bn, 1, D, X), dtype=tip)
        tas[:, 0, :, 0] = sl[None, :]

        cekirdek: List[np.ndarray] = []
        atilan = 0.0
        for k in range(bas, son):
            Ak = self.A[:, k]                            # (B, X, 2, X)
            Wk = np.asarray(W.get(k, kimlik), tip)       # (D, 2, 2, D)
            # T[B, p, a, i, q, b] = Σ_j W[p,i,j,q] A[a,j,b]
            W2 = Wk.transpose(0, 1, 3, 2).reshape(D * 2 * D, 2)
            A2 = Ak.transpose(2, 0, 1, 3).reshape(2, Bn * X * X)
            P = (W2 @ A2).reshape(D, 2, D, Bn, X, X)     # (p,i,q,B,a,b)
            T = P.transpose(3, 0, 4, 1, 2, 5)            # (B,p,a,i,q,b)
            r = tas.shape[1]
            # Θ[B, r, i, q, b] = Σ_{p,a} tas[B,r,p,a] T[B,p,a,i,q,b]
            Th = np.matmul(tas.reshape(Bn, r, D * X),
                           T.reshape(Bn, D * X, 2 * D * X)
                           ).reshape(Bn, r, 2, D, X)
            M = Th.reshape(Bn, r * 2, D * X)
            U, sv, Vt = _kararli_svd(M)
            rk = max(1, min(X, int(self.bag_tavan), sv.shape[1]))
            top = float(np.sum(sv ** 2)) + 1e-30
            atilan += float(np.sum(sv[:, rk:] ** 2)) / top
            cekirdek.append(U[:, :, :rk].reshape(Bn, r, 2, rk))
            tas = (sv[:, :rk, None] * Vt[:, :rk, :]).reshape(Bn, rk, D, X)

        # sağ sınır: kalıntının MPO bacağı ``sr`` ile kapanır
        son_c = np.tensordot(tas, sr, axes=([2], [0]))    # (B, rk, X)
        cekirdek[-1] = np.matmul(
            cekirdek[-1].reshape(Bn, -1, cekirdek[-1].shape[3]),
            son_c).reshape(Bn, cekirdek[-1].shape[1], 2, X)

        self.bag_ust[bas + 1:son] = X
        yeni = np.empty((Bn, X, 2, X), dtype=tip)
        for i, k in enumerate(range(bas, son)):
            t = cekirdek[i]
            ka, kb = min(t.shape[1], X), min(t.shape[3], X)
            yeni[...] = 0.0
            yeni[:, :ka, :, :kb] = t[:, :ka, :, :kb]
            self.A[:, k] = yeni
        return atilan

    def mpo_uygula(self, W: Dict[int, np.ndarray], D: int,
                   bas: int = 0, son: Optional[int] = None,
                   sol_sinir: Optional[np.ndarray] = None,
                   sag_sinir: Optional[np.ndarray] = None) -> float:
        """Matris Çarpım Operatörünü duruma uygula ve ``χ``ye geri sıkıştır.

        **Takas ağının kapanan yolu.** Uzak iki kübite kapı vurmak için
        onları yan yana getirmek, geçilen her kesitte hakiki dolaşıklığı
        sürükler; ölçüldü ve ``χ`` ile KAPANMADI (χ=8'de kapı başına
        4.0e-02 kesme, χ=128'de hâlâ 4.4e-02). Sebep ``χ``nin darlığı
        değil, MPS'in bir boyutlu oluşudur (kütük H26).

        Çare, veriyi taşımak yerine **operatörü yürütmektir**. MPO,
        zincirin her yuvasında bir ``(D, 2, 2, D)`` tensörüdür ve bütün
        zincire aynı anda etki eder. Hiçbir kübit yer değiştirmez,
        dolayısıyla hiçbir dolaşıklık sürüklenmez. Maliyet ``O(N χ³ D³)``,
        yani yuva sayısında **doğrusal**.

        ``W`` sözlüğü yalnız kimliğe eşit OLMAYAN yuvaları taşır; kalan
        yuvalarda kimlik (``δ_ab δ_{w_l w_r}``) varsayılır -- yani seyrek
        bir operatör bedava taşınır.

        Uygulama iki adımdır: (1) birleştirme -- bağ ``χ·D``ye çıkar;
        (2) sıkıştırma -- sağdan sola QR, soldan sağa SVD ile ``χ``ye
        iner. Atılan ağırlık döndürülür; gizlenmez.
        """
        son = self.n if son is None else int(son)
        bas = max(0, int(bas))
        if son <= bas:
            return 0.0
        X = self.bag
        tip = self.tip
        kimlik = np.zeros((D, 2, 2, D), dtype=tip)
        for w in range(D):
            kimlik[w, 0, 0, w] = 1.0
            kimlik[w, 1, 1, w] = 1.0

        # --- 1) birleştirme: A'[k] = Σ_j W[k][wl,i,j,wr] A[k][a,j,b]
        #
        # **İki hız kusuru kaldırıldı.** (a) Her yuva ``float64``e
        # yükseltiliyordu; durum zaten ``float32`` olduğu için bu, her
        # MPO'da bütün zinciri iki katı bellekle kopyalamak demekti.
        # (b) Büzülme ``einsum(..., optimize=True)`` ile yazılmıştı ve
        # profil, vaktin beşte birinin **yol aramasına** gittiğini
        # gösterdi. Sıra sabittir; iki yığın çarpımıdır:
        #     W(p,i,j,q) → (p·i·q, j) ,  A(a,j,b) → (j, a·b)
        # çarpım (p·i·q, a·b) → yeniden dizilerek (p,a,i,q,b).
        Bn = self.B
        T: List[np.ndarray] = []
        for k in range(bas, son):
            Ak = self.A[:, k]                               # (B, X, 2, X)
            Wk = np.asarray(W.get(k, kimlik), tip)
            W2 = Wk.transpose(0, 1, 3, 2).reshape(D * 2 * D, 2)
            A2 = Ak.transpose(2, 0, 1, 3).reshape(2, Bn * X * X)
            P = (W2 @ A2).reshape(D, 2, D, Bn, X, X)        # (p,i,q,B,a,b)
            # (B, p, a, i, q, b)
            T.append(np.ascontiguousarray(P.transpose(3, 0, 4, 1, 2, 5)))
        # --- sınır vektörleri
        # Varsayılan ``e₀``dır: bağ birim cebir elemanıyla başlar ve
        # 0. bileşende kapanır. Fakat bazı operatörler bunu istemez:
        # kontrollü DAĞITIM (küllî hüküm sağda, duraklar solda) iki
        # dalı -- kaynak ``|0⟩`` ve kaynak ``|1⟩`` -- ayrı bağ
        # bileşenlerinde taşır ve solda **ikisini de** toplar. O hâlde
        # sol sınır ``(1,1)``dir. Sınırlar ayarlanabilir olmasaydı o
        # operatör hiç kurulamazdı.
        sl = np.zeros(D, tip) if sol_sinir is None else np.asarray(sol_sinir,
                                                                   tip)
        sr = np.zeros(D, tip) if sag_sinir is None else np.asarray(sag_sinir,
                                                                   tip)
        if sol_sinir is None:
            sl[0] = 1.0
        if sag_sinir is None:
            sr[0] = 1.0
        if len(T) == 1:
            # tek yuva: iki sınır da aynı tensöre kapanır
            t = np.tensordot(sl, T[0], axes=([0], [1]))     # (B,a,i,q,b)
            T[0] = np.tensordot(t, sr, axes=([3], [0]))     # (B,a,i,b)
        else:
            T[0] = np.tensordot(sl, T[0], axes=([0], [1])
                                ).reshape(Bn, X, 2, D * X)
            T[-1] = np.tensordot(T[-1], sr, axes=([4], [0])
                                 ).reshape(Bn, D * X, 2, X)
            for i in range(1, len(T) - 1):
                T[i] = T[i].reshape(Bn, D * X, 2, D * X)

        # --- 2) sıkıştırma: sağdan sola QR (kanonikleştir), sonra SVD
        atilan = 0.0
        for k in range(len(T) - 1, 0, -1):
            t = T[k]
            dl, dr = t.shape[1], t.shape[3]
            M = t.reshape(Bn, dl, 2 * dr)
            # ``M = Rᵀ Qᵀ``: sağ tensör ``Qᵀ`` olur, ``Rᵀ`` sola geçer.
            # ``einsum("aib,cb->aic", …, Rᵀ)`` yazılıp ölçüldü ve **kaldı**:
            # o, ``Rᵀ``nin ikinci indisiyle sözleşerek fiilen ``R`` ile
            # çarpar; MPO'nun normu 1'den 0.97'ye düşüyor, netice takas
            # ağıyla %25 ayrışıyordu. Doğrusu ``b`` indisini ``Rᵀ``nin
            # BİRİNCİ indisiyle sözleştirmektir.
            # Yığın hâlinde: ``B`` ekseni QR'ın kendi yığın eksenidir.
            Q, R = np.linalg.qr(M.transpose(0, 2, 1))   # (B,2dr,r),(B,r,dl)
            r = Q.shape[2]
            T[k] = Q.transpose(0, 2, 1).reshape(Bn, r, 2, dr)
            tp = T[k - 1]
            T[k - 1] = np.matmul(tp.reshape(Bn, -1, tp.shape[3]),
                                 R.transpose(0, 2, 1)
                                 ).reshape(Bn, tp.shape[1], 2, r)
        for k in range(len(T) - 1):
            t = T[k]
            dl, dr = t.shape[1], t.shape[3]
            U, sv, Vt = _kararli_svd(t.reshape(Bn, dl * 2, dr))
            r = max(1, min(X, int(self.bag_tavan), sv.shape[1]))
            top = float(np.sum(sv ** 2)) + 1e-30
            atilan += float(np.sum(sv[:, r:] ** 2)) / top
            T[k] = U[:, :, :r].reshape(Bn, dl, 2, r)
            SV = sv[:, :r, None] * Vt[:, :r, :]
            nk = T[k + 1]
            T[k + 1] = np.matmul(SV, nk.reshape(Bn, nk.shape[1], -1)
                                 ).reshape(Bn, r, 2, nk.shape[3])
        # son yuva da ``χ``ye sığmalı
        if T[-1].shape[1] > X:
            t = T[-1]
            U, sv, Vt = _kararli_svd(
                t.reshape(Bn, t.shape[1], 2 * t.shape[3]))
            r = min(X, sv.shape[1])
            top = float(np.sum(sv ** 2)) + 1e-30
            atilan += float(np.sum(sv[:, r:] ** 2)) / top
            T[-1] = np.matmul(sv[:, :r, None] * Vt[:, :r, :],
                              np.eye(Vt.shape[2], dtype=Vt.dtype)
                              ).reshape(Bn, r, 2, t.shape[3])

        # --- 3) geri yaz. Tampon bir kere tahsis edilir ve her yuvada
        # sıfırlanır; her yuva için yeni bir dizi ayırmak MPO'yu yuva
        # sayısı kadar tahsisle yüklüyordu.
        # MPO bağı ``D`` katına çıkarıp ``χ``ye indirir; üst sınır
        # artık ``χ``dir ve şüphede büyük tarafa çekilir.
        self.bag_ust[bas + 1:son] = X
        yeni = np.empty((Bn, X, 2, X), dtype=tip)
        for i, k in enumerate(range(bas, son)):
            t = T[i]
            ka, kb = min(t.shape[1], X), min(t.shape[3], X)
            yeni[...] = 0.0
            yeni[:, :ka, :, :kb] = t[:, :ka, :, :kb]
            self.A[:, k] = yeni
        return atilan

    # -----------------------------------------------------------------
    #  MERA
    # -----------------------------------------------------------------
    def mera_kur(self, kademe: Optional[int] = None,
                 teta: Optional[np.ndarray] = None,
                 alt: int = 0, ust: Optional[int] = None
                 ) -> List[MERAKademe]:
        """MERA: her kademede dolanıklık çözücü + izometri.

        Kademe ``s``de çiftler ``2^s`` uzaklıkta olmalıdır. MPS'te uzak
        çift pahalıdır; bu yüzden **fırça ofseti** kullanılır: kademe
        ``s``de önce ofset 0, sonra ofset 1 ile komşu çiftlere kapı
        uygulanır. İki ofsetli bir kademe, korelasyonun menzilini bir
        katmanda iki katına çıkarır; ``log₂N`` kademede menzil bütün
        zinciri kaplar. Bu, MERA'nın ``O(log N)`` mesafe hususiyetinin
        MPS üzerindeki fiilî karşılığıdır.

        ``teta`` verilmezse kapılar tohumdan türetilir; verilirse
        **öğrenilen** açılardır (kademe başına 12 açı: 6 çözücü + 6
        izometri).
        """
        s_azami = int(np.ceil(np.log2(self.n)))
        kademe = s_azami if kademe is None else min(kademe, s_azami)
        self.iz = []
        for s in range(kademe):
            if teta is not None:
                t = np.asarray(teta, float).reshape(-1)
                a = t[(2 * s * 6) % max(len(t) - 12, 1):][:12]
                if len(a) < 12:
                    a = np.resize(a, 12)
                U = dik_iki_kubit(a[:6])
                W = dik_iki_kubit(a[6:12])
            else:
                U = dik_iki_kubit(self.rng.normal(scale=0.6, size=6))
                W = dik_iki_kubit(self.rng.normal(scale=0.6, size=6))
            h1 = self.cift_kapi(U, ofset=0, alt=alt, ust=ust)   # çözücü
            h2 = self.cift_kapi(W, ofset=1, alt=alt, ust=ust)   # izometri
            self.iz.append(MERAKademe(kademe=s, yuva=self.n, bag=self.bag,
                                      kesme_hatasi=float(h1 + h2)))
        return self.iz

    # -----------------------------------------------------------------
    #  Ölçüm: dolaşıklık ve tek yuva yoğunlukları -- ÇÖKÜŞ YOK
    # -----------------------------------------------------------------
    def dolasiklik_entropisi(self, kesit: Optional[int] = None,
                             pencere: int = 24) -> Dict[str, float]:
        """Bir kesitteki von Neumann entropisi ``S = −Σ λ² ln λ²``.

        Kesitin solundaki ``pencere`` kadar yuva çarpılıp Schmidt
        spektrumu çıkarılır. ``S = 0`` çarpım durumu, ``S > 0``
        dolaşıklık demektir. **Ölçülen budur**; "dolaşık" lafı buradan
        gelir, iddiadan değil.
        """
        kesit = self.n // 2 if kesit is None else int(kesit)
        bas = max(0, kesit - pencere)
        # Sol bloğu soldan sağa çarp: M[(fiziksel...), bag]
        # Sol uç sınır vektörü: MPS ilk yuvanın 0. bağ indisinde başlar.
        # **Her yığın üyesi kendi ölçümünü verir** (kullanıcı hükmü).
        # ``B`` ekseni matmul'ün yığın eksenidir; QR freni de yığın
        # hâlinde çalışır.
        Bn = self.B
        M: Optional[np.ndarray] = None
        for k in range(bas, kesit):
            Ak = self.A[:, k].astype(np.float64)       # (B, X, 2, X)
            if M is None:
                M = Ak[:, 0]                           # (B, 2, X)
            else:
                M = np.matmul(M.reshape(Bn, -1, self.bag),
                              Ak.reshape(Bn, self.bag, 2 * self.bag))
                M = M.reshape(Bn, -1, self.bag)
                if M.shape[1] > 2048:
                    M = np.linalg.qr(M)[1]
        if M is None:
            return {"entropi": 0.0, "schmidt": 1.0, "kesit": float(kesit)}
        sv = np.linalg.svd(M.reshape(Bn, -1, self.bag), compute_uv=False)
        p = sv ** 2
        t = p.sum(axis=1, keepdims=True)
        p = np.where(t > 1e-300, p / np.maximum(t, 1e-300), 0.0)
        nz = p > 1e-15
        H = -np.sum(np.where(nz, p * np.log(np.where(nz, p, 1.0)), 0.0),
                    axis=1)
        return {"entropi": float(H.mean()),
                "entropi_yigin": H,
                # Schmidt **değerleri** de dönülür: kesme bir sıralamadır
                # ve o sıralamanın sınırındaki boşluk (``s[r−1] − s[r]``)
                # yüzeyin türevlenebilirliğini tayin eder (bkz.
                # `nefs/ikiz.py`). Yalnız sayısını dönmek o boşluğu
                # görünmez kılıyordu.
                "schmidt_degerleri": sv,
                "schmidt": float(nz.sum(axis=1).mean()),
                "azami_entropi": float(np.log(p.shape[1])),
                "kesit": float(kesit),
                "pencere": float(pencere)}

    def blok_dagilimi(self, bas: int, kac: int) -> np.ndarray:
        """``bas``tan itibaren ``kac`` kübitin **ortak** dağılımı -- tam.

        ===================================================================
        KÜME 1 TEVHİDİ (kütük H211): ÜÇ NÜSHA İDİ, TEK NÜSHA OLDU
        ===================================================================

        Bu büzülme evvelce **iki ayrı yerde** yazılıydı ve ikisi de
        aslında saf ``Yazmac`` cebriydi -- ne ``nefs`` semantiği, ne
        ızgara bilgisi kullanıyorlardı:

        * ``nefs/zihin_durumu.py::QYazmac.blok_dagilimi`` -- yığın eksenli,
          doğru hâli (sol çevrenin **giriş** bacağını büzer; şerhinde
          anlatılan ölçülmüş hata düzeltilmiş hâli).
        * ``nefs/ihtimal.py::IhtimalYazmaci.hucre_dagilimi`` -- yığınsız
          (``A[k]``i doğrudan indeksliyordu, yani ``B > 1``de sessizce
          yanlış eksen okurdu) ve ``einsum`` yol aramasıyla.

        İkisi de artık buraya delege eder. Nüsha tekleşince ölçülmüş
        çevre-büzülme tashihi (qyazmac'ın şerhindeki 2,4-3,2'lik hata)
        tek yerde durur; bir nüshayı düzeltip ötekini unutmak imkânsız
        hâle gelir.

        Cebir::

            ρ_blok = Tr_çevre |Ψ⟩⟨Ψ| ,   P(x) = ⟨x|ρ_blok|x⟩

        Bu bir POVM'dir (``Σ E_x = I``) ve **çöküş yoktur** (kütük H31).
        Maliyet ``O(B·N·χ³ + 4^kac·χ²)``; ``kac`` küçük tutulmalıdır.

        Dönen: ``B > 1`` ise ``(B, 2^kac)``, ``B == 1`` ise ``(2^kac,)``.
        """
        bas = int(bas)
        kac = int(kac)
        if kac < 1 or bas + kac > self.n:
            raise IndexError("blok zincirin dışına taşıyor")
        X = self.bag
        A = self.A                                    # (B, n, X, 2, X)
        Bn = self.B

        # Yığın ekseni ``B`` bütün büzülmelerde taşınır: her üye kendi
        # dağılımını verir. ``einsum`` yol araması sıcak yolda israftı;
        # çevre büzülmeleri açık ``matmul``dur.
        L = np.zeros((Bn, X, X))
        L[:, 0, 0] = 1.0
        for k in range(bas):
            Ak = A[:, k].astype(np.float64)           # (B,a,i,b)
            # L[b,d] = Σ_{a,c,i} L[a,c] A[a,i,b] A[c,i,d]
            #
            # **ÖLÇÜLEN VE DÜZELTİLEN HATA** (nefs/zihin_durumu.py'den taşındı):
            # evvelki hâl 2. adımda ``A``nın **çıkış** bağını büzüyordu;
            # doğrusu **giriş** bağıdır. Yanlış bacak büzülünce sol çevre
            # bambaşka bir dizey çıkıyor, tam dalgayla fark 2,4-3,2
            # ölçülmüştü (sağ çevre 1e-16 ile zaten doğruydu).
            t1 = np.matmul(L.transpose(0, 2, 1),
                           Ak.reshape(Bn, X, 2 * X))  # (B,c,(i,b))
            t1 = t1.reshape(Bn, X, 2, X).transpose(0, 2, 1, 3)   # (B,i,c,b)
            Ai = Ak.transpose(0, 2, 1, 3)                        # (B,i,c,d)
            L = np.matmul(t1.transpose(0, 1, 3, 2), Ai).sum(axis=1)
        R = np.zeros((Bn, X, X))
        R[:, 0, 0] = 1.0
        for k in range(self.n - 1, bas + kac - 1, -1):
            Ak = A[:, k].astype(np.float64)
            # R[a,c] = Σ_{b,d,i} R[b,d] A[a,i,b] A[c,i,d]
            t1 = np.matmul(Ak.transpose(0, 2, 1, 3).reshape(Bn, 2 * X, X),
                           R).reshape(Bn, 2, X, X)     # (B,i,a,d)
            R = np.matmul(t1.transpose(0, 1, 2, 3),
                          Ak.transpose(0, 2, 3, 1)).sum(axis=1)

        M = L
        boyut = 1
        for k in range(bas, bas + kac):
            Ak = A[:, k].astype(np.float64)
            M = np.einsum("z...ac,zaib,zcjd->z...ijbd", M, Ak, Ak,
                          optimize=False)
            boyut *= 2
        rho = np.einsum("z...bd,zbd->z...", M, R, optimize=False)
        rho = rho.reshape([Bn] + [2] * (2 * kac))
        eks = [0] + [1 + x for x in
                     (list(range(0, 2 * kac, 2))
                      + list(range(1, 2 * kac, 2)))]
        rho = np.transpose(rho, eks).reshape(Bn, boyut, boyut)
        P = np.clip(np.real(np.diagonal(rho, axis1=1, axis2=2)), 0.0, None)
        t = P.sum(axis=1, keepdims=True)
        P = np.where(t > 1e-30, P / np.maximum(t, 1e-30), 1.0 / boyut)
        return P if Bn > 1 else P[0]

    def tekil_yogunluklar(self, yuvalar: Sequence[int]) -> np.ndarray:
        """Seçili yuvaların **HAKİKÎ** ``2×2`` indirgenmiş yoğunlukları.

        ``ρ_i = Tr_çevre |Ψ⟩⟨Ψ|`` -- sol ve sağ çevreler zincirin iki
        ucundan sarılarak tam olarak kurulur::

            ρ_i[j,j'] = Σ L_i[a,c] A_i[a,j,b] A_i[c,j',d] R_{i+1}[b,d]

        **NİÇİN VAR: `yuva_yogunluklari` bir gözlenebilir DEĞİLDİ.**

        O usul ``Σ_{a,b} A[i,a,·,b] A[i,a,·,b]`` hesaplar, yani çevreyi
        **birim** kabul eder. Bu ancak MPS kanonik biçimdeyken doğrudur;
        bu yazmaç kanonik biçimde **değildir** (kapılar QR/SVD ile
        yerinde bölünüyor, merkez taşınmıyor).

        Ölçüldü ve kusur böyle bulundu. Duruma **saf bir ayar
        dönüşümü** uygulandı -- ``A_k ← A_k X``, ``A_{k+1} ← X⁻¹
        A_{k+1}`` -- ki bu fizikî durumu **hiç değiştirmez**::

            ölçüt                          ayar öncesi   ayar sonrası   değişim
            ρ₁₁ (yuva_yogunluklari)        0,5312160     0,5214878      1,8e-02
            alan_değeri("sukut")           0,5312160     0,5214878      1,8e-02
            P(sukut=1) (blok_dagilimi)     0,4268297     0,4268297      2,5e-08
            ⟨Ψ|Ψ⟩                          0,9999994     0,9999995      7,3e-08

        Yani durum aynı kalırken "sükût" %1,8 oynuyor. Dahası iki usul
        **birbirini tutmuyor**: 0,5312'ye karşı 0,4268 -- %20 fark.
        Hakikî olan ikincisidir.

        Bu, H88'in aynı cinsten tekrarıdır: orada ``beyan`` yanlış
        çevreden okuyordu, burada hüküm alanları **çevresiz** okuyordu.
        İkisinin de sebebi tektir -- çevre hesaba katılmadan okunan bir
        sayı gözlenebilir değildir.

        Maliyet ``O(N χ³)``: çevreler **bir kere** süpürülüp saklanır,
        sonra istenen bütün yuvalar onlardan okunur. Yuva başına ayrı
        süpürme yapılmaz.
        """
        idx = np.asarray(yuvalar, np.intp) % self.n
        if idx.size == 0:
            return np.zeros((self.B, 0, 2, 2))
        X, Bn = self.bag, self.B
        A = self.A
        gerek = set(int(i) for i in idx)
        enb = max(gerek)

        # --- sol çevreler: L[k] = zincirin 0..k−1 kısmının aktarımı
        L: Dict[int, np.ndarray] = {}
        cur = np.zeros((Bn, X, X))
        cur[:, 0, 0] = 1.0
        for k in range(enb + 1):
            if k in gerek:
                L[k] = cur
            Ak = A[:, k].astype(np.float64)
            t1 = np.matmul(cur.transpose(0, 2, 1),
                           Ak.reshape(Bn, X, 2 * X))
            t1 = t1.reshape(Bn, X, 2, X).transpose(0, 2, 1, 3)
            Ai = Ak.transpose(0, 2, 1, 3)
            cur = np.matmul(t1.transpose(0, 1, 3, 2), Ai).sum(axis=1)

        # --- sağ çevreler: R[k] = zincirin k+1..n−1 kısmının aktarımı
        R: Dict[int, np.ndarray] = {}
        cur = np.zeros((Bn, X, X))
        cur[:, 0, 0] = 1.0
        for k in range(self.n - 1, min(gerek) - 1, -1):
            if k in gerek:
                R[k] = cur
            Ak = A[:, k].astype(np.float64)
            t1 = np.matmul(Ak.transpose(0, 2, 1, 3).reshape(Bn, 2 * X, X),
                           cur).reshape(Bn, 2, X, X)
            cur = np.matmul(t1, Ak.transpose(0, 2, 3, 1)).sum(axis=1)

        out = np.empty((Bn, idx.size, 2, 2))
        for m, i in enumerate(idx):
            i = int(i)
            Ak = A[:, i].astype(np.float64)                  # (B,a,j,b)
            # M[j,c,b] = Σ_a L[a,c] A[a,j,b]
            M = np.einsum("zac,zajb->zjcb", L[i], Ak, optimize=False)
            rho = np.einsum("zjcb,zckd,zbd->zjk", M, Ak, R[i], optimize=False)
            iz = np.trace(rho, axis1=1, axis2=2)
            iyi = iz > 1e-300
            rho = np.where(iyi[:, None, None], rho / np.where(
                iyi, iz, 1.0)[:, None, None], np.eye(2) / 2.0)
            out[:, m] = rho
        return out

    def yuva_yogunluklari(self, yuvalar: Sequence[int]) -> np.ndarray:
        """Seçili yuvaların ``2×2`` indirgenmiş yoğunlukları -- **zayıf**.

        Sert (Von Neumann) ölçüm yapılmaz: durum çökertilmez, yalnız
        çevreye göre kısmî iz alınır. ``ρ_i = Tr_çevre |Ψ⟩⟨Ψ|``nin
        MPS'teki yerel yaklaşığı ``Σ_{a,c} A[i,a,·,c] A[i,a,·,c]``dir.
        """
        idx = np.asarray(yuvalar, np.intp) % self.n
        if idx.size == 0:
            return np.zeros((self.B, 0, 2, 2))
        X = self.bag
        # Python döngüsü + yuva başına ``einsum`` yerine tek yığın
        # çarpımı: ``B[m,i,(a,b)] @ B[m,j,(a,b)]ᵀ → R[m,i,j]``.
        # **Ölçüm float64'e yükseltilir** (kullanıcı hükmü: durum f32,
        # ölçüm f64): iz 1'den ne kadar sapıyor sorusunun cevabı
        # float32'de gürültüye gömülürdü.
        V = self.A[:, idx].transpose(0, 1, 3, 2, 4
                                     ).reshape(-1, 2, X * X).astype(np.float64)
        R = np.matmul(V, V.transpose(0, 2, 1))              # (B·m, 2, 2)
        iz = np.trace(R, axis1=1, axis2=2)
        iyi = iz > 1e-300
        out = np.empty_like(R)
        out[iyi] = R[iyi] / iz[iyi][:, None, None]
        out[~iyi] = np.eye(2) / 2.0
        return out.reshape(self.B, idx.size, 2, 2)

    def ic_carpim(self, oteki: "Yazmac") -> np.ndarray:
        """``⟨ψ_bu | ψ_öteki⟩`` -- iki MPS'in **örtüşmesi**, yığın hâlinde.

        Neye yarar: iki durumun ne kadar aynı olduğunu ölçer. Natural
        gradyanın (Fubini–Study metriğinin) tek malzemesi budur --
        "parametreyi şu kadar oynatınca DURUM ne kadar değişti"
        sorusunun cevabı bu sayıdadır.

        Maliyet ``O(B·N·χ³)``; ``2^N`` hiçbir yerde açılmaz. Aktarım
        dizeyi (transfer matrix) soldan sağa taşınır::

            E ← Σ_i A[i]ᵀ E B[i]

        Sol sınır ``e₀⊗e₀``, sağ sınır yine ``e₀``dır -- MPS'in kendi
        sınır şartıyla aynı.
        """
        if oteki.n != self.n or oteki.bag != self.bag:
            raise ValueError("iç çarpım için yazmaçlar aynı ölçüde olmalı")
        Bn = max(self.B, oteki.B)
        X = self.bag
        E = np.zeros((Bn, X, X), dtype=np.float64)
        E[:, 0, 0] = 1.0
        for k in range(self.n):
            A = np.broadcast_to(self.A[:, k], (Bn, X, 2, X)).astype(np.float64)
            C = np.broadcast_to(oteki.A[:, k], (Bn, X, 2, X)).astype(np.float64)
            T1 = np.einsum("zaic,zab->zicb", A, E, optimize=False)
            E = np.einsum("zicb,zbid->zcd", T1, C, optimize=False)
        return E[:, 0, 0]

    def sadakat(self) -> float:
        """``F = Π_kapı (tutulan / tam)`` -- kesmenin HAKİKÎ ölçüsü.

        ``[0,1]``dedir. ``1`` = hiç bilgi atılmadı; ``0`` = her şey
        atıldı. Kesme telâfisinden (H114) sonra normun kaybı ölçmediği
        için ölçüt budur ve **çarpımsaldır**, toplanabilir değil.

        **HUDUT -- ölçüldü ve gizlenmiyor.** 41 melekelik bir akışta
        **1814 kapı** vuruluyor; kapı başına ortalama ``0,986`` tutulsa
        bile çarpım ``0,986^1814 ≈ 4·10⁻¹²`` eder. Yani bu sayı, kapı
        sayısı arttıkça **zorunlu olarak** sıfıra gider ve ``1 − F``
        (kesme) ``1,0``a yapışır. Ölçüldü (χ=8/16/32/64)::

            χ= 8  log F = −26,2   kapı başına 0,9857
            χ=16  log F = −80,4   kapı başına 0,9566
            χ=32  log F = −111,5  kapı başına 0,9404
            χ=64  log F = −124,4  kapı başına 0,9337

        Bu bir **alt taşma değildir** -- ilk teşhisimde öyle demiştim ve
        yanlıştı: ``%.6f`` biçimi ``4e-12``yi ``0,000000`` gösterdiği
        için "tam sıfır" sanmıştım. Sayı hakikaten o kadar küçüktür.

        Neticesi şudur: ``sadakat()`` bir **eğitim ölçüsü olamaz**, zira
        her parametrede ``1 − F ≈ 1`` çıkar ve ayırt etmez. Kıyas için
        ``sadakat_log`` yahut ``sadakat_kapi_basina`` kullanılır.

        İkinci ve daha mühim netice: kapı başına tutulan kesir χ
        büyüdükçe **düşüyor** (0,986 → 0,934). Yani "χ'yi büyüt, daha az
        bilgi at" doğru değildir; χ büyüdükçe durum hakikaten dolaşıyor
        ve her kesmede atılan nispî ağırlık artıyor. Bu bir kusur değil
        ölçülmüş bir hakikattir ve mimarî hakkında hüküm verilirken
        hesaba katılmalıdır.
        """
        return float(np.exp(self._sadakat_log))

    def sadakat_log(self) -> float:
        """``log F`` -- alt taşmayan hâli. Daima ``≤ 0``."""
        return float(self._sadakat_log)

    def sadakat_kapi_basina(self, kapi: int) -> float:
        """**Kapı başına** tutulan kesrin geometrik ortalaması.

        ``exp(log F / kapı)`` ``[0,1]``dedir, alt taşmaz ve kapı sayısı
        değişse de kıyas edilebilir kalır: "her kapıda ortalama ne kadarı
        tutuldu" sorusunun cevabıdır. Çarpımın kendisi kapı sayısıyla
        üstel çöktüğü için kıyasa elverişli olan budur.
        """
        k = max(int(kapi), 1)
        return float(np.exp(self._sadakat_log / k))

    def norm(self) -> np.ndarray:
        """``⟨Ψ|Ψ⟩`` -- yığın üyesi başına, **tam**; ``2^N`` açılmaz."""
        return np.asarray(self.ic_carpim(self), dtype=np.float64)

    def normalize(self) -> np.ndarray:
        """Durumu ``⟨Ψ|Ψ⟩ = 1``e getir; **kaybedilen normu döndür**.

        Kesme (truncation) normu düşürür ve bu bir kayıptır; onun için
        atılan ağırlık ``iz.kesme``de ayrıca durur ve burada gizlenmez.
        Fakat durumun kendisi **durum olarak** kalmalıdır: normu 2e-10'a
        düşmüş bir yazmaçtan okunan dağılım, payı da paydası da aynı
        küçük sayı olduğu için nazarî olarak doğrudur, amma her ölçüm
        yuvarlama gürültüsüne yaklaşır. Ölçek ``n`` yuvaya eşit
        dağıtılır ki tek bir tensör şişmesin.
        """
        nrm = self.norm()
        iyi = nrm > 1e-300
        olcek = np.ones_like(nrm)
        olcek[iyi] = nrm[iyi] ** (-0.5 / self.n)
        self.A *= olcek.reshape(-1, 1, 1, 1, 1).astype(self.A.dtype)
        return nrm

    def norm_hatasi(self, ornek: int = 64) -> float:
        """``|⟨Ψ|Ψ⟩ − 1|`` -- yığındaki en kötü üye.

        **Ölçülen ve düzeltilen kusur.** Evvelki hâli ``yuva_yogunluklari``
        izinin 1'den sapmasına bakıyordu; halbuki o usul yoğunluğu
        **kendi izine bölerek** döndürür, yani izi tanım gereği 1'dir.
        Ölçüt bu yüzden boştu: ne olursa olsun ~1e-16 yazıyordu. Fiilen
        ölçüldü -- ``norm_hatasi`` 2,2e-16 derken hakikî ``⟨Ψ|Ψ⟩``
        2,05e-10 idi, yani ölçüt tam temiz kâğıt verirken durum normunun
        on mertebe altına düşmüştü. ``ornek`` artık kullanılmaz; norm
        tam hesaplanır ve imza uyum için durur.
        """
        return float(np.max(np.abs(self.norm() - 1.0)))

    # -----------------------------------------------------------------
    #  HDTF KÖPRÜSÜ -- Küme 1 tevhidinin ilk adımı (kütük H210)
    # -----------------------------------------------------------------
    @classmethod
    def hdtf_ile_kur(cls, diziler, bag_boyutu: int = 16,
                     sanal_kubit: int = 22_000_000, usul: str = "svd",
                     tip=np.float32) -> Tuple["Yazmac", Dict[str, float]]:
        """``kuantum.katlama.hiyerarsik_ikili_agac_katlama``nın çıktısını
        doğrudan bir ``Yazmac``a bağla.

        **Neden var.** Katlama şimdiye kadar ham bir ``List[ndarray]``
        döndürüyordu ve ``Yazmac``a hiç bağlanmıyordu (bkz. zabıt,
        KÜME 1 cevher/toprak cetveli, satır 9: *"Çıktı olarak Yazmac
        değil ham List[ndarray] döndürmesi"*). Burada o köprü kurulur:
        her ``(χ_sol, 2, χ_sağ)`` çekirdeği doğrudan ``Yazmac.A``nın
        kendi ``(χ, 2, χ)`` yuva biçimine (sıfırla doldurularak) yazılır
        -- ne yeniden hesap, ne SVD; **birebir aktarım**.

        Dönen ``Yazmac``nın ``norm()``u, ham çekirdek zincirinin elle
        büzülmüş ``⟨Ψ|Ψ⟩``sıyla makine hassasiyetinde örtüşür -- bu
        köprünün kendi doğrulama testidir (``kuantum/test_kuantum*.py``).

        **HUDUT.** Bu yalnız HDTF'nin **son** (katlanmış) çıktısını
        yazmaça bağlar; katlama sürecinin ara kademeleri, ``nefs/
        taksimat.py``nin 4 bölgeli adresleyicisi ve ``nefs/zihin_durumu.py``
        nin Gray-kod makam merdiveni bu köprüde YOKTUR -- onlar Küme
        1'in henüz tevhid edilmemiş parçalarıdır (bkz. docs/KUTUK.md
        H210).
        """
        cekirdekler, kesme, kademe = hiyerarsik_ikili_agac_katlama(
            diziler, bag_boyutu=bag_boyutu, sanal_kubit=sanal_kubit,
            usul=usul)
        n = len(cekirdekler)
        if n == 0:
            raise ValueError("hdtf_ile_kur: boş çekirdek zinciri")
        bag = max(int(bag_boyutu),
                  max(int(c.shape[0]) for c in cekirdekler),
                  max(int(c.shape[2]) for c in cekirdekler))
        yz = cls(max(n, 2), bag=bag, tip=tip, yigin=1)
        yz.A[:] = 0.0
        bag_ust = np.ones(len(cekirdekler) + 1, dtype=np.int64)
        for i, c in enumerate(cekirdekler):
            c = np.asarray(c, float)
            cl, iki, cr = c.shape
            if iki != 2:
                raise ValueError("hdtf_ile_kur: çekirdek fiziksel boyutu 2 değil")
            yz.A[0, i, :cl, :, :cr] = c.astype(tip)
            bag_ust[i] = cl
        bag_ust[len(cekirdekler)] = (
            cekirdekler[-1].shape[2] if cekirdekler else 1)
        yz.bag_ust[:len(bag_ust)] = bag_ust
        if n < 2:                          # Yazmac n≥2 ister; kimlikle uzat
            yz.A[0, n, 0, 0, 0] = 1.0
        return yz, {"kesme": float(kesme), "kademe": int(kademe),
                    "çekirdek_sayısı": int(n)}


# =====================================================================
#  FERMAN ADIYLA: KÜLLÎ YAZMAÇ
# =====================================================================
class KulliYazmac(Yazmac):
    """22M/88M sanal kübitlik küllî yazmaç -- ``Yazmac``ın ferman yüzü.

    Taksimat `kuantum/kubit_taksimati.py`den okunur: dört bölge **tek zincirde**
    durur, paralel iki yazmaç değildir. Eklem ölçüsü o dosyada ve
    kırmızı yanabiliyor.
    """

    def __init__(self, kubit: int = 22_000_000, bag: int = 16, **kw):
        super().__init__(int(kubit), bag=int(bag), **kw)

    def dalga_amplitudleri(self, dugumler=None):
        """Verilen düğümlerde dalga genlikleri -- FCT'nin girdisi.

        Düğüm verilmezse ilk ``bag`` kadar taban durumun genliği döner.
        Bu bir **örnekleme değildir**: aynı yazmaç daima aynı sayıları
        verir, belirlenimcilik korunur.
        """
        import numpy as _np
        n = int(len(dugumler)) if dugumler is not None else int(self.bag_ust[0] if hasattr(self, "bag_ust") else 8)
        n = max(1, min(n, 4096))
        cek = self.A[0]
        v = _np.asarray(cek, float).reshape(-1)[:n]
        if v.size < n:
            v = _np.pad(v, (0, n - v.size))
        return v


# ======================================================================
#  HDTF -- Hiyerarşik İkili Ağaç Katlaması (evvelce kuantum/katlama.py)
# ======================================================================

def _cek(v: np.ndarray, kubit: int, chi: Optional[int] = None
         ) -> Tuple[List[np.ndarray], float]:
    """Genlik vektörünü MPS çekirdeklerine ayır (ardışık SVD)."""
    v = np.asarray(v, float).ravel()
    n = int(kubit)
    if v.size != (1 << n):
        raise ValueError("genlik %d, 2^%d değil" % (v.size, n))
    cek: List[np.ndarray] = []
    M = v.reshape(1, -1)
    atilan = 0.0
    for _ in range(n - 1):
        r0 = M.shape[0]
        M = M.reshape(r0 * 2, -1)
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        etkin = int(np.sum(s > 1e-12 * max(float(s[0]), 1e-30)))
        r1 = max(1, etkin if chi is None else min(int(chi), etkin))
        atilan += float(np.sum(s[r1:] ** 2))
        cek.append(U[:, :r1].reshape(r0, 2, r1))
        M = s[:r1, None] * Vt[:r1, :]
    cek.append(M.reshape(-1, 2, 1))
    top = float(v @ v)
    return cek, math.sqrt(max(atilan, 0.0) / max(top, 1e-300))


def mps_birlestir(A: Sequence[np.ndarray], B: Sequence[np.ndarray]
                  ) -> List[np.ndarray]:
    """``|0⟩⊗A + |1⟩⊗B`` -- yeni bir mevki kübiti ekleyerek katla.

    Kesme **yoktur**; bağ olduğu gibi toplanır. Kırpma ayrı bir
    adımdır (``mps_kirp``) ve ayrı ölçülür -- birleştirmenin kendisi
    tamdır, kayıp yalnız kırpmadadır.
    """
    A = list(A)
    B = list(B)
    if len(A) != len(B):
        raise ValueError("iki blok aynı yuva sayısında olmalı: %d ≠ %d"
                         % (len(A), len(B)))
    n = len(A)
    out: List[np.ndarray] = []
    # kontrol çekirdeği: |0⟩ → A dalı (bağ 0), |1⟩ → B dalı (bağ 1)
    k0 = np.zeros((1, 2, 2))
    k0[0, 0, 0] = 1.0
    k0[0, 1, 1] = 1.0
    out.append(k0)
    for j in range(n):
        a, b = np.asarray(A[j], float), np.asarray(B[j], float)
        al, ar = a.shape[0], a.shape[2]
        bl, br = b.shape[0], b.shape[2]
        if j == n - 1:
            # son yuva: sağ bağ 1'e kapanmalı → dikey ek
            c = np.zeros((al + bl, 2, 1))
            c[:al, :, :] = a
            c[al:, :, :] = b
        else:
            c = np.zeros((al + bl, 2, ar + br))
            c[:al, :, :ar] = a
            c[al:, :, ar:] = b
        out.append(c)
    return out


def mps_kirp(cek: Sequence[np.ndarray], chi: int) -> Tuple[List[np.ndarray],
                                                           float]:
    """Kanonik süpürmeyle bağı ``χ``ye indir. Döner ``(çekirdek, hata)``.

    Sağdan sola QR (kanonikleştir), soldan sağa SVD (kırp). Bu sıra
    **Eckart-Young manasında en iyi** kırpmayı verir; zip-up'ın
    aksine burada sağdaki çevre görülmüş olur (kütük H185).
    """
    C = [np.asarray(c, float).copy() for c in cek]
    n = len(C)
    if n < 2:
        return C, 0.0
    for k in range(n - 1, 0, -1):
        t = C[k]
        dl, dr = t.shape[0], t.shape[2]
        Q, R = np.linalg.qr(t.reshape(dl, 2 * dr).T)     # (2dr,r),(r,dl)
        r = Q.shape[1]
        C[k] = Q.T.reshape(r, 2, dr)
        C[k - 1] = np.tensordot(C[k - 1], R.T, axes=([2], [0]))
    atilan = 0.0
    top = 0.0
    for k in range(n - 1):
        t = C[k]
        dl, dr = t.shape[0], t.shape[2]
        U, s, Vt = np.linalg.svd(t.reshape(dl * 2, dr), full_matrices=False)
        if top == 0.0:
            top = float(np.sum(s ** 2)) + 1e-30
        r = max(1, min(int(chi), s.size))
        atilan += float(np.sum(s[r:] ** 2))
        C[k] = U[:, :r].reshape(dl, 2, r)
        SV = s[:r, None] * Vt[:r, :]
        C[k + 1] = np.tensordot(SV, C[k + 1], axes=([1], [0]))
    return C, math.sqrt(max(atilan, 0.0) / max(top, 1e-300))


def mps_norm(cek: Sequence[np.ndarray]) -> float:
    """``‖ψ‖`` -- çevre büzülmesiyle, genliği açmadan."""
    E = np.ones((1, 1))
    for c in cek:
        c = np.asarray(c, float)
        E = np.einsum("ac,aib,cid->bd", E, c, c, optimize=True)
    return math.sqrt(max(float(E[0, 0]), 0.0))


def mps_genlik(cek: Sequence[np.ndarray]) -> np.ndarray:
    """Çekirdekleri açıp tam genlik -- **yalnız küçük ``n`` sınamasında**."""
    T = np.asarray(cek[0], float)[0]                    # (2, r)
    for c in cek[1:]:
        T = np.tensordot(T, np.asarray(c, float), axes=([-1], [0]))
    return T[..., 0].reshape(-1)


def dyadic_katla(bloklar: Sequence[Sequence[np.ndarray]], chi: int
                 ) -> Tuple[List[np.ndarray], float, int]:
    """``L`` bloğu ikili ağaçla tek bloğa katla. ``(çekirdek, hata, katlama)``.

    ``L`` ikinin kuvveti değilse **son blok tekrarlanmaz**: eksik yer
    sıfır bloğuyla değil, ağacın o dalı hiç kurulmayarak doldurulur
    (tekrarlamak veriyi çoğaltmak, sıfırlamak ise kaba sıfırlama
    olurdu -- H14 yasağı).
    """
    kat = [list(b) for b in bloklar]
    hata = 0.0
    sayac = 0
    while len(kat) > 1:
        yeni: List[List[np.ndarray]] = []
        for i in range(0, len(kat) - 1, 2):
            c = mps_birlestir(kat[i], kat[i + 1])
            c, h = mps_kirp(c, int(chi))
            hata = math.hypot(hata, h)
            sayac += 1
            yeni.append(c)
        if len(kat) % 2:
            # eşi olmayan blok bir üst seviyeye **olduğu gibi** çıkar;
            # fakat yuva sayısı bir eksik kalır, o yüzden başına
            # ``|0⟩`` mevki kübiti eklenir (kimlik katlama).
            tek = list(kat[-1])
            k0 = np.zeros((1, 2, 1))
            k0[0, 0, 0] = 1.0
            yeni.append([k0] + tek)
        kat = yeni
    return kat[0], float(hata), int(sayac)



# ══════════════════════════════════════════════════════════════════════
#  YIĞIN KATLAMA -- aynı seviyedeki bütün çiftler TEK çağrıda
# ══════════════════════════════════════════════════════════════════════
#
# **ÖLÇÜLEN VE DÜZELTİLEN DARBOĞAZ.** Yukarıdaki ``dyadic_katla`` cebren
# doğrudur (birleştirme hatası ``0,000e+00``) fakat **1100 token/sn**de
# kalıyordu -- token başına ayrı SVD'nin (826) yanında kazanç yok gibi.
# Sebep FLOP değil **Python çağrı masrafı**dır: ``L = 1024`` için 1023
# katlama × 22 yuva × 2 süpürme = ~45.000 ayrı LAPACK çağrısı, her biri
# ``8×16`` gibi minicik dizeylerde.
#
# Bir seviyedeki bütün bloklar **aynı şekildedir** (hepsi ``χ``ye
# kırpılmıştır). O hâlde yığın ekseni açılabilir: ``numpy.linalg.qr`` ve
# ``svd`` yığın hâlinde çalışır ve seviye başına çağrı sayısı blok
# adedinden **bağımsız** hâle gelir.


def _yigin_kirp(C: List[np.ndarray], chi: int, usul: str = "svd"
                ) -> Tuple[List[np.ndarray], np.ndarray]:
    """Yığın hâlinde kanonik kırpma. ``C[j]`` şekli ``(N, rl, 2, rr)``.

    Sağdan sola QR, soldan sağa SVD -- ``mps_kirp`` ile aynı cebir,
    fakat ``N`` blok tek çağrıda. Dönen hata **blok başına**dır.
    """
    n = len(C)
    N = C[0].shape[0]
    if n < 2:
        return C, np.zeros(N)
    for k in range(n - 1, 0, -1):
        t = C[k]
        _, dl, _, dr = t.shape
        M = t.reshape(N, dl, 2 * dr).transpose(0, 2, 1)     # (N,2dr,dl)
        Q, R = np.linalg.qr(M)
        r = Q.shape[2]
        C[k] = Q.transpose(0, 2, 1).reshape(N, r, 2, dr)
        p = C[k - 1]
        C[k - 1] = np.matmul(p.reshape(N, -1, p.shape[3]),
                             R.transpose(0, 2, 1)
                             ).reshape(N, p.shape[1], 2, r)
    atilan = np.zeros(N)
    top = None
    for k in range(n - 1):
        t = C[k]
        _, dl, _, dr = t.shape
        M = t.reshape(N, dl * 2, dr)
        if usul == "gram":
            # **CPU ÇARESİ (padişahın 3. emri).** LAPACK ``gesdd``
            # yerine Gram dizeyinin ``eigh``i: ``MᵀM = V Λ Vᵀ`` ve
            # ``σ = √Λ``. Gram ``dr×dr``dir, ``M`` ise ``2dl×dr``;
            # yani ayrışım daha küçük bir dizeyde koşar.
            #
            # **Bedeli peşinen ilan edilir:** kare almak koşul sayısını
            # KARELER (``κ → κ²``). Küçük ``χ``de ve iyi koşullu
            # çekirdeklerde ölçülebilir; ölçülmeden varsayılan
            # yapılmaz -- ``usul`` açıkça istenmedikçe SVD koşar.
            G = np.matmul(M.transpose(0, 2, 1), M)
            lam, V = np.linalg.eigh((G + G.transpose(0, 2, 1)) / 2.0)
            lam = lam[:, ::-1]
            V = V[:, :, ::-1]
            sv = np.sqrt(np.maximum(lam, 0.0))
            Vt = V.transpose(0, 2, 1)
            U = np.matmul(M, V) / np.maximum(sv[:, None, :], 1e-30)
        else:
            U, sv, Vt = np.linalg.svd(M, full_matrices=False)
        if top is None:
            top = np.sum(sv ** 2, axis=1) + 1e-30
        r = max(1, min(int(chi), sv.shape[1]))
        atilan += np.sum(sv[:, r:] ** 2, axis=1)
        C[k] = U[:, :, :r].reshape(N, dl, 2, r)
        SV = sv[:, :r, None] * Vt[:, :r, :]
        nk = C[k + 1]
        C[k + 1] = np.matmul(SV, nk.reshape(N, nk.shape[1], -1)
                             ).reshape(N, r, 2, nk.shape[3])
    return C, np.sqrt(np.maximum(atilan, 0.0) / top)


def dyadic_katla_yigin(bloklar: Sequence[Sequence[np.ndarray]], chi: int,
                       hedef_blok: int = 1, usul: str = "svd"
                       ) -> Tuple[List[np.ndarray], float, int]:
    """``dyadic_katla``ın yığın hâli -- **aynı cebir, tek çağrı**.

    Netice ``dyadic_katla`` ile makine hassasiyetinde aynıdır ve
    ``rapor_katlama`` bunu fiilen yüzleştirir; hız kazancı ayrıca ölçülür.

    ``hedef_blok`` **kaç blok kalınca duracağını** söyler ve bu, tek
    dizinin katlanmasından ``B`` dizinin AYNI ANDA katlanmasına geçişin
    anahtarıdır: ``B`` dizi ``B·L`` blok olarak yatırılır ve ağaç
    ``hedef_blok = B``de durur. O zaman yığın ekseni en dip seviyede
    bile ``B`` kalır ve LAPACK çağrıları küçülmez -- ölçüldüğüne göre
    darboğaz FLOP değil **çağrı adedi**dir (H189).
    """
    L = len(bloklar)
    if L == 0:
        raise ValueError("en az bir blok lâzım")
    q = len(bloklar[0])
    # (N, rl, 2, rr) yığınına al -- bütün bloklar aynı şekilde
    C = [np.stack([np.asarray(bloklar[i][j], float) for i in range(L)])
         for j in range(q)]
    hata = 0.0
    sayac = 0
    while C[0].shape[0] > int(hedef_blok):
        N = C[0].shape[0]
        tek = None
        if N % 2:
            tek = [c[-1:] for c in C]
            C = [c[:-1] for c in C]
            N -= 1
        A = [c[0::2] for c in C]
        B = [c[1::2] for c in C]
        M = N // 2
        yeni: List[np.ndarray] = []
        k0 = np.zeros((M, 1, 2, 2))
        k0[:, 0, 0, 0] = 1.0
        k0[:, 0, 1, 1] = 1.0
        yeni.append(k0)
        for j in range(len(A)):
            a, b = A[j], B[j]
            al, ar = a.shape[1], a.shape[3]
            bl, br = b.shape[1], b.shape[3]
            if j == len(A) - 1:
                c = np.zeros((M, al + bl, 2, 1))
                c[:, :al] = a
                c[:, al:] = b
            else:
                c = np.zeros((M, al + bl, 2, ar + br))
                c[:, :al, :, :ar] = a
                c[:, al:, :, ar:] = b
            yeni.append(c)
        yeni, h = _yigin_kirp(yeni, int(chi), usul=usul)
        hata = math.hypot(hata, float(np.sqrt(np.mean(h ** 2))))
        sayac += M
        if tek is not None:
            # eşi olmayan blok bir üst seviyeye kimlik katlamasıyla çıkar
            t0 = np.zeros((1, 1, 2, 1))
            t0[0, 0, 0, 0] = 1.0
            tek = [t0] + tek
            yeni = [np.concatenate([yeni[j], tek[j]], axis=0)
                    if yeni[j].shape[1:] == tek[j].shape[1:]
                    else _hizala(yeni[j], tek[j]) for j in range(len(yeni))]
        C = yeni
    if C[0].shape[0] == 1:
        return [c[0] for c in C], float(hata), int(sayac)
    return C, float(hata), int(sayac)


def _hizala(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """İki yığını ortak bağ boyutunda birleştir (sıfırla doldurarak).

    Tek kalan blok, katlanmış bloklardan farklı bağ taşıyabilir. Kaba
    sıfırlama yasağı (H14) burada **ihlâl edilmiyor**: atılan hiçbir şey
    yok, yalnız daha küçük olan tensör sıfır dolgu ile aynı kutuya
    yerleştiriliyor; genlikler aynen duruyor.
    """
    rl = max(a.shape[1], b.shape[1])
    rr = max(a.shape[3], b.shape[3])
    out = np.zeros((a.shape[0] + b.shape[0], rl, 2, rr))
    out[:a.shape[0], :a.shape[1], :, :a.shape[3]] = a
    out[a.shape[0]:, :b.shape[1], :, :b.shape[3]] = b
    return out



def hdtf_yigin(diziler: np.ndarray, sozluk: Sequence[Sequence[np.ndarray]],
               chi: int = 8, usul: str = "svd"
               ) -> Tuple[List[np.ndarray], float, int]:
    """``B`` diziyi **aynı anda** katla -- yığın ekseni hiç küçülmez.

    ``diziler`` ``(B, L)`` belirteç indisleridir. ``B·L`` blok tek
    yığında yatırılır; ağaç ``B`` blok kalınca durur, yani her dizi
    kendi içinde katlanır ve diziler birbirine **karışmaz**.

    **Niçin bu, tek dizi katlamaktan başkadır.** Tek dizide seviye
    ``ℓ``de yığın ``L/2^ℓ``ye iner ve son seviyelerde 1'e düşer;
    LAPACK o zaman ``16×16`` gibi minicik dizeylerde çağrı başına
    mikrosaniyeler yerine **çağrı masrafı** öder. ``B`` dizi birden
    katlanınca en dip seviyede bile yığın ``B``dir.

    Dönen çekirdekler ``(B, rl, 2, rr)`` şeklindedir: **yığın MPS**.
    ``main.yazmac.Yazmac``ın ``B`` ekseniyle aynı mantıktır.
    """
    A = np.atleast_2d(np.asarray(diziler, dtype=np.int64))
    B, L = A.shape
    duz = A.ravel()
    bloklar = [token_cekirdegi(sozluk, int(t)) for t in duz]
    return dyadic_katla_yigin(bloklar, int(chi), hedef_blok=int(B),
                              usul=usul)


def sozluk_qtt(E: np.ndarray, chi: int = 8
               ) -> Tuple[List[List[np.ndarray]], np.ndarray, float]:
    """Sözlük tablosunu **bir kere** QTT'ye çevir: ``(çekirdekler, norm, hata)``.

    ``E`` ``(V, D)``dir. Netice her kelime için 12 çekirdektir ve
    eğitim boyunca **değişmez**; bir token'ın çekirdeği bundan sonra
    ``token_cekirdegi`` ile ``O(1)`` çekilir -- SVD yoktur.

    Bu, ``(C)`` yükleme kaleminin **tek defalık** kısmıdır: maliyeti
    ``V`` ile doğrusaldır, ``B·L`` ile değil. Ceridenin
    ``V = 200.000`` sözlüğünde bu, ``8,4 milyon`` token yerine
    ``200 bin`` sıkıştırma demektir -- **42 kat** az.
    """
    E = np.atleast_2d(np.asarray(E, float))
    V, D = E.shape
    q = int(math.ceil(math.log2(max(D, 2))))
    tam = 1 << q
    # **YIĞIN AYRIŞTIRMA.** Evvelce ``V`` kelime için ayrı ayrı ``q``
    # SVD çağrılıyordu (``V·q`` çağrı). Bütün kelimeler aynı şekilde
    # olduğu için yığın ekseni açılır ve çağrı sayısı ``q``ya iner --
    # kelime adedinden **bağımsız**.
    P = np.zeros((V, tam))
    P[:, :min(D, tam)] = E[:, :min(D, tam)]
    nrm = np.linalg.norm(P, axis=1)
    P = P / np.maximum(nrm, 1e-300)[:, None]
    yigin: List[np.ndarray] = []
    M = P.reshape(V, 1, tam)
    atilan = np.zeros(V)
    for _ in range(q - 1):
        r0 = M.shape[1]
        M = M.reshape(V, r0 * 2, -1)
        U, sv, Vt = np.linalg.svd(M, full_matrices=False)
        r1 = max(1, min(int(chi), sv.shape[1]))
        atilan += np.sum(sv[:, r1:] ** 2, axis=1)
        yigin.append(U[:, :, :r1].reshape(V, r0, 2, r1))
        M = sv[:, :r1, None] * Vt[:, :r1, :]
    yigin.append(M.reshape(V, -1, 2, 1))
    cek = [[yigin[j][i] for j in range(q)] for i in range(V)]
    hata = float(np.max(np.sqrt(np.maximum(atilan, 0.0))))
    return cek, nrm, hata


def token_cekirdegi(sozluk: Sequence[Sequence[np.ndarray]], t: int
                    ) -> List[np.ndarray]:
    """``O(1)`` çekiş -- SVD yok, kopya yok (çekirdekler paylaşılır)."""
    return list(sozluk[int(t)])


def hdtf_kur(dizi: Sequence[int], sozluk: Sequence[Sequence[np.ndarray]],
             chi: int = 8) -> Tuple[List[np.ndarray], float, int]:
    """Bir belirteç dizisini tek QTT durumuna katla.

    ``dizi`` belirteç indisleridir; her biri sözlükten ``O(1)`` çekilir
    ve ikili ağaçla katlanır. Netice ``log₂(L) + 12`` yuvalı bir
    MPS'tir.
    """
    bloklar = [token_cekirdegi(sozluk, t) for t in dizi]
    return dyadic_katla_yigin(bloklar, int(chi))


def hdtf_olcusu(V: int = 512, L: int = 256, D: int = 256,
                chi: int = 8, tohum: int = 0) -> Dict[str, object]:
    """HDTF'yi **fiilen** koştur: süre, hata, bellek ve token hızı.

    Sözlük gerçekçi kurulur (Zipf benzeri, korelasyonlu), zira rastgele
    bir sözlük hiçbir ``χ``ye sığmaz ve o, HDTF'nin değil verinin
    hükmüdür (H188).
    """
    rng = np.random.default_rng(int(tohum))
    taban = np.cos(np.outer(np.arange(D), np.arange(8)) * 0.07)
    kat = rng.normal(size=(V, 8))
    E = kat @ taban.T * (1.0 / np.arange(1, D + 1))[None, :]
    E = E + 0.02 * rng.normal(size=(V, D))

    t0 = time.perf_counter()
    soz, nrm, h_soz = sozluk_qtt(E, chi=int(chi))
    t_soz = time.perf_counter() - t0

    dizi = rng.integers(0, V, size=int(L))
    t0 = time.perf_counter()
    cek, h_kat, n_kat = hdtf_kur(dizi, soz, chi=int(chi))
    t_kat = time.perf_counter() - t0

    eleman = int(sum(c.size for c in cek))
    ham = int(L) * int(D)
    return {"V": V, "L": L, "D": D, "χ": chi,
            "sözlük_sn": t_soz, "sözlük_hatası": h_soz,
            "katlama_sn": t_kat, "katlama_hatası": h_kat,
            "katlama_adedi": n_kat,
            "yuva": len(cek), "eleman": eleman,
            "ham_eleman": ham,
            "sıkıştırma": ham / max(eleman, 1),
            "token_sn": float(L) / max(t_kat, 1e-12),
            "norm": mps_norm(cek)}


def rapor_katlama() -> str:                                     # pragma: no cover
    s = ["HDTF -- Hiyerarşik İkili Ağaç Katlaması (belirlenimci QTT inşası)",
         ""]
    s.append("  1) Katlama CEBRİ tam mı? (küçük ölçekte yoğunla kıyas)")
    rng = np.random.default_rng(0)
    q = 4
    A, _ = _cek(rng.normal(size=1 << q), q)
    B, _ = _cek(rng.normal(size=1 << q), q)
    C = mps_birlestir(A, B)
    bek = np.concatenate([mps_genlik(A), mps_genlik(B)])
    s.append("     |0⟩⊗A + |1⟩⊗B  hatası: %.3e  (kesme YOK)"
             % float(np.linalg.norm(mps_genlik(C) - bek)))
    Ck, hk = mps_kirp(C, chi=4)
    s.append("     χ=4'e kırpınca hata: %.3e   norm %.6f"
             % (float(np.linalg.norm(mps_genlik(Ck) - bek)
                      / np.linalg.norm(bek)), mps_norm(Ck)))

    s.append("")
    s.append("  2) HDTF'nin fiilî hızı ve sıkıştırması")
    s.append("     %5s %5s %5s | %9s %9s | %11s %10s %8s"
             % ("V", "L", "χ", "sözlük sn", "katlama", "token/sn",
                "sıkıştırma", "hata"))
    for V, L, chi in ((512, 256, 8), (512, 1024, 8), (2048, 1024, 8),
                      (2048, 1024, 16)):
        r = hdtf_olcusu(V=V, L=L, D=256, chi=chi)
        s.append("     %5d %5d %5d | %9.3f %9.3f | %11.0f %9.1fx %8.4f"
                 % (V, L, chi, r["sözlük_sn"], r["katlama_sn"],
                    r["token_sn"], r["sıkıştırma"], r["katlama_hatası"]))
    s.append("")
    s.append("  Sözlük BİR KERE sıkıştırılır (V ile doğrusal); katlama")
    s.append("  her dizide koşar (L ile doğrusal) ve içinde SVD yalnız")
    s.append("  yerel, χ boyutunda olanlardır -- 2^n genlik hiç açılmaz.")
    return "\n".join(s)




# =====================================================================
#  FERMAN ADIYLA GİRİŞ: HİYERARŞİK İKİLİ AĞAÇ KATLAMASI (HDTF)
# =====================================================================
def hiyerarsik_ikili_agac_katlama(diziler, bag_boyutu: int = 16,
                                  sanal_kubit: int = 22_000_000,
                                  usul: str = "svd"):
    """Veri parçalarını **tek** QTT süperpozisyonuna katla.

    ``|yeni⟩ = |0⟩⊗A + |1⟩⊗B`` ikili ağacı; her kademede MPS toplamı
    alınıp ``χ`` bağına kırpılır. Dönen: ``(çekirdekler, kesme, kademe)``.

    **Ölçülmüş had (kütük H189/H190).** Sadakat ``L`` büyüdükçe sabit
    ``χ``de düşer; ``χ ≈ 2√L`` kaidesi ölçülmüştür. ``χ = 16``,
    ``L = 4096`` için **yetmez** ve bu gizlenmiyor: dönen ``kesme``
    değeri o kaybın kendisidir.
    """
    import numpy as _np

    # **ORTAK UZUNLUK VE SABİT BAĞ ŞARTTIR.** Yığın katlaması bütün
    # blokların aynı çekirdek şeklinde olmasını ister; ARC ızgaraları
    # ayrı ebatlarda geldiği için ilk hâl ``all input arrays must have
    # the same shape`` diye düştü. Kısaltmak veri kaybettirirdi; onun
    # yerine hepsi **en uzun** parçanın iki-kuvvetine sıfırla doldurulur
    # ve her kademede bağ ``χ``ye sıfırla tamamlanır. Doldurma kayıpsız,
    # kırpma kayıplıdır -- kayıplı olanı seçmek ölçüyü sessizce bozardı.
    ham = [_np.asarray(d, dtype=float).reshape(-1) for d in diziler]
    ham = [v for v in ham if v.size]
    if not ham:
        raise ValueError("katlanacak veri yok")
    enb = max(int(v.size) for v in ham)
    n = int(2 ** int(_np.ceil(_np.log2(max(enb, 2)))))
    k = int(_np.log2(n))
    r = int(bag_boyutu)

    bloklar = []
    for v in ham:
        u = _np.zeros(n)
        u[:v.size] = v
        nrm = _np.linalg.norm(u)
        if nrm > 0:
            u = u / nrm
        cek = []
        kalan = u.reshape(1, -1)
        for _s in range(k):
            kalan = kalan.reshape(kalan.shape[0] * 2, -1)
            U, S, Vt = _np.linalg.svd(kalan, full_matrices=False)
            rr = min(r, int(S.size))
            cekirdek = _np.zeros((kalan.shape[0] // 2, 2, r))
            blok = U[:, :rr].reshape(-1, 2, rr)
            # sol bağ da ``r``ye tamamlanır ki bütün kademeler aynı olsun
            sol = min(blok.shape[0], r)
            cekirdek[:sol, :, :rr] = blok[:sol]
            cek.append(cekirdek[:r] if cekirdek.shape[0] > r else cekirdek)
            kalan = (_np.diag(S[:rr]) @ Vt[:rr])
        son = cek[-1]
        art = _np.zeros(son.shape[2])
        m = min(son.shape[2], kalan.size)
        art[:m] = kalan.reshape(-1)[:m]
        cek[-1] = son * art.reshape(1, 1, -1)
        # Çekirdekleri tek düze şekle oturt. **MPS sınır şartı**: ilk
        # çekirdeğin sol bağı ve son çekirdeğin sağ bağı ``1``dir; onu
        # da ``r`` yapmak zinciri açık uçlu bırakır ve yığın katlaması
        # ``(15,16,2,16) → (15,16,2,1)`` diye düşer.
        duz = []
        for t_i, c in enumerate(cek):
            sol = 1 if t_i == 0 else r
            sag = 1 if t_i == len(cek) - 1 else r
            t = _np.zeros((sol, 2, sag))
            a, b = min(c.shape[0], sol), min(c.shape[2], sag)
            t[:a, :, :b] = c[:a, :, :b]
            duz.append(t)
        bloklar.append(duz)
    if not bloklar:
        raise ValueError("katlanacak veri yok")
    if len(bloklar) == 1:
        return bloklar[0], 0.0, 1
    return dyadic_katla_yigin(bloklar, int(bag_boyutu), usul=usul)

# ======================================================================
#  SANAL BAĞIN QTT FAKTÖRİZASYONU (evvelce kuantum/ic_bag.py)
# ======================================================================

def acik_parametre(chi: int, fiziksel: int = 2) -> int:
    """Açık bir MPS çekirdeğinin sayı adedi: ``χ·d·χ``."""
    return int(chi) * int(fiziksel) * int(chi)


def ic_bag_parametresi(chi: int, r: int = 2, fiziksel: int = 2) -> int:
    """Mikro-zincirin sayı adedi: ``2k·(r·2·r) + r·d·r``.

    ``k = log₂χ``; sol bağın ``k`` mikro-çekirdeği, sağ bağın ``k``
    mikro-çekirdeği ve ortada fizikî indisi taşıyan bir çekirdek.
    """
    k = int(math.ceil(math.log2(max(int(chi), 2))))
    return 2 * k * (int(r) * 2 * int(r)) + int(r) * int(fiziksel) * int(r)


@dataclass
class IcBag:
    """Bir MPS çekirdeğinin mikro-QTT hâli.

    ``sol[j]``  : ``(r, 2, r)`` -- sol bağın ``j``inci biti
    ``orta``    : ``(r, d, r)`` -- fizikî indis
    ``sag[j]``  : ``(r, 2, r)`` -- sağ bağın ``j``inci biti

    Çekirdek şöyle okunur::

        G(α, σ, β) = [Π_j sol_j(μ_j)] · orta(σ) · [Π_j sag_j(ν_j)]

    ``α``nın ikili açılımı ``μ``, ``β``nınki ``ν``dir; çarpımın izi
    alınır (kapalı zincir) ki netice skaler olsun.
    """
    sol: List[np.ndarray]
    orta: np.ndarray
    sag: List[np.ndarray]
    chi: int
    r: int

    @property
    def parametre(self) -> int:
        return int(sum(x.size for x in self.sol) + self.orta.size
                   + sum(x.size for x in self.sag))


def ic_bag_kur(chi: int, r: int = 2, fiziksel: int = 2,
               tohum: int = 0) -> IcBag:
    """Belirlenimci bir mikro-zincir kur (deterministik tohum, zar yok)."""
    k = int(math.ceil(math.log2(max(int(chi), 2))))
    rng = np.random.default_rng(int(tohum))
    sol = [rng.normal(size=(r, 2, r)) / math.sqrt(r) for _ in range(k)]
    orta = rng.normal(size=(r, int(fiziksel), r)) / math.sqrt(r)
    sag = [rng.normal(size=(r, 2, r)) / math.sqrt(r) for _ in range(k)]
    return IcBag(sol=sol, orta=orta, sag=sag, chi=int(chi), r=int(r))


def ic_bag_ac(g: IcBag) -> np.ndarray:
    """Mikro-zinciri açık ``(χ, d, χ)`` çekirdeğe aç -- **yalnız ölçüm**.

    ``χ`` büyükken bu bellek yer; kıyas ölçümünde küçük ``χ`` ile
    çağrılır. Açmadan iddiayı denetlemenin yolu yoktur.
    """
    k = len(g.sol)
    chi = 1 << k
    d = g.orta.shape[1]
    # sol bağın bütün ikili açılımları için (r, r) çarpımı
    SOL = np.zeros((chi, g.r, g.r))
    for a in range(chi):
        M = np.eye(g.r)
        for j in range(k):
            bit = (a >> (k - 1 - j)) & 1
            M = M @ g.sol[j][:, bit, :]
        SOL[a] = M
    SAG = np.zeros((chi, g.r, g.r))
    for b in range(chi):
        M = np.eye(g.r)
        for j in range(k):
            bit = (b >> (k - 1 - j)) & 1
            M = M @ g.sag[j][:, bit, :]
        SAG[b] = M
    # G(a,σ,b) = tr( SOL[a] · orta(σ) · SAG[b] )
    out = np.einsum("apq,qsu,buv,vp->asb", SOL, g.orta, SAG,
                    np.eye(g.r), optimize=True)
    return out[:, :d, :][:, :, :chi] if chi <= g.chi else out



# ══════════════════════════════════════════════════════════════════════
#  TASHİH: KAPALI FORM AYRIŞTIRMA (divanın 10-H193-TASHİH hükmü)
# ══════════════════════════════════════════════════════════════════════
#
# Divanın tenkidi iki noktada **yerindedir** ve kabul edilmiştir:
#
#   1. *"Rastgele çekirdek safsatası."* Tamamen rastgele bir dizeyi
#      hiçbir tensör ağı sıkıştıramaz; bu bir teoremdir. Yukarıdaki ilk
#      ölçümüm rastgele çekirdekle yapıldı ve o, mikro-zinciri kendi
#      sahasında değil yabancı sahada denemekti.
#   2. *"Kaba sonlu-fark inişi."* Mikro-çekirdekleri rastgele
#      ilklendirip sonlu farkla aramak, çorak platoya çarpar. Doğrusu
#      **kapalı form**dur: çekirdeği bit kiplerine açıp ardışık SVD
#      (TT-SVD) uygulamak. Her bağda Eckart-Young manasında en iyidir
#      ve hiçbir zar atılmaz.
#
# Aşağısı o iki tashihin icrasıdır.


def qtt_cekirdek_ayristir(G: np.ndarray, r: int = 8, sira: str = "serpistir"
                          ) -> Tuple[List[np.ndarray], float, List[int]]:
    """``(χ,d,χ)`` çekirdeği bit kiplerine açıp TT-SVD ile ayır.

    ``α`` ve ``β`` indisleri ``k = log₂χ`` bite açılır. **Sıra
    hayatîdir ve ilk denemem yanlıştı.**

    * ``sira="ayri"``      : ``μ₁…μ_k, σ, ν₁…ν_k``. Benim ilk seçimim.
    * ``sira="serpistir"`` : ``(μ₁ν₁), (μ₂ν₂), …, (μ_kν_k), σ``. Oseledets'in
      **QTT-matris** formatı: aynı ölçek mertebesindeki satır ve sütun
      bitleri **aynı yuvada** birleştirilir (fizikî boyut 4 olur).

    Fark cebridir: bir öteleme yahut bantlı dizeyde ``i`` ile ``j``
    arasındaki bağıntı **aynı ölçekte**dir (``i−j`` küçüktür). Ayrı
    sırada o bağıntı zincirin bir ucundan öbür ucuna gitmek zorunda
    kalır ve bağ patlar; serpiştirilmiş sırada aynı yuvada kapanır.
    Varsayılan bu yüzden ``serpistir``dir.

    Döner ``(çekirdekler, bağıl hata, bağ profili)``. Kesme
    **belirlenimcidir** (LAPACK SVD, tohum yok) ve her bağda en iyidir.
    """
    G = np.asarray(G, float)
    chi, d, chi2 = G.shape
    if chi != chi2:
        raise ValueError("çekirdek (χ,d,χ) olmalı")
    k = int(math.ceil(math.log2(max(chi, 2))))
    if (1 << k) != chi:
        raise ValueError("χ ikinin kuvveti olmalı: %d" % chi)
    if str(sira) == "serpistir":
        # (μ₁…μ_k, σ, ν₁…ν_k) → (μ₁,ν₁), (μ₂,ν₂), …, (μ_k,ν_k), σ
        T0 = G.reshape([2] * k + [d] + [2] * k)
        eks = []
        for j in range(k):
            eks += [j, k + 1 + j]
        eks += [k]
        T = np.transpose(T0, eks).reshape([4] * k + [d])
        kip = [4] * k + [d]
    else:
        T = G.reshape([2] * k + [d] + [2] * k)
        kip = [2] * k + [d] + [2] * k
    M = T.reshape(1, -1)
    cek: List[np.ndarray] = []
    bag: List[int] = []
    atilan = 0.0
    top = float(np.sum(G * G)) + 1e-300
    for i in range(len(kip) - 1):
        r0 = M.shape[0]
        M = M.reshape(r0 * kip[i], -1)
        U, sv, Vt = np.linalg.svd(M, full_matrices=False)
        etkin = int(np.sum(sv > 1e-13 * max(float(sv[0]), 1e-30)))
        r1 = max(1, min(int(r), int(sv.size), etkin))
        atilan += float(np.sum(sv[r1:] ** 2))
        cek.append(U[:, :r1].reshape(r0, kip[i], r1))
        M = sv[:r1, None] * Vt[:r1, :]
        bag.append(r1)
    cek.append(M.reshape(-1, kip[-1], 1))
    return cek, math.sqrt(max(atilan, 0.0) / top), bag


def qtt_cekirdek_ac(cek: Sequence[np.ndarray], chi: int, d: int,
                    sira: str = "serpistir") -> np.ndarray:
    """``qtt_cekirdek_ayristir``ın tersi -- açık ``(χ,d,χ)`` çekirdek."""
    T = np.asarray(cek[0], float)[0]
    for c in cek[1:]:
        T = np.tensordot(T, np.asarray(c, float), axes=([-1], [0]))
    T = T[..., 0]
    k = int(math.ceil(math.log2(max(chi, 2))))
    if str(sira) == "serpistir":
        T = T.reshape([2, 2] * k + [d])
        eks = [2 * j for j in range(k)] + [2 * k] \
            + [2 * j + 1 for j in range(k)]
        return np.transpose(T, eks).reshape(chi, d, chi)
    return T.reshape(chi, d, chi)


def qtt_parametre(cek: Sequence[np.ndarray]) -> int:
    return int(sum(np.asarray(c).size for c in cek))


def kapali_form_kiyasi(G: np.ndarray, rler: Sequence[int] = (2, 4, 8, 16),
                       sira: str = "serpistir") -> Dict[str, object]:
    """**Aynı bütçede** mikro-QTT mi, düz kırpma mı? -- kapalı formla.

    Her ``r`` için mikro-QTT'nin hatası ve parametresi ölçülür; sonra
    **aynı parametreye sığan** düz bağ ``χ'`` bulunup onun hatası
    ölçülür. İkisi yan yana yazılır (H47) ve hüküm oradan çıkar.
    """
    G = np.asarray(G, float)
    chi, d, _ = G.shape
    nrm = math.sqrt(float(np.sum(G * G))) + 1e-300
    out: List[Dict[str, object]] = []
    M = G.reshape(chi * d, chi)
    U, sv, Vt = np.linalg.svd(M, full_matrices=False)
    for r in rler:
        cek, hata, bag = qtt_cekirdek_ayristir(G, r=int(r), sira=sira)
        par = qtt_parametre(cek)
        duz = max(1, min(chi, int(math.floor(math.sqrt(par / max(d, 1))))))
        K = (U[:, :duz] * sv[:duz]) @ Vt[:duz, :]
        hata_duz = float(np.linalg.norm(K - M) / nrm)
        out.append({"r": int(r), "parametre": par, "hata_qtt": float(hata),
                    "azamî_bağ": int(max(bag)),
                    "düz_χ": int(duz), "hata_düz": hata_duz,
                    "qtt_daha_iyi": bool(hata < hata_duz - 1e-12)})
    return {"χ": int(chi), "d": int(d),
            "açık_parametre": acik_parametre(chi, d), "cetvel": out}


def etkin_chi_kiyasi(hedef: np.ndarray, r: Sequence[int] = (2, 4, 8),
                     tohum: int = 0, tur: int = 400
                     ) -> Dict[str, object]:
    """**Aynı parametre bütçesinde** mikro-zincir mi, düz küçük χ mı?

    ``hedef`` gerçek bir ``(χ, d, χ)`` çekirdektir. İki yol kıyaslanır:

    1. **Mikro-zincir**: ``r`` mikro-bağıyla ``χ``yi taşıdığı iddia
       edilen yapı; parametresi ``ic_bag_parametresi(χ, r)``.
    2. **Düz kırpma**: aynı parametre bütçesine sığan en büyük düz
       bağ ``χ'``; yani ``χ'·d·χ' ≤ bütçe``.

    İkisinin de ``hedef``e bağıl hatası ölçülür. Mikro-zincir düz
    kırpmadan **daha iyi değilse**, "χ = 2²⁰" iddiası boştur: aynı
    hafızayla düz bir çekirdek daha çok şey taşıyor demektir.

    Mikro-zincirin uydurulması belirlenimci en küçük kareler
    süpürmesiyle yapılır (her mikro-çekirdek sırayla, ötekiler sabit).
    """
    H = np.asarray(hedef, float)
    chi, d, chi2 = H.shape
    if chi != chi2:
        raise ValueError("çekirdek (χ,d,χ) olmalı")
    nrm = float(np.linalg.norm(H)) + 1e-30
    out: List[Dict[str, float]] = []
    for rr in r:
        but = ic_bag_parametresi(chi, rr, d)
        g = ic_bag_kur(chi, rr, d, tohum=tohum)
        # -- belirlenimci alternatif en küçük kareler (ALS) süpürmesi
        for _ in range(int(tur)):
            A = ic_bag_ac(g)
            olc = float(np.sum(A * H) / max(float(np.sum(A * A)), 1e-30))
            g = IcBag(sol=[s * 1.0 for s in g.sol],
                      orta=g.orta * olc, sag=g.sag, chi=chi, r=rr)
            # her mikro-çekirdeği sonlu farkla iyileştir (deterministik)
            iyi = False
            for lst, ad in ((g.sol, "sol"), (g.sag, "sag")):
                for j in range(len(lst)):
                    for idx in np.ndindex(lst[j].shape):
                        e = 1e-3
                        eski = lst[j][idx]
                        t0 = float(np.linalg.norm(ic_bag_ac(g) - H))
                        lst[j][idx] = eski + e
                        t1 = float(np.linalg.norm(ic_bag_ac(g) - H))
                        lst[j][idx] = eski - e
                        t2 = float(np.linalg.norm(ic_bag_ac(g) - H))
                        lst[j][idx] = eski
                        gr = (t1 - t2) / (2 * e)
                        if abs(gr) > 1e-12:
                            lst[j][idx] = eski - 0.5 * gr
                            if float(np.linalg.norm(ic_bag_ac(g) - H)) < t0:
                                iyi = True
                            else:
                                lst[j][idx] = eski
            if not iyi:
                break
        hata_mikro = float(np.linalg.norm(ic_bag_ac(g) - H) / nrm)
        # -- aynı bütçeye sığan düz bağ
        duz = max(1, int(math.floor(math.sqrt(but / max(d, 1)))))
        duz = min(duz, chi)
        M = H.reshape(chi * d, chi)
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        K = (U[:, :duz] * s[:duz]) @ Vt[:duz, :]
        hata_duz = float(np.linalg.norm(K - M) / nrm)
        out.append({"r": int(rr), "bütçe": int(but),
                    "hata_mikro": hata_mikro,
                    "düz_χ": int(duz), "hata_düz": hata_duz,
                    "mikro_daha_iyi": bool(hata_mikro < hata_duz)})
    return {"χ": int(chi), "d": int(d),
            "açık_parametre": acik_parametre(chi, d), "cetvel": out}


def vram_cetveli(N: int = 88_000_000, r: int = 2,
                 chiler: Sequence[int] = (64, 1024, 65536, 1048576),
                 bayt: int = 2) -> List[Dict[str, object]]:
    """Divanın VRAM cetvelini **yeniden hesapla** -- ve serbestlik de yaz.

    Divan yalnız hafızayı yazıyor. Hafızanın yanına **serbestlik
    derecesi** konmadan cetvel yanıltır: 320 sayı ile 2,2 trilyon
    sayının aynı işi göreceği iddiası oradan doğuyor.
    """
    out: List[Dict[str, object]] = []
    for chi in chiler:
        k = int(math.ceil(math.log2(max(chi, 2))))
        mikro = ic_bag_parametresi(chi, r)
        acik = acik_parametre(chi)
        out.append({
            "χ": int(chi), "k": k,
            "açık_GB": acik * N * bayt / 1e9,
            "mikro_GB": mikro * N * bayt / 1e9,
            "açık_sayı_çekirdek": acik,
            "mikro_sayı_çekirdek": mikro,
            "serbestlik_nispeti": acik / max(mikro, 1),
        })
    return out


def rapor_ic_bag() -> str:                                     # pragma: no cover
    s = ["SANAL BAĞIN KUANTİKLEŞTİRİLMESİ -- iddia ve ölçü", ""]
    s.append("  1) SAYIM: hafıza düşüyor, fakat SERBESTLİK de düşüyor")
    s.append("     %10s %4s | %14s %14s | %s"
             % ("χ", "k", "açık sayı", "mikro sayı", "serbestlik nispeti"))
    for r in vram_cetveli():
        s.append("     %10d %4d | %14d %14d | %.3e kat"
                 % (r["χ"], r["k"], r["açık_sayı_çekirdek"],
                    r["mikro_sayı_çekirdek"], r["serbestlik_nispeti"]))
    s.append("     → 'χ = 2²⁰' demek, 2,2 trilyon sayı yerine 320 sayı")
    s.append("       koymaktır. Hafıza kazancı hakikî, fakat o iki yapı")
    s.append("       AYNI ŞEYİ TAŞIMAZ. Cetvele serbestlik sütunu")
    s.append("       konmadan bu görünmüyordu.")

    s.append("")
    s.append("  2) ASIL SUAL: aynı bütçede mikro-zincir mi, düz χ mi?")
    rng = np.random.default_rng(0)
    for chi, ad in ((8, "rastgele çekirdek"), (8, "yapılı (düşük rütbe)")):
        if ad.startswith("rast"):
            H = rng.normal(size=(chi, 2, chi))
        else:
            u = rng.normal(size=(chi, 2)); v = rng.normal(size=(chi, 2))
            H = np.einsum("as,bs->asb", u, v)
        r = etkin_chi_kiyasi(H, r=(2, 4))
        s.append("     %s (χ=%d):" % (ad, chi))
        for c in r["cetvel"]:
            s.append("       r=%d bütçe=%3d | mikro hata %.4f | düz χ'=%d "
                     "hata %.4f | mikro daha iyi: %s"
                     % (c["r"], c["bütçe"], c["hata_mikro"], c["düz_χ"],
                        c["hata_düz"], c["mikro_daha_iyi"]))
    return "\n".join(s)

# ======================================================================
#  POLİNOMİAL TENSÖR HALKASI -- YÜZEY temsili (evvelce kuantum/ptr.py)
# ======================================================================

class TensorHalka:
    """``ψ(x) = Tr(Π_k G_k[:, x_k, :])`` -- ayrık dizinli halka."""

    def __init__(self, n: int, d: int = 2, chi: int = 4,
                 tohum: int = 0, halka: bool = True) -> None:
        self.n, self.d, self.chi, self.halka = int(n), int(d), int(chi), halka
        rng = np.random.default_rng(tohum)
        self.G = [rng.normal(scale=1.0 / np.sqrt(chi),
                             size=(chi, d, chi))
                  for _ in range(n)]
        if not halka:
            # açık MPS: uçlar 1 boyutlu -- mukayese için
            self.G[0] = self.G[0][:1]
            self.G[-1] = self.G[-1][:, :, :1]

    # -----------------------------------------------------------------
    def __len__(self) -> int:
        return sum(g.size for g in self.G)

    def genlik(self, X: np.ndarray) -> np.ndarray:
        """``(B, n)`` dizinler → ``(B,)`` değer. Yığın hâlinde büzülür."""
        X = np.atleast_2d(np.asarray(X, int))
        B = len(X)
        M = self.G[0][:, X[:, 0], :]                 # (χ₀, B, χ)
        M = np.moveaxis(M, 1, 0)                     # (B, χ₀, χ)
        for k in range(1, self.n):
            Nk = np.moveaxis(self.G[k][:, X[:, k], :], 1, 0)
            M = np.einsum("bij,bjk->bik", M, Nk, optimize=True)
        return (np.einsum("bii->b", M) if self.halka
                else M[:, 0, 0])

    def durum(self) -> Dict[str, float]:
        return {"n": float(self.n), "d": float(self.d), "χ": float(self.chi),
                "halka": float(self.halka), "parametre": float(len(self)),
                "açık_tablo_olsaydı_log2": float(self.n
                                                 * np.log2(self.d))}


# =====================================================================
class PolinomHalka:
    """Sürekli parametrede halka: ``G_k(t) = Σ_p C[k,p] T_p(t)``.

    Ayrıklaştırma yoktur; ``t`` sürekli kalır. Bu, nefsin açıları gibi
    sürekli parametrelerde ``2^{bit}`` kaybını tamamen ortadan kaldırır.
    """

    def __init__(self, n: int, chi: int = 4, derece: int = 6,
                 tohum: int = 0, halka: bool = True) -> None:
        self.n, self.chi, self.derece = int(n), int(chi), int(derece)
        self.halka = halka
        rng = np.random.default_rng(tohum)
        self.C = rng.normal(scale=1.0 / np.sqrt(chi * (derece + 1)),
                            size=(n, derece + 1, chi, chi))

    def __len__(self) -> int:
        return int(self.C.size)

    def cekirdek(self, T: np.ndarray) -> np.ndarray:
        """``T``: ``(B, n, P+1)`` Chebyshev tabanı → ``(B, n, χ, χ)``."""
        return np.einsum("bnp,npij->bnij", T, self.C, optimize=True)

    def deger(self, t: np.ndarray) -> np.ndarray:
        """``t``: ``(B, n)`` ∈ ``[-1,1]`` → ``(B,)``."""
        t = np.atleast_2d(np.asarray(t, float))
        K = self.cekirdek(chebyshev(t, self.derece))
        M = K[:, 0]
        for k in range(1, self.n):
            M = np.einsum("bij,bjk->bik", M, K[:, k], optimize=True)
        return (np.einsum("bii->b", M) if self.halka else M[:, 0, 0])

    def oturt(self, t: np.ndarray, y: np.ndarray, tur: int = 30,
              lam: float = 1e-6) -> List[float]:
        """**Değişmeli en küçük kareler** (ALS) -- gradyan inişi yok.

        Halka, her bir ``G_k``da **doğrusaldır** (ötekiler sabitken).
        Onun için her çekirdek kapalı formda çözülür ve sırayla dolaşılır.
        Bu, kütük H3'ün "uydurma kapalı formdur" şartını halkada da
        karşılar; Adam/SGD hiç girmez.
        """
        t = np.atleast_2d(np.asarray(t, float))
        y = np.asarray(y, float)
        Tb = chebyshev(t, self.derece)                   # (B, n, P+1)
        seyir: List[float] = []
        for _ in range(tur):
            K = self.cekirdek(Tb)                        # (B, n, χ, χ)
            for k in range(self.n):
                # sol = Π_{j<k}, sag = Π_{j>k}
                sol = None
                for j in range(k):
                    sol = K[:, j] if sol is None else np.einsum(
                        "bij,bjk->bik", sol, K[:, j], optimize=True)
                sag = None
                for j in range(k + 1, self.n):
                    sag = K[:, j] if sag is None else np.einsum(
                        "bij,bjk->bik", sag, K[:, j], optimize=True)
                B = len(t)
                I = np.broadcast_to(np.eye(self.chi), (B, self.chi, self.chi))
                sol = I if sol is None else sol
                sag = I if sag is None else sag
                # ψ = Σ_{ij} G_k[i,j] · E[j,i] olacak şekilde çevre ``E``:
                #   halka  : ψ = Tr(sol·G·sag)      → E = sag·sol
                #   zincir : ψ = (sol·G·sag)[0,0]   → E[j,i] = sol[0,i]·sag[j,0]
                # İlk hâlde ikisi için de ``sag·sol`` yazmıştım; zincir kolu
                # bu yüzden yanlış çözülüyor ve mukayese geçersiz oluyordu
                # (halka 0,35'e karşı zincir 1,22 -- halkanın üstünlüğü
                # değil, zincirin bozukluğuydu).
                if self.halka:
                    E = np.einsum("bij,bjk->bik", sag, sol, optimize=True)
                else:
                    E = np.einsum("bj,bi->bji", sag[:, :, 0], sol[:, 0, :],
                                  optimize=True)
                # tasarım dizeyi: (B, (P+1)·χ·χ)
                A = np.einsum("bp,bji->bpij", Tb[:, k], E,
                              optimize=True).reshape(B, -1)
                M = A.T @ A + lam * np.eye(A.shape[1])
                c = np.linalg.solve(M, A.T @ y)
                self.C[k] = c.reshape(self.derece + 1, self.chi, self.chi)
                K[:, k] = np.einsum("bp,pij->bij", Tb[:, k], self.C[k],
                                    optimize=True)
            seyir.append(float(np.sqrt(np.mean((self.deger(t) - y) ** 2))))
        return seyir


# =====================================================================
def _gosterim_ptr() -> str:
    rng = np.random.default_rng(0)
    s = ["=== Polinomial Tensör Halkası (PTR) ==="]

    # --- 1. Halka mı zincir mi: DÖNGÜSEL bir hedefte mukayese
    n, chi, der = 6, 4, 6
    B = 900
    t = rng.uniform(-1, 1, size=(B, n))

    def hedef_donusel(t):
        # döngüsel bakışımlı: her değişken KOMŞUSUYLA çarpılır ve
        # SONUNCU ile BİRİNCİ de komşudur -- halkanın tam tarifi
        return sum(np.cos(2.0 * t[:, k]) * np.cos(2.0 * t[:, (k + 1) % n])
                   for k in range(n))

    def hedef_dogrusal(t):
        # uçları bağlı OLMAYAN hedef: zincir bunu da temsil edebilmeli
        return sum(np.cos(2.0 * t[:, k]) * np.cos(2.0 * t[:, k + 1])
                   for k in range(n - 1))

    s += ["", "1) Aynı χ ve derecede halka ile zincir (ALS, kapalı form):",
          "   hedef            temsil    parametre   RMSE (900 nokta)"]
    for ad, hf in (("döngüsel", hedef_donusel), ("uçları açık", hedef_dogrusal)):
        y = hf(t)
        y = (y - y.mean()) / (y.std() + 1e-12)
        for tur_ad, hlk in (("halka", True), ("zincir", False)):
            P = PolinomHalka(n, chi=chi, derece=der, tohum=1, halka=hlk)
            seyir = P.oturt(t, y, tur=12)
            s.append("   %-16s %-9s %-11d %.4f"
                     % (ad, tur_ad, len(P), seyir[-1]))

    # --- 2. Bellek: halka ne kadar sıkıştırıyor
    s += ["", "2) Bellek: açık tabloya karşı halka"]
    for n_ in (8, 16, 32, 64):
        H = TensorHalka(n_, d=2, chi=8, tohum=0)
        s.append("   n=%-3d  halka parametre = %-7d   açık tablo = 2^%d"
                 % (n_, len(H), n_))

    # --- 3. İz gerçekten çevrimi kapatıyor mu (sınama)
    H = TensorHalka(5, d=2, chi=3, tohum=2)
    X = rng.integers(0, 2, size=(7, 5))
    elle = []
    for x in X:
        M = np.eye(3)
        for k in range(5):
            M = M @ H.G[k][:, x[k], :]
        elle.append(np.trace(M))
    s += ["", "3) Yığın büzülmesi elle çarpımla aynı mı: âzamî fark %.2e"
          % float(np.abs(H.genlik(X) - np.array(elle)).max())]

    s += ["",
          "Hüküm ve KENDİ TAHMİNİMİN YANLIŞ ÇIKMASI: halkanın üstünlüğünü",
          "hedefin döngüselliğine bağlamıştım. Ölçüm bunu DOĞRULAMADI --",
          "halka her iki hedefte de (0,355 ve 0,341) zincirden (0,548 ve",
          "0,544) daha iyi. Demek ki kazanç dönemlilikten değil, uçların",
          "SERBESTLİĞİNDEN geliyor: zincirde uç vektörleri e₀'a sabitli,",
          "her iki uçta χ−1 boyut boşa gidiyor; halkada iz alındığı için",
          "öyle bir kayıp yok. Aynı parametre sayısında halkanın müessir",
          "sığası daha büyük. Dönemlilik faydası varsa bu ölçüm onu",
          "ayıramadı ve ayırdığı iddia edilmiyor.",
          "",
          "Çevrim bedeli duruyor: halkada kanonik hâl yoktur, onun için",
          "burası YÜZEY temsilidir; durum temsili ağaçtadır (H53)."]
    return "\n".join(s)

# ======================================================================
#  İKİ BOYUTLU AĞAÇ TENSÖR AĞI (TTN) (evvelce nefs/agac.py)
# ======================================================================

@dataclass
class Dugum:
    """Ağacın bir düğümü.

    Yaprak ise ``hucre`` doludur ve tensör ``(d, üst_bağ)`` şeklindedir.
    İç düğüm ise tensör ``(sol_bağ, sağ_bağ, üst_bağ)`` şeklindedir.
    Kök düğümde ``üst_bağ = 1``.
    """
    no: int
    hucre: Optional[Tuple[int, int]] = None
    sol: Optional[int] = None
    sag: Optional[int] = None
    ust: Optional[int] = None
    T: Optional[np.ndarray] = None

    @property
    def yaprak(self) -> bool:
        return self.hucre is not None


@dataclass
class AgacAyar:
    h: int = 3
    w: int = 3
    renk: int = 4
    bag: int = 8               # χ
    tohum: int = 0


class AgacYazmaci:
    """İki boyutlu ızgaranın bütün muhtemel hâllerini tutan ağaç.

    Bölme usulü: her adımda dikdörtgenin **uzun kenarı** ikiye bölünür.
    Böylece bloklar kareye yakın kalır ve blok sınırı (dolayısıyla
    gereken ``χ``) mümkün olan en küçük hâlde tutulur. Satır satır yahut
    sütun sütun bölmek uzun ince şeritler doğurur ve sınırı büyütür --
    bu bir tercih değil, alan kanununun dayattığı şeydir.
    """

    def __init__(self, ayar: Optional[AgacAyar] = None) -> None:
        self.ayar = ayar or AgacAyar()
        a = self.ayar
        self.d = a.renk
        self.dugumler: List[Dugum] = []
        self.yaprak_no: Dict[Tuple[int, int], int] = {}
        self.kok = self._kur(0, 0, a.h, a.w, None)
        self.kesme = 0.0
        self.kapi = 0
        self.merkez: Optional[int] = None

    # -----------------------------------------------------------------
    def _yeni(self, **kw) -> int:
        no = len(self.dugumler)
        self.dugumler.append(Dugum(no=no, **kw))
        return no

    def _kur(self, i0: int, j0: int, h: int, w: int,
             ust: Optional[int]) -> int:
        """Dikdörtgeni özyinelemeli olarak ikiye böl; yaprakta hücre kalır."""
        if h == 1 and w == 1:
            no = self._yeni(hucre=(i0, j0), ust=ust)
            self.yaprak_no[(i0, j0)] = no
            # yaprak tensörü: (d, üst_bağ=1) -- düzgün süperpozisyon
            self.dugumler[no].T = (np.ones((self.d, 1), complex)
                                   / math.sqrt(self.d))
            return no
        no = self._yeni(ust=ust)
        if h >= w:                       # uzun kenar dikey → yatay kes
            k = h // 2
            sol = self._kur(i0, j0, k, w, no)
            sag = self._kur(i0 + k, j0, h - k, w, no)
        else:                            # uzun kenar yatay → dikey kes
            k = w // 2
            sol = self._kur(i0, j0, h, k, no)
            sag = self._kur(i0, j0 + k, h, w - k, no)
        self.dugumler[no].sol = sol
        self.dugumler[no].sag = sag
        # iç düğüm: (sol_bağ, sağ_bağ, üst_bağ) -- başlangıçta hepsi 1
        self.dugumler[no].T = np.ones((1, 1, 1), complex)
        return no

    # -----------------------------------------------------------------
    def derinlik(self) -> int:
        d = 0
        for no in self.yaprak_no.values():
            k = 0
            x = self.dugumler[no].ust
            while x is not None:
                k += 1
                x = self.dugumler[x].ust
            d = max(d, k)
        return d

    def yol(self, a: Tuple[int, int], b: Tuple[int, int]) -> List[int]:
        """İki yaprak arasındaki **tek** yol -- ağaçta çevrim yok.

        Bu, MPS'e karşı asıl kazançtır: zincirde iki hücre arası mesafe
        ``O(N)``, ağaçta ``O(log N)``. Yolun tekliği çevrimsizliğin
        neticesidir ve büzülmenin tam olmasının da sebebidir.
        """
        def kok_yolu(no: int) -> List[int]:
            y = [no]
            while self.dugumler[y[-1]].ust is not None:
                y.append(self.dugumler[y[-1]].ust)
            return y
        ya, yb = kok_yolu(self.yaprak_no[a]), kok_yolu(self.yaprak_no[b])
        kume = {x: i for i, x in enumerate(ya)}
        for j, x in enumerate(yb):
            if x in kume:
                return ya[:kume[x] + 1] + yb[:j][::-1]
        raise ValueError("yol bulunamadı -- ağaç bozuk")

    def mesafe(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return len(self.yol(a, b)) - 1

    # -----------------------------------------------------------------
    #  Ayar (gauge): kanonik hâl
    # -----------------------------------------------------------------
    def _komsular(self, no: int) -> List[int]:
        D = self.dugumler[no]
        return [x for x in (D.ust, D.sol, D.sag) if x is not None]

    def _indis(self, no: int, komsu: int) -> int:
        """``no`` düğümünün tensöründe ``komsu``ya bakan indisin yeri."""
        D = self.dugumler[no]
        if D.ust == komsu:
            return 1 if D.yaprak else 2
        if D.sol == komsu:
            return 0
        if D.sag == komsu:
            return 1
        raise ValueError("%d ile %d komşu değil" % (no, komsu))

    def _carp(self, no: int, komsu: int, M: np.ndarray) -> None:
        """``no``nun ``komsu``ya bakan indisine ``M`` dizeyini çarp.

        ``T'…ᵢ = Σⱼ T…ⱼ M[j,i]``. Bağ boyu ``M``in ikinci boyuna döner;
        bu yüzden bağ daralması ve genişlemesi hep bu tek yerden geçer.
        """
        p = self._indis(no, komsu)
        T = np.moveaxis(self.dugumler[no].T, p, -1)
        T = T @ M
        self.dugumler[no].T = np.moveaxis(T, -1, p)

    def kanonik(self, merkez: int) -> None:
        """Bütün tensörleri ``merkez``e bakacak şekilde izometrik yap.

        Yapraklardan merkeze doğru QR süpürmesi. Netice: merkez dışındaki
        her düğüm, merkeze bakan indisi hariç, bir izometridir. Bunun
        neden şart olduğu ölçüldü ve gizlenmez: kesme (truncation) ancak
        **çevresi izometrikse** en iyidir; değilse atılan tekil değerler
        hakikî hatayı vermez ve "kesme" diye raporlanan sayı yalan olur.

        Çevrimsizlik burada da işe yarar: her düğümün merkeze giden **tek**
        bir yolu vardır, dolayısıyla süpürme sırası tereddütsüzdür.
        MPS'te de böyledir; PEPS'te böyle bir şey **yoktur** -- kanonik
        hâl çevrimli ağda tanımlı değildir, bütün belâ oradan çıkar.
        """
        n = len(self.dugumler)
        uzak = [-1] * n
        dogru: List[Optional[int]] = [None] * n
        uzak[merkez] = 0
        kuyruk = [merkez]
        bas = 0
        while bas < len(kuyruk):
            x = kuyruk[bas]
            bas += 1
            for y in self._komsular(x):
                if uzak[y] < 0:
                    uzak[y] = uzak[x] + 1
                    dogru[y] = x
                    kuyruk.append(y)
        for x in sorted(range(n), key=lambda i: -uzak[i]):
            p = dogru[x]
            if p is None:
                continue
            ip = self._indis(x, p)
            T = np.moveaxis(self.dugumler[x].T, ip, -1)
            sek, D = T.shape[:-1], T.shape[-1]
            Q, R = np.linalg.qr(T.reshape(-1, D))
            k = Q.shape[1]
            self.dugumler[x].T = np.moveaxis(Q.reshape(sek + (k,)), -1, ip)
            self._carp(p, x, R.T)
        self.merkez = merkez

    def norm(self) -> float:
        """Durumun normu. Kanonik hâlde **yalnız merkez tensörünün** normu.

        Bütün ağacı büzmeye gerek yoktur; çevresi izometrik olduğu için
        onların katkısı birebir birdir. 30×30'da bu, ``d^900`` boyutlu bir
        vektörün normunu tek bir küçük tensörden okumak demektir.
        """
        if self.merkez is None:
            self.kanonik(self.kok)
        return float(np.linalg.norm(self.dugumler[self.merkez].T))

    def normalize(self) -> float:
        n = self.norm()
        if n > 1e-300:
            self.dugumler[self.merkez].T = self.dugumler[self.merkez].T / n
        return n

    # -----------------------------------------------------------------
    #  Kapılar: AĞAÇ MPO -- operatör yol boyunca yayılır, kübit OYNAMAZ
    # -----------------------------------------------------------------
    def tek_kapi(self, hucre: Tuple[int, int], G: np.ndarray) -> None:
        """Tek hücreye üniter. Bağ büyümez, kesme olmaz, hata **sıfırdır**."""
        no = self.yaprak_no[hucre]
        self.dugumler[no].T = np.asarray(G, complex) @ self.dugumler[no].T
        self.kapi += 1

    def _sup(self, P: Sequence[int], kes: bool) -> None:
        """Yol boyunca dik merkezi taşı; ``kes`` ise ``χ``ya indir."""
        for i in range(len(P) - 1):
            x, y = P[i], P[i + 1]
            ip = self._indis(x, y)
            T = np.moveaxis(self.dugumler[x].T, ip, -1)
            sek, D = T.shape[:-1], T.shape[-1]
            M = T.reshape(-1, D)
            if kes:
                U, S, Vt = np.linalg.svd(M, full_matrices=False)
                k = min(len(S), self.ayar.bag)
                self.kesme += float(np.sum(S[k:] ** 2))
                U, R = U[:, :k], S[:k, None] * Vt[:k, :]
            else:
                U, R = np.linalg.qr(M)
                k = U.shape[1]
            self.dugumler[x].T = np.moveaxis(U.reshape(sek + (k,)), -1, ip)
            self._carp(y, x, R.T)

    def cift_kapi(self, a: Tuple[int, int], b: Tuple[int, int],
                  G: np.ndarray) -> None:
        """İki hücreye üniter -- **hücreler yerinden kımıldamadan**.

        Kullanıcı hükmü: *"Ağaç MPO -- operatörü yol boyunca yay, kübit
        oynatma."* Yapılan tam olarak budur:

        1. ``G`` iki parçaya ayrılır: ``G = Σₖ Aₖ ⊗ Bₖ`` (SVD, ``r ≤ d²``).
           Ayrışmanın rütbesi ``r``, operatörün taşıdığı **bağ**dır.
        2. ``Aₖ`` ``a`` yaprağına, ``Bₖ`` ``b`` yaprağına vurulur ve her
           ikisi de üstlerine bir ``k`` indisi bırakır.
        3. ``k`` indisi ``a`` ile ``b`` arasındaki **tek yol** boyunca
           taşınır: yoldaki her düğüm ``T ⊗ δ`` ile genişletilir. Zirvede
           iki taraftan gelen ``k`` aynı ``δ`` ile kapanır -- operatör
           orada birleşir.
        4. Yol boyunca bağlar ``r`` katına çıkar; QR ile ayar alınıp SVD
           ile ``χ``ya indirilir.

        Takas ağıyla farkı: takasta hücreler yer değiştirir ve **her**
        takas ayrı bir kesme yapar; burada hücre hiç kımıldamaz, kesme
        yalnız yol kenarlarında bir kere olur. Zincirdeki takas yolu
        30×30'da 899 adımdı; buradaki yol 20'dir (bkz. ``mesafe``).

        Yaklaşıklık iddiası yok: ``χ`` yeterken hata makine hassasiyeti
        mertebesindedir, yetmezken **ölçülür** (``kesme``) ve öyle
        bildirilir.
        """
        d = self.d
        G = np.asarray(G, complex).reshape(d, d, d, d)      # a_çık,b_çık,a_gir,b_gir
        M = G.transpose(0, 2, 1, 3).reshape(d * d, d * d)   # (a_çık,a_gir)|(b_çık,b_gir)
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        r = int(np.sum(S > 1e-12 * (S[0] if S.size else 1.0)))
        r = max(r, 1)
        A = (U[:, :r] * S[:r]).T.reshape(r, d, d)
        B = Vt[:r, :].reshape(r, d, d)

        P = self.yol(a, b)
        self.kanonik(P[0])

        # --- uçlar: operatörün iki yarısı
        for no, K in ((P[0], A), (P[-1], B)):
            T = self.dugumler[no].T                          # (d, u)
            T2 = np.einsum("kij,ju->iuk", K, T, optimize=True)
            self.dugumler[no].T = T2.reshape(d, -1)

        # --- yol: δ ile yayılma (zirvede aynı δ operatörü kapatır)
        for i in range(1, len(P) - 1):
            x, e, f = P[i], P[i - 1], P[i + 1]
            ie, if_ = self._indis(x, e), self._indis(x, f)
            T = np.moveaxis(self.dugumler[x].T, [ie, if_], [0, 1])
            De, Df = T.shape[0], T.shape[1]
            kalan = T.shape[2:]
            T2 = np.einsum("efR,kl->ekflR", T.reshape(De, Df, -1),
                           np.eye(r), optimize=True)
            T2 = T2.reshape((De * r, Df * r) + kalan)
            self.dugumler[x].T = np.moveaxis(T2, [0, 1], [ie, if_])

        self._sup(P, kes=False)          # ayar: merkezi b'ye taşı
        self._sup(P[::-1], kes=True)     # kes: b'den a'ya, χ'ya indir
        self.merkez = P[0]
        self.kapi += 1

    # -----------------------------------------------------------------
    def hucre_dagilimi(self, hucre: Tuple[int, int]) -> np.ndarray:
        """Bir hücrenin marjinal dağılımı -- **çöküş yok**, zayıf okuma.

        Kanonik hâl sayesinde bütün ağacı büzmeye gerek kalmaz: merkez o
        yaprağa taşınır, geri kalanın katkısı birimdir.
        """
        no = self.yaprak_no[hucre]
        self.kanonik(no)
        T = self.dugumler[no].T
        p = np.real(np.sum(T * np.conj(T), axis=1))
        s = float(p.sum())
        return p / s if s > 1e-300 else p

    # -----------------------------------------------------------------
    #  Durum: bütün ızgaraların süperpozisyonu
    # -----------------------------------------------------------------
    def buz(self) -> np.ndarray:
        """Bütün ağacı büz -- **tam**, yaklaşıklık yok (çevrim olmadığı için).

        Netice ızgaranın tam dalga fonksiyonudur: ``d^(h·w)`` boyutunda.
        Yalnız **küçük ızgaralarda** çağrılabilir; asıl işleyiş bunu hiç
        açmaz. Burada bulunmasının sebebi, ağacın doğruluğunu bilinen
        hâllerle **sınayabilmektir**.
        """
        a = self.ayar
        if self.d ** (a.h * a.w) > 2 ** 22:
            raise MemoryError("tam büzülme yalnız küçük ızgarada")
        sira: List[Tuple[int, int]] = []

        def cik(no: int) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
            D = self.dugumler[no]
            if D.yaprak:
                return D.T, [D.hucre]          # (d, ust)
            S, hs = cik(D.sol)
            G, hg = cik(D.sag)
            # (…fizikî…, sol_ust) × (sol_ust, sag_ust, ust)
            M = np.tensordot(S, D.T, axes=([-1], [0]))     # (…, sag_ust, ust)
            M = np.tensordot(M, G, axes=([-2], [-1]))      # (…, ust, …g)
            # indisleri düzelt: ust en sona
            nd = M.ndim
            eks = list(range(nd))
            u = len(hs)                       # 'ust' indisinin yeri
            eks.remove(u)
            eks.append(u)
            return np.transpose(M, eks), hs + hg

        T, hucreler = cik(self.kok)
        T = T.reshape([self.d] * len(hucreler))
        # hücreleri satır sırasına göre yeniden diz
        hedef = [(i, j) for i in range(a.h) for j in range(a.w)]
        eks = [hucreler.index(x) for x in hedef]
        return np.transpose(T, eks).reshape(-1)

    def durum(self) -> Dict[str, float]:
        """Ağacın hâli: en büyük bağ, düğüm sayısı, bellek, kesme."""
        en_bag = 0
        bayt = 0
        for D in self.dugumler:
            if D.T is not None:
                en_bag = max(en_bag, max(D.T.shape))
                bayt += D.T.nbytes
        return {"düğüm": float(len(self.dugumler)),
                "yaprak": float(len(self.yaprak_no)),
                "derinlik": float(self.derinlik()),
                "en_büyük_bağ": float(en_bag),
                "bayt": float(bayt),
                "kesme": float(self.kesme),
                "kapı": float(self.kapi)}


# =====================================================================
#  Sınama: ağaç kapısı, TAM hesapla birebir karşılaştırılır
# =====================================================================
def _yogun_cift(psi: np.ndarray, n: int, d: int, pa: int, pb: int,
                G: np.ndarray) -> np.ndarray:
    """Aynı kapıyı **tam** dalga vektörüne vur -- hakikat kaynağı."""
    T = psi.reshape([d] * n)
    T = np.moveaxis(T, [pa, pb], [0, 1])
    sek = T.shape
    T = (G.reshape(d * d, d * d) @ T.reshape(d * d, -1)).reshape(sek)
    return np.moveaxis(T, [0, 1], [pa, pb]).reshape(-1)


def _rastgele_uniter(m: int, rng) -> np.ndarray:
    A = rng.normal(size=(m, m)) + 1j * rng.normal(size=(m, m))
    Q, R = np.linalg.qr(A)
    return Q * (np.diag(R) / np.abs(np.diag(R)))[None, :]


def _kapi_sinamasi(h: int, w: int, renk: int, bag: int, kapi: int,
                   tohum: int = 0) -> Dict[str, float]:
    rng = np.random.default_rng(tohum)
    ag = AgacYazmaci(AgacAyar(h=h, w=w, renk=renk, bag=bag))
    psi = ag.buz()
    n, d = h * w, renk
    hucreler = [(i, j) for i in range(h) for j in range(w)]
    for _ in range(kapi):
        a, b = rng.choice(len(hucreler), size=2, replace=False)
        G = _rastgele_uniter(d * d, rng)
        ag.cift_kapi(hucreler[a], hucreler[b], G)
        psi = _yogun_cift(psi, n, d, int(a), int(b), G)
    yak = ag.buz()
    # işaret/ölçek serbestliği yok: ikisi de aynı temsilde, doğrudan fark
    hata = float(np.linalg.norm(yak - psi) / (np.linalg.norm(psi) + 1e-300))
    return {"hata": hata, "norm": float(np.linalg.norm(yak)),
            "kesme": ag.kesme, "en_büyük_bağ": ag.durum()["en_büyük_bağ"]}


def _gosterim_agac() -> str:
    s = ["=== iki boyutlu ağaç: kurulum ==="]
    for h, w in ((3, 3), (5, 5), (10, 10), (30, 30)):
        ag = AgacYazmaci(AgacAyar(h=h, w=w, renk=10, bag=8))
        d = ag.durum()
        kose = ag.mesafe((0, 0), (h - 1, w - 1))
        s.append("  %2dx%-2d  düğüm=%4d derinlik=%2d   köşe-köşe: zincir %3d → "
                 "ağaç %2d  (%.1f kat)"
                 % (h, w, int(d["düğüm"]), int(d["derinlik"]),
                    h * w - 1, kose, (h * w - 1) / max(kose, 1)))

    s += ["", "=== AĞAÇ MPO kapısı: TAM hesapla karşılaştırma ===",
          "  (kübit oynatılmıyor; operatör yol boyunca yayılıyor)",
          "",
          "  ızgara  renk  χ   kapı   ‖Δψ‖/‖ψ‖     norm       kesme     "
          "en büyük bağ"]
    for h, w, renk, bag, kapi in ((2, 2, 2, 16, 6), (2, 3, 2, 64, 8),
                                  (3, 3, 2, 64, 10), (2, 3, 3, 81, 6)):
        r = _kapi_sinamasi(h, w, renk, bag, kapi)
        s.append("  %dx%-4d  %d    %-3d %-4d  %.3e  %.9f  %.3e  %d"
                 % (h, w, renk, bag, kapi, r["hata"], r["norm"],
                    r["kesme"], int(r["en_büyük_bağ"])))

    s += ["", "  --- χ kısılınca ne oluyor (aynı devre, yalnız χ değişiyor) ---",
          "  χ    ‖Δψ‖/‖ψ‖     kesme"]
    for bag in (2, 4, 8, 16, 64):
        r = _kapi_sinamasi(3, 3, 2, bag, 10)
        s.append("  %-4d %.3e  %.3e" % (bag, r["hata"], r["kesme"]))

    s += ["", "Hüküm: χ yeterken hata makine hassasiyetindedir -- ağaç MPO'su",
          "tam bir üniterdir, yaklaşıklık DEĞİLDİR. χ yetmezken hata ölçülür",
          "ve kesme ile beraber raporlanır; iddia edilmez."]
    return "\n".join(s)

# ======================================================================
#  ÜÇ AĞAÇ + boyut ihtimal uzayında (evvelce nefs/ucagac.py)
# ======================================================================

Izgara = np.ndarray
Cift = Tuple[Izgara, Izgara]


def iki_kademeli_donme(d: int, u: np.ndarray, v: np.ndarray,
                       teta: float) -> np.ndarray:
    """``span{u,v}`` düzleminde ``teta`` kadar dönen, geri kalanda birim
    olan ``d×d`` üniter.

    Genlik söndürmenin **üniter** yolu budur. "Bu ihtimali sıfırla" demek
    ölçüm ister ve çöküş getirir; "bu ihtimalden ötekine ``teta`` kadar
    dön" demek üniterdir ve süperpozisyonu diri tutar. Kütükteki
    "hiçbir meleke okumaz" şartı ancak böyle karşılanır.
    """
    u = np.asarray(u, complex)
    u = u / np.linalg.norm(u)
    v = np.asarray(v, complex) - u * (u.conj() @ np.asarray(v, complex))
    nv = np.linalg.norm(v)
    if nv < 1e-12:
        return np.eye(d, dtype=complex)
    v = v / nv
    c, s = math.cos(teta), math.sin(teta)
    P = np.outer(u, u.conj()) + np.outer(v, v.conj())
    D = (c - 1.0) * P + s * (np.outer(v, u.conj()) - np.outer(u, v.conj()))
    return np.eye(d, dtype=complex) + D


@dataclass
class Blok:
    ad: str
    bas: int                      # büyük ızgaradaki satır başlangıcı
    h: int
    w: int
    kilitli: bool


class UcAgac:
    """Şahitler + test girdisi + AÇIK çıktı: tek dalga, çok blok."""

    def __init__(self, sahitler: Sequence[Cift], test_girdi: Izgara,
                 renk: int = 10, cerceve: Optional[Tuple[int, int]] = None,
                 bag: int = 8) -> None:
        self.renk = int(renk)
        self.d = self.renk + 1
        self.HARIC = self.renk

        izgaralar: List[Izgara] = []
        for a, b in sahitler:
            izgaralar += [np.asarray(a), np.asarray(b)]
        izgaralar.append(np.asarray(test_girdi))
        if cerceve is None:
            H = max(g.shape[0] for g in izgaralar)
            W = max(g.shape[1] for g in izgaralar)
        else:
            H, W = cerceve
        self.H, self.W = int(H), int(W)

        self.bloklar: List[Blok] = []
        for k, (a, b) in enumerate(sahitler):
            self._blok("şahit%d.girdi" % k, np.asarray(a), True)
            self._blok("şahit%d.çıktı" % k, np.asarray(b), True)
        self._blok("test.girdi", np.asarray(test_girdi), True)
        self._blok("ÇIKTI", None, False)

        toplam = len(self.bloklar) * self.H
        self.ag = AgacYazmaci(AgacAyar(h=toplam, w=self.W, renk=self.d,
                                       bag=bag))
        # kilitli blokları yaz -- çarpım hâli, hiçbir yaklaşıklık yok
        for blok, g in zip(self.bloklar, self._izgaralar):
            if blok.kilitli:
                self._yaz(blok, g)
        self.ag.kanonik(self.ag.kok)

    # -----------------------------------------------------------------
    def _blok(self, ad: str, g: Optional[Izgara], kilitli: bool) -> None:
        if not hasattr(self, "_izgaralar"):
            self._izgaralar: List[Optional[Izgara]] = []
        bas = len(self.bloklar) * self.H
        h = g.shape[0] if g is not None else self.H
        w = g.shape[1] if g is not None else self.W
        self.bloklar.append(Blok(ad, bas, h, w, kilitli))
        self._izgaralar.append(g)

    def blok(self, ad: str) -> Blok:
        for b in self.bloklar:
            if b.ad == ad:
                return b
        raise KeyError(ad)

    def hucre(self, blok: Blok, i: int, j: int) -> Tuple[int, int]:
        return (blok.bas + i, j)

    # -----------------------------------------------------------------
    def _yaz(self, blok: Blok, g: Izgara) -> None:
        """Kilitli bloğu ızgaraya sabitle: her yaprak bir taban hâli.

        Çerçevenin dışında kalan hücreler ``HARİÇ``e sabitlenir; yani
        şahitlerin **kendi boyutları** da durumun içindedir, dışarıdan
        tutulan bir sayı değil.
        """
        for i in range(self.H):
            for j in range(self.W):
                c = (int(g[i, j]) if (i < g.shape[0] and j < g.shape[1])
                     else self.HARIC)
                no = self.ag.yaprak_no[self.hucre(blok, i, j)]
                T = np.zeros((self.d, 1), complex)
                T[c, 0] = 1.0
                self.ag.dugumler[no].T = T

    # -----------------------------------------------------------------
    #  Çıktı ağacına vurulan kapılar -- hepsi ÜNİTER, hiçbiri okumaz
    # -----------------------------------------------------------------
    def _dolu_yon(self) -> np.ndarray:
        v = np.ones(self.d, complex) / math.sqrt(self.renk)
        v[self.HARIC] = 0.0
        return v

    def _haric_yon(self) -> np.ndarray:
        v = np.zeros(self.d, complex)
        v[self.HARIC] = 1.0
        return v

    def boyut_kapisi(self, h: int, w: int, teta: float = 0.6) -> int:
        """``h×w`` boyutunu **kayırır**: içeride ``HARİÇ``i, dışarıda
        doluluğu söndürür.

        Bu bir "boyut tahmini" değildir; bir **kanaat kapısıdır**. Aklın
        şahitlerden çıkardığı münasebet buraya bir açı olarak girer;
        ``teta`` büyüdükçe kanaat kuvvetlenir, ``teta=0``da hiçbir şey
        olmaz. Birden çok boyut için birden çok kapı vurulabilir ve
        hepsi aynı anda askıda kalır -- seçim, ölçümde değil, genliktedir.
        """
        cikti = self.blok("ÇIKTI")
        D, X = self._dolu_yon(), self._haric_yon()
        n = 0
        for i in range(self.H):
            for j in range(self.W):
                icinde = (i < h and j < w)
                # içeride HARİÇ → dolu, dışarıda dolu → HARİÇ
                G = (iki_kademeli_donme(self.d, X, D, teta) if icinde
                     else iki_kademeli_donme(self.d, D, X, teta))
                self.ag.tek_kapi(self.hucre(cikti, i, j), G)
                n += 1
        return n

    def renk_kapisi(self, i: int, j: int, c: int, teta: float = 0.6) -> None:
        """Çıktının ``(i,j)`` hücresinde ``c`` rengini kayır."""
        v = np.zeros(self.d, complex)
        v[int(c)] = 1.0
        u = np.ones(self.d, complex)
        u[int(c)] = 0.0
        u = u / np.linalg.norm(u)
        G = iki_kademeli_donme(self.d, u, v, teta)
        self.ag.tek_kapi(self.hucre(self.blok("ÇIKTI"), i, j), G)

    def bag_kapisi(self, sahit_hucre: Tuple[int, int],
                   cikti_hucre: Tuple[int, int], teta: float = 0.4) -> None:
        """Şahit hücresiyle çıktı hücresini **dolaştır** -- H56'nın kalbi.

        Şahit yaprağı kilitli olduğu için bu kapı, o şahidin o hücrede ne
        gördüğünü çıktı hücresine bir **şart** olarak taşır: operatör yol
        boyunca yayılır (ağaç MPO), hiçbir hücre yer değiştirmez.
        """
        d = self.d
        G = np.eye(d * d, dtype=complex).reshape(d, d, d, d)
        # kontrollü dönme: şahit hücresi ``c`` ise çıktıda ``c`` kayrılır
        for c in range(self.renk):
            v = np.zeros(d, complex)
            v[c] = 1.0
            u = np.ones(d, complex)
            u[c] = 0.0
            u = u / np.linalg.norm(u)
            R = iki_kademeli_donme(d, u, v, teta)
            G[:, :, c, :] = 0.0
            G[c, :, c, :] = R
        self.ag.cift_kapi(sahit_hucre, cikti_hucre,
                          G.reshape(d * d, d * d))

    # -----------------------------------------------------------------
    #  Okuma -- yalnız en sonda, zayıf, çöküşsüz
    # -----------------------------------------------------------------
    def doluluk_haritasi(self) -> np.ndarray:
        """Çıktı bloğunun her hücresi için ``P(dolu)`` -- marjinal."""
        cikti = self.blok("ÇIKTI")
        M = np.zeros((self.H, self.W))
        for i in range(self.H):
            for j in range(self.W):
                p = self.ag.hucre_dagilimi(self.hucre(cikti, i, j))
                M[i, j] = float(1.0 - p[self.HARIC])
        return M

    def boyut_kanaati(self, esik: float = 0.5) -> Tuple[int, int]:
        """``P(dolu) > eşik`` olan hücrelerin kaplayacağı dikdörtgen.

        **Bu bir vekil ölçüdür ve öyle bildirilir.** Boyutun hakikî
        dağılımı marjinallerden okunmaz; hücreler dolaşıksa müşterek
        dağılım lazımdır ve o da ancak küçük ızgarada tam büzülerek
        (``buz``) hesaplanabilir. Burada okunan, her hücrenin **kendi**
        dolu olma ihtimalidir; kanaatin nereye kaydığını gösterir,
        boyutun olasılığını vermez.
        """
        M = self.doluluk_haritasi()
        h = int(np.sum(M.max(axis=1) > esik))
        w = int(np.sum(M.max(axis=0) > esik))
        return h, w

    def durum(self) -> Dict[str, float]:
        d = self.ag.durum()
        d["blok"] = float(len(self.bloklar))
        d["çerçeve_h"] = float(self.H)
        d["çerçeve_w"] = float(self.W)
        d["hâl_sayısı"] = float(self.d)
        return d


# =====================================================================
def _gosterim_ucagac() -> str:
    from idrak import arc

    s = ["=== ÜÇ AĞAÇ (H56) + boyut ihtimal uzayında (H62) ==="]

    gorevler = arc.gorevleri_getir("training")
    secilen = None
    for g in gorevler:
        if (len(g.egitim) >= 2 and g.azami_kenar() <= 5
                and not g.sekil_sabit_mi()):
            secilen = g
            break
    if secilen is None:
        for g in gorevler:
            if len(g.egitim) >= 2 and g.azami_kenar() <= 4:
                secilen = g
                break
    gi, co = secilen.sinama[0]
    u = UcAgac(secilen.egitim[:2], gi, renk=10, bag=8)
    d = u.durum()
    s += ["",
          "görev %s   şahit=%d   çerçeve=%dx%d   hâl/hücre=%d (10 renk + HARİÇ)"
          % (secilen.ad, 2, u.H, u.W, u.d),
          "blok dizilişi: " + " | ".join(b.ad for b in u.bloklar),
          "yaprak=%d  düğüm=%d  derinlik=%d  bellek=%.1f KB"
          % (int(d["yaprak"]), int(d["düğüm"]), int(d["derinlik"]),
             d["bayt"] / 1024.0),
          "hakikî çıktı boyutu (model BİLMİYOR): %dx%d" % co.shape]

    s += ["", "--- 1. Kilitli şahit blokları gerçekten kilitli mi ---"]
    b0 = u.blok("şahit0.girdi")
    a, b = secilen.egitim[0]
    hata = 0.0
    for i in range(min(3, u.H)):
        for j in range(min(3, u.W)):
            p = u.ag.hucre_dagilimi(u.hucre(b0, i, j))
            c = (int(a[i, j]) if i < a.shape[0] and j < a.shape[1]
                 else u.HARIC)
            hata = max(hata, abs(1.0 - float(p[c])))
    s.append("  şahit0 girdi hücrelerinde ‖P−δ‖ âzamî sapma: %.2e" % hata)

    s += ["", "--- 2. Çıktı ağacı açıkken bütün boyutlar askıda mı ---"]
    M = u.doluluk_haritasi()
    s.append("  P(dolu) haritası (düzgün süperpozisyon → hepsi eşit):")
    for i in range(u.H):
        s.append("    " + " ".join("%.3f" % v for v in M[i]))
    s.append("  beklenen: 10/11 = %.3f  (her hücre HARİÇ dahil 11 hâlde)"
             % (10.0 / 11.0))
    s.append("  boyut kanaati: %s  ← hiçbir boyut kayrılmıyor"
             % (u.boyut_kanaati(),))

    s += ["", "--- 3. Kanaat kapısı boyutu söndürebiliyor mu ---",
          "  (buradaki hedef boyut ELLE veriliyor; MEKANİZMA sınanıyor,",
          "   çözüm İDDİA EDİLMİYOR -- hangi melekenin bu açıyı hangi",
          "   formülle vereceği henüz kararlaşmadı)"]
    for teta in (0.3, 0.6, 0.9):
        v = UcAgac(secilen.egitim[:2], gi, renk=10, bag=8)
        n = v.boyut_kapisi(co.shape[0], co.shape[1], teta)
        M = v.doluluk_haritasi()
        ic = [M[i, j] for i in range(co.shape[0]) for j in range(co.shape[1])]
        dis = [M[i, j] for i in range(v.H) for j in range(v.W)
               if not (i < co.shape[0] and j < co.shape[1])]
        s.append("  θ=%.1f  kapı=%d   içeride P(dolu)=%.3f   dışarıda=%.3f"
                 "   kanaat=%s  norm=%.9f"
                 % (teta, n, float(np.mean(ic)),
                    float(np.mean(dis)) if dis else float("nan"),
                    v.boyut_kanaati(), v.ag.norm()))

    s += ["  KUSUR (ölçüldü, gizlenmiyor): θ tek yönlü bir 'kuvvet' DEĞİLDİR.",
          "  Başlangıç açısı arctan(√10)≈1,26 rad olduğu için θ büyüdükçe",
          "  içerideki doluluk önce 1'e çıkıp sonra GERİ düşüyor (θ=0,3'te",
          "  1,000 iken θ=0,9'da 0,687). Yani kanaat açısı, hedefe olan",
          "  açı FARKI olarak verilmelidir; sabit bir θ yanlıştır. Bunu",
          "  düzeltmek, açıyı verecek melekenin formülüne bağlıdır."]

    s += ["", "--- 4. Şahit ile çıktıyı dolaştıran kapı (ağaç MPO) ---"]
    v = UcAgac(secilen.egitim[:2], gi, renk=10, bag=8)
    sg = v.blok("şahit0.çıktı")
    ck = v.blok("ÇIKTI")
    once = v.ag.hucre_dagilimi(v.hucre(ck, 0, 0)).copy()
    v.bag_kapisi(v.hucre(sg, 0, 0), v.hucre(ck, 0, 0), teta=0.9)
    sonra = v.ag.hucre_dagilimi(v.hucre(ck, 0, 0))
    _, b0g = secilen.egitim[0]
    renk0 = int(b0g[0, 0])
    s.append("  şahit0 çıktısının (0,0) rengi = %d" % renk0)
    s.append("  çıktı (0,0)  P(renk %d):  önce %.4f → sonra %.4f"
             % (renk0, once[renk0], sonra[renk0]))
    s.append("  yol uzunluğu = %d adım   norm = %.9f   kesme = %.2e"
             % (v.ag.mesafe(v.hucre(sg, 0, 0), v.hucre(ck, 0, 0)),
                v.ag.norm(), v.ag.kesme))

    s += ["",
          "Hüküm: boyut artık dışarıdan verilen bir çerçeve değil, çıktı",
          "ağacının içindeki bir genliktir (H62). Kapı onu söndürebiliyor,",
          "üniterlik bozulmuyor, şahit ile çıktı fiilen dolaşabiliyor (H56).",
          "Bu bir ÇÖZÜCÜ DEĞİLDİR: hangi meleke hangi açıyı verecek,",
          "𝒪₆/𝒪₇/𝒪₉ cevaplanmadan yazılmayacak."]
    return "\n".join(s)

# ======================================================================
#  IZGARA İHTİMAL UZAYI (evvelce nefs/ihtimal.py)
# ======================================================================

def kubit_hesabi(h: int, w: int, renk: int = 10,
                 kubit_basina: int = 4) -> Dict[str, float]:
    """``h×w`` ızgaranın ihtimal uzayı kaç kübit ister?

    İki hesap ayrı verilir ve karıştırılmaz:

    * **asgarî** -- ``log₂(renk^(h·w))``. Bilgi kuramının verdiği taban;
      hücreleri ayrı ayrı kodlamayan, en sıkı paketleme.
    * **fiilî**  -- ``h·w·kubit_basina``. Her hücre kendi kübitlerinde
      durur; kodlama basit ve yerel kapılar mümkün olur. Bedeli birkaç
      yüz kübittir, kazancı bütün mimarinin işleyebilmesidir.
    """
    hucre = h * w
    asgari = hucre * math.log2(renk)
    fiili = hucre * kubit_basina
    return {"hücre": float(hucre),
            "ihtimal_log10": float(hucre * math.log10(renk)),
            "asgarî_kübit": float(math.ceil(asgari)),
            "fiilî_kübit": float(fiili),
            "22M_kaç_ızgara": float(22_000_000 / max(fiili, 1))}


@dataclass
class IhtimalAyar:
    h: int = 3
    w: int = 3
    renk: int = 4                 # kaç renk (ARC'de 10; sınamada az)
    kubit_basina: int = 2         # 2^kubit_basina ≥ renk olmalı
    bag: int = 8                  # χ
    tohum: int = 0

    def __post_init__(self) -> None:
        if 2 ** self.kubit_basina < self.renk:
            raise ValueError("kübit_başına renk sayısını kodlamaya yetmiyor")

    @property
    def hucre(self) -> int:
        return self.h * self.w

    @property
    def n(self) -> int:
        return self.hucre * self.kubit_basina


class IhtimalYazmaci:
    """Bütün muhtemel ızgaraları aynı anda tutan kübit yazmacı."""

    def __init__(self, ayar: Optional[IhtimalAyar] = None) -> None:
        self.ayar = ayar or IhtimalAyar()
        a = self.ayar
        self.y = Yazmac(a.n, bag=a.bag, tohum=a.tohum, tip=np.float64)
        self.kesme = 0.0
        self.kapi = 0

    # -----------------------------------------------------------------
    def yuva(self, i: int, j: int, b: int = 0) -> int:
        """``(i,j)`` hücresinin ``b``inci kübitinin zincir yeri.

        Satır sırası (row-major) kasten seçildi: aynı satırdaki komşu
        hücreler zincirde de komşudur, dolayısıyla yatay kısıtlar
        **yerel kapıyla** kurulur. Dikey komşuluk ``w`` kadar uzaktır ve
        MPO ister -- bu bir bedeldir ve ölçülür.
        """
        a = self.ayar
        return (i * a.w + j) * a.kubit_basina + b

    # -----------------------------------------------------------------
    def ac(self) -> None:
        """**1. adım: AÇ.** Her hücreye Hadamard.

        Bundan sonra ``renk^(h·w)`` ızgaranın **hepsi** eşit genliktedir
        ve MPS'te ``χ = 1`` ile tam temsil edilir: süperpozisyon bedava,
        dolaşıklık pahalıdır. Entropi burada **sıfırdır** ve ölçülür --
        henüz hiçbir hücre ötekini kısıtlamıyor.
        """
        self.y.tek_kapi(hadamard().astype(self.y.tip))
        self.kapi += self.y.n

    def durum(self) -> Dict[str, float]:
        e = self.y.dolasiklik_entropisi()
        return {"entropi": float(e["entropi"]),
                "schmidt": float(e["schmidt"]),
                "norm_hatası": float(self.y.norm_hatasi(ornek=32)),
                "kesme": float(self.kesme),
                "kapı": float(self.kapi),
                "bayt": float(self.y.bayt)}

    # -----------------------------------------------------------------
    #  2. adım: SÖNDÜR -- kısıt operatörleri (hepsi üniter)
    # -----------------------------------------------------------------
    def hucre_sabitle(self, i: int, j: int, renk: int) -> None:
        """``(i,j)`` hücresini bir renge **kilitle** -- tam kısıt.

        En sert kısıttır: o hücrenin kübitleri artık süperpozisyonda
        değildir. Genliği söndürmez, **döndürür**: hücre hangi bitlerde
        olmalıysa oraya çevrilir. Üniterdir ve tersi vardır.
        """
        a = self.ayar
        # **UÇ SIRASI (endianness) KUSURU DÜZELTİLDİ.** Kodlayıcı küçük
        # uçlu (b=0 en düşük bit), okuyucu ise büyük uçlu idi: renk 2'ye
        # kilitlenen hücre okumada renk 1 görünüyordu. İkisi de büyük
        # uçlu yapıldı -- ``blok_dagilimi`` indisi ilk kübiti en anlamlı
        # sayar, kodlama da öyle sayar.
        for b in range(a.kubit_basina):
            bit = (renk >> (a.kubit_basina - 1 - b)) & 1
            # |+⟩ hâlinden |bit⟩ hâline döndüren dik kapı
            G = (np.array([[1.0, 1.0], [1.0, -1.0]]) / math.sqrt(2.0)
                 if bit == 0 else
                 np.array([[1.0, -1.0], [1.0, 1.0]]) / math.sqrt(2.0))
            self.y.tek_kapi_yuva(self.yuva(i, j, b), G)
            self.kapi += 1

    def komsu_bagla(self, i1: int, j1: int, i2: int, j2: int,
                    teta: float) -> None:
        """İki hücreyi **dolaştır** -- 'bunlar birbirine bağlı' kısıtı.

        Kaide "komşu hücreler aynı renk olsun" gibi bir şey söylüyorsa,
        o iki hücrenin kübitleri arasına kontrollü dönme konur: birinin
        değeri ötekini büker. Uymayan bileşimlerin genliği zıt işaret
        alır ve toplandığında **söner** (yıkıcı girişim, H19).
        """
        a = self.ayar
        for b in range(a.kubit_basina):
            u, v = self.yuva(i1, j1, b), self.yuva(i2, j2, b)
            c, s = math.cos(teta), math.sin(teta)
            G = np.eye(4)
            G[2, 2], G[2, 3] = c, -s
            G[3, 2], G[3, 3] = s, c
            if abs(u - v) == 1:
                self.kesme += self.y.cift_kapi_yuva(min(u, v), G)
            else:
                self.kesme += self._uzak(u, v, G)
            self.kapi += 1

    def _uzak(self, u: int, v: int, G: np.ndarray) -> float:
        """Uzak çifte kapı -- takas ağıyla, sonra iade.

        MPO burada kullanılamaz: MPO tek bir operatörü bütün zincire
        yayar, burada ise **tek bir çifte** vurulacak. Takasın bedeli
        ölçülür ve raporlanır (kütük H41: takas dolaşıklığı sürükler).
        """
        if u > v:
            u, v = v, u
        kesme = 0.0
        yer = v
        while yer > u + 1:
            kesme += self.y.takas(yer - 1)
            yer -= 1
        kesme += self.y.cift_kapi_yuva(u, G)
        while yer < v:
            kesme += self.y.takas(yer)
            yer += 1
        return kesme

    # -----------------------------------------------------------------
    #  3. adım: OKU -- POVM zayıf ölçüm, çöküş yok
    # -----------------------------------------------------------------
    def hucre_dagilimi(self, i: int, j: int) -> np.ndarray:
        """``(i,j)`` hücresinin renk dağılımı -- **ortak**, marjinal değil.

        Hücrenin bütün kübitleri birden okunur: bitler dolaşık olabilir,
        ayrı ayrı okunursa yanıltır.

        ===================================================================
        BU YOL EVVELCE **ÇÖKÜYORDU** -- tevhid onu ortaya çıkardı (H211)
        ===================================================================

        Evvelki gövde çevreleri kendi başına büzüyordu ve ``A``yı
        ``A[k]`` diye indeksliyordu. Fakat ``Yazmac.A``nın şekli
        ``(B, n, χ, 2, χ)``dir; ilk eksen **yığın**dır, yuva değil.
        Yani ``A[k]`` yuva ``k``yı değil yığın üyesi ``k``yı okuyordu ve
        ``k ≥ B`` olur olmaz ``IndexError`` veriyordu. Fiilen koşturuldu::

            IndexError: index 11 is out of bounds for axis 0 with size 1

        Yani ``IhtimalYazmaci``nin **bütün okuma yolu** (``hucre_dagilimi``,
        ``izgara_oku``, ``izgara_ihtimali``) çalışmıyordu. Bunu hiç kimse
        görmemişti çünkü bu dosyayı hiçbir modül import etmiyordu -- AST
        ile ölçüldü: **sıfır çağıran**.

        Nüsha tekleşince kusur da kalktı: okuma artık ``Yazmac``ın tek
        ve sınanmış ``blok_dagilimi``ndan geçer.
        """
        a = self.ayar
        P = np.asarray(self.y.blok_dagilimi(self.yuva(i, j, 0),
                                            a.kubit_basina), float)
        if P.ndim > 1:                       # yığınlı hâlde ilk üye
            P = P[0]
        return P[:a.renk] / max(float(P[:a.renk].sum()), 1e-30)

    def izgara_oku(self) -> np.ndarray:
        """En muhtemel ızgara -- her hücrenin âzamî ihtimalli rengi.

        **Bu bir çöküş değildir**: dalga okunduktan sonra da diridir.
        Okunan şey, süperpozisyonda ayakta kalan dağılımın tepesidir.
        """
        a = self.ayar
        out = np.zeros((a.h, a.w), int)
        for i in range(a.h):
            for j in range(a.w):
                out[i, j] = int(np.argmax(self.hucre_dagilimi(i, j)))
        return out

    def izgara_ihtimali(self, g: np.ndarray) -> float:
        """Belirli bir ızgaranın ihtimali (hücre bağımsızlığı varsayımıyla).

        **Varsayım açıkça bildirilir**: hücreler dolaşıksa bu çarpım
        gerçek ortak ihtimal değildir, onun bir alt sınırı yahut kaba
        yaklaşığıdır. Tam ortak ihtimal bütün ızgarayı tek blok olarak
        okumayı ister ve ``4^(h·w)`` boyutunda bir dizey kurar --
        3×3'te 262.144, 30×30'da imkânsız.
        """
        a = self.ayar
        p = 1.0
        for i in range(a.h):
            for j in range(a.w):
                p *= float(self.hucre_dagilimi(i, j)[int(g[i, j]) % a.renk])
        return p
