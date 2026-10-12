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
