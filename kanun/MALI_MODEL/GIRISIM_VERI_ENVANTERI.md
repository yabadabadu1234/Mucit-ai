# GİRİŞİM VERİ ENVANTERİ (TÜİK, yüklenen 13 dosya)

Kaynak: `veri/girisim_dokum.txt` (500 satır, baştan sona okundu). Her dosyanın okunma durumu ve modele bağlanan sayılar burada tutulur. Sayılar tablo değerleridir; türetilenler "(türetildi)" diye işaretlidir.

## 1. Dosya dökümü

| # | Dosya kısa adı | İçerik | Okundu | Modele bağlanan |
| :-- | :-- | :-- | :-- | :-- |
| 1 | `19242e77` | Doğan girişimler, hukuki durum (2015–2024) | evet | doğum sayısı, hukuki dağılım (aşağıda) |
| 2 | `2c2bdd47` | Faal girişimler, sektör (2015–2024) | evet | yalnız bağlam; doğan değil, kullanılmadı |
| 3 | `8e7f8e06` | Doğan girişimler, sektör (2015–2024) | evet | sektör karışımı (SEKTOREL_DOGUM_DAGILIMI.md) |
| 4 | `a32f71ab` | Doğan girişim, sektör içi pay (2015–2024) | evet | sektör içi doğum oranı (aşağıda) |
| 5 | `5f5697a6` | Ceylan (gazelle) girişim, sektör (2016–2024) | evet | bağlam |
| 6 | `73ae6f2a` | Ölen girişim, sektör dağılımı (2013–2022) | evet | ölüm karışımı (aşağıda) |
| 7 | `2c8ada63` | Ölen girişim, sektör içi pay (2013–2022) | evet | bağlam |
| 8 | `80827cfa` | Doğum göstergeleri (2015–2024) | evet | doğum sayısı kontrolü |
| 9 | `cf8e1e33` | Faal girişim, kuruluş yılı (2024) | evet | yaş yapısı (aşağıda) |
| 10 | `d7c0c28d` | Hızlı büyüyen ve ceylan girişim oranları (2015–2024) | evet | bağlam |
| 11 | `e514e2d6` | Ölen girişim, hukuki durum (2013–2022) | evet | ölüm hukuki karışımı |
| 12 | `f361f6a7` | Hayatta kalma göstergeleri, doğum kohortları (2019–2023) | evet | **genç seyri kalibrasyonu (genc3.py)** |
| 13 | `f9ca6980` | İmalat doğan girişim, teknoloji düzeyi (2015–2024) | evet | imalat içi kırılım |
| 14 | `9953c0b2` | Hızlı büyüyen girişim, sektör (2015–2024) | evet | bağlam |

Not: `2c2bdd47` faal girişimleri verir; doğan girişim sanılmamalıdır. `f361f6a7` kohortu ile `8e7f8e06` doğum serisi birbirini doğrular (aşağıda 2.1).

## 2. Ana sayılar

### 2.1 Hayatta kalma (f361f6a7) ve çapraz kontrol

Girişim oranı = kohort içinde hayatta kalan / doğan.

| Kohort (doğum yılı) | Doğan | 1 yıl | 2 yıl | 3 yıl | 4 yıl | 5 yıl |
| :-- | --: | --: | --: | --: | --: | --: |
| 2019 | 430.610 | 80,59 | 64,43 | 54,86 | 47,04 | 41,24 |
| 2020 | 500.380 | 78,30 | 62,86 | 52,11 | 44,85 | — |
| 2021 | 582.406 | 77,16 | 59,16 | 49,28 | — | — |
| 2022 | 611.227 | 75,23 | 58,60 | — | — | — |
| 2023 | 590.372 | 78,27 | — | — | — | — |

Ortalama (basit): 1 yıl **77,9**; 2 yıl **61,3**; 3 yıl **52,1**; 4 yıl **45,9**; 5 yıl **41,2** (tek kohort).

