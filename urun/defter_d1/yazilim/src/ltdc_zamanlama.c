#include "ltdc_zamanlama.h"

#define ALAN_AZAMI 0x0FFFu

uint32_t ltdc_toplam_genislik(const panel_zamanlama_t *z)
{
    return (uint32_t)z->hsync + z->hbp + z->aktif_genislik + z->hfp;
}

uint32_t ltdc_toplam_yukseklik(const panel_zamanlama_t *z)
{
    return (uint32_t)z->vsync + z->vbp + z->aktif_yukseklik + z->vfp;
}

int ltdc_panel_dogrula(const panel_zamanlama_t *z, uint32_t piksel_saati_hz)
{
    uint32_t ht;
    uint32_t vt;
    if (z == NULL || z->aktif_genislik == 0 || z->aktif_yukseklik == 0 || z->hsync == 0 || z->vsync == 0) {
        return HATA_PARAMETRE;
    }
    ht = ltdc_toplam_genislik(z);
    vt = ltdc_toplam_yukseklik(z);
    if (ht > ALAN_AZAMI || vt > ALAN_AZAMI) {
        return HATA_PARAMETRE;
    }
    if (ht < z->hdonem_asgari || ht > z->hdonem_azami || vt < z->vdonem_asgari || vt > z->vdonem_azami) {
        return HATA_PARAMETRE;
    }
    if (piksel_saati_hz < z->piksel_saati_asgari_hz || piksel_saati_hz > z->piksel_saati_azami_hz ||
        piksel_saati_hz > LTDC_PIKSEL_SAATI_AZAMI_HZ) {
        return HATA_PARAMETRE;
    }
    return HATA_YOK;
}

int ltdc_kayitlari_hesapla(const panel_zamanlama_t *z, ltdc_kayit_t *k)
{
    uint32_t hsw;
    uint32_t vsh;
    uint32_t ahbp;
    uint32_t avbp;
    uint32_t aaw;
    uint32_t aah;
    uint32_t tw;
    uint32_t th;
    if (z == NULL || k == NULL || z->aktif_genislik == 0 || z->aktif_yukseklik == 0 || z->hsync == 0 ||
        z->vsync == 0) {
        return HATA_PARAMETRE;
    }
    hsw = (uint32_t)z->hsync - 1u;
    vsh = (uint32_t)z->vsync - 1u;
    ahbp = (uint32_t)z->hsync + z->hbp - 1u;
    avbp = (uint32_t)z->vsync + z->vbp - 1u;
    aaw = (uint32_t)z->hsync + z->hbp + z->aktif_genislik - 1u;
    aah = (uint32_t)z->vsync + z->vbp + z->aktif_yukseklik - 1u;
    tw = ltdc_toplam_genislik(z) - 1u;
    th = ltdc_toplam_yukseklik(z) - 1u;
    if (tw > ALAN_AZAMI || th > ALAN_AZAMI) {
        return HATA_PARAMETRE;
    }
    k->sscr = (hsw << 16) | vsh;
    k->bpcr = (ahbp << 16) | avbp;
    k->awcr = (aaw << 16) | aah;
    k->twcr = (tw << 16) | th;
    return HATA_YOK;
}

uint32_t ltdc_yenileme_mhz(const panel_zamanlama_t *z, uint32_t piksel_saati_hz)
{
    uint64_t kare = (uint64_t)ltdc_toplam_genislik(z) * ltdc_toplam_yukseklik(z);
    return (uint32_t)(((uint64_t)piksel_saati_hz * 1000u) / kare);
}

uint32_t ltdc_tarama_bant_genisligi_bayt_s(uint32_t piksel_saati_hz, uint32_t bit_derinligi)
{
    return (uint32_t)(((uint64_t)piksel_saati_hz * bit_derinligi) / 8u);
}

int pllsai_bul(uint32_t hse_hz, uint32_t hedef_hz, uint32_t tolerans_ppm, pllsai_t *sonuc)
{
    static const uint8_t bolenler[4] = {2, 4, 8, 16};
    uint32_t en_iyi_hata = 0xFFFFFFFFu;
    int bulundu = 0;
    uint32_t m;
    uint32_t n;
    uint32_t r;
    uint32_t d;

    if (sonuc == NULL || hse_hz == 0 || hedef_hz == 0) {
        return HATA_PARAMETRE;
    }
    for (m = 2; m <= 63; m++) {
        uint32_t vco_giris;
        if (hse_hz % m != 0) {
            continue;
        }
        vco_giris = hse_hz / m;
        if (vco_giris < 1000000u || vco_giris > 2000000u) {
            continue;
        }
        for (n = 50; n <= 432; n++) {
            uint32_t vco_cikis = vco_giris * n;
            if (vco_cikis < 100000000u || vco_cikis > 432000000u) {
                continue;
            }
            for (r = 2; r <= 7; r++) {
                for (d = 0; d < 4; d++) {
                    uint32_t frekans = vco_cikis / r / bolenler[d];
                    uint32_t hata = frekans > hedef_hz ? frekans - hedef_hz : hedef_hz - frekans;
                    if (hata < en_iyi_hata) {
                        en_iyi_hata = hata;
                        sonuc->pllm = (uint8_t)m;
                        sonuc->pllsain = (uint16_t)n;
                        sonuc->pllsair = (uint8_t)r;
                        sonuc->divr = bolenler[d];
                        sonuc->cikis_hz = frekans;
                        bulundu = 1;
                    }
                }
            }
        }
    }
    if (!bulundu) {
        return HATA_PARAMETRE;
    }
    if ((uint64_t)en_iyi_hata * 1000000u > (uint64_t)tolerans_ppm * hedef_hz) {
        return HATA_PARAMETRE;
    }
    return HATA_YOK;
}
