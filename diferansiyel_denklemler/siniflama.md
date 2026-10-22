# Diferansiyel Denklemlerin Sınıflandırılması

Bu dosya diferansiyel denklemleri dal dal ayırır. Her düğümün alt dalları birbirini dışlar ve üst düzeydeki kümeyi tamamen örter. Bir denklem tam bir yaprağa düşer.

## 0. Kapsam ve öncelik kuralı

Kapsam: bir ya da daha çok bilinmeyen fonksiyonu ve bu fonksiyonların türevlerini içeren, bağımsız değişkenlere göre yazılmış her denklem (ve denklem sistemi).

Öncelik kuralı: Bir denklem birden fazla dala uyuyorsa (örneğin hem ayrılabilir hem Bernoulli tipi) kendisini **dalların yazılış sırasında en önce gelen** dala koyar. Böylece her denklem tek bir yaprağa düşer ve yapraklar çakışmaz.

## 1. Üst düzey ayrım

```
DİFERANSİYEL DENKLEM
├── A. Adi (ADE): bağımsız değişken sayısı = 1
└── B. Kısmi (KDE): bağımsız değişken sayısı ≥ 2
```

Her denklemin bağımsız değişken sayısı 1 ya da en az 2 olduğu için bu ayrım eksiksizdir.

## 2. Adi diferansiyel denklemler (A)

```
A. ADİ DİFERANSİYEL DENKLEM
├── A1. Tek bilinmeyen fonksiyon
│   ├── A1.1 Birinci mertebe
│   │   ├── A1.1.1 Ayrılabilir: y' = f(x)g(y)
│   │   ├── A1.1.2 Lineer: y' + p(x)y = q(x)
│   │   ├── A1.1.3 Bernoulli: y' + p(x)y = q(x)y^n, n ∉ {0, 1}
│   │   ├── A1.1.4 Riccati: y' = p(x) + q(x)y + r(x)y²
│   │   ├── A1.1.5 Homojen (Euler): y' = F(y/x)
│   │   ├── A1.1.6 Tam diferansiyel: M dx + N dy = 0, ∂M/∂y = ∂N/∂x
│   │   ├── A1.1.7 Integrasyon çarpanlı (tam değil, ama μ(x,y) ile tam yapılabilen)
│   │   ├── A1.1.8 Clairaut: y = xy' + f(y')
│   │   ├── A1.1.9 Lagrange: y = x f(y') + g(y')
│   │   └── A1.1.10 Diğer birinci mertebe
│   ├── A1.2 İkinci mertebe
│   │   ├── A1.2.1 Lineer
│   │   │   ├── A1.2.1.1 Sabit katsayılı
│   │   │   │   ├── A1.2.1.1.a Homojen, karakteristik kökler reel ve farklı
│   │   │   │   ├── A1.2.1.1.b Homojen, karakteristik kökler reel ve eşit
│   │   │   │   ├── A1.2.1.1.c Homojen, karakteristik kökler karmaşık eşlenik
│   │   │   │   └── A1.2.1.1.d Homojen olmayan (sağ taraf f(x) ≠ 0)
│   │   │   ├── A1.2.1.2 Euler–Cauchy: x²y'' + axy' + by = f(x), a,b sabit
│   │   │   └── A1.2.1.3 Değişken katsayılı, Euler–Cauchy değil
│   │   └── A1.2.2 Lineer değil
│   │       ├── A1.2.2.1 x açık değil: y'' = F(y, y')
│   │       ├── A1.2.2.2 y açık değil: y'' = F(x, y')
│   │       └── A1.2.2.3 Diğer ikinci mertebe
│   └── A1.3 Üçüncü ve daha yüksek mertebe
│       ├── A1.3.1 Lineer, sabit katsayılı
│       ├── A1.3.2 Lineer, değişken katsayılı
│       └── A1.3.3 Lineer değil
└── A2. Sistem (birden fazla bilinmeyen fonksiyon)
    ├── A2.1 Lineer, sabit katsayılı: X' = AX + F(t), A sabit matris
    │   ├── A2.1.1 Özdeğerleri reel ve farklı
    │   ├── A2.1.2 Özdeğerleri reel ve tekrarlı (köşegenleştirilemeyen dahil)
    │   ├── A2.1.3 Özdeğerleri karmaşık eşlenik
    │   └── A2.1.4 Özdeğer sıfır içeren (A tekil)
    ├── A2.2 Lineer, değişken katsayılı: X' = A(t)X + F(t), A(t) sabit değil
    └── A2.3 Lineer değil: X' = G(t, X)
```

## 3. Kısmi diferansiyel denklemler (B)

