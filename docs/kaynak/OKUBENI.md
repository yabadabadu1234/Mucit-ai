# docs/kaynak — kaynak risaleler ve tashihleri

Projenin dayandığı 13 risale, **dokunulmamış hâlleriyle** bu dizinde
duruyor. Tashihli nüshalar `tashihli/` altındadır; hiçbiri elle
düzenlenmez, `tashih.py` kaydından üretilir.

```
python3 docs/kaynak/tashih.py               # tashihli nüshaları üretir + cetveli yazar
python3 docs/kaynak/tashih.py --cetvel      # cetveli basar
python3 docs/kaynak/test_tashih.py          # 8 sınama
python3 docs/kaynak/tex_denetle.py docs/kaynak/*.tex     # yapı denetimi
```

## Ne yapıldı

Metinlerdeki formüller tek tek denetlendi ve **125 tashih** uygulandı.
Her tashih bir veri kaydıdır: hangi dosya, hangi metin, yerine ne, ve
**niçin**. Böylece düzeltme kaynağa birebir uygulanabilir, tam olarak bir
kere eşleştiği sınanabilir, ve cetvel elle değil kayıttan üretilir.

Ayrıca 41-meleke nüshasına **35 eksik denklem** eklendi (aşağıda).

| tür | adet |
|---|---|
| tip / ulam hatası | 48 |
| mantıkî denklik hatası | 33 |
| tanımsız ifade | 21 |
| boyut uyuşmazlığı | 8 |
| **derlemeyi kıran yapı hatası** | 6 |
| erişilemez eşik | 3 |
| işaret hatası | 3 |
| kendi tanım kümesinde özdeş sıfır | 2 |
| **sağlamlık hatası** | 1 |
| **toplam** | **125** |

Gerekçelerin tamamı: **`TASHIH_CETVELI.md`**.

## Ölçüt

Buraya yalnız **gösterilebilir** hatalar alındı: tip/boyut uyuşmazlığı,
işaret hatası, tanımsız veya erişilemez ifade, mantıkî denklik hatası, bir
ifadenin kendi tanım kümesinde özdeş olarak sıfırlanması, ve derlemeyi
kıran yapı hataları. Üslûp tercihleri, gösterim alışkanlıkları ve
modelleme seçimleri **alınmadı** — onlar hata değildir.

## En mühim altı bulgu

**1. İki metin hiç derlenmiyordu.** `mizan_i_muhakemat.tex` ve
`mizan_zeyl.tex` içinde üç yerde `\end{align">` yazılmış; LaTeX bunu ortam
kapanışı saymaz. Ayrıca üç yerde markdown başlığı (`\## 1. ...`) LaTeX'e
sızmış. Bu makinede TeX kurulu olmadığı için `tex_denetle.py` yazıldı ve
hatayı `\begin{align} (satır 323) ile \end{document} uyuşmuyor` diye
yakaladı.

**2. Sağlamlık hatası: `hcomp` tabana indirgenmiyor.** Token-uzayları
risalesi `hcomp^i 𝒳 […] u₀ ⟶ u₀` diye bir indirgeme kuralı koyuyor.
Bu kural **sağlam değildir** ve bu depoda makineyle çürütüldü:
`omega_kategori` çekirdeğinde bir ara kurulmuştu, `isoToEquiv`'in kare
inşasını bozdu (`fill0 1 1`, `x₀` yerine `g(f x₀)` verdi) ve `ℤ`
üzerindeki bütün dolgular çöktü. `hcomp`, tarifi gereği `φ` üzerinde `u`'ya
eşit olmalıdır; `u₀`'a indirgemek tam olarak o sınır şartını kırar.

**3. Tasdik mührü erişilemez bir eşikteydi.** `T = σ(CosSim − Tenakuz)`
ve `𝟙 = 𝕀(T ≥ 1−ε)`. `CosSim ≤ 1`, `Tenakuz ≥ 0` olduğundan
`T ≤ σ(1) = 0.731`; `ε = 0.05` için eşik `0.95`. Yani mühür **hiçbir zaman
vurulamaz**. Aynı kusur 𝒪₃₀ Tahkik'te de var. Kazanç katsayısı `β_T ≥ 4`
eklendi.

