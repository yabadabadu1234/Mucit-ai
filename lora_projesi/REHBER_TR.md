# Rehber: Yaptığım işler, ne işe yarıyor, nasıl okunur

Bu rehber kısaltma kullanmadan yazıldı. Bir terim ilk geçtiğinde açıklanır. Durum bilgisi en sonda.

## 1. Ne yapıldı, bir bakışta

Müşterinin ilanındaki iki cihaz için elektronik tasarım hazırlandı:

1. **Verici (uzaktan kumanda):** altı düğmeli, pille çalışan, telsizle (LoRa) mesaj gönderen küçük kart.
2. **Alıcı:** sabit duran, telsizle mesajı alan, internete kabloyla (Ethernet) ya da cep telefonu şebekesiyle (4G) bağlanan, 12 voltluk bir lambayı röleyle açıp kapatan kart.

"Tasarım" burada şu demek: devre şeması (hangi parça neye bağlı), baskı devre kartının çizimi (parçaların kart üstündeki yeri ve bakır yolları) ve üreticiye gönderilecek dosyalar. Yazılım (firmware) ilanda istenmediği için yok.

## 2. Terimler

- **Baskı devre kartı:** Üstünde bakır yollar olan, parçaların lehimlendiği yeşil levha. Bu projede dört katmanlı: üstte ve altta parçalar ile yollar, içte iki katman (biri toprak, biri 3,3 voltluk besleme düzlemi). Sebep: telsiz anten hattının altında kesintisiz toprak düzlemi olması.
- **Net listesi:** Şemadan çıkarılan "hangi parçanın hangi ayağı hangisine bağlı" listesi. Kartı şemaya bağlayan şey budur.
- **Gerber dosyaları:** Kart üreticisinin okuduğu katman katman resim dosyaları (bakır, lehim maskesi, serigrafi, kart kenarı).
- **Delik dosyası:** Delinecek yerlerin listesi.
- **Malzeme listesi:** Hangi parçadan kaç tane, hangi numaralarla.
- **Yerleştirme dosyası:** Montaj makinesi için her parçanın koordinatı ve dönüşü.
- **Lehim maskesi, serigrafi:** Bakırı kaplayan yeşil boya; üstündeki beyaz yazılar.
- **Delikli geçit (via):** Katmanlar arası bakır bağlantı deliği.
- **Otomatik yönlendirici (Freerouting):** Bakır yolları kendi çizen program. Ben parçaları yerleştirdim, yolları o çizdi, ben sonucu denetledim.
- **Kural denetimi (KiCad):** Kartın üretim kurallarına uyup uymadığını ölçen program (yollar arası boşluk, delik mesafeleri, bağlantısı eksik ayak). "Hata yok" demek bu denetimden geçmek demektir. Telsiz menzilini ya da devrenin sahada çalışacağını göstermez.
- **Benzetim (ngspice):** Devrenin bir bölümünü bilgisayarda hesaplatmak. Genel parça modelleri kullandım, üreticinin kendi modelleri değil.

## 3. Dosyalar nerede

Her şey `lora_projesi/` klasöründe:

| Yer | İçerik |
| :-- | :-- |
| `verici/` | Verici: şema, kart, üretim dosyaları (`uretim_dosyalari/`), tasarım notu |
| `alici/` | Alıcı: şema, kart (bitmedi), tasarım notu |
| `simulasyon/` | İki benzetim: röle sürücüsü, 12 voltluk giriş koruması |
| `uretim/` | Her şeyi üreten Python programları (yeniden çalıştırılabilir) |
| `teklif_taslagi.md`, `teklif_kisa.txt` | Teklif metinleri |

Üretim klasöründeki `*_sema.pdf` şemayı, `*_pano_on.pdf` ve `*_pano_arka.pdf` kartın ön ve arka yüzünü gösterir. `*_gerber.zip` doğrudan kart üreticisine yüklenecek paket.

## 4. Verici nasıl çalışıyor

1. **Besleme:** İki adet AAA pil bir yuvada. Pil anahtardan ve bir diyottan geçip 3,3 volta çeviriciye gider. Çevirici (TPS63031) pil bittikçe gerilim düşse de 3,3 volt üretir. USB-C takılınca onun 5 voltu da başka bir diyotla aynı noktaya girer, pile geri akım gitmesin diye.
2. **Beyin:** ESP32-S3 modülü. Derin uykuda yaklaşık 8 mikroamper çeker. Altı düğmenin her biri modülün uyandırma yapabilen bir ayağına bağlı; basınca uyanır.
3. **Telsiz:** RFM95W modülü 915 megahertzte mesaj yollar. Anten, kartın üst kenarındaki SMA konnektörüne tek düz bakır yolla bağlı; yolun genişliği (0,4 mm) altındaki toprak düzlemiyle 50 ohm verecek şekilde hesaplandı. Bu hesabı üreticinin gerçek katman kalınlığıyla doğrulatmak gerekir.
4. **USB-C:** Programlama için. Modülün USB'si kendi içinde olduğu için ayrı çeviri çipi yok. Programlama kipine girmek için birinci düğmeye basılı tutup USB takılır.
5. **LED:** Bir adet durum ışığı.

Ayak atamaları ve güç tahmini `verici/TASARIM_NOTU.md` içinde.

## 5. Alıcı nasıl çalışıyor

