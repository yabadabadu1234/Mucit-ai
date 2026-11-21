#ifndef MSC_SCSI_H
#define MSC_SCSI_H

#include "hal.h"

#define MSC_BLOK_BAYT 512

#define SCSI_TEST_UNIT_READY 0x00
#define SCSI_REQUEST_SENSE 0x03
#define SCSI_INQUIRY 0x12
#define SCSI_MODE_SENSE_6 0x1A
#define SCSI_START_STOP_UNIT 0x1B
#define SCSI_PREVENT_ALLOW 0x1E
#define SCSI_READ_CAPACITY_10 0x25
#define SCSI_READ_10 0x28
#define SCSI_WRITE_10 0x2A

typedef enum {
    MSC_SAHIP_YAZILIM = 0,
    MSC_SAHIP_ANA_BILGISAYAR = 1
} msc_sahip_t;

typedef enum {
    MSC_ISLEM_YOK = 0,
    MSC_ISLEM_OKU = 1,
    MSC_ISLEM_YAZ = 2
} msc_islem_t;

typedef struct {
    msc_islem_t islem;
    uint32_t lba;
    uint32_t adet;
} msc_istek_t;

typedef struct {
    hal_blok_t *blok;
    msc_sahip_t sahip;
    int kart_var;
    int yazma_korumali;
    int cikarma_istendi;
    uint8_t anahtar;
    uint8_t ek_kod;
    uint8_t ek_kod_nitelik;
} msc_t;

int msc_baslat(msc_t *m, hal_blok_t *blok);
int msc_komut(msc_t *m, const uint8_t *cdb, size_t cdb_uzunluk, uint8_t *yanit, size_t yanit_kapasite,
              size_t *yanit_uzunlugu, msc_istek_t *istek);
int msc_bloklari_oku(msc_t *m, const msc_istek_t *istek, uint32_t ilk, uint32_t adet, uint8_t *veri);
int msc_bloklari_yaz(msc_t *m, const msc_istek_t *istek, uint32_t ilk, uint32_t adet, const uint8_t *veri);

typedef struct {
    msc_t *msc;
    int acik_yazma_sayisi;
    int usb_bagli;
} ortam_t;

void ortam_baslat(ortam_t *o, msc_t *msc);
int ortam_ana_bilgisayara_ver(ortam_t *o);
void ortam_yazilima_al(ortam_t *o);

#endif
