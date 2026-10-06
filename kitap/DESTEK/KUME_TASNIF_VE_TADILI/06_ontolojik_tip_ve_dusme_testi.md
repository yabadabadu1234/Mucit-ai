> Dizin: [KUME_TASNIF_VE_TADILI.md](../KUME_TASNIF_VE_TADILI.md) · Kümenin ontolojik tipi, üç küllî usul, düşme testi ve numuneler

Bu usuller her türlü kümeyi tasnif ederken kullanılamaz. Her küme girdi kutu çıktı değil ki  
  
İtirazın son derece yerindedir. Tahlili anlatırken az evvel kurduğumuz "girdi-kutu-çıktı" (sistem ve durum makineleri) modeli, **ameliyeleri (operatörleri ve süreçleri)** tasnif etmek için elverişli bir metafordur; fakat kalkıp bunu "her türlü kümeye" şamil bir usul diye dayatırsak açık bir kategori hatası yapmış oluruz.  
Zira:  
* Asal sayılar kümesi bir kutu değildir; ne bir şey yer ne bir şey çıkarır.  
* Bir mimari üsluplar kümesi bir fabrika değildir.  
* Bir geometri aksiyomları kümesi bir süreç işletmez.  
Kümeler ontolojik yapıları bakımından tek tip değildir. O halde, "kara kutu" mecazına sığınmadan, **herhangi bir X kümesinin** serbestlik derecelerini bulurken kategori hatasını önleyen, nesnenin kendi tabiatına uygun **küllî usul** nedir?  
**I. Kümenin Ontolojik Tipini Tespit (Mevki Tayini)**  
Bir kümenin serbestlik derecesini aramaya başlamadan evvel sorulacak ilk sual şudur: **"Bu kümenin elemanları ne tür bir varlıktır?"**  
Kümeler mantık ve varlık sahasında üç temel tipe ayrılır. Her tipin serbestlik derecesi kendi sahasından devşirilir:  

| Küme Tipi | Elemanların Mahiyeti | Tipik Misal | Serbestlik Derecesinin Aranacağı Zemin |
| ---------------------------- | --------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| 1. Cevherî / Nesnel Kümeler | Kendi başına kaim olan fertler, nesneler veya varlıklar. | Kimyasal elementler, otomobiller, geometrik cisimler. | Morfoloji ve Zâtî Nitelikler: Kütle, hacim, simetri, iç yapı, kurucu bağlar. |
| 2. İtibarî / Mefhumî Kümeler | Zihnin inşa ettiği soyut kavramlar veya kabuller. | Hukuki haklar, önermeler, aksiyomlar, ahlaki değerler. | Mantıkî Kapsam ve Hüküm: Güç/yetki derecesi, bağlayıcılık, doğruluk değeri, tezatlar. |
| 3. Süreçsel / Amelî Kümeler | Zaman veya intikal içinde cereyan eden hareketler, operatörler. | Tahlil türleri, muhakeme adımları, algoritmalar. | Dinamik Parametreler: Girdi/çıktı, yön, granülarite (derinlik), dönüşüm kuralı. |
  
