from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = ["HEDEF", "had", "had_sifirla", "BUTCE_SANIYESI",
           "olc", "teftis", "rapor"]

HEDEF: float = 1_000_000.0
_HAD: list = []


def had(yazmac_boyu: int = 0, kapi: int = 0) -> float:
    if _HAD:
        return float(_HAD[0])
    from nefs.donanim import tamsayi_hizi
    t = tamsayi_hizi()
    sn = float(t["sn"])
    assert sn > 0.0, (
        "tamsayı hızı yoklanamadı -- had ölçüsüz konamaz (ferman 5-B)")
    kelime = float(t["satır"]) * float(t["kelime"])
    d = float(yazmac_boyu) if int(yazmac_boyu) > 0 else kelime
    k = float(kapi) if int(kapi) > 0 else 1.0
    _HAD.append(kelime / sn / max(d / kelime, 1.0) / k)
    return float(_HAD[0])


def had_sifirla() -> None:
    _HAD.clear()

BUTCE_SANIYESI: float = 86_400.0


@dataclass
class Kalem:

    ad: str
    cagri: int
    sure: float

    @property
    def basina(self) -> float:
        return self.sure / max(1, self.cagri)


def _saat(f, *a, **k) -> Tuple[Any, float]:
    t = time.perf_counter()
    r = f(*a, **k)
    return r, time.perf_counter() - t


def olc(ayar=None, ornek: int = 0, tekrar: int = 1) -> Dict[str, Any]:
    from main.egitim import KISA_CPU, mizan_ayari
    from nefs.hafiza import Hafiza
    from nefs.kulli_mizan import kulli_mizan
    from nefs.melekeler import QNefs
    from nefs.musahede import gorevleri_getir
    from kuantum.qegitim import belirtecleri_kodla, ornekler

    a = ayar or KISA_CPU
    ornek = int(ornek) if int(ornek) > 0 else int(a.ornek_sayisi)
    g = list(gorevleri_getir("training"))
    veri = ornekler(g, azami=int(ornek), pencere=int(a.pencere),
                    sozluk=int(a.sozluk), tohum=int(a.tohum),
                    taban=int(a.veri_lifi),
                    basamak=int(getattr(a, "belirtec_basamak", 0)))
    assert veri, "hız teftişi için veri BOŞ"
    from kuantum.qegitim import ornek_bol
    nefs = QNefs(a.tohum, a.qayar())
    nefs.idrak_et(belirtecleri_kodla(list(ornek_bol(veri[0])[0]),
                                     a.veri_lifi, a.veri_lifi))
    p = nefs.vektor()

    kalem: List[Kalem] = []

    t = 0.0
    for bag, _h, _c, _m in (ornek_bol(o) for o in veri):
        _, s = _saat(belirtecleri_kodla, list(bag), a.veri_lifi, a.sozluk)
        t += s
    kalem.append(Kalem("belirteç kodlaması", len(veri), t))

    E = belirtecleri_kodla(list(veri[0][0]), a.veri_lifi,
                           a.veri_lifi)
    t = 0.0
    _boy = {}
    for _o in veri:
        _boy.setdefault(len(_o[0]), []).append(_o)
    _esit = _boy[max(_boy, key=lambda k: len(_boy[k]))]
    Ey = np.stack([belirtecleri_kodla(list(bag), a.veri_lifi,
                                          a.veri_lifi)
                   for bag, _h, _c, _m in (ornek_bol(o) for o in _esit)])
    for _ in range(int(tekrar)):
        _, s = _saat(nefs.idrak_et, Ey)
        t += s
    kalem.append(Kalem("ileri geçiş (idrak_et)", int(tekrar), t))

    q = nefs.idrak_et(E)
    tek: List[Tuple[str, float]] = []
    for no in list(nefs.sira)[:41]:
        _, s = _saat(nefs.s[no].kosu, q, nefs.p)
        tek.append((getattr(nefs.s[no], "ad", str(no)), s))
    tek.sort(key=lambda x: -x[1])

    _, s_harman = _saat(q.harman)
    _, s_olc = _saat(q.olcumler)
    _, s_ent = _saat(q.y.dolasiklik_entropisi)
    _, s_bey = _saat(q.beyan, 0)
    kalem.append(Kalem("harman", 1, s_harman))
    kalem.append(Kalem("olcumler", 1, s_olc))
    kalem.append(Kalem("dolaşıklık entropisi", 1, s_ent))
    kalem.append(Kalem("beyan", 1, s_bey))

    mz = mizan_ayari(a)
    haf = Hafiza(kapasite=32)
    _, s_mizan = _saat(kulli_mizan, nefs, veri, p, a.sozluk,
                       ayar=mz, hafiza=haf, adim=0)
    kalem.append(Kalem("kulli_mizan (tam çağrı)", 1, s_mizan))

    belirtec = len(veri) * int(a.pencere)
    ileri = [k for k in kalem if k.ad.startswith("ileri")][0]
    return {
        "kalem": kalem, "tek_meleke": tek,
        "belirteç": belirtec,
        "d": int(np.prod(q.y.ayar.lif)), "lif": tuple(q.y.ayar.lif),
        "parametre": len(nefs),
        "kayıp_süresi": s_mizan,
        "ileri_payı": ileri.sure / max(1e-12, s_mizan)
        * (1.0 / max(1, int(tekrar))),
        "belirteç_sn": belirtec / max(1e-12, s_mizan),
        "meleke_sayısı": len(tek),
    }


