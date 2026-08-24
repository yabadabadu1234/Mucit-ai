"""
omega_kategori sınama takımı.

Doğrudan çalıştırılır:  ``python3 -m omega_kategori.test_omega_kategori``
pytest ile de uyumludur.

Sınamalar iki cephelidir ve İKİSİ DE şarttır:
  * MÜSBET: doğru terimler tip denetiminden GEÇMELİ ve doğru indirgenmeli.
  * MENFÎ : hatalı terimler REDDEDİLMELİ. Menfî sınamalar olmadan bir tip
            denetleyicisinin "geçti" demesi hiçbir şey ifade etmez.
"""
from __future__ import annotations

from .aralik import (BIR, DOGRU, SIFIR, YANLIS, Aralik, Kofibrasyon,
                     aralik_esitligi)
from . import cekirdek as K
from . import denklik as Dk
from . import kutuphane as L
from . import sozdizim as S
from . import turetimler as T
from .denetleyici import Baglam, DenetimHatasi, denetle, sentezle

U = S.Evren(0)
U1 = S.Evren(1)
D = S.Deg
ar = S.ar


def _temel_baglam() -> Baglam:
    A, B = D("A"), D("B")
    a, b, c = D("a"), D("b"), D("c")
    return Baglam({
        "A": U, "B": U, "a": A, "b": A, "c": A, "d": A,
        "p": S.yol(A, a, b), "q": S.yol(A, b, c),
        "r": S.yol(A, c, D("d")),
        "f": S.ok(A, B), "x": A,
    })


# =====================================================================
#  1. De Morgan aralık cebri
# =====================================================================
def test_aralik_de_morgan():
    i, j, k = Aralik.degisken("i"), Aralik.degisken("j"), Aralik.degisken("k")
    assert SIFIR.degil() == BIR and BIR.degil() == SIFIR
    assert i.degil().degil() == i
    assert i.ve(j).degil() == i.degil().veya(j.degil())
    assert i.veya(j).degil() == i.degil().ve(j.degil())
    assert i.veya(i.ve(j)) == i                      # yutma
    assert i.ve(j.veya(k)) == i.ve(j).veya(i.ve(k))  # dağılma
    # KRİTİK: De Morgan cebrinde tümleyen YOKTUR
    assert i.ve(i.degil()) != SIFIR
    assert i.veya(i.degil()) != BIR


def test_yuz_kafesi():
    i0, i1 = Kofibrasyon.atom("i", False), Kofibrasyon.atom("i", True)
    # yüz kafesinde ise tümleyen VARDIR
    assert i0.ve(i1).bos_mu()
    i = Aralik.degisken("i")
    j0 = Kofibrasyon.atom("j", False)
    assert aralik_esitligi(i.degil(), True) == i0
    assert aralik_esitligi(i.ve(Aralik.degisken("j")), False) == i0.veya(j0)
    assert aralik_esitligi(BIR, False).bos_mu()
    assert Dk.her_i_icin(i0.veya(j0), "i") == j0


# =====================================================================
#  2. Çekirdek indirgeme
# =====================================================================
def test_mltt_indirgeme():
    g = _temel_baglam()
    a, f = D("a"), D("f")
    assert K.esdeger_mi(S.Uygula(S.Lam("z", D("z")), a), a, g.tipler)
    assert K.esdeger_mi(f, S.Lam("z", S.Uygula(f, D("z"))), g.tipler)   # eta
    assert K.esdeger_mi(S.Birinci(S.Cift(a, D("b"))), a, g.tipler)


def test_yol_temelleri():
    g = _temel_baglam()
    a, b, p = D("a"), D("b"), D("p")
    assert K.esdeger_mi(K.yol_uygula(L.refl(a), ar("i")), a, g.tipler)
    assert K.esdeger_mi(S.YolUygula(p, SIFIR), a, g.tipler)   # nötr uç kuralı
    assert K.esdeger_mi(S.YolUygula(p, BIR), b, g.tipler)
    assert K.esdeger_mi(S.Dongu(SIFIR), S.Taban(), g.tipler)


