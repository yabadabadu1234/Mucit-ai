# MUCİT-AI -- MİMARİNİN TAM FORMÜLÜ, KELİMELERLE

Bu dosya bir tarif yahut niyet beyanı değildir. **Şu anda koşan kodun**
formülüdür. Her satırı `main/egitim.py` ile `nefs/` altındaki uzuvların
fiilen yaptığı işten çıkarılmıştır. Kod değişirse bu dosya aynı turda
değişir; değişmezse yalan söylüyor demektir.

Ferman gereği semboller kullanılmamıştır: her ameliye kelimeyle yazılır.

---

## SIFIR. BİR CÜMLEDE

Model, bir metni tiktoken kimliklerine, kimlikleri veri lifi tabanında
basamaklara, basamakları dört bin doksan altı seviyeli tek bir qudit
yazmacının genliklerine çevirir; bu yazmacı kırk dört melekenin sabit
sırasıyla bir kere geçirir; çıkan hâli hem bir kaide hipotezi hem bir
cevap dağılımı sayar; hatayı tek bir sayıya indirmeden **yetmiş küsur
bileşenli bir vektör** olarak ölçer; ve türev almadan, yön tarayarak
parametreyi kımıldatır.

Transformerdan farkı üç kelimede: **katman yok, dikkat yok, türev yok.**

---

## BİR. GİRDİNİN HAZIRLANMASI

1. **Belirteçleme.** Ne gelirse gelsin -- ARC ızgarası, İngilizce metin,
   riyaziye ispatı -- tek kapıdan geçer: tiktoken `o200k_base`. Sözlük
   ebadı elle yazılmaz, kodlamanın kendi `n_vocab` alanından yoklanır ve
   iki yüz bin on dokuz çıkar.

2. **Tip vektörü.** Her belirteç kimliği, veri lifi tabanında (on altı)
   basamaklarına açılır. Basamak sayısı, sözlüğü taşımaya yetecek en
   küçük tam sayıdır ve beş çıkar. Yâni bir belirteç, **beş tane on altı
   tabanlı basamağa** dönüşür. Sürekli bir gömme matrisi **yoktur**;
   gömme, basamakların qudit seviyelerine yerleşmesidir.

3. **Bağlam penceresi.** Pencere bir bütçe artığı değildir: ARC
   görevlerinin ölçülen en uzun belirteç boyunun basamak sayısıyla
   çarpımının üstündeki ikinin kuvvetidir. Şu anda altmış beş bin beş
   yüz otuz altı basamaktır ve görevlerin yüzde doksan dokuz virgül
   doksanı içine sığar.

4. **Örnek üçlüsü.** Her örnek üç parçadır: bağlam basamakları, hedef
   basamak, ve cins. Cins ya ARC'dir ya sözlüdür. **İki cins için iki
   ayrı motor, iki ayrı kayıp yoktur**; cins yalnız hedefin nereden
   geldiğini ve sadakat kefesinin ne kadar kat'î olduğunu değiştirir.

5. **Kategorik kodlama.** Bağlamın her basamağı, veri lifi uzunluğunda
   bir birim vektöre çevrilir: o basamağın yerine bir, ötekilerin yerine
   sıfır. Bir örnek böylece satır sayısı bağlam boyu, sütun sayısı on
   altı olan bir tabloya döner.

---

## İKİ. YAZMAÇ -- NEYİN ÜSTÜNDE HESAP YAPILIYOR

Tek bir **qudit yazmacı** vardır ve durumu **tam** tutulur; hiçbir
kesme, hiçbir bağ budaması yoktur.

* Seviye sayısı dört bin doksan altıdır ve üç lifin çarpımıdır: veri
  lifi on altı, karo on altı, karo on altı. Bu üçlü Kronecker karosu
  birinci seviye önbelleğe sığacak şekilde **ölçülerek** seçilir, elle
  yazılmaz.
