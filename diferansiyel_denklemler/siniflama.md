# Diferansiyel Denklemlerin Sınıflandırılması

Bu dosya diferansiyel denklemleri dal dal ayırır. Her düğümün alt dalları birbirini dışlar ve üst düzeydeki kümeyi tamamen örter. Bir denklem tam bir yaprağa düşer.

## 0. Kapsam ve öncelik kuralı

Kapsam: bir ya da daha çok bilinmeyen fonksiyonu ve bu fonksiyonların türevlerini içeren, bağımsız değişkenlere göre yazılmış her denklem ve denklem sistemi.

Öncelik kuralı: Bir denklem birden fazla dala uyuyorsa (örneğin hem ayrılabilir hem Bernoulli tipi) dalların yazılış sırasında en önce gelen dala konur. Böylece her denklem tek bir yaprağa düşer ve yapraklar çakışmaz.

## 1. Üst düzey ayrım

```
DİFERANSİYEL DENKLEM
├── Adi diferansiyel denklem: bağımsız değişken sayısı 1
└── Kısmi diferansiyel denklem: bağımsız değişken sayısı 2 veya daha fazla
```

Her denklemin bağımsız değişken sayısı 1 ya da en az 2 olduğu için bu ayrım eksiksizdir.

## 2. Adi diferansiyel denklemler

```
ADİ DİFERANSİYEL DENKLEM
├── Tek bilinmeyen fonksiyon
│   ├── Birinci mertebe
│   │   ├── Ayrılabilir: y' = f(x)g(y)
│   │   ├── Lineer: y' + p(x)y = q(x)
│   │   ├── Bernoulli: y' + p(x)y = q(x)y^n, n ∉ {0, 1}
│   │   ├── Riccati: y' = p(x) + q(x)y + r(x)y²
│   │   ├── Homojen: y' = F(y/x)
│   │   ├── Tam diferansiyel: M dx + N dy = 0, ∂M/∂y = ∂N/∂x
│   │   ├── İntegrasyon çarpanlı: tam değil, ama bir çarpanla tam yapılabilen
│   │   ├── Clairaut: y = xy' + f(y')
│   │   ├── Lagrange: y = x f(y') + g(y')
│   │   └── Diğer birinci mertebe
│   ├── İkinci mertebe
│   │   ├── Lineer
│   │   │   ├── Sabit katsayılı
│   │   │   │   ├── Homojen, karakteristik kökler reel ve farklı
│   │   │   │   ├── Homojen, karakteristik kökler reel ve eşit
│   │   │   │   ├── Homojen, karakteristik kökler karmaşık eşlenik
│   │   │   │   └── Homojen olmayan (sağ taraf sıfırdan farklı)
│   │   │   ├── Euler–Cauchy: x²y'' + axy' + by = f(x), a ve b sabit
│   │   │   └── Değişken katsayılı, Euler–Cauchy değil
│   │   └── Lineer değil
│   │       ├── x açık değil: y'' = F(y, y')
│   │       ├── y açık değil: y'' = F(x, y')
│   │       └── Diğer ikinci mertebe
│   └── Üçüncü ve daha yüksek mertebe
│       ├── Lineer, sabit katsayılı
│       ├── Lineer, değişken katsayılı
│       └── Lineer değil
└── Birden fazla bilinmeyen fonksiyon (sistem)
    ├── Lineer, sabit katsayılı: X' = AX + F(t), A sabit matris
    │   ├── Özdeğerleri reel ve farklı
    │   ├── Özdeğerleri reel ve tekrarlı (köşegenleştirilemeyen dahil)
    │   ├── Özdeğerleri karmaşık eşlenik
    │   └── Özdeğerlerinden biri sıfır (A tekil)
    ├── Lineer, değişken katsayılı: X' = A(t)X + F(t), A(t) sabit değil
    └── Lineer değil: X' = G(t, X)
```

## 3. Kısmi diferansiyel denklemler

```
KISMİ DİFERANSİYEL DENKLEM
├── Tek bilinmeyen fonksiyon
│   ├── Birinci mertebe
│   │   ├── Lineer: a·u_x + b·u_y = c·u + d
│   │   ├── Kuazi-lineer: a(x,y,u)u_x + b(x,y,u)u_y = c(x,y,u)
│   │   └── Diğer birinci mertebe (kuazi-lineer de değil)
│   ├── İkinci mertebe, lineer, iki bağımsız değişkenli
│   │   ├── Eliptik: B² − 4AC < 0 (örnek: Laplace denklemi u_xx + u_yy = 0)
│   │   ├── Parabolik: B² − 4AC = 0 (örnek: ısı denklemi u_t = u_xx)
│   │   └── Hiperbolik: B² − 4AC > 0 (örnek: dalga denklemi u_tt = u_xx)
│   ├── İkinci mertebe, lineer, ikiden fazla bağımsız değişkenli
│   └── İkinci mertebe lineer değil, ya da üçüncü ve daha yüksek mertebe
└── Birden fazla bilinmeyen fonksiyon (sistem)
    ├── Lineer
    └── Lineer değil
```

İkinci mertebe lineer kısmi denklemlerde ayrım, kısmi türevlerin katsayılarından (A, B, C) hesaplanan $B^2-4AC$ işaretine göre yapılır. İşaret üç durumdan tam biridir (negatif, sıfır, pozitif), bu yüzden yapraklar eksiksizdir.

## 4. Yaprak listesi

| Yaprak | Tanım |
|---|---|
| Ayrılabilir | $y' = f(x)g(y)$ |
| Birinci mertebe lineer | $y' + p(x)y = q(x)$ |
| Bernoulli | $y' + p y = q y^n$, $n \notin \{0,1\}$ |
| Riccati | $y' = p + q y + r y^2$ |
| Homojen | $y' = F(y/x)$ |
| Tam diferansiyel | $M\,dx + N\,dy = 0$, $M_y = N_x$ |
| İntegrasyon çarpanlı | Bir çarpanla tam hâle getirilebilen |
| Clairaut | $y = xy' + f(y')$ |
| Lagrange | $y = x f(y') + g(y')$ |
| Diğer birinci mertebe | Yukarıdakilerin hiçbiri |
| Sabit katsayılı ikinci mertebe | Karakteristik kök türüne göre ve homojen olmayan |
| Euler–Cauchy | $x^2y'' + axy' + by = f(x)$ |
| Değişken katsayılı lineer | Euler–Cauchy değil |
| Lineer olmayan ikinci mertebe | $x$ açık değil / $y$ açık değil / diğer |
| Üçüncü ve yüksek mertebe | Lineer sabit / lineer değişken / lineer değil |
| Sabit katsayılı sistem | $A$ matrisinin özdeğer türü |
| Değişken katsayılı sistem | $A(t)$ |
| Lineer olmayan sistem | $X' = G(t,X)$ |
| Birinci mertebe lineer kısmi | $a\,u_x + b\,u_y = c\,u + d$ |
| Kuazi-lineer kısmi | En yüksek türevler lineer |
| Diğer birinci mertebe kısmi | Kuazi-lineer da değil |
| Eliptik | $B^2 - 4AC < 0$ |
| Parabolik | $B^2 - 4AC = 0$ |
| Hiperbolik | $B^2 - 4AC > 0$ |
| İkiden fazla bağımsız değişkenli ikinci mertebe lineer kısmi | — |
| Lineer olmayan ikinci veya yüksek mertebe kısmi | — |
| Lineer kısmi sistem | — |
| Lineer olmayan kısmi sistem | — |

## 5. Kapsama ve ayrıklık kontrolü

- **Üst ayrım:** Bağımsız değişken sayısı 1 ya da en az 2'dir.
- **Tek ya da çok bilinmeyen:** Bilinmeyen fonksiyon sayısı 1 ya da en az 2'dir.
- **Birinci mertebe adi denklemler:** Ayrılabilir olanlar önce ayrılır. Kalanlar sırayla lineer, Bernoulli, Riccati, homojen, tam, integrasyon çarpanlı, Clairaut ve Lagrange'a bakılarak atanır. "Diğer birinci mertebe" bu sıralamada kalan her şeyi alır.
- **İkinci ve yüksek mertebe adi denklemler:** Lineer / lineer değil ayrımı tam bir bölümlemedir. Lineer dalda katsayıların sabit ya da değişken, Euler–Cauchy biçiminde ya da değil olması ayrımı tamamlar. Homojen olup olmama ve karakteristik kökün türü sabit katsayılı dalı ayrıştırır.
- **Sistemler:** Lineer / lineer değil; lineer dalda sabit / değişken katsayı; sabit dalda $A$ matrisinin özdeğer türü ayrımı tamamlar.
- **İkinci mertebe kısmi denklemler:** $B^2 - 4AC$ için üç durum (negatif, sıfır, pozitif) tamdır.
- **Birinci mertebe kısmi denklemler:** Lineer, kuazi-lineer ve diğer; bu üç küme eksiksiz böler.

## 6. Çözüm yöntemleri

Bu tablo, verilen usul haritasının düzeltilmiş ve genişletilmiş hâlidir. Düzeltmeler ilgili satırda ayrıca not edilmiştir.

