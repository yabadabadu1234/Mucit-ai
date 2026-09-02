"""
İSKELET (``H_S``) -- *"hangi hücre dönüşür, hangisi zemin kalır"*.

===================================================================
NİÇİN VAR: KÜTÜK H91'İN ADI KONMUŞ, KODU YAZILMAMIŞ RÜKNÜ
===================================================================

H91 kâidenin beş rüknünü saymış ve dördünün karşılığını göstermişti::

    H_D ebat            "ebat kesin mi"                _teklik_ispati   ✓
    H_S iskelet/support "hangi hücre dönüşür"          (henüz yok)      ✗
    H_C illet           "her rengi neden koydum"       _illet_kesfi     ✓
    H_N nakz            "yerine başkası niçin konamaz"  karsi_ornek     ✓
    H_J muhakeme        "hükm-i yakîn"                 _makam           ✓

``H_S`` **eksikti** ve H98'de tekrar zabıtlanmıştı: *"Kurulan yalnız
ebat rüknüdür."* `nefs/kaide.py` tarafında (klasik mîzân) borç H161'de
kapandı. **Bu dosya onun çıkarım hattındaki karşılığıdır** ve asıl
kıymeti oradadır.

===================================================================
NİÇİN ÇIKARIM HATTINDA MÜHİM -- ölçülmüş darboğaz
===================================================================

Kütük H135'in ölçümü: 120 görevin **103'ünde** *"kaide bulunamadı"*.
H138 devam ediyor: 19 seçici × 12 dönüştürücü çarpımı kuruldu, çözülemeyen
79 aynı şekilli görevin 48'inde bir kaide hiç dokunmamaktan iyi netice
veriyor -- fakat **hiçbirinde tam uymuyor**.

Sebep, `nefs/kaideler.py`nin cebrinde **ifade edilemeyen** bir desen
sınıfıdır. Oradaki bütün atomlar ızgaranın **tamamına** etki eder:
döndür, kırp, döşe, renk eşle. ARC'de en sık görülen desen ise şudur:

    "şu hücreleri değiştir, ötekilere dokunma"

Bu cümle o cebirle **kurulamıyordu**. ``renk_eşlemesi`` en yakınıdır
fakat o da rengi rengin kendisinden tayin eder; *"en büyük nesnenin
içi"* yahut *"kapalı delik"* gibi **yer** esaslı bir iskelet
söyleyemez.

===================================================================
KAİDENİN ŞEKLİ -- iki parça, ikisi de yanlışlanabilir
===================================================================

Bir iskelet kâidesi iki iddiadan ibarettir::

    1. NEREYE   -- ``maske(girdi)``: dönüşecek hücreler
    2. NE       -- o hücrelere ne konacak (sabit renk yahut renk eşlemesi)

Ve ikisi de **doğrudan ölçülür**: aynı ebatlı bir şahitte fiilî iskelet
``çıktı ≠ girdi`` hücrelerinin kümesidir. Yani kâide *"yalnız kırmızıları
değiştiririm"* diyorsa ve şahitte mavi de değişmişse iddia **düşer**.
Bu, H90'ın şartıdır: ölçüt kırmızı yanabiliyor.

===================================================================
EZBERE KARŞI -- ``hipotez`` dürüstçe sayılır
===================================================================

Kütük H134'ün dersi: *"delilden büyük hipotez, istikrâ değil ezberdir."*
Buradaki hipotez sayısı küçüktür ve saklanmaz:

* sabit renkli iskelet   : ``hipotez = 1``  (tek sayı öğrenildi)
* renk eşlemeli iskelet  : ``hipotez = eşlemedeki giriş sayısı``

Maskenin kendisi öğrenilmez, **kataloğdan seçilir**; seçim de bütün
şahitlerde tutmak zorundadır. O hâlde bu aile bırak-birini kapısından
(`nefs/kaideler.capraz_gecerli`) geçebilir -- nitekim ``ogrenilen_aileler``
içine konmasının sebebi budur: her katta yeniden öğrenilir ve ölçüm
kendi cevabını görmez.

===================================================================
HUDUT -- açıkça
===================================================================

* Yalnız **aynı ebatlı** çiftlerde tanımlıdır. Farklı ebatta "aynı
  hücre" diye bir şey yoktur; iskelet orada tanımsızdır ve bu dosya
  o görevlerde **hiçbir kaide üretmez** (boş liste). Tanımsızı sıfır
  saymak, ölçütü sessizce yeşile boyamak olurdu.
* Maske kataloğu **kapalı bir küme değildir** (H60) fakat şu an
  sonludur; genişlemesi hükmü **zayıflatır** (rakip artar), yani
  dürüst istikamettedir.
* Bu bir ARC çözücüsü **değildir**; kâide cebrine eksik olan bir ifade
  gücünü ekler. Kaç görev çözüldüğü ayrıca ölçülür ve iddia edilmez.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from idrak.cozucu import _bilesenler

__all__ = ["maske_adaylari", "iskelet_kaideleri", "rapor"]

Izgara = np.ndarray
ARKA = 0


# =====================================================================
#  Maske adayları -- hepsi YALNIZ GİRDİDEN hesaplanır
# =====================================================================
def _arka_renk(g: Izgara) -> int:
    return int(np.argmax(np.bincount(np.asarray(g).ravel(), minlength=10)))


def _kapali_delik(g: Izgara) -> np.ndarray:
    """Bir nesnenin **içinde kalmış** arka plan hücreleri.

    Kenardan taşma (flood fill) ile bulunur: kenardan erişilebilen arka
    plan "dışarısı"dır; erişilemeyen arka plan **deliktir**. ARC'nin en
    sık desenlerinden biri deliği boyamaktır ve mevcut cebirde bu
    ifade edilemiyordu.
    """
    g = np.asarray(g)
    arka = g == ARKA
    h, w = g.shape
    disari = np.zeros_like(arka)
    yigin: List[Tuple[int, int]] = []
    for i in range(h):
        for j in (0, w - 1):
            if arka[i, j] and not disari[i, j]:
                disari[i, j] = True
                yigin.append((i, j))
    for j in range(w):
        for i in (0, h - 1):
            if arka[i, j] and not disari[i, j]:
                disari[i, j] = True
                yigin.append((i, j))
    while yigin:
        i, j = yigin.pop()
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = i + di, j + dj
            if 0 <= a < h and 0 <= b < w and arka[a, b] and not disari[a, b]:
                disari[a, b] = True
                yigin.append((a, b))
    return arka & ~disari


def _bilesen_maskesi(g: Izgara, olcut: str) -> np.ndarray:
    """Bir bileşen ölçütüne göre maske -- nesne esaslı iskelet."""
    b = _bilesenler(np.asarray(g), ARKA)
    if not b:
        return np.zeros(np.asarray(g).shape, bool)
    if olcut == "en_büyük":
        sec = [max(b, key=lambda x: int(x[1].sum()))]
    elif olcut == "en_küçük":
        sec = [min(b, key=lambda x: int(x[1].sum()))]
    elif olcut == "tekil":                 # tek hücrelik bileşenler
        sec = [x for x in b if int(x[1].sum()) == 1]
    elif olcut == "kenara_değen":
        h, w = np.asarray(g).shape
        sec = [x for x in b
               if x[2][0] == 0 or x[2][1] == h - 1
               or x[2][2] == 0 or x[2][3] == w - 1]
    elif olcut == "kenara_değmeyen":
        h, w = np.asarray(g).shape
        sec = [x for x in b
               if not (x[2][0] == 0 or x[2][1] == h - 1
                       or x[2][2] == 0 or x[2][3] == w - 1)]
    elif olcut == "delikli":
        def delik(x):
            r0, r1, c0, c1 = x[2]
            return (r1 - r0 + 1) * (c1 - c0 + 1) - int(x[1].sum())
        sec = [x for x in b if delik(x) > 0]
    else:
        sec = []
    out = np.zeros(np.asarray(g).shape, bool)
    for _r, m, _k in sec:
        out |= np.asarray(m, bool)
    return out


def maske_adaylari(g: Izgara) -> Dict[str, np.ndarray]:
    """Girdiden hesaplanabilen bütün iskelet adayları.

    **Hiçbiri çıktıya bakmaz.** Bakılsaydı maske "değişen hücreler"
    olurdu ve kaide her şahidi tanım gereği tutardı -- yani kırmızı
    yanamayan bir ölçüt (H90). İskeletin iddia olabilmesi, ancak
    girdiden söylenmesiyle mümkündür.
    """
    g = np.asarray(g)
    arka = _arka_renk(g)
    ad: Dict[str, np.ndarray] = {
        "sıfır": g == ARKA,
        "sıfır_hariç": g != ARKA,
        "arka": g == arka,
        "arka_hariç": g != arka,
        "kapalı_delik": _kapali_delik(g),
    }
    for k in range(10):
        m = g == k
        if m.any() and not m.all():
            ad["renk_%d" % k] = m
    for o in ("en_büyük", "en_küçük", "tekil", "kenara_değen",
              "kenara_değmeyen", "delikli"):
        m = _bilesen_maskesi(g, o)
        if m.any() and not m.all():
            ad["nesne_" + o] = m
    return {k: v for k, v in ad.items() if v.any()}


# =====================================================================
#  Kaide üretimi
# =====================================================================
def iskelet_kaideleri(ciftler: Sequence[Tuple[Izgara, Izgara]]):
    """``H_S`` kâideleri: *"şurayı şöyle yap, ötekine dokunma."*

    Usul üç adımdır ve her adım bütün şahitlerde tutmak zorundadır:

    1. **Fiilî iskelet** okunur: ``çıktı ≠ girdi``.
    2. Katalogdaki hangi maske **tam olarak** o iskeleti veriyor
       (fazlası da eksiği de kabul edilmez).
    3. O iskelete ne konduğu öğrenilir: sabit bir renk mi, yoksa
       girdinin rengine bağlı bir eşleme mi.

    2. adımdaki *"tam olarak"* şarttır. *"Kapsıyor"* denseydi
    ``sıfır_hariç`` gibi geniş bir maske her şeyi tutar ve iddia
    boşalırdı; bu, H98'de ölçülen **âşikâr kâide** kusurunun aynısı
    olurdu (*"her ispat, ispatladığı şeyin boş olmadığını da
    ispatlamalıdır"*).
    """
    from .kaideler import Kaide

    cift = [(np.asarray(a, np.int64), np.asarray(b, np.int64))
            for a, b in ciftler]
    if not cift or any(a.shape != b.shape for a, b in cift):
        return []                       # H_S farklı ebatta TANIMSIZ

    # --- 1. fiilî iskeletler
    fiili = [(a != b) for a, b in cift]
    if not any(f.any() for f in fiili):
        return []                       # hiçbir şey değişmemiş

    # --- 2. hangi maske tam tutuyor
    ortak: Optional[set] = None
    for (a, _b), f in zip(cift, fiili):
        tutan = {ad for ad, m in maske_adaylari(a).items()
                 if m.shape == f.shape and np.array_equal(m, f)}
        ortak = tutan if ortak is None else (ortak & tutan)
        if not ortak:
            return []
    out: List = []

    for ad in sorted(ortak or ()):
        # --- 3. o iskelete NE konuyor
        sabit: Optional[int] = None
        tutarli_sabit = True
        esleme: Dict[int, int] = {}
        tutarli_esleme = True
        for (a, b), f in zip(cift, fiili):
            hedef = b[f]
            if hedef.size:
                v = np.unique(hedef)
                if v.size == 1:
                    r = int(v[0])
                    if sabit is None:
                        sabit = r
                    elif sabit != r:
                        tutarli_sabit = False
                else:
                    tutarli_sabit = False
            for x, y in zip(a[f].tolist(), b[f].tolist()):
                x, y = int(x), int(y)
                if x in esleme and esleme[x] != y:
                    tutarli_esleme = False
                    break
                esleme[x] = y
            if not tutarli_esleme:
                break

        if tutarli_sabit and sabit is not None:
            def _f(g, _ad=ad, _r=sabit):
                m = maske_adaylari(g).get(_ad)
                if m is None or m.shape != np.asarray(g).shape:
                    return None
                return np.where(m, _r, np.asarray(g))
            out.append(Kaide("iskelet[%s]=%d" % (ad, sabit), _f,
                             boy=1, hipotez=1))

        if tutarli_esleme and esleme and len(esleme) > 1:
            pal = np.arange(10, dtype=np.int64)
            for k, v in esleme.items():
                if 0 <= k < 10:
                    pal[k] = v

            def _g(g, _ad=ad, _p=pal):
                m = maske_adaylari(g).get(_ad)
                g = np.asarray(g)
                if m is None or m.shape != g.shape:
                    return None
                return np.where(m, _p[np.clip(g, 0, 9)], g)
            out.append(Kaide("iskelet[%s]↦eşleme" % ad, _g,
                             boy=1, hipotez=len(esleme)))
    return out


# =====================================================================
def rapor(kume: str = "training", n: int = 120) -> str:
    """``H_S`` kaç görevde bir kâide üretiyor -- **sayım**, iddia değil."""
    from idrak import arc

    gorevler = arc.yukle_hepsi(kume)[:int(n)]
    ureten = 0
    tam = 0
    adlar: Dict[str, int] = {}
    for gv in gorevler:
        cift = [(np.asarray(a), np.asarray(b)) for a, b in gv.egitim]
        try:
            ks = iskelet_kaideleri(cift)
        except Exception:                                # noqa: BLE001
            continue
        if not ks:
            continue
        ureten += 1
        for k in ks:
            adlar[k.ad.split("[")[0]] = adlar.get(k.ad.split("[")[0], 0) + 1
        # sınama girdisinde tam çözüyor mu
        for k in ks:
            iyi = True
            for gi, ci in gv.sinama:
                o = k(np.asarray(gi))
                if o is None or o.shape != np.asarray(ci).shape \
                        or not np.array_equal(o, np.asarray(ci)):
                    iyi = False
                    break
            if iyi:
                tam += 1
                break
    s = ["=== İSKELET (H_S) -- kütük H91'in kapanan borcu ===", "",
         "  taranan görev            : %d" % len(gorevler),
         "  kâide ÜRETEN görev       : %d" % ureten,
         "  sınamayı TAM çözen görev : %d" % tam, ""]
    for ad, c in sorted(adlar.items(), key=lambda x: -x[1]):
        s.append("  %-24s %d" % (ad, c))
    s += ["",
          "Bu sayı bir çözücü iddiası değildir: iskelet, kâide cebrine",
          "eksik olan bir ifade gücünü ekler. Terkiple beraber neticesi",
          "`nefs/mudrike.py` üzerinden ayrıca ölçülür."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
