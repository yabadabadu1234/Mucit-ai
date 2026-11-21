#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "pdf.h"
#include "test.h"

typedef struct {
    uint8_t *veri;
    size_t uzunluk;
    size_t kapasite;
    size_t basarisiz_esik;
} tampon_t;

static int tampona_yaz(void *b, const uint8_t *veri, size_t n)
{
    tampon_t *t = (tampon_t *)b;
    if (t->basarisiz_esik != 0 && t->uzunluk + n > t->basarisiz_esik) {
        return -1;
    }
    if (t->uzunluk + n > t->kapasite) {
        size_t yeni = (t->kapasite == 0 ? 4096 : t->kapasite) * 2;
        while (yeni < t->uzunluk + n) {
            yeni *= 2;
        }
        t->veri = realloc(t->veri, yeni);
        t->kapasite = yeni;
    }
    memcpy(t->veri + t->uzunluk, veri, n);
    t->uzunluk += n;
    return 0;
}

static uint32_t lcg_durum = 4242;
static uint32_t lcg(void)
{
    lcg_durum = lcg_durum * 1664525u + 1013904223u;
    return lcg_durum >> 8;
}

static uint8_t *dosya_oku(const char *yol, size_t *uzunluk)
{
    FILE *f = fopen(yol, "rb");
    uint8_t *veri;
    long boyut;
    if (f == NULL) {
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    boyut = ftell(f);
    fseek(f, 0, SEEK_SET);
    veri = malloc((size_t)boyut);
    if (fread(veri, 1, (size_t)boyut, f) != (size_t)boyut) {
        free(veri);
        fclose(f);
        return NULL;
    }
    fclose(f);
    *uzunluk = (size_t)boyut;
    return veri;
}

static void sayfa_testi(void)
{
    sayfa_t *s = calloc(1, sizeof *s);
    uint32_t i;
    KONTROL(sayfa_baslat(s, 800, 480) == HATA_YOK);
    KONTROL(sayfa_baslat(s, 0, 480) == HATA_PARAMETRE);
    KONTROL(sayfa_nokta_ekle(s, 1, 1) == HATA_PARAMETRE);
    KONTROL(sayfa_strok_ac(s) == HATA_YOK);
    KONTROL(sayfa_nokta_ekle(s, 800, 1) == HATA_PARAMETRE);
    KONTROL(sayfa_nokta_ekle(s, 1, 480) == HATA_PARAMETRE);
    KONTROL(sayfa_nokta_ekle(s, 799, 479) == HATA_YOK);
    KONTROL(sayfa_strok_nokta_sayisi(s, 0) == 1);
    KONTROL(sayfa_strok_ac(s) == HATA_YOK);
    KONTROL(sayfa_nokta_ekle(s, 5, 5) == HATA_YOK);
    KONTROL(sayfa_nokta_ekle(s, 6, 6) == HATA_YOK);
    KONTROL(sayfa_strok_nokta_sayisi(s, 0) == 1);
    KONTROL(sayfa_strok_nokta_sayisi(s, 1) == 2);
    KONTROL(sayfa_strok_nokta_sayisi(s, 2) == 0);

    KONTROL(sayfa_baslat(s, 800, 480) == HATA_YOK);
    for (i = 0; i < SAYFA_STROK_AZAMI; i++) {
        KONTROL(sayfa_strok_ac(s) == HATA_YOK);
    }
    KONTROL(sayfa_strok_ac(s) == HATA_YER_YOK);

    KONTROL(sayfa_baslat(s, 800, 480) == HATA_YOK);
    KONTROL(sayfa_strok_ac(s) == HATA_YOK);
    for (i = 0; i < SAYFA_NOKTA_AZAMI; i++) {
        KONTROL(sayfa_nokta_ekle(s, (uint16_t)(i % 800), (uint16_t)(i % 480)) == HATA_YOK);
        if (test_basarisiz > 5) {
            break;
        }
    }
    KONTROL(sayfa_nokta_ekle(s, 1, 1) == HATA_YER_YOK);
    free(s);
}

static void doldur(sayfa_t *s, uint32_t strok_adedi)
{
    uint32_t i;
    uint32_t j;
    sayfa_baslat(s, 800, 480);
    for (i = 0; i < strok_adedi; i++) {
        uint32_t adet = 1 + lcg() % 60;
        uint32_t x = lcg() % 800;
        uint32_t y = lcg() % 480;
        sayfa_strok_ac(s);
        for (j = 0; j < adet; j++) {
            int dx = (int)(lcg() % 41) - 20;
            int dy = (int)(lcg() % 41) - 20;
            int nx = (int)x + dx;
            int ny = (int)y + dy;
            if (nx < 0) nx = 0;
            if (nx > 799) nx = 799;
            if (ny < 0) ny = 0;
            if (ny > 479) ny = 479;
            x = (uint32_t)nx;
            y = (uint32_t)ny;
            sayfa_nokta_ekle(s, (uint16_t)x, (uint16_t)y);
        }
    }
}

static void serilestirme_testi(void)
{
    sayfa_t *s = calloc(1, sizeof *s);
    sayfa_t *r = calloc(1, sizeof *r);
    static uint8_t tampon[200000];
    size_t yazilan = 0;
    size_t i;
    int hepsi_reddedildi = 1;
    int kesilmis_hepsi_reddedildi = 1;

    doldur(s, 40);
    KONTROL(sayfa_serilestir(s, tampon, sizeof tampon, &yazilan) == HATA_YOK);
    KONTROL(sayfa_cozumle(r, tampon, yazilan) == HATA_YOK);
    KONTROL(r->genislik == s->genislik && r->yukseklik == s->yukseklik);
    KONTROL(r->strok_sayisi == s->strok_sayisi && r->nokta_sayisi == s->nokta_sayisi);
    KONTROL(memcmp(r->nokta, s->nokta, s->nokta_sayisi * sizeof(sayfa_nokta_t)) == 0);
    KONTROL(memcmp(r->strok_baslangic, s->strok_baslangic, (s->strok_sayisi + 1) * sizeof(uint32_t)) == 0);

    for (i = 0; i < yazilan; i++) {
        uint8_t eski = tampon[i];
        tampon[i] = (uint8_t)(eski ^ 0x10);
        if (sayfa_cozumle(r, tampon, yazilan) == HATA_YOK) {
            hepsi_reddedildi = 0;
        }
        tampon[i] = eski;
    }
    KONTROL(hepsi_reddedildi);
    for (i = 0; i < yazilan; i++) {
        if (sayfa_cozumle(r, tampon, i) == HATA_YOK) {
            kesilmis_hepsi_reddedildi = 0;
        }
    }
    KONTROL(kesilmis_hepsi_reddedildi);
    KONTROL(sayfa_serilestir(s, tampon, 20, &yazilan) == HATA_YER_YOK);
    KONTROL(sayfa_serilestir(s, tampon, 0, &yazilan) == HATA_PARAMETRE);

    sayfa_baslat(s, 800, 480);
    KONTROL(sayfa_serilestir(s, tampon, sizeof tampon, &yazilan) == HATA_YOK);
    KONTROL(sayfa_cozumle(r, tampon, yazilan) == HATA_YOK && r->strok_sayisi == 0);
    free(s);
    free(r);
}

static void jpeg_testi(const uint8_t *jpeg, size_t n)
{
    jpeg_bilgi_t b;
    uint8_t bozuk[16] = {0xFF, 0xD8, 0xFF, 0xDA, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    KONTROL(jpeg_bilgi_oku(jpeg, n, &b) == HATA_YOK);
    KONTROL(b.genislik == 64 && b.yukseklik == 48 && (b.bilesen == 3 || b.bilesen == 1));
    KONTROL(jpeg_bilgi_oku(jpeg, 3, &b) == HATA_BOZUK_VERI);
    KONTROL(jpeg_bilgi_oku(bozuk, sizeof bozuk, &b) == HATA_BOZUK_VERI);
    KONTROL(jpeg_bilgi_oku(NULL, 10, &b) == HATA_BOZUK_VERI);
    KONTROL(jpeg_bilgi_oku(jpeg, n / 4, &b) == HATA_BOZUK_VERI);
}

static void pdf_testi(const uint8_t *jpeg, size_t jpeg_n, const char *cikti_yolu)
{
    sayfa_t *s1 = calloc(1, sizeof *s1);
    sayfa_t *s2 = calloc(1, sizeof *s2);
    tampon_t t;
    pdf_cikti_t c;
    pdf_sayfa_t sayfalar[2];
    pdf_ayar_t ayar = {546, 120};
    FILE *f;

    memset(&t, 0, sizeof t);
    c.yaz = tampona_yaz;
    c.baglam = &t;

    sayfa_baslat(s1, 800, 480);
    sayfa_strok_ac(s1);
    sayfa_nokta_ekle(s1, 100, 80);
    sayfa_nokta_ekle(s1, 200, 90);
    sayfa_nokta_ekle(s1, 300, 400);
    sayfa_strok_ac(s1);
    sayfa_nokta_ekle(s1, 50, 50);
    sayfa_strok_ac(s1);
    sayfa_nokta_ekle(s1, 700, 10);
    sayfa_nokta_ekle(s1, 710, 20);

    doldur(s2, 25);

    sayfalar[0].sayfa = s1;
    sayfalar[0].jpeg = NULL;
    sayfalar[0].jpeg_uzunluk = 0;
    sayfalar[1].sayfa = s2;
    sayfalar[1].jpeg = jpeg;
    sayfalar[1].jpeg_uzunluk = jpeg_n;

    KONTROL(pdf_yaz(&c, sayfalar, 2, &ayar) == HATA_YOK);
    KONTROL(t.uzunluk > 500);
    KONTROL(memcmp(t.veri, "%PDF-1.4", 8) == 0);
    KONTROL(memcmp(t.veri + t.uzunluk - 6, "%%EOF\n", 6) == 0);

    f = fopen(cikti_yolu, "wb");
    KONTROL(f != NULL);
    if (f != NULL) {
        fwrite(t.veri, 1, t.uzunluk, f);
        fclose(f);
    }

    {
        tampon_t kisa;
        pdf_cikti_t kc;
        memset(&kisa, 0, sizeof kisa);
        kisa.basarisiz_esik = 300;
        kc.yaz = tampona_yaz;
        kc.baglam = &kisa;
        KONTROL(pdf_yaz(&kc, sayfalar, 2, &ayar) == HATA_GIRIS_CIKIS);
        free(kisa.veri);
    }
    KONTROL(pdf_yaz(&c, sayfalar, 0, &ayar) == HATA_PARAMETRE);
    KONTROL(pdf_yaz(&c, NULL, 2, &ayar) == HATA_PARAMETRE);
    {
        pdf_ayar_t sifir = {0, 120};
        KONTROL(pdf_yaz(&c, sayfalar, 2, &sifir) == HATA_PARAMETRE);
    }
    {
        pdf_sayfa_t kotu[1];
        uint8_t kotu_jpeg[8] = {1, 2, 3, 4, 5, 6, 7, 8};
        kotu[0].sayfa = s1;
        kotu[0].jpeg = kotu_jpeg;
        kotu[0].jpeg_uzunluk = sizeof kotu_jpeg;
        KONTROL(pdf_yaz(&c, kotu, 1, &ayar) == HATA_BOZUK_VERI);
    }
    free(t.veri);
    free(s1);
    free(s2);
}

int main(int argc, char **argv)
{
    uint8_t *jpeg;
    size_t jpeg_n = 0;
    if (argc < 3) {
        printf("kullanim: test_sayfa_pdf <jpeg> <cikti.pdf>\n");
        return 2;
    }
    jpeg = dosya_oku(argv[1], &jpeg_n);
    if (jpeg == NULL) {
        printf("jpeg okunamadi: %s\n", argv[1]);
        return 2;
    }
    sayfa_testi();
    serilestirme_testi();
    jpeg_testi(jpeg, jpeg_n);
    pdf_testi(jpeg, jpeg_n, argv[2]);
    free(jpeg);
    SONUC("sayfa_pdf");
}
