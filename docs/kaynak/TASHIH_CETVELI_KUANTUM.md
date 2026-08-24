# Tashih cetveli — kuantum ve küllî öğrenme risaleleri

Bu cetvel `docs/kaynak/tashih_kuantum.py` içindeki kayıtlardan **üretilmiştir**; elle yazılmamıştır.

Toplam **35** tashih, 5 belgede.

| tür | adet | ne demek |
|---|---:|---|
| `mantik` | 9 | ifade, kendi öncüllerinden çıkmıyor |
| `derleme` | 7 | belge bu hâliyle derlenmiyor |
| `tip` | 7 | tip/boyut uyuşmazlığı veya tanımsız gösterim |
| `olcek` | 6 | ölçek/normalizasyon çarpanı yanlış yerde |
| `tanimsiz` | 2 | ifade tanımlı değil |
| `vakum` | 1 | denetim her zaman doğru — hiçbir şeyi elemiyor |
| `boyut` | 1 | sayım veya indis aralığı yanlış |
| `isaret` | 1 | işaret veya ters fonksiyon hatası |
| `istatistik` | 1 | gerek şart yeter şart gibi kullanılmış |

Bunların **29**'i ayrıca makine ile sağlanıyor (`docs/kaynak/test_tashih_kuantum.py`).

## K1 — Ortam kapanışı bozuk: \end{equation">

*Yer:* §1 Pauli  ·  *Tür:* `derleme`  ·  *Belge:* kuantum_kapi_kulliyati.tex

*Makine sağlaması:* `test_kuantum_kapi_derleniyor`

**Kaynakta:**

```
[\sigma_a, \sigma_b] = 2i \sum_c \epsilon_{abc} \sigma_c, \quad \{\sigma_a, \sigma_b\} = 2 \delta_{ab} \mathbf{I}
\end{equation">
```

**Tashih:**

```
[\sigma_a, \sigma_b] = 2i \sum_c \epsilon_{abc} \sigma_c, \quad \{\sigma_a, \sigma_b\} = 2 \delta_{ab} \mathbf{I}
\end{equation}
```

