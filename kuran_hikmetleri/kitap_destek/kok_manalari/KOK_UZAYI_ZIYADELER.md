# Kök uzayı · 100 ziyade (F 3-I 405)

Her satır `ziyade_sina.js` içinde ayrı bir sınamayla doğrulanır (`node ziyade_sina.js`, yerel sunucudan). Son koşu: **100 / 100 geçti**, sayfa hatası 0. Etiket: davranış = tarayıcıda fiilen denendi; ölçü = veri üzerinde sayıyla ölçüldü; kod = kaynakta bulunduğu denetlendi.

| # | Ziyade | Doğrulama |
| :-- | :-- | :-- |
| 1 | sûre odaları arası boşluk ≥3 | ölçü |
| 2 | kısım odaları arası boşluk ≥1.4 | ölçü |
| 3 | âyet odaları arası boşluk ≥0.6 | ölçü |
| 4 | sûre içi dolgu ≥1 | ölçü |
| 5 | kısım içi dolgu ≥0.5 | ölçü |
| 6 | sûre başlık payı 4.2 | ölçü |
| 7 | kısım başlık payı 2.6 | ölçü |
| 8 | hücreler arası iç boşluk | kod |
| 9 | yuvarlak köşe | kod |
| 10 | çizgi kalınlığı seviyeye göre | davranış |
| 11 | sûre çakışması yok | ölçü |
| 12 | kısım çakışması yok | ölçü |
| 13 | âyet çakışması yok | ölçü |
| 14 | hücre oda içinde taşmaz | ölçü |
| 15 | sıra sağdan sola: 1 ve 2. sûre sağ üstte | ölçü |
| 16 | sûre rengi mevzu kümesinden | davranış |
| 17 | aynı kümeler aynı ton ailesinde (renkli kümelerde ton farkı küçük) | ölçü |
| 18 | komşu aynı küme sûrelerde ton farkı | davranış |
| 19 | kısım rengi sûre renginden türer | davranış |
| 20 | âyet zemini sûre tonundan | kod |
| 21 | kenar rengi küme koyusu | kod |
| 22 | legend paneli var | davranış |
| 23 | legend tıkla odak | davranış |
| 24 | legend küme sayıları toplamı 98 | ölçü |
| 25 | Diğer kümesi nötr renk | ölçü |
| 26 | karanlık tema | davranış |
| 27 | tema hatırlanır (localStorage kod) | davranış |
| 28 | sistem temasına uyum | kod |
| 29 | pan sınırı: aşırı kaydırılınca harita merkezde kalır | davranış |
| 30 | zoom sınırı | davranış |
| 31 | klavye oklar | davranış |
| 32 | +/- tuşları | davranış |
| 33 | 0 tuşu sığdırır | davranış |
| 34 | ⌂ düğmesi | davranış |
| 35 | ＋ düğmesi | davranış |
| 36 | － düğmesi | davranış |
| 37 | geri düğmesi | davranış |
| 38 | Backspace geri | davranış |
| 39 | geçmiş yığını | davranış |
| 40 | animasyonlu geçiş (ara kareler) | davranış |
| 41 | çift tık odaya sığdırır | davranış |
| 42 | sûre başlığına tık sûreye gider | davranış |
| 43 | kısım başlığına tık | kod |
| 44 | âyete tık seçer ve paneli açar | davranış |
| 45 | mini harita var | davranış |
| 46 | mini haritaya tıkla gider | davranış |
| 47 | mini harita görünüm dikdörtgeni | kod |
| 48 | arama: sûre adı | davranış |
| 49 | arama: sûre no | davranış |
| 50 | arama: 2:255 | davranış |
| 51 | arama: Arapça kök | davranış |
| 52 | arama önerileri (datalist 98) | davranış |
| 53 | / kısayolu aramaya odaklanır | davranış |
| 54 | hash derin bağ | davranış |
| 55 | hash açılışta okunur | davranış |
| 56 | hashchange senkron | davranış |
| 57 | atalet | kod |
| 58 | pinch zoom | kod |
| 59 | tekerlek ctrl duyarlılığı | kod |
| 60 | breadcrumb yol canlı | davranış |
| 61 | hover ipucu: âyet meali | davranış |
| 62 | hover ipucu: kök anlamı | davranış |
| 63 | hover ipucu: sûre ve küme | davranış |
| 64 | panel: tam âyet metni | davranış |
| 65 | panel: Türkçe meal | davranış |
| 66 | panel: kök çipleri | davranış |
| 67 | panel: önceki/sonraki | davranış |
| 68 | panel: sığdır düğmesi | davranış |
| 69 | panel: ses bağlantısı | davranış |
| 70 | panel: sûre kartı | davranış |
| 71 | seçili âyet vurgusu | kod |
| 72 | seçili kök vurgusu | davranış |
| 73 | âyet numarası rozeti | kod |
| 74 | alt şerit istatistik | davranış |
| 75 | yakınlık yüzdesi | davranış |
| 76 | ölçek çubuğu | davranış |
| 77 | içindekiler paneli | davranış |
| 78 | içindekiler küme noktaları | davranış |
| 79 | içindekiler tıkla uç | davranış |
| 80 | yardım paneli | davranış |
| 81 | yükleme çubuğu | davranış |
| 82 | mekânsal ızgara (hit-test) | davranış |
| 83 | uzak görünüm önbellek katmanı | davranış |
| 84 | LOD yazı eşiği | kod |
| 85 | görüntü LRU | kod |
| 86 | atlas önyükleme | davranış |
| 87 | DPR sınırı 2 | kod |
| 88 | yalnız kirliyse çiz | kod |
| 89 | görünür dışı odalar atlanır | kod |
| 90 | galeri başlığında kök anlamı | davranış |
| 91 | galeri etiketli sayfalar | davranış |
| 92 | galeri indir bağlantısı | davranış |
| 93 | galeri ESC kapatır | davranış |
| 94 | galeri dışına tık kapatır | davranış |
| 95 | galeri sayfaya tık büyütür | davranış |
| 96 | galeri açıkken kaydırma kilidi | davranış |
| 97 | erişilebilirlik: aria-label ve canlı özet | davranış |
| 98 | PNG dışa aktarma | davranış |
| 99 | odak halkası ve mobil büyük düğme (stil) | davranış |
| 100 | legend daraltılabilir (details) | davranış |

