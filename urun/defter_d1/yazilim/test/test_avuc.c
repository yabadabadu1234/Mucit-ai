#include <stdlib.h>
#include <string.h>

#include "avuc.h"
#include "test.h"

#define CIKIS_KAP 256

typedef struct {
    avuc_t a;
    avuc_cikis_t gunluk[8192];
    size_t sayi;
} deney_t;

static const avuc_ayar_t AYAR_GERCEK = {52, 98, 80, 30};

static void deney_baslat(deney_t *d)
{
    KONTROL(avuc_baslat(&d->a, &AYAR_GERCEK) == HATA_YOK);
    d->sayi = 0;
}

static size_t kare(deney_t *d, uint32_t t, const dokunus_t *n, uint8_t adet)
{
    avuc_cikis_t gecici[CIKIS_KAP];
    size_t k = avuc_isle(&d->a, n, adet, 1, t, gecici, CIKIS_KAP);
    size_t i;
    for (i = 0; i < k; i++) {
        d->gunluk[d->sayi++] = gecici[i];
    }
    return k;
}

static size_t sadece_zaman(deney_t *d, uint32_t t)
{
    avuc_cikis_t gecici[CIKIS_KAP];
    size_t k = avuc_isle(&d->a, NULL, 0, 0, t, gecici, CIKIS_KAP);
    size_t i;
    for (i = 0; i < k; i++) {
        d->gunluk[d->sayi++] = gecici[i];
    }
    return k;
}

static size_t say(const deney_t *d, uint8_t iz, sinif_t s, int bitti)
{
    size_t i;
    size_t n = 0;
    for (i = 0; i < d->sayi; i++) {
        if (d->gunluk[i].iz_no == iz && d->gunluk[i].sinif == s && d->gunluk[i].bitti == bitti) {
            n++;
        }
    }
    return n;
}

static size_t say_iz(const deney_t *d, uint8_t iz)
{
    size_t i;
    size_t n = 0;
    for (i = 0; i < d->sayi; i++) {
        if (d->gunluk[i].iz_no == iz) {
            n++;
        }
    }
    return n;
}

static dokunus_t nk(uint8_t iz, uint16_t x, uint16_t y, uint16_t boyut)
{
    dokunus_t n;
    n.iz_no = iz;
    n.x = x;
    n.y = y;
    n.boyut = boyut;
    return n;
}

static uint32_t lcg_durum = 12345;
static uint32_t lcg(void)
{
    lcg_durum = lcg_durum * 1664525u + 1013904223u;
    return lcg_durum >> 8;
}

static void kalibrasyon_testi(void)
{
    avuc_ayar_t ayar;
    const uint16_t kalem[] = {20, 24, 28, 30};
    const uint16_t avuc[] = {120, 140, 200};
    const uint16_t kalem_cakisan[] = {20, 130};
    memset(&ayar, 0, sizeof ayar);
    KONTROL(avuc_kalibre_et(&ayar, kalem, 4, avuc, 3, 80, 30) == HATA_YOK);
    KONTROL(ayar.kalem_azami_boyut == 52);
    KONTROL(ayar.avuc_asgari_boyut == 98);
    KONTROL(ayar.kalem_azami_boyut < ayar.avuc_asgari_boyut);
    KONTROL(avuc_kalibre_et(&ayar, kalem_cakisan, 2, avuc, 3, 80, 30) == HATA_PARAMETRE);
    KONTROL(avuc_kalibre_et(&ayar, kalem, 0, avuc, 3, 80, 30) == HATA_PARAMETRE);
    KONTROL(avuc_kalibre_et(&ayar, NULL, 4, avuc, 3, 80, 30) == HATA_PARAMETRE);
    KONTROL(avuc_ayar_dogrula(&AYAR_GERCEK) == HATA_YOK);
    {
        avuc_ayar_t kotu = {100, 90, 80, 30};
        avuc_t a;
        KONTROL(avuc_ayar_dogrula(&kotu) == HATA_PARAMETRE);
        KONTROL(avuc_baslat(&a, &kotu) == HATA_PARAMETRE);
    }
}

