# token_uzaylari — token manifoldları, morfizmler ve B-spline KAN

Token uzayını düz bir vektör yığını değil, üzerinde metrik taşıyan bir
**manifold** olarak ele alır. Bütün geometrik büyüklükler metrikten
türetilir; hiçbiri elle verilmez.

| modül | satır | ne yapar |
|---|---:|---|
| `manifold.py` | 359 | metrik, Christoffel, Riemann, Ricci, skaler eğrilik, Laplace–Beltrami |
| `morfizm.py` | 304 | itme/çekme, metrik çekme, funktoryellik, izometri/konformallik |
| `kan_spline.py` | 439 | Cox–de Boor B-spline temeli, KAN kenarı, katman, ağ |
| `test_token_uzaylari.py` | 409 | 62 test |

## Ölçülen neticeler

Geometride "çalışıyor gibi görünmek" ucuzdur: tek bir işaret hatası
bütün tabloyu **tutarlı ama yanlış** kılar. Bu yüzden ölçüt hep
bağımsız olarak bilinen cevaba göre.

**Eğrilik.** Düz uzayda (n=1..4) Christoffel, Riemann ve skaler eğriliğin
hepsi tam `0`. `r` yarıçaplı 2-kürede `K = 1/r²` ve `R = 2/r²`,
r = 0.5, 1, 2, 3 için `1e-5` bağıl hassasiyetle. Hiperbolik düzlemde
dört ayrı noktada `K = −1`, `R = −2`. Aynı formül kürede pozitif,
hiperbolikte negatif veriyor — işaret konvansiyonu sabit.

**Riemann'ın dört simetrisi** (çift antisimetri ×2, çift değişimi,
birinci Bianchi) küre, hiperbolik ve düz metriklerde `1e-5`in altında
bağıl ihlalle sağlanıyor. Christoffel alt iki indiste simetrik
(burulmasızlık), Ricci simetrik.

**Laplace–Beltrami iki ayrı yoldan** hesaplanıyor — diverjans formu ve
Christoffel formu — üç manifoldda da `1e-4` içinde uyuşuyorlar. Düz
uzayda alelâde Laplasyen'e iniyor (kapalı formla `1e-5` içinde). Sabit
fonksiyonun Laplasyeni her manifoldda `1e-6`nın altında.

**Funktoryellik.** `d(ψ∘φ) = dψ·dφ` bağıl sapması üç ayrı noktada
`1e-8`in altında. Çekmede sıra **tersine dönüyor** ve `(ψ∘φ)^* = φ^*∘ψ^*`
`1e-8` içinde tutuyor. Yanlış sıra (`ψ^*∘φ^*`) denendiğinde sayısal bir
sapma değil doğrudan **tip hatası** veriyor — yani sessizce yanlış sayı
üretemiyor.

**İzometri v konformallik** ayırt ediliyor: dönme ikisi de (λ=1.0000),
×2.5 konformal ama izometri değil (λ=6.2500 sabit), `(x²,y)` ikisi de
değil (λ sabit değil). Çarpım morfizminin Jacobi'si tam blok köşegen —
köşegen dışı bloklar `0.000e+00`.

**B-spline.** Birliğin bölünmesi `Σᵢ Bᵢₖ(t) = 1`, altı ayrı `(G,k)`
çiftinde `4.4e-16`nın altında sapmayla. Temel hiçbir yerde negatif
değil. Yerellik ölçüldü: derece `k` temelinin desteği tam `k+1` düğüm
aralığı (k=0..4 için `±0.02` içinde). Kapalı form türev, merkezî farkla
`1e-7`nin altında uyuşuyor.

Uydurma artıkları (400 nokta, kübik):

| fonksiyon | G=5 | G=10 | G=20 | G=40 |
|---|---:|---:|---:|---:|
| sin(3t) | 2.14e-03 | 9.78e-05 | 5.52e-06 | 3.36e-07 |
| \|t\| | 2.42e-02 | 5.02e-03 | 1.77e-03 | 6.17e-04 |
| t³−t | 9.33e-06 | 5.20e-07 | 3.16e-08 | 3.61e-09 |

Köşeli `|t|` beklendiği gibi çok daha yavaş yakınsıyor. `t³−t`'deki
9.3e-06'lık artık ilk bakışta şaşırtıcı — kübik spline kübiği tam
temsil etmeli. Sebebi ölçülerek bulundu: düzenleme terimi değil (0'a
indirince değişmiyor), `uydur`un önce **silu tabanını çıkarması**;
spline'a kalan `t³−t−silu(t)` kübik değil. Taban kapatılınca artık
`3.4e-09`'a düşüyor.

## Hız

**Paylaşılan temel dizeyi.** Bir KAN katmanında bütün kenarlar aynı
ızgarayı kullandığından temel, **girdi kanalı başına bir kere**
hesaplanıp bütün çıktı kanalları için tekrar kullanılır. 12→24 katman,
2000 örnek:

| yol | süre |
|---|---:|
| paylaşımlı temel | 17.13 ms |
| kenar başına naif | 260.90 ms |

**15.2× hızlanma**, iki yolun azamî farkı `5.6e-16` — yani hızlanma
neticeyi değiştirmiyor. Bu, testte de ayrıca sınanıyor
(`test_katman_paylasimli_temel_naifle_ayni_netice`).

Modül raporlarının süreleri: `manifold` 0.100 s, `morfizm` 0.115 s,
`kan_spline` 0.428 s. Test takımı **0.55 s** (62 test).

## Formüllerin kuruluşuna dair üç not

**Kesit eğriliğinde daralma sırası.** `R^ρ_{σμν}` konvansiyonunda `μν`
"hangi iki yön" slotları, `σ` üzerine etki edilen argümandır; o hâlde
`⟨R(u,v)v, u⟩` daralması `u^ρ v^σ u^μ v^ν` sırasını verir. `u,v,v,u`
yazmak — ki ilk hâlde öyle yazılmıştı — `R`nin son çift antisimetrisi
yüzünden işareti tersine çevirir ve **küreyi negatif eğrilikli
gösterir**. Skaler eğrilik doğru çıkmaya devam ettiği için hata
yalnız küre/hiperbolik sağlamasında yakalandı.

**Christoffel'de indisler doğrudan `∂_k g_{ij}` tensöründen okunur.**
Ara bir transpoze almak, `∂_i g_{jl}` yerine `∂_l g_{ij}` koyar ve
bütün eğrilikleri bozar. İlk hâlde bu hata vardı; Riemann simetrileri
testinde bağıl ihlal `1.00e+00` çıkarak yakalandı.

**Cox–de Boor'da sıfır payda terimi atlar.** Tekrarlı düğümlerde limit
budur; sıfıra bölünüp `nan` üretilmez. Sağ uç ayrıca kapalı sayılır,
yoksa tam sınırda bütün temel sıfırlanır ve birliğin bölünmesi orada
`0` verir.

## Çalıştırma

```
python3 -m token_uzaylari.manifold      # ve diğer iki modül
python3 -m pytest token_uzaylari/test_token_uzaylari.py -q
```
