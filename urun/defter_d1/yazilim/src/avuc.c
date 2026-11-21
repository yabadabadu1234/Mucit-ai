#include <string.h>

#include "avuc.h"

int avuc_ayar_dogrula(const avuc_ayar_t *ayar)
{
    if (ayar == NULL) {
        return HATA_PARAMETRE;
    }
    if (ayar->kalem_azami_boyut == 0 || ayar->kalem_azami_boyut >= ayar->avuc_asgari_boyut) {
        return HATA_PARAMETRE;
    }
    return HATA_YOK;
}

int avuc_kalibre_et(avuc_ayar_t *ayar, const uint16_t *kalem_boyutlari, size_t kalem_adet,
                    const uint16_t *avuc_boyutlari, size_t avuc_adet,
                    uint16_t golge_yaricapi_px, uint32_t bekleme_ms)
{
    uint16_t kalem_en_buyuk = 0;
    uint16_t avuc_en_kucuk = 0xFFFF;
    uint16_t aralik;
    uint16_t pay;
    size_t i;

    if (ayar == NULL || kalem_boyutlari == NULL || avuc_boyutlari == NULL || kalem_adet == 0 || avuc_adet == 0) {
        return HATA_PARAMETRE;
    }
    for (i = 0; i < kalem_adet; i++) {
        if (kalem_boyutlari[i] > kalem_en_buyuk) {
            kalem_en_buyuk = kalem_boyutlari[i];
        }
    }
    for (i = 0; i < avuc_adet; i++) {
        if (avuc_boyutlari[i] < avuc_en_kucuk) {
            avuc_en_kucuk = avuc_boyutlari[i];
        }
    }
    if (kalem_en_buyuk == 0 || kalem_en_buyuk >= avuc_en_kucuk) {
        return HATA_PARAMETRE;
    }
    aralik = (uint16_t)(avuc_en_kucuk - kalem_en_buyuk);
    pay = (uint16_t)(aralik / 4);
    ayar->kalem_azami_boyut = (uint16_t)(kalem_en_buyuk + pay);
    ayar->avuc_asgari_boyut = (uint16_t)(avuc_en_kucuk - pay);
    ayar->golge_yaricapi_px = golge_yaricapi_px;
    ayar->bekleme_ms = bekleme_ms;
    return avuc_ayar_dogrula(ayar);
}

int avuc_baslat(avuc_t *a, const avuc_ayar_t *ayar)
{
    if (a == NULL || avuc_ayar_dogrula(ayar) != HATA_YOK) {
        return HATA_PARAMETRE;
    }
    memset(a, 0, sizeof *a);
    a->ayar = *ayar;
    return HATA_YOK;
}

sinif_t avuc_sinifi(const avuc_t *a, uint8_t iz_no)
{
    size_t i;
    for (i = 0; i < AVUC_IZ_AZAMI; i++) {
        if (a->iz[i].kullanimda && a->iz[i].iz_no == iz_no) {
            return a->iz[i].sinif;
        }
    }
    return SINIF_BELIRSIZ;
}

static avuc_iz_t *iz_bul(avuc_t *a, uint8_t iz_no)
{
    size_t i;
    for (i = 0; i < AVUC_IZ_AZAMI; i++) {
        if (a->iz[i].kullanimda && a->iz[i].iz_no == iz_no) {
            return &a->iz[i];
        }
    }
    return NULL;
}

static avuc_iz_t *iz_ayir(avuc_t *a)
{
    size_t i;
    for (i = 0; i < AVUC_IZ_AZAMI; i++) {
        if (!a->iz[i].kullanimda) {
            return &a->iz[i];
        }
    }
    return NULL;
}

static void yay(avuc_t *a, avuc_cikis_t *cikis, size_t kapasite, size_t *sayac, sinif_t sinif,
                uint8_t iz_no, uint16_t x, uint16_t y, uint32_t zaman_ms, uint8_t bitti)
{
    if (*sayac < kapasite) {
        cikis[*sayac].sinif = sinif;
        cikis[*sayac].iz_no = iz_no;
        cikis[*sayac].x = x;
        cikis[*sayac].y = y;
        cikis[*sayac].zaman_ms = zaman_ms;
        cikis[*sayac].bitti = bitti;
        (*sayac)++;
    } else {
        a->kayip++;
    }
}

