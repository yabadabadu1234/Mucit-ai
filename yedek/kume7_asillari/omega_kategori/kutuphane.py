"""
Nesne dilinde yazılmış temel kütüphane.

Buradaki her şey ``sozdizim`` terimidir ve ``denetleyici`` tarafından
makine ile doğrulanabilir. Python tarafı yalnız terim İNŞA eder; hiçbir
matematiksel iddia Python'da "kabul edilmez".

Kapsam:
  * ∞-grupoid yapısı: refl, ters, terkip, esle (ap), taşıma
  * J (yol tümevarımı)
  * büzülebilirlik / önerme / küme / grupoid mertebeleri (h-seviyeleri)
  * lif, denklik (equivalence), özdeşlik denkliği
  * ua (tümel değişmezliğin yol hâlinde ifadesi)
  * S¹ araçları
"""
from __future__ import annotations

from typing import Optional

from .aralik import BIR, SIFIR, YANLIS, Aralik
from . import cekirdek as K
from . import sozdizim as S
from .sozdizim import Terim

U = S.Evren(0)
U1 = S.Evren(1)


def _t(ad: str) -> Terim:
    return S.Deg(ad)


# =====================================================================
#  ∞-grupoid yapısı
# =====================================================================
def refl(a: Terim) -> Terim:
    """``refl a : Path A a a``"""
    return S.YolLam("_", a)


def ters(A: Terim, a: Terim, b: Terim, p: Terim) -> Terim:
    """``p⁻¹ : Path A b a``"""
    i, j = K.taze("i"), K.taze("j")
    return S.YolLam(i, S.HKomp(A, j,
        [(S.yuz(**{i: 0}), K.yol_uygula(p, Aralik.degisken(j))),
         (S.yuz(**{i: 1}), a)], a))


def terkip(A: Terim, a: Terim, b: Terim, c: Terim,
           p: Terim, q: Terim) -> Terim:
    """``p ∙ q : Path A a c``"""
    i, j = K.taze("i"), K.taze("j")
    return S.YolLam(i, S.HKomp(A, j,
        [(S.yuz(**{i: 0}), a),
         (S.yuz(**{i: 1}), K.yol_uygula(q, Aralik.degisken(j)))],
        K.yol_uygula(p, Aralik.degisken(i))))


def esle(A: Terim, B: Terim, f: Terim, a: Terim, b: Terim, p: Terim) -> Terim:
    """``ap f p : Path B (f a) (f b)``"""
    i = K.taze("i")
    return S.YolLam(i, S.Uygula(f, K.yol_uygula(p, Aralik.degisken(i))))


def tasi(P: Terim, x: Terim) -> Terim:
    """``transport : Path U A B → A → B``  (``P`` bir tip yoludur)"""
    i = K.taze("i")
    return S.Transp(i, K.yol_uygula(P, Aralik.degisken(i)), YANLIS, x)


def aile_tasi(C: Terim, p: Terim, x: Terim) -> Terim:
    """``C : A → U`` ailesinde ``p : Path A a b`` boyunca taşıma."""
    i = K.taze("i")
    return S.Transp(i, S.Uygula(C, K.yol_uygula(p, Aralik.degisken(i))),
                    YANLIS, x)


def yol_tumevarimi(A: Terim, a: Terim, C: Terim, d: Terim,
                   b: Terim, p: Terim) -> Terim:
    """J: ``C : (b:A) → Path A a b → U`` ve ``d : C a (refl a)`` verildiğinde
    ``J A a C d b p : C b p``.

    Kübik ispat: ``transp^i (C (p@i) (<j> p@(i∧j))) ⊥ d``.
    """
    i, j = K.taze("i"), K.taze("j")
    i_ar, j_ar = Aralik.degisken(i), Aralik.degisken(j)
    kismi_yol = S.YolLam(j, K.yol_uygula(p, i_ar.ve(j_ar)))
    cizgi = S.Uygula(S.Uygula(C, K.yol_uygula(p, i_ar)), kismi_yol)
    return S.Transp(i, cizgi, YANLIS, d)


