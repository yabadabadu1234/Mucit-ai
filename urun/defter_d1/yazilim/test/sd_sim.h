#ifndef SD_SIM_H
#define SD_SIM_H

#include <stdlib.h>
#include <string.h>

#include "sdspi.h"

typedef enum {
    SD_V2_YUKSEK = 0,
    SD_V2_STANDART = 1,
    SD_V1 = 2,
    SD_YOK = 3,
    SD_HAZIR_OLMAZ = 4
} sdsim_tur_t;

typedef enum {
    ST_KOMUT_BEKLE = 0,
    ST_KOMUT_TOPLA = 1,
    ST_YAZ_JETON = 2,
    ST_YAZ_VERI = 3,
    ST_YAZ_CRC = 4
} sdsim_durum_t;

#define SIM_DEPO 64

typedef struct {
    uint32_t lba;
    int kullanimda;
    uint8_t veri[512];
} sdsim_blok_t;

typedef struct {
    sdsim_tur_t tur;
    uint32_t blok_sayisi;
    int cs;
    int bosta;
    int uygulama_komutu;
    int baslatma_sayaci;
    int baslatma_gerekli;
    sdsim_durum_t durum;
    uint8_t komut[6];
    int komut_n;
    uint8_t cikis[1100];
    int cikis_n;
    int cikis_i;
    uint8_t yazma_tamponu[512];
    int yazma_n;
    uint32_t yazma_lba;
    int yazma_crc_n;
    int yazma_hatasi_enjekte;
    int mesgul_bayt;
    int aktarim_hatasi_no;
    int aktarim_sayisi;
    uint32_t son_oku_argumani;
    uint32_t son_yaz_argumani;
    sdsim_blok_t depo[SIM_DEPO];
    uint32_t milisaniye;
} sdsim_t;

static void sim_blok_deseni(uint32_t lba, uint8_t *veri)
{
    int i;
    for (i = 0; i < 512; i++) {
        veri[i] = (uint8_t)(lba * 31u + (uint32_t)i * 7u);
    }
}

static sdsim_blok_t *sim_depo_bul(sdsim_t *s, uint32_t lba, int olustur)
{
    int i;
    for (i = 0; i < SIM_DEPO; i++) {
        if (s->depo[i].kullanimda && s->depo[i].lba == lba) {
            return &s->depo[i];
        }
    }
    if (!olustur) {
        return NULL;
    }
    for (i = 0; i < SIM_DEPO; i++) {
        if (!s->depo[i].kullanimda) {
            s->depo[i].kullanimda = 1;
            s->depo[i].lba = lba;
            return &s->depo[i];
        }
    }
    return NULL;
}

static void sim_csd(const sdsim_t *s, uint8_t *csd)
{
    memset(csd, 0, 16);
    if (s->tur == SD_V2_YUKSEK || s->tur == SD_V2_STANDART) {
        uint32_t c = s->blok_sayisi / 1024u - 1u;
        csd[0] = 0x40;
        csd[5] = 0x09;
        csd[7] = (uint8_t)((c >> 16) & 0x3F);
        csd[8] = (uint8_t)(c >> 8);
        csd[9] = (uint8_t)c;
    } else {
        uint32_t c = s->blok_sayisi / 512u - 1u;
        csd[0] = 0x00;
        csd[5] = 0x09;
        csd[6] = (uint8_t)((c >> 10) & 0x03);
        csd[7] = (uint8_t)((c >> 2) & 0xFF);
        csd[8] = (uint8_t)((c & 0x03) << 6);
        csd[9] = 0x03;
        csd[10] = 0x80;
    }
}

static void sim_cikis_ekle(sdsim_t *s, uint8_t b)
{
    s->cikis[s->cikis_n++] = b;
}

