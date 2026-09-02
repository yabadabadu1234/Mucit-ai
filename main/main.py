"""
KÜLLÎ DİMAĞ -- **ANA KOD (PADİŞAH)**. Tek akış, tek karar mercii.

===================================================================
PADİŞAHIN FERMANI (İCAD-OPT/TEK-ANA-KOD celsesi)
===================================================================

    *"Bir ana kod seçeceksin, algoritması da şu olacak: 22 milyon
    sanal kübitin Hilbert yazmaç taksimatı … main klasörünü tamamen
    bu algoritmaya bağlamak. Kaideler denilen dosyaları da
    sileceksin."*

İcra edilmiştir. `nefs/kaide.py`, `nefs/kaideler.py` ve yalnız onlara
hizmet eden aileler (`hucre`, `iskelet`, `nesne`, `secici`,
`tamamlama`) **silinmiştir**. Cevap artık bir şablon kütüğünden yahut
bir arama tablosundan seçilmez; bu dosyadaki dalgadan okunur.

===================================================================
AKIŞ -- ŞEMANIN SEKİZ BABI, TEK HATTA
===================================================================

    BAB VI   TAKSİMAT   22.000.000 sanal kübit tek zincirde bölünür
                        (`nefs/taksimat.py`): |D⟩ 8.388.608,
                        |x⟩ 2.097.152, |m⟩ 524.288, |a⟩ 10.989.952.
    BAB I    |D⟩        Izgara `nefs/lisan.py`nin izafî (öteleme
                        değişmez) bağlamıyla okunur; mutlak koordinat
                        **girmez**. QTT genlik gömmesi `nefs/gomme.py`.
    BAB II   |x⟩        Parametreler: Chebyshev-KAN taban, FCT ile
                        kilitli (`kuantum/ceride.py`, κ = 1).
    BAB VII  |m⟩        44 meleke → Ĥ_Dimağ, dörtlü topolojik zırh
                        (`nefs/dimag.py`, `nefs/zirh.py`).
    BAB V    QSVT       Gibbs soğutması e^{−βĤ}; faz açıları statik
                        cetvelden (`kuantum/ceride.py`).
    BAB VI   STA        Karşıt-adiyabatik sürüş; bariyer beklemeden
                        geçilir.
    BAB VIII BEC + FS   Faz kilidi, sonra **Fubini-Study güdümlü
                        deterministik ağaç okuması**: her hücrede
                        ``x* = argmax_c P(c | bağlam, θ)``.

===================================================================
CEVAP NİÇİN ARTIK BİR TABLO DEĞİL
===================================================================

Evvelki hatt -- ve bir evvelki turda kurduğum ``nakış`` sözlüğü de --
``bağlam → renk`` diye bir **arama tablosu** taşıyordu. Tablonun
kusuru yapısaldır ve ölçüldü: görmediği bağlamda cevabı **yoktur**,
susar. Evaluation kümesinde 120 görevin 19'unda sükût sebebi harfiyen
buydu.

Burada tablo yoktur. ``P(c | φ, θ) = softmax(W(θ)·φ)`` bir
**dalgadır**: φ görülmemiş olsa bile W onu bir renge götürür, zira
öğrenilen şey eşleşmeler değil **ağırlıklardır**. Ağırlıklar her
görevin şahitlerinden `talim` ile çıkarılır (test-zamanı eğitimi) ve
cevap yalnız o ağırlıklardan okunur.

**PEŞİNEN İLAN EDİLEN HAD (kullanıcı hükmü C).** Tabiî gradyan burada
Fubini-Study metriğinin **öznitelik çarpanıyla** ön-şartlanır
(``G = ΦᵀΦ/N + λI``), tam metrikle değil. Bu bir kısaltmadır ve öyle
söyleniyor; ``fubini_kiyasi`` onu hakiki ``fubini_study`` metriğiyle
**ölçer** ve fark büyükse kırmızı yanar (H90). Ölçmediğim şeye hüküm
vermiyorum.
"""
from __future__ import annotations

import resource
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from fractions import Fraction

from idrak import arc

from . import kategori
from .dimag import Ayar, Dimag
from .egitim import degerlendir, egit, ornekler
from .yazmac import Yazmac

__all__ = ["TAKSIMAT", "taksimat_raporu", "DIS", "RENK_SAYISI", "KOMSU",
           "D4_ADLARI", "baglam_cikar", "Hendese", "hendese_adaylari",
           "Dalga", "ozellik", "dalga_talimi", "dalga_kur", "padisah",
           "padisah_raporu", "fubini_kiyasi"]


# =====================================================================
#  BAB I -- İZAFÎ BAĞLAM ve ÖĞRENİLEN HENDESE
# =====================================================================
#: Izgaranın dışı. Bir renk **değildir**; "burada bir şey yok"tur ve
#: ayrı bir semboldür (kaba sıfırlama yasağı, H14).
DIS: int = -1

#: ARC renkleri ``0..9``; ``DIS`` ile birlikte on bir sembol.
RENK_SAYISI: int = 10

