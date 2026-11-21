#ifndef HAL_H
#define HAL_H

#include <stddef.h>
#include <stdint.h>

typedef enum {
    HATA_YOK = 0,
    HATA_GIRIS_CIKIS = -1,
    HATA_ZAMAN_ASIMI = -2,
    HATA_KART_YOK = -3,
    HATA_PARAMETRE = -4,
    HATA_PROTOKOL = -5,
    HATA_YAZMA_REDDI = -6,
    HATA_YER_YOK = -7,
    HATA_MESGUL = -8,
    HATA_BOZUK_VERI = -9
} hata_t;

typedef struct {
    int (*yaz)(void *baglam, uint8_t adres, const uint8_t *veri, size_t uzunluk);
    int (*oku)(void *baglam, uint8_t adres, uint8_t *veri, size_t uzunluk);
    void *baglam;
} hal_i2c_t;

typedef struct {
    int (*aktar)(void *baglam, const uint8_t *giden, uint8_t *gelen, size_t uzunluk);
    void (*cs)(void *baglam, int seviye);
    void *baglam;
} hal_spi_t;

typedef struct {
    uint32_t (*milisaniye)(void *baglam);
    void (*bekle_ms)(void *baglam, uint32_t ms);
    void *baglam;
} hal_zaman_t;

typedef struct {
    int (*oku)(void *baglam, uint32_t blok, uint32_t adet, uint8_t *veri);
    int (*yaz)(void *baglam, uint32_t blok, uint32_t adet, const uint8_t *veri);
    uint32_t (*blok_sayisi)(void *baglam);
    void *baglam;
} hal_blok_t;

#endif
