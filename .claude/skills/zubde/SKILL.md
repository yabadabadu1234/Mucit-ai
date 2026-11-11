---
name: zubde
description: Bir metni, dosyayı yahut mevzuu Zübde formatına (.zbd) çevirir, kanunlarını denetler ve tek sayfalık uygulamasını üretir. Kullanıcı "/zubde <dosya ya da mevzu>" dediğinde, bir metnin özünü şebeke hâlinde istediğinde yahut düzyazıyı kısaltıp yapısını göstermek istediğinde kullanılır.
---

# Zübde

Girdi: bir dosya yolu, yapıştırılmış metin yahut bir mevzu adı. Çıktı: `X.zbd` ve `X.html`.

## Adımlar

1. Kaynağı baştan sona oku (dosyaysa tamamını; mevzuysa bildiğini ve yoklayabildiğini topla).
2. Birimleri çıkar: tek başına tasdik yahut tasavvur edilen en küçük söz parçaları. Hiçbir malumatı atma.
3. `X.zbd` yaz (aşağıdaki yazım ve kanunlarla). Âyet ve hadis yalnız `N` düğümünde, harfiyen.
4. Denetle ve sayfayı üret: `python zubde/zubde.py X.zbd [asıl_metin]`. İhlâl sıfır olana kadar düzelt.
5. `X.html` dosyasını kullanıcıya gönder; düğüm sayısını, hacim nispetini ve ihlâl sayısını bir satırda söyle.

## Yazım

```
ADRES CİNS[*|?] Levha (en çok 100 harf)  <a <b !c =d ~e
    gövde satırı (girintili; devam)
    | cetvel | satırı |
```

- Adres noktalı sayıdır; ilk düğüm `0 K Başlık`. `2.3`'ün babası `2`'dir.
- Cins: `K` kitap · `B` bâb · `T` tarif · `H` hüküm · `D` delil · `M` misal · `S` suâl · `I` itiraz · `U` usul · `V` veri · `N` nakil.
- Damga: `H*` evvelî (delil istemez) · `H?` açık (delili yok).
- Bağ: `<a` dayanır · `!a` itiraz eder · `=a` misalidir · `~a` bakınız.

## Kanunlar

| K1 | Levha en çok 100 harf, tek başına mana verir |
| K2 | Bir düğümün en çok 9 çocuğu |
| K3 | Her `H` ya `<` ile dayanır ya `*` ya `?` taşır |
| K4 | Her muhteva bir kere; tekrar yerine adres |
| K5 | Aynı kalıptaki hükümler tek cetvelde |
| K6 | Düğüm ancak kendinden evvel yazılana dayanır |
| K7 | Bağ ancak hakikî dayanma varsa; levha altındakilerin hulâsası |

## Dikkat

- Delili kaynakta olmayan hükmü `H?` yaz; delil uydurma.
- Dört cephe bağlardan doğar: mantık `<`, gaye ona dayananlar, tatbikat `=` ve `U`, mahiyet düğümün kendisi. Bu yüzden her hükme misal ve usul düğümü aramayı ihmal etme.
- Tarif ve örnek dosya: `zubde/ZUBDE.zbd`.
