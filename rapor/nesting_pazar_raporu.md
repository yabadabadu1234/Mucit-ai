# Nesting (Düzensiz Parça Yerleşim) Motoru — Pazar ve Fizibilite Raporu

Tarih: 4 Ekim 2026. Yöntem: açık kaynaklardan web taraması (13 arama, 9 sayfa okuma). **Ölçmediğim, bulamadığım ve satıcı iddiası olan her şey ayrıca işaretlidir.** Türk lirası fiyat, pazar payı ve Ankara'daki tüm atölyelerin listesi bulunamadı; uydurulmadı.

## 0. Hüküm (kısa)

**Şu hâliyle, "çıplak yerleşim motoru satacağım" fikri girmeye değmez; fakat "nesting + makine koduna çeviren (CAM/post-processor) + atölyeye ölçülü fire taahhüdü" paketi, küçük ve ucuz bir deneyle sınanmaya değer.** Sebepler aşağıda; en ağır üç bulgu:

1. **Algoritma artık sır değil, bedava.** Akademik en iyi sonuç (Sparrow, KU Leuven 2025) MIT lisanslı açık kaynak; Deepnest (GPL) ve SVGnest ticari yazılımla "başa baş" iddiasıyla ücretsiz. Motorun matematiği tek başına hendek (moat) olmaz.
2. **Satın alacak "boş koltuk" sanıldığı kadar boş değil.** Ermaksan "Lantek Inside" ile, Baykal BLS-F serisi Lantek ile, Durmazlar (Durma) Lantek-Metalix ile geliyor. Yerli makine imalatçıları zaten bir ortakla bağlı.
3. **Asıl iş yerleşim değil, yerleşimin makine koduna dönüşmesi** (giriş/çıkış noktaları, delme sırası, ortak kesim, makineye özel post-processor). Mesajdaki planda bu hiç yok; devlerin kapıyı kilitleyen yeri burasıdır.

## 1. Rakipler ve çalışma mantıkları

| Ürün | Ne | Algoritma hakkında bilinen | İddia edilen verim | Fiyat |
| :-- | :-- | :-- | :-- | :-- |
| SigmaNEST (SigmaTEK; Türkiye: BDT Yazılım) | CAD/CAM nesting, her kesim teknolojisi | "Mülkiyetli motor, matematikçi ve mühendis ekibi"; kapalı kaynak. İç yöntem **belgelenmemiş** | "Çoğu müşteri %4'ten fazla malzeme tasarrufu"(satıcı) | Bir üçüncü taraf site (laserspechub): 15–30 bin $ ilk lisans + yıllık %18–22 (**kaynağı belirsiz**) |
| Lantek Expert / Metalix / Inside | Aynı | "Dünyanın en gelişmiş algoritması"; **yöntem belgelenmemiş**; kalan parça (remnant) takibi var | "malzeme tüketimini %20'ye kadar azaltır" (satıcı pazarlaması) | aynı üçüncü taraf site: 10–22 bin $ (**kaynağı belirsiz**) |
| ProNest (Hypertherm) | Aynı | Belgelenmemiş | — | — |
| CypNest / CypCut (Bochu, Friendess, FSCUT) | Çin kontrol kartı + gömülü nesting | "Hızlı, yüksek verim", otomatik/elle/karma mod, 2000 parça tipine kadar; **iç yöntem belgelenmemiş** | — | tezgâhla birlikte |
| Nestra (yerli, tek geliştirici, GitHub) | Lazer/plazma nesting, 14 gün deneme, makineye kilitli lisans | çok çekirdekli; "plakayı sıkıştırma"; ortak kesim | 398 parça, 9 tip, 3000×1500: 40 sn, **%80,6 doluluk** (kendi örneği) | belirtilmemiş |
| FSD Online Optimizasyon (yerli, bulut) | Mobilya/panel (muhtemelen dikdörtgen) | "true-shape" **anılmıyor** | niceliksiz | iletişimle |
| Deepnest / SVGnest | Açık kaynak, GA + NFP (Burke 2006 yörünge yaklaşımı) | belgeli | "ticariyle başa baş" (kendi iddiaları) | ücretsiz; SVGnest 2019'dan beri bakımsız |
| Lapas, Nest&Cut (Alma) | Bulut abonelik | — | — | 49 $/ay, 60 $/ay'dan |
| Sparrow (KU Leuven 2025) | Araştırma kodu, Rust, MIT | çarpışmaları kademeli çözen "olurluk dizisi"; jagua-rs çarpışma motoru; keşif %80 / sıkıştırma %20, varsayılan 600 sn | makale: "en iyiyi bazen şaşırtıcı farkla geçiyor" (sayı özette yok) | ücretsiz |

