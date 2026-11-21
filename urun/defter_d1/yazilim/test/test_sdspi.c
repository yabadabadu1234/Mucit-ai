#include "sd_sim.h"
#include "test.h"

static int baslat(sdsim_t *sim, sdspi_t *sd, hal_spi_t *spi, hal_zaman_t *zaman, sdsim_tur_t tur, uint32_t blok)
{
    sdsim_baslat(sim, tur, blok);
    *spi = sdsim_spi(sim);
    *zaman = sdsim_zaman(sim);
    return sdspi_baslat(sd, spi, zaman);
}

static void crc_testi(void)
{
    const uint8_t cmd0[5] = {0x40, 0, 0, 0, 0};
    const uint8_t cmd8[5] = {0x48, 0, 0, 0x01, 0xAA};
    KONTROL(sdspi_crc7(cmd0, 5) == 0x95);
    KONTROL(sdspi_crc7(cmd8, 5) == 0x87);
}

static void kapasite_testi(void)
{
    sdsim_t *sim = calloc(1, sizeof *sim);
    sdspi_t sd;
    hal_spi_t spi;
    hal_zaman_t z;

    KONTROL(baslat(sim, &sd, &spi, &z, SD_V2_YUKSEK, 62333952u) == HATA_YOK);
    KONTROL(sd.yuksek_kapasite == 1 && sd.hazir == 1);
    KONTROL(sd.blok_sayisi == 62333952u);
    KONTROL(sdspi_kapasite_bayt(&sd) == 31914983424ull);
    KONTROL(sdspi_kapasite_bayt(&sd) >= 31000000000ull);

    KONTROL(baslat(sim, &sd, &spi, &z, SD_V2_YUKSEK, 125042688u) == HATA_YOK);
    KONTROL(sdspi_kapasite_bayt(&sd) == 64021856256ull);
    KONTROL(sdspi_kapasite_bayt(&sd) >= 64000000000ull);

    KONTROL(baslat(sim, &sd, &spi, &z, SD_V1, 2097152u) == HATA_YOK);
    KONTROL(sd.yuksek_kapasite == 0);
    KONTROL(sdspi_kapasite_bayt(&sd) == 1073741824ull);

    KONTROL(baslat(sim, &sd, &spi, &z, SD_V2_STANDART, 4194304u) == HATA_YOK);
    KONTROL(sd.yuksek_kapasite == 0);
    free(sim);
}

static void hata_baslatma_testi(void)
{
    sdsim_t *sim = calloc(1, sizeof *sim);
    sdspi_t sd;
    hal_spi_t spi;
    hal_zaman_t z;
    KONTROL(baslat(sim, &sd, &spi, &z, SD_YOK, 1024) == HATA_KART_YOK);
    KONTROL(sd.hazir == 0);
    KONTROL(baslat(sim, &sd, &spi, &z, SD_HAZIR_OLMAZ, 1024) == HATA_ZAMAN_ASIMI);
    KONTROL(sd.hazir == 0);

    sdsim_baslat(sim, SD_V2_YUKSEK, 2048);
    sim->baslatma_gerekli = 400;
    spi = sdsim_spi(sim);
    z = sdsim_zaman(sim);
    KONTROL(sdspi_baslat(&sd, &spi, &z) == HATA_YOK);

    sdsim_baslat(sim, SD_V2_YUKSEK, 2048);
    sim->aktarim_hatasi_no = 20;
    spi = sdsim_spi(sim);
    z = sdsim_zaman(sim);
    KONTROL(sdspi_baslat(&sd, &spi, &z) == HATA_GIRIS_CIKIS);

    KONTROL(sdspi_baslat(NULL, &spi, &z) == HATA_PARAMETRE);
    KONTROL(sdspi_baslat(&sd, NULL, &z) == HATA_PARAMETRE);
    free(sim);
}

