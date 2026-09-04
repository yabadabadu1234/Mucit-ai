"""
omega_kategori_nbe sınama takımı.

``python3 -m omega_kategori_nbe.test_omega_kategori_nbe``

Terim sürümündeki sınamaların aynısı + NbE'nin asıl gerekçesi olan
**π₁(S¹) hesabı** (terim sürümünde |n| ≥ 2 için bitmiyordu).
"""
from __future__ import annotations

from matematik.tip_teorisi import (BIR, DOGRU, SIFIR, YANLIS, Aralik, Kofibrasyon,
                     aralik_esitligi)
from matematik import tip_teorisi as K
from matematik import tip_teorisi as Dk
from matematik import tip_teorisi as L
from matematik import tip_teorisi as S
from matematik import tip_teorisi as TR
from matematik.tip_teorisi import (Baglam, DenetimHatasi,
                                   denetle_t as denetle, sentezle)

U = S.Evren(0)
U1 = S.Evren(1)
D = S.Deg
N, Z, S1 = S.Dogal(), S.Tamsayi(), S.Cember()
TB = S.Taban()


def _g() -> Baglam:
    A, B = D("A"), D("B")
    a, b, c = D("a"), D("b"), D("c")
    return Baglam.terimlerden({
        "A": U, "B": U, "a": A, "b": A, "c": A, "d": A,
        "p": S.yol(A, a, b), "q": S.yol(A, b, c), "r": S.yol(A, c, D("d")),
        "f": S.ok(A, B), "x": A,
    })


def _bg() -> dict:
    A, B = D("A"), D("B")
    a, b, c = D("a"), D("b"), D("c")
    return {"A": U, "B": U, "a": A, "b": A, "c": A, "d": A,
            "p": S.yol(A, a, b), "q": S.yol(A, b, c), "r": S.yol(A, c, D("d")),
            "f": S.ok(A, B), "x": A}


# =====================================================================
#  1. Aralık cebri (paylaşılan katman)
# =====================================================================
def test_aralik_de_morgan():
    i, j, k = (Aralik.degisken("i"), Aralik.degisken("j"),
               Aralik.degisken("k"))
    assert i.degil().degil() == i
    assert i.ve(j).degil() == i.degil().veya(j.degil())
    assert i.veya(i.ve(j)) == i
    assert i.ve(j.veya(k)) == i.ve(j).veya(i.ve(k))
    assert i.ve(i.degil()) != SIFIR          # tümleyen YOK
    assert Kofibrasyon.atom("i", False).ve(Kofibrasyon.atom("i", True)).bos_mu()
    assert Dk.her_i_icin(Kofibrasyon.atom("i", False), "i").bos_mu()


# =====================================================================
#  2. NbE indirgeme
# =====================================================================
def test_mltt():
    bg = _bg()
    a, f = D("a"), D("f")
    assert K.esdeger_mi(S.Uygula(S.Lam("z", D("z")), a), a, bg)
    assert K.esdeger_mi(f, S.Lam("z", S.Uygula(f, D("z"))), bg)   # eta
    assert K.esdeger_mi(S.Birinci(S.Cift(a, D("b"))), a, bg)
    assert not K.esdeger_mi(D("A"), a, bg)


def test_yollar():
    bg = _bg()
    a, b, p = D("a"), D("b"), D("p")
    assert K.esdeger_mi(S.YolUygula(S.refl(a), Aralik.degisken("i")), a, bg)
    assert K.esdeger_mi(S.YolUygula(p, SIFIR), a, bg)
    assert K.esdeger_mi(S.YolUygula(p, BIR), b, bg)
    assert K.esdeger_mi(p, S.YolLam("i", S.YolUygula(p, Aralik.degisken("i"))),
                        bg)
    assert K.esdeger_mi(S.Dongu(SIFIR), TB, bg)


def test_transp_sabit():
    bg = _bg()
    A, a, f = D("A"), D("a"), D("f")
    assert K.esdeger_mi(S.Transp("i", A, YANLIS, a), a, bg)
    assert K.esdeger_mi(S.Transp("i", S.ok(A, A), YANLIS, f), f,
                        dict(bg, f=S.ok(A, A)))
    assert K.esdeger_mi(S.Transp("i", S.yol(A, a, a), YANLIS, L.refl(a)),
                        L.refl(a), bg)


def test_hcomp_terkip_ters():
    bg = _bg()
    A, a, b, c, p, q = D("A"), D("a"), D("b"), D("c"), D("p"), D("q")
    tr = L.terkip(A, a, b, c, p, q)
    assert K.esdeger_mi(S.YolUygula(tr, SIFIR), a, bg)
    assert K.esdeger_mi(S.YolUygula(tr, BIR), c, bg)
    sy = L.ters(A, a, b, p)
    assert K.esdeger_mi(S.YolUygula(sy, SIFIR), b, bg)
    assert K.esdeger_mi(S.YolUygula(sy, BIR), a, bg)