```
B. KISMİ DİFERANSİYEL DENKLEM
├── B1. Tek bilinmeyen fonksiyon
│   ├── B1.1 Birinci mertebe
│   │   ├── B1.1.1 Lineer: a·u_x + b·u_y = c·u + d
│   │   ├── B1.1.2 Kuazi-lineer: a(x,y,u)u_x + b(x,y,u)u_y = c(x,y,u)
│   │   └── B1.1.3 Tam lineer ve kuazi-lineer olmayan
│   ├── B1.2 İkinci mertebe, lineer, iki bağımsız değişkenli
│   │   ├── B1.2.1 Eliptik: B² − 4AC < 0        (örnek: Laplace u_xx + u_yy = 0)
│   │   ├── B1.2.2 Parabolik: B² − 4AC = 0      (örnek: ısı u_t = u_xx)
│   │   └── B1.2.3 Hiperbolik: B² − 4AC > 0     (örnek: dalga u_tt = u_xx)
│   ├── B1.3 İkinci mertebe, lineer, ikiden fazla bağımsız değişkenli
│   └── B1.4 İkinci mertebe lineer değil, ve üçüncü ve daha yüksek mertebe
└── B2. Sistem (birden fazla bilinmeyen fonksiyon)
    ├── B2.1 Lineer
    └── B2.2 Lineer değil
```

B1.2 dalındaki ayrım, kısmi türevlerin katsayılarından (A, B, C) hesaplanan ayırıcıya göre yapılır. Bir sayı için sonuç üç durumdan tam biri olduğu için yapraklar eksiksizdir.

## 4. Yaprak listesi (özet)

| Yaprak | Ad | Tanım |
|---|---|---|
| A1.1.1 | Ayrılabilir | y' = f(x)g(y) |
| A1.1.2 | Birinci mertebe lineer | y' + p(x)y = q(x) |
| A1.1.3 | Bernoulli | y' + p y = q y^n, n ∉ {0,1} |
| A1.1.4 | Riccati | y' = p + q y + r y² |
| A1.1.5 | Homojen | y' = F(y/x) |
| A1.1.6 | Tam diferansiyel | M dx + N dy = 0, M_y = N_x |
| A1.1.7 | Integrasyon çarpanlı | μ ile tam hâle getirilebilen |
| A1.1.8 | Clairaut | y = xy' + f(y') |
| A1.1.9 | Lagrange | y = x f(y') + g(y') |
| A1.1.10 | Diğer birinci mertebe | Yukarıdakilerin hiçbiri |
| A1.2.1.1.a–d | Sabit katsayılı ikinci mertebe | Karakteristik kök türüne göre ve homojen olmayan |
| A1.2.1.2 | Euler–Cauchy | x²y'' + axy' + by = f(x) |
| A1.2.1.3 | Değişken katsayılı lineer | Euler–Cauchy değil |
| A1.2.2.1–3 | Lineer olmayan ikinci mertebe | x açık değil / y açık değil / diğer |
| A1.3.1–3 | Üçüncü ve yüksek mertebe | Lineer sabit / lineer değişken / lineer değil |
| A2.1.1–4 | Sabit katsayılı sistem | A matrisinin özdeğer türü |
| A2.2 | Değişken katsayılı sistem | A(t) |
| A2.3 | Lineer olmayan sistem | X' = G(t,X) |
| B1.1.1 | Birinci mertebe lineer KDE | a u_x + b u_y = c u + d |
| B1.1.2 | Kuazi-lineer | En yüksek türevler lineer |
| B1.1.3 | Diğer birinci mertebe | Kuazi-lineer da değil |
| B1.2.1 | Eliptik | B² − 4AC < 0 |
| B1.2.2 | Parabolik | B² − 4AC = 0 |
| B1.2.3 | Hiperbolik | B² − 4AC > 0 |
| B1.3 | İkiden fazla bağımsız değişkenli ikinci mertebe lineer | — |
| B1.4 | Lineer olmayan ikinci veya yüksek mertebe | — |
| B2.1 | Lineer KDE sistemi | — |
| B2.2 | Lineer olmayan KDE sistemi | — |

## 5. Kapsama ve ayrıklık kontrolü