* Genlikler karmaşık sayıdır ve **büyüklükleri** kayan noktadır.
* **Faz ise kayan nokta değildir**: faz üssü on altı mertebeli tamsayı
  defterinde birikir. Genliğe inen tek şey Palmer çeyreğidir -- bir
  genliğin gerçek ve sanal parçasının yer değiştirip birinin işaretinin
  dönmesi. Çeyreğe yetmeyen artık üs genliğe hiç dokunmaz, deftere geri
  konur ve bir sonraki faz çağrısında ödenir. Bu borç ölçülür ve rapora
  basılır.
* Yazmaç on bir **küllî alana** bölünmüştür ve her alan seviyelerin bir
  aralığıdır: makam, mizan, tenakuz, tasdik, sükût, nakz, kelâm, kaide,
  orak, gaye, tertip. Bir alanın "değeri", o aralıktaki genliklerin
  büyüklük karelerinin toplamıdır.

---

## ÜÇ. İLERİ GEÇİŞ -- BİR ÖRNEK İÇİN

Bu, transformerin katman zincirinin yerine geçen şeydir. **Katman
yoktur; tek bir yazmaç vardır ve üstünde sırayla ameliye yapılır.**

1. **Yerleştirme.** Bağlamın ilk basamağı yazmacın veri lifinde bir
   temel duruma konur; kalan basamaklar faz açılarına çevrilip faz
   defterine yazılır. Yazmaç sonra eşit üstüste binmeye sokulur.

2. **Harman.** Üç kademe boyunca, her lifin her bit düzleminde küçük
   açılı bir dönme vurulur. Açılar tohumdan türer, öğrenilen parametre
   değildir; maksat başlangıç durumunu tek bir eksene yapışık
   bırakmamaktır.

3. **Kırk dört melekenin sabit sırası.** Melekeler sırayla koşar ve
   sıra sabittir; on üçüncü meleke bir kere tekrar edilir. Her meleke:
   - yazmaca kendi kapılarını vurur (parametreden türeyen açılarla),
   - kendi ilân ettiği küllî alanların değerini **okur** ve o okumayı
     kendi hanesine yazar,
   - dolaşıklık entropisinin farkını taşır.

   Meleke sayısı kırk dörttür, koşan sıra kırk beş adımdır. Her meleke
   **ayrı bir kategoride iş yapar** ve ölçüsü asla ötekilerle tek bir
   sayıda toplanmaz.

4. **Vicdan.** Her melekeden sonra bir işaret denetimi koşar; sıranın
   sonunda usul denetimi ve intâc denetimi koşar.

5. **Gaye.** Tasdik, tenakuz ve nakz alanlarından beslenen bir
   teleoloji ameliyesi: gaye alanına bir çeyrek dönme vurulur, tasdik
   artı, tenakuz ve nakz eksi işaretle faz defterine toplanır, sonra
   nakz ile gaye ve tenakuz ile gaye arasında kontrollü işaret kapısı
   vurulur. Sükût alanına sabit bir eksi eğilim dağıtılır.

6. **Sadakat.** Parite lifi üstünde bir sadakat ameliyesi koşar ve
   durumun ne kadar bozulduğu ölçülür.

7. **Faz kilidi.** Bose-Einstein yoğuşması benzeri bir faz kilidi
   ameliyesi koşar.

8. **Normalize.** Yazmaç birim norma çekilir.

9. **Hâl çıkarılır.** Yazmacın genlik tablosu, veri lifi sayısı kadar
   satıra bölünür; satırlar toplanıp normalize edilir. Çıkan şey o
   örneğin **hâlidir** ve iki iş görür: hem o örneğin **kaide
   hipotezidir**, hem sonraki bütün kefelerin girdisidir.

