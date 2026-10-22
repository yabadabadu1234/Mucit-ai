# Ders sitesi

Verici ve alıcı kartlarını sıfırdan tasarlamayı öğreten site.

- `python3 veri_cikar.py` (yerelde, KiCad kütüphanesi ister): tasarımı `veri/*.json` olarak dışa aktarır. Tasarım değişince çalıştır.
- `python3 uret.py`: siteyi `site/` altına üretir (yalnız standart Python). Çizilen her şema bağlantı listesiyle karşılaştırılır; uyuşmazlıkta durur.
- `.github/workflows/ders_sitesi.yml`: her push'ta siteyi üretip `gh-pages` dalının `lora-ders/` klasörüne yayınlar.
