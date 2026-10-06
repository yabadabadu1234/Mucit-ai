> Dizin: [KUME_TASNIF_VE_TADILI.md](../KUME_TASNIF_VE_TADILI.md) · Küme tasnifi: sonsuz çeşit küme, üç kat’î şart, usul

# Küme tasnif ve tadili  
  
Haklısın. Dört illet dediğin şey sadece "fiziki veya mevcud olan bir nesnenin/oluşun varlık sebeplerini" açıklar; soyut bir kümeye, bir matematiksel nesneye, bir ayetler yahut arabalar kümesine dört illeti zorla giydirmeye çalışmak meselenin mahiyetini zorlamaktır.  
"Herhangi bir X kümesi verildiğinde, sorulacak hangi sorular o kümeyi **tam, eksiksiz ve örtücü** bir tasnifata kavuşturur?" sualine mantık, küme teorisi ve bilgi felsefesi zaviyesinden bakalım.  
**I. Sonsuz Çeşit Küme Var mıdır?**  
Matematiksel ve mantıki olarak: **Eleman sayısı bakımından sonsuz küme vardır; lakin yapısal/kategorik bakımdan kümelerin çeşitleri sonsuz değildir.**  
Bir küme mantık terazisinde şu üç sınıftan birine girmek mecburiyetindedir:  
1. **İntensional (Kavramsal / Niteliksel) Kümeler:** Elemanları bir kural, vasıf veya şartla tanımlananlar: X = \{x \mid \Phi(x)\}. (Mesela: "Bütün ayetler", "bütün ispatlar", "bütün arabalar").  
2. **Extensional (Sayılabilir / Liste) Kümeler:** Elemanları vasıfla değil, doğrudan tek tek gösterilerek tanımlananlar: X = \{a, b, c\}.  
3. **Mürekkep / Yapısal Kümeler:** Sadece elemanlardan ibaret olmayıp, elemanları arasında bağıntılar veya cebirsel işlemler bulunanlar (uzaylar, cebirler, kategoriler).  
Dolayısıyla rastgele sonsuzluk yoktur; kümenin tanımlanma biçimi (yani onun kuruluş kaidesi) bellidir.  
**II. Bir Kümeye Hangi Soruları Sorarsak "Tam Tasnifata" Erişiriz?**  
Bir küme üzerinde "sorulabilecek sorular" harici bir vehimle gökten inmez. **Sorulabilecek meşru soruların tamamı, o kümenin tanım bağıntısında gizlidir.**  
Bunu adım adım işletelim:  
**1. Sorunun Matematiksel Mahiyeti Nedir?**  
Bir küme üzerinde soru sormak demek, o kümenin elemanlarını bir **özellikler uzayına** (değer kümesine) haritalayan bir f fonksiyonu tanımlamak demektir:  
```
f : X \to V

```
* Soru: "Yakıt tipi nedir?" (Arabalar kümesi için)  
* Değer kümesi (V): \{\text{Benzin}, \text{Dizel}, \text{Elektrik}, \text{Hibrit}\}  
* Bu soru, X kümesini f fonksiyonunun ters görüntüleri (f^{-1}(v)) üzerinden ayrık parçalara böler.  
**2. Soruların "Tam Tasnifat" Sağladığını Nereden Bileceksin? (Üç Kat'î Şart)**  
Sorularının o kümeyi bütünüyle, açıkta hiçbir şey bırakmadan ve fazlalık üretmeden örttüğünü garanti eden **üç matematiksel şart** vardır:  
**A. Örtücülük Şartı (Exhaustiveness / Mâniatü'l-Hulüvv)**  
Sorunun değer kümesi V, kümedeki her bir elemanın en az bir cevaba sahip olmasını temin etmelidir:  
```
\bigcup_{v \in V} f^{-1}(v) = X

```
Eğer kümede öyle bir x elemanı varsa ki soruya hiçbir cevap veremiyorsa (fonksiyon o elemanda tanımsızsa), soru kümenin zâtına ait değildir; dışarıdan yamadır. (Mesela "Ayetler kümesine" gidip "Motor hacmi nedir?" diye soramazsın; fonksiyon tanımsız kalır).  
**B. Ayrıklık Şartı (Disjointness / Mâniatü'l-Cem')**  
Tasnif edilen sınıflar birbirine taşmamalıdır:  
```
v_i \ne v_j \implies f^{-1}(v_i) \cap f^{-1}(v_j) = \emptyset

```
Bir eleman aynı anda iki zıt kompartımanda yer alamaz. Eğer alıyorsa sorduğun soru tek bir boyut değil, birbirine karışmış iki ayrı sorudur (tahlil edilmemiştir).  
**C. İndirgenemezlik / Ayırt Edilebilirlik Şartı (Separation / Kolmogorov Şartı)**  
"Soruları nerede durduracağım, tam tasnifata ulaştığımı nereden bileceğim?" sualinin cevabı buradadır:  
Eğer elinde öyle bir sorular takımı \mathcal{F} = \{f_1, f_2, \dots, f_k\} varsa ve bu sorular kümedeki **herhangi iki farklı elemanı birbirinden ayırt etmeye kâfi geliyorsa**, tasnifat tamamlanmıştır:  
```
\forall x, y \in X \quad (x \ne y \implies \exists f_i \in \mathcal{F} \text{ öyle ki } f_i(x) \ne f_i(y))

```
Bu noktaya eriştiğin an, sorular kümesi o kümenin **"tüm bilgi topolojisini"** (ayırıcı vasıflarını) örtmüş demektir. Bundan sonra soracağın her yeni soru ya lüzumsuzdur (totolojidir) ya da mevcut soruların bir kombinasyonudur.  
**III. Usul: Hangi Soruların Sorulacağını Kümenin Kendisinden Otomatik Olarak Nasıl Çıkarırsın?**  
Keyfiliği önlemenin tek bir yolu vardır: **Kümenin kurucu aksiyomuna (üretici kuralına) müracaat etmek.**  
1. **Adım 1 - Kümenin İnşa Şartını Yaz:** Küme nasıl tanımlandı?  
    * *Arabalar:* Bir şasi üzerinde tahrik mekanizmasıyla hareket eden mekanik taşıt.  
    * *Ayetler:* Vahiyle inmiş, başı ve sonu tevkîfî olarak tayin edilmiş lafzî vahiy birimi.  
    * *İspatlar:* Aksiyomlardan başlayıp çıkarım kurallarıyla bir iddiayı doğrulayan sonlu önermeler silsilesi.  
2. **Adım 2 - Tanımdaki Bağımsız Değişkenleri (Ortogonal Boyutları) Ayıkla:** Tanımın içindeki her bir serbestlik derecesi (degree of freedom), sorulabilecek bir **asli sorudur**:  
    * *Arabalar tanımında serbestlik dereceleri:*  
        1. Tahrik kaynağı ne? (Yakıt cinsi)  
        2. Hareket iletimi nasıl? (Şanzıman/Çekiş)  
        3. Taşıma hacmi/gayesi ne? (Segment/Kasa)  
    * *İspatlar tanımında serbestlik dereceleri:*  
        1. Dayandığı aksiyom sistemi ne? (Klasik, Sezgici, Modal)  
        2. Çıkarımın istikameti ne? (Doğrudan, Çelişkiyle, Tümevarımla)  
        3. Temsil biçimi ne? (Biçimsel/Sentaktik, Semantik)  
Tanımda yer almayan serbestlik dereceleri (mesela arabanın rengi veya sahibinin adı) arızîdir; kümenin kurucu tasnifatına dahil edilemez.  
**Hülasa**  
Bir kümenin tam tasnifatı için:  
1. Kümenin **tanımındaki bağımsız değişkenleri (ortogonal boyutları)** tespit edersin; asli sorular bunlardır.  
2. Bu soruların değer kümeleri her elemanı kapsamalı (\bigcup A_i = X) ve sınıflar kesişmemelidir (A_i \cap A_j = \emptyset).  
3. Sorular takımı kümedeki farklı elemanları birbirinden ayırt edebilecek seviyeye ulaştığı an (tüm lifler ayrıştığında), **tasnifat tamdır ve kapanmıştır**.  
Bundan başka hiçbir harici metafizik şablona (dört illete yahut zorlama ikili cetvellere) muhtaç değilsin; ölçü bizzat kümenin inşa kuralının serbestlik dereceleridir.  