**Dürüst not (sorunun "hangi algoritma, hangi formül" kısmı):** Ticari devlerin iç algoritması **dışarıdan öğrenilemez**; satıcılar yayımlamıyor. Bilinen yalnız literatürdür: NFP (Minkowski farkı) ile sınır çarpışması, Bottom-Left-Fill türevi yerleştirme, genetik algoritma/yerel arama ile sıra ve dönme araması, MIP'te ayırıcı doğrular (arXiv 1707.07177), Sparrow'un çarpışma-çözme sezgisi. Devlerin tam olarak hangisini kullandığını **bilmiyorum**; "SigmaNEST şu formüle dayanır" diyemem.

## 2. "Cari verim ne kadar?" — bulunan sayılar ve güvenilirliği

- Konu satıcı sitelerinde: manuel %60–70; temel yazılım %75–85; gelişmiş otomatik %85–92 (anebon vb. üretici blogları, **kaynaksız**).
- laserspechub.com karşılaştırması: SigmaNEST %85–90, ProNest %83–88, Lantek %82–87; **hiç dış kaynak yok, kendi analizleri**.
- Yerli: Aktif Lazer (İstanbul) "optimize edilmemiş fire %20–30, optimize %5–10"; başka sayfa "%15'ten %5'e". İkisi de pazarlama.
- Nestra'nın kendi örneği %80,6 (tek örnek, parça şekilleri belirsiz).
- **Hiçbirinin ortak bir kıyas kümesi yok.** Doluluk parçaya bağlıdır: basit parçalar %75–85, braket/gövde %65–75, karmaşık %50–65 (yine kaynaksız). Yani "%18'den %11'e" gibi bir hedef parça kümesinden bağımsız söylenemez.

## 3. Mesajdaki iddiaların yoklaması

| İddia | Bulgu |
| :-- | :-- |
| Devlerin zaafı hantal/pahalı lisans | Kısmen doğrulanabilir (fiyat aralığı var), ama kaynak zayıf; TL fiyatı yok |
| Atölyelerin %70'i Çin yazılımı kullanıyor | **Doğrulayamadım.** CypNest/CypCut'un yaygın olduğu doğru; %70 sayısı kaynaksız |
| Çin yazılımı %25 fire verir | **Doğrulayamadım.** Satıcı "yüksek verim" der, sayı yok |
| Ermaksan, Durmazlar, Baykal'a SDK satılır | **Çelişiyor:** üçü de zaten Lantek (veya SigmaNEST uyumlu) ile gidiyor. Kapı kapalı değil ama "boş" da değil; onlara geçmek için Lantek'ten iyi *ve* ucuz olmak, ayrıca entegrasyon yükü gerekir |
| "Levhada %5 daha az fire" | Lider satıcının kendi iddiası "%4'ten fazla" (ortalama tasarruf). Bunu Lantek/SigmaNEST kullanan birine karşı geçmek **gerçekçi değil**; Çin kartı veya elle yerleştirmeye karşı gerçekçi olabilir. Hangisi olduğunu atölye atölye ölçmek gerek |
| "Dörtte biri / beşte biri yazılım payı" | Taahhüde dayalı model hukuken ve ölçüm olarak zor: taban çizgisi (mevcut yazılımın sonucu) ve işin değişkenleri (parça karması, kalan malzeme) tartışma doğurur |

