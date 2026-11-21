#include <string.h>

#include "guc_yonetimi.h"
#include "test.h"

static const batarya_noktasi_t TABLO[] = {
    {4200, 100}, {4100, 88}, {4000, 76}, {3900, 62}, {3800, 48}, {3700, 34},
    {3600, 20}, {3500, 10}, {3400, 5}, {3300, 2}, {3000, 0}
};

static const batarya_modeli_t MODEL = {TABLO, sizeof TABLO / sizeof TABLO[0], 80};

static const guc_ayar_t AYAR = {60000, 300000, 20, 5, 5, 80, 25};

static uint16_t yuzdeden_mv(uint8_t hedef)
{
    uint16_t mv;
    for (mv = 3000; mv <= 4200; mv++) {
        if (batarya_yuzde(&MODEL, mv, 0) >= hedef) {
            return mv;
        }
    }
    return 4200;
}

static void batarya_testi(void)
{
    uint32_t mv;
    uint8_t onceki = 0;
    size_t i;
    batarya_modeli_t kotu;
    batarya_noktasi_t sirasiz[] = {{4200, 100}, {4300, 50}, {3000, 0}};
    batarya_noktasi_t ustten_100_degil[] = {{4200, 99}, {3000, 0}};
    batarya_noktasi_t alttan_0_degil[] = {{4200, 100}, {3000, 3}};

    KONTROL(batarya_modeli_dogrula(&MODEL) == HATA_YOK);
    kotu = MODEL;
    kotu.tablo = sirasiz;
    kotu.adet = 3;
    KONTROL(batarya_modeli_dogrula(&kotu) == HATA_PARAMETRE);
    kotu.tablo = ustten_100_degil;
    kotu.adet = 2;
    KONTROL(batarya_modeli_dogrula(&kotu) == HATA_PARAMETRE);
    kotu.tablo = alttan_0_degil;
    KONTROL(batarya_modeli_dogrula(&kotu) == HATA_PARAMETRE);
    KONTROL(batarya_modeli_dogrula(NULL) == HATA_PARAMETRE);

    for (mv = 2800; mv <= 4400; mv += 1) {
        uint8_t y = batarya_yuzde(&MODEL, (uint16_t)mv, 0);
        KONTROL(y >= onceki);
        KONTROL(y <= 100);
        onceki = y;
    }
    for (i = 0; i < MODEL.adet; i++) {
        KONTROL(batarya_yuzde(&MODEL, TABLO[i].mv, 0) == TABLO[i].yuzde);
    }
    KONTROL(batarya_yuzde(&MODEL, 3750, 0) == 41);
    KONTROL(batarya_yuzde(&MODEL, 3750, 500) > batarya_yuzde(&MODEL, 3750, 0));
    KONTROL(batarya_yuzde(&MODEL, 3700, 500) == batarya_yuzde(&MODEL, 3740, 0));
}

static guc_girdi_t girdi(uint32_t t, uint32_t etkinlik, uint8_t yuzde, int vbus, int usb_veri)
{
    guc_girdi_t g;
    memset(&g, 0, sizeof g);
    g.simdi_ms = t;
    g.son_etkinlik_ms = etkinlik;
    g.pil_yuzde = yuzde;
    g.usb_vbus = vbus;
    g.usb_veri_aktarimi = usb_veri;
    return g;
}

static void durum_testi(void)
{
    guc_t g;
    guc_cikti_t c;
    guc_ayar_t kotu = AYAR;

    KONTROL(guc_baslat(&g, &AYAR) == HATA_YOK);
    kotu.uyku_ms = kotu.karartma_ms;
    KONTROL(guc_baslat(&g, &kotu) == HATA_PARAMETRE);
    kotu = AYAR;
    kotu.kritik_yuzde = kotu.uyari_yuzde;
    KONTROL(guc_baslat(&g, &kotu) == HATA_PARAMETRE);
    kotu = AYAR;
    kotu.histerezis_yuzde = 0;
    KONTROL(guc_baslat(&g, &kotu) == HATA_PARAMETRE);
    KONTROL(guc_baslat(&g, &AYAR) == HATA_YOK);

    c = guc_guncelle(&g, &(guc_girdi_t){1000, 0, 80, 0, 0, 0});
    KONTROL(c.durum == GUC_AKTIF && c.ekran_acik && c.parlaklik == 80);

    c = guc_guncelle(&g, &(guc_girdi_t){61000, 0, 80, 0, 0, 0});
    KONTROL(c.durum == GUC_KARARMIS && c.ekran_acik && c.parlaklik == 25);

    c = guc_guncelle(&g, &(guc_girdi_t){301000, 0, 80, 0, 0, 0});
    KONTROL(c.durum == GUC_UYKU && !c.ekran_acik && c.parlaklik == 0);

    c = guc_guncelle(&g, &(guc_girdi_t){301100, 0, 80, 0, 0, 1});
    KONTROL(c.durum == GUC_AKTIF && c.ekran_acik);

    c = guc_guncelle(&g, &(guc_girdi_t){400000, 399000, 80, 1, 1, 0});
    KONTROL(c.durum == GUC_USB_AKTARIM && !c.ekran_acik);

    c = guc_guncelle(&g, &(guc_girdi_t){700000, 10, 80, 1, 1, 0});
    KONTROL(c.durum == GUC_USB_AKTARIM);

    c = guc_guncelle(&g, &(guc_girdi_t){701000, 10, 80, 1, 0, 0});
    KONTROL(c.durum == GUC_AKTIF && c.ekran_acik);
    c = guc_guncelle(&g, &(guc_girdi_t){750000, 10, 80, 1, 0, 0});
    KONTROL(c.durum == GUC_AKTIF);
    c = guc_guncelle(&g, &(guc_girdi_t){770000, 10, 80, 1, 0, 0});
    KONTROL(c.durum == GUC_KARARMIS);
}

