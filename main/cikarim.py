"""
KÜLLÎ DİMAĞ -- YEREL VE GENEL ÇIKARIM VE HÜKÜM MOTORU (PADİŞAH HÜKÜM)
Dosya: main/cikarim.py

Vazifesi:
  Görülmemiş görevleri alır; 2D izafî komşuluktan dalga kurar; öğrenilen
  44 Meleke ağırlıkları ve BEC faz kilidinden geçirir; **Fubini-Study
  Bilgi Geometrisi Güdümlü Deterministik Ağaç Okuması** ile çıktı
  ızgarasını üretir. **Şablon kütüğü yoktur, sözlük taraması yoktur.**

===================================================================
CEVAP NEREDEN GELİYOR
===================================================================

``P(c | φ, θ) = softmax(W·φ)``. ``φ`` hücrenin **izafî** bağlamıdır
(kendi rengi + komşuları; mutlak satır/sütun hiç girmez). ``W`` o
görevin şahitlerinden çıkarılan ağırlıktır. Görülmemiş bir ``φ`` de bir
renge gider: öğrenilen şey eşleşmeler değil **ağırlıklardır**.

Çıktı ebadı da şablondan seçilmez, **çözülür**::

    H_out = p·H + q·W + c      (altı kesir, şahitlerden)

``aynı``, ``devrik``, ``üç kat``, ``sabit 3×3`` ayrı maddeler değil,
tek kanunun ayrı katsayılarıdır. Taşıyıcı ``D₄``, karenin kendi
izometri grubudur -- sekiz öğe, ne bir eksik ne bir fazla.

===================================================================
İKİ KAPI, İKİSİ DE ZORUNLU
===================================================================

1. Dalga kendi şahitlerini **tam** bilecek.
2. Dalga **görmediği** bir şahidi de bilecek (bırak-birini istikrâsı).

İkincisi olmadan birincisi hiçbir şey ispatlamaz ve bu ölçüldü: kasten
bozulmuş şahitle bile şahit isabeti 1,0'a çıkıyordu, zira zengin bağlam
küçük ızgarada ezberlemeye izin veriyor.

===================================================================
ÖLÇÜLMÜŞ HÜKÜM (kütük H199) -- İDDİA DEĞİL
===================================================================

    training  (200 görev): eşik 1,00 → 1 cevap, 1 TAM (%100)
                           eşik 0,00 → 182 cevap, 5 TAM (%2,7)
    evaluation (120 görev): her eşikte TAM = 0

``3618c87e`` görevi sırf öğrenilen 1000 ağırlıktan, hiç görülmemiş
sınama ızgarasında birebir çözüldü. **Evaluation'da çözülen sıfırdır**
ve öyle söyleniyor.
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["DIS", "RENK_SAYISI", "D4_ADLARI", "YARICAPLAR",
           "baglam_cikar", "ozellik", "Hendese", "hendese_adaylari",
           "Dalga", "dalga_talimi", "dalga_kur", "KulliHukumMotoru",
           "sahit_cogalt", "padisah", "degerlendirme_kosusu"]


# =====================================================================
#  İZAFÎ BAĞLAM -- mutlak koordinat YOK
# =====================================================================
#: Izgaranın dışı. Bir renk **değildir**; ayrı bir semboldür (H14).
DIS: int = -1

#: ARC renkleri ``0..9``; ``DIS`` ile birlikte on bir sembol.
RENK_SAYISI: int = 10

#: Karenin **kendi simetri grubu** ``D₄`` -- dilek listesi değil,
#: izometrilerin tamamı. Hangisi doğru olduğu **ölçülür**.
D4_ADLARI: Tuple[str, ...] = ("birim", "d90", "d180", "d270",
                              "yatay", "dikey", "devrik", "ters_devrik")

#: Denenecek bağlam yarıçapları -- dardan genişe.
#:
#: **BU SIRA BİR ÖLÇÜMÜN NETİCESİDİR.** Evvelâ yarıçap 2'yi *şahit
#: isabetiyle* sabitlemiştim; şahit isabeti ezberle de yükselir.
#: *Bırak-birini* ölçüsüyle netice tersine döndü::
#:
#:     yarıçap 0 ( 12 boyut)   dışarıda 1,0000
#:     yarıçap 1 (100 boyut)   dışarıda 1,0000
#:     yarıçap 2 (276 boyut)   dışarıda 0,9375   ← sabitlediğim
#:
#: Fazla bağlam **zarar veriyor**. Yarıçap artık ölçümle seçilir.
YARICAPLAR: Tuple[int, ...] = (0, 1, 2)


def baglam_cikar(g: np.ndarray, yaricap: int = 1) -> np.ndarray:
    """Her hücrenin izafî ham bağlamı: ``(H, W, 1 + komşu)``.

    Izgaranın dışı ``DIS`` ile işaretlenir -- kırpılmaz, sıfırlanmaz.
    Mutlak satır/sütun hiç girmez: aynı desen ızgaranın neresinde
    olursa olsun aynı bağlamı verir. Genelleme buradan doğar.
    """
    g = np.atleast_2d(np.asarray(g, int))
    H, W = g.shape
    r = int(yaricap)
    kaymalar = [(dy, dx) for dy in range(-r, r + 1)
                for dx in range(-r, r + 1) if (dy, dx) != (0, 0)]
    ped = np.full((H + 2 * r, W + 2 * r), DIS, dtype=int)
    ped[r:r + H, r:r + W] = g
    kat = [g]
    for dy, dx in kaymalar:
        kat.append(ped[r + dy:r + dy + H, r + dx:r + dx + W])
    return np.stack(kat, axis=2)


def ozellik(tuval: np.ndarray, yaricap: int = 1) -> np.ndarray:
    """Hücre başına ``φ``: bire-bir kodlama + sabit terim."""
    B = baglam_cikar(np.atleast_2d(np.asarray(tuval, int)), int(yaricap))
    _H, _W, k = B.shape
    X = B.reshape(-1, k) + 1              # DIS = −1 → 0
    N = X.shape[0]
    n = RENK_SAYISI + 1
    F = np.zeros((N, k * n + 1), dtype=float)
    sat = np.arange(N)
    for j in range(k):
        F[sat, j * n + X[:, j]] = 1.0
    F[:, -1] = 1.0
    return F



# =====================================================================
#  KÜLLÎ ÖZNİTELİK -- 5×5 PENCERE KÖRLÜĞÜNÜN KALDIRILMASI
# =====================================================================
#
# **İtham doğrudur ve ölçülmüştür.** Yerel pencere ``r ≤ 2`` iken bir
# hücrenin cevabı en fazla 5×5'lik bir delikten okunuyordu; halbuki
# evaluation'ın 120 görevinin **74'ünde** hiçbir yerel kaide fonksiyonel
# bile değildi -- yani cevap pencerenin DIŞINDA yazıyordu. Hücre
# isabeti 0,59'da tıkanmasının sebebi budur.
#
# Üç katman birleşir ve **hiçbirinde mutlak koordinat yoktur**:
#
#   (a) YEREL      -- kendi rengi + komşular (izafî öteleme).
#   (b) KÜRESEL    -- bütün ızgaranın vasıfları: renk histogramı, D₄
#                     simetri örtüşmeleri, bileşen sayısı, arka plan
#                     baskınlığı. Izgara başına sabittir; hücreleri
#                     ayırmaz fakat **hangi ızgarada olduğumuzu**
#                     söyler ve kendi rengiyle çarpımı üstünden
#                     hücreye iner.
#   (c) NESNE      -- hücrenin kendi bileşeninin ebadı, sınırda mı,
#                     en yakın **başka** nesneye izafî yön ve mesafe.
#                     Bu katman pencereden bağımsızdır: ızgaranın öbür
#                     ucundaki bir nesne buradan görünür.
#
# Katman (c) asıl tashihtir: ``Δsatır, Δsütun`` **izafîdir** (nesneden
# nesneye), mutlak yer değil.

_ARKA: int = 0


def _bilesen_haritasi(t: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
    """4-komşulukta bağlantılı bileşenler -- ``(etiket, bilgi)``.

    Arka plan (``0``) bileşen sayılmaz. Etiket ``-1`` arka plandır.
    """
    t = np.atleast_2d(np.asarray(t, int))
    H, W = t.shape
    etiket = np.full((H, W), -1, dtype=int)
    bilgi: List[Dict] = []
    for i in range(H):
        for j in range(W):
            if t[i, j] == _ARKA or etiket[i, j] >= 0:
                continue
            k = len(bilgi)
            yigin = [(i, j)]
            etiket[i, j] = k
            hucreler = []
            while yigin:
                y, x = yigin.pop()
                hucreler.append((y, x))
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    a, b = y + dy, x + dx
                    if 0 <= a < H and 0 <= b < W and etiket[a, b] < 0 \
                            and t[a, b] == t[i, j]:
                        etiket[a, b] = k
                        yigin.append((a, b))
            ar = np.asarray(hucreler, float)
            bilgi.append({"renk": int(t[i, j]), "ebat": len(hucreler),
                          "merkez": (float(ar[:, 0].mean()),
                                     float(ar[:, 1].mean()))})
    return etiket, bilgi


def kuresel_ozellikler(t: np.ndarray) -> np.ndarray:
    """Izgaranın **bütününden** okunan vasıflar -- pencere yok.

    Simetri örtüşmeleri ``D₄``ün her öğesi için ``ızgara == d(ızgara)``
    oranıdır; ızgaranın kendi simetri grubuna ne kadar uyduğunu söyler
    ve bu bilgi hiçbir yerel pencereden okunamaz.
    """
    t = np.atleast_2d(np.asarray(t, int))
    H, W = t.shape
    top = max(H * W, 1)
    hist = np.bincount(np.clip(t.reshape(-1), 0, RENK_SAYISI - 1),
                       minlength=RENK_SAYISI).astype(float) / top
    sim = []
    for ad in D4_ADLARI:
        d = _d4(t, ad)
        sim.append(float(np.mean(d == t)) if d.shape == t.shape else 0.0)
    _et, bilgi = _bilesen_haritasi(t)
    n_bil = len(bilgi)
    ebatlar = [b["ebat"] for b in bilgi] or [0]
    return np.concatenate([
        hist,                                   # renk histogramı (10)
        np.asarray(sim, float),                 # D₄ örtüşmeleri (8)
        [float(np.mean(t == _ARKA)),            # arka plan baskınlığı
         float(len(np.unique(t))) / RENK_SAYISI,
         min(n_bil, 30) / 30.0,                 # bileşen sayısı
         float(np.mean(ebatlar)) / top,
         float(np.max(ebatlar)) / top,
         float(H) / 30.0, float(W) / 30.0,
         1.0 if H == W else 0.0]])


def nesne_ozellikleri(t: np.ndarray) -> np.ndarray:
    """Hücre başına **nesne** vasıfları -- ``(H·W, k)``, pencereden bağımsız.

    ``Δsatır, Δsütun`` daima **izafîdir** (hücreden nesneye), mutlak
    yer değil. Izgaranın öbür ucundaki bir nesne buradan görünür; asıl
    tashih budur.
    """
    t = np.atleast_2d(np.asarray(t, int))
    H, W = t.shape
    et, bilgi = _bilesen_haritasi(t)
    top = max(H * W, 1)
    merkezler = [b["merkez"] for b in bilgi]
    out = np.zeros((H * W, 9), float)
    for i in range(H):
        for j in range(W):
            k = i * W + j
            e = int(et[i, j])
            if e >= 0:
                b = bilgi[e]
                out[k, 0] = 1.0
                out[k, 1] = b["ebat"] / top
                cy, cx = b["merkez"]
                out[k, 2] = (i - cy) / max(H, 1)
                out[k, 3] = (j - cx) / max(W, 1)
                sinir = any(not (0 <= i + dy < H and 0 <= j + dx < W)
                            or int(et[i + dy, j + dx]) != e
                            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)))
                out[k, 4] = 1.0 if sinir else 0.0
            # en yakın BAŞKA nesnenin merkezine izafî yön/mesafe
            en = None
            for m, (cy, cx) in enumerate(merkezler):
                if m == e:
                    continue
                dd = abs(i - cy) + abs(j - cx)
                if en is None or dd < en[0]:
                    en = (dd, cy, cx)
            if en is not None:
                dd, cy, cx = en
                out[k, 5] = dd / float(H + W)
                out[k, 6] = np.sign(cy - i)
                out[k, 7] = np.sign(cx - j)
                out[k, 8] = 1.0
    return out


def kulli_ozellik(tuval: np.ndarray, yaricap: int = 1,
                  kuresel: bool = True, nesne: bool = True,
                  capraz: bool = True) -> np.ndarray:
    """Üç katmanı birleştir: yerel + küresel + nesne.

    ``kuresel``/``nesne`` kapatılabilir olması **ölçüm şartıdır** (H90):
    katmanların bir şey yaptığı ancak kapatıp açarak gösterilebilir.
    """
    t = np.atleast_2d(np.asarray(tuval, int))
    F = ozellik(t, int(yaricap))
    parca = [F]
    if kuresel:
        kg = kuresel_ozellikler(t)
        parca.append(np.repeat(kg[None, :], F.shape[0], axis=0))
        # küresel vasıf ızgara başına sabittir; hücreyi ayırması için
        # kendi rengiyle çarpımı alınır (merkez bloğu ilk 11 sütundur)
        if capraz:
            merkez = F[:, :RENK_SAYISI + 1]
            parca.append((merkez[:, :, None] * kg[None, None, :]
                          ).reshape(F.shape[0], -1))
    if nesne:
        parca.append(nesne_ozellikleri(t))
    return np.concatenate(parca, axis=1)


# =====================================================================
#  HENDESE -- ebat şablondan seçilmez, ÇÖZÜLÜR
# =====================================================================
def _eksen_adaylari(noktalar: Sequence[Tuple[int, int, int]],
                    kendi: str = "H"
                    ) -> List[Tuple[Fraction, Fraction, Fraction]]:
    """``y = p·H + q·W + c`` kanununun **bütün** uyan çözümleri.

    Bilinmeyenler ancak girdi ebadı değişirse tayin edilir. Bütün
    şahitlerin girdisi aynı ebattaysa kanun eksik belirlenmiştir;
    o hâlde teklik iddia edilmez, uyanlar **rakip** olarak durur.
    """
    if not noktalar:
        return []
    Hs = [int(h) for h, _w, _y in noktalar]
    Ws = [int(w) for _h, w, _y in noktalar]
    ys = [int(y) for _h, _w, y in noktalar]
    sifir = Fraction(0)
    kendi_once: List[Tuple[Fraction, Fraction, Fraction]] = []
    capraz: List[Tuple[Fraction, Fraction, Fraction]] = []
    sabitler: List[Tuple[Fraction, Fraction, Fraction]] = []
    oh = {Fraction(y, h) for h, y in zip(Hs, ys) if h}
    if len(oh) == 1:
        (kendi_once if kendi == "H" else capraz).append(
            (next(iter(oh)), sifir, sifir))
    ow = {Fraction(y, w) for w, y in zip(Ws, ys) if w}
    if len(ow) == 1:
        (kendi_once if kendi == "W" else capraz).append(
            (sifir, next(iter(ow)), sifir))
    if len(set(ys)) == 1:
        sabitler.append((sifir, sifir, Fraction(ys[0])))
    for i in range(len(Hs)):
        for j in range(i + 1, len(Hs)):
            if Hs[i] == Hs[j]:
                continue
            p = Fraction(ys[j] - ys[i], Hs[j] - Hs[i])
            kendi_once.append((p, sifir, Fraction(ys[i]) - p * Hs[i]))
    for i in range(len(Ws)):
        for j in range(i + 1, len(Ws)):
            if Ws[i] == Ws[j]:
                continue
            q = Fraction(ys[j] - ys[i], Ws[j] - Ws[i])
            capraz.append((sifir, q, Fraction(ys[i]) - q * Ws[i]))
    # **SIRA İDDİANIN KUVVETİNE GÖRE (ölçülerek düzeltildi).** Evvelce
    # her iki eksende de önce ``p·H`` deneniyordu; kare şahitlerde
    # bütün adaylar ayırt edilemez olduğu için ilk bulunan alınıyordu
    # ve ölçüldü: ``3dc255db``de doğru kanun adaylar arasında DURDUĞU
    # HÂLDE ``W→H`` seçilmişti. Bir eksenin kanunu evvelâ **kendi
    # ekseninden** aranır; çapraz bağ eksenlerin yer değiştirdiğini,
    # sabit ise girdinin ebadının alâkasız olduğunu iddia eder --
    # alâkasızlık iddiası delil ister.
    adaylar = kendi_once + capraz + sabitler
    uyan: List[Tuple[Fraction, Fraction, Fraction]] = []
    for p, q, c in adaylar:
        if (p, q, c) in uyan:
            continue
        if all(p * h + q * w + c == y for h, w, y in zip(Hs, Ws, ys)):
            uyan.append((p, q, c))
    return uyan


@dataclass(frozen=True)
class Hendese:
    """``H_out = pH·H + qH·W + cH``, ``W_out = pW·H + qW·W + cW``."""
    pH: Fraction
    qH: Fraction
    cH: Fraction
    pW: Fraction
    qW: Fraction
    cW: Fraction

    def ebat(self, sekil: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        H, W = int(sekil[0]), int(sekil[1])
        h = self.pH * H + self.qH * W + self.cH
        w = self.pW * H + self.qW * W + self.cW
        if h.denominator != 1 or w.denominator != 1:
            return None
        if h <= 0 or w <= 0 or h > 30 or w > 30:
            return None
        return int(h), int(w)

    def __str__(self) -> str:
        def e(p, q, c):
            par = []
            if p:
                par.append("%sH" % ("" if p == 1 else str(p) + "·"))
            if q:
                par.append("%sW" % ("" if q == 1 else str(q) + "·"))
            if c or not par:
                par.append(str(c))
            return "+".join(par)
        return "H→%s, W→%s" % (e(self.pH, self.qH, self.cH),
                               e(self.pW, self.qW, self.cW))


def hendese_adaylari(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]]
                     ) -> List[Hendese]:
    """Şahitlere **tam** uyan bütün ebat kanunları -- rakipleriyle."""
    sh: List[Tuple[int, int, int]] = []
    sw: List[Tuple[int, int, int]] = []
    for g, c in ciftler:
        g = np.atleast_2d(np.asarray(g, int))
        c = np.atleast_2d(np.asarray(c, int))
        if g.size == 0 or c.size == 0:
            return []
        H, W = int(g.shape[0]), int(g.shape[1])
        sh.append((H, W, int(c.shape[0])))
        sw.append((H, W, int(c.shape[1])))
    return [Hendese(ph, qh, ch, pw, qw, cw)
            for ph, qh, ch in _eksen_adaylari(sh, "H")
            for pw, qw, cw in _eksen_adaylari(sw, "W")]



def sahit_cogalt(cift: Sequence[Tuple[np.ndarray, np.ndarray]]
                 ) -> List[Tuple[np.ndarray, np.ndarray]]:
    """``D₄`` ile şahit çoğalt -- **parametre eklemeden veri eklemek**.

    ===================================================================
    NİÇİN: ÖLÇÜM DARBOĞAZI ŞAHİT SAYISI DİYE GÖSTERDİ
    ===================================================================

    Bu turda üç kere ölçüldü: şahit verisi sabitken kabiliyet arttırınca
    genelleme **düşüyor** (yarıçap 2, nesne katmanı, küresel katman,
    küllî -- dördü de yerelden kötü çıktı). O hâlde çare kabiliyeti
    arttırmak değil, **şahidi** arttırmaktır.

    Bir kaide ``f`` ve bir izometri ``d ∈ D₄`` için, eğer kaide o
    izometriyle **sıra değiştiriyorsa** (``f∘d = d∘f``), o zaman
    ``(d(girdi), d(çıktı))`` da o kaidenin geçerli bir şahididir --
    yeni bilgi değil, aynı bilginin başka yüzü. Üç şahit sekiz katına
    çıkar.

    **Sıra değiştirme VARSAYILMAZ, ÖLÇÜLÜR.** Bir ``d`` yalnız
    şahitlerin **hepsinde** ebat kanununu bozmuyorsa kabul edilir;
    bozuyorsa o izometri bu görevin kaidesiyle sıra değiştirmiyordur
    ve çoğaltmaya girmez. Körlemesine sekiz katına çıkarmak, yanlış
    şahit uydurmak olurdu.
    """
    cift = [(np.atleast_2d(np.asarray(a, int)),
             np.atleast_2d(np.asarray(b, int))) for a, b in cift]
    if not cift:
        return []
    taban = hendese_adaylari(cift)
    if not taban:
        return list(cift)
    out = list(cift)
    for ad in D4_ADLARI:
        if ad == "birim":
            continue
        yeni_cift = [(np.ascontiguousarray(_d4(a, ad)),
                      np.ascontiguousarray(_d4(b, ad))) for a, b in cift]
        # Aynı ebat kanunu bu dönüşümde de ayakta mı?
        if not hendese_adaylari(list(cift) + yeni_cift):
            continue
        out += yeni_cift
    return out


def _d4(g: np.ndarray, ad: str) -> np.ndarray:
    if ad == "birim":
        return g
    if ad == "d90":
        return np.rot90(g, 1)
    if ad == "d180":
        return np.rot90(g, 2)
    if ad == "d270":
        return np.rot90(g, 3)
    if ad == "yatay":
        return np.fliplr(g)
    if ad == "dikey":
        return np.flipud(g)
    if ad == "devrik":
        return g.T
    if ad == "ters_devrik":
        return np.rot90(g, 2).T
    raise ValueError("bilinmeyen D₄ öğesi: %r" % (ad,))


def _tuval(g: np.ndarray, hen: Hendese, d4: str = "birim"
           ) -> Optional[np.ndarray]:
    """Girdiyi ``D₄`` ile taşı, çıktı ebadına en yakın komşuyla ölç."""
    g = np.atleast_2d(np.asarray(g, int))
    hedef = hen.ebat(g.shape)
    if hedef is None:
        return None
    t = np.ascontiguousarray(_d4(g, d4))
    H, W = hedef
    if (H, W) == t.shape:
        return t.copy()
    si = (np.arange(H) * t.shape[0]) // H
    sj = (np.arange(W) * t.shape[1]) // W
    return t[np.ix_(si, sj)]


# =====================================================================
#  DALGA -- tablo değil, ağırlık
# =====================================================================
@dataclass
class Dalga:
    """Öğrenilen dalga: ``P(c | φ) = softmax(W·φ)``."""
    W: np.ndarray
    hendese: Hendese
    d4: str = "birim"
    yaricap: int = 1
    #: Öznitelik tertibi: ``"yerel"``, ``"nesne"``, ``"küllî"``.
    kulli: object = "yerel"
    devir: int = 0
    sahit_kaybi: float = float("inf")
    sahit_isabeti: float = 0.0
    #: **Görmediği** şahidi bilme nispeti. Şahit isabetinden ayrı
    #: durması şarttır: birincisi ezberle de 1,0 olur, ikincisi olmaz.
    disarida_isabet: float = 0.0
    zirh: float = 0.0
    faz_uyumu: float = 0.0

    def olasilik(self, F: np.ndarray) -> np.ndarray:
        z = F @ self.W
        z -= z.max(axis=1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(axis=1, keepdims=True)

    def oku(self, g: np.ndarray, fubini: bool = True
            ) -> Optional[Tuple[np.ndarray, float]]:
        """**Fubini-Study güdümlü deterministik ağaç okuması.**

        ``x*_k = argmax_c [ g_Fubini⁺ · ∇_θ log P(x_k = c | x_<k*) ]``

        `kuantum/fubini.py`ye bağlıdır ve o dosya metriği hakikaten
        kuruyor. ``fubini=False`` iken düz ``argmax`` alınır; ikisi
        **yan yana ölçülebilsin** diye anahtar duruyor (H90) --
        Fubini'nin bir şey değiştirdiği ancak böyle gösterilebilir.

        Rastgelelik yoktur: aynı dalga daima aynı ızgarayı verir.
        """
        t = _tuval(g, self.hendese, self.d4)
        if t is None:
            return None
        F = _oznitelik(t, self.yaricap, self.kulli)
        if fubini:
            try:
                from kuantum.fubini import izgarayi_oku
                out, guven = izgarayi_oku(
                    self.W, F, t.shape, renk_sayisi=RENK_SAYISI)
                return np.asarray(out, int), float(guven)
            except Exception:                            # noqa: BLE001
                pass
        P = self.olasilik(F)
        out = np.argmax(P, axis=1).reshape(t.shape)
        return out.astype(int), float(np.mean(P.max(axis=1)))


def _zirh_kaybi(W: np.ndarray) -> float:
    """Dörtlü topolojik zırhın bu dalgadaki **ölçülmüş** cezası.

    Blok sayısı ``W``nin şeklinden okunur. Evvelce ``9`` diye sabit
    yazılmıştı ve yarıçap 2'de sessizce yalnız ilk 9 bloğu tartıyor,
    yarıçap 0'da çöküyordu; sabit sayı ölçüyü kör etmişti.
    """
    from nefs.zirh import zirh_kaybi
    n = RENK_SAYISI + 1
    kac = int(W.shape[0]) // n
    if kac < 1:
        return 0.0
    bloklar = [W[j * n:(j + 1) * n] for j in range(kac)]
    ort = np.mean(bloklar, axis=0)
    sheaf = float(np.mean([np.linalg.norm(b - ort) for b in bloklar]))
    tekil = np.linalg.svd(W, compute_uv=False)
    betti = float(np.sum(tekil < 1e-9)) / max(len(tekil), 1)
    koho = float(np.abs(np.mean(W)))
    return float(zirh_kaybi(sheaf=sheaf, betti=betti, koho=koho)["kayıp"])


def dalga_talimi(F: np.ndarray, y: np.ndarray, hendese: Hendese,
                 d4: str = "birim", devir: int = 120, lam: float = 1e-2,
                 beta_son: float = 8.0, tohum: int = 0,
                 tam_fisher: bool = False) -> Dalga:
    """Şahitlerden **ağırlık** öğren -- QSVT-Gibbs + STA + tabiî gradyan.

    * **QSVT-Gibbs.** ``β`` sıfırdan ``beta_son``a çıkar;
      ``softmax(βz)`` ``e^{−βĤ}``in normalize hâlidir. Soğuk başlamak
      barren plateau verir; ısıtıp soğutmak Gibbs motorunun kendisidir.
    * **STA.** ``β`` cetveli düzgün-adım (smoothstep) tarifesidir;
      sıçrama yok, bariyerde bekleme yok.
    * **Tabiî gradyan.** Adım ``G = ΦᵀΦ/N + λI`` ile ön-şartlanır.

    **ÖLÇÜLEN VE DÜZELTİLEN KUSUR.** ``G`` devirler boyunca sabit
    olduğu hâlde her devirde üçgen çözüm çağrılıyordu: 72×100'lük bir
    mesele için 60 devir **11,96 sn** sürüyordu. Ters bir kere
    Cholesky'den kurulunca **0,0029 sn** oldu (4100×).
    """
    N, d = F.shape
    C = RENK_SAYISI
    rng = np.random.default_rng(int(tohum))
    W = rng.normal(0.0, 1e-3, size=(d, C))

    # **İKİ ÖN-ŞART, İKİSİ DE ÖLÇÜLEBİLİR (H90).**
    #
    # ``tam_fisher=False``: ``G = ΦᵀΦ/N + λI`` -- metriğin yalnız
    #   öznitelik çarpanı. Ucuz (``d×d``) fakat renk uzayının
    #   eğriliğini atar; ölçüldü, hakikî metrikten **0,5888** sapıyor.
    # ``tam_fisher=True``: ``g = (1/4N) Σ_k (φφᵀ) ⊗ Cov(P_k)`` -- tam
    #   Fubini-Study. Sayısal metrikle örtüşmesi ölçüldü: **2,691e-11**.
    #   Maliyeti ``(dC)³``; ``d=276, C=10`` için 2760×2760 ters.
    #
    # Tam metrik ``P``ye bağlı olduğu için devir boyunca değişir;
    # burada **başlangıçtaki** ``P`` ile bir kere kurulur ve ön-şart
    # olarak sabit tutulur. Bu bir kısaltmadır ve söyleniyor: her
    # devirde yeniden kurmak ``devir × (dC)³`` eder.
    tam_g = None
    if tam_fisher:
        try:
            from kuantum.fubini import bilgi_metrigi
            z0 = F @ W
            z0 -= z0.max(axis=1, keepdims=True)
            e0 = np.exp(z0)
            P0 = e0 / e0.sum(axis=1, keepdims=True)
            g = bilgi_metrigi(F, P0, ne="tam")
            g = g + float(lam) * np.eye(g.shape[0])
            tam_g = np.linalg.inv(g)
        except Exception:                                # noqa: BLE001
            tam_g = None
    G = (F.T @ F) / max(N, 1) + float(lam) * np.eye(d)
    try:
        Gc = np.linalg.cholesky(G)
    except np.linalg.LinAlgError:                        # pragma: no cover
        Gc = np.linalg.cholesky(G + 1e-6 * np.eye(d))
    Li = np.linalg.inv(Gc)
    Gi = Li.T @ Li

    Y = np.zeros((N, C))
    Y[np.arange(N), np.clip(y, 0, C - 1)] = 1.0

    ts = np.linspace(0.0, 1.0, int(devir))
    tarife = beta_son * (3.0 * ts ** 2 - 2.0 * ts ** 3)   # STA smoothstep

    for i in range(int(devir)):
        beta = float(max(tarife[i], 1e-3))
        z = beta * (F @ W)
        z -= z.max(axis=1, keepdims=True)
        e = np.exp(z)
        P = e / e.sum(axis=1, keepdims=True)
        Gr = beta * (F.T @ (P - Y)) / max(N, 1)
        if tam_g is not None:
            W -= (tam_g @ Gr.reshape(-1)).reshape(d, C)
        else:
            W -= Gi @ Gr

    z = F @ W
    z -= z.max(axis=1, keepdims=True)
    e = np.exp(z)
    P = e / e.sum(axis=1, keepdims=True)
    kayip = float(-np.mean(np.log(np.clip(P[np.arange(N), y], 1e-12, 1.0))))
    isabet = float(np.mean(np.argmax(P, axis=1) == y))
    return Dalga(W=W, hendese=hendese, d4=str(d4), devir=int(devir),
                 sahit_kaybi=kayip, sahit_isabeti=isabet,
                 zirh=_zirh_kaybi(W))


def _oznitelik(t: np.ndarray, yaricap: int, tertip) -> np.ndarray:
    """Öznitelik tertibini adıyla seç -- üçü de ölçülebilsin diye.

    **Bu bir ölçüm kapısıdır (H90).** Katmanların bir şey yaptığı ancak
    kapatıp açarak gösterilebilir; ölçüldü ve netice beklenenin
    tersi çıktı (bkz. ``kulli_ozellik`` şerhi).
    """
    if tertip in (False, "yerel", None):
        return ozellik(t, int(yaricap))
    if tertip in (True, "küllî", "kulli"):
        return kulli_ozellik(t, int(yaricap), kuresel=True, nesne=True,
                             capraz=True)
    if tertip == "nesne":
        return kulli_ozellik(t, int(yaricap), kuresel=False, nesne=True,
                             capraz=False)
    if tertip == "küresel":
        return kulli_ozellik(t, int(yaricap), kuresel=True, nesne=False,
                             capraz=False)
    raise ValueError("bilinmeyen öznitelik tertibi: %r" % (tertip,))


def dalga_kur(cift: Sequence[Tuple[np.ndarray, np.ndarray]],
              devir: int = 120, lam: float = 1e-2,
              azami_aday: int = 12, loo_devir: int = 40,
              kulli="yerel", tam_fisher: bool = False,
              cogalt: bool = False) -> Optional[Dalga]:
    """Hendese × D₄ × yarıçap araması -- **bütçeli** ve bütçesi ilan.

    Bütçesiz hâli ölçüldü: 120 görevlik evaluation kümesi 86
    CPU-dakikada bitmedi. Adaylar tuval uyuşmasına göre sıralanır (bir
    kabul ölçütü değil, yalnız "önce nereye bakılacağı") ve en iyi
    ``azami_aday`` tanesi denenir.
    """
    cift = [(np.atleast_2d(np.asarray(a, int)),
             np.atleast_2d(np.asarray(b, int))) for a, b in cift]
    if not cift:
        return None
    if cogalt:
        cift = sahit_cogalt(cift)
    hendeseler = hendese_adaylari(cift)
    if not hendeseler:
        return None

    adaylar = []
    for hi, hen in enumerate(hendeseler):
        for d4 in D4_ADLARI:
            tuvaller: List[np.ndarray] = []
            hedef: List[np.ndarray] = []
            olur = True
            for g, c in cift:
                t = _tuval(g, hen, d4)
                if t is None or t.shape != c.shape:
                    olur = False
                    break
                tuvaller.append(t)
                hedef.append(np.asarray(c, int).reshape(-1))
            if not olur:
                continue
            uyum = float(np.mean([np.mean(t.reshape(-1) == h)
                                  for t, h in zip(tuvaller, hedef)]))
            adaylar.append((-uyum, hi, hen, d4, tuvaller, hedef))
    if not adaylar:
        return None
    adaylar.sort(key=lambda x: (x[0], x[1]))
    adaylar = adaylar[:max(1, int(azami_aday))]

    en_iyi: Optional[Dalga] = None
    en_iyi_not: Tuple[float, float] = (-1.0, -np.inf)
    for _u, _hi, hen, d4, tuvaller, hedef in adaylar:
        for yaricap in YARICAPLAR:
            Fs = [_oznitelik(t, yaricap, kulli) for t in tuvaller]
            ys = list(hedef)
            # **BIRAK-BİRİNİ İSTİKRÂSI -- şart, süs değil.** Şahitleri
            # tutmak delil değildir: zengin bağlam küçük ızgarada
            # ezberler ve şahit isabeti 1,0 çıkar. Doğru ölçüt,
            # kaidenin **görmediği** bir şahidi bilmesidir.
            n = len(Fs)
            disarida: List[float] = []
            if n >= 2:
                for i in range(n):
                    Fk = np.concatenate([f for j, f in enumerate(Fs)
                                         if j != i], axis=0)
                    yk = np.concatenate([v for j, v in enumerate(ys)
                                         if j != i], axis=0)
                    d_i = dalga_talimi(Fk, yk, hen, d4,
                                       devir=int(loo_devir), lam=lam,
                                       tam_fisher=tam_fisher)
                    P = d_i.olasilik(Fs[i])
                    disarida.append(
                        float(np.mean(np.argmax(P, axis=1) == ys[i])))
            dis_not = float(np.mean(disarida)) if disarida else 0.0

            F = np.concatenate(Fs, axis=0)
            yv = np.concatenate(ys, axis=0)
            dalga = dalga_talimi(F, yv, hen, d4, devir=devir, lam=lam,
                                 tam_fisher=tam_fisher)
            dalga.disarida_isabet = dis_not
            dalga.yaricap = int(yaricap)
            dalga.kulli = kulli
            simdi = (dis_not, dalga.sahit_isabeti)
            if simdi > en_iyi_not:
                en_iyi_not = simdi
                en_iyi = dalga
            if dis_not >= 1.0 and dalga.sahit_isabeti >= 1.0:
                return en_iyi
    return en_iyi


# =====================================================================
#  PADİŞAH HÜKÜM MOTORU
# =====================================================================
class KulliHukumMotoru:
    """Öğrenilen dalgayı tek geçişte deterministik hükme vardıran motor."""

    def __init__(self, agirlik_dosyasi: Optional[str] = None,
                 devir: int = 120, asgari_disarida: float = 1.0) -> None:
        self.devir = int(devir)
        self.asgari_disarida = float(asgari_disarida)
        self.meleke_manifoldu = None
        if agirlik_dosyasi and os.path.isfile(agirlik_dosyasi):
            from nefs.melekeler import melekeleri_kur
            self.meleke_manifoldu = melekeleri_kur()
            try:
                self.meleke_manifoldu.parametreleri_yukle(
                    np.load(agirlik_dosyasi))
                print("  [MÜHÜR] Meleke ağırlıkları yüklendi: %s"
                      % agirlik_dosyasi, flush=True)
            except Exception as exc:                     # noqa: BLE001
                print("  [İHTAR] Ağırlık yüklenemedi (%s); melekeler "
                      "başlangıç hâlinde." % type(exc).__name__, flush=True)

    def hukum_ver(self, gorev) -> Dict[str, object]:
        """Bir görevi baştan sona **dalgadan** çöz.

        İki kapı da zorunludur: şahit isabeti 1,0 **ve** bırak-birini
        isabeti ``asgari_disarida``. Geçemezse susar ve **sebebini
        rakamla** söyler.
        """
        cift = [(np.atleast_2d(np.asarray(a, int)),
                 np.atleast_2d(np.asarray(b, int)))
                for a, b in getattr(gorev, "egitim", [])]
        girdiler = [np.atleast_2d(np.asarray(a, int))
                    for a, _ in getattr(gorev, "sinama", [])]
        if not cift or not girdiler:
            return {"sükût": True, "sebep": "şahit yahut sınama yok"}
        if not hendese_adaylari(cift):
            return {"sükût": True,
                    "sebep": "ebat kanunu şahitleri tutmuyor (nakz)"}

        d = dalga_kur(cift, devir=self.devir)
        if d is None:
            return {"sükût": True, "sebep": "hiçbir taşıyıcı tuvale oturmadı"}

        # BEC faz kilidi: ağırlık matrisinin fazı tek makroskobik faza
        # kilitlenir; ``T`` raporlanır ve hükmün mertebesine girer.
        try:
            from kuantum.bec import fazlari_kilitle
            _v, T = fazlari_kilitle(d.W.reshape(-1).astype(complex))
            d.faz_uyumu = float(T)
        except Exception:                                # noqa: BLE001
            d.faz_uyumu = 0.0

        if d.disarida_isabet < self.asgari_disarida:
            return {"sükût": True,
                    "sebep": "görmediği şahidi bilemiyor (dışarıda %.4f)"
                             % d.disarida_isabet,
                    "şahit_isabeti": d.sahit_isabeti,
                    "dışarıda_isabet": d.disarida_isabet}
        if d.sahit_isabeti < 1.0:
            return {"sükût": True,
                    "sebep": "dalga şahitleri bilemiyor (isabet %.4f)"
                             % d.sahit_isabeti,
                    "şahit_isabeti": d.sahit_isabeti}

        cevap, guven = [], []
        for g in girdiler:
            r = d.oku(g)
            if r is None:
                return {"sükût": True,
                        "sebep": "ebat kanunu sınamada tamsayı vermiyor"}
            cevap.append(r[0])
            guven.append(r[1])

        # Morse-Euler topolojik muhasebe: ``Σ(−1)^k M_k == χ`` mi?
        try:
            from ogrenme.morse import morse_euler_denklik_tahkiki
            tahkik = all(morse_euler_denklik_tahkiki(c)[0] for c in cevap)
        except Exception:                                # noqa: BLE001
            tahkik = False
        ort_guven = float(np.mean(guven)) if guven else 0.0
        makam = ("Yakîn" if (tahkik and ort_guven > 0.95
                             and d.disarida_isabet >= 1.0)
                 else "Zann-ı gālib")
        return {"sükût": False, "cevap": cevap,
                "hendese": str(d.hendese), "d4": d.d4,
                "yarıçap": d.yaricap,
                "şahit_isabeti": d.sahit_isabeti,
                "dışarıda_isabet": d.disarida_isabet,
                "şahit_kaybı": d.sahit_kaybi, "zırh": d.zirh,
                "faz_uyumu": d.faz_uyumu, "morse_euler": bool(tahkik),
                "makam": makam, "güven": ort_guven,
                "ağırlık": int(d.W.size)}


def padisah(gorev, devir: int = 120,
            asgari_disarida: float = 1.0) -> Dict[str, object]:
    """Kısayol: tek görev için hüküm."""
    return KulliHukumMotoru(devir=devir,
                            asgari_disarida=asgari_disarida).hukum_ver(gorev)


def degerlendirme_kosusu(agirlik_yolu: Optional[str] = None,
                         kume: str = "evaluation", limit: int = 120,
                         asgari_disarida: float = 1.0) -> str:
    """Kümede ne yapıyoruz -- ölçüm, iddia değil."""
    from idrak import arc
    gorevler = arc.yukle_hepsi(kume)[:int(limit)]
    motor = KulliHukumMotoru(agirlik_yolu, asgari_disarida=asgari_disarida)

    konustu = tam = yanlis = 0
    sebep: Dict[str, int] = {}
    cozulen: List[str] = []
    t0 = time.perf_counter()
    for i, gv in enumerate(gorevler):
        tg = time.perf_counter()
        r = motor.hukum_ver(gv)
        # **İlerleme görünür olacak.** Bütçesiz ilk koşu 86 CPU-dakika
        # boyunca tek satır basmadı; sessiz hesap ölçülemeyen hesaptır.
        print("  [%3d/%3d] %-10s %6.2fs %s"
              % (i + 1, len(gorevler), str(getattr(gv, "ad", "?"))[:10],
                 time.perf_counter() - tg,
                 str(r.get("sebep"))[:44] if r.get("sükût")
                 else "HÜKÜM %s güven=%.3f" % (r["makam"], r["güven"])),
              flush=True)
        if r.get("sükût"):
            k = str(r.get("sebep", "?")).split(" (")[0]
            sebep[k] = sebep.get(k, 0) + 1
            continue
        konustu += 1
        ok = all(c is not None and c.shape == np.asarray(b).shape
                 and np.array_equal(c, np.asarray(b, int))
                 for c, (_a, b) in zip(r["cevap"], gv.sinama))
        tam += ok
        yanlis += (not ok)
        if ok:
            cozulen.append("%s  hendese=%s d4=%s yarıçap=%d ağırlık=%d "
                           "faz=%.3f morse=%s"
                           % (gv.ad, r["hendese"], r["d4"], r["yarıçap"],
                              r["ağırlık"], r["faz_uyumu"], r["morse_euler"]))
    sure = time.perf_counter() - t0
    s = ["", "=== PADİŞAH HÜKÜM -- %s (%d görev) ===" % (kume, len(gorevler)),
         "", "  konuştu      : %d" % konustu,
         "  TAM ÇÖZDÜ    : %d  (%%%.1f)"
         % (tam, 100.0 * tam / max(len(gorevler), 1)),
         "  yanlış cevap : %d" % yanlis,
         "  sustu        : %d" % (len(gorevler) - konustu),
         "  süre         : %.1f sn" % sure, "", "  SÜKÛT SEBEPLERİ:"]
    for k, v in sorted(sebep.items(), key=lambda x: -x[1]):
        s.append("    %-46s %d" % (k, v))
    if cozulen:
        s += ["", "  TAM ÇÖZÜLENLER (sırf öğrenilen ağırlıklardan):"]
        s += ["    " + x for x in cozulen]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    agirlik = sys.argv[1] if len(sys.argv) > 1 else \
        "depo/kulli_dimag_agirlik.npy"
    kume = sys.argv[2] if len(sys.argv) > 2 else "evaluation"
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    esik = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    print(degerlendirme_kosusu(agirlik if os.path.isfile(agirlik) else None,
                               kume, n, esik))