static uint32_t uzaklik_kare(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2)
{
    int32_t dx = (int32_t)x1 - (int32_t)x2;
    int32_t dy = (int32_t)y1 - (int32_t)y2;
    return (uint32_t)(dx * dx + dy * dy);
}

static int golgede_mi(const avuc_t *a, const avuc_iz_t *t)
{
    uint32_t r2;
    size_t i;
    if (a->ayar.golge_yaricapi_px == 0) {
        return 0;
    }
    r2 = (uint32_t)a->ayar.golge_yaricapi_px * (uint32_t)a->ayar.golge_yaricapi_px;
    for (i = 0; i < AVUC_IZ_AZAMI; i++) {
        const avuc_iz_t *u = &a->iz[i];
        if (u == t || !u->kullanimda || u->sinif != SINIF_AVUC || !u->goruldu) {
            continue;
        }
        if (uzaklik_kare(t->ilk_x, t->ilk_y, u->x, u->y) <= r2) {
            return 1;
        }
    }
    return 0;
}

static int etkin_kalem_var(const avuc_t *a, const avuc_iz_t *t)
{
    size_t i;
    for (i = 0; i < AVUC_IZ_AZAMI; i++) {
        const avuc_iz_t *u = &a->iz[i];
        if (u != t && u->kullanimda && u->goruldu && u->sinif == SINIF_KALEM) {
            return 1;
        }
    }
    return 0;
}

static void avuca_cevir(avuc_t *a, avuc_iz_t *t, avuc_cikis_t *cikis, size_t kapasite, size_t *sayac, uint32_t simdi)
{
    if ((t->sinif == SINIF_KALEM || t->sinif == SINIF_PARMAK) && t->yayin_basladi) {
        yay(a, cikis, kapasite, sayac, t->sinif, t->iz_no, t->x, t->y, simdi, 1);
    }
    t->sinif = SINIF_AVUC;
    t->bekleyen_sayisi = 0;
}

static void karar_ver(avuc_t *a, avuc_iz_t *t, avuc_cikis_t *cikis, size_t kapasite, size_t *sayac, uint32_t simdi)
{
    sinif_t sonuc;
    size_t i;

    if (t->en_buyuk_boyut >= a->ayar.avuc_asgari_boyut) {
        sonuc = SINIF_AVUC;
    } else if (golgede_mi(a, t)) {
        sonuc = SINIF_AVUC;
    } else if (etkin_kalem_var(a, t)) {
        sonuc = SINIF_AVUC;
    } else if (t->en_buyuk_boyut <= a->ayar.kalem_azami_boyut) {
        sonuc = SINIF_KALEM;
    } else {
        sonuc = SINIF_PARMAK;
    }

    if (sonuc == SINIF_AVUC) {
        t->sinif = SINIF_AVUC;
        t->bekleyen_sayisi = 0;
        return;
    }

    if (sonuc == SINIF_KALEM) {
        for (i = 0; i < AVUC_IZ_AZAMI; i++) {
            avuc_iz_t *u = &a->iz[i];
            if (u != t && u->kullanimda && u->sinif == SINIF_PARMAK) {
                avuca_cevir(a, u, cikis, kapasite, sayac, simdi);
            }
        }
    }

    t->sinif = sonuc;
    t->yayin_basladi = 1;
    for (i = 0; i < t->bekleyen_sayisi; i++) {
        yay(a, cikis, kapasite, sayac, sonuc, t->iz_no, t->bekleyen[i].x, t->bekleyen[i].y,
            t->bekleyen[i].zaman_ms, 0);
    }
    t->bekleyen_sayisi = 0;
}

static void karar_turu(avuc_t *a, uint32_t simdi, int serbest_birakilanlar, avuc_cikis_t *cikis,
                       size_t kapasite, size_t *sayac)
{
    for (;;) {
        avuc_iz_t *secilen = NULL;
        size_t i;
        for (i = 0; i < AVUC_IZ_AZAMI; i++) {
            avuc_iz_t *t = &a->iz[i];
            int hazir;
            if (!t->kullanimda || t->sinif != SINIF_BELIRSIZ) {
                continue;
            }
            if (serbest_birakilanlar) {
                hazir = !t->goruldu;
            } else {
                hazir = t->goruldu && (uint32_t)(simdi - t->baslangic_ms) >= a->ayar.bekleme_ms;
            }
            if (!hazir) {
                continue;
            }
            if (secilen == NULL || t->en_buyuk_boyut < secilen->en_buyuk_boyut) {
                secilen = t;
            }
        }
        if (secilen == NULL) {
            break;
        }
        karar_ver(a, secilen, cikis, kapasite, sayac, simdi);
    }
}