static void okuma_yazma_testi(void)
{
    sdsim_t *sim = calloc(1, sizeof *sim);
    sdspi_t sd;
    hal_spi_t spi;
    hal_zaman_t z;
    uint8_t yaz_tampon[512 * 4];
    uint8_t oku_tampon[512 * 4];
    uint8_t beklenen[512];
    int i;

    KONTROL(baslat(sim, &sd, &spi, &z, SD_V2_YUKSEK, 62333952u) == HATA_YOK);
    for (i = 0; i < (int)sizeof yaz_tampon; i++) {
        yaz_tampon[i] = (uint8_t)(i * 13 + 5);
    }
    KONTROL(sdspi_yaz(&sd, 0, 4, yaz_tampon) == HATA_YOK);
    KONTROL(sdspi_oku(&sd, 0, 4, oku_tampon) == HATA_YOK);
    KONTROL(memcmp(yaz_tampon, oku_tampon, sizeof yaz_tampon) == 0);

    KONTROL(sdspi_yaz(&sd, 60000000u, 1, yaz_tampon) == HATA_YOK);
    KONTROL(sdspi_oku(&sd, 60000000u, 1, oku_tampon) == HATA_YOK);
    KONTROL(memcmp(yaz_tampon, oku_tampon, 512) == 0);
    KONTROL(sim->son_yaz_argumani == 60000000u);

    sim_blok_deseni(123456u, beklenen);
    KONTROL(sdspi_oku(&sd, 123456u, 1, oku_tampon) == HATA_YOK);
    KONTROL(memcmp(oku_tampon, beklenen, 512) == 0);

    KONTROL(sdspi_oku(&sd, 62333951u, 1, oku_tampon) == HATA_YOK);
    KONTROL(sdspi_oku(&sd, 62333952u, 1, oku_tampon) == HATA_PARAMETRE);
    KONTROL(sdspi_oku(&sd, 62333951u, 2, oku_tampon) == HATA_PARAMETRE);
    KONTROL(sdspi_oku(&sd, 0, 0, oku_tampon) == HATA_PARAMETRE);
    KONTROL(sdspi_oku(&sd, 0, 1, NULL) == HATA_PARAMETRE);
    KONTROL(sdspi_yaz(&sd, 62333952u, 1, yaz_tampon) == HATA_PARAMETRE);

    KONTROL(baslat(sim, &sd, &spi, &z, SD_V1, 2097152u) == HATA_YOK);
    KONTROL(sdspi_yaz(&sd, 5, 1, yaz_tampon) == HATA_YOK);
    KONTROL(sim->son_yaz_argumani == 5u * 512u);
    KONTROL(sdspi_oku(&sd, 5, 1, oku_tampon) == HATA_YOK);
    KONTROL(sim->son_oku_argumani == 5u * 512u);
    KONTROL(memcmp(yaz_tampon, oku_tampon, 512) == 0);
    free(sim);
}

static void ariza_testi(void)
{
    sdsim_t *sim = calloc(1, sizeof *sim);
    sdspi_t sd;
    hal_spi_t spi;
    hal_zaman_t z;
    uint8_t tampon[512];
    memset(tampon, 0xA5, sizeof tampon);

    KONTROL(baslat(sim, &sd, &spi, &z, SD_V2_YUKSEK, 4096) == HATA_YOK);
    sim->yazma_hatasi_enjekte = 1;
    KONTROL(sdspi_yaz(&sd, 10, 1, tampon) == HATA_YAZMA_REDDI);
    sim->yazma_hatasi_enjekte = 0;

    sim->mesgul_bayt = 100;
    KONTROL(sdspi_yaz(&sd, 10, 1, tampon) == HATA_YOK);
    sim->mesgul_bayt = 1000;
    KONTROL(sdspi_yaz(&sd, 11, 1, tampon) == HATA_ZAMAN_ASIMI);
    sim->mesgul_bayt = 0;

    sim->tur = SD_YOK;
    KONTROL(sdspi_oku(&sd, 1, 1, tampon) == HATA_KART_YOK);
    KONTROL(sdspi_yaz(&sd, 1, 1, tampon) == HATA_KART_YOK);

    sim->tur = SD_V2_YUKSEK;
    sim->aktarim_sayisi = 0;
    sim->aktarim_hatasi_no = 3;
    KONTROL(sdspi_oku(&sd, 1, 1, tampon) == HATA_GIRIS_CIKIS);
    free(sim);
}

int main(void)
{
    crc_testi();
    kapasite_testi();
    hata_baslatma_testi();
    okuma_yazma_testi();
    ariza_testi();
    SONUC("sdspi");
}