**Dikkat yoktur.** Transformerdeki sorgu-anahtar-değer üçlüsü, softmax
ağırlıklandırması ve çok başlılık burada **yoktur**. Bağlam
elemanlarının birbirini görmesi, hepsinin aynı yazmaca yazılması ve
aynı kapılardan geçmesiyle olur.

**Artık bağlantı yoktur.** Transformerin "girdiyi çıktıya ekle"
kaidesinin yerini yazmacın kendisinin taşınması alır: durum silinip
yeniden kurulmaz, üstüne ameliye yapılır.

---

## DÖRT. HATA -- TEK SAYI DEĞİL, VEKTÖR

Türev almadığımız için hatayı tek bir sayıya indirmenin hiçbir faydası,
bütün zararı vardır: bileşenler birbirini örter. O hâlde kayıp bir
**vektördür** ve bileşenleri şunlardır.

### (a) Melekelerin kefeleri -- her biri ayrı

Her melekenin okuduğu her alan için bir eksiklik ölçülür ve **meleke
başına bir kefe** açılır. Ayrıca her küllî alan için bir kefe, ve
kademe görevlerinin her biri için bir kefe. Bunların hiçbiri
birbiriyle toplanmaz; hepsi vektörde ayrı satırdır. Toplam ağırlıkları
meleke payına bölünerek dağıtılır.

### (b) Zırhın beş kefesi

Demet cezası, Betti cezası, kohomoloji cezası, homotopi cezası ve nizam
cezası. Nizam cezası, melekelerin taşıdığı entropi farkının o melekenin
sınıfının taahhüdüne uyup uymadığından gelir.

### (c) Kaide halkası -- modelin kendi hipotezlerinin teftişi

Aynı cinsteki örneklerin **hâlleri** birer kaide hipotezidir. Bu
hipotezler bir halkaya dizilir ve halka boyunca ardışık iç çarpımların
çarpımı alınır. Bu çarpımın büyüklüğü birden ne kadar uzaksa, açısı
yarım turdan ne kadar yakınsa, halka nerede kopuksa ceza o kadardır.
Yâni kefe şudur: birden eksik büyüklük, artı tenakuz varsa bir, artı
kısırdöngü varsa bir, artı kopukluk varsa bir. **Elle yazılmış hiçbir
kaide yoktur**; model kendi tutarlılığını teftiş eder.

### (d) Mizanın kendi kefeleri

* **Nokta kefesi.** Hedef basamağın kısmî Born olabilirliği; körlemesine
  çapraz düzensizlik değil, üç zırhtan sonra ve küçük ağırlıkla.
* **Uzay kefesi.** Model hâli ile hedef hâl arasındaki Uhlmann sadakati.
  Bu kefenin ağırlığı bire sabitlenmiştir ve ötekiler ona göre ölçülür:
  çıpa budur.
* **Kategori kefesi.** Bileşke morfizmin, morfizmlerin bileşkesine ne
  kadar uyduğu. Etiketsizdir, kendi kendini denetler.
* **Tip kefesi.** Hâlin Hodge Laplasyeninin çekirdeğine ne kadar uzak
  olduğu.
* **Çevrim kefesi.** Rastgele seçilen üçlü çevrimler boyunca taşınan
  holonomi izinin fıtrattan sapması.
* **Tenakuz kefesi.** Çevrim üniterinin izine vurulan logaritmik bariyer
  ile, o çevrimdeki hâllerin birlikte hiç görülmemiş olma nispetinin
  çarpımı.
* **Gedik kefesi.** Usullerin kapatamadığı karanlık çevrimlerin borcu.
* **Monogami kefesi.** Dolaşıklığın paylaşımına konan Coffman-Kundu-
  Wootters haddinin ihlâli.
* **Engel kefesi.** Sürekli ölçüm altındaki engellenme.

### (e) Toplama nerede yapılır

Vektör **vektör kalır**. Eniyileyici bir sıralama istediği için, ve
yalnız orada, bileşenler ağırlıklarıyla çarpılıp toplanır. O toplama tek
bir satırdadır ve açıkça yazılıdır.

