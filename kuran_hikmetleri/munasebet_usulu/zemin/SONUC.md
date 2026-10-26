# Zemin: embedding vektörleri üstünde üç makalenin modeli

Zemin: Qwen3.5 (0,8B / 2B / 4B) token vektörleri ve bağlam durumları. Metin: `veri_harici/eyupipler/quran-morphology.txt`ten kelimeler, 114 sûre, 6236 âyet, 77 429 kelime parçası.

| Makale | Kod | Zemin üstünde kurulan |
| :-- | :-- | :-- |
| Tsipidi 2024 | `vektor.py`, `uret_surpriz.py`, `tsipidi.py` | −log p(kelime \| önceki) her kelime için, 2048'lik pencere; yapı öngörücüleri; ridge, 5 katlı çapraz sınama (sûre gruplu), ΔMSE |
| Roberts 2012 | `alaka.py` | Alâka (15)/uygunluk (25): ihtiyaç ↔ âyet, LM olabilirliğiyle; yön A: log p(âyet \| sual) − log p(âyet); yön B: log p(ihtiyaç \| âyet) |
| Tsvilodub 2026 | `tsvilodub.py` | Karar modeli; makalenin parametreleriyle (ε, δ) = (0,17; 0,32), (0,49; 0,32), (0,49; 0,11) için P(r_cq) = 0,491 · 0,623 · 0,437 |

## Elle yazılanlar
`alaka.py`'deki `OLUMSUZ` (her ihtiyacın olumsuzu), `FATIHA_KARARLAR.json`'daki ihtiyaç metinleri ve karar–âyet eşleşmeleri, kısım sınırları (`sureler/*/sure.md`).

## Sayılar
**Şaşırtıcılık ve yapı (0,8B; 114 sûre; 77 315 kelime; kısımlı 53 358).** Taban: token sayısı, önceki kelimenin şaşırtıcılığı, âyetin kelime sayısı, log(sûredeki kelime sırası). Taban MSE 25,79 (kelime), 6,72 (5'lik ort.).

| Öngörücü | ΔMSE kelime | ΔMSE 5'lik |
| :-- | :-- | :-- |
| âyet içi konum + sınır (nesir) | −0,148 | −0,063 |
| kısım göreli konum | +0,014 | +0,005 |
| kısım en yakın sınır | +0,002 | +0,000 |
| kısım hiyerarşik konum | +0,016 | +0,006 |
| sûre hiyerarşik konum | +0,019 | +0,019 |
| hepsi | −0,120 | −0,042 |

Kısım yapısı, âyet yapısının üstüne şaşırtıcılık öngörüsü katmadı.

**İhtiyaç ↔ âyet (Fâtiha; 15 ihtiyaç; 8 aday âyet; tesadüf: ilk sıra 1,88/15, MRR 0,34).**

| Yön / model | ilk sıra | MRR | olumsuzu daha yüksek bulunan çift |
| :-- | :-- | :-- | :-- |
| A 0,8B | 4/15 | 0,457 | 4/15 |
| A 2B | 2/15 | 0,317 | 5/15 |
| A 4B | 3/15 | 0,420 | 3/15 |
| B 0,8B | 6/15 | 0,547 | 11/15 |
| B 4B | 6/15 | 0,551 | 2/15 (ortalama fark +1,99) |

B 4B ihtiyaç bazında: 1:5, 1:6, 1:7'nin altı ihtiyacının altısı da ilk sıra (I3a, I3b, I5, I4a, I4b, I4c). 1:1–1:4 ve 2:2'nin dokuz ihtiyacında hedef âyet 2.–7. sırada (I1d 4, I1a 2, I2 4, H1 3, I1b 6, H2 7, I1c 5, H3 6, I6 4).

**Âyet bazında z-skoru (yön B, 4B).** Her âyet için 15 ihtiyacın log p'si o âyetin ortalama ve sapmasıyla standartlaştırıldı (âyetin kendine has uzunluk ve kolaylığı sıradan çıkar).

| Yön / model | ilk sıra | MRR | olumsuzu daha yüksek bulunan çift |
| :-- | :-- | :-- | :-- |
| B 4B, z-skorlu | 8/15 | 0,697 | 2/15 (ortalama fark +0,10 sapma) |

Hedef âyeti ilk sıra olanlar: I1d, I1a, H1, I3a, I3b, I5, I4a, I4b. Sıra: I2 3, I1b 2, H2 5, I1c 2, H3 4, I4c 6, I6 2.
