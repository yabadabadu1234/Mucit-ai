# VERİ DEFTERİ (F 3-I 261, 262) -- gerçek / hafıza / yoklanamadı

## Gerçek veri (ILO ILOSTAT = TÜİK HİA, 2025; `veri_ilo/`)
- Nüfus, işgücü, istihdam, işsiz, kayıt dışı çalışan: yaş bandı 15-24 … 65+ (`POP/EAP/EMP/UNE/NIFL.csv`).
- Kayıt dışı çalışan 8 659,8 bin: tarım 3 889,5 bin, tarım dışı 4 770,4 bin (%55,1) (`NIFL_ECO.csv`). **Yaşa göre tarım ayrımı yok.**
- İstihdam durumu: ücretli/yevmiyeli 23 353,0 · işveren 1 515,7 · kendi hesabına 5 234,0 · ücretsiz aile işçisi 2 463,7 bin (`EMP_STE.csv`).
- Yaş × eğitim (nüfus, ISCED 2011): 15-24'te 4 950 bin ortaokul, 4 801 bin lise, 753 bin lisans; 25-34'te lisans+yükseklisans+doktora 5 631 bin (`POP_EDU.csv`).
- NEET 15-24: 2 684,3 bin.
- Girişim hayatta kalma (haber aktarımı, TÜİK bülteni birebir okunmadı): 1 yıl %75-78, 5 yıl ~%41,6.
- Kazanç: DİSK-AR aktarımı (Euronews, veri kümesi adı yok; 2022): ücretlilerin %18,1'i asgari ücretin 2 katından fazla alıyor, %33,8'i asgari altında.

## Karar (padişah, F 3-I 262)
Memnun = asgarinin 2 katı ve üzeri; kayıt dışı tarım sayılmaz; ücretsiz aile işçisi namzet.

## Uygulanan (havuz2.py)
m = 0,181 (üst sınır sayılır: asgari ücret payı yıllar içinde arttı, 2022 sonrası oran yoklanamadı); kayıt dışı tarım dışı payı tüm yaşlara %55,1 uniform (**yaşa göre yoklanamadı, kaba**); m tüm kayıtlı istihdama uygulandı (işveren ve kendi hesabına kayıtlılar maaşlı değil, **ayrım yoklanamadı**: pay m olduğundan yüksek çıkabilir, havuz biraz küçük kalır).
Sonuç: havuz 48 851 bin, 16-34 yaş 19 871 bin. Ücretsiz aile işçisi toplam 2 464 bin, tarımda ~2 066 bin (2018 oranı 2,6/3,1 ile çıkarım, yaş dağılımı yok) ayrıca eklenir.

## Yoklanamadı
Eğitim × işgücü durumu (okuyor mu); kazanç dağılımı 2023-2025 ve yaşa göre; kayıt dışının yaşa × sektör kırılımı; ilk yıl geliri ve iflas oranı gençler için; nüfus projeksiyonu 2026-31.

---
# EK (F 3-I 263): padişahın verdiği Orta Vadeli Program/Ekonomik Görünüm ekleri ve yeni bulgular

## Okuma durumu (sayıyla)
- II. İstihdam, Verimlilik, Ücretler ve Gelir Dağılımı (20 sayfa): **baştan sona okundu** (satır metni `veri_ek/`).
- Ekonomik Görünüm Eylül 2026 (82 sayfa): sayfa 1-46 okundu (makro göstergeler, OVP hedefleri, iç ticaret, mal ticareti); 47-82 (hizmet ticareti, yatırım ortamı, serbest bölge, ticaret anlaşmaları) **okunmadı**, modelle ilgisi görülmediği için; ilgisizliği okunmadan söylenmiştir.
- V. Fiyatlar (15 sayfa): sayfa 1-10 okundu; 11-15 okunmadı.
- IV. Kamu Maliyesi (23 sayfa): sayfa 1-7 okundu (borç, merkezî bütçe gelir/gider tabloları); tablo ayrıştırması bozuk, gelir vergisi ve prim kalemleri **güvenle çıkarılamadı** (yoklanamadı).
- I. Üretim ve Yatırım, III. Dış Ticaret ve Ödemeler Dengesi, VI. Mali Piyasalar: **okunmadı** (mikro mükellefiyet modeline girdisi yok; okunmadan söylenmiştir).
- DİSK-AR Asgari Ücret Araştırması 2026 (159 sayfa, Aralık 2025): sayfa 1-21 (genişletilmiş basın özeti) okundu; Bölüm 3-4 ayrıntıları okunmadı.