def teftis(ayar=None, had_degeri: float = 0.0, sert: bool = True) -> Dict[str, Any]:
    o = olc(ayar)
    h = float(had_degeri) if float(had_degeri) > 0.0 else had()
    o["had"] = h
    o["hedef"] = float(HEDEF)
    o["hedefe_kat"] = float(HEDEF) / max(1e-9, o["belirteç_sn"])
    o["geçti"] = bool(o["belirteç_sn"] >= h)
    if sert:
        assert o["geçti"], (
            "HIZ HADDİ TUTMUYOR: %.1f belirteç/sn ölçüldü, %.0f lâzım "
            "(%.1f kat eksik). Had ELLE YAZILMADI, donanımdan ÖLÇÜLDÜ "
            "(ferman 5-B). Hedef %.0f'e uzaklık: %.1f kat. "
            "En pahalı uzuv: %s"
            % (o["belirteç_sn"], h, h / max(1e-9, o["belirteç_sn"]),
               HEDEF, o["hedefe_kat"],
               o["tek_meleke"][0][0] if o["tek_meleke"] else "?"))
    return o


def rapor(ayar=None) -> str:
    o = olc(ayar)
    s = ["=== HIZ TEFTİŞİ -- belirteç/sn haddi ===", "",
         "  yazmaç: d=%d  lif=%r  parametre=%d"
         % (o["d"], o["lif"], o["parametre"]),
         "  ölçülen: %d belirteç, %.3f sn → **%.1f belirteç/sn**"
         % (o["belirteç"], o["kayıp_süresi"], o["belirteç_sn"]),
         "  HAD    : %.0f belirteç/sn   →  %s  (%.1f kat eksik)"
         "   [ÖLÇÜLDÜ, elle yazılmadı -- ferman 5-B]"
         % (had(), "GEÇTİ" if o["belirteç_sn"] >= had() else "KALDI",
            had() / max(1e-9, o["belirteç_sn"])),
         "  HEDEF  : %.0f belirteç/sn   →  %.1f kat uzakta"
         % (HEDEF, HEDEF / max(1e-9, o["belirteç_sn"])),
         "", "  --- KALEM KALEM (tahmin yok, saatlendi) ---"]
    for k in o["kalem"]:
        s.append("    %-26s %5d çağrı  %8.3f sn  (%8.4f sn/çağrı)"
                 % (k.ad, k.cagri, k.sure, k.basina))
    s += ["", "  --- EN PAHALI 10 MELEKE ---"]
    for ad, sn in o["tek_meleke"][:10]:
        s.append("    %-40s %8.4f sn" % (ad[:40], sn))
    s += ["", "  ileri geçişin kayıp içindeki payı: %%%.1f"
          % (100.0 * o["ileri_payı"])]
    return "\n".join(s)
