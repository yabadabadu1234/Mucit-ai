from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from matematik.sonsuz_mertebeler_teorisi import (
    MERTEBE_ADI, Baglam, Cember, Deg, Dugum, Evren, Lam, Pi, Sigma, Taban,
    Terim, YolLam, denetle_t, denetle_tip, dongu_uzayi_n, evrensel_demet,
    iz_butun, iz_grupoid, iz_kume, iz_onerme, kesit_tipi, mertebe_sarti,
    morfizm_tipi, n_mertebe, ok, tikanma_postulati)

__all__ = ["Uzay", "SABIT", "uzaylari_kur", "rapor", "AZAMI_TAM_MERTEBE",
           "h_mertebe_sec", "h_sarti_denetle", "kategori_beyani"]

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
    h_mertebe: int = -1
    h_adi: str = ""
    h_denetlendi: bool = False
    h_hata: str = ""

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


def h_mertebe_sec(mertebe: int) -> int:
    return int(min(max(int(mertebe), 0), len(MERTEBE_ADI) - 1))


def h_sarti_denetle(mertebe: int, baglam: Baglam) -> Tuple[int, str, bool, str]:
    l = h_mertebe_sec(mertebe)
    try:
        denetle_t(mertebe_sarti(Deg("A"), l), Evren(0), baglam)
        return l, MERTEBE_ADI[l], True, ""
    except Exception as e:
        return l, MERTEBE_ADI[l], False, "%s: %s" % (type(e).__name__,
                                                     str(e)[:120])


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
        hl, had, hg, hh = h_sarti_denetle(m, gA)
        uzaylar.append(Uzay(yuva=yuva, mertebe=m, tam_kuruldu=tam,
                            denetlendi=gecti, baglayici=_baglayici_say(tip),
                            tip_ozeti=ozet, hata=hata,
                            h_mertebe=hl, h_adi=had,
                            h_denetlendi=hg, h_hata=hh))
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


def kategori_beyani(uzaylar: Sequence[Uzay]) -> str:
    uz = list(uzaylar)
    s = ["=== YİRMİ ∞-KATEGORİ UZAYI (idrak/kategori.py) ===", "",
         "  %-5s %-8s %-9s %-11s %-9s %-7s %-4s %-10s %s"
         % ("yuva", "mertebe", "kuruluş", "denetim", "bağlayıcı",
            "pencere", "adım", "h-mertebe", "tip"),
         "  " + "-" * 96]
    for u in uz:
        s.append("  %-5d %-8d %-9s %-11s %-9d %-7d %-4d %-10s %s"
                 % (u.yuva, u.mertebe,
                    "TAM" if u.tam_kuruldu else "temsilci",
                    "geçti" if u.denetlendi else "KALDI",
                    u.baglayici, u.pencere, u.adim,
                    "%s%s" % (u.h_adi, "" if u.h_denetlendi else "!"),
                    u.tip_ozeti))
        if u.hata:
            s.append("        ! " + u.hata)
        if u.h_hata:
            s.append("        ! h-mertebe: " + u.h_hata)
    s += ["",
          "  H-MERTEBE (ferman 1-Ğ: vechin mertebesi diziden okunur)",
          "    nokta=büzülebilir · uzay=önerme · kategori=küme · "
          "tip=grupoid ve üstü",
          "    ``n_mertebe`` ile kurulur, ``denetle_t`` ile DENETLENİR;",
          "    bu dördü omega_kategori'den geri getirilen cevherlerdir.",
          "",
          "  Akit denetimi (modül fiilen çağrılıyor mu):"]
    for n in akit_denetle():
        s.append("    %s %s%s" % ("✓" if n["netice"] == "GEÇTİ" else "✗",
                                  n["ad"],
                                  "" if n["netice"] == "GEÇTİ"
                                  else "  [%s]" % n.get("izah", "")))
    tam = sum(1 for u in uz if u.tam_kuruldu)
    gecen = sum(1 for u in uz if u.denetlendi)
    h_gecen = sum(1 for u in uz if u.h_denetlendi)
    s += ["",
          "  hulâsa: %d/%d uzay TAM kuruldu, %d/%d makine denetiminden "
          "geçti, %d/%d h-mertebe şartı denetlendi."
          % (tam, len(uz), gecen, len(uz), h_gecen, len(uz)),
          "  Mertebesi %d'ten büyük olanlar temsilci tiple denetlendi;"
          % AZAMI_TAM_MERTEBE,
          "  sebebi seyrek Kan sıçramasıdır (aradaki mertebeler açılmaz)."]
    return "\n".join(s)
