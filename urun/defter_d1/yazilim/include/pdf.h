#ifndef PDF_H
#define PDF_H

#include "sayfa.h"

#define PDF_SAYFA_AZAMI 32

typedef struct {
    int (*yaz)(void *baglam, const uint8_t *veri, size_t uzunluk);
    void *baglam;
} pdf_cikti_t;

typedef struct {
    const sayfa_t *sayfa;
    const uint8_t *jpeg;
    size_t jpeg_uzunluk;
} pdf_sayfa_t;

typedef struct {
    uint32_t olcek_binde_pt;
    uint32_t cizgi_yuzde_pt;
} pdf_ayar_t;

typedef struct {
    uint16_t genislik;
    uint16_t yukseklik;
    uint8_t bilesen;
} jpeg_bilgi_t;

int jpeg_bilgi_oku(const uint8_t *jpeg, size_t uzunluk, jpeg_bilgi_t *bilgi);
int pdf_yaz(const pdf_cikti_t *cikti, const pdf_sayfa_t *sayfalar, size_t sayfa_adedi, const pdf_ayar_t *ayar);

#endif
