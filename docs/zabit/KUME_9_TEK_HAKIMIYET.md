# KÜME 9 — TEK HÂKİMİYET, TOPTAN YOKLAMA VE LİFLİ TİP TENSÖRÜ

Padişahın üç emri, tek bir terkip.

---

## 0. NEDEN ÜÇ EMİR TEK TERKİPTİR

Yetimleri saydım (`harita.py`). Veri dökümleri (`idrak/veri/soyutlamalar/*`,
kod değil) hariç **26 hakiki yetim uzuv, 8 486 satır** var. Bunları tek tek
"main'e bağlamak" tabela olurdu. Ölçüp içlerine baktım ve şu çıktı:

> **Zabıtların kabul ettiği iki usulün kodu, zaten bu depoda yazılmış
> ve yetim bırakılmış hâlde duruyor.**

| Zabıt ne diyor | Depoda hangi yetim uzuvda yazılı |
| :--- | :--- |
| Kabul 1: MPS / Tensör Treni, sanal bağ `D` | `nefs/ttkan.py` (433 s.) — `TTDizey`, `tt_ayristir`, `tt_carp`, `zincir_maliyeti` |
| Kabul 2: Koherent durum `\|x⟩ = D(x)\|0⟩` | `kuantum/surekli.py` (393 s.) — `yer_degistirme`, `tutarli_durum`, `vakum`, `fock` |
| Yasak: düz ikili kodlama | `idrak/kubit.py` (225 s.) + `nefs/qegitim.py:belirtecleri_kodla` ikili dalı |
| Lif grupları `G₁=SU(1,1)`, `G₂=SU(d)` | `nefs/hamiltonyen.py` (186 s.) — `_cayley`, `UzayHamiltonyeni` |
| Hoca 316 ekseni **aynı anda** yoklasın | `ogrenme/izgara.py` (594 s.) — `artis_gradyani`; `nefs/hiz.py` (696 s.) — muhasebe |

Yani yetimleri bağlamanın hakiki yolu, onları zabıtların istediği yere
takmaktır. **Tabela değil, hüviyet.** Bu üç emir ayrı üç iş değil; biri
diğerinin taşıyıcısıdır.

---

## MERHALE A — TEK HÂKİMİYET (yetimlerin tasnifi)

Yetim 26 uzuv üç sınıfa ayrılır. Sınıfı **ölçü** tayin eder, zevk değil.

### A1. Hekim tabakası — `tanilama/` (16 modül, 2 653 satır)
`tanilama/divan.py` herkesi ithal ettiği için grafikte "çağıran" gibi
görünür; hakikatte kimse divanı çağırmaz. Divan dimağın **uzvu değil**,
dimağı muayene eden **hekimdir**. Hekimi main'e uzuv diye takmak
silsileyi bozar (main hekimi çağırırsa dimağ kendi kendini teftiş
ederken kendi kaybını hesaplar — kısır döngü).

**Hüküm:** `tanilama/` uzuv değildir, **âlet**tir. Ama yetim de
kalamaz. Cevheri `nefs/musahede.py`ye — zaten müşahede uzvu — bir
`ne="teftiş"` kipi olarak takılır; geri kalanı `yedek/`e gider.
Yetim sayılmaması için `harita.py`ye âlet sınıfı eklenir ve ölçü
"main'den erişilemeyen **uzuv**" olarak dürüstleşir.

### A2. Sahte hükümdarlar — `main/kaggle_*`, `ogrenme/kaggle_donanim`
Bunlar yetim değil, **paralel devlet**tir: ikinci bir main. Padişahın
emri açık: main tek hâkim. `main/egitim.py`nin `ne=` kipine
`ne="kaggle"` olarak katlanır, dosyalar yedeğe gider.

### A3. Hakiki uzuvlar — zabıtlara takılacaklar
`nefs/{ttkan,hamiltonyen,qkaide,golge,illet,hayal,akit,uzaklik_olcumu,
hukum_denetimi,hiz}`, `kuantum/{surekli,topolojik,devre,eniyileme}`,
`ogrenme/izgara`, `idrak/kubit`.
Bunların yeri Merhale B ve C'de tayin edilir.