def test_transp_sabit_cizgide_ozdeslik():
    g = _temel_baglam()
    A, a, x, f = D("A"), D("a"), D("x"), D("f")
    assert K.esdeger_mi(S.Transp("i", A, YANLIS, x), x, g.tipler)
    assert K.esdeger_mi(S.Transp("i", S.ok(A, A), YANLIS, f), f,
                        dict(g.tipler, f=S.ok(A, A)))
    assert K.esdeger_mi(S.Transp("i", S.yol(A, a, a), YANLIS, L.refl(a)),
                        L.refl(a), g.tipler)
    # refl boyunca taşıma özdeşliktir
    Cf = D("C")
    gg = dict(g.tipler, C=S.ok(A, U), y=S.Uygula(Cf, a))
    assert K.esdeger_mi(L.aile_tasi(Cf, L.refl(a), D("y")), D("y"), gg)


def test_s1_hcomp_kanonik_ve_ayrik_hedefte_indirger():
    g = _temel_baglam()
    dongu_terkip = S.HKomp(S.Cember(), "j",
        [(S.yuz(i=0), S.Taban()), (S.yuz(i=1), S.Dongu(ar("j")))],
        S.Dongu(ar("i")))
    # uçlar doğru
    assert K.esdeger_mi(K.ara_ikame(dongu_terkip, {"i": SIFIR}), S.Taban())
    assert K.esdeger_mi(K.ara_ikame(dongu_terkip, {"i": BIR}), S.Taban())
    # AYRIK hedefte (ℕ) eliminatör indirger
    recN = S.CemberInd("_", S.Dogal(), S.dogal_sayi(0), "i",
                       S.dogal_sayi(0), dongu_terkip)
    assert K.esdeger_mi(recN, S.dogal_sayi(0))
    # NÖTR hedefte takılı kalır (CCHM'de regülerlik YOKTUR)
    recA = S.CemberInd("_", D("A"), D("a"), "i", D("a"), dongu_terkip)
    assert isinstance(K.whnf(recA, g.tipler), (S.Komp, S.HKomp))


def test_dogal_ve_tamsayi_hesabi():
    topla = lambda m, n: S.DogalInd("_", S.Dogal(), n, "k", "r",
                                    S.Ard(D("r")), m)
    assert K.esdeger_mi(topla(S.dogal_sayi(2), S.dogal_sayi(3)),
                        S.dogal_sayi(5))
    suc, pred = L.ardil_z(), L.oncel_z()
    for n in (-3, -1, 0, 1, 5):
        assert K.esdeger_mi(S.Uygula(suc, S.tam_sayi(n)), S.tam_sayi(n + 1))
        assert K.esdeger_mi(S.Uygula(pred, S.tam_sayi(n)), S.tam_sayi(n - 1))


# =====================================================================
#  3. Tip denetimi -- MÜSBET
# =====================================================================
def test_grupoid_yapisi_tip_denetiminden_gecer():
    g = _temel_baglam()
    A, B = D("A"), D("B")
    a, b, c, f, p, q = D("a"), D("b"), D("c"), D("f"), D("p"), D("q")
    denetle(L.refl(a), S.yol(A, a, a), g)
    denetle(L.ters(A, a, b, p), S.yol(A, b, a), g)
    denetle(L.terkip(A, a, b, c, p, q), S.yol(A, a, c), g)
    denetle(L.esle(A, B, f, a, b, p),
            S.yol(B, S.Uygula(f, a), S.Uygula(f, b)), g)


def test_j_yol_tumevarimi():
    g = _temel_baglam()
    A, a, b, p, Cf, d = D("A"), D("a"), D("b"), D("p"), D("C"), D("d")
    bb, pp = K.taze("b"), K.taze("p")
    C_tip = S.Pi(bb, A, S.Pi(pp, S.yol(A, a, D(bb)), U))
    gJ = Baglam(dict(g.tipler, C=C_tip,
                     d=S.Uygula(S.Uygula(Cf, a), L.refl(a))))
    denetle(L.yol_tumevarimi(A, a, Cf, d, b, p),
            S.Uygula(S.Uygula(Cf, b), p), gJ)


def test_denklik_ve_ua():
    g = _temel_baglam()
    A, B, e = D("A"), D("B"), D("e")
    denetle(L.denklik_tipi(A, B), U, g)
    denetle(L.ozdeslik_denkligi(A), L.denklik_tipi(A, A), g)
    gua = Baglam(dict(g.tipler, e=L.denklik_tipi(A, B)))
    denetle(L.ua(A, B, e), S.yol(U, A, B), gua)
    # ua'nın UÇLARI tanımsal olarak doğrudur
    assert K.esdeger_mi(S.YolUygula(L.ua(A, B, e), SIFIR), A, gua.tipler)
    assert K.esdeger_mi(S.YolUygula(L.ua(A, B, e), BIR), B, gua.tipler)