static void uyari_ve_kritik_testi(void)
{
    guc_t g;
    guc_cikti_t c;
    static const uint8_t gurultu[] = {22, 21, 20, 21, 22, 24, 25, 26, 21, 20, 19, 22};
    static const int beklenen_uyari[] = {0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1};
    size_t i;
    int kayit_sayisi = 0;

    KONTROL(guc_baslat(&g, &AYAR) == HATA_YOK);
    for (i = 0; i < sizeof gurultu; i++) {
        guc_girdi_t gi = girdi(1000 + (uint32_t)i, 1000, gurultu[i], 0, 0);
        c = guc_guncelle(&g, &gi);
        KONTROL(c.uyari_goster == beklenen_uyari[i]);
    }

    for (i = 0; i < 6; i++) {
        guc_girdi_t gi = girdi(2000 + (uint32_t)i, 2000, (uint8_t)(8 - i), 0, 0);
        c = guc_guncelle(&g, &gi);
        if (c.notlari_kaydet) {
            kayit_sayisi++;
        }
        if ((8 - (int)i) > 5) {
            KONTROL(c.kapat == 0 && c.durum != GUC_KAPANIS);
        } else {
            KONTROL(c.kapat == 1 && c.durum == GUC_KAPANIS);
        }
    }
    KONTROL(kayit_sayisi == 1);

    {
        guc_girdi_t gi = girdi(3000, 3000, 50, 0, 0);
        c = guc_guncelle(&g, &gi);
        KONTROL(c.kapat == 1);
        gi = girdi(3001, 3001, 4, 1, 0);
        c = guc_guncelle(&g, &gi);
        KONTROL(c.kapat == 1);
        gi = girdi(3002, 3002, 10, 1, 0);
        c = guc_guncelle(&g, &gi);
        KONTROL(c.kapat == 0 && c.durum == GUC_AKTIF && c.ekran_acik);
    }

    KONTROL(guc_baslat(&g, &AYAR) == HATA_YOK);
    {
        guc_girdi_t gi = girdi(10, 10, 4, 1, 0);
        c = guc_guncelle(&g, &gi);
        KONTROL(c.kapat == 0 && c.notlari_kaydet == 0);
    }
}

static void bosalma_benzetimi(void)
{
    guc_t g;
    uint32_t dakika;
    int kayit_sayisi = 0;
    int ilk_kapat = -1;
    int ilk_kayit = -1;
    double enerji_wh = 9.58;
    double guc_w = 1.318;
    double harcanan = 0.0;
    uint16_t son_mv = 4200;
    KONTROL(guc_baslat(&g, &AYAR) == HATA_YOK);
    for (dakika = 0; dakika < 600; dakika++) {
        double oran = 1.0 - harcanan / enerji_wh;
        uint8_t hedef;
        uint16_t mv;
        guc_girdi_t gi;
        guc_cikti_t c;
        if (oran < 0.0) {
            oran = 0.0;
        }
        hedef = (uint8_t)(oran * 100.0);
        mv = yuzdeden_mv(hedef);
        son_mv = mv;
        gi = girdi(dakika * 60000u, dakika * 60000u, batarya_yuzde(&MODEL, mv, 300), 0, 0);
        c = guc_guncelle(&g, &gi);
        if (c.notlari_kaydet) {
            kayit_sayisi++;
            if (ilk_kayit < 0) {
                ilk_kayit = (int)dakika;
            }
        }
        if (c.kapat && ilk_kapat < 0) {
            ilk_kapat = (int)dakika;
        }
        if (c.kapat) {
            break;
        }
        harcanan += guc_w / 60.0;
    }
    KONTROL(kayit_sayisi == 1);
    KONTROL(ilk_kapat >= 0 && ilk_kapat == ilk_kayit);
    KONTROL(son_mv >= 3200);
    KONTROL(ilk_kapat > 360 && ilk_kapat < 440);
}

int main(void)
{
    batarya_testi();
    durum_testi();
    uyari_ve_kritik_testi();
    bosalma_benzetimi();
    SONUC("guc_yonetimi");
}
