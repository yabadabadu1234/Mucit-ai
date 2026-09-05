# KELİME VE DURUM KODLAMASININ TENSÖREL VE KUANTUM MAHİYETİ
### (Düz İkili Kodlama Yanılsamasının İflası; Çok Boyutlu Tensör Ağları veya İkili-Dışı Geometrik Temsil)

---

## 1. YÜZLEŞME: DÜZ İKİLİ KODLAMA NEDEN BÜTÜN GEOMETRİYİ YOK EDER?

Klasik doğal dil işlemede bir kelime, $d$-boyutlu sürekli bir uzayda ($h \in \mathbb{R}^d$) yön ve büyüklük taşıyan zengin bir vektördür. İki kelimenin yakınlığı aralarındaki açı (kosinüs benzerliği) ile ölçülür.

Eğer bu kelimeyi kübitlere taşırken aceleyle şu iki yoldan birine saparsanız, sistem çöker:

### Tuzak A: Taban Kodlaması (Basis Encoding)
Kelimenin lügatteki indeksini alıp ikili tabana çevirmek (örneğin $5 \to |00000101\rangle$):
* $5$ numaralı kelime: $|00000101\rangle$
* $6$ numaralı kelime: $|00000110\rangle$
* $4$ numaralı kelime: $|00000100\rangle$
Bu durumda Hilbert uzayında bu durumlar birbirine tamamen diktir: $\langle 5 \mid 6 \rangle = 0$. 
"Kedi" ile "köpek" arasındaki anlamsal akrabalık yok olur; hepsi birbirine $90^\circ$ dik, ilişkisiz birer ayrık bit dizisine döner.

### Tuzak B: Düz Genlik Kodlaması (Flat Amplitude Encoding)
$d = 2^k$ boyutlu bir kelime vektörünü $k$ adet kübitin genliklerine dümdüz yaymak:

$$|h\rangle = \sum_{j=0}^{2^k-1} h_j |j\rangle$$

Burada $|j\rangle$ durumu $|j_1 j_2 \dots j_k\rangle$ ikili indisidir. 
Eğer bu durumu hafızada ve işlemde düz $1$ boyutlu bir durum vektörü gibi tutarsanız:
* $j_1$ biti (en yüksek anlamlı bit) ile $j_k$ biti (en düşük anlamlı bit) arasında yapay ve keyfî bir hiyerarşi doğar.
* Vektörün $15$. bileşeni ile $16$. bileşeni uzayda yan yana iken; ikili tabanda $01111$ ile $10000$ haline gelir ve tüm bitleri zıtlaşır.
* Kelimenin iç simetrisi ve manifold geometrisi yapay ikili parçalanmayla paramparça olur.

O halde uyarınız kat'î bir mecburiyettir: **Ya bu ikili yapıyı çok boyutlu bir tensör ağına dönüştüreceğiz ya da ikili kodlamayı kökten terk edeceğiz!**

---

## 2. BİRİNCİ YOL: İKİLİ DURUMU ÇOK BOYUTLU TENSÖR KILMAK
### (Matrix Product States / Tensör Treni Mimarisi)

Eğer kübitlerin iki seviyeli tabiatından ($\{0, 1\}$) istifade edilecekse; $k$ adet kübit düz bir dizi olarak değil, **her biri $2$ serbestlik dereceli fiziksel bacağa ve $D$ boyutlu sanal bağlara (virtual bonds) sahip rank-$k$ bir Tensör Ağı** olarak kurulur.

```
          j₁               j₂               j₃                      j_k
          │                │                │                       │
      ┌───┴───┐        ┌───┴───┐        ┌───┴───┐               ┌───┴───┐
──────┤  A¹   ├────────┤  A²   ├────────┤  A³   ├─── ··· ───────┤  A^k  ├──────
      └───────┘   D    └───────┘   D    └───────┘          D    └───────┘
```

