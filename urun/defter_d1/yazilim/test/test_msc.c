#include <stdlib.h>
#include <string.h>

#include "msc_scsi.h"
#include "test.h"

#define RAM_BLOK 2048u

typedef struct {
    uint8_t veri[RAM_BLOK * 512];
    int hata_oku;
    int hata_yaz;
    uint32_t say;
} ram_t;

static int ram_oku(void *b, uint32_t blok, uint32_t adet, uint8_t *veri)
{
    ram_t *r = (ram_t *)b;
    if (r->hata_oku || blok + adet > RAM_BLOK) {
        return -1;
    }
    memcpy(veri, r->veri + (size_t)blok * 512, (size_t)adet * 512);
    return 0;
}

static int ram_yaz(void *b, uint32_t blok, uint32_t adet, const uint8_t *veri)
{
    ram_t *r = (ram_t *)b;
    if (r->hata_yaz || blok + adet > RAM_BLOK) {
        return -1;
    }
    memcpy(r->veri + (size_t)blok * 512, veri, (size_t)adet * 512);
    return 0;
}

static uint32_t ram_sayisi(void *b)
{
    ram_t *r = (ram_t *)b;
    return r->say;
}

static int cdb_gonder(msc_t *m, const uint8_t *cdb, size_t n, uint8_t *yanit, size_t kap, size_t *uzun, msc_istek_t *istek)
{
    return msc_komut(m, cdb, n, yanit, kap, uzun, istek);
}

static void duyarlama_kontrol(msc_t *m, uint8_t anahtar, uint8_t ek, uint8_t nitelik, int satir)
{
    uint8_t cdb[6] = {SCSI_REQUEST_SENSE, 0, 0, 0, 18, 0};
    uint8_t yanit[64];
    size_t uzun = 0;
    msc_istek_t istek;
    int d = cdb_gonder(m, cdb, 6, yanit, sizeof yanit, &uzun, &istek);
    test_sayac++;
    if (d != 0 || uzun != 18 || yanit[0] != 0x70 || (yanit[2] & 0x0F) != anahtar || yanit[12] != ek ||
        yanit[13] != nitelik) {
        test_basarisiz++;
        printf("BASARISIZ duyarlama satir %d: anahtar %02X ek %02X nitelik %02X\n", satir, yanit[2], yanit[12], yanit[13]);
    }
}

