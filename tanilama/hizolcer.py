"""HIZÖLÇER -- ANA HATTA **KALICI** BAĞLI, KOŞARKEN ÖLÇER.

    from tanilama.hizolcer import Hizolcer, hizolcer_bagla
    olcer = Hizolcer(belirtec_basina=262144, had=1_000_000)
    hizolcer_bagla(olcer)
    with olcer.saat():
        ...                      # ana hattın bir çağrısı

===================================================================
NİÇİN GEÇİTTEKİ YOKLAMA YETMEZ
===================================================================

``tanilama/hiz_teftisi.py`` koşudan **evvel** tek bir kayıp çağrısı
ölçer ve geçidi ona göre açar. O bir **kestirimdir** ve kestirim
koşunun kendisi değildir:

* İlk çağrı soğuk önbellekle koşar; onuncu çağrı ısınmış koşar.
  Tek yoklama hangisini gördüğünü söylemez.
* Hafıza (``ρ_Hafıza``) koşu boyunca dolar; Zeno budaması devreye
  girer. Tek yoklama boş hafızayı ölçer.
* Kapı bandı ilk çağrıda derlenir/ısınır.

Padişahın fermanı: *"hızölçeri ana hatta kalıcı olarak bağla."* O
hâlde ölçü artık koşunun **içindedir**: her küllî mizan çağrısı
saatlenir, belirteç sayılır, ilk ile son çağrı ayrı ayrı görünür.

===================================================================
NE ÖLÇÜLÜR
===================================================================

    ölçü            manası
    --------------  ------------------------------------------------
    belirteç_sn     bütün koşunun ortalaması (toplam/toplam)
    en_iyi/en_kötü  çağrı başına en hızlı ve en yavaş
    ilk / son       ısınmanın görünmesi için
    ısınma          son / ilk -- 1'e yakınsa ısınma yok
    hüküm           HAD tutuyor mu; ``had=None`` ise "had konmadı"

**ÖLÇÜ KIRMIZI YANABİLİR (ferman 5):** ``had`` verilirse ve
tutmuyorsa ``hüküm`` bunu söyler. ``sert=True`` ile ``assert``
düşürür; varsayılan yumuşaktır çünkü bu ölçü koşuyu **durdurmak**
için değil, koşuyu **görmek** için bağlanmıştır -- durdurma işi
``gecit()``indir.
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

__all__ = ["Hizolcer", "hizolcer_bagla", "hizolcer_al", "hizolcer_beyani",
           "hizolcer_coz"]

#: Ana hatta bağlı ölçer. ``None`` ise hiçbir şey ölçülmüyor demektir
#: ve ``hizolcer_beyani`` bunu açıkça söyler -- sessizce sıfır dönmez.
_BAGLI: Optional["Hizolcer"] = None


class Hizolcer:
    """Bir hattın belirteç/sn'sini **çağrı çağrı** tutar."""

    __slots__ = ("ad", "belirtec_basina", "had", "sert", "sure",
                 "baslangic", "belirtec", "canli_saniye", "_son_bildirim")

    def __init__(self, belirtec_basina: int, had: Optional[float] = None,
                 ad: str = "hat", sert: bool = False,
                 canli_saniye: float = 0.0) -> None:
        assert int(belirtec_basina) > 0, (
            "çağrı başına belirteç sıfır olamaz -- ölçü bölünemez")
        self.ad = str(ad)
        self.belirtec_basina = int(belirtec_basina)
        #: Çağrı başına fiilen işlenen belirteç -- küme küme değişir.
        self.belirtec: list = []
        self.had = None if had is None else float(had)
        self.sert = bool(sert)
        self.sure: List[float] = []
        self.baslangic = time.perf_counter()
        #: **CANLI KÜTÜK.** Tâlim saatler sürebilir; ``0``dan büyükse
        #: hızölçer bu aralıkla koşarken bildirir. Ferman 1-L yan
        #: koşuyu yasakladı, o hâlde akışı gösterme işi de ölçünün
        #: kendi uzvuna düştü -- taht yalnız aralığı verir.
        self.canli_saniye = float(canli_saniye)
        self._son_bildirim = time.perf_counter()

    @contextmanager
    def saat(self, belirtec: int = 0):
        """Tek çağrıyı saatle. ``with olcer.saat(n): ...``

        **``belirtec`` VERİLMEK ZORUNDA KALDI** ve sebebi ölçüldü:
        münasebet döngüsü (ferman 1-I) artık **küme küme** koşuyor ve
        her kümenin boyu ayrı. Sabit bir ``belirtec_basina`` ile
        çarpmak, küçük kümeleri büyük gibi sayıp hızı **şişirirdi**.
        Verilmezse eski davranış sürer (sabit çarpan).
        """
        t0 = time.perf_counter()
        try:
            yield self
        finally:
            self.sure.append(time.perf_counter() - t0)
            self.belirtec.append(int(belirtec) if belirtec > 0
                                 else int(self.belirtec_basina))
            self._canli()
            if self.sert and self.had is not None:
                h = self.belirtec[-1] / max(self.sure[-1], 1e-12)
                assert h >= self.had, (
                    "HIZ HADDİ TUTMADI (%s): %.0f < %.0f belirteç/sn"
                    % (self.ad, h, self.had))

    def _canli(self) -> None:
        """Aralık dolduysa akışı bildir. **Metin burada yazılır** (1-G)."""
        if self.canli_saniye <= 0.0:
            return
        t = time.perf_counter()
        if t - self._son_bildirim < self.canli_saniye:
            return
        self._son_bildirim = t
        sn = sum(self.sure) or 1e-12
        bel = sum(self.belirtec)
        from nefs.munasebet import munasebet_beyani
        from nefs.keyfiyet import keyfiyet_beyani
        m = munasebet_beyani()
        k = keyfiyet_beyani()
        print("  [%7.1f sn] çağrı %4d | belirteç %10d | %9.0f bel/sn | "
              "küme %d temiz / %d kirli / %d geri dönen | "
              "keyfiyet en_iyi %.4f ort %.4f"
              % (t - self.baslangic, len(self.sure), bel, bel / sn,
                 m["temizlenen"], m["kirli_kalan"], m.get("geri_dönen", 0),
                 k["en_iyi"], k["ortalama"]), flush=True)

    def ekle(self, sn: float) -> None:
        """Dışarıda saatlenmiş bir çağrıyı kaydet."""
        self.sure.append(float(sn))

    def beyan(self) -> Dict[str, Any]:
        """Ölçünün tamamı. **Çağrı yoksa sıfır uydurulmaz.**"""
        n = len(self.sure)
        o: Dict[str, Any] = {
            "ad": self.ad, "çağrı": n,
            "had": (0 if self.had is None else self.had),
            "çağrı_belirteci": self.belirtec_basina,
        }
        if n == 0:
            o.update({"toplam_sn": 0.0, "belirteç": 0, "belirteç_sn": 0.0,
                      "en_iyi": 0.0, "en_kötü": 0.0, "ilk": 0.0, "son": 0.0,
                      "ısınma": 0.0,
                      "hüküm": "ÖLÇÜLMEDİ -- hiç çağrı saatlenmedi"})
            return o
        toplam = float(sum(self.sure))
        bel = (self.belirtec if len(self.belirtec) == n
               else [self.belirtec_basina] * n)
        belirtec = int(sum(bel))
        hiz = [b / max(s, 1e-12) for b, s in zip(bel, self.sure)]
        o.update({
            "toplam_sn": toplam,
            "belirteç": int(belirtec),
            "belirteç_sn": float(belirtec / max(toplam, 1e-12)),
            "en_iyi": float(max(hiz)), "en_kötü": float(min(hiz)),
            "ilk": float(hiz[0]), "son": float(hiz[-1]),
            "ısınma": float(hiz[-1] / max(hiz[0], 1e-12)),
        })
        if self.had is None:
            o["hüküm"] = "had konmadı (ölçü yalnız görülüyor)"
        else:
            kat = self.had / max(o["belirteç_sn"], 1e-12)
            o["hüküm"] = ("TUTUYOR" if o["belirteç_sn"] >= self.had
                          else "TUTMUYOR (%.1f kat eksik)" % kat)
        return o