- **Üst ayrım:** Bağımsız değişken sayısı 1 ya da ≥ 2'dir. Ayrım eksiksiz ve çakışmasızdır.
- **A1 / A2:** Bilinmeyen fonksiyon sayısı 1 ya da ≥ 2'dir.
- **A1.1 (birinci mertebe):** Ayrılabilir olanlar önce ayrılır (A1.1.1). Sonra kalan denklemler lineer, Bernoulli, Riccati, homojen, tam, integrasyon çarpanlı, Clairaut ve Lagrange'a sırayla bakılarak atanır. A1.1.10 bu sıralamada kalan her şeyi alır. Böylece yapraklar birbirini dışlar ve kümeyi örter.
- **A1.2 (ikinci mertebe):** Lineer / lineer olmayan ayrımı tam bir bölümlemedir. Lineer dalda katsayıların sabit ya da değişken, Euler–Cauchy biçiminde ya da değil olması ayrımı tamamlar. Homojen olup olmama ve karakteristik kökün türü sabit katsayılı dalı ayrıştırır.
- **A1.3:** Lineer / lineer değil ve katsayıların sabit / değişken olması tam bir bölümlemedir.
- **A2:** Lineer / lineer değil; lineer dalda sabit / değişken katsayı; sabit dalda A matrisinin özdeğer türü ayrımı tamamlar. Özdeğer türleri (reel-farklı, reel-tekrarlı, karmaşık, sıfır) bir matrisin özdeğer kümesini tam olarak böler.
- **B1.2:** B² − 4AC'nin işareti üç durumdan birini verir: < 0, = 0 veya > 0. Yani yapraklar eksiksizdir.
- **B1.1:** Lineer, kuazi-lineer ve diğer; bu üç küme birinci mertebe kısmi denklemleri eksiksiz böler.

## 6. Çözüm yöntemleri (usul tablosu)

Tablo, verilen usul haritasının düzeltilmiş ve genişletilmiş hâlidir. Düzeltmeler tabloda ayrıca işaretlenmiştir.

