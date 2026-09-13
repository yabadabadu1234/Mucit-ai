from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

__all__ = ["Hizolcer", "hizolcer_bagla", "hizolcer_al", "hizolcer_beyani",
           "hizolcer_coz", "hiz_asimi", "hiz_metni"]

_BAGLI: Optional["Hizolcer"] = None


class Hizolcer:

    __slots__ = ("ad", "belirtec_basina", "had", "sert", "sure",
                 "baslangic", "belirtec", "canli_saniye", "_son_bildirim")

    def __init__(self, belirtec_basina: int, had: Optional[float] = None,
                 ad: str = "hat", sert: bool = False,
                 canli_saniye: float = 0.0) -> None:
        assert int(belirtec_basina) > 0, (
            "çağrı başına belirteç sıfır olamaz -- ölçü bölünemez")
        self.ad = str(ad)
        self.belirtec_basina = int(belirtec_basina)
        self.belirtec: list = []
        self.had = None if had is None else float(had)
        self.sert = bool(sert)
        self.sure: List[float] = []
        self.baslangic = time.perf_counter()
        self.canli_saniye = float(canli_saniye)
        self._son_bildirim = time.perf_counter()

    @contextmanager
    def saat(self, belirtec: int = 0):
        t0 = time.perf_counter()
        try:
            yield self
        finally:
            self.sure.append(time.perf_counter() - t0)
            self.belirtec.append(int(belirtec) if belirtec > 0
                                 else int(self.belirtec_basina))
            self._canli()
            if self.sert:
                t = self.tavan()
                assert not t["aşıldı"], (
                    "HIZ TAVANI AŞILDI (%s): had %.0f belirteç/sn, ölçülen "
                    "%.0f -- %.1f kat eksik. Hat kendi ısınmasını (%.2f×) "
                    "tamamladığı hâlde açığı kapatamıyor; devam etmek "
                    "padişahın saatine mal olur (ferman 2-G)."
                    % (self.ad, t["had"], t["hız"], t["kat"], t["ısınma"]))

    def _canli(self) -> None:
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

    def asim(self) -> float:
        b = self.beyan()
        if self.had is None or int(b["çağrı"]) == 0:
            return 0.0
        return max(0.0, 1.0 - float(b["belirteç_sn"]) / float(self.had))

    def tavan(self) -> Dict[str, Any]:
        b = self.beyan()
        hiz = float(b.get("belirteç_sn", 0.0))
        if self.had is None or int(b["çağrı"]) < 2 or hiz <= 0.0:
            return {"aşıldı": False, "kat": 0.0, "ısınma": 0.0,
                    "hız": hiz, "had": float(self.had or 0.0),
                    "sebep": "tavan için en az iki saatlenmiş çağrı gerekir"}
        kat = float(self.had) / hiz
        isinma = max(float(b.get("ısınma", 1.0)), 1.0)
        return {"aşıldı": bool(kat > isinma), "kat": kat, "ısınma": isinma,
                "hız": hiz, "had": float(self.had)}

    def ekle(self, sn: float) -> None:
        self.sure.append(float(sn))

    def beyan(self) -> Dict[str, Any]:
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
    global _BAGLI
    _BAGLI = olcer


def hizolcer_coz() -> None:
    global _BAGLI
    _BAGLI = None


def hizolcer_al() -> Optional[Hizolcer]:
    return _BAGLI


def hizolcer_beyani() -> Dict[str, Any]:
    if _BAGLI is None:
        return {"ad": "-", "çağrı": 0, "had": 0, "çağrı_belirteci": 0,
                "toplam_sn": 0.0, "belirteç": 0, "belirteç_sn": 0.0,
                "en_iyi": 0.0, "en_kötü": 0.0, "ilk": 0.0, "son": 0.0,
                "ısınma": 0.0, "hüküm": "HIZÖLÇER BAĞLI DEĞİL"}
    return _BAGLI.beyan()


def hiz_asimi() -> float:
    return 0.0 if _BAGLI is None else float(_BAGLI.asim())


def hiz_metni() -> str:
    if _BAGLI is None:
        return "  HIZ: hızölçer bağlı değil -- ölçü hiçbir şey ölçmüyor."
    b = _BAGLI.beyan()
    t = _BAGLI.tavan()
    return "\n".join([
        "  HIZ HADDİ (ferman 5: kırmızı yanabilir)",
        "    ölçülen %.0f belirteç/sn   had %.0f   hüküm: %s"
        % (b["belirteç_sn"], b["had"], b["hüküm"]),
        "    aşım kefesi : %.6f   (0 = had tutuyor)" % _BAGLI.asim(),
        "    tavan       : %s   (%.1f kat eksik, ısınma %.2f×)"
        % ("AŞILDI" if t["aşıldı"] else "aşılmadı",
           t.get("kat", 0.0), t.get("ısınma", 0.0)),
        "    tavan SABİT DEĞİL (ferman 1-J): hattın kendi ısınma nispeti.",
        "    Aşım kefesi p'ye zayıf bağlıdır; payı ölçülünce sıfıra yakın",
        "    çıkarsa bu bir kusur değil, ferman 1-S'nin beklediği neticedir."])
