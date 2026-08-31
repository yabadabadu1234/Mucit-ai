"""
TAMAMLAMA KATMANI -- boş yere **ekleyen** kaideler.

===================================================================
NİÇİN BU AİLE: SAYILDI
===================================================================

`nefs/kaideler.py` (bütün ızgara), `nefs/nesne.py` (nesne başına) ve
`nefs/hucre.py` (yerel bağlam) kuruldu. Çözülemeyen 108 görev
**tasnif edildi** -- tahminle değil, değişen hücreleri sayarak::

    aynı şekilli, ağırlıklı EKLEME (arka plan → renk)   48
    aynı şekilli, ağırlıklı BOYAMA (renk → renk)        22
    aynı şekilli, ağırlıklı SİLME  (renk → arka plan)   10
    gerçek ayraç çizgisi olan                           13

Yani en büyük tek küme, **boş yere bir şey ekleyen** görevlerdir ve
mevcut üç katmanın hiçbiri o işi cinsen yapmıyordu: biri ızgarayı
bütün olarak çeviriyor, biri nesneyi boyuyor/siliyor, biri hücreyi
komşusuna bakarak değiştiriyor. Hiçbiri *"burada olması gereken ama
olmayan şeyi koy"* demiyordu.

Bu dosyanın tamamı o cümledir. Beş aile:

1. **bakışım_tamamla** -- ızgara bir bakışıma uyuyor fakat bir yeri
   boş. Boşluk, bakışımın kendisinden doldurulur.
2. **bölge_doldur** -- kenara değmeyen kapalı boşluklar bir renge
   boyanır; renk bölgenin bir vasfından öğrenilir.
3. **kutu_doldur** -- her nesnenin çerçeve kutusu doldurulur.
4. **ışın_uzat** -- her nesne kendi doğrultusunda engele/kenara kadar
   uzatılır.
5. **damga** -- bir şablon nesne, işaret hücrelerinin üstüne basılır.

===================================================================
EZBER TEDBİRİ
===================================================================

Bu ailelerin bir kısmı **parametresiz**dir (bakışım, kutu, ışın):
``hipotez = 0``, yani öğrenilmiş tablo yoktur, ezberleyemezler.
Öğrenilen kısım (bölge rengi, damga şablonu) ``hipotez``i doğru
bildirir ve `nefs/kaideler.py`nin ``capraz_gecerli`` kapısından --
bırak-birini istikrâsı -- geçmek zorundadır. O kapı kurulmadan bu
dosya yazılamazdı: aile genişletmek, kapı olmadan isabeti düşürür.
Sıra tesadüf değildir: **evvela ölçüt, sonra genişleme.**
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from idrak.cozucu import _bilesenler
from .kaideler import ARKA, Kaide

__all__ = ["BAKISIMLAR", "bakisimlar_tutan", "tamamlama_kaideleri"]

Izgara = np.ndarray


# ===================================================================
#  1. BAKIŞIM TAMAMLAMA
# ===================================================================
#
# Bakışım, ızgaranın **kendi üstüne** bir eşlemesidir. Kare olmayan
# ızgarada devrik tanımsızdır; o yüzden her bakışım kendi şartını
# taşır ve şart tutmuyorsa aile o bakışımı hiç denemez.
BAKISIMLAR: Dict[str, object] = {
    "yatay": lambda g: g[:, ::-1],
    "dikey": lambda g: g[::-1, :],
    "yarım_devir": lambda g: g[::-1, ::-1],
    "devrik": lambda g: g.T,
    "ters_devrik": lambda g: g[::-1, ::-1].T,
}


def _kare_ister(ad: str) -> bool:
    return ad in ("devrik", "ters_devrik")


def bakisimlar_tutan(g: Izgara, arka: int = ARKA) -> List[str]:
    """``g``nin **dolu** kısmında hangi bakışımlar çelişmiyor?

    Ölçüt "eşit" değil "**çelişmiyor**"dur ve fark burada bütün
    meseledir: tamamlanacak ızgara zaten tam bakışımlı değildir --
    öyle olsaydı doldurulacak bir şey kalmazdı. Aranan şey, iki
    tarafın da dolu olduğu her yerde uyuşmalarıdır. Boşluk delil
    saymaz; delil sayılsaydı hiçbir bakışım tutmazdı.
    """
    out: List[str] = []
    for ad, f in BAKISIMLAR.items():
        if _kare_ister(ad) and g.shape[0] != g.shape[1]:
            continue
        h = np.asarray(f(g))
        if h.shape != g.shape:
            continue
        ikisi_dolu = (g != arka) & (h != arka)
        if not ikisi_dolu.any():
            continue
        if np.array_equal(g[ikisi_dolu], h[ikisi_dolu]):
            out.append(ad)
    return out


def _bakisim_tamamla(g: Izgara, adlar: Sequence[str],
                     arka: int = ARKA) -> Optional[Izgara]:
    """Boş hücreleri bakışımın gösterdiği renkle doldur.

    Birden fazla bakışım tuttuğunda sırayla tatbik edilir ve
    **yakınsayana kadar** tekrarlanır: yatay ile dikeyin bileşkesi
    yarım devri de doğurur, bir geçiş onu yakalamaz.
    """
    out = np.asarray(g, np.int64).copy()
    for _ in range(4):
        onceki = out.copy()
        for ad in adlar:
            f = BAKISIMLAR[ad]
            if _kare_ister(ad) and out.shape[0] != out.shape[1]:
                continue
            h = np.asarray(f(out))
            if h.shape != out.shape:
                continue
            bos = (out == arka) & (h != arka)
            out[bos] = h[bos]
        if np.array_equal(out, onceki):
            break
    return out


def _bakisim_kaideleri(ciftler: Sequence[Tuple[Izgara, Izgara]]
                       ) -> List[Kaide]:
    """Bakışım tamamlaması iki şekilde: **otomatik** ve **sabit**.

    Otomatik olan, her girdide bakışımı yeniden ölçer; sabit olan,
    gösterimlerin hepsinde ortak olan bakışım kümesini kullanır.
    İkisi de parametresizdir (``hipotez=0``) çünkü hiçbir tablo
    öğrenilmez: ölçülen şey girdinin kendi yapısıdır.
    """
    out: List[Kaide] = []

    def otomatik(g: Izgara) -> Optional[Izgara]:
        adlar = bakisimlar_tutan(g)
        if not adlar:
            return None
        return _bakisim_tamamla(g, adlar)

    out.append(Kaide("bakışım_tamamla[oto]", otomatik))

    ortak: Optional[Set[str]] = None
    for a, _ in ciftler:
        s = set(bakisimlar_tutan(np.asarray(a)))
        ortak = s if ortak is None else (ortak & s)
    if ortak:
        ad = ",".join(sorted(ortak))
        out.append(Kaide("bakışım_tamamla[%s]" % ad,
                         lambda g, s=tuple(sorted(ortak)):
                         _bakisim_tamamla(g, s)))
    return out


# ===================================================================
#  2. KAPALI BÖLGE DOLDURMA
# ===================================================================
def _kapali_bolgeler(g: Izgara, arka: int = ARKA
                     ) -> List[np.ndarray]:
    """Kenara **değmeyen** arka plan bileşenleri: içerideki boşluklar.

    Kenara değen boşluk "dışarısı"dır; onu doldurmak bütün ızgarayı
    boyamak olurdu. Ayrım topolojiktir ve keyfî değildir.
    """
    R, C = g.shape
    bos = (g == arka)
    etiket = np.full((R, C), -1, np.int64)
    bolgeler: List[np.ndarray] = []
    for i in range(R):
        for j in range(C):
            if not bos[i, j] or etiket[i, j] >= 0:
                continue
            yigin = [(i, j)]
            etiket[i, j] = len(bolgeler)
            hucreler = []
            kenarda = False
            while yigin:
                y, x = yigin.pop()
                hucreler.append((y, x))
                if y in (0, R - 1) or x in (0, C - 1):
                    kenarda = True
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    v, u = y + dy, x + dx
                    if 0 <= v < R and 0 <= u < C and bos[v, u] \
                            and etiket[v, u] < 0:
                        etiket[v, u] = len(bolgeler)
                        yigin.append((v, u))
            m = np.zeros((R, C), bool)
            for y, x in hucreler:
                m[y, x] = True
            bolgeler.append(m if not kenarda else np.zeros((R, C), bool))
    return [b for b in bolgeler if b.any()]


#: Bölgenin hangi cihetine bakılarak renk seçilecek.
BOLGE_VASIFLARI: Dict[str, object] = {
    "sabit": lambda m, g: 0,
    "büyüklük": lambda m, g: int(m.sum()),
    "çevre_rengi": lambda m, g: _cevre_rengi(m, g),
    "en×boy": lambda m, g: _kutu_olcusu(m),
}


def _kutu_olcusu(m: np.ndarray) -> Tuple[int, int]:
    r, c = np.where(m)
    return (int(r.max() - r.min() + 1), int(c.max() - c.min() + 1))


def _cevre_rengi(m: np.ndarray, g: Izgara) -> int:
    """Bölgeyi çevreleyen renk tek ise odur, değilse ``-1``."""
    R, C = g.shape
    renkler: Set[int] = set()
    r, c = np.where(m)
    for y, x in zip(r.tolist(), c.tolist()):
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v, u = y + dy, x + dx
            if 0 <= v < R and 0 <= u < C and not m[v, u]:
                renkler.add(int(g[v, u]))
    return int(next(iter(renkler))) if len(renkler) == 1 else -1


def _bolge_ogren(ciftler: Sequence[Tuple[Izgara, Izgara]],
                 vasif: str) -> Optional[Dict[object, int]]:
    f: Dict[object, int] = {}
    gordu = False
    for a, b in ciftler:
        a = np.asarray(a)
        b = np.asarray(b)
        if a.shape != b.shape:
            return None
        bolgeler = _kapali_bolgeler(a)
        if not bolgeler:
            return None
        doldurulan = np.zeros(a.shape, bool)
        for m in bolgeler:
            renkler = {int(v) for v in b[m]}
            if len(renkler) != 1:
                return None
            hedef = int(next(iter(renkler)))
            anahtar = BOLGE_VASIFLARI[vasif](m, a)
            if anahtar in f and f[anahtar] != hedef:
                return None
            f[anahtar] = hedef
            doldurulan |= m
            gordu = True
        # bölge dışında hiçbir şey değişmemeli: aksi hâlde kaide bu değil
        if not np.array_equal(a[~doldurulan], b[~doldurulan]):
            return None
    return f if gordu else None


def _bolge_doldur(g: Izgara, vasif: str, f: Dict[object, int],
                  aynen: bool = False) -> Optional[Izgara]:
    """``aynen=True``: vasfını bilmediğim bölgeye dokunmam.

    İki sükût ayrımı için bkz. `nefs/hucre.py`nin ``_tatbik`` şerhi.
    """
    g = np.asarray(g, np.int64)
    bolgeler = _kapali_bolgeler(g)
    if not bolgeler:
        return None
    out = g.copy()
    for m in bolgeler:
        anahtar = BOLGE_VASIFLARI[vasif](m, g)
        if anahtar not in f:
            if aynen:
                continue
            return None            # görülmemiş bölge: istikrâ yetmez
        out[m] = f[anahtar]
    return out


# ===================================================================
#  3. KUTU DOLDURMA
# ===================================================================
def _kutu_doldur(g: Izgara) -> Optional[Izgara]:
    g = np.asarray(g, np.int64)
    ns = _bilesenler(g, ARKA)
    if not ns:
        return None
    out = g.copy()
    for renk, _m, (r0, r1, c0, c1) in ns:
        out[r0:r1 + 1, c0:c1 + 1] = int(renk)
    return out


# ===================================================================
#  4. IŞIN UZATMA -- engele kadar
# ===================================================================
YONLER: Dict[str, Tuple[Tuple[int, int], ...]] = {
    "dört": ((1, 0), (-1, 0), (0, 1), (0, -1)),
    "sekiz": ((1, 0), (-1, 0), (0, 1), (0, -1),
              (1, 1), (1, -1), (-1, 1), (-1, -1)),
    "yatay": ((0, 1), (0, -1)),
    "dikey": ((1, 0), (-1, 0)),
    "çapraz": ((1, 1), (1, -1), (-1, 1), (-1, -1)),
}


def _isin_uzat(g: Izgara, yon: str, engelde_dur: bool
               ) -> Optional[Izgara]:
    """Her dolu hücreden ışın çıkar; kenara ya da **engele** kadar.

    ``engelde_dur`` ayrımı manevîdir: ışık bir cisme çarpınca durur mu
    yoksa içinden geçer mi? İkisi de ARC'de görülür, ikisi de sınanır,
    hangisinin doğru olduğuna gösterimler karar verir.
    """
    g = np.asarray(g, np.int64)
    R, C = g.shape
    kaynak = np.argwhere(g != ARKA)
    if kaynak.size == 0 or len(kaynak) > 400:
        return None
    out = g.copy()
    for y, x in kaynak.tolist():
        renk = int(g[y, x])
        for dy, dx in YONLER[yon]:
            v, u = y + dy, x + dx
            while 0 <= v < R and 0 <= u < C:
                if g[v, u] != ARKA:
                    if engelde_dur:
                        break
                else:
                    out[v, u] = renk
                v += dy
                u += dx
    return out


# ===================================================================
#  5. DAMGA -- şablonu işaretlerin üstüne bas
# ===================================================================
def _damga_ogren(ciftler: Sequence[Tuple[Izgara, Izgara]]
                 ) -> Optional[np.ndarray]:
    """En büyük nesne şablon, tek hücrelikler işaret midir?

    Şablon gösterimlerin hepsinde **aynı** olmalıdır; değişiyorsa bu
    aile değildir ve zorlanmaz.
    """
    sablon: Optional[np.ndarray] = None
    for a, b in ciftler:
        a = np.asarray(a)
        if a.shape != np.asarray(b).shape:
            return None
        ns = _bilesenler(a, ARKA)
        if len(ns) < 2:
            return None
        buyuk = max(ns, key=lambda t: int(t[1].sum()))
        r0, r1, c0, c1 = buyuk[2]
        kes = a[r0:r1 + 1, c0:c1 + 1]
        if int(buyuk[1].sum()) <= 1:
            return None
        if sablon is None:
            sablon = kes.copy()
        elif sablon.shape != kes.shape or not np.array_equal(sablon, kes):
            return None
    return sablon


def _damga_bas(g: Izgara, sablon: np.ndarray) -> Optional[Izgara]:
    g = np.asarray(g, np.int64)
    R, C = g.shape
    h, w = sablon.shape
    ns = _bilesenler(g, ARKA)
    tekler = [n for n in ns if int(n[1].sum()) == 1]
    if not tekler:
        return None
    out = g.copy()
    for _renk, m, _k in tekler:
        y, x = [int(t[0]) for t in np.where(m)]
        i0, j0 = y - h // 2, x - w // 2
        for i in range(h):
            for j in range(w):
                v, u = i0 + i, j0 + j
                if 0 <= v < R and 0 <= u < C and sablon[i, j] != ARKA:
                    out[v, u] = int(sablon[i, j])
    return out


# ===================================================================
#  TOPLAYICI
# ===================================================================
def tamamlama_kaideleri(ciftler: Sequence[Tuple[Izgara, Izgara]]
                        ) -> List[Kaide]:
    """Beş ailenin hepsi; öğrenilenler ``hipotez``ini doğru bildirir."""
    out: List[Kaide] = []
    try:
        out += _bakisim_kaideleri(ciftler)
    except Exception:                                    # noqa: BLE001
        pass

    for vasif in BOLGE_VASIFLARI:
        try:
            f = _bolge_ogren(ciftler, vasif)
        except Exception:                                # noqa: BLE001
            f = None
        if f:
            out.append(Kaide("bölge_doldur[%s]" % vasif,
                             lambda g, v=vasif, m=f: _bolge_doldur(g, v, m),
                             1, len(f)))
            out.append(Kaide("bölge_doldur[%s|aynen]" % vasif,
                             lambda g, v=vasif, m=f:
                             _bolge_doldur(g, v, m, True),
                             1, len(f)))

    out.append(Kaide("kutu_doldur", _kutu_doldur))

    for yon in YONLER:
        for dur in (True, False):
            out.append(Kaide("ışın_uzat[%s%s]"
                             % (yon, "|engelde_dur" if dur else ""),
                             lambda g, y=yon, d=dur: _isin_uzat(g, y, d)))

    try:
        s = _damga_ogren(ciftler)
    except Exception:                                    # noqa: BLE001
        s = None
    if s is not None:
        out.append(Kaide("damga[%dx%d]" % s.shape,
                         lambda g, t=s: _damga_bas(g, t),
                         1, int(s.size)))
    return out
