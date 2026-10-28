# Otomatik dış ölçü (F 3-I 316)

## Niçin

F 3-I 315'teki Z3 sınamasında senaryoları ve kabul şartlarını ben yazmıştım; 14/14 sonucu yarı yarıya totolojiydi. Padişah, kabul şartlarının benden gelmemesini emretti.

## Neyi ben koymadım

| Kalem | Kaynağı |
| :-- | :-- |
| Sualler ve altın cevaplar | bAbI tasks_1-20_v1-2, en-10k (Facebook AI Research); arşivin sha256 değeri `84f5296a…573c` |
| Geçme ölçüsü (≥ %95) | Weston vd. 2015, arXiv:1502.05698 |
| Puanlama | tam eşleşme, otomatik (`kos.py`) |

## Neyi ben koydum (ve nasıl bağladım)

1. Çözücüyü ben yazdım (`cozucu.py`). Göreve mahsus bir kaide yoktur; 20 görev tek bir modelde, yalnız tren kısmından öğrenilir. Mimari, uçtan uca hafıza ağıdır (Sukhbaatar vd. 2015); şemanın üç unsuru buna anahtar olarak bağlıdır:
   - `hifz` hafıza yuvalarını açar ya da kapatır.
   - `terkip` üç adımlı zincirlemeyi açar ya da kapatır.
   - `kip_zaman` zaman kodlamasını açar ya da kapatır.
2. Şemanın tahminini, yani hangi unsur kapanınca hangi görevin düşeceğini, ben yazdım (`onkayit.py`, `TAHMIN_DUSEN`). Bu bir kabul şartı değildir, sınanan iddiadır.
3. **Mühür:** `onkayit.py`, test kısmı okunmadan evvel çözücünün, koşturucunun ve verinin sha256 değerlerini `ONKAYIT.json`a yazdı. Bu kayıt git'e işlenip itildi; commit `390a579`, tarih 2026-10-28 18:34 UTC. `kos.py`, değerler tutmazsa puan vermez (çıkış kodu 2). Yani netice görüldükten sonra kod ya da tahmin değiştirilirse ölçü kırmızı yanar.

## Sınır (tenkit)

- bAbI, şemanın yalnız bir dilimini ölçer: metinden hafıza, zincirleme ve zaman. Uyku, rüya, savaş ve icat gibi senaryoları ölçmez. Bu ölçü, şemanın tamamının doğruluğunu ispatlamaz.
- Çözücü şemanın bir tatbikidir. Düşen bir görev şemanın değil tatbikin kusuru olabilir; bunu yalnız bu ölçüyle ayırmak mümkün değildir.
- Tohum sabittir (1453); tek koşu yapılır, güven aralığı yoktur.
- Devir sayısı 20'dir. Sayıyı tren kısmında ölçülen süreye bakarak, mühürden evvel indirdim; test neticesine bakarak seçmedim.
