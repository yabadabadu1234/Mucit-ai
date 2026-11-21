#ifndef GT911_H
#define GT911_H

#include "hal.h"

#define GT911_ADRES_A 0x5D
#define GT911_ADRES_B 0x14
#define GT911_AZAMI_NOKTA 5

typedef struct {
    uint8_t iz_no;
    uint16_t x;
    uint16_t y;
    uint16_t boyut;
} dokunus_t;

typedef struct {
    hal_i2c_t *i2c;
    uint8_t adres;
} gt911_t;

int gt911_baslat(gt911_t *g, hal_i2c_t *i2c, uint8_t adres);
int gt911_oku(gt911_t *g, dokunus_t nokta[GT911_AZAMI_NOKTA], uint8_t *adet, int *yeni_kare);

#endif
