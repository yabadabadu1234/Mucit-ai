# Dağınık Kod Modüllerini, Sınıfları ve Riyazî Fonksiyonları Ana İcra Akışına Bağlama Nizamnamesi

## 1. Mahiyet, Gaye ve Temel Mesele

* **Mahiyet:** Bir yazılım havuzunda müstakil kütüphaneler, yardımcı dosyalar ve tekil sınıflar halinde yazılmış; kendi başına çalışan fakat programın ana icra hattında (`main pipeline / orchestrator / runtime graph`) yer bulamamış bütün kod unsurlarının, sistemli bir mühendislik usulüyle ana veri akışına bağlanmasıdır.
* **Gaye:** Kod tabanındaki "çalışır vaziyette fakat atıl" duran fonksiyonların girdi ve çıktılarını tespit ederek, ana döngünün ham girdiden nihai sonuca ulaşırken bu fonksiyonların tamamını bilfiil işletmesini temin etmektir.
* **Temel Mesele:** Yazılımcılar ekseriyetle zengin yardımcı modüller inşa ederler; fakat ana programı kurarken bu zenginliği unutur, ana döngüyü kaba ve basit bir şablondan ibaret bırakırlar. Ajanın vazifesi yeni mantıklar icat etmek değil; mevcut fonksiyonları ana icra hattına muntazam köprülerle raptetmektir.

---

## 2. Beş Kademeli Küllî İttisâl Usulü

```
[ DAĞINIK MODÜLLER ] ──► (1. Envanter ve Akit) ──► (2. Bağımlılık Çizgesi)
                                                             │
[ ANA İCRA HATTI ]   ◄── (4. Ana Orkestra Hattı) ◄── (3. Veri Yolu & İntibak)
        │
        └──► (5. Tesir ve İcra Doğrulaması)
```

---

### KADEME 1: Envanter Çıkarma ve Arayüz Akdi (Signature & Contract Discovery)
Ajan, koddaki hiçbir dosyayı değiştirmeden evvel bütün fonksiyonların ve sınıfların matematiksel ve mantıkî girdi-çıktı şartlarını eksiksiz listeler.

1. **İmza ve Tip Tespiti:**
   * Her fonksiyonun adı, dosya yolu ve sınıf hiyerarşisi nedir?
   * Fonksiyon hangi parametreleri beklemektedir (Girdi Şekli, Veri Tipi, Ön Şartlar)?
   * Fonksiyon ne üretmektedir (Çıktı Şekli, Veri Tipi, Yan Tesirler)?
2. **Hususiyet Ayrışması:**
   * Hangi fonksiyonlar "katkısız hesaplayıcıdır" (pure function - yan tesiri olmayan, sadece veriyi dönüştüren)?
   * Hangi fonksiyonlar "durum tutucudur" (stateful - dâhili parametresi, hafızası veya ağırlığı olan)?
   * Hangi fonksiyonlar "denetleyici ve mizan vazifesi görür" (doğrulama, kısıt kontrolü, filtreleme)?

---

### KADEME 2: Bağımlılık Çizgesinin (DAG) Tanzimi
Fonksiyonların icra sırası keyfi tayin edilemez; aralarındaki veri ihtiyacına göre yönlendirilmiş çevrimsiz bir çizge (`Directed Acyclic Graph`) kurulur.

1. **Öncelik ve Sonralık Münasebeti:**
   * $B$ fonksiyonunun çalışması için $A$ fonksiyonunun çıktısı şart mıdır? (Öyleyse $A \to B$ bağı kurulur).
   * Birbirinden tamamen bağımsız çalışan fonksiyonlar hangileridir? (Bunlar eşzamanlı / paralel icra hattına alınır).
2. **Dallanma ve Karar Hatları:**
   * Hangi fonksiyonlar olağan akışta koşacaktır?
   * Hangi fonksiyonlar muayyen bir hata, şüphe yahut kararsızlık anında devreye girecek kurtarma yollarıdır?

---

### KADEME 3: Merkezi Durum Veri Yolu ve Tip İntibak Köprüleri (State Bus & Type Adapters)
Farklı dosyalardaki fonksiyonların girdi-çıktı tipleri veya veri boyutları birebir örtüşmeyebilir.