**4. Çelişki çekirdeği iki şartı birden sağlamalı.** Tenakuzun tarifi iki
şey dayatır: hiçbir önerme kendisiyle çelişmez, **ve** her önerme kendi
nakîziyle çelişir. Kısıtsız `W` ikisini de vermez; **ters simetrik** `W`
birincisini verir ama ikincisini yıkar (`SᵀW(−S) = 0`). Yarı-negatif
`W = −AᵀA` ikisini birden sağlar. Bu, `nefs` modülünde önce yanlış kurulup
sınamayla yakalanan ve ölçümle düzeltilen hatadır.

**5. Dört silojizm varlık faraziyesi olmadan geçersiz.** Darapti,
Felapton, Bamalip, Fesapo iki tümel öncülden tikel netice çıkarır; orta
terim (Bamalip'te büyük terim) boş ise öncüller boşluktan doğru, netice
yanlıştır. Aristo bu kabulü zımnen yapar; yüklem mantığında **yazılmak**
zorundadır. Aynı şart aks-i müstevîde de düşmüş.

**6. Tümevarım formülü "çok örnek gördüm, öyleyse kesindir" safsatasını
formüle ediyordu.** `P(∀x∈K, P(x)) = 1 − ∏(1−pᵢ)` bağımsız olayların **en
az birinin** gerçekleşme olasılığıdır; ve `k → ∞` iken her `pᵢ` ne kadar
küçük olursa olsun 1'e gider. Laplace'ın ardıllık hesabıyla değiştirildi:
`(k+1)/(N+1)`, ki ancak `k = N` iken 1 olur — bu da metnin kendi
"istikra-i tâmm kesindir, nâkıs değildir" ayrımını riyazî olarak görünür
kılar.

## Metinlerin birbiriyle çelişip birinin doğru olduğu yerler

Bunlarda tashih, **aynı külliyatın kendi doğru satırına** dayandı:

| mesele | yanlış olan | doğru olan |
|---|---|---|
| Burhanın kesinliği | Mîzân (şekil geçerliliği düşmüş) | Zeyl (Gazâlî mîzânı) |
| Zannî netice sınırı | Mîzân (`> 0.5`) | Zeyl (Adams sınırı) |
| Modal `5` aksiyomu | Genişletilmiş (`α ⟹ □◇α` = B) | Mîzân (`◇α ⟹ □◇α`) |
| `hLevel` sayımı | 5 yerde `Truncate_{hLevel 0}` | Mantık nöronları §2.1 |
| Liouville akışı | Sorgu uzayı (hacim değişiyor) | Mantık nöronları (`div X_H = 0`) |
| Tefsir dikkati | Küllî nüsha (değer çarpanı yok) | 41-meleke nüshası |

## 41-meleke nüshası: eksik denklemler

Özet "450'den fazla", kapanış "11'er denklemle tanımlanan" diyordu.
Sayım yapıldı: **yalnız ilk altı meleke 11 taşıyor**, kalan 35'i 10;
toplam 451 değil **416**.

İddiayı 416'ya çekmek yerine eksik denklemler tamamlandı, çünkü denetim
zaten her melekede **aynı cinsten** bir denklemin eksik olduğunu
gösterdi: değer aralığı, normalizasyon yahut iyi tanımlılık şartı. Bu
şartlar yazılmadan yukarıdaki tashihlerin çoğu (erişilemez eşik, sınırsız
skor, normalize olmayan olasılık) zaten **tespit edilemezdi**. Tashihli
nüsha 451 denklem taşıyor ve `test_tashih.py` her melekede tam 11
olduğunu doğruluyor.

## Kendi araçlarımda bulduğum iki hata

Denetleyiciyi de denetlemek gerekti; ikisi de yanlış alarm veriyordu:

* `\leftarrow` ve `\leftrightarrow` de `\left` ile başlar. Sözcük sınırı
  konmadan üç dosyada **olmayan** `\left/\right` dengesizliği bildirildi.
* `cases` içindeki `\\` satır sonu, `&` ise sütun ayracıdır. İç ortamlar
  düşürülmeden sayılınca hem denklem sayımı şişti (416 yerine 419) hem de
  tek satıra sığdırılmış bir `cases` bloğu "2 hizalama işareti" diye
  bildirildi. Düşürme, satır sonuna göre bölmeden **önce** yapılmalı.

## Durum

```
125 tashih · 35 eklenen denklem · 13 dosya
8 sınamanın 8'i geçiyor
tashihli nüshaların 13'ü de yapı denetiminden geçiyor
```
