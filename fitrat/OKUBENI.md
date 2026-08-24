# fitrat — tabii denge, ayrışma ve hüküm motoru

`mizan` mantığın *sûretini* tartar; `fitrat` ise **delilin kendisini**:
denge nerede kurulur, hangi değişken hangisinden ayrıktır, bir tahminin
sürprizi ne kadardır, şahitler birbirini gerçekten mi teyit ediyor, ve
elde ne varken hüküm vermek meşrudur.

| modül | satır | ne yapar |
|---|---:|---|
| `denge.py` | 379 | çok failli muvazene, sönümlü Newton, örtük fonksiyon teoremiyle hassasiyet |
| `ayrisma.py` | 480 | d-ayrışması (Bayes topları), arka kapı, ön kapı, B-ayrışması |
| `serbest_enerji.py` | 322 | ELBO/serbest enerji sınırı, ayrışım kimliği, Gauss kapalı formları |
| `tevafuk.py` | 283 | şartlı-bağımsızlıkla ağırlıklandırılmış şahit teyidi |
| `havuz.py` | 319 | şüphe uzayı, log-uzayı Bayes, karantina ve hüküm |
| `test_fitrat.py` | 555 | 62 test |

## Ölçülen neticeler

**Denge.** 4 firmalı Cournot dengesi 2 Newton adımında bulundu; kapalı
çözümden farkı `2.2e-16`. Asimetrik maliyetlerde de kapalı çözümle
`2.2e-16` uyum. Hassasiyet `∂x*/∂θ` iki bağımsız yoldan hesaplandı —
örtük fonksiyon teoremi ve dengeyi yeniden çözerek — azamî farkları
`1.8e-10`; ikisi de kapalı türevlerle (`−n/(b(n+1))` ve `1/(b(n+1))`)
tutuyor. `∂ₓF` tekil olduğunda sayı **uydurulmuyor**, `None` dönüyor.

**Eşzamanlı en iyi karşılık n=4'te ıraksıyor** — ve bu bir kusur değil:
Jacobi'nin spektral yarıçapı `(n−1)/2 = 1.5 > 1`. Sönüm konunca
(κ=0.5 veya 0.3) 22 adımda Newton'un vardığı noktaya `9.1e-14`
yakınlıkta yakınsıyor.

**Ayrışma.** d-ayrışması iki ayrı usulle hesaplanıyor: Bayes topları
`O(V+E)` ve bütün yolları dolaşma (üstel). **500 rastgele sorguda 0
uyuşmazlık**. Çarpışma kaidesi doğru işliyor: `A→B←C`'de `A⫫C` doğru
ama `A⫫C|B` yanlış — şarta bağlamak bağımsızlığı bozuyor; `B`'nin
*çocuğuna* bağlanmak da bozuyor. Karıştırıcılı çizgede tek uygun arka
kapı kümesi `{Z}`; ardıla (`M`) bağlanmak reddediliyor. Gözlenmemiş
karıştırıcı varken hiçbir arka kapı kümesi yok ama **ön kapı** açık.

**Serbest enerji.** `F ≥ −ln p(x)` sınırı 2000'er rastgele `q` ile
üç ayrı `x` için sınandı: **0 ihlal**. Eşitlik yalnız tam ardılda
(`2.2e-16`). Boşluğun tam olarak `KL(q‖p(z|x))` olduğu 200 örnekte
`1e-10` içinde doğrulandı — bu, sınırın ispatındaki özdeşliğin
kendisidir. `F = kesinsizlik + karmaşıklık` ayrışımının sapması her
örnekte `0.00e+00`. Gauss hâlinde kapalı formüllerle aynı özdeşlik
200 rastgele parametrede tutuyor.

**Tevâfuk.** 5 şahit, 4000 müşahede, her birinin doğruluğu 0.80:

| ortak kaynak | ağırlıksız tevâfuk | muteber şahit | fazla sayma |
|---:|---:|---:|---:|
| 0.0 | +0.361 | 4.96 | 1.008 |
| 0.2 | +0.280 | 4.77 | 1.049 |
| 0.5 | +0.343 | 3.90 | 1.281 |
| 0.8 | +0.655 | 2.40 | 2.083 |
| 1.0 | +1.000 | 1.00 | 5.000 |

