# MİKRO MÜKELLEFİYET MALİ ETKİ MODELİ (güncel: F 3-I 299, 304)

**Tasarım (padişah kararları):** düz tevkifat gayrisafi hasılatın %13,5'i (kanunda üst sınır %27, Cumhurbaşkanı kararıyla); halen kayıtlı olanlar dâhil herkese eşit giriş; gelirden bağımsız sabit prim yok, yerine **gelire bağlı prim**: aylık net mikro gelir geçim haddini (brüt asgari/3 = 11.010 TL) aşmazsa prim yok, aşarsa gelirle doğrusal artar, brüt asgari ücretin altı katında tam prim (11.808,25 TL/ay); maaşlı çalışan isterse mikro mükellef olabilir (payı u). Eski sürümlerin sayıları (götürü gider, kademeli oran, prim sürekliliği şartı, maaşlıyı dışlama) **geçersizdir**; git geçmişindedir.

Dosyalar: `model.py` (hesap), `analiz.py` (varyant, tornado, Monte Carlo), `duyarlilik_tablolari.py` (tek tek parametre tabloları), `DUYARLILIK_TABLOLARI.md` (çıktı), `genc3.py` (genç seyri), `prim_esigi.py` (tam prim eşiği taraması), `MIKRO_MUKELLEF_MALI_MODEL.xlsx` (Excel; Python ile üç senaryoda da aynı sonucu verir).

## 1. Yapı

