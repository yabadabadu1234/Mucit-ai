"""
TERTİP -- mantık usullerini SÜPERPOZİSYONDA koşturan yönlendirici.

Kullanıcı hükmü (H102): *"Mantık yürütme, kalbin Tertip melekesi
vasıtasıyla seçtiği bir stratejidir."* Ve Dosya 8: *"Tertip, 16 mantık
manifoldunu kuantum süperpozisyonunda yöneten koherent bir Router'dır."*

===================================================================
"SEÇMEK" DEĞİL "DOLAŞTIRMAK" -- ve niçin
===================================================================

Kullanıcının şeması *"Kalp, Tertip'e emir verir; Tertip uygun manifoldu
SEÇER"* diyor. Bu, olduğu gibi alınırsa H31'i kırar: duruma bakıp
seçmek bir **okumadır** ve dalgayı çökertir. Bunu evvelce de söyledim
(H102'nin tenkidi) ve Dosya 8 kendi içinde zaten doğrusunu getiriyor:

    |Q_tertip⟩ ──[ H ]──●──  (Mod Seçimi: SÜPERPOZE)
                        │
    |Durum⟩ ────────[ V_router ]──► |M₁⟩ ⊕ … ⊕ |M₁₆⟩  (eşzamanlı açılır)

Yani vesikanın kendi devresi "seçmiyor", **dolaştırıyor**. Burada icra
edilen budur: ``tertip`` yazmacı süperpozisyona sokulur, her usul kendi
tertip koluna **kontrollü** olarak vurulur, ve hangi usulün işe
yaradığını girişim söyler. İşe yaramayan usulün kolu söner.

===================================================================
USUL NEDİR -- ve mizan buraya NASIL BAĞLANIR
===================================================================

Bir mantık usulü, hüküm kübitleri üzerinde bir **önermedir**. Bu
projede önermelerin motoru zaten yazılıydı ve **beylikti**:
`mizan/onerme.py` -- hash-consing'li formül düğümleri ve bit-paralel
doğruluk tablosu (bütün ``2ⁿ`` değerleme tek bir tam sayıda).

Buradaki bağ şudur ve zorlama değildir:

1. Usul, ``mizan.onerme`` ile bir formül olarak **kurulur**.
2. Formülün doğruluk tablosu ``mizan.onerme.Tablo`` ile **tam** çıkarılır
   (yaklaşık değil; kesin karar).
3. Tablonun **yanlış** çıktığı her değerleme, kübit yazmacında
   ``nefs/isaret.py`` ile işaretlenir.
4. İşaret, ``tertip`` yazmacının o usule ait koluna **kontrollüdür**.

Böylece ``mizan`` bir "kütüphane" olarak değil, doğrudan **devrenin
kaynağı** olarak bağlanır: usulün hangi hâlleri yasakladığını mizan
söyler, kübit tarafı yalnız icra eder. İkisi ayrı düşerse mizan
haklıdır (H88'in dersi: hakikat kaynağı klasik taraftır).

===================================================================
İDDİA EDİLMEYEN
===================================================================

* Dosya 8'in ∞-operad kompozisyonu, Grothendieck liflenmesi, traced
  monoidal devridaim ve Čech kohomolojisiyle uzay kapatma kısımları
  **kurulmadı**. Burada kurulan, yalnız **süperpoze yönlendirici**dir.
* Dört usul kuruldu, on altı değil. Sayı ``USULLER``e eklemekle artar;
  eklenince tertip yazmacı da büyümelidir.
* Usullerin hükmü ``beyan``a ne kadar tesir ediyor, **ölçülür**
  (`tanilama/haraplama.py`) ve iddia edilmez.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np

from mizan.onerme import Onerme, Tablo, deg, degil, ise, ve, veya

from .isaret import cok_kontrollu_isaret
from .zihin_durumu import QYazmac, donme

__all__ = ["Usul", "USULLER", "usul_yasaklari", "tertip_kos"]


# =====================================================================
#: Usullerin üzerinde konuştuğu hüküm alanları -- **sıra mühimdir**,
#: ``mizan`` değişkeni ile kübit yuvası bu sırayla eşlenir.
ALANLAR: Tuple[Tuple[str, int], ...] = (
    ("tasdik", 0), ("nakz", 0), ("mizan", 0), ("kelam", 0), ("sukut", 0),
)


def _degiskenler() -> Dict[str, Onerme]:
    return {ad: deg(ad) for ad, _ in ALANLAR}


class Usul:
    """Bir mantık usulü: ``mizan`` formülü + kübit yuvalarına eşlemesi.

    Formül **doğru** olduğu değerlemeler meşrudur; **yanlış** olduğu her
    değerleme mantık dışıdır ve işaretlenir. Yani usul bir yasak
    listesidir ve o listeyi ``mizan`` çıkarır, ben çıkarmam.
    """

    def __init__(self, ad: str, kur: Callable[[Dict[str, Onerme]], Onerme],
                 izah: str = "") -> None:
        self.ad = ad
        self.izah = izah
        self.formul = kur(_degiskenler())

    def yasaklar(self) -> List[Dict[str, int]]:
        """Formülün **yanlış** çıktığı değerlemeler -- ASGARÎ hâlleriyle.

        ``mizan.onerme.Tablo`` bütün ``2ⁿ`` değerlemeyi tek tam sayıda
        tutar; karar **tamdır**, yaklaşık değil.

        **ÖLÇÜLEN VE DÜZELTİLEN KUSUR.** Evvelce tablo BÜTÜN alanlar
        üzerinden kuruluyordu; halbuki her formül ancak birkaçına
        bağlıdır. ``¬(tasdik ∧ nakz)`` tek bir örüntüdür, fakat beş
        değişken üzerinden sayılınca serbest üç değişkenin ``2³ = 8``
        bileşimi ayrı ayrı yazılıyordu. Netice: usul başına 8 MPO,
        toplam 32; ve **kesme 1,8e+01**e fırlıyordu (χ patlaması).

        Doğrusu, formülün fiilen bağlı olduğu değişkenleri
        ``Onerme.degiskenler()``den almak ve tabloyu yalnız onlar
        üzerinde kurmaktır. O zaman her usul **tek** örüntü verir ve
        işaret ``≤3`` kontrollü kalır.
        """
        adlar = sorted(self.formul.degiskenler())
        if not adlar:
            return []
        t = Tablo(adlar)
        sutun = t.sutun(self.formul)
        yasak: List[Dict[str, int]] = []
        for i in range(1 << t.n):
            if not ((sutun >> i) & 1):                # formül YANLIŞ
                yasak.append({ad: (i >> t.yer[ad]) & 1 for ad in adlar})
        return yasak


#: Kurulan usuller. Her biri `mizan/onerme.py` ile tarif edilir.
USULLER: Tuple[Usul, ...] = (
    Usul("tenakuzsuzluk",
         lambda v: degil(ve(v["tasdik"], v["nakz"])),
         "Bir hüküm hem mühürlenip hem nakzedilemez."),
    Usul("kâfi_sebep",
         lambda v: ise(v["tasdik"], v["mizan"]),
         "Mühür ancak delille olur: tasdik varsa mîzân da uyanık olmalı."),
    Usul("kelâm_şartı",
         lambda v: ise(v["kelam"], v["tasdik"]),
         "Mühürlenmemiş hükümle konuşulmaz."),
    Usul("sükût_şartı",
         lambda v: degil(ve(v["sukut"], v["tasdik"])),
         "Susarken mühürlemek olmaz (kütük H10)."),
)


def usul_yasaklari() -> Dict[str, List[Dict[str, int]]]:
    """Her usulün yasakladığı hâller -- **mizan'ın hükmü**, rapor için."""
    return {u.ad: u.yasaklar() for u in USULLER}