# =====================================================================
#  Homotopi mertebeleri (h-seviyeleri)
# =====================================================================
def iz_butun(X: Terim) -> Terim:
    """``isContr X = Σ (x:X). Π (y:X). Path X x y``"""
    x, y = K.taze("x"), K.taze("y")
    return S.Sigma(x, X, S.Pi(y, X, S.yol(X, _t(x), _t(y))))


def iz_onerme(X: Terim) -> Terim:
    """``isProp X = Π (x y : X). Path X x y``"""
    x, y = K.taze("x"), K.taze("y")
    return S.Pi(x, X, S.Pi(y, X, S.yol(X, _t(x), _t(y))))


def iz_kume(X: Terim) -> Terim:
    """``isSet X = Π (x y : X). isProp (Path X x y)``"""
    x, y = K.taze("x"), K.taze("y")
    return S.Pi(x, X, S.Pi(y, X, iz_onerme(S.yol(X, _t(x), _t(y)))))


def iz_grupoid(X: Terim) -> Terim:
    """``isGroupoid X = Π (x y : X). isSet (Path X x y)``"""
    x, y = K.taze("x"), K.taze("y")
    return S.Pi(x, X, S.Pi(y, X, iz_kume(S.yol(X, _t(x), _t(y)))))


def n_mertebe(X: Terim, n: int) -> Terim:
    """``n``-mertebeli olma şartı; ``n = -2`` büzülebilir, ``-1`` önerme,
    ``0`` küme, ``1`` grupoid, ... şeklinde yukarı çıkar."""
    if n <= -2:
        return iz_butun(X)
    if n == -1:
        return iz_onerme(X)
    x, y = K.taze("x"), K.taze("y")
    return S.Pi(x, X, S.Pi(y, X, n_mertebe(S.yol(X, _t(x), _t(y)), n - 1)))


def dongu_uzayi(A: Terim, a: Terim) -> Terim:
    """``Ω(A,a) = Path A a a``"""
    return S.yol(A, a, a)


def dongu_uzayi_n(A: Terim, a: Terim, n: int) -> Terim:
    """``Ωⁿ(A,a)`` -- yineli döngü uzayı."""
    if n <= 0:
        return A
    if n == 1:
        return dongu_uzayi(A, a)
    alt = dongu_uzayi_n(A, a, n - 1)
    return S.yol(alt, refl_n(A, a, n - 1), refl_n(A, a, n - 1))


def refl_n(A: Terim, a: Terim, n: int) -> Terim:
    """``Ωⁿ``nin taban noktası (yineli refl)."""
    nokta = a
    for _ in range(n):
        nokta = refl(nokta)
    return nokta


# =====================================================================
#  Lif, denklik
# =====================================================================
def lif(A: Terim, B: Terim, f: Terim, b: Terim) -> Terim:
    """``fiber f b = Σ (a:A). Path B (f a) b``"""
    a = K.taze("a")
    return S.Sigma(a, A, S.yol(B, S.Uygula(f, _t(a)), b))


def iz_denklik(A: Terim, B: Terim, f: Terim) -> Terim:
    """``isEquiv f = Π (b:B). isContr (fiber f b)``"""
    b = K.taze("b")
    return S.Pi(b, B, iz_butun(lif(A, B, f, _t(b))))


def denklik_tipi(A: Terim, B: Terim) -> Terim:
    """``Equiv A B = Σ (f : A → B). isEquiv f``"""
    f = K.taze("f")
    return S.Sigma(f, S.ok(A, B), iz_denklik(A, B, _t(f)))


def ozdeslik_denkligi(A: Terim) -> Terim:
    """``idEquiv A : Equiv A A``

    Büzülebilirlik ispatı, tekil-lif büzülmesinin kübik hâlidir:
    ``<i> ( z.2 @ ~i , <j> z.2 @ (~i ∨ j) )``.
    """
    x, b, z = K.taze("x"), K.taze("b"), K.taze("z")
    i, j = K.taze("i"), K.taze("j")
    i_ar, j_ar = Aralik.degisken(i), Aralik.degisken(j)
    p = S.Ikinci(_t(z))
    merkez = S.Cift(_t(b), refl(_t(b)))
    buzme = S.Lam(z, S.YolLam(i, S.Cift(
        K.yol_uygula(p, i_ar.degil()),
        S.YolLam(j, K.yol_uygula(p, i_ar.degil().veya(j_ar))))))
    return S.Cift(S.Lam(x, _t(x)),
                  S.Lam(b, S.Cift(merkez, buzme)))