Çapraz kontrol (türetildi): 2019 kohortu 430.610 × %80,59 = 347.037, tabloda 347.037. 2021 kohortu 582.406 × %77,16 = 449.4 bin, tabloda 449.408. Doğum sayıları kohort paydasıyla tutarlıdır.

İstihdam hayatta kalma (1 yıl): 85,15 / 81,39 / 81,25 / 79,45 / 83,61 (2019–2023).

### 2.2 Doğum ve ölüm, hukuki form (2024 doğum, 2022 ölüm)

| Hukuki form | Doğan 2024 (%) | Ölen 2022 (%) |
| :-- | --: | --: |
| Gerçek kişi | 77,46 | 85,04 |
| Limited | 17,88 | 11,02 |
| Anonim | 3,00 | 1,51 |
| Adi ortaklık | 1,01 | 1,75 |
| Kooperatif | 0,16 | 0,12 |
| Diğer | 0,49 | 0,56 |

Toplamlar: doğan 2024 = 633.146 (tabloyla tutar); ölen 2022 = 482.298 (tutar; 410.143 + 53.129 + 7.280 + 8.463 + 567 + 2.716).

Yorum: gerçek kişi işletmeleri doğumun %77'si ama ölümün %85'idir; limited şirketler doğumun %18'i, ölümün %11'i. Sermayesiz genç gerçek kişi olarak başladığında hayatta kalma riski ortalamanın üstündedir. Bu, genc3 modelinde "kalıcılık" kaybını açıklar.

### 2.3 Sektör doğum (8e7f8e06, 2024) ve sektör içi oran (a32f71ab, 2024)

Doğum payları SEKTOREL_DOGUM_DAGILIMI.md'dedir (G %32,07; H %16,84; F %10,11; I %9,40; C %9,39; M %6,27; S %4,26; tarım %0,73).

Sektör içi doğum oranı 2024 (a32f71ab, girişim oranı %): İnşaat 20,81; Konaklama 19,07; Bilgi 19,55; Gayrimenkul 19,88; Ulaştırma 17,71; İdari 17,38; Kültür 18,78; Sağlık 16,61; Eğitim 16,32; Elektrik 15,51; Toptan 14,66; Diğer 15,89; Tarım 14,16; İmalat 12,44; Madencilik 13,51; Su 12,96; Mesleki 12,72; Finans 7,04. Toplam 15,83.

### 2.4 Ölüm sektör dağılımı 2022 (73ae6f2a, toplam 482.298)

G Toptan 168.748 (34,99%); H Ulaştırma 78.624 (16,30%); I Konaklama 50.950 (10,56%); F İnşaat 50.015 (10,37%); C İmalat 46.628 (9,67%); M Mesleki 21.059 (4,37%); S Diğer 24.293 (5,04%); L Gayrimenkul 8.192; J Bilgi 7.021; N İdari 7.925; Q Sağlık 5.454; P Eğitim 3.144; R Kültür 3.680; A Tarım 4.162; E 673; D 587; K 672; B 471. Toplam 482.298 (tutar).

Yorum: ölüm payı ile doğum payı sektörler arasında yakın çıkıyor (toptan ticaretin ölüm payı 35%, doğum payı 32%). Yani toptan ticaret ölümde doğumdan fazla yer kaplıyor; kalıcılık toptanda daha zayıf. Konaklama ölümde 10,6%, doğumda 9,4%.

### 2.5 Yaş yapısı, faal girişim (cf8e1e33, 2024)

Kuruluş yılına göre faal girişim payı (%): 1990 ve öncesi 4,18; 1991–95 4,28; 1996–2000 6,99; 2001–05 7,29; 2006–10 9,71; 2011–15 13,21; 2016–20 20,85; 2021 ve sonrası 33,49. Toplam 100. İstihdam payı 2021 ve sonrası 17,40; ciro payı 13,53.

Yorum: faal girişimlerin üçte biri 2021 sonrası doğmuştur; bu, son dönem doğum yoğunluğunu gösterir. Kuruluş yılı 2021+ olanlar hayatta kalma eğrisinin genç kısmındadır.

