# Nefs-i Müdrike Kod Tabanı ve Ana İcra Döngüsü Paradigma Denetimi

## 1. Mahiyet ve Denetim Mihveri
Bu denetimin mihveri; dosyalarda yazılı olan nazari iddialar veya tekil yardımcı modüller değil, **sistemin baştan sona icra edilen ana hesaplama hattıdır (runtime execution loop / forward graph)**.

Bir riyazî usulün bir kütüphanede veya dosyada tanımlanmış olması, modelin o usulle çalıştığını ispatlamaz. Denetim; ham girdinin ($X$) sisteme girdiği andan nihai çıktının intaç edildiği ana kadar tensörlerin bizzat geçtiği yolları, işletilen fonksiyonları ve alt sistemlerin birbirine nasıl bağlandığını sorgular.

---

## 2. Ana Döngüde İcra Edilen Formüllerin Tespiti (Hesaplama Grafiği Gerçekliği)

### 2.1. İcra Hattı Envanteri
* **Soru:** Ham girdi tensörü (`input_tensor`) modelin `forward` çağrısına girdikten sonra sırasıyla hangi matematiksel operatörlerden geçmektedir?
* **Denetim:**
  1. Ana döngü içerisinde bizzat çağrılan ve tensör dönüşümü yapan formüllerin tam listesi nedir?
  2. Her bir meleke adımı (`Meleke_1` $\to$ `Meleke_41`) ana döngüde müstakil bir fonksiyon veya katman olarak işletilmekte midir, yoksa bu melekelerin bir kısmı tek bir kaba tensör çarpımına indirgenmiş midir?
  3. Girdi-çıktı bağıntılarında (`formül.tex` dosyasında vaz' edilen $\leftarrow$ Girdi ve $\rightarrow$ Çıktı yönlendirmeleri) belirtilen bilgi akış yolları, koddaki tensör yönlendirmeleriyle (`tensor routing / residual connections / graph edges`) birebir örtüşmekte midir?

---

## 3. Paradigma Ayrışması: Yeni Muhakeme vs. Eski Alışkanlıklar

Modelin mimarisi incelenirken, teklif edilen yeni nesil operatörler ile klasik derin öğrenmenin miras kaldığı noktalar açıkça haritalandırılacaktır:

```
[ GİRDİ AKIŞI ]
       │
       ├──► (A) YENİ PARADİGMA ALANLARI:
       │     - Kolmogorov-Arnold (KAN) B-spline düğüm dönüşümleri
       │     - Fourier Nöral Operatörleri (FNO) spektral integralleri
       │     - Grassmannian Manifold izdüşümleri ve alt-uzay hizalamaları
       │     - Topolojik Veri Analizi (Betti / TDA mizan denetimleri)
       │     - Homotopi Tip Teorisi (HoTT / Glue yapıştırma operatörleri)
       │
       └──► (B) ESKİ PARADİGMANIN DEVAM ETTİĞİ YERLER:
             - Sabit ağırlıklı standart matris çarpımları (Linear / Dense layers)
             - Kaba nokta-tabanlı aktivasyonlar (ReLU, GELU, Sigmoid)
             - Sıralı tek-token tahmini (Next-Token Softmax)
             - Klasik birinci derece gradyan inişi (Adam / SGD optimizasyonu)
```

### 3.1. Paradigma Denetim Soruları
1. **Aktivasyon ve Fonksiyon Öğrenimi:** Modelin hangi katmanlarında sabit skaler aktivasyonlar (GELU/ReLU) terk edilip KAN B-spline veya FNO spektral süzgeçleri konulmuştur? Eski MLP blokları nerelerde hala varlığını sürdürmektedir?
2. **Bağlam ve Temsil Uzayı:** Token temsilleri standart öklidyen gömme (embedding) vektörleri olarak mı kalmaktadır, yoksa her bir token veya cümle bir alt-manifold / lif demeti yapısında mı işlenmektedir?
3. **Mizan ve Karar:** Hata kontrolü ve denetim mekanizması klasik bir Cross-Entropy kaybından mı ibarettir, yoksa topolojik kalıcı homoloji (Betti sayıları) ve nedensel müdahale (Do-calculus) mizanları ana döngüde birer kayıp/kısıt fonksiyonu olarak aktif çalışmakta mıdır?

---

## 4. Külliyat-Kod İttisali ve Atıl Fikirler Cetveli (Gap Analysis)

Nazari dokümanlarda (70 Darboğaz, 41 Meleke, Topos Tebliği vb.) teklif edilen çözümlerin koddaki fiili karşılığı denetlenecektir:

| Nazari Teklif / Formül | Koddaki Yeri (Modül / Sınıf) | Ana Döngüde Çağrılıyor mu? | Durum (Aktif / Kısmi / Atıl) |
| :--- | :--- | :--- | :--- |
| **B-Ayrışması ve Fıtrat Filtresi** | *Dosya / Satır No* | *Evet / Hayır* | *Aktif İcrada / Yalnız Yardımcı Sınıf / Atıl* |
| **41 Meleke Dinamik Yönlendirmesi** | *Dosya / Satır No* | *Evet / Hayır* | *Aktif İcrada / Yalnız Yardımcı Sınıf / Atıl* |
| **Grassmannian Manifold İzdüşümü** | *Dosya / Satır No* | *Evet / Hayır* | *Aktif İcrada / Yalnız Yardımcı Sınıf / Atıl* |
| **Topolojik Betti Mizanı (TDA)** | *Dosya / Satır No* | *Evet / Hayır* | *Aktif İcrada / Yalnız Yardımcı Sınıf / Atıl* |
| **Sorgu Havuzu (Moduli Spawning)** | *Dosya / Satır No* | *Evet / Hayır* | *Aktif İcrada / Yalnız Yardımcı Sınıf / Atıl* |
| **Homotopik $Glue$ ve $h$-Level 0** | *Dosya / Satır No* | *Evet / Hayır* | *Aktif İcrada / Yalnız Yardımcı Sınıf / Atıl* |

### 4.1. Atıl Kalma Nedenlerinin Tespiti
* Bir formül veya modül kodda mevcut olduğu halde ana döngüde çağrılmıyorsa; bunun sebebi bir hesaplama karmaşıklığı darboğazı mıdır, tensör boyut uyuşmazlığı mıdır, yoksa entegrasyonun yarım kalması mıdır?
* Bir formül ana döngüde kullanıldığı halde yalnız tek bir yerde mi (örneğin sadece son katmanda) kalmıştır? Bu operatörün modelin diğer ara katmanlarında da kullanılması mümkün ve lüzumlu mudur?

---

## 5. Melekeler Arası Tensör İletişimi ve Tip Uyuşumu

Meşşâî idrak melekelerinin koddaki irtibat noktaları tetkik edilecektir:

1. **Tensör Dönüşüm Köprüleri:** $\mathcal{O}_1$ (Müşahede) çıktısı $\mathcal{O}_5$ (Tecrit) katmanına aktarılırken tensörün boyutu, tipi ve gradyan izleme özelliği korunmakta mıdır?
2. **Boyut ve Şekil İntibakı:** Farklı geometrilere sahip melekeler (örneğin spektral frekans uzayında çalışan bir operatör ile uzaysal teğet uzayında çalışan bir operatör) birbiriyle konuşurken aradaki dönüşüm matrisleri tensörün manasını bozmadan taşıyabilmekte midir?
3. **Münazara ve Tenakuz Ayıklama:** Çelişkili durumların sıfırlanması koddaki tensör operasyonlarında nasıl icra edilmektedir (Maskeleme, Zıt Tensör Çıkarması, İzdüşüm)?

---

## 6. Denetim Raporu Çıktı Şablonu

Bu analizi yürütecek sistemin sunması gereken nihaî tablo:

1. **Ana Döngü Akış Şeması:** Girdiden çıktıya tensörlerin uğradığı tüm gerçek duraklar.
2. **Kullanılan Formüller Kataloğu:** `forward()` içinde fiilen tensör hesaplayan tüm denklemler.
3. **Miras vs. Yeni Paradigma Oranı:** Kodun yüzde kaçının klasik mimari (MLP/Linear/Transformer), yüzde kaçının yeni operatör (KAN/FNO/Manifold/TDA) olduğu.
4. **Atıl Kalan Formüller Listesi:** Dosyalarda olup koda girmeyen veya kodda yazılıp ana akışa bağlanmayan tüm kuramsal unsurlar.
5. **Kapsam Genişletme Teklifleri:** Bir noktada kullanılıp diğer melekelerde ihmal edilen yeni operatörlerin ana döngüye tam yayılma haritası.