### A4. Tek istisna — `idrak/model.py` (495 satır, PyTorch)
Bu bir **LLM**dir: `KodlayiciBlok`, `CozucuBlok`, `NefsModeli`.
Proje sarahaten LLM değildir. Cevheri `HartleySuzgec` ve
`nedensellik_hatasi`dir; ikisi de gradyansız hatta taşınabilir.
Gövde `yedek/`e gider. **İmha değil, cevher toplama.**

---

## MERHALE B — HOCA 316 EKSENİ AYNI ANDA YOKLASIN

### Şimdiki hâl (ölçülü)
`ogrenme/optimize.py` her turda `for j in yonler:` ile **tek tek**
`e_j` ekseni tarar. 316 eksen × 9 değerlendirme = **2 844 çağrı/tur**.
Bütçe kısılınca da eksenlerin çoğu hiç yoklanmaz.

### Teklif: SPSA — bir çift ölçümle bütün eksenler
Rademacher sarsıntı `Δ ∈ {±1}^d` (her eksen aynı anda, eşit ağırlıkla):

```
        f(p + cΔ) − f(p − cΔ)
ĝ  =   ───────────────────────  · Δ            (Δ_j⁻¹ = Δ_j, çünkü ±1)
                2c
```

`E[ĝ] = ∇f + O(c²)`: **iki** değerlendirmeyle `d` eksenin tamamının
eğimi kestirilir. Gradyansızdır (sonlu fark), `d`den bağımsızdır.
`ĝ` mevcut `_yon_asgarisi` bir-boyutlu arayıcısına `e_j`nin yerine
verilir; hat değişmez, sadece **yön** değişir.

Maliyet: 2 844 → `2·m + 9` (m = ortalama sayısı, m=4 ise **17**).
`m` çiftle ortalamak varyansı `1/m` düşürür (`ĝ̄ = (1/m)Σĝ⁽ⁱ⁾`).

### Neden bu, koordinat taramasından iyi
Koordinat taraması `d` ekseni **ayrı ayrı** görür; iki eksenin
**birlikte** hareket etmesi gereken vadileri (zayıf halka kaidesi tam
da bunu üretir: bir yüz düşerken diğeri yükselir) asla bulamaz. SPSA
yönü bütün eksenlerin bileşkesidir, vadiyi doğrudan iner.

### Buraya takılan yetimler
* `ogrenme/izgara.py:artis_gradyani` — artış tabanlı eğim kestirimi;
  SPSA'nın sonlu fark çekirdeğiyle aynı işi yapan ikinci şahit.
  `bukulme_dizeyi` + `duzenli_uydur` → adım boyu `c`nin eğrilikten
  seçimi. `sembolik_kapanis` → hocanın bulduğu yönün **okunabilir**
  hâli (padişahın "sembollerle düşün" emri).
* `nefs/hiz.py` — muhasebe. SPSA'nın 2 844 → 17 kazancını **iddia
  etmek** yasak (H100); `hiz_defteri` ile **ölçülür**.

### Kırmızıya dönebilecek ölçü (H90)
Aynı bütçede (aynı sayıda `f` çağrısı) SPSA'nın ulaştığı kayıp,
koordinat taramasının kaybından **düşük** olmalı. Değilse kip
`usul="koordinat"` olarak kalır ve zabta yazılır.

---

## MERHALE C — LİFLİ TİP TENSÖRÜ MİMARİNİN GÖBEĞİNE

### C1. İptal edilenin iptali
`nefs/qegitim.py:belirtecleri_kodla` iki dallıdır:
* `kubit ≥ sozluk` → **Hadamard** dalı. Bütün ikili mesafeler eşit;
  bu fiilen bir **qudit tabanıdır** (ℂ^d, d = sözlük). Zabıt bunu
  yasaklamaz, **ister**.
