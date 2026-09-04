"""``idrak.cozucu`` sınamaları — ispatlı çözüm ya da sükût."""

from __future__ import annotations

import os

import numpy as np
import pytest

from nefs.musahede import ARC, gorevleri_getir
from idrak import cozucu as cz

VERI_VAR = os.path.isdir(os.path.join(ARC, "training"))
veri_gerek = pytest.mark.skipif(not VERI_VAR, reason="ARC verisi yok")


# ══════════════════════════════════════════════════════════════════════
#  D₄ grubu — reel.meleke'deki permütasyon kapılarının ta kendisi
# ══════════════════════════════════════════════════════════════════════

def test_D4_sekiz_ogeli_ve_hepsi_tersinir():
    assert len(cz.D4) == 8
    g = np.arange(12).reshape(3, 4)
    goruntuler = set()
    for ad in cz.D4:
        h = cz.d4_uygula(g, ad)
        assert h.size == g.size                      # bilgi kaybı yok
        goruntuler.add(h.tobytes() + bytes(h.shape))
    assert len(goruntuler) == 8                      # sekizi de farklı


def test_D4_grup_kapali():
    """İki D₄ öğesinin bileşkesi yine D₄'te."""
    g = np.arange(16).reshape(4, 4)
    tabani = {cz.d4_uygula(g, a).tobytes() for a in cz.D4}
    for a in cz.D4:
        for b in cz.D4:
            assert cz.d4_uygula(cz.d4_uygula(g, a), b).tobytes() in tabani


def test_D4_permutasyon_yani_dik():
    """``reel.meleke`` ile bağ: bunlar permütasyon = dik kapılar."""
    n = 4
    g = np.arange(n * n).reshape(n, n)
    for ad in cz.D4:
        h = cz.d4_uygula(g, ad)
        if h.shape != g.shape:
            continue
        P = np.zeros((n * n, n * n))
        P[h.reshape(-1), g.reshape(-1)] = 1.0
        assert np.abs(P.T @ P - np.eye(n * n)).max() < 1e-12
        assert abs(abs(float(np.linalg.det(P))) - 1.0) < 1e-12


# ══════════════════════════════════════════════════════════════════════
#  Renk eşlemesi ve çelişki
# ══════════════════════════════════════════════════════════════════════

def test_renk_eslemesi_bulunuyor():
    a = np.array([[1, 2], [3, 1]])
    b = np.array([[5, 6], [7, 5]])
    f = cz.renk_eslemesi_bul([(a, b)])
    assert f == {1: 5, 2: 6, 3: 7}


def test_celiskili_renk_eslemesi_reddediliyor():
    """Aynı renk iki ayrı yere gidiyorsa uydurma YAPILMIYOR."""
    a = np.array([[1, 1]])
    b = np.array([[5, 6]])
    assert cz.renk_eslemesi_bul([(a, b)]) is None
    # şekil farkı da reddedilir
    assert cz.renk_eslemesi_bul([(np.zeros((2, 2)), np.zeros((3, 3)))]) is None


# ══════════════════════════════════════════════════════════════════════
#  Doğrulama: aday BÜTÜN çiftleri tutmalı
# ══════════════════════════════════════════════════════════════════════

def test_dogrula_tek_cift_tutmayinca_reddediyor():
    g1 = np.array([[1, 2], [3, 4]])
    ciftler = [(g1, np.fliplr(g1)), (g1, g1)]        # ikinci çift çelişik
    aday = [a for a in cz.adaylar(ciftler)
            if a.ad == "D4:yatay_ayna"][0]
    assert cz.dogrula(aday, [ciftler[0]])            # tek çiftte tutuyor
    assert not cz.dogrula(aday, ciftler)             # ikisinde tutmuyor


def test_dogrula_sekil_uyusmazligini_yakaliyor():
    g = np.array([[1, 2, 3]])
    aday = cz.Aday("büyüt", lambda x: np.tile(x, (2, 1)))
    assert not cz.dogrula(aday, [(g, g)])


def test_aday_istisna_atsa_bile_cokmuyor():
    aday = cz.Aday("patlar", lambda x: (_ for _ in ()).throw(RuntimeError()))
    assert cz.dogrula(aday, [(np.zeros((2, 2)), np.zeros((2, 2)))]) is False


