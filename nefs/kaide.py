"""
KÂİDE = İSPAT YAPISI -- H85'in fiilî karşılığı, ``mizan`` ve ``fitrat``ın
kübit hattına bağlanması (kullanıcı hükmü: *"Kübit hattına BAĞLA --
melekeler onları kullansın"*).

Kullanıcı, kâidenin ne olması gerektiğini şöyle tarif etti:

> *"Kaide şu olmalı: çıktı hücresi ne kadar ebatta olacak, benim
> söylediğim ebat kesin mi, aksinin mümkün olmadığı ispatlandı mı? Tüm
> misaller için ebat tahminlerim doğru mu, renklerim doğru mu? Her rengi
> neden koyduğumu açıklayabiliyor muyum? Hangi rengin yerine başka bir
> şey koymanın imkansızlığını açıklayabiliyor muyum? İşin sebebini
> illetini delillerini ispatlarını biliyor muyum?"*

Bunların **hiçbiri** uydurulmadı: yedisinin de motoru kod tabanında
zaten yazılıydı, fakat padişahın eli oraya uzanmıyordu (nizam ölçümü:
`mizan` 3 749 satır, `fitrat` 3 070 satır, ikisi de **beylik**).

======  ==========================================  =========================
şart    kullanıcının suali                          motoru
======  ==========================================  =========================
1       "çıktı ne ebatta olacak"                    bu modül (namzet kütüğü)
2       "aksinin imkânsızlığı ispatlandı mı"        ``onerme.karsi_ornek``
3       "tüm misaller için doğru mu"                ``istikra.mill_uyusma``
4       "her rengi neden koyduğumu izah ediyor mu"  ``istikra.temsil_hukmu``
5       "yerine başkasını koymanın imkânsızlığı"    ``onerme.gecerli_mi``
6       "illetini delillerini biliyor muyum"        ``mill_birlesik`` + Nyāya
7       hükmün derecesi (makam)                     ``ardisiklik_kaidesi``
======  ==========================================  =========================

**Neden bu, "hüküm ceridesindeki nakz"ın ta kendisidir.** ``nakz``
kütükte *"tek karşı örneğin küllî hükmü düşürmesi"* diye tarif edilmişti;
``onerme.karsi_ornek`` da tam olarak budur -- öncüllerin doğru, neticenin
yanlış olduğu **bir** değerlemeyi bulur. Yani proje ıstılâhı ile mantık
motoru aynı şeyi söylüyormuş, sadece birbirlerini tanımıyorlarmış.

**Neden makam merdiveni buradan çıkar.** ``istikra.tam_istikra_mi``
şunu ispatlar: eksik istikrâ hiçbir sonlu ``n`` için 1 vermez. O hâlde
**Yakîn'e istikrâ ile çıkılamaz**; ancak aksinin imkânsızlığı
ispatlanınca (2. şart) çıkılır. Misal biriktirmek insanı olsa olsa
Zan'da tutar. Bu, kütükteki makam doktrininin ve H10'un (*sükût
fazilettir*) riyazî karşılığıdır ve buradan **türetilmiştir**,
konulmamıştır.

**BU MODÜL OKUMA YAPMAZ DEMİYORUM.** Aksine: burası klasik taraftır ve
klasik olduğu açıkça yazılıdır. Melekeler üniterdir ve akış içinde
hiçbir şey okumaz (H31); bu modül akışın **içinde** çağrılmaz. Nereden
çağrılacağı H85'in açık borcudur ve kullanıcıya sorulmuştur;
uydurulmayacaktır.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import (Callable, Dict, FrozenSet, List, Optional, Sequence,
                    Tuple)

import numpy as np

from fitrat.ayrisma import Cizge, arka_kapi_mi
from mizan.istikra import (Nesne, ardisiklik_kaidesi, mill_ayrilik,
                           mill_birlesik, mill_uyusma, tam_istikra_mi,
                           temsil_hukmu)
from mizan.onerme import deg, degil, gecerli_mi, ise, karsi_ornek, ve

__all__ = ["EbatKaidesi", "EBAT_KUTUGU", "RenkKaidesi", "RENK_KUTUGU",
           "IskeletKaidesi", "ISKELET_KUTUGU", "fiili_iskelet",
           "Kaide", "Ispat", "ispat_yapisi", "namzetleri_ele",
           "MAKAMLAR"]

Izgara = np.ndarray
Sahit = Tuple[Izgara, Izgara]

#: Kütükteki makamlar; `nefs/murakabe.py`nin ``makam_tayin``ıyla aynı
#: kümedir (kütük H158: ``zann-ı gālib`` beşinci mertebe olarak geldi).
MAKAMLAR = ("Vehim", "Şek", "Zan", "Zann-ı gālib", "Yakîn")


# =====================================================================
#  H_S -- İSKELET (varlık sahası / support). Kütük H91'in AÇIK BORCU
# =====================================================================
#
# H91 beş rükün saymıştı ve karşılıklarını yazmıştı::
#
#     H_D ebat            "ebat kesin mi"              _teklik_ispati   ✓
#     H_S iskelet/support "hangi hücre dönüşür"        (henüz yok)      ✗
#     H_C illet           "her rengi neden koydum"     _illet_kesfi     ✓
#     H_N nakz            "yerine başkası niçin konamaz" karsi_ornek    ✓
#     H_J muhakeme        "hükm-i yakîn"               _makam           ✓
#
# ``H_S`` **eksikti** ve H98'de de *"kurulan yalnız ebat rüknüdür"* diye
# tekrar zabıtlanmıştı. Borç burada kapanıyor (kütük H161).
#
# **Niçin ayrı bir rükün.** ``RENK_KUTUGU``nun bütün kaideleri çıktının
# **her** hücresini yeniden yazar. Halbuki ARC'de en sık görülen desen
# şudur: *"şu hücreleri değiştir, ötekilere dokunma."* O desen mevcut
# cebirle **ifade edilemiyordu** -- bir kâide ya her şeyi yeniden yazar
# ya hiçbir şeyi. İskelet, kâidenin **nereye dokunduğunu** söyler ve
# dokunmadığı yer girdiden aynen geçer.
#
# **Ölçüsü uydurma değildir:** aynı ebatlı bir şahitte fiilî iskelet
# ``çıktı ≠ girdi`` hücrelerinin kümesidir ve doğrudan okunur
# (``fiili_iskelet``). Yani iskelet iddiası **yanlışlanabilir**: kâide
# "yalnız kırmızıları değiştiririm" diyorsa ve şahitte mavi de
# değişmişse iddia düşer. H90'ın şartı budur.


@dataclass(frozen=True)
class IskeletKaidesi:
    """Kâidenin **dokunduğu** hücreleri söyleyen kaide (``H_S``).

    ``maske(g)`` girdiye bakıp ``bool`` bir ızgara döndürür: ``True``
    olan hücreler dönüşür, ``False`` olanlar **zemindir** ve girdiden
    aynen geçer.
    """
    ad: str
    maske: Callable[[Izgara], np.ndarray]

    def __call__(self, g: Izgara) -> np.ndarray:
        m = np.asarray(self.maske(g), bool)
        return m if m.shape == g.shape else np.ones(g.shape, bool)


def _arka_renk(g: Izgara) -> int:
    """En sık renk -- ARC'de zemin ekseriya odur, fakat daima değil."""
    d = np.bincount(np.asarray(g).ravel(), minlength=10)
    return int(np.argmax(d))


