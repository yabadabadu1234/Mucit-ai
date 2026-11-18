# MALİYET ANALİZİ: 1.000 LİRAYA KAPATILABİLİR Mİ? EKRANI KENDİMİZ ÜRETEBİLİR MİYİZ?

**Tarih:** 2026-11-18
**Esas:** Padişahın kendi kuruyla 80 € = 4.000 TL, yani 1.000 TL ≈ 20 €. Başka kur kullanılmadı; dolar fiyatları dolar olarak bırakıldı.

## 1. Bulunan en ucuz gerçek fiyatlar (üretici veya mağaza sayfasından)

| Parça | Fiyat | Kaynak / not |
| :-- | :-- | :-- |
| 7,5" E-ink, siyah-beyaz (veya +kırmızı, +sarı), çıplak modül | **20–35 $**/adet, asgarî 10 adet | Shenzhen Yingruida; dokunmatiksiz, kalemsiz |
| 5,83" siyah-beyaz, çıplak | 37 $ (tek fiyat, kademe yok) | buyepaper (Good Display mağazası); arama özetinden, sayfayı doğrudan okumadım |
| 10,3" siyah-beyaz, çıplak | 143–150 $ (1 – 10.000+ adet kademeli) | Made-in-China ilanı, yaklaşık 300 günlük; **eski** |
| 10,3" siyah-beyaz, dokunmatik + ön ışıklı | 148,90 $ | Good Display kendi mağazası |
| 10,1" E6 renkli | teklifle | Shenzhen Yingruida; yenilemesi saniyelerce sürer, yazıya uygun değil |
| 10,3" **Kaleido 3 (renkli, yazıya uygun)** | **hiçbir yerde yayımlı fiyat yok** | yalnız E Ink'ten teklifle |

## 2. 1.000 TL hakkında doğrusu

- 1.000 TL ≈ 20 €. En ucuz doğrulanmış 7,5" modülün kendisi 20–35 $ ve **dokunmatiksiz, kalemsiz, siyah-beyazdır.** Üstüne kart, pil, kasa, kalem katmanı ve montaj girer.
- Renkli ve yazıya elverişli (Kaleido 3) panelin fiyatı bilinmiyor; ama aynı boyun siyah-beyazı bile 143–150 $.
- Bu yüzden **bulduğum hiçbir parça kombinasyonu cihazı 1.000 TL'ye kapatmıyor.** Bu hüküm, elimdeki fiyatlarla verilmiştir; asıl seri fiyatları (1.000 ve üstü adet) teklif alınmadan bilinmez ve çıplak panel fiyatı seri adetle belki hatırı sayılır düşer.
- Fiyat sınıfı için bir ölçü: Boogie Board gibi LCD yazı tahtaları 14,99–29,99 $; en ucuz markasızları 5,69 $'dan başlıyor. Yani 1.000 TL, **kayıt tutmayan, tek renkli bir yazı tahtasının** fiyat sınıfıdır. Kayıtlı, klasörlü, PDF çıkaran bir E-ink defter bu sınıfa girmez.

## 3. Ekranı kendimiz üretebilir miyiz?

Ekran üç kısımdır ve hepsi ayrı bir sanayidir:
1. **Ön yüz filmi (mürekkep kapsülleri):** Kapsül kimyası E Ink'indir; tek kaynak odur (bir pazar raporuna göre dünya payı yüzde 85–90, kaynak zayıf). Film, kapsüllerin plastik şerit üzerine kaplanmasıyla yapılır.
2. **TFT arka yüz:** Her ebat için cam üstünde yarı iletken imalatıdır; ebadı arka yüz belirler.
3. **Birleştirme (lamine) ve kenar mühürleme, sürücü çipi:** Good Display'in kendi üretim sayfasında lazerle film kesme, hassas lamine ve kenar kaplama adımları sayılır.

Bulduklarım:
- E Ink, bir sayfasında hem tam modül hem **kesilmiş film** sattığını, filmin arka yüze lamine edilmesi gerektiğini yazıyor. Küçük bir alıcıya satıp satmadığı, asgarî adet ve fiyat **bulunamadı.**
- Bazı tedarikçiler, hassas lamine şartı yüzünden parçaları ayrı satmıyor, bütün olarak satıyor.
- Maliyet dağılımı (tek, zayıf kaynak, bir pazar raporu özeti): film %30–40, TFT %20–30, sürücü çipi ve kart %10–15, montaj ve test %10–15, lojistik ve gümrük %5–10, dağıtıcı kârı %10–20.