1. **Giriş:** 12 volt vidalı klemense gelir. Sırayla: 2 amperlik kendini toparlayan sigorta, ters bağlanmaya karşı P-kanallı transistör, aşırı gerilime karşı 15 voltluk koruma diyodu.
2. **İki ayrı çevirici:** Biri 12 voltu 3,3 volta çevirir (kart ve modüller). Diğeri 3,8 volt üretir ve yalnızca 4G modemi besler, çünkü modem kısa süreli 2 amper çeker. Yanında 330 mikrofaradlık büyük kondansatör var.
3. **Beyin ve telsiz:** Verici ile aynı ESP32-S3 ve RFM95W. İkisi aynı veri hattını paylaşır, seçim hatları ayrı.
4. **Ethernet:** W5500 çipi ve yerleşik trafolu RJ45 konnektörü. Bağlantı şeması üreticinin (WIZnet) resmî referans devresinden alındı.
5. **4G modem:** SIM7600SA modülü, SIM kart yuvası kartın arka yüzünde modülün altında. Modemin seri hattı 1,8 volt; ESP32 ise 3,3 volt. Aralarına gerilim seviyesi çeviren çip konuldu. İlk planda yoktu, belgeyi okuyunca fark ettim.
6. **Röle:** Röle yalnızca bir transistörle sürülür; transistörün tabanı 10 kilo-ohmla toprağa çekili, yani cihaz açılırken röle yanlışlıkla çekmez. Lambanın akımı röle kontaklarından geçer; bu akım karttaki koruma transistöründen geçmez, doğrudan klemensten gelir.
7. **Gösterge:** Bir düğme, iki programlanabilir ışık.

Ayak atamaları ve açık konular `alici/TASARIM_NOTU.md` içinde.

## 6. Benzetim sonuçları (genel modellerle)

- **Röle sürücüsü:** bobin akımı 29,8 miliamper; transistör doyma gerilimi 62 milivolt; röle bırakırken tepe gerilim 12,2 volt (transistör bunu rahat kaldırır).
- **12 voltluk giriş koruması:** normalde toplam gerilim kaybı 0,30 volt; ters bağlanınca çıkış −0,08 volt ve giriş akımı ihmal edilir düzeyde; 36 voltluk darbe çıkışı 20,3 volta sınırlıyor.

Bunlar tasarımın mantıksal olarak çalıştığını gösterir; gerçek parçalarla ölçüm yerine geçmez.

## 7. Neler değişti, neden (teklife göre)

- ESP32-WROOM-32E yerine ESP32-S3-WROOM-1: USB'si dahili olduğu için çeviri çipi ve onun pilde boşuna akım çekme sorunu ortadan kalktı.
- İki katman yerine dört katman: telsiz anten yolu için.
- SIM yuvası nano yerine micro: elimdeki kütüphanede nano yoktu.
- Alıcıya seviye çevirici eklendi (modem 1,8 volt).

## 8. Neler doğrulanmadı (açıkça)

- Telsiz menzili, anten uyumu, cep telefonu şebekesinde bağlanma: ölçülmedi, kart yapılıp sahada denenmeli.
- Modemin ayak düzeni SIM7600E/E-H resmî belgesinden alındı. SA/SA-H'nin kendi donanım belgesini bulamadım; sipariş öncesi doğrulanmalı. Gönderdiğiniz 3 sayfalık ürün tanıtım belgesi yalnızca şunu doğruluyor: SA ile E aynı gövdede (87 ayaklı, 30×30 mm), besleme 3,4–4,2 volt. Ayak tablosu yok; yani ayak düzenini ne doğruluyor ne yalanlıyor. Ayrıca belgeye göre SA'da 800 MHz'lik 20. bant yok (E'de var); Türkiye'de kullanılacaksa bu bant gerekebilir (bu bilgi hafızamdan, doğrulanmadı).
- Parça stoğu ve satıcı numaraları kontrol edilmedi.
- Pil ömrü rakamları hesap; ölçüm değil.
- Röleden geçecek lamba akımı bilinmiyor; 3 amper varsayıldı.

## 9. Durum

- **Verici:** bitti. Kural denetiminden hata çıkmadı, üretim dosyaları hazır.
- **Alıcı:** bitti. Kart 88 × 102 mm, dört katmanlı. Kural denetiminde hata yok, bağlantısız ayak yok; 531 ayağın hepsi şemadan çıkarılan bağlantı listesiyle karşılaştırıldı, uyumsuzluk yok. Üretim dosyaları `alici/uretim_dosyalari/` içinde. Lamba hattı 1,4 mm genişlikte ve viyasız (3 A varsayımıyla).
- **Bilinen zayıflıklar (alıcı):** W5500'ün kristal hatları uzun (yaklaşık 28 ve 32 mm; veri sayfası kısa ister), Ethernet çiftlerinin uzunlukları eşit değil, modem modülünün SA/SA-H ayak düzeni doğrulanmadı (E/E-H belgesinden alındı), telsiz menzili ve hücresel bağlantı denenmedi. Ayrıntı: `alici/TASARIM_NOTU.md`.
- **Ders sitesi:** tasarımı sıfırdan öğreten bir site `ders/` klasöründedir; her güncellemede GitHub Pages'e otomatik yayınlanır (bkz. `ders/README.md`).