| Kod | Yöntem | Mertebe | Lineer mi? | Temel şart / tetikleyici |
|---|---|---|---|---|
| YM1 | Değişkenlerine ayırma | Ana kullanım 1. mertebe (bazı yüksek mertebe özel biçimler) | Lineer ve lineer değil | Sağ taraf $f(x)\cdot g(y)$ çarpımına ayrılıyorsa |
| YM2 | Tam diferansiyel / tamlaştırma | 1. mertebe | Lineer ve lineer değil | $M\,dx+N\,dy=0$ ve $\partial M/\partial y=\partial N/\partial x$ |
| YM3 | İntegrasyon çarpanı | 1. mertebe | Lineer ve lineer değil | Tam değilse, $\mu(x)$, $\mu(y)$ ya da $\mu(x,y)$ ile tam hâle getirilebiliyorsa. **Düzeltme:** Eski tabloda "sadece lineer" yazıyordu; bu yanlıştı, çarpan gayr-ı lineer denklemlerde de kullanılır. |
| YM4 | Lineer birinci mertebe (çarpan formülü) | 1. mertebe | Sadece lineer | $y'+P(x)y=Q(x)$; çarpan $\mu=e^{\int P\,dx}$ |
| YM5 | Bernoulli | 1. mertebe | Gayr-ı lineer | $y'+P(x)y=Q(x)y^n$, $n\neq0,1$; $v=y^{1-n}$ dönüşümü |
| YM6 | Riccati | 1. mertebe | Gayr-ı lineer | $y'=p+qy+ry^2$; bir özel çözüm $y_1$ biliniyorsa $y=y_1+1/v$ |
| YM7 | Homojen (Euler) | 1. mertebe | Gayr-ı lineer | $y'=F(y/x)$; $v=y/x$ dönüşümü |
| YM8 | Clairaut ve Lagrange ($p=y'$ parametresi) | 1. mertebe | Gayr-ı lineer | $y=xp+f(p)$ ya da $y=xf(p)+g(p)$ biçimi |
| YM9 | Mertebe indirgeme | 2. ve üstü mertebe | Lineer ve lineer değil | (a) Bir çözüm $y_1$ verilmiş (lineer). (b) $x$ açık değil: $y''=F(y,y')$, $p=y'$, $y$ bağımsız. (c) $y$ açık değil: $y''=F(x,y')$, $p=y'$. **Düzeltme:** Eski tabloda "sadece lineer" yazıyordu; (b) ve (c) lineer olmayan denklemlerde de kullanılır. |
| YM10 | Karakteristik denklem | 2. ve üstü mertebe | Sadece lineer | Katsayılar sabit ($ay''+by'+cy=0$ için $ar^2+br+c=0$) |
| YM11 | Euler–Cauchy dönüşümü ($x=e^t$) | 2. ve üstü mertebe | Sadece lineer | $x^2y''+axy'+by=f(x)$ |
| YM12 | Belirsiz katsayılar | 2. ve üstü mertebe | Sadece lineer | Sabit katsayılı ve sağ taraf polinom, üstel ya da trigonometrik ise |
| YM13 | Parametrelerin değişimi | 2. ve üstü mertebe | Sadece lineer | Homojen olmayan lineer denklem; homojen çözümler biliniyorsa |
| YM14 | Özdeğer ve özvektör | Sistem | Sadece lineer | $X'=AX$, $A$ sabit matris |
| YM15 | Jordan biçimi ve üstel matris | Sistem | Sadece lineer | Tekrarlı özdeğer, köşegenleştirilemeyen $A$ |
| YM16 | Temel matris ve parametrelerin değişimi (sistem) | Sistem | Sadece lineer | $X'=A(t)X+F(t)$, $A(t)$ değişken |
| YM17 | Karakteristik yöntemi (birinci mertebe KDE) | 1. mertebe KDE | Lineer ve kuazi-lineer | $a\,u_x+b\,u_y=c\,u+d$ ya da kuazi-lineer biçim |
| YM18 | Sınıflandırma ve kanonik form | 2. mertebe KDE | Sadece lineer | İki bağımsız değişkenli; $B^2-4AC$ işareti |
| YM19 | Değişkenlere ayırma (Fourier) | KDE | Sadece lineer | $u=X(x)Y(y)$ çarpımı ve homojen sınır koşulları |
| YM20 | Laplace ve Fourier dönüşümü | ODE ve KDE | Sadece lineer | Sabit katsayılı; başlangıç ya da sınır koşulları verilmiş |

## 7. Yöntemlerin yapraklara eşlenmesi

Her yaprağa en az bir yöntem atanır. Yöntemi olmayan yapraklar açıkça "genel analitik yöntem yok" diye işaretlenir; bunlar sayısal ya da özel durum yöntemiyle çözülür.

| Yaprak | Yöntem kodları |
|---|---|
| A1.1.1 | YM1 |
| A1.1.2 | YM4, YM3 |
| A1.1.3 | YM5 |
| A1.1.4 | YM6 |
| A1.1.5 | YM7 |
| A1.1.6 | YM2 |
| A1.1.7 | YM3 |
| A1.1.8 | YM8 |
| A1.1.9 | YM8 |
| A1.1.10 | Genel analitik yöntem yok |
| A1.2.1.1.a–c | YM10 |
| A1.2.1.1.d | YM10, YM12, YM13 |
| A1.2.1.2 | YM11, YM13 |
| A1.2.1.3 | YM13 (temel çözüm biliniyorsa); aksi hâlde genel analitik yöntem yok |
| A1.2.2.1 | YM9 (b) |
| A1.2.2.2 | YM9 (c) |
| A1.2.2.3 | YM9 (uygunsa); genel analitik yöntem yok |
| A1.3.1 | YM10, YM12, YM13 |
| A1.3.2 | YM13 (temel çözüm biliniyorsa); aksi hâlde genel analitik yöntem yok |
| A1.3.3 | Genel analitik yöntem yok |
| A2.1.1 | YM14 |
| A2.1.2 | YM14, YM15 |
| A2.1.3 | YM14 |
| A2.1.4 | YM14 |
| A2.2 | YM16 |
| A2.3 | Genel analitik yöntem yok |
| B1.1.1 | YM17 |
| B1.1.2 | YM17 |
| B1.1.3 | Genel analitik yöntem yok |
| B1.2.1 | YM18, YM19, YM20 |
| B1.2.2 | YM18, YM19, YM20 |
| B1.2.3 | YM18, YM19, YM20 |
| B1.3 | YM19 (ayrılabiliyorsa); aksi hâlde genel analitik yöntem yok |
| B1.4 | Genel analitik yöntem yok |
| B2.1 | YM19, YM20 (uygunsa) |
| B2.2 | Genel analitik yöntem yok |

## 8. Kapsama kontrolü (yöntemler için)

- Her yaprak ya bir yöntem koduna ya da "genel analitik yöntem yok" işaretine sahiptir. Başka durum yoktur.
- Yöntem tablosundaki her kod en az bir yaprağa bağlanmıştır: YM1 (A1.1.1), YM2 (A1.1.6), YM3 (A1.1.2, A1.1.7), YM4 (A1.1.2), YM5 (A1.1.3), YM6 (A1.1.4), YM7 (A1.1.5), YM8 (A1.1.8, A1.1.9), YM9 (A1.2.2.1–3), YM10 (A1.2.1.1, A1.3.1), YM11 (A1.2.1.2), YM12 (A1.2.1.1.d, A1.3.1), YM13 (A1.2.1.1.d, A1.2.1.2, A1.2.1.3, A1.3.1, A1.3.2), YM14 (A2.1), YM15 (A2.1.2), YM16 (A2.2), YM17 (B1.1.1, B1.1.2), YM18–YM20 (B1.2, B1.3, B2.1).
- Öncelik kuralı yöntemler için de geçerlidir: bir denklemin hangi yöntemle çözüleceği, denklem yapraklara düştükten sonra, yaprağın ilk yazılan yöntemiyle belirlenir.

Bu dosya bir sınıflama şemasıdır. Bir denklemin hangi yaprağa düştüğü, öncelik kuralı uygulanarak belirlenir.