**Bundan çıkan:**
- Filmi veya TFT'yi kendimiz üretmek, E Ink'in patentli kapsül kimyasına ve bir yarı iletken tesisine girmek demektir; bunun yatırım tutarını gösteren kaynak bulamadım, **rakam yazmıyorum.** İlk safha için makul değil; E Ink'e ve Good Display'e "film ve TFT'yi ayrı satar mısınız, hangi şartla" sorusu sorulmadan karar verilmemeli.
- Padişahın sezgisi isabetli: **ayrılabilen şey kontrol kartıdır.** Çıplak panelin (örneğin Yingruida'nın TTL paralel 10,1" modülü veya Waveshare'in "PCB'siz" 10,3" ham paneli) sürücüsünü ESP32-S3 ile kendimiz yapmak maliyetin yaklaşık %10–15'lik dilimini (zayıf kaynağa göre) bize bırakır.
- Montajı kendimiz yapmak aynı şekilde %10–15 ve dağıtıcı kârını (%10–20) keser.
- Kaleido 3'ün renk süzgeci filmin üstündedir; renkli bir ekranı ayrı üretmek, filmin içine girmektir.

## 4. Gerçekçi ilk safha yolu (öneri)

1. **Doğrudan ithalat:** Türkiye perakendesiyle fabrika arasındaki fark büyük (örnek: Waveshare 10,3" HAT (D) kendi sitesinde 243,99 $; robotsepeti'nde 15.427,46 TL). Çıplak panelleri Shenzhen'den almak ilk kaldıraçtır. Gümrük vergisi **doğrulanamadı**; Ticaret Bakanlığı'ndan "bağlayıcı tarife bilgisi" alınmalıdır (8524 pozisyonu, dokunmatiklisi farklı GTİP'e düşebilir).
2. **Önce siyah-beyaz bir "öğrenci modeli"**, renkli model ikinci aşamada; çünkü renkli yazıya elverişli panelin fiyatı belirsiz.
3. **Kendi sürücü kartımız** (ESP32-S3) ve **yerli montaj** (Makro PCB kart üretimi; dizgi için Milsan veya Acces).
4. Fiyat hedefi, elimizdeki panel fiyatları (20–35 $ ile 143–150 $ arası) yerine, **teklif sonrası** sayıyla yazılacak.

## 5. Doğrudan sorulacak sorular (teklif mektubuna girecek)

- E Ink: kesilmiş film (FPL) küçük alıcıya satılıyor mu, asgarî adet, fiyat; 10,3" Kaleido 3 çıplak panel fiyatı; EMR ile birlikte çalışan konfigürasyon.
- Good Display ve Shenzhen Yingruida: 1.000, 5.000 ve 10.000 adet çıplak panel fiyatı; Kaleido 3 çıplak panel varlığı; TCON'suz (PCB'siz) teslim.
- Ticaret Bakanlığı gümrük müdürlüğü: panel modülü için GTİP ve gümrük vergisi.

## 6. Kaynaklar

- E Ink, elektronik mürekkep filmi: https://www.eink.com/tech/detail/Electronic_Ink_Film
- Good Display, üretim süreci: https://www.good-display.com/intro/18.html
- IRZ, e-paper neden pahalı: https://irz.fr/en/articles/eink-foundational-patent-manufacturing-en/
- Maliyet dağılımı (zayıf): https://www.indexbox.io/store/asia-pacific-electronic-paper-display-epd-market-analysis-forecast-size-trends-and-insights/
- Boogie Board fiyatları: https://techcrunch.com/2010/01/22/boogie-board-writing-tablet-costs-30-features-no-power-lcd-technology
- 8524 pozisyonu: https://www.dutyskip.com/hs-browse/8524-flat-panel-display-modules-whether-or-not-incorporating-touch-sensitive-screens
- Ticaret Bakanlığı ithalat SSS: https://ticaret.gov.tr/gumruk-islemleri/sikca-sorulan-sorular/ticari/ithalat