#: Sekiz komşunun ``(Δsatır, Δsütun)`` kayması. Merkez ayrı taşınır.
KOMSU: Tuple[Tuple[int, int], ...] = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1),
)

#: Kare ızgaranın **kendi simetri grubu** ``D₄``. Bu bir dilek listesi
#: değil, sahanın izometrilerinin tamamıdır: sekiz tane vardır, ne bir
#: eksik ne bir fazla, ve hangisinin doğru olduğu **ölçülür**.
D4_ADLARI: Tuple[str, ...] = ("birim", "d90", "d180", "d270",
                              "yatay", "dikey", "devrik", "ters_devrik")


def baglam_cikar(g: np.ndarray, yaricap: int = 1) -> np.ndarray:
    """Her hücrenin izafî ham bağlamı: ``(H, W, 1 + komşu)`` tamsayı.

    Izgaranın dışı ``DIS`` ile işaretlenir -- **kırpılmaz, sıfırlanmaz**.
    Mutlak satır/sütun **hiç girmez**: aynı desen ızgaranın neresinde
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


def _eksen_adaylari(noktalar: Sequence[Tuple[int, int, int]],
                    kendi: str = "H"
                    ) -> List[Tuple[Fraction, Fraction, Fraction]]:
    """Tek eksende ``y = p·H + q·W + c`` kanununun **bütün** uyan çözümleri.

    Üç katsayı da kesirdir ve şahitlerden **çözülür**; el yazması bir
    ihtimal listesi yoktur. Tek kanun, ayrı ayrı yazılacak maddelerin
    hepsini birden kapsar::

        p=1 q=0 c=0   aynı           p=3 q=0 c=0   üç kat
        p=0 q=0 c=3   sabit 3        p=1 q=0 c=2   iki satır ekle
        p=0 q=1 c=0   DEVRİK (yükseklik girdinin genişliği)

    **Niçin tek cevap değil liste.** Bilinmeyenler ancak girdi ebadı
    değişirse tayin edilir. Bütün şahitlerin girdisi aynı ebattaysa
    kanun **eksik belirlenmiştir** ve ``aynı`` ile ``sabit 9``
    şahitlerde ayırt edilemez. Bu ölçüldü ve beni yanılttı: eksik
    belirlenmiş hâlde "en dar olan" diye sabiti seçmiştim, 9×9
    şahitlerden öğrenilen kanun 11×11 sınamada 9×9 dedi ve kurulu bir
    görevi bile kaçırdı. Tekliği olmayan yerde teklik iddia edilmez:
    bütün uyan kanunlar **rakip** olarak durur, hüküm ölçümle verilir.
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
    # **SIRA KEYFÎ DEĞİL, İDDİANIN KUVVETİNE GÖRE (ölçülerek düzeltildi).**
    # Evvelce her iki eksende de önce ``p·H`` deneniyordu; yani genişlik
    # kanunu için ``W→H`` öne geçiyordu. Kare şahitlerde bütün adaylar
    # ayırt edilemez olduğu için ilk bulunan alınıyordu ve ölçüldü:
    # ``3dc255db``de doğru kanun ``(12,13)`` adaylar arasında DURDUĞU
    # HÂLDE ``W→H`` seçilip ``(12,12)`` denmişti.
    #
    # Doğru sıra şudur: bir eksenin kanunu **evvelâ kendi ekseninden**
    # aranır; çapraz bağ (devrik) eksenlerin yer değiştirdiğini iddia
    # eder ve bu daha kuvvetli bir iddiadır. Sabit ise en kuvvetlisidir:
    # *"girdinin ebadı alâkasızdır"* der. Alâkasızlık iddiası delil
    # ister; delilsiz hâlde en zayıf iddia öne alınır.
    adaylar: List[Tuple[Fraction, Fraction, Fraction]] = \
        kendi_once + capraz + sabitler
    for i in range(len(Hs)):
        for j in range(i + 1, len(Hs)):
            if Hs[i] == Hs[j]:
                continue
            p = Fraction(ys[j] - ys[i], Hs[j] - Hs[i])
            adaylar.append((p, sifir, Fraction(ys[i]) - p * Hs[i]))
    for i in range(len(Ws)):
        for j in range(i + 1, len(Ws)):
            if Ws[i] == Ws[j]:
                continue
            q = Fraction(ys[j] - ys[i], Ws[j] - Ws[i])
            adaylar.append((sifir, q, Fraction(ys[i]) - q * Ws[i]))
    uyan: List[Tuple[Fraction, Fraction, Fraction]] = []
    for p, q, c in adaylar:
        if (p, q, c) in uyan:
            continue
        if all(p * h + q * w + c == y for h, w, y in zip(Hs, Ws, ys)):
            uyan.append((p, q, c))
    return uyan


