#include "sdspi.h"

#define JETON_OKU_BASLA 0xFE
#define YAZMA_KABUL 0x05

uint8_t sdspi_crc7(const uint8_t *veri, size_t uzunluk)
{
    uint8_t crc = 0;
    size_t i;
    int b;
    for (i = 0; i < uzunluk; i++) {
        uint8_t bayt = veri[i];
        for (b = 0; b < 8; b++) {
            uint8_t girdi = (uint8_t)(((bayt >> (7 - b)) & 1) ^ ((crc >> 6) & 1));
            crc = (uint8_t)((crc << 1) & 0x7F);
            if (girdi) {
                crc ^= 0x09;
            }
        }
    }
    return (uint8_t)((crc << 1) | 1);
}

static uint8_t bayt_aktar(sdspi_t *s, uint8_t giden)
{
    uint8_t gelen = 0xFF;
    if (s->spi->aktar(s->spi->baglam, &giden, &gelen, 1) != 0) {
        s->giris_cikis_hatasi = 1;
        return 0xFF;
    }
    return gelen;
}

static void toplu_oku(sdspi_t *s, uint8_t *veri, size_t n)
{
    if (s->spi->aktar(s->spi->baglam, NULL, veri, n) != 0) {
        s->giris_cikis_hatasi = 1;
    }
}

static void toplu_yaz(sdspi_t *s, const uint8_t *veri, size_t n)
{
    if (s->spi->aktar(s->spi->baglam, veri, NULL, n) != 0) {
        s->giris_cikis_hatasi = 1;
    }
}

static void cs_al(sdspi_t *s)
{
    s->spi->cs(s->spi->baglam, 0);
    (void)bayt_aktar(s, 0xFF);
}

static void cs_birak(sdspi_t *s)
{
    s->spi->cs(s->spi->baglam, 1);
    (void)bayt_aktar(s, 0xFF);
}

static uint8_t komut(sdspi_t *s, uint8_t indeks, uint32_t arguman)
{
    uint8_t cerceve[6];
    int i;
    cerceve[0] = (uint8_t)(0x40 | indeks);
    cerceve[1] = (uint8_t)(arguman >> 24);
    cerceve[2] = (uint8_t)(arguman >> 16);
    cerceve[3] = (uint8_t)(arguman >> 8);
    cerceve[4] = (uint8_t)arguman;
    cerceve[5] = sdspi_crc7(cerceve, 5);
    toplu_yaz(s, cerceve, sizeof cerceve);
    for (i = 0; i < 10; i++) {
        uint8_t r = bayt_aktar(s, 0xFF);
        if ((r & 0x80) == 0) {
            return r;
        }
    }
    return 0xFF;
}

static int cevap_hatasi(const sdspi_t *s, uint8_t r1)
{
    if (s->giris_cikis_hatasi) {
        return HATA_GIRIS_CIKIS;
    }
    return r1 == 0xFF ? HATA_KART_YOK : HATA_PROTOKOL;
}

static int jeton_bekle(sdspi_t *s, uint8_t jeton, uint32_t ms)
{
    uint32_t baslangic = s->zaman->milisaniye(s->zaman->baglam);
    for (;;) {
        uint8_t r = bayt_aktar(s, 0xFF);
        if (s->giris_cikis_hatasi) {
            return HATA_GIRIS_CIKIS;
        }
        if (r == jeton) {
            return HATA_YOK;
        }
        if (r != 0xFF) {
            return HATA_PROTOKOL;
        }
        if ((uint32_t)(s->zaman->milisaniye(s->zaman->baglam) - baslangic) >= ms) {
            return HATA_ZAMAN_ASIMI;
        }
    }
}

static int meshgul_bekle(sdspi_t *s, uint32_t ms)
{
    uint32_t baslangic = s->zaman->milisaniye(s->zaman->baglam);
    for (;;) {
        uint8_t r = bayt_aktar(s, 0xFF);
        if (s->giris_cikis_hatasi) {
            return HATA_GIRIS_CIKIS;
        }
        if (r == 0xFF) {
            return HATA_YOK;
        }
        if ((uint32_t)(s->zaman->milisaniye(s->zaman->baglam) - baslangic) >= ms) {
            return HATA_ZAMAN_ASIMI;
        }
    }
}

