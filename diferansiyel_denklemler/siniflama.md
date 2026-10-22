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
| Lineer olmayan ikinci veya yüksek mertebe kısmi | Genel analitik yöntem yok |
| Lineer kısmi sistem | Değişkenlere ayırma (Fourier) ve Laplace ve Fourier dönüşümü, uygunsa |
| Lineer olmayan kısmi sistem | Genel analitik yöntem yok |

## 8. Kapsama kontrolü (yöntemler için)

- Her yaprak ya bir ya da daha çok adlandırılmış yönteme bağlıdır ya da "genel analitik yöntem yok" işaretine sahiptir. Başka durum yoktur.
- Tabloda adı geçen her yöntem en az bir yaprağa bağlanmıştır.
- Bir denklem yapraklara düştükten sonra, yöntem seçimi o yaprağın listesindeki ilk uygun yönteme göre yapılır.

Bu dosya bir sınıflama şemasıdır. Bir denklemin hangi yaprağa düştüğü, öncelik kuralı uygulanarak belirlenir.
