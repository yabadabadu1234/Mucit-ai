# Ders sitesi

Verici ve alıcı kartlarını sıfırdan tasarlamayı öğreten site.

- `python3 veri_cikar.py` (yerelde, KiCad kütüphanesi ister): tasarımı `veri/*.json` olarak dışa aktarır. Tasarım değişince çalıştır.
- `python3 uret.py`: siteyi `site/` altına üretir (yalnız standart Python). Çizilen her şema bağlantı listesiyle karşılaştırılır; uyuşmazlıkta durur.
- `.github/workflows/ders_sitesi.yml`: her push'ta siteyi üretip denetler, sonra yayın iş akışını tetikler. Pages kaynağı "GitHub Actions"tır ve `github-pages` ortamı yalnız `claude/kuran-hikmetleri` dalından yayına izin verir; o daldaki `pages.yml` iki siteyi tek pakette birleştirir (kök = Kuran Hikmetleri, `/lora-ders/` = bu site) ve bu dalın güncel halini çeker. Pages ayarı değiştirilmez.
