"""
Teğet yapısı, tensörler ve monoid nesneleri -- uzayla BERABER gelen paket.

Buradaki iddia şudur: bir uzay teşkil edildiği anda teğeti, kotanjantı,
tensörleri ve üzerindeki cebirsel işlem kaideleri sonradan yamalanan
unsurlar değil, iç dilin (internal language) tabii elemanlarıdır. Bu dosya
o "paketi" fiilen kurar ve her parçasını tip denetiminden geçirir.

Silsile:

  1. Sonsuz küçükler:  ``D = Σ (x:R). x·x = 0``
  2. Teğet demeti HARİTALAMA UZAYI olarak:  ``TX := X^D = (D → X)``
     Lifleri ``T_x X = Σ (v : D → X). v(0) = x``.
  3. ``R``-modül yapısı (vektör demetinin lifi), doğrusal dönüşümler, dual.
  4. Çok-doğrusal dönüşümler ve ``(r,s)`` mertebesinden tensör tipi:
     ``r`` tane kovektör + ``s`` tane vektör ↦ skaler.
  5. Monoid nesnesi (``μ``, ``η``): ``Mod_R`` içinde bir monoid nesnesi tam
     olarak birleşmeli birimli ``R``-cebridir.
  6. Lie yapısı: köşeli parantez, antisimetri, Jacobi -- ve Jacobi'nin bir
     ÜST MERTEBEDEN yol ile koherensi.
  7. de Rham: alterne formlar, ``d`` işlemcisi (postulat) ve ``d∘d = 0``.

Kanunlar KATI eşitlik değil YOL olarak ifade edilir; kümeler üzerinde bu
klasik denklem davranışını verir, daha yüksek mertebede ise koherens
kuleleri kendiliğinden açılır.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

from . import cekirdek as K
from . import kutuphane as L
from . import sozdizim as S
from . import turetimler as T
from .denetleyici import Baglam, denetle, denetle_tip
from .sozdizim import Terim

U = S.Evren(0)
U1 = S.Evren(1)
D = S.Deg


# =====================================================================
#  SDG bağlamı
# =====================================================================
def sdg_baglami() -> Baglam:
    """``R`` ve halka işlemleri postulat olarak eklenmiş bağlam."""
    return T.postulat_baglami(T.sdg_postulatlari())


R = D("R")
TOP = D("top_R")
CARP = D("carp_R")
SIFIR_R = D("sifir_R")


def _top(a: Terim, b: Terim) -> Terim:
    return K.uygula(K.uygula(TOP, a), b)


def _carp(a: Terim, b: Terim) -> Terim:
    return K.uygula(K.uygula(CARP, a), b)


# =====================================================================
#  1. Sonsuz küçükler ve 2. teğet demeti
# =====================================================================
def sonsuz_kucukler() -> Terim:
    """``D = Σ (x : R). Path R (x·x) 0`` -- birinci mertebeden sonsuz küçükler."""
    x = K.taze("x")
    return S.Sigma(x, R, S.yol(R, _carp(D(x), D(x)), SIFIR_R))


def sifir_sonsuz_kucuk() -> Terim:
    """``0 ∈ D``: sıfırın karesi sıfırdır (halka aksiyomundan gelir;
    burada tanık POSTULAT olarak istenir)."""
    return S.Cift(SIFIR_R, D("sifir_kare"))


def teget_demeti(X: Terim) -> Terim:
    """``TX := X^D = (D → X)`` -- teğet demeti HARİTALAMA UZAYIDIR.

    Uzayı kurmak, teğetini de kurmaktır: ayrıca bir inşa gerekmez.
    """
    return S.ok(sonsuz_kucukler(), X)


def teget_izdusum(X: Terim) -> Terim:
    """``π : TX → X``, ``v ↦ v(0)``."""
    v = K.taze("v")
    return S.Lam(v, K.uygula(D(v), sifir_sonsuz_kucuk()))


def teget_lifi(X: Terim, x: Terim) -> Terim:
    """``T_x X = Σ (v : D → X). Path X (v 0) x`` -- ``x``teki teğet uzayı."""
    v = K.taze("v")
    return S.Sigma(v, teget_demeti(X),
                   S.yol(X, K.uygula(D(v), sifir_sonsuz_kucuk()), x))


# =====================================================================
#  3. R-modül yapısı
# =====================================================================
class Modul:
    """Bir ``R``-modülün taşıyıcısı ve işlemleri (terimler)."""

    __slots__ = ("V", "top", "sifir", "eks", "skaler")

    def __init__(self, V: Terim, top: Terim, sifir: Terim,
                 eks: Terim, skaler: Terim) -> None:
        self.V, self.top, self.sifir = V, top, sifir
        self.eks, self.skaler = eks, skaler

    def art(self, a: Terim, b: Terim) -> Terim:
        return K.uygula(K.uygula(self.top, a), b)

    def carp(self, c: Terim, a: Terim) -> Terim:
        return K.uygula(K.uygula(self.skaler, c), a)


def modul_tipi() -> Terim:
    """``Mod_R``: ``R`` üzerinde modül yapısının tipi."""
    V, top, sf, eks, sk = D("V"), D("top"), D("sf"), D("eks"), D("sk")
    x, y, z, c, d_ = D("x"), D("y"), D("z"), D("c"), D("d")
    A = lambda a, b: K.uygula(K.uygula(top, a), b)
    Sm = lambda c_, a: K.uygula(K.uygula(sk, c_), a)
    P = lambda ad, tip, govde: S.Pi(ad, tip, govde)
    return T.sigma_hepsi([
        ("V", U),
        ("kume", L.iz_kume(V)),
        ("top", S.ok(V, S.ok(V, V))),
        ("sf", V),
        ("eks", S.ok(V, V)),
        ("sk", S.ok(R, S.ok(V, V))),
        ("top_birlesme", P("x", V, P("y", V, P("z", V,
            S.yol(V, A(A(x, y), z), A(x, A(y, z))))))),
        ("top_degisme", P("x", V, P("y", V, S.yol(V, A(x, y), A(y, x))))),
        ("top_birim", P("x", V, S.yol(V, A(sf, x), x))),
        ("top_ters", P("x", V, S.yol(V, A(K.uygula(eks, x), x), sf))),
        ("sk_dagilma_V", P("c", R, P("x", V, P("y", V,
            S.yol(V, Sm(c, A(x, y)), A(Sm(c, x), Sm(c, y))))))),
        ("sk_dagilma_R", P("c", R, P("d", R, P("x", V,
            S.yol(V, Sm(_top(c, d_), x), A(Sm(c, x), Sm(d_, x))))))),
    ], P("c", R, P("d", R, P("x", V,
        S.yol(V, Sm(_carp(c, d_), x), Sm(c, Sm(d_, x)))))))


def dogrusal_mi(M: Modul, N: Modul, f: Terim) -> Terim:
    """``f : M.V → N.V`` doğrusal mı? (toplamsal + homojen)"""
    x, y, c = K.taze("x"), K.taze("y"), K.taze("c")
    uy = K.uygula
    toplamsal = S.Pi(x, M.V, S.Pi(y, M.V,
        S.yol(N.V, uy(f, M.art(D(x), D(y))),
                   N.art(uy(f, D(x)), uy(f, D(y))))))
    homojen = S.Pi(c, R, S.Pi(x, M.V,
        S.yol(N.V, uy(f, M.carp(D(c), D(x))),
                   N.carp(D(c), uy(f, D(x))))))
    return S.carpim(toplamsal, homojen)


def skaler_modulu() -> Modul:
    """``R``nin kendisi bir ``R``-modüldür; skalerler burada yaşar."""
    return Modul(R, TOP, SIFIR_R, D("eks_R"), CARP)


def dual(M: Modul) -> Terim:
    """``M* = Σ (f : V → R). f doğrusal`` -- kotanjant tarafı."""
    f = K.taze("f")
    return S.Sigma(f, S.ok(M.V, R), dogrusal_mi(M, skaler_modulu(), D(f)))


# =====================================================================
#  4. Çok-doğrusal dönüşümler ve tensörler
# =====================================================================
def cok_dogrusal_tip(yuvalar: Sequence[Terim], hedef: Terim) -> Terim:
    """``V₁ → V₂ → … → W`` -- çok-doğrusal dönüşümün TAŞIYICI tipi."""
    sonuc = hedef
    for V in reversed(list(yuvalar)):
        sonuc = S.ok(V, sonuc)
    return sonuc


def _yuvada_dogrusal(moduller: Sequence[Modul], N: Modul, f: Terim,
                     k: int) -> Terim:
    """``f``nin ``k``ıncı yuvada doğrusal olduğu şartı; öbür yuvalar
    serbest değişken olarak evrensel nicelenir."""
    adlar = [K.taze("a%d" % n) for n in range(len(moduller))]
    x, y, c = K.taze("x"), K.taze("y"), K.taze("c")

    def uygula_hepsi(kth: Terim) -> Terim:
        arg = [D(a) for a in adlar]
        arg[k] = kth
        sonuc = f
        for a in arg:
            sonuc = K.uygula(sonuc, a)
        return sonuc

    toplamsal = S.yol(N.V,
        uygula_hepsi(moduller[k].art(D(x), D(y))),
        N.art(uygula_hepsi(D(x)), uygula_hepsi(D(y))))
    homojen = S.yol(N.V,
        uygula_hepsi(moduller[k].carp(D(c), D(x))),
        N.carp(D(c), uygula_hepsi(D(x))))
    govde = S.Pi(x, moduller[k].V, S.Pi(y, moduller[k].V,
        S.carpim(toplamsal,
                 S.Pi(c, R, S.Pi(x, moduller[k].V, homojen)))))
    for n, a in enumerate(adlar):
        if n != k:
            govde = S.Pi(a, moduller[n].V, govde)
    return govde


def tensor_tipi(M: Modul, r: int, s: int) -> Terim:
    """``(r,s)`` mertebesinden tensörün tipi.

    ``r`` tane KOVEKTÖR (dual eleman) ve ``s`` tane VEKTÖR alıp skaler
    veren çok-doğrusal dönüşüm. Klasik ``T^{⊗r} ⊗ (T*)^{⊗s}`` demetinin
    global kesitinin iç dildeki karşılığı budur.
    """
    yuvalar = [dual(M)] * r + [M.V] * s
    return cok_dogrusal_tip(yuvalar, R)


def tensor_yapisi(M: Modul, r: int, s: int,
                  dualM: Optional[Modul] = None) -> Terim:
    """``(r,s)``-tensör YAPISI: taşıyıcı çok-doğrusal dönüşüm + HER
    yuvada doğrusallık şartı. Tensörü "yalnız bir fonksiyon"dan ayıran
    şart budur.

    ``r > 0`` ise dual yuvalar için ``M*`` üzerinde de bir modül yapısı
    gerekir; ``dualM`` ile verilir (noktasal yapı, burada teşkil edilmez).
    """
    if dualM is None:
        dualM = Modul(dual(M), D("dtop"), D("dsf"), D("deks"), D("dsk"))
    moduller = [dualM] * r + [M] * s
    f = K.taze("f")
    tasiyici = cok_dogrusal_tip([m.V for m in moduller], R)
    sartlar: List[Tuple[str, Terim]] = [(f, tasiyici)]
    for n in range(len(moduller)):
        sartlar.append(("dogrusal_%d" % n,
                        _yuvada_dogrusal(moduller, skaler_modulu(), D(f), n)))
    son = sartlar.pop()[1]
    return T.sigma_hepsi(sartlar, son)


def teget_tensoru(X: Terim, x: Terim, r: int, s: int) -> Terim:
    """``x`` noktasında ``(r,s)`` tensörlerinin tipi -- teğet lifinden
    doğrudan doğar; ayrıca bir demet inşası GEREKMEZ."""
    Tx = teget_lifi(X, x)
    M = Modul(Tx, D("teget_top"), D("teget_sifir"), D("teget_eks"),
              D("teget_skaler"))
    return tensor_tipi(M, r, s)


# =====================================================================
#  5. Monoid nesnesi = R-cebri (μ, η)
# =====================================================================
def cebir_tipi() -> Terim:
    """``Mod_R`` içindeki monoid nesnesi: ``μ : A⊗A → A``, ``η : 1 → A``.

    ``⊗`` iç dilde çok-doğrusallıkla temsil edildiğinden ``μ`` iki-doğrusal
    bir dönüşümdür; ``η`` bir noktadır (``1 = R``den gelen birim).
    """
    A, top, sf, eks, sk = D("A"), D("top"), D("sf"), D("eks"), D("sk")
    mu, eta = D("mu"), D("eta")
    x, y, z, c = D("x"), D("y"), D("z"), D("c")
    Ad = lambda a, b: K.uygula(K.uygula(top, a), b)
    Sm = lambda c_, a: K.uygula(K.uygula(sk, c_), a)
    M = lambda a, b: K.uygula(K.uygula(mu, a), b)
    P = S.Pi
    return T.sigma_hepsi([
        ("A", U),
        ("kume", L.iz_kume(A)),
        ("top", S.ok(A, S.ok(A, A))),
        ("sf", A),
        ("eks", S.ok(A, A)),
        ("sk", S.ok(R, S.ok(A, A))),
        ("mu", S.ok(A, S.ok(A, A))),        # μ : A ⊗ A → A
        ("eta", A),                          # η : 1 → A
        ("mu_birlesme", P("x", A, P("y", A, P("z", A,
            S.yol(A, M(M(x, y), z), M(x, M(y, z))))))),
        ("eta_sol", P("x", A, S.yol(A, M(eta, x), x))),
        ("eta_sag", P("x", A, S.yol(A, M(x, eta), x))),
        ("mu_dagilma_sol", P("x", A, P("y", A, P("z", A,
            S.yol(A, M(x, Ad(y, z)), Ad(M(x, y), M(x, z))))))),
        ("mu_dagilma_sag", P("x", A, P("y", A, P("z", A,
            S.yol(A, M(Ad(x, y), z), Ad(M(x, z), M(y, z))))))),
    ], P("c", R, P("x", A, P("y", A,
        S.yol(A, M(Sm(c, x), y), Sm(c, M(x, y)))))))


# =====================================================================
#  6. Lie yapısı ve koherens kulesi
# =====================================================================
def lie_tipi() -> Terim:
    """Lie cebri: ``[·,·]``, antisimetri, Jacobi.

    Jacobi bir YOL olarak ifade edilir; kümeler mertebesinde bu klasik
    özdeşliktir, daha yüksek mertebede ise ``lie_koherens`` ile bir üst
    mertebeden yol talep edilebilir.
    """
    V, top, sf, eks, sk, br = (D("V"), D("top"), D("sf"), D("eks"),
                               D("sk"), D("br"))
    x, y, z = D("x"), D("y"), D("z")
    Ad = lambda a, b: K.uygula(K.uygula(top, a), b)
    B = lambda a, b: K.uygula(K.uygula(br, a), b)
    P = S.Pi
    jacobi = P("x", V, P("y", V, P("z", V,
        S.yol(V, Ad(Ad(B(B(x, y), z), B(B(y, z), x)), B(B(z, x), y)), sf))))
    return T.sigma_hepsi([
        ("V", U),
        ("kume", L.iz_kume(V)),
        ("top", S.ok(V, S.ok(V, V))),
        ("sf", V),
        ("eks", S.ok(V, V)),
        ("sk", S.ok(R, S.ok(V, V))),
        ("br", S.ok(V, S.ok(V, V))),
        ("antisimetri", P("x", V, P("y", V,
            S.yol(V, B(x, y), K.uygula(eks, B(y, x)))))),
        ("br_dagilma", P("x", V, P("y", V, P("z", V,
            S.yol(V, B(x, Ad(y, z)), Ad(B(x, y), B(x, z))))))),
    ], jacobi)


def koherens_kulesi(V: Terim, sol: Terim, sag: Terim, n: int) -> Terim:
    """``sol`` ile ``sag`` arasındaki ``n``inci mertebeden koherens tipi.

    ``n=1``: iki terim arasındaki yol (klasik özdeşlik).
    ``n=2``: iki yol arasındaki yol (özdeşliğin İSPATLARI arasındaki
             koherens) -- "katı eşitlik değil, bir üst mertebeden morfizm"
             iddiasının fiilî karşılığı.
    """
    tip = S.yol(V, sol, sag)
    nokta = L.refl(sol)
    for _ in range(n - 1):
        tip, nokta = S.yol(tip, nokta, nokta), L.refl(nokta)
    return tip


# =====================================================================
#  7. de Rham
# =====================================================================
def alterne_form_tipi(M: Modul, n: int) -> Terim:
    """``n``-form: ``n`` tane vektör alıp skaler veren çok-doğrusal
    dönüşüm (alternelik ayrı bir şart olarak istenir)."""
    return cok_dogrusal_tip([M.V] * n, R)


def form_uzayi(X: Terim, n: int) -> Terim:
    """``Ωⁿ(X) = Π (x:X). (T_x X)ⁿ → R``"""
    x = K.taze("x")
    return S.Pi(x, X, alterne_form_tipi(
        Modul(teget_lifi(X, D(x)), D("teget_top"), D("teget_sifir"),
              D("teget_eks"), D("teget_skaler")), n))


def de_rham_postulatlari(X: Terim, n: int) -> List[T.Postulat]:
    """``d : Ωⁿ → Ωⁿ⁺¹`` ve ``d∘d = 0``.

    POSTULATTIR: dış türevin hesaplanan bir kuralı bu çekirdekte yoktur.
    Tipleri denetlenir; sakinleri aksiyomdur.
    """
    om_n, om_n1, om_n2 = (form_uzayi(X, n), form_uzayi(X, n + 1),
                          form_uzayi(X, n + 2))
    w = K.taze("w")
    dd = S.Pi(w, om_n, S.yol(om_n2,
        K.uygula(D("d_%d1" % n), K.uygula(D("d_%d" % n), D(w))),
        D("sifir_form")))
    return [
        T.Postulat("d_%d" % n, S.ok(om_n, om_n1),
                   "Dış türev Ωⁿ → Ωⁿ⁺¹."),
        T.Postulat("d_%d1" % n, S.ok(om_n1, om_n2),
                   "Dış türev Ωⁿ⁺¹ → Ωⁿ⁺²."),
        T.Postulat("sifir_form", om_n2, "Sıfır form."),
        T.Postulat("dd_sifir", dd, "d∘d = 0 -- de Rham kompleksinin şartı."),
    ]


# =====================================================================
#  Doğrulama
# =====================================================================
def _geometri_baglami() -> Baglam:
    g = sdg_baglami()
    Dt = sonsuz_kucukler()
    X = D("X")
    g = g.genislet("sifir_kare", S.yol(R, _carp(SIFIR_R, SIFIR_R), SIFIR_R))
    g = g.genislet("eks_R", S.ok(R, R))
    g = g.genislet("X", U)
    g = g.genislet("x", X)
    Tx = teget_lifi(X, D("x"))
    g = g.genislet("teget_top", S.ok(Tx, S.ok(Tx, Tx)))
    g = g.genislet("teget_sifir", Tx)
    g = g.genislet("teget_eks", S.ok(Tx, Tx))
    g = g.genislet("teget_skaler", S.ok(R, S.ok(Tx, Tx)))
    return g


def dogrula_hepsi() -> List[Dict[str, str]]:
    g = _geometri_baglami()
    X, x = D("X"), D("x")
    M = Modul(D("V"), D("Vtop"), D("Vsf"), D("Veks"), D("Vsk"))
    gM = (g.genislet("V", U)
           .genislet("Vtop", S.ok(D("V"), S.ok(D("V"), D("V"))))
           .genislet("Vsf", D("V"))
           .genislet("Veks", S.ok(D("V"), D("V")))
           .genislet("Vsk", S.ok(R, S.ok(D("V"), D("V")))))
    dV = dual(M)
    dM = Modul(dV, D("dtop"), D("dsf"), D("deks"), D("dsk"))
    gMd = (gM.genislet("dtop", S.ok(dV, S.ok(dV, dV)))
             .genislet("dsf", dV)
             .genislet("deks", S.ok(dV, dV))
             .genislet("dsk", S.ok(R, S.ok(dV, dV))))
    isler: List[Tuple[str, Callable[[], None]]] = [
        ("D (sonsuz küçükler) : U", lambda: denetle(sonsuz_kucukler(), U, g)),
        ("0 ∈ D", lambda: denetle(sifir_sonsuz_kucuk(), sonsuz_kucukler(), g)),
        ("TX = X^D : U", lambda: denetle(teget_demeti(X), U, g)),
        ("π : TX → X", lambda: denetle(teget_izdusum(X),
                                       S.ok(teget_demeti(X), X), g)),
        ("T_x X : U", lambda: denetle(teget_lifi(X, x), U, g)),
        ("Mod_R : U₁", lambda: denetle(modul_tipi(), U1, g)),
        ("M* (dual) : U", lambda: denetle(dual(M), U, gM)),
        ("(1,0)-tensör : U", lambda: denetle(tensor_tipi(M, 1, 0), U, gM)),
        ("(0,2)-tensör (metrik) : U",
         lambda: denetle(tensor_tipi(M, 0, 2), U, gM)),
        ("(1,3)-tensör (Riemann) : U",
         lambda: denetle(tensor_tipi(M, 1, 3), U, gM)),
        ("(0,2)-tensör YAPISI (çok-doğrusallık şartlı) : U",
         lambda: denetle(tensor_yapisi(M, 0, 2), U, gM)),
        ("(1,1)-tensör YAPISI (dual yuvalı) : U",
         lambda: denetle(tensor_yapisi(M, 1, 1, dM), U, gMd)),
        ("teğet (0,2)-tensörü : U",
         lambda: denetle(teget_tensoru(X, x, 0, 2), U, g)),
        ("R-cebri (monoid nesnesi μ,η) : U₁",
         lambda: denetle(cebir_tipi(), U1, g)),
        ("Lie cebri (Jacobi dâhil) : U₁",
         lambda: denetle(lie_tipi(), U1, g)),
        ("Ω⁰(X) : U", lambda: denetle(form_uzayi(X, 0), U, g)),
        ("Ω²(X) : U", lambda: denetle(form_uzayi(X, 2), U, g)),
    ]
    neticeler = [T._dene(ad, f) for ad, f in isler]

    # koherens kulesi: 1., 2., 3. mertebe
    a, b = D("a"), D("b")
    gk = g.genislet("A", U).genislet("a", D("A")).genislet("b", D("A"))
    for n in (1, 2, 3):
        neticeler.append(T._dene(
            "koherens kulesi mertebe %d : U" % n,
            lambda n=n: denetle(koherens_kulesi(D("A"), a, a, n), U, gk)))

    # de Rham postulatlarının tipleri iyi teşkil mi?
    gd = g
    for p in de_rham_postulatlari(X, 1):
        neticeler.append(T._dene("POSTULAT tipi iyi teşkil: %s" % p.ad,
                                 lambda p=p, gd=gd: denetle_tip(p.tip, gd)))
        gd = gd.genislet(p.ad, p.tip)
    return neticeler


def rapor() -> str:
    satirlar = ["=" * 66, "omega_kategori.geometri -- teğet / tensör / cebir",
                "=" * 66, ""]
    gecti = kaldi = 0
    for n in dogrula_hepsi():
        im = {"GEÇTİ": "  ✓ ", "EKSİK KURAL": "  ⊘ ", "HATA": "  ✗ "}[n["netice"]]
        satirlar.append("%s%s%s" % (im, n["ad"],
                                    "" if n["netice"] == "GEÇTİ"
                                    else "   [%s] %s" % (n["netice"],
                                                         n.get("izah", ""))))
        gecti += n["netice"] == "GEÇTİ"
        kaldi += n["netice"] != "GEÇTİ"
    satirlar += ["", "hulâsa: %d geçti, %d kaldı" % (gecti, kaldi), "=" * 66]
    return "\n".join(satirlar)
