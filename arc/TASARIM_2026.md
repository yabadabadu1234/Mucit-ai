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
| 8 | Kaggle `machine_shape: NvidiaL4` ile: **4×NVIDIA L4, her biri 23 034 MiB, sm_89**; 46 CPU çekirdeği; 188 GB RAM; `/kaggle/working` 20 GB; torch 2.11.0+cu128; peft 0.20.0; transformers 5.16.1; triton 3.6.0; **vLLM kurulu değil** (kurulum için tekerlek deposu veri kümesi gerekir). Kuyruk bekleme yaklaşık 2 dakika, betik 27 saniyede bitti. Koşu: `ulankaggle/mucit-arc-olcum0`, 10 dk hudutlu, ücretsiz kota içinde | [Ö] |
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

## 8. Ölçümler (Kaggle, 4×L4, her koşu en çok 10 dk hedefli; defterler `arc/defter/olcum0..2`)

Taban: Qwen3.5-4B (bf16, 8,51 GB/GPU), HF transformers 5.16.1, peft 0.20.0. Yerleşim: **manuel**, 4 işçi süreci, her biri `CUDA_VISIBLE_DEVICES=i` ile tek GPU'da tam kopya; `device_map` yok (F 291). Görevler: değerlendirme kümesinin en kısa 8 tek-çıktılı görevi, işçi başına 2.

