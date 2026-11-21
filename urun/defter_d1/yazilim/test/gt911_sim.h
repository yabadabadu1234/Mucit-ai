#ifndef GT911_SIM_H
#define GT911_SIM_H

#include <string.h>

#include "gt911.h"

#define SIM_KAYIT_BASI 0x8000
#define SIM_KAYIT_BOYUT 0x200

typedef struct {
    uint8_t kayit[SIM_KAYIT_BOYUT];
    uint16_t isaretci;
    uint8_t adres;
    int islem_sayisi;
    int basarisiz_islem_no;
} gt911sim_t;

static int gt911sim_yaz(void *b, uint8_t adres, const uint8_t *veri, size_t n)
{
    gt911sim_t *s = (gt911sim_t *)b;
    size_t i;
    s->islem_sayisi++;
    if (s->basarisiz_islem_no != 0 && s->islem_sayisi == s->basarisiz_islem_no) {
        return -1;
    }
    if (adres != s->adres || n < 2) {
        return -1;
    }
    s->isaretci = (uint16_t)((veri[0] << 8) | veri[1]);
    for (i = 2; i < n; i++) {
        uint16_t konum = (uint16_t)(s->isaretci - SIM_KAYIT_BASI);
        if (konum >= SIM_KAYIT_BOYUT) {
            return -1;
        }
        s->kayit[konum] = veri[i];
        s->isaretci++;
    }
    return 0;
}

static int gt911sim_oku(void *b, uint8_t adres, uint8_t *veri, size_t n)
{
    gt911sim_t *s = (gt911sim_t *)b;
    size_t i;
    s->islem_sayisi++;
    if (s->basarisiz_islem_no != 0 && s->islem_sayisi == s->basarisiz_islem_no) {
        return -1;
    }
    if (adres != s->adres) {
        return -1;
    }
    for (i = 0; i < n; i++) {
        uint16_t konum = (uint16_t)(s->isaretci - SIM_KAYIT_BASI);
        if (konum >= SIM_KAYIT_BOYUT) {
            return -1;
        }
        veri[i] = s->kayit[konum];
        s->isaretci++;
    }
    return 0;
}

static void gt911sim_baslat(gt911sim_t *s, uint8_t adres)
{
    memset(s, 0, sizeof *s);
    s->adres = adres;
    s->kayit[0x140] = '9';
    s->kayit[0x141] = '1';
    s->kayit[0x142] = '1';
    s->kayit[0x143] = 0;
}

static hal_i2c_t gt911sim_hal(gt911sim_t *s)
{
    hal_i2c_t h;
    h.yaz = gt911sim_yaz;
    h.oku = gt911sim_oku;
    h.baglam = s;
    return h;
}

static void gt911sim_kare(gt911sim_t *s, const dokunus_t *nokta, uint8_t adet, uint8_t ham_adet_degeri)
{
    uint8_t i;
    for (i = 0; i < adet; i++) {
        uint8_t *p = &s->kayit[0x14F + 8 * i];
        p[0] = nokta[i].iz_no;
        p[1] = (uint8_t)(nokta[i].x & 0xFF);
        p[2] = (uint8_t)(nokta[i].x >> 8);
        p[3] = (uint8_t)(nokta[i].y & 0xFF);
        p[4] = (uint8_t)(nokta[i].y >> 8);
        p[5] = (uint8_t)(nokta[i].boyut & 0xFF);
        p[6] = (uint8_t)(nokta[i].boyut >> 8);
        p[7] = 0;
    }
    s->kayit[0x14E] = (uint8_t)(0x80 | ham_adet_degeri);
}

#endif