# Kök uzayı · yeni kök getirmeyen âyetler ve meal ziyadeleri (F 3-I 412)

Bütün 6236 âyet haritadadır: 1122 âyet yeni kök getirir, 5114 âyet getirmez. Meal Hayrat Neşriyat'tandır (grav ayraç ’ ile yazılır; Arapça metne dokunulmaz). Sınama: `node ziyade2_sina.js` (27/27 geçti; eski `ziyade_sina.js` 100/100 geçti, 98 sûre sayıları 114'e çevrildi). Her madde, sayılan âyetten değil **niteliğinden** ayrı bir ziyadedir.

| # | Ziyade (vasıf) | Sınama |
| :-- | :-- | :-- |
| 1 | Yeni kök getirmeyen âyetler de oda olarak haritada (6236 = 1122 + 5114) | ölçü |
| 2 | Tür ayrımı: dolgu rengi farklı (getiren koyu, getirmeyen soluk) | davranış (piksel) |
| 3 | Getirmeyen oda kesik çizgili, getiren oda düz ve kalın çizgili | kod |
| 4 | Getirmeyen oda taramalı (çapraz çizgi); uzak katmanda da | kod |
| 5 | Meal her âyet odasının içinde, Arapçanın altında | ölçü |
| 6 | Meal bloğu odaya sığar; yükseklik formülle eşit | ölçü |
| 7 | Rozet: getirende +N, getirmeyende ∅ | kod |
| 8 | Tür süzgeci (hepsi · yeni kök · kök yok), K tuşu | davranış |
| 9 | Efsane: iki tür ve sayıları (1122 · 5114) | davranış |
| 10 | Sûre paneli: yeni kök getiren ve getirmeyen âyet sayısı | davranış |
| 11 | Kısım başlığında yeni/toplam oranı; toplamlar 1122 ve 6236 | ölçü |
| 12 | Getirmeyen âyet paneli: ○ kök çipleri ve ilk geçişe bağ | davranış |
| 13 | Getiren âyet paneli: ● çip sayısı yeni kök sayısına eşit | davranış |
| 14 | Kök hazinesi ilerlemesi (kaç/1830, yüzde, çubuk); son âyette 1830 | ölçü |
| 15 | N tuşu: sonraki yeni kök getiren âyet | davranış |
| 16 | P tuşu: önceki yeni kök getiren âyet | davranış |
| 17 | Panelde önceki ve sonraki yeni kök âyeti, mesafesiyle | davranış |
| 18 | Fare ipucu: âyetin türü ve yeni kökleri | davranış |
| 19 | Alt şerit: görünen âyetlerden kaçı getiren, kaçı getirmeyen | davranış |
| 20 | Meal araması (mealde geçen kelimeyle âyet bulma) | davranış |
| 21 | Bağ (hash) süzgeci taşır: `#f=yeni&a=2:30` | davranış |
| 22 | Kök hazinesi eğrisi (âyet sırasıyla kök edinimi); tıkla, oraya git | davranış |
| 23 | Kök ipucu: Kur'ân'da kaç âyette, kaç geçiş | davranış |
| 24 | Âyet metninde yeni kök kelimesi altın ve kalın | davranış |
| 25 | Canlı özet (ekran okuyucu) âyetin türünü bildirir | davranış |
| 26 | Kelime–kök hizası: âyetlerin ≥ %96'sında kelime başına kök durumu | ölçü |
| 27 | Eğri imleci: seçili âyetin yeri kırmızı çizgiyle | kod |
