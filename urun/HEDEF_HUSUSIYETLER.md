# HEDEF HÜSÛSİYETLER DOSYASI

**Mevzu:** Dijital not ve çizim cihazı (ilk model) ve ilave yapay zekâ kabiliyeti (ikinci model)
**Tarih:** 2026-11-18
**Durum:** Taslak. Her hüsûsiyet için karar ve ölçü, piyasa araştırmasından sonra kesinleşecektir.

---

## 1. Maksat

Bu dosyada, üretilmesi düşünülen cihazın istenen hüsûsiyetleri tek tek kaydedilmiştir. Maksat, cihazın ne yapması gerektiğini açıkça tarif etmek ve sonraki aşamada yapılacak piyasa araştırmasına, üretici seçimine ve fiyat karşılaştırmasına bir ölçü vermektir.

Bu dosyada yalnız **hüsûsiyetler** yer alır. Donanım listesi, üretici bilgileri ve fiyatlar ayrı dosyalarda tutulacaktır (bkz. Bölüm 7).

Bu dosyadaki her madde üç sütunla okunmalıdır: **hüsûsiyetin tarifi**, **taslak ölçü** ve **açık nokta**. Açık nokta, henüz karara bağlanmamış ve padişahın (sahibinin) cevabına muhtaç olan hususu gösterir. Taslak ölçüler, Claude tarafından önerilmiş olup kesin hüküm değildir.

---

## 1-B. GÜNCEL KARARLAR (2026-11-18, padişahın sözü)

- Yapay zekâ **şimdilik düşünülmez**; Bölüm 3 yerinde durur, üzerinde durulmaz.
- Pil ömrü hedefi **güncellenebilir** (24 saat değişmez bir hüküm değildir).
- **Renkli ekran hedeftir.**
- Kalem standardı **bağımlı değişkendir**, tek başına ehemmiyeti yoktur; işe yarasın yeter. **En düşük seviye kalem bile desteklenecek**, kendi kalemimiz maliyete göre tayin edilebilir.
- Güneş paneli **mecburî değildir**; yerli ve verimi yüksek yeni modeller araştırılacaktır.
- **Pil ömrü için E-ink kullanılacak** (renkli hedef sürdüğü için renkli E-ink: Kaleido 3 veya benzeri). Piyasada renkli E-ink tabletlerin fiyatı 250 $ ve üstüdür (bkz. `PIYASA_ARASTIRMASI.md` 2.2); maliyet hedefi bu sınıfa göre yeniden tartılacak.
- **NAKZ (E-ink kararı):** E-ink ekran sürdürülebilir bir tercih değil, **sonraki modellere ertelendi.** İlk model, 7 inça yakın en ucuz cihazdır (bkz. `ILK_MODEL_LCD_MALIYET.md`). Yukarıdaki "pil için E-ink" ve "renkli E-ink" satırları ikinci model içindir; ilk modelde 24 saatlik pil hedefi LCD ile tutmaz.
- **Lüksler terk edildi; avuç reddi zarurettir** (bkz. H5). ESP32 kullanılmaz; ekranı, dosya sistemini ve hafızayı süren **tek bir kendi kartımız** olacak (bkz. `TEK_KART_TASARIMI.md`). Kamera ve telefon bağlantısı çok fark etmezse olur, fark ederse olmaz; bilgisayara bağlantı USB ile.
- **Hedef kitle talebelerdir;** ne kadar ucuz olursa o kadar iyidir.
- **İşletim sistemi çalıştıracak kadar gelişmiş işlemci gerekmez;** maliyeti kısacak olan budur (mikrodenetleyici yeter; bkz. `URETICILER.md` § 3).
- **Montaj ya kendimiz yaparız ya da mutlaka yerli bir yerde yaptırılır.**
- **Girişimci desteği bulunacaktır** (bkz. `URETICILER.md` § 5).
- Piyasa araştırması **hazır üründen değil üretici sitelerinden** yapılır; mühim olan E-ink tabletin değil **E-ink ekranın** maliyetidir.
- Sıra: evvelâ piyasa araştırması (bkz. `PIYASA_ARASTIRMASI.md`), güneş paneli (bkz. `GUNES_PANELI_ARASTIRMASI.md`), kalem standardı (bkz. `KALEM_STANDARDI_TEYIDI.md`).

---

## 2. İLK MODEL: ZORUNLU HÜSÛSİYETLER