def test_s1_dongu_kuvvetleri():
    g = _temel_baglam()
    tip = S.yol(S.Cember(), S.Taban(), S.Taban())
    for n in (0, 1, 2, 3, -1, -2):
        denetle(L.dongu_kuvveti(n), tip, g)


def test_yuksek_koherens_tipleri():
    g = _temel_baglam()
    A = D("A")
    a, b, c, d = D("a"), D("b"), D("c"), D("d")
    p, q, r = D("p"), D("q"), D("r")
    sol = L.terkip(A, a, c, d, L.terkip(A, a, b, c, p, q), r)
    sag = L.terkip(A, a, b, d, p, L.terkip(A, b, c, d, q, r))
    denetle(sol, S.yol(A, a, d), g)
    denetle(sag, S.yol(A, a, d), g)
    # birleşme kanunu KATI eşitlik değil, 2-morfizm olarak ifade edilir
    denetle(S.yol(S.yol(A, a, d), sol, sag), U, g)


def test_turetimler_hepsi():
    neticeler = T.dogrula_hepsi()
    hatalar = [n for n in neticeler if n["netice"] == "HATA"]
    assert not hatalar, "türetimlerde hata: %s" % hatalar
    gecen = [n for n in neticeler if n["netice"] == "GEÇTİ"]
    assert len(gecen) >= 25, "beklenenden az türetim geçti: %d" % len(gecen)


# =====================================================================
#  4. Tip denetimi -- MENFÎ  (hatalı olan REDDEDİLMELİ)
# =====================================================================
def _reddedilmeli(is_):
    try:
        is_()
    except DenetimHatasi:
        return
    raise AssertionError("REDDEDİLMESİ gereken terim kabul edildi")


def test_menfi_tip_uyusmazligi():
    g = _temel_baglam()
    # a : A, B tipinde değil
    _reddedilmeli(lambda: denetle(D("a"), D("B"), g))


def test_menfi_kapsam_disi_degisken():
    g = _temel_baglam()
    _reddedilmeli(lambda: sentezle(D("kimsenin_bilmedigi"), g))


def test_menfi_yolun_ucu_uymuyor():
    g = _temel_baglam()
    A, a, b = D("A"), D("a"), D("b")
    # refl a : Path A a a'dır; Path A a b DEĞİL
    _reddedilmeli(lambda: denetle(L.refl(a), S.yol(A, a, b), g))


def test_menfi_sistem_cakisan_yuzde_uyusmuyor():
    g = _temel_baglam()
    A, a, b = D("A"), D("a"), D("b")
    # aynı yüzde iki ayrı değer veren sistem
    kotu = S.HKomp(A, "j", [(S.yuz(i=0), a), (S.yuz(i=0), b)], a)
    gi = g.aralik_ekle("i")
    _reddedilmeli(lambda: sentezle(kotu, gi))


def test_menfi_sistem_tabanla_uyusmuyor():
    g = _temel_baglam()
    A, a, b = D("A"), D("a"), D("b")
    # dal j=0'da b veriyor, taban ise a
    kotu = S.HKomp(A, "j", [(S.yuz(i=0), b)], a)
    gi = g.aralik_ekle("i")
    _reddedilmeli(lambda: sentezle(kotu, gi))


def test_menfi_transp_cizgisi_kofibrasyonda_sabit_degil():
    g = _temel_baglam()
    Cf, a, b, p, x = D("C"), D("a"), D("b"), D("p"), D("x")
    A = D("A")
    gg = Baglam(dict(g.tipler, C=S.ok(A, U),
                     x=S.Uygula(Cf, a)))
    gg = gg.aralik_ekle("i")
    # çizgi (i) boyunca DEĞİŞİYOR, ama kofibrasyon ⊤ gibi (j=0) veriliyor:
    # (j=0) yüzünde çizgi sabit değil -> reddedilmeli
    cizgi = S.Uygula(Cf, K.yol_uygula(p, ar("k")))
    kotu = S.Transp("k", cizgi, Kofibrasyon([S.yuz(j=0)]), x)
    _reddedilmeli(lambda: sentezle(kotu, gg.aralik_ekle("j")))


