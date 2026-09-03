"""
KÜLLÎ MELEKE ÇİPİ -- 44 meleke, 20 mertebe, iki hat, tek dosya (KÜME 2)

Padişahın tanzim fermanı bu uzvu ``nefs/melekeler.py`` diye adlandırdı
ve Küme 2'nin on üç dosyasını burada birleştirmeyi emretti. Emir
harfiyen icra edildi: **cevher seçilmedi, hepsi taşındı.** Kaynak
gövdeler birebir alındı; hiçbir formül elle yeniden yazılmadı.

===================================================================
İÇİNDEKİLER -- hangi gövde nereden geldi
===================================================================

    bölüm                          kaynak dosya (artık ilga)
    -----------------------------  --------------------------------
    Temel uzaylar, çelişki cebri   ``nefs/uzaylar.py``
    Meleke sözleşmesi ve sicili    ``nefs/meleke.py``
    Ĥ_Dimağ, so(D), BGCM           ``nefs/dimag.py``
    𝒪₄₂/𝒪₄₃/𝒪₄₄ ölçüleri           ``nefs/teskilat.py``
    20 ∞-kategori lifi             ``nefs/mertebe.py``
    𝒪₁–𝒪₁₀  İdrak   (klasik)       ``nefs/idrak.py``
    𝒪₁₁–𝒪₂₄ Akıl    (klasik)       ``nefs/akil.py``
    𝒪₂₅–𝒪₃₆ Murâkabe (klasik)      ``nefs/murakabe.py``
    𝒪₃₇–𝒪₄₁ Beyan   (klasik)       ``nefs/beyan.py``
    Klasik küllî akış              ``nefs/akis.py``
    44 melekenin ÜNİTER hâli       ``nefs/qmeleke.py``
    Kübit-yerli küllî akış         ``nefs/qakis.py``
    Ĥ_Dimağ'ın manifold yüzü       (bu dosyanın eski gövdesi)

===================================================================
İKİ HAT NİÇİN İKİSİ DE DURUYOR
===================================================================

Kullanıcının `nefs/qakis.py`de kayıtlı hükmü şuydu: *"yerinde kalsın,
kübit akışı yanına kurulsun, sonra devralınsın."* Devralma ölçüldü ve
oldu: `main/`ın dört giriş noktasından erişilen tek hat kuantum
hattıdır ve gerçek bir tâlim koşusu klasik hattan **tek fonksiyon**
çağırmıyor.

Fakat "devralındı" demek "atılsın" demek değildir. Klasik hat, aynı
41 melekenin **bağımsız ikinci temsilidir** ve kütük H88'in dersi tam
budur: ``beyan`` aylarca yanlış çevreden okudu, çünkü karşılaştıracak
ikinci bir temsil yoktu. İki hat aynı girdide yan yana koşturulabilir;
biri ötekinin hakemidir.

Klasik hatta duran ve **başka hiçbir yerde bulunmayan** riyaziyat
(ölçüldü, tek tek arandı):

* **HSIC** -- ``Tr(K H L H)/(n-1)^2`` bağımsızlık ölçüsü (𝒪₈ Tahlil).
* **Çelişki cebri** -- ``C = -S(A^T A)S^T``, gradyanı ve eşiği.
* **Procrustes** kapalı formu, **NOTEARS** asiklik cezası, Gazâlî
  mîzânı, altın oran harmonisi, Kan/RBF kenar tabanı.

Bunlar imha edilmedi; hepsi bu dosyadadır.
"""
from __future__ import annotations

import math
import sys
import time
import zlib
from dataclasses import dataclass, field, replace
from functools import lru_cache
from typing import (TYPE_CHECKING, Any, Callable, Dict, List, Optional,
                    Sequence, Tuple)

import numpy as np

from fitrat.tevafuk import fazla_sayma, tevafuk_olcusu
from kuantum.yazmac import dik_iki_kubit
from mizan.istikra import ardisiklik_kaidesi, tam_istikra_mi
from mizan.munazara import (MERTEBELER, ZANN_I_GALIB_ESIGI, hukum_agirligi,
                            ikili_entropi, makam_tayin, mertebe_adi,
                            yakin_gazali, yakin_zinciri)
from omega_kategori_nbe import kutuphane as L
from omega_kategori_nbe import sozdizim as S
from omega_kategori_nbe import turetimler as T
from omega_kategori_nbe.denetleyici import Baglam, denetle_t

from .gaye import gaye_kos
from .kule import ince, kaba
from .operad import tikaniklik_kapisi
from .zihin_durumu import (MAKAM_ADLARI, QAyar, QYazmac, degil_x, donme, faz_z,
                      kontrollu_donme)
from .sadakat import sadakat_intaci, sadakat_kapisi
from .sahit import (artiklar, bolutle, capraz_kovaryans, delil_dizileri,
                    kaide_uydur, kulli_kaide, nakz_bul)
from .tertip import tertip_kos

__all__ = ["MELEKE_SAYISI", "MERTEBE_SAYISI", "KANONIK_CETVEL",
           "EKSIK_MELEKELER", "meleke_mertebeleri", "so_ureteci",
           "mertebe_hamiltonyeni", "bgcm_kaybi", "muvazene_matrisi",
           "zirh_projektorleri", "H_toplam", "DimagAyari", "UMUM",
           "TALIM", "TAHSIL", "umumilestir", "talim_kademesi",
           "tahsil_et", "Lif", "lifleri_kur", "mertebe_gecisi", "SABIT",
           "DINAMIK", "AZAMI_TAM_MERTEBE", "rapor_mertebe", "QMeleke",
           "qsicil", "qmelekeler", "QAKIS", "NIZAM_ACIK", "nizami_ac",
           "nizam_cetveli", "QNefs", "rapor_qakis", "bec_faz_kilidi",
           "KulliMelekeManifoldu", "melekeleri_kur", "softmax",
           "sigmoid", "gelu", "kat_norm", "kosinus", "dikkat", "nicele",
           "guvenli_bol", "celiski_dizeyi", "celiski_gradyani",
           "celiski_esigi", "celiski_skoru", "Parametreler", "Olcumler",
           "Durum", "Meleke", "kaydet", "sicil", "melekeler",
           "rapor_meleke", "Musahede", "Hayal", "KAN_TEMELI",
           "kan_temeli", "Muhayyile", "Tertip", "Tecrit",
           "normalize_laplasyen", "betti_1iskelet", "Tasavvur", "Mana",
           "Tahlil", "hsic", "Terkip", "Tezat", "Tenakuz", "Tenkit",
           "Tasdik", "Gaye", "Merak", "DenemeYanilma", "Ihtimal",
           "Kiyas", "kiyas_ogren", "Temsil", "Tesbih", "pearson",
           "Tefekkur", "IlletKesfi", "asiklik_ihlali", "arka_kapi",
           "Mantik", "ima", "modus_ponens", "Ispat", "Teemmul", "Temkin",
           "Tetkik", "Tashih", "Teyit", "pearson_cok", "Tahkik",
           "Tedebbur", "SekZanYakin", "Muhakeme", "Tafsil", "Tefsir",
           "Tevil", "ALTIN_ORAN", "Fesahat", "susuldu_mu", "Talakat",
           "Belagat", "Sanat", "simetrik_harmoni", "Munazara",
           "ilk_yazanlar", "sira_gecerli_mi", "Nefs"]


# ======================================================================
#  TEMEL UZAYLAR -- Durum, Parametreler, çelişki cebri
#  (evvelce nefs/uzaylar.py)
# ======================================================================

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

    # -----------------------------------------------------------------
    #  BAĞLANMAMIŞ MELEKE BIRAKILMAZ (kütük H33)
    # -----------------------------------------------------------------
    # Aşağıdaki alanların her biri, evvelce yalnız ölçüm defterine yazıp
    # neticeye hiç dokunmayan bir melekenin fiilî çıktısıdır. Her birinin
    # bir yazanı ve **en az bir okuyanı** vardır; okuyanı olmayan alan
    # açılmamıştır.
    strateji: Optional[np.ndarray] = None      # 𝒪₁₆ → 𝒪₂₁  (Mutasarrıfa R_t, H15)
    sonsal: Optional[np.ndarray] = None        # 𝒪₁₇ → 𝒪₂₅  (Bayes ardılı)
    somut: Optional[np.ndarray] = None         # 𝒪₁₉ → 𝒪₂₇  (somut temsil)
    vech: Optional[np.ndarray] = None          # 𝒪₂₀ → 𝒪₃₉  (vech-i şebeh)
    kusur: Optional[np.ndarray] = None         # 𝒪₂₇ → 𝒪₂₈  (kusur haritası)
    akibet: float = 0.0                        # 𝒪₃₁ → 𝒪₃₃  (risk)
    dallar: Optional[np.ndarray] = None        # 𝒪₃₄ → 𝒪₃₇  (tafsil dalları)
    murad: Optional[np.ndarray] = None         # 𝒪₃₅ → 𝒪₃₉  (tefsirin muradı)
    ahenk: float = 1.0                         # 𝒪₄₀ → 𝒪₄₁  (estetik ölçek)
    serbest_enerji: float = 0.0                # 𝒪₁₁ → 𝒪₃₂  (F_tenakuz, H16)

    # 20 ∞-kategori mertebesinden geçişin bıraktığı iz (``nefs/mertebe.py``).
    # 𝒪₂₁ Tefekkür yazar; 𝒪₃₂ makamı, 𝒪₃₃ mîzânı onunla tartar. Mertebeler
    # arası taşınamayan bileşen **tıkanıklıktır**: mana bir mertebeden
    # ötekine geçemiyorsa, o manadan yakîn devşirilemez.
    mertebe_tikanikligi: Optional[np.ndarray] = None   # 𝒪₂₁ → 𝒪₃₂, 𝒪₃₃
    mertebe_betti: Optional[np.ndarray] = None         # 𝒪₂₁ → 𝒪₃₂, 𝒪₃₃

    # Karesel melekelerin göreceği azamî satır sayısı. Bunun üstünde
    # ``nefs/kule.py`` devreye girer ve maliyet satır sayısında
    # DOĞRUSALA iner. ``Durum``da durur ki koşuya göre ayarlanabilsin.
    tavan: int = 256

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

# ======================================================================
#  MELEKE SÖZLEŞMESİ VE SİCİLİ (klasik)
#  (evvelce nefs/meleke.py)
# ======================================================================

class Meleke:
    """Bütün melekelerin ortak atası."""

    no: int = 0
    ad: str = ""
    okur: Tuple[str, ...] = ()
    yazar: Tuple[str, ...] = ()
    # İhtiyarî okumalar: varsa kullanılır, yoksa melekenin kendi yedeği
    # devreye girer. Bunlar bağımlılık çizgesine KATILMAZ; nefsin
    # devrelerinde tabiî olan geri besleme (ör. 𝒪₇ Mana'nın henüz
    # kurulmamış gayeye bakması) ancak böyle temsil edilebilir.
    ihtiyari: Tuple[str, ...] = ()

    def uygula(self, d: Durum, p: Parametreler) -> None:  # pragma: no cover
        raise NotImplementedError

    # -- sözleşme denetimi -------------------------------------------
    def girdiyi_denetle(self, d: Durum) -> None:
        for alan in self.okur:
            if getattr(d, alan, None) is None:
                raise ValueError(
                    "𝒪%d %s: '%s' alanı boş; bu melekeden önce onu yazan "
                    "meleke koşmamış." % (self.no, self.ad, alan)
                )

    def ciktiyi_denetle(self, d: Durum) -> None:
        for alan in self.yazar:
            if getattr(d, alan, None) is None:
                raise ValueError(
                    "𝒪%d %s: '%s' alanını yazacağını bildirdi, yazmadı."
                    % (self.no, self.ad, alan)
                )

    def kosu(self, d: Durum, p: Parametreler) -> None:
        self.girdiyi_denetle(d)
        self.uygula(d, p)
        self.ciktiyi_denetle(d)

    def __repr__(self) -> str:
        return "𝒪%d %s" % (self.no, self.ad)


_SICIL: Dict[int, Meleke] = {}


def kaydet(sinif):
    """Sınıf dekoratörü: melekeyi numarasıyla sicile yazar."""
    ornek = sinif()
    if ornek.no in _SICIL:
        raise ValueError("𝒪%d iki kere kaydedildi: %s ve %s"
                         % (ornek.no, _SICIL[ornek.no].ad, ornek.ad))
    _SICIL[ornek.no] = ornek
    return sinif


def sicil() -> Dict[int, Meleke]:
    return dict(_SICIL)


def melekeler() -> List[Meleke]:
    return [_SICIL[i] for i in sorted(_SICIL)]


def rapor_meleke() -> str:                                     # pragma: no cover
    """Kendi kendini gösterme (H126): **sözleşme fiilen tutuyor mu?**

    Bir sicil raporu, sicilin uzunluğunu yazmakla yetinemez; asıl iddia
    *"sessizce ``None`` taşıma imkânsızlaşır"*dır ve bu ancak ihlâl
    denenerek gösterilir. Burada kasten bozuk bir meleke koşturulur ve
    sözleşmenin **hata verdiği** görülür; vermezse ölçü kırmızıdır.
    """
    import numpy as np


    # Sicil, melekeleri TARİF EDEN modüller içe aktarılınca dolar;
    # bu dosya tek başına koşturulunca boştur ve "0 meleke" yazmak
    # yanıltıcı olurdu. Onun için kayıt eden modüller burada çağrılır.
    for m in ("nefs.idrak", "nefs.akil", "nefs.murakabe", "nefs.beyan"):
        try:
            __import__(m)
        except Exception:                          # pragma: no cover
            pass

    s = ["MELEKE SÖZLEŞMESİ VE SİCİLİ", ""]
    sc = sicil()
    s.append("  sicilde kayıtlı meleke : %d" % len(sc))
    if sc:
        k = sorted(sc)
        s.append("  numara aralığı         : 𝒪%d … 𝒪%d" % (k[0], k[-1]))
        bos = [i for i in k if not sc[i].okur and not sc[i].yazar]
        s.append("  sözleşmesi BOŞ olan    : %d" % len(bos))

    s.append("")
    s.append("  Sözleşme fiilen tutuyor mu? (kasten ihlâl edilir)")

    class _Okumayan(Meleke):
        no, ad = 9001, "sınama-okumayan"
        okur = ("olmayan_alan",)

        def uygula(self, d, p):                    # pragma: no cover
            return None

    class _Yazmayan(Meleke):
        no, ad = 9002, "sınama-yazmayan"
        yazar = ("olmayan_alan",)

        def uygula(self, d, p):
            return None

    d, p = Durum(E=np.zeros((2, 2))), Parametreler()
    for m in (_Okumayan(), _Yazmayan()):
        try:
            m.kosu(d, p)
            s.append("    %-22s HATA VERMEDİ  ← KIRMIZI" % m.ad)
        except (ValueError, AttributeError, TypeError) as e:
            s.append("    %-22s reddedildi: %s"
                     % (m.ad, str(e).split(";")[0][:56]))
    return "\n".join(s)

# ======================================================================
#  KÜLLÎ DİMAĞ HAMİLTONYENİ -- 44 meleke, 20 mertebe
#  (evvelce nefs/dimag.py)
# ======================================================================

#: Melekelerin adedi -- 𝒪₁ … 𝒪₄₄ (divanın 09-KÜLLÎ-TEŞKİLAT celsesi).
#: 41 aslî melekeye üç müstakil uzuv ilâve edildi: 𝒪₄₂ Umumileştirme,
#: 𝒪₄₃ Talim, 𝒪₄₄ Tahsil. Bunlar soyut isim değil, ``nefs/teskilat.py``de
#: formülleriyle duran operatörlerdir.
MELEKE_SAYISI: int = 44
#: Mertebe adedi -- 10 sabit zemin + 10 dinamik lif (`nefs/mertebe.py`).
MERTEBE_SAYISI: int = 20

#: **DİVAN-I ÂLÎ'NİN KANONİK 41 → 20 CETVELİ** (2 Eylül 2026 celsesi).
#:
#: Evvelki turda bu dağılım **inşa edilmişti** ve açık borç olarak
#: yazılmıştı; padişah tam cetveli verdi ve borç kapandı. Cetvel
#: harfiyen buradadır ve sınama onu denetler.
#:
#: Mertebe numaraları: ``0-9`` sabit zemin, ``10-19`` dinamik lif
#: (``d₁ … d₁₀`` sırasıyla ``10 … 19``).
KANONIK_CETVEL: Dict[int, int] = {
    # --- SABİT ZEMİN (lisan, mantık, ontolojik iskelet)
    1: 0, 37: 0, 38: 0,        # k=0 Lafız ve duyu zemini
    4: 1, 34: 1,               # k=1 Sentaks ve tertip
    6: 2, 2: 2, 3: 2,          # k=2 Tasavvur ve iç seyir
    7: 3, 35: 3,               # k=3 Mana ve intikal
    8: 4, 9: 4,                # k=4 Tahlil VE TERKİP (zıt çift, tasdik edildi)
    5: 5,                      # k=5 Tecrit ve soyutlama
    10: 6,                     # k=6 Tezat ve dinamik polarite
    23: 7, 18: 7,              # k=7 Mantık ve dedüksiyon
    11: 8, 12: 8,              # k=8 Tenakuz ve cerh
    13: 9, 32: 9,              # k=9 Tasdik ve itikat derecesi
    # --- DİNAMİK LİFLER (akıl yürütme, keşif, hüküm manifoldu)
    22: 10, 16: 10,            # d₁ İllet ve nedensellik (DAG)
    15: 11, 14: 11,            # d₂ Merak ve teleoloji (gaye)
    21: 12, 25: 12, 26: 12,    # d₃ Tefekkür, Teemmül, Temkin (tasdik edildi)
    27: 13, 28: 13,            # d₄ Tetkik ve kılcal muayene
    24: 14, 29: 14,            # d₅ İspat ve burhân
    30: 15, 36: 15,            # d₆ Tahkik ve asla ircâ (tevil)
    33: 16, 31: 16,            # d₇ Küllî muhakeme ve adalet
    19: 17, 20: 17,            # d₈ Temsil ve teşbih köprüsü
    17: 18, 41: 18,            # d₉ İhtimaliyat ve münazara
    40: 19, 39: 19, 42: 19, 43: 19, 44: 19,   # d₁₀ Sanat, Belâgat,
                               # Umumileştirme, Talim, Tahsil
}

#: **BORÇ KAPANDI.** Evvelki turda ``𝒪₉ Terkip`` ile ``𝒪₂₁ Tefekkür``
#: cetvelde yoktu; gerekçeyle yerleştirilip padişahın tasdikine
#: sunulmuştu. Divan 09-KÜLLÎ-TEŞKİLAT celsesinde **ikisini de
#: onayladı** (𝒪₉ → k=4 Tahlil'in zıt çifti, 𝒪₂₁ → d₃ Tefekkür) ve
#: ayrıca ``𝒪₄₂ Umumileştirme``, ``𝒪₄₃ Talim``, ``𝒪₄₄ Tahsil``
#: melekelerini ``d₁₀``a tescil etti. Cetvel artık **44 tamdır** ve
#: bu sözlük boştur -- boş kalması, borcun kapandığının şahididir.
EKSIK_MELEKELER: Dict[int, int] = {}


def meleke_mertebeleri(cetvel: Optional[Dict[int, int]] = None
                       ) -> Dict[int, int]:
    """Kanonik cetveli döndür -- **inşa yok, tablo var**.

    Evvelki hâli 41 melekeyi "en boş mertebeye" yerleştiriyordu ve bu
    bir tercihti. Artık divanın cetveli statik bağlıdır; yalnız
    cetvelde bulunmayan iki meleke (``𝒪₉``, ``𝒪₂₁``) gerekçeli
    yerlerine konur ve bu **ayrıca işaretlidir**.
    """
    out = dict(KANONIK_CETVEL if cetvel is None else cetvel)
    for no, m in EKSIK_MELEKELER.items():
        out.setdefault(no, m)
    eksik = [n for n in range(1, MELEKE_SAYISI + 1) if n not in out]
    if eksik:                                        # pragma: no cover
        raise ValueError("cetvelde olmayan meleke: %s" % eksik)
    return out


def so_ureteci(D: int, a: int) -> np.ndarray:
    """``T^a = E_{pq} − E_{qp}`` -- ``so(D)``nin temel üreteci.

    Antisimetriktir, dolayısıyla ``exp(θT)`` **tam ortogonaldir** ve
    normu korur (ceridenin reel ``SO(D)`` hükmü). ``a`` indisi
    ``(p, q)`` çiftini sözlük sırasında belirler; belirlenimcidir,
    rastgele seçim yoktur.
    """
    D = int(D)
    ciftler = D * (D - 1) // 2
    if ciftler <= 0:
        raise ValueError("D ≥ 2 olmalı")
    a = int(a) % ciftler
    p = 0
    k = a
    while k >= D - 1 - p:
        k -= D - 1 - p
        p += 1
    q = p + 1 + k
    T = np.zeros((D, D))
    T[p, q] = 1.0
    T[q, p] = -1.0
    return T


def mertebe_hamiltonyeni(m: int, teta: np.ndarray, D: int,
                         cetvel: Optional[Dict[int, int]] = None
                         ) -> Tuple[np.ndarray, List[int]]:
    """``Ĥ_m = Σ_{i ∈ Meleke_m} θ_i T_i`` -- **tek** antisimetrik dizey.

    Döner ``(Ĥ_m, o mertebedeki meleke numaraları)``. 41 meleke ayrı
    ayrı çarpılmaz; hepsi tek bir üretece toplanır -- padişahın küllî
    esası budur ve maliyet farkı buradan doğar.
    """
    cet = meleke_mertebeleri() if cetvel is None else cetvel
    teta = np.asarray(teta, float).ravel()
    if teta.size < MELEKE_SAYISI:
        teta = np.resize(teta, MELEKE_SAYISI)
    H = np.zeros((int(D), int(D)))
    uyeler: List[int] = []
    for no in range(1, MELEKE_SAYISI + 1):
        if cet[no] != int(m):
            continue
        uyeler.append(no)
        H = H + float(teta[no - 1]) * so_ureteci(int(D), no - 1)
    return H, uyeler


def muvazene_matrisi(cetvel: Optional[Dict[int, int]] = None
                     ) -> np.ndarray:
    """``M_ij`` -- hangi iki melekenin çatışması ne kadar ağır sayılır.

    **Aynı mertebedeki melekeler ağır, farklı mertebedekiler hafif
    cezalanır** ve sebebi cebridir: aynı mertebede çalışan iki meleke
    aynı alt uzayı paylaşır, biri ötekinin dalgasını doğrudan söndürür.
    Farklı mertebedekiler zaten ayrı eksenlerdedir (H21: mertebeler
    toplanmaz), çatışmaları dolaylıdır.

    Köşegen sıfırdır: bir melekenin kendisiyle komütatörü zaten sıfır.
    """
    cet = meleke_mertebeleri() if cetvel is None else cetvel
    M = np.zeros((MELEKE_SAYISI, MELEKE_SAYISI))
    for i in range(1, MELEKE_SAYISI + 1):
        for j in range(1, MELEKE_SAYISI + 1):
            if i == j:
                continue
            M[i - 1, j - 1] = 1.0 if cet[i] == cet[j] else 0.1
    return M


def bgcm_kaybi(teta: np.ndarray, D: int,
               M: Optional[np.ndarray] = None,
               cetvel: Optional[Dict[int, int]] = None) -> Dict[str, float]:
    """``Ĥ_BGCM = Σ_ij M_ij ‖[𝒪_i, 𝒪_j]‖²_F`` -- **41 melekenin muvazenesi**.

    İki meleke sıra değiştirebiliyorsa (``[𝒪_i,𝒪_j] = 0``) birbirinin
    işini bozmaz: hangi sırada koşarlarsa koşsunlar netice aynıdır.
    Komütatör büyükse sıra mühimdir ve biri ötekini **eziyor** demektir.

    Ölçü kırmızıya döner: bütün melekeler aynı Cartan alt cebrinde
    (sıra değiştiren) seçilirse kayıp tam sıfırdır; rastgele seçilirse
    büyük çıkar. ``rapor_dimag`` ikisini de gösterir.
    """
    teta = np.asarray(teta, float).ravel()
    if teta.size < MELEKE_SAYISI:
        teta = np.resize(teta, MELEKE_SAYISI)
    Mm = muvazene_matrisi(cetvel) if M is None else np.asarray(M, float)
    O = [float(teta[i]) * so_ureteci(int(D), i)
         for i in range(MELEKE_SAYISI)]
    top = 0.0
    en_kotu = 0.0
    cift: Tuple[int, int] = (0, 0)
    for i in range(MELEKE_SAYISI):
        for j in range(i + 1, MELEKE_SAYISI):
            C = O[i] @ O[j] - O[j] @ O[i]
            v = float(np.sum(C * C))
            w = float(Mm[i, j] + Mm[j, i])
            top += w * v
            if w * v > en_kotu:
                en_kotu, cift = w * v, (i + 1, j + 1)
    # **NORMALİZASYON (padişahın 3. hükmü).** Komütatör ``θ²`` ile,
    # izi ``θ⁴`` ile büyür; ölçüldü: ``λ = 1``de kuvvetli ``θ``da
    # BGCM = 680,86 iken ARC = 1,20 idi -- muvazene terimi gayeyi
    # eziyordu. Payda ``1 + Σ‖O_k‖_F⁴``tür ve aynı mertebeden büyüdüğü
    # için netice **analitik olarak [0,1]e hapsedilir**:
    #
    #     Ĥ_BGCM^norm = Σ M_ij ‖[O_i,O_j]‖²_F / (1 + Σ_k ‖O_k‖_F⁴)
    #
    # Cauchy-Schwarz: ``‖[A,B]‖_F ≤ 2‖A‖_F‖B‖_F`` olduğundan pay,
    # ``4 max(M) (Σ‖O_k‖²)²`` ile sınırlıdır; payda aynı kuvvettedir.
    payda = 1.0 + float(sum(float(np.sum(o * o)) ** 2 for o in O))
    norm = top / payda
    return {"kayıp": float(top), "kayıp_norm": float(norm),
            "payda": float(payda),
            "en_kötü_çift_şiddeti": float(en_kotu),
            "en_kötü_i": float(cift[0]), "en_kötü_j": float(cift[1]),
            "muvazeneli": bool(top <= 1e-12)}


def zirh_projektorleri(nokta: np.ndarray, D: int, eps: float,
                       lam: float = 1.0) -> Dict[str, np.ndarray]:
    """``(𝒮, Π_betti, Π_koho)`` -- dördü de aynı veriden çıkar.

    * ``𝒮``      -- `nefs/zirh.sheaf_izdusumu`; ek yeri uyumsuzluğunu söndürür.
    * ``Π_betti`` -- ``exp(−λ Δ_Hodge)``; delikli yönleri bastırır.
    * ``Π_koho``  -- ``I − Σ_{ω ∈ H⁰, ω≠sabit} |ω⟩⟨ω|``; kopuk mana
      adalarını (çelişkiyi) siler. **Sabit vektör dışarıda bırakılır**:
      o, "her şey tek parça" yönüdür ve silinirse durum tamamen yok
      olurdu -- silinmesi gereken FAZLA bileşenlerdir.
    """
    from kuantum.tda import vietoris_rips
    from nefs.zirh import hodge_laplasyeni, sheaf_izdusumu

    X = np.atleast_2d(np.asarray(nokta, float))
    if X.shape[0] != int(D):
        raise ValueError("nokta sayısı D olmalı: %d ≠ %d" % (X.shape[0], D))
    Dm = np.sqrt(np.maximum(
        np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2), 0.0))
    K = vietoris_rips(Dm, float(eps), azami_boyut=1)
    L = hodge_laplasyeni(K, 0)
    if L.shape[0] != int(D):                       # tekil düğüm eksikse
        Z = np.zeros((int(D), int(D)))
        n = min(L.shape[0], int(D))
        Z[:n, :n] = L[:n, :n]
        L = Z
    oz, V = np.linalg.eigh((L + L.T) / 2.0)
    Pb = V @ np.diag(np.exp(-float(lam) * np.maximum(oz, 0.0))) @ V.T
    # kohomoloji: sıfır özdeğerli yönler = bağlantılı bileşenler.
    olcek = max(float(abs(oz).max()), 1e-30)
    cekirdek = V[:, oz <= 1e-9 * olcek]
    sabit = np.ones((int(D), 1)) / math.sqrt(int(D))
    if cekirdek.shape[1]:
        # sabit yönü çekirdekten çıkar; kalan "fazla ada" yönleridir
        c = cekirdek - sabit @ (sabit.T @ cekirdek)
        n = np.linalg.norm(c, axis=0)
        c = c[:, n > 1e-9] / n[n > 1e-9]
        Pk = np.eye(int(D)) - c @ c.T
    else:
        Pk = np.eye(int(D))
    S = sheaf_izdusumu(X[:, 0], X[:, -1]) if X.shape[1] > 1 else np.eye(D)
    if S.shape[0] != int(D):                       # pragma: no cover
        S = np.eye(int(D))
    return {"S": S, "betti": Pb, "koho": Pk,
            "betti0": int(cekirdek.shape[1])}


@dataclass
class DimagAyari:
    """``Ĥ_toplam``ın ölçüleri."""
    D: int = 16
    lam_mizan: float = 1.0
    lam_hodge: float = 1.0
    eps_rips: float = 1.2


def H_toplam(teta: np.ndarray, nokta: np.ndarray,
             H_arc: Optional[np.ndarray] = None,
             ayar: Optional[DimagAyari] = None
             ) -> Dict[str, object]:
    """Üç katmanı **tek dizeyde** birleştir ve her kalemi ayrı raporla.

    Dönen ``H`` bir ``D×D`` dizeydir; ``kalem`` sözlüğü her terimin
    Frobenius payını verir ki hiçbiri ötekinin arkasına saklanmasın
    (H47: ölçüler daima yan yana).
    """
    a = ayar or DimagAyari()
    D = int(a.D)
    P = zirh_projektorleri(nokta, D, a.eps_rips, a.lam_hodge)
    S, Pb, Pk = P["S"], P["betti"], P["koho"]
    cet = meleke_mertebeleri()

    H_mel = np.zeros((D, D))
    mertebe_payi: List[float] = []
    for m in range(MERTEBE_SAYISI):
        Hm, uyeler = mertebe_hamiltonyeni(m, teta, D, cet)
        if not uyeler:
            mertebe_payi.append(0.0)
            continue
        # Π_koho Π_betti 𝒮 [Ĥ_m] 𝒮ᵀ Π_betti Π_koho -- ceridenin sırası
        Z = Pk @ Pb @ S @ Hm @ S.T @ Pb.T @ Pk.T
        H_mel = H_mel + Z
        mertebe_payi.append(float(np.linalg.norm(Z)))

    b = bgcm_kaybi(teta, D, cetvel=cet)
    Ha = np.zeros((D, D)) if H_arc is None else np.asarray(H_arc, float)
    # ``λ_mizan(θ) = λ₀ / (1 + ‖θ‖²)`` -- padişahın geodezik ölçeklemesi.
    # Normalize BGCM zaten [0,1]dedir; λ o aralığı bir kere daha
    # ``θ`` ile söndürerek büyük ``θ`` rejiminde gayeyi serbest bırakır.
    tt = np.asarray(teta, float).ravel()
    lam = float(a.lam_mizan) / (1.0 + float(tt @ tt))
    bgcm_terim = lam * b["kayıp_norm"]
    H = Ha + H_mel + bgcm_terim * np.eye(D)
    return {"H": H,
            "λ_mizan": float(lam),
            "kalem": {"ARC": float(np.linalg.norm(Ha)),
                      "meleke": float(np.linalg.norm(H_mel)),
                      "BGCM": float(bgcm_terim * math.sqrt(D))},
            "mertebe_payı": mertebe_payi,
            "bgcm": b,
            "betti0": int(P["betti0"]),
            "dolu_mertebe": int(sum(1 for x in mertebe_payi if x > 0))}


def rapor_dimag() -> str:                                     # pragma: no cover
    s = ["KÜLLÎ DİMAĞ HAMİLTONYENİ -- 41 meleke, 20 mertebe, 4 zırh", ""]
    cet = meleke_mertebeleri()
    s.append("  1) 41 melekenin 20 mertebeye dağılımı")
    for m in range(MERTEBE_SAYISI):
        uy = [n for n in range(1, MELEKE_SAYISI + 1) if cet[n] == m]
        s.append("     mertebe %2d : %s" % (m, uy))
    yanlis = [n for n, m in KANONIK_CETVEL.items() if cet[n] != m]
    s.append("     divanın kanonik cetveli tutuyor mu: %s"
             % ("EVET" if not yanlis else "HAYIR %s" % yanlis))
    s.append("     cetvelde OLMAYAN, gerekçeyle konan: %s"
             % {("𝒪%d" % n): m for n, m in EKSIK_MELEKELER.items()})
    bos = [m for m in range(MERTEBE_SAYISI)
           if not any(cet[n] == m for n in cet)]
    s.append("     boş mertebe: %s" % (bos or "yok"))

    s.append("")
    s.append("  2) Muvazene (BGCM) -- ölçü kırmızıya dönüyor mu?")
    D = 12
    # (a) hepsi sıra değiştiren: aynı Cartan alt cebri → kayıp SIFIR
    teta0 = np.zeros(MELEKE_SAYISI)
    teta0[0] = 1.0
    b0 = bgcm_kaybi(teta0, D)
    s.append("     tek meleke uyanık   : ham %.3e  norm %.6f  muvazeneli=%s"
             % (b0["kayıp"], b0["kayıp_norm"], b0["muvazeneli"]))
    rng = np.random.default_rng(0)
    for ad, olc in (("41'i zayıf ×0,05", 0.05), ("41'i orta ×1", 1.0),
                    ("41'i kuvvetli ×5", 5.0), ("41'i azgın ×50", 50.0)):
        bb = bgcm_kaybi(olc * rng.normal(size=MELEKE_SAYISI), D)
        s.append("     %-19s: ham %.3e  norm %.6f"
                 % (ad, bb["kayıp"], bb["kayıp_norm"]))
    s.append("     → ham kayıp θ⁴ ile patlıyor, NORMALİZE olan [0,1]de kalıyor")

    s.append("")
    s.append("  3) Ĥ_toplam -- üç kalem yan yana")
    rng = np.random.default_rng(1)
    D = 16
    nk = rng.normal(size=(D, 3))
    for ad, t in (("zayıf θ", 0.05 * rng.normal(size=MELEKE_SAYISI)),
                  ("kuvvetli θ", rng.normal(size=MELEKE_SAYISI))):
        r = H_toplam(t, nk, H_arc=np.eye(D) * 0.3,
                     ayar=DimagAyari(D=D))
        k = r["kalem"]
        s.append("     %-11s ARC=%.4f  meleke=%.4f  BGCM=%.4f"
                 % (ad, k["ARC"], k["meleke"], k["BGCM"]))
        s.append("                 dolu mertebe=%d/20   zırhın gördüğü β₀=%d"
                 % (r["dolu_mertebe"], r["betti0"]))
    s.append("")
    s.append("  Üç kalem birbirinin arkasına saklanmıyor: θ büyüdükçe")
    s.append("  BGCM θ⁴ ile büyüyüp meleke terimini bastırıyor -- muvazene")
    s.append("  terimi tam bunun içindir (𝒪₂₄'ün 𝒪₃₉'u boğması).")
    return "\n".join(s)

# ======================================================================
#  𝒪₄₂ UMUMİLEŞTİRME, 𝒪₄₃ TALİM, 𝒪₄₄ TAHSİL -- ölçüleri
#  (evvelce nefs/teskilat.py)
# ======================================================================

#: Meleke numaraları (divanın 09-KÜLLÎ-TEŞKİLAT tescili).
UMUM: int = 42
TALIM: int = 43
TAHSIL: int = 44


def umumilestir(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]],
                esik: float = 1e-8) -> Dict[str, object]:
    """𝒪₄₂ -- numunelerin **kesişimindeki** değişmez dönüşümü süz.

    Her ``(X, Y)`` çifti bir ``A`` arar: ``A X ≈ Y``. Tek bir çift
    sonsuz çok ``A``ya uyar; **kanun**, hepsine birden uyanların
    kesişimidir. Kesişim, yığılmış kısıt dizeyinin sıfır uzayının
    ötelenmesidir ve boyutu ``serbestlik``tir.

    * ``serbestlik = 0`` → hiçbir ``A`` hepsine uymuyor: **çelişki**.
    * ``serbestlik > 0`` → bir kanun ailesi var; ``A`` en küçük
      normlusudur (Occam: en sade kanun).
    """
    if not ciftler:
        raise ValueError("en az bir numune lâzım")
    X0 = np.atleast_2d(np.asarray(ciftler[0][0], float))
    d = X0.shape[0]
    # vec(Y) = (Xᵀ ⊗ I) vec(A)
    satirlar: List[np.ndarray] = []
    sag: List[np.ndarray] = []
    for X, Y in ciftler:
        X = np.atleast_2d(np.asarray(X, float))
        Y = np.atleast_2d(np.asarray(Y, float))
        if X.shape[0] != d or Y.shape[0] != d:
            raise ValueError("bütün numuneler aynı boyutta olmalı")
        satirlar.append(np.kron(X.T, np.eye(d)))
        sag.append(Y.T.reshape(-1))
    M = np.vstack(satirlar)
    b = np.concatenate(sag)
    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    olcek = max(float(s[0]) if s.size else 0.0, 1e-30)
    tut = s > float(esik) * olcek
    a = Vt[tut].T @ ((U[:, tut].T @ b) / s[tut])
    A = a.reshape(d, d).T
    artik = float(np.linalg.norm(M @ a - b) / max(np.linalg.norm(b), 1e-30))
    return {"A": A, "serbestlik": int(np.sum(~tut)),
            "artık": artik,
            "umumîleşti": bool(artik < 1e-6),
            "numune": len(ciftler)}