def _sinir_maskesi(g: Izgara) -> np.ndarray:
    m = np.zeros(g.shape, bool)
    m[0, :] = m[-1, :] = True
    m[:, 0] = m[:, -1] = True
    return m


#: İskelet namzetleri. Kütük **açık uçludur** (H60) ve genişlemesi
#: hükmü **zayıflatır** (rakip artar, teklik zorlaşır) -- ``EBAT_KUTUGU``
#: ile aynı dürüst istikamet.
ISKELET_KUTUGU: Tuple[IskeletKaidesi, ...] = (
    IskeletKaidesi("hepsi", lambda g: np.ones(g.shape, bool)),
    IskeletKaidesi("hiçbiri", lambda g: np.zeros(g.shape, bool)),
    IskeletKaidesi("arka_hariç", lambda g: np.asarray(g) != _arka_renk(g)),
    IskeletKaidesi("yalnız_arka", lambda g: np.asarray(g) == _arka_renk(g)),
    IskeletKaidesi("sıfır_hariç", lambda g: np.asarray(g) != 0),
    IskeletKaidesi("yalnız_sıfır", lambda g: np.asarray(g) == 0),
    IskeletKaidesi("sınır", _sinir_maskesi),
    IskeletKaidesi("iç", lambda g: ~_sinir_maskesi(g)),
)


def fiili_iskelet(g: Izgara, c: Izgara) -> Optional[np.ndarray]:
    """Şahidin **fiilî** iskeleti: hangi hücre gerçekten değişmiş.

    Ebatlar ayrıysa ``None``: farklı ebatta "aynı hücre" diye bir şey
    yoktur ve iskelet iddiası orada **tanımsızdır**. Tanımsızı sıfır
    yahut bir saymak, ölçütü sessizce yeşile boyamak olurdu (H90).
    """
    g = np.asarray(g)
    c = np.asarray(c)
    if g.shape != c.shape:
        return None
    return g != c


# =====================================================================
#  1. şart -- ÇIKTI NE EBATTA OLACAK
# =====================================================================
@dataclass(frozen=True)
class EbatKaidesi:
    """Girdi ebadından çıktı ebadını **söyleyen** kaide.

    Bir kaide tahmin etmez, *söyler*: aynı girdiye daima aynı ebadı
    verir. Söylediği yanlışsa ``nakz`` edilir; bu, kaidenin kusuru
    değil, kâide olmasının şartıdır.
    """
    ad: str
    hesap: Callable[[int, int], Tuple[int, int]]

    def __call__(self, h: int, w: int) -> Tuple[int, int]:
        return self.hesap(h, w)


def _sabit(h0: int, w0: int) -> Callable[[int, int], Tuple[int, int]]:
    return lambda h, w: (h0, w0)


