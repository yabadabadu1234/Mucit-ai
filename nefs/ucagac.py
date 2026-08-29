"""
ÜÇ AĞAÇ (H56) ve boyutun ihtimal uzayına girmesi (H62).

Kullanıcı hükümleri:

* **H56** -- her şahidin girdisi ve çıktısı, test girdisi, ve ÇIKTI:
  hepsi ayrı ağaçlardır; şahit ağaçları **kilitli**, çıktı ağacı
  **açıktır**. Tek ağaçta şahitlik diye bir şey olamaz.
* **H62** -- *"boyut girdi çıktı arasında değişiyorsa bu kaideye göre
  değişmiştir, aklın işidir, müşahedenin değil."* Onun için burada
  boyutu tahmin eden bir dağarcık **yoktur**; boyut, ihtimal uzayının
  **içindedir**.

**Boyut ihtimal uzayına nasıl sokuldu.** Hücrenin durum uzayı ``renk``
değil ``renk+1``dir; fazladan hâl ``HARİÇ``tir: *"bu hücre çıktının
dışındadır"*. Böylece:

* çıktı ağacı ``H×W``lik bir çerçevede kurulur (âzamî),
* düzgün süperpozisyonda her hücre ``HARİÇ`` de olabilir, dolu da --
  yani **bütün boyutlar aynı anda askıdadır**,
* bir boyutu seçmek, ayrı bir organın hüküm vermesi değil, çıktı
  ağacına vurulan kapıların ``HARİÇ`` genliğini söndürmesidir.

Boyut böylece dışarıdan verilen bir çerçeve olmaktan çıkıp aklın
söndüre söndüre vardığı bir netice olur.

**Tek durum, çok blok.** Şahitlerle çıktı arasına kapı vurulabilmesi
için hepsinin **aynı** dalga fonksiyonunda olması şarttır; ayrı ayrı
``AgacYazmaci`` nesneleri dolaşıklaşamaz. Onun için bloklar tek bir
ağacın yaprakları olarak dizilir::

    [şahit₁ girdi][şahit₁ çıktı][şahit₂ girdi][şahit₂ çıktı]…
    [test girdi][ÇIKTI]

İlk bloklar kilitli (çarpım hâli, kesin), son blok açık.

**İddia edilmeyen.** Bu dosya bir ARC çözücüsü değildir. Burada kurulan
şey, melekelerin üzerine kapı vuracağı **zemindir**: boyutun ihtimal
uzayında olduğu ölçülür, kapının onu söndürebildiği ölçülür. Hangi
melekenin hangi kapıyı hangi formülle vuracağı henüz kararlaşmamıştır
(𝒪₆, 𝒪₇, 𝒪₉ sualleri cevap beklemektedir) ve uydurulmaz.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .agac import AgacAyar, AgacYazmaci

__all__ = ["UcAgac", "iki_kademeli_donme"]

Izgara = np.ndarray
Cift = Tuple[Izgara, Izgara]


def iki_kademeli_donme(d: int, u: np.ndarray, v: np.ndarray,
                       teta: float) -> np.ndarray:
    """``span{u,v}`` düzleminde ``teta`` kadar dönen, geri kalanda birim
    olan ``d×d`` üniter.

    Genlik söndürmenin **üniter** yolu budur. "Bu ihtimali sıfırla" demek
    ölçüm ister ve çöküş getirir; "bu ihtimalden ötekine ``teta`` kadar
    dön" demek üniterdir ve süperpozisyonu diri tutar. Kütükteki
    "hiçbir meleke okumaz" şartı ancak böyle karşılanır.
    """
    u = np.asarray(u, complex)
    u = u / np.linalg.norm(u)
    v = np.asarray(v, complex) - u * (u.conj() @ np.asarray(v, complex))
    nv = np.linalg.norm(v)
    if nv < 1e-12:
        return np.eye(d, dtype=complex)
    v = v / nv
    c, s = math.cos(teta), math.sin(teta)
    P = np.outer(u, u.conj()) + np.outer(v, v.conj())
    D = (c - 1.0) * P + s * (np.outer(v, u.conj()) - np.outer(u, v.conj()))
    return np.eye(d, dtype=complex) + D


@dataclass
class Blok:
    ad: str
    bas: int                      # büyük ızgaradaki satır başlangıcı
    h: int
    w: int
    kilitli: bool


class UcAgac:
    """Şahitler + test girdisi + AÇIK çıktı: tek dalga, çok blok."""

    def __init__(self, sahitler: Sequence[Cift], test_girdi: Izgara,
                 renk: int = 10, cerceve: Optional[Tuple[int, int]] = None,
                 bag: int = 8) -> None:
        self.renk = int(renk)
        self.d = self.renk + 1
        self.HARIC = self.renk

        izgaralar: List[Izgara] = []
        for a, b in sahitler:
            izgaralar += [np.asarray(a), np.asarray(b)]
        izgaralar.append(np.asarray(test_girdi))
        if cerceve is None:
            H = max(g.shape[0] for g in izgaralar)
            W = max(g.shape[1] for g in izgaralar)
        else:
            H, W = cerceve
        self.H, self.W = int(H), int(W)

        self.bloklar: List[Blok] = []
        for k, (a, b) in enumerate(sahitler):
            self._blok("şahit%d.girdi" % k, np.asarray(a), True)
            self._blok("şahit%d.çıktı" % k, np.asarray(b), True)
        self._blok("test.girdi", np.asarray(test_girdi), True)
        self._blok("ÇIKTI", None, False)

        toplam = len(self.bloklar) * self.H
        self.ag = AgacYazmaci(AgacAyar(h=toplam, w=self.W, renk=self.d,
                                       bag=bag))
        # kilitli blokları yaz -- çarpım hâli, hiçbir yaklaşıklık yok
        for blok, g in zip(self.bloklar, self._izgaralar):
            if blok.kilitli:
                self._yaz(blok, g)
        self.ag.kanonik(self.ag.kok)

    # -----------------------------------------------------------------
    def _blok(self, ad: str, g: Optional[Izgara], kilitli: bool) -> None:
        if not hasattr(self, "_izgaralar"):
            self._izgaralar: List[Optional[Izgara]] = []
        bas = len(self.bloklar) * self.H
        h = g.shape[0] if g is not None else self.H
        w = g.shape[1] if g is not None else self.W
        self.bloklar.append(Blok(ad, bas, h, w, kilitli))
        self._izgaralar.append(g)

    def blok(self, ad: str) -> Blok:
        for b in self.bloklar:
            if b.ad == ad:
                return b
        raise KeyError(ad)

    def hucre(self, blok: Blok, i: int, j: int) -> Tuple[int, int]:
        return (blok.bas + i, j)

    # -----------------------------------------------------------------
    def _yaz(self, blok: Blok, g: Izgara) -> None:
        """Kilitli bloğu ızgaraya sabitle: her yaprak bir taban hâli.

        Çerçevenin dışında kalan hücreler ``HARİÇ``e sabitlenir; yani
        şahitlerin **kendi boyutları** da durumun içindedir, dışarıdan
        tutulan bir sayı değil.
        """
        for i in range(self.H):
            for j in range(self.W):
                c = (int(g[i, j]) if (i < g.shape[0] and j < g.shape[1])
                     else self.HARIC)
                no = self.ag.yaprak_no[self.hucre(blok, i, j)]
                T = np.zeros((self.d, 1), complex)
                T[c, 0] = 1.0
                self.ag.dugumler[no].T = T

    # -----------------------------------------------------------------
    #  Çıktı ağacına vurulan kapılar -- hepsi ÜNİTER, hiçbiri okumaz
    # -----------------------------------------------------------------
    def _dolu_yon(self) -> np.ndarray:
        v = np.ones(self.d, complex) / math.sqrt(self.renk)
        v[self.HARIC] = 0.0
        return v

    def _haric_yon(self) -> np.ndarray:
        v = np.zeros(self.d, complex)
        v[self.HARIC] = 1.0
        return v

    def boyut_kapisi(self, h: int, w: int, teta: float = 0.6) -> int:
        """``h×w`` boyutunu **kayırır**: içeride ``HARİÇ``i, dışarıda
        doluluğu söndürür.

        Bu bir "boyut tahmini" değildir; bir **kanaat kapısıdır**. Aklın
        şahitlerden çıkardığı münasebet buraya bir açı olarak girer;
        ``teta`` büyüdükçe kanaat kuvvetlenir, ``teta=0``da hiçbir şey
        olmaz. Birden çok boyut için birden çok kapı vurulabilir ve
        hepsi aynı anda askıda kalır -- seçim, ölçümde değil, genliktedir.
        """
        cikti = self.blok("ÇIKTI")
        D, X = self._dolu_yon(), self._haric_yon()
        n = 0
        for i in range(self.H):
            for j in range(self.W):
                icinde = (i < h and j < w)
                # içeride HARİÇ → dolu, dışarıda dolu → HARİÇ
                G = (iki_kademeli_donme(self.d, X, D, teta) if icinde
                     else iki_kademeli_donme(self.d, D, X, teta))
                self.ag.tek_kapi(self.hucre(cikti, i, j), G)
                n += 1
        return n

    def renk_kapisi(self, i: int, j: int, c: int, teta: float = 0.6) -> None:
        """Çıktının ``(i,j)`` hücresinde ``c`` rengini kayır."""
        v = np.zeros(self.d, complex)
        v[int(c)] = 1.0
        u = np.ones(self.d, complex)
        u[int(c)] = 0.0
        u = u / np.linalg.norm(u)
        G = iki_kademeli_donme(self.d, u, v, teta)
        self.ag.tek_kapi(self.hucre(self.blok("ÇIKTI"), i, j), G)

    def bag_kapisi(self, sahit_hucre: Tuple[int, int],
                   cikti_hucre: Tuple[int, int], teta: float = 0.4) -> None:
        """Şahit hücresiyle çıktı hücresini **dolaştır** -- H56'nın kalbi.

        Şahit yaprağı kilitli olduğu için bu kapı, o şahidin o hücrede ne
        gördüğünü çıktı hücresine bir **şart** olarak taşır: operatör yol
        boyunca yayılır (ağaç MPO), hiçbir hücre yer değiştirmez.
        """
        d = self.d
        G = np.eye(d * d, dtype=complex).reshape(d, d, d, d)
        # kontrollü dönme: şahit hücresi ``c`` ise çıktıda ``c`` kayrılır
        for c in range(self.renk):
            v = np.zeros(d, complex)
            v[c] = 1.0
            u = np.ones(d, complex)
            u[c] = 0.0
            u = u / np.linalg.norm(u)
            R = iki_kademeli_donme(d, u, v, teta)
            G[:, :, c, :] = 0.0
            G[c, :, c, :] = R
        self.ag.cift_kapi(sahit_hucre, cikti_hucre,
                          G.reshape(d * d, d * d))

    # -----------------------------------------------------------------
    #  Okuma -- yalnız en sonda, zayıf, çöküşsüz
    # -----------------------------------------------------------------
    def doluluk_haritasi(self) -> np.ndarray:
        """Çıktı bloğunun her hücresi için ``P(dolu)`` -- marjinal."""
        cikti = self.blok("ÇIKTI")
        M = np.zeros((self.H, self.W))
        for i in range(self.H):
            for j in range(self.W):
                p = self.ag.hucre_dagilimi(self.hucre(cikti, i, j))
                M[i, j] = float(1.0 - p[self.HARIC])
        return M

    def boyut_kanaati(self, esik: float = 0.5) -> Tuple[int, int]:
        """``P(dolu) > eşik`` olan hücrelerin kaplayacağı dikdörtgen.

        **Bu bir vekil ölçüdür ve öyle bildirilir.** Boyutun hakikî
        dağılımı marjinallerden okunmaz; hücreler dolaşıksa müşterek
        dağılım lazımdır ve o da ancak küçük ızgarada tam büzülerek
        (``buz``) hesaplanabilir. Burada okunan, her hücrenin **kendi**
        dolu olma ihtimalidir; kanaatin nereye kaydığını gösterir,
        boyutun olasılığını vermez.
        """
        M = self.doluluk_haritasi()
        h = int(np.sum(M.max(axis=1) > esik))
        w = int(np.sum(M.max(axis=0) > esik))
        return h, w

    def durum(self) -> Dict[str, float]:
        d = self.ag.durum()
        d["blok"] = float(len(self.bloklar))
        d["çerçeve_h"] = float(self.H)
        d["çerçeve_w"] = float(self.W)
        d["hâl_sayısı"] = float(self.d)
        return d


# =====================================================================
def _gosterim() -> str:
    from idrak import arc

    s = ["=== ÜÇ AĞAÇ (H56) + boyut ihtimal uzayında (H62) ==="]

    gorevler = arc.yukle_hepsi("training")
    secilen = None
    for g in gorevler:
        if (len(g.egitim) >= 2 and g.azami_kenar() <= 5
                and not g.sekil_sabit_mi()):
            secilen = g
            break
    if secilen is None:
        for g in gorevler:
            if len(g.egitim) >= 2 and g.azami_kenar() <= 4:
                secilen = g
                break
    gi, co = secilen.sinama[0]
    u = UcAgac(secilen.egitim[:2], gi, renk=10, bag=8)
    d = u.durum()
    s += ["",
          "görev %s   şahit=%d   çerçeve=%dx%d   hâl/hücre=%d (10 renk + HARİÇ)"
          % (secilen.ad, 2, u.H, u.W, u.d),
          "blok dizilişi: " + " | ".join(b.ad for b in u.bloklar),
          "yaprak=%d  düğüm=%d  derinlik=%d  bellek=%.1f KB"
          % (int(d["yaprak"]), int(d["düğüm"]), int(d["derinlik"]),
             d["bayt"] / 1024.0),
          "hakikî çıktı boyutu (model BİLMİYOR): %dx%d" % co.shape]

    s += ["", "--- 1. Kilitli şahit blokları gerçekten kilitli mi ---"]
    b0 = u.blok("şahit0.girdi")
    a, b = secilen.egitim[0]
    hata = 0.0
    for i in range(min(3, u.H)):
        for j in range(min(3, u.W)):
            p = u.ag.hucre_dagilimi(u.hucre(b0, i, j))
            c = (int(a[i, j]) if i < a.shape[0] and j < a.shape[1]
                 else u.HARIC)
            hata = max(hata, abs(1.0 - float(p[c])))
    s.append("  şahit0 girdi hücrelerinde ‖P−δ‖ âzamî sapma: %.2e" % hata)

    s += ["", "--- 2. Çıktı ağacı açıkken bütün boyutlar askıda mı ---"]
    M = u.doluluk_haritasi()
    s.append("  P(dolu) haritası (düzgün süperpozisyon → hepsi eşit):")
    for i in range(u.H):
        s.append("    " + " ".join("%.3f" % v for v in M[i]))
    s.append("  beklenen: 10/11 = %.3f  (her hücre HARİÇ dahil 11 hâlde)"
             % (10.0 / 11.0))
    s.append("  boyut kanaati: %s  ← hiçbir boyut kayrılmıyor"
             % (u.boyut_kanaati(),))

    s += ["", "--- 3. Kanaat kapısı boyutu söndürebiliyor mu ---",
          "  (buradaki hedef boyut ELLE veriliyor; MEKANİZMA sınanıyor,",
          "   çözüm İDDİA EDİLMİYOR -- hangi melekenin bu açıyı hangi",
          "   formülle vereceği henüz kararlaşmadı)"]
    for teta in (0.3, 0.6, 0.9):
        v = UcAgac(secilen.egitim[:2], gi, renk=10, bag=8)
        n = v.boyut_kapisi(co.shape[0], co.shape[1], teta)
        M = v.doluluk_haritasi()
        ic = [M[i, j] for i in range(co.shape[0]) for j in range(co.shape[1])]
        dis = [M[i, j] for i in range(v.H) for j in range(v.W)
               if not (i < co.shape[0] and j < co.shape[1])]
        s.append("  θ=%.1f  kapı=%d   içeride P(dolu)=%.3f   dışarıda=%.3f"
                 "   kanaat=%s  norm=%.9f"
                 % (teta, n, float(np.mean(ic)),
                    float(np.mean(dis)) if dis else float("nan"),
                    v.boyut_kanaati(), v.ag.norm()))

    s += ["  KUSUR (ölçüldü, gizlenmiyor): θ tek yönlü bir 'kuvvet' DEĞİLDİR.",
          "  Başlangıç açısı arctan(√10)≈1,26 rad olduğu için θ büyüdükçe",
          "  içerideki doluluk önce 1'e çıkıp sonra GERİ düşüyor (θ=0,3'te",
          "  1,000 iken θ=0,9'da 0,687). Yani kanaat açısı, hedefe olan",
          "  açı FARKI olarak verilmelidir; sabit bir θ yanlıştır. Bunu",
          "  düzeltmek, açıyı verecek melekenin formülüne bağlıdır."]

    s += ["", "--- 4. Şahit ile çıktıyı dolaştıran kapı (ağaç MPO) ---"]
    v = UcAgac(secilen.egitim[:2], gi, renk=10, bag=8)
    sg = v.blok("şahit0.çıktı")
    ck = v.blok("ÇIKTI")
    once = v.ag.hucre_dagilimi(v.hucre(ck, 0, 0)).copy()
    v.bag_kapisi(v.hucre(sg, 0, 0), v.hucre(ck, 0, 0), teta=0.9)
    sonra = v.ag.hucre_dagilimi(v.hucre(ck, 0, 0))
    _, b0g = secilen.egitim[0]
    renk0 = int(b0g[0, 0])
    s.append("  şahit0 çıktısının (0,0) rengi = %d" % renk0)
    s.append("  çıktı (0,0)  P(renk %d):  önce %.4f → sonra %.4f"
             % (renk0, once[renk0], sonra[renk0]))
    s.append("  yol uzunluğu = %d adım   norm = %.9f   kesme = %.2e"
             % (v.ag.mesafe(v.hucre(sg, 0, 0), v.hucre(ck, 0, 0)),
                v.ag.norm(), v.ag.kesme))

    s += ["",
          "Hüküm: boyut artık dışarıdan verilen bir çerçeve değil, çıktı",
          "ağacının içindeki bir genliktir (H62). Kapı onu söndürebiliyor,",
          "üniterlik bozulmuyor, şahit ile çıktı fiilen dolaşabiliyor (H56).",
          "Bu bir ÇÖZÜCÜ DEĞİLDİR: hangi meleke hangi açıyı verecek,",
          "𝒪₆/𝒪₇/𝒪₉ cevaplanmadan yazılmayacak."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(_gosterim())
