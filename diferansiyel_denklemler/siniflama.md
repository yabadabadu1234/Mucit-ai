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

Bu dosya bir sınıflama şemasıdır. Bir denklemin hangi yaprağa düştüğü, öncelik kuralı uygulanarak belirlenir.