def test_s1_hcomp():
    dt = S.HKomp(S1, "j", [(S.yuz(i=0), TB),
                           (S.yuz(i=1), S.Dongu(Aralik.degisken("j")))],
                 S.Dongu(Aralik.degisken("i")))
    assert K.esdeger_mi(TR.ara_ikame(dt, {"i": SIFIR}), TB)
    assert K.esdeger_mi(TR.ara_ikame(dt, {"i": BIR}), TB)
    recN = S.CemberInd("_", N, S.dogal_sayi(0), "i", S.dogal_sayi(0), dt)
    assert K.esdeger_mi(recN, S.dogal_sayi(0))


def test_sayilar():
    topla = lambda m, n: S.DogalInd("_", N, n, "k", "r", S.Ard(D("r")), m)
    assert K.esdeger_mi(topla(S.dogal_sayi(2), S.dogal_sayi(3)),
                        S.dogal_sayi(5))
    suc, pred = L.ardil_z(), L.oncel_z()
    for n in (-3, -1, 0, 1, 5):
        assert K.esdeger_mi(S.Uygula(suc, S.tam_sayi(n)), S.tam_sayi(n + 1))
        assert K.esdeger_mi(S.Uygula(pred, S.tam_sayi(n)), S.tam_sayi(n - 1))


# =====================================================================
#  3. Tip denetimi -- MÜSBET
# =====================================================================
def test_grupoid_denetim():
    g = _g()
    A, B = D("A"), D("B")
    a, b, c, f, p, q = D("a"), D("b"), D("c"), D("f"), D("p"), D("q")
    denetle(L.refl(a), g.d(S.yol(A, a, a)), g)
    denetle(L.ters(A, a, b, p), g.d(S.yol(A, b, a)), g)
    denetle(L.terkip(A, a, b, c, p, q), g.d(S.yol(A, a, c)), g)
    denetle(L.esle(A, B, f, a, b, p),
            g.d(S.yol(B, S.Uygula(f, a), S.Uygula(f, b))), g)


def test_j():
    g = _g()
    A, a, b, p, Cf, d = D("A"), D("a"), D("b"), D("p"), D("C"), D("d")
    bb, pp = TR.taze("b"), TR.taze("p")
    C_tip = S.Pi(bb, A, S.Pi(pp, S.yol(A, a, D(bb)), U))
    tab = dict(_bg())          # "d" burada kalmalı: "r"nin tipi ona bağlı
    tab["C"] = C_tip
    tab["dW"] = S.Uygula(S.Uygula(Cf, a), L.refl(a))
    gJ = Baglam.terimlerden(tab)
    d = D("dW")
    denetle(L.yol_tumevarimi(A, a, Cf, d, b, p),
            gJ.d(S.Uygula(S.Uygula(Cf, b), p)), gJ)


def test_denklik_ve_ua():
    g = _g()
    A, B, e = D("A"), D("B"), D("e")
    denetle(L.denklik_tipi(A, B), g.d(U), g)
    denetle(L.ozdeslik_denkligi(A), g.d(L.denklik_tipi(A, A)), g)
    gu = Baglam.terimlerden(dict(_bg(), e=L.denklik_tipi(A, B)))
    denetle(L.ua(A, B, e), gu.d(S.yol(U, A, B)), gu)
    assert K.esdeger_mi(S.YolUygula(L.ua(A, B, e), SIFIR), A,
                        dict(_bg(), e=L.denklik_tipi(A, B)))


def test_izo_denklige():
    g = Baglam()
    denetle(L.ardil_denkligi(), g.d(L.denklik_tipi(Z, Z)), g)


def test_dongu_kuvvetleri():
    g = Baglam()
    tip = g.d(S.yol(S1, TB, TB))
    for n in (0, 1, 2, 3, -1, -2):
        denetle(L.dongu_kuvveti(n), tip, g)


def test_helix_denetim():
    g = Baglam()
    denetle(S.Lam("x", L.sarmal(D("x"))), g.d(S.ok(S1, U)), g)


# =====================================================================
#  4. Tümel değişmezlik HESAPLANIYOR
# =====================================================================
def test_ua_beta():
    uaN = L.ua(N, N, L.ozdeslik_denkligi(N))
    assert K.esdeger_mi(L.tasi(uaN, S.dogal_sayi(3)), S.dogal_sayi(3))
    uaS = L.ua(Z, Z, L.ardil_denkligi())
    for n in (-2, -1, 0, 1, 3):
        assert K.esdeger_mi(L.tasi(uaS, S.tam_sayi(n)), S.tam_sayi(n + 1)), n


