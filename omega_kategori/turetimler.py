"""
Uzayların çekirdekten türetilmesi + AÇIK aksiyom/boşluk kütüğü.

Bu dosya, "bütün uzaylar tek bir çekirdekten türetilebilir" iddiasının
bu modüldeki fiilî karşılığını verir ve -- daha mühimi -- nerede DURDUĞUNU
açıkça söyler. Üç sınıf vardır:

  (A) HESAPLANAN: çekirdek indirger, tip denetleyici doğrular.
      ∞-grupoid kulesi, h-mertebeleri, Ωⁿ, ayrık kümeler (ℕ, ℤ),
      cebirsel yapılar (monoid/grup/halka), kategoriler, globüler tipler,
      S¹ ve döngü kuvvetleri.

  (B) İFADE EDİLEN ama HESAPLANMAYAN: tipi teşkil edilir ve tip denetiminden
      geçer, lakin indirgeme kuralı bu çekirdekte yok.
      Tümel değişmezlik (ua) boyunca TAŞIMA bunun tek örneğidir.

  (C) POSTULAT: nesne dilinde İSPATLANMAZ, aksiyom olarak eklenir. Tipleri
      yine de makine ile denetlenir (yani "iyi teşkil edilmiş aksiyom"
      olduklarından emin olunur). Pürüzsüz (∞,1)-topos / sentetik
      diferansiyel geometri katmanı buradadır.

``rapor()`` bu üç sınıfı çalıştırıp neticeyi dürüstçe basar.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .aralik import BIR, SIFIR, YANLIS, Aralik
from . import cekirdek as K
from . import kutuphane as L
from . import sozdizim as S
from .denetleyici import Baglam, DenetimHatasi, denetle, sentezle
from .denklik import EksikKural
from .sozdizim import Terim

U = S.Evren(0)
U1 = S.Evren(1)
D = S.Deg


def sigma_hepsi(baglar: Sequence[Tuple[str, Terim]], son: Terim) -> Terim:
    for ad, tip in reversed(list(baglar)):
        son = S.Sigma(ad, tip, son)
    return son


def _ikili(f: Terim, x: Terim, y: Terim) -> Terim:
    return S.Uygula(S.Uygula(f, x), y)


# =====================================================================
#  (A1) ∞-grupoid kulesi
#       Her tip, kendiliğinden bir (∞,∞)-grupoiddir: 0-morfizmleri
#       noktaları, 1-morfizmleri yolları, 2-morfizmleri yollar arası
#       yollar... ve bu sonsuza kadar sürer.
# =====================================================================
def morfizm_tipi(A: Terim, n: int) -> Terim:
    """``A`` içindeki ``n``-morfizmlerin tipi (serbest uçlarla).

    ``n=0`` → ``A``;  ``n=1`` → ``Π x y. Path A x y``;
    ``n=2`` → ``Π x y. Π p q. Path (Path A x y) p q`` ...
    """
    if n <= 0:
        return A
    x, y = K.taze("x"), K.taze("y")
    return S.Pi(x, A, S.Pi(y, A, morfizm_tipi(S.yol(A, D(x), D(y)), n - 1)))


def morfizm_uzayi(A: Terim, x: Terim, y: Terim, n: int) -> Terim:
    """``x`` ile ``y`` arasındaki ``n``-morfizm uzayı (n≥1)."""
    if n <= 1:
        return S.yol(A, x, y)
    raise ValueError("n≥2 için uçları da vermek gerekir; morfizm_tipi kullanın")


def koherens_tipi(A: Terim, n: int) -> Terim:
    """``n``-boyutlu koherensin tipi: ``Ωⁿ``nin bir üst mertebesi.

    "Katı eşitlik değil, bir üst mertebedeki morfizmle eşdeğerlik" iddiası
    tam olarak bu tipin sakinleriyle ifade edilir.
    """
    return morfizm_tipi(A, n + 1)


# =====================================================================
#  (A2) Kümeler: 0-mertebeye indirgeme
# =====================================================================
def kume_tipi() -> Terim:
    """``Küme = Σ (X : U). isSet X`` -- klasik küme kavramı buradan doğar."""
    X = K.taze("X")
    return S.Sigma(X, U, L.iz_kume(D(X)))


def onerme_tipi() -> Terim:
    """``Önerme = Σ (X : U). isProp X``"""
    X = K.taze("X")
    return S.Sigma(X, U, L.iz_onerme(D(X)))


def grupoid_tipi() -> Terim:
    """``Grupoid = Σ (X : U). isGroupoid X``"""
    X = K.taze("X")
    return S.Sigma(X, U, L.iz_grupoid(D(X)))


def n_tip_tipi(n: int) -> Terim:
    """``n``-tiplerin tipi: ``Σ (X:U). n-mertebe X``."""
    X = K.taze("X")
    return S.Sigma(X, U, L.n_mertebe(D(X), n))


# =====================================================================
#  (A3) Cebirsel yapılar -- kümeler üzerine
# =====================================================================
def monoid_tipi() -> Terim:
    X, e, m = D("X"), D("e"), D("m")
    x, y, z = D("x"), D("y"), D("z")
    birlesme = S.Pi("x", X, S.Pi("y", X, S.Pi("z", X,
        S.yol(X, _ikili(m, _ikili(m, x, y), z),
                 _ikili(m, x, _ikili(m, y, z))))))
    sol_birim = S.Pi("x", X, S.yol(X, _ikili(m, e, x), x))
    sag_birim = S.Pi("x", X, S.yol(X, _ikili(m, x, e), x))
    return sigma_hepsi([
        ("X", U),
        ("kume", L.iz_kume(X)),
        ("e", X),
        ("m", S.ok(X, S.ok(X, X))),
        ("birlesme", birlesme),
        ("sol_birim", sol_birim),
    ], sag_birim)


def grup_tipi() -> Terim:
    """Grup: küme + birim + çarpma + ters + kanunlar.

    Kanunlar YOL olarak ifade edilir; küme şartı (0-mertebe) bu yolların
    tekil olmasını, yani klasik cebirdeki "denklem" davranışını sağlar.
    """
    X, e, m, iv = D("X"), D("e"), D("m"), D("iv")
    x, y, z = D("x"), D("y"), D("z")
    birlesme = S.Pi("x", X, S.Pi("y", X, S.Pi("z", X,
        S.yol(X, _ikili(m, _ikili(m, x, y), z),
                 _ikili(m, x, _ikili(m, y, z))))))
    sol_birim = S.Pi("x", X, S.yol(X, _ikili(m, e, x), x))
    sag_birim = S.Pi("x", X, S.yol(X, _ikili(m, x, e), x))
    sol_ters = S.Pi("x", X, S.yol(X, _ikili(m, S.Uygula(iv, x), x), e))
    sag_ters = S.Pi("x", X, S.yol(X, _ikili(m, x, S.Uygula(iv, x)), e))
    return sigma_hepsi([
        ("X", U),
        ("kume", L.iz_kume(X)),
        ("e", X),
        ("m", S.ok(X, S.ok(X, X))),
        ("iv", S.ok(X, X)),
        ("birlesme", birlesme),
        ("sol_birim", sol_birim),
        ("sag_birim", sag_birim),
        ("sol_ters", sol_ters),
    ], sag_ters)


def halka_tipi() -> Terim:
    """Değişmeli halka: toplama grubu + çarpma monoidi + dağılma."""
    X = D("X")
    sf, bir = D("sifir"), D("bir")
    top, carp, eks = D("top"), D("carp"), D("eks")
    x, y, z = D("x"), D("y"), D("z")
    P3 = lambda govde: S.Pi("x", X, S.Pi("y", X, S.Pi("z", X, govde)))
    P1 = lambda govde: S.Pi("x", X, govde)
    P2 = lambda govde: S.Pi("x", X, S.Pi("y", X, govde))
    return sigma_hepsi([
        ("X", U),
        ("kume", L.iz_kume(X)),
        ("sifir", X), ("bir", X),
        ("top", S.ok(X, S.ok(X, X))),
        ("carp", S.ok(X, S.ok(X, X))),
        ("eks", S.ok(X, X)),
        ("top_birlesme", P3(S.yol(X, _ikili(top, _ikili(top, x, y), z),
                                     _ikili(top, x, _ikili(top, y, z))))),
        ("top_degisme", P2(S.yol(X, _ikili(top, x, y), _ikili(top, y, x)))),
        ("top_birim", P1(S.yol(X, _ikili(top, sf, x), x))),
        ("top_ters", P1(S.yol(X, _ikili(top, S.Uygula(eks, x), x), sf))),
        ("carp_birlesme", P3(S.yol(X, _ikili(carp, _ikili(carp, x, y), z),
                                      _ikili(carp, x, _ikili(carp, y, z))))),
        ("carp_degisme", P2(S.yol(X, _ikili(carp, x, y), _ikili(carp, y, x)))),
        ("carp_birim", P1(S.yol(X, _ikili(carp, bir, x), x))),
    ], P3(S.yol(X, _ikili(carp, x, _ikili(top, y, z)),
                   _ikili(top, _ikili(carp, x, y), _ikili(carp, x, z)))))


# =====================================================================
#  (A4) Kategoriler ve globüler (∞,∞)-yapılar
# =====================================================================
def kategori_tipi() -> Terim:
    """1-kategori: nesneler + küme-değerli hom + birim + bileşke + kanunlar."""
    Ob, Hom, bir, bil = D("Ob"), D("Hom"), D("bir"), D("bil")
    a, b, c, d = D("a"), D("b"), D("c"), D("d")
    H = lambda u, v: _ikili(Hom, u, v)
    B = lambda u, v, w, f, g: S.Uygula(S.Uygula(
        S.Uygula(S.Uygula(S.Uygula(bil, u), v), w), f), g)
    Pab = lambda govde: S.Pi("a", Ob, S.Pi("b", Ob, govde))
    hom_kume = Pab(L.iz_kume(H(a, b)))
    birim_tip = S.Pi("a", Ob, H(a, a))
    bil_tip = S.Pi("a", Ob, S.Pi("b", Ob, S.Pi("c", Ob,
        S.ok(H(a, b), S.ok(H(b, c), H(a, c))))))
    f, g_, h = D("f"), D("g"), D("h")
    sol_birim = Pab(S.Pi("f", H(a, b),
        S.yol(H(a, b), B(a, a, b, S.Uygula(bir, a), f), f)))
    sag_birim = Pab(S.Pi("f", H(a, b),
        S.yol(H(a, b), B(a, b, b, f, S.Uygula(bir, b)), f)))
    birlesme = Pab(S.Pi("c", Ob, S.Pi("d", Ob,
        S.Pi("f", H(a, b), S.Pi("g", H(b, c), S.Pi("h", H(c, d),
            S.yol(H(a, d), B(a, c, d, B(a, b, c, f, g_), h),
                           B(a, b, d, f, B(b, c, d, g_, h)))))))))
    return sigma_hepsi([
        ("Ob", U),
        ("Hom", S.ok(Ob, S.ok(Ob, U))),
        ("hom_kume", hom_kume),
        ("bir", birim_tip),
        ("bil", bil_tip),
        ("sol_birim", sol_birim),
        ("sag_birim", sag_birim),
    ], birlesme)


def globuler_tip(n: int) -> Terim:
    """``n``-derinlikli globüler tip:

    ``Glob(0) = U``,  ``Glob(k+1) = Σ (Ob : U). (Ob → Ob → Glob(k))``.

    ``n → ∞`` limiti (∞,∞)-kategorinin altında yatan globüler kümedir.
    Sonlu her kesimi burada TEŞKİL EDİLİR ve tip denetiminden geçer;
    limit, sonlu kesimlerin kulesi olarak alınır.
    """
    if n <= 0:
        return U1 if False else U
    Ob = K.taze("Ob")
    return S.Sigma(Ob, U, S.ok(D(Ob), S.ok(D(Ob), globuler_tip(n - 1))))


def omega_grupoid_kulesi(A: Terim, n: int) -> List[Tuple[int, Terim]]:
    """``A``nın ∞-grupoid kulesinin ilk ``n`` katı: ``(k, k-morfizm tipi)``."""
    return [(k, morfizm_tipi(A, k)) for k in range(n + 1)]


# =====================================================================
#  (A5) Topolojik uzaylar: yüksek tümevarımsal tipler
# =====================================================================
def cember_bilgisi() -> Dict[str, Terim]:
    """S¹: bu çekirdekte TAM olarak imâl edilmiş yegâne HIT.

    Poincaré homotopi hipotezine göre ∞-grupoidler ile topolojik uzaylar
    aynı şeydir; S¹ bunun en küçük ehemmiyetli misalidir.
    """
    S1 = S.Cember()
    return {
        "uzay": S1,
        "taban": S.Taban(),
        "dongu": L.dongu(),
        "Omega": L.dongu_uzayi(S1, S.Taban()),
        "Omega2": L.dongu_uzayi_n(S1, S.Taban(), 2),
    }


# =====================================================================
#  (C) POSTULAT KATMANI -- pürüzsüz ∞-topos / sentetik diferansiyel geometri
# =====================================================================
class Postulat:
    """Nesne dilinde İSPATLANMAYAN, aksiyom olarak eklenen sakin.

    Tipi yine de tip denetiminden geçirilir; yani "iyi teşkil edilmiş
    aksiyom" olduğu makine ile doğrulanır. İspatı yoktur.
    """

    __slots__ = ("ad", "tip", "izah")

    def __init__(self, ad: str, tip: Terim, izah: str) -> None:
        self.ad, self.tip, self.izah = ad, tip, izah

    def __repr__(self) -> str:
        return "Postulat(%s)" % self.ad


def sdg_postulatlari() -> List[Postulat]:
    """Sentetik diferansiyel geometrinin (Kock-Lawvere) çekirdek aksiyomları.

    Bunlar POSTULATTIR: hiçbir kübik çekirdek -- bu modül dâhil, Cubical
    Agda dâhil -- pürüzsüz ∞-toposu HESAPLAYAN bir indirgeyici vermez.
    Burada yapılan, aksiyomların TİPLERİNİ makine ile denetlemektir.
    """
    R = D("R")
    hR = D("halka_R")
    # halka_R : bir halka yapısı; R onun taşıyıcısı olsun diye
    # bileşenlerine erişimi kolaylaştıran kısayollar:
    carp = D("carp_R")
    top = D("top_R")
    sf = D("sifir_R")
    d, x, ff, aa, bb = D("d"), D("x"), D("f"), D("a"), D("b")

    # D = Σ (x : R). Path R (x·x) 0   -- birinci mertebeden sonsuz küçükler
    Dtip = S.Sigma("x", R, S.yol(R, _ikili(carp, x, x), sf))

    # Kock-Lawvere: her f : D → R, tek bir (a,b) ile f(d) = a + b·d
    kl_govde = S.Pi("d", Dtip, S.yol(R, S.Uygula(ff, d),
        _ikili(top, aa, _ikili(carp, bb, S.Birinci(d)))))
    kl = S.Pi("f", S.ok(Dtip, R),
              L.iz_butun(sigma_hepsi([("a", R), ("b", R)], kl_govde)))

    # Sonsuz küçük şekil kipi (infinitesimal shape modality) ℑ
    im = D("Im")
    im_tip = S.ok(U, U)
    im_birim = S.Pi("X", U, S.ok(D("X"), S.Uygula(im, D("X"))))

    return [
        Postulat("R", U,
                 "Pürüzsüz doğru (smooth line); SDG'nin taşıyıcı halkası."),
        Postulat("top_R", S.ok(R, S.ok(R, R)), "R üzerinde toplama."),
        Postulat("carp_R", S.ok(R, S.ok(R, R)), "R üzerinde çarpma."),
        Postulat("sifir_R", R, "R'nin sıfırı."),
        Postulat("KockLawvere", kl,
                 "Kock-Lawvere aksiyomu: D üzerindeki her fonksiyon TEK bir "
                 "afin form ile temsil edilir. Türev kavramı buradan doğar; "
                 "sentetik diferansiyel geometrinin bel kemiğidir."),
        Postulat("Im", im_tip,
                 "Sonsuz küçük şekil kipi ℑ (infinitesimal shape modality); "
                 "de Rham uzayı ve düz (crystalline) yapılar bununla kurulur."),
        Postulat("Im_birim", im_birim, "ℑ kipinin birim dönüşümü X → ℑX."),
    ]


def univalence_postulati() -> Postulat:
    """Tümel değişmezlik, bu çekirdekte İFADE EDİLİR fakat TAŞIMASI
    hesaplanmaz; dolayısıyla ``ua``yı hesapla kullanmak isteyen, aksiyom
    olarak ``uaBeta``yı eklemek zorundadır."""
    A, B, e, x = D("A"), D("B"), D("e"), D("x")
    tip = S.Pi("A", U, S.Pi("B", U, S.Pi("e", L.denklik_tipi(A, B),
        S.Pi("x", A, S.yol(B, L.tasi(L.ua(A, B, e), x),
                              S.Uygula(S.Birinci(e), x))))))
    return Postulat("uaBeta", tip,
                    "ua'nın β-kuralı: ua e boyunca taşıma, denkliğin "
                    "fonksiyonudur. Kübik çekirdekte comp^i(Glue) imâl "
                    "edilseydi bu TANIMSAL olurdu; burada postulattır.")


def postulat_baglami(postulatlar: Sequence[Postulat],
                     taban: Optional[Baglam] = None) -> Baglam:
    g = taban or Baglam()
    for p in postulatlar:
        g = g.genislet(p.ad, p.tip)
    return g


# =====================================================================
#  Boşluk kütüğü
# =====================================================================
def bosluklar() -> List[Dict[str, str]]:
    """Bu çekirdeğin BİLİNEN eksikleri. Sessiz değil, kütüklü."""
    return [
        {
            "ad": "S¹ hcomp üzerinde sarım sayısı (|n| ≥ 2 ve n < 0)",
            "durum": "DOĞRU fakat PRATİKTE BİTMİYOR -- hız duvarı",
            "sebep": "S¹ içindeki bir hcomp'a helix uygulanınca 'comp^i U' "
                     "doğar; o da her katmanda BÜTÜN Denklik yapısını "
                     "(Σ/Π/isContr kulesi) taşır. Çekirdek terim seviyesinde, "
                     "paylaşımsız ikame ile çalıştığı için terim patlar. "
                     "Bu bir DOĞRULUK boşluğu değil, değerlendirici mimarisi "
                     "meselesidir; kapanışı NbE'ye (kapanışlı değerler) geçmeyi "
                     "gerektirir.",
            "netice": "sarim(dongu⁰)=+0 ve sarim(dongu¹)=+1 HESAPLANIR; "
                      "|n|≥2 ve negatif n makul sürede bitmez. Buna karşılık "
                      "uaβ (transport (ua sucEquiv) n = n+1) her n için "
                      "hesaplanır -- yani Glue kuralının kendisi işler.",
        },
        {
            "ad": "Genel HIT'ler (süspansiyon, pushout, n-kesme)",
            "durum": "YALNIZ S¹ imâl edildi",
            "sebep": "Her HIT'in kendi hcomp kuralı vardır; genel bir HIT "
                     "şeması yazılmadı.",
            "netice": "Sⁿ (n≥2) ve kesme (truncation) yok; dolayısıyla πₙ "
                      "KÜME olarak tarif edilemiyor. Ωⁿ vardır.",
        },
        {
            "ad": "Pürüzsüz ∞-topos / SDG / de Rham",
            "durum": "POSTULAT",
            "sebep": "Kock-Lawvere, ℑ kipi ve dış türev d'nin HESAPLANAN bir "
                     "indirgeme kuralı hiçbir kübik çekirdekte yoktur "
                     "(Cubical Agda dâhil).",
            "netice": "Tipleri makine ile denetlenir (iyi teşkil edilmiş "
                      "aksiyom), sakinleri aksiyomdur. Teğet demeti X^D, "
                      "tensör tipleri, monoid/Lie nesneleri bu postulatlar "
                      "ÜZERİNE fiilen kurulur ve tip denetiminden geçer.",
        },
        {
            "ad": "ℕ / ℤ üzerinde comp",
            "durum": "DÜZELTİLDİ -- evvelce SAĞLAM DEĞİLDİ",
            "sebep": "Başlangıçta 'ℕ/ℤ ayrıktır, comp = u0' kuralı konmuştu. "
                     "Bu SAĞLAM DEĞİLDİR: sistemin i=1'deki değeri tabana "
                     "yalnız propozisyonel eşittir, tanımsal değil; kural "
                     "bütün ℤ dolgularını çökertiyordu.",
            "netice": "Yerine doğru yapısal kural kondu: taban kurucusuna "
                      "göre sistem bileşenlere dağıtılır; dallar aynı "
                      "kurucuyla başlamıyorsa comp TAKILI kalır.",
        },
    ]


# =====================================================================
#  Kendi kendini doğrulama
# =====================================================================
def _dene(ad: str, is_: Callable[[], None]) -> Dict[str, str]:
    try:
        is_()
        return {"ad": ad, "netice": "GEÇTİ"}
    except EksikKural as e:
        return {"ad": ad, "netice": "EKSİK KURAL", "izah": str(e)[:120]}
    except Exception as e:  # noqa: BLE001
        return {"ad": ad, "netice": "HATA", "izah": ("%s: %s" % (type(e).__name__, e))[:300]}


def dogrula_hepsi() -> List[Dict[str, str]]:
    """Bu dosyadaki her türetimi fiilen tip denetiminden geçirir."""
    g = Baglam()
    A = D("A")
    gA = Baglam({"A": U, "a": A, "b": A})
    S1 = S.Cember()
    isler: List[Tuple[str, Callable[[], None]]] = [
        ("∞-grupoid: 1-morfizm tipi", lambda: denetle(morfizm_tipi(A, 1), U, gA)),
        ("∞-grupoid: 2-morfizm tipi", lambda: denetle(morfizm_tipi(A, 2), U, gA)),
        ("∞-grupoid: 3-morfizm tipi", lambda: denetle(morfizm_tipi(A, 3), U, gA)),
        ("koherens tipi (n=2)", lambda: denetle(koherens_tipi(A, 2), U, gA)),
        ("Küme tipi", lambda: denetle(kume_tipi(), U1, g)),
        ("Önerme tipi", lambda: denetle(onerme_tipi(), U1, g)),
        ("Grupoid tipi", lambda: denetle(grupoid_tipi(), U1, g)),
        ("2-tip tipi", lambda: denetle(n_tip_tipi(2), U1, g)),
        ("Monoid", lambda: denetle(monoid_tipi(), U1, g)),
        ("Grup", lambda: denetle(grup_tipi(), U1, g)),
        ("Değişmeli halka", lambda: denetle(halka_tipi(), U1, g)),
        ("Kategori", lambda: denetle(kategori_tipi(), U1, g)),
        ("Globüler tip (derinlik 3)", lambda: denetle(globuler_tip(3), U1, g)),
        ("S¹ : U", lambda: denetle(S1, U, g)),
        ("Ω(S¹) : U", lambda: denetle(L.dongu_uzayi(S1, S.Taban()), U, g)),
        ("Ω²(S¹) : U", lambda: denetle(L.dongu_uzayi_n(S1, S.Taban(), 2), U, g)),
        ("dongu³ : Ω(S¹)", lambda: denetle(L.dongu_kuvveti(3),
                                           S.yol(S1, S.Taban(), S.Taban()), g)),
        ("ℕ ayrık: 2+3=5", lambda: _esit_dene(
            S.DogalInd("_", S.Dogal(), S.dogal_sayi(3), "k", "r",
                       S.Ard(D("r")), S.dogal_sayi(2)), S.dogal_sayi(5))),
        ("ℤ: sucZ(-1)=0", lambda: _esit_dene(
            S.Uygula(L.ardil_z(), S.tam_sayi(-1)), S.tam_sayi(0))),
    ]
    neticeler = [_dene(ad, f) for ad, f in isler]

    # (C) postulat tipleri iyi teşkil edilmiş mi?
    ps = sdg_postulatlari()
    gp = Baglam()
    for p in ps:
        neticeler.append(_dene("POSTULAT tipi iyi teşkil: %s" % p.ad,
                               lambda p=p, gp=gp: denetle_tip_yardimci(p.tip, gp)))
        gp = gp.genislet(p.ad, p.tip)
    ua_p = univalence_postulati()
    neticeler.append(_dene("POSTULAT tipi iyi teşkil: uaBeta",
                           lambda: denetle_tip_yardimci(ua_p.tip, Baglam())))

    # (B) ifade edilen ama hesaplanmayan
    neticeler.append(_dene(
        "ua boyunca TAŞIMA (hesaplanması beklenmiyor)",
        lambda: _ua_tasima_dene()))
    return neticeler


def denetle_tip_yardimci(t: Terim, g: Baglam) -> None:
    from .denetleyici import denetle_tip
    denetle_tip(t, g)


def _esit_dene(a: Terim, b: Terim) -> None:
    if not K.esdeger_mi(a, b):
        raise AssertionError("%s ≠ %s" % (K.nf(a), K.nf(b)))


def _ua_tasima_dene() -> None:
    A, B, e, x = D("A"), D("B"), D("e"), D("x")
    g = Baglam({"A": U, "B": U, "e": L.denklik_tipi(A, B), "x": A})
    K.nf(L.tasi(L.ua(A, B, e), x), g.tipler)


def rapor() -> str:
    """Dürüst hulâsa: ne hesaplanıyor, ne ifade ediliyor, ne postulat."""
    satirlar = ["=" * 66,
                "omega_kategori -- türetim raporu",
                "=" * 66, "", "(A) HESAPLANAN ve TİP DENETİMİNDEN GEÇEN:"]
    gecti = kaldi = eksik = 0
    for n in dogrula_hepsi():
        im = {"GEÇTİ": "  ✓ ", "EKSİK KURAL": "  ⊘ ", "HATA": "  ✗ "}[n["netice"]]
        satirlar.append("%s%s%s" % (im, n["ad"],
                                    "" if n["netice"] == "GEÇTİ"
                                    else "   [%s]" % n["netice"]))
        if n["netice"] == "GEÇTİ":
            gecti += 1
        elif n["netice"] == "EKSİK KURAL":
            eksik += 1
        else:
            kaldi += 1
    satirlar += ["", "hulâsa: %d geçti, %d eksik kural, %d hata"
                 % (gecti, eksik, kaldi), "",
                 "(C) BOŞLUK KÜTÜĞÜ:"]
    for b in bosluklar():
        satirlar.append("  • %s -- %s" % (b["ad"], b["durum"]))
        satirlar.append("      netice: %s" % b["netice"])
    satirlar.append("=" * 66)
    return "\n".join(satirlar)
