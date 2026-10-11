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
* build_submission.py -- iki arşiv kurar: `bf18` (referans, Budget-Fit ile bayt bayt aynı 4 dosya + atıf)
  ve `locator` (özgün: yeni istem + skills/repo_navigation).
* skills/repo_navigation/scripts/locate.py -- ÖZGÜN. Sorun metninden iz/kimlik/hata dizgisi/yol ipuçlarını
  çıkarır, AST dizinine karşı puanlar, `dosya:satır` + ilgili test verir. Gerekçe: referansın kendi ölçümü
  "12. çağrıya kadar düzenleme yoksa %87 başarısız" ve grafik araçları boş dönüyor.
* skills/repo_navigation/scripts/verify.py -- ÖZGÜN. Tek çağrıda: boş/test-dokunan diff, derleme, yalnız ilgili
  testler (zaman sınırlı), "sözleşme ipucu" (sorunda geçen dizgi yamada yok mu). Sentetik depoda ayırt ettiği
  sınandı (doğru yama sessiz, yanlış mesaj ipucu veriyor).
* eval/localization_bench.py -- gerçek düzeltme commit'lerinden çevrimdışı yerelleştirme mihengi.
  137 görev (fastapi/httpx/requests/rich, ebeveyn sürümde): hit@1/3/5 = 0.51/0.81/0.89 (locate) karşı
  0.39/0.72/0.83 (tüm-dosya TF-IDF). Dosya yolları silinince 0.50/0.81/0.89. Uyarı: "sorun" olarak commit
  mesajı kullanıldı (gerçek sorun metni değil); yani bu bir vekil ölçüdür, çözüm oranı değildir.
* kernel-metadata.json -- betiği Kaggle'da koşturacak script defteri (CPU, internet kapalı).

## Ölçülmeyen (dürüstlük)
* `locator` istemi Gemma'ya karşı HİÇ koşulmadı (GPU yok). Skill betiklerinin harness'te hangi yolla
  çağrılacağı (`run_skill_script` imzası, dosyaların kutuya yerleşimi) HARNESS_README okunmadan bilinmiyor;
  istem bu yüzden `find ... locate.py` ile yolu buluyor. HARNESS_README gelince bu adım sadeleşir.
* Her iki arşivi de göndermek, LB gürültüsü (±0.06) yüzünden tek başına kanıt vermez.

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
