# MELEKE HARİTASI VE DARBOĞAZ TENSİP-TAKDİRİ

> Bu harita **okunarak ve ölçülerek** çıkarıldı; hiçbir satırı hafızadan
> yazılmadı. Her sayı bu makinede, `KISA_CPU` profiliyle (B=128, d=4096,
> lif (16,16,16), n_satir=2, satir_kubiti=16) fiilen ölçüldü.

---

## FASIL 0: EN EVVEL BİLİNMESİ GEREKEN -- İKİ MELEKE KATMANI VAR, BİRİ HİÇ KOŞMUYOR

`nefs/melekeler.py` (6 040 satır) **iki ayrı meleke takımı** barındırıyor:

| katman | sınıf | adet | satır aralığı | ana hatta koşuyor mu |
| :-- | :-- | --: | :-- | :-- |
| **Klasik** | `Meleke` | 41 | 1446–3900 | **HAYIR — sıfır çağrı** |
| **Kuantum** | `QMeleke` | 44 | 4216–5660 | **EVET — geçiş başına 45 çağrı** |

Ölçüldü (tek `idrak_et` geçişi, `kosu` sayaçlanarak):

```
klasik Meleke.kosu  = 0
QMeleke.kosu        = 45      (𝒪13 Tasdik iki kere koşar)
```

Klasik katmanın tek çağrıldığı yerler: `nefs/kulli_kayip.py`'nin
`ne="iz"` ve `ne="tesir"` tanı kipleri ile `nefs/test_nefs.py`.
Yâni **tâlim ve çıkarım hattında hiç koşmuyor**.

Bu, ~2 450 satırlık bir katmanın ölü olması demektir. Klasik katman
`Durum` üstünde numpy ile çalışır (S, X, E, A_neden…); kuantum katman
`QYazmac` üstünde kapı vurur. İkisi **aynı isimleri** taşır fakat aynı
şeyi yapmazlar — karışıklığın kaynağı budur.

> **Karar sizindir:** klasik katman ya bir vazifeye bağlanmalı ya da
> ferman 2-B gereği kökünden kesilmelidir. Ben kendiliğimden silmedim.

Ayrıca `main/egitim.py`'nin `melekeleri_kur(44)` çağrısı bu iki katmanın
**hiçbiri** değildir: o, dalga hattının `KulliMelekeManifoldu`sudur
(bir Hamiltonyen manifoldu) ve tahtın kendi şerhi o hattın
"öğrenmediğini" söyler.

---

## FASIL 1: DARBOĞAZ HARİTASI -- YUKARIDAN AŞAĞI, HER KADEME ÖLÇÜLDÜ

### 1. kademe: küllî mizan (1,53 sn / çağrı)

| kalem | sn | pay |
| :-- | --: | --: |
| **`_ileri` (4 × `idrak_et`)** | **1,2895** | **84,5 %** |
| `_monogami` | 0,0974 | 6,4 % |
| `engellenme` (CIM/ayna) | 0,0771 | 5,0 % |
| diğer (Uhlmann, hafıza, gölge…) | 0,0358 | 2,3 % |
| `_laplasyen` | 0,0237 | 1,6 % |
| `_cevrimleri_tara` (Wilson) | 0,0030 | 0,2 % |

**Hüküm:** kaybın kendisi (Wilson, monogami, Hodge, engel) toplam
%13,2'dir. Kalan %84,5 **ileri geçiştir**. Kaybı hızlandırmanın
kazancı sınırlıdır; iş `idrak_et`tedir.

### 2. kademe: idrak_et (0,23 sn / geçiş, B=128)

| kalem | sn | pay |
| :-- | --: | --: |
| **44 QMeleke** | **0,1379** | **60,0 %** |
| `vicdan` (her melekeden sonra, 45 kere) | 0,0485 | 21,1 % |
| kodla + superpozisyon + mera + gaye_kos + normalize | 0,0434 | 18,9 % |

### 3. kademe: melekeler içinde — ALTI MELEKE %54

