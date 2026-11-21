#include <stdio.h>
#include <string.h>

#include "pdf.h"

typedef struct {
    const pdf_cikti_t *cikti;
    uint64_t konum;
    int sayim_modu;
    int hata;
} yazici_t;

static void ham_yaz(yazici_t *y, const void *veri, size_t n)
{
    if (!y->sayim_modu && !y->hata) {
        if (y->cikti->yaz(y->cikti->baglam, (const uint8_t *)veri, n) != 0) {
            y->hata = 1;
        }
    }
    y->konum += n;
}

static void metin_yaz(yazici_t *y, const char *metin)
{
    ham_yaz(y, metin, strlen(metin));
}

static void sayi_yaz(yazici_t *y, uint32_t yuzlu)
{
    char tampon[24];
    int n = snprintf(tampon, sizeof tampon, "%lu.%02lu", (unsigned long)(yuzlu / 100u), (unsigned long)(yuzlu % 100u));
    ham_yaz(y, tampon, (size_t)n);
}

static void tam_sayi_yaz(yazici_t *y, uint32_t v)
{
    char tampon[16];
    int n = snprintf(tampon, sizeof tampon, "%lu", (unsigned long)v);
    ham_yaz(y, tampon, (size_t)n);
}

static uint32_t piksel_yuzlu(uint32_t piksel, uint32_t olcek_binde)
{
    return (uint32_t)(((uint64_t)piksel * olcek_binde) / 10u);
}

int jpeg_bilgi_oku(const uint8_t *jpeg, size_t uzunluk, jpeg_bilgi_t *bilgi)
{
    size_t i = 2;
    if (jpeg == NULL || bilgi == NULL || uzunluk < 4 || jpeg[0] != 0xFF || jpeg[1] != 0xD8) {
        return HATA_BOZUK_VERI;
    }
    while (i + 4 <= uzunluk) {
        uint8_t isaret;
        size_t parca;
        if (jpeg[i] != 0xFF) {
            return HATA_BOZUK_VERI;
        }
        while (i < uzunluk && jpeg[i] == 0xFF) {
            i++;
        }
        if (i >= uzunluk) {
            return HATA_BOZUK_VERI;
        }
        isaret = jpeg[i++];
        if (isaret == 0xD9 || isaret == 0xDA) {
            return HATA_BOZUK_VERI;
        }
        if (i + 2 > uzunluk) {
            return HATA_BOZUK_VERI;
        }
        parca = (size_t)((jpeg[i] << 8) | jpeg[i + 1]);
        if (parca < 2 || i + parca > uzunluk) {
            return HATA_BOZUK_VERI;
        }
        if (isaret >= 0xC0 && isaret <= 0xCF && isaret != 0xC4 && isaret != 0xC8 && isaret != 0xCC) {
            if (parca < 8) {
                return HATA_BOZUK_VERI;
            }
            bilgi->yukseklik = (uint16_t)((jpeg[i + 3] << 8) | jpeg[i + 4]);
            bilgi->genislik = (uint16_t)((jpeg[i + 5] << 8) | jpeg[i + 6]);
            bilgi->bilesen = jpeg[i + 7];
            if (bilgi->genislik == 0 || bilgi->yukseklik == 0 || (bilgi->bilesen != 1 && bilgi->bilesen != 3)) {
                return HATA_BOZUK_VERI;
            }
            return HATA_YOK;
        }
        i += parca;
    }
    return HATA_BOZUK_VERI;
}

