# Vazife: Arabic Ontology kelimelerini doğru köke eşleştir

`girdi/001.json` … `girdi/010.json` dosyalarını sırayla, **her birini baştan sona oku**.
Her dosya bir kavram listesidir. Her kavramda `belirsiz` kelimeler var: kelimenin harekesiz yazılışı birden fazla köke uyuyor (`adaylar`).

Senin işin: her belirsiz kelime için kavramın `tanim`, `ingilizce` ve `esanlamlilar` alanlarını **manuel okuyarak** kelimenin bu kavramdaki gerçek kökünü seç.

- Kelimenin harekeli yazılışına (şedde, hemze, uzatma) ve kavramın mânâsına bak. Örnek: `أَبَانَ` «açıkladı» kökü بين'dir; `إِبَّان` «zaman» kökü ءبب'dir.
- Adaylardan hiçbiri doğru değilse `"kok": null` yaz ve `"not"` alanına doğru kökü (biliyorsan) yaz.
- Betik, sezgisel kural veya toplu otomatik eşleştirme **kullanma**; her kelimeyi kendin oku. Seçmece yapma, 3 644 kelimenin hepsi.

Çıktı: `cikti/001.json` … `cikti/010.json`, her girdi dosyasına karşılık bir dosya:
```json
[{"id": "46577", "kelimeler": [{"kelime": "أَبَانَ", "kok": "بين", "not": ""}]}]
```
Her dosyayı bitirince git commit et (`git add` + `git commit`, mesaj: «ontoloji eşleştirme 001»). Bütün on dosya bitince dur ve «bitti» yaz.