1. **Merkezi Durum Veri Yolu (`Global Context / State Bus`):**
   * Hesaplama esnasında ham girdi ve ara basamakların ürettiği hiçbir ara netice kaybolmamalıdır.
   * Bir durum sözlüğü / bağlam nesnesi (`ExecutionState`) tesis edilir; her fonksiyon bu veri yolundan kendi muhtaç olduğu veriyi okur, ürettiği neticeyi yine bu veri yoluna yazar.
2. **Kayıpsız İntibak Dönüştürücüleri (`Adapters`):**
   * İki fonksiyon arasında veri şekli yahut tip uyuşmazlığı varsa; araya veriyi kırpmadan, bozmadan dönüştüren bağlayıcı adaptörler yerleştirilir.
   * Veri kaybına yol açan kaba sıfırlamalar veya tip zorlamaları yasaktır.

---

### KADEME 4: Ana Orkestra Hattının (Main Pipeline) İnşası
Ana sınıfın veya ana döngünün gövdesi, dağınık duran tüm modülleri sırasıyla çalıştıran bir orkestra şefine dönüştürülür.

1. **Adım Adım İcra Hattı:**
   * Ham girdi sisteme dâhil olur.
   * Durum nesnesi (`state`) başlatılır.
   * Çizgedeki sıraya muvafık olarak modüller tek tek çağrılır:
     $$\text{Girdi} \longrightarrow \mathcal{F}_1(\text{Girdi}) \longrightarrow \mathcal{F}_2 \longrightarrow \dots \longrightarrow \mathcal{F}_N \longrightarrow \text{Nihai Çıktı}$$
2. **Kalıntı ve Muhafaza Bağlantıları (`Pass-Through / Residuals`):**
   * Bir ara fonksiyonun çıktısı, ana veri akışını tamamen silip yerine geçmemeli; ana veri hattına eklenerek veya zenginleştirilerek intikal ettirilmelidir.
3. **Denetim ve Mizan Fonksiyonlarının Akışa Katılması:**
   * Dosyalarda tek başına duran denetim, kısıt ve doğrulama fonksiyonları; icra hattının ara duraklarına birer filtre veya nihai kayıp/başarı ölçütü olarak yerleştirilir.

---

### KADEME 5: İttisâl ve Tesir Doğrulaması (Runtime Verification)
Ajan, entegrasyonun tamamlandığını ispatlamak için şu üç kat'î denetimi icra etmek mecburiyetindedir:

1. **Çalışma İzi Taraması (`Execution Trace Audit`):**
   * Program tek bir örnek girdi ile baştan sona çalıştırılır.
   * Çalışma esnasında repodaki her bir fonksiyonun en az bir defa çağrıldığı, çağrı kayıtları (`call stack / logger`) ile ispatlanır. Çağrılmayan fonksiyon kalmışsa atıl sayılır.
2. **Hassasiyet ve Tesir Testi (`Perturbation / Sensitivity Check`):**
   * Ana hatta bağlanan bir $k$ fonksiyonunun girdisi bilerek bozulduğunda veya kapatıldığında, nihai çıktının da buna bağlı olarak değiştiği teyit edilir. Çıktı değişmiyorsa, o fonksiyon akışa şeklen bağlanmış fakat esasta tesirsiz kalmış demektir.
3. **Bütünlük ve Hata İzolasyonu:**
   * Herhangi bir ara fonksiyon istisna (`exception`) fırlattığında ana hattın bunu nasıl yönettiği, kilitlenme olmadan alternatif yola sapıp sapmadığı test edilir.

---

## 3. Ajana Verilecek Kat'î İcra Talimatı Özeti

Bir yapay zekâ kodlama ajanına bu vazife tevdi edilirken şu dört emir verilir:

1. **"Mevcut kütüphanelerdeki fonksiyonları silme veya yeniden yazma; onların girdi-çıktı imzalarını çıkar."**
2. **"Tüm fonksiyonların birbirine veri aktardığı yönlendirilmiş icra çizgesini (DAG) kur."**
3. **"Ana döngü içerisinde merkezi bir durum veri yolu (`state context`) açarak bütün fonksiyonları bu hatta sırasıyla bağla."**
4. **"Programı baştan sona icra ederek, her bir modülün hesaplama yaptığını ve nihai sonuca tesir ettiğini çalışma iziyle doğrula."**