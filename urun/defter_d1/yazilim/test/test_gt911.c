#include "gt911_sim.h"
#include "test.h"

int main(void)
{
    gt911sim_t sim;
    hal_i2c_t i2c;
    gt911_t g;
    dokunus_t nokta[GT911_AZAMI_NOKTA];
    dokunus_t giris[3];
    uint8_t adet;
    int yeni;

    gt911sim_baslat(&sim, GT911_ADRES_A);
    i2c = gt911sim_hal(&sim);
    KONTROL(gt911_baslat(&g, &i2c, GT911_ADRES_A) == HATA_YOK);
    KONTROL(gt911_baslat(&g, &i2c, 0x42) == HATA_PARAMETRE);
    KONTROL(gt911_baslat(NULL, &i2c, GT911_ADRES_A) == HATA_PARAMETRE);
    KONTROL(gt911_baslat(&g, &i2c, GT911_ADRES_B) == HATA_GIRIS_CIKIS);

    sim.kayit[0x142] = '2';
    KONTROL(gt911_baslat(&g, &i2c, GT911_ADRES_A) == HATA_PROTOKOL);
    sim.kayit[0x142] = '1';
    KONTROL(gt911_baslat(&g, &i2c, GT911_ADRES_A) == HATA_YOK);

    KONTROL(gt911_oku(&g, nokta, &adet, &yeni) == HATA_YOK);
    KONTROL(adet == 0 && yeni == 0);

    giris[0].iz_no = 3; giris[0].x = 799; giris[0].y = 479; giris[0].boyut = 0x1234;
    giris[1].iz_no = 7; giris[1].x = 256; giris[1].y = 1;   giris[1].boyut = 22;
    giris[2].iz_no = 9; giris[2].x = 0;   giris[2].y = 300; giris[2].boyut = 180;
    gt911sim_kare(&sim, giris, 3, 3);
    KONTROL(gt911_oku(&g, nokta, &adet, &yeni) == HATA_YOK);
    KONTROL(adet == 3 && yeni == 1);
    KONTROL(nokta[0].iz_no == 3 && nokta[0].x == 799 && nokta[0].y == 479 && nokta[0].boyut == 0x1234);
    KONTROL(nokta[1].iz_no == 7 && nokta[1].x == 256 && nokta[1].y == 1 && nokta[1].boyut == 22);
    KONTROL(nokta[2].iz_no == 9 && nokta[2].x == 0 && nokta[2].y == 300 && nokta[2].boyut == 180);
    KONTROL(sim.kayit[0x14E] == 0);

    KONTROL(gt911_oku(&g, nokta, &adet, &yeni) == HATA_YOK);
    KONTROL(adet == 0 && yeni == 0);

    gt911sim_kare(&sim, NULL, 0, 0);
    KONTROL(gt911_oku(&g, nokta, &adet, &yeni) == HATA_YOK);
    KONTROL(adet == 0 && yeni == 1);
    KONTROL(sim.kayit[0x14E] == 0);

    gt911sim_kare(&sim, giris, 3, 6);
    KONTROL(gt911_oku(&g, nokta, &adet, &yeni) == HATA_PROTOKOL);
    KONTROL(adet == 0 && yeni == 0);
    KONTROL(sim.kayit[0x14E] == 0);

    gt911sim_kare(&sim, giris, 3, 3);
    sim.islem_sayisi = 0;
    sim.basarisiz_islem_no = 1;
    KONTROL(gt911_oku(&g, nokta, &adet, &yeni) == HATA_GIRIS_CIKIS);
    sim.islem_sayisi = 0;
    sim.basarisiz_islem_no = 3;
    KONTROL(gt911_oku(&g, nokta, &adet, &yeni) == HATA_GIRIS_CIKIS);
    sim.basarisiz_islem_no = 0;
    sim.islem_sayisi = 0;
    gt911sim_kare(&sim, giris, 3, 3);
    KONTROL(gt911_oku(&g, nokta, &adet, &yeni) == HATA_YOK);
    KONTROL(adet == 3);

    KONTROL(gt911_oku(&g, NULL, &adet, &yeni) == HATA_PARAMETRE);
    KONTROL(gt911_oku(NULL, nokta, &adet, &yeni) == HATA_PARAMETRE);

    SONUC("gt911");
}
