#ifndef USB_TANIM_H
#define USB_TANIM_H

#include "hal.h"

#define USB_CIHAZ_TANIM_BAYT 18
#define USB_YAPILANDIRMA_TANIM_BAYT 32

typedef enum {
    USB_CC_VARSAYILAN = 0,
    USB_CC_1A5 = 1,
    USB_CC_3A0 = 2
} usb_cc_t;

typedef struct {
    usb_cc_t cc;
    int veri_yapilandirildi;
    int ozel_sarj_cihazi;
    uint16_t istenen_ma;
    uint16_t sarj_entegresi_azami_ma;
} usb_kaynak_t;

size_t usb_cihaz_tanimi(uint8_t *tampon, size_t kapasite, uint16_t vid, uint16_t pid);
size_t usb_yapilandirma_tanimi(uint8_t *tampon, size_t kapasite, uint16_t istenen_ma);
uint16_t usb_sarj_akim_siniri_ma(const usb_kaynak_t *k);

#endif
