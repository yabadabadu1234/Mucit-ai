"""
Temsil uzayları, hâl (durum) kaydı ve müşterek işlemler.

Kaynak metnin §1'inde sayılan uzaylar burada somut biçimlerine bağlanır:

| metindeki uzay | burada |
|---|---|
| Ham sinyal ``𝒳 ⊂ ℝ^{d_in}`` | ``Durum.X`` (n, d_in) |
| Hissî suret ``ℋ_hayal`` | ``Durum.Z_hayal`` / ``H_hayal`` (n, d_hayal) |
| Küllî mahiyet ``𝒮`` | ``Durum.S`` (n, d_sem) |
| Grassmannian ``𝒯_inv ⊂ Gr(k,d_in)`` | ``Durum.U_k`` (d_in, k), ortonormal |
| Nedensellik çizgesi ``𝒢_neden ⊂ DAG`` | ``Durum.A_neden`` (n, n) |
| Teleolojik ufuk ``𝒢_gaye`` | ``Durum.G`` (d_sem,) |
| Mutasarrıfa Lie cebri ``𝔤 ⊂ ℒ(𝒮,𝒮)`` | ``Parametreler.lie_uret`` |

**Dürüst kayıt.** Bu modül mimariyi KOŞTURUR; ağırlıklar eğitilmemiştir
(tohumlu sözde-rastgele ve kısmen analitik kurulur). Dolayısıyla burada
doğrulanabilecek şey "sistem doğru düşünüyor" değildir. Doğrulanabilecek
olan şudur ve hepsi ``test_nefs.py``de sınanır:

  1. Her melekenin girdi/çıktı **sözleşmesi** (uzay, boyut, aralık).
  2. Metindeki denklemlerden **riyazî olarak sınanabilir** olanların
     fiilen sağlanması (asiklik şartı, Betti sayıları, modus ponens
     doğruluk tablosu, Şek/Zan/Yakîn parçalanışının tam ve ayrık oluşu,
     Bayes normalizasyonu, HSIC'in bağımsızlıkta sıfırlanması, altın
     oran, Kan genişletmesinin evrensel hususiyeti …).
  3. Akışın **sabit noktaya** yakınsaması (Teemmül durma ölçütü).
  4. Uçtan uca **davranış**: tasdik, birbirini teyit eden delille
     yükseliyor, tenakuzla düşüyor mu?

Bunların hiçbiri "anlam" iddiası değildir. Anlam, eğitilmiş ağırlıkta
yaşar; burada yoktur ve olduğu söylenmez.
"""
from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# =====================================================================
#  Müşterek işlemler
# =====================================================================
def softmax(x: np.ndarray, eksen: int = -1) -> np.ndarray:
    z = x - np.max(x, axis=eksen, keepdims=True)
    e = np.exp(z)
    return e / np.sum(e, axis=eksen, keepdims=True)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60, 60)))


def gelu(x: np.ndarray) -> np.ndarray:
    """Tam (hata fonksiyonlu) GELU değil, tanh yaklaşığı -- kaynak metnin
    ``GELU`` yazdığı her yerde bu kullanılır."""
    return 0.5 * x * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (x + 0.044715 * x ** 3)))