static void sim_komut_isle(sdsim_t *s)
{
    uint8_t indeks = (uint8_t)(s->komut[0] & 0x3F);
    uint32_t arguman = ((uint32_t)s->komut[1] << 24) | ((uint32_t)s->komut[2] << 16) |
                       ((uint32_t)s->komut[3] << 8) | s->komut[4];
    int uygulama = s->uygulama_komutu;
    int yuksek = s->tur == SD_V2_YUKSEK;
    uint32_t lba;
    s->uygulama_komutu = 0;
    s->cikis_n = 0;
    s->cikis_i = 0;
    sim_cikis_ekle(s, 0xFF);

    if ((indeks == 0 || indeks == 8) && sdspi_crc7(s->komut, 5) != s->komut[5]) {
        sim_cikis_ekle(s, 0x08);
        return;
    }

    switch (indeks) {
    case 0:
        s->bosta = 1;
        s->baslatma_sayaci = 0;
        sim_cikis_ekle(s, 0x01);
        break;
    case 8:
        if (s->tur == SD_V1) {
            sim_cikis_ekle(s, 0x05);
        } else {
            sim_cikis_ekle(s, 0x01);
            sim_cikis_ekle(s, 0x00);
            sim_cikis_ekle(s, 0x00);
            sim_cikis_ekle(s, 0x01);
            sim_cikis_ekle(s, (uint8_t)(arguman & 0xFF));
        }
        break;
    case 55:
        s->uygulama_komutu = 1;
        sim_cikis_ekle(s, s->bosta ? 0x01 : 0x00);
        break;
    case 41:
        if (!uygulama) {
            sim_cikis_ekle(s, 0x05);
        } else if (s->tur == SD_HAZIR_OLMAZ) {
            sim_cikis_ekle(s, 0x01);
        } else {
            s->baslatma_sayaci++;
            if (s->baslatma_sayaci >= s->baslatma_gerekli) {
                s->bosta = 0;
            }
            sim_cikis_ekle(s, s->bosta ? 0x01 : 0x00);
        }
        break;
    case 58:
        sim_cikis_ekle(s, s->bosta ? 0x01 : 0x00);
        sim_cikis_ekle(s, (uint8_t)(0x80 | (yuksek ? 0x40 : 0x00)));
        sim_cikis_ekle(s, 0xFF);
        sim_cikis_ekle(s, 0x80);
        sim_cikis_ekle(s, 0x00);
        break;
    case 16:
        sim_cikis_ekle(s, arguman == 512 ? 0x00 : 0x40);
        break;
    case 9: {
        uint8_t csd[16];
        int i;
        sim_csd(s, csd);
        sim_cikis_ekle(s, 0x00);
        sim_cikis_ekle(s, 0xFF);
        sim_cikis_ekle(s, 0xFE);
        for (i = 0; i < 16; i++) {
            sim_cikis_ekle(s, csd[i]);
        }
        sim_cikis_ekle(s, 0x00);
        sim_cikis_ekle(s, 0x00);
        break;
    }
    case 17:
        s->son_oku_argumani = arguman;
        lba = yuksek ? arguman : arguman / 512u;
        if (lba >= s->blok_sayisi) {
            sim_cikis_ekle(s, 0x20);
        } else {
            sdsim_blok_t *b = sim_depo_bul(s, lba, 0);
            uint8_t veri[512];
            int i;
            if (b != NULL) {
                memcpy(veri, b->veri, 512);
            } else {
                sim_blok_deseni(lba, veri);
            }
            sim_cikis_ekle(s, 0x00);
            sim_cikis_ekle(s, 0xFF);
            sim_cikis_ekle(s, 0xFE);
            for (i = 0; i < 512; i++) {
                sim_cikis_ekle(s, veri[i]);
            }
            sim_cikis_ekle(s, 0x00);
            sim_cikis_ekle(s, 0x00);
        }
        break;
    case 24:
        s->son_yaz_argumani = arguman;
        lba = yuksek ? arguman : arguman / 512u;
        if (lba >= s->blok_sayisi) {
            sim_cikis_ekle(s, 0x20);
        } else {
            sim_cikis_ekle(s, 0x00);
            s->yazma_lba = lba;
            s->durum = ST_YAZ_JETON;
        }
        break;
    default:
        sim_cikis_ekle(s, 0x05);
        break;
    }
}