def test_pi1_cember():
    """π₁(S¹) ≅ ℤ -- NbE'nin asıl gerekçesi.

    Terim seviyesindeki sürüm |n| ≥ 2 için bu hesabı BİTİREMİYORDU.
    """
    for n in (0, 1, 2, 3, 5, -1, -2, -3, -5):
        r = K.nf(L.sarim(L.dongu_kuvveti(n)))
        assert K.esdeger_mi(r, S.tam_sayi(n)), (n, r)


def test_dongu_tersi_genel_tersle_ayni_sarim():
    """``<i> dongu(~i)`` ile genel ``ters(dongu)`` aynı sarımı vermeli.

    Negatif kuvvetlerdeki hızlanma bir KISA YOL değil, S¹'in kendi
    involüsyonudur; sağlaması, pahalı olan genel inşayla kıyastır.
    """
    for n in (-1, -2, -3):
        sade = K.nf(L.sarim(L.dongu_kuvveti(n)))
        genel = K.nf(L.sarim(L.dongu_kuvveti_genel_ters(n)))
        assert K.esdeger_mi(sade, genel), (n, sade, genel)
        assert K.esdeger_mi(sade, S.tam_sayi(n)), (n, sade)


# =====================================================================
#  4b. Taşınan katmanlar
# =====================================================================
def test_turetimler():
    from matematik import tip_teorisi as T
    r = T.dogrula_hepsi()
    hatalar = [n for n in r if n["netice"] != "GEÇTİ"]
    assert not hatalar, hatalar
    assert len(r) >= 30


def test_geometri():
    from matematik import tip_teorisi as G
    r = G.dogrula_hepsi()
    assert not [n for n in r if n["netice"] != "GEÇTİ"]
    assert len(r) >= 20


def test_iliskiler():
    from matematik import tip_teorisi as I
    r = I.dogrula_hepsi()
    assert not [n for n in r if n["netice"] != "GEÇTİ"]
    assert len(r) >= 20


# =====================================================================
#  5. MENFÎ sınamalar
# =====================================================================
def _red(f):
    try:
        f()
    except DenetimHatasi:
        return
    raise AssertionError("REDDEDİLMESİ gereken terim kabul edildi")


def test_menfi_tip_uyusmazligi():
    g = _g()
    _red(lambda: denetle(D("a"), g.d(D("B")), g))


def test_menfi_kapsam_disi():
    g = _g()
    _red(lambda: sentezle(D("yok_boyle_bir_sey"), g))


def test_menfi_yol_ucu():
    g = _g()
    A, a, b = D("A"), D("a"), D("b")
    _red(lambda: denetle(L.refl(a), g.d(S.yol(A, a, b)), g))


def test_menfi_sistem_cakisma():
    g = _g().ara_ekle("i")
    A, a, b = D("A"), D("a"), D("b")
    _red(lambda: sentezle(S.HKomp(A, "j", [(S.yuz(i=0), a),
                                           (S.yuz(i=0), b)], a), g))


def test_menfi_sistem_taban():
    g = _g().ara_ekle("i")
    A, a, b = D("A"), D("a"), D("b")
    _red(lambda: sentezle(S.HKomp(A, "j", [(S.yuz(i=0), b)], a), g))


def test_menfi_transp_sabit_degil():
    g = _g()
    Cf, p, x = D("C"), D("p"), D("x")
    A = D("A")
    tab = dict(_bg())
    tab.pop("x", None)
    tab["C"] = S.ok(A, U)
    tab["x"] = S.Uygula(Cf, D("a"))
    gg = Baglam.terimlerden(tab)
    gg = gg.ara_ekle("k").ara_ekle("j")
    cizgi = S.YolUygula(p, Aralik.degisken("k"))
    kotu = S.Transp("k", S.Uygula(Cf, cizgi),
                    Kofibrasyon([S.yuz(j=0)]), x)
    _red(lambda: sentezle(kotu, gg))


def _hepsini_calistir() -> int:
    isler = [(a, f) for a, f in sorted(globals().items())
             if a.startswith("test_") and callable(f)]
    gecti = kaldi = 0
    for ad, f in isler:
        try:
            f()
            gecti += 1
            print("  ✓ %s" % ad)
        except Exception as e:  # noqa: BLE001
            kaldi += 1
            print("  ✗ %s\n      %s: %s" % (ad, type(e).__name__,
                                            str(e)[:250]))
    print("\n%d geçti, %d kaldı  (%d sınama)" % (gecti, kaldi, len(isler)))
    return 0 if kaldi == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(_hepsini_calistir())
