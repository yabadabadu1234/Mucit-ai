"""``hesap.palmer`` sınamaları — dört itirazın tartılması ve geri almalar."""

from __future__ import annotations

import math
from fractions import Fraction

import numpy as np
import pytest

from matematik import geometri as pa


# ══════════════════════════════════════════════════════════════════════
#  Kayıtların kendisi
# ══════════════════════════════════════════════════════════════════════

def test_palmer_iddialari_kayitli():
    for k in ("i_ilga_ediliyor_mu", "kubit_tavani", "bell",
              "superdeterminizm", "zemin"):
        assert k in pa.PALMER_IDDIALARI
    # en kritik nokta: i ilga EDİLMİYOR
    assert pa.PALMER_IDDIALARI["i_ilga_ediliyor_mu"].startswith("HAYIR")
    assert "SÜREKLİLİK" in pa.PALMER_IDDIALARI["i_ilga_ediliyor_mu"]
    # süperdeterminizm gizli değil, açık
    assert "AÇIKÇA" in pa.PALMER_IDDIALARI["superdeterminizm"]


def test_geri_almalar_ucu_de_yazili():
    assert len(pa.GERI_ALMALAR) == 3
    yerler = {g["nerede"] for g in pa.GERI_ALMALAR}
    assert any("saklama" in y for y in yerler)
    assert any("karmasik" in y for y in yerler)
    assert any("galois" in y for y in yerler)
    for g in pa.GERI_ALMALAR:
        assert g["yazdığım"] and g["kusur"] and g["düzeltme"]


# ══════════════════════════════════════════════════════════════════════
#  İtiraz 1: sürekli simetri
# ══════════════════════════════════════════════════════════════════════

def test_pisagor_donmeleri_birim_cemberde():
    for c, s in pa.pisagor_donmeleri(30):
        assert c * c + s * s == 1                  # TAM, kayan nokta değil
        assert isinstance(c, Fraction) and isinstance(s, Fraction)


def test_rasyonel_donmeler_grup():
    g = pa.rasyonel_grup_kapali_mi(40, 2000)
    assert g["grup_mu"]
    assert g["kapalı"] == g["deneme"]


def test_acilar_yogun_ama_en_kucuk_yok():
    """Yoğunluk var, SÜREKLİLİK yok — Noether itirazının özü."""
    onceki = None
    for az in (20, 60, 200, 600):
        a = pa.surekli_altgrup_var_mi(az)
        if onceki is not None:
            assert a["azamî_açı_boşluğu"] < onceki      # boşluk kapanıyor
            assert a["en_küçük_pozitif_açı"] < kucuk    # en küçük yok
        onceki = a["azamî_açı_boşluğu"]
        kucuk = a["en_küçük_pozitif_açı"]
    assert a["sıfırdan_farklı_en_küçük_var_mı"] is False
    assert a["limit_rasyonel_mi"] is False


def test_sin_bolu_teta_bire_gidiyor_ama_limit_disarida():
    a = pa.surekli_altgrup_var_mi(600)
    o = a["sin_bölü_teta_dizisi"]
    assert all(0.99 < x < 1.0 for x in o)          # 1'e yaklaşıyor
    assert all(x != 1.0 for x in o)                # ama ulaşmıyor


# ══════════════════════════════════════════════════════════════════════
#  İtiraz 2: Stone–von Neumann
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("N", [4, 8, 16])
def test_komutator_izi_her_zaman_sifir(N):
    e = pa.stone_von_neumann_engeli(N)
    assert e["komütatör_izi_azamî"] < 1e-10        # Tr(AB−BA) = 0
    assert e["iħI_izi"] == float(N)                # Tr(iħI) = N ≠ 0
    assert e["imkânsız_mı"]


@pytest.mark.parametrize("N", [8, 16, 64])
def test_kesilmis_fock_sapmasi_tam_eksi_N(N):
    """``kuantum.surekli``daki ölçüm = Stone–von Neumann engeli."""
    k = pa.sonlu_boyutta_kanonik_baginti(N)
    assert k["son_köşegen"] == pytest.approx(-N)
    assert k["alt_blok_sapma"] < 1e-12
    assert k["iz_sıfır_mı"]                        # iz sıfır KALMAK zorunda


