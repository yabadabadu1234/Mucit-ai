# ARC PRIZE 2026 -- ARC-AGI-2 YARIŞMASI: YOKLANAN OLGULAR VE ÇIKARIMLAR (CANLI BELGE)

Dayanak: F 3-I 277, 288 (`CLAUDE.md`). Tarih: 2026-10-12.
İşaret: **[Y]** yoklandı (kaynak yanında) · **[Ç]** Claude çıkarımı · **[?]** bilinmiyor.

## 1. Yoklanan olgular

| # | Olgu | Kaynak | İşaret |
| :-- | :-- | :-- | :-- |
| 1 | Bitiş 2026-11-02 23:59; 2783 takım; ödül 700 000 $ | `kaggle competitions list -s arc-prize-2026` | [Y] |
| 2 | Hedef: özel kümede %85; bonus 150 000 $ ilk ≥ %85'e; ilerleme ödülleri 275 000 $ (1.'ye 75 000 $) | arcprize.org/competitions/2026/arc-agi-2 | [Y] |
| 3 | Notebook teslimi, değerlendirmede internet yok, ödül için kod ve yöntem açık kaynak şart | aynı | [Y] |
| 4 | Tablo test verisinin yaklaşık %50'siyle hesaplanıyor; final öbür yarıyla | Kaggle yarışma sayfası (arama özeti) | [Y] |
| 5 | Tablo (2026-10-11 görüntüsü): Tufa Labs 88,06 · rabbithole 80,56 · Yi-Chia Chen 77,22 · nvbanana 77,08 · _hans 69,03 · ALbert RUehlman 67,36 · Dawid Kopiczko 62,92 · ARC Raiders 62,08 · Majkel1337 52,50 · matu997 50,83 … padişah 87. sırada | `kaggle competitions leaderboard -s` | [Y] |
| 6 | 2025: birinci NVARC özel kümede %24,03 (kamuya açık tabloda %27,64), ARChitects %16,53, MindsAI %12,64; 1455 takım | arXiv 2601.10904, arcprize.org/blog/arc-prize-2025-results-analysis | [Y] |
| 7 | Herkese açık defterlerin tavanı yaklaşık 33-34 puan ("LB33.89 perfpatch" ve çatalları); en çok oy alanlar NVARC 2025 yeniden üretimleri | `kaggle kernels list` | [Y] |
| 8 | Tablo başı 80-88 puan hiçbir açık defterde yok; yöntemleri yayımlanmamış | aynı + arama | [Y] |
| 9 | 2026 açık defterleri: Qwen3.8-27B FP8, vLLM, tensör paralel 4, 4×L4, düşünme açık, sıcaklık 0, 12 saat; Qwen3.6-35B-A3B 3 saat; Qwen 3.4B LoRA + simetri doğrulayıcı + AIRV + DFS | `kaggle kernels pull` (delongyang, yukailiu) | [Y] |
| 10 | Bu defterlerin ürettiği puan defter çıktılarında yoktur | çıktı hücreleri boş | [Y] |

## 2. Yoklanmayan

- 80+ puanın yöntemi [?]. Tufa Labs / rabbithole yazılarını bulamadım.
- Kaggle'ın 2026 donanım ve süre sınırı sayfadan okunamadı; defterler 4×L4 ve 12 saat gösteriyor, bir 2026 raporu 4×L4, 12 saatte 240 görev diyor (arama özeti, birincil metin okunmadı).
- Test kümesinin 2025 özel kümesiyle ilişkisi [?].

## 3. Çıkarımlar [Ç] (hüküm değildir)

