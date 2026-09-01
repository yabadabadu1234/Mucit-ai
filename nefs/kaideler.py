"""
KÂİDE CEBRİ -- atomik ızgara dönüşümleri ve **terkipleri**.

===================================================================
NİÇİN: TEK ATOM YETMİYOR, ÖLÇÜLDÜ
===================================================================

`idrak/cozucu.py` ispatlı bir çözücüdür ve doğru kurulmuştur: ya
gösterim çiftlerinin **hepsini** tutan bir kaide bulur ya susar.
Cevap verdiğinde isabeti **%100**. Fakat ölçüldü::

    training  (ilk 120) : 5/120 çözüldü, 115 sükût
    evaluation (120)    : 0/120 çözüldü, 120 sükût

Sebep aday listesinin darlığı değil, **cinsi**dir: her aday **tek bir
atomik dönüşümdür**. ARC-AGI-2 görevleri ise nadiren tek atomdur;
"önce kırp, sonra döndür, sonra rengi eşle" gibi **terkiplerdir**.

Ve terkip bu mimarînin zaten merkezinde duruyor: Dosya 3'ün ∞-operad
teklifi tam olarak *"atomların iyi tipli terkibi"*dir (kütük H125).
Orada 41 melekenin terkibi tip denetiminden geçirilmişti; burada aynı
fikir ARC kaidelerine tatbik edilir.

===================================================================
CEBRİN ŞEKLİ
===================================================================

Bir **kâide** ``ızgara → ızgara | None`` fonksiyonudur. ``None``
"tatbik edilemez" demektir ve sessizce yutulmaz -- terkipte de yayılır.

    Atom      : tek dönüşüm (D₄, kırpma, yerçekimi, örtüşme…)
    Terkip    : ``k₂ ∘ k₁`` -- soldan sağa uygulanır
    Doğrulama : bütün gösterim çiftlerinde **tam** eşleşme

Arama derinliği ``d`` iken uzay ``|A|^d``dir; budama şarttır ve iki
usulle yapılır:

1. **Erken ret** -- ilk çiftte tutmayan terkip hiç açılmaz.
2. **Ara hâl imzası** -- aynı ara ızgarayı veren iki farklı yol
   birleştirilir (tekrarlı iş yapılmaz).

===================================================================
OCCAM ve ÇOKLUK
===================================================================

Birden fazla kaide gösterimlerin hepsini tutabilir. `idrak/cozucu.py`
bu hâlde ``tutan[0]``ı, yani **listedeki ilkini** alıyordu -- keyfî bir
tercih. Burada iki şey yapılır:

* **Occam**: en kısa terkip tercih edilir (atom sayısı, sonra ad).
* **Çokluk ölçülür**: tutan kaideler sınama girdisinde **ayrı cevaplar**
  veriyorsa bu bir müphemliktir ve yakîni düşürür (`nefs/mudrike.py`).

İkincisi mühimdir: gösterimleri tutan iki kaide farklı cevap veriyorsa,
gösterimler kaideyi **tayin etmiyor** demektir ve o hâlde emin olmak
mesnetsizdir.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from idrak.cozucu import D4, _bilesenler, d4_uygula

__all__ = ["Kaide", "atomlar", "terkipler", "kaide_ara", "ARKA"]

#: Arka plan rengi -- ARC'de ezici çoğunlukla 0.
ARKA = 0

Izgara = np.ndarray


@dataclass
class Kaide:
    """Bir ızgara dönüşümü: ad + uygulayıcı + kaç atomdan kurulu.

    ``hipotez`` -- kaidenin **taşıdığı serbest bilgi**: öğrenilen bir
    tablonun girdi sayısı. Sabit bir dönüşümde (döndür, kırp) sıfırdır;
    gösterimlerden öğrenilen bir eşlemede tablonun boyudur.

    **Niçin lazım (kütük H134).** Hücre kaideleri eklendiğinde model
    7 görevden 16'ya çıkıp konuştu, fakat 8'i **yanlış** oldu: isabet
    %85,7'den %50'ye düştü. Sebep ezberdir -- 3×3 desen tablosu üç
    gösterimden öğrenilince gösterimleri tutar, sınamayı tutmaz.
    Delilden büyük hipotez, istikrâ değil ezberdir; ``hipotez`` o
    orantıyı ölçülebilir kılar ve yakîni düşürür.
    """
    ad: str
    uygula: Callable[[Izgara], Optional[Izgara]]
    boy: int = 1
    hipotez: int = 0

    def __call__(self, g: Izgara) -> Optional[Izgara]:
        try:
            r = self.uygula(g)
        except Exception:                                # noqa: BLE001
            return None
        if r is None:
            return None
        r = np.asarray(r)
        if r.ndim != 2 or r.size == 0 or r.size > 3600:
            return None
        return np.ascontiguousarray(r.astype(np.int64))


# =====================================================================
#  Atomik dönüşümler
# =====================================================================
def _kirp_dolu(g: Izgara) -> Optional[Izgara]:
    nz = np.argwhere(g != ARKA)
    if nz.size == 0:
        return None
    (r0, c0), (r1, c1) = nz.min(0), nz.max(0)
    return g[r0:r1 + 1, c0:c1 + 1]


def _cerceve_soy(g: Izgara) -> Optional[Izgara]:
    """Bir hücrelik dış çerçeveyi at."""
    if g.shape[0] < 3 or g.shape[1] < 3:
        return None
    return g[1:-1, 1:-1]


def _en_sik_renk(g: Izgara) -> int:
    v, s = np.unique(g, return_counts=True)
    return int(v[int(np.argmax(s))])


def _arka_sifirla(g: Izgara) -> Optional[Izgara]:
    """En sık rengi arka plana (0) çevir."""
    r = _en_sik_renk(g)
    if r == ARKA:
        return None
    return np.where(g == r, ARKA, g)


def _nesne(g: Izgara, olcut: str) -> Optional[Izgara]:
    b = _bilesenler(g, ARKA)
    if not b:
        return None
    if olcut == "en_buyuk":
        sec = max(b, key=lambda x: int(x[1].sum()))
    elif olcut == "en_kucuk":
        sec = min(b, key=lambda x: int(x[1].sum()))
    elif olcut == "tek_renk":
        say: Dict[int, int] = {}
        for r, _m, _k in b:
            say[r] = say.get(r, 0) + 1
        tek = [x for x in b if say[x[0]] == 1]
        if len(tek) != 1:
            return None
        sec = tek[0]
    elif olcut == "en_cok_delik":
        # deliği en çok olan bileşen: kutu alanı − hücre sayısı
        def delik(x):
            r0, r1, c0, c1 = x[2]
            return (r1 - r0 + 1) * (c1 - c0 + 1) - int(x[1].sum())
        sec = max(b, key=delik)
    else:
        return None
    r0, r1, c0, c1 = sec[2]
    return g[r0:r1 + 1, c0:c1 + 1]


def _yercekimi(g: Izgara, yon: str) -> Izgara:
    out = np.full_like(g, ARKA)
    if yon in ("asagi", "yukari"):
        for j in range(g.shape[1]):
            s = [v for v in g[:, j] if v != ARKA]
            if yon == "asagi":
                out[g.shape[0] - len(s):, j] = s
            else:
                out[:len(s), j] = s
    else:
        for i in range(g.shape[0]):
            s = [v for v in g[i] if v != ARKA]
            if yon == "saga":
                out[i, g.shape[1] - len(s):] = s
            else:
                out[i, :len(s)] = s
    return out


def _bakisim_onar(g: Izgara, delik: int) -> Optional[Izgara]:
    if not (g == delik).any():
        return None
    out = g.copy()
    for don in (np.fliplr, np.flipud, lambda x: np.rot90(x, 2)):
        ayna = don(out)
        yaz = (out == delik) & (ayna != delik)
        out = np.where(yaz, ayna, out)
    return None if (out == delik).any() else out


def _bol(g: Izgara, eksen: int) -> Optional[Tuple[Izgara, Izgara]]:
    """Izgarayı ikiye böl -- ayırıcı çizgi varsa onu atarak.

    ARC'de çok sık: iki yarım bir mantık işlemiyle üst üste bindirilir.
    """
    n = g.shape[eksen]
    if n % 2 == 0:
        k = n // 2
        a = g[:k] if eksen == 0 else g[:, :k]
        b = g[k:] if eksen == 0 else g[:, k:]
        return a, b
    # tek sayı: ortada ayırıcı çizgi olmalı ve tek renk olmalı
    k = n // 2
    orta = g[k] if eksen == 0 else g[:, k]
    if len(np.unique(orta)) != 1:
        return None
    a = g[:k] if eksen == 0 else g[:, :k]
    b = g[k + 1:] if eksen == 0 else g[:, k + 1:]
    return a, b


def _ortusme(g: Izgara, eksen: int, islem: str,
             renk: int) -> Optional[Izgara]:
    """İki yarımı mantık işlemiyle birleştir."""
    p = _bol(g, eksen)
    if p is None:
        return None
    a, b = p
    if a.shape != b.shape or a.size == 0:
        return None
    A, B = a != ARKA, b != ARKA
    if islem == "ve":
        m = A & B
    elif islem == "veya":
        m = A | B
    elif islem == "xor":
        m = A ^ B
    elif islem == "fark":
        m = A & ~B
    else:
        return None
    return np.where(m, renk, ARKA)


def _kucult(g: Izgara, p: int, q: int) -> Optional[Izgara]:
    """``p×q`` blokları tek hücreye indir -- blok tek renkliyse."""
    h, w = g.shape
    if p < 1 or q < 1 or h % p or w % q:
        return None
    out = np.zeros((h // p, w // q), dtype=np.int64)
    for i in range(h // p):
        for j in range(w // q):
            blok = g[i * p:(i + 1) * p, j * q:(j + 1) * q]
            v = np.unique(blok)
            if v.size != 1:
                return None
            out[i, j] = int(v[0])
    return out


def _tekrari_sil(g: Izgara, eksen: int) -> Optional[Izgara]:
    """Ardışık aynı satır/sütunları teke indir (sıkıştırma)."""
    if eksen == 0:
        tut = [0] + [i for i in range(1, g.shape[0])
                     if not np.array_equal(g[i], g[i - 1])]
        return g[tut]
    tut = [0] + [j for j in range(1, g.shape[1])
                 if not np.array_equal(g[:, j], g[:, j - 1])]
    return g[:, tut]


def ogrenilen_aileler(ciftler: Sequence[Tuple[Izgara, Izgara]]
                      ) -> List[Kaide]:
    """Veriden **öğrenilen** kaideler: nesne ve hücre aileleri.

    Ayrı bir fonksiyon olması şart: çapraz sınama bunları **her katta
    yeniden öğrenmek** zorundadır, yoksa ölçüm kendi cevabını görür.
    """
    # İçe aktarma **açıkça** yazılır, ``__import__`` ile değil: aksi
    # hâlde `tanilama/nizam.py`nin ``ast`` taraması bu bağı göremez ve
    # dosyalar beylik görünür. Fiilen koşuyor olmaları bunu düzeltmez --
    # ölçüyü kör bırakan bir bağ, bağ sayılmamalıdır.
    from .hucre import hucre_kaideleri
    from .nesne import nesne_kaideleri
    from .secici import carpim_kaideleri
    from .tamamlama import tamamlama_kaideleri

    out: List[Kaide] = []
    for f in (nesne_kaideleri, hucre_kaideleri, tamamlama_kaideleri,
              carpim_kaideleri):
        try:
            out += list(f(ciftler))
        except Exception:                                # noqa: BLE001
            pass
    return out


def capraz_gecerli(ciftler: Sequence[Tuple[Izgara, Izgara]]) -> Set[str]:
    """**Bırak-birini istikrâsı**: hangi öğrenilen kaide adı genelliyor?

    ===================================================================
    NİÇİN: GÖSTERİMLERE TAM UYMAK DELİL DEĞİLDİR
    ===================================================================

    Ölçüldü (ARC-AGI-2 eğitim, ilk 120): ``0ca9ddb6`` ve ``025d127b``
    görevlerinde ``hücre[3x3]`` kaidesi **bütün gösterimlere tam
    uyuyor** -- hücre isabeti ``1.000`` -- fakat sınama girdisinde
    ``None`` dönüyor. Sebebi basittir ve utanç verici değil, ölçülmüş
    bir hakikattir: o kaide bir kaide değil, bir **arama tablosu**dur.
    Bağlam sayısı hücre sayısı mertebesinde olduğu için tabloyu
    ezberlemek gösterimleri tam açıklar ve hiçbir şey öğretmez.

    Demek ki "bütün gösterimlere uyuyor" ölçütü, tablo büyüklüğü veriye
    yaklaştıkça **boşalır**. `nefs/kaideler.py`nin ``hipotez`` cezası
    bunu yumuşatıyordu fakat kesmiyordu; ölçüldü.

    Doğru ölçüt `mizan/istikra.py`nin kendi hükmüdür: *eksik istikrâ
    yakîn vermez.* Bir tümevarımın delili, **görmediği** bir ferde
    doğru hükmetmesidir. Onun için:

        her gösterim çifti sırayla dışarıda bırakılır,
        kaide **kalanlardan yeniden öğrenilir**,
        dışarıda bırakılana tam bilebiliyorsa geçer.

    Bu, ezberi yapısal olarak eler: tablo, görmediği bağlamda ``None``
    döner ve kat düşer. Aynı zamanda **aileyi genişletmeyi serbest
    bırakır** -- yeni aile eklemek artık isabeti düşürme riski
    taşımaz, çünkü ezberleyen aile bu kapıdan geçemez.

    HUDUT: iki gösterimden az olan görevde kat kurulamaz; orada ölçüm
    yapılamadığı için kaide **elenmez**, ``hipotez`` cezasına bırakılır.
    Bu bir gevşeklik değil, ölçülemeyeni ölçtüm dememektir.
    """
    n = len(ciftler)
    if n < 3:
        return set()          # kat kurulamıyor: eleme yapma, karar yok
    gecti: Dict[str, int] = {}
    for i in range(n):
        kalan = [c for j, c in enumerate(ciftler) if j != i]
        a, b = ciftler[i]
        b = np.asarray(b)
        for k in ogrenilen_aileler(kalan):
            o = k(a)
            if o is not None and o.shape == b.shape and np.array_equal(o, b):
                gecti[k.ad] = gecti.get(k.ad, 0) + 1
    return {ad for ad, c in gecti.items() if c == n}


def atomlar(ciftler: Sequence[Tuple[Izgara, Izgara]]) -> List[Kaide]:
    """Görevden **türetilen** atomik kaideler.

    Bir kısmı görevden bağımsızdır (D₄, yerçekimi); bir kısmı görevin
    kendi ölçüsünden çıkar (renk eşlemesi, döşeme katı, delik rengi).
    İkincisi kör arama değildir: gösterimlerin ölçülmüş yapısıdır.
    """
    A: List[Kaide] = []

    # --- görevden bağımsız
    for ad in D4:
        A.append(Kaide("D4:" + ad, lambda g, a=ad: d4_uygula(g, a)))
    A.append(Kaide("kırp", _kirp_dolu))
    A.append(Kaide("çerçeve_soy", _cerceve_soy))
    A.append(Kaide("arka_sıfırla", _arka_sifirla))
    for o in ("en_buyuk", "en_kucuk", "tek_renk", "en_cok_delik"):
        A.append(Kaide("nesne:" + o, lambda g, x=o: _nesne(g, x)))
    for y in ("asagi", "yukari", "saga", "sola"):
        A.append(Kaide("yerçekimi:" + y, lambda g, x=y: _yercekimi(g, x)))
    for e in (0, 1):
        A.append(Kaide("tekrar_sil:%d" % e,
                       lambda g, x=e: _tekrari_sil(g, x)))

    # --- örtüşme: renk, çiftlerin çıktısından alınır (kör değil)
    cikti_renkleri: Set[int] = set()
    for _a, b in ciftler:
        cikti_renkleri |= {int(v) for v in np.unique(b) if int(v) != ARKA}
    for e in (0, 1):
        for islem in ("ve", "veya", "xor", "fark"):
            for r in sorted(cikti_renkleri)[:4]:
                A.append(Kaide("örtüşme:%d:%s:%d" % (e, islem, r),
                               lambda g, x=e, i=islem, c=r:
                               _ortusme(g, x, i, c)))

    # --- renk eşlemesi (şekil koruyan)
    f: Dict[int, int] = {}
    tutarli = True
    for a, b in ciftler:
        if a.shape != b.shape:
            tutarli = False
            break
        for x, y in zip(a.reshape(-1), b.reshape(-1)):
            x, y = int(x), int(y)
            if x in f and f[x] != y:
                tutarli = False
                break
            f[x] = y
        if not tutarli:
            break
    if tutarli and f:
        pal = np.arange(10)
        for k, v in f.items():
            if 0 <= k < 10:
                pal[k] = v
        A.append(Kaide("renk_eşlemesi",
                       lambda g, p=pal: p[np.clip(g, 0, 9)]))

    # --- döşeme / ölçekleme katı: çiftlerin şekillerinden
    katlar: Set[Tuple[int, int]] = set()
    kucultme: Set[Tuple[int, int]] = set()
    for a, b in ciftler:
        if a.shape[0] and a.shape[1]:
            if b.shape[0] % a.shape[0] == 0 and b.shape[1] % a.shape[1] == 0:
                katlar.add((b.shape[0] // a.shape[0],
                            b.shape[1] // a.shape[1]))
            if a.shape[0] % b.shape[0] == 0 and a.shape[1] % b.shape[1] == 0:
                kucultme.add((a.shape[0] // b.shape[0],
                              a.shape[1] // b.shape[1]))
    for p, q in sorted(katlar):
        if (p, q) == (1, 1) or p > 6 or q > 6:
            continue
        A.append(Kaide("döşe_%dx%d" % (p, q),
                       lambda g, x=p, y=q: np.tile(g, (x, y))))
        A.append(Kaide("ölçek_%dx%d" % (p, q),
                       lambda g, x=p, y=q: np.kron(
                           g, np.ones((x, y), dtype=np.int64))))

        def aynali(g, x=p, y=q):
            sat = []
            for i in range(x):
                par = [g if (i + j) % 2 == 0 else np.fliplr(g)
                       for j in range(y)]
                s = np.hstack(par)
                sat.append(s if i % 2 == 0 else np.flipud(s))
            return np.vstack(sat)

        A.append(Kaide("aynalı_döşe_%dx%d" % (p, q), aynali))

        def fraktal(g, x=p, y=q):
            h, w = g.shape
            if (x, y) != (h, w):
                return None
            o = np.zeros((h * x, w * y), dtype=np.int64)
            for i in range(h):
                for j in range(w):
                    if g[i, j] != ARKA:
                        o[i * h:(i + 1) * h, j * w:(j + 1) * w] = g
            return o

        A.append(Kaide("fraktal_%dx%d" % (p, q), fraktal))
    for p, q in sorted(kucultme):
        if (p, q) == (1, 1) or p > 8 or q > 8:
            continue
        A.append(Kaide("küçült_%dx%d" % (p, q),
                       lambda g, x=p, y=q: _kucult(g, x, y)))

    # --- bakışım onarımı: delik rengi görevden
    aday = None
    for a, b in ciftler:
        if a.shape != b.shape:
            aday = None
            break
        fark = set(np.unique(a).tolist()) - set(np.unique(b).tolist())
        if len(fark) != 1:
            aday = None
            break
        r = int(next(iter(fark)))
        if aday is None or aday == r:
            aday = r
        else:
            aday = None
            break
    if aday is not None:
        A.append(Kaide("bakışım_onar:%d" % aday,
                       lambda g, k=aday: _bakisim_onar(g, k)))

        def onar_kirp(g, k=aday):
            t = _bakisim_onar(g, k)
            if t is None:
                return None
            nz = np.argwhere(g == k)
            if nz.size == 0:
                return None
            (r0, c0), (r1, c1) = nz.min(0), nz.max(0)
            return t[r0:r1 + 1, c0:c1 + 1]

        A.append(Kaide("bakışım_onar+kırp:%d" % aday, onar_kirp))
    return A


# =====================================================================
#  Terkip ve arama
# =====================================================================
def _imza(g: Izgara) -> bytes:
    return g.shape[0].to_bytes(2, "little") + \
        g.shape[1].to_bytes(2, "little") + g.astype(np.uint8).tobytes()


def terkipler(k1: Kaide, k2: Kaide) -> Kaide:
    """``k2 ∘ k1`` -- önce ``k1``, sonra ``k2``."""
    def f(g: Izgara, a=k1, b=k2) -> Optional[Izgara]:
        t = a(g)
        return None if t is None else b(t)
    return Kaide("%s → %s" % (k1.ad, k2.ad), f, k1.boy + k2.boy,
                 k1.hipotez + k2.hipotez)


def kaide_ara(ciftler: Sequence[Tuple[Izgara, Izgara]], derinlik: int = 3,
              azami_dal: int = 220) -> List[Kaide]:
    """Gösterimlerin **hepsini** tutan kaideleri ara -- terkiple.

    Budama iki usulle: ilk çiftte tutmayan terkip açılmaz (erken ret),
    ve aynı ara hâl imzasını veren yollar teke indirilir.

    Occam sırasıyla döner: önce en kısa terkip.
    """
    if not ciftler:
        return []
    A = atomlar(ciftler)
    # **ÖĞRENİLEN AİLELER** -- nesne (`nefs/nesne.py`) ve hücre
    # (`nefs/hucre.py`). Bütün-ızgara cebri ARC'de yetmiyor (ölçüldü);
    # bunlar aynı cebre atom olarak girer, yani terkibe de katılır.
    #
    # **ÇAPRAZ SINAMA KAPISI.** Veriden öğrenilen her kaide, bırak-birini
    # istikrâsından geçmek zorundadır (bkz. ``capraz_gecerli``). Geçmeyen
    # kaide bir kaide değil bir tablodur ve **atılır**: gösterimlere tam
    # uyması onu kurtarmaz. Ölçüt kör değildir -- eleme fiilen oluyor mu,
    # ``elenen`` sayısı ile görülebilir.
    ogrenilen = ogrenilen_aileler(ciftler)
    if ogrenilen:
        gecerli = capraz_gecerli(ciftler)
        if gecerli or len(ciftler) >= 3:
            ogrenilen = [k for k in ogrenilen
                         if k.hipotez <= 0 or k.ad in gecerli]
    A = A + ogrenilen
    girdiler = [a for a, _ in ciftler]
    hedefler = [b for _, b in ciftler]

    def tutuyor(hal: List[Optional[Izgara]]) -> bool:
        return all(h is not None and h.shape == t.shape
                   and np.array_equal(h, t)
                   for h, t in zip(hal, hedefler))

    def yakinlik(hal: List[Optional[Izgara]]) -> float:
        """Ara hâl hedefe **ne kadar yaklaştı**: en kötü çiftin isabeti.

        ===================================================================
        NİÇİN: KÖR BUDAMA ARAMAYI AÇ BIRAKIYORDU
        ===================================================================

        Arama, her kademede ``azami_dal`` kadar dal tutuyordu ve sıralama
        ölçütü ``boy``du. Fakat bir kademedeki bütün dalların boyu
        **aynıdır**; yani sıralama hiçbir şey söylemiyor, budama fiilen
        **keyfî** oluyordu. Atom sayısı azken zararsızdı; seçici×
        dönüştürücü çarpımı atomu 150'nin üstüne çıkarınca arama açlıktan
        öldü.

        Ölçüldü ve teşhis budur: çözülemeyen 79 aynı şekilli görevin
        **48'inde** çarpım katmanının tek bir kaidesi hiç dokunmamaktan
        iyi netice veriyor, fakat **hiçbirinde** tek adım tam uymuyor
        (TAM UYAN = 0). Yani lazım olan şey daha çok kaide değil, o
        kaidelerin **birleştirilmesi**dir -- ve birleştirmeyi yapacak
        arama kör budama yüzünden o iyi dalları atıyordu.

        Ölçüt: en kötü gösterimdeki hücre isabeti. **En kötü** olması
        şarttır; ortalama alınsaydı bir gösterimi mükemmel, diğerini
        berbat eden bir dal öne geçerdi. Hâlbuki aranan kaide
        **hepsini** tutmalıdır, o hâlde ilerleme de en zayıf halkadan
        ölçülür.

        HUDUT: bu bir sezgidir (heuristic), ispat değil. Yanlış dalı öne
        alabilir. Fakat **kabul ölçütü değişmedi**: kaide yine bütün
        gösterimleri tam tutmak ve çapraz sınamadan geçmek zorundadır.
        Yani sezgi yalnız **nereye bakılacağını** söyler, neyin doğru
        olduğunu değil.
        """
        en_kotu = 1.0
        for h, t in zip(hal, hedefler):
            if h is None or h.shape != t.shape:
                return -1.0
            en_kotu = min(en_kotu, float(np.mean(h == t)))
        return en_kotu

    bulunan: List[Kaide] = []
    # Kademe: (kaide, her gösterimdeki ara hâl)
    kademe: List[Tuple[Kaide, List[Izgara]]] = []
    gorulen: Set[bytes] = set()
    bas = [np.ascontiguousarray(np.asarray(g, np.int64)) for g in girdiler]
    kademe.append((Kaide("birim", lambda g: g, 0), bas))

    for d in range(int(derinlik)):
        yeni: List[Tuple[Kaide, List[Izgara]]] = []
        for kok, hal in kademe:
            for a in A:
                sonra = [a(h) for h in hal]
                if any(s is None for s in sonra):
                    continue
                k = a if kok.boy == 0 else terkipler(kok, a)
                if tutuyor(sonra):
                    bulunan.append(k)
                    continue          # tutan kaide daha da uzatılmaz
                if d + 1 >= derinlik:
                    continue
                im = b"|".join(_imza(s) for s in sonra)
                if im in gorulen:
                    continue
                gorulen.add(im)
                yeni.append((k, sonra))
        if bulunan:
            break                     # Occam: en kısa kademede dur
        # **YÖNLENDİRİLMİŞ BUDAMA.** Sıralama ölçütü ``boy`` değil hedefe
        # yakınlıktır (bkz. ``yakinlik`` şerhi): bir kademedeki dalların
        # boyu zaten aynı olduğu için eski sıralama budamayı keyfî
        # bırakıyordu. İlerlemeyen dal değil, **en çok ilerleyen** dal
        # açılır. Beraberlikte kısa terkip önde: Occam bozulmaz.
        kademe = sorted(yeni, key=lambda x: (-yakinlik(x[1]), x[0].boy)
                        )[:azami_dal]
        if not kademe:
            break
    # **Occam iki eksende**: önce hipotezi küçük olan (az ezber), sonra
    # kısa terkip. Sıra tersine olsaydı üç gösterimden öğrenilmiş kocaman
    # bir desen tablosu, sabit bir döndürmenin önüne geçerdi.
    return sorted(bulunan, key=lambda k: (k.hipotez, k.boy, k.ad))
