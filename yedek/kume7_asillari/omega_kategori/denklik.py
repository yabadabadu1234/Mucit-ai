"""
Glue tipleri için Kan hesabı -- tümel değişmezliğin HESAPLANAN zemini.

İki kural burada imâl edilir:

  1) ``cizgi_denkligi`` (lineToEquiv):  bir tip çizgisinden denklik.
     Hile şudur: taşımanın denklik olduğunu ayrıca ispatlamak yerine,
     ÖZDEŞLİK DENKLİĞİNİ denklik-tipleri çizgisi boyunca taşırız:

         cizgi_denkligi^i A  :=  transp^i (Denklik A(0) A(i)) ⊥ (idEquiv A(0))

     ``i=0``da ``Denklik A(0) A(0)`` içinde ``idEquiv``dir; ``i=1``de
     ``Denklik A(0) A(1)``. Bu yalnız Σ/Π/Path'te transp gerektirir --
     hepsi çekirdekte zaten var. Böylece ``comp^i U`` işler.

  2) ``komp_yapistir``:  ``comp^i (Glue A [φ ↦ (T,w)]) [ψ ↦ b] b0``
     CCHM (2018) §6.2. Silsile şudur:

         δ    = ∀i.φ
         a    = unglue b,   a0 = unglue b0
         a'1  = comp^i A [ψ ↦ a] a0
         t'1  = comp^i T [ψ ↦ b] b0                      (δ üzerinde)
         ω    = pres^i w.1 [ψ ↦ b] b0                    (δ üzerinde)
         (t1,α) = denklikle_tamamla w(1) [ψ ↦ (b(1),refl), δ ↦ (t'1,ω)] a'1
         a1   = hcomp^j A(1) [ψ ↦ a(1), φ(1) ↦ α(~j)] a'1
         netice = glue [φ(1) ↦ t1] a1

     ``t1`` ve ``α``, ``φ(1)``in HER YÜZÜ için ayrı ayrı, o yüze
     kısıtlanmış bağlamda hesaplanır; ``T`` yalnız orada mevcuttur.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from .aralik import (BIR, DOGRU, SIFIR, YANLIS, Aralik, Kofibrasyon,
                     yuzu_atamaya_cevir)
from . import cekirdek as K
from . import sozdizim as S
from .sozdizim import Terim, Yuz


class EksikKural(NotImplementedError):
    """Bu çekirdekte henüz imâl edilmemiş bir indirgeme kuralı."""


# =====================================================================
#  ∀i.φ
# =====================================================================
def her_i_icin(kof: Kofibrasyon, ad: str) -> Kofibrasyon:
    """``∀ad. kof``: ``ad``i kısıtlamayan yüzlerin birleşimi."""
    return Kofibrasyon([y for y in kof.yuzler
                        if all(a != ad for (a, _) in y)])


def _yuz_i_den_bagimsiz(y: Yuz, ad: str) -> bool:
    return all(a != ad for (a, _) in y)


# =====================================================================
#  Büzülebilirlikten kısmî elemanı tamamlama
# =====================================================================
def buzukten_tamamla(X: Terim, buzuk: Terim,
                     dallar: Sequence[Tuple[Yuz, Terim]]) -> Terim:
    """``buzuk : isContr X`` ve kısmî bir ``X`` elemanı verildiğinde onu
    genişleten TAM bir eleman: ``hcomp^j [dallar ↦ h(dal) @ j] c``."""
    c = K.birinci(buzuk)
    h = K.ikinci(buzuk)
    j = K.taze("j")
    j_ar = Aralik.degisken(j)
    yeni = [(y, K.yol_uygula(K.uygula(h, govde), j_ar))
            for (y, govde) in dallar]
    return K.hkomp(X, j, yeni, c)


def denklikle_tamamla(A: Terim, B: Terim, e: Terim, b: Terim,
                      dallar: Sequence[Tuple[Yuz, Terim]]) -> Terim:
    """``e : Denklik A B``, ``b : B``, ve ``lif(e.1, b)`` üzerinde kısmî bir
    eleman verildiğinde tam bir lif elemanı ``(t, α)`` üretir.

    CCHM'nin ``equiv^ψ`` işlemidir; Glue hesabının kalbi budur.
    """
    from .kutuphane import lif
    X = lif(A, B, K.birinci(e), b)
    buzuk = K.uygula(K.ikinci(e), b)
    return buzukten_tamamla(X, buzuk, dallar)


# =====================================================================
#  1) Tip çizgisinden denklik
# =====================================================================
def cizgi_denkligi(ad: str, cizgi: Terim) -> Terim:
    """``Denklik cizgi(0) cizgi(1)``.

    ``transp^ad (Denklik cizgi(0) cizgi(ad)) ⊥ (idEquiv cizgi(0))``
    """
    from .kutuphane import denklik_tipi, ozdeslik_denkligi
    c0 = K.ara_ikame(cizgi, {ad: SIFIR})
    return K.transp(ad, denklik_tipi(c0, cizgi), YANLIS,
                    ozdeslik_denkligi(c0))


# =====================================================================
#  pres -- comp'un fonksiyonla değişmesi
# =====================================================================
def pres(i: str, A_cizgi: Terim, T_cizgi: Terim, f_i: Terim, f_0: Terim,
         psi_dallar: Sequence[Tuple[Yuz, Terim]], u0: Terim) -> Terim:
    """``ω : Path A(1) (f(1) (comp^i T [ψ↦u] u0)) (comp^i A [ψ↦ f i (u i)] (f(0) u0))``

    ``ω = <j> comp^i A [ψ ↦ f i (u i), (j=1) ↦ f i (fill^i T [ψ↦u] u0)] (f(0) u0)``
    """
    j = K.taze("j")
    tfill = K.dolgu(i, T_cizgi, psi_dallar, u0)
    dallar = [(y, K.uygula(f_i, govde)) for (y, govde) in psi_dallar]
    dallar.append((S.yuz(**{j: 1}), K.uygula(f_i, tfill)))
    return S.YolLam(j, K.komp(i, A_cizgi, dallar, K.uygula(f_0, u0)))


# =====================================================================
#  2) comp^i (Glue ...)
# =====================================================================
def komp_yapistir(i: str, A_glue: S.Yapistir, psi_dallar, u0: Terim,
                  baglam=None) -> Terim:
    A = A_glue.taban            # A : i ↦ U
    G = A_glue.dallar           # ((yuz, T, e), ...) -- yüzler i içerebilir

    def parcalar(sigma: Dict[str, Aralik]):
        taban = K.ara_ikame(A, sigma)
        dallar = K._dallar_ara_ikame(G, sigma,
                                     lambda x: K.ara_ikame(x, sigma))
        return taban, dallar

    A0, G0 = parcalar({i: SIFIR})
    A1, G1 = parcalar({i: BIR})

    # --- taban tipe düşür ---
    a0 = K.coz(A0, G0, u0)
    psi_a = [(y, K.coz(A, G, govde)) for (y, govde) in psi_dallar]
    ap1 = K.komp(i, A, psi_a, a0, baglam)

    # --- δ = ∀i.φ : yüzü i'den bağımsız olan Glue dalları ---
    delta_dallari = [(y, T, e) for (y, T, e) in G if _yuz_i_den_bagimsiz(y, i)]

    t1_dallar: List[Tuple[Yuz, Terim]] = []
    alfa_dallar: List[Tuple[Yuz, Terim]] = []

    for (y1, T1, e1) in G1:
        sig = yuzu_atamaya_cevir(y1)
        A1s = K.ara_ikame(A1, sig)
        T1s = K.ara_ikame(T1, sig)
        e1s = K.ara_ikame(e1, sig)
        ap1s = K.ara_ikame(ap1, sig)

        kismi: List[Tuple[Yuz, Terim]] = []

        # (a) ψ üzerinde: lif elemanı (b(1), refl a'1)
        for (yp, govde) in psi_dallar:
            kof = Kofibrasyon([yp]).yerine_koy(sig)
            if kof.bos_mu():
                continue
            for yf in kof.yuzler:
                sg = dict(sig)
                sg.update(yuzu_atamaya_cevir(yf))
                kismi.append((yf, S.Cift(
                    K.ara_ikame(K.ara_ikame(govde, {i: BIR}), sg),
                    S.YolLam("_", K.ara_ikame(ap1, sg)))))

        # (b) δ üzerinde: (t'1, ω)
        for (yd, Td, ed) in delta_dallari:
            kof = Kofibrasyon([yd]).yerine_koy(sig)
            if kof.bos_mu():
                continue
            for yf in kof.yuzler:
                sg = dict(sig)
                sg.update(yuzu_atamaya_cevir(yf))
                Tds = K.ara_ikame(Td, sg)
                eds = K.ara_ikame(ed, sg)
                As = K.ara_ikame(A, sg)
                u0s = K.ara_ikame(u0, sg)
                psi_s: List[Tuple[Yuz, Terim]] = []
                for (yp, govde) in psi_dallar:
                    kp = Kofibrasyon([yp]).yerine_koy(sg)
                    if kp.bos_mu():
                        continue
                    gs = K.ara_ikame(govde, sg)
                    for yq in kp.yuzler:
                        psi_s.append((yq, gs))
                tp1 = K.komp(i, Tds, psi_s, u0s, baglam)
                f_i = K.birinci(eds)
                f_0 = K.birinci(K.ara_ikame(eds, {i: SIFIR}))
                omega = pres(i, As, Tds, f_i, f_0, psi_s, u0s)
                kismi.append((yf, S.Cift(tp1, omega)))

        tam = denklikle_tamamla(T1s, A1s, e1s, ap1s, kismi)
        t1_dallar.append((y1, K.birinci(tam)))
        alfa_dallar.append((y1, K.ikinci(tam)))

    # --- a1 : taban tipte, φ(1) üzerinde w(1).1 t1'e oturur ---
    j = K.taze("j")
    j_ar = Aralik.degisken(j)
    a1_dallar: List[Tuple[Yuz, Terim]] = []
    for (yp, govde) in psi_dallar:
        b1 = K.ara_ikame(govde, {i: BIR})
        a1_dallar.append((yp, K.coz(A1, G1, b1)))
    for (y1, alfa) in alfa_dallar:
        a1_dallar.append((y1, K.yol_uygula(alfa, j_ar.degil())))
    a1 = K.hkomp(A1, j, a1_dallar, ap1)

    return K.yapistir_terim(t1_dallar, a1)
