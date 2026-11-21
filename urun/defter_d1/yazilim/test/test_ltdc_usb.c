#include <string.h>

#include "ltdc_zamanlama.h"
#include "test.h"
#include "usb_tanim.h"

static const panel_zamanlama_t PANEL = {800, 480, 1, 45, 210, 1, 22, 22, 862, 1200, 510, 650, 26400000u, 46800000u};

static void ltdc_testi(void)
{
    ltdc_kayit_t k;
    pllsai_t p;
    uint32_t yenileme;
    uint32_t bant;
    panel_zamanlama_t kotu;

    KONTROL(ltdc_toplam_genislik(&PANEL) == 1056);
    KONTROL(ltdc_toplam_yukseklik(&PANEL) == 525);
    KONTROL(ltdc_kayitlari_hesapla(&PANEL, &k) == HATA_YOK);
    KONTROL(k.sscr == ((0u << 16) | 0u));
    KONTROL(k.bpcr == ((45u << 16) | 22u));
    KONTROL(k.awcr == ((845u << 16) | 502u));
    KONTROL(k.twcr == ((1055u << 16) | 524u));

    KONTROL(pllsai_bul(8000000u, 33264000u, 5000u, &p) == HATA_YOK);
    KONTROL(p.cikis_hz > 33000000u && p.cikis_hz < 33600000u);
    KONTROL(p.pllm == 4 || p.pllm == 8);
    KONTROL(p.pllsain >= 50 && p.pllsain <= 432);
    KONTROL(p.pllsair >= 2 && p.pllsair <= 7);
    KONTROL(p.divr == 2 || p.divr == 4 || p.divr == 8 || p.divr == 16);
    {
        uint32_t vco_giris = 8000000u / p.pllm;
        uint32_t vco_cikis = vco_giris * p.pllsain;
        KONTROL(vco_giris >= 1000000u && vco_giris <= 2000000u);
        KONTROL(vco_cikis >= 100000000u && vco_cikis <= 432000000u);
        KONTROL(vco_cikis / p.pllsair / p.divr == p.cikis_hz);
    }
    KONTROL(ltdc_panel_dogrula(&PANEL, p.cikis_hz) == HATA_YOK);

    yenileme = ltdc_yenileme_mhz(&PANEL, p.cikis_hz);
    KONTROL(yenileme > 59000 && yenileme < 61500);

    bant = ltdc_tarama_bant_genisligi_bayt_s(p.cikis_hz, 16);
    KONTROL(bant > 60000000u && bant < 70000000u);
    {
        uint32_t sdram_tepe = 90000000u * 2u;
        KONTROL(bant < sdram_tepe / 2u);
    }

    KONTROL(ltdc_panel_dogrula(&PANEL, 90000000u) == HATA_PARAMETRE);
    KONTROL(ltdc_panel_dogrula(&PANEL, 20000000u) == HATA_PARAMETRE);
    kotu = PANEL;
    kotu.hfp = 5;
    KONTROL(ltdc_panel_dogrula(&kotu, 33264000u) == HATA_PARAMETRE);
    kotu = PANEL;
    kotu.vfp = 400;
    KONTROL(ltdc_panel_dogrula(&kotu, 33264000u) == HATA_PARAMETRE);
    kotu = PANEL;
    kotu.hsync = 0;
    KONTROL(ltdc_panel_dogrula(&kotu, 33264000u) == HATA_PARAMETRE);
    KONTROL(ltdc_kayitlari_hesapla(&kotu, &k) == HATA_PARAMETRE);
    KONTROL(ltdc_kayitlari_hesapla(NULL, &k) == HATA_PARAMETRE);
    KONTROL(pllsai_bul(8000000u, 33264000u, 0u, &p) == HATA_PARAMETRE);
    KONTROL(pllsai_bul(0, 33264000u, 5000u, &p) == HATA_PARAMETRE);
    KONTROL(pllsai_bul(8000000u, 5u, 1000u, &p) == HATA_PARAMETRE);
}

static void usb_testi(void)
{
    uint8_t d[32];
    size_t i;
    size_t toplam;
    usb_kaynak_t k;

    KONTROL(usb_cihaz_tanimi(d, sizeof d, 0x1209, 0x0001) == 18);
    KONTROL(d[0] == 18 && d[1] == 1 && d[2] == 0x00 && d[3] == 0x02);
    KONTROL(d[7] == 64);
    KONTROL(d[8] == 0x09 && d[9] == 0x12 && d[10] == 0x01 && d[11] == 0x00);
    KONTROL(d[17] == 1);
    KONTROL(usb_cihaz_tanimi(d, 10, 1, 1) == 0);
    KONTROL(usb_cihaz_tanimi(NULL, 32, 1, 1) == 0);

    KONTROL(usb_yapilandirma_tanimi(d, sizeof d, 100) == 32);
    KONTROL(d[0] == 9 && d[1] == 2 && d[2] == 32 && d[3] == 0);
    KONTROL((d[7] & 0xC0) == 0xC0);
    KONTROL(d[8] == 50);
    toplam = 0;
    i = 0;
    while (i < 32) {
        KONTROL(d[i] >= 2);
        toplam += d[i];
        i += d[i];
    }
    KONTROL(toplam == 32 && i == 32);
    KONTROL(d[9 + 1] == 4 && d[9 + 5] == 0x08 && d[9 + 6] == 0x06 && d[9 + 7] == 0x50);
    KONTROL(d[18 + 1] == 5 && d[18 + 2] == 0x81 && d[18 + 3] == 0x02 && d[18 + 4] == 64);
    KONTROL(d[25 + 1] == 5 && d[25 + 2] == 0x02 && d[25 + 3] == 0x02 && d[25 + 4] == 64);
    KONTROL(usb_yapilandirma_tanimi(d, sizeof d, 501) == 0);
    KONTROL(usb_yapilandirma_tanimi(d, 20, 100) == 0);

    memset(&k, 0, sizeof k);
    k.istenen_ma = 100;
    k.sarj_entegresi_azami_ma = 1500;
    KONTROL(usb_sarj_akim_siniri_ma(&k) == 100);
    k.veri_yapilandirildi = 1;
    KONTROL(usb_sarj_akim_siniri_ma(&k) == 100);
    k.istenen_ma = 500;
    KONTROL(usb_sarj_akim_siniri_ma(&k) == 500);
    k.cc = USB_CC_3A0;
    KONTROL(usb_sarj_akim_siniri_ma(&k) == 1500);
    k.sarj_entegresi_azami_ma = 1000;
    KONTROL(usb_sarj_akim_siniri_ma(&k) == 1000);
    k.cc = USB_CC_VARSAYILAN;
    k.veri_yapilandirildi = 0;
    k.ozel_sarj_cihazi = 1;
    KONTROL(usb_sarj_akim_siniri_ma(&k) == 1000);
    KONTROL(usb_sarj_akim_siniri_ma(NULL) == 0);
}

int main(void)
{
    ltdc_testi();
    usb_testi();
    SONUC("ltdc_usb");
}
