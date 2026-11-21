#ifndef SAYFA_H
#define SAYFA_H

#include "hal.h"

#define SAYFA_NOKTA_AZAMI 20000u
#define SAYFA_STROK_AZAMI 2000u

typedef struct {
    uint16_t x;
    uint16_t y;
} sayfa_nokta_t;

typedef struct {
    uint16_t genislik;
    uint16_t yukseklik;
    uint32_t nokta_sayisi;
    uint32_t strok_sayisi;
    uint32_t strok_baslangic[SAYFA_STROK_AZAMI + 1];
    sayfa_nokta_t nokta[SAYFA_NOKTA_AZAMI];
} sayfa_t;

int sayfa_baslat(sayfa_t *s, uint16_t genislik, uint16_t yukseklik);
int sayfa_strok_ac(sayfa_t *s);
int sayfa_nokta_ekle(sayfa_t *s, uint16_t x, uint16_t y);
uint32_t sayfa_strok_nokta_sayisi(const sayfa_t *s, uint32_t strok);
int sayfa_serilestir(const sayfa_t *s, uint8_t *tampon, size_t kapasite, size_t *yazilan);
int sayfa_cozumle(sayfa_t *s, const uint8_t *tampon, size_t uzunluk);
uint32_t sayfa_crc32(const uint8_t *veri, size_t uzunluk);

#endif