def denklik_fonksiyonu(e: Terim) -> Terim:
    return S.Birinci(e)


# =====================================================================
#  Tümel değişmezlik (univalence) -- yol hâlinde
# =====================================================================
def ua(A: Terim, B: Terim, e: Terim) -> Terim:
    """``ua e : Path U A B``

    ``ua e = <i> Glue B [ (i=0) ↦ (A, e), (i=1) ↦ (B, idEquiv B) ]``

    Uçlarda Glue çöker: ``ua e @ 0 = A``, ``ua e @ 1 = B`` (tanımsal).
    """
    i = K.taze("i")
    return S.YolLam(i, S.Yapistir(B, [
        (S.yuz(**{i: 0}), A, e),
        (S.yuz(**{i: 1}), B, ozdeslik_denkligi(B)),
    ]))


# =====================================================================
#  S¹ araçları
# =====================================================================
def cember_rec(hedef: Terim, taban_dali: Terim, dongu_dali_ad: str,
               dongu_dali: Terim, nokta: Terim) -> Terim:
    """Bağımsız (non-dependent) S¹ özyinelemesi."""
    return S.CemberInd("_", hedef, taban_dali, dongu_dali_ad, dongu_dali, nokta)


def dongu() -> Terim:
    """``dongu : Path S¹ taban taban``"""
    i = K.taze("i")
    return S.YolLam(i, S.Dongu(Aralik.degisken(i)))


def dongu_tersi() -> Terim:
    """``dongu⁻¹ = <i> dongu(~i)`` -- S¹'in KENDİ simetrisi.

    Genel ``ters`` (yol tersleme) bir ``hcomp`` kurar; S¹ döngüsünde ise
    aralık involüsyonu ``~i`` doğrudan ters yolu verir. İkisi de aynı tipin
    sakinidir ve tip denetiminden geçer, fakat sade olan iç içe hcomp
    doğurmadığı için sarım hesabını ÖLÇÜLEN biçimde 245 kat hızlandırır
    (dongu⁻⁵: 27.4 s → 0.11 s).
    """
    i = K.taze("i")
    return S.YolLam(i, S.Dongu(Aralik.degisken(i).degil()))


def dongu_kuvveti(n: int) -> Terim:
    """``dongu`` yolunun ``n`` kez terkibi (n<0 ise ``dongu⁻¹`` ile)."""
    A, a = S.Cember(), S.Taban()
    if n == 0:
        return refl(a)
    tek = dongu() if n > 0 else dongu_tersi()
    sonuc = tek
    for _ in range(abs(n) - 1):
        sonuc = terkip(A, a, a, a, sonuc,
                       dongu() if n > 0 else dongu_tersi())
    return sonuc


def dongu_kuvveti_genel_ters(n: int) -> Terim:
    """Aynı yol, fakat GENEL ``ters`` ile kurulmuş hâli.

    Yalnız kıyas ve sağlama için tutulur: iki inşanın da aynı sarım
    sayısını vermesi, sadeleştirmenin doğruluğunun sınamasıdır.
    """
    A, a = S.Cember(), S.Taban()
    if n == 0:
        return refl(a)
    tek = dongu() if n > 0 else ters(A, a, a, dongu())
    sonuc = tek
    for _ in range(abs(n) - 1):
        sonuc = terkip(A, a, a, a, sonuc, tek)
    return sonuc


# =====================================================================
#  ℤ üzerinde ardıl / öncel
# =====================================================================
def ardil_z() -> Terim:
    """``sucZ : ℤ → ℤ``"""
    n = K.taze("n")
    m = K.taze("m")
    # poz k        ↦ poz (k+1)
    # negArd 0     ↦ poz 0
    # negArd (k+1) ↦ negArd k
    neg_dali = S.DogalInd("_", S.Tamsayi(), S.Poz(S.Sfr()),
                          m, "_r", S.NegArd(_t(m)), _t(n))
    return S.Lam("z", S.TamsayiInd("_", S.Tamsayi(),
                                   n, S.Poz(S.Ard(_t(n))),
                                   n, neg_dali,
                                   _t("z")))


