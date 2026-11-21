#include <string.h>

#include "guc_yonetimi.h"

int batarya_modeli_dogrula(const batarya_modeli_t *m)
{
    size_t i;
    if (m == NULL || m->tablo == NULL || m->adet < 2) {
        return HATA_PARAMETRE;
    }
    for (i = 1; i < m->adet; i++) {
        if (m->tablo[i].mv >= m->tablo[i - 1].mv || m->tablo[i].yuzde > m->tablo[i - 1].yuzde) {
            return HATA_PARAMETRE;
        }
    }
    if (m->tablo[0].yuzde != 100 || m->tablo[m->adet - 1].yuzde != 0) {
        return HATA_PARAMETRE;
    }
    return HATA_YOK;
}

uint8_t batarya_yuzde(const batarya_modeli_t *m, uint16_t olculen_mv, uint16_t yuk_ma)
{
    uint32_t duzeltilmis = (uint32_t)olculen_mv + ((uint32_t)yuk_ma * m->ic_direnc_mohm) / 1000u;
    size_t i;
    if (duzeltilmis >= m->tablo[0].mv) {
        return 100;
    }
    if (duzeltilmis <= m->tablo[m->adet - 1].mv) {
        return 0;
    }
    for (i = 1; i < m->adet; i++) {
        if (duzeltilmis >= m->tablo[i].mv) {
            uint32_t ust_mv = m->tablo[i - 1].mv;
            uint32_t alt_mv = m->tablo[i].mv;
            uint32_t ust_y = m->tablo[i - 1].yuzde;
            uint32_t alt_y = m->tablo[i].yuzde;
            return (uint8_t)(alt_y + ((duzeltilmis - alt_mv) * (ust_y - alt_y)) / (ust_mv - alt_mv));
        }
    }
    return 0;
}

int guc_baslat(guc_t *g, const guc_ayar_t *ayar)
{
    if (g == NULL || ayar == NULL || ayar->karartma_ms == 0 || ayar->uyku_ms <= ayar->karartma_ms ||
        ayar->kritik_yuzde >= ayar->uyari_yuzde || ayar->histerezis_yuzde == 0) {
        return HATA_PARAMETRE;
    }
    memset(g, 0, sizeof *g);
    g->ayar = *ayar;
    g->durum = GUC_AKTIF;
    return HATA_YOK;
}

static uint32_t daha_gec(uint32_t a, uint32_t b)
{
    return (int32_t)(a - b) > 0 ? a : b;
}

guc_cikti_t guc_guncelle(guc_t *g, const guc_girdi_t *girdi)
{
    guc_cikti_t c;
    uint32_t etkinlik;
    uint32_t bosta;
    int kayit_darbesi = 0;

    memset(&c, 0, sizeof c);

    if (g->usb_onceki && !girdi->usb_veri_aktarimi) {
        g->usb_cikis_ms = girdi->simdi_ms;
    }
    g->usb_onceki = girdi->usb_veri_aktarimi;

    if (!g->uyari_acik && girdi->pil_yuzde <= g->ayar.uyari_yuzde) {
        g->uyari_acik = 1;
    } else if (g->uyari_acik && girdi->pil_yuzde >= (uint32_t)g->ayar.uyari_yuzde + g->ayar.histerezis_yuzde) {
        g->uyari_acik = 0;
    }

    if (!g->kritik_verildi && !girdi->usb_vbus && girdi->pil_yuzde <= g->ayar.kritik_yuzde) {
        g->kritik_verildi = 1;
        kayit_darbesi = 1;
    } else if (g->kritik_verildi && girdi->usb_vbus &&
               girdi->pil_yuzde >= (uint32_t)g->ayar.kritik_yuzde + g->ayar.histerezis_yuzde) {
        g->kritik_verildi = 0;
        g->durum = GUC_AKTIF;
    }

    c.uyari_goster = g->uyari_acik;

    if (g->kritik_verildi) {
        g->durum = GUC_KAPANIS;
        c.durum = GUC_KAPANIS;
        c.notlari_kaydet = kayit_darbesi;
        c.kapat = 1;
        return c;
    }

    if (girdi->usb_veri_aktarimi) {
        g->durum = GUC_USB_AKTARIM;
        c.durum = GUC_USB_AKTARIM;
        return c;
    }

    etkinlik = daha_gec(girdi->son_etkinlik_ms, g->usb_cikis_ms);
    bosta = (uint32_t)(girdi->simdi_ms - etkinlik);
    if ((int32_t)(girdi->simdi_ms - etkinlik) < 0) {
        bosta = 0;
    }

    if (girdi->tus_uyandirma) {
        bosta = 0;
    }

    if (bosta < g->ayar.karartma_ms) {
        g->durum = GUC_AKTIF;
        c.parlaklik = g->ayar.parlaklik_aktif;
        c.ekran_acik = 1;
    } else if (bosta < g->ayar.uyku_ms) {
        g->durum = GUC_KARARMIS;
        c.parlaklik = g->ayar.parlaklik_kararmis;
        c.ekran_acik = 1;
    } else {
        g->durum = GUC_UYKU;
    }
    c.durum = g->durum;
    return c;
}