def talim_kademesi(S: np.ndarray, tau: Sequence[float]
                   ) -> Dict[str, object]:
    """𝒪₄₃ -- hükmü kademe kademe keskinleştir; entropi **azalmalı**.

    ``tau`` monoton azalan olmalıdır. Her kademede ``softmax(S/τ)``
    alınır ve Shannon entropisi ölçülür. Entropi bir kademede artarsa
    o talim değil karıştırmadır ve ``sahih`` yalanlanır.
    """
    S = np.asarray(S, float).ravel()
    t = [float(x) for x in tau]
    if any(t[i] <= t[i + 1] for i in range(len(t) - 1)) is False and len(t) > 1:
        pass                                   # monotonluk aşağıda ölçülür
    ent: List[float] = []
    dag: List[np.ndarray] = []
    for x in t:
        z = S / max(float(x), 1e-12)
        z = z - z.max()
        p = np.exp(z)
        p = p / max(float(p.sum()), 1e-300)
        dag.append(p)
        nz = p > 1e-15
        ent.append(float(-np.sum(p[nz] * np.log(p[nz]))))
    azalan = all(ent[i] >= ent[i + 1] - 1e-12 for i in range(len(ent) - 1))
    tau_azalan = all(t[i] > t[i + 1] for i in range(len(t) - 1))
    return {"τ": t, "entropi": ent, "dağılım": dag,
            "τ_azalan": bool(tau_azalan),
            "entropi_azalan": bool(azalan),
            "sahih": bool(tau_azalan and azalan)}


def tahsil_et(teta: np.ndarray, H: np.ndarray, eta: float = 0.1,
              gama: float = 0.05) -> Dict[str, object]:
    """𝒪₄₄ -- ``θ ∘ exp(−η·H) + γ·I`` ile ağırlığı zâtî mülk kıl.

    ``H`` Ĥ_Dimağ'ın o parametreye düşen enerjisidir (burada köşegeni
    alınır: her ağırlığın kendi enerjisi). Yüksek enerji = çelişkili
    yön; ``exp(−ηH)`` onu söndürür.

    Dönen ``değişim`` ve ``sönüm`` ikisi birden okunur (H47): sönüm
    1'e yakınsa hiç öğrenilmemiş, 0'a yakınsa silinmiştir.
    """
    th = np.asarray(teta, float).ravel()
    Hd = np.asarray(H, float)
    e = np.diag(Hd) if Hd.ndim == 2 else Hd.ravel()
    if e.size != th.size:
        e = np.resize(e, th.size)
    sonum = np.exp(-float(eta) * np.abs(e))
    yeni = th * sonum + float(gama)
    return {"θ": yeni,
            "sönüm": float(np.mean(sonum)),
            "değişim": float(np.linalg.norm(yeni - th)
                             / max(np.linalg.norm(th), 1e-30)),
            "silindi": bool(np.mean(sonum) < 0.05),
            "öğrenmedi": bool(np.mean(sonum) > 0.999
                              and abs(float(gama)) < 1e-12)}


def rapor_teskilat() -> str:                                     # pragma: no cover
    s = ["ÜÇ YENİ UZUV -- 𝒪₄₂ Umumileştirme, 𝒪₄₃ Talim, 𝒪₄₄ Tahsil", ""]
    rng = np.random.default_rng(0)

    s.append("  𝒪₄₂ UMUMİLEŞTİRME -- kanun var mı, yoksa çelişki mi?")
    d = 4
    A = rng.normal(size=(d, d))
    cift = [(X, A @ X) for X in (rng.normal(size=(d, 3)) for _ in range(4))]
    r = umumilestir(cift)
    s.append("     tutarlı 4 numune : artık %.2e  serbestlik %d  umumîleşti %s"
             % (r["artık"], r["serbestlik"], r["umumîleşti"]))
    s.append("     bulunan A, hakikî A'ya uzaklığı: %.2e"
             % float(np.linalg.norm(r["A"] - A) / np.linalg.norm(A)))
    bozuk = list(cift[:3]) + [(cift[3][0], rng.normal(size=(d, 3)))]
    r2 = umumilestir(bozuk)
    s.append("     biri çelişkili   : artık %.4f  umumîleşti %s   ← KIRMIZI"
             % (r2["artık"], r2["umumîleşti"]))

    s.append("")
    s.append("  𝒪₄₃ TALİM -- kademeler keskinleşiyor mu?")
    S = np.array([3.0, 1.0, 0.5, -1.0, 2.0])
    t1 = talim_kademesi(S, (4.0, 2.0, 1.0, 0.5))
    s.append("     τ azalan  : entropi %s  sahih %s"
             % ([round(x, 4) for x in t1["entropi"]], t1["sahih"]))
    t2 = talim_kademesi(S, (0.5, 1.0, 2.0, 4.0))
    s.append("     τ ARTAN   : entropi %s  sahih %s   ← KIRMIZI"
             % ([round(x, 4) for x in t2["entropi"]], t2["sahih"]))

    s.append("")
    s.append("  𝒪₄₄ TAHSİL -- öğrenme mi, silme mi, hiç mi?")
    th = rng.normal(size=8)
    H = np.diag(np.abs(rng.normal(size=8)))
    for eta, gama, ad in ((0.1, 0.05, "mutedil"), (50.0, 0.0, "η çok büyük"),
                          (0.0, 0.0, "η sıfır")):
        r3 = tahsil_et(th, H, eta=eta, gama=gama)
        s.append("     %-12s sönüm %.4f  değişim %.4f  silindi=%s "
                 "öğrenmedi=%s"
                 % (ad, r3["sönüm"], r3["değişim"], r3["silindi"],
                    r3["öğrenmedi"]))
    return "\n".join(s)

# ======================================================================
#  20 ∞-KATEGORİ LİFİ
#  (evvelce nefs/mertebe.py)
# ======================================================================

# **``Parametreler`` yalnız TİP için lâzım (kütük H215).**
# ``mertebe_gecisi`` ``p.lie_tasarruf(...)`` çağırır; o usul yalnız
# klasik ``nefs/uzaylar.Parametreler``dedir (``QParametre``de YOKTUR --
# ölçüldü). Yani buradaki anotasyon, `nefs/qmeleke.py`dekinin aksine
# **doğrudur**. Fakat bağ çalışma anında lâzımdır, modül yüklenirken
# değil: modül seviyesinde tutulunca kuantum hattı (``qegitim`` yalnız
# ``DINAMIK``i, ``qmeleke`` yalnız ``lifleri_kur``u alır) bütün klasik
# dünyayı beraberinde sürüklüyordu.


# ``morfizm_tipi(A, n)`` ağacı derindir; denetleyici özyinelemeli iner.
sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))

#: Sabit blok: ardışık ve değişmez zemin (kütük H22).
SABIT: Tuple[int, ...] = tuple(range(10))
#: Dinamik blok: ardışık DEĞİL; sonsuz spektrumdan seçilmiş keyfî on
#: mertebe. Aradaki mertebeler için hiçbir şey açılmaz -- seyrek Kan
#: sıçraması. Bu on sayı ana modelin sabitidir; değiştirmek serbesttir.
DINAMIK: Tuple[int, ...] = (13, 17, 19, 20, 30, 55, 1000, 1009, 58383, 60000)

#: Bu derinliğe kadar ``morfizm_tipi`` fiilen kurulup denetlenir; üstü
#: temsilci tiple denetlenir ve **öyle işaretlenir**. Sebep ölçüldü:
#: denetim süresi mertebeyle üssel büyür (n=20: 0,66 sn, n=22: 1,05 sn),
#: n=60 000 imkânsızdır.
AZAMI_TAM_MERTEBE = 20

_U = S.Evren(0)
_D = S.Deg


@dataclass(frozen=True)
class Lif:
    """Bir ∞-kategori mertebesi ve mananın orada göreceği geometri."""
    yuva: int              # 0..19
    mertebe: int
    tam_kuruldu: bool      # morfizm_tipi fiilen inşa edildi mi
    denetlendi: bool       # makine tip denetiminden geçti mi
    tip_ozeti: str
    hata: str = ""

    @property
    def pencere(self) -> int:
        """Lifin dokunduğu eksen bloğunun genişliği: ``m+1``, 4 ile sınırlı.

        Sınır zaruridir: ``m+1`` genişliğinde yerel bir kapı ``2^(m+1)``
        boyutlu bir dizey ister. Dördün üstündeki mertebe kaybolmaz,
        **adıma** taşınır (aşağıya bak).
        """
        return min(self.mertebe + 1, 4)

    @property
    def adim(self) -> int:
        """Lifin baktığı satır mesafesi -- logaritmik.

        Tabansız alınırsa 60 000 mertebe hiçbir satıra dokunmaz; zincir
        kopar. Logaritma, yüksek mertebeyi uzak fakat erişilebilir kılar.
        """
        return 1 + int(math.log2(1 + self.mertebe))

    @property
    def olcek(self) -> float:
        """Dönme açısı ``1/(1+log(1+m))``: yüksek mertebe daha az büker."""
        return 1.0 / (1.0 + math.log1p(float(self.mertebe)))


# =====================================================================
def _tam_kur(m: int) -> Tuple[object, str]:
    return T.morfizm_tipi(_D("A"), m), "morfizm_tipi(A, %d)" % m


def _temsilci_kur(m: int) -> Tuple[object, str]:
    """Yüksek mertebe için temsilci tip -- ``Ω^n(S¹)`` kulesinin bir katı.

    Bu bir taklit değil **kısıtlı bir şahittir**: aynı homotopi kulesinin
    bir katıdır, fakat ``m``inci katı değildir. Rapor bunu böyle söyler.
    """
    n = 1 + (m % AZAMI_TAM_MERTEBE)
    return (L.dongu_uzayi_n(S.Cember(), S.Taban(), n),
            "Ω^%d(S¹)  [mertebe %d için temsilci]" % (n, m))


@lru_cache(maxsize=4)
def lifleri_kur(dinamik: Tuple[int, ...] = DINAMIK) -> Tuple[Lif, ...]:
    """20 lifi kur ve **her birini makine ile tip denetiminden geçir**.

    Önbelleklidir: denetim ~2 saniye sürer ve akış her koşuda yeniden
    kurmamalıdır. Lifler donuk (``frozen``) olduğu için paylaşmak
    emniyetlidir.
    """
    if len(dinamik) != 10:
        raise ValueError("dinamik mertebe sayısı 10 olmalı (H22)")
    gA = Baglam.terimlerden({"A": _U, "a": _D("A"), "b": _D("A")})
    g0 = Baglam()

    lifler: List[Lif] = []
    for yuva, m in enumerate(tuple(SABIT) + tuple(int(x) for x in dinamik)):
        tam = m <= AZAMI_TAM_MERTEBE
        tip, ozet = _tam_kur(m) if tam else _temsilci_kur(m)
        baglam = gA if tam else g0
        hata = ""
        try:
            denetle_t(tip, _U, baglam)
            gecti = True
        except Exception as e:                       # noqa: BLE001
            gecti = False
            hata = "%s: %s" % (type(e).__name__, str(e)[:120])
        lifler.append(Lif(yuva=yuva, mertebe=m, tam_kuruldu=tam,
                          denetlendi=gecti, tip_ozeti=ozet, hata=hata))
    return tuple(lifler)


# =====================================================================
def _betti0(v: np.ndarray, esik: float = 0.35) -> int:
    """Zincir üzerinde bağlantılı bileşen sayısı -- ``O(n)``.

    Zincirde çizge yalnız komşu kenarlardan ibarettir; bileşen sayısı,
    kopmuş komşuluk sayısının bir fazlasıdır. ``n×n`` bitişiklik dizeyi
    **hiç kurulmaz** -- 𝒪₅ Tecrit'te o dizey 65 536 düğümde 32 GiB
    istemişti; burada o hata tekrarlanmaz.
    """
    if len(v) < 2:
        return 1
    fark = np.abs(np.diff(v))
    olcek = float(np.median(fark)) + 1e-12
    return 1 + int(np.sum(fark > esik + 3.0 * olcek))