- H1 **Taban model sıçraması:** 2025'te 4B'lık, sentetik veriyle eğitilmiş model vardı; 2026'da 27-35B düşünen açık modeller var. Tek başına akıl yürütme + doğrulayıcı büyük sıçrama verebilir.
- H2 **Doğrulanabilir döngü:** model program/ızgara üretir, eğitim çiftlerinde sınanır, hata geri beslenir (2025 raporunun "iyileştirme döngüsü" teması; Poetiq'te 31 → 54).
- H3 **Test anı eğitimi + artırma oyu** (NVARC çizgisi) taban modelin üstüne.
- H4 **Veri sızıntısı / ezber:** genel ARC-AGI-2 görevleri açık modellerin eğitiminde olabilir (2025 raporu "bilgi aşırı uydurması" uyarısı veriyor). Tablo %50 üzerinden; final farklı çıkabilir.

## 4. 76 puanlı defter: nguyennguyen599/dsv41-tools-submit-b32m-external-server (okundu: 2026-11-07)

Okunan: defterin bütün 26 hücresi, içine gömülü çözücü/koşum kitinin (solver_dsv41.py, run_deepseek_tools.py, train_check.py) bütün metni, Kaggle Model sayfasının açıklaması (chankhavu/dsv41-flash-1017-arc-tool-e128-2bit). Defterde skor çıktısı yoktur; "76" rakamı [?] (padişahın sözü, yoklanmadı). Okunmayan: `vllm-wheels` ve `arc2-2026-src` veri kümeleri (403, kapalı), `auto_repair.py` ve `solve` gövdesinin 1200 sonrası kısmı kısmen.

| # | Olgu | Kaynak | İşaret |
| :-- | :-- | :-- | :-- |
| 1 | Model: DeepSeek-V4.1-Flash-1017 (MIT); her katmanda 384 uzmandan 128'i tutulmuş (10M belirteçlik araçlı koşu izlerinde katkı puanıyla, araç çağrısı blokları 10 kat ağırlıklı); uzmanlar 2 bit GPTQ (Humming düzeni); 64 GiB sıkıştırılmış Engram; toplam 131 GB, 136 dosya | Model sayfası, defter hücre 7 | [Y] |
| 2 | Aynı koşum, tam model (DeepSeek API): 120 değerlendirme görevi, pass@1 %74,5, pass@2 %84,9, ortalama 27,4K çıktı belirteci, 13,9 tur. Budanmış 2 bit: pass@1 %72,8, pass@2 %82,5, 35,2K belirteç, 17,1 tur | Model sayfası (yazarın kendi ölçümü; ben doğrulamadım) | [Y] yazar beyanı |
| 3 | Yöntem tür: araçlı akıl yürütme. Kalıcı Python oturumu (`run_python`, `train`, `test_input`, numpy, scipy), `submit_answer` ile cevap `solve(test_input)` ifadesi olarak teslim; harness önce `solve`ü bütün eğitim çiftlerinde koşar | run_deepseek_tools.py | [Y] |
| 4 | İstem (`lean2sub`): "gridleri elle okuma, kopyalama, sayma; kodla incele; hipotezi her eğitim çiftinde kodla sına; uymayan çifti açıklayıp geçme" | run_deepseek_tools.py | [Y] |
| 5 | Cevap seçimi: her çiftin 2 denemesi; `train_check` her deneme bitince cevabı üreten programı eğitim girdilerinde yeniden koşar (4 yol: ifade, hücre, fonksiyon, transkript tekrarı); eğitimi geçenler önce, sonra deneme sırası, iki farklı ızgara | train_check.py | [Y] |
| 6 | Bütçe: tur başına 64K, deneme başına 80K çıktı, 40K yumuşak, 40 tur, sıcaklık 1,0, çaba 50 | solver HARNESS, model sayfası | [Y] |
| 7 | Çok test girdili görevde tek yürütme (liste cevap), bütçe (1+0,5(n−1)); 45 çok çiftli görevde pass@2 %83,1 (çift başına %77,5) ve %29 az belirteç | defter hücre 2 yorumu | [Y] yazar beyanı |
| 8 | Sunucu: vLLM çatalı 0.28.1rc1 (cp313 tekerlekler, CUDA 13), tensör paralel 4 (GPU sırası 0,2,1,3), DCP, fp8 KV, KV'nin CPU'ya boşaltılması, 64 eşzamanlı dizi (80 işçi), bağlam 163 840, önek önbelleği, Humming 2 bit MoE çekirdekleri L4 için elle ayarlı karolar, host all-reduce | defter hücre 15, model sayfası | [Y] |
| 9 | Hız (yazarın): 4×L4'te 40 akışta 340-350 üretim belirteci/sn, ~35 deneme/saat; `--token-exact` olmadan önek önbelleği bozulup 177'ye düşer; KV %0,89'da 381 → 196 | Model sayfası, solver yorumu | [Y] yazar beyanı |
| 10 | Önlemler: ilk hücrede geçerli yedek submission; her deneme sonunda atomik yazım; sürücü güvenlik zamanlaması (yeni deneme durdurma, akış kesme, sert durdurma); gzip ile döngü bekçisi; sunucu denetçisi 3 yeniden başlatma; KV doluluğuna göre kabul | solver, hücre 15 | [Y] |

Çıkarımlar [Ç] (padişahın sözü değil):
- C1 Puanın ana kaynağı mühendislik hilesi değil, **güçlü bir taban model + araçlı akıl yürütme + eğitimde doğrulama**dır (tam modelin API'de %84,9 pass@2'si, budamanın kaybı 2,4 puan). 4×L4'e sığdırma işi ayrı ve ağır bir mühendislik (budama + 2 bit + çatal vLLM).
- C2 Ortalama deneme 35K belirteç; 100K belirteç/görev (F 293) onların harcamasının ~3 katıdır. Puanı belirleyen şeyin belirteç miktarı mı, model kalitesi mi olduğu bu belgede ölçülmedi.
- C3 Bizim F 289 donatımı (terminal, analiz araçları, eğitim çiftlerinde doğrulama) bu koşumun aynısı yönündedir; farklar: onlarda doğrulama harness'te zorunlu (`train_check`, `submit_answer` kapısı), model tokenizer'la tam belirteç geçmişi tutar (`--token-exact`).
- C4 Bizim vLLM engelimiz (cp313, torch 2.11) için onların kullandığı `nguyennguyen599/vllm-wheels` (cp313) kapalı, yoklanamadı.
- C5 Gizli test %50 üzerinden ölçülen 76 ile 120 görevlik değerlendirmede %82,5 arasındaki fark (taslak açıklama: dağılım farkı) ölçülmedi.