## Yeni gerçek veri
- Gelir dağılımı (TÜİK GYKA, OVP eki Tablo II.11-17; gelir referansı önceki yıl): Gini 2025 anketi %0,415 (eşdeğer %0,410); P80/P20 7,9; yıllık hanehalkı kullanılabilir gelir ortalaması en düşük %20: 200 100 TL, en yüksek %20: 1 587 404 TL, ortalama 662 414 TL; eşdeğer birey geliri en düşük %10: 85 090 TL/yıl (yaklaşık 7 090 TL/ay), en düşük %20: 106 058 TL/yıl.
- Göreli yoksulluk (eşdeğer gelir medyanının %50'si): sınır 120 575 TL/yıl, 10,93 milyon kişi (%13,0); %60: 144 690 TL/yıl, 17,36 milyon kişi (%20,6).
- İşgücü (2026-II): işsizlik %7,6; genç (15-24) işsizlik %13,3 (kadın %18,3, erkek %10,7); işgücüne katılma 15-24: kadın %32,4, erkek %59,3; istihdam 32 656 bin; ücretli 23 612 bin, kendi hesabına/işveren 6 699 bin, ücretsiz aile işçisi 2 345 bin.
- Ücret: DİSK-AR (TÜİK HİA mikro verisi, 2024): ücretlilerin %46,7'si (8 359 bin) asgari ve altında; %62,5'i asgari +%20 ve altında; **asgarinin iki katından fazla alan yalnız %12,7**; kayıt dışı ücretlilerin %40'ı asgarinin yarısı ve altında, %85,3'ü asgari +%5 ve altında. (Taban: ücretlilerin 17 899 bin; ikincil kaynak, mikro veri yoklanmadı.)
- Enflasyon: TÜFE yıllık 2026-Eylül %29,73; hizmet %37,65; 2025 yıl sonu %30,89. OVP: büyüme 2026 %3,3, 2027 %4,2; işsizlik 2027 %8,0.
- Girişim: MERSİS aktif şirket + ticari işletme + şube 2 673 735 (2026-Eylül), 2 594 461 (2025).

## Uygulanan (havuz3.py)
m değişti: halinden memnun = ücretlilerin %12,7'si (asgarinin 2 katı ve üzeri) ≈ 2 273 bin, yaşlara kayıtlı istihdam payıyla dağıtıldı (yaşa göre kazanç yoklanamadı). Sonuç havuz 50 905 bin; 16-34 yaş 20 742 bin; ayrıca ücretsiz aile işçisi (tarım) ~2 066 bin.

## Hâlâ yoklanamayan
Yaşa göre kazanç; kamu çalışanlarının (memur) memnun sayılıp sayılmayacağı; ilk yıl geliri ve işi bitirme oranı (genç, sermayesiz); kayıt dışının yaşa × sektör kırılımı; eğitim × işgücü durumu.

---
# EK-2 (F 3-I 264): TÜİK Veri Portalı bültenleri 54058 ve 57986 -- dönüştürücü ile okundu

## Dönüştürücü
Portal bir React sayfasıdır; düz istekle içerik gelmez. `veri_tuik/render.js` (başsız Chromium, yalnız ara CA'nın SPKI özetine güvenir; TLS doğrulaması kapatılmadı) sayfayı çizer ve `/api/tr/press/<no>` yanıtını yakalar; `veri_tuik/dl2.js` bültenin xls tablolarını indirir; xlrd ile TSV'ye çevrildi. 26 tablonun 26'sı okundu (18 girişim demografisi 2024, 8 işgücü Haziran 2026).

## Girişimcilik ve İş Demografisi 2024 (bülten 54058, 16 Aralık 2025) -- gerçek veri
- Hayatta kalma (doğum kohortuna göre): 1 yıl: 2019 %80,6 · 2020 %78,3 · 2021 %77,2 · 2022 %75,2 · 2023 %78,3. 2 yıl: %64,4 · %62,9 · %59,2 · %58,6. 3 yıl: %54,9 · %52,1 · %49,3. 4 yıl: %47,0 · %44,8. **5 yıl (2019 kohortu): %41,2.** İstihdam bazında 1 yıl: %85,2 · %81,4 · %81,2 · %79,5 · %83,6.
- Doğum: 2024'te 633 146 girişim (%15,8), 996 550 istihdam; ölüm 2022'de 482 298 (%12,9). Doğanların **%77,5'i gerçek kişi** (490 458; 2024), ölenlerin %85,0'ı gerçek kişi (410 143; 2022).
- Gerçek kişi (şahıs işletmesi) stoku: 2 915 107 (2024); işletme başına ortalama 2,05 istihdam; ortalama yıllık ciro 2 744 516 TL (2024, **ortalamadır; çarpık dağılım, medyan yoktur; ciro gelir değildir**).
- Hızlı büyüyen girişim oranı %14,4; ceylan %2,4 (2024).
- Kuruluş yılına göre stok (2024): 2021 ve sonrası kurulanlar girişimlerin %33,5'i ama cironun yalnız %13,5'i, istihdamın %17,4'ü.
- Çıkarım (ayrı yazıldı): gerçek kişi ölüm payı %85 iken stok payı yaklaşık %73 olduğundan gerçek kişi ölüm hızı genel ortalamanın yaklaşık 1,16 katıdır; gerçek kişiye mahsus kohort hayatta kalma tablosu **yoktur** (yoklanamadı).

## İşgücü İstatistikleri Haziran 2026 (bülten 57986) -- gerçek veri
- 15-24 yaş, 2026 Haziran (aylık, mevsim arındırması yok): nüfus 11 405 bin, işgücü 5 516, istihdam 4 771, işsiz 745, işgücü dışı 5 890. Erkek: nüfus 5 895, işgücü 3 609, istihdam 3 212, işsiz 397, dışı 2 286. **Kadın: nüfus 5 510, işgücü 1 907, istihdam 1 559, işsiz 348, dışı 3 603** (kadınların %65,4'ü işgücü dışında).
- Mevsim arındırmalı 15+ (Haziran 2026): işsizlik %7,6; atıl işgücü oranı %28,8; işsiz+potansiyel işgücü bütünleşik oranı %19,2.

## Kamu çalışanları (F 3-I 264 (3))
- SGK 2026 Haziran: 4/c (memur) 3 715 638 (ikincil kaynak; resmî tablo okunmadı). En düşük memur maaşı Temmuz 2026'da aile yardımı dâhil 70 224 TL ≈ net asgarinin (28 075,5) 2,5 katı (hesap benimdir; bekâr memurda altında olabilir). Padişah kararı: 2 asgariyi geçen kamu çalışanı modele geçmez; memur havuzdan **tamamen** çıkarıldı. Kamu işçisi (4/d) sayısı ve ücreti yoklanamadı; çıkarılmadı.

## Uygulanan (havuz4.py, yaş × cins)
Havuz **47 189 bin** (kadın 24 509, erkek 22 680); 16-34 yaş 19 471 bin. Çıkarılanlar: memur 3 716 bin (25-64, kayıtlı istihdam payıyla yaş-cinse dağıtım -- yaş ve cins dağılımı yoklanamadı), özel sektör memnunu %12,7 ≈ 2 273 bin. Kayıt dışı tarım dışı payı cinse göre (erkek %59,7; kadın %48,2). Ücretsiz aile işçisi (tarım) ayrıca ~2 066 bin.

---
# EK-3 (F 3-I 265): SBB kamu istihdamı, ASMMMO, KOSGEB ÖİK raporu, Terzibaş (2023)

## 1. SBB Kamu Sektörü İstihdam Sayıları (xlsx, Mart ve Haziran 2026 sayfaları baştan sona okundu) -- gerçek veri
- Haziran 2026 genel toplam **5 417 126** (fiilî dolu): kadrolu 3 582 025 · sözleşmeli 419 801 · sürekli işçi 1 267 501 · geçici işçi 50 418 · diğer 97 381. Mart 2026 toplam 5 368 945 (kadrolu 3 534 981). Belediye şirketleri (BİT) işçisi 696 178.
- SGK 4/c (3 715 638) ile SBB kadrolu (3 582 025) arasındaki fark açıklanamadı (tanım farkı olası; çıkarım).
- **Yoklanamayan:** kamu işçisi (sürekli/geçici), sözleşmeli ve BİT işçisinin ücreti 2 asgariyi geçiyor mu; yaş × cins dağılımı. Bu yüzden F 264 (3) yalnız kadrolu/memur için kesin uygulanır; diğerleri padişaha sorulacak açık kalemdir.

## 2. ASMMMO UyeIstatistikleri.pdf -- amaca uymadı
Yalnız SMMM odası üyeleri (12 339; 25-35: 1 140 · 35-45: 4 602 · 45-55: 3 413 · 55+: 3 184). Kamu çalışanının veya genel nüfusun yaş dağılımı **değildir**; modele girmez.

## 3. Terzibaş (2023, SOBİNARDER) -- TOBB sicil verisi
Gerçek kişi ticari işletmede kapanan/kurulan oranı 2016-2022 ortalaması %55 (yıllar %37-69); limited %13,7; anonim %21,7. Makalenin "yıllık hayatta kalma %98-99" tablosu yalnız resmî sicil kapanışını ölçer; TÜİK kohort ölçüsüyle (1 yıl %75-80) çelişir, **TÜİK esas alınır.** Sonuç sayfaları (s.19-22) okunmadı.

## 4. KOSGEB 12. KP ÖİK Raporu (KOSGEB adresi 404; SBB kopyası, 136 sayfa) -- okunan: içindekiler, PDF s.53-65
- 2021 mikro işletmelerin çalışan dağılımı (Tablo 8): 0 çalışan 1 737 585 (%53,45) · 1 çalışan 812 149 (%24,98) · 2-3: 447 149 (%13,76) · 4-9: 253 742 (%7,81); toplam 3 250 625.
- Çalışan başına katma değer: KOBİ ~27-29 bin $, büyük ~96-123 bin $ (3,3-4,4 kat).
- Şirket açılış/kapanış (TOBB, Tablo 14): 2022 açılan 140 229, kapanan 23 170.
- KOBİ niteliğinde girişim hayatta kalma: 1 yıl %70 (2020) · 2 yıl %67,0 · 3 yıl %55,5 · 4 yıl %46,5 · 5 yıl %41,3 (2016). Doğum kohortu 2014-2016: 5 yıl %39,3-41,3 (TÜİK 2024 bülteniyle uyumlu: %41,2).
- Hızlı büyüyen girişim 2021: 25 426 (istihdama göre); girişim yatırımı konusu (Startups Watch) bu modele girmez.
- **Okunmayan: s.1-52 ve s.66-136** (özellikle 3.8 heterojenlik, Tablo 33 segmentasyon). Okunmayandan sonuç çıkarılmadı. Rapor ilk yıl gelirini **vermiyor** (okunan kısımda).

---
# EK-4 (F 3-I 266): Hazine ve Maliye genelgeleri (Temmuz 2026) ve TÜİK Gelir Dağılımı 2025 (bülten 53993)

## 1. Genelgeler (taranmış PDF; metinsel katman yok, sayfalar görüntü olarak baştan sona okundu)
- **Mali ve Sosyal Haklar, Sıra 5 (3.7.2026):** 1.7–31.12.2026 için memur aylık katsayısı 1,575512, taban aylık katsayısı 25,794915, yan ödeme katsayısı 0,499649. Sözleşmeli (399 KHK 3/c) ücret tavanı **86 231,60 TL**; BKK sözleşmeli (3. madde) tavanı 76 873,55 TL; sözleşmeli ve KİT/BİT ücretleri **%13,52** artırıldı; 2002/3729 kapsamında ortalama ücret toplamı üst sınırı **156 920,53 TL**; kıdem tazminatı tavanı 73 729,87 TL; birinci derece şube müdürü net 102 085,23 TL.
- **Mahalli İdare Sözleşmeli Personeli, Sıra 7 (3.7.2026):** 5393 sayılı Kanun m.49 kapsamı sözleşmelilerin unvan bazında **net aylık ücret tavanları** (tam zamanlı): çocuk eğitimcisi/eğitmen/kameraman 42,3-44,5 bin; sağlık meslek lisansiyeri 44,4-50,7 bin; teknisyen/teknik ressam 42,8-51,9 bin; fizikçi/kimyager/istatistikçi 57,1 bin; ekonomist 41,6 bin; mimar/mühendis/şehir plancısı 63,6 bin; avukat 57,6 bin; hukuk müşaviri 73,5 bin; tabip 61,0 bin; uzman tabip 67,7 bin; kısmi zamanlı en çok 25,4 bin. Ek ödeme (brüt) oranı %85-%200, tutar 12 722-29 935 TL; ek ödeme vergi ve sigorta primine tabi değildir.
- **Hesabım (çıkarım):** net asgari ücret 28 075,5 TL → 2 asgari = **56 151 TL/ay**. Mahalli idare sözleşmelisinde tam zamanlı tavan 2 asgarinin **altında kalan unvanlar çoğunluktur**; üstü yalnız avukat, hukuk müşaviri, tabip, uzman tabip, mühendis, mimar, şehir plancısı ve benzeri lisans meslekleridir ve bunlar **tavandır, fiilî ücret değildir** (fiilî ücret ve unvan dağılımı yoklanamadı). Ek ödeme (net, vergisiz) tavana ilâve edilmediğinden bu rakam 2 asgari kıyasında ek ödemeyi içermez.
- **Yoklanamadı:** kamu işçisinin (4/d) ve BİT işçisinin fiilî ücreti (ortalama ücret toplamı üst sınırı brüttür ve toplu sözleşme ile belirlenir; asgarinin kaç katı olduğu bilinmiyor); sözleşmeli ve işçilerin yaş dağılımı.

## 2. TÜİK Gelir Dağılımı İstatistikleri 2025 (bülten 53993, 26.12.2025; gelir referansı 2024; sayfa tam okundu)
- En yüksek %20'nin payı %48,0; en düşük %20'nin %6,4; Gini 0,410 (brüt gelirde 0,422); P80/P20 7,5; P90/P10 12,9.
- Yıllık ortalama hanehalkı kullanılabilir geliri 662 414 TL; eşdeğer fert geliri 332 882 TL (2024: 187 728 TL; artış %77,3).
- **Yıllık ortalama esas iş geliri (2025 bülteni, 2024 geliri):** yükseköğretim 566 839 · lise ve dengi 376 932 · lise altı 290 323 · okul bitirmeyen 183 900 TL. İşteki duruma göre: işveren 1 204 791 · ücretli/maaşlı 379 047 · **kendi hesabına 348 045** · yevmiyeli 186 682 TL. Sektör: hizmet 426 045 · tarım 237 461 TL.
- Gelir türü payı: maaş ve ücret %49,7, müteşebbis %18,3 (tarım %15,6), sosyal transfer %18,2.
- **Hareketlilik (panel):** önceki yıl işsiz olanların %38,7'si ertesi yıl çalıştı; çalışanların %90,3'ü çalışmaya devam etti; işgücü dışı olanların %10,1'i işgücüne katıldı. En alt %10'da olanların %58,9'u aynı grupta kaldı, %19,8'i bir gruptan fazla yükseldi; en üst %10'da olanların %68,1'i kaldı. Bu, padişahın genç seyri ölçütü ("kalıcı üst segmente geçememe") için **tarafsız (kanunsuz) karşılaştırma tabanıdır**: yıllık geçiş matrisi mevcut.
- **Yoklanamadı:** yaşa göre gelir dağılımı ve yaş × cins esas iş geliri (bültende yok; tablolar 7 adet, yalnız eğitim, sektör ve hanehalkı tipi kırılımı var). Bültendeki tabloların xls dosyaları henüz indirilmedi.

---
# EK-5 (F 3-I 267): işsizlerin yaşa göre dağılımı ve padişahın geçiş oranları
Kaynak: ILO ILOSTAT (TÜİK HİA 2025), `veri_ilo/UNE.csv`, 5 yıllık bantlar; tek yaş için bant içi tekdüze dağılım **varsayımı** (ölçüm değil). Resmî işsiz, bin: 16-21 yaş 442,6 · 22-29: 881,8 · 30-39: 693,1 · 40+: 895,6. Padişahın tahmini (22-29: %60, 30-39: %40) → 529,1 + 277,2 = **806,3 bin kişi**. Hesap: `katilim_egrisi.py`, çıktı `katilim_egrisi_out.txt`.
Haberdar olma gecikmesi için ölçülmüş veri **yoktur**; Bass yayılma eğrisi yalnız **duyarlılık** olarak koşturuldu (q=0,3 benim varsayımım): ilan şiddeti p=0,02 iken 3. yıl sonunda haberdar payı %9, p=0,05 → %21, p=0,15 → %49, p=0,40 → %81.

---
# EK-6 (F 3-I 270, 271): TÜİK Yıllık ve Bölgesel İşgücü İstatistikleri 2025 (bülten 57996, 25.3.2026) + SBB iki rapor
Tablolar: 28 xls indirildi (`veri_tuik/isgucu_2025_57996/`), il düzeyi (İBBS-3, 81 il + Türkiye) işsizlik, istihdam, katılım 2022-2025 `il_duzeyi_2022_2025.csv`. Grafikler görüntü olarak çizilip görüldü (F 271); il tahminleri **örneklem tahminidir, güven aralığı geniştir** (ör. Tekirdağ istihdam oranı 2024 %56,0 → 2025 %52,1).

## Türkiye 2025 (bülten)
İşsizlik %8,3 (2 966 bin) · istihdam 32 566 bin, oran %49,0 · işgücü 35 533 bin (−200 bin), katılım %53,5 (−0,7 puan) · kadın istihdam oranı %32,1, erkek %66,4 · genç (15-24) işsizlik %15,3 (kadın %22,1) · **atıl işgücü %29,7 (+3 puan)** · sektör payı: tarım %14,0, sanayi %20,2, inşaat %6,8, hizmet %59,0; 2025'te tarım −267 bin, sanayi −168 bin, inşaat +62 bin, hizmet +318 bin · **ne eğitimde ne istihdamda** 15-24: %23,3 (2 684 bin), 15-29: %26,3 (4 711 bin).
İl uçları 2025: işsizlik en düşük Ardahan %4,0, en yüksek Hakkari %13,8 (Van %12,7, Yalova %11,8, Muş %11,7, Adana %11,6); istihdam oranı en yüksek Artvin %58,1, en düşük Hakkari %32,9 (Muş %35,7, Van %37,0, Siirt %37,3).
Sosyal güvenliğe kayıtsız (esas iş): 2025'te 8 344 bin (istihdamın %25,6); ücretli 2 843 · işveren 243 · kendi hesabına 3 111 · ücretsiz aile işçisi 2 148 bin.
İşgücü dışı 2025: 30 862 bin; ev işleriyle meşgul 5 844 bin (2021: 9 917), çalışamaz halde 7 690 bin (2021: 4 998), "diğer" 4 665 bin (2021: 2 925). Sütun başlıkları birleşik olduğundan potansiyel işgücü alt kırılımı **ayrıştırılamadı**.

## SBB İşgücü Piyasası Makro Analizi 2026-I (14 sayfa, tamamı okundu; grafikler görüldü)
2026Ç1: büyüme %2,5 iken istihdam −%1,4 (−449 bin, 31 480 bin); MEA istihdam çeyreklik −301 bin; MEA katılım %52,6 (−0,7), MEA işsizlik %8,2, **atıl işgücü %30,4**; HİA tablosunda 2026-I ham katılım %51,6, atıl %31,9. Yıllık: hizmet +33 bin, tarım −158, sanayi −238, inşaat −86 bin. Konaklama-yiyecek −79 bin, idari-destek −71 bin, mesleki-bilimsel-teknik +68 bin (MEA çeyreklik). Grafik 3 (görüldü): emek yoğun imalat 2023Ç3'ten beri imalat genelinden ayrışmış, imalat KKO ve istihdama duyarlı KKO düşüyor; inşaat istihdamı 2025 ortasından beri geriliyor. Kamu istihdamı 5 369 bin (%16,7). İşsizlik sigortası alan 480 928 (Mayıs 2026). Kutu: istihdamın büyüme esnekliği uzun dönemde yükselmiş, tarımda büyümeden bağımsız yapısal düşüş.
## SBB Haftalık Gelişmeler 9 Ekim 2026 (107 sayfa; yalnız işgücü ve asgari ücret sayfaları 22 ve 25 görüntü olarak okundu, kalan sayfalar okunmadı)
Ağustos 2026 (ham): işgücü 36 083 bin, istihdam 33 301, işsiz 2 782, katılım %53,8, işsizlik %7,7; MEA: katılım %52,5, istihdam oranı %48,4, işsizlik %7,8. Asgari ücret 2026 (sayfa 25, 260 dpi görüntüden okundu): brüt 33 030; net 28 075,5; işverene maliyet 40 874,6 TL. İşveren kesintisi 7 844,6 (SSK 7 184,0 + işsizlik 660,6); işçi kesintisi 4 954,5 (SSK 4 624,2 + işsizlik 330,3; gelir ve damga vergisi 0). Net/işveren maliyeti %68,7; **toplam kesinti/işveren maliyeti %31,3**; toplam kesinti/brüt %38,8; işveren payı/brüt %23,8; işçi payı/brüt %15,0. 2026 artışları: işveren maliyeti %28,0, net %27,0, toplam kesinti %32,6.
## ÇSGB e-bülten sayfası: en güncel Çalışma Hayatı bülteni Ocak 2026 (PDF), Ağustos/Eylül 2026 yalnız "ücret ve sendikal" serisi; "81 İle İlişkin Genel Göstergeler" tematik bülteni listede var. **Bu turda okunmadı.**

## EK-7 (F 3-I 272): ATIL İŞGÜCÜ KİŞİ SAYISI VE ÇARE MODELİ GİRDİLERİ

| Girdi | Değer | Kaynak/Durum |
| :-- | :-- | :-- |
| İşgücü / işsiz 2025 | 35 533 / 2 966 bin | TÜİK t27 |
| Potansiyel işgücü 2025 | 5 129 bin (2 608 + 2 348 + 173) | t05, 2021'de 3 275 bin |
| Atıl işgücü oranı 2025 | 29,7% (erkek 24,0; kadın 39,1) | t15 |
| Zamana bağlı eksik istihdam | 3 982 bin | **türetildi**, iki bütünleşik oranla kontrol tuttu |
| 15-29 NEET | 4 711 bin (kadın 3 233) | t03 |
| Uzun süreli işsiz (1 yıl+) | 537 bin | t13 |
| İşsizden İŞKUR'a başvuran | 1 096 bin | t11 |
| Kayıt dışı çalışan | 8 344 bin (tarım 3 735; ücretli 2 843) | t19 |
| Asgari ücret SGK getirisi | 12 799,1 TL/ay | SBB s.25 |
| GSMH 2025 | 62 288 195 804 bin TL | TÜİK KSH |
| Yoklanamadı | tedbir esnekliği; ölü ağırlık; ilçe/il atıl oranı; 2021→2025 sınıflama kayması | -- |
