from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

__all__ = ["MIHENK", "MIHENK_CEVABI", "mihenk_sor", "Nobet", "nobet_kur",
           "mihenk_metni"]


MIHENK = "Question: What is the capital city of France? Answer:"

MIHENK_CEVABI = "Paris"


def _basamaklar(metin: str, kodlama: str, taban: int, basamak: int
                ) -> List[int]:
    from .belirtec import belirtecle, tip_vektoru
    bel = belirtecle(metin, kodlama)
    assert bel, "mihenk suâli boş belirteçlendi -- belirteç kapısı ölü"
    return [int(x) for x in
            np.asarray(tip_vektoru(bel, int(taban), int(basamak)),
                       int).reshape(-1)]


def _metne(basamaklar: Sequence[int], kodlama: str, taban: int,
           basamak: int) -> str:
    from .belirtec import coz, tipten
    b = [int(x) % int(taban) for x in basamaklar]
    kirp = (len(b) // int(basamak)) * int(basamak)
    if kirp <= 0:
        return ""
    bel = [int(t) for t in np.asarray(
        tipten(b[:kirp], int(taban), int(basamak)), int).reshape(-1)]
    sozluk = _sozluk(kodlama)
    bel = [t for t in bel if 0 <= t < sozluk]
    if not bel:
        return ""
    return coz(bel, kodlama)


_SOZLUK: Dict[str, int] = {}


def _sozluk(kodlama: str) -> int:
    v = _SOZLUK.get(str(kodlama))
    if v is None:
        from .belirtec import belirtec_sozlugu
        v = int(belirtec_sozlugu(str(kodlama)))
        _SOZLUK[str(kodlama)] = v
    return v


def mihenk_sor(nefs, p: Optional[np.ndarray] = None, pencere: int = 8,
               sozluk: int = 16, taban: int = 16, basamak: int = 5,
               kodlama: str = "o200k_base", azami_uret: int = 0,
               sual: str = MIHENK) -> Dict[str, Any]:
    from .soyle import _uret
    if p is not None:
        nefs.yukle(np.asarray(p, float))
    bag = [int(x) % int(taban) for x
           in _basamaklar(str(sual), str(kodlama), int(taban), int(basamak))]
    kac = int(azami_uret) if int(azami_uret) > 0 else int(basamak) * 4
    kac = max(int(basamak), (kac // int(basamak)) * int(basamak))
    t0 = time.perf_counter()
    uretilen, bedel, sukutlar, budanan = _uret(
        nefs, bag, kac, int(pencere), int(taban))
    sure = time.perf_counter() - t0
    cevap = _metne(uretilen, str(kodlama), int(taban), int(basamak))
    bekleniyor = str(MIHENK_CEVABI).strip().lower()
    return {"sual": str(sual), "cevap": cevap,
            "basamak": [int(x) for x in uretilen],
            "üretilen_basamak": int(len(uretilen)),
            "bedel": float(bedel), "budanan": int(budanan),
            "sükût": float(np.mean(sukutlar)) if sukutlar else 1.0,
            "saniye": float(sure),
            "boş": bool(not cevap.strip()),
            "isabet": bool(bekleniyor in cevap.strip().lower()),
            "beklenen": str(MIHENK_CEVABI)}


class Nobet:

    def __init__(self, nefs, ara_saniye: float = 300.0, pencere: int = 8,
                 sozluk: int = 16, taban: int = 16, basamak: int = 5,
                 kodlama: str = "o200k_base", azami_uret: int = 0,
                 sual: str = MIHENK) -> None:
        self.nefs = nefs
        self.ara = float(ara_saniye)
        self.pencere = int(pencere)
        self.sozluk = int(sozluk)
        self.taban = int(taban)
        self.basamak = int(basamak)
        self.kodlama = str(kodlama)
        self.azami_uret = int(azami_uret)
        self.sual = str(sual)
        self.defter: List[Dict[str, Any]] = []
        self._t0 = time.perf_counter()
        self._son = self._t0 - self.ara

    def _sor(self, p, kayip: float, adim: int) -> Dict[str, Any]:
        eski = np.asarray(self.nefs.vektor(), float).copy()
        try:
            c = mihenk_sor(self.nefs, p, pencere=self.pencere,
                           sozluk=self.sozluk, taban=self.taban,
                           basamak=self.basamak, kodlama=self.kodlama,
                           azami_uret=self.azami_uret, sual=self.sual)
        finally:
            self.nefs.yukle(eski)
        c["saniye_ofset"] = float(time.perf_counter() - self._t0)
        c["kayıp"] = float(kayip)
        c["adım"] = int(adim)
        self.defter.append(c)
        print("  [mihenk %6.0f sn · adım %d · V %.4f] %s → %r%s"
              % (c["saniye_ofset"], c["adım"], c["kayıp"], self.sual,
                 c["cevap"], "  ✓" if c["isabet"] else ""),
              flush=True)
        return c

    def yokla(self, p, kayip: float = 0.0, adim: int = 0
              ) -> Optional[Dict[str, Any]]:
        simdi = time.perf_counter()
        if simdi - self._son < self.ara:
            return None
        self._son = simdi
        return self._sor(p, kayip, adim)

    def beyan(self, p=None) -> Dict[str, Any]:
        if p is not None:
            self._sor(p, kayip=float("nan"), adim=-1)
        d = list(self.defter)
        return {"sual": self.sual, "beklenen": MIHENK_CEVABI,
                "ara_saniye": self.ara, "yoklama": len(d),
                "defter": d,
                "isabet": sum(1 for c in d if c["isabet"]),
                "boş": sum(1 for c in d if c["boş"]),
                "ayrı_cevap": len({c["cevap"] for c in d}),
                "son_cevap": (d[-1]["cevap"] if d else ""),
                "metin": mihenk_metni({"sual": self.sual,
                                       "beklenen": MIHENK_CEVABI,
                                       "ara_saniye": self.ara,
                                       "defter": d})}


def nobet_kur(nefs, ara_saniye: float = 300.0, pencere: int = 8,
              sozluk: int = 16, taban: int = 16, basamak: int = 5,
              kodlama: str = "o200k_base", azami_uret: int = 0,
              sual: str = MIHENK) -> Nobet:
    return Nobet(nefs, ara_saniye=ara_saniye, pencere=pencere,
                 sozluk=sozluk, taban=taban, basamak=basamak,
                 kodlama=kodlama, azami_uret=azami_uret, sual=sual)


def mihenk_metni(beyan: Dict[str, Any]) -> str:
    d = list(beyan.get("defter") or [])
    s = ["=== MİHENK: ALELÂDE BİR İNGİLİZCE SUAL (ferman 2-F) ===", "",
         "  sual     : %s" % beyan.get("sual", ""),
         "  beklenen : %s" % beyan.get("beklenen", ""),
         "  ara      : her %.0f saniyede bir, MEVCUT ağırlıkla"
         % float(beyan.get("ara_saniye", 0.0)),
         "  yoklama  : %d" % len(d), ""]
    if not d:
        s += ["  ⚠ HİÇ YOKLANMADI -- nöbet koşmadı yahut tâlim aradan",
              "    kısa sürdü. Ölçü kırmızı yanıyor (ferman 5)."]
        return "\n".join(s)
    s += ["  %-8s %-7s %-9s %-6s %s"
          % ("saniye", "adım", "kayıp", "sükût", "cevap")]
    for c in d:
        s.append("  %-8.0f %-7d %-9.4f %-6.3f %r%s"
                 % (c["saniye_ofset"], c["adım"], c["kayıp"], c["sükût"],
                    c["cevap"], "  ✓" if c["isabet"] else ""))
    ayri = len({c["cevap"] for c in d})
    s += ["",
          "  isabet      : %d / %d" % (sum(1 for c in d if c["isabet"]),
                                       len(d)),
          "  boş cevap   : %d / %d" % (sum(1 for c in d if c["boş"]),
                                       len(d)),
          "  ayrı cevap  : %d  %s"
          % (ayri, "(cevap HİÇ DEĞİŞMEDİ -- ağırlık cevaba geçmiyor)"
             if ayri <= 1 and len(d) > 1 else "")]
    return "\n".join(s)
