# Fâtiha mihenk taşı (F 3-I 408)
Yapı ağacı, padişahın Fâtiha şemasından okunup `mushaf_yapi.py` içinde veri olarak kayıtlıdır (kelime sözlüğü ve otomatik ayrıştırma yoktur). Metin 1:2–1:7, sırası ve harfleri aynen; yalnız konum, yön ve girinti ile ifade edilir (basmala şemada yok, dışarıda).

Kod defteri: bant (üç boş satır) = saf · bant yönü R/L = muhatap kırılması · derinlik = 6 sütun girinti · ebeveyn = önceki ana şerit satırlarının bir kademe sığ olan en yakını · yan şerit (bandın ters kenarı) = ebeveynin başka bir çocuğu, kendisi ebeveyn olamaz.

## Maskeli iskelet
```
01 |                                                                                               ███ █████| (2 kutu)
02 |                                                                                   █████████ █████      | (2 kutu)
03 |      ████████ █████████                                                                                | (2 kutu)
04 |                                                                         ██████ ████ ███████            | (3 kutu)
   |                                                                                                        |
   |                                                                                                        |
   |                                                                                                        |
05 |█████ ██████                                                                                            | (2 kutu)
06 |      ████████ ███████                                                                                  | (2 kutu)
07 |            ██████████ █████████ ███████                                                                | (3 kutu)
08 |                  ██████ █████████ ██████ ████████                                                      | (4 kutu)
   |                                                                                                        |
   |                                                                                                        |
   |                                                                                                        |
09 |                                                              ██████ ████████████ ████                  | (3 kutu)
10 |                                                                 ██████████ ████                        | (2 kutu)
```
## Sonuç
- Mekanik çözücü: kenarlar, bantlar ve yönler şemayla **izomorf** (8/8 kenar, 3/3 saf, R-L-R).
- Sıfır bağlamlı ayrı okuyucu (yalnız iskelet ve kod defteri): 8/8 kenar, 3 bant, yönler R-L-R, iki kırılma, iki kök — şemayla **birebir**.
- Sınır: bu, tek bir pasaj (Fâtiha) için elle okunmuş yapı ağacıdır; başka sûrelere yapı ağacı **elle, mana okunarak** çıkarılmadıkça uygulanmaz ve yapılmadı. Şemadaki ✓/✗ oklarının ayrımı (aynı safta kalma / saf değiştirme) bant içi-bant dışı çocuk olarak; "لِلَّهِ ← كَ" yönelişi bandın yön değişimi olarak ifade edildi.