static void yalniz_kalem_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    uint32_t t;
    size_t ilk_yayin_zamani = 0;
    size_t toplam_once_30 = 0;
    int i;
    deney_baslat(d);
    for (i = 0; i < 20; i++) {
        dokunus_t n = nk(1, (uint16_t)(100 + i * 5), 200, 25);
        t = (uint32_t)(i * 10);
        size_t k = kare(d, t, &n, 1);
        if (t < 30) {
            toplam_once_30 += k;
        }
        if (k > 0 && ilk_yayin_zamani == 0) {
            ilk_yayin_zamani = t == 0 ? 1 : t;
        }
    }
    KONTROL(toplam_once_30 == 0);
    KONTROL(ilk_yayin_zamani == 30);
    KONTROL(say(d, 1, SINIF_KALEM, 0) == 20);
    {
        size_t i2;
        size_t ilk = 0;
        int sirali = 1;
        uint16_t onceki = 0;
        for (i2 = 0; i2 < d->sayi; i2++) {
            if (d->gunluk[i2].iz_no == 1 && !d->gunluk[i2].bitti) {
                if (ilk > 0 && d->gunluk[i2].x <= onceki) {
                    sirali = 0;
                }
                onceki = d->gunluk[i2].x;
                ilk++;
            }
        }
        KONTROL(sirali);
        KONTROL(d->gunluk[0].x == 100 && d->gunluk[0].zaman_ms == 0);
    }
    KONTROL(kare(d, 200, NULL, 0) == 1);
    KONTROL(say(d, 1, SINIF_KALEM, 1) == 1);
    KONTROL(avuc_sinifi(&d->a, 1) == SINIF_BELIRSIZ);
    free(d);
}

static void yalniz_avuc_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    int i;
    deney_baslat(d);
    for (i = 0; i < 20; i++) {
        dokunus_t n = nk(0, 300, 300, 180);
        kare(d, (uint32_t)(i * 10), &n, 1);
    }
    KONTROL(d->sayi == 0);
    KONTROL(avuc_sinifi(&d->a, 0) == SINIF_AVUC);
    kare(d, 200, NULL, 0);
    KONTROL(d->sayi == 0);
    free(d);
}

static void buyuyen_avuc_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    dokunus_t a = nk(0, 300, 300, 40);
    dokunus_t b = nk(0, 300, 300, 70);
    dokunus_t c = nk(0, 300, 300, 130);
    int i;
    deney_baslat(d);
    kare(d, 0, &a, 1);
    kare(d, 10, &b, 1);
    kare(d, 20, &c, 1);
    for (i = 3; i < 15; i++) {
        kare(d, (uint32_t)(i * 10), &c, 1);
    }
    KONTROL(d->sayi == 0);
    KONTROL(avuc_sinifi(&d->a, 0) == SINIF_AVUC);
    free(d);
}

static void avuc_yatik_kalem_yazar_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    int i;
    deney_baslat(d);
    for (i = 0; i < 25; i++) {
        dokunus_t n[2];
        n[0] = nk(0, 400, 300, 180);
        n[1] = nk(1, (uint16_t)(100 + i * 4), 100, 22);
        kare(d, (uint32_t)(100 + i * 10), n, 2);
    }
    KONTROL(say_iz(d, 0) == 0);
    KONTROL(say(d, 1, SINIF_KALEM, 0) == 25);
    free(d);
}

static void kalem_yazarken_avuc_konar_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    int i;
    deney_baslat(d);
    for (i = 0; i < 30; i++) {
        dokunus_t n[2];
        uint8_t adet = 1;
        n[0] = nk(1, (uint16_t)(100 + i * 3), 100, 24);
        if (i >= 10) {
            n[1] = nk(2, 150, 150, 160);
            adet = 2;
        }
        kare(d, (uint32_t)(i * 10), n, adet);
    }
    KONTROL(say(d, 1, SINIF_KALEM, 0) == 30);
    KONTROL(say_iz(d, 2) == 0);
    free(d);
}

static void yumruk_golgesi_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    int i;
    deney_baslat(d);
    for (i = 0; i < 12; i++) {
        dokunus_t n[3];
        n[0] = nk(0, 400, 300, 180);
        n[1] = nk(1, 430, 310, 20);
        n[2] = nk(2, (uint16_t)(700 - i * 3), 100, 22);
        kare(d, (uint32_t)(i * 10), n, 3);
    }
    KONTROL(say_iz(d, 0) == 0);
    KONTROL(say_iz(d, 1) == 0);
    KONTROL(say(d, 2, SINIF_KALEM, 0) == 12);
    free(d);
}