static void icerik_yaz(yazici_t *y, const pdf_sayfa_t *p, const pdf_ayar_t *a, int resim_var)
{
    const sayfa_t *s = p->sayfa;
    uint32_t i;
    uint32_t j;
    if (resim_var) {
        metin_yaz(y, "q ");
        sayi_yaz(y, piksel_yuzlu(s->genislik, a->olcek_binde_pt));
        metin_yaz(y, " 0 0 ");
        sayi_yaz(y, piksel_yuzlu(s->yukseklik, a->olcek_binde_pt));
        metin_yaz(y, " 0 0 cm /Im0 Do Q\n");
    }
    metin_yaz(y, "0 0 0 RG ");
    sayi_yaz(y, a->cizgi_yuzde_pt);
    metin_yaz(y, " w 1 J 1 j\n");
    for (i = 0; i < s->strok_sayisi; i++) {
        uint32_t ilk = s->strok_baslangic[i];
        uint32_t adet = s->strok_baslangic[i + 1] - ilk;
        if (adet == 0) {
            continue;
        }
        for (j = 0; j < adet; j++) {
            const sayfa_nokta_t *n = &s->nokta[ilk + j];
            sayi_yaz(y, piksel_yuzlu(n->x, a->olcek_binde_pt));
            metin_yaz(y, " ");
            sayi_yaz(y, piksel_yuzlu((uint32_t)s->yukseklik - n->y, a->olcek_binde_pt));
            metin_yaz(y, j == 0 ? " m\n" : " l\n");
        }
        if (adet == 1) {
            const sayfa_nokta_t *n = &s->nokta[ilk];
            sayi_yaz(y, piksel_yuzlu(n->x, a->olcek_binde_pt));
            metin_yaz(y, " ");
            sayi_yaz(y, piksel_yuzlu((uint32_t)s->yukseklik - n->y, a->olcek_binde_pt));
            metin_yaz(y, " l\n");
        }
        metin_yaz(y, "S\n");
    }
}

static void nesne_basla(yazici_t *y, uint64_t *ofsetler, uint32_t no)
{
    ofsetler[no] = y->konum;
    tam_sayi_yaz(y, no);
    metin_yaz(y, " 0 obj\n");
}

