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
3. **Telsiz:** Ra-01H modülü (SX1276) 915 megahertzte mesaj yollar. Anten, kartın üst kenarındaki SMA konnektörüne tek düz bakır yolla bağlı; yolun genişliği (0,4 mm) altındaki toprak düzlemiyle 50 ohm verecek şekilde hesaplandı. Bu hesabı üreticinin gerçek katman kalınlığıyla doğrulatmak gerekir.
4. **USB-C:** Programlama için. Modülün USB'si kendi içinde olduğu için ayrı çeviri çipi yok. Programlama kipine girmek için birinci düğmeye basılı tutup USB takılır.
5. **LED:** Bir adet durum ışığı.

Ayak atamaları ve güç tahmini `verici/TASARIM_NOTU.md` içinde.

## 5. Alıcı nasıl çalışıyor

1. **Giriş:** 12 volt vidalı klemense gelir. Sırayla: 2 amperlik kendini toparlayan sigorta, ters bağlanmaya karşı P-kanallı transistör, aşırı gerilime karşı 15 voltluk koruma diyodu.
2. **İki ayrı çevirici:** Biri 12 voltu 3,3 volta çevirir (kart ve modüller). Diğeri 4,0 volt üretir ve yalnızca 4G modemi besler, çünkü modem kısa süreli 2,8 amper çeker (A7670SA belgesi). Yanında 330 mikrofaradlık büyük kondansatör var.
3. **Beyin ve telsiz:** Verici ile aynı ESP32-S3 ve Ra-01H. İkisi aynı veri hattını paylaşır, seçim hatları ayrı.
4. **Ethernet:** W5500 çipi ve yerleşik trafolu RJ45 konnektörü. Bağlantı şeması üreticinin (WIZnet) resmî referans devresinden alındı.
5. **4G modem:** SIMCom A7670SA (LTE Cat 1; Şili bantları B28/B7/B4/B2/B66/B5 belge listesinde var), SIM kart yuvası kartın arka yüzünde modülün altında. Modemin seri hattı 1,8 volt; ESP32 ise 3,3 volt. Aralarına gerilim seviyesi çeviren çip konuldu. İlk planda yoktu, belgeyi okuyunca fark ettim.
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
- Bu sürümde: modem SIM7600SA yerine A7670SA (parça başına yaklaşık 9 dolar, öncekinin 37 dolarına karşı), RFM95W yerine Ra-01H (yaklaşık 4,65 dolar), güç bobinleri Bourns SRP7028A, USB yolundaki Schottky yerine LM66100 ideal diyot, PWRKEY/RESET ve SIM hatlarına USBLC6 koruma, SIM hatlarına 22 ohm seri direnç.

## 8. Neler doğrulanmadı (açıkça)

- Telsiz menzili, anten uyumu, cep telefonu şebekesinde bağlanma: ölçülmedi, kart yapılıp sahada denenmeli.
- Modemin ayak tablosu SIMCom'un A7670 Series Hardware Design belgesinden (Tablo 3, Şekil 2 ve 4) alındı: 88 pedin hepsi sembolde ve ayak izinde var. A7670SA'nın LASC/LASE/FASE/MASC son ekleri SIMCom belgelerinde açıklanmıyor; satın almadan önce satıcıya yazılı sorulmalı. LCSC'de LASE'den 1, LASC'den 97 adet görüldü; 100 set için stok ve teslim süresi sorulmalı.
- Ra-01H'nin pedleri, aynı boyuttaki Ra-01 kılavuzunun çiziminden alındı (Ra-01H belgesinde ölçü çizimi yok); üretimden önce Ai-Thinker'e teyit ettirilmeli.
- Modem besleme hattı 1,0 mm (41 mm) ve 0,4 mm (43 mm); SIMCom 2 mm'den geniş öneriyor, ama bobinden modem pedlerine direnç karttan hesaplandı: yaklaşık 18-19 miliohm. 2,8 amperlik patlamada modem ucu, çevirici döngü bant genişliği 20 kHz ve üstündeyse 3,54 V ve üstünde kalıyor; 10 kHz olsaydı 2,9 V'a düşerdi (alt sınır 3,4 V). Bant genişliği veri sayfasında yok, varsayım; prototipte ölçülmeli.
- Parça stoğu ve satıcı numaraları kontrol edilmedi.
- Pil ömrü rakamları hesap; ölçüm değil.
- Röleden geçecek lamba akımı bilinmiyor; 3 amper varsayıldı.

## 9. Durum

- **Verici:** bitti. Kural denetiminden hata çıkmadı, üretim dosyaları hazır.
- **Alıcı:** bitti. Kart 88 × 102 mm, dört katmanlı. Kural denetiminde hata yok, bağlantısız ayak yok; 565 ayağın hepsi şemadan çıkarılan bağlantı listesiyle karşılaştırıldı, uyumsuzluk yok. Üretim dosyaları `alici/uretim_dosyalari/` içinde. Lamba hattı (+12V_IN ve LAMBA_SW) 0,8 mm genişlikte; IPC-2221'e göre 10 derece ısınmayla yaklaşık 2 amper taşır. Gerçek lamba akımı bilinmiyor; 2 amperin üstüyse söyleyin, genişletirim.
- **Bilinen zayıflıklar (alıcı):** W5500'ün kristal hatları uzun (yaklaşık 19,5 ve 21 mm; veri sayfası kısa ister), Ethernet çiftlerinin uzunlukları 2-3 mm farklı, modem besleme izi önerilen 2 mm yerine 1,0/0,4 mm, telsiz menzili ve hücresel bağlantı denenmedi. Ayrıntı: `alici/TASARIM_NOTU.md`.
- **Ders sitesi:** tasarımı sıfırdan öğreten bir site `ders/` klasöründedir; her güncellemede GitHub Pages'e otomatik yayınlanır (bkz. `ders/README.md`).
