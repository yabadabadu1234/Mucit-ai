#ifndef GUC_YONETIMI_H
#define GUC_YONETIMI_H

#include "hal.h"

typedef struct {
    uint16_t mv;
    uint8_t yuzde;
} batarya_noktasi_t;

typedef struct {
    const batarya_noktasi_t *tablo;
    size_t adet;
    uint16_t ic_direnc_mohm;
} batarya_modeli_t;

int batarya_modeli_dogrula(const batarya_modeli_t *m);
uint8_t batarya_yuzde(const batarya_modeli_t *m, uint16_t olculen_mv, uint16_t yuk_ma);

typedef enum {
    GUC_AKTIF = 0,
    GUC_KARARMIS = 1,
    GUC_UYKU = 2,
    GUC_USB_AKTARIM = 3,
    GUC_KAPANIS = 4
} guc_durumu_t;

typedef struct {
    uint32_t karartma_ms;
    uint32_t uyku_ms;
    uint8_t uyari_yuzde;
    uint8_t kritik_yuzde;
    uint8_t histerezis_yuzde;
    uint8_t parlaklik_aktif;
    uint8_t parlaklik_kararmis;
} guc_ayar_t;

typedef struct {
    uint32_t simdi_ms;
    uint32_t son_etkinlik_ms;
    uint8_t pil_yuzde;
    int usb_vbus;
    int usb_veri_aktarimi;
    int tus_uyandirma;
} guc_girdi_t;

typedef struct {
    guc_durumu_t durum;
    uint8_t parlaklik;
    int ekran_acik;
    int uyari_goster;
    int notlari_kaydet;
    int kapat;
} guc_cikti_t;

typedef struct {
    guc_ayar_t ayar;
    guc_durumu_t durum;
    int uyari_acik;
    int kritik_verildi;
    int usb_onceki;
    uint32_t usb_cikis_ms;
} guc_t;

int guc_baslat(guc_t *g, const guc_ayar_t *ayar);
guc_cikti_t guc_guncelle(guc_t *g, const guc_girdi_t *girdi);

#endif