# =====================================================================
def tertip_kos(q: QYazmac, usuller: Sequence[Usul] = USULLER) -> float:
    """Bütün usulleri **aynı anda** koştur -- her biri kendi tertip kolunda.

    ``tertip`` yazmacı evvelâ süperpozisyona sokulur; sonra her usulün
    yasakları, o usule ait tertip kübiti ``|1⟩`` iken işaretlenir. Yani
    bir usul "açık" da "kapalı" da değildir -- **ikisi birden**dir ve
    hangisinin işe yaradığını girişim tayin eder.

    Dönen: toplam kesme. Bütün işaretler köşegen olduğu için ``~1e-16``
    beklenir.
    """
    _, kac = q._alan["tertip"]
    yuv = [q.kulli("tertip", j) for j in range(kac)]
    # süperpozisyon: her usul hem denenir hem denenmez
    q.tek_yigin(yuv, np.stack([donme(0.25 * math.pi)] * len(yuv)))

    kesme = 0.0
    for i, u in enumerate(usuller[:kac]):
        for yasak in u.yasaklar():
            # Yalnız formülün bağlı olduğu alanlar kısıtlanır; ötekiler
            # serbest bırakılır (yukarıdaki ölçülmüş kusurun düzeltmesi).
            orutu = {q.kulli(ad, dict(ALANLAR)[ad]): b
                     for ad, b in yasak.items()}
            orutu[yuv[i]] = 1                 # o usul AÇIK olan kolda
            kesme += cok_kontrollu_isaret(q, orutu)
    return kesme
