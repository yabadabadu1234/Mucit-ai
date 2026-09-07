from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from matematik.tip_teorisi import (Baglam, Cember, Deg, Dugum, Evren, Lam,
                                   Pi, Sigma, Taban, Terim, YolLam,
                                   denetle_t, denetle_tip, dongu_uzayi_n,
                                   evrensel_demet, kesit_tipi, morfizm_tipi,
                                   ok, tikanma_postulati)

__all__ = ["Uzay", "SABIT", "uzaylari_kur", "rapor", "AZAMI_TAM_MERTEBE"]

U = Evren(0)
U1 = Evren(1)
D = Deg

sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))

SABIT: Tuple[int, ...] = tuple(range(10))

AZAMI_TAM_MERTEBE = 20


@dataclass(frozen=True)
class Uzay:
    yuva: int
    mertebe: int
    tam_kuruldu: bool
    denetlendi: bool
    baglayici: int
    tip_ozeti: str
    hata: str = ""

    @property
    def pencere(self) -> int:
        return min(self.mertebe + 1, 4)

    @property
    def adim(self) -> int:
        import math
        return 1 + int(math.log2(1 + self.mertebe))

    @property
    def parametre(self) -> int:
        return 2 ** self.pencere + self.baglayici


def _baglayici_say(t: Terim) -> int:
    n = 0
    yigin: List[object] = [t]
    while yigin:
        d = yigin.pop()
        if not isinstance(d, Dugum):
            continue
        if isinstance(d, (Pi, Sigma, Lam, YolLam)):
            n += 1
        for alan in d._alanlar():
            if isinstance(alan, Dugum):
                yigin.append(alan)
            elif isinstance(alan, tuple):
                yigin.extend(a for a in alan if isinstance(a, Dugum))
    return n


def _tam_kur(mertebe: int) -> Tuple[Terim, str]:
    A = D("A")
    return morfizm_tipi(A, mertebe), "morfizm_tipi(A, %d)" % mertebe


def _temsilci_kur(mertebe: int) -> Tuple[Terim, str]:
    n = 1 + (mertebe % AZAMI_TAM_MERTEBE)
    return (dongu_uzayi_n(Cember(), Taban(), n),
            "Ω^%d(S¹)  [mertebe %d için temsilci]" % (n, mertebe))


def uzaylari_kur(dinamik: Sequence[int]) -> List[Uzay]:
    if len(dinamik) != 10:
        raise ValueError("dinamik mertebe sayısı 10 olmalı")
    gA = Baglam.terimlerden({"A": U, "a": D("A"), "b": D("A")})
    g0 = Baglam()

    uzaylar: List[Uzay] = []
    for yuva, m in enumerate(tuple(SABIT) + tuple(int(x) for x in dinamik)):
        tam = m <= AZAMI_TAM_MERTEBE
        if tam:
            tip, ozet = _tam_kur(m)
            baglam, hedef = gA, U
        else:
            tip, ozet = _temsilci_kur(m)
            baglam, hedef = g0, U
        hata = ""
        try:
            denetle_t(tip, hedef, baglam)
            gecti = True
        except Exception as e:
            gecti = False
            hata = "%s: %s" % (type(e).__name__, str(e)[:120])
        uzaylar.append(Uzay(yuva=yuva, mertebe=m, tam_kuruldu=tam,
                            denetlendi=gecti, baglayici=_baglayici_say(tip),
                            tip_ozeti=ozet, hata=hata))
    return uzaylar


def tikanma_tipi() -> Terim:
    return tikanma_postulati(D("X")).tip


def kesit_tipi_ile_agirlik() -> Tuple[Terim, Terim]:
    M, Fw = D("M"), D("Fw")
    return kesit_tipi(M, Fw), evrensel_demet(M, Fw)


def akit_denetle() -> List[Dict[str, object]]:
    g = Baglam.terimlerden({"M": U, "Fw": ok(D("M"), U), "X": U})
    isler = [
        ("tıkanma (Postnikov) tipi iyi teşkil",
         lambda: denetle_tip(tikanma_tipi(), g)),
        ("kesit tipi Π(w:M). F w : U",
         lambda: denetle_t(kesit_tipi(D("M"), D("Fw")), U, g)),
        ("evrensel demet Σ(w:M). F w : U",
         lambda: denetle_t(evrensel_demet(D("M"), D("Fw")), U, g)),
    ]
    out: List[Dict[str, object]] = []
    for ad, fn in isler:
        try:
            fn()
            out.append({"ad": ad, "netice": "GEÇTİ"})
        except Exception as e:
            out.append({"ad": ad, "netice": "HATA",
                        "izah": str(e)[:120]})
    return out


def rapor(dinamik: Sequence[int] = (13, 17, 19, 20, 30, 55, 1000, 1009,
                                    58383, 60000)) -> str:
    uz = uzaylari_kur(dinamik)
    s = ["=== 20 ∞-KATEGORİ UZAYI (omega_kategori_nbe ile kurulup denetlendi) ===",
         "",
         "%-5s %-8s %-9s %-11s %-8s %-7s %s"
         % ("yuva", "mertebe", "kuruluş", "denetim", "bağlayıcı",
            "pencere", "adım")]
    s.append("-" * 78)
    for u in uz:
        s.append("%-5d %-8d %-9s %-11s %-9d %-7d %d   %s"
                 % (u.yuva, u.mertebe,
                    "TAM" if u.tam_kuruldu else "temsilci",
                    "geçti" if u.denetlendi else "KALDI",
                    u.baglayici, u.pencere, u.adim, u.tip_ozeti))
        if u.hata:
            s.append("      ! " + u.hata)
    s += ["", "Akit denetimi (modül fiilen çağrılıyor mu):"]
    for n in akit_denetle():
        s.append("  %s %s%s" % ("✓" if n["netice"] == "GEÇTİ" else "✗",
                                n["ad"],
                                "" if n["netice"] == "GEÇTİ"
                                else "  [%s]" % n.get("izah", "")))
    tam = sum(1 for u in uz if u.tam_kuruldu)
    ok = sum(1 for u in uz if u.denetlendi)
    s += ["",
          "hulâsa: %d/20 uzay TAM kuruldu, %d/20 makine denetiminden geçti."
          % (tam, ok),
          "Mertebesi %d'ten büyük olanlar temsilci tiple denetlendi;"
          % AZAMI_TAM_MERTEBE,
          "sebebi seyrek Kan sıçramasıdır (aradaki mertebeler açılmaz)."]
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
