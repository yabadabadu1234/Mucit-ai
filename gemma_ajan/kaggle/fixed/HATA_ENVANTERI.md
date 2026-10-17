# Hata envanteri (sürüm 10 + son kaynak + eğitimci + paketleyici)

Durum: KOD = yerelde düzeltildi ve test edildi · ÇALIŞMA = GPU'da doğrulanması gerekiyor (onay bekliyor) · AÇIK = benim kodumla kapatılamıyor

| # | Hata | Kanıt | Durum |
|---|---|---|---|
| E1 | Eğitimde doğruluk formülden (`exit_code`, `patch_overlap` adımdan) — gerçek test yok | trainer satır 718-727 | KOD: `trainer_fixed.py` yalnız `verified: true` yörüngeleri kabul eder |
| E2 | Gradyan çarpanı her zaman 1.0 (no-op) | trainer satır 755-766 | KOD: kaldırıldı |
| E3 | DoRA (`m`, `dora_m`), vLLM desteklemez: `ValueError: vLLM does not yet support DoRA` | kullanıcı logu | KOD: LoRA sargısı; kernel `dora_m` varsa hata veriyor. ÇALIŞMA: yeni adaptör eğitilmeli |
| E4 | Sohbet şablonu yok, kayıp tüm token'larda | trainer `tok.encode(doc)` | KOD: `encode_with_mask` (mock şablonla test edildi; gerçek Gemma şablonu GPU'da doğrulanmalı) |
| E5 | Dört uyumsuz veri kümesi (glaive=genel fonksiyon çağırma, moatless=lokalizasyon, openhands/swe_agent=başka ajan biçimleri) | parquet örnekleri | KOD: kaldırıldı. AÇIK: doğrulanmış veri henüz yok |
| E6 | Adım 2060'a zorla kilitleniyor, eski DoRA ağırlıkları devralınıyor | trainer `load_state`, `load_existing_weights` | KOD: kaldırıldı |
| E7 | "ZAFER / DOĞAL BİTİŞ" durma koşulları formülden | trainer satır 775-785 | KOD: kaldırıldı, durma = veri biter |
| E8 | Gönderimde fold: `B*m` (DoRA eşdeğer değil) | kernel satır 213-223 | KOD: fold kaldırıldı, `sanitize_adapter` yalnız config |
| E9 | Ölü kod "Intelligent resolution check" (`pass`) | kernel satır 341-346 | KOD: kaldırıldı |
| E10 | `locate.py` kardeş modül `summarizer`'ı içe aktarıyor → harness'te `locate` çöküyor (harness_check ile yeniden üretildi) | `harness_check`: AssertionError | KOD: kernel artık repo'nun `wide` arşivini gömüyor (summarizer yok). `harness_check` GEÇİYOR |
| E11 | Deneme sınırı betikte zorlanmıyordu; `NOT SAVED` döngüsü | propose.py | KOD: 3 denemeden sonra `STOP`; test edildi (4. çağrı STOP) |
| E12 | `propose.py`/`choose.py` mesajı `read_file` öneriyor; önericiler `read_file` kullanamıyor | choose.py satır 81 | KOD: CODE bloğu / context.py öneriliyor |
| E12b | Sayaç dosyası yazımında hata (`open("w")` önce boşaltıyor) | test sırasında bulundu | KOD: düzeltildi, test edildi |
| E13 | Bağlam taşması 32768 (girdi 30721 + çıktı 2048) | sürüm 10 logu | KISMEN: sıkıştırma eşiği 25000→12000. ÇALIŞMA: ölçülmedi |
| E14 | Model `skill_name` yerine bozuk biçim üretiyor (`` `,skill_name: ``), Japon parantezi | sürüm 10: 47 + 8 olay | AÇIK: model davranışı; eğitimle (E4/E5 düzeltmesi + doğrulanmış veri) ele alınır. Kodla kapanmaz |
| E15 | Önericiler kodun zaten `is` içerdiğini görüp `==` hipotezi ile dönüyor (sahte öncül) | sürüm 10 log, proposer'lar | AÇIK: scout'un CODE bloğu doğrulanmadan; kısmi azaltma yok |
| E16 | Paketleyici kopyası: eski trainer çıktısı varsayımı | packer | KOD: kaynak kullanılmadı; değişiklik gerekmedi |

## Çalışma sırası (onay gerektiren adımlar sırasıyla)
1. Doğrulanmış veri üret: bizim koşularımızdan testi GEÇEN yörüngeler (base wide6'da 4 görev çözüldü — bunların yörüngesi `traces/` içinde). Sayı çok az; bu yüzden tek başına yetmez.
2. Adaptörsüz taban + düzeltilmiş kernel (E10, E11, E12 etkisi) — GPU koşusu, onay gerekir.
3. `trainer_fixed.py` ile LoRA eğitimi (doğrulanmış veriyle), GPU, onay gerekir.
4. Eğitilmiş adaptörle aynı görevler: `ValueError: DoRA` gitmiş olmalı; `skill_name` hatası sayılır ve karşılaştırılır (E14).

Açık kalanlar (E13 ölçümü, E14, E15) GPU koşusu olmadan kapanmaz.