## 4. Ankara müşteri tablosu (eksik ve çıplak)

- OSTİM: 6.500+ işletme, 65.000+ çalışan; **metal/metal işleme sektöründe 753 firma** (ostim.org.tr). Hangilerinin lazer tezgâhı olduğu **bilinmiyor**.
- Bulduğum lazer fasonu örnekleri (web sayfaları, tam liste **değil**): Muter Lazer, Nur Metal Sac, Epa Lazer (Ermaksan Gen-5 G Force), Bersa Tech; armut.com'da "Ankara lazer kesim" altında 40'a yakın ilan.
- Kullandıkları tezgâh/yazılım: yalnız Epa Lazer'in Ermaksan'ı belli; yazılımı bilinmiyor.
- **"Ankara'daki tüm potansiyel müşteriler" listesini çıkarmadım ve çıkaramam**: kapalı veri (OSTİM firma rehberi, Ankara Sanayi Odası, Ticaret Odası kayıtları) taranmadı. Bu bir sonraki adımdır.

## 5. Piyasadaki cihazlar (nesting'in bağlandığı makineler)

- Ermaksan (Hawk Laser, Fibermak Momentum Gen-3/Gen-5, Lasermak): Lantek Inside.
- Durmazlar / Durma (HD-F, HD-TC): Lantek-Metalix, Durma Cloud, Siemens Sinumerik 840D.
- Baykal (BLS-F): Lantek, Siemens 840D.
- Çin menşeli: FSCUT/Bochu/CypCut/CypNest kontrol ve yazılımı.
- Tezgâhın "yaptığı iş": lazerle sac keser; yerleşim yazılımı **kesim yolunu ve G-kodunu da üretir**. SigmaNEST'in desteklediği makine listesi uzundur (Amada, Baykal, Bodor, Bystronic, Ermaksan, Durma…). Sizin motorunuz her makine için ayrı post-processor yazmadan satılamaz.

## 6. Matematik tarafı — neyi kendin yazarsın, neyi hazır alırsın

- NFP/Minkowski farkı: konveks parçada kolay, içbükey/delikli parçada zordur; sağlam NFP üretimi araştırma konusudur (arXiv 1903.11139). Pratikte Sparrow'un jagua-rs'i NFP'siz çarpışma tespiti yapar.
- MILP: serbest dönmeli ve gerçek parça sayısında (yüzlerce parça) çözülemez; ancak küçük örnekte alt-problem olarak kullanılır (ayırıcı doğrular, arXiv 1707.07177).
- Sezgisel/metasezgisel: GA, tavlama, yerel arama; bu sahada kazandıran, Sparrow'un gösterdiği gibi **olurluk-çözme** yaklaşımıdır.
- Sparrow **strip packing** (genişlik sabit, uzunluk minimize) çözer; sizin sorununuz çoğunlukla **çoklu levhalı bin packing** ve kalan parça yönetimidir. Bu fark gerçek ve onu eklemek özgün iş olur.
- Hesaplamalı geometri (dışbükey kabuk, Voronoi, üçgenleme): bunlar yardımcı, kritik olan sağlam sayısal poligon işlemidir (DXF'ten yay/spline/kapalı eğri okuma, tolerans).

## 7. Ticari risk ve fırsat tablosu

**Fırsat:** (a) lisans bedeli yüksek ve dolar/euro; (b) bulut/kullandığın-kadar-öde modelleri yurt dışında var ama Türkçe/yerel ödeme/kurumsal destekte yerli boşluk olabilir (**doğrulanmadı**); (c) küçük atölye Lantek/SigmaNEST'e ödemiyor olabilir.
**Risk:** (a) açık kaynak motorlar bedava; (b) yerli rakipler var (Nestra); (c) makine imalatçılarının mevcut OEM bağlantıları; (d) post-processor yükü; (e) verim farkını kanıtlamak için gerçek atölye DXF'i gerek; (f) "%X fire azalttım" iddiası, kıyas kümesi yoksa itibar riski.

## 8. Girmeye değer mi? — kapı kapı ölçü

Kararı iddiayla değil **iki haftalık ucuz deneyle** verin:

1. Gerçek DXF topla: en az 5 atölyeden 20–50 gerçek iş (parça kümesi + levha boyu + malzeme + şu an kullandıkları yazılımın çıktısı).
2. Aynı işleri üç taban çizgisiyle koştur: Deepnest-next, Sparrow (levha başına çalıştırılmış), ve eldeki yazılımın sonucu (atölyenin kendi çıktısı).
3. Ölçüt: doluluk farkı, süre, kalan parçanın kullanılabilirliği. **Geçiş eşiği (öneri):** atölyenin mevcut sonucuna göre ortanca ≥ %3 mutlak doluluk kazancı; yoksa dur.
4. Başarı çıkarsa ikinci aşama: tek bir tezgâh/kontrolcü için post-processor ve DXF kapsamı (yay, delik, ortak kesim).
5. Yalnız bundan sonra satış: atölye başına pilot, fire ölçümü sözleşmeye taban çizgisiyle yazılı.

**Kısaca:** matematik ilginç ve bunu kendin yazmak sana tatmin verir; ama para kazandıran kısım matematiğin kendisi değil, tezgâha giden kod ve ölçülü taahhüttür. Algoritma kısmı bedava rakiple yarışmak zorundadır.

## 9. Bilmediğim ve tavsiye edilen sonraki araştırma

- Ankara/OSTİM'deki lazer tezgâhı sayısı ve marka dağılımı (OSTİM firma rehberi, ASO, tezgâh distribütörleri).
- Lantek/SigmaNEST'in Türkiye TL fiyatları (BDT Yazılım, Lanteksms'e fiyat sorusu).
- Sparrow makalesinin gerçek kıyas sayıları (PDF'i tam okumadım; 1707.07177 PDF'i okunamadı).
- Çin yazılımlarının gerçek doluluğu (kendi testle ölçülmeli).