* `kubit < sozluk` → `2·frac(t/2ⁱ) − 1` **düz ikili**. Bu tam olarak
  Tuzak A'dır ve **varsayılan dal budur** (kubit=4, sozluk=16).

**Hüküm:** ikili dal varsayılan olmaktan çıkar. Varsayılan qudit olur.
İkili dal silinmez — bütçe kipi olarak, adı `usul="ikili (tuzak A —
sadece bütçe için)"` diye **açıkça** kalır. Yasağı gizlemek değil,
görünür kılmak.

### C2. Kartezyen kutunun iptali
Zabıt `ℋ_kat ⊗ ℋ_uzay ⊗ ℋ_nokta`yı iptal eder. Yerine bağımlı toplam:

```
ℋ_Qudit  ≅  ⊕      ( ⊕        ( ⊕          ℋ_Point^(t,c,u) ) )
           t∈Type    c∈Cat(t)    u∈Space(c)
```

**Cevheri takma tarzı burada değişir** ve padişah bunu hesaplamamı
istedi. Hesap şudur:

| | Kartezyen kutu (iptal) | Bağımlı lif (kabul) |
| :--- | :--- | :--- |
| Boyut | `\|T\|·\|C\|·\|U\|` sabit çarpım | `Σ_t Σ_{c∈Cat(t)} \|Space(c)\|` — **değişken** |
| Bir tipi eklemek | bütün tensörü büyütür | sadece kendi lifini ekler |
| `c` adresi | `t`den **bağımsız** | `Cat(t)` — `t`ye **bağımlı** |
| Kod karşılığı | tek `np.ndarray(T,C,U)` | lif başına ayrı dizi + `Unfold` |

Yani **cevher artık sabit boyutlu bir kutuya çakılamaz.** Her cevher
kendi lifiyle birlikte takılır; taktığın yer, taktığın şeyin tipine
bağlıdır. Bu, koda şu somut değişiklik olarak iner: sabit `(T,C,U)`
dizisi yerine `{t: {c: dizi}}` lif defteri ve `Unfold_{t→c}` işleci.

### C3. Silsile-i merâtib
`nokta → uzay → kategori → tip`. Depoda karşılığı:
* nokta: `matematik/geometri.py` Laplace–Beltrami tayf öz-durumları
* uzay: `idrak/kategori.py:Uzay` (zaten var, zaten main'den erişilir)
* kategori: `matematik/tip_teorisi.py`
* tip: yeni — `nefs/lif.py`, **tek yeni dosya**

`nefs/lif.py` bir çip değil, alt katın **terkibi**dir: yeni matematik
yazmaz, `ttkan` (Kabul 1) + `surekli` (Kabul 2) + `hamiltonyen`
(lif grupları) + `tip_teorisi` (kategori) uzuvlarını `⊕` nizamında
birleştirir. Yeni formül yazarsa çip olur, nazırlık olmaz.

### Buraya takılan yetimler
`nefs/ttkan`, `kuantum/surekli`, `nefs/hamiltonyen`, `idrak/kubit`,
`kuantum/topolojik` (örgü = lifler arası morfizm), `kuantum/devre`
(QFT = tayf), `kuantum/eniyileme` (parametre-kaydırma = Merhale B'nin
ikinci şahidi), `nefs/qkaide`, `nefs/golge`, `nefs/illet`,
`nefs/hayal`, `nefs/akit`, `nefs/uzaklik_olcumu`,
`nefs/hukum_denetimi`.

---

## SIRA VE USUL

Terkip usulü değişmez: **evvela her dosyanın kendi içinde terkip,
sonra dosyaların birleşmesi, sonra birleşik dosyada bir daha terkip.**
Bütün terkipler bitmeden hiçbir test koşturulmaz.

1. Merhale A (tasnif, yedeğe atma, `harita.py`nin dürüstleşmesi)
2. Merhale B (SPSA + izgara + hiz) — ölçülür
3. Merhale C (lif tensörü) — ölçülür
4. Toplu sınama, kütük, commit