Ham uyuşma **tekdüze değil** — önce düşüyor sonra 1'e tırmanıyor;
sebebi ölçülebilir (az miktarda ortak kaynak, şahitlerin bir kısmını
hükümle alâkasız bir işarete çevirip uyuşmayı seyreltiyor). Muteber
şahit sayısı ise tekdüze düşüyor. Aranan hassasiyet budur: ham uyuşma
yanıltır, **hüküm verildikten sonra kalan bağıntı** yanıltmaz.
Tam bağımlı hâlde 5 şahit fiilen 1 şahide iniyor.

**Havuz.** Üç izahlı şüphe uzayında dört anormal okumadan sonra hüküm
karantinadan kabule geçiyor. Yüksek ardıl tek başına yetmiyor: iki
hipotez 0.599/0.401 iken ardıl eşiği aşılsa da ayrışma eşiği
aşılmadığı için hüküm **karantina**. Altı delilden sonra kabule varılmış
bir dosyaya **sonradan yeni bir izah eklenince** hüküm karantinaya
düşüyor (0.884 → 0.574) — şüphe uzayı eksikken varılan kesinlik
sahteydi.

Log uzayının değeri ölçülerek gösterildi: ham çarpımda payda ilk defa
**n≈7060** delilde sıfırlanıyor (`0.2·0.9^7060 = 0`), orada ardıl 0/0 =
NaN olur ve hiçbir uyarı vermez. Log uzayında böyle bir sınır yok; taşmayan
bölgede (n=50) iki hesabın neticesi `1e-12` içinde aynı — yani hızlanma
neticeyi değiştirmiyor.

## Formüllerin kuruluşuna dair dört not

**Merkezî fark adımı koordinat başına ölçekleniyor.**
`h_j = ε^{1/3}·max(1,|x_j|)`. Sabit bir `h`, büyük ve küçük koordinatlar
bir aradayken birinde kesme, diğerinde yuvarlama hatası doğurur. Ayrıca
bölen olarak istenen `h` değil, kayan noktada **fiilen gerçekleşen** fark
(`x⁺_j − x⁻_j`) kullanılıyor.

**Bayes toplarında yürüyüş düğüm değil, (düğüm, geliş yönü) çifti
üzerinde.** Bir düğümden devam edilip edilemeyeceği oraya yukarıdan mı
aşağıdan mı gelindiğine bağlı. Bu modülün ilk hâlinde başlangıç düğümü
"ebeveyninden gelinmiş" sayılıyordu; o hâlde `X ← Z → Y` çatalı hiç
görünmüyor ve **bütün karıştırıcılar kayboluyordu**. Hata, yol sayımıyla
çapraz sağlamada 300 sorgunun 79'unda ortaya çıktı ve öyle bulundu.

**Tevâfuk toplamı `k < l` üzerinden.** Her çift bir kere sayılır, hiçbir
delil kendisiyle tevâfuk etmiş olmaz, ve `2/(m(m−1))` normalizasyonuyla
ölçü delil sayısından bağımsız olarak `[−1,1]`de kalır. Tek şahitte
tevâfuk **sıfır değil, tanımsızdır** (`None`) — ikisi ayrı şeydir.

**`logsumexp` azamî terimi dışarı alır.** `ln Σ e^{aᵢ} = m + ln Σ e^{aᵢ−m}`.
Üsler `≤ 0` olduğundan taşma imkânsız; en az bir terim tam `e⁰ = 1`
olduğundan alttan taşma toplamı sıfırlayamaz.

## Hız

| modül | süre |
|---|---:|
| `denge` | 0.110 s |
| `ayrisma` | 0.053 s |
| `serbest_enerji` | 0.215 s |
| `tevafuk` | 0.135 s |
| `havuz` | 0.143 s |

Test takımının tamamı **0.73 s** (62 test).

## Çalıştırma

```
python3 -m fitrat.denge        # ve diğer dört modül
python3 -m pytest fitrat/test_fitrat.py -q
```