def oncel_z() -> Terim:
    """``predZ : ℤ → ℤ``"""
    n = K.taze("n")
    m = K.taze("m")
    # poz 0     ↦ negArd 0
    # poz (k+1) ↦ poz k
    # negArd k  ↦ negArd (k+1)
    poz_dali = S.DogalInd("_", S.Tamsayi(), S.NegArd(S.Sfr()),
                          m, "_r", S.Poz(_t(m)), _t(n))
    return S.Lam("z", S.TamsayiInd("_", S.Tamsayi(),
                                   n, poz_dali,
                                   n, S.NegArd(S.Ard(_t(n))),
                                   _t("z")))


# =====================================================================
#  İzomorfizmden denklik (isoToEquiv)
# =====================================================================
def izo_denklige(A: Terim, B: Terim, f: Terim, g: Terim,
                 s: Terim, t: Terim) -> Terim:
    """``f : A→B``, ``g : B→A``, ``s : Π b. f(g b) ≡ b``,
    ``t : Π a. g(f a) ≡ a`` verildiğinde ``Denklik A B``.

    Lifin büzülebilirliği, iki lif elemanını birleştiren bir kare (``sq``)
    ve onun ``s`` ile ``B``ye taşınmışı (``sq1``) üzerinden kurulur; bu,
    yarı-eşlenik (half-adjoint) düzeltmesinin kübik hâlidir.
    """
    y, x0, x1, p0, p1, z = (K.taze("y"), K.taze("x0"), K.taze("x1"),
                            K.taze("p0"), K.taze("p1"), K.taze("z"))
    i, j, k = K.taze("i"), K.taze("j"), K.taze("k")
    I, J, Kk = (Aralik.degisken(i), Aralik.degisken(j), Aralik.degisken(k))
    Y, X0, X1, P0, P1 = _t(y), _t(x0), _t(x1), _t(p0), _t(p1)
    uy = K.uygula

    gy = uy(g, Y)

    def _fill(x, p):
        return K.dolgu(k, A,
            [(S.yuz(**{i: 1}), K.yol_uygula(uy(t, x), Kk)),
             (S.yuz(**{i: 0}), gy)],
            uy(g, K.yol_uygula(p, I.degil())))

    fill0, fill1 = _fill(X0, P0), _fill(X1, P1)
    at = lambda trm, iv, kv: K.ara_ikame(trm, {i: iv, k: kv})

    fill2 = K.dolgu(k, A,
        [(S.yuz(**{i: 1}), at(fill1, Kk, BIR)),
         (S.yuz(**{i: 0}), at(fill0, Kk, BIR))],
        gy)

    p_yol = S.YolLam(i, at(fill2, I, BIR))          # p : Path A x0 x1

    sq = S.HKomp(A, k,
        [(S.yuz(**{i: 1}), at(fill1, J, Kk.degil())),
         (S.yuz(**{i: 0}), at(fill0, J, Kk.degil())),
         (S.yuz(**{j: 0}), gy),
         (S.yuz(**{j: 1}), K.yol_uygula(uy(t, at(fill2, I, BIR)),
                                        Kk.degil()))],
        at(fill2, I, J))                             # i, j serbest

    # sq'nun j yönü p0/p1'e göre TERSİNEDİR: fill1 j (~k) ucu g(p1 @ ~j)
    # verir. Bu yüzden sq1'in i-dallarında p @ ~j, ve j=0/j=1 dalları
    # (g y / f (p i)) sırasıyla yer alır.
    sq1 = S.HKomp(B, k,
        [(S.yuz(**{i: 1}), K.yol_uygula(uy(s, K.yol_uygula(P1, J.degil())),
                                        Kk)),
         (S.yuz(**{i: 0}), K.yol_uygula(uy(s, K.yol_uygula(P0, J.degil())),
                                        Kk)),
         (S.yuz(**{j: 0}), K.yol_uygula(uy(s, Y), Kk)),
         (S.yuz(**{j: 1}), K.yol_uygula(uy(s, uy(f, K.yol_uygula(p_yol, I))),
                                        Kk))],
        uy(f, sq))                                   # i, j serbest

    lem = S.YolLam(i, S.Cift(
        K.yol_uygula(p_yol, I),
        S.YolLam(j, K.ara_ikame(sq1, {j: J.degil()}))))

    # isEquiv f : Π (y:B). isContr (fiber f y)
    merkez = S.Cift(gy, uy(s, Y))
    buzme = S.Lam(z, K.ikame(lem, {x0: gy, p0: uy(s, Y),
                                   x1: S.Birinci(_t(z)),
                                   p1: S.Ikinci(_t(z))}))
    return S.Cift(f, S.Lam(y, S.Cift(merkez, buzme)))


