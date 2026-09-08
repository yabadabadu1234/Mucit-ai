from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

__all__ = ["MIHENK", "MIHENK_CEVABI", "CEVAP_PAYI", "cevap_haddi",
           "mihenk_sor", "Nobet", "nobet_kur", "mihenk_metni"]


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
           basamak: int) -> Dict[str, Any]:
    from .belirtec import coz, tipten
    b = [int(x) % int(taban) for x in basamaklar]
    kirp = (len(b) // int(basamak)) * int(basamak)
    if kirp <= 0:
        return {"metin": "", "belirteç": 0, "geçersiz": 0,
                "kod_uzayı": int(taban) ** int(basamak),
                "sözlük": _sozluk(kodlama)}
    ham = [int(t) for t in np.asarray(
        tipten(b[:kirp], int(taban), int(basamak)), int).reshape(-1)]
    sozluk = _sozluk(kodlama)
    bel = [t for t in ham if 0 <= t < sozluk]
    return {"metin": (coz(bel, kodlama) if bel else ""),
            "belirteç": len(ham), "geçersiz": len(ham) - len(bel),
            "kod_uzayı": int(taban) ** int(basamak), "sözlük": sozluk}


_SOZLUK: Dict[str, int] = {}


def _sozluk(kodlama: str) -> int:
    v = _SOZLUK.get(str(kodlama))
    if v is None:
        from .belirtec import belirtec_sozlugu
        v = int(belirtec_sozlugu(str(kodlama)))
        _SOZLUK[str(kodlama)] = v
    return v


CEVAP_PAYI = 8


def cevap_haddi(basamak: int, kodlama: str = "o200k_base") -> int:
    from .belirtec import belirtecle
    boy = max(1, len(belirtecle(MIHENK_CEVABI, kodlama)))
    return int(max(1, boy * CEVAP_PAYI) * max(1, int(basamak)))


def mihenk_sor(nefs, p: Optional[np.ndarray] = None, pencere: int = 8,
               sozluk: int = 16, taban: int = 16, basamak: int = 5,
               kodlama: str = "o200k_base",
               sual: str = MIHENK, ayna=None) -> Dict[str, Any]:
    from .soyle import _uret
    if p is not None:
        nefs.yukle(np.asarray(p, float))
    bag = [int(x) % int(taban) for x
           in _basamaklar(str(sual), str(kodlama), int(taban), int(basamak))]
    kac = int(cevap_haddi(int(basamak), str(kodlama)))
    t0 = time.perf_counter()
    uretilen, bedel, sukutlar, budanan = _uret(
        nefs, bag, kac, int(pencere), int(taban), ayna=ayna)
    sure = time.perf_counter() - t0
    coz = _metne(uretilen, str(kodlama), int(taban), int(basamak))
    cevap = str(coz["metin"])
    bekleniyor = str(MIHENK_CEVABI).strip().lower()
    return {"sual": str(sual), "cevap": cevap,
            "belirteç": int(coz["belirteç"]),
            "geçersiz": int(coz["geçersiz"]),
            "kod_uzayı": int(coz["kod_uzayı"]),
            "sözlük": int(coz["sözlük"]),
            "basamak": [int(x) for x in uretilen],
            "üretilen_basamak": int(len(uretilen)),
            "ayrı_basamak": int(len(set(int(x) for x in uretilen))),
            "sabit_nokta": bool(len(set(int(x) for x in uretilen)) <= 1),
            "ayna": bool(ayna is not None),
            "bedel": float(bedel), "budanan": int(budanan),
            "tepe_payı": float(np.exp(-float(bedel) / max(kac, 1))),
            "düz_pay": float(1.0 / max(int(taban), 1)),
            "sükût": float(np.mean(sukutlar)) if sukutlar else 1.0,
            "saniye": float(sure),
            "boş": bool(not cevap.strip()),
            "isabet": bool(bekleniyor in cevap.strip().lower()),
            "beklenen": str(MIHENK_CEVABI)}


class Nobet:

    def __init__(self, nefs, ara_saniye: float = 300.0, pencere: int = 8,
                 sozluk: int = 16, taban: int = 16, basamak: int = 5,
                 kodlama: str = "o200k_base",
                 sual: str = MIHENK, ayna=None) -> None:
        self.nefs = nefs
        self.ayna = ayna
        self.ara = float(ara_saniye)
        self.pencere = int(pencere)
        self.sozluk = int(sozluk)
        self.taban = int(taban)
        self.basamak = int(basamak)
        self.kodlama = str(kodlama)
        self.sual = str(sual)
        self.defter: List[Dict[str, Any]] = []
        self._t0 = time.perf_counter()
        self._son = self._t0 - self.ara

    def _sor(self, p, kayip: float, adim: int, ham: float = 0.0,
             kume: int = 0, kume_kimlik: str = "",
             eniyileme: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        eski = np.asarray(self.nefs.vektor(), float).copy()
        try:
            c = mihenk_sor(self.nefs, p, pencere=self.pencere,
                           sozluk=self.sozluk, taban=self.taban,
                           basamak=self.basamak, kodlama=self.kodlama,
                           sual=self.sual, ayna=self.ayna)
        finally:
            self.nefs.yukle(eski)
        c["saniye_ofset"] = float(time.perf_counter() - self._t0)
        c["kayıp"] = float(kayip)
        c["ham"] = float(ham)
        c["küme"] = int(kume)
        c["küme_kimlik"] = str(kume_kimlik)
        c["eniyileme"] = dict(eniyileme or {})
        c["adım"] = int(adim)
        self.defter.append(c)
        print("  [mihenk %6.0f sn · adım %d · V %.4f (ham %.4f · küme %s"
              "/%d)] %s → %r"
              "   (geçersiz %d/%d · ayrı basamak %d%s"
              " · kabul %d/%d · adım‖%.3e‖ · kapsam %d/%d)%s"
              % (c["saniye_ofset"], c["adım"], c["kayıp"], c["ham"],
                 c["küme_kimlik"] or "—", c["küme"], self.sual,
                 c["cevap"], c["geçersiz"], c["belirteç"],
                 c["ayrı_basamak"],
                 " SABİT NOKTA" if c["sabit_nokta"] else "",
                 int(c["eniyileme"].get("kabul", 0)),
                 int(c["eniyileme"].get("tarama", 0)),
                 float(c["eniyileme"].get("adım_normu", 0.0)),
                 int(c["eniyileme"].get("kapsanan_parametre", 0)),
                 int(c["eniyileme"].get("toplam_parametre", 0)),
                 "  ✓" if c["isabet"] else ""),
              flush=True)
        return c

    def yokla(self, p, kayip: float = 0.0, adim: int = 0,
              ham: float = 0.0, kume: int = 0, kume_kimlik: str = "",
              eniyileme: Optional[Dict[str, Any]] = None
              ) -> Optional[Dict[str, Any]]:
        simdi = time.perf_counter()
        if simdi - self._son < self.ara:
            return None
        self._son = simdi
        return self._sor(p, kayip, adim, ham, kume, kume_kimlik,
                         eniyileme)

    def beyan(self, p=None) -> Dict[str, Any]:
        if p is not None:
            self._sor(p, kayip=float("nan"), adim=-1,
                      ham=float("nan"))
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
              kodlama: str = "o200k_base",
              sual: str = MIHENK, ayna=None) -> Nobet:
    return Nobet(nefs, ara_saniye=ara_saniye, pencere=pencere,
                 sozluk=sozluk, taban=taban, basamak=basamak,
                 kodlama=kodlama, sual=sual, ayna=ayna)


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
    s += ["  kod uzayı : %d   sözlük : %d   üretim haddi : %d basamak"
          % (d[-1]["kod_uzayı"], d[-1]["sözlük"],
             int(d[-1].get("üretilen_basamak", 0))),
          "  üretim haddi ARC ızgara bütçesinden DEĞİL, beklenen cevabın",
          "  belirteç boyundan türer (%d kat pay) -- ferman 1-J"
          % CEVAP_PAYI,
          "  vakum kıvılcımı: %s"
          % ("AÇIK" if d[-1].get("ayna") else
             "KAPALI -- açgözlü argmax (ferman 7 ihlâli)"),
          "  düz dağılımın tepe payı : %.6f  (1/taban)"
          % float(d[-1].get("düz_pay", 0.0)),
          "  V ağırlıklıdır ve ağırlık her turda YENİDEN ölçülür",
          "  (ferman 1-J); o hâlde turlar arasında KIYAS KABUL ETMEZ.",
          "  HAM ağırlıksızdır fakat o da ANCAK AYNI KÜME İÇİNDE kıyas",
          "  kabul eder; küme kimliği değişince veri değişmiş demektir.",
          "  DAHASI: bu satırlar eniyileyicinin KABUL ETTİĞİ noktalar",
          "  değil, YOKLADIĞI noktalardır. İlerlemenin ölçüsü V yahut",
          "  HAM değil, KABUL sayısı ve ADIM NORMUDUR: kabul sıfırsa",
          "  eniyileyici hiçbir yönde iyileşme bulamamış demektir.",
          "  %-8s %-7s %-9s %-9s %-9s %-8s %-10s %s"
          % ("saniye", "adım", "V", "ham", "geçersiz",
             "ayrıbas", "tepepayı", "cevap")]
    for c in d:
        _tp = float(c.get("tepe_payı", 0.0))
        _dz = float(c.get("düz_pay", 1.0)) or 1.0
        s.append("  %-8.0f %-7d %-9.4f %-9.4f %-9s %-8s %-10s %r%s"
                 % (c["saniye_ofset"], c["adım"], c["kayıp"],
                    float(c.get("ham", 0.0)),
                    "%d/%d" % (c["geçersiz"], c["belirteç"]),
                    "%d%s" % (c["ayrı_basamak"],
                              "!" if c["sabit_nokta"] else ""),
                    "%.5f(%.1fx)" % (_tp, _tp / _dz),
                    c["cevap"], "  ✓" if c["isabet"] else ""))
    ayri = len({c["cevap"] for c in d})
    s += ["",
          "  isabet      : %d / %d" % (sum(1 for c in d if c["isabet"]),
                                       len(d)),
          "  boş cevap   : %d / %d" % (sum(1 for c in d if c["boş"]),
                                       len(d)),
          "  geçersiz belirteç : %d / %d  -- kod uzayı sözlükten %.1f kat "
          "büyük; taşan kimlik ÇÖZÜLEMEZ, sessizce elenmez, sayılır"
          % (sum(c["geçersiz"] for c in d), sum(c["belirteç"] for c in d),
             float(d[-1]["kod_uzayı"]) / max(1, d[-1]["sözlük"])),
          "  tepe payı düz paya YAKINSA dağılımda yapı yoktur ve",
          "  argmax'ın seçtiği basamak keyfîdir; UZAKSA yapı vardır",
          "  fakat açgözlü çözücü onu sabit noktaya eziyordur.",
          "  sabit nokta : %d / %d yoklamada üretim TEK basamağa çöktü"
          % (sum(1 for c in d if c["sabit_nokta"]), len(d)),
          "  ayrı cevap  : %d  %s"
          % (ayri, "(cevap HİÇ DEĞİŞMEDİ -- ağırlık cevaba geçmiyor)"
             if ayri <= 1 and len(d) > 1 else "")]
    return "\n".join(s)