| 𝒪 | ad | sn | pay | ne yapıyor |
| --: | :-- | --: | --: | :-- |
| 7 | Mana | 0,0456 | 19,8 % | `mpo_topla("tasdik")` |
| 21 | Tefekkür | 0,0337 | 14,7 % | `tek_yigin` + `mpo_topla("makam")` |
| 30 | Tahkik | 0,0199 | 8,7 % | `mpo_topla("tasdik", j=1)` |
| 11 | Tenakuz | 0,0127 | 5,5 % | `mpo_topla("tenakuz")` |
| 34 | Tafsil | 0,0073 | 3,2 % | `mpo_dagit("makam")` |
| 42 | Umumileştirme | 0,0048 | 2,1 % | 2 × `mpo_topla` |
| | **altısı** | **0,124** | **54,0 %** | **hepsi MPO** |

Kalan 38 meleke toplam %6'dır.

### 4. kademe: MPO melekelerinin içi — SEBEP BULUNDU

`mpo_topla`'nın kendi hesabı **ucuzdur**: 0,000113 sn (bunun %59'u
221 elemanlık sektör çarpımı). Pahalı olan şu satırdır:

```python
self.psi[:, i:jj] = self.psi[:, i:jj] * faz
```

`self.psi` bir **property getter**'dır ve okunduğu anda **kapı bandını
boşaltır**. Ölçüldü (`cProfile`, 4 MPO melekesi × 20 tur):

```
_karo_blas   60 çağrı   0,190 sn   ← toplam 0,235 sn'nin %81'i
mpo_topla    80 çağrı   0,016 sn
```

**Yâni MPO melekeleri pahalı değil; her biri bandı boşaltıp 8 MB'lık
durumu baştan sona dolaştırıyor.** Bir `idrak_et` geçişinde 24
boşaltma sayıldı (138 kapı için).

### 5. kademe: DÜŞEN KAPILAR — %98,6

```
vurulan kapı : 223
DÜŞEN kapı   : 15 606        → %98,6'sı hiçbir şey yapmıyor
```

Melekeler yazmacın **haddini aşan** yuvalara kapı vuruyor. Her düşen
kapı yine de bir Python çerçevesi, bir `gecerli()` sözlük araması ve
bir `_lif_no` çağrısıdır. Tek küllî mizan çağrısında ölçülen:

```
gecerli   415 628 çağrı   0,30 sn
veri      392 380 çağrı   0,19 sn
```

Sebep yapısaldır: yazmaçta **yalnız 12 bit düzlemi** vardır
(`d = 2¹²`), melekeler ise `n_satir × satir_kubiti = 2 × 16 = 32` veri
yuvası + 4096 sektör indisi adresliyor.

---

## FASIL 2: OKURKEN BULUNAN DÖRT KUSUR (ölçüldü, düzeltilmedi — kararınız)

### K1. `mpo_topla` `duraklar` ve `j` argümanlarını **tamamen atıyor**

Gövdenin tamamı budur:

```python
a = np.asarray(acilar, float).reshape(-1)
i, jj = self.sektor(alan)
u = np.arange(jj - i)
faz = np.exp(1j * (a.mean() * (u + 1.0) / max(jj - i, 1)))
self.psi[:, i:jj] = self.psi[:, i:jj] * faz
```

`duraklar` gövdede **hiç geçmiyor**. `j` de geçmiyor (`jj` sektör
sonudur). Neticeleri:

* **𝒪21 Tefekkür** 20 lifin `adim`ıyla `duraklar` listesi kuruyor,
  `katki` sözlüğü dolduruyor — **hepsi atılıyor**, geriye yalnız
  `mean(katki.values())` kalıyor. Yâni "uzak menzilli tutarlılık"
  fiilen tek bir skalere iniyor.
* **𝒪30 Tahkik** `j=1` veriyor; atılıyor. O hâlde 𝒪30 ile 𝒪7 Mana
  **aynı sektöre aynı ameliyeyi** yapıyor; tek fark ölçek (1,0'a karşı
  0,9). Docstring "aynı delil iki ayrı yoldan" diyor — **ikinci yol
  yok**.
* **𝒪37 Fesâhat** `for j in range(kk)` ile 4 ayrı çağrı yapıyor;
  dördü de aynı `kelam` sektörüne, yalnız dilim ortalaması farkıyla.

### K2. `mpo_topla` **iptal edilmiş usulü** kullanıyor

`np.exp(1j · …)` — ferman 7: *transandantal faz e^{iθ} İPTAL*.
Yazmacın `faz()` metodu `Z_m`ye geçirilmişti; `mpo_topla` o geçişin
dışında kaldı. 221 elemanlık `np.exp` çağrısı, geçiş başına 6+ kere.

