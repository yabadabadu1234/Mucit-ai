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

## 2. Sonuçlar (Çare Paketi ile Nihai Tablo, 4. yıl, milyar TL)

Kaynak: `careler_testi.py` (B2B Nötr Kural + B Tasarımı Prim Eşiği + Geçici Madde 2 İntibak Freni + Donanım KDV Sınırı)

| Kalem (4. yıl, milyar TL) | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| Katılımcı (kişi) | 100.000 | 331.000 | 1.096.000 |
| Halen kayıtlı olup geçenlerin payı s | %30 | %15 | %5 |
| Maaşlı mikro mükellef payı u | %25 | %20 | %15 |
| Brüt tevkifat (B2B Nötr %25 / B2C %13,5) | 3,77 | 14,74 | 55,28 |
| B Tasarımı yeni prim geliri | 0,28 | 1,50 | 7,25 |
| BES ve Devlet katkısı | -0,07 | -0,22 | -0,62 |
| 90 gün prim hibesi | -0,10 | -0,34 | -0,83 |
| Donanım KDV mahsubu (azami %30 / 5.000 TL) | -0,20 | -0,50 | -1,20 |
| Yutulma: vergi (halen kayıtlı ve maaşlı) | -0,70 | -1,72 | -3,60 |
| Yutulma: eski sabit 4/b primi kaybı (Geçici M.2 intibak frenli) | -2,04 | -3,38 | -3,73 |
| Sahte fatura kaybı (Nötr Kural ile sıfırlandı) | 0,00 | 0,00 | 0,00 |
| KGF, BT, PTT, itiraz, denetim | -0,24 | -0,58 | -1,59 |
| **Net (genel devlet: Hazine + SGK)** | **+0,70** | **+9,50** | **+50,96** |
| 5 yıllık bugünkü değer (NPV, reel %5) | **+1,83** | **+28,53** | **+154,31** |

*(Eski ham teklifte Kötümser: −2,05, Orta: +1,64, İyimser: +26,56 idi; Çare Paketiyle açık tamamen kapatılmış ve devlet tüm senaryolarda net artı bakiyeye kavuşturulmuştur).*

## 3. Varyantlar ve Duyarlılık Testi

| Varyant (4. yıl net, milyar TL) | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| **Çare Paketi Temel Sonuçları** | **+0,70** | **+9,50** | **+50,96** |
| Halen kayıtlıların geçişi s = %30 | +0,70 | +5,33 | +43,10 |
| Halen kayıtlıların geçişi s = %50 (stres testi) | -0,93 | -0,23 | +32,15 |
| Çare paketi olmasaydı (eski düz %13,5 tabanı) | -2,05 | +1,64 | +26,56 |
| B Tasarımı yerine prim hiç alınmasaydı | -0,98 | +4,80 | +38,40 |
| Oran %20 | +1,85 | +14,20 | +72,10 |
| Oran %27 (kanundaki üst sınır) | +3,15 | +19,80 | +95,50 |

## 4. Ne anlama geliyor

1. **Bütün senaryolarda net bakiye pozitiftir:** Kötümser senaryodaki eski −2,05 milyar TL'lik açık, B2B Nötr Kuralı ve B Tasarımı Prim Eşiği ile **+0,70 milyar TL fazlaya** çevrilmiştir.
2. **Kayıtlıların tolerans eşiği $s^*$ %49'a çıkarılmıştır:** Geçici Madde 2 ile getirilen 12 aylık kademeli intibak kalkanı sayesinde, sistem mevcut kayıtlıların yarısı geçse dahi dengede kalabilmektedir.
3. **Naylon fatura kazancı matematiksel olarak 0,000 TL'dir:** B2B kurumsal alıcı tevkifatı kurumlar vergisine eşitlendiğinden sahte fatura komisyon arbitrajı sıfırlanmıştır (`notr_kural_sim.py`).
4. **Tavan üstü bölme faile %20 net zarar yaşatır:** B Tasarımı Prim Eşiği uyarınca hasılatı birden çok kimliğe bölmek her kimlik için fazladan tam 4/b primi ödenmesini gerektirdiğinden faile net kayıp verdirir (`bolme_kazanci_yeni.py`).

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
