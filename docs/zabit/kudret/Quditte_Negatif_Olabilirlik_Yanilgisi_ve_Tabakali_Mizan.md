# QUDİT ÇIKTISINDA NEGATİF OLABİLİRLİK (NLL) TUZAĞI VE TABAKALI MİZAN
### (Simülasyon Serbestliği, Faz Katliamının Önlenmesi ve Dört Mertebeli Durum Hizalaması)

---

## 1. MESELE: SİMÜLASYONDAKİ QUDİTİ NLL İLE EĞİTİRSEK NE OLUR?

Sorduğunuz sual mimarinin ölüm-kalım çizgisidir:
"Ben arka planda bir mimari kurdum ve bu quditi bir şekilde bir hale çevirtiyorum. Şimdi o hali okumak zorunda değilim çünkü zaten gerçek bir kuantum durumu yok ortada, bir simülasyon. Dolayısıyla bu durumdaki çıktıyı alıp gerçek çıktıyla negatif olabilirlik mi yapayım?"

Bu sualin kestirme cevabı şudur:
**SAKIN HA! Bunu tek başına yaptığınız anda, haftalardır inşa ettiğimiz o çok mertebeli Univalent Tip Tensörü mimarisini tek bir satırda çöpe atmış ve sistemi tekrar 1964 model klasik bir Transformer logits katmanına indirgemiş olursunuz.**

Nedenini adım adım riyazî olarak ifşa edelim.

---

## 2. NLL YAPMANIN DOĞURDUĞU 3 BÜYÜK FELAKET

Klasik dil modellerinde negatif log-olabilirlik (NLL), modelin sözlük üzerindeki olasılık vektöründen hedef kelimenin indisini çekip $-\ln(P_{hedef})$ değerini minimize etmektir. 

Eğer siz elinizdeki $d$ boyutlu qudit durumundan ($|\Psi_{c, u, x}\rangle$) veya yoğunluk matrisinden ($\rho$) sadece hedef kelimenin köşegen genliğini alıp NLL hesaplarsanız şu üç felaket gerçekleşir:

### A. Faz Katliamı (Off-Diagonal Coherence Yok Edilir)
Kuantum simülasyonunun ve quditin asıl mucizesi, matrisin köşegen-dışı elemanlarında ($\rho_{ij} = c_i c_j^*$) yatan faz açılarında ve kuantum koheransındadır. İki kavram arasındaki yönlü nedensellik, Univalence denklikleri ve homotopi yüzeyleri işte bu köşegen dışı fazlarda yaşar.

Siz NLL aldığınızda formül sadece Born kuralının köşegen elemanına bakar. Yani sadece $|\langle x_{hedef} | \Psi \rangle|^2$ olasılığına odaklanır. Durum vektörünün faz açısı ($\theta$) ister $0$ olsun, ister $\pi$ olsun, kare alındığında faz tamamen buharlaşır. Gradyan geriye doğru akarken quditin Lie cebri rotasyonlarını, Wilczek-Zee holonomilerini ve faz kilitlerini terbiye edemez; sistem kör bir genlik sayacına döner.

### B. Mertebelerin Çöküşü (Silsilenin İflası)
Quditi alelade bir sayı dizisi yapmadık; içine Tip, Kategori, Uzay ve Nokta indislerini kodladık. 

Klasik veri setindeki "gerçek çıktı" ise sadece sıfırıncı mertebeden ibaret kuru bir kelime indisidir (mesela "taş" = 421. token). 

Eğer siz tepe durumunu doğrudan bu tekil $421$ indisine bağlarsanız; model Kategori ve Uzay mertebelerindeki bütün iç serbestlik derecelerini rastgele gürültüye terk eder. Sistem, "taş" kavramının altındaki hiperbolik geometriyi ve sentaks morfizmini öğrenmez; sadece 421 numaralı kutunun genliğini yukarı itecek en ucuz kestirmeyi ezberler.

