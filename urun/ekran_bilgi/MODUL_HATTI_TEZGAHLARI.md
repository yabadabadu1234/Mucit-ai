# MODÜL HATTI TEZGÂHLARI (hazır hücre camından bitmiş modüle)

**Tarih:** 2026-11-23
**Esas:** Hücre camı (open cell) hazır alınır; hat yalnız modül adımlarını yapar.
**Dürüstlük:** Zorluk puanı (1 kolay, 5 çok zor), "kendin tasarla" hükmü ve işlev tarifleri benim süreç bilgimdendir; yalnız COG parametreleri bir arama özetinden gelir (kaynak altta). Tezgâh fiyatı hiçbirinde bulunamadı, bu yüzden masraf sütunu yoktur.

| # | Tezgâh | Gördüğü iş | Zorluk | Zorluğun sebebi | Kendin tasarla mı? | Hazır alınacak parça |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | Hücre temizleme | Cam yüzeyi yağ ve tozdan arındırmak; COG öncesi 185 ve 254 nm UV veya oksijen plazma (bir satıcı blogundan) | 2 | Düzgün ışık/plazma ve toz kontrolü | Evet | UV lambaları, plazma kaynağı |
| 2 | Görsel denetim (AOI) | Kusur, leke, çizik yakalamak | 3 | Aydınlatma ve görüntü işleme yazılımı | Evet (yazılımı sen yazarsın) | Endüstriyel kamera, lens, aydınlatma |
| 3 | Polarizer yapıştırma | Alt ve üst cama polarizer filmini eksen doğru, kabarcıksız yapıştırmak | 3–4 | Eksen hizası (çapraz 90°), kabarcık, statik | Evet | Film ruloları (polarizer), silikon silindirler, hizalama kamerası |
| 4 | Otoklav | Isı ve basınçla kalan kabarcığı çıkarmak | 2–3 | Basınçlı kap güvenliği ve sertifikası (benim bilgim, yoklanmadı) | Kısmen: gövdeyi hazır al | Basınçlı kap, ısıtıcı, kontrol |
| 5 | ACF ön yapıştırma | Anizotropik iletken filmi cam kenarına ön ısıyla yapıştırmak | 3 | Düzgün sıcaklık ve film besleme | Evet | ACF film ruloları |
| 6 | COG bağlayıcı | Sürücü çipini cama ısı ve basınçla bağlamak; 150–220 °C, 5–15 sn, basınç (arama özeti); ince adımda hizalama zorlaşır | 5 | Mikron hassasiyetli optik hizalama, kafa düzlemliği, sıcaklık dağılımı | Zor; önce kaba adımlı (büyük pitch) ekranla başla | Isıtma kafası, hassas eksenler, hizalama optiği |
| 7 | FOG/FPC bağlayıcı | Esnek bandı cama bağlamak (aynı ACF ilkesi, daha kaba adım) | 3 | COG'dan daha rahat hizalama | Evet | Isıtma kafası, kamera |
| 8 | Dokunmatik ve kapak camı lamine (OCA) | Optik yapıştırıcıyla kapak/dokunmatik katmanı modüle kabarcıksız yapıştırmak | 3–4 | Kabarcık, toz, vakumlu lamine | Evet | OCA film, vakum odası |
| 9 | Arka ışık montajı | LED şerit, kılavuz plaka, filmler, kasa birleştirme | 1–2 | Mekanik; toz | Evet (kalıp tasarlayıp ürettir) | LED şerit, PMMA kılavuz, difüzör ve prizma filmleri |
| 10 | Elektrik testi | Piksel, satır ve sütun, dokunmatik ve parlaklık testi | 2–3 | Test deseni yazılımı | Evet | Kontrol kartı, sondalar |
| 11 | Yaşlandırma (burn-in) | Erken arızaları yakalamak | 1 | Raf ve güç | Evet | Güç kaynağı, raf |

## Elinde kalan zor iş

Tezgâhların çoğu mekanik ve optik hizalama işidir ve sizin tasarlayabileceğiniz düzeydedir. Zor olan **COG bağlayıcıdır** (#6): çipin altın çıkıntıları ile cam pedleri arasında mikron düzeyi hizalama ve sıcaklık/basınç reçetesi. Önce ucuz, büyük adımlı ekran veya FPC ile (FOG) başlayın; COG'u sonra deneyin.

## Boşluklar

- Tezgâh fiyatı yok (Panasonic sayfaları "teklif alın" diyor).
- Polarizer yapıştırma ve otoklav parametreleri bulunamadı; kabarcık giderme ayrıntısı kaynaksız.
- Alt Gen 1 COG hizalama toleransı (mikron) kaynaklarda yazılı değil.

## Kaynaklar

- COG parametreleri (sıcaklık 180–220 °C, süre 5–15 sn, ACF çalışma ilkesi): https://koreascience.kr/article/JAKO201029848355088.page , https://www.displaymodule.com/blogs/knowledge/how-does-cog-lcd-works-structure-bonding-process
- Tezgâh üreticisi sayfaları (fiyatsız): https://connect.panasonic.com/en/products-services/fa_products_display-related/lineup/fpx305cg