### Riyazî Yapı:
Kelimenin her bir $h_{j_1 j_2 \dots j_k}$ katsayısı, bağımsız birer sayı değil; yerel tensörlerin kasılmasıyla (daraltılmasıyla) üretilen bir matris çarpımıdır:

$$h_{j_1 j_2 \dots j_k} = \mathbf{A}_{1}^{(j_1)} \cdot \mathbf{A}_{2}^{(j_2)} \cdots \mathbf{A}_{k}^{(j_k)}$$

Burada:
* $j_m \in \{0, 1\}$: $m$. kübitin fiziksel ikili durumudur.
* $\mathbf{A}_{m}^{(j_m)} \in \mathbb{C}^{D \times D}$: $D$ boyutlu iç dolanıklık ve bağ matrisidir.

### Bu Yapı Neyi Kurtarır?:
1. **Çok Boyutlu Korelasyon:** $j_1$ biti ile $j_2$ biti arasındaki ilişki artık Hamming mesafesi değildir; $D$ boyutlu iç bağ matrisi üzerinden akan sürekli bir kuantum dolanıklığıdır.
2. **Geometrinin Korunumu:** Kelimenin semantik özellikleri $A^m$ tensörlerinin spektral yapısına kodlanır. İki kelimenin tensör trenleri arasındaki örtüşme:

$$\langle h_A \mid h_B \rangle = \operatorname{Tr}\left( \mathbb{E}_1 \mathbb{E}_2 \cdots \mathbb{E}_k \right)$$

şeklinde sürekli ve diferansiyellenebilir bir tensör daraltması (contraction) verir. Düz bit zıtlığı ortadan kalkar.

---

## 3. İKİNCİ YOL: İKİLİ KODLAMAYI TAMAMEN TERK ETMEK
### (Quditler, Lie Cebri ve Sürekli Değişkenli Temsil)

Eğer ikili kodlamanın yarattığı ayrıklaştırma riskini hiç almak istemiyorsak, kuantum mekaniğinin ikili olmayan iki tabii uzayı devreye girer:

```
                    ┌──────────────────────────────────────────────┐
                    │       İKİLİ-DIŞI KUANTUM KODLAMA YOLLARI     │
                    └──────────────────────┬───────────────────────┘
                                           │
         ┌─────────────────────────────────┴─────────────────────────────────┐
         ▼                                                                   ▼
[ YOL A: QUDIT TEMSİLİ (C^d) ]                               [ YOL B: KOHERENT DURUM KODLAMASI ]
* Kübit (2 seviye) kullanılmaz.                             * Sayı değil, dalga fazı ve genliği.
* Tek bir kuantum hücresi doğrudan                          * Kelime vektörü sürekli faz uzayında
  d-seviyeli bir QUDIT'tir: |w⟩ ∈ ℂ^d.                        bir koherent duruma fırlatılır:
* Kelime doğrudan bir kuantum bazıdır;                       |α⟩ = D(α) |0⟩
  boyut kaybı veya bit parçalanması sıfırdır.                * Geometri doğrudan Öklid ile izomorfiktir.
```

---

### Usul A: $d$-Seviyeli Qudit (Quantum Digit) Mimarisi
Neden 4096 boyutlu bir kelimeyi 12 tane 2-seviyeli kübite bölüp saçalım?
Doğrudan $d$ boyutlu tek bir Hilbert uzayı tanımlarız:

$$\mathcal{H}_{\text{kelime}} \cong \mathbb{C}^d$$