## Kaynaklar

- [SigmaNEST paketleri/özet](https://sigmanest.ib-caddy.com/packages.php); [SigmaTEK PDF](https://www.solidsolutions.co.uk/Uploaded/Documents/Partner%20Products/SigmaTEK/sigmaTEK_SigmaNest.pdf)
- [Lantek Expert](https://www.lantek.com/uk/Lantek-Expert-Nesting-Software); [Lantek Inside, Ermaksan](https://www.ermaksan.com.tr/tr-TR/medya/haberler/lantek-inside-ile-programlama)
- [Durmazlar HD-TC broşürü](https://www.durmazlar.com.tr/wp-content/uploads/2022/03/HD-TC_TR_V11.pdf); [Baykal (Haksan)](http://www.haksanmakina.com.tr/?d539%2Fcnc-fiber-lazer-kesim-makinasi.html=)
- [Nestra](https://github.com/webalet/nestra-surumler); [BDT Yazılım/SigmaNEST](https://www.bdtyazilim.com/en); [FSD Online Optimizasyon](https://www.fsdyazilim.com/urunler/online-optimizasyon)
- [Sparrow makale](https://arxiv.org/abs/2509.13329); [Sparrow kod (MIT)](https://github.com/JeroenGar/sparrow); [Deepnest](https://github.com/Jack000/Deepnest/blob/master/main/readme.md)
- [Ücretsiz/ucuz nesting karşılaştırma](https://lapas.io/blog/free-nesting-software/); [ROI karşılaştırma (kaynaksız)](https://www.laserspechub.com/guides/nesting-software-roi-comparison)
- [OSTİM](https://www.ostim.org.tr/); [Muter Lazer](https://www.muterlazer.com/); [Epa Lazer](https://www.epalazer.com/ankara-yenimahalle-ostim-osb-mahallesi-fason-metal-lazer-kesim/)
- [Robust NFP (arXiv 1903.11139)](https://arxiv.org/pdf/1903.11139); [Ayırıcı doğrular (arXiv 1707.07177)](https://arxiv.org/pdf/1707.07177)