def kat_norm(x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """LayerNorm (öğrenilen ölçek/kayma yok)."""
    mu = np.mean(x, axis=-1, keepdims=True)
    sd = np.std(x, axis=-1, keepdims=True)
    return (x - mu) / (sd + eps)


def kosinus(a: np.ndarray, b: np.ndarray) -> float:
    pay = float(np.sum(a * b))
    payda = float(np.linalg.norm(a) * np.linalg.norm(b))
    return pay / payda if payda > 1e-12 else 0.0


def dikkat(q: np.ndarray, k: np.ndarray, v: np.ndarray) -> np.ndarray:
    """``Softmax(QKᵀ/√d)V`` -- metinde geçen her dikkat bloğu bu."""
    d = q.shape[-1]
    return softmax(q @ k.T / np.sqrt(d)) @ v


def nicele(x: np.ndarray, adim: float) -> np.ndarray:
    """``Quantize(·, Δ_ızgara)``."""
    return np.round(x / adim) * adim


def guvenli_bol(a: float, b: float, eps: float = 1e-9) -> float:
    return float(a / (b + eps))


def celiski_dizeyi(S: np.ndarray, A: np.ndarray) -> np.ndarray:
    """``C = −S (AᵀA) Sᵀ``: çelişki çekirdeği. Tenakuzun ORTAK zemini.

    Çekirdeğin ``M = AᵀA`` ile **yarı-pozitif** seçilmesi iki şartı aynı
    anda sağlar ve bu iki şart tenakuzun tarifinden gelir:

    * **Hiçbir önerme kendisiyle çelişmez.** ``C_ii = −‖A Sᵢ‖² ≤ 0``, yani
      ``ReLU`` sonrası köşegen dâima sıfırdır -- istisnasız.
    * **Bir önerme kendi nakîziyle çelişir.** ``Sⱼ = −Sᵢ`` iken
      ``C_ij = +‖A Sᵢ‖² > 0``, yani âzamî çelişki.

    **Ölçümle reddedilen:** çekirdeği TERS SİMETRİK almak
    (``W = A − Aᵀ``). O hâlde köşegen cebren sıfırdır -- görünüşte
    aynı gaye. Fakat ``SᵢᵀW(−Sᵢ) = −SᵢᵀWSᵢ = 0``, yani **bir önerme
    kendi nakîziyle de çelişmez** hâle gelir. Sınama bunu yakaladı:
    birbirini teyit eden girdide tenakuz 0.158, biri diğerinin tam
    zıddı olan girdide 0.017 çıktı -- ölçü ters çalışıyordu. Ters
    simetrik çekirdek çelişkiyi değil, SIRALAMAYI ölçer.
    """
    M = A.T @ A
    C = -(S @ M @ S.T)
    return C


def celiski_gradyani(S: np.ndarray, A: np.ndarray, delta: float) -> np.ndarray:
    """``∂/∂S Σ_{i≠j} ReLU(C_ij − δ)`` -- ``C`` yukarıdaki çekirdek."""
    M = A.T @ A
    C = celiski_dizeyi(S, A)
    maske = (C - delta > 0).astype(float)
    np.fill_diagonal(maske, 0.0)
    return -2.0 * (maske @ S @ M)


def celiski_esigi(S: np.ndarray, A: np.ndarray, oran: float = 0.5) -> float:
    """``δ = oran · ortalama(−C_ii)`` -- ÖLÇEKTEN BAĞIMSIZ çelişki eşiği.

    Sabit ``δ = 0.5`` ölçekten habersizdi: ``C = −S(AᵀA)Sᵀ`` ``S``in
    normuyla karesel büyür, eşik ise sabit kalır. Aynı sistem, girdisi
    iki kat büyütülünce "iki kat daha çelişkili" görünürdü. Eşik artık
    melekenin kendi tarifinden çıkar: bir önerme kendi nakîziyle
    ``+‖A Sᵢ‖²`` kadar çelişir (bkz. `celiski_dizeyi`) ve bu ``−C_ii``dir.
    ``δ``, onun oranıdır -- "kendi nakîziyle çelişeceğinin yarısı kadar
    çelişiyorsa, çelişiyordur".

    **Ölçülen ve düzeltilmeyen.** Bu değişiklik, ``tenakuz``un rastgele
    girdide **tam sıfır** çıkmasını ortadan KALDIRMADI; ölçüldü, hâlâ
    sıfır. Sebep eşik değil, hâlin kendisidir: yüksek boyutta rastgele
    iki satırın ``M`` metriğindeki kosinüsü ``≈ ±1/√d_sem`` mertebesinde
    kalır, yani hiçbir çift "birbirinin nakîzine yarı yolda" değildir.
    Yani rastgele gürültüde çelişki YOKTUR ve sistem doğru davranmaktadır.
    Bunun bedeli ``nefs/tesir.py``de görünür: 𝒪₁₁ Tenakuz, 𝒪₂₈ Tashih ve
    𝒪₃₆ Tevil rastgele girdide tesirsiz ölçülür. Bu, o melekelerin boş
    olduğu anlamına gelmez -- ölçüldükleri girdide yapacak işleri
    olmadığı anlamına gelir; ``tesir.py`` bu yüzden yapılandırılmış bir
    girdiyle de ölçer.
    """
    C = celiski_dizeyi(S, A)
    olcek = float(np.mean(-np.diag(C)))
    return oran * max(olcek, 0.0)


def celiski_skoru(S: np.ndarray, A: np.ndarray, delta: float) -> float:
    C = celiski_dizeyi(S, A)
    T = np.maximum(C - delta, 0.0)
    np.fill_diagonal(T, 0.0)
    n = len(S)
    return float(np.sum(T) / max(n * (n - 1), 1))


# =====================================================================
#  Parametreler
# =====================================================================
class Parametreler:
    """Ad ile çağrılan, tohumlu ve **tekrarlanabilir** ağırlık deposu.

    ``W("müşahede.q", (d, d))`` aynı ad için hep aynı dizeyi verir --
    **aynı koşuda da, başka koşuda da**. Tohum ``zlib.crc32``ten
    türetilir; Python'un yerleşik ``hash()``i kullanılamaz, çünkü
    dizgeler için süreç başına RASTGELELEŞTİRİLİR (``PYTHONHASHSEED``).
    İlk kurulumda ``hash()`` kullanılmıştı ve sınamalar süreçler arası
    kararsızlaştı: aynı sınama ardışık iki koşuda bir geçip bir kaldı.
    Aynı süreç içinde tekrarlanabilirliği ölçen sınama bunu YAKALAYAMAZ;
    süreçler arası sınama şarttır ve eklendi.
    Ölçek ``1/√fan_in``dir; bu, katman çıktısının varyansını girdiyle
    aynı mertebede tutar (aksi hâlde 41 katman boyunca ya patlar ya söner
    -- ölçüldü: ölçeksiz kurulumda ``S``in normu 30 melekede 10¹²'ye
    çıkıyordu).
    """

    def __init__(self, tohum: int = 0) -> None:
        self.tohum = tohum
        self._depo: Dict[str, np.ndarray] = {}

    def W(self, ad: str, bicim: Tuple[int, ...]) -> np.ndarray:
        if ad not in self._depo:
            # ada göre türetilmiş tohum: çağrı sırasından bağımsız
            th = (self.tohum * 1000003 + zlib.crc32(ad.encode("utf-8"))) % (2 ** 31)
            rng = np.random.default_rng(th)
            olcek = 1.0 / np.sqrt(bicim[0])
            self._depo[ad] = rng.normal(scale=olcek, size=bicim)
        return self._depo[ad]

    def v(self, ad: str, n: int) -> np.ndarray:
        return self.W(ad, (n,)) * np.sqrt(n)   # vektörler birim mertebede

    def lie_uret(self, ad: str, d: int) -> np.ndarray:
        """``𝔤 ⊂ ℒ(𝒮,𝒮)`` üreteci: **ters simetrik**, yani ``exp`` ile
        ortogonal grup elde edilir. Metnin ``R = exp(θX) ∈ 𝔤`` ifadesi
        ancak böyle norm koruyan bir "tasarruf" verir."""
        A = self.W(ad, (d, d))
        return A - A.T

    def lie_tasarruf(self, ad: str, d: int, teta: float = 0.3) -> np.ndarray:
        """``R = exp(θ X)`` -- ölçek koruyan operatör (``RᵀR = I``)."""
        X = self.lie_uret(ad, d)
        # matris üsteli: seri (X ters simetrik, spektrum sınırlı)
        M = teta * X
        sonuc = np.eye(d)
        terim = np.eye(d)
        for k in range(1, 25):
            terim = terim @ M / k
            sonuc = sonuc + terim
            if np.max(np.abs(terim)) < 1e-15:
                break
        return sonuc


# =====================================================================
#  Hâl kaydı
# =====================================================================
@dataclass
class Olcumler:
    """Melekelerin ürettiği skaler tanılar; hiçbiri akışı gizlice
    değiştirmez, hepsi rapor edilir."""

    deger: Dict[str, float] = field(default_factory=dict)

    def koy(self, ad: str, v: Any) -> None:
        self.deger[ad] = float(v)

    def al(self, ad: str, varsayilan: float = float("nan")) -> float:
        return self.deger.get(ad, varsayilan)


@dataclass
class Durum:
    """Nefsin bir andaki bütün hâli. Melekeler bunu okur ve yazar."""

    # --- dış âlem
    E: np.ndarray                                  # (n, d_in) ham duyu
    sual: Optional[np.ndarray] = None              # (d_sem,) tevcih edilen sual

    # --- boyutlar
    d_in: int = 0
    d_hayal: int = 0
    d_sem: int = 0

    # --- O1..O10
    X: Optional[np.ndarray] = None                 # müşahede
    Z_hayal: Optional[np.ndarray] = None
    H_hayal: Optional[np.ndarray] = None
    Z_muhayyile: Optional[np.ndarray] = None
    sira: Optional[np.ndarray] = None              # tertip permütasyonu
    U_k: Optional[np.ndarray] = None               # Grassmann çerçevesi
    D: Optional[np.ndarray] = None                 # tecrit izdüşümü
    S: Optional[np.ndarray] = None                 # (n, d_sem) mahiyet
    S_kebir: Optional[np.ndarray] = None           # (d_sem,) makro
    K_vahime: Optional[np.ndarray] = None
    mu_mana: Optional[np.ndarray] = None
    parcalar: Optional[np.ndarray] = None          # tahlil bileşenleri
    tekil_degerler: Optional[np.ndarray] = None

    # --- O11..O24
    tenakuz: float = 0.0
    G: Optional[np.ndarray] = None                 # (d_sem,) gaye
    G_kebir: Optional[np.ndarray] = None
    Q_sual: Optional[np.ndarray] = None
    A_neden: Optional[np.ndarray] = None           # (n, n) DAG
    burhan: Optional[List[np.ndarray]] = None      # ispat zinciri

    # --- O25..O36
    M: Optional[np.ndarray] = None                 # teemmül belleği
    T: float = 0.0                                 # tasdik
    P_idrak: float = 0.5                           # şek/zan/yakîn
    makam: str = "Şek"

    # --- O37..O41
    N: Optional[np.ndarray] = None                 # beyan (ifade)

    # -----------------------------------------------------------------
    #  ŞAHİTLİK HATTI (kütük H6)
    # -----------------------------------------------------------------
    # Bir bulmacanın gösterim çiftleri. Dışarıdan verilebilir; verilmezse
    # 𝒪₄ Tertip bunu ham duyudaki kopmalardan **sezer**. Bayrak değildir:
    # sezilir, sınanır, nakzedilebilir.
    sahitler: Optional[List[Any]] = None           # List[sahit.Sahit]
    kaideler: Optional[List[np.ndarray]] = None    # şahit başına dik kaide
    kaide: Optional[np.ndarray] = None             # küllî kaide (𝒪₃₀ mühürler)
    nakz: Optional[List[int]] = None               # küllî kaideyi düşüren şahitler
    sahit_agirliklari: Optional[np.ndarray] = None # tevafukla düzeltilmiş ağırlık
    muteber_sahit: float = 0.0                     # fazla saymadan arındırılmış sayı
    tevafuk: float = 0.0

    # -----------------------------------------------------------------
    #  SEMBOLİK ALANLAR (kütük H4)
    # -----------------------------------------------------------------
    # Bu alanlar tensör DEĞİLDİR ve tensöre çevrilmezler. Hüküm veren
    # meleke sayı değil hüküm üretir; veri yolu bunu taşıyabilmelidir.
    ispat: Optional[List[Dict[str, Any]]] = None   # burhân kayıtları
    hukum: Optional[Dict[str, Any]] = None         # mühürlenmiş hüküm
    sukut: bool = False                            # makam Şek ise susulur
    tezat_kutbu: Optional[np.ndarray] = None       # 𝒪₁₀ → 𝒪₁₁
    w_kesit: Optional[np.ndarray] = None           # ℳ üzerindeki kesit (H3)

    olcum: Olcumler = field(default_factory=Olcumler)
    gunluk: List[str] = field(default_factory=list)

    @staticmethod
    def kur(E: np.ndarray, d_hayal: int = 24, d_sem: int = 16,
            sahitler: Optional[List[Any]] = None) -> "Durum":
        """``sahitler`` verilirse 𝒪₄ Tertip onu **olduğu gibi** kabul eder.

        Verilmezse bölütleme duyudan sezilir. İkisi de meşrudur; hangisi
        olduğu ``olcum["tertip.şahit_verildi"]`` ile bildirilir, çünkü
        dışarıdan verilen bölütleme modelin kendi kabiliyeti değildir ve
        öyle sayılmamalıdır.
        """
        return Durum(E=E, d_in=E.shape[1], d_hayal=d_hayal, d_sem=d_sem,
                     sahitler=list(sahitler) if sahitler is not None else None)

    def not_dus(self, meleke: str, mesaj: str) -> None:
        self.gunluk.append("%-24s %s" % (meleke, mesaj))
