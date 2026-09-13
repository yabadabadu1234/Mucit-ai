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
                    "HIZ TAVANI AŞILDI (%s): toplam hız %.0f belirteç/sn, "
                    "hattın EN KÖTÜ tek çağrısının (%.0f) bile altında. "
                    "Tek çağrıların hiçbiri bu kadar yavaş değilken "
                    "toplamın altına düşmesi, saatlenmeyen yerde tıkanma "
                    "demektir (en iyi %.0f). Ferman 2-G."
                    % (self.ad, t["hız"], t["en_kötü"], t["en_iyi"]))

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
        from ogrenme.mecz import (mecz_beyani, yetim_bloklar,
                                  adres_beyani)
        from nefs.kulli_mizan import kefe_kimiltisi
        m = munasebet_beyani()
        k = keyfiyet_beyani()
        z = mecz_beyani()
        print("  [%7.1f sn] çağrı %4d | belirteç %10d | %9.0f bel/sn | "
              "küme %d temiz / %d kirli / %d geri dönen | "
              "keyfiyet en_iyi %.4f ort %.4f | "
              "mecz r %.3e · iz_g %.3e · ‖eğim‖ %.3e · κ %.3e · "
              "kabul %d/%d · hissedilmeyen %d · r* %.3e · "
              "ΔV %.3e vs lineer %.3e | kımıldayan kefe %s %+.3e, "
              "%s %+.3e | yetim blok %s | adres %s"
              % (t - self.baslangic, len(self.sure), bel, bel / sn,
                 m["temizlenen"], m["kirli_kalan"], m.get("geri_dönen", 0),
                 k["en_iyi"], k["ortalama"],
                 z["yarıçap"], z["iz_g"], z["eğim_normu"], z["κ"],
                 int(z["kabul"]), int(z["tur"]),
                 int(z["hissedilmeyen_adım"]), z["r_kullanılan"],
                 z["ΔV_gerçek"], z["ΔV_lineer"],
                 kefe_kimiltisi()["ad"], kefe_kimiltisi()["Δ"],
                 kefe_kimiltisi()["ikinci"], kefe_kimiltisi()["Δ2"],
                 " · ".join("%s %d" % (ad, n)
                            for n, ad in yetim_bloklar()) or "yok",
                 adres_beyani() or "yoklanmadı"),
              flush=True)

    def asim(self) -> float:
        b = self.beyan()
        if self.had is None or int(b["çağrı"]) == 0:
            return 0.0
        return max(0.0, 1.0 - float(b["belirteç_sn"]) / float(self.had))

    def tavan(self) -> Dict[str, Any]:
        b = self.beyan()
        hiz = float(b.get("belirteç_sn", 0.0))
        en_iyi = float(b.get("en_iyi", 0.0))
        son = float(b.get("son", 0.0))
        o = {"aşıldı": False, "kat": 0.0, "ısınma": 0.0, "hız": hiz,
             "had": float(self.had or 0.0), "en_iyi": en_iyi, "son": son}
        if int(b["çağrı"]) < 4 or en_iyi <= 0.0 or son <= 0.0:
            o["sebep"] = "tavan için en az dört saatlenmiş çağrı gerekir"
            return o
        en_kotu = float(b.get("en_kötü", 0.0))
        o["en_kötü"] = en_kotu
        o["kat"] = en_iyi / max(hiz, 1e-300)
        o["ısınma"] = max(float(b.get("ısınma", 1.0)), 1.0)
        o["aşıldı"] = bool(en_kotu > 0.0 and hiz < en_kotu)
        return o

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
        "    tavan       : %s   (toplam %.0f · en iyi %.0f · en kötü %.0f)"
        % ("AŞILDI" if t["aşıldı"] else "aşılmadı", t.get("hız", 0.0),
           t.get("en_iyi", 0.0), t.get("en_kötü", 0.0)),
        "    TAVAN HADDE GÖRE DEĞİL, HATTIN KENDİ DAĞILIMINA GÖREDİR:",
        "    toplam hız, en kötü TEK çağrının altına düşerse tıkanma var",
        "    demektir. Sabit bir sayı yok; hudut ölçülenden çıkıyor (1-J).",
        "    Aşım kefesi p'ye zayıf bağlıdır; payı ölçülünce sıfıra yakın",
        "    çıkarsa bu bir kusur değil, ferman 1-S'nin beklediği neticedir."])