static void iki_kucuk_dokunus_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    int i;
    deney_baslat(d);
    for (i = 0; i < 12; i++) {
        dokunus_t n[2];
        n[0] = nk(1, 100, 100, 20);
        n[1] = nk(2, 500, 100, 26);
        kare(d, (uint32_t)(i * 10), n, 2);
    }
    KONTROL(say(d, 1, SINIF_KALEM, 0) == 12);
    KONTROL(say_iz(d, 2) == 0);
    free(d);
}

static void parmak_ve_kalem_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    int i;
    deney_baslat(d);
    for (i = 0; i < 8; i++) {
        dokunus_t n = nk(1, 200, 200, 70);
        kare(d, (uint32_t)(i * 10), &n, 1);
    }
    KONTROL(say(d, 1, SINIF_PARMAK, 0) >= 5);
    {
        size_t parmak_noktasi_once = say(d, 1, SINIF_PARMAK, 0);
        dokunus_t n[2];
        n[0] = nk(1, 200, 200, 70);
        n[1] = nk(2, 500, 300, 20);
        kare(d, 80, n, 2);
        for (i = 9; i < 14; i++) {
            kare(d, (uint32_t)(i * 10), n, 2);
        }
        KONTROL(say(d, 1, SINIF_PARMAK, 1) == 1);
        KONTROL(say(d, 1, SINIF_PARMAK, 0) >= parmak_noktasi_once);
        KONTROL(say(d, 1, SINIF_PARMAK, 0) <= parmak_noktasi_once + 4);
        KONTROL(avuc_sinifi(&d->a, 1) == SINIF_AVUC);
        KONTROL(say(d, 2, SINIF_KALEM, 0) >= 3);
    }
    free(d);
}

static void kisa_dokunus_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    dokunus_t n = nk(5, 100, 100, 25);
    deney_baslat(d);
    KONTROL(kare(d, 0, &n, 1) == 0);
    KONTROL(kare(d, 10, &n, 1) == 0);
    KONTROL(kare(d, 20, NULL, 0) == 3);
    KONTROL(say(d, 5, SINIF_KALEM, 0) == 2);
    KONTROL(say(d, 5, SINIF_KALEM, 1) == 1);
    free(d);
}

static void zaman_tek_basina_karar_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    dokunus_t n = nk(5, 100, 100, 25);
    deney_baslat(d);
    kare(d, 0, &n, 1);
    KONTROL(sadece_zaman(d, 10) == 0);
    KONTROL(sadece_zaman(d, 29) == 0);
    KONTROL(sadece_zaman(d, 31) == 1);
    KONTROL(avuc_sinifi(&d->a, 5) == SINIF_KALEM);
    free(d);
}

static void kimlik_yeniden_kullanimi_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    int i;
    deney_baslat(d);
    for (i = 0; i < 6; i++) {
        dokunus_t n = nk(1, (uint16_t)(100 + i), 100, 24);
        kare(d, (uint32_t)(i * 10), &n, 1);
    }
    kare(d, 60, NULL, 0);
    KONTROL(say(d, 1, SINIF_KALEM, 1) == 1);
    for (i = 0; i < 6; i++) {
        dokunus_t n = nk(1, (uint16_t)(300 + i), 300, 180);
        kare(d, (uint32_t)(100 + i * 10), &n, 1);
    }
    KONTROL(say(d, 1, SINIF_KALEM, 0) == 6);
    KONTROL(avuc_sinifi(&d->a, 1) == SINIF_AVUC);
    free(d);
}

static void kucuk_cikis_ve_tablo_tasmasi_testi(void)
{
    avuc_t a;
    avuc_cikis_t cikis[1];
    dokunus_t n[10];
    int i;
    size_t k;
    KONTROL(avuc_baslat(&a, &AYAR_GERCEK) == HATA_YOK);
    for (i = 0; i < 10; i++) {
        n[i] = nk((uint8_t)i, (uint16_t)(10 * i), 50, 20);
    }
    k = avuc_isle(&a, n, 10, 1, 0, cikis, 1);
    KONTROL(k <= 1);
    KONTROL(a.kayip >= 2);
    for (i = 1; i < 6; i++) {
        k = avuc_isle(&a, n, 10, 1, (uint32_t)(i * 10), cikis, 1);
        KONTROL(k <= 1);
    }
    KONTROL(a.kayip > 2);
    KONTROL(avuc_isle(NULL, n, 1, 1, 0, cikis, 1) == 0);
    KONTROL(avuc_isle(&a, NULL, 1, 1, 0, cikis, 1) == 0);
}