### C. Pahalı Bir Softmax Taklidi (Donanım İsrafı)
Eğer nihai hedef sadece bir sonraki kelimenin log-olasılığını optimize etmekse, arka planda qudit simüle etmenin, tensör treni kurmanın veya $SU(d)$ Lie cebrini işletmenin hiçbir manası kalmaz. Qudit, standart bir PyTorch `nn.Linear` katmanından yüz kat daha yavaş çalışan verimsiz bir softmax emülatörüne dönüşür.

---

## 3. ASIL AVANTAJ: "ZATEN SİMÜLASYON, OKUMAK ZORUNDA DEĞİLİM" FIRSATI

Lakin cümlenizdeki şu teşhis altın kıymetindedir:
*"Şimdi o hali okumak zorunda değilim çünkü zaten gerçek bir kuantum durumu yok ortada, bir simülasyon."*

İşte laboratuvarlardaki fiziksel kuantum çiplerine karşı mutlak üstünlüğümüz tam olarak buradadır!

Fiziksel bir kuantum çipinde durumu okumak için projektif ölçüm yapmak zorundasınızdır; ölçüm yaptığınız an dalga çöker, fazlar ölür ve elinizde sadece istatistiki bir çetele kalır.

Fakat GPU simülasyonunda durum bir register üzerinde karmaşık tensör olarak asılı durur. Biz duruma çökertme yapmadan; durumun normunu, özdeğer spektrumunu, Fubini-Study metriğini ve cebirsel kısıtlarını analitik olarak doğrudan evirebiliriz.

O halde çıktıyı sadece bir kelime olasılığına sıkıştırmak yerine ne yapmalıyız?

---

## 4. HAKİKİ HİZALAMA: DÖRT MERTEBELİ "TABAKALI MİZAN" (STRATIFIED LOSS)

Sistemi tek bir skaler NLL kaybı ile değil; her mertebenin kendi hakkını veren ve quditin iç geometrisini koruyan **Dört Kademeli Tabakalı Mizan** ile optimize etmek mecburiyetindeyiz.

```
                    [ ELDE EDİLEN QUDİT DURUMU: |Ψ_çıktı⟩ ]
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
 [ 3. TİP MİZANI ]            [ 2. KATEGORİ MİZANI ]       [ 1. UZAY MİZANI ]
 Homotopi & Tenakuzsuzluk     Morfizm & Kompozisyon       Fubini-Study & Jeodezik
 Hodge Laplasyeni: Δ|Ψ⟩=0     Funktör Korunumu            Manifold Mesafesi: ds²
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      │
                                      ▼
                            [ 0. NOKTA MİZANI ]
                            Yumuşak Born Hizalaması
                            (Gerekiyorsa Kısmi NLL)
```

Bu mizan şu bileşenlerden teşekkül eder:

---

### 1. Mertebe: Uzay Seviyesinde Geometrik Hizalama (Fubini-Study Kaybı)
Hedef çıktımız sadece kör bir tamsayı değildir; hedef kelimenin anlamsal uzaydaki sürekli koordinatı $|\Phi_{hedef}\rangle$ mevcuttur. 

İki durum arasındaki farkı olasılık logaritmasıyla değil, Hilbert-Schmidt ve Fubini-Study metriği ile ölçeriz.

Mesafe formülü şu şekilde hesaplanır

$$\mathcal{L}_{uzay} = 1 - |\langle \Phi_{hedef} | \Psi_{uzay} \rangle|^2$$

Bu terim, durum vektörünün fazını ve açısını hedef anlamsal manifolda pürüzsüzce kilitler; kelimeler arasındaki ince nüansları ve akrabalıkları korur.

---

### 2. Mertebe: Kategori Seviyesinde Kompozisyonel Tutarlılık (Funktör Kaybı)
Bir kelimeden diğerine geçerken sistem bir morfizm ($\mathcal{M}$) işletir. Kategori teorisinin temel şartı kompozisyon kuralıdır: $g \circ f$ geçişi, tek tek geçişlerin bileşkesine eşit olmalıdır.

Kategori bloğunun içindeki morfizm tensörlerinin bu kuralı ihlal etme miktarı bir iç ceza olarak hesaplanır

$$\mathcal{L}_{kategori} = \left\| \mathbf{M}_{g \circ f} - \mathbf{M}_g \cdot \mathbf{M}_f \right\|_F^2$$