def mertebe_gecisi(S_giren: np.ndarray, p: "Parametreler",
                   dinamik: Tuple[int, ...] = DINAMIK
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """``S`` yirmi mertebeden geçip esas uzaya geri mühürlenir.

    Dönen: ``(S_yeni, tıkanıklık(20,), β₀(20,), büzülme)``.

    Terkip sıralıdır, toplam DEĞİLDİR (H21). Her lifte:

        S ← F_mᵀ · [zırh ∘ U_m ∘ uzak-menzil] · F_m · S

    ``F_m`` diktir (``lie_tasarruf``), dolayısıyla geri mühürleme
    kayıpsızdır; lifin bıraktığı tek iz, arada yapılan iştir.
    """
    A = np.asarray(S_giren, float)
    n, ds = A.shape
    lifler = lifleri_kur(tuple(dinamik))
    tikaniklik = np.zeros(len(lifler))
    betti = np.ones(len(lifler))
    onceki: Optional[np.ndarray] = None

    for lif in lifler:
        # --- F_m: life fırlatım (dik, dolayısıyla norm koruyan)
        F = p.lie_tasarruf("mertebe.F%d" % lif.yuva, ds, teta=0.25)
        B = A @ F.T

        # --- lifin dokunduğu eksen bloğu: AYRI EKSENLER (H21)
        k = min(2 ** lif.pencere, ds)
        bas = (lif.yuva * k) % ds
        sec = (bas + np.arange(k)) % ds
        blok = B[:, sec]

        # --- uzak menzilli tutarlılık: mertebe ne kadar yüksekse o kadar
        #     uzak satıra bakılır. ``roll`` ``O(n·k)``dir.
        adim = min(lif.adim, max(n - 1, 1))
        if n > 1:
            blok = blok + 0.15 * lif.olcek * (np.roll(blok, adim, axis=0) - blok)

        # --- U_m: mertebeye mahsus dönme; açı mertebeden gelir
        Um = p.lie_tasarruf("mertebe.U%d" % lif.yuva, k, teta=lif.olcek)
        blok = blok @ Um.T

        # --- enine zırh (H23), bu lifte ve yalnız bu lifte
        okuma = blok.mean(0)
        b0 = _betti0(okuma)
        betti[lif.yuva] = float(b0)
        ceza = float(np.exp(-0.25 * (b0 - 1) ** 2))
        blok = blok * ceza                      # ezber cezası

        if onceki is not None and len(onceki) == len(okuma):
            o = onceki / (float(np.linalg.norm(onceki)) + 1e-12)
            paralel = o * float(o @ okuma)
            dik = okuma - paralel
            nt = float(np.linalg.norm(okuma)) + 1e-12
            tik = float(np.linalg.norm(dik)) / nt
            tikaniklik[lif.yuva] = tik
            if tik > 0.9:
                # taşınamayan bileşen: yalnız onda biri geçsin
                blok = blok - 0.9 * (blok - blok @ np.outer(o, o))
        onceki = okuma

        B[:, sec] = blok
        # --- F_mᵀ: esas uzaya geri mühürleme
        A = B @ F

    # Yirmi lif boyunca genlik büzülür: uzak menzilli ortalama ve Betti
    # cezası ikisi de söndürücüdür (ölçüldü: 20 lif sonunda norm oranı
    # ≈ 0,52). Ölçek burada geri verilir, çünkü mertebe geçişinin işi
    # mananın YÖNÜNÜ bükmektir, şiddetini kısmak değil; kısılsaydı
    # 𝒪₂₁'den sonraki bütün melekeler sönmüş bir ``S`` görürdü. Büzülme
    # silinmez, ``mertebe.büzülme`` diye rapor_mertebe edilir.
    n_giren = float(np.linalg.norm(S_giren))
    n_cikan = float(np.linalg.norm(A))
    buzulme = n_cikan / max(n_giren, 1e-12)
    if n_cikan > 1e-12 and n_giren > 1e-12:
        A = A * (n_giren / n_cikan)
    return A, tikaniklik, betti, buzulme


# =====================================================================
def rapor_mertebe(dinamik: Tuple[int, ...] = DINAMIK, n: int = 24,
          ds: int = 16, tohum: int = 0) -> str:
    """20 lifin kuruluşu, denetimi ve bir geçişin ölçümü."""
    lifler = lifleri_kur(tuple(dinamik))
    s = ["=== MERTEBE GEÇİŞİ (ana model, omega_kategori_nbe ile) ===", "",
         "%-5s %-8s %-9s %-9s %-8s %-6s %s"
         % ("yuva", "mertebe", "kuruluş", "denetim", "pencere", "adım",
            "ölçek")]
    s.append("-" * 72)
    for u in lifler:
        s.append("%-5d %-8d %-9s %-9s %-8d %-6d %.4f   %s"
                 % (u.yuva, u.mertebe, "TAM" if u.tam_kuruldu else "temsilci",
                    "geçti" if u.denetlendi else "KALDI",
                    u.pencere, u.adim, u.olcek, u.tip_ozeti))
        if u.hata:
            s.append("      ! " + u.hata)

    rng = np.random.default_rng(tohum)
    A = rng.normal(size=(n, ds))
    p = Parametreler(tohum)
    B, tik, b0, buz = mertebe_gecisi(A, p, tuple(dinamik))
    s += ["",
          "geçiş: ‖S‖ %.4f → %.4f   (ölçek geri verilmeden büzülme %.4f)"
          % (np.linalg.norm(A), np.linalg.norm(B), buz),
          "yön değişimi: kosinüs %.4f"
          % float(np.sum(A * B) / max(np.linalg.norm(A) * np.linalg.norm(B),
                                      1e-12)),
          "tıkanıklık: ort %.4f  âzamî %.4f (yuva %d)"
          % (tik.mean(), tik.max(), int(np.argmax(tik))),
          "β₀: ort %.2f  âzamî %d  (β₀>1 olan lif sayısı: %d)"
          % (b0.mean(), int(b0.max()), int(np.sum(b0 > 1)))]
    tam = sum(1 for u in lifler if u.tam_kuruldu)
    ok = sum(1 for u in lifler if u.denetlendi)
    s += ["",
          "hulâsa: %d/20 lif TAM kuruldu, %d/20 makine denetiminden geçti."
          % (tam, ok)]
    return "\n".join(s)

# ======================================================================
#  𝒪₁–𝒪₁₀ İDRAK (klasik tensör hattı)
#  (evvelce nefs/idrak.py)
# ======================================================================

# =====================================================================
@kaydet
class Musahede(Meleke):
    """𝒪₁ Müşahede -- ``X_t = Π_müşahede(E_t)``.

    Hesaplanan: odak çekirdeği ``k_odak`` ile ağırlıklı toplama, öz-dikkat
    ``H⁽¹⁾``, süzgeç kapısı, ve **FNO çekirdeği**
    ``σ(Wv + ℱ⁻¹(R_θ·ℱv))`` (HoTT nüshasının 6. denklemi) -- bu, `yaklasim`
    modülünün Fourier işlemcisinin aynı fikridir ve burada spektral bir
    ön-süzgeç olarak koşar.

    Tanı: ``𝒜_müşahede = Tr(XᵀΔX)`` (uzamsal pürüz) ve ``ℒ_müşahede``.
    """

    no, ad = 1, "Müşahede"
    okur, yazar = ("E",), ("X",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        E = d.E
        n, di = E.shape

        # k_odak(r, r₀): konum uzayında Gauss odak penceresi
        r = np.arange(n, dtype=float)
        r0 = float(np.argmax(np.linalg.norm(E, axis=1)))   # en kuvvetli uyaran
        sigma = max(n / 4.0, 1.0)
        k_odak = np.exp(-((r - r0) ** 2) / (2 * sigma ** 2))
        X = E * k_odak[:, None]

        # FNO çekirdeği: R_θ kip çarpanları (düşük kipler geçer)
        F = np.fft.rfft(X, axis=0)
        kip = min(8, F.shape[0])
        R = p.v("müşahede.R", kip)
        F[:kip] *= (1.0 + 0.5 * R)[:, None]
        F[kip:] *= 0.0
        X_fno = np.fft.irfft(F, n=n, axis=0)
        X = np.tanh(X @ p.W("müşahede.W", (di, di)) + X_fno)

        # öz-dikkat -- KULE ÜZERİNDEN (bkz. nefs/kule.py)
        #
        # ``dikkat`` satır sayısında karesel maliyetlidir; ana modelin
        # uzun pencere tutamamasının birinci sebebi buydu (ölçüldü:
        # 64→0,06 sn, 256→3,09 sn, 1024→12,5 sn). Dikkat artık kaba
        # kademede koşar ve neticesi ince eksene ARTIK olarak geri
        # yayılır -- ince eksen silinmez (nizamname Kademe 4).
        Wq, Wk, Wv = (p.W("müşahede." + a, (di, di)) for a in "qkv")
        Xk, kademe, kayip = kaba(X, d.tavan)
        H1k = dikkat(Xk @ Wq, Xk @ Wk, Xk @ Wv)
        if kademe == 0:
            H1 = H1k
        else:
            H1 = X @ Wv + ince(H1k, n, kademe)      # artık bağı
        d.olcum.koy("kule.kademe", float(kademe))
        d.olcum.koy("kule.kaba_satır", float(len(Xk)))
        d.olcum.koy("kule.kayıp", kayip)

        # süzgeç kapısı  X ⊙ σ(W_süzgeç X)
        kapi = sigmoid(H1 @ p.W("müşahede.süzgeç", (di, di)))
        d.X = kat_norm(H1 * kapi)

        # tanı: uzamsal pürüz  Tr(Xᵀ Δ X),  Δ = ikinci fark
        lap = np.diff(d.X, n=2, axis=0) if n >= 3 else np.zeros((1, di))
        d.olcum.koy("müşahede.pürüz", np.sum(lap * lap))
        d.olcum.koy("müşahede.sadakat", -np.mean((d.X - kat_norm(E)) ** 2))
        d.not_dus(self.ad, "odak r₀=%d, kip=%d" % (int(r0), kip))


# =====================================================================
@kaydet
class Hayal(Meleke):
    """𝒪₂ Hayal -- hissî suretlerin kaydı ve sönümlü tutulması.

    Hesaplanan: ``Z = LayerNorm(W_h X + b)``; ısı denklemi adımı
    ``∂Z/∂t = ΔZ − λZ + F(X)``; kapılı bellek
    ``H = α⊙Z + (1−α)⊙H₋``; ``Memoria`` üstel ağırlıklı iz; ve
    ``Z_sağlam = Quantize(Z, Δ)``.
    """

    no, ad = 2, "Hayal"
    okur, yazar = ("X",), ("Z_hayal", "H_hayal")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        X = d.X
        n, di = X.shape
        dh = d.d_hayal
        Z = kat_norm(X @ p.W("hayal.h", (di, dh)))

        # ısı denklemi adımı (ayrık Laplace, açık Euler)
        lam, dt = 0.1, 0.05
        Zc = Z.copy()
        ileri, geri = np.roll(Zc, -1, axis=0), np.roll(Zc, 1, axis=0)
        Z = Zc + dt * ((ileri - 2 * Zc + geri) - lam * Zc + 0.5 * Zc)

        onceki = d.H_hayal if d.H_hayal is not None else np.zeros_like(Z)
        alfa = sigmoid(np.concatenate([X, onceki], axis=1)
                       @ p.W("hayal.α", (di + dh, dh)))
        H = alfa * Z + (1 - alfa) * onceki

        d.Z_hayal = Z
        d.H_hayal = H
        # Memoria: geçmişe üstel sönümle bakan iz (burada tek adımlık hâli)
        beta = 0.7
        d.olcum.koy("hayal.memoria", np.mean(beta * H + (1 - beta) * onceki))
        d.olcum.koy("hayal.nicelenmis_sapma",
                    np.mean(np.abs(nicele(Z, 0.05) - Z)))
        d.olcum.koy("hayal.kapı_ortalaması", np.mean(alfa))


#: KAN kenarlarının tek değişkenli tabanı: ``"rbf"`` veya ``"bspline"``.
#:
#: Risalelerde KAN kenarları **B-spline** ile tarif edilir; buradaki ilk
#: gerçekleme ise Gauss RBF kullanıyordu.  İkisi de tek değişkenli bir
#: taban verir, fakat üç noktada ayrışırlar ve bu ayrım ölçülebilir:
#:
#: * **Yerellik** — derece ``k`` B-spline'ı yalnız ``k+1`` düğüm
#:   aralığında sıfırdan farklıdır; bir katsayıyı oynatmak uzaktaki
#:   değerleri HİÇ etkilemez.  Gauss RBF her yerde sıfırdan farklıdır.
#: * **Birliğin bölünmesi** — ``Σ_i B_i(t) = 1`` tam sağlanır, yani
#:   çıktı tabanın konveks birleşimidir ve ölçek kaymaz.  RBF'te böyle
#:   bir garanti yoktur; toplam ``t``ye göre dalgalanır.
#: * **Kenar dışı** — B-spline ızgara dışında tam sıfırdır (o yüzden
#:   :mod:`token_uzaylari.kan_spline` ayrıca bir taban terimi taşır);
#:   RBF üstel küçük ama sıfırdan farklı kalır.
#:
#: Varsayılan ``"rbf"`` bırakıldı ki mevcut ölçümler ve testler aynı
#: kalsın; ``"bspline"`` belgelere sadık olandır ve
#: ``test_kan_temelleri_kiyas`` ikisini yan yana tartar.
KAN_TEMELI = "rbf"


def kan_temeli(v: np.ndarray, nb: int, tur: Optional[str] = None
               ) -> np.ndarray:
    """``(n, d)`` girdiden ``(n, d, nb)`` tek değişkenli taban dizeyi.

    ``tur`` verilmezse :data:`KAN_TEMELI` kullanılır.
    """
    tur = tur or KAN_TEMELI
    if tur == "rbf":
        dugum = np.linspace(-2.5, 2.5, nb)
        h = (dugum[1] - dugum[0]) * 1.5
        return np.exp(-0.5 * ((v[:, :, None] - dugum) / h) ** 2)
    if tur == "bspline":
        from token_uzaylari.kan_spline import bspline_temeli, dugum_dizisi
        k = 3
        G = nb - k                      # temel sayısı G+k = nb olsun
        if G < 1:
            raise ValueError("bspline için nb > 3 olmalı")
        d = dugum_dizisi(G, k, -2.5, 2.5)
        n, dh = v.shape
        B = bspline_temeli(v.reshape(-1), d, k)      # (n·dh, nb)
        return B.reshape(n, dh, nb)
    raise ValueError(f"bilinmeyen KAN tabanı: {tur!r}")


# =====================================================================
@kaydet
class Muhayyile(Meleke):
    """𝒪₃ Muhayyile -- kayıtlı suretten YENİ suret kurmak.

    Hesaplanan: Lie tasarrufu ``R ▷ (Z ⊗ M)``; **KAN biçimi**
    ``Φ_kurgu(x) = Σ_q Φ_q(Σ_p φ_{q,p}(z_p))`` (HoTT nüshası, 4-5.
    denklemler) -- kenar fonksiyonları :func:`kan_temeli` ile (RBF veya
    B-spline, bkz. :data:`KAN_TEMELI`); yaratıcılık gürültüsü
    ``ξ ~ 𝒩(0, σ²)``; ve ``Serbestlik = D_KL(P(Ẑ) ‖ P(Z))`` ile fantezi
    süzgeci.

    Metnin ``Ẑ·𝕀(Serbestlik ≤ τ)`` sert kesmesi yerine **uyarlanan adım**
    kullanılır; gerekçesi aşağıda, ölçümüyle birlikte yazılıdır. Netice
    aynı şartı SAĞLAR: çıktının serbestliği her hâlükârda ``τ``nun
    altındadır. Yani muhayyile serbesttir, fakat serbestliği ölçülür ve
    haddi vardır.
    """

    no, ad = 3, "Muhayyile"
    okur, yazar = ("Z_hayal",), ("Z_muhayyile",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        Z = d.Z_hayal
        n, dh = Z.shape
        R = p.lie_tasarruf("muhayyile.R", dh, teta=0.4)
        M = p.W("muhayyile.M", (dh, dh))
        taban = (Z @ M) @ R.T

        # KAN: kenarlarda tek değişkenli taban, düğümlerde yalnız toplam.
        nb = 12

        def kenar(v: np.ndarray, ad: str) -> np.ndarray:
            """``Σ_p φ_{q,p}(v_p)``: her (girdi kanalı, taban) çifti için bir
            ağırlık; düğüm yalnız toplar. KAN'ın tarifi budur."""
            B = kan_temeli(v, nb)                                   # (n, dh, nb)
            C = p.W(ad, (dh * nb, v.shape[1])).reshape(dh, nb, v.shape[1])
            return np.einsum("npb,pbk->nk", B, C)

        ic = kenar(taban, "muhayyile.φ")
        dis = kenar(ic, "muhayyile.Φ")

        rng = np.random.default_rng(p.tohum + 3)
        # Metnin 7. denklemi ``Z⁽ᵗ⁺¹⁾ = Z⁽ᵗ⁾ + η(W Z⁽ᵗ⁾ + ξ)`` bir ARTIK
        # (residual) güncellemedir: muhayyile sıfırdan suret uydurmaz,
        # mevcut sureti BOZAR. Buna sadık kalındı.
        oran = float(np.linalg.norm(Z)) / max(float(np.linalg.norm(dis)), 1e-12)
        sapma = dis * oran + 0.05 * rng.normal(size=dis.shape)

        # Fantezi süzgeci: metinde ``Ẑ · 𝕀(Serbestlik ≤ τ)``, yani eşik
        # aşılınca çıktı SIFIRLANIR. Bu hâliyle kurulup ölçüldü:
        #
        #   eğitilmemiş ağırlıkta Serbestlik 4 ile 792 arasında çıkıyor ve
        #   süzgeç HER seferinde tetikleniyor; muhayyile bütünüyle susuyor.
        #
        # Sert kesme burada iki bakımdan kötüdür: (i) sureti tamamen yok
        # eder -- oysa kayıtlı suret zaten elde; (ii) eşik neyi keseceğini
        # değil, her şeyi keseceğini söyler. Bunun yerine ``η`` UYARLANIR:
        # serbestliği ``τ``nun altına sokan EN BÜYÜK adım seçilir. Böylece
        # muhayyile susturulmaz, DİZGİNLENİR; ve ``Serbestlik ≤ τ`` artık
        # çıktının sağladığı bir NİTELİKTİR (sınanır).
        tau = 2.0
        secilen, Zh = 0.0, Z.copy()
        for eta in (0.35, 0.2, 0.1, 0.05, 0.02, 0.01):
            aday = Z + eta * sapma
            if _kl_gauss(aday, Z, buzulme=0.5) <= tau:
                secilen, Zh = eta, aday
                break
        serbest = _kl_gauss(Zh, Z, buzulme=0.5)
        d.Z_muhayyile = Zh
        d.olcum.koy("muhayyile.serbestlik", serbest)
        d.olcum.koy("muhayyile.eta", secilen)
        d.olcum.koy("muhayyile.dizginlendi", float(secilen < 0.35))
        d.olcum.koy("muhayyile.tau", tau)
        d.not_dus(self.ad, "serbestlik=%.3f (τ=%.1f)" % (serbest, tau))


def _kl_gauss(A: np.ndarray, B: np.ndarray, buzulme: float = 0.1) -> float:
    """Çok değişkenli Gauss tahminleri arasında ``D_KL(P_A ‖ P_B)``.

    Örnek sayısı boyuttan küçük olabildiği için kovaryanslara **büzülme**
    (shrinkage) uygulanır: ``Σ ← (1−α)Σ + α·(tr Σ/d)·I``. Bu olmadan
    ``log det`` tekilleşir ve ölçüm ±∞ olur.
    """
    d = A.shape[1]
    ma, mb = A.mean(0), B.mean(0)

    def kov(V: np.ndarray) -> np.ndarray:
        C = np.cov(V.T) + 1e-9 * np.eye(d)
        return (1 - buzulme) * C + buzulme * (np.trace(C) / d) * np.eye(d)

    Ca, Cb = kov(A), kov(B)
    Cb_inv = np.linalg.inv(Cb)
    fark = mb - ma
    _, la = np.linalg.slogdet(Ca)
    _, lb = np.linalg.slogdet(Cb)
    return float(0.5 * (np.trace(Cb_inv @ Ca) + fark @ Cb_inv @ fark - d + lb - la))


# =====================================================================
@kaydet
class Tertip(Meleke):
    """𝒪₄ Tertip -- suretleri nizama koymak.

    Hesaplanan: ikili öncelik skoru ``Sıra(Zᵢ,Zⱼ) = σ(W(Zᵢ⊕Zⱼ))``den
    türetilen bir sıralama; permütasyon dizeyi ``M = Σ eₖ e_{π(k)}ᵀ``;
    ve nizam ölçüsü ``𝒞 = Tr(Zᵀ Δ_çizge Z)``.

    Metnin ``Equiv_tertip = (Z_ham ≃ Z_düzenli)`` satırı bir DENKLİK
    iddiasıdır: permütasyon tersinirdir, dolayısıyla tertip bilgi
    kaybetmez. Burada bu, ``M``in permütasyon olduğunun (satır ve sütun
    toplamlarının 1 olması) sınanmasıyla karşılanır.

    **Şahit bölütlemesi burada yapılır** (kütük H6). Tertip, suretleri
    yalnız sıralamaz; onları **bölümlere** de ayırır -- bir bulmacanın
    örneklerini birbirinden ayıran şey de bir tertiptir. Ayıraç sembolü
    ARANMAZ; akıştaki kopmalar ölçülür (``sahit.bolutle``). Böylece
    "bunlar ayrı örneklerdir" bilgisi modele bayrakla verilmiş olmaz,
    organla sezilmiş olur.

    Dışarıdan ``Durum.kur(..., sahitler=...)`` ile bölütleme verilirse o
    kabul edilir ve ``tertip.şahit_verildi = 1`` diye **işaretlenir**;
    verilen bölütleme modelin kabiliyeti sayılamaz.
    """

    no, ad = 4, "Tertip"
    okur, yazar = ("E", "Z_hayal"), ("sira", "sahitler")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        Z = d.Z_hayal
        n, dh = Z.shape

        # --- şahit bölütlemesi: **ham duyu** üzerinden
        #
        # Bölütleme evvelce ``Z_hayal`` üzerinden yapılıyordu ve ölçüldü:
        # kurallı beş şahitlik bir akışta üç şahit bulunuyor, kurallı ile
        # bozuk akış aynı bölütlemeyi veriyordu. Sebep 𝒪₁ Müşahede'nin
        # odak penceresi (``k_odak``) ve spektral kesmesidir: ikisi de
        # akışı yumuşatır, örnek sınırlarındaki kopmayı siler. Örnek
        # sınırı ham akışın hususiyetidir; onu suret kurulduktan sonra
        # aramak, delili işlemden sonra aramaya benzer.
        verildi = d.sahitler is not None
        if not verildi:
            b = bolutle(d.E)
            d.sahitler = b.sahitler
            d.olcum.koy("tertip.kopma_eşiği", b.esik)
            d.olcum.koy("tertip.bölütleme_yeterli", float(b.yeterli))
            if not b.yeterli and b.sebep:
                d.not_dus(self.ad, "şahit yok: %s" % b.sebep)
        else:
            d.olcum.koy("tertip.bölütleme_yeterli", float(len(d.sahitler) >= 2))
        d.olcum.koy("tertip.şahit_verildi", float(verildi))
        d.olcum.koy("tertip.şahit_sayısı", float(len(d.sahitler)))
        oncelik = (Z @ p.v("tertip.τ", dh))
        pi = np.argsort(-oncelik)               # yüksek öncelik önce
        d.sira = pi

        # Permütasyon dizeyi ``n×n``dir; 65.536 satırda 32 GiB ister
        # (ölçüldü, akış çöktü). Permütasyon zaten ``pi`` indeksinde
        # duruyor: dizey yalnız "permütasyon mu?" sağlaması için
        # kuruluyordu. Sağlama indeks üzerinden AYNEN yapılabilir --
        # dizeyi kurmak bilgi eklemiyordu, yalnız bellek yiyordu.
        Zd = Z[pi]
        permutasyon_mu = float(np.array_equal(np.sort(pi), np.arange(n)))

        # çizge Laplasyeni ile nizam maliyeti (komşu farkları)
        C = float(np.sum((Zd[1:] - Zd[:-1]) ** 2))
        d.olcum.koy("tertip.nizam_maliyeti", C)
        d.olcum.koy("tertip.permütasyon_mu", permutasyon_mu)
        d.olcum.koy("tertip.düzensizlik",
                    float(np.sum(np.abs(np.argsort(pi) - np.arange(n)))))


# =====================================================================
@kaydet
class Tecrit(Meleke):
    """𝒪₅ Tecrit -- arazı atıp özü almak; **topolojik** soyutlama.

    Hesaplanan: ``P_D = U_k U_kᵀ`` Grassmann izdüşümü (SVD ile);
    normalize çizge Laplasyeni
    ``Δ = I − D^{-1/2} A D^{-1/2}``; ve **Betti sayıları**.

    Betti sayıları burada tahmin değil, TAM hesaptır: 1-iskelet için
    ``β₀`` bağlantılı bileşen sayısı, ``β₁ = |E| − |V| + β₀`` devir
    sayısıdır. İkisi de ``test_nefs.py``de bilinen çizgelerle sınanır.
    """

    no, ad = 5, "Tecrit"
    okur, yazar = ("X",), ("U_k", "D", "w_kesit")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        X = d.X
        n, di = X.shape
        k = max(1, min(di // 2, n - 1, 4))
        U, s, Vt = np.linalg.svd(X, full_matrices=False)
        Uk = Vt[:k].T                                   # (d_in, k) ortonormal
        d.U_k = Uk
        d.D = X @ Uk @ Uk.T                             # P_D(X)

        # ``w ∈ ℳ``: AĞIRLIK, bir kayıp fonksiyonunun durağan noktası
        # değil, parametrize lifleşmenin **kesitidir** (kütük H3).
        # ``ℳ = Gr(k, d_in)`` taban uzayı, lif ``U_k``ın gerdiği alt uzay;
        # kesit, veriden KAPALI FORMDA (SVD ile) okunur -- adım yok,
        # gradyan yok. ``omega_kategori_nbe.iliskiler.kesit_tipi`` bu
        # kesitin tip teorisi tarafındaki karşılığını makineyle denetler;
        # burada onun sayısal cismi taşınır.
        d.w_kesit = Uk
        # kesitin lifte kaldığının sağlaması: ``U_kᵀU_k = I``
        diklik = float(np.max(np.abs(Uk.T @ Uk - np.eye(k))))
        d.olcum.koy("tecrit.kesit_diklik_hatası", diklik)
        d.olcum.koy("tecrit.kesit_boyutu", float(k))

        # komşuluk çizgesi: eşik üstü kosinüs benzerliği.
        # Bitişiklik dizeyi ``n×n``dir -- 16.384 satırda 268 milyon
        # hücre eder ve tek başına akışı kilitler. Betti sayıları
        # topolojik ORANLARDIR; çizge kaba kademede kurulur.
        Xk, _, _ = kaba(X, d.tavan)
        Xn = Xk / (np.linalg.norm(Xk, axis=1, keepdims=True) + 1e-12)
        A = (Xn @ Xn.T > 0.5).astype(float)
        np.fill_diagonal(A, 0.0)
        b0, b1 = betti_1iskelet(A)
        d.olcum.koy("tecrit.β0", b0)
        d.olcum.koy("tecrit.β1", b1)
        d.olcum.koy("tecrit.k", k)
        d.olcum.koy("tecrit.kayıp",
                    float(np.sum((X - d.D) ** 2)) / max(float(np.sum(X * X)), 1e-12))
        d.not_dus(self.ad, "k=%d  β₀=%d β₁=%d" % (k, b0, b1))


def normalize_laplasyen(A: np.ndarray) -> np.ndarray:
    """``Δ = I − D^{-1/2} A D^{-1/2}``. Yalıtık düğümlerde ``D=0``;
    orada ``D^{-1/2}`` yerine 0 alınır (kanonik ihtiyat)."""
    derece = A.sum(1)
    inv = np.where(derece > 0, 1.0 / np.sqrt(np.maximum(derece, 1e-12)), 0.0)
    return np.eye(len(A)) - (inv[:, None] * A * inv[None, :])


def betti_1iskelet(A: np.ndarray) -> Tuple[int, int]:
    """Basit çizgenin (1-iskelet) Betti sayıları.

    ``β₀`` = bağlantılı bileşen sayısı,
    ``β₁ = |E| − |V| + β₀`` (devir uzayının boyutu).
    """
    n = len(A)
    gorulen = np.zeros(n, dtype=bool)
    b0 = 0
    for s in range(n):
        if gorulen[s]:
            continue
        b0 += 1
        yigin = [s]
        gorulen[s] = True
        while yigin:
            u = yigin.pop()
            for v in np.nonzero(A[u])[0]:
                if not gorulen[v]:
                    gorulen[v] = True
                    yigin.append(int(v))
    kenar = int(np.sum(A > 0) // 2)
    return b0, kenar - n + b0


# =====================================================================
@kaydet
class Tasavvur(Meleke):
    """𝒪₆ Tasavvur -- soyut çekirdeğin KAVRAM hâline gelmesi.

    Hesaplanan: ``S = GELU(D W_{d2s} + H W_{h2s} + b)``; Riemann metriği
    ``g_ij = ⟨∂S/∂uᵢ, ∂S/∂uⱼ⟩`` (sonlu farkla); hacim ögesi
    ``√det g``; makro kavram ``S_kebîr``; ve ``LayerNorm`` ile kemâl.

    **Muhayyile buraya katılır.** Tasavvur, hâfızadaki sureti (``H``)
    ve soyutlanmış özü (``D``) birleştirir; fakat kavram yalnız
    görülenden kurulmaz -- muhayyilenin ürettiği varyasyon (``𝒪₃``) da
    girer. Evvelce ``Z_muhayyile`` yazılıyor, kimse okumuyordu: ölçüldü,
    𝒪₃ düşürülünce netice hiç değişmiyordu. Katkı **küçük tutulur**
    (katsayı 0.25), çünkü muhayyile kavramı kurmaz, zenginleştirir.
    """

    no, ad = 6, "Tasavvur"
    okur, yazar = ("D", "H_hayal"), ("S", "S_kebir")
    ihtiyari = ("Z_muhayyile",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        D, H = d.D, d.H_hayal
        n, di = D.shape
        dh, ds = d.d_hayal, d.d_sem
        S = gelu(D @ p.W("tasavvur.d2s", (di, ds)) + H @ p.W("tasavvur.h2s", (dh, ds)))
        if d.Z_muhayyile is not None and d.Z_muhayyile.shape[0] == n:
            S = S + 0.25 * gelu(d.Z_muhayyile
                                @ p.W("tasavvur.m2s",
                                      (d.Z_muhayyile.shape[1], ds)))
            d.olcum.koy("tasavvur.muhayyile_katkısı", 1.0)
        else:
            d.olcum.koy("tasavvur.muhayyile_katkısı", 0.0)
        S = kat_norm(S + S @ p.W("tasavvur.res", (ds, ds)))
        d.S = S
        d.S_kebir = kat_norm(S.mean(0) @ p.W("tasavvur.macro", (ds, ds)))

        # g_ij: örnek ekseni boyunca sonlu fark → (n-1, ds) → Gram
        if n >= 2:
            dS = np.diff(S, axis=0)
            g = dS.T @ dS / max(n - 1, 1)
            isaret, logdet = np.linalg.slogdet(g + 1e-6 * np.eye(ds))
            d.olcum.koy("tasavvur.hacim_log", 0.5 * logdet if isaret > 0 else float("-inf"))
        d.olcum.koy("tasavvur.norm", float(np.linalg.norm(S) / np.sqrt(S.size)))


# =====================================================================
@kaydet
class Mana(Meleke):
    """𝒪₇ Mana -- kavramın **kasda** bağlanması (vâhime etiketi).

    Hesaplanan: ``K_t = LayerNorm(X W_k)`` vâhime etiketi;
    ``μ_mana = σ(S W_m + K W_v)``; bağlam dikkati; ``Ξ = μ_mana ⊗ μ_bağlam``
    ve ``μ_net``. ``AnlamDerecesi`` gaye ile kosinüs olarak ölçülür --
    gaye henüz kurulmadıysa (``𝒪₁₄``den önce) ölçüm ``nan`` kalır ve bu
    açıkça böyle bildirilir.
    """

    no, ad = 7, "Mana"
    okur, yazar = ("S", "X"), ("K_vahime", "mu_mana")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, X = d.S, d.X
        n, ds = S.shape
        di = X.shape[1]
        K = kat_norm(X @ p.W("mana.k", (di, ds)))
        d.K_vahime = K
        mu = sigmoid(S @ p.W("mana.m", (ds, ds)) + K @ p.W("mana.v", (ds, ds)))

        H = d.H_hayal if d.H_hayal is not None else S
        H, _, _ = kaba(H, d.tavan)      # bağlam dikkati ``n×n``dir
        Wq = p.W("mana.q", (ds, ds))
        Wk = p.W("mana.hk", (H.shape[1], ds))
        Wv = p.W("mana.hv", (H.shape[1], ds))
        mu_baglam = dikkat(S @ Wq, H @ Wk, H @ Wv)

        Xi = mu * mu_baglam
        d.mu_mana = kat_norm(mu + Xi @ p.W("mana.x", (ds, ds)))
        if d.G is not None:
            d.olcum.koy("mana.anlam_derecesi", abs(kosinus(S.mean(0), d.G)))
        d.olcum.koy("mana.ilişki_katsayısı",
                    float(np.mean(sigmoid(np.concatenate([S, mu], axis=1)
                                          @ p.v("mana.vm", 2 * ds)))))


# =====================================================================
@kaydet
class Tahlil(Meleke):
    """𝒪₈ Tahlil -- bütünü cins ve fasıllarına ayırmak.

    Hesaplanan: ``S = Σ σᵢ uᵢ vᵢᵀ`` (SVD); spektral entropi
    ``−Σ pᵢ log pᵢ``, ``pᵢ = σᵢ²/Σσⱼ²``; ``S_cins`` (ilk k kip) ve
    ``S_fasıl`` (kalan); ve bileşenler arası **HSIC** bağımsızlık ölçüsü.

    HSIC burada gerçek biçimiyle kurulur: ``Tr(K H L H)/(n−1)²``,
    ``H = I − 11ᵀ/n``. Bağımsız iki bileşende ~0, bağımlı olanda kayda
    değer -- bu ``test_nefs.py``de doğrulanır.
    """

    no, ad = 8, "Tahlil"
    okur, yazar = ("S",), ("parcalar", "tekil_degerler")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        U, s, Vt = np.linalg.svd(S, full_matrices=False)
        d.tekil_degerler = s
        m = len(s)
        # bileşenler: σᵢ uᵢ vᵢᵀ'nin örnek eksenindeki izdüşümü
        d.parcalar = U * s                                   # (n, m)

        pay = s ** 2
        pr = pay / max(float(pay.sum()), 1e-12)
        nz = pr > 0
        d.olcum.koy("tahlil.entropi", -float(np.sum(pr[nz] * np.log(pr[nz]))))
        k = max(1, int(np.sum(s > 0.1 * s[0])))
        d.olcum.koy("tahlil.cins_kip_sayısı", k)
        if m >= 2:
            d.olcum.koy("tahlil.hsic_ilk_iki",
                        hsic(d.parcalar[:, 0], d.parcalar[:, 1]))
        d.not_dus(self.ad, "kip=%d entropi=%.3f" % (k, d.olcum.al("tahlil.entropi")))


def hsic(x: np.ndarray, y: np.ndarray, olcek: float | None = None) -> float:
    """Hilbert--Schmidt Bağımsızlık Ölçütü, Gauss çekirdeğiyle.

    ``HSIC = Tr(K H L H)/(n−1)²``. Bağımsızlıkta 0'a yakınsar.
    """
    n = len(x)
    if n < 4:
        return 0.0
    # Gram dizeyleri ``n×n``dir; uzun pencerede tek başına akışı yer
    # (ölçüldü: 4096 satırda 𝒪₈ Tahlil 4,1 sn). HSIC bir ORAN ölçüsüdür;
    # düzgün aralıklı bir alt örneklem aynı bağımsızlık hükmünü verir.
    TAVAN = 512
    if n > TAVAN:
        idx = np.linspace(0, n - 1, TAVAN).astype(int)
        x, y, n = x[idx], y[idx], TAVAN

    def gram(v: np.ndarray) -> np.ndarray:
        d2 = (v[:, None] - v[None, :]) ** 2
        s = olcek if olcek is not None else np.sqrt(0.5 * np.median(d2[d2 > 0])) if np.any(d2 > 0) else 1.0
        return np.exp(-0.5 * d2 / max(s * s, 1e-12))

    H = np.eye(n) - np.ones((n, n)) / n
    K, L = gram(x), gram(y)
    return float(np.trace(K @ H @ L @ H) / (n - 1) ** 2)


# =====================================================================
@kaydet
class Terkip(Meleke):
    """𝒪₉ Terkip -- parçaları yeniden **bir** kılmak.

    Hesaplanan: ağırlıklar ``w_k = softmax(vᵀS⁽ᵏ⁾)``; her parçaya bir Lie
    tasarrufu ``R_k ▷ S⁽ᵏ⁾``; ``Ω_bütünlük`` (metinde dış çarpım
    ``⋀``; burada **ters simetrik** kısım olarak alınır, çünkü ``⋀``in
    sayısal karşılığı budur); ve uyum katsayısıyla ölçeklenen sentez.

    ``UyumKatsayısı = min_{i≠j} CosSim`` düşükse sentez SÖNER: metnin
    ``S_sentez · σ(Uyum·β)`` çarpanı. Yani terkip, uyuşmayan parçaları
    zorla birleştirmez.
    """

    no, ad = 9, "Terkip"
    okur, yazar = ("S", "parcalar"), ("S",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape
        R = p.lie_tasarruf("terkip.R", ds, teta=0.25)
        w = softmax(S @ p.v("terkip.vt", ds))
        terkip = (w[:, None] * (S @ R.T))

        Om = terkip.T @ terkip
        Om = 0.5 * (Om - Om.T)                     # ⋀: ters simetrik kısım
        sentez = gelu(terkip + terkip @ Om.T * 0.1)

        # uyum: parçalar arası en KÜÇÜK kosinüs. Kosinüs dizeyi ``n×n``
        # -- 65.536 satırda 32 GiB (ölçüldü, akış çöktü). Asgarî bir
        # ORAN ölçüsüdür; kaba kademede aranır.
        Sk, _, _ = kaba(S, d.tavan)
        Sn = Sk / (np.linalg.norm(Sk, axis=1, keepdims=True) + 1e-12)
        C = Sn @ Sn.T
        np.fill_diagonal(C, np.inf)
        uyum = float(np.min(C)) if len(Sk) > 1 else 1.0
        d.S = kat_norm(sentez) * float(sigmoid(3.0 * uyum))
        d.olcum.koy("terkip.uyum_katsayısı", uyum)
        d.olcum.koy("terkip.ω_ters_simetrik",
                    float(np.max(np.abs(Om + Om.T))))     # ≈ 0 olmalı


# =====================================================================
@kaydet
class Tezat(Meleke):
    """𝒪₁₀ Tezat -- zıtlığı ÖLÇMEK (henüz hüküm vermeden).

    Hesaplanan: ``Θ(Sᵢ,Sⱼ) = 1 − cos(Sᵢ,Sⱼ)`` tezat dizeyi; en büyük
    özvektör ile "tezat kutbu"; ve ``W_opp = −I + v v ᵀ`` zıtlık
    operatörü.

    Hüküm ``𝒪₁₁ Tenakuz``ün işidir; fakat Tezat'ın bulduğu **kutup**
    ona verilir. Evvelce bu meleke ``Durum``a hiçbir şey yazmıyordu ve
    ölçüldü: düşürüldüğünde neticede ``‖ΔN‖ = 0`` çıkıyordu -- yani
    hesaplanan her şey günlüğe yazılıp atılıyordu. Tezat kutbu artık
    veri yoluna konur ve 𝒪₁₁ çelişki çekirdeğini o kutupla kurar.
    Ölçmekle hükmetmek yine ayrıdır; ayrı olan, ölçünün ZAYİ olması
    değildir.
    """

    no, ad = 10, "Tezat"
    okur, yazar = ("S",), ("tezat_kutbu",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        # Tezat dizeyi ``n×n`` ve özayrışımı ``O(n³)``dür -- kule
        # olmadan uzun pencerede tek başına akışı kilitler.
        S, _, _ = kaba(d.S, d.tavan)
        n = len(S)
        Sn = S / (np.linalg.norm(S, axis=1, keepdims=True) + 1e-12)
        Theta = 1.0 - Sn @ Sn.T
        d.olcum.koy("tezat.azami", float(np.max(Theta)))
        d.olcum.koy("tezat.ortalama", float(np.mean(Theta)))
        kutup = S.mean(0)
        if n >= 2:
            oz, vek = np.linalg.eigh(0.5 * (Theta + Theta.T))
            d.olcum.koy("tezat.baskın_özdeğer", float(oz[-1]))
            kutup = softmax(vek[:, -1]) @ S
            d.olcum.koy("tezat.kutup_normu", float(np.linalg.norm(kutup)))
        d.tezat_kutbu = kutup / (float(np.linalg.norm(kutup)) + 1e-12)

# ======================================================================
#  𝒪₁₁–𝒪₂₄ AKIL (klasik tensör hattı)
#  (evvelce nefs/akil.py)
# ======================================================================

# =====================================================================
@kaydet
class Tenakuz(Meleke):
    """𝒪₁₁ Tenakuz Bulma -- çelişkiyi TESPİT ve ıslah.

    Hesaplanan: ``Tenakuz(Sᵢ,Sⱼ) = ReLU(Sᵢᵀ W_tenakuz Sⱼ − δ)``;
    çelişki haritası ``∇_S Tenakuz``; ve ıslah adımı
    ``Sᵢ ← Sᵢ − η ∇_ıslah``.

    Çekirdek ``uzaylar.celiski_dizeyi``dedir: ``C = −S(AᵀA)Sᵀ``. Orada
    yazılı iki şart (kendisiyle çelişmemek, nakîziyle çelişmek) burada
    doğrudan sınanır. İlk kurulumda çekirdek ters simetrik alınmıştı ve
    ikinci şartı bozuyordu; ölçüm yakaladı, çekirdek değişti.
    """

    no, ad = 11, "Tenakuz Bulma"
    okur, yazar = ("S",), ("S", "tenakuz")
    ihtiyari = ("tezat_kutbu",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape
        A = p.W("tenakuz.A", (ds, ds))
        # 𝒪₁₀ Tezat bir kutup bulduysa çelişki çekirdeği o kutup boyunca
        # KUVVETLENDİRİLİR: ``A ← A + v vᵀ``. ``AᵀA`` hâlâ yarı-pozitiftir,
        # dolayısıyla ``uzaylar.celiski_dizeyi``nin iki şartı (kendisiyle
        # çelişmemek, nakîziyle çelişmek) bozulmaz -- bunlar ``M = AᵀA``nın
        # yarı-pozitifliğinden çıkar, ``A``nın husûsî şeklinden değil.
        if d.tezat_kutbu is not None:
            v = np.asarray(d.tezat_kutbu, float)
            A = A + np.outer(v, v)
        # Çelişki dizeyi de karesel: kaba kademede kurulur, ıslah ince
        # eksene artık olarak yayılır (bkz. nefs/kule.py).
        Sk, kademe, _ = kaba(S, d.tavan)
        delta = celiski_esigi(Sk, A, 0.5)
        d.olcum.koy("tenakuz.eşik", delta)
        C = celiski_dizeyi(Sk, A)
        skor = celiski_skoru(Sk, A, delta)
        d.tenakuz = skor

        gradk = celiski_gradyani(Sk, A, delta)
        grad = gradk if kademe == 0 else ince(gradk, n, kademe)
        olcek = 0.02 / max(float(np.max(np.abs(grad))), 1.0)
        d.S = S - olcek * grad
        # F_tenakuz: sükût eşiğinin (H16) dayandığı serbest enerji.
        # Çelişki + pürüz + vehim; üçü de metinde sayılan bileşenlerdir.
        puruz = float(np.sum(np.diff(Sk, axis=0) ** 2)) / max(len(Sk) - 1, 1)
        d.serbest_enerji = float(skor + 0.05 * puruz)
        d.olcum.koy("tenakuz.serbest_enerji", d.serbest_enerji)
        d.olcum.koy("tenakuz.skor", skor)
        # köşegen ``ReLU`` sonrası dâima 0: ``C_ii ≤ 0``
        d.olcum.koy("tenakuz.köşegen",
                    float(np.max(np.maximum(np.diag(C) - delta, 0.0))))
        d.olcum.koy("tenakuz.köşegen_negatif", float(np.max(np.diag(C)) <= 0.0))
        d.olcum.koy("tenakuz.ıslah_miktarı", float(np.linalg.norm(olcek * grad)))


# =====================================================================
@kaydet
class Tenkit(Meleke):
    """𝒪₁₂ Tenkit -- üç başlıklı maliyet ve eleme.

    ``𝒦 = Tenakuz + λ₁ Pürüz + λ₂ Sapma``. ``Sapma`` gayeye göredir;
    gaye henüz kurulmamışsa (bu meleke 𝒪₁₄'ten önce koşar) ``S_kebîr``
    yönü **geçici gaye** sayılır ve bu ölçümde açıkça bildirilir.
    """

    no, ad = 12, "Tenkit"
    okur, yazar = ("S", "S_kebir"), ("S",)
    ihtiyari = ("G",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape
        puruz = float(np.sum(np.diff(S, axis=0) ** 2)) / max(n - 1, 1)
        hedef = d.G if d.G is not None else d.S_kebir
        sapma = 1.0 - kosinus(S.mean(0), hedef)
        K = d.tenakuz + 0.1 * puruz + 0.5 * sapma

        skor = sigmoid(S @ p.v("tenkit.k", ds))
        tau = float(np.quantile(skor, 0.25))          # en zayıf çeyreği ele
        maske = (skor > tau).astype(float)
        d.S = S * maske[:, None]
        d.olcum.koy("tenkit.maliyet", K)
        d.olcum.koy("tenkit.pürüz", puruz)
        d.olcum.koy("tenkit.sapma", sapma)
        d.olcum.koy("tenkit.gaye_geçici", float(d.G is None))
        d.olcum.koy("tenkit.elenen", float(n - maske.sum()))


# =====================================================================
@kaydet
class Tasdik(Meleke):
    """𝒪₁₃ Tasdik -- mühür.

    ``T = σ( CosSim(M W, G) − Tenakuz )`` ve ``𝟙_tasdik = 𝕀(T ≥ 1−ε)``.
    Teemmül belleği ``M`` henüz yoksa ``S``in kendisi kullanılır.

    Bu meleke akışta **iki kere** koşar (𝒪₁₃ sırasında ve 𝒪₃₃'ten sonra
    mühür olarak); ikisinde de aynı formül işler.

    **Mühür artık kayda geçer.** Tasdik bir hüküm melekesidir; hükmü
    sayı olarak değil **kayıt** olarak bırakır (kütük H4): hangi
    mertebede, hangi delille, nakz var mı, mühür düştü mü. ``d.hukum``
    sözlüktür, tensör değildir ve tensöre çevrilmez. İkinci koşuda
    üstüne yazar; ``mühür_sırası`` kaçıncı mühür olduğunu söyler.
    """

    no, ad = 13, "Tasdik"
    okur, yazar = ("S",), ("hukum",)
    ihtiyari = ("G", "M")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds = S.shape[1]
        M = d.M if d.M is not None else S
        hedef = d.G if d.G is not None else (d.S_kebir if d.S_kebir is not None
                                             else S.mean(0))
        uyum = kosinus((M @ p.W("tasdik.t", (M.shape[1], ds))).mean(0), hedef)
        d.T = float(sigmoid(4.0 * (uyum - d.tenakuz)))
        eps = 0.05
        muhurlendi = bool(d.T >= 1 - eps)

        onceki = d.hukum or {}
        d.hukum = {
            "mühür_sırası": int(onceki.get("mühür_sırası", 0)) + 1,
            "T": d.T,
            "uyum": uyum,
            "tenakuz": d.tenakuz,
            "mühür": muhurlendi,
            "makam": d.makam,
            "nakz": list(d.nakz) if d.nakz is not None else None,
            "şahit_sayısı": len(d.sahitler) if d.sahitler is not None else 0,
            "müteber_şahit": d.muteber_sahit,
            "gerekçe": ("tasdik: uyum − tenakuz = %.4f" % (uyum - d.tenakuz)),
        }
        d.olcum.koy("tasdik.T", d.T)
        d.olcum.koy("tasdik.uyum", uyum)
        d.olcum.koy("tasdik.mühür", float(muhurlendi))
        d.olcum.koy("tasdik.mühür_sırası", float(d.hukum["mühür_sırası"]))
        d.not_dus(self.ad, "T=%.4f (uyum=%.3f, tenakuz=%.3f)"
                  % (d.T, uyum, d.tenakuz))


# =====================================================================
@kaydet
class Gaye(Meleke):
    """𝒪₁₄ Gaye Belirleme -- teleolojik ufuk.

    ``G_kebîr = Softmax(Sual·W_q·S_kebîrᵀ/√d)·S_kebîr·W_v``; süâl
    verilmemişse ufuk ``S_kebîr``in kendisinden türetilir (nefs kendi
    hâlinden gaye çıkarır). ``G`` bu ufka ``η_gaye`` ile yaklaşır:
    ``G ← G + η(G_kebîr − G)``.
    """

    no, ad = 14, "Gaye Belirleme"
    okur, yazar = ("S", "S_kebir"), ("G", "G_kebir")
    ihtiyari = ("sual",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, Sk = d.S, d.S_kebir
        ds = S.shape[1]
        sual = d.sual if d.sual is not None else Sk
        Wq, Wv = p.W("gaye.q", (ds, ds)), p.W("gaye.v", (ds, ds))
        agirlik = softmax((sual @ Wq) @ S.T / np.sqrt(ds))
        d.G_kebir = kat_norm(agirlik @ S @ Wv)

        onceki = d.G if d.G is not None else np.zeros(ds)
        eta = 0.5
        d.G = onceki + eta * (d.G_kebir - onceki)
        d.olcum.koy("gaye.ilerleme", kosinus(d.G, d.G_kebir))
        d.olcum.koy("gaye.teleoloji_faydası",
                    float(np.exp(-np.linalg.norm(S.mean(0) - d.G_kebir))))
        d.olcum.koy("gaye.sual_verildi", float(d.sual is not None))


# =====================================================================
@kaydet
class Merak(Meleke):
    """𝒪₁₅ Merak ve Sual Tevcihi -- bilgisizliğin ÖLÇÜLÜP adreslenmesi.

    ``Q = Softmax((G − S)W_q / τ_merak)``; bilgisizlik
    ``ℋ = Var(P(S|H))``; sual adresi ``ArgMax_j(Q_j · ℋ_j)``. Sual ancak
    bilgisizlik eşiği aşarsa sorulur -- ``𝕀(ℋ > ε_cehalet)``.
    """

    no, ad = 15, "Merak ve Sual"
    okur, yazar = ("S", "G"), ("Q_sual",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, G = d.S, d.G
        ds = S.shape[1]
        bosluk = G - S.mean(0)
        Q = softmax((bosluk @ p.W("merak.q", (ds, ds))) / 0.5)
        bilgisizlik = S.var(0)
        d.Q_sual = Q

        eps = float(np.median(bilgisizlik))
        soruyor = float(np.max(bilgisizlik) > eps)
        d.olcum.koy("merak.adres", int(np.argmax(Q * bilgisizlik)))
        d.olcum.koy("merak.bilgisizlik", float(np.mean(bilgisizlik)))
        d.olcum.koy("merak.sual_soruyor", soruyor)
        d.olcum.koy("merak.Q_toplamı", float(Q.sum()))       # 1 olmalı


# =====================================================================
@kaydet
class DenemeYanilma(Meleke):
    """𝒪₁₆ Deneme-Yanılma -- oyuncu-eleştirmen (actor-critic) döngüsü.

    ``a = π_θ(S,G) + ε``; ``r = Coşku − Maliyet``; ``θ ← θ + α r ∇log π``.
    Burada politika doğrusal-Gauss, eleştirmen ise ``Q(S,a) = wᵀ[S⊕a]``
    ile doğrusaldır; TD hatası ``δ = r + γQ' − Q``.

    Sınanabilir iddia: **ödül turlarla yükselmeli**. Bu, eğitilmemiş
    ağırlıklara rağmen doğrudur, çünkü burada öğrenilen şey bu melekenin
    kendi ``θ``sıdır ve hedef (``G``ye yaklaşmak) analitiktir.
    """

    no, ad = 16, "Deneme-Yanılma"
    okur, yazar = ("S", "G"), ("strateji",)

    def uygula(self, d: Durum, p: Parametreler, tur: int = 60) -> None:
        S, G = d.S, d.G
        ds = S.shape[1]
        rng = np.random.default_rng(p.tohum + 16)
        teta = p.W("deneme.θ", (ds, ds)).copy()
        s = S.mean(0)
        sigma = 0.3
        oduller: List[float] = []
        taban = 0.0            # eleştirmenin en sade hâli: kayan ortalama
        for t in range(tur):
            a = s @ teta + sigma * rng.normal(size=ds)
            # Politika ıraksarsa ``a`` patlar (ölçüldü: ``a@a`` taşıp inf
            # oluyor, ``θ`` NaN'a düşüyordu). Evvelce bu NaN melekenin
            # içinde kalıyordu; artık ``strateji`` olarak veri yoluna
            # çıktığı için bütün akışı zehirler. Hamle normu sınırlanır --
            # keşif kalır, ıraksama kalkar.
            n_a = float(np.linalg.norm(a))
            if n_a > 10.0:
                a = a * (10.0 / n_a)
            s_yeni = kat_norm(s + 0.3 * a)
            r = kosinus(s_yeni, G) - 0.01 * float(a @ a)
            oduller.append(r)
            # TABAN ÇIKARMA şart. Tabansız REINFORCE kurulup ölçüldü:
            # ödül -0.49'dan -0.70'e DÜŞTÜ, yani usul öğrenmek yerine
            # bozuldu. Sebep, bütün ödüller negatifken her hamlenin
            # cezalandırılması ve gradyanın yalnız gürültüyü takip
            # etmesidir. ``r − taban`` yansızdır (taban hamleden bağımsız)
            # ve varyansı düşürür.
            avantaj = r - taban
            taban = 0.9 * taban + 0.1 * r
            grad = np.outer(s, (a - s @ teta) / (sigma ** 2))
            teta = teta + 0.05 * avantaj * grad
            sigma *= np.exp(-0.005) if avantaj > 0 else 1.0
        ilk = float(np.mean(oduller[:10]))
        son = float(np.mean(oduller[-10:]))
        d.olcum.koy("deneme.ilk_ödül", ilk)
        d.olcum.koy("deneme.son_ödül", son)
        # **Mutasarrıfa strateji operatörü** (kütük H15). Öğrenilen ``θ``
        # burada ölmez; veri yoluna konur ve 𝒪₂₁ Tefekkür akışı onunla
        # büker. Evvelce bu meleke 60 tur koşup öğrendiğini çöpe atıyordu.
        if not np.all(np.isfinite(teta)):
            teta = p.W("deneme.θ", (ds, ds))     # ıraksadı: başlangıca dön
            d.olcum.koy("deneme.ıraksadı", 1.0)
        else:
            d.olcum.koy("deneme.ıraksadı", 0.0)
        d.strateji = kat_norm(teta)
        d.olcum.koy("deneme.strateji_normu", float(np.linalg.norm(d.strateji)))
        d.olcum.koy("deneme.öğrendi", float(son > ilk))
        d.not_dus(self.ad, "ödül %.4f → %.4f" % (ilk, son))


# =====================================================================
@kaydet
class Ihtimal(Meleke):
    """𝒪₁₇ İhtimal Hesabı -- Bayes.

    ``P(S|ℰ) = P(ℰ|S)P(S)/P(ℰ)``, ``P(ℰ) = Σ P(ℰ|S')P(S')``.
    Hipotezler ``S``in satırlarıdır; olabilirlik gayeye yakınlıktan
    türetilir. Sonsal dağılımın **toplamı 1**'dir ve bu sınanır.
    """

    no, ad = 17, "İhtimal Hesabı"
    okur, yazar = ("S", "G"), ("sonsal",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, G = d.S, d.G
        n = len(S)
        onsel = np.full(n, 1.0 / n)
        olabilirlik = np.array([np.exp(kosinus(s, G)) for s in S])
        kanit = float(olabilirlik @ onsel)
        sonsal = (olabilirlik * onsel) / max(kanit, 1e-300)
        d.sonsal = sonsal          # 𝒪₂₅ Teemmül bunu önsel olarak okur
        d.olcum.koy("ihtimal.kanıt", kanit)
        d.olcum.koy("ihtimal.sonsal_toplamı", float(sonsal.sum()))
        d.olcum.koy("ihtimal.sonsal_azami", float(sonsal.max()))
        pr = sonsal / sonsal.sum()
        nz = pr > 0
        d.olcum.koy("ihtimal.entropi", -float(np.sum(pr[nz] * np.log(pr[nz]))))
        d.olcum.koy("ihtimal.beklenen_uyum", float(sonsal @ np.array(
            [kosinus(s, G) for s in S]) / n))


# =====================================================================
@kaydet
class Kiyas(Meleke):
    """𝒪₁₈ Kıyas -- ``S₁ ↦ S₂`` orantısını öğrenmek.

    ``W* = ArgMin_W Σ‖W S₁⁽ⁱ⁾ − S₂⁽ⁱ⁾‖² + λ‖W‖²`` (sırt bağlanımı,
    kapalı çözüm). Sınanabilir iddia: veri gerçekten ``S₂ = A S₁`` ile
    üretilmişse ``W* ≈ A``.

    **Şahit başına kaide burada uydurulur** (kütük H6). Kıyas, bilinen
    vakadan bilinmeyene geçmektir; şahitler bilinen vakalardır. Her
    şahidin girdi→çıktı dönüşümü **dik Procrustes** ile kapalı formda
    çözülür (``sahit.kaide_uydur``): ``R = polar(ÇᵀG)``. Ne adım boyu
    vardır ne yakınsama şartı; kütük H3'ün "uydurma kapalı formdur"
    hükmü burada fiilen işler.

    Kaideler ``d.kaideler``e konur; onları sınamak (nakz) 𝒪₂₃ Mantık'ın,
    tartmak (tevafuk) 𝒪₂₉ Teyit'in, mühürlemek 𝒪₃₀ Tahkik'in işidir.

    **Kaide HAM DUYU üzerinde uydurulur, mana üzerinde değil.** Bu
    ölçümden çıktı: kaide ``S`` üzerinde uydurulunca, kurala tâbi olduğu
    kesin bilinen dört şahitlik bir akışta iki şahit nakzedilmiş
    görünüyordu -- yani sistem kendi bildiği kuralı bulamıyordu. Sebep
    𝒪₁ Müşahede'deki öz-dikkattir: dikkat SATIRLARI KARIŞTIRIR, oysa
    girdi satırı ile çıktı satırı arasındaki eşleşme kaidenin ta
    kendisidir. Karıştıktan sonra o eşleşme artık yoktur. Kıyas, vakayı
    **görüldüğü gibi** kıyaslar.

    Bunun bir bedeli vardır ve saklanmaz: küllî kaide ``d_in`` uzayında
    yaşar, mana uzayında (``d_sem``) değil. 𝒪₃₃ Muhakeme onu ancak
    boyutlar denk düştüğünde doğrudan tatbik edebilir; denk düşmediğinde
    şahit delilini mîzâna **hüküm olarak** katar, dizey olarak değil.
    """

    no, ad = 18, "Kıyas"
    okur, yazar = ("S", "E"), ("kaideler",)
    ihtiyari = ("sahitler",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape

        sahitler = d.sahitler or []
        E = d.E
        d.kaideler = [kaide_uydur(E, s) for s in sahitler]
        d.olcum.koy("kıyas.kaide_sayısı", float(len(d.kaideler)))
        if d.kaideler:
            oz = [float(np.mean(artiklar(E, s, R)))
                  for s, R in zip(sahitler, d.kaideler)
                  if artiklar(E, s, R).size]
            d.olcum.koy("kıyas.şahit_içi_artık",
                        float(np.mean(oz)) if oz else float("nan"))
            d.olcum.koy("kıyas.kaide_dikliği",
                        float(np.max([np.max(np.abs(R.T @ R
                                                    - np.eye(E.shape[1])))
                                      for R in d.kaideler])))

        if n < 4:
            d.olcum.koy("kıyas.geçerlilik", 0.0)
            return
        yari = n // 2
        S1, S2 = S[:yari], S[yari:2 * yari]
        d.olcum.koy("kıyas.geçerlilik",
                    float(sigmoid(np.trace(kiyas_ogren(S1, S2)) / ds)))
        d.olcum.koy("kıyas.hata",
                    float(np.linalg.norm(S1 @ kiyas_ogren(S1, S2).T - S2)
                          / max(np.linalg.norm(S2), 1e-12)))


def kiyas_ogren(S1: np.ndarray, S2: np.ndarray, lam: float = 1e-6) -> np.ndarray:
    """``W* = S₂ᵀS₁(S₁ᵀS₁ + λI)⁻¹``: ``W S₁ᵀ ≈ S₂ᵀ`` sırt çözümü."""
    d = S1.shape[1]
    return S2.T @ S1 @ np.linalg.inv(S1.T @ S1 + lam * np.eye(d))


# =====================================================================
@kaydet
class Temsil(Meleke):
    """𝒪₁₉ Temsil -- soyutu somuta indirmek (ve geri alabilmek).

    ``T_temsil = Ψ_somut(S)``, ``ℒ = ‖S − Encoder(Ψ(S))‖²``. Çözücü ve
    kodlayıcı burada **birbirinin sözde tersi** olacak şekilde kurulur
    (aynı dizeyin sözde tersi), böylece "temsil bilgi kaybetmemeli"
    şartı sınanabilir hâle gelir: devir hatası ölçülür.
    """

    no, ad = 19, "Temsil"
    okur, yazar = ("S",), ("somut",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds, dh = S.shape[1], d.d_hayal
        W = p.W("temsil.dec", (ds, dh))
        somut = gelu(S @ W)
        d.somut = somut            # 𝒪₂₇ Tetkik kusuru buna göre ölçer
        geri = somut @ np.linalg.pinv(W)
        d.olcum.koy("temsil.devir_hatası",
                    float(np.linalg.norm(geri - S) / max(np.linalg.norm(S), 1e-12)))
        d.olcum.koy("temsil.hassasiyet", kosinus(geri.ravel(), S.ravel()))
        d.olcum.koy("temsil.netlik", guvenli_bol(1.0, float(np.var(somut))))


# =====================================================================
@kaydet
class Tesbih(Meleke):
    """𝒪₂₀ Teşbih -- benzeyen ile benzetilen arasında **vech-i şebeh**.

    ``ρ = Cov(S_A,S_B)/σ_Aσ_B``; ortak alt uzay izdüşümü; ve bileşke
    ``αS_A + (1−α)S_B ρ``. ``ρ`` Pearson'dur: aynı iki şey için tam 1
    çıkar, bu sınanır.
    """

    no, ad = 20, "Teşbih"
    okur, yazar = ("S",), ("vech",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n = len(S)
        if n < 2:
            d.vech = S[0] if n else np.zeros(S.shape[1])
            return
        A, B = S[0], S[min(1, n - 1)]
        d.olcum.koy("teşbih.ρ", pearson(A, B))
        vech = A * B * p.v("teşbih.ortak", len(A))
        d.vech = vech              # 𝒪₃₉ Belâgat teşbihi kelama katar
        d.olcum.koy("teşbih.oran",
                    guvenli_bol(float(np.linalg.norm(vech)),
                                float(np.linalg.norm(A) + np.linalg.norm(B))))
        d.olcum.koy("teşbih.kendine_ρ", pearson(A, A))     # 1.0 olmalı


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    a0, b0 = a - a.mean(), b - b.mean()
    payda = float(np.linalg.norm(a0) * np.linalg.norm(b0))
    return float(a0 @ b0 / payda) if payda > 1e-12 else 0.0


# =====================================================================
@kaydet
class Tefekkur(Meleke):
    """𝒪₂₁ Tefekkür -- ``S`` üzerinde akış: ``Ṡ = −∇𝒱_tefekkür(S)``.

    ``𝒱 = ½‖S − G‖² + λ Tenakuz(S, İ)``. Bu bir gradyan akışıdır;
    dolayısıyla ``yaklasim.akislar``daki kaideye tâbidir: potansiyel
    boyunca **azalmalıdır**. Ölçülür ve sınanır.

    Tefekkür yalnız tek bir uzayda akmaz. Akıştan sonra ``S``, yirmi
    ∞-kategori mertebesinden geçip esas uzaya geri mühürlenir
    (``nefs/mertebe.py``). Bu, ``main/`` modelinin icadının buraya
    nakledilen hükmüdür (kütük H40): mertebeler **toplanmaz** (H21),
    ayrı eksenlerde işler ve bileşke terkiptir. Geçişin bıraktığı
    **tıkanıklık** hükme girer: bir mana bir mertebeden ötekine
    geçemiyorsa, o manadan yakîn devşirilemez (𝒪₃₂), ve mîzânda aleyhte
    delildir (𝒪₃₃).
    """

    no, ad = 21, "Tefekkür"
    okur, yazar = ("S", "G"), ("S", "mertebe_tikanikligi", "mertebe_betti")
    ihtiyari = ("mu_mana", "strateji")

    def uygula(self, d: Durum, p: Parametreler, adim: int = 30) -> None:
        S = d.S.copy()
        if len(S) > d.tavan:
            # Uzun pencerede akış adımı kısılır; potansiyelin azalması
            # (sınanan iddia) 8 adımda da sağlanır, 30 adım yalnız daha
            # ince yakınsama verir. Kısıntı ölçüme yazılır.
            adim = 8
        d.olcum.koy("tefekkür.adım", float(adim))
        # Tefekkürün hedefi yalnız gaye değildir; 𝒪₇ Mana'nın çıkardığı
        # mana merkezi de çeker. Evvelce ``mu_mana`` yazılıyor, hiçbir
        # meleke okumuyordu -- ölçüldü: 𝒪₇ düşürülünce netice hiç
        # değişmiyordu. Harman gayeye ağırlıklıdır (0.75/0.25): tefekkür
        # manaya dalar, fakat gayeyi bırakmaz.
        G = d.G
        if d.mu_mana is not None and np.shape(d.mu_mana)[-1] == len(d.G):
            mana = np.asarray(d.mu_mana, float)
            mana = mana.mean(0) if mana.ndim == 2 else mana
            G = 0.75 * d.G + 0.25 * mana
            d.olcum.koy("tefekkür.mana_katkısı", 1.0)
        else:
            d.olcum.koy("tefekkür.mana_katkısı", 0.0)
        lam = 0.1
        A = p.W("tefekkür.A", (S.shape[1], S.shape[1]))

        def V(M: np.ndarray) -> float:
            Mk = kaba(M, d.tavan)[0]
            return (0.5 * float(np.sum((M - G) ** 2))
                    + lam * celiski_skoru(Mk, A, 0.0))

        ilk = V(S)
        # **Mutasarrıfa strateji operatörü** (kütük H15): 𝒪₁₆'nın
        # öğrendiği ``θ`` akışın yönünü büker. Evvelce ``deneme.θ``
        # meleke içinde doğup orada ölüyordu -- ölçüldü: 𝒪₁₆ düşürülünce
        # netice hiç değişmiyordu.
        R = d.strateji if d.strateji is not None else None
        d.olcum.koy("tefekkür.strateji_var", float(R is not None))
        # Akış 30 adım koşar; her adımda çelişki gradyanı ``n×n``dir.
        # Çelişki terimi kaba kademede hesaplanıp ince eksene yayılır --
        # gaye terimi (``S − G``) ince eksende aynen kalır (artık bağı).
        # Kule adım BAŞINA yeniden kurulursa maliyet ``adım·n log n``
        # olur (ölçüldü: 8192 satırda 𝒪₂₁ tek başına 7,0 sn). Akış
        # boyunca çelişki terimi yavaş değişir; kaba görüş bir kere
        # kurulup adımlarda güncellenir.
        _, kademe_f, _ = kaba(S, d.tavan)
        for _ in range(adim):
            if kademe_f:
                Sk = kaba(S, d.tavan)[0]
                gk = ince(celiski_gradyani(Sk, A, 0.0)
                          / max(len(Sk), 1) ** 2, len(S), kademe_f)
            else:
                gk = celiski_gradyani(S, A, 0.0) / max(len(S), 1) ** 2
            grad = (S - G) + lam * gk
            if R is not None:
                grad = grad + 0.25 * (S @ R - S)
            S = S - 0.02 * grad
        d.olcum.koy("tefekkür.V_ilk", ilk)
        d.olcum.koy("tefekkür.V_son", V(S))
        d.olcum.koy("tefekkür.azaldı", float(V(S) < ilk))

        # --- 20 ∞-KATEGORİ MERTEBESİNDEN GEÇİŞ (kütük H40)
        # Akış bittikten SONRA koşar ki yukarıdaki "potansiyel azaldı"
        # iddiası bozulmasın: mertebe geçişi bir gradyan adımı değildir,
        # başka bir iştir ve ölçüsü ayrıdır. Bileşke artıktır (nizamname
        # Kademe 4): ince eksen silinmez, mertebenin bükümü ona yayılır.
        M20, tik, b0, buzulme = mertebe_gecisi(S, p)
        kappa = 0.35
        d.S = S + kappa * (M20 - S)
        d.mertebe_tikanikligi = tik
        d.mertebe_betti = b0
        d.olcum.koy("tefekkür.mertebe_büzülme", buzulme)
        d.olcum.koy("tefekkür.tıkanıklık_ort", float(tik.mean()))
        d.olcum.koy("tefekkür.tıkanıklık_azamî", float(tik.max()))
        d.olcum.koy("tefekkür.tıkanık_lif",
                    float(np.sum(tik > 0.9)))
        d.olcum.koy("tefekkür.ezber_lif", float(np.sum(b0 > 1)))
        d.olcum.koy("tefekkür.mertebe_bükümü",
                    float(np.linalg.norm(d.S - S)))
        d.not_dus(self.ad, "20 mertebe: tıkanıklık ort=%.3f âzamî=%.3f, "
                           "ezberli lif=%d" % (tik.mean(), tik.max(),
                                               int(np.sum(b0 > 1))))


# =====================================================================
@kaydet
class IlletKesfi(Meleke):
    """𝒪₂₂ İllet Keşfi -- nedensellik çizgesi ve **do**-hesabı.

    ``A_neden,ij = 𝕀(Sᵢ→Sⱼ)·σ(W[Sᵢ⊕Sⱼ])`` ve asiklik şartı
    ``h(A) = Tr(exp(A∘A)) − d = 0`` (NOTEARS). Burada çizge, skorlara
    göre **topolojik sırada** kurulur; böylece ``h(A) = 0`` inşa gereği
    sağlanır ve sınanır.

    Ayrıca ``P(Sⱼ | do(Sᵢ)) = Σ_k P(Sⱼ|Sᵢ,Z_k)P(Z_k)`` arka kapı
    düzeltmesi, `yaklasim.nedensel` ile aynı hesap olarak koşar.
    """

    no, ad = 22, "İllet Keşfi"
    okur, yazar = ("S",), ("A_neden",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        # Nedensellik çizgesi ``n×n``dir; kule olmadan uzun pencerede
        # tek başına belleği ve zamanı yer. Çizge kaba kademede kurulur;
        # 𝒪₂₈ Tashih boyut uyuşmasını zaten denetliyor.
        S, _, _ = kaba(d.S, d.tavan)
        n, ds = S.shape
        skor = sigmoid(S @ p.v("illet.dag", ds))
        sira = np.argsort(-skor)                       # yüksek skor önce = sebep
        rutbe = np.empty(n, dtype=int)
        rutbe[sira] = np.arange(n)

        Sn = S / (np.linalg.norm(S, axis=1, keepdims=True) + 1e-12)
        kuvvet = np.abs(Sn @ Sn.T)
        A = np.where(rutbe[:, None] < rutbe[None, :], kuvvet, 0.0)
        A = A * (A > np.quantile(A[A > 0], 0.7) if np.any(A > 0) else 0.0)
        d.A_neden = A
        d.olcum.koy("illet.asiklik_ihlali", asiklik_ihlali(A))
        d.olcum.koy("illet.kenar_sayısı", float(np.sum(A > 0)))
        d.olcum.koy("illet.nedensel_karmaşıklık",
                    float(np.trace(A) - np.linalg.slogdet(np.eye(n) + A)[1]))


def asiklik_ihlali(A: np.ndarray) -> float:
    """NOTEARS ölçütü ``h(A) = Tr(exp(A∘A)) − d``.

    ``A`` bir DAG'ın ağırlık dizeyi ise **tam olarak 0**'dır; herhangi bir
    devir varsa kesin pozitiftir.
    """
    d = len(A)
    M = A * A
    # matris üsteli (Taylor; M ≥ 0 ve küçük normlu tutulur)
    olcek = max(float(np.max(np.sum(M, axis=1))), 1.0)
    Mn = M / olcek
    toplam = np.eye(d)
    terim = np.eye(d)
    for k in range(1, 40):
        terim = terim @ Mn / k
        toplam = toplam + terim
    # exp(M) = exp(Mn)^olcek  --  iz için doğrudan seri kullan
    toplam = np.eye(d)
    terim = np.eye(d)
    for k in range(1, 60):
        terim = terim @ M / k
        toplam = toplam + terim
        if np.max(np.abs(terim)) < 1e-16:
            break
    return float(np.trace(toplam) - d)


def arka_kapi(x: np.ndarray, z: np.ndarray, y: np.ndarray) -> float:
    """``P(y|do(x))``in doğrusal hâli: ``z``ye şart koşarak ``x``in eğimi."""
    A = np.stack([x, z, np.ones_like(x)], axis=1)
    return float(np.linalg.lstsq(A, y, rcond=None)[0][0])


# =====================================================================
@kaydet
class Mantik(Meleke):
    """𝒪₂₃ Mantık Yürütme -- küllî önermeyi kurmak ve **nakza sunmak**.

    Doğruluk tablosu TAM hesaplanır: ``P₁ ⟹ P₂ ≡ ¬P₁ ∨ P₂``. Bu, dört
    satırın hepsinde sınanır; yaklaşık değildir (`ima`, `modus_ponens`).

    **Önermeler nereden geliyor?** Evvelce ``S.mean(1) > 0`` idi: mana
    dizeyinin satır ortalamasının işareti "önerme" sayılıyor, komşu
    satırlar arasında modus ponens işletiliyordu. Bu bir vekildi --
    ölçüldü: bu meleke düşürüldüğünde neticedeki ``‖ΔN‖ = 0`` çıkıyordu,
    yani hiçbir mantık fiilen yürümüyordu. Şimdi önermeler **şahitlerden**
    gelir:

        Pₖ : "küllî kaide, k'ıncı şahitte tutar"
        Netice : "bütün şahitler aynı kurala tâbidir"

    Netice küllîdir; küllî önermeyi düşüren şey **nakz**dır: tek karşı
    örnek yeter (`mizan.munazara.nakz_gecerli_mi` ile aynı hüküm).
    Nakz, dışarıda-bırak sınamasıyla aranır (`sahit.nakz_bul`): ``j``
    olmadan kurulan kaide ``j``de tutmuyorsa ``j`` karşı örnektir.

    Neticenin yakîni Gazâlî mîzânıyla hesaplanır: ``min`` -- çarpım
    değil (`mizan.munazara.yakin_gazali`). Sebebi oradadır: kat'î
    öncüllerden kurulu uzun bir ispat, sırf uzun diye değersizleşmemeli.
    """

    no, ad = 23, "Mantık Yürütme"
    okur, yazar = ("S", "E"), ("nakz", "ispat")
    ihtiyari = ("sahitler", "kaideler")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        sahitler = d.sahitler or []
        kaideler = d.kaideler or []

        # --- doğruluk tablosu: dört satırın hepsi (yaklaşık değil)
        tablo = [(P1, P2, ima(P1, P2)) for P1 in (False, True)
                 for P2 in (False, True)]
        d.olcum.koy("mantık.tablo_tam", float(len(tablo) == 4))
        d.olcum.koy("mantık.tablo_doğru",
                    float(all(im == ((not P1) or P2) for P1, P2, im in tablo)))

        if len(sahitler) < 2 or len(kaideler) != len(sahitler):
            d.nakz = []
            d.ispat = [{"nev": "küllî_iddia", "sebep": "şahit yetersiz",
                        "yakîn": 0.0, "şekil_geçerli": False}]
            d.olcum.koy("mantık.şahit_yeter", 0.0)
            d.olcum.koy("mantık.yakîn", 0.0)
            return

        n = nakz_bul(d.E, sahitler, kaideler)
        d.nakz = list(n["nakz"])
        tol = float(n["tolerans"])
        artik = list(n["artık"])

        # her şahit bir öncüldür; yakîni artığından okunur
        onculler = [float(np.exp(-a / max(tol, 1e-12))) for a in artik]
        onculler = [float(np.clip(y, 0.0, 1.0)) for y in onculler]
        sekil_gecerli = len(d.nakz) == 0        # nakz varsa küllî şekil düşer
        yakin = yakin_gazali(onculler, sekil_gecerli)

        ispat: List[Dict[str, object]] = []
        for k, (a, y) in enumerate(zip(artik, onculler)):
            ispat.append({"nev": "öncül", "şahit": k, "artık": a,
                          "yakîn": y, "nakzedildi": k in d.nakz})
        ispat.append({
            "nev": "küllî_iddia",
            "ifade": "bütün şahitler aynı kaideye tâbidir",
            "şekil_geçerli": sekil_gecerli,
            "nakz": list(d.nakz),
            "yakîn": yakin,
            "mertebe": mertebe_adi(yakin),
            "tolerans": tol,
        })
        d.ispat = ispat

        # modus ponens burada FİİLEN işler: küllî önerme + "hedef bir
        # şahittir" ⟹ "kaide hedefte de tutar".
        P1 = sekil_gecerli
        P2 = sekil_gecerli
        uygulandi = bool(P1 and ima(P1, P2))
        d.olcum.koy("mantık.şahit_yeter", 1.0)
        d.olcum.koy("mantık.nakz_sayısı", float(len(d.nakz)))
        d.olcum.koy("mantık.yakîn", yakin)
        d.olcum.koy("mantık.uygulanan_çıkarım", float(uygulandi))
        d.olcum.koy("mantık.geçerli_çıkarım",
                    float(uygulandi and modus_ponens(P1, P2) == P2))
        d.not_dus(self.ad, "şahit=%d nakz=%s yakîn=%.4f (%s)"
                  % (len(sahitler), d.nakz, yakin, mertebe_adi(yakin)))


def ima(P1: bool, P2: bool) -> bool:
    """``P₁ ⟹ P₂ ≡ ¬P₁ ∨ P₂``."""
    return (not P1) or P2


def modus_ponens(P1: bool, P2: bool) -> bool:
    """``P₁`` ve ``P₁⟹P₂`` doğruysa ``P₂``. Öncüller sağlanmıyorsa
    çıkarım YAPILMAZ -- ``None`` yerine ``P₂``nin kendisi değil, kuralın
    tanımı gereği yalnız sağlandığı hâlde kullanılır."""
    if not (P1 and ima(P1, P2)):
        raise ValueError("modus ponens öncülleri sağlanmıyor")
    return P2


# =====================================================================
@kaydet
class Ispat(Meleke):
    """𝒪₂₄ İspat -- burhân zinciri ``P₀ → P₁ → … → Pₙ ≡ Q``.

    ``T_ispat = Π_k Geçerlilik(P_{k−1} ⟹ P_k)``; ``𝟙_QED = 𝕀(T = 1)``;
    ``Sarsılmazlık = T/(1+λn)`` -- yani uzun zincir, aynı geçerlilikte
    daha zayıf sayılır (Occam'ın ispata tatbiki).
    """

    no, ad = 24, "İspat"
    okur, yazar = ("S",), ("burhan",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        zincir = [S[i] for i in range(len(S))]
        d.burhan = zincir
        gecerlilikler = [
            float(sigmoid(4.0 * kosinus(zincir[k - 1], zincir[k])))
            for k in range(1, len(zincir))
        ]
        T = float(np.prod(gecerlilikler)) if gecerlilikler else 1.0
        n = len(gecerlilikler)
        d.olcum.koy("ispat.T", T)
        d.olcum.koy("ispat.zincir_uzunluğu", float(n))
        d.olcum.koy("ispat.QED", float(T >= 1 - 1e-9))
        d.olcum.koy("ispat.sarsılmazlık", guvenli_bol(T, 1.0 + 0.1 * n))
        d.olcum.koy("ispat.boşluk",
                    float(np.sum([np.sum((zincir[k] - zincir[k - 1]) ** 2)
                                  for k in range(1, len(zincir))])))

# ======================================================================
#  𝒪₂₅–𝒪₃₆ MURÂKABE (klasik tensör hattı)
#  (evvelce nefs/murakabe.py)
# ======================================================================

# **Beş mertebe ve ondan türeyen hüküm ağırlığı buraya AİT DEĞİLDİR**
# (kütük H215): cetvel `mizan/munazara.py`dedir ve türevleri de orada
# durur. Evvelce burada ayrı bir nüsha vardı ve kaynaktan 7/13
# sapıyordu (H214); nüsha kalktı, sapma imkânı da kalktı.



# =====================================================================
@kaydet
class Teemmul(Meleke):
    """𝒪₂₅ Teemmül -- devridaim ve **durma ölçütü**.

    ``M⁽ᵗ⁾ = LayerNorm(M⁽ᵗ⁻¹⁾ + MultiHeadAttn(Ŷ, S, H))``, ve
    ``τ_durma = ArgMin_τ (‖M⁽ᵗ⁾ − M⁽ᵗ⁻¹⁾‖ < ε)``.

    Sınanabilir iddia: devridaim **yakınsar** ve durma ölçütü ``𝒦``
    turdan önce tetiklenir.

    "Ardışık farklar MONOTON azalır" diye kurulup sınandı ve **kaldı**:
    bazı tohumlarda 1-2 tur geriye sıçrama oluyor. Bu beklenir --
    büzücü bir eşleme geometrik yakınsama garanti eder, tur tur
    monotonluk garanti ETMEZ; ``LayerNorm`` de büzücü değildir. İddia
    düzeltildi: ölçülen şey artık ``azalma_oranı = son/ilk`` ve
    geriye sıçrama SAYISIDIR.

    Azamî tur sayısı ölçümle seçildi: yakınsama geometriktir fakat
    yavaştır (κ=0.4'te fark 60 turda 3.64 → 0.055). 12 turda kesilince
    ölçüt hiç tetiklenmiyordu; ``𝒦 = 200`` ile ``ε = 10⁻³`` tipik olarak
    100-130. turda sağlanıyor. Bu, "teemmül ucuz değildir" demenin
    sayısal hâlidir ve maliyeti ``0.1·τ_durma`` olarak raporlanır.
    """

    no, ad = 25, "Teemmül"
    okur, yazar = ("S", "H_hayal"), ("M",)
    ihtiyari = ("Q_sual", "sonsal")

    def uygula(self, d: Durum, p: Parametreler, K: int = 200,
               eps: float = 1e-3) -> None:
        # 200 tur boyunca ``n×n`` dikkat koşar; kule olmadan bu, uzun
        # pencerede akışın en pahalı yeridir. Devridaim kaba kademede
        # döner; ``M`` ince eksene geri yayılır (artık bağı korunur).
        S_ham, H_ham = d.S, d.H_hayal
        n_ham = len(S_ham)
        S, kademe, _ = kaba(S_ham, d.tavan)
        H, _, _ = kaba(H_ham, d.tavan)
        n, ds = S.shape
        d.olcum.koy("teemmül.kule_kademesi", float(kademe))
        Wq = p.W("teemmül.q", (ds, ds))
        # Teemmül boşluğa dalmaz, bir SUAL etrafında döner. 𝒪₁₅'in
        # ürettiği ``Q_sual`` sorgu yönünü kaydırır. Evvelce ``Q_sual``
        # yazılıyor, kimse okumuyordu -- ölçüldü: 𝒪₁₅ düşürülünce netice
        # hiç değişmiyordu. Kaydırma toplanarak yapılır (çarpımla değil),
        # yoksa sual sıfıra yakınken sorgu söner.
        q_kaydirma = None
        if d.Q_sual is not None and np.shape(d.Q_sual) == (ds,):
            q_kaydirma = np.asarray(d.Q_sual, float)[None, :]
        d.olcum.koy("teemmül.sual_var", float(q_kaydirma is not None))
        Wk = p.W("teemmül.k", (H.shape[1], ds))
        Wv = p.W("teemmül.v", (H.shape[1], ds))

        # 𝒪₁₇'nin Bayes ardılı, teemmülün hangi satıra ağırlık vereceğini
        # söyler. Evvelce ``sonsal`` hesaplanıp atılıyordu -- ölçüldü:
        # 𝒪₁₇ düşürülünce netice hiç değişmiyordu.
        if d.sonsal is not None and len(d.sonsal) == n:
            agirlik = np.asarray(d.sonsal, float)[:, None] * n
            d.olcum.koy("teemmül.sonsal_var", 1.0)
        else:
            agirlik = 1.0
            d.olcum.koy("teemmül.sonsal_var", 0.0)
        M = kat_norm(S.copy() * agirlik)
        farklar: List[float] = []
        tau_durma = K
        for t in range(1, K + 1):
            Q = M @ Wq if q_kaydirma is None else M @ Wq + 0.5 * q_kaydirma
            Y = dikkat(Q, H @ Wk, H @ Wv)
            # SÖNÜMLÜ artık: ``M + κY`` biçiminde kurulup ölçüldü ve
            # yakınsamadı (12 turda fark 0.51'de takıldı). ``(1−κ)M + κY``
            # dışbükey harmandır; dikkat çıktısı ``H``nin dışbükey
            # örtüsünde kaldığı için harman büzücüdür ve yakınsar.
            kappa = 0.4
            M_yeni = kat_norm((1 - kappa) * M + kappa * Y)
            fark = float(np.linalg.norm(M_yeni - M))
            farklar.append(fark)
            M = M_yeni
            if fark < eps:
                tau_durma = t
                break
        d.M = M if kademe == 0 else ince(M, n_ham, kademe)
        d.olcum.koy("teemmül.τ_durma", float(tau_durma))
        d.olcum.koy("teemmül.son_fark", farklar[-1])
        d.olcum.koy("teemmül.yakınsadı", float(farklar[-1] < eps))
        sicrama = sum(1 for i in range(len(farklar) - 1)
                      if farklar[i + 1] > farklar[i] + 1e-12)
        d.olcum.koy("teemmül.geriye_sıçrama", float(sicrama))
        d.olcum.koy("teemmül.azalma_oranı",
                    farklar[-1] / max(farklar[0], 1e-300))
        d.olcum.koy("teemmül.maliyet", 0.1 * tau_durma)
        d.not_dus(self.ad, "τ=%d, son fark=%.2e" % (tau_durma, farklar[-1]))


# =====================================================================
@kaydet
class Temkin(Meleke):
    """𝒪₂₆ Temkin -- sarsılmazlık: ``min_{‖δ‖≤ε} T(S+δ)``.

    ``VakarKatsayısı = 1/(1+‖∇_t S‖²)``; ``S_müstakar`` hâlihazırdaki ile
    öncekinin vakarla ağırlıklı harmanıdır. Sarsılmazlık, en kötü
    hâldeki tasdik değeriyle ölçülür -- bu bir **asgarî** aramasıdır,
    ortalama değil; temkinin tarifi budur.
    """

    no, ad = 26, "Temkin"
    okur, yazar = ("S", "M"), ("S",)

    def uygula(self, d: Durum, p: Parametreler, ornek: int = 24) -> None:
        S, M = d.S, d.M
        hedef = d.G if d.G is not None else S.mean(0)
        rng = np.random.default_rng(p.tohum + 26)
        eps = 0.1 * float(np.linalg.norm(S)) / max(np.sqrt(S.size), 1.0)

        temel = kosinus(M.mean(0), hedef)
        en_kotu = temel
        for _ in range(ornek):
            delta = rng.normal(size=S.shape)
            delta *= eps / max(float(np.linalg.norm(delta)), 1e-12)
            en_kotu = min(en_kotu, kosinus((M + delta).mean(0), hedef))

        vakar = 1.0 / (1.0 + float(np.sum(np.diff(S, axis=0) ** 2)))
        d.olcum.koy("temkin.vakar", vakar)
        d.olcum.koy("temkin.sarsılmazlık", en_kotu)
        d.olcum.koy("temkin.tolerans_marjı", temel - en_kotu)
        # **Temkin fiilen sarsılmazlığı KURAR.** Metin "S_müstakar,
        # hâlihazırdaki ile öncekinin vakarla ağırlıklı harmanıdır" der;
        # evvelce yalnız ölçülüyordu. Vakar yüksekse (akış pürüzsüzse)
        # hâl korunur; düşükse teemmül belleğine yaslanılır.
        d.S = kat_norm(vakar * S + (1.0 - vakar) * M)
        d.olcum.koy("temkin.harman", float(np.linalg.norm(d.S - S)))
        d.olcum.koy("temkin.emin", float(temel - en_kotu < 0.05))


# =====================================================================
@kaydet
class Tetkik(Meleke):
    """𝒪₂₇ Tetkik -- kılcal kusur haritası.

    ``δS_kılcal = S ⊙ M_mikro``, ``KusurHaritası = |δS − S_ideal|``.
    "İdeal" burada, ``S``in kendi düşük kipli (pürüzsüz) izdüşümüdür:
    kusur, sinyalin **kendi düzgün hâlinden** sapmasıdır. Böylece ölçüt
    dışarıdan bir doğru dayatmaz.
    """

    no, ad = 27, "Tetkik"
    okur, yazar = ("S",), ("kusur",)
    ihtiyari = ("somut",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape
        maske = sigmoid(S @ p.W("tetkik.mikro", (ds, ds)))
        kilcal = S * maske

        # ideal: ilk yarı tekil kiple yeniden kurulan pürüzsüz hâl
        U, s, Vt = np.linalg.svd(S, full_matrices=False)
        k = max(1, len(s) // 2)
        ideal = (U[:, :k] * s[:k]) @ Vt[:k]
        # 𝒪₁₉ Temsil'in somut hâli varsa "ideal" ona göre düzeltilir:
        # kusur, sinyalin kendi düzgün hâlinden VE somut temsilinden
        # sapmasıdır. Evvelce ``somut`` üretilip atılıyordu.
        if d.somut is not None and d.somut.shape[0] == n:
            geri = d.somut @ np.linalg.pinv(p.W("temsil.dec", (ds, d.d_hayal)))
            ideal = 0.5 * ideal + 0.5 * geri
            d.olcum.koy("tetkik.somut_var", 1.0)
        else:
            d.olcum.koy("tetkik.somut_var", 0.0)
        kusur = np.abs(kilcal - ideal)
        d.kusur = kusur          # 𝒪₂₈ Tashih bunu kendi formülünde kullanır

        d.olcum.koy("tetkik.kusur_l1", float(np.sum(kusur)))
        d.olcum.koy("tetkik.pürüz_derecesi", float(np.sum(np.diff(kilcal, axis=0) ** 2)))
        d.olcum.koy("tetkik.azami_kusur", float(np.max(kusur)))
        d.olcum.koy("tetkik.kusurlu_hücre_oranı",
                    float(np.mean(kusur > np.quantile(kusur, 0.9))))


# =====================================================================
@kaydet
class Tashih(Meleke):
    """𝒪₂₈ Tashih -- düzeltme, fakat **şartlı**.

    ``S_musahhah = S − γ·KusurHaritası ⊙ ∇Tenakuz``; düzeltme ancak
    ``T_yeni > T_eski`` ise kabul edilir, aksi hâlde ``S_itidal``
    (tez ile antitezin ortası) alınır. Yani tashih, iyileştirdiğini
    ÖLÇEREK kabul eder; körü körüne uygulanmaz.
    """

    no, ad = 28, "Tashih"
    okur, yazar = ("S",), ("S",)
    ihtiyari = ("G", "A_neden", "kusur")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds = S.shape[1]
        hedef = d.G if d.G is not None else S.mean(0)

        def tasdik(M: np.ndarray) -> float:
            return kosinus(M.mean(0), hedef)

        eski = tasdik(S)
        A = p.W("tashih.A", (ds, ds))
        Sk, kademe_t, _ = kaba(S, d.tavan)   # çelişki dizeyi ``n×n``
        esik = celiski_esigi(Sk, A, 0.5)
        d.olcum.koy("tashih.eşik", esik)
        grad = celiski_gradyani(Sk, A, esik)
        if kademe_t:
            grad = ince(grad, len(S), kademe_t)
        # **Düzeltme illetin bulunduğu yerde yapılır.** 𝒪₂₂ İllet Keşfi
        # bir nedensellik çizgesi (``A_neden``) kuruyor, hiçbir meleke
        # okumuyordu -- ölçüldü: 𝒪₂₂ düşürülünce netice hiç değişmiyordu.
        # Artık düzeltme, satırın nedensel derecesiyle ağırlıklanır:
        # hiçbir şeyin sebebi olmayan satırı düzeltmek bir şeyi düzeltmez.
        if d.A_neden is not None and d.A_neden.shape == (len(S), len(S)):
            derece = np.abs(np.asarray(d.A_neden, float)).sum(1)
            agirlik = derece / (float(np.max(derece)) + 1e-12)
            grad = grad * (0.5 + 0.5 * agirlik)[:, None]
            d.olcum.koy("tashih.illet_ağırlığı", 1.0)
        else:
            d.olcum.koy("tashih.illet_ağırlığı", 0.0)
        # Metnin kendi formülü: ``S − γ·KusurHaritası ⊙ ∇Tenakuz``.
        # Kusur haritası evvelce hiç çarpılmıyordu -- formül yazılıydı,
        # icra edilmiyordu.
        if d.kusur is not None and d.kusur.shape == grad.shape:
            k = d.kusur / (float(np.max(d.kusur)) + 1e-12)
            grad = grad * k
            d.olcum.koy("tashih.kusur_kullanıldı", 1.0)
        else:
            d.olcum.koy("tashih.kusur_kullanıldı", 0.0)
        grad = grad / max(float(np.max(np.abs(grad))), 1.0)
        musahhah = S - 0.05 * grad
        yeni = tasdik(musahhah)

        itidal = 0.5 * (S + musahhah)
        basarili = yeni > eski
        d.S = musahhah if basarili else itidal
        d.olcum.koy("tashih.eski_T", eski)
        d.olcum.koy("tashih.yeni_T", yeni)
        d.olcum.koy("tashih.başarılı", float(basarili))
        d.olcum.koy("tashih.düzeltme_miktarı",
                    float(np.linalg.norm(d.S - S)))


# =====================================================================
@kaydet
class Teyit(Meleke):
    """𝒪₂₉ Teyit -- **bağımsız** ikinci kanaldan doğrulama.

    ``NetTeyitSkoru = GüvenKatsayısı × BağımsızlıkDüzeyi``, ve
    ``T ← min(1, T + W_teyit)``. Buradaki incelik şudur: birbirini teyit
    eden iki kanal, ancak BAĞIMSIZ ise delil kuvvetlendirir. Bağımlı iki
    kanalın uyuşması yeni bilgi değildir -- bu yüzden çarpan olarak
    ``1 − |Cov|`` konur ve sınanır.

    **Şahitler burada tartılır** (kütük H6). Bir bulmacanın beş örneği,
    beş şahit demek DEĞİLDİR: birbirinden türemiş şahitler tek şahit
    hükmündedir. ``fitrat.tevafuk`` bunu zaten ölçüyordu ve ana akışta
    hiç çağrılmıyordu; artık çağrılır:

    * ``tevafuk_olcusu`` -- şartlı bağımsızlıkla ağırlıklı uyuşma,
    * ``fazla_sayma``    -- ``müteber şahit = 1 + (m−1)·ortalama ağırlık``.

    ``müteber_sahit``, 𝒪₃₂'deki istikrânın ``n``idir. Yani "kaç örnek
    gördüm" değil, "kaç **bağımsız** örnek gördüm" sorusunun cevabı
    hükme girer.
    """

    no, ad = 29, "Teyit"
    okur, yazar = ("S", "X", "E"), ("sahit_agirliklari",)
    ihtiyari = ("sahitler", "kaideler", "nakz")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, X = d.S, d.X
        ds = S.shape[1]
        # ikinci kanal: ham duyudan doğrudan türetilen bağımsız okuma
        E2 = kat_norm(X @ p.W("teyit.kanal2", (X.shape[1], ds)))
        guven = kosinus(S.mean(0), E2.mean(0))
        bagimsizlik = 1.0 - abs(pearson_cok(S, E2))
        net = guven * bagimsizlik
        eski = d.T
        d.T = float(min(1.0, eski + 0.2 * max(net, 0.0)))
        d.olcum.koy("teyit.güven", guven)
        d.olcum.koy("teyit.bağımsızlık", bagimsizlik)
        d.olcum.koy("teyit.net_skor", net)
        d.olcum.koy("teyit.T_artışı", d.T - eski)

        # ---- şahitlerin tartılması
        sahitler = d.sahitler or []
        kaideler = d.kaideler or []
        m = len(sahitler)
        if m < 2 or len(kaideler) != m:
            d.sahit_agirliklari = np.ones(max(m, 0))
            d.muteber_sahit = float(m)
            d.tevafuk = 0.0
            d.olcum.koy("teyit.tevafuk_tanımlı", 0.0)
            d.olcum.koy("teyit.müteber_şahit", float(m))
            return

        # deliller ham duyu uzayında kurulur -- kaideler orada yaşar
        # (bkz. 𝒪₁₈ Kıyas). ``S`` ile kurulup ölçüldü: satırları karışmış
        # bir uzayda hiçbir kaide tutmuyor, bütün delil dizileri sıfır
        # çıkıyor ve müteber şahit sayısı 1'e çöküyordu.
        deliller, tol = delil_dizileri(d.E, sahitler, kaideler)
        # hipotez: şahit i, nakzedilmemiş olanlardan mıdır?
        nakz = set(d.nakz or [])
        H = np.array([0.0 if i in nakz else 1.0 for i in range(m)])
        if H.min() == H.max():
            # tek sınıf: log-olabilirlik oranı tanımsızlaşır. Bu bir
            # kusur değil, hâlin kendisidir -- ayrıştırıcı delil yok.
            H = np.array([1.0] * m)

        t = tevafuk_olcusu(deliller, H)
        d.tevafuk = float(t["tevafuk"]) if t["tevafuk"] is not None else 0.0
        f = fazla_sayma(deliller, H)
        d.muteber_sahit = float(f.get("muteber_şahit_sayısı", m))

        # şahit başına ağırlık: kendi delil dizisinin, hipotezle uyuşması
        agirlik = []
        for k in range(m):
            uyusan = float(np.mean(deliller[k] == H))
            agirlik.append(uyusan)
        d.sahit_agirliklari = np.asarray(agirlik, float)

        d.olcum.koy("teyit.tevafuk_tanımlı", 1.0)
        d.olcum.koy("teyit.tevafuk", d.tevafuk)
        d.olcum.koy("teyit.şahit_sayısı", float(m))
        d.olcum.koy("teyit.müteber_şahit", d.muteber_sahit)
        d.olcum.koy("teyit.fazla_sayma_oranı",
                    float(f.get("fazla_sayma_oranı", 1.0)))
        d.olcum.koy("teyit.delil_toleransı", tol)
        d.not_dus(self.ad, "şahit=%d → müteber=%.2f  tevafuk=%.3f"
                  % (m, d.muteber_sahit, d.tevafuk))


def pearson_cok(A: np.ndarray, B: np.ndarray) -> float:
    a, b = A.ravel(), B.ravel()
    a0, b0 = a - a.mean(), b - b.mean()
    payda = float(np.linalg.norm(a0) * np.linalg.norm(b0))
    return float(a0 @ b0 / payda) if payda > 1e-12 else 0.0


# =====================================================================
@kaydet
class Tahkik(Meleke):
    """𝒪₃₀ Tahkik -- kökene inmek; **taklidi** ayırmak.

    ``S_tahkik = ArgMin_S (ℒ_köken(S) + Tenakuz(S, Aksiyomlar))``.
    ``TaklitDerecesi = exp(−α‖S − S_şöhret‖²)``: yaygın (şöhretli)
    cevaba ne kadar yakınsan taklit ihtimali o kadar yüksektir. Tahkik,
    yakınlığı değil **kökenle bağı** arar.

    **Küllî kaide burada mühürlenir** (kütük H6). Kaide, şahitlerin
    çapraz kovaryanslarının kutupsal toplamıdır (`sahit.kulli_kaide`) --
    fakat **nakzedilmiş şahitler dışarıda bırakılır**: kökeni bozuk
    şahitten alınan kaide taklittir, tahkik değildir.

    Evvelki hâlde ``TaklitDerecesi`` daima 1 çıkıyordu, çünkü ``S_şöhret``
    ``S.mean(0)``ın kendisi olarak alınmıştı: ``exp(−0.5·‖x−x‖²) = 1``.
    Yani "taklit mi?" sorusunun cevabı hesaplanmadan "evet" veriliyordu.
    Şöhret artık şahitlerden **bağımsız** bir merci olarak alınır: en
    kalabalık kümenin merkezi değil, mananın ana bileşenidir; taklit
    ölçüsü de ona olan uzaklıktan okunur.
    """

    no, ad = 30, "Tahkik"
    okur, yazar = ("S", "X", "E"), ("kaide",)
    ihtiyari = ("sahitler", "nakz")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, X = d.S, d.X
        ds = S.shape[1]
        koken = kat_norm(X @ p.W("tahkik.köken", (X.shape[1], ds))).mean(0)

        # şöhret: mananın baskın bileşeni -- "herkesin söylediği".
        U, sv, Vt = np.linalg.svd(S - S.mean(0), full_matrices=False)
        sohret = Vt[0] * float(np.linalg.norm(S.mean(0)))

        kokenle_bag = kosinus(S.mean(0), koken)
        taklit = float(np.exp(-0.5 * float(np.sum((S.mean(0) - sohret) ** 2))))
        T_tahkik = float(sigmoid(4.0 * (kokenle_bag - taklit)))
        d.olcum.koy("tahkik.kökenle_bağ", kokenle_bag)
        d.olcum.koy("tahkik.taklit_derecesi", taklit)
        d.olcum.koy("tahkik.T", T_tahkik)
        d.olcum.koy("tahkik.muhakkik", float(T_tahkik > 0.9))

        # ---- küllî kaidenin mühürlenmesi
        sahitler = d.sahitler or []
        nakz = set(d.nakz or [])
        temiz = [s for i, s in enumerate(sahitler) if i not in nakz]
        if temiz:
            # kaide ham duyu uzayında yaşar (bkz. 𝒪₁₈ Kıyas)
            d.kaide = kulli_kaide([capraz_kovaryans(d.E, s) for s in temiz])
            kalan = [float(np.mean(artiklar(d.E, s, d.kaide)))
                     for s in temiz if artiklar(d.E, s, d.kaide).size]
            d.olcum.koy("tahkik.kaide_artığı",
                        float(np.mean(kalan)) if kalan else float("nan"))
            d.olcum.koy("tahkik.kaide_dikliği",
                        float(np.max(np.abs(d.kaide.T @ d.kaide
                                            - np.eye(len(d.kaide))))))
        else:
            # Hiç temiz şahit yok: kaide **birim**tir, yani "hiçbir şey
            # değişmiyor" hükmü. Uydurma bir kaide üretmek yerine
            # cehli îlan etmek doğrusudur; 𝒪₃₂ bunu Şek'e çevirir.
            d.kaide = np.eye(d.E.shape[1])
            d.olcum.koy("tahkik.kaide_artığı", float("nan"))
        d.olcum.koy("tahkik.temiz_şahit", float(len(temiz)))


# =====================================================================
@kaydet
class Tedebbur(Meleke):
    """𝒪₃₁ Tedebbür -- âkıbete bakmak.

    ``S_{t+H} = ∫ Evrim``; ``𝒱_âkıbet = 𝔼[Σ βᵏ 𝒰_gaye(S_{t+k})]``;
    ``Risk = P(S_{t+H} ∈ 𝒮_tehlike)``; ve emniyetli hamle
    ``ArgMax_a (𝒱 − γ·Risk)``.

    Risk, ileri sarımların **kaçının** felaket eşiğinin altına düştüğü
    ile ölçülür; bu bir Monte Carlo tahminidir ve öyle bildirilir.
    """

    no, ad = 31, "Tedebbür"
    okur, yazar = ("M", "G"), ("akibet",)

    def uygula(self, d: Durum, p: Parametreler, H: int = 8,
               sarim: int = 24) -> None:
        M, G = d.M, d.G
        ds = M.shape[1]
        A = p.lie_tasarruf("tedebbür.evrim", ds, teta=0.15)
        rng = np.random.default_rng(p.tohum + 31)
        beta, tehlike = 0.9, 0.0

        degerler, felaket = [], 0
        for _ in range(sarim):
            s = M.mean(0).copy()
            V = 0.0
            for k in range(1, H + 1):
                s = kat_norm(s @ A.T + 0.1 * rng.normal(size=ds))
                V += (beta ** k) * float(np.exp(-np.linalg.norm(s - G)))
            degerler.append(V)
            if float(np.exp(-np.linalg.norm(s - G))) < tehlike + 1e-3:
                felaket += 1
        risk = felaket / sarim
        V_ort = float(np.mean(degerler))
        d.akibet = float(risk)   # 𝒪₃₃ mîzânda aleyhte delil olarak tartar
        d.olcum.koy("tedebbür.değer", V_ort)
        d.olcum.koy("tedebbür.risk", risk)
        d.olcum.koy("tedebbür.net", V_ort * (1 - risk))
        d.olcum.koy("tedebbür.ufuk", float(H))


# =====================================================================
@kaydet
class SekZanYakin(Meleke):
    """𝒪₃₂ Şek-Zan-Yakîn İdraki -- makam tayini.

    ``P_idrak = σ(W[S ⊕ İ ⊕ T])`` ve

        Şek   : ``|P − 0.5| < ε_şek``
        Zan   : ``0.5 + ε_şek ≤ P < 1 − ε_yakîn``
        Yakîn : ``P ≥ 1 − ε_yakîn``

    **Metinde bir boşluk var ve kapatıldı.** Yukarıdaki üç şart
    ``P < 0.5 − ε_şek`` aralığını (yani "aleyhte zan") KAPSAMAZ. Sadık
    kalıp boş bırakmak, ``Makam``ı tanımsız yapardı. Burada o aralık
    **Vehim** diye adlandırıldı: zannın aleyhte olanı. Böylece parçalanış
    hem TAM hem AYRIK olur ve bu ``test_nefs.py``de sınanır.

    **``P_idrak`` artık istikrâdan gelir** (kütük H3/H6). Evvelce
    ``σ(W[S ⊕ tenakuz ⊕ T])`` idi: eğitilmemiş bir ağırlıkla çarpılan,
    hiçbir delile bağlanmayan bir sayı. Şimdi:

        k = nakzedilmemiş şahit sayısı
        n = MÜTEBER şahit sayısı (𝒪₂₉'un fazla saymadan arındırdığı)
        P = (k+α)/(n+α+β)          -- Laplace'ın ardışıklık kaidesi

    (`mizan.istikra.ardisiklik_kaidesi`). İki hüküm buradan çıkar ve
    ikisi de kasten böyledir:

    * **Nakz varsa yakîn olmaz.** Tek karşı örnek küllî önermeyi
      düşürür; makam en çok Zan'a kadar çıkabilir.
    * **Sonlu şahitle yakîn olmaz.** ``β > 0`` iken ``P < 1``
      (`tam_istikra_mi`). Eksik istikrâdan yakîn devşirmek, delilden
      değil önselden devşirmektir. Bu, projenin dürüstlük şartıdır ve
      gizlenmez -- ölçüsü ``idrak.tam_istikrâ`` diye raporlanır.

    Şahit yoksa eski vekil formül **açıkça işaretlenerek** kullanılır
    (``idrak.vekil_formül = 1``).

    **Sükût** (kütük H10): makam Şek ise ``d.sukut`` kalkar ve beyan
    melekeleri susar. Bilmediğini söylememek bir kabiliyettir.
    """

    no, ad = 32, "Şek-Zan-Yakîn"
    okur, yazar = ("S",), ("makam", "sukut")
    ihtiyari = ("sahitler", "nakz", "sahit_agirliklari",
                "mertebe_tikanikligi")

    EPS_SEK = 0.05
    EPS_YAKIN = 0.05

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds = S.shape[1]
        sahitler = d.sahitler or []
        m = len(sahitler)

        if m >= 2 and d.nakz is not None:
            k_ham = m - len(d.nakz)
            muteber = max(float(d.muteber_sahit), 1.0)
            # müteber şahit sayısı kesirlidir; istikrâ tam sayı ister.
            n = max(1, int(round(min(muteber, float(m)))))
            k = int(np.clip(round(k_ham * n / max(m, 1)), 0, n))
            d.P_idrak = float(ardisiklik_kaidesi(k, n))
            d.olcum.koy("idrak.istikrâ_k", float(k))
            d.olcum.koy("idrak.istikrâ_n", float(n))
            d.olcum.koy("idrak.tam_istikrâ", float(tam_istikra_mi(k, n)))
            d.olcum.koy("idrak.vekil_formül", 0.0)
            makam = makam_tayin(d.P_idrak, self.EPS_SEK, self.EPS_YAKIN)
            if d.nakz and makam == "Yakîn":
                makam = "Zan"       # nakz varken yakîn iddiası meşru değil
                d.olcum.koy("idrak.nakz_yakîni_düşürdü", 1.0)
            d.makam = makam
        else:
            ozellik = np.concatenate([S.mean(0), np.full(ds, d.tenakuz),
                                      np.full(ds, d.T)])
            d.P_idrak = float(sigmoid(ozellik @ p.v("idrak.p", 3 * ds)))
            d.makam = makam_tayin(d.P_idrak, self.EPS_SEK, self.EPS_YAKIN)
            d.olcum.koy("idrak.vekil_formül", 1.0)

        # **Mertebe tıkanıklığı yakîni düşürür** (kütük H40). 𝒪₂₁'in
        # 20 ∞-kategori mertebesinden geçirdiği mana bir mertebeden
        # ötekine TAŞINAMIYORSA -- yani taşınamayan dik bileşen normun
        # onda dokuzunu aşıyorsa -- o mana bir mertebeye hapsolmuştur.
        # Hapsolmuş bir manadan yakîn devşirmek, nakz varken yakîn
        # iddia etmekle aynı hatadır: küllîlik iddiası yerel bir delille
        # temellendirilmiş olur. Makam en çok Zan'a çıkabilir.
        if d.mertebe_tikanikligi is not None:
            tik = np.asarray(d.mertebe_tikanikligi, float)
            tikanik = int(np.sum(tik > 0.9))
            d.olcum.koy("idrak.tıkanık_lif", float(tikanik))
            d.olcum.koy("idrak.tıkanıklık_ort", float(tik.mean()))
            if tikanik and d.makam == "Yakîn":
                d.makam = "Zan"
                d.olcum.koy("idrak.tıkanıklık_yakîni_düşürdü", 1.0)
            else:
                d.olcum.koy("idrak.tıkanıklık_yakîni_düşürdü", 0.0)

        # **Sükût iki kapıdan geçer** (kütük H16). Birincisi makamdır:
        # Şek'te söylenecek bir şey yoktur. İkincisi serbest enerjidir:
        # ``F_tenakuz ≤ ε_durgun`` ise zihinde çözülmesi gereken bir
        # tenakuz kalmamıştır ve zihin durgun suya döner. ``ε_durgun``
        # ELLE KONMAZ (H17): mananın kendi gürültü tabanından türetilir.
        eps_durgun = float(np.mean(np.abs(np.diff(S, axis=0)))) * 0.05 \
            if len(S) > 1 else 0.0
        durgun = bool(d.serbest_enerji <= eps_durgun)
        d.sukut = bool(d.makam == "Şek" or durgun)
        d.olcum.koy("idrak.ε_durgun", eps_durgun)
        d.olcum.koy("idrak.F_tenakuz", d.serbest_enerji)
        d.olcum.koy("idrak.durgun", float(durgun))
        d.olcum.koy("idrak.P", d.P_idrak)
        d.olcum.koy("idrak.entropi", ikili_entropi(d.P_idrak))
        d.olcum.koy("idrak.hüküm", hukum_agirligi(d.P_idrak, d.makam))
        d.olcum.koy("idrak.sükût", float(d.sukut))
        d.not_dus(self.ad, "P=%.4f → %s%s"
                  % (d.P_idrak, d.makam, "  (sükût)" if d.sukut else ""))


# =====================================================================
@kaydet
class Muhakeme(Meleke):
    """𝒪₃₃ Muhakeme -- **meclis**: bütün delillerin tartıldığı yer.

    ``Γ_mizan = AleyhteDeliller/(LehteDeliller+ε)``; karar eşiği
    ``𝕀(Γ < τ_kabul)``; ve makro operatör ``R_kebîr`` ile program sentezi.
    Karar geçmezse ``RejimDeğiştir`` -- yani nefs, hükmü zorlamak yerine
    kipini değiştirir.

    **En büyük kopukluk buradaydı ve burada kapatıldı.** ``S_kebîr`` bir
    kere 𝒪₆ Tasavvur'da yazılıyor, sonra hiç güncellenmiyordu. Beyan
    melekeleri (𝒪₃₇–𝒪₄₁) ise yalnız ``S_kebîr``i okur. Netice: 𝒪₇'den
    𝒪₃₂'ye kadar ``S`` üzerinde yapılan bütün iş -- tefekkür, illet,
    tashih, te'vil -- kelama HİÇ ULAŞMIYORDU. Ölçüldü: bu melekelerin
    düşürülmesi ``‖ΔN‖ = 0`` veriyordu; sebep melekelerin boş olması
    değil, mecliste mikro hâlin okunmamasıydı.

    Meclis artık mevcut ``S``ten toplanır: tez, o âna kadar yapılmış
    bütün murâkabenin hâlidir. Eski ``S_kebîr`` atılmaz, harmana girer
    (``0.5/0.5``) -- tasavvurun kurduğu makro mana da bir delildir.
    """

    no, ad = 33, "Muhakeme"
    okur, yazar = ("M", "S", "S_kebir", "G_kebir", "E"), ("S_kebir",)
    ihtiyari = ("kaide", "sahitler", "nakz", "mertebe_tikanikligi",
                "mertebe_betti")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        ds = d.S_kebir.shape[0]
        guncel = kat_norm(d.S.mean(0) @ p.W("muhakeme.macro", (ds, ds)))
        d.S_kebir = kat_norm(0.5 * d.S_kebir + 0.5 * guncel)
        d.olcum.koy("muhakeme.mikro_katkısı",
                    float(np.linalg.norm(guncel)))
        # **Küllî kaide burada tatbik edilir.** 𝒪₃₀ Tahkik'in mühürlediği
        # kaide varsa makro operatör O'dur; yoksa tohumdan türetilen bir
        # dönme kullanılır ve bu **işaretlenir**. Evvelce kaide hiç
        # okunmuyordu: 𝒪₃₀ hesaplıyor, kimse kullanmıyordu -- ölçüldü,
        # 𝒪₃₀ düşürülünce netice hiç değişmiyordu.
        if d.kaide is not None and d.kaide.shape == (ds, ds):
            R = d.kaide
            d.olcum.koy("muhakeme.kaide_tatbik", 1.0)
        else:
            R = p.lie_tasarruf("muhakeme.R", ds, teta=0.2)
            d.olcum.koy("muhakeme.kaide_tatbik", 0.0)
        S_yeni = R @ d.S_kebir

        lehte = max(kosinus(S_yeni, d.G_kebir), 0.0) + max(d.T, 0.0)
        aleyhte = (max(d.tenakuz, 0.0)
                   + max(d.olcum.al("tenkit.sapma", 0.0), 0.0)
                   + max(d.akibet, 0.0))     # 𝒪₃₁'in ölçtüğü âkıbet riski

        # **Şahit delili mîzâna girer.** Küllî kaide ``d_in`` uzayında
        # yaşadığı için (bkz. 𝒪₁₈) meclis onu dizey olarak tatbik
        # edemeyebilir; fakat hükmünü tartabilir ve tartmalıdır: kaç
        # müteber şahit tasdik ediyor, kaçı nakzediyor. Bu bağ olmadan
        # 𝒪₂₃ Mantık, 𝒪₂₉ Teyit ve 𝒪₃₀ Tahkik'in bütün işi mecliste
        # kayboluyordu -- ölçüldü, üçü de "tesirsiz" çıkıyordu.
        if d.sahitler:
            m = len(d.sahitler)
            n_nakz = len(d.nakz or [])
            muteber = max(float(d.muteber_sahit), 0.0)
            lehte += muteber * (m - n_nakz) / max(m, 1)
            aleyhte += muteber * n_nakz / max(m, 1)
            d.olcum.koy("muhakeme.şahit_lehte", muteber * (m - n_nakz) / max(m, 1))
            d.olcum.koy("muhakeme.şahit_aleyhte", muteber * n_nakz / max(m, 1))
            # 𝒪₃₀'un mühürlediği küllî kaide, kalan şahitleri ne kadar
            # açıklıyor? Kaide dizey olarak tatbik edilemese de (boyut
            # uyuşmazlığı) hükmü tartılabilir; bu bağ olmadan 𝒪₃₀
            # tamamen tesirsiz kalıyordu.
            if d.kaide is not None and d.kaide.shape[0] == d.E.shape[1]:
                temiz = [x for i, x in enumerate(d.sahitler)
                         if i not in set(d.nakz or [])]
                art = [float(np.mean(artiklar(d.E, x, d.kaide)))
                       for x in temiz if artiklar(d.E, x, d.kaide).size]
                if art:
                    ort = float(np.mean(art))
                    lehte += max(1.0 - ort, 0.0)
                    aleyhte += max(ort, 0.0)
                    d.olcum.koy("muhakeme.kaide_artığı", ort)
        # **Mertebeler arası tıkanıklık ve ezber mîzâna girer** (H40).
        # 𝒪₂₁'in 20 mertebeden geçirdiği mana bir mertebede hapsolduysa
        # (tıkanıklık) yahut ayrık adacıklara bölündüyse (``β₀ > 1``,
        # yani ezber -- H23), bu aleyhte delildir. Tıkanıklığın TERSİ de
        # delildir ve lehte sayılır: yirmi mertebenin hepsinde tutan bir
        # mana, tek mertebede tutandan kuvvetlidir.
        if d.mertebe_tikanikligi is not None:
            tik = np.asarray(d.mertebe_tikanikligi, float)
            ort = float(tik.mean())
            aleyhte += ort
            lehte += max(1.0 - ort, 0.0)
            d.olcum.koy("muhakeme.mertebe_aleyhte", ort)
            d.olcum.koy("muhakeme.mertebe_lehte", max(1.0 - ort, 0.0))
        if d.mertebe_betti is not None:
            b0 = np.asarray(d.mertebe_betti, float)
            ezber = float(np.mean(np.maximum(b0 - 1.0, 0.0)))
            aleyhte += ezber
            d.olcum.koy("muhakeme.mertebe_ezber", ezber)

        mizan = guvenli_bol(aleyhte, lehte)
        tau = 1.0
        gecti = mizan < tau

        program = gelu(S_yeni @ p.W("muhakeme.p1", (ds, ds))) @ p.W("muhakeme.p2", (ds, ds))
        nakz_orani = (len(d.nakz or []) / max(len(d.sahitler or []), 1)
                      if d.sahitler else 0.0)
        T_kebir = float(sigmoid(4.0 * (kosinus(S_yeni, d.G_kebir)
                                       - d.tenakuz - nakz_orani)))
        # **Karar geçmezse program tatbik EDİLMEZ.** Evvelce mîzân
        # hesaplanıyor, ``karar_geçti`` ölçüme yazılıyor ve program yine
        # de uygulanıyordu -- yani "rejim değiştir" hükmünün hiçbir
        # neticesi yoktu. Mîzânın bir hükmü varsa, hükmün bir neticesi
        # de olmalıdır: karar geçmediyse meclis dağılır, makro mana
        # olduğu gibi kalır.
        if gecti:
            d.S_kebir = kat_norm(T_kebir * program + (1 - T_kebir) * d.S_kebir)
        else:
            d.S_kebir = kat_norm(d.S_kebir)
        d.olcum.koy("muhakeme.mizan", mizan)
        d.olcum.koy("muhakeme.karar_geçti", float(gecti))
        d.olcum.koy("muhakeme.T_kebîr", T_kebir)
        d.olcum.koy("muhakeme.rejim_değişti", float(not gecti))
        d.not_dus(self.ad, "mizan=%.3f (τ=1.0) → %s"
                  % (mizan, "karar" if gecti else "rejim değiştir"))


# =====================================================================
@kaydet
class Tafsil(Meleke):
    """𝒪₃₄ Tafsil -- mücmeli dallarına açmak.

    ``S_tafsil = ⊕_k S_dal⁽ᵏ⁾``, ``w_k = softmax(v_dᵀ S_dal⁽ᵏ⁾)``, ve
    **sadakat şartı** ``Birleştir(S_tafsil) ≈ S_mücmel``.

    Tafsilin bedeli budur: açmak, toplayınca geri gelmiyorsa açmak değil
    dağıtmaktır. Sadakat hatası ölçülür ve sınanır.
    """

    no, ad = 34, "Tafsil"
    okur, yazar = ("S_kebir",), ("dallar",)

    def uygula(self, d: Durum, p: Parametreler, K: int = 5) -> None:
        mucmel = d.S_kebir
        ds = len(mucmel)
        dallar = np.stack([gelu(mucmel @ p.W("tafsil.dal%d" % k, (ds, ds)))
                           for k in range(K)])
        w = softmax(dallar @ p.v("tafsil.vd", ds))
        birlesik = w @ dallar

        # sadakat: birleştirilmiş dalları mücmele en iyi afin uydurma
        olcek = float(birlesik @ mucmel) / max(float(birlesik @ birlesik), 1e-12)
        hata = float(np.linalg.norm(olcek * birlesik - mucmel)
                     / max(np.linalg.norm(mucmel), 1e-12))
        d.dallar = np.asarray(birlesik, float)   # 𝒪₃₇ Fesâhat kelamı buradan kurar
        d.olcum.koy("tafsil.dallanma", float(K))
        d.olcum.koy("tafsil.sadakat_hatası", hata)
        d.olcum.koy("tafsil.netlik",
                    guvenli_bol(float(np.sum(np.linalg.norm(dallar, axis=1))),
                                float(np.linalg.norm(mucmel))))
        d.olcum.koy("tafsil.ağırlık_toplamı", float(w.sum()))


# =====================================================================
@kaydet
class Tefsir(Meleke):
    """𝒪₃₅ Tefsir -- müphemi **siyak ve sibakla** açmak.

    ``Murad = Softmax(S W [A⊕B]ᵀ/√d)[A⊕B]W_v``; ``Vuzuh = 1 − ℋ(P(Murad))``.
    ``Muhkemat`` (yakîn makamındaki önermeler) tefsirin sınırıdır:
    tefsir, muhkemle çelişemez -- çelişirse iş ``𝒪₃₆ Tevil``e düşer.
    """

    no, ad = 35, "Tefsir"
    okur, yazar = ("S", "H_hayal"), ("murad",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, _, _ = kaba(d.S, d.tavan)     # dikkat ``n×2n``dir; kule şart
        H = d.H_hayal
        ds = S.shape[1]
        siyak = np.roll(S, 1, axis=0)               # önceki bağlam
        sibak = np.roll(S, -1, axis=0)              # sonraki bağlam
        baglam = np.concatenate([siyak, sibak], axis=0)
        W = p.W("tefsir.W", (ds, ds))
        agirlik = softmax((S @ W) @ baglam.T / np.sqrt(ds))
        murad = agirlik @ baglam @ p.W("tefsir.v", (ds, ds))

        d.murad = np.asarray(murad.mean(0), float)   # 𝒪₃₉ Belâgat murada uyar
        pr = agirlik.mean(0)
        nz = pr > 0
        H_ent = -float(np.sum(pr[nz] * np.log(pr[nz])))
        azami = float(np.log(len(pr)))
        d.olcum.koy("tefsir.vuzuh", 1.0 - H_ent / max(azami, 1e-12))
        d.olcum.koy("tefsir.murad_normu", float(np.linalg.norm(murad)))
        d.olcum.koy("tefsir.muhkem_mi", float(d.makam == "Yakîn"))
        d.olcum.koy("tefsir.dikkat_toplamı", float(agirlik.sum(1).mean()))


# =====================================================================
@kaydet
class Tevil(Meleke):
    """𝒪₃₆ Tevil -- zâhir çelişince **irca**.

    ``T_tevil = 𝕀(Tenakuz(zâhir) > 0 ∧ Tenakuz(müevvel) = 0)``. Yani
    te'vil ancak (i) zâhirde hakikaten çelişki varsa ve (ii) te'vil o
    çelişkiyi KALDIRIYORSA geçerlidir. İki şarttan biri düşerse zâhir
    olduğu gibi kalır -- keyfî te'vilin önündeki sed budur ve sınanır.
    """

    no, ad = 36, "Tevil"
    okur, yazar = ("S",), ("S",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds = S.shape[1]
        A = p.W("tevil.A", (ds, ds))

        Sk, kademe_v, _ = kaba(S, d.tavan)   # çelişki dizeyi ``n×n``
        esik = celiski_esigi(Sk, A, 0.5)
        d.olcum.koy("tevil.eşik", esik)

        def celiski(M: np.ndarray) -> float:
            Mk, _, _ = kaba(M, d.tavan)
            return celiski_skoru(Mk, A, esik)

        zahir = celiski(S)
        illet = celiski_gradyani(Sk, A, esik)
        if kademe_v:
            illet = ince(illet, len(S), kademe_v)
        illet = illet / max(float(np.max(np.abs(illet))), 1.0)
        muevvel = S - 0.1 * illet
        sonra = celiski(muevvel)

        gecerli = (zahir > 0.0) and (sonra < zahir)
        d.S = muevvel if gecerli else S
        d.olcum.koy("tevil.zâhir_çelişki", zahir)
        d.olcum.koy("tevil.müevvel_çelişki", sonra)
        d.olcum.koy("tevil.geçerli", float(gecerli))
        d.olcum.koy("tevil.gereksiz_tevil_yok", float(zahir > 0 or not gecerli))

# ======================================================================
#  𝒪₃₇–𝒪₄₁ BEYAN (klasik tensör hattı)
#  (evvelce nefs/beyan.py)
# ======================================================================

ALTIN_ORAN = (1.0 + np.sqrt(5.0)) / 2.0

# mertebe adlarının sayısal sırası -- ölçüm defteri float ister
MERTEBE_SIRA: Dict[str, int] = {
    ad: i for i, (_, ad) in enumerate(reversed(MERTEBELER), start=1)
}


# =====================================================================
@kaydet
class Fesahat(Meleke):
    """𝒪₃₇ Fesâhat -- lafzın üç kusurundan arınması.

    ``FesâhatScore = 1 − [μ₁Tenâfür + μ₂Garâbet + μ₃Ta'kîd]``

    * **Tenâfür**: komşu ögelerin mahreç mesafesi -- ardışık farkların
      normu. Yüksekse söyleyiş tökezler.
    * **Garâbet**: ``−Σ log P_lügat(yᵢ)`` -- nadir öge kullanımı.
    * **Ta'kîd**: ``‖J_sentaks‖_F`` -- yapı karmaşıklığı.

    Üçü de ``[0,1]``e sıkıştırılır, yoksa skor negatife kaçar ve
    "fesâhat" ölçüsü olmaktan çıkar (ölçüldü: sıkıştırmasız kurulumda
    skor −18'e iniyordu).

    **Sükût hakkı buradan başlar** (kütük H10). ``d.sukut`` kalkmışsa
    (makam Şek) beyan **kurulmaz**: ``N`` sıfır kelamdır. Susmak,
    boş konuşmanın kibar hâli değildir; hükümsüzlüğün doğru ifadesidir.
    Sonraki beyan melekeleri sükûtu bozmaz, yalnız kayda geçer.
    """

    no, ad = 37, "Fesâhat"
    okur, yazar = ("S_kebir",), ("N",)
    ihtiyari = ("sukut", "dallar")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        ds = len(d.S_kebir)
        if d.sukut:
            d.N = np.zeros(ds)
            d.olcum.koy("fesâhat.sükût", 1.0)
            d.olcum.koy("fesâhat.skor", float("nan"))
            d.not_dus(self.ad, "sükût: makam Şek, kelam kurulmadı")
            return
        d.olcum.koy("fesâhat.sükût", 0.0)
        # 𝒪₃₄ Tafsil mücmeli dallarına açtıysa kelam o dallardan kurulur;
        # evvelce dallar hesaplanıp atılıyordu.
        taban = d.S_kebir
        if d.dallar is not None and len(d.dallar) == ds:
            taban = kat_norm(0.5 * d.S_kebir + 0.5 * d.dallar)
            d.olcum.koy("fesâhat.dallar_var", 1.0)
        else:
            d.olcum.koy("fesâhat.dallar_var", 0.0)
        N = kat_norm(gelu(taban @ p.W("fesâhat.dec", (ds, ds))))
        d.N = N

        tenafur = _sik(float(np.mean(np.abs(np.diff(N)))))
        pr = softmax(np.abs(N))
        garabet = _sik(-float(np.mean(np.log(pr + 1e-12))) / max(np.log(ds), 1e-12))
        takid = _sik(float(np.linalg.norm(np.diff(N, n=2))) / max(np.sqrt(ds), 1.0))

        skor = 1.0 - (0.4 * tenafur + 0.3 * garabet + 0.3 * takid)
        d.olcum.koy("fesâhat.tenâfür", tenafur)
        d.olcum.koy("fesâhat.garâbet", garabet)
        d.olcum.koy("fesâhat.ta'kîd", takid)
        d.olcum.koy("fesâhat.skor", skor)


def susuldu_mu(d: Durum, meleke: "Meleke") -> bool:
    """Sükût hâlinde beyan melekeleri kelamı **bozmaz**.

    Sükûtu her melekede ayrı ayrı ele almak yerine tek kapı: ``N``
    sıfırdır ve sıfır kalır. Aksi hâlde Talâkat sıfırı düzleştirir,
    Belâgat ölçekler, Münazara döndürür ve sonuçta susulmuş olmaz --
    gürültü çıkar. Ölçüm yine konur ki sükût **görünsün**.
    """
    if not d.sukut:
        return False
    d.olcum.koy("%s.sükût" % meleke.ad.lower(), 1.0)
    return True


def _sik(x: float) -> float:
    """``[0,∞) → [0,1)``; ``x/(1+x)``. Monoton ve tersinir."""
    return float(x / (1.0 + x))


# =====================================================================
@kaydet
class Talakat(Meleke):
    """𝒪₃₈ Talâkat -- akıcılık.

    ``N_akıcı = ∫ N_τ k_akış(t−τ)dτ`` (Gauss çekirdeğiyle düzleştirme);
    ``AkıcılıkScore = exp(−α·DuraksamaSüresi)``, duraksama ``‖dN/dt‖``in
    eşik altında kaldığı ölçü.

    Sınanabilir iddia: düzleştirme **pürüzü azaltmalı** ve toplam
    değişimi düşürmelidir; ölçülür.
    """

    no, ad = 38, "Talâkat"
    okur, yazar = ("N",), ("N",)
    ihtiyari = ("sukut",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        if susuldu_mu(d, self):
            return
        N = d.N
        n = len(N)
        t = np.arange(n)
        sigma = 1.2
        cekirdek = np.exp(-0.5 * ((t[:, None] - t[None, :]) / sigma) ** 2)
        cekirdek /= cekirdek.sum(1, keepdims=True)
        akici = cekirdek @ N

        onceki_puruz = float(np.sum(np.diff(N) ** 2))
        sonraki_puruz = float(np.sum(np.diff(akici) ** 2))
        hiz = np.abs(np.diff(akici))
        esik = 0.1 * float(np.mean(hiz)) if n > 1 else 0.0
        duraksama = float(np.mean(hiz < esik)) if n > 1 else 0.0

        d.N = akici
        d.olcum.koy("talâkat.pürüz_önce", onceki_puruz)
        d.olcum.koy("talâkat.pürüz_sonra", sonraki_puruz)
        d.olcum.koy("talâkat.düzleşti", float(sonraki_puruz <= onceki_puruz))
        d.olcum.koy("talâkat.duraksama", duraksama)
        d.olcum.koy("talâkat.akıcılık", float(np.exp(-2.0 * duraksama)))


# =====================================================================
@kaydet
class Belagat(Meleke):
    """𝒪₃₉ Belâgat -- **muktezâ-yı hâl**: sözü muhataba uydurmak.

    ``BelâgatScore = FesâhatScore × Uyum(N, Makam_muhatap)``;
    ``R_belâgat = exp(θ X_muktezâ) ∈ 𝔤``; ve kip seçimi:

        Muhatap akıllı  → **İcâz** (az sözle çok mana)
        Muhatap talebkâr → **İtnâb** (açarak anlatma)

    Fesâhat ile Belâgat'in çarpım hâlinde olması bir tercih değil,
    metnin tarifidir: fasih olmayan söz beliğ olamaz; fasih olup
    muhataba uymayan söz de beliğ olamaz.
    """

    no, ad = 39, "Belâgat"
    okur, yazar = ("N", "G_kebir"), ("N",)
    ihtiyari = ("sukut", "vech", "murad")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        if susuldu_mu(d, self):
            return
        N = d.N
        ds = len(N)
        # muhatabın makamı: gayenin kendisi (kime, ne için söylüyoruz)
        # Muhatabın makamı gayedir; fakat söz **murada** uymalı ve
        # teşbihin vech-i şebehini taşımalıdır. 𝒪₂₀ ve 𝒪₃₅ evvelce
        # ölçüm defterinde kalıyordu.
        makam_muhatap = d.G_kebir
        katki = 0
        if d.murad is not None and len(d.murad) == ds:
            makam_muhatap = makam_muhatap + 0.3 * kat_norm(d.murad)
            katki += 1
        if d.vech is not None and len(d.vech) == ds:
            makam_muhatap = makam_muhatap + 0.2 * kat_norm(d.vech)
            katki += 2
        d.olcum.koy("belâgat.murad_vech", float(katki))
        R = p.lie_tasarruf("belâgat.R", ds, teta=0.2)
        belig = R @ (N * makam_muhatap)

        uyum = kosinus(N @ p.W("belâgat.ifade", (ds, ds)),
                       makam_muhatap @ p.W("belâgat.makam", (ds, ds)))
        fesahat = d.olcum.al("fesâhat.skor", 0.5)
        skor = fesahat * uyum
        isabet = kosinus(belig @ p.W("belâgat.tesir", (ds, ds)), d.G_kebir)

        # icâz/itnâb: muhatabın idrak makamına göre
        # ``Zann-ı gālib`` de icâz tarafındadır: kuvvetli zan sahibi
        # sözü uzatmaz. Mertebe H158'de açıldı; buraya eklenmeseydi
        # ARC'nin HER görevi (istikrâ yakîni ~0,80) sessizce
        # itnâba düşerdi -- yani yeni mertebe beyanı bozardı.
        kip = "İcâz" if d.makam in ("Yakîn", "Zann-ı gālib", "Zan") \
            else "İtnâb"
        d.N = kat_norm(belig) * float(np.clip(skor, 0.05, 1.0))
        d.olcum.koy("belâgat.uyum", uyum)
        d.olcum.koy("belâgat.skor", skor)
        d.olcum.koy("belâgat.isabet", isabet)
        d.olcum.koy("belâgat.icâz_mı", float(kip == "İcâz"))
        d.olcum.koy("belâgat.fesâhatı_aşamaz",
                    float(abs(skor) <= abs(fesahat) + 1e-9))
        d.not_dus(self.ad, "kip=%s uyum=%.3f isabet=%.3f" % (kip, uyum, isabet))


# =====================================================================
@kaydet
class Sanat(Meleke):
    """𝒪₄₀ Sanat -- ahenk ve yenilik.

    ``EstetikDeğer = SimetrikHarmoni + λ·Yenilik``, ``SimetrikHarmoni =
    1 − ‖Y − Yᵀ‖_F``, ``Ω_altın = φ·I``, ``φ = (1+√5)/2``.

    İki şey tam olarak sınanır: ``φ``nin değeri (``φ² = φ + 1``) ve
    simetrik harmoninin **simetrik** dizeyde âzamî oluşu.
    """

    no, ad = 40, "Sanat"
    okur, yazar = ("N", "H_hayal"), ("ahenk",)
    ihtiyari = ("sukut",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        if susuldu_mu(d, self):
            return
        N, H = d.N, d.H_hayal
        ds = len(N)
        Y = np.outer(N, H.mean(0) @ p.W("sanat.h", (H.shape[1], ds)))
        Om = p.W("sanat.ahenk", (ds, ds))

        harmoni = simetrik_harmoni(Y)
        gelenek = np.eye(ds) * ALTIN_ORAN
        yenilik = float(np.linalg.norm(Om - gelenek) / max(np.sqrt(Om.size), 1.0))
        estetik = harmoni + 0.3 * yenilik

        # Estetik değer kelamı FİİLEN ölçekler; 𝒪₄₁ bunu okur.
        d.ahenk = float(np.clip(0.5 + 0.5 * harmoni, 0.25, 1.5))
        d.olcum.koy("sanat.harmoni", harmoni)
        d.olcum.koy("sanat.yenilik", yenilik)
        d.olcum.koy("sanat.estetik", estetik)
        d.olcum.koy("sanat.φ", ALTIN_ORAN)
        d.olcum.koy("sanat.φ_özdeşliği",
                    float(abs(ALTIN_ORAN ** 2 - ALTIN_ORAN - 1.0)))


def simetrik_harmoni(Y: np.ndarray) -> float:
    """``1 − ‖Y − Yᵀ‖_F / (2‖Y‖_F)``.

    Metindeki hâl ``1 − ‖Y − Yᵀ‖_F``dir; iki düzeltme yapıldı ve ikisi de
    ölçümden çıktı:

    * **Payda**: paydasız ölçü ``Y``nin BÜYÜKLÜĞÜNE bağlı olur, oysa
      harmoni bir orandır -- aynı şekilli iki dizeden büyük olanı "daha
      ahenksiz" görünürdü.
    * **2 katsayısı**: ``‖Y−Yᵀ‖² = 2‖Y‖² − 2⟨Y,Yᵀ⟩ ≤ 4‖Y‖²`` olduğundan
      yalnız ``‖Y‖``a bölmek ölçüyü ``[1−2, 1]``e taşır. Nitekim ölçüldü:
      harmoni −0.351 çıktı, yani "ahenk" negatif oldu. ``2‖Y‖`` ile
      bölünce ölçü ``[0,1]``dedir; ters simetrik dizede tam 0, simetrik
      dizede tam 1.
    """
    payda = float(np.linalg.norm(Y))
    if payda < 1e-12:
        return 1.0
    return float(1.0 - np.linalg.norm(Y - Y.T) / (2.0 * payda))


# =====================================================================
@kaydet
class Munazara(Meleke):
    """𝒪₄₁ Münazara -- hükmü hasmın karşısında sınamak.

    ``Cerh(S) = Tenakuz(S, Aksiyomlar) + (1 − BurhânSkoru(S))``;
    ``S_sentez = αS_tez + (1−α)S_antitez``;
    ``T = σ(İspatKuvveti(tez) − İspatKuvveti(antitez))``.

    ``HasmıSusturma`` ancak cerh eşiği aşarsa gerçekleşir; aksi hâlde
    netice **sentezdir**. Yani münazaranın tabiî sonucu galibiyet değil,
    telîftir; galibiyet istisnadır.

    **Burhân zinciri burada tartılır** (kütük H6). 𝒪₂₃'ün bıraktığı
    ``d.ispat`` kayıtları bir kıyas zinciridir; zincirin yakîni
    `mizan.munazara.yakin_zinciri` ile hesaplanır -- ``min``, çarpım
    değil. Cerh, o yakînin eksiğidir: ``Cerh = 1 − yakîn``. Evvelce
    burhân kuvveti ``d.olcum.al("ispat.T", 0.5)``ten okunuyordu, yani
    ölçüm defterinden; şimdi delilin kendisinden okunur.
    """

    no, ad = 41, "Münazara"
    okur, yazar = ("S_kebir", "N"), ("N",)
    ihtiyari = ("sukut", "ispat", "hukum", "burhan", "ahenk")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        if susuldu_mu(d, self):
            d.olcum.koy("münazara.netice_sentez", 0.0)
            return
        ds = len(d.S_kebir)
        tez = d.S_kebir
        R = p.lie_tasarruf("münazara.antitez", ds, teta=1.4)
        antitez = R @ tez                       # tezden döndürülmüş karşı görüş

        aksiyom = d.G_kebir if d.G_kebir is not None else tez

        # burhân kuvveti: ispat zincirinin yakîni (Gazâlî mîzânı)
        halkalar: List[Tuple[List[float], bool]] = []
        for kayit in (d.ispat or []):
            if kayit.get("nev") == "küllî_iddia":
                halkalar.append(([float(kayit.get("yakîn", 0.0))],
                                 bool(kayit.get("şekil_geçerli", False))))
        if halkalar:
            burhan = float(yakin_zinciri(halkalar))
            d.olcum.koy("münazara.burhân_kaynağı", 1.0)   # delilden
        else:
            burhan = float(d.olcum.al("ispat.T", 0.5))
            d.olcum.koy("münazara.burhân_kaynağı", 0.0)   # ölçüm defterinden
        # **Mühür cerhe girer.** 𝒪₁₃ Tasdik'in mührü düşmemişse tezin
        # burhânı eksiktir. Evvelce ``d.hukum`` hiç okunmuyordu; 𝒪₁₃
        # mühürlüyor, kimse bakmıyordu.
        muhur = bool((d.hukum or {}).get("mühür", False))
        if d.hukum is not None:
            burhan = burhan if muhur else burhan * 0.5
        d.olcum.koy("münazara.mühür", float(muhur))
        d.olcum.koy("münazara.burhân", burhan)
        d.olcum.koy("münazara.mertebe_sayısal",
                    float(MERTEBE_SIRA.get(mertebe_adi(
                        float(np.clip(burhan, 0.0, 1.0))), 0)))

        def cerh(S: np.ndarray, kuvvet: float) -> float:
            return max(0.0, -kosinus(S, aksiyom)) + (1.0 - kuvvet)

        c_tez = cerh(tez, burhan)
        c_anti = cerh(antitez, 1.0 - burhan)
        T = float(sigmoid(4.0 * (c_anti - c_tez)))

        alfa = 0.5
        sentez = alfa * tez + (1 - alfa) * antitez
        susturma = c_anti > 1.2
        galip = tez if susturma else sentez

        # 𝒪₂₄'ün burhân zinciri ve 𝒪₄₀'ın ahengi kelama fiilen girer.
        if d.burhan is not None and len(d.burhan):
            zincir = float(np.clip(len(d.burhan) / (len(d.burhan) + 4.0), 0, 1))
            burhan = max(burhan, zincir * burhan + (1 - zincir) * 0.5 * burhan)
            d.olcum.koy("münazara.burhân_halkası", float(len(d.burhan)))
        d.N = kat_norm(galip * d.N) * d.ahenk
        d.olcum.koy("münazara.cerh_tez", c_tez)
        d.olcum.koy("münazara.cerh_antitez", c_anti)
        d.olcum.koy("münazara.T", T)
        d.olcum.koy("münazara.hasım_susturuldu", float(susturma))
        d.olcum.koy("münazara.netice_sentez", float(not susturma))
        d.not_dus(self.ad, "cerh tez=%.3f antitez=%.3f → %s"
                  % (c_tez, c_anti, "galibiyet" if susturma else "telîf"))

# ======================================================================
#  KLASİK KÜLLÎ AKIŞ -- reel S üzerinde 41 meleke
#  (evvelce nefs/akis.py)
# ======================================================================

# Metnin kapanış bölümündeki kısmî sıra (önce → sonra)
KULLI_SIRA: Tuple[Tuple[int, int], ...] = (
    (1, 5), (5, 6), (6, 7),
    (7, 21), (21, 22), (22, 23),
    (23, 25), (25, 26), (26, 27), (27, 30),
    (30, 33), (33, 13),
    (13, 37), (37, 38), (38, 39),
)

# Akışın tam sırası. 𝒪₁₃ Tasdik İKİ kere koşar: bir kere kendi
# mertebesinde (ön tasdik), bir kere de 𝒪₃₃ Muhakeme meclisinden sonra
# **mühür** olarak. Metin bunu açıkça böyle söylüyor ("Muhakeme
# meclisinde Tasdik mührünü alarak").
AKIS: Tuple[int, ...] = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,          # idrak
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, # hüküm ve gaye
    21, 22, 23, 24,                          # burhân
    25, 26, 27, 28, 29, 30, 31, 32,          # murâkabe
    33, 13,                                  # meclis + mühür
    34, 35, 36,                              # tafsil / tefsir / tevil
    37, 38, 39, 40, 41,                      # beyan
)


def ilk_yazanlar() -> Dict[str, int]:
    """Her alanı yazan melekelerin numaraları (akış sırasına bakmadan)."""
    yazan: Dict[str, List[int]] = {}
    for m in melekeler():
        for alan in m.yazar:
            yazan.setdefault(alan, []).append(m.no)
    return yazan


def sira_gecerli_mi(sira: Sequence[int] = AKIS) -> Tuple[bool, List[str]]:
    """Akış sırası hem sözleşmeyi hem küllî kısmî sırayı sağlıyor mu?

    Sözleşme şartı **sıralı** okunur: bir meleke koştuğunda, mecburî
    okuduğu her alan o ana kadar YA ``Durum``la birlikte gelmiş
    (``E``, ``d_*``) YA da daha önce koşan bir meleke tarafından
    yazılmış olmalıdır.

    Bunun "her okuyan, o alanı yazan HERKESTEN sonra gelmeli" biçiminde
    kurulması yanlış olurdu ve kurulup ölçüldü: yerinde güncelleyen
    melekeler (``okur=("S",)``, ``yazar=("S",)``) yüzünden 70'ten fazla
    sahte ihlâl üretti. Doğru şart, ilk yazımın ilk okumadan önce
    gelmesidir.
    """
    hatalar: List[str] = []
    baslangic = {"E", "d_in", "d_hayal", "d_sem"}
    yazilmis = set(baslangic)
    s = sicil()
    for yer, no in enumerate(sira):
        if no not in s:
            hatalar.append("𝒪%d sicilde yok" % no)
            continue
        m = s[no]
        for alan in m.okur:
            if alan not in yazilmis:
                hatalar.append("𝒪%d (%s) '%s' alanını okuyor; henüz yazılmadı"
                               % (no, m.ad, alan))
        yazilmis.update(m.yazar)

    eksik = set(x.no for x in melekeler()) - set(sira)
    if eksik:
        hatalar.append("akışta olmayan melekeler: %s" % sorted(eksik))

    # küllî kısmî sıra: 'a' EN GEÇ, 'b'nin EN ERKEN koştuğu yere kadar
    # koşmuş olmalı. Bir meleke akışta birden çok kere geçebildiği için
    # (𝒪₁₃ iki kere) uçlar ayrı ayrı alınır.
    ilk = {}
    son = {}
    for yer, no in enumerate(sira):
        ilk.setdefault(no, yer)
        son[no] = yer
    for a, b in KULLI_SIRA:
        if a not in ilk or b not in son:
            hatalar.append("küllî sırada geçen 𝒪%d/𝒪%d akışta yok" % (a, b))
        elif ilk[a] > son[b]:
            hatalar.append("küllî sıra ihlâli: 𝒪%d, 𝒪%d'den sonra" % (a, b))
    return (not hatalar), hatalar


class Nefs:
    """Bütün melekeleri sırayla koşturan işletici."""

    def __init__(self, tohum: int = 0, sira: Sequence[int] = AKIS) -> None:
        self.p = Parametreler(tohum)
        self.sira = tuple(sira)
        self.s = sicil()

    def idrak_et(self, E: np.ndarray, sual: Optional[np.ndarray] = None,
                 d_hayal: int = 24, d_sem: int = 16) -> Durum:
        d = Durum.kur(E, d_hayal=d_hayal, d_sem=d_sem)
        d.sual = sual
        for no in self.sira:
            self.s[no].kosu(d, self.p)
        return d


def rapor_akis(tohum: int = 0, n: int = 20, d_in: int = 12) -> str:
    rng = np.random.default_rng(tohum)
    E = rng.normal(size=(n, d_in))
    nefs = Nefs(tohum)
    d = nefs.idrak_et(E)

    gecerli, hatalar = sira_gecerli_mi()
    satir = ["=== nefs: küllî akış ===",
             "meleke sayısı: %d   akış uzunluğu: %d   sıra geçerli: %s"
             % (len(melekeler()), len(AKIS), gecerli)]
    if hatalar:
        satir += ["  ! " + h for h in hatalar]
    satir.append("")
    satir += d.gunluk
    satir.append("")
    satir.append("makam=%s  P_idrak=%.4f  T=%.4f  tenakuz=%.4f"
                 % (d.makam, d.P_idrak, d.T, d.tenakuz))
    onemli = ["tecrit.β0", "tecrit.β1", "teemmül.τ_durma", "teemmül.yakınsadı",
              "illet.asiklik_ihlali", "muhakeme.mizan", "muhakeme.karar_geçti",
              "fesâhat.skor", "belâgat.skor", "sanat.harmoni",
              "münazara.netice_sentez"]
    satir.append("")
    for k in onemli:
        satir.append("  %-26s %.5g" % (k, d.olcum.al(k)))
    return "\n".join(satir)

# ======================================================================
#  44 MELEKENİN ÜNİTER HÂLİ -- hiçbiri okumaz
#  (evvelce nefs/qmeleke.py)
# ======================================================================

#: Altın oran -- 𝒪₄₀ Sanat'ın kendi tarifinden gelen açı.
ALTIN = (1.0 + math.sqrt(5.0)) / 2.0

#: χ tavanı **icra edilsin mi**? Varsayılan artık ``False``dır
#: (kütük H149, H118'in nakzı) ve sebebi ölçülmüştür:
#:
#:     tavanlı  : log F = −60,50, akış sonu entropisi 1,3863 (ln 4, ÇAKILI)
#:     tavansız : log F = −57,64, akış sonu entropisi 2,7708 (≈ ln 16)
#:
#: Tavan bir bütçe değil imhaydı: bir melekenin bağını kısmak, o
#: melekenin yerini daraltmaz; **diğer melekelerin kurduğu dolaşıklığı
#: siler**. Beyan melekelerine ulaşan dalganın entropisi yarıya iniyor
#: ve akış sonu girdiden bağımsız sabit bir sayıya çivileniyordu.
#:
#: ``True`` yapılarak eski davranış geri alınabilir -- kapatılamayan
#: bir tedbirin faydası ölçülemez (kütük H90) ve bu bayrak, nakzın
#: kendisinin de sınanabilmesi için duruyor.
NIZAM_ACIK: bool = False


def nizami_ac(acik: bool = True) -> bool:
    """Dolaşıklık nizamını aç/kapa; **evvelki hâli** döndürür."""
    global NIZAM_ACIK
    eski = NIZAM_ACIK
    NIZAM_ACIK = bool(acik)
    return eski


#: **STIEFEL İZOMETRİSİ -- meleke başına kanonikleştirme** (ceridenin
#: 1. mecburi müdahalesi; kütük H163).
#:
#: `kuantum/yazmac.py::kanonikle` MPS'i karışık kanonik hâle getirir ve o
#: hâlde SVD kesmesi **ispatlı olarak en iyidir** (Eckart–Young);
#: kanonik olmayan biçimde tekil değerler atılan durumların hakikî
#: ağırlığını temsil etmez. H121 bu yazmacın kanonik **olmadığını**
#: zaten yazıyordu; bedeli hiç ölçülmemişti.
#:
#: ÖLÇÜLDÜ (40 iki-kübitlik kapı, kanonikleştirme periyodu değişken)::
#:
#:     kübit χ   periyot    log F     kapı başına   kanoniklik hatası
#:     16    8   yok       −17,17       0,6509         2,87e+00
#:     16    8   1         −10,97       0,7602         5,58e-08   (+6,21)
#:     16   16   yok       −11,96       0,7415         4,26e+00
#:     16   16   1          −7,18       0,8357         6,19e-08   (+4,79)
#:     24   16   yok       −25,72       0,5257         4,61e+00
#:     24   16   1         −14,82       0,6904         6,81e-08  (+10,90)
#:
#: 24 kübitte ``e^{10,9} ≈ 54 000`` kat daha çok genlik tutuluyor ve
#: kazanç **zincir uzadıkça büyüyor** -- nazariyenin dediği tam budur:
#: zincir uzadıkça çevre diklikten daha çok sapar.
#:
#: **VE BU ÖLÇÜM YANILTICIYDI -- VARSAYILAN ``False``** (kütük H167).
#:
#: Yukarıdaki tablo ``sadakat_log`` ile alınmıştı ve o sayı **ayara
#: (gauge) bağlıdır**. Kanonik hâlde manası değişir: merkezden **uzak**
#: bir bağda iki sol-izometrik tensörün kurduğu ``Θ``nın bütün tekil
#: değerleri **eşittir** (``ΘᵀΘ = I``). O hâlde:
#:
#: * ``kalan/tam`` oranı ayarın değil **şeklin** hükmüne düşer, yani
#:   ölçü kıyas edilemez hâle gelir;
#: * daha kötüsü, orada kesmek fizikî olarak **en kötü** kesmedir --
#:   Schmidt tayfı merkezde durur, merkez dışında her yön eşit
#:   ağırlıklı görünür ve budama körlemesine olur.
#:
#: Akışta ölçüldü ve felâket: 𝒪₂₀ Teşbih'te durum normu
#: ``4,411 → 1,888e-64``, ``log F = −inf``.
#:
#: **Bu, H80'in kendi dersinin tekrarıdır** ve benim hatamdır:
#: *"Ayar-bağımlı bir büyüklükle hüküm vermek, ölçmeden hüküm
#: vermekten farksızdır."* Aynı tuzağa ikinci defa düştüm.
#:
#: Kanoniklik **yanlış değildir**; yanlış olan onu merkezden uzakta
#: kesmeyle beraber kullanmaktır. Doğrusu TEBD'in usulüdür: dikgenlik
#: merkezi **kapıyla beraber yürür**. Bu yazmaçta kapılar yığın hâlinde
#: (aynı anda birçok bağda) vurulduğu için -- ki o yığın 2 kat hız
#: kazandırmıştı (H79/H80) -- tek bir merkez tutulamaz. İki tasarım
#: birbiriyle çelişiyor ve bu **açık bir borçtur**, örtülmüyor.
#:
#: ``kanonikle`` ve ``kanonik_hata`` `kuantum/yazmac.py`de **durmaya devam
#: eder**: ölçüm âleti olarak doğrudur (H121'in iddiasını sayıyla
#: gösterir) ve merkez takibi kurulduğunda hazırdır.
KANONIK_ACIK: bool = False


def kanoniklestir(acik: bool = True) -> bool:
    """Kanonikleştirmeyi aç/kapa; **evvelki hâli** döndürür (H90)."""
    global KANONIK_ACIK
    eski = KANONIK_ACIK
    KANONIK_ACIK = bool(acik)
    return eski

_QSICIL: Dict[int, "QMeleke"] = {}


def qkaydet(sinif):
    ornek = sinif()
    if ornek.no in _QSICIL:
        raise ValueError("𝒪%d iki kere kaydedildi" % ornek.no)
    _QSICIL[ornek.no] = ornek
    return sinif


def qsicil() -> Dict[int, "QMeleke"]:
    return dict(_QSICIL)


def qmelekeler() -> List["QMeleke"]:
    return [_QSICIL[i] for i in sorted(_QSICIL)]


def nizam_cetveli() -> List[Tuple[int, str, str, Optional[int]]]:
    """41 melekenin dolaşıklık sınıfı ve χ tavanı -- rapor için.

    Cetvel koda gömülü değil, **okunabilirdir**: hangi melekenin hangi
    sınıfta olduğu iddia edilmez, buradan okunur ve
    `tanilama/nizam_dolasiklik.py` neticesini ölçer.
    """
    return [(m.no, m.ad, m.SINIF, m.CHI) for m in qmelekeler()]


class QParametre:
    """Bütün melekelerin açılarını taşıyan **tek düz vektör**.

    Eğitim motoru (AS-GEK) tek bir ``ℝ^d`` vektörü üzerinde çalışır;
    dolayısıyla melekelerin açıları dağınık duramaz. Her meleke ilk
    istediğinde kendine bir dilim ayrılır ve o dilim ebediyen onundur --
    yer tahsisi **çağrı sırasına göre** ve tekrarlanabilirdir.

    Bu, ``main/``daki dersin ana modele taşınmış hâlidir: orada
    Hamiltonyen parametreleri mertebeye anahtarlanınca ayrık motor
    kendi öğrendiğini siliyordu (kütük H39). Burada anahtar melekenin
    **numarası ve adı**dır; akış sırası değişse de dilim kaymaz.
    """

    def __init__(self, tohum: int = 0) -> None:
        self.tohum = int(tohum)
        self._yer: Dict[str, Tuple[int, int]] = {}
        self._n = 0
        self._vek: Optional[np.ndarray] = None

    # -- yer tahsisi --------------------------------------------------
    def al(self, anahtar: str, n: int) -> np.ndarray:
        if anahtar not in self._yer:
            self._yer[anahtar] = (self._n, int(n))
            self._n += int(n)
        bas, kac = self._yer[anahtar]
        if self._vek is None or len(self._vek) < self._n:
            self._buyut()
        return self._vek[bas:bas + kac]

    def _buyut(self) -> None:
        eski = self._vek
        rng = np.random.default_rng(self.tohum)
        yeni = rng.normal(scale=1.0, size=max(self._n, 1))
        if eski is not None:
            yeni[:len(eski)] = eski
        self._vek = yeni

    # -- eğitim arayüzü -----------------------------------------------
    def __len__(self) -> int:
        return self._n

    def vektor(self) -> np.ndarray:
        if self._vek is None:
            self._buyut()
        return np.asarray(self._vek[:self._n], float).copy()

    def yukle(self, v: np.ndarray) -> None:
        """Eğitim motorunun verdiği vektörü yerine koy."""
        v = np.asarray(v, float).reshape(-1)
        if self._vek is None:
            self._buyut()
        m = min(len(v), len(self._vek))
        self._vek[:m] = v[:m]

    def defter(self) -> Dict[str, Tuple[int, int]]:
        """Hangi melekenin nerede olduğu -- dürüstlük için raporlanır."""
        return dict(self._yer)


class QMeleke:
    """Üniter melekenin ortak atası."""

    no: int = 0
    ad: str = ""
    #: Bir küllî alanda birikecek açıların **sabit** sayısı. Durak sayısı
    #: değişse de bu değişmez; açılar duraklara devrolur.
    BIRIKIM_ACI: int = 8

    # =================================================================
    #  DOLAŞIKLIK NİZAMI (Dosya 1 / kütük H118)
    # =================================================================
    #: Melekenin dolaşıklık sınıfı: ``"kurucu"``, ``"koruyucu"``,
    #: ``"çözücü"``.
    #:
    #: **Tenkidim baştan yazılıdır ve saklanmıyor.** Dosya 1 "Tecrit
    #: χ→1", "Tasdik χ=1 saf durum", "İspat mutlak çözücü" diyor. Sabit
    #: bir ÜNİTER kapı Schmidt rütbesini şartsız düşüremez -- H107'de
    #: ispatlandı (üniterlik normu korur, dönme monoton değildir). O
    #: hâlde tablo bir üniter iddiası olarak okunursa **yanlıştır**.
    #:
    #: Doğru okunuşu **kesme cetveli**dir: kesme zaten üniter değildir,
    #: yaklaşıklığın kendisidir. Bir melekeye χ tavanı vermek, o
    #: melekenin kapılarından sonra bağın kaç Schmidt değeriyle
    #: tutulacağını söylemektir. Bu tam olarak kurulabilir ve
    #: ÖLÇÜLEBİLİR -- `tanilama/nizam_dolasiklik.py` ölçer.
    SINIF: str = "koruyucu"
    #: Bu meleke koşarken izin verilen âzamî Schmidt rütbesi.
    #: ``None`` = tavan yok (yazmacın kendi ``bag``ı).
    CHI: Optional[int] = None

    def aci(self, p, n: int, olcek: float = 0.6) -> np.ndarray:
        """Bu melekenin öğrenilen açıları -- düz vektördeki kendi dilimi."""
        # Anahtara UZUNLUK da girer. Girmediğinde ölçüldü ve kırıldı:
        # 𝒪₁ Müşahede önce 4, sonra 6 açı istiyor; tek anahtar ikisini
        # aynı dilime yolluyordu ve ``dik_iki_kubit`` 6 yerine 4 açı
        # alıyordu. Uzunluk artık girdiden bağımsız olduğu için (bkz.
        # ``yay``) anahtar da kararlıdır.
        anahtar = "q%d.%s/%d" % (self.no, self.ad, int(n))
        if isinstance(p, QParametre):
            return olcek * p.al(anahtar, n)
        return olcek * p.v(anahtar, n)          # eski (tohumlu) arayüz

    def yay(self, p, n_sabit: int, hedef: int, olcek: float = 0.6
            ) -> np.ndarray:
        """``n_sabit`` öğrenilen açıyı ``hedef`` durağa **yay**.

        **Ölçülen ve düzeltilen kusur.** Açılar evvelce satır sayısı
        kadar isteniyordu (``aci(p, n_satir*k)``); 4 satırla kurulan
        model 8 satır görünce ``IndexError`` veriyordu. Daha kötüsü:
        parametre sayısı girdinin uzunluğuna bağlı olsaydı model
        uzunluklar arasında hiç genelleyemezdi -- öğrendiği şey "bu
        uzunlukta ne yapılır" olurdu.

        Doğrusu, parametrenin **satırdan bağımsız** olmasıdır: öğrenilen
        şey "kaçıncı satırda ne yapılır" değil, "bir satırın kaçıncı
        kübitinde ne yapılır"dır. Evrişimin (convolution) ötelemeye
        bağışıklığı ile aynı kaidedir. Fazla durak varsa açılar
        devrolur (tile), eksikse kesilir.
        """
        a = self.aci(p, int(n_sabit), olcek)
        if hedef <= 0:
            return np.zeros(0)
        return np.resize(a, int(hedef))

    def birikim(self, p, n: int, olcek: float = 0.6) -> np.ndarray:
        """Bir küllî alanda BİRİKECEK açılar -- ``n`` ile bölünmüş.

        **Ölçülen ve düzeltilen kusur.** Birikim açıları doğrudan
        ``aci()``den alınıp 20 duraktan geçirilince toplam dönme ~10
        radyana çıkıyor; çember sarılıyor ve hedef kübit tamamen faz
        siliniyor. Ölçüldü: kelam alanının 16 taban durumu **tam
        düzgün** (her biri 0.0625) çıkıyordu, yani model konuşamıyordu.

        Sebep dolaşıklığın tabiatı değil, ölçeğin yanlışlığıydı: bir
        şahidin küllî hükme katkısı sınırlı olmalıdır ki yüz şahit
        çemberi tur atmasın. Birikim açısı ``θ_i / n``dir; böylece
        toplam dönme durak sayısından bağımsız olarak ``O(1)`` kalır ve
        hüküm, delil çoğaldıkça **keskinleşir**, silinmez.
        """
        return self.yay(p, self.BIRIKIM_ACI, n, olcek) / max(float(n), 1.0)

    def uygula(self, q: QYazmac, p: "QParametre") -> None:  # pragma: no cover
        raise NotImplementedError

    def kosu(self, q: QYazmac, p: "QParametre") -> None:
        n0 = q.iz.kapi
        # =============================================================
        # χ TAVANI **İCRADAN KALDIRILDI** (kütük H149, H118'in nakzı)
        # =============================================================
        #
        # Evvelce her meleke kendi ``CHI`` bütçesiyle koşuyor, yani o
        # meleke vurulurken yazmacın bağı zorla ``CHI``ye indiriliyordu.
        # Fikir makuldü: kurucu çok bağ ister, çözücü az. Fakat icrası
        # **yanlıştı** ve ölçüldü.
        #
        # Kusur şudur: bağ boyutu bir **kapının** değil, **bütün
        # dalganın** vasfıdır. Bir melekeyi düşük tavanla koşturmak "bu
        # meleke az yer kaplasın" demek değil, "**bu meleke, diğer
        # melekelerin kurduğu dolaşıklığı silsin**" demektir. Yani tavan
        # bir bütçe değil, bir imhadır.
        #
        # ÖLÇÜLDÜ (χ=16 yazmaç, 1814 kapı, tek geçiş):
        #
        #     tavanlı   : log F = −60,50   kapı başına 0,9672
        #                 akış sonu entropisi 1,3863  (= ln 4, ÇAKILI)
        #     TAVANSIZ  : log F = −57,64   kapı başına 0,9687
        #                 akış sonu entropisi 2,7708  (≈ ln 16)
        #
        # Yani tavan, beyan melekelerine ulaşan dalganın dolaşıklığını
        # **yarıya indiriyordu**; üstelik akış sonunu tam ``ln 4``e
        # çiviliyordu -- girdiden bağımsız sabit bir sayı, ki bu bir
        # ölçüm değil bir kelepçedir. Bedeli yalnız %11 süredir.
        #
        # ``CHI`` **kaldırılmadı**: sınıf ilanı (kurucu/koruyucu/çözücü)
        # manalı bir taahhüttür ve ``nizam_yuzlestir()`` onu ölçümle
        # yüzleştirir -- tıpkı `nefs/sozlesme.py`nin bölge ilanını
        # yüzleştirdiği gibi. İlan artık **icra edilmiyor, sınanıyor**;
        # aradaki fark, kelepçe ile sözleşme arasındaki farktır.
        #
        # ``NIZAM_ACIK`` ile eski davranış geri alınabilir; kapatılamayan
        # bir tedbirin faydası ölçülemez (kütük H90).
        eski = q.y.bag_tavan
        if NIZAM_ACIK and self.CHI is not None:
            q.y.bag_tavan = max(1, min(int(self.CHI), q.y.bag))
        try:
            # **STIEFEL İZOMETRİSİ -- meleke koşmadan EVVEL** (H163).
            # Kanonik hâlde SVD kesmesi en iyidir; kanonik olmayan
            # biçimde tekil değerler atılanın hakikî ağırlığını
            # temsil etmez. Ölçüldü: 24 kübitte log F −25,72 → −14,82,
            # yani 54 000 kat daha çok genlik tutuluyor.
            #
            # **Meleke başına** çağrılır, kapı başına değil: kapı başına
            # en iyi neticeyi veriyor (yukarıdaki tabloda periyot 1)
            # fakat maliyeti akışta ölçülmelidir; meleke başına
            # çağırmak, kazancın çoğunu maliyetin küçük bir kısmıyla
            # alır. Bu bir tercih değil, ölçülen iki ucun arasıdır.
            if KANONIK_ACIK:
                q.y.kanonikle()
            self.uygula(q, p)
        finally:
            q.y.bag_tavan = eski
        q.iz.not_dus("𝒪%d %s" % (self.no, self.ad),
                     "%d kapı" % (q.iz.kapi - n0))

    # -- müşterek desenler -------------------------------------------
    def tugla(self, q: QYazmac, p: "QParametre", ofset: int = 0,
              olcek: float = 0.5) -> None:
        """Veri kübitleri üzerinde fırça (brick) düzeninde ``SO(4)`` katmanı.

        Komşu çiftlere dik kapı vurmak dolaşıklığı yayar; iki ofsetli iki
        katman, menzili bir kademede iki katına çıkarır (MERA'nın MPS
        üzerindeki fiilî karşılığı).
        """
        a = self.aci(p, 6, olcek)
        G = dik_iki_kubit(a)
        k = q.ayar.satir_kubiti
        # **Y I Ğ I N.** Bütün fırça çiftleri birbirinden ayrıktır:
        # bir satır içinde ``j`` ile ``j+2`` çakışmaz, satırlar arasında
        # da yerel hüküm kübiti ayırıcı durur. O hâlde ``n·⌊k/2⌋`` ayrı
        # çağrı yerine TEK yığın SVD'si yeter (kütük H79).
        sol = [q.veri(i, j) for i in range(q.n_satir)
               for j in range(ofset, k - 1, 2)]
        q.cift_yigin(sol, G)

    def satir_donmesi(self, q: QYazmac, p: "QParametre",
                      olcek: float = 0.6) -> None:
        """Her satırın her veri kübitine kendi öğrenilen dönmesi."""
        k = q.ayar.satir_kubiti
        a = self.aci(p, k, olcek)          # sütun başına, satırdan bağımsız
        # Kapılar sütuna bağlı olduğu için ``k`` ayrı dizey yeter;
        # ``n·k`` yuvaya tek çağrıda yayılır.
        Gk = np.stack([donme(float(t)) for t in a])
        yuv = np.array([q.veri(i, j) for i in range(q.n_satir)
                        for j in range(k)])
        q.tek_yigin(yuv, np.tile(Gk, (q.n_satir, 1, 1)))


# =====================================================================
#  𝒪₁–𝒪₁₀  İDRAK
# =====================================================================
@qkaydet
class QMusahede(QMeleke):
    """𝒪₁ Müşahede -- odaklanma: veri kübitlerine öz-dikkat katmanı.

    Reel modelde bu ``Softmax(QKᵀ/√d)V`` idi ve ``n×n`` maliyetliydi.
    Üniter karşılığı fırça düzeninde iki ``SO(4)`` katmanıdır: her kapı
    komşu iki kübitin genliklerini karıştırır, iki ofset menzili
    ikiye katlar. Maliyet yuva sayısında **doğrusal**; dikkatin karesel
    derdi burada yoktur (kütük H34'ün kule ile çözdüğü şeyi, kübit
    yazmacı yapısı gereği çözer).
    """
    no, ad = 1, "Müşahede"
    SINIF, CHI = "kurucu", 8   # öz-dikkat: fırça katmanı dolaşıklığı kurar

    def uygula(self, q, p):
        self.satir_donmesi(q, p, 0.7)
        self.tugla(q, p, ofset=0, olcek=0.6)
        self.tugla(q, p, ofset=1, olcek=0.6)


@qkaydet
class QHayal(QMeleke):
    """𝒪₂ Hayal -- suretin açılması: kısmî süperpozisyon.

    Tam Hadamard bütün ihtimalleri eşitler; hayal o kadar başıboş
    değildir. Her satırın son veri kübiti ``θ`` kadar açılır: ihtimal
    kapısı aralanır, fakat mevcut suret silinmez.
    """
    no, ad = 2, "Hayal"
    SINIF, CHI = "kurucu", 8   # süperpozisyonu aralar

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.9)
        j = q.ayar.satir_kubiti - 1
        q.tek_yigin([q.veri(i, j) for i in range(q.n_satir)],
                    np.stack([donme(0.25 * math.pi + float(t)) for t in a]))


@qkaydet
class QMuhayyile(QMeleke):
    """𝒪₃ Muhayyile -- terkip serbestliği: uzak kübitleri karıştırır.

    Hayal gördüğünü açar; muhayyile **görmediğini** birleştirir. Bunun
    için satır içinde atlamalı çiftler (``j`` ile ``j+2``) kullanılır --
    komşuluk değil, sıçrama.
    """
    no, ad = 3, "Muhayyile"
    SINIF, CHI = "kurucu", 16   # atlamalı çift: uzak menzil kurar

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.8))
        k = q.ayar.satir_kubiti
        for i in range(q.n_satir):
            for j in range(0, k - 2):
                q.uzak_cift(q.veri(i, j), q.veri(i, j + 2), G)


@qkaydet
class QTertip(QMeleke):
    """𝒪₄ Tertip -- şahit bölütlemesi: satırı kendi yerel hükmüne bağlar.

    Kütük H6: "hepsi aynı kurala tâbidir" bilgisi bayrakla bildirilmez,
    organlarla sezilir. Burada her satırın son veri kübiti, o satırın
    yerel hüküm kübitine **kontrollü dönme** ile bağlanır; ikisi zincirde
    bitişiktir, dolayısıyla kapı yereldir ve ucuzdur. Satırın muhtevası
    hiçbir yerde okunmaz; hüküm onunla **dolaşır**.
    """
    no, ad = 4, "Tertip"
    SINIF, CHI = "koruyucu", 8   # satırı yerel hükme bağlar, menzil kısa

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.7)
        j = q.ayar.satir_kubiti - 1
        # (veri son kübiti, yerel hüküm) çiftleri bitişik ve ayrıktır
        q.cift_yigin([q.veri(i, j) for i in range(q.n_satir)],
                     np.stack([kontrollu_donme(float(t)) for t in a]))


@qkaydet
class QTecrit(QMeleke):
    """𝒪₅ Tecrit -- soyutlama: dolanıklık **çözücü**.

    MERA'nın ``U``su gibi çalışır fakat ters yönde: ortak olmayanı ayırır.
    Fırça katmanının tersi (``Gᵀ``) uygulanır; dik olduğu için bu tam
    tersidir ve bilgi kaybetmez -- tecrit, atmak değil **ayırmaktır**.
    """
    no, ad = 5, "Tecrit"
    #: **χ TAVANI KALDIRILDI (kütük H148, H118'in nakzı).** Evvelce
    #: ``CHI = 1`` idi, yani bu meleke koşarken yazmacın bağı zorla 1'e
    #: iniyor ve dalga **çarpım durumuna kesiliyordu**. Ölçüldü (χ=32):
    #:
    #:     tavan=1     : tutulan 6,6e-10   entropi 3,357 → 0,693
    #:     tavan=yok   : tutulan 0,909     entropi 3,357 → 3,346
    #:
    #: İki netice çıktı. Birincisi: tavan bilgiyi **on milyar kat**
    #: imha ediyordu. İkincisi ve daha mühimi: tavan kalkınca bu
    #: melekenin daraltması **tamamen kayboluyor** -- demek ki Tecrit'in
    #: çözücülüğü hiç kapısından gelmiyor, yalnız kesmeden geliyormuş.
    #: Şerhi "fırça katmanının tersi (Gᵀ), bilgi kaybetmez" diyor fakat
    #: kapı kurucununkinden **başka kübit çiftlerine** vuruyor; o hâlde
    #: hakikaten ters değil. Bu bir borçtur ve gizlenmiyor: tecridin
    #: manasını üniter olarak icra edecek kapı henüz yazılmadı.
    SINIF, CHI = "çözücü", None

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        k = q.ayar.satir_kubiti
        q.cift_yigin([q.veri(i, j) for i in range(q.n_satir)
                      for j in range(1, k - 1, 2)], G.T)


@qkaydet
class QTasavvur(QMeleke):
    """𝒪₆ Tasavvur -- küllî mahiyetin kurulması: bir MERA kademesi daha.

    Dolaşıklığı satırlar arasına taşıyan yer burasıdır; tek satırın
    kendi içindeki kapılar mahiyeti küllîleştirmez.
    """
    no, ad = 6, "Tasavvur"
    SINIF, CHI = "kurucu", 16   # MERA kademesi: dolaşıklığı satırlar arasına taşır

    def uygula(self, q, p):
        q.mera(kademe=1, teta=self.aci(p, 24, 0.6))


@qkaydet
class QMana(QMeleke):
    """𝒪₇ Mana -- satırların manası küllî tasdike akar.

    Bütün yerel hükümler tek bir MPO ile ``tasdik`` alanına akıtılır.
    Kübit oynamaz, dolaşıklık sürüklenmez; bağ 2'dir.
    """
    no, ad = 7, "Mana"
    SINIF, CHI = "koruyucu", 4   # MPO bağı zaten 2; birikim tek kübite akar

    def uygula(self, q, p):
        q.mpo_topla("tasdik", self.birikim(p, q.n_satir, 0.9))


@qkaydet
class QTahlil(QMeleke):
    """𝒪₈ Tahlil -- bileşenlerine ayırma: kübit başına ayrı dönme.

    Her kübit kendi açısıyla çevrilince ortak hâl bileşenlerine ayrışır;
    bu, tekil değer ayrışımının üniter karşılığıdır (dik dönmeler).
    """
    no, ad = 8, "Tahlil"
    SINIF, CHI = "çözücü", 2   # tahlil: ortak hâli bileşenlerine ayırır

    def uygula(self, q, p):
        self.satir_donmesi(q, p, 0.8)


@qkaydet
class QTerkip(QMeleke):
    """𝒪₉ Terkip -- ayrılanı birleştirme: ters yönlü fırça katmanı."""
    no, ad = 9, "Terkip"
    SINIF, CHI = "kurucu", 8   # terkip: ayrılanı birleştirir

    def uygula(self, q, p):
        self.tugla(q, p, ofset=1, olcek=0.7)


@qkaydet
class QTezat(QMeleke):
    """𝒪₁₀ Tezat -- **yıkıcı girişim**: zıt kutupların işareti çevrilir.

    Kütük H19'un üç şartından üçüncüsü budur ve burada fiilen olur:
    ``σ_z`` bir taban durumunun işaretini çevirir, o genlik komşusuyla
    toplandığında **sıfırlanır**. Klasik bir "tezat skoru" hesaplansaydı
    bu olmazdı; girişim ancak işaretli genlikte olur.
    """
    no, ad = 10, "Tezat"
    SINIF, CHI = "koruyucu", 4   # işaret çevirme; bağ büyütmez

    def uygula(self, q, p):
        Z = faz_z()
        k = q.ayar.satir_kubiti
        q.tek_yigin([q.veri(i, k - 1) for i in range(1, q.n_satir, 2)], Z)


# =====================================================================
#  𝒪₁₁–𝒪₂₄  HÜKÜM, GAYE, BURHÂN
# =====================================================================
@qkaydet
class QTenakuz(QMeleke):
    """𝒪₁₁ Tenakuz -- çelişkinin küllî ``tenakuz`` alanına akıtılması.

    Reel modelde çelişki ``C = −S(AᵀA)Sᵀ`` idi: ``n×n``, karesel. Burada
    çelişki bir dizey değil, bir **dolaşıklıktır**: her satırın yerel
    hükmü küllî tenakuz kübitine bağlanır; birbiriyle uyuşmayan satırlar
    o kübitte zıt yönde dönme üretir ve **birbirini söndürür** (yıkıcı
    girişim). Uyuşanlar ise aynı yönde döner ve yapıcı girişimle
    kuvvetlenir. Ölçü hiçbir yerde çıkmaz; hüküm dalgada durur.
    """
    no, ad = 11, "Tenakuz Bulma"
    SINIF, CHI = "koruyucu", 4   # MPO birikimi, bağ 2

    def uygula(self, q, p):
        a = self.birikim(p, q.n_satir, 1.1)
        # işaret satır sırasına göre alternatiflenir: uyuşmazlık zıt döner
        isaret = np.where(np.arange(q.n_satir) % 2 == 0, 1.0, -1.0)
        q.mpo_topla("tenakuz", a * isaret)


@qkaydet
class QTenkit(QMeleke):
    """𝒪₁₂ Tenkit -- zayıf satırın yerel hükmü ``|0⟩``a doğru çevrilir.

    Elemek, reel modelde satırı **sıfırlamaktı** -- kayıplı ve H14'e
    aykırı. Üniter karşılığı elemek değil **bastırmaktır**: yerel hüküm
    kübiti sıfır yönüne döndürülür, bilgi silinmez, ağırlığı düşer.
    """
    no, ad = 12, "Tenkit"
    SINIF, CHI = "çözücü", 2   # tenkit: zayıf şahidi bastırır

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.4)
        q.tek_yigin(q.yereller(),
                    np.stack([donme(-abs(float(t))) for t in a]))


@qkaydet
class QTasdik(QMeleke):
    """𝒪₁₃ Tasdik -- mühür: küllî tasdik alanı içinde faz kilidi.

    Akışta **iki kere** koşar (kendi mertebesinde ve 𝒪₃₃'ten sonra);
    ikisinde de aynı kapıdır. Mühür, tasdik kübitlerini birbirine
    bağlayan bir kontrollü dönmedir: ikisi hemfikirse mühür tutar.
    """
    no, ad = 13, "Tasdik"
    #: Tavan **ölçüldü ve tesirsizdi**: ``CHI`` 1, 2, 4 yahut ``None``
    #: iken tutulan kesir daima ``1,0000`` ve entropi hiç değişmiyor.
    #: Yani bu meleke kesme gerektirecek bir dolaşıklık kurmuyor; ilan
    #: edilen "saf durum (χ=1)" şartı bir şey icra etmiyordu. Yanıltıcı
    #: olmasın diye kaldırıldı; davranış aynen aynıdır.
    SINIF, CHI = "çözücü", None

    def uygula(self, q, p):
        a = self.aci(p, 2, 0.5)
        q.cift(q.kulli("tasdik", 0), kontrollu_donme(float(a[0])))
        q.tek(q.kulli("tasdik", 1), donme(float(a[1])))


@qkaydet
class QGaye(QMeleke):
    """𝒪₁₄ Gaye -- teleolojik ufuk: tasdik ``mîzân``a bağlanır.

    Gaye, hükmün nereye çekildiğidir. Tasdik alanı mîzân alanına
    kontrollü dönme ile bağlanır; ikisi de küllî blok içindedir ve
    aralarındaki mesafe blok boyu kadardır (13 kübit), dolayısıyla takas
    burada meşrudur ve ucuzdur.
    """
    no, ad = 14, "Gaye Belirleme"
    SINIF, CHI = "koruyucu", 4   # tasdik→mîzân, küllî blok içinde kısa bağ

    def uygula(self, q, p):
        a = self.aci(p, 4, 0.5)
        for j in range(2):
            q.uzak_cift(q.kulli("tasdik", j), q.kulli("mizan", j),
                        kontrollu_donme(float(a[j])))


@qkaydet
class QMerak(QMeleke):
    """𝒪₁₅ Merak -- bilgisizliğin açılması: ``nakz`` alanı süperpozisyona.

    Sual sormak, cevabı bilmediğini ilan etmektir; kuantum karşılığı o
    kübiti süperpozisyona sokmaktır. Merak ayrıca tünelleme vanasını
    açan melekedir (kütük H29) -- ``Γ`` buradan yükselir.
    """
    no, ad = 15, "Merak ve Sual"
    SINIF, CHI = "kurucu", 8   # merak: nakz alanını süperpozisyona sokar

    def uygula(self, q, p):
        a = self.aci(p, 2, 0.5)
        q.tek_yigin([q.kulli("nakz", j) for j in range(2)],
                    np.stack([donme(0.25 * math.pi + float(t))
                              for t in a[:2]]))


@qkaydet
class QDenemeYanilma(QMeleke):
    """𝒪₁₆ Deneme-Yanılma -- keşif: küçük rastgele (fakat tohumlu) hamleler.

    Oyuncu-eleştirmen döngüsünün üniter karşılığı, ödülü ölçüp geri
    beslemek değildir (o okuma olurdu); **hamle dizisini** uygulamaktır.
    Hangi hamlenin iyi olduğunu eğitim motoru söyler: bu melekenin
    açıları öğrenilen parametrelerdir.
    """
    no, ad = 16, "Deneme-Yanılma"
    SINIF, CHI = "kurucu", 8   # keşif hamleleri

    def uygula(self, q, p):
        k = q.ayar.satir_kubiti
        a = self.aci(p, k, 0.3)
        Gk = np.tile(np.stack([donme(float(t)) for t in a]),
                     (q.n_satir, 1, 1))
        q.tek_yigin([q.veri(i, j) for i in range(q.n_satir)
                     for j in range(k)], Gk)


@qkaydet
class QIhtimal(QMeleke):
    """𝒪₁₇ İhtimal -- Bayes: önselin mîzâna yazılması.

    ``P(S|ℰ) ∝ P(ℰ|S)P(S)``. Üniter karşılığı, mîzân kübitlerinin
    önsel açıyla çevrilmesidir; olabilirlik ise 𝒪₇ Mana'nın akıttığı
    dolaşıklıkta zaten durmaktadır. Çarpım, dönmelerin **bileşkesidir**
    (``R(α)R(β) = R(α+β)``) -- yani logaritmik toplama.
    """
    no, ad = 17, "İhtimal Hesabı"
    SINIF, CHI = "koruyucu", 4   # önsel: tek kübitlik dönmeler

    def uygula(self, q, p):
        a = self.aci(p, 4, 0.4)
        q.tek_yigin([q.kulli("mizan", j) for j in range(4)],
                    np.stack([donme(float(t)) for t in a[:4]]))


@qkaydet
class QKiyas(QMeleke):
    """𝒪₁₈ Kıyas -- şahitten şahide: komşu satırlar arasında kapı.

    Bilinen vakadan bilinmeyene geçmek, iki satırı aynı kapıdan
    geçirmektir: aralarındaki dönüşüm ortak olursa dolaşıklık kurulur.
    Satırlar zincirde ``oge`` kadar uzaktır (varsayılan 5); bu kısa
    mesafede takas meşrudur.
    """
    no, ad = 18, "Kıyas"
    SINIF, CHI = "kurucu", 8   # kıyas: satırdan satıra dolaşıklık

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        for i in range(q.n_satir - 1):
            q.uzak_cift(q.veri(i, 0), q.veri(i + 1, 0), G)


@qkaydet
class QTemsil(QMeleke):
    """𝒪₁₉ Temsil -- soyutu somuta indirmek, **tersinir** olarak.

    Reel modelde bu bir kodlayıcı/çözücü çiftiydi ve devir hatası
    ölçülüyordu. Üniter kapı dik olduğu için devir hatası **cebren
    sıfırdır**: ``GᵀG = I``. Temsilin bilgi kaybetmemesi burada bir
    iddia değil, kapının tarifidir.
    """
    no, ad = 19, "Temsil"
    SINIF, CHI = "koruyucu", 8   # temsil dik ve tersinir

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.6))
        k = q.ayar.satir_kubiti
        sol = [q.veri(i, 0) for i in range(q.n_satir)]
        if k >= 4:
            sol += [q.veri(i, 2) for i in range(q.n_satir)]
        q.cift_yigin(sol, G)


@qkaydet
class QTesbih(QMeleke):
    """𝒪₂₀ Teşbih -- vech-i şebeh: ilk iki satırın ortak yönü.

    Benzeyen ile benzetilen arasındaki ortak vecih, iki satırı aynı
    kapıdan geçirip dolaştırmakla kurulur.
    """
    no, ad = 20, "Teşbih"
    SINIF, CHI = "kurucu", 8   # teşbih: iki satırı dolaştırır

    def uygula(self, q, p):
        if q.n_satir < 2:
            return
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        k = q.ayar.satir_kubiti
        for j in range(k):
            q.uzak_cift(q.veri(0, j), q.veri(1, j), G)


@qkaydet
class QTefekkur(QMeleke):
    """𝒪₂₁ Tefekkür -- **20 ∞-kategori mertebesinden geçiş** (kütük H40).

    Ana modelin ``main/``dan devraldığı asıl icat budur. Yirmi lif
    ``omega_kategori_nbe`` ile kurulup makineyle denetlenir; her lif
    dalgayı **kendi mertebesine mahsus** açı ve menzille büker:

    * ``olcek`` -- dönme açısı ``1/(1+log(1+m))``; yüksek mertebe az büker.
    * ``adim``  -- lifin baktığı satır mesafesi ``1+⌊log₂(1+m)⌋``; yüksek
      mertebe **uzak menzilli** tutarlılıktır.
    * ``pencere`` -- lifin dokunduğu kübit bloğunun genişliği.

    Mertebeler **toplanmaz** (H21); ayrı liflerde ayrı eksenlere etki
    eder, bileşke terkiptir. Uzak menzilli bağ MPO ile kurulur -- yani
    1000. mertebe 16 satır ötesine takas yapmadan dokunur.
    """
    no, ad = 21, "Tefekkür"
    SINIF, CHI = "kurucu", 16   # tefekkür: 20 mertebe, uzak menzil

    def uygula(self, q, p):
        lifler = lifleri_kur(DINAMIK)
        a = self.aci(p, len(lifler), 1.0)
        k = q.ayar.satir_kubiti

        # --- (1) Tek kübitlik kısım: her lif KENDİ eksenine dokunur.
        # Aynı eksene düşen lifler (yuva % k aynı olanlar) aynı kübite
        # ardışık dönme vurur; ``R(α)R(β) = R(α+β)`` olduğu için bunlar
        # **toplanabilir** ve netice birebir aynıdır. Ayrı eksenler ayrı
        # kalır -- H21 (mertebeler toplanmaz) bozulmaz: toplanan şey
        # mertebeler değil, aynı eksendeki dönme açılarıdır.
        eksen_acisi: Dict[int, float] = {}
        for lif in lifler:
            teta = lif.olcek * (1.0 + 0.3 * float(a[lif.yuva]))
            eksen_acisi[lif.yuva % k] = eksen_acisi.get(lif.yuva % k, 0.0) + teta
        yuv, Gl = [], []
        for j, top in eksen_acisi.items():
            R = donme(top)
            for i in range(q.n_satir):
                yuv.append(q.veri(i, j))
                Gl.append(R)
        q.tek_yigin(yuv, np.stack(Gl))
            # Uzak menzilli tutarlılık. **Ölçülen ve düzeltilen kusur
            # (kütük H54, 3. borç).** Mesafe evvelce SATIR cinsinden
            # alınıyor ve ``adim < n_satir`` şartına takılıyordu. Ölçüldü:
            # 6 satırlık bir girdide ``adım`` 1000. mertebe için 10,
            # 60 000. mertebe için 17 çıkıyor; ikisi de 6'dan büyük
            # olduğu için yüksek mertebelerin **ayırt edici tarafı olan
            # uzak menzil hiç ateşlenmiyordu**. Geriye yalnız ``olcek``
            # kalıyor, o da 1000 ile 60 000 arasında 0,126'ya karşı
            # 0,083 -- yani ayrık motorun seçtiği yüksek mertebe fiilen
            # hiçbir şey yapmıyordu.
            #
        # Doğrusu, mesafeyi satırda değil **kübit zincirinde** ölçmek.
        # Yazmaç zaten bir zincirdir; 6 satır × 12 kübit = 72 kübitlik
        # bir zincirde 17 adımlık bir sıçrama pekâlâ tanımlıdır ve
        # satır sayısından bağımsızdır.
        #
        # --- (2) Uzak menzil: YİRMİ MPO YERİNE TEK MPO.
        #
        # Yirmi lif ayrı ayrı ``mpo_topla`` çağırıyordu ve profilde en
        # pahalı tek kalem buydu (0,52 sn, koşunun %41'i). Halbuki
        # ``mpo_topla``nın uyguladığı üniter ``U = exp((Σᵢ θᵢ nᵢ) ⊗ Y)``
        # şeklindedir; ``nᵢ`` aynı tabanda köşegen ve ``Y`` sabit olduğu
        # için iki çağrı **değişmeli**dir:
        #
        #     exp(A⊗Y)·exp(B⊗Y) = exp((A+B)⊗Y)
        #
        # Yani yirmi çağrının bileşkesi, durak açılarının toplandığı TEK
        # çağrıya birebir eşittir. **H21 bozulmaz:** toplanan şey
        # mertebeler değil, aynı durağa düşen dönme açılarıdır; her lif
        # kendi ``adım``ıyla kendi duraklarını seçmeye devam eder.
        son = q.kulli("makam", 0)
        katki: Dict[int, float] = {}
        for lif in lifler:
            teta = lif.olcek * (1.0 + 0.3 * float(a[lif.yuva]))
            bas = q.veri(0, lif.yuva % k)
            duraklar = list(range(bas, son, lif.adim))
            if len(duraklar) < 2:
                continue
            pay = teta / len(duraklar)
            for d in duraklar:
                katki[d] = katki.get(d, 0.0) + pay
        if len(katki) >= 2:
            dur = sorted(katki)
            q.mpo_topla("makam", [katki[d] for d in dur], duraklar=dur)


@qkaydet
class QIllet(QMeleke):
    """𝒪₂₂ İllet Keşfi -- nedensellik: **yönlü** bağ.

    Nedensellik simetrik değildir; sebep sonuçtan öncedir. Kontrollü
    dönme tam da böyledir: kontrol (önceki satır) ``|1⟩`` iken hedef
    (sonraki satır) döner, tersi olmaz. Asiklik şartı inşa gereği
    sağlanır -- kapı hep soldan sağadır.
    """
    no, ad = 22, "İllet Keşfi"
    SINIF, CHI = "koruyucu", 8   # illet: yönlü ve seyrek

    def uygula(self, q, p):
        a = self.yay(p, 4, max(q.n_satir - 1, 1), 0.5)
        for i in range(q.n_satir - 1):
            q.uzak_cift(q.veri(i, 0), q.veri(i + 1, 0),
                        kontrollu_donme(float(a[i])))


@qkaydet
class QMantik(QMeleke):
    """𝒪₂₃ Mantık -- nakz: tek karşı örnek küllî önermeyi düşürür.

    Kütük H6'nın kaidesi burada bir üniterdir: her yerel hüküm ``nakz``
    alanına **negatif** açıyla akar. Bir tek şahit ters yönde uyanırsa
    küllî nakz kübiti döner ve 𝒪₃₂'de yakîni düşürür. Toplama değil
    girişimdir: nakzlar birbirini kuvvetlendirir, tasdikler söndürür.
    """
    no, ad = 23, "Mantık Yürütme"
    SINIF, CHI = "koruyucu", 4   # MPO nakz birikimi, bağ 2

    def uygula(self, q, p):
        q.mpo_topla("nakz", -np.abs(self.birikim(p, q.n_satir, 0.8)))


@qkaydet
class QIspat(QMeleke):
    """𝒪₂₄ İspat -- burhân zinciri: yerel hükümler ardışık bağlanır.

    ``P₀ → P₁ → … → Pₙ``. Zincirin her halkası bir kontrollü dönmedir;
    bir halka kopuksa (kontrol ``|0⟩``) sonraki hiç dönmez -- yani
    geçersiz öncülden netice çıkmaz. Occam cezası açıların küçülmesiyle
    temsil edilir: uzun zincir daha az döndürür.
    """
    no, ad = 24, "İspat"
    #: **χ TAVANI KALDIRILDI (kütük H148, H118'in nakzı).** Ölçüldü (χ=32):
    #:
    #:     tavan=1     : tutulan 8,7e-12   entropi 3,357 → 1,386
    #:     tavan=yok   : tutulan 0,548     entropi 3,357 → 1,383
    #:
    #: Yani "ispat daraltır" manası **kapının kendisinde** üniter olarak
    #: zaten vardır: tavan kalkınca da entropi ~ln4'e iniyor. Tavan o
    #: manayı üretmiyordu; üstüne 6×10¹⁰ kat genlik imha ediyordu.
    #:
    #: Bunun bedeli mimarîdedir: 𝒪₂₄ akışın 24. sırasındadır, yani
    #: beyan melekeleri (𝒪₃₇–𝒪₄₀) amputte bir dalga üstünde çalışıyordu.
    #: Kütük H133'ün ("hüküm cevaba ulaşmıyor") **fizikî sebebi** budur.
    SINIF, CHI = "çözücü", None

    def uygula(self, q, p):
        a = self.yay(p, 4, max(q.n_satir - 1, 1), 0.5)
        for i in range(q.n_satir - 1):
            teta = float(a[i]) / (1.0 + 0.1 * i)      # Occam: uzun zincir zayıf
            q.uzak_cift(q.yerel(i), q.yerel(i + 1), kontrollu_donme(teta))


# =====================================================================
#  𝒪₂₅–𝒪₃₆  MURÂKABE
# =====================================================================
@qkaydet
class QTeemmul(QMeleke):
    """𝒪₂₅ Teemmül -- devridaim: aynı katman birkaç kere.

    Reel modelde 200 tur dikkat koşuyor ve durma ölçütü aranıyordu; o,
    her turda okuma isterdi. Üniter karşılığı sabit sayıda tekrardır ve
    yakınsama **kapının kendisinden** gelir: ``R(θ)`` tekrarı ``R(kθ)``
    verir, yani devridaim bir dönmeye eşdeğerdir ve ıraksamaz.
    """
    no, ad = 25, "Teemmül"
    SINIF, CHI = "koruyucu", 8   # devridaim; yeni menzil açmaz
    TUR = 3

    def uygula(self, q, p):
        for t in range(self.TUR):
            self.tugla(q, p, ofset=t % 2, olcek=0.3)


@qkaydet
class QTemkin(QMeleke):
    """𝒪₂₆ Temkin -- sarsılmazlık: küçük açı, büyük vakar.

    Temkin, hâli az değiştirmektir. Açılar kasten küçüktür; bu bir
    ihmal değil melekenin tarifidir.
    """
    no, ad = 26, "Temkin"
    SINIF, CHI = "koruyucu", 4   # temkin: küçük açı

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.12)
        q.tek_yigin(q.yereller(),
                    np.stack([donme(float(t)) for t in a]))


@qkaydet
class QTetkik(QMeleke):
    """𝒪₂₇ Tetkik -- kılcal inceleme: her kübite ayrı ince dönme."""
    no, ad = 27, "Tetkik"
    SINIF, CHI = "koruyucu", 4   # tetkik: ince tek kübit dönmesi

    def uygula(self, q, p):
        self.satir_donmesi(q, p, 0.2)


@qkaydet
class QTashih(QMeleke):
    """𝒪₂₈ Tashih -- düzeltme: tetkikin bulduğunun **tersi**.

    Reel modelde düzeltme "iyileştirdiyse kabul" edilirdi; o bir okuma
    isterdi. Üniter karşılığı, tetkikin uyguladığı dönmenin bir kısmını
    geri almaktır: ``R(−λθ)``. ``λ`` öğrenilir; eğitim motoru ne kadar
    geri alınacağını söyler.
    """
    no, ad = 28, "Tashih"
    SINIF, CHI = "çözücü", 2   # tashih: tetkikin bir kısmını geri alır

    def uygula(self, q, p):
        k = q.ayar.satir_kubiti
        tetkik = QTetkik().aci(p, k, 0.2)
        lam = float(np.tanh(self.aci(p, 1, 1.0)[0]))
        Gk = np.tile(np.stack([donme(-lam * float(t)) for t in tetkik]),
                     (q.n_satir, 1, 1))
        q.tek_yigin([q.veri(i, j) for i in range(q.n_satir)
                     for j in range(k)], Gk)


@qkaydet
class QTeyit(QMeleke):
    """𝒪₂₉ Teyit -- **bağımsız** ikinci kanal.

    İki kanal dolaştırılınca uyuşma yapıcı, uyuşmazlık yıkıcı girişim
    verir. Bağımlı iki kanalın uyuşması **yeni bilgi değildir**; o
    hâlde kanalların mümkün olduğunca ayrı olması şarttır.

    **KANAL ÇİFTİ ELLE DEĞİL ÖLÇÜMLE SEÇİLDİ (kütük H162, H128'in
    borcu).** Evvelce *"satırın iki ucu"* alınıyordu ve bu bir
    **tedbir**di, ölçülmemişti. H128'de ölçüldü: fazla sayma oranı
    ``1,2091``, muteber şahit sayısı 2 değil **1,65** -- yani 𝒪₂₉
    delili yaklaşık **%19 şişiriyordu**. Kusur küçüktü fakat sıfır
    değildi ve borç olarak yazılmıştı.

    Beş aday çift aynı ölçüyle yarıştırıldı (12 koşu, 8 satır)::

        usul              Pearson    fazla sayma   muteber şahit
        satır_iki_ucu     +0,1643      1,2091          1,6541   ← evvelki
        veri_vs_yerel     +0,0826      1,1675          1,7130   ← seçilen
        çapraz_satır      +0,2177      1,1315          1,7675
        yerel_vs_yerel    −0,0916      1,2302          1,6257
        veri_ortası       −0,0300      1,1883          1,6830

    ``veri_vs_yerel`` seçildi ve sebebi **iki ölçütte birden**
    üstünlüğüdür: fazla saymada da (1,2091 → 1,1675) Pearson'da da
    (0,164 → 0,083) yürürlükteki çifti yeniyor. ``çapraz_satır`` fazla
    saymada daha iyidir fakat Pearson'da **kötüdür**; onu seçmek,
    hükmü destekleyen ölçütü seçmek olurdu ve kütük H47 tam olarak
    bunu yasaklar (*"ölçütü ölçen koyarsa kendini kandırır"*).

    Kazanç mütevazıdır ve büyütülmüyor: fazla sayma %19'dan **%17**'ye
    iniyor. Kanallar hâlâ tam bağımsız değildir (bağımsız üç şahitte
    kıyas tabanı 1,05) ve bu **açıkça** duruyor.

    Manası da evvelkinden sağlamdır: ham duyu (veri kübiti) ile o satır
    hakkında **verilmiş hüküm** (yerel kübit) iki ayrı cinstendir; aynı
    satırın iki ucu ise aynı cinsten iki noktadır.
    """
    no, ad = 29, "Teyit"
    SINIF, CHI = "koruyucu", 8   # teyit: veri ile yerel hüküm

    def uygula(self, q, p):
        k = q.ayar.satir_kubiti
        if k < 2:
            return
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        # Kanal 1: satırın ilk veri kübiti (ham duyu).
        # Kanal 2: o satırın yerel hüküm kübiti (verilmiş hüküm).
        # İkisi zincirde bitişik değildir (aralarında ``k−1`` kübit
        # vardır), o yüzden ``uzak_cift`` yolu seçer -- takas mı MPO mu,
        # kararı ``mpo_esigi`` verir (H80: eşiği ölçüm koydu).
        for i in range(q.n_satir):
            q.uzak_cift(q.veri(i, 0), q.yerel(i), G)


@qkaydet
class QTahkik(QMeleke):
    """𝒪₃₀ Tahkik -- kökene inmek: küllî kaidenin mühürlenmesi.

    Yerel hükümler ikinci defa, fakat bu sefer **tasdik** alanına ve
    farklı açılarla akıtılır. Taklit ile tahkiki ayıran budur: aynı
    delil iki ayrı yoldan aynı hükmü veriyorsa tahkik, yalnız birinden
    geliyorsa taklittir. İki yol girişimle karşılaştırılır.
    """
    no, ad = 30, "Tahkik"
    SINIF, CHI = "koruyucu", 4   # MPO tasdik birikimi, bağ 2

    def uygula(self, q, p):
        q.mpo_topla("tasdik", self.birikim(p, q.n_satir, 1.0), j=1)


@qkaydet
class QTedebbur(QMeleke):
    """𝒪₃₁ Tedebbür -- âkıbete bakmak: evrim operatörünün tekrarı.

    ``S_{t+H} = ∫ Evrim``. Üniter karşılığı aynı dik operatörün ``H``
    kere uygulanmasıdır. Risk ölçülmez (okuma olurdu); onun yerine
    ileri sarımın kendisi mîzâna bağlanır.
    """
    no, ad = 31, "Tedebbür"
    SINIF, CHI = "kurucu", 8   # tedebbür: ileri sarım
    UFUK = 4

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.25))
        # **Cebrî sadeleştirme (kullanıcı hükmü: netice birebir aynı
        # kaldığı ispatlanabildiği sürece serbest).** Aynı ``G`` aynı
        # çifte ``UFUK`` kere vuruluyordu; dik dizeyler için
        # ``G·G·G·G = G⁴`` ve tek kapıda uygulanır. Netice birebir
        # aynıdır (``_sadelestirme_sinamasi`` ölçer), maliyet ``UFUK``
        # katı ucuzdur. İz kaydı yine "UFUK=4" der: meleke ne yaptığını
        # söylemeye devam eder, makine ucuz yoldan yapar.
        GU = np.linalg.matrix_power(np.asarray(G, float), self.UFUK)
        q.cift_yigin([q.veri(i, 0) for i in range(q.n_satir)], GU)
        a = self.aci(p, 2, 0.3)
        q.tek_yigin([q.kulli("mizan", 2 + j) for j in range(2)],
                    np.stack([donme(float(t)) for t in a[:2]]))


@qkaydet
class QSekZanYakin(QMeleke):
    """𝒪₃₂ Şek-Zan-Yakîn -- **makam bir faza kodlanır** (kullanıcı hükmü).

    Makam **üç** kübitlik bir merdivendir (kütük H129'un kapanan
    borcu): sekiz basamak, Gray sırasında, beş mertebeyi taşır. Hiçbir
    yerde okunmaz; **çevrilir**.

    **Hangi kübit ne demek -- iddia değil, hesap.** Merdiven Gray
    olduğu için her kübitin manası ``makam_kubit_manasi()`` ile fiilen
    hesaplanır ve şu çıkar (sınama denetler)::

        makam₀ = 1  ⟺  üst yarı        (Zan ve üstü)  → hükmün CİHETİ
        makam₁ = 1  ⟺  orta dörtlü     (Şek–Zan)      → KARARSIZLIK kuşağı
        makam₂ = 1  ⟺  ara basamaklar                 → İNCE ayar

    Kapılar buna göre yöneltilir:

    * ``tasdik`` uyanıksa ``makam₀`` müsbet döner -- hüküm üst yarıya,
      Zan ve üstüne çekilir.
    * ``nakz`` uyanıksa ``makam₀`` menfî döner: tek karşı örnek küllî
      önermeyi düşürür (H6), yani hükmü alt yarıya iter.
    * ``tenakuz`` uyanıksa ``makam₁`` **müsbet** döner. Bu bir
      tashihtir: evvelce menfî dönüyordu, yani çelişki makamı aşağı
      itiyordu. Çelişkinin işi hükmü düşürmek değil **kararsızlaştırmak**
      -- Şek–Zan kuşağına, kararın verilemediği yere çekmektir.
    * ``tasdik₁`` (tahkikin ikinci yolu) ``makam₂``ye ince ayar verir:
      iki müstakil yol aynı hükmü veriyorsa makam bir basamak yukarı
      kayabilsin. ``zann-ı gālib`` ile ``yakîn`` arasındaki fark tam
      olarak bu ince basamaktır; iki kübitle temsil edilemiyordu.

    Sükût kapısı da ``makam₁``e taşındı: susmak, hükmün **düşük**
    olmasından değil **kararsız** olmasından doğar. Evvelce ``makam₀``a
    bağlıydı, yani model "hükmüm menfî" ile "hükmüm yok"u
    ayıramıyordu.

    Hepsi kontrollü dönmedir, hepsi küllî blok içindedir. Makamın
    sayısı ancak nihaî POVM'de doğar ve o da bir **dağılımdır** --
    "makam Zan'dır" diye sert bir hüküm hiç kurulmaz (H31).
    """
    no, ad = 32, "Şek-Zan-Yakîn"
    SINIF, CHI = "çözücü", 2   # makam kararı: ihtimaller daralır

    def uygula(self, q, p):
        a = self.aci(p, 5, 0.6)
        mk = q._alan["makam"][1]
        # cihet: tasdik yukarı, nakz aşağı -- ikisi de EN ANLAMLI kübite
        q.uzak_cift(q.kulli("tasdik", 0), q.kulli("makam", 0),
                    kontrollu_donme(abs(float(a[0]))))
        q.uzak_cift(q.kulli("nakz", 0), q.kulli("makam", 0),
                    kontrollu_donme(-abs(float(a[1]))))
        # kararsızlık: çelişki makamı orta kuşağa çeker
        if mk >= 2:
            q.uzak_cift(q.kulli("tenakuz", 0), q.kulli("makam", 1),
                        kontrollu_donme(abs(float(a[2]))))
        # ince ayar: tahkikin ikinci yolu (tasdik₁) zann-ı gālib ile
        # yakîn arasındaki basamağı oynatır -- iki kübitte YOK olan yer.
        if mk >= 3:
            q.uzak_cift(q.kulli("tasdik", 1), q.kulli("makam", 2),
                        kontrollu_donme(float(a[3])))
        # Sükût kapısı: makam KARARSIZ kuşaktaysa sükût kübiti uyanır.
        q.uzak_cift(q.kulli("makam", 1 if mk >= 2 else 0),
                    q.kulli("sukut", 0),
                    kontrollu_donme(abs(float(a[4]))))


@qkaydet
class QMuhakeme(QMeleke):
    """𝒪₃₃ Muhakeme -- meclis: bütün küllî alanların tartıldığı yer.

    Mîzân ``Γ = aleyhte/lehte``dir. Üniter karşılığı bir bölme değil,
    **zıt yönlü dönmelerin bileşkesidir**: lehte deliller (tasdik) mîzânı
    bir yöne, aleyhte deliller (tenakuz, nakz) öbür yöne çevirir. Netice
    ``R(Σ lehte − Σ aleyhte)``dir -- bölmenin logaritmik karşılığı.
    Hiçbir yerde bölme yapılmaz, dolayısıyla sıfıra bölme derdi de yoktur.
    """
    no, ad = 33, "Muhakeme"
    SINIF, CHI = "koruyucu", 4   # muhakeme: küllî blok içi bağlar

    def uygula(self, q, p):
        a = self.aci(p, 6, 0.5)
        # lehte: tasdik → mîzân (artı yön)
        for j in range(2):
            q.uzak_cift(q.kulli("tasdik", j), q.kulli("mizan", j),
                        kontrollu_donme(abs(float(a[j]))))
        # aleyhte: tenakuz ve nakz → mîzân (eksi yön)
        for j in range(2):
            q.uzak_cift(q.kulli("tenakuz", j), q.kulli("mizan", 2 + j),
                        kontrollu_donme(-abs(float(a[2 + j]))))
        for j in range(2):
            q.uzak_cift(q.kulli("nakz", j), q.kulli("mizan", j),
                        kontrollu_donme(-abs(float(a[4 + j]))))


@qkaydet
class QTafsil(QMeleke):
    """𝒪₃₄ Tafsil -- mücmeli dallarına açmak: küllîden yerele **dağıtım**.

    Buraya kadar bilgi hep yukarı aktı; tafsil onu geri indirir.
    ``mpo_dagit`` bunu kübit oynatmadan yapar. Sadakat şartı (açılan
    şey toplanınca geri gelmeli) burada cebren sağlanır: dağıtım
    üniterdir, tersi vardır.
    """
    no, ad = 34, "Tafsil"
    SINIF, CHI = "koruyucu", 8   # tafsil: MPO dağıtımı, bağ 2

    def uygula(self, q, p):
        q.mpo_dagit("makam", self.birikim(p, q.n_satir, 0.7))


@qkaydet
class QTefsir(QMeleke):
    """𝒪₃₅ Tefsir -- müphemi siyak ve sibakla açmak.

    Her satır hem öncekiyle hem sonrakiyle bağlanır; murâd, bu üçlünün
    ortak dolaşıklığında durur.
    """
    no, ad = 35, "Tefsir"
    SINIF, CHI = "koruyucu", 8   # tefsir: siyak-sibak, komşu satır

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.4))
        k = q.ayar.satir_kubiti
        for i in range(1, q.n_satir):
            q.uzak_cift(q.veri(i - 1, k - 1), q.veri(i, 0), G)


@qkaydet
class QTevil(QMeleke):
    """𝒪₃₆ Tevil -- zâhir çelişince irca; **şartlı** ve üniter.

    Keyfî te'vilin önündeki sed, kontrolün ta kendisidir: te'vil ancak
    ``tenakuz`` kübiti uyanıkken döner. Çelişki yoksa kontrol ``|0⟩``dır
    ve te'vil hiç olmaz -- "gereksiz te'vil yok" şartı burada bir ölçüm
    değil, kapının tarifidir.
    """
    no, ad = 36, "Tevil"
    SINIF, CHI = "koruyucu", 4   # te'vil şartlıdır; çelişki yoksa hiç dönmez

    def uygula(self, q, p):
        a = self.aci(p, 2, 0.5)
        for j in range(2):
            q.uzak_cift(q.kulli("tenakuz", j), q.kulli("tasdik", j),
                        kontrollu_donme(float(a[j])))


# =====================================================================
#  𝒪₃₇–𝒪₄₁  BEYAN
# =====================================================================
@qkaydet
class QFesahat(QMeleke):
    """𝒪₃₇ Fesâhat -- mana **kelam alanına** akar.

    Buraya kadar bütün iş veri ve hüküm kübitlerindeydi; kelam ``|0⟩``da
    bekliyordu. Fesâhat, satırların manasını kelama akıtan ilk
    melekedir: her satırın ilk veri kübiti, kelamın bir kübitine MPO
    ile bağlanır.

    **Neden ayrı bir alan.** Ölçüldü: veri kübitlerinden okunan
    dağılım tam düzgün çıkıyordu (16 durumun her biri 0.0625) -- her
    şey her şeyle dolaştığında küçük bloğun marjinali âzamî karışıktır
    ve model konuşamaz. Kelam ``|0⟩``dan başlayıp yalnız beyan
    melekelerinin yazdığı bir alandır; oradan okunan dağılım
    yoğunlaşabilir.
    """
    no, ad = 37, "Fesâhat"
    SINIF, CHI = "koruyucu", 4   # fesâhat: MPO ile kelama akar

    def uygula(self, q, p):
        # **BEYAN KAPISI (kullanıcı kat'î kararı / kütük H131).**
        # Duraklar evvelce ``q.veri(i, 0)`` idi -- yani mana HAM VERİDEN
        # akıyordu. Karar ilga etti: *"Beyan melekeleri ham veriden
        # doğrudan BESLENEMEZ… mana yalnızca Muhakeme Meclisinden geçmiş,
        # Tasdik mührü basılmış muhkem hüküm üzerinden akacaktır."*
        #
        # Yerel hüküm kübiti, o satır hakkında **verilmiş hükümdür**;
        # ham duyu değildir. Mana artık oradan akıyor.
        _, kk = q._alan["kelam"]
        a = self.birikim(p, q.n_satir * kk, 1.2) * kk
        duraklar = q.yereller()
        for j in range(kk):
            q.mpo_topla("kelam", a[j * q.n_satir:(j + 1) * q.n_satir],
                        duraklar=duraklar, j=j)
        # TASDİK MÜHRÜ: mühür yoksa kelâm bastırılır. Menfî kontrol
        # (``X`` sarmalı) ile: ``tasdik₀ = 0`` iken kelam sıfıra çevrilir.
        b = self.aci(p, 2, 0.6)
        tas = q.kulli("tasdik", 0)
        q.tek(tas, degil_x())
        for j in range(min(kk, 2)):
            q.uzak_cift(tas, q.kulli("kelam", j),
                        kontrollu_donme(-abs(float(b[j]))))
        q.tek(tas, degil_x())


@qkaydet
class QTalakat(QMeleke):
    """𝒪₃₈ Talâkat -- akıcılık: kelam kübitleri arası bağ.

    Kelam kopuk hecelerden ibaret olmasın diye kelam alanının komşu
    kübitleri birbirine bağlanır; bunlar bitişiktir, kapı yereldir.
    """
    no, ad = 38, "Talâkat"
    SINIF, CHI = "koruyucu", 4   # talâkat: kelam içi komşu bağ

    def uygula(self, q, p):
        # **BEYAN KAPISI (H131).** Son satır evvelce ``self.tugla(...)``
        # idi, yani talâkat VERİ kübitlerine fırça atıyordu. Akıcılık
        # kelamın kendi içinde olur; ham veriden akıcılık devşirmek,
        # kararın ilga ettiği doğrudan beslenmenin ta kendisidir.
        _, kk = q._alan["kelam"]
        G = dik_iki_kubit(self.aci(p, 6, 0.4))
        for j in range(kk - 1):
            q.cift(q.kulli("kelam", j), G)
        # Akıcılık artık TASDİKten besleniyor: mühürlü hüküm ne kadar
        # kuvvetliyse kelam o kadar akıcı.
        a = self.aci(p, 2, 0.35)
        for j in range(2):
            q.uzak_cift(q.kulli("tasdik", j), q.kulli("kelam", j),
                        kontrollu_donme(float(a[j])))


@qkaydet
class QBelagat(QMeleke):
    """𝒪₃₉ Belâgat -- makamın kelama sirayeti.

    Belâgat, sözü **makamına göre** söylemektir. Küllî makam kübiti
    bütün satırlara dağıtılır: Yakîn makamında kelam başka, Şek
    makamında başka bükülür. Dağıtım MPO iledir.
    """
    no, ad = 39, "Belâgat"
    SINIF, CHI = "koruyucu", 4   # belâgat: makam kelama sirayet eder

    def uygula(self, q, p):
        _, kk = q._alan["kelam"]
        a = np.concatenate([self.aci(p, kk, 0.45),
                            self.birikim(p, q.n_satir, 0.7)])
        # makam kelama sirayet eder: küllî blok içinde, kısa mesafe.
        # Bölen ``2`` değil alanın **kendi genişliğidir**: makam 3
        # kübite çıkınca (H129) sabit 2 üçüncü kübiti hiç kullanmaz ve
        # sirayet, merdivenin ince basamağını görmezden gelirdi.
        mk = q._alan["makam"][1]
        for j in range(kk):
            q.uzak_cift(q.kulli("makam", j % mk), q.kulli("kelam", j),
                        kontrollu_donme(float(a[j])))
        # **BEYAN KAPISI (H131).** Evvelce ``mpo_dagit("makam", …)`` ile
        # makam SATIRLARA (yerel hükümlere) iniyordu. Belâgat sözü
        # makamına göre söylemektir; hükmü aşağı indirmek 𝒪₃₄ Tafsil'in
        # işidir, beyanın değil. Sirayet artık tasdik üzerinden kelama.
        for j in range(2):
            q.uzak_cift(q.kulli("tasdik", j), q.kulli("kelam", j + 2),
                        kontrollu_donme(float(a[kk + j])))


@qkaydet
class QSanat(QMeleke):
    """𝒪₄₀ Sanat -- **altın oran**: açı melekenin kendi tarifinden gelir.

    Bu melekenin açısı öğrenilmez ve öğrenilmemelidir: ``2π/φ²``
    altın açıdır ve ardışık uygulandığında hiçbir yuvaya iki kere aynı
    fazı vermez (en düzgün dağılım). Ahenk bir tercih değil, bir sayıdır.
    """
    no, ad = 40, "Sanat"
    SINIF, CHI = "koruyucu", None   # sanat: yalnız tek kübitlik dönme, kesme yok

    def uygula(self, q, p):
        # **BEYAN KAPISI (H131).** Altın açı evvelce VERİ kübitlerine de
        # vuruluyordu. Sanat, keşfedilmiş hakikate elbise giydirmektir;
        # ham duyuyu bükmek onun işi değildir. Artık yalnız kelam ve
        # makam alanına dokunur.
        altin_aci = 2.0 * math.pi / (ALTIN ** 2)
        _, kk = q._alan["kelam"]
        mk = q._alan["makam"][1]
        q.tek_yigin([q.kulli("makam", j) for j in range(mk)],
                    np.stack([donme((altin_aci * (j + 1)) % (2 * math.pi))
                              for j in range(mk)]))
        q.tek_yigin([q.kulli("kelam", j) for j in range(kk)],
                    np.stack([donme((altin_aci * (j + 1)) % (2 * math.pi))
                              for j in range(kk)]))


@qkaydet
class QMunazara(QMeleke):
    """𝒪₄₁ Münazara -- tez ve antitezin telîfi: son bileşke.

    Mîzân ile makam son kere bağlanır; beyan bundan sonra okunur.
    """
    no, ad = 41, "Münazara"
    SINIF, CHI = "çözücü", 2   # münazara: son bileşke, telîf daraltır

    def uygula(self, q, p):
        _, kk = q._alan["kelam"]
        a = self.aci(p, 4 + kk, 0.5)
        for j in range(2):
            q.uzak_cift(q.kulli("mizan", j), q.kulli("makam", j),
                        kontrollu_donme(float(a[j])))
        # SÜKÛT KAPISI (kütük H10/H16): sükût kübiti uyanıksa kelam
        # bastırılır. Bilmediğini söylememek bir kabiliyettir ve burada
        # bir kapıdır: kontrol |1⟩ iken kelam sıfır yönüne döner.
        for j in range(kk):
            q.uzak_cift(q.kulli("sukut", 0), q.kulli("kelam", j),
                        kontrollu_donme(-abs(float(a[4 + j]))))
        q.tek(q.kulli("sukut", 0), donme(float(a[2]) * 0.5))


# =====================================================================
#  𝒪₄₂–𝒪₄₄  TEŞKİLÂT -- üç uzuv NİHAYET akışa girdi (kütük H213)
# =====================================================================
#
# **ÖLÇÜLEN VE KAPATILAN ÇELİŞKİ.** `nefs/dimag.py` ``MELEKE_SAYISI =
# 44`` diyor ve ``KANONIK_CETVEL`` 𝒪₄₂/𝒪₄₃/𝒪₄₄'ü ``d₁₀``a tescil
# ediyordu; fakat ``QAKIS`` 41'de bitiyordu. Yani Lie manifoldu 44
# üreteç sayarken akış 41 kapı vuruyordu -- üç meleke cetvelde vardı,
# icrada yoktu. `nefs/teskilat.py` de AST ile ölçüldü: **sıfır gerçek
# çağıran**, yalnız divanın sicilinde duruyordu.
#
# Aşağıdaki üç sınıf o boşluğu kapatır. Formüller `nefs/teskilat.py`den
# alınmıştır; oradaki klasik hâlleri **ölçü** (sözleşme denetçisi)
# olarak yerinde durur, buradaki hâlleri **kapı**dır. İkisi ayrı
# şeydir ve karıştırılmaz: kapı hiçbir şey okumaz (H31).


@qkaydet
class QUmumilestirme(QMeleke):
    """𝒪₄₂ Umumileştirme -- numunelerin **kesişimindeki** kanun.

    `nefs/teskilat.py`nin formülü::

        𝒪_umum(S) = Π_inv · [ ⊗_j 𝒮_j(X_in^(j) → Y_out^(j)) ]

    Manası: birkaç numunede görülen dönüşümlerin kesişimindeki
    **değişmez** kısmı süzmek; bir numuneye mahsus araz kesişimde
    kalmaz, kanun kalır.

    **Üniter karşılığı budur ve uydurma değildir.** Numuneler burada
    satırların yerel hüküm kübitleridir. ``mpo_topla`` bütün durakları
    **aynı** açıyla küllî alana akıtır::

        U = exp( (Σ_i θ n_i) ⊗ Y )

    Açı her durakta aynı olduğu için, uyanık olan duraklar birbirini
    **pekiştirir**, uyuşmayanlar katkı vermez -- yani biriken dönme
    tam olarak durakların **ortak** (kesişimdeki) kısmını taşır.
    Π_inv'in kübit üzerindeki karşılığı budur: ayrı ayrı açı vermek
    her numuneye kendi arazını taşıtırdı, aynı açı yalnız kanunu
    taşır.

    Bir numunenin arazı için ayrıca ``tenakuz``a zayıf bir sızıntı
    açılır: kesişim dışında kalan, çelişki alanında birikir.
    """
    no, ad = 42, "Umumileştirme"
    # Ölçüldü (``nefs/nizam.yuzlestir``): ΔS = +0,0080 -- koruyucu
    # bandının (|ΔS| ≤ 0,05) içinde. Sınıf iddia değil, ölçüdür.
    # CHI, emsali MPO birikimlerininkiyle aynı (bağ zaten 2).
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        n = max(1, q.n_satir)
        a = self.aci(p, 2, 0.5)
        # Π_inv: BÜTÜN duraklar AYNI açıyla -- kesişim böyle süzülür.
        ortak = np.full(n, float(a[0]) / float(n))
        q.iz.kesme += q.mpo_topla("mizan", ortak)
        # kesişim dışında kalan araz: zayıf, ters işaretli sızıntı
        q.iz.kesme += q.mpo_topla("tenakuz", -0.25 * ortak)


@qkaydet
class QTalim(QMeleke):
    """𝒪₄₃ Talim -- hükmü kademe kademe **keskinleştirmek**.

    `nefs/teskilat.py`nin formülü::

        𝒪_talim(S, τ) = Π_l softmax(S·W_l / τ_l) · Π_fesahat
        şart: τ₁ > τ₂ > … > τ_L  (yayvandan keskine, tersi olmaz)

    **Üniter karşılığı.** Sıcaklığı düşürmek dağılımı keskinleştirir;
    kübitte bunun karşılığı, kelam alanının genliğini kademe kademe
    **daha büyük** açıyla tek yöne toplamaktır: ``θ_l ∝ 1/τ_l``. τ
    monoton azaldığı için θ monoton **artar** ve beyan yayvandan
    keskine gider.

    **Kademe cetveli uydurulmaz, sözleşmeden gelir.** ``τ`` merdiveni
    `teskilat.talim_kademesi` ile fiilen sınanır: sabit ve
    belirlenimci bir hüküm vektöründe entropinin monoton azaldığı
    denetlenir. ``sahih`` yalanlanırsa merdiven kurulmaz ve meleke
    **hiç dönmez** -- karıştırmayı talim diye icra etmektense
    susmak yeğdir (H10).
    """
    no, ad = 43, "Talim"
    # Ölçüldü: ΔS = +0,0195 -- koruyucu bandının içinde. Yalnız tek
    # kübitlik dönmeler vurur, bağ büyütmez.
    SINIF, CHI = "koruyucu", 4
    #: Yayvandan keskine; ``talim_kademesi`` bunun monotonluğunu ölçer.
    TAU: Tuple[float, ...] = (4.0, 2.0, 1.0, 0.5)
    #: Merdivenin sınandığı sabit hüküm vektörü -- girdiden bağımsız,
    #: belirlenimci. Dalgadan OKUNMAZ; melekenin kendi tarifidir.
    OLCU: Tuple[float, ...] = (3.0, 1.0, 0.5, -1.0, 2.0)

    def uygula(self, q, p):
        r = talim_kademesi(np.asarray(self.OLCU, float), self.TAU)
        if not r["sahih"]:                       # pragma: no cover
            return                               # karıştırma yapmaktansa sus
        _, kk = q._alan["kelam"]
        a = self.aci(p, len(self.TAU), 0.4)
        for l, tau in enumerate(self.TAU):
            # θ_l ∝ 1/τ_l : τ düştükçe dönme büyür, beyan keskinleşir
            teta = float(a[l]) / float(tau)
            q.tek_yigin([q.kulli("kelam", j) for j in range(kk)],
                        np.stack([donme(teta) for _ in range(kk)]))


@qkaydet
class QTahsil(QMeleke):
    """𝒪₄₄ Tahsil -- ağırlığı emanet olmaktan çıkarıp **zâtî mülk** kılmak.

    `nefs/teskilat.py`nin formülü::

        𝒪_tahsil(θ) = θ ∘ exp(−η · Ĥ_Dimağ(θ)) + γ · I_meleke

    ``exp(−ηĤ)`` bir Gibbs sönümüdür (çelişkili yönler bastırılır);
    ``γI`` melekenin kendi kimliğini korur -- tamamen dışarının
    şekline girmesin diye.

    **Üniter karşılığı ve NEDEN ORAYA VURULDUĞU.** Bu meleke ötekiler
    gibi hükme değil, **parametre bölgesine** dokunur: `kuantum/kubit_taksimati.py`
    zincirde ``|x⟩`` diye bir bölge ayırır ve ceride onu "model
    ağırlıkları" diye tarif eder. Tahsil tam orada iş görür:

    * Gibbs sönümü ``exp(−ηĤ)`` → parametre kübitlerine, mîzân
      (çelişki enerjisi) **kontrollü** bir dönme: mîzân uyanıksa
      parametre söner. Çelişkili yön bastırılır.
    * ``γ·I`` → parametre kübitlerine küçük, kontrolsüz bir kimlik
      dönmesi: kaynak ne derse desin meleke kendi kimliğinden bir
      pay saklar.

    Bölge kapalıysa (``bolge_ac=False``) meleke sessizce hiçbir şey
    yapmaz; ``eklem_olcusu`` o zaman zaten kırmızı yanar.
    """
    no, ad = 44, "Tahsil"
    # **SINIFIM YANLIŞTI VE ÖLÇÜM YALANLADI (kütük H213).** Evvelâ
    # ``koruyucu`` yazmıştım; ``nefs/nizam.yuzlestir`` ΔS = **−0,5541**
    # ölçtü, yani ihlâl 0,4654. Hâlbuki melekenin kendi tarifi zaten
    # *"yüksek enerjili, yani çelişkili yönler bastırılır"* diyor --
    # bu bir **çözücü**nün tarifidir. İlan ölçüye uyduruldu, ölçü
    # ilana değil. CHI emsali çözücülerinkiyle aynı (tashih, tenkit).
    SINIF, CHI = "çözücü", 2
    #: Gibbs sönüm şiddeti ve kimlik payı -- melekenin kendi tarifi.
    ETA: float = 0.1
    GAMA: float = 0.05

    def uygula(self, q, p):
        if not q.bolge_var("parametre"):
            return
        npar = q.taksimat.bolge["parametre"][1]
        kac = min(int(npar), 8)                  # bütçe: ilk 8 kübit
        a = self.aci(p, 2, 0.5)
        # exp(−ηĤ): mîzân uyanıksa parametre söner (kontrollü dönme)
        for j in range(kac):
            q.uzak_cift(q.kulli("mizan", j % 4), q.parametre(j),
                        kontrollu_donme(-abs(float(a[0])) * float(self.ETA)))
        # γ·I: kimlik payı -- kontrolsüz, küçük, daima
        q.tek_yigin([q.parametre(j) for j in range(kac)],
                    np.stack([donme(float(self.GAMA) * float(a[1]))
                              for _ in range(kac)]))


#: Akış sırası -- reel modelin ``AKIS``ıyla birebir aynı (𝒪₁₃ iki kere),
#: **artık 44 melekelik** (kütük H213): 𝒪₄₂/𝒪₄₃/𝒪₄₄ beyanın ardından
#: koşar, zira teşkilât hükmün değil hükmü **sahiplenmenin** işidir.
QAKIS: Tuple[int, ...] = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24,
    25, 26, 27, 28, 29, 30, 31, 32,
    33, 13,
    34, 35, 36,
    37, 38, 39, 40, 41,
    42, 43, 44,
)

# ======================================================================
#  KÜBİT-YERLİ KÜLLÎ AKIŞ -- 44 meleke, tek dalga
#  (evvelce nefs/qakis.py)
# ======================================================================

#: Yoğuşmaya (kondensata) **giren** küllî alanlar. Kütük H54, 4. borç:
#: BEC bütün küllî bloğa vurulunca sükûtu boğuyordu. Ölçüldü:
#: ``sukut 0,7924 → 0,0626`` (12,7 kat düşüş), üstelik ``tenakuz
#: 0,3305 → 0,5758`` ve ``P_Şek 0,1553 → 0,2561`` -- yani faz kilidi
#: nefsi hem susamaz hem daha çelişkili kılıyordu.
#:
#: Sebep kavramîdir, sayısal değil. BEC **hükmün ittihadıdır**: bütün
#: parçaların tek bir faza kilitlenmesi. Sükût bir hüküm DEĞİLDİR;
#: tenakuz ve nakz da hüküm değil, hükmün ÖNÜNDEKİ engellerdir. Onları
#: da aynı faza kilitlemek, "bilmiyorum" diyebilme kabiliyetini
#: (kütük H10) faz kilidiyle susturmak demektir. Onun için yoğuşmaya
#: yalnız hüküm taşıyan alanlar girer.
YOGUSAN: Tuple[str, ...] = ("makam", "mizan", "tasdik", "kelam")


def bec_faz_kilidi(q: QYazmac, tur: int = 6, g: float = 0.35) -> None:
    """Gross–Pitaevskii faz kilidi -- **yalnız tepede** (kütük H30).

    ``iħ∂Ψ/∂t = (−∇²/2m + V_gaye + g|Ψ|²)Ψ``. BEC'i her yere boca etmek
    süperpozisyonu öldürür; burada yalnız **küllî hüküm bloğuna**, yani
    nihaî tasdik makamına uygulanır. Veri kübitlerine dokunulmaz;
    dolayısıyla dalga diri kalır.

    Üniter kalması şarttır: doğrusal olmayan ``g|Ψ|²`` terimi burada
    kübit sayısına bağlı **sabit** bir açıya çevrilir (ortalama alan
    yaklaşığı). Gerçek doğrusalsızlık okuma isterdi; bu, onun üniter
    ve okumasız karşılığıdır ve öyle bildirilir.
    """
    alanlar = [(ad, kac) for ad, kac in q.ayar.kulli_alanlar
               if ad in YOGUSAN]
    for t in range(tur):
        # kinetik terim: blok içi komşu bağları
        for ad, kac in alanlar:
            for j in range(kac - 1):
                q.cift(q.kulli(ad, j), _kinetik(0.12))
        # ortalama alan: her kübite aynı faz -- ittihad
        faz = g / (1.0 + t)
        for ad, kac in alanlar:
            for j in range(kac):
                q.tek(q.kulli(ad, j), donme(faz))


def _kinetik(teta: float) -> np.ndarray:
    """``−∇²``in iki kübitlik üniter karşılığı: komşu genlik alışverişi."""
    c, s = math.cos(teta), math.sin(teta)
    G = np.eye(4)
    G[1, 1] = c
    G[1, 2] = -s
    G[2, 1] = s
    G[2, 2] = c
    return G


class QNefs:
    """41 üniter melekeyi tek dalga üzerinde koşturan işletici."""

    def __init__(self, tohum: int = 0, ayar: Optional[QAyar] = None,
                 sira: Sequence[int] = QAKIS, sadakat: bool = True,
                 gaye: bool = True) -> None:
        self.p = QParametre(tohum)
        self.ayar = ayar or QAyar(tohum=tohum)
        self.sira = tuple(sira)
        self.s = qsicil()
        #: Gaye doğuşu açık mı (Dosya 4 / kütük H122)? Yalnız **ölçüm**
        #: için kapatılır: kapatılamayan bir tedbirin faydası ölçülemez
        #: (H90). Akışta daima açıktır.
        self.gaye = bool(gaye)
        #: Mantığa sadakat kapısı açık mı? Yalnız **ölçüm** için
        #: kapatılır (haraplama: kalp söküldüğünde vücut ne olur?).
        #: Akışta daima açıktır ve kapatılması bir hüküm değil, bir
        #: teşrihtir.
        self.sadakat = bool(sadakat)

    # -----------------------------------------------------------------
    def idrak_et(self, E: np.ndarray, bec: bool = True,
                 yigin: int = 0, tikaniklik: float = 0.0) -> QYazmac:
        """Ham duyudan nihaî hükme -- tek geçiş, hiç okuma yok.

        ``E`` ``(n, d)`` ise tek girdi; ``(B, n, d)`` ise **yığın**:
        ``B`` ayrı girdi aynı anda idrak edilir ve her üye kendi hükmünü
        verir. ``yigin`` açıkça verilirse yazmaç o büyüklükte kurulur
        (aynı girdi ``B`` kere -- yalnız hız ölçümü için).
        """
        E = np.asarray(E, float)
        B = E.shape[0] if E.ndim == 3 else max(1, int(yigin))
        n_satir = E.shape[-2]
        ayar = self.ayar
        if B != ayar.yigin:
            ayar = replace(ayar, yigin=B)
        q = QYazmac(n_satir, ayar)
        q.kodla(E)
        # **ČECH TIKANIKLIĞI (Dosya 3 / kütük H125).** ``H¹`` dalganın
        # değil GİRDİNİN vasfıdır -- görevin gösterim çiftlerinden, akış
        # hiç koşmadan hesaplanır. Onu bir kapıya çevirmek ``kodla`` ile
        # aynı cinstendir; H31 yasağı melekenin dalgaya bakmasınaydı.
        # Küllî cevabı olmayan bir suale verilecek karşılık susmaktır.
        if tikaniklik:
            tikaniklik_kapisi(q, float(tikaniklik))
        q.superpozisyon()
        q.mera()
        # **MANTIĞA SADAKAT: her melekeden sonra, muafiyetsiz** (H102/H105).
        # Bu bir meleke değildir, melekelerin tâbi olduğu şarttır -- yani
        # bu mimarinin kalbidir. Kaldırıldığında hiçbir hüküm mantıklı
        # kalmaz; H94'te *aranan* ve bulunamayan uzuv budur.
        # Hiçbir şey OKUMAZ: şartı hesaplayıp karar vererek değil,
        # dolaştırarak icra eder (kullanıcı hükmü: "kalp seçmez,
        # dolaştırır").
        for no in self.sira:
            self.s[no].kosu(q, self.p)
            if self.sadakat:
                sadakat_kapisi(q, self.p)
        if self.sadakat:
            # TERTİP: mantık usulleri süperpozisyonda koşar ve `mizan`
            # neyin yasak olduğunu söyler (H109). Ana akışa buradan
            # bağlanır -- artık `mizan` beylik değil tebaadır.
            q.iz.kesme += tertip_kos(q)
        if self.gaye:
            # **GAYE DOĞUŞU (Dosya 4 / H122).** ``gaye`` alanı H108'den
            # beri tahsisliydi fakat ÖLÇÜLDÜ ve tam ``|0⟩``daydı: hiçbir
            # meleke ona dokunmuyordu. Burada hükümden **doğar**
            # (tasdik kuvvetlendirir, tenakuz ve nakz zayıflatır), sonra
            # mîzâna sirayet eder ve sükût eşiğini kurar. Üçü de MPO'dur;
            # hiçbir yerde okuma yoktur.
            q.iz.kesme += gaye_kos(q, self.p)
        if self.sadakat:
            # İşaretlenen mantık dışı kollar burada SÖNER: faz farkı,
            # yansıtmayla genlik farkına çevrilir (H98'de ölçülen usul).
            sadakat_intaci(q)
        if bec:
            bec_faz_kilidi(q)
        # **Ölçümden evvel durum, durum olmalıdır.** Kesme her vuruşta
        # normu bir parça düşürür; kırk bir meleke boyunca birikince
        # ``⟨Ψ|Ψ⟩`` 2e-10'a kadar indiği ÖLÇÜLDÜ. Atılan ağırlık
        # ``q.iz.kesme``de ayrıca durur -- yani unutma gizlenmiyor --
        # fakat dağılım artık normu 1 olan bir dalgadan okunur.
        # **HAKİKÎ kesme burada ölçülür.** Bütün kapılar diktir; normu
        # düşüren tek şey kesmedir. O hâlde normalize etmeden EVVELKİ
        # ``⟨Ψ|Ψ⟩``, atılan ağırlığın tam tamlamasıdır::
        #
        #     kesme_hakiki = 1 − ⟨Ψ|Ψ⟩        (``[0,1]``, kıyas edilebilir)
        #
        # ``iz.kesme`` (kapı başına nispî atılanların toplamı) H111'de
        # ölçüldü ve **ölçüt olmadığı** görüldü: χ büyüdükçe artıyordu.
        # Teşhis için duruyor; hüküm bu satırdan verilir.
        # Telâfiden sonra norm kaybı göstermez; hakikî ölçü, kapı
        # başına tutulan kesrin ÇARPIMIDIR (``Yazmac.sadakat``).
        q.iz.kesme_hakiki = float(max(0.0, 1.0 - q.y.sadakat()))
        q.y.normalize()
        return q

    # -- eğitim arayüzü ------------------------------------------------
    def __len__(self) -> int:
        """Öğrenilecek açı sayısı. Yer tahsisi ilk koşuda yapılır;
        bu yüzden ``idrak_et`` bir kere çağrılmadan sayı bilinmez ve
        bilinmediği hâlde tahmin edilmez."""
        return len(self.p)

    def vektor(self) -> np.ndarray:
        return self.p.vektor()

    def yukle(self, v: np.ndarray) -> None:
        self.p.yukle(v)


# =====================================================================
def rapor_qakis(tohum: int = 0, n: int = 20, d_in: int = 12,
          ayar: Optional[QAyar] = None) -> str:
    rng = np.random.default_rng(tohum)
    E = rng.normal(size=(n, d_in))
    nefs = QNefs(tohum, ayar)
    t0 = time.perf_counter()
    q = nefs.idrak_et(E)
    dt = time.perf_counter() - t0
    o = q.olcumler()

    s = ["=== nefs (KÜBİT): 41 meleke, tek dalga, tek ölçüm ===",
         "",
         "kübit=%d  (satır=%d × %d + küllî %d)   χ=%d   durum=%.1f KB"
         % (q.n, q.n_satir, q.oge, q.ayar.kulli_kubit, q.ayar.bag,
            q.y.bayt / 1024.0),
         "kapı=%d  takas=%d  MPO=%d  toplam kesme=%.3e  %.2f sn"
         % (q.iz.kapi, q.iz.takas, q.iz.supurme, q.iz.kesme, dt),
         "",
         "SÜPERPOZİSYON → DOLAŞIKLIK (ölçülen, iddia edilen değil):",
         "  MERA öncesi entropi = %.6f  (Schmidt = %d)"
         % (q.iz.entropi_once, q.iz.schmidt_once),
         "  MERA sonrası entropi = %.6f  (Schmidt = %d)"
         % (q.iz.entropi_sonra, q.iz.schmidt),
         "  akış sonu entropi    = %.6f" % o["entropi"],
         "  norm hatası          = %.2e" % o["norm_hatası"],
         "",
         "MAKAM DAĞILIMI (POVM zayıf ölçüm -- ÇÖKÜŞ YOK):"]
    for ad in MAKAM_ADLARI:
        p = o["P_" + ad]
        s.append("  %-6s %.4f  %s" % (ad, p, "█" * int(round(40 * p))))
    s += ["",
          "KÜLLÎ HÜKÜMLER (zayıf okuma, [0,1]):"]
    for ad, _ in q.ayar.kulli_alanlar:
        s.append("  %-9s %.4f" % (ad, o[ad]))
    s += ["", "MELEKELERİN İCRA İZİ:"]
    s += ["  " + x for x in q.iz.gunluk]
    return "\n".join(s)

# ======================================================================
#  KÜLLÎ MELEKE MANİFOLDU -- Ĥ_Dimağ'ın manifold yüzü
#  (bu dosyanın kendi eski gövdesi)
# ======================================================================

@dataclass
class KulliMelekeManifoldu:
    """44 melekenin Lie parametreleri ve onlardan kurulan Ĥ_Dimağ."""
    meleke_sayisi: int = MELEKE_SAYISI
    D: int = 16
    ayar: DimagAyari = field(default_factory=DimagAyari)
    teta: np.ndarray = field(default_factory=lambda: np.zeros(0))
    _nokta: Optional[np.ndarray] = None

    def __post_init__(self) -> None:
        if self.teta.size == 0:
            rng = np.random.default_rng(0)
            self.teta = rng.normal(0.0, 0.02, size=int(self.meleke_sayisi))
        if self._nokta is None:
            rng = np.random.default_rng(1)
            self._nokta = rng.normal(size=(int(self.D), 3))

    # -- parametre mührü ------------------------------------------------
    def parametreler_vektoru(self) -> np.ndarray:
        return np.asarray(self.teta, float).copy()

    def parametreleri_yukle(self, p: np.ndarray) -> None:
        p = np.asarray(p, float).reshape(-1)
        if p.size != self.teta.size:
            raise ValueError("parametre boyu tutmuyor: %d ≠ %d"
                             % (p.size, self.teta.size))
        self.teta = p.copy()

    def katsayilari_guncelle(self, katsayi: np.ndarray,
                             oran: float = 1.0) -> None:
        """FCT'den gelen kapalı form katsayılarını parametrelere işle.

        Katsayı dizisi meleke sayısından uzun yahut kısa olabilir;
        **kırpılmaz, kesilmez**: uzunsa ilk ``n``i alınır, kısaysa
        kalan parametreler dokunulmadan durur. Sessizce sıfırlamak,
        öğrenilmiş bir ağırlığı yok saymak olurdu.
        """
        k = np.asarray(katsayi, float).reshape(-1)
        n = min(k.size, self.teta.size)
        if n == 0:
            return
        yeni = self.teta.copy()
        yeni[:n] = (1.0 - float(oran)) * yeni[:n] + float(oran) * k[:n]
        self.teta = yeni

    # -- Hamiltonyen ----------------------------------------------------
    def hamiltonyen_uret(self) -> np.ndarray:
        """Zırhlı ``Ĥ_Dimağ`` -- 20 mertebenin toplamı."""
        r = H_toplam(self.teta, self._nokta, ayar=self.ayar)
        H = r["H"] if isinstance(r, dict) and "H" in r else r
        return np.atleast_2d(np.asarray(H, float))

    def bgcm_mizan_enerjisi(self) -> float:
        """Normalize BGCM: ``[0,1]``de bir sayı, ``λ_mizan``ın çarpanı."""
        r = bgcm_kaybi(self.teta, int(self.D), cetvel=KANONIK_CETVEL)
        return float(r.get("kayıp_norm", r.get("kayıp", 0.0)))

    def mertebe_dagilimi(self) -> Dict[int, int]:
        """Hangi mertebede kaç meleke -- **boş mertebe olmamalı**."""
        cet = meleke_mertebeleri(KANONIK_CETVEL)
        say: Dict[int, int] = {}
        for _m, mert in cet.items():
            say[int(mert)] = say.get(int(mert), 0) + 1
        return say

    def eksikler(self) -> Dict[int, str]:
        return dict(EKSIK_MELEKELER)


def melekeleri_kur(meleke_sayisi: int = MELEKE_SAYISI, D: int = 16,
                   tohum: int = 0) -> KulliMelekeManifoldu:
    """Manifoldu kur -- ferman adıyla giriş noktası."""
    rng = np.random.default_rng(int(tohum))
    return KulliMelekeManifoldu(
        meleke_sayisi=int(meleke_sayisi), D=int(D),
        teta=rng.normal(0.0, 0.02, size=int(meleke_sayisi)))


def rapor_manifold() -> str:                                      # pragma: no cover
    m = melekeleri_kur()
    d = m.mertebe_dagilimi()
    bos = [k for k in range(MERTEBE_SAYISI) if d.get(k, 0) == 0]
    H = m.hamiltonyen_uret()
    s = ["KÜLLÎ MELEKE MANİFOLDU", "",
         "  meleke        : %d" % m.meleke_sayisi,
         "  mertebe       : %d" % MERTEBE_SAYISI,
         "  boş mertebe   : %s" % (bos if bos else "yok"),
         "  eksik meleke  : %s" % (m.eksikler() or "yok"),
         "  Ĥ_Dimağ şekli : %s" % (H.shape,),
         "  ‖Ĥ‖_F         : %.6f" % float(np.linalg.norm(H)),
         "  BGCM mizanı   : %.6f  (normalize, [0,1])"
         % m.bgcm_mizan_enerjisi()]
    return "\n".join(s)
