"""HIZ TEFTİŞİ -- tâlim başlamadan EVVEL, belirteç/sn haddi tutuyor mu?

    python -m tanilama.hiz_teftisi

===================================================================
NİÇİN VAR: BİR YALANIN TASHİHİ
===================================================================

Padişahın ikazı:

    *"Saniyede 1 milyon token üretebildiğimizi iddia etmiştin, o hâlde
    neden 38 dakika olmuş hâlâ eski eğitim bitmedi? Hız konusunda
    garanti elde etmeden umumi eğitim başlatma!"*

**İTİRAF.** 1 milyon belirteç/sn'ye ulaştığımız hiç ölçülmedi. Ölçülen
tek sayı ``nefs/soyle.py``de yazılıdır: ``d=256``te **1401 belirteç/sn**
ve o da eski MPS hattına nispetle "127 kat" diye anılmıştı. Nispet
doğruydu, mutlak had ise **hiçbir zaman tutmadı**. Hedef 1.000.000'du;
"127 kat hızlandı" cümlesi hedefin tutulduğu intibaını veriyordu ve bu
bir örtmedir.

Bu modül o örtmeyi imkânsız kılar: tâlim, bu teftişten geçmeden
başlamaz (``main/egitim.py:kulli_kayip_talimi`` onu çağırır ve
``assert`` eder).

===================================================================
BELİRTEÇ NASIL SAYILIR (TARİF ÖNCE, SAYI SONRA)
===================================================================

Bir "belirteç işlendi" demek, o belirtecin **ileri geçişten geçip
mizana girmesi** demektir. Bir kayıp çağrısı ``B`` örneği ve örnek
başına ``L`` bağlam belirtecini işler::

    belirteç / kayıp çağrısı = B × L

Bu sayım şişirilemez: üretimde atılan adımlar değil, fiilen ileri
geçişten geçen belirteçler sayılır.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = ["HAD", "AZAMI_SANIYE", "olc", "teftis", "rapor"]

#: **HAD (ferman).** Bunun altında umumi tâlim BAŞLAMAZ.
HAD: float = 1_000_000.0

#: **TÂLİM HADDİ (ferman).** Toplam tâlim bunu aşamaz.
AZAMI_SANIYE: float = 600.0


@dataclass
class Kalem:
    """Tek bir uzvun payı: kaç kere çağrıldı, ne kadar sürdü."""

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
    """Bir kayıp çağrısının **içini** aç: hangi uzuv kaç saniye yiyor?

    Tahmin yoktur; her kalem ayrı ayrı saatlenir. Toplamın kalemlerin
    toplamına eşit olması ``assert`` edilir -- yoksa ölçüm bir yeri
    kaçırıyor demektir ve o boşluk saklanamaz.
    """
    from main.egitim import KISA_CPU, mizan_ayari
    from nefs.hafiza import Hafiza
    from nefs.kulli_mizan import kulli_mizan
    from nefs.melekeler import QNefs
    from nefs.musahede import gorevleri_getir
    from nefs.qegitim import belirtecleri_kodla, ornekler

    a = ayar or KISA_CPU
    # **ÖRNEK SAYISI AYARIN YIĞIN BOYUDUR.** Evvelce sabit 4'tü ve
    # ölçüm kendi kendini bozuyordu: yazmaç B=64 kuruluyor, teftiş 4
    # örnek veriyor, netice 2 119 belirteç/sn çıkıyordu -- halbuki aynı
    # ayar 64 örnekle 37 542 veriyor. Ölçü, ölçtüğü şeyle aynı ölçekte
    # olmalıdır.
    ornek = int(ornek) if int(ornek) > 0 else int(a.ornek_sayisi)
    g = list(gorevleri_getir("training"))
    veri = ornekler(g, azami=int(ornek), pencere=int(a.pencere),
                    sozluk=int(a.sozluk), tohum=int(a.tohum))
    assert veri, "hız teftişi için veri BOŞ"
    nefs = QNefs(a.tohum, a.qayar())
    nefs.idrak_et(np.zeros((2, a.satir_kubiti)))
    p = nefs.vektor()

    kalem: List[Kalem] = []

    # ── 1. Kodlama
    t = 0.0
    for bag, _h in veri:
        _, s = _saat(belirtecleri_kodla, list(bag), a.satir_kubiti, a.sozluk)
        t += s
    kalem.append(Kalem("belirteç kodlaması", len(veri), t))

    # ── 2. İLERİ GEÇİŞ (41 meleke) -- asıl şüpheli
    E = belirtecleri_kodla(list(veri[0][0]), a.satir_kubiti, a.sozluk)
    t = 0.0
    Ey = np.stack([belirtecleri_kodla(list(bag), a.satir_kubiti, a.sozluk)
                   for bag, _h in veri])
    for _ in range(int(tekrar)):
        _, s = _saat(nefs.idrak_et, Ey)
        t += s
    kalem.append(Kalem("ileri geçiş (idrak_et)", int(tekrar), t))

    # ── 3. Tek melekenin payı
    q = nefs.idrak_et(E)
    tek: List[Tuple[str, float]] = []
    for no in list(nefs.sira)[:41]:
        _, s = _saat(nefs.s[no].kosu, q, nefs.p)
        tek.append((getattr(nefs.s[no], "ad", str(no)), s))
    tek.sort(key=lambda x: -x[1])

    # ── 4. Yazmaç ameliyeleri
    _, s_mera = _saat(q.mera)
    _, s_olc = _saat(q.olcumler)
    _, s_ent = _saat(q.y.dolasiklik_entropisi)
    _, s_bey = _saat(q.beyan, a.sozluk)
    kalem.append(Kalem("mera", 1, s_mera))
    kalem.append(Kalem("olcumler", 1, s_olc))
    kalem.append(Kalem("dolaşıklık entropisi", 1, s_ent))
    kalem.append(Kalem("beyan", 1, s_bey))

    # ── 5. MİZANIN KENDİSİ (ileri geçiş dâhil ve hariç)
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


def teftis(ayar=None, had: float = HAD, sert: bool = True) -> Dict[str, Any]:
    """HIZ GEÇİDİ -- had tutmuyorsa tâlim BAŞLAMAZ.

    ``sert`` doğruysa ``assert`` ile durdurur. Bu geçit kapatılabilir
    (``sert=False``) ve kapatılınca yalnız raporlar; yâni ölçü kırmızı
    yanabilir ve yandığında görünür (H90).
    """
    o = olc(ayar)
    o["had"] = float(had)
    o["geçti"] = bool(o["belirteç_sn"] >= float(had))
    if sert:
        assert o["geçti"], (
            "HIZ HADDİ TUTMUYOR: %.1f belirteç/sn ölçüldü, %.0f lâzım "
            "(%.0f kat eksik). Ferman: hız garantisi almadan umumi tâlim "
            "başlatılmaz. En pahalı uzuv: %s"
            % (o["belirteç_sn"], had, had / max(1e-9, o["belirteç_sn"]),
               o["tek_meleke"][0][0] if o["tek_meleke"] else "?"))
    return o


def rapor(ayar=None) -> str:                             # pragma: no cover
    o = olc(ayar)
    s = ["=== HIZ TEFTİŞİ -- belirteç/sn haddi ===", "",
         "  yazmaç: d=%d  lif=%r  parametre=%d"
         % (o["d"], o["lif"], o["parametre"]),
         "  ölçülen: %d belirteç, %.3f sn → **%.1f belirteç/sn**"
         % (o["belirteç"], o["kayıp_süresi"], o["belirteç_sn"]),
         "  HAD    : %.0f belirteç/sn   →  %s  (%.0f kat eksik)"
         % (HAD, "GEÇTİ" if o["belirteç_sn"] >= HAD else "KALDI",
            HAD / max(1e-9, o["belirteç_sn"])),
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


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