Az önceki "kutu-girdi-çıktı" hatası, 3. tipe (ameliyelere) ait bir şablonu alıp genel kural zannetmekten doğmuştur. Cevherî bir kümede girdi-çıktı aranmaz; orada bakılacak şey nesnenin kendi zâtî sınırlarıdır.  
**II. Her Kümede Kategori Hatasını Önleyen 3 Küllî Usul**  
Kutu metaforu olmadan, saf mantıkla serbestlik derecesini ararken şu üç süzgeç işletilir:  
**1. "Tanım Çekirdeği Dışındakileri Ayıklama" Süzgeci**  
Bir elemanı X kümesine sokan kurucu önerme nedir?  
* Tanımda yer alan zorunlu unsurlar \rightarrow **Zâtî serbestlik derecesi adaylarıdır.**  
* Tanım değiştirmeksizin serbestçe değişebilen dış ilişkiler \rightarrow **Arazdır (kategori hatasıdır, elenir).**  
*Misal:* "Asal sayılar kümesi."  
* Elemanı kümeye sokan kural: "Yalnızca 1'e ve kendisine bölünebilen 1'den büyük tam sayı."  
* Burada "sayının çift/tek olması" veya "büyüklüğü" zâtî bir değişken/serbestlik eksenidir.  
* Lakin *"Bu asal sayıyı kim buldu?"* yahut *"Bu sayı hangi kriptografi algoritmasında kullanılıyor?"* sualleri sayının zâtına ait değildir; kullanıma/tarihe aittir. Kümeyi tasnif ederken asal sayıları "kullanan algoritmanın niyetine göre" bölmeye kalkarsan kategori hatası doğar.  
**2. "Bağımlılık (İzomorfizm ve Fonksiyon) Testi"**  
Aklına gelen iki sorunun aynı serbestlik derecesini mi sorduğunu, yoksa hakikaten ayrı iki boyut mu olduğunu anlamanın tek yolu:  
* Eğer bir vasfın değeri (A), diğer bir vasfın değerinden (B) doğrudan türetilebiliyorsa (A = f(B)), bunlar iki ayrı serbestlik derecesi değildir.  
* *Misal:* "Düzgün çokgenler kümesi."  
    * Soru 1: "Köşe sayısı kaçtır?" (n)  
    * Soru 2: "İç açılar toplamı kaçtır?" (\theta) Burada \theta = (n - 2) \times 180^\circ bağıntısı vardır. Dolayısıyla iç açılar toplamı bağımsız bir serbestlik derecesi değildir; köşe sayısının bir fonksiyonudur. İkisini de ayrı eksen saymak sahte serbestlik derecesi üretmektir.  
**3. "Düşme / Kırpma (Projection) Testi"**  
Bir boyutu zihnen sıfırladığında yahut yok saydığında küme hala ayakta kalıyor mu?  
* Eğer bir parametreyi çektiğinde geriye kalan yapı mefluç olmuyor, küme kendi sınırları içinde tanımlı kalmaya devam ediyorsa, o parametre haricidir veya tali bir arazdır.  
* Eğer o parametreyi çektiğinde kümenin elemanları birbirine çöküyor (tümüyle ayırt edilemez hale geliyorsa), o parametre **aslî bir serbestlik derecesidir**.  
**Hülasa**  
Bir küme girdi-çıktı kutusu olmak zorunda değildir; fakat **kendi iç nizamında birbirini doğurmayan, birbirine dik (bağımsız) ve elemanlarını tekil olarak nitelemeye yeten asgari parametreler demetine** sahip olmak zorundadır.  
Kategori hatasından kaçınmanın anahtarı:  
* Elemanın **"kendi iç yapısını" (zâtını)**,  
* O elemanın **"kullanıldığı yeri, harici gayesini yahut tarihi şartlarını" (arazlarını)** birbirinden tefrik etmektir.  
Bunu yaptığında bir kimya tablosunu da, sayılar teorisini de, fıkıh kaidelerini de hiçbir yapay kutu metaforuna muhtaç kalmadan tam ve örtücü bir hendeseyle tasnif edebilirsin.  
  
  
“Bir boyutu zihnen sıfırladığında yahut yok saydığında küme hala ayakta kalıyor mu?  
￼ Eğer bir parametreyi çektiğinde geriye kalan yapı mefluç olmuyor, küme kendi sınırları içinde tanımlı kalmaya devam ediyorsa, o parametre haricidir veya tali bir arazdır.  
￼ Eğer o parametreyi çektiğinde kümenin elemanları birbirine çöküyor (tümüyle ayırt edilemez hale geliyorsa), o parametre aslî bir serbestlik derecesidir.”  
  
Mesela?  
  
