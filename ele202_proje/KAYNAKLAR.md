# ELE 202 Güz 2026 Projesi, 1. Kısım: Hane Aletleri Araştırmasının Kaynakları

Kaynaklar, 20 Kasım 2026 tarihinde sanal makineden (Linux, `curl` ve `pdftotext`) doğrudan açılıp metinleri okunduktan sonra yazılmıştır. Okunamayan sayfalar, en altta ayrıca ve açıkça belirtilmiştir; onlardan hiçbir sayı alınmamıştır.

Kaynakça biçimi, föyün "web sayfası" örneğine göredir.

---

## [1] Aletlerin gücü ve hesabın usulü

Grisso, R., Walker, M. A., & Ignosh, J. (2020, February 26). *Estimating appliance and home electronic energy use* (Publication 2901-9014). Virginia Cooperative Extension. Retrieved November 20, 2026, from http://pubs.ext.vt.edu/2901/2901-9014/2901-9014.html

**Neyin kaynağıdır:** Evdeki her aletin etiket gücü (watt) bu sayfadan alınmıştır: buzdolabı 725 W, bulaşık makinesi 1200–2400 W, kurutma makinesi 1800–5000 W, çamaşır makinesi 350–500 W, düz ekran televizyon 120 W, mikrodalga 750–1100 W ve diğerleri. Hesabın usulü de buradandır: gücü günlük saatle çarp, binle böl, günlük kilovatsaati bul.

**Söz:** Bu sayfa, elektriğin hangi aletten ne kadar aktığını ölçülü bir dille bildirir; kimseye fazla, kimseye eksik vermez. Rakamı bu çarşıdan alan, hesabının hangi tezgâhta tartıldığını da söyleyebilir.

**Dikkat:** Yazılan güçler *anma* gücüdür, yani azamî çekiştir; alet bunun hep altında çalışır. Sayfa bunu kendisi de söyler ve buzdolabı için, takılı kalınan süreyi üçe bölmeyi önerir; çünkü dolap açılıp kapanarak çalışır. Sayfa kullanım *süresi* vermez, yalnız iki örnekte (pencere vantilatörü ve bilgisayar için günde 4 saat) hesap gösterir.

---

## [2] Hanenin bir yıllık elektrik yükü

U.S. Energy Information Administration. (2023, June). *CE4.6.EL.ST: Annual household site end-use electricity consumption in the United States by state—averages, 2020* [Residential Energy Consumption Survey 2020]. Retrieved November 20, 2026, from https://www.eia.gov/consumption/residential/data/2020/state/pdf/ce4.6.el.st.pdf

**Neyin kaynağıdır:** Kuzey Carolina'daki bir hanenin yıllık elektrik tüketimi. Tabloda, doğrudan kilovatsaat olarak, şu satır yazılıdır: toplam 12.498; ısıtma 2.861; su ısıtma 2.895; iklimlendirme 2.470; buzdolabı 847; diğer 5.174 kWh. Ülke ortalaması 10.566 kWh'tır. Günlük ortalamaya çevrilince Kuzey Carolina için 12.498 ÷ 365 ≈ 34,2 kWh/gün çıkar.

**Söz:** Elde bir ölçü bulunmayınca el, kendi tahminine meyleder; bu tablo ise ölçüyü hanelerin kendi sayaçlarından toplamıştır. Hesabın doğruluğu, ona uzatılan bu cetvelle sınanır.

**Dikkat:** Tablo "o işi gören hanelerin" ortalamasını verir; bu yüzden alt kalemler toplamı, genel toplamı aşar ve yayıncı bunun yuvarlama ve kapsam farkından olabileceğini yazar. Rakamlar hane başınadır, tek bir aletin değil.

---

## [3] Televizyonun başında geçen vakit

U.S. Bureau of Labor Statistics. (2025, June 26). *American Time Use Survey — 2024 results* (USDL-25-1060). Retrieved November 20, 2026, from https://fraser.stlouisfed.org/files/docs/releases/atus/atus_20250626.pdf

**Neyin kaynağıdır:** Televizyon izleme süresi: 2024 verisine göre günde ortalama 2,60 saat (erkeklerde 2,82; kadınlarda 2,39). Metin, bunu boş vakitlerin en çok zaman alan işi olarak gösterir.

**Söz:** İnsanın vaktini nereye harcadığı, çoğu kez gönlünün nerede olduğunu gösterir; bu rapor ise o vaktin kaç kilovatsaat ettiğini hesaplar.

**Dikkat:** Bu rakam kişi başınadır, hane başına değildir; birden çok kişi aynı ekranı izleyince hane süresi daha kısa olabilir. Dosya, Federal Reserve Bank of St. Louis'in FRASER arşivinden okunmuştur; BLS'in kendi sitesi otomatik isteğe 403 verdiği için açılamadı, ama FRASER'daki kopya aynı yayını taşır (yayın numarası ve tarih yukarıda).

---

## Okunamayan sayfalar

Bu iki sayfa, sanal makineden de açılamamıştır ve kaynakçaya konmamıştır:

- U.S. Department of Energy, Energy Saver, "Estimating Appliance and Home Electronic Energy Use": `https://www.energy.gov/energysaver/articles/estimating-appliance-and-home-electronic-energy-use` ve `https://www.energy.gov/node/365749` adresleri HTTP 404 döndürdü. Sayfanın adresi değişmiş olabilir.
- Oregon State University'de arşivlenmiş "Energy Use of Some Typical Home Appliances" sayfası: HTTP 404.

Bunların yerine [1] numaralı Virginia Tech yayını kullanılmıştır; o, aynı hesap usulünü ve watt aralıklarını verir.

## Bu araştırmada düzeltilenler

1. Önceki mesajda televizyon süresini "2025" diye vermiştim; doğrusu, **2024 verisi, 26 Haziran 2025'te yayımlanmış sonuçlardır**.
2. Önceki mesajda Kuzey Carolina kilovatsaat değerlerini "benim dönüşümüm" diye yazmıştım; tablonun kendisi kilovatsaati doğrudan verir (yukarıda), dönüşüme gerek yoktur.
3. Aydınlatma için hiçbir kaynak bulunamadı; ışık gücü ve süresi, raporda açıkça "varsayım" diye yazılmalıdır.

## Notlar (raporda açıkça yazılması gerekenler)

- Örnek hane tablosundaki kullanım saatlerinin çoğu (kurutma, bulaşık, çamaşır, mikrodalga ve benzerleri) kaynaksızdır ve **varsayım** olarak yazılmalıdır. Su ısıtıcının 1,6 saati, [2]'deki yıllık 2.895 kWh değerinden 5000 W'a bölünerek türetilmiştir (2.895 ÷ 365 ÷ 5 ≈ 1,6 saat).
- Kaynaklı olanlar: aletlerin watt değeri [1], buzdolabının ÷3 usulü [1], televizyon süresi [3], hane ortalaması [2].