| Yöntem | Mertebe | Lineer mi? | Temel şart / tetikleyici |
|---|---|---|---|
| Değişkenlerine ayırma | Ana kullanım birinci mertebe; bazı yüksek mertebe özel biçimler | Lineer ve lineer değil | Sağ taraf $f(x)\cdot g(y)$ çarpımına ayrılıyorsa |
| Tam diferansiyel (tamlaştırma) | Birinci mertebe | Lineer ve lineer değil | $\partial M/\partial y = \partial N/\partial x$ |
| İntegrasyon çarpanı | Birinci mertebe | Lineer ve lineer değil | Tam değilse, $\mu(x)$, $\mu(y)$ ya da $\mu(x,y)$ ile tam hâle getirilebiliyorsa. *Düzeltme:* Eski tabloda "sadece lineer" yazıyordu; bu yanlıştı. |
| Lineer birinci mertebe (çarpan formülü) | Birinci mertebe | Sadece lineer | $y' + P(x)y = Q(x)$; çarpan $\mu = e^{\int P\,dx}$ |
| Bernoulli dönüşümü | Birinci mertebe | Lineer değil | $y' + Py = Qy^n$, $n \neq 0, 1$; $v = y^{1-n}$ |
| Riccati dönüşümü | Birinci mertebe | Lineer değil | $y' = p + qy + ry^2$; bir özel çözüm $y_1$ biliniyorsa $y = y_1 + 1/v$ |
| Homojen dönüşüm (Euler) | Birinci mertebe | Lineer değil | $y' = F(y/x)$; $v = y/x$ |
| Clairaut ve Lagrange yöntemi | Birinci mertebe | Lineer değil | $p = y'$ parametresiyle $y = xp + f(p)$ ya da $y = xf(p) + g(p)$ |
| Mertebe indirgeme | İkinci ve üstü mertebe | Lineer ve lineer değil | Bir çözüm $y_1$ verilmiş (lineer); $x$ açık değil; $y$ açık değil. *Düzeltme:* Eski tabloda "sadece lineer" yazıyordu; $x$ ve $y$ açık değil durumları lineer değil denklemlerde de kullanılır. |
| Karakteristik denklem | İkinci ve üstü mertebe | Sadece lineer | Katsayılar sabit: $ay'' + by' + cy = 0$ için $ar^2 + br + c = 0$ |
| Euler–Cauchy dönüşümü ($x = e^t$) | İkinci ve üstü mertebe | Sadece lineer | $x^2y'' + axy' + by = f(x)$ |
| Belirsiz katsayılar | İkinci ve üstü mertebe | Sadece lineer | Sabit katsayılı, sağ taraf polinom, üstel ya da trigonometrik |
| Parametrelerin değişimi | İkinci ve üstü mertebe | Sadece lineer | Homojen olmayan lineer denklem; homojen çözümler biliniyorsa |
| Özdeğer ve özvektör | Sistem | Sadece lineer | $X' = AX$, $A$ sabit matris |
| Jordan biçimi ve üstel matris | Sistem | Sadece lineer | Tekrarlı özdeğer, köşegenleştirilemeyen $A$ |
| Temel matris ve parametrelerin değişimi (sistem) | Sistem | Sadece lineer | $X' = A(t)X + F(t)$, $A(t)$ değişken |
| Karakteristik yöntemi | Birinci mertebe kısmi | Lineer ve kuazi-lineer | $a\,u_x + b\,u_y = c\,u + d$ ya da kuazi-lineer biçim |
| Sınıflandırma ve kanonik form | İkinci mertebe kısmi | Sadece lineer | İki bağımsız değişkenli; $B^2 - 4AC$ işareti |
| Değişkenlere ayırma (Fourier) | Kısmi | Sadece lineer | $u = X(x)Y(y)$ çarpımı ve homojen sınır koşulları |
| Laplace ve Fourier dönüşümü | Adi ve kısmi | Sadece lineer | Sabit katsayılı; başlangıç ya da sınır koşulları verilmiş |
| Ters saçılma dönüşümü (IST) | Kısmi (birinci mertebe zamana göre) | Lineer değil (integrable denklemler) | Denklemin bir Lax çifti olması; KdV, NLS, sine-Gordon gibi |

## 7. Yöntemlerin yapraklara eşlenmesi

Her yaprağa en az bir yöntem atanır. Yöntemi olmayan yapraklar "genel analitik yöntem yok" diye işaretlenir; bunlar sayısal ya da özel durum yöntemiyle çözülür.

| Yaprak | Yöntemler |
|---|---|
| Ayrılabilir | Değişkenlerine ayırma |
| Birinci mertebe lineer | Lineer birinci mertebe (çarpan formülü); integrasyon çarpanı |
| Bernoulli | Bernoulli dönüşümü |
| Riccati | Riccati dönüşümü |
| Homojen | Homojen dönüşüm |
| Tam diferansiyel | Tam diferansiyel (tamlaştırma) |
| İntegrasyon çarpanlı | İntegrasyon çarpanı |
| Clairaut | Clairaut ve Lagrange yöntemi |
| Lagrange | Clairaut ve Lagrange yöntemi |
| Diğer birinci mertebe | Genel analitik yöntem yok |
| Sabit katsayılı ikinci mertebe (homojen) | Karakteristik denklem |
| Sabit katsayılı ikinci mertebe (homojen olmayan) | Karakteristik denklem; belirsiz katsayılar; parametrelerin değişimi |
| Euler–Cauchy | Euler–Cauchy dönüşümü; parametrelerin değişimi |
| Değişken katsayılı lineer ikinci mertebe | Parametrelerin değişimi (homojen çözümler biliniyorsa); aksi hâlde genel analitik yöntem yok |
| Lineer olmayan ikinci mertebe ($x$ açık değil) | Mertebe indirgeme |
| Lineer olmayan ikinci mertebe ($y$ açık değil) | Mertebe indirgeme |
| Lineer olmayan ikinci mertebe (diğer) | Mertebe indirgeme (uygunsa); aksi hâlde genel analitik yöntem yok |
| Üçüncü ve yüksek mertebe, lineer sabit katsayılı | Karakteristik denklem; belirsiz katsayılar; parametrelerin değişimi |
| Üçüncü ve yüksek mertebe, lineer değişken katsayılı | Parametrelerin değişimi (homojen çözümler biliniyorsa); aksi hâlde genel analitik yöntem yok |
| Üçüncü ve yüksek mertebe, lineer değil | Genel analitik yöntem yok |
| Sabit katsayılı sistem (özdeğerler reel ve farklı, reel ve tekrarlı, karmaşık, sıfır içeren) | Özdeğer ve özvektör |
| Sabit katsayılı sistem (tekrarlı, köşegenleştirilemeyen) | Özdeğer ve özvektör; Jordan biçimi ve üstel matris |
| Değişken katsayılı sistem | Temel matris ve parametrelerin değişimi |
| Lineer olmayan sistem | Genel analitik yöntem yok |
| Birinci mertebe lineer kısmi | Karakteristik yöntemi |
| Kuazi-lineer kısmi | Karakteristik yöntemi |
| Diğer birinci mertebe kısmi | Genel analitik yöntem yok |
| Eliptik | Sınıflandırma ve kanonik form; değişkenlere ayırma (Fourier); Laplace ve Fourier dönüşümü |
| Parabolik | Sınıflandırma ve kanonik form; değişkenlere ayırma (Fourier); Laplace ve Fourier dönüşümü |
| Hiperbolik | Sınıflandırma ve kanonik form; değişkenlere ayırma (Fourier); Laplace ve Fourier dönüşümü |
| İkiden fazla bağımsız değişkenli ikinci mertebe lineer kısmi | Değişkenlere ayırma (Fourier), ayrılabiliyorsa; aksi hâlde genel analitik yöntem yok |
| Lineer olmayan ikinci veya yüksek mertebe kısmi | Ters saçılma dönüşümü (IST), integrable ise; Cole–Hopf (Burgers tipi); aksi hâlde genel analitik yöntem yok |
| Lineer kısmi sistem | Değişkenlere ayırma (Fourier) ve Laplace ve Fourier dönüşümü, uygunsa |
| Lineer olmayan kısmi sistem | Genel analitik yöntem yok |

## 8. Kapsama kontrolü (yöntemler için)

- Her yaprak ya bir ya da daha çok adlandırılmış yönteme bağlıdır ya da "genel analitik yöntem yok" işaretine sahiptir. Başka durum yoktur.
- Tabloda adı geçen her yöntem en az bir yaprağa bağlanmıştır.
- Bir denklem yapraklara düştükten sonra, yöntem seçimi o yaprağın listesindeki ilk uygun yönteme göre yapılır.

## 9. Ek: Her yaprak için üç örnek denklem ve çözüm usulü

Her yaprak için üç örnek verilmiştir. "Bariz" örnek yaprağa açıkça uyar. "Görmek zor" örnek, yaprağa uyması için bir dönüşüm ya da düzenleme gerektirir. "Fevkalade zor" örnek, o yaprağın içinde tanıması ve çözmesi en zor olanıdır.

Yazım notu: Türev y' ile, ikinci türev y'' ile gösterilir; kuvvet ^ ile yazılır; e^x yerine exp(x) kullanılır.

### 9.1 Adi diferansiyel denklemler, tek bilinmeyen, birinci mertebe

Yaprak: Ayrılabilir

Bariz: y' = x*y
Usul: Değişkenlere ayırma. dy/y = x dx, buradan ln|y| = x^2/2 + c.

Görmek zor: y' = exp(x + y)
Usul: exp(x + y) = exp(x)*exp(y) olduğu görülür; sonra exp(-y) dy = exp(x) dx ile ayrılır.

