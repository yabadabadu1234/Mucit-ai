"""
KEYFİYET -- ÜÇ KAT'Î HUDUT VE ONLARIN TEMİZLİK NİSPETİ

===================================================================
PADİŞAHIN HÜKMÜ (ferman 1-I ve 1-J)
===================================================================

    "Sıfırlanmaktan en bariz kastım şu: kesinlikle tenakuz, kısırdöngü,
    mantıksızlık olmayacak, bunlar kesin huduttur, bunun haricinde zaten
    sıfır olamaz ama eşik koyarken sabit bir değer koymayacaksın, bir
    fonksiyona bağlı olacak o eşik. Yâni kemiyete değil keyfiyete, o
    keyfiyetin ne nispete eriştiğini ölçen bir fonksiyon vasıtasıyla."

Bu iki cümle iki ayrı şey söyler ve karıştırılırsa ikisi de bozulur:

**1. KAT'Î HUDUT -- İKİLİDİR, EŞİĞİ YOKTUR.**
Tenakuz, kısırdöngü ve mantıksızlık ya vardır ya yoktur. Bunlara eşik
konmaz; "az tenakuz" diye bir şey yoktur. Üçü de **sayılır** ve üçü de
**sıfır olmak zorundadır**::

    hudut_temiz = (tenakuz == 0) ∧ (kısır == 0) ∧ (taşma == 0)

**2. KEYFİYET NİSPETİ -- SÜREKLİDİR, EŞİĞİ FONKSİYONDUR.**
Hudut temizlendikten sonra "ne kadar iyi" sorusu kalır ve onun cevabı
bir sayı değil, bir **nispettir**: keyfiyetin eriştiği mertebe. Eşik de
sabit bir sayı değil, o nispeti ölçen fonksiyonun kendisidir.

===================================================================
EŞİK NİÇİN SABİT OLAMAZ -- ÖLÇÜLMÜŞ SEBEP
===================================================================

Kodda evvelce ``zeno_esigi = 0.35``, ``tevakkuf_esigi = 0.35``,
``merak_esigi = 0.5``, ``usul_haddi = 0.0`` gibi sabitler vardı. Her
biri bir kere ölçülmüştü, fakat ölçüldüğü şart değişince yerinde kaldı.
Daha kötüsü: sabit eşik **kemiyet** ölçer. ``0,35``in manası "kaybın
büyüklüğü"dür; halbuki sorulan soru "mantık temiz mi"dir ve o bir
büyüklük değil, bir **keyfiyettir**.

Buradaki eşik şudur ve bir sayı değildir::

    eşik(t) = en_iyi_nispet_şimdiye_kadar × kalan_bütçe_nispeti

Yâni: *"bugüne kadar erişebildiğimin ne kadarına, kalan vaktimle
erişmem beklenir?"* Bütçe tükendikçe eşik iner (elde olanla yetinilir);
keyfiyet yükseldikçe eşik yükselir (bir daha o kadarını isteriz). Sabit
hiçbir sayı yoktur ve eşik **kendi ölçtüğü şeyden** doğar.

===================================================================
NİSPET NASIL KURULUR
===================================================================

Üç hudut, kemiyetleriyle değil **temizlik nispetleriyle** girer::

    n_tenakuz = 1 − tenakuz_çevrimi / çevrim
    n_kısır   = 1 − kısır_çevrimi   / çevrim
    n_mantık  = 1 − kod_uzayı_dışı_ağırlık

Ve nispet **çarpımdır, ortalama değil**: bir hudut kirliyse netice
kirlidir. Ortalama alsaydık, iki temiz hudut bir kirliyi örterdi --
tam da fermanın yasakladığı şey.

    nispet = n_tenakuz · n_kısır · n_mantık
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

__all__ = ["KeyfiyetAyari", "keyfiyet", "esik", "keyfiyet_beyani",
           "keyfiyet_sifirla"]


@dataclass
class KeyfiyetAyari:
    """Keyfiyet ölçüsünün ayarları. **Eşik burada YOKTUR** -- eşik bir
    ayar değil, ``esik()`` fonksiyonunun neticesidir."""

    #: ``0`` = keyfiyet kapısı kapalı: münasebet döngüsü tek turda
    #: geçer ve hudut denetlenmez. Ferman 5.
    acik: int = 1
    #: Bir örnek üstünde azamî kaç tur durulacak. Bu bir eşik değil,
    #: bir **bütçedir**: hudut temizlenmezse sonsuza kadar durulmaz.
    azami_tur: int = 8
    #: Bütçe tükenirken eşiğin ineceği taban nispet. ``esik()``in
    #: çarpanıdır, eşiğin kendisi değil.
    taban: float = 0.25


#: Koşu boyunca erişilen en iyi nispet. **Eşik bundan doğar**; bir
#: sabitten değil. Modül seviyesindedir çünkü keyfiyet bir örneğin
#: değil, **koşunun** hâlidir: bir örnekte erişilen mertebe, öteki
#: örneklerden ne beklendiğini tayin eder.
_HAL: Dict[str, float] = {"en_iyi": 0.0, "çağrı": 0.0, "toplam": 0.0,
                          "temiz": 0.0, "kirli": 0.0}
_GECMIS: List[float] = []


def keyfiyet(kefeler: Dict[str, Any],
             sadakat: Optional[Dict[str, Any]] = None,
             ayar: Optional[KeyfiyetAyari] = None) -> Dict[str, Any]:
    """**ÜÇ HUDUDU ÖLÇ.** İkili hüküm + sürekli nispet, ayrı ayrı.

    ``kefeler`` ``kulli_mizan(..., ne="döküm")``in neticesidir;
    ``sadakat`` ``nefs/sadakat.py:sadakat_beyani()``.

    Dönen sözlükte iki ayrı şey vardır ve karıştırılmaz:

    ``hudut_temiz``  -- **ikili**. Üç kat'î hudut da sıfır mı?
    ``nispet``       -- **sürekli**. Keyfiyet hangi mertebeye erişti?
    """
    a = ayar or KeyfiyetAyari()
    _HAL["çağrı"] += 1.0

    cevrim = max(1, int(kefeler.get("meşru", 0)) + int(kefeler.get("kısır", 0))
                 + int(kefeler.get("tenakuz", 0)) + int(kefeler.get("engel", 0)))
    n_ten = int(kefeler.get("tenakuz", 0))
    n_kis = int(kefeler.get("kısır", 0))
    # Mantıksızlık: kod uzayı dışına taşan ağırlık. Sadakat kapısı
    # açıkken bu **sıfırlanmış** olmalıdır; sıfır değilse zemin
    # koşmuyor demektir ve o bir mimarî çöküştür.
    tasma = float((sadakat or {}).get("alarm_nispeti", 0.0))

    # ── ÜÇ NİSPET ────────────────────────────────────────────────
    nis_ten = 1.0 - float(n_ten) / cevrim
    nis_kis = 1.0 - float(n_kis) / cevrim
    nis_man = max(0.0, 1.0 - tasma)
    # **ÇARPIM, ORTALAMA DEĞİL.** Bir hudut kirliyse netice kirlidir;
    # ortalama alsaydık iki temiz hudut bir kirliyi örterdi.
    nispet = float(nis_ten * nis_kis * nis_man)
    assert 0.0 <= nispet <= 1.0 + 1e-9, "nispet [0,1] dışına çıktı"

    # ── KAT'Î HUDUT: İKİLİ, EŞİĞİ YOK ────────────────────────────
    hudut = {"tenakuz": n_ten, "kısırdöngü": n_kis,
             "mantıksızlık": int(tasma > 1e-12)}
    temiz = all(v == 0 for v in hudut.values())

    _HAL["toplam"] += nispet
    _HAL["en_iyi"] = max(_HAL["en_iyi"], nispet)
    _HAL["temiz" if temiz else "kirli"] += 1.0
    _GECMIS.append(nispet)
    return {"hudut": hudut, "hudut_temiz": bool(temiz), "nispet": nispet,
            "nispet_tenakuz": nis_ten, "nispet_kısır": nis_kis,
            "nispet_mantık": nis_man, "çevrim": cevrim,
            "açık": bool(int(a.acik))}


def esik(tur: int, azami_tur: int,
         ayar: Optional[KeyfiyetAyari] = None) -> float:
    """**EŞİK BİR SAYI DEĞİL, BİR FONKSİYONDUR** (ferman 1-J).

        eşik(t) = en_iyi_nispet × (taban + (1−taban)·(1 − t/T))

    * ``en_iyi_nispet`` koşu boyunca fiilen **erişilmiş** en yüksek
      keyfiyettir. Yâni eşik, elde edilemeyecek bir şeyi istemez:
      istediği şey, bir kere yapılabildiği **ölçülmüş** olandır.
    * İkinci çarpan bütçenin kalanıdır: vakit ilerledikçe eşik iner ve
      elde olanla yetinilir. Sonsuza kadar bir örnekte durmak, öteki
      bütün örnekleri kaybetmektir.
    * Hiçbir sabit yoktur: ``taban`` bile eşiğin kendisi değil, inişin
      dibidir ve o da bir nispettir.

    Koşunun başında ``en_iyi = 0``dır ve eşik ``0`` olur -- yâni ilk
    örnekte hiçbir şey istenmez, yalnız **ölçülür**. Eşik, ancak
    ölçülmüş bir keyfiyet varken doğar.
    """
    a = ayar or KeyfiyetAyari()
    T = max(1, int(azami_tur))
    kalan = max(0.0, 1.0 - float(tur) / T)
    t = float(a.taban)
    return float(_HAL["en_iyi"] * (t + (1.0 - t) * kalan))


def keyfiyet_beyani() -> Dict[str, Any]:
    """Koşunun keyfiyet hâli. **Taht bunu ``assert`` ile denetler.**"""
    c = max(1.0, _HAL["çağrı"])
    g = np.asarray(_GECMIS, float) if _GECMIS else np.zeros(1)
    return {"çağrı": int(_HAL["çağrı"]),
            "en_iyi": float(_HAL["en_iyi"]),
            "ortalama": float(_HAL["toplam"] / c),
            "ortanca": float(np.median(g)),
            "temiz": int(_HAL["temiz"]), "kirli": int(_HAL["kirli"]),
            "temiz_nispeti": float(_HAL["temiz"] / c),
            "son_eşik": float(esik(0, 1))}


def keyfiyet_sifirla() -> None:
    for k in _HAL:
        _HAL[k] = 0.0
    _GECMIS.clear()