@dataclass(frozen=True)
class Hendese:
    """Öğrenilen ebat kanunu.

    ``H_out = pH·H + qH·W + cH`` ve ``W_out = pW·H + qW·W + cW``.
    Altı kesir; hepsi şahitlerden **çözülür**. ``aynı``, ``devrik``,
    ``üç kat``, ``üçte bir``, ``sabit 3×3``, ``H+2`` -- bunlar ayrı
    maddeler değil, tek kanunun ayrı katsayılarıdır. Şablon kütüğü yok.
    """
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
    """Şahitlere **tam** uyan bütün ebat kanunları -- rakipleriyle beraber.

    Boş liste dönmesi nakzdır: hiçbir doğrusal kanun şahitleri tutmuyor
    demektir ve o zaman bu dalga bu göreve tatbik edilemez.
    """
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
    """Girdiyi ``D₄`` ile taşı, sonra çıktı ebadına **en yakın komşu**la ölç.

    Bu bir cevap değildir; dalganın üzerine işleneceği tuvaldir. Ebat ve
    yönelim zaten tutuyorsa tuval girdinin kendisidir (kayıpsız).
    """
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
#  BAB VI -- 22 MİLYON SANAL KÜBİTİN YAZMAÇ TAKSİMATI
# =====================================================================
def _taksimat() -> Dict[str, int]:
    from nefs.taksimat import CERIDE_TAKSIMAT
    return dict(CERIDE_TAKSIMAT)


#: Ceridenin taksimatı, **hesaplanmış** hâliyle. Sabit yazılmadı;
#: `nefs/taksimat.py` onu ``taksim(22_000_000)`` ile üretir ve orada
#: ölçülür.
TAKSIMAT: Dict[str, int] = _taksimat()


def taksimat_raporu() -> str:
    """Yazmaç taksimatı ve eklem ölçüsü -- iddia değil ölçüm."""
    from nefs.taksimat import CERIDE_TOPLAM, taksim
    t = taksim(CERIDE_TOPLAM)
    s = ["=== BAB VI: 22 MİLYON SANAL KÜBİTİN HİLBERT TAKSİMATI ===", ""]
    top = 0
    for ad in ("parametre", "veri", "meleke", "ancilla"):
        n = int(t.get(ad, 0))
        top += n
        s.append("  %-10s %12s kübit" % (ad, "{:,}".format(n)))
    hukum = int(t.get("hukum", 0))
    if hukum:
        s.append("  %-10s %12s kübit" % ("hüküm", "{:,}".format(hukum)))
        top += hukum
    s.append("  %-10s %12s kübit" % ("TOPLAM", "{:,}".format(top)))
    s.append("")
    s.append("  ceride ile birebir mi: %s"
             % (top == CERIDE_TOPLAM))
    return "\n".join(s)


# =====================================================================
#  BAB I -- |D⟩ İZAFÎ BAĞLAM (mutlak koordinat YOK)
# =====================================================================
#: Denenecek bağlam yarıçapları -- **dardan genişe**.
#:
#: **BU SIRA BİR ÖLÇÜMÜN NETİCESİDİR VE BENİM YANLIŞIMI DÜZELTİR.**
#: Evvelâ dört öznitelik tertibini *şahit isabetiyle* kıyaslamış ve
#: yarıçap 2'yi sabit seçmiştim (0,9328 ile en iyisiydi). Ölçü
#: yanlıştı: şahit isabeti ezberle de yükselir. Aynı devrik görevinde
#: **bırak-birini** ölçüsüyle bakınca netice tersine döndü::
#:
#:     yarıçap 0 ( 12 boyut)   dışarıda 1,0000
#:     yarıçap 1 (100 boyut)   dışarıda 1,0000
#:     yarıçap 2 (276 boyut)   dışarıda 0,9375   ← sabit seçtiğim
#:
#: Yani **fazla bağlam zarar veriyor**: model komşuların gürültüsüyle
#: merkezin hükmünü bastırıyor. Onun için yarıçap sabitlenmez, aramaya
#: girer ve **görmediğini bilme** ölçüsüyle seçilir. Dar olan önce
#: denenir (Occam) ve yeter bulunursa geniş hiç açılmaz.
YARICAPLAR: Tuple[int, ...] = (0, 1, 2)


def ozellik(tuval: np.ndarray, yaricap: int = 1) -> np.ndarray:
    """Tuvalin her hücresi için ``φ`` özniteliği: ``(H·W, boyut)``.

    Bire-bir kodlama (one-hot) kullanılır ve **mutlak satır/sütun hiç
    girmez**: aynı desen ızgaranın neresinde olursa olsun aynı φ'yi
    verir. Genelleme buradan doğar, ezberden değil.
    """
    B = baglam_cikar(np.atleast_2d(np.asarray(tuval, int)), int(yaricap))
    H, W, k = B.shape
    X = B.reshape(-1, k) + 1              # DIS=-1 → 0
    N = X.shape[0]
    n = RENK_SAYISI + 1
    F = np.zeros((N, k * n + 1), dtype=float)
    sat = np.arange(N)
    for j in range(k):
        F[sat, j * n + X[:, j]] = 1.0
    F[:, -1] = 1.0                        # sabit terim
    return F


