"""Terimleri okunur biçimde yazdırma."""
from __future__ import annotations

from . import sozdizim as S


def _yuz_yaz(y) -> str:
    if not y:
        return "⊤"
    return "∧".join(sorted("(%s=%d)" % (ad, 1 if d else 0) for (ad, d) in y))


def _sistem_yaz(dallar) -> str:
    return ", ".join("%s ↦ %s" % (_yuz_yaz(y), terimi_yaz(t)) for (y, t) in dallar)


def terimi_yaz(t) -> str:
    y = terimi_yaz
    if isinstance(t, S.Deg):
        return t.ad
    if isinstance(t, S.Evren):
        return "U" if t.seviye == 0 else "U%d" % t.seviye
    if isinstance(t, S.Pi):
        if t.ad == "_":
            return "(%s → %s)" % (y(t.alan), y(t.hedef))
        return "((%s : %s) → %s)" % (t.ad, y(t.alan), y(t.hedef))
    if isinstance(t, S.Lam):
        return "(λ %s. %s)" % (t.ad, y(t.govde))
    if isinstance(t, S.Uygula):
        return "(%s %s)" % (y(t.fonk), y(t.arg))
    if isinstance(t, S.Sigma):
        if t.ad == "_":
            return "(%s × %s)" % (y(t.alan), y(t.hedef))
        return "((%s : %s) × %s)" % (t.ad, y(t.alan), y(t.hedef))
    if isinstance(t, S.Cift):
        return "(%s , %s)" % (y(t.bir), y(t.iki))
    if isinstance(t, S.Birinci):
        return "%s.1" % y(t.cift)
    if isinstance(t, S.Ikinci):
        return "%s.2" % y(t.cift)
    if isinstance(t, S.YolP):
        if t.ad == "_":
            return "(Path %s %s %s)" % (y(t.cizgi), y(t.sol), y(t.sag))
        return "(PathP (λ %s. %s) %s %s)" % (t.ad, y(t.cizgi), y(t.sol), y(t.sag))
    if isinstance(t, S.YolLam):
        return "(<%s> %s)" % (t.ad, y(t.govde))
    if isinstance(t, S.YolUygula):
        return "(%s @ %r)" % (y(t.yol), t.r)
    if isinstance(t, S.Transp):
        return "transp (λ %s. %s) %r %s" % (t.ad, y(t.cizgi), t.kof, y(t.u0))
    if isinstance(t, S.Komp):
        return "comp (λ %s. %s) [%s] %s" % (t.ad, y(t.cizgi),
                                            _sistem_yaz(t.dallar), y(t.u0))
    if isinstance(t, S.HKomp):
        return "hcomp {%s} (λ %s) [%s] %s" % (y(t.tip), t.ad,
                                              _sistem_yaz(t.dallar), y(t.u0))
    if isinstance(t, S.Yapistir):
        ic = ", ".join("%s ↦ (%s, %s)" % (_yuz_yaz(f), y(T), y(e))
                       for (f, T, e) in t.dallar)
        return "Glue %s [%s]" % (y(t.taban), ic)
    if isinstance(t, S.YapistirTerim):
        return "glue [%s] %s" % (_sistem_yaz(t.dallar), y(t.taban_terim))
    if isinstance(t, S.Coz):
        return "unglue %s" % y(t.govde)
    if isinstance(t, S.Dogal):
        return "ℕ"
    if isinstance(t, S.Sfr):
        return "0"
    if isinstance(t, S.Ard):
        n, alt = 0, t
        while isinstance(alt, S.Ard):
            n += 1
            alt = alt.alt
        if isinstance(alt, S.Sfr):
            return str(n)
        return "(%d+%s)" % (n, y(alt))
    if isinstance(t, S.DogalInd):
        return "natInd(...; %s)" % y(t.sayi)
    if isinstance(t, S.Tamsayi):
        return "ℤ"
    if isinstance(t, S.Poz):
        return "+%s" % y(t.alt)
    if isinstance(t, S.NegArd):
        return "-(1+%s)" % y(t.alt)
    if isinstance(t, S.TamsayiInd):
        return "intInd(...; %s)" % y(t.sayi)
    if isinstance(t, S.Cember):
        return "S¹"
    if isinstance(t, S.Taban):
        return "taban"
    if isinstance(t, S.Dongu):
        return "(dongu %r)" % t.r
    if isinstance(t, S.CemberInd):
        return "S¹ind(...; %s)" % y(t.nokta)
    return object.__repr__(t)