static int csd_coz(sdspi_t *s, const uint8_t *csd)
{
    uint8_t surum = (uint8_t)(csd[0] >> 6);
    if (surum == 1) {
        uint32_t c_boyut = ((uint32_t)(csd[7] & 0x3F) << 16) | ((uint32_t)csd[8] << 8) | csd[9];
        s->blok_sayisi = (c_boyut + 1u) * 1024u;
        return HATA_YOK;
    }
    if (surum == 0) {
        uint32_t c_boyut = ((uint32_t)(csd[6] & 0x03) << 10) | ((uint32_t)csd[7] << 2) | (uint32_t)(csd[8] >> 6);
        uint32_t carpan = (uint32_t)(((csd[9] & 0x03) << 1) | (csd[10] >> 7));
        uint32_t blok_uzunlugu = (uint32_t)(csd[5] & 0x0F);
        uint64_t bayt = ((uint64_t)(c_boyut + 1u) << (carpan + 2u)) << blok_uzunlugu;
        s->blok_sayisi = (uint32_t)(bayt / SDSPI_BLOK_BAYT);
        return HATA_YOK;
    }
    return HATA_PROTOKOL;
}

int sdspi_baslat(sdspi_t *s, hal_spi_t *spi, hal_zaman_t *zaman)
{
    uint8_t r1;
    uint8_t yanit[4];
    uint8_t csd[18];
    int surum2 = 0;
    int i;
    int hata;
    uint32_t baslangic;

    if (s == NULL || spi == NULL || zaman == NULL) {
        return HATA_PARAMETRE;
    }
    s->spi = spi;
    s->zaman = zaman;
    s->blok_sayisi = 0;
    s->yuksek_kapasite = 0;
    s->hazir = 0;
    s->giris_cikis_hatasi = 0;

    spi->cs(spi->baglam, 1);
    for (i = 0; i < 10; i++) {
        (void)bayt_aktar(s, 0xFF);
    }
    cs_al(s);

    r1 = 0xFF;
    for (i = 0; i < 10; i++) {
        r1 = komut(s, 0, 0);
        if (r1 == 0x01) {
            break;
        }
    }
    if (r1 != 0x01) {
        hata = cevap_hatasi(s, r1);
        cs_birak(s);
        return hata;
    }

    r1 = komut(s, 8, 0x1AA);
    if (r1 == 0x05) {
        surum2 = 0;
    } else if (r1 == 0x01) {
        toplu_oku(s, yanit, 4);
        if (yanit[2] != 0x01 || yanit[3] != 0xAA) {
            cs_birak(s);
            return HATA_PROTOKOL;
        }
        surum2 = 1;
    } else {
        hata = cevap_hatasi(s, r1);
        cs_birak(s);
        return hata;
    }

    baslangic = zaman->milisaniye(zaman->baglam);
    for (;;) {
        r1 = komut(s, 55, 0);
        if (r1 > 0x01) {
            hata = cevap_hatasi(s, r1);
            cs_birak(s);
            return hata;
        }
        r1 = komut(s, 41, surum2 ? 0x40000000u : 0u);
        if (r1 == 0x00) {
            break;
        }
        if (r1 > 0x01) {
            hata = cevap_hatasi(s, r1);
            cs_birak(s);
            return hata;
        }
        if ((uint32_t)(zaman->milisaniye(zaman->baglam) - baslangic) >= 1000u) {
            cs_birak(s);
            return HATA_ZAMAN_ASIMI;
        }
        zaman->bekle_ms(zaman->baglam, 1);
    }

    if (surum2) {
        r1 = komut(s, 58, 0);
        if (r1 != 0x00) {
            hata = cevap_hatasi(s, r1);
            cs_birak(s);
            return hata;
        }
        toplu_oku(s, yanit, 4);
        s->yuksek_kapasite = (yanit[0] & 0x40) != 0;
    }
    if (!s->yuksek_kapasite) {
        r1 = komut(s, 16, SDSPI_BLOK_BAYT);
        if (r1 != 0x00) {
            hata = cevap_hatasi(s, r1);
            cs_birak(s);
            return hata;
        }
    }

    r1 = komut(s, 9, 0);
    if (r1 != 0x00) {
        hata = cevap_hatasi(s, r1);
        cs_birak(s);
        return hata;
    }
    hata = jeton_bekle(s, JETON_OKU_BASLA, 200);
    if (hata != HATA_YOK) {
        cs_birak(s);
        return hata;
    }
    toplu_oku(s, csd, 18);
    cs_birak(s);
    if (s->giris_cikis_hatasi) {
        return HATA_GIRIS_CIKIS;
    }
    hata = csd_coz(s, csd);
    if (hata != HATA_YOK) {
        return hata;
    }
    s->hazir = 1;
    return HATA_YOK;
}