# =====================================================================
#  ℤ üzerinde ardıl bir denkliktir
# =====================================================================
def _z_yol_ispati(dis_govde, ic_sfr, ic_ard, neg_govde) -> Terim:
    """ℤ tümevarımı + poz dalında ℕ tümevarımı ile yol ispatı iskeleti."""
    Z = S.Tamsayi()
    z, n, m = K.taze("z"), K.taze("n"), K.taze("m")
    poz_dali = S.DogalInd(m, dis_govde(S.Poz(_t(m))), ic_sfr,
                          m, "_r", ic_ard(_t(m)), _t(n))
    return S.Lam("w", S.TamsayiInd(z, dis_govde(_t(z)),
                                   n, poz_dali,
                                   n, neg_govde(_t(n)),
                                   _t("w")))


def ardil_oncel() -> Terim:
    """``Π b:ℤ. sucZ (predZ b) ≡ b`` -- her hâlde refl ile kapanır."""
    Z = S.Tamsayi()
    suc, pred = ardil_z(), oncel_z()
    ifade = lambda w: S.yol(Z, K.uygula(suc, K.uygula(pred, w)), w)
    return _z_yol_ispati(
        ifade,
        refl(S.Poz(S.Sfr())),
        lambda m: refl(S.Poz(S.Ard(m))),
        lambda n: refl(S.NegArd(n)))


def oncel_ardil() -> Terim:
    """``Π a:ℤ. predZ (sucZ a) ≡ a``"""
    Z = S.Tamsayi()
    suc, pred = ardil_z(), oncel_z()
    ifade = lambda w: S.yol(Z, K.uygula(pred, K.uygula(suc, w)), w)
    z, n, m = K.taze("z"), K.taze("n"), K.taze("m")
    poz_dali = refl(S.Poz(_t(n)))
    neg_ic = S.DogalInd(m, ifade(S.NegArd(_t(m))), refl(S.NegArd(S.Sfr())),
                        m, "_r", refl(S.NegArd(S.Ard(_t(m)))), _t(n))
    return S.Lam("w", S.TamsayiInd(z, ifade(_t(z)),
                                   n, poz_dali, n, neg_ic, _t("w")))


def ardil_denkligi() -> Terim:
    """``sucEquiv : Denklik ℤ ℤ``"""
    Z = S.Tamsayi()
    return izo_denklige(Z, Z, ardil_z(), oncel_z(),
                        ardil_oncel(), oncel_ardil())


# =====================================================================
#  Sarmal (helix) ve sarım sayısı -- π₁(S¹)
# =====================================================================
def sarmal(nokta: Terim) -> Terim:
    """``helix : S¹ → U``;  ``taban ↦ ℤ``,  ``dongu ↦ ua sucEquiv``."""
    Z = S.Tamsayi()
    i = K.taze("i")
    govde = S.Yapistir(Z, [
        (S.yuz(**{i: 0}), Z, ardil_denkligi()),
        (S.yuz(**{i: 1}), Z, ozdeslik_denkligi(Z)),
    ])
    return S.CemberInd("_", U, Z, i, govde, nokta)


def sarim(p: Terim) -> Terim:
    """``sarim : (Path S¹ taban taban) → ℤ`` -- sarım sayısı."""
    i = K.taze("i")
    cizgi = sarmal(K.yol_uygula(p, Aralik.degisken(i)))
    return S.Transp(i, cizgi, YANLIS, S.Poz(S.Sfr()))
