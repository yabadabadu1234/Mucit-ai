import unittest

import erc
import guc
import gunes
import kalinlik
import maliyet


class GucTesti(unittest.TestCase):
    def setUp(self):
        self.p = guc.parametreleri_yukle()

    def test_bekleme_en_az_guc(self):
        bekleme = guc.mod_gucu_w(self.p, "bekleme")
        for mod in ("yazma", "okuma", "kamera", "usb_aktarim"):
            self.assertLess(bekleme, guc.mod_gucu_w(self.p, mod))

    def test_yuk_carpani_dogrusal(self):
        self.assertAlmostEqual(guc.mod_gucu_w(self.p, "yazma", 2.0), 2 * guc.mod_gucu_w(self.p, "yazma"), places=9)

    def test_gun_profili_yirmi_dort_saat(self):
        self.assertAlmostEqual(sum(self.p["gun_profili_saat"].values()), 24.0, places=6)

    def test_pil_enerjisi(self):
        beklenen = 2.8 * 3.6 * 0.95
        self.assertAlmostEqual(guc.pil_enerjisi_wh(self.p), beklenen, places=9)

    def test_yirmi_dort_saat_ekran_acik_pil_yetmez(self):
        ihtiyac = 24 * guc.mod_gucu_w(self.p, "yazma")
        self.assertGreater(ihtiyac, guc.pil_enerjisi_wh(self.p))


class GunesTesti(unittest.TestCase):
    def setUp(self):
        self.p = guc.parametreleri_yukle()
        self.panel = gunes.panel_kur(self.p, 0.22)

    def test_tepe_guc_hesapla_ozdes(self):
        hesap = gunes.en_yuksek_guc_w(self.panel, 1000.0)
        self.assertAlmostEqual(hesap, self.panel["guc_stc_w"], delta=0.02 * self.panel["guc_stc_w"])

    def test_karanlikta_sifir(self):
        self.assertEqual(gunes.en_yuksek_guc_w(self.panel, 0.0), 0.0)
        self.assertEqual(gunes.dpm_pile_giren_w(self.p, self.panel, 0.0, 3.7), 0.0)

    def test_isinim_arttikca_guc_artar(self):
        onceki = -1.0
        for g in (5, 40, 150, 700, 1000):
            simdiki = gunes.en_yuksek_guc_w(self.panel, g)
            self.assertGreater(simdiki, onceki)
            onceki = simdiki

    def test_mppt_dpm_den_az_degil(self):
        for g in (150, 700, 1000):
            self.assertGreaterEqual(gunes.mppt_pile_giren_w(self.p, self.panel, g) * 1.0001,
                                    gunes.dpm_pile_giren_w(self.p, self.panel, g, 3.7))

    def test_dpm_gerilimi_acik_devre_geriliminin_ustundeyse_sifir(self):
        zayif = 0.0001
        self.assertEqual(gunes.dpm_pile_giren_w(self.p, self.panel, zayif, 3.7), 0.0)

    def test_gunluk_enerji_saatle_artar(self):
        temel = gunes.gunluk_enerji_wh(self.p, self.panel, "dpm")
        self.p["gunes"]["gun_saat"]["acik_hava_gunes_elde"] += 1.0
        self.assertGreater(gunes.gunluk_enerji_wh(self.p, self.panel, "dpm"), temel)

    def test_verim_arttikca_enerji_artar(self):
        dusuk = gunes.gunluk_enerji_wh(self.p, gunes.panel_kur(self.p, 0.20), "mppt")
        yuksek = gunes.gunluk_enerji_wh(self.p, gunes.panel_kur(self.p, 0.24), "mppt")
        self.assertGreater(yuksek, dusuk)


class KalinlikTesti(unittest.TestCase):
    def test_eink_lcd_den_ince(self):
        p = guc.parametreleri_yukle()
        self.assertLess(kalinlik.govde_kalinligi_mm(p, "eink"), kalinlik.govde_kalinligi_mm(p, "lcd"))

    def test_sirt_gövdeden_kalin(self):
        p = guc.parametreleri_yukle()
        self.assertGreater(kalinlik.sirt_kalinligi_mm(p), kalinlik.govde_kalinligi_mm(p, "lcd"))