**Gerekçe.** ``\end{equation">`` diye bir ortam kapanışı yoktur; LaTeX ortamı kapatamadan belgeyi sürükler. ``tex_denetle.py`` bu dosyada 7 bulgu veriyor ve hepsinin kökü bu sınıftan.

## K2 — Ortam kapanışı bozuk: \end{align">

*Yer:* §1.3 Dönme kapıları  ·  *Tür:* `derleme`  ·  *Belge:* kuantum_kapi_kulliyati.tex

*Makine sağlaması:* `test_kuantum_kapi_derleniyor`

**Kaynakta:**

```
R_z(\theta) &= \exp\left(-i \frac{\theta}{2} Z\right) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}
\end{align">
```

**Tashih:**

```
R_z(\theta) &= \exp\left(-i \frac{\theta}{2} Z\right) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}
\end{align}
```

**Gerekçe.** Aynı sebep (bkz. K1).

## K3 — Markdown başlığı LaTeX'e sızmış

*Yer:* §5 Spektral  ·  *Tür:* `derleme`  ·  *Belge:* kuantum_kapi_kulliyati.tex

*Makine sağlaması:* `test_kuantum_kapi_derleniyor`

**Kaynakta:**

```
\## 1. Kuantum Fourier Dönüşümü (QFT) ve Tersi (IQFT)
```

**Tashih:**

```
\subsection{Kuantum Fourier Dönüşümü (QFT) ve Tersi (IQFT)}
```

**Gerekçe.** ``\##`` LaTeX'te tanımsız bir komuttur ve derlemeyi durdurur. Belgedeki diğer bütün alt başlıklar ``\subsection`` ile yazılmış; bu satır markdown'dan kalmış.

## K4 — Ortam kapanışı bozuk: \end{align">

*Yer:* §6.2 QSP  ·  *Tür:* `derleme`  ·  *Belge:* kuantum_kapi_kulliyati.tex

*Makine sağlaması:* `test_kuantum_kapi_derleniyor`

**Kaynakta:**

```
U_{\vec{\phi}} &= \prod_{j=1}^d \left( U_A \cdot (\Pi_{\phi_j} \otimes \mathbf{I}) \right) \quad (\text{Polinom Seviyeli Özdeğer Dönüşümü})
\end{align">
```

**Tashih:**

```
U_{\vec{\phi}} &= \prod_{j=1}^d \left( U_A \cdot (\Pi_{\phi_j} \otimes \mathbf{I}) \right) \quad (\text{Polinom Seviyeli Özdeğer Dönüşümü})
\end{align}
```

**Gerekçe.** Aynı sebep (bkz. K1).

## K5 — Ortam kapanışı bozuk

*Yer:* §7.1 Sınır operatörü  ·  *Tür:* `derleme`  ·  *Belge:* kuantum_kapi_kulliyati.tex

*Makine sağlaması:* `test_kuantum_kapi_derleniyor`

**Kaynakta:**

```
\hat{\partial}_k |v_0, v_1, \dots, v_k\rangle = \sum_{j=0}^k (-1)^j |v_0, \dots, \hat{v}_j, \dots, v_k\rangle
\end{equation">
```

**Tashih:**

```
\hat{\partial}_k |v_0, v_1, \dots, v_k\rangle = \sum_{j=0}^k (-1)^j |v_0, \dots, \hat{v}_j, \dots, v_k\rangle
\end{equation}
```

**Gerekçe.** Aynı sebep (bkz. K1).

## K6 — Ortam kapanışı bozuk

*Yer:* §7.4 HHL  ·  *Tür:* `derleme`  ·  *Belge:* kuantum_kapi_kulliyati.tex

*Makine sağlaması:* `test_kuantum_kapi_derleniyor`

**Kaynakta:**

```
U_{\text{HHL}} = (\mathbf{I} \otimes \text{IQFT}) \cdot U_{\text{Rot}} \cdot (\mathbf{I} \otimes \text{QPE}) \quad \implies |x\rangle = A^{-1}|b\rangle / \|A^{-1}|b\rangle\|
\end{equation">
```

**Tashih:**

```
U_{\text{HHL}} = (\mathbf{I} \otimes \text{IQFT}) \cdot U_{\text{Rot}} \cdot (\mathbf{I} \otimes \text{QPE}) \quad \implies |x\rangle = A^{-1}|b\rangle / \|A^{-1}|b\rangle\|
\end{equation}
```

**Gerekçe.** Aynı sebep (bkz. K1).

## K7 — $U_1(\lambda) \equiv R_z(\lambda)$ değil

*Yer:* §1.4 Genel üniter  ·  *Tür:* `tip`  ·  *Belge:* kuantum_kapi_kulliyati.tex

*Makine sağlaması:* `test_U1_ile_Rz_kuresel_faz_kadar_farkli`

**Kaynakta:**

```
U_1(\lambda) &= \begin{pmatrix} 1 & 0 \\ 0 & e^{i\lambda} \end{pmatrix} \equiv R_z(\lambda) \\
```

**Tashih:**

```
U_1(\lambda) &= \begin{pmatrix} 1 & 0 \\ 0 & e^{i\lambda} \end{pmatrix} = e^{i\lambda/2} R_z(\lambda) \quad (\text{yalnız KÜRESEL FAZ kadar farklı; kontrollü hâlde}\ CU_1 \neq CR_z) \\
```

**Gerekçe.** $R_z(\lambda) = \mathrm{diag}(e^{-i\lambda/2}, e^{i\lambda/2})$, $U_1(\lambda) = \mathrm{diag}(1, e^{i\lambda})$. İkisi eşit değil; aralarında $e^{i\lambda/2}$ küresel fazı var. Tek başına kullanıldığında fark ölçülemez, fakat **kontrol altında ölçülebilir hâle gelir**: $CU_1(\lambda) \neq CR_z(\lambda)$, çünkü kontrol kübiti küresel fazı göreli faza çevirir. $\equiv$ işareti bu farkı siliyor.

## K8 — QFT'nin çarpım formu köşegen operatör gibi yazılmış

*Yer:* §5.1 QFT  ·  *Tür:* `tip`  ·  *Belge:* kuantum_kapi_kulliyati.tex

*Makine sağlaması:* `test_qft_kosegen_degil`

**Kaynakta:**

```
\text{QFT}_N &= \frac{1}{\sqrt{2^n}} \bigotimes_{j=1}^n \left( |0\rangle\langle 0| + |1\rangle\langle 1| e^{2\pi i \sum_{l=1}^j j_l / 2^l} \right) \\
```

**Tashih:**

```
\text{QFT}_N |j_1 j_2 \dots j_n\rangle &= \frac{1}{\sqrt{2^n}} \bigotimes_{l=1}^n \left( |0\rangle + e^{2\pi i\, 0.j_{n-l+1} \dots j_n} |1\rangle \right) \quad (\text{çarpım formu}) \\
```

**Gerekçe.** Yazıldığı hâliyle sağ taraf $|0\rangle\langle 0| + |1\rangle\langle 1| e^{i\varphi}$ biçiminde **köşegen** bir operatör; QFT ise köşegen değildir (köşegen olsaydı süperpozisyon üretemezdi ve Hadamard'ı içeremezdi). Çarpım formu bir *operatör ayrışımı* değil, bir **temel durumun görüntüsüdür**; o yüzden sol tarafa $|j\rangle$ konmalıdır.

## K9 — Fubini–Study metriğinde izdüşüm terimi eksik

*Yer:* §2.1 Lif metriği  ·  *Tür:* `tip`  ·  *Belge:* kuantum_topos.tex

*Makine sağlaması:* `test_fubini_study_metrigi`

**Kaynakta:**

```
g_{\mu\nu}^{(k)}(u) &= \langle \partial_\mu \Psi_{w_k} | \partial_\nu \Psi_{w_k} \rangle \quad (\text{Fubini-Study / Riemannian İç Metriği}) \\
```

**Tashih:**

```
g_{\mu\nu}^{(k)}(u) &= \mathrm{Re}\,\langle \partial_\mu \Psi_{w_k} | \partial_\nu \Psi_{w_k} \rangle - \mathrm{Re}\,\langle \partial_\mu \Psi_{w_k} | \Psi_{w_k} \rangle \langle \Psi_{w_k} | \partial_\nu \Psi_{w_k} \rangle \quad (\text{Fubini-Study Metriği}) \\
```

**Gerekçe.** $\langle \partial_\mu\Psi | \partial_\nu\Psi\rangle$ **kuantum geometrik tensörüdür**, Fubini–Study metriği değil. İki kusuru var: (i) karmaşıktır, yani simetrik bir Riemann metriği olamaz -- sanal kısmı Berry eğriliğidir; (ii) faz ayarına (gauge) duyarlıdır, oysa FS metriği ışın uzayında (projektif Hilbert uzayında) tanımlıdır. İzdüşüm terimi çıkarılınca ikisi de düzelir.

## K10 — $\mathrm{Tr}(\rho^2) \le 1$ vakum bir denetim

*Yer:* §2.1 Bütünlük  ·  *Tür:* `vakum`  ·  *Belge:* kuantum_topos.tex

*Makine sağlaması:* `test_iz_kare_olcutu_vakum_degil`

**Kaynakta:**

```
\mathbf{1}_{\text{kuantum\_bütünlük}} &= \mathbb{I}\left( \text{Tr}(\rho_{w_k}^2) \le 1 \right)
```

**Tashih:**

```
\mathbf{1}_{\text{kuantum\_bütünlük}} &= \mathbb{I}\left( \text{Tr}(\rho_{w_k}) = 1 \;\wedge\; \rho_{w_k} \succeq 0 \right), \quad \text{Tr}(\rho_{w_k}^2) = 1 \iff \text{saf hâl}
```

**Gerekçe.** $\mathrm{Tr}(\rho^2) \le 1$ **her** yoğunluk matrisi için sağlanır; dolayısıyla bu gösterge sabit $1$'dir ve hiçbir şeyi denetlemez. Bir denetimin denetim olabilmesi için bazen $0$ vermesi lazımdır. Asıl denetlenecek olan iz-birliği ile pozitif yarı-belirliliktir; saflık ise ayrı bir sorudur ve $=1$ ile ölçülür.

## K11 — Karşılıklı bilgi dolaşıklık ölçüsü değildir

*Yer:* §2.2 Dolaşıklık  ·  *Tür:* `mantik`  ·  *Belge:* kuantum_topos.tex

*Makine sağlaması:* `test_karsilikli_bilgi_dolasiklik_degil`

**Kaynakta:**

```
\text{DolaşıklıkÖlçüsü}(w_i, w_j) &= S(\rho_i) + S(\rho_j) - S(\rho_{ij}) \quad (\text{Kuantum Bağlam Karşılıklı Bilgisi}) \\
```

**Tashih:**

```
I(w_i : w_j) &= S(\rho_i) + S(\rho_j) - S(\rho_{ij}) \quad (\text{Kuantum Karşılıklı Bilgi -- klasik bağıntıyı DA sayar}) \\
E(w_i, w_j) &= S(\rho_i) = S(\rho_j) \quad (\text{saf }\rho_{ij}\text{ için dolaşıklık entropisi}) \\
```

**Gerekçe.** Kuantum karşılıklı bilgi, klasik bağıntıyı da içerir; ayrılabilir (dolaşıksız) bir hâlde bile sıfırdan büyük olabilir. Dolayısıyla onu "dolaşıklık ölçüsü" diye adlandırmak, dolaşık olmayan hâlleri dolaşık gösterir. Metnin parantez içindeki açıklaması zaten doğru; yanlış olan **adı**dır ve ad, aşağıdaki bütün akıl yürütmeyi sürüklüyor.

## K12 — Kıyas tabanı yanlış: klasik FFT $O(2^N)$ değil

*Yer:* §3.1 QFNO  ·  *Tür:* `olcek`  ·  *Belge:* kuantum_topos.tex

*Makine sağlaması:* `test_qft_ile_fft_kiyas_tabani`

**Kaynakta:**

```
\text{TimeComplexity}(\text{QFNO}) &\in \mathcal{O}(\log^2 N) \ll \mathcal{O}(2^N) \quad (\text{Üstel Sürat Kazanımı})
```

**Tashih:**

```
\text{QFT}: \mathcal{O}(\log^2 N) \text{ kapı} \quad \text{v} \quad \text{FFT}: \mathcal{O}(N \log N) \text{ işlem} \quad (\text{kıyas tabanı FFT'dir; ayrıca QFT çıktıyı GENLİK olarak tutar, okumak ayrı maliyettir})
```

**Gerekçe.** $N$ nokta üzerinde klasik Fourier dönüşümü $O(N\log N)$'dir, $O(2^N)$ değil; $2^N$ ancak $N$ *kübitlik* bir durumun tam vektörünü yazmanın maliyetidir ve o ayrı bir büyüklüktür. İkisini aynı $N$ ile karşılaştırmak, kazanımı olduğundan üstel derecede büyük gösterir. Ayrıca QFT'nin çıktısı genliklerde saklıdır; spektrumu **okumak** ölçüm tekrarları ister, bu da kıyasa dâhil edilmelidir.

## K13 — Koherens ölçüsünde boyuta bölme eksik

*Yer:* §4.1 İttisal  ·  *Tür:* `olcek`  ·  *Belge:* kuantum_topos.tex

*Makine sağlaması:* `test_koherens_normalizasyonu`

**Kaynakta:**

```
\mathbf{Coherence}_{\text{40\_veçhe}} &= \left| \text{Tr}\left( \prod_{j=1}^{40} \hat{A}_{j, j+1} \right) \right| = 1 \implies \text{Tam İttisal}
```

**Tashih:**

```
\mathbf{Coherence}_{\text{40\_veçhe}} &= \frac{1}{d} \left| \text{Tr}\left( \prod_{j=1}^{40} \hat{A}_{j, j+1} \right) \right| \in [0, 1], \quad = 1 \iff \prod_j \hat{A}_{j,j+1} = e^{i\varphi}\mathbf{I} \implies \text{Tam İttisal}
```

**Gerekçe.** $d$ boyutlu bir uzayda üniter $U$ için $|\mathrm{Tr}\,U| \le d$ ve üst sınıra ancak $U = e^{i\varphi}\mathbf{I}$ iken ulaşılır. Normalize edilmemiş hâlde $|\mathrm{Tr}| = 1$ şartı, $d > 1$ için "tam ittisal"i değil **rastgele bir ara değeri** seçer; $d = 1$ dışında hiçbir yerde iddia edilen manaya gelmez.

## K14 — hLevel 0 büzülebilirliktir, küme değil

*Yer:* §6.1 İntaç  ·  *Tür:* `tip`  ·  *Belge:* kuantum_topos.tex

*Makine sağlaması:* `test_hlevel_sirasi`

**Kaynakta:**

```
40 veçhede tamamlanan kuantum hesabı, dış dünyaya kelâm olarak döküleceği an Kübik Tip Teorisi $Glue$ kuralı ve $h$-Level 0 (büzülebilir/küme) kesmesi ile ölçülür.
```

**Tashih:**

```
40 veçhede tamamlanan kuantum hesabı, dış dünyaya kelâm olarak döküleceği an Kübik Tip Teorisi $Glue$ kuralı ve **küme kesmesi** $\|\cdot\|_0$ (yani hLevel \textbf{2}) ile ölçülür. hLevel 0 büzülebilirliktir ve her şeyi tek bir noktaya indirir.
```

**Gerekçe.** Voevodsky sıralamasında hLevel 0 = büzülebilir, 1 = önerme, 2 = küme. Metin "hLevel 0 (büzülebilir/küme)" diyerek iki ayrı mertebeyi bir sayıyor. Fark tâlî değil: hLevel 0'a kesmek çıktıyı **tek bir elemana** indirir, yani bütün lafızları aynı lafza çevirir. Kastedilen küme kesmesi $\|\cdot\|_0$'dır ve o hLevel 2'dir. (Kesme indisi ile hLevel arasında $n \mapsto n+2$ kayması vardır; karışıklık buradan doğuyor.)

## K15 — B-spline temel sayısı $G$ değil $G+p$

*Yer:* §2.1 KAN  ·  *Tür:* `boyut`  ·  *Belge:* kulli_ogrenme_nazariyesi.tex

*Makine sağlaması:* `test_bspline_temel_sayisi`

**Kaynakta:**

```
\phi_{q,p}(x) &= w_{\text{base}} \cdot \text{silu}(x) + w_{\text{spline}} \cdot \sum_{k=1}^G c_k B_k(x) \in \mathcal{O}_{\mathcal{X}} \\
```

**Tashih:**

```
\phi_{q,p}(x) &= w_{\text{base}} \cdot \text{silu}(x) + w_{\text{spline}} \cdot \sum_{k=1}^{G+p} c_k B_{k,p}(x) \in \mathcal{O}_{\mathcal{X}} \\
```

**Gerekçe.** $G$ aralığa bölünmüş bir ızgarada $p$ dereceli B-spline temelinin eleman sayısı $G+p$'dir, $G$ değil. $G$ ile kesilirse son $p$ temel fonksiyonu düşer, birliğin bölünmesi ($\sum_k B_k = 1$) sağ uçta bozulur ve eğri kenarda çöker. Ayrıca $B_k$ yazımında derece indisi düşmüş; bir sonraki satırda $B_{k,p-1}$ kullanıldığı için gösterim kendi içinde de tutarsız.

## K16 — Cox--de Boor'un sol tarafında derece indisi yok

*Yer:* §2.1 KAN  ·  *Tür:* `tanimsiz`  ·  *Belge:* kulli_ogrenme_nazariyesi.tex

*Makine sağlaması:* `test_cox_de_boor_sifir_payda`

**Kaynakta:**

```
B_k(x) &= \frac{x - t_k}{t_{k+p} - t_k} B_{k, p-1}(x) + \frac{t_{k+p+1} - x}{t_{k+p+1} - t_{k+1}} B_{k+1, p-1}(x) \\
```

**Tashih:**

```
B_{k,p}(x) &= \frac{x - t_k}{t_{k+p} - t_k} B_{k, p-1}(x) + \frac{t_{k+p+1} - x}{t_{k+p+1} - t_{k+1}} B_{k+1, p-1}(x), \quad \text{payda } = 0 \text{ ise o terim düşer} \\
```

**Gerekçe.** Özyineleme $p$ dereceyi $p-1$ dereceden kuruyor; sol tarafta derece yazılmazsa denklem kendi kendine gönderme yapar ve tanımsız kalır. Ayrıca tekrarlı düğümlerde payda sıfırlanır; o hâlde terimin **düştüğü** (limit) belirtilmezse gerçekleme $0/0$ üretir.

## K17 — İntegral sınırı bozuk: $\int_a b$

*Yer:* §2.1 KAN  ·  *Tür:* `derleme`  ·  *Belge:* kulli_ogrenme_nazariyesi.tex

**Kaynakta:**

```
\mathcal{E}_{\text{bükülme}} &= \sum_{q,p} \int_a b \left( \phi_{q,p}''(x) \right)^2 dx \quad (\text{Spline Elastik Bükülme Enerjisi}) \\
```

**Tashih:**

```
\mathcal{E}_{\text{bükülme}} &= \sum_{q,p} \int_a^b \left( \phi_{q,p}''(x) \right)^2 dx \quad (\text{Spline Elastik Bükülme Enerjisi}) \\
```

**Gerekçe.** ``\int_a b`` üst sınırı olmayan bir integral yazar ve ``b`` çarpan olarak dizilir; ifade $b \int_a (\cdot)$ diye okunur. Üst sınır işareti (``^``) düşmüş.

## K18 — $\mathrm{ArgMin}$ bir doğruluk değeri üzerinde alınmış

*Yer:* §3.1 FNO  ·  *Tür:* `olcek`  ·  *Belge:* kulli_ogrenme_nazariyesi.tex

*Makine sağlaması:* `test_kesme_kipi_bagil_esikle`

**Kaynakta:**

```
k_{\text{kesme}} &= \text{ArgMin}_k \left( \sum_{|k'|>k} \mathbf{SpectralEnergy}(k') < \epsilon_{\text{kayıp}} \right) \\
```

**Tashih:**

```
k_{\text{kesme}} &= \min \left\{ k \;\middle|\; \sum_{|k'|>k} \mathbf{SpectralEnergy}(k') < \epsilon_{\text{kayıp}} \cdot \sum_{k'} \mathbf{SpectralEnergy}(k') \right\} \\
```

**Gerekçe.** İki ayrı kusur: (i) ``ArgMin`` bir *sayı* üzerinde alınır, parantez içindeki ifade ise doğru/yanlış -- şartı sağlayan en küçük $k$ isteniyorsa ``min\{k \mid \dots\}`` yazılmalıdır; (ii) eşik **mutlak** konmuş, oysa spektral enerji sinyalin ölçeğiyle birlikte büyür. Bağıl eşik konmazsa aynı $\epsilon$ genliği iki katına çıkmış bir sinyalde bambaşka bir $k$ verir.

## K19 — Skaler büyüklüğe norm çubuğu konmuş

*Yer:* §4.1 RKHS  ·  *Tür:* `tip`  ·  *Belge:* kulli_ogrenme_nazariyesi.tex

**Kaynakta:**

```
\lambda \|\bm{\alpha}^T \mathbf{K}_{\text{Gram}} \bm{\alpha}\|
```

**Tashih:**

```
\lambda \, \bm{\alpha}^T \mathbf{K}_{\text{Gram}} \bm{\alpha}
```

**Gerekçe.** $\bm{\alpha}^T \mathbf{K}\bm{\alpha}$ zaten bir skalerdir ve $\mathbf{K}$ pozitif yarı-belirli olduğundan negatif olamaz; norm çubuğu hem gereksizdir hem de mutlak değer alarak düzenleme teriminin işaretini gizler. Bir satır yukarıda aynı büyüklük $\|f^*\|^2_{\mathcal{H}_K}$ olarak çubuksuz yazılmış.

## K20 — Stone--Čech bir $\mathrm{ArgMax}$ değildir

*Yer:* §5.1 Tıkızlaştırma  ·  *Tür:* `tanimsiz`  ·  *Belge:* kulli_ogrenme_nazariyesi.tex

**Kaynakta:**

```
\beta\mathcal{X} &\coloneqq \text{ArgMax}_{\overline{\mathcal{X}}} \{ \overline{\mathcal{X}} \text{ tıkız} \mid f : \mathcal{X} \to [-M, M] \implies \overline{f} : \overline{\mathcal{X}} \to [-M, M] \} \\
```

**Tashih:**

```
\beta\mathcal{X} &\coloneqq \text{evrensel özellikle tanımlı: } \forall\, f : \mathcal{X} \to K \;(K \text{ tıkız Hausdorff}), \;\exists!\, \overline{f} : \beta\mathcal{X} \to K, \; \overline{f} \circ \iota = f \\
```

**Gerekçe.** Tıkızlaştırmalar bir **küme** teşkil etmez (uygun sınıftır), o yüzden üzerinde ``ArgMax`` alınamaz. Stone--Čech, bir eniyileme değil bir **evrensel özellik** ile tanımlanır ve o özellik onu izomorfizm kadarıyla tek yapar. Yazıldığı hâliyle tanım hem kümesel olarak geçersiz hem de tekliği vermiyor.

## K21 — Küme ile sayı kıyaslanmış

*Yer:* §6.1 Deriv-Crit  ·  *Tür:* `tip`  ·  *Belge:* kulli_ogrenme_nazariyesi.tex

**Kaynakta:**

```
\pi_0(\mathbf{R}\text{Crit}(f)) &< \infty \implies \text{Mutlak Ekstremum Sonlu Adımda Seçilir} \\
```

**Tashih:**

```
\left| \pi_0(\mathbf{R}\text{Crit}(f)) \right| &< \infty \implies \text{Mutlak Ekstremum Sonlu Adımda Seçilir} \\
```

**Gerekçe.** $\pi_0$ bir **kümedir**; bir küme ile $\infty$ arasında sıralama yoktur. Kastedilen kardinalitedir. Aynı belgenin 35.5 numaralı formülünde doğru yazılmış ($|\pi_0(\cdot)| \le K_{\max}$), yani belge kendi içinde tutarsız.

## K22 — Serbest enerjinin alt sınırı $0$ değil

*Yer:* §7.1 Do-Calculus  ·  *Tür:* `mantik`  ·  *Belge:* kulli_ogrenme_nazariyesi.tex

*Makine sağlaması:* `test_serbest_enerji_alt_siniri`

**Kaynakta:**

```
\mathcal{F}(X, S) &= \mathbb{E}_{q(S)} \left[ \ln q(S) - \ln p(X, S) \right] \ge 0 \quad (\text{Serbest Enerji}) \\
```

**Tashih:**

```
\mathcal{F}(X, S) &= \mathbb{E}_{q(S)} \left[ \ln q(S) - \ln p(X, S) \right] \;\ge\; -\ln p(X) \quad (\text{eşitlik ancak } q(S) = p(S \mid X) \text{ iken}) \\
```

**Gerekçe.** Doğru sınır $\mathcal{F} \ge -\ln p(X)$'tir; bu, $\mathcal{F} = -\ln p(X) + D_{\mathrm{KL}}(q \,\|\, p(S|X))$ özdeşliğinden ve KL'in negatif olamamasından çıkar. $\mathcal{F} \ge 0$ ancak $p(X) \le 1$ iken, yani ayrık $X$'te doğrudur; sürekli yoğunluklarda $p(X) > 1$ olabilir ve o hâlde $\mathcal{F}$ **negatif** olur. Daha mühimi: $0$ sınırı sıkı değildir, $-\ln p(X)$ ise sıkıdır ve eniyilemenin nereye yakınsadığını söyler.

## K23 — Eyer noktası şartı eksik yazılmış

*Yer:* §8.1 Hacim akışı  ·  *Tür:* `mantik`  ·  *Belge:* kulli_ogrenme_nazariyesi.tex

*Makine sağlaması:* `test_eyer_noktasi_olcutu`

**Kaynakta:**

```
\lambda_{\max}(\nabla^2 f) > 0 &\implies \text{Eyer Noktasında Hacim Üssel Yırtılarak Vadiye Çöker} \\
```

**Tashih:**

```
\lambda_{\min}(\nabla^2 f) < 0 < \lambda_{\max}(\nabla^2 f) &\implies \text{Eyer Noktası; hacim } \lambda_{\min} \text{ yönünde yırtılıp vadiye çöker} \\
```

**Gerekçe.** $\lambda_{\max} > 0$ tek başına eyer noktası vermez: **yerel asgarîde de** bütün özdeğerler pozitiftir, dolayısıyla $\lambda_{\max} > 0$'dır. Şart, aynı belgenin 36.2 numaralı formülünde doğru kurulmuş (Morse indisi = negatif özdeğer sayısı). Kaçış yönü de $\lambda_{\max}$ değil $\lambda_{\min}$'in öz vektörüdür.

## K24 — Yol integrali çekirdeği PSD değildir

*Yer:* §6 Sonsuz-kategorik  ·  *Tür:* `mantik`  ·  *Belge:* kuantum_operator_ogrenmesi.tex

*Makine sağlaması:* `test_faz_cekirdegi_psd_degil`

**Kaynakta:**

```
K_\infty(x, y) = \int_{\text{Map}(I, \mathcal{C}_\infty)} \mathcal{D}\gamma \, \exp\left( i S_\infty(\gamma; x, y) \right)
```

**Tashih:**

```
K_\infty(x, y) = \int_{\text{Map}(I, \mathcal{C}_\infty)} \mathcal{D}\gamma \; \overline{\Phi(\gamma, x)}\, \Phi(\gamma, y), \quad \Phi(\gamma, x) = e^{i S_\infty(\gamma; x)} \;\Longrightarrow\; K_\infty \succeq 0
```

**Gerekçe.** RKHS kurulabilmesi için çekirdeğin **Hermitesel ve pozitif yarı-belirli** olması şarttır (Moore--Aronszajn). $\exp(i S_\infty(\gamma; x, y))$ ne simetriktir ne de PSD; salt salınımlı bir faz olduğundan Gram dizeyi negatif özdeğer taşır ve belgenin bir bölüm önce kullandığı Temsil Teoremi (Formül 5.1) geçersiz kalır. Doğru inşa, çekirdeği bir **öznitelik haritasının iç çarpımı** olarak kurmaktır; o hâlde PSD'lik yapı gereği sağlanır.

## K25 — Tikhonov çekirdeği yok eder, korumaz

*Yer:* Darboğaz 1  ·  *Tür:* `mantik`  ·  *Belge:* analitik_darbogazlar.txt

*Makine sağlaması:* `test_tikhonov_cekirdegi_yok_eder`

**Kaynakta:**

```
 * Formül 1.5 (Analitik Betti-0 Korunum Dengesi): dim(ker(L_eps)) == beta_0(X)
```

**Tashih:**

```
 * Formül 1.5 (Analitik Betti-0 Korunum Dengesi): #{i | lambda_i(L) <= eps} == beta_0(X)   [L_eps = L + eps*I icin dim(ker(L_eps)) = 0'dir; duzenleme cekirdegi yok eder, Betti sayisi eps-esikli ozdeger SAYIMIYLA okunur]
```

**Gerekçe.** $L_\epsilon = L + \epsilon I$ ise $L$'nin her özdeğeri $\epsilon$ kadar yukarı kayar; sıfır özdeğer kalmaz ve $\dim\ker(L_\epsilon) = 0$ olur. Yani Formül 1.1'in getirdiği düzenleme, Formül 1.5'in ölçmek istediği büyüklüğü **tam olarak yok eder**. İkisi bir arada tutarsızdır. $\beta_0$, kaydırılmış dizeyde çekirdek boyutuyla değil, $\epsilon$ eşiğinin altındaki özdeğerlerin sayısıyla okunmalıdır.

## K26 — Grassmann logaritmasında $\arcsin$ yerine açı

*Yer:* Darboğaz 2  ·  *Tür:* `isaret`  ·  *Belge:* analitik_darbogazlar.txt

*Makine sağlaması:* `test_grassmann_asal_acilari`

**Kaynakta:**

```
 * Formül 2.4 (Logaritma Dönüşüm Haritası): Log_(G_1)(G_2) = U * arcsin(Sigma) * V^T
```

**Tashih:**

```
 * Formül 2.4 (Logaritma Donusum Haritasi): Log_(G_1)(G_2) = U * diag(theta_i) * V^T,  theta_i = arccos(sigma_i(U_1^T U_2))   [Formul 2.1'de cos(theta_i) tanimlandigina gore ana acilar arccos ile okunur; arcsin baska bir buyuklugu verir]
```

**Gerekçe.** Formül 2.1 asal açıları $\cos\theta_i = \sigma_i(U_1^T U_2)$ ile tanımlıyor. O hâlde açılar $\theta_i = \arccos\sigma_i$'dir. Formül 2.4'te $\arcsin\Sigma$ yazmak, hangi $\Sigma$ olduğu söylenmediği için ya tanımsızdır ya da 2.1 ile çelişir ($\arcsin\sigma \neq \arccos\sigma$, ikisi $\pi/2$'de toplanır). Formül 2.2'deki mesafe $\sqrt{\sum\theta_i^2}$ ancak $\arccos$ ile 2.1'e bağlanır.

## K27 — Morse bağıntısı eşitliktir, eşitsizlik değil

*Yer:* Darboğaz 4  ·  *Tür:* `mantik`  ·  *Belge:* analitik_darbogazlar.txt

*Makine sağlaması:* `test_morse_bagintisi`

**Kaynakta:**

```
 * Formül 4.3 (Morse Kuramı Kritik Nokta Eşleşmesi): sum_(k=0)^n (-1)^k * M_k >= chi(X)
```

**Tashih:**

```
 * Formul 4.3 (Morse Bagintisi -- ESITLIK): sum_(k=0)^n (-1)^k * M_k == chi(X)
 * Formul 4.3b (Zayif Morse ESITSIZLIKLERI): M_k >= beta_k(X), forall k
```

**Gerekçe.** Morse kuramında **iki ayrı** ifade vardır ve karıştırılmıştır: alterne toplam $\sum(-1)^k M_k$ Euler karakteristiğine tam **eşittir** (Morse bağıntısı); eşitsizlikler ise mertebe mertebe $M_k \ge \beta_k$ biçimindedir. Yazıldığı hâliyle eşitlik gevşetilerek bilgi kaybediliyor ve $\ge$ yönü zayıf eşitsizliklerden de gelmiyor.

## K28 — Simetrikleştirme idempotentliği geri getirmez

*Yer:* Darboğaz 10  ·  *Tür:* `mantik`  ·  *Belge:* analitik_darbogazlar.txt

*Makine sağlaması:* `test_simetriklestirme_idempotent_yapmaz`

**Kaynakta:**

```
 * Formül 10.3 (Analitik İzdüşüm Onarımı): P_düzeltilmiş = 0.5 * (P_Gr + P_Gr^T)
```

**Tashih:**

```
 * Formul 10.3 (Analitik Izdusum Onarimi): U_ortho = Polar(U_k) = U*V^T  (U_k = U*Sigma*V^T),  P_duzeltilmis = U_ortho * U_ortho^T   [simetriklestirme idempotentligi VERMEZ; onarim tabani yeniden dikleyerek yapilir]
```

**Gerekçe.** Simetrik olmak ile idempotent olmak ayrı şartlardır: $\tfrac12(P+P^T)$ simetriktir ama $P^2 = P$'yi sağlamaz. Sayısal olarak bozulmuş bir izdüşümün onarımı, **tabanın yeniden diklenmesinden** geçer (kutup ayrışımı veya QR); bu, Formül 10.4'ün zaten söylediği şeydir. 10.3 ile 10.4 aynı işi iddia ediyor ama yalnız 10.4 doğru.

## K29 — ``isSet`` tanımsal indirgeme vermez

*Yer:* Darboğaz 12  ·  *Tür:* `mantik`  ·  *Belge:* analitik_darbogazlar.txt

*Makine sağlaması:* `test_hcomp_isset_ile_indirgenmez`

**Kaynakta:**

```
 * Formül 12.3 (Ayrık Lif hcomp İndirgemesi): hcomp^i A [...] u_0 ---> u_0  (isSet(A) ise)
```

**Tashih:**

```
 * Formul 12.3 (Ayrik Lif hcomp Yol-Esitligi): isSet(A) ==> Path A (hcomp^i A [...] u_0) u_0   [ONERMESEL esitlik; TANIMSAL indirgeme (--->) DEGILDIR]
```

**Gerekçe.** ``--->`` tanımsal (hesaplamalı) indirgemeyi gösterir. $\mathsf{isSet}(A)$ ise $A$'daki *yollar* önerme olur, yani $\mathsf{hcomp}$'un neticesi $u_0$ ile **yol-eşit** olur; fakat değerlendirici onu $u_0$'a indirgemez, sistem boş değilse nötr kalır. Bu ayrım aynı külliyattaki bir başka risalede de aynı şekilde kurulmuş ve ``omega_kategori`` modülünde makine ile çürütülmüştü.

## K30 — Ölçek çarpanı alana değil norma aittir

*Yer:* Darboğaz 30  ·  *Tür:* `olcek`  ·  *Belge:* analitik_darbogazlar.txt

*Makine sağlaması:* `test_quadrature_agirligi_alana_uygulanmaz`

**Kaynakta:**

```
 * Formül 30.1 (Izgara Bağımsız Doğrusal Ölçekleme): v_norm(x) = v(x) * sqrt( Area(Omega) / N_grid )
```

**Tashih:**

```
 * Formul 30.1 (Izgara Bagimsiz Norm): ||v_N||_L2 = sqrt( (Area(Omega)/N_grid) * sum_i |v(x_i)|^2 )   [olcek carpani QUADRATURE agirligidir; ALANIN kendisine uygulanirsa alan cozunurluge bagimli hale gelir]
```

**Gerekçe.** $\sqrt{|\Omega|/N}$ bir **quadrature ağırlığıdır**: Riemann toplamını integrale çevirir ve *norm* hesabına girer. Alanın kendisini bu çarpanla ölçeklemek, $v$'yi çözünürlüğe bağımlı kılar -- yani Formül 30.4'ün ($G_{4096}(v) = G_{128}(v)$) tam aksini yapar. Formül 30.3 zaten doğru hâlini yazıyor; 30.1 onunla çelişiyor.

## K31 — Sıfır kovaryans bağımsızlık demek değildir

*Yer:* Darboğaz 42  ·  *Tür:* `istatistik`  ·  *Belge:* analitik_darbogazlar.txt

*Makine sağlaması:* `test_sifir_kovaryans_bagimsizlik_degil`

**Kaynakta:**

```
 * Formül 42.5 (B-Separation İnvaryantı): I( X_i ||_B X_j | Z ) == I( Cov(X_i, X_j | Z) == 0 )
```

**Tashih:**

```
 * Formul 42.5 (B-Separation Invaryanti): I( X_i ||_B X_j | Z ) ==> I( Cov(X_i, X_j | Z) == 0 )   [tek yonlu; tersi ancak MUSTEREK GAUSS halde dogrudur. Genel halde sartli bagimsizlik testi kullanilir, kovaryans yetmez]
```

**Gerekçe.** Sıfır (şartlı) kovaryans, (şartlı) bağımsızlığın **gerek** şartıdır, yeter şartı değil. $X \sim U(-1,1)$, $Y = X^2$ alın: $\mathrm{Cov}(X,Y) = 0$ fakat $Y$ tamamen $X$ tarafından belirlenmiştir. Formül çift yönlü ($==$) yazıldığı için, doğrusal olmayan her bağımlılığı "bağımsız" ilan eder -- ki nedensellik keşfinde en tehlikeli yanılgı budur.

## K32 — Kahan hata sınırı $N$'den bağımsızdır

*Yer:* Darboğaz 62  ·  *Tür:* `olcek`  ·  *Belge:* analitik_darbogazlar.txt

*Makine sağlaması:* `test_kahan_hata_siniri_N_den_bagimsiz`

**Kaynakta:**

```
 * Formül 62.5 (Sayısal Duyarlılık İnvaryantı): | KahanSum({x_i}) - sum_analitik(x_i) | <= N * eps_mach * sum|x_i|
```

**Tashih:**

```
 * Formul 62.5 (Sayisal Duyarlilik Invaryanti): | KahanSum({x_i}) - sum_analitik(x_i) | <= (2*eps_mach + O(N*eps_mach^2)) * sum|x_i|   [N'den BAGIMSIZ; N*eps siniri naif toplamanin sinridir ve Kahan'in butun faydasini siler]
```

**Gerekçe.** Kahan toplamasının klasik hata sınırı $(2\varepsilon + O(N\varepsilon^2))\sum|x_i|$'dir ve baş terim $N$'den **bağımsızdır**; usulün bütün değeri buradadır. $N\varepsilon\sum|x_i|$ ise tam olarak **naif** toplamanın sınırıdır. Yazıldığı hâliyle formül, Kahan kullanmakla kullanmamak arasında fark olmadığını söylüyor.

## K33 — Lif hacmi çarpım hacmine eşitse demet aşikârdır

*Yer:* Darboğaz 63  ·  *Tür:* `mantik`  ·  *Belge:* analitik_darbogazlar.txt

**Kaynakta:**

```
 * Formül 63.5 (Lifli Mana Korunumu): ManaHacmi(w) == prod_(j=1)^40 vol(X_j) > 0
```

**Tashih:**

```
 * Formul 63.5 (Lifli Mana Korunumu): 0 < ManaHacmi(w) <= prod_(j=1)^40 vol(X_j),  ve  int_(w in Taban) ManaHacmi(w) dw == vol(Theta_40)   [lif TOPLAM uzaya esit olamaz; esit olsaydi pi bilgi tasimazdi]
```

**Gerekçe.** $\mathrm{Fib}_w = \pi^{-1}(w)$ toplam uzayın bir **lifidir**; hacmi bütün veçhe uzaylarının çarpımına eşit olsaydı, lif toplam uzayın kendisi olurdu ve $\pi$ hiçbir şeyi ayırt etmezdi -- yani kelimeye göre değişen bir mana kalmazdı. Doğru korunum, liflerin taban üzerinde **integralinin** toplam hacmi vermesidir (Fubini).

## K34 — Pencereden sonra Parseval eşitliği bozulur

*Yer:* Darboğaz 66  ·  *Tür:* `olcek`  ·  *Belge:* analitik_darbogazlar.txt

*Makine sağlaması:* `test_pencereden_sonra_parseval`

**Kaynakta:**

```
 * Formül 66.5 (Girişimsiz Sinyal Korunumu): || Phi_metin_sade ||^2 == sum || Fib_(w_k) ||^2
```

**Tashih:**

```
 * Formul 66.5 (Girisimsiz Sinyal Korunumu): || Phi_metin_sade ||^2 == (||w_kaiser||^2 / L) * sum || Fib_(w_k) ||^2   [pencereleme enerjiyi DEGISTIRIR; Parseval ancak pencere enerjisi carpaniyla kurulur, penceresiz halde ise esitlik tamdir]
```

**Gerekçe.** Parseval eşitliği ortonormal taban için geçerlidir. Formül 66.3 sinyali $w_{\text{kaiser}}$ ile çarpıyor; çarpılmış sinyalin enerjisi pencerenin enerjisiyle ölçeklenir ve ham katsayı toplamına **eşit olmaz**. Yani 66.3 ile 66.5 bir arada duramaz: ya pencere kalkar (eşitlik tam olur) ya da eşitliğe pencere enerjisi çarpanı girer.

## K35 — Kare olmayan Jacobi'nin tayfı yoktur

*Yer:* Darboğaz 41  ·  *Tür:* `tip`  ·  *Belge:* analitik_darbogazlar.txt

**Kaynakta:**

```
 * Formül 41.4 (Kararlı Denge Şartı): forall lambda in Spec(J_phi), Re(lambda) < 0
```

**Tashih:**

```
 * Formul 41.4 (Kararli Denge Sarti): m == n olmali (denklem sayisi = bilinmeyen sayisi); o halde forall lambda in Spec(J_phi), Re(lambda) < 0.  m != n ise denge tekil degildir ve kararlilik Spec ile degil, tekil degerlerle (sigma_min(J_phi) > 0) okunur
```

**Gerekçe.** Formül 41.3 $J_\phi = [\partial\phi_j/\partial X_k]$'yi $m \times n$ olarak tanımlıyor (Formül 41.2'de $A_{\text{BGCM}} \in \mathbb{R}^{n\times m}$). Kare olmayan bir dizeyin **özdeğeri yoktur**, dolayısıyla $\mathrm{Spec}(J_\phi)$ tanımsızdır. Kararlılık ancak $m = n$ iken özdeğerlerle konuşulur.