size_t avuc_isle(avuc_t *a, const dokunus_t *nokta, uint8_t adet, int yeni_kare, uint32_t simdi_ms,
                 avuc_cikis_t *cikis, size_t kapasite)
{
    size_t sayac = 0;
    size_t i;
    uint8_t k;

    if (a == NULL || cikis == NULL || (adet > 0 && nokta == NULL)) {
        return 0;
    }

    if (yeni_kare) {
        for (i = 0; i < AVUC_IZ_AZAMI; i++) {
            a->iz[i].goruldu = 0;
        }
        for (k = 0; k < adet; k++) {
            avuc_iz_t *t = iz_bul(a, nokta[k].iz_no);
            if (t == NULL) {
                t = iz_ayir(a);
                if (t == NULL) {
                    a->kayip++;
                    continue;
                }
                memset(t, 0, sizeof *t);
                t->kullanimda = 1;
                t->iz_no = nokta[k].iz_no;
                t->sinif = SINIF_BELIRSIZ;
                t->ilk_x = nokta[k].x;
                t->ilk_y = nokta[k].y;
                t->baslangic_ms = simdi_ms;
            }
            t->goruldu = 1;
            t->x = nokta[k].x;
            t->y = nokta[k].y;
            if (nokta[k].boyut > t->en_buyuk_boyut) {
                t->en_buyuk_boyut = nokta[k].boyut;
            }
            if (t->sinif != SINIF_AVUC && t->en_buyuk_boyut >= a->ayar.avuc_asgari_boyut) {
                avuca_cevir(a, t, cikis, kapasite, &sayac, simdi_ms);
                continue;
            }
            if (t->sinif == SINIF_BELIRSIZ) {
                if (t->bekleyen_sayisi == AVUC_BEKLEYEN_AZAMI) {
                    memmove(&t->bekleyen[0], &t->bekleyen[1],
                            (AVUC_BEKLEYEN_AZAMI - 1) * sizeof t->bekleyen[0]);
                    t->bekleyen_sayisi--;
                    a->kayip++;
                }
                t->bekleyen[t->bekleyen_sayisi].x = nokta[k].x;
                t->bekleyen[t->bekleyen_sayisi].y = nokta[k].y;
                t->bekleyen[t->bekleyen_sayisi].zaman_ms = simdi_ms;
                t->bekleyen_sayisi++;
            } else if (t->sinif == SINIF_KALEM || t->sinif == SINIF_PARMAK) {
                yay(a, cikis, kapasite, &sayac, t->sinif, t->iz_no, nokta[k].x, nokta[k].y, simdi_ms, 0);
            }
        }
        for (i = 0; i < AVUC_IZ_AZAMI; i++) {
            avuc_iz_t *t = &a->iz[i];
            if (t->kullanimda && !t->goruldu && t->sinif != SINIF_BELIRSIZ) {
                if ((t->sinif == SINIF_KALEM || t->sinif == SINIF_PARMAK) && t->yayin_basladi) {
                    yay(a, cikis, kapasite, &sayac, t->sinif, t->iz_no, t->x, t->y, simdi_ms, 1);
                }
                t->kullanimda = 0;
            }
        }
        karar_turu(a, simdi_ms, 1, cikis, kapasite, &sayac);
        for (i = 0; i < AVUC_IZ_AZAMI; i++) {
            avuc_iz_t *t = &a->iz[i];
            if (t->kullanimda && !t->goruldu) {
                if ((t->sinif == SINIF_KALEM || t->sinif == SINIF_PARMAK) && t->yayin_basladi) {
                    yay(a, cikis, kapasite, &sayac, t->sinif, t->iz_no, t->x, t->y, simdi_ms, 1);
                }
                t->kullanimda = 0;
            }
        }
    }
    karar_turu(a, simdi_ms, 0, cikis, kapasite, &sayac);
    return sayac;
}
