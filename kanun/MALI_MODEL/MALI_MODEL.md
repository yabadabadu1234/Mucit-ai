# MİKRO MÜKELLEFİYET MALİ ETKİ MODELİ (güncel: F 3-I 299, 300, 302)

**Tasarım (padişah kararları):** düz tevkifat gayrisafi hasılatın %13,5'i (kanunda üst sınır %27, Cumhurbaşkanı kararıyla); halen kayıtlı olanlar dâhil herkese eşit giriş; prim isteğe bağlı; ücretli çalışan (4/a, 4/c) rejime alınmaz. Eski sürümlerin sayıları (götürü gider, kademeli oran, prim sürekliliği şartı, ücretli ek gelir payı) **geçersizdir**; git geçmişindedir.

Dosyalar: `model.py` (hesap), `duyarlilik_tablolari.py` (tek tek parametre tabloları), `DUYARLILIK_TABLOLARI.md` (çıktı), `genc3.py` (genç seyri), `MIKRO_MUKELLEF_MALI_MODEL.xlsx` (Excel; yeni oran ve ücretli payı için yeniden üretilmelidir, bkz. GUNCEL_MODEL.md).

## 1. Yapı

1. **Nüfus.** Katılımcı sayısı N (kararlı durumda): Kötümser 100.000 (padişah: en fazla 100 bin), Orta 331.000, İyimser 1.096.000 (padişah oranları × ILO 2025 verisi; GUNCEL_MODEL.md §1); yıllık hasılat H log-normal (medyan 5 asgari ücret, σ 0,9), 0,1 ile 24 asgari ücret arasına kırpılmış.
2. **Katılımcı türleri.** (a) yeni (daha önce vergi ve prim ödemeyen), (b) halen kayıtlı (s): eski rejimde vergi ve 4/b primi öderdi; yeni rejimde vergi tevkifatla, prim isteğe bağlıdır (`prim_devam`: primi sürdürenlerin payı, baz 0), (c) ücretli ek gelir (u): ücretli çalışan rejime alınmadığından baz 0.
3. **Gelir.** T(H) = 0,135 × H (düz oran, gider tenzili yok).
4. **Giderler.** BES (tevkifatın %3'ü) ve Devlet katkısı (%20); 90 gün MYÖ primi hibesi; donanım KDV mahsubu; KGF; PTT; BT; itiraz; denetim.
5. **Sahte fatura.** Kayıp = hacim × (kurumlar vergisi %25 − %13,5) × φ × (1 − önlem) × kurumsal pay.
6. **Zaman.** Beş yıl; rampa %25, %55, %80, %100, %100; reel iskonto %5; sabit 2026 TL.

## 2. Sonuç (4. yıl, prim hiç sürmezse, milyar TL)

| Kalem (4. yıl, milyar TL) | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| Katılımcı (kişi) | 100.000 | 331.000 | 1.096.000 |
| Halen kayıtlı olup geçenlerin payı s | %30 | %15 | %5 |
| Brüt tevkifat (%13,5) | 2,36 | 9,23 | 34,63 |
| BES ve Devlet katkısı | -0,07 | -0,22 | -0,62 |
| 90 gün prim hibesi | -0,10 | -0,34 | -0,83 |
| Donanım KDV mahsubu | -0,23 | -0,62 | -1,57 |
| Yutulma: vergi | -0,40 | -0,80 | -1,00 |
| Yutulma: 4/b primi kaybı (prim hiç sürmezse) | -3,40 | -5,63 | -6,21 |
| Sahte fatura, KGF, BT, PTT, itiraz, denetim | -0,17 | -0,32 | -0,68 |
| **Net (Hazine + SGK)** | **-2,01** | **1,32** | **23,72** |
| 5 yıllık bugünkü değer (reel %5) | -6,41 | 3,70 | 71,65 |

## 3. Varyantlar (tek tek)

| Varyant (4. yıl net, milyar TL) | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| V0 Baz: oran %13,5, eski kayıtlıların primi hiç sürmez | -2,01 | 1,32 | 23,72 |
| V1 Eski kayıtlıların %50'si primi sürdürür | -0,31 | 4,13 | 26,82 |
| V2 %75'i sürdürür | 0,54 | 5,54 | 28,38 |
| V3 Hepsi sürdürür | 1,39 | 6,95 | 29,93 |
| V4 Oran %20 | -0,92 | 5,61 | 39,89 |
| V5 Oran %25 | -0,08 | 8,91 | 52,36 |
| V6 Oran %27 (üst sınır) | 0,26 | 10,23 | 57,34 |
| V7 Ücretli çalışana izin verilseydi (u=%20; reddedildi, F 3-I 302) | -2,25 | 0,40 | 20,25 |
| V8 SGK tahsil oranı π=%50 | -0,74 | 3,43 | 26,05 |
| V9 π=%100 | -2,86 | -0,09 | 22,16 |
| V10 Halen kayıtlıların hepsi geçse (s=%100) | -10,89 | -35,08 | -113,31 |
| V11 90 gün prim hibesi olmasaydı | -1,91 | 1,66 | 24,55 |
| V12 Donanım KDV mahsubu olmasaydı | -1,79 | 1,94 | 25,28 |

## 4. Ne anlama geliyor

1. **%13,5'te Orta ve İyimser pozitif, Kötümser negatiftir.** Kötümser; oran %25,5'e çıkarsa veya halen kayıtlı olanların %59'u isteğe bağlı primi sürdürürse sıfırı geçer.
2. **Ana açık risk s'dir** (halen kayıtlı olup geçenlerin payı) ve primi sürdürenlerin payıdır; ikisi de ölçülmemiştir. s=%100'de üç senaryo da olumsuzdur.
3. SGK tahsil oranı π (0,8) harici metne göre %35-40 olabilir (yoklanmadı); π=%50 ve π=%100 varyantları yukarıdadır.
4. Ücretli çalışanın dışarıda bırakılması Orta'da yaklaşık 0,9 milyar TL kazandırır (V0 − V7).
5. Her varyantın tam tablosu ve diğer parametreler `DUYARLILIK_TABLOLARI.md` içindedir.

## 5. Veri talebi (ölçülmemiş girdileri kapatacak)

| Girdi | Kurum | İstenen |
| :-- | :-- | :-- |
| s ve primi sürdürenlerin payı, eski vergi ve prim | SGK, GİB | Halen 4/b sigortalısı veya gelir vergisi mükellefi olup bu rejime başvurabilecek kişi sayısı; hizmet ve fikir sektörü hasılat dağılımı; prim tahsilat oranı |
| N | TÜİK, GİB | Serbest çalışan sayısı; 20/B kapsamındaki mükellef sayısı ve hasılatı |
| φ | GİB, MASAK | Hizmet faturalarında sahte fatura oranı |
| BES vazgeçme | EGM | Otomatik katılımda vazgeçme oranı |
| KGF | KGF, Hazine | Mikro ölçek faizsiz finansman temerrüt oranı |
| PTT, BT | PTT, GİB, BDDK | UETS birim gideri; portal ve banka entegrasyon maliyeti |