1. **Nüfus.** Katılımcı sayısı N (kararlı durumda): Kötümser 100.000 (padişah: en fazla 100 bin), Orta 331.000, İyimser 1.096.000 (padişah oranları × ILO 2025 verisi; GUNCEL_MODEL.md §1); yıllık hasılat H log-normal (medyan 5 asgari ücret, σ 0,9), 0,1 ile 24 asgari ücret arasına kırpılmış.
2. **Katılımcı türleri.** (a) yeni (daha önce vergi ve prim ödemeyen), (b) halen kayıtlı (s): eski rejimde vergi ve sabit 4/b primi öderdi (141.699 TL/yıl × π tahsil oranı); yeni rejimde vergi tevkifatla, prim gelire bağlıdır, (c) maaşlı mikro mükellef (u): eski rejimde ek geliri ücret vergisine tabiydi; yeni rejimde ayrı ve nihaî %13,5 öder, mikro primi ödemez (o ay 4/a primi ödediğinden).
3. **Gelir.** T(H) = 0,135 × H (düz oran, gider tenzili yok). Gelire bağlı prim: yıl boyunca eşit aylık hasılat varsayımıyla 12 × 11.808,25 × min(1, max(0, (y − 11.010)/(198.180 − 11.010))), y = (H − T)/12; tahsil oranı 1 (tevkifatla birlikte kaynakta kesilir; tasarım, ölçülmemiş).
4. **Giderler.** BES (tevkifatın %3'ü) ve Devlet katkısı (%20); 90 gün MYÖ primi hibesi; donanım KDV mahsubu; KGF; PTT; BT; itiraz; denetim.
5. **Sahte fatura.** Kayıp = hacim × (kurumlar vergisi %25 − %13,5) × φ × (1 − önlem) × kurumsal pay.
6. **Zaman.** Beş yıl; rampa %25, %55, %80, %100, %100; reel iskonto %5; sabit 2026 TL.

## 2. Sonuç (4. yıl, milyar TL)

| Kalem (4. yıl, milyar TL) | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| Katılımcı (kişi) | 100.000 | 331.000 | 1.096.000 |
| Halen kayıtlı olup geçenlerin payı s | %30 | %15 | %5 |
| Maaşlı mikro mükellef payı u | %25 | %20 | %15 |
| Brüt tevkifat (%13,5) | 2,36 | 9,23 | 34,63 |
| Gelire bağlı yeni prim | 0,26 | 1,25 | 5,44 |
| BES ve Devlet katkısı | -0,07 | -0,22 | -0,62 |
| 90 gün prim hibesi | -0,10 | -0,34 | -0,83 |
| Donanım KDV mahsubu | -0,23 | -0,62 | -1,57 |
| Yutulma: vergi (halen kayıtlı ve maaşlı) | -0,70 | -1,72 | -3,60 |
| Yutulma: eski sabit 4/b primi kaybı | -3,40 | -5,63 | -6,21 |
| Sahte fatura, KGF, BT, PTT, itiraz, denetim | -0,17 | -0,32 | -0,68 |
| **Net (Hazine + SGK)** | **-2,05** | **1,64** | **26,56** |
| 5 yıllık bugünkü değer (reel %5) | -6,52 | 4,67 | 80,29 |

## 3. Varyantlar (tek tek)

| Varyant (4. yıl net, milyar TL) | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| V0 Baz: oran %13,5, gelire bağlı prim (tam prim 6 asgari ücrette), maaşlı payı u | -2,05 | 1,64 | 26,56 |
| V1 Gelire bağlı prim hiç alınmasaydı | -2,31 | 0,40 | 21,12 |
| V2 Tam prim eşiği 3 asgari ücret | -1,75 | 3,04 | 32,69 |
| V3 Tam prim eşiği 12 asgari ücret | -2,18 | 1,00 | 23,76 |
| V4 Oran %20 | -1,00 | 5,75 | 42,00 |
| V5 Oran %25 | -0,18 | 8,93 | 53,91 |
| V6 Oran %27 (üst sınır) | 0,14 | 10,20 | 58,68 |
| V7 Maaşlı hiç mikro mükellef olmasaydı (u=0) | -1,67 | 2,88 | 30,12 |
| V8 Eski prim tahsil oranı π=%50 | -0,77 | 3,75 | 28,89 |
| V9 π=%100 | -2,90 | 0,23 | 25,01 |
| V10 Yeni primin tahsil oranı %80 | -2,10 | 1,39 | 25,48 |
| V11 Halen kayıtlıların hepsi geçse (s=%100) | -10,93 | -34,76 | -110,47 |
| V12 90 gün prim hibesi olmasaydı | -1,95 | 1,98 | 27,40 |
| V13 Donanım KDV mahsubu olmasaydı | -1,82 | 2,26 | 28,13 |

## 4. Ne anlama geliyor

1. **%13,5'te Orta ve İyimser pozitif, Kötümser negatiftir** (−2,05). Kötümser, oran %26,1'e çıkarsa sıfırı geçer (%27'de +0,14).
2. **Ana açık risk s'dir** (Orta'da kırılma noktası s*=%18,8; Monte Carlo, 4000 deneme: medyan -0,47, %90 aralığı -16,35 ile 8,55, net > 0 olasılığı %46). Ölçülmemiş girdiler: s, u, π, yeni primin tahsil oranı. s=%100'de üç senaryo da olumsuzdur.
3. SGK tahsil oranı π (0,8) harici metne göre %35-40 olabilir (yoklanmadı); π=%50 ve π=%100 varyantları yukarıdadır.
4. Gelire bağlı prim Orta'da +1,24 milyar TL kazandırır (V0 − V1); maaşlının girebilmesi yaklaşık 1,24 milyar TL bedel getirir (V7 − V0).
5. Tam prim eşiği altı asgari ücrette seçilmiştir: genç modelinde tam primin açık firma ve geçim oranını sıfırdan ayırt edilemeyecek kadar etkilediği en küçük eşiktir (`GENC3_RAPOR.md`, `prim_esigi_out2.txt`). Eşiği üçe indirmek devlete Orta'da +1,40 getirir, gence açık firma oranında −0,009, geçimde −0,015 puan yazar.
6. Her varyantın tam tablosu ve diğer parametreler `DUYARLILIK_TABLOLARI.md` içindedir.

## 5. Veri talebi (ölçülmemiş girdileri kapatacak)

| Girdi | Kurum | İstenen |
| :-- | :-- | :-- |
| SGK 4/b prim tahsil oranı (π) | SGK | **Resmî veri bulunamadı** (iki arama, 12/10/2026: yalnız TBMM soru önergeleri ve haberler; "düzenli ödeyen 4/b sayısı" soruluyor, cevap yok). Modelde π=0,8 en kötü yönlü varsayımdır (düşük π yutulma kaybını azaltır): π=0,5'te Orta +3,43, π=0,375'te yaklaşık +4,3 |
| s ve u (maaşlı payı), eski vergi ve prim, yeni primin tahsil oranı | SGK, GİB | Halen 4/b sigortalısı veya gelir vergisi mükellefi olup bu rejime başvurabilecek kişi sayısı; hizmet ve fikir sektörü hasılat dağılımı; prim tahsilat oranı |
| N | TÜİK, GİB | Serbest çalışan sayısı; 20/B kapsamındaki mükellef sayısı ve hasılatı |
| φ | GİB, MASAK | Hizmet faturalarında sahte fatura oranı |
| BES vazgeçme | EGM | Otomatik katılımda vazgeçme oranı |
| KGF | KGF, Hazine | Mikro ölçek faizsiz finansman temerrüt oranı |
| PTT, BT | PTT, GİB, BDDK | UETS birim gideri; portal ve banka entegrasyon maliyeti |
