#ifndef LTDC_ZAMANLAMA_H
#define LTDC_ZAMANLAMA_H

#include "hal.h"

#define LTDC_PIKSEL_SAATI_AZAMI_HZ 83000000u

typedef struct {
    uint16_t aktif_genislik;
    uint16_t aktif_yukseklik;
    uint16_t hsync;
    uint16_t hbp;
    uint16_t hfp;
    uint16_t vsync;
    uint16_t vbp;
    uint16_t vfp;
    uint16_t hdonem_asgari;
    uint16_t hdonem_azami;
    uint16_t vdonem_asgari;
    uint16_t vdonem_azami;
    uint32_t piksel_saati_asgari_hz;
    uint32_t piksel_saati_azami_hz;
} panel_zamanlama_t;

typedef struct {
    uint32_t sscr;
    uint32_t bpcr;
    uint32_t awcr;
    uint32_t twcr;
} ltdc_kayit_t;

typedef struct {
    uint8_t pllm;
    uint16_t pllsain;
    uint8_t pllsair;
    uint8_t divr;
    uint32_t cikis_hz;
} pllsai_t;

uint32_t ltdc_toplam_genislik(const panel_zamanlama_t *z);
uint32_t ltdc_toplam_yukseklik(const panel_zamanlama_t *z);
int ltdc_panel_dogrula(const panel_zamanlama_t *z, uint32_t piksel_saati_hz);
int ltdc_kayitlari_hesapla(const panel_zamanlama_t *z, ltdc_kayit_t *k);
uint32_t ltdc_yenileme_mhz(const panel_zamanlama_t *z, uint32_t piksel_saati_hz);
uint32_t ltdc_tarama_bant_genisligi_bayt_s(uint32_t piksel_saati_hz, uint32_t bit_derinligi);
int pllsai_bul(uint32_t hse_hz, uint32_t hedef_hz, uint32_t tolerans_ppm, pllsai_t *sonuc);

#endif
