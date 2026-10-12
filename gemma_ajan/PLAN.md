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
  ve `locator` (özgün: yeni istem + skills/repo-navigation).
* skills/repo-navigation/scripts/locate.py -- ÖZGÜN. Sorun metninden iz/kimlik/hata dizgisi/yol ipuçlarını
  çıkarır, AST dizinine karşı puanlar, `dosya:satır` + ilgili test verir. Gerekçe: referansın kendi ölçümü
  "12. çağrıya kadar düzenleme yoksa %87 başarısız" ve grafik araçları boş dönüyor.
* skills/repo-navigation/scripts/verify.py -- ÖZGÜN. Tek çağrıda: boş/test-dokunan diff, derleme, yalnız ilgili
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

## Durum (2026-10-11 22:55 UTC)
* GÖNDERİLDİ: `locator` arşivi, ref 57087206, durum PENDING. Günlük gönderim hakkı doldu ("0 submissions remaining
  today"); referans arşiv (`bf18`) kontrol olarak ertesi gün gönderilebilir.
* Kaggle jetonu yalnız komut ortamı değişkeni olarak kullanıldı; depoda/dosyada yok (tarandı). Sohbette göründüğü
  için sahibi Kaggle > Settings > API'den iptal edip yenilemelidir.
* Harness kaynağı (`metric/gemma-4-developer-agent-wheelhouse`: google-adk 1.36.1, adk-submission 0.2.13,
  swegemma 0.2.11) indirilip okundu. Bulgular: (1) skill adı kebab-case olmalı (`repo_navigation` ile arşiv
  DERLENMİYORDU, düzeltildi); (2) `run_skill_script` betiği geçici dizinde `runpy` ile koşturur, cwd /workspace
  değildir, sıfırdan farklı çıkış kodu stdout'u kaybettirir -> betikler her zaman 0 ile çıkar ve /workspace'i
  açıkça kullanır; (3) `read_file` 150 satır, komut çıktısı 5000 karakter sınırlı.
* Doğrulama: `eval/harness_check.py` arşivi GERÇEK adk-submission ile derler ve betikleri GERÇEK run_skill_script
  sarmalayıcısıyla sentetik depoda koşturur (boş diff / yanlış mesaj / sözdizimi hatası ayırt edilir).
* Gerçek 129 görevde yerelleştirme (`eval/real_bench.py`, base_commit ağacı): locate hit@1/3/5 = 0.50/0.72/0.80,
  tüm-dosya TF-IDF 0.36/0.56/0.67. FastAPI (67): 0.46/0.72/0.84 karşı 0.25/0.52/0.66; Rich (48): 0.48/0.67/0.71
  karşı 0.40/0.50/0.58; requests (13): 0.69/0.92/0.92 karşı 0.77/0.92/1.00 (TF-IDF önde).

## Ölçülmeyen (dürüstlük)
* İstem Gemma'ya karşı HİÇ koşulmadı (GPU yok); gerçek skor yalnız LB'den gelir ve LB gürültüsü ±0.06'dır.
* Gerçek harness'in `ctx.code_executor` değerinin hangi yürütücü olduğu kaynaktan okunmadı (swegemma agent_runner
  okunmadı); görev metni "run_skill_script Docker kutusunda koşar" diyor.

## Sıradaki adımlar
1. LB sonucunu bekle (`kaggle competitions submissions gemma-4-developer-agent`).
2. Ertesi gün `submission_bf18.zip` kontrol olarak gönder; iki skoru yan yana yaz (gürültü payıyla).
3. `swegemma eval` yerelde Docker+GPU ister; Kaggle L4x4 defterinde eşleştirilmiş koşu yapılabilir.

## GPU deneyleri (2026-10-12)
Ayrıntı: `eval/GPU_SONUCLARI.md`. Özet: 3 aşamalı "wide" tasarım gerçek Gemma ile uçtan uca çalıştı, ama sağlam görevlerde
referans tek ajanla aynı sonucu aldı (4/5 = 4/5); ek getiri yok. Bekleyen gönderim 57087206 (`locator` v1) `--` tuzağı hatasını
içerir (model `positional_args` kullanınca locate çalışmaz); düzeltilmiş sürüm bu dalda.