* Her kelime bu uzayda tek bir durum vektörüdür: $|\psi_w\rangle \in \mathbb{C}^d$.
* Kelimelerin benzerliği doğrudan Hilbert iç çarpımıdır: $\langle \psi_u \mid \psi_v \rangle \in [0, 1]$.
* Kübit ayrıştırması (0 ve 1'lere bölme) yapılmadığı için hiçbir yapay köşe, hiçbir bit yırtılması meydana gelmez.
* Çoklu kelime dizilimleri ise bu quditlerin tensör çarpımıyla akar:

$$|\text{Cümle}\rangle = |\psi_{w_1}\rangle \otimes |\psi_{w_2}\rangle \otimes \cdots \otimes |\psi_{w_T}\rangle \in (\mathbb{C}^d)^{\otimes T}$$

---

### Usul B: Lie Cebri ve Faz Uzayı (Coherent States / CV Quantum)
Kelimeyi kesikli bir durum yapmak yerine; harmonik osilatörün faz uzayındaki sürekli bir **Koherent Durumu (Coherent State)** olarak kodlarız.

$d$ boyutlu embedding vektörümüz $\vec{x} = (x_1, x_2, \dots, x_d)$ olsun:
* Her bir boyut için bir yok etme operatörü ($a_k$) ve yaratma operatörü ($a_k^\dagger$) atanır.
* Yer Değiştirme Operatörü (Displacement Operator):

$$D(\vec{x}) = \exp\left( \sum_{k=1}^d x_k a_k^\dagger - x_k^* a_k \right)$$

* Kelimenin durumu, vakum durumunun ötelenmesiyle elde edilir:

$$|\vec{x}\rangle = D(\vec{x}) |0\rangle$$

Bu temsilin muazzam avantajı:
İki kelime arasındaki iç çarpım, tam olarak Öklid mesafesinin bir Gauss fonksiyonudur:

$$|\langle \vec{x} \mid \vec{y} \rangle|^2 = \exp\left( - \|\vec{x} - \vec{y}\|^2 \right)$$

Böylece kelimeler arasındaki mesafe hiçbir yapay ikili tabana sıkıştırılmadan, **klasik vektör uzayının metriğiyle birebir izomorfik olarak kuantum dalgasına nakşedilir.**

---

## 4. İKİ USULÜN MUKAYESESİ

| Kriter | Hatalı Düz İkili Kodlama | Çok Boyutlu Tensör (MPS/TT) | Qudit / Koherent Temsil |
| :--- | :--- | :--- | :--- |
| **Durum Uzayı** | $\mathbb{C}^{2^k}$ (Düz Vektör) | $\mathbb{C}^{2 \times D \times D}$ Tensör Ağı | $\mathbb{C}^d$ veya Sonsuz Faz Uzayı |
| **Semantik Korunum** | Sıfır (Hamming açmazı) | **Yüksek (D bağı ile)** | **Kusursuz (Doğal İzomorfizm)** |
| **GPU/İşlem Yükü** | Düşük ama anlamsız | Orta ($O(k \cdot D^3)$ GEMM) | Düşük-Orta ($O(d^2)$ Tensör) |
| **Yapay Bit Hiyerarşisi** | Var (Felaket) | **Yok (Dengeli Ağ)** | **Yok (Ayrık Bit Yok)** |
| **Dolanıklık Temsili** | Taklit edilemez | Matris bağları ile açık | Çok modlu faz girişimleri ile |

---

## HÜLASA

Teşhisiniz mimarinin temel direğidir:

1. **Düz ikili kodlama yasaklanmıştır:** Kelimeyi $12$ tane ikili kübitin düz indeksine ($|0110\dots\rangle$) sıkıştırıp sonra klasik benzerlik beklemek matematiksel bir tenakuzdur.
2. **Kabul edilen 1. Çözüm:** İkili kübit kullanılacaksa, her kübit rank-$k$ bir **Tensör Treninin bağımsız bir modu ($A_{j_m}$)** olacak; geometrik akrabalık sanal bağ boyutuyla ($D$) taşınacaktır.
3. **Kabul edilen 2. Çözüm:** İkili kodlama terk edilecek; kelime doğrudan $d$-boyutlu tekil bir **Qudit ($\mathbb{C}^d$)** veya faz uzayı **Koherent Durumu ($D(\vec{x})|0\rangle$)** olarak kodlanacaktır.

Böylece kelimenin geometrisi sakatlanmaz ve hesaplanan örtüşmeler hakiki semantik manayı kayıpsız yansıtır.