static uint8_t sim_bayt(sdsim_t *s, uint8_t tx)
{
    if (s->tur == SD_YOK || s->cs) {
        return 0xFF;
    }
    if (s->cikis_i < s->cikis_n) {
        uint8_t r = s->cikis[s->cikis_i++];
        if (s->cikis_i >= s->cikis_n && s->durum == ST_KOMUT_BEKLE) {
            s->cikis_i = 0;
            s->cikis_n = 0;
        }
        return r;
    }
    switch (s->durum) {
    case ST_KOMUT_BEKLE:
        if ((tx & 0xC0) == 0x40) {
            s->komut[0] = tx;
            s->komut_n = 1;
            s->durum = ST_KOMUT_TOPLA;
        }
        return 0xFF;
    case ST_KOMUT_TOPLA:
        s->komut[s->komut_n++] = tx;
        if (s->komut_n == 6) {
            s->durum = ST_KOMUT_BEKLE;
            sim_komut_isle(s);
        }
        return 0xFF;
    case ST_YAZ_JETON:
        if (tx == 0xFE) {
            s->durum = ST_YAZ_VERI;
            s->yazma_n = 0;
        }
        return 0xFF;
    case ST_YAZ_VERI:
        s->yazma_tamponu[s->yazma_n++] = tx;
        if (s->yazma_n == 512) {
            s->durum = ST_YAZ_CRC;
            s->yazma_crc_n = 0;
        }
        return 0xFF;
    case ST_YAZ_CRC:
        s->yazma_crc_n++;
        if (s->yazma_crc_n == 2) {
            int i;
            s->durum = ST_KOMUT_BEKLE;
            s->cikis_n = 0;
            s->cikis_i = 0;
            if (s->yazma_hatasi_enjekte) {
                sim_cikis_ekle(s, 0x0B);
            } else {
                sdsim_blok_t *b = sim_depo_bul(s, s->yazma_lba, 1);
                if (b != NULL) {
                    memcpy(b->veri, s->yazma_tamponu, 512);
                }
                sim_cikis_ekle(s, 0x05);
                for (i = 0; i < s->mesgul_bayt && s->cikis_n < (int)sizeof s->cikis - 2; i++) {
                    sim_cikis_ekle(s, 0x00);
                }
            }
        }
        return 0xFF;
    }
    return 0xFF;
}

static int sim_aktar(void *baglam, const uint8_t *giden, uint8_t *gelen, size_t n)
{
    sdsim_t *s = (sdsim_t *)baglam;
    size_t i;
    s->aktarim_sayisi++;
    if (s->aktarim_hatasi_no != 0 && s->aktarim_sayisi == s->aktarim_hatasi_no) {
        return -1;
    }
    for (i = 0; i < n; i++) {
        uint8_t r = sim_bayt(s, giden != NULL ? giden[i] : 0xFF);
        if (gelen != NULL) {
            gelen[i] = r;
        }
    }
    return 0;
}

static void sim_cs(void *baglam, int seviye)
{
    sdsim_t *s = (sdsim_t *)baglam;
    s->cs = seviye;
    if (seviye) {
        s->durum = ST_KOMUT_BEKLE;
        s->komut_n = 0;
        s->cikis_n = 0;
        s->cikis_i = 0;
    }
}

static uint32_t sim_ms(void *baglam)
{
    sdsim_t *s = (sdsim_t *)baglam;
    return s->milisaniye++;
}

static void sim_bekle(void *baglam, uint32_t ms)
{
    sdsim_t *s = (sdsim_t *)baglam;
    s->milisaniye += ms;
}

static void sdsim_baslat(sdsim_t *s, sdsim_tur_t tur, uint32_t blok_sayisi)
{
    memset(s, 0, sizeof *s);
    s->tur = tur;
    s->blok_sayisi = blok_sayisi;
    s->cs = 1;
    s->baslatma_gerekli = 3;
}

static hal_spi_t sdsim_spi(sdsim_t *s)
{
    hal_spi_t h;
    h.aktar = sim_aktar;
    h.cs = sim_cs;
    h.baglam = s;
    return h;
}

static hal_zaman_t sdsim_zaman(sdsim_t *s)
{
    hal_zaman_t z;
    z.milisaniye = sim_ms;
    z.bekle_ms = sim_bekle;
    z.baglam = s;
    return z;
}

#endif