### K3. Bütün MPO melekeleri **ortalamaya** iniyor

`a.mean()` — `birikim(p, n_satir, ölçek)` ile üretilen satır başına
açılar tek bir sayıya çöküyor. `n_satir=2` olduğu için şu an kayıp
küçük; fakat `n_satir` büyüdükçe **satırlar arası ayrım tamamen
kaybolur**. `𝒪11 Tenakuz`un `isaret` alternasyonu (`+1,−1,+1,…`)
ortalaması **tam sıfırdır** çift satır sayısında — yâni 𝒪11 çift
satırda hiçbir faz uygulamıyor.

### K4. `_gomulu` kapı başına `np.eye(n)` tahsis ediyor

Profilde 240 çağrı. Her bit kapısı 16×16 kimlik kurup 8 girdisini
değiştiriyor.

---

## FASIL 3: 44 QMELEKENİN TAM CETVELİ

**Sütunlar:** `kapı` = bir geçişte fiilen vurulan, `düşen` = hadde
takılıp boş dönen, `sn` = tek koşu süresi.

### İlkel desenler (melekelerin kullandığı yapı taşları)

| ilkel | ne yapar | maliyet |
| :-- | :-- | :-- |
| `aci(p, n, ölçek)` | melekenin öğrenilen `n` açısı — düz vektördeki kendi dilimi | O(n) |
| `yay(p, n_sabit, hedef, ölçek)` | `n_sabit` açıyı `hedef` durağa `np.resize` ile yayar (satırdan bağımsızlık) | O(hedef) |
| `birikim(p, n, ölçek)` | `yay(…)/n` — toplam dönme durak sayısından bağımsız kalsın diye | O(n) |
| `satir_donmesi(q,p,ölçek)` | her satırın her veri kübitine sütun başına `donme(θ)`; `tek_yigin` ile tek çağrı | n·k yuva → ≤k karo |
| `tugla(q,p,ofset,ölçek)` | komşu çiftlere `SO(4)` fırça katmanı; `cift_yigin` | n·⌊k/2⌋ çift |
| `mpo_topla(alan,…)` | sektöre faz — **band boşaltır** | 1 boşaltma + O(sektör) |
| `mpo_dagit(alan,…)` | `faz(−mean)` — Cartan köşegeni | 1 boşaltma + O(d) |

### 𝒪₁–𝒪₁₀ · İDRAK

| 𝒪 | ad | sınıf | adım adım ne yapıyor | kapı | düşen | sn |
| --: | :-- | :-- | :-- | --: | --: | --: |
| 1 | **Müşahede** | kurucu | ① `satir_donmesi(0.7)` — her (satır,sütun) veri kübitine öğrenilen dönme ② `tugla(ofset=0, 0.6)` ③ `tugla(ofset=1, 0.6)` — iki ofsetli fırça, menzili iki katına çıkarır. Reel modeldeki `Softmax(QKᵀ/√d)V`'nin üniter karşılığı | 22 | 40 | 0,0013 |
| 2 | **Hayal** | kurucu | Her satırın **son** veri kübitine `donme(π/4 + θᵢ)` — tam Hadamard değil, kısmî süperpozisyon | 0 | 2 | 0,0001 |
| 3 | **Muhayyile** | kurucu | Satır içinde `j` ile `j+2` arasında **atlamalı** `dik_iki_kubit` — görmediğini birleştirir, uzak menzil kurar | 8 | 20 | 0,0008 |
| 4 | **Tertip** | koruyucu | (veri son kübiti, yerel hüküm) çiftlerine `kontrollu_donme` — satırı kendi yerel hükmüne bağlar; şahit bölütlemesi | 0 | 2 | 0,0002 |
| 5 | **Tecrit** | çözücü | `cift_yigin` ile `G.T` (**devrik**) — kurucunun tersi: ortak olmayanı ayırır, dolaşıklık **çözer** | 4 | 10 | 0,0006 |
| 6 | **Tasavvur** | kurucu | `q.mera(kademe=1, teta=aci(24))` — bir MERA kademesi; dolaşıklığı **satırlar arasına** taşır | 12 | 0 | 0,0005 |
| 7 | **Mana** | koruyucu | `mpo_topla("tasdik", birikim(0.9))` — bütün yerel hükümler tasdik sektörüne akar. **En pahalı meleke (%19,8)** | 1 | 0 | **0,0456** |
| 8 | **Tahlil** | çözücü | `satir_donmesi(0.8)` — her kübit kendi açısıyla; ortak hâl bileşenlerine ayrışır | 12 | 20 | 0,0005 |
| 9 | **Terkip** | kurucu | `tugla(ofset=1, 0.7)` — ayrılanı ters yönlü fırçayla birleştirir | 4 | 10 | 0,0007 |
| 10 | **Tezat** | koruyucu | **Tek** satırlara (`range(1,n,2)`) son kübite `faz_z()` — yıkıcı girişim, işaret çevirme | 0 | 1 | 0,0001 |

