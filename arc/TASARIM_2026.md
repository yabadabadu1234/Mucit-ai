# ARC-AGI-2 2026 -- MÜHENDİSLİK TASARIMI (CANLI BELGE)

Dayanak: F 3-I 277, 288, 289 (`CLAUDE.md`). Olgular `arc/YARISMA_2026.md`de.
İşaret: **[Y]** yoklandı · **[Ö]** bu oturumda ölçüldü · **[Ç]** Claude çıkarımı · **[?]** bilinmiyor.

## 1. Ölçülen kısıtlar

| # | Olgu | İşaret |
| :-- | :-- | :-- |
| 1 | İndirilen "test" dosyası 240 görev / 259 çıktı; 240 görevin **hepsi eğitim kümesinde** var, eğitim ile eşleşmeyen yok: yer tutucu. Gerçek test puanlama anında gelir | [Ö] |
| 2 | Eğitim 1000 görev / 1076 çıktı; değerlendirme 120 görev / 172 çıktı; ortalama örnek sayısı 3,0-3,2 | [Ö] |
| 3 | Test yer tutucusunda istem büyüklüğü ortanca 1051, azami 6510 hücre (belirteç ≈ hücre, satır sonu dâhil) | [Ö] |
| 4 | 12 saat ve 4×L4 ile 240 görev: görev başına yaklaşık **180 saniye duvar saati** (240 görev rakamı bir 2026 raporundan, birincil metin okunmadı) | [Y] arama özeti, [Ç] bölme |
| 5 | Açık defterlerin modelleri: Qwen3.8-27B (FP8, W4A16, GPTQ, GGUF), Qwen3.8-Flash-Next (NVFP4, W4A16, 512 uzman), DFlash2 taslak modeli, Flash-Next için ayrı taslak model | [Y] `kaggle models list` |
| 6 | Bu konteynerde GPU yok; model koşan hiçbir şey burada sınanamaz. Model dışı parçalar sınandı | [Ö] |
| 7 | Her çıktı için iki deneme verilir; tek çıktılı görevde ikisi de aynı çıktıya aday | [Y] defter metni |

## 2. İki kanal, bir hakem

```
 görev ──► KANAL I  İSTİKRÂ (program yazar)  : düşünen büyük model + terminal
      │           adayı = eğitim çiftlerini geçen program ──► test girdisine uygula
      └─► KANAL T  TRANSDÜKSİYON (B katmanı) : küçük LoRA, görevin türetmeleriyle eğitilir
                  adayı = doğrudan çıktı ızgarası (D8 × renk kaydırma oylu)
            HAKEM: eğitim çiftlerini geçen program > B oyu çoğunluğu > ikisinin uyuşması
            iki deneme = en iyi iki ayrı aday
```

Gerekçe [Ç]: istikrâ yanlış kuralı eğitim çiftlerinden geçirebilir, transdüksiyon kuralı hiç yazamaz; ikisi farklı hatalar yapar. Uyuşma (aynı ızgara iki kanaldan) en güçlü işarettir.

## 3. Donatım (Kanal I)

| Araç | Ne yapar | Durum |
| :-- | :-- | :-- |
| `calistir(kod, gridler)` | Alt süreçte `solve(g)` koşar; 10 sn CPU, 2 GiB bellek haddi | **yazıldı, sınandı** (`arc/arac.py`) |
| `sinama(kod, görev)` | Her eğitim çifti için doğru/yanlış/boyut/hata + hücre farkı | **yazıldı, sınandı** |
| `test_uygula(kod, görev)` | Geçen programı test girdilerine uygular | yazıldı |
| ızgara yardımcıları (nesne etiketleme, simetri, ayna, parça, fark haritası) | Modelin terminalinde hazır içe aktarılır | yazılmadı |
| `teslim(ızgara)` | Adayı deftere yazar | yazılmadı |

Terminal: model düşünce içinde araç çağırır (vLLM `qwen3_coder` aracı ayrıştırıcısı açık defterlerde zaten kullanılıyor [Y]); ağ yok, dosya yazma yalnız geçici dizine.

## 4. KV önbelleği büyümesin

Bedel formülü [Ç]: `KV_bayt/belirteç = 2 × (tam dikkatli katman sayısı) × (KV başı sayısı) × (baş boyu) × (bayt)`. Qwen3.8 katman düzeni ve baş sayıları **okunmadı** [?]; `config.json` ve vLLM açılış günlüğündeki "GPU KV cache size" satırı ilk koşuda ölçülür.

Dört kilit, hepsi beraber:

1. **Yuva başına sabit tavan.** `yuva_sayısı × L_tavan × KV_bayt/belirteç ≤ KV havuzu`. Tavan aşılmaz; aşılacaksa sıkıştırılır.
2. **Sohbet sıkıştırma (kaide cümlesi).** Bağlam tavanın %70'ine varınca model durdurulur ve **durum notu** yazar: (a) güncel kural hipotezi, (b) her eğitim çiftinde doğrulanmış/çürümüş olgular, (c) denenmiş programlar ve **neden düştükleri**, (d) şimdiye kadarki en iyi program (kod), (e) sıradaki plan. Yeni bağlam = görev istemi + not. Not için belirteç tavanı var. Bu, F 277'deki "kaide cümlesi"nin metin kanadıdır [Ç].
3. **Düşünce izleri tarihe girmez.** `preserve_thinking` kapalı; araç çıktıları kırpılır, büyük çıktı dosyaya yazılıp adıyla anılır.
4. **Önek önbelleği.** Görev istemi her yeniden başlatmada ve B varyantlarında aynı önektir; yalnız not değişir.

Ek [?]: katmanların bir kısmı doğrusal dikkatliyse (Qwen3.5 tabanlı dendiği için ihtimal [Y: keras açıklaması], katman düzeni okunmadı) o katmanların durumu belirteç sayısından bağımsız sabittir; ölçülecek.

## 5. B katmanı (Kanal T) ve türetmeler

Eğitim verisi, **aynı görevin** türetmeleri:

| Kaynak | Üretim | Adet (görev başına) | Doğruluğu |
| :-- | :-- | :-- | :-- |
| Bırakma | n çiftten biri sınav, kalan n−1 örnek | n | görevin kendisi |
| D8 | 8 geometrik dönüşüm, hem girdi hem çıktıya | ×8 | kural dönüşümle korunuyorsa; **korunmayan görev var** |
| Renk kaydırma | 1..9 renkleri döngüsel kaydır, 0 sabit | ×9 | aynı; renk anlamı taşıyan görevde bozulur |
| Program çoğaltma | Eğitimi geçen program, dönüştürülmüş girdilere uygulanır | ×(girdi sayısı × 72) | programın doğruluğu kadar |

Ölçüm [Ö]: dönüşüm ve tersi 232 704 durumda bozuk sıfır; n örnekli görevden **n × 8 × 9 = n × 72** benzersiz bırakma türetmesi çıkar (2 örnekli görevde 144/200 benzersiz). Tekrar, benzersiz sayının ötesinde faydasızdır.

Uyarı [Ç]: D8 ve renk kaydırma her görevde kuralı korumaz (yön, sayı, renk anlamı). Korunup korunmadığı **Kanal I'in geçen programına** sorularak ölçülebilir: program dönüştürülmüş girdide, dönüştürülmüş çıktıyı veriyorsa o dönüşüm kural-korur. Program yoksa kör uygulanır ve bu risk işaretlenir.

Eğitim: tek küçük LoRA (düşük dereceli), görev başına sıfırdan, birkaç dakikanın altı hedef [?]. 4. satırdaki 180 saniye duvar saati bütün kanalları kapsar; B eğitimi **büyük modelin düşünmesiyle aynı anda** koşmak zorundadır. Aynı GPU'da 27B FP8 sunucu ile LoRA eğitimi bellekte yer kavgası yapar [Ç]; bu yüzden B'nin tabanı **küçük ayrı model** olabilir (açık defter: 3,4B LoRA [Y]). Karar bekliyor (Soru 2).

## 6. Ölçüm planı (Kaggle'da, GPU ile)

| Ölçü | Nerede |
| :-- | :-- |
| Yuva başına KV belirteç havuzu, tavan | vLLM açılış günlüğü |
| Düşünme hızı (belirteç/sn) 1 ve 16 eşzamanlı | defter |
| Görev başına ortalama belirteç, sıkıştırma sayısı, notun boyu | defter |
| Kanal I tek başına, Kanal T tek başına, hakemli birleşik doğruluk | değerlendirme kümesi (120 görev, 172 çıktı) |
| Bu doğruluklar değerlendirme kümesinde; Qwen'in bu görevleri eğitimde görmüş olabileceği **ölçülemez** | [?] |

Değerlendirme kümesi ölçü aracıdır, eğitime girmez (F 2-D 93).

## 7. Açık sualler

| # | Sual |
| :-- | :-- |
| S-T1 | "Qwen 8"in en çalıştırılabilir hâli: 27B FP8 (4×L4, TP=4) mi, Flash-Next W4A16/NVFP4 (MoE) mi? Yalnız ölçü karar verir |
| S-T2 | B'nin tabanı büyük modelin kendisi mi, ayrı küçük model mi |
| S-T3 | Kaggle'da koşturmak GPU kotanızı ve günlük gönderim hakkınızı yer; izin |
| S-T4 | D8/renk kayması kural-korumayan görevlerde B'yi bozar; program-doğrulamalı süzgeç şart mı |
