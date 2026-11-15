# Bir malumat yığınını en kompakt ve en az vakitte anlaşılır temsil etme usulü

## Hedefin iki ölçüsü
- **Kompaktlık:** tarifin uzunluğu, bit cinsinden. Ölçü: en kısa tarif ilkesi (MDL) ([Grünwald 2005](https://doi.org/10.7551/mitpress/1114.003.0004)).
- **Anlaşılma vakti:** okuyanın bir suâle cevap bulma süresi. Bu, insanla ölçülür; ölçülmedikçe vekili kullanılır: aranan şey için bakılan yer sayısı (arama adımı) ve yer hatırlanınca tanıma.

İki ölçü çatışabilir: en kısa tarif, okuyana yabancı simgelerle yazılırsa geç anlaşılır. Bu yüzden usul, kısaltmayı **okuyanın tanıdığı yapılardan bir sözlükle** yapar.

## Usul (dört adım)
1. **Tabloya çevir.** Malumatı varlık × vasıf (ve varlık × varlık) tablosu yap. Her malumat bir hücredir.
2. **Tanıdık yapılarla sıkıştır.** Tabloyu, insanın bir bakışta tanıdığı yapı türlerinden (dikdörtgen/kavram, yıldız, zincir, hiyerarşi) bir sözlükle, en kısa tarif verecek şekilde örter. Dayanak: büyük çizgeleri yıldız, iki parçalı çekirdek, klik ve zincir sözlüğüyle MDL'e göre özetleyen VoG ([Koutra vd. 2014](https://doi.org/10.1137/1.9781611973440.11)); ikili tabloyu en az sayıda formal kavramla (dikdörtgenle) örten çarpanlama ([Belohlavek & Vychodil 2010](https://doi.org/10.1016/j.jcss.2009.05.002)); tablodaki sık kalıpları sıkıştırmayla seçen Krimp ([Vreeken vd. 2011](https://doi.org/10.1007/s10618-010-0202-x)).
3. **Yere bağla.** Birlikte gereken malumatı yan yana koy; böylece arama azalır, tanıma göze kalır ([Larkin & Simon 1987](https://doi.org/10.1111/j.1551-6708.1987.tb00863.x)). Sıra, her yapının parçalarını bitişik tutacak biçimde seçilir (doğrusal diyagramda çizgi parçası en aza).
4. **En hızlı okunan işarete kodla.** Nicel değer önce konum, sonra uzunluk, açı, alan, renk ile ([Cleveland & McGill 1984](https://doi.org/10.1080/01621459.1984.10478080); [Mackinlay 1986](https://doi.org/10.1145/22949.22950)). Grup ayrımı ön-dikkatli özelliklerle (renk tonu, yönelim): bakışta ayırt edilir ([Healey & Enns 2012](https://doi.org/10.1109/tvcg.2011.127)). Tablo mu çizim mi, suâlin türüne göre seçilir: tek değer aranıyorsa tablo, ilişki aranıyorsa çizim ([Vessey 1991](https://doi.org/10.1111/j.1540-5915.1991.tb00344.x)). Küme üyeliği için doğrusal diyagram ([Rodgers, Stapleton, Chapman 2015](https://doi.org/10.1145/2810012)).

## خلق üstünde ölçüm (`faktor.py`, `faktor_rapor.json`)
- Tablo: 37 kelime × 16 mana, 47 dolu hücre.
- Bütün tabloyu bit bit yazmak: 592 bit. Dolu hücreleri tek tek yazmak: 433 bit.
- Kavram dikdörtgenleriyle (15 çarpan) yazmak: **316 bit**. Hücre listesine göre 1,37 kat kısa.
- 15 çarpanın 13'ü tek manalı bir küme ("bu 6 kelime eskimek manasını taşır"); 2'si çok anlamlı kelimenin dikdörtgeni (`خَلَقَ`: ölçüp biçmek + yaratmak + uydurmak; `تَخَلَّقَ`: uydurmak + öfkelenmek + huy takınmak).
- Çizimi: `../dogrusal_diyagram/dogrusal.png` bu çarpanları çizgi olarak gösterir; çizgi parçası 20, alt sınır 16.

## Sınırlar
- Her adımın kendi en iyisi ispatlı değildir: en kısa örtüyü bulmak genelde NP-zordur (GreConD aç gözlü bir yaklaşımdır), en iyi satır sırası da NP-zordur. Bu yüzden "en kompakt" iddiası **bu sözlük ve bu arama** için geçerlidir.
- Anlaşılma vakti burada **ölçülmedi**; yalnız vekil (yer sayısı) var. Doğrulamak için okuyanla süre ölçmek gerekir.
- `خلق` tablosu seyrek (kelime başına çoğunlukla bir mana) olduğundan kazanç küçük çıktı (1,37 kat). Daha yoğun tabloda kazanç büyür.