uint64_t sdspi_kapasite_bayt(const sdspi_t *s)
{
    return (uint64_t)s->blok_sayisi * SDSPI_BLOK_BAYT;
}

static int aralik_dogru(const sdspi_t *s, uint32_t blok, uint32_t adet)
{
    return s != NULL && s->hazir && adet > 0 && blok < s->blok_sayisi && adet <= s->blok_sayisi - blok;
}

int sdspi_oku(sdspi_t *s, uint32_t blok, uint32_t adet, uint8_t *veri)
{
    uint32_t i;
    if (veri == NULL || !aralik_dogru(s, blok, adet)) {
        return HATA_PARAMETRE;
    }
    for (i = 0; i < adet; i++) {
        uint32_t adres = s->yuksek_kapasite ? blok + i : (blok + i) * SDSPI_BLOK_BAYT;
        uint8_t crc[2];
        uint8_t r1;
        int hata;
        cs_al(s);
        r1 = komut(s, 17, adres);
        if (r1 != 0x00) {
            hata = cevap_hatasi(s, r1);
            cs_birak(s);
            return hata;
        }
        hata = jeton_bekle(s, JETON_OKU_BASLA, 200);
        if (hata != HATA_YOK) {
            cs_birak(s);
            return hata;
        }
        toplu_oku(s, veri + (size_t)i * SDSPI_BLOK_BAYT, SDSPI_BLOK_BAYT);
        toplu_oku(s, crc, 2);
        cs_birak(s);
        if (s->giris_cikis_hatasi) {
            return HATA_GIRIS_CIKIS;
        }
    }
    return HATA_YOK;
}

int sdspi_yaz(sdspi_t *s, uint32_t blok, uint32_t adet, const uint8_t *veri)
{
    uint32_t i;
    if (veri == NULL || !aralik_dogru(s, blok, adet)) {
        return HATA_PARAMETRE;
    }
    for (i = 0; i < adet; i++) {
        uint32_t adres = s->yuksek_kapasite ? blok + i : (blok + i) * SDSPI_BLOK_BAYT;
        uint8_t jeton = JETON_OKU_BASLA;
        uint8_t crc[2] = {0xFF, 0xFF};
        uint8_t r1;
        uint8_t cevap;
        int hata;
        cs_al(s);
        r1 = komut(s, 24, adres);
        if (r1 != 0x00) {
            hata = cevap_hatasi(s, r1);
            cs_birak(s);
            return hata;
        }
        (void)bayt_aktar(s, 0xFF);
        toplu_yaz(s, &jeton, 1);
        toplu_yaz(s, veri + (size_t)i * SDSPI_BLOK_BAYT, SDSPI_BLOK_BAYT);
        toplu_yaz(s, crc, 2);
        cevap = bayt_aktar(s, 0xFF);
        if (s->giris_cikis_hatasi) {
            cs_birak(s);
            return HATA_GIRIS_CIKIS;
        }
        if ((cevap & 0x1F) != YAZMA_KABUL) {
            cs_birak(s);
            return cevap == 0xFF ? HATA_KART_YOK : HATA_YAZMA_REDDI;
        }
        hata = meshgul_bekle(s, 500);
        cs_birak(s);
        if (hata != HATA_YOK) {
            return hata;
        }
    }
    return HATA_YOK;
}
