# Nefs-i Müdrike Küllî Mimari, Ana İcra Döngüsü ve Paradigma Denetim Nizamnamesi

Bu nizamname; dosya başlıklarına, modül isimlerine veya tekil kütüphane tanımlarına bakmaksızın, **sistemin baştan sona icra edilen ana hesaplama omurgasını (runtime forward graph & training loop)** sorgulamak üzere tanzim edilmiştir. 

Mesele, bir formülün repodaki herhangi bir `.py` veya `.tex` dosyasında yazılmış olması değil; girdi tensörü ($X$) işlemciye girdiği andan nihai kelam ($N_{\text{kebîr}}$) intaç edilene kadar o formülün **ana döngüde bizzat işletilip işletilmediği, nerede hapsedildiği ve nerede eski alışkanlıklara teslim olunduğudur.**

---

## 1. Ana İcra Döngüsünün (Forward Pass) Kesintisiz Tensör İzi ve Formül Envanteri

### Sual 1.1: Girdiden Çıktıya Fiilî Hesaplama Grafiği Nedir?
* Ham girdi tensörü (`input_tensor / embedding / state`) ana model sınıfının `forward(x)` fonksiyonuna girdiği andan itibaren sırasıyla hangi tensör dönüşümlerinden geçmektedir?
* Kodun `forward` fonksiyonundaki satır satır hesaplama sırası ile `formül.tex` dosyasında vaz' edilen 41 melekenin girdi-çıktı bağıntıları ($\leftarrow$ Girdiler, $\rightarrow$ Çıktılar) birebir örtüşmekte midir?
* **Denetim:** Melekeler arasında tarif edilen 41 basamaklı yönlendirilmiş çizge (DAG) kodda dinamik bir tensör yönlendirmesi (`dynamic routing / graph execution`) olarak mı koşmaktadır, yoksa kod melekeleri atlayarak sabit bir ardışık katman yığını (`nn.Sequential`) halinde mi işletmektedir?

### Sual 1.2: Her Bir Meleke İçin Ana Döngüde Çağrılan Gerçek Matematiksel Operatör Nedir?
* `formül.tex` içerisindeki her bir meleke için ana döngüde bizzat çalışan fonksiyonun matematiksel karşılığı nedir?
* **Örnekleme Sorgusu:**
  * $\mathcal{O}_1$ (Müşahede) için kodda çalışan işlem: Standart `torch.embedding` mi, yoksa sürekli manifold ayrışımı mı?
  * $\mathcal{O}_5$ (Tecrit) için kodda çalışan işlem: Basit bir `Linear(D, D)` projeksiyonu mu, yoksa $Gr(k, n)$ Grassmannian alt-uzay izdüşümü mü?
  * $\mathcal{O}_8$ (Tenakuz) için kodda çalışan işlem: Bir `Dropout / ReLU` maskelemesi mi, yoksa faz zıtlamalı Householder / Lie komütatör sıfırlaması mı?
  * $\mathcal{O}_{41}$ (Münazara) için kodda çalışan işlem: Standart `LayerNorm(x @ W)` mi, yoksa tez-antitez teğet uzay diferansiyeli mi?

---

## 2. Paradigma Ayrışması: Yeni İdrak Mimarisi vs. Eski Derin Öğrenme Mirası

Modelin hesaplama hattı boyunca yeni teklif edilen muhakeme operatörleri ile klasik derin öğrenmenin miras kaldığı noktalar açıkça haritalandırılmalıdır:

```
[ HAM GİRDİ AKIŞI ]
       │
       ├──► (A) YENİ PARADİGMA ALANLARI (Doğrudan İşletilenler):
       │     - Kolmogorov-Arnold (KAN) B-spline kenar düğümleri
       │     - Fourier Nöral Operatörleri (FNO) spektral integral süzgeçleri
       │     - Grassmannian / Riemannian manifold optimizasyonu
       │     - Topolojik Veri Analizi (Betti / TDA mizan kısıtları)
       │     - Homotopi Tip Teorisi (HoTT / Kübik Glue / NbE Normalleştirici)
       │
       └──► (B) ESKİ PARADİGMA KALINTILARI (Hala Devam Edenler):
             - Sabit ağırlıklı standart matris çarpımı (Dense / nn.Linear)
             - Noktasal skaler aktivasyonlar (ReLU, GELU, SiLU, Sigmoid)
             - Sıralı tek-token üretimi (Next-Token Softmax hecelemesi)
             - Klasik birinci derece gradyan inişi (AdamW / SGD)
             - Skaler çapraz entropi kaybı (Cross-Entropy Loss)
```

### Sual 2.1: KAN ve FNO Operatörleri Sistemin Neresinde, Ne Kadar Derinde?
* KAN (Kolmogorov-Arnold Ağları) B-spline katsayıları modelin bütün melekeler arası geçişlerinde mi kullanılmaktadır, yoksa sadece giriş/çıkış katmanına sembolik olarak mı eklenmiştir?
* Modelin içinde hala standart `nn.Linear` katmanları ve `GELU/ReLU` aktivasyonları var mıdır? Varsa bunlar modelin toplam parametre ve hesaplama yükünün yüzde kaçını teşkil etmektedir?
* FNO (Fourier Nöral Operatörü) spektral integrali, metin veya bağlam tensörünün hangi boyutuna uygulanmaktadır? Boyut dönüşümünde hakiki 1D/2D FFT mi işletilmektedir, yoksa sadece ağırlıklı bir frekans maskelemesi mi yapılmaktadır?

