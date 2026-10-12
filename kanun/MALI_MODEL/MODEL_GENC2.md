> **[TARİHÎ KAYIT, 12/10/2026]** Genç modelinin ikinci sürümüdür; yerine `GENC3_RAPOR.md` geçmiştir.

# GENÇ SEYRİ MODELİ, İKİNCİ SÜRÜM (F 3-I 259)

> **GÜNCELLEME (11/10/2026, nakz F 3-I 179):** Tip payları güncellendi, sonuçlar GUNCEL_MODEL.md §2'dedir (S kalıcı üst: zor 1,5, orta 7,8, kolay 25,1). Aşağıdaki eski sayılar tarihî kayıttır.

Kod: `genc2.py` (3000 genç × 72 ay, ortak şoklar); sonuç: `sonuc_genc2.json`, `genc2_out.txt`. Önceki sürüm `MODEL_GENC.md`. **Bütün davranış ve oran parametreleri varsayımdır; TÜİK'in eğitim/okuma kırılımı tabloları alınamadı.**

## 1. İşsizlik oranı kimi sayıyor (padişahın sualine cevap)
- **Formül:** işsizlik oranı = işsiz ÷ işgücü; işgücü = istihdam + işsiz. Esas gösterge **15 yaş ve üzeri** içindir (TÜİK bülteninde ayrıca 15–24 genç oranı verilir).
- **"İşsiz" sayılmak için üç şart** (ILO/Eurostat standardı; hafızadan, TÜİK metodolojisi bu oturumda birincil kaynaktan okunmadı): işi olmamak, son dört hafta içinde aktif iş aramış olmak, kısa sürede (iki hafta) işe başlayabilir olmak. Haber kaynakları 2021'de tanımın revize edildiğini yazıyor; ayrıntısı doğrulanmadı.
- **Vasıf/eğitim sayılmaz:** manşet oran diploma, beceri, meslek ayırmaz; herkesi aynı kefeye koyar. Eğitim ve yaş kırılımları ayrı tablolarda yayımlanır (bu oturumda eğitim kırılımını bulamadım).
- **Sayılmayanlar (modeli ilgilendiren asıl kısım):** (a) iş **aramayan** herkes, umudunu kesenler dâhil; (b) okuyanlar iş aramıyorsa; (c) işi olup çok az çalışan ya da kayıt dışı/gelirsiz aile işçisi **çalışan sayılır**: istihdam tanımı geniştir (haftada bir saat ücretli iş yeterli; ILO standardı, hafızadan).
- **Güncel rakamlar (TÜİK, Ağustos 2026, 15+, mevsimsellikten arındırılmış):** işsizlik %7,8 (2.740 bin); işgücüne katılım %52,5; istihdam oranı %48,4; **atıl işgücü oranı %31,0** (işsiz + zamana bağlı eksik istihdam + potansiyel işgücü); genç (15–24) işsizlik %13,0 (erkek %9,7, kadın %19,4). 2025 yıllığında genç işsizlik %15,3. **NEET (ne okulda ne işte, ne eğitimde)**: 15–24 yaşta %22,9 civarı (2024/2025; Bahçeşehir BETAM ve basın aktarımı, dönem farkıyla %22,1–22,9); "ev gençleri" (iş aramayan, okumayan) 15–24'te %23,3, 15–29'da %26,3 (Eğitim-İş'in TÜİK kaynaklı metni; ikincil kaynak).
- **Modele etkisi:** %13 genç işsizlik, sermayesiz gencin sorununu **çok küçük** gösterir; 15–24'ün beşte biri hiç sayıda yoktur. Bu yüzden modelde işsizlik oranı değil, "geçimini sağlayabilen genç oranı" ölçülür.

## 2. Eklenen faktörler
- **Tip (varsayım payları):** okuyor-lise %15 · okuyor-üniversite %20 · okumuyor-lise altı %20 · okumuyor-lise %25 · okumuyor-lisans+ %20. 16 yaş altı yok; yaşlar 16–29. (Nüfusun gerçek yaş yapısı ve gelecek yıllar: 2025 sonunda 15–24 nüfusu 12.708.348 [ADNKS, basın aktarımı]; 2010–2016 doğumları yılda yaklaşık 1,24–1,33 milyon [TÜİK doğum istatistikleri, basın aktarımı], yani 16 yaşa girecek koşuların büyüklüğü önümüzdeki 6 yılda sabit kalır. Yaş×tip karışımı verisi bulunamadı; tip payları varsayımdır.)
- **Vakit:** okuyor-lise 0,35; okuyor-üniversite 0,45; okumayan 1,0 (müşteri akışını çarpar).
- **Serbest çalışan erişimi (diploma kapısı):** lise altı 0,25 · lise 0,45 · lisans+ 1,0 · okuyor-lise 0,20 · okuyor-üniversite 0,50.
- **Kendi işi:** *bol rakipli* (müşteri akışı yüksek, birim fiyat 0,6×), *az rakipli* (akış 0,3×, fiyat 1,8×, beceri eşiği 1,15: beceri yetmezse iş yok); her ay %4 ihtimalle satış çöküşü (mevcut işin yarısını kaybeder).
- **Yaşama eşiği:** aylık **net asgarinin 1/3'ü = 9.358 TL**; önce bu karşılanır, ancak artan kısmın yarısı sermayeye eklenir; eşik karşılanmayıp sermaye eksideyse "aç ay" sayılır; borç −56.000 TL'yi aşarsa 6 ay yıkım (yan iş).
- **Aile desteği:** okuyanın %70'i, okumayanın %35'i yaşama eşiği kadar destek alır (okuyanda 36 ay, okumayanda 12 ay; varsayım).
- **Mevcut kanunda burs kaybı:** kayıtlı okuyanların %40'ı aylık 0,25 net asgari burs/yardım kaybeder (varsayım; teklif Madde 5 bunu yasaklıyor).
- Genç girişimci istisnası: tek bir haber kaynağına göre 2026 için 1.737.500 TL'ye kadar; modelde 36 ay uygulanır (resmî metin doğrulanmadı).
- Segment: son 12 ayın ortalama **kendi** geliri / net asgari: A <1/3 · B 1/3–1 · C 1–2 · D >2; **kalıcı üst** = 49.–72. aylar boyunca C veya D.

## 3. Sonuç (orta kalibrasyon; zor ve kolay aşağıda)
| Rejim | Kalıcı üst | Dip (hiç C'ye varamayıp B/A'da bitmiş) | En az bir yıkım | Aç ay (72 ayda ort.) | Devlet PV (genç başı) |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Tarafsız ölçü | %25,0 | %54,0 | %52,1 | 20,9 | 0 |
| **Mevcut kanun, kayıtlı** | **%2,5** | %96,3 | %97,8 | 30,1 | 310.807 |
| **Mevcut kanun, kayıt dışı** | **%4,3** | %90,4 | %87,8 | 32,0 | 0 |
| Teklif S | **%17,6** | %64,4 | %58,8 | 23,6 | 267.049 |
| Model G | %11,7 | %74,1 | %63,7 | 25,5 | 318.716 |
| Model G2 | %11,9 | %74,1 | %63,7 | 25,5 | 392.170 |

Kalıcı üst — zor: tarafsız %8,9 · mevcut kayıtlı %0,1 · kayıt dışı %0,3 · S %5,9 · G %3,5. Kolay: tarafsız %49,5 · mevcut kayıtlı %8,7 · kayıt dışı %13,3 · S %36,3 · G %25,3.

Tipe göre kalıcı üst (orta; tarafsız / mevcut kayıtlı / mevcut kayıt dışı / S / G): okuyor-lise 1,5 / 0 / 0 / 0 / 0 · okuyor-üniversite 11,5 / 0,2 / 0,2 / 4,9 / 1,0 · okumuyor-lise altı 16,0 / 0,2 / 0,3 / 8,1 / 2,6 · okumuyor-lise 21,2 / 0,1 / 0,4 / 11,4 / 4,6 · okumuyor-lisans+ 71,1 / 12,0 / 20,6 / 61,5 / 49,5 (%).
Yola göre (tarafsız / mevcut kayıtlı / kayıt dışı / S / G): serbest çalışan 29,2 / 3,8 / 6,3 / 22,3 / 16,1 · bol rakipli iş 18,2 / 0,1 / 0,4 / 9,2 / 3,6 · az rakipli iş 9,9 / 0,3 / 0,3 / 5,6 / 2,9 (%).

## 4. Padişahın ölçütüne göre hüküm
1. **Mevcut kanunda hata vardır ve ağırdır:** kalıcı üst %2,5–4,3 (kanunsuz ölçü %25); kayıtlı yolda gençlerin %98'i, kayıt dışı yolda %88'i en az bir kez yıkıma düşer. Sebep: 1/3 asgari yaşama eşiği altında ek sabit prim/ofis yükü, kayıt dışında erişim kaybı ve ceza.
2. **Teklif S hatayı büyük ölçüde giderir ama tamamen değil:** %17,6 (tarafsıza göre 7,4 puan eksik). Kalan açığın büyük kısmı **kanundan değil faktörlerden gelir**: okuyan lise öğrencisi hiçbir rejimde kalıcı üste çıkamaz (%0–1,5), diploması olmayan serbest çalışan erişim kapısına takılır, az rakipli sahada beceri eşiği yüksektir. Kanun bunları çözemez; **kanunun eklediği hata** S için 7,4 puan, Model G için 13,3 puan, mevcut kanun için 22,5 puan.
3. **Model G (gelir primi) bu ölçütle kötüdür:** S'ye göre kalıcı üst 5,9 puan düşer, aç ay artar; devlet PV +%19 (318.716 vs 267.049). Gençlerin maksadı için S, devletin geliri için G2.
4. **Yapısal sorun:** diploma kapısı ve okuma/vakit sınırı model sonuçlarının ana belirleyicisidir. Bu iki faktör vergi/prim kanunuyla değil **eğitim ve iş piyasası politikasıyla** değişir; kanun maddesi (ör. diplomasız serbest çalışana erişim açan platform hükmü) ancak dolaylı yardım edebilir.
5. **Salınım:** 12 aylık segmentte salınım %6–13 aralığında ve tarafsızda da var (%12,1); rejimin eklediği salınım küçük, asıl sorun salınım değil **kalıcı yükselememe**dir.

## 5. Sınırlar ve eksikler
- Tip payları, vakit, erişim, aile desteği, burs kaybı varsayımdır; TÜİK eğitim×okuma×yaş tabloları alınıp model yeniden ağırlıklandırılmalıdır.
- Tarafsız ölçüde bile kalıcı üst %25 (orta) olması, parametrelerin sermayesiz gençler için karamsar kalibre olduğunu gösterir; yön önemlidir, düzey değil.
- Model gencin yol seçimini rasyonel yapmaz: tip başına sabit yol payları (varsayım). Yol bazlı sonuçlar `sonuc_genc2.json` içinde.
- Hibe, BES, KDV, sahte fatura, tavan çentiği dışındaki devlet kalemleri bu modelde yok.

Kaynaklar: [TÜİK Ağustos 2026 bülteni özeti](https://www.alomaliye.com/2026/09/30/issizlik-orani-aciklandi-agustos-2026/) · [BETAM NEET notu](https://betam.bahcesehir.edu.tr/wp-content/uploads/2025/10/ArastirmaNotu282.pdf) · [Eğitim-İş ev gençleri](https://www.egitimis.org.tr/assets/files/basin-yayin/695b862e3bede176760580652.pdf) · [genç nüfus 2025](https://www.cnbce.com/veriler/2025te-genc-nufusun-turkiye-nufusuna-orani-azaldi-h30027) · [asgari ücret 2026](https://kpmgvergi.com/yayinlar/mali-bultenler/sosyal-guvenlik/2026-yili-asgari-ucreti-aciklandi/3342) · [genç girişimci istisnası](https://www.haberturk.com/2026-yilinda-genc-girisimci-tesviki-ne-kadar-3856269-ekonomi).
