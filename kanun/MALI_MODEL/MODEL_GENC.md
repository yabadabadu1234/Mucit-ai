> **[TARİHÎ KAYIT, 12/10/2026]** Genç modelinin ilk sürümüdür; yerine `GENC3_RAPOR.md` geçmiştir.

# GENÇ SEYRİ MODELİ (F 3-I 258)

Kod: `genc_model.py`; sonuç: `sonuc_genc.json`, `genc_out.txt`. 3000 genç × 72 ay, aynı rastgele şoklar bütün rejimlerde (ortak rastgele sayılar). **Bütün parametreler varsayımdır, ölçülmemiştir**; hiçbiri veriye oturtulmadı. Reel (2026) TL.

## 1. Model
- Genç 0 sermayeyle başlar; ilk 12 ay yan gelir (0,35 asgari net), 15.000 TL aylık geçim, %1,5 aylık aile/sağlık şoku (2 aylık geçim), ortak makro şok.
- Müşteri havuzu: aylık yeni müşteri olasılığı, müşteri kaybı (tampon sermayeyle azalır), beceri öğrenmeyle artar; tampon (sermaye) yeni müşteri ve beceri artışını hızlandırır; borç −90.000 TL'yi aşarsa 6 ay yıkım (yan iş, işletme sıfır).
- Segment: son 12 ayın ortalama net geliri / net asgari (28.075 TL, 2026 değeri hafızadandır, yoklanmadı): A <0,6 · B 0,6–1,2 · C 1,2–2,5 · D >2,5. **Kalıcı üst:** 49.–72. aylarda hep C veya D. **Salınım:** 25.–72. ayda ≥4 segment değişimi ve kalıcı üstte değil. **Dip:** hiç C'ye varamamış ve sonda A/B.
- Rejimler: **Mevcut kanun, kayıtlı** (aylık 11.808 TL Bağ-Kur asgari prim + 2.000 TL ofis/muhasebe, gerçek kâr üzerinden gelir vergisi, ilk 3 yıl 400.000 TL genç girişimci istisnası [tutar hafızadan, yoklanmadı; sıfırlanınca sonuç aynı yönde]); **Mevcut kanun, kayıt dışı** (vergi ve prim yok; müşteriye erişim %55, kayıp oranı yüksek, aylık %0,4 denetim ihtimali ve 3 aylık hasılat cezası); **Teklif S** (nihaî tevkifat, sabit yük yok, tavan 24 asgari ücret aşılınca genel hükümler); **Model G** (S + gelir primi: net gelir 2W altında yok, üstünde %10, 10W üstünde %20; tavanda genel hükümler); **G2** (G, tavanda uçurum yok); **G3** (G2 + yıl içinde dişli değil, son 12 ayın etkin oranıyla yuvarlanan tevkifat); **Tarafsız ölçü** (kanunsuz, vergi ve prim yok).
- Üç kalibrasyon: zor (aylık yeni müşteri 0,30, bütçe 4.500), **orta** (0,45; 5.500), kolay (0,60; 7.000). Aşağıdaki ana tablo **orta**dır.

## 2. Sonuç — orta kalibrasyon
| Rejim | Kalıcı üst | Salınım | Dip | En az bir yıkım | Devlet PV (genç başı, 5 yıl, %5 iskonto) | Son yıl aylık net |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Tarafsız ölçü | %87,1 | %0,8 | %6,9 | %5,2 | 0 | 97.398 |
| **Mevcut kanun, kayıtlı** | **%16,7** | %0,4 | %81,3 | **%81,8** | 534.064 | 22.261 |
| **Mevcut kanun, kayıt dışı** | **%12,9** | %5,1 | %79,0 | %70,9 | **0** | 20.451 |
| Teklif S | %71,1 | %2,9 | %15,9 | %10,1 | 974.163 | 60.222 |
| Model G | %52,0 | %2,8 | %32,4 | %16,2 | 1.031.064 | 53.939 |
| Model G2 | %51,1 | %3,4 | %32,8 | %16,2 | 1.327.577 | 45.389 |
| Model G3 | %51,5 | %3,0 | %32,5 | %16,2 | 1.308.483 | 45.530 |

