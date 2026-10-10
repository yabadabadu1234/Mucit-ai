# MİKRO MÜKELLEFİYET MALİ ETKİ MODELİ

Dosyalar: `model.py` (hesap), `analiz.py` (senaryo, tornado, Monte Carlo, varyant), `grafik.py`, `xlsx_uret.py`, `MIKRO_MUKELLEF_MALI_MODEL.xlsx` (canlı formüllü Excel), `sonuc.json`. Grafikler `../GORSELLER/model_*.png`.

**Doğrulama.** Excel'deki formüller (Girdiler, Hesap, Sonuc sayfaları) bağımsız bir formül hesaplayıcısıyla (`formulas` kütüphanesi) çalıştırılıp Python modelinin Orta senaryo çıktılarıyla karşılaştırıldı; 14 kalemde göreli fark 10⁻¹⁵ mertebesindedir. Excel dosyası değerleri önbelleğe almadan kaydedilmiştir; Excel açıldığında kendisi hesaplar. Monte Carlo ve tornado Python'dadır; Excel'de statik değer olarak `Senaryolar_Python` sayfasındadır.

## 1. Yapı

1. **Nüfus.** Katılımcı sayısı $N$ (kararlı durumda); yıllık hasılat $H$ log-normal (medyan $m$ asgari ücret, yayılım $\sigma$), 0,1 ile 24 asgari ücret arasına kırpılmış, 60 geometrik dilimle ayrıklaştırılmış.
2. **Üç tür katılımcı.** (a) yeni: daha önce hiç vergi ve prim ödemeyen; (b) halen kayıtlı ($s$): eski rejimde gelir vergisi (kâr marjı × $H$ üzerinden tarife) ve 4/b primi ödüyordu; (c) ücretli ek gelir ($u$): eski rejimde marjinal oranla ve kısmî uyumla vergi ödüyordu.
3. **Yeni rejim geliri.** $T(H)$ = GVK m.103 genel tarifesi (190.000 TL %15; 400.000'e kadar %20; 1.000.000'a kadar %27; 5.300.000'e kadar %35; üstü %40) uygulanan safi matrah $0{,}7\,H$ (götürü gider %30).
4. **Giderler.** BES aktarımı (tevkifatın %3'ü, vazgeçme payı kadar azalır) ve Devlet katkısı (%20); 90 günlük MYÖ primi hibesi ($H \geq 12$ asgari ücret ve çakışmasız olanlar için $3 \times W \times 0{,}21$); donanım KDV mahsubu (üst sınır tevkifatın %50'si); KGF (kullanım × kefalet × temerrüt × (1 − kurtarma)); PTT UETS; BT tek seferlik ve yıllık; itiraz; denetim.
5. **Sahte fatura.** Kurumsal akıştaki sahte pay $\varphi$, önlem etkinliği kadar azalır; kayıp = hacim × (kurumlar vergisi oranı − etkin tevkifat oranı).
6. **Zaman.** Beş yıl; katılım rampası %25, %55, %80, %100, %100; 1. yılda tek seferlik BT ve PTT; reel iskonto %5; sabit 2026 TL.
7. **Çıktılar.** Yıl yıl net etki, 5 yıllık bugünkü değer, kırılma noktası $s^*$, politika varyantları, tornado, Monte Carlo (4000 deneme, sabit tohum 20261010).

## 2. Girdi tablosu ve durumu

Durum sütunu: **M** mevzuattan okundu, **İ** ikincil kaynak, **H** varsayım (ölçülmemiş, veriyle doldurulacak).

| Girdi | Kötümser | Orta | İyimser | Durum |
| :-- | :-- | :-- | :-- | :-- |
| Medyan hasılat (asgari ücret katı) | 4.0 | 5.0 | 6.0 | H |
| Katılımcı sayısı N | 150000 | 350000 | 700000 | H |
| Halen kayıtlı payı s | 0.45 | 0.25 | 0.1 | H |
| Ücretli ek gelir payı u | 0.25 | 0.2 | 0.15 | H |
| Sahte fatura payı φ | 0.02 | 0.01 | 0.005 | H |
| Önlem etkinliği | 0.3 | 0.5 | 0.7 | H |
| 90 gün primi hak edenler | 0.5 | 0.35 | 0.2 | H |
| BES vazgeçme payı | 0.2 | 0.35 | 0.5 | H |
| KGF kullanım oranı | 0.08 | 0.05 | 0.03 | H |
| KGF temerrüt oranı | 0.15 | 0.1 | 0.06 | H |
| Donanım alan payı | 0.5 | 0.4 | 0.3 | H |
| Brüt asgari ücret 2026 | 33.030 | 33.030 | 33.030 | İ (birden çok kaynakta tutarlı) |
| Tarife eşikleri ve oranlar | 103. madde | 103. madde | 103. madde | M |
| MYÖ prim oranı %21, 4/b toplam %35,75 | | | | M (5510 m.81) |
| Devlet katkısı %20 | | | | İ (4632 Ek 1 dipnotu M; 10811 sayılı Karar metni okunmadı) |
| Götürü gider %30, BES %3, hibe prim 90 gün, donanım mahsup tavanı %50 | | | | Teklif hükmü |
| Eski rejim kâr marjı, eski prim ödeme oranı, ücretli uyumu, ücretli marjinal oranı, kurumsal pay, KGF kurtarma, PTT birim, BT giderleri, itiraz oranı ve birim gideri, denetim oranı | bkz. xlsx Girdiler | | | H |

## 3. Sonuçlar (4. yıl, Orta senaryo, milyar TL)

Brüt tevkifat 8,18; BES ve Devlet katkısı −0,19; 90 gün prim −0,36; donanım KDV −0,63; yutulma vergi −2,38; yutulma SGK primi −9,92; sahte fatura −0,03; KGF −0,13; BT, itiraz, denetim −0,16; **net −5,62** (yalnız vergi tarafı +4,30). Kötümser −6,87; İyimser +5,61. Beş yıllık bugünkü değerler −21,2 / −17,4 / +16,7.

Kırılma noktası: s* = %12.6 (Orta). Monte Carlo net: P5 -19.9, P50 -19.90, P95 3.8 (milyar TL); net > 0 olasılığı %24.


## 4. Politika varyantları (Orta, 4. yıl net, milyar TL)

| Varyant | Net |
| :-- | :-- |
| P0 Teklif (Orta) | -5.62 |
| P1 Kayıtlı mükellef girişi kapalı (s=0,02) | 4.80 |
| P2 Geçiş yapan 4/b primini yarı oranda sürdürür | -0.66 |
| P3 Götürü gider %20 | -4.29 |
| P4 (e) bendi yok: düz %10,5 | -6.18 |
| P5 90 gün prim hibesi yok | -5.26 |
| P6 P1 + P3 | 6.13 |
| P7 P2 + P3 | 0.67 |

## 5. Ne anlama geliyor

1. Teklifin Hazine'ye net katkısı **yutulma** (halen kayıtlı mükellef ve 4/b sigortalıların rejime geçmesi) ile belirlenir. Yutulmanın büyük kısmı SGK primi kaybıdır; yalnız vergi tarafına bakıldığında Orta senaryo olumlu (+4,3), SGK dahil olumsuzdur (−5,6).
2. "Hazine'ye yük olmaz" cümlesi bu modelle desteklenmez. Desteklenen cümle: "Kayıt dışı üretici kayda girer; Hazine etkisi yutulma payına bağlıdır, bu pay ölçülmemiştir."
3. Model; kademeli oran (Madde 1 (e)), geri akış karinesi (r) ve kimlik tekliği (s) gibi suistimal önlemlerinin etkisini yalnız sahte fatura kalemi ($\varphi$, önlem etkinliği) üzerinden yakalar; bu kalem küçüktür. Yutulma ise hukukî suistimal değil, rejimin kendi tasarımının sonucudur.

## 6. Karar bekleyen iki hüküm (hazır metin, teklife işlenmemiştir)

**Seçenek P1: giriş kapısı.** Madde 1 (p) sonuna: "Başvuru tarihinden önceki yirmi dört ay içinde 5510 sayılı Kanunun 4 üncü maddesinin birinci fıkrasının (b) bendi kapsamında sigortalı sayılmış olanlar veya ticarî kazanç ya da serbest meslek kazancı yönünden gelir vergisi mükellefi olmuş olanlar bu istisnadan yararlanamaz." ve Geçici Madde 1'in kaldırılması. Etki: +4,8 milyar TL (Orta). Bedeli: mevcut küçük esnaf rejimden yararlanamaz, eşitlik itirazı doğar.

**Seçenek P2: prim devamı.** Geçici Madde 1'e: "Bu madde uyarınca mikro mükellefiyete geçenler, geçiş tarihinden önceki prim ödeme gün sayılarının sürdürülmesi için asgari prim tutarının yarısını tevkifattan bağımsız olarak ödemeye devam ederler." Etki: −0,7 milyar TL (Orta; yutulma kaybı yarı yarıya kapanır). Bedeli: mikro mükellefe prim yükü geri gelir, rejimin cazibesi düşer.

## 7. Veri talebi (modelin ölçülmemiş girdilerini kapatacak)

| Girdi | Kurum | İstenen |
| :-- | :-- | :-- |
| $s$, eski vergi ve prim | SGK, GİB | 4/b sigortalı ve basit/gerçek usul mükellef sayısı; hizmet ve fikir sektörü kodlarına göre yıllık hasılat dağılımı; prim tahsilat oranı |
| $N$, $u$ | TÜİK, GİB | Serbest çalışan ve ek iş yapan ücretli sayısı; 20/B kapsamındaki mükellef sayısı ve hasılatı |
| $\varphi$ | GİB, MASAK | Hizmet faturalarında sahte fatura oranı |
| BES vazgeçme | EGM | Otomatik katılımda vazgeçme oranı |
| KGF | KGF, Hazine | Mikro ölçek faizsiz finansman temerrüt oranı |
| PTT, BT | PTT, GİB, BDDK | UETS birim gideri; portal ve banka entegrasyon maliyeti |