static int sinir_ihlali = 0;
static int ayni_anda_kalem_ihlali = 0;

static void ozellik_testi(void)
{
    deney_t *d = calloc(1, sizeof *d);
    uint8_t palm_boyutlu_goruldu[8];
    uint8_t kalemde_mi[8];
    uint8_t aktif[8];
    int kare_no;
    deney_baslat(d);
    memset(palm_boyutlu_goruldu, 0, sizeof palm_boyutlu_goruldu);
    memset(kalemde_mi, 0, sizeof kalemde_mi);
    memset(aktif, 0, sizeof aktif);
    lcg_durum = 987654321u;
    for (kare_no = 0; kare_no < 20000; kare_no++) {
        dokunus_t n[GT911_AZAMI_NOKTA];
        uint8_t adet = 0;
        uint8_t iz;
        avuc_cikis_t gecici[CIKIS_KAP];
        size_t k;
        size_t i;
        uint8_t bu_karede[8];
        int kalem_sayisi;
        memset(bu_karede, 0, sizeof bu_karede);
        for (iz = 0; iz < 5; iz++) {
            uint32_t r = lcg();
            if (aktif[iz]) {
                if (r % 40 == 0) {
                    aktif[iz] = 0;
                }
            } else if (r % 25 == 0) {
                aktif[iz] = 1;
                palm_boyutlu_goruldu[iz] = 0;
            }
            if (aktif[iz]) {
                uint32_t tur = lcg() % 10;
                uint16_t boyut;
                if (tur < 5) {
                    boyut = (uint16_t)(10 + lcg() % 31);
                } else if (tur < 7) {
                    boyut = (uint16_t)(60 + lcg() % 31);
                } else {
                    boyut = (uint16_t)(110 + lcg() % 141);
                }
                n[adet] = nk(iz, (uint16_t)(lcg() % 800), (uint16_t)(lcg() % 480), boyut);
                if (boyut >= AYAR_GERCEK.avuc_asgari_boyut) {
                    palm_boyutlu_goruldu[iz] = 1;
                }
                bu_karede[iz] = 1;
                adet++;
            }
        }
        k = avuc_isle(&d->a, n, adet, 1, (uint32_t)(kare_no * 10), gecici, CIKIS_KAP);
        for (i = 0; i < k; i++) {
            const avuc_cikis_t *c = &gecici[i];
            if (c->sinif == SINIF_AVUC) {
                sinir_ihlali++;
                continue;
            }
            if (!c->bitti && palm_boyutlu_goruldu[c->iz_no]) {
                sinir_ihlali++;
            }
            if (c->sinif == SINIF_KALEM) {
                kalemde_mi[c->iz_no] = c->bitti ? 0 : 1;
            }
            kalem_sayisi = 0;
            {
                size_t j;
                for (j = 0; j < 8; j++) {
                    kalem_sayisi += kalemde_mi[j];
                }
            }
            if (kalem_sayisi > 1) {
                ayni_anda_kalem_ihlali++;
            }
        }
    }
    KONTROL(sinir_ihlali == 0);
    KONTROL(ayni_anda_kalem_ihlali == 0);
    free(d);
}

int main(void)
{
    kalibrasyon_testi();
    yalniz_kalem_testi();
    yalniz_avuc_testi();
    buyuyen_avuc_testi();
    avuc_yatik_kalem_yazar_testi();
    kalem_yazarken_avuc_konar_testi();
    yumruk_golgesi_testi();
    iki_kucuk_dokunus_testi();
    parmak_ve_kalem_testi();
    kisa_dokunus_testi();
    zaman_tek_basina_karar_testi();
    kimlik_yeniden_kullanimi_testi();
    kucuk_cikis_ve_tablo_tasmasi_testi();
    ozellik_testi();
    SONUC("avuc");
}