| No | Hüsûsiyet | Tarif | Taslak ölçü | Açık nokta |
| :-- | :-- | :-- | :-- | :-- |
| H1 | Dokunmatik ekran | Parmakla ve kalemle dokunma ile kullanım. | Çok noktalı (multi-touch) dokunmatik katman. | Dokunmatik teknolojisi (kapasitif veya kalemle birlikte çalışan EMR katmanı) H2 ile birlikte seçilecek. |
| H2 | Dijital kaleme uygunluk | Cihaz, bir dijital kalem standardını destekleyecek. | En düşük seviye kalem bile çalışsın; standart maliyete göre seçilir, kendi kalemimiz de olabilir. | Standart bağımlı değişkendir; üretici ve maliyet belli olunca seçilecek. |
| H3 | Parmakla yazılabilirlik | Kalem olmadan parmakla el yazısı yazılabilecek. | Parmakla yazı tanıma ve çizim, gecikmesi kabul edilebilir düzeyde. | Parmakla yazı ile kalem yazısı aynı kalitede olmayabilir; bu kabul edilecek mi? |
| H4 | Geniş ekran | Ekranın boyutu, okuma ve yazma için yeterli olacak. | Taslak: 10 inç ve üzeri. | Kesin boyut ve en-boy oranı kararı bekliyor. Taşınabilirlik ile ekran büyüklüğü arasında denge kurulacak. |
| H5 | Bileği ekrana yaslayabilirlik | Yazarken elin ekrana dayanması, cihazın istenmeyen dokunuşlar yapmaması. | Avuç içi reddi (palm rejection) yazılımı ve donanımı. | Avuç içi reddi hem kalem hem parmak girişinde çalışacak mı? |
| H6 | Kamerayla resim çekip üzerine not alabilme | Kamera ile fotoğraf çekilecek, fotoğraf üzerine kalemle not eklenebilecek. | Fotoğraf üzerinde katmanlı (layer) not alma. | Kamera çözünürlüğü ve belge tarama (düzeltme, kenar tespiti) isteniyor mu? |
| H7 | Ayrı notlar açabilme | Birden çok bağımsız not dosyası oluşturulabilecek. | Sınırsız değil, ama pratikte yeterli sayıda not. | Bulut hesabı ile not senkronizasyonu isteniyor mu? (H14 ile bağlantılı.) |
| H8 | Klasör sistemi | Notlar klasörlere ayrılabilecek, klasörün içinde klasör olabilecek. | İç içe klasör. | Derinlik sınırı var mı? |
| H9 | PDF çıkarabilme | Not, çizim veya fotoğraflı sayfa PDF dosyası olarak dışa aktarılabilecek. | Tek sayfa ve çok sayfa PDF. | Dışa aktarılan PDF içinde el yazısı metin aranabilir olacak mı? |
| H10 | Güneş paneli desteği | Cihaz, güneş enerjisi ile şarj edilebilecek. | **Mecburî değil.** Yerli ve verimi yüksek yeni paneller araştırılacak. | Entegre mi, aksesuar mı, hiç olmasın mı: araştırma sonrası karar. |
| H11 | 24 saat pil ömrü | Cihaz tek şarjla 24 saat kullanılabilecek. | Başlangıç hedefi 24 saat; **güncellenebilir** (renkli ekran ile birlikte yeniden tartılacak). | Kullanım profili tanımlanmadan ölçü anlamlı değildir. Rakiplerin pil süreleri araştırılacak. |
| H12 | Telefona bağlanabilirlik | Cihaz, akıllı telefonla eşleşebilecek ve veri alışverişi yapabilecek. | Bluetooth veya Wi-Fi ile eşleşme ve dosya aktarımı. | Telefon uygulaması ayrı mı geliştirilecek? Hangi işletim sistemleri? |
| H13 | Bilgisayara bağlanabilirlik | Cihaz, bilgisayarla kablosuz veya kablolu bağlanabilecek. | USB-C veya Wi-Fi ile dosya aktarımı ve gerekirse ekran yansıtma. | Hangi işletim sistemleri (Windows, macOS, Linux)? |
| H14 | Yerel depolama ve bulut eşitleme | Notlar cihazda tutulacak ve isteğe bağlı olarak buluta yedeklenecek. | Yerel depolama zorunlu. Bulut isteğe bağlı. | Bulut sunucusunu kim işletecek? Veri gizliliği ve KVKK uyumu ayrıca değerlendirilecek. |

---

## 3. İKİNCİ MODEL: İLAVE HÜSÛSİYET

| No | Hüsûsiyet | Tarif | Taslak ölçü | Açık nokta |
| :-- | :-- | :-- | :-- | :-- |
| M1 | Yapay zekâ | İlk modeldeki bütün hüsûsiyetlere ek olarak, cihaz notları anlayabilecek, özetleyebilecek ve sorulara cevap verebilecek. | Asgari işlevler: el yazısı tanıma, not özetleme, serbest metin sorusu. | Hangi işler yerelde, hangileri bulutta yapılacak? |
| M2 | Yerel yapay zekâ desteği | Yapay zekâ cihaz üzerinde, internet bağlantısı olmadan çalışabilecek. | Küçük bir dil modeli (örneğin birkaç milyar parametre) cihazda çalıştırılabilecek. | Cihazın işlemci ve bellek gereksinimi, pil ömrünü ne kadar düşürür? Ölçülmemiştir. |
| M3 | Bulut yapay zekâ desteği | Daha güçlü işler için yapay zekâ bulutta çalışabilecek. | İnternet varken isteğe bağlı kullanım. | Bulut maliyeti kimin sırtında olacak? Abonelik mi, cihaz içi ücret mi, cihaza dahil mi? |

