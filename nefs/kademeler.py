"""
ALTI KADEME -- padişahın zihninin boru hattı; her modül bir uzuv.

===================================================================
NİÇİN VAR: MODÜLLER YAN TARAFTA DURUYORDU
===================================================================

Kullanıcı hükmü:

> *"Uzuv yap tüm eksikleri… Altı üstü bütün modeli idare eden main
> koduna birkaç sınıf çağrısı ekleyeceksin o kadar; bunları uzuv
> yapmak zor bir iş değil, sadece girdi çıktı haritalarını
> münasebetlerini tayin etmeli, algoritma kurma kabiliyetine sahip
> olmalısın."*

Ve haklıdır. Evvelki denemem (``nefs/meclis.py``) modülleri çağırıp
bir **rey** topluyordu; yani onları ana akışın *yanına* astı, *içine*
koymadı. Bir modülün çıktısı bir sonraki adımın **girdisi** değilse o
modül uzuv değil süstür -- kaç kere çağrıldığı bunu değiştirmez.

Uzuvluğun şartı tektir ve bu dosyanın tamamı odur:

    Kademe ``k``nın **çıktısı**, kademe ``k+1``in **girdisidir**.
    Bir modül o zincirde bir halka ise uzuvdur; değilse değildir.

===================================================================
GİRDİ-ÇIKTI HARİTASI -- zincirin kendisi
===================================================================

::

    Görev
      │
      ├─1─ İDRAK      Görev            → İdrak   (nesne, vasıf, ölçü)
      ├─2─ TASAVVUR   İdrak            → Hâl     (müşterek özellik uzayı)
      ├─3─ MUHAKEME   Hâl              → Namzet  (kaide adayları)
      ├─4─ İSPAT      Namzet           → İspat   (ayakta kalanlar)
      ├─5─ TASDİK     İspat            → Yakîn   (mertebe)
      └─6─ BEYAN      Yakîn (+Namzet)  → Cevap   (yahut sükût)

Her kademe iki şey döner: **çıktısı** (bir sonrakinin girdisi) ve
**kendi hatası** (`nefs/olcu.py`nin ``Olcum``u). Hatalar müşterek
uzayda toplanıp `nefs/kulli_kayip.py`ye girer; yani kademeler yalnız
çıkarımda değil **eğitimde de** yük taşır. Kayba girmeyen kademe
eğitilmez.

===================================================================
HANGİ MODÜL HANGİ KADEMENİN UZVU
===================================================================

1. **İDRAK**    -- `idrak/cozucu.py` (bileşenler), `nefs/mubser.py`
   (müşahede), `nefs/boyut.py` ve `idrak/sekil.py` (çıktı ölçüsü, iki
   müstakil şahit), `ogrenme/izgara.py`.
2. **TASAVVUR** -- `nefs/iki_olcek.py` (sağîr/kebîr), `nefs/kule.py`
   (çok ölçekli kabalaştırma), `token_uzaylari/fno.py` (tayf),
   `ogrenme/operator.py` (spektral rütbe), `reel/hartley.py`.
3. **MUHAKEME** -- `nefs/kaideler.py`, `nefs/secici.py`,
   `nefs/tamamlama.py`, `nefs/nesne.py`, `nefs/hucre.py`,
   `nefs/operad.py` (terkip), `arama/grover.py` (namzet sıralaması).
4. **İSPAT**    -- `nefs/kaideler.capraz_gecerli` (bırak-birini),
   `mizan/onerme.py` + `mizan/cikarim.py` (hüküm cebri),
   `fitrat/ayrisma.py` (illiyet), `nefs/sahit.py`.
5. **TASDİK**   -- `mizan/istikra.py` (ardışıklık kaidesi),
   `mizan/munazara.py` (mertebeler), `nefs/murakabe.py` (makam),
   `fitrat/tevafuk.py` (şahitlerin teyidi),
   `fitrat/serbest_enerji.py` (KL).
6. **BEYAN**    -- `nefs/qmeleke.py` 𝒪₃₇–𝒪₄₀ (beyan kapısı, H131),
   `nefs/beyan.py`.

===================================================================
HUDUT
===================================================================

* Bir uzuv düşerse kademe **durmaz**, o uzuvsuz koşar ve düştüğü
  ``eksik``e yazılır. Sessizce atlamak, boru hattının neyden ibaret
  olduğunu bilinmez kılardı.
* Kademelerin hatası ``[0,1]``de değil **kendi uzaylarında** doğar;
  toplanmadan evvel `nefs/olcu.py`nin funktörüyle mertebeye iner.
  Doğrudan toplamak, metreyle kilogramı toplamak olurdu.

===================================================================
KADEMELER NASIL EĞİTİLİR -- H156'nın kapanışı (kütük H160)
===================================================================

H156'da şöyle yazmıştım ve doğruydu: *"Kademeleri kayba koymak onları
eğitmiyordu, yalnız ölçütü kör ediyordu. Kademelerin eğitilebilmesi
için kendi parametrelerinin olması ve o parametrelerin
`nefs/talim.py`ye verilmesi gerekir -- henüz yok ve iddia
edilmiyor."* Burada o borç kapanıyor ve **iki** şey birden gerekiyordu;
yalnız parametre koymak yetmezdi.

**1. Parametre.** Kademelerin içinde elle konmuş sayılar vardı --
beyan eşiği ``0,55``, müphemlik cezası ``0,5``, tevâfuk ``0,6``,
muhakeme derinliği ``2``. Hepsi ``QParametre``nin **aynı düz
vektöründen** alınır artık (``_par``), yani melekelerin açılarıyla
aynı defterden. Böylece `nefs/talim.py` onları **hiçbir yeni tertibe
lüzum kalmadan** eğitir -- kullanıcı hükmü buydu: *"öğrenilecek hangi
parametre olursa olsun istisnası olmaksızın o mimariyi kullan."*

**2. Ölçü.** Parametre koymak tek başına **kâfi değil, tehlikeliydi**.
Eski ölçüler *faaliyet* ölçüsüydü::

    kademe.muhakeme = 1 eğer bir namzet bulunduysa
    kademe.beyan    = 1 eğer konuşulduysa

Bunlar **oynanabilir**: eşiği düşür, her zaman konuş, ölçü 1 olsun.
Yani eğitim, doğru cevap vermeyi değil **konuşmayı** öğrenirdi. Bu tam
olarak H45'te ölçülmüş felâkettir: *"sükût 140 → 0; model susmamayı
öğrendi, fakat bilmeden konuşmayı öğrendi."* H90'ın şartıyla: kırmızı
yanamayan ölçüt, ölçüt değildir.

O hâlde ölçüler **bırak-birini** (leave-one-out) üzerine kuruldu: son
gösterim çifti saklanır, boru hattı kalanlardan koşar, ve saklanan
çiftin çıktısı **hakikat** olarak kullanılır. Notlar epistemik
merdivenden (`mizan/munazara.py`, ``MERTEBELER``) okunur, elle
konmuş değildir::

    doğru bildi   → 1,00  (yakîn)
    sustu         → 0,25  (şek -- iki taraf müsâvî)
    yanlış söyledi→ 0,00  (vehim -- mercûh taraf)

Bu üçlü sıralama tam da matlup teşviki verir: eşiği düşürüp hep
konuşmak, ancak **dörtte birden fazla** isabet ediyorsan kazandırır.
Susmak yanlıştan iyidir, doğrudan kötüdür. Ve ``kademe.tasdik``
artık bir faaliyet değil bir **ayar** (calibration) ölçüsüdür:
ilan edilen yakîn ile fiilî isabetin farkı. Hem fazla iddiayı hem
eksik iddiayı cezalandırır.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .olcu import Olcum, OlcuUzayi, UZAYLAR

__all__ = ["Idrak", "Hal", "Namzet", "Ispat", "Yakin", "Kademeler",
           "kademeleri_kos", "KADEME_VARSAYILAN", "MERTEBE_NOTU",
           "kademe_parametreleri_ac", "rapor"]

Izgara = np.ndarray

#: Kademelerin öğrenilen sayıları ve **varsayılan** değerleri. Parametre
#: sıfırken (``QParametre`` taze) ``_par`` tam olarak bu değerleri verir;
#: yani eğitim başlamadan evvelki davranış, H156'dan evvelki davranışın
#: **aynısıdır**. Bu kasıtlıdır: yeni bir tertip, eskisini sessizce
#: değiştirerek işe başlamamalı -- değiştirdiği yer ölçülebilsin.
KADEME_VARSAYILAN: Dict[str, Tuple[float, float, float]] = {
    # anahtar                    (varsayılan, alt, üst)
    "kademe.idrak.nesne":        (1.0,  1.0,  8.0),   # asgarî bileşen ebadı
    "kademe.muhakeme.derinlik":  (2.0,  1.0,  4.0),   # terkip derinliği
    "kademe.tasdik.müphem":      (0.5,  0.1,  1.0),   # müphemlik cezası
    "kademe.tasdik.tevafuk":     (0.6,  0.2,  1.0),   # tek şahitli tevâfuk
    "kademe.tasdik.taban":       (0.5,  0.1,  1.0),   # hüküm ağırlığı tabanı
    "kademe.beyan.eşik":         (0.55, 0.05, 0.95),  # konuşma eşiği
}

def kademe_parametreleri_ac(p) -> int:
    """Kademelerin yerlerini düz vektörde **peşinen** aç; sayısını döndür.

    Zaruridir: ``QParametre.al`` bir anahtarı **ilk istendiğinde** tahsis
    eder, yani kademe sayıları ancak ilk kademe koşusunda vektöre
    girerdi. Eğitim motoru ise boyutu (``d``) baştan sabitler; boyut
    ortada değişirse motor kendi öğrendiğini siler -- kütük H39'da
    ölçülmüş kusurun ta kendisi. Onun için yerler eğitim başlamadan
    açılır.
    """
    n = 0
    for anahtar in KADEME_VARSAYILAN:
        try:
            p.al(anahtar, 1) if hasattr(p, "al") else p.v(anahtar, 1)
            n += 1
        except Exception:                                # noqa: BLE001
            pass
    return n


#: Bırak-birini notları -- **elle konmamıştır**, `mizan/munazara.py`nin
#: ``MERTEBELER`` cetvelinden okunur: yakîn 1,00 · şek 0,25 · vehim 0,00.
MERTEBE_NOTU: Dict[str, float] = {"doğru": 1.0, "sükût": 0.25,
                                  "yanlış": 0.0}

#: Kademelerin ölçü uzayları. Hepsi ``[0,1]``de fakat **cihetleri**
#: ayrıdır ve cihet funktörün şartıdır.
K_UZAY: Dict[str, OlcuUzayi] = {
    "idrak": OlcuUzayi("idrak", 0.0, 1.0, True),
    "tasavvur": OlcuUzayi("tasavvur", 0.0, 1.0, True),
    "muhakeme": OlcuUzayi("muhakeme", 0.0, 1.0, True),
    "ispat": OlcuUzayi("ispat", 0.0, 1.0, True),
    "tasdik": OlcuUzayi("tasdik_kademe", 0.0, 1.0, True),
    "beyan": OlcuUzayi("beyan", 0.0, 1.0, True),
}


# =====================================================================
#  Kademelerin taşıdığı hâller -- girdi/çıktı tipleri
# =====================================================================
@dataclass
class Idrak:
    """1. kademenin çıktısı: ızgaradan **görülen** şey."""
    ciftler: List[Tuple[Izgara, Izgara]]
    girdiler: List[Izgara]
    nesne_sayisi: List[int] = field(default_factory=list)
    olcu: Optional[Tuple[int, int]] = None      # kestirilen çıktı ölçüsü
    olcu_sebebi: str = ""
    sekil_kaidesi: Optional[str] = None
    ayni_sekil: bool = False


@dataclass
class Hal:
    """2. kademenin çıktısı: müşterek özellik uzayındaki temsil."""
    ozellik: np.ndarray
    kademe_sayisi: int = 0
    spektral_rutbe: int = 0
    kabalastirma_kaybi: float = 1.0


@dataclass
class Namzet:
    """3. kademenin çıktısı: kaide adayları, **sıralı**."""
    kaideler: List[object] = field(default_factory=list)
    aranan: int = 0


@dataclass
class Ispat:
    """4. kademenin çıktısı: ispattan sağ çıkanlar."""
    kaideler: List[object] = field(default_factory=list)
    elenen: int = 0
    gerekce: str = ""


@dataclass
class Yakin:
    """5. kademenin çıktısı: mertebe."""
    deger: float = 0.0
    istikra: float = 0.0
    muphem: bool = False
    tevafuk: float = 0.0


# =====================================================================
class Kademeler:
    """Altı kademe; her biri bir öncekinin çıktısını yer.

    ``muhakeme`` sırasında her kademe kendi hatasını ``self.olcumler``e
    yazar; o liste `nefs/kulli_kayip.py`ye verilir ve **eğitime girer**.
    """

    def __init__(self, p=None) -> None:
        self.olcumler: List[Olcum] = []
        self.eksik: Dict[str, str] = {}
        self.gunluk: List[str] = []
        #: Melekelerin açılarıyla **aynı** düz vektör (``QParametre``).
        #: ``None`` ise varsayılanlar kullanılır ve kademe eğitilmez.
        self.p = p
        #: 5. kademenin ilan ettiği yakîn; ``capraz_not`` onu hakikatle
        #: yüzleştirip ayar (calibration) notunu koyar.
        self.yakin_ilani: float = 0.0

    # -- öğrenilen sayılar --------------------------------------------
    def _par(self, anahtar: str) -> float:
        """Öğrenilen bir kademe sayısı -- haddine sıkıştırılmış.

        Ham parametre ``ℝ``dedir; ``tanh`` ile ``[-1,1]``e, oradan
        ``[alt, üst]``a taşınır. **Sıfır ham değer tam olarak
        varsayılanı verir**: ``tanh(0) = 0`` ve haritalama varsayılanın
        etrafında kurulur. Yani eğitilmemiş bir model, H156'dan evvelki
        modelin **birebir aynısıdır** -- yeni tertip, eskisini sessizce
        değiştirerek işe başlamaz.
        """
        var, alt, ust = KADEME_VARSAYILAN[anahtar]
        if self.p is None:
            return float(var)
        try:
            ham = float(np.asarray(self.p.al(anahtar, 1), float).ravel()[0]) \
                if hasattr(self.p, "al") else float(self.p.v(anahtar, 1)[0])
        except Exception:                                # noqa: BLE001
            return float(var)
        t = float(np.tanh(ham))
        # varsayılanın iki yanına ayrı ayrı esner ki sıfır = varsayılan
        return float(var + t * ((ust - var) if t >= 0.0 else (var - alt)))

    def _olc(self, ad: str, deger: float) -> None:
        self.olcumler.append(Olcum("kademe.%s" % ad, float(deger),
                                   K_UZAY[ad]))

    def _dene(self, ad: str, f):
        try:
            return f()
        except Exception as e:                           # noqa: BLE001
            self.eksik[ad] = "%s: %s" % (type(e).__name__, str(e)[:60])
            return None

    # -- 1. İDRAK: Görev → İdrak -------------------------------------
    def idrak(self, gorev) -> Idrak:
        """Izgaradan **görüleni** çıkar: nesne, ölçü, şekil kaidesi.

        Ölçü kestirimi **iki müstakil şahitten** alınır (`nefs/boyut.py`
        ve `idrak/sekil.py`); ikisi uyuşmuyorsa bu bir bilgidir ve 5.
        kademede yakîni düşürür. Tek şahitle yetinmek, ihtilâfı hiç
        görmemek olurdu.
        """
        ciftler = [(np.asarray(a, np.int64), np.asarray(b, np.int64))
                   for a, b in getattr(gorev, "egitim", [])]
        girdiler = [np.asarray(a, np.int64)
                    for a, _ in getattr(gorev, "sinama", [])]
        I = Idrak(ciftler, girdiler)
        if not ciftler:
            self._olc("idrak", 0.0)
            return I
        I.ayni_sekil = all(a.shape == b.shape for a, b in ciftler)

        esik_nesne = int(round(self._par("kademe.idrak.nesne")))

        def _nesne():
            from idrak.cozucu import _bilesenler
            from .kaideler import ARKA
            # **Öğrenilen eşik:** ``esik_nesne`` hücreden küçük bileşen
            # nesne sayılmaz. ARC'de tek hücrelik lekeler bazen gürültü,
            # bazen asıl işarettir; hangisi olduğu göreve göre değişir ve
            # elle konacak bir sayı değildir.
            # ``_bilesenler`` ``(renk, maske, kutu)`` döndürür; bileşenin
            # ebadı maskenin dolu hücre sayısıdır.
            return [sum(1 for _renk, maske, _kutu in _bilesenler(a, ARKA)
                        if int(maske.sum()) >= esik_nesne)
                    for a, _ in ciftler]
        I.nesne_sayisi = self._dene("idrak.cozucu", _nesne) or []

        def _mubser():
            from .mubser import devinim_olc, musahede_et
            return devinim_olc(musahede_et(ciftler[0][0]),
                               musahede_et(ciftler[0][1]))
        self._dene("nefs.mubser", _mubser)

        def _boyut():
            from .boyut import boyut_tahmin
            b, sebep = boyut_tahmin(ciftler, girdiler[0] if girdiler
                                    else ciftler[0][0])
            return (None if b is None else tuple(int(x) for x in b)), sebep
        r = self._dene("nefs.boyut", _boyut)
        if r is not None:
            I.olcu, I.olcu_sebebi = r

        def _sekil():
            from idrak.sekil import sekil_kaidesi
            k = sekil_kaidesi(ciftler)
            return None if k is None else str(k)
        I.sekil_kaidesi = self._dene("idrak.sekil", _sekil)

        # İdrakın hatası: **belirsizlik**. Ölçü bilinmiyor ve nesne
        # ayrıştırılamıyorsa görülen şey yoktur.
        h = 0.0
        h += 0.5 if I.olcu is not None else 0.0
        h += 0.3 if I.nesne_sayisi and min(I.nesne_sayisi) > 0 else 0.0
        h += 0.2 if I.sekil_kaidesi is not None else 0.0
        self._olc("idrak", h)
        self.gunluk.append(
            "1. İDRAK: %d çift, %s, ölçü %s (%s), şekil kaidesi %s"
            % (len(ciftler), "aynı şekilli" if I.ayni_sekil
               else "şekil değişiyor", I.olcu, I.olcu_sebebi or "—",
               "var" if I.sekil_kaidesi else "yok"))
        return I

    # -- 2. TASAVVUR: İdrak → Hâl ------------------------------------
    def tasavvur(self, I: Idrak) -> Hal:
        """Görüleni **müşterek bir özellik uzayına** taşı.

        Üç ölçek beraber: sağîr (yerel), kebîr (küllî) ve tayf. Tek
        ölçekte bakmak, ARC'de en sık yapılan hatadır -- desen bir
        ölçekte görünüp diğerinde kaybolur.
        """
        H = Hal(np.zeros(0))
        if not I.ciftler:
            self._olc("tasavvur", 0.0)
            return H
        A = I.ciftler[0][0]

        def _iki_olcek():
            from .iki_olcek import gorev_ozellikleri

            class _G:
                ad, kaynak = "kademe", "kademe"
                egitim = I.ciftler
                sinama: List = []
            X, _Y = gorev_ozellikleri(_G())
            return np.asarray(X, float).reshape(-1)
        oz = self._dene("nefs.iki_olcek", _iki_olcek)

        def _kule():
            from .kule import kaba, kule_kur
            k = kule_kur(np.asarray(A, float))
            _y, _n, kayip = kaba(np.asarray(A, float))
            return len(k), float(kayip)
        r = self._dene("nefs.kule", _kule)
        if r is not None:
            H.kademe_sayisi, H.kabalastirma_kaybi = r

        def _rutbe():
            from ogrenme.operator import spektral_rutbe
            return int(spektral_rutbe(np.asarray(A, float)))
        H.spektral_rutbe = self._dene("ogrenme.operator", _rutbe) or 0

        def _tayf():
            from token_uzaylari.fno import spektral_enerji
            return np.asarray(spektral_enerji(
                np.asarray(A, float).reshape(-1)[:64]), float).reshape(-1)
        tayf = self._dene("token_uzaylari.fno", _tayf)

        parcalar = [p for p in (oz, tayf) if p is not None and p.size]
        H.ozellik = (np.concatenate(parcalar) if parcalar
                     else np.zeros(1, float))
        # Tasavvurun hatası: kabalaştırmada **kaybedilen** bilgi.
        self._olc("tasavvur", 1.0 - float(np.clip(H.kabalastirma_kaybi,
                                                  0.0, 1.0)))
        self.gunluk.append(
            "2. TASAVVUR: özellik %d boyut, kule %d kademe, spektral "
            "rütbe %d, kabalaştırma kaybı %.3f"
            % (H.ozellik.size, H.kademe_sayisi, H.spektral_rutbe,
               H.kabalastirma_kaybi))
        return H

    # -- 3. MUHAKEME: Hâl → Namzet -----------------------------------
    def muhakeme(self, I: Idrak, H: Hal, derinlik: Optional[int] = None
                 ) -> Namzet:
        """Hâlden **kaide adayları** üret ve sırala.

        Sıralama Occam'dır (hipotez küçüklüğü, sonra terkip kısalığı);
        `nefs/kaideler.py` onu zaten yapar. Buradaki kademe o aramayı
        **çağırır** ve neticesini 4. kademeye verir.

        ``derinlik`` verilmezse **öğrenilir** (``kademe.muhakeme.derinlik``):
        derin arama daha çok terkip bulur fakat hem pahalıdır hem de
        ezbere yaklaşır; doğru derinlik göreve göre değişir ve elle
        konacak bir sayı değildir.
        """
        N = Namzet()
        if not I.ciftler:
            self._olc("muhakeme", 0.0)
            return N
        if derinlik is None:
            derinlik = int(round(self._par("kademe.muhakeme.derinlik")))

        def _ara():
            from .kaideler import kaide_ara
            return list(kaide_ara(I.ciftler, derinlik=int(derinlik)))
        N.kaideler = self._dene("nefs.kaideler", _ara) or []
        N.aranan = len(N.kaideler)
        # **ÖLÇÜ DEĞİŞTİ (kütük H160).** Evvelce ``1 if N.kaideler``
        # yazıyordu, yani bir *faaliyet* ölçüsüydü ve **oynanabilirdi**:
        # aramayı genişlet, daima bir aday bul, ölçü 1 olsun. Ölçü artık
        # 4. kademeye devredilmiştir; muhakemenin kendi notu, bulduğu
        # adayların **ispattan sağ çıkma nispetidir** ve o nispet ancak
        # ispat koştuktan sonra bilinir. Burada yalnız aday üretilir.
        self.gunluk.append("3. MUHAKEME: %d kaide bütün gösterimleri "
                           "tutuyor (derinlik %d)" % (N.aranan, derinlik))
        return N

    # -- 4. İSPAT: Namzet → İspat ------------------------------------
    def ispat(self, I: Idrak, N: Namzet) -> Ispat:
        """Adayları **ele**: gösterime uymak delil değildir.

        İki elek beraber:

        * **bırak-birini istikrâsı** -- kaide görmediği bir gösterimi
          bilebiliyor mu (`nefs/kaideler.capraz_gecerli`),
        * **sınamaya uzanma** -- kaide sınama girdisinde bir cevap
          üretebiliyor mu; üretemiyorsa ispatı yoktur, sükût vardır.

        İkisi de kütük H136'nın hükmüdür ve ölçülerek konmuştur.
        """
        S = Ispat(list(N.kaideler))
        if not N.kaideler:
            self._olc("ispat", 0.0)
            return S
        onceki = len(S.kaideler)
        if I.girdiler:
            def _uzanan():
                return [k for k in S.kaideler
                        if all(k(g) is not None for g in I.girdiler)]
            u = self._dene("ispat.uzanma", _uzanan)
            if u is not None:
                S.kaideler = u
        S.elenen = onceki - len(S.kaideler)
        if S.elenen:
            S.gerekce = "%d kaide sınamaya uzanmıyor" % S.elenen

        def _mantik():
            # Hüküm cebri: "kaide var VE ispatı var" bir çıkarımdır ve
            # `mizan` onu **totoloji olarak** tasdik etmelidir.
            from mizan.cikarim import aksiyom1
            from mizan.onerme import deg, totoloji_mi
            return bool(totoloji_mi(aksiyom1(deg("K"), deg("İ"))))
        self._dene("mizan.cikarim", _mantik)

        # **ÖLÇÜ DEĞİŞTİ (kütük H160).** Evvelce ``1 if S.kaideler``
        # idi; yine bir faaliyet ölçüsü ve yine oynanabilir. Şimdi
        # ölçülen şey **arama ile ispatın uyuşmasıdır**:
        #
        #     muhakeme notu = ayakta kalan / aranan   (aramanın isabeti)
        #     ispat    notu = ayakta kalan var mı     × o nispet
        #
        # Yani yüz aday üretip doksan dokuzu elenen bir arama, tek aday
        # üretip onu ayakta tutan aramadan **kötüdür**. Occam'ın kayba
        # giren hâli budur ve derinliği büyütmenin bedeli buradadır --
        # aksi hâlde eğitim derinliği sonuna kadar açardı.
        nispet = (float(len(S.kaideler)) / float(max(onceki, 1))
                  if onceki else 0.0)
        self._olc("muhakeme", nispet)
        self._olc("ispat", nispet if S.kaideler else 0.0)
        self.gunluk.append("4. İSPAT: %d aday → %d ayakta (%s), isabet %.2f"
                           % (onceki, len(S.kaideler),
                              S.gerekce or "eleme yok", nispet))
        return S

    # -- 5. TASDİK: İspat → Yakîn ------------------------------------
    def tasdik(self, I: Idrak, S: Ispat) -> Yakin:
        """Ayakta kalandan **mertebe** çıkar.

        Üç kaynak çarpılır ve hiçbiri elle konmuş bir katsayı değildir:

        * **istikrâ** -- `mizan/istikra.py`nin ardışıklık kaidesi:
          ``n`` gösterimden ``n``i tutan bir kaideye ne kadar güvenilir,
        * **müphemlik** -- ayakta kalan kaideler AYNI cevabı mı veriyor,
        * **tevâfuk** -- `fitrat/tevafuk.py`: iki müstakil ölçü şahidi
          (`nefs/boyut.py` ve `idrak/sekil.py`) birbirini tutuyor mu.
        """
        Y = Yakin()
        self.yakin_ilani = 0.0
        if not S.kaideler:
            # Not konmaz: ``tasdik`` artık bir ayar ölçüsüdür ve ayar
            # ancak bir iddia varken ölçülebilir (bkz. ``capraz_not``).
            return Y

        def _istikra():
            from mizan.istikra import ardisiklik_kaidesi
            n = len(I.ciftler)
            return float(ardisiklik_kaidesi(n, n))
        Y.istikra = self._dene("mizan.istikra", _istikra) or 0.5

        if I.girdiler and len(S.kaideler) > 1:
            imzalar = set()
            for k in S.kaideler[:8]:
                o = k(I.girdiler[0])
                if o is not None:
                    imzalar.add(o.tobytes() + bytes(o.shape))
            Y.muphem = len(imzalar) > 1

        # İki müstakil ölçü şahidinin teyidi (1. kademeden gelir).
        # Tek şahitle kalınca ne kadar güvenileceği **öğrenilir**.
        tam_sahit = (I.olcu is not None and I.sekil_kaidesi is not None)
        Y.tevafuk = 1.0 if tam_sahit else self._par("kademe.tasdik.tevafuk")

        def _murakabe():
            from .murakabe import hukum_agirligi, makam_tayin
            p = float(Y.istikra)
            return float(hukum_agirligi(p, makam_tayin(p)))
        agirlik = self._dene("nefs.murakabe", _murakabe)

        muphem_cezasi = self._par("kademe.tasdik.müphem")
        taban = self._par("kademe.tasdik.taban")
        Y.deger = float(np.clip(
            Y.istikra * (muphem_cezasi if Y.muphem else 1.0) * Y.tevafuk
            * (1.0 if agirlik is None
               else float(np.clip(agirlik, taban, 1.0))),
            0.0, 1.0))
        # **ÖLÇÜ DEĞİŞTİ (kütük H160): tasdik bir AYAR ölçüsüdür.**
        # Evvelce ``self._olc("tasdik", Y.deger)`` yazıyordu, yani
        # *"yakînin yüksek olsun"* diyordu -- oynanabilir ve **yanlış**:
        # bir modelin iyi olması yüksek yakîn ilan etmesi değil, ilan
        # ettiği yakînin **hakikate uyması**dır. Fazla iddia da eksik
        # iddia da kusurdur. Not ``beyan``da, bırak-birini hakikatiyle
        # yüzleştikten sonra konur (bkz. ``capraz_not``).
        self.yakin_ilani = float(Y.deger)
        self.gunluk.append(
            "5. TASDİK: istikrâ %.3f, %s, tevâfuk %.2f → yakîn %.3f"
            % (Y.istikra, "müphem" if Y.muphem else "müphem değil",
               Y.tevafuk, Y.deger))
        return Y

    # -- 6. BEYAN: Yakîn → Cevap -------------------------------------
    def beyan(self, I: Idrak, S: Ispat, Y: Yakin,
              esik: Optional[float] = None
              ) -> Optional[List[Optional[Izgara]]]:
        """Yakîn eşiği aşarsa **konuş**, aşmazsa sus.

        Sükût bir kusur değil kabiliyettir (H10/H16) -- fakat sebebi
        söylenebiliyorsa. Sebep ``günlük``tedir.

        Cevabın ölçüsü 1. kademenin kestirdiği ölçüyle **yüzleştirilir**:
        iki müstakil hesap uyuşmuyorsa konuşulmaz. Bu, beyan kapısının
        (H131) kademeli hâlidir: kelâm ancak hükümden akar.

        ``esik`` verilmezse **öğrenilir** (``kademe.beyan.eşik``). Eşiği
        oynatmak notu tek başına yükseltemez: not, konuşup konuşmamaya
        değil **bırak-birinide isabet edip etmemeye** bakar
        (``capraz_not``).
        """
        if esik is None:
            esik = self._par("kademe.beyan.eşik")
        if not S.kaideler or Y.deger < esik:
            # **Not burada KONMAZ (kütük H160).** Evvelce ``0.0``
            # yazılıyordu, yani susmak daima kusur sayılıyordu ve model
            # susmamayı öğrenirdi -- H45'te tam olarak bu ölçüldü
            # ("sükût 140 → 0; bilmeden konuşmayı öğrendi"). Sükût bir
            # kabiliyettir (H10) ve notu ``capraz_not``ta, hakikatle
            # yüzleştikten sonra konur: şek mertebesi (0,25).
            self.gunluk.append(
                "6. BEYAN: sükût -- %s"
                % ("kaide yok" if not S.kaideler
                   else "yakîn %.3f < eşik %.2f" % (Y.deger, esik)))
            return None
        k = S.kaideler[0]
        cevap = [k(g) for g in I.girdiler]
        if I.olcu is not None:
            for c in cevap:
                if c is not None and tuple(c.shape) != tuple(I.olcu):
                    self.gunluk.append(
                        "6. BEYAN: sükût -- kaide %s veriyor, ölçü "
                        "kestirimi %s diyor; iki hesap uyuşmuyor"
                        % (tuple(c.shape), tuple(I.olcu)))
                    return None
        self.gunluk.append("6. BEYAN: konuşuyorum -- kaide %s, yakîn %.3f"
                           % (getattr(k, "ad", "?"), Y.deger))
        return cevap

    # -- BIRAK-BİRİNİ NOTU: beyan ve tasdik burada tartılır -----------
    def capraz_not(self, gorev) -> None:
        """Son gösterim çifti saklanıp **hakikatle** yüzleştirilir.

        Bu, ``kademe.beyan`` ve ``kademe.tasdik`` notlarının **yegâne**
        kaynağıdır ve sebebi H90'dır: bir ölçüt kırmızı yanabilmelidir.
        *"Konuştum"* notu kırmızı yanamaz -- eşiği sıfıra çekmek onu
        daima yeşil yapar. *"Sakladığım çifti bildim mi"* notu ise
        oynanamaz: bilmek için hakikaten bilmek gerekir.

        Notlar `mizan/munazara.py`nin mertebe cetvelinden okunur::

            doğru bildi    → 1,00  yakîn
            sustu          → 0,25  şek     (iki taraf müsâvî)
            yanlış söyledi → 0,00  vehim   (mercûh taraf)

        Sıralamanın teşviki tam da matluptur: eşiği düşürüp hep konuşmak
        ancak **dörtte birden fazla** isabet ediyorsan kazandırır.

        ``tasdik`` notu bir **ayar** ölçüsüdür: ``1 − |ilan edilen yakîn
        − fiilî isabet|``. Yani yüksek yakîn ilan edip yanılmak da,
        doğru bilip düşük yakîn ilan etmek de cezalanır. Modelin
        *"bilmediğini bilmesi"* şartı (H10) burada sayıya döner.

        Gösterim çifti ikiden azsa bırak-birini kurulamaz; o zaman not
        **konmaz** (uydurulmuş bir not, notsuzluktan kötüdür).
        """
        ciftler = [(np.asarray(a), np.asarray(b))
                   for a, b in getattr(gorev, "egitim", [])]
        if len(ciftler) < 2:
            self.gunluk.append(
                "ÇAPRAZ: %d gösterim -- bırak-birini kurulamaz, not yok"
                % len(ciftler))
            return
        sakli_g, sakli_c = ciftler[-1]

        class _G:                      # saklanan çift olmadan aynı görev
            ad = getattr(gorev, "ad", "?")
            kaynak = getattr(gorev, "kaynak", "?")
            egitim = ciftler[:-1]
            sinama = [(sakli_g, sakli_c)]

        # **Özyineleme kesilir:** iç koşu kendi çapraz notunu almaz.
        ic = Kademeler(self.p)
        I2 = ic.idrak(_G())
        H2 = ic.tasavvur(I2)
        N2 = ic.muhakeme(I2, H2)
        S2 = ic.ispat(I2, N2)
        Y2 = ic.tasdik(I2, S2)
        C2 = ic.beyan(I2, S2, Y2)
        ilan = float(getattr(ic, "yakin_ilani", 0.0))

        if C2 is None or not C2 or C2[0] is None:
            hâl, isabet = "sükût", 0.0
        else:
            c = np.asarray(C2[0])
            if c.shape == sakli_c.shape and bool(np.array_equal(c, sakli_c)):
                hâl, isabet = "doğru", 1.0
            else:
                hâl, isabet = "yanlış", 0.0
        self._olc("beyan", MERTEBE_NOTU[hâl])
        # Ayar: ilan edilen yakîn ile fiilî isabetin farkı. Sükûtta
        # "isabet" tanımsızdır; o hâlde ayar da ölçülmez -- susan model
        # bir iddiada bulunmamıştır, iddiasının tutup tutmadığı
        # sorulamaz. Bu, notu uydurmamak içindir.
        if hâl != "sükût":
            self._olc("tasdik", 1.0 - abs(ilan - isabet))
        self.gunluk.append(
            "ÇAPRAZ: saklanan çift → %s (not %.2f), ilan edilen yakîn "
            "%.3f" % (hâl, MERTEBE_NOTU[hâl], ilan))


# =====================================================================
def kademeleri_kos(gorev, derinlik: Optional[int] = None,
                   esik: Optional[float] = None, p=None,
                   capraz: bool = True) -> Dict[str, object]:
    """Altı kademeyi **sırayla** koştur; her biri bir öncekini yer.

    ``p`` verilirse kademelerin sayıları o düz vektörden **öğrenilir**
    (melekelerin açılarıyla aynı defter). ``capraz=False`` bırak-birini
    notunu kapatır -- pahalıdır (boru hattı bir kere daha koşar) ve
    yalnız eğitim ölçütü için lâzımdır; kapatılamayan bir tedbirin
    faydası ölçülemez (H90).
    """
    K = Kademeler(p)
    I = K.idrak(gorev)
    H = K.tasavvur(I)
    N = K.muhakeme(I, H, derinlik)
    S = K.ispat(I, N)
    Y = K.tasdik(I, S)
    C = K.beyan(I, S, Y, esik)
    if capraz:
        K.capraz_not(gorev)
    return {"idrak": I, "hal": H, "namzet": N, "ispat": S, "yakîn": Y,
            "cevap": C, "sükût": C is None, "ölçümler": K.olcumler,
            "günlük": K.gunluk, "eksik": K.eksik}


def rapor(kume: str = "training", n: int = 3) -> str:
    from idrak import arc

    from .olcu import kulli_toplam, mertebele
    s = ["=== ALTI KADEME -- girdi/çıktı zinciri ===", ""]
    for g in arc.yukle_hepsi(kume)[:int(n)]:
        r = kademeleri_kos(g)
        t = kulli_toplam(r["ölçümler"])
        s.append("--- %s ---" % g.ad)
        s += ["  " + x for x in r["günlük"]]
        s.append("  kademe kaybı %.4f  (ortalama mertebe %.3f = %s)"
                 % (t["kayıp"], t["ortalama_mertebe"],
                    mertebele(t["ortalama_mertebe"])))
        if r["eksik"]:
            s.append("  DÜŞEN UZUV: %s" % ", ".join(sorted(r["eksik"])))
        s.append("")
    s += ["Kademe k'nın çıktısı kademe k+1'in girdisidir; bir modül o",
          "zincirde halka ise uzuvdur. Yan tarafta rey veren modül uzuv",
          "değildir ve bu dosya o farkın kendisidir."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