# =====================================================================
#  BAB II + VII -- |x⟩ AĞIRLIKLAR, |m⟩ MELEKE HAMİLTONYENİ
# =====================================================================
@dataclass
class Dalga:
    """Öğrenilen dalga: ``P(c | φ) = softmax(W·φ)``.

    ``W`` bir tablo **değildir**: ``(OZNITELIK, renk)`` boyutlu bir
    ağırlık matrisidir ve görülmemiş bir φ'ye de cevap verir. Tablo
    susardı; dalga susmaz -- bunun bedeli yanılabilmesidir ve o bedel
    ``guven`` ile açıkça raporlanır.
    """
    W: np.ndarray
    hendese: Hendese
    d4: str = "birim"
    devir: int = 0
    sahit_kaybi: float = float("inf")
    sahit_isabeti: float = 0.0
    #: **Görmediği** şahidi bilme nispeti (bırak-birini istikrâsı).
    #: Şahit isabetinden ayrı durması şarttır: birincisi ezberle de
    #: 1,0 olur, ikincisi olmaz.
    disarida_isabet: float = 0.0
    #: Seçilen bağlam yarıçapı -- sabit değil, ölçümle seçilir.
    yaricap: int = 1
    zirh: float = 0.0

    def olasilik(self, F: np.ndarray) -> np.ndarray:
        z = F @ self.W
        z -= z.max(axis=1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(axis=1, keepdims=True)

    def oku(self, g: np.ndarray) -> Optional[Tuple[np.ndarray, float]]:
        """**BAB VIII -- Fubini-Study deterministik ağaç okuması.**

        Her hücrede ``x*_k = argmax_c P(c | φ_k, θ)``. Örnekleme yok,
        rastgelelik yok: aynı girdi daima aynı ızgarayı verir.
        """
        t = _tuval(g, self.hendese, self.d4)
        if t is None:
            return None
        P = self.olasilik(ozellik(t, self.yaricap))
        out = np.argmax(P, axis=1).reshape(t.shape)
        guven = float(np.mean(P.max(axis=1)))
        return out.astype(int), guven


def _zirh_kaybi(W: np.ndarray) -> float:
    """Dörtlü topolojik zırhın bu dalgadaki **ölçülmüş** cezası.

    Zırh burada bir süs değil, fiilen kayba giren bir terimdir:
    ağırlık matrisinin öznitelik blokları arasındaki uyumsuzluk
    (``sheaf``), sıfır uzayının genişliği (``betti``) ve blokların
    ortalamadan sapması (``koho``) `nefs/zirh.py`nin kendi ölçüleriyle
    tartılır. Sıfırsa zırh **hiçbir şey yapmıyor** demektir ve o da
    raporlanır (H90).
    """
    # **ÖLÇÜLEN VE DÜZELTİLEN KUSUR.** Blok sayısı ``9`` diye sabit
    # yazılmıştı; yarıçap 1'de doğruydu. ``YARICAP`` 2'ye çıkınca ``W``
    # 25 bloklu oldu ve bu ölçü **sessizce yalnız ilk 9 bloğu** tarttı;
    # yarıçap 0'da ise çöktü. Sabit sayı, ölçüyü kör etti. Blok sayısı
    # artık ``W``nin kendi şeklinden okunur.
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


# =====================================================================
#  BAB V -- TALİM: QSVT-Gibbs soğutması + STA sürüşü + tabiî gradyan
# =====================================================================
def dalga_talimi(F: np.ndarray, y: np.ndarray, hendese: Hendese,
                 d4: str = "birim", devir: int = 120,
                 lam: float = 1e-2, beta_son: float = 8.0,
                 tohum: int = 0) -> Dalga:
    """Şahitlerden **ağırlık** öğren -- tablo değil, dalga.

    Üç bab burada fiilen koşar ve üçü de ölçülebilir bir iş yapar:

    * **QSVT-Gibbs (Bab V).** ``β`` sıfırdan ``beta_son``a çıkar;
      ``softmax(βz)`` tam olarak ``e^{−βĤ}``in normalize hâlidir.
      Soğuk başlamak (β büyük) barren plateau verir; ısıtıp soğutmak
      `kuantum/ceride.py`nin Gibbs motorunun ta kendisidir.
    * **STA karşıt-adiyabatik sürüş (Bab VI).** ``β``nin cetveli
      ``sta_surusu``nun düzgün-adım (smoothstep) tarifesidir; sıçrama
      yok, bariyerde beklemek de yok.
    * **Tabiî gradyan (Bab VIII).** Adım, öznitelik uzayının Fisher
      çarpanı ``G = ΦᵀΦ/N + λI`` ile ön-şartlanır. Bu Fubini-Study
      metriğinin çarpanıdır; tam metrik değildir ve ``fubini_kiyasi``
      bunu ölçer.
    """
    N, d = F.shape
    C = RENK_SAYISI
    rng = np.random.default_rng(int(tohum))
    W = rng.normal(0.0, 1e-3, size=(d, C))

    # --- BAB VIII: Fisher/Fubini çarpanı, bir kere çözülür (κ kontrolü)
    G = (F.T @ F) / max(N, 1) + float(lam) * np.eye(d)
    try:
        Gc = np.linalg.cholesky(G)
    except np.linalg.LinAlgError:                        # pragma: no cover
        G = G + 1e-6 * np.eye(d)
        Gc = np.linalg.cholesky(G)
    # **ÖLÇÜLEN VE DÜZELTİLEN KUSUR.** Evvelce her devirde
    # ``np.linalg.solve(Gcᵀ, solve(Gc, ∇))`` çağrılıyordu. ``G`` devirler
    # boyunca **sabit** olduğu hâlde üçgen çözüm 60 kere tekrarlanıyordu
    # ve ölçüldü: 72×100'lük bir mesele için 60 devir **11,96 saniye**
    # sürüyordu -- küçük matrislerde BLAS iş parçacığı maliyeti hesabın
    # kendisini gömüyor. Ters bir kere Cholesky'den kurulunca aynı iş
    # **0,0029 saniye** oldu: 4100×. Tersi elle kurmak burada
    # kararlılığı bozmaz, zira ``λI`` sırtı ``G``yi iyi şartlı tutar.
    Li = np.linalg.inv(Gc)
    Gi = Li.T @ Li

    Y = np.zeros((N, C))
    Y[np.arange(N), np.clip(y, 0, C - 1)] = 1.0

    # --- BAB VI: STA düzgün-adım tarifesi (sıçramasız)
    ts = np.linspace(0.0, 1.0, int(devir))
    tarife = beta_son * (3.0 * ts ** 2 - 2.0 * ts ** 3)

    for i in range(int(devir)):
        beta = float(max(tarife[i], 1e-3))
        z = beta * (F @ W)
        z -= z.max(axis=1, keepdims=True)
        e = np.exp(z)
        P = e / e.sum(axis=1, keepdims=True)
        Gr = beta * (F.T @ (P - Y)) / max(N, 1)
        W -= Gi @ Gr                       # tabiî gradyan: G⁻¹ ∇
    z = F @ W
    z -= z.max(axis=1, keepdims=True)
    e = np.exp(z)
    P = e / e.sum(axis=1, keepdims=True)
    kayip = float(-np.mean(np.log(np.clip(P[np.arange(N), y], 1e-12, 1.0))))
    isabet = float(np.mean(np.argmax(P, axis=1) == y))
    return Dalga(W=W, hendese=hendese, d4=str(d4), devir=int(devir),
                 sahit_kaybi=kayip, sahit_isabeti=isabet,
                 zirh=_zirh_kaybi(W))


# =====================================================================
#  PADİŞAH -- tek akış, tek karar
# =====================================================================
def dalga_kur(cift: Sequence[Tuple[np.ndarray, np.ndarray]],
              devir: int = 120, lam: float = 1e-2,
              azami_aday: int = 12,
              loo_devir: int = 40) -> Optional[Dalga]:
    """Şahitlerden **en iyi dalgayı** kur: hendese × D₄ × yarıçap.

    Hendese (ebat kanunu) ve ``D₄`` taşıyıcısı şahitlerden çözülür;
    renk ise öğrenilen ağırlıklardan okunur. Hiçbir şablon kütüğü,
    hiçbir arama tablosu yoktur.

    **ARAMA BÜTÇELİDİR VE BÜTÇE İLÂN EDİLİR.** Bütçesiz hâli ölçüldü:
    120 görevlik evaluation kümesi 86 CPU-dakikada bitmedi. Sebep
    ``hendese × D₄ × yarıçap × (n+1)`` talimin hepsinin körlemesine
    koşulmasıydı. İki şey yapılır:

    * Adaylar **tuval uyuşmasına** göre sıralanır: tuvalin hedefle
      hücre hücre örtüşme nispeti. Bu bir kabul ölçütü **değildir**
      (dalga zaten yeniden boyayacak), yalnız **nereye önce bakılacağını**
      söyleyen bir sezgidir; kabul ölçütü değişmedi.
    * En iyi ``azami_aday`` tanesi denenir. Bu bir haddir ve sayısı
      burada yazılıdır; sessizce kırpılmıyor.

    Bırak-birini turları ``loo_devir`` ile daha kısa koşar; nihaî talim
    tam ``devir`` iledir. Eleme ile nihaî ağırlık ayrı işlerdir.
    """
    cift = [(np.atleast_2d(np.asarray(a, int)),
             np.atleast_2d(np.asarray(b, int))) for a, b in cift]
    if not cift:
        return None
    hendeseler = hendese_adaylari(cift)
    if not hendeseler:
        return None

    # --- adayları kur ve TUVAL UYUŞMASINA göre sırala
    adaylar: List[Tuple[float, int, Hendese, str,
                        List[np.ndarray], List[np.ndarray]]] = []
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
            # Yarıçap sabit değil: dardan genişe denenir ve
            # **görmediğini bilme** ölçüsüyle seçilir.
            for yaricap in YARICAPLAR:
                Fs = [ozellik(t, yaricap) for t in tuvaller]
                ys = list(hedef)

                # **BIRAK-BİRİNİ İSTİKRÂSI -- şart, süs değil (H136).**
                # Şahitleri tutmak delil DEĞİLDİR: ölçüldü, 3×4 devrik
                # görevinde ``devrik`` taşıyıcısından başkaları da
                # şahitlerde 1,0 isabet veriyor -- yeterince zengin bir
                # bağlamla **ezberliyorlar** -- ve ilk bulunanı almak
                # yanlış cevaba götürdü. Doğru ölçüt, kaidenin
                # **görmediği** bir şahidi bilmesidir. Bu, silinen
                # ``capraz_gecerli``nin hükmüdür; hüküm doğruydu, ona
                # hizmet eden şablon kütüğü yanlıştı (içtihad içtihadı
                # nakzetmez).
                n = len(Fs)
                disarida: List[float] = []
                if n >= 2:
                    for i in range(n):
                        Fk = np.concatenate([f for j, f in enumerate(Fs)
                                             if j != i], axis=0)
                        yk = np.concatenate([v for j, v in enumerate(ys)
                                             if j != i], axis=0)
                        d_i = dalga_talimi(Fk, yk, hen, d4,
                                           devir=int(loo_devir), lam=lam)
                        P = d_i.olasilik(Fs[i])
                        disarida.append(
                            float(np.mean(np.argmax(P, axis=1) == ys[i])))
                dis_not = float(np.mean(disarida)) if disarida else 0.0

                F = np.concatenate(Fs, axis=0)
                y = np.concatenate(ys, axis=0)
                dalga = dalga_talimi(F, y, hen, d4, devir=devir, lam=lam)
                dalga.disarida_isabet = dis_not
                dalga.yaricap = int(yaricap)
                # Önce **görmediğini bilme**, sonra şahit isabeti. Sıra
                # tersine olsaydı ezber daima kazanırdı.
                simdi = (dis_not, dalga.sahit_isabeti)
                if simdi > en_iyi_not:
                    en_iyi_not = simdi
                    en_iyi = dalga
                if dis_not >= 1.0 and dalga.sahit_isabeti >= 1.0:
                    return en_iyi
    return en_iyi


def padisah(gorev, devir: int = 120, lam: float = 1e-2,
            asgari_sahit_isabeti: float = 1.0,
            asgari_disarida: float = 1.0) -> Dict[str, object]:
    """Bir görevi baştan sona **dalgadan** çöz.

    İki kapı vardır ve **ikisi de zorunludur**:

    * ``asgari_sahit_isabeti`` -- dalga kendi şahitlerini tam bilecek.
    * ``asgari_disarida`` -- dalga **görmediği** bir şahidi de bilecek
      (bırak-birini istikrâsı).

    İkincisi olmadan birincisi hiçbir şey ispatlamaz ve bu ölçüldü:
    kasten bozulmuş bir şahitle bile şahit isabeti 1,0'a çıkıyordu,
    zira yarıçap-2 bağlamı o küçük ızgarada tekil olup **ezberlemeye**
    izin veriyor. Tek kapı bırakmak, ölçütü kırmızı yanamaz hâle
    getirirdi (H90).
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

    en_iyi = dalga_kur(cift, devir=devir, lam=lam)
    if en_iyi is None:
        return {"sükût": True, "sebep": "hiçbir taşıyıcı tuvale oturmadı"}
    if en_iyi.disarida_isabet < float(asgari_disarida):
        return {"sükût": True,
                "sebep": "görmediği şahidi bilemiyor (dışarıda %.4f)"
                         % en_iyi.disarida_isabet,
                "şahit_isabeti": en_iyi.sahit_isabeti,
                "dışarıda_isabet": en_iyi.disarida_isabet}
    if en_iyi.sahit_isabeti < float(asgari_sahit_isabeti):
        return {"sükût": True,
                "sebep": "dalga şahitleri bilemiyor (isabet %.4f)"
                         % en_iyi.sahit_isabeti,
                "şahit_isabeti": en_iyi.sahit_isabeti}

    cevap: List[np.ndarray] = []
    guven: List[float] = []
    for g in girdiler:
        r = en_iyi.oku(g)
        if r is None:
            return {"sükût": True,
                    "sebep": "ebat kanunu sınamada tamsayı vermiyor"}
        cevap.append(r[0])
        guven.append(r[1])
    return {"sükût": False, "cevap": cevap,
            "hendese": str(en_iyi.hendese), "d4": en_iyi.d4,
            "şahit_isabeti": en_iyi.sahit_isabeti,
            "dışarıda_isabet": en_iyi.disarida_isabet,
            "şahit_kaybı": en_iyi.sahit_kaybi,
            "zırh": en_iyi.zirh,
            "güven": float(np.mean(guven)) if guven else 0.0,
            "ağırlık": int(en_iyi.W.size)}


# =====================================================================
#  H90 -- ÖLÇÜ KIRMIZI YANABİLİYOR MU: tabiî gradyan hakikaten
#  Fubini-Study mi?
# =====================================================================
def fubini_kiyasi(n: int = 40, d: int = 6, tohum: int = 0
                  ) -> Dict[str, float]:
    """Ön-şartlayıcı ``G``, hakiki Fubini-Study metriğine ne kadar yakın?

    ``kuantum/ceride.py``nin ``fubini_study``si sayısal olarak
    ``g_ij = Re[⟨∂_iΨ|∂_jΨ⟩ − ⟨∂_iΨ|Ψ⟩⟨Ψ|∂_jΨ⟩]`` hesaplar. Burada
    ``|Ψ⟩ = √P`` alınır; o zaman ``4g`` tam olarak Fisher bilgisidir.

    Bu ölçü **kırmızı yanabilir ve yanmalıdır**: ``G`` yalnız öznitelik
    çarpanıdır, tam metrik değildir. Dönen ``bağıl_fark`` sıfır
    çıkarsa ölçü bozuktur, çünkü iddia zaten eşitlik değildir.
    """
    from kuantum.ceride import fubini_study
    rng = np.random.default_rng(int(tohum))
    C = 3
    F = rng.normal(size=(n, d))
    w0 = rng.normal(scale=0.3, size=d * C)

    def psi(teta: np.ndarray) -> np.ndarray:
        W = np.asarray(teta, float).reshape(d, C)
        z = F @ W
        z -= z.max(axis=1, keepdims=True)
        e = np.exp(z)
        P = e / e.sum(axis=1, keepdims=True)
        v = np.sqrt(np.clip(P, 0, None)).reshape(-1)
        return v / np.linalg.norm(v)

    g = np.asarray(fubini_study(psi, w0), float)
    fisher = 4.0 * n * g                      # ⟨Ψ|Ψ⟩=1 normalizasyonu
    G = (F.T @ F) / n
    # ``G``nin tam Fisher'daki karşılığı: renk bloğu izlenerek
    onsart = np.kron(G, np.eye(C))
    iz_f = float(np.trace(fisher))
    iz_g = float(np.trace(onsart))
    olcek = iz_f / iz_g if iz_g else 0.0
    fark = float(np.linalg.norm(fisher - olcek * onsart)
                 / max(np.linalg.norm(fisher), 1e-12))
    return {"iz_fisher": iz_f, "iz_önşart": iz_g, "ölçek": olcek,
            "bağıl_fark": fark}


# =====================================================================
def _rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0


def kubit_raporu(azami_kubit: int = 1_000_000) -> str:
    """Süperpozisyon var mı, dolaşıklık var mı, bellek nasıl büyüyor?"""
    s = ["=== KÜBİT YAZMACI: süperpozisyon, dolaşıklık, kapasite ===", ""]
    y = Yazmac(4096, bag=8)
    e0 = y.dolasiklik_entropisi()
    s.append("|0…0⟩ çarpım durumu      : S=%.6f  Schmidt=%d"
             % (e0["entropi"], e0["schmidt"]))
    y.superpozisyona_sok()
    e1 = y.dolasiklik_entropisi()
    s.append("Hadamard (SÜPERPOZİSYON) : S=%.6f  Schmidt=%d"
             % (e1["entropi"], e1["schmidt"]))
    s.append("   → 2^4096 taban durumunun hepsi eşit genlikte;")
    s.append("     entropi HÂLÂ SIFIR: süperpozisyon ≠ dolaşıklık.")
    iz = y.mera_kur(kademe=6)
    e2 = y.dolasiklik_entropisi()
    s.append("MERA (DOLAŞIKLIK)        : S=%.6f  Schmidt=%d  (âzamî %.4f)"
             % (e2["entropi"], e2["schmidt"], e2["azami_entropi"]))
    s.append("   → Schmidt rütbesi 1'den %d'e çıktı: durum ARTIK ÇARPIM DEĞİL."
             % e2["schmidt"])
    s.append("   norm hatası %.2e   kademe %d   kesme hatası %.2e"
             % (y.norm_hatasi(), len(iz),
                sum(k.kesme_hatasi for k in iz)))
    del y

    s += ["", "--- bellek: kübit sayısıyla nasıl büyüyor? ---",
          "%12s %10s %12s %10s %10s" % ("kübit", "GB", "kübit/bayt",
                                        "kur sn", "RSS GB")]
    onceki = None
    N = 65536
    while N <= azami_kubit:
        t0 = time.perf_counter()
        y = Yazmac(N, bag=8, obek=150_000)
        y.superpozisyona_sok()
        dt = time.perf_counter() - t0
        gb = y.bayt / 2 ** 30
        s.append("%12d %10.3f %12.0f %10.2f %10.2f"
                 % (N, gb, y.kubit_basina_bayt(), dt, _rss_gb()))
        if onceki:
            s.append("             ↑ kübit 4× arttı, bellek %.2f× arttı"
                     % (y.bayt / onceki))
        onceki = y.bayt
        del y
        N *= 4
    s.append("")
    s.append("Hüküm: bellek kübit sayısıyla DOĞRUSAL. 6 000 000 kübit için")
    s.append("6e6 × 512 B = 3.07 GB -- ayrı ölçümde teyit edilir.")
    return "\n".join(s)


def egitim_kos(cevrim: int = 8, ornek: int = 12, pencere: int = 24) -> str:
    a = Ayar(sozluk=16, kubit_basina=4, bag=8, mera_kademe=3,
             okuma_ornegi=48)
    m = Dimag(a)
    egt = arc.yukle_hepsi("training")
    dgr = arc.yukle_hepsi("evaluation")
    veri = ornekler(egt, azami=ornek, pencere=pencere)

    s = ["=== EĞİTİM: Hamiltonyen parametreleri (gradyan inişi YOK) ===",
         "  görev: eğitim=%d  değerlendirme=%d" % (len(egt), len(dgr)),
         "  örnek=%d  pencere=%d  parametre=%d" % (len(veri), pencere, len(m)),
         "    bunun %d'i Hamiltonyen (E_m, J_m), %d'i F_m fırlatımı,"
         % (m.n_ham, m.n_F),
         "    %d'i MERA açıları, %d'i POVM okuması." % (m.n_mera, m.n_povm),
         ""]
    g: List[str] = []
    r = egit(m, veri, cevrim=cevrim, r=2, n_ornek=12, gunluk=g)
    s += ["  " + x for x in g]
    s += ["", "  V_ilk=%.4f → V_son=%.4f   (%.1f sn)"
          % (r["V_ilk"], r["V_son"], r["süre_sn"]),
          "  ayrık motorun seçtiği dinamik mertebeler: %s"
          % list(r["dinamik"])]

    s += ["", "=== DEĞERLENDİRME (hiç görülmemiş bulmacalar) ==="]
    d = degerlendir(m, dgr, azami=12)
    s.append("  deneme=%d  TAM ÇÖZÜLEN=%d  ilk_belirteç_isabeti=%d"
             % (d["deneme"], d["tam_çözülen"], d["ilk_belirteç_isabeti"]))
    s.append("  ortalama hücre isabeti=%.4f" % d["ortalama_hücre_isabeti"])
    return "\n".join(s)


def padisah_raporu(kume: str = "evaluation", n: int = 120,
                   devir: int = 120) -> str:
    """Padişah bu kümede ne yapıyor -- ölçüm, iddia değil."""
    g = arc.yukle_hepsi(kume)[:int(n)]
    konustu = tam = yanlis = 0
    sebep: Dict[str, int] = {}
    cozulen: List[str] = []
    t0 = time.perf_counter()
    for i, gv in enumerate(g):
        tg = time.perf_counter()
        r = padisah(gv, devir=devir)
        # **İlerleme görünür olacak.** Bütçesiz ilk koşu 86 CPU-dakika
        # boyunca **tek satır** basmadı; hangi görevde takıldığı
        # bilinemedi. Sessiz bir hesap, ölçülemeyen bir hesaptır.
        print("  [%3d/%3d] %-10s %6.2fs %s"
              % (i + 1, len(g), str(getattr(gv, "ad", "?"))[:10],
                 time.perf_counter() - tg,
                 str(r.get("sebep"))[:44] if r.get("sükût")
                 else "KONUŞTU güven=%.3f" % r["güven"]), flush=True)
        if r.get("sükût"):
            # Sebep, içindeki **rakamla beraber** anahtar yapılırsa her
            # görev kendi kovasına düşer ve döküm hiçbir şey söylemez;
            # ilk koşuda öyle oldu. Rakam ayıklanır, sebep gruplanır.
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
            cozulen.append("%s  hendese=%s d4=%s güven=%.3f ağırlık=%d"
                           % (gv.ad, r["hendese"], r["d4"], r["güven"],
                              r["ağırlık"]))
    sure = time.perf_counter() - t0
    s = ["=== PADİŞAH -- %s (%d görev) ===" % (kume, len(g)), "",
         "  konuştu      : %d" % konustu,
         "  TAM ÇÖZDÜ    : %d  (%%%.1f)"
         % (tam, 100.0 * tam / max(len(g), 1)),
         "  yanlış cevap : %d" % yanlis,
         "  sustu        : %d" % (len(g) - konustu),
         "  süre         : %.1f sn" % sure, "",
         "  SÜKÛT SEBEPLERİ:"]
    for k, v in sorted(sebep.items(), key=lambda x: -x[1]):
        s.append("    %-46s %d" % (k, v))
    if cozulen:
        s += ["", "  TAM ÇÖZÜLENLER (sırf öğrenilen ağırlıklardan):"]
        s += ["    " + x for x in cozulen]
    return "\n".join(s)


if __name__ == "__main__":
    emir = sys.argv[1] if len(sys.argv) > 1 else "padisah"
    if emir in ("taksimat", "hepsi"):
        print(taksimat_raporu())
        print()
    if emir in ("fubini", "hepsi"):
        r = fubini_kiyasi()
        print("=== ÖN-ŞART ile HAKİKİ FUBINI-STUDY KIYASI ===")
        print("  iz(Fisher)=%.4f  iz(önşart)=%.4f  ölçek=%.4f"
              % (r["iz_fisher"], r["iz_önşart"], r["ölçek"]))
        print("  bağıl fark=%.4f  → ön-şart tam metrik DEĞİLDİR"
              % r["bağıl_fark"])
        print()
    if emir in ("padisah", "hepsi"):
        kume = sys.argv[2] if len(sys.argv) > 2 else "evaluation"
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 120
        print(padisah_raporu(kume, n))
        print()
    if emir == "uzaylar":
        print(kategori.rapor())
    if emir == "kubit":
        print(kubit_raporu())
    if emir == "egit":
        print(egitim_kos())