### 𝒪₁₁–𝒪₂₀ · HÜKÜM VE KEŞİF

| 𝒪 | ad | sınıf | adım adım ne yapıyor | kapı | düşen | sn |
| --: | :-- | :-- | :-- | --: | --: | --: |
| 11 | **Tenakuz Bulma** | koruyucu | `a = birikim(1.1)`; `isaret = (+1,−1,+1,…)`; `mpo_topla("tenakuz", a·isaret)`. **K3: çift satırda ortalama tam sıfır** | 1 | 0 | 0,0127 |
| 12 | **Tenkit** | çözücü | Yerel hüküm kübitlerine `donme(−|θ|)` — zayıf şahidi `|0⟩`a doğru bastırır (sıfırlamaz) | 0 | 1 | 0,0001 |
| 13 | **Tasdik** | çözücü | ① `cift(tasdik₀, kontrollu_donme)` ② `tek(tasdik₁, donme)`. **Akışta iki kere koşar** (kendi yerinde ve 𝒪33'ten sonra) | 0 | 2 | 0,0001 |
| 14 | **Gaye Belirleme** | koruyucu | `tasdik_j → mizan_j` (j=0,1) `kontrollu_donme` — hükmün nereye çekildiği | 0 | 2 | 0,0001 |
| 15 | **Merak ve Sual** | kurucu | `nakz_j`'ye `donme(π/4 + θ)` — bilgisizliği süperpozisyona sokar | 0 | 2 | 0,0002 |
| 16 | **Deneme-Yanılma** | kurucu | Bütün (satır,sütun) veri kübitlerine `donme(θⱼ)`, tohumlu küçük hamleler | 12 | 20 | 0,0005 |
| 17 | **İhtimal Hesabı** | koruyucu | `mizan_j` (j=0..3) kübitlerine `donme` — Bayes önseli mîzâna yazar | 0 | 4 | 0,0001 |
| 18 | **Kıyas** | kurucu | Komşu satırların ilk kübitleri arası `dik_iki_kubit` — bilinenden bilinmeyene | 1 | 0 | 0,0004 |
| 19 | **Temsil** | koruyucu | `cift_yigin` ile sütun 0 (ve k≥4 ise sütun 2) — **tersinir** soyut→somut | 4 | 0 | 0,0005 |
| 20 | **Teşbih** | kurucu | İlk **iki satırın** her sütununu `uzak_cift` ile bağlar — vech-i şebeh | 4 | 12 | 0,0007 |

### 𝒪₂₁–𝒪₃₀ · TEFEKKÜR VE TAHKİK

| 𝒪 | ad | sınıf | adım adım ne yapıyor | kapı | düşen | sn |
| --: | :-- | :-- | :-- | --: | --: | --: |
| 21 | **Tefekkür** | kurucu | ① `lifleri_kur(DINAMIK)` → 20 ∞-kategori mertebesi ② her lifin `olcek`'iyle `eksen_acisi[yuva % k]` toplanır → `tek_yigin` ③ her lifin `adim`ıyla `duraklar` kurulur → `mpo_topla("makam", …, duraklar=dur)`. **K1: `duraklar` atılıyor** — ②'nin ötesindeki bütün mertebe hesabı tek skalere iniyor | 13 | 20 | **0,0337** |
| 22 | **İllet Keşfi** | koruyucu | Komşu satırlar arası **yönlü** `kontrollu_donme` — nedensellik simetrik değildir | 1 | 0 | 0,0003 |
| 23 | **Mantık Yürütme** | koruyucu | `mpo_topla("nakz", −|birikim(0.8)|)` — tek karşı örnek küllî önermeyi düşürür | 1 | 0 | 0,0021 |
| 24 | **İspat** | çözücü | Yerel hüküm kübitleri zinciri: `θᵢ/(1+0,1i)` — **Occam**: uzun zincir zayıf | 0 | 1 | 0,0001 |
| 25 | **Teemmül** | koruyucu | `TUR` kere `tugla(ofset=t%2, 0.3)` — devridaim, yeni menzil açmaz | 16 | 30 | 0,0013 |
| 26 | **Temkin** | koruyucu | Yerel hükümlere **çok küçük** açı (`ölçek=0,12`) — sarsılmazlık | 0 | 1 | 0,0002 |
| 27 | **Tetkik** | koruyucu | `satir_donmesi(0.2)` — kılcal inceleme | 12 | 20 | 0,0005 |
| 28 | **Tashih** | çözücü | 𝒪27'nin açılarını okur, `λ = tanh(θ)` ile **negatifini** vurur — tetkikin bir kısmını geri alır | 12 | 20 | 0,0004 |
| 29 | **Teyit** | — | Her satırda (ilk veri kübiti ↔ yerel hüküm) `uzak_cift` — **bağımsız ikinci kanal**; uyuşma yapıcı, uyuşmazlık yıkıcı girişim | 0 | 2 | 0,0004 |
| 30 | **Tahkik** | koruyucu | `mpo_topla("tasdik", birikim(1.0), j=1)`. **K1: `j` atılıyor → 𝒪7 ile aynı ameliye** | 1 | 0 | **0,0199** |

### 𝒪₃₁–𝒪₄₁ · MUHAKEME VE BEYAN

| 𝒪 | ad | sınıf | adım adım ne yapıyor | kapı | düşen | sn |
| --: | :-- | :-- | :-- | --: | --: | --: |
| 31 | **Tedebbür** | kurucu | ① `G⁴ = matrix_power(G, UFUK)` — dört vuruş tek kapıda (cebrî sadeleştirme) ② `mizan₂,mizan₃`'e `donme` — âkıbete bakmak | 2 | 2 | 0,0006 |
| 32 | **Şek-Zan-Yakîn** | — | ① `tasdik₀ → makam₀` (+) ② `nakz₀ → makam₀` (−) ③ `tenakuz₀ → makam₁` (kararsızlık) ④ `tasdik₁ → makam₂` (ince basamak) ⑤ `makam → sukut` — makam **üç kübitlik merdiven**, faza kodlanır | 0 | 5 | 0,0002 |
| 33 | **Muhakeme** | koruyucu | Meclis: `tasdik_j → mizan_j` (+), `tenakuz_j → mizan_{2+j}` (−), `nakz_j → mizan_j` (−). Mîzân bir bölme değil, **lehte/aleyhte dönme** | 0 | 6 | 0,0001 |
| 34 | **Tafsil** | koruyucu | `mpo_dagit("makam", birikim(0.7))` — **tek yönü tersine çeviren meleke**: küllîden yerele iner | 1 | 0 | 0,0073 |
| 35 | **Tefsir** | koruyucu | `(satır i−1'in son kübiti) ↔ (satır i'nin ilk kübiti)` — siyak ve sibak | 0 | 1 | 0,0004 |
| 36 | **Tevil** | koruyucu | `tenakuz_j → tasdik_j` `kontrollu_donme` — **şartlı**: çelişki yoksa hiç dönmez | 0 | 2 | 0,0001 |
| 37 | **Fesâhat** | koruyucu | ① `kk` kere `mpo_topla("kelam", dilim, duraklar=yereller, j=j)` ② **tasdik mührü**: `X`-sarmalı ile `tasdik₀=0` iken kelam bastırılır. **K1: `j` ve `duraklar` atılıyor** | 4 | 4 | 0,0023 |
| 38 | **Talâkat** | koruyucu | ① kelam kübitleri arası komşu `cift` ② `tasdik_j → kelam_j` — akıcılık ham veriden değil **mühürlü hükümden** | 0 | 5 | 0,0004 |
| 39 | **Belâgat** | koruyucu | ① `makam_{j%mk} → kelam_j` ② `tasdik_j → kelam_{j+2}` — sözü **makamına göre** söylemek | 0 | 6 | 0,0002 |
| 40 | **Sanat** | koruyucu | **Altın açı** `2π/φ²` — öğrenilmez, melekenin kendi tarifinden gelir. Yalnız makam ve kelam alanına | 3 | 4 | 0,0002 |
| 41 | **Münazara** | çözücü | ① `mizan_j → makam_j` ② **sükût kapısı**: `sukut₀` uyanıksa kelam bastırılır ③ `tek(sukut₀, donme)` — bilmediğini söylememek | 0 | 7 | 0,0001 |

### 𝒪₄₂–𝒪₄₄ · TEŞKİLÂT (klasik katmanda karşılığı YOK)

| 𝒪 | ad | sınıf | adım adım ne yapıyor | kapı | düşen | sn |
| --: | :-- | :-- | :-- | --: | --: | --: |
| 42 | **Umumileştirme** | koruyucu | `Π_inv`: bütün duraklara **aynı** açı (`a₀/n`) → `mpo_topla("mizan")`; kesişim dışı araz → `mpo_topla("tenakuz", −0,25·ortak)` | 2 | 0 | 0,0048 |
| 43 | **Talim** | koruyucu | `talim_kademesi(OLCU, TAU)` sahihse: her `τ_l` için `θ = a_l/τ_l` ile kelam kübitlerine `donme` — τ düştükçe beyan keskinleşir | 0 | 16 | 0,0003 |
| 44 | **Tahsil** | çözücü | `parametre` bölgesi varsa: ① `mizan_{j%4} → parametre_j` `kontrollu_donme(−η)` (exp(−ηĤ)) ② `parametre_j`'ye `donme(γ·a₁)` (kimlik payı). **Bölge yoksa hiç koşmaz** | 0 | 0 | 0,0000 |

---

## FASIL 4: SÜPERSEÇİM SEKTÖRLERİ (melekelerin yazdığı adresler)

`d = 4096`, on bir alan **paya orantılı** bölünmüş:

| alan | aralık | genişlik | pay | kim yazıyor |
| :-- | :-- | --: | --: | :-- |
| `makam` | [0, 332) | 332 | 3 | 𝒪21, 𝒪32, 𝒪34, 𝒪39, 𝒪40, 𝒪41 |
| `mizan` | [332, 775) | 443 | 4 | 𝒪14, 𝒪17, 𝒪31, 𝒪33, 𝒪41, 𝒪42, 𝒪44 |
| `tenakuz` | [775, 996) | 221 | 2 | 𝒪11, 𝒪32, 𝒪33, 𝒪36, 𝒪42 |
| `tasdik` | [996, 1217) | 221 | 2 | 𝒪7, 𝒪13, 𝒪14, 𝒪30, 𝒪32, 𝒪33, 𝒪36, 𝒪37, 𝒪38, 𝒪39 |
| `sukut` | [1217, 1328) | 111 | 1 | 𝒪32, 𝒪41 |
| `nakz` | [1328, 1549) | 221 | 2 | 𝒪15, 𝒪23, 𝒪32, 𝒪33 |
| `kelam` | [1549, 1992) | 443 | 4 | 𝒪37, 𝒪38, 𝒪39, 𝒪40, 𝒪41, 𝒪43 |
| `kaide` | [1992, 3320) | **1328** | 12 | **hiç kimse** |
| `orak` | [3320, 3431) | 111 | 1 | **hiç kimse** |
| `gaye` | [3431, 3652) | 221 | 2 | `gaye_kos` (meleke değil) |
| `tertip` | [3652, 4096) | 444 | 4 | **hiç kimse** |

**Bulgu:** `kaide` (d'nin **%32,4'ü**, 1328 genlik), `orak` ve `tertip`
sektörlerine **hiçbir melekenin adresi düşmüyor**. Toplam
`1328+111+444 = 1883` genlik = durumun **%46'sı**.

**Tam olarak ne demek — ölçüldü, abartılmıyor:** o sektörler *tamamen*
hareketsiz değildir; `kodla`, `superpozisyon`, `mera` ve `faz` bütün
lifler üstünde koştuğu için oraya da dokunurlar. Ölçülen ağırlıklar
(bir geçiş sonunda):

```
kaide   0,302655   (düzgün başlangıçta olurdu: 0,324219)
orak    0,033929
tertip  0,101830
```

Yâni umumî ameliyeler karıştırıyor, fakat **hiçbir hüküm oraya
yazılmıyor**: 44 melekenin hiçbiri `q.kulli("kaide", …)`,
`q.kulli("orak", …)` yahut `q.kulli("tertip", …)` adresini
kullanmıyor. O hâlde bu üç alan **hüküm taşımıyor**, yalnız yer
kaplıyor ve her kapıda dolaşılıyor.

---

## FASIL 5: TENSİP-TAKDİR — HANGİ ÇARE NEREYE

Bu bölüm **teklif değil, ölçünün gösterdiği yerlerin listesidir**.
Çareyi siz takdir edeceksiniz.

| # | darboğaz | ölçülen | nereye dokunulur |
| --: | :-- | :-- | :-- |
| **D1** | MPO melekeleri bandı boşaltıyor | 4 meleke, geçişin %38'i; `_karo_blas` %81 | `mpo_topla` sektöre faz yazıyor — bu **köşegen** bir ameliyedir ve karo bandıyla **değişmez değildir**, o yüzden boşaltma zorunlu görünüyor. Fakat `faz()` gibi **banda yazılabilir**: köşegen op olarak banda eklenip C'de sektör dilimine vurulabilir. O zaman 6 boşaltma → 0. |
| **D2** | %98,6 kapı düşüyor | 15 606 düşen / 223 vurulan | Melekeler yuva adresliyor, yazmaçta 12 bit düzlemi var. Ya adresleme yeniden tarif edilir (meleke başına **geçerli yuva listesi** koşu başında bir kere kurulur), ya `gecerli` C'ye alınır. Şu an her düşen kapı 3 Python çağrısı. |
| **D3** | `vicdan` her melekeden sonra | 45 çağrı, geçişin %21,1'i | Şart mı yoksa periyodik mi olacağı **hüküm meselesidir** (H102/H105 "muafiyetsiz" diyor). Kararı siz verirsiniz; ben dokunmadım. |
| **D4** | `mpo_topla` `np.exp` kullanıyor | 221 elemanlık transandantal, geçiş başına 6+ | Ferman 7 ihlâli. `ayrik_faz` (Z_m) ile değiştirilebilir — `faz()` zaten öyle. |
| **D5** | `duraklar`/`j` atılıyor | 𝒪21'in 20 mertebe hesabı, 𝒪30'un ikinci yolu, 𝒪37'nin 4 dilimi | **Riyazî kayıp**, hız meselesi değil. `mpo_topla` ya `duraklar`ı kullanmalı ya melekeler onu hesaplamamalı. |
| **D6** | Durumun %46'sı hüküm taşımıyor | `kaide`+`orak`+`tertip` = 1883/4096 genlik; hiçbir meleke adreslemiyor | Ya bu alanlara yazan meleke eklenir, ya `kulli_alanlar` payları küçültülür. İkincisi `d`yi düşürür ve **doğrudan hızdır**: her karo GEMM'i ve her sektör çarpımı `d` ile doğrusaldır. `kaide` payı 12→2 yapılsa `d` 4096'dan 2048'e inerdi (lif (16,16,8) yahut (16,8,16)). |
| **D7** | Klasik `Meleke` katmanı ölü | 41 sınıf, ~2 450 satır, 0 çağrı | Bağlanır yahut ferman 2-B ile kesilir. |
| **D8** | `_gomulu` kapı başına `np.eye` | 240 çağrı/geçiş | Karo önbelleklenebilir: `(n, alt, G)` → 16×16. |
| **D9** | `_monogami` + `engellenme` | kaybın %11,4'ü | 12 sektör × yığın GEMM; `engellenme` CIM halkası 24 tur. |

---

## EK: ÖLÇÜM USULÜ

Bütün sayılar şu şekilde alındı:

* **Meleke süreleri**: `QMeleke.kosu` sarmalanıp `time.perf_counter`
  ile; ısıtma geçişinden **sonra**.
* **Kapı sayıları**: `q.y._kapi` ve `q.y._dusen_kapi` farkı.
* **Kademe payları**: `cProfile` `tottime`/`cumtime`.
* **Sektör aralıkları**: `q.y.sektor(ad)` doğrudan okundu.
* **Katman ölülüğü**: `Meleke.kosu` ve `QMeleke.kosu` sayaçlanarak.

Hiçbiri kestirim değildir; hepsi bu makinede koştu.