def test_menfi_glue_yuzunde_denklik_uyusmuyor():
    g = _temel_baglam()
    A, B, a = D("A"), D("B"), D("a")
    # glue [i=0 ↦ a] a : Glue B [...] -- taban tipi B ama a : A
    gi = g.aralik_ekle("i")
    kotu = S.YapistirTerim([(S.yuz(i=0), a)], a)
    tip = S.Yapistir(D("B"), [(S.yuz(i=0), A, L.ozdeslik_denkligi(A))])
    _reddedilmeli(lambda: denetle(kotu, tip, gi))


# =====================================================================
#  5. Glue hesabı -- tümel değişmezlik HESAPLANIYOR
# =====================================================================
def test_cizgi_denkligi():
    """``comp^i U``nun dayandığı lineToEquiv."""
    N = S.Dogal()
    denetle(Dk.cizgi_denkligi("k", N), L.denklik_tipi(N, N), Baglam())


def test_izo_denklige_sucEquiv():
    """isoToEquiv: sucZ bir denkliktir -- TİP DENETİMİNDEN geçer."""
    Z = S.Tamsayi()
    denetle(L.ardil_denkligi(), L.denklik_tipi(Z, Z), Baglam())


def test_ua_beta_ozdeslik_denkligiyle():
    N = S.Dogal()
    uaN = L.ua(N, N, L.ozdeslik_denkligi(N))
    denetle(uaN, S.yol(U, N, N), Baglam())
    assert K.esdeger_mi(L.tasi(uaN, S.dogal_sayi(3)), S.dogal_sayi(3))


def test_ua_beta_asikar_olmayan_denklikle():
    """ASIL SINAV: ua sucEquiv boyunca taşıma ardılı vermeli.

    Bu, Glue'nun comp kuralının fiilen ve doğru işlediğinin delilidir;
    aşikâr olmayan bir denklik kullanıldığı için özdeşlikle geçiştirilemez.
    """
    Z = S.Tamsayi()
    uaS = L.ua(Z, Z, L.ardil_denkligi())
    denetle(uaS, S.yol(U, Z, Z), Baglam())
    for n in (-2, -1, 0, 1, 3):
        assert K.esdeger_mi(L.tasi(uaS, S.tam_sayi(n)), S.tam_sayi(n + 1)), n


def test_helix_ve_sarim():
    """π₁(S¹): sarmal tip denetiminden geçer, sarım sayısı hesaplanır.

    NOT: |n| ≥ 2 ve negatif n için hesap pratikte bitmez (hız duvarı,
    turetimler.bosluklar() kütüğünde kayıtlı); doğruluk meselesi değildir.
    """
    S1 = S.Cember()
    denetle(S.Lam("x", L.sarmal(D("x"))), S.ok(S1, U), Baglam())
    assert K.esdeger_mi(L.sarim(L.dongu_kuvveti(0)), S.tam_sayi(0))
    assert K.esdeger_mi(L.sarim(L.dongu_kuvveti(1)), S.tam_sayi(1))


# =====================================================================
#  6. Geometri katmanı: teğet, tensör, monoid nesnesi
# =====================================================================
def test_geometri_hepsi():
    from . import geometri as G
    neticeler = G.dogrula_hepsi()
    hatalar = [n for n in neticeler if n["netice"] != "GEÇTİ"]
    assert not hatalar, "geometri katmanında hata: %s" % hatalar
    assert len(neticeler) >= 20


# =====================================================================
#  Doğrudan çalıştırma
# =====================================================================
def _hepsini_calistir() -> int:
    isler = [(ad, f) for ad, f in sorted(globals().items())
             if ad.startswith("test_") and callable(f)]
    gecti = kaldi = 0
    for ad, f in isler:
        try:
            f()
            gecti += 1
            print("  ✓ %s" % ad)
        except Exception as e:  # noqa: BLE001
            kaldi += 1
            print("  ✗ %s\n      %s: %s" % (ad, type(e).__name__, e))
    print("\n%d geçti, %d kaldı  (%d sınama)" % (gecti, kaldi, len(isler)))
    return 0 if kaldi == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(_hepsini_calistir())