# ══════════════════════════════════════════════════════════════════════
#  Uydurulmuş görevlerde uçtan uca
# ══════════════════════════════════════════════════════════════════════

def _gorev(ad, kural, girdiler):
    ciftler = [(g, kural(g)) for g in girdiler]
    return Gorev(ad, ciftler[:-1], ciftler[-1:])


def test_dondurme_gorevini_cozuyor():
    r = np.random.default_rng(0)
    g = _gorev("dön", lambda x: np.rot90(x, 1),
               [r.integers(0, 10, (3, 4)) for _ in range(4)])
    d = cz.gorev_coz(g)
    assert d["cevap_verildi"] and d["tam_mı"]
    assert "dön90" in d["kural"]


def test_renk_gorevini_cozuyor():
    r = np.random.default_rng(1)
    m = {i: (i * 3 + 1) % 10 for i in range(10)}
    g = _gorev("renk", lambda x: np.vectorize(m.get)(x).astype(np.int64),
               [r.integers(0, 10, (4, 4)) for _ in range(4)])
    d = cz.gorev_coz(g)
    assert d["cevap_verildi"] and d["tam_mı"]


def test_cozulemeyen_gorevde_SUSUYOR():
    """Ölçütün kalbi: tutan kural yoksa CEVAP VERİLMİYOR."""
    r = np.random.default_rng(2)
    ciftler = [(r.integers(0, 10, (4, 4)), r.integers(0, 10, (4, 4)))
               for _ in range(4)]
    g = Gorev("gürültü", ciftler[:-1], ciftler[-1:])
    d = cz.gorev_coz(g)
    assert d["cevap_verildi"] is False
    assert d["kural"] is None
    assert d["tam_mı"] is False


# ══════════════════════════════════════════════════════════════════════
#  Resmî küme üzerinde
# ══════════════════════════════════════════════════════════════════════

@veri_gerek
def test_egitim_kumesinde_en_az_bir_gorev_TAM_cozuluyor():
    """Kullanıcının şartı: en az bir görev %100 doğru."""
    r = cz.kume_coz(gorevleri_getir("training"))
    assert r["tam_çözülen"] >= 1
    assert r["tam_çözülen"] == len(r["tam_çözülen_ad"])


@veri_gerek
def test_dogrulama_bolmesinde_de_tam_cozum_var():
    """Sinir ağının HİÇ görmediği bölmede de tam çözüm."""
    e = gorevleri_getir("training")
    _egt, dog = gorevleri_getir(ne="böl", gorevler=e, dogrulama=100, tohum=0)
    r = cz.kume_coz(dog)
    assert r["tam_çözülen"] >= 1


@veri_gerek
def test_cevap_verince_isabet_yuksek():
    """Susma ölçütü işe yarıyor mu? — cevap verince isabet yüksek olmalı."""
    r = cz.kume_coz(gorevleri_getir("training"))
    assert r["cevap_verilen"] > 0
    assert r["isabet_cevap_verince"] > 0.8
    assert r["susulan"] > r["cevap_verilen"]        # çoğunlukla susuyor


@veri_gerek
def test_cozulen_gorevler_gercekten_dogrulaniyor():
    """Bağımsız teyit: çözülen her görev elle yeniden sınanıyor."""
    e = gorevleri_getir("training")
    r = cz.kume_coz(e)
    adlar = set(r["tam_çözülen_ad"])
    assert adlar
    for g in e:
        if g.ad not in adlar:
            continue
        d = cz.gorev_coz(g)
        kural = [a for a in cz.adaylar(g.egitim) if a.ad == d["kural"]][0]
        for a, b in g.egitim:                        # gösterim çiftleri
            assert np.array_equal(kural.uygula(a), b)
        for a, b in g.sinama:                        # SINAMA çiftleri
            assert np.array_equal(kural.uygula(a), b)


@veri_gerek
def test_degerlendirme_kumesi_bu_DSL_ile_cozulmuyor():
    """Dürüst başarısızlık: ARC-AGI-2 eval tam bunu yenmek için kuruldu."""
    r = cz.kume_coz(gorevleri_getir("evaluation"))
    assert r["tam_çözülen"] == 0
    assert r["görev"] == 120