int pdf_yaz(const pdf_cikti_t *cikti, const pdf_sayfa_t *sayfalar, size_t sayfa_adedi, const pdf_ayar_t *ayar)
{
    yazici_t y;
    uint32_t sayfa_no[PDF_SAYFA_AZAMI];
    uint32_t icerik_no[PDF_SAYFA_AZAMI];
    uint32_t resim_no[PDF_SAYFA_AZAMI];
    jpeg_bilgi_t jpeg[PDF_SAYFA_AZAMI];
    uint64_t ofsetler[3 + 3 * PDF_SAYFA_AZAMI];
    uint32_t sonraki = 3;
    uint32_t toplam_nesne;
    uint64_t xref_konum;
    size_t i;
    uint32_t no;

    if (cikti == NULL || cikti->yaz == NULL || sayfalar == NULL || ayar == NULL || sayfa_adedi == 0 ||
        sayfa_adedi > PDF_SAYFA_AZAMI || ayar->olcek_binde_pt == 0) {
        return HATA_PARAMETRE;
    }
    for (i = 0; i < sayfa_adedi; i++) {
        if (sayfalar[i].sayfa == NULL || sayfalar[i].sayfa->genislik == 0) {
            return HATA_PARAMETRE;
        }
        resim_no[i] = 0;
        if (sayfalar[i].jpeg != NULL) {
            if (jpeg_bilgi_oku(sayfalar[i].jpeg, sayfalar[i].jpeg_uzunluk, &jpeg[i]) != HATA_YOK) {
                return HATA_BOZUK_VERI;
            }
        }
        sayfa_no[i] = sonraki++;
        icerik_no[i] = sonraki++;
        if (sayfalar[i].jpeg != NULL) {
            resim_no[i] = sonraki++;
        }
    }
    toplam_nesne = sonraki;
    memset(ofsetler, 0, sizeof ofsetler);

    y.cikti = cikti;
    y.konum = 0;
    y.sayim_modu = 0;
    y.hata = 0;

    metin_yaz(&y, "%PDF-1.4\n");
    ham_yaz(&y, "%\xE2\xE3\xCF\xD3\n", 6);

    nesne_basla(&y, ofsetler, 1);
    metin_yaz(&y, "<< /Type /Catalog /Pages 2 0 R >>\nendobj\n");

    nesne_basla(&y, ofsetler, 2);
    metin_yaz(&y, "<< /Type /Pages /Kids [");
    for (i = 0; i < sayfa_adedi; i++) {
        tam_sayi_yaz(&y, sayfa_no[i]);
        metin_yaz(&y, " 0 R ");
    }
    metin_yaz(&y, "] /Count ");
    tam_sayi_yaz(&y, (uint32_t)sayfa_adedi);
    metin_yaz(&y, " >>\nendobj\n");

    for (i = 0; i < sayfa_adedi; i++) {
        const sayfa_t *s = sayfalar[i].sayfa;
        yazici_t sayac;
        sayac.cikti = cikti;
        sayac.konum = 0;
        sayac.sayim_modu = 1;
        sayac.hata = 0;
        icerik_yaz(&sayac, &sayfalar[i], ayar, resim_no[i] != 0);

        nesne_basla(&y, ofsetler, sayfa_no[i]);
        metin_yaz(&y, "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ");
        sayi_yaz(&y, piksel_yuzlu(s->genislik, ayar->olcek_binde_pt));
        metin_yaz(&y, " ");
        sayi_yaz(&y, piksel_yuzlu(s->yukseklik, ayar->olcek_binde_pt));
        metin_yaz(&y, "] /Contents ");
        tam_sayi_yaz(&y, icerik_no[i]);
        metin_yaz(&y, " 0 R /Resources << ");
        if (resim_no[i] != 0) {
            metin_yaz(&y, "/XObject << /Im0 ");
            tam_sayi_yaz(&y, resim_no[i]);
            metin_yaz(&y, " 0 R >> ");
        }
        metin_yaz(&y, ">> >>\nendobj\n");

        nesne_basla(&y, ofsetler, icerik_no[i]);
        metin_yaz(&y, "<< /Length ");
        tam_sayi_yaz(&y, (uint32_t)sayac.konum);
        metin_yaz(&y, " >>\nstream\n");
        icerik_yaz(&y, &sayfalar[i], ayar, resim_no[i] != 0);
        metin_yaz(&y, "endstream\nendobj\n");

        if (resim_no[i] != 0) {
            nesne_basla(&y, ofsetler, resim_no[i]);
            metin_yaz(&y, "<< /Type /XObject /Subtype /Image /Width ");
            tam_sayi_yaz(&y, jpeg[i].genislik);
            metin_yaz(&y, " /Height ");
            tam_sayi_yaz(&y, jpeg[i].yukseklik);
            metin_yaz(&y, jpeg[i].bilesen == 1 ? " /ColorSpace /DeviceGray" : " /ColorSpace /DeviceRGB");
            metin_yaz(&y, " /BitsPerComponent 8 /Filter /DCTDecode /Length ");
            tam_sayi_yaz(&y, (uint32_t)sayfalar[i].jpeg_uzunluk);
            metin_yaz(&y, " >>\nstream\n");
            ham_yaz(&y, sayfalar[i].jpeg, sayfalar[i].jpeg_uzunluk);
            metin_yaz(&y, "\nendstream\nendobj\n");
        }
    }

    xref_konum = y.konum;
    metin_yaz(&y, "xref\n0 ");
    tam_sayi_yaz(&y, toplam_nesne);
    metin_yaz(&y, "\n0000000000 65535 f \n");
    for (no = 1; no < toplam_nesne; no++) {
        char satir[24];
        int n = snprintf(satir, sizeof satir, "%010lu 00000 n \n", (unsigned long)ofsetler[no]);
        ham_yaz(&y, satir, (size_t)n);
    }
    metin_yaz(&y, "trailer\n<< /Size ");
    tam_sayi_yaz(&y, toplam_nesne);
    metin_yaz(&y, " /Root 1 0 R >>\nstartxref\n");
    tam_sayi_yaz(&y, (uint32_t)xref_konum);
    metin_yaz(&y, "\n%%EOF\n");
    return y.hata ? HATA_GIRIS_CIKIS : HATA_YOK;
}