### (f) Ağırlıklar nereden gelir

Elle yazılmaz. Artık vektörünün bileşenleri bir halkaya dizilir ve
rezonanslarından payları ölçülür; uzay kefesi çıpa olduğu için ötekiler
ona nispetle konur. Bir kefenin ağırlığı **her turda yeniden ölçülür**;
donmuşsa rapor bunu söyler.

---

## BEŞ. ADIM -- TÜREVSİZ

Transformerde adım, geri yayılımla hesaplanan gradyanın ters yönüdür.
Burada **gradyan yoktur ve hesaplanmaz.** Adım şöyle atılır:

1. **Had yarıçapı ölçülür.** Merkezin etrafında üç ayrı yarıçapta,
   her yarıçapta üç rastgele yönde kayıp yoklanır. Kayıp yarıçapla
   birlikte tekdüze artıyorsa manzara zorlayıcıdır ve tam yarıçap
   kullanılır; artmıyorsa yarıçap yarıya indirilir.

2. **Yön seçilir.** Parametre sayısı altmış dörtten büyükse **toptan**
   usul koşar: rastgele artı bir eksi bir işaretlerinden kurulu bir yön
   boyunca iki yanlı fark alınıp ortalanır -- bu bir gradyan **değildir**,
   tek bir yön kestirimidir ve dört tekrarla ortalanır. Küçükse
   koordinat usulü koşar: eksenler karıştırılıp bir kısmı seçilir.

3. **O yön boyunca bir boyutlu tarama.** Seçilen yön üstünde,
   Gauss-Chebyshev-Lobatto düğümlerine yerleştirilmiş noktalarda kayıp
   ölçülür ve en küçüğü alınır. Bu düğümler eşit aralıklı değildir;
   eşit aralıkta koşul sayısı patlarken burada bire oturur.

4. **Durgunluk ölçülür.** Bu turun altuzayı ile bir evvelkinin arasındaki
   Grassmann mesafesi bakılır.

5. **Tünel.** Durgunluk eşiğin altındaysa ve manzara zorlayıcı değilse,
   karşıt-adiyabatik sürüş uygulanıp bir aday üretilir; kaybı
   düşürüyorsa kabul edilir.

**Öğrenme oranı yoktur, momentum yoktur, Adam yoktur.** Adım, taranan
doğru üstündeki en iyi noktadır.

---

## ALTI. DIŞ DÖNGÜ -- BİR VERİ, HUDUDU TEMİZLENENE KADAR

Tâlim veri yığınını bir kere görüp geçmez.

1. **Küme seçimi.** Kalan örnekler arasından, müşterek münasebet
   haritasına göre **en zayıf bağlı** olanlar bir öbek hâlinde seçilir.
2. **İç turlar.** O küme üstünde, en çok belirlenmiş tur sayısı kadar,
   her turda ağırlıklar yeniden ölçülerek adım atılır.
3. **Bırakma şartı keyfiyettir, kemiyet değil.** Küme ancak **üç hudut
   temizlenince** bırakılır: tenakuz yok, kısırdöngü yok, mantıksızlık
   yok. Kaybın sayısal sıfırı aranmaz, çünkü o zaten imkânsızdır.
4. **Kirli kalan geri döner.** Temizlenemeyen küme kuyruğun **başına**
   döner; kaç defa döneceği o kümenin ölçülen keyfiyetinin
   fonksiyonudur, elle yazılmış bir sabır sayısı yoktur.
5. **Harita birikir.** Her küme kapandığında, o kümedeki bağlam
   basamakları arasındaki bağlar müşterek münasebet haritasına
   işlenir. Biriken şey tek tek cevaplar değil, **bütün veriler için
   müşterek bir münasebet haritasıdır**.
6. **İmleç ilerler.** Küme kapanınca külliyatın hangi kaynağının hangi
   baytında kalındığı hazineye yazılır; sonraki koşu oradan devam eder.