class MaliyetTesti(unittest.TestCase):
    def test_alt_ust_sirasi(self):
        p = guc.parametreleri_yukle()
        alt, ust, _, _ = maliyet.kalem_toplami(p)
        self.assertLess(alt, ust)

    def test_her_kalemde_alt_ust(self):
        p = guc.parametreleri_yukle()
        for k in p["bom"]:
            self.assertLessEqual(k["usd_min"], k["usd_max"], k["ad"])

    def test_yerlilik_toplami_butun_toplam(self):
        p = guc.parametreleri_yukle()
        alt, ust, _, _ = maliyet.kalem_toplami(p)
        sinif_alt = sum(v[0] for v in maliyet.yerlilige_gore(p).values())
        self.assertAlmostEqual(alt, sinif_alt, places=9)

    def test_cikarilabilir_kalemler_listede(self):
        p = guc.parametreleri_yukle()
        adlar = {k["ad"] for k in p["bom"]}
        for liste in p["cikarilabilir_kalemler"].values():
            for ad in liste:
                self.assertIn(ad, adlar)


class ErcTesti(unittest.TestCase):
    def setUp(self):
        self.nl = erc.netlist_yukle()

    def reddedilenler(self, nl):
        return [ad for ad, tamam, _ in erc.kontrol_et(nl) if not tamam]

    def test_tasarim_gecer(self):
        self.assertEqual(self.reddedilenler(self.nl), [])

    def test_asiri_yuk_reddedilir(self):
        def bozuk(nl):
            nl["yukler"][0]["ma_maks"] = 2000
        self.assertIn("ray_akimi:V3V3", self.reddedilenler(erc.bozuk_kopya(self.nl, bozuk)))

    def test_yanlis_gerilim_reddedilir(self):
        def bozuk(nl):
            for y in nl["yukler"]:
                if y["blok"] == "KAMERA_ANALOG":
                    y["ray"] = "V3V3"
        self.assertIn("gerilim:KAMERA_ANALOG", self.reddedilenler(erc.bozuk_kopya(self.nl, bozuk)))

    def test_pin_tasmasi_reddedilir(self):
        def bozuk(nl):
            nl["arayuzler"].append({"ad": "FAZLA", "pin": 30, "aciklama": ""})
        self.assertIn("gpio_sayisi", self.reddedilenler(erc.bozuk_kopya(self.nl, bozuk)))

    def test_cakisan_i2c_adresi_reddedilir(self):
        def bozuk(nl):
            nl["i2c_adresleri"]["I2C1"][1]["adres"] = "0x5D"
        self.assertIn("i2c_adres:I2C1", self.reddedilenler(erc.bozuk_kopya(self.nl, bozuk)))

    def test_eksik_cc_direnci_reddedilir(self):
        def bozuk(nl):
            nl["usb"]["cc2_rd_kohm"] = 0
        self.assertIn("usb_cc", self.reddedilenler(erc.bozuk_kopya(self.nl, bozuk)))

    def test_pil_korumasiz_reddedilir(self):
        def bozuk(nl):
            nl["pil_ve_sarj"]["koruma_devresi"] = False
        self.assertIn("pil_koruma", self.reddedilenler(erc.bozuk_kopya(self.nl, bozuk)))

    def test_sdram_yetmezse_reddedilir(self):
        def bozuk(nl):
            nl["bellek"]["sdram_bayt"] = 1000000
        self.assertIn("sdram_kapasite", self.reddedilenler(erc.bozuk_kopya(self.nl, bozuk)))

    def test_seviye_ceviricisiz_kamera_reddedilir(self):
        def bozuk(nl):
            nl["seviye_cevirici"] = []
        self.assertIn("seviye:KAMERA_GIRIS_CIKIS", self.reddedilenler(erc.bozuk_kopya(self.nl, bozuk)))

    def test_kamera_3v3_rayinda_reddedilir(self):
        def bozuk(nl):
            for y in nl["yukler"]:
                if y["blok"] == "KAMERA_GIRIS_CIKIS":
                    y["ray"] = "V3V3"
            nl["seviye_cevirici"] = []
        self.assertIn("gerilim:KAMERA_GIRIS_CIKIS", self.reddedilenler(erc.bozuk_kopya(self.nl, bozuk)))

    def test_tanimsiz_ray_reddedilir(self):
        def bozuk(nl):
            nl["yukler"][1]["ray"] = "V9V9"
        self.assertIn("ray_yok:SDRAM", self.reddedilenler(erc.bozuk_kopya(self.nl, bozuk)))


if __name__ == "__main__":
    unittest.main()