def hizolcer_bagla(olcer: Optional[Hizolcer]) -> None:
    """Ölçeri ana hatta bağla. Bağlı olan **tektir**: iki ayrı ölçü
    iki ayrı hakikat demek olurdu."""
    global _BAGLI
    _BAGLI = olcer


def hizolcer_coz() -> None:
    """Bağı çöz -- ölçü artık alınmıyor ve bu **görünür**."""
    global _BAGLI
    _BAGLI = None


def hizolcer_al() -> Optional[Hizolcer]:
    return _BAGLI


def hizolcer_beyani() -> Dict[str, Any]:
    """Bağlı ölçerin beyanı. **Bağlı değilse öyle yazılır.**"""
    if _BAGLI is None:
        return {"ad": "-", "çağrı": 0, "had": 0, "çağrı_belirteci": 0,
                "toplam_sn": 0.0, "belirteç": 0, "belirteç_sn": 0.0,
                "en_iyi": 0.0, "en_kötü": 0.0, "ilk": 0.0, "son": 0.0,
                "ısınma": 0.0, "hüküm": "HIZÖLÇER BAĞLI DEĞİL"}
    return _BAGLI.beyan()


def rapor() -> str:                                      # pragma: no cover
    """Ölçerin kendisi doğru mu -- bilinen sürelerle sına."""
    o = Hizolcer(belirtec_basina=1000, had=5000.0, ad="sınama")
    for sn in (0.5, 0.25, 0.2, 0.1):
        o.ekle(sn)
    b = o.beyan()
    bos = Hizolcer(belirtec_basina=1, ad="boş").beyan()
    return "\n".join([
        "=== HIZÖLÇER ===", "",
        "  bilinen sürelerle sınama: 0,5 / 0,25 / 0,2 / 0,1 sn",
        "    çağrı %d  toplam %.2f sn  belirteç %d"
        % (b["çağrı"], b["toplam_sn"], b["belirteç"]),
        "    ortalama %.0f  (beklenen 4000/1,05 = %.0f)"
        % (b["belirteç_sn"], 4000 / 1.05),
        "    en iyi %.0f (beklenen 10000)   en kötü %.0f (beklenen 2000)"
        % (b["en_iyi"], b["en_kötü"]),
        "    ilk %.0f → son %.0f   ısınma %.2f×  (beklenen 5,00)"
        % (b["ilk"], b["son"], b["ısınma"]),
        "    had 5000 → %s" % b["hüküm"],
        "",
        "  ÖLÇÜ KIRMIZI YANABİLİR:",
        "    hiç çağrı yoksa: %r" % bos["hüküm"],
        "    bağlı değilse  : %r" % hizolcer_beyani()["hüküm"],
        "    (ikisi de sıfır DÖNDÜRMÜYOR; 'ölçülmedi' diyor)",
    ])


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
