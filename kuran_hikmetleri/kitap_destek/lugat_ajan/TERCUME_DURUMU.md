# Opencode tercüme işi durumu (2026-11-21)

| Küme | Dosya | Tercümeli | Kalan |
| :-- | :-- | :-- | :-- |
| kuranda_var/kokler | 1661 | 1661 | 0 |
| kuranda_yok/kokler | 6752 | 320 | 6432 |

**Kur'ân'daki 1661 kökün tercümesi tamamdır** (bu kök sayfalarının hepsi kitapta kullanılan Türkçe metinle üretilmiştir). Bitmeyen kısım, Kur'ân'da geçmeyen kökler (kuranda_yok) kümesidir.

**Neden bitmedi (hesap).** Ücretsiz modellerin hepsi (deepseek-v4.1-flash-free, big-pickle, mimo-v2.6-flash-free, beam-free) bu oturumda `Free usage limit reached` hatası verdi; yani OpenCode hesabının ücretsiz kotası dolmuş. Betik (`opencode_tercume.py`) bu hatayı stdout'ta aramıyordu, stderr'de geldiği için kota hatasını "başarısız" sayıp bütün dosyaları saniyeler içinde geçiyordu; bu kusur düzeltildi (stdout ve stderr birlikte taranır, kota hatasında 15 dakika bekler ve yeniden dener). Kota dönene kadar betik arka planda bekler; kota dönünce 6 işçiyle kaldığı yerden devam eder. Ücretli model kullanılmadı (F 3-I 402 (3)).

Kalan iş: 6432 dosya. Başlatma komutu: `KOKLER_DIZIN=.../kelime_kaydi/kuranda_yok/kokler python3 opencode_tercume.py 6`.
