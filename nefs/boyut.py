"""
Çıktı ızgarasının boyutu -- **kullanıcının koyduğu ara ölçüt**.

Kullanıcı hükmü (H47): ölçüt ikidir ve ikisi de her raporda yan yana
yazılır -- **boyut isabeti** (ara) ve **tam çözüm** (nihai). Ara ölçüt
ilerlemeyi gösterir; tam çözüm hükmü verir. Ara ölçüt yükselirken tam
çözüm sıfır kalıyorsa bu da bir hükümdür ve gizlenmez.

Neden boyut? Ölçüldü: ARC çiftlerinin **%28'inde** çıktı ızgarasının
boyutu girdiden farklıdır ve şu ana kadar hiçbir kanal bunu tahmin
etmiyordu. Kaçamak yeri olmayan bir ölçüdür: kaide eğitim çiftlerinden
çıkarılır, test girdisine tatbik edilir, doğru mu değil mi -- bitti.

**Bu bir öğrenme değildir.** Kaideler sayılıdır ve hepsi ``müşahede``den
okunur (nesne sayısı, en büyük nesnenin kutusu, dolu bölgenin sınırı...).
Eğitim çiftlerinin **hepsini** sağlamayan kaide reddedilir; hiçbir kaide
sağlamıyorsa model **susar** (kütük H10: bilmediğini söylememek bir
kabiliyettir) ve o görev "kaide yok" diye sayılır -- yanlış tahminle
değil.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .mubser import Mesud, musahede_et

__all__ = ["KAIDE_ADLARI", "cikti_ne_kadar"]

Boyut = Tuple[int, int]


# =====================================================================
#  Kaide dağarcığı -- adları; gövdeleri tek terkiptedir
# =====================================================================
#: Sıra mühimdir: **ilk** tutan kaide kabul edilir, o yüzden hususî
#: olanlar umumîlerden evvel denenmez -- umumî olan (``ayni``) en
#: başta durur ki tesadüfî bir hususî kaide onu gölgelemesin.
KAIDE_ADLARI: Tuple[str, ...] = (
    "aynı", "devrik", "dolu_kutu", "en_büyük_nesne", "en_küçük_nesne",
    "tek_nesne", "nesne_sayısı_kare", "renk_sayısı_kare", "nesne_katı",
    "×2", "÷2", "×3", "÷3", "×4", "÷4", "×2 yatay", "×2 dikey",
)


def cikti_ne_kadar(ciftler=None, girdi=None, ne: str = "tahmin",
                   ad: str = "", g=None, m=None, kh: int = 1, kw: int = 1,
                   gorevler=None):
    """ÇIKTI KAÇ SATIR KAÇ SÜTUN OLACAK -- **tek terkip** (kütük H225).

    Küme: on bir aday kaide (``_ayni, _devrik, _dolu_kutu,
    _en_buyuk_nesne, _en_kucuk_nesne, _tek_nesne, _nesne_sayisi_kare,
    _renk_sayisi_kare, _olcekli, _bolunmus, _nesne_katı``) +
    ``boyut_kaidesi_bul`` + ``boyut_tahmin`` + ``olc``. On üçü tek
    sualin parçalarıydı ve on biri yalnız bir cetvele girmek için
    ayrı isim taşıyordu.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``kaide``       adı verilen kaidenin bu ızgarada verdiği boyut
    ``bul``         eğitim çiftlerinin **hepsini** sağlayan ilk kaide
    ``tahmin``      ``(boyut, kaide_adı)``; bulunamazsa ``(None, sükût)``
    ``ölç``         görev kümesinde kaide isabetinin dökümü
    ==============  ==================================================

    **Hepsini sağlaması şarttır**: tek karşı örnek küllî kaideyi düşürür
    (kütük H6 -- nakz). Bir kaide dokuz çiftin sekizinde tutuyorsa
    **kabul edilmez**; o, kaide değil tesadüftür.

    Sabit boyut kaidesi ayrıca denenir: bütün çıktılar aynı boyutta ise
    o boyut ezberlenebilir. Bu bir kaide değil **ezberdir** ve öyle
    işaretlenir; yine de ARC'de meşru bir kaidedir (bazı görevlerde
    çıktı hep 3×3'tür).

    Kaide bulunamazsa ``(None, "sükût")`` döner -- model **susar**.
    Uydurma bir boyut vermek, bilmediğini söylememekten kötüdür (H10).

    ``_tek_nesne`` ARC'nin en sık kaidelerinden biridir: *"aykırı olanı
    bul ve onu ver"*. Aykırılık şekil imzasının **tekliğinden** okunur;
    ayrı bir sinyal aranmaz.
    """
    def kaide(k: str, gg, mm):
        gg = np.asarray(gg)
        if k == "aynı":
            return (gg.shape[0], gg.shape[1])
        if k == "devrik":
            return (gg.shape[1], gg.shape[0])
        if k == "dolu_kutu":
            # zemin olmayan bölgenin sınırlayıcı kutusu -- kırpma
            idx = np.argwhere(gg != 0)
            if not len(idx):
                return None
            a, b = idx.min(0)
            c, d = idx.max(0)
            return (int(c - a + 1), int(d - b + 1))
        if k in ("en_büyük_nesne", "en_küçük_nesne"):
            if not mm.nesneler:
                return None
            n = mm.nesneler[0 if k == "en_büyük_nesne" else -1]
            return (n.sekil.shape[0], n.sekil.shape[1])
        if k == "tek_nesne":
            if len(mm.nesneler) < 3:
                return None
            imza = {}
            for i, n in enumerate(mm.nesneler):
                anah = (np.asarray(n.sekil, np.uint8).tobytes()
                        + bytes(n.sekil.shape))
                imza.setdefault(anah, []).append(i)
            tekler = [v[0] for v in imza.values() if len(v) == 1]
            if len(tekler) != 1:
                return None
            n = mm.nesneler[tekler[0]]
            return (n.sekil.shape[0], n.sekil.shape[1])
        if k == "nesne_sayısı_kare":
            n = len(mm.nesneler)
            return (n, n) if n else None
        if k == "renk_sayısı_kare":
            n = len(mm.adet)
            return (n, n) if n else None
        if k == "×2 yatay":
            return (gg.shape[0], gg.shape[1] * 2)
        if k == "×2 dikey":
            return (gg.shape[0] * 2, gg.shape[1])
        if k.startswith("×"):
            a = int(k[1:])
            return (gg.shape[0] * a, gg.shape[1] * a)
        if k.startswith("÷"):
            a = int(k[1:])
            if gg.shape[0] % a or gg.shape[1] % a:
                return None
            return (gg.shape[0] // a, gg.shape[1] // a)
        if k == "nesne_katı":
            n = len(mm.nesneler)
            return (gg.shape[0] * n, gg.shape[1] * n) if n else None
        if k.startswith("sabit"):
            return tuple(int(x) for x in k[6:-1].split(", "))
        raise ValueError("boyut kaidesi bilinmiyor: %r" % (k,))

    if ne == "kaide":
        return kaide(ad, g, m)

    if ne == "bul":
        if not ciftler:
            return None
        mesudlar = [musahede_et(a) for a, _ in ciftler]
        for k in KAIDE_ADLARI:
            tamam = True
            for (a, b), mm in zip(ciftler, mesudlar):
                t_ = kaide(k, a, mm)
                if t_ is None or t_ != (b.shape[0], b.shape[1]):
                    tamam = False
                    break
            if tamam:
                return k
        boyutlar = {(b.shape[0], b.shape[1]) for _, b in ciftler}
        if len(boyutlar) == 1:
            sb = boyutlar.pop()
            return "sabit%s" % (sb,)
        return None

    if ne == "tahmin":
        k = cikti_ne_kadar(ciftler, ne="bul")
        if k is None:
            return None, "sükût"
        gg = np.asarray(girdi)
        return kaide(k, gg, musahede_et(gg)), k

    if ne != "ölç":
        raise ValueError("boyut kipi bilinmiyor: %r" % (ne,))
    isabet = yanlis = sukut = deneme = 0
    kaide_say: Dict[str, int] = {}
    kaide_isabet: Dict[str, int] = {}
    for gv in gorevler[:azami]:
        egt = [(np.array(a), np.array(b)) for a, b in gv.egitim
               if np.array(a).size <= azami_hucre
               and np.array(b).size <= azami_hucre]
        sin = [(np.array(a), np.array(b)) for a, b in gv.sinama
               if np.array(a).size <= azami_hucre
               and np.array(b).size <= azami_hucre]
        if len(egt) < 2 or not sin:
            continue
        deneme += 1
        gi, co = sin[0]
        t, ad = cikti_ne_kadar(egt, gi)
        kaide_say[ad] = kaide_say.get(ad, 0) + 1
        if t is None:
            sukut += 1
        elif t == (co.shape[0], co.shape[1]):
            isabet += 1
            kaide_isabet[ad] = kaide_isabet.get(ad, 0) + 1
        else:
            yanlis += 1
    return {"deneme": deneme, "isabet": isabet, "yanlış": yanlis,
            "sükût": sukut,
            "isabet_oranı": isabet / max(deneme, 1),
            "konuşunca_isabet": isabet / max(isabet + yanlis, 1),
            "kaide_dağılımı": dict(sorted(kaide_say.items(),
                                          key=lambda x: -x[1])),
            "kaide_isabeti": kaide_isabet}

