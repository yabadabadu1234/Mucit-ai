#include "gt911.h"

#define KAYIT_URUN 0x8140
#define KAYIT_DURUM 0x814E
#define KAYIT_NOKTA 0x814F
#define NOKTA_BAYT 8

static int kayit_oku(gt911_t *g, uint16_t kayit, uint8_t *veri, size_t n)
{
    uint8_t adres[2];
    adres[0] = (uint8_t)(kayit >> 8);
    adres[1] = (uint8_t)(kayit & 0xFF);
    if (g->i2c->yaz(g->i2c->baglam, g->adres, adres, 2) != 0) {
        return HATA_GIRIS_CIKIS;
    }
    if (g->i2c->oku(g->i2c->baglam, g->adres, veri, n) != 0) {
        return HATA_GIRIS_CIKIS;
    }
    return HATA_YOK;
}

static int kayit_yaz_bir(gt911_t *g, uint16_t kayit, uint8_t deger)
{
    uint8_t paket[3];
    paket[0] = (uint8_t)(kayit >> 8);
    paket[1] = (uint8_t)(kayit & 0xFF);
    paket[2] = deger;
    return g->i2c->yaz(g->i2c->baglam, g->adres, paket, 3) == 0 ? HATA_YOK : HATA_GIRIS_CIKIS;
}

int gt911_baslat(gt911_t *g, hal_i2c_t *i2c, uint8_t adres)
{
    uint8_t kimlik[4];
    int r;
    if (g == NULL || i2c == NULL || (adres != GT911_ADRES_A && adres != GT911_ADRES_B)) {
        return HATA_PARAMETRE;
    }
    g->i2c = i2c;
    g->adres = adres;
    r = kayit_oku(g, KAYIT_URUN, kimlik, sizeof kimlik);
    if (r != HATA_YOK) {
        return r;
    }
    if (kimlik[0] != '9' || kimlik[1] != '1' || kimlik[2] != '1' || kimlik[3] != 0) {
        return HATA_PROTOKOL;
    }
    return HATA_YOK;
}

int gt911_oku(gt911_t *g, dokunus_t nokta[GT911_AZAMI_NOKTA], uint8_t *adet, int *yeni_kare)
{
    uint8_t durum;
    uint8_t ham[NOKTA_BAYT * GT911_AZAMI_NOKTA];
    uint8_t n;
    uint8_t i;
    int r;

    if (g == NULL || nokta == NULL || adet == NULL || yeni_kare == NULL) {
        return HATA_PARAMETRE;
    }
    *adet = 0;
    *yeni_kare = 0;
    r = kayit_oku(g, KAYIT_DURUM, &durum, 1);
    if (r != HATA_YOK) {
        return r;
    }
    if ((durum & 0x80) == 0) {
        return HATA_YOK;
    }
    n = (uint8_t)(durum & 0x0F);
    if (n > GT911_AZAMI_NOKTA) {
        (void)kayit_yaz_bir(g, KAYIT_DURUM, 0);
        return HATA_PROTOKOL;
    }
    if (n > 0) {
        r = kayit_oku(g, KAYIT_NOKTA, ham, (size_t)n * NOKTA_BAYT);
        if (r != HATA_YOK) {
            return r;
        }
        for (i = 0; i < n; i++) {
            const uint8_t *p = ham + (size_t)i * NOKTA_BAYT;
            nokta[i].iz_no = p[0];
            nokta[i].x = (uint16_t)(p[1] | (p[2] << 8));
            nokta[i].y = (uint16_t)(p[3] | (p[4] << 8));
            nokta[i].boyut = (uint16_t)(p[5] | (p[6] << 8));
        }
    }
    r = kayit_yaz_bir(g, KAYIT_DURUM, 0);
    if (r != HATA_YOK) {
        return r;
    }
    *adet = n;
    *yeni_kare = 1;
    return HATA_YOK;
}