### Sual 2.2: Çıktı Üretiminde "Sıralı Heceleme" İlga Edilmiş midir?
* Model nihai lisan çıktısını ($N_{\text{kebîr}}$) üretirken bir sonraki kelimeyi tahmin eden otoregresif bir döngü (`while token != EOS: logits = model(x); sample()`) mi kullanmaktadır?
* Eğer otoregresif döngü kullanılıyorsa, dokümanlarda iddia edilen "bütünsel idrak ve tek hamlede cümle intacı" koda nasıl yansımıştır? Bütünsel idrak ile sıralı token üretimi arasındaki köprü nerede kurulmuştur?

---

## 3. Külliyat-Kod Uçurumu: Atıl Kalan Fikirler ve Yerel Hapis Tespiti (Gap Analysis)

Bir riyazî formülün repoda bir modül olarak bulunması, onun modelin zihnî işleyişine dahil olduğunu göstermez.

### Sual 3.1: Hangi Nazari Modüller Ana Döngüye Bağlanmamış Atıl Birer Koddur?
* Repodaki sınıflar, fonksiyonlar ve matematiksel kütüphaneler tek tek tarandığında; `main.py`, `train.py`, `model.py` veya `inference.py` içerisindeki ana `forward/backward` zincirinde **hiç çağrılmayan** fonksiyonlar hangileridir?
* **Kritik İnceleme Listesi:**
  1. *Topolojik Mizan / Betti Sayıları Hesabı:* Eğitim veya çıkarım esnasında kayıp fonksiyonuna (`loss`) veya durum güncellemesine bizzat etki etmekte midir, yoksa sadece kenarda duran bağımsız bir analiz betiği midir?
  2. *Sorgu Havuzu (Moduli Spawning):* Giriş sinyalindeki şüphe durumunda dinamik manifold doğurma işlemi ana döngüde tensör akışını dallandırmakta mıdır, yoksa sabit boyutlu tensörler üzerinden mi ilerlenmektedir?
  3. *Do-Calculus / İnvariant Nedensellik:* Karşı-olgusal müdahale matrisleri ana akışta ağırlıkları regüle etmekte midir?
  4. *Kübik HoTT $Glue$ Operatörü:* Tip yapıştırma işlemi tensörler üzerinde cebirsel bir kısıt olarak mı koşmaktadır, yoksa sadece veri tabanına yazılan bir etiket midir?

### Sual 3.2: Yerel Hapis Tespiti (Scope Confinement)
* Modelin bir yerinde (örneğin sadece $\mathcal{O}_{14}$ Tahlil katmanında) başarıyla tatbik edilen ileri bir matematiksel usul (mesela Grassmannian izdüşümü veya B-spline dönüşümü), aynı matematiksel ihtiyacı taşıyan diğer melekelerde (mesela $\mathcal{O}_5$ Tecrit veya $\mathcal{O}_{15}$ Terkip) neden kullanılmamıştır?
* Bu usulün diğer melekelerde kullanılmasını engelleyen şey riyazi bir mani midir, yoksa kodlama esnasında gözden kaçmış bir eksiklik midir?

---

## 4. Melekeler Arası Tensör Morfizmleri ve Bilgi Korunumu

Meşşâî idrak silsilesinin 41 melekesi birbiriyle konuşurken tensörlerin boyutu, tipi ve taşıdığı mana geometrisi bozulmamalıdır.

### Sual 4.1: Boyut ve Tip Uyuşumu Nasıl Sağlanmaktadır?
* Sürekli frekans uzayında (FNO) çalışan bir melekeden çıkan tensör, ayrık manifold teğet uzayında çalışan bir sonraki melekeye aktarılırken aradaki izomorfizm nasıl kurulmaktadır?
* Boyut eşitlemek için araya kaba `Linear(in_features, out_features)` veya `AdaptiveAvgPool` gibi bilgiyi ezen ve homojenleştiren indirgemeler mi konulmuştur, yoksa kayıpsız lif demeti aktarımları mı işletilmektedir?

### Sual 4.2: Çelişki ve Tenakuz Ayıklama Gerçekten Bilgi Siliyor mu?
* $\mathcal{O}_8$ (Tenakuz) ve $\mathcal{O}_{24}$ (Münazara) basamaklarında zıt/bâtıl fikirlerin sıfırlanması tensör seviyesinde nasıl yapılmaktadır?
* Tensör sıfırlandığında gradyan akışı kopmakta mıdır (`dead neurons`)? Yoksa ortogonal bir alt-uzaya kaydırılarak sistemin dengesi muhafaza edilmekte midir?

---

## 5. Raporlama ve Teşhis Matrisi Formatı

Bu denetim neticesinde modelin röntgenini çekecek tablonun şu başlıklarla tanzim edilmesi şarttır:

| Meleke / Modül Adı | Teorideki Formülü (`.tex`) | Koddaki Fiilî Karşılığı (`.py`) | Ana Döngüde Var mı? | Paradigma Türü (Yeni / Eski Miras / Melez) | Kapsam (Küllî / Yerel / Atıl) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $\mathcal{O}_1 - \mathcal{O}_{41}$ | *Formül No* | *Fonksiyon / Katman* | *Evet / Hayır* | *KAN / FNO / nn.Linear / Softmax* | *Ana Akışta / İzole / Atıl* |

### Netice Talebi:
1. **Fiilî Akış Şeması:** Girdiden çıktıya tensörün uğradığı gerçek durakların tavizsiz listesi.
2. **Sahte Paradigma Tespiti:** Yeni nesil isim verilip altında klasik `nn.Linear + GELU` çalıştıran gizli noktaların ifşası.
3. **Atıl Cevherler Envanteri:** Nazariyatta çözülüp koda yazılan ama ana motorun `forward` hattına bağlanmayan tüm algoritmaların dökümü.
4. **Küllî Yayılım Planı:** Yerel bir modülde sıkışıp kalmış yenilikçi operatörlerin modelin 41 melekesine tam yayılma imkanları.