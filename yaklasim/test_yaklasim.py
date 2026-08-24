"""
yaklasim sınamaları.

    python3 -m yaklasim.test_yaklasim

Her sınama, ilgili katmanın DOSYADA YAZILI iddiasını doğrular. Bir iddia
ölçümle desteklenmiyorsa iddia düzeltilir, sınama gevşetilmez.
"""
from __future__ import annotations

import time
import traceback
from typing import Callable, Dict, List

import numpy as np

from . import akislar, genisletme, kara_kutu, modern, nedensel, simgesel


# =====================================================================
#  kara_kutu
# =====================================================================
def test_nfl_tam_sayim():
    for m, n in ((3, 3), (4, 2)):
        r = kara_kutu.nfl_tam_sayim(m, n)
        assert r["iz_dagilimlari_ayni"], (m, n)
        assert r["ortalamalar_ayni"], (m, n)


def test_nfl_kacamagi():
    r = kara_kutu.nfl_kacamagi()
    assert r["yapili_usul_daha_iyi"], r


def test_sifir_zinciri():
    r = kara_kutu.sifir_zinciri_sinamasi(k=8, adim=5)
    assert r["destek_dizisi"] == [1, 2, 3, 4, 5], r
    assert r["destek_adimla_sinirli"], r


def test_nesterov_alt_siniri():
    r = kara_kutu.alt_sinir_ihlal_var_mi()
    assert r["ihlal_yok"], r["ihlal"]


# =====================================================================
#  tikizlik
# =====================================================================
from . import tikizlik


def test_zorlayicilik_ayirt_ediliyor():
    z = tikizlik.zorlayici_mi(tikizlik.kare, 3)
    zn = tikizlik.zorlayici_mi(tikizlik.zorlayici_olmayan, 3)
    assert z["delil_artiyor"], z
    assert not zn["delil_artiyor"], zn


def test_alt_seviye_kumeleri():
    a = tikizlik.alt_seviye_sinirli_mi(tikizlik.kare, 3, c=4.0)
    b = tikizlik.alt_seviye_sinirli_mi(tikizlik.zorlayici_olmayan, 3, c=4.0)
    assert a["sinirli_gorunuyor"], a
    assert not b["sinirli_gorunuyor"], b
    assert abs(a["azami_norm"] - 2.0) < 0.05, a


def test_ulasilmayan_infimum():
    r = tikizlik.ulasilmayan_infimum()
    assert r["kaciyor"] and r["asgari_ulasilmadi"], r


def test_tikizlastirilamayanlar():
    p = tikizlik.sin_bir_bolu_x()
    assert p["iki_dizi_de_sifira_gidiyor"] and p["limitler_ayrisiyor"], p
    q = tikizlik.yon_bagimli_limit()
    assert q["cos2theta_ile_uyusuyor"] and q["limit_yok"], q


# =====================================================================
#  akislar
# =====================================================================
def test_vektor_akisi_yerel_tuzakta_kaliyor():
    r = akislar.yerel_tuzak()
    assert r["sig_cukurda_kaldi"], r


def test_topluluk_tuzaktan_kaciyor():
    r = akislar.tuzaktan_kacis()
    assert r["topluluk_kacti"], r
    assert not r["vektor_akisi_kacti"], r


def test_langevin_gibbs_ile_uyusuyor():
    r = akislar.gibbs_ile_kiyas()
    assert r["gibbs_ile_uyusuyor"], r
    assert r["kutle_uyusuyor"], r


def test_serbest_enerji_azaliyor():
    r = akislar.serbest_enerji_azaliyor_mu()
    assert r["azaldi"] and r["kayda_deger_artis_yok"], r


def test_egri_kisaltma_kanunu():
    r = akislar.egri_kisaltma()
    assert r["kanunla_uyusuyor"], r


# =====================================================================
#  genisletme
# =====================================================================
def test_kan_genisletmesi_evrensel():
    r = genisletme.kan_ozellikleri()
    assert r["ornekte_tam_oturma_hatasi"] < 1e-12, r
    assert r["lipschitz_asilmadi"], r
    assert r["hedef_arada"], r