Bu usulü havada bırakmayıp doğrudan üç farklı varlık sahasından somut numunelerle masaya yatıralım:  
**1. Riyazî/Hendesi Numune: "Dörtyüzlüler (Tetrahedron) Kümesi"**  
Uzayda tanımlı üçgen piramitleri tasnif ediyoruz.  
* **Aday Parametre A: "Cismin Hacmi ve Kenar Uzunlukları Oranı" (Aslî Serbestlik Derecesi)**  
    * **Test:** Bu parametreyi zihnen sıfırla yahut yok say.  
    * **Netice:** Bütün dörtyüzlülerin nispetlerini eşitlemiş olursun; düzgün (eşkenar) piramit ile bir iğne gibi yassılmış piramidin farkı ortadan kalkar. Elemanlar biçimsel bakımdan tek bir noktaya çöker, birbirine karışır. Demek ki bu boyut **aslî bir serbestlik derecesidir**.  
* **Aday Parametre B: "Cismin Uzaydaki Koordinatı / Konumu (x, y, z)" (Araz / Harici Değişken)**  
    * **Test:** Bu parametreyi yok say (bütün dörtyüzlüleri orijine taşı).  
    * **Netice:** Piramidin dörtyüzlü olma mahiyeti zerre kadar sarsılmaz; kenar nispetleri, açıları ve geometrik hüviyeti tastamam ayakta kalır. Demek ki cismin uzaydaki yeri bir serbestlik derecesi değildir; ona sonradan ilişen **harici bir arazdır**.  
**2. Tabiat İlmi Numunesi: "Kimyasal Elementler Kümesi (Periyodik Tablo)"**  
Maddenin yapı taşlarını tasnif ediyoruz.  
* **Aday Parametre A: "Çekirdekteki Proton Sayısı (Z)" (Aslî Serbestlik Derecesi)**  
    * **Test:** Proton sayısını zihnen yok say.  
    * **Netice:** Altın ile cıva, hidrojen ile demir arasındaki bütün ayrım anında buharlaşır; 118 elementin tamamı tek bir homojen nükleon çorbasına çöker, element mefhumu imha olur. Demek ki proton sayısı **kurucu ve aslî serbestlik derecesidir**.  
* **Aday Parametre B: "Elementin Doğadaki Rezerv Miktarı veya Piyasa Fiyatı" (Araz / Harici Değişken)**  
    * **Test:** Dünyadaki altın rezervini sıfırla yahut fiyatını yok say.  
    * **Netice:** Altın atomu kendi atomik yapısıyla, valans elektronlarıyla ve kimyasal tabiatıyla yerli yerinde durur; elementler kümesi hiçbir şey kaybetmez. Demek ki "fiyat/bulunurluk", periyodik tablonun serbestlik derecesi olamaz; nesneye sonradan yapışan harici bir vasıftır.  
**3. Fıkıh/Hukuk Numunesi: "Akitler (Sözleşmeler) Kümesi"**  
Hukuki işlemleri tasnif ediyoruz.  
* **Aday Parametre A: "İvaz (Bedel / Karşılık) Şartı" (Aslî Serbestlik Derecesi)**  
    * **Test:** Akitlerdeki ivaz (bedel) şartını yok say.  
    * **Netice:** Satış (*bey'*) akdi ile bağış (*hibe*) akdi, kira (*icâre*) akdi ile ödünç (*âriyet*) akdi arasındaki sınır çöker; ticaret ile teberru birbirine karışır, sistem ayırt ediciliğini kaybeder. Demek ki ivazlı/ivazsız olma vasfı akitler kümesinin **aslî serbestlik derecesidir**.  
* **Aday Parametre B: "Akdin Yazıldığı Kâğıdın Cinsi veya Mürekkebin Rengi" (Araz / Harici Değişken)**  
    * **Test:** Kâğıdı yahut mürekkebi yok say; akdi şifahi veya dijital kabul et.  
    * **Netice:** Akdin sıhhati, borç doğurması, mülkiyet intikali ve hukuki mahiyeti zerre kadar değişmez; akitler kümesi dimdik ayakta kalır. Demek ki kâğıt türü akitler kümesinin serbestlik derecesi değildir; laubali bir arazdır.  
Bir parametrenin sahici serbestlik derecesi olup olmadığını anlamanın yolu bu kadar yalındır: **Onu çekip aldığında kümenin fertleri birbirine karışıp bir pelteye dönüyorsa zâtîdir; küme kendi iç intizamını muhafaza ediyorsa kapının dışına konulacak bir arazdır.**  
  
  