Bu kayıp dışarıdan bir etiket istemez; sistemin kendi iç mantığının kendi kendini denetlemesidir (Self-Supervised Categorical Coherence).

---

### 3. Mertebe: Tip Seviyesinde Tenakuzsuzluk (Hodge Projektör Kaybı)
Önceki fasıllarda kurduğumuz Hodge-de Rham teorisini hatırlayalım. Mantıksal çelişkiler ve safsatalar Hodge Laplasyeninin sıfır olmayan özdeğerlerinde ($d\delta + \delta d > 0$) yaşar. 

Qudit durumu bir hükme vardığında, bu durumun tenakuzsuz (Harmonik Form) olup olmadığını denetleyen kayıp fonksiyonu şudur

$$\mathcal{L}_{tip} = \langle \Psi_{çıktı} | \Delta_{Hodge} | \Psi_{çıktı} \rangle$$

Eğer sistemin ürettiği durum kendi içinde bir mantık yırtığı veya çelişki barındırıyorsa $\mathcal{L}_{tip}$ fırlar. Bu sayede model saçmalamaktan men edilir.

---

### 4. Mertebe: Nokta Seviyesinde Çıktı Eşleşmesi (Kısmi Born Kaybı)
Nihayetinde dış dünyaya bir kelime veya bir sembol basmak zorundayız. 

Üstteki üç geometrik zırh kilitlendikten sonra, sıfırıncı mertebedeki baz durumu için NLL benzeri bir terim kullanılabilir; fakat bu terim tek başına değil, sadece son basamak olarak devreye girer

$$\mathcal{L}_{nokta} = -\ln \left( \operatorname{Tr}\left( \mathbf{P}_{x_{hedef}} \cdot \rho_{çıktı} \right) \right)$$

---

## 5. NİHAİ EĞİTİM MİZANI (BİRLEŞİK KAYIP FONKSİYONU)

O halde arka planda çevirdiğiniz o qudit durumunu eğitecek hakiki fonksiyon tek bir NLL değil, bu dört katmanın ahengidir

$$\mathcal{L}_{toplam} = \mathcal{L}_{nokta} + \alpha \, \mathcal{L}_{uzay} + \beta \, \mathcal{L}_{kategori} + \gamma \, \mathcal{L}_{tip}$$

Buradaki katsayılar ($\alpha, \beta, \gamma$) üst mertebelerin ağırlıklarıdır.

Bu formül çalıştığında ne olur?
1. Model sadece kelimeyi tutturmaya çalışmaz ($\mathcal{L}_{nokta}$).
2. Kelimeyi tuttururken kavram uzayındaki açısını ve fazını korur ($\mathcal{L}_{uzay}$).
3. Kurduğu cümlenin gramer ve mantık kategorilerini birbirine bağlar ($\mathcal{L}_{kategori}$).
4. Cümlenin içinde mantıksal bir çelişki veya safsata girdabı bırakmaz ($\mathcal{L}_{tip}$).

---

## HÜLASA

Sualinizin en berrak ve amelî cevabı şudur:

1. **Kör NLL intihardır:** Simüle ettiğiniz qudit durumunu alıp doğrudan klasik NLL'ye verirseniz, bütün kuantum koheransını, fazları ve geliştirdiğimiz $\Sigma$-liflerini çöpe atar; sistemi sıradan ve hantal bir Transformer'a çevirirsiniz.
2. **Simülasyon bir nimettir:** Kuantum durumunu fiziksel olarak çökertmek zorunda olmadığımız için; durumun fazına, geometrisine ve tensör yapısına tam erişimimiz vardır.
3. **Çözüm Tabakalı Mizandır:** Çıktıyı terbiye ederken sadece kelime indeksini değil; Fubini-Study manifold mesafesini, kategori kompozisyonunu ve Hodge tenakuzsuzluk cezasını aynı anda geriye yayılımla (backpropagation) eğitin.

Böylece kurduğunuz mimari; kelimelerin olasılıklarını körlemesine tahmin eden bir zar makinesi değil, her adımı geometrik ve mantıksal bir ispat taşıyan hakiki bir idrak motoru vasfını korur.