int main(void)
{
    ram_t *ram = calloc(1, sizeof *ram);
    hal_blok_t blok;
    msc_t m;
    ortam_t o;
    uint8_t yanit[512 * 4];
    uint8_t veri[512 * 4];
    size_t uzun;
    msc_istek_t istek;
    int i;

    blok.oku = ram_oku;
    blok.yaz = ram_yaz;
    blok.blok_sayisi = ram_sayisi;
    blok.baglam = ram;
    ram->say = RAM_BLOK;

    KONTROL(msc_baslat(&m, &blok) == HATA_YOK);
    ortam_baslat(&o, &m);

    {
        uint8_t tur[6] = {SCSI_TEST_UNIT_READY, 0, 0, 0, 0, 0};
        KONTROL(cdb_gonder(&m, tur, 6, yanit, sizeof yanit, &uzun, &istek) == 1);
        duyarlama_kontrol(&m, 0x02, 0x04, 0x00, __LINE__);
        KONTROL(ortam_ana_bilgisayara_ver(&o) == HATA_YOK);
        KONTROL(cdb_gonder(&m, tur, 6, yanit, sizeof yanit, &uzun, &istek) == 0);
        m.kart_var = 0;
        KONTROL(cdb_gonder(&m, tur, 6, yanit, sizeof yanit, &uzun, &istek) == 1);
        duyarlama_kontrol(&m, 0x02, 0x3A, 0x00, __LINE__);
        m.kart_var = 1;
    }

    {
        uint8_t sorgu[6] = {SCSI_INQUIRY, 0, 0, 0, 36, 0};
        KONTROL(cdb_gonder(&m, sorgu, 6, yanit, sizeof yanit, &uzun, &istek) == 0);
        KONTROL(uzun == 36);
        KONTROL(yanit[0] == 0x00 && (yanit[1] & 0x80) == 0x80);
        KONTROL(memcmp(yanit + 8, "MUCITAI ", 8) == 0);
        KONTROL(memcmp(yanit + 16, "DEFTER D1       ", 16) == 0);
        KONTROL(yanit[4] == 31);
        KONTROL(cdb_gonder(&m, sorgu, 6, yanit, 10, &uzun, &istek) == 1);
    }

    {
        uint8_t kap[10] = {SCSI_READ_CAPACITY_10, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        KONTROL(cdb_gonder(&m, kap, 10, yanit, sizeof yanit, &uzun, &istek) == 0);
        KONTROL(uzun == 8);
        KONTROL(yanit[0] == 0 && yanit[1] == 0 && yanit[2] == 0x07 && yanit[3] == 0xFF);
        KONTROL(yanit[4] == 0 && yanit[5] == 0 && yanit[6] == 0x02 && yanit[7] == 0x00);
    }

    {
        uint8_t mod[6] = {SCSI_MODE_SENSE_6, 0, 0x3F, 0, 192, 0};
        KONTROL(cdb_gonder(&m, mod, 6, yanit, sizeof yanit, &uzun, &istek) == 0);
        KONTROL(uzun == 4 && yanit[0] == 3 && (yanit[2] & 0x80) == 0);
        m.yazma_korumali = 1;
        KONTROL(cdb_gonder(&m, mod, 6, yanit, sizeof yanit, &uzun, &istek) == 0);
        KONTROL((yanit[2] & 0x80) == 0x80);
        m.yazma_korumali = 0;
    }

    for (i = 0; i < (int)sizeof veri; i++) {
        veri[i] = (uint8_t)(i * 3 + 1);
    }
    {
        uint8_t yaz[10] = {SCSI_WRITE_10, 0, 0, 0, 0, 100, 0, 0, 4, 0};
        uint8_t oku[10] = {SCSI_READ_10, 0, 0, 0, 0, 100, 0, 0, 4, 0};
        msc_istek_t yistek;
        msc_istek_t oistek;
        KONTROL(cdb_gonder(&m, yaz, 10, yanit, sizeof yanit, &uzun, &yistek) == 0);
        KONTROL(yistek.islem == MSC_ISLEM_YAZ && yistek.lba == 100 && yistek.adet == 4);
        KONTROL(msc_bloklari_yaz(&m, &yistek, 0, 2, veri) == HATA_YOK);
        KONTROL(msc_bloklari_yaz(&m, &yistek, 2, 2, veri + 1024) == HATA_YOK);
        KONTROL(msc_bloklari_yaz(&m, &yistek, 3, 2, veri) == HATA_PARAMETRE);
        KONTROL(msc_bloklari_oku(&m, &yistek, 0, 1, yanit) == HATA_PARAMETRE);
        KONTROL(cdb_gonder(&m, oku, 10, yanit, sizeof yanit, &uzun, &oistek) == 0);
        KONTROL(oistek.islem == MSC_ISLEM_OKU);
        KONTROL(msc_bloklari_oku(&m, &oistek, 0, 4, yanit) == HATA_YOK);
        KONTROL(memcmp(yanit, veri, 2048) == 0);
        KONTROL(msc_bloklari_oku(&m, &oistek, 4, 1, yanit) == HATA_PARAMETRE);
        KONTROL(memcmp(ram->veri + 100 * 512, veri, 2048) == 0);

        ram->hata_oku = 1;
        KONTROL(msc_bloklari_oku(&m, &oistek, 0, 1, yanit) == HATA_GIRIS_CIKIS);
        duyarlama_kontrol(&m, 0x03, 0x11, 0x00, __LINE__);
        ram->hata_oku = 0;
        ram->hata_yaz = 1;
        KONTROL(msc_bloklari_yaz(&m, &yistek, 0, 1, veri) == HATA_GIRIS_CIKIS);
        duyarlama_kontrol(&m, 0x03, 0x03, 0x00, __LINE__);
        ram->hata_yaz = 0;
    }

    {
        uint8_t son[10] = {SCSI_READ_10, 0, 0, 0, 0x07, 0xFF, 0, 0, 1, 0};
        uint8_t tasma[10] = {SCSI_READ_10, 0, 0, 0, 0x07, 0xFF, 0, 0, 2, 0};
        uint8_t uzak[10] = {SCSI_READ_10, 0, 0xFF, 0xFF, 0xFF, 0xFF, 0, 0, 1, 0};
        uint8_t sifir[10] = {SCSI_READ_10, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        KONTROL(cdb_gonder(&m, son, 10, yanit, sizeof yanit, &uzun, &istek) == 0);
        KONTROL(cdb_gonder(&m, tasma, 10, yanit, sizeof yanit, &uzun, &istek) == 1);
        duyarlama_kontrol(&m, 0x05, 0x21, 0x00, __LINE__);
        KONTROL(cdb_gonder(&m, uzak, 10, yanit, sizeof yanit, &uzun, &istek) == 1);
        duyarlama_kontrol(&m, 0x05, 0x21, 0x00, __LINE__);
        KONTROL(cdb_gonder(&m, sifir, 10, yanit, sizeof yanit, &uzun, &istek) == 0);
        KONTROL(istek.islem == MSC_ISLEM_YOK);
        KONTROL(cdb_gonder(&m, son, 8, yanit, sizeof yanit, &uzun, &istek) == 1);
    }

    {
        uint8_t yaz[10] = {SCSI_WRITE_10, 0, 0, 0, 0, 5, 0, 0, 1, 0};
        m.yazma_korumali = 1;
        KONTROL(cdb_gonder(&m, yaz, 10, yanit, sizeof yanit, &uzun, &istek) == 1);
        duyarlama_kontrol(&m, 0x07, 0x27, 0x00, __LINE__);
        m.yazma_korumali = 0;
    }

    {
        uint8_t bilinmeyen[6] = {0xEE, 0, 0, 0, 0, 0};
        uint8_t cikar[6] = {SCSI_START_STOP_UNIT, 0, 0, 0, 0x02, 0};
        uint8_t kilit[6] = {SCSI_PREVENT_ALLOW, 0, 0, 0, 1, 0};
        KONTROL(cdb_gonder(&m, bilinmeyen, 6, yanit, sizeof yanit, &uzun, &istek) == 1);
        duyarlama_kontrol(&m, 0x05, 0x20, 0x00, __LINE__);
        KONTROL(cdb_gonder(&m, kilit, 6, yanit, sizeof yanit, &uzun, &istek) == 0);
        KONTROL(m.cikarma_istendi == 0);
        KONTROL(cdb_gonder(&m, cikar, 6, yanit, sizeof yanit, &uzun, &istek) == 0);
        KONTROL(m.cikarma_istendi == 1);
        KONTROL(cdb_gonder(&m, NULL, 6, yanit, sizeof yanit, &uzun, &istek) == 1);
        KONTROL(cdb_gonder(&m, kilit, 3, yanit, sizeof yanit, &uzun, &istek) == 1);
    }

    {
        uint8_t oku[10] = {SCSI_READ_10, 0, 0, 0, 0, 0, 0, 0, 1, 0};
        ortam_yazilima_al(&o);
        KONTROL(cdb_gonder(&m, oku, 10, yanit, sizeof yanit, &uzun, &istek) == 1);
        duyarlama_kontrol(&m, 0x02, 0x04, 0x00, __LINE__);
        o.acik_yazma_sayisi = 1;
        KONTROL(ortam_ana_bilgisayara_ver(&o) == HATA_MESGUL);
        KONTROL(m.sahip == MSC_SAHIP_YAZILIM);
        o.acik_yazma_sayisi = 0;
        KONTROL(ortam_ana_bilgisayara_ver(&o) == HATA_YOK);
        KONTROL(m.sahip == MSC_SAHIP_ANA_BILGISAYAR && o.usb_bagli == 1);
        KONTROL(cdb_gonder(&m, oku, 10, yanit, sizeof yanit, &uzun, &istek) == 0);
    }

    KONTROL(msc_baslat(NULL, &blok) == HATA_PARAMETRE);
    KONTROL(msc_komut(NULL, NULL, 0, NULL, 0, &uzun, &istek) == 1);

    free(ram);
    SONUC("msc_scsi");
}