Zor kalibrasyonda kalıcı üst: tarafsız %35,0 · mevcut kayıtlı %0,8 · kayıt dışı %0,5 · S %17,8 · G %7,9. Kolay kalibrasyonda: tarafsız %99,2 · mevcut kayıtlı %62,4 · kayıt dışı %57,0 · S %93,8 · G %88,3 · G2 %87,5.

## 3. Padişahın ölçütüne göre hüküm
1. **Mevcut kanunda hata vardır.** Orta kalibrasyonda genç %83–87'si kalıcı üst segmente çıkamıyor (tarafsız %87'ye karşı %13–17), %71–82'si en az bir kez yıkıma düşüyor. Sebep modelde ayrışıyor: kayıtlı yolda sabit prim ve ofis/muhasebe yükü sermayesiz genci tamponsuz bırakıyor; kayıt dışı yolda müşteri erişimi kısıtlı ve cezalı. Genç "hangi yolu seçse" kaybeder. Bu sonuç kalibrasyondan bağımsız yönde çıkıyor (zor/orta/kolay hepsinde mevcut < S).
2. **Devlet mevcut kanunda:** kayıtlı yolun genç başı bugünkü değeri 534.000 TL, kayıt dışı yolun 0. Gençlerin hangi kısmının kayıtlı olduğu bilinmediği için karma değer ölçülmedi; kayıtlı pay q ise devlet PV = q × 534.000. Teklif S 974.000 TL: gençlerin tamamı kayıtlı olur varsayımıyla (bu varsayım ölçülmedi).
3. **Teklif S büyük ölçüde çözer, fakat kalıcı üst %71 (tarafsız %87'nin 16 puan altı).** Fark iki yerden gelir: (a) nihaî tevkifat yükü; (b) **tavan çentiği:** 24 asgari ücretlik hasılat tavanında yıllık net 442.600 TL iken tavanı bir lira aşınca 324.900 TL'ye düşer (−%27, −117.700 TL); S'deki genç ortalama **72 ayın 28,6'sını genel hükümler altında** geçirir (başarılı genç eski yükün altına geri düşer). Bu, "yükselip alçalma" ölçütüne uyan bir **tasarım hatasıdır**: tavan başarıyı cezalandırıyor.
4. **Model G (gelir primi):** S'ye göre kalıcı üst 19 puan düşer (%71 → %52), devlet PV yalnız %6 artar (974 → 1.031 bin). Gençler için kötü takas. **G2** (uçurumsuz) devlet PV'sini %36 artırır (1.328 bin) ama kalıcı üst yine %51. Yani gelir primi, gencin yükselişini bedel sayarak devlete akıyor.
5. **12 aylık segmentte salınım** her rejimde %5'in altında (kayıt dışı %5,1); bu ölçüyle salınım hatası yok. **3 aylık aylık dalgalanma** S'de %21,8, tarafsızda %5,5; G3'ün yuvarlanan tevkifatı bunu belirgin azaltmadı (%19,8). Bu ölçü gelir seviyesine de duyarlı olduğu için (segment sınırına yakın olan çok kişi daha çok dalgalanır) kaynağını ayıramadım; "yıl içi tevkifat dişi" hipotezi bu model içinde teyit edilmedi.

## 4. Sınırlar
- Müşteri havuzu, beceri öğrenmesi, şok, yıkım eşiği, kayıt dışı erişim %55 ve denetim ihtimali tamamen varsayımdır. Kayıtlı/kayıt dışı seçimi modellenmedi (iki yol ayrı ayrı gösterildi).
- Hibe, BES katkısı, donanım KDV'si, sahte fatura ve sosyal güvenlik yardımları bu modelde yok (mali modelde var). Mevcut kayıtlı yolun devlet geliri yıkımdaki aylarda sıfırdır (prim tahsil edilemez; birikmiş prim borcu yazılmadı).
- 400.000 TL genç girişimci istisnası ve 28.075 TL net asgari hafızadandır, yoklanmadı.
