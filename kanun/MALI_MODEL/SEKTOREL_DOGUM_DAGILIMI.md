# SEKTÖREL DOĞUM DAĞILIMI (TÜİK, 2015–2024)

Kaynak: `veri/girisim_dokum.txt` içindeki `8e7f8e06-Doğan girişimlerin ve yarattığı istihdamın sektörlere göre dağılımı 2015-2024` tablosu (TÜİK Girişimcilik ve İş Demografisi). Tablo, doğan girişimlerin (yeni kurulan işletmelerin) NACE Rev. 2 kısımlarına göre sayısını ve oranını verir. Girişim oranı = sektördeki doğan girişim / toplam doğan girişim.

Önemli ayrım: `2c2bdd47` dosyası **faal** girişimlerin sektör dağılımıdır (doğan değil); bu dosya burada kullanılmamıştır. Ayrıca `5f5697a6` gazel (hızlı büyüyen) girişimlerin dağılımıdır; `73ae6f2a` ve `2c8ada63` ölen girişimlerin dağılımıdır.

## 1. 2024 doğum dağılımı

Toplam: **633.146** doğan girişim (tablodaki toplam satırıyla birebir; bölümlerin toplamı 633.146).

| NACE | Kısım | Doğan girişim (2024) | Oran (%) |
| :-- | :-- | --: | --: |
| G | Toptan ve perakende ticaret | 203.028 | 32,07 |
| H | Ulaştırma ve depolama | 106.630 | 16,84 |
| F | İnşaat | 64.021 | 10,11 |
| I | Konaklama ve yiyecek hizmeti | 59.544 | 9,40 |
| C | İmalat | 59.454 | 9,39 |
| M | Mesleki, bilimsel ve teknik faaliyetler | 39.718 | 6,27 |
| S | Diğer hizmet faaliyetleri | 26.956 | 4,26 |
| L | Gayrimenkul faaliyetleri | 14.435 | 2,28 |
| J | Bilgi ve iletişim | 12.894 | 2,04 |
| Q | İnsan sağlığı ve sosyal hizmetler | 12.769 | 2,02 |
| N | İdari ve destek hizmetleri | 12.554 | 1,98 |
| R | Kültür, sanat, eğlence | 6.352 | 1,00 |
| P | Eğitim | 5.625 | 0,89 |
| K | Finans ve sigorta | 1.700 | 0,27 |
| D | Elektrik, gaz, buhar | 1.184 | 0,19 |
| B | Madencilik ve taşocakçılığı | 839 | 0,13 |
| E | Su temini, kanalizasyon | 792 | 0,13 |
| A | Tarım, ormancılık, balıkçılık | 4.651 | 0,73 |

Not: A satırı (tarım) tabloda 4.651 olarak yer alır; yukarıdaki sıralama oran büyüklüğüne göredir.

## 2. 2015–2024 seyri (sektör sayıları, seçilmiş)

| NACE | 2015 | 2019 | 2024 | 2015 payı (%) | 2024 payı (%) |
| :-- | --: | --: | --: | --: | --: |
| G Toptan/perakende | 138.886 | 157.601 | 203.028 | 34,99 | 32,07 |
| H Ulaştırma | 43.465 | 45.256 | 106.630 | 10,95 | 16,84 |
| F İnşaat | 34.159 | 23.809 | 64.021 | 8,60 | 10,11 |
| C İmalat | 44.687 | 48.772 | 59.454 | 11,26 | 9,39 |
| I Konaklama | 48.256 | 57.459 | 59.544 | 12,16 | 9,40 |
| M Mesleki | 22.376 | 28.578 | 39.718 | 5,64 | 6,27 |

(Tablonun 2015 ve 2019 değerleri aynı dosyadan okunmuştur. 2015 payları tablodaki 2015 oranlarıdır.)

## 3. Modele bağlama

- Sermayesiz genç girişimin olası sektörlerinin ağırlığını gösterir. Toptan ticaret ve ulaştırma (birlikte %49) mikro mükellefiyetin tipik alanıdır; bu iki kısım yük ve tevkifat duyarlılığında en önemli sektörlerdir.
- Tarım (A) yalnız %0,73'tür; katılım havuzu tarım dışı ağırlıkla hesaplanmalıdır (F 3-I 262 ile uyumlu).
- Model N kalibrasyonu (`KALIBRASYON_ANALOG.md`) doğan girişim sayısını (633 bin, 2024) kullanmaz; bu tablo yalnız sektör karışımını verir. Doğan girişim sayısı ile kendi işini kurma niyeti serisi (255–332 bin) ayrı ölçülerdir.
- Hayatta kalma ve sektör ölüm oranları için `73ae6f2a` ve `2c8ada63` dosyaları ayrı bir kalibrasyon adımıdır; bu dosyada henüz eşleştirilmemiştir.

## 4. Açık kalanlar

- `girisim_dokum.txt` dosyasının 282. satırdan sonrası (`9953c0b2` hızlı büyüyen girişimler ve devamındaki dosyalar: `f9ca6980`, `cf8e1e33`, `73ae6f2a` sonrası kalan bölümler) bu turda okunmamıştır. Dosyanın tamamı okunmadan o dosyalar hakkında hüküm yoktur; okuma ayrı bir turda yapılacaktır.
- Sektör başına hayatta kalma oranı yoktur; sektör bazlı ölüm oranı yoklanamamıştır.