### 2.6 Hızlı büyüyen ve ceylan (d7c0c28d, 9953c0b2, 5f5697a6)

Hızlı büyüyen girişim oranı 2024 %14,45 (2015: %15,13; dip 2020: %11,92). Ceylan 2024 %2,39 (2016–2024 aralığı %2,27–2,61).

2024 hızlı büyüyen sayıları sektöre göre (9953c0b2, toplam 33.370): C İmalat 7.858; G Toptan 6.831; F İnşaat 5.059; H Ulaştırma 2.595; I Konaklama 3.491; M Mesleki 1.580; N İdari 1.642; S Diğer 312; Q Sağlık 869; P Eğitim 967; J Bilgi 705; L Gayrimenkul 224; K Finans 263; R Kültür 195; A Tarım 202; B Madencilik 268; D Elektrik 190; E Su 119. (Toplam tutar.)

### 2.7 İmalat teknoloji düzeyi (f9ca6980, 2024, toplam 59.454)

Düşük teknoloji 34.346 (%57,77); orta-düşük 17.582 (%29,57); orta-yüksek 6.971 (%11,73); yüksek 555 (%0,93). Toplam tutar.

## 3. Modele bağlama (ne yapıldı, ne yapılmadı)

**Yapıldı:**
- `genc3.py`: `VARSAYILAN.hedef_canli12` 0,75 → **0,779** (f361f6a7 beş kohortun 1 yıllık hayatta kalma ortalaması). Ekrandaki A başlığı veri kaynağını yazacak şekilde güncellendi. Koşu yapıldı (aşağıda).

**Yapılmadı, sebebi:**
- `genc3` kalibrasyonu yalnız 1 yıl hedefi tutar. 2 yıl (%61,3) ve 3 yıl (%52,1) hedefleri modelde karşılaştırılmadı. Modelin `yikim` (72. ay iflas payı, tarafsız %29,9) ile veri `1−3 yıllık hayatta kalma` (%47,9 çıkış) tanımsaldır: model iflası nakit açığıyla, TÜİK çıkışı faaliyetin sona ermesiyle tanımlar. Bu iki tanım ayrı ölçülür; aynı sayıya zorlanmadı.
- Sektör karışımı N kalibrasyonuna girmedi; N kararı kendi işini kurma niyeti serisinden kalır (`KALIBRASYON_ANALOG.md`).
- Gerçek kişi / limited ayrımı genc3'te yok; 2.2'deki ölüm farkı bir sonraki adım olarak not edildi (gerçek kişi ölüm payı %85 → sermayesiz gerçek kişi modelinde kalıcılık riski ağırlığı).

## 4. Genç modeli koşusu (genc3.py, 8 tohum, 2000 kişi)

Kalibre b0 ort. 8.595 (std 680). Tarafsız senaryo: 1 yıl canlılık 0,779 (hedefe kalibre); 72 ay canlı 0,768; iflas (yikim) 0,299; kalıcı üst segment 0,603; geçim eşiği 1/3 aşımı 72. ayda 0,908.

Mevcut-kayıtlı: 1 yıl canlılık 0,647, iflas 0,882. Teklif: 1 yıl canlılık 0,697, iflas 0,435, kalıcı üst segment 0,378. Yani teklif tarafsıza göre canlılığı düşürür ama mevcut kayıt dışı (0,540) ve kayıtlı (0,647) senaryolarından iyidir. (Bu sonuç teklifin genç için mevcut düzenden daha iyi olduğunu gösterir; tarafsıza yakınlık hedef değildir.)

## 5. Açık sualler (veri değil, karar)

1. `yikim` (iflas) ile TÜİK çıkışı arasındaki tanım farkı: hangisi "başarısızlık" sayılacak? Padişah kararı gerekir (F 3-I 298'deki "açık kalma" ölçütüyle uyumlu olan model tanımıdır).
2. Gerçek kişi ile limited ayrımının genc3'e girmesi için hangi tanım kullanılacak (kendi hesabına gerçek kişi, mikro mükellef payı ayrı)?
