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

__all__ = ["KAIDELER", "boyut_kaidesi_bul", "boyut_tahmin", "olc"]

Boyut = Tuple[int, int]


# =====================================================================
#  Kaide dağarcığı -- her biri (girdi, müşahede) → boyut yahut None
# =====================================================================
def _ayni(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
    """Çıktı girdiyle aynı boyutta."""
    return (g.shape[0], g.shape[1])


def _devrik(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
    return (g.shape[1], g.shape[0])


def _dolu_kutu(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
    """Zemin olmayan bölgenin sınırlayıcı kutusu -- kırpma kaidesi."""
    idx = np.argwhere(g != 0)
    if not len(idx):
        return None
    a, b = idx.min(0)
    c, d = idx.max(0)
    return (int(c - a + 1), int(d - b + 1))


def _en_buyuk_nesne(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
    if not m.nesneler:
        return None
    n = m.nesneler[0]              # ızama göre sıralı
    return (n.sekil.shape[0], n.sekil.shape[1])


def _en_kucuk_nesne(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
    if not m.nesneler:
        return None
    n = m.nesneler[-1]
    return (n.sekil.shape[0], n.sekil.shape[1])


def _tek_nesne(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
    """Ötekilerden farklı olan (tek başına kalan) nesnenin kutusu.

    ARC'nin en sık kaidelerinden biri: "aykırı olanı bul ve onu ver".
    Aykırılık şekil imzasının **tekliğinden** okunur; ayrı bir sinyal
    aranmaz.
    """
    if len(m.nesneler) < 3:
        return None
    imza: Dict[bytes, List[int]] = {}
    for i, n in enumerate(m.nesneler):
        k = np.asarray(n.sekil, np.uint8).tobytes() + bytes(n.sekil.shape)
        imza.setdefault(k, []).append(i)
    tekler = [v[0] for v in imza.values() if len(v) == 1]
    if len(tekler) != 1:
        return None
    n = m.nesneler[tekler[0]]
    return (n.sekil.shape[0], n.sekil.shape[1])


def _nesne_sayisi_kare(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
    k = len(m.nesneler)
    return (k, k) if k else None


def _renk_sayisi_kare(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
    k = len(m.adet)
    return (k, k) if k else None


def _olcekli(kh: int, kw: int) -> Callable[[np.ndarray, Mesud], Optional[Boyut]]:
    def f(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
        return (g.shape[0] * kh, g.shape[1] * kw)
    return f


def _bolunmus(kh: int, kw: int) -> Callable[[np.ndarray, Mesud], Optional[Boyut]]:
    def f(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
        if g.shape[0] % kh or g.shape[1] % kw:
            return None
        return (g.shape[0] // kh, g.shape[1] // kw)
    return f


def _nesne_katı(g: np.ndarray, m: Mesud) -> Optional[Boyut]:
    """Girdi boyutunun nesne sayısı katı -- 'her nesne için bir kopya'."""
    k = len(m.nesneler)
    if k < 1 or k > 6:
        return None
    return (g.shape[0] * k, g.shape[1] * k)


#: Kaide dağarcığı. Sıra mühimdir: en dar kaide en başta denenir ki
#: "aynı boyut" gibi geniş bir kaide daha keskin olanı gölgelemesin.
KAIDELER: List[Tuple[str, Callable[[np.ndarray, Mesud], Optional[Boyut]]]] = [
    ("aynı", _ayni),
    ("devrik", _devrik),
    ("dolu_kutu", _dolu_kutu),
    ("en_büyük_nesne", _en_buyuk_nesne),
    ("en_küçük_nesne", _en_kucuk_nesne),
    ("tek_nesne", _tek_nesne),
    ("nesne_sayısı_kare", _nesne_sayisi_kare),
    ("renk_sayısı_kare", _renk_sayisi_kare),
    ("nesne_katı", _nesne_katı),
]
for _kh in (2, 3, 4):
    KAIDELER.append(("×%d" % _kh, _olcekli(_kh, _kh)))
    KAIDELER.append(("÷%d" % _kh, _bolunmus(_kh, _kh)))
KAIDELER.append(("×2 yatay", _olcekli(1, 2)))
KAIDELER.append(("×2 dikey", _olcekli(2, 1)))


# =====================================================================
def boyut_kaidesi_bul(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]]
                      ) -> Optional[Tuple[str, Callable]]:
    """Eğitim çiftlerinin **hepsini** sağlayan ilk kaide.

    Hepsini sağlaması şarttır: tek karşı örnek küllî kaideyi düşürür
    (kütük H6 -- nakz). Bir kaide dokuz çiftin sekizinde tutuyorsa
    **kabul edilmez**; o, kaide değil tesadüftür.

    Sabit boyut kaidesi ayrıca denenir: bütün çıktılar aynı boyutta ise
    o boyut ezberlenebilir. Bu bir kaide değil **ezberdir** ve öyle
    işaretlenir; yine de ARC'de meşru bir kaidedir (bazı görevlerde çıktı
    hep 3×3'tür).
    """
    if not ciftler:
        return None
    mesudlar = [musahede_et(a) for a, _ in ciftler]

    for ad, f in KAIDELER:
        tamam = True
        for (a, b), m in zip(ciftler, mesudlar):
            t = f(np.asarray(a), m)
            if t is None or t != (b.shape[0], b.shape[1]):
                tamam = False
                break
        if tamam:
            return ad, f

    # sabit boyut (ezber)
    boyutlar = {(b.shape[0], b.shape[1]) for _, b in ciftler}
    if len(boyutlar) == 1:
        sabit = boyutlar.pop()

        def g_(g: np.ndarray, m: Mesud, s=sabit) -> Optional[Boyut]:
            return s
        return "sabit%s" % (sabit,), g_
    return None


def boyut_tahmin(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]],
                 girdi: np.ndarray) -> Tuple[Optional[Boyut], str]:
    """Kaideyi eğitimden çıkar, test girdisine tatbik et.

    Kaide bulunamazsa ``(None, "sükût")`` döner -- model **susar**.
    Uydurma bir boyut vermek, bilmediğini söylememekten kötüdür (H10).
    """
    k = boyut_kaidesi_bul(ciftler)
    if k is None:
        return None, "sükût"
    ad, f = k
    t = f(np.asarray(girdi), musahede_et(np.asarray(girdi)))
    return (t, ad) if t is not None else (None, "sükût")


def olc(gorevler: Sequence, azami: int = 400,
        azami_hucre: int = 1600) -> Dict[str, object]:
    """**Ara ölçüt**: kaç görevde çıktı boyutu doğru tahmin edildi.

    Üç sayı ayrı ayrı raporlanır ve karıştırılmaz:

    * ``isabet``     -- doğru tahmin sayısı.
    * ``yanlış``     -- kaide bulundu fakat tahmin tuttu**ma**dı.
    * ``sükût``      -- hiçbir kaide bütün eğitim çiftlerini sağlamadı.

    Sükût bir başarısızlık değildir; **cehli îlan etmektir** ve yanlış
    tahminden ayrı sayılır (H10). Fakat sükût oranı yüksekse dağarcığın
    dar olduğunu söyler ve bu da bir hükümdür.
    """
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
        t, ad = boyut_tahmin(egt, gi)
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
