#ifndef SDSPI_H
#define SDSPI_H

#include "hal.h"

#define SDSPI_BLOK_BAYT 512

typedef struct {
    hal_spi_t *spi;
    hal_zaman_t *zaman;
    uint32_t blok_sayisi;
    int yuksek_kapasite;
    int hazir;
    int giris_cikis_hatasi;
} sdspi_t;

uint8_t sdspi_crc7(const uint8_t *veri, size_t uzunluk);
int sdspi_baslat(sdspi_t *s, hal_spi_t *spi, hal_zaman_t *zaman);
int sdspi_oku(sdspi_t *s, uint32_t blok, uint32_t adet, uint8_t *veri);
int sdspi_yaz(sdspi_t *s, uint32_t blok, uint32_t adet, const uint8_t *veri);
uint64_t sdspi_kapasite_bayt(const sdspi_t *s);

#endif
