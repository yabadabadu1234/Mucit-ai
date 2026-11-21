#include <string.h>

#include "usb_tanim.h"

size_t usb_cihaz_tanimi(uint8_t *tampon, size_t kapasite, uint16_t vid, uint16_t pid)
{
    if (tampon == NULL || kapasite < USB_CIHAZ_TANIM_BAYT) {
        return 0;
    }
    memset(tampon, 0, USB_CIHAZ_TANIM_BAYT);
    tampon[0] = USB_CIHAZ_TANIM_BAYT;
    tampon[1] = 0x01;
    tampon[2] = 0x00;
    tampon[3] = 0x02;
    tampon[7] = 64;
    tampon[8] = (uint8_t)(vid & 0xFF);
    tampon[9] = (uint8_t)(vid >> 8);
    tampon[10] = (uint8_t)(pid & 0xFF);
    tampon[11] = (uint8_t)(pid >> 8);
    tampon[12] = 0x00;
    tampon[13] = 0x01;
    tampon[14] = 1;
    tampon[15] = 2;
    tampon[16] = 3;
    tampon[17] = 1;
    return USB_CIHAZ_TANIM_BAYT;
}

size_t usb_yapilandirma_tanimi(uint8_t *tampon, size_t kapasite, uint16_t istenen_ma)
{
    uint8_t *p;
    if (tampon == NULL || kapasite < USB_YAPILANDIRMA_TANIM_BAYT || istenen_ma > 500) {
        return 0;
    }
    memset(tampon, 0, USB_YAPILANDIRMA_TANIM_BAYT);
    p = tampon;
    p[0] = 9;
    p[1] = 0x02;
    p[2] = USB_YAPILANDIRMA_TANIM_BAYT;
    p[3] = 0;
    p[4] = 1;
    p[5] = 1;
    p[6] = 0;
    p[7] = 0xC0;
    p[8] = (uint8_t)(istenen_ma / 2);
    p += 9;
    p[0] = 9;
    p[1] = 0x04;
    p[2] = 0;
    p[3] = 0;
    p[4] = 2;
    p[5] = 0x08;
    p[6] = 0x06;
    p[7] = 0x50;
    p[8] = 0;
    p += 9;
    p[0] = 7;
    p[1] = 0x05;
    p[2] = 0x81;
    p[3] = 0x02;
    p[4] = 64;
    p[5] = 0;
    p[6] = 0;
    p += 7;
    p[0] = 7;
    p[1] = 0x05;
    p[2] = 0x02;
    p[3] = 0x02;
    p[4] = 64;
    p[5] = 0;
    p[6] = 0;
    return USB_YAPILANDIRMA_TANIM_BAYT;
}

uint16_t usb_sarj_akim_siniri_ma(const usb_kaynak_t *k)
{
    uint16_t sinir;
    if (k == NULL) {
        return 0;
    }
    if (k->ozel_sarj_cihazi || k->cc == USB_CC_1A5 || k->cc == USB_CC_3A0) {
        sinir = 1500;
    } else if (k->veri_yapilandirildi) {
        sinir = k->istenen_ma;
    } else {
        sinir = 100;
    }
    if (sinir > k->sarj_entegresi_azami_ma) {
        sinir = k->sarj_entegresi_azami_ma;
    }
    return sinir;
}
