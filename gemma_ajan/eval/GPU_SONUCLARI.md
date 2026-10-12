# GPU deneyleri (Kaggle 4xL4, gerçek swegemma harness, `subprocess` sandbox; yarışmaya GÖNDERİM YOK)

Her koşu 30 dakika sınırlı (vLLM açılışı ~6,5 dk dahil). Örneklem çok küçük: sonuçlar doğruluk farkı için kanıt değildir.

| görev (veri seti zorluğu) | referans (bf18, tek ajan) | wide (scout > 3 paralel öneren > yargıç) |
| :-- | :-- | :-- |
| fastapi_14786 (8/8 çözmüş) | ÇÖZDÜ 61 sn, 9 çağrı | ÇÖZDÜ 174 sn, 19 çağrı (yama bayt bayt aynı) |
| rich_3518 (3/8) | ÇÖZDÜ 93 sn, 15 çağrı | ÇÖZDÜ 371 sn, 49 çağrı (yama bayt bayt aynı) |
| rich_3006 (3/8) | ÇÖZDÜ 96 sn, 19 çağrı | ÇÖZDÜ 79 sn, 10 çağrı |
| fastapi_13537 (4/8) | ÇÖZDÜ 150 sn, 10 çağrı | ÇÖZDÜ 208 sn, 12 çağrı |
| rich_3296 (3/8) | ÇÖZMEDİ (2 test kalır) 350 sn | ÇÖZMEDİ: boş yama, öneren dallar OLD metni tutturamadı, zaman aşımı |
| fastapi_14303 (4/8) | ÇÖZMEDİ: ortam (dirty_equals yok) | aynı ortam hatası |
| requests_6592 | (koşulmadı) | yama doğru, ortam hatası (httpbin fixture özyinelemesi, 185 hata) |
| rich_3469 | (koşulmadı) | ÇÖZMEDİ: sorun metni yalnız "fix superfluous space" + bağlantı |

Sonuç: sağlam görevlerde 4/5 = 4/5. Ek getiri ölçülmedi.

## Öğrenilenler (kaynak ve koşudan)
* İstem sınır koymaz: keşifçi "en çok 8 çağrı" dedik, 37 çağrı yaptı. Sınırı yalnız araç kısıtı ve araç tarafı sayaç koyar.
* run_skill_script betiği geçici dizinde runpy ile koşar; sıfırdan farklı çıkış stdout'u kaybettirir; model `args`, `positional_args` karışık kullanır (ADK araya `--` koyar): betikler hepsine dayanmalı.
* Skill adı kebab-case olmalı (yoksa arşiv derlenmez). Betik `select.py` adı stdlib ile çakışır.
* Beceri kodu /workspace içine geçici dosya olarak yazılır: dizini (git index) değiştirmeyin; yoksa yamada iz kalır.
* ParallelAgent dalları gerçekten eşzamanlı koşar, ama boru hattı en yavaş dalı bekler.
* Sorun metinleri çoğu zaman PR başlığı + bağlantıdır; bazı görevler metinden çözülemez.
* Referans ajan görev başına ~60-150 sn kullanır; 12 saat / ~120 görev = ~360 sn payı var: zaman payının yarısından fazlası kullanılmıyor.
* Sandbox ortamı bazı görevleri bozuk ölçer (requests httpbin, fastapi dirty_equals): veri setindeki "sound" listesini kullanın.
