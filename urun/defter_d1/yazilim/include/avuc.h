#ifndef AVUC_H
#define AVUC_H

#include "gt911.h"

#define AVUC_IZ_AZAMI 8
#define AVUC_BEKLEYEN_AZAMI 16

typedef enum {
    SINIF_BELIRSIZ = 0,
    SINIF_KALEM = 1,
    SINIF_PARMAK = 2,
    SINIF_AVUC = 3
} sinif_t;

typedef struct {
    uint16_t kalem_azami_boyut;
    uint16_t avuc_asgari_boyut;
    uint16_t golge_yaricapi_px;
    uint32_t bekleme_ms;
} avuc_ayar_t;

typedef struct {
    sinif_t sinif;
    uint8_t iz_no;
    uint16_t x;
    uint16_t y;
    uint32_t zaman_ms;
    uint8_t bitti;
} avuc_cikis_t;

typedef struct {
    uint16_t x;
    uint16_t y;
    uint32_t zaman_ms;
} avuc_bekleyen_t;

typedef struct {
    uint8_t kullanimda;
    uint8_t iz_no;
    uint8_t goruldu;
    uint8_t yayin_basladi;
    sinif_t sinif;
    uint16_t ilk_x;
    uint16_t ilk_y;
    uint16_t x;
    uint16_t y;
    uint16_t en_buyuk_boyut;
    uint32_t baslangic_ms;
    uint8_t bekleyen_sayisi;
    avuc_bekleyen_t bekleyen[AVUC_BEKLEYEN_AZAMI];
} avuc_iz_t;

typedef struct {
    avuc_ayar_t ayar;
    avuc_iz_t iz[AVUC_IZ_AZAMI];
    uint32_t kayip;
} avuc_t;

int avuc_ayar_dogrula(const avuc_ayar_t *ayar);
int avuc_kalibre_et(avuc_ayar_t *ayar, const uint16_t *kalem_boyutlari, size_t kalem_adet,
                    const uint16_t *avuc_boyutlari, size_t avuc_adet,
                    uint16_t golge_yaricapi_px, uint32_t bekleme_ms);
int avuc_baslat(avuc_t *a, const avuc_ayar_t *ayar);
size_t avuc_isle(avuc_t *a, const dokunus_t *nokta, uint8_t adet, int yeni_kare, uint32_t simdi_ms,
                 avuc_cikis_t *cikis, size_t kapasite);
sinif_t avuc_sinifi(const avuc_t *a, uint8_t iz_no);

#endif
