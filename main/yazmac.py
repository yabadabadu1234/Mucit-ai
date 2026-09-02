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

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Yazmac", "hadamard", "dik_iki_kubit", "dik_iki_kubit_yigin",
           "MERAKademe"]

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
                "schmidt": float(nz.sum(axis=1).mean()),
                "azami_entropi": float(np.log(p.shape[1])),
                "kesit": float(kesit),
                "pencere": float(pencere)}

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
