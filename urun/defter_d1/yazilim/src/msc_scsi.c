#include <string.h>

#include "msc_scsi.h"

#define ANAHTAR_YOK 0x00
#define ANAHTAR_HAZIR_DEGIL 0x02
#define ANAHTAR_ORTAM_HATASI 0x03
#define ANAHTAR_GECERSIZ_ISTEK 0x05
#define ANAHTAR_YAZMA_KORUMALI 0x07

#define DURUM_IYI 0
#define DURUM_KONTROL 1

static int duyarla(msc_t *m, uint8_t anahtar, uint8_t ek, uint8_t nitelik)
{
    m->anahtar = anahtar;
    m->ek_kod = ek;
    m->ek_kod_nitelik = nitelik;
    return DURUM_KONTROL;
}

static void duyarlamayi_sil(msc_t *m)
{
    m->anahtar = ANAHTAR_YOK;
    m->ek_kod = 0;
    m->ek_kod_nitelik = 0;
}

static uint32_t buyuk_oku32(const uint8_t *p)
{
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) | ((uint32_t)p[2] << 8) | p[3];
}

static void buyuk_yaz32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)(v >> 24);
    p[1] = (uint8_t)(v >> 16);
    p[2] = (uint8_t)(v >> 8);
    p[3] = (uint8_t)v;
}

int msc_baslat(msc_t *m, hal_blok_t *blok)
{
    if (m == NULL || blok == NULL) {
        return HATA_PARAMETRE;
    }
    memset(m, 0, sizeof *m);
    m->blok = blok;
    m->sahip = MSC_SAHIP_YAZILIM;
    m->kart_var = 1;
    return HATA_YOK;
}

static int ortam_hazir_mi(msc_t *m)
{
    if (!m->kart_var) {
        return duyarla(m, ANAHTAR_HAZIR_DEGIL, 0x3A, 0x00);
    }
    if (m->sahip != MSC_SAHIP_ANA_BILGISAYAR) {
        return duyarla(m, ANAHTAR_HAZIR_DEGIL, 0x04, 0x00);
    }
    return DURUM_IYI;
}

static int aralik_gecerli(const msc_t *m, uint32_t lba, uint32_t adet)
{
    uint32_t toplam = m->blok->blok_sayisi(m->blok->baglam);
    return lba < toplam && adet <= toplam - lba;
}

int msc_komut(msc_t *m, const uint8_t *cdb, size_t cdb_uzunluk, uint8_t *yanit, size_t yanit_kapasite,
              size_t *yanit_uzunlugu, msc_istek_t *istek)
{
    int durum;
    if (m == NULL || istek == NULL || yanit_uzunlugu == NULL) {
        return DURUM_KONTROL;
    }
    *yanit_uzunlugu = 0;
    istek->islem = MSC_ISLEM_YOK;
    istek->lba = 0;
    istek->adet = 0;

    if (cdb == NULL || cdb_uzunluk < 6 || yanit == NULL) {
        return duyarla(m, ANAHTAR_GECERSIZ_ISTEK, 0x20, 0x00);
    }

    switch (cdb[0]) {
    case SCSI_TEST_UNIT_READY:
        durum = ortam_hazir_mi(m);
        if (durum == DURUM_IYI) {
            duyarlamayi_sil(m);
        }
        return durum;

    case SCSI_REQUEST_SENSE:
        if (yanit_kapasite < 18) {
            return duyarla(m, ANAHTAR_GECERSIZ_ISTEK, 0x24, 0x00);
        }
        memset(yanit, 0, 18);
        yanit[0] = 0x70;
        yanit[2] = m->anahtar;
        yanit[7] = 10;
        yanit[12] = m->ek_kod;
        yanit[13] = m->ek_kod_nitelik;
        *yanit_uzunlugu = 18;
        duyarlamayi_sil(m);
        return DURUM_IYI;

    case SCSI_INQUIRY:
        if (yanit_kapasite < 36) {
            return duyarla(m, ANAHTAR_GECERSIZ_ISTEK, 0x24, 0x00);
        }
        memset(yanit, 0, 36);
        yanit[1] = 0x80;
        yanit[2] = 0x04;
        yanit[3] = 0x02;
        yanit[4] = 31;
        memcpy(yanit + 8, "MUCITAI ", 8);
        memcpy(yanit + 16, "DEFTER D1       ", 16);
        memcpy(yanit + 32, "0001", 4);
        *yanit_uzunlugu = 36;
        return DURUM_IYI;

    case SCSI_MODE_SENSE_6:
        if (yanit_kapasite < 4) {
            return duyarla(m, ANAHTAR_GECERSIZ_ISTEK, 0x24, 0x00);
        }
        memset(yanit, 0, 4);
        yanit[0] = 3;
        yanit[2] = m->yazma_korumali ? 0x80 : 0x00;
        *yanit_uzunlugu = 4;
        return DURUM_IYI;

    case SCSI_START_STOP_UNIT:
        if ((cdb[4] & 0x03) == 0x02) {
            m->cikarma_istendi = 1;
        }
        return DURUM_IYI;

    case SCSI_PREVENT_ALLOW:
        return DURUM_IYI;

    case SCSI_READ_CAPACITY_10:
        durum = ortam_hazir_mi(m);
        if (durum != DURUM_IYI) {
            return durum;
        }
        if (yanit_kapasite < 8) {
            return duyarla(m, ANAHTAR_GECERSIZ_ISTEK, 0x24, 0x00);
        }
        if (m->blok->blok_sayisi(m->blok->baglam) == 0) {
            return duyarla(m, ANAHTAR_HAZIR_DEGIL, 0x3A, 0x00);
        }
        buyuk_yaz32(yanit, m->blok->blok_sayisi(m->blok->baglam) - 1u);
        buyuk_yaz32(yanit + 4, MSC_BLOK_BAYT);
        *yanit_uzunlugu = 8;
        return DURUM_IYI;

    case SCSI_READ_10:
    case SCSI_WRITE_10:
        if (cdb_uzunluk < 10) {
            return duyarla(m, ANAHTAR_GECERSIZ_ISTEK, 0x20, 0x00);
        }
        durum = ortam_hazir_mi(m);
        if (durum != DURUM_IYI) {
            return durum;
        }
        if (cdb[0] == SCSI_WRITE_10 && m->yazma_korumali) {
            return duyarla(m, ANAHTAR_YAZMA_KORUMALI, 0x27, 0x00);
        }
        istek->lba = buyuk_oku32(cdb + 2);
        istek->adet = (uint32_t)((cdb[7] << 8) | cdb[8]);
        if (istek->adet == 0) {
            istek->islem = MSC_ISLEM_YOK;
            return DURUM_IYI;
        }
        if (!aralik_gecerli(m, istek->lba, istek->adet)) {
            return duyarla(m, ANAHTAR_GECERSIZ_ISTEK, 0x21, 0x00);
        }
        istek->islem = cdb[0] == SCSI_READ_10 ? MSC_ISLEM_OKU : MSC_ISLEM_YAZ;
        return DURUM_IYI;

    default:
        return duyarla(m, ANAHTAR_GECERSIZ_ISTEK, 0x20, 0x00);
    }
}