#: Namzet ebat kaideleri. Kütük **açık uçludur** (H60): buraya kaide
#: eklenebilir; eklenince 2. şart (teklik) otomatik olarak zorlaşır,
#: çünkü rakip sayısı artar. Yani kütüğü genişletmek hükmü **zayıflatır**,
#: kuvvetlendirmez -- dürüst istikamet budur.
EBAT_KUTUGU: Tuple[EbatKaidesi, ...] = (
    EbatKaidesi("aynı", lambda h, w: (h, w)),
    EbatKaidesi("devrik", lambda h, w: (w, h)),
    EbatKaidesi("iki_kat", lambda h, w: (2 * h, 2 * w)),
    EbatKaidesi("üç_kat", lambda h, w: (3 * h, 3 * w)),
    EbatKaidesi("yarı", lambda h, w: (max(1, h // 2), max(1, w // 2))),
    EbatKaidesi("üçte_bir", lambda h, w: (max(1, h // 3), max(1, w // 3))),
    EbatKaidesi("kare_h", lambda h, w: (h, h)),
    EbatKaidesi("kare_w", lambda h, w: (w, w)),
    EbatKaidesi("tek_hücre", _sabit(1, 1)),
    EbatKaidesi("satır_şeridi", lambda h, w: (h, 1)),
    EbatKaidesi("sütun_şeridi", lambda h, w: (1, w)),
    EbatKaidesi("kat_kare", lambda h, w: (h * h, w * w)),
)


# =====================================================================
#  4. şart -- HER RENGİ NEDEN KOYDUM
# =====================================================================
@dataclass(frozen=True)
class RenkKaidesi:
    """Çıktı hücresinin rengini **illetiyle beraber** söyleyen kaide.

    ``hesap`` rengi verir; ``illet`` o rengin **niçin** o olduğunu
    söyleyen vasıf adıdır. İllet olmadan renk konmaz: 4. şart tam da
    "her rengi neden koyduğumu açıklayabiliyor muyum" suâlidir ve
    illetsiz bir renk kaidesi o suâle cevap veremez.
    """
    ad: str
    illet: str
    hesap: Callable[[Izgara, int, int], int]

    def __call__(self, g: Izgara, i: int, j: int) -> int:
        return self.hesap(g, i, j)


def _kaynak(g: Izgara, i: int, j: int) -> int:
    """Aynı yerdeki girdi hücresi (ebat aynıysa)."""
    return int(g[i % g.shape[0], j % g.shape[1]])


def _en_sik(g: Izgara, i: int, j: int) -> int:
    d = np.bincount(np.asarray(g).ravel(), minlength=10)
    return int(np.argmax(d))


def _en_seyrek(g: Izgara, i: int, j: int) -> int:
    d = np.bincount(np.asarray(g).ravel(), minlength=10).astype(float)
    d[d == 0] = np.inf
    return int(np.argmin(d))


RENK_KUTUGU: Tuple[RenkKaidesi, ...] = (
    RenkKaidesi("kaynak", "yer_aynı", _kaynak),
    RenkKaidesi("yatay_ayna", "yer_yansık",
                lambda g, i, j: int(g[i % g.shape[0],
                                      g.shape[1] - 1 - (j % g.shape[1])])),
    RenkKaidesi("dikey_ayna", "yer_yansık",
                lambda g, i, j: int(g[g.shape[0] - 1 - (i % g.shape[0]),
                                      j % g.shape[1]])),
    RenkKaidesi("devrik", "yer_devrik",
                lambda g, i, j: int(g[j % g.shape[0], i % g.shape[1]])),
    RenkKaidesi("en_sık_renk", "renk_sayısı", _en_sik),
    RenkKaidesi("en_seyrek_renk", "renk_sayısı", _en_seyrek),
    RenkKaidesi("sıfır", "sabit", lambda g, i, j: 0),
)


# =====================================================================
@dataclass(frozen=True)
class Kaide:
    """Bir namzet kâide: ebat (``H_D``), iskelet (``H_S``), renk (``H_C``).

    Üç rükün üç ayrı suale cevap verir ve üçü de ayrı ayrı
    **yanlışlanabilir**:

    * ``ebat``    -- çıktı ne kadar olacak,
    * ``iskelet`` -- hangi hücre dönüşecek, hangisi zemin kalacak,
    * ``renk``    -- dönüşen hücreye ne konacak, ve **niçin** (illet).

    İskelet ``None`` ise eski davranış aynen durur (her hücre yeniden
    yazılır); yani ``H_S``in eklenmesi evvelki kâideleri **bozmaz**.
    """
    ebat: EbatKaidesi
    renk: RenkKaidesi
    iskelet: Optional[IskeletKaidesi] = None

    @property
    def ad(self) -> str:
        if self.iskelet is None:
            return "%s/%s" % (self.ebat.ad, self.renk.ad)
        return "%s/%s/%s" % (self.ebat.ad, self.iskelet.ad, self.renk.ad)

    def uygula(self, g: Izgara) -> Izgara:
        h, w = self.ebat(int(g.shape[0]), int(g.shape[1]))
        h, w = max(1, min(int(h), 30)), max(1, min(int(w), 30))
        out = np.array([[self.renk(g, i, j) for j in range(w)]
                        for i in range(h)], dtype=np.int64)
        if self.iskelet is None:
            return out
        # **İSKELET (H_S): dokunulmayan yer girdiden AYNEN geçer.**
        # Yalnız ebat aynıyken manalıdır; ebat değişince "aynı hücre"
        # diye bir şey olmadığı için iskelet tatbik edilmez ve bu
        # sessizce yapılmaz -- ``ispat_yapisi`` orada ``H_S``i
        # **ölçmez**, tanımsız sayar.
        g = np.asarray(g)
        if out.shape != g.shape:
            return out
        m = self.iskelet(g)
        return np.where(m, out, g).astype(np.int64)


# =====================================================================
@dataclass
class Ispat:
    """Bir kâidenin yedi şart karşısındaki hâli -- ölçüm, iddia değil."""
    kaide_adi: str
    ebat_dogru: Tuple[bool, ...] = ()      # şahit başına
    renk_dogru: Tuple[bool, ...] = ()
    ebat_tek_mi: bool = False              # 2. şart
    ebat_rakipleri: Tuple[str, ...] = ()
    renk_tek_mi: bool = False              # 5. şart
    renk_rakipleri: Tuple[str, ...] = ()
    illet: FrozenSet[str] = frozenset()    # 6. şart
    illet_izah_edildi: bool = False        # 4. şart
    nakz_sahidi: Optional[int] = None      # hangi şahit düşürdü
    nakz_delili: Optional[Dict[str, bool]] = None
    derece: float = 0.0                    # 7. şart
    makam: str = "Şek"
    #: ``H_S`` -- iskelet iddiası şahit başına tuttu mu. Ebat değişen
    #: şahitte iskelet **tanımsızdır** ve o şahit buraya hiç girmez;
    #: yani boş bir dizi "hepsi doğru" demek değil "hiç ölçülemedi"
    #: demektir ve ``iskelet_olculdu`` onu ayırır.
    iskelet_dogru: Tuple[bool, ...] = ()
    iskelet_olculdu: bool = False

    @property
    def butun_misaller(self) -> bool:
        return bool(self.ebat_dogru) and all(self.ebat_dogru) \
            and all(self.renk_dogru)

    @property
    def iskelet_tuttu(self) -> bool:
        """``H_S`` **ölçüldü ve tuttu** mu. Ölçülmediyse ``False``.

        Ölçülmemişi "tuttu" saymak, olmayan bir ispat iddia etmek
        olurdu; ölçülmemişi "düştü" saymak da ebat değiştiren bütün
        görevleri haksız yere cezalandırırdı. Onun için iki alan ayrı
        durur ve hükmü çağıran verir.
        """
        return bool(self.iskelet_olculdu) and bool(self.iskelet_dogru) \
            and all(self.iskelet_dogru)

    def satir(self) -> str:
        isk = ("iskelet=%d/%d" % (sum(self.iskelet_dogru),
                                  len(self.iskelet_dogru))
               if self.iskelet_olculdu else "iskelet=—")
        return ("%-30s ebat=%d/%d %s renk=%d/%d  teklik(ebat=%s renk=%s)  "
                "illet=%s  derece=%.3f  makam=%s"
                % (self.kaide_adi, sum(self.ebat_dogru), len(self.ebat_dogru),
                   isk, sum(self.renk_dogru), len(self.renk_dogru),
                   self.ebat_tek_mi, self.renk_tek_mi,
                   ",".join(sorted(self.illet)) or "-",
                   self.derece, self.makam))


# =====================================================================
def _ebat_uyan_kaideler(sahitler: Sequence[Sahit]) -> List[str]:
    """BÜTÜN şahitlerde ebadı tutturan kaideler -- Mill'in uyuşma usulü.

    ``mill_uyusma`` "neticenin olduğu bütün vakalarda ortak olan âmiller"
    der; burada âmil = kaide adı, vaka = şahit. Yani her şahit bir vaka
    olur ve o vakada 'mevcut âmiller' o şahidi tutturan kaidelerdir.
    Kesişimleri, bütün misallerde geçerli kaidelerdir (3. şart).
    """
    vakalar = []
    for g, c in sahitler:
        tutan = {k.ad for k in EBAT_KUTUGU
                 if k(int(g.shape[0]), int(g.shape[1]))
                 == (int(c.shape[0]), int(c.shape[1]))}
        vakalar.append((frozenset(tutan), True))
    return sorted(mill_uyusma(vakalar))


def _renk_uyan_kaideler(sahitler: Sequence[Sahit],
                        ebat: EbatKaidesi) -> List[str]:
    """Aynı usul, renk için: bütün şahitlerde her hücreyi tutturanlar."""
    vakalar = []
    for g, c in sahitler:
        tutan = set()
        for r in RENK_KUTUGU:
            k = Kaide(ebat, r)
            try:
                u = k.uygula(g)
            except Exception:
                continue
            if u.shape == c.shape and bool(np.array_equal(u, c)):
                tutan.add(r.ad)
        vakalar.append((frozenset(tutan), True))
    return sorted(mill_uyusma(vakalar))


def _teklik_ispati(kaide_adi: str, uyanlar: Sequence[str], kendi_tutuyor: bool
                   ) -> Tuple[bool, Tuple[str, ...], Optional[Dict[str, bool]]]:
    """2./5. şart: *aksinin imkânsızlığı* ispatlandı mı?

    Bu, mantıkta şu önermenin geçerliliğidir::

        (bu_kaide_uyuyor ∧ ¬başka_kaide_uyuyor) → bu_kaide_zorunlu

    Rakip kalmamışsa öncül bütün değerlemelerde neticeyi verir ve
    ``gecerli_mi`` **doğru** der; rakip varsa ``karsi_ornek`` o rakibin
    şahsında **nakz delilini** getirir. Yani teklik iddiası bir kanaat
    değil, doğruluk tablosuyla kararlaştırılan bir hükümdür.

    Dikkat: burada ispatlanan şey "kaide doğrudur" değil, **"elimizdeki
    kütükte ondan başkası uymuyor"**dur. Kütük genişlerse hüküm zayıflar
    ve bu dürüstlüğün gereğidir -- imkânsızlık iddiası daima bir
    ihtimaller uzayına nispetle söylenir.
    """
    rakipler = tuple(a for a in uyanlar if a != kaide_adi)
    uyar = deg("bu_uyar")
    rakip = deg("rakip_uyar")
    zorunlu = deg("bu_zorunlu")
    # **ÖLÇÜLEN VE DÜZELTİLEN BOŞ HÜKÜM (kütük H90).** Evvelki hâli
    # yalnız rakip sayısına bakıyordu; hiçbir kaide tutmayınca rakip de
    # kalmadığı için ``teklik=True`` çıkıyordu. Yani ölçüt, kâide
    # **hiçbir şey açıklamadığı** hâlde "zorunlu" diyordu -- kırmızı
    # yanamayan bir ölçüt. Zorunluluk iddiasının ilk şartı, kâidenin
    # kendisinin tutmasıdır: tutmayan bir şeyin zorunluluğu konuşulmaz.
    if not kendi_tutuyor:
        oncul = [degil(uyar), ise(ve(uyar, degil(rakip)), zorunlu)]
        return False, rakipler, karsi_ornek(oncul, zorunlu)
    if rakipler:
        # Rakip fiilen var: öncüle ``rakip_uyar`` konur ve netice düşer.
        oncul = [uyar, rakip, ise(ve(uyar, degil(rakip)), zorunlu)]
    else:
        oncul = [uyar, degil(rakip), ise(ve(uyar, degil(rakip)), zorunlu)]
    tek = gecerli_mi(oncul, zorunlu)
    delil = None if tek else karsi_ornek(oncul, zorunlu)
    return bool(tek), rakipler, delil


def _illet_taninabilir(namzetler: Sequence[str], kaide_illeti: str
                       ) -> List[str]:
    """Mill'in verdiği illet namzetlerinden **tanınabilir** olanları ayır.

    Kütük H92: ``fitrat`` buraya **uzuv** olarak girer, yedek olarak
    değil. Onsuz bu ayrım yapılamaz ve model sahte illet kabul eder.

    **Mill niçin yetmez.** Mill'in birleşik usulü "her müsbette var,
    hiçbir menfîde yok" der ve orada durur. Halbuki ``şahit``in kendisi
    **ortak sebeptir**: ``ebat_sabit`` ile kâidenin tutması birlikte
    görünür, çünkü ikisini de görevin kendisi tayin eder. Ölçüldü: Mill
    tek bir kâide için dört illet döndürüyordu, üçü şahidin vasfıydı.

    **``ayrisma`` ne söyler.** Nedensellik çizgesi şudur::

        kaide_illeti ─────────────→ tuttu
                                      ↑
        şahit(gizli) ──→ vasıf_i ─────┘
              │
              └───────────────────────→ tuttu

    * ``kaide_illeti`` **kökte durur**: hangi illeti ileri sürdüğümüz
      bizim seçimimizdir, yani bir **müdahaledir** (``do``). Ebeveyni
      olmadığı için arka kapı boş kümeyle kapanır ⇒ **tanınabilir**.
    * ``vasıf_i`` ise bir **müşahededir**: ``şahit`` hem onu hem
      ``tuttu``yu doğurur, yani ikisi bir **çatal** paylaşır. Çatalı
      kapatmak ``şahit``e şarta bağlanmayı ister; ``şahit``
      **gözlenmez** (görev gizlidir) ve öteki vasıflar yolun üstünde
      değildir, dolayısıyla hiçbir gözlenebilir küme kapıyı kapatmaz
      ⇒ illet iddiası **ispatlanamaz**.

    **Bu çizge bir kere yanlış kuruldu ve ölçüm yakaladı:** illet
    ``izah``ın *çocuğu* yapılmıştı, yani illet sebep değil **etiket**
    olmuştu; o zaman ``illet ← izah → tuttu`` çatalı açık kalıyor ve
    doğru illet de eleniyordu (ölçüldü: ``yer_devrik`` eleniyor, Yakîn
    kayboluyordu). İlletin sebep olması, çizgede **kökte durmasıyla**
    ifade edilir.

    Dönen liste, arka kapısı gözlenebilir bir kümeyle kapanan
    namzetlerdir. Kapanmayan namzet *yanlış* diye atılmaz -- **hükmü
    verilemez** diye atılır; aradaki fark, kütükteki sükût makamının ta
    kendisidir (H10).
    """
    namzetler = list(dict.fromkeys(namzetler))
    if not namzetler:
        return []
    gozlenen = [n for n in namzetler if n != kaide_illeti]
    dugumler = ["şahit", "tuttu"] + namzetler
    kenarlar: List[Tuple[str, str]] = [("şahit", "tuttu")]
    for n in namzetler:
        kenarlar.append((n, "tuttu"))        # her namzet, tuttu'nun sebebi
        if n != kaide_illeti:
            kenarlar.append(("şahit", n))    # ama şahit vasfını şahit doğurur
    g = Cizge(tuple(dugumler), tuple(kenarlar))

    tanınan: List[str] = []
    for n in namzetler:
        aday = [z for z in gozlenen if z != n]     # ``şahit`` GÖZLENMEZ
        if any(arka_kapi_mi(g, n, "tuttu", Z)
               for k in range(len(aday) + 1)
               for Z in _altkumeler(aday, k)):
            tanınan.append(n)
    return tanınan


def _altkumeler(ogeler: Sequence[str], k: int) -> List[Tuple[str, ...]]:
    import itertools
    return list(itertools.combinations(ogeler, k))


def _illet_kesfi(sahitler: Sequence[Sahit], kaide: Kaide
                 ) -> Tuple[FrozenSet[str], bool]:
    """6. şart: illet ve delili -- Mill'in birleşik usulü.

    Her şahit bir vaka olur; âmiller o şahidin **vasıflarıdır**
    (kare mi, ebat değişiyor mu, renk sayısı arttı mı …). Netice ise
    "bu kâide o şahitte tuttu mu"dur. Birleşik usul, her müsbet vakada
    bulunup hiçbir menfî vakada bulunmayan âmilleri verir: illet
    namzetleri bunlardır.

    Menfî vaka yoksa ``mill_ayrilik`` bütün müsbet âmilleri geçirir ve
    illet ayırt edici olmaz; bu hâl **ayrıca** raporlanır (``izah``
    yanlış kalır), çünkü "hepsinde var" demek "illet budur" demek
    değildir -- eleyecek karşı vaka lâzımdır.
    """
    def _sahit_vasiflari(g: Izgara, c: Izgara) -> set:
        v = set()
        h, w = int(g.shape[0]), int(g.shape[1])
        if h == w:
            v.add("girdi_kare")
        if (h, w) == (int(c.shape[0]), int(c.shape[1])):
            v.add("ebat_sabit")
        if int(c.shape[0]) > h or int(c.shape[1]) > w:
            v.add("ebat_büyüdü")
        if int(c.shape[0]) < h or int(c.shape[1]) < w:
            v.add("ebat_küçüldü")
        if len(np.unique(c)) < len(np.unique(g)):
            v.add("renk_azaldı")
        if len(np.unique(c)) == len(np.unique(g)):
            v.add("renk_sabit")
        return v

    # **ÖLÇÜLEN VE DÜZELTİLEN KUSUR -- menfî vaka nerede aranır.**
    # Evvelki hâli menfî vakayı ŞAHİTLER arasında arıyordu: kâidenin
    # düştüğü bir şahit. Halbuki kâide doğruysa öyle bir şahit YOKTUR;
    # o zaman Mill'in ayrılık usulü hiçbir şeyi eleyemiyor, ``izah``
    # daima yanlış kalıyor ve **Yakîn hiç ateşlenmiyordu**. Bile bile
    # kurulmuş bir görevde bile (çıktı = girdinin devriği) makam Zan'da
    # tıkanıyordu; yani ölçüt yeşil yanamıyordu ki bu da H90'a göre
    # ölçüt sayılmaz.
    #
    # Doğrusu şudur: menfî vaka, kâidenin düştüğü şahit değil, **aynı
    # şahitte düşen RAKİP kâidedir**. Mill'in ayrılık usulü tam da budur
    # -- vaka aynı, âmil farklı, netice farklı ⇒ farkeden âmil illettir.
    # Böylece "her rengi neden koyduğumu açıklayabiliyor muyum" suâli
    # şu ölçülebilir hâle gelir: *benim illetim, tutan izahları tutmayan
    # izahlardan ayıran vasıf mıdır?*
    vakalar: List[Tuple[FrozenSet[str], bool]] = []
    for r in RENK_KUTUGU:
        k2 = Kaide(kaide.ebat, r)
        for g, c in sahitler:
            v = _sahit_vasiflari(g, c) | {r.illet}
            try:
                tuttu = bool(np.array_equal(k2.uygula(g), c))
            except Exception:
                tuttu = False
            vakalar.append((frozenset(v), tuttu))

    ham = mill_birlesik(vakalar)
    # --- fitrat UZUV olarak devreye girer (kütük H92) ---------------
    illet = frozenset(_illet_taninabilir(ham, kaide.renk.illet))
    # İzah ancak **bu kâidenin kendi illeti** ayırt edici çıkarsa kabul
    # edilir; başka bir vasfın ayırt etmesi bu kâideyi izah etmez.
    izah = kaide.renk.illet in illet
    if izah:
        # Temsil hükmü: illet fer'de TAM intibak etmeden hüküm taşınmaz.
        asil = Nesne("asıl", frozenset(illet))
        fer = Nesne("fer", frozenset(illet))
        h, g_ = temsil_hukmu(asil, fer, sorted(illet), True)
        izah = (h is True) and g_ >= 1.0
    return illet, izah


def _makam(ispat: Ispat) -> Tuple[float, str]:
    """7. şart: hükmün derecesi ve makamı.

    ``ardisiklik_kaidesi(k, n)`` -- ``n`` şahidin ``k``sında tutan bir
    kâidenin bir sonraki şahitte de tutma ihtimali. ``tam_istikra_mi``
    ispatlar ki bu sayı **hiçbir sonlu n için 1 olmaz**; öyleyse:

    * **Yakîn** ancak istikrâdan değil, **tekliğin ispatından** gelir
      (2. ve 5. şart). Misal biriktirmek insanı Yakîn'e çıkarmaz.
    * **Zan**: bütün misaller tutuyor fakat rakip elenmemiş.
    * **Şek**: misaller bölünmüş.
    * **Vehim**: kâide misallerde düşmüş olduğu hâlde ileri sürülmüş.
    """
    n = len(ispat.ebat_dogru)
    if not n:
        return 0.0, "Şek"
    k = sum(1 for a, b in zip(ispat.ebat_dogru, ispat.renk_dogru) if a and b)
    derece = ardisiklik_kaidesi(k, n)
    ebat_hepsi = all(ispat.ebat_dogru)
    renk_hepsi = all(ispat.renk_dogru)

    # **Ebat ile rengi ayrı saymak şarttır.** Kullanıcı bunları ayrı
    # suâl olarak sordu: *"tüm misaller için ebat tahminlerim doğru mu,
    # renklerim doğru mu?"* Evvelki hâli ikisini tek sayıda topluyordu;
    # o zaman ebadı BÜTÜN şahitlerde tutturan bir kâide ile hiçbir şey
    # tutturmayan kâide aynı makama (Vehim) düşüyordu ve aynı dereceyi
    # alıyordu. Halbuki ebadı bilmek, rengi bilmeye giden yolun yarısıdır
    # ve o bilgi kaybedilmemelidir.
    # **H_S DÜŞMÜŞSE HÜKÜM YÜKSELEMEZ (kütük H161).** İskelet iddiası
    # ölçülüp yanlış çıkmışsa kâide, dokunacağını söylediği yeri
    # bilmiyor demektir; renkleri tesadüfen tutturmuş olsa bile o bir
    # ispat değildir. Ölçülmemiş iskelet ise ne lehte ne aleyhtedir.
    iskelet_dustu = bool(ispat.iskelet_olculdu) and not all(
        ispat.iskelet_dogru)
    if iskelet_dustu:
        return derece, "Şek"

    if not ebat_hepsi and k == 0:
        return derece, "Vehim"          # ne ebat ne renk: asılsız iddia
    if ebat_hepsi and renk_hepsi:
        if ispat.ebat_tek_mi and ispat.renk_tek_mi and ispat.illet_izah_edildi:
            # Teklik ispatlandı: istikrânın VEREMEYECEĞİ yakîni
            # (``tam_istikra_mi``) ancak ispat verir.
            return 1.0, "Yakîn"
        # **ZANN-I GĀLİB (kütük H158/H161).** Beşinci mertebe geldiğinde
        # burada da yeri açıldı ve keyfî değildir: bütün misaller tutuyor
        # **ve** rükünlerin çoğu ispatlanmış fakat biri eksikse, bu
        # "zan" değil "kuvvetli zan"dır. `mizan/munazara.py`nin eşiği
        # 0,75'tir ve derece o eşiği aşıyorsa mertebe de odur.
        rukun = sum((bool(ispat.ebat_tek_mi), bool(ispat.renk_tek_mi),
                     bool(ispat.illet_izah_edildi),
                     bool(ispat.iskelet_tuttu)))
        if rukun >= 2 and derece >= 0.75:
            return derece, "Zann-ı gālib"
        return derece, "Zan"
    return derece, "Şek"                # kısmî bilgi -- sükût makamı


# =====================================================================
def ispat_yapisi(kaide: Kaide, sahitler: Sequence[Sahit]) -> Ispat:
    """Bir kâideyi yedi şart karşısında **ölç** -- H85'in icrası."""
    ebat_ok: List[bool] = []
    renk_ok: List[bool] = []
    nakz_sahidi: Optional[int] = None
    for i, (g, c) in enumerate(sahitler):
        e = kaide.ebat(int(g.shape[0]), int(g.shape[1])) \
            == (int(c.shape[0]), int(c.shape[1]))
        try:
            r = bool(np.array_equal(kaide.uygula(g), c))
        except Exception:
            r = False
        ebat_ok.append(bool(e))
        renk_ok.append(r)
        if nakz_sahidi is None and not (e and r):
            nakz_sahidi = i          # tek karşı örnek küllîyi düşürür

    # --- H_S: iskelet iddiası şahitlerin FİİLÎ iskeletiyle yüzleşir --
    isk_ok: List[bool] = []
    if kaide.iskelet is not None:
        for g, c in sahitler:
            fiili = fiili_iskelet(g, c)
            if fiili is None:
                continue                 # ebat değişti: H_S tanımsız
            try:
                iddia = np.asarray(kaide.iskelet(np.asarray(g)), bool)
            except Exception:            # noqa: BLE001
                isk_ok.append(False)
                continue
            # İddia, fiilen değişen her hücreyi **kapsamalı** ve
            # dokunmadığını iddia ettiği yerde hiçbir şey değişmemiş
            # olmalıdır. İkisi birden: ``iddia == fiili``.
            isk_ok.append(bool(iddia.shape == fiili.shape
                               and np.array_equal(iddia, fiili)))

    ebat_uyan = _ebat_uyan_kaideler(sahitler)
    renk_uyan = _renk_uyan_kaideler(sahitler, kaide.ebat)
    e_tek, e_rakip, e_delil = _teklik_ispati(
        kaide.ebat.ad, ebat_uyan, all(ebat_ok))
    r_tek, r_rakip, r_delil = _teklik_ispati(
        kaide.renk.ad, renk_uyan, all(renk_ok))
    illet, izah = _illet_kesfi(sahitler, kaide)

    ispat = Ispat(
        kaide_adi=kaide.ad,
        ebat_dogru=tuple(ebat_ok), renk_dogru=tuple(renk_ok),
        ebat_tek_mi=e_tek, ebat_rakipleri=e_rakip,
        renk_tek_mi=r_tek, renk_rakipleri=r_rakip,
        illet=illet, illet_izah_edildi=izah,
        nakz_sahidi=nakz_sahidi,
        nakz_delili=e_delil or r_delil,
        iskelet_dogru=tuple(isk_ok),
        iskelet_olculdu=bool(kaide.iskelet is not None and isk_ok),
    )
    ispat.derece, ispat.makam = _makam(ispat)
    return ispat


def namzetleri_ele(sahitler: Sequence[Sahit],
                   azami: int = 0) -> List[Ispat]:
    """Bütün namzet kâideleri ölç ve **makama göre** sırala.

    Dönen liste bir cevap değil bir **mîzândır**: hiçbiri Yakîn'e
    çıkmıyorsa o da bir hükümdür ve sükût edilir (H10). Burada
    ``azami`` yalnız raporu kısaltır, eleme yapmaz.
    """
    sira = {ad: i for i, ad in enumerate(
        ("Yakîn", "Zann-ı gālib", "Zan", "Şek", "Vehim"))}
    hepsi = [ispat_yapisi(Kaide(e, r), sahitler)
             for e in EBAT_KUTUGU for r in RENK_KUTUGU]
    # --- H_S: iskeletli namzetler (kütük H161) ----------------------
    # Yalnız ebat AYNI iken kurulur ve sebebi tanımdır: farklı ebatta
    # "aynı hücre" diye bir şey yoktur, iskelet orada tanımsızdır.
    # Şahitlerin hepsi aynı ebatlı değilse hiç kurulmaz -- kurulsaydı
    # ölçülemeyen bir rükün için maliyet ödenmiş olurdu.
    ayni_ebat = all(np.asarray(g).shape == np.asarray(c).shape
                    for g, c in sahitler)
    if ayni_ebat and sahitler:
        ayni = next((e for e in EBAT_KUTUGU if e.ad == "aynı"), None)
        if ayni is not None:
            hepsi += [ispat_yapisi(Kaide(ayni, r, i), sahitler)
                      for i in ISKELET_KUTUGU
                      if i.ad not in ("hepsi",)   # "hepsi" iskeletsizle aynı
                      for r in RENK_KUTUGU]
    # Makam, sonra EBAT isabeti, sonra derece. Ebadı bütün şahitlerde
    # tutturan kâide, hiçbir şey tutturmayanın üstünde durmalıdır.
    hepsi.sort(key=lambda x: (sira.get(x.makam, 9),
                              -sum(x.ebat_dogru), -x.derece))
    return hepsi[:azami] if azami else hepsi


# =====================================================================
def rapor(gorev=None) -> str:
    """Bir ARC görevinde kâide mîzânı -- ölçüm, iddia değil."""
    if gorev is None:
        from idrak import arc
        gorevler = arc.yukle_hepsi("training")
        gorev = gorevler[0]
    sahitler = list(gorev.egitim)
    s = ["=== KÂİDE MÎZÂNI -- görev %s, %d şahit ==="
         % (gorev.ad, len(sahitler)), ""]
    hepsi = namzetleri_ele(sahitler)
    yakin = [i for i in hepsi if i.makam == "Yakîn"]
    zan = [i for i in hepsi if i.makam == "Zan"]
    s.append("namzet kâide: %d   Yakîn: %d   Zan: %d"
             % (len(hepsi), len(yakin), len(zan)))
    s.append("")
    for i in hepsi[:12]:
        s.append("  " + i.satir())
    if not yakin:
        s += ["", "Yakîn'e çıkan kâide YOK → sükût edilir (kütük H10).",
              "Bu bir kusur değil ölçümdür: elimizdeki kütükte bu görevi",
              "ispatlayan kâide bulunmuyor."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