Not: Yapay zekâ hüsûsiyetleri ilk modelde yer almaz. İlk model, yapay zekâ olmadan da bağımsız olarak satılabilir olmalıdır.

---

## 4. MALİYET HEDEFİ

| Konu | Durum |
| :-- | :-- |
| Hedef | Cihazın, piyasadaki mevcut ürünlerden çok daha ucuza üretilip satılması. |
| Rakam | Padişahın hedefi 1.000 TL (≈ 20 €). Bulunan parça fiyatlarıyla bu hedef **kapanmıyor**; ayrıntı `MALIYET_ANALIZI.md`de. Gerçek seri fiyatı teklifle öğrenilecek. |
| Rekabet kıyası | Mevcut dijital not cihazlarının fiyatları, piyasa araştırması aşamasında toplanacaktır. |

---

## 5. AÇIK SORULAR (padişahın kararını bekleyen)

1. **Ekran teknolojisi:** E-ink (elektronik mürekkep) mi, renkli LCD mi? Bu seçim pil ömrünü, yazı gecikmesini ve renk kabiliyetini doğrudan belirler.
2. **Kalem standardı:** Hangi kalem standardı destekleneceği ve kalemin cihazla birlikte mi satılacağı.
3. **Ekran boyutu:** Kesin boyut ve taşınabilirlik sınırı.
4. **Pil hedefi:** 24 saat hangi kullanım profiliyle ölçülecek? (Örneğin: saatte yüzde kaç ekran ışığı, kaç saat yazma, kaç saat kamera, kaç saat yapay zekâ.)
5. **İşletim sistemi:** Cihaz kendi işletim sistemi mi kullanacak, yoksa mevcut bir Android tabanlı sistem mi?
6. **Yapay zekânın yeri:** Yerel model için hangi işlemci ve bellek düzeyi düşünülüyor?
7. **Güneş paneli:** Cihazın tamamen güneşle mi şarj olması, yoksa yalnız pil ömrüne destek mi kastedilmektedir?
8. **Hedef kullanıcı:** Öğrenci, serbest meslek sahibi, mühendis, öğretmen mi? Kullanıcı kitlesi hüsûsiyetlerin önceliğini değiştirir.

---

## 6. TEKNİK NOT (çıkarım, henüz yoklanmamıştır)

Aşağıdaki notlar, Claude tarafından yapılmış ilk değerlendirmelerdir. Bunlar hüküm değil, sonraki aşamada yoklanacak tahminlerdir.

- **H11 ile H1, H4, H6, M2 arasında gerilim vardır.** Renkli, geniş ve kameralı bir dokunmatik ekran, işlemci ve yapay zekâ tek şarjla 24 saat çalışmakta zorlanır. 24 saatlik hedefin gerçekleşmesi için büyük olasılıkla E-ink ekran veya düşük güçlü bir işlemci gerekir. Bu, H1'in renkli ekran kanadını ve M2'nin yerel model kanadını sınırlayabilir.
- **H10 (güneş paneli)** tek başına pil ömrünü 24 saate çıkarmaya yetmeyebilir. Güneş panelinin gerçek katkısı, panel alanı ve ışık koşullarına bağlıdır, ölçülmemiştir.
- **H2 (kalem standardı)** ile **H1 (dokunmatik)** birlikte seçilmelidir. Kalem standardı, ekran katmanını belirler.
- **M1 ve M2** ikinci modeldedir ve ilk modelin tasarımını etkilememelidir. İlk modelin işlemci ve bellek kapasitesi, ikinci modelde yapay zekâ için yeterli olacak şekilde seçilmelidir.

---

## 7. SONRAKİ DOSYALAR (planlanan)

Bu dosya tamamlandıktan sonra, sırasıyla aşağıdaki dosyalar hazırlanacaktır:

1. `urun/DONANIM_GEREKSINIMLERI.md`: Bu hüsûsiyetleri karşılamak için gereken işlemci, ekran, pil, bellek, bağlantı ve kalem bileşenleri.
2. `urun/URETICILER.md`: Yerli ve yabancı üreticiler; her biri için şirket adı, üretim yeri, fiyat ve kapasite. Bilgiler kaynağı belirtilerek ve yoklanarak yazılacaktır.
3. `urun/PIYASA_ARASTIRMASI.md`: Mevcut dijital not cihazlarının hüsûsiyetleri, fiyatları ve pazar payları.

Her dosya, bu dosyadaki hüsûsiyetlere geri bağlanacak ve sayıyla karşılaştırılacaktır.