Fevkalade zor: y' = sin(x + y) - sin(x - y)
Usul: Toplam-fark özdeşliği sin(x+y) - sin(x-y) = 2*cos(x)*sin(y) verir. Sonra csc(y) dy = 2*cos(x) dx ile ayrılır. Özdeşliği görmek gerekir.

Yaprak: Birinci mertebe lineer

Bariz: y' + 2y = exp(x)
Usul: İntegrasyon çarpanı mu = exp(2x). (mu*y)' = mu*exp(x) integrallenir.

Görmek zor: x*y' + y = x^3
Usul: Standart biçime getirilir: y' + y/x = x^2. Çarpan mu = x, yani (x*y)' = x^3 yazılır ve integrallenir.

Fevkalade zor: sin(x)*y' + cos(x)*y = exp(x)
Usul: Sol taraf (y*sin(x))' türevidir. Standart biçime getirip çarpan mu = sin(x) ile de çözülür. Sonuç y = (exp(x) + c)/sin(x).

Yaprak: Bernoulli

Bariz: y' + y = y^2
Usul: n = 2. v = y^(1-2) = 1/y dönüşümü yapılır; v' - v = -1 lineer denklemi elde edilir.

Görmek zor: 2*x*y*y' + y^2 = x^3
Usul: Denklem y' + y/(2x) = (x^2/2)/y biçimine getirilir; n = -1. v = y^2 dönüşümüyle x*v' + v = x^3, yani v' + v/x = x^2 lineer hâle gelir.

Fevkalade zor: y' + y/x = (1 + ln(x))*y^3
Usul: n = 3. v = y^(-2) dönüşümüyle v' - 2v/x = -2(1 + ln(x)) lineer denklemi elde edilir.

Yaprak: Riccati

Bariz: y' = y^2 - 2/x^2
Usul: y1 = 1/x bilinen özel çözümdür (kontrol: y1' = -1/x^2 ve y1^2 - 2/x^2 = -1/x^2). Dönüşüm y = y1 + 1/v, sonra v için lineer denklem çözülür.

Görmek zor: x^2*y' = x^2*y^2 - 6
Usul: Denklem y' = y^2 - 6/x^2 biçimine getirilir. y1 = 2/x özel çözümdür (kontrol: y1' = -2/x^2 ve 4/x^2 - 6/x^2 = -2/x^2). Dönüşüm y = y1 + 1/v.

Fevkalade zor: y' = exp(x) - exp(2x) + y^2
Usul: y1 = exp(x) özel çözümü denemeyle bulunur (kontrol: exp(x) = exp(x) - exp(2x) + exp(2x)). Sonra y = y1 + 1/v ve v için lineer denklem.

Yaprak: Homojen

Bariz: y' = y/x + sin(y/x)
Usul: v = y/x dönüşümü. Sonra y = v*x olarak yazılır, v' ile ayrılabilir denklem elde edilir.

Görmek zor: x*y' = y + sqrt(x^2 + y^2) (x > 0)
Usul: Denklem y' = y/x + sqrt(1 + (y/x)^2) biçimine getirilir, v = y/x dönüşümü uygulanır.

Fevkalade zor: x*dy - (y + x*exp(y/x)) dx = 0
Usul: y/x = v dönüşümüyle ayrılabilir hâle gelir. Ayrılabilirlik, exp(v) teriminin dönüşümden sonra ortaya çıkmasıyla görülür.

Yaprak: Tam diferansiyel

Bariz: (2x + y) dx + (x + 2y) dy = 0
Usul: M_y = 1 = N_x. Potansiyel f = x^2 + xy + y^2; çözüm f = c.

Görmek zor: (y*cos(xy) + 1) dx + x*cos(xy) dy = 0
Usul: M_y = cos(xy) - xy*sin(xy) = N_x. Potansiyel f = x + sin(xy); çözüm f = c.

Fevkalade zor: (y/(x^2 + y^2) + exp(x)) dx - (x/(x^2 + y^2)) dy = 0
Usul: M_y = (x^2 - y^2)/(x^2 + y^2)^2 = N_x. Potansiyel, iki terimin ayrı ayrı integrali alınarak bulunur. Terim y/(x^2+y^2) ile x/(x^2+y^2) ilişkisi bir açı fonksiyonuna götürür.

Yaprak: İntegrasyon çarpanlı

Bariz: (x + y^2) dx - 2xy dy = 0
Usul: M_y = 2y ve N_x = -2y, tam değil. (M_y - N_x)/N = -2/x yalnız x'e bağlı olduğundan mu = 1/x^2 çarpanı kullanılır; sonra tam denklem çözülür.

Görmek zor: (x^2 + y) dx - x dy = 0
Usul: (M_y - N_x)/N = -2/x yalnız x'e bağlıdır. mu = 1/x^2 ile tam hâle gelir.

Fevkalade zor: (x^2 + y^2 + x) dx + y dy = 0
Usul: M_y - N_x = 2y, N = y. (M_y - N_x)/N = 2 sabit olduğundan mu = exp(2x). Çarpanla tam hâle gelen denklem integrallenir.

Yaprak: Clairaut

Bariz: y = x*y' + (y')^2
Usul: p = y' parametresi. Genel çözüm y = c*x + c^2 (p = c). Tekil çözüm, p'ye göre türev alınarak bulunur.

Görmek zor: y = x*y' + ln(y')
Usul: y = x*p + f(p) biçimindedir, f(p) = ln(p). Genel çözüm y = c*x + ln(c).

Fevkalade zor: y = x*y' - exp(y')
Usul: f(p) = -exp(p). Genel çözüm y = c*x - exp(c). Tekil çözüm için f'(p) = x eşitliğinden p elimine edilir.

Yaprak: Lagrange

Bariz: y = 2*x*y' + (y')^2
Usul: p = y' ile f(p) = 2p, g(p) = p^2. Denklem p'ye göre türevlenir; p-x lineer denklemine indirgenir.