def test_kan_ezberi_ve_duzenlileme():
    r = genisletme.ezber_kiyasi()
    assert r["kan_tam_oturuyor"], r
    assert r["gurultu_lipschitzi_patlatti"], r
    assert r["ezber_gorunuyor"], r
    assert r["duzenlileme_sinamayi_iyilestirdi"], r
    assert r["duzenlileme_egitimi_kotulestirdi"], r


def test_sobolev_turevi_iyilestiriyor():
    r = genisletme.sobolev_kiyasi()
    assert r["turev_iyilesti"], r
    assert r["sobolev__turev_hatasi"] < 0.2 * r["yalniz_deger__turev_hatasi"], r


# =====================================================================
#  simgesel
# =====================================================================
def test_temiz_veride_formul_bulunuyor():
    r = simgesel.temiz_veride_bulunuyor_mu()
    assert r["dogru_terimler"], r
    assert r["katsayilar_dogru"], r


def test_occam_cezasi_sadelestiriyor():
    r = simgesel.ceza_fazla_terimi_eliyor_mu()
    assert r["bic_dogruyu_buldu"], r
    assert r["bic_daha_sade"], r


def test_kutuphane_disi_zaafi():
    r = simgesel.kutuphane_disinda_ne_oluyor()
    assert r["icerde_iyi_gorunuyor"], r
    assert r["disarida_bozuluyor"], r


# =====================================================================
#  nedensel
# =====================================================================
def test_baglanim_mudahaleden_farkli():
    r = nedensel.baglanim_mudahale_ayrimi()
    assert r["ham_yanli"], r
    assert r["arka_kapi_dogru"], r
    assert r["deneysel_dogru"], r
    assert r["arka_kapi_deneyselle_uyusuyor"], r


def test_olculmemis_karistirici_zaafi():
    r = nedensel.olculmemis_karistirici()
    assert r["z_ile_hala_yanli"], r
    assert r["u_gorulunce_duzeliyor"], r


def test_catal_ve_carpisma():
    r = nedensel.catal_ve_carpisma()
    assert r["catal_sart_kosmak_duzeltti"], r
    assert r["carpisma_sart_kosmak_bozdu"], r


# =====================================================================
#  modern
# =====================================================================
def test_kan_ag_okunabilir():
    r = modern.kan_sinamasi(restart=4)
    assert r["iyi_uyduruyor"], r
    assert r["kenarlar_okunabilir"], r
    assert r["basarili_restart_sayisi"] >= 1, r


def test_fno_cozunurlukten_bagimsiz():
    r = modern.fno_sinamasi()
    assert r["ayni_cozunurluk_hatasi"] < 1e-8, r
    assert r["cozunurluk_aktarimi_calisiyor"], r
    assert r["yuksek_kipte_bozuluyor"], r


def test_deeponet_arayuz_farki():
    r = modern.deeponet_sinamasi()
    assert r["iyi_ogreniyor"], r
    assert not r["ham_aktarim_mumkun"], r
    assert r["fark_dogrulukta_degil_arayuzde"], r


# =====================================================================
#  koşturucu
# =====================================================================
def _sinamalar() -> List[Callable[[], None]]:
    g = globals()
    return [g[a] for a in sorted(g) if a.startswith("test_") and callable(g[a])]


def main() -> int:
    gecen, kalan = 0, []
    for f in _sinamalar():
        t0 = time.time()
        try:
            f()
            print("  ✓ %-42s %5.2fs" % (f.__name__, time.time() - t0))
            gecen += 1
        except Exception:
            print("  ✗ %-42s %5.2fs" % (f.__name__, time.time() - t0))
            traceback.print_exc()
            kalan.append(f.__name__)
    toplam = gecen + len(kalan)
    print("\n%d geçti, %d kaldı  (%d sınama)" % (gecen, len(kalan), toplam))
    return 1 if kalan else 0


if __name__ == "__main__":
    raise SystemExit(main())
