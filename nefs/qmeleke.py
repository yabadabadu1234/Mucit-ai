"""
41 melekenin **üniter** hâli -- hiçbiri okumaz, hepsi kapıdır.

Kullanıcı hükmü: *"Her meleke bizzat bir üniter olsun, hiç reel görüş
alınmasın"* ve *"hüküm de üniter olsun: makam bir faza kodlansın"*.
Buradaki 41 sınıfın hiçbirinde ``yuva_yogunluklari``, ``povm`` yahut
başka bir okuma çağrısı **yoktur**. Melekeler dalgayı büker; hükmün
sayısı ancak en sonda, tek bir zayıf ölçümle okunur (kütük H31).

Bunun bedeli açıktır ve saklanmaz: bir meleke kendi girdisine bakıp
"şuna göre şu kadar dönderelim" diyemez. Açılar ya **parametreden**
gelir (öğrenilir; ``Parametreler`` tohumludur ve tekrarlanabilir) ya da
melekenin kendi tarifinden (altın oran, ∞-kategori mertebesi). Bilginin
kendisi açıya değil, **dolaşıklığa** girer: kontrollü dönme, veriyi
hükümle dolaştırır; hangi hükmün uyandığı veriye bağlıdır, fakat bu
bağlılık hiçbir yerde sayıya dökülmez.

Kullanılan kapılar ve maliyetleri:

* ``tek(i, R)``        -- ``O(χ²)``, bedava sayılır.
* ``cift(i, G)``       -- komşu çift, bir SVD.
* ``uzak_cift(i,j,G)`` -- takas ağı; **yalnız küllî blok içinde** ve
  kısa mesafede kullanılır (blok 13 kübittir).
* ``mpo_topla`` / ``mpo_dagit`` -- uzun menzil; kübit oynamaz, bağ 2,
  kesme ölçüldü: χ=64'te 2.7e-03 (takas ağı aynı işte 2.06e+01 idi).

Uzun menzilli her iş MPO iledir. Takas ağı zincirin gövdesinde
**kullanılmaz**; ölçüldü ve dolaşıklığı yok ediyordu.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from main.yazmac import dik_iki_kubit

from .mertebe import DINAMIK, lifleri_kur
from .qyazmac import (QYazmac, degil_x, donme, faz_z, kontrollu_donme)
from .uzaylar import Parametreler

__all__ = ["QMeleke", "qsicil", "qmelekeler", "QAKIS",
           "NIZAM_ACIK", "nizami_ac", "nizam_cetveli"]

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

    def uygula(self, q: QYazmac, p: Parametreler) -> None:  # pragma: no cover
        raise NotImplementedError

    def kosu(self, q: QYazmac, p: Parametreler) -> None:
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
            self.uygula(q, p)
        finally:
            q.y.bag_tavan = eski
        q.iz.not_dus("𝒪%d %s" % (self.no, self.ad),
                     "%d kapı" % (q.iz.kapi - n0))

    # -- müşterek desenler -------------------------------------------
    def tugla(self, q: QYazmac, p: Parametreler, ofset: int = 0,
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

    def satir_donmesi(self, q: QYazmac, p: Parametreler,
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


#: Akış sırası -- reel modelin ``AKIS``ıyla birebir aynı (𝒪₁₃ iki kere).
QAKIS: Tuple[int, ...] = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24,
    25, 26, 27, 28, 29, 30, 31, 32,
    33, 13,
    34, 35, 36,
    37, 38, 39, 40, 41,
)