static int blok_parametreleri_gecerli(const msc_t *m, const msc_istek_t *istek, uint32_t ilk, uint32_t adet)
{
    return m != NULL && istek != NULL && adet > 0 && ilk <= istek->adet && adet <= istek->adet - ilk;
}

int msc_bloklari_oku(msc_t *m, const msc_istek_t *istek, uint32_t ilk, uint32_t adet, uint8_t *veri)
{
    if (!blok_parametreleri_gecerli(m, istek, ilk, adet) || istek->islem != MSC_ISLEM_OKU || veri == NULL) {
        return HATA_PARAMETRE;
    }
    if (m->blok->oku(m->blok->baglam, istek->lba + ilk, adet, veri) != 0) {
        duyarla(m, ANAHTAR_ORTAM_HATASI, 0x11, 0x00);
        return HATA_GIRIS_CIKIS;
    }
    return HATA_YOK;
}

int msc_bloklari_yaz(msc_t *m, const msc_istek_t *istek, uint32_t ilk, uint32_t adet, const uint8_t *veri)
{
    if (!blok_parametreleri_gecerli(m, istek, ilk, adet) || istek->islem != MSC_ISLEM_YAZ || veri == NULL) {
        return HATA_PARAMETRE;
    }
    if (m->blok->yaz(m->blok->baglam, istek->lba + ilk, adet, veri) != 0) {
        duyarla(m, ANAHTAR_ORTAM_HATASI, 0x03, 0x00);
        return HATA_GIRIS_CIKIS;
    }
    return HATA_YOK;
}

void ortam_baslat(ortam_t *o, msc_t *msc)
{
    o->msc = msc;
    o->acik_yazma_sayisi = 0;
    o->usb_bagli = 0;
    msc->sahip = MSC_SAHIP_YAZILIM;
}

int ortam_ana_bilgisayara_ver(ortam_t *o)
{
    if (o->acik_yazma_sayisi > 0) {
        return HATA_MESGUL;
    }
    o->usb_bagli = 1;
    o->msc->sahip = MSC_SAHIP_ANA_BILGISAYAR;
    o->msc->cikarma_istendi = 0;
    return HATA_YOK;
}

void ortam_yazilima_al(ortam_t *o)
{
    o->usb_bagli = 0;
    o->msc->sahip = MSC_SAHIP_YAZILIM;
    o->msc->cikarma_istendi = 0;
}
