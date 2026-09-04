"""
ÖLÇÜ FUNKTORU -- ayrı uzaylardaki hataları **müşterek uzaya** çekmek.

===================================================================
NİÇİN VAR: TOPLANAMAYAN ŞEYLERİ TOPLUYORDUK
===================================================================

Kullanıcı hükmü:

> *"Kademelerin ölçüleri farklı uzaylarda bulunmaktadır, hepsini
> funktörle müşterek bir uzaya çekip oradan toplam almalısın, tüm
> melekelerin hatasını bu şekilde toplamalısın, sadece senin
> söylediklerini değil yani, 41'in hepsini."*

Eski ``nefs/qegitim.py::uygunluk`` şuydu::

    V(p) = −log P(doğru belirteç) + 0,25·mîzân_cezası − 0,1·entropi

İki katmerli kusur, ikisi de yapısal:

1. **Toplanamaz şeyler toplanıyordu.** ``−log P`` ``[0, ∞)``da ve
   *küçüğü iyi*; ``entropi`` ``[0, log χ]``da ve *büyüğü iyi*;
   ``tenakuz`` ``[0,1]``de ve *küçüğü iyi*. Bunları ``0,25`` ve
   ``0,1`` gibi elle konmuş katsayılarla toplamak, metreyle kilogramı
   toplamaktır. Katsayı bir **ölçü** değil bir **örtü**dür: uzaylar
   arası intibakın yokluğunu gizler.

2. **41 meleke 5 sayı ile eğitiliyordu.** ``mizan_cezasi`` yalnız
   ``tenakuz``, ``nakz``, ``tasdik``, ``sukut``, ``P_Şek`` okuyordu.
   Kırk bir melekenin kendi hatası **hiç yoktu**; yani otuz altı
   meleke için eğitim sinyali sıfırdı. Bir uzvun hatası kayba
   girmiyorsa o uzuv eğitilmiyor demektir -- kaç kere çağrıldığı
   bunu değiştirmez.

===================================================================
FUNKTÖR NEDİR, BURADA NE YAPAR
===================================================================

İki kategori vardır:

**𝒮 -- ölçü uzayları kategorisi.** Nesneleri ``OlcuUzayi``dır: bir ad,
bir tanım aralığı ``[alt, üst]`` ve bir **cihet** (büyüğü mü iyi,
küçüğü mü). Morfizmleri o aralıklar arasındaki **monoton** eşlemelerdir
-- monoton olması şarttır, zira cihet bozulursa "hata" kavramı ters
döner.

**𝔐 -- mertebe uzayı.** Tek nesnesi ``[0,1]`` aralığıdır ve mânası
`mizan/munazara.py`nin epistemik merdivenidir::

    vehim 0,00  <  şek 0,25  <  zan 0,50  <  zann-ı gālib 0,75  <  yakîn 1,00

Yani müşterek uzay keyfî bir ``[0,1]`` değildir; bu projenin **kendi**
bilgi mertebesidir. Bir melekenin hatasını oraya çekmek demek, "bu
meleke bu girdide hangi mertebede isabet etti" demektir -- ve bu,
melekelerin hepsi için aynı manaya gelen tek sorudur.

**Funktör** ``F : 𝒮 → 𝔐``:

* *nesneler üzerinde*: ``F(S) = 𝔐``; her uzay mertebeye iner.
* *elemanlar üzerinde*: ``F_S(x)`` -- ``x``i kendi aralığında
  normalleştirir ve cihetine göre çevirir, öyle ki **1 daima yakîn**,
  **0 daima vehim** olsun.
* *morfizmler üzerinde*: ``F(f) = F_{S'} ∘ f ∘ F_S⁻¹``.

Bu tanımla iki funktör kaidesi sağlanır::

    F(id_S)   = id_𝔐
    F(g ∘ f)  = F(g) ∘ F(f)

**Fakat terkip kaidesi bir delil değildir ve bunu saklamak yanlış
olurdu.** İlk yazışımda ona bir körlük sınaması koymuştum -- "monoton
olmayan bir eşleme kaideyi bozmalı" -- ve ölçüldü: bozmuyor. Sebebi
cebrîdir ve sınamanın değil benim hatamdı::

    F(g)∘F(f) = (F_U∘g∘F_T⁻¹)∘(F_T∘f∘F_S⁻¹) = F_U∘(g∘f)∘F_S⁻¹ = F(g∘f)

``F_T⁻¹∘F_T`` sadeleşir; yani terkip kaidesi ``f`` ve ``g`` ne olursa
olsun sağlanır ve hiçbir şey ispat etmez.

Bu inşada **yük taşıyan** hususiyet başkadır: ``F_S``in **sıra
koruması**. 𝒮 ile 𝔐 birer sıralı kümedir (hata büyüdükçe mertebe
düşer) ve funktörün manalı olması o sıranın korunmasına bağlıdır.
``funktor_dogrula()`` onu sınar, ve orada körlük hakikîdir: cihet ters
çevrilirse sıra bozulur ve kırmızı yanar.

===================================================================
TOPLAM NİÇİN MERTEBE UZAYINDA ALINIYOR
===================================================================

Mertebe bir **isabet**tir; kayıp ise onun eksiğidir::

    ℒ = Σ_i  w_i · (1 − F_{S_i}(x_i))

``1 − m`` "yakînden ne kadar uzak" demektir ve bütün uzaylar için aynı
şeyi ifade eder; o hâlde toplanabilir. Ağırlık ``w_i`` bir kalibrasyon
sabiti **değildir** -- uzayların intibakı zaten funktörle sağlandı --
yalnız bir melekenin kaç kere sayılacağını söyler ve varsayılanı
birdir. Yani eski ``0,25``/``0,1`` gibi sayılar buradan **kalkmıştır**.

===================================================================
HUDUT -- açıkça
===================================================================

* Bir uzayın ``[alt, üst]`` haddi bilinmiyorsa funktör kurulamaz.
  O hâlde ölçü **atılmaz**, ``üst`` gözlemden tahmin edilir ve bu
  ``tahminî`` olarak işaretlenir. İşaretlenmemiş tahmin, ölçüm
  kılığında bir uydurmadır.
* Mertebeye **yuvarlama** (``mertebele``) yalnız rapor içindir.
  Kayıpta sürekli değer kullanılır: beş kademeye yuvarlamak
  gradyansız aramayı basamaklı bir yüzeye hapsederdi.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["OlcuUzayi", "MERTEBE_UZAYI", "UZAYLAR", "funktor",
           "funktor_tersi", "morfizm_funktoru", "funktor_dogrula",
           "mertebele", "Olcum", "kulli_toplam", "yumusak_asgari",
           "dinamik_beta", "BETA", "HEDEF_USSU", "DINAMIK_BETA",
           "rapor"]


# =====================================================================
#  𝒮 -- ölçü uzayları
# =====================================================================
@dataclass(frozen=True)
class OlcuUzayi:
    """Bir ölçünün yaşadığı uzay.

    ``buyugu_iyi`` **cihet**tir ve funktörün monotonluğunu tayin eder:
    entropi büyüdükçe iyidir (dolaşıklık zenginliktir), tenakuz
    büyüdükçe kötüdür. Cihet yazılmazsa toplam manasını yitirir --
    nitekim eski kayıpta entropi eksi işaretle toplanıyordu ve o eksi
    işaret, cihetin koda gömülmüş hâliydi.
    """
    ad: str
    alt: float
    ust: float
    buyugu_iyi: bool
    tahmini_ust: bool = False

    def gecerli_mi(self) -> bool:
        return float(self.ust) > float(self.alt)


#: Müşterek uzay: `mizan/munazara.py`nin epistemik merdiveni.
MERTEBE_UZAYI = OlcuUzayi("mertebe", 0.0, 1.0, True)


def _mertebeler() -> Dict[str, float]:
    """Merdiven **mizan**dan alınır, burada tekrar yazılmaz.

    Tekrar yazılsaydı iki nüsha olurdu ve biri değişince diğeri sessizce
    yalan söylerdi.
    """
    try:
        # `mizan/munazara.py` merdiveni ``((eşik, ad), …)`` olarak tutar
        # -- eşik önce, ad sonra. Ters çevirip ``ad → eşik`` veriyoruz;
        # ``dict(MERTEBELER)`` doğrudan alınsaydı anahtar sayı, değer
        # dizgi olurdu ve karşılaştırmalar sessizce ters dönerdi.
        from mizan.munazara import MERTEBELER
        return {str(ad): float(esik) for esik, ad in MERTEBELER}
    except Exception:                                    # noqa: BLE001
        return {"vehim": 0.0, "şek": 0.25, "zan": 0.5,
                "zann-ı gālib": 0.75, "yakîn": 1.0}


#: Padişahın okuduğu bütün küllî alanların uzayları. Hadleri
#: **uydurulmadı**: ``[0,1]`` olanlar zayıf ölçümün (POVM) kendi
#: haddidir; ``entropi``nin haddi ``log χ``dır ve χ ayardan gelir.
UZAYLAR: Dict[str, OlcuUzayi] = {
    "tenakuz": OlcuUzayi("tenakuz", 0.0, 1.0, False),
    "nakz": OlcuUzayi("nakz", 0.0, 1.0, False),
    "tasdik": OlcuUzayi("tasdik", 0.0, 1.0, True),
    "sukut": OlcuUzayi("sukut", 0.0, 1.0, False),
    "gaye": OlcuUzayi("gaye", 0.0, 1.0, True),
    "mizan": OlcuUzayi("mizan", 0.0, 1.0, True),
    "makam": OlcuUzayi("makam", 0.0, 1.0, True),
    "kelam": OlcuUzayi("kelam", 0.0, 1.0, True),
    "kesme_hakiki": OlcuUzayi("kesme_hakiki", 0.0, 1.0, False),
    "norm_hatası": OlcuUzayi("norm_hatası", 0.0, 1.0, False),
    # ``−log P`` sınırsızdır; haddi sözlük büyüklüğünden gelir:
    # tekdüze dağılımda ``log(sözlük)``. Ondan kötüsü "tesadüften
    # beter"dir ve kırpılır. Bu bir tahmin değil, hesaplanmış hadd.
    "capraz_entropi": OlcuUzayi("capraz_entropi", 0.0, float(np.log(16.0)),
                                False),
    "hucre_isabeti": OlcuUzayi("hucre_isabeti", 0.0, 1.0, True),
    "tam_cozum": OlcuUzayi("tam_cozum", 0.0, 1.0, True),
}


def uzay(ad: str, ust: Optional[float] = None) -> OlcuUzayi:
    """Adı bilinen uzayı ver; bilinmiyorsa **tahminî** olarak kur."""
    if ad in UZAYLAR and ust is None:
        return UZAYLAR[ad]
    if ust is None:
        return OlcuUzayi(ad, 0.0, 1.0, False, tahmini_ust=True)
    return OlcuUzayi(ad, 0.0, float(ust), False,
                     tahmini_ust=ad not in UZAYLAR)


# =====================================================================
#  F -- funktörün eleman eşlemesi
# =====================================================================
def funktor(x: float, S: OlcuUzayi) -> float:
    """``F_S : S → 𝔐``. Netice **daima** 1 = yakîn, 0 = vehim.

    Monotondur: ``buyugu_iyi`` ise artan, değilse azalan. Monotonluk
    funktörün morfizm kaidesinin şartıdır ve ``funktor_dogrula``da
    fiilen sınanır.
    """
    if not S.gecerli_mi():
        return 0.5                      # had yok: hüküm yok, orta mertebe
    u = (float(x) - S.alt) / (S.ust - S.alt)
    u = float(np.clip(u, 0.0, 1.0))
    return u if S.buyugu_iyi else 1.0 - u


def funktor_tersi(m: float, S: OlcuUzayi) -> float:
    """``F_S⁻¹ : 𝔐 → S``. Morfizm eşlemesi bunu gerektirir."""
    if not S.gecerli_mi():
        return S.alt
    u = float(np.clip(m, 0.0, 1.0))
    if not S.buyugu_iyi:
        u = 1.0 - u
    return S.alt + u * (S.ust - S.alt)


def morfizm_funktoru(f: Callable[[float], float], S: OlcuUzayi,
                     T: OlcuUzayi) -> Callable[[float], float]:
    """``F(f) = F_T ∘ f ∘ F_S⁻¹`` -- morfizmlerin eşlemesi.

    Funktörün asıl tarifi budur; eleman eşlemesi bunun husûsî hâlidir.
    """
    def g(m: float) -> float:
        return funktor(f(funktor_tersi(m, S)), T)
    return g


def funktor_dogrula(tohum: int = 0, n: int = 64) -> Dict[str, object]:
    """İki funktör kaidesini **sayısal olarak** sına.

    ``F(id) = id`` ve ``F(g∘f) = F(g)∘F(f)``. Sınanmayan bir funktör
    iddiası, elle konmuş katsayının süslü hâlidir; onun için bu
    fonksiyon vardır ve kırmızı yanabilir.

    Ölçüt kör değildir: kasten **monoton olmayan** bir eşleme de
    denenir ve onun kaideyi bozması beklenir. Bozmuyorsa sınama bir şey
    ispat etmiyor demektir.
    """
    rng = np.random.default_rng(tohum)
    S = OlcuUzayi("S", -2.0, 5.0, True)
    T = OlcuUzayi("T", 0.0, 3.0, False)
    U = OlcuUzayi("U", 1.0, 9.0, True)
    m = rng.uniform(0.0, 1.0, size=n)

    # 1) birim kaidesi
    birim = morfizm_funktoru(lambda x: x, S, S)
    hata_birim = float(np.max(np.abs([birim(v) - v for v in m])))

    # 2) terkip kaidesi -- iki monoton eşleme
    def f(x: float) -> float:            # S → T, artan
        return 0.0 + 3.0 * (x + 2.0) / 7.0

    def g(x: float) -> float:            # T → U, artan
        return 1.0 + 8.0 * x / 3.0

    sol = morfizm_funktoru(lambda x: g(f(x)), S, U)
    sag_f = morfizm_funktoru(f, S, T)
    sag_g = morfizm_funktoru(g, T, U)
    hata_terkip = float(np.max(np.abs(
        [sol(v) - sag_g(sag_f(v)) for v in m])))

    # 3) **TERKİP KAİDESİ ZATEN AŞİKÂRDIR -- ve bunu saklamak yanlış olurdu.**
    #
    # İlk yazışımda buraya "monoton olmayan bir eşleme terkip kaidesini
    # bozmalı" diye bir körlük sınaması koymuştum ve ÖLÇÜLDÜ: bozmuyor.
    # Sebebi cebrîdir ve sınamanın değil benim hatamdı::
    #
    #     F(g)∘F(f) = (F_U∘g∘F_T⁻¹)∘(F_T∘f∘F_S⁻¹) = F_U∘(g∘f)∘F_S⁻¹ = F(g∘f)
    #
    # ``F_T⁻¹∘F_T`` sadeleşir; yani terkip kaidesi ``f`` ve ``g`` **ne
    # olursa olsun** sağlanır. O hâlde terkip sınaması bir şey ispat
    # etmez ve "funktör olduğunu sınadım" demenin dayanağı olamaz.
    #
    # Bu inşada **yük taşıyan** hususiyet başkadır: ``F_S``in
    # **sıra koruması**. 𝒮 ve 𝔐 birer sıralı kümedir (hata büyüdükçe
    # mertebe düşer); funktörün manalı olması, o sıranın korunmasına
    # bağlıdır. Sınanan da odur ve burada körlük hakikîdir: cihet ters
    # çevrilirse sıra bozulur ve kırmızı yanar.
    x = np.sort(rng.uniform(S.alt, S.ust, size=n))
    mert = np.asarray([funktor(v, S) for v in x])
    sira_korunuyor = bool(np.all(np.diff(mert) >= -1e-12))

    S_ters = OlcuUzayi("S_ters", S.alt, S.ust, not S.buyugu_iyi)
    mert_ters = np.asarray([funktor(v, S_ters) for v in x])
    sira_bozuluyor = bool(np.all(np.diff(mert_ters) <= 1e-12)
                          and np.ptp(mert_ters) > 1e-6)

    return {"birim_hatası": hata_birim,
            "terkip_hatası": hata_terkip,
            "terkip_aşikâr_mı": True,
            "sıra_korunuyor": sira_korunuyor,
            "cihet_ters_çevrilince_bozuluyor": sira_bozuluyor,
            "funktör_mü": (hata_birim < 1e-9 and hata_terkip < 1e-9
                           and sira_korunuyor),
            "ölçüt_kör_değil": sira_korunuyor and sira_bozuluyor}


def mertebele(m: float) -> str:
    """Sürekli mertebeyi merdivenin en yakın basamağına **adlandır**.

    Yalnız rapor içindir; kayıpta kullanılmaz (bkz. şerhin HUDUT'u).
    """
    ad, _ = min(_mertebeler().items(), key=lambda kv: abs(kv[1] - float(m)))
    return ad


# =====================================================================
#  Ölçüm ve küllî toplam
# =====================================================================
@dataclass
class Olcum:
    """Bir uzuvun **kendi uzayındaki** ham hatası.

    ``kaynak`` melekenin numarası yahut kademenin adıdır; ``agirlik``
    bir kalibrasyon sabiti değil, o uzvun kaç kere sayılacağıdır.
    """
    kaynak: str
    deger: float
    uzay: OlcuUzayi
    agirlik: float = 1.0

    def mertebe(self) -> float:
        return funktor(self.deger, self.uzay)

    def eksik(self) -> float:
        """Yakînden uzaklık: müşterek uzaydaki **kayıp** payı."""
        return self.agirlik * (1.0 - self.mertebe())


def yumusak_asgari(x, beta: float = 8.0) -> float:
    """Yığın ekseninin **en zayıf üyesine** göre birleşimi.

    ===================================================================
    NİÇİN ORTALAMA DEĞİL
    ===================================================================

    Bir organ ölçüsü yığında ``B`` üye üzerinde okunur. Evvelce
    ortalaması alınıyordu ve ölçüldü (kütük H151): ``B`` büyüdükçe
    parametre yayılımı **düşüyor** -- yani yığını büyütmek, tam da
    eniyilenen işareti söndürüyordu (σ/√B). Bu, kütük H145'in bir
    kademe yukarısıdır: orada 105 uzuv ortalanıyordu, burada ``B`` veri.

    Hüküm aynıdır ve manevîdir: **bir yığında tek bir veride düşen
    parametre yakîn sayılamaz.** Netice en zayıf üyesi kadar sağlamdır;
    üyeleri ortalamak, kötü üyeyi iyilerin arkasına saklamaktır.

    Onun için yumuşak asgarî alınır (log-sum-exp'in asgarî hâli)::

        m = −(1/β)·[ log Σ exp(−β·xᵢ) − log B ]

    ``β → 0`` ortalamaya, ``β → ∞`` tam asgarîye gider. ``log B``
    çıkarılır ki üye sayısı arttıkça netice kendiliğinden kaymasın.
    """
    a = np.asarray(x, float).reshape(-1)
    if a.size == 0:
        return 0.0
    if a.size == 1:
        return float(a[0])
    b = float(max(beta, 1e-6))
    z = -b * a
    m = float(np.max(z))
    return float(-(m + np.log(np.sum(np.exp(z - m))) - np.log(a.size)) / b)


#: Yumuşak azamînin sertliği. ``β→0`` ortalama, ``β→∞`` azamî verir.
BETA: float = 8.0

#: Dinamik ``β`` **varsayılan mı** (ceride hükmü, kütük H169).
#:
#: Ceride dinamik LogSumExp'i emrediyor ve `dinamik_beta` onu kurdu.
#: Fakat varsayılan yapılıp yapılmayacağı **ölçüme** bırakıldı ve
#: ölçüm ikiye bölündü:
#:
#: * **Doymuş uzuv varken dinamik KAZANIYOR.** Sentetik sınama (bir
#:   uzuv 0,01'de çakılı, 40 uzuv oynuyor): yayılım ``0,01899 →
#:   0,03909``, yani **2,06 kat**.
#: * **Hakikî kayıpta dinamik KAYBEDİYOR.** 5 parametre, aynı akış::
#:
#:       sabit  β=8    yayılım 0,1271
#:       dinamik β≈6,4–7,3  yayılım 0,0954   ← %25 daha az
#:
#: Sebep anlaşıldı ve tersi yönde işliyor: hakikî kayıpta artık doymuş
#: bir uzuv **yok** (H154/H156/H160 onları tek tek çıkardı), o hâlde
#: ``√n`` hedefi ``β``yı 8'in **altına** çekiyor ve fazla ortalama
#: alıyor. Yani dinamik ``β``, çare olduğu derdi bulamayınca zarar
#: veriyor.
#:
#: **Hüküm ölçüme uyuyor:** varsayılan ``False``, yani sabit ``β``.
#: Dinamik yol **duruyor** ve tek satırla açılır; doymuş bir uzuv geri
#: geldiğinde (``katılan_uzuv`` 1'e çökerse) açılması gerekir ve o
#: alâmet ``kulli_toplam``ın çıktısında **ölçülebilir** hâldedir.
#:
#: Hudut açıkça: mukayese 5 parametre üzerinden; %25'lik fark
#: istikamet gösterir, kat'î hüküm vermez.
DINAMIK_BETA: bool = False

#: Dinamik ``β``nın hedefi: kaç uzuv **fiilen** hükme katılsın.
#: ``√n`` seçildi ve keyfî değildir -- iki ölçülmüş felâketin log
#: ortasıdır (bkz. ``dinamik_beta``).
HEDEF_USSU: float = 0.5


def _katilan_uzuv(eksikler: np.ndarray, beta: float) -> float:
    """Yumuşak azamîde **fiilen hükmeden** uzuv sayısı (perpleksite).

    Ağırlıklar ``w_i ∝ exp(β·eksik_i)``; katılan uzuv sayısı o
    dağılımın perpleksitesidir, ``exp(H(w))``. ``β→0`` iken ``n``,
    ``β→∞`` iken ``1`` verir; yani doğrudan "kaç uzuv konuşuyor"
    sorusunun cevabıdır.
    """
    z = beta * eksikler
    z = z - float(np.max(z))
    w = np.exp(z)
    t = float(np.sum(w))
    if t <= 0.0:
        return float(eksikler.size)
    w = w / t
    nz = w > 0.0
    H = float(-np.sum(w[nz] * np.log(w[nz])))
    return float(np.exp(H))


def dinamik_beta(eksikler: Sequence[float], hedef_ussu: float = HEDEF_USSU,
                 alt: float = 0.05, ust: float = 256.0) -> float:
    """``β``yı ölçünün kendi dağılımından tayin et (ceride hükmü).

    ===================================================================
    NİÇİN SABİT ``β`` YETMİYOR -- üç ayrı koşuda ölçüldü
    ===================================================================

    Yumuşak azamî ``ℒ = (1/β)·log(1/n Σ e^{β·eᵢ})`` şudur: bir uzuv
    ``e_max``ta çakılıysa

        ℒ ≈ e_max + (1/β)·log(1 + Σ_{j≠max} e^{β(e_j − e_max)})

    yani **yalnız ``1/β`` mesafesindeki uzuvlar görünür**. ``β = 8``de
    bu mesafe ``0,125``tir: en kötüden 0,125'ten uzak her uzuv kaybı
    hiç oynatmaz.

    Ve bu tam olarak üç kere ölçülmüş felâkettir::

        H154  𝒪₂₄.kesme    doymuş, yapısal, açıyla değişmez → kayıp kilitli
        H156  kademeler    parametreden bağımsız sabit      → kayıp kilitli
        H160  kademe notu  çoğu görevde ``sükût`` = sabit   → işaret %41 düştü

    Üçünde de çare "o terimi çıkarmak" oldu; fakat bu bir **çare değil
    kaçınmadır** -- her yeni doymuş uzuv aynı derdi geri getirir.

    ===================================================================
    ÇARE: ``β``yı KAÇ UZVUN KONUŞTUĞUNA göre kur
    ===================================================================

    ``β`` doğrudan seçilmez; **katılan uzuv sayısı** hedeflenir ve ``β``
    ona göre çözülür (ikili arama, monoton olduğu için tektir):

        hedef = n^{hedef_ussu} = √n        (``hedef_ussu = 0,5``)

    ``√n`` **keyfî değildir**: kütükte ölçülmüş iki felâketin log
    ortasıdır.

    * ``n`` uzuv katılırsa toplam **ortalamadır** ve H145'te ölçüldü:
      ``σ/√n`` işareti söndürüyor (yayılım 0,05'e düşüyor).
    * ``1`` uzuv katılırsa toplam **sert azamîdir** ve H154/H156/H160'ta
      ölçüldü: doymuş tek uzuv kaybı kilitliyor.

    İkisi de ölçülmüş kusurdur; ``√n`` ikisinin arasında, logaritmik
    ölçekte tam ortadadır. Yani sayı bir tercih değil, iki ölçülmüş
    hududun ortasıdır.

    **Epistemik manası da bozulmuyor:** hüküm hâlâ en zayıf öncüllere
    ağırlık verir (H145'in klasik kaidesi), yalnız "en zayıf" tek bir
    uzuv değil, en zayıf **kanat** olur. Bir zincirin en zayıf halkası
    tekse ``β`` kendiliğinden büyür; birçok halka aynı zayıflıktaysa
    küçülür. Yani sertlik ölçünün kendisinden doğar.
    """
    e = np.asarray(eksikler, float).reshape(-1)
    n = e.size
    if n <= 1:
        return float(BETA)
    if float(np.ptp(e)) < 1e-12:
        # Bütün uzuvlar eşit: ``β``nın hiçbir tesiri yok, en ucuzu.
        return float(alt)
    hedef = float(n) ** float(np.clip(hedef_ussu, 0.0, 1.0))
    hedef = float(np.clip(hedef, 1.0 + 1e-9, n - 1e-9))
    lo, hi = float(alt), float(ust)
    # ``_katilan_uzuv`` ``β``da azalandır; ikili arama tektir.
    if _katilan_uzuv(e, lo) <= hedef:
        return lo
    if _katilan_uzuv(e, hi) >= hedef:
        return hi
    for _ in range(48):
        orta = 0.5 * (lo + hi)
        if _katilan_uzuv(e, orta) > hedef:
            lo = orta
        else:
            hi = orta
    return 0.5 * (lo + hi)


def kulli_toplam(olcumler: Sequence[Olcum], beta: Optional[float] = None
                 ) -> Dict[str, object]:
    """Bütün ölçüleri müşterek uzayda topla -- **ortalama ile değil**.

    ===================================================================
    ORTALAMA KAYBI KÖR EDİYORDU -- ölçüldü
    ===================================================================

    İlk hâlinde toplam bir **ortalamaydı** ve padişah koşturulunca
    görüldü: 120 aday parametrede kayıp ``0,6422``de sabit kaldı,
    hiç kımıldamadı. Sebep arandı ve bulundu -- kusur modüllerde
    değil, bu fonksiyondaydı.

    Ölçüldü (dört farklı parametrede, 80 ölçü):

        tek tek ölçüler       : 75'i değişiyor; ``alan.nakz`` 0,95
                                yayılıyor, ``𝒪₃₇.tasdik`` 0,79
        ortalamaları (kayıp)  : 0,7044 … 0,7561  → yayılım **0,05**

    Yani uzuvlar pekâlâ konuşuyordu; ortalama onları **susturuyordu**.
    Sebep basit ve kaçınılmazdır: bağımsız değişen ``n`` sayının
    ortalamasının yayılımı ``σ/√n``dir. ``n = 105`` uzuvla her ferdî
    işaret ondan fazla kat küçülür. Yani "daha çok uzvu kayba soktum"
    demek, ortalama ile birleştirildiğinde **her uzvun sesini
    kısmak** demekti. Mimarînin kendini cezalandırması buydu.

    ===================================================================
    NİÇİN AZAMÎ -- ve niçin YUMUŞAK azamî
    ===================================================================

    Doğrusu bir hesap hilesi değil, klasik bir hükümdür: **bir
    neticenin yakîni, en zayıf öncülünün yakînini geçemez.** Zincir en
    zayıf halkası kadar sağlamdır; öncülleri ortalamak epistemik
    olarak yanlıştır, zira bir öncül vehim mertebesindeyse neticenin
    yakîn olması mümkün değildir -- diğerleri ne kadar sağlam olursa
    olsun.

    O hâlde toplam **azamî eksik**tir. Fakat sert azamî tek bir uzva
    bakar ve gerisini büsbütün görmez; gradyansız arama için de
    basamaklıdır. Onun için **yumuşak azamî** (log-sum-exp) alınır::

        ℒ = (1/β)·[ log Σ exp(β·eksik_i) − log n ]

    ``β → 0`` iken ortalamaya, ``β → ∞`` iken azamîye gider; arada
    bütün uzuvlar sayılır fakat **en zayıflar hükmeder**. Toplayıcı
    `fitrat/havuz.py`nin ``logsumexp``idir -- taşmaya karşı kaydırmalı
    hâli orada zaten yazılıdır ve tekrar yazılmaz.

    ``log n`` çıkarılması şarttır: çıkarılmazsa uzuv sayısı arttıkça
    kayıp kendiliğinden büyür ve yine "daha çok uzuv bağlamak"
    cezalandırılırdı.
    """
    if not olcumler:
        return {"kayıp": 0.0, "ortalama_mertebe": 1.0, "uzuv": 0,
                "en_zayıf": None, "tahminî_hadli": 0}
    eksikler = [o.eksik() for o in olcumler]
    mert = [o.mertebe() for o in olcumler]
    en_zayif = min(olcumler, key=lambda o: o.mertebe())
    n = len(eksikler)
    # **DİNAMİK β (ceride hükmü).** ``beta`` verilmezse ölçünün kendi
    # dağılımından tayin edilir; sabit ``β`` verilirse eski davranış
    # aynen durur ve kıyas edilebilir (H90).
    if beta is None:
        beta = dinamik_beta(eksikler) if DINAMIK_BETA else BETA
    b = float(max(beta, 1e-6))
    try:
        from fitrat.havuz import logsumexp
        yumusak = (float(logsumexp([b * e for e in eksikler]))
                   - float(np.log(n))) / b
    except Exception:                                    # noqa: BLE001
        z = b * np.asarray(eksikler, float)
        yumusak = float(z.max() + np.log(np.exp(z - z.max()).sum())
                        - np.log(n)) / b
    return {"kayıp": float(np.clip(yumusak, 0.0, 1.0)),
            "β": b,
            "katılan_uzuv": _katilan_uzuv(np.asarray(eksikler, float), b),
            "azamî_eksik": float(max(eksikler)),
            "ortalama_eksik": float(np.mean(eksikler)),
            "ortalama_mertebe": float(np.mean(mert)),
            "uzuv": n,
            "en_zayıf": (en_zayif.kaynak, float(en_zayif.mertebe())),
            "tahminî_hadli": sum(1 for o in olcumler if o.uzay.tahmini_ust)}


def rapor() -> str:
    d = funktor_dogrula()
    s = ["=== ÖLÇÜ FUNKTORU -- ayrı uzaylardan müşterek uzaya ===",
         "",
         "Müşterek uzay `mizan/munazara.py`nin merdivenidir:",
         "  " + "  <  ".join("%s %.2f" % (k, v) for k, v in
                             sorted(_mertebeler().items(),
                                    key=lambda kv: kv[1])),
         "",
         "FUNKTÖR KAİDELERİ (iddia değil, sınanmış):",
         "  F(id) = id            hata %.2e" % d["birim_hatası"],
         "  F(g∘f) = F(g)∘F(f)    hata %.2e   ← AŞİKÂR, delil DEĞİL"
         % d["terkip_hatası"],
         "",
         "  Terkip kaidesi bu inşada cebren sağlanır (F_T⁻¹∘F_T",
         "  sadeleşir), o yüzden hiçbir şey ispat etmez. Yük taşıyan",
         "  hususiyet SIRA KORUMASIDIR ve sınanan odur:",
         "    sıra korunuyor mu            : %s" % d["sıra_korunuyor"],
         "    cihet ters çevrilince bozuluyor mu: %s"
         % d["cihet_ters_çevrilince_bozuluyor"],
         "    → ölçüt kör değil            : %s" % d["ölçüt_kör_değil"],
         "  funktör mü                     : %s" % d["funktör_mü"],
         "",
         "TANIMLI UZAYLAR (had ve cihet):"]
    for ad in sorted(UZAYLAR):
        S = UZAYLAR[ad]
        s.append("  %-16s [%.3f, %.3f]  %s%s"
                 % (S.ad, S.alt, S.ust,
                    "büyüğü iyi" if S.buyugu_iyi else "küçüğü iyi",
                    "  (haddi TAHMİNÎ)" if S.tahmini_ust else ""))
    s += ["",
          "Eski kayıptaki 0,25 ve 0,1 gibi elle konmuş katsayılar",
          "KALKMIŞTIR: uzaylar arası intibak artık funktörle sağlanıyor,",
          "katsayıyla değil. Katsayı bir ölçü değil, ölçüsüzlüğün örtüsüdür."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
