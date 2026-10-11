# Gemma 4 Developer Agent -- plan ve durum (2026-10-11)

## Soru: mucitlik mi, amelelik mi?
Ne biri ne öbürü. Model sabit (gemma-4-31b-it-qat-w4a16-ct), ölçüt SWE-bench tarzı PASS/FAIL.
Yeni teori gerekmiyor; fakat "yapıştır-çalıştır" da değil: kamuya açık deneylere göre skoru
belirleyen şeyler (a) 12 saatlik toplam süreyi ~120 görev arasında bölen zaman/araç bütçesi,
(b) istemin (prompt) "12. çağrıya kadar düzenle" gibi kuralları. Kazanan = en iyi ölçülmüş mühendislik.

## Okunan kamu kanıtı (Kaggle defterleri, 2026-10-11)
* verracodeguacas "Budget-Fit Single Agent": kamuya açık skor 0.18; tek ajan, 8 dk / 28 araç çağrısı,
  grafik araçları istemle yasak, timeout 240 s. Apache-2.0.
* dmitriigluzdov "Measure Before You Tune": aynı arşiv skoru 0.06-0.12 arasında oynuyor (gürültü
  büyük); LoRA hata ayıklama denemesi NO-GO (2/32 çözüm, taban 4/32); panel/çok-ajan mimarisi
  tek ajanı geçmedi; 120 görev için ~282 s/görev planlama payı.
* Lider tablo tepesi ~0.24 (kaynağı arşivle bağlanmış değil).

## Bu klasördeki iş
* build_submission.py -- submission.zip kurar (Budget-Fit ile bayt bayt aynı 4 dosya + ATTRIBUTION.md).
* kernel-metadata.json -- aynı betiği Kaggle'da koşturacak script defteri (CPU, internet kapalı).

## Beni durduran şeyler (hesap işi, benim aşamayacağım)
1. Veri (22 GB, HARNESS_README, örnek gönderim) giriş + kural kabulü istiyor (anonim GetDataViewExternal = 403).
2. Gönderim `kaggle competitions submit` / arayüz: Kaggle API jetonu gerekir. Kural kabulü sizin hukukî fiilinizdir.
3. Gemma-4-31B'yi çalıştırmak L4x4 GPU ister (yalnız yarışmaya bağlı Kaggle defterlerinde). Bu kutuda GPU yok;
   yerel ajan koşusu / LoRA eğitimi burada yapılamaz.

## Sıradaki adımlar
1. (Sizde) Kaggle'da yarışma kurallarını kabul et; Settings > API > jeton üret; jetonu bu oturumun
   ortam gizlisi olarak KAGGLE_API_TOKEN ver.
2. (Bende) `kaggle kernels push` ile defteri gönder, çıktıdaki submission.zip'i
   `kaggle competitions submit gemma-4-developer-agent -f submission.zip` ile yolla.
3. (Bende) Veri inince HARNESS_README'yi baştan sona oku, 129 görev üstünde yerel eşleştirilmiş deney yap
   (GPU gerektiği için bunu Kaggle L4x4 defterinde), yalnız eşleştirilmiş kazanç gösteren değişikliği ekle.
