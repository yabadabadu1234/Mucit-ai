"""
Glue'nun Kan hesabı -- DEĞER seviyesinde (NbE).

Terim sürümüyle aynı CCHM (2018) §6.2 silsilesidir; farkı, her şeyin
değer ve çizgi (``ACizgi``) olarak kurulmasıdır. Bütün ara çizgiler
``ATuretilmis`` veri kurucularıdır, dolayısıyla aralık ikamesi (``act``)
altında doğru davranırlar.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from .aralik import (BIR, DOGRU, SIFIR, YANLIS, Aralik, Kofibrasyon,
                     aralik_esitligi, yuzu_atamaya_cevir)
from . import cekirdek as C
from . import kutuphane as L
from . import sozdizim as S
from .cekirdek import (ACizgi, ASabit, ATuretilmis, AYeniden, BOS, Deger,
                       Ortam, Sistem, bir, coz, degerlendir, dolgu, hkomp,
                       iki, komp, taze, transp, uygula, yapistir,
                       yapistir_terim, _dallari_act)


class EksikKural(NotImplementedError):
    pass


# --- bir kere kurulan sözdizim şablonları -----------------------------
_A0, _AR, _AA, _BB, _FF, _BSC = (S.Deg("!A0"), S.Deg("!Ar"), S.Deg("!A"),
                                 S.Deg("!B"), S.Deg("!f"), S.Deg("!b"))
_DENKLIK_T = L.denklik_tipi(_A0, _AR)
_IDEQ_T = L.ozdeslik_denkligi(_A0)
_LIF_T = L.lif(_AA, _BB, _FF, _BSC)


class GlueHam:
    """Glue'nun HAM bileşenleri.

    ``DYapistir`` değeri ``act`` altında bir yüz ⊤ olunca ``T``ye ÇÖKER;
    hesabın ortasında taban ve dalların kaybolmaması için ham hâlleri
    ayrıca taşınır.
    """

    __slots__ = ("taban", "dallar")

    def __init__(self, taban, dallar) -> None:
        self.taban, self.dallar = taban, tuple(dallar)

    def act(self, s) -> "GlueHam":
        return GlueHam(self.taban.act(s), _dallari_act(self.dallar, s))


def her_i_icin(kof: Kofibrasyon, ad: str) -> Kofibrasyon:
    """``∀ad. kof`` -- ``ad``i kısıtlamayan yüzlerin birleşimi."""
    return Kofibrasyon([y for y in kof.yuzler
                        if all(a != ad for (a, _) in y)])


# =====================================================================
#  Tip çizgisinden denklik (comp^i U'nun dayanağı)
# =====================================================================
def _denklik_cizgi(al, r):
    c0, hat = al
    return degerlendir(_DENKLIK_T,
                       BOS.genislet("!A0", c0).genislet("!Ar", hat.uygula(r)))


def cizgi_denkligi(hat: ACizgi) -> Deger:
    """``Denklik hat(0) hat(1)``.

    Özdeşlik denkliğini ``Denklik hat(0) hat(r)`` çizgisi boyunca taşır;
    yalnız Σ/Π/Path'te ``transp`` gerektirir.
    """
    c0 = hat.uygula(SIFIR)
    idq = degerlendir(_IDEQ_T, BOS.genislet("!A0", c0))
    return transp(ATuretilmis(_denklik_cizgi, (c0, hat)), YANLIS, idq)


# =====================================================================
#  comp^i U
# =====================================================================
def komp_evren(hat: ACizgi, sistem: Sistem, u0: Deger) -> Deger:
    dallar = []
    for (y, c) in sistem:
        k = taze("k")
        ters = AYeniden(c, k, Aralik.degisken(k).degil())
        dallar.append((y, c.uygula(BIR), cizgi_denkligi(ters)))
    return yapistir(u0, dallar)


# =====================================================================
#  Büzülebilirlikten kısmî elemanı tamamlama
# =====================================================================
def _buzme_c(al, j):
    h, v = al
    return C.yol_uygula(uygula(h, v), j)


def denklikle_tamamla(A: Deger, B: Deger, e: Deger, b: Deger,
                      kismi: Sequence[Tuple[frozenset, Deger]]) -> Deger:
    """``e : Denklik A B``, ``b : B`` ve kısmî lif elemanı → tam lif elemanı."""
    X = degerlendir(_LIF_T, BOS.genislet("!A", A).genislet("!B", B)
                    .genislet("!f", bir(e)).genislet("!b", b))
    buzuk = uygula(iki(e), b)
    return hkomp(X, Sistem([(y, ATuretilmis(_buzme_c, (iki(buzuk), v)))
                            for (y, v) in kismi]), bir(buzuk))


# =====================================================================
#  pres -- comp'un fonksiyonla değişmesi
# =====================================================================
def _act_cizgi(al, r):
    """``λr. deger.act({ad: r})``"""
    d, ad = al
    return d.act({ad: r})


def _uyg_bir_c(al, r):
    """``λr. (e(r)).1 (c(r))``"""
    e_hat, c = al
    return uygula(bir(e_hat.uygula(r)), c.uygula(r))


def _pres_c(al, j):
    A_hat, T_hat, e_hat, psi, u0 = al
    tfill = dolgu(T_hat, psi, u0)
    dallar = [(y, ATuretilmis(_uyg_bir_c, (e_hat, c))) for (y, c) in psi]
    for f in aralik_esitligi(j, True).yuzler:
        dallar.append((f, ATuretilmis(_uyg_bir_c, (e_hat, tfill))))
    f0 = bir(e_hat.uygula(SIFIR))
    return komp(A_hat, Sistem(dallar), uygula(f0, u0))


# =====================================================================
#  comp^i (Glue …)
# =====================================================================
def _glue_taban_c(al, r):
    gh, ad = al
    return gh.taban.act({ad: r})


def _unglue_c(al, r):
    gh, ad, c = al
    return coz(gh.taban.act({ad: r}), _dallari_act(gh.dallar, {ad: r}),
               c.uygula(r))


def _alfa_ters_c(al, j):
    (alfa,) = al
    return C.yol_uygula(alfa, j.degil())


def komp_yapistir(hat: ACizgi, sistem: Sistem, u0: Deger) -> Deger:
    i = taze("i")
    Ai = hat.uygula(Aralik.degisken(i))          # DYapistir (yüzler i içerebilir)
    if not isinstance(Ai, C.DYapistir):
        raise EksikKural("komp_yapistir: Glue bekleniyordu")

    gh = GlueHam(Ai.taban, Ai.dallar)
    A_hat = ATuretilmis(_glue_taban_c, (gh, i))
    G0 = _dallari_act(Ai.dallar, {i: SIFIR})
    G1 = _dallari_act(Ai.dallar, {i: BIR})
    A0 = Ai.taban.act({i: SIFIR})
    A1 = Ai.taban.act({i: BIR})

    a0 = coz(A0, G0, u0)
    psi_a = Sistem([(y, ATuretilmis(_unglue_c, (gh, i, c)))
                    for (y, c) in sistem])
    ap1 = komp(A_hat, psi_a, a0)

    phi = Kofibrasyon([y for (y, _, _) in Ai.dallar])
    delta_dallari = [(y, T, e) for (y, T, e) in Ai.dallar
                     if all(a != i for (a, _) in y)]

    t1_dallar: List[Tuple[frozenset, Deger]] = []
    alfa_dallar: List[Tuple[frozenset, Deger]] = []

    for (y1, T1, e1) in G1:
        sig = yuzu_atamaya_cevir(y1)
        A1s, T1s, e1s, ap1s = (A1.act(sig), T1.act(sig), e1.act(sig),
                               ap1.act(sig))
        kismi: List[Tuple[frozenset, Deger]] = []

        # (a) ψ üzerinde: (b(1), refl a'1)
        for (yp, c) in sistem:
            k = Kofibrasyon([yp]).yerine_koy(sig)
            if k.bos_mu():
                continue
            for yf in k.yuzler:
                sg = dict(sig)
                sg.update(yuzu_atamaya_cevir(yf))
                kismi.append((yf, C.DCift(c.uygula(BIR).act(sg),
                                          C.DYolLam(ASabit(ap1.act(sg))))))

        # (b) δ üzerinde: (t'1, ω)
        for (yd, Td, ed) in delta_dallari:
            k = Kofibrasyon([yd]).yerine_koy(sig)
            if k.bos_mu():
                continue
            for yf in k.yuzler:
                sg = dict(sig)
                sg.update(yuzu_atamaya_cevir(yf))
                T_hat = ATuretilmis(_act_cizgi, (Td.act(sg), i))
                e_hat = ATuretilmis(_act_cizgi, (ed.act(sg), i))
                As = ATuretilmis(_glue_taban_c, (gh.act(sg), i))
                psi_s = sistem.act(sg)
                u0s = u0.act(sg)
                tp1 = komp(T_hat, psi_s, u0s)
                omega = C.DYolLam(ATuretilmis(
                    _pres_c, (As, T_hat, e_hat, psi_s, u0s)))
                kismi.append((yf, C.DCift(tp1, omega)))

        tam = denklikle_tamamla(T1s, A1s, e1s, ap1s, kismi)
        t1_dallar.append((y1, bir(tam)))
        alfa_dallar.append((y1, iki(tam)))

    a1_dallar = [(y, ASabit(coz(A1, G1, c.uygula(BIR))))
                 for (y, c) in sistem]
    a1_dallar += [(y1, ATuretilmis(_alfa_ters_c, (alfa,)))
                  for (y1, alfa) in alfa_dallar]
    a1 = hkomp(A1, Sistem(a1_dallar), ap1)
    return yapistir_terim(t1_dallar, a1)