| # | Ölçü | Değer | İşaret |
| :-- | :-- | :-- | :-- |
| 1 | Mimari: 32 katman, **8 tam dikkat + 24 doğrusal dikkat** (her 4. katman tam), 4 KV başı, baş boyu 256 | config.json | [Ö] |
| 2 | KV bedeli = 2 × 8 × 4 × 256 × 2 bayt = **32 768 bayt/belirteç (32 KiB)**; doğrusal katmanlar belirteç sayısından bağımsız sabit durum tutar | hesap, config'ten | [Ö] |
| 3 | Model yükleme: 72-117 sn (4 işçi aynı anda diskten) | günlük | [Ö] |
| 4 | `peft` ortamdaki `torchao 0.10.0` yüzünden kırılıyor; çözüm: `is_torchao_available` kapatıldı | hata günlüğü | [Ö] |
| 5 | Hızlı doğrusal-dikkat çekirdeği (`fla` 0.5.2) kurulmadan LoRA eğitimi 22 GB'ı aştı (OOM, 800-1000 belirteçlik dizide) | günlük | [Ö] |
| 6 | `fla` + gradyan kontrol noktası + yalnız cevap konumlarında kayıp ile zirve bellek **9,2-10,0 GB** | günlük | [Ö] |
| 7 | **İlk çağrıda ~55 sn JIT/derleme** (eğitim ilk görevde 1 adım atabildi); ikinci görevde **41-50 adım / 45 sn**, yaklaşık 880 belirteç/sn, adım başına yaklaşık 1 sn | günlük | [Ö] |
| 8 | HF `generate` bir çıktı için 8-40 sn (ısındıktan sonra), ilk çağrıda 49-60 sn | günlük | [Ö] |
| 9 | Kayıp: bazı görevlerde 0,003'e düştü (ezberledi); diğerlerinde 0,12-0,16 | günlük | [Ö] |
| 10 | **Doğruluk: LoRA öncesi 0/4, 45 sn LoRA sonrası 0/4** (iki görev işçi başına, sekiz görevden dört tanesi sonuna kadar yürüdü) | günlük | [Ö] |
| 11 | Platform: betik süresine ek yük 41-60 sn (bir koşuda 632 ve 992 sn "RUNNING" gözlendi, betik 58 ve 143 sn'ydi; sebebi bilinmiyor) | durum sorguları | [Ö] |

Yorum [Ç]: ARC'a önceden hiç eğitilmemiş bir tabana 45 sn'lik görev-içi eğitim kural öğretmedi; kayıp düştü ama test çıktısı tutmadı (4 görev, küçük örnek). Bu, NVARC'ın önce büyük sentetik ARC külliyatıyla ön eğitim yapıp sonra görev başına ince ayar yapmasının gerekçesini ölçüyle destekler. Sonuç görev sayısı küçük olduğu için kesin hüküm değildir.

Bütçe [Ç]: 240 görev / 12 saat = 180 sn/görev. Isınma 55 sn bir kerelik (işçi başına), eğitim 45 sn, üretim 10-40 sn: sığar, fakat tek işçi sırayla 240 görev yapamaz; 4 işçi × 60 görev × (45+25 sn) = 70 dk. Yük burada üretim hızıdır (HF `generate`); vLLM ile LoRA'lı üretim ayrıca denenmeli.

## 9. NVARC'ın açık hattından okunanlar (`yiheng/reproduce-nvarc-2025-results`, 9 hücre, baştan sona okunmadı; ilk altı hücre okundu)

| # | Olgu | İşaret |
| :-- | :-- | :-- |
| 1 | Her GPU için ayrı işçi süreci, `CUDA_VISIBLE_DEVICES=rank`: bizim manuel yerleşimimizle aynı kalıp | [Y] |
| 2 | Kelime hazinesi **16 belirtece** indirgenmiş: rakamlar 0-9, satır sonu, kullanıcı/asistan/boşluk/bitiş işaretleri (`ARC_VOCAB`). Bizim OOM'un sebebi olan 248 bin kelimelik logit tablosu yoktur | [Y] |
| 3 | Biçim: satır başına rakam dizisi, `\n` ayırıcı (bizimkiyle aynı) | [Y] |
| 4 | Çıkarım: artırma + ışın puanı toplamı (`getter_full_probmul_3`: çıkarım puanı + artırma puanı) ile adaylar oylanır | [Y] |
| 5 | Açık veri kümeleri: `sorokin/nvarc-synthetic-puzzles` (338 MB), `sorokin/nvarc-augmented-puzzles` (1,3 GB; arc2_training, concept, mini...), `sanyul/nvarc-full` (11,9 GB) | [Y] listeler |
| 6 | Hazır ince ayar ağırlıkları: `madarshbb/nvarc-training-adapters-1..4` (12,4 GB'lık dört veri kümesi) | [Y] listeden, içeriği açılmadı [?] |

Sonuç [Ç]: kanal T'yi sıfırdan kurmak yerine (a) kelime hazinesini 16'ya indirmek, (b) NVARC'ın açık sentetik bulmaca külliyatıyla ön eğitilmiş taban kullanmak gerekir; aksi hâlde § 8 satır 10'daki 0/4 tekrar eder.

## 10. Qwen3.8-27B ölçümü (F 3-I 292; olcum3, 4×L4, manuel yerleşim)

NOT (F 3-I 292): § 8-9'daki Qwen3.5-4B ölçümleri **yanlış modelle alınmıştır** (padişah Qwen3.8 dedi; 4B'ye geçiş örtük ikameydi). Silinmedi, işaretlendi. Ayrıca o koşularda modelin ürettiği metin kaydedilmemişti; "model ne dedi" sorusuna cevap yoktur.

| # | Ölçü | Değer | İşaret |
| :-- | :-- | :-- | :-- |
| 1 | Qwen3.8-27B: 64 katman, **16 tam dikkat + 48 doğrusal dikkat**, 24 dikkat başı, **4 KV başı**, baş boyu 256, sözlük 248 320, bağlam 262 144, `mtp_num_hidden_layers` 1 | HF config.json | [Y] |
| 2 | **KV bedeli = 2 × 16 × 4 × 256 × 2 bayt = 65 536 bayt/belirteç (64 KiB, bf16)**; fp8 KV ile 32 KiB. 32 bin belirteç = 2 GiB (bf16) | hesap | [Ö] |
| 3 | Resmî FP8 ağırlıkları 30,9 GB; `FineGrainedFP8Config(dequantize=True)` ile bf16'ya açıldı | Kaggle model bilgisi, günlük | [Ö] |
| 4 | Elle yerleşim: 64 katman 4 parçaya (0-15, 16-31, 32-47, 48-63); gömme+görsel GPU0'da, norm+`lm_head` GPU3'te. GPU belleği **14,7 / 12,2 / 12,2 / 14,7 GB** | günlük | [Ö] |
| 5 | `transformers` 5.16.1'in FP8 niceleyicisi `update_tp_plan`'da çöküyor (`NoneType.get`); niceleyicinin bu metodu etkisizleştirilerek aşıldı | hata günlüğü | [Ö] |
| 6 | Yükleme **202 sn** | günlük | [Ö] |
| 7 | HF `generate` + elle boru hattı: **3,81 belirteç/sn** (877 belirteç, 230 sn); bir anda tek GPU çalışır (%25 doluluk) | günlük | [Ö] |
| 8 | 240 görev × tek akış × 3,81 belirteç/sn ile 12 saatte görev başına yalnız yaklaşık 680 belirteç düşer: **HF boru hattı yarışmaya yetmez; toplu (eşzamanlı) çıkarım şart** | hesap | [Ç] |

Modelin ilk görevde (`e8686506`, doğru cevap 8×5 ızgara) ürettiği tam metin `arc/defter/olcum3/cikti_e8686506.txt`: 877 belirtecin **tamamını** örnek ızgaraları satır satır yeniden yazmaya ve sütun saymaya harcadı ("Let's count: Row0: 8888888888888 (13)…"), arka plan rengini 0 mı 8 mi diye tarttı, kurala hiç varmadı, cevap üretmedi. Süre sınırım (230 sn) üretimi kesti; modelin düşünme kalitesi hakkında hüküm vermek için yetersizdir.

Çıkarım [Ç]: modelin ilk işi ızgarayı yeniden yazıp saymak olduğundan, boyut/renk/nesne dökümünü **araç** verirse (F 3-I 289) bu belirteçler kurala ayrılır.
