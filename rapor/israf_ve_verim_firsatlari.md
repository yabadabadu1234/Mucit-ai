# "En çok israf nerede?" — verim satılabilecek sahalar (5 Ekim 2026)

Yöntem: 8 web araması. Rakamlar kaynak sayfalarından özetlendi; çoğu danışmanlık/pazarlama/haber kaynağıdır ve **doğrulanmamıştır**. "En çok israf" tek bir sayıyla ölçülemez; aşağıda hacim, satış kolaylığı ve tek kişilik yapılabilirlik ayrı ayrı yazılmıştır.

| Saha | Israf (bulunan) | Alıcı kim | Yazılımla çözülür mü | Rekabet / engel |
| :-- | :-- | :-- | :-- | :-- |
| Sanayide elektrik/enerji | Sanayi tasarruf potansiyeli %32 ve 25 milyar $ ([AA](https://www.aa.com.tr/tr/ekonomi/sanayide-enerji-verimliligi-uygulamalariyla-25-milyar-dolar-tasarruf-mumkun/2927426)); en az %20, bunun yarısı <2 yıl geri dönüşlü; basınçlı hava kaçakları | Fabrikalar (alıcı parayı faturadan görür) | **Evet:** saatlik tüketim verisinden analiz, tarife/puant/reaktif, yük kaydırma, kompanzasyon boyutlandırma | Danışmanlık firmaları ve tezgâh satıcıları var; yazılım kısmı manuel ve Excel'le yapılıyor görünüyor (**doğrulanmadı**) |
| Elektrik faturasında reaktif ceza | 50 kVA üstü: %20'yi aşan reaktif tüketimde ceza; 2026 birim bedeli 2,645474 TL/kVArh ([Piagrid](https://www.piagrid.com/rehber/reaktif-enerji-bedeli)); kompanzasyon sistemi 50–300 bin TL, 1–3 yılda amorti | Aynı | Evet (fatura/ölçüm analizi) | Elektrik firmaları kompanzasyon panosu satıyor |
| Perakende taze ürün/stok | Türkiye'de ~19–26 milyon ton gıda israfı; %12'si perakendede; meyve-sebze fire %15–20 ([GPD](https://www.gidaperakendecileri.org/?p=7462)) | Market zincirleri | Evet (talep tahmini, sipariş, indirim) | RobotPOS vb. "YZ ile talep tahmini" ürünleri var |
| Karayolu yük taşımacılığı | Kamyonların ~%37'si boş dönüyor (Tırport'un kendi rakamı); boşaltma bekleme ~11 saat | Nakliyeciler, yük sahipleri | Evet (eşleştirme, rota) | Tırport, Trans.eu gibi platformlar var |
| Şehir suyu kayıp-kaçak | En iyi belediye %25 (Kayseri); Muğla bölgelerinde %65 ([CNN Türk](https://www.cnnturk.com/yerel-haberler/kayseri/kayseri-su-kayip-kacak-oraninda-5-buyuksehir-su-ve-kanalizasyon-idaresi-arasinda-yer-aldi-3471787)) | Belediye su idareleri | Kısmen (SCADA verisi analizi, sızıntı konumlama) | İhale ve alım süreci yavaş |
| Tarımda sulama | %61 salma sulama; salmada %40, damlada %90–95 verim | Çiftçi | Donanım gerekir | Alıcı küçük ve dağınık |
| Tekstil kesimi | Pastal yerleşimde fire %10–15'ten %3–5'e (nesting yazılımı tanıtım) | Konfeksiyon atölyeleri | Evet (nesting) | Lectra/Gemini vb.; önceki nesting raporuna bak |

## Değerlendirme (çıkarım, kanıt değil)
- **En kolay satılan:** alıcının cebinden çıkan parayı doğrudan azaltan şey — yani fatura. Enerji/fatura analizi tek başına bir gün içinde 12 aylık faturadan tahmin edilebilir; tasarruf payı modeli bundan kurulabilir.
- **Matematiği en ağır ve hâlâ ürünleşmemiş görünen:** talep tahmini (belirsizlik altında sipariş), yük kaydırma optimizasyonu, kompresör/kompanzasyon boyutlandırma. Bu alanlar senin yeteneğine uyar.
- **Dikkat:** "İsraf büyük" ile "ürün satılır" aynı şey değildir. Önce **bir gerçek müşterinin verisiyle** tasarruf hesapla; sonra sat.

## Doğrulama adımı (1–2 hafta)
1. 5 fabrikadan (veya atölyeden) 12 aylık elektrik faturası ve mümkünse saatlik tüketim verisi iste (karşılığında ücretsiz analiz).
2. Reaktif, puant, tarife ve yük dağılımından **gerçek TL tasarrufunu** hesapla.
3. Ortanca tasarruf alıcının yıllık faturasının en az birkaç yüzde puanıysa devam et; değilse bu sahayı bırak.
4. Aynı şeyi perakendede (sipariş verisiyle) tekrarla; hangisi daha çok para çıkarıyorsa onu seç.