**Devam asıldır, baştan başlamak istisnadır.** Ağırlık, hafıza, imleç ve
ölçülen hız tek bir hazine dosyasında durur ve koşu başlarken oradan
yüklenir.

---

## YEDİ. KONUŞMA -- HER İKİ KAPIDA DA

Tâlim konuşmadan bitmez. Çıkarım ile tâlim arasındaki **tek fark**,
çıkarımda eniyilemenin koşmamasıdır.

1. Bağlam yazmaca kodlanır.
2. Her adımda kelâm alanının genlik büyüklüklerinin kareleri sözlük
   kadar parçaya bölünüp toplanır; çıkan dağılım cevap dağılımıdır.
3. Hafızada cerhedilmiş bir yola benzeyen bölge varsa o bölge budanır.
4. Vakum kıvılcımı ile bir basamak seçilir; körlemesine sıcaklık
   örneklemesi **yoktur**.
5. Seçilen basamak bağlama eklenir ve döngü sürer.
6. Basamaklar beşerli gruplanıp tiktoken kimliğine geri çevrilir,
   kimlikler çözülüp metin olur.
7. Sükût alanı eşiği aşarsa yahut şüphe manifoldu teâruz derse model
   **susar**; sükût bir cevap değildir fakat yalan da değildir.

**Mihenk.** Tâlim koşarken, her birkaç yüz saniyede bir, o anki
ağırlıkla sabit bir İngilizce suâl sorulur ve cevabı kütüğe yazılır.
Cevabın turdan tura nasıl değiştiği hem koda hem göze görünür.

---

## SEKİZ. TRANSFORMER İLE YAN YANA

| Transformerde | Bizde |
| :-- | :-- |
| Gömme matrisi | Tip vektörü: belirteç kimliğinin taban açılımı |
| Çok başlı dikkat | Yok. Hepsi aynı yazmaca yazılır |
| Softmax ağırlığı | Yok. Genlik büyüklüğünün karesi |
| Katman yığını | Yok. Tek yazmaç, kırk dört melekenin sabit sırası |
| Artık bağlantı | Yazmacın taşınması |
| Katman normalizasyonu | Birim norma çekme |
| Çapraz düzensizlik kaybı | Yetmiş küsur bileşenli hata vektörü |
| Geri yayılım | Yok. Yön taraması |
| Öğrenme oranı, Adam | Yok. Taranan doğru üstündeki en iyi nokta |
| Devir sayısı | Yok. Küme, hududu temizlenene kadar |
| Sıcaklıkla örnekleme | Vakum kıvılcımı |

---

## DOKUZ. NE İDDİA EDİLMİYOR

* **"Tamamen Galois'ya geçildi" denmiyor.** Faz ve gayri-lineerlik
  Galois tarafındadır; genlik **büyüklüğü** kayan noktadır. Ayrıca
  vakum kıvılcımı uzvunda hâlâ aşkın işlem koşar ve bu sayılmıştır.
* **"Durum CNOT-Dihedral sınıfındadır" denmiyor.** Ölçülen Reed-Muller
  derecesi on ikidir; teoremin varsaydığı üçün çok üstünde.
* **Bu kod gerçek bir kuantum donanımında bu hâliyle koşmaz.**
  Klonlanamazlık bilerek ihlâl edilmiştir; karşılığında doğruluk ve
  hız alınmış, donanım taşınabilirliği kaybedilmiştir.
* **Model şu anda İngilizce mihenk suâline mânalı cevap vermiyor.**
  Cevap boş çıkıyor ve sebebi ölçülmüştür: basamak uzayı sözlükten beş
  kat büyüktür, üretilen kimliklerin çoğu sözlük dışına düşer. Bu,
  mizanın mantıksızlık hududunun ölçtüğü şeydir ve düşmesi beklenir.
