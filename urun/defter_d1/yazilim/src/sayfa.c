#include <string.h>

#include "sayfa.h"

#define SURUM 1
#define BASLIK_BAYT 16

uint32_t sayfa_crc32(const uint8_t *veri, size_t uzunluk)
{
    uint32_t crc = 0xFFFFFFFFu;
    size_t i;
    int b;
    for (i = 0; i < uzunluk; i++) {
        crc ^= veri[i];
        for (b = 0; b < 8; b++) {
            crc = (crc >> 1) ^ (0xEDB88320u & (uint32_t)(-(int32_t)(crc & 1u)));
        }
    }
    return ~crc;
}

int sayfa_baslat(sayfa_t *s, uint16_t genislik, uint16_t yukseklik)
{
    if (s == NULL || genislik == 0 || yukseklik == 0) {
        return HATA_PARAMETRE;
    }
    s->genislik = genislik;
    s->yukseklik = yukseklik;
    s->nokta_sayisi = 0;
    s->strok_sayisi = 0;
    s->strok_baslangic[0] = 0;
    return HATA_YOK;
}

int sayfa_strok_ac(sayfa_t *s)
{
    if (s == NULL) {
        return HATA_PARAMETRE;
    }
    if (s->strok_sayisi >= SAYFA_STROK_AZAMI) {
        return HATA_YER_YOK;
    }
    s->strok_baslangic[s->strok_sayisi] = s->nokta_sayisi;
    s->strok_sayisi++;
    s->strok_baslangic[s->strok_sayisi] = s->nokta_sayisi;
    return HATA_YOK;
}

int sayfa_nokta_ekle(sayfa_t *s, uint16_t x, uint16_t y)
{
    if (s == NULL || s->strok_sayisi == 0 || x >= s->genislik || y >= s->yukseklik) {
        return HATA_PARAMETRE;
    }
    if (s->nokta_sayisi >= SAYFA_NOKTA_AZAMI) {
        return HATA_YER_YOK;
    }
    s->nokta[s->nokta_sayisi].x = x;
    s->nokta[s->nokta_sayisi].y = y;
    s->nokta_sayisi++;
    s->strok_baslangic[s->strok_sayisi] = s->nokta_sayisi;
    return HATA_YOK;
}

uint32_t sayfa_strok_nokta_sayisi(const sayfa_t *s, uint32_t strok)
{
    if (strok >= s->strok_sayisi) {
        return 0;
    }
    return s->strok_baslangic[strok + 1] - s->strok_baslangic[strok];
}

static void yaz16(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)(v & 0xFF);
    p[1] = (uint8_t)(v >> 8);
}

static void yaz32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)(v & 0xFF);
    p[1] = (uint8_t)((v >> 8) & 0xFF);
    p[2] = (uint8_t)((v >> 16) & 0xFF);
    p[3] = (uint8_t)(v >> 24);
}

static uint16_t oku16(const uint8_t *p)
{
    return (uint16_t)(p[0] | (p[1] << 8));
}

static uint32_t oku32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

int sayfa_serilestir(const sayfa_t *s, uint8_t *tampon, size_t kapasite, size_t *yazilan)
{
    size_t konum;
    uint32_t i;
    uint32_t j;
    if (s == NULL || tampon == NULL || yazilan == NULL || kapasite < BASLIK_BAYT + 4) {
        return HATA_PARAMETRE;
    }
    memcpy(tampon, "DFTR", 4);
    tampon[4] = SURUM;
    tampon[5] = 0;
    yaz16(tampon + 6, s->genislik);
    yaz16(tampon + 8, s->yukseklik);
    yaz16(tampon + 10, (uint16_t)s->strok_sayisi);
    yaz32(tampon + 12, s->nokta_sayisi);
    konum = BASLIK_BAYT;
    for (i = 0; i < s->strok_sayisi; i++) {
        uint32_t adet = sayfa_strok_nokta_sayisi(s, i);
        uint32_t ilk = s->strok_baslangic[i];
        if (konum + 2 + (size_t)adet * 4 + 4 > kapasite) {
            return HATA_YER_YOK;
        }
        yaz16(tampon + konum, (uint16_t)adet);
        konum += 2;
        for (j = 0; j < adet; j++) {
            const sayfa_nokta_t *n = &s->nokta[ilk + j];
            if (j == 0) {
                yaz16(tampon + konum, n->x);
                yaz16(tampon + konum + 2, n->y);
            } else {
                const sayfa_nokta_t *o = &s->nokta[ilk + j - 1];
                yaz16(tampon + konum, (uint16_t)((int32_t)n->x - (int32_t)o->x));
                yaz16(tampon + konum + 2, (uint16_t)((int32_t)n->y - (int32_t)o->y));
            }
            konum += 4;
        }
    }
    if (konum + 4 > kapasite) {
        return HATA_YER_YOK;
    }
    yaz32(tampon + konum, sayfa_crc32(tampon, konum));
    *yazilan = konum + 4;
    return HATA_YOK;
}

int sayfa_cozumle(sayfa_t *s, const uint8_t *tampon, size_t uzunluk)
{
    size_t konum;
    uint16_t strok_sayisi;
    uint32_t nokta_sayisi;
    uint32_t i;
    uint32_t j;
    uint32_t toplam = 0;

    if (s == NULL || tampon == NULL || uzunluk < BASLIK_BAYT + 4) {
        return HATA_PARAMETRE;
    }
    if (memcmp(tampon, "DFTR", 4) != 0 || tampon[4] != SURUM) {
        return HATA_BOZUK_VERI;
    }
    if (sayfa_crc32(tampon, uzunluk - 4) != oku32(tampon + uzunluk - 4)) {
        return HATA_BOZUK_VERI;
    }
    if (sayfa_baslat(s, oku16(tampon + 6), oku16(tampon + 8)) != HATA_YOK) {
        return HATA_BOZUK_VERI;
    }
    strok_sayisi = oku16(tampon + 10);
    nokta_sayisi = oku32(tampon + 12);
    if (strok_sayisi > SAYFA_STROK_AZAMI || nokta_sayisi > SAYFA_NOKTA_AZAMI) {
        return HATA_BOZUK_VERI;
    }
    konum = BASLIK_BAYT;
    for (i = 0; i < strok_sayisi; i++) {
        uint16_t adet;
        int32_t x = 0;
        int32_t y = 0;
        if (konum + 2 > uzunluk - 4) {
            return HATA_BOZUK_VERI;
        }
        adet = oku16(tampon + konum);
        konum += 2;
        if (adet == 0 || (size_t)adet * 4 > uzunluk - 4 - konum || toplam + adet > nokta_sayisi) {
            return HATA_BOZUK_VERI;
        }
        if (sayfa_strok_ac(s) != HATA_YOK) {
            return HATA_BOZUK_VERI;
        }
        for (j = 0; j < adet; j++) {
            if (j == 0) {
                x = oku16(tampon + konum);
                y = oku16(tampon + konum + 2);
            } else {
                x += (int16_t)oku16(tampon + konum);
                y += (int16_t)oku16(tampon + konum + 2);
            }
            konum += 4;
            if (x < 0 || y < 0 || sayfa_nokta_ekle(s, (uint16_t)x, (uint16_t)y) != HATA_YOK) {
                return HATA_BOZUK_VERI;
            }
        }
        toplam += adet;
    }
    if (toplam != nokta_sayisi || konum != uzunluk - 4) {
        return HATA_BOZUK_VERI;
    }
    return HATA_YOK;
}
