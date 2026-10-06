> Dizin: [KUME_TASNIF_VE_TADILI.md](../KUME_TASNIF_VE_TADILI.md) · Serbestlik derecesi: iki şart, dört boyut türü, otomatik çıkarma

  
Meselenin tam omurgasını yakaladın; zira **"serbestlik derecesi" (degree of freedom)** mefhumu, tasnifatı dışarıdan uydurulan keyfi başlıklardan kurtarıp nesnenin kendi hendesesine bağlayan yegâne anahtardır.  
Fizikte ve matematikte serbestlik derecesi nedir? Bir sistemin durumunu şüpheye yer bırakmayacak kesinlikte belirlemek için gereken **asgari bağımsız parametre sayısıdır**.  
Eğer bir kümenin serbestlik derecelerini (yani birbirinden bağımsız, birbirine indirgenemeyen ve birbirini tüketmeyen asal eksenlerini) tam ve eksiksiz tespit edebilirsen; soracağın suallerin o kümeyi **tam örteceğini (surjective / exhaustive)** ve hiçbir kör nokta bırakmayacağını riyazi bir kesinlikle garanti edersin.  
Peki, serbestlik derecelerinin bizzat kendisi nasıl tasnif edilir ve bir kümenin serbestlik dereceleri keyfilikten uzak bir usulle nasıl ortaya çıkarılır?  
**I. Serbestlik Derecesinin İki Asli Şartı (Doğrulama Mihengi)**  
Bir vasfa veya boyuta "bu kümenin serbestlik derecesidir" diyebilmen için şu iki cebirsel-mantıki şartı sağlaması zaruridir:  
1. **İstiklal (Doğrusal Bağımsızlık / Orthogonality):** Eksenlerden biri, diğer eksenlerin bir fonksiyonu veya türevi olamaz: D_i \ne f(D_j, D_k, \dots) Eğer bir eksendeki değişimi diğer eksenlerin değerlerinden hesaplayabiliyorsan, o bağımsız bir serbestlik derecesi değildir; sahte bir boyuttur, elenmesi gerekir. (Mesela bir arabada "motor hacmi" ile "silindir hacmi" iki ayrı serbestlik derecesi değildir; biri diğerine bağımlıdır).  
2. **Kifayet (Tam Temsil / Spanning):** Kümedeki herhangi bir x elemanı, bu eksenlerde alacağı değerler demetiyle (v_1, v_2, \dots, v_n) istisnasız ve tekil olarak tanımlanabilmelidir: \forall x \in X, \quad x \mapsto \langle v_1(x), v_2(x), \dots, v_n(x) \rangle Eğer iki farklı eleman bütün eksenlerde aynı değerleri aldığı halde hala birbirinden farklı kalıyorsa, sistemde **tespit edilmemiş gizli bir serbestlik derecesi** var demektir; küme henüz örtülmemiştir.  
**II. Serbestlik Derecelerinin Tasnifi (Boyut Türleri)**  
Herhangi bir X kümesinde ortaya çıkabilecek serbestlik dereceleri yapısal olarak **dört asli sınıfa** ayrılır:  
```
              [ SERBESTLİK DERECELERİ (EKSENLER) ]
                               │
   ┌────────────────┬──────────┴──────────┬────────────────┐
   │                │                     │                │
1. Durum /       2. Nispet /           3. Ameliye /     4. Mertebe /
   Mahiyet          İrtibat               Zaman            Hiyerarşi
   (Statik Eksen)   (Topolojik Eksen)     (Dinamik Eksen)  (Skalar Eksen)

```
**1. Durum ve Mahiyet Eksenleri (Statik Serbestlik Dereceleri)**  
Nesnenin kendi iç bünyesindeki bağımsız değişkenlerdir.  
* **Soru Formu:** *"Kendi zatında hangi ayrık halleri alabilir?"*  
* **Misal:** Bir sayının işareti (pozitif, negatif, sıfır); bir verinin tipi (kesikli, sürekli); bir devrenin modu (iletimde, kesimde).  
**2. Nispet ve İrtibat Eksenleri (Topolojik / Münasebet Eksenleri)**  
Elemanın diğer elemanlarla veya sistemin bütünüyle kurduğu bağın serbestlik derecesidir.  
* **Soru Formu:** *"Çevresiyle ve diğer parçalarla kaç farklı tarzda rabıta kurabilir?"*  
* **Misal:** Bir graf düğümünün derecesi ve yönü; bir önermenin diğerine nispeti (tenakuz, telazum, tehalüf); bir parçanın bütüne irtibatı (asli kurucu, tali eklenti).  
**3. Ameliye ve Süreç Eksenleri (Dinamik / Zaman Eksenleri)**  
Nesnenin durum değiştirirken tabi olduğu hareket serbestliğidir.  
* **Soru Formu:** *"Hangi istikamette, hangi kural altında başkalaşabilir?"*  
* **Misal:** Bir sistemin tersinir (reversible) veya tersinmez oluşu; bir muhakemenin yönü (tümdengelim, tümevarım, geriye doğru iz sürme).  
**4. Mertebe ve Hiyerarşi Eksenleri (Ölçek / Skalar Eksenler)**  
Elemanın hangi soyutlama veya kuvvet seviyesinde yer aldığını belirleyen eksendir.  
* **Soru Formu:** *"Hangi yetki, kapsam veya genellik derecesindedir?"*  
* **Misal:** Bir kuralın anayasal mı, kanuni mi, yönetmelik düzeyinde mi olduğu; bir bilginin burhanî (kesin), zannî (ihtimalli) veya vehmî mi olduğu.  
**III. Bir Kümenin Serbestlik Derecelerini Otomatik Çıkarma Usulü**  
İçini tam bilmediğin bir kümede serbestlik derecelerini atlamadan, eksiksiz tespit etmek için şu **üç kademeli differansiyel ameliyat** tatbik edilir:  
**Adım 1: "Kısıtları Sıfırlama" (Maksimum Serbestlik Uzayı)**  
Evvela sistemin üzerindeki bütün harici kayıtları kaldırıp en kaba evrensel uzayı tasavvur edersin.  
* Fizikte N tane parçacığın 3 boyutlu uzaydaki serbestlik derecesi 3N'dir.  
* Mantıkta bir X kümesi için sorulabilecek en kaba bağımsız soru sayısı, o kümenin tanımlandığı en yakın üst cinsin (super-class) boyutları kadardır.  
**Adım 2: "Kısıt Fonksiyonlarını Düşme" (Bağımsız Kalan Eksenler)**  
Bir sistemin hakiki serbestlik derecesi, **mümkün boyutlardan kısıt denklemlerinin çıkarılmasıyla** bulunur:   
```
\text{Serbestlik Derecesi} = \text{Toplam Değişken Sayısı} - \text{Bağımsız Kısıt Sayısı}

```
* Bir kümenin tanımına koyduğun her şart, her aksiyom bir serbestlik derecesini **yutar (dondurur)**.  
* **Misal:** "Üçgenler kümesi" tasavvur et. Üç iç açı vardır (\alpha, \beta, \gamma). İlk bakışta 3 serbestlik derecesi görünür. Lakin tanım icabı bir kısıt vardır: \alpha + \beta + \gamma = 180^\circ. Bu bağıntı 1 serbestlik derecesini yok eder. Geriye **2 serbestlik derecesi** kalır. Demek ki bir üçgenin şeklini tam tasnif etmek için sadece ve sadece **2 bağımsız soru** sorma hakkın vardır (mesela iki açıyı bilmek yeter, üçüncüyü sormak gereksiz fazlalıktır).  
**Adım 3: "Ayırt Edilemezlik (İkiz) Testi" ile Örtücülüğü Doğrulama**  
Çıkardığın eksenlerin kümeyi tam örtüp örtmediğini anlamanın kat'î yolu şudur:  
1. Belirlediğin serbestlik derecelerine göre bütün koordinatları aynı olan iki eleman (x_1 ve x_2) seç.  
2. Bu iki eleman arasında hala ayırt edici bir fark bulabiliyor musun?  
    * **Fark yoksa:** Tebrikler, serbestlik derecelerin **tamdır ve örtendir**. Sorduğun sorular kümenin bütün ontolojik uzayını kapatmıştır.  
    * **Hala fark varsa:** O farkı meydana getiren vasıf, gözden kaçırdığın **yeni bir serbestlik derecesidir**. Onu da bağımsız bir eksen olarak sisteme eklersin.  
**Netice**  
Kümenin tam tasnifatını garanti eden şey rastgele sorular değil; **kümenin kısıtlarından arta kalan bağımsız serbestlik derecelerinin matrisidir**.  
Serbestlik derecelerini bu riyazi usulle (bağımsız eksenleri teker teker soyup, kısıtları düşerek) çıkardığın an, o eksenlerin her birine sorulacak birer soru ile oluşturulacak Kartezyen çarpım uzayı:   
```
X \subseteq D_1 \times D_2 \times \dots \times D_k

```
kümeyi tek bir artık eleman bırakmaksızın, tam ve eksiksiz bir surette örter.  