def test_kuantum_surekli_ile_ayni_sayi():
    """İki modül aynı şeyi ölçüyor mu? — bağ kuruluyor."""
    from kuantum.surekli import komutator_sapmasi
    for N in (8, 32):
        a = komutator_sapmasi(N)
        b = pa.sonlu_boyutta_kanonik_baginti(N)
        assert a["son_köşegen"].real == pytest.approx(b["son_köşegen"])


# ══════════════════════════════════════════════════════════════════════
#  İtiraz 3: tensör çarpımı
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("m,n", [(2, 2), (2, 3), (4, 4), (3, 5)])
def test_tensor_boyutu_iki_kat_uyusmuyor(m, n):
    t = pa.tensor_boyut_uyusmazligi(m, n)
    assert t["dim_R(C^m ⊗ C^n)"] == 2 * m * n
    assert t["dim(R^2m ⊗ R^2n)"] == 4 * m * n
    assert t["oran"] == 2.0
    assert t["uyuşuyor_mu"] is False


def test_reel_gomme_tek_sistemde_carpimsal_birlesikte_degil():
    b = pa.reel_gomme_tek_sistemde_birebir()
    assert b["tek_sistemde_birebir_mi"]            # ρ(AB) = ρ(A)ρ(B)
    assert b["tek_sistem_çarpım_hatası"] < 1e-9
    assert b["şekiller_uyuşuyor_mu"] is False      # ρ(A⊗B) ≠ ρ(A)⊗ρ(B)
    assert b["birleşik_sol_şekil"] == (8, 8)
    assert b["birleşik_sağ_şekil"] == (16, 16)


def test_reel_karmasik_modulu_tek_sistemde_dogru():
    """``reel.karmasik`` hükmü tek sistemde geçerli kalıyor."""
    from matematik.geometri import reel_hamiltonyen, reel_evrim
    r = np.random.default_rng(0)
    A = r.normal(size=(3, 3)); A = A + A.T
    B = r.normal(size=(3, 3)); B = B - B.T
    H = A + 1j * B
    U = reel_evrim(H, 0.5)
    assert np.abs(U.T @ U - np.eye(6)).max() < 1e-10


# ══════════════════════════════════════════════════════════════════════
#  İtiraz 4: rasyonel CHSH
# ══════════════════════════════════════════════════════════════════════

def test_chsh_klasik_siniri_rasyonel_ayarla_asiyor():
    """Bell ihlali İRRASYONEL AÇIYA MUHTAÇ DEĞİL."""
    r = pa.rasyonel_ayarla_chsh(25)
    assert r["klasik_aşıldı_mı"]
    assert r["en_iyi_S"] > 2.8
    assert r["bütün_bileşenler_rasyonel_mi"]
    assert r["en_iyi_S"] <= r["tsirelson"] + 1e-12   # Tsirelson aşılmıyor


def test_chsh_tsirelsona_yaklasiyor():
    d = pa.en_iyi_rasyonel_chsh((5, 12, 25))
    s = [x["en_iyi_S"] for x in d]
    assert s == sorted(s)                            # tekdüze artıyor
    assert d[-1]["tsirelsona_uzaklık"] < 1e-4


def test_chsh_bilinen_ornekle_dogrulaniyor():
    """Kapalı form: en iyi açılar 0, π/4, π/8, 3π/8 → 2√2."""
    def v(t):
        return (math.cos(t), math.sin(t))
    S = pa.chshdegeri(v(0), v(math.pi / 2), v(math.pi / 4),
                      v(-math.pi / 4))
    assert abs(S) == pytest.approx(2 * math.sqrt(2), abs=1e-12)


def test_klasik_ayarla_sinir_asilmiyor():
    """Şahit: paralel/dik ayarlarda ihlal YOK."""
    e = (Fraction(1), Fraction(0))
    d = (Fraction(0), Fraction(1))
    assert abs(pa.chshdegeri(e, d, e, d)) <= 2.0 + 1e-12
    assert abs(pa.chshdegeri(e, e, e, e)) <= 2.0 + 1e-12