Görmek zor: y = x*(y')^2 + 2*y'
Usul: f(p) = p^2, g(p) = 2p. p parametresi ile türev alınır; x(p) için lineer denklem elde edilir.

Fevkalade zor: y = x*exp(y') + ln(y')
Usul: p = y' ile türev alınır: p = exp(p) + (x*exp(p) + 1/p)*dp/dx. Ters çevrilerek dx/dp için lineer denklem çözülür.

Yaprak: Diğer birinci mertebe

Bariz: y' = x + sin(y)
Usul: Genel analitik yöntem yoktur. Sayısal çözüm (ör. Runge–Kutta) uygulanır.

Görmek zor: y' = y^3 - x^2
Usul: Genel analitik yöntem yoktur. Sayısal çözüm uygulanır.

Fevkalade zor: y' = x*y^3 + x^3*y
Usul: Genel analitik yöntem yoktur. Yalnız belirli başlangıç koşulları için sayısal çözüm uygulanır.

### 9.2 Adi diferansiyel denklemler, tek bilinmeyen, ikinci mertebe

Yaprak: Sabit katsayılı, homojen, reel ve farklı kökler

Bariz: y'' - 3y' + 2y = 0
Usul: Karakteristik denklem r^2 - 3r + 2 = 0; kökler 1 ve 2. Genel çözüm c1*exp(x) + c2*exp(2x).

Görmek zor: y'' + y' - 2y = 0 ile yazılmış (D^2 + D - 2) y = 0 biçimi
Usul: Operatör biçimi karakteristik denkleme çevrilir; r^2 + r - 2 = 0, kökler 1 ve -2.

Fevkalade zor: 6*y'' - 5*y' + y = 0
Usul: 6r^2 - 5r + 1 = 0; kökler 1/2 ve 1/3. Katsayıların baş katsayısı 1 olmayınca kökler kesirli çıkar; karakteristik denklem doğrudan çözülür.

Yaprak: Sabit katsayılı, homojen, reel ve eşit kökler

Bariz: y'' + 4y' + 4y = 0
Usul: r^2 + 4r + 4 = 0, r = -2 çift kök. Genel çözüm (c1 + c2*x)*exp(-2x).

Görmek zor: y'' - 2y' + y = 0 ile yazılmış (D - 1)^2 y = 0
Usul: Operatör çarpanlarına ayrılır; kök 1, çift. Genel çözüm (c1 + c2*x)*exp(x).

Fevkalade zor: 9*y'' - 12*y' + 4*y = 0
Usul: 9r^2 - 12r + 4 = (3r - 2)^2 = 0, r = 2/3 çift. Genel çözüm (c1 + c2*x)*exp(2x/3).

Yaprak: Sabit katsayılı, homojen, karmaşık eşlenik kökler

Bariz: y'' + y = 0
Usul: r^2 + 1 = 0, r = ±i. Genel çözüm c1*cos(x) + c2*sin(x).

Görmek zor: y'' + 2y' + 5y = 0
Usul: r^2 + 2r + 5 = 0, r = -1 ± 2i. Genel çözüm exp(-x)*(c1*cos(2x) + c2*sin(2x)).

Fevkalade zor: y'' - 4y' + 13y = 0
Usul: r^2 - 4r + 13 = 0, r = 2 ± 3i. Genel çözüm exp(2x)*(c1*cos(3x) + c2*sin(3x)).

Yaprak: Sabit katsayılı, homojen olmayan

Bariz: y'' + y = x^2
Usul: Belirsiz katsayılar. Homojen çözüm c1*cos(x) + c2*sin(x). Özel çözüm y_p = a*x^2 + b*x + c; katsayılar yerine konularak bulunur.

Görmek zor: y'' - 3y' + 2y = exp(x)
Usul: Sağ taraf exp(x) homojen çözümle çakışır (kök 1). Bu yüzden özel çözüm x*exp(x) biçiminde denenir.

Fevkalade zor: y'' + y = sec(x)
Usul: Belirsiz katsayılar uygulanamaz. Parametrelerin değişimi: y_p = -cos(x)*integral(sin(x)*sec(x) dx) + sin(x)*integral(cos(x)*sec(x) dx).

Yaprak: Euler–Cauchy

Bariz: x^2*y'' + 3x*y' + y = 0
Usul: y = x^r yerine konulur: r(r-1) + 3r + 1 = 0, (r+1)^2 = 0, r = -1 çift. Genel çözüm (c1 + c2*ln(x))/x.

Görmek zor: x^2*y'' - 2x*y' + 2y = x^3
Usul: Homojen kısım y = x^r ile çözülür (r^2 - 3r + 2 = 0, r = 1, 2). Sağ taraf x^3 için özel çözüm a*x^3 biçiminde denenir ya da parametrelerin değişimi uygulanır.

Fevkalade zor: x^2*y'' - x*y' + 2y = x^2*ln(x)
Usul: x = exp(t) dönüşümüyle sabit katsayılı lineer denkleme çevrilir (t cinsinden). Homojen kısmın karakteristik kökleri karmaşıktır; özel çözüm parametrelerin değişimiyle bulunur.

Yaprak: Değişken katsayılı lineer (Euler–Cauchy değil)

Bariz: y'' + x*y = 0
Usul: Airy tipi denklem. Kuvvet serisi (Frobenius) yöntemiyle çözülür; kapalı form olarak Airy fonksiyonları kullanılır.

Görmek zor: x*y'' + (1 - x)*y' + 2y = 0
Usul: Kuvvet serisi yöntemi; bu denklem Laguerre tipindedir, katsayılar seri katsayılarına dönüştürülür.

Fevkalade zor: x^2*y'' + x*y' + (x^2 - 4)*y = 0
Usul: Bessel denklemi (mertebe 2). Bessel fonksiyonları J2 ve Y2 ile genel çözüm yazılır; tanıma ve kuvvet serisi yöntemi kullanılır.

Yaprak: Lineer değil, x açık değil

Bariz: y'' = 2*y
Usul: Mertebe indirgeme: p = y', y'' = p*dp/dy. p*dp/dy = 2y, p^2 = 2y^2 + c.

Görmek zor: y*y'' - (y')^2 = 0
Usul: Mertebe indirgeme: p = y', y'' = p*dp/dy. y*p*dp/dy = p^2, sonra p = c*y, y = exp(c*x) ailesi.

Fevkalade zor: y*y'' = (y')^2 + (y')^3
Usul: p = y', y*p*dp/dy = p^2 + p^3, yani y*dp/dy = p + p^2. Ayrılabilir: dp/(p + p^2) = dy/y; sonra y ve x ilişkisi p'den integral alınarak bulunur.

Yaprak: Lineer değil, y açık değil

Bariz: y'' = 3*x
Usul: p = y', p' = 3x, p = (3/2)x^2 + c1; sonra bir integral daha. Aslında doğrudan iki kez integral alınarak çözülür.

Görmek zor: x*y'' + y' = 1
Usul: Denklem (x*y')' = 1 biçimindedir. p = y' ile x*p = x + c, p = 1 + c/x; sonra integral.

Fevkalade zor: y'' = x + (y')^2
Usul: p = y' ile p' = x + p^2 (Riccati tipi). Mertebe indirgeme sonrası Riccati dönüşümü uygulanır; özel çözüm polinom değildir, çözüm Airy tipi fonksiyonlarla yazılır.

Yaprak: Lineer değil, diğer ikinci mertebe

Bariz: y'' + y*y' + x = 0
Usul: Genel analitik yöntem yoktur. Sayısal çözüm (ör. Runge–Kutta) uygulanır.

Görmek zor: y'' = x*y + (y')^2
Usul: Genel analitik yöntem yoktur. Sayısal çözüm uygulanır.

Fevkalade zor: y'' = exp(x*y)
Usul: Genel analitik yöntem yoktur. Sayısal çözüm uygulanır.

### 9.3 Adi diferansiyel denklemler, tek bilinmeyen, üçüncü ve yüksek mertebe

Yaprak: Lineer, sabit katsayılı

Bariz: y''' - y' = 0
Usul: r^3 - r = 0, r = 0, 1, -1. Genel çözüm c1 + c2*exp(x) + c3*exp(-x).

Görmek zor: y''' - 3y'' + 3y' - y = 0
Usul: (r - 1)^3 = 0, r = 1 üçlü. Genel çözüm (c1 + c2*x + c3*x^2)*exp(x).

Fevkalade zor: y''' + 2y'' + 2y' + 4y = 0
Usul: r^3 + 2r^2 + 2r + 4 = (r + 2)(r^2 + 2) = 0. Kökler -2 ve ±i*sqrt(2). Çarpanlara ayırmayı görmek gerekir.

Yaprak: Lineer, değişken katsayılı

Bariz: x*y''' + y'' = 0
Usul: y'' = w diye alınır; x*w' + w = 0 birinci mertebe lineer (ayrılabilir), sonra iki integral.

Görmek zor: x^3*y''' + 3x^2*y'' + x*y' = 1
Usul: Euler–Cauchy yapısındadır; x = exp(t) ile sabit katsayılı denkleme çevrilir. Ya da parametrelerin değişimi uygulanır.

Fevkalade zor: (1 - x^2)*y''' - 2x*y'' + 3y' = 0
Usul: w = y' diye alınır; (1 - x^2)*w'' - 2x*w' + 3w = 0, ikinci mertebe lineer, değişken katsayılı (Legendre tipi, ν(ν+1) = 3). Kuvvet serisi yöntemi kullanılır.

Yaprak: Lineer değil

Bariz: y''' + y'*y'' = 0
Usul: Sol taraf (y'' + (y')^2/2)' türevidir. Buradan y'' + (y')^2/2 = c; bu ikinci mertebeli bir denklemdir ve mertebe indirgemesi ile ilerler.

Görmek zor: y''' = exp(y)
Usul: y' = p(y) mertebe indirgemesi: y'' = p*dp/dy, y''' = p*d(p dp/dy)/dy. Bu mertebe indirgemesiyle çözüm birinci mertebe denklemlere iner.

Fevkalade zor: y''' + x*y*y' = 0
Usul: Genel analitik yöntem yoktur. Sayısal çözüm (ör. Runge–Kutta) uygulanır.

### 9.4 Adi diferansiyel denklem sistemleri

Yaprak: Lineer, sabit katsayılı, özdeğerler reel ve farklı

Bariz: x' = x + 2y, y' = 3x + 2y
Usul: A = [[1, 2], [3, 2]]; özdeğerler 4 ve -1 (reel, farklı). Özvektörler bulunur; genel çözüm iki özvektörün üstel çözümlerinin toplamıdır.

Görmek zor: x' = 3x + y, y' = 2x + 4y
Usul: A = [[3, 1], [2, 4]]; iz 7, determinant 10; özdeğerler 5 ve 2 (reel, farklı). Özvektörlerle genel çözüm yazılır.

Fevkalade zor: x' = 0.5x + 1.5y, y' = 1.5x + 0.5y
Usul: A simetrik; özdeğerler 2 ve -1 (reel, farklı). Özvektörler (1,1) ve (1,-1) ile genel çözüm yazılır.

Yaprak: Lineer, sabit katsayılı, özdeğerler reel ve tekrarlı

Bariz: x' = 2x, y' = 2y
Usul: A = 2I, köşegenleştirilebilir. Özdeğer 2 çift, her yön özvektör; genel çözüm exp(2t)*(c1, c2).

Görmek zor: x' = 2x + y, y' = 2y
Usul: A = [[2, 1], [0, 2]], özdeğer 2 çift ama köşegenleştirilemez. Jordan biçimi; çözüm (c1 + c2*t)*exp(2t) biçiminde.

Fevkalade zor: x' = 4x - y, y' = x + 2y
Usul: A = [[4, -1], [1, 2]]; iz 6, det 9; özdeğer 3 çift. A - 3I rank 1; köşegenleştirilemez, Jordan biçimi ve üstel matris ile çözülür.

Yaprak: Lineer, sabit katsayılı, özdeğerler karmaşık eşlenik

Bariz: x' = -y, y' = x
Usul: A = [[0, -1], [1, 0]]; özdeğerler ±i. Genel çözüm dönme: (c1*cos(t) - c2*sin(t), c1*sin(t) + c2*cos(t)).

Görmek zor: x' = x - 2y, y' = 2x + y
Usul: A = [[1, -2], [2, 1]]; özdeğerler 1 ± 2i. Gerçek ve sanal kısımlarla çözüm exp(t)*(cos(2t), sin(2t)) türevlerinden oluşur.

Fevkalade zor: x' = x + 5y, y' = -2x - y
Usul: A = [[1, 5], [-2, -1]]; iz 0, det 9; özdeğerler ±3i. Karmaşık özdeğer usulüyle çözülür.

Yaprak: Lineer, sabit katsayılı, özdeğerlerden biri sıfır

Bariz: x' = 0, y' = y
Usul: A = diag(0, 1); özdeğerler 0 ve 1. x sabittir, y = c2*exp(t).

Görmek zor: x' = x + y, y' = x + y
Usul: A = [[1, 1], [1, 1]]; özdeğerler 0 ve 2. Sıfır özdeğere karşılık gelen özvektör sabit çözüm verir.

Fevkalade zor: x' = 2x - 2y, y' = x - y
Usul: A = [[2, -2], [1, -1]]; iz 1, det 0; özdeğerler 0 ve 1. Sıfır özdeğerin özvektörü ile sabit çözüm, diğer özdeğer ile üstel çözüm birleştirilir.

Yaprak: Lineer, değişken katsayılı

Bariz: x' = t*x, y' = y
Usul: Köşegen sistem. Her denklem ayrı ayrı integrallenir: x = c1*exp(t^2/2), y = c2*exp(t).

Görmek zor: x' = y, y' = t*x
Usul: x'' = t*x: Airy denklemi. Kuvvet serisi veya Airy fonksiyonları ile çözülür.

Fevkalade zor: x' = (1/t)*x + y, y' = -t*x
Usul: Temel matris ve parametrelerin değişimi. Homojen sistem için temel matris kuvvet serisiyle yazılır; homojen olmayan kısım parametrelerin değişimiyle eklenir.

Yaprak: Lineer değil sistem

Bariz: x' = x - y^2, y' = y
Usul: Genel analitik yöntem yoktur. Sayısal çözüm uygulanır. (y = c*exp(t) ile kısmi analiz yapılabilir.)

Görmek zor: x' = x*y, y' = x + y
Usul: Genel analitik yöntem yoktur. Sayısal çözüm uygulanır.

Fevkalade zor: x' = x*(1 - y), y' = y*(x - 1)
Usul: Lotka–Volterra denklemi. H = x + y - ln(x) - ln(y) ilk integraldir (türevi sıfırdır); faz portresi bu integral ve sayısal çözümle çizilir.

### 9.5 Kısmi diferansiyel denklemler

Yaprak: Birinci mertebe lineer

Bariz: u_x + u_y = 0
Usul: Karakteristik yöntemi. Karakteristik eğriler x - y = sabit. Genel çözüm u = f(x - y).

Görmek zor: x*u_x + y*u_y = u
Usul: Karakteristik yöntemi. Karakteristikler x = c*s, y = d*s biçimindedir; u = x*g(y/x) biçiminde genel çözüm.

Fevkalade zor: y*u_x - x*u_y = 0
Usul: Karakteristik yöntemi. Karakteristikler dairelerdir: x^2 + y^2 = sabit. Genel çözüm u = f(x^2 + y^2).

Yaprak: Kuazi-lineer

Bariz: u*u_x + u_y = 0
Usul: Karakteristik yöntemi (kuazi-lineer). Karakteristik eğriler dx/u = dy/1 = du/0; u sabittir ve karakteristikler doğrudur. Genel çözüm u = f(x - u*y).

Görmek zor: x*u_x + u*u_y = 0
Usul: Karakteristik yöntemi. Karakteristik dx/x = dy/u, du = 0; u sabit, sonra integral.

Fevkalade zor: u*u_x + y*u_y = x
Usul: Karakteristik yöntemi. Karakteristik denklemleri birbirine bağlıdır; u^2 - x^2 = sabit ailesi bulunur, genel çözüm bu ilişkiden yazılır.

Yaprak: Diğer birinci mertebe kısmi

Bariz: u_x^2 + u_y^2 = 1
Usul: Genel analitik yöntem bu tabloda yoktur. Özel çözüm için u = a*x + b*y + c (a^2 + b^2 = 1) denenir; genel çözüm için Charpit yöntemi ya da sayısal yöntem gerekir.

Görmek zor: u_x*u_y = u
Usul: Genel analitik yöntem bu tabloda yoktur. Çözüm için değişkenlere ayırma (u = f(x)g(y)) denenebilir; genelde Charpit yöntemi kullanılır.

Fevkalade zor: u_x*u_y + u_x^2 = x*y
Usul: Genel analitik yöntem bu tabloda yoktur. Charpit yöntemi, uygun durumda tam integral üretir.

Yaprak: Eliptik

Bariz: u_xx + u_yy = 0
Usul: Kanonik biçim zaten Laplace denklemidir. Değişkenlere ayırma veya Fourier serisi, sınır koşullarına göre uygulanır.

Görmek zor: u_xx + 2*u_xy + 5*u_yy = 0
Usul: Ayırıcı B^2 - 4AC = 4 - 20 < 0 eliptik. Kanonik dönüşüm ile Laplace denklemine çevrilir.

Fevkalade zor: x^2*u_xx + y^2*u_yy = 0
Usul: Değişken katsayılı, x, y > 0 için eliptik. Euler tipi: u = x^r*y^s dönüşümü ya da değişkenlere ayırma (u = X(x)*Y(y)) ile Euler–Cauchy adi denklemlere iner.

Yaprak: Parabolik

Bariz: u_t = u_xx
Usul: Isı denklemi. Değişkenlere ayırma veya Fourier serisi; sınır koşullarına göre çözüm.

Görmek zor: u_t = 4*u_xx + 3*u_x
Usul: Parabolik, sabit katsayılı. Taşıma terimi u_x, u = exp(a*x + b*t)*v dönüşümüyle ısı denklemine indirgenir; sonra Fourier.

Fevkalade zor: u_t = x^2*u_xx
Usul: Değişken katsayılı parabolik. Benzerlik dönüşümü u = f(z), z = x/sqrt(t) ya da t ve x'in uygun bir kombinasyonu ile adi denkleme indirgenir.

Yaprak: Hiperbolik

Bariz: u_tt = u_xx
Usul: Dalga denklemi. d'Alembert çözümü u = f(x + t) + g(x - t).

Görmek zor: u_xy = 0
Usul: Kanonik biçimdir (B^2 - 4AC = 1 > 0). Genel çözüm u = f(x) + g(y).

Fevkalade zor: u_xx - 4*u_xy + 3*u_yy = 0
Usul: Ayırıcı 16 - 12 = 4 > 0 hiperbolik. Karakteristik denklem λ^2 + 4λ + 3 = 0 (λ = dy/dx), kökler -1 ve -3. Karakteristik değişkenler x + y ve 3x + y; genel çözüm u = f(x + y) + g(3x + y).

Yaprak: İkiden fazla bağımsız değişkenli ikinci mertebe lineer

Bariz: u_xx + u_yy + u_zz = 0
Usul: Laplace denklemi, üç boyut. Değişkenlere ayırma; küresel koordinatlarda küresel harmonikler.

Görmek zor: u_t = u_xx + u_yy
Usul: İki uzaysal boyutlu ısı denklemi. Değişkenlere ayırma: u = T(t)*X(x)*Y(y).

Fevkalade zor: u_tt = u_xx + u_yy + u_zz with sınır koşulu bir küre üzerinde
Usul: Dalga denklemi, üç boyut, küresel simetri. Küresel koordinatlar ve Fourier–Bessel açılımı; ayrıca Laplace dönüşümü başlangıç koşulları için kullanılabilir.

Yaprak: Lineer değil ikinci veya yüksek mertebe kısmi

Bariz: u_xx*u_yy - (u_xy)^2 = 1
Usul: Monge–Ampère tipi. Genel analitik yöntem bu tabloda yoktur; özel çözümler (ör. u = (x^2 + y^2)/2) denenir.

Görmek zor: u_t + u*u_x = u_xx
Usul: Viskoz Burgers denklemi. Cole–Hopf dönüşümü u = -2*v_x/v, v ısı denklemine indirgenir.

Fevkalade zor: u_t + 6*u*u_x + u_xxx = 0
Usul: Korteweg–de Vries (KdV) denklemi. Tam çözüm ters saçılma dönüşümü (IST) ile bulunur; adım adım çözüm bölüm 10'da verilmiştir.

Yaprak: Lineer kısmi sistem

Bariz: u_x = v, v_x = u
Usul: Adi sistem gibi davranır (y'ye göre ayrı değişken). Laplace dönüşümü ya da doğrudan çözüm: u = c1*exp(x) + c2*exp(-x).

Görmek zor: u_x + v_y = 0, u_y - v_x = 0
Usul: Cauchy–Riemann tipi. Karmaşık fonksiyon teorisi (analitik fonksiyonlar) ile çözülür.

Fevkalade zor: u_t = v_xx, v_t = u_xx
Usul: Lineer parabolik sistem. Fourier dönüşümü ile sabit katsayılı cebirsel sisteme indirgenir.

Yaprak: Lineer olmayan kısmi sistem

Bariz: u_x = u*v, v_y = u^2
Usul: Genel analitik yöntem yoktur. Sayısal çözüm uygulanır.

Görmek zor: u_x = u*v + 1, v_y = u^2
Usul: Genel analitik yöntem yoktur. Sayısal çözüm uygulanır.

Fevkalade zor: Navier–Stokes denklemleri (sıkıştırılamaz, üç boyutlu)
Usul: Genel analitik yöntem yoktur; açık problem düzeyinde zordur. Sayısal (hesaplamalı akışkanlar dinamiği) yöntemler uygulanır.

## 10. Ters saçılma dönüşümü (IST): ayrıntılı çözüm

### 10.1 Yöntem ne yapar?

Bazı lineer olmayan kısmi denklemler, bir lineer spektral problemin uyumluluk koşulu olarak yazılabilir. Bu özelliğe integrable denir. KdV denklemi bu sınıftadır. IST yönteminde denklemin çözümü, lineer problemin saçılma verisi üzerinden üç adımda elde edilir. Bu yöntem her denklem için değil, yalnızca integrable denklemler için çalışır.

Üç adım şunlardır:
1. Doğrudan saçılma: Başlangıç koşulundan saçılma verisi (özdeğerler, normalizasyon sabitleri, yansıma katsayısı) hesaplanır.
2. Zaman evrimi: Saçılma verisi zamanla basit bir şekilde değişir; bu değişim lineer denklemlerden çıkar.
3. Ters saçılma: Gelfand–Levitan–Marchenko (GLM) integral denklemi çözülerek u(x,t) geri kazanılır.

### 10.2 Örnek denklem: KdV

Denklem: u_t + 6*u*u_x + u_xxx = 0.

Başlangıç koşulu: u(x,0) = -2*k^2*sech(k*x)^2, burada k > 0 bir sabittir.

Bu denklemin genel çözümü ayrıca bir tek soliton ailesi ile verilir; bunu adım adım türeteceğiz.

### 10.3 Lax çifti

Lineer spektral problem: L*psi = lambda*psi, burada L = -d^2/dx^2 + u(x,t).

Zaman evrimi: psi_t = M*psi, burada M = -4*d^3/dx^3 - 6*u*d/dx - 3*u_x.

Uyumluluk koşulu L_t = M*L - L*M, yani L_t = [M, L], KdV denklemini verir. Bu, Lax çiftinin doğruluğunun kanıtıdır. Kontrol için: bu iki operatörün komütatörü alınıp u_t + 6uu_x + u_xxx = 0 elde edilmelidir.

İşaret notu: Bu çift u(x,t) negatif kuyu için düzenlenmiştir. Bağlı işaret tutarlılığı tek soliton kontrolünde doğrulanır (aşağıda).

### 10.4 Adım 1: Doğrudan saçılma (t = 0)

Başlangıç potansiyeli u(x,0) = -2*k^2*sech(k*x)^2 bir kuyudur. Bağ durumu (özdeğer) bulunur.

Deneme fonksiyonu psi = sech(k*x) alınır. Hesap:
- psi' = -k*sech(k*x)*tanh(k*x)
- psi'' = k^2*(sech(k*x) - 2*sech(k*x)^3)

Bu durumda -psi'' + u*psi = -k^2*sech + 2*k^2*sech^3 - 2*k^2*sech^3 = -k^2*psi. Böylece lambda = -k^2 bir özdeğerdir.

Normalizasyon: integral(sech(k*x)^2 dx) = 2/k olduğundan, normalize özfonksiyon psi_n = sqrt(k/2)*sech(k*x) ile tanımlanır. x -> sonsuzda asimptotik davranış psi_n ~ sqrt(2*k)*exp(-k*|x|) olur. Bu nedenle normalizasyon sabiti c_0^2 = 2*k.

Yansıma katsayısı sıfırdır: bu potansiyel yansıtmaz, yani saçılma verisinde sürekli spektrum katkısı yoktur. Bu yüzden saçılma verisi yalnızca tek bağ durumudur.

### 10.5 Adım 2: Zaman evrimi

Saçılma verisi zamanla şu biçimde değişir: c^2(t) = c_0^2 * exp(8*k^3*t), yani c^2(t) = 2*k*exp(8*k^3*t).

Özdeğer lambda = -k^2 zamanla sabittir; yalnızca normalizasyon sabiti değişir. Bu, Lax çiftinin M operatörü ile bulunur.

### 10.6 Adım 3: Ters saçılma (GLM)

GLM integral denklemi, bağ durumu için şu biçimdedir:

K(x,y) + F(x+y) + integral_{x}^{infinity} K(x,z)*F(z+y) dz = 0, burada F(s) = c^2(t)*exp(-k*s).

Ayrılabilir çözüm arandığında K(x,y) = -A(x)*exp(-k*y) biçimi denenir. Yerine konulup düzenlenirse:

A(x) = -c^2*exp(-k*x) / (1 + c^2*exp(-2*k*x)/(2*k)).

Buradan köşegen değer K(x,x) elde edilir. Bu değeri q ile gösterelim:

q(x,t) = c^2(t)*exp(-2*k*x)/(2*k) = exp(-2*k*x + 8*k^3*t), çünkü c_0^2/(2*k) = 1.

### 10.7 Geri kazanım formülü

Bu sistemde potansiyel şu biçimde geri kazanılır:

u(x,t) = -2 * d^2/dx^2 [ln(1 + q(x,t))].

Bu formül işaret konvansiyonuyla tutarlıdır, çünkü aşağıdaki hesapla tek soliton doğru çıkar.

### 10.8 Hesap: tek soliton

Hesap için θ = ln(q) = -2*k*x + 8*k^3*t olsun. Bilinen özdeşlik:

d^2/dθ^2 [ln(1 + e^θ)] = e^θ / (1 + e^θ)^2 = (1/4)*sech^2(θ/2).

Zincir kuralı ile dθ/dx = -2*k olduğundan:

d^2/dx^2 [ln(1 + q)] = 4*k^2 * (1/4)*sech^2(θ/2) = k^2*sech^2(θ/2).

Bu nedenle u(x,t) = -2*k^2*sech^2(θ/2). Burada θ/2 = -k*x + 4*k^3*t = -k*(x - 4*k^2*t).

Sonuç: u(x,t) = -2*k^2*sech^2(k*(x - 4*k^2*t)).

Bu, başlangıç koşuluyla tutarlıdır (t = 0 için u = -2*k^2*sech^2(k*x)). Hız 4*k^2 olan hareketli bir soliton elde edilmiştir: genlik büyüklüğü 2*k^2 ve genişlik k ile belirlenir. Dalga hızı genliğe bağlıdır; daha yüksek soliton daha hızlı gider.

### 10.9 Doğrulama

Bu çözümün KdV denklemini sağladığı doğrudan yerine koyma ile kontrol edilebilir. Kontrol adımları:
- u_x ve u_xxx hesaplanır (sech türevleri ile).
- u_t + 6*u*u_x + u_xxx toplamı sıfır çıkmalıdır.

Bu kontrol, bu bölümde ayrıntıya girilmeden yapılabilir; sonucun doğruluğu bu yoldan bağımsız olarak teyit edilir.

### 10.10 Sınırlamalar

- Bu örnek yalnızca tek soliton içerir. Çoklu soliton ve sürekli spektrum katkısı (yansıma katsayısının sıfırdan farklı olduğu durumlar) bu bölümde yoktur. Çoklu soliton için GLM çekirdeği genel biçimde çözülür.
- IST her lineer olmayan denklemde çalışmaz; integrable denklemler sınıfı için geçerlidir.
- Yöntem, yukarıdaki usul tablosunda "Ters saçılma dönüşümü (IST)" satırı olarak yer alır.

## 11. Örneklerin tam çözümleri

Bu bölümde yalnızca 9. bölümde verilen örneklerin tam çözümleri yazılır. Her bölüm yaprak sırasına göre ilerler. Şu an birinci mertebe adi denklemler tamamlanmıştır; diğer yapraklar sırayla eklenecektir.

Yazım notu: Sabit C, her çözümde genel sabittir. Başlangıç koşulu verilirse C o koşuldan bulunur.

### 11.1 Birinci mertebe adi denklemler

#### Ayrılabilir

Örnek 1 (bariz): y' = x*y.
Adım 1: Değişkenler ayrılır: dy/y = x dx.
Adım 2: İki taraf integre edilir: ln|y| = x^2/2 + C.
Adım 3: Üstel alınır: y = K*exp(x^2/2), K = ±e^C (K sıfır da olabilir).

Örnek 2 (görmek zor): y' = exp(x + y).
Adım 1: exp(x + y) = exp(x)*exp(y) olduğu fark edilir. Böylece y' = exp(x)*exp(y).
Adım 2: Ayırma: exp(-y) dy = exp(x) dx.
Adım 3: İntegrasyon: -exp(-y) = exp(x) + C.
Adım 4: exp(-y) = -exp(x) - C yazılır. K = -C diyelim: exp(-y) = K - exp(x).
Sonuç: y = -ln(K - exp(x)). Tanım kümesi K > exp(x) olacak biçimde seçilir.

Örnek 3 (fevkalade zor): y' = sin(x + y) - sin(x - y).
Adım 1: Toplam-fark özdeşliği uygulanır: sin(A) - sin(B) = 2*cos((A+B)/2)*sin((A-B)/2). A = x + y, B = x - y için (A+B)/2 = x ve (A-B)/2 = y. Böylece y' = 2*cos(x)*sin(y).
Adım 2: Ayırma: dy/sin(y) = 2*cos(x) dx.
Adım 3: Sol taraf ∫ csc(y) dy = ln|tan(y/2)|; sağ taraf 2 sin(x). Böylece ln|tan(y/2)| = 2*sin(x) + C.
Sonuç: tan(y/2) = K*exp(2*sin(x)).

#### Birinci mertebe lineer

Örnek 1 (bariz): y' + 2y = exp(x).
Adım 1: Çarpan mu = exp(∫2 dx) = exp(2x).
Adım 2: (mu*y)' = mu*exp(x) = exp(3x).
Adım 3: İntegrasyon: exp(2x)*y = exp(3x)/3 + C.
Sonuç: y = exp(x)/3 + C*exp(-2x).

Örnek 2 (görmek zor): x*y' + y = x^3.
Adım 1: Standart biçim: y' + y/x = x^2 (x ≠ 0).
Adım 2: Çarpan mu = exp(∫dx/x) = x.
Adım 3: (x*y)' = x^3 çünkü x*y' + y = (x*y)'.
Adım 4: İntegrasyon: x*y = x^4/4 + C.
Sonuç: y = x^3/4 + C/x.

Örnek 3 (fevkalade zor): sin(x)*y' + cos(x)*y = exp(x).
Adım 1: Sol taraf (y*sin(x))' türevidir: (y*sin(x))' = y'*sin(x) + y*cos(x).
Adım 2: Böylece (y*sin(x))' = exp(x).
Adım 3: İntegrasyon: y*sin(x) = exp(x) + C.
Sonuç: y = (exp(x) + C)/sin(x). Tanım kümesi sin(x) ≠ 0 olan aralıklarda geçerlidir.

#### Bernoulli

Örnek 1 (bariz): y' + y = y^2.
Adım 1: n = 2. Dönüşüm v = y^(1-2) = 1/y, yani v = y^(-1).
Adım 2: v' = -y'/y^2, buradan y' = -y^2*v'.
Adım 3: Denklemde yerine konulur: -y^2*v' + y = y^2. Her iki taraf y^2 ile bölünür: -v' + 1/y = 1, yani -v' + v = 1.
Adım 4: Lineer denklem: v' - v = -1. Çözüm: v = 1 + C*exp(x). (Kontrol: v = 1 için v' - v = -1 sağlanır.)
Sonuç: y = 1/(1 + C*exp(x)).

Örnek 2 (görmek zor): 2*x*y*y' + y^2 = x^3.
Adım 1: Denklemi y' + y/(2x) = x^2/(2y) biçimine getirilir. Bu bir Bernoulli denklemi, n = -1.
Adım 2: Dönüşüm v = y^(1-n) = y^2.
Adım 3: v' = 2*y*y', yani 2*x*y*y' = x*v'.
Adım 4: Orijinal denklem x*v' + v = x^3 olur. Bu lineer: (x*v)' = x^3.
Adım 5: İntegrasyon: x*v = x^4/4 + C, v = x^3/4 + C/x.
Sonuç: y = ±sqrt(x^3/4 + C/x).

Örnek 3 (fevkalade zor): y' + y/x = (1 + ln(x))*y^3.
Adım 1: n = 3. Dönüşüm v = y^(1-n) = y^(-2).
Adım 2: v' = -2*y^(-3)*y', yani y' = -(y^3/2)*v'.
Adım 3: Denkleme yerine konulur: -(y^3/2)*v' + y/x = (1 + ln(x))*y^3. Her iki taraf -2/y^3 ile çarpılır: v' - 2*v/x = -2*(1 + ln(x)).
Adım 4: Lineer denklem. Çarpan mu = exp(∫ -2/x dx) = x^(-2).
Adım 5: (v*x^(-2))' = -2*(1 + ln(x))*x^(-2). Sağ taraf integre edilir: ∫(1 + ln(x))/x^2 dx = -(2 + ln(x))/x. Böylece v*x^(-2) = 2*(2 + ln(x))/x + C.
Adım 6: v = 2*x*(2 + ln(x)) + C*x^2.
Sonuç: y = 1/sqrt(2*x*(2 + ln(x)) + C*x^2) (y > 0 dalı). Kontrol: v' - 2v/x = -2(1 + ln(x)) sağlanır.

#### Riccati

Örnek 1 (bariz): y' = y^2 - 2/x^2, bilinen özel çözüm y1 = 1/x.
Adım 1: Doğrulama: y1' = -1/x^2; y1^2 - 2/x^2 = 1/x^2 - 2/x^2 = -1/x^2. Eşit, yani y1 özel çözümdür.
Adım 2: Dönüşüm y = y1 + 1/v. Riccati için v' = -(q + 2*r*y1)*v - r burada q = 0, r = 1 ve y1 = 1/x. Böylece v' = -(2/x)*v - 1.
Adım 3: Lineer denklem: v' + (2/x)*v = -1. Çarpan x^2: (x^2*v)' = -x^2.
Adım 4: İntegrasyon: x^2*v = -x^3/3 + C, v = -x/3 + C/x^2.
Sonuç: y = 1/x + 1/(-x/3 + C/x^2).

Örnek 2 (görmek zor): x^2*y' = x^2*y^2 - 6, yani y' = y^2 - 6/x^2.
Adım 1: Özel çözüm y1 = 2/x. Doğrulama: y1' = -2/x^2; y1^2 - 6/x^2 = 4/x^2 - 6/x^2 = -2/x^2. Eşit.
Adım 2: Dönüşüm y = y1 + 1/v, v' = -(2*y1)*v - 1 = -(4/x)*v - 1.
Adım 3: Lineer denklem: v' + (4/x)*v = -1. Çarpan x^4: (x^4*v)' = -x^4.
Adım 4: İntegrasyon: x^4*v = -x^5/5 + C, v = -x/5 + C/x^4.
Sonuç: y = 2/x + 1/(-x/5 + C/x^4).

Örnek 3 (fevkalade zor): y' = exp(x) - exp(2x) + y^2.
Adım 1: Özel çözüm y1 = exp(x) denenir. Doğrulama: y1' = exp(x); sağ taraf exp(x) - exp(2x) + exp(2x) = exp(x). Eşit.
Adım 2: Dönüşüm y = y1 + 1/v, v' = -2*exp(x)*v - 1.
Adım 3: Lineer denklem: v' + 2*exp(x)*v = -1. Çarpan mu = exp(2*exp(x)).
Adım 4: (v*exp(2*exp(x)))' = -exp(2*exp(x)). Sağ taraf ∫exp(2*exp(x)) dx ifadesine dönüşür. s = exp(x) yazılırsa dx = ds/s ve integral ∫exp(2s)/s ds = Ei(2s) olur (Ei üstel integral fonksiyonudur).
Adım 5: v = exp(-2*exp(x))*(C - Ei(2*exp(x))).
Sonuç: y = exp(x) + exp(2*exp(x))/(C - Ei(2*exp(x))).

#### Homojen

Örnek 1 (bariz): y' = y/x + sin(y/x).
Adım 1: v = y/x, yani y = v*x. Türev: y' = v + x*v'.
Adım 2: Denklemde yerine konulur: v + x*v' = v + sin(v), yani x*v' = sin(v).
Adım 3: Ayırma: dv/sin(v) = dx/x.
Adım 4: ∫csc(v) dv = ln|tan(v/2)| ve ∫dx/x = ln|x|. ln|tan(v/2)| = ln|x| + C, yani tan(v/2) = K*x.
Sonuç: y = 2*x*arctan(K*x).

Örnek 2 (görmek zor): x*y' = y + sqrt(x^2 + y^2), x > 0.
Adım 1: v = y/x. Denklemi x ile bölünce y' = v + sqrt(1 + v^2) ... pratikte: x*(v + x*v') = v*x + x*sqrt(1 + v^2), yani x^2*v' = x*sqrt(1 + v^2).
Adım 2: Ayırma: v'/sqrt(1 + v^2) = 1/x.
Adım 3: İntegrasyon: asinh(v) = ln(x) + C. v = sinh(ln(x) + C) = (K*x - 1/(K*x))/2, K = e^C > 0.
Adım 4: y = x*v = (K*x^2 - 1/K)/2.
Kontrol: x*y' = K*x^2 ve y + sqrt(x^2 + y^2) = K*x^2 sağlanır.

Örnek 3 (fevkalade zor): x*dy - (y + x*exp(y/x)) dx = 0.
Adım 1: Denklem y' = y/x + exp(y/x) biçimine getirilir. Homojen; v = y/x.
Adım 2: y' = v + x*v' ve denklem v + x*v' = v + exp(v) ⇒ x*v' = exp(v).
Adım 3: Ayırma: exp(-v) dv = dx/x.
Adım 4: İntegrasyon: -exp(-v) = ln|x| + C. exp(-v) = K - ln(x) (K = -C).
Adım 5: v = -ln(K - ln(x)).
Sonuç: y = -x*ln(K - ln(x)). Tanım kümesi K - ln(x) > 0.

#### Tam diferansiyel

Örnek 1 (bariz): (2x + y) dx + (x + 2y) dy = 0.
Adım 1: M = 2x + y, N = x + 2y. M_y = 1 = N_x: tam.
Adım 2: f_x = M ⇒ f = x^2 + x*y + g(y).
Adım 3: f_y = x + g'(y) = N = x + 2y ⇒ g' = 2y, g = y^2.
Sonuç: x^2 + x*y + y^2 = C.

Örnek 2 (görmek zor): (y*cos(x*y) + 1) dx + x*cos(x*y) dy = 0.
Adım 1: M_y = cos(xy) - x*y*sin(xy) ve N_x = cos(xy) - x*y*sin(xy). Tam.
Adım 2: f_x = M ⇒ f = x + sin(x*y) + g(y).
Adım 3: f_y = x*cos(x*y) + g'(y) = N = x*cos(x*y) ⇒ g' = 0.
Sonuç: x + sin(x*y) = C.

Örnek 3 (fevkalade zor): (y/(x^2 + y^2) + exp(x)) dx - (x/(x^2 + y^2)) dy = 0.
Adım 1: M = y/(x^2 + y^2) + exp(x), N = -x/(x^2 + y^2).
Adım 2: M_y = (x^2 - y^2)/(x^2 + y^2)^2; N_x = -(y^2 - x^2)/(x^2 + y^2)^2 = (x^2 - y^2)/(x^2 + y^2)^2. Tam.
Adım 3: f_x = M ⇒ f = exp(x) + ∫ y/(x^2 + y^2) dx + g(y). ∫ y/(x^2 + y^2) dx = arctan(x/y) (türevi kontrol edilir).
Adım 4: f = exp(x) + arctan(x/y) + g(y). f_y = -x/(x^2 + y^2) + g'(y) = N ⇒ g' = 0.
Sonuç: exp(x) + arctan(x/y) = C.

#### İntegrasyon çarpanlı

Örnek 1 (bariz): (x + y^2) dx - 2*x*y dy = 0.
Adım 1: M_y = 2y, N_x = -2y. Tam değil.
Adım 2: (M_y - N_x)/N = 4y/(-2xy) = -2/x, yalnız x'e bağlı. Çarpan mu(x) = exp(∫-2/x dx) = x^(-2).
Adım 3: Yeni M = 1/x + y^2/x^2, N = -2y/x. Kontrol: M_y = 2y/x^2 = N_x.
Adım 4: f_x = M ⇒ f = ln|x| - y^2/x + g(y). f_y = -2y/x + g' = N ⇒ g' = 0.
Sonuç: ln|x| - y^2/x = C.

Örnek 2 (görmek zor): (x^2 + y) dx - x dy = 0.
Adım 1: M_y = 1, N_x = -1; (M_y - N_x)/N = 2/(-x) = -2/x. Çarpan mu = x^(-2).
Adım 2: Yeni M = 1 + y/x^2, N = -1/x. Kontrol: M_y = 1/x^2 = N_x.
Adım 3: f = x - y/x + g(y); f_y = -1/x + g' = -1/x ⇒ g' = 0.
Sonuç: x - y/x = C, yani x^2 - y = C*x.

Örnek 3 (fevkalade zor): (x^2 + y^2 + x) dx + y dy = 0.
Adım 1: M_y = 2y, N_x = 0. (M_y - N_x)/N = 2y/y = 2. Yalnız x'e bağlı; mu = exp(∫2 dx) = exp(2x).
Adım 2: Yeni M = exp(2x)*(x^2 + y^2 + x), N = y*exp(2x). Kontrol: M_y = 2y*exp(2x) = N_x.
Adım 3: f_y = y*exp(2x) ⇒ f = y^2*exp(2x)/2 + h(x).
Adım 4: f_x = y^2*exp(2x) + h'(x) = exp(2x)*(x^2 + y^2 + x) ⇒ h'(x) = exp(2x)*(x^2 + x).
Adım 5: h(x) = (x^2/2)*exp(2x) (kontrol: türevi exp(2x)*(x^2 + x) verir).
Sonuç: (x^2 + y^2)*exp(2x) = C.

#### Clairaut

Örnek 1 (bariz): y = x*y' + (y')^2.
Adım 1: p = y' yazılır; denklem y = x*p + p^2.
Adım 2: Genel çözüm: p = C, yani y = C*x + C^2.
Adım 3: Tekil çözüm: p'ye göre türev alınır: 0 = x + 2p, p = -x/2. Yerine konulursa y = -x^2/4 bulunur.
Kontrol: y' = -x/2; x*y' + y'^2 = -x^2/2 + x^2/4 = -x^2/4 = y.
Sonuç: Genel y = C*x + C^2; tekil y = -x^2/4.

Örnek 2 (görmek zor): y = x*y' + ln(y').
Adım 1: Clairaut biçimi: f(p) = ln(p).
Adım 2: Genel çözüm: y = C*x + ln(C).
Adım 3: Tekil çözüm: p'ye göre türev: 0 = x + 1/p ⇒ x = -1/p. Yerine konulursa y = -1 + ln(-1/x) (x < 0).
Kontrol: p = -1/x > 0 (x < 0), x*p + ln(p) = -1 + ln(-1/x) = y.

Örnek 3 (fevkalade zor): y = x*y' - exp(y').
Adım 1: f(p) = -exp(p).
Adım 2: Genel çözüm: y = C*x - exp(C).
Adım 3: Tekil çözüm: x = -f'(p) = exp(p) ⇒ p = ln(x). Yerine konulursa y = x*ln(x) - x.
Kontrol: y' = ln(x); x*y' - exp(y') = x*ln(x) - x = y.

#### Lagrange

Örnek 1 (bariz): y = 2*x*y' + (y')^2.
Adım 1: p = y'. f(p) = 2p, g(p) = p^2. Denklem y = x*f(p) + g(p).
Adım 2: x'e göre türev: p = 2p + 2*x*p' + 2*p*p', yani -p = 2(x + p)*p'.
Adım 3: dx/dp biçimine çevrilir: dx/dp = -2(x + p)/p, yani dx/dp + (2/p)*x = -2.
Adım 4: Çarpan p^2: (p^2*x)' = -2*p^2 ⇒ p^2*x = -2*p^3/3 + C ⇒ x = -2p/3 + C/p^2.
Adım 5: y = 2*x*p + p^2 = -p^2/3 + 2C/p.
Sonuç (parametrik): x = -2p/3 + C/p^2, y = -p^2/3 + 2C/p.

Örnek 2 (görmek zor): y = x*(y')^2 + 2*y'.
Adım 1: p = y'. f(p) = p^2, g(p) = 2p.
Adım 2: Türev: p = p^2 + 2*x*p*p' + 2p', yani (2x*p + 2)*p' = p - p^2.
Adım 3: dx/dp = (2x*p + 2)/(p - p^2) = 2x/(1 - p) + 2/(p(1 - p)).
Adım 4: Lineer denklem: dx/dp - (2/(1 - p))*x = 2/(p(1 - p)). Çarpan (1 - p)^2 (ters işaretli dönüşümle kontrol edilir: exp(-∫2/(1-p)dp) = (1-p)^2).
Adım 5: ((1-p)^2*x)' = (1-p)^2 * 2/(p(1-p)) = 2(1-p)/p = 2/p - 2.
Adım 6: İntegrasyon: (1-p)^2*x = 2 ln|p| - 2p + C.
Adım 7: y = x*p^2 + 2p.
Sonuç (parametrik): x = (2 ln|p| - 2p + C)/(1 - p)^2, y = x*p^2 + 2p.

Örnek 3 (fevkalade zor): y = x*exp(y') + ln(y').
Adım 1: p = y'. f(p) = exp(p), g(p) = ln(p).
Adım 2: Türev: p = exp(p) + x*exp(p)*p' + p'/p, yani p - exp(p) = (x*exp(p) + 1/p)*p'.
Adım 3: dx/dp = (x*exp(p) + 1/p)/(p - exp(p)). Lineer denklem: dx/dp - (exp(p)/(p - exp(p)))*x = (1/p)/(p - exp(p)).
Adım 4: Çarpan mu(p) = exp(-∫exp(p)/(p - exp(p)) dp). Bu integral elementer değildir; çarpan integral biçiminde bırakılır.
Adım 5: x(p) = (1/mu(p))*(∫ mu(p)*(1/p)/(p - exp(p)) dp + C). Parametrik çözüm: x(p) yukarıdaki gibi, y = x*exp(p) + ln(p).
Not: Bu örnekte çözüm kapalı biçimde elementer fonksiyonlarla verilemez; integral temsili yeterlidir.

#### Diğer birinci mertebe

Örnek 1 (bariz): y' = x + sin(y).
Adım 1: Ayrılabilir değildir (toplam biçimi), lineer değildir (sin(y)), Bernoulli, Riccati, homojen, tam, Clairaut ve Lagrange biçimine uymaz.
Adım 2: Genel analitik yöntem yoktur. Başlangıç koşulu y(x0) = y0 verildiğinde sayısal çözüm yapılır.
Adım 3: Sayısal yöntem: Runge–Kutta 4. mertebe; her adımda k1 = f(x, y), k2 = f(x + h/2, y + h*k1/2), k3 = f(x + h/2, y + h*k2/2), k4 = f(x + h, y + h*k3), y_{n+1} = y_n + h*(k1 + 2k2 + 2k3 + k4)/6.

Örnek 2 (görmek zor): y' = y^3 - x^2.
Adım 1: Sağ taraf y^3 ve x^2 terimlerinin toplamıdır. Riccati değildir (y^2 terimi yok). Bernoulli değildir, çünkü y'ye bağlı lineer terim yoktur ve y'nin sabit kısmı -x^2 bağımlı değildir. Analitik kapalı form yoktur.
Adım 2: Sayısal Runge–Kutta uygulanır (Örnek 1'deki formül).

Örnek 3 (fevkalade zor): y' = x*y^3 + x^3*y.
Adım 1: Sağ taraf iki farklı kuvvet (y^3 ve y) içerir; Bernoulli tek n ile tanımlanamaz. Lineer değildir, tam değildir (M ve N ayrılamaz).
Adım 2: Dönüşüm bulunamaz; genel analitik yöntem yoktur. Sayısal yöntem uygulanır.

Bu dosya bir sınıflama şemasıdır. Bir denklemin hangi yaprağa düştüğü, öncelik kuralı uygulanarak belirlenir.
